from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

CLASS_LABELS = {
    "material_gauge_feedback": "material gauge feedback",
    "practically_negligible_gauge_feedback": "practically negligible gauge feedback",
    "unresolved": "unresolved",
}
ASSOCIATION_LABELS = {
    "positive_mechanism_support": "positive mechanism support",
    "not_supported": "not supported",
    "unresolved_constant_rank": "unresolved constant rank",
    "unresolved_bootstrap_degeneracy": "unresolved bootstrap degeneracy",
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("gauge-feedback analysis is not a JSON object")
    return value


def _number(value: float) -> str:
    if not math.isfinite(value):
        raise ValueError("refusing to format a non-finite value")
    magnitude = abs(value)
    if magnitude == 0.0:
        return "0"
    if magnitude < 1e-4 or magnitude >= 1e3:
        return f"{value:.3e}"
    return f"{value:.5f}"


def _macro(name: str, value: str | int) -> str:
    if re.fullmatch(r"[A-Za-z]+", name) is None:
        raise ValueError(f"invalid TeX macro name: {name}")
    return rf"\newcommand{{\{name}}}{{{value}}}"


def _summary(values: list[tuple[str, str | int]], prefix: str, summary: dict[str, Any]) -> None:
    low, high = (float(value) for value in summary["ci95"])
    values.extend(
        (
            (prefix, _number(float(summary["mean"]))),
            (prefix + "Low", _number(low)),
            (prefix + "High", _number(high)),
        )
    )


def make_macros(analysis: dict[str, Any], *, prefix: str = "Gauge") -> str:
    if re.fullmatch(r"[A-Za-z]+", prefix) is None:
        raise ValueError("macro prefix must contain ASCII letters only")
    schema = analysis.get("schema_version")
    if schema not in {
        "constraint-iclr-pdebench-gauge-feedback-analysis-v1",
        "constraint-iclr-pdebench-gauge-feedback-analysis-v2",
    }:
        raise ValueError("unexpected gauge-feedback analysis schema")
    if analysis.get("integrity_gates_passed") is not True:
        raise ValueError("refusing to report a failed gauge-feedback analysis")
    if analysis.get("record_count") != 60 or analysis.get("checkpoint_count") != 120:
        raise ValueError("gauge-feedback analysis lacks exact frozen coverage")
    primary = analysis["primary"]
    if primary.get("case") != "ood_r512":
        raise ValueError("gauge-feedback primary case changed")
    classification = str(primary["classification"])
    if classification not in CLASS_LABELS:
        raise ValueError("unknown gauge-feedback classification")
    association = analysis["secondary_final_harm_association"]
    association_class = str(association["classification"])
    if association_class not in ASSOCIATION_LABELS:
        raise ValueError("unknown gauge-feedback association classification")

    values: list[tuple[str, str | int]] = [
        ("Records", int(analysis["record_count"])),
        ("Checkpoints", int(analysis["checkpoint_count"])),
        ("PrimaryCase", str(primary["case"]).replace("_", r"\_")),
        ("Threshold", _number(float(analysis["practical_ratio_threshold"]))),
        ("Classification", CLASS_LABELS[classification]),
        ("AssociationClassification", ASSOCIATION_LABELS[association_class]),
    ]
    if schema.endswith("-v2"):
        identity = analysis.get("identity_integrity", {})
        contamination = float(identity["max_contamination_fraction"])
        contamination_limit = float(identity["relative_to_projected_baseline_max"])
        if contamination > contamination_limit:
            raise ValueError("gauge-feedback numerical contamination gate failed")
        values.extend(
            (
                ("MaxContamination", _number(contamination)),
                ("ContaminationLimit", _number(contamination_limit)),
                (
                    "MaterialCases",
                    sum(
                        str(cell["classification"]) == "material_gauge_feedback"
                        for cell in analysis["all_cases"]
                    ),
                ),
            )
        )
    _summary(values, "Ratio", primary["coordinate_average_feedback_ratio"])
    values.append(
        (
            "RatioOverThreshold",
            f"{float(primary['coordinate_average_feedback_ratio']['mean']) / float(analysis['practical_ratio_threshold']):.1f}",
        )
    )
    _summary(values, "FeedbackRMSE", primary["coordinate_average_feedback_rmse"])
    _summary(
        values,
        "AbsoluteRatio",
        primary["by_coordinate_feedback_ratio"]["hard_abs"],
    )
    _summary(
        values,
        "ResidualRatio",
        primary["by_coordinate_feedback_ratio"]["hard"],
    )
    if association.get("rho") is None:
        values.extend(
            (
                ("AssociationRho", "NA"),
                ("AssociationRhoLow", "NA"),
                ("AssociationRhoHigh", "NA"),
            )
        )
    else:
        interval = association.get("ci95")
        if not isinstance(interval, list) or len(interval) != 2:
            raise ValueError("estimable gauge-feedback association lacks a 95% interval")
        values.extend(
            (
                ("AssociationRho", _number(float(association["rho"]))),
                ("AssociationRhoLow", _number(float(interval[0]))),
                ("AssociationRhoHigh", _number(float(interval[1]))),
            )
        )
    return "\n".join(_macro(prefix + name, value) for name, value in values) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--prefix", default="Gauge")
    args = parser.parse_args()
    content = make_macros(_load(args.analysis), prefix=args.prefix)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
