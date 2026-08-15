# AEMO historical ZIP-prefix reachability result

**Decision:** `FAIL_HISTORICAL_PREFIX_REACHABILITY`

**Frozen protocol commit:** `d7dd5af5bc3b654a46da37364d118f98e408f067`

## Provenance

Both fixed range requests returned HTTP 206 and exactly 67,108,864 bytes. Their declared total sizes matched the
frozen 95,238,254-byte January and 1,610,349,080-byte December archives. The prefixes were uploaded and verified
in R2 before the first ZIP member or CSV row was opened. No request was retried, extended or replaced.

Artifact SHA-256 values are:

- download receipt: `13b652388b680b810d11d61186d539c756239015d9947814deff5156fc4a0bca`;
- R2 retention receipt: `9a1845c7b81e541c45821d09ba8876d6b6232387e7d5f65e846f321bc8b22389`;
- result summary: `4e865928a5362e00eb4d07e7a89272c0638c1aaa0dedeb0871f35aeceeab478e`.

## Results

| Gate | 2021-01 legacy | 2021-12 post-v5.1 |
|---|---:|---:|
| Exact 64 MiB request and R2 retention | PASS | PASS |
| Frozen source header | PASS | PASS |
| Parsed data rows | 6,833,888 | 8,671,581 |
| Timestamp parse | 100% | 100% |
| Malformed rows | 0 | 0 |
| Second distinct market day reached | PASS | PASS |
| Expected first market day | FAIL (`2021-01-02`) | PASS (`2021-12-01`) |
| Market-day order non-decreasing | **FAIL** | **FAIL** |
| Complete first-day prefix block | **FAIL** | **FAIL** |

The parser reached its frozen 1 GiB uncompressed cap after feeding only 23,068,672 compressed payload bytes in
January and 32,243,712 in December. It observed 31 distinct dates in each prefix, but dates later regressed. The
post-v5.1 first-appearance order itself includes `2021-12-21` before `2021-12-17` and `2021-12-23` before
`2021-12-22`. January also extends through `2021-02-01` while beginning on `2021-01-02`.

## Interpretation

The monthly period-offer CSVs are not date-contiguous streams. A leading compressed prefix can expose rows from
many dates while leaving every date incomplete. Therefore the first transition to another date is not a safe
end-of-day boundary, and a fixed ZIP prefix cannot provide a complete one-day cross-section.

This rejects the proposed low-transfer extraction route; it does not reject historical AEMO data or prove that a
full local decompression is the only possible source route. The next admissible work is a source audit for a free
queryable/date-partitioned mirror or official interface. If none has verifiable provenance and licensing, a new
protocol may compare a complete sequential compressed stream against its exact data/storage budget. The failed
prefixes cannot be extended under this protocol.

No fresh confirmation month, target outcome, paid data, remote worker, model or GPU was used. Historical joins,
action semantics, causal effects and EcoMD remain unvalidated.
