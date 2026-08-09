# Experiment 135 — latent-flow misspecification and observation-only stress

**Frozen:** 2026-08-10, before implementation or results  
**Status:** G3 synthetic falsification preflight only  
**Cost boundary:** Mac CPU, generated data only, no purchased data, no V100/H20

## Question

Does the signed-flow component used in exp134 distinguish a correctly specified latent driver from four cases
that should defeat or qualify it: observed-flow autocorrelation, a combined latent/observed mechanism, a lagged
latent driver, an even nonlinear latent driver and a complete null? The test must compare against an
observation-only baseline on a strict future split and must expose near-nonidentifiability rather than forcing a
winner.

Passing does not validate EcoMD, solve the latent sign gauge, reproduce a real limit-order book or unlock paid
L2 data. It only shows that the evaluator rejects several synthetic wrong stories instead of rewarding any
correlated latent series.

## Frozen data-generating processes

For each stream,

\[
z_t=\rho z_{t-1}+\sqrt{1-\rho^2}\epsilon_t,
\qquad \epsilon_t\sim N(0,1),
\]

with `rho in {0.0, 0.8, 0.98}`. Let `q_t in {-1,+1}` be displayed signed flow and `q_(t-1)` its observed lag.
The conditional probability is `P(q_t=+1)=sigmoid(ell_t)`. Six frozen truth families are used:

| Truth family | `ell_t` |
|---|---|
| `latent_current` | `2 * 0.8 * z_t` |
| `observation_only` | `2 * 0.8 * q_(t-1)` |
| `combined` | `2 * (0.6 * z_t + 0.6 * q_(t-1))` |
| `latent_lagged` | `2 * 0.8 * z_(t-1)` |
| `latent_even` | `2 * 0.6 * (z_t^2 - 1)` |
| `null` | `0` |

`q_-1` and `z_-1` are independent stationary draws. Each `(truth, rho)` cell has 8 independent streams of
30,000 events. Child seeds are spawned once from root seed `135_202_608`. The first 60% of every stream is used
for fitting and the last 40% only for scoring. No seed or threshold changes are permitted after output is seen.

This experiment isolates signed flow; exp134 already tests queue reconstruction and the other event marks. No
claim about book mechanics may be inferred from exp135.

## Frozen candidate and baseline models

All models are unregularized Bernoulli maximum-likelihood fits with an intercept. Feature columns use the factor
two below so fitted coefficients match the truth table:

- `null`: intercept only;
- `latent_current`: `2 z_t`;
- `observation_only`: `2 q_(t-1)`;
- `combined`: `2 z_t`, `2 q_(t-1)`;
- `latent_lagged_oracle`: `2 z_(t-1)`;
- `latent_even_oracle`: `2 (z_t^2-1)`.

Every model is fit on the same training indices and scored by held-out nats per event. Report fitted
coefficients, convergence, held-out log likelihood, gains over `null`, and pairwise gains required by the gates.
The oracle labels are binding: they diagnose misspecification and are not deployable baselines when the true lag
or nonlinearity is unknown.

## Frozen hard gates

All statements below refer to the median across 8 independent streams in each `rho` cell.

1. Every fit converges, all values are finite and every train/test count is exact.
2. Under `latent_current`, the latent coefficient has at most 7.5% relative error; `latent_current` beats
   `observation_only` by at least 0.03 held-out nats/event; adding observed lag gives at most 0.003 nats/event.
3. Under `observation_only`, the observed-lag coefficient has at most 7.5% relative error;
   `observation_only` beats `latent_current` by at least 0.08 nats/event; in the combined fit the absolute latent
   coefficient is at most 0.08 and its gain over `observation_only` is at most 0.003 nats/event.
4. Under `combined`, both coefficients have at most 10% relative error and the combined model beats each
   single-source model by at least 0.02 nats/event.
5. Under `latent_lagged`, the oracle lag coefficient has at most 7.5% relative error. For `rho=0.0` and `0.8`,
   the lagged oracle beats the current-latent model by at least 0.03 nats/event. At `rho=0.98` the gap is reported
   but has no winner threshold: high collinearity is an a-priori identifiability warning, not permission to call
   current and lagged causally equivalent.
6. Under `latent_even`, the oracle even coefficient has at most 10% relative error, beats the linear-current
   model by at least 0.05 nats/event, and the absolute linear-current slope is at most 0.08.
7. Under `null`, the largest positive held-out gain of any non-null model over the null has median at most
   0.001 nats/event, and every median absolute non-intercept coefficient is at most 0.05.

The experiment passes only if every threshold passes. A failure remains visible and triggers a separately
preregistered v2; thresholds may not be relaxed in place.

## Interpretation boundary

A PASS permits the observation evaluator and these baselines to be reused in a later EcoMD adapter experiment.
It does not establish that `latent_flow_alignment` drives market messages. That requires a state-complete EcoMD
adapter, a predeclared temporal alignment, an externally fixed buy/sell sign anchor, and comparison on data not
used to select the emission family.
