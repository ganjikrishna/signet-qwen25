#!/usr/bin/env python3
"""Score two models on the sealed test items and print the paired table.

This is the entry point that produced the closing numbers in REPORT.md
(run once, on 2026-11-06, when the seal was spent). It scores a base model
directory against an edited model directory with the frozen definitions in
signet_scoring.py: greedy, 160 tokens, float32, raw completion, degenerate =
cap hit or repetition share at least 0.3 or any CJK. Significance is the
freeze standard: paired McNemar exact test plus a bootstrap CI on the
improvement (seed 7, 4000 resamples).

Usage:
    python evaluate.py --base-model /path/to/base_dir --edited-model /path/to/t4_dir

Each model directory is a Hugging Face folder (config, tokenizer, weights).
To score the T4 model, first build it with apply_t4.py and place the output
safetensors in a copy of the base model folder.
"""
import argparse
import json

import numpy as np

from signet_scoring import bootstrap_ci, deg_rate, gen_rows, load_model_dir, load_tok, mcnemar_exact

SLICES = [
    ("all_items", lambda it: True),
    ("story_all", lambda it: it["slice"] == "story"),
    ("story_seen_families", lambda it: it["slice"] == "story" and it.get("family") != "station"),
    ("story_HELDOUT_station", lambda it: it.get("family") == "station"),
    ("factual", lambda it: it["slice"] == "factual"),
    ("other_genre", lambda it: it["slice"] in ("explain", "dialogue", "description")),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base-model", required=True, help="HF dir of the base model")
    ap.add_argument("--edited-model", required=True, help="HF dir of the edited model")
    ap.add_argument("--items", default="data/sealed_items.json", help="items json (default: data/sealed_items.json)")
    ap.add_argument("--out", default=None, help="optional path to write the results json")
    args = ap.parse_args()

    items = json.load(open(args.items))
    prompts = [i["prompt"] for i in items]
    tok = load_tok(args.base_model)
    flags = {}
    for label, path in (("base", args.base_model), ("edited", args.edited_model)):
        model = load_model_dir(path)
        flags[label] = gen_rows(model, tok, prompts)
        del model
        print(f"{label}: overall degeneration {deg_rate(flags[label]):.4f}")

    results = []
    for name, pred in SLICES:
        idx = [i for i, it in enumerate(items) if pred(it)]
        if not idx:
            continue
        rb = [flags["base"][i] for i in idx]
        rt = [flags["edited"][i] for i in idx]
        b = sum(1 for i in idx if flags["base"][i]["degenerate"] and not flags["edited"][i]["degenerate"])
        c = sum(1 for i in idx if flags["edited"][i]["degenerate"] and not flags["base"][i]["degenerate"])
        diffs = [(1 if flags["base"][i]["degenerate"] else 0) - (1 if flags["edited"][i]["degenerate"] else 0) for i in idx]
        row = {"slice": name, "n": len(idx), "base_deg": deg_rate(rb), "edited_deg": deg_rate(rt),
               "improvement_pts": 100 * float(np.mean(diffs)), "mcnemar_b": b, "mcnemar_c": c,
               "mcnemar_p": mcnemar_exact(b, c), "boot_ci95_pts": [100 * x for x in bootstrap_ci(diffs)]}
        results.append(row)
        print(f"{name}: n={row['n']} base {row['base_deg']:.4f} edited {row['edited_deg']:.4f} "
              f"improvement {row['improvement_pts']:+.2f} pts p {row['mcnemar_p']:.4g} "
              f"CI [{row['boot_ci95_pts'][0]:.2f}, {row['boot_ci95_pts'][1]:.2f}]")
    if args.out:
        json.dump({"items": args.items, "slices": results}, open(args.out, "w"), indent=1)
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
