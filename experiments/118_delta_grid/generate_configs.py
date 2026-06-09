"""Exp 118 — δ-grid extension: harden the per-asset hill(δ) line behind the δ*≈0.5 headline.

114's per-asset δ* fit (the δ where hill(δ) crosses 3, the empirical inverse-cubic) used only TWO
concave points {0.45, 0.50} — a 0.05-wide lever arm, so the fit is noise-dominated. The result:
spx 0.488 / gold 0.492 / btc 0.500 land on the TLB √-law value, but ndx 0.589 / eurusd 0.658
deviate, and we cannot tell deviation from fit noise. SPX already has 5 points (113: 0.40/0.50/
0.60/0.70 + 114: 0.45); this experiment gives every other asset the same 4-point arm by adding
δ ∈ {0.40, 0.60} → per-asset OLS hill(δ) lines and an honest universal-vs-asset-specific verdict
on the √-law crossing (the headline figure: 5 assets, one line each, crossing hill=3 at δ≈0.5).

Identical recipe to 113/114/115 (108 baseline_mmd base + rollout_reg_every=4) — results pool
directly with the existing cells in scripts/score_delta_grid.py.

Layout: per-asset SUBDIRS (each is an independent h20_run_phase/side_worker queue):
  experiments/118_delta_grid/{eurusd,ndx,btcusdt,gold}/config_s{SS}_{asset}_concave_d{040|060}.yaml

SEED-MAJOR file naming (s00_..d040, s00_..d060, s01_..d040, …): queues run configs in lexical
order, so a wall-clock cutoff leaves the two δ cells with BALANCED seed counts — partial queues
still yield usable fit points.

Where they run (2026-06-06 weekend window): eurusd → H20-2 (after exp 116); ndx then btcusdt →
H20-3; gold → H20-1 only on the G1-FAIL branch (see scripts/h20_sprint_driver.sh).
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "118_delta_grid"

REG_EVERY = 4
DELTAS = [0.40, 0.60]   # original 118 run; 2026-06-09 extension passes --deltas 0.35 0.55

# asset -> (target_dataset, target_period). spx added 2026-06-09 for the δ-grid extension
# (the original 118 omitted it since 113 already spans δ 0.40–0.70).
ASSETS = {
    "spx":     ("spx", "2015-2026_daily"),
    "ndx":     ("ndx", "2015-2026_daily"),
    "gold":    ("gold", "2015-2026_daily"),
    "eurusd":  ("eurusd", "2015-2026_daily"),
    "btcusdt": ("btcusdt", "2024Q1_1m"),
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--assets", nargs="+", default=list(ASSETS), choices=list(ASSETS))
    ap.add_argument("--deltas", nargs="+", type=float, default=DELTAS,
                    help="fixed δ values to emit (default the original 118 grid 0.40 0.60)")
    ap.add_argument("--seed-start", type=int, default=0)
    ap.add_argument("--seed-end", type=int, default=29)
    args = ap.parse_args()

    base = yaml.safe_load(BASE_PATH.read_text())
    n = 0
    for asset in args.assets:
        dataset, period = ASSETS[asset]
        adir = OUT / asset
        adir.mkdir(parents=True, exist_ok=True)
        for seed in range(args.seed_start, args.seed_end + 1):
            for delta in args.deltas:
                cfg = copy.deepcopy(base)
                cfg["training"]["seed"] = seed
                cfg["training"]["target_dataset"] = dataset
                cfg["training"]["target_period"] = period
                cfg["training"]["rollout_reg_every"] = REG_EVERY
                cfg["simulator"]["price_formation_kwargs"].update(
                    {"impact_concave_enabled": True, "impact_delta_init": delta,
                     "impact_delta_learnable": False})
                name = f"config_s{seed:02d}_{asset}_concave_d{round(delta * 100):03d}.yaml"
                (adir / name).write_text(yaml.safe_dump(cfg))
                n += 1

    est_h = n * 62 / 60
    print(f"wrote {n} configs under {OUT}/{{{','.join(args.assets)}}} "
          f"(seeds {args.seed_start}–{args.seed_end}, δ ∈ {args.deltas}, seed-major order)")
    print(f"  recipe: N={base['simulator']['n_agents']} {base['training']['mixed_precision']} "
          f"reg_every={REG_EVERY} (identical to 113/114/115)")
    print(f"  ≈ {est_h:.0f} card-hours total (~62 min/cfg incl eval)")


if __name__ == "__main__":
    main()
