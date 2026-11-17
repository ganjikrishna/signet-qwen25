# The Dials Can Be Turned by Hand

Author: Vinay K Ganji Krishna
Written with Muse Spark (Ember)
Draft, Tue 2026-11-17. Not yet published.

On Nov 2, 2026, four researchers at MIT CSAIL published something that deserves more attention than it got. They handed a frontier AI model, GPT-6 Astra, the raw weights of a small open model, Qwen3.5-0.8B, and let it edit those weights directly, the way a programmer edits code. No retraining. No gradients. The small model had a defect: it thought in loops and ran into its token limit on 93% of answers. Astra traced the looping to one harmful direction written into the MLPs of layers 15 and 19, and subtracted that direction from 64 output columns in each, 128 columns in all, and the model started finishing its answers. On MATH-500, scored with a budget of 50 forward passes per problem, it went from 7.9% to 48.1%. The whole edit touched 131,072 weights, 0.016% of the model.

I read their work with real respect, and one disagreement. This article is about that disagreement, and about a result of mine that was already public before their post appeared.

## Two ways to turn the dials

Think of a model as a machine with billions of tiny dials. Its behavior is just where the dials sit. Training is the slow, expensive way of setting them. The MIT work and mine both ask: can you set some of them by hand, on purpose, and prove the change did what you claim?

MIT's move was removal. The model already knew the answers; one bad pattern in its weights stopped it from answering. They found that pattern and subtracted it. The authors are honest about what this means, in their own words: the edit "lets the model finish answers it could already work out." It cleared a blockage. It added nothing, and they say plainly that this kind of edit cannot add an ability the model does not already have.

My move was addition. My base model, Qwen2.5-0.5B, was bad at something its own instruct sibling did well: continuing a story without falling apart into loops and repeated text. I ran one short training session on the base model, taught by the sibling's filtered examples. Then I threw the training away and kept only one bit of it per weight: which direction each dial had moved, up or down. I applied just those directions, with one scale per tensor, to a fresh copy of the base model. That edit is called Signet: the up-down signs of about 358 million weights across 168 tensors, one bit per weight, about 45 megabytes in all.

On a sealed test of 224 prompts the edited model had never seen, scored once and never re-run, story degeneration fell from 0.86 to 0.69. The same direction of improvement held on factual prompts. Control edits built from random signs did nothing, and flipping my signs upside down made the model worse, which is what you would expect if the directions themselves carry the information.

Here is my point of view, stated as plainly as I can state it. Removal is the right tool when a model has a defect hiding an ability it already owns. But when a model lacks a behavior and a teacher has it, you may not need to search the weights at all. A short training run already tells you which way every dial wants to move. The signs alone carry a usable part of that knowledge.

## The cost difference

Finding MIT's edit took 158 turns of a frontier model working for about 20.3 hours. That is frontier lab model time, the most expensive class of AI compute, and no dollar figure was published.

My training run took 2,014 seconds, about 34 minutes, on a desktop CPU. The sign extraction took seconds. The sealed test took about 20 minutes. Total cash cost: zero dollars, beyond a few cents of electricity. The models are open, the machine is the one under my desk, and anyone with a gaming PC can repeat it from the public code.

Neither number is the full end-to-end clock for either project, and I am not claiming otherwise. But the kind of resource each method needs is not close: a frontier lab, or a home computer.

## The direction is bigger than both of us

Just over a week after the MIT post, a company called Edge0 shipped a 145-billion-parameter model (51.2 billion of those parameters are an n-gram embedding table, not transformer compute) built by restructuring the weights of Qwen3.8-Flash-Next: they rebuilt its expert layers in a narrower form and retrained the new shape, cutting the expert bytes each token pushes through by about 30%. Their benchmark numbers are their own and nobody independent has verified them yet: on the card's own table the base model still leads on HLE, GPQA-Diamond, and IFBench, Edge0's lead is on the two agentic tests, and its technical report is still not out. Their license bars commercial product use without a separate written license, and Edge0's own release-scope file marks the exact training base revision as unverified. I cite them for one reason only: editing and restructuring weights is now something a company ships at production scale, not just something researchers and hobbyists try. On that point, MIT, Edge0, and a man with a desktop in Georgia all agree.

## What I am not claiming

Honesty is the whole value of a result like mine, so here are the limits, unedited.

Signet is proven on one model pair and one flaw. A held-out theme in the sealed test, stories about a station, improved only slightly and not significantly. The sign edit captured about 40% of what the full training run achieved; it is a partial transfer, not a free replacement for training. In my own bake-off, a factored method transferred behavior better per byte than signs did; sign's advantage is simplicity and size, not fidelity. And there is no head-to-head test between my method and MIT's, because they do different jobs on different models. Anyone who tells you one of these methods is simply "better" than the other, including me on a careless day, is selling something.

What I am claiming is narrower, and I think it is enough. Where a teacher already has the behavior, the sign of a short training run's changes, one bit per weight, can add part of that behavior to a base model. No frontier editor. No 20-hour search. Proven on a sealed test, with the code and the signs public and the failures disclosed.

## Dates and links

I keep the dates visible because credit in this field lives and dies on them.

- Oct 20, 2026: Fraction Compressor public on GitHub, including the first Signet sign-of-delta transfer test. The large Signet program ran Nov 5-6, after the MIT post, and used none of its inputs; the sign idea and its first test predate it.
- Nov 2, 2026: MIT, "Sparks of Weight-Space Programming," published. My hackathon submission was filed the same day.
- Nov 5-6, 2026: Signet program on Qwen2.5-0.5B; sealed test run once on Nov 6; program closed.
- Nov 11-12, 2026: Edge0 145B and 120B released.
- Nov 17, 2026: this article drafted.

Links:
- MIT post: https://rikiyat.github.io/blog/weight-space-programming/
- Signet: https://github.com/ganjikrishna/signet-qwen25
- Fraction Compressor: https://github.com/ganjikrishna/fraction-compressor
- Fraction Compressor demo video: https://www.youtube.com/watch?v=V2twYpXC3zU
- Edge0 model card: https://huggingface.co/Edge0/Edge0-145B-NVFP4
- My GitHub: https://github.com/ganjikrishna
