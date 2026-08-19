# dYdX fixed-funding-carry D0 result — 2026-08-20

## Decision

**D0 PASS, with a binding low-activity warning.** All frozen metadata and governance gates passed. This result
authorizes a separately frozen pre-period activity screen; it does not authorize a causal claim or bulk trade
analysis.

The first run stopped on one 30-second read timeout and wrote no partial result. After the fixed transport-only
retry amendment was committed and pushed, the clean run completed from git commit `ddb729525` and wrote the
sanitized manifest `results/empirical_physics/dydx_funding_carry_d0_result.json` with canonical SHA-256
`777d502612b91375ea9fb4207e407300d362d8b11b492fc21a35cdb5a931ddfc`.

## Passed gates

- The public Cosmos endpoint returned 391 proposals and 256 passed perpetual-parameter messages. All 21
  development transitions revalidated as a singleton `default_funding_ppm: 100 -> 0` payload change.
- All 21 markets returned non-empty historical trade, one-minute candle and historical-funding responses at the
  frozen 2025 heights.
- Every fixed one-hour candle probe returned 60 distinct one-minute rows with the required schema.
- Trade responses expose `id`, `side`, `size`, `price`, `type`, `createdAt` and `createdAtHeight`; candle and
  funding schemas also match the official implementation.
- Two five-row pages for each of the frozen `BEAM-USD`, `ENA-USD` and `PAXG-USD` probes have offsets 0/5 and
  zero identity overlap.
- Raw responses were never written. The manifest retains only schema, types, counts, timestamps, heights and
  hashes; it contains no price, size, side, funding-rate, OHLC, volume, OI or midpoint value.

The clean run used CPU and free unauthenticated endpoints only. No V100, RTX2060, H20, paid data or EcoMD was
used.

## Low-activity warning

The D0 post cursor is a fixed 20,000 blocks after execution, roughly several hours. For eight markets—`2Z`,
`ATH`, `BEAM`, `BERA`, `DRIFT`, `KAITO`, `PAXG` and `S`—the latest returned trade was unchanged between the
pre-execution and post-cursor probes. Several last-trade timestamps were already many hours old.

This does not violate the frozen D0 gate, which tests whether public history and schemas exist. It does imply a
material risk that the frozen activity rule—at least 100 trades on at least 21 of the 28 pre-event days—will
exclude enough markets to destroy the intended stacked design. D0 counts cannot answer that question and must
not be spun as evidence for or against the mechanism.

## Next gate

Before any bulk tick acquisition, D1A should request only the 28 full pre-event UTC days of `1DAY` candles for
the 21 development markets and apply the already-frozen activity/completeness rule without adjustment. Daily
`trades` counts are sufficient for this eligibility calculation and require only 21 small requests.

The D1A stop rule should be fixed before those values are opened:

- 20 or 21 eligible development markets: proceed with the planned multi-wave tick pilot;
- 15--19: AMBER; redesign power and confirmation logic without changing the activity threshold, then decide
  before tick outcomes;
- fewer than 15: stop the dYdX-only causal paper before bulk acquisition.

Proposal 317 and the proposal-220 outcome window remain sealed during D1A. No GPU is authorized.
