#!/usr/bin/env python3
"""Run the preregistered Experiment 143 aggregation repair."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ecomd.invariant_calibration.g0_gate_aggregation import (
    ResourceObservations,
    aggregate_positive_gates,
    has_positive_gate_namespace,
    resource_pass_gates,
)

RESULT_SCHEMA = "exp143-g0-aggregation-repair/v1"
EXPECTED_FIXTURE_SHA256 = "6da9c773512a7b7c642e8ef7c0ba1e231a59c720c8ba9a83618299660d19bf2e"
EXPECTED_CONTRACT_SHA256 = "96aed45ceba1e7c98bc3648c036c7302364bb4799ad0c6b2d9cd657c2a0a0f8e"
EXPECTED_PARENT_RUNNER_SHA256 = "3538ab7633e5a0a460e4bd7c88928637f505107d9ec0b4a1c05e024663f49d44"
EXPECTED_READY_HASH = "a29bbf74fd20e47bf80f2de529e4eef03f0254681052763341f8033924413343"


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _require_clean_repository() -> None:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        raise RuntimeError("Experiment 143 requires a clean committed checkout")


def _load_parent_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("exp142_frozen_runner", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the frozen exp142 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_parent_suite(parent_runner: Path, fixtures: Path) -> dict[str, object]:
    module = _load_parent_module(parent_runner)
    callback_object = getattr(module, "run_suite", None)
    if not callable(callback_object):
        raise RuntimeError("frozen exp142 runner has no callable run_suite")
    callback = cast(Callable[[Path], dict[str, object]], callback_object)
    result = callback(fixtures)
    if not isinstance(result, dict):
        raise RuntimeError("frozen exp142 run_suite returned a non-mapping")
    return result


def _mapping(payload: dict[str, object], key: str) -> dict[str, object]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"parent result {key!r} must be a mapping")
    return cast(dict[str, object], value)


def _resource_observations(parent: dict[str, object]) -> ResourceObservations:
    resource = _mapping(parent, "resource_audit")
    market_files = resource.get("market_data_files_read")
    sealed_periods = resource.get("sealed_periods_opened")
    gpu_hours = resource.get("gpu_hours")
    if isinstance(market_files, bool) or not isinstance(market_files, int):
        raise ValueError("parent market_data_files_read must be an integer")
    if isinstance(sealed_periods, bool) or not isinstance(sealed_periods, int):
        raise ValueError("parent sealed_periods_opened must be an integer")
    if isinstance(gpu_hours, bool) or not isinstance(gpu_hours, (int, float)):
        raise ValueError("parent gpu_hours must be numeric")
    return ResourceObservations(
        market_data_files_read=market_files,
        sealed_periods_opened=sealed_periods,
        gpu_hours=float(gpu_hours),
    )


def run_repair(fixtures: Path, parent_runner: Path) -> dict[str, object]:
    """Re-evaluate the frozen suite and aggregate only positive pass predicates."""
    fixture_hash = _file_sha256(fixtures)
    contract_hash = _file_sha256(ROOT / "ecomd/invariant_calibration/g0_contract.py")
    parent_runner_hash = _file_sha256(parent_runner)
    parent = _run_parent_suite(parent_runner, fixtures)
    parent_gates = _mapping(parent, "gates")
    semantic_groups = _mapping(parent, "semantic_equivalence_groups")
    ready_group = semantic_groups.get("ready-pair")
    observations = _resource_observations(parent)

    gates: dict[str, bool] = {
        "exact_expected_outcomes": parent_gates.get("exact_expected_outcomes") is True,
        "semantic_hash_invariance": parent_gates.get("semantic_hash_invariance") is True
        and ready_group == [EXPECTED_READY_HASH],
        "no_automated_novelty_pass": parent_gates.get("no_automated_novelty_pass") is True,
        "no_pass_state": parent_gates.get("no_pass_state") is True,
        "no_real_candidate": parent_gates.get("no_real_candidate") is True,
        "frozen_parent_inputs": fixture_hash == EXPECTED_FIXTURE_SHA256
        and contract_hash == EXPECTED_CONTRACT_SHA256
        and parent_runner_hash == EXPECTED_PARENT_RUNNER_SHA256,
    }
    gates.update(resource_pass_gates(observations))
    gates["positive_gate_namespace"] = has_positive_gate_namespace(gates)
    passed = aggregate_positive_gates(gates)

    return {
        "schema": RESULT_SCHEMA,
        "experiment": 143,
        "git_commit": _git_commit(),
        "parent_experiment": 142,
        "parent_decision_reproduced": parent.get("decision"),
        "fixture_file_sha256": fixture_hash,
        "contract_implementation_sha256": contract_hash,
        "parent_runner_sha256": parent_runner_hash,
        "cases": parent.get("cases"),
        "semantic_equivalence_groups": semantic_groups,
        "observations": observations.to_dict(),
        "gates": gates,
        "decision": "PASS_AGGREGATION_REPAIR" if passed else "FAIL_AGGREGATION_REPAIR",
        "scientific_status": "NO_ADMISSIBLE_REAL_CANDIDATE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=ROOT / "experiments/142_ncs_g0_reentry_contract/fixtures.yaml",
    )
    parser.add_argument(
        "--parent-runner",
        type=Path,
        default=ROOT / "experiments/142_ncs_g0_reentry_contract/run_contract.py",
    )
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.output.exists():
        raise FileExistsError(f"refusing to overwrite {arguments.output}")
    _require_clean_repository()
    result = run_repair(arguments.fixtures, arguments.parent_runner)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
