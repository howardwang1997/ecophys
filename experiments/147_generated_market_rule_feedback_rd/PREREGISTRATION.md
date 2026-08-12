# Experiment 147 — generated annual market-rule-feedback RD preflight

**Frozen:** 2026-08-13

**Branch:** `endogenous-market-rule-feedback-v5`

**Parent audit:** `research/theory_exploration/market_rule_feedback_audit_v5.md`

**Scientific role:** generated identification and implementation stress only; cannot establish a market effect,
method novelty, EcoMD validity or venue readiness

## 1. Question

Can the frozen V5 analysis distinguish a real discontinuity in the next annual controller input from smooth annual
dynamics, regression to the mean and known design failures at sample sizes bounded by blind official-register
counts?

The preflight has two jobs:

1. verify that an established robust local-linear RD implementation controls false positives and detects a
   standardized 5% jump under admissible generated cases; and
2. verify that mass-point, sorting, attrition, shared-rule and zero-first-stage cases are rejected by design guards
   instead of being promoted as market feedback.

Passing validates only the code path and the declared design boundary. It does not authorize instrument-level
FITRS values. A failure keeps every real-data and compute gate locked.

## 2. Frozen estimand and estimators

For one normalized statutory cutoff,

\[
X=\log(N/c),\qquad Z=1[X\ge 0],\qquad
Y=m(X)+\tau Z+\alpha_y+\epsilon.
\]

The target is the jump `tau` at zero. Generated observations span six input years, 2018--2023, with 240 candidate
rows per year before optional attrition. `N/c` is generated on `[0.8,1.2]`; this matches the blind 20% count window
without using any instrument record. In standard cases, `N/c` is uniform on that interval, optional ADNT rounding
is applied on the level scale, and `X` is recomputed from the rounded level. The generated conditional mean is
`0.5 X + b X^2 + alpha_y + tau_y Z`, where `b`, `alpha_y` and `tau_y` are frozen in `config.yaml`. Year indicators
enter the primary estimator as predetermined covariates.

Every stochastic stream is order-independent. Its NumPy `SeedSequence` entropy is the first four unsigned
32-bit words obtained by interpreting the first 16 digest bytes, four bytes at a time, in big-endian order from
`SHA256("14720260813|<scenario>|<cutoff>|<sigma>|<replicate>")`. Cutoff and sigma use Python
`format(value, ".12g")`; replicate is base-10 with no leading zero. Changing this formatter or any stream label
requires Experiment 148.

### Primary estimator

Use the official Python `rdrobust==2.0.0` implementation with cutoff zero, local-linear point fit `p=1`, quadratic
bias correction `q=2`, triangular kernel, `bwselect="mserd"`, 95% robust bias-corrected interval and
`masspoints="adjust"`. Independent cases use `vce="hc3"`. Generated repeated-identifier cases use their frozen
cluster labels and `vce="cr3"`. No global polynomial result may enter a gate.

The gated point estimate is the package's bias-corrected jump `tau_bc`; rejection and interval coverage use the
package's robust bias-corrected p-value and confidence-interval row. The conventional point estimate, interval and
p-value are retained for audit but cannot enter a gate. The configuration's confidence level `0.95` is passed to
the package as `level=95`.

If the package API cannot execute these frozen options, the result is `IMPLEMENTATION_OR_SPEC_FAILURE`; options
may not be silently substituted. Any repair uses Experiment 148.

### Bias-bound oracle

For declared independent Gaussian cases only, also fit separate triangular-weighted local-linear regressions in the
fixed bandwidth from `config.yaml`. Given the generated conditional-mean curvature bound `M` and known noise
standard deviation `sigma`, form the conditional fixed-design interval

\[
\widehat\tau\ \pm\left[z_{0.975}\sigma\sqrt{\sum_i a_i^2}
+\frac{M}{2}\sum_i |a_i|X_i^2\right],
\]

where `a` are the combined left/right intercept weights. This is an oracle check of whether discrete support and a
declared smoothness class permit honest coverage. It is not a practical estimator and cannot be used on market
data with `M` or `sigma` estimated after seeing outcomes.

The oracle applies only to `smooth_null`, `rounded_null` and `curved_null`. The known generated year effects are
subtracted before fitting. For each case `M=2|b|`, and the conditional mean is evaluated at the post-rounding `X`,
so the bound remains the declared one on the observed support. Oracle construction refuses singular side-specific
designs or fewer than the frozen minimum number of distinct support points inside the bandwidth.

## 3. Frozen generated cases

All parameters and seeds live in `config.yaml`. Every stochastic case has 300 independent Monte Carlo replicates.

### Admissible null cases

- `smooth_null`: continuous running variable, smooth conditional mean and `tau=0`.
- `rounded_null`: published ADNT rounded to 0.01 transaction/day before recomputing `X`, with `tau=0`.
- `curved_null`: larger but declared smooth curvature, 0.01 rounding and `tau=0`.
- `regression_to_mean_null`: draw latent log liquidity `L` uniformly on the frozen latent support, draw baseline
  measurement noise `u_0`, and rejection-sample until `X_raw=L+u_0` lies in the ordinary running-variable support.
  Round `c exp(X_raw)` as declared and recompute `X`. Generate `Y=alpha_y+rho L+u_1`, with independent Gaussian
  `u_1`. Thus cutoff assignment is based on a noisy baseline measurement, the follow-up regresses toward latent
  liquidity with `rho<1`, and assignment itself has exactly zero effect. This case is excluded from the curvature
  oracle because its post-rounding conditional-mean bound is not supplied to the estimator.
- `mcar_attrition_null`: 15% outcome loss independent of side, running variable and outcome.
- `clustered_null`: 240 generated identifiers each occur once in every one of the six years. Each identifier adds
  one Gaussian random intercept shared across its six observations; the running variable and idiosyncratic noise
  are independently regenerated by identifier-year. Cluster-robust inference uses the identifier.

Each null is evaluated at normalized versions of cutoffs 10 and 600 where listed in `config.yaml`. The cutoff
changes rounding severity but does not change the normalized estimand.

### Admissible effect cases

- `reinforcing`: observed assignment ITT `tau=+0.05`.
- `corrective`: observed assignment ITT `tau=-0.05`.
- `mixed_exposure`: the full-exposure shift is `0.05 / mean(f_y)`, multiplied by the six frozen year-specific
  fractions `f_y`; because their arithmetic mean is exactly 0.75, the balanced-design mean observed ITT is exactly
  `+0.05`.
- `clustered_reinforcing`: `tau=+0.05` with repeated identifiers and cluster-robust inference.

The noise standard deviation for pass/fail power is 0.10 log units, so the frozen standardized effect is 0.5. A
secondary `sigma=0.20` power curve is descriptive only: no generated residual scale is evidence about real ADNT.

### Inadmissible diagnostic cases

- `sorting`: the probability of appearing above the cutoff is 0.65 within the symmetric generation window. A
  two-sided exact binomial continuity proxy at alpha 0.01 must flag the case. It is a preflight guard, not a
  substitute for the preregistered real-data density test. Each replicate draws an absolute `X` uniformly on
  `[0,h]` and assigns its sign independently with the frozen right-side probability.
- `differential_attrition`: follow-up loss depends on cutoff side and a latent outcome shock. A two-sided
  difference-in-proportions test at alpha 0.01 must flag the case. Its loss probability is the frozen base rate
  plus a right-side increment plus a positive-standard-normal-shock increment, clipped to `[0,1]`; the shock is
  generated before loss and is not supplied to the test.
- `coarse_mass_points`: cutoff 10 ADNT is rounded to whole transactions/day. The estimator must not run when fewer
  than 10 distinct values exist on either side inside the fixed bandwidth.
- `shared_rule_cutoff`: cutoffs 80 and 2,000 must be rejected by the rule registry regardless of the estimated
  jump because RTS 28 changes reporting groups at the same values.
- `zero_tick_first_stage`: generated price/cutoff pairs with identical adjacent statutory ticks must be rejected;
  declared nonzero pairs must be admitted by the same deterministic table.

The diagnostic cases cannot pass by producing the expected sign. Correct behavior is refusal or an explicit
invalid-design code.

## 4. Frozen metrics and gates

For every primary-estimator null case:

- observed two-sided rejection rate at 5% must be at most 0.08;
- robust-interval coverage must be at least 0.90;
- the 95% Wilson upper bound for rejection must be at most 0.11;
- fit/specification failures must be at most 0.02; and
- absolute median point-estimate bias `|median(tau_hat)-tau|` must be at most 0.01.

For each pass/fail effect case at `sigma=0.10`:

- two-sided power must be at least 0.80;
- the 95% Wilson lower bound for power must be at least 0.75;
- sign accuracy must be at least 0.95;
- absolute median bias `|median(tau_hat)-tau|` must be at most 0.01; and
- fit/specification failures must be at most 0.02.

For each declared independent null oracle case:

- bias-bound interval coverage must be at least 0.94; and
- oracle construction failures must be at most 0.01.

Diagnostic gates are:

- sorting detection at least 0.90;
- differential-attrition detection at least 0.90;
- coarse-mass-point refusal exactly 1.00;
- shared-rule-cutoff refusal exactly 1.00; and
- all frozen zero/nonzero statutory tick first-stage labels exactly correct.

The overall decision is `GENERATED_RD_PREFLIGHT_PASS` only if every applicable gate passes. Otherwise it is
`GENERATED_RD_PREFLIGHT_FAIL` or `IMPLEMENTATION_OR_SPEC_FAILURE`. There is no partial scientific pass and no
automatic threshold relaxation.

Fit-failure rates use all 300 replicates as denominator. Rejection, coverage, power, sign and estimator-bias
metrics use successful fits only, and their Wilson intervals use that same successful-fit denominator. A cell
with zero successful fits is an implementation/specification failure. Diagnostic detection rates use all 300
diagnostic replicates. All scenario-by-cutoff pass/fail cells must pass separately; pooling cannot rescue a failed
cell. The `sigma=0.20` cells are recorded but excluded from the overall decision.

## 5. Interpretation and routing

A PASS authorizes only preparation of a real-data preregistration and immutable source/licence/file manifest. It
does not authorize opening ESMA instrument pairs, downloading FCA ZIPs, unsealing the UK jurisdiction or contacting
remote workers. Before any values, V5 still requires a licence-safe date-correct price/corporate-action source and
a committed cutoff-10 plus price-qualified-cutoff-600 first-stage design.

A FAIL from null calibration, coverage, power or diagnostic routing retires the current V5 identification plan
before market outcomes. A failure caused only by package/API implementation may be repaired in Experiment 148 with
a new preregistration; the Experiment 147 artifact remains immutable.

## 6. Chronology and artifact contract

1. Commit and push this preregistration, README and configuration before the estimator module, runner or generated
   result exists.
2. Implement `ecomd/research/market_rule_feedback_preflight.py`,
   `tests/test_market_rule_feedback_preflight.py` and
   `experiments/147_generated_market_rule_feedback_rd/run_preflight.py`.
3. Run focused tests only, then commit the implementation.
4. Create `FREEZE.yaml` containing the preregistration commit, implementation commit, exact hashes and dependency
   versions; commit and push it before the formal run.
5. Execute exactly once from a clean checkout with network disabled in the runner and write
   `artifacts/raw/preflight.json`. Refuse overwrite.
6. Any change to a seed, DGP, estimator option, threshold or failure mapping requires Experiment 148.

The result schema must record every scenario, replicate count, fit failure, Wilson interval, estimator option,
package version, input-file hash, git SHA, wall time and resource audit.

## 7. Resource and data boundary

- Inputs: generated constants in `config.yaml` only.
- Market, FITRS instrument, price, paid, R2, user and sealed data: forbidden.
- Network during the formal run: forbidden.
- Compute: Mac CPU only, at most four processes, 12 CPU core-hours, 8 GB RAM and 90 minutes wall time.
- GPU hours: zero. V100-A, V100-B and RTX2060 are not contacted or queued.
- Temporary development output is forbidden before the chronology freeze; focused unit tests use deterministic
  micro-fixtures and cannot execute the 300-replicate suite.
