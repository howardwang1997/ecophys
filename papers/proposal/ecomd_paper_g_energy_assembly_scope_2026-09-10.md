# Paper G: boundary-response and energy-assembly scope

PRIVATE / INTERNAL. `public_evidence_eligible: false`.
Started 2026-09-09T17:45:25Z (2026-09-10 05:45 Pacific/Auckland).
Previous goal turn: progress. The overall Paper G goal remains unachieved.

**Decision: not a qualified re-entry trigger.** Generic field-value versus
assembled-curvature mismatch, convex learned elements and nullspace-aware
regularization already have direct parents. The selected primary works do not
supply an opposite prediction for a matched physical state and intervention.
The two paper-only controls below are classical variational identities, not
new theorems or observed model failures.

This continues the source-only NOEM/convex-element lead, attached to the
closed `paper_g_numerical_teacher_continuum_ranking` route. It removes neither
the elementary-certificate nor the direct-supervision-parent blocker. The
repository connection is the original neural-PDE constraint/generalization
question and the use of learned physical responses inside downstream solves.
No Paper D outcomes, implementation history or contribution are transferred.

## What is actually in the sources

[NOEM arXiv2506.18427v1](https://arxiv.org/html/2506.18427v1), Sections 3.2–3.3,
4.3.2 and Appendix C, already acknowledges nonconvex energy minimization and
reuses one pretrained model in many same-geometry elements. Its field response
is parameterized by boundary inputs and inserted into the physical energy;
automatic differentiation supplies assembled forces and tangents. Fixed
element geometry is different from a single element instance.

The [NOEM version of record](https://doi.org/10.1038/s43588-026-00974-2) was
also read in selected author-uploaded full-text passages on
[ResearchGate](https://www.researchgate.net/publication/404271016_NOEM_efficient_and_scalable_finite_element_method_enabled_by_reusable_neural_operators).
The page identifies Lu Lu's April 29, 2026 upload and reproduces the published
article. Its main text explicitly reports negative Hessian eigenvalues for
out-of-distribution inputs and associated convergence risk, referring to
Supplementary Section 4. The supplement itself was not read. The main error
theorem assumes the energy minimizer and includes a gap to an enlarged linear
trial space; it is not a guarantee that Newton reaches that minimizer.

[Convex Neural Energy Elements2608.02036v1](https://arxiv.org/html/2608.02036v1),
Sections 2–3, 4.7–4.8, selected 5–7 and Appendix A, already targets condensed
boundary energies, preserves positive semidefiniteness and treats the physics
nullspace. Its linear construction regresses a condensed-matrix square-root
target; a global polynomial baseline is competitive in the stated smooth,
low-dimensional geometry family. Thus the guarantee is not identified with
the neural regressor. Boundary-only and full-field costs are explicitly
separated, with exact interior lifting charged separately.

Its nonlinear study concerns a convex reaction–diffusion energy, not arbitrary
nonconvex mechanics. Exact condensation, a linear-response trial energy and
finite Newton-refinement energies have different guarantees; the text does
not prove global convexity for every finite-refinement energy. The source's
implementation-development footnote and failed development variants are
excluded from scientific support. No experimental failure magnitude, timing,
or generic superiority claim is adopted as a Paper G result. Source/data
release and independent replication remain unqualified.

Consequently, neither “NOEM did not know about negative curvature” nor
“NOEM cannot reuse multiple elements” is a valid motivation. Geometry family,
trial map, boundary representation, physical energy, training targets and
global coupling all need matching before an explanatory comparison.

## Control 1: accurate spatial fields do not control boundary curvature

Consider unit-coefficient scalar diffusion on `x in [0,1]`, with boundary
values `u(0)=0`, `u(1)=U`. The exact harmonic field and condensed energy are
`u(x;U)=xU` and `E_0(U)=U^2/2`. For `epsilon,omega>0`, define a boundary-exact trial family

\[
q(x;U)=xU+\epsilon\sin(\omega U)\sin(\pi x).
\]

For every `U`, its field error is at most `epsilon/sqrt(2)` in spatial `L2`,
and its spatial derivative error at most `pi epsilon/sqrt(2)`. Exact spatial
integration, with no quadrature approximation, gives

\[
E_q(U)=\frac12\int_0^1 q_x^2\,dx
=\frac12U^2+\frac{\pi^2\epsilon^2}{4}\sin^2(\omega U),
\]
\[
E_q''(U)=1+\frac{\pi^2\epsilon^2\omega^2}{2}\cos(2\omega U).
\]

The physical energy excess is uniformly bounded by `pi^2 epsilon^2/4`,
while the boundary Hessian can be negative and arbitrarily large in magnitude.
Here `omega` changes the trial map's input dependence; it is **not** a new
physical control parameter or physical instability.

For a prescribed boundary load `f=U_0>0`, the exact physical total energy
`E_0(U)-fU` has its unique minimum at `U_0`. Choose
`omega U_0=pi/2` modulo `pi`. Then `E_q'(U_0)=f`; if
`pi^2 epsilon^2 omega^2/2>1`, the trial total energy has negative curvature
at that stationary point. This diagnoses representational curvature relevant
to a Newton solve, not a failure of the diffusion PDE.

There is an essential null result. Any **global** minimizer `U_hat` of the
trial total energy still satisfies

\[
\frac12|\widehat U-f|^2
\leq \frac{\pi^2\epsilon^2}{4},
\qquad
|\widehat U-f|\leq\frac{\pi\epsilon}{\sqrt2}.
\]

Proof: compare the trial objective at `U_hat` and `f`, and use the nonnegative,
uniformly bounded energy excess. Hence negative local curvature alone does
not prove a large global-minimizer error. Solver convergence and approximation
accuracy are separate estimands. This exact calculus example is a standard
scope control, not a trained neural model, empirical prevalence claim or new
publication-level theorem.

## Control 2: boundary-linear field lifting is an indispensable null

For a fixed discretization of a self-adjoint quadratic physical energy with
`K` positive semidefinite, partition degrees of freedom into boundary `U` and
interior `v`, with `K_ii` positive definite. With zero volume forcing, set

\[
R_*=-K_{ii}^{-1}K_{ib},\qquad
S=K_{bb}-K_{bi}K_{ii}^{-1}K_{ib}.
\]

An arbitrary **linear** interior response `v=R U`, retaining the exact boundary
trace, induces the stiffness

\[
\widehat S=[I;R]^T K[I;R]
=S+(R-R_*)^TK_{ii}(R-R_*).
\]

The first expression is a Gram construction and the second follows by
completing the square. Thus `S_hat >= S` in the positive-semidefinite order;
the field model need not learn energy directly to retain convexity. If a
physical null mode is to be preserved, the lift must reproduce that mode.
With forcing, affine terms and the corresponding particular lift must also
be retained. Arbitrary inaccurate boundary enforcement or quadrature cannot
be silently included in this identity.

The general chain rule explains the distinction: for a free physical vector
`z=q(c)` and `J(z)=z^T K z/2-f^T z`,

\[
\nabla_c^2J(q(c))
=J_q^TKJ_q+\sum_i(Kq-f)_i\nabla_c^2q_i.
\]

The second term vanishes for affine `q`. Comparing an unrestricted nonlinear
boundary map against a convex energy architecture changes this structural
factor as well as the learning target. Geometry dependence of `R(g)` can be
nonlinear while `U -> R(g)U` remains linear for each geometry.

This is classical static condensation/Rayleigh–Ritz theory. It does not
establish a fast learned lifting algorithm, geometry generalization, equality
of target-generation costs, accuracy in nonquadratic physics or an independent
continuum reference. The classical null must be faced before a field-versus-
energy claim is escalated.

## What is stopped, and what remains useful

Stop generic Hessian-sign diagnosis, value/derivative mismatch, convex energy
export, nullspace regularization and square-root regression as topic generators.
The counterexample and affine-lifting identity are reusable evaluation controls;
they do not remove the recorded contribution blocker or authorize a new cycle.

The next bounded source lead is
[Parish et al.2307.05434](https://arxiv.org/abs/2307.05434), located through the
convex-element bibliography and official abstract. Its detailed formulation
and simplified well-posedness theorem have not yet been read. Before borrowing
its SPSD guarantee, identify whether the learned object is a secant map, a
consistent force derivative or a condensed energy Hessian, especially when it
depends on displacement. Those objects are not interchangeable. A classical
Jacobian/integrability distinction alone would again supply no new topic.

No primary disagreement, independent confirmation partition, qualified new
truth asset or full-cost advantage is established. Neither the sources nor
this document authorize scientific implementation, outcome access, experiments,
GPU work, outreach or publication. Formal contract, source manifest, graph,
re-entry ledger, memory and daily log record this as private infrastructure
work. The full ICML/NMI/NCS-oriented Paper G objective remains active.
