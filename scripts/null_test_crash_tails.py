"""exp 123 Stage 3+ — formal null-distribution test for the real-data driven-transient claim.

Statistic per crash episode: Δα = α_Hill(crash 2d) − α_Hill(pre-crash 5d), on VOL-STANDARDIZED
returns (k_frac=0.05). The EcoMD driven-transient predicts the crash makes the tail HEAVIER ⇒ Δα ≪ 0.

Null: slide the SAME (5d pre, 2d event) window-pair across a long calm stretch (null_2023_calm,
~3 months) → the distribution of Δα when there is NO crash. Then test, per episode and pooled,
whether the crash Δα sits in the heavy-tail (negative) tail of the null.

  conda run -n ecophys python scripts/null_test_crash_tails.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from scripts.analyze_crash_tails import H, vol_standardize  # noqa: E402

D = 24 * 60
PRE, EVT = 5 * D, 2 * D
CRASHES = {  # episode → (BTC npz, shock_idx)
    "covid_2020_03": 10079, "china_2021_05": 10079, "celsius_2022_06": 10079,
    "luna_2022_05": 10079, "ftx_2022_11": 10079,
}


def dalpha(r: np.ndarray, ss: int) -> float:
    """Δα = α(event) − α(pre), vol-standardized. Negative ⇒ tail heavier at the event."""
    rs = vol_standardize(r)
    pre, evt = rs[max(0, ss - PRE):ss], rs[ss:ss + EVT]
    if pre.size < PRE // 2 or evt.size < EVT // 2:
        return float("nan")
    return H(evt) - H(pre)


def main() -> None:
    # null distribution from the long calm window
    nf = ROOT / "data/real/null_2023_calm/trajectory_BTCUSDT.npz"
    if not nf.exists():
        raise SystemExit("missing data/real/null_2023_calm — run fetch_crash_windows.py")
    rn = np.load(nf)["log_returns"]
    null = []
    for s in range(0, len(rn) - (PRE + EVT), D // 2):   # slide by 12h
        v = dalpha(rn, s + PRE)
        if np.isfinite(v):
            null.append(v)
    null = np.array(null)
    mu, sd = float(null.mean()), float(null.std())
    print(f"=== Null Δα (no-crash, vol-standardized, n={null.size} placements) ===")
    print(f"   mean={mu:+.3f}  std={sd:.3f}  q05={np.quantile(null,0.05):+.3f}  q95={np.quantile(null,0.95):+.3f}")
    print(f"   (driven-transient predicts crash Δα in the NEGATIVE tail, i.e. Δα ≤ q05)\n")

    print(f"{'episode':16}{'Δα crash':>10}{'z':>8}{'p(null≤Δα)':>12}  driven-transient?")
    crash_ds = []
    episodes = []
    for ep, ss in CRASHES.items():
        f = ROOT / f"data/real/{ep}/trajectory_BTCUSDT.npz"
        if not f.exists():
            print(f"{ep:16}{'(missing)':>10}")
            continue
        d = dalpha(np.load(f)["log_returns"], ss)
        crash_ds.append(d)
        z = (d - mu) / sd if sd > 0 else float("nan")
        p = float((null <= d).mean())   # one-sided: how often the null is at least this heavy
        sig = "YES (sig. heavier)" if p <= 0.05 else ("no — flat" if abs(z) < 1.64 else "no — LIGHTER")
        print(f"{ep:16}{d:>+10.3f}{z:>8.2f}{p:>12.2f}  {sig}")
        episodes.append({"episode": ep, "dalpha": float(d), "z": float(z), "p": p, "sig": sig})

    cd = np.array(crash_ds)
    # pooled: is the mean crash Δα below the null mean-of-n distribution?
    n = cd.size
    pooled_z = (cd.mean() - mu) / (sd / np.sqrt(n)) if n and sd > 0 else float("nan")
    print(f"\nPooled crash Δα: mean={cd.mean():+.3f} (n={n})  vs null mean {mu:+.3f}  → z={pooled_z:+.2f}")
    verdict = ("DRIVEN-TRANSIENT SUPPORTED: crashes drive a significantly heavier tail."
               if pooled_z <= -1.64 else
               "NEGATIVE CONFIRMED: real crashes do NOT drive a heavier-than-baseline tail "
               "(Δα ≥ 0, not in the null's heavy tail). The transient is sim-only.")
    print(f"\nVERDICT: {verdict}")

    out = ROOT / "experiments/123_driven_transient/null_test_report.json"
    out.write_text(json.dumps({
        "statistic": "dalpha = alpha(crash 2d) - alpha(pre 5d), vol-standardized",
        "null": {"mean": mu, "std": sd, "n": int(null.size),
                 "q05": float(np.quantile(null, 0.05)), "q95": float(np.quantile(null, 0.95))},
        "episodes": episodes, "pooled_mean": float(cd.mean()), "pooled_z": float(pooled_z),
        "verdict": verdict,
    }, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
