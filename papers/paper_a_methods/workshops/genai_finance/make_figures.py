"""Build the two figures for the GenAI-in-Finance workshop paper from the committed JSON reports.

  conda run -n ecophys python papers/paper_a_methods/workshops/genai_finance/make_figures.py

Fig 1 (fig1_pitfall.pdf)         : Hill tail index vs warm-up discard length (the evaluation pitfall).
Fig 2 (fig2_control_fidelity.pdf): (left) OFI memory burst-and-relax under coherent liquidation vs
                                    inert price-gap; (right) real-crash Δα vs the calm null.
Sources: experiments/123_driven_transient/{r1_warmup_report,ofi_transient_spx,null_test_report}.json
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/123_driven_transient"
OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 150, "savefig.bbox": "tight"})
C = {"baseline": "#1f77b4", "concave": "#d62728", "kick6": "#d62728",
     "jump6": "#1f77b4", "control": "#7f7f7f"}


def fig1_pitfall() -> None:
    rpt = json.loads((EXP / "r1_warmup_report.json").read_text())
    cells = rpt["rows"]
    band = rpt.get("band", [2.0, 4.0])
    fig, ax = plt.subplots(figsize=(4.0, 2.9))
    # cube-law "in-band" zone (the target a fat-tail scorer is matching)
    ax.axhspan(band[0], band[1], color="0.85", alpha=0.6, zorder=0)
    ax.text(150, (band[0] + band[1]) / 2, "cube-law\n\"in-band\"", color="0.4",
            fontsize=7, ha="center", va="center")
    for cell in cells:
        name = cell["cell"]
        key = "concave" if "concave" in name else "baseline"
        hbd = cell["hill_by_drop"]
        drops = sorted(int(k) for k in hbd)
        mean = [hbd[str(d)]["mean"] for d in drops]
        std = [hbd[str(d)]["std"] for d in drops]
        lbl = "concave (tuned to \"solve\")" if key == "concave" else "baseline"
        ax.errorbar(drops, mean, yerr=std, marker="o", ms=4, capsize=2, color=C[key], label=lbl)
    ax.annotate("scored on full rollout\n(inflated match)", xy=(0, 4.0), xytext=(40, 2.2),
                fontsize=7, ha="left", arrowprops=dict(arrowstyle="->", color="0.3"))
    ax.annotate("steady state\n(light-tailed)", xy=(200, 8.0), xytext=(95, 8.4),
                fontsize=7, ha="left", arrowprops=dict(arrowstyle="->", color="0.3"))
    ax.set_xlabel("warm-up discard length (steps)")
    ax.set_ylabel("Hill tail index  $\\alpha$  (higher = lighter)")
    ax.set_title("The evaluation pitfall: warm-up inflates tail fidelity", fontsize=9)
    ax.legend(fontsize=7, loc="center right")
    fig.savefig(OUT / "fig1_pitfall.pdf"); fig.savefig(OUT / "fig1_pitfall.png", dpi=150)
    plt.close(fig)
    print(f"wrote {OUT/'fig1_pitfall.pdf'}")


def fig2_control_fidelity() -> None:
    ofi = json.loads((EXP / "ofi_transient_spx.json").read_text())["arms"]
    nt = json.loads((EXP / "null_test_report.json").read_text())
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(7.0, 2.9))

    # left: OFI memory burst-and-relax (pre / at-shock / post)
    x = [0, 1, 2]
    for arm in ("kick6", "jump6", "control"):
        m = ofi[arm]["measures"]["mem"]
        y = [m["base"], m["shock"], m["rec"]]
        lbl = {"kick6": "coherent liquidation", "jump6": "exogenous price gap",
               "control": "no shock"}[arm]
        axL.plot(x, y, marker="o", ms=5, color=C[arm], label=lbl,
                 lw=2 if arm == "kick6" else 1.3)
    axL.set_xticks(x); axL.set_xticklabels(["pre", "at shock", "post"])
    axL.set_ylabel("order-flow imbalance memory\n(lag-1 autocorr.)")
    axL.set_title("Controllability: OFI burst-and-relax", fontsize=9)
    axL.axhline(0, color="0.8", lw=0.8, zorder=0)
    axL.legend(fontsize=7, loc="center left")

    # right: real-crash Δα vs the calm null
    null = nt["null"]
    eps = nt["episodes"]
    names = [e["episode"].split("_")[0] for e in eps]
    da = [e["dalpha"] for e in eps]
    xx = range(len(eps))
    axR.axhspan(null["mean"] - null["std"], null["mean"] + null["std"], color="0.85",
                alpha=0.7, zorder=0, label="calm null (±1σ)")
    axR.axhline(null["q05"], color="#d62728", ls="--", lw=1,
                label="transient predicts ↓ (Δα≤q05)")
    axR.axhline(0, color="0.7", lw=0.8)
    axR.scatter(xx, da, color="#1f77b4", zorder=3, s=36)
    for i, e in enumerate(eps):
        axR.annotate(f"{e['dalpha']:+.2f}", (i, e["dalpha"]), fontsize=6.5,
                     xytext=(0, 6), textcoords="offset points", ha="center")
    axR.set_xticks(list(xx)); axR.set_xticklabels(names, rotation=30, ha="right", fontsize=7)
    axR.set_ylabel("$\\Delta\\alpha$  (crash $-$ pre)")
    axR.set_title(f"Fidelity: real tails stationary (pooled z={nt['pooled_z']:+.2f})", fontsize=9)
    axR.legend(fontsize=6.5, loc="upper left")
    fig.savefig(OUT / "fig2_control_fidelity.pdf"); fig.savefig(OUT / "fig2_control_fidelity.png", dpi=150)
    plt.close(fig)
    print(f"wrote {OUT/'fig2_control_fidelity.pdf'}")


if __name__ == "__main__":
    fig1_pitfall()
    fig2_control_fidelity()
