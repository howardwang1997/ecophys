"""Shared figure library for Paper A (NCS) + the two workshop spines (ml4ps, genai_finance).

Three papers run in lockstep off ONE figure set so panels, numbers and styling stay consistent.
This module writes every panel to papers/paper_a_methods/shared/figures/, then distribute.py
copies the per-paper subsets into each paper's figures/ dir.

  conda run -n ecophys python papers/paper_a_methods/shared/make_figures.py

All data are committed JSON reports under experiments/123_driven_transient/. No re-training.

Figures
  fig_hero          : EcoMD as a controlled-experiment platform (schematic, no data)
  fig_transient     : (a) alpha_ED(t) dip-and-recover  (b) dose-response (SPX sweep + 4 assets)
                      (c) relaxation time tau vs dose  -- tau is dose-dependent, not a constant
  fig_correction    : Hill index vs warm-up discard (the measurement pitfall), annotated  [+ Table 1]
  fig_mechanism     : (a) OFI memory burst-and-relax (reconstructed from the fit)  (b) OFI dose-response
                      (c) two timescales: OFI vs tail relaxation  (d) entropy-production proxy is flat
  fig_boundary      : real-crash Delta-alpha vs the calm null, all five episodes
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments/123_driven_transient"
OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 9.5, "figure.dpi": 150, "savefig.bbox": "tight",
    "savefig.dpi": 200, "legend.frameon": False,
})
RED, BLUE, GREY, GREEN, PURPLE = "#d62728", "#1f77b4", "#7f7f7f", "#2ca02c", "#7e3f9e"
BAND = "0.90"
SHOCK = 3000
ASSET_LABEL = {"spx": "S&P 500", "ndx": "NASDAQ", "gold": "gold", "btcusdt": "BTC", "eurusd": "EUR/USD"}
ASSET_COLOR = {"spx": RED, "ndx": "#e377c2", "gold": "#bcbd22", "btcusdt": "#ff7f0e", "eurusd": BLUE}


def _load(p):
    return json.loads((EXP / p).read_text())


def _wr(asset, arm):
    """windowed alpha_ED(t): centers, mean."""
    d = _load(f"results_{asset}_{arm}/windowed_hill_report.json")
    return np.asarray(d["centers"], float), np.asarray(d["alpha_ED_mean"], float)


def _saveboth(fig, name):
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=200)
    plt.close(fig)
    print(f"  wrote {name}.png / .pdf")


# ──────────────────────────────────────────────────────────────────────────
# FIG HERO — EcoMD as a controlled-experiment platform (schematic)
# ──────────────────────────────────────────────────────────────────────────
def fig_hero():
    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(11.4, 3.2),
                                        gridspec_kw={"width_ratios": [1.05, 1.25, 1.0]})
    fig.subplots_adjust(wspace=0.22, top=0.86, bottom=0.04, left=0.02, right=0.98)
    for ax in (axA, axB, axC):
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    def box(ax, x, y, w, h, text, fc, ec="0.3", fs=8.0, lw=1.2):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.03",
                                    fc=fc, ec=ec, lw=lw, zorder=2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, zorder=3)

    def arrow(ax, x0, y0, x1, y1, lw=1.6, color="0.25"):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=12,
                                     lw=lw, color=color, zorder=1))

    # ---- Panel A: the model (particles -> force -> excess demand -> price) ----
    axA.set_title("a   Particle market model", loc="left", fontsize=9, fontweight="bold", pad=6)
    rng = np.random.default_rng(7)
    pts = rng.uniform(0.12, 0.62, size=(9, 2))
    pts[:, 1] = pts[:, 1] * 0.42 + 0.50  # cluster in upper-left region
    # k-NN edges
    for i in range(len(pts)):
        d = np.hypot(*(pts - pts[i]).T); order = np.argsort(d)[1:3]
        for j in order:
            axA.plot([pts[i, 0], pts[j, 0]], [pts[i, 1], pts[j, 1]], color="0.7", lw=0.7, zorder=1)
    for (x, y) in pts:
        axA.add_patch(Circle((x, y), 0.028, fc=PURPLE, ec="white", lw=0.6, zorder=3))
    axA.text(0.37, 0.95, r"$N$ agents $s_i\in\mathbb{R}^d$", ha="center", fontsize=7.8)
    axA.text(0.37, 0.46, r"learned force $-\nabla U(\{s\};c_t)$", ha="center", fontsize=7.2, color=PURPLE)
    box(axA, 0.62, 0.62, 0.34, 0.16, r"excess demand" + "\n" + r"$\mathrm{ED}_t=\kappa\sum_i\Delta s_{i,0}$", "#eef0ff", fs=7.3)
    box(axA, 0.62, 0.30, 0.34, 0.14, r"log-price $p_t$", "#eafbe9", fs=8.0)
    arrow(axA, 0.50, 0.62, 0.62, 0.70)         # particles -> ED
    arrow(axA, 0.79, 0.62, 0.79, 0.44)         # ED -> price
    axA.text(0.04, 0.10, "overdamped Langevin + MACE-lite force;\nfully differentiable",
             fontsize=6.8, color="0.35")

    # ---- Panel B: the controlled experiment (steady -> shock -> relax) + 3 readouts ----
    axB.set_title("b   Controlled intervention", loc="left", fontsize=9, fontweight="bold", pad=6)
    t = np.linspace(0, 1, 400)
    ts = 0.42  # shock location in axis units
    base = 0.78 + 0.012 * np.sin(2 * np.pi * 6 * t)
    dip = np.where(t < ts, base, 0.78 - 0.46 * np.exp(-(t - ts) / 0.12) * (t >= ts))
    dip = np.where(t < ts, base, 0.32 + 0.46 * (1 - np.exp(-(t - ts) / 0.16)))
    axB.plot(t, dip, color=RED, lw=2.0, zorder=3)
    axB.axvline(ts, color="0.4", ls=":", lw=1.1)
    arrow(axB, ts, 0.96, ts, 0.80, lw=1.4, color=RED)
    axB.text(ts, 0.99, "scheduled shock $t^*$", ha="center", fontsize=7.4, color=RED)
    axB.text(0.18, 0.86, "steady state", fontsize=7.2, color="0.3")
    axB.text(0.74, 0.50, "relaxation", fontsize=7.2, color="0.3", rotation=12)
    axB.annotate("", xy=(0.985, 0.30), xytext=(0.02, 0.30),
                 arrowprops=dict(arrowstyle="-|>", color="0.5", lw=1.0))
    axB.text(0.5, 0.235, "time", ha="center", fontsize=7.2, color="0.4")
    # 3 readouts
    for i, (lab, col) in enumerate([(r"tail index $\alpha_{\mathrm{ED}}$", RED),
                                    ("order-flow memory", GREEN),
                                    ("price / return", "#444")]):
        box(axB, 0.04 + i * 0.33, 0.04, 0.30, 0.14, lab, "white", ec=col, fs=6.9, lw=1.3)
    axB.text(0.5, 0.205, "exact internal observables (read, not inferred)", ha="center",
             fontsize=6.6, color="0.45")

    # ---- Panel C: the four findings / logic chain ----
    axC.set_title("c   Four controlled results", loc="left", fontsize=9, fontweight="bold", pad=6)
    items = [
        ("1  Measurement correction", "warm-up inflates the tail", "#fff3e0"),
        ("2  Driven transient", "heavy tail only out of equilibrium", "#ffebee"),
        ("3  Mechanism + OFI signature", "coordinated flow, not price shocks", "#e8f5e9"),
        ("4  Real-market boundary", "returns stationary " + r"$\Rightarrow$" + " OF prediction", "#e3f2fd"),
    ]
    y = 0.80
    for title, sub, fc in items:
        box(axC, 0.02, y, 0.96, 0.165, "", fc, fs=8)
        axC.text(0.06, y + 0.105, title, fontsize=7.8, fontweight="bold", va="center")
        axC.text(0.06, y + 0.04, sub, fontsize=6.8, color="0.35", va="center")
        y -= 0.205
    _saveboth(fig, "fig_hero")


# ──────────────────────────────────────────────────────────────────────────
# FIG TRANSIENT — dip-and-recover, dose-response, tau(dose)
# ──────────────────────────────────────────────────────────────────────────
def fig_transient():
    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(10.5, 3.0))
    tau = _load("tau_report_spx.json")

    # (a) alpha_ED(t)
    c0, a0 = _wr("spx", "control")
    ck, ak = _wr("spx", "kick6")
    axA.axhspan(2, 4, color=BAND, zorder=0)
    axA.text(7400, 3.0, "cube-law\nband", fontsize=6.6, color="0.5", ha="right", va="center")
    axA.plot(c0, a0, color=GREY, lw=1.2, label="control (steady)")
    axA.plot(ck, ak, color=RED, lw=1.7, label="coherent shock")
    axA.axvline(SHOCK, color="0.5", ls=":", lw=1)
    f = tau["arms"]["kick6"]
    tt = np.linspace(f["t_min"], f["t_min"] + 1600, 200)
    axA.plot(tt, f["a_inf"] - f["amp"] * np.exp(-(tt - f["t_min"]) / f["tau"]),
             color="black", ls="--", lw=1.1, label=fr"relax fit ($\tau\approx{f['tau']:.0f}$)")
    # burn-in marker
    axA.annotate("burn-in dip\n(same depth, fast)", xy=(250, 0.66), xytext=(900, 1.7),
                 fontsize=6.4, color="0.35", arrowprops=dict(arrowstyle="-|>", color="0.5", lw=0.8))
    axA.set_xlabel("step $t$"); axA.set_ylabel(r"order-flow tail $\alpha_{\mathrm{ED}}(t)$")
    axA.set_title("a  Driven transient: dip-and-recover")
    axA.legend(fontsize=6.6, loc="lower right")
    axA.set_ylim(0, 6)

    # (b) dose-response per asset: a connected sweep where >=4 doses exist, else markers.
    # Auto-upgrades to five curves once the ndx/gold/btc/eurusd full sweeps land (exp 123 dose-sweep).
    def post_min(asset, arm):
        c, a = _wr(asset, arm)
        m = (c >= SHOCK) & (c < SHOCK + 1500)
        return float(np.nanmin(a[m])) if m.any() else np.nan
    axB.axhspan(2, 4, color=BAND, zorder=0)
    for asset in ["spx", "ndx", "gold", "btcusdt", "eurusd"]:
        pts = []
        for p in sorted(EXP.glob(f"results_{asset}_kick*/windowed_hill_report.json")):
            name = p.parent.name.replace(f"results_{asset}_kick", "")
            try:
                dose = float(name)
            except ValueError:
                continue
            pts.append((dose, post_min(asset, f"kick{name}")))
        if not pts:
            continue
        pts.sort()
        xs = [d for d, _ in pts]; ys = [m for _, m in pts]
        if len(pts) >= 4:
            axB.semilogx(xs, ys, "-o", ms=4.5, color=ASSET_COLOR[asset], label=ASSET_LABEL[asset])
        else:
            axB.semilogx(xs, ys, "D", ms=5, color=ASSET_COLOR[asset], label=ASSET_LABEL[asset])
    axB.axhline(4.7, color=GREY, ls=":", lw=1)
    axB.text(0.06, 4.85, "steady state", fontsize=6.6, color="0.5")
    axB.set_xlabel(r"shock magnitude ($\sigma$)")
    axB.set_ylabel(r"post-shock min $\alpha_{\mathrm{ED}}$")
    axB.set_title("b  Dose-response (5 assets)")
    axB.legend(fontsize=6.2, loc="upper right")
    axB.set_ylim(0, 5.4)

    # (c) tau vs dose  -- tau is dose-dependent (the real result)
    doses, taus = [], []
    for arm, v in tau["arms"].items():
        try:
            d = float(arm.replace("kick", ""))
        except ValueError:
            continue
        if "tau" in v:
            doses.append(d); taus.append(v["tau"])
    order = np.argsort(doses)
    doses = np.array(doses)[order]; taus = np.array(taus)[order]
    onset = 0.1
    sub = doses < onset
    axC.axhspan(0, 20, color=BAND, zorder=0)
    axC.text(9, 11.5, "fit-resolution floor", fontsize=6.2, color="0.5", ha="right")
    axC.axvspan(doses.min() * 0.8, onset, color="#fdecea", zorder=0)
    axC.semilogx(doses[~sub], taus[~sub], "-o", ms=5, color=PURPLE, zorder=3)
    axC.semilogx(doses[sub], taus[sub], "o", ms=5, mfc="white", mec=PURPLE, zorder=3)
    axC.text(0.052, 360, "sub-onset\n(unresolved)", fontsize=5.8, color="#c0392b", ha="left", va="top")
    axC.axhline(tau["arms"]["kick6"]["tau"], color="0.6", ls="--", lw=0.9)
    axC.text(1.1, 250, r"saturated $\tau\approx236$", fontsize=6.6, color="0.4")
    axC.set_xlabel(r"shock magnitude ($\sigma$)")
    axC.set_ylabel(r"relaxation time $\tau$ (steps)")
    axC.set_title(r"c  $\tau$ is dose-dependent (CV$=71\%$)")
    axC.set_ylim(0, 430)
    _saveboth(fig, "fig_transient")


# ──────────────────────────────────────────────────────────────────────────
# FIG CORRECTION — Hill vs warm-up discard (annotated)
# ──────────────────────────────────────────────────────────────────────────
def fig_correction():
    fig, ax = plt.subplots(figsize=(4.7, 3.6))
    r = _load("r1_warmup_report.json")
    ax.axhspan(r["band"][0], r["band"][1], color=BAND, zorder=0)
    ax.text(195, 3.0, 'cube-law "in-band"', fontsize=7, color="0.5", ha="right")
    for cell in r["rows"]:
        is_con = "concave" in cell["cell"]
        col = RED if is_con else BLUE
        lab = 'concave (tuned to "solve")' if is_con else "baseline"
        hbd = cell["hill_by_drop"]; ds = sorted(int(x) for x in hbd)
        ax.errorbar(ds, [hbd[str(d)]["mean"] for d in ds], yerr=[hbd[str(d)]["std"] for d in ds],
                    marker="o", ms=4, capsize=2.5, lw=1.6, color=col, label=lab)
    ax.annotate("scored on full rollout\n(inflated cube-law match)", xy=(0, 3.87), xytext=(33, 2.4),
                fontsize=6.8, arrowprops=dict(arrowstyle="-|>", color="0.45", lw=0.9))
    ax.annotate("true steady state\n(light-tailed)", xy=(200, 9.26), xytext=(95, 8.0),
                fontsize=6.8, arrowprops=dict(arrowstyle="-|>", color="0.45", lw=0.9))
    ax.set_xlabel("warm-up discard length (steps)")
    ax.set_ylabel(r"Hill tail index $\alpha$  (higher = lighter)")
    ax.set_title("The warm-up scoring pitfall")
    ax.legend(fontsize=7.2, loc="center right")
    ax.set_ylim(2, 10.2)
    _saveboth(fig, "fig_correction")


# ──────────────────────────────────────────────────────────────────────────
# FIG MECHANISM — OFI burst-relax, OFI dose-response, two timescales, entropy flat
# ──────────────────────────────────────────────────────────────────────────
def fig_mechanism():
    fig, ((axA, axB), (axC, axD)) = plt.subplots(2, 2, figsize=(8.4, 6.0))
    fig.subplots_adjust(wspace=0.30, hspace=0.42)
    oft = _load("ofi_tau_report.json")
    sp = oft["assets"]["spx"]

    # (a) OFI memory burst-and-relax (reconstructed from the exponential fit)
    post = np.linspace(sp["t_peak"], sp["t_peak"] + 200, 160)
    mem_post = sp["m_inf"] + sp["amp"] * np.exp(-(post - sp["t_peak"]) / sp["tau_ofi"])
    axA.axhline(0, color="0.8", lw=0.8)
    axA.plot([-400, 0], [sp["m_inf"], sp["m_inf"]], color=RED, lw=2)
    axA.plot([0, sp["t_peak"] - SHOCK], [sp["m_inf"], sp["m_peak"]], color=RED, lw=2)
    axA.plot(post - SHOCK, mem_post, color=RED, lw=2, label="coherent shock")
    oti = _load("ofi_transient_spx.json")["arms"]
    for arm, col, lab in [("jump6", BLUE, "price gap (inert)"), ("control", GREY, "control")]:
        b = oti[arm]["measures"]["mem"]["base"]
        axA.plot([-400, 450], [b, b], color=col, lw=1.3, label=lab)
    axA.axvline(0, color="0.5", ls=":", lw=1)
    axA.annotate(fr"sharp relax $\tau_{{\mathrm{{OFI}}}}\approx{sp['tau_ofi']:.0f}$",
                 xy=(sp["t_peak"] - SHOCK + 40, 0.5), xytext=(150, 0.72), fontsize=7,
                 color=RED, arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.8))
    axA.set_xlabel("step relative to shock"); axA.set_ylabel("OFI memory (lag-1 autocorr.)")
    axA.set_title("a  Order-flow memory burst")
    axA.legend(fontsize=6.6, loc="upper left"); axA.set_ylim(-0.2, 1.12); axA.set_xlim(-400, 450)

    # (b) OFI memory dose-response (SPX) — the sigmoid
    arms = _load("ofi_transient_spx.json")["arms"]
    dr = sorted((float(a.replace("kick", "")), v["measures"]["mem"]["shock"])
                for a, v in arms.items() if a.startswith("kick"))
    axB.semilogx([d for d, _ in dr], [m for _, m in dr], "-o", ms=5, color=GREEN)
    axB.axhline(1.0, color="0.6", ls=":", lw=0.9)
    axB.text(0.06, 0.92, "perfect persistence", fontsize=6.6, color="0.5")
    axB.set_xlabel(r"shock magnitude ($\sigma$)"); axB.set_ylabel("peak OFI memory")
    axB.set_title("b  OFI dose-response (sigmoid)"); axB.set_ylim(-0.1, 1.12)

    # (c) two timescales: OFI vs tail relaxation (normalized recovery)
    tau = _load("tau_report_spx.json")["arms"]["kick6"]
    x = np.linspace(0, 600, 300)
    axC.plot(x, 1 - np.exp(-x / sp["tau_ofi"]), color=GREEN, lw=2,
             label=fr"OFI memory ($\tau\approx{sp['tau_ofi']:.0f}$)")
    axC.plot(x, 1 - np.exp(-x / tau["tau"]), color=RED, lw=2,
             label=fr"tail $\alpha_{{\mathrm{{ED}}}}$ ($\tau\approx{tau['tau']:.0f}$)")
    axC.axhline(1 - 1 / np.e, color="0.7", ls=":", lw=0.8)
    axC.set_xlabel("steps after shock"); axC.set_ylabel("fraction relaxed")
    axC.set_title("c  Two timescales ($\\sim$10$\\times$ apart)")
    axC.legend(fontsize=7, loc="lower right")

    # (d) entropy-production proxy is flat (per asset, kick6)
    assets = ["spx", "ndx", "gold", "btcusdt", "eurusd"]
    labs, base_v, shock_v = [], [], []
    for a in assets:
        try:
            e = _load(f"ofi_entropy_{a}.json")["arms"]["kick6"]
        except (FileNotFoundError, KeyError):
            continue
        labs.append(ASSET_LABEL[a]); base_v.append(e["base"]); shock_v.append(e["shock"])
    xx = np.arange(len(labs)); w = 0.36
    axD.bar(xx - w / 2, base_v, w, color="0.7", label="pre-shock")
    axD.bar(xx + w / 2, shock_v, w, color=RED, label="at shock")
    axD.set_xticks(xx); axD.set_xticklabels(labs, rotation=30, ha="right", fontsize=7)
    axD.set_ylabel(r"entropy-production proxy $\dot S$")
    axD.set_title(r"d  Irreversibility stays flat")
    axD.legend(fontsize=6.8, loc="upper right"); axD.set_ylim(0, max(shock_v) * 1.7)
    _saveboth(fig, "fig_mechanism")


# ──────────────────────────────────────────────────────────────────────────
# FIG BOUNDARY — real-crash null test, all five episodes
# ──────────────────────────────────────────────────────────────────────────
def fig_boundary():
    fig, ax = plt.subplots(figsize=(5.0, 3.4))
    nt = _load("null_test_report.json")
    null, eps = nt["null"], nt["episodes"]
    xx = np.arange(len(eps))
    ax.axhspan(null["mean"] - null["std"], null["mean"] + null["std"], color=BAND, zorder=0,
               label=r"calm null ($\pm1\sigma$)")
    ax.axhline(null["q05"], color=RED, ls="--", lw=1.1, label=r"transient predicts $\Delta\alpha \leq q_{05}$")
    ax.axhline(0, color="0.7", lw=0.8)
    vals = [e["dalpha"] for e in eps]
    ax.scatter(xx, vals, color=BLUE, zorder=3, s=44)
    for x, v in zip(xx, vals):
        ax.annotate(f"{v:+.2f}", (x, v), textcoords="offset points",
                    xytext=(0, 8 if v >= 0 else -13), ha="center", fontsize=6.6, color="0.3")
    ax.set_xticks(xx)
    ax.set_xticklabels([e["episode"].split("_")[0] for e in eps], rotation=30, ha="right", fontsize=7.4)
    ax.set_ylabel(r"$\Delta\alpha$  (crash $-$ pre)")
    ax.set_title(f"Real return tails are stationary  (pooled $z={nt['pooled_z']:+.2f}$)")
    ax.legend(fontsize=6.8, loc="lower left")
    ax.set_ylim(-1.15, 1.35)
    _saveboth(fig, "fig_boundary")


def main():
    print("Building shared Paper A figures…")
    fig_hero()
    fig_transient()
    fig_correction()
    fig_mechanism()
    fig_boundary()
    print("done.")


if __name__ == "__main__":
    main()
