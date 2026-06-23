"""Figure 1: Pareto attribution matrix — Paper A central figure.

Two-panel evidence for the "no single mechanism in our 10-mechanism family
simultaneously satisfies all 11 Cont 2001 facts" central claim of §4:

  (a) 16-cell × 11-fact pass-rate heatmap from 089 attribution (n=50 seeds each)
      Shows each mechanism is a specialist — high on some facts, low on others.
      Mean column on right hand side gives cell-level ranking.

  (b) Per-fact "biggest mover" — for each of 11 facts, the mechanism that lifts
      pass-rate most vs baseline_v3. Floor-lifter cells highlighted in red.

Source: experiments/089_attribution_50seed/attribution_matrix.json
Output: papers/paper_a_methods/figures/fig1_attribution.{pdf,png}
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

REPO = Path(__file__).resolve().parents[3]
DATA = REPO / "experiments" / "089_attribution_50seed" / "attribution_matrix.json"
OUT_PDF = Path(__file__).resolve().parent / "fig1_attribution.pdf"
OUT_PNG = Path(__file__).resolve().parent / "fig1_attribution.png"

FACT_LABELS_SHORT = {
    "autocorr_returns": "ACF(r)",
    "hill_tail_index": "Hill",
    "gain_loss_asymmetry": "Gain/Loss",
    "aggregational_gaussianity": "AggGauss",
    "intermittency_fano": "Fano",
    "acf_squared_returns": "ACF(r²)",
    "conditional_kurtosis": "Cond.kurt.",
    "dfa_hurst_abs_r": "Hurst",
    "leverage_effect": "Leverage",
    "volume_volatility_corr": "Vol-σ",
    "zumbach_asymmetry": "Zumbach",
}

FLOOR_FACTS = {"autocorr_returns", "zumbach_asymmetry"}


def short_cell_name(cell: str) -> str:
    return cell.replace("attr_", "").replace("_", " ").replace("zumbach dn", "zumdn")


def main() -> None:
    payload = json.loads(DATA.read_text())
    facts = payload["facts"]
    rows = payload["rows"]
    baseline_cell = payload.get("baseline_cell", "attr_baseline_v3")

    baseline_row = next((r for r in rows if r["cell"] == baseline_cell), None)
    if baseline_row is None:
        raise SystemExit(f"baseline row {baseline_cell!r} not found")
    baseline_rates = baseline_row["per_fact_pass_rate"]

    rows_sorted = sorted(rows, key=lambda r: -r["mean_n_pass"])
    cells = [r["cell"] for r in rows_sorted]
    cell_labels = [short_cell_name(c) for c in cells]
    means = [r["mean_n_pass"] for r in rows_sorted]
    matrix = np.array([
        [r["per_fact_pass_rate"][f] for f in facts]
        for r in rows_sorted
    ])

    fact_labels = [FACT_LABELS_SHORT.get(f, f) for f in facts]
    fact_is_floor = [f in FLOOR_FACTS for f in facts]
    baseline_idx = cells.index(baseline_cell)

    cmap = LinearSegmentedColormap.from_list(
        "passrate", ["#08306b", "#4292c6", "#ffffff", "#fb6a4a", "#67000d"], N=256
    )

    fig = plt.figure(figsize=(12, 9.2), constrained_layout=False)
    gs = fig.add_gridspec(
        2, 2,
        height_ratios=[1.6, 1.0],
        width_ratios=[12, 1.0],
        hspace=0.28,
        wspace=0.04,
        left=0.13, right=0.96, top=0.94, bottom=0.08,
    )
    ax_hm = fig.add_subplot(gs[0, 0])
    ax_mean = fig.add_subplot(gs[0, 1], sharey=ax_hm)
    ax_bar = fig.add_subplot(gs[1, :])

    im = ax_hm.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=100)
    ax_hm.set_xticks(np.arange(len(fact_labels)))
    ax_hm.set_xticklabels(fact_labels, rotation=35, ha="right", fontsize=9)
    ax_hm.set_yticks(np.arange(len(cell_labels)))
    ax_hm.set_yticklabels(cell_labels, fontsize=9)

    for xi, is_floor in enumerate(fact_is_floor):
        if is_floor:
            tick = ax_hm.get_xticklabels()[xi]
            tick.set_color("#b30000")
            tick.set_fontweight("bold")

    for yi, cell in enumerate(cells):
        if cell == baseline_cell:
            ax_hm.get_yticklabels()[yi].set_fontweight("bold")
            ax_hm.get_yticklabels()[yi].set_color("#444")

    for yi in range(matrix.shape[0]):
        for xi in range(matrix.shape[1]):
            v = matrix[yi, xi]
            txt_color = "white" if (v > 70 or v < 25) else "black"
            ax_hm.text(xi, yi, f"{v:.0f}", ha="center", va="center",
                       fontsize=7, color=txt_color)

    ax_hm.set_title(
        "(a) Per-cell × per-fact pass rate (% of n=50 seeds in target band)",
        loc="left", fontsize=11, pad=10,
    )

    cbar = fig.colorbar(im, ax=ax_hm, shrink=0.7, pad=0.02, location="left")
    cbar.set_label("pass rate (%)", fontsize=9)
    cbar.ax.tick_params(labelsize=8)
    cbar.ax.yaxis.set_ticks_position("left")
    cbar.ax.yaxis.set_label_position("left")

    ax_mean.barh(
        np.arange(len(means)),
        means,
        color=["#cd5c5c" if c == baseline_cell else "#4682b4" for c in cells],
        height=0.7,
    )
    ax_mean.set_xlim(0, 7)
    ax_mean.axvline(baseline_row["mean_n_pass"], color="#cd5c5c",
                    linestyle="--", linewidth=0.8, alpha=0.7)
    for yi, m in enumerate(means):
        ax_mean.text(m + 0.1, yi, f"{m:.2f}", va="center", fontsize=8)
    ax_mean.set_xlabel("mean /11", fontsize=9)
    ax_mean.tick_params(axis="y", labelleft=False)
    ax_mean.set_title("(rank by mean)", fontsize=9, pad=10)
    ax_mean.spines[["top", "right"]].set_visible(False)

    biggest_mover = []
    delta_pp = []
    fact_floor_color = []
    for f in facts:
        b = baseline_rates.get(f, 0.0)
        best_cell = None
        best_delta = -1e9
        for r in rows:
            if r["cell"] == baseline_cell:
                continue
            delta = r["per_fact_pass_rate"].get(f, 0.0) - b
            if delta > best_delta:
                best_delta = delta
                best_cell = r["cell"]
        biggest_mover.append((best_cell, best_delta))
        delta_pp.append(best_delta)
        fact_floor_color.append("#b30000" if f in FLOOR_FACTS else "#4682b4")

    order = np.argsort(delta_pp)[::-1]
    facts_o = [fact_labels[i] for i in order]
    deltas_o = [delta_pp[i] for i in order]
    cells_o = [biggest_mover[i][0] for i in order]
    colors_o = [fact_floor_color[i] for i in order]

    bars = ax_bar.bar(
        np.arange(len(facts_o)), deltas_o, color=colors_o, edgecolor="black", linewidth=0.4,
    )
    ax_bar.axhline(0, color="black", linewidth=0.5)
    ax_bar.set_xticks(np.arange(len(facts_o)))
    ax_bar.set_xticklabels(facts_o, rotation=25, ha="right", fontsize=9)
    ax_bar.set_ylabel("Δ pass-rate vs v3 baseline (pp)", fontsize=9)
    ax_bar.set_title(
        "(b) Per-fact biggest mover — every fact has a different specialist mechanism. "
        "Red bars mark the two architectural floors lifted only at the cost of Pareto trades.",
        loc="left", fontsize=11, pad=10,
    )
    ax_bar.spines[["top", "right"]].set_visible(False)

    for i, (bar, cell) in enumerate(zip(bars, cells_o)):
        label = short_cell_name(cell)
        y = bar.get_height()
        y_off = 2 if y >= 0 else -2
        va = "bottom" if y >= 0 else "top"
        ax_bar.annotate(
            label, xy=(bar.get_x() + bar.get_width() / 2, y),
            xytext=(0, y_off), textcoords="offset points",
            ha="center", va=va, fontsize=7.5, color="#222",
            rotation=0,
        )

    fig.suptitle(
        "Figure 1.  Mechanism–fact attribution matrix (n=50 seeds × 16 cells). "
        "Specialist mechanisms, no generalist; floors are Pareto-bounded.",
        fontsize=12, y=0.985,
    )

    fig.savefig(OUT_PDF, dpi=200, bbox_inches="tight")
    fig.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
    print(f"wrote {OUT_PDF}")
    print(f"wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
