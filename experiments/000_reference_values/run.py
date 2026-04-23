"""First empirical reference values for stylized facts.

Reads the yfinance + Binance Parquet shards written by ecomd/data/*_ingest.py
and computes the v0 (4-metric) stylized-facts suite on each dataset slice.

Writes JSON reports per (dataset, period) into results/.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ecomd.eval.stylized_facts import compute_all_v0, log_returns_from_prices

log = logging.getLogger("reference_values")


REPO = Path(__file__).resolve().parents[2]
RAW_DIR = REPO / "data" / "raw"
RESULTS = Path(__file__).parent / "results"


def _read_yfinance(symbol: str) -> pd.DataFrame:
    root = RAW_DIR / "yfinance" / "interval=1d" / f"symbol={symbol}"
    frames = [pd.read_parquet(p) for p in sorted(root.glob("year=*.parquet"))]
    if not frames:
        raise FileNotFoundError(f"no shards under {root}")
    df = pd.concat(frames, ignore_index=True).sort_values("timestamp")
    return df


def _read_binance(symbol: str) -> pd.DataFrame:
    root = RAW_DIR / "binance" / "market=spot" / "interval=1m" / f"symbol={symbol}"
    frames = [pd.read_parquet(p) for p in sorted(root.rglob("month=*.parquet"))]
    if not frames:
        raise FileNotFoundError(f"no shards under {root}")
    df = pd.concat(frames, ignore_index=True).sort_values("open_time")
    return df


def _to_serialisable(v: Any) -> Any:
    if isinstance(v, dict):
        return {k: _to_serialisable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_to_serialisable(x) for x in v]
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, np.ndarray):
        return v.tolist()
    return v


def _compute_and_dump(returns: np.ndarray, dataset: str, period: str, meta: dict[str, Any]) -> Path:
    results = compute_all_v0(returns)
    payload = {
        "dataset": dataset,
        "period": period,
        "meta": meta,
        "results": {k: _to_serialisable(asdict(v)) for k, v in results.items()},
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    path = RESULTS / f"{dataset}_{period}.json"
    with path.open("w") as f:
        json.dump(payload, f, indent=2)
    return path


def _summary_line(dataset: str, period: str, n: int, results: dict) -> str:
    alpha = results["hill_tail_index"].estimate
    acf2 = results["acf_squared_returns"].estimate
    lev = results["leverage_effect"].estimate
    h = results["dfa_hurst_abs_r"].estimate
    return (
        f"{dataset:<12} {period:<12} n={n:>7}  "
        f"α={alpha:>5.2f}  ⟨ACF(r²)⟩={acf2:>6.3f}  "
        f"ΣLev={lev:>+6.3f}  H(|r|)={h:>5.3f}"
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    # ── SPX daily ──
    spx = _read_yfinance("^GSPC")
    spx_close = spx["adjusted_close"].astype(float).to_numpy() if "adjusted_close" in spx.columns else spx["close"].astype(float).to_numpy()
    r_spx = log_returns_from_prices(spx_close)
    lines = []
    results_spx_all = compute_all_v0(r_spx)
    _compute_and_dump(r_spx, "spx", "2015-2026_daily", {"n_prices": int(len(spx_close)), "frequency": "1d"})
    lines.append(_summary_line("SPX", "2015-2026_d", len(r_spx), results_spx_all))

    # SPX sub-slice: COVID window 2020-02-01 .. 2020-05-31
    spx["timestamp"] = pd.to_datetime(spx["timestamp"], utc=True)
    covid = spx[(spx["timestamp"] >= "2020-02-01") & (spx["timestamp"] <= "2020-05-31")]
    if len(covid) > 50:
        c = covid["adjusted_close" if "adjusted_close" in covid.columns else "close"].astype(float).to_numpy()
        r = log_returns_from_prices(c)
        # 50-day threshold in Hill requires us to relax; skip if truly too small
        try:
            res = compute_all_v0(r)
            _compute_and_dump(r, "spx", "2020-02-01_2020-05-31", {"n_prices": int(len(c)), "frequency": "1d"})
            lines.append(_summary_line("SPX", "2020-covid", len(r), res))
        except ValueError as exc:
            log.warning("SPX covid window skipped: %s", exc)

    # ── SPY daily ──
    spy = _read_yfinance("SPY")
    spy_close = spy["adjusted_close"].astype(float).to_numpy() if "adjusted_close" in spy.columns else spy["close"].astype(float).to_numpy()
    r_spy = log_returns_from_prices(spy_close)
    results_spy = compute_all_v0(r_spy)
    _compute_and_dump(r_spy, "spy", "2015-2026_daily", {"n_prices": int(len(spy_close)), "frequency": "1d"})
    lines.append(_summary_line("SPY", "2015-2026_d", len(r_spy), results_spy))

    # ── BTC 1m ──
    btc = _read_binance("BTCUSDT")
    btc_close = btc["close"].astype(float).to_numpy()
    r_btc = log_returns_from_prices(btc_close)
    results_btc = compute_all_v0(r_btc)
    _compute_and_dump(r_btc, "btcusdt", "2024Q1_1m", {"n_prices": int(len(btc_close)), "frequency": "1m"})
    lines.append(_summary_line("BTCUSDT", "2024Q1_1m", len(r_btc), results_btc))

    # ── ETH 1m ──
    eth = _read_binance("ETHUSDT")
    eth_close = eth["close"].astype(float).to_numpy()
    r_eth = log_returns_from_prices(eth_close)
    results_eth = compute_all_v0(r_eth)
    _compute_and_dump(r_eth, "ethusdt", "2024Q1_1m", {"n_prices": int(len(eth_close)), "frequency": "1m"})
    lines.append(_summary_line("ETHUSDT", "2024Q1_1m", len(r_eth), results_eth))

    # Pretty print summary table
    print()
    print("=" * 100)
    print("Stylized facts reference values — v0 (4 metrics)")
    print("=" * 100)
    print(f"{'dataset':<12} {'period':<12} {'n':>9}  {'α':>6}  {'⟨ACF(r²)⟩':>10}  {'ΣLev':>7}  {'H(|r|)':>7}")
    print("-" * 100)
    for line in lines:
        print(line)
    print("=" * 100)
    print("\nExpected reference ranges (Cont 2001 + MITRE 2023):")
    print("  α ∈ [3, 5]        ← fat tails (Hill)")
    print("  ⟨ACF(r²)⟩ > 0.05 ← volatility clustering (Cont #6)")
    print("  ΣLev < 0         ← leverage effect at daily (Cont #9; may be weak at 1m)")
    print("  H(|r|) ∈ [0.55, 0.80]  ← long memory (Cont #8)")
    print()


if __name__ == "__main__":
    main()
