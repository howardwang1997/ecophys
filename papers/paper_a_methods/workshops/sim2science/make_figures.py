"""Generate the Sim2Science paper figures from frozen experiment-127 artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
RESULTS_PATH = REPO_ROOT / "experiments/127_workshop_claim_gates/ANALYTIC_RESULTS.json"
FIGURE_DIR = HERE / "figures"

NAVY = "#17324D"
TEAL = "#197B7A"
ORANGE = "#D97706"
RED = "#B33A3A"
GREY = "#6B7280"
LIGHT_BLUE = "#DCEAF4"
LIGHT_TEAL = "#DDF1EE"
LIGHT_ORANGE = "#F8E8CE"


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.labelsize": 8,
            "axes.titlesize": 8.5,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def _save(fig: Figure, stem: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_DIR / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(FIGURE_DIR / f"{stem}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_protocol() -> None:
    fig, ax = plt.subplots(figsize=(7.15, 2.05))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis("off")

    _box(ax, 0.15, 2.5, 2.0, 1.05, LIGHT_BLUE, "Calibration\n16 trajectories")
    _box(ax, 2.65, 2.5, 2.15, 1.05, LIGHT_TEAL, "Late blocks\nscale + null")
    _box(ax, 5.30, 2.5, 2.15, 1.05, LIGHT_ORANGE, "Energy distance\n3-block plateau")
    _box(ax, 7.95, 2.5, 1.55, 1.05, "#E8E5F4", "Freeze\n$W^{\\star}$")
    _box(ax, 10.00, 2.5, 1.85, 1.05, "#EFEFEF", "Serialize + hash\nbefore holdout")

    for start, stop in ((2.15, 2.65), (4.80, 5.30), (7.45, 7.95), (9.50, 10.00)):
        _arrow(ax, start, 3.025, stop, 3.025)

    _box(ax, 0.15, 0.45, 2.0, 1.05, LIGHT_BLUE, "Held-out\n16 trajectories")
    _box(ax, 2.65, 0.45, 2.15, 1.05, LIGHT_TEAL, "Apply frozen\nscale, tolerance, $W^{\\star}$")
    _box(ax, 5.30, 0.45, 2.15, 1.05, LIGHT_ORANGE, "Transfer check\n(no refitting)")
    _box(ax, 7.95, 0.45, 3.90, 1.05, "#EFEFEF", "Equal-length scoring\n$[0,4000)$ vs. $[W^{\\star},W^{\\star}+4000)$")
    for start, stop in ((2.15, 2.65), (4.80, 5.30), (7.45, 7.95)):
        _arrow(ax, start, 0.975, stop, 0.975)
    ax.add_patch(
        FancyArrowPatch(
            (8.72, 2.5),
            (3.73, 1.5),
            connectionstyle="arc3,rad=0.18",
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=1.2,
            color=NAVY,
        )
    )
    ax.text(6.55, 1.82, "frozen quantities only", ha="center", va="center", color=NAVY, fontsize=7)
    ax.text(0.15, 3.82, "Fit", color=NAVY, fontweight="bold", fontsize=9)
    ax.text(0.15, 1.77, "Test", color=NAVY, fontweight="bold", fontsize=9)
    _save(fig, "fig_protocol")


def _box(ax: Axes, x: float, y: float, width: float, height: float, color: str, label: str) -> None:
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.035,rounding_size=0.07",
        facecolor=color,
        edgecolor=NAVY,
        linewidth=0.9,
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height / 2, label, ha="center", va="center", color=NAVY)


def _arrow(ax: Axes, x0: float, y0: float, x1: float, y1: float) -> None:
    ax.add_patch(
        FancyArrowPatch(
            (x0, y0),
            (x1, y1),
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=1.0,
            color=NAVY,
        )
    )


def make_analytic_controls() -> None:
    payload = cast(dict[str, Any], json.loads(RESULTS_PATH.read_text()))
    summary = cast(dict[str, Any], payload["summary"])
    condition_rows = cast(list[dict[str, Any]], summary["by_condition_method"])
    stationary = cast(dict[str, dict[str, Any]], summary["pooled_stationary_false_positive"])
    rows_by_key = {
        (str(row["model"]), str(row["condition"]), str(row["method"])): row
        for row in condition_rows
    }

    fig, axes = plt.subplots(1, 3, figsize=(7.15, 2.38), gridspec_kw={"wspace": 0.42})
    _stationary_panel(axes[0], stationary)
    _sensitivity_panel(axes[1], rows_by_key)
    _error_panel(axes[2], payload)
    for label, ax in zip(("a", "b", "c"), axes, strict=True):
        ax.text(-0.20, 1.08, label, transform=ax.transAxes, fontweight="bold", fontsize=9)
    _save(fig, "fig_analytic_controls")


def _stationary_panel(ax: Axes, stationary: dict[str, dict[str, Any]]) -> None:
    methods = ["no_discard", "fixed_500", "fixed_1000", "adf_kpss", "energy"]
    labels = ["None", "Fixed\n500", "Fixed\n1000", "ADF/\nKPSS", "Energy"]
    rates = np.array([float(stationary[name]["rate"]) for name in methods])
    intervals = np.array([stationary[name]["wilson_95"] for name in methods], dtype=float)
    errors = np.clip(np.vstack((rates - intervals[:, 0], intervals[:, 1] - rates)), 0.0, None)
    colors = [GREY, ORANGE, ORANGE, RED, TEAL]
    x = np.arange(len(methods))
    ax.bar(x, rates, color=colors, width=0.72, edgecolor="white", linewidth=0.5)
    ax.errorbar(x, rates, yerr=errors, fmt="none", ecolor=NAVY, capsize=2.2, linewidth=0.8)
    ax.axhline(0.15, color=NAVY, linestyle="--", linewidth=0.9, label="frozen bound")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("unnecessary-discard rate")
    ax.set_title("Stationary controls (n=62)", pad=5)
    ax.legend(frameon=False, loc="upper left")
    ax.grid(axis="y", color="#D1D5DB", linewidth=0.5, alpha=0.7)


def _sensitivity_panel(ax: Axes, rows: dict[tuple[str, str, str], dict[str, Any]]) -> None:
    keys = [
        ("garch_t", "cold_low", "energy"),
        ("garch_t", "cold_high", "energy"),
        ("ar1_sv", "cold_low", "energy"),
        ("ar1_sv", "cold_high", "energy"),
    ]
    labels = ["GARCH\n0.1x", "GARCH\n10x", "SV\n0.1x", "SV\n10x"]
    rates = np.array([float(rows[key]["detection_rate"]) for key in keys])
    intervals = np.array([rows[key]["detection_wilson_95"] for key in keys], dtype=float)
    errors = np.clip(np.vstack((rates - intervals[:, 0], intervals[:, 1] - rates)), 0.0, None)
    x = np.arange(len(keys))
    ax.bar(x, rates, color=[TEAL, TEAL, TEAL, TEAL], width=0.68)
    ax.errorbar(x, rates, yerr=errors, fmt="none", ecolor=NAVY, capsize=2.2, linewidth=0.8)
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 0.86)
    ax.set_ylabel("transient-detection rate")
    ax.set_title("Cold-start sensitivity (n=31 each)", pad=5)
    ax.grid(axis="y", color="#D1D5DB", linewidth=0.5, alpha=0.7)


def _error_panel(ax: Axes, payload: dict[str, Any]) -> None:
    rows = cast(list[dict[str, Any]], payload["pseudo_checkpoint_rows"])
    methods = ["no_discard", "fixed_500", "fixed_1000", "energy"]
    labels = ["None", "Fixed\n500", "Fixed\n1000", "Energy"]
    means: list[float] = []
    medians: list[float] = []
    for method in methods:
        values = np.asarray(
            [
                float(row["hill_abs_error_to_reference"])
                for row in rows
                if row["method"] == method
                and row["condition"] in ("cold_low", "cold_high")
                and row["hill_abs_error_to_reference"] is not None
            ],
            dtype=float,
        )
        means.append(float(np.mean(values)))
        medians.append(float(np.median(values)))
    x = np.arange(len(methods))
    width = 0.34
    ax.bar(x - width / 2, medians, width, color=TEAL, label="median")
    ax.bar(x + width / 2, means, width, color=ORANGE, label="mean")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 0.13)
    ax.set_ylabel("absolute Hill error")
    ax.set_title("Cold-condition score error", pad=5)
    ax.legend(frameon=False, ncol=2, loc="upper left", columnspacing=0.8, handlelength=1.2)
    ax.grid(axis="y", color="#D1D5DB", linewidth=0.5, alpha=0.7)


def main() -> None:
    _style()
    make_protocol()
    make_analytic_controls()


if __name__ == "__main__":
    main()
