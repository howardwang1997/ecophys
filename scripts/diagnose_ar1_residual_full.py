"""E3b: Re-run inference for selected 064 seeds, compute all 11 stylized facts
on raw returns AND on AR(1)-whitened residuals. Compare pass-counts.

This addresses Reviewer-2's likely attack: 'after AR(1) whitening, do other
facts (acf_squared_returns, dfa_hurst, leverage, etc.) survive — or are
they artifacts of the same drift?'

Mac CPU only — designed to run on a handful of representative seeds.
For population-level conclusion we'd need this on H20 across all 50 seeds.

Usage:
  conda run -n ecophys python scripts/diagnose_ar1_residual_full.py \\
      --seeds 51 70 60 39 38 79 74 82  \\
      --n-realizations 1   \\
      --n-steps 4000

Outputs:
  experiments/067_ar1_diagnostics/full_eval/seed{S}_realization{R}.json
  experiments/067_ar1_diagnostics/ar1_full_summary.md
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import yaml

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "experiments" / "064_winner_50seed_repro"
OUT = REPO / "experiments" / "067_ar1_diagnostics"
OUT_FULL = OUT / "full_eval"
OUT_FULL.mkdir(parents=True, exist_ok=True)

BANDS = {
    "autocorr_returns": (-0.1, 0.20),
    "hill_tail_index": (2.0, 4.0),
    "gain_loss_asymmetry": (-30.0, -3.0),
    "aggregational_gaussianity": (10, 200),
    "intermittency_fano": (5, 100),
    "acf_squared_returns": (0.15, 0.55),
    "conditional_kurtosis": (-1.0, 3.0),
    "dfa_hurst_abs_r": (0.6, 0.9),
    "leverage_effect": (-6.0, -0.5),
    "volume_volatility_corr": (0.3, 0.8),
    "zumbach_asymmetry": (0.001, 0.5),
}


def ar1_residual(r: np.ndarray) -> tuple[np.ndarray, float]:
    """Fit AR(1) by least squares; return residual series eps and rho_hat."""
    if len(r) < 3:
        return r.copy(), 0.0
    x = r[:-1]
    y = r[1:]
    rho = float(np.dot(x, y) / max(np.dot(x, x), 1e-12))
    eps = y - rho * x
    return eps, rho


def score_facts(facts: dict) -> tuple[int, dict]:
    n_pass = 0
    per = {}
    for k, (lo, hi) in BANDS.items():
        if k not in facts:
            per[k] = {"value": None, "pass": False}
            continue
        v = facts[k].estimate if hasattr(facts[k], "estimate") else facts[k].get("estimate")
        if v is None or not np.isfinite(v):
            per[k] = {"value": v, "pass": False}
            continue
        ok = lo <= v <= hi
        per[k] = {"value": float(v), "pass": bool(ok), "band": [lo, hi]}
        if ok:
            n_pass += 1
    return n_pass, per


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    parser.add_argument("--n-realizations", type=int, default=1)
    parser.add_argument("--n-steps", type=int, default=4000)
    parser.add_argument("--seed-base", type=int, default=10000)
    args = parser.parse_args()

    # Lazy imports so timing doesn't include torch import
    from ecomd.eval.stylized_facts import compute_all
    from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator

    summary_rows = []
    for seed in args.seeds:
        d = SRC / f"results_p_4_2__2_1_seed{seed}"
        ckpt_path = d / "checkpoint.pt"
        cfg_path = SRC / f"config_p_4_2__2_1_seed{seed}.yaml"
        if not ckpt_path.exists() or not cfg_path.exists():
            print(f"skip seed={seed}: missing files")
            continue

        cfg = yaml.safe_load(cfg_path.read_text())
        sim_cfg = EcoMDConfig(**dict(cfg["simulator"]))
        sim = EcoMDSimulator(sim_cfg)
        ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        sim.load_state_dict(ck["sim_state_dict"])
        sim.eval()

        for r_idx in range(args.n_realizations):
            roll_seed = args.seed_base + r_idx
            t0 = time.time()
            traj = sim.run(n_steps=args.n_steps, seed=roll_seed)
            dt = time.time() - t0
            returns = traj.log_returns_np()[1:]
            volumes = traj.volumes_np()[1:]
            print(f"seed={seed} r={r_idx} rollout took {dt:.1f}s, n_returns={len(returns)}")

            # Raw facts
            facts_raw = compute_all(returns, volume=volumes)
            n_raw, per_raw = score_facts(facts_raw)

            # AR(1) residuals — re-aligned with volumes (drop first vol to match)
            eps, rho = ar1_residual(returns)
            volumes_eps = volumes[1:]
            facts_eps = compute_all(eps, volume=volumes_eps)
            n_eps, per_eps = score_facts(facts_eps)

            row = dict(
                seed=seed,
                realization=r_idx,
                rho_hat=rho,
                rollout_time_s=dt,
                pass_raw=n_raw,
                pass_residual=n_eps,
                per_fact_raw=per_raw,
                per_fact_residual=per_eps,
            )
            summary_rows.append(row)

            (OUT_FULL / f"seed{seed}_r{r_idx}.json").write_text(json.dumps(row, indent=2))

    # Summary markdown
    md = []
    md.append("# E3b — Full re-eval on AR(1)-whitened residuals\n")
    md.append(f"Re-ran inference for {len(args.seeds)} seeds × {args.n_realizations} realizations, "
              f"n_steps={args.n_steps}.")
    md.append("Computed all 11 stylized facts on raw returns AND on AR(1)-residuals "
              "(eps_t = r_t - rho_hat * r_{t-1}).\n")
    md.append("## Pass count: raw vs AR(1)-residual\n")
    md.append("| seed | r | rho_hat | pass_raw | pass_residual | delta |")
    md.append("|---:|---:|---:|---:|---:|---:|")
    for row in summary_rows:
        delta = row["pass_residual"] - row["pass_raw"]
        sign = "+" if delta > 0 else ("" if delta == 0 else "")
        md.append(f"| {row['seed']} | {row['realization']} | {row['rho_hat']:.3f} | "
                  f"{row['pass_raw']}/11 | {row['pass_residual']}/11 | {sign}{delta} |")
    md.append("")

    if summary_rows:
        avg_raw = np.mean([r["pass_raw"] for r in summary_rows])
        avg_eps = np.mean([r["pass_residual"] for r in summary_rows])
        md.append(f"**Mean pass — raw:** {avg_raw:.2f}/11")
        md.append(f"**Mean pass — AR(1) residual:** {avg_eps:.2f}/11\n")

    md.append("## Per-fact pass rate change\n")
    md.append("| fact | raw_pass | residual_pass | delta |")
    md.append("|---|---:|---:|---:|")
    for k in BANDS:
        rp = sum(1 for r in summary_rows if r["per_fact_raw"][k].get("pass"))
        ep = sum(1 for r in summary_rows if r["per_fact_residual"][k].get("pass"))
        n = len(summary_rows)
        md.append(f"| {k} | {rp}/{n} | {ep}/{n} | {ep-rp:+d} |")
    md.append("")

    md.append("## Per-fact value change (mean across realizations)\n")
    md.append("| fact | band | mean_raw | mean_residual |")
    md.append("|---|---|---:|---:|")
    for k, (lo, hi) in BANDS.items():
        raws = [r["per_fact_raw"][k].get("value") for r in summary_rows
                if r["per_fact_raw"][k].get("value") is not None]
        eps_ = [r["per_fact_residual"][k].get("value") for r in summary_rows
                if r["per_fact_residual"][k].get("value") is not None]
        mr = np.mean(raws) if raws else float("nan")
        me = np.mean(eps_) if eps_ else float("nan")
        md.append(f"| {k} | [{lo},{hi}] | {mr:+.3f} | {me:+.3f} |")
    md.append("")

    (OUT / "ar1_full_summary.md").write_text("\n".join(md) + "\n")
    print(f"\nwrote {OUT / 'ar1_full_summary.md'}")
    print("\n".join(md))


if __name__ == "__main__":
    main()
