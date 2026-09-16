# Paper G: SPSD coefficient, consistent tangent and nonlinear equilibrium

PRIVATE / INTERNAL. `public_evidence_eligible: false`.
Started 2026-09-09T18:00:03Z; resumed after user continuation on 2026-09-10.
Previous completed goal turn: progress. The overall objective is unachieved.

**Decision: not a qualified re-entry trigger.** Pointwise SPSD coefficients,
monotone force maps, conservative forces, nonlinear uniqueness and solver
convergence require different hypotheses. The exact controls below clarify
these hypotheses by elementary calculus. They are not new theorems, evidence
of trained-model failure, or a publication-ready contribution.

This bounded source audit follows the Parish lead from the energy-assembly
audit. It is attached to the closed numerical-teacher route and removes
neither recorded blocker: elementary certificates and direct prior parents.
Its repository connection is neural-PDE constraints and learned responses
inside physical solves. No Paper D outcome or implementation history is used.

## Source scope and version boundary

[Parish et al., arXiv2307.05434v3](https://arxiv.org/html/2307.05434v3), dated
October 23, 2023, uses a common reduced basis and a state-dependent factor
`L L^T` to map displacement to force, with a preload offset (Section 4.3).
Remarks 4.1–4.2 distinguish this boundary map from constitutive learning and
limit it to static, path-independent problems. Section 5 treats 1D linear
elasticity; equations 18–19 distinguish constant and learned coefficients.
Section 6.1 specifies nonlinear conjugate gradients with a tangent
preconditioner, using different stiffness constructions for the two model
forms. Section 7 explicitly leaves solver interaction versus ill-posedness
unresolved. These are source statements, not independently reproduced results.

The [publisher record](https://link.springer.com/article/10.1007/s00466-024-02481-5)
confirms Computational Mechanics 74, 1357–1381, published May 6, 2024. Only its
preview, notes and metadata were available; the final Section 5 was not read.
Accordingly, the detailed audit is version-specific to arXiv v3 and does not
assert that the journal text is unchanged.

[Xu, Huang and Darve](https://arxiv.org/abs/2004.00265), v1 April 1, 2020,
is a cited constitutive-learning lead. Only its abstract and version history
were read. No exact tangent guarantee is imported from it.

## Control 1: an SPD frozen matrix can admit several nonlinear equilibria

Let `F(u)=K(u)u+f0` with a differentiable symmetric PSD coefficient. Its
consistent directional derivative is

\[
DF(u)[v]=K(u)v+DK(u)[v]u.
\]

The sign of `K` controls `u^T(F(u)-f0)`, but says nothing by itself about the
second term, force monotonicity or the symmetry of `DF`. If `K` is constant,
the second term vanishes: this is the essential valid linear null.

For an exact scalar control, set `l(u)=max(2-u,0)` and consider the residual

\[
G(u)-b=\{1+l(u)^2\}u-b.
\]

Its frozen coefficient is at least one for every real `u`. On `0<u<2`,

\[
G(u)=u^3-4u^2+5u,\qquad G'(u)=3u^2-8u+5.
\]

Choose `b=15/8`. Factorization gives

\[
G(u)-\frac{15}{8}
=\left(u-\frac32\right)
 \left(u^2-\frac52u+\frac54\right).
\]

Thus three distinct solutions are

\[
u\in\left\{\frac{5-\sqrt5}{4},\frac32,
\frac{5+\sqrt5}{4}\right\}\subset(0,2).
\]

At `u=3/2`, `G'=-1/4`. Every frozen linear system is invertible, yet the
nonlinear equation is not uniquely solvable. All three roots lie in a smooth
piece of the ReLU factor, so a kink is not responsible. This is an admissible
factor-form control, not a fitted network, training optimum, or physical
material law. No empirical prevalence follows from its existence.

The control also embeds into the displayed four-degree outer system of the
v3 Section 5, rather than relying only on a scalar analogy. In its normalized
units use

\[
A=\begin{bmatrix}2&-1&0&0\\-1&1&0&0\\
0&0&1&-1\\0&0&-1&2\end{bmatrix},\qquad
K_{ML}(q)=\operatorname{diag}\left(0,\frac{l(q_2)^2}{2},
\frac{l(q_3)^2}{2},0\right),
\quad B=\frac58(1,1,1,1)^T.
\]

Each two-by-two block of `A` has positive leading minors, so `A` is SPD;
`A+K_ML(q)` remains SPD for every `q`. Set the preload offset to zero and
use the full two-coordinate interface basis. The coefficient is generated
by the diagonal interface factor `diag(l(q2),l(q3))/sqrt(2)`.

Eliminate `q1=(5/8+q2)/2` and `q4=(5/8+q3)/2`. Both remaining equations
become `G(qj)=15/8`, `j=2,3`. Therefore this constructed system has nine
equilibria, including three with reflection symmetry. It preserves the
outer matrix, common load and factorized coefficient structure. It does not
claim that a learned coefficient approximating the actual linear condensed
response takes this form. Exact constant condensation retains uniqueness.

Consequently, the PSD algebra in v3 proves invertibility of a matrix with
its state held fixed. If interpreted as unconditional uniqueness of the
nonlinear equation 19 for arbitrary factor networks, the inference needs
additional assumptions. This does not invalidate reported experiments or
establish an implementation defect.

## Control 2: radial positivity does not supply a potential

On an open neighborhood of the unit square with `x>-1`, define

\[
K(x,y)=\operatorname{diag}(1,(1+x)^2),\qquad
F(x,y)=(x,(1+x)^2y).
\]

This coefficient is SPD and has the affine diagonal factor
`L=diag(1,1+x)`. Nevertheless,

\[
DF=\begin{bmatrix}1&0\\2(1+x)y&(1+x)^2\end{bmatrix},
\qquad \partial_xF_y-\partial_yF_x=2(1+x)y.
\]

The counterclockwise line integral around `[0,1]^2` equals `3/2`, by either
direct edge integration or Green's theorem. Reversing the loop reverses its
sign. Hence no scalar potential generates this force on that neighborhood,
despite `u^TF(u)=x^2+(1+x)^2y^2>=0`. With constant `L`, the loop integral
vanishes and `F` is the gradient of a quadratic energy.

This is an integrability diagnostic for a constructed memoryless map.
It is not frictional dissipation or a physical hysteresis discovery. Applying
a zero-work criterion to contact, history-dependent or dissipative truth
requires a separate valid physical-state contract. The word path-independent
in a model's stated scope does not establish a potential for every map in
its parameterization.

## Consequences for selection and the next admissible update

A derivative condition would genuinely change the mathematical guarantee.
For example, on a convex domain, if the outer matrix satisfies `A>=a I`,
`K>=0`, and the symmetric part of `v -> DK(u)[v]u` has operator norm bounded
by `c<a` uniformly, then the full residual is strongly monotone with modulus
at least `a-c`. This proves at most one equilibrium. Existence still needs
appropriate domain/coercivity assumptions. This standard sufficient bound
is not a novel certificate or evidence that it is feasible to enforce.

For causal attribution, changing an approximation while changing the solver
does not isolate either contribution. A future asset must expose the same
force residual, its consistent derivative, any preconditioning matrix,
initialization, physical residual stopping rule, reference branch and total
cost. A solver-only intervention must leave the force law and load fixed.
An architecture intervention must account for changes in approximation and
training. Linear CG applied to a frozen system, nonlinear CG, and Newton
with a Krylov subsolve are different procedures; no generic solver failure
is inferred from a Jacobian's sign alone.

The generic SPSD-versus-tangent and loop-work directions stop here. The
source's own solver-versus-model ambiguity is not a new matched disagreement
between two primary models. The counterexamples remove an overbroad reading,
not a recorded novelty blocker. There is no new cycle, forecast, candidate
card, status change, outcome access or experiment authorization.

One bounded source-only follow-up is retained: read the exact constitutive
update and integrability/stability hypotheses of Xu2004.00265v1, then compare
the mathematical objects actually constrained. Repeated coefficient/tangent
calculus is an immediate stop. Re-entry requires a separately qualified
truth/control capability or substantive matched disagreement beyond it.

## Private access and truth contract

Only public article text and metadata were read. A web excerpt exposed part
of Parish's article-embedded Appendix A code; it was not executed. No separate
repository source file, notebook, scientific implementation, raw outcome,
model payload, simulation or GPU was accessed. No local article cache was
created: the optional public-HTML fetch failed before receiving content.
This access issue has no scientific interpretation. No PDF was downloaded.

The companion YAML freezes eight fields: estimands; assignment/interference;
lifecycle/replay; rights/release; untouched confirmation; independent
replication; cost; and stop rules. The preprint HTML declares CC BY 4.0;
publisher preview has separate rights. These permissions do not authorize
data access, execution, redistribution or publication in this record.
Published outcomes visible during reading are not Paper G confirmation.
The control algebra was checked by hand; bookkeeping tests validate only
the consistency of records and authorization boundaries.
