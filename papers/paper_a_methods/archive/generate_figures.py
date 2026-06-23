"""Generate Paper A figures from existing experimental data.

Outputs to papers/paper_a_methods/figures/:
  fig1_force_probe.pdf       — |F|/σ ratio across architectures (refresh w/ v3)
  fig2_acf_shape.pdf         — ACF(r²) lag-curve comparison
  fig3_scoreboard_matrix.pdf — facts × architectures heatmap
  fig4_loss_curves.pdf       — D-series Goodhart evidence
  fig5_d_overfit_trace.pdf   — single example of training loss falling
                                while facts diverge
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[2]
FIG_DIR = Path(__file__).resolve().parent / "figures"
FIG_DIR.mkdir(exist_ok=True)


def load_inference(p: Path) -> dict | None:
    if not p.exists():
        return None
    return json.loads(p.read_text())


# ─── Fig 3 — scoreboard matrix ──────────────────────────────────────────
def fig3_scoreboard():
    """11 facts × N architectures heatmap of pass/fail."""
    bands = {
        "autocorr_returns":           (-0.1, 0.20),
        "hill_tail_index":            (2.0, 4.0),
        "gain_loss_asymmetry":        (-30.0, -3.0),
        "aggregational_gaussianity":  (10, 200),
        "intermittency_fano":         (5, 100),
        "acf_squared_returns":        (0.15, 0.55),
        "conditional_kurtosis":       (-1.0, 3.0),
        "dfa_hurst_abs_r":            (0.6, 0.9),
        "leverage_effect":            (-6.0, -0.5),
        "volume_volatility_corr":     (0.3, 0.8),
        "zumbach_asymmetry":          (0.001, 0.5),
    }
    cols = [
        ("A0\n baseline\n SPX", "experiments/022_h20_batch/results_a0/inference_merged.json"),
        ("A4\n +twopop", "experiments/022_h20_batch/results_a4/inference_merged.json"),
        ("B3\n +regime", "experiments/022_h20_batch/results_b3/inference_merged.json"),
        ("C0\n +exploss", "experiments/022_h20_batch/results_c0/inference_merged.json"),
        ("C2\n +mshawkes\n+exploss", "experiments/022_h20_batch/results_c2/inference_merged.json"),
        ("**C4** ★\nfull v3", "experiments/022_h20_batch/results_c4/inference_merged.json"),
        ("D4\n long-train", "experiments/022_h20_batch/results_d4/inference_merged.json"),
    ]
    fact_keys = list(bands.keys())
    n_arch = len(cols)
    mat = np.full((len(fact_keys), n_arch), np.nan)
    pass_mat = np.zeros((len(fact_keys), n_arch), dtype=int)
    for j, (lbl, p) in enumerate(cols):
        d = load_inference(REPO / p)
        if d is None:
            continue
        for i, k in enumerate(fact_keys):
            if k in d["aggregated"]:
                v = d["aggregated"][k]["mean"]
                mat[i, j] = v
                lo, hi = bands[k]
                pass_mat[i, j] = 1 if lo <= v <= hi else 0

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(pass_mat, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(n_arch))
    ax.set_xticklabels([c[0] for c in cols], fontsize=8)
    ax.set_yticks(np.arange(len(fact_keys)))
    ax.set_yticklabels(fact_keys, fontsize=8)
    # annotate values
    for i in range(len(fact_keys)):
        for j in range(n_arch):
            v = mat[i, j]
            if np.isfinite(v):
                col = "white" if pass_mat[i, j] == 0 else "black"
                ax.text(j, i, f"{v:+.2f}", ha="center", va="center",
                        fontsize=6, color=col)
    # n_pass per column at top
    for j, (lbl, p) in enumerate(cols):
        s = pass_mat[:, j].sum()
        ax.text(j, -0.6, f"{s}/11", ha="center", va="bottom",
                fontsize=9, fontweight="bold",
                color="darkgreen" if s >= 7 else "black")
    ax.set_title("Stylized facts pass/fail across architectures (H20 N=10⁴)")
    plt.tight_layout()
    out = FIG_DIR / "fig3_scoreboard_matrix.pdf"
    plt.savefig(out, dpi=150)
    plt.savefig(out.with_suffix(".png"), dpi=150)
    plt.close()
    print(f"  wrote {out}")


# ─── Fig 4 — loss-curves D-series Goodhart evidence ────────────────────
def fig4_d_overfit():
    """Show D series (400-iter) loss curves — loss falls but facts diverge."""
    runs = [
        ("D0 (A0 long)", "experiments/022_h20_batch/results_d0/training_log.json", "tab:blue", 2),
        ("D2 (B4 long)", "experiments/022_h20_batch/results_d2/training_log.json", "tab:orange", 3),
        ("D3 (C0 long)", "experiments/022_h20_batch/results_d3/training_log.json", "tab:green", 4),
        ("D4 (C4 long)", "experiments/022_h20_batch/results_d4/training_log.json", "tab:red", 4),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for label, path, c, n_pass in runs:
        d = load_inference(REPO / path)
        if d is None:
            continue
        h = d["history"]
        iters = [r["iter"] for r in h]
        loss = [r["total_world_mean"] for r in h]
        acf = [r["acf_sim"] for r in h]
        axes[0].plot(iters, loss, color=c, alpha=0.7, lw=1.2,
                     label=f"{label} → {n_pass}/11")
        axes[1].plot(iters, acf, color=c, alpha=0.7, lw=1.2)
    axes[0].set_xlabel("iter")
    axes[0].set_ylabel("training loss (world mean)")
    axes[0].set_title("D series — training loss falls smoothly")
    axes[0].set_yscale("log")
    axes[0].legend(loc="upper right", fontsize=8)
    axes[0].grid(alpha=0.3)

    axes[1].set_xlabel("iter")
    axes[1].set_ylabel("acf_sim (mean over lags 1..8)")
    axes[1].set_title("D series — but inline acf_sim oscillates / diverges")
    axes[1].axhline(0.342, color="black", ls="--", lw=0.8, label="real SPX")
    axes[1].axhline(0, color="gray", ls=":", lw=0.5)
    axes[1].legend(loc="upper right", fontsize=8)
    axes[1].grid(alpha=0.3)
    plt.tight_layout()
    out = FIG_DIR / "fig4_d_overfit.pdf"
    plt.savefig(out, dpi=150)
    plt.savefig(out.with_suffix(".png"), dpi=150)
    plt.close()
    print(f"  wrote {out}")


# ─── Fig 5 — phase progression A→B→C→D ────────────────────────────────
def fig5_phase_progression():
    """Bar chart of best-in-phase n/11 score."""
    bests = [
        ("A (default v3)", 7, "A0"),
        ("B (conservative)", 6, "B3"),
        ("C (expanded loss)", 8, "C4"),
        ("D (long training)", 4, "D4"),
    ]
    fig, ax = plt.subplots(figsize=(7, 4))
    labels = [b[0] for b in bests]
    scores = [b[1] for b in bests]
    bestnames = [b[2] for b in bests]
    bars = ax.bar(labels, scores, color=["#888", "#888", "#2d8", "#888"])
    for i, (bar, name) in enumerate(zip(bars, bestnames)):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f"{name}\n{scores[i]}/11", ha="center", va="bottom",
                fontsize=9, fontweight="bold")
    ax.set_ylim(0, 11)
    ax.axhline(8, color="green", ls="--", alpha=0.5, label="C4 winner (8/11)")
    ax.axhline(7, color="orange", ls=":", alpha=0.5, label="prior best (v1.0 Hawkes 7/11)")
    ax.set_ylabel("max n/11 in phase")
    ax.set_title("Architecture progression — expanded loss is the cure")
    ax.legend(loc="lower left", fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    out = FIG_DIR / "fig5_phase_progression.pdf"
    plt.savefig(out, dpi=150)
    plt.savefig(out.with_suffix(".png"), dpi=150)
    plt.close()
    print(f"  wrote {out}")


# ─── Fig 1 — refresh force probe with v3 ────────────────────────────────
def fig1_force_probe_refresh():
    """Existing 018 experiment data, extend with v3."""
    src = REPO / "experiments/018_force_probe/results/force_data.json"
    if not src.exists():
        print(f"  [skip fig1] no force_data.json — run experiment 018 first")
        return
    d = json.loads(src.read_text())
    fig, ax = plt.subplots(figsize=(8, 4.5))
    names = []
    f_means = []
    f_stds = []
    for r in d:
        if "error" in r:
            continue
        names.append(r["name"])
        f_means.append(r["F_mean"])
        f_stds.append(r["F_std"])
    sigma = 0.032  # Langevin noise σ from 018
    ratios = np.array(f_means) / sigma
    colors = ["#d33" if r < 1 else "#3a3" if r > 30 else "#fa3" for r in ratios]
    ypos = np.arange(len(names))
    ax.barh(ypos, ratios, xerr=np.array(f_stds) / sigma, color=colors, alpha=0.8)
    ax.axvline(1, color="black", ls="--", lw=1, label="|F|=σ noise floor")
    ax.axvline(30, color="green", ls=":", lw=1, label="|F|=30σ trainable lower bound")
    ax.set_yticks(ypos)
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel("|F| / σ_noise (init)")
    ax.set_title("Force-magnitude probe — architectural sweet spot")
    ax.set_xscale("log")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    out = FIG_DIR / "fig1_force_probe.pdf"
    plt.savefig(out, dpi=150)
    plt.savefig(out.with_suffix(".png"), dpi=150)
    plt.close()
    print(f"  wrote {out}")


# ─── Fig 2 — ACF shape comparison ────────────────────────────────────
def fig2_acf_shape():
    """Existing 019 data: ACF curves across architectures."""
    src = REPO / "experiments/019_acf_shape/results/acf_shape_data.json"
    if not src.exists():
        print(f"  [skip fig2] no acf_shape_data.json — run experiment 019 first")
        return
    d = json.loads(src.read_text())
    fig, ax = plt.subplots(figsize=(8, 5))
    for arch in d:
        if "missing" in arch or not arch.get("acf_mean"):
            continue
        mean = np.array(arch["acf_mean"])
        std = np.array(arch["acf_std"])
        lags = np.arange(len(mean))
        ax.plot(lags, mean, label=arch["label"], lw=1.5)
        ax.fill_between(lags, mean - std, mean + std, alpha=0.15)
    ax.axhline(0, color="gray", ls=":", lw=0.5)
    ax.set_xlabel("lag τ")
    ax.set_ylabel("ACF(r²)")
    ax.set_title("ACF(r²) decay shape — peak-decay vs flat (Goodhart fail)")
    ax.legend(fontsize=7, loc="upper right")
    ax.grid(alpha=0.3)
    ax.set_xlim(0, 20)
    plt.tight_layout()
    out = FIG_DIR / "fig2_acf_shape.pdf"
    plt.savefig(out, dpi=150)
    plt.savefig(out.with_suffix(".png"), dpi=150)
    plt.close()
    print(f"  wrote {out}")


def main():
    print("Generating Paper A figures…")
    fig1_force_probe_refresh()
    fig2_acf_shape()
    fig3_scoreboard()
    fig4_d_overfit()
    fig5_phase_progression()
    print("done.")


if __name__ == "__main__":
    main()
