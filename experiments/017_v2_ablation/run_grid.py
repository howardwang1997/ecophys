"""Grid ablation runner for EcoMD v2.

Reads a grid YAML file that points at a base config and specifies per-knob
value lists. Expands the Cartesian product into N concrete configs, runs
each sequentially, and writes a summary table.

Usage:
    # Mac quick-tune (15-20 runs, ~30 min):
    conda run -n ecophys python experiments/017_v2_ablation/run_grid.py \\
        --grid experiments/017_v2_ablation/grid_mac_quick.yaml

    # H20 full (50+ runs, several hours — should be launched via DDP):
    torchrun --nproc_per_node=4 --standalone \\
        experiments/017_v2_ablation/run_grid.py \\
        --grid experiments/017_v2_ablation/grid_h20_full.yaml

Grid YAML format:
    base_config: base_config.yaml     # path relative to the grid file
    grid:
      simulator.v2_kyle_lambda_init: [0.05, 0.5, 2.0]
      training.loss_weights.w_acf_shape: [0.0, 0.5]
    skip_when:                         # optional: configs to exclude
      - simulator.v2_kyle_lambda_init: 2.0
        simulator.v2_phi_init_gain: 3.0
    variant_template: "λ{simulator.v2_kyle_lambda_init}"
"""

from __future__ import annotations

import argparse
import copy
import itertools
import json
import logging
import os
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import yaml

from ecomd.eval.acf_shape import acf_shape_loss, acf_squared_per_lag, ljung_box_stat
from ecomd.eval.stylized_facts import compute_all, log_returns_from_prices
from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.training.losses import LossWeights, build_targets_from_returns
from ecomd.training.train import train_ecomd

log = logging.getLogger("v2_grid")

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RAW_DIR = Path(os.environ.get("ECOPHYS_DATA_DIR", str(REPO / "data" / "raw")))


# ─── Dotted-key utilities ──────────────────────────────────────────────────


def _set_dotted(cfg: dict, key: str, value: Any) -> None:
    parts = key.split(".")
    d = cfg
    for k in parts[:-1]:
        if k not in d or not isinstance(d[k], dict):
            d[k] = {}
        d = d[k]
    d[parts[-1]] = value


def _get_dotted(cfg: dict, key: str) -> Any:
    d = cfg
    for k in key.split("."):
        d = d[k]
    return d


def _expand_grid(grid_spec: dict[str, list], skip_when: list[dict]) -> list[dict]:
    """Return a list of {dotted-key: value} assignments, after pruning skip_when."""
    keys = list(grid_spec.keys())
    value_lists = [grid_spec[k] for k in keys]
    assignments = []
    for combo in itertools.product(*value_lists):
        a = dict(zip(keys, combo))
        skipped = False
        for skip in skip_when or []:
            if all(a.get(k) == v for k, v in skip.items()):
                skipped = True
                break
        if not skipped:
            assignments.append(a)
    return assignments


def _variant_name(template: str, assignment: dict) -> str:
    name = template
    for key, val in assignment.items():
        ph = "{" + key + "}"
        if ph in name:
            if isinstance(val, float):
                val_str = f"{val:.2g}"
            else:
                val_str = str(val)
            name = name.replace(ph, val_str)
    # Sanitize for filesystem
    return (name.replace("/", "_").replace(" ", "_")
                .replace(":", "_").replace(".", "p"))


# ─── Data loading (reuses cross-asset dispatch) ────────────────────────────


def _load_returns(dataset: str, period: str) -> np.ndarray:
    if dataset == "spx" and period == "2015-2026_daily":
        root = RAW_DIR / "yfinance" / "interval=1d" / "symbol=^GSPC"
        frames = [pd.read_parquet(p) for p in sorted(root.glob("year=*.parquet"))]
        df = pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)
        col = "adjusted_close" if "adjusted_close" in df.columns else "close"
        return log_returns_from_prices(df[col].to_numpy())
    if dataset == "btcusdt" and period == "2024Q1_1m":
        root = RAW_DIR / "binance" / "market=spot" / "interval=1m" / "symbol=BTCUSDT" / "year=2024"
        frames = [pd.read_parquet(p) for p in sorted(root.glob("month=*.parquet"))]
        df = pd.concat(frames, ignore_index=True).sort_values("open_time").reset_index(drop=True)
        return log_returns_from_prices(df["close"].to_numpy())
    raise ValueError(f"unknown {dataset}/{period}")


# ─── 11-fact rule ──────────────────────────────────────────────────────────


FACT_RULES = [
    ("#1 ACF(r)",       "autocorr_returns",          lambda m: abs(m) < 0.08),
    ("#2 α Hill",       "hill_tail_index",           lambda m: 2.0 <= m <= 6.0),
    ("#3 skew",         "gain_loss_asymmetry",       lambda m: m < -0.05),
    ("#4 Δκ agg",       "aggregational_gaussianity", lambda m: m > 0),
    ("#5 Fano",         "intermittency_fano",        lambda m: m > 1.0),
    ("#6 ⟨ACF(r²)⟩",    "acf_squared_returns",       lambda m: m > 0.05),
    ("#7 κ GARCH-std",  "conditional_kurtosis",      lambda m: abs(m) < 3.0),
    ("#8 H DFA|r|",     "dfa_hurst_abs_r",           lambda m: 0.50 <= m <= 0.85),
    ("#9 ΣLev",         "leverage_effect",           lambda m: m < -0.05),
    ("#10 corr(V,|r|)", "volume_volatility_corr",    lambda m: m > 0.1),
    ("#11 Zumbach D",   "zumbach_asymmetry",         lambda m: m > 0.01),
]


def _score_facts(aggregated: dict) -> tuple[int, list[bool]]:
    marks = []
    for _, key, rule in FACT_RULES:
        m = (aggregated.get(key) or {}).get("mean")
        ok = m is not None and np.isfinite(m) and rule(m)
        marks.append(bool(ok))
    return sum(marks), marks


# ─── Single-run executor ───────────────────────────────────────────────────


def _run_single(cfg: dict, variant: str, out_dir: Path) -> dict:
    sim_cfg = dict(cfg["simulator"])
    train_cfg = dict(cfg["training"])
    eval_cfg = dict(cfg["evaluation"])

    dataset = train_cfg.get("target_dataset", "spx")
    period = train_cfg.get("target_period", "2015-2026_daily")
    real_r = _load_returns(dataset, period)

    w_cfg = train_cfg["loss_weights"]
    weights = LossWeights(
        w_acf_sq=w_cfg["w_acf_sq"],
        w_leverage=w_cfg["w_leverage"],
        w_hill=w_cfg["w_hill"],
        max_lag=w_cfg["max_lag"],
        hill_k_frac=w_cfg["hill_k_frac"],
        w_acf_shape=w_cfg.get("w_acf_shape", 0.0),
        acf_shape_target_ratio=w_cfg.get("acf_shape_target_ratio", 2.0),
        acf_shape_lag_peak=w_cfg.get("acf_shape_lag_peak", 1),
        acf_shape_lag_tail=w_cfg.get("acf_shape_lag_tail", 10),
    )
    targets = build_targets_from_returns(
        real_r, max_lag=weights.max_lag, k_frac=weights.hill_k_frac
    )

    torch.manual_seed(train_cfg["seed"])
    sim = EcoMDSimulator(EcoMDConfig(**sim_cfg))

    t0 = time.time()
    history = train_ecomd(
        sim, targets,
        n_iters=train_cfg["n_iters"],
        chunk_steps=train_cfg["chunk_steps"],
        lr=train_cfg["lr"],
        grad_clip=train_cfg["grad_clip_max_norm"],
        weights=weights, seed=train_cfg["seed"],
        persistent_state=train_cfg.get("persistent_state", False),
        warmup_steps=train_cfg.get("warmup_steps", 0),
        lr_warmup_iters=train_cfg.get("lr_warmup_iters", 0),
    )
    t_train = time.time() - t0

    # eval
    realizations = []
    t0 = time.time()
    for r_idx in range(eval_cfg["n_realizations"]):
        traj = sim.run(n_steps=eval_cfg["eval_steps"], seed=1000 + r_idx)
        returns = traj.log_returns_np()[1:]
        volumes = traj.volumes_np()[1:]
        facts = compute_all(returns, volume=volumes)
        r_t = torch.tensor(returns, dtype=torch.float32)
        realizations.append({
            "facts": {k: v.to_dict() for k, v in facts.items()},
            "shape_loss": float(acf_shape_loss(r_t, target_ratio=2.0).item()),
            "ljung_box": ljung_box_stat(returns, lags=10, squared=True).p_value,
        })
    t_eval = time.time() - t0
    keys = list(realizations[0]["facts"].keys())
    agg: dict[str, dict[str, float]] = {}
    for k in keys:
        vals = [float(r["facts"][k]["estimate"])
                for r in realizations
                if isinstance(r["facts"][k].get("estimate"), (int, float))
                and np.isfinite(r["facts"][k].get("estimate"))]
        if vals:
            agg[k] = {"mean": float(np.mean(vals)), "std": float(np.std(vals))}

    passed, marks = _score_facts(agg)
    shape_mean = float(np.mean([r["shape_loss"] for r in realizations]))
    lb_mean = float(np.mean([r["ljung_box"] for r in realizations]))

    result = {
        "variant": variant,
        "n_passed": passed,
        "passed_marks": marks,
        "aggregated": agg,
        "shape_loss_mean": shape_mean,
        "ljung_box_p_mean": lb_mean,
        "train_time_seconds": t_train,
        "eval_time_seconds": t_eval,
        "final_loss": float(history[-1]["total"]),
        "params": int(sum(p.numel() for p in sim.parameters())),
        "config": {"simulator": sim_cfg, "training": train_cfg},
    }

    # Persist per-variant result
    (out_dir / f"{variant}_result.json").write_text(json.dumps(result, indent=2))
    return result


# ─── Main driver ───────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--grid", required=True, help="path to grid YAML")
    parser.add_argument("--skip", type=int, default=0,
                        help="skip first N runs (for resume)")
    parser.add_argument("--limit", type=int, default=None,
                        help="run only first N after skip")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")

    grid_path = Path(args.grid).resolve()
    grid_spec = yaml.safe_load(grid_path.read_text())
    base_path = grid_path.parent / grid_spec["base_config"]
    base_cfg = yaml.safe_load(base_path.read_text())

    out_dir = HERE / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    assignments = _expand_grid(grid_spec["grid"], grid_spec.get("skip_when", []))
    log.info(f"grid expanded to {len(assignments)} assignments")

    runs = []
    for i, a in enumerate(assignments):
        if i < args.skip:
            continue
        if args.limit is not None and i >= args.skip + args.limit:
            break
        cfg = copy.deepcopy(base_cfg)
        for key, val in a.items():
            _set_dotted(cfg, key, val)
        variant = _variant_name(grid_spec.get("variant_template", "run_{i}"), a)
        log.info(f"[{i+1}/{len(assignments)}] running {variant}")
        try:
            result = _run_single(cfg, variant, out_dir)
            log.info(f"  {variant}: {result['n_passed']}/11  shape={result['shape_loss_mean']:.2f} "
                     f"lb_p={result['ljung_box_p_mean']:.2e}  "
                     f"({result['train_time_seconds']:.0f}s+{result['eval_time_seconds']:.0f}s)")
            runs.append(result)
        except Exception as e:  # noqa: BLE001
            log.error(f"  {variant}: ERROR {type(e).__name__}: {e}")
            runs.append({"variant": variant, "error": str(e), "n_passed": -1})

    # Summary table (sorted by n_passed descending)
    sorted_runs = sorted(runs, key=lambda r: r.get("n_passed", -1), reverse=True)
    lines = [
        "# v2 ablation summary",
        "",
        f"Grid: `{grid_path.name}`",
        f"Total: {len(runs)} runs completed  ("
        f"{sum(1 for r in runs if r.get('n_passed', -1) >= 7)} passed ≥7/11)",
        "",
        "| rank | variant | passed | shape | LB_p | final_loss |",
        "|---|---|---|---|---|---|",
    ]
    for rank, r in enumerate(sorted_runs, 1):
        if "error" in r:
            lines.append(f"| {rank} | `{r['variant']}` | ERROR | — | — | — |")
            continue
        lines.append(
            f"| {rank} | `{r['variant']}` | **{r['n_passed']}/11** | "
            f"{r['shape_loss_mean']:.2f} | {r['ljung_box_p_mean']:.2e} | "
            f"{r['final_loss']:.3f} |"
        )
    (out_dir / "grid_summary.md").write_text("\n".join(lines))

    # Top-3 dump for quick view
    print("\n".join(lines))


if __name__ == "__main__":
    main()
