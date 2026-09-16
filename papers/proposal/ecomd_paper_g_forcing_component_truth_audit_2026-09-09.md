# Paper G: forcing-component reference truth audit

PRIVATE / INTERNAL. Selected primary comparison and elementary development
control. Started 2026-09-09 11:06:36 UTC. `not_trigger`; no new candidate,
cycle or execution. The previous REACT turn was verified progress.

## Decision and exact comparison

The newly inspected paleoclimate study supplies a relevant evaluation protocol,
but it does not establish a contradiction with the existing response literature
or supply independent truth for its component-response diagnostic. Do not open
another history/response-method cycle on that basis.

[Subel and Zanna, arXiv2608.13494v1](https://arxiv.org/html/2608.13494v1),
13 August 2026, uses CESM2 ocean state and boundary fields, and compares
emulator responses between piControl and midHolocene conditions. Section2.5
specifies matched emulator initial conditions and climatological boundary
forcing; forcing-only baselines address information carried by the boundaries.
Section4.2 explicitly limits its additivity finding to the emulator because
single-forcing CESM2 reference experiments are unavailable. The study also
reports that ordinary prediction metrics do not reliably select response skill.
Thus its successful total-response comparisons do not constitute reference
labels for the unobserved component interventions. Its numerical climate
reference is not an independent real-ocean intervention.

[Falasca, arXiv2506.22552v8](https://arxiv.org/html/2506.22552v8), already in the
registry, studies different full/partial-state stochastic triad inference and
specified impulse or sustained forcing. The full-state experiments include
successful neural forced responses. Those conditional results are compatible
with the paleoclimate findings. No shared native state, legal intervention,
conditioning set, observation clock or target was found for opposite predictions.

[Womack et al., Earth System Dynamics17,107–139](https://esd.copernicus.org/articles/17/107/2026/),
published 16 January 2026, connects mean-response emulation to operator and
response methods. Selected sections2.3.2 and3–4 distinguish access to governing
equations and dedicated perturbation ensembles from fitting available scenarios.
Its MethodII and equation18 use perturbed/unperturbed ensemble responses.
Those capabilities must be counted when comparing cost and information access;
they cannot be assumed available from two archived climates. Generic response
functions, memory corrections or another factorial diagnostic remain direct
prior work, not an independent Paper G contribution.

## A conservative exact control for the missing-reference distinction

This is an elementary two-compartment tracer model, not an approximation fitted
to CESM2 or a claim about any trained model. Let x,y be nonnegative tracer
masses, x+y=1, and let u,v in [0,1] be two externally set controls on exchange
rates. Set gamma>0 and

\[
m_\lambda(u,v)=\tfrac12+\tfrac18u+\tfrac18v+\lambda u(1-v),
\qquad \lambda\in\{-\tfrac18,0,\tfrac18\}.
\]

The physical exchange equations are

\[
\dot x=\gamma m_\lambda y-\gamma(1-m_\lambda)x,
\qquad \dot y=-\dot x.
\]

For every permitted lambda, the four corner values of m lie in [1/2,3/4].
Because m is bilinear, it is a convex combination of these corners throughout
the unit square. Both transfer rates are nonnegative. At x=0 the derivative
of x is nonnegative, and at y=0 the derivative of y is nonnegative. Total mass
is exactly conserved; no unstable or invalid trajectory is needed.

Start from x=y=1/2. Under a constant control held for physical time t,

\[
R_\lambda(u,v;t)=x(t)-\tfrac12
=g(t)\left[\tfrac18u+\tfrac18v+\lambda u(1-v)\right],
\qquad g(t)=1-e^{-\gamma t}.
\]

For all three systems, the entire baseline path under (u,v)=(0,0) and the
entire joint-control path under (1,1) agree. This also holds for any control
tape switching only between those two endpoints. Nevertheless, the physical
four-corner contrast is

\[
I_\lambda(t)=R_\lambda(1,1;t)-R_\lambda(1,0;t)
-R_\lambda(0,1;t)+R_\lambda(0,0;t)=-g(t)\lambda.
\]

For t>0, lambda=+1/8 gives a negative interaction, lambda=-1/8 gives a
positive interaction, and lambda=0 gives an additive null. A model that
perfectly matches the baseline and joint-control paths can therefore have
zero interaction while either sign is compatible with those reference paths.
Conservation, positivity, stable relaxation and arbitrarily dense temporal
sampling of the two available treatments do not identify the missing contrast.
This is standard treatment-support nonidentification with a physical realization,
not a new impossibility theorem or evidence of an error in the cited study.

The cheapest resolving observation depends on structural assumptions. Inside
this stipulated family, one reference endpoint under (1,0) identifies lambda
when gamma and the fixed coefficients are known. A single intermediate joint
dose also suffices:

\[
R_\lambda(\tfrac12,\tfrac12;t)-\tfrac12R_\lambda(1,1;t)
=\tfrac14g(t)\lambda.
\]

This dose contrast cancels unknown additive coefficients if the same bilinear
functional form is retained. It is not a general substitute for component
experiments: an unrestricted response surface may agree at all three joint
doses and still differ at the single-control corners. No universal requirement
for all 2^k treatment combinations, or universal one-probe sufficiency, follows.

## Reusable contract and stopping rule

Keep three targets separate: a total response between two specified boundary
regimes, a component intervention holding other boundaries fixed, and a mixed
response contrast. Each needs reference support for that target or an explicit
structural identification theorem. Passing a scalar range check or matching a
total-response map does not itself supply that theorem.

A future reference source must name the physical state and observation mapping,
joint control law, baseline and component/dose assignments, initial-state law,
time horizon, clock and averaging rule. It must state whether boundary histories
are coupled realizations, prescribed time series or monthly climatologies.
The cost contract must count dedicated perturbation runs, reference precision,
ensemble dependence, training and evaluation separately. A scalar observed
reference error bound is not an uncertainty certificate for a missing treatment.

No source code, raw climate fields, checkpoints or outcomes were accessed.
Selected articles are development reading, not a held-out confirmation set.
The paper's archive declarations do not by themselves qualify immutable code,
data rights, required component labels, replay, independent truth or compute.
This bounded comparison stops at the explicit reference-scope limit; a repository
download cannot create the missing physical intervention truth.

The new control confirms the existing off-support reduction rather than defeating
it. Both recorded contribution blockers remain: generic sensitivity/history
remedies have direct prior work, and no new variance-cost result has been supplied.
Re-enter only on actual target-matched reference support plus a distinct
contribution, or a theorem/primary disagreement that removes a recorded blocker.
No re-labelling of the current diagnostic as climate additivity is authorized.

Structured record:
`research/paper_g/forcing_component_truth_audit_20260909.yaml`.
