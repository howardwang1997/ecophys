"""EcoMD v1 ablation runner.

Given one of the 4 config files (A/B/C/D), trains the variant with the
config's recipe, evaluates 11 stylized facts on a long rollout, and
writes:

  results/<variant>_stylized_facts.json    # aggregated + per-realization
  results/<variant>_training_log.json      # per-iter loss trace

Usage:
  conda run -n ecophys python experiments/008_ecomd_v1_ablation/run.py \\
    --config experiments/008_ecomd_v1_ablation/config_A_matched.yaml

After all 4 variants run, call:
  conda run -n ecophys python experiments/008_ecomd_v1_ablation/run.py --summarize

to build results/ablation_summary.md comparing v0.6 baseline + A/B/C/D.
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

log = logging.getLogger("v1_ablation")

REPO = Path(__file__).resolve().parents[2]
RAW_DIR = REPO / "data" / "raw"
OUT = Path(__file__).parent / "results"
V0P6_RESULTS = REPO / "experiments" / "005_ecomd_v0p6" / "results"
REF_RESULTS = REPO / "experiments" / "000_reference_values" / "results"


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


def run_variant(config_path: Path) -> None:
    cfg = yaml.safe_load(config_path.read_text())
    variant = cfg.get("variant", config_path.stem)
    log.info(f"running ablation variant: {variant}")

    sim_cfg_dict = dict(cfg["simulator"])
    train_cfg = dict(cfg["training"])
    eval_cfg = dict(cfg["evaluation"])

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
             f"leverage_sum={targets.leverage_sum:+.3f} hill_alpha={targets.hill_alpha:.2f}")

    simulator_config = EcoMDConfig(**sim_cfg_dict)
    torch.manual_seed(train_cfg["seed"])
    sim = EcoMDSimulator(simulator_config)
    n_params = sum(p.numel() for p in sim.parameters())
    log.info(f"built sim: {n_params} params (body={simulator_config.mace_body_order}, "
             f"k={simulator_config.mace_k}, LN={simulator_config.mace_use_layernorm})")

    OUT.mkdir(parents=True, exist_ok=True)

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
    log.info(f"train done: {t_train:.1f}s, final loss={history[-1]['total']:.3f}")

    (OUT / f"{variant}_training_log.json").write_text(json.dumps({
        "variant": variant,
        "config": {"simulator": sim_cfg_dict, "training": train_cfg, "evaluation": eval_cfg},
        "targets": asdict(targets),
        "history": history,
        "train_time_seconds": t_train,
    }, indent=2))

    log.info(f"evaluating {eval_cfg['n_realizations']} realizations × {eval_cfg['eval_steps']} steps")
    t0 = time.time()
    eval_out = evaluate(sim, eval_cfg["n_realizations"], eval_cfg["eval_steps"])
    t_eval = time.time() - t0
    log.info(f"eval done: {t_eval:.1f}s")

    (OUT / f"{variant}_stylized_facts.json").write_text(json.dumps({
        "variant": variant,
        "aggregated": eval_out["aggregated"],
        "realizations": eval_out["realizations"],
        "eval_time_seconds": t_eval,
    }, indent=2))

    agg = eval_out["aggregated"]
    acf = agg.get("acf_squared_returns", {}).get("mean", float("nan"))
    lev = agg.get("leverage_effect", {}).get("mean", float("nan"))
    hill = agg.get("hill_tail_index", {}).get("mean", float("nan"))
    log.info(f"{variant} eval: acf(r²)={acf:+.3f}  leverage={lev:+.3f}  hill={hill:+.2f}")
    log.info(f"→ target:  acf(r²)=+0.221  leverage=-0.863  hill=+2.67")
    log.info(f"→ v0.6:    acf(r²)=+0.306  leverage=-2.815  hill=+5.35")
    print(f"\n{variant:<20}  acf(r²)={acf:+.4f}  lev={lev:+.3f}  hill={hill:+.2f}  "
          f"(train {t_train:.0f}s + eval {t_eval:.0f}s)")


def summarize() -> None:
    """Build results/ablation_summary.md from whichever variants have run."""
    OUT.mkdir(parents=True, exist_ok=True)

    real_path = REF_RESULTS / "stylized_facts_spx_2015-2026_daily.json"
    real = json.loads(real_path.read_text()) if real_path.exists() else {}
    real_facts = {k: (v.get("estimate") if isinstance(v, dict) else v)
                  for k, v in (real.get("results") or {}).items()}

    v0p6_path = V0P6_RESULTS / "ecomd_v0p6_stylized_facts.json"
    v0p6 = json.loads(v0p6_path.read_text()) if v0p6_path.exists() else {}
    v0p6_agg = v0p6.get("aggregated", {})

    variants = {}
    for p in sorted(OUT.glob("*_stylized_facts.json")):
        name = p.stem.replace("_stylized_facts", "")
        d = json.loads(p.read_text())
        variants[name] = d.get("aggregated", {})

    if not variants:
        print("No variant results found in results/. Run at least one config first.")
        return

    metrics = [
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

    def fmt(v: Any) -> str:
        if isinstance(v, dict) and "mean" in v:
            return f"{v['mean']:+.3f}"
        if isinstance(v, (int, float)) and np.isfinite(v):
            return f"{v:+.3f}"
        return "—"

    lines = ["# EcoMD v1 ablation — stylized-fact comparison",
             "",
             "All variants share v0.6's training recipe (Student-t noise, learnable β, 80 iter, chunk=32,",
             "warmup=16, eval 2000 steps × 3 realizations). Architecture variation only.",
             ""]

    cols = ["metric", "rule", "real SPX", "v0.6"] + sorted(variants.keys())
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("|" + "---|" * len(cols))
    for label, key, rule in metrics:
        row = [label, rule, fmt(real_facts.get(key)), fmt(v0p6_agg.get(key))]
        for name in sorted(variants.keys()):
            row.append(fmt(variants[name].get(key)))
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("## Headline: acf(r²) across variants")
    lines.append("")
    lines.append("| model | acf(r²) | leverage | hill |")
    lines.append("|---|---|---|---|")
    lines.append(f"| real SPX daily | {fmt(real_facts.get('acf_squared_returns'))} | "
                 f"{fmt(real_facts.get('leverage_effect'))} | {fmt(real_facts.get('hill_tail_index'))} |")
    lines.append(f"| v0.6 trained | {fmt(v0p6_agg.get('acf_squared_returns'))} | "
                 f"{fmt(v0p6_agg.get('leverage_effect'))} | {fmt(v0p6_agg.get('hill_tail_index'))} |")
    for name in sorted(variants.keys()):
        a = variants[name]
        lines.append(f"| v1 {name} | {fmt(a.get('acf_squared_returns'))} | "
                     f"{fmt(a.get('leverage_effect'))} | {fmt(a.get('hill_tail_index'))} |")

    md = "\n".join(lines)
    (OUT / "ablation_summary.md").write_text(md)
    print(md)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="path to config_<variant>.yaml")
    parser.add_argument("--summarize", action="store_true", help="build summary table")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    if args.summarize:
        summarize()
        return
    if not args.config:
        parser.error("either --config <path> or --summarize is required")
    run_variant(Path(args.config))


if __name__ == "__main__":
    main()
