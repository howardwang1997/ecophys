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
| G1 data contract | one development event plus two untouched independent transitions, exact rule/version clocks, public actions/identities/outcomes, licences and common observables | no endpoint collection or experiment |
| G2 historical feasibility | frozen development replay has calibrated type-I error, adequate power/precision and no leakage; model ladder runs end to end | stop or narrow to a non-flagship methods benchmark |
| G3 method value | M3/M4 gives a compute-matched development gain not reproduced by M0/M1 or post-hoc tuning | NMI route closes; retain reality-test protocol only |
| G4 prospective seal | code, hashes, response vectors, forecast distributions, exclusion rules and analysis script are public before event time | event becomes development-only |
| G5 real confirmation | at least two independent events support the same scoped model-selection conclusion with all nulls and failures reported | no NCS/NMI flagship claim |

**Current gate state (2026-08-14):** `G1 NOT PASSED`. FTA lacks an established public affected-participant panel,
IPRR has no stable implementation clock after its reset, and no second untouched event is admitted. The detailed
experiment/resource audit is `papers/proposal/v14_experiment_data_compute_audit_2026-08-14.md`. The verified source
and purchase decision is `papers/proposal/v14_data_acquisition_decision_2026-08-14.md`: free official AEMO and CoW
sources suffice for historical feasibility, `NO_BUY_NOW`, and FTA confirmation access requires a participant
partnership rather than a generic market-data purchase.

## 8. Data and compute plan

### Before G1

- Data: official documents, schemas, licences and zero-row availability queries only; no affected outcome values.
- Compute: Mac CPU only, expected below 20 core-hours and 32 GB RAM.
- Workers: both V100 32 GB nodes and the RTX2060 remain idle and unqueued.

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
2. Audit AEMO public-table coverage, retention, licence and DUID/aggregator continuity without opening target
   outcome values.
3. Build a metadata-only event registry for historical development and future confirmation candidates.
4. Define one proper forecast vector per candidate and a negative-control event before any data download.
5. Freeze a full V14 plan only if G0 and G1 pass. Otherwise close this scout without creating Experiment 156.
