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
- AEMO has asynchronous mechanism and observation clocks. Emulated reporting compatibility deployed on 2021-03-08; bidding transition began
  on 2021-04-01; the 5MS rule commenced on 2021-10-01. The official March control loads a
  `BIDOFFERPERIOD`-shaped export into legacy `BIDPEROFFER` and discards new-only clock/ramp fields. March is a
  measurement bridge, not a clean baseline.
- The frozen loader endpoint audit passed 6/6 untouched 2020-09 and 2022-04 controls at commit `25560ccde`; no
  archive or row was opened. Row access remains locked behind a separately frozen two-clock archive-header gate.
  Do not delete the prior package gate or reuse 2021-09 as held-out evidence. Audit:
  `papers/proposal/v14_aemo_5ms_schema_transition_audit_2026-08-14.md`.
- The bounded prefix-header gate at commit `ee673e126` failed 7/10 exact versions while all ten member, package,
  table and required-field checks passed. Failures: 2020-09 `BIDPEROFFER` v1 versus v2; 2022-04
  `UNIT_SOLUTION` v3 versus v2; `DUDETAILSUMMARY` v5 versus v4. No `D` row was parsed, but a 2026-08-15 review of
  the preserved `Content-Range` metadata found that the 2020-09 and 2022-04 `DUDETAILSUMMARY` responses transferred
  every compressed byte. The original hard-coded no-full-download flag was wrong. The observation layer must carry
  source-specific version clocks; 2020-09/2022-04 are now discovery only.
- Official follow-up resolves the failure classes without relaxing the gate. The v2 `BIDPEROFFER` citation is
  scoped to `NEXT_DAY_OFFER_*` participant files and was incorrectly transferred to the observed `PUBLIC_DVD`
  archive. The version key must include delivery channel/file ID or archive family, member, package, table/report,
  report version and effective interval.
- Data Model v5.1 went live on 2021-10-24. `DISPATCH,UNIT_SOLUTION,3` adds the non-key fast-start state field
  `DISPATCHMODETIME`; `PARTICIPANT_REGISTRATION,DUDETAILSUMMARY,5` adds non-key `DISPATCHSUBTYPE`, which AEMO says
  is required to distinguish scheduled loads from WDR loads.
- WDR is a real second mechanism that commenced on 2021-10-24, only 23 days after 5MS. Split 2021-10-01--23 from
  2021-10-24 onward; never code October as one post-5MS month. Excluding WDR rows does not remove market-wide WDR
  spillovers, and the short first interval is diagnostic rather than a clean causal design.
- Private `BIDOFFERFILETRK.SUBMISSION_METHOD` was declared but explicitly unpopulated within the WDR release
  timeline. It records transport rather than legacy/current bid semantics and cannot recover historical interface
  choice. Compatibility-report shape is not submission provenance; unknown mode remains partially identified.
- Canonical official audit:
  `papers/proposal/v14_aemo_source_version_and_clustered_reform_audit_2026-08-14.md`.
- The channel-keyed source contract was frozen at commit `39c45dddf736e418a3e112a5a4689a782e918466` before
  accessing mechanically selected 2021-02 and 2021-11. Its scientific header subgate passed 10/10, including
  `PUBLIC_DVD` `BIDPEROFFER` v1 and the post-v5.1 `DISPATCHMODETIME`/`DISPATCHSUBTYPE` fields.
- Its authoritative overall decision is `FAIL_FULL_ARCHIVE_TRANSFER_GUARD`: the 256 KiB requests transferred the
  complete 150,150-byte and 162,163-byte `DUDETAILSUMMARY` objects. No `D` row was parsed, no body persisted, and no
  GPU or paid data was used. Raw summary SHA-256 is
  `e7abbcf530d8d75a0f69c5885dfcbdc74a84f743ff9a7134754e6e8b28d8a239`; preserve it unchanged and use the
  separate adjudication as authoritative.
- The generic detector now derives full compressed-object transfer from `Content-Range`. Do not rerun or replace
  any consumed month. Row access remains locked until a separately frozen smaller-range protocol proves header
  sufficiency and selects new untouched months mechanically.
- The deterministic offline repair proof passed at exactly 65,536 compressed bytes. Across 20 preserved real
  prefixes, maximum data offset/header fields were 89/57; the synthetic stress archive uses 95/128 and is 624,432
  compressed bytes. Proof SHA is `0be682973ed75bc65c630c8ac650cb839cffc60baa3fa4d256d5a4816ca3c8d5`.
- The v2 rule skipped every consumed month and selected 2021-01/2021-12. Frozen commit
  `23c847de0527ad1e7b367d596d3a4bb82d34c194` passed once: 10/10 exact 64 KiB partial transfers, 10/10 scientific
  source headers, zero complete compressed objects and zero `D` rows. Raw summary SHA is
  `e4bac4ac57b8b25b8d91a3465eba544c9c9e22050c47750c89344e339f6417c4`; total transfer was 655,360 bytes.
- This pass closes only source-version and bounded-transfer metadata. Timestamp, key, effective-dated identity and
  applied-offer/dispatch joins remain untested. The 2021-12 `BIDPEROFFER` object declares 1,610,349,080 compressed
  bytes; do not full-download it for conformance. A separately frozen minimal-row protocol must first inventory
  already consumed artifacts or exact small daily alternatives. Workers/GPU remain locked.

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

## Modern AEMO row-conformance freeze

- The earlier complete AEMO development ZIPs are absent locally and have no verified R2 raw-object manifest.
  Preserve their summaries, but do not claim the bytes are reusable or rerun consumed months. Every new row
  protocol must verify immutable R2 retention before opening a ZIP.
- A modern, non-target protocol is frozen for 2026-06-16 using exact daily `BID_MOVE_COMPLETE`,
  `NEXT_DAY_DISPATCH` and June `DUDETAILSUMMARY` objects (18,085,971 compressed bytes). It tests five table
  headers, timestamps, primary keys, bid parentage, applied-offer/period multiplicity, physical dispatch and
  effective-dated identity. `DISPATCHOFFERTRK` lacks direction; ambiguity must be measured, never imputed.
- At freeze, those three ZIPs and all selected rows were unaccessed. Exact bytes must be retained and SHA-256
  verified in R2 before parsing. The smoke is CPU-only and cannot validate raw submissions, rejected actions,
  NEMDE replay, historical equivalence, causality or model prediction.
- Frozen commit `5645990496065b0f812db4c969e152a7b7198c7d` was pushed before access. All three downloads and
  R2 size/SHA checks passed, so rows were opened once. All five schemas, 4,535,925 timestamps, primary keys,
  market windows, bid parentage, tracker-to-dispatch and dispatch-to-identity gates passed.
- Authoritative decision is `FAIL_MODERN_ROW_CONFORMANCE_SMOKE`: 43,200/592,560 tracker rows matched more than one
  period-bid direction (`7.290400972% > 5%`). Preserve the threshold and failure. Never impute a direction from
  the two-table join. E1a, multi-day acquisition, Exp156 and GPUs remain locked.
- Official Data Model v5.3 and the real 69-field `DISPATCHLOAD` v6 header confirm that dispatch contains no
  direction field. `TOTALCLEARED` is negative for BDU import and positive otherwise, but it is a realized outcome;
  using it to select an ex-ante bid row would be leakage.
- The development hypothesis is therefore set-valued: one tracker record may apply a two-leg `{GEN, LOAD}` offer
  bundle for BDU energy/regulation services. A post-hoc descriptive diagnostic is frozen to test cardinality,
  direction sets, bid types and effective identity on the retained day. It cannot override E1a. Any bundle bridge
  needs fresh-day confirmation. Summary SHA:
  `fc422654de5c64a91e71b8dcceb22612f406092cdf6a36900859072041a6668b`.
- Post-hoc bundle diagnostic commit `b6572efc96b816268bb959e033a9127930970c7f` exactly reproduced 592,560
  tracker rows and 43,200 ambiguous rows. All ambiguous records were exactly one `{GEN, LOAD}` pair, with no
  repeated direction, exactly one effective `BIDIRECTIONAL` identity and bid type limited to `ENERGY` (17,280),
  `LOWERREG` (12,960) or `RAISEREG` (12,960); 60 DUIDs were involved.
- This supports a set-valued applied-offer bundle, not direction imputation. Realized `TOTALCLEARED` sign cannot
  choose an ex-ante leg. The result is post-hoc and does not override E1a; freeze the exact relation contract and
  confirm on one fresh date. Diagnostic SHA:
  `d8b4bb0ffe6ede3fadf00cdac68c6851568fab132b6e2c94162c8bb4317cfaa2`.
- Fresh E1b is frozen before source access. A metadata-only rule selects 2026-07-07: the first Tuesday of the first
  complete calendar month after the June development month, with a fresh July identity snapshot. Three exact
  public objects total 18,244,129 compressed bytes and must be R2-verified before parsing.
- The frozen relation permits one candidate or exactly one unique `{GEN, LOAD}` pair. Each pair requires one
  effective `BIDIRECTIONAL` identity, bid type in `ENERGY`/`LOWERREG`/`RAISEREG`, and a nonempty pair count.
  Realized dispatch cannot select a leg. This is CPU-only confirmation; multi-day data, Exp156 and GPUs remain
  locked until a full pass. Protocol: `experiments/v14_aemo_bundle_confirmation/PREREGISTRATION.md`.
- E1b protocol commit `9ee922f91ca1b4be4257e8555b49d13f27272c1a` passed all 25 gates on the untouched
  2026-07-07 sample. All 594,720 trackers were covered: 549,792 singletons and 44,928 exact `{GEN, LOAD}` pairs;
  all pair direction, uniqueness, effective-BDU-identity and bid-type violation counts were zero. Summary SHA:
  `dc36b2fe31cc5c230def8f808a7efef1fa320f80ab30e61f1999d367dd9e466b`.
- This confirms only a modern set-valued observation bridge. E1a remains a failure of the discarded unique-row
  contract. The next unlocked action is to freeze a limited mechanically sampled within-version multi-day panel;
  historical portability remains a separate gate. Exp156, prospective outcomes and GPU/model work remain locked.
- The next protocol separates within-version stability from historical portability. Four untouched Tuesdays are
  frozen mechanically: 2026-06-23/30 and 2026-07-14/28. Eight new daily objects total 70,593,936 compressed bytes;
  verified June/July identity objects are reused from R2 for 71,350,764 staged bytes. August is excluded because a
  complete monthly identity archive was not published at freeze.
- Each date must independently pass all 25 E1b gates; there is no pooled-rate exception. At freeze the panel was
  unexecuted and CPU-only. Even a pass unlocks only a separately frozen historical-version bridge audit, not
  Exp156 or GPU/model work. Protocol: `experiments/v14_aemo_bundle_stability_panel/PREREGISTRATION.md`.
- Panel v1 commit `1f44811e75a455f161532fbfdd3bde2092508bf5` passed all eight source downloads and ten
  R2 materializations, then failed before the first ZIP open because the derived day manifest omitted
  `resource_contract`. Decision: `FAIL_PANEL_IMPLEMENTATION_PRE_PARSE`; zero ZIPs, rows, day summaries or market
  content were observed. Download/retention SHAs are `5a9735d0…` and `1eba9a2d…`.
- Preserve v1. A separate pushed repair may reuse the exact R2 bytes with no AEMO source request and add only the
  missing resource section plus preflight coverage. Dates, relations, gates and claim boundary cannot change.
- The repair is frozen with all ten exact R2 hashes and the v1 provenance chain. It adds only
  `resource_contract.maximum_total_data_rows=4000000` to derived day manifests, plus a parser-entry integration
  preflight and R2-only materializer. New AEMO request count is fixed at zero; 28 combined AEMO tests pass. The
  repair remains unexecuted, CPU-only and unable to unlock historical/model claims by itself.
- Repair commit `59540001a5ce9ee6a340ea346e5755609c4bdd77` materialized all ten R2 objects with zero AEMO
  requests and passed all four unchanged panel days. Aggregate: 2,382,192 trackers, 2,203,632 singletons, 178,560
  exact `{GEN, LOAD}` bundles, 18,255,035 timestamps and zero relation violations. Summary SHA:
  `d939fffd8bc7673eb0aac78e06ae2abf38b1ea27e81cba67d03c355bec77ec88`.
- Modern within-version bridge stability is now supported across six Tuesdays/two monthly identity snapshots.
  Additional same-version days have low value. Next freeze a minimal historical schema/source bridge audit; raw
  action provenance, prospective G1, Exp156 and GPU/model work remain locked.
