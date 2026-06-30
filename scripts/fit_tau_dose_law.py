#!/usr/bin/env python3
"""exp 125/126 — G-C relaxation law: fit the dose-response of the post-shock dip and recovery time tau.

For each asset with a state_kick dose sweep (results_<asset>_kick<m>), reads windowed_hill_report.json
and extracts, per dose m:
  - dip(m)  = pre-shock steady alpha_ED  -  post-shock min alpha_ED
  - tau(m)  = recovery time: #steps from the post-shock min back to halfway to the pre-shock level
Fits dip(m) to three pre-specified forms (saturating, power-law, logarithmic) and reports the best by R^2,
plus the sigmoid onset (smallest dose with dip >= 0.5 above the dose=floor baseline).

Usage:  python scripts/fit_tau_dose_law.py --exp DIR [DIR2 ...]
Writes: <first exp dir>/tau_dose_law.json
"""
import argparse, glob, json, os, math
from collections import defaultdict

ASSETS = ("spx", "ndx", "btcusdt", "gold", "eurusd")

try:
    import numpy as np
    from scipy.optimize import curve_fit
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False
    import numpy as np  # numpy is required


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


def dip_tau(w):
    centers = [int(c) for c in w["centers"]]
    aED = w["alpha_ED_mean"]
    shock = int(w.get("shock_step", 3000))
    pre = [m for c, m in zip(centers, aED) if 500 <= c < shock]
    if not pre:
        return None
    pre_lvl = sum(pre) / len(pre)
    post = [(c, m) for c, m in zip(centers, aED) if c >= shock]
    if not post:
        return None
    cmin, vmin = min(post, key=lambda x: x[1])
    dip = pre_lvl - vmin
    half = vmin + 0.5 * (pre_lvl - vmin)
    tau = None
    for c, m in post:
        if c >= cmin and m >= half:
            tau = c - shock
            break
    return {"dip": round(dip, 4), "postmin": round(vmin, 4), "pre": round(pre_lvl, 4),
            "tau_recovery": tau, "min_center": cmin}


def fit_forms(doses, dips):
    x = np.asarray(doses, float)
    y = np.asarray(dips, float)
    results = {}
    if HAVE_SCIPY and len(x) >= 4:
        forms = {
            "saturating": (lambda m, A, k: A * (1 - np.exp(-k * m)), [max(y), 1.0]),
            "power_law":  (lambda m, A, z: A * np.power(np.clip(m, 1e-6, None), z), [1.0, 0.5]),
            "logarithmic": (lambda m, A, b: A * np.log1p(b * m), [1.0, 1.0]),
        }
        for name, (fn, p0) in forms.items():
            try:
                popt, _ = curve_fit(fn, x, y, p0=p0, maxfev=20000)
                resid = y - fn(x, *popt)
                ss_res = float(np.sum(resid ** 2))
                ss_tot = float(np.sum((y - y.mean()) ** 2)) or 1e-12
                results[name] = {"params": [round(float(v), 5) for v in popt],
                                 "r2": round(1 - ss_res / ss_tot, 4)}
            except Exception as e:
                results[name] = {"error": str(e)[:80]}
    best = max((k for k in results if "r2" in results[k]),
               key=lambda k: results[k]["r2"], default=None)
    return results, best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", nargs="+", required=True)
    args = ap.parse_args()
    WIN = read_windowed(args.exp)

    by_asset = defaultdict(dict)  # asset -> dose(float) -> dip_tau
    for arm, w in WIN.items():
        for a in ASSETS:
            if arm.startswith(a + "_kick"):
                try:
                    m = float(arm[len(a) + 5:])
                except ValueError:
                    continue
                dt = dip_tau(w)
                if dt:
                    by_asset[a][m] = dt

    out = {}
    for a, dd in by_asset.items():
        doses = sorted(dd)
        dips = [dd[m]["dip"] for m in doses]
        taus = [dd[m]["tau_recovery"] for m in doses]
        forms, best = fit_forms(doses, dips)
        onset = next((m for m in doses if dd[m]["dip"] >= 0.5), None)
        out[a] = {"doses": doses, "dip": dips, "tau_recovery": taus,
                  "onset_dose_dip>=0.5": onset, "dip_fits": forms, "best_dip_fit": best,
                  "per_dose": {str(m): dd[m] for m in doses}}
        print(f"  {a:<8} doses={doses}  best dip-fit={best} "
              f"(R2={forms.get(best,{}).get('r2') if best else None})  onset={onset}")
    outp = os.path.join(args.exp[0], "tau_dose_law.json")
    json.dump({"by_asset": out,
               "note": "dip(m)=pre-min; tau=steps from post-min back to halfway to pre; "
                       "fits on dip(m). scipy=%s" % HAVE_SCIPY}, open(outp, "w"), indent=1)
    print("wrote", outp)


if __name__ == "__main__":
    main()
