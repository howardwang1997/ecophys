#!/usr/bin/env python3
"""Run the frozen Experiment 147 generated market-rule feedback RD preflight."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import subprocess
import sys
import time
from collections.abc import Mapping
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import cast

for _thread_variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_thread_variable] = "1"

import numpy as np
import scipy
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ecomd.research.market_rule_feedback_preflight import (
    FrozenSpecificationError,
    bias_bound_oracle,
    differential_attrition_detected,
    distinct_mass_points_by_side,
    fit_rdrobust,
    generate_panel,
    rng_for_stream,
    shared_rule_reason,
    sorting_detected,
    tick_first_stage,
    wilson_interval,
)

CONFIG_SCHEMA = "exp147-generated-market-rule-feedback-rd/v1"
RESULT_SCHEMA = "exp147-generated-market-rule-feedback-rd-result/v1"
FREEZE_SCHEMA = "exp147-generated-market-rule-feedback-rd-freeze/v1"
EXPERIMENT = 147
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
        raise PermissionError(f"network disabled during Experiment 147: {event}")


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
        raise RuntimeError("Experiment 147 requires a clean committed checkout")


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


def _verify_freeze(freeze: Mapping[str, object], config_path: Path) -> tuple[str, str]:
    if freeze.get("schema") != FREEZE_SCHEMA or freeze.get("formal_run_authorized") is not True:
        raise RuntimeError("Experiment 147 freeze does not authorize the formal run")
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
        "config": config_path,
        "preregistration": config_path.parent / "PREREGISTRATION.md",
        "readme": config_path.parent / "README.md",
        "runner": Path(__file__).resolve(),
        "research_module": ROOT / "ecomd/research/market_rule_feedback_preflight.py",
        "focused_test": ROOT / "tests/test_market_rule_feedback_preflight.py",
        "project_metadata": ROOT / "pyproject.toml",
    }
    for key, expected_path in expected_paths.items():
        entry = _mapping(files, key)
        recorded_path = _string(entry, "path")
        recorded_hash = _string(entry, "sha256")
        resolved = (ROOT / recorded_path).resolve()
        if resolved != expected_path.resolve() or _sha256(resolved) != recorded_hash:
            raise RuntimeError(f"frozen file mismatch: {key}")
    dependencies = _mapping(freeze, "dependencies")
    for package in ("rdrobust", "numpy", "scipy", "pandas"):
        expected = _string(dependencies, package)
        actual = importlib.metadata.version(package)
        if actual != expected:
            raise RuntimeError(f"frozen dependency mismatch for {package}: expected {expected}, got {actual}")
    return preregistration_commit, implementation_commit


def _scenario_mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ValueError("scenario entries must be mappings")
    return value


def _float_list(value: object, *, name: str) -> tuple[float, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a list")
    numbers: list[float] = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ValueError(f"{name} must contain numbers")
        numbers.append(float(item))
    return tuple(numbers)


def _fit_task(task: tuple[dict[str, object], dict[str, object], float, float, int]) -> dict[str, object]:
    config, scenario, cutoff, sigma, replicate = task
    panel = generate_panel(config, scenario, cutoff=cutoff, sigma=sigma, replicate=replicate)
    estimator = _mapping(config, "estimator")
    minimum_mass_points = _integer(config, "minimum_mass_points_per_side")
    result: dict[str, object] = {"replicate": replicate, "fit_failure": False, "oracle_failure": False}
    try:
        estimate = fit_rdrobust(panel, estimator, minimum_mass_points)
        result["estimate"] = estimate.to_dict()
    except FrozenSpecificationError:
        raise
    except Exception as error:
        result["fit_failure"] = True
        result["fit_error_type"] = type(error).__name__
        result["fit_error"] = str(error)
    if scenario.get("oracle") is True:
        try:
            quadratic = _number(scenario, "quadratic")
            oracle = bias_bound_oracle(
                panel,
                bandwidth=_number(config, "fixed_oracle_bandwidth"),
                curvature_bound=2.0 * abs(quadratic),
                sigma=sigma,
                confidence_level=_number(config, "confidence_level"),
                minimum_mass_points=minimum_mass_points,
            )
            result["oracle"] = oracle.to_dict()
        except Exception as error:
            result["oracle_failure"] = True
            result["oracle_error_type"] = type(error).__name__
            result["oracle_error"] = str(error)
    return result


def _cell_summary(
    *,
    scenario_name: str,
    cutoff: float,
    sigma: float,
    true_tau: float,
    replicate_results: list[dict[str, object]],
    config: Mapping[str, object],
    is_null: bool,
    is_descriptive: bool,
    oracle_required: bool,
) -> dict[str, object]:
    confidence = _number(config, "confidence_level")
    gates = _mapping(config, "gates")
    total = len(replicate_results)
    successful = [item for item in replicate_results if item["fit_failure"] is False]
    failure_count = total - len(successful)
    fit_failure_rate = failure_count / total
    estimates: list[float] = []
    p_values: list[float] = []
    coverage: list[bool] = []
    signs: list[bool] = []
    for item in successful:
        estimate = _mapping(item, "estimate")
        point = _number(estimate, "estimate")
        estimates.append(point)
        p_values.append(_number(estimate, "p_value"))
        coverage.append(_number(estimate, "ci_low") <= true_tau <= _number(estimate, "ci_high"))
        signs.append(point * true_tau > 0.0)
    summary: dict[str, object] = {
        "scenario": scenario_name,
        "cutoff": cutoff,
        "sigma": sigma,
        "true_tau": true_tau,
        "descriptive_only": is_descriptive,
        "replicates": total,
        "successful_fits": len(successful),
        "fit_failures": failure_count,
        "fit_failure_rate": fit_failure_rate,
        "fit_failure_types": sorted(
            {
                str(item["fit_error_type"])
                for item in replicate_results
                if item["fit_failure"] is True and "fit_error_type" in item
            }
        ),
        "failed_replicates": [
            _integer(item, "replicate") for item in replicate_results if item["fit_failure"] is True
        ],
    }
    gate_checks: dict[str, bool] = {
        "fit_failure_rate": fit_failure_rate <= _number(gates, "max_fit_failure_rate")
    }
    if successful:
        significant = sum(p_value < 0.05 for p_value in p_values)
        wilson_low, wilson_high = wilson_interval(significant, len(successful), confidence)
        absolute_median_bias = abs(float(np.median(np.asarray(estimates))) - true_tau)
        significant_rate = significant / len(successful)
        coverage_rate = sum(coverage) / len(successful)
        summary.update(
            {
                "significant_count": significant,
                "significant_rate": significant_rate,
                "significant_wilson_low": wilson_low,
                "significant_wilson_high": wilson_high,
                "coverage_count": sum(coverage),
                "coverage_rate": coverage_rate,
                "median_estimate": float(np.median(np.asarray(estimates))),
                "absolute_median_bias": absolute_median_bias,
            }
        )
        if is_null:
            gate_checks.update(
                {
                    "rejection_rate": significant_rate <= _number(gates, "null_max_rejection_rate"),
                    "coverage": coverage_rate >= _number(gates, "null_min_coverage"),
                    "wilson_rejection_upper": wilson_high <= _number(gates, "null_max_wilson_rejection_upper"),
                    "median_bias": absolute_median_bias <= _number(gates, "max_median_absolute_bias"),
                }
            )
        elif not is_descriptive:
            sign_accuracy = sum(signs) / len(successful)
            summary["sign_accuracy"] = sign_accuracy
            gate_checks.update(
                {
                    "power": significant_rate >= _number(gates, "effect_min_power"),
                    "wilson_power_lower": wilson_low >= _number(gates, "effect_min_wilson_power_lower"),
                    "sign_accuracy": sign_accuracy >= _number(gates, "effect_min_sign_accuracy"),
                    "median_bias": absolute_median_bias <= _number(gates, "max_median_absolute_bias"),
                }
            )
    else:
        gate_checks["successful_fits"] = False

    if oracle_required:
        oracle_successful = [item for item in replicate_results if item["oracle_failure"] is False and "oracle" in item]
        oracle_coverage = [
            _number(_mapping(item, "oracle"), "ci_low") <= true_tau <= _number(_mapping(item, "oracle"), "ci_high")
            for item in oracle_successful
        ]
        oracle_failures = total - len(oracle_successful)
        summary["oracle"] = {
            "successful": len(oracle_successful),
            "failures": oracle_failures,
            "failure_rate": oracle_failures / total,
            "coverage_count": sum(oracle_coverage),
            "coverage_rate": sum(oracle_coverage) / len(oracle_successful) if oracle_successful else None,
            "failure_types": sorted(
                {
                    str(item["oracle_error_type"])
                    for item in replicate_results
                    if item["oracle_failure"] is True and "oracle_error_type" in item
                }
            ),
            "failed_replicates": [
                _integer(item, "replicate") for item in replicate_results if item["oracle_failure"] is True
            ],
        }
        gate_checks["oracle_failure_rate"] = oracle_failures / total <= _number(gates, "oracle_max_failure_rate")
        gate_checks["oracle_coverage"] = bool(oracle_successful) and (
            sum(oracle_coverage) / len(oracle_successful) >= _number(gates, "oracle_min_coverage")
        )
    summary["gate_checks"] = gate_checks
    summary["gate_pass"] = all(gate_checks.values()) if not is_descriptive else None
    return summary


def _diagnostics(config: Mapping[str, object]) -> dict[str, object]:
    replicates = _integer(config, "replicates")
    seed = _integer(config, "seed")
    float_format = _string(config, "seed_float_format")
    alpha = _number(config, "diagnostic_alpha")
    bandwidth = _number(config, "fixed_oracle_bandwidth")
    sample_size = _integer(config, "n_candidates_per_year") * len(_list(config, "years"))
    sorting_hits = 0
    attrition_hits = 0
    sorting_p_values: list[float] = []
    attrition_p_values: list[float] = []
    attrition = _mapping(config, "differential_attrition")
    for replicate in range(replicates):
        sorting_rng = rng_for_stream(
            seed=seed,
            scenario="diagnostic_sorting",
            cutoff=10.0,
            sigma=0.0,
            replicate=replicate,
            float_format=float_format,
        )
        detected, p_value, _ = sorting_detected(
            sorting_rng,
            sample_size=sample_size,
            bandwidth=bandwidth,
            right_probability=_number(config, "sorting_right_probability"),
            alpha=alpha,
        )
        sorting_hits += int(detected)
        sorting_p_values.append(p_value)
        attrition_rng = rng_for_stream(
            seed=seed,
            scenario="diagnostic_differential_attrition",
            cutoff=10.0,
            sigma=0.0,
            replicate=replicate,
            float_format=float_format,
        )
        detected, p_value = differential_attrition_detected(
            attrition_rng,
            sample_size=sample_size,
            base_probability=_number(attrition, "base_probability"),
            right_side_increment=_number(attrition, "right_side_increment"),
            positive_shock_increment=_number(attrition, "positive_shock_increment"),
            alpha=alpha,
        )
        attrition_hits += int(detected)
        attrition_p_values.append(p_value)

    coarse_refusals = 0
    coarse_counts: list[tuple[int, int]] = []
    support = _float_list(config.get("ratio_support"), name="ratio_support")
    for replicate in range(replicates):
        rng = rng_for_stream(
            seed=seed,
            scenario="diagnostic_coarse_mass_points",
            cutoff=10.0,
            sigma=0.0,
            replicate=replicate,
            float_format=float_format,
        )
        ratio = rng.uniform(support[0], support[1], sample_size)
        increment = _number(config, "coarse_rounding_increment")
        rounded = np.round(10.0 * ratio / increment) * increment
        x = np.asarray(np.log(rounded / 10.0), dtype=np.float64)
        counts = distinct_mass_points_by_side(x.tolist(), bandwidth=bandwidth)
        coarse_counts.append(counts)
        coarse_refusals += int(min(counts) < _integer(config, "minimum_mass_points_per_side"))

    shared_cases = []
    shared_cutoffs = _float_list(config.get("shared_rule_cutoffs"), name="shared_rule_cutoffs")
    for cutoff in shared_cutoffs:
        reason = shared_rule_reason(cutoff, shared_cutoffs)
        shared_cases.append({"cutoff": cutoff, "reason": reason, "correct": reason is not None})

    tick_cases = []
    for raw_case in _list(config, "tick_first_stage_cases"):
        case = _scenario_mapping(raw_case)
        cutoff = _number(case, "cutoff")
        price = _number(case, "price")
        expected = case.get("expected_nonzero")
        if not isinstance(expected, bool):
            raise ValueError("expected_nonzero must be boolean")
        nonzero, left_tick, right_tick = tick_first_stage(cutoff, price)
        tick_cases.append(
            {
                "cutoff": cutoff,
                "price": price,
                "expected_nonzero": expected,
                "observed_nonzero": nonzero,
                "left_tick": left_tick,
                "right_tick": right_tick,
                "correct": nonzero == expected,
            }
        )

    sorting_rate = sorting_hits / replicates
    attrition_rate = attrition_hits / replicates
    coarse_rate = coarse_refusals / replicates
    shared_accuracy = sum(bool(case["correct"]) for case in shared_cases) / len(shared_cases)
    tick_accuracy = sum(bool(case["correct"]) for case in tick_cases) / len(tick_cases)
    gates = _mapping(config, "gates")
    checks = {
        "sorting_detection": sorting_rate >= _number(gates, "sorting_min_detection"),
        "attrition_detection": attrition_rate >= _number(gates, "attrition_min_detection"),
        "coarse_mass_point_refusal": coarse_rate == _number(gates, "deterministic_guard_accuracy"),
        "shared_rule_refusal": shared_accuracy == _number(gates, "deterministic_guard_accuracy"),
        "tick_first_stage_labels": tick_accuracy == _number(gates, "deterministic_guard_accuracy"),
    }
    return {
        "sorting": {
            "detections": sorting_hits,
            "replicates": replicates,
            "detection_rate": sorting_rate,
            "median_p_value": float(np.median(np.asarray(sorting_p_values))),
        },
        "differential_attrition": {
            "detections": attrition_hits,
            "replicates": replicates,
            "detection_rate": attrition_rate,
            "median_p_value": float(np.median(np.asarray(attrition_p_values))),
        },
        "coarse_mass_points": {
            "refusals": coarse_refusals,
            "replicates": replicates,
            "refusal_rate": coarse_rate,
            "unique_left_range": [min(value[0] for value in coarse_counts), max(value[0] for value in coarse_counts)],
            "unique_right_range": [min(value[1] for value in coarse_counts), max(value[1] for value in coarse_counts)],
        },
        "shared_rule_cutoff": {"cases": shared_cases, "accuracy": shared_accuracy},
        "zero_tick_first_stage": {"cases": tick_cases, "accuracy": tick_accuracy},
        "gate_checks": checks,
        "gate_pass": all(checks.values()),
    }


def run_preflight(config: Mapping[str, object]) -> dict[str, object]:
    """Execute all frozen stochastic and deterministic Experiment 147 cells."""

    if config.get("schema") != CONFIG_SCHEMA:
        raise ValueError(f"config schema must equal {CONFIG_SCHEMA}")
    estimator = _mapping(config, "estimator")
    if importlib.metadata.version(_string(estimator, "package")) != _string(estimator, "version"):
        raise FrozenSpecificationError("installed rdrobust version does not match the frozen estimator version")
    resources = _mapping(config, "resources")
    max_processes = _integer(resources, "max_processes")
    if max_processes < 2:
        raise ValueError("max_processes must permit one controller and at least one worker")
    worker_processes = max_processes - 1
    replicates = _integer(config, "replicates")
    if replicates != 300:
        raise FrozenSpecificationError("formal replicate count must remain 300")
    base_sigma = _number(config, "base_noise_sigma")
    effect_sigmas = _float_list(config.get("descriptive_power_sigmas"), name="descriptive_power_sigmas")
    tasks_by_cell: list[tuple[Mapping[str, object], float, float, bool, bool]] = []
    for raw_scenario in _list(config, "null_scenarios"):
        scenario = _scenario_mapping(raw_scenario)
        for cutoff in _float_list(scenario.get("cutoffs"), name="cutoffs"):
            tasks_by_cell.append((scenario, cutoff, base_sigma, True, False))
    for raw_scenario in _list(config, "effect_scenarios"):
        scenario = _scenario_mapping(raw_scenario)
        for cutoff in _float_list(scenario.get("cutoffs"), name="cutoffs"):
            for sigma in effect_sigmas:
                tasks_by_cell.append((scenario, cutoff, sigma, False, sigma != base_sigma))

    cells: list[dict[str, object]] = []
    try:
        with ProcessPoolExecutor(max_workers=worker_processes, initializer=_install_network_guard) as executor:
            for scenario, cutoff, sigma, is_null, is_descriptive in tasks_by_cell:
                task_list = [
                    (dict(config), dict(scenario), cutoff, sigma, replicate) for replicate in range(replicates)
                ]
                replicate_results = list(executor.map(_fit_task, task_list, chunksize=8))
                cells.append(
                    _cell_summary(
                        scenario_name=_string(scenario, "name"),
                        cutoff=cutoff,
                        sigma=sigma,
                        true_tau=_number(scenario, "tau") if not is_null else 0.0,
                        replicate_results=replicate_results,
                        config=config,
                        is_null=is_null,
                        is_descriptive=is_descriptive,
                        oracle_required=scenario.get("oracle") is True,
                    )
                )
    except FrozenSpecificationError as error:
        return {
            "schema": RESULT_SCHEMA,
            "experiment": EXPERIMENT,
            "decision": "IMPLEMENTATION_OR_SPEC_FAILURE",
            "reason": str(error),
            "cells": cells,
        }

    diagnostics = _diagnostics(config)
    gated_cells = [cell for cell in cells if cell["descriptive_only"] is False]
    zero_success_cells = [
        f"{cell['scenario']}@{cell['cutoff']}|sigma={cell['sigma']}"
        for cell in gated_cells
        if cell["successful_fits"] == 0
    ]
    if zero_success_cells:
        return {
            "schema": RESULT_SCHEMA,
            "experiment": EXPERIMENT,
            "decision": "IMPLEMENTATION_OR_SPEC_FAILURE",
            "reason": "zero successful fits in gated cells",
            "zero_success_cells": zero_success_cells,
            "cells": cells,
            "diagnostics": diagnostics,
        }
    all_pass = all(cell["gate_pass"] is True for cell in gated_cells) and diagnostics["gate_pass"] is True
    return {
        "schema": RESULT_SCHEMA,
        "experiment": EXPERIMENT,
        "decision": "GENERATED_RD_PREFLIGHT_PASS" if all_pass else "GENERATED_RD_PREFLIGHT_FAIL",
        "scientific_evidence": False,
        "real_data_authorized": False,
        "nmi_survivor": False,
        "cells": cells,
        "diagnostics": diagnostics,
        "gate_summary": {
            "gated_cells": len(gated_cells),
            "passed_cells": sum(cell["gate_pass"] is True for cell in gated_cells),
            "diagnostics_pass": diagnostics["gate_pass"],
            "overall_pass": all_pass,
        },
    }


def main() -> int:
    """Validate the freeze, execute once, and write the immutable raw artifact."""

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
    preregistration_commit, implementation_commit = _verify_freeze(freeze, args.config)
    resources = _mapping(config, "resources")
    if resources.get("network_during_formal_run") is not False or resources.get("remote_workers_contacted") is not False:
        raise RuntimeError("frozen resource boundary must disable network and remote workers")
    if _number(resources, "gpu_hours") != 0.0 or _string(resources, "device") != "mac_cpu":
        raise RuntimeError("frozen resource boundary must remain Mac CPU with zero GPU-hours")
    for variable in ("CUDA_VISIBLE_DEVICES", "ROCR_VISIBLE_DEVICES"):
        if os.environ.get(variable) not in (None, "", "-1"):
            raise RuntimeError(f"{variable} must hide accelerators for Experiment 147")

    _install_network_guard()
    started = time.perf_counter()
    result = run_preflight(config)
    elapsed = time.perf_counter() - started
    max_wall_seconds = 60.0 * _number(resources, "max_wall_minutes")
    processes = _integer(resources, "max_processes")
    worker_processes = processes - 1
    core_hour_upper_bound = elapsed * processes / 3600.0
    max_core_hours = _number(resources, "max_cpu_core_hours")
    if elapsed > max_wall_seconds:
        result["decision"] = "IMPLEMENTATION_OR_SPEC_FAILURE"
        result["resource_failure"] = f"wall time {elapsed:.3f}s exceeds {max_wall_seconds:.3f}s"
    if core_hour_upper_bound > max_core_hours:
        result["decision"] = "IMPLEMENTATION_OR_SPEC_FAILURE"
        result["resource_failure"] = (
            f"core-hour upper bound {core_hour_upper_bound:.6f} exceeds {max_core_hours:.6f}"
        )
    rss_divisor = 1024.0**3 if platform.system() == "Darwin" else 1024.0**2
    parent_rss_gb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rss_divisor
    child_rss_gb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / rss_divisor
    conservative_rss_gb = parent_rss_gb + worker_processes * child_rss_gb
    max_ram_gb = _number(resources, "max_ram_gb")
    if conservative_rss_gb > max_ram_gb:
        result["decision"] = "IMPLEMENTATION_OR_SPEC_FAILURE"
        result["resource_failure"] = (
            f"conservative RSS upper bound {conservative_rss_gb:.6f} GB exceeds {max_ram_gb:.6f} GB"
        )
    dependency_versions = {
        package: importlib.metadata.version(package) for package in ("rdrobust", "numpy", "scipy", "pandas")
    }
    result["manifest"] = {
        "git_commit": _git("rev-parse", "HEAD"),
        "preregistration_commit": preregistration_commit,
        "implementation_commit": implementation_commit,
        "git_dirty_before_run": False,
        "config_sha256": _sha256(args.config),
        "preregistration_sha256": _sha256(args.config.parent / "PREREGISTRATION.md"),
        "freeze_sha256": _sha256(args.freeze),
        "python": platform.python_version(),
        "dependencies": dependency_versions,
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
        "processes": processes,
        "controller_processes": 1,
        "worker_processes": worker_processes,
        "numerical_threads_per_process": 1,
        "cpu_core_hour_upper_bound": core_hour_upper_bound,
        "parent_max_rss_gb": parent_rss_gb,
        "child_max_rss_gb": child_rss_gb,
        "conservative_max_rss_gb": conservative_rss_gb,
        "scipy": scipy.__version__,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["decision"] == "GENERATED_RD_PREFLIGHT_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
