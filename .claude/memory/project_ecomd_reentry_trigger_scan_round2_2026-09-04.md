# EcoMD re-entry trigger scan round 2 (2026-09-04)

## Canonical decision

The incremental EcoMD scan found no qualified re-entry trigger. Cycle 17 remains closed and no implementation,
outcome access, simulator run, machine card, SSH session, or GPU work is authorized. The formal record is
`papers/proposal/ecomd_reentry_trigger_scan_round2_2026-09-04.md`.

## Durable findings

- PST (arXiv:2608.25631, 2026-08-26) is the strongest new neighbor. It gives exact one-step
  conditional-mean sensitivity for exact-forward CTMC trajectories and an explicit multistep
  finite-difference-to-directional-derivative discrepancy. It does not give a globally reliable trajectory
  gradient; discrepancies may accumulate or change sign.
- Exact-forward Gumbel straight-through, PST, score-function, alternative-path, coupled/unbiased CTMC
  sensitivity, differentiable queueing simulation, DiffMJX, and mixed-order simulator gradients crowd the
  obvious correction space. The obvious residual or branching correction reduces to existing estimator
  families.
- A forward-equivalence killer is now explicit. For `Y ~ Bernoulli(p)`, the discrete loss `Q(0)=0, Q(1)=1`
  has true gradient 1, while the forward-equivalent extensions
  `Q_c(x)=x+c*x*(1-x)*(1-2*x)` give identity-ST gradient `1+c` at both reachable states and can reverse sign.
  Therefore a surrogate sign is not an intrinsic property of the exact discrete forward model unless the
  off-state extension is frozen. AISTATS 2026 generalized/optimal STEs, established coarse-gradient alignment
  results, and a 2026 single-query unbiased combinatorial-gradient preprint occupy the generic repair space;
  this is a kill theorem, not a candidate contribution.
- EcoMD's scientific core is a fixed-step Langevin/neural-force transition. Its discrete order streams are
  mainly observation adapters. Converting EcoMD to a Gillespie CTMC to use PST changes the object and is not a
  native extension.
- DoTime 0.1.3 is one licensed, pinned exact-counterfactual truth system (Apache-2.0 code, CC-BY-4.0 suites).
  The independent epidemic ABM benchmark is conceptually useful but its repository had no explicit licence at
  commit `824ca2a9785038eaec4e277903856d796ac4adb3`; two contract-ready systems remain absent.
- UAI 2026 sign identifiability assumes a known linear stationary SDE graph. Partially observed linear and
  near-linear SDE structural identifiability already has direct 2025 prior art; neither removes EcoMD's latent,
  nonlinear observation-quotient blocker.
- Lean Marketron (arXiv:2608.20589) directly occupies gauge-reduced financial generalized-Langevin calibration.
  KNNR is a mandatory interactive LOB baseline but not assigned field truth. Harper's controlled private-
  information market has request-only raw data and published outcomes.

## Re-entry condition

Require a representation-invariant non-vacuous global sign certificate at event-support changes, an irreducible
new estimator with a bias--variance--cost theorem, or a second licensed pinned hard-event truth system with
common semantics. Pure algebra/source work may continue outcome-blind; implementation and compute may not.
