"""098D — Why did 098B regress from 092? Asset × Zumbach-mode 2×3 ablation.

Diagnostic for Paper A §3 "diagnose" narrative. 098B (single-asset SPX,
zumbach mode=downside) gave 5.59/11 at n=30 — a regression from 092's
xa_gold_zumdn 5.96 (cross-asset average). The 0.37-fact gap might be due to:

(a) **Single-asset bottleneck**: training only on SPX daily limits the
    regime diversity the model is exposed to.
(b) **Downside-only Zumbach feedback**: restricts the leverage-effect
    channel to negative returns, missing symmetric volatility clustering.

098D crosses these two axes:

| Asset       | Mode      | Cell tag             |
|-------------|-----------|----------------------|
| spx         | none      | spx_zum_none         |
| spx         | abs       | spx_zum_abs          |
| spx         | downside  | spx_zum_downside     | ← 098B reference
| joint_5     | none      | x5_zum_none          |
| joint_5     | abs       | x5_zum_abs           |
| joint_5     | downside  | x5_zum_downside      |

joint_5 = simultaneous matching of {spx daily, btcusdt 1m, eurusd daily,
gold daily, ndx daily} via train_cfg.joint_assets (single model, five
target distributions, weighted-sum loss). NOTE: this differs from 092's
"cross-5" which is the *aggregate across 5 specialist models* — but the
diagnostic question ("does adding asset diversity help?") is sharper with
joint_assets because it isolates the diversity effect from the
seed-lottery noise of 5 separate models.

6 cells × 30 seeds = 180 configs ≈ 3.7h on 8-card H20.

Zumbach hyperparameters (s, λ) match the 098B winner (s=0.75, λ=0.95) so
the "mode" axis is the only variable when comparing cells. Mode=none
disables zumbach entirely.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "099b_memk_refinement_n30" / "config_baseline_v3_seed0.yaml"
OUT = REPO / "experiments" / "098d_asset_mode_n30"
OUT.mkdir(parents=True, exist_ok=True)


JOINT_5_ASSETS = [
    {"dataset": "spx",      "period": "2015-2026_daily", "weight": 1.0},
    {"dataset": "btcusdt",  "period": "2024Q1_1m",       "weight": 1.0},
    {"dataset": "eurusd",   "period": "daily",           "weight": 1.0},
    {"dataset": "gold",     "period": "daily",           "weight": 1.0},
    {"dataset": "ndx",      "period": "daily",           "weight": 1.0},
]

# 098B winner cell hyperparams (zumdn_s075_lam095, mean 5.59 at n=30)
ZUM_S = 0.75
ZUM_LAM = 0.95

# (asset_tag, mode) tuples — 6 cells total
CELLS = [
    ("spx", "none"),
    ("spx", "abs"),
    ("spx", "downside"),
    ("x5",  "none"),
    ("x5",  "abs"),
    ("x5",  "downside"),
]

N_SEEDS = 30


def _apply_asset(cfg: dict, asset_tag: str) -> None:
    if asset_tag == "spx":
        cfg["training"]["target_dataset"] = "spx"
        cfg["training"]["target_period"] = "2015-2026_daily"
        cfg["training"].pop("joint_assets", None)
    elif asset_tag == "x5":
        cfg["training"]["joint_assets"] = copy.deepcopy(JOINT_5_ASSETS)
        cfg["training"].pop("target_dataset", None)
        cfg["training"].pop("target_period", None)
    else:
        raise ValueError(f"unknown asset_tag {asset_tag!r}")


def _apply_mode(cfg: dict, mode: str) -> None:
    sim = cfg["simulator"]
    if mode == "none":
        for k in ("zumbach_feedback_lambda", "zumbach_feedback_strength",
                  "zumbach_feedback_mode"):
            sim.pop(k, None)
    elif mode in ("abs", "downside"):
        sim["zumbach_feedback_lambda"] = ZUM_LAM
        sim["zumbach_feedback_strength"] = ZUM_S
        sim["zumbach_feedback_mode"] = mode
    else:
        raise ValueError(f"unknown mode {mode!r}")


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    n = 0
    for asset_tag, mode in CELLS:
        cell_tag = f"{asset_tag}_zum_{mode}"
        for seed in range(N_SEEDS):
            cfg = copy.deepcopy(base)
            _apply_asset(cfg, asset_tag)
            _apply_mode(cfg, mode)
            cfg["training"]["seed"] = seed
            out_path = OUT / f"config_{cell_tag}_seed{seed}.yaml"
            out_path.write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs across {len(CELLS)} cells × {N_SEEDS} seeds to {OUT}")


if __name__ == "__main__":
    main()
