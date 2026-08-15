# AEMO 64 KiB source-contract transfer repair

**State:** frozen and network-unexecuted. No selected 2021-01 or 2021-12 ZIP prefix, CSV or market row was accessed
before this document, manifest and collector.

**Scientific role:** development-only confirmation that the already-supported channel-scoped source matrix can be
tested without transferring a complete compressed object. This is not a causal result or a row-access gate by
itself.

## Why this repair exists

The v1 source-header predictions passed 10/10, but its 256 KiB request transferred two smaller
`DUDETAILSUMMARY` objects completely. The raw v1 collector failed to infer that fact from `Content-Range`; the
authoritative result is therefore `FAIL_FULL_ARCHIVE_TRANSFER_GUARD`. The v1 months remain consumed development
evidence and cannot be rerun or replaced.

## Offline range proof

Before selecting new URLs, a deterministic no-network proof compared the preserved metadata from 20 consumed
prefixes with a synthetic AEMO-style deflated ZIP:

- observed maximum local-data offset: 89 bytes;
- observed maximum rows before the information header: 1;
- observed maximum information-header fields: 57;
- synthetic stress values: 95 bytes, 1 row and 128 fields;
- synthetic full compressed size: 624,432 bytes;
- tested prefix: exactly 65,536 bytes with a successful header parse and no `D` row; and
- proof decision: `PASS_64_KIB_PREFIX_BUDGET`.

The artifact SHA-256 is `0be682973ed75bc65c630c8ac650cb839cffc60baa3fa4d256d5a4816ca3c8d5`.
This is a parser-budget proof, not evidence that a future AEMO object must exceed 64 KiB. Any smaller object causes
an immutable transfer-gate failure.

## Mechanical untouched-month selection

For each boundary, start at the nearest complete outside calendar month and move outward until the month is absent
from the complete consumed-month registry. This selects:

1. `2021-01`, because the nearest pre-bridge month `2021-02` is consumed; and
2. `2021-12`, because the nearest post-v5.1 month `2021-11` is consumed.

The frozen consumed registry is `2020-09`, `2021-02`, `2021-03`, `2021-09`, `2021-11`, `2022-04`, `2025-01` and
`2025-07`. October 2021 remains prohibited because it straddles the WDR/v5.1 boundary. Missing, redirected,
malformed, short or mismatched objects are not replaced.

## Exact request and gates

Each of the same five roles in each month receives one request with `Range: bytes=0-65535`. A passing object must
have all of the following:

1. HTTP 206;
2. exactly 65,536 response bytes;
3. `Content-Range` final byte 65,535 and declared total strictly greater than 65,536;
4. no complete compressed-object transfer;
5. a parseable first ZIP member and MMSDM `I` row before any `D` row; and
6. the exact frozen channel/package/table/version and required/forbidden-field projection.

The scientific source-header and transfer-safety subgates are reported separately. Overall pass requires 10/10 on
both, zero complete compressed-object transfers and zero market rows. The parser retains the 65,536-byte inflated
cap. Response bodies are not persisted.

## Immutable decision rule

The exact manifest is `data/manifests/aemo_source_contract_repair_v2.yaml`. It is committed and pushed before any
selected request. The collector runs once from that clean commit and refuses an existing output. Any failure is
preserved without rerun, substitution, range increase or contract relaxation.

Even a 10/10 overall pass authorizes only the design of a separately frozen, minimal row-level timestamp/join
conformance sample. It does not authorize bulk data, effect estimation, prospective outcomes, training, paid data,
remote workers or GPU use.
