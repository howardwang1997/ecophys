"""Admit the frozen PDEBench 2D shallow-water radial-dam-break file."""

from __future__ import annotations

import argparse
import hashlib
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

LOCK_SCHEMA_VERSION = "constraint-iclr-pdebench-swe-data-lock-v1"


def md5_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def restrict_swe_numpy(values: np.ndarray, factor: int, method: str) -> np.ndarray:
    array = np.asarray(values)
    if array.ndim < 2 or factor <= 0:
        raise ValueError("SWE restriction requires two spatial axes and a positive factor")
    nx, ny = array.shape[-2:]
    if nx % factor != 0 or ny % factor != 0:
        raise ValueError("SWE restriction factor must divide both spatial axes")
    if factor == 1:
        return np.asarray(array, dtype=np.float32)
    if method == "point":
        return np.asarray(array[..., ::factor, ::factor], dtype=np.float32)
    if method == "block_average":
        reshaped = array.reshape(
            *array.shape[:-2], nx // factor, factor, ny // factor, factor
        )
        return np.mean(reshaped, axis=(-3, -1), dtype=np.float64).astype(np.float32)
    raise ValueError(f"unsupported SWE restriction method: {method}")


def _coordinate_report(
    values: np.ndarray,
    *,
    expected_length: int,
    expected_start: float,
    expected_stop: float,
    expected_spacing: float,
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
    spacing_error = float(np.max(np.abs(differences - expected_spacing)))
    if abs(float(coordinate[0]) - expected_start) > atol:
        raise RuntimeError("coordinate start differs from the frozen SWE contract")
    if abs(float(coordinate[-1]) - expected_stop) > atol:
        raise RuntimeError("coordinate stop differs from the frozen SWE contract")
    if spacing_error > atol:
        raise RuntimeError("coordinate spacing differs from the frozen SWE contract")
    return {
        "length": int(coordinate.size),
        "start": float(coordinate[0]),
        "stop": float(coordinate[-1]),
        "mean_spacing": float(np.mean(differences)),
        "max_spacing_error": spacing_error,
        "strictly_increasing": True,
    }


def _group_name(index: int, width: int) -> str:
    return str(index).zfill(width)


def scan_swe_dataset(path: Path, dataset_cfg: Mapping[str, Any]) -> dict[str, Any]:
    expected_groups = int(dataset_cfg["expected_groups"])
    width = int(dataset_cfg["group_name_width"])
    expected_names = [_group_name(index, width) for index in range(expected_groups)]
    expected_shape = tuple(int(value) for value in dataset_cfg["expected_shape"])
    expected_dtype = str(dataset_cfg["expected_dtype"])
    data_key = str(dataset_cfg["data_key"])
    threshold = float(dataset_cfg["max_abs_mean_drift"])
    factors = [int(value) for value in dataset_cfg["invariant_spatial_factors"]]
    restriction_method = str(dataset_cfg["restriction_method"])
    identity_atol = float(dataset_cfg["restriction_identity_atol"])
    coordinate_atol = float(dataset_cfg["coordinate_atol"])
    require_positive = bool(dataset_cfg["require_strict_positive"])
    if expected_shape != (101, 128, 128, 1):
        raise RuntimeError("SWE schema must retain the frozen [101,128,128,1] shape")
    if any(factor <= 0 or 128 % factor != 0 for factor in factors):
        raise RuntimeError("every SWE restriction factor must divide the native grid")

    maximum_drift = 0.0
    drift_sum = 0.0
    drift_count = 0
    global_minimum = math.inf
    global_maximum = -math.inf
    restriction_maxima = {str(factor): 0.0 for factor in factors if factor != 1}
    with h5py.File(path, "r") as handle:
        observed_names = sorted(str(name) for name in handle)
        if observed_names != expected_names:
            missing = sorted(set(expected_names).difference(observed_names))
            extra = sorted(set(observed_names).difference(expected_names))
            raise RuntimeError(
                "SWE top-level group contract failed: "
                f"count={len(observed_names)}, missing={missing[:5]}, extra={extra[:5]}"
            )
        reference_coordinates: dict[str, np.ndarray] = {}
        coordinate_reports: dict[str, Any] = {}
        for index, name in enumerate(expected_names):
            group = handle[name]
            required = {data_key, "grid"}
            if not required.issubset(group.keys()):
                raise RuntimeError(f"SWE group {name} is missing data or grid")
            if not {"x", "y", "t"}.issubset(group["grid"].keys()):
                raise RuntimeError(f"SWE group {name} is missing a grid coordinate")
            dataset = group[data_key]
            observed_shape = tuple(int(value) for value in dataset.shape)
            observed_dtype = np.dtype(dataset.dtype).name
            if observed_shape != expected_shape:
                raise RuntimeError(
                    f"SWE group {name} shape mismatch: {observed_shape}"
                )
            if observed_dtype != expected_dtype:
                raise RuntimeError(
                    f"SWE group {name} dtype mismatch: {observed_dtype}"
                )
            coordinates = {
                axis: np.asarray(group[f"grid/{axis}"], dtype=np.float32)
                for axis in ("x", "y", "t")
            }
            if index == 0:
                reference_coordinates = coordinates
                coordinate_reports = {
                    "x": _coordinate_report(
                        coordinates["x"],
                        expected_length=128,
                        expected_start=float(dataset_cfg["expected_x_start"]),
                        expected_stop=float(dataset_cfg["expected_x_stop"]),
                        expected_spacing=float(dataset_cfg["expected_spatial_spacing"]),
                        atol=coordinate_atol,
                    ),
                    "y": _coordinate_report(
                        coordinates["y"],
                        expected_length=128,
                        expected_start=float(dataset_cfg["expected_y_start"]),
                        expected_stop=float(dataset_cfg["expected_y_stop"]),
                        expected_spacing=float(dataset_cfg["expected_spatial_spacing"]),
                        atol=coordinate_atol,
                    ),
                    "t": _coordinate_report(
                        coordinates["t"],
                        expected_length=101,
                        expected_start=float(dataset_cfg["expected_t_start"]),
                        expected_stop=float(dataset_cfg["expected_t_stop"]),
                        expected_spacing=float(dataset_cfg["expected_temporal_spacing"]),
                        atol=coordinate_atol,
                    ),
                }
            else:
                for axis, coordinate in coordinates.items():
                    if not np.array_equal(coordinate, reference_coordinates[axis]):
                        raise RuntimeError(
                            f"SWE group {name} {axis} coordinate differs from group 0000"
                        )

            values = np.asarray(dataset[..., 0], dtype=np.float32)
            if not np.isfinite(values).all():
                raise RuntimeError(f"SWE group {name} contains a non-finite depth")
            minimum = float(np.min(values))
            maximum = float(np.max(values))
            if require_positive and minimum <= 0.0:
                raise RuntimeError(f"SWE group {name} contains non-positive depth")
            global_minimum = min(global_minimum, minimum)
            global_maximum = max(global_maximum, maximum)
            native_means = np.mean(values, axis=(-2, -1), dtype=np.float64)
            drift = np.abs(native_means - native_means[:1])
            maximum_drift = max(maximum_drift, float(np.max(drift)))
            drift_sum += float(np.sum(drift, dtype=np.float64))
            drift_count += int(drift.size)
            for factor in factors:
                if factor == 1:
                    continue
                restricted = restrict_swe_numpy(values, factor, restriction_method)
                restricted_means = np.mean(restricted, axis=(-2, -1), dtype=np.float64)
                restriction_maxima[str(factor)] = max(
                    restriction_maxima[str(factor)],
                    float(np.max(np.abs(restricted_means - native_means))),
                )

    drift_passed = maximum_drift <= threshold
    identity_passed = all(
        value <= identity_atol for value in restriction_maxima.values()
    )
    admitted = drift_passed and identity_passed
    report = {
        "groups": expected_groups,
        "group_name_first": expected_names[0],
        "group_name_last": expected_names[-1],
        "data_shape": list(expected_shape),
        "data_dtype": expected_dtype,
        "coordinates": coordinate_reports,
        "all_finite": True,
        "strictly_positive": global_minimum > 0.0,
        "minimum_depth": global_minimum,
        "maximum_depth": global_maximum,
        "max_abs_depth_mean_drift": maximum_drift,
        "mean_abs_depth_mean_drift": drift_sum / drift_count,
        "depth_drift_threshold": threshold,
        "restriction_method": restriction_method,
        "restriction_identity_max_abs_by_factor": restriction_maxima,
        "restriction_identity_atol": identity_atol,
        "restriction_identity_passed": identity_passed,
        "admitted": admitted,
    }
    if not admitted:
        raise RuntimeError(
            "SWE invariant gate failed: "
            f"max_drift={maximum_drift}, threshold={threshold}, "
            f"restriction={restriction_maxima}, identity_atol={identity_atol}"
        )
    return report


def inspect_swe_dataset(path: Path, dataset_cfg: Mapping[str, Any]) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"SWE dataset does not exist: {path}")
    observed_bytes = path.stat().st_size
    expected_bytes = int(dataset_cfg["expected_bytes"])
    if observed_bytes != expected_bytes:
        raise RuntimeError(
            f"SWE byte count mismatch: expected {expected_bytes}, got {observed_bytes}"
        )
    observed_md5 = md5_file(path)
    if observed_md5 != str(dataset_cfg["expected_md5"]):
        raise RuntimeError("SWE MD5 differs from the official PDEBench checksum")
    observed_sha256 = sha256_file(path)
    expected_sha256 = dataset_cfg.get("expected_sha256")
    if expected_sha256 and observed_sha256 != str(expected_sha256):
        raise RuntimeError("SWE SHA-256 differs from the frozen transport object")
    return {
        "bytes": observed_bytes,
        "md5": observed_md5,
        "sha256": observed_sha256,
        "hdf5": scan_swe_dataset(path, dataset_cfg),
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
    artifacts: dict[str, dict[str, str]] = {}
    for key, label in (
        ("protocol", "SWE protocol"),
        ("source_metadata", "SWE source metadata"),
        ("data_decision", "SWE data decision"),
        ("transport_decision", "SWE transport decision"),
    ):
        path = _validate_artifact(
            root,
            str(config[f"{key}_path"]),
            str(config[f"{key}_sha256"]),
            label,
        )
        artifacts[key] = {
            "path": str(config[f"{key}_path"]),
            "sha256": sha256_file(path),
        }
    dataset_path = Path(str(dataset_cfg["path"]))
    if not dataset_path.is_absolute():
        dataset_path = root / dataset_path
    inspection = inspect_swe_dataset(dataset_path, dataset_cfg)
    lock = {
        "schema_version": LOCK_SCHEMA_VERSION,
        "benchmark_id": config["benchmark_id"],
        **artifacts,
        "dataset": {
            "path": str(dataset_cfg["path"]),
            "filename": str(dataset_cfg["filename"]),
            "dataverse_file_id": int(dataset_cfg["dataverse_file_id"]),
        },
        "inspection": inspection,
        "admitted": True,
    }
    lock_path = Path(str(dataset_cfg["lock_path"]))
    if not lock_path.is_absolute():
        lock_path = root / lock_path
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = lock_path.with_suffix(lock_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, lock_path)
    return lock_path, lock


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default="configs/constraint_iclr/pdebench_swe_rdb_factorial_20260902.yaml",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    config = load_config(root / args.config)
    lock_path, lock = prepare_lock(config, root)
    print(
        json.dumps(
            {
                "lock_path": str(lock_path),
                "lock_sha256": sha256_file(lock_path),
                "dataset_sha256": lock["inspection"]["sha256"],
                "admitted": lock["admitted"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
