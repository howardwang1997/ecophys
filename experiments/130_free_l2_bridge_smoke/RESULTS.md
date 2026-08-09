# Experiment 130 results — free LOBSTER observation bridge

**Run date:** 2026-08-09  
**Artifact:** `L2_SMOKE_RESULTS.json`  
**Decision:** schema/reconstruction smoke PASS; G3 observation bridge remains open

## Coverage and resource use

- 8/8 local free-sample ZIPs passed CRC and were processed.
- 1,381,420 message/book rows were streamed; files shorter than 200,000 rows were consumed fully, others hit
  the preregistered cap.
- Symbols/depths: AAPL L10/L50, AMZN L10, GOOG L10, MSFT L1/L10/L50, SPY L50.
- Wall time was about 25.1 seconds. Peak RSS reported by macOS was about 1.18 GB; the script never materialized
  an entire L50 CSV.

## Frozen hard gates

| Check | Result |
|---|---:|
| timestamp-order violations | 0 |
| crossed/locked top-of-book rows | 0 |
| ask/bid level-order violations | 0 |
| negative displayed-size cells | 0 |
| exact visible reconstruction, event types 1--4 | 100% in every archive |
| hidden executions leaving displayed book unchanged | 100% in every archive |

All preregistered smoke thresholds passed.

The L1 Cont--Kukanov--Stoikov OFI was mechanically distinct from a simple signed message-size proxy except in
the MSFT L1 file, where retaining only one level makes them coincide. Across the other samples their correlation
ranged from about 0.384 to 0.779. OFI--mid-price-change correlation ranged from about 0.064 to 0.379. This is a
useful warning against equating EcoMD's current latent alignment statistic with real OFI.

## What this establishes

The free samples are sufficient to implement and unit-check a message-to-visible-L2 observation operator,
including exact queue deltas and a standard L1 OFI series. They are also sufficient for synthetic-recovery code
smokes and basic event-emission schema tests.

## What this does not establish

- All files are from one date, and the L50 samples cover only one hour; there is no temporal or regime coverage.
- Exact reconstruction validates parsing conventions, not an EcoMD emission model.
- No latent-to-L2 identifiability, parameter recovery, likelihood, calibration or held-out prediction was tested.
- These one-day samples cannot support G3/G4, universal market claims or a paid-data purchasing decision by
  themselves.

The next free step is a synthetic queue-emission/recovery benchmark. Paid multi-day L2 remains gated until that
benchmark identifies which fields and sampling frequency are actually necessary.
