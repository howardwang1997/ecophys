# Experiment 130 — free LOBSTER L2 observation-bridge smoke

**Frozen:** 2026-08-09, before summary statistics were computed  
**Status:** schema/reconstruction feasibility only  
**Resources:** eight already-present free LOBSTER sample ZIPs; CPU only; no purchase

## Purpose

Test whether the repository's free samples are sufficient to define and validate a real order-book observation
operator before purchasing any L2 history. This is not an EcoMD calibration experiment and cannot establish
out-of-sample market fidelity.

## Frozen sample and memory bound

- Process every ZIP under `data/sample/LOBSTER/`.
- Stream at most the first 200,000 events per archive in chunks of 50,000.
- Do not fully materialize L50 CSVs; the SPY L50 orderbook alone is about 1.45 GB uncompressed.
- Record SHA256, archive byte size, symbol, level, rows processed and whether the cap was reached.

## Checks

1. message and book chunks have equal rows and timestamps are nondecreasing;
2. best ask is above best bid, ask levels are nondecreasing, bid levels nonincreasing, sizes nonnegative;
3. for visible event types 1--4, reconstruct size change at the message's exact price on the indicated side;
4. for hidden executions (type 5), measure whether displayed L2 stays unchanged;
5. compute Cont--Kukanov--Stoikov L1 OFI from consecutive books;
6. report OFI correlation with a message-signed displayed-flow proxy and with mid-price change.

For item 3, an event is `visible` only when its message price occurs in the pre- or post-event retained depth.
Exact reconstruction requires observed queue delta `+size` for additions and `-size` for cancel/delete/visible
execution. Events outside the retained depth are excluded from the exact-rate denominator, not counted as
failures.

## Feasibility thresholds

- all archives pass ZIP integrity and row alignment;
- crossed/locked top-of-book rate `< 1e-4`;
- level ordering and nonnegative-size violation rates `< 1e-6`;
- visible event reconstruction exact rate `>= 0.99` for event types 1--4 pooled;
- hidden executions leave displayed depth unchanged in `>= 0.99` of sampled cases.

Failure means either the implementation/convention is wrong or the proposed observation operator is not yet
validated. No model-to-real OFI language is allowed until the discrepancy is resolved.

