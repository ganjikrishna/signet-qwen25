#!/usr/bin/env python3
"""Reconstruct the Signet T4 model from Qwen2.5-0.5B base weights.

T4 is a sign-restricted (binary) edit. For each of the 168 tensors that a
flaw-targeted LoRA training run touched, the edit is:

    edited = base + alpha_t * sign(training_delta_t)

where training_delta_t = (trained weights - base weights) for that tensor and
alpha_t is that tensor's own mean |training_delta|. Every weight moves by
exactly +alpha_t, -alpha_t, or 0 (the 1,616 positions where the training
delta was exactly zero do not move). Nothing else in the model changes.

Two ways to run it:

1. From the shipped sign file (no training needed):
       python apply_t4.py --base model.safetensors --out t4.safetensors
   data/t4_signs.npz holds the packed sign bits, the zero positions, the
   per-tensor shapes, and the 168 alpha values, derived from the training
   delta during the program (see derive mode below).

2. Derive mode, from a merged copy of the Arm T trained model:
       python apply_t4.py --base base.safetensors --trained armt.safetensors \
           --out t4.safetensors
   This recomputes signs and alphas straight from the training delta. It is
   the construction the loop itself used, and it produces the same weights.

Verification: during the program, the reconstruction was compared tensor by
tensor against the measured artifact and matched exactly on all 290 tensors.
The measured artifact file (written by the Hugging Face save path) has
sha256 ca123f513d5f282d6f7ea4147c5da0fbf51b997bd00aa8c3eb9d772e3c3d6756; a
plain safetensors save of the identical tensors can hash differently, so
compare tensors, or score the output with evaluate.py and check the sealed
numbers in REPORT.md.

Needs: numpy, torch, safetensors. Base weights: the official Qwen2.5-0.5B
base checkpoint (model.safetensors). This script does not download anything.
"""
import argparse

import numpy as np
import torch
from safetensors import safe_open
from safetensors.torch import load_file, save_file

TENSORS_HINT = "the 168 LoRA tensors (7 projection types x 24 layers)"


def signs_from_npz(path):
    """Yield (name, shape, alpha, sign_array_float32) from the shipped file."""
    z = np.load(path)
    for k in z["tensor_names"].tolist():
        shape = z[f"shape::{k}"].tolist()
        n = int(np.prod(shape))
        bits = np.unpackbits(z[f"bits::{k}"])[:n]
        sign = np.where(bits > 0, 1.0, -1.0)
        sign[z[f"zero_idx::{k}"]] = 0.0
        yield k, shape, float(z[f"alpha::{k}"]), sign.astype(np.float32).reshape(shape)


def signs_from_trained(base_path, trained_path):
    """Recompute signs and alphas from a merged Arm T model. A tensor counts
    as touched when its training delta is nonzero anywhere."""
    with safe_open(base_path, framework="pt") as fb, safe_open(trained_path, framework="pt") as ft:
        only = set(fb.keys()) ^ set(ft.keys())
        if only:
            print(f"warning: {len(only)} tensors exist in only one checkpoint and are skipped: {sorted(only)[:4]}")
        names = sorted(set(fb.keys()) & set(ft.keys()))
        for k in names:
            d = ft.get_tensor(k).float() - fb.get_tensor(k).float()
            if float(d.abs().max()) == 0.0:
                continue
            alpha = float(d.abs().mean())
            yield k, list(d.shape), alpha, torch.sign(d).numpy()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", required=True, help="base Qwen2.5-0.5B model.safetensors")
    ap.add_argument("--signs", default="data/t4_signs.npz", help="shipped sign file (default: data/t4_signs.npz)")
    ap.add_argument("--trained", default=None, help="merged Arm T model safetensors; if given, derive signs from it instead of --signs")
    ap.add_argument("--out", required=True, help="output safetensors path for the T4 weights")
    args = ap.parse_args()

    base = load_file(args.base)
    out = {k: v.float() for k, v in base.items()}
    src = signs_from_trained(args.base, args.trained) if args.trained else signs_from_npz(args.signs)
    count = 0
    for k, shape, alpha, sign in src:
        assert list(out[k].shape) == shape, f"shape mismatch on {k}"
        out[k] = out[k] + alpha * torch.from_numpy(np.asarray(sign, dtype=np.float32))
        count += 1
    print(f"edited {count} tensors (expected: {TENSORS_HINT})")
    if count != 168:
        print(f"warning: edited tensor count is {count}, not 168; this is not the T4 edit as measured")
    save_file(out, args.out, metadata={"format": "pt"})
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
