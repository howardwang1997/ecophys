#!/usr/bin/env python3
"""Run the frozen Experiment 145 relaxation-attribution negative controls."""

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

from ecomd.research.relaxation_negative_controls import (
    fixed_clock_chain_witness,
    hidden_slow_mode_witness,
)

CONFIG_SCHEMA = "exp145-relaxation-negative-controls-config/v1"
RESULT_SCHEMA = "exp145-relaxation-negative-controls-result/v1"
FREEZE_SCHEMA = "exp145-implementation-freeze/v1"


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
        raise RuntimeError("Experiment 145 requires a clean committed checkout")


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
        raise RuntimeError("Experiment 145 freeze does not authorize the formal run")
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
        "witness_module": ROOT / "ecomd/research/relaxation_negative_controls.py",
        "focused_test": ROOT / "tests/test_relaxation_negative_controls.py",
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


def run_negative_controls(config: Mapping[str, object]) -> dict[str, object]:
    """Evaluate both preregistered non-adaptive fixtures."""

    if config.get("schema") != CONFIG_SCHEMA:
        raise ValueError(f"config schema must equal {CONFIG_SCHEMA}")
    tolerance = _number(config, "absolute_tolerance")
    slow = _mapping(config, "hidden_slow_mode")
    slow_result = hidden_slow_mode_witness(
        baseline_contraction=_number(slow, "baseline_contraction"),
        hidden_contraction=_number(slow, "hidden_contraction"),
        initial_amplitude=_number(slow, "initial_amplitude"),
        lags=_integer_sequence(slow, "lags"),
        absolute_tolerance=tolerance,
    )
    clock = _mapping(config, "fixed_clock_chain")
    clock_result = fixed_clock_chain_witness(
        _float_sequence(clock, "residual_path"),
        expected_dobrushin=_number(clock, "expected_dobrushin"),
        absolute_tolerance=tolerance,
    )

    slow_decision = (
        "CONFIRMED_HIDDEN_SLOW_MODE_EXCEEDANCE"
        if slow_result.matches_expected
        else "IMPLEMENTATION_OR_SPEC_FAILURE"
    )
    clock_decision = (
        "CONFIRMED_FIXED_CLOCK_REPRESENTATION"
        if clock_result.matches_expected
        else "IMPLEMENTATION_OR_SPEC_FAILURE"
    )
    overall = (
        "ATTRIBUTION_NOT_IDENTIFIED"
        if slow_result.matches_expected and clock_result.matches_expected
        else "IMPLEMENTATION_OR_SPEC_FAILURE"
    )
    return {
        "schema": RESULT_SCHEMA,
        "experiment": 145,
        "decision": overall,
        "candidate_admission": False,
        "novelty_pass": False,
        "adaptation_identified": False,
        "witnesses": {
            "hidden_slow_mode": {"decision": slow_decision, **slow_result.to_dict()},
            "fixed_clock_chain": {"decision": clock_decision, **clock_result.to_dict()},
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
    result = run_negative_controls(config)
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
        "workers_contacted": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["decision"] == "ATTRIBUTION_NOT_IDENTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

