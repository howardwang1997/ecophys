# Re-exploration experiment & theory plan: merged GAMMA-led paper (2026-09-06)

Stage: D_minus_2→D_minus_1 transition planning under decision `pi_topic_reexploration_directive_20260906`.
This is the freeze-ready plan for the merged paper (merge gate recorded in
`ecomd_reexploration_d2_evidence_map_2026-09-06.md` §4): GAMMA theorems T1–T3 carry the science;
the ALPHA eight-cell cube is the experimental section and the attribution instrument for T2/T3.

**Legality tags:** [NOW] = theorem/literature/schema work, legal at screening stage. [AUTH] =
requires D0 outcome-blind freeze + explicit PI authorization (no GPU, no simulation execution, no
data access before then). Nothing in this plan is standing authorization.

Companion documents (same 9-agent planning workflow, full texts):
- `ecomd_reexploration_theory_appendix_2026-09-06.md` — T1 and T2/T3 theorem packages with
  derivations grounded in the frozen lab-asset-v3 artifacts.
- `ecomd_reexploration_contract_v1_2026-09-06.md` — statistical contract port, FROZEN CONTRACT v1
  (C1–C16, gates G1–G12).
- `ecomd_reexploration_d1_killer_tests_and_ops_2026-09-06.md` — red-team killer-test
  specification (12 tests) + ops/compute plan.

Three planning inputs (risk-minimal / rigor-maximal / theory-led drafts) are superseded by this
synthesis and remain in the session task record, not the repo.

---

## 1. Synthesis rulings (conflicts resolved; strongest element taken, not averaged)

| # | Conflict | Ruling | Why / rejected alternative |
|---|---|---|---|
| 1 | Training grid size | 4 trained arms (A-R, A-M, I-R, I-M) + 4 zero-training surgery cells on locked checkpoints; **Stage 1 = 240 trainings** (D1, both lineages, 30 seeds) — exactly Paper D's 240-checkpoint precedent | Rejected risk-minimal 144-run grid (24/12/12 seeds): violates verbatim 30-seed contract, drops Holm calibration and the D-1 two-lineage gate for ~10 GPU-days the ops arithmetic shows we have. Rejected rigor-maximal 750-run factorial: self-flagged 30–35% over ceiling |
| 2 | Staging | **Two-stage** split: Stage 1 confirmatory = contract blocks B1 (L1×lab-asset) + B3 (L2×lab-asset), 30 seeds; Stage 2 conditional robustness = B2/B4 (synthetic), preregistered first-15-seed subsets, **mechanical triggers only** (burn <1150 V100-h; Stage 1 done by D0+26d; L1 nonfinite ≤15%; L2 trainability pass). Never outcome-triggered | Full 480-run grid ≈1371 V100-h ≈ ceiling exactly, zero slack (ops). Contract C1/C14 amended; recorded in C16 ledger (items 11–12) |
| 3 | Seeds/pairing | Contract C1 verbatim: seed = frozen RNG-tree root (data/init/minibatch/train_kernel/kernel:1..8); K=8 replayed across cells within a seed; per-seed value = K-draw mean; deterministic decode; ranges 11000–11029 / 12000–12029; Stage 2 uses frozen first-15 subsets | DGP frozen in **M0/M1-lumpable policy class** at D0 → exact request-level CRN (the load-bearing pairing assumption) |
| 4 | Horizons | **{1,4,16,31}** (contract C4) confirmatory; horizons-inside-one-rollout-record mechanics (record economy); h=64 recorded descriptively only | Contract is statistical authority; mandatory family 16 = 4 axes × 4 horizons calibrated to it |
| 5 | Eval axes | Contract's 4 axes (ID, pop 2N, tick 2Δ, kswap FIFO→random_unit) = 16-cell mandatory family/block; truncation conditions (trunc_lag, trunc_cap) added as deployment-map passes carrying orderings O-C/O-D as a preregistered secondary Holm family (3 tests/block). pop_4x, tick_half, reverse/pro-rata swaps → exploratory | T3's truncation map needs the trunc conditions the contract lacked; keeps confirmatory machinery verbatim |
| 6 | Through-M estimator | **Primary = straight-through, pinned scale** (forward exact M; backward identity-on-cleared/zero-on-uncleared — Paper D rank-one gauge generalized, literally T2's minimal special case). **Audit = perturb-and-MAP, pinned noise** (KT-A4 menu). Both hashed pre-D0; two-estimator retrain of audit cell (increment, M-train, raw-infer, D1, 30 seeds) [AUTH]; frozen downgrade = estimator-conditional reporting with both shown | Rejected single-estimator lock (hands referees the documented surrogate-artifact kill) and full 3-way menu (compute) |
| 7 | Through-M corpus | **F_exec** (execution payloads + allocation_draw + pre/post BBO prices) — the highest-leverage freeze item | Under F_full/F_exec+orders the fiber collapses toward a point and T1–T3 are vacuous |
| 8 | Theory leads | T1 = P4 interaction grid + market-native dimension formulas + exposure asymmetry; **deterministic shrinkage demoted to sufficiency corollary** (cite Diaconis–Sturmfels 1998; contingency-table fibers 2014; DPIOT; Perturb-Argmax arXiv:2406.02180). T2 = **bounded Theorem 1 lead** (proven: exact floor R²‖v_U‖²/12, tight minimax, tape-computable constants); unbounded = Corollary 2 only. T3 = exposure propositions incl. exact swap asymmetry (swap→ru Θ(δ/S); swap→fifo exactly blind). T4 conjecture only | From the T1 hostile-reduction verdict + T2/T3 package; KT-G1's static toric concession (uniform interleavings, P=∏q_i!/Q!) written into T1 scope [NOW]; the **forward non-lumpability obstruction for M1+ flows is the must-prove pre-D0 lemma** — no input proved it yet |
| 9 | Compute model | Conservative GPU-h anchors (T=1.8 V100-h; L1 raw 2.2 / through-M 3.2; L2 0.7/1.1) AND throughput mechanics (contingent calendar ladder; all-cells table where unrun cells surface as "not run"/"unresolved", never dropped) | Both models reproduce Paper D's ~2 weeks; conservative GPU-h + throughput discipline covers both failure modes |
| 10 | Hostile-T0 forecasts | Red-team ledger entries adopted (most granular, correlations flagged, floor-compliant); risk-minimal 0.17 and theory-led 0.22 lower bounds recorded as sensitivity notes only | See §8 |

## 2. Frozen design

**Grid.** 8 cells = 4 trained arms × 2 inference enforcements; surgery cells read sha256-locked
checkpoints, zero optimizer steps, parameter parity byte-identical. Estimand = path-dependence
attribution **J = D00 − D10 − D01 + D11**; no confirmatory through-M-vs-raw superiority test
anywhere.

**DGPs.** D1 = lab-asset-v3 dual-arm engine (bundle manifest fea8a136…9581c; 27 conformance
tests; replay validator; schema lab-asset-v3) as primary truth, with a frozen M0/M1-lumpable
request generator (episodes, actor mix, rates, bands, master seeds hashed at D0). D2 = synthetic
robustness, Stage 2 only: variant A `garch_student_t5` (both lineages), variant B
`multiscale_logvol` (L2-only), each through a frozen series→request wrapper into the **same
engine** (conservation/replay semantics preserved). `negative_jump_iid` named-but-not-run.

**Lineages + gates.** L1 = ecomd_v2 transformer/potential; L2 = recurrent fact-surrogate. Both
ship frozen simulator contracts (input grammar; ABS/INC semantics; enforcement path + estimator;
RNG wiring; torch-loadable checkpoint format; pass the 27 conformance tests + replay validator).
Day-5 trainability quality gate (NaN ≤5% at long rollout; R00 val ≤3× L1 seed-median; ≥28/30
seeds complete) [AUTH] = early warning only. Preregistered **transfer gate stays contract C9**:
B3 passes iff primary J material AND ≥8/16 mandatory cells material (Paper D 6/12 fraction
preserved); failure = boundary report (U-Net lesson), claims scoped L1.

**Endpoints (each mapped to its claim).**

- **EP1 primary** [AUTH]: B1, kernel-swap axis, horizon 16. Ordered classification vs
  δ_s = 0.1·Ȳ_R00(s); channel-scaled conserving-rollout RMS (frozen DGP-native scales);
  reference-degeneracy guard (<1.0 scaled unit → "unresolved (reference-degenerate)"); fallback
  strata B1-kswap-h31, B1-tick-h16, B1-pop-h16. Supports the ALPHA attribution estimand and
  Prop 3.5's criterion.
- **EP2 (T2/T3 money results)** [AUTH]: on locked checkpoints and S1a fiber pairs — O-A
  attribution floor (consumer RMSE ≥ precomputed R‖v_U‖/√12; raw arms at noise ceiling); O-B swap
  asymmetry (swap→ru > 0 vs swap→fifo point null, equivalence-tested); O-C truncation
  monotonicity vs precomputed curve; O-D granularity fingerprint incl. the preregistered
  **exact-zero null cell** (price-notional on ru splits); O-E tape-measurable controls (zero
  interaction). Distinguishes mechanism fiber divergence from representational failure (Do LLMs
  Understand LOB 2026) and operator set-identification (Counterfactual Operator Relevance 2025)
  via the three rescue levers.
- **EP3 = S3 exact FIM rank grid** [AUTH, CPU-exact]: 3 kernels × 3 rungs × V*∈{1,2,4,6} in R⁹,
  frozen τ=1e-8, one-shot; preregistered ranks: agg=3 all kernels; fifo-po 3,3,3,4; pro_rata-po 6;
  ru-po 6,7,7,7; pu=po everywhere; annotated pu V*=1 → 7. **The V*=2 rank jump is the
  without-replacement discriminator** (multinomial law shows no jump) — kills the engine-law
  mismatch death directly.
- **EP4 = S1a constructed fiber pairs** [AUTH]: fifo orthant injections on never-executed orders;
  ru integer splits across never-drawn orders; gates G1–G3 (byte-identical F_exec corpora;
  state_hash chains differ; |ΔC| matches Theorem 1). **Hard prerequisite: fixture enrichment**
  (multi-order rationed touched levels, clock-straddling never-drawn orders) — current 21–22-event
  fixtures cannot measure O-C/O-D.
- **EP5 = T4 drift telemetry** [AUTH]: exploratory register only; cites Soudry 2017 + The Loss
  Does Not See the Basis but Adam Does 2026; never theorem-claimed.

**OOD axes.** Kernel swap FIFO→random_unit (primary; T3 bridge; truth reference unchanged),
truncation lag/cap, population 2N, tick 2Δ — all inference-only on locked checkpoints; K=8
streams replayed; deterministic-kernel cells' 8 identical records = determinism gate G8.

**Fiber resampler (new instrument)** [NOW if authorized]: regenerates without-replacement
interleavings holding the aggregate tape fixed; acceptance = identical `aggregate_state_hash`
sequence with differing `state_hash`. Single highest-leverage prerequisite: KT-A3, KT-M1 and the
merged T0 forecast's floor compliance depend on it.

## 3. Theory deliverables

**Complete and proof-checked pre-D0 [NOW]:** P1 fiber taxonomy **with constructive tangent-basis
algorithm** (S2 surgery is unexecutable without it; unit-tested for exact engine invariance on
frozen fixtures); P2 = T1 grid + dimension formulas + stratification (exhaustion via price-only
quotes; V*-ladder); P3 = bounded T2 Theorem 1 + Prop 1b (distillation no-recovery) + Corollary 2;
P4 = T3 exposure sets + non-commutativity remark; **KT-G1 R2 non-lumpability obstruction lemma**
(two-state point-mass vs multi-hypergeometric, TV ≥ 1−max_x p_x); **KT-G2 separation lemma**
(equal-geometry-budget fibers, ≥2× consumer-variance gap vs generic L×E[distance]) — the one T2
armor item still unproven; KT-G3 lemma pair (not-function-preserving; no-quotient-repair, citing
the internal gauge_enforce injury precedent); KT-G4 chart-free restatement (P8 generic-rank =
chart-dependent prong (d), DPIOT owns that residue); KT-G5 exposed-set characterization incl. the
postponed-composition direction; V4 gauge remark upgraded from prose to Lemma A/B citations (vs
Quotient-Space Diffusion ICLR 2026, Neural Mechanics ICLR 2020); parent-reduction table (owns /
does-not-own rows); KT-M2 template-expressibility table; T4 conjecture box.
**Post-freeze permitted:** finite-instance corollaries, constants polishing, enumeration against
preregistered targets, T4 conjecture refinement. **Prohibited:** any new confirmatory
proposition; any endpoint, estimator, threshold, cell or schema change.

## 4. Contract v1 adoption

Adopt C1–C16 verbatim (seed=RNG-tree root; 50,000-draw paired eight-cell bootstrap; ordered
classification; 4×16 Holm within block; one-shot analyzers G1–G12 incl. horizon-one **clearing
identity** via replay validator, integer conservation exactness, allocation_rule binding,
parameter parity + zero-step attestation; frozen macros; reflexive five-firewall clause). Two
amendments recorded in C16: (11) two-stage execution with Stage-2 15-seed directional robustness;
(12) truncation-condition secondary family (O-C/O-D). Reflexive cell retained exploratory-only
(~6 V100-h) under the five firewalls, scheduled only after confirmatory analyzer hashes publish.
Tape-likelihood diagnostic = one-shot descriptive profile feeding T1/T2, outside confirmatory
machinery. Full text: `ecomd_reexploration_contract_v1_2026-09-06.md`.

## 5. Compute and timeline

| Phase | Content | V100-h / days |
|---|---|---|
| Pre-D0 [NOW], ~2 wks | All §3 theory; fixture enrichment + fiber resampler builds (if PI-authorized); estimator menu + read-only fixture unit test; L1/L2 contracts; prereg + adversarial 3-reviewer pass; ledger entries; cleanup dry-run scripts | 0 GPU |
| D0-S1 (d0–1) [AUTH] | Disk cleanup ≥40% free both nodes (98/96% full; R2 relocation of paper D archive, manifest-verified); env sync; focused tests; seed-999 preflight | 15 |
| D0-S2 (d1–2) | D1 dual-arm corpora (30 data seeds) + byte-exact re-derivation both nodes | 18 |
| D0-S3 (d2–16) | Stage-1 training (GPU-a L1 / GPU-b L2); day-5 L2 trainability check; first-record gate d2–3; eval/surgery/truncation/kswap interleaved | 432+96 |
| D0-S4 (d16–17) | Coverage/checkpoint gates; one-shot analyzers; Stage-2 mechanical trigger | 8 |
| D0-S5 (d17–28) | Stage 2 (synthetic, 15 seeds) or buffer; reflexive cell last | ~410 |
| D0-S6 (d28–29) | Manifests, R2 upload, freeze audit | — |

Stage 1 ≈ 650 V100-h ≈ 19–20 days at 70% campaign efficiency; total inside the ~4-week ceiling
with the preregistered shrink/cancel ladder (slip >5d → variant A at 12 seeds; slip >D0+26d or
burn >1150 → cancel Stage 2, forfeit robustness leg as a reported deviation; theorems
unaffected). Worst-case mid-run death ≈ 14 GPU-days; **all novelty-critical gates fire pre-GPU**
(death budget: 0 GPU at week 2–3).

## 6. Killer-test register (≥2 per family; theory-answered attacks recorded as checks)

| ID | Family | Status after theory inputs | When |
|---|---|---|---|
| KT-G1 sufficiency reduction | GAMMA | **Partially answered**: T1 admits deterministic branch = DS/sufficiency corollary; R1 static toric concession + R3 trivial-direction label written into scope. **Remains: prove R2 non-lumpability obstruction** | [NOW] |
| KT-G2 triviality | GAMMA | Theorem 1 tightness already answers the law-of-total-variance existence attack (conceded, scoped, not fought). **Remains: (i) separation lemma; (ii) static dual-hash loss audit** (any loss term reading per-unit/per-maker fields falsifies T2's premise) | [NOW] |
| KT-G3 gauge conflation | GAMMA | Remark drafted (T2/T3 §4); **lemma pair unproven**; empirical twin = KT-M1 | [NOW] |
| KT-G4 parameterization artifact | GAMMA | **Partially answered** by P8 generic-rank; chart-free prongs (a)–(c) remain | [NOW] |
| KT-G5 contrived-D vacuity | GAMMA | **Partially answered** by P6 one-step exposure table; full characterization incl. postponed-composition direction remains | [NOW] |
| KT-A1 estimand boundary | ALPHA | Not answerable pre-run; P1/P2/P3 patterns + kill pattern frozen as decision rule | rule [NOW], run [AUTH] |
| KT-A2 M-level manipulation | ALPHA | Stage-1 TV separation lemma provable now; stage-2 identical-input replay + single-maker negative control later | lemma [NOW], run [AUTH] |
| KT-A3 kernel-invariance | ALPHA | Contrast spec frozen (swap > δ AND resample < δ/10 AND identity-readout ablation kills it); needs fiber resampler | spec [NOW], run [AUTH] |
| KT-A4 surrogate artifact | ALPHA | Menu frozen + read-only fixture unit test; two-estimator audit retrain | menu [NOW], retrain [AUTH] |
| KT-A5 portability | ALPHA | Sign-reproduction rules frozen; transfer gate = C9 | rule [NOW], run [AUTH] |
| KT-M1 gauge-twin empirical | merged | Resampler build (dual-hash acceptance) now if authorized; deployment experiment + gauge-repair falsification later | build [NOW], run [AUTH] |
| KT-M2 genre-template reduction | merged | Expressibility table now (competing-mechanism swap; kernel×enforcement on OOD; fiber-resampling control are template-inexpressible); confirmation shared with KT-A1/A3/M1 — one confirmation discharges four | table [NOW], run [AUTH] |

Full per-test rationale, attack statements, pass criteria and kill scopes:
`ecomd_reexploration_d1_killer_tests_and_ops_2026-09-06.md` §A.

## 7. Deliberate nonclaims

No first train×infer crossing. No bare positive-dimensional-fiber novelty (DPIOT). No
constrained-is-better superiority. No T4 theorem; drift measurements permanently exploratory. No
quotient/gauge repair claim. No real-market mechanism-identification or performance claims (bridge
is qualification-only; crash reserves untouched). No cross-market/universal scaling. No
post-freeze schema, prediction, threshold or cell-set change; no analyzer reruns; no H20; no
outcome-dependent analysis of any kind.

## 8. Hostile-T0 forecasts (proposed entries → `research/discovery/forecast_ledger.yaml` at D-1) [NOW]

- `d1_gamma_theorem_structure_survival` — 0.55 / 0.75 / 0.88. True iff no KT-G* forces T1/T2/T3
  below lead status (re-scoping with obstruction lemmas intact = survival).
- `d1_alpha_attribution_estimand_survival` — 0.18 / 0.35 / 0.55. True iff ≥1 of P1/P2/P3 confirms
  under the frozen KT-A1 rule with KT-A4 stability.
- `d1_merged_gammas_led_paper_gate` — **0.18 / 0.34 / 0.55** (floor 0.15 cleared with thin margin;
  margin carried by the ALPHA estimand). Resolution rule must flag: **without fiber-resampler
  authorization the lower bound drops to ≈0.10, below floor** — KT-A3/KT-M1 become unrunnable.
- Components (floor-exempt): L2 transfer 0.25/0.45/0.65; EP1 material 0.30/0.50/0.70; bridge
  qualification 0.55/0.75/0.90.

These are the workflow's proposed ledger entries; the formal append (schema v1,
basis_evidence_refs) happens in the D-1 session.

## 9. D0 freeze artifacts

Preregistration PDF (claims T1–T4, grid, EP1–EP5, orderings, gates, nonclaims, de-scope ladder);
theory appendix (P1–P4 proofs, lemma pairs, killer ledger, parent + template tables);
cell/axis/record enumeration + record schema; estimator menu + fixture unit-test evidence;
seed/stream manifest (11000–11029 / 12000–12029, derivation salts); DGP configs + bundle hash
fea8a136…9581c + **enriched-fixture manifest** + fiber-resampler conformance tests; L1/L2
simulator contracts + gate thresholds; analyzer contracts (G1–G12) + frozen macros; bridge
qualification checklist; ops plan + mechanical triggers + retention policy + disk certificate;
hash-locked archive with clean-room verify; ledger entries above.

---

## 10. D-1 gate checklist (protocol `D_minus_1` requirements vs this plan)

| Protocol requirement | Status |
|---|---|
| ≥2 killer tests per family | **Provided** — register of 12 (KT-G1..G5, KT-A1..A5, KT-M1/M2); theory-level items executable [NOW], empirical items frozen as preregistered protocols. **Remains:** execute/prove the [NOW] items (KT-G1 R2 non-lumpability lemma, KT-G2 separation lemma + static dual-hash loss audit, KT-G3 lemma pair, KT-G4 chart-free prongs, KT-G5 exposed-set characterization, KT-A2 stage-1 lemma, KT-M2 expressibility table) before D0 |
| Parent-problem reductions | **Provided** — T1 deterministic-branch reduction verdict (Diaconis–Sturmfels/sufficiency corollary, demoted sub-claim), T2 hostile triviality check (existence-level conceded; tape-computable tight constant + endogenous kernel-dependent censoring + exact-zero predictions as differentiators), parent-reduction table. **Remains:** write the KT-M2 template-expressibility table vs Duruisseaux 2024 and freeze the reduction packet into the prereg [NOW] |
| Simulator contracts ≥2 independent lineages | **Provided (design)** — L1 (ecomd/models/ecomd_v2.py) and L2 (ecomd/training/fact_surrogates.py) contract specs. **Remains:** write both contracts, bind to the 27 conformance tests + replay validator, freeze configs + transfer-gate thresholds at D0 [NOW for documents] |
| Real-data bridge qualification (stylized-fact bridge) | **Provided (protocol)** — frozen mapping spec public-tier (lobster/binance/yfinance) → engine request grammar; qualification = ≥95% event-type coverage, tick-lattice compatibility, FIFO reconstructability bounds with hidden-order gaps documented, ≥8/11 stylized facts with CIs via ecomd/eval/stylized_facts.py, provenance files, reserved 2019 vanilla windows, zero confirmatory use. **Remains:** freeze the checklist pre-D0; actual data read requires separate PI authorization post-D0 [AUTH] |
| Calibrated hostile-T0 forecasts to forecast_ledger.yaml | **Provided** — §8 entries with resolution rules and the fiber-resampler dependency flag. **Remains:** append in v1 schema with basis_evidence_refs before D0 [NOW] |

Additional prerequisites surfaced by the plan: statistical contract PI sign-off on the two C16
amendments; fixture-enrichment + fiber-resampler PI decisions (below); ops node cleanup [AUTH];
adversarial 3-reviewer pass on the prereg text before freeze; explicit PI authorization record.

## 11. PI decision list (required before D0; nothing proceeds without them)

1. **Freeze F_exec** (execution payloads + allocation draws + BBO prices) as the through-M corpus
   contract? Under F_full or F_exec+orders the fibers collapse toward points and T1–T3 die in
   instrument-grounded form — the single highest-leverage freeze item.
2. **Authorize the dual-hash-validated fiber resampler** (plus conformance tests) before D0?
   KT-A3, KT-M1 and the O-A..O-D orderings depend on it; without it the merged hostile-T0 lower
   bound is ≈0.10, below the 0.15 activation floor, so D-1 activation fails on that alone.
3. **Authorize lab-asset-v3 fixture enrichment** (multi-order rationed touched levels,
   clock-straddling never-drawn orders) as a schema-EXTENSION before D0? Current 21–22-event
   fixtures cannot measure O-C, O-D, or the S1a random-unit gates.
4. **Approve the two-stage amendment** to contract v1 (Stage 1 = B1+B3 at 30 seeds confirmatory;
   Stage 2 = B2/B4 at preregistered first-15 subsets, directional robustness only), versus the
   full 480-run grid that consumes the entire ~4-week ceiling with zero slack?
5. **Confirm Stage-2 synthetic members** — variant A `garch_student_t5` (both lineages) and
   variant B `multiscale_logvol` (L2-only), with `negative_jump_iid` named-but-not-run — and the
   frozen series-to-request wrapper into the same engine?
6. **Authorize the DGP-only, zero-GPU variance preflight** to move K within {4,8,16} before D0
   (immutable after), default K=8?
7. **Confirm the through-M estimator menu** — straight-through (pinned scale) primary and
   perturb-and-MAP (pinned noise) as the KT-A4 audit estimator, with the two-estimator retrain of
   the audit cell inside the compute envelope?
8. **Set the D0 date** and the adversarial 3-reviewer panel pass on the preregistration text
   before freeze; confirm the reference calendar (theory complete ~09-12, D0 ~09-19) or set new
   dates.
9. **Authorize node cleanup op-session 1 at D0** (relocate paper D deployment archive to
   r2://ecophys/paper_d_archive/ with manifest verification, target ≥40% free on both 98/96%-full
   V100 nodes)?
10. **Adopt seed namespaces** 11000–11029 / 12000–12029 (avoids Paper D namespaces)?

## 12. Risk register with stop rules

STOP = line halts, PI informed, no narrative repair. REFRAME = claim repositioned with recorded
deviation. BOUNDARY = reported as boundary, claims scoped down.

| Risk | Rule |
|---|---|
| Engine-law mismatch: lab-asset-v3 random arm is draws-with-replacement or proportional-to-initial | **STOP** — detected by S3 (no V*=2 rank jump; kernel-dependent agg rank; pu≠po); pool scale never identified; T1's unique identifying cell dies; new truth engine required before any GAMMA claim survives |
| S1a structure-lemma falsification: injected fifo excess or ru splits change any F_exec field | **STOP** — engine records finer than the schema-static analysis; no cube-level result can rescue it |
| Corpus-contract reversal: F_full frozen instead of F_exec | **STOP** — fibers collapse; T2/T3 lose ambiguous sets; paper reduces to abstract T1; reframe or die at freeze |
| KT-G1 R2 failure (non-lumpability unprovable) | **REFRAME** — T1 demotes to scoped proposition; merge rationale re-led by T2/T3 |
| KT-G2 separation-lemma failure (variance derivable from generic Lipschitz × geometry) | **REFRAME** — T2 repositioned as risk characterization with mechanism-endogenous constants; if T1 also lost its dichotomy trace (O-D inverted, exact-zero null rejected), no theorem spine — **STOP** |
| KT-A1 kill pattern (|I| ≤ δ/2 everywhere, no sign opposition, surgery antisymmetric) | **REFRAME** — attribution reduces to scalar superiority; ALPHA reframed as ablation; paper rests on GAMMA + boundary report; must be reported, never narrated around |
| KT-A4 estimator instability (sign patterns flip between estimators beyond Holm bands) | **REFRAME** — through-M claims estimator-conditional, both shown; if both estimators fail the fixture competence gate, cube collapses to surgery-only (below D-1 bar) — **STOP** |
| KT-M1 gauge-twin null (all deployment maps < δ/10 on fiber pairs) | **REFRAME** — fiber behaves like internal gauge symmetry; empirical bridge severed; program survives as GAMMA theory only |
| M0/M1-lumpable freeze impossible (request streams irreducibly allocation-identity-dependent) | **STOP** — exact request-level CRN impossible; paired-seed premise collapses; needs fundamentally different design |
| Byte-exact replay failure across nodes | **STOP** — CRN unverifiable; gates G6/G8/G9 unpassable |
| Reference degeneracy in all four strata (mean R00 < 1.0 scaled unit) | **STOP** — SESOI inoperative; no post-hoc metric substitution under one-shot rule |
| Convergence-failure halt (>15% nonfinite on any mandatory cell after resume, or >3/30 seeds lost) | **STOP + PI** — mandatory halt for PI decision; never silent seed substitution |
| Outcome-access breach (any metric inspected before both workers complete) | **STOP, NO REPAIR** — voids outcome-blind freeze and the preregistration chain |
| Stage-2 trigger breach (burn >1150 V100-h or Stage 1 past D0+26d) | **REFRAME** — Stage 2 auto-cancels, robustness leg forfeited as reported deviation; theorems unaffected; any outcome-triggered Stage-2 launch downgrades the D2 block to exploratory or forbids it |
| Disk/compute prerequisite failure (nodes not ≥40% free, or capacity cut) | **STOP** — launch blocked, not descoped ad hoc |
| Hostile-T0 calibration failure (ledger lower bound < 0.15 at calibration) | **STOP, PRE-GPU** — activation fails at D-1 with zero GPU spent |
| Prior-art reopen (post-freeze work stating mechanism-fiber training non-identification or train-through ablation) | **STOP/REPOSITION** — direct collision; reposition before D0 |
| L2 transfer-gate failure (B3 fails) | **BOUNDARY** — report architecture boundary per U-Net lesson; claims scoped L1; never pooled, never hidden |
| KT-A5 portability kill (no lineage×DGP shows attribution-only pattern) | **REFRAME** — estimand-boundary attack confirmed; ALPHA is an ablation |
| Through-M surrogate non-convergence | **REFRAME** — cells classify unresolved, never dropped; deviation ledgered |
| Reflexive-cell leak (five-firewall breach) | **CONTAINED** — voids only that exploratory subsection |
| Post-freeze edit breach (any change after D0, or analyzer rerun without PI memo) | **STOP, NO REPAIR** — preregistration integrity fails |

---

*Provenance: 9-agent planning workflow (T1, T2/T3 theory; contract adapter; ops; red team; three
independent plan drafts; synthesis) under session task wnnfx2616, 2026-09-06. Session ledger:
logs/2026-09-06.md Session 4.*
