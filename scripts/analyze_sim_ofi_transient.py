"""exp 123 Route-A (sim side) — does order-flow imbalance (OFI) show a shock transient the
return/ED *tails* missed?

For each arm's rollouts (npz with `ofi` = signed imbalance ρ∈[-1,1]), compute windowed OFI measures
and ask whether they spike/dip at the shock and relax — distinct from the tail (which only state_kick
moved). Measures per window (W, stride):
  - |ρ|        : mean |imbalance| = coordination level (a coherent shock → net-flow burst)
  - std(ρ)     : imbalance volatility
  - mem(ρ)     : lag-1 autocorrelation = order-flow persistence (Lillo-Farmer memory)
  - sat(ρ)     : fraction with |ρ|>0.5 = extreme-coordination saturation
Aggregated across rollouts. Verdict per arm/measure: transient if the shock window deviates from the
pre-shock baseline by > the control arm's baseline band AND relaxes back.

  conda run -n ecophys python scripts/analyze_sim_ofi_transient.py --exp experiments/123_driven_transient \
      --asset spx --arms control kick6 jump6 --shock 3000
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np


def windowed(ofi: np.ndarray, W: int, stride: int):
    c, mag, std, mem, sat = [], [], [], [], []
    i = 0
    while i + W <= ofi.size:
        seg = ofi[i:i + W]
        seg = seg[np.isfinite(seg)]
        c.append(i + W // 2)
        if seg.size < 8:
            mag.append(np.nan); std.append(np.nan); mem.append(np.nan); sat.append(np.nan)
        else:
            mag.append(float(np.mean(np.abs(seg))))
            std.append(float(np.std(seg)))
            mem.append(float(np.corrcoef(seg[:-1], seg[1:])[0, 1]) if seg.std() > 1e-9 else np.nan)
            sat.append(float(np.mean(np.abs(seg) > 0.5)))
        i += stride
    return np.array(c), {"|rho|": np.array(mag), "std": np.array(std),
                         "mem": np.array(mem), "sat": np.array(sat)}


def arm_curves(exp: Path, asset: str, arm: str, W: int, stride: int):
    files = sorted(exp.glob(f"results_{asset}_{arm}/**/trajectory_*.npz"))
    files = [f for f in files if "ofi" in np.load(f)]
    if not files:
        return None, None
    centers = None
    stacks = {k: [] for k in ("|rho|", "std", "mem", "sat")}
    for f in files:
        ofi = np.asarray(np.load(f)["ofi"], float)
        c, m = windowed(ofi, W, stride)
        centers = c
        for k in stacks:
            stacks[k].append(m[k])
    n = min(len(centers), *(min(len(x) for x in v) for v in stacks.values()))
    centers = centers[:n]
    agg = {k: np.nanmean(np.array([x[:n] for x in v]), axis=0) for k, v in stacks.items()}
    return centers, agg, len(files)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exp", default="experiments/123_driven_transient")
    ap.add_argument("--asset", default="spx")
    ap.add_argument("--arms", nargs="+", default=["control", "kick6", "jump6"])
    ap.add_argument("--shock", type=int, default=3000)
    ap.add_argument("--window", type=int, default=500)
    ap.add_argument("--stride", type=int, default=100)
    args = ap.parse_args()
    exp = Path(args.exp); SS = args.shock

    data = {}
    for arm in args.arms:
        res = arm_curves(exp, args.asset, arm, args.window, args.stride)
        if res[0] is None:
            print(f"  [skip] {arm}: no npz with 'ofi'"); continue
        data[arm] = {"c": res[0], "agg": res[1], "n": res[2]}

    def win(c, a, lo, hi, fn):
        m = (c >= lo) & (c < hi)
        return float(fn(a[m])) if m.any() and np.isfinite(a[m]).any() else float("nan")

    # control baseline band per measure (mean ± std over its whole post-burn-in series)
    ctrl = data.get("control")
    band = {}
    if ctrl:
        for k, a in ctrl["agg"].items():
            m = ctrl["c"] >= 500
            band[k] = (float(np.nanmean(a[m])), float(np.nanstd(a[m])))

    print(f"=== exp 123 sim-side OFI transient ({args.asset}, shock@{SS}, W={args.window}) ===")
    print(f"   control baseline band (mean±std, post-burn-in): "
          + "  ".join(f"{k}={band[k][0]:.3f}±{band[k][1]:.3f}" for k in band) if band else "(no control)")
    report = {"asset": args.asset, "shock": SS, "window": args.window, "control_band": band, "arms": {}}
    for arm, d in data.items():
        c, agg = d["c"], d["agg"]
        print(f"\n{arm}  (n={d['n']})")
        arm_rep = {"n": d["n"], "measures": {}}
        for k, a in agg.items():
            base = win(c, a, 500, SS, np.nanmean)
            shock = win(c, a, SS, SS + 1500, np.nanmax if k != "mem" else (lambda x: x[np.nanargmax(np.abs(x - base))]))
            rec = win(c, a, SS + 4000, 10 ** 9, np.nanmean)
            dev = shock - base
            bstd = band.get(k, (np.nan, np.nan))[1]
            transient = (abs(dev) > max(2 * bstd, 1e-6)) and (abs(rec - base) < abs(dev) * 0.6)
            tag = "TRANSIENT" if (arm != "control" and transient) else ("—" if arm == "control" else "flat")
            print(f"   {k:6} base={base:.3f}  shock={shock:.3f} (Δ={dev:+.3f})  rec={rec:.3f}   {tag}")
            arm_rep["measures"][k] = {"base": base, "shock": shock, "dev": dev, "rec": rec, "transient": bool(arm != "control" and transient)}
        report["arms"][arm] = arm_rep

    out = exp / f"ofi_transient_{args.asset}.json"
    out.write_text(json.dumps(report, indent=2, default=float))
    print(f"\nwrote {out}")
    # one-line verdict
    hits = {arm: [k for k, v in r["measures"].items() if v["transient"]] for arm, r in report["arms"].items() if arm != "control"}
    print("VERDICT:", "; ".join(f"{a}: {'+'.join(ks) if ks else 'no OFI transient'}" for a, ks in hits.items()))


if __name__ == "__main__":
    main()
