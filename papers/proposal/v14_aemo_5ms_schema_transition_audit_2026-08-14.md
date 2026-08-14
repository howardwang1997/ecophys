# AEMO 5MS schema-transition audit

**Date:** 2026-08-14

**Decision:** `DOCUMENTED_MECHANISM_TRANSITION_NOT_NAMESPACE_ALIAS`

**Consequence:** preserve the v2 held-out failure, keep all AEMO rows locked, and replace the binary
legacy/current crosswalk with an explicitly regime-aware development design. Do not make the failed test pass by
allowing both package labels as synonyms.

## 1. Question

The held-out header audit found `BIDS,BIDDAYOFFER,1` and `BIDS,BIDOFFERPERIOD,1` in 2021-09 after freezing
`OFFER,BIDDAYOFFER,2` and an `OFFER` package from 2021-03 discovery. All required source fields and internal table
names otherwise passed. The question was whether `OFFER` to `BIDS` is a cosmetic export rename or marks a real
change in the bidding observation process.

## 2. Official evidence

| Evidence | Implication |
|---|---|
| AEMO's [5MS bidding production page](https://www.aemo.com.au/initiatives/major-programs/past-major-programs/five-minute-settlement/5ms-systems-in-production/bidding) dates the bidding transition from 1 April through 30 September 2021. Participants could remain on the legacy 30-minute interface or submit 5-minute bids; before rule commencement, each six-period profile had to be identical within a half-hour. | The transition window contains two action representations and participant choice of submission mode. It is not a stationary legacy regime. |
| AEMO's [5MS transition FAQ](https://www.aemo.com.au/-/media/files/electricity/nem/5ms/readiness-workstream/2020/5ms-bidding-transition-plan-faqs.pdf) distinguishes legacy `BIDPEROFFER` from 5-minute `BIDOFFERPERIOD`; it states that the latter contains 5-minute submissions rather than replicated 30-minute bids and that next-day files carried both during transition. | A table/package change can identify action granularity and submission path. A field-presence crosswalk alone cannot recover which mechanism generated a row. |
| The official [EMMS 5MS Data Model v5.00 technical specification](https://aemo.com.au/-/media/files/electricity/nem/5ms/systems-workstream/2021/emms-technical-specification-5ms-data-model-v500-marked-up.pdf) maps legacy CSV records `OFFER,BIDDAYOFFER,2` and `OFFER,BIDPEROFFER,2` to `BIDS,BIDDAYOFFER,1` and `BIDS,BIDOFFERPERIOD,1`. | `OFFER` and `BIDS` are documented report generations, not arbitrary spelling variants. |
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

The current evidence does not explain the discovery archive's unusual `OFFER,BIDOFFERPERIOD,1` combination, which
is not the canonical old/new pair in the transition specification. Because the historical objects were republished
in April 2026 and AEMO warns of archive/loader incompatibilities, this combination stays unresolved until its
SQLLoader control/version record or an AEMO clarification is obtained. It cannot be normalized silently.

## 4. Revised development ontology

| Regime | Clock | Required action representation | Scientific role |
|---|---|---|---|
| R0 pre-transition | before 2021-04-01 | legacy 30-minute `OFFER/BIDPEROFFER` plus daily offer and applied-offer tracking | baseline development |
| R1 bidding transition | 2021-04-01 through 2021-09-30 | both legacy `BIDPEROFFER` and 5-minute `BIDOFFERPERIOD`, with submission mode and six-identical-period constraint | mechanism-transition development; not schema validation |
| R2 5MS rule live | from 2021-10-01 | `BIDS/BIDOFFERPERIOD` and rule-valid 5-minute profiles | post-change development |
| R3 later public summary | version-specific `_D` reports plus raw/applied offer linkage | derived observation layer, not assumed equivalent to submitted actions | modern robustness only |

The exact implementation must use official version clocks rather than infer regimes from file names. Any row whose
submission mode or source generation is unresolved is retained as unresolved; it is not assigned by its values.

## 5. Research implication

This changes the AEMO role in V14 in a useful way. Five-Minute Settlement is not merely a source of convenient old
data; it is a completed, real mechanism intervention with an explicitly staged action-space migration. It can be a
historical development event for the Lucas-test architecture:

- M2 must encode the old/transition/new bidding constraints and applied-offer selection;
- M3 must represent participant choice and adaptation between submission modes during transition; and
- M4 can test changes in participation, contribution shares and technology/registration composition.

It remains development-only because the outcome is historical and known. It cannot supply prospective NCS/NMI
confirmation, but it is better aligned with the paper than treating AEMO as a generic price/dispatch panel.

## 6. Next gate

Before any AEMO data row is opened:

1. obtain the exact report/control mapping for the republished March 2021 `OFFER,BIDOFFERPERIOD,1` archive;
2. freeze a regime-aware field and key contract covering R0--R2, including action granularity and applied-offer
   linkage;
3. choose fresh, non-transition validation months on each side of the clock without reusing 2021-03, 2021-09,
   2025-01 or 2025-07 as held-out evidence; and
4. preregister empty-row, mixed-mode, timestamp, identity and join-coverage failure rules.

No new archive download, row parser, model training, paid data or GPU allocation is authorized by this audit.
