#!/usr/bin/env python3
"""Run the frozen Experiment 144 theory-reduction witnesses."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import cast

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ecomd.research.theory_witnesses import (
    fixed_operator_order_witness,
    stacked_observability_witness,
)

RESULT_SCHEMA = "exp144-theory-reduction-result/v1"
FREEZE_SCHEMA = "exp144-implementation-freeze/v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _require_clean_repository() -> None:
    if _git("status", "--porcelain"):
        raise RuntimeError("Experiment 144 requires a clean committed checkout")


def _load_mapping(path: Path) -> dict[str, object]:
    raw: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must contain a mapping")
    return cast(dict[str, object], raw)


def _mapping(payload: Mapping[str, object], key: str) -> dict[str, object]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a mapping")
    return cast(dict[str, object], value)


def _sequence(payload: Mapping[str, object], key: str) -> list[object]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    return cast(list[object], value)


def _number(payload: Mapping[str, object], key: str) -> float:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key} must be numeric")
    return float(value)


def _integer_sequence(payload: Mapping[str, object], key: str) -> tuple[int, ...]:
    values = _sequence(payload, key)
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise ValueError(f"{key} must contain integers")
    return tuple(cast(int, value) for value in values)


def _float_sequence(payload: Mapping[str, object], key: str) -> tuple[float, ...]:
    values = _sequence(payload, key)
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in values):
        raise ValueError(f"{key} must contain numbers")
    return tuple(float(cast(int | float, value)) for value in values)


def _verify_freeze(freeze: Mapping[str, object], config_path: Path) -> str:
    if freeze.get("schema") != FREEZE_SCHEMA or freeze.get("formal_run_authorized") is not True:
        raise RuntimeError("Experiment 144 freeze does not authorize the formal run")
    implementation_commit = freeze.get("implementation_commit")
    if not isinstance(implementation_commit, str):
        raise ValueError("freeze implementation_commit must be a string")
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", implementation_commit, "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    files = _mapping(freeze, "files")
    expected_paths = {
        "config": config_path,
        "runner": Path(__file__).resolve(),
        "witness_module": ROOT / "ecomd/research/theory_witnesses.py",
        "focused_test": ROOT / "tests/test_theory_witnesses.py",
    }
    for key, expected_path in expected_paths.items():
        entry = _mapping(files, key)
        recorded_path = entry.get("path")
        recorded_hash = entry.get("sha256")
        if not isinstance(recorded_path, str) or not isinstance(recorded_hash, str):
            raise ValueError(f"freeze files.{key} is malformed")
        resolved = (ROOT / recorded_path).resolve()
        if resolved != expected_path.resolve() or _sha256(resolved) != recorded_hash:
            raise RuntimeError(f"frozen file mismatch: {key}")
    return implementation_commit


def run_witnesses(config: Mapping[str, object]) -> dict[str, object]:
    """Evaluate both preregistered negative-control fixtures."""

    tolerance = _number(config, "absolute_tolerance")
    if tolerance <= 0.0:
        raise ValueError("absolute_tolerance must be positive")
    stacked = _mapping(config, "stacked_observability")
    matrices = _sequence(stacked, "matrices")
    stacked_result = stacked_observability_witness(
        matrices,
        expected_single_ranks=_integer_sequence(stacked, "expected_single_ranks"),
        expected_stacked_rank=int(_number(stacked, "expected_stacked_rank")),
        expected_stacked_eigenvalues=_float_sequence(stacked, "expected_stacked_eigenvalues"),
        absolute_tolerance=tolerance,
    )

    order = _mapping(config, "order_effect")
    order_result = fixed_operator_order_witness(
        order.get("initial_distribution"),
        order.get("operator_a"),
        order.get("operator_b"),
        order.get("observable"),
        expected_ab=_number(order, "expected_ab"),
        expected_ba=_number(order, "expected_ba"),
        expected_difference=_number(order, "expected_difference"),
        absolute_tolerance=tolerance,
    )
    w1_decision = (
        "CONFIRMED_GENERIC_REDUCTION" if stacked_result.matches_expected else "IMPLEMENTATION_OR_SPEC_FAILURE"
    )
    w2_decision = (
        "CONFIRMED_ORDER_EFFECT_WITHOUT_ADAPTATION"
        if order_result.matches_expected
        else "IMPLEMENTATION_OR_SPEC_FAILURE"
    )
    overall = (
        "NEGATIVE_CONTROLS_CONFIRMED"
        if stacked_result.matches_expected and order_result.matches_expected
        else "IMPLEMENTATION_OR_SPEC_FAILURE"
    )
    return {
        "schema": RESULT_SCHEMA,
        "experiment": 144,
        "decision": overall,
        "candidate_admission": False,
        "novelty_pass": False,
        "witnesses": {
            "stacked_observability": {"decision": w1_decision, **stacked_result.to_dict()},
            "fixed_operator_order": {"decision": w2_decision, **order_result.to_dict()},
        },
    }


def main() -> int:
    """Validate the freeze, execute once and write the immutable raw artifact."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    _require_clean_repository()
    if args.output.exists():
        raise RuntimeError(f"refusing to overwrite formal artifact: {args.output}")
    config = _load_mapping(args.config)
    freeze = _load_mapping(args.freeze)
    implementation_commit = _verify_freeze(freeze, args.config)
    started = time.perf_counter()
    result = run_witnesses(config)
    result["manifest"] = {
        "git_commit": _git("rev-parse", "HEAD"),
        "implementation_commit": implementation_commit,
        "git_dirty": False,
        "config_sha256": _sha256(args.config),
        "freeze_sha256": _sha256(args.freeze),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "seed": config.get("seed"),
        "wall_seconds": time.perf_counter() - started,
    }
    result["resource_audit"] = {
        "market_data_files_read": 0,
        "sealed_periods_opened": 0,
        "network_access": False,
        "gpu_hours": 0.0,
        "device": "mac_cpu",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["decision"] == "NEGATIVE_CONTROLS_CONFIRMED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
