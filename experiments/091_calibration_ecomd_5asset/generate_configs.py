"""091 — ECoMD calibration-speed shootout, ECoMD leg only (M1.6 weekend half).

Wall-clock × coverage tradeoff for ECoMD across 5 assets at 3 n_iters
budgets × 2 seeds. After the batch, `wallclock_harness.analyze_*` builds
the Pareto frontier per asset.

Cells (5 assets × 3 budgets × 2 seeds = 30 cfg, ~3h H20):

  Per asset {spx, btcusdt, eurusd, gold, ndx}:
    calib_<asset>_b40    n_iters=40
    calib_<asset>_b80    n_iters=80
    calib_<asset>_b160   n_iters=160

The headline claim "≤100 gradient iterations matches reasonable coverage"
is checked at b40/b80 vs the full-budget b160 reference. Once ABIDES+SBI
leg lands (next weekend, blocked on H20 install), append its data points
to the same Pareto plot.

We use the best post-089 single mechanism (zumbach_dn_s10) so each
calibration represents a realistic paper-grade target. Seeds × asset
gives within-run variance.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "091_calibration_ecomd_5asset"
OUT.mkdir(parents=True, exist_ok=True)

ASSETS = ["spx", "btcusdt", "eurusd", "gold", "ndx"]
ASSET_PERIOD = {
    "spx":     "daily",
    "btcusdt": "2024Q1_1m",
    "eurusd":  "daily",
    "gold":    "daily",
    "ndx":     "daily",
}
BUDGETS = [40, 80, 160]
SEEDS = [0, 1]


def apply_zumbach_dn(cfg):
    cfg["simulator"]["zumbach_feedback_lambda"] = 0.95
    cfg["simulator"]["zumbach_feedback_strength"] = 1.0
    cfg["simulator"]["zumbach_feedback_mode"] = "downside"


def main() -> None:
    base_spx = yaml.safe_load(BASE_SPX.read_text())
    n = 0
    for asset in ASSETS:
        for budget in BUDGETS:
            for seed in SEEDS:
                cfg = copy.deepcopy(base_spx)
                apply_zumbach_dn(cfg)
                cfg["training"]["seed"] = seed
                cfg["training"]["n_iters"] = budget
                cfg["training"]["target_dataset"] = asset
                cfg["training"]["target_period"] = ASSET_PERIOD[asset]
                tag = f"calib_{asset}_b{budget}"
                (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
                n += 1
    print(f"wrote {n} configs to {OUT} ({len(ASSETS)} assets × {len(BUDGETS)} budgets × {len(SEEDS)} seeds)")


if __name__ == "__main__":
    main()
