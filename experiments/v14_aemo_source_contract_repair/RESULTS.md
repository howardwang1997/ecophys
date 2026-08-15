# AEMO 64 KiB source-contract repair results

**Decision:** `PASS_TRANSFER_REPAIR_AND_SOURCE_HEADER_CONFIRMATION`

**Frozen protocol commit:** `23c847de0527ad1e7b367d596d3a4bb82d34c194`

**Manifest SHA-256:** `55c1e46e78992719955ca68415724d9dc0a266ccacb2cbddcfaf6fd617c16986`

**Offline proof SHA-256:** `0be682973ed75bc65c630c8ac650cb839cffc60baa3fa4d256d5a4816ca3c8d5`

**Raw summary SHA-256:** `e4bac4ac57b8b25b8d91a3465eba544c9c9e22050c47750c89344e339f6417c4`

## Gates

| Gate | Observed | Required | Result |
|---|---:|---:|---|
| Exact frozen objects requested | 10/10 | 10/10 | PASS |
| HTTP 206 | 10/10 | 10/10 | PASS |
| Exact 65,536-byte response and strict partial `Content-Range` | 10/10 | 10/10 | PASS |
| ZIP local header and MMSDM `I` row parsed | 10/10 | 10/10 | PASS |
| Exact scientific source-header contract | 10/10 | 10/10 | PASS |
| Complete compressed archive transferred | 0 | 0 | PASS |
| `D` market row parsed | 0 | 0 | PASS |
| GPU or paid data used | 0 | 0 | PASS |

Total transfer was exactly 655,360 bytes. Response bodies were not persisted; the artifact retains parsed metadata,
URL, retrieval time, response headers and prefix SHA-256 only.

## What passed

The repaired transport gate works as intended. Every response was exactly 65,536 bytes, every final byte was
65,535, and every declared object total was larger than the response. The smallest selected objects were the
identity archives: 150,066 bytes in 2021-01 and 162,525 bytes in 2021-12. Neither was transferred completely.

The scientific header result independently reproduces the v1 finding on two new mechanically selected months:

- 2021-01 uses `OFFER,BIDPEROFFER,1`, `DISPATCH,UNIT_SOLUTION,2` and
  `PARTICIPANT_REGISTRATION,DUDETAILSUMMARY,4` without the v5.1 fields;
- 2021-12 uses `BIDS,BIDOFFERPERIOD,1`, `DISPATCH,UNIT_SOLUTION,3` with `DISPATCHMODETIME`, and
  `PARTICIPANT_REGISTRATION,DUDETAILSUMMARY,5` with `DISPATCHSUBTYPE`; and
- both months preserve the expected bid-day and applied-offer-link headers.

The exact source matrix is therefore supported at information-header level across two independent pre/post month
pairs. This closes the source-version and transfer-safety metadata gate.

## What did not become evidence

No market row, timestamp, key uniqueness, effective-dated identity interval, applied-offer join, dispatch join or
market outcome was inspected. The result cannot identify participant submission interface, estimate a 5MS/WDR
effect, establish causal comparability or validate an Economic World Model. The 2021-12 bid-period archive declares
a compressed total of 1,610,349,080 bytes, so a full-download row strategy would be scientifically and
operationally disproportionate at this gate.

## Authorization and next gate

This pass authorizes only the design of a separately frozen minimal E1 row-level conformance protocol. That design
must first determine whether already consumed local artifacts or official small daily reports can test timestamp,
key and join semantics without downloading a multi-gigabyte monthly bid archive. It must specify exact rows/dates,
byte/storage caps, leakage rules and failure-without-replacement before access.

Bulk synchronization, causal estimation, prospective outcomes, model training, paid data and GPU remain locked.
