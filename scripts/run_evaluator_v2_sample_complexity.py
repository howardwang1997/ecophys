"""Run the frozen synthetic sample-complexity calibration on CPU."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import yaml

from ecomd.data.yfinance_provenance import (
    canonical_payload_sha256,
    repository_state,
    sha256_file,
)
from ecomd.eval.evaluator_v2 import (
    SurrogateKind,
    assess_declared_relation,
    deterministic_seed,
    make_surrogate,
    safe_estimate,
)
from ecomd.eval.synthetic_dgps import dgp_registry, simulate_dgp

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_RESULT = REPO_ROOT / "results/evaluator_v2/feasibility_v1.json"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def run_condition(
    *,
    metric_name: str,
    length: int,
    condition_name: str,
    dgp_name: str,
    declared_relation: str,
    diagnostic_only: bool,
    primary_surrogate: SurrogateKind,
    replications: int,
    controls_per_path: int,
    root_seed: int,
    burn_in: int,
    registry: dict[str, dict[str, Any]],
    gates: dict[str, Any],
) -> dict[str, Any]:
    """Run one metric/length/DGP condition with deterministic paired controls."""
    real_estimates: list[float | None] = []
    control_estimates: list[list[float | None]] = []
    real_errors: list[str | None] = []
    control_errors: list[list[str | None]] = []
    for replication in range(replications):
        path_seed = deterministic_seed(
            root_seed,
            metric_name,
            length,
            condition_name,
            replication,
            "path",
        )
        try:
            path = simulate_dgp(
                dgp_name,
                length=length,
                burn_in=burn_in,
                seed=path_seed,
                registry=registry,
            )
            real_value, real_error = safe_estimate(metric_name, path)
        except Exception as exc:
            path = None
            real_value, real_error = None, f"{type(exc).__name__}: {exc}"
        path_controls: list[float | None] = []
        path_control_errors: list[str | None] = []
        for control_index in range(controls_per_path):
            value: float | None
            error: str | None
            if path is None:
                value, error = None, "PathUnavailable: signal/null path generation failed"
            else:
                control_seed = deterministic_seed(
                    root_seed,
                    metric_name,
                    length,
                    condition_name,
                    replication,
                    primary_surrogate,
                    control_index,
                )
                try:
                    control = make_surrogate(
                        path,
                        primary_surrogate,
                        seed=control_seed,
                    )
                    value, error = safe_estimate(metric_name, control)
                except Exception as exc:
                    value, error = None, f"{type(exc).__name__}: {exc}"
            path_controls.append(value)
            path_control_errors.append(error)
        real_estimates.append(real_value)
        real_errors.append(real_error)
        control_estimates.append(path_controls)
        control_errors.append(path_control_errors)

    complete_indices = [
        index
        for index, real_value in enumerate(real_estimates)
        if real_value is not None
        and all(value is not None for value in control_estimates[index])
    ]
    complete_fraction = len(complete_indices) / replications
    if complete_indices:
        complete_real = [
            float(cast(float, real_estimates[index])) for index in complete_indices
        ]
        complete_controls = [
            [float(value) for value in control_estimates[index] if value is not None]
            for index in complete_indices
        ]
        assessment = assess_declared_relation(
            complete_real,
            complete_controls,
            declared_relation=declared_relation,
            diagnostic_only=diagnostic_only,
            minimum_direction_fraction=float(
                gates["signal_direction_minimum_paired_path_fraction"]
            ),
            minimum_abs_effect_iqr=float(
                gates["signal_minimum_abs_median_effect_in_pooled_iqr_units"]
            ),
            maximum_abs_equivalence_effect_iqr=float(
                gates["equivalence_maximum_abs_median_effect_in_pooled_iqr_units"]
            ),
        )
    else:
        assessment = {
            "status": "no_complete_path_control_sets",
            "passed": None if diagnostic_only else False,
        }
    complete_pass = complete_fraction >= float(
        gates["complete_real_and_all_surrogate_fraction"]
    )
    relation_pass = assessment.get("passed") is True
    return {
        "condition": condition_name,
        "dgp": dgp_name,
        "declared_relation": declared_relation,
        "replications": replications,
        "controls_per_path": controls_per_path,
        "complete_path_control_sets": len(complete_indices),
        "complete_fraction": complete_fraction,
        "complete_gate_pass": complete_pass,
        "relation_gate_pass": None if diagnostic_only else relation_pass,
        "condition_gate_pass": None
        if diagnostic_only
        else complete_pass and relation_pass,
        "assessment": assessment,
        "real_estimates": real_estimates,
        "control_estimates": control_estimates,
        "real_errors": real_errors,
        "control_errors": control_errors,
    }


def evaluate_protocol(protocol: dict[str, Any]) -> dict[str, Any]:
    """Evaluate every frozen metric, length, signal DGP, and null DGP."""
    monte_carlo = _mapping(protocol["monte_carlo"], "monte_carlo")
    tests = _mapping(protocol["metric_tests"], "metric_tests")
    gates = _mapping(protocol["gates"], "gates")
    registry = dgp_registry(protocol["dgp"])
    lengths = [int(str(value)) for value in cast(list[object], monte_carlo["lengths"])]
    replications = int(monte_carlo["replications_per_length"])
    controls_per_path = int(monte_carlo["surrogate_replicates_per_path"])
    root_seed = int(monte_carlo["root_seed"])
    burn_in = int(monte_carlo["burn_in"])
    cells: dict[str, dict[str, Any]] = {}
    decisions: dict[str, dict[str, Any]] = {}
    for metric_name, raw_spec in tests.items():
        spec = _mapping(raw_spec, f"metric_tests.{metric_name}")
        floor = int(spec["analytic_min_length"])
        diagnostic_only = bool(spec.get("diagnostic_only", False))
        surrogate = cast(SurrogateKind, str(spec["primary_surrogate"]))
        cells[metric_name] = {}
        for length in lengths:
            signal = run_condition(
                metric_name=metric_name,
                length=length,
                condition_name="signal",
                dgp_name=str(spec["signal_dgp"]),
                declared_relation=str(spec["signal_relation"]),
                diagnostic_only=diagnostic_only,
                primary_surrogate=surrogate,
                replications=replications,
                controls_per_path=controls_per_path,
                root_seed=root_seed,
                burn_in=burn_in,
                registry=registry,
                gates=gates,
            )
            null = run_condition(
                metric_name=metric_name,
                length=length,
                condition_name="null",
                dgp_name=str(spec["null_dgp"]),
                declared_relation=str(gates["null_relation"]),
                diagnostic_only=False,
                primary_surrogate=surrogate,
                replications=replications,
                controls_per_path=controls_per_path,
                root_seed=root_seed,
                burn_in=burn_in,
                registry=registry,
                gates={
                    **gates,
                    "equivalence_maximum_abs_median_effect_in_pooled_iqr_units": gates[
                        "null_maximum_abs_median_effect_in_pooled_iqr_units"
                    ],
                },
            )
            gate_used = length >= floor and not diagnostic_only
            cell_pass = bool(
                gate_used
                and signal["condition_gate_pass"] is True
                and null["condition_gate_pass"] is True
            )
            cells[metric_name][str(length)] = {
                "analytic_min_length": floor,
                "formal_gate_used": gate_used,
                "formal_cell_pass": cell_pass if gate_used else None,
                "signal": signal,
                "null": null,
            }

        eligible_lengths = [length for length in lengths if length >= floor]
        if diagnostic_only:
            decisions[metric_name] = {
                "diagnostic_only": True,
                "admissible_minimum_length": None,
                "metric_admissible": None,
                "reason": "diagnostic_only_no_admissibility_decision",
            }
            continue
        minimum = suffix_admissible_minimum(
            eligible_lengths,
            {
                length: cells[metric_name][str(length)]["formal_cell_pass"] is True
                for length in eligible_lengths
            },
        )
        decisions[metric_name] = {
            "diagnostic_only": False,
            "analytic_min_length": floor,
            "eligible_grid_lengths": eligible_lengths,
            "passing_grid_lengths": [
                length
                for length in eligible_lengths
                if cells[metric_name][str(length)]["formal_cell_pass"] is True
            ],
            "admissible_minimum_length": minimum,
            "metric_admissible": minimum is not None,
            "suffix_stability_required": True,
        }
    return {
        "cells": cells,
        "decisions": decisions,
        "admissible_metrics": {
            name: decision["admissible_minimum_length"]
            for name, decision in decisions.items()
            if decision["metric_admissible"] is True
        },
    }


def suffix_admissible_minimum(
    eligible_lengths: list[int],
    pass_by_length: dict[int, bool],
) -> int | None:
    """Return the first grid length whose entire remaining suffix passes."""
    if not eligible_lengths or sorted(set(eligible_lengths)) != eligible_lengths:
        raise ValueError("eligible lengths must be sorted, unique, and non-empty")
    if set(pass_by_length) != set(eligible_lengths):
        raise ValueError("pass registry must match eligible lengths exactly")
    for index, length in enumerate(eligible_lengths):
        if all(pass_by_length[candidate] for candidate in eligible_lengths[index:]):
            return length
    return None


def run(protocol_path: Path, output_path: Path) -> dict[str, Any]:
    """Run from a clean pushed commit and atomically write the formal result."""
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite formal output: {output_path}")
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    if temporary.exists():
        raise FileExistsError(f"refusing to overwrite stale temporary: {temporary}")
    state = repository_state(REPO_ROOT)
    if not state["clean"]:
        raise RuntimeError("formal sample-complexity run requires a clean worktree")
    upstream = subprocess.run(
        ["git", "rev-parse", "@{u}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if upstream != state["git_sha"]:
        raise RuntimeError("formal sample-complexity source commit must be pushed")
    protocol = _load_yaml_object(protocol_path)
    compute = _mapping(protocol["compute"], "compute")
    if compute != {
        "cpu_only": True,
        "gpu_forbidden": True,
        "paid_data_forbidden": True,
        "h20_forbidden": True,
    }:
        raise ValueError("compute policy differs from the frozen contract")
    source_result = _load_json_object(SOURCE_RESULT)
    contract = _mapping(protocol["contract"], "contract")
    if sha256_file(SOURCE_RESULT) != contract["source_feasibility_result_file_sha256"]:
        raise ValueError("source feasibility result file hash mismatch")
    if canonical_payload_sha256(source_result) != contract[
        "source_feasibility_result_canonical_sha256"
    ]:
        raise ValueError("source feasibility result canonical hash mismatch")
    started = _utc_now()
    evaluation = evaluate_protocol(protocol)
    finished = _utc_now()
    payload: dict[str, Any] = {
        "schema_version": 1,
        "status": "formal_evaluator_v2_sample_complexity_complete",
        "contract": {
            "name": contract["name"],
            "version": contract["version"],
            "purpose": contract["purpose"],
        },
        "run": {
            "started_at_utc": started,
            "finished_at_utc": finished,
            "command_template": (
                "conda run -n ecophys python -m scripts.run_evaluator_v2_sample_complexity "
                "--output <fresh-result.json>"
            ),
            "cpu_only": True,
            "gpu_used": False,
        },
        "repository": {**state, "upstream_sha": upstream},
        "bindings": {
            "protocol_path": str(protocol_path.relative_to(REPO_ROOT)),
            "protocol_sha256": sha256_file(protocol_path),
            "source_feasibility_result_path": str(SOURCE_RESULT.relative_to(REPO_ROOT)),
            "source_feasibility_result_file_sha256": sha256_file(SOURCE_RESULT),
            "source_feasibility_result_canonical_sha256": source_result[
                "canonical_payload_sha256"
            ],
        },
        "code": {
            "evaluator_v2_sha256": sha256_file(
                REPO_ROOT / "ecomd/eval/evaluator_v2.py"
            ),
            "synthetic_dgps_sha256": sha256_file(
                REPO_ROOT / "ecomd/eval/synthetic_dgps.py"
            ),
            "stylized_facts_sha256": sha256_file(
                REPO_ROOT / "ecomd/eval/stylized_facts.py"
            ),
            "runner_sha256": sha256_file(Path(__file__).resolve()),
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": importlib.metadata.version("numpy"),
            "scipy": importlib.metadata.version("scipy"),
            "arch": importlib.metadata.version("arch"),
        },
        "evaluation": evaluation,
    }
    payload["canonical_payload_sha256"] = canonical_payload_sha256(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(output_path)
    return payload


def _mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return cast(dict[str, Any], value)


def _load_json_object(path: Path) -> dict[str, Any]:
    return _mapping(json.loads(path.read_text()), str(path))


def _load_yaml_object(path: Path) -> dict[str, Any]:
    return _mapping(yaml.safe_load(path.read_text()), str(path))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--protocol",
        type=Path,
        default=REPO_ROOT / "configs/evaluator_v2/sample_complexity_v1.yaml",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = run(args.protocol.resolve(), args.output.resolve())
    print(
        json.dumps(
            {
                "admissible_metrics": payload["evaluation"]["admissible_metrics"],
                "canonical_payload_sha256": payload["canonical_payload_sha256"],
                "output": str(args.output.resolve()),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
