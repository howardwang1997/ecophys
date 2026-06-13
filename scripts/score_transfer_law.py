"""Tail-transfer law for concave price impact:  α_return = ζ_ED / δ   (theory_tail_transfer.md).

Two modes:
  (default)        fit:  test Hill·δ ≈ const = ζ_ED across the δ-grid (113/114/118), no new data.
  --measure-zeta D  measure ζ_ED DIRECTLY: Hill-estimate the tail of |ED| from trajectory npz files
                    under D/results_<asset>/ (run_large.py --save-trajectory), and compare to the
                    Hill·δ prediction. This closes the derivation end-to-end (P0 in the gap list).

Usage:
  python scripts/score_transfer_law.py                                   # fit mode
  python scripts/score_transfer_law.py --measure-zeta experiments/122_zeta_ed
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ASSETS = ["spx", "ndx", "gold", "eurusd", "btcusdt"]
# ζ_ED predicted via the law from the δ-grid Hill·δ means (score this file's fit mode, 2026-06-13).
ZETA_PREDICTED = {"spx": 1.483, "ndx": 1.596, "gold": 1.509, "eurusd": 1.551, "btcusdt": 1.492}


# ─────────────────────────── fit mode (existing) ───────────────────────────
def _hill_mean(d: Path) -> float:
    a = json.loads((d / "inference_merged.json").read_text()).get("aggregated", {})
    v = a.get("hill_tail_index")
    m = v.get("mean") if isinstance(v, dict) else v
    return float(m) if (m is not None and np.isfinite(m)) else np.nan


def _collect(exp: Path) -> dict[str, dict[float, list[float]]]:
    pts: dict[str, dict[float, list[float]]] = defaultdict(lambda: defaultdict(list))

    def add(asset: str, delta: float, d: Path) -> None:
        if (d / "inference_merged.json").exists():
            h = _hill_mean(d)
            if not np.isnan(h):
                pts[asset][delta].append(h)

    for d in (exp / "113_gabaix_solve").glob("results_concave_d*_seed*"):
        m = re.match(r"results_concave_d(\d{3})_seed\d+$", d.name)
        if m:
            add("spx", int(m.group(1)) / 100, d)
    for d in (exp / "114_concave_confirm").glob("results_*_concave_d*_seed*"):
        m = re.match(r"results_(\w+?)_concave_d(\d{3})_seed\d+$", d.name)
        if m:
            add(m.group(1), int(m.group(2)) / 100, d)
    for d in (exp / "118_delta_grid").glob("*/results_s*_concave_d*"):
        m = re.match(r"results_s\d+_(\w+?)_concave_d(\d{3})$", d.name)
        if m:
            add(m.group(1), int(m.group(2)) / 100, d)
    return pts


def fit_mode(exp: Path) -> None:
    pts = _collect(exp)
    print(f"{'asset':8}{'δ: meanHill (Hill·δ)':52}{'lin r²':>8}{'inv r²':>8}"
          f"{'ζ=Hill·δ':>11}{'CV%':>7}{'δ*=ζ/3':>9}")
    for a in ASSETS:
        cells = pts.get(a, {})
        if len(cells) < 3:
            print(f"{a:8}(<3 δ)")
            continue
        ds = np.array(sorted(cells))
        hm = np.array([np.mean(cells[d]) for d in ds])
        p = np.polyfit(ds, hm, 1)
        r2_lin = 1 - np.sum((hm - np.polyval(p, ds)) ** 2) / np.sum((hm - hm.mean()) ** 2)
        x = 1 / ds
        c = np.sum(x * hm) / np.sum(x * x)  # OLS Hill = c·(1/δ)
        r2_inv = 1 - np.sum((hm - c * x) ** 2) / np.sum((hm - hm.mean()) ** 2)
        prod = hm * ds
        zeta, cv = prod.mean(), 100 * prod.std() / prod.mean()
        desc = " ".join(f"{d:.2f}:{h:.2f}({h*d:.2f})" for d, h in zip(ds, hm))
        print(f"{a:8}{desc:52}{r2_lin:>8.2f}{r2_inv:>8.2f}{zeta:>11.3f}{cv:>7.1f}{zeta/3:>9.3f}")
    print("\n transfer law predicts: Hill·δ ≈ const (=ζ_ED) across the grid, δ*≈0.5 ⟺ ζ_ED≈1.5")


# ─────────────────────── measure-zeta mode (new, P0) ───────────────────────
def _asset_of(results_dir: Path) -> str | None:
    """results_<asset>[...] → <asset>; tolerate the 113/114 naming too."""
    name = results_dir.name
    for a in ASSETS:
        if a in name:
            return a
    return None


def measure_zeta_mode(root: Path) -> None:
    """Directly Hill-estimate ζ_ED = α(|ED|) from saved trajectories, per asset."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from ecomd.eval.stylized_facts import hill_tail_index  # canonical estimator

    by_asset: dict[str, list[np.ndarray]] = defaultdict(list)
    npz_files = sorted(root.glob("results_*/trajectory_*.npz"))
    if not npz_files:
        print(f"no trajectory_*.npz under {root}/results_*/ — run run_large.py --save-trajectory first")
        sys.exit(2)
    for f in npz_files:
        asset = _asset_of(f.parent)
        if asset is None:
            print(f"  [warn] cannot infer asset from {f.parent.name} — skipping")
            continue
        z = np.load(f)
        if "excess_demand" not in z:
            print(f"  [warn] {f.name} has no 'excess_demand' (re-run with --save-trajectory) — skip")
            continue
        ed = np.asarray(z["excess_demand"], dtype=float)
        by_asset[asset].append(ed[np.isfinite(ed)])

    print(f"# ζ_ED measured directly (Hill on |ED|, k_frac=0.05) vs predicted via Hill·δ. "
          f"theory: δ*=ζ_ED/3.\n")
    print(f"{'asset':8}{'n_ED':>10}{'ζ_ED(meas)':>12}{'ζ_ED(pred)':>12}{'Δ':>8}{'δ*=ζ/3':>9}{'covers 1.5?':>12}")
    rows = []
    for a in ASSETS:
        chunks = by_asset.get(a, [])
        if not chunks:
            print(f"{a:8}{'(no ED)':>10}")
            continue
        ed = np.concatenate(chunks)
        try:
            res = hill_tail_index(ed, k_frac=0.05, side="both", n_bootstrap=0)
            zmeas = float(res.estimate)
        except Exception as e:  # too few points / degenerate
            print(f"{a:8}{ed.size:>10}  hill failed: {e}")
            continue
        zpred = ZETA_PREDICTED.get(a, float("nan"))
        near = "✓" if abs(zmeas - 1.5) <= 0.2 else "✗"
        print(f"{a:8}{ed.size:>10}{zmeas:>12.3f}{zpred:>12.3f}{zmeas-zpred:>+8.3f}"
              f"{zmeas/3:>9.3f}{near:>12}")
        rows.append({"asset": a, "n_ED": int(ed.size), "zeta_ED_measured": zmeas,
                     "zeta_ED_predicted_via_hilldelta": zpred, "delta_star_from_measured": zmeas / 3})
    out = root / "zeta_ed_report.json"
    out.write_text(json.dumps({"rows": rows, "prediction": "ζ_ED≈1.50 (ndx≈1.60); δ*=ζ_ED/3"}, indent=2))
    print(f"\n  VERDICT: derivation closes end-to-end iff measured ζ_ED ≈ predicted (≈1.5, ndx≈1.6).")
    print(f"  wrote {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("exp_dir", nargs="?", default="experiments",
                    help="experiments root for fit mode (default: experiments)")
    ap.add_argument("--measure-zeta", metavar="DIR", default=None,
                    help="directory with results_<asset>/trajectory_*.npz → measure ζ_ED directly")
    args = ap.parse_args()
    if args.measure_zeta:
        measure_zeta_mode(Path(args.measure_zeta))
    else:
        fit_mode(Path(args.exp_dir))


if __name__ == "__main__":
    main()
