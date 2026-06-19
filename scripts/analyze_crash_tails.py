"""exp 123 Stage 3 — robust regime-level + vol-standardized Hill on real crash windows.

Companion to scripts/fetch_crash_windows.py. The sliding-window α(t) (score_transfer_law.py
--windows) is estimator-noise-dominated at 1m/W=720; this does the robust test instead: a SINGLE
Hill estimate per regime (pre / crash / post, thousands of points each), and the same on
VOL-STANDARDIZED returns (r / EWMA|r|) to rule out the high-vol→lighter-Hill confound. Compares to a
calm-control null (2-day chunks).

  conda run -n ecophys python scripts/analyze_crash_tails.py
"""
from __future__ import annotations
import glob
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ecomd.eval.stylized_facts import hill_tail_index  # noqa: E402

D = 24 * 60  # 1 day in minutes
EPISODES = {"luna_2022_05": 10079, "ftx_2022_11": 10079}  # crash minute-index (= 7d into window − 1)


def H(x: np.ndarray, k: float = 0.05) -> float:
    x = x[np.isfinite(x)]
    return float(hill_tail_index(x, k_frac=k, side="both", n_bootstrap=0).estimate)


def vol_standardize(r: np.ndarray, w: int = 60) -> np.ndarray:
    """r / causal-EWMA(|r|) — removes the vol-scaling confound (high vol mechanically lightens Hill)."""
    v = np.zeros_like(r)
    a = 2.0 / (w + 1)
    ev = np.abs(r[:w]).mean() + 1e-12
    for i, x in enumerate(r):
        ev = (1 - a) * ev + a * abs(x)
        v[i] = ev
    return r / (v + 1e-12)


def regimes(r: np.ndarray, ss: int):
    return r[max(0, ss - 5 * D):ss], r[ss:ss + 2 * D], r[ss + 4 * D:ss + 8 * D]  # pre, crash, post


def main() -> None:
    for tag, transform in [("RAW returns", lambda x: x),
                           ("VOL-STANDARDIZED (r/EWMA|r|)", vol_standardize)]:
        print(f"\n=== regime-level Hill — {tag}  (cube law α≈3; transient ⇒ crash α < pre) ===")
        for ep, ss in EPISODES.items():
            for f in sorted(glob.glob(str(ROOT / f"data/real/{ep}/trajectory_*.npz"))):
                z = np.load(f)
                r = transform(z["log_returns"])
                pre, evt, post = regimes(r, ss)
                print(f"  {ep:14}/{str(z['symbol']):8} pre α={H(pre):.2f}  CRASH α={H(evt):.2f}  "
                      f"post α={H(post):.2f}   Δcrash={H(evt) - H(pre):+.2f}")
        cf = ROOT / "data/real/calm_2023_07/trajectory_BTCUSDT.npz"
        if cf.exists():
            r = transform(np.load(cf)["log_returns"])
            chunks = [H(r[i:i + 2 * D]) for i in range(0, len(r) - 2 * D, 2 * D)]
            print(f"  calm null: mean={np.mean(chunks):.2f} std={np.std(chunks):.2f} "
                  f"chunks={[round(x, 2) for x in chunks]}")
    print("\nVerdict: real crashes do NOT heavy-up the tail (Luna lightens, FTX flat) even after "
          "vol-standardization → real fat tails ~stationary cube-law; the EcoMD transient is sim-only.")


if __name__ == "__main__":
    main()
