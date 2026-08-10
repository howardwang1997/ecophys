# Experiment 143 — aggregate-bin P3 reconstruction and train-only measurement gate

**Frozen:** 2026-08-10, after exp142 formally passed and before any aggregate-bin module, fixture, pilot,
formal seed, fitted coefficient or target result exists

**Status:** narrow F1 implementation gate for `aggregate_bin` + P3 only

**Cost boundary:** generated data only; Mac CPU in the `ecophys` Conda environment; no real archive, exposed or
unseen test data, fitting to a market, GPU, purchase, H20 or compute expansion

## Question and claim boundary

Can EcoMD transition summaries be connected to an externally meaningful **fixed-time-bin** object without
inventing message/order semantics, while preserving half-open physical-time bins, exact aggregate counts and
share volume, train-only measurement fitting, required sign/observation-only controls and the latent-scale
identifiability warning?

A PASS closes only the synthetic implementation part of F1 for unconditional `aggregate_bin` + P3. It does not
show that EcoMD improves prediction on real data, identify latent agents or physical volume, validate the
current event adapter, pass F0/F2/F4, or support market-physics language. The current `EcoMDL2Adapter` remains
`synthetic_fixture`; exp143 must not call or reinterpret it.

## Frozen observation object and clock

The external aggregate-bin object has:

- half-open bins `[start + j*Delta, start + (j+1)*Delta)`, with `Delta=60.0` seconds;
- bin start/end seconds and a declared market size unit of `shares` or `contracts`;
- close-to-close log mid return, with the supplied pre-window mid as the first reference and forward-filled mid
  across an empty bin;
- executed volume equal to the integer size sum for event types 4 and 5 only;
- six integer mark counts in the frozen exp138 order
  `(bid_add, ask_add, bid_cancel, ask_cancel, aggressive_buy, aggressive_sell)`;
- no `order_id`, queue priority, individual-order lifecycle or exact event-time likelihood.

Input rows contain nondecreasing seconds, event type 1--5, positive integer size, direction `{-1,+1}` and a
positive after-event midpoint. Equal timestamps retain input row order. An event at the right endpoint is out
of scope and must be rejected, not clipped into the final bin. NaN/Inf, decreasing time, nonpositive midpoint,
invalid size/type/direction or a non-integral number of bins hard fails.

## Frozen hand-computable fixture

Aggregate 11 rows over six 60-second bins `[0,360)` from initial midpoint 100. The rows are:

| time | type | direction | size | midpoint after row |
|---:|---:|---:|---:|---:|
| 0 | 1 | +1 | 10 | 100 |
| 15 | 1 | -1 | 12 | 100 |
| 59.5 | 4 | -1 | 7 | 101 |
| 60 | 2 | +1 | 3 | 101 |
| 60 | 5 | +1 | 5 | 100 |
| 119.999 | 3 | -1 | 4 | 100 |
| 180 | 4 | +1 | 9 | 99 |
| 239.999 | 1 | +1 | 11 | 99 |
| 240 | 5 | -1 | 6 | 100 |
| 300 | 2 | -1 | 2 | 100 |
| 359.999 | 1 | -1 | 8 | 102 |

Expected closes are `(101,100,100,99,100,102)`, executed volumes are `(7,5,0,9,6,0)`, and mark-count rows
are:

```text
(1,1,0,0,1,0)
(0,0,1,1,0,1)
(0,0,0,0,0,0)
(1,0,0,0,0,1)
(0,0,0,0,1,0)
(0,1,0,1,0,0)
```

Returns are exactly `log(close[j]/previous_close)` up to float64 error `2e-15`. Batch, chunks
`(1,3,1,4,2)` and a serialize/restore immediately after the first row at time 60 must agree bit-for-bit in
integer fields and within `2e-15` in returns/mids. This split deliberately crosses an equal-time group.

## Frozen generated bin process

Use root seed `143202608` and `numpy.random.SeedSequence(root).spawn(...)`; smoke uses separate root
`143202609`. Generate 4,096 bins and freeze the first 60% (`train_end=2457`) as training. Generate independent
stationary unit-variance AR(1) paths using their analytic initial law:

- return predictor `x_r = 0.01 * AR1(rho=0.30)`;
- log-volume predictor `x_v = 3.5 + 0.35 * AR1(rho=0.55)` and latent volume `expm1(x_v)` in model units;
- directional predictor `z = tanh(0.9 * AR1(rho=0.40))`.

Generate aggregate observations with independent noises:

- `y_r = 0.0001 + 1.25*x_r + Normal(0,0.004)`;
- provisional share volume `round(expm1(0.65 + 0.82*x_v + Normal(0,0.12)))`;
- total marks `K = 12 + Poisson(exp(2.6 + 0.20*(x_v-3.5)))`;
- positive-pressure marks `P ~ Binomial(K, sigmoid(-0.15 + 1.70*z))`.

Distribute `P` across marks `(bid_add, ask_cancel, aggressive_buy)` with probabilities `(0.40,0.30,0.30)`
and `K-P` across `(ask_add, bid_cancel, aggressive_sell)` with the same probabilities. If a bin has no
execution mark, move one same-sign add/cancel count to its execution category without changing `P` or `K`.
Set share volume to at least the execution count, then allocate it as positive integer sizes across execution
rows. Nonexecution sizes are one. Within-bin marks are deterministically shuffled; times are ordered inside the
bin with deterministic equal-time pairs, and the last row carries the new midpoint. Starting midpoint is 100.

The formal runner reconstructs its bin object from these generated raw rows. It may not consume the directly
generated aggregate response except as an independent reference. Mark counts and executed volume must match
exactly; close/return maximum absolute error must be `<=5e-13`.

## Frozen state and chunk/resume test

The streaming accumulator state contains all partial counts/volume, current and pre-window mid, last raw time,
next unfinalized bin and the clock/unit configuration. It must have a versioned JSON-safe checkpoint.

Compare monolithic aggregation to deterministic raw-row chunk lengths cycling through
`(1,997,37,4096,13,251)` and one checkpoint/restore after 10,003 rows. All integer fields, timestamps and
terminal state must be bit-exact; close/return arrays must be bit-exact because both paths use the same ordered
last-mid updates. A chunk boundary may split equal timestamps. Finalization is permitted exactly once; input
after finalization hard fails.

## Frozen P3 measurement fits

Fit each link only on bin indices `1:train_end`; index zero is dropped so every observation-only feature is a
strict lag. Three designs are fitted with an intercept:

- `latent`: current `(x_r, x_v, z)` for the matching channel;
- `observation_only`: previous observed return, previous `log1p(executed_volume)`, or previous signed mark
  fraction;
- `combined`: current latent predictor plus the same previous observed feature.

Return and log-volume links use float64 least squares and train-residual Gaussian scale. Direction uses grouped
binomial Newton updates on positive versus total mark counts; all counts remain aggregated. Report every
coefficient, scale, convergence flag and held-out metric. The latent-only generating targets are return
`(intercept=0.0001, slope=1.25, sigma=0.004)`, log-volume `(0.65,0.82,0.12)`, and directional logit
`(-0.15,1.70)`.

Frozen recovery thresholds:

- return intercept absolute error `<=5e-4`, slope relative error `<=5%`, sigma relative error `<=10%`;
- log-volume intercept absolute error `<=0.08`, slope relative error `<=5%`, sigma relative error `<=15%`;
- directional intercept absolute error `<=0.08`, slope relative error `<=5%`;
- all fits finite; grouped-binomial fits converge within 100 Newton iterations.

Frozen held-out controls:

- latent return RMSE `<=0.60` times observation-only RMSE;
- latent log-volume RMSE `<=0.65` times observation-only RMSE;
- latent directional held-out log likelihood exceeds observation-only by at least `0.02` nats/event;
- combined return/volume RMSE is at most `1.02` times the corresponding latent RMSE, and combined directional
  likelihood is no worse than latent by more than `0.002` nats/event;
- scoring the fitted latent directional model on `-z` without refitting loses at least `0.05` held-out
  nats/event versus anchored `z`.

These self-generated recovery thresholds validate plumbing only and cannot be reported as market performance.

## Frozen train-only and identifiability controls

1. Replace every held-out return by `return+10`, every held-out volume by `volume+1_000_000_000`, and swap
   positive/negative mark groups. Every fitted parameter, scale and training-prefix hash must remain bit-exact.
2. Perturb one training row in all three channels. The fit hash must change; a fit that ignores observations
   therefore fails.
3. The fit object records the exact training-prefix SHA-256, `train_end=2457`, `test_start=2457`, and warning
   `COEFFICIENTS_CONDITIONAL_ON_FROZEN_LATENT_SCALE`.
4. Rescale a latent predictor by exactly seven and divide its slope by seven. Predictions must agree within
   `1e-12`. This is a required demonstration of the latent-scale gauge, not an identified physical unit.

No fit API accepts a test-selected boundary or arbitrary row mask. No threshold or model may be chosen using
held-out outcomes.

## Frozen hard gates

1. **Chronology/provenance:** preregistration precedes implementation; clean formal SHA, protocol hash, fixed
   root ownership, Conda/package versions and one-thread settings are recorded.
2. **Schema/units/clock:** valid rows/config pass; every frozen invalid time, boundary, unit, size, midpoint,
   mark and finalized-state case is rejected.
3. **Hand fixture:** all six bins, empty-bin carry, boundary placement, tie order, counts, volume, closes and
   returns match the frozen values under batch/chunk/checkpoint execution.
4. **Generated reconstruction:** 4,096 independently generated reference bins reconstruct with exact integer
   counts/volume and maximum close/return error `<=5e-13`.
5. **State completeness:** monolithic/chunked/checkpoint outputs and terminal states meet the exact parity rule;
   post-finalization input fails.
6. **Train-only firewall:** held-out corruption leaves the fit byte-identical; training corruption changes its
   hash; recorded split and prefix hash are exact.
7. **Parameter recovery:** every frozen coefficient/scale/convergence threshold passes.
8. **Negative controls:** every observation-only, combined and sign-flip threshold passes with all unfavorable
   per-channel values reported.
9. **Identifiability:** the scale-gauge identity passes and the exact warning is serialized; no physical latent
   volume or recovered-agent claim appears.
10. **Code quality and complete reporting:** focused pytest, Ruff and strict mypy pass; all raw-generation
    summaries, splits, fits, controls, mutations, hashes, runtime and peak RSS are archived in
    `AGGREGATE_BIN_RESULTS.json` and `RESULTS.md`.

All ten gates are required. A formal failure is retained; thresholds or seeds cannot be changed after output is
inspected. Smoke may expose code defects using only root `143202609`, never the formal descendants.

## Execution and next decision

Run one CPU process via
`conda run -n ecophys python experiments/143_aggregate_bin_p3/run_aggregate_bin.py`. Expected cost is under two
CPU core-hours and 2 GiB RAM.

A PASS marks the **synthetic implementation** of F1 as PASS for aggregate-bin P3 only, leaving external evidence
to F4 and leaving event/order support FAIL. The next action is F0 prior-art closure before any E-B defect
screening. A FAIL blocks the observation bridge and sends the project directly toward the narrower EcoMD
correctness/software release until a new versioned protocol is frozen.
