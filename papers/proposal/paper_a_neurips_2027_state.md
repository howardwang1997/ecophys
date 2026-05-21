# Paper A — NeurIPS 2027 status (living document)

**Last updated**: 2026-05-21 (framing pivot: ceiling as motivation, not conclusion)
**Branch**: `feature/paper-a-neurips-2027`
**Plan**:
- `papers/proposal/paper_a_next_steps_2026-05-21.md` — **current** (Track A + B-β + B-α primary, B-γ + B-MACEv2 secondary, C fallback)
- `~/.claude/plans/089-099-humming-jellyfish.md` — superseded for framing, still authoritative for in-flight H20 batches (098b/098c/099b/095b)
- `~/.claude/plans/curried-cuddling-cloud.md` — mid-term M1-M6 (→ 2027-05 deadline)

This document is the single source of truth for what's done, what's launching,
and what H20 batches still need to be designed. Update in place as state changes;
see `logs/YYYY-MM-DD.md` for chronological history.

---

## TL;DR (2026-05-21 — framing pivot)

**Headline framing changed**: ceiling discovered in 089-099 (5-asset Pareto frontier
@ 5.5 / 11 in hand-crafted Markov family) is now **motivation**, not **conclusion**.

Paper A arc: **problem → diagnose → propose extensions that break ceiling → calibration-speed utility**.

Five "constructive solution" tracks (B-β + B-α primary parallel; B-γ + B-MACEv2 secondary; C fallback only):
- **Track A** — Memory kernels (memk via 099b, decision tomorrow)
- **Track B-β** — Scheduled-sampling depth-3 (1-1.5 wk, lowest risk)
- **Track B-α** — Hopfield regime attractors (2-3 wk, highest claim value)
- **Track B-γ** — Adversarial per-fact discriminator (3-4 wk, GAN risk)
- **Track B-MACEv2** — MACE-lite v2 with failure-aware fixes (2-3 wk, **canonical failure case**, pre-flight gated)
- **Track C** — Multi-objective Pareto (fallback only, requires 5/5 B-track failures)
- **Track D** — ABIDES+SBI calibration shootout (independent parallel, §7 utility)

**Target NeurIPS 2027 acceptance: 30–40%** (conditional on ≥2 of A/B-β/B-α succeeding at 5-asset mean ≥ 6.0).
M3 (arXiv) shifts Wk 28 → Wk 32; deadline Wk 60 leaves 28 wk buffer.

**Critical**: MACE-lite v1 is the canonical failure case (0-4/11 across 8 ablations,
2026-04-22). Any learned-potential work (B-MACEv2) requires explicit pre-flight gates
on force magnitude + unbiased graph topology. See `papers/proposal/paper_a_next_steps_2026-05-21.md` §7.

---

## TL;DR (2026-05-20)

- **5-asset rescore lands** (commit `84e5c871`): EURUSD + NDX from H20's `f65cdb0d`
  pushed today, now scored across 089b/091/092/093/095.
  - **`xa_gold_zumdn` = 5.96** (n=26) remains best single-mech cell across all batches.
  - **`xa_eurusd_zumdn` = 5.36** is the second-strongest single-mech result — adds
    a third "zumdn is best" asset to the Gold/SPX pair.
  - **No EURUSD/NDX cell exceeds 5.5** — Pareto ceiling cross-asset confirmed.
  - 091 calibration leg: `calib_eurusd_b80 = 8.50 (n=2!)`, `calib_ndx_b80 = 8.00 (n=2!)`
    — note: calibrated cells use a fit loss, not the falsification setting; high
    fact-pass is a positive C3a/C3b headline, NOT a Pareto breach.
- **Figure 1 v1 lands**: `papers/paper_a_methods/figures/fig1_attribution.{py,pdf,png}`.
  Two-panel from 089: (a) 16×11 attribution heatmap, (b) per-fact biggest-mover bar.
- **H20 day-shift 098b launching** (`scripts/h20_098b_dayshift.sh`, ~3h, 240 cfg):
  8 trimmed zumdn (s, λ) cells × 30 seeds. Confirms or kills the noisy 098 top
  `zumdn_s075_lam095=6.67 at n=3`.
- **H20 overnight launching** (`scripts/h20_overnight_2026-05-20.sh`, ~9h, 520 cfg):
  099b memk_n30 (270 cfg) + 095b baselines_n30 (250 cfg). Lifts C3b confidence
  from preliminary (n=5 max=6) to confident (n=30).
- **Supabase catalog reconcile**: running on Mac (`checkpoint_sync sync` against
  R2 + Supabase). H20's `f65cdb0d` re-introduced 6861 checkpoint.pt files into
  git tree — `experiments/**/results_*/*.pt` added to .gitignore for future
  protection; existing tracked .pt files need separate filter-repo cleanup.

---

## Earlier TL;DR (2026-05-15)

- **089 attribution batch landed** (796/800, commit `321633ba`): `attr_zumbach_dn_s10` is best single mech (mean **5.12**, +0.31 vs baseline, only 2/50 rej). **Both floors lifted by single mechanisms** but with collateral tradeoffs → falsification reframes from "absolute" to "Pareto-bounded".
- **3-day batch (2026-05-15 PM → 2026-05-18 PM, ~50h H20 wall)**: 14 sub-batches totaling 3026 cfg. Original five (090/090b/094/091/095) + four bonus phases (090c/090d/092/089b) + five Tier-1/2 closeouts (096 all-pairs, 097 n_agents scaling, 098 Zumbach refinement, 099 memk refinement, 093 traditional baselines).
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

### 2.2 Falsification claim — Pareto-bounded (CONFIRMED 5-asset 2026-05-20)

Old (pre-089): "two facts are architecturally impossible in v3" — too strong, **not survived**.
Provisional (post-089 SPX-only): **"the 11 facts form a Pareto frontier no single mechanism crosses simultaneously."**
CONFIRMED (post-rescore 089b 5-asset, 092 5-asset, 096 all-pairs): same pattern reproduces across
all 5 assets and all 23 pair combinations. No SPX/BTC/Gold/EURUSD/NDX cell at n≥26 reaches mean ≥ 5.5;
best per asset: Gold zumdn 5.96, EURUSD zumdn 5.36, SPX zumdn 5.24, BTC b3 5.10, NDX pair_zumdn_b3 5.18.

Every cell that lifts a floor breaks ≥1 other fact by ≥20pp. Specifically:
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
| 10 | **096 all-pairs interaction matrix** | 690 | 12h | **Pareto-impossibility evidence** |
| 11 | 097 n_agents scaling ablation | 90 | 2h | rebut "ceiling is N-dependent" attack |
| 12 | 098 Zumbach `dn` strength × λ refinement | 100 | 1.5h | SOTA dose-response surface |
| 13 | 099 memk strength × λ refinement | 100 | 1.5h | rule out missed memk operating point |
| 14 | 093 GARCH/GBM/AR1+SV/LM 5-asset baselines | 100 | 0.5h (CPU) | M3 baseline table close |
| | **TOTAL** | **3026** | **~50h** | |

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
