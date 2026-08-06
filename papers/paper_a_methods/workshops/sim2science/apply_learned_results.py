"""Synchronize frozen learned-result fields into the Sim2Science manuscript."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
DEFAULT_RESULTS = REPO_ROOT / "experiments/127_workshop_claim_gates/LEARNED_RESULTS.json"
DEFAULT_PAPER = HERE / "main.tex"
MACRO_NAMES = (
    "learnedScorable",
    "learnedConfirmed",
    "learnedDelta",
    "learnedCI",
    "variantSigns",
)


def _signed(value: float) -> str:
    rendered = f"{value:+.2f}"
    return "0.00" if rendered == "-0.00" else rendered


def macro_values(payload: Mapping[str, Any]) -> dict[str, str]:
    primary = cast(Mapping[str, Any], payload["primary"])
    if int(primary["e1_total"]) != 7:
        raise ValueError("learned result must contain exactly seven primary checkpoints")
    scorable = int(primary["e1_scorable"])
    confirmed = int(primary["e1_heldout_gate_confirmed"])
    e3_scorable = int(primary["e3_scorable"])
    positive_e3 = int(primary["e3_positive_sign_count"])
    if not 0 <= confirmed <= scorable <= 7:
        raise ValueError("invalid primary scorable/confirmed counts")
    if not 0 <= positive_e3 <= e3_scorable <= 3:
        raise ValueError("invalid within-family sign counts")
    effect = primary["effect"]
    interval = primary["ci_95"]
    if effect is None or interval is None:
        raise ValueError("learned effect and interval are required before manuscript synchronization")
    if not isinstance(interval, list) or len(interval) != 2:
        raise ValueError("ci_95 must contain two endpoints")
    low, high = float(interval[0]), float(interval[1])
    point = float(effect)
    if low > high:
        raise ValueError("ci_95 endpoints are reversed")
    return {
        "learnedScorable": str(scorable),
        "learnedConfirmed": str(confirmed),
        "learnedDelta": rf"\ensuremath{{{_signed(point)}}}",
        "learnedCI": rf"\ensuremath{{[{_signed(low)},\,{_signed(high)}]}}",
        "variantSigns": rf"\ensuremath{{{positive_e3}/3}}",
    }


def synchronize_text(text: str, values: Mapping[str, str]) -> str:
    lines = text.splitlines(keepends=True)
    replacements = {name: 0 for name in MACRO_NAMES}
    for index, line in enumerate(lines):
        for name in MACRO_NAMES:
            prefix = rf"\newcommand{{\{name}}}"
            if line.startswith(prefix):
                newline = "\n" if line.endswith("\n") else ""
                lines[index] = f"{prefix}{{{values[name]}}}{newline}"
                replacements[name] += 1
    invalid = {name: count for name, count in replacements.items() if count != 1}
    if invalid:
        raise ValueError(f"expected exactly one definition per learned macro: {invalid}")
    return "".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    payload = cast(dict[str, Any], json.loads(args.results.read_text()))
    values = macro_values(payload)
    current = args.paper.read_text()
    synchronized = synchronize_text(current, values)
    if args.write:
        args.paper.write_text(synchronized)
    elif synchronized != current:
        raise SystemExit("manuscript learned-result macros are not synchronized; rerun with --write")
    primary = cast(dict[str, Any], payload["primary"])
    print(
        json.dumps(
            {
                "paper": str(args.paper),
                "written": bool(args.write),
                "macros": values,
                "expected_positive_direction_passes": bool(
                    primary["expected_positive_direction_passes"]
                ),
                "e3_same_positive_sign_2_of_3": bool(
                    primary["e3_same_positive_sign_2_of_3"]
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
