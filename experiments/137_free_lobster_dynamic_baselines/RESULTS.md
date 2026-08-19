# Experiment 137 results — free LOBSTER dynamic observation baselines

**Run date:** 2026-08-19
**Frozen protocol commit:** `b9fe0569d`
**Final execution commit:** `5fa745ef4`
**Decision:** feasibility PASS (5/5 baseline-relevance paths); G3 remains open

## Frozen gates

All five independent symbols completed with finite scores and the declared model/depth/latency variants.
Displayed books were ordered, nonnegative, non-crossed and timestamp-monotone. Exact dynamic price-level queue
reconstruction passed on 927,811/927,811 visible type 1--4 events. Every symbol exceeded the frozen 0.01
nats/event observation-baseline gain threshold, so the global requirement of at least four symbols passed 5/5.

| Symbol | Eligible transitions | Unconditional NLL | Combined NLL | Combined gain | Markov gain | History gain | L10 queue gain | Delay-5 gain | Delay-20 gain |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| AAPL | 199,999 | 1.7198 | 1.5291 | 0.1908 | 0.1598 | 0.1193 | 0.0281 | 0.0528 | 0.0231 |
| AMZN | 199,999 | 1.6243 | 1.5247 | 0.0996 | 0.0781 | 0.0776 | 0.0067 | 0.0424 | 0.0184 |
| GOOG | 147,915 | 1.8494 | 1.5784 | 0.2710 | 0.2363 | 0.1848 | 0.0644 | 0.0797 | 0.0221 |
| MSFT | 199,999 | 1.5768 | 1.2657 | 0.3111 | 0.2367 | 0.1944 | 0.0767 | 0.1806 | 0.1133 |
| SPY | 199,999 | 1.4201 | 1.1058 | 0.3143 | 0.2772 | 0.1736 | 0.0652 | 0.1517 | 0.1236 |

NLL and gains are nats per held-out event. The median combined gain was 0.2710, versus 0.2363 for first-order
Markov, 0.1736 for the Hawkes-style history feature model and 0.0644 for the L10 queue-only model. Combined was
the strongest declared baseline on every symbol.

## Latency and censoring findings

The combined model's median gain fell from 0.2710 with current features to 0.0797 when features were stale by
five events and 0.0231 when stale by twenty. The direction was consistent, but the remaining positive gain
shows that slow event-state persistence is a strong control. A later EcoMD result cannot claim mechanism value
merely by exploiting that persistence.

Queue depth was not monotonically helpful. For example, SPY's L5 queue-only model was worse than its
unconditional null even though L10 was positive. This is evidence against selecting depth after seeing the
test score; future depths and censoring rules must stay pre-registered.

## Reproducibility and execution history

- All five canonical paths ran on the RTX2060 in the `ecophys-g0-regression` Conda environment. Independent
  Mac `ecophys` CPU replications were retained for AAPL, MSFT and SPY while both V100 SSH paths were unavailable.
- All three CPU/CUDA pairs cleared the frozen gain gate. Absolute held-out combined-NLL differences were
  0.0055, 0.0021 and 0.0164 nats/event for AAPL, MSFT and SPY, respectively. The gate is robust to device, but
  the fits are not bitwise cross-device replicas.
- GOOG was rerun after the shard-invariant seed fix and again after adding single-archive scheduling. The two
  correct-seed CUDA artifacts have exactly identical audit and model dictionaries. The pre-fix artifact is
  retained as `NONCANONICAL_GOOG_PRE_SEED_FIX.json` and excluded from aggregation.
- All eight repository-held sample archives were copied to private R2 under
  `free/lobster_samples/2012-06-21/`; inputs in canonical results retain their original SHA256.

## Interpretation boundary and next gate

This result establishes that real dynamic price/queue semantics, chronological scoring, observation-only
controls and latency/depth stress can be executed without purchasing data. It is not evidence that EcoMD beats
these controls: EcoMD was not fit or scored. All samples are one market day, four individual stocks plus one
ETF, and the repeated date is not five independent regimes.

G3 therefore remains open. Before a paid-data decision, implement a proper continuous-time Hawkes or
queue-reactive point-process likelihood and use the same evaluator for EcoMD, observation-only and empirical
resampling paths. Tardis/other multi-day crypto L2 and multi-day US-equity L2 remain necessary for temporal and
cross-domain holdouts after G2; no crash/test event was opened here.
