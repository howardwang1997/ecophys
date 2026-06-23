"""exp 124 — three revision add-ons on the driven-transient trajectories (C-a / B3 / F-a).

Run where the raw rollout npz live (the H20 box, after a --save-trajectory regen):

  conda run -n ecophys python scripts/analyze_transient_extras.py \
      --exp experiments/123_driven_transient --asset spx --arms control kick6 jump6 --shock 3000

Reads results_{asset}_{arm}/**/trajectory_*.npz (keys: log_returns, ofi, excess_demand) and writes three
JSONs consumed by papers/paper_a_methods/shared/make_figures.py:

  C-a  irrev_dhvg_{asset}.json        — model-free DHVG (+Zumbach) time-irreversibility, base/shock/rec
                                        per arm. Answers "does a stronger estimator see the irreversibility
                                        the sign-level proxy missed?" (Paper A §5; ML4PS C-a slot).
  B3   dip_stat_{asset}.json          — censoring-free heaviness of |ED| during the dip (excess kurtosis +
                                        exceedance fraction vs control), so the dose-response floor does not
                                        rest on the Hill estimator's α≈0.5 saturation.
  F-a  ofi_memory_centered_{asset}.json — OFI lag-1 memory on a *centered* window, so the burst aligns with
                                        the shock instead of lagging it by ~½ window (fig_mechanism panel a).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from ecomd.eval.time_irreversibility import windowed_dhvg, zumbach_asymmetry


def _trajs(exp: Path, asset: str, arm: str) -> list[np.lib.npyio.NpzFile]:
    files = sorted(exp.glob(f"results_{asset}_{arm}/**/trajectory_*.npz"))
    return [np.load(f) for f in files if "ofi" in np.load(f)]


def _win(centers: np.ndarray, vals: np.ndarray, lo: float, hi: float, fn) -> float:
    m = (centers >= lo) & (centers < hi)
    return float(fn(vals[m])) if m.any() else float("nan")


# ── C-a: DHVG / Zumbach irreversibility ───────────────────────────────────────────────────────────
def irrev_arm(trajs, W: int, stride: int):
    centers, dhvg_stack, zumb = None, [], []
    for z in trajs:
        r = np.abs(np.asarray(z["log_returns"], float))   # amplitude structure of |return|
        c, d = windowed_dhvg(r, W, stride)
        centers = c
        dhvg_stack.append(d)
        zumb.append(zumbach_asymmetry(np.asarray(z["log_returns"], float)))
    m = min(len(centers), *(len(x) for x in dhvg_stack))
    dhvg = np.nanmean([x[:m] for x in dhvg_stack], axis=0)
    return centers[:m], dhvg, float(np.nanmean(zumb))


# ── B3: censoring-free dip heaviness of |ED| ──────────────────────────────────────────────────────
def dip_stat_arm(trajs, shock: int):
    """Excess kurtosis and exceedance fraction of |ED| in the dip window vs the pre-shock baseline."""
    base_ed, dip_ed = [], []
    for z in trajs:
        ed = np.abs(np.asarray(z["excess_demand"], float))
        base_ed.append(ed[500:shock])
        dip_ed.append(ed[shock : shock + 1500])
    base = np.concatenate(base_ed)
    dip = np.concatenate(dip_ed)
    q99 = float(np.quantile(base, 0.99))

    def _kurt(a: np.ndarray) -> float:
        a = a - a.mean()
        s = a.std()
        return float((a**4).mean() / s**4 - 3.0) if s > 0 else float("nan")

    return {
        "ed_is_raw": int(trajs[0]["ed_is_raw"]) if "ed_is_raw" in trajs[0] else -1,
        "base_excess_kurtosis": _kurt(base),
        "dip_excess_kurtosis": _kurt(dip),
        "base_exceed_q99": float((base > q99).mean()),
        "dip_exceed_q99": float((dip > q99).mean()),   # >0.01 ⇒ heavier than the control upper tail
        "q99_control": q99,
    }


# ── F-a: centered-window OFI memory series ────────────────────────────────────────────────────────
def centered_memory_arm(trajs, W: int, stride: int):
    half = W // 2
    centers, stack = None, []
    for z in trajs:
        rho = np.asarray(z["ofi"], float)
        c, mem = [], []
        i = half
        while i + half <= rho.size:
            v = rho[i - half : i + half]
            a, b = v[:-1], v[1:]
            sa, sb = a.std(), b.std()
            mem.append(float(((a - a.mean()) * (b - b.mean())).mean() / (sa * sb)) if sa > 0 and sb > 0 else 0.0)
            c.append(i)
            i += stride
        centers = np.asarray(c)
        stack.append(np.asarray(mem))
    m = min(len(centers), *(len(x) for x in stack))
    return centers[:m], np.nanmean([x[:m] for x in stack], axis=0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exp", default="experiments/123_driven_transient")
    ap.add_argument("--asset", default="spx")
    ap.add_argument("--arms", nargs="+", default=["control", "kick6", "jump6"])
    ap.add_argument("--shock", type=int, default=3000)
    ap.add_argument("--window", type=int, default=500)
    ap.add_argument("--stride", type=int, default=100)
    args = ap.parse_args()
    exp, SS = Path(args.exp), args.shock

    loaded = {arm: _trajs(exp, args.asset, arm) for arm in args.arms}
    loaded = {a: t for a, t in loaded.items() if t}
    if not loaded:
        print(f"no trajectory npz under {exp}/results_{args.asset}_*/ — regenerate with --save-trajectory")
        return

    # C-a
    print(f"=== C-a DHVG irreversibility ({args.asset}, shock@{SS}) ===")
    irr = {"asset": args.asset, "shock": SS, "window": args.window, "estimator": "DHVG-KL", "arms": {}}
    for arm, trajs in loaded.items():
        c, d, zb = irrev_arm(trajs, args.window, args.stride)
        base = _win(c, d, 500, SS, np.nanmean)
        shock = _win(c, d, SS, SS + 1500, np.nanmax)
        rec = _win(c, d, SS + 4000, 10**9, np.nanmean)
        burst = arm != "control" and (shock - base) > 0.02
        print(f"  {arm:9} DHVG base={base:.4f} shock={shock:.4f} (Δ={shock-base:+.4f}) rec={rec:.4f} "
              f"zumbach={zb:+.4f}  {'BURST' if burst else 'flat'}")
        irr["arms"][arm] = {"base": base, "shock": shock, "rec": rec, "zumbach": zb, "burst": bool(burst)}
    (exp / f"irrev_dhvg_{args.asset}.json").write_text(json.dumps(irr, indent=2))

    # B3
    print(f"=== B3 censoring-free dip heaviness of |ED| ({args.asset}) ===")
    dip = {"asset": args.asset, "shock": SS, "arms": {}}
    for arm, trajs in loaded.items():
        s = dip_stat_arm(trajs, SS)
        dip["arms"][arm] = s
        print(f"  {arm:9} kurtosis base={s['base_excess_kurtosis']:.2f} dip={s['dip_excess_kurtosis']:.2f} | "
              f"exceed_q99 base={s['base_exceed_q99']:.4f} dip={s['dip_exceed_q99']:.4f}")
    (exp / f"dip_stat_{args.asset}.json").write_text(json.dumps(dip, indent=2))

    # F-a
    print(f"=== F-a centered-window OFI memory ({args.asset}) ===")
    mem = {"asset": args.asset, "shock": SS, "window": args.window, "arms": {}}
    for arm in ("control", "kick6"):
        if arm in loaded:
            c, mm = centered_memory_arm(loaded[arm], args.window, args.stride)
            peak = int(c[int(np.nanargmax(mm))]) if mm.size else -1
            mem["arms"][arm] = {"centers": c.tolist(), "mem": mm.tolist(), "peak_center": peak}
            print(f"  {arm:9} centered-memory peak at t={peak} (shock={SS}; trailing-window peaked ~+250)")
    (exp / f"ofi_memory_centered_{args.asset}.json").write_text(json.dumps(mem, indent=2))
    print("wrote irrev_dhvg / dip_stat / ofi_memory_centered JSONs")


if __name__ == "__main__":
    main()
