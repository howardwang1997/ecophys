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
        "smaller statistical non-additivity"
    ),
    "practical_additivity": "practical additivity",
    "unresolved": "unresolved",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _number(value: float) -> str:
    magnitude = abs(value)
    if magnitude == 0.0:
        return "0"
    if magnitude < 1e-4 or magnitude >= 1e3:
        return f"{value:.3e}"
    return f"{value:.5f}"


def _macro(prefix: str, name: str, value: str | int) -> str:
    return rf"\newcommand{{\{prefix}{name}}}{{{value}}}"


def make_macros(
    cube: dict[str, Any], gradient: dict[str, Any], prefix: str
) -> str:
    if re.fullmatch(r"[A-Za-z]+", prefix) is None:
        raise ValueError("macro prefix must contain ASCII letters only")
    if cube.get("schema_version") != (
        "constraint-iclr-pdebench-enforcement-cube-analysis-v1"
    ):
        raise ValueError("unexpected cube-analysis schema")
    if gradient.get("schema_version") != (
        "constraint-iclr-gradient-coupling-analysis-v2"
    ):
        raise ValueError("unexpected gradient-analysis schema")
    if cube.get("integrity_gates_passed") is not True or gradient.get(
        "integrity_gates_passed"
    ) is not True:
        raise ValueError("refusing to report an analysis with failed integrity gates")
    if (
        cube.get("core_record_count") != 150
        or cube.get("derived_record_count") != 90
        or cube.get("checkpoint_count") != 120
        or gradient.get("record_count") != 60
    ):
        raise ValueError("fresh analyses do not have exact frozen coverage")

    primary = cube["primary"]
    interaction = primary["three_way_interaction"]
    effects = primary["effects"]
    cells = primary["cell_mean_conserving_rmse"]
    class_counts = Counter(
        str(cell["three_way_interaction"]["classification"])
        for cell in cube["all_cases"]
    )
    holm_significant = sum(
        float(cell["three_way_interaction"]["sign_flip_p_holm"]) < 0.05
        for cell in cube["all_cases"]
    )
    values: list[tuple[str, str | int]] = [
        ("CoreRecords", int(cube["core_record_count"])),
        ("DerivedRecords", int(cube["derived_record_count"])),
        ("Checkpoints", int(cube["checkpoint_count"])),
        ("PrimaryCase", str(primary["case"]).replace("_", r"\_")),
        ("PrimaryHorizon", int(primary["horizon"])),
        ("J", _number(float(interaction["mean"]))),
        ("JLow", _number(float(interaction["ci95"][0]))),
        ("JHigh", _number(float(interaction["ci95"][1]))),
        ("Sesoi", _number(float(interaction["sesoi"]))),
        ("JOverSesoi", f"{float(interaction['mean']) / float(interaction['sesoi']):.1f}"),
        ("Classification", CLASS_LABELS[str(interaction["classification"])]),
        ("HolmP", _number(float(interaction["sign_flip_p_holm"]))),
        ("HolmSignificantCells", holm_significant),
        ("MaterialCells", class_counts["material_nonadditivity"]),
        (
            "SmallerStatisticalCells",
            class_counts["statistical_nonadditivity_below_or_crossing_sesoi"],
        ),
        ("AdditiveCells", class_counts["practical_additivity"]),
        ("UnresolvedCells", class_counts["unresolved"]),
    ]
    cell_names = {
        "A00": "AZeroZero",
        "R00": "RZeroZero",
        "A01": "AZeroOne",
        "R01": "RZeroOne",
        "A10": "AOneZero",
        "R10": "ROneZero",
        "A11": "AOneOne",
        "R11": "ROneOne",
    }
    for cell, suffix in cell_names.items():
        values.append((suffix, _number(float(cells[cell]))))
    effect_names = {
        "I_bundle": "IBundle",
        "T0": "TZero",
        "T1": "TOne",
        "E0": "EZero",
        "E1": "EOne",
        "J": "JEffect",
        "phi_train": "PhiTrain",
        "phi_infer": "PhiInfer",
    }
    for key, suffix in effect_names.items():
        result = effects[key]
        values.extend(
            (
                (suffix, _number(float(result["mean"]))),
                (suffix + "Low", _number(float(result["ci"][0]))),
                (suffix + "High", _number(float(result["ci"][1]))),
            )
        )

    one_step = gradient["one_step"]["interaction"]
    association = gradient["primary_mechanistic_association"]
    final_training = gradient["primary_final_training_interaction"]
    values.extend(
        (
            ("GradientRecords", int(gradient["record_count"])),
            ("OneStepInteraction", _number(float(one_step["mean"]))),
            ("OneStepInteractionLow", _number(float(one_step["ci95"][0]))),
            ("OneStepInteractionHigh", _number(float(one_step["ci95"][1]))),
            ("FinalTrainingInteraction", _number(float(final_training["mean"]))),
            (
                "FinalTrainingInteractionLow",
                _number(float(final_training["ci95"][0])),
            ),
            (
                "FinalTrainingInteractionHigh",
                _number(float(final_training["ci95"][1])),
            ),
            ("MechanismRho", f"{float(association['rho']):.3f}"),
            ("MechanismRhoLow", f"{float(association['ci95'][0]):.3f}"),
            ("MechanismRhoHigh", f"{float(association['ci95'][1]):.3f}"),
            (
                "MechanismClassification",
                str(association["classification"]).replace("_", " "),
            ),
        )
    )
    return "\n".join(_macro(prefix, name, value) for name, value in values) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cube_analysis", type=Path)
    parser.add_argument("gradient_analysis", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--prefix", default="Cube")
    args = parser.parse_args()
    content = make_macros(
        _load(args.cube_analysis), _load(args.gradient_analysis), args.prefix
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
