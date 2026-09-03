from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PRIMARY_CASE = {
    "A": "ood_flat",
    "B": "ood_flat",
    "C": "ood_rich",
    "H": "ood_flat",
    "M2": "high_imbalance",
}
SYSTEM_ORDER = (
    "A:advection",
    "A:diffusion",
    "B:advection",
    "B:diffusion",
    "C:ad2d",
    "H:contraction_near",
    "H:contraction_strong",
    "M2:fifo_cda",
)
SYSTEM_LABEL = {
    "A:advection": "A advection",
    "A:diffusion": "A diffusion",
    "B:advection": "B advection",
    "B:diffusion": "B diffusion",
    "C:ad2d": "C ad2d",
    "H:contraction_near": "H near",
    "H:contraction_strong": "H strong",
    "M2:fifo_cda": "M2 FIFO",
}


def load_analysis(path: Path) -> dict[str, Any]:
    analysis = json.loads(path.read_text(encoding="utf-8"))
    if analysis.get("schema_version") != "constraint-iclr-analysis-amended-v1":
        raise ValueError("unexpected amended-analysis schema")
    integrity = analysis.get("integrity", {})
    if (
        integrity.get("record_count") != 1830
        or integrity.get("expected_record_count") != 1830
        or integrity.get("all_numeric_fields_finite") is not True
        or integrity.get("provenance_passed") is not True
        or integrity.get("lock_binding_passed") is not True
    ):
        raise ValueError("refusing to report an amended analysis without all integrity gates")
    if tuple(sorted(analysis.get("systems", {}))) != tuple(sorted(SYSTEM_ORDER)):
        raise ValueError("amended analysis does not contain the exact eight complete systems")
    return analysis


def _number(value: float) -> str:
    magnitude = abs(value)
    if magnitude == 0.0:
        return "0"
    if magnitude < 1e-3 or magnitude >= 1e3:
        return f"{value:.2e}".replace("e-0", "e-").replace("e+0", "e+")
    return f"{value:.4f}"


def _effect(result: dict[str, Any], interval: str) -> str:
    mean = float(result["paired_mean_difference"])
    low, high = (float(value) for value in result[interval])
    return f"{_number(mean)} [{_number(low)}, {_number(high)}]"


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def make_rows(analysis: dict[str, Any]) -> str:
    rows: list[str] = []
    for key in SYSTEM_ORDER:
        system = analysis["systems"][key]
        case = PRIMARY_CASE[str(system["family"])]
        parameterization = system["comparisons"]["free__free_res"]["effects"][case]["1"]
        enforcement = system["comparisons"]["free_res__hard"]["effects"][case]["1"]
        equivalent = bool(system["hard_free_res_equivalence"][case]["1"]["equivalent"])
        overlap = bool(
            system["comparisons"]["free__free_res"]["confirmation_overlap"]["passes"]
            and system["comparisons"]["free_res__hard"]["confirmation_overlap"]["passes"]
        )
        full_pass = bool(system["attribution"][case]["1"]["passes"])
        holm = float(analysis["primary_parameterization_holm"][key]["holm_pvalue"])
        rows.append(
            " & ".join(
                (
                    SYSTEM_LABEL[key],
                    _effect(parameterization, "ci95"),
                    _number(holm),
                    _effect(enforcement, "ci90"),
                    _yes_no(equivalent),
                    _yes_no(overlap),
                    _yes_no(full_pass),
                )
            )
            + r" \\"
        )
    return "\n".join(rows) + "\n" + r"\bottomrule" + "\n"


def make_macros(analysis: dict[str, Any]) -> str:
    nonzero = 0
    holm_significant = 0
    residual_favored = 0
    equivalent = 0
    full_pass = 0
    for key in SYSTEM_ORDER:
        system = analysis["systems"][key]
        case = PRIMARY_CASE[str(system["family"])]
        parameterization = system["comparisons"]["free__free_res"]["effects"][case]["1"]
        low, high = (float(value) for value in parameterization["ci95"])
        nonzero += low > 0.0 or high < 0.0
        residual_favored += float(parameterization["paired_mean_difference"]) > 0.0
        holm_significant += (
            float(analysis["primary_parameterization_holm"][key]["holm_pvalue"])
            < 0.05
        )
        equivalent += bool(system["hard_free_res_equivalence"][case]["1"]["equivalent"])
        full_pass += bool(system["attribution"][case]["1"]["passes"])
    values = {
        "SyntheticSystems": len(SYSTEM_ORDER),
        "SyntheticParameterizationNonzero": nonzero,
        "SyntheticParameterizationHolm": holm_significant,
        "SyntheticResidualFavored": residual_favored,
        "SyntheticEquivalent": equivalent,
        "SyntheticFullPass": full_pass,
    }
    return "\n".join(
        rf"\newcommand{{\{name}}}{{{value}}}" for name, value in values.items()
    ) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the integrity-gated amended synthetic appendix rows."
    )
    parser.add_argument("analysis", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--macros", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analysis = load_analysis(args.analysis)
    rows = make_rows(analysis)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rows, encoding="utf-8")
    if args.macros is not None:
        args.macros.parent.mkdir(parents=True, exist_ok=True)
        args.macros.write_text(make_macros(analysis), encoding="utf-8")


if __name__ == "__main__":
    main()
