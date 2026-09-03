from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

CASE_ORDER = {"id_r256": 0, "ood_r512": 1, "ood_r1024": 2}
CASE_LABELS = {"id_r256": "ID 256", "ood_r512": "OOD 512", "ood_r1024": "OOD 1024"}
CASE_COLORS = {"id_r256": "#4C78A8", "ood_r512": "#F58518", "ood_r1024": "#54A24B"}


def load_analysis(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        analysis = json.load(handle)
    if analysis.get("integrity_gates_passed") is not True:
        raise ValueError("refusing to plot an analysis with failed integrity gates")
    cases = analysis.get("all_cases")
    if not isinstance(cases, list) or len(cases) != 12:
        raise ValueError("expected the frozen 12 case-by-horizon cells")
    return analysis


def ordered_cases(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        analysis["all_cases"],
        key=lambda item: (CASE_ORDER[str(item["case"])], int(item["horizon"])),
    )


def make_figure(analysis: dict[str, Any], output: Path) -> None:
    cases = ordered_cases(analysis)
    positions = np.arange(len(cases), dtype=float)
    labels = [f"{CASE_LABELS[str(item['case'])]}\nh={int(item['horizon'])}" for item in cases]
    colors = [CASE_COLORS[str(item["case"])] for item in cases]

    parameterization = np.array(
        [float(item["parameterization_effect_free_minus_free_res"]) for item in cases]
    )
    parameterization_ci = np.array([item["parameterization_effect_ci95"] for item in cases], dtype=float)
    parameterization_error = np.vstack(
        (parameterization - parameterization_ci[:, 0], parameterization_ci[:, 1] - parameterization)
    )

    hard_benefit = -np.array(
        [float(item["hard_enforcement_effect_hard_minus_free_res"]) for item in cases]
    )
    hard_ci_raw = np.array([item["hard_enforcement_effect_ci90"] for item in cases], dtype=float)
    hard_ci = np.column_stack((-hard_ci_raw[:, 1], -hard_ci_raw[:, 0]))
    hard_error = np.vstack((hard_benefit - hard_ci[:, 0], hard_ci[:, 1] - hard_benefit))

    plt.rcParams.update(
        {
            "font.size": 8.5,
            "axes.labelsize": 9,
            "axes.titlesize": 9.5,
            "legend.fontsize": 8,
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    figure, axes = plt.subplots(2, 1, figsize=(6.7, 5.0), sharex=True, constrained_layout=True)

    panels = (
        (
            axes[0],
            parameterization,
            parameterization_error,
            "Effect on conserving RMSE",
            "Parameterization: free - free-res (95% CI)",
        ),
        (
            axes[1],
            hard_benefit,
            hard_error,
            "Effect on conserving RMSE",
            "Hard enforcement: free-res - hard (90% CI)",
        ),
    )
    for panel_index, (axis, values, errors, ylabel, subtitle) in enumerate(panels):
        axis.axhline(0.0, color="#555555", linewidth=0.8, linestyle="--", zorder=1)
        for split in (3.5, 7.5):
            axis.axvline(split, color="#D0D0D0", linewidth=0.7, zorder=0)
        for index, (position, value, color) in enumerate(zip(positions, values, colors, strict=True)):
            axis.errorbar(
                position,
                value,
                yerr=errors[:, index : index + 1],
                fmt="o",
                color=color,
                ecolor=color,
                capsize=2.5,
                markersize=4.5,
                linewidth=1.1,
                zorder=2,
            )
        primary_index = next(
            index
            for index, item in enumerate(cases)
            if item["case"] == analysis["primary"]["case"]
            and int(item["horizon"]) == int(analysis["primary"]["horizon"])
        )
        axis.scatter(
            [positions[primary_index]],
            [values[primary_index]],
            marker="*",
            s=85,
            facecolors="none",
            edgecolors="#111111",
            linewidths=0.9,
            zorder=3,
        )
        axis.set_ylabel(ylabel)
        axis.set_title(f"({chr(97 + panel_index)}) {subtitle}", loc="left", fontweight="bold")
        axis.grid(axis="y", color="#E6E6E6", linewidth=0.6)
        axis.spines[["top", "right"]].set_visible(False)

    axes[1].set_xticks(positions, labels, rotation=38, ha="right")
    legend_handles = [
        plt.Line2D([0], [0], marker="o", linestyle="", color=color, label=CASE_LABELS[case])
        for case, color in CASE_COLORS.items()
    ]
    axes[0].legend(handles=legend_handles, ncols=3, frameon=False, loc="upper left")

    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, bbox_inches="tight")
    figure.savefig(output.with_suffix(".png"), dpi=240, bbox_inches="tight")
    plt.close(figure)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot frozen PDEBench attribution effects.")
    parser.add_argument("analysis", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    make_figure(load_analysis(args.analysis), args.output)


if __name__ == "__main__":
    main()
