---
name: Gauge-invariant controller probes v7
description: Theorem-first search for observable or partially identified controller-probe targets after V6 closure.
type: project
---

# Gauge-invariant controller probes v7

Started branch `gauge-invariant-controller-probes-v7` from clean integrated
`main@d89a2dc59fa4e8ad0c0b7755a39b37ba3fe389a8` on 2026-08-13. Frozen plan:
`papers/proposal/plan_gauge_invariant_controller_probes_nmi_ncs_v7.md`.

V7 does not reopen V6. It treats V6's exact one-regime response/latent alias and cross-regime invariance failure as
the starting obstruction. It asks whether an admissible target can be constant on the observational gauge class,
remain informative under bounded latent drift and be refined by safe prospective controller probes.

Three initial `SCOUT` candidates were frozen:

1. an observable quotient response;
2. a sharp identified set under a latent-drift budget;
3. a paired randomized controller-loop/curvature probe.

Mandatory kill baselines are transfer functions/minimal realizations, predictive-state/process-state objects,
interventional and switching-system identification, safe active/optimal input design, robust set-membership
identification, partial-identification sensitivity analysis, switchback/crossover experiments and stochastic
pumps. Search failure is not novelty evidence. No experiment may be created until a candidate passes non-
equivalence, equivalence-class validity and executable-probe gates.

## Closure

Closed `V7_NO_SURVIVOR` on 2026-08-13 before any experiment or outcome access.

- C1 `RETIRED_PRIOR_ART`: a functional constant on equality classes of the complete controlled input--output law
  factors uniquely through that law. Transfer/Markov/Hankel/minimal-realization and PSR objects occupy the target.
- C2 `RETIRED_PRIOR_ART`: `b=S delta+e`, `||e||<=rho` yields a standard set-membership ellipsoid. Its full-rank
  diameter is `2 sqrt(rho^2-||r||^2)/sigma_min(S)` and it is unbounded along `ker(S)` absent external constraints.
  Safe probe selection is standard active/optimal excitation.
- C3 `RETIRED_IDENTIFIABILITY`: a fixed time-homogeneous history-state transducer reproduces the full law on any
  finite randomized safe probe tree. Switchbacks identify path assignment effects, not adaptation versus fixed
  hidden memory.

Primary PDFs for set membership, active dual MPC and switchbacks were rendered and visually checked at the formal
definitions. Canonical audit:
`research/theory_exploration/gauge_invariant_probe_audit_v7.md`. The append-only graph has 264 nodes.

No experiment directory, generated trajectory, market outcome, paid data, remote host, V100, RTX2060, GPU job or
H20 assumption was used. Re-entry requires an external state measurement, verified physical reset/erasure with a
manipulation check, or a different directly observable scientific target.
