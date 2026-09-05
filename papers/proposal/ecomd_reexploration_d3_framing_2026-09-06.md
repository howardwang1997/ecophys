# Re-exploration D-3 framing: GAMMA and ALPHA (2026-09-06)

Stage: D_minus_3 question_framing under decision `pi_topic_reexploration_directive_20260906`.
Outcome access: **none**. No simulation, no GPU, no data access, no route-level decision. This
document frames the two pre-screened families into the protocol's required elements (native
scientific object, intervention, observable, invariances, explicit nonclaims), specifies target
theorems and audit designs, and assigns each family's D-2 hostile neighborhood. The search-cycle
ledger entry is appended at cycle completion.

---

## Family GAMMA — matching-fiber gauge non-identifiability of matched/cleared training

### Native scientific object

The **training identification of a generative market simulator whose loss observes its raw
output only through a mechanism layer**. Formally: discrete-time market state
`s_t ∈ S` (book with resting units, accounts); a neural simulator outputs intended flow
`z_θ(s_t) ∈ Z`; a mechanism layer

```
M_k : Z × S × Ω → Y_g × S
```

maps intended flow, state, and internal randomness `ω` to a tape increment at tape granularity
`g` plus the next state, under priority kernel `k ∈ {fifo, pro_rata, random_unit}`. Training
loss `L(θ) = Σ_t ℓ(M_k(z_θ(s_t), s_t), y*_t)` depends on `θ` only through `M_k(z_θ(s_t))`.

The object is the **mechanism fiber** `F_M(z; s, g) = {z′ : M(z′; s) = M(z; s)}` (deterministic
kernels) or the likelihood-equivalence class `{z′ : P_ω(M(z′) = ·) = P_ω(M(z) = ·)}` (stochastic
kernels): what training through `M` can and cannot identify about the learned raw map.

### Intervention

Within-fiber surgery on a locked, trained checkpoint: edits `z_θ → z_θ + δ` with
`δ` in the tangent cone of the fiber are **exactly loss-invariant by construction**; the
intervention exposes whether downstream consumers of the raw flow (distillation, latency
truncation, kernel swap, raw-flow risk aggregation) diverge. Also: kernel replacement
`k → k′` and tape-granularity changes `g → g′` as mechanism-side interventions on the same
locked weights.

### Observable

(i) Fiber dimension/structure per `(k, g)` under a linear order-flow parameterization;
(ii) likelihood Fisher-information rank on `Z` per kernel; (iii) downstream divergence
`‖C(z) − C(z′)‖` for within-fiber pairs under a fixed consumer `C: Z → R^d`;
(iv) cross-seed gauge wander: distribution of pairwise raw-output distances among checkpoints
with equal tape fit.

### Invariances (the claim structure)

Training is invariant along fiber directions — this is the theorem, not an assumption. The
nonclaims are as explicit as the claims: see below.

### Target theorems (D-1 proof attempts; none claimed yet)

- **T1 (fiber taxonomy).** For uniform-price clearing with quantity aggregation:
  - deterministic kernels (`fifo`, `pro_rata`): the fiber is a positive-dimensional preimage;
    under a linear parameterization its tangent dimension is `dim Z − rank` of the recorded
    linear map on the cleared portion, plus all uncleared-excess directions. Tape granularity
    `g` coarsens the recorded map and enlarges the fiber (per-order tape records more than
    aggregate prints; per-unit allocation tape records more still).
  - `random_unit` kernel with **per-unit allocation tape**: the likelihood over draws without
    replacement (probability proportional to remaining `q`) identifies strictly more than the
    deterministic preimage at the same granularity — **gauge shrinkage under randomized
    kernels** — but never fully: exchangeable-agent symmetries remain.
  - `random_unit` kernel with **aggregate tape**: the allocation randomness marginalizes out
    and the likelihood collapses to the deterministic aggregate — shrinkage disappears.
    Punchline: identification depends on the **interaction** of kernel randomness and tape
    granularity, not on either alone.
- **T2 (consumer instability).** For unbounded `Z` and a consumer `C` with growth along a
  recession direction of the fiber: within-fiber pairs achieve unbounded `C`-divergence at
  exactly zero training-loss change. Bounded version: within-fiber `C`-variance lower bound
  under a reference measure. The rank-one projection gauge of Paper D (fiber `z + α(x)a`) is
  the minimal special case.
- **T3 (partial-mechanism exposure).** Characterize the **training-silent but
  deployment-detectable set** `F_M \ F_D` for deployment maps `D` (identity = raw consumption;
  `M_{k′}` kernel swap; `M ∘ π` latency/message truncation) per `(k, k′, g)` triple. Paper D's
  "remove the projector" cell is the `D = id` special case; the market version adds kernel-swap
  and truncation directions absent in PDEs.
- **T4 (SGD fiber selection) — conjecture, labeled.** Implicit regularization selects
  low-norm fiber representatives in the rank-one case (analyzable); combinatorial case open.
  Empirical signatures only; never stated as a theorem without proof.

### Synthetic signature experiments (design only; no execution authorized)

- S1 gauge wander: train small simulators through `M` under each kernel × granularity;
  measure cross-seed raw-output dispersion at matched tape fit. Prediction from T1: dispersion
  ordered by fiber dimension.
- S2 surgery cells: within-fiber edits, kernel swaps, truncation on locked checkpoints;
  divergence measured on `C`. Prediction from T3: divergence localized to the detectable
  coordinate set.
- S3 identification check: Fisher-information rank on `Z` by kernel × granularity
  (T1's likelihood side).

### Explicit nonclaims

- No claim about real markets, real exchanges, or any deployed production simulator.
- No claim that any specific published simulator was trained through a mechanism layer.
- No gradient-estimation claim (differentiating through matching is an occupied lane:
  Lee–Yu–Yang, Parmas–Sugiyama, Potto, StochasticAD/ADEV, EventFBP).
- No inference claim (tape-to-parent-order reconstruction non-identification is a different,
  occupied estimand — own ledger).
- T4 stays a conjecture unless proved; inconclusive results trigger stop rules, not narratives.

### D-2 hostile neighborhood assignment (≥ 15 primary works)

Transportation-polytope fiber theory (classical); OT in ML (Cuturi 2013; Blondel et al. 2020;
Genevay et al.) — *differentiation vs training identification*; implicit/deep-equilibrium
layers; gauge symmetries in neural networks (weight permutation, scale symmetries, simplex
gauge in flows); econometric matching identification (Choo–Siow 2006; Galichon–Salanié
lineage); random assignment mechanisms in market design (Abdulkadiroğlu–Sönmez;
Bogomolnaia–Moulin) — *mechanism randomness known, training identification not*;
simulation-based inference with non-identified summaries; cycle-7 nullspace result (internal,
consistent-not-colliding); own metaorder-reconstruction audits (internal). Adjudication
standard: a work that states *training/likelihood non-identification of pre-mechanism outputs
modulo the mechanism fiber* is a direct collision; mechanism-randomness or differentiation
results alone are adjacent.

---

## Family ALPHA — plug-and-play attribution audit for mechanism layers in market simulators

### Native scientific object

An **autoregressive market simulator trained with an exact mechanism layer** (execution forced
through exact clearing/accounting: volume conservation, cash conservation, nonnegative
inventory bookkeeping — lab-asset-v3 engine semantics), audited by the Paper D eight-cell
factorial: output coordinate `{absolute next state, increment}` × training enforcement
`{raw, through-M}` × inference enforcement `{raw, through-M}`, four trained arms plus four
zero-training surgery cells on locked weights.

### Intervention

The eight-cell cube itself (mechanism-layer presence at training × at inference, crossed with
output coordinate), with paired seeds sharing trajectories, minibatch order, and initial
tensors — the frozen Paper D contract verbatim.

### Observable

Primary: conserving-channel rollout error against the synthetic DGP's exact truth in the
primary cell (OOD population-scaled, fixed horizon — the market analogue of Paper D's OOD-512 /
horizon-16). Secondary: stylized-fact distance vector (existing `stylized_facts.py` machinery),
accounting-drift, horizon-resolved cells with Holm correction.

### Invariances / statistical contract (inherited from Paper D, verbatim)

Seed = inference unit; 50,000-draw paired bootstrap; SESOI `δ = 0.1·Ȳ_R00`; ordered
classification {material non-additivity / smaller statistical non-additivity / practical
additivity / unresolved}; sign-flip secondaries Holm-corrected across mandatory cells;
one-shot analyzers with record-coverage and checkpoint-lock gates.

### Market-native design elements (the anti-"domain transfer" burden of proof)

1. **Primary layer is combinatorial/integer**, not a linear projection: clearing with unit
   integerality, tick-lattice price grid (registered secondary layer variant).
2. **Two DGPs**: lab-asset-v3 dual-arm engine (exact, replay-complete) as primary truth;
   `synthetic_dgps.py` family as robustness truth — no single-DGP overfit.
3. **OOD axes are market-native**: agent-population scaling, tick-size shift, and
   **priority-kernel shift (FIFO ↔ random-unit)** — the last bridges directly to GAMMA T3.
4. **Reflexive evaluation cell (registered secondary, labeled exploratory)**: the trained
   simulator deployed against a simple adapting execution policy; measure execution-cost/welfare
   gap vs DGP. This axis (deployment = interaction with an adapting consumer) does not exist in
   the PDE setting and is the strongest novelty claim — kept secondary to control scope.
5. **Two lineages, honestly gated**: L1 EcoMD v2 (transformer/potential family); L2 recurrent
   fact-surrogate (existing `fact_surrogates.py` baseline). The architecture-transfer gate is
   preregistered with the U-Net lesson: a failed transfer is reported as a boundary, not buried.

### Compute and data budget (D1, only after D0 freeze + explicit PI authorization)

4 trained arms × 30 seeds × 2 lineages at Paper-D model scales ≈ Paper D × 2; ≤ 2–3 weeks
wall-clock on 2×V100; surgery cells free (zero training). Ops prerequisite: V100 disk cleanup
(98%/96%). Data: synthetic DGPs + public/free stylized-fact bridge via existing ingests
(`lobster_ingest`/`binance_ingest`/`yfinance`); zero purchase; crash-event reserves untouched.

### Explicit nonclaims

- No real-market intervention claim; no claim that production simulators train through
  mechanism layers (the audit concerns the design pattern, not any named system).
- Conditional on the two DGPs and two lineages; no architecture-general or DGP-general claim.
- Reflexive cell is exploratory and cannot rescue or upgrade any primary classification.
- No superiority claim for constrained training — the estimand is path-dependence attribution,
  exactly as in Paper D.

### D-2 hostile neighborhood assignment (≥ 15 primary works)

Duruisseaux et al. 2024 (parent — must be positioned as the linear/PDE special case we extend
to combinatorial mechanism layers); GradABM (Chopra et al. 2023) and Dyer et al. 2023
(differentiable market ABMs — feasibility, not attribution); the hard-matching gradient lane
(Lee–Yu–Yang; Parmas–Sugiyama; Potto; StochasticAD; EventFBP) — *estimand distinction:
empirical identification audit, not gradient estimation*; decision-focused simulator training
(Gen-DFL; Diff2SP); simulator-internal mechanism decomposition (Chen 2026;
Hashimoto–Izumi 2025); **market-ABM validation and calibration tradition (Franke–Westerhoff
stylized-fact validation; global sensitivity analysis of ABMs)** — sharpest adjacent parent:
they validate/calibrate parameters against stylized facts, we audit training-time
mechanism-layer attribution under exact truth; **scheduled sampling / exposure bias**
(teacher-forcing mismatch is about supervision targets, not mechanism-layer path dependence —
must be explicitly distinguished); differentiable-environment / agent–environment co-training
in MARL (**highest collision risk — search hardest**: any work ablating "train through the
environment mechanism vs not" is a direct collision); constraint-layer literature beyond PDE
(equivariant/hard-constraint layers).

---

## Merge/split decision (D-3 output; final merge gate at end of D-2)

**Recommendation: target ONE paper** with GAMMA T1–T3 as the theory core and the ALPHA cube as
the experimental section — the exact Paper D template (propositions + factorial audit), because
the logical chain is the same phenomenon: fiber non-identification → surgery instability → the
cube measures the training/deployment path dependence. Rationale:

- GAMMA alone risks "known mathematics, new packaging" without the audit's empirical bite;
- ALPHA alone risks "Paper D in a new domain" without T1/T3's market-native fiber structure
  (kernel-randomness × granularity interaction, kernel-swap/truncation exposure).
- Combined compute stays Paper-D scale; both halves share the lab-asset-v3 instrument.

**Fallback**: if either family dies at D-2, the survivor proceeds alone (GAMMA as a
theory+signatures paper; ALPHA with only Paper D's rank-one-style proposition imported).
D-2 runs for both families regardless, since their hostile neighborhoods are disjoint.

## Sequencing

1. **D-2 session A (next)**: GAMMA hostile neighborhood (≥15 works, adjudication table,
   unresolved-collision list). Paper-only.
2. **D-2 session B**: ALPHA hostile neighborhood (≥15 works, MARL co-training lane searched
   hardest). Paper-only.
3. Merge gate: single-paper vs split decision recorded with D-2 evidence.
4. **D-1**: killer tests (≥2 per family), simulator-contract checks for both lineages, real
   bridge qualification (stylized-fact bridge), calibrated hostile-T0 forecasts to
   `forecast_ledger.yaml`.
5. **D0**: outcome-blind freeze; explicit PI authorization required before any GPU/execution.
6. Venue decision at D0 (ML methodology venue per Paper D precedent, or protocol-scope
   NMI/NCS), consistent with the evidence contract.
