# Paper G: what a tail-statistic gradient estimates

PRIVATE / INTERNAL — paper-only scope audit, 2026-09-11. Decision: `not_trigger`.
No independently original estimator or theorem is claimed. The calculations below
are analytic controls, not simulator results or evidence of practical model failure.

## 1. Question and repository connection

The closed route `tail_functional_differentiable_simulator_calibration` concerns
calibration of return-tail statistics through EcoMD. Its scientific blockers include
`dependent_path_threshold_bias_unresolved` and `new_bias_variance_cost_theorem_absent`.
The September 4 scope result establishes that differentiating a fixed top-k statistic
alone supplies no new method. This follow-up separates two explanations for an
unhelpful gradient: invalid differentiation of the finite statistic, and valid
differentiation of a statistic whose expectation differs from the intended tail target.
An exact counterexample distinguishes these explanations without outcomes or code.

Let the survival exponent be alpha and the extreme-value index be gamma=1/alpha.
These parameterizations must not be interchanged silently. The intended population
target, finite batch size n, fixed integer k in [1,n-1], and parameter direction
are specified separately throughout.

## 2. Rank changes alone do not invalidate dominated pathwise differentiation

Write z_i(theta,U)=log X_i(theta,U), with positive samples and a
parameter-independent base random variable U. Descending order statistics give

\[
H_k(z)=k^{-1}\sum_{i=1}^k z_{(i)}-z_{(k+1)}.
\]

The top-k average and each order statistic are 1-Lipschitz in the maximum norm;
therefore H_k is 2-Lipschitz, including across rank boundaries. Fix theta_0.
Assume log paths are locally Lipschitz on one deterministic neighborhood, with
max_i |z_i(theta,U)-z_i(eta,U)| <= M(U)|theta-eta| and E M < infinity.
Assume also almost-sure differentiability of every log path at theta_0, no ties
there, and E|H_k(theta_0)|<infinity. Then

\[
\frac{d}{d\theta}\mathbb E H_k(\theta)\bigg|_{\theta_0}
=\mathbb E\left[\frac1k\sum_{i\in I_k(\theta_0)}z_i'
-z_{j_{k+1}(\theta_0)}'\right].
\]

Proof: at a no-tie sample the selected indices are locally fixed by continuity.
The difference quotient is bounded by 2M, so dominated convergence applies.
There is no discontinuous jump at a rank boundary needing a missing surface term.
Independence among the samples is unnecessary for this finite-batch identity.
This does not cover arbitrary support changes, positive-probability ties, adaptive
k, discontinuous sample paths, or lack of domination. For 1/H_k, near-zero H_k
requires an additional integrable bound on reciprocal difference quotients; the
Lipschitz argument for H_k alone is insufficient.

## 3. Exact Pareto control: finite-target and reciprocal effects

For iid U_i uniform on (0,1), let

\[
X_i(\theta)=s(\theta)U_i^{-\gamma(\theta)},\qquad s,\gamma>0.
\]

The iid exponential variables E_i=-log U_i have descending upper excess sum
S_k=sum_{i=1}^k(E_(i)-E_(k+1)) distributed as Gamma(k,1).
For example, conditioning on the threshold and upper labels, exponential
memorylessness makes the unordered upper excesses k iid unit exponentials;
sorting leaves their sum unchanged. Under the common-U coupling S_k is
parameter-independent and scale s cancels exactly. Hence

\[
H_k=\gamma S_k/k,\quad
\mathbb E H_k'=\gamma',\quad
\operatorname{Var}(H_k')=(\gamma')^2/k.
\]

With alpha=1/gamma and alpha_hat=1/H_k=k alpha/S_k,

\[
\mathbb E\widehat\alpha'=\alpha'\frac{k}{k-1}\quad(k>1),
\qquad
\operatorname{Var}(\widehat\alpha')=
(\alpha')^2\frac{k^2}{(k-1)^2(k-2)}\quad(k>2).
\]

These follow directly from E[S_k^{-r}]=Gamma(k-r)/Gamma(k) for k>r.
Multiplying alpha_hat by (k-1)/k yields an unbiased alpha gradient with variance
(alpha')^2/(k-2), for k>2. Reciprocal moments fail at the corresponding small-k
boundaries; derivative divergence statements presume alpha' is nonzero.
These are classical Pareto/order-statistic consequences, not a new correction
for general tails or dependent trajectories.

## 4. A valid gradient can target a changing finite-threshold bias

Consider the smooth interior mixture, for x>=1 and 0<w<1,

\[
\overline F_w(x)=(1-w)x^{-2}+wx^{-1}.
\]

Its asymptotic survival exponent alpha(w)=1 and extreme-value index gamma(w)=1
are constant on the interior. Using iid common uniforms, the exact inverse is

\[
X_w(u)=\frac{w+\sqrt{w^2+4(1-w)u}}{2u}.
\]

Ranks are determined by u for every w, so there are no rank crossings.
Implicit differentiation of u=(1-w)X^{-2}+wX^{-1} gives

\[
q_w(x):=\partial_w\log X_w(u)\big|_{X_w(u)=x}
=\frac{x-1}{wx+2(1-w)},\qquad
\partial_x q_w(x)=\frac{2-w}{[wx+2(1-w)]^2}>0.
\]

Every upper observation exceeds the threshold almost surely. Consequently,

\[
\partial_w H_k
=\frac1k\sum_{i=1}^k q_w(X_{(i)})-q_w(X_{(k+1)})>0,
\qquad \gamma'(w)=0.
\]

On a compact interior neighborhood with w>=w_0>0, 0<=q_w<=1/w_0.
Also 1<=X_w(u)<=1/u, so the finite-batch log maximum is integrable.
Section 2 therefore justifies differentiation of the expectation and proves
E[partial_w H_k]>0, whereas partial_w gamma=0. The gradient is correct for
E H_k: the discrepancy is the derivative of finite-threshold bias.

This construction neither uses a support boundary nor refutes eventual
consistency at fixed positive w under an appropriate intermediate-k limit.
It does not show that every tail loss fails or that EcoMD exhibits this mixture.
It isolates why making sorting differentiable cannot establish calibration of
the asymptotic target. The algebra is a standard diagnostic, not claimed novelty.

## 5. Crossover coverage is a limited cost statement

For 0<w<1/2 the two survival terms are equal at

\[
x_c=(1-w)/w,\qquad p_c=\Pr(X>x_c)=2w^2/(1-w).
\]

For iid sample size n, the chance of any observation above x_c is
1-(1-p_c)^n <= n p_c. Let N_c count exceedances. A Hill threshold above x_c
requires N_c>=k+1, so Markov's inequality gives

\[
\Pr(X_{(k+1)}>x_c)\le \min\{1,np_c/(k+1)\}.
\]

Thus n w^2 much smaller than k makes even crossing this equality threshold
unlikely. A threshold well inside the heavier-tail regime is more demanding.
This is a Hill threshold-coverage calculation, not an any-algorithm minimax
lower bound: a known parametric mixture can use bulk observations, and its
interior asymptotic exponent is already specified. The growing second-order
coefficient (1-w)/w identifies a need for parameter-uniform tail assumptions;
no uniform derivative-consistency or impossibility theorem is proved here.

## 6. Primary-work scope and decision

[Drees, *Extreme Quantile Estimation for Dependent Data with Applications to
Finance*, Saarland preprint 68, submitted August 14, 2002](https://scidok.sulb.uni-saarland.de/bitstream/20.500.11880/26274/1/preprint_68_02.pdf)
develops dependent-tail inference using stationary beta-mixing, joint-tail and
tail-approximation conditions. Section 2 conditions T0–T3 concern a tail
functional; T3 is interpreted as Hadamard differentiability at the limiting
Pareto quantile function. Theorem 2.2 states extreme-quantile asymptotic
normality under the preceding assumptions and condition (15).
This statistical functional derivative must not be equated with a simulator
parameter derivative uniformly over a parameter-dependent family. Selected
text passages were inspected; no full-proof verification or empirical reproduction
is claimed. [Pareto GAN](https://proceedings.mlr.press/v139/huster21a.html),
revisited at abstract scope, supplies existing EVT-aware heavy-tail generation
context, not the proofs of Sections 2–5.

Decision: `not_trigger`; no recorded route-level blocker is removed. Rank
nonsmoothness alone is not sufficient grounds to reject pathwise gradients,
but valid finite-batch differentiation does not establish the desired population
tail sensitivity. The separate dependent-path calibration and new joint
bias/variance/cost requirements remain unresolved.

Retain four analytic controls for future evaluation. Stop soft-sort and scalar
Pareto-mixture variants as topic generators. A substantive next result would
need parameter-uniform gradient calibration under explicit tail regularity and
dependence, with a contribution beyond the existing parent theory and comparison
at equal computational cost. That requirement is a re-entry condition, not a
new topic or permission to implement experiments.
