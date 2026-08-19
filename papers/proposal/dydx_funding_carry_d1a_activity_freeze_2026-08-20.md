# dYdX fixed-funding-carry D1A activity freeze — 2026-08-20

## Purpose

D0 passed public-history and schema checks but showed that eight development markets had no new trade by a
fixed several-hour post cursor. D1A is therefore a cheap earning-or-kill gate before bulk tick acquisition. It
applies the activity rule already frozen at T0; it does not estimate a treatment response.

This document is frozen before opening any daily `trades` value.

## Data lock

For each of the 21 proposal-314--316 development markets, request exactly the 28 full UTC days immediately before
its execution date from the public `1DAY` candle endpoint. Retain only `startedAt` and the daily `trades` count,
plus response hashes and schema metadata. Do not retain OHLC, volume, open interest or midpoint fields. Do not
request post-event candles, individual trades, proposal-317 data or the proposal-220 outcome window.

The two frozen windows are 17 October through 13 November 2025 for proposal 314 and 19 October through 15
November 2025 for proposals 315--316. No date may be moved after values are read.

## Eligibility and decision

A market is activity-eligible only if all 28 daily candles are present and at least 21 days have at least 100
trades. The 100/21 threshold is inherited from T0 and cannot be relaxed.

- 20--21 eligible markets: D1A passes; separately freeze D1B tick acquisition and the development-wave
  estimator.
- 15--19: AMBER; do not acquire ticks until power and confirmation logic are redesigned without changing the
  activity threshold.
- fewer than 15: stop the dYdX-only causal paper before bulk ticks. Proposal 317 cannot be opened to rescue the
  gate.

D1A is 21 unauthenticated requests, below one CPU core-hour and 50 MB. GPU, paid data and EcoMD are forbidden.
