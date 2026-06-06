"""Exp 119 — champion 5-asset confirmation (the no-best-of-N gate after exp 115 G1).

Generates <winner cell> × {ndx, gold, eurusd, btcusdt} × n seeds. SPX is NOT regenerated — the
winner's SPX n=30 comes from exp 115 itself (identical recipe). Per-asset BASELINES are NOT
regenerated either: 113 (spx) and 114 (ndx/gold/eurusd/btcusdt) baselines share the exact recipe
(108 baseline_mmd base + rollout_reg_every=4, verified 2026-06-06), so the champion Welch tests
reuse them at n=29–30.

Pre-declared statistics (set BEFORE results exist, to kill gate-shopping):
  per asset: champion vs that asset's 113/114 baseline (Welch), Bonferroni m=5;
  vs SOTA 5.96: one-sample t on the pooled champion net (report regardless of significance —
  at n=30/cell a small exceedance over 5.96 may be ns; the paper then reports the point estimate
  with CI, NOT a "beats SOTA" claim).

The cell recipes are exp 115's (kept in sync by hand — 115 is frozen as of 2026-06-06).
Driver usage (scripts/h20_sprint_driver.sh picks the winner from score_composition --json):
  python experiments/119_champion_confirm/generate_configs.py --cell concave_sv_both --n-seeds 30

Seed-major file naming (config_s00_ndx_*.yaml, config_s00_gold_*.yaml, …) so a wall-clock cutoff
leaves assets with balanced seed counts.
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "119_champion_confirm"

REG_EVERY = 4

# == exp 115 cell recipes (mirror of experiments/115_composition/generate_configs.py) ==
CONCAVE = {"impact_concave_enabled": True, "impact_delta_init": 0.50,
           "impact_delta_learnable": False}
SV_BOTH = {"sv_price_enabled": True, "sv_d": 3, "sv_gain_init": 0.5, "sv_leverage": True,
           "sv_state_dep": False, "sv_v_clip": 3.0}
SV_NOLEV = {**SV_BOTH, "sv_leverage": False}
CELLS: dict[str, dict] = {
    "concave":           {**CONCAVE},
    "sv_both":           {**SV_BOTH},
    "concave_sv_both":   {**CONCAVE, **SV_BOTH},
    "concave_sv_nolev":  {**CONCAVE, **SV_NOLEV},
}

# asset -> (target_dataset, target_period); spx comes from exp 115 itself
ASSETS = {
    "ndx":     ("ndx", "2015-2026_daily"),
    "gold":    ("gold", "2015-2026_daily"),
    "eurusd":  ("eurusd", "2015-2026_daily"),
    "btcusdt": ("btcusdt", "2024Q1_1m"),
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cell", required=True, choices=list(CELLS),
                    help="winner cell from exp 115 (score_composition --json)")
    ap.add_argument("--n-seeds", type=int, default=30)
    ap.add_argument("--assets", nargs="+", default=list(ASSETS), choices=list(ASSETS))
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    base = yaml.safe_load(BASE_PATH.read_text())
    pf_over = CELLS[args.cell]
    n = 0
    for seed in range(args.n_seeds):
        for asset in args.assets:
            dataset, period = ASSETS[asset]
            cfg = copy.deepcopy(base)
            cfg["training"]["seed"] = seed
            cfg["training"]["target_dataset"] = dataset
            cfg["training"]["target_period"] = period
            cfg["training"]["rollout_reg_every"] = REG_EVERY
            cfg["simulator"]["price_formation_kwargs"].update(pf_over)
            (OUT / f"config_s{seed:02d}_{asset}_{args.cell}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1

    print(f"wrote {n} configs to {OUT} (cell={args.cell}, {len(args.assets)} assets × "
          f"{args.n_seeds} seeds, seed-major order)")
    print(f"  spx n=30 reused from 115; baselines reused from 113/114 (same recipe)")
    print(f"  ≈ {n * 62 / 60 / 8:.1f}h on 8 cards (~62 min/cfg incl eval)")


if __name__ == "__main__":
    main()
