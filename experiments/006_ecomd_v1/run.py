"""EcoMD v1 (MACE-lite) — Mac smoke runner.

This is the Mac-only smoke entry point: verifies the full v0.5 + MACE-lite
pipeline runs end-to-end under small N, produces stylized facts, and writes
a 7-way comparison vs real / GARCH / LM99 / v0 / v0.5 / v0.6.

Real v1 training happens on H20 via ``scripts/h20_launch_v1.sh`` →
``ecomd.training.train_distributed``. This script does NOT launch H20.
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

log = logging.getLogger("ecomd_v1")

REPO = Path(__file__).resolve().parents[2]
RAW_DIR = REPO / "data" / "raw"
REF_RESULTS = REPO / "experiments" / "000_reference_values" / "results"
LM_RESULTS = REPO / "experiments" / "001_lux_marchesi_baseline" / "results"
GARCH_RESULTS = REPO / "experiments" / "002_garch_baseline" / "results"
V0_RESULTS = REPO / "experiments" / "003_ecomd_v0" / "results"
V0P5_RESULTS = REPO / "experiments" / "004_ecomd_v0p5" / "results"
V0P6_RESULTS = REPO / "experiments" / "005_ecomd_v0p6" / "results"
OUT = Path(__file__).parent / "results"


def _spx_returns() -> np.ndarray:
    # Prefer data/raw then fall back to data/sample
    for root in (RAW_DIR, REPO / "data" / "sample"):
        d = root / "yfinance" / "interval=1d" / "symbol=^GSPC"
        if d.exists():
            frames = [pd.read_parquet(p) for p in sorted(d.glob("year=*.parquet"))]
            if frames:
                df = pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)
                col = "adjusted_close" if "adjusted_close" in df.columns else "close"
                return log_returns_from_prices(df[col].to_numpy())
    raise FileNotFoundError("no ^GSPC yfinance data found in data/raw or data/sample")


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


def _agg_list(xs: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    if not xs:
        return {}
    keys = list(xs[0].get("results", {}).keys())
    out: dict[str, dict[str, float]] = {}
    for k in keys:
        vals = [float((r.get("results", {}).get(k) or {}).get("estimate"))
                for r in xs
                if isinstance((r.get("results", {}).get(k) or {}).get("estimate"), (int, float))
                and np.isfinite((r.get("results", {}).get(k) or {}).get("estimate"))]
        if vals:
            out[k] = {"mean": float(np.mean(vals)), "std": float(np.std(vals))}
    return out


def build_seven_way(v1_eval: dict[str, Any]) -> str:
    real_raw = _load_json(REF_RESULTS / "stylized_facts_spx_2015-2026_daily.json") or {}
    real_facts = {k: v.get("estimate") for k, v in (real_raw.get("results") or {}).items()
                  if isinstance(v, dict)}
    garch_raw = _load_json(GARCH_RESULTS / "garch_stylized_facts.json") or []
    garch_agg = next((f["aggregated"] for f in garch_raw if f.get("dataset") == "spx"), {})
    lm_raw = _load_json(LM_RESULTS / "lux_marchesi_stylized_facts.json") or []
    lm_agg = _agg_list(lm_raw) if isinstance(lm_raw, list) else {}
    v0_agg = (_load_json(V0_RESULTS / "ecomd_stylized_facts.json") or {}).get("aggregated", {})
    v0p5_agg = (_load_json(V0P5_RESULTS / "ecomd_v0p5_stylized_facts.json") or {}).get("aggregated", {})
    v0p6_agg = (_load_json(V0P6_RESULTS / "ecomd_v0p6_stylized_facts.json") or {}).get("aggregated", {})
    v1_agg = v1_eval["aggregated"]

    def fmt(v: Any) -> str:
        if isinstance(v, dict) and "mean" in v:
            return f"{v['mean']:+.3f} ± {v['std']:.3f}"
        if isinstance(v, (int, float)) and np.isfinite(v):
            return f"{v:+.3f}"
        return "—"

    lines = [
        "# Seven-way comparison — real (spx) / GARCH / LM99 / v0 / v0.5 / v0.6 / v1 (Mac smoke)",
        "",
        "v1 Mac smoke is **not** the real v1 number — real v1 training runs on H20",
        "via scripts/h20_launch_v1.sh. This table confirms the pipeline works end-to-end",
        "and gives a sanity-check floor at small N.",
        "",
        "| metric | expected | real | GARCH | LM99 | v0 | v0.5 | v0.6 | v1 Mac |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for label, key, expected in ROWS:
        lines.append("| " + " | ".join([
            label, expected,
            fmt(real_facts.get(key)),
            fmt(garch_agg.get(key)),
            fmt(lm_agg.get(key)),
            fmt(v0_agg.get(key)),
            fmt(v0p5_agg.get(key)),
            fmt(v0p6_agg.get(key)),
            fmt(v1_agg.get(key)),
        ]) + " |")
    lines.append("")
    lines.append("## Scoreboard")
    lines.append("")
    lines.append("| metric | GARCH | LM99 | v0 | v0.5 | v0.6 | v1 Mac |")
    lines.append("|---|---|---|---|---|---|---|")
    totals = {k: 0 for k in ("g", "lm", "v0", "v0p5", "v0p6", "v1")}
    for label, key, _ in ROWS:
        row = [label]
        for name, agg in [("g", garch_agg), ("lm", lm_agg), ("v0", v0_agg),
                          ("v0p5", v0p5_agg), ("v0p6", v0p6_agg), ("v1", v1_agg)]:
            val = (agg.get(key) or {}).get("mean")
            ok = _score(val, key)
            totals[name] += int(ok)
            row.append("✓" if ok else "✗")
        lines.append("| " + " | ".join(row) + " |")
    lines.append(f"| **Total** | **{totals['g']}/11** | **{totals['lm']}/11** "
                 f"| **{totals['v0']}/11** | **{totals['v0p5']}/11** "
                 f"| **{totals['v0p6']}/11** | **{totals['v1']}/11** |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(Path(__file__).parent / "config_mac_smoke.yaml"))
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    OUT.mkdir(parents=True, exist_ok=True)

    cfg = yaml.safe_load(Path(args.config).read_text())
    sim_cfg_dict = dict(cfg["simulator"])
    train_cfg = dict(cfg["training"])
    eval_cfg = dict(cfg["evaluation"])

    log.info(f"simulator config: {sim_cfg_dict}")
    log.info(f"training config: {train_cfg}")

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
    log.info(f"targets: acf_sq={targets.acf_sq_mean:.3f} leverage_sum={targets.leverage_sum:+.3f} "
             f"hill_alpha={targets.hill_alpha:.2f}")

    simulator_config = EcoMDConfig(**sim_cfg_dict)
    torch.manual_seed(train_cfg["seed"])
    sim = EcoMDSimulator(simulator_config)
    log.info(f"EcoMDSimulator built: {sum(p.numel() for p in sim.parameters())} parameters "
             f"(pairwise={sim.cfg.pairwise_kind}, body_order={sim.cfg.mace_body_order}, "
             f"K={sim.cfg.mace_n_classes}, k={sim.cfg.mace_k})")

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
        "targets": asdict(targets), "history": history,
        "train_time_seconds": t_train,
    }, indent=2))

    t0 = time.time()
    eval_out = evaluate(sim, eval_cfg["n_realizations"], eval_cfg["eval_steps"])
    t_eval = time.time() - t0
    log.info(f"evaluation finished in {t_eval:.1f}s")

    (OUT / "mace_smoke_stylized_facts.json").write_text(json.dumps({
        "aggregated": eval_out["aggregated"],
        "realizations": eval_out["realizations"],
        "eval_time_seconds": t_eval,
    }, indent=2))

    md = build_seven_way(eval_out)
    (OUT / "seven_way_comparison.md").write_text(md)
    print(md)
    log.info(f"wrote outputs under {OUT}/")


if __name__ == "__main__":
    main()
