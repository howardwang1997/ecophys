"""Admit the frozen PDEBench periodic 1D compressible-NS dataset."""

from __future__ import annotations

import argparse
import json
import math
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import h5py
import numpy as np
from analyze_constraint_iclr_pdebench import load_config
from constraint_iclr_common import sha256_file
from run_constraint_iclr_pdebench_fno import restrict_spatial_numpy

LOCK_SCHEMA_VERSION = "constraint-iclr-pdebench-cns-data-lock-v1"


def _coordinate_report(
    values: np.ndarray,
    *,
    expected_length: int,
    expected_start: float,
    expected_end: float,
    periodic: bool,
    atol: float,
) -> dict[str, float | int | bool]:
    coordinate = np.asarray(values, dtype=np.float64)
    if coordinate.shape != (expected_length,):
        raise RuntimeError(
            f"coordinate shape mismatch: expected {(expected_length,)}, got {coordinate.shape}"
        )
    if not np.isfinite(coordinate).all():
        raise RuntimeError("coordinate contains a non-finite value")
    differences = np.diff(coordinate)
    if not np.all(differences > 0.0):
        raise RuntimeError("coordinate must be strictly increasing")
    spacing = float(np.mean(differences))
    uniform_error = float(np.max(np.abs(differences - spacing)))
    observed_end = (
        float(coordinate[-1] - coordinate[0] + spacing)
        if periodic
        else float(coordinate[-1])
    )
    if abs(float(coordinate[0]) - expected_start) > atol:
        raise RuntimeError("coordinate start does not match the frozen CNS contract")
    if abs(observed_end - expected_end) > atol:
        raise RuntimeError("coordinate end/period does not match the frozen CNS contract")
    if uniform_error > atol:
        raise RuntimeError("coordinate is not uniform within the frozen CNS tolerance")
    return {
        "length": int(coordinate.size),
        "start": float(coordinate[0]),
        "observed_end_or_period": observed_end,
        "mean_spacing": spacing,
        "max_uniform_spacing_error": uniform_error,
        "strictly_increasing": True,
    }


def scan_cns_dataset(path: Path, dataset_cfg: Mapping[str, Any]) -> dict[str, Any]:
    expected_shape = tuple(int(value) for value in dataset_cfg["expected_shape"])
    expected_dtype = str(dataset_cfg["expected_dtype"])
    fields = [str(value) for value in dataset_cfg["fields"]]
    invariant_field = str(dataset_cfg["invariant_field"])
    strides = [int(value) for value in dataset_cfg["invariant_spatial_strides"]]
    chunk_size = int(dataset_cfg["scan_chunk_trajectories"])
    restriction_method = str(dataset_cfg["restriction_method"])
    drift_threshold = float(dataset_cfg["max_abs_mean_drift"])
    identity_atol = float(dataset_cfg["restriction_identity_atol"])
    if len(expected_shape) != 3:
        raise RuntimeError("CNS fields must use the frozen [trajectory,time,x] shape")
    if invariant_field not in fields:
        raise RuntimeError("frozen invariant field is not included in the channel list")
    if any(stride <= 0 or expected_shape[-1] % stride != 0 for stride in strides):
        raise RuntimeError("every CNS restriction factor must divide the native grid")

    maximum_drift = 0.0
    drift_sum = 0.0
    drift_count = 0
    restriction_maxima = {str(stride): 0.0 for stride in strides if stride != 1}
    field_abs_maxima = {field: 0.0 for field in fields}
    with h5py.File(path, "r") as handle:
        required = {*fields, "x-coordinate", "t-coordinate"}
        missing = required.difference(handle.keys())
        if missing:
            raise RuntimeError(f"CNS HDF5 is missing required keys: {sorted(missing)}")
        for field in fields:
            dataset = handle[field]
            observed_shape = tuple(int(value) for value in dataset.shape)
            observed_dtype = np.dtype(dataset.dtype).name
            if observed_shape != expected_shape:
                raise RuntimeError(
                    f"{field} shape mismatch: expected {expected_shape}, got {observed_shape}"
                )
            if observed_dtype != expected_dtype:
                raise RuntimeError(
                    f"{field} dtype mismatch: expected {expected_dtype}, got {observed_dtype}"
                )
        x_report = _coordinate_report(
            np.asarray(handle["x-coordinate"]),
            expected_length=expected_shape[2],
            expected_start=float(dataset_cfg["expected_x_start"]),
            expected_end=float(dataset_cfg["expected_x_period"]),
            periodic=True,
            atol=float(dataset_cfg["coordinate_atol"]),
        )
        t_report = _coordinate_report(
            np.asarray(handle["t-coordinate"]),
            expected_length=expected_shape[1],
            expected_start=float(dataset_cfg["expected_t_start"]),
            expected_end=float(dataset_cfg["expected_t_stop"]),
            periodic=False,
            atol=float(dataset_cfg["coordinate_atol"]),
        )
        attribute_atol = float(dataset_cfg["attribute_atol"])
        attributes = {}
        for name in ("eta", "zeta"):
            if name not in handle.attrs:
                raise RuntimeError(f"CNS HDF5 is missing the {name} attribute")
            observed = float(handle.attrs[name])
            expected = float(dataset_cfg[f"expected_{name}"])
            if not math.isfinite(observed) or abs(observed - expected) > attribute_atol:
                raise RuntimeError(f"CNS {name} attribute does not match the frozen contract")
            attributes[name] = observed

        for start in range(0, expected_shape[0], chunk_size):
            stop = min(start + chunk_size, expected_shape[0])
            for field in fields:
                values = np.asarray(handle[field][start:stop], dtype=np.float32)
                if not np.isfinite(values).all():
                    raise RuntimeError(
                        f"{field} contains a non-finite value in trajectories {start}:{stop}"
                    )
                field_abs_maxima[field] = max(
                    field_abs_maxima[field], float(np.max(np.abs(values)))
                )
                if field != invariant_field:
                    continue
                native_means = np.mean(values, axis=-1, dtype=np.float64)
                drift = np.abs(native_means - native_means[:, :1])
                maximum_drift = max(maximum_drift, float(np.max(drift)))
                drift_sum += float(np.sum(drift, dtype=np.float64))
                drift_count += int(drift.size)
                for stride in strides:
                    if stride == 1:
                        continue
                    restricted = restrict_spatial_numpy(
                        values, stride, restriction_method
                    )
                    restricted_means = np.mean(
                        restricted, axis=-1, dtype=np.float64
                    )
                    restriction_maxima[str(stride)] = max(
                        restriction_maxima[str(stride)],
                        float(np.max(np.abs(restricted_means - native_means))),
                    )
    drift_passed = maximum_drift <= drift_threshold
    identity_passed = all(value <= identity_atol for value in restriction_maxima.values())
    admitted = drift_passed and identity_passed
    report = {
        "fields": fields,
        "shape_by_field": {field: list(expected_shape) for field in fields},
        "dtype_by_field": {field: expected_dtype for field in fields},
        "all_finite": True,
        "field_abs_maxima": field_abs_maxima,
        "x_coordinate": x_report,
        "t_coordinate": t_report,
        "attributes": attributes,
        "invariant_field": invariant_field,
        "max_abs_density_mean_drift": maximum_drift,
        "mean_abs_density_mean_drift": drift_sum / drift_count,
        "density_drift_threshold": drift_threshold,
        "restriction_method": restriction_method,
        "restriction_identity_max_abs_by_factor": restriction_maxima,
        "restriction_identity_atol": identity_atol,
        "restriction_identity_passed": identity_passed,
        "admitted": admitted,
    }
    if not admitted:
        raise RuntimeError(
            "CNS invariant gate failed: "
            f"max_drift={maximum_drift}, threshold={drift_threshold}, "
            f"restriction={restriction_maxima}, identity_atol={identity_atol}"
        )
    return report


def inspect_cns_dataset(path: Path, dataset_cfg: Mapping[str, Any]) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"CNS dataset does not exist: {path}")
    observed_bytes = path.stat().st_size
    expected_bytes = int(dataset_cfg["expected_bytes"])
    if observed_bytes != expected_bytes:
        raise RuntimeError(
            f"CNS byte count mismatch: expected {expected_bytes}, got {observed_bytes}"
        )
    observed_sha256 = sha256_file(path)
    expected_sha256 = str(dataset_cfg["expected_sha256"])
    if observed_sha256 != expected_sha256:
        raise RuntimeError(
            f"CNS SHA-256 mismatch: expected {expected_sha256}, got {observed_sha256}"
        )
    return {
        "bytes": observed_bytes,
        "sha256": observed_sha256,
        "hdf5": scan_cns_dataset(path, dataset_cfg),
    }


def _validate_artifact(root: Path, raw_path: str, expected: str, label: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = root / path
    if not path.is_file():
        raise RuntimeError(f"{label} is missing: {path}")
    observed = sha256_file(path)
    if observed != expected:
        raise RuntimeError(
            f"{label} SHA-256 mismatch: expected {expected}, got {observed}"
        )
    return path


def prepare_lock(config: dict[str, Any], root: Path) -> tuple[Path, dict[str, Any]]:
    dataset_cfg = config["dataset"]
    protocol_path = _validate_artifact(
        root, config["protocol_path"], config["protocol_sha256"], "CNS protocol"
    )
    source_path = _validate_artifact(
        root,
        config["source_metadata_path"],
        config["source_metadata_sha256"],
        "CNS source metadata",
    )
    decision_path = _validate_artifact(
        root,
        config["data_decision_path"],
        config["data_decision_sha256"],
        "CNS data decision",
    )
    dataset_path = Path(dataset_cfg["path"])
    if not dataset_path.is_absolute():
        dataset_path = root / dataset_path
    inspection = inspect_cns_dataset(dataset_path, dataset_cfg)
    lock = {
        "schema_version": LOCK_SCHEMA_VERSION,
        "benchmark_id": config["benchmark_id"],
        "protocol": {
            "path": config["protocol_path"],
            "sha256": sha256_file(protocol_path),
        },
        "source_metadata": {
            "path": config["source_metadata_path"],
            "sha256": sha256_file(source_path),
        },
        "data_decision": {
            "path": config["data_decision_path"],
            "sha256": sha256_file(decision_path),
        },
        "inspection": inspection,
    }
    lock_path = Path(dataset_cfg["lock_path"])
    if not lock_path.is_absolute():
        lock_path = root / lock_path
    return lock_path, lock


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(
            "configs/constraint_iclr/pdebench_cns_eta0p01_factorial_20260901.yaml"
        ),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    config_path = args.config if args.config.is_absolute() else root / args.config
    config = load_config(config_path)
    lock_path, lock = prepare_lock(config, root)
    if args.output is not None:
        lock_path = args.output if args.output.is_absolute() else root / args.output
    canonical = json.dumps(lock, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if lock_path.exists():
        if lock_path.read_text(encoding="utf-8") != canonical:
            raise RuntimeError("existing CNS data lock differs from the frozen admission result")
    else:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = lock_path.with_suffix(lock_path.suffix + ".tmp")
        temporary.write_text(canonical, encoding="utf-8")
        os.replace(temporary, lock_path)
    print(f"data_lock={lock_path}")
    print(f"data_lock_sha256={sha256_file(lock_path)}")


if __name__ == "__main__":
    main()
