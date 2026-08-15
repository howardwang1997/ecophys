# AEMO NEMDE two-interval XML conformance v1 — result

**Decision:** `PASS_NEMDE_XML_CONFORMANCE`

The pushed protocol at `9f44bb4431b57564608848cb5b577b7b1e58fa9b` was executed once. Both exact 1 MiB
ranges returned HTTP 206, were SHA-256 verified in R2 before parsing, and reproduced the frozen local-header,
deflate, uncompressed-size and CRC contracts. No following member was parsed and no raw range/XML is committed.

| Gate | 2021-01-01 interval 144 | 2021-12-01 interval 144 |
|---|---:|---:|
| XML bytes | 7,851,704 | 8,895,016 |
| total elements | 50,571 | 58,679 |
| input descendants | 49,200 | 57,261 |
| traders / trader solutions | 349 / 349 | 383 / 383 |
| generic constraints / solutions | 815 / 815 | 937 / 937 |
| price-setting rows | 190 | 81 |

Both cases have root `NEMSPDCaseFile`, exactly one `NemSpdInputs`, `NemSpdOutputs` and `SolutionAnalysis`, every
frozen input/output group and a nonempty price-setting section. The applied input includes all five prospectively
listed action attributes: `PriceBand1`, `BandAvail1`, `MaxAvail`, `RampUpRate` and `RampDnRate`. It also exposes
`ParticipantID`, `DUID`/`TraderID`, offer effective/settlement dates and version, forecast-offer time, initial
conditions, SCADA, demand, network and generic constraints. Output exposes solver version/status/objective,
regional prices, unit energy/FCAS targets, interconnector flows, constraint marginal values and violations.

## Cross-regime finding

The two cases have identical input tag-name and input attribute-name sets. Output tag names and price-setting
attribute names are also identical. The sole output attribute present only after 5MS/WDR is
`FSTargetModeTime`. This matches the independent Data Model audit that `DISPATCHMODETIME` was added as a
scientifically meaningful fast-start state, and supports a version-aware common projection plus one explicit
post-change state extension. This is evidence from one interval per regime, not a universal schema theorem.

Artifact SHA-256 values:

- download receipt: `ad0c0ebefeca55404afe393f972281670d0018ae4267763cb1c5e301a7013416`
- retention receipt: `b36f59936deddf927957308a32a4cf150b6dfe1c7c71c78dfbeaea7e43b07609`
- summary: `f48d86b8f7837956fa5813e8719a712d543ade3e795fa1ad691036bd096bb7cd`

## Interpretation

Historical production NEMDE cases are a synchronized real mechanism interface, not merely a collection of derived
dispatch tables. The next useful experiment is an outcome-blind one-day development audit that measures temporal
schema stability and exact alignment of case outputs to public dispatch tables, followed by a scoped open-solver
replay baseline.

This result does not show that public files contain every submitted/rejected action, does not make NEMDE
executable and does not validate a counterfactual, adaptation effect or model. Raw redistribution remains locked
pending written clarification. Total source transfer was 2 MiB; GPU-hours, paid data and target events were zero.
