# D-1 execution session 1 record (2026-09-06): theorem package + authorized instruments

Stage: D_minus_1_execution_authorized_prep_d0 under decision
`pi_reexploration_d1_authorization_20260906` (PI "全部授权" of all ten experiment-plan §11
items). Execution: 10-agent workflow (5 theorem + 3 build wave 1; 2 build wave 2), 0 errors;
full per-agent returns in the workflow journal (wf_65cd14e7-d12). Independently re-verified
post-hoc: 93 passed + 1 by-design strict xfail across the four new test files; frozen bundle
verify PASS (7 files, both fixtures replay byte-exact); `git status` shows zero modifications
under `experiments/lab_asset_a2/a2_exit_20260905/`. Zero GPU, zero market data, zero trained
models, zero confirmatory endpoints — all work theorem/schema/CPU-instrument class.

Full writeups (statements + proofs + hostile checks):
`papers/proposal/ecomd_reexploration_d1_lemma_writeups_2026-09-06/` — kt_g1_r2…, kt_g2…,
kt_g3…, kt_g4_g5…, kt_a2_tv_separation_and_kt_m2_template_table.md.

---

## 1. Theorem outcomes — all seven [NOW] items discharged at theorem level; zero REFRAME triggers

| Item | Status | Core result | Key conditions / honest boundaries |
|---|---|---|---|
| **KT-G1 R2 non-lumpability** (the must-prove pre-D0 lemma) | **proven** (4-part package; R2-B proven_with_conditions) | R2-A: point-mass vs MVHG TV = 1 − max_x p_x, exact constants — (2,2) pool V*=2: **TV 5/6**; S3 pool (5,4,3,2): TV = 9/14, 81/91, 996/1001, 1 at V* = 1,2,4,6. R2-B: for EVERY responsive policy (single designated pool actor, injective non-cancelling response), one-step aggregate-transition kernels of aggregate-indistinguishable states separate by TV ≥ 5/6, uniform over the class. R2-D training-signal obstruction: any aggregate-tape-measurable predictor incurs sup TV ≥ 5/12. R2-C M0 concession proven in the other direction with a SHARP boundary | Obstruction is the **kernel × granularity × policy-feedback triple interaction**, not blanket M1+: all-respond buy-back-own-fills policies are aggregate-silent at pooled windows (sharpness counterexample proven). True boundary = "no active identity channel" (off the slack stratum even M0 fails, TV = 1 via self-trade prevention — stronger than the ladder story but muddies it). General-composition asymptotic constant 1 − O(R*^−1/2) UNPROVEN (maximal-atom/log-concavity not in D-2 map) — scoped to balanced-family Binomial limit |
| **KT-G2 separation** | **proven_with_conditions** — REFRAME row does NOT fire | G2-2 (infinity separation): any **kernel-blind** uniformly valid floor bound is forced to be identically zero on data where kernel-specific floors are positive — kernel-blind certification is vacuous. G2-3 same-data separation ≥ 2x (headline 3x; family 4·m_out/m). G2-4 resolves the tape-aware question (the tape pins U(τ) but not the kernel) | The finite-gap factor is coupled to the frozen reference convention (two-sided eps ~ Unif[−R,R] vs one-sided box [0,R]) — under width-matching the gap inverts to m_out/m ≤ 1; **both conventions must be stated at D-1 wording freeze**. Swap-invariance formalization of "mechanism-independent" is a definitional choice argued minimal, not proven unique. (Its "no dynamic fixture realization" caveat was written pre-enrichment; the enrichment now supplies multi-order fixtures — S1a dynamic gates remain post-D0.) |
| **KT-G3 gauge pair** | proven_with_conditions (Lemma B + soft-quotient extension proven) | Lemma A: no corpus-compatible, fiber-nontrivial quotient preserves the named consumers — complete quantity-direction dichotomy (Σp_i u_i ≠ 0 ⇒ C_risk; = 0 ⇒ C_lat^W; never-drawn splits clock-free by the swap consumer, TV ≥ \|u_i\|/S_ℓ). Lemma B + B.3: deterministic, loss-side, and **soft/randomized** quotients all confine predictors to fiber-constant selections at exactly the Theorem 1 floor; B.4 prior-universal; B.5 quotient destroys (not relocates) the deployment-composed prediction map | Task's Lemma-A route phrasing was false as literally stated (Q = id) — corrected openly: fiber-nontriviality is hypothesized as the repair's defining property. **Ownership-relabeling of never-executed orders conceded as a genuine function-preserving gauge core** (Lemma A.4; = T1-P2(v) aggregation residue). Lemma B is corollary-grade by design — never to be sold as a new estimation theorem |
| **KT-G4 chart-free prongs** | (a),(b) proven; (c) proven_with_conditions; **(d) refuted as stated** | (a) σ-algebra transport; (b) V*=2 jump is a property of the count-law family — multinomial provably jump-free under every smooth reparameterization; (c) floor/exposed-set naturality as a trichotomy | **Prong (d): positive fiber dimensionality in θ-charts IS chart-dependent — DPIOT owns that residue; T1 must carry the concession sentence with DPIOT + Perturb-Argmax citations.** Exact floor constant is reference-measure-relative (declared contract item); chart-free object is Var_μ(C\|σ(T)) |
| **KT-G5 exposed sets** | proven (T-1, T-2a, T-2b; T-2c with conditions) | Exhaustive one-step exposed-set table (exact/sign/magnitude) for the preregistered deployment grammar; functorial no-creation; composition-order asymmetry (P3.4 elevated); postponed creation via horizon extension | swap→fifo-on-ru-cell row is instance-level (threshold depends on never-drawn quantities the ru tape does not record). **Nomenclature conflict found: killer-doc 'exposed(D_id) = ∅' vs appendix P3.1 'Exp(id) = span⁺(U)' — replace D_id by two preregistered null controls D_read (Exp = ∅) and D_raw (Exp = U)** |
| **KT-A2 stage-1 TV separation** | proven_with_conditions | Three layers: (0) aggregate anonymity TV = 0 — conceded in the same sentence; (1) full F_exec grammar TV = 1 (trivial layer, no lead claim rests on it); (2) **key-equalized attribution projection TV = 1 − ∏_i C(q_i, c_i^F)/C(R*, V*) exactly** — S3 pool: 0.64 / 0.89 / 0.995 / 0.999 across V* ∈ {1,2,4,6}; strict-positivity dichotomy with collapse strata exactly the stage-2 negative controls | **No uniform-in-pool constant**: adversarial pools (q = (R*−1, 1), V* = 1) drive TV to 1/R* — constants are pool-parameterized (preregistered per fixture). MVHG instantiation conditional on (A3′) until S3/conformance machine-check the draw law post-freeze |
| **KT-M2 template-expressibility table** | proven (table) | Rows (competing-mechanism swap, kernel×enforcement on OOD, fiber-resampling control, + identified others) × genre parents (Duruisseaux 2024, GradABM, Dyer ICAIF 2023, Gen-DFL, …) with owns/does-not-own + one-line reasons, checkable line-by-line against the D-2 adjudication rows | No new claims about the parents beyond the evidence map |

New references needing verification (deliberately NOT cited as fact): Markov-lumpability
literature (used as vocabulary only; both statements proved directly from the engine);
Le Cam two-point lineage (deliberately kept OUT — the needed inequality is proved inline from
the TV triangle inequality); maximal-atom bounds for log-concave lattice laws (only the
unproven general-composition constant would need them); optional MVHG/log-concavity
bibliographic anchor (proofs are self-contained via Stirling bounds).

## 2. Authorized instruments — all three built and tested

### 2.1 Fixture enrichment (D1_03) — `experiments/lab_asset_a2/enrichment_20260906/`
10 new engine-generated fixtures: **5 arm-consistent kernel-swap pairs on the S3 scaffold**
(q_P = (5,4,3,2), two better levels, two deeper orders), V* ∈ {1,2,4,6} + **exhaustion
episode**, clock-straddling never-drawn sets at every interior rung; backward-compatible
**lab-asset-v3.1** schema extension (arrival_clocks as pre-session prestate metadata,
deliberately excluded from prestate_hash — clocks live in the raw flow, exactly the F_exec
point); `enrichment_manifest.json` (per-file sha256, parent lineage = frozen bundle manifest,
supports flags); generator + config (master seed 20260972, documented deterministic search);
byte-exact regeneration proven. Conformance: `tests/test_lab_asset_enrichment_conformance.py`
green (13 of 27 frozen conformance tests apply to these scenarios and pass; 14 are
own-scenario and remain green in the frozen suite; manifest verification + replay determinism
+ frozen-bundle read-only guard included). Honest caveats: V*-ladder never-drawn realizations
are seed-frozen facts, not laws; ru tapes realize ONE draw sequence per episode (law-level
work uses the resampler/enumeration); no rejection/latency-choice/crossing-replace events by
design.

### 2.2 Fiber resampler (D1_02) — `scripts/lab_asset/fiber_resampler.py` (881 lines)
Engine-driven, dual-hash acceptance: aggregate_state_hash sequence identical AND state_hash
chain differs, with **native RNG-state accounting so state-chain equality coincides with
allocation-trajectory equality**. MVHG exact-law conformance at three levels (exact
enumeration, conditioned engine law, seeded MC over all attempts: p ∈ [0.29, 0.88]); acceptance
rate = 1 − P_engine(original trajectory) exactly as predicted (vstar1 ≈ 71.4%, vstar2 ≈ 93.4% —
rejections are correct trajectory-clone refusals, not failures); deterministic kernels and
single-order pools correctly admit NO accepted resample (the KT-A3 control). 40 tests + 1
by-design strict xfail (`tests/test_fiber_resampler.py`). Frozen prereg statement
(sha256 703ca36e…2c4b, hash-pinned in the test). Seed namespace 20260973.
**Documented judgment call requiring D0 ratification:** the criterion-(ii) semantics
(native-RNG-state-preservation) — the literal raw-hash reading would count rng-state-only
differences as variation and make fifo/single-order pools trivially "accepted", destroying the
KT-A3 control; the wrapper is one class to swap if the freeze prefers literal.

### 2.3 K-variance preflight (D1_06) — `experiments/reexploration/k_preflight_20260906/`
32 seeds × 6 episodes × 2 arms × 16 nested draw replays (192 episodes, 6144 engine
evaluations, ~24 s CPU); 4 stream-null + 5 draw-dependent DGP-native statistics; variance
decomposition B(K) = V_between + W/K with seeded bootstrap CIs; 6 engine-grounded invariants
zero-failure (incl. FIFO payload-projection identity and request-boundary aggregate-hash
identity across BOTH arms and all replays); byte-identical determinism (results.json sha256
f61e410c…). **Frozen conservative rule returns none_in_set → K_recommended = 16 with
insufficiency flag**: all endpoint-shaped functional statistics (c_lat_exec, alloc_l2,
n_maker_filled) clear the 10% bar by an order of magnitude already at K=8 (e.g. c_lat_exec
0.0022 at K=8), but **alloc_proprata_dev_mean is draw-dominated at every authorized K**
(0.196 at K=16; W > V_between). K=4 not supported (alloc_hhi CI upper 17%).
**PI options at D0 freeze: (a) K = 16 (~+15% Stage-1 eval V100-h) or (b) K = 8 on the
functional-statistic + CRN-paired reading.** Caveats: preflight bounds only the DGP-side
draw-replay component (training noise invisible to it); must be re-run against the D0 corpus
generator if it adds feedback channels; CRN direction conservative. Seed namespace
31000–31099 claimed.

## 3. Simulator contracts (D-1 gate row 3) — `ecomd_reexploration_simulator_contracts_2026-09-06.md`
Every claim file:line-verified and classed [EXISTS] or [D0 BUILD]. Load-bearing findings:

1. **L1 RNG gap (blocks G8/G9)**: ecomd_v2 SPS edge sampling uses global `torch.rand`
   (ecomd_v2.py:145); step-generator binding covers only StochasticPairwisePotential
   (ecomd.py:1245-1247). Cross-node byte-exact v2 rollout replay currently rests on identical
   global-RNG consumption order — an assumption, not a contract. **Build item L1-4 must land
   BEFORE D0 freeze.**
2. **L2 is ~90% a D0 build**: `fact_surrogates.py` is a library of 4 loss functions, not a
   recurrent model — no parameters, training loop, checkpoint, or seeding surface exist; ops
   compute anchors for L2 are unmeasured planning estimates.
3. **pro_rata is NOT an engine kernel** (schema.py:22-24 implements FIFO +
   RANDOM_UNIT_WITHIN_PRICE only); it exists as S3 exact-arithmetic. **Contract C3's kernel
   sentence must be tightened at freeze** or contract text and engine truth diverge.
4. Conservation values are engine state, not tape payload fields — the conserving-channel
   endpoint Y requires the E-4 regenerate()-based emitter.
5. Seed-namespace inconsistency (ops draft 1000-1029/2000-2014 vs PI D1_10 + contract C1):
   **D1_10 governs**; prereg panel must pin it.

## 4. Estimator menu (D1_07) — `ecomd/mechanisms/through_m.py` + estimator-menu doc
Straight-through (pinned scale) primary + perturb-and-MAP (pinned noise) audit; 20/20
read-only fixture tests green; mypy --strict + ruff clean. PAM forward exactness on the two
frozen fixtures is a single-maker fixture property; the general forward-exactness burden is
carried by exact_clearing's live-engine multi-maker cross-check (shared with ST). PAM's
selection-masked-identity surrogate coarseness is exactly what KT-A4 measures. Priority-score
maps are frozen menu choices (immutable after D0). Production seeds must come from the
D0-frozen RNG-tree (contract C2), not the module replay default.

## 5. Updated killer-test register (supersedes plan §6 "Remains" column)

| ID | Status after this session |
|---|---|
| KT-G1 | **Theory discharged** (R2 proven with sharp M0/M1 boundary + triple-interaction scoping). Remains post-D0: S3 machine-check of the draw law (engine-law mismatch STOP risk lives there) |
| KT-G2 | **Theory discharged** (REFRAME row does not fire; Defense 4 added to T2's hostile check). Remains: static dual-hash loss audit — **subsumed by the resampler + estimator fixture gates**; wording freeze must state both reference conventions |
| KT-G3 | **Theory discharged** (Lemma A/B/B.3 + final V4 text). Empirical twin = KT-M1 post-D0 |
| KT-G4 | **Theory discharged with prong-(d) concession** (DPIOT owns the θ-chart residue — write the concession sentence into T1) |
| KT-G5 | **Theory discharged** (T-1/T-2a/T-2b/T-2c + contrived-D scoping). Nomenclature fix D_id → D_read/D_raw must reach both T3 statement and prereg |
| KT-A2 | **Stage-1 lemma proven** (three-layer TV with per-fixture constants). Stage-2 items remain run-gated |
| KT-A3 | Instrument READY (resampler); contrast spec frozen; run post-D0 |
| KT-A4 | Menu built + fixture-tested; two-estimator audit retrain remains [AUTH] |
| KT-A5 | Unchanged (run-gated; transfer gate C9) |
| KT-M1 | Instrument READY (resampler dual-hash = the machine-checkable within-fiber relation); deployment experiment post-D0 |
| KT-M2 | **Table delivered** (checkable vs evidence map); confirmation shared with KT-A1/A3/M1 |

## 6. New PI decision items surfaced (add to the D0-freeze decision list)

1. **K = 16 vs K = 8** (preflight rule output vs functional-statistic reading; ~15% Stage-1
   eval V100-h difference; alloc_proprata_dev_mean is draw-dominated at every authorized K).
2. **Ratify the resampler criterion-(ii) semantics** (native-RNG-state-preservation
   recommended; literal reading destroys the KT-A3 control).
3. **L1-4 RNG-fix build before D0** (byte-exact replay contract), and **confirm the L2 build
   scope** (~90% D0 build: the recurrent surrogate itself, its training loop, checkpoint
   format, seeding surface; current compute anchors for L2 are unmeasured estimates).
4. **Contract C3 kernel-sentence tightening** (pro_rata not an engine kernel; S3-only).
5. Optional: adjudicate lumpability vocabulary if used in theorem names (needs-verify list).

## 7. Remaining pre-D0 work (reference calendar: theory ~09-12 ✅ ahead of schedule, D0 ~09-19)

- Preregistration draft (claims T1–T4 with the five wording changes above baked in; grid;
  EP1–EP5; orderings; gates; nonclaims; de-scope ladder) → adversarial 3-reviewer panel →
  confirm D0 date.
- KT-M2/parent-reduction packet freeze into the prereg; L1-4 RNG fix; L2 build decision.
- D0-S1 node cleanup (authorized, executes at D0): paper D archive → r2://ecophys/paper_d_archive/,
  ≥40% free both nodes.
- Post-freeze permitted only: finite-instance corollaries, constants polishing, enumeration
  vs preregistered targets.

---

Provenance: workflow wf_65cd14e7-d12 (10 agents, 1.27 M subagent tokens, 500 tool calls,
51 min); independent post-hoc verification by the orchestrator (tests, bundle verifier, git
status). Session ledger: logs/2026-09-06.md Session 5.
