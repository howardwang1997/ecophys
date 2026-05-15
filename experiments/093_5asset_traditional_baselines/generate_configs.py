"""093 — 5-asset traditional baselines (M3 milestone, closes baseline table).

Runs GARCH(1,1), GBM, AR1+SV, Lux-Marchesi on all 5 assets × 5 seeds.
Together with 095 (WGAN-LP + TrajCast-lite), this gives the complete
§5 baseline table — 6 baselines × 5 assets × 5 seeds.

These baselines are CPU-cheap (no neural network training), so per-cell
wall is ~30s on CPU. Even at 8-way parallel, the whole batch finishes
in a few minutes; we schedule on H20 just to keep everything in one
pipeline for `score_attribution.py` consumption.

Cells (4 models × 5 assets × 5 seeds = 100 cfg, ~0.5h H20):

  GARCH(1,1) Student-t fit:
    trad_garch_{spx,btcusdt,eurusd,gold,ndx}_seed{0..4}

  Geometric Brownian Motion (μ + σ·z, fitted):
    trad_gbm_{...}_seed{...}

  AR(1) + Stochastic Volatility:
    trad_ar1sv_{...}_seed{...}

  Lux-Marchesi 1999 (default parameters):
    trad_lm_{...}_seed{...}
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "experiments" / "093_5asset_traditional_baselines"
OUT.mkdir(parents=True, exist_ok=True)

ASSET_PERIOD = {
    "spx":     "daily",
    "btcusdt": "2024Q1_1m",
    "eurusd":  "daily",
    "gold":    "daily",
    "ndx":     "daily",
}

MODELS = [
    ("garch", "garch", {"dist": "t", "rescale_to_percent": True}),
    ("gbm",   "gbm",   {}),
    ("ar1sv", "ar1sv", {}),
    ("lm",    "lux_marchesi", {}),
]

TEMPLATE = {
    "simulator": {},  # ignored by traditional runner
    "training": {"seed": 0},
}


def main() -> None:
    n = 0
    n_cells = 0
    for tag_short, model_name, fit_kwargs in MODELS:
        for asset, period in ASSET_PERIOD.items():
            tag = f"trad_{tag_short}_{asset}"
            n_cells += 1
            for seed in range(5):
                cfg = copy.deepcopy(TEMPLATE)
                cfg["training"]["seed"] = seed
                cfg["traditional"] = {
                    "model": model_name,
                    "asset": asset,
                    "period": period,
                    "n_paths": 4,
                    "n_steps_per_path": 2520,
                }
                if fit_kwargs and model_name != "lux_marchesi":
                    cfg["traditional"]["fit_kwargs"] = fit_kwargs
                (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
                n += 1
    print(f"wrote {n} configs across {n_cells} cells to {OUT}")


if __name__ == "__main__":
    main()
