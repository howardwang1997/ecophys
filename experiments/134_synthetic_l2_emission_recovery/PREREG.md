# Experiment 134 — synthetic L2 emission and parameter recovery

**Frozen:** 2026-08-10, before implementation or results  
**Status:** G3 observation-bridge feasibility only; not an EcoMD or real-market validation  
**Cost boundary:** Mac CPU, generated data only, no purchased data, no V100/H20

## Question

Can a minimal, explicitly defined latent-to-visible-queue observation operator emit LOBSTER-compatible aggregate
messages that reconstruct its book exactly, and can its conditional emission parameters be recovered on a
strict future time split? A negative control must show that the same recovery does not survive when the latent
driver is permuted.

Passing only establishes identifiability of this synthetic operator under correct specification. It does not
show that EcoMD has the right latent variable, that real order flow follows this law, or that price formation is
identified.

## Frozen latent process

For every independent stream,

`z_t = rho z_(t-1) + sqrt(1-rho^2) epsilon_t`, `epsilon_t ~ Normal(0,1)`.

- `rho in {0.0, 0.8, 0.98}`;
- conditional flow slopes `beta in {0.0, 0.5, 1.0}`;
- 8 independent streams per `(rho, beta)` cell;
- 30,000 events per stream;
- one frozen root seed, with child seeds spawned before simulation;
- first 60% of each stream for fitting, final 40% for held-out scoring.

The temporal split is binding even though the data are synthetic.

## Frozen aggregate-queue emission law

The displayed book has five fixed price levels per side and large positive initial queues. Each event emits the
LOBSTER fields `(time, event_type, order_id, size, price, direction)` plus an after-event L5 snapshot.

1. Hidden execution indicator has probability `p_hidden = 0.08`. Event type 5 leaves every displayed queue
   unchanged exactly.
2. A visible event is an addition with probability `p_add = 0.50`; otherwise it is a removal. Removal type
   probabilities for cancel/delete/visible-execution (`2/3/4`) are `(0.45, 0.15, 0.40)`.
3. Define signed displayed flow `q = direction * action`, where `action=+1` for additions and `-1` for removals.
   Then `P(q=+1 | z) = sigmoid(2 beta z)`; direction is implied by `q` and action.
4. Level `l in {0,...,4}` has probability proportional to `exp(-eta l)`, with `eta = 0.70`.
5. `size - 1` is Poisson with log mean `log_mu + gamma |z|`, where `log_mu = log(7)` and `gamma = 0.25`.

Initial queues are `100,000` units, so the frozen event count and size law should not require reflection or
forced events. Any non-positive queue hard fails rather than modifying the generated action.

This is an aggregate visible-depth operator. `order_id` is a schema identifier only: price-time priority,
individual-order cancellation consistency, inside-spread placement, queue depletion and price moves are outside
this experiment.

## Frozen reconstruction and estimators

- Reconstruct all ten queue-size series from the initial book and emitted messages; compare every after-event
  L5 snapshot exactly and verify hidden executions make no displayed change.
- Fit `beta` by conditional Bernoulli maximum likelihood without an intercept.
- Estimate `p_hidden`, `p_add` and removal-type probabilities by their training frequencies.
- Fit `eta` by the truncated-geometric likelihood.
- Fit `(log_mu, gamma)` by a Poisson log-link likelihood.
- Report each parameter on every independent stream and held-out per-event log-likelihood gain over:
  `beta=0` for signed flow and `gamma=0` for size.

The implementation may use stable Newton/bisection solvers but may not change the model, split, seeds, event
count or thresholds after results are visible.

## Frozen negative and gauge controls

1. Independently permute `z` within the training and held-out blocks, refit `beta`, and score on the permuted
   held-out block. This should remove the conditional signal while preserving all marginal event counts.
2. Replace `z` by `-z`. The fitted slope must flip sign while held-out likelihood remains numerically equal.
   This records a real gauge limitation: L2 messages alone cannot orient an otherwise unsigned latent coordinate.

## Hard gates

- Message reconstruction and hidden-display invariance are bit-exact for every stream; no queue becomes
  non-positive.
- For `beta in {0.5,1.0}`, median absolute relative recovery error in every `rho` cell is at most 10% and at
  least 7/8 stream estimates have the correct sign.
- For `beta=0`, median absolute fitted slope in every `rho` cell is at most `0.05`.
- Median held-out signed-flow log-likelihood gain is at least `0.04` nats/visible event for `beta=0.5` and
  `0.12` for `beta=1.0`; for `beta=0`, its absolute median is at most `0.002`.
- Under the permuted-latent control, median absolute slope is at most `0.05` and absolute median held-out gain
  is at most `0.002` in every nonzero-`beta` cell.
- Sign-gauge fits obey `|beta_flipped + beta_fitted| <= 1e-8` and held-out likelihood differs by at most
  `1e-12` per event.
- Across all 72 streams, median absolute error is at most `0.02` for `p_hidden`, `p_add` and every removal-type
  probability, and at most `0.05` for `eta`.
- Across all streams, median absolute relative error for `gamma` is at most 15% and median held-out size
  log-likelihood gain over `gamma=0` is positive.
- Every optimizer/solver converges and every reported value is finite.

Any failed gate remains visible. Passing permits implementation of an EcoMD adapter as the next G3 step; it
does not permit paid-data purchase or a real-data claim. Before real L2 use, a separate protocol must add price
levels/moves, order-level consistency, latency/aggregation, censoring and model-misspecification tests.

