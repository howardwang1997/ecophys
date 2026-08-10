# Experiment 138 — external continuous-time queue/Hawkes baseline gate

**Frozen:** 2026-08-10, before implementation, synthetic pilot, real likelihood fit or target result

**Status:** G3 external-baseline preflight only

**Cost boundary:** five already-tracked free LOBSTER streams plus generated controls; CPU only on the two
16-core V100 hosts; CUDA hidden; no purchase, no H20 and no compute expansion

## Question and claim boundary

Can the observation evaluator support a genuine continuous-time marked point-process likelihood on external
messages, preserve the vendor's causal row order and sign convention, and show that aligned queue state adds
held-out information beyond a full multiscale Hawkes history without exploiting timestamp ties or future book
states?

A PASS validates an external baseline/evaluation harness. It does not fit EcoMD to a market, establish that
`latent_flow_alignment` drives real order flow, pass G3, justify a physical claim or unlock paid L2. No EcoMD
latent appears in the external likelihood in this experiment.

## Information inspected before freezing

Exp130 had already inspected the first 200,000 rows per archive for schema, exact visible-depth reconstruction
and elementary correlations. Before this freeze, a metadata-only full-stream audit counted rows, event types,
directions, first/last timestamps, negative time increments and exact timestamp ties. It did **not** construct
queue features, fit any model, compute any target likelihood or inspect train/test performance.

That audit found nondecreasing raw time in every canonical stream but 3.14%--10.67% zero interarrival times,
with vendor row order still distinguishing sequential book updates. Therefore an explicit tie policy and a
tie-policy sensitivity are frozen below; treating these data as a simple point process without one is forbidden.

## Frozen external streams

Only one archive per symbol enters model fitting, preventing depth variants of the same symbol/day from being
treated as independent evidence. All rows are processed.

| Stream | Depth | Window | Rows | Zero-`dt` | SHA-256 |
|---|---:|---|---:|---:|---|
| AAPL | L10 | 09:30--16:00 | 400,391 | 4.012% | `32683931...e9d43` |
| AMZN | L10 | 09:30--16:00 | 269,748 | 3.145% | `5cff62a6...a54f` |
| GOOG | L10 | 09:30--16:00 | 147,916 | 5.772% | `2fa66b61...dde4a` |
| MSFT | L10 | 09:30--16:00 | 668,765 | 8.554% | `0825e00e...be4c` |
| SPY | L50 | 09:30--10:30 | 1,154,737 | 10.673% | `2d562be8...7b991` |

The total is 2,641,557 messages. AAPL L50 and MSFT L1/L50 remain non-independent schema fixtures and do not
enter formal cross-symbol medians. Archive and embedded-ReadMe hashes must match
`data/sample/LOBSTER/PROVENANCE.md`; a mismatch is a hard failure.

## Frozen external sign and six marks

The embedded vendor ReadMe, SHA-256 `fd97b5f...d5b`, defines direction `+1` as a buy limit order and `-1` as a
sell limit order. It also states that executing a sell limit is buyer initiated and executing a buy limit is
seller initiated. Every type-1--5 message is mapped exactly once to:

| Mark | Vendor rule |
|---|---|
| `bid_add` | type 1, direction `+1` |
| `ask_add` | type 1, direction `-1` |
| `bid_cancel` | type 2 or 3, direction `+1` |
| `ask_cancel` | type 2 or 3, direction `-1` |
| `aggressive_buy` | type 4 or 5, executed-limit direction `-1` |
| `aggressive_sell` | type 4 or 5, executed-limit direction `+1` |

Type 7 would hard fail this frozen sample manifest rather than be silently fitted. The external direction is a
real schema anchor for these marks; it does not orient an arbitrary EcoMD latent coordinate.

## Frozen timestamp policies

Both policies preserve raw vendor row order and leave every originally distinct timestamp unchanged.

1. **Primary `nextafter`:** inside each equal-time group, keep the first time and replace each later time by the
   next representable float after its adjusted predecessor. Hard fail if the adjusted group reaches the next
   distinct raw timestamp.
2. **Sensitivity `capped_uniform`:** for a group of size `m` at time `t`, use ordered offsets
   `k * min(1e-9, (t_next-t)/(m+1))`; the terminal group uses `1e-9`. If float rounding is not strict, advance by
   `nextafter`. Hard fail on crossing.

The adjusted time must be strictly increasing; raw-to-adjusted displacement, tie count, largest group and
minimum positive interval are reported. The primary and sensitivity policies are fitted independently. No
random jitter is allowed.

## Frozen split, scaling and no-lookahead queue features

- Split each stream by absolute row order: first 10% burn/history only, next 50% train, final 40% held out.
- Every likelihood interval ending at event `i` uses only the L1 book after event `i-1`. The LOBSTER book row
  after event `i` is forbidden as a predictor of event `i`.
- Normalize time by the train-only mean event rate. Fixed normalized inverse timescales are
  `beta=(0.1, 1.0, 10.0)`; they are not selected per symbol.
- Queue-state features are L1 imbalance, `log((bid_size+1)/(ask_size+1))`, `log1p(total best depth)` and
  `log(max(spread,1))`.
- Clock features are sine and cosine of position in the archive's declared window. Non-intercept features use
  train-only means/scales; near-zero train scale hard fails.
- The shifted-queue control circularly shifts only the four queue-state feature sequences by
  `floor(split_length/3)` separately inside train and test. Clock features remain aligned. This preserves queue
  marginals and temporal ordering while destroying contemporaneous pairing; it is deterministic and uses no
  seed search.

## Frozen likelihoods and models

For mark `k`, the normalized-time linear Hawkes intensity is

`lambda_k(t) = mu_k + sum_{j,r} alpha[k,j,r] * h[j,r](t)`,

where `h[j,r](t)=sum_{i<t, mark_i=j} beta_r*exp(-beta_r*(t-t_i))`. Coefficients are nonnegative, so the
compensator is analytic. Queue-reactive baseline intensity is piecewise constant between messages,
`exp(theta_k^T q_i)`. The combined intensity is

`lambda_k(t) = exp(theta_k^T q_i) + sum_{j,r} alpha[k,j,r] * h[j,r](t)`.

Thus both the event log intensity and the full interval compensator are continuous-time quantities; this is not
the discrete marked-Hawkes-logit proxy used in exp137.

Fit six deterministic models on identical train/test events:

- `poisson`: constant mark intensities;
- `queue_reactive`: aligned piecewise-constant queue/clock baseline;
- `hawkes_diagonal`: three timescales, same-mark excitation only;
- `hawkes_full`: all six source marks and three timescales;
- `queue_hawkes_full`: aligned queue/clock baseline plus full Hawkes excitation;
- `queue_hawkes_shifted`: identical combined model with only queue-state features circularly shifted.

Use analytic gradients and SciPy L-BFGS-B on negative log likelihood divided by training-event count, maximum
300 iterations, `ftol=1e-10`, `gtol=1e-6`, maximum 40 line-search steps and intensity floor `1e-12` only for
numeric validation. Hawkes coefficients have lower bound zero; queue coefficients are unbounded. Combined fits
use two frozen starts, the fitted queue model with zero excitation and the fitted Hawkes model with constant
queue baseline; retain the higher **training** likelihood. No regularization, hyperparameter search or test-set
model selection is allowed.

Report train and held-out log likelihood in nats/event; all pairwise comparisons use the same adjusted-time
policy and events. Also report coefficient matrices, optimizer status/gradient, branching spectral radius,
per-mark counts, intensities and total-intensity time-rescaling residual mean, variance, exponential KS
statistic and lag-1 correlation. Real-data calibration diagnostics are descriptive, not a pass threshold.

## Frozen generated control

Eight independent two-mark stationary exponential-Hawkes streams use root seed `138_202_608`. Poisson
immigrants start at time -1,000, offspring are generated recursively through time 30,000, and only events in
`[0,30000]` are retained. The decay is 1.3, immigrant rates are `(0.35,0.25)`, and the branching matrix is
`[[0.22,0.08],[0.06,0.18]]`. Simulation uses the Poisson-cluster representation and the same 10/50/40 split.
Fit Poisson and correctly specified full Hawkes with fixed decay 1.3.

Generated-control thresholds are frozen before simulation:

- all 8 fits finite and converged;
- median relative error of each immigrant rate at most 15%;
- median relative error of each nonzero branching coefficient at most 25%;
- median held-out Hawkes-minus-Poisson gain at least 0.005 nats/event;
- median held-out total-intensity rescaling mean in `[0.90,1.10]`, KS statistic at most 0.05 and absolute lag-1
  correlation at most 0.05.

This control validates likelihood/compensator plumbing. It cannot validate the market model.

## Frozen execution and merge

- Formal work has two CPU-only shards at one process and one BLAS thread each, CUDA hidden.
- Shard 0 owns GOOG, SPY and generated replicates 0/2/4/6; shard 1 owns AAPL, AMZN, MSFT and replicates
  1/3/5/7. The split balances message counts; node identity never changes data or seeds.
- Each shard records protocol hash, implementation git SHA, dirty flag, archive hashes, environment, thread
  settings and complete results. Formal execution requires an exact clean implementation commit.
- The merger hard fails on missing/duplicate streams or controls, wrong shard ownership, protocol mismatch,
  dirty tree, wrong SHA, changed hashes, CUDA visibility or non-frozen thread settings.
- Expected total is below 20 CPU core-hours and 8 GiB RAM per worker. Pilot outputs use separate paths and may
  test execution only; no target threshold may change after any fit is inspected.

## Frozen hard gates

1. Exact manifest/provenance/ReadMe hashes, 5 canonical streams, 2,641,557 rows and declared raw-time metadata.
2. All raw times nondecreasing; both deterministic policies strictly increase without crossing and preserve row
   order; all type-1--5 messages map exactly once to a frozen mark.
3. Train/test counts and feature normalizers are exact; every queue feature for event `i` comes from book row
   `i-1`; no after-event or future-split state enters a fit.
4. The eight generated controls pass every recovery, likelihood and time-rescaling threshold above.
5. Every real-data model/tie-policy cell is finite and reports optimizer diagnostics. Failed optimizer success
   may pass only if the final infinity-norm gradient is at most `1e-5` and all nesting checks pass.
6. On training data, `hawkes_full` is no worse than `hawkes_diagonal` or `poisson`, `queue_reactive` is no worse
   than `poisson`, and `queue_hawkes_full` is no worse than both `hawkes_full` and `queue_reactive`, within
   `1e-7` nats/event. This is a deterministic optimization/nesting check, not empirical evidence.
7. Under both tie policies, the cross-symbol median held-out
   `queue_hawkes_full - queue_hawkes_shifted` is nonnegative. Per-symbol signs and magnitudes are reported; no
   symbol may be dropped.
8. Tie robustness: the cross-symbol median held-out `queue_hawkes_full - hawkes_full` has the same sign under
   both policies, and the two medians differ by at most 0.002 nats/event.
9. All held-out model comparisons, branching radii and time-rescaling diagnostics are reported even if they are
   unfavorable. No real-data winner threshold beyond controls 7--8 is introduced post hoc.

All nine gates are required for PASS. A failed real control remains a result; v2 would require a new protocol,
new commit and independent data rather than a relaxed threshold.

## Interpretation and next gate

A PASS permits this continuous-time baseline family and external sign/timestamp parser to enter a later G3
comparison. G3 still requires a frozen EcoMD-to-message mapping trained without the real test split, a real
latent-vs-observation-only comparison, more than one market day and an external replication. A FAIL blocks
model-to-real language and paid data; it does not justify reverting to the weaker discrete proxy.

Method references fixed for this protocol: Hawkes, *Biometrika* 58 (1971), 83--90,
doi:`10.1093/biomet/58.1.83`; Ogata, *JASA* 83 (1988), 9--27,
doi:`10.1080/01621459.1988.10478560`; Wu, Rambaldi, Muzy and Bacry, “Queue-reactive Hawkes models for the order
flow,” arXiv:`1901.08938`; Martins and Hendricks, “The statistical significance of multivariate Hawkes processes
fitted to limit order book data,” arXiv:`1604.01824`.
