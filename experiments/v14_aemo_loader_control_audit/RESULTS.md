# AEMO 5MS two-clock loader-control results

**Decision:** `PASS_TWO_CLOCK_LOADER_ENDPOINTS_ONLY`

**Frozen protocol commit:** `25560ccdec9dafa292c93f9d5bf4f403beb154ed`

**Manifest SHA-256:** `2a4c81df160c24336da6b8af6ac5629645299c0948af320770e3f3430f7b9e74`

**Summary SHA-256:** `577e1815898acdbd750c7bc5e38c1c588195cc6262ac0144baa509dc427cfa13`

## Gates

| Gate | Observed | Required | Result |
|---|---:|---:|---|
| Exact frozen controls requested | 6/6 | 6/6 | PASS |
| HTTP 200 without replacement | 6/6 | 6/6 | PASS |
| SQLLoader parse | 6/6 | 6/6 | PASS |
| Owner and target-table contract | 6/6 | 6/6 | PASS |
| Required columns present and non-`FILLER` | 6/6 | 6/6 | PASS |
| CSV/ZIP archive opened | 0 | 0 | PASS |
| Market rows opened | 0 | 0 | PASS |
| GPU or paid data used | 0 | 0 | PASS |

## Findings

The untouched 2020-09 endpoint validates the legacy representation. Its period control connects as and appends
into `BIDPEROFFER`, retaining `SETTLEMENTDATE`, `OFFERDATE`, `VERSIONNO`, `ROCUP` and `ROCDOWN`. The daily offer
and applied-offer controls retain their frozen legacy owners, targets and keys.

The untouched 2022-04 endpoint validates the post-5MS representation. The historically named
`PUBLIC_DVD_BIDPEROFFER_202204.ctl` connects as and appends into `BIDOFFERPERIOD`, retaining `TRADINGDATE`,
`OFFERDATETIME`, `RAMPUPRATE` and `RAMPDOWNRATE`. Its daily control retains the rebid metadata and `REFERENCE_ID`;
the applied-offer tracker preserves its target and key fields.

Together with the development-only March controls, this validates a two-clock metadata ontology: the reporting
compatibility layer deployed before the action/rule transition. It also resolves the March
`OFFER,BIDOFFERPERIOD,1` puzzle at the loader level: the March period file was designed to load into legacy
`BIDPEROFFER` while discarding new-only clock and ramp columns. It is a compatibility bridge, not a clean legacy
month and not evidence that native 5-minute bids were legal before transition.

All six server objects report April 2026 `Last-Modified` times, so the committed URL, byte count and SHA-256 are
the reproducibility identity. No raw control text is committed.

## Limit

This result proves that official free metadata can distinguish clean legacy and post-5MS loader endpoints. It does
not establish row availability, action provenance, participant submission mode, applied-offer join coverage,
behavioral adaptation or a market effect. A SQLLoader control describes how an export is loaded, not which process
generated every row.

## Next gate

The pass authorizes only a separately frozen archive-header protocol. That protocol must preserve both clocks,
verify exact report package/table/version and required keys, and fail on mixed or information-losing records. No
archive download, row count, row filter, model training, prospective outcome, paid data or GPU is unlocked by this
result alone.
