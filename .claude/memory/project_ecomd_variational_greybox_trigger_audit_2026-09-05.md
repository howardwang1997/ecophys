---
name: EcoMD variational grey-box trigger audit
description: VGB-DM has an exact additive parameter/residual gauge; GPL-FMR is genuinely post-closure but assumes a fully parametric ODE and occupies the obvious local-to-global repair. No qualified trigger or GPU work.
type: project
---

# EcoMD variational grey-box and flow-map trigger audit

- AISTATS 2026 VGB-DM fits the sum of a parameterized physical field and a flexible learned field
  from consecutive points of full trajectories. Its arXiv submission, repository creation, and
  final fixed code all predate the August EcoMD closures; September PMLR compilation is indexing,
  not a capability change.
- Exact gauge: replacing `theta` by any `theta'` and adding
  `f_phys(x;theta)-f_phys(x;theta')` to the residual preserves the complete vector field and every
  trajectory. KL, residual norms, schedules, stable window codes, and synthetic parameter RMSE can
  select or evaluate a convention but do not identify its physical semantics from observations.
- VGB-DM's coupling proposition is conditional on an encoder attaining a zero total objective and
  identifies only the total-flow coupling, not the physical/residual decomposition.
- Its unconditional `Var(grad L_DM) < Var(grad L_sim)` statement is false. In the scalar constant-
  velocity/noisy-endpoint example, the variances are `2 sigma^2 / Delta^2` and
  `2 sigma^2 Delta^2`; moreover the two losses differ by the arbitrary factor `Delta^2`.
- APHYNITY already states the additive nonuniqueness and supplies a minimum-residual metric-
  projection convention; Takeishi--Kalousis analyze grey-box regularizers; Ye et al. analyze hybrid-
  DGM nonidentifiability and a meta-learning remedy; Loman--Browning--Baker prove the exact gauge;
  FNODE and integral trajectory methods occupy noisy derivative/global consistency repairs.
- GPL-FMR and its MIT code are a real post-closure release dated 2026-08-23. It combines GP
  derivative matching with multi-shooting flow-map MAP, but assumes a known parametric ODE with no
  neural residual, proves no structural identification result, and supplies no market bridge. It
  occupies rather than opens the obvious local-to-global extension.
- EcoMD/public market data do not provide iid full trajectories, complete state, assigned parameter
  changes, component truth, or untouched same-estimand replication. Synthetic EcoMD recovery would
  be generator self-validation.
- Machine decision: `not_trigger`, zero blockers removed, no candidate harvest, topic card,
  experiment, implementation, outcome access, SSH, or GPU. Re-entry requires a finite-noise,
  partial-observation quotient-identification theorem and estimator beyond the named parents, two
  non-EcoMD systems with component truth, and a matching legal market truth asset.

