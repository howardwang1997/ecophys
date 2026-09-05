# EcoMD Zumbach-orientation re-entry audit

**Date:** 2026-09-05

**Mode:** outcome-blind source, exact-population and primary-work audit under the saturated-family
re-entry rule

**Decision:** **NO-GO / KILL as an ICLR topic. Quarantine the current Zumbach score as an invalid
time-reversal statistic; do not implement, rescore, retrain, SSH or use GPU under this route.**

## 1. Frozen question and rival explanations

The market-native object is the direction of the cross-scale dependence between squared returns and
future realized volatility. The repository repeatedly interpreted a negative
`zumbach_asymmetry` score as evidence that EcoMD lacked a causal volatility-feedback mechanism.

- **H1 — mechanism failure:** the simulator's state and transition law cannot produce the empirical
  arrow from past return innovations to future volatility.
- **H0 — evaluator orientation bias:** the implemented statistic compares two different ordinary
  lag distances, so any positively autocorrelated volatility process with decaying memory is driven
  negative even when its law is time reversible.
- **Decisive result:** evaluate the implemented population functional on a stationary reversible
  process with a symmetric, non-increasing volatility autocovariance. A valid antisymmetric
  statistic must be zero. A strictly negative value identifies the evaluator rather than the model.

Both outcomes would matter. H1 would justify a state/mechanism search only after the statistic
passed its null contract. H0 invalidates the historical sign-floor interpretation and prevents a
new architecture or GPU sweep from optimizing a geometrically biased target.

## 2. What the production evaluator actually computes

Let $v_t=r_t^2$, let $w$ be `coarse_window`, and let
$g=\texttt{max_lag}+1$. The production evaluator in
`ecomd/eval/stylized_facts.py:604-675` defines

\[
 c_t={1\over w}\sum_{j=0}^{w-1}v_{t-g-j},\qquad
 D_k=\operatorname{Corr}(c_t,v_{t+k})-
     \operatorname{Corr}(c_t,v_{t-k}).
\]

The differentiable training objective in `ecomd/training/losses.py:67-119` mirrors the same
functional. The inserted gap prevents shared samples, but it does not make the two orientations
comparable: $v_{t+k}$ is farther from every element of $c_t$ than $v_{t-k}$.

The canonical score nevertheless requires `zumbach_asymmetry` in `[0.001, 0.5]`, and the only
synthetic null check is iid Gaussian noise. The GARCH test merely accepts any finite value between
`-0.2` and `0.5`; it therefore cannot detect the failure below.

## 3. Exact reversible-process counterexample

Suppose $v_t$ is covariance-stationary and time reversible, with autocovariance
$C(h)=C(-h)$. Since the variances in both correlations are independent of $k$,

\[
 \operatorname{Cov}(c_t,v_{t+k})={1\over w}\sum_{j=0}^{w-1}C(g+j+k),
\]

and, because $g>k$,

\[
 \operatorname{Cov}(c_t,v_{t-k})={1\over w}\sum_{j=0}^{w-1}C(g+j-k).
\]

If $C(h)$ is non-increasing for $h\geq 0$, every summand in the first expression is no larger
than its partner in the second. Hence $D_k\leq0$, with strict inequality whenever the covariance
decreases on one compared lag. For the explicit reversible exponential law
$C(h)=C(0)\rho^{|h|}$, $0<\rho<1$,

\[
 D_k\ \propto\ {\rho^g(1-\rho^w)\over w(1-\rho)}
                 (\rho^k-\rho^{-k}) < 0.
\]

This is attainable with nonnegative squared returns: take a stationary reversible two-state Markov
chain $V_t\in\{a,b\}$ with positive values and second eigenvalue $\rho$, draw independent
Rademacher signs $\epsilon_t$, and set $r_t=\epsilon_t\sqrt{V_t}$. Then $r_t$ is reversible,
$r_t^2=V_t$, and the centered covariance is exactly
$\operatorname{Var}(V_t)\rho^{|h|}$.

Thus the implementation assigns a negative arrow of time to a broad class of reversible,
volatility-clustered processes. Passing the iid test is uninformative because iid data have
$C(h)=0$ at every nonzero lag, exactly the special case in which the artifact vanishes.

## 4. The correct comparison swaps the roles

The standard Zumbach-effect definition compares the same two objects under a reversal of their
roles at a common separation. El Euch, Gatheral, Radoičić and Rosenbaum write, for daily squared
return $r_t^2$ and integrated variance $\sigma_t^2$,

\[
 Z_t(k)=\operatorname{Cov}(r_t^2,\sigma_{t+k}^2)
       -\operatorname{Cov}(r_{t+k}^2,\sigma_t^2).
\]

This population difference is zero under time reversal and can be nonzero in rough Heston. The
repository even contains a closer role-swapping implementation in
`ecomd/eval/time_irreversibility.py:94-112`, although its boundary padding and finite-sample null
still require a separate audit. It is not the function used by the canonical eleven-fact scorer or
the differentiable loss.

## 5. Consequences for prior EcoMD evidence

The following interpretations are no longer admissible without a clean rescore under a frozen,
null-calibrated definition:

1. the claim that a negative canonical Zumbach score proves an architectural time-asymmetry floor;
2. pass-rate comparisons for `ar1_s05`, `zumbach_dn_s10` or combinations that optimized the biased
   functional;
3. the portion of the eleven-fact Pareto ceiling whose trade-off is created by this score; and
4. any causal-mechanism claim based on moving the score from negative to positive.

This does **not** establish that EcoMD has the correct Zumbach effect. It removes the old evidence in
both directions. The model already has explicitly causal EMA feedback and asymmetric drag, so the
earlier proposal that an otherwise reversible architecture structurally forbids the statistic is
also false at source level.

## 6. Why the correction is not an ICLR contribution

The exact bug is important, but the obvious paper claim is occupied:

- Zumbach's original work already constructs statistics that vanish for time-reversal-invariant
  series and applies them to financial processes.
- El Euch et al. give the role-swapped covariance definition and an explicit rough-Heston result.
- Bauer, Schölkopf and Peters give a consistent arrow-of-time procedure and theorem for non-Gaussian
  VARMA models.
- GrandPre, Teza and Bialek directly estimate forward-versus-reverse trajectory KL and correct
  finite-sample errors on detailed-balance and nonequilibrium controls.
- Kim et al. give a neural entropy-production estimator with a rigorous steady-state objective, and
  Solowjow et al. give a kernel two-sample test for dependent dynamical systems with mixing-based
  guarantees. Applying such critics to forward and reversed blocks occupies the obvious learned or
  kernel path-law test.

Replacing the faulty expression by the standard role swap is a correctness repair, not a new
algorithm. Antisymmetrizing an arbitrary path functional as
$f(x)-f(\mathcal R x)$ is elementary. No new power, minimax, finite-sample calibration or
computational guarantee has been supplied beyond these parents.

Diagnostic ICLR survival for the current formulation is **1--3%**. This is not a prospective
forecast; the hard failure is standard-parent reduction after the evaluator defect is removed.

## 7. Re-entry contract

Re-audit only if a written method exists that simultaneously:

1. is exactly zero at population level for every law invariant under a declared time-reversal
   involution, including odd-parity state variables;
2. has finite-sample type-I error or confidence coverage for one dependent trajectory, with
   boundary and overlapping-window effects included;
3. has a theorem or lower-bound separation not reduced to forward/reverse trajectory KL,
   classifier two-sample tests, VARMA arrow identification, signature/path-kernel MMD or existing
   entropy-production estimators;
4. beats those parents at equal sample and compute budgets on at least two independent non-EcoMD
   systems with reversible and irreversible controls; and
5. freezes an untouched market confirmation partition before any corrected EcoMD or real-market
   outcome is opened.

A future QA decision may authorize implementing and validating a corrected metric. That would not
by itself create a research card or authorize model selection, training or three-server GPU work.

## 8. Compute decision

No candidate passed. This audit opened no new outcome file, ran no simulator, changed no model or
metric code, made no SSH connection to `100.113.230.38`, `100.80.236.112` or `100.123.220.57`, and
allocated zero A800/V100 work.

## Primary sources

1. Gilles Zumbach, *Time reversal invariance in finance*:
   https://arxiv.org/abs/0708.4022
2. Omar El Euch, Jim Gatheral, Radoš Radoičić and Mathieu Rosenbaum, *The Zumbach effect under rough
   Heston*: https://arxiv.org/abs/1809.02098
3. Stefan Bauer, Bernhard Schölkopf and Jonas Peters, *The Arrow of Time in Multivariate Time
   Series*: https://proceedings.mlr.press/v48/bauer16.html
4. Trevor GrandPre, Gianluca Teza and William Bialek, *Direct estimates of irreversibility from time
   series*: https://arxiv.org/abs/2412.19772
5. Dong-Kyum Kim, Youngkyoung Bae, Sangyun Lee and Hawoong Jeong, *Learning entropy production via
   neural networks*: https://arxiv.org/abs/2003.04166
6. Friedrich Solowjow et al., *A Kernel Two-sample Test for Dynamical Systems*:
   https://arxiv.org/abs/2004.11098
