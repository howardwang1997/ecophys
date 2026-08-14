# AEMO 5MS schema-transition audit

**Date:** 2026-08-14

**Decision:** `DOCUMENTED_MECHANISM_TRANSITION_NOT_NAMESPACE_ALIAS`

**Consequence:** preserve the v2 held-out failure, keep all AEMO rows locked, and replace the binary
legacy/current crosswalk with an explicitly regime-aware development design. Do not make the failed test pass by
allowing both package labels as synonyms.

**Refinement:** the later official version audit shows that report generation does not by itself reveal which
participant interface generated an action during compatibility emulation, and that WDR plus Data Model v5.1 add a
second clustered mechanism/observation boundary on 24 October 2021. See
`papers/proposal/v14_aemo_source_version_and_clustered_reform_audit_2026-08-14.md`.

## 1. Question

The held-out header audit found `BIDS,BIDDAYOFFER,1` and `BIDS,BIDOFFERPERIOD,1` in 2021-09 after freezing
`OFFER,BIDDAYOFFER,2` and an `OFFER` package from 2021-03 discovery. All required source fields and internal table
names otherwise passed. The question was whether `OFFER` to `BIDS` is a cosmetic export rename or marks a real
change in the bidding observation process.

## 2. Official evidence

| Evidence | Implication |
|---|---|
| AEMO's [5MS bidding production page](https://www.aemo.com.au/initiatives/major-programs/past-major-programs/five-minute-settlement/5ms-systems-in-production/bidding) dates the bidding transition from 1 April through 30 September 2021. Participants could remain on the legacy 30-minute interface or submit 5-minute bids; before rule commencement, each six-period profile had to be identical within a half-hour. | The transition window contains two eligible bid interfaces, but public report shape alone need not identify which one a participant used. It is not a stationary legacy regime. |
| AEMO's [5MS transition FAQ](https://www.aemo.com.au/-/media/files/electricity/nem/5ms/readiness-workstream/2020/5ms-bidding-transition-plan-faqs.pdf) distinguishes legacy `BIDPEROFFER` from 5-minute `BIDOFFERPERIOD`; it states that the latter contains 5-minute records and that next-day files carried both during transition. | A table/package change identifies report generation and possible action granularity, but compatibility emulation means it is not sufficient evidence of the participant's underlying submission interface. A field-presence crosswalk cannot recover which mechanism generated a row. |
| The official [EMMS 5MS Data Model v5.00 technical specification](https://aemo.com.au/-/media/files/electricity/nem/5ms/systems-workstream/2021/emms-technical-specification-5ms-data-model-v500-marked-up.pdf) maps legacy CSV records `OFFER,BIDDAYOFFER,2` and `OFFER,BIDPEROFFER,2` to `BIDS,BIDDAYOFFER,1` and `BIDS,BIDOFFERPERIOD,1`. | `OFFER` and `BIDS` are documented report generations, not arbitrary spelling variants. |
| The same specification schedules production deployment of replicated dispatch Bid/Offer reports for 8 March 2021, before bidding-transition go-live. It describes an emulated 288-period report accompanying legacy 48-period reports so participant models could remain consistent across `BIDPEROFFER` and `BIDOFFERPERIOD`. | The observation/data-model clock changes before the action/rule clock. March cannot be classified from its market date alone. |
| AEMO records [5MS rule commencement on 1 October 2021](https://www.aemo.com.au/initiatives/major-programs/past-major-programs/five-minute-settlement), after the six-month transition. | The correct temporal ontology has at least pre-transition, transition and post-commencement regimes. |
| AEMO describes the monthly archive as a [historical subset for analysis](https://di-help.docs.public.aemo.com.au/Content/Data_Interchange/Populating_historical_data_to_data_model_tables.htm) and separately warns that some historical files are not loader-compatible in its [historical-data guidance](https://markets-portal-help.docs.public.aemo.com.au/Content/InformationSystems/Electricity/HistoricalData.htm). | Archive file names and current loader assumptions cannot substitute for package/table/version provenance. Exact raw hashes and per-object headers are required. |

## 3. Verdict on the failed v2 gate

The package failure was scientifically correct. September 2021 lies inside the declared 5MS bidding transition,
when 30-minute and 5-minute submission paths coexisted. The v2 selector classified months only by archive naming
style (`PUBLIC_DVD` versus `PUBLIC_ARCHIVE#...`) and therefore collapsed a mechanism transition into one “legacy”
regime.

The 10/10 source-field pass remains useful: a common numerical projection may exist. It is not sufficient to claim
common action semantics. At minimum, a row needs the rule phase, source report generation, bid granularity,
submission clock and applied-offer link. A six-period 5-minute submission constrained to be identical is not the
same observed action as a native 30-minute bid merely because both can yield the same MW vector.

The discovery archive's unusual `OFFER,BIDOFFERPERIOD,1` combination is now resolved at the loader/reporting level.
The official March control file `PUBLIC_DVD_BIDPEROFFER_202103.ctl` instructs users to connect as the legacy
`BIDPEROFFER` owner and append into `BIDPEROFFER`, even though the CSV header and column layout use
`BIDOFFERPERIOD`. It marks `TRADINGDATE`, `OFFERDATETIME`, `RAMPUPRATE` and `RAMPDOWNRATE` as `FILLER`; the January
and February controls instead use the legacy `SETTLEMENTDATE`, `OFFERDATE`, `VERSIONNO`, `ROCUP` and `ROCDOWN`
columns. From April onward the control targets `BIDOFFERPERIOD` and retains the new clock and ramp columns.

This is an official compatibility bridge around the 8 March reporting deployment, not evidence that native
5-minute action was legal in March and not a 2026 republishing accident. It resolves which table the March archive
was designed to load, but it also establishes information loss under the legacy loader. March remains discovery
only and is unsuitable as a clean pre-intervention month.

## 4. Revised two-clock development ontology

The mechanism/action clock and observation/reporting clock must be encoded separately.

| Action phase | Clock | Legally meaningful action space |
|---|---|---|
| A0 | before 2021-04-01 | legacy 30-minute bids only |
| A1 | 2021-04-01 through 2021-09-30 | legacy and 5-minute interfaces coexist, but each six-period profile within a half-hour must be identical |
| A2 | 2021-10-01 through 2021-10-23 | native 5-minute profiles under the live 5MS rule; WDR not yet live |
| A3 | from 2021-10-24 | 5MS plus the live Wholesale Demand Response mechanism |

| Observation phase | Clock | Reporting/data-model representation |
|---|---|---|
| O0 | before 2021-03-08 | legacy `OFFER/BIDPEROFFER` representation |
| O1 | 2021-03-08 through 2021-03-31 | production compatibility bridge with emulated 288-period reports; March monthly control loads the new-shaped period report into the legacy table and discards new-only fields |
| O2 | 2021-04-01 through 2021-09-30 | dual submission/report generations during bidding transition |
| O3 | 2021-10-01 through 2021-10-23 | 5-minute reports after legacy 30-minute interfaces/reports discontinue, before Data Model v5.1 go-live |
| O4 | from 2021-10-24 | Data Model v5.1 and source-specific report versions; dispatch state and WDR identity observability change |

The exact implementation must use both clocks plus source-specific delivery/version clocks rather than infer
regimes from a monthly file name. Any row whose participant submission interface or source generation is
unresolved is retained as unresolved; it is not assigned by its values.
A whole-month March baseline would mix O0 and O1 while remaining in A0, creating a direct measurement-change
negative control for any claimed behavioral effect.

## 5. Research implication

This changes the AEMO role in V14 in a useful way. Five-Minute Settlement is not merely a source of convenient old
data; it is a completed, real mechanism intervention with an explicitly staged action-space migration. It can be a
historical development event for the Lucas-test architecture:

- M2 must encode the old/transition/new bidding constraints and applied-offer selection;
- M3 may represent participant choice and adaptation between submission modes only as latent or partially
  identified unless independent provenance is obtained; and
- M4 can test changes in participation, contribution shares and technology/registration composition.

The early reporting deployment also supplies a falsification test: a model that interprets the 8 March observation
change as participant adaptation has failed to separate measurement from mechanism. This two-clock separation is
more general than AEMO and should become part of the model-to-observation bridge rather than an AEMO-specific data
cleaning exception.

It remains development-only because the outcome is historical and known. It cannot supply prospective NCS/NMI
confirmation, but it is better aligned with the paper than treating AEMO as a generic price/dispatch panel.

## 6. Next gate

The frozen six-control validation on untouched 2020-09 and 2022-04 controls passed 6/6 HTTP, parse, owner,
target-table, required-column and non-`FILLER` gates. Its summary SHA-256 is
`577e1815898acdbd750c7bc5e38c1c588195cc6262ac0144baa509dc427cfa13`; full results are in
`experiments/v14_aemo_loader_control_audit/RESULTS.md`.

Before any AEMO data row is opened:

1. freeze a two-clock archive-header contract including action granularity, submission/report generation and
   applied-offer linkage;
2. choose fresh day ranges without reusing 2021-03, 2021-09, 2025-01 or 2025-07 as held-out evidence; and
3. preregister empty-row, mixed-mode, timestamp, identity, information-loss and join-coverage failure rules.

The metadata pass does not authorize CSV/ZIP access by itself. No row parser, model training, paid data or GPU
allocation is authorized by this audit.

The separately frozen bounded ZIP-prefix gate then failed at 7/10 exact versions while passing 10/10 HTTP 206,
ZIP-prefix parse, member, package, table and required-field checks. `BIDPEROFFER` was version 1 rather than 2 in
2020-09; `UNIT_SOLUTION` was version 3 rather than 2 and `DUDETAILSUMMARY` version 5 rather than 4 in 2022-04.
The official follow-up classifies these as a delivery-channel-scoped bid version, a fast-start dynamic-state
observation extension and a WDR mechanism-identity extension. It also establishes that WDR and Data Model v5.1
went live together on 24 October, so October cannot be one post-5MS bin. The failure remains immutable; the next
contract must follow the clustered-reform audit before fresh prefixes are frozen. Full archive and row access
remain locked.
