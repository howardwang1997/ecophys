"""E3b post-processor — once H20 has produced trajectory_rank0_r{0,1}.npz files
for the 064 winner seeds, compute all 11 stylized facts on raw returns AND on
AR(1)-whitened residuals, and produce the comparison table.

Run after `scripts/h20_e3b_save_trajectories.sh` finishes on H20 and trajectories
are pulled to Mac.

Usage:
  conda run -n ecophys python scripts/diagnose_ar1_residual_full_from_traj.py
"""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "experiments" / "064_winner_50seed_repro"
OUT = REPO / "experiments" / "067_ar1_diagnostics"
OUT.mkdir(exist_ok=True)

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
    if len(r) < 3:
        return r.copy(), 0.0
    x = r[:-1]
    y = r[1:]
    rho = float(np.dot(x, y) / max(np.dot(x, x), 1e-12))
    eps = y - rho * x
    return eps, rho


def score_facts_dict(facts: dict) -> tuple[int, dict]:
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
    from ecomd.eval.stylized_facts import compute_all

    rows = []
    seed_dirs = sorted(SRC.glob("results_p_4_2__2_1_seed*"))
    n_with_traj = 0
    for d in seed_dirs:
        m = re.search(r"seed(\d+)$", d.name)
        if not m:
            continue
        seed = int(m.group(1))
        for r_idx in range(8):
            traj_path = d / f"trajectory_rank0_r{r_idx}.npz"
            if not traj_path.exists():
                continue
            n_with_traj += 1
            data = np.load(traj_path)
            returns = data["log_returns"]
            volumes = data["volumes"] if "volumes" in data.files else None

            facts_raw = compute_all(returns, volume=volumes)
            n_raw, per_raw = score_facts_dict(facts_raw)

            eps, rho = ar1_residual(returns)
            volumes_eps = volumes[1:] if volumes is not None else None
            facts_eps = compute_all(eps, volume=volumes_eps)
            n_eps, per_eps = score_facts_dict(facts_eps)

            rows.append(dict(
                seed=seed,
                realization=r_idx,
                rho_hat=rho,
                pass_raw=n_raw,
                pass_residual=n_eps,
                per_fact_raw=per_raw,
                per_fact_residual=per_eps,
            ))

    if not rows:
        print("No trajectories found. Run scripts/h20_e3b_save_trajectories.sh on H20 first.")
        return

    md = []
    md.append("# E3b — Full re-eval on AR(1)-whitened residuals (50 064 seeds)\n")
    md.append(f"Realizations scanned: {len(rows)} (over {len(seed_dirs)} seeds).\n")

    avg_raw = np.mean([r["pass_raw"] for r in rows])
    avg_eps = np.mean([r["pass_residual"] for r in rows])
    avg_delta = avg_eps - avg_raw
    md.append(f"**Mean pass — raw:** {avg_raw:.2f}/11")
    md.append(f"**Mean pass — AR(1) residual:** {avg_eps:.2f}/11")
    md.append(f"**Delta:** {avg_delta:+.2f}\n")

    md.append("## Per-fact pass rate change\n")
    md.append("| fact | raw_pass | residual_pass | delta |")
    md.append("|---|---:|---:|---:|")
    for k in BANDS:
        rp = sum(1 for r in rows if r["per_fact_raw"][k].get("pass"))
        ep = sum(1 for r in rows if r["per_fact_residual"][k].get("pass"))
        md.append(f"| {k} | {rp}/{len(rows)} | {ep}/{len(rows)} | {ep-rp:+d} |")
    md.append("")

    md.append("## Per-fact mean values\n")
    md.append("| fact | band | mean_raw | mean_residual |")
    md.append("|---|---|---:|---:|")
    for k, (lo, hi) in BANDS.items():
        raws = [r["per_fact_raw"][k].get("value") for r in rows
                if r["per_fact_raw"][k].get("value") is not None]
        eps_ = [r["per_fact_residual"][k].get("value") for r in rows
                if r["per_fact_residual"][k].get("value") is not None]
        mr = np.mean(raws) if raws else float("nan")
        me = np.mean(eps_) if eps_ else float("nan")
        md.append(f"| {k} | [{lo},{hi}] | {mr:+.3f} | {me:+.3f} |")
    md.append("")

    md.append("## Per-seed (avg of realizations)\n")
    md.append("| seed | n | rho_hat | pass_raw | pass_residual |")
    md.append("|---:|---:|---:|---:|---:|")
    by_seed: dict[int, list] = {}
    for r in rows:
        by_seed.setdefault(r["seed"], []).append(r)
    for s in sorted(by_seed):
        lst = by_seed[s]
        rho = statistics.mean(r["rho_hat"] for r in lst)
        pr = statistics.mean(r["pass_raw"] for r in lst)
        po = statistics.mean(r["pass_residual"] for r in lst)
        md.append(f"| {s} | {len(lst)} | {rho:.3f} | {pr:.2f} | {po:.2f} |")
    md.append("")

    (OUT / "ar1_full_summary.md").write_text("\n".join(md) + "\n")
    print(f"wrote {OUT / 'ar1_full_summary.md'}")
    print()
    print("\n".join(md[:30]))


if __name__ == "__main__":
    main()
