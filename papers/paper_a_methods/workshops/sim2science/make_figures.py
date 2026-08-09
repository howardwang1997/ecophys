"""Generate the Sim2Science paper figures from frozen experiment-127 artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
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
EXPLORATORY_RESULTS_PATH = (
    REPO_ROOT / "experiments/127_workshop_claim_gates/EXPLORATORY_MSER5_RESULTS.json"
)
LEARNED_RESULTS_PATH = REPO_ROOT / "experiments/127_workshop_claim_gates/LEARNED_RESULTS.json"
FIGURE_DIR = HERE / "figures"

NAVY = "#17324D"
TEAL = "#197B7A"
ORANGE = "#D97706"
RED = "#B33A3A"
GREY = "#6B7280"
LIGHT_BLUE = "#DCEAF4"
LIGHT_TEAL = "#DDF1EE"
LIGHT_ORANGE = "#F8E8CE"

JOB_LABELS = {
    "e1_spx_concave": "SPX concave",
    "e1_spx_base": "SPX baseline",
    "e1_ndx_concave": "NDX concave",
    "e1_gold_concave": "Gold concave",
    "e1_eurusd_concave": "EUR/USD concave",
    "e1_btc_concave": "BTC concave",
    "e1_btc_base": "BTC baseline",
    "e3_sv_0": "SV variant 0",
    "e3_sv_1": "SV variant 1",
    "e3_sv_2": "SV variant 2",
}


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
    timestamp = datetime(1980, 1, 1, tzinfo=UTC)
    fig.savefig(
        FIGURE_DIR / f"{stem}.pdf",
        bbox_inches="tight",
        metadata={"Creator": "anonymous artifact", "CreationDate": timestamp, "ModDate": timestamp},
    )
    fig.savefig(
        FIGURE_DIR / f"{stem}.png",
        dpi=300,
        bbox_inches="tight",
        metadata={"Software": "anonymous artifact"},
    )
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


def make_ecomd_object() -> None:
    """Draw the complete data flow of the frozen simulator audit object."""
    fig, ax = plt.subplots(figsize=(7.15, 1.72))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 3.25)
    ax.axis("off")

    _box(ax, 0.10, 1.55, 2.15, 1.00, LIGHT_BLUE, "Agent state $s_t$\n$N=10^4$, $d=32$")
    _box(ax, 2.75, 1.55, 1.75, 1.00, "#E8E5F4", "Global $u_t$\nGRU, $d_u=16$")
    _box(
        ax,
        5.00,
        1.55,
        2.35,
        1.00,
        LIGHT_TEAL,
        "Pair kernel + gate\nExternal potential",
    )
    _box(ax, 7.85, 1.55, 2.10, 1.00, LIGHT_ORANGE, "Langevin step\n$t_5$ noise + jumps")
    _box(ax, 10.45, 1.55, 1.55, 1.00, "#F3E4E4", "Excess\ndemand")
    _box(ax, 12.50, 1.55, 1.40, 1.00, "#EFEFEF", "Impact\n+ return")

    for start, stop in ((2.25, 2.75), (4.50, 5.00), (7.35, 7.85), (9.95, 10.45), (12.00, 12.50)):
        _arrow(ax, start, 2.05, stop, 2.05)

    ax.add_patch(
        FancyArrowPatch(
            (13.20, 1.55),
            (3.62, 1.55),
            connectionstyle="arc3,rad=-0.24",
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=1.0,
            color=NAVY,
        )
    )
    ax.text(
        8.55,
        0.38,
        "return context feeds the global and external states",
        ha="center",
        va="center",
        color=NAVY,
        fontsize=7,
    )
    ax.text(
        0.10,
        2.92,
        "Frozen EcoMD audit object (not a previously published model)",
        color=NAVY,
        fontweight="bold",
        fontsize=8.5,
    )
    _save(fig, "fig_ecomd_object")


def make_analytic_controls() -> None:
    payload = cast(dict[str, Any], json.loads(RESULTS_PATH.read_text()))
    exploratory_payload = cast(dict[str, Any], json.loads(EXPLORATORY_RESULTS_PATH.read_text()))
    exploratory_summary = cast(dict[str, Any], exploratory_payload["summary"])
    summary = cast(dict[str, Any], payload["summary"])
    condition_rows = cast(list[dict[str, Any]], summary["by_condition_method"])
    stationary = cast(dict[str, dict[str, Any]], summary["pooled_stationary_false_positive"])
    rows_by_key = {
        (str(row["model"]), str(row["condition"]), str(row["method"])): row
        for row in condition_rows
    }

    fig, axes = plt.subplots(1, 3, figsize=(7.15, 2.38), gridspec_kw={"wspace": 0.42})
    _stationary_panel(axes[0], stationary, exploratory_summary)
    _sensitivity_panel(axes[1], rows_by_key, exploratory_summary)
    _error_panel(axes[2], payload, exploratory_summary)
    for label, ax in zip(("a", "b", "c"), axes, strict=True):
        ax.text(-0.20, 1.08, label, transform=ax.transAxes, fontweight="bold", fontsize=9)
    _save(fig, "fig_analytic_controls")


def _stationary_panel(
    ax: Axes,
    stationary: dict[str, dict[str, Any]],
    exploratory: dict[str, Any],
) -> None:
    methods = ["fixed_500", "fixed_1000", "adf_kpss", "energy"]
    labels = ["500", "1000", "ADF+\nKPSS", "ED", "MSER-\n5"]
    mser_count = int(exploratory["stationary_unnecessary_discard_count"])
    mser_n = int(exploratory["stationary_n"])
    rates = np.array(
        [*[float(stationary[name]["rate"]) for name in methods], mser_count / mser_n]
    )
    intervals = np.array(
        [
            *[stationary[name]["wilson_95"] for name in methods],
            _wilson_interval(mser_count, mser_n),
        ],
        dtype=float,
    )
    errors = np.clip(np.vstack((rates - intervals[:, 0], intervals[:, 1] - rates)), 0.0, None)
    colors = [ORANGE, ORANGE, RED, TEAL, GREY]
    x = np.arange(len(labels))
    ax.bar(x, rates, color=colors, width=0.72, edgecolor="white", linewidth=0.5)
    ax.errorbar(x, rates, yerr=errors, fmt="none", ecolor=NAVY, capsize=2.2, linewidth=0.8)
    ax.axhline(0.15, color=NAVY, linestyle="--", linewidth=0.9, label="frozen bound")
    ax.set_xticks(x, labels)
    ax.tick_params(axis="x", labelsize=6)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("unnecessary-discard rate")
    ax.set_title("Stationary controls (n=62)", pad=5)
    ax.legend(frameon=False, loc="upper left")
    ax.grid(axis="y", color="#D1D5DB", linewidth=0.5, alpha=0.7)


def _sensitivity_panel(
    ax: Axes,
    rows: dict[tuple[str, str, str], dict[str, Any]],
    exploratory: dict[str, Any],
) -> None:
    keys = [
        ("garch_t", "cold_low", "energy"),
        ("garch_t", "cold_high", "energy"),
        ("ar1_sv", "cold_low", "energy"),
        ("ar1_sv", "cold_high", "energy"),
    ]
    labels = ["GARCH\n0.1x", "GARCH\n10x", "SV\n0.1x", "SV\n10x"]
    energy_rates = np.array([float(rows[key]["detection_rate"]) for key in keys])
    energy_intervals = np.array(
        [rows[key]["detection_wilson_95"] for key in keys], dtype=float
    )
    energy_errors = np.clip(
        np.vstack(
            (energy_rates - energy_intervals[:, 0], energy_intervals[:, 1] - energy_rates)
        ),
        0.0,
        None,
    )
    exploratory_rows = {
        (str(row["model"]), str(row["condition"])): row
        for row in cast(list[dict[str, Any]], exploratory["by_condition"])
    }
    mser_counts = np.array(
        [
            round(float(exploratory_rows[(model, condition)]["selection_rate"]) * 31)
            for model, condition, _ in keys
        ]
    )
    mser_rates = mser_counts / 31
    mser_intervals = np.array([_wilson_interval(int(count), 31) for count in mser_counts])
    mser_errors = np.clip(
        np.vstack((mser_rates - mser_intervals[:, 0], mser_intervals[:, 1] - mser_rates)),
        0.0,
        None,
    )
    x = np.arange(len(keys))
    width = 0.34
    ax.bar(x - width / 2, energy_rates, color=TEAL, width=width)
    ax.bar(x + width / 2, mser_rates, color=GREY, width=width)
    ax.errorbar(
        x - width / 2,
        energy_rates,
        yerr=energy_errors,
        fmt="none",
        ecolor=NAVY,
        capsize=1.8,
        linewidth=0.7,
    )
    ax.errorbar(
        x + width / 2,
        mser_rates,
        yerr=mser_errors,
        fmt="none",
        ecolor=NAVY,
        capsize=1.8,
        linewidth=0.7,
    )
    ax.set_xticks(x, labels)
    ax.tick_params(axis="x", labelsize=6)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("transient-detection rate")
    ax.set_title("Cold-start sensitivity (n=31 each)", pad=5)
    ax.grid(axis="y", color="#D1D5DB", linewidth=0.5, alpha=0.7)


def _error_panel(ax: Axes, payload: dict[str, Any], exploratory: dict[str, Any]) -> None:
    rows = cast(list[dict[str, Any]], payload["pseudo_checkpoint_rows"])
    methods = ["no_discard", "fixed_500", "fixed_1000", "energy"]
    labels = ["None", "500", "1000", "ED", "MSER-\n5"]
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
    means.append(float(exploratory["cold_mean_hill_abs_error"]))
    medians.append(float(exploratory["cold_median_hill_abs_error"]))
    x = np.arange(len(labels))
    width = 0.34
    ax.bar(x - width / 2, medians, width, color=TEAL, label="median")
    ax.bar(x + width / 2, means, width, color=ORANGE, label="mean")
    ax.set_xticks(x, labels)
    ax.tick_params(axis="x", labelsize=6)
    ax.set_ylim(0, 0.13)
    ax.set_ylabel("absolute Hill error")
    ax.set_title("Cold-condition score error", pad=5)
    ax.legend(frameon=False, ncol=2, loc="upper left", columnspacing=0.8, handlelength=1.2)
    ax.grid(axis="y", color="#D1D5DB", linewidth=0.5, alpha=0.7)


def _wilson_interval(count: int, n: int) -> tuple[float, float]:
    z = 1.959963984540054
    rate = count / n
    denominator = 1.0 + z**2 / n
    center = (rate + z**2 / (2.0 * n)) / denominator
    half_width = z * np.sqrt(rate * (1.0 - rate) / n + z**2 / (4.0 * n**2)) / denominator
    return float(center - half_width), float(center + half_width)


def make_learned_results() -> None:
    payload = cast(dict[str, Any], json.loads(LEARNED_RESULTS_PATH.read_text()))
    checkpoints = cast(list[dict[str, Any]], payload["checkpoints"])
    primary = cast(dict[str, Any], payload["primary"])
    fig, (forest, slopes) = plt.subplots(
        1,
        2,
        figsize=(7.15, 3.05),
        gridspec_kw={"width_ratios": (1.36, 1.0), "wspace": 0.46},
    )
    _learned_forest_panel(forest, checkpoints, primary)
    _learned_slope_panel(slopes, checkpoints)
    forest.text(-0.28, 1.04, "a", transform=forest.transAxes, fontweight="bold", fontsize=9)
    slopes.text(-0.26, 1.04, "b", transform=slopes.transAxes, fontweight="bold", fontsize=9)
    _save(fig, "fig_learned_results")


def _learned_forest_panel(
    ax: Axes,
    checkpoints: list[dict[str, Any]],
    primary: dict[str, Any],
) -> None:
    ordered = list(checkpoints)
    intervals: list[tuple[float, float]] = []
    for index, checkpoint in enumerate(ordered):
        differences = np.asarray(checkpoint["paired_hill_differences"], dtype=float)
        if differences.size:
            intervals.append(_bootstrap_median_interval(differences, 128000 + index))
    aggregate_ci = primary.get("ci_95")
    if aggregate_ci is not None:
        intervals.append((float(aggregate_ci[0]), float(aggregate_ci[1])))
    finite_limits = [value for interval in intervals for value in interval]
    limit_low = min([*finite_limits, 0.0])
    limit_high = max([*finite_limits, 0.0])
    padding = max(0.12 * (limit_high - limit_low), 0.12)
    missing_x = limit_low - 0.55 * padding
    ax.set_xlim(limit_low - padding, limit_high + padding)

    for y, checkpoint in enumerate(ordered):
        job_id = str(checkpoint["job_id"])
        differences = np.asarray(checkpoint["paired_hill_differences"], dtype=float)
        if not differences.size:
            ax.scatter(missing_x, y, marker="x", color=GREY, s=24, linewidth=1.2, zorder=3)
            ax.text(missing_x, y - 0.28, "no $W^{\\star}$", color=GREY, ha="center", fontsize=5.7)
            continue
        point = float(np.median(differences))
        low, high = _bootstrap_median_interval(differences, 128000 + y)
        transfer = checkpoint["heldout_gate_evaluation"]["frozen_w_star_passes"] is True
        color = NAVY if job_id.startswith("e1_") else TEAL
        ax.errorbar(
            point,
            y,
            xerr=np.array([[point - low], [high - point]]),
            fmt="o",
            markersize=4.3,
            markerfacecolor=color if transfer else "white",
            markeredgecolor=color,
            ecolor=color,
            capsize=2.0,
            linewidth=0.9,
            zorder=3,
        )

    aggregate_y = len(ordered) + 0.45
    aggregate = primary.get("effect")
    if aggregate is not None and aggregate_ci is not None:
        point = float(aggregate)
        low, high = float(aggregate_ci[0]), float(aggregate_ci[1])
        ax.errorbar(
            point,
            aggregate_y,
            xerr=np.array([[point - low], [high - point]]),
            fmt="D",
            markersize=5.0,
            markerfacecolor=ORANGE,
            markeredgecolor=NAVY,
            ecolor=NAVY,
            capsize=2.2,
            linewidth=1.1,
            zorder=4,
        )
    labels = [JOB_LABELS.get(str(row["job_id"]), str(row["job_id"])) for row in ordered] + [
        "Primary aggregate"
    ]
    ax.set_yticks([*range(len(ordered)), aggregate_y], labels)
    ax.invert_yaxis()
    ax.axhline(len(ordered) - 0.5, color="#D1D5DB", linewidth=0.7)
    ax.axvline(0.0, color=GREY, linewidth=0.8, linestyle="--")
    ax.set_xlabel(r"paired Hill change $\Delta\alpha$")
    ax.set_title("Checkpoint effects (95% bootstrap)", pad=5)
    ax.grid(axis="x", color="#D1D5DB", linewidth=0.5, alpha=0.7)


def _learned_slope_panel(ax: Axes, checkpoints: list[dict[str, Any]]) -> None:
    plotted = 0
    for checkpoint in checkpoints:
        job_id = str(checkpoint["job_id"])
        if not job_id.startswith("e1_") or checkpoint["calibration_w_star"] is None:
            continue
        w_star = int(checkpoint["calibration_w_star"])
        sensitivity = cast(dict[str, Any], checkpoint["sensitivity"])
        early = float(sensitivity["0"]["heldout_median_estimates"]["hill_tail_index"])
        post = float(sensitivity[str(w_star)]["heldout_median_estimates"]["hill_tail_index"])
        transfer = checkpoint["heldout_gate_evaluation"]["frozen_w_star_passes"] is True
        color = NAVY if transfer else GREY
        ax.plot((0, 1), (early, post), color=color, linewidth=0.9, alpha=0.85)
        ax.scatter(
            (0, 1),
            (early, post),
            s=18,
            facecolors=color if transfer else "white",
            edgecolors=color,
            linewidths=0.8,
            zorder=3,
        )
        plotted += 1
    ax.axhspan(2.0, 4.0, color=LIGHT_ORANGE, alpha=0.75, zorder=0)
    ax.text(0.5, 3.0, "canonical 2--4", color=ORANGE, ha="center", va="center", fontsize=6.5)
    ax.set_xlim(-0.18, 1.18)
    ax.set_xticks((0, 1), ("early", "frozen $W^{\\star}$"))
    ax.set_ylabel("held-out median Hill index")
    ax.set_title(f"Absolute tail scores (n={plotted})", pad=5)
    ax.grid(axis="y", color="#D1D5DB", linewidth=0.5, alpha=0.7)


def _bootstrap_median_interval(values: np.ndarray, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, values.size, size=(2000, values.size))
    medians = np.median(values[indices], axis=1)
    return float(np.quantile(medians, 0.025)), float(np.quantile(medians, 0.975))


def main() -> None:
    _style()
    make_ecomd_object()
    make_protocol()
    make_analytic_controls()
    if LEARNED_RESULTS_PATH.is_file():
        make_learned_results()


if __name__ == "__main__":
    main()
