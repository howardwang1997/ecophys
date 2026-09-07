---
document: Preregistration v2 (post-panel, freeze candidate) — merged GAMMA-led reexploration paper
repo_path: papers/proposal/ecomd_reexploration_prereg_v2_2026-09-06.md
authored: 2026-09-06
supersedes: papers/proposal/ecomd_reexploration_prereg_v1_2026-09-06.md
panel: adversarial 3-reviewer panel (D1_08), 2026-09-06 — three major_revision verdicts,
  28 issues (9 + 9 + 10); all 28 incorporated in this v2 (disposition table in
  papers/proposal/ecomd_reexploration_prereg_panel_response_2026-09-06.md)
stage: D_minus_1_execution_authorized_prep_d0 (decision pi_reexploration_d1_authorization_20260906)
freeze_date: PINNED 2026-09-19 (D1_08 reference calendar; R1-9/R3 panel ruling; Annex A.10)
freeze_policy: sha256-frozen at D0 2026-09-19; exact freeze timestamp + freeze sha256 are the
  only [TO BE PINNED AT D0] items remaining in this document (freeze mechanics: Section 1.3)
outcome_access_at_authoring: none — no confirmatory endpoint measured, no GPU used, no market
  data accessed; the frozen A-2 bundle was consumed strictly read-only
---

# Preregistration v2 — Merged GAMMA-Led Reexploration Paper (EcoMD x lab-asset-v3 ALPHA cube)

This is the single authoritative document for every confirmatory decision downstream of the D0
freeze. All companion documents are incorporated by reference with absolute paths; where any
companion conflicts with this prereg, this prereg governs for science and the frozen statistical
contract governs for statistics (precedence: Section 1.4). This v2 is a complete document, not a
diff against v1; every clause of v1 is either carried, amended in place with recorded provenance,
or explicitly superseded via the errata register (Annex C).

---

## 1. Title, scope, version chain, and freeze mechanics

### 1.1 Scope

One paper, GAMMA-led. The theorem family T1–T3 (matching-fiber gauge non-identification, its
bounded consumer-variance floor, and the deployment exposed-set characterization) carries the
science; the ALPHA eight-cell market cube (coordinate x training-enforcement x inference-
enforcement, estimand J = D_00 − D_10 − D_01 + D_11, path-dependence attribution) is the
experimental section and the attribution instrument for T2/T3. T4 is conjecture-only and carries
no confirmatory weight. The merge gate and full prior-art adjudication are recorded in
`papers/proposal/ecomd_reexploration_d2_evidence_map_2026-09-06.md` (the ONLY permitted citation
source; Section 2.8 and References).

Primary truth asset: the frozen lab-asset-v3 engine
(`experiments/lab_asset_a2/a2_exit_20260905/`, bundle manifest `fea8a136b0c3e19a00bddcb131a1540ca40fda6c1576dbc949001dbf76a9581c`
— full 64-hex form pinned here once; the elided short form `fea8a136...9581c` used elsewhere in
this document refers to exactly this value), 27 conformance tests + replay validator, read-only,
never mutated) with the authorized lab-asset-v3.1 fixture enrichment (Section 7.2).

### 1.2 Version chain

| Version | Content | Status |
|---|---|---|
| v1 (`ecomd_reexploration_prereg_v1_2026-09-06.md`) | Complete freeze-grade draft; five mandatory wording changes; C14 recomputed under K = 16 with loud flag | SUPERSEDED by panel outcome |
| Panel (D1_08, 2026-09-06) | Adversarial 3-reviewer panel: preregistration-integrity auditor, statistical methodologist, market-microstructure/scientific-ML referee. Three **major_revision** verdicts; 28 issues (R1: 9, R2: 9, R3: 10) | Closed; verdicts and dispositions recorded in the panel-response document |
| v2 (this document) | All 28 panel issues incorporated (28 fixed, 0 rejected, 0 deferred); restated C14 with full record enumeration; C16 ledger extended to items (13)–(16); freeze mechanics, seed pinning, and family definitions completed (Annex B) | Freeze candidate — PI review, then D0 hash-freeze |
| D0 freeze (2026-09-19) | v2 sha256-frozen together with the amended contract, theory appendix, and hash-locked archive (Section 1.3); DGP configs, seed/stream manifest, estimator hashes, analyzer contracts, enriched-fixture manifest, ops plan hash-locked in the same archive | [TO BE PINNED AT D0: freeze timestamp + freeze sha256 ONLY] |

Reference calendar (PI decision D1_08, as pinned by the panel per Annex A.10): theorem work
complete ~2026-09-12 (done, ahead of schedule); **D0 outcome-blind freeze 2026-09-19**;
post-freeze campaign: Stage 1 ~19–20 wall-clock days at 70% efficiency, 4-week hard ceiling
(Section 8.2).

### 1.3 Freeze mechanics and post-freeze edit policy

**Freeze mechanics (pinned at v2 per panel R1-6).**

1. *Hashing agent and procedure.* The D0 freeze hash is computed by the PI in the D0 freeze
   session (or by the PI-directed freeze agent in that same session, recorded as such), using
   `sha256sum` (or `shasum -a 256`) over the exact file bytes, with the command and its stdout
   recorded verbatim in the session log.
2. *Exact hash inputs (frozen file list).* The D0 freeze hash chain covers, at minimum: this
   prereg v2; the statistical contract
   `papers/proposal/ecomd_reexploration_contract_v1_2026-09-06.md` AS AMENDED by the pre-freeze
   amendment banner of 2026-09-06 extended through the v2 restatements (C14/C9/C16 items
   (13)–(16), Part 2a.6 supersession note; Section 3.1); the theory appendix
   `ecomd_reexploration_theory_appendix_2026-09-06.md`; the experiment plan; the D-2 evidence
   map; the D-1 session record, killer-tests/ops document, estimator menu, simulator contracts,
   and lemma writeups directory manifest; the enriched-fixture manifest; the K-preflight results
   file (sha256 `f61e410cd59c37b5624504a3cdf057c701b4b682067f948d2f8528ace018c2d4`); the
   fiber-resampler prereg statement (sha256 `703ca36e...2c4b`); the DGP generator + config; the
   seed/stream manifest; the frozen estimator module hashes; the analyzer contract; and the ops
   plan. Per-file hashes plus one commit-level hash over the ordered file list (lexicographic by
   path) constitute the freeze record.
3. *Recording location and order.* (i) git commit on `paper-d-iclr-2027-completion` containing
   exactly the frozen file set (commit sha256 recorded); (ii) upload of the freeze record
   (per-file hashes + commit hash + freeze timestamp) to the immutable R2 object
   `r2://ecophys/alpha_cube_d0_20260919/freeze_record.json`; (iii) entry in the D0 session log
   with the R2 object etag. Order is mandatory; a failure at any step stops the freeze (no
   partial freeze).
4. *Known-typo policy.* The four companion documents that print the bundle-anchor typo
   `fea8b136...9581c` (Annex C, items C-4) are NOT edited pre-freeze; instead this prereg v2
   records the canonical 64-hex anchor (Section 1.1) and the full typo inventory in Annex C,
   and the freeze record binds those companions by their own per-file hashes. String-matching
   auditors are directed to Annex C. (Editing hash-locked companions pre-freeze to fix typos
   would itself churn hashes referenced elsewhere; the flag-list route is the lower-risk
   freeze-grade fix and satisfies G3, whose anchor is the canonical value pinned in Section 1.1.)

**Post-freeze edit policy.** After the D0 freeze the ONLY permitted edits to this document and
the frozen contract are:

1. finite-instance corollaries of already-frozen statements;
2. constants polishing (no change of form, reference convention, or scope);
3. enumeration of realized results against the preregistered targets of Sections 4.3–4.4 and 7.

PROHIBITED after freeze: any new confirmatory proposition; any endpoint, estimator, threshold,
cell, seed, axis, horizon, family, schema, or record-count definition change; any analyzer rerun;
any outcome-dependent analysis of any kind. Any breach is STOP-class, no repair (Section 8.3).

### 1.4 Authority and precedence

1. This preregistration (science + global constraints).
2. `papers/proposal/ecomd_reexploration_contract_v1_2026-09-06.md` — "Statistical Contract Port:
   Paper D → ALPHA Market Cube (FROZEN CONTRACT v1 candidate)", clauses C1–C16 and gates G1–G12,
   incorporated by reference in Section 3 together with its pre-freeze amendment banner, EXTENDED
   at v2 by the recorded pre-freeze restatements of C14 (K = 16 enumeration), C9 (transfer-gate
   primary reference), C2(e) (dead-letter clause rewrite), and C16 items (13)–(16). The contract
   is a D-1 candidate until the D0 freeze; pre-freeze restatements are lawful amendments with
   recorded provenance (Section 10.2), and the freeze binds the contract text into the hash
   chain (Section 1.3).
3. `papers/proposal/ecomd_reexploration_experiment_plan_2026-09-06.md` (design synthesis, risk
   register) and `papers/proposal/ecomd_reexploration_theory_appendix_2026-09-06.md` (theorem
   statements and proofs).
4. D-1 session companions: `ecomd_reexploration_d1_lemma_writeups_2026-09-06/` (kt_g1_r2…,
   kt_g2…, kt_g3…, kt_g4_g5…, kt_a2_tv_separation_and_kt_m2_template_table.md),
   `ecomd_reexploration_d1_session1_record_2026-09-06.md`,
   `ecomd_reexploration_d1_killer_tests_and_ops_2026-09-06.md`,
   `ecomd_reexploration_estimator_menu_2026-09-06.md`,
   `ecomd_reexploration_simulator_contracts_2026-09-06.md`.
5. Authorization (never science): `research/discovery/decisions/pi_reexploration_d1_authorization_20260906.yaml`
   (D1_01–D1_10 blanket "全部授权" + addendum D1_11–D1_14 "用需要算力多的那个，批准，确认，确认").

Nothing in this prereg is standing authorization for execution. GPU training, confirmatory
simulation, market-data access, and the two-estimator audit retrain remain gated on the D0
outcome-blind freeze plus their own explicit PI authorization steps.

### 1.5 Outcome-blind attestation at authoring time

Zero confirmatory endpoints measured; zero analyzer runs; zero GPU allocation; zero market-data
access; zero trained models; the frozen A-2 bundle strictly read-only. All theory status labels
below are theorem-level facts proved or refuted on paper, not empirical results.

---

## 2. Scientific hypotheses T1–T4 with frozen status labels

Status labels (authority: D-1 session-1 record §1, per-statement): **proven** (proof complete,
conditions stated where hypothesized), **proven_with_conditions** (proof complete under named
conditions that remain live), **conjecture** (no proof; never confirmatory). Honest boundaries
are copied from the lemma writeups verbatim-faithfully, never weakened. Where the term
"lumpability" appears below it is vocabulary only — every statement is proved directly from the
engine; the Markov-lumpability literature is on the needs-verify list and is not cited as fact
(Section 2.8).

### 2.1 T1 — the aggregate-sufficiency (non-lumpability) obstruction — **proven_with_conditions**

**Lead statement (kernel x granularity x policy-feedback TRIPLE interaction).** For
identity-responsive (M1+) flows the aggregate tape is not sufficient for the engine's own
forward law: aggregate-indistinguishable book compositions induce one-step aggregate-transition
laws separated by TV ≥ 1 − max_x p_x^{MVHG} (explicit constants; 5/6 on the two-unit balanced
pool q = (2,2), V* = 2), uniformly over the responsive-policy class — stated in the same block
as the M0-slack concession and the validation-channel remark, because the honest boundary is
**"no active identity channel," not "M1 or below."**

**Component results.**

- **R2-A (mechanism-level separation; policy-free) — proven.** At a multi-order rationed level
  a deterministic attribution is a point mass δ_{x°} while the random-unit attribution is
  multivariate hypergeometric MVHG(q, V*), giving TV = 1 − p(x°) ≥ 1 − max_x p_x. Exact
  constants: q = (2,2), V* ∈ {1,2} → 1 − max = 1/2, 1/3 (TV = 5/6 at V* = 2 with x° the
  prefix fill); S3 pool q = (5,4,3,2), R* = 14 with x° = (V*, 0, 0, 0): **feasible-ladder
  constants TV = 9/14, 81/91, 996/1001 at V* = 1, 2, 4, and the FIFO-prefix value 0.9987 at
  V* = 6** (Section 2.5 per-fixture table; the two instantiations coincide for V* ≤ 5).
  **The bare value TV = 1 at V* = 6 is the INFEASIBLE-SINGLE-ORDER WITNESS, not a
  pool-realizable constant:** its x° = (6, 0, 0, 0) cannot be produced by the pool (q_1 = 5 < 6),
  and TV = 1 holds there by empty intersection of the two supports; it is reported only as the
  exhaustion-adjacent boundary witness and never quoted as a separation the pool attains
  (panel R2-9 relabel; consistent with Section 2.5, which always carried 0.9987 as the feasible
  V* = 6 value). Kernel-law-general universal bounds 1 − max_x p(x) on the same pool: 0.357 /
  0.505 / 0.580 / 0.580 across the V*-ladder; balanced-family Binomial limits 1/2, 5/8, 11/16.
  Exhaustion rounds (V* = R*) carry their own deterministic clause and are never merged with
  the random bound; V* = 1 carries the 1/2 constant.
- **R2-B (responsive-policy non-lumpability) — proven_with_conditions.** Conditions: single
  designated pool actor with injective, non-cancelling response (Π_resp-class). Under those
  conditions, for EVERY responsive policy the one-step aggregate-transition kernels of
  aggregate-indistinguishable states separate by TV ≥ 5/6, uniform over the class.
- **R2-C (the M0 concession — and its sharp boundary) — proven.** On the resource-slack /
  no-self-crossing stratum, M0 flows ARE lumpable: the aggregate state sequence is a measurable
  function of (aggregate initial state, request sequence), so the sufficiency reduction goes
  through exactly as conceded. Grammar clause: order-id-addressed cancel/replace actions are
  not M0-admissible unless keyed to aggregate-observable labels. **Off the slack stratum even
  M0 fails:** with the owner of the best ask differing across fiber members, an aggregate-
  measurable "actor A buys at 101" is rejected (SELF_TRADE_PREVENTED) in one member and executes
  in the other — aggregate one-step laws differ by TV = 1; the same holds via per-actor
  INSUFFICIENT_CASH / INSUFFICIENT_INVENTORY reserves. The true boundary of the reduction is
  "no identity-dependent channel is active" (policy feedback and validation feedback are the
  two engine-native instances). The M0 concession is a stratum statement, not a class statement.
- **R2-D (training-signal obstruction) — proven.** Any aggregate-tape-measurable predictor
  incurs sup TV ≥ (1/2)(1 − max_x p_x) = 5/12. The inequality is proved inline from the TV
  triangle inequality; the Le Cam two-point lineage is deliberately excluded (Section 2.8).
- **Sharpness counterexample — proven.** All-respond buy-back-own-fills policies (every pool
  actor responds with exact buy-back of own fills, g_i(c_i) = c_i) are aggregate-silent at
  pooled windows: total response volume Σc_i = V* in every fiber member, so the one-step
  aggregate separation at that node is TV = 0. Per-event print granularity still separates —
  print sequence (single print (V*) vs ((c_i)_i)): TV = 1 − C(q_r, V*)/C(R*, V*), 5/6 on the
  (2,2), V* = 2 pool. Hence no injective-own-count response ⇒ no uniform separation; the
  obstruction is exactly coextensive with active identity feedback, and the stronger
  "all M1+" claim is false and must never be made.
- **KT-G4 chart-free prongs.** (a) recorded information is a σ-algebra and identification
  content transports — **proven**. (b) the count-law family itself jumps: multinomial never
  jumps, MVHG jumps at V* ≥ 2, under every smooth reparameterization — **proven**. (c)
  floor/exposed-set naturality as a trichotomy — **proven_with_conditions** (C4 requires
  D-transport compatibility; the exact floor constant is reference-measure-relative, a declared
  contract item). (d) positive fiber dimensionality in θ-charts — **refuted as stated:
  chart-dependent.** Concession sentence (mandatory in the paper text): *positive-dimensional
  preimages under nonlinear parameterization are owned by DPIOT (ICML 2022) for learned
  simulators, with the perturb-argmax family analog owned by Perturb-Argmax/Softmax (Cohen
  Indelman & Hazan, 2024, arXiv:2406.02180); T1 claims no chart-dependent fiber-dimension
  novelty and is stated over the admissible flow x draw space with the chart demoted to a
  convenience.*

**Scoped, conceded, and deliberately not claimed in T1.**

- Static toric concession (R1): uniform interleavings with P = ∏ q_i!/Q! are a Diaconis–Sturmfels
  toric fiber; Diaconis–Sturmfels (1998) and the contingency-table fibers (2014) literature own
  the static fiber shape. R2 is the dynamic complement; R3 (aggregate + random collapse =
  marginalization) is labeled the trivial data-processing direction so no referee may inflate it.
- Deterministic-kernel shrinkage is demoted to a sufficiency corollary with those citations.
- The general-composition asymptotic constant 1 − O(R*^{−1/2}) is UNPROVEN and not claimed; the
  maximal-atom/log-concavity bounds it would need are not invoked (Section 2.8); the result is
  scoped to the balanced-family Binomial limits.
- The R2 witness pair requires a multi-order rationed level: any empirical S1a-type realization
  depends on the D1_03 fixture enrichment (Section 7.2); the frozen 21/22-event bundle contains
  only single-maker touched levels.

### 2.2 T2 — bounded consumer-variance floor and kernel-blind vacuity — **proven_with_conditions**

**Theorem 1 (bounded quantitative floor; T2 lead).** Fix tape τ with nonempty ambiguous set
U(τ) under (kernel, granularity, F_exec), reference μ_R on the box-truncated fiber, linear
consumer C(z) = v^T z with v_U not identically zero. Then:

- (a) **Exact variance**: Var_{μ_R}(C | τ) = (R²/12)‖v_U‖² (orthant/box case); split case per
  touched level: Var = (R²/3)·Σ_{i ∈ neverdrawn(ℓ)}(v_i − v̄_ℓ)².
- (b) **Estimation floor**: every τ-measurable estimator Ĉ — in particular every through-M-
  trained simulator consumer — obeys E_{μ_R}[(C − Ĉ)² | τ] ≥ Var_{μ_R}(C | τ), equality iff
  Ĉ = E[C | τ].
- (c) **Tightness**: the fiber-center estimator attains the bound; the floor is the exact
  minimax value over tape-information-constrained estimators.
- (d) **Growth**: floor RMSE = R‖v_U‖/√12 ≈ 0.289·R·‖v_U‖; per-direction contributions
  tape-computable.
- (e) **Granularity trace**: under fifo the floor grows Θ(R²) on the never-executed orthant;
  under random-unit + per-unit tape the magnitude directions are pinned (eligible_units pins
  level aggregates, maker_remaining pins drawn orders) and the surviving floor is the split
  term — with **exact zeros**: price-notional consumer on ru splits (floor identically 0) and
  the latency consumer floor (R²/3)·p_ℓ²·(m_in·m_out/m), positive exactly when a touched
  level's never-drawn orders straddle the latency window.

Proposition 1b (distillation no-recovery): any student measurable in a through-M teacher
inherits the floor. Corollary 2 (unbounded recession directions) is deliberately subordinate
and never led with.

**Hostile-triviality defenses (frozen).** Defense 1 — the constant R‖v_U‖/√12 is tape-computable
from the public tape alone. Defense 2 — the censoring geometry U(τ) is mechanism-endogenous and
kernel-dependent (orthant vs split kernel with exact zeros), not a fixed missingness pattern;
exogenous-threshold censoring (Tobit lineage) cannot predict the kernel x granularity
interaction. Defense 3 — tightness plus exact-zero point predictions (falsifiable nulls, not
one-sided hedges). Residual honesty: if reviewers judge Defenses 1–3 "engineering of a classical
bound," T2 is repositioned as risk characterization of tape-trained market simulators with
mechanism-endogenous constants; T2 is never sold as a new estimation theorem.

**Defense 4 (KT-G2 separation package; leads the armor) — kernel-blind certification is
vacuous.**

- **G2-1 — proven.** The aggregate tape (the engine's own aggregate_state_hash content) is
  swap-invariant: all kernel-blind data coincide on swap pairs. Frozen-fixture hash identity
  (exact sequences and hash roles, pinned per panel R3-6, matching the KT-G2 writeup §3): the
  **fifo tape SEQUENCE 7** (one aggregated fill record, quantity 2) and the **random_unit tape
  SEQUENCE 8** (two unit fill records) share the pre_aggregate_state_hash `da930600...` and
  reach the identical post_aggregate_state_hash `f0862093...`, under the completed-request-
  boundary convention (both arms processed the same completed request at that point of the
  episode; record indices are per-arm tape indices, not episode event numbers).
- **G2-2 — proven (given Theorem 1); CONVENTION-ROBUST; the lead.** Price-notional cell: on the
  SAME (prestate, request stream), floor_fifo = (n−1)p²R²/12 > 0 while floor_ru = 0. Any
  uniformly valid kernel-blind bound B is therefore forced identically zero on the shared
  kernel-blind data, while sup_k floor_k / inf_k floor_k = ∞: no kernel-blind bound is
  c-informative for any finite c — against the (R, ‖v‖, dim) class, against Lipschitz x
  diameter budgets, and against every swap-invariant functional. Zero stays zero and the fifo
  floor stays positive under any positive-width rescaling, so this lemma survives every
  reference-convention choice.
- **G2-3 — proven_with_conditions; the finite-gap illustration UNDER THE FROZEN CONVENTION.**
  Latency consumer, same prestate and request stream: ρ = floor_ru / floor_fifo = 4·m_out/m
  ∈ [0,4), where m_in/m_out count never-touched orders inside/outside the latency window;
  same-data concrete instance ratio exactly 3 (n = 5 orders, window covering {O_1, O_2},
  V* = 1, draw realization O_1); equal-second-moment-budget cross-instance ratio exactly 2;
  c < 4 impossible within the latency family. **Both reference conventions are preregistered as
  per-coordinate deviation budgets:** (i) two-sided ε ~ Unif[−R, R] (split case, |ε_i| ≤ R,
  reference constant R²/3) and (ii) one-sided box [0, R] (orthant case, reference constant
  R²/12). **Width-matching gap inversion, stated so no referee can read the factor 4 as an
  inconsistency:** under the width-matched convention ε ~ Unif[−R/2, R/2], ρ = 4·m_out/m
  becomes m_out/m ≤ 1 — the ru floor is then always the smaller one, the ≥ 2x gap of G2-3
  inverts, the separation SURVIVES (ρ ∈ [0,1), still kernel-dependent, still exactly zero for
  constant v) but the headline number "3" does not. The theory appendix froze the
  deviation-budget reading, under which G2-3's constants hold as stated. Conditions: frozen
  reference convention; draw-realization conditioning (every realization of the instance gives
  ρ ∈ {3, 4}).
- **G2-4 — proven.** The F_exec grammar carries a kernel fingerprint (allocation_draw presence,
  record granularity, eligible_units); Theorem 1(e)'s tape-computability is therefore
  kernel-aware — no referee circularity between Defenses 1 and 4.
- Hash-augmented kernel-blind procedures (H2 of the writeup) fail in opposite directions on the
  two arms of the same (P, s); a procedure that branches on the reference-measure geometry has
  read swap-variant data and is kernel-aware by the back door.

**Conditions carried.** Theorem 1 as given in the theory appendix (A1–A5: one-step linear
clearing; F = F_exec; finite linear consumers; deterministic training given corpus + paired
seed draws; integer-lattice constructions); the multi-order split cells are proven at the
engine-semantics level with dynamic confirmation on enriched fixtures deferred to the post-D0
S1a gates; if the enriched engine ever records a per-never-drawn-order quantity, the G2-2 ru
floor ceases to be zero — and that event also falsifies Theorem 1(e) itself (S1a STOP class),
so lemma and theorem stand or fall together.

### 2.3 T3 — deployment exposed-set characterization — **proven / proven_with_conditions (per statement)**

**Preregistered deployment grammar 𝒢 (nothing post hoc):** D_read (record readout), D_raw
(raw-flow readout), D_swap→ru, D_swap→fifo (kernel swap by replaying the recorded request
stream from the same prestate with allocation_rule exchanged — the replay contract's native
operation), D_trunc^W (truncation window W on arrival clocks), D_h (horizon extension, h ∈
{1,4,16,31}), and finite compositions. Consumers: linear raw-flow consumers C_v (risk notional;
latency notional v = p ⊙ 1{clock ≤ W}) and allocation consumers on deployed fill counts.

**Nomenclature (frozen; replaces the conflicted D_id everywhere).** The two preregistered null
controls are:

- **D_read** — record readout; the consumer sees only the deployed tape. Null control:
  Exp(D_read, C) = ∅ for every consumer (every C∘D_read is σ(T)-measurable, constant on
  fibers; probability-1 detection none).
- **D_raw** — raw-flow readout; the consumer sees the true submitted flow (the risk-manager
  baseline). Maximal control: Exp(D_raw, C_v) = {u ∈ U : v^T u ≠ 0} = U for every consumer
  with v_U not identically zero.

The earlier single name D_id conflated these two different identity maps; T1/T3 wording here
and everywhere downstream uses D_read and D_raw.

**Theorem T-1 (one-step exposed-set table; exact, with sign and magnitude) — proven.** Highlights
frozen as predictions: swap→ru exposes U(τ)\{0} for allocation consumers with first-order
magnitude O(δ/S) (every next-draw probability moves at order δ/S; per-level weights 1/S
computable from fixtures); swap→fifo on fifo cells is EXACTLY blind — M_fifo(z̄ + t·u) =
M_fifo(z̄) for all t ≥ 0, including on the integer lattice — Exp = ∅ (point null;
integer-exact subcheck under O-B, Section 4.4); truncation: Exp(D_trunc^W, C) = U(τ) ∩ W with
floor localization (monitor nondecreasing in W, zero when no straddling; O-C); the
deterministic eligible_units displacement under swap→ru is the strongest O-B/O-C prediction
(probability-1 visible, integer-exact, fixture-testable post-enrichment). Instance-level
disclosure: the swap→fifo row on ru cells is instance-level (its threshold depends on
never-drawn quantities the ru tape does not record).

**Theorem T-2 — proven / proven_with_conditions.** T-2a functorial no-creation under
composition (proven); T-2b composition-order asymmetry (destruction asymmetry; proven; needs a
clock configuration, legal but not in the current fixtures); T-2c postponed creation via
horizon extension (proven_with_conditions: on the P7 event of positive probability under a
nondegenerate flow, with two-round book persistence engine-grounded); T-2d floor localization
under compositions (proven). The exposed-set characterization is always stated with its grammar
scope clause: 𝒢 as preregistered above, each map a function of the recorded tape plus the
deployment perturbation only.

**Three-way distinction (with separating observables; frozen).** (a) mechanism-induced fiber
divergence (ours) — separated by constructed exact-tape pairs (S1a) and raw-arm collapse;
(b) representational failure — separated by positive within-cell tape validation loss
correlated with downstream error; (c) design-induced operator set-identification — separated
by divergence moving under D redesign at fixed information. Each failure mode has exactly one
rescue lever, and the three levers are the cube's axes.

### 2.4 T4 — within-fiber optimizer drift — **conjecture (no confirmatory status, ever)**

Conjecture box: SGD/Adam selection among fiber-equivalent parameters may drift along the fiber
even though the loss is exactly fiber-constant (Lemma 0: identical corpora, literally the same
learning problem). No theorem; no test assigned by design; any within-fiber drift measurement
(S1b cross-seed gauge wander; retained-checkpoint telemetry on the 10-seed subset) lives in the
exploratory periphery with its citation pair (Soudry et al. 2017; "The Loss Does Not See the
Basis but Adam Does", 2026) and must not be promoted under D-1 pressure.

### 2.5 H5 — kernel-swap manipulation validity (KT-A2 stage-1 TV separation) — **proven_with_conditions**

The kernel-swap axis is a law-changing scientific manipulation, not re-plumbing: the two arms of
the frozen DGP generate total-variation-separated training-corpus laws with explicit constants,
and the separation collapses exactly on the strata the stage-2 negative controls name. Three
layers, stated together so the concession is on paper in the same sentence:

- **Layer 0 (Lemma A — aggregate anonymity; proven): TV = 0.** At aggregate granularity
  (G_agg) the swap IS plumbing: both corpus laws are the point mass of the same deterministic
  aggregate tape. Conceded in the same sentence as every positive claim below.
- **Layer 1 (Lemma B — full F_exec grammar; proven): TV = 1.** The trivial layer (draw-key
  presence); no lead claim rests on it, and no referee may inflate it into one.
- **Layer 2 (Lemma C — key-equalized attribution projection Π_att; the load-bearing lemma;
  proven_with_conditions under (A3′) for the MVHG constants, with (iii) kernel-law-general).**
  Stripping allocation_draw and aggregating each clearing round's per-unit records into the
  per-maker fill-count vector c:
  - (i) FIFO corpus law is a point mass at the prefix allocation c^F. (ii) Under (A3′) the
    random-unit attribution law is MVHG(q, V*). (iii) Exact identity, kernel-law-general:
    **TV = 1 − ν({c^F})**, and under (A3′) **TV = 1 − ∏_i C(q_i, c_i^F) / C(R*, V*)** —
    computable and preregistered PER FIXTURE.
  - **Per-fixture constants (S3 frozen family pool q = (5,4,3,2), R* = 14; exact integer
    arithmetic):** V* = 1 → Q(c^F) = 5/14 = 0.3571, **TV = 0.6429**; V* = 2 → 10/91 = 0.1099,
    **TV = 0.8901**; V* = 4 → 5/1001 = 0.0050, **TV = 0.9950**; V* = 6 → 4/3003 = 0.00133,
    **TV = 0.9987**.
  - **Strict-positivity dichotomy (exact under A3′):** the separation collapses (Q(c^F) = 1)
    iff m = 1 (single-order pool) OR V* = R* (exhaustion); on multi-order pools with
    1 ≤ V* ≤ R*−1 it is strictly positive for every pool vector q. Partial-fill floor:
    TV ≥ Σ_{i : c_i^F = 0} q_i / R*.
  - **NO uniform-in-pool constant exists and none is claimed:** adversarial pools
    q = (R*−1, 1), V* = 1 give Q(c^F) = (R*−1)/R* and TV = 1/R* → 0. Constants are
    pool-parameterized and preregistered per fixture. The C/√V* rate (Lemma D: mode atom
    ≤ 2/σ for σ* ≥ 2) holds ONLY in the contested regime (bounded fractional orders, bounded
    V*/R*) and is a regime corollary, never a uniform bound.
  - Corpus-level contraction: the single-round constant lower-bounds the full-corpus
    separation on any grammar coarser than the full tape, including F_exec.
  - Lemma D (hypergeometric mode-atom ≤ 2/σ, σ ≥ 2) — proven, self-contained via explicit
    Stirling bounds.

**Conditions and scope.** (A3′) engine draw-law realization: the MVHG constants are conditional
statements about the recorded kernel semantics until the post-freeze S3/conformance
machine-check pins them; failure of (A3′) is the STOP-class engine-law mismatch. The positive
branch is a statement about the frozen engine semantics and the enriched-fixture / S3-scaffold
family — NEVER about the 21/22-event frozen bundle, whose only touched level is single-maker
(instantiating the collapse stratum). Single-maker and exhaustion strata are preregistered
negative-control strata, excluded from separation claims. Stage-2 items (identical-input
replay through the recorded request subsequence with only allocation_rule swapped; the
single-maker negative-control run) remain run-gated [AUTH].

### 2.6 V4 — the gauge-conflation remark (FINAL TEXT; Lemma A/B-backed)

The following replaces the theory-appendix draft verbatim (KT-G3 §4). Under the KT-M1 REFRAME
rule, if the empirical gauge-twin nulls, the lemmas stand as recording-map facts and only the
final empirical sentence is rewritten as a boundary report.

> **V4 (not a gauge; quotienting is not a repair).** *The mechanism fiber is not a gauge
> symmetry, and quotienting the hypothesis space is not a repair.* A gauge symmetry of a
> hypothesis space is a function-preserving equivalence: every observable, loss, and deployment
> map is constant on its orbits, so quotienting is harmless-by-design and removes genuine
> redundancy — the design principle of Quotient-Space Diffusion Models (ICLR 2026) for internal
> SE(3) orbits, and, in the same symmetry family, of the conservation laws Neural Mechanics
> derives for the training dynamics (ICLR 2021).
> The through-M mechanism fiber is provably not of this kind. **By Lemma A**, any quotient of
> raw-flow space that (i) keeps the F_exec training corpus recoverable (corpus-compatibility)
> and (ii) is nontrivial on the fiber — as any fiber-collapsing repair must be — necessarily
> breaks the factorization of a preregistered consumer: the identity deployment already
> separates fiber members through the risk consumer C_risk on every unrecorded magnitude
> direction (the Corollary 2 recession directions); the kernel-swap deployment separates
> never-drawn split directions through the next-draw probabilities q_i/S (Theorem 3, P3.2);
> the latency/truncation family separates clock directions (P3.3). The equivalence is a
> property of the recording mechanism, not a symmetry of the market: fiber members are
> physically different states (different submitted flows, different consumers, different
> outcomes under D_swap and D_trunc) that are informationally identical to the training loss.
> **By Lemma B**, the repair is also vacuous as an error-reduction device: every through-M
> predictor is tape-measurable regardless of hypothesis space (Lemma 0), so its best-case
> consumer error equals the Theorem 1 information floor exactly — for deterministic quotients,
> loss-side quotients, and stochastic/soft encoders alike, a fiber-measurable encoder being
> fiber-constant in distribution; the floor depends only on the recorded σ-algebra, the
> consumer, and the practitioner's prior — not on the representation. Quotienting therefore
> deletes physically market-relevant states without moving the floor: destruction, not
> relocation (Lemma B.5). The internal precedent is EcoMD v2's gauge_enforce ablation
> (2026-04-25): enforcing an invalid gauge on the pair representation erased |s_i|-dependent
> information required for volatility clustering — 33/33 gauged configurations locked at 4/11
> stylized facts, recovered by disabling the enforcement — the same failure class in
> engineering form. What does survive as a genuine gauge is exactly the conceded residue:
> ownership relabeling of never-executed orders (the aggregation core of T1-P2(v)); on all
> consumer-relevant coordinates the fiber is function-preserving iff its ambiguous set is
> empty (Lemma A.4). The correct responses to fiber degeneracy are exposure characterization
> (Theorem 3) and information-side repair (raw-arm information, Proposition 1b) — never
> quotienting; the empirical twin is the KT-M1 gauge-repair falsification. Within-fiber drift
> under SGD (T4) is a separate, conjecture-only question about optimizer selection among
> fiber-equivalent parameters and is not claimed (Soudry et al. 2017; The Loss Does Not See
> the Basis but Adam Does, 2026).

**Status and citation conditions (frozen).** KT-G3 Lemma A: proven with its hypothesized
conditions (F_exec payload projection excluding integrity hashes and order_accepted;
preregistered C_named; per-fiber conditional on a (q,t)-nontrivial fiber). Lemma B (incl. B.3
soft/randomized quotients and B.4 prior-universality): proven. Lemma B is corollary-grade by
design and is never sold as a new estimation theorem. **Wordings that must never appear**
(checked at panel and again at D0): "the fiber is a gauge symmetry" (false by Lemma A);
"quotienting removes the degeneracy" (vacuous by Lemma B.2); "canonical interleaving restores
kernel invariance" (refuted by A.2 + B.5, empirically by KT-M1). Ownership-relabeling of
never-executed orders is conceded as a genuine function-preserving gauge core.

### 2.7 Theorem-package summary table (frozen labels)

| Claim | Lead content | Status | Live conditions |
|---|---|---|---|
| T1 | triple-interaction aggregate-sufficiency obstruction, both boundaries | proven_with_conditions | R2-B responsive-policy class; KT-G4(c) D-transport compatibility; enrichment dependency for empirical realization |
| T2 Theorem 1 | exact bounded consumer-variance floor, tight, tape-computable, exact zeros | proven_with_conditions | A1–A5; reference convention declared |
| T2 Defense 4 (G2-2) | kernel-blind uniformly valid floor bounds forced identically zero | proven (given Theorem 1) | none (convention-robust) |
| T2 G2-3 | same-data finite-gap ρ = 4·m_out/m ∈ [0,4), instance 3 | proven_with_conditions | frozen two-sided reference convention; draw-realization conditioning; width-matching inversion disclosed |
| T3 T-1/T-2 | exposed-set table + composition laws, D_read/D_raw nulls | proven (T-2c proven_with_conditions) | grammar scope clause; ru-cell swap→fifo row instance-level |
| T4 | within-fiber optimizer drift | conjecture | none — never confirmatory |
| H5 (KT-A2) | key-equalized TV = 1 − ∏C(q_i,c_i^F)/C(R*,V*), per-fixture constants | proven_with_conditions | (A3′); per-fixture constants only (no uniform-in-pool constant) |
| V4 (KT-G3 A/B) | not a gauge; no quotient repair | proven (A with hypothesized conditions; B) | corpus-compatibility + fiber-nontriviality; KT-M1 dependency for the final empirical sentence |

### 2.8 Needs-verify and deliberately-excluded notes (vocabulary only; never cited as fact)

- **Markov-lumpability literature** — used as vocabulary only; both lumpability statements are
  proved directly from the engine. If any theorem name retains "lumpability," the flag note
  "vocabulary only; needs-verify" must accompany it; this prereg uses "aggregate-sufficiency
  obstruction" in theorem names (panel A.8 ruling adopted).
- **Le Cam two-point lineage** — deliberately excluded; the needed inequality (R2-D) is proved
  inline from the TV triangle inequality.
- **Maximal-atom / log-concavity bounds for lattice laws** — not invoked; only the unproven
  general-composition constant would need them (T1 scope).
- **Optional MVHG/log-concavity bibliographic anchor** — not needed; Lemma D is self-contained
  via explicit Stirling bounds.

---

## 3. Statistical contract (incorporated by reference) and load-bearing numbers

### 3.1 Incorporation identity and pre-freeze amendment record

The document **"Statistical Contract Port: Paper D → ALPHA Market Cube (FROZEN CONTRACT v1
candidate)"** (`papers/proposal/ecomd_reexploration_contract_v1_2026-09-06.md`), clauses C1–C16
and one-shot analyzer gates G1–G12, is incorporated by reference in full, together with its
pre-freeze amendment banner of 2026-09-06 (PI rulings "用需要算力多的那个，批准，确认，确认"):
(A) C2 K = 16 (K-preflight conservative rule `none_in_set` → 16; PI chose the compute-heavier
option, ~+15% Stage-1 eval V100-h; K immutable after D0); (B) C3 kernel sentence tightened
(engine kernels exactly {fifo, random_unit_within_price}; pro_rata is S3 exact-arithmetic only
and never executes in any cell) — recorded as C16 ledger items (11)–(12).

**v2 pre-freeze restatements (panel-mandated; lawful amendments with recorded provenance until
the D0 freeze binds them; each becomes a C16 ledger row, Section 10.1):**

- (C) **C14 restated** under K = 16 with the complete record enumeration of Section 3.4 —
  C16 item (15). The contract's printed "122,880 (30 x 8 x 4 x 4 x 8 per block x 4 blocks)"
  is stale K = 8 arithmetic and is superseded by Section 3.4's 299,520-record campaign
  enumeration.
- (D) **C9 transfer-gate primary reference disambiguated** — C16 item (16): "primary J" in the
  B3 gate means **B3's own primary-analogue cell (kernel-swap axis, horizon 16, block B3)**,
  never the B1 primary cell (panel R1-2 ruling; the cross-block reading is rejected as
  outcome-choosable).
- (E) **C2(e) dead-letter clause rewritten** (panel R1-8/R2-4): see the C2(e) text in
  Section 3.2.
- (F) **Contract Part 2 section 2a.6 sentence** ("reverse swap and pro_rata swaps are
  exploratory") marked superseded by PI ruling D1_14 + panel R3-2: the reverse swap
  (random_unit → FIFO at inference) remains an executable exploratory item; **pro_rata is not
  an engine kernel and never executes in any cell — S3 exact-arithmetic analyses only**
  (Annex C, item C-5).

Derivation sections of the contract retain their original K = 8 wording as historical
reasoning superseded by the frozen clauses (Annex C).

### 3.2 Load-bearing clauses (inline restatement; amended contract text authoritative)

- **C1 Units and pairing.** Inference unit = seed (root of a frozen RNG derivation tree:
  data, init, minibatch, train_kernel, kernel:1..K). Kernel draws, rollout rounds and tapes are
  nested, never inference units. n = 30 seeds per block (Stage-2 subsets 15, pinned below);
  fresh never-reused ranges: **B1/B2 seeds 11000–11029; B3/B4 seeds 12000–12029** (PI decision
  D1_10 governs; the ops draft's 1000–1029/2000–2014 convention is superseded — Annex C, C-2).
  **Stage-2 first-15-seed subsets pinned (panel R3-5): B2 = seeds 11000–11014; B4 = seeds
  12000–12014, ascending within namespace.** Each bootstrap draw resamples the complete paired
  eight-cell seed vector.
- **C2 Randomness contract.** (a) Primary-truth DGP frozen in the M0/M1-lumpable policy class
  (actions depend only on anonymous book state, own inventory, cash, induced values — never on
  allocation identity), so executed request streams are kernel-invariant and request-level CRN
  is exact; this is the single load-bearing pairing assumption. (b) **K = 16** inference-kernel
  draws per seed per cell, derived spawn(seed, "kernel", k), k = 1..16, replayed identically
  across cells within a seed; per-seed cell value = K-draw mean. Provenance: K-variance
  preflight (`experiments/reexploration/k_preflight_20260906/`, results sha256
  `f61e410cd59c37b5624504a3cdf057c701b4b682067f948d2f8528ace018c2d4`) — frozen conservative
  rule (every random_unit draw-dependent statistic with bootstrap 95% upper bound of the
  between-ratio ≤ 0.10) returned `none_in_set` (alloc_proprata_dev_mean draw-dominated at every
  authorized K: ratio 0.1958, CI [0.1182, 0.4703] at K = 16) → K = 16 with explicit
  insufficiency flag; PI ruling 2026-09-06 (addendum D1_11) chose K = 16. K adjustment window
  CLOSED; K immutable through D0 and after. alloc_proprata_dev_mean carries an explicit
  draw-noise caveat in all reporting, and every allocation-level confirmatory contrast is
  stated at seed-mean level with the draw-noise guard of Section 4.4. (c) Deterministic-kernel
  cells execute 16 identical evaluations; byte-identity is gate G8. (d) Deterministic neural
  decode at eval. (e) **(rewritten at v2; panel R1-8/R2-4)** The E-2 corpus generator (D0
  build) is preflighted against the same preflight protocol BEFORE the D0 freeze; the result
  is recorded as caveat-and-reporting-only. **K = 16 is immutable regardless of that preflight's
  outcome.** If the E-2 preflight shows material endpoint-shaped draw-noise insufficiency
  (a between-ratio upper bound > 0.10 on any endpoint-shaped statistic), that fact is a named
  STOP-class PI decision item at D0 — it can stop or restructure the campaign before launch,
  never change K. The M1 own-state question is dissolved empirically, not definitionally: the
  E-2 preflight runs on the actual D0 generator (whatever its own-state structure), so
  "adds feedback channels" never has to be adjudicated in the abstract; the preflight measures
  the generator that will actually generate the corpus.
- **C3 Cube structure and estimands.** Trained arms (c, t), c ∈ {absolute next state,
  increment}, t ∈ {raw, through-M}; each evaluated at e ∈ {raw, through-M} → 8 cells.
  D_{te} = Ȳ_absolute,te − Ȳ_increment,te; J = D_00 − D_10 − D_01 + D_11;
  φ_train = (T_0 + T_1)/2; φ_infer = (E_0 + E_1)/2, where **(pinned inline at v2, panel R2-7)
  T_0 = D_00 − D_10 and T_1 = D_01 − D_11 are the training-enforcement contrasts at inference
  enforcement raw and through-M respectively; E_0 = D_00 − D_01 and E_1 = D_10 − D_11 are the
  inference-enforcement contrasts at training enforcement raw and through-M respectively**
  (subscript order in D_{te} is (training, inference)). Positive J = the absolute-minus-increment
  contrast grows with joint through-M enforcement. M = the exact combinatorial clearing layer
  (volume and cash conservation, unit integrality, tick lattice, priority kernel ∈ exactly
  **{fifo, random_unit_within_price}**, `scripts/lab_asset/schema.py:22-24`; **pro_rata is NOT
  an engine kernel and never executes in any cell** — S3 exact-arithmetic only, per PI ruling
  D1_14). Through-M training uses the preregistered surrogate family frozen at D0
  (Section 5). **No confirmatory test compares through-M vs raw for superiority; the estimand
  is path-dependence attribution.**
- **C4 Blocks, axes, horizons, fixture generators; kernel-swap stratum definition.** Blocks
  B1 = (L1 EcoMD v2 x lab-asset-v3) [primary], B2 = (L1 x synthetic), B3 = (L2 recurrent
  fact-surrogate x lab-asset-v3), B4 = (L2 x synthetic). Axes (4, confirmatory): ID;
  agent-population x2 (prestates regenerated at 2N, induced capacities rescaled per
  lab-asset-v3 schema); tick x2 coarser (tick 2Δ, frozen band-scaling rule); kernel-swap (DGP
  truth under FIFO; through-M inference under random_unit; truth reference unchanged).
  Horizons: {1, 4, 16, 31} autoregressive clearing rounds (h = 64 recorded descriptively only).
  All fixtures from the frozen fixture-generation procedure from seed roots; every prestate and
  tape sha256 bound at D0 (lab-asset-v3 bundle manifest
  `fea8a136b0c3e19a00bddcb131a1540ca40fda6c1576dbc949001dbf76a9581c` is the schema anchor;
  per-seed fixtures extend, never modify, the schema).

  **Kernel-swap stratum (pinned paragraph, panel R2-3; single pinned location, cross-referenced
  by G10).** (i) Through-M TRAINING embeds M with the **FIFO kernel** — the truth kernel on
  the FIFO-generated F_exec corpus; every block's DGP truth is generated under FIFO. (ii) The
  kernel-swap axis changes ONLY the inference-M deployment kernel, from fifo to
  random_unit_within_price. (iii) Raw-inference cells ((·, raw-train, raw-infer) and
  (·, through-M-train, raw-infer)) have no inference-M clearing layer, hence no deployment
  kernel: **their kswap-stratum evaluations are byte-identical duplicates of their ID-stratum
  evaluations**, recorded separately for record-coverage symmetry with `allocation_rule`
  pinned to the training-time kernel field (`fifo`) and n_draws == 16 per G8/G10; the analyzer
  checks the duplicate byte-identity and a mismatch is a G8/G10 failure. (iv) Consequently
  R00(s) — computed at the (increment, raw-train, raw-infer) cell of the same stratum — is
  **numerically identical across the ID and kswap strata by construction**, so δ_s at kswap is
  anchored to the ID-scale R00; the contract Part 2b rationale that "OOD axes get proportionally
  larger thresholds" applies to the population and tick axes and NOT to the kernel-swap primary
  axis (v1's silence on this was the defect; this paragraph is the correction).
- **C5 Endpoints.** Primary: conserving-channel rollout error against DGP truth,
  Y = sqrt(mean_ch mean_t ((x̂_ch,t − x_ch,t)/s_ch)²), **channels pinned at v2 (panel R2-6):
  exactly two AGGREGATE engine-level conserving channels per clearing round — {total executed
  volume units, total executed cash ticks}** (aggregate per-round totals; no per-actor or
  per-side series in the primary endpoint). Granularity consequences, stated so the choice is
  auditable: the DGP-truth side is draw-invariant given the request stream (M0/M1-lumpability:
  the aggregate state sequence is a measurable function of aggregate initial state + request
  sequence); the simulator side is draw-sensitive through internal clearing feedback
  (random-unit allocation draws move remaining per-order quantities, hence future matching,
  hence future aggregate outcomes) — therefore K-draw averaging IS active on the primary
  endpoint, exactly as C2(b) provides. **s_ch frozen DGP-native per-event innovation std,
  computed from the hash-sealed DGP-only sample branch** (single branch, pinned at v2: s_ch is
  computed on the DGP-truth side alone, from the D0-hash-committed generator sample, never
  from simulator output and never from the paired corpus; the either/or "analytic values or a
  hash-sealed DGP-only sample" wording of v1 is resolved to the hash-sealed DGP-only sample
  branch, Annex B(e)). Through-M cells' conservation violation exactly zero (integer-exact);
  raw cells never clamped or repaired. Book-state and price-path errors: preregistered
  secondary, descriptive only, outside all Holm families.
- **C6 SESOI.** Per stratum s: **δ_s = 0.1 · Ȳ_R00(s)**, R00(s) = the (increment, raw-train,
  raw-infer) cell in the same stratum. Reference-degeneracy guard: Ȳ_R00(s) < 1.0 scaled unit
  → "unresolved (reference-degenerate)", no positive label, reported, never dropped, never
  rescoped. Primary fallback strata in order: B1 kernel-swap h31; B1 tick-shift h16;
  B1 population h16.
- **C7 Ordered classification (verbatim).** *Material non-additivity* if the 95%
  paired-bootstrap interval for the estimand lies wholly above +δ_s or below −δ_s; *smaller
  statistical non-additivity* if that interval excludes zero but the first rule fails;
  *practical additivity* if the 90% interval lies wholly inside [−δ_s, +δ_s]; *unresolved*
  otherwise (with the reference-degenerate sub-label per C6). Both interaction and additivity
  are falsifiable; an interval spanning zero and a SESOI boundary receives no positive label.
- **C8 Bootstrap (verbatim mechanics).** 50,000 draws, percentile intervals, seed-level
  resampling of the complete paired eight-cell vector; draws averaged within seed and never
  resampled. **Bootstrap RNG seed derivation pinned at v2 (Annex B(a)): for each (block,
  family) the bootstrap seed = int(sha256("ecomd_reexploration_v2_bootstrap" || block_id ||
  family_id), 16) mod 2^63 — deterministic from frozen strings, independent of all training
  seeds, recorded in the analyzer manifest.**
- **C9 Primary and multiplicity.** Primary cell: **B1, kernel-swap axis, horizon 16**; single
  prespecified primary; not Holm-adjusted; not overridable by secondaries. Holm families:
  sign-flip tests on the 16 mandatory interaction cells (4 axes x 4 horizons) per block,
  Holm WITHIN each block (4 families of 16). Axis-contrast secondary family: per block the
  three (J_axis − J_ID) at horizon 16, Holm within the triple. Architecture-transfer gate
  (C9 as amended at v2, panel R1-2; C16 item (16)): **B3 passes iff B3's own primary-analogue
  cell (kernel-swap axis, horizon 16, block B3) is material AND ≥ 8/16 mandatory cells of
  block B3 are material** (Paper D 6/12 fraction preserved); failure reported as an
  architecture boundary (U-Net lesson), never hidden, never re-gated. **Gate denominator under
  degeneracy (pinned at v2, panel R2-8): the ≥ 8/16 denominator remains 16 under per-cell
  reference degeneracy — degenerate cells count as not-material, the gate is never renormalized,
  and a gate failure can never be attributed to or excused by degeneracy after results are
  seen (degeneracy labels are reported alongside).** The h = 1 strata are pre-flagged as the
  degeneracy-risk strata (one-step conserving-channel increments are near-deterministic given
  the request stream).
- **C10 Class flips and reporting-all.** Every cell, axis, horizon, block, class flip and null
  reported unconditionally (unrun cells surface as "not run"/"unresolved", never dropped);
  class flips are preregistered descriptive findings carrying no p-values; the transfer gate is
  the only preregistered lineage-level decision.
- **C11 Zero-training surgery cells.** Derived from sha256-locked checkpoints (lock order: last
  training record → hash lock → metric unlock); zero optimizer steps; parameter parity
  byte-identical to parent; inference randomness identical to C2 (seed-owned kernel streams
  inherited by surgery cells).
- **C12 Reflexive firewall.** The five firewalls verbatim: namespace separation; temporal
  separation (scheduled only after all four confirmatory one-shot analyzers have run and their
  analysis-JSON hashes are published); statistical separation (descriptive only, mandatory
  label "exploratory, excluded from confirmatory inference", TRADES 2025 / DEX closed-loop 2026
  cited for the paired-seed descriptive discipline it does follow); no gate inputs; no
  retro-hypotheses.
- **C13 One-shot analyzers.** Each analyzer runs once, on complete records, after gates G1–G12
  pass, in order; any failure aborts with no partial metrics; no rerun without a new frozen,
  hash-recorded amendment.
- **C14 Record-coverage contract.** **Restated at v2 with the complete enumeration of
  Section 3.4** (panel R1-1/R2-1/R3-1; C16 item (15)). The operative count for gate G1 is the
  v2 Section 3.4 table: **299,520 confirmatory evaluation records campaign-total (215,040
  mandatory-axes + 76,800 truncation passes + 7,680 audit cell), 450 trainings, 420 horizon-one
  probes**; the contract's printed 122,880 is stale K = 8 arithmetic, superseded.
- **C15 Frozen macros.** All tables and macros generated from the hashed analysis JSON; macros
  include K, fixture-manifest hashes, and the amendment ledger (non-omissible).
- **C16 Amendment ledger (generated, non-omissible).** Items (1) seed = RNG-tree root;
  (2) eight-cell resampling vector; (3) R00 coordinate pinned to increment; (4) channel-scaled
  multi-channel endpoint; (5) reference-degeneracy guard; (6) Holm families 4 x 16
  (Paper D: 1 x 12); (7) axis-contrast family; (8) K-draw CRN protocol; (9) transfer-gate
  fraction 8/16 = 6/12 preserved; (10) clearing-identity gate replaces projection-identity
  gate; (11) K = 16 (preflight `none_in_set` → 16, sha256 f61e410c…, PI ruling "用需要算力多的那个");
  (12) kernel set = {fifo, random_unit_within_price}, pro_rata demoted to S3 exact-arithmetic;
  **(13) two-stage execution (ratified at v2, panel R1-5/R3-1; PI decision D1_04): Stage 1 =
  B1+B3 at 30 seeds confirmatory; Stage 2 = B2/B4 at the pinned first-15-seed subsets
  (11000–11014 / 12000–12014), directional robustness only, mechanical triggers only
  (Section 4.1), B2/B4 mandatory-family tests executed and reported with NO confirmatory
  material-nonadditivity claim attaching to any Stage-2 cell (family status: descriptive
  robustness, Holm p-values computed for completeness and labeled non-confirmatory);**
  **(14) truncation secondary family (ratified at v2 with corrected membership, panel
  R1-4/R3-4/R2-2(i); plan ruling 5): per L1 block a TWO-test Holm family
  {J_trunclag,h16 − J_ID,h16; J_trunccap,h16 − J_ID,h16}, one-sided in the O-C direction
  (divergence nondecreasing in truncation), Holm within the pair; per L2 block a ONE-test
  family {J_trunclag,h16 − J_ID,h16} — recorded reason for the change from the plan's "3
  tests/block": membership was never enumerated anywhere in the package, and the L2 trunc_cap
  de-scope (Section 8.2 ladder) makes a uniform 3-test family structurally impossible in
  B3/B4; no third test exists to define;** **(15) C14 restatement under K = 16 (Section 3.4);**
  **(16) C9 transfer-gate primary reference = B3's own primary-analogue cell (kernel-swap,
  h16, block B3).**

### 3.3 One-shot analyzer gate list G1–G12 (one line each; G2 and G4 amended at v2)

- **G1 Record coverage**: exact counts per the ratified C14 (Section 3.4 table), per
  cell/axis/horizon/draw; no extras, no missing.
- **G2 Run-ID uniqueness and seed pairing — with namespace-disjointness sub-check (folded in
  at v2, panel R3-8; NOT a new gate)**: each seed's 8 cells share
  data/init/minibatch/train_kernel stream hashes and config hashes; AND every preregistered
  instrument/instrument-analysis namespace is disjoint from every training namespace and from
  every other: S3 robustness seeds (Annex B(c)), enrichment master 20260972, resampler
  namespace 20260973, K-preflight 31000–31099, bootstrap seeds (Annex B(a)), and training
  namespaces 11000–11029 / 12000–12029.
- **G3 Source/config binding**: DGP fixture manifest hashes (incl. lab-asset-v3 anchor
  `fea8a136b0c3e19a00bddcb131a1540ca40fda6c1576dbc949001dbf76a9581c`, the canonical value;
  Annex C typo inventory governs audit reconciliation), schema_version == "lab-asset-v3",
  git SHA, config.yaml hash, seed ranges per C1.
- **G4 Checkpoint binding (amended at v2, panel R2-1)**: **450** checkpoint sha256 vs lock
  manifest (240 Stage-1 mandatory + 180 Stage-2 + 30 audit-cell; Section 3.4); surgery records
  reference parent hash.
- **G5 Parameter parity + zero-step attestation**: surgery parameters byte-identical to parent;
  optimizer-step count = training-final.
- **G6 Horizon-one clearing identity**: through-M on the DGP's realized request stream
  reproduces the DGP tape byte-exactly (lab-asset replay validator, record-by-record including
  every state_hash).
- **G7 Conservation exactness**: through-M inference cells exactly zero volume/cash conservation
  violation at every step (integer-exact); no clamping anywhere.
- **G8 Deterministic-kernel draw identity**: fifo cells' K = 16 draw-records byte-identical;
  raw-inference kswap-stratum duplicates byte-identical to their ID-stratum evaluations
  (C4(iii)).
- **G9 Determinism replay**: frozen 5% seeded sample of records re-executed byte-identically.
  **Selection rule pinned at v2 (Annex B(b)): deterministic stride — sort all record keys
  lexicographically within each record class, select every 20th record starting at index 0
  (exactly 5%), no RNG.**
- **G10 Field validity**: finite metrics; pre/post_best_bid/ask present; allocation_rule
  matches the cell/axis spec **per the pinned kernel-swap stratum definition (C4(i)–(iii),
  including allocation_rule = fifo on raw-inference duplicates)**; n_draws == 16.
- **G11 Namespace hygiene**: no exploratory/reflexive namespace records in any confirmatory
  input.
- **G12 Macro binding**: analyzer emits macros exactly once from the analysis JSON; hashes
  published.

One-shot discipline additionally covers: frozen draw count K, kernel-stream derivation,
fixture-generation procedure, axis generators, and estimators — any change after D0 is a
frozen, hash-recorded amendment or nothing.

### 3.4 C14 record-coverage arithmetic — RESTATED AT V2 (ratified; C16 item (15))

Authoritative enumeration under K = 16, derived from the C1/C2/C14 definitions (seeds ×
8 cells × 4 axes × 4 horizons × K = 16 draws per block for mandatory axes; L2 drops trunc_cap
per the de-scope ladder; Stage-2 subsets pinned at 15 seeds; B4 carries BOTH DGP variants per
D1_05 — variant A both lineages, variant B L2-only — so B4 contributes two variant sub-blocks;
the audit cell A10 retrain contributes its own training and evaluation records). **Panel
adjudication recorded (R2-1 over R1-1/R3-1's carried-over 61,440): v1's Stage-2 evaluation row
(61,440) double-counted no variant yet v1's own training row (180) counted both — internally
contradictory; the correct mandatory-axes Stage-2 total is 92,160.**

**Mandatory-axes evaluation records (per seed-block unit = 8 cells × 4 axes × 4 horizons × 16
draws = 2,048 per seed):**

| Block | Lineage × DGP | Seeds | Records |
|---|---|---|---|
| B1 (Stage 1) | L1 × lab-asset | 30 | 30 × 2,048 = **61,440** |
| B3 (Stage 1) | L2 × lab-asset | 30 | 30 × 2,048 = **61,440** |
| B2 (Stage 2) | L1 × variant A | 15 | 15 × 2,048 = **30,720** |
| B4-variantA (Stage 2) | L2 × variant A | 15 | 15 × 2,048 = **30,720** |
| B4-variantB (Stage 2) | L2 × variant B | 15 | 15 × 2,048 = **30,720** |
| **Stage 1 subtotal** | | | **122,880** |
| **Stage 2 subtotal** | | | **92,160** |
| **Mandatory-axes campaign total** | | | **215,040** |

(Full 4-block 30-seed grid at K = 16, for reference: 245,760 — not the authorized design.)

**Truncation-condition deployment passes (secondary family; C16 item (14); at the ID axis, all
8 cells, all 4 horizons, K = 16 draws per condition; L1 blocks carry both conditions, L2 blocks
trunc_lag only):**

| Block | Conditions × seeds × 8 × 4 × 16 | Records |
|---|---|---|
| B1 | 2 × 30 × 8 × 4 × 16 | **30,720** |
| B3 | 1 × 30 × 8 × 4 × 16 | **15,360** |
| B2 | 2 × 15 × 8 × 4 × 16 | **15,360** |
| B4-variantA | 1 × 15 × 8 × 4 × 16 | **7,680** |
| B4-variantB | 1 × 15 × 8 × 4 × 16 | **7,680** |
| **Campaign total** | | **76,800** |

**Audit cell A10 (KT-A4 two-estimator audit; Section 5.4):** +30 trainings (D1 block, L1
lineage, 30 paired seeds 11000–11029); evaluation records = 1 cell × 30 seeds × 4 axes × 4
horizons × 16 = **7,680**. The audit reuses B1's D1/L1 fixture streams (pinned; no new
horizon-one probes and no new fixtures: same data/init/train seeds, only the estimator
differs).

**Campaign totals (the G1 target):**

| Quantity | Count |
|---|---|
| Mandatory-axes evaluation records | 215,040 |
| Truncation deployment passes | 76,800 |
| Audit-cell evaluation records | 7,680 |
| **Confirmatory evaluation records, campaign total** | **299,520** |
| Trainings / sha256-locked checkpoints (G4) | 240 (Stage 1: 4 arms × 30 seeds × 2 lineages) + 180 (Stage 2: 120 variant-A both lineages + 60 variant-B L2-only) + 30 (audit A10) = **450** |
| Horizon-one clearing-identity probes | 4 × 30 + 4 × 30 + 4 × 15 + 4 × 15 + 4 × 15 = 120 (B1) + 120 (B3) + 60 (B2) + 60 (B4-A) + 60 (B4-B) = **420** (per block-lineage × DGP-variant unit at 4 axes; K-independent) |
| Reflexive namespace | excluded by construction, uncounted (C12) |

Derivation notes for the record: the mandatory-axes formula is the contract's own
(seeds × 8 × 4 × 4 × K); the Stage-2 row follows from D1_04 (15-seed subsets) and D1_05
(variant A both lineages; variant B L2-only ⇒ B4 = two variant sub-blocks); the truncation-pass
enumeration follows from plan ruling 5 as corrected by C16 item (14) (two conditions on L1,
one on L2 after the de-scope ladder); the probe count formula (4 axes per block-lineage-variant
unit) preserves the contract's per-unit structure under the two-stage split. Residual
ambiguity flagged for the PI: none — every formerly "[TO BE PINNED AT D0]" count is now
enumerated above; the only D0-pinned items remaining in this document are the freeze timestamp
and freeze sha256 (Section 1.3).

---

## 4. Experimental design

### 4.1 Blocks, lineages, DGPs, staging

Lineages: L1 = ecomd_v2 transformer/potential (`ecomd/models/ecomd_v2.py`); L2 = recurrent
fact-surrogate (code-only pre-D0 build per PI ruling D1_13: architecture + training loop +
CPU-torch-loadable checkpoint format + RNG-tree-namespaced seeding surface, validated by CPU
smoke; GPU training stays D0-gated). Both lineages ship frozen simulator contracts (input
grammar; ABS/INC semantics; enforcement path + estimator; RNG wiring; checkpoint format; pass
the 27 conformance tests + replay validator). **L1-4 RNG fix (SPS edge sampling on global
torch.rand) must land BEFORE D0** or cross-node byte-exact replay rests on an assumption rather
than a contract (Annex A.7) — this is a named pre-freeze blocking item for the PI.

DGPs: D1 = lab-asset-v3 dual-arm engine (bundle manifest
`fea8a136b0c3e19a00bddcb131a1540ca40fda6c1576dbc949001dbf76a9581c`) as primary truth,
with a frozen M0/M1-lumpable request generator (episodes, actor mix, rates, bands, master seeds
hashed at D0). D2 = synthetic robustness, Stage 2 only: variant A `garch_student_t5` (both
lineages), variant B `multiscale_logvol` (L2-only), each through a frozen series→request
wrapper into the SAME engine (conservation/replay semantics preserved);
`negative_jump_iid` named-but-not-run.

Staging (two-stage amendment, PI decision D1_04; C16 item (13)): **Stage 1 confirmatory** =
B1 + B3 (both lineages x lab-asset), 30 seeds, ~650 V100-h (anchor T = 1.8 V100-h per Paper-D
training run; ~19–20 days at 70% campaign efficiency; 4-week hard ceiling). **Stage 2
conditional robustness** = B2 + B4, preregistered first-15-seed subsets (11000–11014 /
12000–12014, C1), directional robustness only (no material-nonadditivity claims from Stage 2;
mandatory-family tests executed and reported as descriptive robustness per C16 item (13)),
~410 V100-h, **mechanical triggers only — never outcome-triggered**: (t1) cumulative burn <
1,150 V100-h; (t2) Stage 1 complete by D0+26d; (t3) L1 convergence-failure rate ≤ 15%
(quality gate, not performance); (t4) **mechanical L2 trainability threshold: ≥ 28/30 L2 seeds
reach finite training loss under the day-5 thresholds on D1** (renamed at v2 per panel R1-3;
this is a trainability count, not the C9 gate). **The C9 architecture-transfer-gate result is
NOT an input to any Stage-2 entry, de-scope, or cancellation decision; any outcome-triggered
Stage-2 launch downgrades the D2 block to exploratory or forbids it (Section 8.3).** Day-5
trainability quality gate (NaN ≤ 5% at long rollout; R00 val ≤ 3x L1 seed-median; ≥ 28/30
seeds complete) = early warning only.

Ops prerequisite: node cleanup at D0-S1 (relocate paper D deployment archive to
r2://ecophys/paper_d_archive/ with manifest verification; target ≥ 40% free on both currently
98%/96%-full V100 nodes) — authorized (D1_09), executes at D0, nothing deleted without a
verified manifest.

### 4.2 Axes, horizons, truncation secondary family

Confirmatory axes (4) and horizons {1,4,16,31} per C4, with the kernel-swap stratum definition
pinned at C4 (training kernel FIFO; deployment kernel swap at inference; raw-infer duplicates).
Truncation conditions (trunc_lag, trunc_cap) run as deployment-map passes carrying orderings
O-C/O-D as the preregistered secondary Holm family **exactly as itemized in C16 item (14)**:
per L1 block {J_trunclag,h16 − J_ID,h16; J_trunccap,h16 − J_ID,h16}, one-sided in the O-C
direction, Holm within the pair; per L2 block {J_trunclag,h16 − J_ID,h16} alone. Record
coverage per Section 3.4 (76,800 passes). pop_4x, tick_half, and the reverse kernel swap are
exploratory periphery (4.7); **pro-rata analysis is S3 exact-arithmetic only and never
executes in the engine** (D1_14). h = 64 recorded descriptively only.

### 4.3 Endpoints (each mapped to its claim; all [AUTH] post-D0)

- **EP1 primary.** B1, kernel-swap axis, horizon 16 (fallbacks: B1-kswap-h31, B1-tick-h16,
  B1-pop-h16). Ordered classification vs δ_s = 0.1·Ȳ_R00(s); channel-scaled conserving-rollout
  RMS; reference-degeneracy guard. Supports the ALPHA attribution estimand and Prop 3.5's
  criterion.
- **EP2 (T2/T3 money results).** On locked checkpoints and S1a fiber pairs: O-A attribution
  floor; O-B swap asymmetry; O-C truncation monotonicity; O-D granularity fingerprint
  including the preregistered exact-zero null cell; O-E tape-measurable controls. Full
  per-test specification (statistic, units, margin, procedure, count, family status) in
  Section 4.4. Distinguishes mechanism fiber divergence from representational failure
  (Do LLMs Understand LOB Dynamics 2026) and operator set-identification
  (Counterfactual Operator Relevance 2025) via the three rescue levers (Section 2.3).
- **EP3 = S3 exact FIM rank grid** [CPU-exact]. 3 kernels x 3 rungs x V* ∈ {1,2,4,6} in R⁹;
  frozen τ = 1e-8; one-shot; preregistered ranks: (k, agg) rank 3 for all kernels and V*
  (kernel-independence signature); (fifo, po) 3,3,3,4 (rank = 2 + j*(V*), j*-schedule from
  prefix sums (5,9,12,14)); (pro_rata, po) 6 for all V* ≥ 1 (ray signature; S3
  exact-arithmetic only); (ru, po) 6,7,7,7; (ru, pu) = (ru, po) at every V* and (k, pu) =
  (k, po) for all k (saturation signature); annotated (ru, pu) at V* = 1 → 7 (eligible_units
  supplies R*). **The V* = 2 rank jump is the without-replacement discriminator** — under
  with-replacement / proportional-to-initial draws the count law is multinomial,
  proportions-only at every V*, and the jump never happens. Falsification map frozen (e.g.
  rank(ru,po) = 6 at V* = 6 kills P2(iii) — engine-law mismatch STOP). **S3 robustness-arm
  seeds pinned: 20260974, 20260975, 20260976** (Annex B(c)).
- **EP4 = S1a constructed fiber pairs.** fifo orthant injections on never-executed orders; ru
  integer splits across never-drawn orders at touched levels. Acceptance gates **S1a-G1–S1a-G3**
  (renamed at v2 per panel R1-7(f); formerly "G1–G3" of the theory appendix, never the analyzer
  gates): S1a-G1 byte-identical F_exec corpora; S1a-G2 state_hash chains differ; S1a-G3 |ΔC|
  matches Theorem 1's predicted linear/exact-split values. Hard prerequisite — fixture
  enrichment (Section 7.2); the 21–22-event frozen fixtures cannot measure O-C/O-D or the S1a
  random-unit gates.
- **EP5 = T4 drift telemetry.** Exploratory register only; citation pair Soudry 2017 + "The
  Loss Does Not See the Basis but Adam Does" 2026; never theorem-claimed.

### 4.4 Predicted orderings (S2, on locked checkpoints; confirmatory predictions from T2/T3) — full O-test specification

**Units and level conventions (pinned at v2, panels R2-2(ii)/R2-5).** All allocation-level
confirmatory quantities (O-B arms, KT-A3 resample arm, KT-M1) are computed and reported at
**seed-mean level**: the per-seed value is the K-draw mean (16 draws), and the interval is the
seed-level 95% paired bootstrap over seeds, so draw noise enters the interval through the
K-draw means rather than sitting outside the comparison. **Mechanical draw-noise guard:** for
every O-test or KT contrast whose decision margin is an allocation-level margin, if the margin
is smaller than 10× the preflight-derived draw-noise scale for that statistic class (bootstrap
upper CI of the within-seed draw-std of the K-draw mean, matched units; for the allocation
class the K-preflight's alloc_proprata_dev_mean gives within-seed variance W = 0.0141, i.e.
draw-std of the K = 16 mean ≈ √(W/16) ≈ 0.030 in its native units), the test auto-labels
**"unresolved (draw-noise-dominated)"** — it can never fire a confirmatory claim from inside
the draw-noise floor. The guard is a reporting-integrity control, not a power rescue.

**O-test specification table (each test: statistic, native units, margin, procedure, count,
family status).**

| Test | Statistic (seed-mean) | Native units | Margin / prediction | Procedure | Count | Family status |
|---|---|---|---|---|---|---|
| **O-A attribution floor** | consumer RMSE(through-M-trained, raw-infer) − R‖v_U‖/√12 | consumer notional units (v^T z); floor constant tape-computable | prediction: RMSE ≥ floor; float tolerance 1e-9 relative on the integer-exact floor | per cell: seed-level 95% bootstrap interval of RMSE; prediction confirmed iff interval lower bound ≥ floor − tol | per block: fiber-exposed consumer cells (locked checkpoints) | **Outside all Holm families, with justification:** the comparison constant is a deterministic tape-computable integer-arithmetic object (no sampling distribution on the prediction side); exhaustive pass/fail reporting of every cell with no selective claiming; paper sentence limited to "floor attained in k of n cells (full table)" |
| **O-B swap→ru** | allocation-consumer divergence under D_swap→ru | fill-count units (integer lattice; any nonzero divergence ≥ 1 fill) | prediction: Θ(δ/S) > 0, per-level weights 1/S preregistered | seed-mean divergence, 95% seed-level bootstrap interval; confirmed iff interval lower bound > 10× draw-noise scale (guard above) | per block, per locked checkpoint | **Outside Holm with justification** (deterministic subcheck + guard; see below) |
| **O-B swap→fifo (point null)** | allocation-consumer divergence under D_swap→fifo | fill-count units, integer-exact | **exact-zero point null** (Theorem T-1: Exp = ∅; any nonzero value falsifies) | integer-exact deterministic subcheck across all seeds and all K draws: prediction confirmed iff every measured divergence is exactly 0; NO statistical equivalence margin (v1's "equivalence-tested against the SESOI margin" was dimensionally undefined — δ_s lives in channel-scaled RMS units, the divergence in fill counts — and is withdrawn; the point null is stronger and unit-native) | per block, per locked checkpoint | **Outside Holm with justification:** integer-exact subcheck, no sampling distribution exists to calibrate |
| **O-C truncation monotonicity** | divergence increments vs window W | consumer units per arm family: (R²/12)Δ‖v_{U∩W}‖² (orthant) / (R²/3)p²Δ(m_in·m_out/m) (split) | prediction: increments match the precomputed curves; monotone nondecreasing in W, zero when no straddling | deterministic curve comparison per fixture (integer-exact curve constants; seed-mean measured increments with intervals; subcheck = zero at no-straddling windows) | per L1/L2 block × windows | **Outside Holm with justification** (tape-computable constants + integer-exact subchecks); the J-level truncation contrasts are separately INSIDE the C16-(14) Holm pair |
| **O-D granularity fingerprint** | magnitude-consumer floor collapse; exact-zero cell | consumer units | prediction: price-notional on ru splits floor ≡ 0 (preregistered null); latency consumer retains split floor | integer-exact zero subcheck for the null cell; interval comparison for the retained floor | per fixture family | **Outside Holm with justification** (exact-zero point prediction; falsifiable null, not a hedge) |
| **O-E controls** | training-enforcement interaction for tape-measurable consumers | δ_s units (endpoint Y) | prediction: zero interaction | ordered classification vs δ_s per C7 (same machinery as mandatory cells) | per block | **Descriptive control:** reported with C7 labels; no claim attaches |

**Deterministic subchecks (declared outside statistics by justification, panel R2-2(ii)):** the
eligible_units displacement under swap→ru, the O-B swap→fifo exact-zero null, and the O-C
no-straddling zeros are integer-exact engine-semantics checks — the predicted value is a
deterministic function of the recorded tape, there is no sampling distribution on the
prediction side, and pass/fail is exhaustive (every seed, every draw). They are reported as
pass/fail tables with no p-values.

**KT-A3 and KT-M1 contrasts (restated at seed-mean endpoint level, panel R2-5).** KT-A3:
swap arm = seed-mean endpoint divergence under D_swap (channel-scaled RMS units of Y, matched
to δ_s of the stratum); resample arm = seed-mean endpoint divergence under within-fiber
allocation regeneration; contrast fires KT-A3 iff swap > δ_s AND resample < δ_s/10, both at
seed-mean with 95% seed-level bootstrap intervals, and subject to the draw-noise guard on the
δ_s/10 margin. KT-M1 (gauge-twin): the fiber-resampler regeneration divergence at seed-mean
level against the same guard. Both are preregistered robustness gates outside all Holm
families (as in Section 5.5's audit logic: mechanical, exhaustive-reporting, no selective
claiming).

**Multiplicity mapping (panel R2-2(iii); stated so no corrected family licenses anything
unintended).** The Holm sign-flip 16-cell families (C9) feed **no gate**: the architecture-
transfer gate consumes the **UNADJUSTED C7 ordered-classification labels by frozen design**
(C9's "material" = the C7 95%-interval rule, not a Holm-adjusted p-value). The
Holm-adjusted sign-flip results are consumed by exactly these named paper sentences:
"interaction present under multiplicity control in k of 16 cells per block" (per block,
Section 4.3 of the paper) and the axis-contrast family sentence. No other claim, gate, or
ledger resolution consumes an adjusted value. The sign-flip families are confirmatory
multiplicity control for those sentences, not decorative, and not gate inputs.

All cells, axes, both lineages reported, including class flips and nulls.

### 4.5 Zero-training surgery cells (C11)

The 4 surgery cells per (trained arm, seed) = the trained (coordinate, training-enforcement)
arm evaluated at the other inference enforcement, on the same sha256-locked checkpoint, zero
optimizer steps, parameter parity byte-identical, inference randomness identical to trained
cells (seed-owned kernel streams). They are the empirical exhibit for V4: members
indistinguishable to the training loss (within-fiber) yet distinguished by the deployment maps.

### 4.6 Reflexive firewall (C12)

Reflexive deployment cell (simulator vs a simple adapting execution policy, sim-in-loop),
exploratory only (~6 V100-h; **10 seeds pinned at v2: first 10 of each namespace — B1-side
11000–11009, B3-side 12000–12009** (Annex B(d)); cells {R00, R11}; D1; both lineages), under
the five verbatim firewalls of C12, scheduled only after all four confirmatory one-shot
analyzer hashes publish.

### 4.7 Exploratory periphery (mandatory label; no confirmatory status)

Per-cell simple effects beyond the interaction; endpoint class-flip enumeration; reflexive
cell; tape-likelihood diagnostic (one-shot descriptive profile feeding T1/T2, outside
confirmatory machinery); SGD within-fiber drift measurements (T4, 10-seed telemetry subset
Annex B(d)); **reverse kernel swap (random_unit → FIFO at inference) — executable exploratory
item; pro-rata allocation analysis — S3 exact-arithmetic ONLY, never executed in the engine
(split at v2 per panel R3-2; the contract Part 2a.6 wording is superseded, Annex C-5)**;
pop_4x / tick_half; M2 adaptive DGP runs; any post-transfer-gate lineage follow-up. Mandatory
label on every output: "exploratory, excluded from confirmatory inference"; excluded from
abstract; no Holm; no SESOI claims.

---

## 5. Estimator menu (frozen; KT-A4)

Implementation: `ecomd/mechanisms/through_m.py` (CPU-only, typed, mypy --strict + ruff clean);
20/20 read-only fixture tests green against the frozen bundle (manifest sha256 re-verified
in-suite before any estimator claim; both arms replayed in memory only).

### 5.1 Primary — straight-through through-M, pinned scale

Forward = the exact integer clearing M (bit-identical to `ReferenceEngine._select_maker`;
FIFO fills by queue position; random-unit consumes the recorded draw stream unit by unit).
Backward = λ · grad_output on cleared/executed coordinates, exactly zero (bitwise) on
never-cleared coordinates. λ = PINNED_STRAIGHT_THROUGH_SCALE = 1.0, a module-level frozen
constant; no learned scale, no caller-configurable scale. This is the structural
generalization of Paper D's rank-one projection gauge Jacobian I − P (identity on the
constraint complement, zero on the gauge direction): identity on cleared coordinates, zero on
never-cleared coordinates, which are precisely the fiber directions U(τ) (Paper D's gauge =
the |U| = 1 special case). λ = 1.0 is inherited from Paper D's unit-Jacobian convention,
frozen before any training, not tunable.

### 5.2 Audit — perturb-and-MAP through-M, pinned noise

Forward = exact M applied to perturbed priority scores; scores are kernel-fixed frozen
functions of the raw flow (FIFO: −queue_position, stable descending argsort; random-unit:
depleting remaining quantity, per-draw argmax with unit depletion — the perturb-argmax
surrogate of probability-proportional-to-remaining draws). Noise = N(0,1) drawn up-front from a
seeded CPU torch.Generator; σ = PINNED_PERTURB_AND_MAP_SIGMA = 1.0 (one lattice unit of the
priority-score scale), frozen, not caller-configurable. Backward = unit-scale
selection-masked identity. Same seed → bitwise-identical allocations. On deterministic arms ST
is exactly the σ→0 limit of PAM (asserted at σ ∈ {1e-3, 1e-6, 1e-9, 0}), so a disagreement on
the audit cell measures the stochastic surrogate's smoothing at pinned σ, not a hyperparameter
gap. External grounding (D-2 map only): Perturb-Argmax/Softmax (arXiv:2406.02180) — the PAM
estimator is the queue/clearing analogue on kernel-fixed scores with an exact multi-unit
rationing forward; Minimizing Surrogate Losses for DFL (2025) — the LP/integer zero-gradient
obstruction making preregistered surrogates mandatory; "Do Differentiable Simulators Give
Better Policy Gradients?" (ICLR 2026) — estimator bias as the confound KT-A4 controls;
Gumbel-Softmax (2016) background only, not used.

### 5.3 Frozen constants and seed discipline

| Constant | Value | Rationale |
|---|---|---|
| PINNED_STRAIGHT_THROUGH_SCALE (λ) | 1.0 | unit Jacobian on cleared coordinates; Paper D I − P precedent |
| PINNED_PERTURB_AND_MAP_SIGMA (σ) | 1.0 | one lattice unit of the priority-score scale |
| Noise law | N(0,1) per score | standard normal on the score lattice; seeded CPU generator |
| PINNED_PERTURB_AND_MAP_SEED | 20260906 | fixture/replay default only; production seeds from the frozen RNG tree |
| Priority-score maps | kernel-fixed | frozen functions of the raw flow; not learned, not tuned |

Production seeds must come from the D0-frozen RNG tree (spawn(seed_root, ...) per C2), never
the module replay default; the run config carrying them is hashed before D0. Library+version
pin: torch CPU torch.Generator (frozen ecophys env), recorded in the run manifest. All
constants immutable after D0; any change is a new frozen, hash-recorded amendment (C13/C15).

### 5.4 KT-A4 two-estimator audit protocol (frozen)

Attack controlled: "through-M results are surrogate artifacts" (joint-highest kill
probability 0.30). Audit cell: retrain under PAM the increment-coordinate, through-M-train,
raw-infer cell (A10 / Y_increment,through-M,raw) on the D1 lab-asset block, L1 lineage, all 30
paired seeds 11000–11029 sharing data/init/train seeds and the training-time kernel stream
with the ST run — the only manipulated factor is the estimator. Everything else inherited
verbatim from contract v1: request-level CRN (C2), **K = 16 inference-kernel draws replayed per
cell** (the estimator-menu document's inherited-verbatim "K = 8" line is superseded by the C2
amendment — Annex C, C-1), endpoints (C5), SESOI (C6), 50,000-draw paired bootstrap (C1,
Annex B(a)), checkpoint hash-lock (C11; the audit's 30 checkpoints are inside the G4 total of
450, Section 3.4), one-shot analyzers (C13), record coverage (C14: +30 trainings, +7,680
evaluation records). Compute: inside the D1_07 envelope; [AUTH] at D0.

### 5.5 Instability criteria, downgrade, and collapse (frozen, mechanical)

The audit fires the downgrade iff (1) sign-pattern instability: any preregistered attribution
contrast (J, φ_train, φ_infer, or D-contrasts involving the retrained cell) flips sign across
the Holm-corrected significance bands between ST-trained and PAM-trained versions
(within-band sign differences reported but do not fire); or (2) ordered-classification
instability: any affected cell or contrast changes class across the SESOI band. Both criteria
mechanical; the comparison is outside all Holm families (a preregistered robustness gate, not a
confirmatory estimator-superiority test). Downgrade if fired: estimator-conditional reporting,
both estimators' values shown side by side, no pooled or ST-only claim for any estimand
touching the retrained coordinate; raw-train cells unaffected (no estimator). **If both
estimators fail the fixture competence gate (the 20-test suite) at any point before or during
the campaign: the through-M arms lose their forward-exactness premise, the cube collapses to
surgery-only (below the D-1 bar) and the campaign STOPs pending PI decision.** No repair,
re-tuning of λ/σ, or estimator substitution post-D0.

---

## 6. Parent-reduction and template-expressibility packet (KT-M2; appendix table)

### 6.1 The parent template (as adjudicated; no new claims)

Duruisseaux et al. 2024 (ICML AI4Sci WS; D-2 map §2.2 adjudication-table row, OpenReview
Zvxm14Rd1F; panel ruling recorded at map §2.4 V1): four arms on an FNO surrogate for PDE
operator learning — baseline G; G trained with the projection; and the locked-checkpoint
inference-only surgery cell; continuous Fourier/Leray projection layer; estimand
constraint-satisfaction / L2 fidelity, 5 seeds. Ruling: external genre parent, must be cited;
"first train x inference constraint crossing" phrasing permanently falsified; novelty scoped
to (i) the market-native combinatorial/integer clearing layer M and (ii) the SESOI-graded
path-dependence attribution estimand.

### 6.2 Rows = template-inexpressible features of the merged design

- **R1. Competing-mechanism swap at fixed truth reference.** allocation_rule exchange
  (fifo → random_unit) inside one engine, DGP truth tapes unchanged (C4 kernel-swap axis;
  truth reference stays the original FIFO tape). The parent template has exactly one mechanism
  (a projection of the same physics); no slot for exchanging one clearing mechanism for a
  different one at fixed truth.
- **R2. Kernel x enforcement interaction measured on OOD axes.** The train x infer enforcement
  factorial crossed with population-2N / tick-2Δ / truncation stress axes as confirmatory
  interaction estimands (C3 J, C4 axes, C9 families). No OOD factor in the template.
- **R3. Fiber-resampling control.** Dual-hash-validated without-replacement interleaving
  regeneration holding the aggregate tape fixed (Section 7.1); requires a stochastic kernel
  whose draws admit within-fiber regeneration; the template's layer is deterministic
  projection.
- **R4. Dual-lineage architecture-transfer gate (C9).** Two independent simulator lineages
  through the same 8-cell grid with a preregistered ≥ 8/16-material gate and boundary
  reporting; the template is single-architecture, 5 seeds.
- **R5. Preregistered point-null / exact-zero pattern cells.** O-B swap→fifo exact-zero point
  null (integer-exact, Section 4.4); O-D price-notional exact-zero preregistered null on ru
  splits; KT-A1 P1/P2/P3 attribution patterns inexpressible as scalar comparisons. The
  template's estimand has no point-null, equivalence-test, or pattern-class slot.

### 6.3 Expressibility table (cells: OWNS / DNO = does-not-own; every reason restates a
D-2 evidence-map row, per-cell map locator in parentheses)

**Column provenance note (pinned at v2, panel R3-3).** The v1 column "Dyer et al. ICAIF 2023"
is REPLACED by **Nagy et al. (2023, ICAIF)** — the actually adjudicated feasibility-anchor row
of D-2 map §2.2 ("Generative AI for End-to-end LOB Modelling / Nagy et al. (2023, ICAIF) |
adjacent | low | feasibility anchor; M never an experimental factor"). The v1 Dyer column's
cell reasons were verbatim restatements of that Nagy row, and "Dyer" traces only to the D-3
framing document and the D-1 session record — never to a D-2 map row — so under the
citation-source rule of Section 1.1 the column was mis-attributed. Dyer is removed from
References. All other columns restate map §2.2 rows directly (locators below); the
matching-engine ABM (2021) pointer rests on map §2.5 (cleared-but-instructive list) and the
map's citation condition 4, recorded here as its locator.

| Inexpressible feature | Duruisseaux 2024 (map §2.2) | Solver-in-the-Loop 2020 (map §2.2) | GradABM (Chopra 2023) (map §2.2) | Nagy et al. ICAIF 2023 (map §2.2) | Gen-DFL 2025 (map §2.2) | MarS 2024 (map §2.2) | M3 2026 (map §2.2) | KineticSim 2026 (map §2.2) / matching-ABM 2021 (map §2.5) |
|---|---|---|---|---|---|---|---|---|
| **R1 competing-mechanism swap at fixed truth** | DNO — layer is continuous Fourier/Leray projection of the same physics; no second mechanism exists to swap | DNO — training-face only; inference always through solver, never swapped | DNO — epi feasibility; no cube | DNO — feasibility anchor; M never an experimental factor | DNO — no mechanism layer; decision-robustness estimand | DNO — production raw-train/through-M-infer cell; never crossed | DNO — anchor mismatch documented; engine never removed | DNO — M as fixed infrastructure, nothing trained/swapped |
| **R2 kernel x enforcement on OOD axes** | DNO — no OOD factor; constraint/L2 estimand, 5 seeds | DNO — single face, no factorial | DNO — no cube | DNO — M never a factor | DNO — no enforcement axis | DNO — single production cell, no axes | DNO — engine never off, no FIFO to swap | DNO — no trained model to cross |
| **R3 fiber-resampling control (dual-hash regeneration)** | DNO — deterministic projection layer; no draws to regenerate | DNO — no stochastic kernel | DNO — no kernel/fiber object | DNO — no kernel/fiber object | DNO — no kernel/fiber object | DNO — pre-mechanism likelihood, engine downstream; no draw-level control | DNO — order-level likelihood; no mechanism in loss, no fiber | DNO — M is infrastructure; KineticSim's bitwise-identical books support swap well-definedness only |
| **R4 dual-lineage transfer gate (C9)** | DNO — single FNO lineage, 5 seeds | DNO — single lineage | DNO — single lineage | DNO — single model | DNO — no lineage axis | DNO — single system | DNO — single foundation model | DNO — nothing trained |
| **R5 point-null / exact-zero pattern cells** | DNO — constraint-satisfaction/L2 fidelity; no point-null or pattern slot | DNO — solver-fidelity comparisons | DNO — feasibility, no null machinery | DNO — feasibility anchor; no estimand machinery | DNO — decision-robustness estimand | DNO — production objectives, no preregistered nulls | DNO — likelihood anchor, no equivalence tests | DNO — no estimand machinery at all |

### 6.4 What the template DOES own (recorded, never claimed by us)

The four-arm train x infer constraint-enforcement factorial including the locked-checkpoint
inference-only surgery cell (Duruisseaux 2024); the training face (Solver-in-the-Loop 2020);
the production (raw-train, through-M-infer) default cell (MarS 2024; Nagy 2023; MarketGPT 2024;
TABL-ABM 2025; TradeFM 2026); M-infrastructure prior art (matching-engine ABM 2021; KineticSim
2026). Paper D remains the internal parent for the cube and the statistical contract — cited,
never double-counted.

**Deliberate exclusion (honesty item).** Plain "surgery cells on locked checkpoints with zero
optimizer steps" is NOT an inexpressible row: the panel's verbatim evidence assigns the
locked-checkpoint inference-only surgery cell to the parent template. The inexpressible part of
our surgery cells is the mechanism-identity crossing (swapping the clearing kernel, not a
projection of the same physics), which is row R1. The prereg table shows the surgery template
as parent-owned with R1 as the delta.

### 6.5 Confirmation vehicles and discharge linkage (preregistered)

| Row | Post-D0 confirmation vehicle | Discharges |
|---|---|---|
| R1 | KT-A2 stage-2 identical-input replay (same prestate + request subsequence, only allocation_rule swapped; Lemma C constant 1 − Q(c^F) preregistered per fixture) + KT-A3 swap contrast on locked checkpoints | KT-A2, KT-A3 |
| R2 | Mandatory-family interaction J on OOD axes at h ∈ {1,4,16,31} (C9; EP1 primary cell B1 kernel-swap h16) | KT-A1 (P2 pure-interaction pattern), KT-A3 |
| R3 | KT-A3 resample arm (swap > δ AND resample < δ/10, dual-hash acceptance; seed-mean + draw-noise guard, Section 4.4) + KT-M1 deployment experiment | KT-A3, KT-M1 |
| R4 | C9 transfer gate on block B3 (both outcomes reported; failure = boundary) | KT-A5 |
| R5 | O-B swap→fifo exact-zero point null and O-D exact-zero null cell; KT-A1 P1/P2/P3 frozen decision rule (restated inline in Annex B(h)) | KT-A1, KT-A3 |

One confirmation discharges KT-A1/A3/M1 simultaneously (correlated by design; forecasts must
not multiply them independently). Wording rule (never violated): the cube is never phrased as
"first train x inference constraint crossing"; R1 is phrased as "competing-mechanism exchange
at fixed truth reference — template-inexpressible," with the surgery template itself attributed
to the parent.

---

## 7. Instruments (built, hashed, frozen)

### 7.1 Dual-hash fiber resampler (D1_02) — `scripts/lab_asset/fiber_resampler.py` (881 lines)

Engine-driven regeneration of without-replacement interleavings holding the aggregate tape
fixed; acceptance = identical aggregate_state_hash sequence AND differing state_hash chain,
with native RNG-state accounting so that state-chain equality coincides with
allocation-trajectory equality. MVHG exact-law conformance at three levels (exact enumeration,
conditioned engine law, seeded MC over all attempts: p ∈ [0.29, 0.88]); acceptance rate =
1 − P_engine(original trajectory) exactly as predicted (vstar1 ≈ 71.4%, vstar2 ≈ 93.4% —
rejections are correct trajectory-clone refusals, not failures); deterministic kernels and
single-order pools correctly admit NO accepted resample (the KT-A3 control). 40 tests + 1
by-design strict xfail (`tests/test_fiber_resampler.py`). **Criterion-(ii) semantics RATIFIED
by PI ruling D1_12 ("批准"): native-RNG-state-preservation.** The literal raw-hash reading
(which would count rng-state-only differences as variation, making fifo/single-order pools
trivially accepted and destroying the KT-A3 control) is REJECTED. The frozen prereg statement
in the module (sha256 `703ca36e...2c4b`, hash-pinned in the test) stands as written. Seed
namespace 20260973. Without this instrument the merged hostile-T0 lower bound would be ≈ 0.10,
below the 0.15 activation floor (Section 9); the dependency is now discharged by construction.

### 7.2 Fixture enrichment (D1_03) — `experiments/lab_asset_a2/enrichment_20260906/`

10 new engine-generated fixtures: 5 arm-consistent kernel-swap pairs on the S3 scaffold
(q_P = (5,4,3,2), two better levels, two deeper orders), V* ∈ {1,2,4,6} + exhaustion episode,
clock-straddling never-drawn sets at every interior rung; backward-compatible lab-asset-v3.1
schema extension (arrival_clocks as pre-session prestate metadata, deliberately excluded from
prestate_hash — clocks live in the raw flow, exactly the F_exec point); enrichment_manifest.json
(per-file sha256; parent lineage = the frozen bundle manifest
`fea8a136b0c3e19a00bddcb131a1540ca40fda6c1576dbc949001dbf76a9581c`; supports
flags); generator + config (master seed 20260972, documented deterministic search); byte-exact
regeneration proven. Conformance (frozen wording, panel A.5): enriched fixtures pass **13 of
the 27 frozen conformance tests (the scenario-applicable subset); the other 14 are
own-scenario and remain green in the frozen suite** — `tests/test_lab_asset_enrichment_conformance.py`
green; manifest verification + replay determinism + frozen-bundle read-only guard included.
The frozen `a2_exit_20260905` bundle is NEVER mutated. Honest caveats: V*-ladder never-drawn
realizations are seed-frozen facts, not laws; ru tapes realize ONE draw sequence per episode
(law-level work uses the resampler/enumeration); no rejection/latency-choice/crossing-replace
events by design.

### 7.3 K-variance preflight (D1_06) — `experiments/reexploration/k_preflight_20260906/`

32 seeds x 6 episodes x 2 arms x 16 nested draw replays (192 episodes, 6,144 engine
evaluations, ~24 s CPU); M0-policy-class calibration generator (master seeds 31000–31031 within
the reserved namespace 31000–31099, disjoint from all training/Paper-D/D2 ranges); 4
stream-null + 5 draw-dependent DGP-native statistics; variance identity B(K) = V_between + W/K
with seeded bootstrap CIs; 6 engine-grounded invariants zero-failure (incl. FIFO
payload-projection identity and request-boundary aggregate-hash identity across both arms and
all replays); byte-identical determinism, results sha256 `f61e410c…` (full:
`f61e410cd59c37b5624504a3cdf057c701b4b682067f948d2f8528ace018c2d4`). Outcome: conservative
rule `none_in_set` → K = 16 with the alloc_proprata_dev_mean insufficiency flag (Section 3.2);
PI ruling D1_11 froze K = 16. Honest caveats (all carried): the preflight bounds only the
DGP-side draw-replay component (training noise invisible); between-seed variance is
calibration-generator design variance — the E-2 preflight re-run (C2(e) as rewritten) covers
the D0 generator; CRN direction conservative; training-time kernel stream out of scope; FIFO
arm exactly draw-invariant (verified), so K > 1 on deterministic cells buys only the G8
byte-identity gate.

### 7.4 Hash and namespace inventory (frozen or to-be-frozen)

| Item | Value |
|---|---|
| Frozen A-2 bundle manifest (canonical, full 64-hex) | `fea8a136b0c3e19a00bddcb131a1540ca40fda6c1576dbc949001dbf76a9581c` (read-only, never mutated; Annex C-4 typo inventory) |
| Fiber-resampler prereg statement | sha256 `703ca36e...2c4b` (hash-pinned in test) |
| K-preflight results | sha256 `f61e410cd59c37b5624504a3cdf057c701b4b682067f948d2f8528ace018c2d4` |
| Enrichment master seed | 20260972 |
| Resampler seed namespace | 20260973 |
| S3 robustness-arm seeds (pinned v2, Annex B(c)) | 20260974, 20260975, 20260976 |
| K-preflight namespace | 31000–31099 (masters 31000–31031) |
| Training seed namespaces | 11000–11029 (B1/B2), 12000–12029 (B3/B4) — D1_10; Stage-2 subsets 11000–11014 / 12000–12014 |
| Reflexive + telemetry 10-seed subsets (Annex B(d)) | 11000–11009, 12000–12009 |
| Bootstrap seed derivation (Annex B(a)) | sha256 over frozen strings (block, family); mod 2^63 |
| Estimator module defaults | λ = 1.0, σ = 1.0, PAM default seed 20260906 (fixture/replay only) |
| D0 archive layout | r2://ecophys/alpha_cube_d0_20260919/ (immutable staging; byte-exact re-derivation on both nodes) |
| D0 freeze hash + timestamp | [TO BE PINNED AT D0 — the only two such items in this document] |

---

## 8. Deliberate nonclaims, de-scope ladder, and inherited stop rules

### 8.1 Deliberate nonclaims (verbatim from the plan; nothing here may be claimed)

No first train x infer crossing. No bare positive-dimensional-fiber novelty (DPIOT). No
constrained-is-better superiority (the estimand is attribution, never superiority). No T4
theorem; drift measurements permanently exploratory. No quotient/gauge repair claim. No
real-market mechanism-identification or performance claims (the bridge is qualification-only;
crash reserves untouched). No cross-market or universal-scaling claims. No post-freeze schema,
prediction, threshold or cell-set change; no analyzer reruns; no H20; no outcome-dependent
analysis of any kind.

### 8.2 De-scope ladder and never-cut list (frozen)

Shrink ladder: slip > 5 days → Stage 2 variant A only at 12 seeds; slip > D0+26d or cumulative
burn > 1,150 V100-h → cancel Stage 2, forfeit the robustness leg as a reported deviation
(theorems unaffected). Cuts and what each forfeits: D2 deferred/canceled → robustness-truth
leg forfeited, experimental section scoped to lab-asset-v3 single family, "two DGPs" reported
as deviation; T1/T2/T3 unaffected. L2 drops trunc_cap / pop_4x → lineage-consistency of the
truncation-depth direction and L2 population dose-response forfeited (T3 truncation evidence
still carried by L1 both directions). Stage 2 at 15 seeds → directional-replication block
only, no material-nonadditivity claims. Variant B L2-only → forfeits the L1 x second-variant
cross. Reflexive exploratory-only → no confirmatory loss by design. **Never cut:** the 8-cell
cube x 30 seeds on D1 both lineages (core estimand = path-dependence attribution); kswap and
both truncation conditions on L1 (T2/T3 bridges); the surgery cells (T2 within-fiber
evidence); all-cells/all-axes/all-lineages reporting incl. class flips and nulls.

### 8.3 STOP-class rules (verbatim rows of the inherited 22-item risk register, condensed
presentation; the full register in the experiment plan §12 is incorporated by reference
WITHOUT EXCEPTION and without weakening — panel R3-7; line halts, PI informed, no narrative
repair)

| Trigger | Rule |
|---|---|
| Engine-law mismatch (S3: no V* = 2 rank jump; kernel-dependent agg rank; pu ≠ po) | STOP — pool scale never identified; T1's unique identifying cell dies; new truth engine required before any GAMMA claim survives |
| S1a structure-lemma falsification (injected fifo excess or ru splits change any F_exec field) | STOP — engine records finer than the schema-static analysis; no cube-level result can rescue it |
| Corpus-contract reversal (F_full frozen instead of F_exec) | STOP — fibers collapse; T2/T3 lose ambiguous sets; paper reduces to abstract T1 |
| M0/M1-lumpable freeze impossible (request streams irreducibly allocation-identity-dependent) | STOP — exact request-level CRN impossible; paired-seed premise collapses |
| Byte-exact replay failure across nodes | STOP — CRN unverifiable; G6/G8/G9 unpassable |
| Reference degeneracy in all four strata (mean R00 < 1.0 scaled unit) | STOP — SESOI inoperative; no post-hoc metric substitution under the one-shot rule |
| Convergence-failure halt (> 15% nonfinite on any mandatory cell after resume, or > 3/30 seeds lost) | STOP + PI — mandatory halt for PI decision; never silent seed substitution |
| Outcome-access breach (any metric inspected before both workers complete) | STOP, NO REPAIR — voids the outcome-blind freeze and the preregistration chain |
| Disk/compute prerequisite failure (nodes not ≥ 40% free, or capacity cut) | STOP — launch blocked, not descoped ad hoc |
| Hostile-T0 calibration failure (ledger lower bound < 0.15) | STOP, PRE-GPU — activation fails at D-1 with zero GPU spent |
| Prior-art reopen (post-freeze work stating mechanism-fiber training non-identification or train-through ablation) | STOP/REPOSITION — direct collision; reposition before D0 |
| Post-freeze edit breach (any change after D0, or analyzer rerun without PI memo) | STOP, NO REPAIR — preregistration integrity fails |
| Both estimators fail the fixture competence gate (Section 5.5) | STOP — cube collapses to surgery-only (below D-1 bar); PI decision |
| **Outcome-triggered Stage-2 launch (any Stage-2 entry decision that consumed a Stage-1 outcome)** | **STOP-class protective clause (restored at v2, panel R3-7): the D2 block is downgraded to exploratory or forbidden entirely; the breach is reported as a preregistration-integrity deviation** |

REFRAME-class (recorded, claim repositioned with recorded deviation): KT-G1 R2 failure
(demote T1 to scoped proposition); KT-G2 separation failure (T2 as risk characterization; if
T1 also loses its dichotomy trace — O-D inverted, exact-zero null rejected — STOP); KT-A1 kill
pattern (|I| ≤ δ/2 everywhere, no sign opposition, surgery antisymmetric → ALPHA is an ablation;
paper rests on GAMMA + boundary report); **KT-A5 portability-kill REFRAME (restored at v2,
panel R3-7): no lineage x DGP combination shows an attribution-only pattern → ALPHA is an
ablation; the paper rests on GAMMA + the boundary report**; KT-A4 estimator instability
(estimator-conditional reporting, both shown); KT-M1 gauge-twin null (fiber behaves like
internal gauge; empirical bridge severed; program survives as GAMMA theory; V4 final sentence
rewritten as boundary); through-M surrogate non-convergence (cells classify unresolved, never
dropped). BOUNDARY-class: L2 transfer-gate failure (architecture boundary per the U-Net
lesson; claims scoped L1; never pooled, never hidden). CONTAINED: reflexive-cell leak voids
only that exploratory subsection.

---

## 9. Forecast-ledger cross-reference (verbatim resolution rules)

Target `t0_activation_eligibility`, floor 0.15, point scoring brier; entries in v1 schema with
basis_evidence_refs appended to `research/discovery/forecast_ledger.yaml` before D0.

- **`d1_gamma_theorem_structure_survival`** — lower 0.55 / point 0.75 / upper 0.88.
  Resolution rule (verbatim): "true iff none of KT-G1..G5 forces demotion of T1/T2/T3 below
  lead-theorem status (re-scoping with the obstruction lemmas intact counts as survival; T1
  demotion to scoped proposition counts as false)."
- **`d1_alpha_attribution_estimand_survival`** — lower 0.18 / point 0.35 / upper 0.55.
  Resolution rule (verbatim): "true iff at least one of P1/P2/P3 confirms under the frozen
  KT-A1 rule with KT-A4 estimator stability holding; false iff the kill pattern obtains or
  estimator instability forces the conditional downgrade." **The frozen KT-A1 rule is restated
  inline in Annex B(h)** so the resolution does not depend on a level-4 companion.
- **`d1_merged_gammas_led_paper_gate`** — lower 0.18 / point 0.34 / upper 0.55.
  Resolution rule (verbatim): "true iff GAMMA structure survives AND at least one
  template-inexpressible pattern class confirms (KT-M2). Clears the 0.15 activation floor with
  thin margin; the margin is carried almost entirely by the ALPHA estimand, not the theorems.
  If the fiber resampler is not authorized, this forecast drops to lower ≈ 0.10 (below floor)
  because KT-A3/KT-M1 contrasts become unrunnable — flag this dependency in the ledger
  resolution_rule." Status of that dependency at authoring: DISCHARGED — the resampler is
  authorized (D1_02), built, tested, and its criterion-(ii) semantics ratified (D1_12); the
  ledger entry must record the dependency as resolved-by-instrument, not silently dropped.
- Floor-exempt components: L2 transfer 0.25/0.45/0.65; EP1 material 0.30/0.50/0.70; bridge
  qualification 0.55/0.75/0.90.

Per-test kill probabilities (correlated; never multiplied independently — KT-A1/A3/M1/M2
share the same underlying grid; KT-G1/G4 share the T1 statement): KT-G1 0.20, KT-G2 0.15,
KT-G3 0.05, KT-G4 0.10, KT-G5 0.20, KT-A1 0.30, KT-A2 0.05, KT-A3 0.25, KT-A4 0.30, KT-A5
0.20 (two-lineage claim only), KT-M1 0.20, KT-M2 0.30. Theory-level attacks KT-G1..G5 and
KT-A2 stage-1 are discharged at theorem level (D-1 session record §5); their residual mass
lives in the post-D0 empirical branches (S3 machine-check, S1a gates, stage-2 replays).

---

## 10. Deviation ledger pointer and amendment provenance chain

### 10.1 Deviation/amendment ledger

The generated, non-omissible C16 ledger (contract v1, as amended at v2) carries items
(1)–(16) as restated in Section 3.2. Items ratified at v2 (panel R1-5/R3-1): (13) the
two-stage execution amendment (PI decision D1_04; Stage-2 seed subsets and family status
pinned); (14) the truncation-condition secondary Holm family with corrected itemized
membership; (15) the C14 restatement of Section 3.4; (16) the C9 transfer-gate primary
reference disambiguation. The experiment plan §4 recorded the two-stage and truncation items
as C16 (11)–(12) "to be recorded"; the frozen contract's (11)–(12) were taken by the K = 16
and kernel-set amendments, leaving the two-stage and truncation amendments
authorized-but-unrecorded — a ledger completeness gap, not a design change, now closed by
items (13)–(14). With (15)–(16) the ledger is complete against every authorized amendment as
of the v2 freeze candidate.

### 10.2 Amendment provenance chain (full)

1. PI blanket authorization `pi_reexploration_d1_authorization_20260906` ("全部授权", 2026-09-06):
   D1_01 freeze F_exec corpus contract; D1_02 dual-hash fiber resampler before D0; D1_03
   fixture enrichment as schema-extension (frozen bundle never mutated); D1_04 two-stage
   amendment; D1_05 Stage-2 synthetic members; D1_06 K-variance preflight (scope-bounded
   CPU-only); D1_07 estimator menu + audit retrain inside envelope [AUTH at D0]; D1_08 calendar
   + adversarial 3-reviewer panel; D1_09 node cleanup at D0; D1_10 seed namespaces. Explicit
   bounds: no GPU before D0 freeze; no confirmatory execution; no market data; verification-
   liquidity holdout sealed until 2026-10-17 UTC; Paper D terminal; no topic-card creation.
2. Addendum `D1_ADD_session1_followup_20260906` ("用需要算力多的那个，批准，确认，确认"):
   D1_11 K = 16 frozen (window closed, immutable); D1_12 resampler criterion-(ii)
   native-RNG-state-preservation semantics ratified, literal reading rejected, module statement
   sha256 `703ca36e...2c4b` stands; D1_13 L2 build scope confirmed as code-only pre-D0 build
   (CPU smoke validation only; GPU training stays D0-gated); D1_14 C3 kernel sentence tightened
   (pro_rata not an engine kernel).
3. Preregistration v1 (2026-09-06) — pre-panel draft.
4. Adversarial 3-reviewer panel (D1_08, 2026-09-06) — three major_revision verdicts, 28
   issues; full verdicts and per-issue dispositions in
   `papers/proposal/ecomd_reexploration_prereg_panel_response_2026-09-06.md`.
5. This preregistration v2 (2026-09-06) — post-panel freeze candidate; incorporates all 28
   panel dispositions; records the v2 pre-freeze restatements (C)–(F) of Section 3.1 into the
   contract's amendment banner; D0 freeze sha256 [TO BE PINNED AT D0].

---

## ANNEX A — Panel items from v1, resolved (record of disposition)

1. **C14 restatement** — RESOLVED: Section 3.4 (C16 item (15)); adjudication of the Stage-2
   count conflict recorded (92,160).
2. **C16 ledger completeness** — RESOLVED: items (13)–(16) ratified (Section 10.1).
3. **C9 transfer-gate "primary J" reference** — RESOLVED: B3's own primary-analogue cell
   (C16 item (16)).
4. **Seed namespaces** — RESOLVED: D1_10 namespaces govern; Stage-2 subsets pinned
   (11000–11014 / 12000–12014).
5. **Conformance wording** — RESOLVED: frozen wording in Section 7.2 ("13 of 27
   scenario-applicable; other 14 own-scenario and green in the frozen suite").
6. **Namespace-collision check** — RESOLVED: folded into gate G2 as a namespace-disjointness
   sub-check (Section 3.3); no thirteenth gate, no naming collision.
7. **L1-4 RNG fix dependency** — UNCHANGED PRE-FREEZE BLOCKER for the PI: must land before
   D0; L2 compute anchors unmeasured until the D1_13 build's CPU smoke lands. Both are PI
   checklist items at the v2 review, not v2-text items.
8. **Lumpability vocabulary** — RESOLVED: kept out of theorem names ("aggregate-sufficiency
   obstruction"); needs-verify flag in Section 2.8.
9. **Estimator-menu audit cell under K = 16** — RESOLVED: superseded-line flag Annex C-1;
   K = 16 governs the audit cell (Section 5.4).
10. **D0 date** — RESOLVED: pinned 2026-09-19 (Section 1.2); "by the panel at D0" phrasing
    removed everywhere.

## ANNEX B — Consolidated pinning table (panel R1-7; every formerly analyst-choosable degree
of freedom pinned in this frozen text)

| # | Item | Pinned value / rule (single branch, no analyst choice) |
|---|---|---|
| (a) | C8 bootstrap RNG seed | per (block, family): int(sha256("ecomd_reexploration_v2_bootstrap" ‖ block_id ‖ family_id), 16) mod 2^63; deterministic from frozen strings; independent of training seeds; recorded in analyzer manifest |
| (b) | G9 5% replay sample | deterministic stride: lexicographic sort of record keys within each record class; every 20th record from index 0; exactly 5%; no RNG |
| (c) | S3 robustness-arm seeds (EP3) | 20260974, 20260975, 20260976 — next three free integers of the reserved 2026097x instrument block (after 20260972 enrichment, 20260973 resampler), allocated in rung order; disjointness enforced by gate G2 sub-check |
| (d) | Reflexive + T4-telemetry 10-seed subsets | first 10 seeds of each namespace: 11000–11009 (B1-side), 12000–12009 (B3-side) |
| (e) | s_ch provenance | single branch: hash-sealed DGP-only sample (DGP-truth side only; D0-hash-committed generator sample; never simulator output; never the paired corpus) |
| (f) | Theory-appendix S1a acceptance gates | renamed S1a-G1, S1a-G2, S1a-G3 (EP4); the analyzer gates G1–G12 are the only "G"-numbered gates |
| (g) | Classification label → analyzer macro mapping | "material non-additivity" → `class_material_nonadditivity`; "smaller statistical non-additivity" → `class_smaller_stat_nonadditivity`; "practical additivity" → `class_practical_additivity`; "unresolved" → `class_unresolved`; "unresolved (reference-degenerate)" → `class_unresolved_ref_degenerate`; "unresolved (draw-noise-dominated)" → `class_unresolved_draw_noise_dominated` (Section 4.4); "not run" → `class_not_run` |
| (h) | KT-A1 P1/P2/P3 frozen decision rule (restated inline from killer-tests L43) | **P1** = opposing-sign training/inference enforcement credits (T-contrast and E-contrast signs oppose); **P2** = pure interaction (J material with both main-effect contrasts non-material); **P3** = surgery hysteresis on locked checkpoints (surgery cells diverge across deployment maps while parents are training-loss-identical). Kill pattern: \|I\| ≤ δ/2 everywhere, no sign opposition, surgery antisymmetric → ALPHA is an ablation (REFRAME, Section 8.3) |
| (i) | Freeze mechanics | Section 1.3 (agent, hash inputs, recording order, known-typo policy) |
| (j) | Freeze date | 2026-09-19 (Section 1.2) |

Provenance note (honesty): (a)–(d) are convention constants — deterministic rules chosen at
v2 because the panel ruled that v2 is the hashed text and no such choice may remain open; they
follow pre-existing repo conventions (reserved instrument block, first-k-of-namespace) and are
PI-ratifiable at the v2 review before the D0 hash; none is an empirical quantity and none
depends on any outcome.

## ANNEX C — Superseded-wording errata register (known-stale lines inside incorporated
companions; audit hazards recorded so string-matching reconciliation succeeds; none edited
pre-freeze per Section 1.3(4))

- **C-1** Estimator menu, audit-protocol section: "K = 8" — superseded by C2 amendment
  (K = 16; PI D1_11). Section 5.4 is authoritative.
- **C-2** Ops document seed convention "1000–1029 / 2000–2014" — superseded by D1_10
  (11000–11029 / 12000–12029; Stage-2 subsets 11000–11014 / 12000–12014).
- **C-3** Ops document and killer-tests document: "Holm across the 8 mandatory cells" (two
  occurrences) — superseded by C9's 16-cell mandatory family per block (4 axes × 4 horizons).
- **C-4** Bundle-anchor typo `fea8b136...9581c`, five lines across four companions
  (estimator menu §3; simulator contracts §2.6 and §5B; kt_a2/kt_m2 writeup header; killer-
  tests L23) — canonical value:
  `fea8a136b0c3e19a00bddcb131a1540ca40fda6c1576dbc949001dbf76a9581c`
  (Section 1.1). Killer-tests L184 prints the correct value; that document is internally
  contradictory exactly as listed here.
- **C-5** Contract Part 2 §2a.6: "reverse swap and pro_rata swaps are exploratory" —
  superseded by D1_14 + panel R3-2: reverse swap executable exploratory; pro_rata S3
  exact-arithmetic only, never executes (Section 4.7).
- **C-6** Contract C14 printed "122,880 (30 x 8 x 4 x 4 x 8 per block x 4 blocks)" and
  "240 training records" / "480 probes" without two-stage splits — superseded by the v2
  Section 3.4 restatement (C16 item (15)): 299,520 / 450 / 420.
- **C-7** Contract C2(e) original re-run clause ("must be re-run ... before freezing K") —
  superseded by the rewritten C2(e) (Section 3.2): E-2 preflight pre-D0, caveat-only, K
  immutable, material insufficiency = STOP-class PI decision item.
- **C-8** Contract C9 original "primary J" — superseded by C16 item (16) (B3's own
  primary-analogue cell).
- **C-9** Plan §4 (synthesis rulings): "truncation ... 3 tests/block" — superseded by C16
  item (14)'s itemized membership (2 tests per L1 block, 1 per L2 block; recorded reason).
- **C-10** Prereg v1 §2.2 G2-1 "sequence 6/7" wording — superseded by the v2 §2.2 wording
  (fifo SEQUENCE 7 = random_unit SEQUENCE 8, hash roles and boundary convention pinned).
- **C-11** v2 §2.6 V4 citation clause and v2 References: "conservation-law weight structure in
  Neural Mechanics (ICLR 2020)" — mischaracterization and wrong year against the verified
  publication record (Kunin, Sagastuy-Brena, Ganguli, Yamins, Tanaka, "Neural Mechanics:
  Symmetry and Broken Conservation Laws in Deep Learning Dynamics", ICLR 2021,
  arXiv:2012.04728): the work derives conservation laws of the training dynamics from
  architectural symmetry and studies their breaking; it does not build a conservation-law
  structure into the weights. Both sites corrected 2026-09-08 as a PI-approved pre-freeze
  erratum (verification evidence: arXiv abs page, 2026-09-07 bibliographic round; manuscript
  V4 citation clause corrected in step on 2026-09-07). No theorem statement, condition,
  constant, or ruling is affected; the V4 lemma argument is untouched.

---

## References (ALL from the D-2 evidence map adjudication; no other source is cited as fact)

DPIOT (ICML 2022); Perturb-Argmax/Softmax statistical representation properties (Cohen
Indelman & Hazan, 2024, arXiv:2406.02180); Diaconis & Sturmfels (1998); contingency-table
fibers (2014); Duruisseaux et al. (2024, ICML AI4Sci WS, OpenReview Zvxm14Rd1F);
Solver-in-the-Loop (2020, NeurIPS) — title-only form as adjudicated in D-2 map §2
(the v1 author enrichment "Um et al." could not be verified against the publication record
before freeze and is withdrawn; map-faithful form governs; panel R3-10); GradABM (Chopra
et al., AAMAS 2023); **Nagy et al. (2023, ICAIF) — "Generative AI for End-to-end LOB
Modelling", D-2 map §2.2 adjudicated row (replaces the v1 Dyer column, Section 6.3)**;
Gen-DFL (2025); MarS (2024, ICLR 2025); M3 State-Event Foundation Model (2026); KineticSim
(2026); matching-engine ABM (2021) (map §2.5 + citation condition 4); Quotient-Space Diffusion
Models (ICLR 2026); Neural Mechanics (ICLR 2021); Soudry et al. (2017); "The Loss Does Not See
the Basis but Adam Does" (2026); "Do Differentiable Simulators Give Better Policy Gradients?"
(ICLR 2026; "Onoda ICLR 2026" in D-1 documents); Minimizing Surrogate Losses for DFL (2025);
Gumbel-Softmax (2016); Do LLMs Understand LOB Dynamics (2026); Counterfactual Operator
Relevance (2025); TRADES (2025); DEX closed-loop (2026); Paper D (internal parent,
`papers/paper_d_constraints/`). Needs-verify items (vocabulary only, never cited as fact):
Markov-lumpability literature. Deliberately excluded: Le Cam two-point lineage (inline TV
triangle proof); maximal-atom/log-concavity lattice bounds; **Dyer et al. (ICAIF 2023) —
removed at v2 (never a D-2 map row; Section 6.3 provenance note)**.

---

*Provenance: authored by the preregistration-reviser agent of the D-1/D0-prep workflow (session
task record; branch paper-d-iclr-2027-completion), incorporating all 28 dispositions of the
adversarial 3-reviewer panel of 2026-09-06, grounded in the companion documents listed in
Section 1.4, all read in full. Zero GPU, zero market data, zero confirmatory endpoints, zero
outcome access; the frozen A-2 bundle consumed strictly read-only.*
