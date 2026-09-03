from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

CASE_ORDER = {"id_r256": 0, "ood_r512": 1, "ood_r1024": 2}
CASE_LABELS = {
    "id_r256": "ID 256",
    "ood_r512": "OOD 512",
    "ood_r1024": "OOD 1024",
}
CLASS_LABELS = {
    "material_nonadditivity": "material",
    "statistical_nonadditivity_below_or_crossing_sesoi": "smaller",
    "practical_additivity": "additive",
    "unresolved": "unresolved",
}


def _number(value: float) -> str:
    if value == 0.0:
        return "0"
    if abs(value) < 1e-4:
        mantissa, exponent = f"{value:.2e}".split("e")
        return rf"${mantissa}\!\times\!10^{{{int(exponent)}}}$"
    return f"{value:.4f}"


def make_rows(analysis: dict[str, Any]) -> str:
    if analysis.get("schema_version") != (
        "constraint-iclr-pdebench-enforcement-cube-analysis-v1"
    ):
        raise ValueError("unexpected cube-analysis schema")
    if analysis.get("integrity_gates_passed") is not True:
        raise ValueError("refusing to report a failed analysis")
    cells = sorted(
        analysis["all_cases"],
        key=lambda cell: (CASE_ORDER[str(cell["case"])], int(cell["horizon"])),
    )
    if len(cells) != 12:
        raise ValueError("expected 12 frozen case-by-horizon cells")
    rows = []
    for cell in cells:
        result = cell["three_way_interaction"]
        mean = float(result["mean"])
        low, high = (float(value) for value in result["ci95"])
        normalized = mean / float(result["sesoi"])
        if abs(normalized) < 0.05:
            normalized = 0.0
        rows.append(
            " & ".join(
                (
                    CASE_LABELS[str(cell["case"])],
                    str(int(cell["horizon"])),
                    _number(mean),
                    f"[{_number(low)}, {_number(high)}]",
                    f"{normalized:.1f}",
                    CLASS_LABELS[str(result["classification"])],
                    _number(float(result["sign_flip_p_holm"])),
                )
            )
            + r" \\"
        )
    return "\n".join(rows) + "\n\\bottomrule\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    analysis = json.loads(args.analysis.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(make_rows(analysis), encoding="utf-8")


if __name__ == "__main__":
    main()
