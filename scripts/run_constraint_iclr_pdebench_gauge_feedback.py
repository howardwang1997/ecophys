"""Run the frozen zero-training Advection input-gauge feedback intervention."""

from __future__ import annotations

import json
import math
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import hydra
import numpy as np
import torch
from analyze_constraint_iclr_pdebench import read_records
from analyze_constraint_iclr_pdebench_enforcement_cube import (
    canonical_object_sha256,
    validate_cube_records,
)
from analyze_constraint_iclr_pdebench_factorial import validate_factorial_records
from constraint_iclr_common import (
    append_jsonl,
    canonical_run_id,
    count_trainable_parameters,
    provenance,
    sha256_file,
)
from constraint_iclr_gauge_identity import gauge_identity_gate
from omegaconf import DictConfig, OmegaConf
from run_constraint_iclr_pdebench_enforcement_cube import (
    _checkpoint_payload,
    validate_checkpoint_files_against_lock,
)
from run_constraint_iclr_pdebench_fno import (
    FNO1d,
    build_model,
    load_trajectories,
    load_x_coordinate,
    project_mass,
    resolve_path,
    restrict_grid,
    restrict_spatial_torch,
    validate_data_lock,
)


def _validate_hashed_file(root: Path, raw_path: str, expected_sha256: str, label: str) -> Path:
    path = resolve_path(root, raw_path)
    if not path.is_file():
        raise RuntimeError(f"{label} is missing: {path}")
    observed = sha256_file(path)
    if observed != expected_sha256:
        raise RuntimeError(f"{label} SHA-256 mismatch: expected {expected_sha256}, got {observed}")
    return path


def _existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    completed: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"invalid gauge-feedback JSONL at line {line_number}: {error}") from error
        completed.add(str(record["run_id"]))
    return completed


def evaluate_gauge_feedback(
    *,
    model: FNO1d,
    trajectories: torch.Tensor,
    grid: torch.Tensor,
    history: int,
    batch_size: int,
    device: torch.device,
) -> dict[str, float]:
    """Intervene only on the first predicted state's uniform gauge component."""

    if history + 2 > trajectories.shape[1]:
        raise RuntimeError("two-step gauge intervention exceeds the trajectory length")
    grid_device = grid.to(device=device, dtype=torch.float32)
    feedback_squared_error = 0.0
    projected_error_squared = 0.0
    raw_error_squared = 0.0
    gauge_squared = 0.0
    elements = 0
    identity_max = 0.0
    nonconstant_max = 0.0
    identity_scale_max = 0.0
    model.eval()
    with torch.no_grad():
        for start in range(0, trajectories.shape[0], batch_size):
            batch = trajectories[start : start + batch_size]
            state = batch[:, :history].permute(0, 2, 1).to(device=device, dtype=torch.float32)
            previous = state[..., -1]
            first_raw = model(state, grid_device)
            first_projected = project_mass(previous, first_raw)
            gauge_shift = first_raw - first_projected
            gauge_nonconstant = gauge_shift - gauge_shift.mean(dim=-1, keepdim=True)
            identity_scale_max = max(
                identity_scale_max,
                *(
                    float(value.abs().max().detach().cpu())
                    for value in (
                        previous,
                        first_raw,
                        first_projected,
                        gauge_shift,
                    )
                ),
            )
            identity_max = max(
                identity_max,
                float(gauge_nonconstant.abs().max().detach().cpu()),
            )
            nonconstant_max = max(
                nonconstant_max,
                float((gauge_shift - gauge_shift[..., :1].expand_as(gauge_shift)).abs().max().detach().cpu()),
            )

            raw_history = torch.cat((state[..., 1:], first_raw.unsqueeze(-1)), dim=-1)
            projected_history = torch.cat((state[..., 1:], first_projected.unsqueeze(-1)), dim=-1)
            second_raw_history = model(raw_history, grid_device)
            second_projected_history = model(projected_history, grid_device)
            feedback = second_raw_history - second_projected_history
            conserving_feedback = feedback - feedback.mean(dim=-1, keepdim=True)
            target = batch[:, history + 1].to(device=device, dtype=torch.float32)
            projected_error = second_projected_history - target
            projected_conserving_error = projected_error - projected_error.mean(dim=-1, keepdim=True)
            raw_error = second_raw_history - target
            raw_conserving_error = raw_error - raw_error.mean(dim=-1, keepdim=True)

            feedback_squared_error += float(conserving_feedback.square().sum().detach().cpu())
            projected_error_squared += float(projected_conserving_error.square().sum().detach().cpu())
            raw_error_squared += float(raw_conserving_error.square().sum().detach().cpu())
            gauge_squared += float(gauge_shift.square().sum().detach().cpu())
            elements += int(feedback.numel())

    if elements <= 0:
        raise RuntimeError("gauge-feedback evaluation accumulated no elements")
    feedback_rmse = math.sqrt(feedback_squared_error / elements)
    projected_rmse = math.sqrt(projected_error_squared / elements)
    raw_rmse = math.sqrt(raw_error_squared / elements)
    gauge_rmse = math.sqrt(gauge_squared / elements)
    if projected_rmse <= 0.0:
        raise RuntimeError("gauge-feedback baseline denominator is not positive")
    result = {
        "feedback_rmse": feedback_rmse,
        "projected_history_conserving_rmse": projected_rmse,
        "raw_history_conserving_rmse": raw_rmse,
        "feedback_ratio": feedback_rmse / projected_rmse,
        "first_step_gauge_rmse": gauge_rmse,
        "step_one_q_identity_max_abs": identity_max,
        "step_one_gauge_nonconstant_max_abs": nonconstant_max,
        "step_one_identity_scale_max_abs": identity_scale_max,
    }
    if not all(math.isfinite(value) for value in result.values()):
        raise FloatingPointError("non-finite gauge-feedback metric")
    return result


def evaluate_gauge_feedback_cases(
    *,
    model: FNO1d,
    native_trajectories: torch.Tensor,
    native_grid: torch.Tensor,
    evaluation_cfg: Mapping[str, Any],
    history: int,
    device: torch.device,
) -> dict[str, dict[str, float]]:
    strides = [int(value) for value in evaluation_cfg["spatial_strides"]]
    names = [str(value) for value in evaluation_cfg["case_names"]]
    if len(strides) != len(names):
        raise RuntimeError("evaluation strides and case names must have equal length")
    restriction_method = str(evaluation_cfg["restriction_method"])
    batch_size = int(evaluation_cfg["batch_size"])
    return {
        name: evaluate_gauge_feedback(
            model=model,
            trajectories=restrict_spatial_torch(native_trajectories, stride, restriction_method).contiguous(),
            grid=restrict_grid(native_grid, stride, restriction_method),
            history=history,
            batch_size=batch_size,
            device=device,
        )
        for stride, name in zip(strides, names, strict=True)
    }


def _validate_parent_artifacts(
    *, root: Path, resolved: dict[str, Any]
) -> tuple[
    dict[tuple[int, str], dict[str, Any]],
    dict[tuple[int, str], dict[str, Any]],
    dict[str, Any],
    dict[str, Path],
]:
    gauge = resolved["gauge_feedback"]
    core_path = _validate_hashed_file(
        root,
        str(resolved["output"]),
        str(gauge["parent_core_records_sha256"]),
        "parent core records",
    )
    core_analysis_path = _validate_hashed_file(
        root,
        str(resolved["cube"]["core_analysis"]),
        str(gauge["parent_core_analysis_sha256"]),
        "parent core analysis",
    )
    cube_path = _validate_hashed_file(
        root,
        str(gauge["parent_cube_records"]),
        str(gauge["parent_cube_records_sha256"]),
        "parent cube records",
    )
    cube_analysis_path = _validate_hashed_file(
        root,
        str(gauge["parent_cube_analysis"]),
        str(gauge["parent_cube_analysis_sha256"]),
        "parent cube analysis",
    )
    lock_path = _validate_hashed_file(
        root,
        str(resolved["cube"]["checkpoint_lock"]),
        str(gauge["checkpoint_lock_sha256"]),
        "parent checkpoint lock",
    )
    core_records = read_records(core_path)
    cube_records = read_records(cube_path)
    core = validate_factorial_records(core_records, resolved)
    core_analysis = json.loads(core_analysis_path.read_text(encoding="utf-8"))
    cube_analysis = json.loads(cube_analysis_path.read_text(encoding="utf-8"))
    _validate_parent_analysis_bindings(
        core_analysis=core_analysis,
        cube_analysis=cube_analysis,
        core_records_sha256=sha256_file(core_path),
        cube_records_sha256=sha256_file(cube_path),
    )
    checkpoint_lock = json.loads(lock_path.read_text(encoding="utf-8"))
    validate_cube_records(
        cube_records,
        core_records,
        checkpoint_lock,
        resolved,
        core_records_sha256=sha256_file(core_path),
        core_analysis_sha256=sha256_file(core_analysis_path),
        checkpoint_lock_sha256=sha256_file(lock_path),
    )
    checkpoint_entries = validate_checkpoint_files_against_lock(
        root=root,
        checkpoint_lock=checkpoint_lock,
        config=resolved,
    )
    return (
        core,
        checkpoint_entries,
        checkpoint_lock,
        {
            "core": core_path,
            "core_analysis": core_analysis_path,
            "cube": cube_path,
            "cube_analysis": cube_analysis_path,
            "checkpoint_lock": lock_path,
        },
    )


def _validate_parent_analysis_bindings(
    *,
    core_analysis: dict[str, Any],
    cube_analysis: dict[str, Any],
    core_records_sha256: str,
    cube_records_sha256: str,
) -> None:
    """Validate the hashes emitted by the frozen core and cube analyzers."""

    if (
        core_analysis.get("input_sha256") != core_records_sha256
        or core_analysis.get("integrity_gates_passed") is not True
    ):
        raise RuntimeError("parent core analysis is not integrity-bound")
    if (
        cube_analysis.get("core_input_sha256") != core_records_sha256
        or cube_analysis.get("derived_input_sha256") != cube_records_sha256
        or cube_analysis.get("integrity_gates_passed") is not True
    ):
        raise RuntimeError("parent cube analysis is not integrity-bound")


def run_gauge_feedback(cfg: DictConfig) -> None:
    root = Path(__file__).resolve().parents[1]
    resolved = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(resolved, dict):
        raise TypeError("resolved gauge-feedback config must be a mapping")
    gauge = resolved.get("gauge_feedback")
    if not isinstance(gauge, Mapping):
        raise TypeError("gauge-feedback config is missing")
    seeds = [int(value) for value in resolved["seeds"]]
    mechanisms = [str(value) for value in gauge["parent_mechanisms"]]
    maps = {str(key): str(value) for key, value in gauge["compatible_forward_maps"].items()}
    if seeds != list(range(3000, 3030)):
        raise RuntimeError("gauge-feedback seeds must remain 3000--3029")
    if mechanisms != ["hard_abs", "hard"] or maps != {
        "hard_abs": "free",
        "hard": "free_res",
    }:
        raise RuntimeError("gauge-feedback parent/forward-map design changed")
    if int(gauge["expected_records"]) != len(seeds) * len(mechanisms):
        raise RuntimeError("gauge-feedback expected record count changed")
    if str(gauge["primary_case"]) != "ood_r512" or float(gauge["practical_ratio_threshold"]) != 0.10:
        raise RuntimeError("gauge-feedback primary decision changed")

    protocol_path = _validate_hashed_file(
        root,
        str(gauge["protocol_path"]),
        str(gauge["protocol_sha256"]),
        "gauge-feedback protocol",
    )
    decision_path = _validate_hashed_file(
        root,
        str(gauge["decision_path"]),
        str(gauge["decision_sha256"]),
        "gauge-feedback decision",
    )
    identity_amendment_path = _validate_hashed_file(
        root,
        str(gauge["identity_runtime_amendment_path"]),
        str(gauge["identity_runtime_amendment_sha256"]),
        "gauge identity runtime amendment",
    )
    identity_decision_path = _validate_hashed_file(
        root,
        str(gauge["identity_runtime_decision_path"]),
        str(gauge["identity_runtime_decision_sha256"]),
        "gauge identity runtime decision",
    )
    core, checkpoint_entries, _, parent_paths = _validate_parent_artifacts(root=root, resolved=resolved)

    dataset_path = resolve_path(root, str(resolved["dataset"]["path"]))
    data_lock_path, data_lock_sha256, data_lock = validate_data_lock(
        root=root, resolved=resolved, dataset_path=dataset_path
    )
    if data_lock_sha256 != str(resolved["dataset"]["lock_sha256"]):
        raise RuntimeError("validated data-lock SHA-256 changed")

    active_config_path = root / str(resolved["active_config_path"])
    source_files = [
        Path(__file__),
        root / "scripts/analyze_constraint_iclr_pdebench_gauge_feedback.py",
        root / "scripts/run_constraint_iclr_pdebench_enforcement_cube.py",
        root / "scripts/analyze_constraint_iclr_pdebench_enforcement_cube.py",
        root / "scripts/analyze_constraint_iclr_pdebench_factorial.py",
        root / "scripts/analyze_constraint_iclr_pdebench.py",
        root / "scripts/run_constraint_iclr_pdebench_fno.py",
        root / "scripts/constraint_iclr_common.py",
        root / "scripts/constraint_iclr_gauge_identity.py",
        active_config_path,
        protocol_path,
        decision_path,
        identity_amendment_path,
        identity_decision_path,
        data_lock_path,
        *parent_paths.values(),
    ]
    shared_provenance = provenance(root=root, resolved_config=resolved, source_files=source_files)
    if shared_provenance["git_head"] != str(resolved["expected_git_head"]):
        raise RuntimeError("unexpected Git HEAD for gauge-feedback intervention")
    if bool(shared_provenance["git_dirty"]) is not bool(resolved["expected_git_dirty"]):
        raise RuntimeError("unexpected dirty flag for gauge-feedback intervention")

    device = torch.device(str(resolved["device"]))
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    confirmation_indices = np.arange(
        int(resolved["split"]["confirmation_start"]),
        int(resolved["split"]["confirmation_start"]) + int(resolved["split"]["confirmation_count"]),
        dtype=np.int64,
    )
    native_trajectories = load_trajectories(
        dataset_path,
        confirmation_indices,
        temporal_stride=int(resolved["training"]["temporal_stride"]),
        spatial_stride=1,
    )
    native_grid = load_x_coordinate(dataset_path, 1)
    output_path = resolve_path(root, str(gauge["output"]))
    completed = _existing_ids(output_path)
    history = int(resolved["model"]["history"])

    for seed in seeds:
        for mechanism in mechanisms:
            parent = core[(seed, mechanism)]
            checkpoint_entry = checkpoint_entries[(seed, mechanism)]
            forward_map = maps[mechanism]
            identity = {
                "schema_version": gauge["schema_version"],
                "stage": gauge["stage"],
                "benchmark_id": resolved["benchmark_id"],
                "dataset_sha256": data_lock["inspection"]["sha256"],
                "data_lock_sha256": data_lock_sha256,
                "gauge_protocol_sha256": gauge["protocol_sha256"],
                "gauge_decision_sha256": gauge["decision_sha256"],
                "gauge_identity_amendment_sha256": gauge["identity_runtime_amendment_sha256"],
                "gauge_identity_decision_sha256": gauge["identity_runtime_decision_sha256"],
                "core_records_sha256": gauge["parent_core_records_sha256"],
                "core_analysis_sha256": gauge["parent_core_analysis_sha256"],
                "cube_records_sha256": gauge["parent_cube_records_sha256"],
                "cube_analysis_sha256": gauge["parent_cube_analysis_sha256"],
                "checkpoint_lock_sha256": gauge["checkpoint_lock_sha256"],
                "seed": seed,
                "mechanism": mechanism,
                "forward_map": forward_map,
                "parent_run_id": parent["run_id"],
            }
            run_id = canonical_run_id(identity)
            if run_id in completed:
                continue
            checkpoint_path = resolve_path(root, str(checkpoint_entry["path"]))
            if sha256_file(checkpoint_path) != str(checkpoint_entry["sha256"]):
                raise RuntimeError(f"parent checkpoint changed: {checkpoint_path}")
            checkpoint = _checkpoint_payload(
                checkpoint_path,
                expected_run_id=str(parent["run_id"]),
                expected_schema=str(resolved["cube"]["checkpoint_schema_version"]),
                expected_epochs=int(resolved["cube"]["checkpoint_completed_epochs"]),
            )
            model = build_model(resolved["model"], forward_map).to(device)
            model.load_state_dict(checkpoint["model_state_dict"], strict=True)
            parameter_count = count_trainable_parameters(model)
            if parameter_count != int(parent["compute"]["trainable_parameters"]):
                raise RuntimeError("gauge-feedback parent parameter count changed")
            if device.type == "cuda":
                torch.cuda.reset_peak_memory_stats(device)
            started = time.perf_counter()
            cases = evaluate_gauge_feedback_cases(
                model=model,
                native_trajectories=native_trajectories,
                native_grid=native_grid,
                evaluation_cfg=resolved["evaluation"],
                history=history,
                device=device,
            )
            evaluation_runtime = time.perf_counter() - started
            if any(not gauge_identity_gate(metrics, gauge)[2] for metrics in cases.values()):
                raise RuntimeError("step-one gauge identity exceeded tolerance")
            peak_memory = int(torch.cuda.max_memory_allocated(device)) if device.type == "cuda" else None
            record = {
                **identity,
                "run_id": run_id,
                "derived_from": parent["run_id"],
                "training_index_sha256": parent["training_index_sha256"],
                "initialization_sha256": parent["initialization_sha256"],
                "parent": {
                    "run_id": parent["run_id"],
                    "mechanism": mechanism,
                    "checkpoint_path": checkpoint_entry["path"],
                    "checkpoint_sha256": checkpoint_entry["sha256"],
                    "checkpoint_bytes": checkpoint_entry["bytes"],
                    "training_index_sha256": parent["training_index_sha256"],
                    "initialization_sha256": parent["initialization_sha256"],
                    "provenance_sha256": canonical_object_sha256(parent["provenance"]),
                },
                "compute": {
                    "trainable_parameters": parameter_count,
                    "examples_seen": 0,
                    "proxy": 0,
                    "training_runtime_seconds": 0.0,
                    "evaluation_runtime_seconds": evaluation_runtime,
                    "peak_gpu_memory_bytes": peak_memory,
                    "optimization_runs": 0,
                },
                "cases": cases,
                "provenance": shared_provenance,
            }
            append_jsonl(output_path, record)
            completed.add(run_id)
            print(f"completed {run_id} {mechanism} seed={seed}", flush=True)


@hydra.main(
    version_base=None,
    config_path="../configs/constraint_iclr",
    config_name="pdebench_advection_fno_gauge_feedback_20260902",
)
def main(cfg: DictConfig) -> None:
    run_gauge_feedback(cfg)


if __name__ == "__main__":
    main()
