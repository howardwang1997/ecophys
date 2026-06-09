# Paper A week — H20 fleet launch runbook (2026-06-09)

Pre-registration (frozen BEFORE these runs): `papers/proposal/prereg_2026-06-09_power_topup_and_delta_grid.md`.
First push these Mac-built generators/scripts, then on each machine:
`git fetch && git checkout feature/exp113-gabaix-solve && git pull`.

Honest Paper A spine after the weekend sprint: **diagnose (3-paradigm ceiling) + concave-impact
solve + δ\*≈0.5 universality**. SOTA-break (G1) and SV-composition method are DEAD (115/119) — do
NOT re-chase them.

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

## H20-4 (CPU) — ABIDES timescale-fair daily re-run (parallel, all week, no GPU contention)

```bash
MODE=daily N_SEEDS=250 ABIDES_ENV=abides bash scripts/h20_abides_baseline.sh
# → writes experiments/105_abides_ceiling/results_rmsc03_*_daily/, auto-drops volume_volatility_corr.
# N_SEEDS=250 = 250 daily returns/cell (each sim = one close-to-close return); raise for more power.
```

---

## Scoring (Mac, after `git pull` of results)

```bash
python scripts/score_delta_grid.py                                      # δ* per-asset OLS + CI, 5-asset universality verdict
python scripts/score_concave_confirm.py experiments/114_concave_confirm # strict per-asset gate at n=60
python scripts/score_surrogate_kill.py                                  # rigor (currently SURVIVES 7/11 > GARCH 5/11)
python scripts/assemble_frontier.py                                     # 3-paradigm figure (auto-uses ABIDES _daily once present)
```
For 117: per-fact leverage pass-rate of each cell vs `concave_only` (collateral on hill/acf²/agg).

Frontier finalization TODO: replace the `EcoMD zumdn (best net)` row in `assemble_frontier.py`
SOURCES with the actual 5.96 SOTA cell (092/098 gold), and the ABIDES row auto-upgrades to `_daily`.
