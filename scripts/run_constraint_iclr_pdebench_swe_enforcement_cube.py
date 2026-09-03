"""Run the frozen zero-training PDEBench shallow-water enforcement cube."""

from __future__ import annotations

import json
import math
import os
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import h5py
import hydra
import numpy as np
import torch
from analyze_constraint_iclr_pdebench import read_records
from analyze_constraint_iclr_pdebench_swe import validate_swe_records
from analyze_constraint_iclr_pdebench_swe_enforcement_cube import (
    DERIVED_SPEC,
    canonical_object_sha256,
    validate_swe_checkpoint_lock,
)
from constraint_iclr_common import (
    append_jsonl,
    canonical_run_id,
    count_trainable_parameters,
    provenance,
    sha256_file,
)
from omegaconf import DictConfig, OmegaConf
from run_constraint_iclr_pdebench_fno import resolve_path
from run_constraint_iclr_pdebench_swe import (
    build_swe_model,
    evaluate_swe_cases,
    load_swe_trajectories,
    validate_swe_data_lock,
)


def _validate_hashed_artifact(
    root: Path, raw_path: str, expected_sha256: str, label: str
) -> Path:
    path = resolve_path(root, raw_path)
    if not path.is_file():
        raise RuntimeError(f"{label} is missing: {path}")
    observed = sha256_file(path)
    if observed != expected_sha256:
        raise RuntimeError(
            f"{label} SHA-256 mismatch: expected {expected_sha256}, got {observed}"
        )
    return path


def _checkpoint_payload(
    path: Path,
    *,
    expected_run_id: str,
    expected_schema: str,
    expected_epochs: int,
) -> dict[str, Any]:
    payload = torch.load(path, map_location="cpu", weights_only=False)
    if not isinstance(payload, dict):
        raise RuntimeError(f"SWE checkpoint payload is not a mapping: {path}")
    if payload.get("schema_version") != expected_schema:
        raise RuntimeError(f"SWE checkpoint schema mismatch: {path}")
    if payload.get("run_id") != expected_run_id:
        raise RuntimeError(f"SWE checkpoint run ID mismatch: {path}")
    if int(payload.get("completed_epochs", -1)) != expected_epochs:
        raise RuntimeError(f"SWE checkpoint epoch count mismatch: {path}")
    state = payload.get("model_state_dict")
    if not isinstance(state, dict) or not state:
        raise RuntimeError(f"SWE checkpoint has no model state: {path}")
    return payload


def swe_checkpoint_lock_payload(
    *,
    root: Path,
    core: dict[tuple[int, str], dict[str, Any]],
    config: dict[str, Any],
    core_records_path: Path,
    core_analysis_path: Path,
) -> dict[str, Any]:
    cube = config["cube"]
    entries: list[dict[str, Any]] = []
    expected_schema = str(cube["checkpoint_schema_version"])
    expected_epochs = int(cube["checkpoint_completed_epochs"])
    for seed in [int(value) for value in config["seeds"]]:
        for mechanism in [str(value) for value in cube["trained_parent_mechanisms"]]:
            parent = core[(seed, mechanism)]
            checkpoint = parent.get("checkpoint", {})
            raw_path = str(checkpoint.get("path"))
            path = resolve_path(root, raw_path)
            if not path.is_file():
                raise RuntimeError(f"SWE parent checkpoint is missing: {path}")
            observed_bytes = path.stat().st_size
            observed_sha256 = sha256_file(path)
            if observed_bytes != int(checkpoint.get("bytes", -1)):
                raise RuntimeError(f"SWE parent checkpoint byte count changed: {path}")
            if observed_sha256 != str(checkpoint.get("sha256")):
                raise RuntimeError(f"SWE parent checkpoint SHA-256 changed: {path}")
            payload = _checkpoint_payload(
                path,
                expected_run_id=str(parent["run_id"]),
                expected_schema=expected_schema,
                expected_epochs=expected_epochs,
            )
            entries.append(
                {
                    "seed": seed,
                    "mechanism": mechanism,
                    "run_id": parent["run_id"],
                    "path": raw_path,
                    "bytes": observed_bytes,
                    "sha256": observed_sha256,
                    "payload_schema_version": payload["schema_version"],
                    "completed_epochs": int(payload["completed_epochs"]),
                }
            )
    return {
        "schema_version": cube["checkpoint_lock_schema_version"],
        "benchmark_id": config["benchmark_id"],
        "core_records": {
            "path": str(config["output"]),
            "sha256": sha256_file(core_records_path),
            "record_count": len(core),
        },
        "core_analysis": {
            "path": str(cube["core_analysis"]),
            "sha256": sha256_file(core_analysis_path),
        },
        "factorial_protocol_sha256": config["protocol_sha256"],
        "cube_protocol_sha256": cube["protocol_sha256"],
        "cube_decision_sha256": cube["decision_sha256"],
        "checkpoints": entries,
    }


def create_or_validate_swe_checkpoint_lock(
    *,
    root: Path,
    core: dict[tuple[int, str], dict[str, Any]],
    config: dict[str, Any],
    core_records_path: Path,
    core_analysis_path: Path,
) -> tuple[Path, str, dict[str, Any]]:
    cube = config["cube"]
    lock_path = resolve_path(root, str(cube["checkpoint_lock"]))
    payload = swe_checkpoint_lock_payload(
        root=root,
        core=core,
        config=config,
        core_records_path=core_records_path,
        core_analysis_path=core_analysis_path,
    )
    canonical = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if lock_path.exists():
        if lock_path.read_text(encoding="utf-8") != canonical:
            raise RuntimeError("existing SWE checkpoint lock is not byte-identical")
    else:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = lock_path.with_suffix(lock_path.suffix + ".tmp")
        temporary.write_text(canonical, encoding="utf-8")
        os.replace(temporary, lock_path)
    lock_sha256 = sha256_file(lock_path)
    validate_swe_checkpoint_lock(
        payload,
        core,
        config,
        core_records_sha256=sha256_file(core_records_path),
        core_analysis_sha256=sha256_file(core_analysis_path),
    )
    return lock_path, lock_sha256, payload


def validate_swe_checkpoint_files(
    *, root: Path, checkpoint_lock: dict[str, Any], config: dict[str, Any]
) -> dict[tuple[int, str], dict[str, Any]]:
    cube = config["cube"]
    indexed: dict[tuple[int, str], dict[str, Any]] = {}
    for entry in checkpoint_lock["checkpoints"]:
        key = (int(entry["seed"]), str(entry["mechanism"]))
        path = resolve_path(root, str(entry["path"]))
        if not path.is_file():
            raise RuntimeError(f"locked SWE checkpoint disappeared: {path}")
        if path.stat().st_size != int(entry["bytes"]):
            raise RuntimeError(f"locked SWE checkpoint byte count changed: {path}")
        if sha256_file(path) != str(entry["sha256"]):
            raise RuntimeError(f"locked SWE checkpoint SHA-256 changed: {path}")
        _checkpoint_payload(
            path,
            expected_run_id=str(entry["run_id"]),
            expected_schema=str(cube["checkpoint_schema_version"]),
            expected_epochs=int(cube["checkpoint_completed_epochs"]),
        )
        indexed[key] = entry
    return indexed


def _existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    completed: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"invalid SWE cube JSONL at line {line_number}") from error
        run_id = str(record["run_id"])
        if run_id in completed:
            raise RuntimeError(f"duplicate SWE cube run ID already present: {run_id}")
        completed.add(run_id)
    return completed


def run_swe_cube(cfg: DictConfig) -> None:
    root = Path(__file__).resolve().parents[1]
    resolved = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(resolved, dict):
        raise TypeError("resolved SWE cube config must be a mapping")
    cube = resolved.get("cube")
    if not isinstance(cube, Mapping):
        raise TypeError("SWE cube config must be a mapping")
    if cube.get("stage") not in {
        "swe_enforcement_cube_confirmation",
        "swe_enforcement_cube_smoke",
    }:
        raise RuntimeError("unsupported SWE enforcement-cube stage")
    if [str(value) for value in cube["derived_mechanisms"]] != list(DERIVED_SPEC):
        raise RuntimeError("SWE derived mechanisms differ from the frozen cube")
    if int(cube["expected_derived_records"]) != 3 * len(resolved["seeds"]):
        raise RuntimeError("SWE derived record count differs from the seed list")
    if cube["stage"] == "swe_enforcement_cube_confirmation":
        if [int(value) for value in resolved["seeds"]] != list(range(6000, 6030)):
            raise RuntimeError("formal SWE cube seeds must remain 6000--6029")
        if int(cube["expected_core_records"]) != 150:
            raise RuntimeError("formal SWE cube requires exactly 150 core records")
        if int(cube["expected_trained_checkpoints"]) != 120:
            raise RuntimeError("formal SWE cube requires exactly 120 checkpoints")
        if int(cube["expected_derived_records"]) != 90:
            raise RuntimeError("formal SWE cube requires exactly 90 derived records")
        if len(resolved["evaluation"]["case_names"]) * len(
            resolved["evaluation"]["horizons"]
        ) != 8:
            raise RuntimeError("formal SWE cube requires all eight evaluation cells")

    cube_protocol_path = _validate_hashed_artifact(
        root,
        str(cube["protocol_path"]),
        str(cube["protocol_sha256"]),
        "SWE cube protocol",
    )
    cube_decision_path = _validate_hashed_artifact(
        root,
        str(cube["decision_path"]),
        str(cube["decision_sha256"]),
        "SWE cube decision",
    )
    factorial_protocol_path = _validate_hashed_artifact(
        root,
        str(resolved["protocol_path"]),
        str(resolved["protocol_sha256"]),
        "SWE factorial protocol",
    )
    source_metadata_path = _validate_hashed_artifact(
        root,
        str(resolved["source_metadata_path"]),
        str(resolved["source_metadata_sha256"]),
        "SWE source metadata",
    )
    data_decision_path = _validate_hashed_artifact(
        root,
        str(resolved["data_decision_path"]),
        str(resolved["data_decision_sha256"]),
        "SWE data decision",
    )
    transport_decision_path = _validate_hashed_artifact(
        root,
        str(resolved["transport_decision_path"]),
        str(resolved["transport_decision_sha256"]),
        "SWE transport decision",
    )
    model_decision_path = None
    if cube["stage"] == "swe_enforcement_cube_confirmation":
        if not resolved.get("model_decision_path") or not resolved.get(
            "model_decision_sha256"
        ):
            raise RuntimeError("SWE cube requires the frozen formal model decision")
        model_decision_path = _validate_hashed_artifact(
            root,
            str(resolved["model_decision_path"]),
            str(resolved["model_decision_sha256"]),
            "SWE model decision",
        )

    core_records_path = resolve_path(root, str(resolved["output"]))
    core_analysis_path = resolve_path(root, str(cube["core_analysis"]))
    if not core_records_path.is_file() or not core_analysis_path.is_file():
        raise RuntimeError("SWE cube activation requires complete core records and analysis")
    core_records = read_records(core_records_path)
    if len(core_records) != int(cube["expected_core_records"]):
        raise RuntimeError("SWE cube parent does not have exact core coverage")
    core = validate_swe_records(core_records, resolved)
    completed_core_analysis = json.loads(core_analysis_path.read_text(encoding="utf-8"))
    if completed_core_analysis.get("input_sha256") != sha256_file(core_records_path):
        raise RuntimeError("SWE core analysis is not bound to the parent JSONL")
    if not completed_core_analysis.get("integrity_gates_passed", False):
        raise RuntimeError("SWE core analysis did not pass integrity gates")

    dataset_path = resolve_path(root, str(resolved["dataset"]["path"]))
    data_lock_path, data_lock_sha256, data_lock = validate_swe_data_lock(
        root=root, resolved=resolved, dataset_path=dataset_path
    )
    if data_lock_sha256 != str(resolved["dataset"]["lock_sha256"]):
        raise RuntimeError("SWE cube validated data lock differs from config")
    checkpoint_lock_path, checkpoint_lock_sha256, checkpoint_lock = (
        create_or_validate_swe_checkpoint_lock(
            root=root,
            core=core,
            config=resolved,
            core_records_path=core_records_path,
            core_analysis_path=core_analysis_path,
        )
    )
    checkpoints = validate_swe_checkpoint_files(
        root=root, checkpoint_lock=checkpoint_lock, config=resolved
    )

    cube_config_path = root / (
        "configs/constraint_iclr/"
        "pdebench_swe_rdb_enforcement_cube_20260902.yaml"
    )
    active_config_path = resolve_path(root, str(resolved["active_config_path"]))
    source_files = [
        Path(__file__),
        root / "scripts/analyze_constraint_iclr_pdebench_swe_enforcement_cube.py",
        root / "scripts/analyze_constraint_iclr_pdebench_swe.py",
        root / "scripts/run_constraint_iclr_pdebench_swe.py",
        root / "scripts/prepare_constraint_iclr_pdebench_swe.py",
        root / "scripts/run_constraint_iclr_pdebench_fno.py",
        root / "scripts/constraint_iclr_common.py",
        cube_config_path,
        active_config_path,
        cube_protocol_path,
        cube_decision_path,
        factorial_protocol_path,
        source_metadata_path,
        data_decision_path,
        transport_decision_path,
        data_lock_path,
        core_analysis_path,
        checkpoint_lock_path,
    ]
    if model_decision_path is not None:
        source_files.append(model_decision_path)
    shared_provenance = provenance(
        root=root, resolved_config=resolved, source_files=source_files
    )
    if shared_provenance["git_head"] != str(resolved["expected_git_head"]):
        raise RuntimeError("unexpected Git HEAD for SWE enforcement cube")
    if bool(shared_provenance["git_dirty"]) is not bool(
        resolved["expected_git_dirty"]
    ):
        raise RuntimeError("unexpected dirty flag for SWE enforcement cube")

    device = torch.device(str(resolved["device"]))
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    confirmation_indices = np.arange(
        int(resolved["split"]["confirmation_start"]),
        int(resolved["split"]["confirmation_start"])
        + int(resolved["split"]["confirmation_count"]),
        dtype=np.int64,
    )
    evaluation_trajectories = load_swe_trajectories(
        dataset_path,
        confirmation_indices,
        temporal_stride=int(resolved["training"]["temporal_stride"]),
        spatial_factor=1,
        restriction_method="block_average",
    )
    with h5py.File(dataset_path, "r") as handle:
        native_grid_x = torch.from_numpy(
            np.asarray(handle["0000/grid/x"], dtype=np.float32)
        )
        native_grid_y = torch.from_numpy(
            np.asarray(handle["0000/grid/y"], dtype=np.float32)
        )
    output_path = resolve_path(root, str(cube["output"]))
    completed = _existing_ids(output_path)
    core_records_sha256 = sha256_file(core_records_path)
    core_analysis_sha256 = sha256_file(core_analysis_path)
    dataset_sha256 = str(data_lock["inspection"]["sha256"])

    for seed in [int(value) for value in resolved["seeds"]]:
        for mechanism, spec in DERIVED_SPEC.items():
            parent_mechanism = str(spec["parent"])
            parent = core[(seed, parent_mechanism)]
            checkpoint_entry = checkpoints[(seed, parent_mechanism)]
            identity = {
                "schema_version": cube["schema_version"],
                "stage": cube["stage"],
                "benchmark_id": resolved["benchmark_id"],
                "dataset_sha256": dataset_sha256,
                "data_lock_sha256": data_lock_sha256,
                "factorial_protocol_sha256": resolved["protocol_sha256"],
                "cube_protocol_sha256": cube["protocol_sha256"],
                "cube_decision_sha256": cube["decision_sha256"],
                "core_records_sha256": core_records_sha256,
                "core_analysis_sha256": core_analysis_sha256,
                "checkpoint_lock_sha256": checkpoint_lock_sha256,
                "seed": seed,
                "mechanism": mechanism,
                "parent_run_id": parent["run_id"],
                "forward_map": spec["forward_map"],
                "inference_projected": spec["inference_projected"],
            }
            run_id = canonical_run_id(identity)
            if run_id in completed:
                continue
            checkpoint_path = resolve_path(root, str(checkpoint_entry["path"]))
            if sha256_file(checkpoint_path) != checkpoint_entry["sha256"]:
                raise RuntimeError("SWE parent checkpoint changed before evaluation")
            checkpoint = _checkpoint_payload(
                checkpoint_path,
                expected_run_id=str(parent["run_id"]),
                expected_schema=str(cube["checkpoint_schema_version"]),
                expected_epochs=int(cube["checkpoint_completed_epochs"]),
            )
            model = build_swe_model(resolved["model"], str(spec["forward_map"])).to(
                device
            )
            model.load_state_dict(checkpoint["model_state_dict"], strict=True)
            parameter_count = count_trainable_parameters(model)
            if parameter_count != int(parent["compute"]["trainable_parameters"]):
                raise RuntimeError("SWE cube parent parameter count mismatch")
            if device.type == "cuda":
                torch.cuda.reset_peak_memory_stats(device)
            started = time.perf_counter()
            cases, projection_identity = evaluate_swe_cases(
                model=model,
                native_trajectories=evaluation_trajectories,
                native_grid_x=native_grid_x,
                native_grid_y=native_grid_y,
                evaluation_cfg=resolved["evaluation"],
                device=device,
                projected=bool(spec["inference_projected"]),
            )
            evaluation_runtime = time.perf_counter() - started
            if not all(
                math.isfinite(float(value))
                for case in cases.values()
                for horizon_metrics in case.values()
                for value in horizon_metrics.values()
            ):
                raise FloatingPointError("non-finite SWE cube metric")
            peak_memory = (
                int(torch.cuda.max_memory_allocated(device))
                if device.type == "cuda"
                else None
            )
            record = {
                **identity,
                "run_id": run_id,
                "derived_from": parent["run_id"],
                "training_index_sha256": parent["training_index_sha256"],
                "initialization_sha256": parent["initialization_sha256"],
                "parent": {
                    "run_id": parent["run_id"],
                    "mechanism": parent_mechanism,
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
                "projection_identity_max_abs_by_case": projection_identity,
                "provenance": shared_provenance,
            }
            append_jsonl(output_path, record)
            completed.add(run_id)
            print(f"completed {run_id} {mechanism} seed={seed}", flush=True)


@hydra.main(
    version_base=None,
    config_path="../configs/constraint_iclr",
    config_name="pdebench_swe_rdb_enforcement_cube_20260902",
)
def main(cfg: DictConfig) -> None:
    run_swe_cube(cfg)


if __name__ == "__main__":
    main()
