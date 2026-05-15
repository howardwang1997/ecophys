# Paper A — NeurIPS 2027 status (living document)

**Last updated**: 2026-05-15 (089 landed, weekend batch designed)
**Branch**: `feature/paper-a-neurips-2027`
**Plan**: `~/.claude/plans/curried-cuddling-cloud.md` (M1-M6, 8 wk each, → 2027-05 deadline)

This document is the single source of truth for what's done, what's launching,
and what H20 batches still need to be designed. Update in place as state changes;
see `logs/YYYY-MM-DD.md` for chronological history.

---

## TL;DR

- **089 attribution batch landed** (796/800, commit `321633ba`): `attr_zumbach_dn_s10` is best single mech (mean **5.12**, +0.31 vs baseline, only 2/50 rej). **Both floors lifted by single mechanisms** but with collateral tradeoffs → falsification reframes from "absolute" to "Pareto-bounded".
- **3-day batch (2026-05-15 PM → 2026-05-18 PM, ~36h H20 wall)**: 9 sub-batches totaling 1946 cfg. Original five (090/090b/094/091/095) + four bonus phases pulling M3 work forward: 090c n=50 confirms + AR(1)-clip×Zumbach, 090d depth-3 interference, 092 5-asset replication, 089b cross-asset attribution.
- **Mac-side M1 modules are 6/6 done after this session**: AR(1) + Zumbach + distributional metrics + VaR ✅; TimeGAN/WGAN-LP + calibration harness shipping in the weekend batch commits.

---

## 1. Done — committed on `feature/paper-a-neurips-2027`

| Commit | Module | Tests | LoC |
|---|---|---|---|
| `b24ac01d` | M1.7 — Memory + log + Branch F analysis | — | — |
| `3530a8ed` | M1.1 AR(1) whitening + M1.2 Zumbach feedback (integrator + config wiring) | 17 | ~120 + 200 |
| `1be6e4ab` | M2.1 — 089 attribution batch (800 cfg) + `h20_paper_a_neurips_2027.sh` launcher | preflight ✓ | 153 + 228 |
| `afa164e1` | M1.3 distributional metrics + M2.2 attribution analyzer | 11 | 150 + 230 |
| `(M1.4)` | VaR/ES backtest + 3 samplers (Historical, GARCH, ECoMD) | 15 | 230 + 145 |
| `fe1a2fd6` | Daily log capture (Sessions 4 + 5) | — | — |

Total: **43 new passing tests** across 4 new modules.

---

## 2. 089 attribution batch — LANDED 2026-05-15

**Result summary** (full matrix at `experiments/089_attribution_50seed/attribution_matrix.md`):

| cell | n/50 | rej | mean | Δ vs baseline | notes |
|---|---:|---:|---:|---:|---|
| **`attr_zumbach_dn_s10`** | 48 | 2 | **5.12** | **+0.31** | new mech, best single, 8/12 facts ↑ |
| `attr_b3_k3` | 50 | 0 | 4.96 | +0.14 | replicates Branch F (4.94) |
| `attr_asymdrag_a06` | 48 | 2 | 4.92 | +0.10 | replicates Branch F (4.94) |
| `attr_powerlaw_a15` | 50 | 0 | 4.88 | +0.06 |  |
| `attr_ar1_s05` | 49 | 1 | 4.88 | +0.06 | huge fact-trader, see below |
| `attr_baseline_v3` | 49 | 1 | 4.82 | — | reference |
| ... | | | | | 10 more cells, all -0.07 to -0.89 |
| `attr_ar1_s03` | **15** | **35** | 4.47 | -0.35 | unstable; lifts autocorr +62pp |

### 2.1 Positive findings (paper-ready)

1. **Zumbach `dn` variant validates Zumbach 2009 theoretical direction**: downside-only causal asymmetry beats abs variants on both overall mean (5.12 vs 4.12-4.75) and zumbach_asymmetry pass rate (29% vs 10-12%). Section §4 of the paper writes itself: "we designed two variants of a causal-asymmetry mechanism; the theory-aligned variant (downside-only) was the best single mechanism in 16-cell ablation."
2. **Both architectural floors lifted by single mechanisms** (was thought impossible after Branch F):
   - `autocorr_returns`: 24% (baseline) → **87%** (ar1_s03) → +62pp
   - `zumbach_asymmetry`: 6% (baseline) → **43%** (ar1_s05) → +37pp; or 29% (zumbach_dn_s10, stable) → +23pp
3. **Per-fact "biggest mover" table** (11 facts, each owned by a different specialist mechanism): this IS Figure 1. Mechanisms behave as specialists, not generalists. C1 contribution evidenced directly.
4. **Scoring pipeline reproducible across batches** (Branch F → 089): asymdrag 4.94 → 4.92, b3 4.94 → 4.96. Δ ≤ 0.02 at n=48-50. Standardized tooling claim defensible.

### 2.2 Falsification claim — reframed

Old (pre-089): "two facts are architecturally impossible in v3" — too strong, **not survived**.
New (post-089): **"the 11 facts form a Pareto frontier no single mechanism crosses simultaneously."** Every cell that lifts a floor breaks ≥1 other fact by ≥20pp. Specifically:
- `ar1_s03` lifts autocorr +62pp but breaks acf² -65pp
- `ar1_s05` lifts zumbach +37pp but breaks ckur -47pp
- `asymdrag_a06` lifts leverage +28pp but breaks ckur -24pp, hurst -20pp
- `zumbach_dn_s10` is the only cell with no individual breakage ≥ -13pp — hence the safest composition seed

Still NeurIPS-grade: compositional impossibility is a publishable result; the claim weakens from "absolute" to "tradeoff-bounded".

### 2.3 Open instability — AR(1) low-strength fails to train

`ar1_s03` has 70% rejection rate (35/50 seeds blow up). Mechanism works (when it converges, autocorr 87%), but the parameter envelope is fragile. **Weekend batch §3.2 addresses this** with a (strength × λ × drift-clip) grid.

---

## 3. 3-day batch (2026-05-15 PM → 2026-05-18 PM) — nine sub-batches

Total wall: ~36h on 8-card H20, 1946 ABM cfg + 50 GAN/TrajCast fits.

Launcher: `scripts/h20_weekend_2026-05-15.sh` sequences all nine with preflight checks and CONFIG_ORDER_PREFIXES priority.

| # | batch | cfg | est wall | purpose |
|---|---|---:|---:|---|
| 1 | 090 patch composition | 240 | 3.5h | hero cell mean ≥5.5 hunt |
| 2 | 090b AR(1) stability grid | 120 | 2h | fix s03 70% rej |
| 3 | 090c n=50 confirm + AR(1)-clip×Zumbach | 150 | 2.5h | strengthen SOTA cells + new combo |
| 4 | 090d depth-3 interference probe | 180 | 3h | strengthen depth ceiling claim |
| 5 | 094 VaR holdout | 96 | 1.5h | clean train-test split |
| 6 | 091 calibration ECoMD leg | 30 | 0.5h | wall × coverage |
| 7 | **092 5-asset cross-asset replication** | 600 | 11h | reviewer-2 cross-asset attack |
| 8 | **089b cross-asset attribution** | 480 | 9h | per-asset Figure 1 |
| 9 | 095 WGAN-LP + TrajCast-lite baselines | 50 | 7h | §5 baseline table |
| | **TOTAL** | **1946** | **~36h** | |

### 3.1 Batch 090 — patch composition (3.5h, top priority)

**Why we need it**: 089 identified `zumbach_dn_s10` as the safest patch seed (no fact dropped ≥-13pp). Composing it with existing best singles is the cleanest path to the first mean ≥5.5 cell. Bundles AR(1) compositions too.

**Cells** (8 × 30 seeds = 240 cfg):
1. `pair_zumdn_b3` — Zumbach `dn` + B3 k=3 (target: 5.5+)
2. `pair_zumdn_asym` — Zumbach `dn` + asymdrag α=0.6
3. `pair_zumdn_ar1` — Zumbach `dn` + AR(1) s05 (the two new mechanisms together)
4. `pair_ar1_b3` — AR(1) s05 + B3 k=3
5. `pair_ar1_asym` — AR(1) s05 + asymdrag α=0.6
6. `triple_zumdn_ar1_b3` — depth-3 stress test (does it interfere per Branch F finding?)
7. `pair_AB_reref` — asymdrag + B3 re-run at n=30 (Branch F best 5.18, verify on neurips branch)
8. `zumdn_solo_n30` — Zumbach `dn` solo n=30 (Branch F-style replication)

### 3.2 AR(1) stability grid — fix the 70% rejection (2h)

**Why**: `ar1_s03` succeeds at autocorr_returns (87%) but blows up training. Need parameter envelope.

**Cells** (6 × 20 seeds = 120 cfg): cross strength {0.2, 0.25, 0.3} × lambda {0.90, 0.97} + 2 drift-clip variants.

### 3.3 Batch 094 — VaR holdout training (1.5h)

**Why we need it**: 089 trains on SPX `2015-2026_daily`. VaR backtest on 2018-2026 with those checkpoints = **training-test overlap → information leakage**. Reviewer-2 will catch this immediately. Trimmed to 8 best cells (post-089) × 12 seeds = 96 cfg.

**Cells**: baseline_v3, zumbach_dn_s10, b3_k3, asymdrag_a06, ar1_s05, powerlaw_a15, pair_zumdn_b3, pair_zumdn_asym.

### 3.4 Batch 095 — TimeGAN/WGAN-LP + TrajCast bundle (M1.5, ~7h)

**Why we need it**: reviewer-2 will demand a GAN-family baseline. WGAN-LP variant chosen (Wiese 2020 QuantGAN) — ~3× simpler than TimeGAN, similar paper story. Bundles a TrajCast-lite surrogate (§6.1).

**Cells** (5 assets × 5 seeds × 2 models = 50 fits): SPX, BTC, EURUSD, GOLD, NDX × {WGAN-LP, TrajCast-lite}.

### 3.5 Batch 091 — Calibration-speed shootout, ECoMD leg (M1.6, ~3h)

**Why we need it**: headline downstream task — "ECoMD calibrates ~100× faster than ABIDES+SBI". This weekend we ship the **ECoMD leg only** (30 calibration runs × 5 assets = 150 runs); ABIDES+SBI leg blocked on H20 install and runs next weekend.

ECoMD calibration harness (`ecomd/calibration/wallclock_harness.py`) records wall-clock + n_iters + final fact coverage at multiple early-stopping budgets. Output drives Figure 3 once ABIDES leg lands.

---

## 4. Mac-side M1 progress (6/6 done after this session)

| | module | status |
|---|---|---|
| ✅ M1.1 | AR(1) drift whitening (integrator) | committed |
| ✅ M1.2 | Zumbach causal-asymmetry (integrator) | committed |
| ✅ M1.3 | Distributional metrics (`ecomd/eval/distributional_metrics.py`) | committed |
| ✅ M1.4 | VaR backtest (`ecomd/risk/`) | committed (clean numbers from 094) |
| ✅ M1.5 | WGAN-LP + TrajCast-lite (`ecomd/baselines/wgan_lp.py`, `trajcast_lite.py`) | this session |
| ✅ M1.6 | Calibration harness ECoMD leg (`ecomd/calibration/wallclock_harness.py`) | this session |

Plus M2 sub-tasks already shipped:
- ✅ M2.1 089 attribution batch generator + H20 launcher
- ✅ M2.2 `scripts/score_attribution.py` — auto-builds 10×11 attribution matrix (validated on 089)

---

## 5. Decision queue

1. **Monday morning (2026-05-18) after weekend batch lands**:
   - Run `score_attribution.py` on 090 → does any patch composition reach mean ≥ 5.5? If yes, that's the hero cell. If no, write up "Pareto frontier is hard" as central finding.
   - Run `var_backtest.py` on 094 checkpoints → does ECoMD beat GARCH on 1d VaR? Independence test?
   - Run `score_continuous.py` on 095 → do WGAN-LP and TrajCast-lite also hit the Pareto frontier? (Critical for falsification scope.)
   - Run `wallclock_harness.py --report` on 091 → does ECoMD calibrate in ≤100 grad iters on all 5 assets?
2. **Within 1 week** (post-Monday): add TrajCast (NMI 2025) citation + positioning paragraph to `papers/paper_a_methods/outline.md` §2 Related Work + symmetry-group disclosure in §3 (agent permutation, not E(3)).
3. **Within 1 week**: install ABIDES on H20 (1-2h interactive); design ABIDES+SBI leg of 091 calibration shootout for next weekend window.
4. **Within 2 weeks**: write up 089 attribution matrix as Figure 1 draft (`papers/paper_a_methods/figures/fig1_attribution.py`). This is the highest-information density figure in the paper.

---

## 6. TrajCast (Thiemann et al. 2025, NMI) — relevance + integration

Reviewed 2026-05-13. Autoregressive equivariant GNN for force-free MD prediction in materials/chemistry; reports 30× longer stable forecast intervals and 15ns/day on a 4000-atom solid. Three angles for Paper A:

### 6.1 Bundle a TrajCast-style autoregressive surrogate into batch 095

The headline TrajCast claim is that an autoregressive GNN can replace explicit force computation while staying stable over long rollouts. For Paper A's falsification framing, the question is: **does a force-free autoregressive surrogate also hit the `autocorr_returns` and `zumbach_asymmetry` floors when trained on the same SPX/BTC/EURUSD/GOLD/NDX data?**

If **yes** (likely outcome) → the floors generalize beyond ECoMD's mechanism class to the entire differentiable-surrogate family — strongest possible falsification claim, lifts acceptance estimate ~+5-8pp.

If **no** → TrajCast clears a floor we cannot, which becomes a positive finding for *that* baseline and forces us to re-scope the falsification claim (still publishable, weaker headline).

**Implementation**: minimal autoregressive surrogate (~300 LoC) — single MLP/transformer predicting `r_{t+1}` from `[r_{t-K:t}, σ_{t-K:t}, regime indicator]`, no explicit force decomposition. Permutation symmetry on agents collapses to a no-op since we operate on aggregate market state, not per-agent particles → compare apples to apples. Wire into `ecomd/baselines/trajcast_lite.py` parallel to `ecomd/baselines/timegan.py`.

**H20 cost**: bundle into batch 095 alongside TimeGAN/WGAN-LP. Same 5 assets × 5 seeds = 25 fits. ~+4h H20 wall on top of TimeGAN's ~10h. Unified scoring through the existing 11-fact pipeline.

**Decision gate** (after 089 lands): only commit to this if AR(1) and Zumbach floors persist in the 089 attribution matrix. If either floor is lifted by a single mechanism, TrajCast bundling becomes lower priority.

### 6.2 Borrow rollout-stability training tricks (P1, gated on time)

TrajCast's long-rollout stability comes from autoregressive training with noise/perturbation regularization (training section needs verification against their code). Our `depth ≥ 3 ⇒ degradation` finding (4.94 → 5.18 → 4.79 → 4.62) is plausibly rollout drift, not a fundamental mechanism-class limit. Adding scheduled-sampling-style perturbations to `ecomd/training/train_distributed.py` could push the compositional ceiling from depth-2 to depth-3 — that would be a paper-grade finding by itself.

**Effort**: ~2-3h Mac dev + one small H20 sweep (~5h). Defer until 089 results are in; if depth-2 ceiling story holds in 089 attribution, this gets prioritized for batch 092 cross-asset replication.

### 6.3 Mandatory citation + framing in §2 Related Work

TrajCast (NMI 2025) must be cited in §2 with an explicit positioning sentence:

> "Recent autoregressive equivariant approaches (TrajCast, Thiemann et al. 2025) learn integrator surrogates that bypass explicit force computation; ECoMD takes the complementary stance of exposing interpretable mechanism components for systematic ablation, trading rollout-length headroom for falsifiability of mechanism-class sufficiency claims."

Symmetry-group disclosure in §3 to pre-empt reviewer-2: ECoMD respects **permutation symmetry over agents**, not E(3) symmetry on Cartesian coordinates, because agents inhabit a learned latent feature space, not 3D physical space. This is a deliberate scope choice — equivariant networks designed for atomic geometry do not transfer here without violating the latent-space abstraction.

### 6.4 Out-of-scope for Paper A

- Adopting force-free black-box dynamics — kills the mechanism-decomposition contribution
- Lifting E(3) equivariance machinery — wrong symmetry group for our problem; reviewer-2 will catch the mismatch

---

## 7. References

- Plan: `~/.claude/plans/curried-cuddling-cloud.md`
- Branch F (088) analysis: `logs/2026-05-13.md` Sessions 1-2
- Falsification reframe origin: `logs/2026-05-13.md` Session 4 + `.claude/memory/project_paper_a_neurips_2027.md`
- Architectural floors documentation: `.claude/memory/project_arch_floors.md`
- Memory index: `.claude/memory/MEMORY.md`
- Original Paper A outline (ICAIF 2026, **superseded** by this plan): `papers/paper_a_methods/outline.md`
