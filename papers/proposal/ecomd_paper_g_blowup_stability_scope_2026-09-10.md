# Paper G: blow-up stability, clock and explicit truth-family scope

**PRIVATE / INTERNAL. Development analysis; public_evidence_eligible: false.**
Session started 2026-09-10 02:35 NZST. Previous goal turn: progress.
This resolves the stability-theorem follow-up from the
[event-time preflight](ecomd_paper_g_singularity_event_truth_preflight_2026-09-10.md).

**Decision: partial_capability; stop generic neural singularity-certificate
expansion.** A concrete stability theorem and an explicit event-time reference
family are now available at paper-only scope. Generic neural profile search,
normalization, asymptotic constraints and stability verification have direct
parents. No contribution blocker is removed. No topic cycle or harvest begins.

## The actual stability theorem

[Hou–Nguyen–Wang](https://doi.org/10.1007/s00205-026-02191-7), ARMA 250:28
(2026), treat \(a_t=\Delta a+a^2\) on \(\mathbb R^n\), with decay at infinity.
Their Theorem 1 uses

\[
\bar u(z)=(1+|z|^2/8)^{-1},\quad
a_0=\lambda^{-1}(\bar u+g),\quad k=2n+10,
\qquad \|g\|_{\mathcal E_k}\le C_0\lambda,\quad0<\lambda<\lambda_0.
\]

The perturbation is even in every coordinate. Its norm includes a singularly
weighted \(L^2\) term **and** a weighted derivative of order \(k\). The result
establishes finite-time blow-up with a logarithmic spatial correction. It is not
a theorem assuming merely small unweighted prediction error. In one dimension
\(k=12\). The proof gives thresholds in terms of energy-estimate constants;
those constants have not been numerically certified in this audit.

Selected final-article sections 1–3 and the local-existence discussion were read
from the author-hosted PDF. Theorem, normalization and closing-bootstrap pages
3, 6 and 15 were visually checked. No verification software was executed.

## A conditional physical-clock consequence

Use the source's one-dimensional normalization, with perturbation \(v\):

\[
\hat u=\bar u+v=C_u(\tau)a(C_l(\tau)z,t(\tau)),\quad
t_\tau=C_u,\quad \lambda=C_u/C_l^2,
\quad v(0)=v_{zz}(0)=0.
\]

The source's modulation identities are

\[
(\log C_u)_\tau=-1+\lambda/4,
\qquad \lambda_\tau=-(1+4v_{zzzz}(0))\lambda^2.
\]

Here is an elementary consequence, not a new theorem. If the full stability
bootstrap applies from \(\tau_0\), it supplies \(0<\lambda(\tau)\le
\lambda(\tau_0)<4\) thereafter, and \(C_u\to0\) at the physical singularity.
Because \((C_u)_t=-1+\lambda/4\), integration gives

\[
C_u(\tau_0)\le T-t(\tau_0)
\le\frac{C_u(\tau_0)}{1-\lambda(\tau_0)/4}.
\]

This makes the clock input explicit, but a learned profile does not certify
membership in the theorem's initial-data class. The bootstrap and normalization
must concern the actual solution. It is not sufficient to integrate a learned
rate over a finite window or attach a pointwise residual loss.

## A fully explicit event-time family from elementary comparison

The scalar event interval can be obtained independently of the high-order
stability theorem for a restricted family. This is a **standard comparison
construction**, rederived here as a reusable truth asset, with no novelty claim.

Consider the maximal bounded classical solution of

\[
u_t=u_{xx}+u^2\quad\text{on }\mathbb R,\qquad
u(0,x)=\frac1{a+bx^2},\quad a>0,\quad0<b<\tfrac12.
\]

Let \(T_\infty\) be its maximal time in the bounded-solution class. The smooth,
bounded initial function admits the standard local Cauchy solution; bounded
\(L^\infty\) norm permits continuation. Define

\[
U(t)=\frac1{a-t},\qquad
L(t,x)=\frac1{a-(1-2b)t+bx^2}.
\]

The constant-in-space \(U\) is a solution, dominates the initial field, and
stays bounded on compact time intervals below \(a\). Comparison and the
boundedness continuation criterion therefore imply \(T_\infty\ge a\).

Writing \(D=a-(1-2b)t+bx^2>0\), direct differentiation gives

\[
L_t=(1-2b)D^{-2},\quad
L_{xx}=-2bD^{-2}+8b^2x^2D^{-3},\quad
L_t-L_{xx}-L^2=-8b^2x^2D^{-3}\le0.
\]

Thus \(L\) is a subsolution with exactly the same initial data. Comparison
holds on each compact interval below both maximal times. If the true solution
existed past \(a/(1-2b)\), then \(u(t,0)\ge L(t,0)\to\infty\) would
contradict bounded classical existence there. Hence

\[
\boxed{a\le T_\infty\le\frac a{1-2b}}.
\]

No integration, learned model, unspecified stability constant or numerical
outcome is needed for this statement. The bound is an enclosure, not the exact
time; it does not identify the blow-up profile or assert sharpness. Its relative
width is \(2b/(1-2b)\). Loss of this upper bound at \(b\ge1/2\) is not a
claim of global regularity or a physical critical point. The event norm is
\(L^\infty\); no equivalence with another norm is asserted.

For the unperturbed HNW initial family, \(a=\lambda\), \(b=\lambda/8\).
The same interval \([\lambda,\lambda/(1-\lambda/4)]\) follows for
\(0<\lambda<4\) from these barriers alone. The richer logarithmic-profile
conclusion still requires its own theorem; the wider interval-validity range
does not extend that theorem.

### Scaling and the required baseline

Under \(u_s(t,x)=s^2u(s^2t,sx)\), the initial parameters become
\((a/s^2,b)\). Thus varying \(a\) at fixed \(b\) gives scaled copies; varying
\(b\) changes the invariant

\[
-u_0''(0)/u_0(0)^2=2b.
\]

One can fix \(a=1\) and vary \(b\) to avoid counting scale copies as different
physical controls. The entire initial field is still required: no universal
event law determined only by this curvature ratio is proposed. All examples
remain one equation/reference lineage, not independent replication.

The elementary predictor \(T_{\rm ODE}=a\) already has guaranteed error at
most \(2ab/(1-2b)\) on this family. A neural result must beat an appropriate
classical baseline under an adequate reference resolution. Compatibility with
the interval cannot establish such an improvement, and generating many members
of this family does not by itself yield a substantial research question.

## Why the previous Dirichlet reference cannot be spliced into HNW

The previous published interval concerns a bounded Dirichlet problem. Centering
its polynomial at the midpoint makes it even, but does not remove the boundary.
For \(f(x)=(192/5)x(x-1)(x^2-x-1)\),

\[
f'(0)=192/5,\qquad f'(1)=-192/5.
\]

The zero extension is continuous with jumps in its first derivative at both
endpoints. Its weak second derivative contains nonzero point masses. It is
therefore not locally \(H^2\) across those endpoints, and cannot meet the
weighted \(H^{12}\) hypothesis, whose weight is positive and finite there.
Moreover, full-line and Dirichlet evolution are different problems. Smoothing
or evolving an extension changes the initial-value contract; it cannot inherit
the published Dirichlet time interval without a separate proof.

This is a mathematical scope obstruction. It is not an implementation failure
or a criticism of either source theorem.

## Low-order normalized agreement does not supply the missing norm

For \(n=1\), the HNW zeroth-order weight is
\(\rho(z)=|z|^{-6}+10^{-3}\). Choose an even compactly supported smooth
\(\phi(z)=z^4\eta(z)/24\), with \(\eta=1\) near zero, and let
\(g_{\epsilon,\sigma}(z)=\sigma\epsilon^4\phi(z/\epsilon)\),
\(\sigma\in\{-1,1\}\). These perturbations preserve the origin value and
second derivative, but

\[
g_{\epsilon,\sigma}^{(4)}(0)=\sigma,\qquad
\|g_{\epsilon,\sigma}\|_\rho^2
=\epsilon^3\int\phi(y)^2|y|^{-6}dy
+10^{-3}\epsilon^9\int\phi(y)^2dy\to0.
\]

The corresponding *initial* modulation derivatives have opposite signs:
\(\lambda_\tau=-5\lambda^2\) for \(\sigma=1\), and
\(\lambda_\tau=3\lambda^2\) for \(\sigma=-1\). For sufficiently small
\(\epsilon\), both total initial profiles remain positive. Meanwhile
\(\|\partial^{12}g_{\epsilon,\sigma}\|_2^2
=\epsilon^{-15}\|\phi^{(12)}\|_2^2\), so the full stability norm is not
small. This standard concentration control explains why omitting the derivative
term changes the theorem. It does not prove different ultimate blow-up types,
neural training failure, or a new theorem beyond functional analysis.

## Direct method parents and next decision

[Wang et al., arXiv v1](https://arxiv.org/html/2506.19243v1) already combine
neural singularity profiles with origin derivative constraints, parity,
asymptotic information and specialized optimization. Its Sections 2–4 also
explicitly connect this work to the HNW stability framework. A generic
“PINN plus normalization plus proof” contribution is therefore occupied.
The preprint was inspected; final TMLR text/status identity was not established.

[Chen–Hou–Nguyen–Wang](https://arxiv.org/html/2407.15812v1), selected introduction
and main-result setup, extend the normalization/stability approach with
translation and rotation. Simply removing evenness is not a new direction.
[Fasondini–King–Weideman](https://doi.org/10.1016/j.physd.2023.133660), publisher
abstract only, already study reciprocal variables and periodic heat blow-up.
Neither its asymptotics nor its numerical post-event continuation are imported
into the full-line comparison argument.

The explicit interval family is positive infrastructure progress. The
scientific contribution, independent confirmation and cost advantage remain
unqualified. Stop collecting generic singularity certificates or proposing
normalization/reciprocal-coordinate variants under this formulation.
Re-entry needs a named, matched physical mechanism disagreement or a theorem
with a nonclassical residual contribution; apply the existing truth controls
to that claim. Another interval or smoothness penalty is insufficient.

No raw question, search cycle, full audit, forecast, machine card, scientific
implementation, solver, outcome arrays, source-code execution, GPU/SSH,
participants, outreach, purchase, publication, commit or push occurred.
The original Paper G objective remains active and unachieved.
