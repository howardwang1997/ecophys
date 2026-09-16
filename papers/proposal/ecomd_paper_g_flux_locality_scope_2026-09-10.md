# Paper G: flux locality and physical response scope audit

PRIVATE / INTERNAL. `public_evidence_eligible: false`.
Started 2026-09-09T17:06:20Z (2026-09-10 05:06 Pacific/Auckland).
Previous goal turn: progress. Paper G goal remains active and unachieved.

**Decision: not a qualified re-entry trigger.** Local conservation, a local
divergence stencil, and a local physical response are distinct properties.
The generic global-correction/locality trade-off is already explicit in the
primary work. Standard telescoping and diffusion controls resolve the
apparent contradiction without producing a new method or a matched empirical
mechanism disagreement.

This follows the source lead in the constraint-comparability audit. It attaches
to `paper_g_numerical_teacher_continuum_ranking`, still `failed_closed`, and
removes neither the elementary-certificate nor direct-supervision-parent
blocker. This is a source/theorem-scope preflight, not a new candidate cycle.

## What the primary sources actually support

[McGreivy and Hakim, arXiv2303.16110v2](https://arxiv.org/html/2303.16110v2)
is the full paper corresponding to the cited 2023 workshop contribution.
The introduction and Section 8 explicitly discuss global dependence, its
finite-propagation trade-off for hyperbolic equations, and limitations from
time stepping, boundary fluxes and inaccurate updates. Section 6.1 separates
flux-form preservation of linear invariants from stronger nonlinear-invariant
restrictions. The paper does not leave generic nonlocality undiscovered.
Its finite-speed statement concerns hyperbolic physics; do not apply it
indiscriminately to diffusion or incompressible pressure response. Selected
mathematical scope was read; reported numerical performance was not reproduced.

[Ye, Li and Yan, arXiv2504.09807v1](https://arxiv.org/html/2504.09807v1),
Sections 2.1–2.3 and 3, gives a local-operator definition with zero exterior
input derivative, then targets compressible viscous flow with thermal
conduction. Its boundary treatment extends the required input region. Training
initial velocities use a finite low-mode trigonometric family, with constant
initial density and temperature. These are different assumptions from an
arbitrary-function continuum response claim. Boundary imposition and domain
reuse already have a direct local-neural-operator parent.

Huang2506.05513v1 Appendix F is reused only as the source of the local-flux
lead. No published tables, source code, checkpoint, raw array, or boundary
optimization output was independently evaluated. Source equations define the
audit; source or implementation defects are not a scientific narrative here.

## Control 1: flux representation does not identify locality

On a periodic one-dimensional grid with spacing `h`, let a proposed update
rate `r_j(u)` satisfy `sum_j r_j(u)=0`. Choose `F_(1/2)=0` and define

\[
F_{j+1/2}(u)=-h\sum_{i=1}^{j}r_i(u).
\]

Then `F_(N+1/2)=F_(1/2)` and

\[
r_j(u)=-\frac{F_{j+1/2}(u)-F_{j-1/2}(u)}h.
\]

The flux can depend on the whole domain. Adding a common flux constant leaves
the update unchanged. Thus even a globally mean-corrected update can be
written in flux form and telescope on every subdomain. In graph notation,
`1^T D=0` establishes balance; response locality instead concerns the support
of `D J_F(u)`. Both require a boundary and cell-volume convention.

For example, `r_j(u)=u_j-mean(u)` has
`partial r_j/partial u_k=delta_jk-1/N`, including remote dependence, yet it
admits the flux representation above. This is only a standard algebraic
control, not a proposed accurate/stable physical model or a source result.
A meaningful local method must additionally restrict the *input dependence
of its flux*, including normalization, attention, pressure and solver steps.

## Control 2: a local generator need not have a local finite-time map

For scalar diffusion on the line,

\[
\partial_t w=\nu\partial_{yy}w,\qquad
w(0,t)=\int_{\mathbb R}K_t(y)w(y,0)\,dy,\qquad
K_t(y)=\frac{e^{-y^2/(4\nu t)}}{\sqrt{4\pi\nu t}},\quad\nu>0.
\]

The generator is local but `K_t` is positive everywhere for `t>0`. Given only
the initial field on `[-R,R]` and an exterior amplitude bound `A`, the omitted
contribution is at most

\[
A\,\operatorname{erfc}\!\left(\frac{R}{\sqrt{4\nu t}}\right).
\]

For the unrestricted exterior `L-infinity` class, the bound is the worst-case
absolute uncertainty radius. Additional momentum, energy or support constraints
change that class. This is the classical heat-kernel tail, not a new neural
error bound. It illustrates why useful approximate locality must specify
amplitude, tolerance, diffusion, horizon and boundary—not merely a radius.
Tiny nonzero tails do not demonstrate practical failure of a learned model.

There is also a direct **linearized** connection to the viscous equations read
above. Around a uniform resting positive-density/temperature state, take a
transverse perturbation `(delta v_x,delta v_y)=(w(y),0)` with zero density and
temperature perturbations. The linearized divergence, pressure and energy
perturbations vanish, and the shear obeys the heat equation with a positive
kinematic coefficient. With the stress tensor exactly as written in that
source's Eq. 7, the coefficient is `nu=2/(rho_0 Re)`. This uses the written
normalization and makes no claim about its implementation.

On a periodic domain use the periodic heat kernel. Two equal-integral smooth
bumps outside the observed patch, at different kernel weights, give a
zero-mean difference `psi` with `(K_t*psi)(0) != 0`. Initial states with
velocities `+epsilon psi` and `-epsilon psi`, common density and temperature,
have identical mass, zero total momentum and equal total energy, and coincide
on the observed patch. Their first-order future shear responses differ.
For sufficiently small smooth perturbations this is a local-in-time
linearization control; it is not a formula for arbitrary finite-amplitude
compressible dynamics or the nonlinear thermal response.

The bump directions are outside the cited low-mode training initialization
family. Consequently this is an admissible continuum-response control, not
evidence of an observed error on that paper's training/test distribution.
Incompressible pressure introduces a separate global elliptic dependence;
its absence or inclusion must be frozen, not assumed from the word “flow.”

## Control 3: the observation family can hide nonlocal dependence

A finite trigonometric polynomial is determined by its values on an open
interval. Two such functions agreeing there agree everywhere. Thus, on a
restricted finite-mode initialization family, local observations may encode
global coefficients even though the PDE response is nonlocal on the larger
function class. For finitely sampled observations, this requires full column
rank and adequate conditioning of the sampling matrix; neither is asserted
for the cited model. Later nonlinear states require a separate observability
analysis. This standard uniqueness fact is not a learned physical-locality
theorem or a claim that the paper's performance is explained by it.

These controls separate three estimands: derivative with respect to arbitrary
admissible remote fields, prediction under a restricted state distribution,
and sensitivity above a declared tolerance. They cannot be substituted for
one another to create an opposing primary prediction.

## Frozen scope and next action

The truth contract fixes the PDE and observable, allowed remote intervention,
state/observation family, global invariants, boundaries, grid and cell volumes,
flux receptive field, pressure/elliptic steps, time integration, normalization,
noise and tolerance. Neither independent confirmation nor full cost is
qualified. Public article reading does not grant data/source execution or
publication authority. No experiment, source execution or numerical/symbolic
calculation was performed.

Stop generic local-versus-global correction, flux-form rewrites, heat-tail
certificates and locality labels as candidate generators. A next useful update
must add a nonstandard source-specific information/control residual, not
another instance of these identities. No raw question, cycle, full fifteen-work
audit, forecast, card or qualified trigger is created.

One abstract-only routing lead remains:
[NEST, arXiv2605.12343v1](https://arxiv.org/abs/2605.12343v1), which couples
local learned solid-mechanics solvers through global Schwarz iteration. It
cannot be cited as evidence that the full physical response is local. If
followed, audit the actual interface variables, coupling/convergence and
reference-truth contract before considering any new question. It predates
this closure and is not a new-publication trigger. Classical domain
decomposition alone would not remove a contribution blocker.

All evidence and reasoning are private/internal. The graph, trigger ledger,
formal contract, source manifest, memory and daily log record the failed
trigger and reusable controls; their consistency tests do not prove novelty,
practical effect size or suitability for ICML/NMI/NCS.
