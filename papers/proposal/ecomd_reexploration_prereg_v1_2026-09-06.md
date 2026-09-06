---
document: Preregistration draft v1 (pre-panel) — merged GAMMA-led reexploration paper
repo_path: papers/proposal/ecomd_reexploration_prereg_v1_2026-09-06.md
authored: 2026-09-06
stage: D_minus_1_execution_authorized_prep_d0 (decision pi_reexploration_d1_authorization_20260906)
status: v1 DRAFT — goes to the adversarial 3-reviewer panel (D1_08) before v2 and the D0 freeze
freeze_policy: sha256-frozen at D0 (~2026-09-19; exact date [TO BE PINNED AT D0] by the panel)
outcome_access_at_authoring: none — no confirmatory endpoint measured, no GPU used, no market
  data accessed; the frozen A-2 bundle was consumed strictly read-only
---

# Preregistration v1 — Merged GAMMA-Led Reexploration Paper (EcoMD x lab-asset-v3 ALPHA cube)

This is the single authoritative document for every confirmatory decision downstream of the D0
freeze. All companion documents are incorporated by reference with absolute paths; where any
companion conflicts with this prereg, this prereg governs for science and the frozen statistical
contract governs for statistics (precedence: Section 1.4).

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
(`experiments/lab_asset_a2/a2_exit_20260905/`, bundle manifest `fea8a136...9581c`, 27 conformance
tests + replay validator, read-only, never mutated) with the authorized lab-asset-v3.1 fixture
enrichment (Section 7.2).

### 1.2 Version chain

| Version | Content | Status |
|---|---|---|
| v1 (this document) | Complete freeze-grade draft; five mandatory wording changes baked in (Section 2); C14 arithmetic recomputed under K = 16 with a loud flag (Section 3.4) | Goes to adversarial 3-reviewer panel |
| v2 | Panel revisions; all panel rulings incorporated or answered; C14/C16 restatements ratified | Freeze candidate |
| D0 freeze | v2 sha256-frozen; freeze hash, DGP configs, seed/stream manifest, estimator hashes, analyzer contracts, enriched-fixture manifest, ops plan all hash-locked in the same archive | [TO BE PINNED AT D0: exact freeze timestamp + sha256] |

Reference calendar (PI decision D1_08): theorem work complete ~2026-09-12 (done, ahead of
schedule); D0 outcome-blind freeze ~2026-09-19, to be confirmed by the panel. Post-freeze
campaign: Stage 1 ~19–20 wall-clock days at 70% efficiency, 4-week hard ceiling (Section 8.2).

### 1.3 Freeze mechanics and post-freeze edit policy

After the D0 freeze the ONLY permitted edits to this document and the frozen contract are:

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
   incorporated by reference in Section 3 together with its pre-freeze amendment banner.
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
  prefix fill); S3 pool q = (5,4,3,2), R* = 14 with x° = (V*, 0, 0, 0) (the single-order
  fiber member): TV = 9/14, 81/91, 996/1001, 1 at V* = 1, 2, 4, 6 — at V* = 6 the supports
  are disjoint (q_1 = 5 < 6), hence TV = 1; under the FIFO-prefix point mass c^F the V* = 6
  value is 0.9987 instead (Section 2.5 per-fixture table; the two instantiations coincide for
  V* ≤ 5). Kernel-law-general universal bounds 1 − max_x p(x) on the same pool: 0.357 / 0.505
  / 0.580 / 0.580 across the V*-ladder; balanced-family Binomial limits 1/2, 5/8, 11/16.
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
  swap-invariant: all kernel-blind data coincide on swap pairs (frozen-fixture hash identity
  `da930600...` → `f0862093...` at sequence 6/7 of the dual-arm fixtures).
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
M_fifo(z̄) for all t ≥ 0, including on the integer lattice — Exp = ∅ (point null,
equivalence-tested; O-B); truncation: Exp(D_trunc^W, C) = U(τ) ∩ W with floor localization
(monitor nondecreasing in W, zero when no straddling; O-C); the deterministic eligible_units
displacement under swap→ru is the strongest O-B/O-C prediction (probability-1 visible,
integer-exact, fixture-testable post-enrichment). Instance-level disclosure: the swap→fifo row
on ru cells is instance-level (its threshold depends on never-drawn quantities the ru tape does
not record).

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
> SE(3) orbits, and of the conservation-law weight structure in Neural Mechanics (ICLR 2020).
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
> fiber-equivalent parameters and is not claimed (Soudry et al. 2017; The Loss Does Not See the
> Basis but Adam Does, 2026).

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
  proved directly from the engine. If the panel retains "lumpability" in any theorem name, the
  flag note "vocabulary only; needs-verify" must accompany it; the recommended fix is to avoid
  it in theorem names (this prereg uses "aggregate-sufficiency obstruction").
- **Le Cam two-point lineage** — deliberately excluded; the needed inequality (R2-D) is proved
  inline from the TV triangle inequality.
- **Maximal-atom / log-concavity bounds for lattice laws** — not invoked; only the unproven
  general-composition constant would need them (T1 scope).
- **Optional MVHG/log-concavity bibliographic anchor** — not needed; Lemma D is self-contained
  via explicit Stirling bounds.

---

## 3. Statistical contract (incorporated by reference) and load-bearing numbers

### 3.1 Incorporation identity

The document **"Statistical Contract Port: Paper D → ALPHA Market Cube (FROZEN CONTRACT v1
candidate)"** (`papers/proposal/ecomd_reexploration_contract_v1_2026-09-06.md`), clauses C1–C16
and one-shot analyzer gates G1–G12, is incorporated by reference in full, together with its
pre-freeze amendment banner of 2026-09-06 (PI rulings "用需要算力多的那个，批准，确认，确认"):
(A) C2 K = 16 (K-preflight conservative rule `none_in_set` → 16; PI chose the compute-heavier
option, ~+15% Stage-1 eval V100-h; K immutable after D0); (B) C3 kernel sentence tightened
(engine kernels exactly {fifo, random_unit_within_price}; pro_rata is S3 exact-arithmetic only
and never executes in any cell). Both recorded as C16 ledger items (11)–(12). Derivation
sections of the contract retain their original K = 8 wording as historical reasoning superseded
by the frozen clauses.

### 3.2 Load-bearing clauses (inline restatement; contract text authoritative)

- **C1 Units and pairing.** Inference unit = seed (root of a frozen RNG derivation tree:
  data, init, minibatch, train_kernel, kernel:1..K). Kernel draws, rollout rounds and tapes are
  nested, never inference units. n = 30 seeds per block; fresh never-reused ranges:
  **B1/B2 seeds 11000–11029; B3/B4 seeds 12000–12029** (PI decision D1_10 governs; the ops
  draft's 1000–1029/2000–2014 convention is superseded — panel to confirm, Annex A.4). Each
  bootstrap draw resamples the complete paired eight-cell seed vector.
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
  draw-noise caveat in all reporting. (c) Deterministic-kernel cells execute 16 identical
  evaluations; byte-identity is gate G8. (d) Deterministic neural decode at eval. (e) If the
  D0 corpus generator adds feedback channels, the preflight must be re-run against it before
  freezing K (preflight caveat 2).
- **C3 Cube structure and estimands.** Trained arms (c, t), c ∈ {absolute next state,
  increment}, t ∈ {raw, through-M}; each evaluated at e ∈ {raw, through-M} → 8 cells.
  D_{te} = Ȳ_absolute,te − Ȳ_increment,te; J = D_00 − D_10 − D_01 + D_11;
  φ_train = (T_0 + T_1)/2; φ_infer = (E_0 + E_1)/2. Positive J = the absolute-minus-increment
  contrast grows with joint through-M enforcement. M = the exact combinatorial clearing layer
  (volume and cash conservation, unit integrality, tick lattice, priority kernel ∈ exactly
  **{fifo, random_unit_within_price}**, `scripts/lab_asset/schema.py:22-24`; **pro_rata is NOT
  an engine kernel and never executes in any cell** — S3 exact-arithmetic only, per PI ruling
  D1_14). Through-M training uses the preregistered surrogate family frozen at D0
  (Section 5). **No confirmatory test compares through-M vs raw for superiority; the estimand
  is path-dependence attribution.**
- **C4 Blocks, axes, horizons, fixture generators.** Blocks B1 = (L1 EcoMD v2 x lab-asset-v3)
  [primary], B2 = (L1 x synthetic), B3 = (L2 recurrent fact-surrogate x lab-asset-v3),
  B4 = (L2 x synthetic). Axes (4, confirmatory): ID; agent-population x2 (prestates
  regenerated at 2N, induced capacities rescaled per lab-asset-v3 schema); tick x2 coarser
  (tick 2Δ, frozen band-scaling rule); kernel-swap (DGP truth under FIFO; through-M inference
  under random_unit; truth reference unchanged). Horizons: {1, 4, 16, 31} autoregressive
  clearing rounds (h = 64 recorded descriptively only). All fixtures from the frozen
  fixture-generation procedure from seed roots; every prestate and tape sha256 bound at D0
  (lab-asset-v3 bundle manifest `fea8a136...9581c` is the schema anchor; per-seed fixtures
  extend, never modify, the schema).
- **C5 Endpoints.** Primary: conserving-channel rollout error against DGP truth,
  Y = sqrt(mean_ch mean_t ((x̂_ch,t − x_ch,t)/s_ch)²), channels {volume units, cash ticks},
  s_ch frozen DGP-native per-event innovation std from the generator alone. Through-M cells'
  conservation violation exactly zero (integer-exact); raw cells never clamped or repaired.
  Book-state and price-path errors: preregistered secondary, descriptive only, outside all Holm
  families.
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
  resampled.
- **C9 Primary and multiplicity.** Primary cell: **B1, kernel-swap axis, horizon 16**; single
  prespecified primary; not Holm-adjusted; not overridable by secondaries. Holm families:
  sign-flip tests on the 16 mandatory interaction cells (4 axes x 4 horizons) per block,
  Holm WITHIN each block (4 families of 16). Axis-contrast secondary family: per block the
  three (J_axis − J_ID) at horizon 16, Holm within the triple. Architecture-transfer gate:
  B3 passes iff the primary J is material AND ≥ 8/16 mandatory cells material (Paper D 6/12
  fraction preserved); failure reported as an architecture boundary (U-Net lesson), never
  hidden, never re-gated. [Panel item: pin the "primary J" reference for B3's gate to the
  B3-analogue primary cell — Annex A.3.]
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
- **C14 Record-coverage contract.** See Section 3.4 — recomputed under K = 16 with a loud flag;
  the contract's printed arithmetic (122,880) is stale and MUST be restated at v2.
- **C15 Frozen macros.** All tables and macros generated from the hashed analysis JSON; macros
  include K, fixture-manifest hashes, and the amendment ledger (non-omissible).
- **C16 Amendment ledger (generated, non-omissible).** Items (1) seed = RNG-tree root;
  (2) eight-cell resampling vector; (3) R00 coordinate pinned to increment; (4) channel-scaled
  multi-channel endpoint; (5) reference-degeneracy guard; (6) Holm families 4 x 16
  (Paper D: 1 x 12); (7) axis-contrast family; (8) K-draw CRN protocol; (9) transfer-gate
  fraction 8/16 = 6/12 preserved; (10) clearing-identity gate replaces projection-identity
  gate; (11) K = 16 (preflight `none_in_set` → 16, sha256 f61e410c…, PI ruling "用需要算力多的那个");
  (12) kernel set = {fifo, random_unit_within_price}, pro_rata demoted to S3 exact-arithmetic.
  [Panel items: the authorized two-stage execution (D1_04) and the truncation-condition
  secondary family (plan synthesis ruling 5) are NOT yet rows of this ledger — ratify their
  addition as items (13)–(14) at v2, together with the C14 restatement — Annex A.2.]

### 3.3 One-shot analyzer gate list G1–G12 (one line each)

- **G1 Record coverage**: exact counts per the ratified C14, per cell/axis/horizon/draw; no
  extras, no missing.
- **G2 Run-ID uniqueness and seed pairing**: each seed's 8 cells share
  data/init/minibatch/train_kernel stream hashes and config hashes.
- **G3 Source/config binding**: DGP fixture manifest hashes (incl. lab-asset-v3 anchor
  `fea8a136...9581c`), schema_version == "lab-asset-v3", git SHA, config.yaml hash, seed ranges
  per C1.
- **G4 Checkpoint binding**: 240 checkpoint sha256 vs lock manifest; surgery records reference
  parent hash.
- **G5 Parameter parity + zero-step attestation**: surgery parameters byte-identical to parent;
  optimizer-step count = training-final.
- **G6 Horizon-one clearing identity**: through-M on the DGP's realized request stream
  reproduces the DGP tape byte-exactly (lab-asset replay validator, record-by-record including
  every state_hash).
- **G7 Conservation exactness**: through-M inference cells exactly zero volume/cash conservation
  violation at every step (integer-exact); no clamping anywhere.
- **G8 Deterministic-kernel draw identity**: fifo cells' K = 16 draw-records byte-identical.
- **G9 Determinism replay**: frozen 5% seeded sample of records re-executed byte-identically.
- **G10 Field validity**: finite metrics; pre/post_best_bid/ask present; allocation_rule matches
  the cell/axis spec; n_draws == 16.
- **G11 Namespace hygiene**: no exploratory/reflexive namespace records in any confirmatory
  input.
- **G12 Macro binding**: analyzer emits macros exactly once from the analysis JSON; hashes
  published.

One-shot discipline additionally covers: frozen draw count K, kernel-stream derivation,
fixture-generation procedure, axis generators, and estimators — any change after D0 is a
frozen, hash-recorded amendment or nothing.

### 3.4 C14 record-coverage arithmetic — RECOMPUTED UNDER K = 16 (LOUD FLAG FOR THE PANEL)

The frozen contract C14 prints: "240 training records; 122,880 confirmatory evaluation records
(30 x 8 x 4 x 4 x 8 per block x 4 blocks); 480 horizon-one clearing-identity probes." In that
formula the final factor 8 is the draw count K. Gates G8/G10 were updated to 16 by the K = 16
amendment, but **C14's printed count was not: 122,880 is STALE under K = 16.**

Corrected arithmetic under the frozen K = 16, per the contract's own formula
(30 seeds x 8 cells x 4 axes x 4 horizons x K draws per block):

| Quantity | Contract text (K = 8) | Full 4-block grid at K = 16 | Two-stage design as authorized (D1_04) |
|---|---|---|---|
| Evaluation records per block | 30,720 | **61,440** | Stage 1 (B1+B3, 30 seeds): 2 x 61,440 = **122,880**; Stage 2 (B2+B4, 15 seeds): 2 x 30,720 = **61,440** |
| Confirmatory evaluation records total | 122,880 | **245,760** | **184,320** campaign total |
| Training records | 240 | 240 (K-independent) | Stage 1: **240** (= Paper D's 240-checkpoint precedent: 4 arms x 30 seeds x 2 lineages); Stage 2 adds 180 (variant A both lineages x 15 seeds = 120; variant B L2-only x 15 seeds = 60) = **420** campaign |
| Horizon-one clearing-identity probes | 480 (4 x 30 x 4) | 480 (K-independent) | [TO BE PINNED AT D0: two-stage split of the probe count and its exact condition enumeration] |

Additional enumeration gaps the restatement must close (panel to ratify at v2, Annex A.1):
(i) the truncation-condition deployment passes (secondary family, O-C/O-D) generate records not
enumerated by the C14 formula; (ii) the reflexive namespace is excluded by construction
(uncounted); (iii) the audit-cell retrain (Section 5.4) adds training and evaluation records
under the same formula (cell A10, D1 block, L1, 30 seeds). Until the restated C14 is ratified
at v2, the operative count for gate G1 is the recomputed 61,440 per full seed block at K = 16,
with the two-stage split above; the analyzer aborts on any mismatch against the ratified text.

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
than a contract (Annex A.7).

DGPs: D1 = lab-asset-v3 dual-arm engine (bundle manifest `fea8a136...9581c`) as primary truth,
with a frozen M0/M1-lumpable request generator (episodes, actor mix, rates, bands, master seeds
hashed at D0). D2 = synthetic robustness, Stage 2 only: variant A `garch_student_t5` (both
lineages), variant B `multiscale_logvol` (L2-only), each through a frozen series→request
wrapper into the SAME engine (conservation/replay semantics preserved);
`negative_jump_iid` named-but-not-run.

Staging (two-stage amendment, PI decision D1_04): **Stage 1 confirmatory** = B1 + B3 (both
lineages x lab-asset), 30 seeds, ~650 V100-h (anchor T = 1.8 V100-h per Paper-D training run;
~19–20 days at 70% campaign efficiency; 4-week hard ceiling). **Stage 2 conditional
robustness** = B2 + B4, preregistered first-15-seed subsets, directional robustness only
(no material-nonadditivity claims from Stage 2), ~410 V100-h, mechanical triggers only — never
outcome-triggered: cumulative burn < 1,150 V100-h; Stage 1 complete by D0+26d; L1
convergence-failure rate ≤ 15% (quality gate, not performance); L2 trainability/transfer gate
(finite-loss trainability on D1, else failed transfer reported as boundary per the U-Net
lesson). Day-5 trainability quality gate (NaN ≤ 5% at long rollout; R00 val ≤ 3x L1
seed-median; ≥ 28/30 seeds complete) = early warning only.

Ops prerequisite: node cleanup at D0-S1 (relocate paper D deployment archive to
r2://ecophys/paper_d_archive/ with manifest verification; target ≥ 40% free on both currently
98%/96%-full V100 nodes) — authorized (D1_09), executes at D0, nothing deleted without a
verified manifest.

### 4.2 Axes, horizons, truncation secondary family

Confirmatory axes (4) and horizons {1,4,16,31} per C4. Truncation conditions (trunc_lag,
trunc_cap) run as deployment-map passes carrying orderings O-C/O-D as a preregistered secondary
Holm family (3 tests/block). pop_4x, tick_half, and reverse/pro-rata kernel swaps are
exploratory periphery (4.7). h = 64 recorded descriptively only.

### 4.3 Endpoints (each mapped to its claim; all [AUTH] post-D0)

- **EP1 primary.** B1, kernel-swap axis, horizon 16 (fallbacks: B1-kswap-h31, B1-tick-h16,
  B1-pop-h16). Ordered classification vs δ_s = 0.1·Ȳ_R00(s); channel-scaled conserving-rollout
  RMS; reference-degeneracy guard. Supports the ALPHA attribution estimand and Prop 3.5's
  criterion.
- **EP2 (T2/T3 money results).** On locked checkpoints and S1a fiber pairs: O-A attribution
  floor (consumer RMSE ≥ precomputed R‖v_U‖/√12; raw arms at noise ceiling); O-B swap
  asymmetry (swap→ru > 0 vs swap→fifo point null, equivalence-tested against the SESOI margin);
  O-C truncation monotonicity vs the precomputed curve; O-D granularity fingerprint including
  the preregistered exact-zero null cell (price-notional on ru splits); O-E tape-measurable
  controls (zero interaction). Distinguishes mechanism fiber divergence from representational
  failure (Do LLMs Understand LOB Dynamics 2026) and operator set-identification
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
  rank(ru,po) = 6 at V* = 6 kills P2(iii) — engine-law mismatch STOP).
- **EP4 = S1a constructed fiber pairs.** fifo orthant injections on never-executed orders; ru
  integer splits across never-drawn orders at touched levels. Acceptance gates G1–G3 of the
  theory appendix S1a spec (byte-identical F_exec corpora; state_hash chains differ; |ΔC|
  matches Theorem 1's predicted linear/exact-split values). Hard prerequisite — fixture
  enrichment (Section 7.2); the 21–22-event frozen fixtures cannot measure O-C/O-D or the S1a
  random-unit gates.
- **EP5 = T4 drift telemetry.** Exploratory register only; citation pair Soudry 2017 + "The
  Loss Does Not See the Basis but Adam Does" 2026; never theorem-claimed.

### 4.4 Predicted orderings (S2, on locked checkpoints; confirmatory predictions from T2/T3)

- **O-A (attribution):** consumer RMSE(through-M-trained, raw-infer) ≥ R‖v_U‖/√12 per cell,
  floor precomputed from fixture tapes; RMSE(raw-trained, raw-infer) at noise ceiling; positive
  interaction for fiber-exposed consumers.
- **O-B (swap asymmetry):** swap→ru divergence Θ(R/S) > 0 vs swap→fifo exactly 0 (point null,
  equivalence-tested); per-level weights 1/S preregistered; deterministic eligible_units
  displacement as the strongest prediction.
- **O-C (truncation monotonicity):** divergence increments match the precomputed curves
  (R²/12)Δ‖v_{U∩W}‖² (orthant arms) and (R²/3)p²Δ(m_in·m_out/m) (split arms); monotone in W.
- **O-D (granularity fingerprint):** per-unit-tape arm shows magnitude-consumer floor collapse
  (exact zero for price-notional at touched levels — preregistered null cell) while the latency
  consumer retains the split floor; aggregate-tape variant restores Θ(R²).
- **O-E (controls):** tape-measurable consumers (e.g., cleared-volume prediction) show no
  training-enforcement interaction; zero interaction expected.

All cells, axes, both lineages reported, including class flips and nulls.

### 4.5 Zero-training surgery cells (C11)

The 4 surgery cells per (trained arm, seed) = the trained (coordinate, training-enforcement)
arm evaluated at the other inference enforcement, on the same sha256-locked checkpoint, zero
optimizer steps, parameter parity byte-identical, inference randomness identical to trained
cells (seed-owned kernel streams). They are the empirical exhibit for V4: members
indistinguishable to the training loss (within-fiber) yet distinguished by the deployment maps.

### 4.6 Reflexive firewall (C12)

Reflexive deployment cell (simulator vs a simple adapting execution policy, sim-in-loop),
exploratory only (~6 V100-h; 10 seeds; cells {R00, R11}; D1; both lineages), under the five
verbatim firewalls of C12, scheduled only after all four confirmatory one-shot analyzer hashes
publish.

### 4.7 Exploratory periphery (mandatory label; no confirmatory status)

Per-cell simple effects beyond the interaction; endpoint class-flip enumeration; reflexive
cell; tape-likelihood diagnostic (one-shot descriptive profile feeding T1/T2, outside
confirmatory machinery); SGD within-fiber drift measurements (T4); reverse and pro-rata kernel
swaps; pop_4x / tick_half; M2 adaptive DGP runs; any post-transfer-gate lineage follow-up.
Mandatory label on every output: "exploratory, excluded from confirmatory inference"; excluded
from abstract; no Holm; no SESOI claims.

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
amendment — panel to ratify, Annex A.9), endpoints (C5), SESOI (C6), 50,000-draw paired
bootstrap (C1), checkpoint hash-lock (C11), one-shot analyzers (C13), record coverage (C14).
Compute: inside the D1_07 envelope; [AUTH] at D0.

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

Duruisseaux et al. 2024 (ICML AI4Sci WS; D-2 map §2.3 panel ruling): four arms on an FNO
surrogate for PDE operator learning — baseline G; G trained with the projection; and the
locked-checkpoint inference-only surgery cell; continuous Fourier/Leray projection layer;
estimand constraint-satisfaction / L2 fidelity, 5 seeds. Ruling: external genre parent, must be
cited; "first train x inference constraint crossing" phrasing permanently falsified; novelty
scoped to (i) the market-native combinatorial/integer clearing layer M and (ii) the
SESOI-graded path-dependence attribution estimand.

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
- **R5. Preregistered point-null / exact-zero pattern cells.** O-B swap→fifo point null
  (equivalence-tested against SESOI); O-D price-notional exact-zero preregistered null on ru
  splits; KT-A1 P1/P2/P3 attribution patterns inexpressible as scalar comparisons. The
  template's estimand has no point-null, equivalence-test, or pattern-class slot.

### 6.3 Expressibility table (cells: OWNS / DNO = does-not-own; each reason a restatement of a D-2 map row)

| Inexpressible feature | Duruisseaux 2024 | Solver-in-the-Loop 2020 | GradABM (Chopra 2023) | Dyer et al. ICAIF 2023 | Gen-DFL 2025 | MarS 2024 | M3 2026 | KineticSim 2026 / matching-ABM 2021 |
|---|---|---|---|---|---|---|---|---|
| **R1 competing-mechanism swap at fixed truth** | DNO — layer is continuous Fourier/Leray projection of the same physics; no second mechanism exists to swap | DNO — training-face only; inference always through solver, never swapped | DNO — epi feasibility; no clearing layer/cube | DNO — feasibility anchor; M never an experimental factor | DNO — no mechanism layer; decision-robustness estimand | DNO — production raw-train/through-M-infer cell; never crossed | DNO — engine never off, no FIFO to swap | DNO — M as fixed infrastructure, nothing trained/swapped |
| **R2 kernel x enforcement on OOD axes** | DNO — no OOD factor; constraint/L2 estimand, 5 seeds | DNO — single face, no factorial | DNO — no cube | DNO — M never a factor | DNO — no enforcement axis | DNO — single production cell, no axes | DNO — anchor mismatch documented; engine never removed | DNO — no trained model to cross |
| **R3 fiber-resampling control (dual-hash regeneration)** | DNO — deterministic projection layer; no draws to regenerate | DNO — no stochastic kernel | DNO — no kernel/fiber object | DNO — no kernel/fiber object | DNO — no kernel/fiber object | DNO — pre-mechanism likelihood, engine downstream; no draw-level control | DNO — order-level likelihood; no mechanism in loss, no fiber | DNO — M is infrastructure; KineticSim's bitwise-identical books support swap well-definedness only |
| **R4 dual-lineage transfer gate (C9)** | DNO — single FNO lineage, 5 seeds | DNO — single lineage | DNO — single lineage | DNO — single model | DNO — no lineage axis | DNO — single system | DNO — single foundation model | DNO — nothing trained |
| **R5 point-null / exact-zero pattern cells** | DNO — constraint-satisfaction/L2 fidelity; no point-null or pattern slot | DNO — solver-fidelity comparisons | DNO — feasibility, no null machinery | DNO — feasibility anchor | DNO — decision-robustness estimand | DNO — production objectives, no preregistered nulls | DNO — likelihood anchor, no equivalence tests | DNO — no estimand machinery at all |

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
| R3 | KT-A3 resample arm (swap > δ AND resample < δ/10, dual-hash acceptance) + KT-M1 deployment experiment | KT-A3, KT-M1 |
| R4 | C9 transfer gate on block B3 (both outcomes reported; failure = boundary) | KT-A5 |
| R5 | O-B swap→fifo point null (equivalence-tested) and O-D exact-zero null cell; KT-A1 P1/P2/P3 frozen decision rule | KT-A1, KT-A3 |

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
(per-file sha256; parent lineage = the frozen bundle manifest `fea8a136...9581c`; supports
flags); generator + config (master seed 20260972, documented deterministic search); byte-exact
regeneration proven. Conformance: `tests/test_lab_asset_enrichment_conformance.py` green —
13 of the 27 frozen conformance tests apply to these scenarios and pass; the other 14 are
own-scenario and remain green in the frozen suite; manifest verification + replay determinism +
frozen-bundle read-only guard included. The frozen `a2_exit_20260905` bundle is NEVER mutated.
[Panel item: conformance-wording pin — Annex A.5.] Honest caveats: V*-ladder never-drawn
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
calibration-generator design variance — re-run against the D0 corpus generator if it adds
feedback channels; CRN direction conservative; training-time kernel stream out of scope; FIFO
arm exactly draw-invariant (verified), so K > 1 on deterministic cells buys only the G8
byte-identity gate.

### 7.4 Hash and namespace inventory (frozen or to-be-frozen)

| Item | Value |
|---|---|
| Frozen A-2 bundle manifest | `fea8a136...9581c` (read-only, never mutated) |
| Fiber-resampler prereg statement | sha256 `703ca36e...2c4b` (hash-pinned in test) |
| K-preflight results | sha256 `f61e410cd59c37b5624504a3cdf057c701b4b682067f948d2f8528ace018c2d4` |
| Enrichment master seed | 20260972 |
| Resampler seed namespace | 20260973 |
| K-preflight namespace | 31000–31099 (masters 31000–31031) |
| Training seed namespaces | 11000–11029 (B1/B2), 12000–12029 (B3/B4) — D1_10 |
| Estimator module defaults | λ = 1.0, σ = 1.0, PAM default seed 20260906 (fixture/replay only) |
| D0 archive layout | r2://ecophys/alpha_cube_d0_YYYYMMDD/ (immutable staging; byte-exact re-derivation on both nodes) |
| D0 freeze hash + timestamp | [TO BE PINNED AT D0] |

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

### 8.3 STOP-class rules (verbatim from the inherited risk register; line halts, PI informed, no narrative repair)

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

REFRAME-class (recorded, claim repositioned with recorded deviation): KT-G1 R2 failure
(demote T1 to scoped proposition); KT-G2 separation failure (T2 as risk characterization; if
T1 also loses its dichotomy trace — O-D inverted, exact-zero null rejected — STOP); KT-A1 kill
pattern (|I| ≤ δ/2 everywhere, no sign opposition, surgery antisymmetric → ALPHA is an ablation;
paper rests on GAMMA + boundary report); KT-A4 estimator instability (estimator-conditional
reporting, both shown); KT-M1 gauge-twin null (fiber behaves like internal gauge; empirical
bridge severed; program survives as GAMMA theory; V4 final sentence rewritten as boundary);
through-M surrogate non-convergence (cells classify unresolved, never dropped). BOUNDARY-class:
L2 transfer-gate failure (architecture boundary per the U-Net lesson; claims scoped L1; never
pooled, never hidden). CONTAINED: reflexive-cell leak voids only that exploratory subsection.

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
  estimator instability forces the conditional downgrade."
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

The generated, non-omissible C16 ledger (contract v1) currently carries items (1)–(12) as
restated in Section 3.2. The panel must ratify at v2: (13) the two-stage execution amendment
(PI decision D1_04: Stage 1 = B1+B3 at 30 seeds confirmatory; Stage 2 = B2/B4 at preregistered
first-15-seed subsets, directional robustness only, mechanical triggers only); (14) the
truncation-condition secondary Holm family (O-C/O-D, 3 tests/block); and the C14 restatement of
Section 3.4. The experiment plan §4 recorded the two-stage and truncation items as C16 (11)–(12)
"to be recorded"; the frozen contract's (11)–(12) were taken by the K = 16 and kernel-set
amendments, leaving the two-stage and truncation amendments authorized-but-unrecorded — a ledger
completeness gap, not a design change (Annex A.2).

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
3. This preregistration (v1) — pre-panel draft; v2 = post-panel freeze candidate; D0 freeze
   sha256 [TO BE PINNED AT D0].

---

## ANNEX A — Items submitted to the adversarial panel (v1)

1. **C14 restatement under K = 16 (LOUD).** The contract's printed 122,880 confirmatory
   evaluation records is stale under K = 16 (correct: 61,440 per full-seed block; 245,760
   full-grid; 184,320 under the authorized two-stage design). Trainings (240 Stage 1; +180
   Stage 2) and the probe count (480 formula) need their two-stage splits and the
   truncation-pass/audit-cell record enumerations pinned. Ratify a restated C14 at v2 so G1 has
   an internally consistent target.
2. **C16 ledger completeness.** Add items (13) two-stage execution and (14) truncation
   secondary family (authorized by D1_04 and plan ruling 5 but absent from the frozen ledger
   list), alongside the C14 correction.
3. **C9 transfer-gate "primary J" reference.** Simulator-contracts flag: B3's gate condition
   "primary J material" is ambiguous between the B1 primary cell and B3's analogue; adopt the
   B3-analogue reading (gate measures B3's own primary cell) unless the panel rules otherwise.
4. **Seed namespaces.** D1_10 (11000–11029 / 12000–12029) governs; the ops draft's
   1000–1029/2000–2014 convention is superseded — confirm one final time in the frozen text.
5. **Conformance wording.** Enriched fixtures pass 13 of 27 frozen conformance tests
   (scenario-applicable) with the other 14 own-scenario and green in the frozen suite; freeze
   the exact wording (avoid any "27 + 5 adapter" reading that overstates).
6. **G2 rank-seed collision check.** Add an explicit analyzer check that the three
   preregistered S3 robustness seeds and all instrument namespaces (20260972, 20260973,
   31000–31099) are disjoint from training namespaces and from each other.
7. **L1-4 RNG fix dependency.** The ecomd_v2 SPS edge-sampling RNG gap (global torch.rand)
   must land before D0 or G8/G9 byte-exact replay rests on an assumption; L2 compute anchors
   are unmeasured planning estimates until the D1_13 code-only build lands — panel should
   verify both before freeze.
8. **Lumpability vocabulary.** If "lumpability" is retained in any theorem name, attach the
   needs-verify vocabulary-only flag (Section 2.8); recommended: keep it out of theorem names
   (this prereg already uses "aggregate-sufficiency obstruction").
9. **Estimator-menu audit cell under K = 16.** Section 5.4's statement that K = 16 governs the
   audit cell supersedes the estimator-menu document's inherited "K = 8" line — ratify.
10. **D0 date.** Confirm ~2026-09-19 or set a new freeze date (D1_08 reference calendar).

---

## References (ALL from the D-2 evidence map adjudication; no other source is cited as fact)

DPIOT (ICML 2022); Perturb-Argmax/Softmax statistical representation properties (Cohen
Indelman & Hazan, 2024, arXiv:2406.02180); Diaconis & Sturmfels (1998); contingency-table
fibers (2014); Duruisseaux et al. (2024, ICML AI4Sci WS); Solver-in-the-Loop (Um et al., 
2020); GradABM (Chopra et al., AAMAS 2023); Dyer et al. (ICAIF 2023); Gen-DFL (2025); MarS
(2024); M3 (2026); KineticSim (2026); matching-engine ABM (2021); Quotient-Space Diffusion
Models (ICLR 2026); Neural Mechanics (ICLR 2020); Soudry et al. (2017); "The Loss Does Not See
the Basis but Adam Does" (2026); "Do Differentiable Simulators Give Better Policy Gradients?"
(ICLR 2026; "Onoda ICLR 2026" in D-1 documents); Minimizing Surrogate Losses for DFL (2025);
Gumbel-Softmax (2016); Do LLMs Understand LOB Dynamics (2026); Counterfactual Operator
Relevance (2025); TRADES (2025); DEX closed-loop (2026); Paper D (internal parent, 
`papers/paper_d_constraints/`). Needs-verify items (vocabulary only, never cited as fact):
Markov-lumpability literature. Deliberately excluded: Le Cam two-point lineage (inline TV
triangle proof); maximal-atom/log-concavity lattice bounds.

---

*Provenance: authored by the preregistration-drafter agent of the D-1/D0-prep workflow
(session task record; branch paper-d-iclr-2027-completion), grounded in the 11 companion
documents listed in Section 1.4, all read in full. Zero GPU, zero market data, zero
confirmatory endpoints, zero outcome access; the frozen A-2 bundle consumed strictly
read-only.*
