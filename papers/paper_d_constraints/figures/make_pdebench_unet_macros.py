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
    "statistical_nonadditivity_below_or_crossing_sesoi": (
        "smaller statistical non-additivity"
    ),
    "practical_additivity": "practical additivity",
    "unresolved": "unresolved",
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


def _macro(name: str, value: str | int) -> str:
    if re.fullmatch(r"[A-Za-z]+", name) is None:
        raise ValueError(f"invalid TeX macro name: {name}")
    return rf"\newcommand{{\{name}}}{{{value}}}"


def make_macros(
    analysis: dict[str, Any], *, cube_analysis_sha256: str | None = None
) -> str:
    if analysis.get("schema_version") != (
        "constraint-iclr-pdebench-enforcement-cube-analysis-v1"
    ):
        raise ValueError("unexpected U-Net cube-analysis schema")
    if analysis.get("benchmark_id") != (
        "pdebench_advection_beta0.4_unet_factorial_v1"
    ):
        raise ValueError("unexpected U-Net benchmark identity")
    if analysis.get("integrity_gates_passed") is not True:
        raise ValueError("refusing to report an analysis with failed integrity gates")
    if (
        analysis.get("core_record_count") != 150
        or analysis.get("derived_record_count") != 90
        or analysis.get("checkpoint_count") != 120
        or len(analysis.get("all_cases", [])) != 12
    ):
        raise ValueError("U-Net analysis does not have exact frozen coverage")
    primary = analysis["primary"]
    if (str(primary["case"]), int(primary["horizon"])) != ("ood_r512", 16):
        raise ValueError("U-Net primary cell differs from the frozen cell")
    interaction = primary["three_way_interaction"]
    classification = str(interaction["classification"])
    if classification not in CLASS_LABELS:
        raise ValueError("unknown U-Net primary classification")
    counts = Counter(
        str(cell["three_way_interaction"]["classification"])
        for cell in analysis["all_cases"]
    )
    material_cells = counts["material_nonadditivity"]
    admission_passed = classification == "material_nonadditivity" and material_cells >= 6
    effects = primary["effects"]
    cells = primary["cell_mean_conserving_rmse"]
    values: list[tuple[str, str | int]] = [
        ("UNetCoreRecords", int(analysis["core_record_count"])),
        ("UNetDerivedRecords", int(analysis["derived_record_count"])),
        ("UNetCheckpoints", int(analysis["checkpoint_count"])),
        ("UNetJ", _number(float(interaction["mean"]))),
        ("UNetJLow", _number(float(interaction["ci95"][0]))),
        ("UNetJHigh", _number(float(interaction["ci95"][1]))),
        ("UNetSesoi", _number(float(interaction["sesoi"]))),
        (
            "UNetJOverSesoi",
            f"{abs(float(interaction['mean'])) / float(interaction['sesoi']):.1f}",
        ),
        ("UNetClassification", CLASS_LABELS[classification]),
        ("UNetHolmP", _number(float(interaction["sign_flip_p_holm"]))),
        ("UNetMaterialCells", material_cells),
        (
            "UNetSmallerStatisticalCells",
            counts["statistical_nonadditivity_below_or_crossing_sesoi"],
        ),
        ("UNetAdditiveCells", counts["practical_additivity"]),
        ("UNetUnresolvedCells", counts["unresolved"]),
        ("UNetAdmission", "passed" if admission_passed else "did not pass"),
        ("UNetCoreSHA", str(analysis["core_input_sha256"])[:12]),
        ("UNetCoreAnalysisSHA", str(analysis["core_analysis_sha256"])[:12]),
        ("UNetLockSHA", str(analysis["checkpoint_lock_sha256"])[:12]),
        ("UNetCubeSHA", str(analysis["derived_input_sha256"])[:12]),
    ]
    if cube_analysis_sha256 is not None:
        if re.fullmatch(r"[0-9a-f]{64}", cube_analysis_sha256) is None:
            raise ValueError("invalid U-Net cube-analysis SHA-256")
        values.append(("UNetCubeAnalysisSHA", cube_analysis_sha256[:12]))
    for key, suffix in (
        ("I_bundle", "IBundle"),
        ("T0", "TZero"),
        ("T1", "TOne"),
        ("E0", "EZero"),
        ("E1", "EOne"),
        ("phi_train", "PhiTrain"),
        ("phi_infer", "PhiInfer"),
    ):
        summary = effects[key]
        values.extend(
            (
                (f"UNet{suffix}", _number(float(summary["mean"]))),
                (f"UNet{suffix}Low", _number(float(summary["ci"][0]))),
                (f"UNet{suffix}High", _number(float(summary["ci"][1]))),
            )
        )
    for key, suffix in (
        ("A00", "AZeroZero"),
        ("R00", "RZeroZero"),
        ("A01", "AZeroOne"),
        ("R01", "RZeroOne"),
        ("A10", "AOneZero"),
        ("R10", "ROneZero"),
        ("A11", "AOneOne"),
        ("R11", "ROneOne"),
    ):
        values.append((f"UNet{suffix}", _number(float(cells[key]))))
    return "\n".join(_macro(name, value) for name, value in values) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cube_analysis", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    content = make_macros(
        _load(args.cube_analysis), cube_analysis_sha256=_sha256(args.cube_analysis)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")
    print(f"macros={args.output}")
    print(f"macros_sha256={_sha256(args.output)}")


if __name__ == "__main__":
    main()
