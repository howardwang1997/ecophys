# AEMO channel-scoped source-contract prefix validation

**State:** frozen protocol; no selected ZIP prefix or CSV was accessed before this document and manifest.

**Scientific role:** development-only validation of source identity and observation boundaries. This is not an
effect estimate, prospective confirmation or permission to inspect market rows.

## Question

Does the official postmortem of the failed 7/10 version gate predict exact `PUBLIC_DVD` information headers and
version-specific field availability on fresh pre-bridge and post-v5.1 months?

## Mechanical sample selection

The sample is determined without availability checks:

1. take the nearest complete calendar month strictly before the 8 March 2021 reporting bridge: `2021-02`;
2. take the nearest complete calendar month strictly after the 24 October 2021 WDR/v5.1 boundary: `2021-11`;
3. inspect the five fixed roles `BIDDAYOFFER`, `BIDPEROFFER`, `DISPATCHOFFERTRK`, `DISPATCHLOAD` and
   `DUDETAILSUMMARY` in each month; and
4. make no replacement for a missing, redirected, malformed or mismatched object.

The rule excludes all prior discovery/failed-validation months: `2020-09`, `2021-03`, `2021-09`, `2022-04`,
`2025-01` and `2025-07`. It also prohibits the mixed October 2021 month.

## Frozen source contract

- Delivery channel: `PUBLIC_MONTHLY_ARCHIVE`.
- Archive family: `MMSDM_Historical_Data_SQLLoader/PUBLIC_DVD`.
- Pre-bridge period report: `OFFER,BIDPEROFFER,1`, not the next-day-report version 2.
- Post-v5.1 dispatch report: `DISPATCH,UNIT_SOLUTION,3`, with required `DISPATCHMODETIME`.
- Post-v5.1 identity report: `PARTICIPANT_REGISTRATION,DUDETAILSUMMARY,5`, with required
  `DISPATCHSUBTYPE`.
- Pre-v5.1 dispatch/identity reports must not contain those two added fields.
- Participant interface choice during the transition remains partially identified; report shape and values are
  prohibited proxies, and private `SUBMISSION_METHOD` is recorded as declared but unpopulated.

The exact URLs, members, versions, required/forbidden fields, timeline and output path are frozen in
`data/manifests/aemo_source_contract_v1.yaml`.

## Access cap and gates

Each of the ten objects receives one `Range: bytes=0-262143` request. The parser may inflate at most 65,536 bytes,
must stop after the first complete MMSDM `I` row and must fail if it encounters a `D` row first. A full-download
fallback is prohibited.

The total gate passes only if all ten objects have:

1. HTTP 206 and a zero-based `Content-Range`;
2. a parseable ZIP local header and expected CSV member;
3. the exact channel-scoped package/table/version header;
4. every frozen required field and no frozen forbidden field; and
5. zero market-row, full-archive, GPU and paid-data access.

Failure is immutable. A failed URL or contract is not replaced, the manifest is not relaxed and the selected
months become development evidence. Passing authorizes only the design of a separately frozen small E1 row-level
conformance sample; it does not itself authorize that sample.
