# V14 experiment, data and compute audit

**Date:** 2026-08-14

**Decision:** `PLAN_NOT_RUNNABLE_YET`; the question is worth scouting, but neither prospective event currently
passes the public-data and event-clock contract. The current bottleneck is observability and mechanism replay, not
GPU capacity.

## 1. Reviewer-2 verdict

The V14 plan has the right high-level test: models should be judged by forecasts frozen before a real rule change,
not only by reconstruction of the old regime. Its present experiment section is still one level too abstract to
run. Four issues must be repaired before Experiment 156 exists:

1. `C1` cannot be decided by one rank correlation over five model families. The independent units are rule-change
   events, and the flagship contract requires at least two untouched events. Model families are repeated
   measurements within an event, not independent replications.
2. “Exact mechanism” must be demonstrated separately in each domain. CoW publishes executable services and a
   competition endpoint. AEMO publishes bids, dispatch and constraint data, but production NEMDE and its formulation
   are restricted fee-for-service resources. An open `nempy` reconstruction is an audited approximate mechanism,
   not an exact oracle, until replay tolerances pass.
3. The proposed AEMO events are not yet confirmation events. FTA has a current 2026-11-01 clock, but the affected
   SSP/MSATS meter and retail transaction data are not shown to be public. IPRR's original 2027-05-23 dispatch-mode
   date is under an official pause/reset and must not be treated as fixed.
4. The response vector is too broad. Six outcome families multiplied by several horizons invites silent outcome
   selection. Each domain needs one primary proper score over a frozen vector and a short, hierarchical set of
   secondary diagnostics.

The plan should therefore split into a free `G1a` metadata/replay audit, a historical development experiment, and a
later prospective confirmation program. No GPU job is justified until `G1a` passes.

## 2. Revised experimental ladder

| ID | Experiment | Scientific question | Data | Statistical unit | Compute | Gate |
|---|---|---|---|---|---|---|
| E0 | source, licence and clock audit | Is there a legal, versioned action/identity/outcome panel and a fixed intervention time? | schemas, table dictionaries, licences, official status pages; zero target rows | source/table/event | Mac CPU, `<=20` core-h, `<16 GB` RAM | required now |
| E1 | mechanism replay conformance | Can the declared rule engine reproduce recorded allocations/outcomes from recorded actions? | 100--1,000 historical CoW auctions; 1--7 AEMO days sampled before target selection | auction or dispatch interval, clustered by day | `50--300` CPU core-h; optional `<=10` V100-eq h only for learned nuisance models | must pass before M2 |
| E2 | leakage and power calibration | Does the sealed scoring procedure control false positives and distinguish declared effect sizes? | generated nulls plus historical placebo dates | independent event/day blocks, never five-minute rows | `200--1,000` CPU core-h; `0--30` V100-eq h | required before historical replay |
| E3 | historical development replay | Does pre-change fit rank policy prediction, and do M2--M4 improve unseen historical-rule forecasts? | CoW CIP history and one completed AEMO wholesale reform with public DUID/action data | rule event; days/participants nested | `100--300` V100-eq h, `1,000--5,000` CPU core-h, `0.2--1 TB` active storage | development evidence only |
| E4 | prospective forecast freeze | Can code, inputs, models and full predictive distributions be sealed before the event? | only pre-event panel and finalized rule/version | one frozen event package | `50--150` V100-eq h per event, `200--1,000` CPU core-h | turns an event into confirmation |
| E5 | blind post-event scoring | Does historical model selection predict policy fidelity without refitting? | immutable post-event action/outcome shards collected by the frozen contract | event, with horizon and participant nested | mostly CPU; `<=50` V100-eq h for fixed inference | primary result |
| E6 | independent replication | Does the scoped model-order/adaptation conclusion repeat under independent governance? | second untouched system/event | event | same order as E4--E5 | mandatory for flagship claim |

E0--E2 answer whether the project is executable. E3 answers whether the protocol has signal. E4--E6 answer the
paper question. A large E3 result must never be relabeled as prospective evidence.

## 3. Model and scoring specification

### 3.1 Minimal model ladder

- `M0a`: seasonal persistence and local event-study forecast.
- `M0b`: regularized tabular/boosted-tree forecast using only pre-event covariates.
- `M1`: small reduced-form sequence model, initially a TCN or transformer below roughly `5--20M` parameters.
- `M2`: audited mechanism replay plus a frozen action policy.
- `M3`: M2 plus participant-conditioned action adaptation.
- `M4`: M3 plus entry, exit and contribution-share dynamics.
- `M5`: post-event refit and privileged-information bounds, labelled as oracles and excluded from fair rankings.

EcoMD is not an implementation shortcut for M2--M4. The first implementation should be a small sibling package
with typed event, participant, action, rule-version and outcome interfaces.

### 3.2 Frozen forecast object

For each event, declare one primary response vector at horizons such as immediate, 1 day, 1 week and 4 weeks only
when those horizons are scientifically meaningful. Candidate components are:

- participant coverage or participation share;
- concentration/effective number of participants;
- action aggressiveness or solution quality;
- execution/dispatch failure rate; and
- allocative cost, surplus or a domain-specific welfare proxy.

Use a multivariate energy score or another declared strictly proper score as primary. Report marginal CRPS/log
scores as secondary diagnostics. Scaling constants, horizon weights, missingness rules and aggregation must be
estimated from pre-event data and frozen. Do not average heterogeneous metrics after seeing their signs.

### 3.3 Inference

- The independent unit for the flagship conclusion is the event, not a five-minute interval, auction or participant.
- Within an event, use block bootstrap or randomization/placebo inference at the market-day level with participant
  clustering where relevant.
- With only two confirmation events, report paired model loss differences and full uncertainty rather than a
  conventional cross-event significance claim. Strong generalization requires more future events.
- The pre-fit versus policy-loss rank plot is descriptive at small model count. The main inferential object is the
  predeclared loss difference between model capabilities across events.
- Response attribution must show both sequential orders and symmetric/Shapley allocation. Anticipation windows,
  concurrent reforms, weather, outages and demand shocks are exclusion/sensitivity variables, not learned-away
  nuisances.

## 4. Data requirements

### 4.1 Common immutable schema

Every row or event bundle needs:

- `system_id`, `event_id`, UTC timestamp plus native market-clock timestamp;
- rule/specification version and activation interval;
- stable participant ID with an explicit identity-change table;
- primitive action submitted before allocation;
- observable state available at action time;
- allocation/execution outcome, failure code and declared welfare/cost fields;
- entry/exit/registration interval;
- source URL/object key, retrieval time, licence, raw SHA-256 and parser git SHA.

Time splits are strict. Post-event data cannot determine features, scaling, horizon weights, participant filters or
missingness treatment.

### 4.2 CoW development data

Minimum fields:

- auction ID/time, auction orders and tokens;
- solver identity, submitted solutions/ranking, objective/score components;
- winner, settlement transaction, execution success/failure and gas/cost/surplus fields;
- deployed service version and applicable CIP/reward-rule interval.

The public `/api/v2/solver_competition/{auction_id}` endpoint and open service repository make CoW the best E1
mechanism-development domain. Historical CIP outcomes are already known, so CoW currently contributes development,
not confirmation. A future governance change must be registered before results are queried.

Expected scale for a useful historical panel is provisionally `10^5--10^6` auctions and `50--300 GB` compressed,
but this must be measured from a 1,000-auction sample rather than asserted.

### 4.3 AEMO wholesale development data

Minimum public tables:

- `BIDDAYOFFER_D`, `BIDPEROFFER_D` and `DISPATCHOFFERTRK` for actions and applied bid versions;
- `DISPATCHLOAD`, `DISPATCHPRICE`, regional summaries, interconnector and constraint solutions for outcomes/state;
- `DUDETAILSUMMARY`, participant and registration tables for DUID ownership, schedule type, aggregation and
  effective dates;
- weather, outages and concurrent-rule registry for confounding/sensitivity analysis.

Official documentation reports roughly `40--50k` `DISPATCHLOAD` rows and `250k` `DISPATCHOFFERTRK` rows per day.
The official 2025-01 directory metadata gives about `355 MB` compressed for the five core bid/dispatch/identity
files and about `590 MB` after adding price, region, dispatch-constraint, SCADA and network-outage files. The
2024-08 core set is about `350 MB`. A provisional two-to-four-year selected-table budget is therefore `20--100 GB`
compressed and `0.1--0.5 TB` working storage after expansion, immutable raw copies and derived caches. Do not
download full monthly MMSDM bundles. Replace the range with measured per-month manifests before bulk synchronization.

Official 2021-03 and 2021-10 directories contain legacy `PUBLIC_DVD_BIDDAYOFFER` and `PUBLIC_DVD_BIDPEROFFER`
archives even though common tooling reports a bid-table gap. This is not yet proof of semantic continuity: E1 must
inspect headers and data-model versions across the legacy and newer `_D` naming regimes.

Known hazards:

- NEM timestamps are period-ending AEST rather than local daylight-saving time;
- `DUDETAILSUMMARY` can contain retrospective registration corrections;
- public bid-table availability has known gaps in common download tooling between 2021 and 2024 and must be
  checked against raw AEMO archives;
- the public monthly archive, participant next-day files and Data Model tables have distinct delivery/report
  version identities; a table name alone is not a version key;
- 1--23 October 2021 is 5MS without live WDR, while WDR and Data Model v5.1 begin together on 24 October;
  month-level October treatment coding is invalid;
- `DISPATCHMODETIME` becomes observable with `DISPATCH,UNIT_SOLUTION,3` and must be treated as versioned fast-start
  state, while `DISPATCHSUBTYPE` becomes necessary to distinguish WDR loads in
  `PARTICIPANT_REGISTRATION,DUDETAILSUMMARY,5`;
- `BIDOFFERFILETRK.SUBMISSION_METHOD` was declared private and unpopulated within the WDR release timeline; it is
  not a historical legacy-versus-five-minute interface label; and
- the production NEMDE executable and Queue are not open. Historical production input/output/price-setting audit
  files are publicly downloadable by day, but they do not make the exact solver independently runnable. Use
  `nempy` only as an audited approximate replay and quantify target/price/constraint mismatches on E1.

### 4.4 Prospective event status on 2026-08-14

| Candidate | Clock status | Action/identity observability | Current role |
|---|---|---|---|
| GB NESO GC0166 | operational implementation required by 2026-11-05; five units/four lead parties were already in controlled rollout | MDO/MDB revisions are documented; CRA-I015 defines effective-dated identity, but the complete historical extract/terms and submission/default/rejection provenance are not delivered | `G1_PARTIAL_5_OF_10`, not confirmation |
| AEMO FTA Release 2 | official page still schedules 2026-11-01 | core SSP, NMI, meter and MSATS transaction/adoption data appear participant/retail-facing; public affected-panel contract not established | `WATCHLIST`, not confirmation |
| AEMO IPRR dispatch mode | original 2027-05-23 date is subject to an official pause/reset and alternate staged path | wholesale DUID bids/dispatch may eventually be public, but new participant mapping and revised schema/timing are unsettled | `PAUSED_CLOCK`, not confirmation |
| future CoW/Uniswap rule | selector frozen at 2026-08-14 07:00 UTC; no event selected | twelve clauses require actions, identities, null/failures, outcomes, licence and precision before selection | `FROZEN_EMPTY_REGISTRY` |
| ePBS | specification/activation and common pre/post observation remain unsettled | V13 failures remain | monitoring only |

The current plan therefore has zero admitted confirmation events. G1 does not pass. GC0166 is a better public-data
lead than FTA, but a promising endpoint inventory is not an admitted event contract. The frozen on-chain selector
prevents later cherry-picking but does not count as independent replication until its registry selects an event.

The detailed source and purchase decision is
`papers/proposal/v14_data_acquisition_decision_2026-08-14.md`; its machine-readable metadata-only registry is
`data/manifests/economic_world_model_v14_sources.yaml`. Current decision: `NO_BUY_NOW`. Public historical AEMO and
CoW sources are sufficient for E0/E1, while FTA confirmation data require an authorised participant partnership
rather than another aggregate commercial feed.

## 5. Compute requirements

### 5.1 Current no-GPU phase

| Work | CPU/RAM | GPU | Storage |
|---|---|---|---|
| E0 metadata/schema/licence audit | Mac, `<=20` core-h, `<16 GB` | `0` | `<5 GB` documents/metadata |
| E1 1,000-auction + one-day NEM sample and parsers | `50--150` core-h, `32--64 GB` desirable | `0` initially | `<20 GB` initially; raise only from measured manifests |
| mechanism conformance and generated nulls | `100--500` core-h, `32--64 GB` | optional `<=10` V100-eq h | `<200 GB` |

The CPUs on the V100 hosts may run these jobs with CUDA hidden after the data gate and a frozen manifest. Do not
transfer target event outcomes during E0.

### 5.2 Feasibility on current hardware

The current two V100 32 GB cards and one RTX2060 8 GB are sufficient for E2--E3 if models stay below about `20M`
parameters and the data loader streams participant/day shards. A prudent first ceiling is:

- pilot: `4` fair model families × `3` training seeds × `2` development events, `<=150` V100-equivalent hours;
- expanded development: surviving models × `10` seeds, cumulative `<=400` V100-equivalent hours;
- CPU preprocessing/replay: `1,000--5,000` core-hours;
- active storage: `0.2--1 TB`, which exceeds current worker-local free space and therefore requires R2 plus staged
  shards or a dedicated local data disk.

At continuous use, `150` V100-equivalent hours is about `3.1` days on two V100s; `400` hours is about `8.3` days,
before queue and failure margin. The RTX2060 is for smoke/parity only and should not be mixed into confirmatory
timing comparisons.

These are ceilings, not forecasts. Before the pilot, benchmark exactly one M1 and one M3 job on one V100 and record
examples/s, peak memory, epoch time and checkpoint size. Recompute the budget as:

`measured_job_hours × model_configs × training_seeds × events × 1.25 failure_margin`.

### 5.3 Conditional paper-scale budget

If two prospective events eventually pass G1 and historical development passes G2/G3:

- `500--1,500` V100-equivalent GPU-hours for final retraining, ablations, calibration and fixed inference;
- `5,000--30,000` CPU core-hours for replay, block bootstrap, Shapley sensitivity and data validation;
- `2--5 TB` R2 capacity including immutable raw data, Parquet shards, manifests, checkpoints and results;
- current two V100s imply roughly `10--31` continuous GPU-days. Expansion to `4--8` non-H20 GPUs improves calendar
  time but is not scientifically required.

Do not reserve `1,000--4,000` GPU-hours merely because NCS is the target. Increase beyond `1,500` only after a
measured profile shows that seed/model coverage cannot fit the conditional budget. No LLM is needed.

## 6. Immediate work order

1. Correct the V14 plan: FTA becomes `WATCHLIST`; IPRR becomes `PAUSED_CLOCK`; G1 is explicitly failed/not passed.
2. Maintain the metadata-only source registry and create the event-contract table. Do not download target outcomes.
3. Ask AEMO or verify official documentation for public access to SSP/NMISP adoption, participant mapping and IPRR
   revised timing/schema. If affected-level data are private, retire FTA/IPRR as confirmation events.
4. Preserve the failed initial CoW and AEMO schema audits; do not replace 404 IDs or reinterpret archive file names
   as internal MMS table identities.
5. Preserve the failed held-out AEMO crosswalk, resolve its `OFFER`/`BIDS` transition from official version records,
   and freeze an outcome-blind CoW competition enumerator before selecting any further sample.
6. Replace the underpowered 48-block E2 design only through a new power protocol with a scientifically justified
   independent-block count and fresh root seed; do not inflate five-minute rows into independent events.
7. Only after the repaired E1/E2 gates pass, benchmark one small M1/M3 job on a single V100.
8. Search continuously for a second independently governed future mechanism change. Without two admitted events,
   pursue a specialist benchmark or stop rather than manufacture a Nature narrative.

## 7. Free-data execution checkpoint

The first outcome-blind development package was executed on 2026-08-14 and failed all three promotion decisions:

- generated calibration controlled the null false-positive rate at 5.8%, but power was 38.6% and correct-clock
  selection was 56.0%; the frozen 48-independent-block design is underpowered;
- the exact CoW ledger retained all 100 requests and parsed all 33 available responses, but arithmetic auction-ID
  sampling achieved only 33% HTTP-200 coverage; no 404 was replaced and the 1,000-ID expansion stays locked; and
- all ten exact AEMO objects downloaded with correct size, SHA-256, one CSV member and passing CRC. They occupy
  1.178 GB compressed and 31.879 GB uncompressed, but only 5/10 matched the frozen internal-table identity and
  9/10 contained the frozen minimum fields. No data row was counted or joined.

The AEMO failure exposes a real cross-version mapping problem: archive names `DISPATCHOFFERTRK` and `DISPATCHLOAD`
contain internal tables `OFFERTRK` and `UNIT_SOLUTION`, while the legacy per-period bid table is
`OFFER/BIDOFFERPERIOD` with `TRADINGDATE` rather than the current `BID/BIDPEROFFER_D` contract. A new field-level
crosswalk must be learned from these discovery months and tested on unopened months. The run used a V100 host only
as a CPU/data node with CUDA hidden; no GPU model job was opened.

That held-out test was subsequently frozen and executed on 2021-09 and 2025-07. It downloaded 1.557 GB compressed
(43.677 GB uncompressed) and passed all ten byte, hash, CRC, internal-table and required-source-field projections.
It nevertheless failed the preregistered total gate: both 2021-09 bid objects use package `BIDS`, not the discovery-
derived `OFFER`, so package and overall header pass rates were 8/10. AEMO's official 5MS records show that September
lies inside the 1 April--30 September bidding transition, when legacy 30-minute and new 5-minute paths coexisted;
the v5.00 specification formally replaces the relevant `OFFER` records with `BIDS` records. This is a staged
mechanism/action-space transition, not a safe namespace alias. Row filtering remains locked.

Official Data Model v5.00 records and the March SQLLoader control further separate the observation clock from the
rule clock. Emulated reporting entered production on 8 March; the March period control loads the new-shaped export
into legacy `BIDPEROFFER` while discarding new-only clock/ramp columns. Bidding transition began on 1 April and the
rule commenced on 1 October. A frozen endpoint test then passed 6/6 untouched controls from 2020-09 and 2022-04,
  using only 9,978 downloaded metadata bytes. No CSV/ZIP, row, remote node or GPU was used.

A separately frozen range-prefix audit then requested exactly 256 KiB from each of ten endpoint archives. All ten
HTTP 206, ZIP-prefix parser, member, package, table and required-field checks passed, but the total header gate
failed at 7/10 because three exact versions advanced or differed. It transferred 2,409,220 bytes, opened no `D`
row, but a later `Content-Range` audit found that two small identity archives were transferred in full. The
original collector's full-download flag was hard-coded and wrong. This is both a source-version ontology failure
and a transfer-guard failure, not a compute failure.

The official follow-up classifies those failures rather than relaxing them. `BIDPEROFFER` v2 was inferred from a
`NEXT_DAY_OFFER_*` contract and does not document the observed `PUBLIC_DVD` channel. `UNIT_SOLUTION` v3 adds
fast-start dynamic state; `DUDETAILSUMMARY` v5 adds WDR identity. Data Model v5.1 and WDR both went live on
24 October 2021, so this boundary mixes a real mechanism with new observation fields. The repaired contract must
key every version by delivery channel/archive family and effective interval, separate 1--23 October from
24 October onward, and retain unknown bid-interface provenance. Audit:
`papers/proposal/v14_aemo_source_version_and_clustered_reform_audit_2026-08-14.md`.

The repaired channel-keyed contract was frozen at `39c45dddf` and run once on mechanically selected 2021-02 and
2021-11. Every one of the ten header, version and required/forbidden-field contracts passed. The overall gate again
failed because the 256 KiB request transferred both smaller `DUDETAILSUMMARY` objects completely. Total transfer
was 2,409,465 bytes; no `D` row was parsed, no GPU or paid data was used, and no object will be rerun or replaced.
The source matrix is empirically supported at header level, but row access remains locked behind a smaller-range
protocol with automatic complete-object detection.

That repair was frozen at `23c847de0` and passed once on untouched 2021-01/2021-12: all ten responses were exact
64 KiB partial transfers, all ten scientific headers passed, and no complete object or `D` row was opened. The
metadata transport problem is closed. Row timestamp/key/join semantics remain open; the 1.610 GB declared size of
the 2021-12 bid-period object rules out an indiscriminate full-month conformance download.

## 8. Bottom line

- **Experiment plan:** scientifically sensible, operationally incomplete; E0/E1 must precede model training.
- **Data:** rich free AEMO wholesale and CoW development data exist, but current prospective confirmation data do
  not pass. FTA is probably too retail-private; IPRR's date is reset.
- **Compute:** current GPUs are enough for feasibility and likely enough for a carefully scoped paper. CPU, storage
  and event availability matter more. No compute expansion is justified now.
- **Current action:** inventory already consumed local AEMO artifacts and exact official daily alternatives, then
  design—but do not yet execute—a minimal timestamp/key/join conformance protocol; separately obtain an
  outcome-blind CoW enumerator. Do not open new rows, train models, open target outcomes or buy data.

## 9. AEMO modern row-conformance resource checkpoint — 15 August 2026

The inventory is complete. Earlier full development ZIPs are absent and lack verified R2 retention, so they will
not be reused or silently reacquired. The frozen replacement is a non-target, modern one-day *conformance* smoke,
not a replacement result: three official objects, 18,085,971 compressed bytes, five tables and a hard 4,000,000
MMSDM-row cap.

Required work is exact download/hash verification, R2 retention, ZIP CRC, schema/time/key validation and four
joins. Expected compute is minutes of Mac CPU time and less than about 1.11 GB maximum uncompressed working data.
Required GPU-hours are zero; both V100s and the RTX 2060 remain idle. Required paid data and purchased storage are
zero. A pass unlocks only the design of a multi-day historical development protocol, not model training or a
prospective claim. See `experiments/v14_aemo_row_conformance/PREREGISTRATION.md`.

### Executed result and next compute gate

The one-day smoke used 18.1 MB compressed input and CPU only. Eighteen of nineteen gates passed; the unique-action
bridge failed because 7.2904% of applied-offer tracker rows had more than one direction candidate. This failure is
preserved and does not unlock the proposed multi-day E1 panel or any GPU training.

The next diagnostic still needs zero GPU-hours, no new purchase and no new source data: inspect official
`DISPATCHLOAD` direction semantics and characterize the ambiguity on the already-retained development day. If a
principled three-table bridge exists, confirmation requires one fresh frozen daily sample. V100/RTX 2060 resources
stay idle until the corrected E1 gate passes.

The post-hoc diagnostic supports a precise correction: all 43,200 ambiguous relations were complete two-leg
`{GEN, LOAD}` bundles for effective bidirectional units, restricted to energy and regulation FCAS. No dispatch
sign selector is admissible. The next E1b confirmation remains a small CPU/data job on one fresh day; model/GPU
work stays locked.

### Frozen E1b resource contract

E1b uses the mechanically selected 7 July 2026 daily pair plus the July identity snapshot: 18,244,129 compressed
bytes, at most 1,107,296,256 uncompressed bytes and at most 4,000,000 MMSDM data rows. Required compute is local
CPU only and expected runtime is minutes. Required V100/RTX 2060 hours, paid-data budget, purchased storage and
remote-worker capacity are all zero.

The 25 frozen gates cover exact acquisition/R2 retention, archive integrity, schemas, timestamps, primary keys,
base joins and the prospective one-or-exact-`{GEN, LOAD}` relation. The GPUs remain idle regardless of E1b outcome.
A pass unlocks only a new protocol for a limited multi-day development panel; a failure ends this bridge attempt
unless a genuinely new, independently frozen source contract is justified.

### Executed E1b compute result

E1b passed 25/25 gates on 1,422,918 target rows and 4,559,065 contracted timestamps using local CPU only. It used
18,244,129 compressed bytes, no paid data, no remote worker and zero GPU-hours. There is therefore no evidence for
GPU expansion or even current V100/RTX 2060 use at this stage.

The next compute estimate must be derived from a frozen multi-day sample count and these measured row/runtime
characteristics. That next step remains CPU/data engineering. Model training and Experiment 156 stay locked until
the observation bridge is shown stable across the limited within-version panel, historical portability is treated
separately and a model protocol is preregistered.

### Frozen four-day panel budget

The modern stability panel adds 70.6 MB of public daily ZIPs and stages 71.4 MB after verified identity reuse.
Each date retains the existing caps of 4,000,000 MMSDM rows and about 1.11 GB uncompressed input; days must be
processed sequentially, with a 16,000,000-row and 4.43 GB cumulative ceiling. Expected work is several minutes of
local CPU plus R2 transfer.

Required GPU-hours remain zero. Neither V100 nor RTX 2060 should be queued, and no compute expansion is justified.
All four dates must independently pass the 25 E1b gates before a historical-version protocol is designed.

### Stability-panel v1 execution failure

Acquisition and R2 materialization passed, but the analyzer stopped before the first ZIP open because the derived
day manifest lacked `resource_contract`. No row computation, GPU or scientific evaluation occurred. A minimal
repair remains local CPU work and must use the retained bytes with zero new source requests. Compute requirements
and all model/GPU locks are unchanged.

### Frozen repair compute budget

The repair adds one parser-entry preflight and the missing per-day row cap, then runs the same sequential CPU
analysis on R2-materialized bytes. New source transfer is zero; maximum staged/computation budgets are unchanged.
Twenty-eight combined AEMO tests pass before execution. Required GPU-hours and paid-data spend remain zero.

### Repaired panel compute result

The four sequential CPU analyses passed on 5,697,359 target rows and 18,255,035 contracted timestamps. No GPU,
remote worker, paid data or model run was used. More same-version sampling is not compute-efficient: the next work
is historical schema/source reconnaissance and small CPU preflights. V100/RTX 2060 queues remain empty until a
separate model experiment is scientifically unlocked.

### Frozen historical reachability budget

The next preflight transfers exactly two 64 MiB compressed prefixes and retains 128 MiB in existing R2. It streams
at most 1 GiB uncompressed per object, stores only counts/date blocks in memory and runs sequentially on local CPU.
Expected GPU-hours, paid-data spend and remote-worker requirements are zero. A pass triggers protocol design, not
training; V100 and RTX 2060 queues remain empty.

### Historical reachability compute result

The CPU parser processed 15,505,469 rows and hit both 1 GiB uncompressed caps while retaining only aggregate date
counts. It used 128 MiB of R2-backed compressed input, no GPU, remote worker or paid data. The scientific decision
failed because dates were not contiguous, not because of inadequate compute. Adding CPU/GPU capacity cannot repair
that source-layout failure; the next work is a source/provenance audit. GPU queues remain empty.

### CoW HEAD-enumeration compute checkpoint

The previous 33/100 CoW result has been reclassified as a shared-ID-space sampling failure, not 33% retention.
The repair first sends exactly 384 HEAD requests at at most one request per second, retaining only status and zero
body bytes. Expected wall time is about 6.5 minutes plus bounded retries; memory and storage are negligible. It
uses zero GPU-hours, no paid data and no remote worker.

At least 100 HTTP-200 IDs and complete 200/404 terminal coverage are required. Only a passing, committed resolved
ID list can unlock a separately frozen payload and score-replay audit. V100 and RTX 2060 queues remain empty.

### CoW HEAD-enumeration result

The run used about 6.5 minutes of local CPU/network time and returned 93 HTTP 200 plus 291 HTTP 404 statuses. All
integrity gates passed, but the eligible-count gate failed by seven. No GET, GPU, remote worker or paid data was
used, and no payload experiment is queued. Additional compute cannot repair the sealed sampling decision; use an
official list/snapshot or move exact-mechanism development to a fully indexed on-chain system.

### Uniswap v3 U0 treatment-conformance checkpoint

The next free exact-M2 gate is a mechanism-only Uniswap v3 Proposal 94 conformance run. Its sealed input consists
of chain ID and deployed code plus one governance and two propagation transaction/receipt/block triples: 11
read-only Ethereum RPC calls in total, capped at one request per second with two transport retries. Expected
retained volume is below 20 MB and expected local compute is under one CPU core-hour.

Required paid-data spend, remote workers and GPU-hours are zero. Both V100s and the RTX 2060 remain idle; H20 is
excluded. The run may retain exact treatment transitions but cannot open LP actions, swaps, liquidity, price,
volume or any post-treatment response. Only a passing, committed U0 result can unlock design—not execution—of a
separately frozen pre-treatment U1 identity/support audit. Model training and GPU allocation remain locked.

### Uniswap v3 U0 v1 transport result and v2 budget

V1 used one successful `eth_chainId` call and three failed HTTP-403 historical-code attempts, then stopped before
any governance or propagation receipt. No artifact, fee transition or market response was produced. This was an
RPC capability failure; more CPU/GPU cannot repair it.

V2 retains the same 11-successful-call ceiling and all data/compute locks, changing only the provenance code query
to `latest`. Its expected retained volume remains below 20 MB and local work below one CPU core-hour. Paid-data,
remote-worker and GPU budgets remain zero; the V100s and RTX 2060 stay idle. If the sealed v2 transport fails,
there is no within-protocol endpoint substitution.

### Uniswap v3 U0 v2 compute result

V2 completed exactly 11 successful read-only RPC calls, all on one attempt, and retained about 482 KiB of
normalized treatment rows plus about 9 KiB of summary/provenance metadata. It reconstructed 1,000 unique pool
transitions and passed all frozen U0 gates. No raw RPC envelope, LP response, paid data, remote worker or GPU was
used.

Additional compute is not the next bottleneck. U1 is a CPU/network-only, pre-treatment data-coverage design and
must first benchmark log volume and identity mapping before any larger acquisition. Both V100s and the RTX 2060
remain idle; no model queue is authorized. The absence of within-frame controls is an identification issue, not a
reason to allocate more compute.

### Uniswap v3 U1a frozen resource budget

U1a is a 16-pool, 50,400-block preperiod-only audit. The unsaturated expected path is roughly 259 successful HTTP
responses: 64 pool/event log queries, three chain/header calls, and at most 64 each of transaction, transaction-log
and token-transfer-history queries. Exactly-1,000-log responses add deterministic block bisections. Hard ceilings
are 2,000 HTTP attempts, 128 MiB response bytes and 250,000 normalized pool events.

Only counts, manager addresses, selected transaction senders, NPM token IDs, bounded transfer histories and
response hashes are retained. Amount/price/liquidity fields and all post-treatment events remain undecoded. The
run needs local CPU/network and under one core-hour in the expected path. Paid data, remote workers and GPU-hours
remain zero; both V100s and the RTX 2060 stay idle. A pass does not itself justify compute expansion.

### Uniswap v3 U1a compute result

U1a used 75 successful one-attempt HTTP responses and 405,836 response bytes. All 64 base pool/event queries were
unsaturated; only three transaction-log pages and two token-transfer queries were needed because the sample had
six position actions. The run used local CPU/network, zero paid data, zero remote workers and zero GPU-hours.

The failure is support/identification, not compute: 3/16 pools were swap-active, 1/16 position-active and only
three identity transactions existed. More GPU cannot repair this. The V100/RTX 2060 queues remain empty. A future
full-population preperiod census, if separately justified, is still CPU/network work and must be budgeted before
launch; post-treatment acquisition and model training remain unauthorized.

### Uniswap v3 U1R full-population census budget

U1R is now frozen as a new full-population development estimand, not a top-up of failed U1a. It queries each of
the exact 1,000 U0 pools once over the same 50,400-block preperiod using four topic-0 values in one request. Three
chain/header calls make the expected unsaturated path 1,003 successful responses. At the frozen two requests per
second this is about 8.4 minutes plus deterministic interval splits and transport overhead.

Hard ceilings are 5,000 HTTP attempts, 512 MiB response bytes and 1,000,000 normalized events. Raw payloads,
decoded amounts/prices/liquidity, non-NPM manager addresses, identity histories, controls and post-treatment data
are not retained. Expected local work remains under one CPU core-hour with negligible durable storage. Paid-data,
remote-worker and GPU requirements are zero; both V100s and the RTX 2060 remain idle, and H20 is excluded. A pass
can unlock only separate control/identity protocol design, not acquisition or training.

### Uniswap v3 U1R compute result

U1R completed in about 9.2 minutes between its first and final recorded responses. It used 1,009 successful
one-attempt requests and 10,463,695 response bytes: three chain/header calls, 1,000 base pool calls and six child
calls for one saturated pool. It normalized 9,075 events and retained about 1.8 MiB across the census, response-
hash manifest and summary.

The run failed only the predeclared swap-count concentration gate, not a compute or transport gate. Additional
CPU/GPU cannot repair the decision, and excluding the dominant pool post hoc is prohibited. Paid-data spend,
remote-worker use and GPU-hours were zero. Both V100s and the RTX 2060 remain idle; no Uniswap response/model job
is queued.

### Exposure-routing exploratory budget

The post-U1R routing description rereads only the committed 1,000-row census. It performs sorting and scalar
reductions for three count channels and four fixed partitions, writes one small JSON summary and makes zero
network requests. Expected work is seconds on one local CPU core with negligible memory/storage.

This is explicitly post hoc and has no gate; more compute cannot increase its evidential status. Paid data,
remote workers and GPU-hours are zero. V100/RTX 2060 queues remain empty, and no response/model access is
authorized by the output.

### Exposure-routing exploratory compute result

The clean committed run completed in about one second on local CPU and wrote one small JSON artifact. Independent
scalar recomputation reproduced HHI, effective count, top-10 share, total variation, fee/batch totals and the
aggregation identity to floating-point precision.

No network, new data, paid service, remote worker or GPU was used. The output is architectural description only;
V100/RTX 2060 queues remain empty until a new M3/M4 source and identification gate pass.

### M3/M4 source-selection and Compound metadata budget — 16 August 2026

The cross-domain scorecard uses official documentation and versioned source metadata only. It opens zero chain,
account, participant-action or realized-response rows and requires no purchase, remote worker or GPU. Compound III
ranks first for a bounded metadata preflight because its address-level position state may provide an ex ante
exposure denominator and explicit successful-adjustment null; it is not G1-admitted.

The frozen preflight reads one clean official Git checkout at commit
`f766f51583c23acc33b2a7824654ef2029a96804`: six mainnet configuration/root pairs, migration filenames,
three contract-source files and LICENSE. Expected runtime is seconds on local CPU and durable output is one small
JSON artifact. Required V100, RTX 2060 and H20 hours are zero; the GPU queues remain empty. A pass can unlock only
chain deployment/code/configuration and archive-provider *metadata* design under a new freeze. Account-state,
action, price, liquidation, response and model work remain locked.

### Compound metadata v1 runner failure and v2 budget

V1 used seconds of local CPU for nine passing tests, then failed at the direct-script import before reading the
manifest or any Compound source file. No artifact, network request, chain row, paid data, remote worker or GPU was
used. The sparse-materialization setup and import-path failure do not change the scientific resource estimate.

V2 invokes the same committed collector as a package module. It retains the seconds-scale local CPU budget, one
small JSON output, zero network/RPC and zero GPU-hours. No compute worker should be queued for this repair.

### Compound source-metadata v2 compute result

V2 completed in about one second on local CPU and wrote an 11,318-byte artifact. It audited 16 official source
files, six mainnet market pairs, 22 collateral configurations and 56 migration filenames. Nine gates and all
independent file-hash checks passed. It used no network/RPC, paid data, remote worker or GPU.

The next bottleneck is on-chain deployment/archive provenance and control design, not compute. A separately frozen
metadata-only RPC audit will need only tens to low hundreds of read calls and local CPU. Do not queue either V100
or the RTX 2060; account/action/response data and model training remain unauthorized.

### Frozen Compound chain-metadata budget

The next audit permits exactly 61 public Ethereum metadata calls at at most two requests per second: finalized and
fixed historical headers, proxy/implementation code, ERC-1967 implementation/admin slots and four non-account
configuration getters. Hard ceilings are 80 HTTP attempts and 8 MiB response bytes. Raw bodies and code are
discarded after hashing and bounded decoding.

Expected runtime is about 31 seconds plus local parsing; durable output is two small JSON files. Required paid
data, remote workers and GPU-hours are zero. Neither V100 nor RTX 2060 should be queued. Even a pass unlocks only
the design of an account-exposure/control protocol, not its execution.

### Compound chain-metadata v1 endpoint failure and v2 budget

V1 made one successful chain-ID call, then used its three allowed attempts on an unsupported `finalized` header
tag and stopped before all contract and historical calls. It created no artifact and used no paid data, remote
worker or GPU. Additional compute cannot repair an endpoint method/tag capability mismatch.

V2 keeps the endpoint and caps but adds one header call: latest head, explicit `head - 64` snapshot and fixed
historical block yield exactly 62 successful calls on the expected path. Runtime remains about 31 seconds at two
requests per second, retained output remains two small JSON files and the hard limits remain 80 HTTP attempts and
8 MiB. The 64-block lag is not consensus finality. Required V100, RTX 2060 and paid-data budgets remain zero;
the GPU queues stay empty even after a pass because only exposure/control protocol design could be unlocked.

### Compound chain-metadata v2 compute result

V2 completed 62/62 one-attempt metadata calls in 36.18 seconds and transferred 418,232 response bytes. Its two
artifacts total 51,854 bytes. All twelve gates and an independent structural/hash verification passed. The run used
local CPU/network only, zero paid data, zero remote-worker time and zero GPU-hours.

This removes deployment/archive metadata as the immediate bottleneck but does not create a compute queue. Exposure
denominator, shared-authority controls, finality replication and retention/licence must be solved in a zero-row
design before any account acquisition. Neither V100 nor RTX 2060 is queued; no training job is authorized.

### Compound zero-row exposure/control design budget

The machine-checked design, exact residual identity and 21-test relevant suite use seconds of local CPU, negligible
storage, no chain request and zero GPU. It opens no governance payload, account, action, trace, liquidation, price
or response row.

The next D0 governance-metadata protocol is expected to remain a small CPU/network inventory, but its exact calls
and bytes must be frozen before execution. D1 exposure cost is not yet authorized: it scales with deployment-to-
event logs, unique candidate accounts and active collateral assets, and first needs a count-only budget. Complete
M3 additionally requires historical successful call traces; if no free reproducible source exists, the resource
choice is a terms-reviewed provider or a self-managed archive/trace index with substantial SSD and CPU/RAM. This is
not GPU work. Both V100s and the RTX 2060 remain idle through D2.

### Frozen Compound D0 governance-log inventory budget

D0 scans a fixed 11,760,573-block window through 48 inclusive root partitions at one Configurator and six Comet
proxy addresses. The expected unsaturated path is 339 public RPC calls: chain ID, two fixed headers and 336 log
queries. Exactly 1,000 returned logs trigger deterministic recursive bisection. Hard ceilings are 2,000 HTTP
attempts, 256 MiB of response bytes and 100,000 normalized logs at two requests per second.

Expected wall time is about three minutes plus parsing, with small JSON outputs. It uses local CPU/network, zero
paid data, zero remote-worker time and zero GPU-hours. No V100 or RTX 2060 job is queued. Even a pass unlocks only
a separately frozen all-candidate receipt/payload/call-path/finality preflight; D1 account acquisition and all
model training remain unauthorized.

### Compound D0 governance-log compute result

D0 completed the exact 339-call unsaturated path in about 188.9 seconds. All calls succeeded on their first
attempt; total response traffic was 605,863 bytes. It normalized 886 public governance/configuration logs and wrote
about 1.1 MiB across the summary, inventory and response-hash ledger. No raw RPC body was retained.

The pass yields 14 provisional log-level candidates but does not create a GPU queue. The next receipt/payload/
getter/finality preflight is still a small CPU/network task over all 14 candidates and must be separately budgeted
and frozen. Paid-data, remote-worker and GPU use were zero; both V100s and the RTX 2060 remain idle. Account
acquisition, trace-scale indexing and model training remain unauthorized.

### Frozen Compound D0b all-candidate mechanics budget

D0b fixes 187 JSON-RPC calls and one Beacon REST request over all 14 provisional candidates. The method vector is
32 headers, 14 each of transaction/receipt/call trace, 56 proxy-slot reads, 28 implementation-code reads, 28
asset-info calls and one chain ID. The full ordered provider/method/parameter vector is a runtime gate. At one
operation per second, the mechanical lower bound is about 3.2 minutes; the runbook budgets up to 15 minutes for
callTracer latency.

Hard ceilings are 600 HTTP attempts, 256 MiB of responses, 200,000 normalized call nodes, 64 MiB of retained
governance-call inputs and 100,000 receipt logs. Raw response envelopes, code and trace outputs are discarded after
normalization/hashing. Expected durable output is small to moderate JSON, depending on governance call-tree size.

This is CPU/network work only. Paid data, remote workers and GPU-hours remain zero; both V100s and the RTX 2060
stay idle. A pass permits only D1 exposure-count/cost protocol design, not account collection or training.

### Compound D0b v1 actual resource result

V1 stopped after about 15.2 seconds at the first candidate's trace request. Ten earlier logical operations
completed; PublicNode then returned `-32601` for each of three allowed `debug_traceTransaction` attempts. No trace,
slot, code, getter, later candidate or participant/response request succeeded. No durable artifact was emitted, so
response bytes and prior retry counts are unavailable rather than estimated. Actual paid-data, remote-worker and
GPU use remained zero. This infrastructure failure unlocks no D1 work.

### Frozen Compound D0b v2 transport-repair budget

V2 preserves the 188-operation lower bound but changes its composition to 173 JSON-RPC calls, 14 Blockscout
raw-trace REST calls and one Beacon REST request. At the unchanged global rate of one operation per second, the
mechanical lower bound remains about 3.2 minutes; the runbook still budgets 15 minutes. Existing hard caps remain
600 HTTP attempts, 256 MiB total responses, 200,000 flat trace nodes, 64 MiB trace inputs and 100,000 receipt logs.

The successful path writes summary, candidates and a bounded HTTP evidence ledger. Any caught collection exception
writes only a failure artifact with all successful-operation hashes and every attempt outcome/hash; raw response
bodies are never retained. V2 uses only local CPU and public network access. Paid data, remote-worker hours and GPU
hours are zero; the two V100s and RTX 2060 remain idle. D1 and model training are still unauthorized.

### Compound D0b v2 actual resource result

The one sealed run completed all 188 logical operations in 191 HTTP attempts. Three transient HTTP 500 responses
succeeded on the next attempt. The response ledger spans 240.472 seconds and accounts for 3,711,152 bytes, 599
normalized trace nodes, 532,327 trace-input bytes and 129 receipt logs. All 12 gates passed and four candidates
survived. Actual paid-data, remote-worker and GPU use was zero.

The next authorized work is protocol design, not an account-scale census. Because every survivor is a supply-cap
increase, first budget a four-candidate aggregate cap-activation/estimand preflight using fixed historical getters
only. This remains tens of RPC calls, seconds-to-minutes of CPU/network, and zero GPU. Account enumeration, action
traces and response construction remain unbudgeted and locked until that gate is frozen and passes.

### Frozen Compound D1a supply-cap activation budget

D1a is now exactly budgeted at 141 successful no-retry operations: 134 JSON-RPC calls and seven Blockscout
verified-source REST calls. The RPC vector contains two chain IDs, eight historical implementation-code reads, 24
pre-event headers and 100 fixed configuration/aggregate calls. It covers four mechanics survivors and six
pre-event block offsets per survivor, with both providers reproducing each contemporaneous cap and aggregate
collateral total.

The global throttle is one operation per second, so the mechanical lower bound is 2.35 minutes; the runbook budgets
15 minutes for source payload and provider latency. Hard ceilings are 512 HTTP attempts, 128 MiB of responses,
2,048 verified-source files and 64 MiB of decoded source text. Raw source/RPC bodies are discarded after bounded
normalization and hashing. Expected durable output is small JSON containing source inventories, state snapshots
and the attempt ledger.

This remains local CPU/network work with zero paid data, remote-worker hours and GPU-hours. Both V100s and the RTX
2060 stay idle. The protocol forbids accounts, actions, logs/traces, prices, liquidations, post-event aggregate
state and realized responses. Even an exact-saturation pass budgets only a separate market-level D1b design; no
participant-data or training job is queued.

### Compound D1a v1 actual resource result

V1 stopped after 14.878 seconds. Nine logical operations succeeded—two chain IDs and seven Blockscout source-
metadata GETs—before PublicNode returned HTTP 403 on all three allowed attempts for the first historical
`eth_getCode`. The failure ledger contains 12 attempts and 1,370,203 response bytes. Only `failure.json` exists;
the three success artifacts are absent.

No historical code result, configuration getter, aggregate total or participant/response row was opened. Actual
paid-data, external-worker and GPU use was zero. Extra GPU capacity cannot repair this endpoint capability. Any v2
budget must remain CPU/network-only and freeze a documented historical-state transport before another candidate
request; D1b and training remain unqueued.

### Frozen Compound D1a v2 transport-repair budget

V2 contains 105 successful no-retry operations: 98 RPC and seven verified-source REST calls. Its RPC vector is two
chain IDs, 48 historical headers and 48 Blockscout historical state calls. PublicNode supplies only one chain ID
and 24 headers; it performs no archive-state method. Both providers reproduce every lookback header, while
Blockscout alone supplies configuration and aggregate state.

The one-request-per-second lower bound is 1.75 minutes, with the same 15-minute runbook budget. Caps are 384 HTTP
attempts, 128 MiB responses, 2,048 source files and 64 MiB normalized source text. A failure now retains completed
normalized source/candidate evidence plus the full hash ledger, never raw payloads and never a partial scientific
decision.

This is again free local CPU/network work with zero remote workers and GPU-hours. Both V100s and the RTX 2060 stay
idle. The weaker single-provider historical-state provenance is a scientific limitation, not a compute need; a
later confirmatory study would require independent archive state or verified state proofs.

### Compound D1a v2 actual resource result

The sole sealed run completed all 105 logical operations in exactly 105 HTTP attempts: 98 JSON-RPC calls and seven
verified-source REST reads. It transferred 1,961,938 response bytes over 107.202 seconds between the first and last
recorded response. Seven source implementations, four candidates, 24 two-provider historical-header pairs and 48
Blockscout historical state calls all conformed; all ten integrity gates passed.

Actual paid-data, external-worker and GPU consumption was zero. Both V100s and the RTX 2060 remained idle. No
account, action, trace, price, liquidation, post-event aggregate or realized-response row was opened. Because none
of the four candidates was exactly saturated at T−1, the frozen decision retires the Compound M3 causal route.
Consequently no Compound D1b, participant census or training budget exists. The next budget may cover only a new
source's zero-row identification/source audit; GPU allocation remains locked until that route independently
passes its data and identification gates.

### Frozen Aave A0 source/effect budget

A0 reads exactly fourteen files from one clean partial checkout of official Aave V3.7 source commit
`cff15de6d1271b0c800fc001f4aea4c263e8a597`. It performs no API or chain call. The durable artifact contains file
paths, byte counts and hashes, normalized marker booleans, twelve gate booleans and small deterministic effect
self-checks; it retains no raw source body. The expected local audit runtime is under one minute, with well below
100 MiB of checkout and artifact data.

Actual pre-run requirements are one Mac CPU core, free GitHub source, zero paid data, zero external-worker time and
zero GPU-hours. The two V100 workers and RTX 2060 remain idle and unqueued; H20 is excluded. Even an A0 pass only
budgets the **design** of an Ethereum deployment/version and strict LT-decrease event inventory. Chain scanning,
account reconstruction, action/response collection and training have no budget until separately frozen gates pass.

### Aave A0 actual resource result

The one sealed audit read fourteen already-staged source files totaling 197,890 bytes and wrote one 15,589-byte
summary. It made no network, API or chain call during the audit and used local CPU only. An independent verifier
re-read all raw files and reproduced 63 marker checks, file/inventory hashes, five integer identity checks and all
twelve gates. Actual paid-data, external-worker and GPU use was zero; both V100s and the RTX 2060 remained idle.

The frozen reconnaissance disclosure's 197,858 count was Unicode characters, not UTF-8 bytes; this accounting
correction changes no source content or resource conclusion. A1 currently has a **design-only** budget. No chain
request, account-scale storage, remote CPU or GPU allocation exists until the deployment/event protocol freezes.

### Frozen Aave A1a zero-account directory budget

A1a now freezes 312 root log reads: 104 inclusive 250,000-block intervals for the PoolAddressesProvider, the
PoolConfigurator proxy and Pool-proxy upgrades. Two providers each supply chain ID and start/end headers (six
calls). Blockscout then supplies three terminal provider getters, two ERC-1967 slots and code for the provider,
two proxies and every unique implementation derived from the complete histories. With no saturated root, the
successful request count is `326 + N_impl`; `N_impl` is response-derived but the sorted request rule and 128-address
cap are fixed ex ante.

Hard caps are 2,000 HTTP attempts, 256 MiB responses, 100,000 normalized logs and two requests/s. Expected local
wall time is three to five minutes; durable JSON should be small. Raw RPC bodies are hashed then discarded.
PublicNode does not receive a historical state request: prior evidence already restricts its free use to header
replication, while Blockscout supplies fixed-block getters/slots/code. This is a stated single-provider state
limitation, not a reason to retry a known-incompatible method.

No historical per-event configuration, transaction, receipt, payload, trace, account, participant action,
liquidation, price value or response is budgeted. Paid data, external workers and GPU-hours are zero. Both V100s
and the RTX 2060 remain idle; H20 is excluded. Even a pass budgets only a separately frozen all-candidate A1b
mechanics/source protocol.

### Aave A1a actual resource result

The sole sealed run completed 344 successful requests in 344 HTTP attempts over a 181.476-second response span.
It transferred 2,948,736 bytes, normalized 3,119 logs and inventoried 18 unique implementation addresses plus the
provider and two proxies. All 312 log roots were unsaturated. Three fixed-end calls, two slots and all 21 code
objects conformed.

Actual paid-data, external-worker and GPU use was zero; both V100s and the RTX 2060 remained idle. No historical
per-event state, transaction/receipt/payload/trace, account, action, liquidation, price value or response was
opened. Because the strict candidate count is zero, no A1b/account/training budget exists for the Ethereum scalar-
LT route. A new cross-deployment or bundled-vector project requires a new data/compute audit rather than reusing
this budget.

### Frozen development-only Aave bundle replay budget

The bundle replay reads only the committed 2.1-MiB A1a normalized directory and its hash-pinned summary/manifest.
It makes zero network calls. One deterministic pass groups configuration events by transaction, preserves unknown
predecessors, reconstructs final-minus-predecessor LTV/LT/bonus vectors and identifies in-transaction round trips.
Other Configurator topics remain opaque counts.

Expected runtime is seconds on one Mac CPU core and output is small JSON. Paid data, external workers and GPU-hours
are zero; both V100s and the RTX 2060 remain idle. Completion budgets only a new zero-account vector-compiler
protocol design. Receipts, source-by-version, historical state, accounts, actions and responses have no current
budget.

### Development-only Aave bundle replay actual resource result

The deterministic pass read only the immutable A1a parent and wrote one 288,390-byte summary. It grouped 3,119
unique normalized logs into 77 collateral-configuration transaction bundles. An independent no-module-import
verifier reconstructed every bundle and all seven integrity gates passed. Actual network calls, paid data,
external-worker time and GPU-hours were zero; both V100s and the RTX 2060 remained idle.

The replay found 27 bundles with at least one known-predecessor net change, five with a net LT decrease, zero pure
emitted-LT vectors, one round trip and 54 unknown-predecessor asset occurrences. These development-explored counts
do not determine the B0 support threshold. The only new resource authorization is to design a frozen, zero-account
cross-deployment B0 inventory and B1 compiler protocol; no new chain read, account row, response row or GPU job is
yet budgeted.

### Frozen Aave B0 cross-deployment program-directory budget

B0 v1 adds nine named canonical V3 deployments under a split frozen before their event counts are opened:
Arbitrum/Avalanche/Optimism/Polygon train, Base/Gnosis validation, and BNB/Linea/Scroll untouched test. Ethereum is
reused only as a development parent and makes no new RPC call. Ten official address-book files at commit
`70e2f303...` total 279,290 bytes and are pinned by git blob and SHA-256.

For every new chain, two fixed no-auth endpoints may serve only chain IDs and cutoff block headers. PublicNode is
the sole log source. The program cutoff is the last block at or before 2026-08-15 00:00 UTC; both endpoints must
derive the same boundary and successor. The collector reads complete PoolAddressesProvider and every derived
Configurator-address log directory, plus one primary header per program block. It does not call transaction,
receipt, trace, state or code methods.

Hard caps are 50,000 HTTP attempts, 512 MiB responses, 250,000 normalized logs and 50,000 programs at two requests
per second. Expected wall time is about 1.5--4 hours and durable output below 100 MiB. One Mac CPU/network worker is
sufficient; alternatively a V100 machine may supply CPU/network only. Paid data, external workers and GPU-hours are
zero. Both V100 GPUs and the RTX 2060 remain idle, and H20 is excluded. A PASS budgets only B1 protocol design.

### Aave B0 v1 actual transport use

The sealed run at commit `707956291...` ended on Arbitrum before a successful event-log response. It completed 66
chain/header calls and recorded 14 failed logical `eth_getLogs` calls with three attempts each: 108 HTTP attempts
and 129,956 response bytes total. No normalized log, program, account, outcome or model row was retained. Mac CPU/
network wall time was under one minute; paid data, remote-worker hours and GPU-hours were zero. Both V100s and the
RTX 2060 remained idle. This is an infrastructure failure and creates no B0 support estimate.

### Target-row-free transport-canary budget

The versioned canary uses the Mac, two V100 hosts and RTX 2060 host as four independent CPU/network egresses, with
CUDA hidden. Each tests the same 18 existing chain endpoints using only chain IDs and empty zero-address genesis
log ranges. Per-host caps are 500 HTTP attempts, 32 MiB responses, two requests/s and two attempts/logical call.
Expected parallel wall time is below ten minutes, durable output below 1 MiB, paid data zero and GPU-hours zero.
All four artifacts are mandatory; PASS licenses only a B0 v2 protocol with the selected single-host route.

The actual canary completed on all four CPU hosts: 322 logical calls, 347 HTTP attempts and 27,601 response bytes.
Wall time was 47.6--169.5 seconds/host and durable artifacts about 327 KiB. Coverage was 5/9 on each V100 and 6/9
on RTX 2060/Mac, so no route was selected. Every successful log result was empty, no target row was retained, paid
data remained zero and all GPUs remained unused. B0 v2 compute/data remain unbudgeted.

### Frozen target-row-free transport-repair budget

Repair v2 inherits six routes from the hash-pinned RTX 2060 and Mac v1 artifacts and issues requests only for
Polygon, Base and one predeclared BNB candidate. Both eligible hosts run as CPU/network workers with CUDA hidden;
the V100 hosts are not repeated because their v1 coverage cannot satisfy the same-host nine-chain rule after only
three repairs.

Per host caps are 100 HTTP attempts, 8 MiB responses, two requests/s, two attempts/logical call and 30 seconds per
attempt. Expected parallel wall time is below five minutes and durable output below 1 MiB. Inputs are public
documentation plus existing immutable canary artifacts; paid data, new storage, software installation and GPU-hours
are zero. B0 v2, B1 and all model training still have no budget unless this canary passes and a separate protocol
is committed.
