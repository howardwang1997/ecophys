"""EcoMD v0 — train on SPX daily, evaluate stylized facts, compare with baselines.

Usage:
  python experiments/003_ecomd_v0/run.py             # full demo run (slow-ish on CPU)
  python experiments/003_ecomd_v0/run.py --smoke     # fast smoke test

Outputs (under experiments/003_ecomd_v0/results/):
  training_log.json             — per-iter loss trace + grad norms
  ecomd_stylized_facts.json     — per-realization + aggregated facts
  four_way_comparison.md        — real / GARCH / LM99 / EcoMD comparison
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
from ecomd.training.losses import (
    LossWeights,
    MomentTargets,
    build_targets_from_returns,
    moment_matching_loss,
)

log = logging.getLogger("ecomd_v0")

REPO = Path(__file__).resolve().parents[2]
RAW_DIR = REPO / "data" / "raw"
REF_RESULTS = REPO / "experiments" / "000_reference_values" / "results"
LM_RESULTS = REPO / "experiments" / "001_lux_marchesi_baseline" / "results"
GARCH_RESULTS = REPO / "experiments" / "002_garch_baseline" / "results"
OUT = Path(__file__).parent / "results"


# ─── Data loading (mirrors other experiments) ───────────────────────────────


def _read_yfinance(symbol: str) -> pd.DataFrame:
    root = RAW_DIR / "yfinance" / "interval=1d" / f"symbol={symbol}"
    frames = [pd.read_parquet(p) for p in sorted(root.glob("year=*.parquet"))]
    return pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)


def _spx_returns() -> np.ndarray:
    df = _read_yfinance("^GSPC")
    col = "adjusted_close" if "adjusted_close" in df.columns else "close"
    return log_returns_from_prices(df[col].to_numpy())


# ─── Training loop ──────────────────────────────────────────────────────────


def train_ecomd(
    sim: EcoMDSimulator,
    targets: MomentTargets,
    *,
    n_iters: int,
    chunk_steps: int,
    lr: float,
    grad_clip: float,
    weights: LossWeights,
    seed: int,
) -> list[dict[str, Any]]:
    """Truncated-BPTT training loop.

    At each iter: sample a fresh initial state, roll out `chunk_steps` with
    gradient on, compute loss against moment targets, step optimizer. Log
    loss + grad norm per iter.
    """
    device = sim.device
    optim = torch.optim.Adam(sim.parameters(), lr=lr)
    gen = torch.Generator(device=device)
    gen.manual_seed(seed)

    history: list[dict[str, Any]] = []
    for it in range(n_iters):
        optim.zero_grad()
        s = sim.init_state(generator=gen)
        s_prev = s.detach().clone()
        price_state = sim.init_price()

        _, _, traj, _ = sim.rollout_chunk(
            s, s_prev, price_state,
            n_steps=chunk_steps,
            generator=gen,
            create_graph=True,
        )
        sim_returns = traj.log_returns[1:]  # drop the t=0 zero-return step
        out = moment_matching_loss(sim_returns, targets, weights)
        total = out["total"]
        total.backward()

        # gradient norm for logging
        with torch.no_grad():
            grad_norm = torch.tensor(0.0)
            for p in sim.parameters():
                if p.grad is not None:
                    grad_norm = grad_norm + p.grad.detach().pow(2).sum()
            grad_norm = grad_norm.sqrt()
        torch.nn.utils.clip_grad_norm_(sim.parameters(), grad_clip)
        optim.step()

        rec = {
            "iter": it,
            "total": float(total.item()),
            "acf_sq_dev": float(out["acf_sq"].item()),
            "leverage_dev": float(out["leverage"].item()),
            "hill_dev": float(out["hill"].item()),
            "acf_sim": float(out["acf_sim"].item()),
            "leverage_sim": float(out["leverage_sim"].item()),
            "hill_sim": float(out["hill_sim"].item()),
            "grad_norm": float(grad_norm.item()),
            "gamma": float(sim.gamma.item()),
            "temperature": float(sim.temperature.item()),
        }
        history.append(rec)
        if it == 0 or (it + 1) % max(1, n_iters // 10) == 0:
            log.info(
                f"it={it:3d} total={rec['total']:.4f} "
                f"acf_sim={rec['acf_sim']:+.3f} lev_sim={rec['leverage_sim']:+.3f} "
                f"hill_sim={rec['hill_sim']:.2f} grad_norm={rec['grad_norm']:.2e}"
            )
    return history


# ─── Evaluation rollouts ────────────────────────────────────────────────────


def evaluate(sim: EcoMDSimulator, n_realizations: int, n_steps: int) -> dict[str, Any]:
    realizations = []
    for r_idx in range(n_realizations):
        traj = sim.run(n_steps=n_steps, seed=1000 + r_idx)
        returns = traj.log_returns_np()[1:]  # drop t=0
        volumes = traj.volumes_np()[1:]
        facts = compute_all(returns, volume=volumes)
        realizations.append({
            "seed": 1000 + r_idx,
            "facts": {k: v.to_dict() for k, v in facts.items()},
        })

    # aggregate
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


# ─── Comparison table ───────────────────────────────────────────────────────


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
    """Aggregate mean±std per metric from a list of realization dicts with `results` key."""
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


def build_four_way_comparison(ecomd_eval: dict[str, Any], target_dataset: str = "spx") -> str:
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

    ecomd_agg = ecomd_eval["aggregated"]

    lines: list[str] = []
    lines.append(f"# Four-way comparison — real ({target_dataset}) / GARCH(1,1)-t / LM99 / EcoMD v0")
    lines.append("")
    lines.append(f"Trained on {target_dataset} moment targets (ACF(r²), Σ leverage, Hill α).")
    lines.append("EcoMD evaluated with 5 rollouts from the trained model; LM99 / GARCH reused from experiments 001 / 002.")
    lines.append("")
    lines.append(f"| metric | expected | real ({target_dataset}) | GARCH(1,1)-t | LM99 | EcoMD v0 |")
    lines.append("|---|---|---|---|---|---|")
    for label, key, expected in ROWS:
        real_v = real_facts.get(key)
        g = garch_for_dataset.get(key)
        lm = lm_agg.get(key)
        ec = ecomd_agg.get(key)
        real_s = f"{real_v:+.3f}" if isinstance(real_v, (int, float)) and np.isfinite(real_v) else "—"
        g_s = f"{g['mean']:+.3f} ± {g['std']:.3f}" if g else "—"
        lm_s = f"{lm['mean']:+.3f} ± {lm['std']:.3f}" if lm else "—"
        ec_s = f"{ec['mean']:+.3f} ± {ec['std']:.3f}" if ec else "—"
        lines.append(f"| {label} | {expected} | {real_s} | {g_s} | {lm_s} | {ec_s} |")

    lines.append("")
    lines.append("## Scoreboard (loose tolerance)")
    lines.append("")
    lines.append("| metric | GARCH | LM99 | EcoMD v0 |")
    lines.append("|---|---|---|---|")
    gt = lt = et = 0
    for label, key, _ in ROWS:
        gv = (garch_for_dataset.get(key) or {}).get("mean")
        lv = (lm_agg.get(key) or {}).get("mean")
        ev = (ecomd_agg.get(key) or {}).get("mean")
        gc = _score(gv, key); lc = _score(lv, key); ec = _score(ev, key)
        gt += int(gc); lt += int(lc); et += int(ec)
        lines.append(f"| {label} | {'✓' if gc else '✗'} | {'✓' if lc else '✗'} | {'✓' if ec else '✗'} |")
    lines.append(f"| **Total** | **{gt}/11** | **{lt}/11** | **{et}/11** |")
    return "\n".join(lines)


# ─── Main ───────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="tiny fast run (for CI / sanity)")
    parser.add_argument("--config", default=str(Path(__file__).parent / "config.yaml"))
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    OUT.mkdir(parents=True, exist_ok=True)

    cfg = yaml.safe_load(Path(args.config).read_text())

    # Apply smoke overrides
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
        log.info("SMOKE MODE — reduced scale")

    log.info(f"simulator config: {sim_cfg_dict}")
    log.info(f"training config: {train_cfg}")
    log.info(f"evaluation config: {eval_cfg}")

    # Build targets from real SPX data
    log.info("loading SPX returns and building moment targets...")
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

    # Build simulator
    simulator_config = EcoMDConfig(**sim_cfg_dict)
    torch.manual_seed(train_cfg["seed"])
    sim = EcoMDSimulator(simulator_config)
    n_params = sum(p.numel() for p in sim.parameters())
    log.info(f"EcoMDSimulator built: {n_params} parameters")

    # Train
    t0 = time.time()
    history = train_ecomd(
        sim, targets,
        n_iters=train_cfg["n_iters"],
        chunk_steps=train_cfg["chunk_steps"],
        lr=train_cfg["lr"],
        grad_clip=train_cfg["grad_clip_max_norm"],
        weights=weights,
        seed=train_cfg["seed"],
    )
    t_train = time.time() - t0
    log.info(f"training finished in {t_train:.1f}s")

    (OUT / "training_log.json").write_text(json.dumps({
        "config": {"simulator": sim_cfg_dict, "training": train_cfg, "evaluation": eval_cfg},
        "targets": asdict(targets),
        "history": history,
        "train_time_seconds": t_train,
    }, indent=2))

    # Evaluate
    log.info(f"evaluating: {eval_cfg['n_realizations']} rollouts × {eval_cfg['eval_steps']} steps...")
    t0 = time.time()
    eval_out = evaluate(sim, eval_cfg["n_realizations"], eval_cfg["eval_steps"])
    t_eval = time.time() - t0
    log.info(f"evaluation finished in {t_eval:.1f}s")

    (OUT / "ecomd_stylized_facts.json").write_text(json.dumps({
        "aggregated": eval_out["aggregated"],
        "realizations": eval_out["realizations"],
        "eval_time_seconds": t_eval,
    }, indent=2))

    # Comparison table
    md = build_four_way_comparison(eval_out, target_dataset=train_cfg["target_dataset"])
    (OUT / "four_way_comparison.md").write_text(md)
    print(md)

    log.info(f"wrote outputs under {OUT}/")


if __name__ == "__main__":
    main()
