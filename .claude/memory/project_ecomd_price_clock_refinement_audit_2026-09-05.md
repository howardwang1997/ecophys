---
name: EcoMD price-clock refinement audit
description: Fixed-parameter per-integrator-step price refinement is non-tight, but EcoMD already exposes a lawful fixed-clearing-bucket refinement; the issue is QA and unit semantics, not an ICLR method.
type: project
---

# EcoMD price-clock refinement audit — 2026-09-05

- `not_trigger`; no simulator, outcome, source edit, SSH or GPU work was authorized.
- In the zero-force Gaussian subsystem, aggregate displacement over an agent step `h` is
  `a*sqrt(h)*Z`. If every shrinking agent step is also a price step, fixed `sigma_price` makes the
  fixed-horizon price variance grow as `1/h` and its `-sigma_price^2/2` drift diverge.
- With price noise off, the implemented concave map
  `sign(x)*s*(abs(x)/s+1e-8)^delta` is discontinuous at zero and also gives `1/h` variance growth in
  the ultimate offset-dominated regime. Removing the offset leaves variance proportional to
  `h^(delta-1)`, which diverges for `delta<1`.
- Rescaling the concave coefficient by `h^((1-delta)/2)` restores finite variance but yields an
  ordinary Gaussian aggregation limit in the iid witness; it does not preserve a heavy-tail
  continuum mechanism.
- Exact memoryless aggregation consistency implies `psi(x+y)=psi(x)+psi(y)` and hence linearity.
  Nonlinear cross-scale impact requires a fixed aggregation horizon or a stateful/history model.
- EcoMD already has the appropriate clock separation: keep `Delta=dt*inner_steps_per_price` fixed,
  refine the latent `dt`, increase `inner_steps_per_price`, and call the price head once per fixed
  bucket. Therefore the missing object is a convergence/unit contract, not a new architecture.
- Realized power variation, Neural SDE/RDE and function-space process models, learned-integrator
  analysis, semigroup-consistency diagnostics, and stateful nonlinear market-impact theories occupy
  the obvious general claims.
- Re-entry requires a genuinely new stateful resolution-equivariant operator/theorem beyond those
  parents, a frozen market-native multi-clock prediction, two independent truth systems, untouched
  market confirmation, and a new machine decision.

Formal result: `papers/proposal/ecomd_price_clock_refinement_reentry_audit_2026-09-05.md`.
