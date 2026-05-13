# Paper A — NeurIPS 2027 status (living document)

**Last updated**: 2026-05-13 evening
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

**What to design**: TimeGAN reference (Yoon 2019, or simplified WGAN-LP per Wiese 2020 QuantGAN — ~3× simpler with similar paper-quality story) trained on each of 5 assets (SPX, BTC, EURUSD, GOLD, NDX), 5 seeds each.

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
3. **Within 2 weeks**: decide TimeGAN vs WGAN-LP for M1.5; install ABIDES on H20 for M1.6.
4. **Within 4 weeks**: 095 (GAN baseline) + 091 (calibration shootout) running.

---

## 6. References

- Plan: `~/.claude/plans/curried-cuddling-cloud.md`
- Branch F (088) analysis: `logs/2026-05-13.md` Sessions 1-2
- Falsification reframe origin: `logs/2026-05-13.md` Session 4 + `.claude/memory/project_paper_a_neurips_2027.md`
- Architectural floors documentation: `.claude/memory/project_arch_floors.md`
- Memory index: `.claude/memory/MEMORY.md`
- Original Paper A outline (ICAIF 2026, **superseded** by this plan): `papers/paper_a_methods/outline.md`
