# Multi-stationary drift tomography v11

**Date:** 2026-08-13

**Decision:** `V11_CONJECTURE_ONLY`

**Branch:** `multi-stationary-drift-tomography-audit-v11`

V11 studied recovery of a common non-gradient SDE drift from positive stationary densities under quantitatively
known additive drift perturbations and common known diffusion. Experiment 152 was frozen and run once from
`0ab9cba6594b1354447aa28e1f5e8cccce91b4a4`; all six exact fixtures matched, raw SHA-256
`ee08eb70ed8551c8b7ff8cd8e98d9e93cda1a50ce1d1419be2210f0718a5862a`, decision
`IDENTITY_AND_OBSTRUCTIONS_CONFIRMED`, and all admission/novelty/compute flags remained false.

Lasting equations:

- stationary FP subtraction gives `alpha_m(b)=q_m` with
  `alpha_m=d log(rho_m/rho_0)`; full pointwise covector rank recovers `b`;
- for two candidate common drifts, `j=rho_0(b_tilde-b)` is an exact ambiguity iff
  `div j=0` and `j dot grad(rho_m/rho_0)=0` for every environment, subject to admissibility;
- use the diffusion-metric frame operator, not raw chart singular values, for intrinsic pointwise conditioning;
- the score-difference matrix is `dR` for the density-ratio map. A closed `d`-manifold cannot immerse into `R^d`,
  so uniform pointwise inversion needs at least `d+1` nonbaseline densities; the minimal abstract count is the
  Euclidean immersion dimension.

Scope boundary: the topology statement is not a global identification lower bound. On `S^1`, one nonconstant
density ratio has mandatory critical points but eliminates every constant divergence-free current, so two total
environments can identify the common drift globally while pointwise inversion is singular.

Novelty audit: DyNoSeD already provides local score FP residuals, global Stein/KSD, affine rank identification and
sensitivity; KDS learns stationary diffusions across interventions; interventional-SDE identification counts and
ergodic-measure drift ambiguity are direct prior art. Jacobi multipliers and Nambu currents cover the geometric
ingredients. V11-C1 is `RETIRED_PRIOR_ART`; V11-C2 remains `CONJECTURE` pending a human novelty/value audit and a
stronger global/minimax consequence, feasible drift-blind design and non-equivalent estimator.

Experiment 153 is locked. No generated sample, real outcome, remote host or GPU was opened. Both V100 32 GB
workers and the RTX2060 remain uncontacted and unqueued.

Canonical documents:

- `papers/proposal/plan_multi_stationary_drift_tomography_nmi_ncs_v11.md`
- `research/theory_exploration/formal_cards_v11.md`
- `research/theory_exploration/multi_stationary_drift_tomography_audit_v11.md`
- `experiments/152_multi_stationary_drift_tomography/RESULTS.md`
