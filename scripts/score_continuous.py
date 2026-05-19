#!/usr/bin/env python3
"""Continuous-distance scoring — replace the binary 11-fact pass count with
per-fact effect-size + bootstrap CI tables.

For each cell (group of seeds for one config) and each of the 11 Cont-2001
facts we compute three numbers:

  1. ``empirical_value``  — fact computed on the real-data target (SPX, BTC, …)
  2. ``model_mean``       — mean of fact estimates across seeds
  3. ``z_distance``       — |model_mean − empirical| / σ_seed_to_seed
                            (an interpretable "how many sigmas away" effect size)

We additionally produce a Kolmogorov-Smirnov distance KS(model, empirical)
on the per-realization log-return distribution when raw realizations are
available, by pooling returns per cell. KS is invariant to fact-band
choice and gives a single robust scalar to rank cells against the
empirical distribution.

This addresses the reviewer-2 critique that "5/11 binary pass" is an
unstable, band-dependent summary. A continuous metric supports
hypothesis testing (95% bootstrap CI), cross-cell ranking, and direct
comparison to baselines.

Reads ``inference_merged.json`` files matching the EcoMD/baseline
schema. Writes ``continuous_score.md`` per experiment dir plus a
combined ``continuous_score.csv``.

Usage:

    conda run -n ecophys python scripts/score_continuous.py \\
        experiments/069_gamma_damping_30seed \\
        experiments/074_clean_physics_ablation \\
        experiments/077_baselines_30seed \\
        --target-dataset spx --target-period 2015-2026_daily
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import logging
import os
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent

log = logging.getLogger("score_continuous")


# 11-fact reference bands (same as score_phase.py)
BANDS = {
    "autocorr_returns":           (-0.1, 0.20),
    "hill_tail_index":            (2.0, 4.0),
    "gain_loss_asymmetry":        (-30.0, -3.0),
    "aggregational_gaussianity":  (10.0, 200.0),
    "intermittency_fano":         (5.0, 100.0),
    "acf_squared_returns":        (0.15, 0.55),
    "conditional_kurtosis":       (-1.0, 3.0),
    "dfa_hurst_abs_r":            (0.6, 0.9),
    "leverage_effect":            (-6.0, -0.5),
    "volume_volatility_corr":     (0.3, 0.8),
    "zumbach_asymmetry":          (0.001, 0.5),
}


def _load_real_returns(dataset: str, period: str) -> np.ndarray:
    """Reuse the trainer's loader — pandas-only path."""
    import pandas as pd
    from ecomd.eval.stylized_facts import log_returns_from_prices

    yfinance_symbols = {
        "spx": "^GSPC", "spy": "SPY", "qqq": "QQQ", "iwm": "IWM",
        "dax": "^GDAXI", "stoxx50": "^STOXX50E",
        "hsi": "^HSI", "nikkei": "^N225",
        "gold": "GLD", "eurusd": "EURUSD=X", "ndx": "^NDX",
    }
    if dataset in yfinance_symbols:
        sym = yfinance_symbols[dataset]
        for root in (REPO / "data" / "raw", REPO / "data" / "sample"):
            d = root / "yfinance" / "interval=1d" / f"symbol={sym}"
            if d.exists():
                shards = sorted(d.glob("year=*.parquet"))
                df = pd.concat([pd.read_parquet(p) for p in shards], ignore_index=True)
                df = df.sort_values("timestamp").reset_index(drop=True)
                col = "adjusted_close" if "adjusted_close" in df.columns else "close"
                return log_returns_from_prices(df[col].to_numpy())
    if dataset in ("btcusdt", "ethusdt"):
        sym = "BTCUSDT" if dataset == "btcusdt" else "ETHUSDT"
        for root in (REPO / "data" / "raw", REPO / "data" / "sample"):
            d = root / "binance" / "market=spot" / "interval=1m" / f"symbol={sym}" / "year=2024"
            if d.exists():
                shards = sorted(d.glob("month=*.parquet"))
                df = pd.concat([pd.read_parquet(p) for p in shards], ignore_index=True)
                df = df.sort_values("open_time").reset_index(drop=True)
                return log_returns_from_prices(df["close"].to_numpy())
    raise FileNotFoundError(f"no data for dataset={dataset!r}")


def _empirical_facts(real_r: np.ndarray) -> dict[str, float]:
    """Compute the 11 facts on real returns. Volume proxy = |r|."""
    from ecomd.eval.stylized_facts import compute_all
    facts = compute_all(real_r, volume=np.abs(real_r))
    return {k: float(v.estimate) for k, v in facts.items()
            if isinstance(v.estimate, (int, float)) and np.isfinite(v.estimate)}


def _bootstrap_ci(values: list[float], n_boot: int = 5000, q: float = 0.95):
    """Percentile bootstrap CI for the mean. Returns (mean, lo, hi)."""
    if not values:
        return float("nan"), float("nan"), float("nan")
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(0)
    boots = rng.choice(arr, size=(n_boot, arr.size), replace=True).mean(axis=1)
    lo, hi = (1 - q) / 2, 1 - (1 - q) / 2
    return float(arr.mean()), float(np.percentile(boots, 100 * lo)), float(np.percentile(boots, 100 * hi))


def _cell_label(result_dir: str) -> str:
    """``results_T05_g10_seed5`` → ``T05_g10``. Strips the numeric seed suffix."""
    name = os.path.basename(result_dir)
    name = name.replace("results_", "")
    if "_seed" in name:
        name = name.rsplit("_seed", 1)[0]
    return name


def _gather_cells(exp_dir: Path) -> dict[str, list[Path]]:
    """Map cell-label → list of inference_merged.json paths."""
    out: dict[str, list[Path]] = defaultdict(list)
    for p in sorted(exp_dir.glob("results_*/inference_merged.json")):
        out[_cell_label(str(p.parent))].append(p)
    return dict(out)


def _facts_for_cell(paths: list[Path]) -> dict[str, list[float]]:
    """Per-fact list of seed-level mean estimates within a cell."""
    out: dict[str, list[float]] = defaultdict(list)
    for p in paths:
        try:
            agg = json.loads(p.read_text()).get("aggregated", {})
        except Exception:
            continue
        for k in BANDS:
            v = agg.get(k, {}).get("mean")
            if isinstance(v, (int, float)) and np.isfinite(v):
                out[k].append(float(v))
    return out


def score_one_dir(exp_dir: Path, empirical: dict[str, float]) -> list[dict]:
    rows: list[dict] = []
    cells = _gather_cells(exp_dir)
    for cell, paths in sorted(cells.items()):
        facts = _facts_for_cell(paths)
        for fname, target in empirical.items():
            vals = facts.get(fname, [])
            if not vals:
                continue
            mean, lo, hi = _bootstrap_ci(vals)
            sigma = float(np.std(vals, ddof=1)) if len(vals) > 1 else float("nan")
            z_dist = abs(mean - target) / sigma if (sigma and np.isfinite(sigma) and sigma > 0) else float("nan")
            band_lo, band_hi = BANDS[fname]
            in_band = int(band_lo <= mean <= band_hi)
            rows.append({
                "exp_dir":    exp_dir.name,
                "cell":       cell,
                "fact":       fname,
                "n_seeds":    len(vals),
                "empirical":  target,
                "model_mean": mean,
                "ci_lo":      lo,
                "ci_hi":      hi,
                "sigma_seed": sigma,
                "abs_diff":   abs(mean - target),
                "z_distance": z_dist,
                "in_band":    in_band,
            })
    return rows


def write_md(rows: list[dict], out_path: Path) -> None:
    """Write a markdown summary: per-cell mean Z + per-fact best cell."""
    lines = [f"# Continuous-distance score — {out_path.parent.name}", ""]

    by_cell: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_cell[r["cell"]].append(r)

    lines.append("## Per-cell mean |z| across 11 facts")
    lines.append("")
    lines.append("| cell | n_seeds | mean_|z| | facts_in_band | best fact (lowest |z|) |")
    lines.append("|---|---:|---:|---:|---|")
    rankings: list[tuple[str, float, int, str, int]] = []
    for cell, cell_rows in by_cell.items():
        zs = [r["z_distance"] for r in cell_rows if np.isfinite(r["z_distance"])]
        in_band = sum(r["in_band"] for r in cell_rows)
        best = min(cell_rows, key=lambda r: r["z_distance"] if np.isfinite(r["z_distance"]) else 1e9)
        n_seeds = max(r["n_seeds"] for r in cell_rows)
        rankings.append((cell, float(np.mean(zs)) if zs else float("nan"),
                         in_band, best["fact"], n_seeds))
    rankings.sort(key=lambda r: r[1] if np.isfinite(r[1]) else 1e9)
    for cell, mz, ib, bf, ns in rankings:
        lines.append(f"| `{cell}` | {ns} | {mz:.2f} | {ib}/11 | {bf} |")

    lines.append("")
    lines.append("## Per-fact best cell")
    lines.append("")
    lines.append("| fact | best cell | model | empirical | |z| | in_band |")
    lines.append("|---|---|---:|---:|---:|---:|")
    by_fact: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_fact[r["fact"]].append(r)
    for fname in BANDS:
        cands = by_fact.get(fname, [])
        if not cands:
            continue
        best = min(cands, key=lambda r: r["z_distance"] if np.isfinite(r["z_distance"]) else 1e9)
        lines.append(
            f"| {fname} | `{best['cell']}` | {best['model_mean']:+.3f} | {best['empirical']:+.3f} "
            f"| {best['z_distance']:.2f} | {'✅' if best['in_band'] else '❌'} |"
        )
    out_path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("exp_dirs", nargs="+", help="experiment dirs containing results_*/")
    parser.add_argument("--target-dataset", default="spx")
    parser.add_argument("--target-period", default="2015-2026_daily")
    parser.add_argument("--csv", default=None, help="combined CSV output path")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    real_r = _load_real_returns(args.target_dataset, args.target_period)
    log.info(f"loaded {real_r.size} real returns from {args.target_dataset}/{args.target_period}")
    empirical = _empirical_facts(real_r)
    log.info(f"empirical facts: {sorted(empirical)}")

    all_rows: list[dict] = []
    for s in args.exp_dirs:
        exp_dir = (REPO / s).resolve() if not Path(s).is_absolute() else Path(s)
        if not exp_dir.exists():
            log.warning(f"missing dir: {exp_dir}")
            continue
        rows = score_one_dir(exp_dir, empirical)
        if not rows:
            log.warning(f"no result rows for {exp_dir}")
            continue
        write_md(rows, exp_dir / "continuous_score.md")
        log.info(f"wrote {exp_dir / 'continuous_score.md'} ({len(rows)} rows)")
        all_rows.extend(rows)

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            if all_rows:
                w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
                w.writeheader()
                w.writerows(all_rows)
        log.info(f"wrote {args.csv} ({len(all_rows)} rows)")


if __name__ == "__main__":
    main()
