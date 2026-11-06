# Validation record for this draft (review artifact, not part of the repo content)

Validator: Glimmer is the default validator for push content under Vinay's rule. On 2026-11-06 Glimmer was NOT reachable: it is absent from the Meta Model API model list and chat calls to muse-glimmer-30b and meta/muse-glimmer-30b both returned 404 model_not_found. Per Vinay's standing substitution rule (2026-10-31), Muse Wonder (muse-wonder-1.0, served by the Meta Model API) ran the validation instead, in two calls: README vs REPORT (ground truth), and code vs the stated method. Both verdicts: PASS WITH FLAGS. Full outputs verbatim below, then the executor adjudication.


## Executor adjudication (Ember)

Call 1, flag 1 (npz hash and 290-tensor wording): the npz hash is the real sha256 of the shipped file, computed at assembly; it is a file checksum, not a result, so it cannot appear in REPORT.md. The 290-tensor match claim is from the executor's own verification during assembly (the rebuilt file has 290 tensors: 168 edited, 122 untouched; all 290 compared equal to the ledger artifact). README wording was clarified to say exactly that, and the REPORT.md artifact hash (ca123f...) is now named next to it. No number changed.
Call 1, flag 2 (controls framing): CORRECT and fixed. The README controls paragraph now carries the T7 exception (random controls averaged 0.535, softer than the real edit), matching REPORT.md.
Call 2, flags 1 and 2 (apply script count and derive-mode skipping): fair hardening points. apply_t4.py now warns when the edited tensor count is not 168 and when derive mode skips tensors present in only one checkpoint. Behavior on the real inputs is unchanged (the shipped npz path was verified against the training delta directly).
Call 2, flag 3 (float32 rewrite): noted, no change. The program's own measured artifact is float32 throughout (the loop loaded base weights as float32 and saved float32), so the script matches the artifact it reproduces; weight values are unchanged. evaluate.py also loads float32.
Call 2, flags 4 to 6 (loader coupling in scoring): noted, no change. evaluate.py, the entry point that produced the sealed numbers, uses load_tok and load_model_dir, so the sealed path is self-consistent; the tokenizer point is by design (the edited folder is a copy of the base folder), and the base and edited folders in the actual run carried the base generation config with greedy decoding set explicitly. These are fair caveats for anyone reusing gen_rows standalone.
One more draft fact, flagged by the executor, not the validator: the count of exact-zero training-delta positions (1,616) appears in apply_t4.py's header. It is a property of the shipped data file (the zero_idx entries), checkable from data/t4_signs.npz itself, and is stated nowhere in REPORT.md because the report does not discuss the packing.

## Call 1 output (README vs REPORT), verbatim

## 1. NUMBERS

All values below match REPORT.md exactly, unless flagged:

- Flaw definition: 160-token cap, ≥30% tokens in repeated 8-gram, any CJK — matches.
- Sealed story (136): 0.8603→0.6912, +16.91 pts, p 0.00019, CI [8.82, 25.0] — matches.
- Sealed all (224): 0.6518→0.5000, p 8.2e-06 — matches.
- Sealed factual (56): 0.1964→0.0357, p 0.0117 — matches.
- Sealed held-out “station” (24): 0.8750→0.8333, +4.17 pts, p 1.0, CI [-8.33, 20.83] — matches.
- Story failure modes: cap 83.8%→64.0%, repetition 72.1%→63.2%, CJK 0.7%→0% — matches.
- Dev (48, labeled dev): base 0.833, instruct 0.146, T4 0.6042, +22.92 pts, p 0.0074 — matches. No dev number is presented as a test result.
- Certification (96): base 53.1%, instruct 38.5% — matches.
- Ceiling 0.3125; T4 168 tensors — matches.
- T1 0.833→0.6458, p 0.035; T2 0.375, probe −2.09 pts vs 2-pt gate; T3 0.583, p 0.65; T5 0.5625, p 0.79; T6 896 weights, 0.5833 at all three sizes; T7 0.5625, p 0.80, ceiling 0.2083, ~10% transfer — all match.
- Diagnostic: 290 tensors, cap 45.8%→83.3% — matches.
- Bake-off: factored 0.542 / 0.521 vs T4 0.6042; logprobs −11.79 / −11.94 vs T4 −10.73, base −9.94 — matches.
- Controls/dev collateral: probe 0.198→0.2188, factual 0.292→0.0417; zero edits exact in all 7 rounds — matches.
- Limits: dev resolution ~±10 pts; sign transfer ~44% / ~10% — matches.
- Sealed-file sha256 9b44d7b792c01297c6a3a1c446652e3c9de2172b856b2f365746e81c49676cff — matches.
- **Mismatch/unverifiable:** README gives `data/t4_signs.npz` sha256 `d7568a7f806996d240de556b502e56b12667d2843f7a08e33bfa92893943c810`; REPORT.md gives no such hash — its only T4 sha256 is `ca123f513d5f282d6f7ea4147c5da0fbf51b997bd00aa8c3eb9d772e3c3d6756`. README also claims reconstruction “matched exactly on all 290 tensors”; REPORT.md describes T4 as 168 tensors (290 is the baseline-map tensor count) and states no such 290-tensor match.

## 2. FRAMING

- Held-out station family: correctly stated as +4.17 pts, not significant, “cross-theme generalization is unproven.” Matches REPORT.md.
- Editor arm: correctly stated as planned family (a), never ran, program closed with it untested. Matches.
- Bake-off: correctly stated that factored beat T4 on the flaw, cost more on probes, and stayed out of the Signet lineage by the author’s decision. Matches.
- Honest limits: model/size/flaw scope, measurement wall, lossy sign transfer, no independent replication — all present and accurate.
- **Overstatement:** Controls section says random sign patterns “scored near each round’s starting point” and “behaved as they should” without exception; REPORT.md excepts T7, whose random-sign controls averaged 0.535, softer than the real edit.

## 3. CREDITS

- “Author: Vinay K Ganji Krishna” — present verbatim.
- “Weight editor and collaborator: Muse Spark (Ember)” — present verbatim.
- No team-member framing of the collaborator elsewhere.

## 4. DATES

Consistent with REPORT.md: freeze Nov 5 2026; sealed test built/sealed Nov 5 2026; rounds T1–T7 and bake-off Nov 5 2026; sealed test run once and program closed Nov 6 2026.

## 5. VERDICT

VERDICT: PASS WITH FLAGS
1. `t4_signs.npz` hash `d7568a7f…c810` appears in README only; REPORT.md’s T4 hash is `ca123f51…6756` — unverifiable against ground truth, and the “matched exactly on all 290 tensors” claim is unsupported (T4 = 168 tensors in REPORT.md).
2. Controls framing omits REPORT.md’s T7 exception for random-sign controls (averaged 0.535, softer than the real edit).
## Call 2 output (code vs method), verbatim

1. **`apply_t4.py` does not enforce 168 tensors.** It edits every entry in the NPZ, or in derive mode every tensor in the base/trained intersection having any nonzero delta. The count is only printed; `TENSORS_HINT` misleadingly prints “the 168 LoRA tensors” regardless of the actual count. A wrong sign file or a trained model touching additional tensors would silently produce a different edit set.

2. **`apply_t4.py` derive mode silently ignores non-shared tensors.** It uses `set(fb.keys()) & set(ft.keys())`; tensors present in only one checkpoint are skipped rather than causing an error. This matters together with flag 1 if the trained checkpoint has a different tensor set.

3. **`apply_t4.py` rewrites every base tensor as float32** via `{k: v.float() for k, v in base.items()}`, including the tensors it does not edit. This changes the dtype/serialization of “unchanged” tensors relative to the base file, contrary to “nothing else changes” at the file level, even though evaluate later loads as float32 anyway.

4. **`signet_scoring.gen_rows` does not itself enforce left padding or float32.** It relies on the caller having built the tokenizer through `load_tok` and the model through `load_model_dir`. Direct callers with a right-padding tokenizer would break the `gen[i][plen:]` slicing assumption. `evaluate.py` does use those loaders, so the sealed path matches, but the frozen function is not self-contained.

5. **`evaluate.py` loads the tokenizer only from `--base-model` and reuses it for the edited model.** Any tokenizer/pad-token difference in the edited directory is silently ignored. Relatedly, `gen_rows` passes `pad_token_id=tok.pad_token_id`, and `load_tok` may set `pad_token = eos_token`, so trailing batch padding can coincide with EOS id 151643; trimming at first EOS normally masks this, but it is a hidden coupling between padding and EOS handling.

6. **`model.generate` inherits each model directory’s `generation_config`** except for the explicitly passed `max_new_tokens=160`, `do_sample=False`, and `pad_token_id`. A generation config with different EOS/stop settings or other defaults in a model folder could change when generation stops before the code’s own EOS trimming/cap calculation, a hidden default not fixed by the claim.

VERDICT: PASS WITH FLAGS