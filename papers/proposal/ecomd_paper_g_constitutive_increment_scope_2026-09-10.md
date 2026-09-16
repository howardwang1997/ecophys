# Paper G: incremental constitutive laws and refinement controls

PRIVATE / INTERNAL. `public_evidence_eligible: false`.
Session started 2026-09-10T02:41:56Z. Previous goal turn: no progress
(record confirmation only). This audit supplies new source evidence and
exact controls; the overall publication-level objective remains unachieved.

**Decision: not a qualified re-entry trigger.** The bounded Xu follow-up
resolves the promised source question. It distinguishes zero-increment
consistency, finite-step integration error, continuous path dependence and
the derivative used by a nonlinear solver. These are standard distinctions;
the generic positivity/integrability citation chain stops here.

The repository connection remains learned physical responses and constraint
generalization in neural-PDE work. No Paper D outcomes or implementation
history are used. The closed numerical-teacher route and its elementary-
certificate/direct-parent blockers remain unchanged.

## What was read

[Xu, Huang and Darve, arXiv2004.00265v1](https://arxiv.org/pdf/2004.00265v1),
April 1, 2020: selected Sections 2.2–3.1, with printed pages 5–7 visually
checked against the PDF. Equations 12 and 17 define time consistency as
`Delta sigma -> 0` when `Delta epsilon -> 0`, with a bounded-network
condition. Equations 15–19 use `H=L L^T` in an incremental stress update,
evaluated at the new strain for nonlinear elasticity. Plasticity also uses
previous strain and stress; the text acknowledges that longer history may
be needed. Strain softening is explicitly outside scope.

The audit concerns this preprint, not an assumed identical journal version.
The related DOI is `10.1016/j.jcp.2020.110072`. The source's repository link
was not followed. Published outcome tables incidentally visible in web
search within the paper are not adopted as evidence of Paper G performance
or failure. Search-indexed Simo/Pister and Romano/Barretta material provided
historical routing only; neither full text was audited, and their differing
finite-deformation formulations are not a qualified opposing-model pair.

## Control 1: finite-step path drift can vanish under refinement

Use a scalar strain `x` and the positive tangent `H(x)=(1+x)^2` on `x>=0`.
Its exact stress and convex energy, with zero reference constants, are

\[
\sigma(x)=x+x^2+x^3/3,\qquad
W(x)=x^2/2+x^3/3+x^4/12,\qquad W''=H>0.
\]

Apply the endpoint update corresponding to the source's equation 19:

\[
\sigma_{n+1}=\sigma_n+H(x_{n+1})(x_{n+1}-x_n).
\]

Load from `0` to `a>0` with `m` equal steps and unload along the same
strain path using `m` equal steps. With `h=a/m`, the final residual stress is

\[
\sigma_{\rm final}-\sigma_0
=h\left[\sum_{j=1}^m H(jh)-\sum_{j=0}^{m-1}H(jh)\right]
=\frac{2a^2+a^3}{m}.
\]

The identity follows by telescoping. The continuum constitutive law is
elastic, and this residual tends to zero. Constant `H` makes it zero even
at finite step size. It is therefore insufficient to infer material memory
from a nonzero finite-step stress return alone. This is an exact quadrature
control, not a trained-network result or an implementation defect.

Zero-increment consistency also does not mean exact subdivision invariance.
For loading `0 -> h`, a single endpoint update exceeds two half updates by

\[
\frac h2\{H(h)-H(h/2)\}=\frac{h^2}{2}+\frac{3h^3}{8}.
\]

Both satisfy the source's zero-increment limit. That definition is retained;
it is not silently replaced by a stronger claim and then refuted.

The algorithmic derivative with the previous state held fixed is

\[
\frac{\partial\sigma_{n+1}}{\partial x_{n+1}}
=H(x_{n+1})+H'(x_{n+1})(x_{n+1}-x_n).
\]

For the large unloading step `x_n=1,x_{n+1}=0`, it equals `-1`, although
`H(0)=1`. This is finite-increment differentiation of an otherwise integrable
scalar tangent. It says nothing about an actual source solver's convergence.
The constant-H null again eliminates the additional term.

## Control 2: refining a nonintegrable rate law does not restore elasticity

Now strain is `(x,y)` in an open neighborhood of the unit square, with
`x>-1`. Prescribe the continuous rate relation

\[
d\sigma=H(x,y)\,d\epsilon,\qquad
H=\operatorname{diag}(1,(1+x)^2),\qquad \epsilon=(x,y).
\]

`H` is SPD with an affine diagonal factor. Starting from zero stress at the
origin, the path `x first, then y` to `(1,1)` produces `(1,4)`, while `y
first, then x` produces `(1,1)`. A counterclockwise rectangular strain loop
therefore leaves the stress increment `(0,3)`. Every straight segment has
constant relevant tangent entries, so subdivision leaves this result
unchanged, even at finite step size. Reversing the path changes its sign.

This is a **stress increment obtained by integrating a matrix-valued rate
law**. It differs from the scalar force-work integral `3/2` in the preceding
SPSD audit, which used a memoryless force `F=H epsilon`. The two quantities
must not be conflated.

On a simply connected strain domain, a smooth matrix field can be the
Jacobian of a single-valued stress only if its rows are closed:

\[
\partial_k H_{ij}=\partial_j H_{ik}.
\]

Here `partial_x H_22=2(1+x)` but `partial_y H_21=0`. Symmetry of `H`
alone is insufficient. If row integrability holds and `H` is symmetric,
the resulting stress has a scalar potential; PSD then controls convexity
on convex domains.
These are standard potential-theory conditions, not a new theorem.

For a null control, let `W=x^2/2+y^2/2+alpha x^4/4`, `alpha>=0`.
Then `H=Hessian W=diag(1+3 alpha x^2,1)` is SPD and integrable; every
continuous closed strain loop returns to the same stress. Endpoint
quadrature can still produce finite-step errors of the first kind.

The constructed nonintegrable law is not evidence of actual material
hysteresis. Plasticity intentionally retains internal state, so equal strain
endpoints do not imply equal complete physical states. Any physical elastic
test must fix stress/strain measures, material regime and work conjugacy;
finite-deformation objective-rate claims require their own full contract.

## Selection decision and next admissible action

The cheap separating observation is now precise: compare the same prescribed
strain path at successively finer increments, and separately compare two
different paths with the same endpoints in a physically elastic regime.
The first changes discretization; the second changes loading history.
Neither operation by itself identifies a new physical mechanism. A matched
study would need an unchanged constitutive model, independently qualified
elastic truth, complete internal state, exact physical work convention and
a nonstandard residual after these controls. None is supplied here.

The source does not remove either recorded novelty blocker. No new candidate,
cycle, forecast, machine card or scientific execution is authorized. Generic
SPSD, zero-increment consistency, algorithmic tangent and loop-integrability
extensions are closed at this scope audit. Do not continue by following
another citation for another elementary counterexample. The next useful
preflight must identify a concrete new truth/control asset or matched primary
disagreement that can distinguish physical explanations beyond these known
effects, then qualify its re-entry trigger before harvesting questions.

## Access and verification scope

One public arXiv PDF was downloaded to a private temporary path; its SHA-256,
text extraction and three page renders are in the source manifest. Printed
pages 5–7 were inspected visually. The arXiv distribution license does not
grant a downstream open-source/data license. No repository code, notebooks,
models or raw outcomes were accessed or executed. No simulation, scientific
implementation, GPU, outreach or publication occurred. Tool access errors
are private process details with no scientific meaning.

The two controls were derived and checked by hand. Registry tests validate
record consistency only. The companion contract freezes estimands,
assignment/interference, lifecycle/replay, rights/release, confirmation,
replication, cost and stop rules. There is no untouched confirmation asset
and no independent reproduction of the paper's models.
