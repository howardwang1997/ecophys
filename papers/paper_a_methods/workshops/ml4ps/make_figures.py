"""Build the two figures for the ML4PS workshop paper from committed JSON reports.

  conda run -n ecophys python papers/paper_a_methods/workshops/ml4ps/make_figures.py

Fig 1 (fig1_transient.pdf)     : (left) order-flow tail alpha_ED(t) dip-and-recover (control vs shock)
                                  with the exponential relaxation fit; (right) the sigmoid dose-response.
Fig 2 (fig2_mech_boundary.pdf) : (a) Hill vs warm-up discard; (b) OFI memory burst-and-relax (coherent
                                  shock vs inert price gap); (c) real-crash Delta-alpha vs the calm null.
Sources: experiments/123_driven_transient/{results_spx_*/windowed_hill_report,tau_report_spx,
         r1_warmup_report,ofi_transient_spx,null_test_report}.json
"""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/123_driven_transient"
OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 150, "savefig.bbox": "tight"})
RED, BLUE, GREY = "#d62728", "#1f77b4", "#7f7f7f"
SHOCK = 3000


def _wr(arm):
    p = EXP / f"results_spx_{arm}" / "windowed_hill_report.json"
    d = json.loads(p.read_text())
    return np.array(d["centers"], float), np.array(d["alpha_ED_mean"], float)


def fig1_transient() -> None:
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(7.0, 2.8))

    # left: alpha_ED(t) control vs kick6 + relaxation fit
    c0, a0 = _wr("control"); n0 = min(len(c0), len(a0))
    ck, ak = _wr("kick6"); nk = min(len(ck), len(ak))
    axL.axhspan(2, 4, color="0.9", alpha=0.6, zorder=0)
    axL.plot(c0[:n0], a0[:n0], color=GREY, lw=1.3, label="control (steady)")
    axL.plot(ck[:nk], ak[:nk], color=RED, lw=1.6, label="coherent shock")
    axL.axvline(SHOCK, color="0.5", ls=":", lw=1)
    tau = json.loads((EXP / "tau_report_spx.json").read_text())["arms"].get("kick6")
    if tau and "tau" in tau:
        t = np.linspace(tau["t_min"], tau["t_min"] + 2500, 200)
        fit = tau["a_inf"] - tau["amp"] * np.exp(-(t - tau["t_min"]) / tau["tau"])
        axL.plot(t, fit, color="black", ls="--", lw=1.1, label=f"relax fit ($\\tau\\approx{tau['tau']:.0f}$)")
    axL.set_xlabel("step $t$"); axL.set_ylabel("order-flow tail $\\alpha_{\\mathrm{ED}}(t)$")
    axL.set_title("Driven transient: dip-and-recover", fontsize=9)
    axL.legend(fontsize=6.8, loc="center right")

    # right: dose-response (post-shock min alpha vs dose)
    arms = []
    for p in EXP.glob("results_spx_kick*/windowed_hill_report.json"):
        name = p.parent.name.replace("results_spx_kick", "")
        try:
            dose = float(name)
        except ValueError:
            continue
        c, a = _wr(f"kick{name}"); n = min(len(c), len(a))
        m = (c[:n] >= SHOCK) & (c[:n] < SHOCK + 1500)
        if m.any():
            arms.append((dose, float(np.nanmin(a[:n][m]))))
    arms.sort()
    doses = [d for d, _ in arms]; mins = [m for _, m in arms]
    axR.axhspan(2, 4, color="0.9", alpha=0.6, zorder=0)
    axR.semilogx(doses, mins, marker="o", ms=5, color=RED)
    axR.axhline(4.7, color=GREY, ls=":", lw=1, label="steady state")
    axR.set_xlabel("shock magnitude ($\\sigma$)")
    axR.set_ylabel("post-shock min $\\alpha_{\\mathrm{ED}}$")
    axR.set_title("Sigmoid dose-response (5 assets)", fontsize=9)
    axR.legend(fontsize=7, loc="upper right")
    fig.savefig(OUT / "fig1_transient.pdf")
    plt.close(fig)
    print(f"wrote {OUT/'fig1_transient.pdf'}")


def fig2_mech_boundary() -> None:
    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(7.2, 2.5))

    # (a) Hill vs warm-up
    rpt = json.loads((EXP / "r1_warmup_report.json").read_text())
    axA.axhspan(rpt["band"][0], rpt["band"][1], color="0.9", alpha=0.6, zorder=0)
    for cell in rpt["rows"]:
        k = "concave" if "concave" in cell["cell"] else "baseline"
        col = RED if k == "concave" else BLUE
        hbd = cell["hill_by_drop"]; ds = sorted(int(x) for x in hbd)
        axA.errorbar(ds, [hbd[str(d)]["mean"] for d in ds], yerr=[hbd[str(d)]["std"] for d in ds],
                     marker="o", ms=3, capsize=2, color=col, label=k)
    axA.set_xlabel("warm-up discard"); axA.set_ylabel("Hill $\\alpha$")
    axA.set_title("(a) measurement pitfall", fontsize=8.5)
    axA.legend(fontsize=6.5)

    # (b) OFI memory burst-and-relax
    ofi = json.loads((EXP / "ofi_transient_spx.json").read_text())["arms"]
    for arm, col, lbl in [("kick6", RED, "coherent shock"), ("jump6", BLUE, "price gap"),
                          ("control", GREY, "control")]:
        m = ofi[arm]["measures"]["mem"]
        axB.plot([0, 1, 2], [m["base"], m["shock"], m["rec"]], marker="o", ms=4, color=col,
                 lw=2 if arm == "kick6" else 1.2, label=lbl)
    axB.set_xticks([0, 1, 2]); axB.set_xticklabels(["pre", "shock", "post"])
    axB.axhline(0, color="0.8", lw=0.8); axB.set_ylabel("OFI memory")
    axB.set_title("(b) order-flow signature", fontsize=8.5)
    axB.legend(fontsize=6.3, loc="center left")

    # (c) real-crash null test
    nt = json.loads((EXP / "null_test_report.json").read_text())
    null, eps = nt["null"], nt["episodes"]
    xx = range(len(eps))
    axC.axhspan(null["mean"] - null["std"], null["mean"] + null["std"], color="0.9", alpha=0.7,
                zorder=0, label="calm null")
    axC.axhline(null["q05"], color=RED, ls="--", lw=1, label="transient $\\Rightarrow\\downarrow$")
    axC.axhline(0, color="0.7", lw=0.8)
    axC.scatter(list(xx), [e["dalpha"] for e in eps], color=BLUE, zorder=3, s=28)
    axC.set_xticks(list(xx))
    axC.set_xticklabels([e["episode"].split("_")[0] for e in eps], rotation=35, ha="right", fontsize=6.3)
    axC.set_ylabel("$\\Delta\\alpha$")
    axC.set_title(f"(c) real: stationary (z={nt['pooled_z']:+.2f})", fontsize=8.5)
    axC.legend(fontsize=6.0, loc="lower left")
    fig.savefig(OUT / "fig2_mech_boundary.pdf")
    plt.close(fig)
    print(f"wrote {OUT/'fig2_mech_boundary.pdf'}")


if __name__ == "__main__":
    fig1_transient()
    fig2_mech_boundary()
