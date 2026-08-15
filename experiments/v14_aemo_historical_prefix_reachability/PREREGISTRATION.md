# AEMO historical ZIP-prefix reachability audit

**State at freeze:** network-unexecuted. No new request to either selected object and no market row from either
month has been opened under this protocol.

**Scientific role:** development-only feasibility test. It asks whether one complete historical market day can be
reached in chronological order from a fixed prefix of the pre- and post-5MS monthly period-offer archives. It does
not test cross-table joins, participant action semantics, an intervention effect or a model.

## Why this gate comes next

The modern set-valued observation bridge passed on six Tuesdays, and the historical source/header matrix passed
on two pre/post month pairs. The remaining historical obstacle is operational: the 2021-12 `BIDPEROFFER` archive
is 1,610,349,080 compressed bytes. Downloading the whole object before establishing row order and day reachability
would be disproportionate.

AEMO's rolling daily-report archive retains only about thirteen months and therefore cannot recover a 2021 daily
`BIDMOVE_COMPLETE`/`NEXT_DAY_DISPATCH` pair. The official monthly table archives remain the authoritative free
source for the 2021 boundary. This audit tests a bounded streaming route into those archives.

## Frozen samples

The audit deliberately reuses the already consumed, header-only development months `2021-01` and `2021-12`.
They cannot become confirmation samples. Reusing them protects untouched months for a later row-bridge test.

| Regime | Object | Declared archive bytes | Fixed response |
|---|---|---:|---:|
| A0/O0, legacy 30-minute | `PUBLIC_DVD_BIDPEROFFER_202101010000.zip` | 95,238,254 | 67,108,864 |
| A3/O4, 5MS + WDR/v5.1 | `PUBLIC_DVD_BIDPEROFFER_202112010000.zip` | 1,610,349,080 | 67,108,864 |

Each object receives exactly one `Range: bytes=0-67108863` request. No retry, replacement, extension or full-file
fallback is allowed. Exact response bytes are stored opaquely and verified in R2 before the first ZIP member or
CSV row is opened. Raw prefix bodies are not committed to Git.

## Parsing contract

After retention, the analyzer streams raw deflate output with a 1 GiB uncompressed cap per object. It requires the
already confirmed source headers:

- January: `OFFER,BIDPEROFFER,1`, market-day field `SETTLEMENTDATE`;
- December: `BIDS,BIDOFFERPERIOD,1`, market-day field `TRADINGDATE`.

Rows must parse without malformed records or timestamp loss, begin on the first day of the declared month, remain
non-decreasing by market day and reach a second distinct market day. Reaching the second day makes the first day a
complete prefix block and yields a conservative compressed-byte upper bound for a later one-day extraction.

## Immutable decision

`PASS_HISTORICAL_PREFIX_REACHABILITY` requires both objects to pass every transport, R2, header, date, ordering,
completeness and partial-archive gate. Any failure is preserved. The same responses are not extended and the
months are not replaced after observing their rows.

A pass authorizes only a new, separately frozen historical row-bridge protocol on untouched months. That later
protocol must include all five logical roles, version-specific keys, applied-offer linkage, identity intervals and
the set-valued observation rule where `DIRECTION` exists. A failure sends the source design back to archive/query
selection; it does not authorize a bulk download.

CPU and existing R2 are sufficient. GPU hours, paid-data spend, remote worker requirements and target-event use
are all zero. Experiment 156 and every model claim remain locked.
