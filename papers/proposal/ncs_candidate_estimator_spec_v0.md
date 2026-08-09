# Candidate invariant-gradient estimator v0: mathematical specification and red-team audit

**Frozen:** 2026-08-10  
**Status:** specification complete; **NOT CLEARED as a novel method**  
**Parent gate:** G0 in `plan_v4_ncs.md`  
**Permitted use:** baseline definition and falsification only; do not assign an algorithm name or make a novelty claim

## 1. Target and scope

Let the state-complete simulator be a parameterized Markov chain

\[
S_{t+1}=F_\theta(S_t,\epsilon_{t+1},E_{t+1}),\qquad
E_{t+1}\sim q_\theta(\cdot\mid S_t),
\]

where `S` includes every continuous and discrete latent, absolute time, mutable buffer, cache state and RNG
state needed for the next transition. Assume that the kernel `P_theta` has a unique invariant distribution
`pi_theta`. The first target is the stationary moment

\[
m(\theta)=\pi_\theta h_\theta
=\lim_{H\rightarrow\infty}\mathbb E_\nu[h_\theta(S_H)],
\qquad g(\theta)=\nabla_\theta m(\theta).
\]

A calibration loss `L(m(theta), m_data)` is handled by estimating `g(theta)` and applying the outer derivative
of `L`. Nonlinear distributional losses are not silently covered by this notation. MMD requires independent
stationary pairs (equivalently a product chain) and an unbiased U-statistic; nonlinear plug-in gradients require
sample splitting or an explicit finite-sample bias term.

This specification does not cover a simulator that changes its scientific transition law when autodiff is on.
Forward-law parity is an entry condition, not an estimator feature.

## 2. Finite-horizon hybrid baseline

For burn-in `B`, averaging window `W` and `H=B+W`, define a finite-horizon gradient estimate `G_H`. The
continuous component uses the pathwise tangent `Y_t=dS_t/dtheta`, conditional on the realized event path:

\[
G_H^{\rm pw}=\frac1W\sum_{t=B}^{H-1}
\left(\partial_\theta h_\theta(S_t)+\nabla_s h_\theta(S_t)Y_t\right).
\]

For event-probability parameters, a centered likelihood-ratio version is

\[
G_H^{\rm event}=\frac1W\sum_{t=B}^{H-1}
(h_\theta(S_t)-b_t)\sum_{u=0}^{t-1}
\nabla_\theta\log q_\theta(E_{u+1}\mid S_u),
\]

where a baseline `b_t` may depend on pre-event information but must not introduce bias. StochasticAD or the
generator-gradient estimator may replace this score term only as a named existing baseline. The combined
finite-horizon estimator is `G_H = G_H_pw + G_H_event`.

This hybridization is standard composition. It is not the candidate novelty.

## 3. Randomized horizon correction

Take levels `H_l = H_0 2^l`. Couple `G_l=G_(H_l)` and `G_(l-1)` with common initial state and compatible
randomness, and write `Delta_l=G_l-G_(l-1)`. For an independent random level `N` with
`p_l=P(N>=l)>0`, the sum estimator is

\[
Z=G_0+\sum_{l=1}^{N}\frac{\Delta_l}{p_l}.
\]

Under the usual interchange and summability conditions,

\[
\mathbb E Z=\lim_{l\rightarrow\infty}\mathbb E G_l=g(\theta).
\]

Finite expected cost and variance require, respectively,

\[
\sum_l p_l H_l < \infty,\qquad
\sum_l \frac{\mathbb E\|\Delta_l\|^2}{p_l}<\infty.
\]

Slow or metastable mixing can make these requirements incompatible. In production the level is necessarily
capped at `K`, leaving the exact residual

\[
R_K=g(\theta)-\mathbb E Z_K=\sum_{l>K}\mathbb E\Delta_l.
\]

An empirical decay fit for `Delta_l` is not a proof that `R_K` is small. The output may be called
`theoretically_certified` only when a model-specific contraction/minorization bound controls the tail. Otherwise
it is at most `empirically_resolved`, with the fitted envelope, uncertainty and failed diagnostics reported.

This section is the Rhee--Glynn randomized telescoping construction applied to a gradient sequence. It is not
yet non-equivalent to prior work.

## 4. Persistent ensemble and parameter staleness

At optimizer iteration `k`, each state-bank member stores

\[
(S_i,\;\theta_i^{\rm version},\;t_i^{\rm absolute},\;\mathrm{RNG}_i,\;\mathrm{schema\ version}).
\]

Missing metadata is a hard error. Suppose, only for analysis, that `P_theta` contracts `W_1` by known
`rho<1` and is parameter-Lipschitz with constant `L_P`. A state last equilibrated near `theta_(k-l)` then obeys
the schematic bound

\[
W_1(\mu_i,\pi_{\theta_k})
\le W_1(\mu_i,\pi_{\theta_{k-l}})
+\frac{L_P}{1-\rho}\|\theta_k-\theta_{k-l}\|.
\]

After `r` current-parameter refresh steps, the right-hand side is multiplied by `rho^r`. This separates old
non-equilibrium error from parameter-version drift. In a learned high-dimensional simulator, however, `rho`
and `L_P` are generally unknown. Estimated IACT, split-chain discrepancy or empirical coupling distance are
diagnostics, not substitutes for the bound.

Persistent chains can reduce initialization cost, but randomized infinite-horizon correction already removes
the starting-law bias when its assumptions and sums hold. Staleness mainly changes finite-cap residual and
variance. Merely storing parameter versions does not create a new estimator.

## 5. Required output and error ledger

Every estimate must return a record, not only a tensor:

- point estimate and between-chain interval;
- simulator steps, event count, wall time and peak memory;
- level probabilities, realized levels and coupled increments;
- ESS/IACT, split-chain discrepancy and coupling-distance diagnostics;
- state-bank parameter age and cumulative parameter drift;
- estimated cap residual, its assumptions and `certification_class`;
- event-gradient implementation and variance-control baseline;
- a decision in `{theoretically_certified, empirically_resolved, unresolved}`.

The auditable decomposition is

\[
\widehat g-g=
\underbrace{(\widehat g-\mathbb E\widehat g)}_{\text{Monte Carlo}}
-\underbrace{R_K}_{\text{capped horizon}}
+\underbrace{B_{\rm stale}}_{\text{finite refresh}}
+\underbrace{B_{\rm event}}_{\text{event approximation}}
+\underbrace{B_{\Delta t}}_{\text{time discretization}}
+\underbrace{B_{\rm objective}}_{\text{nonlinear plug-in}}.
\]

An exact score/StochasticAD event term has `B_event=0`; a straight-through or drift proxy does not. A
randomized uncapped estimator has `R_K=0` in expectation only when the summability assumptions hold. No
diagnostic is allowed to set an unmeasured term to zero.

## 6. Non-equivalence audit against nearest methods

| Closest method | Component reproduced here | Irreducible difference established? | v0 verdict |
|---|---|---:|---|
| Glynn--Olvera-Cravioto steady-state LR; Wang--Plechac centered LR | stationary score gradient and centering | No | direct reuse |
| Assaraf--Jourdain--Lelievre--Roux invariant-diffusion sensitivity | long-time tangent/pathwise derivative | No | direct reuse |
| Glynn--Rhee exact estimation and coupled unbiased MCMC | randomized coupled telescoping to equilibrium | No | direct reuse |
| Persistent contrastive divergence / persistent MCMC | state bank carried across parameter updates | No | metadata and rejection logic are engineering controls |
| Arya et al. StochasticAD | unbiased discrete-event derivative | No | named baseline |
| Wang--Blanchet--Glynn generator gradient estimator | high-dimensional continuous/jump SDE gradient | No | named baseline; mandatory E3 comparator |

The fail-visible wrapper is scientifically useful, but v0 has neither a new stochastic identity, a new coupling,
a proved residual bound under weaker assumptions, nor a new variance reduction result. A specialist can describe
the full construction as “persistent chains + hybrid pathwise/LR + Rhee--Glynn truncation + convergence
diagnostics.” Therefore the required non-equivalence test fails.

## 7. Binding decision

1. **G0 remains AMBER / not passed.** This v0 specification must not be implemented or presented as a named
   novel estimator.
2. exp131 remains a valid known-baseline harness; exp132 remains a frozen failed diagnostic. Neither is method
   evidence.
3. E0--E3 candidate comparisons stay blocked until an irreducible mathematical primitive is written down.
   Running more baseline cells cannot resolve novelty.
4. A v1 may proceed only if it contributes at least one of: a new cross-parameter coupling with a proved
   staleness correction; a computable finite-budget residual bound under materially weaker assumptions; or a
   variance/cost result not obtained by the direct composition above.
5. Before v1 coding, that primitive must survive a targeted citation audit and be expressible as a theorem or
   falsifiable estimator identity. If it cannot, the NCS methods route stops and the work retreats to a rigorous
   simulator-audit/benchmark paper.

## 8. Primary sources checked for this specification

- Glynn and Olvera-Cravioto, [Likelihood Ratio Gradient Estimation for Steady-State Parameters](https://doi.org/10.1287/stsy.2018.0023), *Stochastic Systems* 2019.
- Wang and Plechac, [Steady-State Sensitivity Analysis of Continuous Time Markov Chains](https://doi.org/10.1137/18M119402X), *SIAM J. Numerical Analysis* 2019.
- Assaraf et al., [Computation of sensitivities for the invariant measure of a parameter dependent diffusion](https://arxiv.org/abs/1509.01348), 2018.
- Glynn and Rhee, [Exact Estimation for Markov Chain Equilibrium Expectations](https://arxiv.org/abs/1409.4302), *J. Applied Probability* 2014.
- Jacob, O'Leary and Atchade, [Unbiased Markov chain Monte Carlo with couplings](https://arxiv.org/abs/1708.03625), *JRSS B* 2020.
- Tieleman, [Training Restricted Boltzmann Machines Using Approximations to the Likelihood Gradient](https://doi.org/10.1145/1390156.1390290), ICML 2008.
- Arya et al., [Automatic Differentiation of Programs with Discrete Randomness](https://arxiv.org/abs/2210.08572), NeurIPS 2022.
- Wang, Blanchet and Glynn, [An Efficient High-dimensional Gradient Estimator for Stochastic Differential Equations](https://proceedings.neurips.cc/paper_files/paper/2024/hash/a0cd56b91305239e2580dd9440b2e155-Abstract-Conference.html), NeurIPS 2024.
