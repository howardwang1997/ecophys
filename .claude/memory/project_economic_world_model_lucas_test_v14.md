# Economic World Model Lucas-test scout v14

## Durable state

- Opened 2026-08-14 from `main@67e07971e` on branch
  `economic-world-model-lucas-test-scout-v14`.
- State: `V14_SCOUT_GC0166_G1_5_OF_10_OPEN_DATA_FEASIBILITY_FAILED`.
- V13's self-concealing-action equivalence is a diagnostic warning only; it is not the paper headline.
- Working title: *Past Fit Is Not Policy Fidelity: A Prospective Lucas Test for Economic World Models*.
- “Lucas test” and “LucasBench” are provisional labels pending a naming-collision audit.

## Scientific bet

The paper-sized question is whether an Economic World Model selected for historical realism can prospectively
predict how real adaptive agents, their population and aggregate outcomes respond after a market rule changes.
The stronger hypothesis is that rule changes expose a hierarchy of adaptation:

1. exact mechanical response at the event layer;
2. action changes among persistent participants; and
3. entry, exit and contribution-share reallocation at the population layer.

The flagship result must show that this hierarchy changes model usefulness under intervention, not merely that a
forecast metric worsens. Historical-fit versus frozen-policy-loss rank, compute-matched model-family loss
differences and measured response attribution are the planned evidence. Sequential response decomposition is
order-dependent and requires alternate-order plus symmetric/Shapley sensitivity.

## Novelty boundary

Lucas critique, structural transport, ABM validation, synthetic counterfactual world-model benchmarks, market
ecology and multiscale architecture are established. V14 can be important only through a prospectively sealed,
participant-level, independently replicated real result, or through a genuinely non-equivalent learning method.
A single historical event study is specialist work, not an NCS/NMI flagship.

## Candidate systems

- CoW solver competitions and completed AEMO reforms: development only.
- NESO GC0166, Great Britain, 2026-11-05: G1 metadata audit completed at 5/10, not admitted. Clock, licence, action
  schema, intended superseded-record retrieval and a scoped public-mechanism boundary pass. Five units/four lead
  parties are already pilot/development only. CRA-I015 officially defines action codes, BMU/Lead Party IDs and
  effective-from/to dates, and Elexon directs non-Parties to its Service Desk; a complete historical extract,
  access/licence/retention, public participant-versus-default/error provenance, response freeze and independent
  replication remain unresolved.
- AEMO Flexible Trading Arrangements, 2026-11-01: watchlist only; affected-provider adoption/actions are not shown
  to be public.
- AEMO Integrating Price-Responsive Resources: the original 2027-05-23 dispatch-mode date is under an official
  pause/reset and is not a freezeable clock.
- At least two independently governed untouched transitions are required. ePBS remains monitoring-only.
- Australia is not a scientific scope requirement. The preferred confirmation pair is one public power-system
  transition plus one permissionless digital-market transition, if the same model-capability and scoring claims are
  substantive in both.
- The next qualifying CoW/Uniswap economic-mechanism change is a frozen empty registry, not a selected event. Its
  cutoff is 2026-08-14 07:00 UTC; only post-cutoff proposals passing all twelve clauses with 28-day lead qualify.
  Final packages are audited within 72 hours and ordered by official timestamp, with no replacement for failure or
  a null. Solana Alpenglow and Ethereum Hegotá remain clock-unfrozen watchlist entries.

## Compute and data lock

Before G1/G2, official documents and explicitly preregistered non-target historical development samples may be
used for CPU-only calibration, transport, schema and replay audits. A V100 host may serve as a generic CPU/data
worker with CUDA hidden after a clean commit and immutable manifest. No prospective endpoint outcomes,
Experiment 156 or GPU model job may be opened; failed samples cannot be replaced. H20 is excluded. EcoMD is not
silently treated as the adaptive-ecology model; it may be a disclosed legacy or negative-control architecture only.

## First free-data feasibility checkpoint

- Generated calibration under the frozen 48-independent-block protocol passed null calibration and structural
  leakage/identity/status checks but failed power (38.6% versus 80%) and correct-clock selection (56.0% versus 80%).
- The exact 100-ID CoW ledger returned 33 HTTP 200 and 67 HTTP 404. All 33 available payloads parsed, but arithmetic
  auction-ID space is not a valid high-coverage competition frame. The 1,000-ID expansion remains locked.
- The exact ten-object AEMO header audit downloaded 1,177,771,842 compressed bytes, representing 31,878,556,073
  uncompressed CSV bytes. Availability, byte length, SHA-256, CRC and single-member gates all passed; only 5/10
  objects passed the frozen internal-table identity and 9/10 passed minimum fields. No row was counted or joined.
- The main AEMO discrepancies are archive/internal names (`DISPATCHOFFERTRK` to `OFFERTRK`, `DISPATCHLOAD` to
  `UNIT_SOLUTION`) and legacy `OFFER/BIDOFFERPERIOD` using `TRADINGDATE` versus current
  `BID/BIDPEROFFER_D`. The two observed periods are schema-discovery data; a new field-level crosswalk must pass
  unopened held-out months before row filtering.
- All three initial promotion decisions failed and are preserved in
  `experiments/v14_open_data_feasibility/RESULTS.md`. No paid data, target row or GPU model run is justified.
- A separate v2 crosswalk froze 2021-09 and 2025-07 before access. All 10 held-out objects passed bytes, SHA, CRC,
  internal table and required source fields, but package/overall headers passed only 8/10: both 2021-09 bid objects
  expose `BIDS` rather than the discovery-derived `OFFER`. The sample is 1,557,149,667 bytes compressed and
  43,677,147,189 bytes uncompressed. This is a failed namespace gate, not evidence that row semantics differ.
- Official AEMO 5MS records show that `OFFER` to `BIDS` is part of a staged bidding/action-space migration. From
  2021-04-01 through 2021-09-30, legacy 30-minute and new 5-minute submission paths coexisted; 5MS commenced on
  2021-10-01. September is transition data, not stationary legacy validation.
- AEMO has two distinct clocks. Emulated reporting compatibility deployed on 2021-03-08; bidding transition began
  on 2021-04-01; the 5MS rule commenced on 2021-10-01. The official March control loads a
  `BIDOFFERPERIOD`-shaped export into legacy `BIDPEROFFER` and discards new-only clock/ramp fields. March is a
  measurement bridge, not a clean baseline.
- The frozen loader endpoint audit passed 6/6 untouched 2020-09 and 2022-04 controls at commit `25560ccde`; no
  archive or row was opened. Row access remains locked behind a separately frozen two-clock archive-header gate.
  Do not delete the prior package gate or reuse 2021-09 as held-out evidence. Audit:
  `papers/proposal/v14_aemo_5ms_schema_transition_audit_2026-08-14.md`.

## GC0166 metadata audit boundary

- All BMUs active in the Balancing Mechanism are subject to MDO/MDB. Units able to deliver a full BOA may use
  defaults; constrained units report an energy limitation. A row is not a limited-duration label or an adoption
  outcome.
- Initial values are MDO `9999.000` and MDB `-9999.000` MWh. Missing/partial day-ahead data use a BMU-specific
  copy-forward (`C`) or zero-fill (`Z`) rule. Public values can therefore be generated without a participant action.
- MDO/MDB are submitted through EDL. Valid/error acknowledgement and reason codes exist, but public BMRS capture of
  submitted versus defaulted, rejected, failed, late and missing messages is not established. This is the pivotal
  behavioral-observable gate.
- Exact replay is limited to public validation/defaulting, post-gate resubmission constraints and declared-energy
  caps. NESO optimiser selection, emergency intervention and operator discretion are observed stochastic outcomes,
  not an exact public engine.
- Elexon states that dataset endpoints publish data as received and allow superseded retrieval/archive backfill;
  MDO/MDB expose `publishTime` and `serialNumber`. Intended revision semantics pass G1, while empirical completeness
  remains G2.
- Live NETA IDD Part 2 V55.0 defines CRA-I015 action codes, BMU and Lead Party identity, capacity/status fields and
  effective-from/to dates. The history therefore exists as an official BSC flow; only delivery of a complete
  historical extract and its terms remain open. Elexon's documented route is the BSC Service Desk for non-Parties.
- Public P499/MDO/MDB documentation establishes publication of received values but exposes no participant/initial/
  `C`/`Z`/rejection origin field. This negative schema finding keeps the behavioral gate unresolved.
- Event contract: `data/manifests/gc0166_prospective_event_contract_v1.yaml`.
- Content-free documentation probe: `data/manifests/gc0166_documentation_probe_2026-08-14.yaml`.
- Audit report: `papers/proposal/v14_gc0166_g1_metadata_audit_2026-08-14.md`.
- Send-ready unsent requests: `papers/proposal/v14_gc0166_elexon_neso_clarification_brief_2026-08-14.md`.

## On-chain first-event freeze

- Machine contract: `data/manifests/onchain_prospective_event_selection_v1.yaml`; validator:
  `ecomd/research/prospective_event_selection.py`; report:
  `papers/proposal/v14_onchain_event_selection_freeze_2026-08-14.md`.
- Eligible universe is future-only CoW Protocol and Uniswap economic-mechanism proposals originating strictly after
  2026-08-14 07:00 UTC. Every proposal visible before the cutoff remains development-only.
- All twelve criteria are mandatory: post-freeze origin, economic treatment, binding spec, 28-day lead, actions,
  identities, null/failures, outcomes, licence/retention, common ladder, independent governance and pre-event
  precision.
- Rank by official final-package timestamp, tie-break with the canonical-ID SHA-256, and complete each audit within
  72 hours. An earlier pending final package blocks selection of a later proposal.
- The first selected event remains the headline after a null, adverse result, cancellation or data failure. A later
  event may only be a separately labelled secondary event.
- Current registry is empty and outcome-blind. No target row, effect comparison, external worker or GPU was used.

## Source and purchase decision

- `NO_BUY_NOW` on 2026-08-14. Official AEMO NEMWeb individual-table archives and the CoW solver-competition API
  are sufficient for E0 and the later limited historical E1 sample.
- Official 2021-03/2021-10 AEMO archives contain legacy-named bid files; a gap in common tooling is not evidence of
  source absence. Header/model-version equivalence remains unproved.
- A selected 2025-01 AEMO panel is about 355 MB compressed for five core files and about 590 MB with principal
  state/confound tables. Retire the `0.5--2 TB` AEMO-only estimate; provisionally use `20--100 GB` compressed and
  `0.1--0.5 TB` working storage for two to four years, pending measured manifests.
- FTA RM29/RM53 and SSP/NMI data are participant-delivered. Confirmation requires an authorised
  FRMP/NMISP/MDP/MC/DNSP partner and publication rights; no public/off-the-shelf affected panel was found.
- NEMDE Queue is paid and registered-participant-only and does not fill the action/adoption gap. Do not purchase it
  before open replay residuals are measured.

Canonical plan: `papers/proposal/plan_economic_world_model_lucas_test_nmi_ncs_v14.md`.
Detailed experiment/data/compute audit: `papers/proposal/v14_experiment_data_compute_audit_2026-08-14.md`.
Source/purchase decision: `papers/proposal/v14_data_acquisition_decision_2026-08-14.md`.

## FTA collaboration boundary

- The minimum viable FTA partnership is an SSP-operating FRMP/retailer/aggregator together with its authorised
  NMISP and MDP/MC chain. AEMO is a clock/schema/facilitation partner; it is not assumed to supply retailer product,
  invitation, consent or control-action histories.
- Access must cover the complete eligible cohort, including non-adopters, null/failed actions and exits; it must
  support stable pseudonyms, effective-dated SSP/role history, product/rule versions, interval outcomes and data
  quality flags.
- Preferred form is a prospectively declared rollout with a control or staggered-invitation design and a blind
  post-seal outcome release. Secure-enclave/code-to-data access is acceptable if audit metadata and
  disclosure-controlled aggregates can be retained.
- Non-negotiable terms are pre-outcome sealing, negative-result publication, no result-based partner veto and
  privacy/ethics governance. One partner portfolio is feasibility evidence, not independent NCS/NMI confirmation.
- AEMO consultation participants are only a contact pool, not confirmed FTA operators. AEMO's public page did not
  expose a downloadable NMISP roster on 2026-08-14; any self-described NMISP status requires official confirmation.
- Collaboration brief: `papers/proposal/v14_fta_collaboration_brief_2026-08-14.md`.
- Cross-domain event scout: `papers/proposal/v14_cross_domain_event_scout_2026-08-14.md`.
