# Paper A week — H20 fleet launch runbook (2026-06-09)

Pre-registration (frozen BEFORE these runs): `papers/proposal/prereg_2026-06-09_power_topup_and_delta_grid.md`.
First push these Mac-built generators/scripts, then on each machine:
`git fetch && git checkout feature/exp113-gabaix-solve && git pull`.

Honest Paper A spine after the weekend sprint: **diagnose (3-paradigm ceiling) + concave-impact
solve + δ\*≈0.5 universality**. SOTA-break (G1) and SV-composition method are DEAD (115/119) — do
NOT re-chase them.

---

## Step 0 — data prereq (R2): confirm all 5 assets are pullable

Training data is gitignored; the canonical store is **R2** (H20 pulls via `h20_pull_from_r2.sh`,
**not** git). **2026-06-09: spx (`^GSPC`) and btc (`BTCUSDT` 1m) were MISSING from R2 `raw/` and
have now been uploaded** (ndx/gold/eurusd were already there — this was the latent cause of the
weekend "btc 0/60"; any clean clone pulling from R2 would also have missed spx). On each H20 box,
after the git pull:

```bash
bash scripts/h20_pull_from_r2.sh raw          # pull raw/ into the NFS canonical store
# confirm all 5 assets load (each must print a non-trivial count):
for a in spx ndx gold eurusd; do conda run -n ecophys python -c "from pathlib import Path; from ecomd.training.train_distributed import load_real_returns as L; print('$a', L(Path('.'),'$a','2015-2026_daily').size)"; done
conda run -n ecophys python -c "from pathlib import Path; from ecomd.training.train_distributed import load_real_returns as L; print('btc', L(Path('.'),'btcusdt','2024Q1_1m').size)"
```
If anything errors, re-upload from a machine that has the parquet + `.env.r2`:
`conda run -n ecophys python -m ecomd.data.r2_sync upload data/raw/binance/market=spot/interval=1m/symbol=BTCUSDT raw/binance/market=spot/interval=1m/symbol=BTCUSDT`

---

## H20-1 (8 cards) — GPU · ~540 cfg ≈ 2.8 d (split (A1/A2) onto H20-2/3 to halve)

```bash
# (A) δ-grid extension → ≥6 δ points/asset, tight per-asset δ* CI   [360 cfg]
python experiments/118_delta_grid/generate_configs.py --assets btcusdt --deltas 0.35 0.40 0.55 0.60 --seed-start 0 --seed-end 29
python experiments/118_delta_grid/generate_configs.py --assets ndx gold eurusd spx --deltas 0.35 0.55 --seed-start 0 --seed-end 29
for a in btcusdt ndx gold eurusd spx; do PARALLEL=8 bash scripts/h20_run_phase.sh experiments/118_delta_grid/$a; done

# (B) power top-up n=30→60 on the 3 power-limited assets   [180 cfg]
python experiments/114_concave_confirm/generate_configs.py --assets ndx gold eurusd --cells baseline concave_d050 --seed-start 30 --seed-end 59
PARALLEL=8 bash scripts/h20_run_phase.sh experiments/114_concave_confirm
```

## H20-2 or H20-3 (2 cards) — 117 leverage 2nd-mechanism sweep (timeboxed)

```bash
python experiments/117_leverage/generate_configs.py --assets spx --n-seeds 20   # 120 cfg ≈ 0.6 d
PARALLEL=2 bash scripts/h20_run_phase.sh experiments/117_leverage
```
NB: concave_d050 already passes leverage (-0.98 mean, n=30) — this sweep tests whether asym_drag /
zumbach-downside raise the per-seed leverage **pass-rate** WITHOUT undoing hill/acf². If no cell
beats concave_only on pass-rate without collateral, drop per pre-registration → single-mechanism.

## S6 across-regime held-out (sanity rigor) — ~240 cfg ≈ 1.25 d, any free GPU slot

Answers reviewer-2's "did you overfit the 2015–2026 window?": train baseline + concave_d050 on two
disjoint regimes (2015-2020 incl. COVID, 2021-2026 incl. 2022 drawdown) and check the solve holds +
is consistent in BOTH. btc excluded (2024Q1 = 3 months, too short to split).
```bash
python experiments/121_heldout_regime/generate_configs.py --assets spx ndx gold eurusd --n-seeds 15
for r in r1 r2; do PARALLEL=8 bash scripts/h20_run_phase.sh experiments/121_heldout_regime/$r; done
```

## H20-4 (CPU) — ABIDES timescale-fair daily re-run (parallel, all week, no GPU contention)

**One-time env setup** (the scripts do NOT install ABIDES). The calibrate heredoc imports the
**JPMC ABIDES v1** module layout (`Kernel`, `agent.ExchangeAgent`, `agent.NoiseAgent`,
`agent.market_makers.AdaptiveMarketMakerAgent`, `util.oracle.SparseMeanRevertingOracle`,
`model.LatencyModel`) — this is the ORIGINAL abides (github.com/abides-sim/abides), **NOT
`abides-markets`** (the `paper_a_next_steps_2026-05-21.md` D.1 note saying `pip install
abides-markets` is **stale** — abides-markets has a different `abides_markets.*` API the scripts
don't use):
```bash
conda create -n abides python=3.10 -y && conda activate abides
pip install numpy pandas                                       # abides v1's only hard deps for rmsc03
git clone https://github.com/abides-sim/abides.git ~/abides    # provides agent/ util/ model/ Kernel.py
# the heredoc imports these at top level → put the repo ROOT on PYTHONPATH (persist in the env):
export PYTHONPATH=$HOME/abides:$PYTHONPATH
```

**Run** (daily, timescale-fair):
```bash
MODE=daily N_SEEDS=250 ABIDES_ENV=abides PYTHONPATH=$HOME/abides bash scripts/h20_abides_baseline.sh
# → writes experiments/105_abides_ceiling/results_rmsc03_*_daily/, auto-drops volume_volatility_corr.
# N_SEEDS=250 = 250 daily returns/cell (each sim = one close-to-close return); raise for more power.
```
**Or orchestrate from H20 onto a side CPU box** (keeps the H20 GPUs on training):
```bash
export ABIDES_HOST=<side-box-ip>           # only required setting; box needs the same abides env + repo clone
bash scripts/h20_abides_remote.sh launch   # rsync runner + nohup P parallel shards
bash scripts/h20_abides_remote.sh status   # tail remote progress
bash scripts/h20_abides_remote.sh fetch    # pull CSVs back + score daily on H20
```

---

## Scoring (Mac, after `git pull` of results)

```bash
python scripts/score_delta_grid.py                                      # δ* per-asset OLS + CI, 5-asset universality verdict
python scripts/score_concave_confirm.py experiments/114_concave_confirm # strict per-asset gate at n=60
python scripts/score_surrogate_kill.py                                  # rigor (currently SURVIVES 7/11 > GARCH 5/11)
python scripts/assemble_frontier.py                                     # 3-paradigm figure (auto-uses ABIDES _daily once present)
# S6 across-regime: score each regime subdir separately, then compare (solve must hold + be consistent)
for r in r1 r2; do python scripts/score_concave_confirm.py experiments/121_heldout_regime/$r; done
```
For 117: per-fact leverage pass-rate of each cell vs `concave_only` (collateral on hill/acf²/agg).
For S6: concave_d050 must pass hill∈[2,4] AND acf²∈[.15,.55] vs its baseline in BOTH regimes, with
consistent hill (|Δhill| small r1↔r2) → time-universal, not a window artifact.

Frontier finalization TODO: replace the `EcoMD zumdn (best net)` row in `assemble_frontier.py`
SOURCES with the actual 5.96 SOTA cell (092/098 gold), and the ABIDES row auto-upgrades to `_daily`.
