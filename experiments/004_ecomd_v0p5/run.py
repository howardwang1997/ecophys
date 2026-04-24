"""EcoMD v0.5 — train on SPX with persistent state + warm-up detach.

Imports the shared training loop from ``ecomd.training.train``; comparison table
reuses the same dataset scaffolding as experiment 003 but adds a 5th column so
we can see v0 trained / v0.5 trained / baselines side-by-side.
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

log = logging.getLogger("ecomd_v0p5")

REPO = Path(__file__).resolve().parents[2]
RAW_DIR = REPO / "data" / "raw"
REF_RESULTS = REPO / "experiments" / "000_reference_values" / "results"
LM_RESULTS = REPO / "experiments" / "001_lux_marchesi_baseline" / "results"
GARCH_RESULTS = REPO / "experiments" / "002_garch_baseline" / "results"
V0_RESULTS = REPO / "experiments" / "003_ecomd_v0" / "results"
OUT = Path(__file__).parent / "results"


# ─── Data ────────────────────────────────────────────────────────────────


def _read_yfinance(symbol: str) -> pd.DataFrame:
    root = RAW_DIR / "yfinance" / "interval=1d" / f"symbol={symbol}"
    frames = [pd.read_parquet(p) for p in sorted(root.glob("year=*.parquet"))]
    return pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)


def _spx_returns() -> np.ndarray:
    df = _read_yfinance("^GSPC")
    col = "adjusted_close" if "adjusted_close" in df.columns else "close"
    return log_returns_from_prices(df[col].to_numpy())


# ─── Evaluation ──────────────────────────────────────────────────────────


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
    keys: list[str] = list(realizations[0]["facts"].keys())
    aggregated: dict[str, dict[str, float]] = {}
    for k in keys:
        vals: list[float] = []
        for r in realizations:
            v = r["facts"][k].get("estimate")
            if isinstance(v, (int, float)) and np.isfinite(v):
                vals.append(float(v))
        if vals:
            aggregated[k] = {"mean": float(np.mean(vals)), "std": float(np.std(vals))}
    return {"realizations": realizations, "aggregated": aggregated}


# ─── Comparison table ────────────────────────────────────────────────────


ROWS = [
    ("#1 ACF(r)",       "autocorr_returns",          "<0.05"),
    ("#2 α Hill",       "hill_tail_index",           "[3, 5]"),
    ("#3 skew",         "gain_loss_asymmetry",       "<0 daily equity"),
    ("#4 Δκ agg",       "aggregational_gaussianity", ">0"),
    ("#5 Fano",         "intermittency_fano",        ">1"),
    ("#6 ⟨ACF(r²)⟩",   "acf_squared_returns",       ">0.05"),
    ("#7 κ GARCH-std",  "conditional_kurtosis",      ">0, <uncond"),
    ("#8 H DFA|r|",     "dfa_hurst_abs_r",           "[0.55, 0.80]"),
    ("#9 ΣLev",         "leverage_effect",           "<0 daily"),
    ("#10 corr(V,|r|)", "volume_volatility_corr",    "[0.2, 0.6]"),
    ("#11 Zumbach D",   "zumbach_asymmetry",         ">0 indices"),
]


def _score(m: float | None, key: str) -> bool:
    if m is None or not np.isfinite(m):
        return False
    if key == "autocorr_returns":      return m < 0.08
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


def build_five_way_comparison(ecomd_v0p5_eval: dict[str, Any], target_dataset: str = "spx") -> str:
    real_raw = _load_json(REF_RESULTS / f"stylized_facts_{target_dataset}_2015-2026_daily.json") or {}
    real_results = real_raw.get("results", {})
    real_facts = {k: v.get("estimate") for k, v in real_results.items() if isinstance(v, dict)}

    garch_raw = _load_json(GARCH_RESULTS / "garch_stylized_facts.json") or []
    garch_for_dataset = next(
        (f["aggregated"] for f in garch_raw if f.get("dataset") == target_dataset),
        {},
    )

    lm_raw = _load_json(LM_RESULTS / "lux_marchesi_stylized_facts.json") or []
    lm_agg = _aggregate_realizations(lm_raw) if isinstance(lm_raw, list) else {}

    v0_raw = _load_json(V0_RESULTS / "ecomd_stylized_facts.json") or {}
    v0_agg = v0_raw.get("aggregated", {})

    v0p5_agg = ecomd_v0p5_eval["aggregated"]

    lines: list[str] = []
    lines.append(f"# Five-way comparison — real ({target_dataset}) / GARCH / LM99 / EcoMD v0 / EcoMD v0.5")
    lines.append("")
    lines.append(f"Trained on {target_dataset} moment targets. EcoMD v0 from experiment 003; v0.5 improvements:")
    lines.append("persistent state across iters, warm-up detach (first 16 steps), LR 1e-3 + cosine schedule, max_lag=8.")
    lines.append("")
    lines.append(f"| metric | expected | real ({target_dataset}) | GARCH | LM99 | EcoMD v0 | EcoMD v0.5 |")
    lines.append("|---|---|---|---|---|---|---|")
    for label, key, expected in ROWS:
        real_v = real_facts.get(key)
        g = garch_for_dataset.get(key)
        lm = lm_agg.get(key)
        v0 = v0_agg.get(key)
        v0p5 = v0p5_agg.get(key)
        real_s = f"{real_v:+.3f}" if isinstance(real_v, (int, float)) and np.isfinite(real_v) else "—"
        g_s = f"{g['mean']:+.3f} ± {g['std']:.3f}" if g else "—"
        lm_s = f"{lm['mean']:+.3f} ± {lm['std']:.3f}" if lm else "—"
        v0_s = f"{v0['mean']:+.3f} ± {v0['std']:.3f}" if v0 else "—"
        v0p5_s = f"{v0p5['mean']:+.3f} ± {v0p5['std']:.3f}" if v0p5 else "—"
        lines.append(f"| {label} | {expected} | {real_s} | {g_s} | {lm_s} | {v0_s} | {v0p5_s} |")

    lines.append("")
    lines.append("## Scoreboard (loose tolerance)")
    lines.append("")
    lines.append("| metric | GARCH | LM99 | EcoMD v0 | EcoMD v0.5 |")
    lines.append("|---|---|---|---|---|")
    gt = lt = v0t = v0p5t = 0
    for label, key, _ in ROWS:
        gv = (garch_for_dataset.get(key) or {}).get("mean")
        lv = (lm_agg.get(key) or {}).get("mean")
        v0v = (v0_agg.get(key) or {}).get("mean")
        v0p5v = (v0p5_agg.get(key) or {}).get("mean")
        gc = _score(gv, key); lc = _score(lv, key)
        v0c = _score(v0v, key); v0p5c = _score(v0p5v, key)
        gt += int(gc); lt += int(lc); v0t += int(v0c); v0p5t += int(v0p5c)
        lines.append(
            f"| {label} | {'✓' if gc else '✗'} | {'✓' if lc else '✗'} "
            f"| {'✓' if v0c else '✗'} | {'✓' if v0p5c else '✗'} |"
        )
    lines.append(f"| **Total** | **{gt}/11** | **{lt}/11** | **{v0t}/11** | **{v0p5t}/11** |")
    return "\n".join(lines)


# ─── Main ────────────────────────────────────────────────────────────────


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

    log.info(f"simulator config: {sim_cfg_dict}")
    log.info(f"training config: {train_cfg}")
    log.info(f"evaluation config: {eval_cfg}")

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
             f"leverage_sum={targets.leverage_sum:+.3f} hill_alpha={targets.hill_alpha:.2f}")

    simulator_config = EcoMDConfig(**sim_cfg_dict)
    torch.manual_seed(train_cfg["seed"])
    sim = EcoMDSimulator(simulator_config)
    log.info(f"EcoMDSimulator built: {sum(p.numel() for p in sim.parameters())} parameters")

    t0 = time.time()
    history = train_ecomd(
        sim, targets,
        n_iters=train_cfg["n_iters"],
        chunk_steps=train_cfg["chunk_steps"],
        lr=train_cfg["lr"],
        grad_clip=train_cfg["grad_clip_max_norm"],
        weights=weights,
        seed=train_cfg["seed"],
        persistent_state=train_cfg.get("persistent_state", False),
        warmup_steps=train_cfg.get("warmup_steps", 0),
        lr_warmup_iters=train_cfg.get("lr_warmup_iters", 0),
    )
    t_train = time.time() - t0
    log.info(f"training finished in {t_train:.1f}s")

    (OUT / "training_log.json").write_text(json.dumps({
        "config": {"simulator": sim_cfg_dict, "training": train_cfg, "evaluation": eval_cfg},
        "targets": asdict(targets),
        "history": history,
        "train_time_seconds": t_train,
    }, indent=2))

    log.info(f"evaluating: {eval_cfg['n_realizations']} × {eval_cfg['eval_steps']} steps")
    t0 = time.time()
    eval_out = evaluate(sim, eval_cfg["n_realizations"], eval_cfg["eval_steps"])
    t_eval = time.time() - t0
    log.info(f"evaluation finished in {t_eval:.1f}s")

    (OUT / "ecomd_v0p5_stylized_facts.json").write_text(json.dumps({
        "aggregated": eval_out["aggregated"],
        "realizations": eval_out["realizations"],
        "eval_time_seconds": t_eval,
    }, indent=2))

    md = build_five_way_comparison(eval_out, target_dataset=train_cfg["target_dataset"])
    (OUT / "five_way_comparison.md").write_text(md)
    print(md)

    log.info(f"wrote outputs under {OUT}/")


if __name__ == "__main__":
    main()
