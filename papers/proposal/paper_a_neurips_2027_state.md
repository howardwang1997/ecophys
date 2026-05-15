# Paper A — NeurIPS 2027 status (living document)

**Last updated**: 2026-05-14 (TrajCast review folded in; 089 still running on H20)
**Branch**: `feature/paper-a-neurips-2027`
**Plan**: `~/.claude/plans/curried-cuddling-cloud.md` (M1-M6, 8 wk each, → 2027-05 deadline)

This document is the single source of truth for what's done, what's launching,
and what H20 batches still need to be designed. Update in place as state changes;
see `logs/YYYY-MM-DD.md` for chronological history.

---

## TL;DR

- **Tonight (2026-05-13)**: launch **089 only** (mechanism-fact attribution, ~14h H20)
- **Tomorrow morning**: analyze with `score_attribution.py`, decide next H20 batch
- **Three H20 batches still need to be designed** before Paper A can submit: 094 (VaR holdout training), 095 (TimeGAN baseline), 091 (calibration-speed shootout)
- **Mac-side M1 modules are 4/6 done**: AR(1) + Zumbach mechanisms ✅, distributional metrics ✅, VaR module ✅; pending: TimeGAN baseline, calibration harness

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

## 2. Tonight (2026-05-13) — 089 attribution batch

**What it is**: 800 configs (16 cells × 50 seeds), clean leave-one-in single-mechanism cells. Output is the 10×11 mechanism × fact pass-rate matrix that becomes Paper A's Figure 1.

**Cells** (priority order via `CONFIG_ORDER_PREFIXES`):
1. `attr_baseline_v3` (control)
2. `attr_ar1_{s03,s05,s08}` — M1.1 dose-response (NEW mechanism, paper-critical)
3. `attr_zumbach_{s05,s10,s20,dn_s10}` — M1.2 dose-response (NEW mechanism + downside variant)
4. `attr_b3_k3` — Branch F best single (re-run at n=50 for consistency)
5. `attr_asymdrag_a06` — Branch D best single
6. `attr_levy_a17`, `attr_memk_l095_s10`, `attr_powerlaw_a15`, `attr_microstructure_r03`, `attr_inner_3`, `attr_jump_l01` — existing single mechanisms

**Wall**: ~14h on 8-card H20 (estimate from 088's 8.8 min/cfg rate). If process dies past 12h (Branch D failure mode), the paper-critical first ~550 cfg are already on disk.

**Launch commands**:
```bash
ssh h20 && cd ecophys
git fetch
git checkout feature/paper-a-neurips-2027
git pull
unset NPROC && bash scripts/h20_refresh_deps.sh
bash scripts/h20_paper_a_neurips_2027.sh --dry-run    # 8 preflight checks
DAEMON=1 bash scripts/h20_paper_a_neurips_2027.sh
tail -f experiments/_paper_a_neurips_*.log
```

**Tomorrow morning workflow**:
```bash
git pull   # on Mac
conda run -n ecophys python scripts/score_phase.py experiments/089_attribution_50seed
conda run -n ecophys python scripts/score_summary.py experiments/089_attribution_50seed
conda run -n ecophys python scripts/score_attribution.py experiments/089_attribution_50seed
# → experiments/089_attribution_50seed/{scoreboard,attribution_matrix}.{md,json}
```

---

## 3. Outstanding H20 batches — designed but generators NOT yet written

These are needed to finish Paper A's claims; we deferred them tonight per user direction (one batch at a time).

### 3.1 Batch 094 — VaR holdout training (M1.4 H20 component)

**Why we need it**: 089 trains on SPX `2015-2026_daily` (verified in `experiments/069_gamma_damping_30seed/config_T05_g10_seed0.yaml`). VaR backtest on 2018-2026 with those checkpoints would be **training-test overlap → information leakage**. Reviewer-2 will catch this immediately.

**What to design**: same 16-cell mechanism set as 089 but trained on SPX **2010-2017 only**, then VaR backtested on 2018-2026 cleanly held out. Suggest n=12 seeds per cell (we don't need 50 seeds for VaR, just enough for path-distribution stability).

| | value |
|---|---|
| cfgs | 16 cells × 12 seeds = 192 |
| H20 wall | ~3h (192 × 8.8min / 8 cards) |
| outputs | checkpoints for `EcoMDSampler` to load + 11-fact eval (sanity) |
| Mac-side downstream | `python -m ecomd.risk.var_backtest` rolling backtest on each checkpoint |

**Effort to ship**: ~2h Mac work — generator + tweak launcher to point at new dataset window.

### 3.2 Batch 095 — TimeGAN baseline (M1.5 H20 component)

**Why we need it**: reviewer-2 will demand a GAN-family baseline; GARCH alone isn't enough on the ML side. TimeGAN training on a single asset is GPU-heavy (~1-2h per fit on Mac); doing 5 assets × 5 seeds = 25 fits is a 25-50h Mac job, infeasible.

**What to design**: TimeGAN reference (Yoon 2019, or simplified WGAN-LP per Wiese 2020 QuantGAN — ~3× simpler with similar paper-quality story) trained on each of 5 assets (SPX, BTC, EURUSD, GOLD, NDX), 5 seeds each. **Bundle a TrajCast-style autoregressive surrogate into this same batch** — see §6 below; same H20 window, same 5-asset × 5-seed grid, ~+4h H20 wall.

| | value |
|---|---|
| cfgs | 5 assets × 5 seeds = 25 fits |
| H20 wall | ~10h (25 × ~3h per fit / 8 cards) |
| outputs | trained GAN checkpoints + sampled trajectories scored on the 11 facts |
| Mac-side downstream | per-fact score table + add to scoreboard alongside ECoMD/GARCH/LM/AR1+SV/GBM |

**Effort to ship**: ~6-8h Mac work — TimeGAN/WGAN-LP impl (~250 LoC) + sklearn-style fit/sample API + generator + launcher. Suggest WGAN-LP variant to bound complexity.

**Risk R6 fallback**: if TimeGAN implementation drags > 10h Mac, drop and cite Yoon 2019 + Wiese 2020 as "incomparable due to non-stationary financial returns vs synthetic time series" (per plan risk register).

### 3.3 Batch 091 — Calibration-speed shootout (M1.6 H20 component, **paper headline**)

**Why we need it**: this is the **headline downstream task** in the NeurIPS 2027 plan reframe. The claim "ECoMD calibrates ~100× faster than ABIDES+SBI at matched coverage" is what justifies the differentiability contribution.

**Pre-requisite**: ABIDES needs to be installed on H20. `pip install abides` works on most boxes but the SBI dependency (`pip install sbi`) often needs torch-CPU compatibility tweaks. Allow a 1-2h H20 install session before generator design.

**What to design**: uniform calibration harness that records wall-clock + n_iters + final fact coverage for:
- ECoMD: gradient descent (existing `ecomd/training/train_distributed.py`)
- ABIDES + SBI (Sequential Neural Posterior Estimation, NPE-C): forward simulation + posterior fit
- Lux-Marchesi + ABC (Approximate Bayesian Computation): rejection sampling

| | value |
|---|---|
| cfgs | ~50 calibration runs × 3 methods × 5 assets = 750 calibrations |
| H20 wall | ~15h (mostly ABIDES forward sims; ECoMD is the fast leg) |
| outputs | wall-clock × coverage tradeoff CSV + Pareto figure |
| Mac-side downstream | Figure 3 builder |

**Effort to ship**: ~4-6h Mac work + ~1-2h H20 ABIDES install verification — wallclock harness module (`ecomd/calibration/wallclock_harness.py`, ~200 LoC) + ABIDES wrapper + Lux-Marchesi calibration via existing `ecomd/baselines/lux_marchesi.py` + generator + launcher.

**Risk R3**: if ABIDES+SBI is faster than expected, even 10× advantage is publishable; below 10× → reframe to "capability difference" (ECoMD differentiable through training, SBI not).

---

## 4. Mac-side M1 progress (4/6 done)

| | module | status | reusable in 089 analysis? |
|---|---|---|---|
| ✅ M1.1 | AR(1) drift whitening (integrator) | committed | yes — config keys live |
| ✅ M1.2 | Zumbach causal-asymmetry (integrator) | committed | yes — config keys live |
| ✅ M1.3 | Distributional metrics (`ecomd/eval/distributional_metrics.py`) | committed | yes — wire into `score_continuous.py` next |
| ✅ M1.4 | VaR backtest (`ecomd/risk/`) | committed | needs **batch 094** for clean numbers |
| ⏳ M1.5 | TimeGAN baseline (`ecomd/baselines/timegan.py`) | not started | needs **batch 095** |
| ⏳ M1.6 | Calibration wall-clock harness (`ecomd/calibration/wallclock_harness.py`) | not started | needs **batch 091** + ABIDES install |

Plus M2 sub-tasks already shipped:
- ✅ M2.1 089 attribution batch generator + H20 launcher
- ✅ M2.2 `scripts/score_attribution.py` — auto-builds 10×11 attribution matrix

---

## 5. Decision queue

1. **After 089 lands** (tomorrow morning): does AR(1) whitening lift `autocorr_returns` pass-rate from baseline? Does Zumbach feedback ANY variant flip the sign of `zumbach_asymmetry`?
   - If **YES** to either → write 090 batch (compose patches with existing best singles/pairs).
   - If **NO** → that's the central falsification finding ("no Markovian mechanism class lifts these floors"), still publishable.
2. **Within 1 week**: write batch 094 (VaR holdout) generator + launcher. Run when next H20 window opens.
3. **Within 1 week**: add TrajCast (NMI 2025) citation + positioning paragraph to `papers/paper_a_methods/outline.md` §2 Related Work + clarify ECoMD's symmetry group (agent permutation, not E(3)) in §3 — see §7 below.
4. **Within 2 weeks**: decide TimeGAN vs WGAN-LP for M1.5; install ABIDES on H20 for M1.6.
5. **Within 4 weeks**: 095 (GAN + TrajCast-style baseline bundled) + 091 (calibration shootout) running.

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
