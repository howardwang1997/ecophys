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
