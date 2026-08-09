# Experiment 129 — analytic invariant-gradient feasibility

**Frozen:** 2026-08-09, before examining results  
**Status:** G0 diagnostic, not a new-method claim  
**Resources:** CPU only, synthetic data only

## Model and truth

Use the scalar AR(1) discretization

\[
x_{t+1}=a x_t+\sigma\epsilon_t,\qquad \epsilon_t\sim\mathcal N(0,1),
\]

with `sigma=0.3` and `a in {0.2, 0.8, 0.97}`. Its invariant second moment and derivative are

\[
v(a)=\frac{\sigma^2}{1-a^2},\qquad
v'(a)=\frac{2a\sigma^2}{(1-a^2)^2}.
\]

Each estimator targets `v'(a)`. Use 2,000 independent replicates. The short horizon is 24 and the long
reference horizon is 2,048.

## Estimators

1. `fresh_short`: start at zero and differentiate a 24-step final statistic.
2. `persistent_detached`: run 2,048 steps to approach stationarity, detach/reset the tangent, then
   differentiate only 24 further steps. This isolates the missing stationary-state derivative.
3. `full_long`: differentiate through all 2,048+24 steps from zero.
4. `stationary_oracle`: sample the exact stationary initial condition including its pathwise derivative.
5. `finite_difference_crn`: centered finite difference with common random numbers and `delta=1e-4` after
   a 2,048-step trajectory.
6. `rhee_glynn_linear`: an established randomized telescoping equilibrium estimator using suffix-coupled
   horizons `h_l=l+1`; survival probability is frozen as
   `q=min(0.995, max(0.6, a^2+0.02))`.

The randomized estimator is explicitly a known baseline, not the candidate contribution.

## Metrics

For every regime and estimator report mean, bias, relative bias, replicate standard deviation, standard error,
RMSE of the Monte Carlo mean, sign accuracy, and mean simulator steps. Do not rank only by bias while ignoring
variance or cost.

## Feasibility interpretation

- Expected: `fresh_short` becomes biased as mixing slows.
- A persistent state with a detached tangent is not assumed correct; it passes only if its bias is empirically
  small at the stated horizon.
- `stationary_oracle` and `full_long` are correctness controls.
- The randomized baseline is useful only if it reduces bias without an unusable variance/cost explosion.

This experiment cannot pass G0. It can falsify the premise that a new estimator is needed, expose which baseline
already solves the problem, or identify the slow-mixing regime in which a candidate must improve the
accuracy--cost Pareto frontier.

