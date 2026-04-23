"""Empirical reference values for all 11 Cont-2001 stylized facts, plus a
multi-order DFA diagnostic to investigate the H ≈ 0.98 anomaly flagged on
2026-04-23.

Reads yfinance + Binance Parquet shards written by ecomd/data/*_ingest.py.

Outputs:
  results/stylized_facts_{dataset}_{period}.json    — per-(dataset, period) all 11 metrics
  results/dfa_multi_order.json                      — DFA H at orders 1/2/3 on each dataset
  results/dfa_subperiod.json                        — DFA H on fixed-length chunks
  results/summary_table.md                          — scan-friendly Paper A Table 1 candidate

Run:
  python experiments/000_reference_values/run.py
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ecomd.eval.stylized_facts import (
    compute_all,
    dfa_hurst,
    dfa_hurst_multi_order,
    log_returns_from_prices,
)

log = logging.getLogger("reference_values")


REPO = Path(__file__).resolve().parents[2]
RAW_DIR = REPO / "data" / "raw"
RESULTS = Path(__file__).parent / "results"


# ─── I/O ───────────────────────────────────────────────────────────────────


def _read_yfinance(symbol: str) -> pd.DataFrame:
    root = RAW_DIR / "yfinance" / "interval=1d" / f"symbol={symbol}"
    frames = [pd.read_parquet(p) for p in sorted(root.glob("year=*.parquet"))]
    if not frames:
        raise FileNotFoundError(f"no shards under {root}")
    return pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)


def _read_binance(symbol: str) -> pd.DataFrame:
    root = RAW_DIR / "binance" / "market=spot" / "interval=1m" / f"symbol={symbol}"
    frames = [pd.read_parquet(p) for p in sorted(root.rglob("month=*.parquet"))]
    if not frames:
        raise FileNotFoundError(f"no shards under {root}")
    return pd.concat(frames, ignore_index=True).sort_values("open_time").reset_index(drop=True)


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


def _dump_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(_to_serialisable(obj), f, indent=2)


# ─── Main metric runs ──────────────────────────────────────────────────────


def _run_all_metrics(
    dataset: str,
    period: str,
    prices: np.ndarray,
    volume: np.ndarray | None,
    frequency: str,
) -> dict[str, Any]:
    r = log_returns_from_prices(prices)
    # Volume needs to align with returns (one shorter than prices)
    v_aligned = None
    if volume is not None:
        v = volume[-r.size:] if volume.size >= r.size else None
        if v is not None and v.size == r.size:
            v_aligned = v
    results = compute_all(r, volume=v_aligned)
    payload = {
        "dataset": dataset,
        "period": period,
        "meta": {"n_prices": int(len(prices)), "n_returns": int(r.size), "frequency": frequency, "has_volume": v_aligned is not None},
        "results": {k: asdict(res) for k, res in results.items()},
    }
    _dump_json(RESULTS / f"stylized_facts_{dataset}_{period}.json", payload)
    return {"returns": r, "volume": v_aligned, "results": results, "meta": payload["meta"]}


def _extract_scalar(res) -> float:
    return float(res.estimate) if res is not None else float("nan")


# ─── DFA investigation ────────────────────────────────────────────────────


def _dfa_multi_and_subperiod(name: str, returns: np.ndarray, chunk_size: int = 2000) -> dict[str, Any]:
    abs_r = np.abs(returns)
    # Multi-order
    multi = dfa_hurst_multi_order(abs_r, orders=(1, 2, 3))
    multi_out = {o: {"H": float(res.estimate), "n": res.meta["n"]} for o, res in multi.items()}
    # Sub-period (non-overlapping fixed-length chunks)
    sub: list[dict[str, Any]] = []
    n = abs_r.size
    for i in range(0, n, chunk_size):
        chunk = abs_r[i : i + chunk_size]
        if chunk.size < 500:
            continue
        try:
            h1 = dfa_hurst(chunk, order=1).estimate
        except ValueError:
            h1 = float("nan")
        try:
            h2 = dfa_hurst(chunk, order=2).estimate
        except ValueError:
            h2 = float("nan")
        sub.append({"start_idx": int(i), "end_idx": int(min(i + chunk_size, n)), "H_order1": float(h1), "H_order2": float(h2)})
    return {"dataset": name, "multi_order": multi_out, "sub_periods": sub}


# ─── Main ──────────────────────────────────────────────────────────────────


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    runs: list[dict[str, Any]] = []

    # SPX daily 2015–2026
    spx = _read_yfinance("^GSPC")
    spx_close = (spx["adjusted_close"] if "adjusted_close" in spx.columns else spx["close"]).astype(float).to_numpy()
    runs.append({"dataset": "spx", "period": "2015-2026_daily", "freq": "1d",
                 **_run_all_metrics("spx", "2015-2026_daily", spx_close, None, "1d")})

    # SPY daily 2015–2026 (has volume)
    spy = _read_yfinance("SPY")
    spy_close = (spy["adjusted_close"] if "adjusted_close" in spy.columns else spy["close"]).astype(float).to_numpy()
    spy_volume = spy["volume"].astype(float).to_numpy() if "volume" in spy.columns else None
    runs.append({"dataset": "spy", "period": "2015-2026_daily", "freq": "1d",
                 **_run_all_metrics("spy", "2015-2026_daily", spy_close, spy_volume, "1d")})

    # BTC 1m 2024Q1 (has volume)
    btc = _read_binance("BTCUSDT")
    btc_close = btc["close"].astype(float).to_numpy()
    btc_volume = btc["volume"].astype(float).to_numpy()
    runs.append({"dataset": "btcusdt", "period": "2024Q1_1m", "freq": "1m",
                 **_run_all_metrics("btcusdt", "2024Q1_1m", btc_close, btc_volume, "1m")})

    # ETH 1m 2024Q1 (has volume)
    eth = _read_binance("ETHUSDT")
    eth_close = eth["close"].astype(float).to_numpy()
    eth_volume = eth["volume"].astype(float).to_numpy()
    runs.append({"dataset": "ethusdt", "period": "2024Q1_1m", "freq": "1m",
                 **_run_all_metrics("ethusdt", "2024Q1_1m", eth_close, eth_volume, "1m")})

    # ── DFA investigation ──
    dfa_runs = [
        ("spx_daily_2015_2026", runs[0]["returns"]),
        ("spy_daily_2015_2026", runs[1]["returns"]),
        ("btc_1m_2024Q1", runs[2]["returns"]),
        ("eth_1m_2024Q1", runs[3]["returns"]),
    ]
    # For daily we want smaller chunks (the series is only ~2800 points)
    dfa_payload = {}
    for name, r in dfa_runs:
        chunk = 500 if r.size < 5000 else 20_000
        dfa_payload[name] = _dfa_multi_and_subperiod(name, r, chunk_size=chunk)
    _dump_json(RESULTS / "dfa_investigation.json", dfa_payload)

    # ── Summary table ──
    cols = [
        ("#1 ACF(r)", "autocorr_returns"),
        ("#2 α tail", "hill_tail_index"),
        ("#3 skew", "gain_loss_asymmetry"),
        ("#4 Δκ agg", "aggregational_gaussianity"),
        ("#5 Fano", "intermittency_fano"),
        ("#6 ACF(r²)", "acf_squared_returns"),
        ("#7 κ GARCH-std", "conditional_kurtosis"),
        ("#8 H DFA|r|", "dfa_hurst_abs_r"),
        ("#9 ΣLev", "leverage_effect"),
       ("#10 corr(V,|r|)", "volume_volatility_corr"),
        ("#11 Zumbach D", "zumbach_asymmetry"),
    ]
    lines: list[str] = []
    lines.append("# Stylized Facts Reference Values — Paper A Table 1 candidate")
    lines.append("")
    lines.append(f"Generated: 2026-04-23  |  11 metrics per Cont (2001)  |  hardware: Mac / conda env `ecophys`")
    lines.append("")
    header = "| dataset | period | n | " + " | ".join(c for c, _ in cols) + " |"
    sep = "|" + "|".join(["---"] * (3 + len(cols))) + "|"
    lines.append(header)
    lines.append(sep)
    for run in runs:
        vals = []
        for _label, key in cols:
            if key in run["results"]:
                vals.append(f"{run['results'][key].estimate:+.3f}")
            else:
                vals.append("—")
        lines.append(f"| {run['dataset']} | {run['period']} | {run['meta']['n_returns']} | " + " | ".join(vals) + " |")
    lines.append("")
    lines.append("")
    lines.append("## Cont 2001 / MITRE 2023 expected ranges")
    lines.append("")
    lines.append("- #1 ACF(r) near 0 (< 0.05 typically); Ljung-Box p > 0.05")
    lines.append("- #2 α ∈ [3, 5]")
    lines.append("- #3 skew < 0 for daily equity indices; may be ≈0 or positive for crypto / intraday individual stocks (MITRE 2023)")
    lines.append("- #4 Δκ = κ(scale=1) − κ(scale=max) > 0 (Gaussianisation with aggregation)")
    lines.append("- #5 Fano > 1 (clustering of extremes); MITRE reports 2.6–4.7 at 1-min Dow stocks")
    lines.append("- #6 ⟨ACF(r²)⟩ > 0.05 (volatility clustering)")
    lines.append("- #7 excess κ of GARCH residuals > 0 but < unconditional κ")
    lines.append("- #8 H ∈ [0.55, 0.80] on stationary samples; values near 1 indicate non-stationarity")
    lines.append("- #9 ΣLev < 0 for daily equity indices; weak/absent at intraday (MITRE 2023)")
    lines.append("- #10 corr(V, |r|) > 0 (≈0.2–0.6) in clock time")
    lines.append("- #11 Zumbach D > 0 for indices; weak for individual intraday")
    lines.append("")
    lines.append("## DFA Hurst multi-order investigation (H ≈ 0.98 anomaly)")
    lines.append("")
    lines.append("| dataset | H(order=1) | H(order=2) | H(order=3) | Δ(1-3) |")
    lines.append("|---|---|---|---|---|")
    for name, payload in dfa_payload.items():
        mo = payload["multi_order"]
        h1, h2, h3 = mo[1]["H"], mo[2]["H"], mo[3]["H"]
        lines.append(f"| {name} | {h1:+.3f} | {h2:+.3f} | {h3:+.3f} | {h1 - h3:+.3f} |")
    lines.append("")
    lines.append("Large Δ(1-3) → order-1 DFA was picking up across-window trend rather than long memory.")
    lines.append("")

    summary_path = RESULTS / "summary_table.md"
    summary_path.write_text("\n".join(lines))

    # Also print to stdout for quick inspection
    print()
    print("=" * 120)
    for line in lines:
        print(line)
    print("=" * 120)
    print(f"\n→ summary written to {summary_path}")
    print(f"→ per-dataset JSONs in {RESULTS}")


if __name__ == "__main__":
    main()
