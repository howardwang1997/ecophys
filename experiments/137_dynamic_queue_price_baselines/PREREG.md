# Experiment 137 — dynamic queue/price bridge with strong observation baselines

**Frozen:** 2026-08-10, before implementation, pilot output or formal results

**Status:** G3 synthetic falsification preflight only

**Cost boundary:** generated data plus existing free schema fixtures; two 16-core V100-host CPUs are allowed;
the GPUs are not used; no purchased data and no H20

## Question

After adding state-complete queue depletion and price moves, can the evaluator distinguish a genuinely
incremental EcoMD-like latent driver from a purely observation-driven marked-flow process? The latent model must
beat a queue-reactive plus marked-Hawkes-logit baseline only under latent-incremental truth, must add nothing
under observation-only truth, and must survive declared latency/censoring controls without lookahead.

A PASS is not real-market validation. The process generates its own messages and uses a stylized deterministic
book reset after best-queue depletion. The test may validate dynamic plumbing and kill weak evaluators; it
cannot establish that EcoMD drives market order flow or unlock paid L2 data.

## Frozen dynamic book

- Five aggregate levels, one-tick spread, initial mid tick `10_000`, and initial queue `32` at every displayed
  level.
- Each event first reads the pre-event book and history. A signed-flow mark `q_t in {-1,+1}` is then drawn;
  `q_t=+1` means bid addition or ask removal, and `q_t=-1` means ask addition or bid removal.
- Addition probability is `0.45`. Removal types 2/3/4 use probabilities `(0.45, 0.15, 0.40)`; hidden type 5
  has probability `0.05` and does not modify displayed depth.
- Level probability is proportional to `exp(-0.70 * level)`. Event size is
  `1 + Poisson(exp(log(7) + 0.15*abs(z_t)))`.
- A non-best removal is truncated to leave one displayed unit. A best removal that reaches its queue records
  exactly the remaining displayed size, moves the mid by `sign(q_t)`, and deterministically resets all five
  levels to queue 32 around the new one-tick-spread mid. This reset rule is part of the observable schema, not
  latent randomness.
- The complete generator state contains book, mid, next event/order IDs, true marked-flow traces, previous
  signed flow and NumPy RNG state. Monolithic, chunked and serialized-resume generation must be bit-exact.
- An independent reconstructor receives only the initial state, messages and frozen reset rule. It must recover
  every after-event book, mid tick and price-move mark exactly.

The dynamic operator is deliberately aggregate and stylized. It does not claim individual-order price-time
priority, exchange latency or a calibrated queue-reset distribution.

### Pre-formal implementation clarification — executable non-best removals

After the first unit test, but before any pilot/formal statistic or fitted result existed, the following
previously unspecified boundary was frozen. For an addition or hidden event, the level law remains exactly
proportional to `exp(-0.70*level)`. For a displayed removal, the same weights are conditioned on executable
levels: level 0 is always eligible because depletion invokes the declared price reset, while a non-best level
is eligible only when its displayed queue exceeds one. The chosen non-best removal is then truncated to leave
one unit. This prevents zero-size/no-op messages without changing truth coefficients, thresholds, seeds,
counts, censoring or any fitted model. The original commit remains the audit record of the ambiguity.

## Frozen truth families and stress cells

For each stream, `z_t` is stationary Gaussian AR(1) with `rho in {0.60, 0.95}`. Let `h_t` be a pre-event
displayed-flow EMA with decay `0.80`, and let `I_t=(Q_bid-Q_ask)/(Q_bid+Q_ask)` use pre-event best queues. The
signed-flow probability is `P(q_t=+1)=sigmoid(ell_t)`:

| Truth | `ell_t` |
|---|---|
| `latent_incremental` | `2 * (0.65*z_t + 0.50*h_t + 0.40*I_t)` |
| `observation_only` | `2 * (0.70*h_t + 0.55*I_t)` |

After each event, the true EMA is updated only for displayed messages. For evaluator censoring, an independent
Bernoulli mask removes `0%` or `20%` of displayed messages from the observed history and fitting set; the true
process still receives every displayed event. Censoring is generated prospectively and never depends on the
event sign, price move or fitted likelihood.

The Cartesian product is `2 truths x 2 rho values x 2 censor rates = 8 cells`. Each cell has 8 independent
streams of 40,000 events, for 64 streams and 2,560,000 generated events. Seeds are spawned once from root seed
`137_202_608`; no seed is replaced. The first 60% of retained displayed events is training and the final 40%
is held out by absolute event time.

## Frozen no-lookahead features and baselines

Every feature is snapshotted before event `t`. Observed traces update only after an uncensored displayed event.
All fits are unregularized Bernoulli maximum likelihood with an intercept and identical train/test indices:

- `null`: intercept only;
- `latent_current`: `2*z_t`;
- `latent_lag3`: `2*z_(t-3)`;
- `queue_reactive`: `2*I_t` and log pre-event best-depth ratio;
- `marked_hawkes`: pre-event signed-flow EMAs with decays `0.50`, `0.80`, `0.95`;
- `observation_full`: queue-reactive and all three marked-flow traces;
- `combined_current`: current latent plus `observation_full`;
- `combined_lag3`: lag-3 latent plus `observation_full`;
- `combined_permuted`: latent independently permuted inside train and test blocks plus `observation_full`.

`marked_hawkes` is a discrete marked-Hawkes-logit baseline, not a continuous-time Hawkes likelihood. The report
must retain this qualifier. Report coefficients, convergence, held-out nats per retained displayed event,
pairwise gains, censoring degradation, price-move counts/rates and reconstruction diagnostics.

## Frozen execution and merge

- Formal execution uses two shards. Shard 0 contains even global stream indices; shard 1 contains odd indices.
  Node identity must not affect seeds or results.
- Each worker uses one process and one BLAS/PyTorch thread. CUDA is hidden from the process. Expected total is
  below 12 CPU core-hours and 4 GiB RAM per worker.
- Each shard records protocol hash, git SHA, dirty flag, stream IDs, environment and records. The merger hard
  fails on a missing/duplicate stream, protocol mismatch, wrong git SHA, dirty formal tree or unexpected count.
- Pilot/smoke output is written outside the formal artifact path. Formal thresholds are not inspected or
  changed between shard execution and merge.

## Frozen hard gates

1. All 64 streams have exact event/train/test counts, finite values and converged fits. Stream IDs and seeds are
   unique and the two-shard merge is complete.
2. Monolithic versus fixed chunks `(137, 499, 61, 803, 1500, remainder)` plus a serialized resume after event
   1,500 are bit-exact for every message, pre-event feature, snapshot, mid path and terminal generator state.
3. Independent reconstruction is bit-exact; all after-event queues are positive; every nonzero price move has
   the same sign as signed flow; each stream has both up and down moves; each cell's median move rate lies in
   `[0.002, 0.050]`.
4. Under `latent_incremental`, in every `(rho,censor)` cell the median `combined_current - observation_full`
   held-out gain is at least `0.015` nats/event, and `combined_current - latent_current` is at least `0.005`.
5. Under `latent_incremental` with zero censoring, the median fitted current-latent coefficient in
   `combined_current` has at most 15% relative error from `0.65` and at least 7/8 signs are positive.
6. Under `observation_only`, in every `(rho,censor)` cell `observation_full - latent_current` is at least
   `0.020` nats/event, `combined_current - observation_full` is at most `0.003`, and the median absolute latent
   coefficient in `combined_current` is at most `0.08`.
7. `combined_permuted - observation_full` has median absolute gain at most `0.003` and median absolute permuted
   coefficient at most `0.10` in every cell.
8. For `latent_incremental, rho=0.60`, `combined_current - combined_lag3` is at least `0.010` nats/event in both
   censor cells. At `rho=0.95`, the gap is reported without a winner threshold because high persistence is an
   a-priori temporal-identifiability warning.
9. Moving from zero to 20% censoring may reduce likelihood, but gates 4, 6 and 7 must still pass. A result that
   survives only uncensored history is a formal FAIL.

The experiment passes only if every applicable threshold passes. No threshold, truth coefficient, stream or
seed may be edited after any pilot or formal output is inspected. A v2 requires a new preregistration and an
independent seed family.

## Interpretation boundary and next gate

A PASS permits this dynamic operator and the three observation baseline families to enter a later G3 protocol.
G3 remains open until the same definitions work on external messages, a real continuous-time point-process
baseline is included, timestamp/sign conventions are externally validated, and train/test data are not
generated by the fitted family. A FAIL blocks paid L2 and model-to-real language; it does not justify weakening
the baselines or thresholds.
