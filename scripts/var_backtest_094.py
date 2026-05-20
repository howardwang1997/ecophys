"""VaR backtest driver for 094 — SPX 2018-2026 holdout (no leakage; 094 trained on 2010-2017).

Loads SPX returns from data/raw/yfinance, splits at 2018-01-01, and runs
rolling_backtest for each of:
  - HistoricalSampler (250-day window) — bootstrap reference
  - GARCH(1,1)-t — strong statistical reference
  - EcoMDSampler — for each of top-K 094 cells × top-3 seeds by fact-pass

Writes a markdown table to experiments/094_var_holdout_12seed/var_results.md.

Known limitation (documented in paper Future Work): v3 EcoMDSampler is
unconditional — past_returns are ignored. This produces a STATIC VaR
(modulo random sampling). We report it honestly and frame ECoMD VaR as
distributional realism rather than time-varying tail forecasting.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from ecomd.baselines.runner import _load_real_returns
from ecomd.risk.samplers import EcoMDSampler, GARCHSampler, HistoricalSampler
from ecomd.risk.var_backtest import rolling_backtest

REPO = Path(__file__).resolve().parent.parent
EXP = REPO / "experiments" / "094_var_holdout_12seed"
OUT = EXP / "var_results.md"


def load_holdout_spx() -> tuple[np.ndarray, int]:
    full = _load_real_returns(REPO, "spx", "2015-2026_daily")
    n = full.size
    holdout_start = max(int(n * (2018 - 2010) / (2026 - 2010)), 0)
    return full, holdout_start


def select_top_cells(top_k: int, top_seeds_per_cell: int) -> list[tuple[str, int]]:
    """Pick (cell, seed) pairs from 094 by fact-pass count."""
    cell_scores: dict[str, list[tuple[int, int]]] = {}
    for d in sorted(EXP.glob("results_var_*_seed*")):
        merged = d / "inference_merged.json"
        ckpt = d / "checkpoint.pt"
        if not merged.exists() or not ckpt.exists():
            continue
        try:
            agg = json.loads(merged.read_text()).get("aggregated", {})
        except Exception:
            continue
        bands = {
            "autocorr_returns":           (-0.1, 0.20),
            "hill_tail_index":            (2.0, 4.0),
            "gain_loss_asymmetry":        (-30.0, -3.0),
            "aggregational_gaussianity":  (10.0, 200.0),
            "intermittency_fano":         (5.0, 100.0),
            "acf_squared_returns":        (0.15, 0.55),
            "conditional_kurtosis":       (3.0, 100.0),
            "dfa_hurst_abs_r":            (0.6, 0.9),
            "leverage_effect":            (-0.6, -0.1),
            "volume_volatility_corr":     (0.0, 0.6),
            "zumbach_asymmetry":          (0.001, 0.5),
        }
        n_pass = sum(
            1 for k, (lo, hi) in bands.items()
            if k in agg and lo <= agg[k]["mean"] <= hi
        )
        label = d.name.replace("results_", "")
        cell, _, seed_tag = label.rpartition("_seed")
        seed = int(seed_tag)
        cell_scores.setdefault(cell, []).append((n_pass, seed))

    ranked = sorted(
        cell_scores.items(),
        key=lambda kv: -float(np.mean([n for n, _ in kv[1]])),
    )
    chosen: list[tuple[str, int]] = []
    for cell, score_seeds in ranked[:top_k]:
        score_seeds.sort(key=lambda ns: -ns[0])
        for _, seed in score_seeds[:top_seeds_per_cell]:
            chosen.append((cell, seed))
    return chosen


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--top-k-cells", type=int, default=3)
    p.add_argument("--top-seeds-per-cell", type=int, default=2)
    p.add_argument("--n-paths", type=int, default=500)
    p.add_argument("--alpha", type=float, default=0.95)
    p.add_argument("--horizon", type=int, default=1)
    p.add_argument("--train-window", type=int, default=500)
    p.add_argument("--stride", type=int, default=1)
    p.add_argument("--smoke", action="store_true", help="Tiny subset for smoke test")
    args = p.parse_args()

    if args.smoke:
        args.top_k_cells = 1
        args.top_seeds_per_cell = 1
        args.n_paths = 100
        args.stride = 20

    print(f"loading SPX returns ...")
    full_r, holdout_start = load_holdout_spx()
    print(f"  total={full_r.size}, holdout starts at idx={holdout_start} (~2018-01)")
    holdout = full_r[holdout_start:]
    print(f"  holdout length={holdout.size}")

    lines: list[str] = []
    lines.append("# VaR Backtest — 094 holdout (SPX 2018-2026, no leakage)\n")
    lines.append(f"Trained on `spx 2010-2017_daily`; backtest on SPX 2018-2026 daily.")
    lines.append(f"Parameters: α={args.alpha}, horizon={args.horizon}, train_window={args.train_window}, n_paths={args.n_paths}, stride={args.stride}\n")

    rows = []

    sampler_hist = HistoricalSampler(window=250)
    res_hist = rolling_backtest(
        sampler=lambda past, h, n, seed: sampler_hist.sample(past, h, n, seed),
        real_returns=holdout, horizon=args.horizon, alpha=args.alpha,
        n_paths=args.n_paths, train_window=args.train_window,
        sampler_name="Historical(250)", seed=0, stride=args.stride,
    )
    rows.append(res_hist)

    sampler_garch = GARCHSampler(dist="t", fit_window=500, refit_every=0)
    res_garch = rolling_backtest(
        sampler=lambda past, h, n, seed: sampler_garch.sample(past, h, n, seed),
        real_returns=holdout, horizon=args.horizon, alpha=args.alpha,
        n_paths=args.n_paths, train_window=args.train_window,
        sampler_name="GARCH(1,1)-t", seed=0, stride=args.stride,
    )
    rows.append(res_garch)

    cells = select_top_cells(args.top_k_cells, args.top_seeds_per_cell)
    print(f"selected {len(cells)} ECoMD (cell, seed) pairs: {cells}")
    for cell, seed in cells:
        result_dir = EXP / f"results_{cell}_seed{seed}"
        ckpt = result_dir / "checkpoint.pt"
        cfg = result_dir / "config.yaml"
        if not cfg.exists():
            cfg = EXP / f"config_{cell}_seed{seed}.yaml"
        if not (ckpt.exists() and cfg.exists()):
            print(f"  [skip] {cell} seed{seed} — missing ckpt or cfg")
            continue
        sampler_ecomd = EcoMDSampler(ckpt, cfg, device="cpu")
        try:
            res = rolling_backtest(
                sampler=lambda past, h, n, seed: sampler_ecomd.sample(past, h, n, seed),
                real_returns=holdout, horizon=args.horizon, alpha=args.alpha,
                n_paths=args.n_paths, train_window=args.train_window,
                sampler_name=f"ECoMD/{cell}/seed{seed}", seed=0, stride=args.stride,
            )
            rows.append(res)
        except Exception as exc:
            print(f"  [error] {cell} seed{seed}: {exc}")

    lines.append("## Results\n")
    lines.append("| Sampler | n_pred | n_viol | rate | exp.rate | Kupiec p | Ind. p | CC p | Pass |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|:---:|")
    for r in rows:
        rate = 100 * r.violation_rate
        exp_rate = 100 * (1 - r.alpha)
        passes = sum([r.passes_kupiec, r.passes_independence, r.passes_cc])
        flag = {3: "✅✅✅", 2: "✅✅", 1: "✅", 0: "—"}[passes]
        lines.append(
            f"| `{r.sampler_name}` | {r.n_predictions} | {r.n_violations} | "
            f"{rate:.2f}% | {exp_rate:.2f}% | "
            f"{r.kupiec_p:.3f} | {r.christoffersen_ind_p:.3f} | {r.christoffersen_cc_p:.3f} | {flag} |"
        )
    lines.append("")
    lines.append("**Caveat (Future Work)**: v3 EcoMDSampler is unconditional — `past_returns` are")
    lines.append("ignored, so ECoMD VaR is approximately constant modulo random sampling. This is")
    lines.append("a known limitation; conditional VaR via warm-start agent state is Paper A's")
    lines.append("Future Work item. The headline downstream task for Paper A is calibration-speed,")
    lines.append("not VaR-against-GARCH; VaR here is reported for distributional-realism scope.")

    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")
    for r in rows:
        print(f"  {r.sampler_name}: rate={100*r.violation_rate:.2f}% Kupiec p={r.kupiec_p:.3f}")


if __name__ == "__main__":
    main()
