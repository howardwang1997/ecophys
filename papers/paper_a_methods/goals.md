# Paper A — Goals & alignment principles

**Date crystallized**: 2026-04-25
**Status**: foundational reference. Every section, figure, and ablation
in Paper A must derive from these goals.

---

## 0. Project hierarchy (recap)

The EcoPhys / EcoMD project produces three papers, in service of one
scientific question: **are markets describable by a non-equilibrium
thermodynamic theory with universal critical-scaling signatures?**

| Paper | Role | Venue target | Status |
|---|---|---|---|
| **Paper A** | **Methodology** — the simulator + calibration pipeline | ICAIF 2026 (primary), arXiv preprint Wk 28 | drafting |
| **Paper B** | Physics — universal T_eff scaling + Jarzynski + TUR | Nature Physics → PRL retreat | data collection (high-freq vendor purchase pending) |
| **Paper C** | Applications — crash EWS, optimal execution | Quantitative Finance / JEDC | future |

**Paper A exists to enable Paper B.** Every choice in Paper A — the title,
the architecture, the claims, the ablations — must serve this purpose.

---

## 1. Paper A's primary goal

Deliver a **calibrated, differentiable, particle-based simulator** that
Paper B's physics protocols can run on.

**"Calibrated"** means: trained to reproduce real-data statistical
properties (Cont (2001) stylized facts) so that measured quantities
(T_eff, entropy production rates) reflect actual market structure
rather than artifacts of the model's noise floor.

**"Differentiable"** means: gradient-based calibration in O(10²)
optimizer steps, vs Simulation-Based Inference's O(10⁴+) forward
rollouts in ABIDES literature. Paper B needs to recalibrate around
specific event windows (FOMC, earnings) — only feasible with gradients.

**"Particle-based"** means: each agent has individual state; forces
decompose per-particle; entropy production decomposes per-channel.
GAN/diffusion sims lack this structure. Mean-field SDEs lack this structure.

---

## 2. Paper A's secondary goal

**Establish architectural rigor** — show that our architecture choices
are evidence-based, not chosen by aesthetics. Reviewers in 2026 are
sensitive to overclaimed novelty; the v2 ablation history (33 configs
of v2.0 stuck at 4/11 → diagnosis → v2.1) is exactly the kind of
quantitative honesty that makes a methodology paper trustworthy.

This is **not the same** as a paper whose primary contribution is
"systematic ablation." It is methodology with rigorous ablation as
support material.

---

## 3. Goals that are EXPLICITLY OUT OF SCOPE

| Off-goal | Why off-goal |
|---|---|
| Beat ABIDES on stylized facts | ABIDES already does ~7/11; we don't need to beat, we need to *match within rigour budget* |
| Beat GAN/diffusion baselines on distribution match | Different family of methods; head-to-head benchmarking is a separate paper |
| Claim equivariant GNN novelty | Honest analysis of v2.1 shows weaker equivariance than v0.x. Overclaiming this hurts credibility. |
| Derive architecture from microstructure theory alone | Tried (v2.0, 33 configs). 5 of 6 theory-suggested ingredients failed. The architecture is empirically chosen. |
| Demonstrate Paper B's physics findings | That is Paper B. Mentioning T_eff in Paper A is forward-looking, not a contribution. |

---

## 4. Title alignment

The title must:
1. **Lead with the deliverable**: "calibrated, differentiable, particle-based"
2. **State the purpose**: "for non-equilibrium analysis of financial markets"
3. **NOT mention**: equivariance (overclaim), specific architecture name (too narrow), comparisons (off-goal)

**Selected title** (2026-04-25):
> *EcoMD: A Calibrated Differentiable Particle Simulator for Non-Equilibrium Analysis of Financial Markets*

**Rejected titles** with reasons:
- ~~"Equivariant GNN derived from microstructure symmetries"~~ — overclaim,
  v2.1 has weaker equivariance than v0.x; "derived from" implies a
  derivation that 5 ablations falsified.
- ~~"Differentiable Typed Pair Potential for Market Simulation"~~ —
  describes the architecture but not the goal. Paper A's purpose is not
  to advertise the architecture; it's to deliver a tool.
- ~~"What Doesn't Work in Differentiable Market Simulation"~~ — leads with
  negative framing; while ablation rigor is a virtue, leading with it
  signals the paper has nothing positive to deliver, which is false.

---

## 5. Each section must answer "how does this serve the goal?"

Section-by-section justification. If a section can't answer this in
one sentence, it must be rewritten or cut.

| Section | Goal-justification |
|---|---|
| 1. Intro | Frames the demand for a calibrated differentiable particle simulator (= the deliverable). |
| 1.5. Paper B requirements | Explicitly motivates the design from downstream measurement needs. |
| 2. Related work | Demonstrates that existing tools (ABIDES, GAN, MACE-style GNNs) don't meet all three criteria simultaneously. |
| 3. Method | Presents the simulator + recipe. Each architectural choice cross-referenced to which Paper-B requirement it satisfies. |
| 4. Architecture ablations | Provides evidence-based justification for each choice. **Negative results** (gauge, Kyle, MACE) are framed as "what we ruled out" not as "interesting failures." |
| 5. Calibration | 7/11 SPX + 7/11 BTC 1m. Frames as "sufficient for Paper B's measurements", not as SOTA claim. |
| 5.4. OOS crash | Validates simulator generalises to unseen regimes — required for Paper B's crash precursor analysis. |
| 5.5. Cross-asset | Validates simulator transfers between asset classes — required for Paper B's universality claim. |
| 6. Discussion | Looks forward: enabled measurements; remaining limitations; explicit pointer to Paper B. |

---

## 6. Concrete decisions that follow from this goal alignment

1. **Architecture story arc**: NOT "we propose v2.1." Instead, "we
   need a particle simulator with X, Y, Z properties; we tried two
   architecture families (v0.x simple, v2 microstructure-informed);
   ablations selected v0.x-style typed pair MLP + Hawkes; v2.1 is the
   chosen instantiation."

2. **Negative results placement**: §4 (ablations), NOT §3 (method) and
   NOT §1 (intro). Method presents the chosen design; intro states the
   goal; ablations justify the chosen design.

3. **Comparison table**: present as "11 stylized facts × {real, GARCH,
   v0.x, v2.1, v1 MACE attempted, GAN baseline if added}". The v1 MACE
   row is the strongest negative result and goes IN the table, not
   only in §4 prose.

4. **Hawkes**: motivated by Paper B (vol clustering is the central
   phenomenon Paper B's T_eff measures). Not just because we found it
   helps stylized facts.

5. **Type embedding**: motivated by Paper B's universality claim
   (different markets / regimes have different agent populations;
   typed model lets θ transfer across markets). Not just because
   K×K coupling is novel.

---

## 7. Continuity with Paper B

Paper A must end with a **single concrete handoff** to Paper B:

> "The calibrated EcoMD simulator described in this paper provides the
> measurement substrate for [Paper B reference]. Specifically, the
> per-particle force decomposition (§3.1), Hawkes-augmented price
> formation (§3.3), and FOMC-windowed gradient calibration (§5.5)
> together enable the multi-timescale T_eff and Jarzynski-protocol
> measurements reported there."

Paper B's first section will reference Paper A's §3.1, 3.3, 5.5 by
name. Reviewers seeing both papers will see seamless continuity.

---

## 8. Writing-time check: every paragraph

Each paragraph in Paper A must answer one of:

1. *Why is this part of a calibrated differentiable particle simulator
   that Paper B can use?*
2. *What evidence justifies this architectural / training choice?*
3. *What does this measurement (stylized facts, force probes, ACF
   shape) tell the reader about the simulator's fitness for purpose?*

If a paragraph answers none of those, it's filler and should be cut.

---

## 9. Living document

This file is the source of truth for Paper A's framing. When
disagreement arises (or a reviewer suggests changes), come back here
first. Do not let the paper drift away from these goals during writing.
