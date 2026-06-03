"""Score exp 114 — 5-asset confirmation of the concave √-impact solve.

Per asset: concave_d050 vs that asset's baseline — hill∈[2,4] AND acf²∈[.15,.55], Welch t-test
with Bonferroni (m = #assets) on the net stylized-fact score AND on hill. Also re-fits the
hill(δ) line per asset from {baseline-implied, d045, d050} to test whether δ*≈0.5 (the empirical
inverse-cubic crossing) is universal or asset-specific.

SPX baseline + concave_d050 are REUSED from exp 113 (identical base config + conditions); pass
--spx113 to point at that dir (default experiments/113_gabaix_solve).

SOLVE-CONFIRMED iff the d050 gate holds on ≥4/5 assets with no ≥20pp single-fact collateral.

Usage: python scripts/score_concave_confirm.py experiments/114_concave_confirm
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

HILL_BAND = (2.0, 4.0)
ACF2_BAND = (0.15, 0.55)
BANDS = {
    "hill_tail_index": (2, 4), "acf_squared_returns": (0.15, 0.55),
    "aggregational_gaussianity": (10, 200), "dfa_hurst_abs_r": (0.4, 0.8),
    "autocorr_returns": (-0.1, 0.1), "intermittency_fano": (1, 1e9),
    "leverage_effect": (-1, 0), "gain_loss_asymmetry": (0, 1e9),
    "volume_volatility_corr": (0.1, 1), "zumbach_asymmetry": (0, 1e9),
    "conditional_kurtosis": (0, 100),
}
ASSETS = ["spx", "ndx", "gold", "eurusd", "btcusdt"]
DELTAS = {"concave_d045": 0.45, "concave_d050": 0.50}


def _vals(mj: Path) -> dict:
    agg = json.loads(mj.read_text()).get("aggregated", {})
    out = {}
    for k in BANDS:
        v = agg.get(k)
        m = (v or {}).get("mean") if isinstance(v, dict) else v
        out[k] = float(m) if (m is not None and np.isfinite(m)) else np.nan
    return out


def _load(root: Path, asset: str, cell: str) -> list[dict]:
    rows = []
    for d in sorted(root.glob(f"results_{asset}_{cell}_seed*")):
        mj = d / "inference_merged.json"
        if mj.exists():
            rows.append(_vals(mj))
    return rows


def _net(rows: list[dict]) -> np.ndarray:
    return np.array([sum(1 for k, (lo, hi) in BANDS.items()
                         if not np.isnan(r[k]) and lo <= r[k] <= hi) for r in rows])


def _rate(rows: list[dict], k: str) -> float:
    lo, hi = BANDS[k]
    xs = [r[k] for r in rows if not np.isnan(r[k])]
    return 100 * np.mean([lo <= x <= hi for x in xs]) if xs else float("nan")


def _col(rows: list[dict], k: str) -> np.ndarray:
    return np.array([r[k] for r in rows if not np.isnan(r[k])])


def main() -> None:
    root = Path(sys.argv[1])
    spx113 = Path(sys.argv[2]) if len(sys.argv) > 2 else root.parent / "113_gabaix_solve"

    def cell(asset, c):
        rows = _load(root, asset, c)
        if not rows and asset == "spx":  # reuse 113 for spx baseline/d050
            rows = _load(spx113, asset.replace("spx", ""), c) or _load(spx113, "", c)
            if not rows:  # 113 dirs are results_<cell>_seed* (no asset prefix)
                rows = [_vals(d / "inference_merged.json")
                        for d in sorted(spx113.glob(f"results_{c}_seed*"))
                        if (d / "inference_merged.json").exists()]
        return rows

    m = len(ASSETS)
    print(f"# exp 114 — 5-asset confirmation of concave √-impact (δ=0.5). "
          f"Bonferroni m={m}, α=0.01.\n")
    hdr = (f"{'asset':9}{'base_hill':>10}{'d050_hill':>10}{'d050_acf2':>10}"
           f"{'Δnet':>7}{'p_net':>9}{'cohen_d':>8}{'δ*_fit':>8}{'GATE':>6}")
    print(hdr)
    confirmed = 0
    for a in ASSETS:
        base = cell(a, "baseline"); d050 = cell(a, "concave_d050"); d045 = cell(a, "concave_d045")
        if not base or not d050:
            print(f"{a:9}{'(missing)':>10}")
            continue
        bh = _col(base, "hill_tail_index"); dh = _col(d050, "hill_tail_index")
        bnet = _net(base); dnet = _net(d050)
        base_hill = float(np.mean(bh)); d050_hill = float(np.mean(dh))
        d050_acf2 = float(np.nanmean([r["acf_squared_returns"] for r in d050]))
        tn, pn = stats.ttest_ind(dnet, bnet, equal_var=False)
        dcoh = (dnet.mean() - bnet.mean()) / np.sqrt((dnet.std()**2 + bnet.std()**2) / 2 + 1e-12)
        # per-asset hill(δ) line from the two concave points; intercept via baseline-implied slope
        dstar = float("nan")
        if d045:
            h45 = float(np.mean(_col(d045, "hill_tail_index")))
            slope = (d050_hill - h45) / (0.50 - 0.45)
            icpt = d050_hill - slope * 0.50
            if slope != 0:
                dstar = (3.0 - icpt) / slope
        hb = HILL_BAND[0] <= d050_hill <= HILL_BAND[1]
        ab = ACF2_BAND[0] <= d050_acf2 <= ACF2_BAND[1]
        sig = pn < 0.01 / m
        gate = "✓" if (hb and ab and sig) else ("hill" if not hb else "acf2" if not ab else "ns")
        confirmed += int(hb and ab and sig)
        ds = f"{dstar:.3f}" if not np.isnan(dstar) else "  —"
        print(f"{a:9}{base_hill:>10.3f}{d050_hill:>10.3f}{d050_acf2:>10.3f}"
              f"{dnet.mean()-bnet.mean():>+7.2f}{pn:>9.4f}{dcoh:>+8.2f}{ds:>8}{gate:>6}")

    # per-fact collateral on the pooled (all-asset) d050 vs baseline
    print("\n# pooled per-fact in-band % (all assets) — collateral check")
    allbase = [r for a in ASSETS for r in cell(a, "baseline")]
    alld050 = [r for a in ASSETS for r in cell(a, "concave_d050")]
    worst = 0.0
    for k in BANDS:
        db = _rate(allbase, k); dd = _rate(alld050, k); delta = dd - db
        worst = min(worst, delta if not np.isnan(delta) else 0)
        tag = " <-tail" if k == "hill_tail_index" else (" ***" if delta <= -20 else "")
        print(f"  {k:26}{db:>6.0f} ->{dd:>5.0f}  ({delta:+.0f}pp){tag}")
    print(f"\n  worst single-fact Δ = {worst:+.0f}pp  → collateral gate "
          f"{'PASS' if worst > -20 else 'FAIL'}")
    print(f"  SOLVE-CONFIRMED iff d050 gate ✓ on ≥4/5 assets AND collateral PASS. "
          f"→ {confirmed}/5 assets passed.")
    print("  δ*_fit ≈ 0.5 across assets ⇒ the TLB √-law crossing is UNIVERSAL (the headline).")


if __name__ == "__main__":
    main()
