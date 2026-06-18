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
    """Directly measure ζ_ED = α(|ED|) AND the |return| tail (cube-law sanity) from trajectories.

    A single-point Hill number is unreliable for heavy tails (it swings wildly with k). So we
    report (i) Hill α at a representative k with 95% bootstrap CI, and (ii) the α-vs-k curve
    (Hill plot, Cont 2001) for BOTH |ED| and |log_returns|. Three independent verdicts per asset:
      - ζ_ED: does its CI include the theory value 1.5?  (tail-transfer δ*=ζ_ED/3)
      - |ret|: does its CI include the cube-law value 3?
      - transfer: α_ret ≈ ζ_ED/δ = 2·ζ_ED  (ratio α_ret/ζ_ED should be ≈2 at δ=0.5)
    If CIs are wide or no α(k) plateau exists, the rollout is too short → need more steps (C).
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from ecomd.eval.stylized_facts import hill_tail_index  # canonical estimator

    ed_of: dict[str, list[np.ndarray]] = defaultdict(list)
    ret_of: dict[str, list[np.ndarray]] = defaultdict(list)
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
        ed_of[asset].append(ed[np.isfinite(ed)])
        if "log_returns" in z:  # sanity series (cube law: Hill α≈3)
            rt = np.asarray(z["log_returns"], dtype=float)
            ret_of[asset].append(rt[np.isfinite(rt)])

    k_grid = [0.005, 0.01, 0.02, 0.05, 0.1]   # Hill-plot sample points
    k_point = 0.02                              # representative k for CI
    n_boot = 200

    print(f"# ζ_ED direct measurement: Hill α on |ED| (theory ζ_ED≈1.5) + |log_returns| sanity (cube law α≈3).")
    print(f"# point k_frac={k_point} with {n_boot}-bootstrap 95% CI; curve sampled at k_frac∈{k_grid}.\n")

    rows = []
    for a in ASSETS:
        ed_chunks = ed_of.get(a, [])
        if not ed_chunks:
            print(f"{a:8}  (no ED)")
            continue
        ed = np.concatenate(ed_chunks)
        rt = np.concatenate(ret_of[a]) if ret_of.get(a) else None

        def curve(x: np.ndarray) -> list[float]:
            out: list[float] = []
            for kf in k_grid:
                try:
                    out.append(float(hill_tail_index(x, k_frac=kf, n_bootstrap=0).estimate))
                except ValueError:
                    out.append(float("nan"))
            return out

        try:
            ed_res = hill_tail_index(ed, k_frac=k_point, n_bootstrap=n_boot)
        except ValueError as e:
            print(f"{a:8}  ED hill failed (n={ed.size}): {e}\n")
            continue
        ed_ci = (ed_res.ci_low, ed_res.ci_high)
        ed_curve = curve(ed)

        ret_res = ret_ci = ret_curve = None
        if rt is not None and rt.size >= 50:
            try:
                ret_res = hill_tail_index(rt, k_frac=k_point, n_bootstrap=n_boot)
                ret_ci = (ret_res.ci_low, ret_res.ci_high)
                ret_curve = curve(rt)
            except ValueError:
                pass

        def fmt_ci(ci: tuple) -> str:
            return f"[{ci[0]:.2f},{ci[1]:.2f}]" if ci and ci[0] is not None else "[—]"

        def fmt_curve(cs: list[float]) -> str:
            return "  ".join(f"{int(kf*1000)}‰:{v:.2f}" for kf, v in zip(k_grid, cs))

        zpred = ZETA_PREDICTED.get(a, float("nan"))
        ed_has15 = ed_ci[0] is not None and (ed_ci[0] <= 1.5 <= ed_ci[1])
        ret_has3 = bool(ret_ci and ret_ci[0] is not None and (ret_ci[0] <= 3.0 <= ret_ci[1]))
        transfer_ratio = (ret_res.estimate / ed_res.estimate) if ret_res else float("nan")

        print(f"{a:8}  n_ED={ed.size:>6}  n_ret={rt.size if rt is not None else 0:>6}")
        print(f"          ζ_ED    = {ed_res.estimate:>6.3f}  {fmt_ci(ed_ci)}   "
              f"(pred {zpred:.3f})   1.5∈CI? {'✓' if ed_has15 else '✗'}   δ*={ed_res.estimate/3:.3f}")
        if ret_res:
            print(f"          |ret| α = {ret_res.estimate:>6.3f}  {fmt_ci(ret_ci)}   "
                  f"3∈CI? {'✓' if ret_has3 else '✗'}   α_ret/ζ_ED={transfer_ratio:.2f} (theory 2.0)")
        print(f"          |ED|  α(k): {fmt_curve(ed_curve)}")
        if ret_curve:
            print(f"          |ret| α(k): {fmt_curve(ret_curve)}")
        print()

        rows.append({
            "asset": a, "n_ED": int(ed.size), "n_ret": int(rt.size) if rt is not None else 0,
            "zeta_ED_measured": float(ed_res.estimate),
            "zeta_ED_ci": [float(c) for c in ed_ci] if ed_ci[0] is not None else None,
            "zeta_ED_predicted": float(zpred), "zeta_ED_includes_1p5": bool(ed_has15),
            "ret_hill": float(ret_res.estimate) if ret_res else None,
            "ret_ci": [float(c) for c in ret_ci] if ret_ci and ret_ci[0] is not None else None,
            "ret_includes_3": bool(ret_has3),
            "transfer_ratio_alpha_ret_over_zeta_ed": float(transfer_ratio) if ret_res else None,
            "ed_alpha_of_k": {f"k{kf}": v for kf, v in zip(k_grid, ed_curve)},
            "ret_alpha_of_k": {f"k{kf}": v for kf, v in zip(k_grid, ret_curve)} if ret_curve else None,
            "k_point": k_point, "k_grid": k_grid, "n_bootstrap": n_boot,
        })

    out = root / "zeta_ed_report.json"
    out.write_text(json.dumps({
        "rows": rows,
        "prediction": "ζ_ED≈1.50 (ndx≈1.60); δ*=ζ_ED/3; cube law |ret| Hill≈3; transfer α_ret=ζ_ED/δ=2·ζ_ED",
        "note": "single-point Hill is unreliable for heavy tails; judge via CI tightness + α(k) plateau.",
    }, indent=2))
    closes = sum(1 for r in rows if r["zeta_ED_includes_1p5"])
    sane = sum(1 for r in rows if r["ret_includes_3"])
    print(f"  VERDICT: ζ_ED CI∋1.5 for {closes}/{len(rows)}; |ret| CI∋3 for {sane}/{len(rows)}.")
    print(f"  Derivation closes iff CIs are tight AND both hold AND α_ret/ζ_ED≈2 (transfer law).")
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
