# AEMO modern daily row-conformance result

**Authoritative decision:** `FAIL_MODERN_ROW_CONFORMANCE_SMOKE`

**Frozen protocol commit:** `5645990496065b0f812db4c969e152a7b7198c7d`

**Execution time:** 15 August 2026. The three source requests were executed once, without replacement or retry,
only after the protocol commit was pushed. ZIP/CSV access occurred only after all exact bytes were independently
retained and verified in R2.

## 1. Acquisition and retention

All three immutable transfer and retention gates passed:

| Object | Bytes | SHA-256 | R2 verified |
|---|---:|---|---:|
| `BID_MOVE_COMPLETE` | 9,095,887 | `dcb7484168f8648ff9cb86a5843ab10f400bd984f1c6e0629273e3cc9e432189` | yes |
| `NEXT_DAY_DISPATCH` | 8,611,556 | `e0b39c1ad43c91bf980ebc0af5598bbd1924a27a21df2f88413046c3625c6c2a` | yes |
| `DUDETAILSUMMARY` | 378,528 | `f6af1ba508eb473bb95ee0dae0964b9e00d29aa6f8bf549a60f75d597f48c3ae` | yes |

Total compressed bytes were exactly 18,085,971. Every remote object under
`r2://ecophys/raw/aemo/v14_row_conformance/market_date=2026-06-16/` matched its local content length and SHA-256
metadata. All three ZIP CRC checks then passed.

Artifact hashes:

- download receipt: `cbd1ff01adf39e6493dfaa9bf59d8021df30911ea139e045a2eb1dfe43623617`;
- retention receipt: `ac527a26be88005e72241c3b2f1a1c8b3106618daf2e3113a2e3e850431aa7c9`; and
- result summary: `fc422654de5c64a91e71b8dcceb22612f406092cdf6a36900859072041a6668b`.

## 2. Schema, time and key results

All five exact table headers and required fields passed. Parsed target-row counts were:

| Table | Rows | Primary-key duplicates |
|---|---:|---:|
| `BIDDAYOFFER_D` | 2,215 | 0 |
| `BIDPEROFFER_D` | 635,760 | 0 |
| `DISPATCHOFFERTRK` | 592,560 | 0 |
| `DISPATCHLOAD` | 161,952 | 0 |
| `DUDETAILSUMMARY` | 23,304 | 0 |

All 4,535,925 contracted timestamp values parsed. All 637,975 bid rows had the frozen market date and all
1,390,272 interval rows were inside the declared AEMO market-day window. The resource cap also passed: 1,493,888
total MMSDM data rows were scanned, including non-target tables in the next-day archive.

## 3. Join results

The daily/period bid parent join passed `635,760/635,760`. Every tracker record had non-null applied-offer
references and at least one exact period-bid match: `592,560/592,560`. Every tracker record also matched physical
dispatch: `592,560/592,560`. Every unique physical dispatch key matched exactly one effective-dated DUID identity:
`161,952/161,952`, with zero overlapping identity intervals.

The preregistered direction-multiplicity gate failed. Because `DISPATCHOFFERTRK` has no direction field,
43,200 of 592,560 tracker rows matched more than one period-bid row, an ambiguous rate of `0.0729040097`. The
frozen maximum was `0.05`. The threshold is not relaxed and the result is not reclassified.

## 4. Interpretation

The modern public data plane is structurally strong: exact sources, schemas, timestamps, keys, bid parentage,
dispatch and effective identities all conformed on the selected day. But a two-table
`DISPATCHOFFERTRK`--`BIDPEROFFER_D` join is not a unique applied-action bridge for bidirectional cases. Silently
choosing one candidate would fabricate agent actions.

This is a useful engineering/scientific boundary, not a paper-level finding. It does not show market adaptation,
causality, replay fidelity or EcoMD prediction. It also does not establish raw participant submissions or rejected
actions. E1a remains failed and does not unlock a multi-day panel or GPU model training.

The next admissible work is an explicitly post-hoc development audit of official `DISPATCHLOAD` direction
semantics and the retained 16 June rows. If a three-table direction bridge is justified, it must be frozen and
confirmed on a fresh mechanically selected day. Both V100s and the RTX 2060 remain unallocated.
