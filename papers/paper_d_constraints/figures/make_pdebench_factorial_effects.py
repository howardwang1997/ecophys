from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

CASE_ORDER = {"id_r256": 0, "ood_r512": 1, "ood_r1024": 2}
CASE_LABELS = {
    "id_r256": "ID 256",
    "ood_r512": "OOD 512",
    "ood_r1024": "OOD 1024",
}
CASE_COLORS = {
    "id_r256": "#4C78A8",
    "ood_r512": "#F58518",
    "ood_r1024": "#54A24B",
}


def load_analysis(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        analysis = json.load(handle)
    if analysis.get("schema_version") != "constraint-iclr-pdebench-factorial-analysis-v1":
        raise ValueError("unexpected factorial-analysis schema")
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


def _asymmetric_error(mean: np.ndarray, interval: np.ndarray) -> np.ndarray:
    return np.vstack((mean - interval[:, 0], interval[:, 1] - mean))


def make_figure(analysis: dict[str, Any], output: Path) -> None:
    primary = analysis["primary"]
    credit_spec = (
        ("parameterization_when_free", "$P_0$\nfree"),
        ("parameterization_when_hard", "$P_1$\nhard"),
        ("enforcement_in_absolute_coordinates", "$E_A$\nabsolute"),
        ("enforcement_in_residual_coordinates", "$E_R$\nresidual"),
        ("shapley_parameterization", "$\\phi_P$\npath avg."),
        ("shapley_enforcement", "$\\phi_E$\npath avg."),
    )
    credit_means = np.asarray(
        [float(primary["credits"][key]["mean"]) for key, _ in credit_spec],
        dtype=float,
    )
    credit_ci = np.asarray(
        [primary["credits"][key]["ci"] for key, _ in credit_spec], dtype=float
    )
    credit_errors = _asymmetric_error(credit_means, credit_ci)
    credit_colors = ["#4C78A8", "#4C78A8", "#F58518", "#F58518", "#4C78A8", "#F58518"]

    cases = ordered_cases(analysis)
    positions = np.arange(len(cases), dtype=float)
    interaction = np.asarray(
        [float(item["interaction"]["mean"]) for item in cases], dtype=float
    )
    interaction_ci = np.asarray(
        [item["interaction"]["ci95"] for item in cases], dtype=float
    )
    sesoi = np.asarray(
        [float(item["interaction"]["sesoi"]) for item in cases], dtype=float
    )
    if np.any(sesoi <= 0.0):
        raise ValueError("every cell must have a positive frozen SESOI")
    normalized_interaction = interaction / sesoi
    normalized_ci = interaction_ci / sesoi[:, None]
    normalized_errors = _asymmetric_error(normalized_interaction, normalized_ci)
    case_colors = [CASE_COLORS[str(item["case"])] for item in cases]
    case_labels = [
        f"{CASE_LABELS[str(item['case'])]}\nh={int(item['horizon'])}" for item in cases
    ]

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
    figure, axes = plt.subplots(
        2, 1, figsize=(6.7, 5.05), constrained_layout=True
    )

    credit_axis = axes[0]
    credit_axis.axhline(0.0, color="#555555", linewidth=0.8, linestyle="--", zorder=1)
    for index, (value, color) in enumerate(
        zip(credit_means, credit_colors, strict=True)
    ):
        credit_axis.errorbar(
            index,
            value,
            yerr=credit_errors[:, index : index + 1],
            fmt="o",
            color=color,
            ecolor=color,
            capsize=3,
            markersize=5,
            linewidth=1.2,
            zorder=2,
        )
    credit_axis.axvline(3.5, color="#D0D0D0", linewidth=0.7, zorder=0)
    credit_axis.set_xticks(
        np.arange(len(credit_spec)), [label for _, label in credit_spec]
    )
    credit_axis.set_ylabel("Conserving-RMSE reduction")
    credit_axis.set_title(
        "(a) Primary simple and path-averaged intervention credits (95% CI)",
        loc="left",
        fontweight="bold",
    )
    credit_axis.grid(axis="y", color="#E6E6E6", linewidth=0.6)
    credit_axis.spines[["top", "right"]].set_visible(False)
    credit_axis.legend(
        handles=[
            plt.Line2D(
                [0], [0], marker="o", linestyle="", color="#4C78A8", label="parameterization"
            ),
            plt.Line2D(
                [0], [0], marker="o", linestyle="", color="#F58518", label="enforcement"
            ),
        ],
        ncols=2,
        frameon=False,
        loc="best",
    )

    interaction_axis = axes[1]
    interaction_axis.axhspan(-1.0, 1.0, color="#E8E8E8", alpha=0.65, zorder=0)
    interaction_axis.axhline(0.0, color="#555555", linewidth=0.8, linestyle="--", zorder=1)
    interaction_axis.axhline(1.0, color="#888888", linewidth=0.65, linestyle=":", zorder=1)
    interaction_axis.axhline(-1.0, color="#888888", linewidth=0.65, linestyle=":", zorder=1)
    for split in (3.5, 7.5):
        interaction_axis.axvline(split, color="#D0D0D0", linewidth=0.7, zorder=0)
    for index, (value, color) in enumerate(
        zip(normalized_interaction, case_colors, strict=True)
    ):
        interaction_axis.errorbar(
            positions[index],
            value,
            yerr=normalized_errors[:, index : index + 1],
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
        if item["case"] == primary["case"]
        and int(item["horizon"]) == int(primary["horizon"])
    )
    interaction_axis.scatter(
        [positions[primary_index]],
        [normalized_interaction[primary_index]],
        marker="*",
        s=85,
        facecolors="none",
        edgecolors="#111111",
        linewidths=0.9,
        zorder=3,
    )
    interaction_axis.set_xticks(positions, case_labels, rotation=38, ha="right")
    interaction_axis.set_ylabel(r"Interaction $I / \delta$")
    interaction_axis.set_title(
        "(b) Path dependence relative to each cell's frozen SESOI (95% CI)",
        loc="left",
        fontweight="bold",
    )
    interaction_axis.grid(axis="y", color="#E6E6E6", linewidth=0.6)
    interaction_axis.spines[["top", "right"]].set_visible(False)
    interaction_axis.legend(
        handles=[
            plt.Line2D([0], [0], marker="o", linestyle="", color=color, label=CASE_LABELS[case])
            for case, color in CASE_COLORS.items()
        ],
        ncols=3,
        frameon=False,
        loc="best",
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, bbox_inches="tight")
    figure.savefig(output.with_suffix(".png"), dpi=240, bbox_inches="tight")
    plt.close(figure)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot the frozen PDEBench factorial attribution analysis."
    )
    parser.add_argument("analysis", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    make_figure(load_analysis(args.analysis), args.output)


if __name__ == "__main__":
    main()
