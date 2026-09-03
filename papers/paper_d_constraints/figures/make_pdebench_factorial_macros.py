from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

CLASS_LABELS = {
    "material_nonadditivity": "material non-additivity",
    "statistical_nonadditivity_below_or_crossing_sesoi": (
        "statistical non-additivity below/crossing the SESOI"
    ),
    "practical_additivity": "practical additivity",
    "unresolved": "unresolved",
}


def load_analysis(path: Path) -> dict[str, Any]:
    analysis = json.loads(path.read_text(encoding="utf-8"))
    if analysis.get("schema_version") != "constraint-iclr-pdebench-factorial-analysis-v1":
        raise ValueError("unexpected factorial-analysis schema")
    if analysis.get("integrity_gates_passed") is not True:
        raise ValueError("refusing to report an analysis with failed integrity gates")
    if analysis.get("record_count") != 150:
        raise ValueError("factorial analysis must contain exactly 150 records")
    if not isinstance(analysis.get("all_cases"), list) or len(analysis["all_cases"]) != 12:
        raise ValueError("factorial analysis must contain exactly 12 evaluation cells")
    classification = analysis.get("primary", {}).get("interaction", {}).get("classification")
    if classification not in CLASS_LABELS:
        raise ValueError("unknown frozen primary classification")
    return analysis


def _number(value: float) -> str:
    magnitude = abs(value)
    if magnitude == 0.0:
        return "0"
    if magnitude < 1e-4 or magnitude >= 1e3:
        return f"{value:.3e}"
    return f"{value:.5f}"


def _macro(prefix: str, name: str, value: str | int) -> str:
    return rf"\newcommand{{\{prefix}{name}}}{{{value}}}"


def make_macros(analysis: dict[str, Any], prefix: str) -> str:
    if re.fullmatch(r"[A-Za-z]+", prefix) is None:
        raise ValueError("macro prefix must contain ASCII letters only")
    primary = analysis["primary"]
    cells = primary["cell_mean_conserving_rmse"]
    credits = primary["credits"]
    interaction = primary["interaction"]
    classification = str(interaction["classification"])
    class_counts = Counter(
        str(cell["interaction"]["classification"]) for cell in analysis["all_cases"]
    )
    holm_significant = sum(
        float(cell["interaction"]["sign_flip_p_holm"]) < 0.05
        for cell in analysis["all_cases"]
    )

    values: list[tuple[str, str | int]] = [
        ("Benchmark", str(analysis["benchmark_id"]).replace("_", r"\_")),
        ("Records", int(analysis["record_count"])),
        ("PrimaryCase", str(primary["case"]).replace("_", r"\_")),
        ("PrimaryHorizon", int(primary["horizon"])),
        ("AZero", _number(float(cells["absolute_free"]))),
        ("RZero", _number(float(cells["residual_free"]))),
        ("AOne", _number(float(cells["absolute_hard"]))),
        ("ROne", _number(float(cells["residual_hard"]))),
        ("Projected", _number(float(cells["absolute_free_projected"]))),
        ("Interaction", _number(float(interaction["mean"]))),
        ("InteractionLow", _number(float(interaction["ci95"][0]))),
        ("InteractionHigh", _number(float(interaction["ci95"][1]))),
        ("InteractionLowNinety", _number(float(interaction["ci90"][0]))),
        ("InteractionHighNinety", _number(float(interaction["ci90"][1]))),
        ("Sesoi", _number(float(interaction["sesoi"]))),
        ("Classification", CLASS_LABELS[classification]),
        ("HolmSignificantCells", holm_significant),
        ("MaterialCells", class_counts["material_nonadditivity"]),
        (
            "SmallerStatisticalCells",
            class_counts["statistical_nonadditivity_below_or_crossing_sesoi"],
        ),
        ("AdditiveCells", class_counts["practical_additivity"]),
        ("UnresolvedCells", class_counts["unresolved"]),
    ]
    credit_names = {
        "parameterization_when_free": "PZero",
        "parameterization_when_hard": "POne",
        "enforcement_in_absolute_coordinates": "EAbsolute",
        "enforcement_in_residual_coordinates": "EResidual",
        "shapley_parameterization": "PhiParameterization",
        "shapley_enforcement": "PhiEnforcement",
        "projection_minus_hard_abs": "ProjectionMinusHardAbsolute",
    }
    for key, suffix in credit_names.items():
        result = credits[key]
        values.extend(
            (
                (suffix, _number(float(result["mean"]))),
                (suffix + "Low", _number(float(result["ci"][0]))),
                (suffix + "High", _number(float(result["ci"][1]))),
            )
        )
    return "\n".join(_macro(prefix, name, value) for name, value in values) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate integrity-gated LaTeX macros from a factorial analysis."
    )
    parser.add_argument("analysis", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--prefix", default="Factor")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    macros = make_macros(load_analysis(args.analysis), args.prefix)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(macros, encoding="utf-8")


if __name__ == "__main__":
    main()
