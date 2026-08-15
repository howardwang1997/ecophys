# V14 data acquisition and purchase decision

**Date:** 2026-08-14

**Decision:** `NO_BUY_NOW`

**Access boundary:** source metadata plus preregistered non-target historical development objects. No
prospective-event outcome row was opened, and no historical AEMO data row was counted or joined.

## 1. Bottom line

The historical feasibility study does not require a commercial dataset. AEMO exposes the required wholesale bid,
participant, dispatch and constraint tables through official NEMWeb directories at no cost, and CoW exposes solver
competitions through a public API together with the service implementation. These sources are sufficient to build
the E0 source contracts and, after the data gate is frozen, the limited E1 replay sample.

The first frozen sample confirms free transport but does not yet pass the scientific data contract. CoW arithmetic
auction-ID sampling yielded 33/100 available competitions and is not a valid high-coverage sampling frame. All ten
AEMO archives were available and intact, totaling 1.178 GB compressed and 31.879 GB uncompressed, but the frozen
file-name/internal-table mapping passed only 5/10 objects and the minimum fields passed 9/10. These failures
strengthen `NO_BUY_NOW`: the next bottleneck is an auditable enumerator and versioned semantic crosswalk, not a
commercial price feed.

The unresolved confirmation-data problem cannot currently be solved by buying a conventional market-data feed.
FTA's affected SSP/NMI standing data and settlement reports are delivered to eligible participant roles through
MSATS participant channels. Access therefore needs an authorised FRMP/NMISP/MDP/MC/DNSP research partner and an
explicit data-sharing/publication agreement. No public retail-level panel or off-the-shelf commercial FTA dataset
was established in this audit.

Production NEMDE access is a separate paid service. It is not a substitute for participant actions or adoption
data and is not recommended for purchase at the present gate.

## 2. Verified official sources

| Source | What is available | Access/cost | Current decision |
|---|---|---|---|
| [AEMO NEMWeb current reports](https://nemweb.com.au/Reports/Current/) | current bids, dispatch, prices, SCADA, network and other reports | public, no authentication | use for small non-target daily E1 samples after the manifest is frozen |
| [AEMO NEMWeb report archive](https://nemweb.com.au/Reports/ARCHIVE/) | report files retained for roughly the recent 13-month window | public, no authentication | use only for declared non-target dates |
| [AEMO MMSDM monthly archive](https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/) | individually downloadable historical tables from 2009 onward | public, no authentication | canonical historical AEMO source; never download the full monthly bundle by default |
| [AEMO MMS data-model report](https://aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem/market-management-system-mms-data) | table semantics, visibility, keys and update schedules | public | pin the model version for every month and validate schema drift |
| [AEMO registration page](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/registration) | current registered-participant list and exemptions | public | supplement effective-dated `PARTICIPANT`, `DUALLOC`, `DUDETAIL` and `DUDETAILSUMMARY`; not sufficient alone for historical identity |
| [AEMO copyright permissions](https://www.aemo.com.au/privacy-and-legal-notices/copyright-permissions) | general permission to use public AEMO material with accurate attribution, excluding confidential and third-party material | no licence fee identified | record exact attribution and source object; obtain clarification before redistributing bulk raw files |
| [CoW Order Book API](https://api.cow.fi/docs/) | auction IDs/blocks, order IDs and prices, solver submissions, addresses, ranks, scores, winner/filter state and transaction hashes | public endpoint; no purchase identified | best E1 mechanism-development source; retention, rate limits and dataset redistribution still require confirmation |
| [CoW OpenAPI contract](https://raw.githubusercontent.com/cowprotocol/services/main/crates/orderbook/openapi.yml) | versioned endpoint and field contract | public | pin raw SHA and deployed `/api/v1/version` for every collection interval |
| [CoW services repository](https://github.com/cowprotocol/services) | executable off-chain auction services and database semantics | open source under repository licences | use for mechanism audit; code licence does not automatically settle API-data redistribution terms |
| [AEMO FTA implementation page](https://www.aemo.com.au/initiatives/major-programs/nem-reform-program/nem-reform-program-initiatives/flexible-trading-arrangements) | rule clock, procedures, schemas, readiness and accreditation links | public metadata | watchlist only; not an affected-participant outcome panel |
| [AEMO FTA MDM reports](https://tech-specs.docs.public.aemo.com.au/Content/TSP_MSATS_Oct2026/MDM_Reports.htm) | documented SSP/NMI fields and RM29/RM53 report schemas | participant delivery: eligible FRMP/NMISP/MC roles | partnership/authorisation route, not a public download |
| [AEMO data-sharing process](https://di-help.docs.public.aemo.com.au/Content/Data_Sharing/2_-Requesting_data_sharing.htm) | formal sharing of participant subscription data after affected parties agree | agreement and participant infrastructure required | use only through a real partner with confidentiality and publication terms |
| [AEMO NEMDE Queue](https://www.aemo.com.au/energy-systems/market-it-systems/electricity-system-guides/nemde-queue-service) | production dispatch-engine input/output service | service page lists AUD 18,450 + GST application/annual fee, registered participants only | do not buy now; first test open `nempy` replay and identify the residual value of exact access |

This is a sourcing assessment, not legal advice. Each provenance object must preserve the applicable terms as
retrieved on the collection date.

## 3. AEMO table set and measured directory metadata

### 3.1 Minimum wholesale panel

- actions: `BIDDAYOFFER_D`, `BIDPEROFFER_D`, `DISPATCHOFFERTRK`;
- identity and entry/exit: `PARTICIPANT`, `DUALLOC`, `DUDETAIL`, `DUDETAILSUMMARY`, registration/exemption list;
- state and mechanism inputs: `DISPATCH_UNIT_SCADA`, demand, interconnector, constraint and network-outage tables;
- outcomes: `DISPATCHLOAD`, `DISPATCHPRICE`, `DISPATCHREGIONSUM`, constraint and interconnector solutions.

The 2025-01 official directory reports approximately 355 MB compressed for the five core bid/dispatch/identity
files (`BIDDAYOFFER_D`, `BIDPEROFFER_D`, `DISPATCHLOAD`, `DISPATCHOFFERTRK`, `DUDETAILSUMMARY`). Adding the price,
regional, dispatch-constraint, SCADA and network-outage files raises the selected set to roughly 590 MB compressed
for that month. The 2024-08 core set is approximately 350 MB compressed. This makes selective retrieval essential:
the full 2025-01 MMSDM bundle is roughly 19 GB, while the full 2026 monthly bundles shown by AEMO are much larger.

A provisional two-to-four-year selected-table budget is therefore `20--100 GB` compressed and `0.1--0.5 TB` of
working storage after CSV expansion, Parquet conversion, raw retention and derived caches. Replace this range with
measured `Content-Length`, row-count and compression-ratio manifests before bulk synchronization. The earlier
`0.5--2 TB` estimate for AEMO alone was too conservative and is retired.

The exact two-regime header sample measured 1,177,771,842 compressed bytes and 31,878,556,073 uncompressed bytes
across ten objects. Transport, byte length, SHA-256, CRC and single-member checks all passed. Semantic identity did
not: `DISPATCHOFFERTRK` and `DISPATCHLOAD` file names map to internal `OFFERTRK` and `UNIT_SOLUTION` tables, and
legacy `BIDPEROFFER` maps to `OFFER/BIDOFFERPERIOD` with `TRADINGDATE`. These discovery months cannot also serve as
the held-out proof of a repaired crosswalk.

The first independent crosswalk validation used mechanically selected 2021-09 and 2025-07 objects. All ten
internal tables and required source-field projections passed, but the strict package gate failed for the two
2021-09 bid objects (`BIDS` observed versus `OFFER` frozen). The held-out sample measured 1.557 GB compressed and
43.677 GB uncompressed. This is evidence that a field-level parser is plausible, but it does not authorize row
access. Official 5MS documentation shows that September 2021 is a mixed 30-minute/5-minute bidding transition and
that the old `OFFER` report types were formally replaced by `BIDS` types. The package change must therefore remain
part of the mechanism/action provenance.

### 3.2 Historical schema hazard

Official 2021-03 and 2021-10 directories do contain public bid, dispatch and identity archives, but their bid files
use legacy names such as `PUBLIC_DVD_BIDDAYOFFER` and `PUBLIC_DVD_BIDPEROFFER`; the 2024-08 and 2025-01 directories
expose `BIDDAYOFFER_D` and `BIDPEROFFER_D` under a newer `PUBLIC_ARCHIVE#...` convention. Consequently, a gap in a
third-party downloader is not evidence that the official raw data are absent. E1 must inspect headers and model
versions and prove semantic equivalence rather than renaming files blindly.

The bounded-prefix follow-up passed all stable field projections but failed three exact versions. Official release
records show that the `BIDPEROFFER` v2 expectation was scoped to `NEXT_DAY_OFFER_*`, not the `PUBLIC_DVD` archive;
`DISPATCH,UNIT_SOLUTION,3` adds fast-start state; and
`PARTICIPANT_REGISTRATION,DUDETAILSUMMARY,5` adds WDR identity. WDR and Data Model v5.1 both began on
24 October 2021, so a monthly October extract conflates 5MS-only and 5MS-plus-WDR intervals. Acquisition manifests
must include delivery channel/archive family and day-level mechanism/observation clocks, not only table and month.

The resulting channel-keyed contract was frozen at commit `39c45dddf` and tested once on mechanically selected
2021-02 and 2021-11 prefixes. All ten exact channel/package/table/version and required/forbidden-field predictions
passed. The total gate still failed: the 256 KiB request transferred both smaller `DUDETAILSUMMARY` compressed
objects in full (150,150 and 162,163 bytes). No `D` row was parsed and no body was retained, but the raw collector's
hard-coded `full_archive_downloaded=false` was incorrect. The immutable raw output is superseded by a machine-readable
`FAIL_FULL_ARCHIVE_TRANSFER_GUARD` adjudication. These months are development evidence and cannot be rerun or
replaced; row acquisition remains locked.

The separately frozen 64 KiB repair then passed all ten transfer and scientific header gates on untouched 2021-01
and 2021-12, with zero complete compressed objects and zero rows. This resolves the metadata acquisition method,
not row semantics. The 2021-12 bid-period object declares a 1.610 GB compressed total, so the next conformance
protocol must avoid indiscriminate monthly-archive downloads and first inventory already consumed local material
or exact official daily alternatives.

## 4. What can be acquired now

### Free and immediately locatable

1. AEMO table dictionaries, rule documents, current/archive directory metadata and exact individual-file URLs.
2. AEMO historical wholesale bids, applied offer versions, DUID identities, dispatch, prices, SCADA, constraints
   and outages for declared non-target dates.
3. CoW OpenAPI/service versions and the retained 100-ID failed audit; any larger historical solver-competition
   sample requires an outcome-blind eligible-auction enumerator first.
4. Public AEMO participant/accreditation lists and CoW on-chain settlement references.

### Available only through application or partnership

1. FTA SSP/NMI standing data, adoption, meter flows and participant reports delivered through MSATS.
2. Private participant bid/settlement subscriptions not reproduced on NEMWeb.
3. Production NEMDE queue access and copyright-restricted formulation material.

The official FTA documentation states that relevant RM29 reports are sent to participant outboxes and RM53 is
available to eligible FRMPs/AEMO. AEMO's public accreditation page describes NMISP applications but, at this audit
date, does not expose a dedicated downloadable accredited-NMISP register. Candidate partners must therefore be
identified from updated accreditation/registration records as they appear, not guessed in advance. A partner
agreement must also cover privacy/ethics review, de-identification, stable research pseudonyms, secure retention and
publication rights; raw household-level NMI or meter records must not be assumed publishable.

## 5. Purchase gate

No purchase or paid subscription is authorised until all of the following hold:

1. the free E1 sample has passed schema, identity, timestamp, leakage and replay checks;
2. a field-level missing-data report shows exactly which headline estimand cannot be measured publicly;
3. a vendor or partner supplies a sample and data dictionary that fill those fields, including failed actions and
   entry/exit rather than only prices;
4. licence terms permit the planned analysis, retained hashes, peer review and at least derived-data release;
5. one development event and two untouched confirmation events pass their event-clock contracts; and
6. the quote is compared with narrowing the claim or changing domain.

Buying another price feed, aggregate series or convenient repackaging of public AEMO tables does not pass this
gate. Buying NEMDE before open replay has been quantified also does not pass.

## 6. Next acquisition actions

1. Keep the machine-readable source registry metadata-only; record HEAD status, size, model version, terms URL and
   retrieval time without downloading target rows.
2. Ask AEMO Support Hub one precise question: whether any de-identified public report will expose SSP creation,
   active interval, NMISP/FRMP role and interval settlement outcomes after 2026-11-01.
3. Monitor the accreditation page for a real NMISP roster and approach an eligible partner only with a one-page
   minimum-field and publication-rights request.
4. Maintain the frozen CoW/Uniswap event registry; request competition-history retention, rate-limit and research-
   redistribution clarification only for a post-cutoff candidate that reaches a final package.
5. Use the prepared, unsent Elexon/NESO request for CRA-I015 and MDO/MDB provenance if external contact is approved.
6. Preserve all failed AEMO header protocols and the later 10/10 64 KiB repair pass. Inventory already consumed
   local AEMO rows and official small daily alternatives before freezing a minimal timestamp/key/join sample; do
   not fetch the 1.610 GB monthly bid-period object. Independently obtain a valid CoW enumeration rule. No GPU is
   needed.

The required partner topology, minimum field contract, candidate contact pool and scientific red lines are specified
in `papers/proposal/v14_fta_collaboration_brief_2026-08-14.md`. No named organisation is yet a confirmed collaborator
or confirmed production SSP operator.

The later cross-domain scout identified Elexon's public, no-key BMRS APIs and open-data licence as a potentially
superior route for the GB GC0166 event. This reinforces `NO_BUY_NOW`. CRA-I015 defines the required identity history
and Elexon supplies a formal request route, but the complete extract/licence/retention and submission/default/error
provenance still require written confirmation before target retrieval. See
`papers/proposal/v14_cross_domain_event_scout_2026-08-14.md` and
`papers/proposal/v14_gc0166_elexon_neso_clarification_brief_2026-08-14.md`.

## 7. Modern daily row-smoke decision — 15 August 2026

The previously downloaded complete AEMO development ZIPs are no longer locally available and were never covered
by a verified R2 raw-object manifest. Do not treat their result summaries as recoverable input data. This is a
retention-process gap, not permission to rerun the consumed held-out months.

The free official alternative is a mechanically selected non-target daily sample for 16 June 2026:
`BID_MOVE_COMPLETE` (9,095,887 bytes), `NEXT_DAY_DISPATCH` (8,611,556 bytes) and June
`DUDETAILSUMMARY` (378,528 bytes). Total compressed acquisition is 18,085,971 bytes. The exact manifest requires
one GET per object, no replacement, exact-size/SHA verification and immutable R2 retention before any ZIP/CSV
access. At freeze, no selected row had been opened.

This preserves `NO_BUY_NOW`: the experiment is free and CPU-only. It tests modern parser, time, key and join
conformance, not raw submission/rejection provenance, historical comparability or policy effects. Full source
inventory: `papers/proposal/v14_aemo_row_conformance_source_inventory_2026-08-15.md`.

### Executed result

All 18,085,971 exact bytes were downloaded once and verified under the frozen R2 prefix before parsing. Five
schemas, timestamps, primary keys and all non-direction joins passed, but the overall smoke failed: 43,200 of
592,560 `DISPATCHOFFERTRK` rows had multiple period-bid direction matches (`7.2904% > 5%`). The public data are
sufficient to investigate a three-table direction bridge at zero purchase cost, but the current two-table bridge
is not admissible for reconstructing unique applied actions. `NO_BUY_NOW` remains unchanged.

The post-hoc retained-day diagnostic found an exact bundle structure rather than arbitrary multiplicity: every
ambiguous relation was one `{GEN, LOAD}` pair for an effective BDU, across energy and regulation FCAS only. This
supports one additional free daily confirmation sample under a new frozen E1b relation contract. It does not
justify commercial data, bulk history or model training.

### Frozen E1b acquisition

The fresh confirmation is mechanically selected as 7 July 2026, the first Tuesday of the first complete month
after the June development month. Directory metadata alone identified one `BIDMOVE_COMPLETE`, one
`NEXT_DAY_DISPATCH` and the fresh July `DUDETAILSUMMARY` snapshot: 18,244,129 compressed bytes in total. No ZIP
member or market row was inspected before freeze.

The exact three URLs, byte counts and R2 keys are immutable in
`data/manifests/aemo_bundle_confirmation_v1.yaml`. Acquisition remains free and requires exactly one GET per
object, no replacement, and verified R2 retention before parsing. `NO_BUY_NOW` therefore remains the correct
decision. Even a full E1b pass licenses only design of a limited multi-day development sample; it does not license
a data purchase, bulk panel acquisition, prospective outcome access or model training.

### Executed E1b result

All three exact objects were downloaded once, retained in R2 before parsing and passed CRC/schema checks. E1b then
passed all 25 gates on 594,720 tracker records, including 44,928 exact two-leg BDU bundles. The result confirms the
corrected modern relation on a fresh month without paid data.

`NO_BUY_NOW` remains unchanged. The next data action is not a bulk purchase: first freeze a small, mechanically
sampled within-version multi-day development panel across ordinary days. Its byte budget and dates must be fixed
before acquisition; historical table-version strata require a later, separate protocol. Commercial history and
prospective target data remain behind their original evidence gates.

### Frozen modern stability-panel acquisition

The next free acquisition is bounded to four untouched Tuesdays: 23/30 June and 14/28 July 2026. The mechanical
rule chooses the earliest and latest unaccessed Tuesday in every month with an already retained complete identity
snapshot. August is excluded because its monthly identity archive was not published at freeze.

Eight new daily objects total 70,593,936 compressed bytes. The verified June and July identity objects are reused
from R2 without another AEMO source request, bringing staged bytes to 71,350,764. Every literal URL, filename,
byte count, prior-object hash and R2 key is frozen in
`data/manifests/aemo_bundle_stability_panel_v1.yaml`. This remains free and does not alter `NO_BUY_NOW`.

### Stability-panel v1 acquisition result

All 70,593,936 new bytes were obtained in eight one-shot requests and retained in R2. Both prior identity objects
were also verified/materialized from R2 without a new AEMO request. The subsequent failure occurred before archive
access, so the exact data remain content-blind and reusable only under a newly pushed plumbing-repair protocol.
No additional source acquisition or purchase is justified; `NO_BUY_NOW` remains unchanged.

### Frozen pre-parse repair data path

The repair performs zero AEMO source requests. It freezes all ten existing R2 keys, exact sizes and SHA-256 values
and materializes only those bytes. New acquisition is therefore 0 bytes; staged bytes remain 71,350,764. Any R2
mismatch fails the repair. This is provenance reuse, not a replacement sample, and leaves `NO_BUY_NOW` unchanged.

### Repaired panel result and next data gate

All ten R2 objects re-materialized exactly with zero AEMO requests. Four of four dates then passed the unchanged
relation contract. Modern daily acquisition is now adequate for within-version bridge stability; collecting more
days from the same versions has sharply diminishing value.

Do not buy data or bulk-download more modern days. The next data question is historical portability: identify a
minimal public source combination that supplies the same five logical roles across declared schema regimes, then
freeze a header/time/key bridge before any large historical object is fetched. Raw submission/rejection provenance
and prospective-event data remain separate blockers. `NO_BUY_NOW` remains unchanged.
