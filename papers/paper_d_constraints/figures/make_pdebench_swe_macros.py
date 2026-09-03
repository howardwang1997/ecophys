from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

CLASS_LABELS = {
    "material_nonadditivity": "material non-additivity",
    "statistical_nonadditivity_below_or_crossing_sesoi": ("smaller statistical non-additivity"),
    "practical_additivity": "practical additivity",
    "unresolved": "unresolved",
}
TRADEOFF_LABELS = {
    "conservation_gain_not_resolved": "conservation gain not resolved",
    "resolved_conservation_positivity_tradeoff": ("resolved conservation--positivity trade-off"),
    "resolved_conservation_positivity_synergy": ("resolved conservation--positivity synergy"),
    "conservation_gain_with_unresolved_positivity_effect": (
        "conservation gain with unresolved positivity effect"
    ),
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"analysis is not a JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _number(value: float) -> str:
    magnitude = abs(value)
    if magnitude == 0.0:
        return "0"
    if magnitude < 1e-4 or magnitude >= 1e3:
        return f"{value:.3e}"
    return f"{value:.5f}"


def _macro(prefix: str, name: str, value: str | int) -> str:
    if re.fullmatch(r"[A-Za-z]+", prefix + name) is None:
        raise ValueError(f"invalid TeX macro name: {prefix}{name}")
    return rf"\newcommand{{\{prefix}{name}}}{{{value}}}"


def _append_summary(values: list[tuple[str, str | int]], suffix: str, summary: dict[str, Any]) -> None:
    low, high = (float(value) for value in summary["ci"])
    values.extend(
        (
            (suffix, _number(float(summary["mean"]))),
            (suffix + "Low", _number(low)),
            (suffix + "High", _number(high)),
        )
    )


def make_macros(
    core: dict[str, Any],
    cube: dict[str, Any],
    *,
    core_analysis_sha256: str,
    prefix: str = "SWE",
) -> str:
    if re.fullmatch(r"[A-Za-z]+", prefix) is None:
        raise ValueError("macro prefix must contain ASCII letters only")
    if core.get("schema_version") != ("constraint-iclr-pdebench-swe-factorial-analysis-v1"):
        raise ValueError("unexpected SWE core-analysis schema")
    if cube.get("schema_version") != ("constraint-iclr-pdebench-swe-enforcement-cube-analysis-v1"):
        raise ValueError("unexpected SWE cube-analysis schema")
    if core.get("integrity_gates_passed") is not True or cube.get("integrity_gates_passed") is not True:
        raise ValueError("refusing to report an analysis with failed integrity gates")
    if (
        core.get("record_count") != 150
        or cube.get("core_record_count") != 150
        or cube.get("derived_record_count") != 90
        or cube.get("checkpoint_count") != 120
    ):
        raise ValueError("SWE analyses do not have exact frozen coverage")
    if cube.get("core_analysis_sha256") != core_analysis_sha256:
        raise ValueError("SWE cube is not bound to the supplied core analysis")
    if core.get("benchmark_id") != cube.get("benchmark_id"):
        raise ValueError("SWE analysis benchmark identities differ")

    core_primary = core["primary"]
    primary = cube["primary"]
    if (core_primary["case"], int(core_primary["horizon"])) != (
        primary["case"],
        int(primary["horizon"]),
    ):
        raise ValueError("SWE core and cube primary cells differ")
    interaction = primary["three_way_interaction"]
    classification = str(interaction["classification"])
    if classification not in CLASS_LABELS:
        raise ValueError("unknown SWE cube classification")
    tradeoff = cube["conservation_positivity_tradeoff"]
    tradeoff_class = str(tradeoff["classification"])
    if tradeoff_class not in TRADEOFF_LABELS:
        raise ValueError("unknown SWE conservation--positivity classification")
    counts = Counter(str(cell["three_way_interaction"]["classification"]) for cell in cube["all_cases"])
    if len(cube["all_cases"]) != 8:
        raise ValueError("expected all eight SWE resolution--horizon cells")

    low, high = (float(value) for value in interaction["ci95"])
    sesoi = float(interaction["sesoi"])
    values: list[tuple[str, str | int]] = [
        ("CoreRecords", int(core["record_count"])),
        ("DerivedRecords", int(cube["derived_record_count"])),
        ("Checkpoints", int(cube["checkpoint_count"])),
        ("PrimaryCase", str(primary["case"]).replace("_", r"\_")),
        ("PrimaryHorizon", int(primary["horizon"])),
        ("J", _number(float(interaction["mean"]))),
        ("JLow", _number(low)),
        ("JHigh", _number(high)),
        ("Sesoi", _number(sesoi)),
        ("JOverSesoi", f"{abs(float(interaction['mean'])) / sesoi:.1f}"),
        ("Classification", CLASS_LABELS[classification]),
        ("HolmP", _number(float(interaction["sign_flip_p_holm"]))),
        ("MaterialCells", counts["material_nonadditivity"]),
        (
            "SmallerStatisticalCells",
            counts["statistical_nonadditivity_below_or_crossing_sesoi"],
        ),
        ("AdditiveCells", counts["practical_additivity"]),
        ("UnresolvedCells", counts["unresolved"]),
        ("TradeoffCase", str(tradeoff["case"]).replace("_", r"\_")),
        ("TradeoffHorizon", int(tradeoff["horizon"])),
        ("TradeoffClassification", TRADEOFF_LABELS[tradeoff_class]),
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
        values.append((suffix, _number(float(primary["cell_mean_primary_metric"][cell]))))
    for key, suffix in (
        ("I_bundle", "IBundle"),
        ("T0", "TZero"),
        ("T1", "TOne"),
        ("E0", "EZero"),
        ("E1", "EOne"),
        ("phi_train", "PhiTrain"),
        ("phi_infer", "PhiInfer"),
    ):
        _append_summary(values, suffix, primary["effects"][key])
    for key, suffix in (
        ("conservation", "TradeoffConservation"),
        ("positivity", "TradeoffPositivity"),
        ("positivity_secondary", "TradeoffNegativeFraction"),
        ("dynamics", "TradeoffDynamics"),
    ):
        _append_summary(values, suffix, tradeoff["metrics"][key]["infer_free_train"])
    core_interaction = core_primary["interaction"]
    values.extend(
        (
            ("CoreInteraction", _number(float(core_interaction["mean"]))),
            ("CoreInteractionLow", _number(float(core_interaction["ci95"][0]))),
            ("CoreInteractionHigh", _number(float(core_interaction["ci95"][1]))),
            (
                "CoreClassification",
                CLASS_LABELS[str(core_interaction["classification"])],
            ),
        )
    )
    return "\n".join(_macro(prefix, name, value) for name, value in values) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("core_analysis", type=Path)
    parser.add_argument("cube_analysis", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--prefix", default="SWE")
    args = parser.parse_args()
    content = make_macros(
        _load(args.core_analysis),
        _load(args.cube_analysis),
        core_analysis_sha256=_sha256(args.core_analysis),
        prefix=args.prefix,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
