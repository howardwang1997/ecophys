# AEMO two-clock bounded ZIP-prefix header results

**Decision:** `FAIL_VERSION_CLOCK_CONTRACT`

**Post-run safety correction (2026-08-15):** `FAIL_FULL_ARCHIVE_TRANSFER_GUARD`

**Frozen protocol commit:** `ee673e12609b6f8dc8b7760f1681f36b2e99df6a`

**Manifest SHA-256:** `2391b145e710ec34eb94d5e09af58837462fa78c04ec77ead0071922588d6527`

**Summary SHA-256:** `d1d0be04b398584d44d0f495760c627760a75d07fceb2bccc2f041a9a8c6ce21`

## Gates

| Gate | Observed | Required | Result |
|---|---:|---:|---|
| Exact frozen prefixes requested | 10/10 | 10/10 | PASS |
| HTTP 206 with zero-based `Content-Range` | 10/10 | 10/10 | PASS |
| ZIP local header and MMSDM `I` row parsed | 10/10 | 10/10 | PASS |
| Member/package/table/required fields | 10/10 | 10/10 | PASS |
| Exact package/table/version header contract | 7/10 | 10/10 | **FAIL** |
| `D` market row opened | 0 | 0 | PASS |
| Complete compressed archive transferred | 2 | 0 | **FAIL** |
| GPU or paid data used | 0 | 0 | PASS |

The ten responses total 2,409,220 bytes. Raw prefix bytes were not committed; each response retains its URL,
`Content-Range`, retrieval time, byte count and prefix SHA-256.

The original frozen collector incorrectly hard-coded `full_archive_downloaded=false`. A later audit of its own
immutable response metadata found that both small identity objects were transferred in full:
`r0-prefix-2020-09-dudetailsummary` returned 148,577 bytes with
`bytes 0-148576/148577`, and `r2-prefix-2022-04-dudetailsummary` returned 163,491 bytes with
`bytes 0-163490/163491`. No `D` row or full object was decompressed or parsed, but receiving every compressed byte
violated the declared transfer guard. This correction does not change the already-failing overall decision.

## Three preserved failures

1. The 2020-09 period object is `OFFER,BIDPEROFFER,1`, not the frozen
   `OFFER,BIDPEROFFER,2`. Its member, package, table and all eleven required legacy fields pass.
2. The 2022-04 dispatch object is `DISPATCH,UNIT_SOLUTION,3`, not version 2. It retains every required field and
   adds `DISPATCHMODETIME` relative to the earlier header.
3. The 2022-04 identity object is `PARTICIPANT_REGISTRATION,DUDETAILSUMMARY,5`, not version 4. It retains every
   required field and adds `DISPATCHSUBTYPE`.

No object is replaced and the version gate is not relaxed after observing these results. The two validation months
are now development evidence, not a reusable held-out pair.

## Interpretation

The main 5MS action/report endpoints pass: 2020-09 exposes legacy `OFFER/BIDPEROFFER` fields, while 2022-04
exposes `BIDS/BIDOFFERPERIOD` with the new clock and ramp fields. Applied-offer linkage also passes on both sides.
The failure shows that a single observation clock is still too coarse. The official follow-up finds that the
legacy version-2 expectation was scoped to `NEXT_DAY_OFFER_*`, not the observed `PUBLIC_DVD` archive channel;
`UNIT_SOLUTION` v3 adds fast-start dynamic-state observability; and `DUDETAILSUMMARY` v5 adds the identity required
for the WDR mechanism that commenced on 24 October 2021. These are three different failure classes, not one global
schema boundary.

The correct design is therefore not merely “mechanism clock plus observation clock.” It needs mechanism clocks,
delivery-channel identity and a source-specific observation-version vector. Stable required-field projections may
bridge versions, but version numbers cannot be silently ignored because added fields can alter observability or
mechanism identity. Full classification is in
`papers/proposal/v14_aemo_source_version_and_clustered_reform_audit_2026-08-14.md`.

## Next gate

The later channel-keyed source contract validated all ten header/field predictions, but independently repeated the
complete-transfer error on two small identity objects. Repair the generic `Content-Range` guard and freeze a
smaller-range protocol on new untouched months. Treat all consumed months as development only. This failure does
not authorize row access, model training, prospective outcomes, paid data or GPU.
