# EcomD Paper G Topic Cycle 47 (2026-09-15) — asset-first harvest, two F1 screens, zero survivors

PRIVATE / INTERNAL.

Protocol basis: standing PI scope (ICLR/ICML scientific ML, cross-domain, literature-only). This
cycle implements the Cycle 46 postmortem changes: (1) `new_truth_or_control_capability` weighted to
5 of 8 generators, each asset-first — programs must name a public, solo-computable archived
measurement asset with an exploitable control handle; (2) every generator received the full
333-node occupied route list plus the four Cycle 46 record-only programs and had to name the
closest 1-3 nodes with an exact difference before proposing; (3) mandatory self-hostile search
(search for the 2-3 strongest near-answering works before proposing); (4) per-anchor honesty fields
(exactly what was opened, via which tool). Outcome: 6 raw programs from 8/8 generators (honest
empty returns permitted), 2 F1 quick screens, both closed. Zero survivors; no F2/F3/forecast/card/
execution.

## F0 harvest

Eight lane-scoped generators (astro-archives, bioimaging-archives, env-sensor-archives,
materials-archives, neuro-ephys-archives, disagreement-biochem, disagreement-physical,
cross-domain-theorem) via workflow wf_d2d548a4-d17 (9 agents incl. Pareto judge, 948k subagent
tokens, 0 errors). Six programs; all four assets spot-checked open by the judge. The
cross-domain-theorem and astro generators returned zero programs with honest tooling notes — the
self-hostile search discarded their candidates.

| program | lane | archetype | judge | disposition |
|---|---|---|---|---|
| g47_sequence_plasticity_allocation_prediction | new_truth | empirical_intervention | 6.80 | F1 → quick_closed |
| g47_whi5_start_pipeline_invariance | unresolved_model_disagreement | empirical_intervention | 6.60 | F1 → quick_closed |
| g47-censoring-adjudicated-cell-size-control | new_truth | measurement_method | 6.00 | portfolio_pruned at F0 |
| g47_purpleair_twin_replicate_conditional_validity | new_truth | measurement_method | 5.60 | portfolio_pruned at F0 |
| g47_thermoelectric_cross_determination_bias_attribution | new_truth | measurement_method | 4.80 | portfolio_pruned at F0 |
| g47_inner_core_rotation_vs_deformation | unresolved_model_disagreement | measurement_method | 4.30 | portfolio_pruned at F0 |

F0 prune reasons (judge, spot-checked): cell-size-control — Genthon & Thomas 2026
(arXiv:2601.05193, mother-machine-vs-population context already shown to alter measured strategy)
plus Thiermann et al. eLife pipeline-robustness on the same asset; batch-doubling-time truth
contract cracked by sister-culture sourcing. PurpleAir — deSouza et al. 2022 (same asset,
twin-divergence degradation, descriptive) plus drift-adaptive conformal (G-DACP) jointly cover;
conditioning-conformal-on-replicate-features is a thin increment. Thermoelectric — Athar et al.
2025 (same archive, round-robin error filtering) plus ISO-5725 variance-components metrology;
method-identity field sparsity is the program's own expected killer. Inner core — Vidale et al.
2025 Nat Geosci already concluded rotation and near-surface deformation both operate; the
rigid-only H1 arm is born falsified; same-position recurrence control semi-circular.

## F1 screens (workflow wf_c5732056-071, 2 screeners, 638k subagent tokens)

### g47_sequence_plasticity_allocation_prediction — quick_close

Asset verification PASSED at claimed granularity (this is not an absent-instrument kill): DANDI:000617
v0.250312.0130 (CC-BY-4.0, 13 subjects, 5-day ABCABC design, relatedResource: [] — no primary
paper yet); the 3.6 MB assets.yaml manifest was fetched and enumerated exhaustively: 1,197 assets
= 599 raw-movie NWB files (21-24 GB each, 12.8 TB) + 598 processed ophys NWB files at MB scale
(ROI dF/F traces + stimulus tables), so trace-level analysis is real. Scoop probe found no 000617
primary analysis (DDG; unrelated arXiv hit only). Killers:

1. Analytic non-identifiability (decisive). Response is a binary per-neuron label
   "acquires calibrated-significant sequence selectivity"; the H1 feature set includes day-0
   reliability/SNR. Exact toy: for contrast statistic z_i = delta + sigma_i*eps_i with per-neuron
   noise sigma_i, P(label=1) is a monotone function of sigma_i ALONE under the scientific null of
   uniform allocation (pivotal calibrated statistic: decreasing, 1-G(c-delta*sqrt(n)/sigma_i);
   non-pivotal raw contrast below threshold: increasing, 1-F((c-delta)/sigma_i)). Day-0
   reliability/SNR features are monotone in the same sigma_i, so a classifier achieves AUC>0.5
   under H0, and the coupling is pipeline-shared so it transfers across held-out mice. The
   (features, labels) joint law is identical to H1 with a 1/sigma-type (or sigma-type) biological
   allocation rule: uniform biology x heterogeneous noise equals heterogeneous biology x uniform
   measurement. The proposers' escapes fail: SNR regression is errors-in-variables plus CDF
   nonlinearity (insufficient under H0, destructive under H1); surrogate calibration makes it
   worse — circular-shift surrogates are pivotal hence sigma-independent, so real-AUC >
   surrogate-AUC is manufactured exactly when the scientific null is true. Known repairs
   (continuous effect-size labels, split-half disjoint-trial noise estimates, within-SNR-stratum
   AUC) are standard practice, so the repaired program falls to the venue killer.
2. Venue increment. H1 branch is an eLife/Neuron-style systems-neuroscience finding
   (cross-animal AUC ~0.65-0.75 with off-the-shelf classification); H0 branch has no ML-venue
   home. Compounded by a 6-18 month scoop race with the producing lab on their own archive.
3. Occupancy (supporting): Mocle et al., Neuron 112(9):1487-1497, 2024 answers "do pre-learning
   features pick which neurons store the memory" causally (TRAP2/scFLARE2 tagging + optogenetic
   interference, dCA1); the archive version reads as dataset swap plus downgrade from causal
   identification to correlational AUC. Route-graph occupancy itself was clear (all 333 ids read;
   no cortex plasticity-allocation node).

### g47_whi5_start_pipeline_invariance — quick_close

Asset existence PASSED but granularity FAILED against the proposal's claim ("hundreds-to-thousands
of per-cell trajectories"): file-level enumeration of the five DataverseNL deposits gives
IVWACK = 34 individually tracked cells x 6 time points (3.8 MB); HNWBYM = 231 elutriated cells
each imaged ONCE (single-exposure snapshots, not trajectories); PKZZOJ = per-cell Cln3 columns,
glucose only (41.4 KB); TFC012 = Nup133 nuclear-volume cross-sections; SWRBYR = raw bleaching
movies (518.7 MB). No constitutive-reporter (ACT1/TEF1) per-cell trajectories are deposited at
all, so Y2 (synthesis-rate ratio) is not recomputable on the Litsios side; the 49 contested
wide-field traces were shared only privately with Schmoller, and Schmoller et al. 2022 state in
print that raw-level transfer was refused. Killers (any one sufficient):

1. Occupancy by capable parent: the 2022 MBoC exchange already ran the cross-pipeline
   reanalysis in both directions — Schmoller et al. 2022 reanalyzed Litsios' own 49 traces
   (44/49-cells decrease statistic) and published the exact alignment toy (their Fig 1B-D);
   Litsios et al. 2022 reanalyzed Schmoller's own ACT1 data (digitized slopes 4.58 early vs 15.9
   late) and showed alignment is removable via a per-cell dilution factor. Both off-diagonal
   cells of the program's transfer design are already published.
2. Analytic non-identifiability: all three named artifacts (photobleaching, nuclear-volume
   sub-scaling, partial-confocal effect) are common-mode across the entire specification union —
   monotone in G1 progression, parameterized by calibration quantities no analysis-choice axis
   touches. Hand arithmetic from the camps' own calibrations: mCherry cumulative bleaching
   (1-0.0029)^20 = 0.9435 (~6%); nuclear sub-scaling ~10% at 60% growth; combined ~15%, inside
   the 12-25% wide-field window BOTH camps concede. The specification union spans zero directions
   in the artifact subspace: H0+artifacts and H1+clean-measurement are observationally identical
   across the whole grid. The only identifying instruments (2p single-exposure slope -0.004
   +/- 0.005 on 231 cells; TCA mass spec; FRAP) lie outside the union.
3. Absent instrument at claimed granularity (above).
4. Design confound: specification x provenance perfectly aliased (strain, fluorophore, microscope
   modality, medium, protocol all alias with lab); with the actually-deposited material no
   matched-strata cross-camp contrast separates specification from provenance effects.
5. Venue increment: specification-curve analysis (Simonsohn, Simmons, Nelson, Nat Hum Behav
   4:1208-1214, 2020) is the capable generic parent; both outcome branches are Cell-Biology
   letters or robustness commentaries, not ICLR/ICML method papers.

Screener re-entry observation (recorded, not authority): the screen would NOT have killed a
reformulation "what new measurement identifies mechanism vs shared wide-field artifact in
single-cell fluorescence" — but that is a wet-lab program outside the no-new-collection lane.

## Honesty and tooling record

- WebSearch API 529/429 degradation persisted through both stages; all verification used the
  sanctioned fallbacks (WebFetch on arXiv/PubMed/eutils/DANDI/INSPIRE, Z.ai webReader MCP,
  DuckDuckGo HTML), recorded per anchor. Dataverse REST API was blocked by an Anubis bot-gate;
  dataset.xhtml file tables were read instead.
- Generator bookkeeping defects (caught by the judge, verified by me against the graph YAML):
  the sequence-plasticity generator cited occupied node g46_motor_tur_hidden_state_inference,
  which exists neither in the 333-node list nor in record-only — fabricated; the whi5 generator
  cited record-only g46_single_molecule_footprint_microstates as occupied (category error). Three
  other suspicious node references (dynamic_truth_pdebench_multi_kg,
  observation_truth_cylinder_primary_kg, calibration_reference_tlc_primary_kg) turned out to be
  real nested graph locator ids (lines 351/391/411), not fabrications.
- Granularity inflation: the judge verified asset existence/license at F0 but not file-level
  counts; the whi5 claim of "hundreds-to-thousands of per-cell trajectories" failed file-level
  enumeration at F1. Lesson for the next cycle: F0 asset verification must enumerate file tables,
  not confirm portal existence.
- Anchor verification upgrades this cycle: Barber/Amir/Murray PNAS 2020 from DDG snippet (F0) to
  full abstract + figure captions (F1); Mocle 2024 from listing snippet to full abstract plus
  efetch verbatim text; Tkalcic GRL 2023 remains snippet-only (Wiley 403), registered with that
  limitation.

## Counts

Paper G 107 formulations / 31 cycles / 0 cards (detailed 32 funnel cycles). Route graph unchanged:
333 top-level nodes (active=1, failed_closed=291, parked=14, passed_closed=26, superseded=1), 279
typed edges, 1995 evidence/artifact locators — no nodes added (both screens closed; no deferrals).
Evidence registry 1367 → 1390 (23 new entries: 18 primary works, 5 asset/archive records; the
GDACP dataset entry is counted once, under primary works).
Efficiency: 22 primary-source opens (17 primary works, tkalcic2023 snippet-only not counted,
plus 5 asset file-table verifications), 2 killer toys constructed, 3 reusable assets recorded
(mother-machine four-pipeline reprocessing control; DANDI:000617 embedded matched-order control;
DataverseNL Litsios deposits with measured granularity). Portfolio targets met without quota
pressure (4 measurement, 2 empirical, 0 theory; lanes 4 new-truth / 2 unresolved / 0 native / 0
cross-domain-theorem — the two zero-return generators are the honest-empty mechanism working, not
a lane failure).

## Failure-mode tally and next

Both screens died to analytic identification + venue, with occupancy as supporting fire; zero
deaths to pure route-graph occupancy (the F0 occupancy check worked), zero asset-existence
failures (asset-first worked at the existence level), one granularity failure (whi5). The
dominant residual pattern across Cycles 46-47: programs that survive occupancy die because (a)
the label/estimator construction is non-identifiably coupled to nuisance structure, or (b) the
answered question yields a strong domain-science paper with no learning-method increment. If a
Cycle 48 is allocated: generators must pre-state the venue-contribution sentence (what the
ICLR/ICML method contribution is, in one sentence, before the contract) and the F0 judge must
verify asset granularity at file-table level. No forecast (no F3 subject), no re-entry triggers
qualified, no execution, no simulation, no outcome access.
