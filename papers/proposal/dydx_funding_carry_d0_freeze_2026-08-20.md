# dYdX fixed-funding-carry D0 freeze — 2026-08-20

## Lock point and purpose

This protocol is frozen after T0 passed and before the first dYdX Indexer response row is requested. D0 asks
only whether free public history can support the already-frozen design. It cannot estimate, visualize or reveal
the signed dipole or any secondary outcome.

The development scope is proposals 314--316 and their 21 clean markets. Proposal 317 remains sealed as
confirmation. The March proposal-220 outcome window remains sealed until the reverse estimator and confirmation
decision are immutable.

## Permitted retained information

D0 may retain endpoint status, response byte count and SHA-256, top-level and row field names, scalar data types,
row counts, duplicate counts, timestamps, block heights and pagination metadata. It may transiently parse a row
to make those summaries. It must not write raw responses or retain price, size, side, trade type, funding rate,
oracle price, OHLC, volume, trade-count, open-interest or midpoint values.

The code enforces this by reducing each response to a no-values manifest in memory. Tests insert recognizable
fake outcomes and require that none appears in serialized output.

Transport failures use three fixed idempotent-GET retries with exponential backoff. This policy cannot alter a
market, event window, endpoint, row limit or scientific gate. A failed attempt writes no partial manifest.

## Frozen probes

For every development market, D0 requests:

- the last trade at or before the executing height and the last trade at a fixed later-height cursor;
- one-minute candle coverage for a fixed 30-minute interval on each side of execution; and
- the last historical funding record at or before the executing height.

`BEAM-USD`, `ENA-USD` and `PAXG-USD` are fixed pagination probes for waves 314, 315 and 316. Two five-row trade
pages must be non-empty and non-overlapping. These tickers cannot be replaced after the probe is run.

The source-code semantics are frozen as part of D0: the official trades controller filters the fill table to
`Liquidity.TAKER`, maps that taker fill's `side` into the public response and supports explicit `page`. Thus the
primary outcome uses taker direction; it is not inferred from price changes.

## Gate

D0 passes only if all 21 governance transitions revalidate, every fixed endpoint probe is non-empty, every
required schema field is present, the three pagination checks do not overlap and the manifest contains no
market outcome value. Failure stops the empirical branch before bulk acquisition. A sparse activity result may
exclude markets under the already-frozen pre-period rule, but the activity threshold cannot be changed.

Passing D0 does not authorize analysis. The next step would be a separate, committed D1 acquisition and analysis
freeze covering only proposals 314--316. CPU remains sufficient; V100, RTX2060, H20, paid data and EcoMD remain
forbidden.
