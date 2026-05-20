"""095b — WGAN-LP + TrajCast-lite baselines at n=30 (overnight follow-up to 095 n=5).

095 ran 2 models × 5 assets × 5 seeds with max≤6 on every cell. C3b "ECoMD
≥ modern surrogates" rests on this comparison being statistically firm —
n=5 isn't enough. 095b extends each cell to n=30 by adding seeds 5-29.

Cells (2 × 5 × 25 = 250 cfg ≈ 3-4h on 8-card H20):
  baseline_wgan_{spx,btcusdt,eurusd,gold,ndx}_seed{5..29}
  baseline_trajcast_{spx,btcusdt,eurusd,gold,ndx}_seed{5..29}
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "experiments" / "095b_baselines_n30"
OUT.mkdir(parents=True, exist_ok=True)


ASSET_PERIOD = {
    "spx":      "daily",
    "btcusdt":  "2024Q1_1m",
    "eurusd":   "daily",
    "gold":     "daily",
    "ndx":      "daily",
}


MODEL_DEFAULTS = {
    "wgan_lp": {
        "model_kwargs": {"window": 64, "latent_dim": 16, "hidden": 32},
        "fit_kwargs":   {"n_epochs": 200, "batch_size": 128, "n_critic": 5, "lr": 1e-4},
    },
    "trajcast_lite": {
        "model_kwargs": {"context": 64, "hidden": 64, "n_layers": 2, "n_heads": 4},
        "fit_kwargs":   {"n_epochs": 100, "batch_size": 256, "lr": 3e-4},
    },
}

TEMPLATE = {
    "simulator": {},
    "training": {"seed": 0},
}

SEED_RANGE = range(5, 30)


def main() -> None:
    n = 0
    n_cells = 0
    for model in ("wgan_lp", "trajcast_lite"):
        defaults = MODEL_DEFAULTS[model]
        for asset, period in ASSET_PERIOD.items():
            model_tag = "wgan" if model == "wgan_lp" else "trajcast"
            tag = f"baseline_{model_tag}_{asset}"
            n_cells += 1
            for seed in SEED_RANGE:
                cfg = copy.deepcopy(TEMPLATE)
                cfg["training"]["seed"] = seed
                cfg["baseline"] = {
                    "model": model,
                    "asset": asset,
                    "period": period,
                    "n_rollouts": 4,
                    "n_steps_per_rollout": 2520,
                    "model_kwargs": defaults["model_kwargs"],
                    "fit_kwargs": defaults["fit_kwargs"],
                }
                (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
                n += 1
    print(f"wrote {n} configs across {n_cells} cells (seeds {min(SEED_RANGE)}..{max(SEED_RANGE)}) to {OUT}")


if __name__ == "__main__":
    main()
