#!/usr/bin/env python3
"""Run the serial Experiment 148 repair of the generated RD preflight."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import resource
import subprocess
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from types import ModuleType
from typing import cast

_ACCELERATOR_ENV_BEFORE_GUARD = {
    variable: os.environ.get(variable) for variable in ("CUDA_VISIBLE_DEVICES", "ROCR_VISIBLE_DEVICES")
}
for _accelerator_variable in _ACCELERATOR_ENV_BEFORE_GUARD:
    os.environ[_accelerator_variable] = "-1"
for _thread_variable in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[_thread_variable] = "1"

import yaml

ROOT = Path(__file__).resolve().parents[2]
PARENT_RUNNER_PATH = ROOT / "experiments/147_generated_market_rule_feedback_rd/run_preflight.py"
sys.path.insert(0, str(ROOT))

EXECUTION_SCHEMA = "exp148-generated-market-rule-feedback-rd-serial-execution/v1"
FREEZE_SCHEMA = "exp148-generated-market-rule-feedback-rd-serial-freeze/v1"
RESULT_SCHEMA = "exp148-generated-market-rule-feedback-rd-serial-result/v1"
EXPERIMENT = 148
FitTask = tuple[dict[str, object], dict[str, object], float, float, int]
_NETWORK_AUDIT_EVENTS = {
    "socket.bind",
    "socket.connect",
    "socket.getaddrinfo",
    "socket.gethostbyaddr",
    "socket.gethostbyname",
    "socket.sendto",
}


def _network_audit_hook(event: str, _arguments: tuple[object, ...]) -> None:
    if event in _NETWORK_AUDIT_EVENTS:
        raise PermissionError(f"network disabled during Experiment 148: {event}")


def _install_network_guard() -> None:
    sys.addaudithook(_network_audit_hook)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _require_clean_repository() -> None:
    if _git("status", "--porcelain"):
        raise RuntimeError("Experiment 148 requires a clean committed checkout")


def _load_mapping(path: Path) -> dict[str, object]:
    raw: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must contain a mapping")
    return cast(dict[str, object], raw)


def _mapping(payload: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a mapping")
    return value


def _list(payload: Mapping[str, object], key: str) -> list[object]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    return value


def _number(payload: Mapping[str, object], key: str) -> float:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key} must be numeric")
    return float(value)


def _integer(payload: Mapping[str, object], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _string(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value


def _float_list(value: object, *, name: str) -> tuple[float, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a list")
    result: list[float] = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ValueError(f"{name} must contain numbers")
        result.append(float(item))
    return tuple(result)


def _scenario_mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ValueError("scenario entries must be mappings")
    return value


def _load_parent_runner() -> ModuleType:
    spec = importlib.util.spec_from_file_location("exp147_frozen_runner", PARENT_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the frozen Experiment 147 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _verify_parent_files(execution: Mapping[str, object]) -> dict[str, Path]:
    expected_keys = {
        "parent_config",
        "parent_preregistration",
        "parent_research_module",
        "parent_runner",
        "parent_failure_record",
    }
    paths: dict[str, Path] = {}
    for key in expected_keys:
        entry = _mapping(execution, key)
        path = (ROOT / _string(entry, "path")).resolve()
        if not path.is_relative_to(ROOT) or _sha256(path) != _string(entry, "sha256"):
            raise RuntimeError(f"Experiment 148 parent mismatch: {key}")
        paths[key] = path
    return paths


def _verify_freeze(
    freeze: Mapping[str, object], execution_path: Path, parent_paths: Mapping[str, Path]
) -> tuple[str, str]:
    if freeze.get("schema") != FREEZE_SCHEMA or freeze.get("formal_run_authorized") is not True:
        raise RuntimeError("Experiment 148 freeze does not authorize the formal run")
    preregistration_commit = _string(freeze, "preregistration_commit")
    implementation_commit = _string(freeze, "implementation_commit")
    for commit in (preregistration_commit, implementation_commit):
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
    files = _mapping(freeze, "files")
    expected_paths = {
        "execution_config": execution_path,
        "preregistration": execution_path.parent / "PREREGISTRATION.md",
        "readme": execution_path.parent / "README.md",
        "runner": Path(__file__).resolve(),
        "focused_test": ROOT / "tests/test_market_rule_feedback_serial.py",
        **parent_paths,
    }
    for key, expected_path in expected_paths.items():
        entry = _mapping(files, key)
        recorded_path = (ROOT / _string(entry, "path")).resolve()
        if recorded_path != expected_path.resolve() or _sha256(recorded_path) != _string(entry, "sha256"):
            raise RuntimeError(f"Experiment 148 frozen file mismatch: {key}")
    dependencies = _mapping(freeze, "dependencies")
    expected_python = _string(dependencies, "python")
    if platform.python_version() != expected_python:
        raise RuntimeError(
            f"Experiment 148 Python mismatch: {expected_python} != {platform.python_version()}"
        )
    for package in ("rdrobust", "numpy", "scipy", "pandas"):
        expected = _string(dependencies, package)
        actual = importlib.metadata.version(package)
        if expected != actual:
            raise RuntimeError(f"Experiment 148 dependency mismatch for {package}: {expected} != {actual}")
    return preregistration_commit, implementation_commit


def count_frozen_tasks(config: Mapping[str, object]) -> tuple[int, int]:
    """Return primary-fit and oracle task counts without executing a task."""

    replicates = _integer(config, "replicates")
    fit_cells = 0
    oracle_cells = 0
    for raw_scenario in _list(config, "null_scenarios"):
        scenario = _scenario_mapping(raw_scenario)
        cutoffs = _float_list(scenario.get("cutoffs"), name="cutoffs")
        fit_cells += len(cutoffs)
        if scenario.get("oracle") is True:
            oracle_cells += len(cutoffs)
    sigmas = _float_list(config.get("descriptive_power_sigmas"), name="descriptive_power_sigmas")
    for raw_scenario in _list(config, "effect_scenarios"):
        scenario = _scenario_mapping(raw_scenario)
        fit_cells += len(_float_list(scenario.get("cutoffs"), name="cutoffs")) * len(sigmas)
    return fit_cells * replicates, oracle_cells * replicates


def execute_serial_tasks(
    tasks: Sequence[FitTask], task_function: Callable[[FitTask], dict[str, object]]
) -> list[dict[str, object]]:
    """Execute every task in order and fail if control moves to another process."""

    controller_pid = os.getpid()
    results: list[dict[str, object]] = []
    for task in tasks:
        results.append(task_function(task))
        if os.getpid() != controller_pid:
            raise RuntimeError("Experiment 148 task left the controller process")
    return results


def run_serial_preflight(config: Mapping[str, object], execution: Mapping[str, object]) -> dict[str, object]:
    """Execute the exact Experiment 147 tasks serially in the controller process."""

    if execution.get("schema") != EXECUTION_SCHEMA or execution.get("backend") != "serial_in_process":
        raise ValueError("Experiment 148 execution contract is malformed")
    if _integer(execution, "controller_processes") != 1 or _integer(execution, "worker_processes") != 0:
        raise ValueError("Experiment 148 must have one controller and no workers")
    fit_tasks, oracle_tasks = count_frozen_tasks(config)
    if fit_tasks != _integer(execution, "expected_fit_tasks"):
        raise RuntimeError("Experiment 148 fit-task count differs from the preregistration")
    if oracle_tasks != _integer(execution, "expected_oracle_tasks"):
        raise RuntimeError("Experiment 148 oracle-task count differs from the preregistration")
    parent = _load_parent_runner()
    estimator = _mapping(config, "estimator")
    if importlib.metadata.version(_string(estimator, "package")) != _string(estimator, "version"):
        raise parent.FrozenSpecificationError("installed estimator version does not match the frozen version")
    replicates = _integer(config, "replicates")
    base_sigma = _number(config, "base_noise_sigma")
    effect_sigmas = _float_list(config.get("descriptive_power_sigmas"), name="descriptive_power_sigmas")
    cells: list[dict[str, object]] = []
    task_count = 0
    oracle_attempt_count = 0
    oracle_success_count = 0
    execution_pid = os.getpid()

    for raw_scenario in _list(config, "null_scenarios"):
        scenario = _scenario_mapping(raw_scenario)
        for cutoff in _float_list(scenario.get("cutoffs"), name="cutoffs"):
            tasks = [
                (dict(config), dict(scenario), cutoff, base_sigma, replicate)
                for replicate in range(replicates)
            ]
            results = execute_serial_tasks(tasks, parent._fit_task)
            task_count += len(results)
            if scenario.get("oracle") is True:
                oracle_attempt_count += len(results)
                oracle_success_count += sum(
                    item.get("oracle_failure") is False and "oracle" in item for item in results
                )
            cells.append(
                parent._cell_summary(
                    scenario_name=_string(scenario, "name"),
                    cutoff=cutoff,
                    sigma=base_sigma,
                    true_tau=0.0,
                    replicate_results=results,
                    config=config,
                    is_null=True,
                    is_descriptive=False,
                    oracle_required=scenario.get("oracle") is True,
                )
            )
    for raw_scenario in _list(config, "effect_scenarios"):
        scenario = _scenario_mapping(raw_scenario)
        for cutoff in _float_list(scenario.get("cutoffs"), name="cutoffs"):
            for sigma in effect_sigmas:
                tasks = [
                    (dict(config), dict(scenario), cutoff, sigma, replicate)
                    for replicate in range(replicates)
                ]
                results = execute_serial_tasks(tasks, parent._fit_task)
                task_count += len(results)
                cells.append(
                    parent._cell_summary(
                        scenario_name=_string(scenario, "name"),
                        cutoff=cutoff,
                        sigma=sigma,
                        true_tau=_number(scenario, "tau"),
                        replicate_results=results,
                        config=config,
                        is_null=False,
                        is_descriptive=sigma != base_sigma,
                        oracle_required=False,
                    )
                )

    if task_count != fit_tasks:
        raise RuntimeError(f"Experiment 148 completed {task_count} fit tasks instead of {fit_tasks}")
    if oracle_attempt_count != oracle_tasks:
        raise RuntimeError(
            f"Experiment 148 attempted {oracle_attempt_count} oracle tasks instead of {oracle_tasks}"
        )
    diagnostics = parent._diagnostics(config)
    gated_cells = [cell for cell in cells if cell["descriptive_only"] is False]
    zero_success_cells = [
        f"{cell['scenario']}@{cell['cutoff']}|sigma={cell['sigma']}"
        for cell in gated_cells
        if cell["successful_fits"] == 0
    ]
    if zero_success_cells:
        decision = "IMPLEMENTATION_OR_SPEC_FAILURE"
        overall_pass = False
    else:
        overall_pass = all(cell["gate_pass"] is True for cell in gated_cells) and diagnostics["gate_pass"] is True
        decision = "GENERATED_RD_PREFLIGHT_PASS" if overall_pass else "GENERATED_RD_PREFLIGHT_FAIL"
    return {
        "schema": RESULT_SCHEMA,
        "experiment": EXPERIMENT,
        "parent_experiment": 147,
        "decision": decision,
        "scientific_evidence": False,
        "real_data_authorized": False,
        "nmi_survivor": False,
        "cells": cells,
        "diagnostics": diagnostics,
        "zero_success_cells": zero_success_cells,
        "gate_summary": {
            "gated_cells": len(gated_cells),
            "passed_cells": sum(cell["gate_pass"] is True for cell in gated_cells),
            "diagnostics_pass": diagnostics["gate_pass"],
            "overall_pass": overall_pass,
        },
        "execution_audit": {
            "backend": "serial_in_process",
            "controller_pid": execution_pid,
            "worker_processes": 0,
            "fit_tasks_expected": fit_tasks,
            "fit_tasks_completed": task_count,
            "oracle_tasks_expected": oracle_tasks,
            "oracle_tasks_attempted": oracle_attempt_count,
            "oracle_tasks_successful": oracle_success_count,
            "oracle_tasks_failed": oracle_attempt_count - oracle_success_count,
        },
    }


def main() -> int:
    """Verify the repair freeze, execute once, and atomically create the result."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execution-config", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    _require_clean_repository()
    if args.output.exists():
        raise RuntimeError(f"refusing to overwrite formal artifact: {args.output}")
    execution = _load_mapping(args.execution_config)
    parent_paths = _verify_parent_files(execution)
    freeze = _load_mapping(args.freeze)
    preregistration_commit, implementation_commit = _verify_freeze(freeze, args.execution_config, parent_paths)
    resources = _mapping(execution, "resources")
    if resources.get("network_during_formal_run") is not False or resources.get("remote_workers_contacted") is not False:
        raise RuntimeError("Experiment 148 must disable network and remote workers")
    if _number(resources, "gpu_hours") != 0.0 or _string(resources, "device") != "mac_cpu":
        raise RuntimeError("Experiment 148 must remain Mac CPU with zero GPU-hours")
    for variable, original_value in _ACCELERATOR_ENV_BEFORE_GUARD.items():
        if original_value not in (None, "", "-1"):
            raise RuntimeError(f"{variable} exposed accelerators before the Experiment 148 guard")
        if os.environ.get(variable) != "-1":
            raise RuntimeError(f"{variable} guard was modified after import")

    _install_network_guard()
    config_path = parent_paths["parent_config"]
    config = _load_mapping(config_path)
    started = time.perf_counter()
    result = run_serial_preflight(config, execution)
    elapsed = time.perf_counter() - started
    max_wall_seconds = 60.0 * _number(resources, "max_wall_minutes")
    core_hour_upper_bound = elapsed / 3600.0
    max_core_hours = _number(resources, "max_cpu_core_hours")
    rss_divisor = 1024.0**3 if platform.system() == "Darwin" else 1024.0**2
    max_rss_gb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rss_divisor
    if elapsed > max_wall_seconds:
        result["decision"] = "IMPLEMENTATION_OR_SPEC_FAILURE"
        result["resource_failure"] = f"wall time {elapsed:.3f}s exceeds {max_wall_seconds:.3f}s"
    if core_hour_upper_bound > max_core_hours:
        result["decision"] = "IMPLEMENTATION_OR_SPEC_FAILURE"
        result["resource_failure"] = f"core-hour bound {core_hour_upper_bound:.6f} exceeds {max_core_hours:.6f}"
    if max_rss_gb > _number(resources, "max_ram_gb"):
        result["decision"] = "IMPLEMENTATION_OR_SPEC_FAILURE"
        result["resource_failure"] = f"RSS {max_rss_gb:.6f} GB exceeds the frozen RAM limit"

    dependencies = {
        package: importlib.metadata.version(package) for package in ("rdrobust", "numpy", "scipy", "pandas")
    }
    result["manifest"] = {
        "git_commit": _git("rev-parse", "HEAD"),
        "preregistration_commit": preregistration_commit,
        "implementation_commit": implementation_commit,
        "git_dirty_before_run": False,
        "execution_config_sha256": _sha256(args.execution_config),
        "parent_config_sha256": _sha256(config_path),
        "parent_preregistration_sha256": _sha256(parent_paths["parent_preregistration"]),
        "parent_research_module_sha256": _sha256(parent_paths["parent_research_module"]),
        "parent_runner_sha256": _sha256(parent_paths["parent_runner"]),
        "freeze_sha256": _sha256(args.freeze),
        "python": platform.python_version(),
        "dependencies": dependencies,
        "platform": platform.platform(),
        "seed": config.get("seed"),
        "wall_seconds": elapsed,
        "estimator_options": dict(_mapping(config, "estimator")),
    }
    result["resource_audit"] = {
        "market_data_files_read": 0,
        "fitrs_instrument_values_read": 0,
        "price_files_read": 0,
        "sealed_periods_opened": 0,
        "paid_data_read": 0,
        "network_access": False,
        "gpu_hours": 0.0,
        "device": "mac_cpu",
        "workers_contacted": 0,
        "controller_processes": 1,
        "worker_processes": 0,
        "numerical_threads": 1,
        "cpu_core_hour_upper_bound": core_hour_upper_bound,
        "max_rss_gb": max_rss_gb,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = args.output.with_suffix(args.output.suffix + ".tmp")
    if temporary_output.exists():
        raise RuntimeError(f"refusing stale partial output: {temporary_output}")
    temporary_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary_output.replace(args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["decision"] == "GENERATED_RD_PREFLIGHT_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
