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

Three initial `SCOUT` candidates are frozen:

1. an observable quotient response;
2. a sharp identified set under a latent-drift budget;
3. a paired randomized controller-loop/curvature probe.

Mandatory kill baselines are transfer functions/minimal realizations, predictive-state/process-state objects,
interventional and switching-system identification, safe active/optimal input design, robust set-membership
identification, partial-identification sensitivity analysis, switchback/crossover experiments and stochastic
pumps. Search failure is not novelty evidence. No experiment may be created until a candidate passes non-
equivalence, equivalence-class validity and executable-probe gates.

Current authorization is primary literature, symbolic algebra and tiny hand fixtures on at most 20 local Mac CPU
core-hours. No market outcome, paid data, remote host, V100, RTX2060, GPU job or H20 assumption is authorized.
