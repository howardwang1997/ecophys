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


def windows_mode(root: Path, window: int, stride: int, k_frac: float,
                 shock_step: int | None) -> None:
    """Sliding-window Hill α(t) over trajectory npz — the exp 123 driven-transient
    estimator. Renders the tail-heaviness time profile: a burn-in dip at t≈0 (heavy,
    low α), a light steady-state plateau (high α), and — if a shock was injected —
    a post-shock dip-and-recover. Aggregates across rollouts (npz files). Heavy tail
    ⇒ LOW α; light ⇒ HIGH α. Cube law α≈3.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from ecomd.eval.stylized_facts import hill_tail_index

    npz_files = sorted(root.glob("**/trajectory_*.npz"))
    if not npz_files:
        print(f"no trajectory_*.npz under {root} — run run_large.py --save-trajectory first")
        sys.exit(2)

    def windowed_hill(x: np.ndarray) -> tuple[list[int], list[float]]:
        centers: list[int] = []
        alphas: list[float] = []
        start = 0
        while start + window <= x.size:
            seg = x[start:start + window]
            seg = seg[np.isfinite(seg)]
            try:
                a = float(hill_tail_index(seg, k_frac=k_frac, side="both", n_bootstrap=0).estimate)
            except Exception:
                a = float("nan")
            centers.append(start + window // 2)
            alphas.append(a)
            start += stride
        return centers, alphas

    ed_curves: list[list[float]] = []
    ret_curves: list[list[float]] = []
    centers_ref: list[int] = []
    ed_is_raw: int | None = None
    for f in npz_files:
        z = np.load(f)
        if ed_is_raw is None and "ed_is_raw" in z:
            ed_is_raw = int(z["ed_is_raw"])
        if "excess_demand" in z:
            c, a = windowed_hill(np.asarray(z["excess_demand"], dtype=float))
            centers_ref = c
            ed_curves.append(a)
        if "log_returns" in z:
            c, a = windowed_hill(np.asarray(z["log_returns"], dtype=float))
            centers_ref = c or centers_ref
            ret_curves.append(a)

    def agg(curves: list[list[float]]) -> tuple[list, list]:
        if not curves:
            return [], []
        width = min(len(c) for c in curves)
        M = np.array([c[:width] for c in curves], dtype=float)
        with np.errstate(all="ignore"):
            return list(np.nanmean(M, axis=0)), list(np.nanstd(M, axis=0))

    ed_mean, ed_std = agg(ed_curves)
    ret_mean, ret_std = agg(ret_curves)
    centers = centers_ref[:len(ed_mean or ret_mean)]

    ed_lbl = {1: "RAW pre-impact (ζ_ED)", 0: "POST-impact (=return tail)"}.get(
        ed_is_raw, "unknown (re-run with log_raw_excess_demand)")
    print(f"# windowed Hill α(t): window={window} stride={stride} k_frac={k_frac}  "
          f"({len(npz_files)} rollouts)")
    print(f"# excess_demand logged as: {ed_lbl}.  heavy tail⇒low α, light⇒high α, cube law α≈3.")
    if shock_step is not None:
        print(f"# shock injected at step {shock_step} (marked ▼).")
    print(f"\n{'center':>8} {'α_ED':>7} {'±':>5} {'α_ret':>7} {'±':>5}")
    for i, c in enumerate(centers):
        mark = " ▼shock" if (shock_step is not None and abs(c - shock_step) <= stride // 2) else ""
        em = ed_mean[i] if i < len(ed_mean) else float("nan")
        es = ed_std[i] if i < len(ed_std) else float("nan")
        rm = ret_mean[i] if i < len(ret_mean) else float("nan")
        rs = ret_std[i] if i < len(ret_std) else float("nan")
        print(f"{c:>8} {em:>7.2f} {es:>5.2f} {rm:>7.2f} {rs:>5.2f}{mark}")

    out = root / "windowed_hill_report.json"
    out.write_text(json.dumps({
        "window": window, "stride": stride, "k_frac": k_frac, "shock_step": shock_step,
        "n_rollouts": len(npz_files), "ed_is_raw": ed_is_raw,
        "centers": [int(c) for c in centers],
        "alpha_ED_mean": [float(v) for v in ed_mean], "alpha_ED_std": [float(v) for v in ed_std],
        "alpha_ret_mean": [float(v) for v in ret_mean], "alpha_ret_std": [float(v) for v in ret_std],
        "note": "exp 123 driven-transient: burn-in dip + steady plateau + (if shocked) dip-and-recover.",
    }, indent=2))
    print(f"\n  wrote {out}")


def r1_warmup_mode(root: Path, drops: tuple[int, ...] = (0, 20, 50, 200)) -> None:
    """R1 magnitude: reproduce the STANDARD `hill_tail_index` (k_frac=0.05, side='both' — exactly
    `compute_all`'s call) on each R1 cell's RETURN series WITH vs WITHOUT a warmup discard. Answers
    Phase 0's open magnitude question: does the concave 'in-band' hill flip to TOO-THIN once burn-in
    is dropped, and does baseline leave the TOO-FAT regime? Cells = `r1_*` dirs from
    `gpu_exp123_stage1.sh r1` (114/113 baseline + concave_d050, --save-trajectory).
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from ecomd.eval.stylized_facts import hill_tail_index  # canonical standard estimator

    BAND = (2.0, 4.0)
    cell_dirs = sorted(d for d in root.glob("r1_*") if d.is_dir())
    if not cell_dirs:
        print(f"no r1_* cell dirs under {root} — run `gpu_exp123_stage1.sh r1` first")
        sys.exit(2)

    def verdict(h: float) -> str:
        return "IN-BAND" if BAND[0] <= h <= BAND[1] else ("TOO-FAT" if h < BAND[0] else "TOO-THIN")

    rows = []
    print(f"# R1 standard-hill (k_frac=0.05, side=both — as compute_all) vs warmup discard. band {BAND}.")
    print(f"# heavy⇒low hill. drops={list(drops)} steps.\n")
    hdr = "cell".ljust(22) + "".join(f"drop{d:>4}".rjust(14) for d in drops) + "   Δ(50-0)  flip?"
    print(hdr)
    for d in cell_dirs:
        npz = sorted(d.glob("**/trajectory_*.npz"))
        if not npz:
            continue
        per_drop: dict[int, tuple[float, float, int]] = {}
        for drop in drops:
            hills = []
            for f in npz:
                z = np.load(f)
                if "log_returns" not in z:
                    continue
                r = np.asarray(z["log_returns"], dtype=float)[drop:]
                r = r[np.isfinite(r)]
                if r.size < 50:
                    continue
                try:
                    hills.append(float(hill_tail_index(r, k_frac=0.05, side="both").estimate))
                except Exception:
                    pass
            if hills:
                per_drop[drop] = (float(np.mean(hills)), float(np.std(hills)), len(hills))
        if not per_drop:
            continue
        cells = "".join(
            (f"{per_drop[d][0]:6.2f}±{per_drop[d][1]:.2f}" if d in per_drop else "    —    ").rjust(14)
            for d in drops)
        h0 = per_drop.get(0, (float("nan"),))[0]
        h50 = per_drop.get(50, (float("nan"),))[0]
        delta = h50 - h0
        flip = f"{verdict(h0)}→{verdict(h50)}" if np.isfinite(delta) else "—"
        print(f"{d.name.ljust(22)}{cells}   {delta:+7.2f}  {flip}")
        rows.append({"cell": d.name, "n_rollouts": len(npz),
                     "hill_by_drop": {str(k): {"mean": v[0], "std": v[1], "n": v[2]}
                                      for k, v in per_drop.items()},
                     "delta_50_minus_0": float(delta) if np.isfinite(delta) else None,
                     "verdict_drop0": verdict(h0) if np.isfinite(h0) else None,
                     "verdict_drop50": verdict(h50) if np.isfinite(h50) else None})

    out = root / "r1_warmup_report.json"
    out.write_text(json.dumps({"band": list(BAND), "drops": list(drops),
                               "estimator": "hill_tail_index(k_frac=0.05, side=both)", "rows": rows}, indent=2))
    print("\n  R1 verdict: contamination is real iff dropping warmup moves hill UP (Δ>0) and the")
    print("  concave cell flips IN-BAND→TOO-THIN. Then the 5-asset concave 'solve' is burn-in-held.")
    print(f"  wrote {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("exp_dir", nargs="?", default="experiments",
                    help="experiments root for fit mode (default: experiments)")
    ap.add_argument("--measure-zeta", metavar="DIR", default=None,
                    help="directory with results_<asset>/trajectory_*.npz → measure ζ_ED directly")
    ap.add_argument("--windows", metavar="DIR", default=None,
                    help="dir with trajectory_*.npz → sliding-window Hill α(t) (exp 123 driven-transient)")
    ap.add_argument("--window", type=int, default=500, help="window length (steps)")
    ap.add_argument("--stride", type=int, default=100, help="window stride (steps)")
    ap.add_argument("--k-frac", type=float, default=0.1, help="Hill k fraction per window")
    ap.add_argument("--shock-step", type=int, default=None, help="step where a shock was injected (marker)")
    ap.add_argument("--r1-warmup", metavar="DIR", default=None,
                    help="dir with r1_*/trajectory_*.npz → standard hill with/without warmup discard (R1 magnitude)")
    args = ap.parse_args()
    if args.r1_warmup:
        r1_warmup_mode(Path(args.r1_warmup))
    elif args.windows:
        windows_mode(Path(args.windows), args.window, args.stride, args.k_frac, args.shock_step)
    elif args.measure_zeta:
        measure_zeta_mode(Path(args.measure_zeta))
    else:
        fit_mode(Path(args.exp_dir))


if __name__ == "__main__":
    main()
