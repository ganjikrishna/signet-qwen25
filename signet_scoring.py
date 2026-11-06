#!/usr/bin/env python3
"""Frozen scoring for the Signet Qwen2.5-0.5B program.

These are the exact definitions every number in REPORT.md was produced with.
They were frozen before the editing rounds and never retuned:

- greedy decoding, 160 new tokens, float32, batch 24, left padding
- raw completion (no chat template) for base-style models
- output trimmed at the first EOS token (ids 151643, 151645)
- degenerate = generation hit the 160 token cap, OR repetition share at
  least 0.3 (share of output tokens inside a repeated 8-gram), OR the
  decoded text contains any CJK character
"""
import re
from math import comb

import numpy as np
import torch

EOS_IDS = {151643, 151645}
CJK_RANGES = ((0x4E00, 0x9FFF), (0x3040, 0x30FF), (0xAC00, 0xD7AF))
CJK = re.compile("[" + "".join(chr(a) + "-" + chr(b) for a, b in CJK_RANGES) + "]")


def rep_rate(ids):
    """Share of tokens covered by any repeated 8-gram."""
    if len(ids) < 8:
        return 0.0
    grams = {}
    for i in range(len(ids) - 7):
        grams.setdefault(tuple(ids[i:i + 8]), []).append(i)
    covered = set()
    for pos in grams.values():
        if len(pos) >= 2:
            for p in pos:
                covered.update(range(p, p + 8))
    return len(covered) / len(ids)


def gen_rows(model, tok, prompts, batch=24):
    """Generate greedily on raw prompts and score each output."""
    rows = []
    for s in range(0, len(prompts), batch):
        chunk = prompts[s:s + batch]
        enc = tok(chunk, return_tensors="pt", padding=True)
        gen = model.generate(**enc, max_new_tokens=160, do_sample=False, pad_token_id=tok.pad_token_id)
        plen = enc["input_ids"].shape[1]
        for i in range(len(chunk)):
            out_ids = gen[i][plen:].tolist()
            hit = any(t in EOS_IDS for t in out_ids)
            if hit:
                out_ids = out_ids[:min(j for j, t in enumerate(out_ids) if t in EOS_IDS)]
            text = tok.decode(out_ids, skip_special_tokens=True)
            rep = rep_rate(out_ids)
            cjk = len(CJK.findall(text)) > 0
            cap = len(out_ids) >= 160 and not hit
            rows.append({"n_tokens": len(out_ids), "cap_hit": bool(cap), "rep": rep,
                         "cjk": bool(cjk), "degenerate": bool(cap or rep >= 0.3 or cjk)})
    return rows


def deg_rate(rows):
    return float(np.mean([r["degenerate"] for r in rows])) if rows else 0.0


def mcnemar_exact(b, c):
    """Two-sided exact McNemar p-value from discordant pair counts."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def bootstrap_ci(diffs, seed=7, n=4000):
    """95% percentile bootstrap CI for the mean of paired differences."""
    rng = np.random.default_rng(seed)
    d = np.asarray(diffs, dtype=float)
    means = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(n)]
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def load_model_dir(path):
    from transformers import AutoModelForCausalLM
    m = AutoModelForCausalLM.from_pretrained(path, dtype=torch.float32)
    m.eval()
    return m


def load_tok(path):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(path)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    return tok
