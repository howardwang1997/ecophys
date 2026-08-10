"""Run and merge the preregistered active-set Hawkes reference gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import subprocess
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, TypeAlias, cast

import numpy as np
import scipy
from numpy.typing import NDArray

from ecomd.observation.continuous_time import (
    ActiveSetNewtonResult,
    OptimizerStageResult,
    bound_constrained_kkt_diagnostics,
    exponential_trace_design,
    hawkes_objective_gradient,
    hawkes_objective_gradient_hessian,
    queue_hawkes_objective_gradient,
    run_active_set_newton,
    run_lbfgsb_stage,
    simulate_exponential_hawkes_cluster,
)

FloatArray: TypeAlias = NDArray[np.float64]
GradientObjective: TypeAlias = Callable[[FloatArray], tuple[float, FloatArray]]
HessianObjective: TypeAlias = Callable[[FloatArray], tuple[float, FloatArray, FloatArray]]
Bound: TypeAlias = tuple[float | None, float | None]

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = Path(__file__).with_name("REFERENCE_GATE_RESULTS.json")
PREREGISTRATION_COMMIT = "6d3940b9024b2eb05a7728b4ee5619ed603d1212"
FORMAL_ROOT_SEED = 140_202_608
FORMAL_ANCHOR_SEED = 140_202_609
SMOKE_ROOT_SEED = 140_202_610
SMOKE_ANCHOR_SEED = 140_202_611
FORBIDDEN_ROOT_SEEDS = (139_202_608, 139_202_609, 139_202_610)
FORMAL_REPLICATES = 16
SMOKE_REPLICATES = 2
IMMIGRANT = (0.35, 0.25)
BRANCHING = ((0.22, 0.08), (0.06, 0.18))
BETA = 1.3
FORMAL_BURN_START = -1_000.0
FORMAL_END = 30_000.0
SMOKE_BURN_START = -200.0
SMOKE_END = 3_000.0
ANCHOR_BURN_START = -500.0
ANCHOR_END = 5_000.0
ACTIVE_TOLERANCE = 1e-12
NEWTON_STOP_KKT = 1e-11
SELECTION_KKT = 1e-10
WARM_OPTIONS = {
    "maxiter": 1_000,
    "ftol": 1e-15,
    "gtol": 1e-9,
    "maxls": 100,
    "maxcor": 20,
}
NEWTON_OPTIONS = {
    "maxiter": 8,
    "stop_kkt": NEWTON_STOP_KKT,
    "active_tolerance": ACTIVE_TOLERANCE,
    "armijo_constant": 1e-4,
    "backtrack_factor": 0.5,
    "max_line_search_trials": 60,
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def _git_text(*arguments: str) -> str:
    result = subprocess.run(
        ("git", *arguments),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _environment() -> dict[str, Any]:
    return {
        "git_sha": _git_text("rev-parse", "HEAD"),
        "git_dirty": bool(_git_text("status", "--porcelain")),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "hostname": platform.node(),
        "cpu_count": os.cpu_count(),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
        "openblas_num_threads": os.environ.get("OPENBLAS_NUM_THREADS"),
        "mkl_num_threads": os.environ.get("MKL_NUM_THREADS"),
    }


def _protocol(*, formal: bool) -> dict[str, Any]:
    return {
        "experiment": 140,
        "formal": formal,
        "preregistration_commit": PREREGISTRATION_COMMIT,
        "root_seed": FORMAL_ROOT_SEED if formal else SMOKE_ROOT_SEED,
        "anchor_seed": FORMAL_ANCHOR_SEED if formal else SMOKE_ANCHOR_SEED,
        "replicates": FORMAL_REPLICATES if formal else SMOKE_REPLICATES,
        "immigrant": list(IMMIGRANT),
        "branching": [list(row) for row in BRANCHING],
        "beta": BETA,
        "burn_start": FORMAL_BURN_START if formal else SMOKE_BURN_START,
        "end": FORMAL_END if formal else SMOKE_END,
        "anchor_burn_start": ANCHOR_BURN_START,
        "anchor_end": ANCHOR_END,
        "split": {"burn": 0.10, "training": 0.50, "unused": 0.40},
        "active_tolerance": ACTIVE_TOLERANCE,
        "newton_stop_kkt": NEWTON_STOP_KKT,
        "selection_kkt": SELECTION_KKT,
        "warm_options": WARM_OPTIONS,
        "newton_options": NEWTON_OPTIONS,
        "starts": {"rate_zero": "rate, zeros", "positive": "0.5 * rate, 0.05"},
        "finite_difference": {
            "step": 1e-6,
            "gradient_maximum_error": 5e-7,
            "hessian_maximum_error": 5e-7,
            "symmetry_maximum_error": 1e-14,
            "bound_maximum_error": 1e-15,
        },
        "algebraic_equivalence": {
            "objective": 1e-12,
            "gradient_chain_rule": 1e-12,
            "inverse_parameter": 1e-14,
        },
        "objective_regression": 1e-13,
        "start_gap_maximum": 1e-11,
        "start_gap_median": 1e-12,
        "forbidden_root_seeds": list(FORBIDDEN_ROOT_SEEDS),
        "data_sources": ["generated"],
    }


def _stage_to_dict(result: OptimizerStageResult) -> dict[str, Any]:
    return {
        "parameters": result.parameters.tolist(),
        "objective": result.objective,
        "scipy_success": result.scipy_success,
        "iterations": result.iterations,
        "function_evaluations": result.function_evaluations,
        "raw_gradient_inf_norm": result.raw_gradient_inf_norm,
        "projected_gradient_inf_norm": result.projected_gradient_inf_norm,
        "complementarity_inf_norm": result.complementarity_inf_norm,
        "active_bounds": result.active_bounds,
        "message": result.message,
    }


def _newton_to_dict(result: ActiveSetNewtonResult) -> dict[str, Any]:
    return {
        "parameters": result.parameters.tolist(),
        "objective": result.objective,
        "success": result.success,
        "message": result.message,
        "raw_gradient_inf_norm": result.raw_gradient_inf_norm,
        "projected_gradient_inf_norm": result.projected_gradient_inf_norm,
        "complementarity_inf_norm": result.complementarity_inf_norm,
        "active_bounds": result.active_bounds,
        "trace": [
            {
                "index": iteration.index,
                "parameters": iteration.parameters.tolist(),
                "objective": iteration.objective,
                "raw_gradient_inf_norm": iteration.raw_gradient_inf_norm,
                "projected_gradient_inf_norm": iteration.projected_gradient_inf_norm,
                "complementarity_inf_norm": iteration.complementarity_inf_norm,
                "active_bounds": iteration.active_bounds,
                "hessian_condition_number": iteration.hessian_condition_number,
                "hessian_minimum_eigenvalue": iteration.hessian_minimum_eigenvalue,
                "step_size": iteration.step_size,
                "line_search_trials": iteration.line_search_trials,
                "directional_derivative": iteration.directional_derivative,
                "armijo_satisfied": iteration.armijo_satisfied,
            }
            for iteration in result.trace
        ],
    }


def _finite_difference_value(
    objective: GradientObjective,
    values: FloatArray,
    epsilon: float,
) -> FloatArray:
    result = np.empty_like(values)
    for index in range(values.size):
        plus = values.copy()
        minus = values.copy()
        plus[index] += epsilon
        minus[index] -= epsilon
        result[index] = (objective(plus)[0] - objective(minus)[0]) / (2.0 * epsilon)
    return result


def _finite_difference_gradient(
    objective: HessianObjective,
    values: FloatArray,
    epsilon: float,
) -> FloatArray:
    result = np.empty((values.size, values.size), dtype=np.float64)
    for index in range(values.size):
        plus = values.copy()
        minus = values.copy()
        plus[index] += epsilon
        minus[index] -= epsilon
        result[:, index] = (objective(plus)[1] - objective(minus)[1]) / (2.0 * epsilon)
    return result


def _self_check() -> dict[str, float]:
    features = np.asarray(((0.2, 0.5), (0.7, 0.1), (0.4, 0.3)), dtype=np.float64)
    integrated = np.asarray((1.4, 0.8), dtype=np.float64)
    values = np.asarray((0.8, 0.15, 0.12), dtype=np.float64)

    def hessian_objective(candidate: FloatArray) -> tuple[float, FloatArray, FloatArray]:
        return hawkes_objective_gradient_hessian(candidate, features, integrated, 3.2, 7)

    def gradient_objective(candidate: FloatArray) -> tuple[float, FloatArray]:
        value, gradient, _ = hessian_objective(candidate)
        return value, gradient

    _, gradient, hessian = hessian_objective(values)
    numerical_gradient = _finite_difference_value(gradient_objective, values, 1e-6)
    numerical_hessian = _finite_difference_gradient(hessian_objective, values, 1e-6)
    _, projected, complementarity, active = bound_constrained_kkt_diagnostics(
        np.asarray((0.8, 0.0, 0.2), dtype=np.float64),
        np.asarray((-0.3, 0.5, -0.4), dtype=np.float64),
        ((1e-12, None), (0.0, None), (0.0, None)),
        active_tolerance=ACTIVE_TOLERANCE,
    )
    expected = np.asarray((-0.3, 0.0, -0.4), dtype=np.float64)
    _, expected_projected, expected_complementarity, expected_active = (
        bound_constrained_kkt_diagnostics(
            np.asarray((0.8, 0.0, 0.2), dtype=np.float64),
            expected,
            ((1e-12, None), (0.0, None), (0.0, None)),
            active_tolerance=ACTIVE_TOLERANCE,
        )
    )
    return {
        "gradient_maximum_absolute_error": float(np.max(np.abs(gradient - numerical_gradient))),
        "hessian_maximum_absolute_error": float(np.max(np.abs(hessian - numerical_hessian))),
        "hessian_symmetry_maximum_absolute_error": float(np.max(np.abs(hessian - hessian.T))),
        "bound_case_maximum_absolute_error": max(
            abs(projected - expected_projected),
            abs(complementarity - expected_complementarity),
            float(abs(active - expected_active)),
        ),
    }


def _seed(replicate: int, *, formal: bool) -> int:
    count = FORMAL_REPLICATES if formal else SMOKE_REPLICATES
    root_seed = FORMAL_ROOT_SEED if formal else SMOKE_ROOT_SEED
    children = np.random.SeedSequence(root_seed).spawn(count)
    return int(children[replicate].generate_state(1, dtype=np.uint64)[0])


def _equivalence(
    parameters: FloatArray,
    event_features: FloatArray,
    integrated_features: FloatArray,
    interval_lengths: FloatArray,
    normalizer: int,
) -> dict[str, Any]:
    duration = float(np.sum(interval_lengths))
    direct_objective, direct_gradient = hawkes_objective_gradient(
        parameters,
        event_features,
        integrated_features,
        duration,
        normalizer,
    )
    combined_parameters = np.concatenate(([np.log(parameters[0])], parameters[1:]))
    all_queue = np.ones((interval_lengths.size, 1), dtype=np.float64)
    event_queue = np.ones((event_features.shape[0], 1), dtype=np.float64)
    combined_objective, combined_gradient = queue_hawkes_objective_gradient(
        combined_parameters,
        event_queue,
        event_features,
        all_queue,
        interval_lengths,
        integrated_features,
        normalizer,
    )
    expected_gradient = np.concatenate(
        ((parameters[0] * direct_gradient[0],), direct_gradient[1:]),
    )
    recovered = np.concatenate(((np.exp(combined_parameters[0]),), combined_parameters[1:]))
    return {
        "combined_parameters": combined_parameters.tolist(),
        "direct_objective": direct_objective,
        "combined_objective": combined_objective,
        "absolute_objective_difference": abs(combined_objective - direct_objective),
        "gradient_chain_rule_maximum_absolute_error": float(
            np.max(np.abs(combined_gradient - expected_gradient))
        ),
        "inverse_parameter_maximum_absolute_error": float(np.max(np.abs(recovered - parameters))),
    }


def _fit_start(
    initial: FloatArray,
    objective: GradientObjective,
    hessian_objective: HessianObjective,
    lower_bounds: FloatArray,
    event_features: FloatArray,
    integrated_features: FloatArray,
    interval_lengths: FloatArray,
    normalizer: int,
) -> dict[str, Any]:
    bounds: tuple[Bound, ...] = tuple((float(bound), None) for bound in lower_bounds)
    warm = run_lbfgsb_stage(
        objective,
        initial,
        bounds,
        maxiter=cast(int, WARM_OPTIONS["maxiter"]),
        ftol=float(WARM_OPTIONS["ftol"]),
        gtol=float(WARM_OPTIONS["gtol"]),
        maxls=cast(int, WARM_OPTIONS["maxls"]),
        maxcor=cast(int, WARM_OPTIONS["maxcor"]),
        active_tolerance=ACTIVE_TOLERANCE,
    )
    newton = run_active_set_newton(
        hessian_objective,
        warm.parameters,
        lower_bounds,
        maxiter=cast(int, NEWTON_OPTIONS["maxiter"]),
        stop_kkt=float(NEWTON_OPTIONS["stop_kkt"]),
        active_tolerance=float(NEWTON_OPTIONS["active_tolerance"]),
        armijo_constant=float(NEWTON_OPTIONS["armijo_constant"]),
        backtrack_factor=float(NEWTON_OPTIONS["backtrack_factor"]),
        max_line_search_trials=cast(int, NEWTON_OPTIONS["max_line_search_trials"]),
    )
    return {
        "initial_parameters": initial.tolist(),
        "warm": _stage_to_dict(warm),
        "newton": _newton_to_dict(newton),
        "objective_change_from_warm": newton.objective - warm.objective,
        "qualified": bool(
            np.isfinite(newton.objective)
            and newton.projected_gradient_inf_norm <= SELECTION_KKT
            and newton.complementarity_inf_norm <= SELECTION_KKT
        ),
        "equivalence": _equivalence(
            newton.parameters,
            event_features,
            integrated_features,
            interval_lengths,
            normalizer,
        ),
    }


def _fit_target(
    times: FloatArray,
    marks: NDArray[np.int64],
    traces: FloatArray,
    integrals: FloatArray,
    *,
    target: int,
    start: int,
    end: int,
) -> dict[str, Any]:
    interval_lengths = times[start:end] - times[start - 1 : end - 1]
    window_marks = marks[start:end]
    integrated_unscaled = np.sum(integrals[start:end], axis=0)
    duration = float(np.sum(interval_lengths))
    trace_scales = np.maximum(integrated_unscaled / duration, 1e-8)
    event_features = traces[start:end][window_marks == target] / trace_scales
    integrated_features = integrated_unscaled / trace_scales
    normalizer = end - start
    rate = event_features.shape[0] / duration

    def objective(values: FloatArray) -> tuple[float, FloatArray]:
        return hawkes_objective_gradient(
            values,
            event_features,
            integrated_features,
            duration,
            normalizer,
        )

    def hessian_objective(values: FloatArray) -> tuple[float, FloatArray, FloatArray]:
        return hawkes_objective_gradient_hessian(
            values,
            event_features,
            integrated_features,
            duration,
            normalizer,
        )

    lower = np.concatenate(([1e-12], np.zeros(trace_scales.size, dtype=np.float64)))
    starts = {
        "rate_zero": np.concatenate(([rate], np.zeros(trace_scales.size, dtype=np.float64))),
        "positive": np.concatenate(
            (([0.5 * rate], np.full(trace_scales.size, 0.05, dtype=np.float64))),
        ),
    }
    fitted = {
        name: _fit_start(
            initial,
            objective,
            hessian_objective,
            lower,
            event_features,
            integrated_features,
            interval_lengths,
            normalizer,
        )
        for name, initial in starts.items()
    }
    qualified = [
        (name, result)
        for name, result in fitted.items()
        if bool(result["qualified"])
    ]
    candidates = qualified or list(fitted.items())
    selected_name, selected = min(
        candidates,
        key=lambda item: float(cast(dict[str, Any], item[1]["newton"])["objective"]),
    )
    objectives = [float(cast(dict[str, Any], result["newton"])["objective"]) for result in fitted.values()]
    return {
        "target": target,
        "event_count": int(event_features.shape[0]),
        "trace_scales": trace_scales.tolist(),
        "starts": fitted,
        "both_starts_qualified": len(qualified) == 2,
        "selected_start": selected_name,
        "selected": cast(dict[str, Any], selected["newton"]),
        "start_objective_gap": abs(objectives[0] - objectives[1]),
    }


def _run_generated(
    replicate: int,
    *,
    formal: bool,
    anchor: bool = False,
) -> dict[str, Any]:
    started = time.perf_counter()
    if anchor:
        seed = FORMAL_ANCHOR_SEED if formal else SMOKE_ANCHOR_SEED
        burn_start = ANCHOR_BURN_START
        end_time = ANCHOR_END
    else:
        seed = _seed(replicate, formal=formal)
        burn_start = FORMAL_BURN_START if formal else SMOKE_BURN_START
        end_time = FORMAL_END if formal else SMOKE_END
    generator = np.random.default_rng(seed)
    times, marks = simulate_exponential_hawkes_cluster(
        IMMIGRANT,
        np.asarray(BRANCHING, dtype=np.float64),
        BETA,
        burn_start=burn_start,
        end_time=end_time,
        generator=generator,
    )
    train_start = int(0.10 * times.size)
    train_end = int(0.60 * times.size)
    traces, integrals = exponential_trace_design(times, marks, 2, (BETA,))
    result = {
        "replicate": None if anchor else replicate,
        "seed": seed,
        "shard": None if anchor else replicate % 2,
        "n_events": int(times.size),
        "train_start": train_start,
        "train_end": train_end,
        "mark_counts": np.bincount(marks, minlength=2).tolist(),
        "targets": [
            _fit_target(
                times,
                marks,
                traces,
                integrals,
                target=target,
                start=train_start,
                end=train_end,
            )
            for target in range(2)
        ],
    }
    if not anchor:
        result["elapsed_seconds"] = time.perf_counter() - started
    return result


def _validate_formal_environment(environment: dict[str, Any], expected_git_sha: str) -> None:
    if environment["git_sha"] != expected_git_sha:
        raise RuntimeError("formal git SHA does not match --expected-git-sha")
    if environment["git_dirty"]:
        raise RuntimeError("formal execution requires a clean worktree")
    if environment["cuda_visible_devices"] != "-1":
        raise RuntimeError("formal execution requires CUDA_VISIBLE_DEVICES=-1")
    for name in ("omp_num_threads", "openblas_num_threads", "mkl_num_threads"):
        if environment[name] != "1":
            raise RuntimeError(f"formal execution requires {name}=1")
    ancestry = subprocess.run(
        ("git", "merge-base", "--is-ancestor", PREREGISTRATION_COMMIT, expected_git_sha),
        cwd=ROOT,
        check=False,
    )
    if ancestry.returncode != 0:
        raise RuntimeError("implementation commit is not descended from the preregistration")


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    temporary.replace(path)


def _run_shard(
    shard: int,
    *,
    formal: bool,
    expected_git_sha: str | None,
    output: Path,
) -> dict[str, Any]:
    if shard not in (0, 1):
        raise ValueError("shard must be 0 or 1")
    environment = _environment()
    if formal:
        if expected_git_sha is None:
            raise RuntimeError("formal execution requires --expected-git-sha")
        _validate_formal_environment(environment, expected_git_sha)
    protocol = _protocol(formal=formal)
    count = FORMAL_REPLICATES if formal else SMOKE_REPLICATES
    replicates = tuple(index for index in range(count) if index % 2 == shard)
    started = time.perf_counter()
    records = [_run_generated(index, formal=formal) for index in replicates]
    anchor = _run_generated(0, formal=formal, anchor=True)
    result = {
        "experiment": 140,
        "title": "independent active-set Newton Hawkes reference gate",
        "formal": formal,
        "shard": {"index": shard, "n_shards": 2, "replicates": list(replicates)},
        "protocol": protocol,
        "protocol_hash": _canonical_hash(protocol),
        "environment": environment,
        "source_hashes": {
            "runner": _sha256(Path(__file__)),
            "continuous_time": _sha256(ROOT / "ecomd/observation/continuous_time.py"),
        },
        "data_sources": ["generated"],
        "real_data_loaded": False,
        "self_check": _self_check(),
        "records": records,
        "anchor": anchor,
        "anchor_hash": _canonical_hash(anchor),
        "elapsed_seconds": time.perf_counter() - started,
        "peak_rss_raw": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    _write_json(output, result)
    print(
        json.dumps(
            {
                "output": str(output),
                "formal": formal,
                "shard": shard,
                "records": len(records),
                "anchor_hash": result["anchor_hash"],
                "elapsed_seconds": result["elapsed_seconds"],
                "environment": environment,
                "protocol_hash": result["protocol_hash"],
                "self_check": result["self_check"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return result


def _finite_tree(value: Any) -> bool:
    if isinstance(value, dict):
        return all(_finite_tree(item) for item in value.values())
    if isinstance(value, list):
        return all(_finite_tree(item) for item in value)
    if isinstance(value, float):
        return bool(np.isfinite(value))
    return True


def _iter_targets(records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    return [target for record in records for target in record["targets"]]


def _iter_starts(records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    return [start for target in _iter_targets(records) for start in target["starts"].values()]


def _armijo_exact(start: dict[str, Any]) -> bool:
    trace = cast(list[dict[str, Any]], start["newton"]["trace"])
    for index, endpoint in enumerate(trace):
        if endpoint["step_size"] is None:
            if endpoint["armijo_satisfied"] is False:
                return False
            continue
        if endpoint["armijo_satisfied"] is not True or index + 1 >= len(trace):
            return False
        right = float(endpoint["objective"]) + NEWTON_OPTIONS["armijo_constant"] * float(
            endpoint["step_size"]
        ) * float(endpoint["directional_derivative"])
        if float(trace[index + 1]["objective"]) > right + 1e-15:
            return False
    return True


def _forbidden_child_seeds() -> set[int]:
    result = set(FORBIDDEN_ROOT_SEEDS)
    for root_seed in FORBIDDEN_ROOT_SEEDS:
        for child in np.random.SeedSequence(root_seed).spawn(FORMAL_REPLICATES):
            result.add(int(child.generate_state(1, dtype=np.uint64)[0]))
    return result


def _merge(paths: Sequence[Path], *, expected_git_sha: str, output: Path) -> dict[str, Any]:
    if len(paths) != 2:
        raise ValueError("merge requires exactly two shard paths")
    shards = [json.loads(path.read_text()) for path in paths]
    protocol = _protocol(formal=True)
    protocol_hash = _canonical_hash(protocol)
    expected_ownership = {0: list(range(0, FORMAL_REPLICATES, 2)), 1: list(range(1, FORMAL_REPLICATES, 2))}
    chronology = True
    seen_shards: set[int] = set()
    for shard in shards:
        index = int(shard["shard"]["index"])
        seen_shards.add(index)
        chronology &= bool(shard["formal"])
        chronology &= shard["protocol"] == protocol
        chronology &= shard["protocol_hash"] == protocol_hash
        chronology &= shard["shard"]["replicates"] == expected_ownership.get(index)
        chronology &= shard["environment"]["git_sha"] == expected_git_sha
        chronology &= shard["environment"]["git_dirty"] is False
        chronology &= shard["environment"]["cuda_visible_devices"] == "-1"
        chronology &= all(
            shard["environment"][name] == "1"
            for name in ("omp_num_threads", "openblas_num_threads", "mkl_num_threads")
        )
        chronology &= shard["data_sources"] == ["generated"]
        chronology &= shard["real_data_loaded"] is False
    chronology &= seen_shards == {0, 1}
    chronology &= shards[0]["source_hashes"] == shards[1]["source_hashes"]

    records = sorted(
        [record for shard in shards for record in shard["records"]],
        key=lambda record: int(record["replicate"]),
    )
    expected_seeds = [_seed(index, formal=True) for index in range(FORMAL_REPLICATES)]
    forbidden = _forbidden_child_seeds()
    isolation = (
        len(records) == FORMAL_REPLICATES
        and [record["replicate"] for record in records] == list(range(FORMAL_REPLICATES))
        and [record["seed"] for record in records] == expected_seeds
        and not any(int(record["seed"]) in forbidden for record in records)
    )
    checks = [shard["self_check"] for shard in shards]
    derivative = all(
        float(check["gradient_maximum_absolute_error"]) <= 5e-7
        and float(check["hessian_maximum_absolute_error"]) <= 5e-7
        and float(check["hessian_symmetry_maximum_absolute_error"]) <= 1e-14
        and float(check["bound_case_maximum_absolute_error"]) <= 1e-15
        for check in checks
    )
    targets = _iter_targets(records)
    starts = _iter_starts(records)
    newton_convergence = len(starts) == 64 and all(
        float(start["newton"]["projected_gradient_inf_norm"]) <= SELECTION_KKT
        and float(start["newton"]["complementarity_inf_norm"]) <= SELECTION_KKT
        for start in starts
    )
    monotone = len(starts) == 64 and all(
        float(start["newton"]["objective"]) <= float(start["warm"]["objective"]) + 1e-13
        and _armijo_exact(start)
        for start in starts
    )
    gaps = [float(target["start_objective_gap"]) for target in targets]
    start_robustness = (
        len(targets) == 32
        and all(bool(target["both_starts_qualified"]) for target in targets)
        and max(gaps, default=float("inf")) <= 1e-11
        and float(np.median(np.asarray(gaps, dtype=np.float64))) <= 1e-12
    )
    equivalence_records = [start["equivalence"] for start in starts]
    equivalence = len(equivalence_records) == 64 and all(
        float(record["absolute_objective_difference"]) <= 1e-12
        and float(record["gradient_chain_rule_maximum_absolute_error"]) <= 1e-12
        and float(record["inverse_parameter_maximum_absolute_error"]) <= 1e-14
        for record in equivalence_records
    )
    cross_node = (
        shards[0]["anchor_hash"] == shards[1]["anchor_hash"]
        and shards[0]["anchor"] == shards[1]["anchor"]
    )
    complete = (
        len(records) == FORMAL_REPLICATES
        and len(targets) == 32
        and len(starts) == 64
        and all(len(start["newton"]["trace"]) >= 1 for start in starts)
        and all("peak_rss_raw" in shard and "elapsed_seconds" in shard for shard in shards)
        and _finite_tree(records)
        and _finite_tree(checks)
    )
    hard_gates = {
        "chronology_and_provenance": chronology,
        "fresh_generated_isolation": isolation,
        "derivative_and_kkt_correctness": derivative,
        "newton_convergence": newton_convergence,
        "monotone_repair": monotone,
        "start_robustness": start_robustness,
        "algebraic_equivalence": equivalence,
        "cross_node_determinism": cross_node,
        "complete_unfavorable_reporting": complete,
    }
    projected = [float(start["newton"]["projected_gradient_inf_norm"]) for start in starts]
    complementarity = [float(start["newton"]["complementarity_inf_norm"]) for start in starts]
    objective_changes = [float(start["objective_change_from_warm"]) for start in starts]
    result = {
        "experiment": 140,
        "title": "independent active-set Newton Hawkes reference gate",
        "formal": True,
        "git_sha": expected_git_sha,
        "protocol": protocol,
        "protocol_hash": protocol_hash,
        "source_hashes": shards[0]["source_hashes"],
        "source_shards": [str(path) for path in paths],
        "source_environments": [shard["environment"] for shard in shards],
        "self_checks": checks,
        "records": records,
        "anchor_hash": shards[0]["anchor_hash"],
        "hard_gates": hard_gates,
        "all_hard_gates_pass": all(hard_gates.values()),
        "summary": {
            "n_streams": len(records),
            "n_targets": len(targets),
            "n_endpoints": len(starts),
            "qualified_endpoints": sum(bool(start["qualified"]) for start in starts),
            "maximum_projected_kkt": max(projected),
            "maximum_complementarity": max(complementarity),
            "maximum_start_objective_gap": max(gaps),
            "median_start_objective_gap": float(np.median(np.asarray(gaps, dtype=np.float64))),
            "maximum_objective_change_from_warm": max(objective_changes),
            "minimum_objective_change_from_warm": min(objective_changes),
            "maximum_equivalence_objective_error": max(
                float(record["absolute_objective_difference"]) for record in equivalence_records
            ),
            "maximum_equivalence_gradient_error": max(
                float(record["gradient_chain_rule_maximum_absolute_error"])
                for record in equivalence_records
            ),
            "maximum_inverse_parameter_error": max(
                float(record["inverse_parameter_maximum_absolute_error"])
                for record in equivalence_records
            ),
        },
        "total_worker_seconds": sum(float(shard["elapsed_seconds"]) for shard in shards),
        "peak_rss_raw": [shard["peak_rss_raw"] for shard in shards],
    }
    _write_json(output, result)
    print(
        json.dumps(
            {
                "all_hard_gates_pass": result["all_hard_gates_pass"],
                "hard_gates": hard_gates,
                "summary": result["summary"],
                "total_worker_seconds": result["total_worker_seconds"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return result


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formal", action="store_true")
    parser.add_argument("--shard", type=int, choices=(0, 1))
    parser.add_argument("--merge", type=Path, nargs=2)
    parser.add_argument("--expected-git-sha")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.merge is not None:
        if args.shard is not None or not args.formal:
            raise SystemExit("--merge requires --formal and forbids --shard")
        if args.expected_git_sha is None:
            raise SystemExit("--merge requires --expected-git-sha")
        _merge(args.merge, expected_git_sha=args.expected_git_sha, output=args.output)
        return
    if args.shard is None:
        raise SystemExit("a non-merge run requires --shard")
    _run_shard(
        args.shard,
        formal=bool(args.formal),
        expected_git_sha=args.expected_git_sha,
        output=args.output,
    )


if __name__ == "__main__":
    main()
