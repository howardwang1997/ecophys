"""exp 123 Stage 3 — fetch real crash windows (1m crypto) for the NCS Gate-2 pilot.

Pulls 1-minute klines from the Binance public REST API (free, no key) for real stress episodes +
a matched calm control, computes log-returns from close, and writes
``data/real/<episode>/trajectory_<sym>.npz`` with a ``log_returns`` key — exactly the format the
existing ``score_transfer_law.py --windows`` estimator reads. Prints each crash's minute-index for
the ``--shock-step`` marker.

Question (Gate 2): do REAL fat tails show the same DRIVEN-TRANSIENT dip-and-recover (windowed Hill α
drops at the crash, recovers after) seen in EcoMD, or are they stationary (flat α)?

  conda run -n ecophys python scripts/fetch_crash_windows.py
"""
from __future__ import annotations
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/real"
API = "https://api.binance.com/api/v3/klines"


def _ms(y: int, m: int, d: int) -> int:
    return int(datetime(y, m, d, tzinfo=timezone.utc).timestamp() * 1000)


# episode: (symbols, window start, window end, crash marker) — all UTC dates.
EPISODES = {
    # crash episodes (1m, BTC ± ETH), each centered 7 days into the window (shock_idx≈10079):
    "covid_2020_03":  dict(syms=["BTCUSDT"], start=_ms(2020, 3, 5), end=_ms(2020, 3, 23),
                           crash=_ms(2020, 3, 12), note="COVID crash — BTC −50% Mar 12-13"),
    "china_2021_05":  dict(syms=["BTCUSDT"], start=_ms(2021, 5, 12), end=_ms(2021, 5, 30),
                           crash=_ms(2021, 5, 19), note="China mining ban — BTC −30% May 19"),
    "celsius_2022_06": dict(syms=["BTCUSDT"], start=_ms(2022, 6, 6), end=_ms(2022, 6, 24),
                           crash=_ms(2022, 6, 13), note="Celsius/3AC — BTC 28k→17.6k Jun 13-18"),
    "luna_2022_05": dict(syms=["BTCUSDT", "ETHUSDT"], start=_ms(2022, 5, 2), end=_ms(2022, 5, 20),
                         crash=_ms(2022, 5, 9), note="UST depeg → LUNA collapse (May 9-13)"),
    "ftx_2022_11":  dict(syms=["BTCUSDT", "ETHUSDT"], start=_ms(2022, 11, 1), end=_ms(2022, 11, 18),
                         crash=_ms(2022, 11, 8), note="FTX insolvency → BTC 20.5k→15.6k (Nov 8-9)"),
    "calm_2023_07": dict(syms=["BTCUSDT"], start=_ms(2023, 7, 1), end=_ms(2023, 7, 18),
                         crash=None, note="rangebound ~30-31k — matched calm control"),
    # long calm stretch — the NULL source for the Δα permutation test (many non-crash window-pairs).
    "null_2023_calm": dict(syms=["BTCUSDT"], start=_ms(2023, 5, 1), end=_ms(2023, 8, 1),
                           crash=None, note="May-Jul 2023 rangebound 26-31k — null-distribution source"),
}


def fetch_klines(sym: str, start_ms: int, end_ms: int) -> tuple[np.ndarray, np.ndarray]:
    """Paginated 1m klines → (open_times_ms, close_prices). Polite (0.3s/req)."""
    times: list[int] = []
    closes: list[float] = []
    cur = start_ms
    while cur < end_ms:
        url = f"{API}?symbol={sym}&interval=1m&startTime={cur}&endTime={end_ms}&limit=1000"
        with urllib.request.urlopen(url, timeout=30) as r:
            rows = json.load(r)
        if not rows:
            break
        for k in rows:
            times.append(int(k[0]))
            closes.append(float(k[4]))
        nxt = int(rows[-1][0]) + 60_000
        if nxt <= cur:
            break
        cur = nxt
        time.sleep(0.3)
    return np.asarray(times, dtype=np.int64), np.asarray(closes, dtype=float)


def main() -> None:
    summary = {}
    for ep, cfg in EPISODES.items():
        d = OUT / ep
        d.mkdir(parents=True, exist_ok=True)
        ep_info = {"note": cfg["note"], "symbols": {}}
        for sym in cfg["syms"]:
            if (d / f"trajectory_{sym}.npz").exists():
                print(f"  {ep}/{sym}: already on disk — skip")
                continue
            t, px = fetch_klines(sym, cfg["start"], cfg["end"])
            if px.size < 100:
                print(f"  [warn] {ep}/{sym}: only {px.size} bars — skip")
                continue
            logp = np.log(px)
            logret = np.diff(logp)                                   # (T-1,)
            # crash marker → index into the RETURN series (align to diff offset)
            shock_idx = None
            if cfg["crash"] is not None:
                shock_idx = int(np.searchsorted(t, cfg["crash"])) - 1
                shock_idx = max(0, min(shock_idx, logret.size - 1))
            np.savez_compressed(
                d / f"trajectory_{sym}.npz",
                log_returns=logret, log_prices=logp, open_time_ms=t,
                symbol=sym, crash_ms=(cfg["crash"] or 0), shock_idx=(shock_idx if shock_idx is not None else -1),
            )
            ep_info["symbols"][sym] = {
                "bars": int(px.size), "minutes": int((cfg["end"] - cfg["start"]) / 60000),
                "shock_idx": shock_idx, "px_start": float(px[0]), "px_min": float(px.min()),
                "px_max": float(px.max()),
                "max_abs_1m_ret": float(np.abs(logret).max()),
            }
            print(f"  {ep}/{sym}: {px.size} bars, shock_idx={shock_idx}, "
                  f"px {px[0]:.0f}→min {px.min():.0f} (max|1m r|={np.abs(logret).max():.3f})")
        summary[ep] = ep_info
    (OUT / "_fetch_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nwrote {OUT/'_fetch_summary.json'}")
    print("next: for each episode dir, score_transfer_law.py --windows data/real/<ep> "
          "--window 720 --stride 60 --k-frac 0.1 --shock-step <shock_idx>")


if __name__ == "__main__":
    main()
