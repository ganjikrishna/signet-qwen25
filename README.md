# Signet: sign-restricted weight edits on Qwen2.5-0.5B

Signet tests a simple question: can a language model's flaw be corrected by editing its weights with plus-or-minus steps only? Each changed weight moves by one fixed step size per tensor, in the direction a trained fix moved it, and by nothing else. No new weights are learned at edit time. The program ran on the Qwen2.5-0.5B base model under rules frozen in advance (what counts as the flaw, how edits are proposed, which controls every round must carry, and when an edit is kept or reverted). The final edit, called T4, was built entirely on a small development set and then scored once on a sealed test of 224 fresh prompts that no part of the loop had seen. This repo holds the method, the edit, the test items, and the full record, including every round that failed.

Author: Vinay K Ganji Krishna
Weight editor and collaborator: Muse Spark (Ember)

## Headline results (sealed test, run once)

The flaw: degenerate story continuation. Asked for a short story, the base model usually fails to finish: it runs to the token cap, loops repeated phrases, or drifts into Chinese characters. An output counts as degenerate if it hits the 160 token cap, or at least 30% of its tokens sit inside a repeated 8-gram, or it contains any CJK character. Scoring is greedy decoding, float32, frozen before any editing.

Sealed test, base model vs the T4 edit, paired tests:

- Story prompts (136 items): degeneration 0.8603 to 0.6912, an improvement of 16.91 points (McNemar p 0.00019, bootstrap CI [8.82, 25.0])
- All items (224): 0.6518 to 0.5000 (p 8.2e-06)
- Factual prompts (56 items): 0.1964 to 0.0357 (p 0.0117)
- Held-out story family (24 items, a theme that appears nowhere in development or training data): 0.8750 to 0.8333, +4.17 points, not significant (p 1.0, CI [-8.33, 20.83])

On stories, the edit works mainly by letting the model finish: cap hits fell from 83.8% to 64.0%, repetition from 72.1% to 63.2%, and CJK output from 0.7% to 0%. The full per-slice table and the failure-mode detail are in REPORT.md.

Development numbers, for context only (48 story prompts the loop iterated on): base 0.833 degenerate, the official instruct twin 0.146, T4 0.6042 (+22.92 points, p 0.0074). Sealed numbers above are the result; dev numbers are labeled dev wherever they appear.

## Dates

Dates and credit are part of the record, so they get their own section.

- Design freeze (rules R1 to R7, then the R8 training arm amendment): November 5, 2026
- Sealed test built and sealed: November 5, 2026 (sha256 9b44d7b792c01297c6a3a1c446652e3c9de2172b856b2f365746e81c49676cff, recorded before any editing round)
- Editing rounds T1 to T7 and the bake-off: November 5, 2026
- Sealed test run once on the final edit, and the program closed: November 6, 2026

## Method, in plain words

1. Pick the flaw by measurement, not by opinion. Candidate flaws were scored as the gap between the base model and its instruct twin on fresh prompts. Degenerate story continuation won by a wide margin (certified on 96 fresh prompts: base 53.1% degenerate, instruct 38.5%).
2. Train a small fix in full precision. A LoRA adapter was trained on the base model using the instruct twin's own generations on fresh prompts, filtered by the frozen scorer so only clean, finished stories became targets, with factual and instruction examples mixed in to protect other behavior. The trained model is a ceiling, not the product: it shows how far a real fix could go (dev degeneration 0.3125).
3. Convert the trained change into a binary edit. For each tensor the training touched, keep only the sign of its change and one step size, the tensor's own average change. That is T4: 168 tensors, each weight moved by +step, -step, or not at all.
4. Measure every edit against controls, and keep it only if it clearly wins. Each round also ran random sign patterns, the exact opposite edit, a zero edit, and the full-precision version, plus collateral checks on unrelated prompts. An edit was kept only when the improvement was statistically clear and collateral damage stayed inside a 2 point gate.
5. Never tune on the test. The sealed test was written and hashed before the rounds began and was opened exactly once, at the end.

The frozen rules (R1 to R8) are in FREEZE.md exactly as written before the work. The day-by-day record, with every proposal logged before its measurement, is summarized in REPORT.md.

## Round ledger (development set)

| Round | What was tried | Dev degeneration | Verdict |
|---|---|---|---|
| Arm T ceiling | The full-precision LoRA-trained model itself | 0.3125 | Ceiling, not a ship candidate |
| T1 | Sign of the training delta, one global step size, from base | 0.833 to 0.6458 (p 0.035) | KEEP, first verified binary fix |
| T2 | A second identical sign step stacked on T1 | 0.375 | REVERTED: the flaw improved but the collateral probe fell 2.09 points against a 2 point gate |
| T3 | A half step stacked on T1 | 0.583 (p 0.65) | NULL, not significant |
| T4 | Sign of the training delta from base, each tensor at its own step size | 0.833 to 0.6042 (p 0.0074) | KEEP, supersedes T1 as the final model |
| T5 | The sign of what T4's step left behind, stacked on T4 | 0.5625 (p 0.79) | NULL |
| T6 | Only the final norm tensor (896 weights), at three step sizes | 0.5833 at every size | NULL, flat |
| T7 | Retrain a LoRA from the T4 model, take the sign of the new change | 0.5625 (p 0.80) | NULL (its full-precision ceiling reached 0.2083, so the fix existed but its sign carried only about a tenth of it) |

A pre-rounds diagnostic matters too: a sign patch applied to all 290 tensors at one global step size wrecked behavior (cap rate 45.8% to 83.3%). Untargeted binary updates hurt. Targeting and per-tensor step sizes are what made T4 work.

One comparison was run and settled by the author's decision: a factored, non-binary construction (the Fraction Compressor v0.4 method) on the same training delta reached dev degeneration 0.542 and 0.521 at two sizes, better on the flaw than T4's 0.6042, but it cost more on knowledge probes (mean target logprob -11.79 and -11.94, vs T4 -10.73 and base -9.94). The factored method stays the compressor method; Signet stays sign-restricted, and the factored arms never entered the Signet lineage.

## Controls

Every round carried the same controls, and they behaved as they should, with one exception noted in T7: random sign patterns scored near each round's starting point (in T7 they averaged 0.535, softer than the real edit, a warning that the dev metric flips marginal stories under almost any nudge at stacking doses), opposite edits hurt (one exactly cancelled a kept edit back to the original base rate), zero edits reproduced the starting rate exactly in all 7 rounds, and full-precision ceiling arms reproduced their trained models. Collateral was checked two ways each round, a 96-question probe set and a factual slice; the final edit improved both on dev (probe accuracy 0.198 to 0.2188, factual degeneration 0.292 to 0.0417).

## Honest limits

- The held-out family result is the weak point. On "station" stories, a theme absent from development and training, the gain was +4.17 points with a confidence interval that includes zero and worse. The edit generalizes across new prompts in known territory and to factual prompts; cross-theme generalization is unproven.
- The development set was 48 prompts, which resolves only about plus or minus 10 points. Rounds T5, T6, and T7 each landed a few points better than T4 and none could be separated from noise. The loop ended at a measurement wall, not a proven method wall.
- One planned arm never ran. The design included rounds proposed by a frontier model acting as editor (family (a)); that seat stayed unfilled while the training-delta line ran first, and the program closed with the arm untested.
- One model, one size, one flaw: Qwen2.5-0.5B base and its instruct twin, story degeneration only. Nothing here shows the method transfers to other models, sizes, or flaw types.
- Sign transfer is lossy and variable: about 44% of the trained ceiling's gain for the first delta, about 10% for the retraining delta in T7. The binary claim is about storage and simplicity, not superiority; per byte, the factored construction transferred behavior better in the bake-off.
- All numbers come from one pipeline on one machine, greedy decoding, float32. Determinism checks passed throughout (zero edits, seal hash, weight hashes), but no independent replication exists yet. That is what the reproduction steps below are for.

## How to reproduce

You need Python with torch, transformers, safetensors, and numpy, plus the official Qwen2.5-0.5B base checkpoint (a Hugging Face folder with config, tokenizer, and model.safetensors).

1. Build the T4 weights:
   `python apply_t4.py --base /path/to/base/model.safetensors --out t4.safetensors`
   This reads data/t4_signs.npz (packed signs, per-tensor step sizes, sha256 d7568a7f806996d240de556b502e56b12667d2843f7a08e33bfa92893943c810) and writes the edited weights. In this repository the npz ships split in two, as t4_signs_part1.npz and t4_signs_part2.npz at the repo root (about 22.5 MB each); apply_t4.py finds and merges the parts automatically, and merging them reproduces the file hashed above exactly. During the program, this reconstruction was checked tensor by tensor against the measured artifact and matched exactly on all 290 tensors of the rebuilt file (168 edited by the sign rule, 122 carried over untouched). The measured artifact itself is the file hashed in REPORT.md (sha256 ca123f513d5f282d6f7ea4147c5da0fbf51b997bd00aa8c3eb9d772e3c3d6756); the npz is the portable form of the same edit.
2. Put t4.safetensors into a copy of the base model folder as its model.safetensors.
3. Score base against T4 on the sealed items:
   `python evaluate.py --base-model /path/to/base_dir --edited-model /path/to/t4_dir`
   The printed table should match the sealed results in REPORT.md (story 0.8603 to 0.6912, all items 0.6518 to 0.5000, factual 0.1964 to 0.0357). The items in data/sealed_items.json are the original sealed file; its sha256 is 9b44d7b792c01297c6a3a1c446652e3c9de2172b856b2f365746e81c49676cff, so anyone can confirm the test was fixed before the edit existed.

Files: REPORT.md is the full closing report. FREEZE.md is the design freeze and its R8 amendment, verbatim. signet_scoring.py holds the frozen scoring definitions; evaluate.py is the scoring entry point. data/sealed_items.json holds the 224 test prompts with slice and family labels (publishable now that the seal is spent).

## License

MIT, (c) 2026 Vinay K Ganji Krishna. See LICENSE.
