# AEMO channel-scoped source-contract prefix results

**Authoritative decision:** `FAIL_FULL_ARCHIVE_TRANSFER_GUARD`

**Scientific subgate:** `PASS_SOURCE_CONTRACT_10_OF_10`

**Frozen protocol commit:** `39c45dddf736e418a3e112a5a4689a782e918466`

**Manifest SHA-256:** `42cc9a940b68847aba1719c1f9568b3c1f9ee07785061080ba286be9e9e60296`

**Raw summary SHA-256:** `e7abbcf530d8d75a0f69c5885dfcbdc74a84f743ff9a7134754e6e8b28d8a239`

## Gates

| Gate | Observed | Required | Result |
|---|---:|---:|---|
| Exact frozen objects requested | 10/10 | 10/10 | PASS |
| HTTP 206 with zero-based `Content-Range` | 10/10 | 10/10 | PASS |
| ZIP local header and MMSDM `I` row parsed | 10/10 | 10/10 | PASS |
| Exact channel/package/table/version and required/forbidden fields | 10/10 | 10/10 | PASS |
| `D` market row parsed | 0 | 0 | PASS |
| Complete compressed archive transferred | 2 | 0 | **FAIL** |
| GPU or paid data used | 0 | 0 | PASS |

The ten responses transferred 2,409,465 bytes. The collector retained only parsed metadata, response provenance and
prefix hashes; it did not persist response bodies.

## Source-contract result

The scientific metadata hypothesis passed on both mechanically selected months:

- 2021-02 `PUBLIC_DVD_BIDPEROFFER` is exactly `OFFER,BIDPEROFFER,1`, confirming that the public monthly channel
  must not inherit the participant next-day version-2 expectation;
- 2021-02 `UNIT_SOLUTION,2` and `DUDETAILSUMMARY,4` omit `DISPATCHMODETIME` and `DISPATCHSUBTYPE`;
- 2021-11 `UNIT_SOLUTION,3` and `DUDETAILSUMMARY,5` contain those fields; and
- the bid, applied-offer and identity headers otherwise match all frozen projections.

This validates the asynchronous, channel-scoped observation matrix at the information-header level. It does not
identify participant interface choice during the transition, validate timestamps or joins, estimate a market
effect, or distinguish 5MS from WDR responses.

## Mandatory post-run correction

The raw summary reports `pass=true` and `full_archive_downloaded=false`. Those fields are wrong. For both
`DUDETAILSUMMARY` objects, the requested 256 KiB range exceeded the compressed object size:

| Object | Response bytes | `Content-Range` |
|---|---:|---|
| `pre-bridge-prefix-2021-02-dudetailsummary` | 150,150 | `bytes 0-150149/150150` |
| `post-v51-prefix-2021-11-dudetailsummary` | 162,163 | `bytes 0-162162/162163` |

In each case the final byte plus one equals the declared total, so the response contained every compressed byte of
the object. The parser inflated only its bounded prefix and stopped at the `I` row; no `D` row or full archive was
decompressed or parsed. Nevertheless, a complete compressed-object transfer is a full-archive download for the
frozen safety gate. The machine-readable correction is `artifacts/adjudication.json` and overrides the raw overall
pass flag without modifying the immutable raw summary.

No object is replaced and neither selected month is rerun. Both are now development evidence.

## Next gate

Repair the generic range auditor so `Content-Range` detects a complete-object transfer and forces failure. Any new
protocol must use a smaller fixed byte range, prove on synthetic or already consumed material that the information
header remains parseable, and mechanically select new untouched months. It must be frozen before requesting them.

That repair is now implemented, but remains network-unexecuted, in
`experiments/v14_aemo_source_contract_repair/PREREGISTRATION.md`. Its deterministic offline proof passes at 64 KiB
and its mechanical rule selects untouched 2021-01 and 2021-12. The repair protocol must be committed and pushed
before either month is requested.

This result does not authorize row access, bulk synchronization, model training, causal claims, prospective
outcomes, paid data or GPU.
