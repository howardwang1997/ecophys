"""EcoMD v0.7 — v0.6 + sigma_price reduction for #10 corr(V,|r|).

Train + eval + produce seven_way_comparison.md (real/GARCH/LM99/v0/v0.5/v0.6/v0.7).
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

from ecomd.eval.stylized_facts import compute_all, log_returns_from_prices
from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.training.losses import LossWeights, build_targets_from_returns
from ecomd.training.train import train_ecomd

log = logging.getLogger("ecomd_v0p7")

REPO = Path(__file__).resolve().parents[2]
RAW_DIR = REPO / "data" / "raw"
REF_RESULTS = REPO / "experiments" / "000_reference_values" / "results"
LM_RESULTS = REPO / "experiments" / "001_lux_marchesi_baseline" / "results"
GARCH_RESULTS = REPO / "experiments" / "002_garch_baseline" / "results"
V0_RESULTS = REPO / "experiments" / "003_ecomd_v0" / "results"
V0P5_RESULTS = REPO / "experiments" / "004_ecomd_v0p5" / "results"
V0P6_RESULTS = REPO / "experiments" / "005_ecomd_v0p6" / "results"
OUT = Path(__file__).parent / "results"


def _read_yfinance(symbol: str) -> pd.DataFrame:
    root = RAW_DIR / "yfinance" / "interval=1d" / f"symbol={symbol}"
    frames = [pd.read_parquet(p) for p in sorted(root.glob("year=*.parquet"))]
    return pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)


def _spx_returns() -> np.ndarray:
    df = _read_yfinance("^GSPC")
    col = "adjusted_close" if "adjusted_close" in df.columns else "close"
    return log_returns_from_prices(df[col].to_numpy())


def evaluate(sim: EcoMDSimulator, n_realizations: int, n_steps: int) -> dict[str, Any]:
    realizations = []
    for r_idx in range(n_realizations):
        traj = sim.run(n_steps=n_steps, seed=1000 + r_idx)
        returns = traj.log_returns_np()[1:]
        volumes = traj.volumes_np()[1:]
        facts = compute_all(returns, volume=volumes)
        realizations.append({
            "seed": 1000 + r_idx,
            "facts": {k: v.to_dict() for k, v in facts.items()},
        })
    keys = list(realizations[0]["facts"].keys())
    aggregated: dict[str, dict[str, float]] = {}
    for k in keys:
        vals = [float(r["facts"][k]["estimate"])
                for r in realizations
                if isinstance(r["facts"][k].get("estimate"), (int, float))
                and np.isfinite(r["facts"][k].get("estimate"))]
        if vals:
            aggregated[k] = {"mean": float(np.mean(vals)), "std": float(np.std(vals))}
    return {"realizations": realizations, "aggregated": aggregated}


ROWS = [
    ("#1 ACF(r)",       "autocorr_returns",          "<0.08"),
    ("#2 α Hill",       "hill_tail_index",           "[2,6]"),
    ("#3 skew",         "gain_loss_asymmetry",       "<-0.05"),
    ("#4 Δκ agg",       "aggregational_gaussianity", ">0"),
    ("#5 Fano",         "intermittency_fano",        ">1"),
    ("#6 ⟨ACF(r²)⟩",    "acf_squared_returns",       ">0.05"),
    ("#7 κ GARCH-std",  "conditional_kurtosis",      "|·|<3"),
    ("#8 H DFA|r|",     "dfa_hurst_abs_r",           "[0.5,0.85]"),
    ("#9 ΣLev",         "leverage_effect",           "<-0.05"),
    ("#10 corr(V,|r|)", "volume_volatility_corr",    ">0.1"),
    ("#11 Zumbach D",   "zumbach_asymmetry",         ">0.01"),
]


def _score(m: float | None, key: str) -> bool:
    if m is None or not np.isfinite(m):
        return False
    if key == "autocorr_returns":      return abs(m) < 0.08
    if key == "hill_tail_index":       return 2.0 <= m <= 6.0
    if key == "gain_loss_asymmetry":   return m < -0.05
    if key == "aggregational_gaussianity": return m > 0
    if key == "intermittency_fano":    return m > 1.0
    if key == "acf_squared_returns":   return m > 0.05
    if key == "conditional_kurtosis":  return abs(m) < 3.0
    if key == "dfa_hurst_abs_r":       return 0.50 <= m <= 0.85
    if key == "leverage_effect":       return m < -0.05
    if key == "volume_volatility_corr": return m > 0.1
    if key == "zumbach_asymmetry":     return m > 0.01
    return False


def _load_json(p: Path) -> Any:
    return json.loads(p.read_text()) if p.exists() else None


def _aggregate_realizations(realizations: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    if not realizations:
        return {}
    sample_keys = list(realizations[0].get("results", {}).keys())
    out: dict[str, dict[str, float]] = {}
    for k in sample_keys:
        vals: list[float] = []
        for r in realizations:
            est = (r.get("results", {}).get(k) or {}).get("estimate")
            if isinstance(est, (int, float)) and np.isfinite(est):
                vals.append(float(est))
        if vals:
            out[k] = {"mean": float(np.mean(vals)), "std": float(np.std(vals))}
    return out


def build_seven_way_comparison(v0p7_eval: dict[str, Any], target_dataset: str = "spx") -> str:
    real_raw = _load_json(REF_RESULTS / f"stylized_facts_{target_dataset}_2015-2026_daily.json") or {}
    real_facts = {k: v.get("estimate") for k, v in (real_raw.get("results") or {}).items()
                  if isinstance(v, dict)}

    garch_raw = _load_json(GARCH_RESULTS / "garch_stylized_facts.json") or []
    garch_agg = next(
        (f["aggregated"] for f in garch_raw if f.get("dataset") == target_dataset),
        {},
    )

    lm_raw = _load_json(LM_RESULTS / "lux_marchesi_stylized_facts.json") or []
    lm_agg = _aggregate_realizations(lm_raw) if isinstance(lm_raw, list) else {}

    v0_agg = (_load_json(V0_RESULTS / "ecomd_stylized_facts.json") or {}).get("aggregated", {})
    v0p5_agg = (_load_json(V0P5_RESULTS / "ecomd_v0p5_stylized_facts.json") or {}).get("aggregated", {})
    v0p6_agg = (_load_json(V0P6_RESULTS / "ecomd_v0p6_stylized_facts.json") or {}).get("aggregated", {})
    v0p7_agg = v0p7_eval["aggregated"]

    lines: list[str] = []
    lines.append(f"# Seven-way comparison — real ({target_dataset}) / GARCH / LM99 / EcoMD v0 / v0.5 / v0.6 / v0.7")
    lines.append("")
    lines.append("v0.7 changes over v0.6: sigma_price 0.005 → 0.001 (only change).")
    lines.append("Target: boost #10 corr(V,|r|) above 0.1 to hit M2 gate (7/11).")
    lines.append("")
    header_cols = ["metric", "expected", f"real ({target_dataset})", "GARCH", "LM99",
                   "v0", "v0.5", "v0.6", "v0.7"]
    lines.append("| " + " | ".join(header_cols) + " |")
    lines.append("|" + "---|" * len(header_cols))

    def fmt(v: Any) -> str:
        if isinstance(v, dict) and "mean" in v:
            std = v.get("std")
            if isinstance(std, (int, float)):
                return f"{v['mean']:+.3f} ± {std:.3f}"
            return f"{v['mean']:+.3f}"
        if isinstance(v, (int, float)) and np.isfinite(v):
            return f"{v:+.3f}"
        return "—"

    for label, key, expected in ROWS:
        row = [label, expected, fmt(real_facts.get(key)), fmt(garch_agg.get(key)),
               fmt(lm_agg.get(key)), fmt(v0_agg.get(key)), fmt(v0p5_agg.get(key)),
               fmt(v0p6_agg.get(key)), fmt(v0p7_agg.get(key))]
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("## Scoreboard")
    lines.append("")
    lines.append("| metric | GARCH | LM99 | v0 | v0.5 | v0.6 | v0.7 |")
    lines.append("|---|---|---|---|---|---|---|")
    tot = {"g": 0, "lm": 0, "v0": 0, "v0p5": 0, "v0p6": 0, "v0p7": 0}
    for label, key, _ in ROWS:
        gv = (garch_agg.get(key) or {}).get("mean")
        lv = (lm_agg.get(key) or {}).get("mean")
        v0v = (v0_agg.get(key) or {}).get("mean")
        v0p5v = (v0p5_agg.get(key) or {}).get("mean")
        v0p6v = (v0p6_agg.get(key) or {}).get("mean")
        v0p7v = (v0p7_agg.get(key) or {}).get("mean")
        tot["g"]    += int(_score(gv, key))
        tot["lm"]   += int(_score(lv, key))
        tot["v0"]   += int(_score(v0v, key))
        tot["v0p5"] += int(_score(v0p5v, key))
        tot["v0p6"] += int(_score(v0p6v, key))
        tot["v0p7"] += int(_score(v0p7v, key))
        mark = lambda b: "✓" if b else "✗"
        lines.append(f"| {label} | {mark(_score(gv, key))} | {mark(_score(lv, key))} "
                     f"| {mark(_score(v0v, key))} | {mark(_score(v0p5v, key))} "
                     f"| {mark(_score(v0p6v, key))} | {mark(_score(v0p7v, key))} |")
    lines.append(f"| **Total** | **{tot['g']}/11** | **{tot['lm']}/11** | **{tot['v0']}/11** "
                 f"| **{tot['v0p5']}/11** | **{tot['v0p6']}/11** | **{tot['v0p7']}/11** |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--config", default=str(Path(__file__).parent / "config.yaml"))
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    OUT.mkdir(parents=True, exist_ok=True)

    cfg = yaml.safe_load(Path(args.config).read_text())
    sim_cfg_dict = dict(cfg["simulator"])
    train_cfg = dict(cfg["training"])
    eval_cfg = dict(cfg["evaluation"])
    if args.smoke:
        smoke = cfg.get("smoke", {})
        sim_cfg_dict["n_agents"] = smoke.get("n_agents", sim_cfg_dict["n_agents"])
        train_cfg["n_iters"] = smoke.get("n_iters", train_cfg["n_iters"])
        train_cfg["chunk_steps"] = smoke.get("chunk_steps", train_cfg["chunk_steps"])
        eval_cfg["eval_steps"] = smoke.get("eval_steps", eval_cfg["eval_steps"])
        eval_cfg["n_realizations"] = smoke.get("n_realizations", eval_cfg["n_realizations"])
        log.info("SMOKE MODE")

    log.info(f"simulator: {sim_cfg_dict}")
    log.info(f"training: {train_cfg}")
    log.info(f"evaluation: {eval_cfg}")

    real_r = _spx_returns()
    weights_cfg = train_cfg["loss_weights"]
    weights = LossWeights(
        w_acf_sq=weights_cfg["w_acf_sq"],
        w_leverage=weights_cfg["w_leverage"],
        w_hill=weights_cfg["w_hill"],
        max_lag=weights_cfg["max_lag"],
        hill_k_frac=weights_cfg["hill_k_frac"],
    )
    targets = build_targets_from_returns(real_r, max_lag=weights.max_lag, k_frac=weights.hill_k_frac)
    log.info(f"targets: acf_sq={targets.acf_sq_mean:.3f} "
             f"leverage={targets.leverage_sum:+.3f} hill={targets.hill_alpha:.2f}")

    simulator_config = EcoMDConfig(**sim_cfg_dict)
    torch.manual_seed(train_cfg["seed"])
    sim = EcoMDSimulator(simulator_config)
    log.info(f"EcoMDSimulator: {sum(p.numel() for p in sim.parameters())} params "
             f"(sigma_price={simulator_config.price_formation_kwargs.get('sigma_price')})")

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
    log.info(f"train done in {t_train:.1f}s, final loss={history[-1]['total']:.3f}")

    (OUT / "training_log.json").write_text(json.dumps({
        "config": {"simulator": sim_cfg_dict, "training": train_cfg, "evaluation": eval_cfg},
        "targets": asdict(targets),
        "history": history,
        "train_time_seconds": t_train,
    }, indent=2))

    log.info(f"evaluating {eval_cfg['n_realizations']} × {eval_cfg['eval_steps']} steps")
    t0 = time.time()
    eval_out = evaluate(sim, eval_cfg["n_realizations"], eval_cfg["eval_steps"])
    t_eval = time.time() - t0
    log.info(f"eval done in {t_eval:.1f}s")

    (OUT / "ecomd_v0p7_stylized_facts.json").write_text(json.dumps({
        "aggregated": eval_out["aggregated"],
        "realizations": eval_out["realizations"],
        "eval_time_seconds": t_eval,
    }, indent=2))

    md = build_seven_way_comparison(eval_out, target_dataset=train_cfg["target_dataset"])
    (OUT / "seven_way_comparison.md").write_text(md)
    print(md)

    agg = eval_out["aggregated"]
    v10 = agg.get("volume_volatility_corr", {}).get("mean", float("nan"))
    v6  = agg.get("acf_squared_returns", {}).get("mean", float("nan"))
    print(f"\n#10 corr(V,|r|) = {v10:+.3f}  (target >0.1, v0.6 was +0.078)")
    print(f"#6  ACF(r²)     = {v6:+.3f}  (v0.6 was +0.306)")
    log.info(f"outputs under {OUT}/")


if __name__ == "__main__":
    main()
