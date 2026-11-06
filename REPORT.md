# Signet closing report: Qwen2.5-0.5B binary weight editing

Date: Fri 2026-11-06. Status: PROGRAM CLOSED by Vinay's order (main chat, 2026-11-06 14:03 ET), after one final sealed test run. Nothing here is published; the Fraction Compressor repo stayed frozen throughout.

## The question

Can a model's flaw be corrected with binary (sign-restricted) weight updates only, in a diagnose, propose, apply, measure, keep-or-revert loop, under a pre-registered freeze (rules R1 to R8)?

## The flaw

Flaw #1, certified in Phase 1: degenerate story continuation in Qwen2.5-0.5B base. The model runs to the token cap, loops repeated 8-grams, or drifts into CJK text instead of finishing a short story. Certification on 96 fresh prompts: base 53.1% degenerate vs instruct twin 38.5%. Dev set (48 fresh story prompts): base 0.833, instruct 0.146. Scoring frozen all program: greedy, 160 tokens, float32, degenerate = cap hit, or repetition share at least 0.3, or any CJK.

## The final model

Standing best: base + T4. T4 is the sign of the Arm T training delta (a LoRA trained on the flaw from instruct generations), applied from the original base with each of the 168 tensors at its own natural scale (per-tensor mean |delta|). One binary pattern plus 168 scale values; rebuild rule in the ledger diff. sha256 ca123f513d5f282d6f7ea4147c5da0fbf51b997bd00aa8c3eb9d772e3c3d6756.

Dev results: story degeneration 0.833 to 0.6042 (+22.92 pts, McNemar p 0.0074, bootstrap CI [8.33, 37.5]); probe accuracy 0.198 to 0.2188; factual degeneration 0.292 to 0.0417.

## The sealed test (run once, 2026-11-06; the seal is now spent)

224 items sealed 2026-11-05 before any editing round (sha256 9b44d7b792c01297c6a3a1c446652e3c9de2172b856b2f365746e81c49676cff), never shown to any editor process, scored with the frozen settings, nothing retuned. Base vs T4, paired McNemar and bootstrap CI (seed 7, 4000 resamples):

- All 224 items: base 0.6518 to T4 0.5000, +15.18 pts, p 8.2e-06, CI [8.93, 21.88]
- Story, all 136: base 0.8603 to T4 0.6912, +16.91 pts, p 0.00019, CI [8.82, 25.0]
- Story, seen families (112): +19.64 pts, p 0.0002, CI [9.82, 29.46]
- Story, held-out family "station" (24, theme never in dev or training data): base 0.8750 to T4 0.8333, +4.17 pts, p 1.0, CI [-8.33, 20.83]. No measurable gain on the wholly unseen family at this size.
- Factual (56): base 0.1964 to T4 0.0357, +16.07 pts, p 0.0117, CI [5.36, 26.79]
- Other genre (32): +6.25 pts, p 0.75, not significant (description sub-slice, n 10, ran 10 pts the other way)

Per family (story): childhood +33.3 pts (p 0.021), city +37.5 (p 0.031), forest +25.0 (p 0.031), sea +8.3 (p 0.69), village 0.0 (p 1.0), station +4.2 (p 1.0). Family slices are n 16 to 24, so only the pooled numbers carry real weight.

Failure modes on story: cap hits 83.8% to 64.0%, repetition 72.1% to 63.2%, CJK 0.7% to 0%. The edit mostly makes the model finish stories; it does not fully cure looping.

Probe accuracy on test items: not applicable. The sealed items are prompts only, with no answer choices, so the probe harness has nothing to score. Probe evidence stays at the dev/collateral level (0.2188, improved vs base 0.1979).

Verdict on the closing question: the dev gain held on unseen items. A sign-restricted edit, built without ever seeing the test, cut story degeneration by about 17 points and factual degeneration by about 16 points on fresh prompts, both significant, with collateral probes improved rather than harmed.

## Round ledger (dev set, 48 story prompts)

- Arm T training (LoRA on flaw #1, teacher = instruct generations on fresh prompts): ceiling 0.3125 degeneration (p 1.6e-06 vs base). The full-precision fix exists; everything after asks how much of it a binary edit keeps.
- T1: sign of training delta, one global scale, from base. 0.833 to 0.6458, p 0.035. KEEP, first verified binary fix (about 36% of the ceiling gain).
- T2: second identical sign step stacked (2x dose). 0.375 on the flaw but probe fell 2.09 pts against a 2 pt gate. REVERTED, gated null by 0.09 pts.
- T3: half step stacked (1.5x). 0.583, p 0.65. NULL, discordant churn.
- T4: per-tensor scaled sign from base. 0.6042, p 0.0074. KEEP, supersedes T1 as standing best. Captured about 44% of the ceiling gain with the probe intact.
- Bake-off vs Fraction Compressor v0.4 factored method (same delta, same tensors): factored reached 0.542 (rank 32, 0.41 bpw) and 0.521 (byte-matched rank 82) on the flaw with factual 0.000, but taxed probe logprobs more (mean target logprob -11.79 and -11.94 vs T4 -10.73, base -9.94). Vinay's decision 2026-11-05: keep v4. Factored stays the compressor method and stays out of the Signet lineage; Signet remains sign-restricted.
- T5: residual sign step on T4. 0.5625, p 0.79. NULL.
- T6: final-norm isolation (896 weights, sign of instruct delta at 0.1x, 0.3x, 1.0x). Flat 0.5833 at every dose. SWEEP NULL, item closed.
- T7 (Wonder arm): LoRA retrained from the T4-edited weights reached a full-precision ceiling of 0.2083 (p 0.0001 vs T4), better than the first ceiling and near instruct 0.1458. Its sign derivative: 0.5625, p 0.80. NULL; sign transfer fell to about 10% of the ceiling gain, and that round's random-sign controls averaged 0.535, softer than the real edit.
- Diagnostic D (Phase 1, pre-rounds): a global sign patch on all 290 tensors at the global mean scale wrecked behavior (cap rate 45.8% to 83.3%). Untargeted binary updates hurt; targeting and per-tensor scale are what made T4 work.
- Family (a), the frontier-model editor seat, never ran a round: the seat stayed unfilled under Vinay's direction to push the training-delta line first. The program closes with that arm untested.

Controls behaved in every round: random-sign means sat near each round's starting point (except T7, noted above), anti-edits hurt or cancelled exactly (T2's anti reproduced the original base rate), zero-edit reruns reproduced the starting rate exactly in all 7 rounds, and ceiling arms reproduced their trained models.

## Honest limits

- One model pair (Qwen2.5-0.5B base and instruct), one flaw, one training recipe. Nothing here shows the method transfers to other models, sizes, or flaw types.
- The held-out family result is the weakest point: on "station" stories, a theme absent from dev and training, the gain is +4.2 pts with a CI that includes zero and worse. The edit generalizes across prompts in known territory and to factual prompts; cross-theme generalization is unproven.
- The dev set (48 prompts) resolves only about plus or minus 10 points. T5, T6, and T7 all landed a few points better than T4 and none could be distinguished from noise. The loop ended at a measurement wall, not a proven method wall; a larger dev set would have been the next step and was declined at closing.
- Sign transfer is lossy and variable: about 44% of the ceiling gain for the first delta, about 10% for the retraining delta. The factored (non-binary) construction transferred behavior better per byte in the bake-off; the binary claim is about storage and simplicity, not superiority.
- The T7 ceiling (0.2083) shows a second full-precision training pass from the edited model goes far beyond what its sign derivative kept. Whether iterating train, sign, retrain converges somewhere useful is an open thread the program did not pursue.
- All numbers are from one executor pipeline on one machine (Flash), greedy decoding, float32. Determinism checks (zero arms, seal hash, best hash) all passed, but no independent replication exists.
- Nothing is published. Any future claim should quote the sealed test numbers above, not the dev numbers.

## Records

- Ledger: Flash ~/signet-qwen25/ledger/ (baseline map for all 290 tensors, one entry per variant per round, compact diffs that rebuild every edited model exactly, best/ with manifest and hashes), mirrored exports in goal hidden_files/phase2-out/.
- Sealed run: Flash ~/signet-qwen25/sealed/sealed_eval_results.json (aggregates and per-item flags; prompt texts were never written out by the eval).
- Design freeze: hidden_files/signet-qwen25-design-freeze-2026-11-05.md plus the R8 training-arm amendment. Seal record: hidden_files/signet-qwen25-seal-record-2026-11-05.md.
- Dashboard data export carries the final state (seal spent, closing numbers, program closed).
