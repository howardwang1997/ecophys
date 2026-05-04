"""E3a: Analytical AR(1)-residual analysis using existing inference_rank_0.json ACF.

For each of 50 seeds × 4 realizations in 064, we already have:
  - facts.autocorr_returns.diagnostic.acf  : ACF of returns at lags 0..30
  - facts.autocorr_returns.estimate        : mean |ACF[1..20]|  (the metric scored)

We:
  1. Confirm the metric definition (mean |ACF[1..20]|).
  2. Fit AR(1) with rho_hat = ACF[1] for each realization.
  3. Compute analytical post-whitening residual ACF (for stationary AR(1) signal,
     residual ACF[k] vanishes; for ARMA-like signal, partial cancellation).
  4. Report pre/post mean |ACF[1..20]| and pass-rate against band (-0.1, +0.20).

This tells us:
  - How much of the autocorr_returns failure is "pure AR(1) drift" (curable by
    post-hoc whitening that any honest reviewer will demand).
  - Whether the post-whitening series still has structured autocorrelation
    (i.e., the simulator has memory beyond simple drift).

Note this CANNOT recompute facts that need raw returns
(hurst_abs_r, hill_tail, acf_squared, leverage, volume_volatility, zumbach,
gain_loss_asymmetry, conditional_kurtosis, intermittency_fano, agg_gaussian).
That's E3b.

Run:
  conda run -n ecophys python scripts/diagnose_ar1_residual_acf.py
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


def whiten_acf_ar1(rho: float, acf: np.ndarray) -> np.ndarray:
    """Given ACF of x_t and AR(1) coefficient rho, compute approximate ACF of
    residual eps_t = x_t - rho * x_{t-1}.

    For pure AR(1) x_t = rho x_{t-1} + eps_t, eps_t is iid → ACF_eps[k] = 0 for k≥1.
    For general weakly-stationary x with cov γ_x[k] = σ² · ACF_x[k]:
        Cov(eps_t, eps_{t-k}) = γ_x[k] - rho * (γ_x[k-1] + γ_x[k+1]) + rho² * γ_x[k]
                              = γ_x[k] (1 + rho²) - rho * (γ_x[k-1] + γ_x[k+1])
    Var(eps_t) = γ_x[0] (1 + rho²) - 2 rho γ_x[1] = σ²·(1 + rho² - 2 rho ACF_x[1])
    Since ACF_x[1] = rho for sample-AR(1), Var(eps) = σ²·(1 - rho²).
    Then ACF_eps[k] = numerator / Var(eps).
    """
    K = len(acf)
    out = np.zeros(K)
    out[0] = 1.0
    var_x = 1.0  # ACF normalized
    var_eps = var_x * (1.0 + rho * rho) - 2 * rho * acf[1]
    if var_eps <= 1e-9:
        return np.zeros(K)
    for k in range(1, K - 1):
        num = acf[k] * (1.0 + rho * rho) - rho * (acf[k - 1] + acf[k + 1])
        out[k] = num / var_eps
    # last lag: use one-sided extrapolation (assume acf[K] decays like acf[K-1] * acf[1])
    if K >= 2:
        acf_K_extrap = acf[K - 1] * acf[1]
        num = acf[K - 1] * (1.0 + rho * rho) - rho * (acf[K - 2] + acf_K_extrap)
        out[K - 1] = num / var_eps
    return out


def main() -> None:
    BAND = (-0.1, 0.20)
    rows = []

    for d in sorted(SRC.glob("results_p_4_2__2_1_seed*")):
        m = re.search(r"seed(\d+)$", d.name)
        if not m:
            continue
        seed = int(m.group(1))
        f = d / "inference_rank_0.json"
        if not f.exists():
            continue
        recs = json.loads(f.read_text())
        for r_idx, rec in enumerate(recs):
            ar = rec["facts"].get("autocorr_returns")
            if ar is None:
                continue
            acf = np.array(ar["diagnostic"]["acf"])
            est = ar["estimate"]
            rho = float(acf[1])
            # Recompute pre to verify metric definition
            pre_metric = float(np.mean(np.abs(acf[1:21])))
            # Whiten
            acf_w = whiten_acf_ar1(rho, acf)
            post_metric = float(np.mean(np.abs(acf_w[1:21])))
            rows.append(dict(
                seed=seed,
                realization=r_idx,
                rho_hat=rho,
                acf_lag1=float(acf[1]),
                acf_lag5=float(acf[5]),
                acf_lag10=float(acf[10]),
                acf_lag20=float(acf[20]),
                pre_metric=pre_metric,
                pre_metric_reported=est,
                post_metric=post_metric,
                pre_pass=int(BAND[0] <= pre_metric <= BAND[1]),
                post_pass=int(BAND[0] <= post_metric <= BAND[1]),
            ))

    n = len(rows)
    pre = [r["pre_metric"] for r in rows]
    post = [r["post_metric"] for r in rows]
    rhos = [r["rho_hat"] for r in rows]

    pre_pass = sum(r["pre_pass"] for r in rows)
    post_pass = sum(r["post_pass"] for r in rows)

    md = []
    md.append("# E3a — Analytical AR(1)-residual ACF analysis (064 winner_50seed_repro)\n")
    md.append("## What this measures")
    md.append("Sample raw return ACF was computed in 064 inference. Here we fit AR(1) per realization "
              "(rho = ACF[1]), analytically whiten the ACF, and recompute the autocorr_returns metric "
              "(mean |ACF| over lags 1..20).")
    md.append("- **pre_metric** = mean |ACF_raw|  (matches `autocorr_returns.estimate`)")
    md.append("- **post_metric** = mean |ACF_residual|  (after AR(1) whitening)")
    md.append(f"- **band** = {BAND} (pass = white-noise-like)\n")
    md.append("## Population summary\n")
    md.append(f"- realizations scanned: {n} (50 seeds × 4 rollouts each)")
    md.append(f"- rho_hat (AR(1) coef): mean={statistics.mean(rhos):.3f}  median={statistics.median(rhos):.3f}  "
              f"min={min(rhos):.3f}  max={max(rhos):.3f}")
    md.append(f"- pre_metric:  mean={statistics.mean(pre):.3f}  pass={pre_pass}/{n} ({pre_pass/n*100:.1f}%)")
    md.append(f"- post_metric: mean={statistics.mean(post):.3f}  pass={post_pass}/{n} ({post_pass/n*100:.1f}%)\n")

    # ACF shape evidence
    md.append("## Is the autocorr structure pure AR(1)?\n")
    md.append("If yes, ACF[k] should equal rho^k. We measure deviation from pure AR(1):\n")
    md.append("| lag | mean ACF observed | mean rho^lag (pure AR(1) expected) | excess |")
    md.append("|---:|---:|---:|---:|")
    for lag in (1, 2, 3, 5, 10, 20):
        obs = []
        exp = []
        for r in rows:
            rho = r["rho_hat"]
            # we have lag1 directly, others need the per-row acf which we didn't save
            # compute from what we stored
            if lag == 1: o = r["acf_lag1"]
            elif lag == 5: o = r["acf_lag5"]
            elif lag == 10: o = r["acf_lag10"]
            elif lag == 20: o = r["acf_lag20"]
            else: o = None
            if o is None: continue
            obs.append(o)
            exp.append(rho ** lag)
        if obs:
            md.append(f"| {lag} | {statistics.mean(obs):+.3f} | {statistics.mean(exp):+.3f} | "
                      f"{statistics.mean(obs)-statistics.mean(exp):+.3f} |")
    md.append("")

    # Per-seed (one row per seed, averaging realizations)
    md.append("## Per-seed (avg of 4 realizations)\n")
    md.append("| seed | rho_hat | pre_metric | post_metric | pre_pass | post_pass |")
    md.append("|---:|---:|---:|---:|---:|---:|")
    by_seed: dict[int, list] = {}
    for r in rows:
        by_seed.setdefault(r["seed"], []).append(r)
    for seed in sorted(by_seed):
        lst = by_seed[seed]
        rho = statistics.mean(r["rho_hat"] for r in lst)
        pr = statistics.mean(r["pre_metric"] for r in lst)
        po = statistics.mean(r["post_metric"] for r in lst)
        pp = sum(r["pre_pass"] for r in lst)
        ppp = sum(r["post_pass"] for r in lst)
        md.append(f"| {seed} | {rho:.3f} | {pr:.3f} | {po:.3f} | {pp}/4 | {ppp}/4 |")
    md.append("")

    md.append("## Verdict\n")
    if post_pass >= 0.9 * n:
        md.append(f"**AR(1) FULLY EXPLAINS THE DRIFT**: {post_pass}/{n} ({post_pass/n*100:.0f}%) realizations pass after whitening.")
        md.append("→ The autocorr_returns failure is essentially the lag-1 component alone.")
        md.append("→ Reviewer-2 verdict: 'this fact only fails because returns are AR(1); other facts may share the artifact'.")
        md.append("→ Action: must check whether vol-clustering (acf_sq²) and Hurst survive whitening (E3b).")
    elif post_pass >= 0.5 * n:
        md.append(f"**AR(1) PARTIALLY EXPLAINS**: {post_pass}/{n} pass after whitening.")
        md.append("→ Some realizations have structure beyond pure AR(1) (ARMA or long-memory).")
    else:
        md.append(f"**AR(1) DOES NOT EXPLAIN**: only {post_pass}/{n} pass after whitening.")
        md.append("→ The autocorr structure is NOT pure drift; deeper memory is present.")

    md_path = OUT / "ar1_residual_analysis.md"
    md_path.write_text("\n".join(md) + "\n")
    print(f"wrote {md_path}")
    print()
    print("\n".join(md))


if __name__ == "__main__":
    main()
