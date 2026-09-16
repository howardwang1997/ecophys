# Paper G: tail consistency does not imply tangent consistency

PRIVATE / INTERNAL — paper-only scope audit, September 11, 2026.
Decision: `not_trigger`. These are standard limit/differentiation controls,
not an independently original theorem, simulator result or qualified topic.

## Question

The preceding [tail-gradient audit](ecomd_paper_g_tail_gradient_target_scope_2026-09-11.md)
separated valid finite-batch differentiation from finite-threshold bias. It left
open whether consistent tail estimation, strengthened to parameter-uniform
consistency, suffices for a consistent gradient. This follow-up answers that
precise question and gives a sufficient tangent condition. It continues the
scientific scope audit of `tail_functional_differentiable_simulator_calibration`;
it is not a new candidate cycle or another scalar-mixture method proposal.

## 1. A smooth valid quantile family

Let theta in [-1/4,1/4], t>=1, l=log t and a=1+l. Define the upper-tail quantile

\[
\log Q_\theta(t)
=2\log t+\frac{\sin(\theta(1+\log t)^2)}{1+\log t}-\sin\theta.
\tag{1}
\]

It has Q_theta(1)=1, tends to infinity, and is strictly increasing because

\[
\partial_l\log Q_\theta(e^l)
=2+2\theta\cos(\theta a^2)-\frac{\sin(\theta a^2)}{a^2}
\ge 2-\tfrac12-1=\tfrac12.
\]

Consequently X_theta=Q_theta(1/U), for U uniform on (0,1), defines a continuous
positive distribution with smooth parameter paths and parameter-independent
ranks under this coupling. Its tail quantile satisfies

\[
\sup_\theta\left|\log\frac{Q_\theta(t)}{e^{-\sin\theta}t^2}\right|
\le\frac1{1+\log t}\longrightarrow0.
\tag{2}
\]

In particular every member has extreme-value index gamma(theta)=2 and survival
exponent alpha(theta)=1/2. Both population parameter derivatives are zero.
The quantile ratio is regularly varying even uniformly over theta for each
fixed multiplicative argument. This is a value-level statement, not uniform
regularity of its parameter derivative. No second-order derivative condition
or dependent-process realization is asserted.

## 2. Uniform Hill consistency

Take n iid common uniforms, L_i=-log U_i iid Exp(1), descending order, and
1<=k<n. Set T=L_(k+1) and

\[
A_{n,k}=\frac1k\sum_{i=1}^k(L_{(i)}-T),\qquad
H_{n,k}(\theta)=\frac1k\sum_{i=1}^k
\log\frac{Q_\theta(e^{L_{(i)}})}{Q_\theta(e^T)}.
\]

The constant -sin(theta) cancels. Since L_(i)>=T,

\[
\sup_\theta|H_{n,k}(\theta)-2A_{n,k}|
\le \frac2{1+T}.
\tag{3}
\]

For any deterministic intermediate sequence k=k_n with k_n->infinity and
k_n/n->0, T->infinity in probability. To see this, for every finite M the
number of L_i>M divided by n tends to exp(-M)>0, whereas (k_n+1)/n->0.
Also k A_(n,k) is Gamma(k,1), hence E A=1 and Var A=1/k. Therefore

\[
\sup_\theta|H_{n,k_n}(\theta)-2|\xrightarrow{P}0,
\qquad
\mathbb E\sup_\theta|H_{n,k_n}(\theta)-2|\longrightarrow0.
\tag{4}
\]

The latter follows from E|A-1|<=1/sqrt(k), equation (3), and bounded
convergence in probability of 2/(1+T). Thus even the expected Hill objective
converges uniformly to the constant true index.

## 3. Its correct gradient converges to the wrong target

The parameter tangent of (1) is

\[
v_\theta(l)=\partial_\theta\log Q_\theta(e^l)
=(1+l)\cos(\theta(1+l)^2)-\cos\theta.
\]

At theta=0, v_0(l)=l, and consequently

\[
\partial_\theta H_{n,k}(0)=A_{n,k},\qquad
\mathbb E\partial_\theta H_{n,k}(0)=1,\qquad
\operatorname{Var}(\partial_\theta H_{n,k}(0))=1/k.
\tag{5}
\]

For each finite n, |v_theta(l)|<=l+2 yields an integrable local path bound
using max_i L_i. Dominated finite-batch expectation differentiation is valid,
so d E[H_(n,k)(theta)]/dtheta at zero is exactly 1. As k_n->infinity,

\[
\partial_\theta H_{n,k_n}(0)\xrightarrow{L^2}1
\ne\gamma'(0)=0.
\tag{6}
\]

This is genuine gradient inconsistency despite uniform value consistency.
It is not a finite-n differentiation error, rank crossing, support change or
failure of Hill consistency. It illustrates the classical noncommutation of
parameter differentiation and a limit; smoothness at every finite t is insufficient.

## 4. A sufficient tangent condition, with its scope exposed

For a general strictly increasing upper-tail quantile Q_theta, on a compact
parameter interval, suppose differentiable log paths have the representation

\[
\partial_\theta\log Q_\theta(e^l)
=b(\theta)+\gamma'(\theta)l+r_\theta(l),\qquad
\sup_\theta|\gamma'(\theta)|\le C<\infty,
\]

and impose the separate tail-tangent condition

\[
\varepsilon(M):=\sup_{\theta,\,l\ge M}|r_\theta(l)|\longrightarrow0.
\tag{7}
\]

This is sufficient, not claimed necessary. Under common iid uniforms and fixed
deterministic k, ranks are unchanged and the constant b(theta) cancels, giving

\[
\sup_\theta|\partial_\theta H_{n,k}(\theta)-\gamma'(\theta)|
\le C|A_{n,k}-1|+2\varepsilon(T).
\tag{8}
\]

For an intermediate k sequence, (8) gives uniform consistency in probability
of the sample gradient. Indeed T->infinity in probability and epsilon(M)->0;
only the high-probability large-T event is needed if epsilon is infinite near
zero. Expectation convergence requires additional uniform integrability or
an integrable low-threshold bound, and is not automatic. Differentiation of
E H likewise still requires its own finite-n domination assumption.

The counterexample violates (7): gamma'=0, while its tangent at zero grows as l
after any constant b(0) is subtracted. Equation (2) bounds the size of the
quantile remainder but does not control its parameter derivative.

This simple iid bound supplies neither a dependent-path convergence rate,
adaptive threshold method, minimax result, nor computational advantage. It uses
an analytic quantile representation that a simulator generally does not expose.

## 5. Source and novelty boundary

The existing [Drees preprint68, 2002, Section2 T0–T3 and Theorem2.2](https://scidok.sulb.uni-saarland.de/bitstream/20.500.11880/26274/1/preprint_68_02.pdf)
treats the derivative of a statistical functional at a limiting tail quantile
and dependent-tail asymptotics under explicit conditions. Its selected text was
revisited. It does not, by itself, justify exchanging simulator-parameter
differentiation and the extreme-tail limit in an arbitrary smooth family.
The construction above is not asserted to meet all its asymptotic-normality
assumptions, and does not refute that theorem. No new primary source or full
proof review is claimed. Equations (1)–(8) are self-contained manual controls.

The family was analytically designed to separate two theorem assumptions; no
market-native mechanism, simulator occurrence or empirical prevalence is
established. Encoding a standard failure of derivative/limit interchange in a
tail quantile does not alone qualify a Paper G contribution.

Decision: `not_trigger`. The original dependent-path gradient calibration and
novel bias/variance/cost blockers remain. The useful resolution is precise:
uniform value-level tail control is insufficient; any proposed gradient theorem
must control tail tangents or supply another valid interchange argument. Stop
this scalar analytic branch after recording the counterexample and sufficient
condition. Re-entry needs a nonstandard theorem for an independently motivated
model class or a qualified truth asset, not another oscillatory construction.
