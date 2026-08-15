# V14 direction scout — the Lucas test for Economic World Models

**Opened:** 2026-08-14

**Branch:** `economic-world-model-lucas-test-scout-v14`

**State:** `SCOUT`; no novelty, data or compute gate has passed

**Outcome access:** official rules, schemas, schedules and paper-reported results only
**Working title:** *Past Fit Is Not Policy Fidelity: A Prospective Lucas Test for Economic World Models*

## 1. Executive decision

The V13 self-concealing-action observation equivalence is too elementary and too narrow for a flagship paper. It
is retained as a diagnostic warning, not a research headline. The larger question is:

> Can an Economic World Model fitted before a market-rule change predict how real adaptive agents, their
> population and aggregate outcomes respond after the rule changes?

This is a computational version of the Lucas critique and a direct reality test of the emerging claim that
Economic World Models can serve as policy sandboxes. The Lucas critique, structural policy transport, agent-based
model validation and synthetic counterfactual benchmarks are established. V14 can be important only by combining
all of the following evidence that those precedents do not yet jointly supply:

1. real markets with executable and versioned rules;
2. participant-level actions and stable or explicitly bounded identities;
3. forecasts frozen before a future rule takes effect;
4. matched historical development events and independently governed confirmation events;
5. a model zoo that separates exact mechanics, within-participant adaptation and population turnover; and
6. proper scoring of the complete preregistered forecast distribution, including failed predictions.

The immediate task is a zero-outcome data/novelty scout. No EcoMD redesign, endpoint outcome, worker or GPU is
authorized by this document.

The scientific bet is stronger than “models make mistakes.” It is that an institutional change exposes a
previously hidden hierarchy of adaptation: exact rule mechanics determine the instantaneous response, persistent
participants revise actions on an intermediate horizon, and entry, exit and contribution-share reallocation may
dominate the medium-run response. The flagship result must show that this hierarchy changes which model is useful
for intervention, not merely that one forecast metric deteriorates.

This becomes a Nature-sized story only if all three levels are measured in real systems, the forecasts are sealed
before the changes, and the same scoped conclusion survives independently governed transitions. Without that
combination, V14 is a benchmark or specialist event study rather than a flagship scientific result.

## 2. The paper-sized story

### Act I — the promise

Economic World Models are proposed as generative economies for policy simulation, agent training and safety
testing. Agent-based models are often validated by matching historical time series or stylized facts.

### Act II — the scientific problem

Historical fit is not the use case that justifies a policy sandbox. When rules change, agents alter bids, timing,
participation, capital allocation and sometimes the algorithms they deploy. Multiple models can fit the same old
market yet imply incompatible new-market outcomes. Synthetic DSGE benchmarks already demonstrate off-policy
failure; the unresolved test is whether models survive a prospectively sealed transition in a real adaptive
economy.

### Act III — the experiment

Train several model classes only on pre-change data and historical development interventions. Before an untouched
rule change, freeze their probabilistic forecasts for a common response vector. After the event, score every model
without refitting and locate its error across three operational scales:

- **mechanical response:** the immediate consequence of applying the new executable rule to fixed actions;
- **behavioral plasticity:** changed actions among persistent participants; and
- **ecological selection:** entry, exit and market-share reallocation among participants or algorithm families.

The decomposition is an accounting and model-diagnostic device, not a new identity or automatic causal
attribution. Identity continuity, common support, anticipatory behavior and contemporaneous shocks require separate
design checks.

### Act IV — the possible finding

There are two publishable outcomes, neither assumed in advance:

- **reality-test result:** models ranked highly by pre-change realism fail or reorder sharply under blind policy
  prediction, establishing that past fit is a poor certificate of policy fidelity; or
- **constructive result:** an exact-mechanism model with explicit behavioral and population adaptation predicts
  unseen rule responses materially better than reduced-form, frozen-agent and post-hoc calibrated baselines.

A stronger scientific result would be replicated evidence that population reallocation carries more of the
medium-run response than within-participant policy updating. That is a hypothesis, not the planned conclusion.

## 3. Candidate claims and kill conditions

| Candidate claim | Minimum evidence | Immediate kill condition |
|---|---|---|
| C1 — observational fit does not certify policy fidelity | at least two independently governed real transitions; pre-event model ranking and post-event proper scores frozen | model rankings remain stable within uncertainty, or only one event is observed |
| C2 — exact mechanics plus adaptive ecology improve unseen-rule forecasts | compute-matched win over reduced-form, structural-frozen, within-only and population-only baselines on development and sealed events | gain disappears against a simple event-study, retrained baseline, or oracle-free structural replay |
| C3 — market adaptation has separable mechanical, within-participant and population components | stable action/identity panel, entry/exit accounting, common observables and sensitivity to anticipation/contemporaneous shocks | missing identities/actions make the components model-imputed rather than measured |
| C4 — one model-selection protocol transfers across digital economies | same preregistered scoring and gate logic in at least two domains with domain-specific exact rules | only labels and plots transfer while estimands, actions or scoring rules differ materially |

No headline may be “first Economic World Model,” “first Lucas critique for ABMs,” “first market ecology” or “first
counterfactual world-model benchmark.” Those neighborhoods are occupied.

## 4. Formal evaluation object

For model `q`, let `F_q` be a pre-intervention observational score and let `L_{qe}` be a strictly proper loss for a
forecast frozen before event `e`. The primary reality-test objects are:

\[
 \rho_{\rm rank}=\operatorname{corr}_{q}
 \bigl(\operatorname{rank}F_q,\operatorname{rank}(-L_{qe})\bigr)
\]

and the paired loss differences between declared model families across events. Neither a low rank correlation nor
a model-order reversal identifies why a model failed. They measure whether the validation criterion selected
models useful for the declared policy-prediction task.

For a persistent participant set `P`, entry set `E` and exit set `X`, response attribution will keep four quantities
separate:

1. exact-rule replay with pre-change actions;
2. action changes inside `P` conditional on declared observed state;
3. contribution-share changes inside `P`; and
4. explicitly reported entry and exit contributions from `E` and `X`.

Any sequential Oaxaca/Price-style decomposition is order-dependent when interactions are present. V14 must show
the alternate ordering and a Shapley or symmetric allocation sensitivity; the decomposition itself is prior art.

## 5. Model ladder

Every domain uses the same capability ladder rather than one favored architecture:

| Level | Model | Purpose |
|---|---|---|
| M0 | persistence, seasonal and local event-study forecasts | minimum empirical baselines |
| M1 | reduced-form sequence/world model | tests whether historical predictive fit transports |
| M2 | exact mechanism plus frozen fitted action policy | isolates mechanical recomposition |
| M3 | M2 plus within-participant online or slow policy adaptation | tests behavioral plasticity |
| M4 | M3 plus entry, exit and contribution-share dynamics | tests ecological selection |
| M5 | post-event refit/oracle-information ablations | unattainable upper bounds, never fair competitors |

EcoMD is not M4. It may enter only as a disclosed legacy simulator or negative-control architecture. Its latent
particles, synthetic price head and stylized-fact calibration cannot stand in for typed participants, executable
rules or participant-level actions. A new exact-market adapter or sibling package is likely cleaner than making
EcoMD's ontology carry the paper.

## 6. Candidate real systems and outcome lock

### 6.1 Development systems

**CoW Protocol solver competitions.** The public API exposes solver submissions and rankings. CIP-74, CIP-85 and
Consistency Metric v2 provide historical reward-rule changes, but their outcomes and a direct CIP-74 study already
exist. They may be used only to develop schemas, baselines and scoring before a later untouched event.

**Australian National Electricity Market historical reforms.** AEMO publishes next-day unit-level dispatch and
the bid/offer version used in each five-minute interval. Historical Five-Minute Settlement and other completed
rules can provide development events. Existing studies and public outcomes prevent confirmation use.

### 6.2 Prospective candidates

**NESO GC0166, Great Britain, 5 November 2026 — G1 partial 5/10, not admitted.** Limited-duration assets must
operationally implement the new MDO/MDB dynamic parameters by this date. Elexon publicly documents BMU identities,
MDO/MDB, bids, acceptances and settlement/cashflow endpoints under an open-data licence. Five units across four lead
parties entered a controlled rollout before this scout, so they are development-only. The zero-row audit passes the
clock, licence, action schema, intended revision-history and scoped mechanism-boundary clauses. CRA-I015 defines
effective-dated BMU/Lead Party history and Elexon provides a non-Party Service Desk request route, but a complete
historical extract, its terms and participant-versus-default/error provenance remain unconfirmed; response freeze
and independent replication are also unresolved. All active BMUs are subject to defined MDO/MDB or defaults, so a
public row is not automatically adoption or behavioral plasticity. Detailed audit:
`papers/proposal/v14_gc0166_g1_metadata_audit_2026-08-14.md`.

**AEMO Flexible Trading Arrangements, 1 November 2026 — watchlist only.** The effective date and technical schemas are public, but
the reform concerns retail metering, settlement points and voluntary service-provider participation. It remains a
candidate only if public data expose adoption and a response vector at the affected participant level. Aggregate
wholesale prices alone are insufficient. The current audit has not established public SSP/MSATS transaction or
affected-customer panels, so FTA is not an admitted confirmation event.

**AEMO Integrating Price-Responsive Resources — paused clock.** The final rule allows aggregated consumer resources,
virtual power plants, small generators and batteries to enter dispatch mode. The original commencement date was
23 May 2027, but AEMO proposed a pause and alternate staged delivery path in April 2026. The old date cannot be
frozen as a prospective clock. IPRR may re-enter only after a revised official schedule and a versioned public panel
linking registered/aggregated participants, bids, dispatch, forecast error and market outcomes are final.

**Future independently governed digital-market rule.** A CoW, power-market, auction or protocol change announced
after the V14 freeze may supply the second confirmation. ePBS is monitoring-only until the protocol version,
activation time and common observation instrument become final. No event may be selected after its outcomes are
read.

The current cross-domain watchlist also includes the next qualifying CoW or Uniswap economic-mechanism change,
Solana Alpenglow after an exact activation clock, and Ethereum Hegotá after a separable mechanism and exact clock.
Already active CoW and Uniswap changes are development-only. The on-chain first-qualifying-event rule is frozen at
2026-08-14 07:00 UTC: a proposal must originate after the cutoff, pass twelve metadata clauses, and leave at least
28 days before activation. It is audited within 72 hours and ordered by its official final-package timestamp; an
inconvenient, failed or null first event cannot be replaced post hoc. No event is currently selected. Contract:
`data/manifests/onchain_prospective_event_selection_v1.yaml`.

Australia is not a scope requirement. AEMO FTA is retained because of its official clock, but a public GB event or
permissionless digital market is preferable when it supplies a complete action/failure/outcome panel without access
negotiation. The current cross-domain audit is
`papers/proposal/v14_cross_domain_event_scout_2026-08-14.md`.

“Lucas test” and “LucasBench” are working labels only. A naming-collision audit is required before a public
benchmark or repository is created.

### 6.3 Required common response schema

Domain units differ, so raw outcome equality is not claimed. Each event must expose preregistered versions of:

- participation/coverage and entry/exit;
- concentration or contribution-share distribution;
- action quality, bid/offer aggressiveness or service coverage;
- execution/dispatch reliability and failure;
- allocative quality, cost, surplus or declared welfare proxy; and
- response time at fixed horizons.

The cross-domain claim concerns forecasting protocol and model-family ordering, not a universal numerical effect.

## 7. Sequential gates

| Gate | Requirement | Failure action |
|---|---|---|
| G0 story and novelty | equation-level comparison with ABM validation, Lucas/structural transport, DSGE-Gym, causal twins, market ecology and prospective forecasting | retire before a benchmark name or code project |
| G1 data contract | one development event plus two untouched independent transitions, exact rule/version clocks, public actions/identities/outcomes, licences and common observables | no prospective-target collection or model experiment; only preregistered non-target historical feasibility may continue |
| G2 historical feasibility | frozen development replay has calibrated type-I error, adequate power/precision and no leakage; model ladder runs end to end | stop or narrow to a non-flagship methods benchmark |
| G3 method value | M3/M4 gives a compute-matched development gain not reproduced by M0/M1 or post-hoc tuning | NMI route closes; retain reality-test protocol only |
| G4 prospective seal | code, hashes, response vectors, forecast distributions, exclusion rules and analysis script are public before event time | event becomes development-only |
| G5 real confirmation | at least two independent events support the same scoped model-selection conclusion with all nulls and failures reported | no NCS/NMI flagship claim |

**Current gate state (2026-08-14):** `G1 NOT PASSED`. FTA lacks an established public affected-participant panel,
IPRR has no stable implementation clock after its reset, GC0166 passes 5/10 metadata clauses but lacks a delivered
complete effective-dated population/identity history, public action/default/error provenance and a frozen response,
and the frozen on-chain registry contains no second untouched event. The detailed
experiment/resource audit is `papers/proposal/v14_experiment_data_compute_audit_2026-08-14.md`. The verified source
and purchase decision is `papers/proposal/v14_data_acquisition_decision_2026-08-14.md`: free official AEMO and CoW
sources suffice for historical feasibility, `NO_BUY_NOW`, and FTA confirmation access requires a participant
partnership rather than a generic market-data purchase.

The first preregistered free-data checkpoint has now failed rather than promoted G1/G2. Generated calibration at
48 independent blocks had 38.6% power and selected the correct clock 56.0% of the time. Arithmetic sampling of 100
CoW auction IDs returned 33 available competitions, below the 80% frame gate. Ten frozen AEMO archives were all
available, byte-exact and CRC-valid, but only 5/10 passed the preregistered internal-table contract and 9/10 passed
the minimum-field contract. These failures are retained in
`experiments/v14_open_data_feasibility/RESULTS.md`; no scale-up, row join or model ranking is authorized.

A separately frozen repair treated those two periods as discovery data and selected 2021-09 and 2025-07 by adding
six calendar months. All ten held-out objects passed availability, bytes, SHA-256, CRC, internal-table and required-
source-field gates. The strict header-package gate passed only 8/10 because both 2021-09 bid objects use `BIDS`
rather than the frozen `OFFER` namespace. The v2 result therefore also fails and remains row-locked. It shows that
the field projection is promising, but the two-regime version model is incomplete; it is not permission to delete
the failed gate post hoc.

The official 5MS postmortem resolves the main interpretation. AEMO ran a bidding transition from 1 April through
30 September 2021 in which legacy 30-minute and new 5-minute submission paths coexisted, then commenced the 5MS
rule on 1 October. Its v5.00 specification explicitly replaces the old `OFFER` CSV records with `BIDS` records.
September 2021 is therefore a mechanism-transition regime, not a clean held-out legacy month. V14 must preserve
submission granularity and regime clocks rather than normalize this change away. Compatibility reports mean the
public report generation is not, by itself, an observed participant submission interface. Detailed audit:
`papers/proposal/v14_aemo_5ms_schema_transition_audit_2026-08-14.md`.

A second official clock precedes that mechanism transition. The Data Model v5.00 specification schedules
production deployment of emulated 5-minute reporting on 8 March 2021. The March SQLLoader control confirms a
compatibility bridge: it loads a `BIDOFFERPERIOD`-shaped CSV into legacy `BIDPEROFFER` while discarding the new
date/time and ramp fields; April controls target `BIDOFFERPERIOD` directly. V14 must therefore encode an action
clock and an observation clock separately. The 8 March--31 March interval is a measurement-change negative
control: any inferred participant adaptation there is evidence that the model-to-observation bridge is confounded.

The independently frozen loader endpoint check passed all six controls from 2020-09 and 2022-04: HTTP, parser,
owner, target table, required fields and non-`FILLER` gates were 6/6. This validates the clean metadata endpoints,
not rows or effects. Archive headers and day-level joins remain behind a new frozen gate.

The next bounded prefix check failed its stricter header gate at 7/10 exact versions despite passing all ten
member/package/table/required-field projections. The misses were `BIDPEROFFER` v1 versus v2 in 2020-09,
`UNIT_SOLUTION` v3 versus v2 and `DUDETAILSUMMARY` v5 versus v4 in 2022-04. Therefore the observation layer is a
vector of source-specific version clocks, not one global reporting clock. V14 may project stable fields across a
documented version boundary, but it may not discard version provenance or refit the failed sample.

The official version audit separates the three misses. The `BIDPEROFFER` v2 citation was tied to participant
`NEXT_DAY_OFFER_*` files and was incorrectly transferred to the `PUBLIC_DVD` archive channel. `UNIT_SOLUTION` v3
adds the fast-start dynamic-state field `DISPATCHMODETIME`. `DUDETAILSUMMARY` v5 adds `DISPATCHSUBTYPE`, which AEMO
says is required to distinguish scheduled loads from WDR loads. Data Model v5.1 and the real WDR mechanism both
went live on 24 October 2021, 23 days after 5MS. The development timeline must therefore separate 1--23 October
from 24 October onward and use a delivery-channel-keyed source-version vector. The private
`BIDOFFERFILETRK.SUBMISSION_METHOD` field was explicitly not populated within the WDR release timeline, so it
cannot repair historical action-interface provenance. Detailed audit:
`papers/proposal/v14_aemo_source_version_and_clustered_reform_audit_2026-08-14.md`.

The channel-keyed matrix was then frozen before access and tested on mechanically selected 2021-02/2021-11
prefixes. All ten exact source contracts passed, including absence/presence of `DISPATCHMODETIME` and
`DISPATCHSUBTYPE`. The total protocol still fails: the 256 KiB Range request transferred both smaller
`DUDETAILSUMMARY` archives in full (150,150 and 162,163 compressed bytes). No `D` row was parsed, but the raw
collector's `full_archive_downloaded=false` flag was wrong. The immutable raw summary is overridden by a separate
`FAIL_FULL_ARCHIVE_TRANSFER_GUARD` adjudication; selected objects are not rerun. Results:
`experiments/v14_aemo_source_contract_audit/RESULTS.md`.

The separately frozen repair uses an exact 64 KiB partial response. After its deterministic offline proof and
protocol commit `23c847de0527ad1e7b367d596d3a4bb82d34c194`, one no-replacement execution on mechanically selected
2021-01/2021-12 passed 10/10 exact partial transfers and 10/10 scientific source headers, with zero complete
objects and zero `D` rows. Total transfer was 655,360 bytes. This closes only the source-version/transport metadata
gate; row semantics remain untested and locked. Results:
`experiments/v14_aemo_source_contract_repair/RESULTS.md`.

## 8. Data and compute plan

### Before G1

- Data: official documents plus explicitly preregistered, non-target historical development samples; no
  prospective affected outcome values. Failed samples and unavailable IDs cannot be replaced.
- Compute: CPU only for generated calibration, acquisition, hashing, schema and replay audits. GPU model training
  remains locked.
- Workers: a V100 host may be used as a generic CPU/data worker with CUDA hidden after a clean commit and immutable
  manifest. The GPU itself, the second V100 and the RTX2060 remain unallocated unless a later gate requires them.

### After G1/G2

- Data: immutable historical action/dispatch/competition shards stored with provenance and temporal splits in R2;
  future event collectors begin only after the observation contract is frozen.
- Current compute: the RTX2060 is for smoke and parser/model parity; the two V100s run independent
  domain/model/seed jobs. They are sufficient for feasibility and small-to-medium sequence/agent models.
- Expansion: add CPU workers for parsing and simulation and non-H20 GPU workers only after profiling shows that
  the model ladder, rather than event support, is the bottleneck. H20 is excluded.
- Large language models are not required. If a slow language-conditioned policy is later justified by actual text
  decisions, it must be an ablation and may require rented non-H20 inference capacity.

## 9. Venue routing and probability

**NCS route.** Primary route if the prospective study reveals a replicated scientific fact about how real
algorithmic economies adapt and releases a reproducible computational testbed. A single historical event study is
not sufficient. Current unconditional chance of an NCS-level completed result is approximately `8--15%`; after G1
and a successful G2/G3 it may rise to `25--40%`.

**NMI route.** Opens only if a transferable model or training criterion materially improves unseen-mechanism
prediction across market and non-market multi-agent systems. A benchmark, exact engine or multiscale architecture
alone is not NMI novelty. Current probability is below `10%` until G3.

**Fallback.** A rigorously sealed benchmark showing broad policy-prediction failure may fit a strong ML/economic-
systems or computational-social-science venue. If only one domain/event survives, split into a specialist market-
design paper rather than preserve the Nature narrative by overclaiming.

## 10. Figures that would make the story complete

1. Promise versus test: historical reconstruction compared with sealed rule-change prediction.
2. Exact mechanisms, adaptive policies and population ecology across the model ladder.
3. Prospective event registry and immutable forecast timeline.
4. Pre-change realism rank versus blind policy-fidelity rank.
5. Mechanical, persistent-participant, share-reallocation and entry/exit response attribution.
6. Cross-domain proper-score comparison with every failed prediction visible.

If figures 4--6 cannot be built without post-event fitting or model-imputed identities, there is no flagship paper.

## 11. Immediate zero-cost work

1. Complete a systematic nearest-work audit for prospective real-intervention validation rather than generic ABM
   or world-model validation.
2. With user approval, send the prepared Elexon/NESO clarification requests for historical CRA-I015 access and
   submission/default/rejection provenance; do not query live MDO/MDB rows to infer them.
3. Maintain the frozen on-chain first-qualifying-event registry daily and audit every final package within 72 hours
   without viewing candidate outcomes.
4. Define one proper forecast vector, fixed horizons and negative-control event only for candidates with auditable
   actions and identities.
5. Preserve the failed v1 and v2 checkpoints. Treat AEMO 5MS as a staged historical development intervention with
   separate mechanism, reporting, delivery-channel and table-version clocks. The 2020-09/2022-04 loader-control
   gate passed; the bounded-prefix gate failed on three distinct version classes, and the official change audit is
   complete. The channel-keyed source subgate passed 10/10 but its transfer guard failed on two small complete
   objects. The 64 KiB repair then passed 10/10 on untouched 2021-01/2021-12 with zero complete transfers. Preserve
   the failed E1a unique-direction gate and its post-hoc bundle diagnosis. Execute only the separately frozen,
   cross-month E1b set-valued relation confirmation before designing a multi-day panel. Obtain an outcome-blind
   CoW competition enumerator before any new CoW sample.
6. Open no Experiment 156, prospective-target collector or GPU job unless the full event contract passes G1.

### 11.1 Modern AEMO row-conformance gate frozen on 15 August 2026

The source inventory found that the earlier complete development ZIPs are absent locally and have no verified R2
manifest. Their preserved results remain evidence, but their bytes cannot be reused. A new retention-before-parse
rule is now mandatory.

A separately frozen, non-target modern smoke uses the mechanically selected 16 June 2026 daily reports and one
monthly identity table: 18,085,971 compressed bytes total. It tests exact bytes/CRC, five headers, timestamp and
primary-key conformance, daily-to-period bids, applied offers to period bids, applied offers to physical dispatch,
and dispatch to effective-dated DUID identity. Because `DISPATCHOFFERTRK` omits direction, match multiplicity is
reported rather than resolved by imputation.

At protocol freeze, no selected ZIP or row had been accessed. The inputs must be uploaded and SHA-256 verified in
R2 before any ZIP is opened. This is CPU-only E1a data-plane validation. Even a full pass does not establish raw
participant actions, NEMDE replay, historical regime equivalence, causality or model fidelity; it only permits a
separately frozen multi-day development design. Protocol:
`experiments/v14_aemo_row_conformance/PREREGISTRATION.md`. Source inventory:
`papers/proposal/v14_aemo_row_conformance_source_inventory_2026-08-15.md`.

### 11.2 Immutable row-conformance result

The protocol was pushed at `564599049`, then executed once. Exact download, R2 retention, CRC, five schemas,
4,535,925 timestamp parses, all primary keys, market windows, bid parentage, tracker-to-dispatch and
dispatch-to-effective-identity gates passed. Applied-offer references also matched at least one period bid for all
592,560 tracker rows.

The overall decision is nevertheless `FAIL_MODERN_ROW_CONFORMANCE_SMOKE`: 43,200 tracker rows had multiple
direction candidates because `DISPATCHOFFERTRK` omits direction, an ambiguity rate of 7.2904% versus the frozen 5%
maximum. Do not relax the threshold or choose a candidate post hoc. E1a remains failed; no multi-day panel,
Experiment 156 or GPU job is unlocked.

The official v5.3 specification and the retained 69-field `DISPATCHLOAD` v6 header show that dispatch has no
direction field. It instead gives a signed realized target: negative for BDU import and positive otherwise. Using
that outcome to select an ex-ante bid direction would leak realization into action. The better development
hypothesis is that one tracker record applies a *bundle* of direction-specific bid rows for BDU energy/regulation
services, rather than selecting one row.

An explicitly post-hoc diagnostic is frozen to test whether every ambiguity is exactly a two-row `{GEN, LOAD}`
bundle attached to one effective BDU identity. It has no pass/fail authority and cannot override E1a. If supported,
the set-valued bridge must be confirmed on a fresh mechanically selected date. Result:
`experiments/v14_aemo_row_conformance/RESULTS.md`. Diagnostic plan:
`experiments/v14_aemo_direction_bundle_diagnostic/ANALYSIS_PLAN.md`.

The post-hoc run exactly reproduced the E1a multiplicity. All 43,200 ambiguous tracker records were exactly
two-row `{GEN, LOAD}` pairs with no repeated direction; every one matched exactly one effective
`BIDIRECTIONAL` identity. They involved 60 DUIDs and only `ENERGY` (17,280), `LOWERREG` (12,960) and `RAISEREG`
(12,960). This strongly supports a set-valued offer-version bridge on the development day.

The result is deliberately non-promotional: it is post-hoc, E1a remains failed and the bundle rule may not be
fitted further. Freeze an E1b relation-level contract and test one fresh mechanically selected day. A valid bridge
maps a tracker to either one bid row or the complete two-leg `{GEN, LOAD}` bundle; realized dispatch may be joined
as an outcome but may never choose the ex-ante leg. Diagnostic result:
`experiments/v14_aemo_direction_bundle_diagnostic/RESULTS.md`.

### 11.3 Fresh cross-month bundle confirmation frozen on 15 August 2026

E1b is frozen before any selected ZIP or market row is accessed. The outcome-blind selection rule takes the first
Tuesday of the first complete calendar month after the June development month, giving 7 July 2026 and a fresh July
identity snapshot. The three exact public objects total 18,244,129 compressed bytes. They must be downloaded once,
retained with size/SHA verification in R2 and only then parsed.

The prospective relation allows either one period-bid candidate or exactly one `{GEN, LOAD}` pair. Every pair must
belong to exactly one effective `BIDIRECTIONAL` DUID and have bid type `ENERGY`, `LOWERREG` or `RAISEREG`; at least
one pair must occur. All base schema, timestamp, primary-key and join gates require exact conformance. Realized
dispatch is never permitted to select an ex-ante leg.

This is a free local CPU confirmation with zero GPU-hours. A pass validates only the modern set-valued observation
bridge on one fresh day and unlocks design—not execution—of a limited multi-day development panel. A failure keeps
that panel, Experiment 156 and all GPU/model work closed. Protocol:
`experiments/v14_aemo_bundle_confirmation/PREREGISTRATION.md`.

### 11.4 E1b confirmation result and revised work order

E1b was executed once from pushed protocol commit `9ee922f91`. All 25 frozen gates passed. All 594,720 tracker
records had complete relation coverage: 549,792 singletons and 44,928 exact `{GEN, LOAD}` pairs. Every pair had
one effective `BIDIRECTIONAL` identity and an allowed bid type; every violation count was zero. All R2, CRC,
schema, timestamp, primary-key and supporting-join gates also passed. Summary SHA-256:
`dc36b2fe31cc5c230def8f808a7efef1fa320f80ab30e61f1999d367dd9e466b`.

This confirms the corrected modern set-valued bridge across one fresh month. It does not rehabilitate the old E1a
unique-direction contract and does not establish historical compatibility, causal adaptation, replay or model
quality. The next admissible step is to freeze a *limited* within-version multi-day development-panel protocol
with mechanical date selection and no target events; historical-version portability remains a later gate. Do not
start Experiment 156 or a GPU model job yet. Result:
`experiments/v14_aemo_bundle_confirmation/RESULTS.md`.

### 11.5 Within-version four-day stability panel frozen on 15 August 2026

The next gate is deliberately limited to temporal stability within the already confirmed modern table versions.
It does not claim historical-version portability. Metadata-only selection controls the weekday, excludes the two
accessed dates and takes the earliest and latest remaining Tuesday in each month with a complete retained identity
snapshot. The four untouched dates are 23/30 June and 14/28 July 2026. August is excluded because its monthly
identity archive was not published at freeze; July identity data may not stand in for August.

The protocol adds eight daily public objects (70,593,936 compressed bytes) and reuses the exact June/July identity
objects from verified R2, for 71,350,764 staged bytes. Every date independently runs all 25 E1b gates and must
pass; one failed date fails the panel, with no pooled-rate exception. Dates are processed sequentially on local
CPU. Required GPU-hours, paid data and remote workers remain zero.

At freeze this protocol was unexecuted and row-locked. A pass would establish only modern within-version
stability, then permit a separately frozen historical-version bridge audit. It would not unlock Experiment 156, causal
claims or model training by itself. Protocol:
`experiments/v14_aemo_bundle_stability_panel/PREREGISTRATION.md`.

### 11.6 Stability-panel v1 pre-parse implementation failure

Protocol commit `1f44811e7` completed all eight one-shot downloads and verified all ten new/reused objects in R2.
The analyzer then failed before opening the first ZIP because its derived day manifest omitted the parser's
`resource_contract`. The authoritative v1 decision is `FAIL_PANEL_IMPLEMENTATION_PRE_PARSE`: zero archives opened,
zero CSV rows read, zero market content observed and zero day summaries produced.

This is not scientific evidence about stability. Preserve v1 and do not rerun it. Because the exception occurred
before the archive loop, an independent repair protocol may reuse the exact verified R2 bytes with zero new AEMO
source requests. The repair may add only the missing resource section plus a preflight integration test; dates,
tables, relation gates, thresholds and claim boundary must remain byte-for-byte or semantically identical. Result:
`experiments/v14_aemo_bundle_stability_panel/RESULTS.md`.

### 11.7 Zero-source-request pre-parse repair frozen on 15 August 2026

The repair is a new protocol, not a v1 rerun. It freezes all ten R2 object hashes plus the v1 manifest, receipt and
failure-artifact hashes. It permits exactly one scientific-code change: inject the already frozen
`maximum_total_data_rows=4,000,000` cap into each derived day manifest. A parser-entry integration preflight is now
mandatory. No AEMO request, replacement date, table/relation/gate change or claim expansion is allowed.

Execution must materialize 10/10 bytes from R2 before content access, then apply the original four-date/all-days
decision. The repair is unexecuted and CPU-only. Even a pass remains a within-version observation-bridge result;
historical portability, Experiment 156 and GPU/model work stay locked. Protocol:
`experiments/v14_aemo_bundle_stability_panel_repair/PREREGISTRATION.md`.

### 11.8 Repaired stability-panel result

Repair commit `59540001a` materialized 10/10 exact R2 objects with zero AEMO source requests, then ran the unchanged
four-day decision. Every date passed all 25 gates. Across 2,382,192 tracker records there were 2,203,632 singletons
and 178,560 exact `{GEN, LOAD}` bundles; all direction, duplicate, identity and bid-type violation counts were zero.
The day-level pair rate ranged from 7.3017% to 7.5992%. Summary SHA-256:
`d939fffd8bc7673eb0aac78e06ae2abf38b1ea27e81cba67d03c355bec77ec88`.

This closes modern within-version temporal stability: the relation is supported on the development day, fresh E1b
day and four prospectively frozen panel days across June/July identity snapshots. It does not close historical
version portability or actual-action provenance. The next free gate is a separately frozen historical source/
schema bridge audit; only after it passes should a bounded historical action panel be designed. Experiment 156,
causal claims and GPU/model work remain locked. Result:
`experiments/v14_aemo_bundle_stability_panel_repair/RESULTS.md`.

### 11.9 Historical prefix-reachability gate frozen on 15 August 2026

The official rolling daily-report archive cannot recover the 2021 5MS/WDR boundary, while the post-v5.1 monthly
period-offer object is 1,610,349,080 compressed bytes. Before any fresh historical month or full object is opened,
the next gate tests whether a complete first market day is reachable from a bounded chronological ZIP prefix.

The development-only protocol reuses the already consumed, header-only January/December 2021 objects; they cannot
serve as confirmation. Each receives exactly one 64 MiB range request. Exact bytes must be retained in R2 before
row parsing; retry, extension, substitution and full-file fallback are forbidden. A streaming CPU parser must
reconfirm the pre/post header, parse all reached dates without loss or regression, start at the first month day and
reach a second day in both objects. Manifest SHA-256:
`40bf7a5c76aaf87a3533edb11cc42a41eb59fa2877bbd1c1bcf21f0dc338e9ed`.

A pass licenses only a separately frozen five-role historical row bridge on untouched months. It is not a
historical join, action-semantics, intervention or model result. At freeze the protocol is network-unexecuted;
Experiment 156 and all GPU/model work remain locked. Protocol:
`experiments/v14_aemo_historical_prefix_reachability/PREREGISTRATION.md`.

### 11.10 Historical prefix-reachability result

Both fixed 64 MiB requests and their R2 retention passed. The streaming parser then read 15,505,469 period-offer
rows with 100% timestamp parsing and zero malformed rows. Nevertheless both archive generations violated the
frozen market-day ordering gate. January began on `2021-01-02`, reached `2021-02-01` and regressed between date
blocks; December exposed all 31 dates with explicit regressions such as day 21 before day 17. Neither prefix
contained a provably complete first-day block. Decision: `FAIL_HISTORICAL_PREFIX_REACHABILITY`; summary SHA-256:
`4e865928a5362e00eb4d07e7a89272c0638c1aaa0dedeb0871f35aeceeab478e`.

This falsifies prefix-by-date extraction, not historical portability itself. Do not extend the consumed prefixes.
The next source gate must compare free queryable/date-partitioned interfaces by official provenance, row-level
identity, licence and temporal coverage. Only if none passes may a separately frozen complete sequential-stream
budget be considered. Historical joins, action semantics, Experiment 156 and GPU/model work remain locked.
Result: `experiments/v14_aemo_historical_prefix_reachability/RESULTS.md`.

### 11.11 Date-partitioned production NEMDE source gate frozen on 15 August 2026

The source audit corrects an earlier conflation. AEMO's exact executable and paid Queue remain restricted, but its
historical archive publicly exposes date-partitioned production NEMDE format files. The official guide says every
five-minute file combines the applied input state, production output and price-setting analysis; one day contains
288 interval files. This is a potentially stronger synchronized mechanism source than joining the failed monthly
period-offer stream to separate dispatch tables.

The next protocol is metadata-only. It reuses the first daily archive in the already consumed January and
December 2021 development months, requests exactly the final 1 MiB of each ZIP and retains both suffixes in R2
before parsing. Both central directories must cover interval IDs `001..288`, contain no encrypted or unsupported
members and place a deterministic interval-144 member within a conservative 2 MiB future range cap. No XML byte
may be opened. Total data are 2 MiB; GPU-hours and paid-data spend are zero.

A pass permits only a separately frozen two-interval XML schema audit. It does not expose raw submission/rejection
history, make the solver executable, validate replay, or unlock Experiment 156. The current general AEMO
permission and an older archive-specific personal-use notice also conflict; raw redistribution stays prohibited
until written clarification. Source audit:
`papers/proposal/v14_aemo_nemde_source_audit_2026-08-15.md`. Protocol:
`experiments/v14_aemo_nemde_tail_inventory/PREREGISTRATION.md`.

### 11.12 NEMDE tail-inventory result

Protocol commit `0787be5f0` passed both development regimes. Each retained suffix contained a complete central
directory with exactly 288 members and the full interval set `001..288`. There were no encrypted, unsupported or
wrong-date members. The deterministic interval-144 members are uniquely identified at local-header offsets
57,637,442 and 65,590,506, with 404,030 and 459,136 compressed bytes. Their conservative range bounds are 469,595
and 524,701 bytes, well below the frozen 2 MiB cap. Summary SHA-256:
`9fca06c5e627960499f0e045dbbf77de174ac8a99b3f5fe46d975dfdbb1e1bb8`.

This establishes cheap date/member addressability, not XML content or replay. The next admissible step is a
separately frozen two-member conformance protocol using these exact names, offsets, sizes and CRCs. It must retain
bytes before parsing, require input/output/price-setting sections and report rather than post-hoc select fields.
Historical model training, Experiment 156 and all GPUs remain locked. Result:
`experiments/v14_aemo_nemde_tail_inventory/RESULTS.md`.

### 11.13 Two-interval NEMDE XML conformance frozen on 15 August 2026

The passed inventory fixes the exact interval-144 names, local-header offsets, compressed/uncompressed sizes and
CRCs before any XML access. The next protocol requests exactly 1 MiB beginning at each frozen offset: one
pre-5MS case on 1 January 2021 and one post-5MS/WDR case on 1 December 2021. Both opaque ranges must be retained
and verified in R2 before parsing. Retry, extension, replacement, full download and parsing a following member are
prohibited.

Each member must reproduce the frozen ZIP metadata, decode to exact size/CRC without DTD/entity declarations and
parse as XML. Both regimes require exactly one `NemSpdInputs`, `NemSpdOutputs` and `SolutionAnalysis`, the six
officially documented input group families, the six output solution families and a nonempty price-analysis
section. Attribute names are inventoried without values; action-like spelling is descriptive, not a gate.

A pass licenses only a one-day alignment/replay design. It does not run the exact engine, validate raw
submission/rejection history, or unlock a model, causal claim or Experiment 156. Data are 2 MiB and CPU-only;
V100/2060 and paid resources remain unused. Protocol:
`experiments/v14_aemo_nemde_xml_conformance/PREREGISTRATION.md`.

### 11.14 NEMDE XML conformance result and research pivot

Protocol commit `9f44bb443` passed every frozen gate in both regimes. The two exact members reproduced their ZIP
metadata, deflate EOF, uncompressed size and CRC, then parsed into valid production cases with all three sections,
all twelve documented input/output group families and nonempty price-setting analysis. The input exposes applied
offer price/availability bands, maximum availability, ramp rates, participant/unit IDs, offer version/times,
SCADA, demand and constraints. The output exposes solver version/status/objective, prices, targets, flows,
marginal values and violations. Summary SHA-256:
`f48d86b8f7837956fa5813e8719a712d543ade3e795fa1ad691036bd096bb7cd`.

Across the two cases, input tag and attribute sets are identical. Output tag and price-setting attribute sets are
also identical; only `FSTargetModeTime` is post-change-only, independently matching the known fast-start state
extension. This makes production-case replay/alignment the preferred historical source route. Monthly
`BIDPEROFFER` bulk extraction is no longer next.

The next gate should mechanically sample one complete development day, verify within-day schema/solver-version
stability and align production outputs to public dispatch tables before attempting an open replay. It must not
call applied offers raw submission history or infer strategy from one solver case. Exact replay, Experiment 156
and GPU training remain locked. Result:
`experiments/v14_aemo_nemde_xml_conformance/RESULTS.md`.

### 11.15 Open-replay engine audit and input-RHS gate

The two leading open reconstructions do not yet provide an independent replay claim. Current Nempy
(`2d3cef0e5`, version 3.0.3) obtains its standard generic-constraint RHS values from production
`NemSpdOutputs/ConstraintSolution`; akxen/nemde (`23afcdf12`) likewise serializes the production solution RHS into
`P_GC_RHS`. Their historical agreement is therefore a solution-assisted engineering baseline. In akxen/nemde,
`run_mode="target"` selects the physical intervention case rather than fixing all targets, but that does not remove
the output-RHS dependence.

Nempy is selected for the next component gate because it is maintained and contains a distinct input-side RHS
expression evaluator. Before a full one-day archive or solver is run, freeze a two-case R2-only preflight at the
audited commit. It must seal production RHS for scoring, replace every output RHS with two different sentinel
assignments, compute all dynamic equations from `NemSpdInputs`, require sentinel-invariant predictions, preserve
unsupported equations and report frozen coverage/error summaries. No new AEMO byte, solver, paid data or GPU is
needed.

A pass establishes only that one mechanical sublayer is reconstructible without its realized answer. It then
permits a one-day temporal-schema/output-alignment gate and the design of paired solution-assisted versus
input-only solver arms. An accurate assisted replay is never evidence of participant adaptation. Experiment 156,
counterfactual claims and GPU training remain locked. Audit:
`papers/proposal/v14_aemo_open_replay_engine_audit_2026-08-15.md`.

### 11.16 Two-case input-side RHS protocol frozen on 15 August 2026

The first solver-component gate is now frozen without reopening either target. It reuses only the two exact 1 MiB
ranges already retained by the XML protocol; new AEMO request count is fixed at zero. The R2 materializer must
reproduce remote metadata, local size/SHA, member metadata, deflate EOF, CRC and the prior XML SHA before the
analyzer runs. Neither date may be replaced or promoted to confirmation.

The engine is fixed to clean Nempy commit `2d3cef0e5545c820067fecddfa2e2fd984ac5583` with exact source hashes and
`xmltodict==0.12.0`. For each case, intervention-zero production RHS is sealed for scoring, then **all** output
constraint RHS fields are replaced in two deep copies by `-1e100` and `1e100`. Every input dynamic equation is
attempted once under both sentinels. Exceptions cannot be filtered or repaired; both outcomes and every successful
float must match across sentinels.

Each case requires 100% reference coverage, at least 95% evaluated coverage, exact sentinel invariance, median
normalized error at most `1e-8` and p95 at most `1e-3`; both cases must pass. Manifest SHA-256:
`b56f40999518a7e2df657ea7480a85f0f855a9d8ee8151b6f7cf4f76c99ab7cd`. A pass validates only this dynamic-RHS
component and unlocks one-day alignment design—not a full replay, counterfactual, behavior, EcoMD or Experiment
156 claim. The protocol is CPU-only with 2 MiB of R2 reads, zero paid data and zero GPU-hours. Protocol:
`experiments/v14_aemo_nemde_rhs_reconstruction/PREREGISTRATION.md`.

### 11.17 Input-side RHS result: high coverage but frozen tail-error failure

Protocol commit `8a26320a3` reproduced both exact R2 objects and the pinned Nempy engine, then passed every leakage
integrity gate. Under `-1e100/+1e100` output-RHS sentinels, success/error outcomes and all successful floats were
100% identical. The evaluator scored 772/774 pre-5MS and 882/884 post-5MS/WDR dynamic equations, with 100%
reference coverage and 99.74%/99.77% evaluation coverage. Median normalized errors were
`4.11e-10`/`1.34e-10`, below the frozen `1e-8` gate.

Both cases nevertheless failed the headline tail criterion: normalized p95 was `0.00416664` and `0.00194488`,
above the frozen `0.001`. The immutable decision is `PARTIAL_INPUT_SIDE_DYNAMIC_RHS_RECONSTRUCTION`; summary
SHA-256 `704b20a54e8232eda57ebdc4525182c8586b104f400dbdddb0a9aa29c6e57119`. Two equations per case also raised
sentinel-invariant `IndexError` and remain in the denominator.

Do not relax the p95 gate, delete tail equations or proceed to a whole-day/full-solver claim. The admissible next
step is a post-hoc descriptive classification of tail equations on these consumed cases. A concrete repair, if
found, must be frozen and tested on fresh deterministic intervals. One-day alignment, Experiment 156 and all GPU
model work remain locked. Result:
`experiments/v14_aemo_nemde_rhs_reconstruction/RESULTS.md`.

### 11.18 Post-hoc RHS tail diagnostic fixed before tail inspection

The partial decision is preserved. Before inspecting individual tail IDs or equation terms, a descriptive-only
analysis plan fixes six error thresholds, top-25 ordering, all failure records, recursively expanded RPN
operations/SPD types, unresolved-input counts and SCADA quality/replacement flags. It also fixes feature,
operation and SPD-type slices against the original `1e-3` tail boundary. No individual production/predicted RHS
or SCADA value is retained.

This diagnostic has no pass/fail outcome, may not change the original denominator/threshold and uses only the two
consumed local ranges plus the same pinned Nempy checkout. Its sole permissible output is a concrete repair
hypothesis to test on fresh deterministic intervals. Whole-day/full-solver work, Experiment 156 and GPUs remain
locked. Plan: `experiments/v14_aemo_nemde_rhs_reconstruction/TAIL_DIAGNOSTIC_PLAN.md`.

### 11.19 Tail diagnostic result and repair topology

The descriptive artifact confirms a structured multi-cause tail. At the original `1e-3` boundary, 133/772
(17.23%) pre-5MS and 84/882 (9.52%) post-change equations exceed tolerance. All four evaluation exceptions end at
the same unchecked Nempy group-boundary access (`_rpn_stack:555`); the source block also references `group.pop`
without calling it. Separately, nine catastrophic pre-5MS `Q_NIL_STRGTH_*` equations have normalized error
`0.988--0.9968` with an identical group/generic structure, while the post maximum `Q>YLTX_DS` is `0.500001` and
also group-structured.

The wider tail is enriched for multiple SCADA entries (52.8%/49.4% beyond `1e-3`) and resolver-missing inputs
(36.7%/26.3%), compared with 17.2%/9.52% overall. These overlapping post-hoc slices are not causal, but they rule
out a one-line success story. Artifact SHA-256:
`5c51257ed48c54b4b2164c83729332dd1288438444c1e35fd14dc7022fe80348`.

The next admissible development is a two-factor repair with independently switchable RPN-group and
specification-grounded input/SCADA arms. Any evaluation must use fresh mechanically selected intervals and four
paired arms (`baseline`, `RPN`, `input`, `combined`), with dual-sentinel and full-tail gates frozen before new RHS
access. The diagnostic validates no repair, and whole-day/full-solver/GPU work remains locked. Result:
`experiments/v14_aemo_nemde_rhs_reconstruction/TAIL_DIAGNOSTIC_RESULTS.md`.

### 11.20 Official RHS-rule audit narrows the repair on 15 August 2026

AEMO's final April 2023 Constraint Implementation Guidelines fixes the group semantics needed for one repair arm:
each group has an independent stack; its final top value is multiplied once by the group factor and added once to
the parent stack. The simple official known answer is `1118.222`. The pinned Nempy implementation has two direct
violations: unchecked next/end-group indexing and a no-op `group.pop` where its own comment requires removal of
the **first** shared-ID `G` member. An unqualified `pop()` would remove the wrong member.

The same audit does **not** establish an official SCADA repair. Public AEMO material defines SCADA-derived SPD
types and the `EMSMASTER` ID/type catalogue, but not duplicate-record selection, `EMS_Good`/replacement precedence
or default fallback. The production formulation remains restricted through the paid participant Queue. Therefore
the prior descriptive 2-by-2 suggestion is narrowed: freeze `baseline` versus a minimal RPN-group repair only.
Keep the input/SCADA arm explicitly blocked until an authoritative rule or an outcome-blind identification plus
fresh confirmation exists; production RHS cannot choose the rule.

Development may reuse the two consumed intervals for known-answer and non-claim checks. Evaluation must use fresh
mechanically selected members with dual sentinels, unchanged denominators and pre-registered improvement plus
non-degradation gates. Expected new data are only 2--4 MiB and CPU minutes; paid data, solver runs and all GPUs
remain locked. Audit: `papers/proposal/v14_aemo_nemde_rhs_official_rule_audit_2026-08-15.md`.

### 11.21 Identifier-tree RPN development frozen before repaired execution

A structure-only inspection of the four known exceptions falsified a literal three-line bounds patch. In nested
equations, sibling `G` anchors can become adjacent to another sibling's members after an outer `GroupTerm` is
stripped. Nempy's adjacency heuristic then binds the wrong anchor and leaves the true terminal anchor without a
value. The explicit XML relation is instead `child/@GroupTerm == anchor/@TermID`.

The development adapter is fixed before execution: build that identifier tree, preserve direct-child source order,
treat `G` with `TermID == GroupTerm` as a self-marked leading anchor, evaluate every group on an independent stack,
then delegate the group-free equation to the unchanged pinned numerical operators. Missing/duplicate anchors,
cycles, empty groups and unreachable terms remain errors. SCADA, defaults, generic expansion and non-group
operators are untouched.

The consumed two-case run must first reproduce the committed baseline exactly, then report both sentinels,
coverage/error tails, all failure transitions, strict paired improvements/worsenings, `1e-3` boundary crossings
and structural counters. It is development-only and has no pass/fail decision. Sixteen relevant tests pass; Ruff
and strict mypy pass. After the code/plan commit, execute once from a clean detached worktree with the existing
local 2 MiB, zero network requests and zero GPU. Plan:
`experiments/v14_aemo_nemde_rpn_repair_development/DEVELOPMENT_PLAN.md`.

### 11.22 RPN tree candidate rejected; free input-only NEMDE replay stops

The clean development run reproduced both committed baselines and preserved exact dual-sentinel invariance. The
identifier tree recovered all four exceptions and achieved 100% evaluation coverage, but it was semantically
destructive. Pre-5MS normalized p95 changed from `0.00416664` to `0.50073642`; post-change p95 changed from
`0.00194488` to `0.31578724`. Across jointly scored equations there were 57/63 strict regressions, zero/one strict
improvements and 42/59 new crossings above `1e-3`. Artifact SHA-256:
`07298146e9bc1075fbdb0b9fa010cc837ac6d1d0709b56e23a9771b6d178ff19`.

Reject the candidate and do not take it to fresh intervals. The public AEMO group rule determines independent-stack
mathematics but not enough of the nested XML grammar; SCADA selection is independently unresolved. No
exception-family patch may be chosen from these production errors. The original partial decision remains.

For V14, AEMO can still supply synchronized applied cases and a declared solution-assisted mechanical baseline,
but free public inputs plus current open code do not support exact M2 counterfactual replay. If exact NEMDE is
essential, it requires authoritative formulation/Queue access through collaboration. Otherwise the exact-mechanism
leg should move to a domain with public executable rules, while AEMO is retained only within its observed-state
claim boundary. Full-day acquisition, model training and GPUs remain locked pending that route decision. Result:
`experiments/v14_aemo_nemde_rpn_repair_development/RESULTS.md`.

### 11.23 CoW outcome-blind competition enumeration frozen

The earlier 33/100 CoW HTTP-200 result is not a historical-retention estimate. Official service code shows that
regular auctions, fast-path quote competitions and empty auctions draw from the same PostgreSQL auction-ID
sequence, while only valid solver competitions enter the table behind the public lookup route. The OpenAPI has no
historical list endpoint. Integer-space 404s therefore cannot be interpreted as deleted competitions.

The deployed lookup route does support HEAD. On two previously consumed controls it returned the same known
200/404 existence classes without a response body. Before accessing any fresh ID, a new two-stage protocol freezes
exactly 384 contiguous, non-overlapping candidate IDs (`13,373,706` down to `13,373,323`; candidate-list SHA-256
`ea4ad29d44185999c18d89338147a9394324d664c7c3280637266798787bbf35`). Stage one stores only HEAD status,
request order and transport attempts; every header, body length and body field is discarded. Stage two may open
only the exact HTTP-200 list, and only after that resolved list is committed and pushed.

The HEAD stage requires all 384 requests in order, zero body bytes, terminal statuses only in `{200,404}`, no
replacement and at least 100 eligible IDs. The threshold is a feasibility/sample-size gate, not a prevalence or
representativeness claim. This route is public, CPU/network-only, free and uses zero GPU-hours. If it passes, the
next protocol can audit payload schema and exact score/ranking replay on the sealed set. If it fails, GET remains
forbidden and the exact-mechanism leg moves to another public executable system. Protocol:
`experiments/v14_cow_competition_head_enumeration/PREREGISTRATION.md`.

### 11.24 CoW HEAD frame misses the sealed sample-size gate

The protocol-commit run completed all 384 HEAD requests in exact order with 384/384 terminal 200/404 statuses,
zero transport errors, one attempt per ID, zero response-body bytes and no retained header/body field. The
enumeration mechanism itself therefore behaved cleanly.

Only 93 IDs returned 200, below the sealed minimum of 100; 291 returned 404. Decision:
`FAIL_MINIMUM_ELIGIBLE_COUNT_NO_GET`. Ledger SHA-256:
`2f9ae3e94aae1cb02e23d2e85eba44914b45f450e6414475ecc8b3137749dcd9`; summary SHA-256:
`4c52b570dcef855e686eb39997f30fcc7703c58b60598da3328c48133579176b`.

Do not lower the gate, append seven IDs, combine a post-hoc top-up or open the 93 bodies. No resolved manifest was
created. CoW can reopen only through a new non-top-up source such as an official list/snapshot or collaboration.
The immediate free exact-M2 route should move to a public on-chain system with a complete event index and
executable state transition. GPUs, learned models and AEMO full-day acquisition remain locked. Result:
`experiments/v14_cow_competition_head_enumeration/RESULTS.md`.

### 11.25 Uniswap v3 treatment conformance frozen before response access

Proposal 94 supplies a promising public exact-M2 development event, but neither its prose nor its governance
execution time is the pool-level treatment. The proposal text names adapter `0x3e40...`; the executed factory
`OwnerChanged` log and Seatbelt calldata instead name `0xf237...`. Likewise, the front-end execution timestamp
differs from the Ethereum block timestamp. Chain calldata, receipts and block headers are authoritative.

The address discrepancy exposes a broader Economic World Model requirement. The stale and executed adapters have
identical 7,266-byte runtime code, so a code hash alone does not identify the operative rule. An executable
mechanism must be pinned by runtime code, immutable arguments, relevant storage, authority state and executed
transition history. For Uniswap v3, Proposal 94 transfers authority; each pool is treated only when a successful
`setFeeProtocol` transition occurs.

U0 freezes the first two successful direct 500-pool propagation batches after execution, in chain order. The
runner must reconstruct exactly 1,000 unique calldata/event pairs, require one ordered `SetFeeProtocol` plus one
`FeeUpdateTriggered` event per pool, accept only symmetric new fees `(4,4)` or `(6,6)`, and find at least 100
zero-to-nonzero activations with at least ten in each fee class. This is a deterministic conformance prefix, not a
population sample. Reconnaissance had already opened calldata and receipt event-type counts for the two
transactions; that access is disclosed. Old/new fee arguments, activation classes and LP responses remained
unopened when the thresholds were frozen.

Only governance and propagation transactions, receipts, block headers and adapter runtime code may be opened.
LP actions, swaps, liquidity, price, volume, post-treatment outcomes and even preperiod selection remain locked.
A pass authorizes only a separately frozen U1 pre-treatment support/identity audit; a failure blocks response
collection without batch replacement or threshold repair. U0 uses 11 read-only RPC calls, less than 20 MB, under
one local CPU core-hour, no paid data and zero GPU-hours. Protocol:
`experiments/v14_uniswap_v3_fee_treatment_conformance/PREREGISTRATION.md`.

### 11.26 Uniswap U0 v1 transport failure and sealed v2 repair

The clean v1 run at protocol commit `647da77a3987f3009af1c5a9462d574c1ce353d4` verified chain ID, then the
public endpoint returned HTTP 403 on all three allowed historical `eth_getCode` attempts. It stopped before the
governance or propagation transaction/receipt calls. Thus no old/new fee argument, activation class or market
response was opened, and the event-conformance question remains unanswered rather than failed.

V2 changes only the bytecode provenance query from historical block `24,599,177` to `latest`. The frozen runtime
hash remains identical, and code provenance does not define governance or per-pool treatment time. Proposal,
batches, gates, thresholds, non-representative scope, reconnaissance disclosure and every outcome lock remain
unchanged. The v2 manifest pins the exact v1 contract hash/failure and writes to a disjoint artifact directory.
After the v2 protocol is committed and pushed, execute it once; another transport substitution is not permitted
inside that protocol. V1 result: `experiments/v14_uniswap_v3_fee_treatment_conformance/RESULTS_V1.md`. V2 protocol:
`experiments/v14_uniswap_v3_fee_treatment_conformance/PREREGISTRATION_V2.md`.

### 11.27 Uniswap U0 passes exact treatment reconstruction; natural control is absent

The v2 run at pushed protocol commit `2ad540a99131595cb131d425dc8885f5eff3ba5f` passed every frozen gate. Both
500-pool batches paired exactly in calldata order, yielding 1,000 unique successful pool transitions. All 1,000
were zero-to-nonzero activations: 107 packed `0x44` and 893 packed `0x66`. Runtime code, governance owner change,
transaction/receipt/block hashes, timestamps and the 27,672-second governance-to-first-pool delay all conformed.
Ledger SHA-256: `8d3c4c1137f2ad6abfe1c0fc8326bd3845d269275c8fc6b00eac857ac1a6ae08`.

This establishes the first free, answer-free exact-M2 treatment ledger in V14, but only for a disclosed
non-representative development prefix. It also removes a hoped-for identification shortcut: there are zero
same-fee reapplications and thus no within-batch always-treated control. U1 must freeze a pre-treatment-only pool
support, identity-coverage and control-candidate construction. Controls cannot be chosen from post-treatment
liquidity, volume, price or LP actions; overlap/positivity must be evaluated before response access. No U2 event
study, learned model or GPU job is yet authorized. Result:
`experiments/v14_uniswap_v3_fee_treatment_conformance/RESULTS_V2.md`.

### 11.28 U1a preperiod support and NPM identity gate frozen

U0 does not authorize response access: all 1,000 pools were newly activated, so a natural within-frame control is
absent. U1a first tests whether free data can support a defensible observation layer. It hash-selects exactly 16
treated pools from the committed U0 ledger—eight per packed fee class—without preperiod behavior. Sample SHA-256:
`902312be995fd514e39c368d4d1170b3d0d1ca64426dc278787e2c94cfc9529a`.

The only opened pool window will be blocks 24,548,777--24,599,176, the 50,400 blocks immediately preceding the
first treatment block. Per pool, query `Swap`, `Mint`, `Burn` and `Collect` separately; count events and manager
owners but do not decode amount, price, tick, liquidity or token-amount fields. Blockscout's documented 1,000-log
limit is handled by deterministic inclusive-interval bisection, with single-block saturation, 128 MiB, 2,000 HTTP
attempts or 250,000 normalized events all causing a stop.

For NPM-managed position actions, hash-sample at most 64 unique preperiod transactions. Retain the transaction
sender, pair pool actions to following NPM token-ID events, and recover ERC-721 transfer history only through the
action block. These are separate observable identity layers, not a beneficial-owner ontology. Gates require
activity in at least eight pools of each support type, 64 position actions, NPM action-count share at least 0.50,
32 eligible identity transactions, 0.80 exact token pairing and 0.95 post-transaction owner resolution.

Transport was preflighted only on already consumed U0 mechanism transactions; no sampled-pool preperiod log was
opened. A pass unlocks only expanded preperiod U1b and a separately frozen control-source audit. U2, all
post-treatment variables and all GPU/model work remain locked. Protocol:
`experiments/v14_uniswap_v3_preperiod_support/PREREGISTRATION.md`.

### 11.29 U1a fails: contract activation is not economic exposure

The clean run at protocol commit `961266c72bae34fc4a9470dd5f6ed16f95ded6fb` completed all 64 pool/event queries
without saturation or transport error, but failed the frozen support gates. Only 3/16 pools had a preperiod swap;
only 1/16 had a position action. The window contained 374 swaps but just six position actions—zero mints, three
burns and three collects—across three eligible NPM transactions. Exact pool-to-token pairing was 4/6. Conditional
owner resolution was 4/4, and NPM action share was 6/6, but both have tiny denominators.

This is a substantive modeling result, not merely a data inconvenience. Governance authorization, adapter
configuration, pool contract activation, economic exposure and participant response are distinct clocks. U0
validated the first three; U1a shows that contract activation does not imply active economic exposure in this
small hash-stratified sample. The 1,000-pool propagation prefix is therefore not a ready-made agent panel.

Do not top up the sample, extend its window or launch the planned U1b. Uniswap remains a valid exact-M2 case. To
retain participant-level M3/M4, either move that layer to another real system or separately preregister a
full-population pre-treatment eligibility census as a route reset, followed by an independent control-source
gate. No post-treatment data or GPU/model run is unlocked. Result:
`experiments/v14_uniswap_v3_preperiod_support/RESULTS.md`.

### 11.30 Full-population preperiod census frozen as a disclosed route reset

The next admissible free test is not a U1a top-up. U1R changes the estimand to every pool in the exact committed U0
ledger and applies one uniform query to all 1,000 rows, including the 16 already consumed in U1a. Its canonical
population hash is `bdfad0b57a8873bbb3ff95c28598d4b3869a019284163ca269c0d9f0adafbcd9`. The scope remains
the first two propagation batches, not all Uniswap v3 pools.

For the same strictly pre-treatment 50,400-block window, U1R opens only `Swap/Mint/Burn/Collect` event existence,
counts and position-manager class. It does not decode amount, price, tick, liquidity or token amounts; raw payloads
and non-NPM manager addresses are discarded. Transaction envelopes, token histories, controls and every
post-treatment field remain closed. A one-address/four-topic-OR Blockscout query is frozen after preflights on
consumed U0 mechanism data showed that the deployed endpoint supports topic OR but rejects address arrays.

U1a informed the thresholds, so this is explicitly development rather than pristine confirmation. Gates require
50 swap-active pools, 20 position-active pools, 200 position actions, support in both fee classes, NPM share at
least 0.50 and bounded single-pool concentration. A pass licenses only separate outcome-blind control and identity
design; a failure fixes Uniswap at M2 for this route. The unsaturated path is about 1,003 requests and 8.4 minutes,
with 5,000-request/512-MiB/1,000,000-event hard caps. It needs no paid data, remote worker or GPU. Protocol:
`experiments/v14_uniswap_v3_preperiod_exposure_census/PREREGISTRATION.md`.

### 11.31 U1R reveals support but fails the frozen concentration gate

The clean protocol-commit run covered all 1,000 pools and passed every integrity, count, fee-class, position-
support and NPM gate. It found 89 swap-active and 25 position-active pools, with 8,722 swaps, 353 position actions
and 212 NPM-managed actions. Only 91 pools had any frozen event; event support is therefore sparse within this
specific propagation prefix.

U1R nevertheless fails conjunctively. One pool contributed 2,625 swaps, 30.096% of all swap events, above the
frozen 25% cap. It also contributed 102/353 position actions, but that 28.895% share passed the separate 50% cap.
These are event-count concentrations, not volume or liquidity shares. All 16 U1a counts reproduced exactly, and
1,009/1,009 HTTP responses succeeded on one attempt, so transport cannot explain the decision.

Do not drop the dominant pool, relax the cap or open outcomes. For the active V14 route, Uniswap is now fixed as
the exact-M2 mechanism case; participant response M3/M4 must come from another real system or a genuinely new
prospective event/control frame. Post-hoc analysis of already consumed preperiod counts may inform an exposure-
routing module, but cannot repair this gate or support a causal claim. Result:
`experiments/v14_uniswap_v3_preperiod_exposure_census/RESULTS.md`.

### 11.32 Post-hoc exposure-routing geometry frozen without a gate

Before selecting a replacement M3/M4 domain, quantify what U1R already consumed. The exploratory analysis fixes
swap, position-action and combined event measures; top-1/3/5/10/20 shares; HHI/effective counts; full/active Gini;
total variation from uniform contracts; fee/batch partitions; and swap-versus-position support/mass divergence.
There is no pass/fail threshold and no fresh data. U1R remains failed regardless of output.

This exposes a missing operator in the multiscale design. Exact mechanism execution remains fixed at M2, while a
state- and channel-dependent router maps technical units into economic exposure before M3 participant adaptation.
For `u_i=1/N`, event weights `p_i` and `g_i=Np_i`, the exact aggregation identity is
`E_p[r]-E_u[r]=Cov_u(g,r)`, with `Var_u(g)=N HHI(p)-1`. These are elementary identities, not a novelty claim; the
unopened response determines the covariance and its sign.

The computation reads only the committed 1,000 count rows, runs locally in seconds and uses zero network, paid
data and GPU. Its purpose is to constrain architecture and the next source gate, not to generate a causal result.
Plan: `experiments/v14_uniswap_v3_exposure_routing_exploratory/EXPLORATORY_PLAN.md`; topology:
`papers/proposal/v14_exposure_routing_topology_2026-08-15.md`.
