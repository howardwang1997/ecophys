---
note: >-
  Verbatim output of a planning-workflow agent (2026-09-06), grounded in the frozen lab-asset-v3
  artifacts and the D-2 evidence map. Theorem status: propositions/proofs below are D-1 working
  material, NOT claimed results of the paper. Companion to
  ecomd_reexploration_experiment_plan_2026-09-06.md.
---

# D-1 killer-test specification and ops/compute plan (working material)

## Part A — red-team killer-test specification

# D-1 Red-Team Killer-Test Specification (GAMMA / ALPHA / merged)

## 0. Verdict

The GAMMA theorem family is well-armored against triviality attacks but **structurally exposed on exactly one front**: the static (single-event) per-unit equivalence class genuinely *is* a Diaconis–Sturmfels toric fiber, because probability-proportional-to-remaining-quantity draws without replacement give `P(interleaving) = prod_i q_i!/Q!` — uniform on interleavings, i.e., the multi-hypergeometric fiber with an adjacent-transposition Markov basis. KT-G1 forces this concession now, on paper, and forces T1's lead statement to rest on the obstruction that survives: forward non-lumpability of the aggregate tape for any flow whose submissions depend on own fills/inventory/cash (the lab-asset M1+ policy ladder), plus state-coupling of feasible draw sets across events. Neither exists in a fixed-sample-space sufficiency framework.

The ALPHA family is where the paper actually dies if it dies. The binding risks are **KT-A1 (attribution reduces to superiority: additivity holds everywhere on the grid)** and **KT-A4 (through-M results are surrogate artifacts)** — both documented hazards in this literature, both with kill probabilities around 0.30. The theorems are comparatively safe (0.05–0.20). Red-team conclusion: D-1 effort should be split roughly 40% theorem-side (KT-G1/G5 statements), 60% experimental-estimand side (KT-A1/A4 decision rules and the estimator menu), and the single highest-leverage engineering prerequisite is the dual-hash-validated fiber resampler, without which the KT-A3/KT-M1 gauge controls cannot run and the merged hostile-T0 forecast drops below the 0.15 activation floor.

## 1. Grounding facts pulled from the repo (all paths absolute)

- `/Users/howardwang/Desktop/playground/ecophys/experiments/lab_asset_a2/a2_exit_20260905/schema_spec.json` (schema_version `lab-asset-v3`, bundle manifest `fea8b136...9581c`): `state_hash` binds "prestate hash, full book with FIFO order, cash, inventory, induced counters, order metadata/status/parent, used client ids, latency choices, counters, last match tick and engine RNG state"; `aggregate_state_hash` binds "anonymous level quantities and totals only". This dual-hash contract is the ready-made, machine-checkable operationalization of T1's two tape granularities and of the "loss equivalence vs deployment distinguishability" split in T2/T3/KT-M1.
- Same spec, `execution` payload: `allocation_draw?` is optional. In the frozen fixtures, `allocation_draw` occurs only in `fixture_random_unit_within_price/tape.jsonl` (2 records, e.g., `{"eligible_units": 4, "maker_order_id": "O00000003", "price": 101, "selected_unit": 2}`) and never in `fixture_fifo/tape.jsonl`. Per-unit tape granularity is therefore a schema-level knob, not a new instrument.
- Event 7 across the two fixtures: same prestate-derived book (identical `pre_aggregate_state_hash` `da930600...`), FIFO arm executes quantity 2 from maker `O00000003` (maker_remaining 2); random_unit arm executes quantity 1 (maker_remaining 3) with the recorded draw. Kernel-dependent divergence from near-identical inputs is already visible in frozen data; note the fixture request streams differ slightly (21 vs 22 records), so KT-A2 must equalize inputs by replaying one recorded request subsequence through both arms — the replay contract ("re-execute the request events from the prestate; the regenerated tape must equal the recorded tape record-by-record") supports swapping only `allocation_rule` natively.
- `/Users/howardwang/Desktop/playground/ecophys/papers/proposal/ecomd_random_unit_priority_thesis_v2_2026-08-27.md`: the M0–M3 policy ladder ("M0 aggregate-lumpable: allocation identity never feeds back") is reused in KT-G1 as the exact boundary where the sufficiency reduction succeeds vs fails — internal coherence bonus: the same ladder that gated the human experiment gates the fiber taxonomy.
- `/Users/howardwang/Desktop/playground/ecophys/ecomd/models/ecomd_v2.py` (L1 lineage; note its own `gauge_enforce` history — the 2026-04-25 finding that enforcing the Ilinski log-price gauge killed vol-clustering facts is a live internal precedent for KT-G3's "no quotient repair" lemma: quotienting destroyed function-relevant information there too).
- `/Users/howardwang/Desktop/playground/ecophys/ecomd/training/fact_surrogates.py` (L2 lineage), `/Users/howardwang/Desktop/playground/ecophys/ecomd/eval/synthetic_dgps.py` (robustness DGP family; includes `garch_volume_coupled` — a resource-feedback DGP relevant to the KT-G1 policy-class condition).
- `/Users/howardwang/Desktop/playground/ecophys/research/discovery/forecast_ledger.yaml`: v1 schema with `target_id t0_activation_eligibility`, `activation_floor: 0.15`, `point_scoring_rule: brier`, entries carry `lower/point/upper` + `resolution_rule`. Section 5 gives ledger-ready entries.

## 2. Why each test is the strongest version of its attack

**KT-G1 (Attack A, sufficiency reduction).** The attack as a referee would actually run it: not "fibers exist elsewhere" (D-2 already cleared bare-fiber novelty vs DPIOT), but "your dichotomy is a corollary of statistic fineness." Split into three sub-reductions because they have opposite expected outcomes and the paper must treat them differently. R1 (static toric embedding) is expected to *succeed* by the uniform-interleaving computation above — the strongest red-team move is to concede it preemptively in scope, which converts the attack into a scoping discipline. R2 (dynamic sufficiency) is the load-bearing one: sufficiency theorems equate fibers across *all* downstream uses under the model; here the aggregate tape fails to be sufficient for the engine's own forward law exactly when policies are M1+ (two aggregate-identical queue compositions [A(q1),B(q2)] vs [B(q2),A(q1)] produce different next-event fill-split laws; under FIFO the split is a point mass at the queue-determined allocation, giving TV ≥ 1 − max_x p_x of the random-unit multi-hypergeometric split). The honest special case — M0 aggregate-measurable flows are lumpable and the reduction *goes through* — must be conceded and scoped; this makes T1 a theorem about the kernel × granularity × policy-feedback triple interaction, which no sufficiency framework states. R3 (aggregate+random collapse = marginalization) is genuinely a data-processing corollary and must be labeled the trivial direction so no referee can inflate it into the lead claim.

**KT-G2 (Attack B, triviality).** The unbounded version is dead on arrival (unbounded fiber diameter ⇒ any Lipschitz consumer diverges; the D-3 condition-adjusted framing already knows this). The only defensible lead is the bounded quantitative version, and its content test is sharp: two fibers with *equal reference-measure geometry budget* (equal second moment of pairwise separation under the without-replacement reference measure) but different directional composition (queue-composition-dominant vs uncleared-excess-dominant) must give provably different kernel-swap consumer variance — a factor ≥ 2 with explicit constants, against the matching generic `L × E[distance]` upper bound. The closed-form multi-hypergeometric fill-split variances make this provable, not hand-waved. Component (ii) is cheap and absolute: T2's premise ("exactly zero training-loss difference") must be bit-exact by construction, and the dual-hash contract plus a static audit of the loss code makes "exact" machine-checkable rather than asserted. Any loss term reading per-unit/per-maker fields silently falsifies T2's premise.

**KT-G3 (Attack E, theorem half).** The gauge attack is the strongest philosophical attack on the whole program because the repo has its own gauge-injury precedent (v2 `gauge_enforce` destroying vol clustering). The defense must therefore be a lemma pair, not prose: (A) gauge symmetries live in the kernel of *every* deployment map; the mechanism fiber provably does not (identity map sees nothing, kernel swap separates members — the two-state construction gives the TV bound). (B) no quotient/canonical-interleaving repair preserves the D_k-composed prediction map, because D_k *reads* the suppressed coordinates — quotienting destroys rather than relocates the information. This positions exactly against Quotient-Space Diffusion (ICLR 2026) and Neural Mechanics (ICLR 2020) and upgrades the V4 remark to citations of proven lemmas.

**KT-G4 (added attack, parameterization artifact).** A transversality-literate referee notes that generic nonlinear parameterizations make preimages zero-dimensional, so positive-dimensional fibers can be an artifact of the linear chart. The test forces T1 to be stated over the admissible flow × draw space with the chart demoted to a convenience; prongs (a)–(c) (strict shrinkage, non-collapse via exchangeable relabeling, parameterization-free marginalization) must hold chart-free, and (d) (positive dimensionality) must be explicitly marked chart-dependent with DPIOT cited as owner of that residue. This is the cheapest way to survive a real ICLR attack.

**KT-G5 (added attack, contrived-D vacuity).** "For any loss-invariant fiber you can contrive a separating map." The discharge is a characterization, not an existence proof: exposed(D_id) = ∅, exposed(D_k) and exposed(D_tr) nonempty, proper, and pairwise distinct (truncation at horizon h cannot see composition effects postponed past h; kernel swap reads cumulative composition). All D restricted to the preregistered three, each a function of the recorded tape plus the deployment perturbation only. If all exposed sets are equal or trivial, T3 collapses into T2 and the "market-native generalization absent in PDEs" sentence dies with it.

**KT-A1 (Attack C, estimand boundary).** The strongest version gives the attack its best shot at killing: preregister the *kill pattern* (|I| ≤ δ/2 everywhere, no sign opposition, surgery antisymmetric — i.e., a single scalar superiority index explains the grid) as an explicit, reachable outcome, not a strawman. The three attribution-only patterns P1/P2/P3 are chosen because each is *inexpressible* as a scalar comparison: P1 (opposing-sign train/infer credits) nets to an approximate null under superiority; P2 (pure interaction, no main effects) reads as total null under superiority; P3 (surgery hysteresis on locked checkpoints) has no superiority analogue at all, since a map-only theory predicts add-M/remove-M antisymmetry. The decision rule is frozen per cell × axis × DGP × lineage with the inherited contract (seed = inference unit, 50k paired bootstrap, δ = 0.1 × mean(R00), Holm-corrected sign-flip secondaries, one-shot analyzers).

**KT-A2 (Attack D, M-level).** Split from KT-A3 deliberately: "re-plugging an engine" is an attack on the *manipulation*, and it is answered at the M level with identical inputs (same prestate, same request subsequence, only `allocation_rule` swapped — the replay contract's native operation), a closed-form TV separation lemma (point mass vs multi-hypergeometric: TV ≥ 1 − C/√k), and the single-maker negative control that removes every non-priority explanation. If disagreement on multi-maker executions sits at the single-maker control level, the swap is plumbing and no cube-level result can rescue the axis.

**KT-A3 (Attack D, cube level / T3 bridge).** The bridge claim is operationalized as a *contrast*, which is what makes it falsifiable: locked-checkpoint kernel swap must move outcomes > δ while within-kernel fiber resampling (draw-level regeneration, aggregate tape held fixed, dual-hash-validated) moves them < δ/10. Swap ≈ resample would mean the "kernel-swap direction" is just generic draw noise — exactly the engineering accusation. The identity-readout ablation (M removed, retrained, 30 paired seeds) is the mechanism-attribution control: swap effects must vanish without M.

**KT-A4 (added attack, surrogate artifact).** Named and documented (Onoda ICLR 2026; Minimizing Surrogate Losses for DFL 2025: LP/integer objectives have zero a.e. gradient). The D-2 condition already requires preregistering estimator handling; this test adds the teeth — a two-estimator retrain of one mandatory audit cell, with preregistered downgrade-to-estimator-conditional if attribution sign patterns flip. Skipping this hands a hostile referee a guaranteed kill later.

**KT-A5 (added attack, portability).** Uses the cube as designed; adds only the frozen sign-reproduction standard (signs, not magnitudes) for L1→L2 and primary→robustness DGP, and the honest report rule (failed transfer = boundary, never pooled; U-Net lesson). The family-level kill condition is cross-linked to KT-A1: portability failure with significant pairwise superiority everywhere is the estimand-boundary attack confirmed from a second direction.

**KT-M1 (Attack E, empirical half).** The gauge-twin attack survives KT-G3's lemmas empirically only if deployment maps actually separate fiber members in the trained systems. All inference-time on locked checkpoints (cheap, fits envelope). The dual-hash resampler makes "within-fiber pair" a machine-checkable relation: identical `aggregate_state_hash` sequence, differing `state_hash`. The gauge-repair falsification (canonical-interleaving fix fails to restore D_k invariance) is the empirical twin of KT-G3 Lemma B and the direct answer to "just quotient it."

**KT-M2 (added merged attack, genre-template reduction).** Duruisseaux et al. 2024 must be cited as genre parent anyway; the attack is "the cube is that template on a matching engine." The discharge is a written template-expressibility table now, plus preregistered confirmation of at least one template-inexpressible pattern class: competing-mechanism swap surgery (the parent swaps a projection of the *same* physics), kernel × enforcement interaction on OOD axes (no OOD factor in the template), fiber-resampling control. One confirmation discharges KT-A1 or KT-A3 or KT-M1 simultaneously — the tests are correlated by design, which is efficient, and the correlation is flagged so the forecast does not multiply them independently.

## 3. Legality split (screening stage)

Legal now (theorem/literature/schema work, no execution): KT-G1, KT-G2(i) derivation + KT-G2(ii) static code/schema audit of frozen files, KT-G3, KT-G4, KT-G5, KT-M2 template table, and writing all empirical protocols into frozen macros. No GPU, no engine execution, no data access. The dual-hash static audit reads only files already in-repo.

Post-D0 (preregistered, run only after outcome-blind freeze + explicit PI authorization): every empirical stage — KT-A1 analyzers, KT-A2 stage 2 replay, KT-A3 contrasts, KT-A4 audit-cell retrains, KT-A5 evaluation, KT-M1 deployment experiment.

## 4. Prerequisites and compute check

1. **Fiber resampler** (new instrument extension): regenerates without-replacement interleavings holding the aggregate tape fixed; acceptance criterion = identical `aggregate_state_hash` sequence with differing `state_hash`; needs its own conformance tests alongside the existing 27. Requires its own authorization decision before D0 — it is the single highest-leverage prerequisite (KT-A3 and KT-M1 controls depend on it).
2. **Estimator menu frozen into macros** (KT-A4) before D0; exact configs hashed.
3. **Disk cleanup** on both V100 nodes (98%/96% full) is a hard prerequisite before any run.
4. Compute: incremental cost over the cube = one 30-seed audit-cell retrain under a second estimator (KT-A4) + one 30-seed identity-readout ablation arm (KT-A3) + inference-time-only analyzers (KT-A1/A2/A5/M1). Roughly +2 arms over a Paper-D-sized 4-arm × 30-seed × 2-model grid, inside the ≈2× Paper D ceiling (~4 weeks wall-clock on 2×V100).

## 5. Hostile-T0 forecasts (ledger-ready, `research/discovery/forecast_ledger.yaml`, target `t0_activation_eligibility`, floor 0.15)

Per-test kill probabilities (correlations noted; do not multiply independently — KT-A1/A3/M1/M2 share the same underlying grid, KT-G1/G4 share the T1 statement):

| test | P(kill claim) | [lower, upper] |
|---|---|---|
| KT-G1 | 0.20 | [0.10, 0.35] |
| KT-G2 | 0.15 | [0.08, 0.30] |
| KT-G3 | 0.05 | [0.02, 0.15] |
| KT-G4 | 0.10 | [0.05, 0.22] |
| KT-G5 | 0.20 | [0.10, 0.35] |
| KT-A1 | 0.30 | [0.15, 0.50] |
| KT-A2 | 0.05 | [0.02, 0.12] |
| KT-A3 | 0.25 | [0.12, 0.45] |
| KT-A4 | 0.30 | [0.15, 0.50] |
| KT-A5 | 0.20 | [0.10, 0.40] (kills two-lineage claim only) |
| KT-M1 | 0.20 | [0.10, 0.40] |
| KT-M2 | 0.30 | [0.15, 0.50] (correlated with KT-A1/A3) |

Recommended entries:

- `d1_gamma_theorem_structure_survival` — lower 0.55, point 0.75, upper 0.88. Resolution: true iff none of KT-G1..G5 forces demotion of T1/T2/T3 below lead-theorem status (re-scoping with the obstruction lemmas intact counts as survival; T1 demotion to scoped proposition counts as false).
- `d1_alpha_attribution_estimand_survival` — lower 0.18, point 0.35, upper 0.55. Resolution: true iff at least one of P1/P2/P3 confirms under the frozen KT-A1 rule with KT-A4 estimator stability holding; false iff the kill pattern obtains or estimator instability forces the conditional downgrade.
- `d1_merged_gammas_led_paper_gate` — lower 0.18, point 0.34, upper 0.55. Resolution: true iff GAMMA structure survives AND at least one template-inexpressible pattern class confirms (KT-M2). Clears the 0.15 activation floor with thin margin; the margin is carried almost entirely by the ALPHA estimand, not the theorems. If the fiber resampler is not authorized, this forecast drops to lower ≈ 0.10 (below floor) because KT-A3/KT-M1 contrasts become unrunnable — flag this dependency in the ledger `resolution_rule`.

## 6. Claim → test discharge map

- T1 lead status: KT-G1, KT-G4. T1 scope (static toric concession, M0 concession): KT-G1.
- T2 bounded lead version + premise: KT-G2 (i) and (ii).
- T3 characterization: KT-G5; empirical content: KT-A3, KT-M1.
- V4 gauge remark (upgraded to lemmas + experiment): KT-G3 + KT-M1.
- ALPHA attribution estimand: KT-A1 (primary), KT-A5 (secondary direction).
- Kernel-swap OOD axis: KT-A2 (manipulation validity), KT-A3 (scientific content).
- Through-M arm credibility: KT-A4.
- Genre-parent positioning / never-claim: KT-M2.
- T4 stays conjecture-only; no test assigned by design (any within-fiber drift measurement remains exploratory per D-3 framing — do not promote it under D-1 pressure).

---

## Part B — ops and compute plan

# ALPHA Cube — Ops & Compute Plan (merged paper, GAMMA-led)

All designs are preregistration-ready: every number below is freezable at D0 before any GPU run. Nothing here authorizes execution; Stage launches require the D0 outcome-blind freeze plus explicit PI authorization.

## 0. Cost model (frozen anchors, grounded in repo evidence)

Anchor unit **T = 1.8 V100-h = one Paper-D training run** (Paper D: ~672 nominal V100-h for 240 training runs at 4 arms x 30 seeds x 2 model types in ~2 weeks; observed campaign efficiency ~65-70% after the two nonfinite incidents, the confirmation-failure continuation, and the HTTP2 transfer incident recorded in `experiments/constraint_attribution_iclr/deployment/`).

Scale factors vs Paper D res-64 PDE models (design point inherited from `configs/constraint_iclr/market_confirmation.yaml`: n_agents 16, episode 64 steps, 100 epochs, batch 512; horizons {1,4,16,64} as in `pde_confirmation.yaml`):

| Item | V100-h | Basis |
|---|---|---|
| L1 (EcoMD v2 transformer/potential, `ecomd/models/ecomd_v2.py`) raw-train arm, n_train 2048 | 2.2 | 1.2 T |
| L1 through-M arm (exact integer clearing + per-unit allocation tape + k-replay/surrogate gradients; LP-integer zero-gradient handling preregistered per Onoda ICLR 2026 / DFL-surrogate 2025) | 3.2 | 1.5x raw |
| L2 (recurrent fact surrogate, `ecomd/training/fact_surrogates.py`) raw arm, n_train 4096 | 0.7 | 0.4 T |
| L2 through-M arm | 1.1 | 0.6 T |
| Eval pass = 1 cell x 1 condition, 4 horizons, 64 episodes + tape emission | L1 0.04 / L2 0.015 | inference-only |
| DGP corpus generation per (DGP, 30 data_seeds, dual-arm) | 18 | exact engine; rate gate at preflight |
| Per seed per DGP: training both lineages | 10.8 + 3.6 = 14.4 | 4 arms each |

Eval conditions (8, frozen): `ID`, `pop_2x`, `pop_4x` (16->32->64 agents), `tick_2x`, `tick_half`, `kswap` (FIFO<->random-unit inside the D1 dual-arm engine — bridges T3, exercises the T1 granularity dichotomy via the per-unit tape arm), `trunc_lag`, `trunc_cap` (T3 latency/message-truncation deployment maps). Cells (8, Paper D vocabulary): R00/R01/R10/R11 (raw-train) and A00/A01/A10/A11 (through-M-train), index = inference enforcement; the four off-diagonal-enforcement combinations are the zero-training surgery cells on locked checkpoints.

## 1. FULL run grid and wall-clock table

Full enumeration: **2 lineages x 2 DGPs x 4 trained arms x 30 paired seeds = 480 training runs**; 4 surgery cells per trained checkpoint (inference-only); 8 eval conditions x 8 cells x 4 horizons; stylized-fact vector (`ecomd/eval/stylized_facts.py::compute_all`) on ID + kswap tapes (T2 raw-flow risk-aggregation consumer); reflexive cell (simulator vs simple adapting execution policy; exploratory, 10 seeds, cells {R00, R11}, D1, both lineages); T4 drift = exploratory measurement on retained intermediate checkpoints (10-seed subset).

| Block | V100-h | Days @100% (2 GPUs) | Days @70% eff. |
|---|---|---|---|
| Preflight: cleanup verification, focused tests, seed-999 CUDA preflight, dry-run composition | 15 | 0.3 | 1 |
| DGP corpora: D1 lab-asset-v3 (dual-arm) + D2 synthetic (2 variants) | 48 | 0.5 | 1 |
| Training D1 (30 seeds x 14.4) | 432 | 4.5 | 6.4 |
| Training D2 (variant A both lineages 15 seeds x 14.4; variant B L2-only 15 x 3.6) | 270 | 2.8 | 4.0 |
| Eval/surgery/stylized-facts D1 (30 x 3.2) | 96 | 1.0 | 1.4 |
| Eval D2 (15 x 2 x 2.4, 6 conditions) | 72 | 0.75 | 1.1 |
| Reflexive cell (10 seeds, 2 cells, 2 lineages) | 6 | 0.06 | 0.1 |
| T4 drift analysis + retention overhead | 2 | — | — |
| One-shot analyzers (50k-draw paired bootstrap, ~1,000 estimands; CPU, overlapped) | 12 | 0.25 | 0.4 |
| Incident/re-run margin (20%; Paper D actually used it twice) | 218 | 2.3 | 3.2 |
| **FULL GRID TOTAL** | **~1,371** | **~14.3** | **~20.4** |

Nominal full grid ~= the 4-week ceiling exactly; at the Paper D observed ~70% campaign efficiency it is ~20 days of pure compute with zero schedule room for the mandatory governance sessions, analyzer freeze, and R2 verification. **Conclusion: the full grid is not schedulable inside the ceiling; run it as two pre-registered stages (below).**

## 2. Recommended grid (two stages, mechanical triggers only)

### Stage 1 — confirmatory core (D0-frozen, target ~2.5-3 weeks)
D1 lab-asset-v3 only; both lineages; 4 trained arms each; **30 paired seeds** (contract verbatim: seed = inference unit; 50,000-draw paired bootstrap; SESOI = 0.1 x mean of R00; ordered classification; Holm across the 8 mandatory cells); all 8 eval conditions on L1, 6 on L2 (drop `trunc_cap`, `pop_4x` on L2); reflexive cell exploratory-only (analyzer exclusion list frozen); T4 drift exploratory.

| Stage 1 | V100-h |
|---|---|
| Preflight 15; corpora D1 18; training 432; eval 88; reflexive 6; drift 2; analyzer 8; margin 15% (~81) | **~650** |

Wall-clock: ~13.5 days @100%, **~19-20 days @70%** with lineage-parallel streams (GPU-a = L1 queue, GPU-b = L2 queue then eval/surgery interleaving). The 2-week target is reachable only at >=90% incident-free utilization; plan for 3 weeks, hold 4 as the hard ceiling.

### Stage 2 — conditional robustness block (pre-registered, ~12 days)
D2 synthetic_dgps (`dgp_registry`): variant A (garch-family) both lineages, variant B (multiscale-logvol) L2-only, **15 paired seeds**, 6 conditions, reduced Holm family preregistered as directional-replication block.

| Stage 2 | V100-h |
|---|---|
| Corpora 12 + 6; training 270; eval 70; analyzer 4; margin 15% (~53) | **~410** |

**Mechanical triggers (frozen; no outcome-direction inputs):** cumulative burn < 1,150 V100-h; Stage 1 complete by D0+26d; L1 convergence-failure rate <= 15% (quality gate, not performance); L2 trainability/transfer gate passed (finite-loss trainability on D1, else report failed transfer as boundary per the U-Net lesson). Shrink ladder: slip > 5d -> variant A only at 12 seeds; slip > D0+26d or burn > 1,150 -> cancel Stage 2.

### Cuts and what each forfeits (mapped to claims)
- **D2 deferred to Stage 2 / canceled:** forfeits the robustness-truth leg; experimental section scoped to lab-asset-v3 single family; ALPHA design element "two DGPs" reported as a deviation; ordered-classification table loses DGP-robustness support. T1/T2/T3 theorem content unaffected (GAMMA carries them); T2 mechanism-attribution stands on D1; T4 unaffected (conjecture).
- **L2 drops `trunc_cap`, `pop_4x`:** forfeits lineage-consistency of the truncation-depth direction and population dose-response on L2 only; T3 truncation evidence still carried by L1 both directions.
- **Stage 2 at 15 seeds:** forfeits confirmatory-grade sign-flip power on the robustness block (preregistered as directional; no material-nonadditivity claims from Stage 2).
- **Variant B L2-only:** forfeits L1 x second-synthetic-variant cross.
- **Reflexive exploratory-only:** no confirmatory loss (by design; TRADES 2025 / DEX 2026 cited for paired-seed discipline).
- **Never cut:** the 8-cell cube x 30 seeds on D1 both lineages (core estimand = path-dependence attribution, the three-way interaction), `kswap` and both truncation conditions on L1 (T2/T3 bridges), the surgery cells (T2 within-fiber evidence), all-cells/all-axes/all-lineages reporting incl. class flips and nulls.

## 3. Ops prerequisites checklist (hard gates, in order)

1. **Disk cleanup (hard prerequisite; nodes 98/96% full).** Working set needs ~300-500 GB (480 final checkpoints x 0.15-0.5 GB + corpora + logs). Target **>= 40% free on both nodes**. Procedure: every artifact in `experiments/constraint_attribution_iclr/deployment/*.files + *.sha256s` re-hash-verified -> uploaded to `r2://ecophys/paper_d_archive/` -> manifest-verified -> local delete -> re-verify. Nothing without a manifest is deleted. Cleanup scripts authored and dry-run (listing/hashes only) on Mac pre-D0; node execution is authorized op-session 1 at D0.
2. **R2 immutable staging** at `r2://ecophys/alpha_cube_d0_YYYYMMDD/`: lab-asset-v3 bundle verified against manifest `fea8a136...9581c` (`experiments/lab_asset_a2/a2_exit_20260905/`, 27 conformance tests + replay validator re-run on both nodes); frozen Hydra configs per (lineage, DGP, arm, condition); frozen seed file; analyzer macros; corpora after generation. Byte-exact re-derivation check on both nodes (lab-asset-v3 replay guarantee).
3. **CRN / paired-seed protocol.** Frozen master seed file: per (lineage, DGP, seed-index i in 0..29) a triplet (data_seed, init_seed, train_seed), sha256'd at D0. data_seed shared across all 4 arms (shared trajectories); train_seed drives a shared minibatch-order stream; init tensors shared where shapes match. Substreams via `numpy SeedSequence.spawn`. Analyzer rejects any record whose config_sha256/seed tuple breaks the pairing (record-coverage gate). Seeds 1000-1029 (D1) / 2000-2014 (D2) continuing repo convention.
4. **Checkpoint retention.** Final locked checkpoints for ALL runs: CPU-offloaded, optimizer-stripped, sha256 into the run manifest, retained until paper acceptance (surgery cells read only these; analyzer enforces `checkpoint_lock_sha256`). Intermediate 30-min checkpoints (`train_distributed` state-complete format incl. RNG) retained only for the 10-seed T4 drift subset; all other intermediates deleted after per-run verification. Disk-pressure rule: intermediates go first.
5. **Verifier machinery (Paper D receipt pattern).** Launch receipt per stage with: machine-decision sha, snapshot sha, selection-lock sha, source git head; gates = archive + per-file hashes, focused tests (>= 25, target the repo's 78), seed-999 CUDA preflight on both nodes, first-record gate (10 records / 5 seeds / both enforcement mechanisms), log error scan, corpus-gen rate gate; `outcome_access: metric_values_printed_or_inspected: false`, no early analysis, frozen analysis only after both workers complete.
6. **Conda env.** `ecophys` spec (Python 3.11, PyTorch 2.3+) synced to both nodes; `pip freeze` hash in manifest; Mac used only for editing + smoke (N <= 500).
7. **One-shot analyzers.** Frozen macros; record-coverage and checkpoint-lock gates; SESOI computed per (lineage, DGP, horizon) as 0.1 x mean R00; ordered classification {material_nonadditivity / statistical_nonadditivity_below_or_crossing_sesoi / practical_additivity / unresolved}; sign-flip Holm across the 8 mandatory cells; reflexive + T4-drift estimands on the frozen exclusion list; no analyzer reruns (any rerun = PI deviation memo).
8. **Forecast ledger (D-1 input).** Ops supplies compute-feasibility and convergence-risk bases for the calibrated hostile-T0 forecasts to `research/discovery/forecast_ledger.yaml` before D0 (Paper D precedent: nonfinite incidents on both hosts and one failed confirmation are the empirical priors for the 20% margin and 15% halt rule).

## 4. Failure containment

- **Job granularity = one (arm, seed) run** (<= 3.2 V100-h each): a crashed run costs hours, not days. Per-host jsonl with per-run status (Paper D `checkpoint_records` pattern); queues migrate across nodes freely since corpora and configs are R2-staged and identical.
- **Checkpoint resume:** 30-min state-complete checkpoints (simulator + optimizer + scheduler + RNG + iter); resume validates world_size and rank-RNG match (`train_distributed` format checks); failed-integrity resume -> re-run that (arm, seed) from scratch from the margin budget.
- **Seed regeneration rule:** completed seeds are never regenerated; only missing/incomplete (arm, seed) tuples re-execute. Data corpora are immutable — a lost corpus file is re-derived from its frozen data_seed and must match the R2 manifest byte-exactly, else halt.
- **Nonfinite incidents (occurred on both Paper D hosts):** auto-detect, mark run failed, one auto-resume attempt, then human look. Per-run loss of a seed removes that seed from the paired bootstrap for ALL arms of that seed-index (pairing preserved); **halt rule: > 3/30 seeds lost on any mandatory cell -> stop, PI decision** (never silent seed substitution).
- **Salvage order on node death:** (1) final checkpoints + eval jsonl records -> R2 incremental after every stream drain; (2) drift-subset intermediates; (3) logs last. A node that dies with undrained queues loses at most its in-flight run plus <= 30 min of checkpoint.
- **Reflexive-cell failure containment:** exploratory; any failure is reported as such, never blocks the confirmatory analyzer.

## 5. Timeline (sessions from D0; 3-week plan, 2-week stretch, 4-week hard ceiling)

| Session | Days | Content |
|---|---|---|
| Pre-D0 (Mac, legal now) | -3..0 | Author Hydra configs (all lineages/DGPs/arms/conditions), frozen seed file, analyzer macros + dummies, reflexive policy impl + Mac smoke (N<=500), cleanup dry-run scripts, R2 layout, Stage-2 trigger text; contribution to forecast ledger; freeze + hash everything |
| D0-S1 | 0-1 | Node cleanup -> R2 relocation -> verify >= 40% free; env sync + pip-freeze hash; focused tests; seed-999 CUDA preflight; launch receipts |
| D0-S2 | 1-2 | D1 corpus generation (dual-arm, 30 data_seeds) + byte-exact re-derivation validation on both nodes |
| D0-S3 | 2-16 | Stage-1 training streams (GPU-a L1, GPU-b L2); eval/surgery interleaved as finals lock; first-record gate at day 2-3; reflexive cell days 14-16; drift subset retention |
| D0-S4 | 16-17 | Record-coverage + checkpoint-lock gates; one-shot analyzer execution (frozen macros); Stage-2 go/no-go via mechanical triggers |
| D0-S5 | 17-28 | Stage 2 (if triggered): D2 corpora, training, eval, analyzer; else buffer/verification |
| D0-S6 | 28-29 | Final manifests, per-file hashes, R2 upload, freeze audit, work log, session commit |

Critical path: D0-S3 (training). The 2-week target holds only with zero nonfinite incidents and >= 90% stream utilization; the plan is resourced for 3 weeks with the 4-week ceiling reserved for the pre-registered Stage-2 shrink ladder, not for slippage.
