"""095 — WGAN-LP + TrajCast-lite baselines on 5 assets (M1.5 H20 batch).

Trains the two new baselines (WGAN-LP per Wiese 2020 QuantGAN; TrajCast-
lite per Thiemann 2025) on each of 5 assets × 5 seeds. Each cell is one
(asset, model, seed) triple. The runner is
`scripts/run_baseline_fit_eval.py` which fits, samples 4 rollouts of 2520
steps, scores on the 11 Cont facts, and writes the standard
`inference_merged.json` so `score_phase.py` and `score_attribution.py`
consume it unchanged.

Cells (10 model×asset combos × 5 seeds = 50 cfg, ~7h H20 total):
  baseline_wgan_{spx,btc,eurusd,gold,ndx}_seed{0..4}
  baseline_trajcast_{spx,btc,eurusd,gold,ndx}_seed{0..4}

Per-cfg wall: WGAN-LP ~8-12min (200 epochs); TrajCast-lite ~6-10min (100
epochs). On 8-card H20 with parallelism, full batch finishes well under
the weekend window.

Note: SPX/EURUSD/GOLD use `daily` period (full history). BTC uses the
1m crypto path (`btcusdt` with `2024Q1_1m`). NDX needs the
`_YFINANCE_DAILY_SYMBOL` registry to include it — added by this batch.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "experiments" / "095_baseline_5asset_5seed"
OUT.mkdir(parents=True, exist_ok=True)


# Per-asset config — period field, etc.
ASSET_PERIOD = {
    "spx":      "daily",
    "btcusdt":  "2024Q1_1m",
    "eurusd":   "daily",
    "gold":     "daily",
    "ndx":      "daily",
}


# Per-model defaults
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


# Template: minimum required fields for `train_distributed.py` schema
# compatibility, even though we don't actually train ECoMD here — the
# launcher pipeline expects each config to be valid YAML with these keys.
TEMPLATE = {
    "simulator": {},  # ignored by baseline runner
    "training": {"seed": 0},
}


def main() -> None:
    n = 0
    n_cells = 0
    for model in ("wgan_lp", "trajcast_lite"):
        defaults = MODEL_DEFAULTS[model]
        for asset, period in ASSET_PERIOD.items():
            model_tag = "wgan" if model == "wgan_lp" else "trajcast"
            tag = f"baseline_{model_tag}_{asset}"
            n_cells += 1
            for seed in range(5):
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
    print(f"wrote {n} configs across {n_cells} cells to {OUT}")


if __name__ == "__main__":
    main()
