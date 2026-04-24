"""EcoMD v2 runner — trains the Kyle + Typed + Gauge architecture and
evaluates 11 stylized facts + ACF shape + Ljung-Box on SPX daily (or BTC).

Builds on experiments/012_cross_asset/run.py pattern but with extra
reporting of the v2-specific diagnostics (Kyle λ trajectory, T matrix
spectrum, type-distribution, ACF shape ratio, LB p-value).
"""

from __future__ import annotations

import argparse
import json
import logging
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

log = logging.getLogger("v2")

REPO = Path(__file__).resolve().parents[2]
RAW_DIR = REPO / "data" / "raw"
REF_RESULTS = REPO / "experiments" / "000_reference_values" / "results"
OUT = Path(__file__).parent / "results"


def _spx_returns() -> np.ndarray:
    root = RAW_DIR / "yfinance" / "interval=1d" / "symbol=^GSPC"
    frames = [pd.read_parquet(p) for p in sorted(root.glob("year=*.parquet"))]
    df = pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)
    col = "adjusted_close" if "adjusted_close" in df.columns else "close"
    return log_returns_from_prices(df[col].to_numpy())


def _btc_1m_returns() -> np.ndarray:
    root = RAW_DIR / "binance" / "market=spot" / "interval=1m" / "symbol=BTCUSDT" / "year=2024"
    frames = [pd.read_parquet(p) for p in sorted(root.glob("month=*.parquet"))]
    df = pd.concat(frames, ignore_index=True).sort_values("open_time").reset_index(drop=True)
    return log_returns_from_prices(df["close"].to_numpy())


def _returns_for(dataset: str, period: str) -> np.ndarray:
    if dataset == "spx" and period == "2015-2026_daily":
        return _spx_returns()
    if dataset == "btcusdt" and period == "2024Q1_1m":
        return _btc_1m_returns()
    raise ValueError(f"unknown {dataset}/{period}")


def evaluate(sim: EcoMDSimulator, n_realizations: int, n_steps: int) -> dict[str, Any]:
    realizations = []
    shape_diags = []
    lb_diags = []
    for r_idx in range(n_realizations):
        traj = sim.run(n_steps=n_steps, seed=1000 + r_idx)
        returns = traj.log_returns_np()[1:]
        volumes = traj.volumes_np()[1:]
        facts = compute_all(returns, volume=volumes)
        # v2 extras: per-realization shape + LB
        r_t = torch.tensor(returns, dtype=torch.float32)
        curve = acf_squared_per_lag(r_t, max_lag=16).detach().numpy().tolist()
        shape_loss = float(acf_shape_loss(r_t, target_ratio=2.0).item())
        lb = ljung_box_stat(returns, lags=10, squared=True)
        realizations.append({
            "seed": 1000 + r_idx,
            "facts": {k: v.to_dict() for k, v in facts.items()},
            "acf_sq_per_lag": curve,
            "acf_shape_loss": shape_loss,
            "ljung_box_Q": lb.statistic,
            "ljung_box_p": lb.p_value,
            "reject_white_noise": lb.reject_white_noise,
        })
        shape_diags.append(shape_loss)
        lb_diags.append(lb.p_value)

    keys = list(realizations[0]["facts"].keys())
    aggregated: dict[str, dict[str, float]] = {}
    for k in keys:
        vals = [float(r["facts"][k]["estimate"])
                for r in realizations
                if isinstance(r["facts"][k].get("estimate"), (int, float))
                and np.isfinite(r["facts"][k].get("estimate"))]
        if vals:
            aggregated[k] = {"mean": float(np.mean(vals)), "std": float(np.std(vals))}

    return {
        "realizations": realizations,
        "aggregated": aggregated,
        "shape_loss_mean": float(np.mean(shape_diags)),
        "ljung_box_p_mean": float(np.mean(lb_diags)),
        "reject_white_noise_fraction": float(
            np.mean([r["reject_white_noise"] for r in realizations])
        ),
    }


ROWS = [
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


def _score(m, rule):
    if m is None or not np.isfinite(m):
        return False
    return bool(rule(m))


def _fmt(v):
    if isinstance(v, dict) and "mean" in v:
        s = v.get("std")
        return f"{v['mean']:+.3f}±{s:.3f}" if isinstance(s, (int, float)) else f"{v['mean']:+.3f}"
    if isinstance(v, (int, float)) and np.isfinite(v):
        return f"{v:+.3f}"
    return "—"


def build_report(variant: str, sim_agg: dict, eval_out: dict) -> tuple[str, int]:
    lines = [f"# EcoMD v2 eval — {variant}",
             "",
             f"| metric | rule | sim | pass? |",
             "|---|---|---|---|"]
    passed = 0
    for label, key, rule in ROWS:
        m = (sim_agg.get(key) or {}).get("mean")
        ok = _score(m, rule)
        if ok:
            passed += 1
        lines.append(f"| {label} | {rule.__name__ if hasattr(rule, '__name__') else '-'} | "
                     f"{_fmt(sim_agg.get(key))} | {'✓' if ok else '✗'} |")
    lines.append(f"| **Total** | | | **{passed}/11** |")
    lines.append("")
    lines.append("## v2 diagnostics (Goodhart protection)")
    lines.append("")
    lines.append(f"- **ACF shape loss** (peak/tail ratio penalty): {eval_out['shape_loss_mean']:.3f}  "
                 f"(0 = passed; >0 = flat curve)")
    lines.append(f"- **Ljung-Box p-value** (r² at lag 10): {eval_out['ljung_box_p_mean']:.2e}  "
                 f"(<0.05 = rejects white noise)")
    lines.append(f"- **Reject white noise** fraction over realizations: "
                 f"{eval_out['reject_white_noise_fraction']:.0%}")
    return "\n".join(lines), passed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    OUT.mkdir(parents=True, exist_ok=True)

    cfg = yaml.safe_load(Path(args.config).read_text())
    variant = cfg.get("variant", Path(args.config).stem)
    sim_cfg_dict = dict(cfg["simulator"])
    train_cfg = dict(cfg["training"])
    eval_cfg = dict(cfg["evaluation"])
    dataset = train_cfg.get("target_dataset", "spx")
    period = train_cfg.get("target_period", "2015-2026_daily")

    real_r = _returns_for(dataset, period)
    log.info(f"{variant}: {len(real_r):,} {dataset} returns")

    w_cfg = train_cfg["loss_weights"]
    weights = LossWeights(
        w_acf_sq=w_cfg["w_acf_sq"], w_leverage=w_cfg["w_leverage"],
        w_hill=w_cfg["w_hill"], max_lag=w_cfg["max_lag"],
        hill_k_frac=w_cfg["hill_k_frac"],
    )
    targets = build_targets_from_returns(real_r, max_lag=weights.max_lag, k_frac=weights.hill_k_frac)
    log.info(f"targets: acf_sq={targets.acf_sq_mean:.3f} "
             f"lev={targets.leverage_sum:+.3f} hill={targets.hill_alpha:.2f}")

    simulator_config = EcoMDConfig(**sim_cfg_dict)
    torch.manual_seed(train_cfg["seed"])
    sim = EcoMDSimulator(simulator_config)
    n_params = sum(p.numel() for p in sim.parameters())
    log.info(f"v2 sim: {n_params:,} params  pairwise={simulator_config.pairwise_kind}")
    # Log v2-specific init
    pair = sim.potential.pairwise
    if hasattr(pair, "types"):
        counts = torch.bincount(pair.types.labels, minlength=simulator_config.v2_k_types).tolist()
        log.info(f"v2 type distribution: {counts}")
        if pair.kyle is not None:
            log.info(f"v2 Kyle λ init: {pair.kyle.lambda_raw.item():+.4f}")
        log.info(f"v2 T matrix (diag): "
                 f"{[round(pair.rel.T[k,k].item(), 3) for k in range(simulator_config.v2_k_types)]}")

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
    log.info(f"train done {t_train:.1f}s, final loss={history[-1]['total']:.3f}")

    # Post-train diagnostics
    if hasattr(pair, "types") and pair.kyle is not None:
        log.info(f"Kyle λ trained: {pair.kyle.lambda_raw.item():+.4f}")
        T_final = pair.rel.T.detach()
        log.info(f"T matrix trained (diag): "
                 f"{[round(T_final[k,k].item(), 3) for k in range(simulator_config.v2_k_types)]}")

    (OUT / f"{variant}_training_log.json").write_text(json.dumps({
        "variant": variant,
        "config": {"simulator": sim_cfg_dict, "training": train_cfg, "evaluation": eval_cfg},
        "targets": asdict(targets),
        "history": history,
        "train_time_seconds": t_train,
        "params_total": n_params,
    }, indent=2))

    log.info(f"evaluating {eval_cfg['n_realizations']} × {eval_cfg['eval_steps']} steps")
    t0 = time.time()
    eval_out = evaluate(sim, eval_cfg["n_realizations"], eval_cfg["eval_steps"])
    t_eval = time.time() - t0
    log.info(f"eval done {t_eval:.1f}s")

    (OUT / f"{variant}_stylized_facts.json").write_text(json.dumps({
        "variant": variant,
        "aggregated": eval_out["aggregated"],
        "shape_loss_mean": eval_out["shape_loss_mean"],
        "ljung_box_p_mean": eval_out["ljung_box_p_mean"],
        "reject_white_noise_fraction": eval_out["reject_white_noise_fraction"],
        "realizations": eval_out["realizations"],
        "eval_time_seconds": t_eval,
    }, indent=2))

    md, passed = build_report(variant, eval_out["aggregated"], eval_out)
    (OUT / f"{variant}_comparison.md").write_text(md)
    print(md)
    log.info(f"{variant}: {passed}/11")


if __name__ == "__main__":
    main()
