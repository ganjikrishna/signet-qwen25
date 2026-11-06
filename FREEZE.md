# Signet fresh-start program: design freeze (Thu 2026-11-05)

Program: Qwen2.5-0.5B base, binary (sign-restricted) weight updates proposed by a frontier editor, flaw-targeted, measured on a frozen eval. Thesis (Vinay): correcting or adding to a model via binary updates.

## Panel (design review, full context pack, raw outputs in panel-signet1/)

Seats answering in full: Spark 1.2, Spark 1.1, Wonder, GPT-OSS 120B, Gemini (on gemini-3.5-flash). DeepSeek: partial (reasoning delivered, final answer not). Grok 4.7: unavailable (route returned "Service temporarily unavailable" twice). Nothing filled in for missing seats.

Consensus:
- Edit family (a): sign of the base-to-instruct delta restricted to editor-chosen tensors, ONE global scale. (GPT-OSS dissented, wanted per-tensor scales first.) Fallback (c) per-tensor scales only after (a) retires under the gate below.
- The 96-question eval alone cannot support a publishable claim. Grow a fresh sealed test before any claim; the editor never sees test items or per-item test results.
- Controls mandatory from round 1 (below).
- Everyone's named failure mode is the same: a powerful editor hill-climbing a tiny dev set (adaptive overfitting).

## Frozen rules (director's freeze, Ember, from the panel)

R1 Flaw choice: flaw #1 = the biggest measured base-to-instruct gap among flaws passing all filters: at least 10 discordant items (instruct right, base wrong), gap at least 0.15, and the gap consistent across split halves of the eval. The ranked menu is frozen before the editor sees any weights. A sign-probe (global sign-of-delta patch) is run on the top 3 flaws as a logged diagnostic only; it does not reorder the menu. If flaw #1 retires as intractable, flaw #2 is next by rank.

R2 Eval: the existing 96 questions are the DEV set. Before any publishable claim, build a fresh sealed TEST of at least 200 items from the same distribution plus paraphrases of the flaw family, never shown to the editor. The loop's working metric is logprob margin on the flaw slice; accuracy is reported at milestones on the sealed test. Editor receives dev aggregates and flaw-slice results, never test anything.

R3 Edit family: round 1 uses (a). One binary edit per round: named tensors, sign pattern = sign of the base-to-instruct delta on those tensors, one global scale, written prediction (direction and rough size) logged before measurement.

R4 Keep/revert: keep only if the flaw-slice dev metric improves beyond noise (paired test, McNemar p < 0.05 or bootstrap CI excluding zero) AND collateral gates hold (overall dev accuracy drop no more than 2 points; collateral probe set drop no more than 2 points). Otherwise revert. No trending-right keeps.

R5 Stopping: 5 consecutive null rounds on (a) retire (a) for that flaw. Fallback (c) is allowed only if the full-precision delta restricted to the same tensors (the ceiling control) actually moved the flaw; (c) gets 5 rounds. Still null: the flaw is logged binary-intractable under this program and the next flaw by rank is taken. No rescues, no rule edits mid-flaw.

R6 Controls, every round, same tensors and scale as the proposed edit: (1) random sign pattern, 3 seeds, mean reported; (2) anti-edit, the negated sign pattern; (3) full-precision delta restricted to the same tensors (ceiling); (4) zero-edit rerun (noise floor, base re-eval variance); (5) collateral probe set of unrelated behaviors. Instruct is the gap ceiling, reported at Phase 1 and at milestones.

R7 Regression protection (Vinay, added Thu 2026-11-05): every kept fix joins a protected regression set. When any later edit is measured, and again before moving to the next flaw, all previously fixed flaws are re-tested on their slices. If a new edit breaks an earlier fix, the new edit does not ship. The model only accumulates verified fixes. This rule is built into the Phase 2 loop design and into the sealed test plan (the sealed test carries a slice per fixed flaw for exactly this re-test).

R7 Regression protection (Vinay's rule, Thu 2026-11-05): every kept fix joins a protected regression set. When any later edit is measured, and again before moving to the next flaw, all previously fixed flaws are re-tested on their slices. If a new edit breaks an earlier fix beyond the noise rule, the new edit does not ship; it is reverted or redesigned. The model only ever accumulates verified fixes.

## Web check: documented Qwen flaw candidates (Vinay's addition, Thu 2026-11-05)

Candidates enter the flaw menu only if our own Phase 1 measurement confirms them on this checkpoint. Sources are leads, not evidence.

1. Repetition and verbosity of the base model. A Stanford CS224R study on this exact model (Qwen2.5-0.5B) found the base produces repetitive, inflated responses, and naive SFT scored below the base on win rate (43.8% vs 50.0%). Measurable: repetition rate and length on open prompts. Source: cs224r.stanford.edu/spring_2025/projects/pdfs/CS_224R_Final_Paper_2.pdf
2. Training-metadata deflections and hallucinated self-descriptions ("I was trained on..." style answers). Same study. Narrower slice; fold into the menu if measurement shows a rate.
3. Language drift / unexpected code-switching into Chinese. Documented across the Qwen family (code-switching study incl. Qwen-3, arXiv 2507.14894; a Language Confusion Benchmark exists). Not yet measured on Qwen2.5-0.5B specifically; Phase 1 verifies (English prompts, non-English output rate).
4. Failure to terminate, rambling to the token cap with repetitive suffixes. A documented Qwen-family pattern (EOS-mismatch work on Qwen3 base students, arXiv 2609.20511). Overlaps candidate 1; measure cap-hit rate.

Traps to avoid (documented):
- Tool-calling format failures on Qwen2.5-0.5B were traced to an upstream chat-template bug, not the weights (toolhound analysis: all 17 failures template-caused). Not a weight-edit target.
- Public benchmark scores for Qwen2.5 are contamination-suspect (AAAI work on MATH-500 memorization in Qwen2.5). Another reason the sealed test is built fresh.
- Hallucination of niche facts and multi-step reasoning depth are real but are capability limits; the panel's logic says they are the least likely to move with sign-only updates. Deprioritized unless the measured menu says otherwise.

## Amendment (Thu 2026-11-05, Vinay's decision in the main chat)

R8, the training arm (Arm T), is added: train a flaw-targeted fix on the base (LoRA, v0.4 baseline shape), derive binary sign edits from the training delta, judged under the same R2, R4, R6, R7 gates, running in parallel with family (a). Full text: signet-qwen25-training-arm-amendment-2026-11-05.md. R1 to R7 are unchanged.


---

# Signet Qwen2.5-0.5B: training arm amendment, R8 (Thu 2026-11-05)

Director amendment to the design freeze (signet-qwen25-design-freeze-2026-11-05.md). Decided by Vinay in the main chat on Thu 2026-11-05: "Add the training arm now." This adds a rule; it does not change R1 to R7. Editor family (a) rounds continue in parallel.

## Why (the v0.4 evidence, checked by Ember against the repo on 2026-11-05)

Vinay's point, verified: the v0.4 headline factored patch involved no training by us; it converted Qwen's own official base-to-Instruct delta into a 1-bit format. The one artifact in v0.4 that we trained ourselves, a LoRA adapter distilled from the full fine-tune (1,500 fresh prompts, teacher = the fine-tune's own greedy generations, about 8 hours of training, 18.7 MB), beat the patch on the same 96 questions: gap closed 1.36 vs 0.23, first-token accuracy 0.167 (tying the full fine-tune) vs patch 0.010. Caveat recorded at the time: the adapter specialized to the probe style. Lesson carried into this program: a trained, flaw-targeted delta is the proven route; sign editing of an existing delta is the unproven one. Both now run, judged by the same gates.

## R8: the training arm (Arm T)

R8.1 What Arm T is. Train a small fix aimed only at flaw #1 (story degeneration) on the base model, take the trained change (the training delta), and derive binary edits from THAT delta. The ship candidate is still a binary edit under the Signet thesis. The trained model itself is measured and reported as Arm T's ceiling (the same role the instruct model and the full-precision restricted delta play for family (a)); it is not the Signet result unless Vinay later rules otherwise.

R8.2 Training data. Fresh prompts only: never dev items, never sealed items, never Phase 1 prompts. Teacher: the instruct twin's own generations, filtered by the frozen degenerate scorer (a training example's continuation must terminate before the cap, repetition share under 0.3, no CJK). Training set: story continuations as the main body, plus a replay slice of factual and instruction examples (instruct generations, same filtering where the scorer applies) to protect collateral behavior. Log the data file's sha256, prompt count per slice, filter pass rates, and the generation settings. The base model's core failure is non-termination, so every story target must end with a proper ending and the EOS token.

R8.3 Training method. LoRA on the base model, following the v0.4 baseline's shape (it is the proven recipe in our own records): rank and target modules, learning rate, epochs, and sequence length are the executor's choices within these bounds: one training run, sized for Flash CPU (11 GB RAM total, peak under about 8 GB for training, and it must not starve the editor loop's measurements; run it as its own systemd user unit, logs in the home dir). Full fine-tune is allowed instead only if the executor shows the LoRA route is blocked. Log the full config in the ledger before training starts. Cost honesty: the v0.4 LoRA took about 8 hours for 1,500 examples; size this run so it lands in hours, not days, and state the expected size and time in the round log before launching.

R8.4 The binary derivative. After training: compute the training delta (trained weights minus base) per tensor and record its stats in the ledger baseline style. Then ONE derivative round under the same discipline as R3: a written proposal logged before measurement (author: the editor seat or the executor from the delta stats, named in the log) choosing the tensors and ONE global scale for sign of the training delta. Measure exactly like a family (a) round: dev story degeneration paired vs the frozen baselines, all R6 controls at the same tensors and scale (random signs 3 seeds, anti-edit, full-precision restricted ceiling = the training delta restricted to the same tensors, zero-edit rerun), collateral (96-probe accuracy, factual slice), R4 keep gates, R7 regression re-tests.

R8.5 Variants and stopping. If the first derivative is a null but the trained model itself (the ceiling) clearly moved the flaw on dev, up to 2 further derivative variants are allowed (different tensor sets or scale), each with its own pre-logged proposal and full controls; they count as Arm T rounds, not family (a) nulls. If the trained model itself does not move the flaw on dev, Arm T stops and is logged as a trained-ceiling null; a second training run needs Vinay's call. R5's 5-null retirement applies to family (a) only; Arm T has its own count.

R8.6 Ledger and dashboard. The training run is a weight event in the ledger (config, data hash, steps, wall time, peak memory, per-tensor training-delta stats). The trained weights are saved under ledger/ as a lineage artifact (the adapter file plus its config is enough if LoRA; the delta must be exactly reconstructible). Derivative rounds get normal ledger entries and appear on the dashboard like family (a) rounds, labeled Arm T.

R8.7 Sequencing. Arm T runs in parallel with editor round 1: data generation and training may start now, while the editor pack and round 1 proposal proceed. Measurements from the two arms never share a model copy. Headlines to the main chat stay in Vinay's format: the flaw, the fix tried, did it work, one headline when training launches (with size and expected time), one when the derivative is measured.

## What does not change

R2 sealed test rules (Arm T never sees sealed items; its training data is fresh and disjoint, and the disjointness check against dev and sealed prompts is logged: exact match and near-duplicate screen, the v0.4 novelty-check shape). R4 gates, R6 controls, R7 regression protection: identical for Arm T derivatives. Nothing public; repo frozen during judging.
