"""Score exp 118 — per-asset hill(δ) lines and the universality of the √-law crossing δ*.

Pools every concave fixed-δ cell across experiments (identical recipe, verified 2026-06-06):
  113 (spx):  results_concave_d{040,050,060,070}_seed*
  114:        results_{asset}_concave_d{045,050}_seed*   (spx d045 included)
  118:        {asset}/results_s{NN}_{asset}_concave_d{040,060}   (partial seed counts OK)

Per asset: OLS fit hill = icpt + slope·δ over all available δ points (point = per-seed hill
values, so the fit is seed-weighted), δ* = δ at hill=3 (the empirical inverse-cubic, same
definition as score_concave_confirm.py), r², and a bootstrap CI on δ* (resample seeds).

Verdict: the √-law crossing is UNIVERSAL iff every asset's δ* 95% CI covers 0.5
(pre-registered headline check; 114's 2-point fits gave ndx 0.589 / eurusd 0.658 — this
re-fit with a 0.40–0.60 lever arm is the noise-vs-deviation decider).

Usage: python scripts/score_delta_grid.py [repo-relative experiments dir, default experiments]
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

RNG = np.random.default_rng(0)
ASSETS = ["spx", "ndx", "gold", "eurusd", "btcusdt"]


def _hill(mj: Path) -> float:
    agg = json.loads(mj.read_text()).get("aggregated", {})
    v = agg.get("hill_tail_index")
    m = (v or {}).get("mean") if isinstance(v, dict) else v
    return float(m) if (m is not None and np.isfinite(m)) else np.nan


def collect(exp_root: Path) -> dict[str, dict[float, list[float]]]:
    pts: dict[str, dict[float, list[float]]] = defaultdict(lambda: defaultdict(list))

    def add(asset: str, delta: float, d: Path) -> None:
        mj = d / "inference_merged.json"
        if mj.exists():
            h = _hill(mj)
            if not np.isnan(h):
                pts[asset][delta].append(h)

    for d in (exp_root / "113_gabaix_solve").glob("results_concave_d*_seed*"):
        m = re.match(r"results_concave_d(\d{3})_seed\d+$", d.name)
        if m:
            add("spx", int(m.group(1)) / 100, d)
    for d in (exp_root / "114_concave_confirm").glob("results_*_concave_d*_seed*"):
        m = re.match(r"results_(\w+?)_concave_d(\d{3})_seed\d+$", d.name)
        if m:
            add(m.group(1), int(m.group(2)) / 100, d)
    for d in (exp_root / "118_delta_grid").glob("*/results_s*_concave_d*"):
        m = re.match(r"results_s\d+_(\w+?)_concave_d(\d{3})$", d.name)
        if m:
            add(m.group(1), int(m.group(2)) / 100, d)
    return pts


def fit(deltas: np.ndarray, hills: np.ndarray) -> tuple[float, float, float, float]:
    """OLS over per-seed points → (slope, icpt, r², δ* at hill=3)."""
    slope, icpt = np.polyfit(deltas, hills, 1)
    pred = icpt + slope * deltas
    ss_res = float(np.sum((hills - pred) ** 2))
    ss_tot = float(np.sum((hills - hills.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    dstar = (3.0 - icpt) / slope if slope != 0 else float("nan")
    return float(slope), float(icpt), r2, float(dstar)


def main() -> None:
    exp_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("experiments")
    pts = collect(exp_root)

    print("# δ-grid — per-asset hill(δ) OLS + √-law crossing δ* (hill=3). target δ*=0.5 (TLB).\n")
    print(f"{'asset':9}{'δ points (n seeds)':34}{'slope':>8}{'r²':>7}{'δ*':>8}{'95%CI':>16}{'covers 0.5':>11}")
    universal = True
    any_fit = False
    for a in ASSETS:
        cells = pts.get(a, {})
        if len(cells) < 2:
            print(f"{a:9}{'(<2 δ points — need 118 results)':34}")
            continue
        pairs = [(d, h) for d, hs in sorted(cells.items()) for h in hs]
        deltas = np.array([p[0] for p in pairs]); hills = np.array([p[1] for p in pairs])
        slope, icpt, r2, dstar = fit(deltas, hills)
        # bootstrap δ* over seeds (resample within each δ cell)
        boots = []
        for _ in range(2000):
            bd, bh = [], []
            for d, hs in cells.items():
                hs = np.asarray(hs)
                bh.extend(RNG.choice(hs, size=len(hs), replace=True)); bd.extend([d] * len(hs))
            try:
                boots.append(fit(np.array(bd), np.array(bh))[3])
            except Exception:
                pass
        lo, hi = (np.nanpercentile(boots, [2.5, 97.5]) if boots else (np.nan, np.nan))
        covers = lo <= 0.5 <= hi
        if len(cells) >= 3:
            any_fit = True
            universal = universal and covers
        desc = " ".join(f"{d:.2f}({len(hs)})" for d, hs in sorted(cells.items()))
        print(f"{a:9}{desc:34}{slope:>8.2f}{r2:>7.2f}{dstar:>8.3f}"
              f"{f'[{lo:.3f},{hi:.3f}]':>16}{'✓' if covers else '✗':>11}")

    if any_fit:
        print(f"\n  VERDICT: √-law crossing δ*≈0.5 {'UNIVERSAL (all ≥3-point CIs cover 0.5)' if universal else 'NOT universal — report the deviating asset(s) honestly'}")
    else:
        print("\n  (no asset has ≥3 δ points yet — run exp 118 first)")


if __name__ == "__main__":
    main()
