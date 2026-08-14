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
- production NEMDE is not open. Use `nempy` only as an audited approximate replay and quantify target/price/
  constraint mismatches on E1.

### 4.4 Prospective event status on 2026-08-14

| Candidate | Clock status | Action/identity observability | Current role |
|---|---|---|---|
| GB NESO GC0166 | operational implementation required by 2026-11-05; five units/four lead parties were already in controlled rollout | Elexon documents public BMU identity, MDO/MDB, bid, acceptance and settlement endpoints; applicable-population completeness, history and revisions remain unproved | `PRIORITY_G1_AUDIT`, not confirmation |
| AEMO FTA Release 2 | official page still schedules 2026-11-01 | core SSP, NMI, meter and MSATS transaction/adoption data appear participant/retail-facing; public affected-panel contract not established | `WATCHLIST`, not confirmation |
| AEMO IPRR dispatch mode | original 2027-05-23 date is subject to an official pause/reset and alternate staged path | wholesale DUID bids/dispatch may eventually be public, but new participant mapping and revised schema/timing are unsettled | `PAUSED_CLOCK`, not confirmation |
| future CoW rule | no frozen new change | action and competition APIs are promising; identity continuity and complete failed submissions still require audit | `WATCHLIST` |
| ePBS | specification/activation and common pre/post observation remain unsettled | V13 failures remain | monitoring only |

The current plan therefore has zero admitted confirmation events. G1 does not pass. GC0166 is a better public-data
lead than FTA, but a promising endpoint inventory is not an admitted event contract.

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
4. Build zero/limited-row CoW and AEMO schema parsers plus provenance manifests.
5. Run E1 on 100--1,000 CoW auctions and one to seven non-target AEMO days. Measure data size and replay mismatch.
6. Only after E1 passes, freeze E2 power/leakage simulations and benchmark one small M1/M3 job on a single V100.
7. Search continuously for a second independently governed future mechanism change. Without two admitted events,
   pursue a specialist benchmark or stop rather than manufacture a Nature narrative.

## 7. Bottom line

- **Experiment plan:** scientifically sensible, operationally incomplete; E0/E1 must precede model training.
- **Data:** rich free AEMO wholesale and CoW development data exist, but current prospective confirmation data do
  not pass. FTA is probably too retail-private; IPRR's date is reset.
- **Compute:** current GPUs are enough for feasibility and likely enough for a carefully scoped paper. CPU, storage
  and event availability matter more. No compute expansion is justified now.
- **Current action:** do not start V100 experiments. First prove public observability and replay fidelity.
