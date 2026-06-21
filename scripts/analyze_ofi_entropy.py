"""exp 124 E-S3 — entropy-production / time-asymmetry proxy of the (Δp, OFI) process.

A driven, irreversible process has a non-zero entropy-production rate; an equilibrium (reversible)
one has zero. We estimate a windowed irreversibility proxy on the joint symbol sequence
a_t = (sign Δp_t, sign OFI_t) ∈ {0,1,2,3}: from the pair-transition distribution P(a→b),

    EP ≈ Σ_{a,b} P(a→b) · log[ P(a→b) / P(b→a) ]     (KL between forward and time-reversed transitions)

EP=0 under detailed balance; EP>0 signals time-irreversibility (non-equilibrium driving). We ask
whether EP bursts at the shock and relaxes (coherent liquidation) vs stays flat (control / price gap).

Reads the committed OFI rollouts (npz with log_returns + ofi). Run where the npz live (the H20 box).

  conda run -n ecophys python scripts/analyze_ofi_entropy.py --exp experiments/123_driven_transient \
      --asset spx --arms control kick6 jump6 --shock 3000
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np

K = 4  # 2 (sign Δp) × 2 (sign OFI)


def windowed_ep(dp: np.ndarray, ofi: np.ndarray, W: int, stride: int):
    sym = (2 * (dp > 0).astype(np.int64) + (ofi > 0).astype(np.int64))
    centers, ep = [], []
    i = 0
    while i + W <= sym.size:
        s = sym[i:i + W]
        a, b = s[:-1], s[1:]
        N = np.bincount(a * K + b, minlength=K * K).reshape(K, K).astype(float)
        N += 1e-3                       # Laplace smoothing (avoids log 0)
        P = N / N.sum()
        ep = ep + [float(np.sum(P * np.log(P / P.T)))]
        centers.append(i + W // 2)
        i += stride
    return np.array(centers), np.array(ep)


def arm_curve(exp: Path, asset: str, arm: str, W: int, stride: int):
    files = [f for f in sorted(exp.glob(f"results_{asset}_{arm}/**/trajectory_*.npz"))
             if "ofi" in np.load(f)]
    if not files:
        return None, None
    centers, stack = None, []
    for f in files:
        z = np.load(f)
        dp = np.asarray(z["log_returns"], float)
        ofi = np.asarray(z["ofi"], float)
        n = min(dp.size, ofi.size)
        c, e = windowed_ep(dp[:n], ofi[:n], W, stride)
        centers = c
        stack.append(e)
    m = min(len(centers), *(len(x) for x in stack))
    return centers[:m], np.nanmean(np.array([x[:m] for x in stack]), axis=0)


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

    def win(c, a, lo, hi, fn):
        m = (c >= lo) & (c < hi)
        return float(fn(a[m])) if m.any() else float("nan")

    print(f"=== exp 124 E-S3 — (Δp,OFI) entropy-production proxy ({args.asset}, shock@{SS}) ===")
    report = {"asset": args.asset, "shock": SS, "window": args.window, "arms": {}}
    for arm in args.arms:
        c, ep = arm_curve(exp, args.asset, arm, args.window, args.stride)
        if c is None:
            print(f"  {arm:9}: no OFI npz"); continue
        base = win(c, ep, 500, SS, np.nanmean)
        shock = win(c, ep, SS, SS + 1500, np.nanmax)
        rec = win(c, ep, SS + 4000, 10 ** 9, np.nanmean)
        burst = (shock - base) > 0.05 and abs(rec - base) < abs(shock - base) * 0.6
        tag = "BURST+RELAX" if (arm != "control" and burst) else ("—" if arm == "control" else "flat")
        print(f"  {arm:9} EP base={base:.3f} shock={shock:.3f} (Δ={shock-base:+.3f}) rec={rec:.3f}  {tag}")
        report["arms"][arm] = {"base": base, "shock": shock, "rec": rec,
                               "burst": bool(arm != "control" and burst)}
    out = exp / f"ofi_entropy_{args.asset}.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
