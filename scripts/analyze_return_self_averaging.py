#!/usr/bin/env python3
"""exp 126 — H-D2' (re-pre-registered): is the RETURN-tail self-averaging genuine, or a scaling artifact?

exp 125 found steady alpha_ED FLAT in N but the return tail alpha_ret RISING with N. alpha_ret rising
could be (a) genuine CLT Gaussianization of returns, or (b) a trivial consequence of returns shrinking
with N (a scale change the Hill index should be invariant to, but the bulk/tail ratio can shift). The
decisive control: standardize returns by their own (EWMA) volatility, THEN Hill-estimate the tail. If
the *vol-standardized* return tail still lightens with N, the self-averaging is a genuine shape change.

Reads, per asset (spx, btcusdt) and N in the nscan sweep:
  - alpha_ED(N), alpha_ret(N) from windowed_hill_report.json (warm-up discarded),
  - alpha_ret_standardized(N) from the trajectory npz log_returns (warm-up [0,500) dropped, EWMA-vol
    standardized, Hill k_frac=0.1 on |.|) -- only when the npz are present (post-gather / on H20).
Fits each vs log10(N): slope + R^2.

Usage:  python scripts/analyze_return_self_averaging.py --exp DIR [DIR2 ...]
Writes: <first exp dir>/return_self_averaging.json
"""
import argparse, glob, json, os, math
from collections import defaultdict
import numpy as np

ASSETS = ("spx", "ndx", "btcusdt", "gold", "eurusd")
N_GRID = (100, 300, 1000, 3000, 10000, 30000, 60000, 100000)
EWMA_LAMBDA = 0.05
WARMUP = 500
K_FRAC = 0.1


def _arm(path):
    for p in path.split(os.sep):
        if p.startswith("results_"):
            return p[len("results_"):]
    return None


def read_windowed(exp_dirs):
    out = {}
    for e in exp_dirs:
        for p in glob.glob(os.path.join(e, "results_*", "windowed_hill_report.json")):
            try:
                out[_arm(p)] = json.load(open(p))
            except Exception:
                pass
    return out


def steady_mean(w, key):
    centers = [int(c) for c in w["centers"]]
    vals = w[key]
    shock = int(w.get("shock_step", 3000))
    s = [v for c, v in zip(centers, vals) if c >= WARMUP and c < shock] or \
        [v for c, v in zip(centers, vals) if c >= WARMUP]
    return sum(s) / len(s) if s else None


def hill_alpha(x, k_frac=K_FRAC):
    a = np.abs(np.asarray(x, float))
    a = a[a > 0]
    n = a.size
    k = max(10, int(k_frac * n))
    if n < k + 2:
        return None
    a = np.sort(a)[::-1]
    xk = a[k]
    if xk <= 0:
        return None
    logs = np.log(a[:k] / xk)
    s = logs.mean()
    return float(1.0 / s) if s > 0 else None


def ewma_standardize(r):
    r = np.asarray(r, float)
    var = np.empty_like(r)
    v = float(np.var(r[:50])) if r.size >= 50 else float(np.var(r)) or 1e-12
    for i, x in enumerate(r):
        v = (1 - EWMA_LAMBDA) * v + EWMA_LAMBDA * x * x
        var[i] = v if v > 0 else 1e-12
    return r / np.sqrt(var)


def std_return_alpha(exp_dirs, asset, N):
    arm = f"{asset}_nscan{N}"
    files = []
    for e in exp_dirs:
        files += glob.glob(os.path.join(e, f"results_{arm}", "**", "trajectory_*.npz"), recursive=True)
    if not files:
        return None, 0
    alphas = []
    for f in files:
        try:
            z = np.load(f)
            if "log_returns" not in z:
                continue
            r = np.asarray(z["log_returns"], float)[WARMUP:]
            if r.size < 200:
                continue
            a = hill_alpha(ewma_standardize(r))
            if a is not None:
                alphas.append(a)
        except Exception:
            continue
    return (float(np.mean(alphas)) if alphas else None), len(alphas)


def loglinfit(N, y):
    pts = [(math.log10(n), v) for n, v in zip(N, y) if v is not None]
    if len(pts) < 3:
        return None
    x = np.array([p[0] for p in pts]); yy = np.array([p[1] for p in pts])
    b, a = np.polyfit(x, yy, 1)
    yhat = a + b * x
    ss_res = float(np.sum((yy - yhat) ** 2)); ss_tot = float(np.sum((yy - yy.mean()) ** 2)) or 1e-12
    return {"slope_per_decade": round(float(b), 4), "intercept": round(float(a), 4),
            "r2": round(1 - ss_res / ss_tot, 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", nargs="+", required=True)
    args = ap.parse_args()
    WIN = read_windowed(args.exp)

    out = {}
    for a in ASSETS:
        aED, aRET, aRETstd, nstd = [], [], [], []
        for N in N_GRID:
            w = WIN.get(f"{a}_nscan{N}")
            aED.append(round(steady_mean(w, "alpha_ED_mean"), 4) if w else None)
            aRET.append(round(steady_mean(w, "alpha_ret_mean"), 4) if w else None)
            s, ns = std_return_alpha(args.exp, a, N)
            aRETstd.append(round(s, 4) if s is not None else None)
            nstd.append(ns)
        out[a] = {
            "N": list(N_GRID),
            "alpha_ED": aED, "fit_alpha_ED": loglinfit(N_GRID, aED),
            "alpha_ret": aRET, "fit_alpha_ret": loglinfit(N_GRID, aRET),
            "alpha_ret_vol_standardized": aRETstd, "n_npz_per_N": nstd,
            "fit_alpha_ret_std": loglinfit(N_GRID, aRETstd),
        }
        fr = out[a]["fit_alpha_ret"]; fs = out[a]["fit_alpha_ret_std"]
        print(f"  {a}: alpha_ret slope/decade={fr['slope_per_decade'] if fr else None} "
              f"(R2={fr['r2'] if fr else None}); vol-std slope={fs['slope_per_decade'] if fs else 'NO-NPZ'}")

    out["verdict_rule"] = ("alpha_ret rises (positive slope) = self-averaging on returns. If "
                           "alpha_ret_vol_standardized ALSO rises -> genuine CLT shape change (re-pre-"
                           "registered headline). If flat -> the raw rise was a return-scaling artifact "
                           "and alpha_ED-flat stands as the primary result. npz required for the control.")
    outp = os.path.join(args.exp[0], "return_self_averaging.json")
    json.dump(out, open(outp, "w"), indent=1)
    print("wrote", outp)


if __name__ == "__main__":
    main()
