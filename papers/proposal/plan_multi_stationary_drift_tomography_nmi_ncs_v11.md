# Plan v11 — Multi-stationary drift tomography under known mechanism perturbations

**Frozen:** 2026-08-13

**Branch:** `multi-stationary-drift-tomography-audit-v11`

**Base:** `main@0ad0d59c27a811cb243b72e0707c5ecbc3be18f1`

**Initial state:** `EQUATION_AUDIT`; no generated sample, real-system outcome, market file, remote host or GPU is
authorized before the novelty and identifiability gates below

## 1. Scientific question and scope

V11 asks whether multiple equilibrium snapshots produced by *quantitatively known* mechanism perturbations can
recover an otherwise unknown stochastic drift without observing trajectories. The intended object is a controlled
diffusion, not a market-specific statistic:

\[
  dX_t = \{b(X_t)+u_m(X_t)\}\,dt+\sqrt{2\kappa}\,dW_t,
  \qquad m=0,\ldots,M,
\]

where `b` is a common unknown drift, `u_m` is a known additive drift field, `kappa>0` is known and common, and
environment `m` has a positive stationary density `rho_m`. The first audit is deliberately restricted to constant
isotropic diffusion in a fixed physical coordinate chart. Unknown or intervention-dependent diffusion, latent
state, transient endpoint distributions and unknown intervention strength are out of scope until the restricted
problem survives.

The broad statement “stationary distributions under interventions identify SDE dynamics” is already occupied.
V11 can survive only through a narrower full-noise, nonparametric and statistically usable result that is not a
direct subtraction of stationary Fokker--Planck equations or a repackaged generator/Stein moment estimator.

## 2. Frozen population identity

Assume initially that each `rho_m` is strictly positive and `C^2`, `b` and `u_m` are `C^1`, the diffusion is
uniquely ergodic, and boundary decay or no-flux conditions justify the stationary Fokker--Planck equation. Define

\[
 s_m=\nabla\log\rho_m,
 \qquad
 g_m=\kappa\{\Delta\log\rho_m+\lVert s_m\rVert^2\}
       -\nabla\!\cdot u_m-u_m^\top s_m.
\]

Dividing the stationary equation by `rho_m` gives

\[
 \nabla\!\cdot b+b^\top s_m=g_m.
\]

Subtracting environment zero eliminates the unknown divergence:

\[
  b(x)^\top\{s_m(x)-s_0(x)\}=g_m(x)-g_0(x).
\]

Let `S(x)` have rows `(s_m-s_0)^T` and let `q_m=g_m-g_0`. If `rank S(x)=d`, then formally

\[
  b(x)=S(x)^\dagger q(x).
\]

This formula is an audit target, not a claimed theorem. The rank condition needs at least `d+1` total environments
pointwise, and estimation requires first and second density derivatives. Both facts may make the construction
mathematically elementary and statistically unusable.

## 3. Candidate claims and non-claims

### V11-I0 — algebraic identity

The equation above recovers a full non-gradient drift at points where the score-difference covectors span the
cotangent space. This is expected to be a direct corollary of stationary Fokker--Planck and linear algebra. It may
be retained as a lemma or diagnostic, but cannot headline an NMI or NCS paper by itself.

### V11-NMI-1 — conditional method survivor

A viable NMI claim would require all of the following:

1. a weak or otherwise regularized estimator that avoids direct stationary-density Hessian estimation;
2. an identifiable nonparametric or explicitly controlled approximation class under weaker or structurally
   different assumptions than existing interventional-SDE results;
3. a finite-sample stability, minimax or experiment-design result governed by a measurable excitation quantity;
4. an equation-level non-equivalence witness against generator moment matching, kernel deviation from
   stationarity, score matching, inverse Fokker--Planck methods and ordinary linear inverse problems;
5. validation in at least two structurally distinct non-financial stochastic systems.

If the weak formulation is only

\[
  \mathbb E_{\rho_m}[b\!\cdot\!\nabla f]
  =-\mathbb E_{\rho_m}[u_m\!\cdot\!\nabla f+\kappa\Delta f],
\]

followed by basis expansion and least squares, V11-NMI-1 is retired as a generator/Stein/GMM composition.

### V11-NCS-1 — conditional scientific route

NCS additionally requires an independently measured scientific finding: calibrated perturbations must expose a
previously unresolved component of real nonequilibrium dynamics and predict a new intervention without refitting
the common drift. A generated SDE, EcoMD fit, cryptocurrency regime change or CRISPR target label alone does not
satisfy this requirement. In particular, an intervention label is not a known additive drift field, and an
endpoint sample is not a stationary sample without an independently validated relaxation protocol.

## 4. Closest-result audit fixed before computation

| Source | Direct coverage | Consequence for V11 |
|---|---|---|
| [Zweig et al., *Towards Identifiability of Interventional Stochastic Differential Equations*](https://arxiv.org/abs/2505.15987) | Stationary samples under known shift interventions; tight linear identifiability counts and nonlinear small-noise recovery bounds. | Closes the broad interventional-stationary-SDE identifiability claim. V11 must differ at theorem and estimator level. |
| [Lorch et al., *Causal Modeling with Stationary Diffusions*](https://proceedings.mlr.press/v238/lorch24a.html) | Learns nonlinear SDEs across interventions using an RKHS stationarity condition and kernel deviation from stationarity. | A weak generator loss or cross-environment stationarity objective is not new. |
| [Liu and Liu, *Inversions of stochastic processes from their ergodic measures*](https://doi.org/10.1515/jiip-2025-0098) | Characterizes drift/diffusion inversion from invariant measures; proves high-dimensional drift non-identifiability without gradient structure and constructs diffusion counterexamples. | Single-environment ambiguity and its divergence-free component are baselines, not V11 discoveries. |
| [Nie et al., *Solving the inverse Frobenius--Perron problem using stationary densities with input perturbations*](https://doi.org/10.1016/j.cnsns.2020.105302) | Recovers a one-dimensional discrete map from stationary densities under linearly independent input distributions. | Input-diversity rank as an inverse-dynamics principle is occupied outside SDEs. |
| [Chen et al., *Learning unknown dynamics via inverse Fokker--Planck*](https://arxiv.org/abs/2008.10653) | Uses physics-informed inverse Fokker--Planck learning to infer drift and diffusion from distributional snapshots. | Numerical PDE inversion is a mandatory baseline and cannot be renamed tomography. |

The audit must search both the references and forward citations of these sources. Search-result novelty, missing
keywords or an application gap cannot issue a pass.

## 5. Proof obligations and kill tests

### N0 — novelty non-equivalence

- Place the frozen strong identity beside the stationary Fokker--Planck equation line by line.
- Derive the weak form and identify whether it is exactly KDS, Stein matching or a standard Galerkin/GMM system.
- Compare assumptions, intervention counts and recovered objects with the 2026 interventional-SDE results.
- **Kill:** retire V11 if the only residual is an elementary pointwise rearrangement plus standard regularization.

### I0 — population identification

- Prove sufficiency of `rank S=d` and construct explicit rank-deficient alternatives.
- Distinguish diversity of intervention fields from diversity of induced stationary scores.
- Test common-drift, common-diffusion and true-stationarity assumptions by exact counterexamples.
- Determine whether score-difference rank is invariant under smooth coordinate changes, while stating correctly how
  Itô drifts and interventions transform.
- **Kill:** retire any coordinate-free claim if only chart-dependent quantities survive, and retire joint
  drift/diffusion recovery if exact aliases remain.

### S0 — statistical stability

- Quantify amplification through `sigma_min(S(x))` and through derivative estimation of `rho_m`.
- Compare the strong estimator with localized weak/Galerkin estimators under the same sample budget.
- Establish a nontrivial rate or lower bound rather than reporting low error on an Ornstein--Uhlenbeck fixture.
- **Kill:** retire the method route if eliminating density Hessians merely trades them for an ordinary ill-posed
  basis inversion with no new guarantee.

### R0 — scientific observability

- Require a versioned, quantitative intervention operator, not only a treatment label.
- Require independent evidence that every sampled environment is stationary in the declared state.
- Freeze an unseen perturbation and a separate system/domain before inspecting its outcome.
- **Kill:** do not infer real dynamics from EcoMD or a market regime whose effective drift perturbation is unknown.

## 6. Authorized feasibility work

### Experiment 152 — exact algebra and obstruction suite

This experiment may be preregistered only after the plan commit. It is limited to symbolic or deterministic
calculations on exact densities:

- one-dimensional gradient diffusion as a sign/convention check;
- two-dimensional Ornstein--Uhlenbeck systems with spanning and rank-deficient shift interventions;
- a nonreversible rotational drift to test whether multiple stationary scores remove the single-density gauge;
- a common-diffusion violation and an intervention that leaves the stationary density unchanged;
- smooth coordinate transforms to test covector-rank and Itô-transformation claims.

No random sample, optimizer, fitted neural score or favorable-condition sweep is allowed in Experiment 152. Passing
it establishes algebra and counterexamples only, never novelty.

### Experiment 153 — conditional finite-sample conditioning study

Experiment 153 remains locked until N0 and I0 survive a documented human novelty audit. If unlocked, it must use a
single preregistered generated benchmark matrix covering dimension, sample size, perturbation geometry,
nonreversibility and density-estimator misspecification. It must compare direct derivative inversion, weak
Galerkin/KDS, trajectory-based drift estimation as an information-rich oracle and a single-environment
non-identifiability control. No real-system or market target is opened at this tier.

## 7. Data requirements

| Tier | Required data | Admission condition |
|---|---|---|
| T0 current | Primary-source text and hand-specified exact densities/vector fields only. | Frozen plan and no outcome computation. |
| T1 generated | Immutable SDE configs, exact intervention fields, stationary samplers, independent seeds and analytic truth where available. | N0/I0 survive and Experiment 153 is separately preregistered. |
| T2 NMI | At least two non-financial controlled stochastic systems with quantitatively calibrated perturbation fields, repeated stationary ensembles, untouched interventions and full provenance/licence records. | Stable estimator and theorem survive generated falsification. |
| T3 NCS | A real system in which the recovered non-gradient or cross-coordinate dynamics answers a scientific question, plus independent system/domain replication and a frozen intervention prediction. | Method is already publishable without the application; stationarity and intervention semantics are independently validated. |

Candidate domains include calibrated colloidal/optical-trap experiments, controlled chemical or ecological
microcosms and perturbational cell systems only when the applied operator can be quantitatively mapped. Public
single-cell intervention datasets may be useful later, but ordinary endpoint Perturb-seq does not by itself certify
an additive drift or a stationary law. Current market data and EcoMD are not evidence for T2/T3.

## 8. Compute requirements

| Tier | CPU | GPU | Current worker policy |
|---|---:|---:|---|
| T0 plan, proof and Experiment 152 | <=20 core-hours | 0 | Mac `ecophys` Conda environment only; do not contact workers. |
| T1 Experiment 153 | <=500 core-hours | <=20 V100-equivalent hours if neural score baselines are indispensable | Two V100 32 GB workers as independent jobs; RTX2060 for smoke or CPU work only. |
| T2 NMI validation | 2,000--20,000 core-hours | 200--2,000 V100-equivalent hours | Scale to additional heterogeneous non-H20 pools after canonical V100 benchmarks. |
| T3 NCS confirmation | 10,000--100,000 core-hours | 2,000--20,000 V100-equivalent hours, revised from measured scaling | Capacity and storage may expand; no design or budget may assume H20 access. |

GPU capacity cannot repair lack of intervention semantics, stationary support, excitation or theorem novelty.

## 9. Venue-specific decision rule

- **NMI:** requires a general, stable and non-equivalent inference method with theorem-level guarantees and
  cross-domain validation. The pointwise identity alone is below the venue threshold.
- **NCS:** requires the same credible computational method plus a substantive, prospectively validated finding in
  a real scientific system. A simulator diagnostic or finance-only example is insufficient.
- **Specialist fallback:** is considered only after the NMI/NCS audit closes and is never used to relax the frozen
  claim while inspecting outcomes.

At freeze, the honest probability of a flagship survivor is low because the broad theorem is direct 2026 prior
art and the strong identity is an elementary Fokker--Planck subtraction. That is a reason to run the cheap kill
tests first, not to generate more data.

## 10. Chronology and record keeping

1. Commit and push this plan before an Experiment 152 preregistration, result or closure statement.
2. Complete N0 and exact proof/counterexample work before any random sample or remote job.
3. Append sources, candidates, proof obligations, counterexamples and decisions to the typed knowledge graph;
   never delete the V1--V10 failures.
4. Synchronize `source_matrix.md`, `candidate_ledger.md`, `failure_ledger.md`, `venue_routes.md`,
   `docs/research_lineage.md`, `.claude/memory/` and the dated work log when a decision becomes lasting.
5. Close as `V11_NO_SURVIVOR_PRIOR_ART`, `V11_NO_SURVIVOR_ILL_POSED`, `V11_CONJECTURE_ONLY` or
   `V11_READY_FOR_HUMAN_AUDIT`. Automation may not issue a novelty pass.

## 11. Completed outcome — 2026-08-13

**Decision:** `V11_CONJECTURE_ONLY`.

Experiment 152 returned `IDENTITY_AND_OBSTRUCTIONS_CONFIRMED` from the sole frozen run, with raw SHA-256
`ee08eb70ed8551c8b7ff8cd8e98d9e93cda1a50ce1d1419be2210f0718a5862a`. It verified exact full-rank
nonreversible recovery and exact rank, intervention-invisibility, unequal-diffusion and coordinate-change
obstructions. It did not issue a novelty, candidate-admission or compute-unlock pass.

The post-result equation audit adds DyNoSeD as a decisive nearest method: it already combines local score-based
Fokker--Planck residuals, global Stein/KSD fitting, affine-parameter rank identification and sensitivity analysis.
The weak/Galerkin/regularized estimator route and the multi-density ambiguity-current headline are therefore
`RETIRED_PRIOR_ART`.

A narrower statement survives only as a research conjecture: score differences are the differential of the
density-ratio map. On a closed `d`-manifold, `d` nonbaseline density ratios cannot form a global exact coframe, so
uniformly conditioned pointwise recovery requires at least `d+1` nonbaseline densities (`d+2` total
environments); the minimal abstract density-family count equals the Euclidean immersion dimension. The proof and
limitations are in `research/theory_exploration/formal_cards_v11.md`. This does not imply global
non-identifiability—the exact circle witness is globally unique with unavoidable rank defects—does not construct
feasible drift-blind interventions and has not passed a human
novelty/value audit.

Experiment 153, real outcomes and all remote/GPU work remain locked. Detailed closure:
`research/theory_exploration/multi_stationary_drift_tomography_audit_v11.md`.
