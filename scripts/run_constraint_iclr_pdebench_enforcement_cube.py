"""Run the frozen zero-training PDEBench enforcement-cube evaluations."""

from __future__ import annotations

import json
import math
import os
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import hydra
import numpy as np
import torch
from analyze_constraint_iclr_pdebench import read_records
from analyze_constraint_iclr_pdebench_enforcement_cube import (
    DERIVED_SPEC,
    canonical_object_sha256,
    validate_checkpoint_lock,
)
from analyze_constraint_iclr_pdebench_factorial import validate_factorial_records
from constraint_iclr_common import (
    append_jsonl,
    canonical_run_id,
    count_trainable_parameters,
    provenance,
    sha256_file,
)
from omegaconf import DictConfig, OmegaConf
from run_constraint_iclr_pdebench_fno import (
    build_model,
    evaluate_cases,
    load_trajectories,
    load_x_coordinate,
    resolve_path,
    validate_data_lock,
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
        raise RuntimeError(f"checkpoint payload is not a mapping: {path}")
    if payload.get("schema_version") != expected_schema:
        raise RuntimeError(f"checkpoint schema mismatch: {path}")
    if payload.get("run_id") != expected_run_id:
        raise RuntimeError(f"checkpoint run ID mismatch: {path}")
    if int(payload.get("completed_epochs", -1)) != expected_epochs:
        raise RuntimeError(f"checkpoint epoch count mismatch: {path}")
    state = payload.get("model_state_dict")
    if not isinstance(state, dict) or not state:
        raise RuntimeError(f"checkpoint has no model state: {path}")
    return payload


def checkpoint_lock_payload(
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
        for mechanism in [
            str(value) for value in cube["trained_parent_mechanisms"]
        ]:
            parent = core[(seed, mechanism)]
            raw_path = str(parent.get("checkpoint", {}).get("path"))
            path = resolve_path(root, raw_path)
            if not path.is_file():
                raise RuntimeError(f"parent checkpoint is missing: {path}")
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
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
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
        "checkpoints": entries,
    }


def create_or_validate_checkpoint_lock(
    *,
    root: Path,
    core: dict[tuple[int, str], dict[str, Any]],
    config: dict[str, Any],
    core_records_path: Path,
    core_analysis_path: Path,
) -> tuple[Path, str, dict[str, Any]]:
    cube = config["cube"]
    lock_path = resolve_path(root, str(cube["checkpoint_lock"]))
    payload = checkpoint_lock_payload(
        root=root,
        core=core,
        config=config,
        core_records_path=core_records_path,
        core_analysis_path=core_analysis_path,
    )
    canonical = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if lock_path.exists():
        if lock_path.read_text(encoding="utf-8") != canonical:
            raise RuntimeError(
                "existing checkpoint lock is not byte-identical to the reconstructed lock"
            )
    else:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = lock_path.with_suffix(lock_path.suffix + ".tmp")
        temporary.write_text(canonical, encoding="utf-8")
        os.replace(temporary, lock_path)
    lock_sha256 = sha256_file(lock_path)
    validate_checkpoint_lock(
        payload,
        core,
        config,
        core_records_sha256=sha256_file(core_records_path),
        core_analysis_sha256=sha256_file(core_analysis_path),
    )
    return lock_path, lock_sha256, payload


def validate_checkpoint_files_against_lock(
    *,
    root: Path,
    checkpoint_lock: dict[str, Any],
    config: dict[str, Any],
) -> dict[tuple[int, str], dict[str, Any]]:
    cube = config["cube"]
    indexed: dict[tuple[int, str], dict[str, Any]] = {}
    for entry in checkpoint_lock["checkpoints"]:
        key = (int(entry["seed"]), str(entry["mechanism"]))
        path = resolve_path(root, str(entry["path"]))
        if not path.is_file():
            raise RuntimeError(f"locked checkpoint disappeared: {path}")
        if path.stat().st_size != int(entry["bytes"]):
            raise RuntimeError(f"locked checkpoint byte count changed: {path}")
        if sha256_file(path) != str(entry["sha256"]):
            raise RuntimeError(f"locked checkpoint SHA-256 changed: {path}")
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
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise RuntimeError(
                f"invalid cube JSONL at line {line_number}: {error}"
            ) from error
        completed.add(str(record["run_id"]))
    return completed


def formal_cube_seeds(config: Mapping[str, Any]) -> list[int]:
    seeds = [int(value) for value in config["seeds"]]
    raw_universe = config.get("formal_seed_universe")
    expected = (
        [int(value) for value in raw_universe]
        if raw_universe is not None
        else list(range(3000, 3030))
    )
    if len(expected) != 30 or len(set(expected)) != 30:
        raise RuntimeError("formal cube requires exactly 30 unique registered seeds")
    if seeds != expected:
        raise RuntimeError("formal cube seeds differ from the registered seed universe")
    return seeds


def run_cube(cfg: DictConfig) -> None:
    root = Path(__file__).resolve().parents[1]
    resolved = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(resolved, dict):
        raise TypeError("resolved cube config must be a mapping")
    cube = resolved.get("cube")
    if not isinstance(cube, Mapping):
        raise TypeError("cube config must be a mapping")
    if cube.get("stage") not in {
        "enforcement_cube_confirmation",
        "enforcement_cube_smoke",
    }:
        raise RuntimeError("unsupported enforcement-cube stage")
    if [str(value) for value in cube["derived_mechanisms"]] != list(
        DERIVED_SPEC
    ):
        raise RuntimeError("derived mechanisms differ from the frozen cube")
    if int(cube["expected_derived_records"]) != 3 * len(resolved["seeds"]):
        raise RuntimeError("derived record count is inconsistent with the seed list")
    if cube["stage"] == "enforcement_cube_confirmation":
        formal_cube_seeds(resolved)
        if int(cube["expected_core_records"]) != 150:
            raise RuntimeError("formal cube requires exactly 150 core records")
        if int(cube["expected_trained_checkpoints"]) != 120:
            raise RuntimeError("formal cube requires exactly 120 trained checkpoints")
        if int(cube["expected_derived_records"]) != 90:
            raise RuntimeError("formal cube requires exactly 90 derived records")
        if len(resolved["evaluation"]["case_names"]) * len(
            resolved["evaluation"]["horizons"]
        ) != 12:
            raise RuntimeError("formal cube requires the 12 frozen evaluation cells")

    protocol_path = _validate_hashed_artifact(
        root,
        str(cube["protocol_path"]),
        str(cube["protocol_sha256"]),
        "cube protocol",
    )
    runtime_amendment_path = _validate_hashed_artifact(
        root,
        str(cube["runtime_amendment_path"]),
        str(cube["runtime_amendment_sha256"]),
        "cube runtime amendment",
    )
    decision_path = _validate_hashed_artifact(
        root,
        str(cube["decision_path"]),
        str(cube["decision_sha256"]),
        "cube scientific decision",
    )
    factorial_protocol_path = _validate_hashed_artifact(
        root,
        str(resolved["protocol_path"]),
        str(resolved["protocol_sha256"]),
        "factorial protocol",
    )
    factorial_decision_path = resolve_path(root, str(resolved["decision_path"]))
    if not factorial_decision_path.is_file():
        raise RuntimeError("factorial decision is missing")

    core_records_path = resolve_path(root, str(resolved["output"]))
    core_analysis_path = resolve_path(root, str(cube["core_analysis"]))
    if not core_records_path.is_file() or not core_analysis_path.is_file():
        raise RuntimeError("cube activation requires complete core records and analysis")
    core_records = read_records(core_records_path)
    if len(core_records) != int(cube["expected_core_records"]):
        raise RuntimeError("parent core does not have exactly 150 records")
    core = validate_factorial_records(core_records, resolved)
    completed_core_analysis = json.loads(
        core_analysis_path.read_text(encoding="utf-8")
    )
    if completed_core_analysis.get("input_sha256") != sha256_file(core_records_path):
        raise RuntimeError("core analysis is not bound to the complete parent JSONL")
    if not completed_core_analysis.get("integrity_gates_passed", False):
        raise RuntimeError("core analysis did not pass its integrity gates")

    dataset_path = resolve_path(root, str(resolved["dataset"]["path"]))
    data_lock_path, data_lock_sha256, data_lock = validate_data_lock(
        root=root, resolved=resolved, dataset_path=dataset_path
    )
    if data_lock_sha256 != str(resolved["dataset"]["lock_sha256"]):
        raise RuntimeError("validated data-lock SHA-256 differs from the frozen config")

    checkpoint_lock_path, checkpoint_lock_sha256, checkpoint_lock = (
        create_or_validate_checkpoint_lock(
            root=root,
            core=core,
            config=resolved,
            core_records_path=core_records_path,
            core_analysis_path=core_analysis_path,
        )
    )
    checkpoint_entries = validate_checkpoint_files_against_lock(
        root=root, checkpoint_lock=checkpoint_lock, config=resolved
    )

    config_path = resolve_path(
        root,
        str(
            cube.get(
                "config_path",
                "configs/constraint_iclr/"
                "pdebench_advection_fno_enforcement_cube_20260901.yaml",
            )
        ),
    )
    if not config_path.is_file():
        raise RuntimeError(f"cube config is missing: {config_path}")
    source_files = [
        Path(__file__),
        root / "scripts/analyze_constraint_iclr_pdebench_enforcement_cube.py",
        root / "scripts/analyze_constraint_iclr_pdebench_factorial.py",
        root / "scripts/analyze_constraint_iclr_pdebench.py",
        root / "scripts/run_constraint_iclr_pdebench_fno.py",
        root / "scripts/constraint_iclr_common.py",
        config_path,
        protocol_path,
        runtime_amendment_path,
        decision_path,
        factorial_protocol_path,
        factorial_decision_path,
        data_lock_path,
        core_analysis_path,
        checkpoint_lock_path,
    ]
    shared_provenance = provenance(
        root=root, resolved_config=resolved, source_files=source_files
    )
    if shared_provenance["git_head"] != str(resolved["expected_git_head"]):
        raise RuntimeError("unexpected Git HEAD for enforcement cube")
    if bool(shared_provenance["git_dirty"]) is not bool(
        resolved["expected_git_dirty"]
    ):
        raise RuntimeError("unexpected dirty-worktree state for enforcement cube")

    device = torch.device(str(resolved["device"]))
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    model_cfg = resolved["model"]
    evaluation_cfg = resolved["evaluation"]
    history = int(model_cfg["history"])
    confirmation_indices = np.arange(
        int(resolved["split"]["confirmation_start"]),
        int(resolved["split"]["confirmation_start"])
        + int(resolved["split"]["confirmation_count"]),
        dtype=np.int64,
    )
    evaluation_trajectories = load_trajectories(
        dataset_path,
        confirmation_indices,
        temporal_stride=int(resolved["training"]["temporal_stride"]),
        spatial_stride=1,
    )
    native_grid = load_x_coordinate(dataset_path, 1)
    output_path = resolve_path(root, str(cube["output"]))
    completed = _existing_ids(output_path)
    core_records_sha256 = sha256_file(core_records_path)
    core_analysis_sha256 = sha256_file(core_analysis_path)
    dataset_sha256 = str(data_lock["inspection"]["sha256"])

    for seed in [int(value) for value in resolved["seeds"]]:
        for mechanism, spec in DERIVED_SPEC.items():
            parent_mechanism = str(spec["parent"])
            parent = core[(seed, parent_mechanism)]
            checkpoint_entry = checkpoint_entries[(seed, parent_mechanism)]
            identity = {
                "schema_version": cube["schema_version"],
                "stage": cube["stage"],
                "benchmark_id": resolved["benchmark_id"],
                "dataset_sha256": dataset_sha256,
                "data_lock_sha256": data_lock_sha256,
                "factorial_protocol_sha256": resolved["protocol_sha256"],
                "cube_protocol_sha256": cube["protocol_sha256"],
                "cube_runtime_amendment_sha256": cube[
                    "runtime_amendment_sha256"
                ],
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
                raise RuntimeError(
                    f"parent checkpoint changed before derived evaluation: {checkpoint_path}"
                )
            checkpoint = _checkpoint_payload(
                checkpoint_path,
                expected_run_id=str(parent["run_id"]),
                expected_schema=str(cube["checkpoint_schema_version"]),
                expected_epochs=int(cube["checkpoint_completed_epochs"]),
            )
            model = build_model(model_cfg, str(spec["forward_map"])).to(device)
            model.load_state_dict(checkpoint["model_state_dict"], strict=True)
            parameter_count = count_trainable_parameters(model)
            if parameter_count != int(parent["compute"]["trainable_parameters"]):
                raise RuntimeError(
                    f"parent parameter count mismatch for seed {seed}, {mechanism}"
                )
            if device.type == "cuda":
                torch.cuda.reset_peak_memory_stats(device)
            started = time.perf_counter()
            cases, projection_identity = evaluate_cases(
                model=model,
                native_trajectories=evaluation_trajectories,
                native_grid=native_grid,
                evaluation_cfg=evaluation_cfg,
                history=history,
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
                raise FloatingPointError("non-finite enforcement-cube metric")
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
                    "provenance_sha256": canonical_object_sha256(
                        parent["provenance"]
                    ),
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
    config_name="pdebench_advection_fno_enforcement_cube_20260901",
)
def main(cfg: DictConfig) -> None:
    run_cube(cfg)


if __name__ == "__main__":
    main()
