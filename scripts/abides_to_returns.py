#!/usr/bin/env python3
"""Convert ABIDES mid-price output → log returns → 11-fact inference_merged.json.

Part of the 2026-05-28 ceiling-attribution probe (D7): ABIDES is a realistic
discrete-event market simulator. Scoring it with the SAME 11-fact evaluator
(ecomd.eval.stylized_facts.compute_all) and the SAME daily-calibrated bands as
EcoMD tells us whether 11/11 is even reachable for the agent-based paradigm —
which sets the Paper A narrative (paradigm-SOTA vs lagging vs framework-redo).

Output schema is byte-compatible with ecomd/baselines/runner.py, so the existing
scripts/score_phase.py and scripts/score_summary.py work unchanged.

FREQUENCY CAVEAT (must disclose in the paper): ABIDES rmsc04 simulates one
intraday session at sub-second resolution; our 11-fact bands were calibrated on
DAILY SPX returns. Two modes are provided:
  --mode intraday : each sim → its own intraday return series (one realization);
                    seeds aggregate as realizations. Returns are intraday, bands
                    are daily — informative for shape, not a like-for-like ceiling.
  --mode daily    : treat each input CSV as one trading day, take one close-to-
                    close return per day → a single daily series across all days
                    (one realization). Like-for-like with daily bands, but needs
                    many sim-days to have enough returns (>= ~250).

Input: a directory of CSVs named ``abides_<cell>_seed<k>.csv`` with columns
``timestamp`` (parseable) and a price column (``mid`` default, override with
--price-col). Produced by scripts/h20_run_abides_calibrate.sh.

Usage:
  python scripts/abides_to_returns.py --abides-dir <dir> --cell rmsc04_base \
      --out-dir experiments/105_abides_ceiling/results_rmsc04_base --mode intraday --bar 60
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ecomd.eval.stylized_facts import compute_all, log_returns_from_prices  # noqa: E402

log = logging.getLogger("abides_to_returns")


def _resample_prices(df: pd.DataFrame, price_col: str, bar_seconds: int) -> np.ndarray:
    """Resample an irregular mid-price path to fixed `bar_seconds` bars (last)."""
    ts = pd.to_datetime(df["timestamp"])
    s = pd.Series(df[price_col].to_numpy(), index=ts).sort_index()
    bars = s.resample(f"{bar_seconds}s").last().dropna()
    return bars.to_numpy()


def _intraday_realizations(csvs: list[Path], price_col: str, bar_seconds: int) -> list[np.ndarray]:
    out = []
    for c in csvs:
        df = pd.read_csv(c)
        prices = _resample_prices(df, price_col, bar_seconds)
        if prices.size >= 60:
            out.append(log_returns_from_prices(prices))
    return out


def _daily_series(csvs: list[Path], price_col: str) -> list[np.ndarray]:
    """One close-to-close-style return per sim-day → a single daily series."""
    day_prices = []
    for c in csvs:
        df = pd.read_csv(c)
        p = df[price_col].to_numpy()
        if p.size >= 2:
            day_prices.append(float(p[-1]) / float(p[0]))  # gross daily return
    if len(day_prices) < 2:
        return []
    daily_ret = np.log(np.asarray(day_prices))
    return [daily_ret]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--abides-dir", required=True)
    ap.add_argument("--cell", required=True, help="e.g. rmsc04_base — matches abides_<cell>_seed*.csv")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--mode", choices=["intraday", "daily"], default="intraday")
    ap.add_argument("--bar", type=int, default=60, help="intraday bar size in seconds")
    ap.add_argument("--price-col", default="mid")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    abides_dir = Path(args.abides_dir)
    csvs = sorted(abides_dir.glob(f"abides_{args.cell}_seed*.csv"))
    if not csvs:
        log.error("no CSVs matching abides_%s_seed*.csv in %s", args.cell, abides_dir)
        sys.exit(2)
    log.info("found %d ABIDES sim CSVs for cell=%s mode=%s", len(csvs), args.cell, args.mode)

    if args.mode == "intraday":
        series_list = _intraday_realizations(csvs, args.price_col, args.bar)
    else:
        series_list = _daily_series(csvs, args.price_col)
    if not series_list:
        log.error("no usable return series produced (too few price points)")
        sys.exit(2)

    realizations: list[dict] = []
    for i, returns in enumerate(series_list):
        t0 = time.time()
        volume = np.abs(returns)  # ABIDES mid-price path carries no volume here; |r| proxy (same as baselines)
        facts = compute_all(returns, volume=volume)
        realizations.append({
            "rank": 0, "seed": i, "n_steps": int(returns.size),
            "rollout_time_s": time.time() - t0,
            "facts": {k: v.to_dict() for k, v in facts.items()},
        })

    keys = list(realizations[0]["facts"].keys())
    aggregated: dict[str, dict[str, float]] = {}
    for k in keys:
        vals = [float(r["facts"][k]["estimate"]) for r in realizations
                if isinstance(r["facts"][k].get("estimate"), (int, float))
                and np.isfinite(r["facts"][k].get("estimate"))]
        if vals:
            aggregated[k] = {"mean": float(np.mean(vals)), "std": float(np.std(vals)), "n": len(vals)}

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    merged = {
        "aggregated": aggregated,
        "n_total_rollouts": len(realizations),
        "realizations": realizations,
        "abides_meta": {"cell": args.cell, "mode": args.mode, "bar_seconds": args.bar,
                        "n_sims": len(csvs), "price_col": args.price_col},
    }
    (out_dir / "inference_merged.json").write_text(json.dumps(merged, indent=2))
    log.info("wrote %s (%d facts aggregated over %d realizations)",
             out_dir / "inference_merged.json", len(aggregated), len(realizations))


if __name__ == "__main__":
    main()
