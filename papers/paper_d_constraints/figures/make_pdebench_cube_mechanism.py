from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

CASE_ORDER = ("id_r256", "ood_r512", "ood_r1024")
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
    analysis = json.loads(path.read_text(encoding="utf-8"))
    if analysis.get("schema_version") != (
        "constraint-iclr-pdebench-enforcement-cube-analysis-v1"
    ):
        raise ValueError("unexpected enforcement-cube analysis schema")
    if analysis.get("integrity_gates_passed") is not True:
        raise ValueError("refusing to plot an analysis with failed integrity gates")
    if (
        analysis.get("core_record_count") != 150
        or analysis.get("derived_record_count") != 90
        or analysis.get("checkpoint_count") != 120
    ):
        raise ValueError("enforcement cube does not have exact frozen coverage")
    if len(analysis.get("all_cases", [])) != 12:
        raise ValueError("enforcement cube must contain 12 case-by-horizon cells")
    return analysis


def _cell_by_case_horizon(
    analysis: dict[str, Any], case: str, horizon: int
) -> dict[str, Any]:
    return next(
        cell
        for cell in analysis["all_cases"]
        if cell["case"] == case and int(cell["horizon"]) == horizon
    )


def _asymmetric_error(mean: float, interval: list[float]) -> np.ndarray:
    return np.asarray([[mean - interval[0]], [interval[1] - mean]], dtype=float)


def make_figure(analysis: dict[str, Any], output: Path) -> None:
    plt.rcParams.update(
        {
            "font.size": 7.7,
            "axes.labelsize": 8.2,
            "axes.titlesize": 8.6,
            "legend.fontsize": 6.8,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    figure, axes = plt.subplots(
        1,
        3,
        figsize=(7.05, 2.35),
        gridspec_kw={"width_ratios": [1.08, 0.86, 1.18]},
        constrained_layout=True,
    )

    horizons = [1, 4, 16, 31]
    primary_case = "ood_r512"
    primary_cells = [
        _cell_by_case_horizon(analysis, primary_case, horizon) for horizon in horizons
    ]
    rollout_axis = axes[0]
    rollout_spec = (
        ("A10", "absolute, projection off", "#4C78A8", "-"),
        ("A11", "absolute, projection on", "#4C78A8", "--"),
        ("R10", "residual, projection off", "#F58518", "-"),
        ("R11", "residual, projection on", "#F58518", "--"),
    )
    for cell_name, label, color, linestyle in rollout_spec:
        values = [
            float(cell["cell_mean_conserving_rmse"][cell_name])
            for cell in primary_cells
        ]
        rollout_axis.plot(
            horizons,
            values,
            marker="o",
            markersize=3.2,
            linewidth=1.25,
            color=color,
            linestyle=linestyle,
            label=label,
        )
    rollout_axis.set_yscale("log")
    rollout_axis.set_xticks(horizons)
    rollout_axis.set_xlabel("rollout horizon")
    rollout_axis.set_ylabel("conserving RMSE (log)")
    rollout_axis.set_title("(a) Hard-trained checkpoints", loc="left", fontweight="bold")
    rollout_axis.grid(axis="y", color="#E4E4E4", linewidth=0.55)
    rollout_axis.spines[["top", "right"]].set_visible(False)
    rollout_axis.legend(frameon=False, loc="upper left")

    primary = analysis["primary"]
    effect_axis = axes[1]
    effect_spec = (
        ("phi_train", r"$\phi_{\mathrm{train}}$", "#4C78A8"),
        ("phi_infer", r"$\phi_{\mathrm{infer}}$", "#F58518"),
    )
    for position, (key, _label, color) in enumerate(effect_spec):
        summary = primary["effects"][key]
        mean = float(summary["mean"])
        effect_axis.errorbar(
            mean,
            position,
            xerr=_asymmetric_error(mean, summary["ci"]),
            fmt="o",
            color=color,
            ecolor=color,
            capsize=3,
            linewidth=1.2,
            markersize=4.2,
        )
    bundle = float(primary["effects"]["I_bundle"]["mean"])
    effect_axis.axvline(0.0, color="#555555", linewidth=0.8, linestyle="--")
    effect_axis.axvline(bundle, color="#222222", linewidth=1.0, linestyle=":")
    effect_axis.text(
        bundle,
        1.48,
        rf"sum $={bundle:.4f}$",
        ha="center",
        va="bottom",
        fontsize=6.8,
    )
    effect_axis.set_yticks([0, 1], [label for _, label, _ in effect_spec])
    effect_axis.set_ylim(-0.55, 1.75)
    effect_axis.set_xlabel("credit to bundled interaction")
    effect_axis.set_title("(b) Countervailing paths", loc="left", fontweight="bold")
    effect_axis.grid(axis="x", color="#E4E4E4", linewidth=0.55)
    effect_axis.spines[["top", "right", "left"]].set_visible(False)

    interaction_axis = axes[2]
    for case in CASE_ORDER:
        cells = [_cell_by_case_horizon(analysis, case, horizon) for horizon in horizons]
        normalized = np.asarray(
            [
                float(cell["three_way_interaction"]["mean"])
                / float(cell["three_way_interaction"]["sesoi"])
                for cell in cells
            ]
        )
        intervals = np.asarray(
            [
                np.asarray(cell["three_way_interaction"]["ci95"], dtype=float)
                / float(cell["three_way_interaction"]["sesoi"])
                for cell in cells
            ]
        )
        errors = np.vstack(
            (normalized - intervals[:, 0], intervals[:, 1] - normalized)
        )
        interaction_axis.errorbar(
            horizons,
            normalized,
            yerr=errors,
            marker="o",
            markersize=3.2,
            linewidth=1.15,
            capsize=2,
            color=CASE_COLORS[case],
            label=CASE_LABELS[case],
        )
    interaction_axis.axhline(0.0, color="#555555", linewidth=0.8, linestyle="--")
    interaction_axis.axhline(1.0, color="#888888", linewidth=0.7, linestyle=":")
    interaction_axis.set_xticks(horizons)
    interaction_axis.set_xlabel("rollout horizon")
    interaction_axis.set_ylabel(r"three-way interaction $J/\delta$")
    interaction_axis.set_title("(c) Feedback-emergent interaction", loc="left", fontweight="bold")
    interaction_axis.grid(axis="y", color="#E4E4E4", linewidth=0.55)
    interaction_axis.spines[["top", "right"]].set_visible(False)
    interaction_axis.legend(frameon=False, loc="upper right")

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() != ".pdf":
        raise ValueError("the archival mechanism figure output must be PDF")
    figure.savefig(
        output,
        bbox_inches="tight",
        metadata={
            "Creator": "EcoPhys Paper D artifact builder",
            "CreationDate": None,
            "ModDate": None,
        },
    )
    figure.savefig(output.with_suffix(".png"), dpi=240, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    make_figure(load_analysis(args.analysis), args.output)


if __name__ == "__main__":
    main()
