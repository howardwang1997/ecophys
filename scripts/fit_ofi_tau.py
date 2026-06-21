"""exp 124 E-S4 — relaxation timescale τ_OFI of the order-flow-memory transient.

After a coherent shock the windowed OFI lag-1 memory bursts toward ~1 and then decays back to baseline.
We fit the decay limb, m(t) = m_inf + amp·exp(-(t - t_peak)/τ_OFI), and report τ_OFI per arm/asset,
comparing it to the return-tail relaxation time (tau_report_spx.json, τ_ED≈240).

Reads the committed OFI rollouts (npz with ofi). Run where the npz live (the H20 box).

  conda run -n ecophys python scripts/fit_ofi_tau.py --exp experiments/123_driven_transient \
      --assets spx ndx gold btcusdt --arm kick6 --shock 3000
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit


def windowed_mem(ofi: np.ndarray, W: int, stride: int):
    c, mem = [], []
    i = 0
    while i + W <= ofi.size:
        s = ofi[i:i + W]
        s = s[np.isfinite(s)]
        c.append(i + W // 2)
        mem.append(float(np.corrcoef(s[:-1], s[1:])[0, 1]) if s.size > 8 and s.std() > 1e-9 else np.nan)
        i += stride
    return np.array(c), np.array(mem)


def arm_mem(exp: Path, asset: str, arm: str, W: int, stride: int):
    files = [f for f in sorted(exp.glob(f"results_{asset}_{arm}/**/trajectory_*.npz"))
             if "ofi" in np.load(f)]
    if not files:
        return None, None
    centers, stack = None, []
    for f in files:
        c, m = windowed_mem(np.asarray(np.load(f)["ofi"], float), W, stride)
        centers = c
        stack.append(m)
    n = min(len(centers), *(len(x) for x in stack))
    return centers[:n], np.nanmean(np.array([x[:n] for x in stack]), axis=0)


def fit_tau(c, m, shock):
    seek = (c >= shock) & (c < shock + 1500)
    if not seek.any():
        return None
    i_pk = np.where(seek)[0][int(np.nanargmax(m[seek]))]
    t_pk, m_pk = c[i_pk], m[i_pk]
    sel = (c >= t_pk) & np.isfinite(m)
    if sel.sum() < 4:
        return None
    tt, mm = c[sel] - t_pk, m[sel]

    def f(t, m_inf, amp, tau):
        return m_inf + amp * np.exp(-t / tau)
    try:
        popt, _ = curve_fit(f, tt, mm, p0=[0.0, max(m_pk, 0.3), 300.0],
                            bounds=([-0.5, 0.0, 20.0], [1.0, 1.5, 6000.0]), maxfev=20000)
        ss = 1.0 - np.sum((mm - f(tt, *popt)) ** 2) / max(np.sum((mm - mm.mean()) ** 2), 1e-9)
        return {"t_peak": float(t_pk), "m_peak": float(m_pk), "m_inf": float(popt[0]),
                "amp": float(popt[1]), "tau_ofi": float(popt[2]), "r2": float(ss)}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e), "m_peak": float(m_pk)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exp", default="experiments/123_driven_transient")
    ap.add_argument("--assets", nargs="+", default=["spx", "ndx", "gold", "btcusdt"])
    ap.add_argument("--arm", default="kick6")
    ap.add_argument("--shock", type=int, default=3000)
    ap.add_argument("--window", type=int, default=500)
    ap.add_argument("--stride", type=int, default=100)
    args = ap.parse_args()
    exp = Path(args.exp)

    tau_ed = None
    tp = exp / "tau_report_spx.json"
    if tp.exists():
        tau_ed = json.loads(tp.read_text())["arms"].get("kick6", {}).get("tau")

    print(f"=== exp 124 E-S4 — OFI-memory relaxation τ_OFI (arm={args.arm}, shock@{args.shock}) ===")
    if tau_ed:
        print(f"  (return-tail τ_ED ≈ {tau_ed:.0f} for reference)")
    print(f"{'asset':9}{'m_peak':>8}{'τ_OFI':>9}{'m_inf':>8}{'R²':>7}")
    rows = {}
    for a in args.assets:
        c, m = arm_mem(exp, a, args.arm, args.window, args.stride)
        if c is None:
            print(f"{a:9}{'(no npz)':>8}"); continue
        r = fit_tau(c, m, args.shock)
        rows[a] = r
        if r and "tau_ofi" in r:
            print(f"{a:9}{r['m_peak']:>8.2f}{r['tau_ofi']:>9.0f}{r['m_inf']:>8.2f}{r['r2']:>7.2f}")
        else:
            print(f"{a:9}{(r or {}).get('m_peak',float('nan')):>8.2f}{'(no fit)':>9}")
    taus = [r["tau_ofi"] for r in rows.values() if r and "tau_ofi" in r]
    summary = (f"τ_OFI across assets: mean={np.mean(taus):.0f} ± {np.std(taus):.0f} steps (n={len(taus)})"
               if taus else "no fits")
    if taus and tau_ed:
        summary += f"; vs return-tail τ_ED≈{tau_ed:.0f}"
    print(f"\n{summary}")
    out = exp / "ofi_tau_report.json"
    out.write_text(json.dumps({"arm": args.arm, "shock": args.shock, "tau_ed_ref": tau_ed,
                               "assets": rows, "summary": summary}, indent=2, default=float))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
