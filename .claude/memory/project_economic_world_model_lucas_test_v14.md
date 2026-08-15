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
- The first historical gate is a bounded order/reachability preflight, not a join test. It deliberately reuses the
  consumed header-only `2021-01` and `2021-12` period-offer objects so untouched months remain eligible for later
  confirmation. Each gets one fixed 64 MiB prefix request, exact R2 retention before row access and no retry,
  extension or full-file fallback. Pass requires the first month day and a chronological transition to day two in
  both regimes. Manifest SHA: `40bf7a5c76aaf87a3533edb11cc42a41eb59fa2877bbd1c1bcf21f0dc338e9ed`.
- The rolling daily report archive exposes only recent months and cannot recover the 2021 mechanism boundary.
  Consequently a pass licenses a fresh, bounded five-role monthly-prefix bridge protocol; a failure returns to
  source design. It never licenses the 1.61 GB full object, causal/model claims, Exp156 or a GPU queue.
- The frozen prefix gate executed once from `d7dd5af5bc3b654a46da37364d118f98e408f067` and failed. Both
  exact 64 MiB responses and R2 copies passed, then 15,505,469 rows parsed with 100% timestamp success and zero
  malformed rows. Both generations had market-day regressions, so neither yielded a complete first-day prefix
  block. Summary SHA: `4e865928a5362e00eb4d07e7a89272c0638c1aaa0dedeb0871f35aeceeab478e`.
- Do not extend these prefixes. The next gate is provenance/licence/partition auditing for a free queryable mirror
  or official interface. If none passes, freeze the cost and semantics of a complete sequential compressed stream
  separately. Untouched confirmation months, Exp156 and all GPUs remain locked.
- Official source audit found a better date-partitioned route: the historical NEMDE archive exposes daily
  production format-file ZIPs, with one combined input/output/price-setting XML per five-minute interval. This
  corrects the earlier conflation between public production audit files and the restricted executable/Queue.
- The files expose the applied solver case and production solution, not raw submission/rejection history or
  participant rationale. They can ground replay error and mechanism/action decomposition but cannot establish
  adaptation alone. Exact counterfactual solving remains unavailable without Queue access or a validated open
  reconstruction.
- Licensing is not treated as settled: AEMO's current permission allows attributed use of public material, while
  the archive's old DVD notice is more restrictive. Do not redistribute raw NEMDE bytes until written
  clarification. Retained private R2 bytes, hashes and derived summaries remain the working boundary.
- A metadata-only tail protocol is frozen on the already consumed 2021-01-01 and 2021-12-01 development dates.
  It permits exactly two 1 MiB suffix requests and no XML access. Both ZIP central directories must cover
  intervals 001--288 and place deterministic interval 144 within a conservative 2 MiB later range. No GPU or
  paid data is required; pass unlocks only a separately frozen two-XML conformance audit.
- Tail protocol commit `0787be5f04f7d66e80c497f85051ce2b742bcc11` passed. Both archives have exactly 288
  date-correct, unencrypted deflate members and complete interval IDs 001--288. Interval 144 is unique in each:
  January offset/size/CRC `57637442 / 404030 / 11f971a8`; December
  `65590506 / 459136 / ebbea93d`. Conservative range bounds are 469,595 and 524,701 bytes. Summary SHA:
  `9fca06c5e627960499f0e045dbbf77de174ac8a99b3f5fe46d975dfdbb1e1bb8`.
- This pass makes one interval per regime cheaply addressable and supersedes bulk monthly-prefix extraction as the
  next source route. It does not validate XML sections, solver replay or behavior. Freeze exact member-range and
  XML conformance gates before requesting content; raw redistribution and GPUs remain locked.
- The two-member XML protocol is now frozen from the committed inventory. It requests exactly 1 MiB at each
  interval-144 local-header offset, requires R2 retention before parsing, validates header/deflate/size/CRC and
  requires the three official sections plus documented input/output group families in both regimes. Attributes
  are inventoried without values. No retry, following-member parse or raw Git artifact is allowed. A pass unlocks
  only one-day replay design; GPUs, exact-replay claims and raw redistribution remain locked.
- XML protocol commit `9f44bb4431b57564608848cb5b577b7b1e58fa9b` passed all gates. Both cases contain
  synchronized input, output and price-setting sections. Applied inputs expose ParticipantID, DUID/TraderID,
  offer dates/version, price/availability bands, MaxAvail, ramp rates, SCADA, demand and constraints; outputs expose
  SolverVersion/status/objective, prices, targets, flows, marginal values and violations.
- Input tag/attribute sets are identical across the sampled pre/post cases. Output tags and price attributes are
  identical; the only post-only output attribute is `FSTargetModeTime`, matching the independent v5.1 fast-start
  observation audit. Summary SHA: `f48d86b8f7837956fa5813e8719a712d543ade3e795fa1ad691036bd096bb7cd`.
- This pivots the historical development route to production NEMDE cases. Next mechanically sample a complete day,
  validate temporal schema and align outputs to public dispatch tables, then benchmark an open solver. Do not call
  applied cases raw submission history. Exact replay/model/GPU and raw redistribution remain locked.
- Open replay-engine audit (2026-08-15): neither current Nempy nor akxen/nemde is an input-only replay by default.
  Both inject realized generic-constraint RHS from `NemSpdOutputs/ConstraintSolution` into the historical solve.
  Treat their published agreement as solution-assisted, not independent mechanism validation. Nempy commit
  `2d3cef0e5545c820067fecddfa2e2fd984ac5583` is the primary next baseline because it is maintained and includes an
  input-side `RHSCalc`; akxen/nemde commit `23afcdf128352f12d3074194a1321a8f810f4407` is a stale secondary
  formulation reference.
- Before downloading a full NEMDE day, run a frozen R2-only two-case RHS reconstructibility gate. Seal output RHS
  for scoring, replace them with two sentinels during computation, require sentinel invariance, and report all
  unsupported equations. It needs zero new AEMO bytes, zero paid data and zero GPU. A pass unlocks only one-day
  alignment and paired assisted/input-only solver design; participant adaptation and Experiment 156 stay locked.
- RHS protocol frozen at manifest SHA
  `b56f40999518a7e2df657ea7480a85f0f855a9d8ee8151b6f7cf4f76c99ab7cd`: two consumed interval-144 cases,
  zero new AEMO requests, exact Nempy commit/source hashes, dual output sentinels `-1e100/+1e100`, all dynamic
  equations retained. Per-case gates are reference coverage 100%, evaluated coverage >=95%, sentinel outcomes and
  successful values 100% invariant, normalized median <=1e-8 and p95 <=1e-3. Both cases must pass. Even a pass is
  only an input-side dynamic-RHS component result.
- RHS execution at protocol commit `8a26320a3b2c1755e873d9c96d06a5196cf45ede` is
  `PARTIAL_INPUT_SIDE_DYNAMIC_RHS_RECONSTRUCTION`, summary SHA
  `704b20a54e8232eda57ebdc4525182c8586b104f400dbdddb0a9aa29c6e57119`. Integrity and exact dual-sentinel
  invariance passed. Coverage was 772/774 (99.7416%) pre-5MS and 882/884 (99.7738%) post-5MS/WDR; reference
  coverage was 100%. Median normalized errors were `4.11e-10`/`1.34e-10`, but p95 errors
  `0.00416664`/`0.00194488` exceeded the frozen `0.001` gate. Two equations per case raised sentinel-invariant
  `IndexError`. Do not relax the threshold or drop tails. Whole-day alignment/full solver/GPU remain locked;
  next is a post-hoc descriptive tail-operation audit, followed by a separately frozen fresh-interval repair if
  justified.
- Tail diagnostic scope was fixed before inspecting individual error IDs/terms: report six threshold exceedance
  rates, top 25 errors, every exception, expanded operations/SPD types, unresolved inputs, group/default/generic
  structure and SCADA quality/replacement flags, plus original-`1e-3` feature slices. It is descriptive only, uses
  the two consumed local ranges, exposes no RHS/SCADA values, and cannot change the partial decision or unlock a
  full day/solver/GPU.
- Tail diagnostic artifact SHA
  `5c51257ed48c54b4b2164c83729332dd1288438444c1e35fd14dc7022fe80348`: 133/772 (17.23%) pre and
  84/882 (9.52%) post equations exceed normalized error `1e-3`. All four exceptions terminate at unchecked Nempy
  `_rpn_stack:555` group-next-term access; the same block uses `group.pop` without calling it. The nine worst pre
  errors are one `Q_NIL_STRGTH_*` group/generic family at `0.988--0.9968`; post maximum `Q>YLTX_DS` is `0.500001`.
  Multiple-SCADA equations have 52.8%/49.4% tail rates and resolver-missing inputs 36.7%/26.3%, versus
  17.2%/9.52% overall. These are overlapping descriptive associations. Next repair must be 2x2: baseline,
  RPN-group only, specification-grounded input/SCADA only, combined; validate on fresh deterministic intervals.
- Official RHS-rule audit supersedes that tentative 2x2 topology. AEMO's final April 2023 guide specifies an
  independent stack per group, one group-factor multiplication and one parent-stack addition; its page-38 known
  answer is `1118.222`. Nempy's unchecked group-boundary indexing and no-op `group.pop` contradict that rule, and
  the required shared-ID removal is the first member, not the default last member.
- Public AEMO `EMSMASTER`, Constraint Implementation Guidelines and Queue Users' Guide do not specify duplicate
  SCADA selection, `EMS_Good`/replacement precedence or term-default fallback. Do not invent or tune an input arm
  against production RHS. Next repair validation is paired baseline/RPN only; SCADA is blocked until an
  authoritative rule or outcome-blind identification with fresh confirmation. Audit:
  `papers/proposal/v14_aemo_nemde_rhs_official_rule_audit_2026-08-15.md`.
- Structure-only inspection of the four known exceptions rejected a literal bounds/`pop(0)` patch before repaired
  execution. Nested sibling `G` anchors are misbound when the adjacency heuristic runs after outer-group
  annotations are stripped. The semantic relation is `child/@GroupTerm == anchor/@TermID`.
- The frozen development adapter builds that identifier tree, evaluates nested independent stacks, handles
  self-marked leading anchors and delegates every group-free operator to pinned Nempy unchanged. SCADA/default and
  generic expansion are untouched; structural inconsistencies remain errors. The consumed run must reproduce the
  parent baseline exactly and is development-only. Plan:
  `experiments/v14_aemo_nemde_rpn_repair_development/DEVELOPMENT_PLAN.md`.
- Identifier-tree development result is rejected, artifact SHA
  `07298146e9bc1075fbdb0b9fa010cc837ac6d1d0709b56e23a9771b6d178ff19`. It recovered all four exceptions and
  achieved full sentinel-invariant coverage, but pre/post normalized p95 worsened from
  `0.00416664/0.00194488` to `0.50073642/0.31578724`; strict regressions were 57/63 versus improvements 0/1.
  Do not run fresh intervals, tune exception families or use the retained adapter as a validated evaluator.
- Public AEMO material specifies independent group-stack mathematics but not enough nested XML grammar; SCADA
  selection is also unresolved. Free NEMDE replay remains solution-assisted with production RHS declared as
  observed state. Exact counterfactual NEMDE requires authoritative formulation/Queue collaboration. For V14,
  prioritize a fully public executable domain for exact M2 mechanics. Result:
  `experiments/v14_aemo_nemde_rpn_repair_development/RESULTS.md`.
- CoW enumerator audit (2026-08-15): the old 33/100 HTTP-200 result is not a retention estimate. Official code
  shows one PostgreSQL auction-ID sequence is consumed by regular auctions, fast-path quote competitions and
  empty auctions, while only valid solver competitions back the lookup route. The public OpenAPI has no list
  endpoint.
- The deployed CoW lookup supports HEAD. Previously consumed 200/404 controls preserved their status without a
  body. A fresh, disjoint 384-ID contiguous frame is now frozen for status-only enumeration; all headers and body
  lengths are discarded, no ID is replaced, and at least 100 HTTP-200 records are required. Candidate-list SHA:
  `ea4ad29d44185999c18d89338147a9394324d664c7c3280637266798787bbf35`.
- No fresh CoW body may be opened until the HEAD run passes and its exact HTTP-200 ID list is committed and pushed.
  This is a CPU/network metadata gate with zero GPU and no paid data. Protocol:
  `experiments/v14_cow_competition_head_enumeration/PREREGISTRATION.md`.
- CoW HEAD result: `FAIL_MINIMUM_ELIGIBLE_COUNT_NO_GET`. All integrity gates passed—384/384 exact HEAD requests,
  one attempt each, statuses only in `{200,404}`, zero transport errors, zero body bytes and no retained headers.
  Eligible count was 93 versus the sealed minimum 100; 291 were 404. Ledger SHA
  `2f9ae3e94aae1cb02e23d2e85eba44914b45f450e6414475ecc8b3137749dcd9`; summary SHA
  `4c52b570dcef855e686eb39997f30fcc7703c58b60598da3328c48133579176b`.
- No resolved manifest exists. Do not lower the gate, append seven IDs, top up another frame or open the 93
  competition bodies. CoW payload development requires an official list/snapshot or collaboration. Move the free
  exact-M2 scout to a fully indexed on-chain mechanism; keep all GPUs/models locked.
- Uniswap v3 Proposal 94 is now the conditional free exact-M2 development route. Governance transaction
  `0xd6c4...9833` changed factory authority at block 24,596,885, but pool treatment occurs later and separately at
  each successful `SetFeeProtocol` event; governance execution is not a simultaneous treatment clock.
- Do not trust the proposal prose as the executed mechanism identifier. It names adapter `0x3e40...`, whereas the
  Seatbelt calldata and factory `OwnerChanged` receipt name `0xf237...`. The Agora timestamp also differs from the
  block-header timestamp; chain calldata, receipts and headers are authoritative.
- The stale and executed adapters have identical 7,266-byte runtime code (SHA-256
  `37bd11b8fd174245af62b4a67691566c2df3d544d12b57cdcf5ebc1039f66bef`). Durable design rule: identify a mechanism
  by runtime code, immutables, relevant storage, authority state and executed event history, never code hash or
  governance prose alone.
- U0 freezes exactly the first two direct 500-pool propagation transactions after Proposal 94, hashes
  `0x0c49...849b` and `0x95b0...9f65`, as a disclosed deterministic conformance prefix. It requires 1,000 unique
  calldata/event pairs, symmetric `(4,4)`/`(6,6)` new fees, at least 100 zero-to-nonzero activations and at least
  ten activations in each fee class.
- This U0 frame is not pristine: reconnaissance had already accessed calldata lengths and receipt event-type
  counts, establishing 500 pool plus 500 adapter events in each transaction. Old/new fee arguments, activation
  classes and all LP responses remained unopened when the thresholds were frozen; preserve that disclosure.
- U0 may read only chain/mechanism metadata. LP actions, swaps, liquidity, prices, volume, preperiod selection and
  post-treatment responses remain unopened. A pass unlocks only a separately frozen U1 pre-treatment
  support/identity audit; it does not authorize an event study, learned model or GPU job. Protocol:
  `experiments/v14_uniswap_v3_fee_treatment_conformance/PREREGISTRATION.md`.
- U0 v1 at commit `647da77a3987f3009af1c5a9462d574c1ce353d4` is an infrastructure failure, not a scientific
  failure: chain ID succeeded, then historical-block `eth_getCode` returned HTTP 403 for all three allowed
  attempts. No governance/propagation receipt or fee transition was accessed and no artifact was written.
- V2 is a sealed transport-only repair: query the already frozen runtime-code hash at `latest`, retain every
  scientific field/gate/access lock, write disjoint `artifacts_v2`, and permit no endpoint substitution after
  execution. V1 result: `experiments/v14_uniswap_v3_fee_treatment_conformance/RESULTS_V1.md`; v2 protocol:
  `experiments/v14_uniswap_v3_fee_treatment_conformance/PREREGISTRATION_V2.md`.
- U0 v2 passed at protocol commit `2ad540a99131595cb131d425dc8885f5eff3ba5f`: 1,000/1,000 unique pools had
  exact ordered calldata/`SetFeeProtocol`/`FeeUpdateTriggered` pairing and all frozen gates passed. All were
  `(0,0)` to nonzero activations: 107 packed `0x44`, 893 packed `0x66`. Ledger SHA
  `8d3c4c1137f2ad6abfe1c0fc8326bd3845d269275c8fc6b00eac857ac1a6ae08`.
- The first pool activation occurred 2,292 blocks/27,672 seconds after governance. This directly confirms the
  per-pool event clock and invalidates a proposal-time simultaneous-treatment assumption for this event.
- There are zero reapplied-same-fee rows, hence no natural within-frame always-treated comparison. U1 must freeze
  candidate controls using treatment status, immutable metadata and pre-treatment data only, then report
  overlap/positivity before any response access. Do not invent controls from post-treatment behavior.
- U0 unlocks only U1 pre-treatment support/identity/control design. No LP response, U2 event study, model training
  or GPU allocation is authorized. Result:
  `experiments/v14_uniswap_v3_fee_treatment_conformance/RESULTS_V2.md`.
- U1a freezes a 16-pool treated sample by salted address hash, eight per `0x44`/`0x66` fee class; sample SHA
  `902312be995fd514e39c368d4d1170b3d0d1ca64426dc278787e2c94cfc9529a`. It reads only blocks
  24,548,777--24,599,176, strictly before first treatment.
- U1a counts preperiod `Swap/Mint/Burn/Collect` and manager-owner layers without decoding amount/price/liquidity
  fields. It hash-samples at most 64 NPM action transactions, pairs pool logs to NPM token IDs, and resolves NFT
  transfer ownership only through action blocks. Sender, manager, token owner and beneficiary must remain distinct.
- Blockscout's 1,000-log cap is handled by frozen recursive block bisection. Run caps: 2,000 HTTP attempts, 128 MiB
  and 250,000 normalized events; no endpoint substitution. Transport preflights used only consumed U0 mechanism
  data and no sampled-pool preperiod log.
- U1a does not construct controls. A pass unlocks only U1b preperiod expansion plus a separate outcome-blind
  control-source audit; U2 responses and GPUs remain locked. Protocol:
  `experiments/v14_uniswap_v3_preperiod_support/PREREGISTRATION.md`.
- U1a failed at protocol commit `961266c72bae34fc4a9470dd5f6ed16f95ded6fb`: only 3/16 sampled pools were
  swap-active and 1/16 position-active in the frozen preperiod. There were 374 swaps but only six position actions
  (zero mint, three burn, three collect) and three eligible NPM transactions.
- NPM share was 6/6 but is not meaningful as a broad coverage estimate. Exact pool-to-token pairing was 4/6;
  owner-after-transaction resolution was 4/4 conditional on pairing. Do not diagnose the two unmatched burns by
  re-querying; raw responses were intentionally not retained.
- Durable model change: distinguish governance authorization, adapter configuration, contract activation,
  economic exposure and participant response clocks. U0 validates the first three; U1a shows activation need not
  imply exposure. The 1,000-pool prefix is not a ready-made behavioral panel.
- Do not top up/extend U1a or launch U1b. Keep Uniswap as exact M2 unless a separately frozen full-population
  pre-treatment eligibility census is approved as a route reset; controls remain independently unresolved. U2 and
  GPUs stay locked. Result: `experiments/v14_uniswap_v3_preperiod_support/RESULTS.md`.
- U1R is frozen as that explicit route reset. It uniformly covers all exact 1,000 U0 ledger pools, including the
  16 consumed U1a pools, over the unchanged 50,400-block preperiod. Population SHA:
  `bdfad0b57a8873bbb3ff95c28598d4b3869a019284163ca269c0d9f0adafbcd9`. This is not a sample top-up and still
  estimates only the first two propagation batches.
- U1R thresholds were informed by the negative pilot and are development, not pristine confirmation: at least 50
  swap-active pools, 20 position-active pools, 200 position actions, minimum support in both fee classes, NPM
  share >=0.50 and bounded single-pool concentration. A pass only unlocks separate control/identity design.
- The deployed Blockscout Ethereum JSON-RPC supports four-value topic-0 OR but rejected address arrays in
  preflights restricted to consumed U0 data. Freeze one pool per request plus recursive exact-1,000 saturation
  splits. Expected path is 1,003 responses; caps are 5,000 attempts, 512 MiB and 1,000,000 events.
- RPC payloads necessarily transfer indexed participant and event-data fields, but U1R decodes no economic
  amounts and retains no raw response or non-NPM manager address. Transaction envelopes, token histories,
  controls, post-treatment responses, paid data and GPUs remain locked. Protocol:
  `experiments/v14_uniswap_v3_preperiod_exposure_census/PREREGISTRATION.md`.
- U1R result is `FAIL_FULL_PREPERIOD_EXPOSURE_SUPPORT_KEEP_UNISWAP_M2_ONLY`. It completed all 1,000 pools and
  passed ten of eleven gates: 89 swap-active, 25 position-active, 91 event-active, 8,722 swaps, 353 position
  actions and 212 NPM actions. Both fee classes met support minima.
- The sole failure is frozen swap event-count concentration: pool `0x919f...af79` contributes 2,625/8,722 =
  30.096%, above 25%. Its position share is 102/353 = 28.895%, below the separate 50% cap. These are event counts,
  not volume/liquidity shares; do not drop the pool or relax the gate.
- Integrity is clean: 1,009/1,009 one-attempt responses, 10,463,695 bytes, 9,075 events, one deterministic
  saturation tree, zero duplicates/conflicts and exact six-count agreement for all 16 U1a pools. Census SHA
  `677483727bfd7d1537640221bb3b7441f2227e5907a5abfa4b5d67370c5bf72f`; summary SHA
  `3ddff9cd49570a85f3c658533266a05539068624cf9385dd008147237adf0d6c`.
- Uniswap is now fixed as exact M2 for this route. Controls/U2/model/GPU access stays locked; move M3/M4 to another
  real system or a genuinely new prospective frame. Post-hoc description of consumed counts may inform an
  exposure-routing module but cannot repair U1R. Result:
  `experiments/v14_uniswap_v3_preperiod_exposure_census/RESULTS.md`.
- Freeze one no-gate post-hoc routing analysis on the committed U1R counts before selecting M3/M4 data. Report
  top-k, HHI/effective counts, Gini, total variation, fee/batch representation and swap-position channel
  divergence. It uses no new network/chain/response/identity data and cannot change U1R.
- Revised architecture: keep exact executable transitions fixed at M2, then learn a state- and channel-dependent
  exposure router before M3/M4. For uniform contracts `u`, event weights `p`, and `g=Np`, the exact identity is
  `E_p[r]-E_u[r]=Cov_u(g,r)` and `Var_u(g)=N*HHI(p)-1`. This is elementary algebra, not a novel theorem or response
  evidence. Topology: `papers/proposal/v14_exposure_routing_topology_2026-08-15.md`.
- Routing geometry result: swap/position active counts are 89/25; inverse-HHI effective counts 8.28/6.69;
  top-ten shares 73.0%/85.0%; uniform-contract TV 0.938/0.975. Extensive zeros plus active-only Gini 0.824/0.639
  motivate a support gate followed by conditional intensity, not one dense router.
- Swap-position support intersects on 23 pools (Jaccard 0.253); 23/25 position-active pools swap, but only 23/89
  swap-active pools have position actions. Weight TV is 0.415 and normalized JS is 0.269, motivating a shared
  latent state with channel-specific heads rather than a universal exposure measure.
- Batch one carries 88.3% of swaps; packed `0x44` has 10.7% of contracts but 23.0% of swaps and 30.0% of position
  actions. These are post-hoc count associations and candidate selection/confounding variables, not effects.
  Artifact SHA `964b809c186894146961f0f2cbc64f8d0e77fdd91eec9cd79edba4b632adf5dc`; U1R remains failed and GPUs locked.
- After U1R, replacement M3/M4 sources are ranked under twelve common criteria and five kill switches. Compound III
  is first for `zero_row_metadata_preflight` only; Aave V3 is the predetermined fallback, GC0166 remains official-
  clarification conditional, Uniswap stays exact M2, CoW is enumerator-blocked and FTA is partner-conditional.
- Compound's candidate unit is `(chain, Comet market, account address)`, not a beneficial person. Pre-event nonzero
  account state may define exposure; the null is no successful state-changing action, not no intent or no revert.
  Sender, manager/Bulker, account and beneficiary layers must remain distinct, and liquidation is a separate
  competing-risk channel.
- Compound currently has five pass, five partial and two unresolved criteria. Exposure denominator,
  outcome-blind controls and licence/retention are non-pass kill switches, so `G1 NOT PASSED` and no account,
  action, response or model data are authorized.
- The frozen source audit pins official Comet commit `f766f51583c23acc33b2a7824654ef2029a96804`, six Ethereum-
  mainnet configuration/root pairs, action/state/configuration markers and licence provenance. It reads a clean
  local checkout with zero RPC/network/GPU. A pass can unlock only a separately frozen chain-metadata audit.
- Compound metadata v1 at commit `aa501def3` is an infrastructure failure before source access. Tests passed; the
  inherited sparse worktree first omitted the experiment path, then the frozen direct-script wrapper failed its
  first `ecomd.research` import. No manifest/source file was read by the collector and no artifact exists.
- V2 is invocation-only: run the identical committed collector as
  `python -m ecomd.research.compound_v3_metadata` from the repository root. All source, market, marker, gate and
  access contracts remain unchanged; commit/push before execution.
- Compound metadata v2 at protocol commit `0245e6ebcd11e263e13bdeb98ff2d66cb1498b6c` passes 9/9 source
  gates: six complete mainnet market pairs, six unique Comet roots, 22 collateral configurations, 56 migration
  filenames and all frozen action/state/Configurator/licence markers. Sixteen source-file hashes reproduce.
  Artifact SHA `643edb6750ab5567528a9754bdf92b84143deaa82a9225a9c8ea9730e0d81e11`.
- All six roots share one Configurator address. Treat cross-market controls as unproved because one governance
  payload can bundle changes or create shared-authority spillovers. Source files are not authoritative deployed
  state or execution evidence.
- The pass unlocks only a separately frozen chain deployment/code/configuration and archive-provider metadata
  audit. `G1 NOT PASSED`; account mappings, actions, liquidations, prices, responses and GPUs remain locked.
- Compound chain metadata v1 is frozen before RPC: exactly 61 calls (24 fixed non-account getters, one chain ID,
  two headers, 18 code and 16 ERC-1967 storage queries) at one finalized block plus fixed block 17,000,000 for
  source-oldest USDC/WETH. Raw bodies/code are discarded after hashing.
- Forbidden: account mappings/balances, arbitrary storage, logs, transactions/receipts, totals, prices/oracles,
  liquidations and responses. All twelve gates are conjunctive; pass unlocks exposure/control protocol design only,
  not execution. Budget is about 31 seconds, under 8 MiB, no paid data/remote worker/GPU.
- Compound chain metadata v1 at protocol commit `ba40179d2a0a18d6c8bc9859d98646a68e5be665` is an endpoint-
  capability failure, not a scientific result. `eth_chainId` succeeded; `eth_getBlockByNumber("finalized")`
  returned `Invalid block number` on all three allowed attempts. No contract, historical or participant query ran
  and no artifact exists. Never rerun or mutate v1.
- Chain metadata v2 keeps the same Blockscout endpoint and every scientific/access lock. It reads `latest`, derives
  and explicitly reads `head - 64`, then pins all current queries to that numeric snapshot. Exact method vector:
  62 total = 24 call + 1 chain ID + 3 headers + 18 code + 16 storage. The observed head/snapshot gap must be 64.
- `head - 64` is a confirmation-depth convention, not Ethereum consensus finality; both headers are one-provider
  observations. Any later intervention/response protocol needs separately frozen consensus-finality and provider-
  replication checks. V2 still uses zero paid data/remote workers/GPUs and can unlock design only.
- Compound chain metadata v2 passed 12/12 at protocol commit
  `d1019df44df4acbc944e6aae408595de69478e09`: 62/62 one-attempt calls, 418,232 response bytes, head
  25,760,636 and explicit snapshot 25,760,572. Fixed block 17,000,000 had coherent USDC/WETH proxy and historical
  implementation state. Summary SHA `14f5b044d8c51e4323419b901a7f037c84c4af45083464e0daaefc561256c944`.
- All six current Comet proxies share one proxy-code hash, while implementations/hashes are six-way distinct. All
  six proxy admin slots and the Configurator share admin `0x1ec63b5883c3481134fd50d5daebc83ecd2e8779`; never treat
  markets as independent controls without payload/event separation and a spillover rule.
- The pass authorizes a separately frozen exposure/control protocol design only. `G1 NOT PASSED`; account/action/
  response rows and GPUs remain locked. Next gates: enumerable pre-event denominator, successful-action null,
  identity layers, liquidation competing risk, outcome-blind controls, finality replication and licence/retention.
- Compound exposure completeness can be certified exactly at one block. For candidate addresses `U`, require
  `totalSupplyBase = sum(max(principal,0))`, `totalBorrowBase = sum(max(-principal,0))` and each
  `totalsCollateral[a] = sum(userCollateral[i,a])`, all with zero tolerance. Under the conforming aggregate
  invariant, nonnegative omitted contributions make zero residual a certificate of no outside nonzero position;
  any positive or negative residual is a hard failure. This is a completeness lemma, not novelty.
- State-owner enumeration uses Supply.dst, Withdraw.src, SupplyCollateral.dst, WithdrawCollateral.src, nonzero
  Transfer endpoints, TransferCollateral endpoints and Absorb borrower. Token funder/recipient, manager/Bulker,
  call operator, tx sender, account and liquidator remain separate layers.
- Logs are not a complete M3 action panel: debt-to-debt base transfers can change two principals without an owner-
  identifying balance event. Full C3 requires successful call traces plus state reconciliation; without traces,
  only logged channels/net state may be reported and the complete-adaptation claim fails.
- Preferred clean event is one existing asset's borrow-CF, then liquidate-CF, then supply-cap update, atomically
  linked to Configurator event + CometDeployed + proxy Upgraded in one transaction. `Upgraded` is the operative
  clock. Shared admin is not control independence; payload spillover and overlap/concentration are hard gates.
- Zero-row design manifest passes 21 relevant tests and authorizes only a separately frozen governance metadata
  inventory. No governance/account/trace/response query or GPU job is yet authorized. Design:
  `papers/proposal/v14_compound_exposure_control_design_2026-08-16.md`.
- Compound D0 is frozen as a governance-log-only inventory over blocks 14,000,000--25,760,572. The exact root
  plan is 48 inclusive 250,000-block partitions at one Configurator plus six Comet proxies: 336 log roots and
  three chain/header calls on the unsaturated path. A 1,000-row response is discarded and recursively bisected.
- Eligible events are existing-asset borrow-CF, liquidate-CF and supply-cap updates. A provisional atomic event
  requires one eligible Configurator log, one same-proxy `CometDeployed`, one matching proxy `Upgraded`, no other
  Configurator/frozen-market upgrade and `old != new` in one transaction. This cannot rule out payload/call-path
  spillovers; a pass unlocks only a separate receipt/calldata/finality preflight.
- D0 retains normalized public governance logs and hashes only. Governance payloads/receipts/traces, accounts,
  participant actions, liquidations, prices and responses remain locked. Expected resource use is about three
  minutes of local CPU/network, zero paid data/worker/GPU; all V100/RTX 2060 queues remain empty.
- D0 passed 10/10 at protocol commit `db26bbe91111b6a71f6a4083231927574dd2b188`: 339 one-attempt requests,
  605,863 response bytes, 886 normalized logs, zero duplicates/conflicts and 14 provisional atomic candidates out
  of 184 eligible parameter updates. Summary SHA is
  `e03161118ac4cd7aea56f92f40aabdd49348d3170ce256ff42896291c1470b7f`.
- The 14 candidates contain twelve supply-cap and two borrow-factor changes. Bundling is common: 170/184 have an
  extra Configurator log, 167/184 another eligible update and 126/184 another frozen-market upgrade; counts
  overlap. Shared authority is therefore an observed spillover problem.
- The top-priority rows are mainnet-USDS wstETH borrow CF 0.82->0.80 at block 22,273,296 and mainnet-WETH rsETH
  0->0.80 at block 25,571,051. Neither is selected. Freeze the next receipt/calldata/call-path/getter/finality
  preflight over all 14, then filter deterministically before any participant row. `G1` and GPU queues remain locked.
- D0b is now frozen over all 14 in event-priority then block/hash order. Exact expected transport is 187 JSON-RPC
  calls plus one Beacon finality request: transactions/receipts, two-provider headers, callTracer, four proxy-slot
  reads, two code hashes and two asset getters per candidate, plus fixed finality/neighbor calls.
- Candidate payload isolation requires one exact `CALL` for setter/deploy/proxy-admin/target-upgrade, with deploy
  and upgrade strict descendants called by that proxy admin, and rejects successful stateful siblings outside the
  required ancestor/descendant cone. Receipt rows re-decode all retained indexed/value fields against D0. T-1/T
  getters must change only the declared field and match D0 old/new values. All failures stay in the 14-row audit;
  at least one full survivor is required.
- D0-derived 24-hour screening needs only two extra block headers; one candidate is already same-block
  contaminated. Finality combines an execution `finalized` tag, Beacon finality update and explicit execution hash
  replica, but remains provider-reported because local BLS/Merkle verification is not implemented.
- D0b uses one request/s with 600-attempt, 256-MiB, 200k-node and 64-MiB trace-input caps. It is CPU/network only;
  the full ordered provider/method/parameter vector is checked at runtime. Pass authorizes D1 exposure count/cost
  protocol design, never account acquisition or GPU work.
- D0b v1 at protocol commit `2ee8a87442b6e5a912354362bddcef572876eb59` is an infrastructure failure, not a
  candidate-mechanics result. After ten preceding logical operations, PublicNode returned JSON-RPC `-32601` for
  `debug_traceTransaction` on all three allowed attempts at the first candidate. No trace result, slot, code,
  getter, later candidate, account or response row was opened, and no artifact exists. Never rerun or mutate v1.
- V1's completion-only writer did not durably retain the ten prior response hashes/bytes/retry counts. Any v2 must
  preserve bounded partial failure evidence and may repair only trace transport while keeping the exact 14 rows,
  order, mechanics gates, access boundary and resource limits. D1, `G1` and every GPU queue remain locked.
- D0b v2 is frozen as that narrow repair. It hash-pins the v1 manifest/result, replaces only the 14 unavailable
  debug RPC calls with Blockscout's documented unpaginated raw-trace REST endpoint, and keeps the total at 188
  operations: 173 RPC, 14 raw trace and one Beacon. No candidate capability probe is allowed before the v2
  protocol commit, and no endpoint substitution is allowed afterward.
- V2 requires a unique empty trace root, every explicit parent and exact direct-child/subtrace counts. Accepted
  actions are call/create/selfdestruct; CREATE2 is not separately exposed and is conservatively CREATE, while a
  successful out-of-cone SELFDESTRUCT is stateful. Missing or malformed trace structure yields no scientific
  result.
- V2 records every HTTP attempt's outcome and response hashes. Full completion writes three success artifacts;
  any caught collection exception writes only a bounded failure artifact with prior successful-operation and
  attempt ledgers. It remains public CPU/network-only with zero paid/worker/GPU use; D1 and `G1` stay locked until
  a complete v2 pass.
- D0b v2 passed 12/12 at protocol commit `c7f770a938abe9f0e8452c9bda84bb8ed69f2e5e`: 188 logical
  operations in 191 HTTP attempts, 3,711,152 bytes, 599 trace nodes, 532,327 trace-input bytes and 129 receipt logs.
  Three transient HTTP 500s succeeded on the next attempt. Artifact SHAs are summary `83e32d0e...`, candidates
  `553055da...` and HTTP evidence `814e66af...`; independent offline reconstruction passed.
- Four of 14 rows fully conform: supply-cap changes at blocks 16,133,171; 16,520,572; 16,549,206; and 16,668,519.
  Eight rows fail stateful-sibling isolation and three fail 24-hour contamination, with one overlap. All other
  candidate checks pass for all 14. The four survivors are all 2022-12--2023-02 cap increases; two repeat one
  WETH-market asset, so they are not four independent replications.
- This exposes a new estimand blocker. A cap increase does not alter existing accounts' balance, CF or liquidation
  threshold; generic nonzero positions are not directly treated, while thwarted would-be suppliers lack a
  pre-event on-chain denominator. D1 is authorized for design only and must begin with a zero-account-row aggregate
  cap-binding/estimand gate. Slack caps or no defensible market-level entrant/flow control retire Compound M3.
  Account/actions/responses, `G1` and every GPU remain locked.
- Compound D1a is designed as a source-matched, zero-account aggregate activation audit over all four D0b v2
  survivors and seven unique historical implementations. Each implementation must match fully verified unchanged
  Blockscout Solidity source, exact aggregate/config ABI, six cap-enforcement/storage markers and the parent
  deployed-bytecode hash.
- The fixed state design uses offsets 1, 300, 1,800, 7,200, 21,600 and 50,400 blocks before each event. Both
  providers reproduce the contemporaneous configuration and `totalsCollateral`; fixed headers give actual elapsed
  time. It never queries event/post-event aggregate totals, accounts, actions, prices or responses.
- Exact `totalSupplyAsset == supplyCap` at T−1 is the only confirmatory activation rule. The 90/95/99% ratios and
  other snapshots are diagnostic and cannot authorize a pass. A pass permits only separate market-level D1b
  design; no exact saturation retires Compound M3. Account-level M3 is retired for every result because potential
  thwarted suppliers are not a pre-event enumerable cohort.
- The D1a no-retry budget is 141 public reads: 134 RPC plus seven verified-source REST requests, one request/s,
  bounded failure ledger, local CPU/network, free data and zero GPU. Both V100s and the RTX 2060 remain idle.
- D1a v1 is an immutable infrastructure failure at protocol commit
  `1dfdecf47d60b3f78a1076d2a09ed60f7ad5fc7f`. Two chain IDs and all seven Blockscout source metadata requests
  succeeded, then the first historical PublicNode `eth_getCode` returned HTTP 403 on all three allowed attempts.
- The v1 failure ledger records nine successful operations, 12 attempts, 1,370,203 bytes and a 14.878-second span;
  SHA-256 is `225266d3fb1e394f0714ceed60000ca42c84476ac8bd1641b4eacb8da30c40c8`. An independent
  offline request/hash/accounting verifier passed. No normalized source result is durable, and no historical code,
  getter, aggregate total, account or response row was opened.
- Never rerun v1. Any v2 may repair only documented historical-state transport and partial source-evidence
  durability while preserving the exact four candidates, six lookbacks, source semantics, exact T−1 saturation,
  decisions and access locks. D1b, `G1` and GPU queues remain locked.
- Official PublicNode UI states that archive data uses a separate “Get Archive Access” action. D1a v2 therefore
  never uses the free PublicNode endpoint for historical code/state; it keeps PublicNode only for chain ID and 24
  historical headers. Blockscout's documented block-parameter `eth_call` is the sole historical state source.
- Every v2 lookback uses Blockscout and PublicNode headers with exact number/hash/timestamp identity before the
  Blockscout configuration/aggregate value is accepted. This anchors canonical block identity but is explicitly
  not cross-provider state replication or a locally verified state proof.
- V2 inherits all four candidates, seven source matches, six lookbacks, exact saturation and access/decision rules.
  It removes eight redundant PublicNode code reads and four redundant post-config reads, yielding 98 RPC + seven
  source REST = 105 operations. Partial failure now preserves completed normalized source/candidate evidence while
  remaining non-scientific. CPU/free network only; all GPUs stay idle.
- D1a v2 was frozen and pushed at `a9af33e9c1e519a1b670f5700bf627655ff053fa`, then executed exactly once from
  a clean detached worktree. All 105 logical operations succeeded in 105 HTTP attempts; the ledger accounts for
  1,961,938 response bytes over 107.202 seconds. Seven source implementations, four candidate records and all ten
  integrity gates conformed. No paid data, external worker or GPU was used.
- None of the four T−1 aggregate totals exactly equalled its contemporaneous supply cap. T−1 utilization was about
  99.860059%, 73.530680%, 99.999622% and 99.999949%, and none of all 24 lookback snapshots was exactly saturated.
  The immutable decision is `FAIL_NO_EXACT_T_MINUS_ONE_SATURATION_RETIRE_COMPOUND_M3_CAUSAL_ROUTE`; D1b,
  Compound participant data, `G1` and GPU training are not authorized.
- The near-boundary WETH/cbETH values are exploratory only. Positive headroom can still block a deposit larger
  than that headroom, so the result does not prove behavioral irrelevance; attempted orders and would-be suppliers
  are unobserved. Never rescue the confirmatory route by moving the threshold. A future hard-constraint boundary-
  layer/endogenous-governance study needs a new cross-protocol protocol and untouched confirmation events.
- D1a v2 artifact SHA-256 values are summary `e5f4ef20a3561d75cd8b13007fcd2b0e23e518c13aa20f7d0cd1fd4b1f5caa66`,
  candidates `e452a2fcd00a238f5d44fb9b9c04eab294979fd93b3f6be2490f5845f26e5707` and HTTP evidence
  `cf62cf400b243e9883e4d97d69d47b12339f2da2ee312a1437351a6cb03069ad`. The independent verifier passes but
  explicitly cannot replay raw-response parsing because the frozen retention contract stores hashes, not bodies.
- The current M3/M4 handoff is a fresh Aave zero-row source/effect-class audit design. Aave is not admitted to G1:
  it must first demonstrate a complete pre-event denominator, exact local execution clock, unbundled effect class,
  authoritative state reconstruction and outcome-blind control support. Compound remains mechanics/development
  evidence only.
