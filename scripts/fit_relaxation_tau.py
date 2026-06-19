"""exp 123 Stage 2d — relaxation-timescale τ of the driven heavy-tail transient.

For each shocked arm, isolate the post-shock recovery limb of α_ED(t) (from the post-shock
minimum onward) and fit an exponential relaxation

    α(t) = α_∞ − (α_∞ − α_min)·exp(−(t − t_min)/τ)

τ is the recovery timescale (in steps). Question: is τ universal across dose (a single intrinsic
relaxation time → strong physics statement) or dose-dependent? Also fit the control's t=0 burn-in
limb as the template, to compare the DRIVEN τ against the cold-start τ.

Pure analysis of the committed windowed_hill_report.json files (no sim, no GPU).

  conda run -n ecophys python scripts/fit_relaxation_tau.py --asset spx [--channel kick]
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit

LIGHT = 4.0
EXP = Path("experiments/123_driven_transient")


def _load(asset: str, arm: str):
    p = EXP / f"results_{asset}_{arm}" / "windowed_hill_report.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    c = np.asarray(d["centers"], float)
    a = np.asarray(d["alpha_ED_mean"], float)
    n = min(len(c), len(a))
    return {"shock": d.get("shock_step", 3000), "c": c[:n], "a": a[:n]}


def _recovery(c, a, t0, t1):
    """Exp-relaxation fit on [t_min, t1] where t_min = argmin α in [t0, t0+1500]. Returns dict."""
    seek = (c >= t0) & (c < t0 + 1500)
    if not seek.any():
        return None
    i_min = np.where(seek)[0][int(np.argmin(a[seek]))]
    t_min, a_min = c[i_min], a[i_min]
    m = (c >= t_min) & (c < t1)
    if m.sum() < 4:
        return None
    tt, aa = c[m] - t_min, a[m]

    def f(t, a_inf, amp, tau):
        return a_inf - amp * np.exp(-t / tau)

    try:
        p0 = [max(a.max(), LIGHT), max(a.max() - a_min, 0.5), 400.0]
        popt, _ = curve_fit(f, tt, aa, p0=p0,
                            bounds=([2.0, 0.0, 20.0], [12.0, 12.0, 6000.0]), maxfev=20000)
        resid = aa - f(tt, *popt)
        ss = 1.0 - np.sum(resid ** 2) / max(np.sum((aa - aa.mean()) ** 2), 1e-9)
        return {"t_min": float(t_min), "a_min": float(a_min),
                "a_inf": float(popt[0]), "amp": float(popt[1]), "tau": float(popt[2]),
                "r2": float(ss), "n_pts": int(m.sum())}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e), "t_min": float(t_min), "a_min": float(a_min)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--asset", default="spx")
    ap.add_argument("--channel", default="kick", choices=["kick", "jump"])
    args = ap.parse_args()
    asset, channel = args.asset, args.channel

    ctrl = _load(asset, "control")
    if ctrl is None:
        raise SystemExit(f"no results_{asset}_control report — run eval first")
    shock = ctrl["shock"]

    # burn-in template τ: the control's t=0 recovery limb (fit over [0, shock)).
    burn = _recovery(ctrl["c"], ctrl["a"], t0=ctrl["c"][0], t1=shock)

    def mag_of(arm: str) -> float:
        try:
            return float(arm.replace(channel, ""))
        except ValueError:
            return float("inf")
    arms = sorted((d.name.replace(f"results_{asset}_", "")
                   for d in EXP.glob(f"results_{asset}_{channel}*")
                   if (d / "windowed_hill_report.json").exists()), key=mag_of)

    rows = {}
    for arm in arms:
        o = _load(asset, arm)
        if o is None:
            continue
        rows[arm] = _recovery(o["c"], o["a"], t0=shock, t1=10 ** 9)

    print(f"=== exp 123 Stage 2d — relaxation τ ({asset}, channel={channel}, shock@{shock}) ===")
    if burn and "tau" in burn:
        print(f"burn-in (t=0) template:  τ={burn['tau']:.0f} steps  α_min={burn['a_min']:.2f} "
              f"α_∞={burn['a_inf']:.2f}  R²={burn['r2']:.2f}")
    print(f"\n{'arm':9}{'dose':>7}{'α_min':>8}{'τ (steps)':>11}{'α_∞':>7}{'R²':>7}")
    taus = []
    for arm in arms:
        r = rows.get(arm)
        if not r or "tau" not in r:
            am = r.get("a_min", float("nan")) if r else float("nan")
            print(f"{arm:9}{mag_of(arm):>7.2f}{am:>8.2f}{'(no fit)':>11}")
            continue
        # only count arms that actually revived (dipped heavy) for the universality stat
        if r["a_min"] <= 2.0:
            taus.append(r["tau"])
        print(f"{arm:9}{mag_of(arm):>7.2f}{r['a_min']:>8.2f}{r['tau']:>11.0f}{r['a_inf']:>7.2f}{r['r2']:>7.2f}")

    verdict = "n/a (need ≥2 revived arms)"
    if len(taus) >= 2:
        t = np.array(taus)
        cv = float(t.std() / t.mean())
        verdict = (f"τ across revived doses: mean={t.mean():.0f} ± {t.std():.0f} steps (CV={cv:.0%}) → "
                   + ("DOSE-UNIVERSAL (CV<25%): a single intrinsic relaxation time."
                      if cv < 0.25 else "dose-dependent (CV≥25%): τ scales with shock."))
    print(f"\n{verdict}")
    out = EXP / (f"tau_report_{asset}.json" if channel == "kick" else f"tau_report_{asset}_{channel}.json")
    out.write_text(json.dumps(
        {"asset": asset, "channel": channel, "shock": shock, "burnin": burn,
         "arms": rows, "tau_universality": verdict}, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
