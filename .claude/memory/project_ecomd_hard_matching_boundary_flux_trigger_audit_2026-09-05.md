---
name: EcoMD hard-matching boundary-flux trigger audit
description: Exact expected gradients through hard matching have a valid boundary-flux decomposition, but direct discontinuous-program, conditional-Monte-Carlo and stochastic-AD parents occupy the method and current EcoMD lacks the required matching semantics.
type: project
---

# EcoMD hard-matching boundary-flux trigger audit

- For a piecewise-smooth hard matching program, the derivative of the expected loss is the sum of
  within-cell pathwise derivatives and interface integrals of `density * loss jump * boundary
  normal velocity`. Almost-everywhere pathwise AD misses the latter.
- One monotone threshold can be conditioned exactly: the boundary contribution is
  `f(tau|Z) * (continuation_left - continuation_right) * d_tau/d_theta`. Forcing the pivot noise to
  the critical value and evaluating both continuations is conditional Monte Carlo/manifold
  sampling, not a new market estimator.
- Lee--Yu--Yang (NeurIPS 2018) already give unbiased interior-plus-surface gradients and reduce an
  affine `L`-branch partition from exponentially many cells to `L` boundary integrals. Parmas--
  Sugiyama place the same correction in a general probability-flow theory; Feng--Liu cover
  change-of-variables conditional Monte Carlo for discontinuous sensitivities.
- Potto (OOPSLA 2024) provides compositional differentiation, separate compilation and Monte Carlo
  sampling of parametric discontinuities; it supports finite loops by unrolling and declared
  nonlinear boundaries by diffeomorphic conditions. StochasticAD/ADEV occupy probabilistic-branch
  and alternative-continuation corrections. ICLR 2026 EventFBP occupies the obvious event-binning
  weak-derivative application.
- A real automation gap remains for data-dependent loops, mutable queues and automatically inverted
  continuous comparisons, but implementation or market specialization alone is not an ICLR
  primitive. No strict variance--work theorem over the parents was derived.
- Current EcoMD is fixed-step aggregate latent dynamics, not an individual-order price-time-priority
  engine. Its L2 adapters do not supply persistent ownership or a legal hard-matching action
  contract, so the candidate would first change the scientific object.
- Decision: `not_trigger`, zero blockers removed, no candidate harvesting, implementation,
  simulation, outcomes, SSH or GPU. Re-entry needs an exact reverse-mode estimator with a proved
  structural variance--work separation and lower bound, two independent gradient-truth systems and
  a preserved market-native action/response contract.
