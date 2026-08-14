# AEMO 5MS two-clock loader-control validation

**Frozen:** 2026-08-14T10:13:03Z

**Parent commit:** `52e3b1d5da290efd7d787106d31fa8efb0f2f355`

**Scientific role:** development-only metadata validation. This protocol cannot establish a market effect or a
prospective result.

## Question

Can untouched official AEMO SQLLoader controls independently validate the structural endpoints of a two-clock
ontology: a legacy 30-minute action/report regime before the March 2021 reporting deployment and a 5-minute
action/report regime after the October 2021 rule commencement?

The discovery evidence is not validation. It includes the already inspected January--December 2021
`BIDPEROFFER` controls, the March and April `BIDDAYOFFER` controls, the March `DISPATCHOFFERTRK` control, the v1/v2
archive headers and AEMO's official [Data Model v5.00 technical
specification](https://www.aemo.com.au/-/media/files/electricity/nem/5ms/systems-workstream/2021/emms-technical-specification-5ms-data-model-v500-marked-up.pdf)
and [bidding production
timeline](https://www.aemo.com.au/initiatives/major-programs/past-major-programs/five-minute-settlement/5ms-systems-in-production/bidding).
Those sources revealed that reporting compatibility deployed in production on 8 March, bidding transition began
on 1 April and the 5MS rule commenced on 1 October.

## Frozen selection

The validation months were selected without requesting their controls: six calendar months before the March 2021
reporting-deployment month gives 2020-09, and six calendar months after the October 2021 rule-commencement month
gives 2022-04. Each month contributes exactly three official controls in fixed order:

1. `BIDDAYOFFER`;
2. `BIDPEROFFER`; and
3. `DISPATCHOFFERTRK`.

The six exact URLs, expected owners, target tables, required columns and non-`FILLER` requirements are frozen in
`data/manifests/aemo_loader_control_audit_v3.yaml`. No replacement is allowed for a missing or mismatched object.

## Gates

The experiment passes only if all six objects:

- return HTTP 200 without redirection;
- remain below the 65,536-byte metadata cap and parse as SQLLoader controls;
- match the frozen owner and target table;
- contain every frozen required column; and
- do not mark any required non-`FILLER` column as `FILLER`.

Every response is represented by URL, retrieval time, selected headers, byte count and SHA-256. Raw control text
is not committed. A failure is retained and the URL set is not repaired post hoc.

## Lock

Only `.ctl` metadata may be requested. No CSV or ZIP archive, market row, row count, outcome, prospective event,
paid dataset, remote worker or GPU is authorized. Even a complete pass authorizes only a later, separately frozen
archive-header protocol; it does not unlock row access.
