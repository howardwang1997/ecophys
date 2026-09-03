"""Run the frozen PDEBench 1D-advection FNO external-validity experiment."""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import h5py
import hydra
import numpy as np
import torch
import torch.nn.functional as functional
from constraint_iclr_common import (
    append_jsonl,
    canonical_run_id,
    count_trainable_parameters,
    provenance,
    seed_everything,
    sha256_file,
    stable_seed,
)
from omegaconf import DictConfig, OmegaConf
from torch import nn

EXTERNAL_SCHEMA_VERSION = "constraint-iclr-pdebench-v1"


def resolve_path(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def path_label(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def hash_file_dual(path: Path) -> dict[str, str]:
    md5 = hashlib.md5(usedforsecurity=False)
    sha256 = hashlib.sha256()
    bytes_read = 0
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            bytes_read += len(block)
            md5.update(block)
            sha256.update(block)
    if bytes_read != path.stat().st_size:
        raise RuntimeError(
            f"dataset read returned {bytes_read} bytes but stat reports {path.stat().st_size}; "
            "the file may be a dataless placeholder"
        )
    return {"md5": md5.hexdigest(), "sha256": sha256.hexdigest()}


def restrict_spatial_numpy(values: np.ndarray, factor: int, method: str) -> np.ndarray:
    if factor <= 0 or values.shape[-1] % factor != 0:
        raise ValueError("restriction factor must divide the spatial resolution")
    if factor == 1:
        return np.asarray(values, dtype=np.float32)
    if method == "point":
        return np.asarray(values[..., ::factor], dtype=np.float32)
    if method == "block_average":
        reshaped = values.reshape(*values.shape[:-1], values.shape[-1] // factor, factor)
        return np.mean(reshaped, axis=-1, dtype=np.float64).astype(np.float32)
    raise ValueError(f"unsupported spatial restriction method: {method}")


def restrict_spatial_torch(values: torch.Tensor, factor: int, method: str) -> torch.Tensor:
    if factor <= 0 or values.shape[-1] % factor != 0:
        raise ValueError("restriction factor must divide the spatial resolution")
    if factor == 1:
        return values
    if method == "point":
        return values[..., ::factor].contiguous()
    if method == "block_average":
        reshaped = values.reshape(*values.shape[:-1], values.shape[-1] // factor, factor)
        return reshaped.to(dtype=torch.float64).mean(dim=-1).to(dtype=values.dtype)
    raise ValueError(f"unsupported spatial restriction method: {method}")


def restrict_grid(grid: torch.Tensor, factor: int, method: str) -> torch.Tensor:
    return restrict_spatial_torch(grid, factor, method).contiguous()


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
    observed_end = float(coordinate[-1] - coordinate[0] + spacing) if periodic else float(coordinate[-1])
    if abs(float(coordinate[0]) - expected_start) > atol:
        raise RuntimeError("coordinate start does not match the frozen contract")
    if abs(observed_end - expected_end) > atol:
        raise RuntimeError("coordinate end/period does not match the frozen contract")
    if uniform_error > atol:
        raise RuntimeError("coordinate is not uniform within the frozen tolerance")
    return {
        "length": int(coordinate.size),
        "start": float(coordinate[0]),
        "observed_end_or_period": observed_end,
        "mean_spacing": spacing,
        "max_uniform_spacing_error": uniform_error,
        "strictly_increasing": True,
    }


def scan_public_dataset(path: Path, dataset_cfg: Mapping[str, Any]) -> dict[str, Any]:
    expected_shape = tuple(int(value) for value in dataset_cfg["expected_shape"])
    expected_dtype = str(dataset_cfg["expected_dtype"])
    strides = [int(value) for value in dataset_cfg["invariant_spatial_strides"]]
    threshold = float(dataset_cfg["max_abs_mean_drift"])
    restriction_method = str(dataset_cfg.get("restriction_method", "point"))
    restriction_identity_atol = float(dataset_cfg.get("restriction_identity_atol", 0.0))
    chunk_size = int(dataset_cfg["scan_chunk_trajectories"])
    if len(expected_shape) != 3:
        raise RuntimeError("PDEBench scalar contract requires a rank-three tensor")
    if any(stride <= 0 or expected_shape[-1] % stride != 0 for stride in strides):
        raise RuntimeError("every invariant stride must divide the native resolution")

    maxima = {str(stride): 0.0 for stride in strides}
    drift_sums = {str(stride): 0.0 for stride in strides}
    drift_counts = {str(stride): 0 for stride in strides}
    restriction_identity_maxima = {str(stride): 0.0 for stride in strides if stride != 1}
    with h5py.File(path, "r") as handle:
        required = {"tensor", "x-coordinate", "t-coordinate"}
        missing = required.difference(handle.keys())
        if missing:
            raise RuntimeError(f"HDF5 is missing required keys: {sorted(missing)}")
        tensor = handle["tensor"]
        observed_shape = tuple(int(value) for value in tensor.shape)
        observed_dtype = np.dtype(tensor.dtype).name
        if observed_shape != expected_shape:
            raise RuntimeError(f"tensor shape mismatch: expected {expected_shape}, got {observed_shape}")
        if observed_dtype != expected_dtype:
            raise RuntimeError(f"tensor dtype mismatch: expected {expected_dtype}, got {observed_dtype}")
        x_report = _coordinate_report(
            np.asarray(handle["x-coordinate"]),
            expected_length=expected_shape[2],
            expected_start=float(dataset_cfg["expected_x_start"]),
            expected_end=float(dataset_cfg["expected_x_period"]),
            periodic=True,
            atol=float(dataset_cfg["coordinate_atol"]),
        )
        raw_t_coordinate = np.asarray(handle["t-coordinate"], dtype=np.float64)
        expected_t_length = int(dataset_cfg.get("expected_t_coordinate_length", expected_shape[1]))
        if raw_t_coordinate.shape != (expected_t_length,):
            raise RuntimeError(
                "raw time-coordinate shape mismatch: "
                f"expected {(expected_t_length,)}, got {raw_t_coordinate.shape}"
            )
        t_report = _coordinate_report(
            raw_t_coordinate[: expected_shape[1]],
            expected_length=expected_shape[1],
            expected_start=float(dataset_cfg["expected_t_start"]),
            expected_end=float(dataset_cfg["expected_t_stop"]),
            periodic=False,
            atol=float(dataset_cfg["coordinate_atol"]),
        )
        trailing_t = raw_t_coordinate[expected_shape[1] :]
        expected_trailing_count = expected_t_length - expected_shape[1]
        if trailing_t.size != expected_trailing_count:
            raise RuntimeError("unexpected number of unused time coordinates")
        if expected_trailing_count:
            expected_trailing_stop = float(dataset_cfg["expected_t_trailing_stop"])
            if not np.isfinite(trailing_t).all() or abs(
                float(trailing_t[-1]) - expected_trailing_stop
            ) > float(dataset_cfg["coordinate_atol"]):
                raise RuntimeError("unused trailing time coordinate does not match the amendment")
        t_report["raw_length"] = int(raw_t_coordinate.size)
        t_report["unused_trailing_count"] = int(trailing_t.size)
        t_report["unused_trailing_stop"] = float(trailing_t[-1]) if trailing_t.size else None
        for start in range(0, expected_shape[0], chunk_size):
            stop = min(start + chunk_size, expected_shape[0])
            values = np.asarray(tensor[start:stop], dtype=np.float32)
            if not np.isfinite(values).all():
                raise RuntimeError(f"tensor contains a non-finite value in trajectories {start}:{stop}")
            native_means = np.mean(values, axis=-1, dtype=np.float64)
            for stride in strides:
                restricted = restrict_spatial_numpy(values, stride, restriction_method)
                means = np.mean(restricted, axis=-1, dtype=np.float64)
                drift = np.abs(means - means[:, :1])
                label = str(stride)
                maxima[label] = max(maxima[label], float(np.max(drift)))
                drift_sums[label] += float(np.sum(drift, dtype=np.float64))
                drift_counts[label] += int(drift.size)
                if stride != 1:
                    restriction_identity_maxima[label] = max(
                        restriction_identity_maxima[label],
                        float(np.max(np.abs(means - native_means))),
                    )

    drift_admitted = all(value <= threshold for value in maxima.values())
    identity_admitted = restriction_method != "block_average" or all(
        value <= restriction_identity_atol for value in restriction_identity_maxima.values()
    )
    admitted = drift_admitted and identity_admitted
    report = {
        "shape": list(expected_shape),
        "dtype": expected_dtype,
        "all_finite": True,
        "x_coordinate": x_report,
        "t_coordinate": t_report,
        "max_abs_mean_drift_by_spatial_stride": maxima,
        "mean_abs_mean_drift_by_spatial_stride": {
            label: drift_sums[label] / drift_counts[label] for label in maxima
        },
        "threshold": threshold,
        "restriction_method": restriction_method,
        "restriction_identity_max_abs_by_factor": restriction_identity_maxima,
        "restriction_identity_atol": restriction_identity_atol,
        "restriction_identity_passed": identity_admitted,
        "admitted": admitted,
    }
    if not admitted:
        raise RuntimeError(
            "dataset invariant gate failed: "
            f"drift_maxima={maxima}, drift_threshold={threshold}, "
            f"restriction_identity_maxima={restriction_identity_maxima}, "
            f"restriction_identity_atol={restriction_identity_atol}"
        )
    return report


def inspect_public_dataset(path: Path, dataset_cfg: Mapping[str, Any]) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"dataset does not exist: {path}")
    observed_bytes = path.stat().st_size
    expected_bytes = int(dataset_cfg["expected_bytes"])
    if observed_bytes != expected_bytes:
        raise RuntimeError(f"dataset byte count mismatch: expected {expected_bytes}, got {observed_bytes}")
    hashes = hash_file_dual(path)
    expected_md5 = str(dataset_cfg["expected_md5"])
    if hashes["md5"] != expected_md5:
        raise RuntimeError(f"dataset MD5 mismatch: expected {expected_md5}, got {hashes['md5']}")
    expected_sha256 = dataset_cfg.get("expected_sha256")
    if expected_sha256 and hashes["sha256"] != str(expected_sha256):
        raise RuntimeError(f"dataset SHA-256 mismatch: expected {expected_sha256}, got {hashes['sha256']}")
    return {
        "bytes": observed_bytes,
        **hashes,
        "hdf5": scan_public_dataset(path, dataset_cfg),
    }


def validate_data_lock(
    *,
    root: Path,
    resolved: Mapping[str, Any],
    dataset_path: Path,
) -> tuple[Path, str, dict[str, Any]]:
    dataset_cfg = resolved["dataset"]
    if not isinstance(dataset_cfg, Mapping):
        raise TypeError("dataset config must be a mapping")
    raw_lock = dataset_cfg.get("lock_path")
    expected_lock_sha256 = dataset_cfg.get("lock_sha256")
    if not raw_lock or not expected_lock_sha256:
        raise RuntimeError("external confirmation/preflight requires a frozen data lock and SHA-256")
    lock_path = resolve_path(root, str(raw_lock))
    if not lock_path.is_file():
        raise RuntimeError(f"data lock does not exist: {lock_path}")
    actual_lock_sha256 = sha256_file(lock_path)
    if actual_lock_sha256 != str(expected_lock_sha256):
        raise RuntimeError(
            f"data-lock SHA-256 mismatch: expected {expected_lock_sha256}, got {actual_lock_sha256}"
        )
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if lock.get("schema_version") != "constraint-iclr-pdebench-data-lock-v1":
        raise RuntimeError("unsupported PDEBench data-lock schema")
    lock_benchmark_id = str(dataset_cfg.get("lock_benchmark_id", resolved["benchmark_id"]))
    if lock.get("benchmark_id") != lock_benchmark_id:
        raise RuntimeError("data lock benchmark identity mismatch")
    if not lock.get("inspection", {}).get("hdf5", {}).get("admitted", False):
        raise RuntimeError("data lock does not contain a passing invariant gate")
    if int(lock["inspection"]["bytes"]) != dataset_path.stat().st_size:
        raise RuntimeError("dataset byte count no longer matches the data lock")
    hashes = hash_file_dual(dataset_path)
    for algorithm in ("md5", "sha256"):
        if hashes[algorithm] != str(lock["inspection"][algorithm]):
            raise RuntimeError(f"dataset {algorithm.upper()} no longer matches the data lock")
    return lock_path, actual_lock_sha256, lock


def load_trajectories(
    path: Path,
    indices: Sequence[int] | np.ndarray,
    *,
    temporal_stride: int,
    spatial_stride: int,
    restriction_method: str = "point",
    read_chunk: int = 64,
) -> torch.Tensor:
    requested = np.asarray(indices, dtype=np.int64)
    if requested.ndim != 1 or requested.size == 0 or np.unique(requested).size != requested.size:
        raise ValueError("trajectory indices must be a non-empty unique vector")
    sort_order = np.argsort(requested)
    sorted_indices = requested[sort_order]
    chunks: list[np.ndarray] = []
    with h5py.File(path, "r") as handle:
        tensor = handle["tensor"]
        if sorted_indices[0] < 0 or sorted_indices[-1] >= tensor.shape[0]:
            raise IndexError("trajectory index is outside the dataset")
        for start in range(0, sorted_indices.size, read_chunk):
            chunk_indices = sorted_indices[start : start + read_chunk]
            if restriction_method == "point":
                values = np.asarray(
                    tensor[chunk_indices.tolist(), ::temporal_stride, ::spatial_stride],
                    dtype=np.float32,
                )
            else:
                native = np.asarray(tensor[chunk_indices.tolist(), ::temporal_stride, :], dtype=np.float32)
                values = restrict_spatial_numpy(native, spatial_stride, restriction_method)
            chunks.append(values)
    sorted_values = np.concatenate(chunks, axis=0)
    inverse = np.empty_like(sort_order)
    inverse[sort_order] = np.arange(sort_order.size)
    return torch.from_numpy(np.ascontiguousarray(sorted_values[inverse]))


def load_x_coordinate(path: Path, spatial_stride: int) -> torch.Tensor:
    with h5py.File(path, "r") as handle:
        values = np.asarray(handle["x-coordinate"][::spatial_stride], dtype=np.float32)
    return torch.from_numpy(values)


def select_training_indices(seed: int, split_cfg: Mapping[str, Any]) -> np.ndarray:
    start = int(split_cfg["train_pool_start"])
    stop = int(split_cfg["train_pool_stop"])
    count = int(split_cfg["train_trajectories_per_seed"])
    if count > stop - start:
        raise ValueError("training subset is larger than the frozen pool")
    rng = np.random.default_rng(stable_seed(seed, "pdebench-train-trajectories"))
    return rng.choice(np.arange(start, stop, dtype=np.int64), size=count, replace=False)


class SpectralConv1d(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, modes: int) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.modes = modes
        scale = 1.0 / (in_channels * out_channels)
        self.weights = nn.Parameter(scale * torch.rand(in_channels, out_channels, modes, dtype=torch.cfloat))

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        spectrum = torch.fft.rfft(inputs, dim=-1)
        if self.modes > spectrum.shape[-1]:
            raise RuntimeError("requested Fourier modes exceed the current resolution")
        output_spectrum = torch.zeros(
            inputs.shape[0],
            self.out_channels,
            spectrum.shape[-1],
            dtype=spectrum.dtype,
            device=inputs.device,
        )
        output_spectrum[..., : self.modes] = torch.einsum(
            "bix,iox->box", spectrum[..., : self.modes], self.weights
        )
        return torch.fft.irfft(output_spectrum, n=inputs.shape[-1], dim=-1)


class FNO1d(nn.Module):
    def __init__(
        self,
        *,
        history: int,
        modes: int,
        width: int,
        padding: int,
        projection_width: int,
        mechanism: str,
    ) -> None:
        super().__init__()
        if mechanism not in {"free", "free_res", "hard_abs", "hard", "soft30"}:
            raise ValueError(f"unsupported mechanism: {mechanism}")
        self.padding = padding
        self.mechanism = mechanism
        self.lift = nn.Linear(history + 1, width)
        self.spectral = nn.ModuleList([SpectralConv1d(width, width, modes) for _ in range(4)])
        self.pointwise = nn.ModuleList([nn.Conv1d(width, width, 1) for _ in range(4)])
        self.project1 = nn.Linear(width, projection_width)
        self.project2 = nn.Linear(projection_width, 1)

    def forward(self, history: torch.Tensor, grid: torch.Tensor) -> torch.Tensor:
        if history.ndim != 3:
            raise ValueError("FNO history must have shape [batch, x, time]")
        coordinate = grid.view(1, -1, 1).expand(history.shape[0], -1, -1)
        features = self.lift(torch.cat((history, coordinate), dim=-1)).permute(0, 2, 1)
        if self.padding:
            features = functional.pad(features, (0, self.padding))
        for index, (spectral, pointwise) in enumerate(zip(self.spectral, self.pointwise, strict=True)):
            features = spectral(features) + pointwise(features)
            if index < 3:
                features = functional.gelu(features)
        if self.padding:
            features = features[..., : -self.padding]
        raw = self.project2(functional.gelu(self.project1(features.permute(0, 2, 1)))).squeeze(-1)
        previous = history[..., -1]
        if self.mechanism == "free_res":
            return previous + raw
        if self.mechanism == "hard_abs":
            return raw + previous.mean(dim=-1, keepdim=True) - raw.mean(dim=-1, keepdim=True)
        if self.mechanism == "hard":
            return previous + raw - raw.mean(dim=-1, keepdim=True)
        return raw


def _unet_block(in_channels: int, out_channels: int) -> nn.Module:
    groups = math.gcd(8, out_channels)
    return nn.Sequential(
        nn.Conv1d(in_channels, out_channels, kernel_size=5, padding=2),
        nn.GroupNorm(groups, out_channels),
        nn.SiLU(),
        nn.Conv1d(out_channels, out_channels, kernel_size=5, padding=2),
        nn.GroupNorm(groups, out_channels),
        nn.SiLU(),
    )


class UNet1d(nn.Module):
    """Two-level fully convolutional U-Net for the architecture replication."""

    def __init__(self, *, history: int, channels: int, mechanism: str) -> None:
        super().__init__()
        if mechanism not in {"free", "free_res", "hard_abs", "hard", "soft30"}:
            raise ValueError(f"unsupported mechanism: {mechanism}")
        self.history = history
        self.mechanism = mechanism
        self.enc1 = _unet_block(history + 1, channels)
        self.enc2 = _unet_block(channels, 2 * channels)
        self.bottleneck = _unet_block(2 * channels, 2 * channels)
        self.up2 = nn.ConvTranspose1d(2 * channels, 2 * channels, 2, stride=2)
        self.dec2 = _unet_block(4 * channels, 2 * channels)
        self.up1 = nn.ConvTranspose1d(2 * channels, channels, 2, stride=2)
        self.dec1 = _unet_block(2 * channels, channels)
        self.head = nn.Conv1d(channels, 1, kernel_size=1)

    def forward(self, history: torch.Tensor, grid: torch.Tensor) -> torch.Tensor:
        if history.ndim != 3 or history.shape[-1] != self.history:
            raise ValueError("U-Net history must have shape [batch, x, history]")
        if history.shape[1] % 4:
            raise ValueError("U-Net spatial resolution must be divisible by four")
        coordinate = grid.view(1, -1, 1).expand(history.shape[0], -1, -1)
        features = torch.cat((history, coordinate), dim=-1).permute(0, 2, 1)
        encoded1 = self.enc1(features)
        encoded2 = self.enc2(functional.avg_pool1d(encoded1, 2))
        bottleneck = self.bottleneck(functional.avg_pool1d(encoded2, 2))
        decoded2 = self.dec2(torch.cat((self.up2(bottleneck), encoded2), dim=1))
        decoded1 = self.dec1(torch.cat((self.up1(decoded2), encoded1), dim=1))
        raw = self.head(decoded1).squeeze(1)
        previous = history[..., -1]
        if self.mechanism == "free_res":
            return previous + raw
        if self.mechanism == "hard_abs":
            return raw + previous.mean(dim=-1, keepdim=True) - raw.mean(dim=-1, keepdim=True)
        if self.mechanism == "hard":
            return previous + raw - raw.mean(dim=-1, keepdim=True)
        return raw


def project_mass(previous: torch.Tensor, prediction: torch.Tensor) -> torch.Tensor:
    return prediction + previous.mean(dim=-1, keepdim=True) - prediction.mean(dim=-1, keepdim=True)


def extract_windows(
    trajectories: torch.Tensor,
    row_indices: torch.Tensor,
    target_indices: torch.Tensor,
    history: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    rows = trajectories[row_indices]
    offsets = torch.arange(history, dtype=torch.long)
    times = target_indices[row_indices, None] - history + offsets[None, :]
    gather_index = times[..., None].expand(-1, -1, rows.shape[-1])
    inputs = rows.gather(1, gather_index).permute(0, 2, 1).contiguous()
    targets = rows[torch.arange(rows.shape[0]), target_indices[row_indices]]
    return inputs, targets


def build_model(model_cfg: Mapping[str, Any], mechanism: str) -> nn.Module:
    architecture = str(model_cfg.get("architecture", "fno1d"))
    if architecture == "unet1d":
        return UNet1d(
            history=int(model_cfg["history"]),
            channels=int(model_cfg["channels"]),
            mechanism=mechanism,
        )
    if architecture != "fno1d":
        raise ValueError(f"unsupported PDEBench architecture: {architecture}")
    return FNO1d(
        history=int(model_cfg["history"]),
        modes=int(model_cfg["modes"]),
        width=int(model_cfg["width"]),
        padding=int(model_cfg["padding"]),
        projection_width=int(model_cfg["projection_width"]),
        mechanism=mechanism,
    )


def model_state_sha256(model: nn.Module) -> str:
    """Hash initialized tensor contents without serialization metadata."""
    digest = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        values = tensor.detach().cpu().contiguous()
        digest.update(name.encode("utf-8"))
        digest.update(str(values.dtype).encode("ascii"))
        digest.update(np.asarray(values.shape, dtype=np.int64).tobytes())
        digest.update(values.view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()


def _save_checkpoint(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(dict(payload), temporary)
    os.replace(temporary, path)


def train_model(
    *,
    model: FNO1d,
    mechanism: str,
    trajectories: torch.Tensor,
    grid: torch.Tensor,
    training_cfg: Mapping[str, Any],
    soft_weight: float,
    seed: int,
    run_id: str,
    checkpoint_path: Path,
    device: torch.device,
) -> dict[str, Any]:
    epochs = int(training_cfg["epochs"])
    batch_size = int(training_cfg["batch_size"])
    history = int(model.history) if hasattr(model, "history") else int(model.lift.in_features - 1)
    num_windows = trajectories.shape[1] - history
    if num_windows <= 0:
        raise RuntimeError("training trajectory is shorter than the frozen history")
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=float(training_cfg["learning_rate"]),
        weight_decay=float(training_cfg["weight_decay"]),
    )
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer,
        step_size=int(training_cfg["scheduler_step"]),
        gamma=float(training_cfg["scheduler_gamma"]),
    )
    start_epoch = 0
    accumulated_runtime = 0.0
    recovered = False
    if checkpoint_path.is_file():
        checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
        if checkpoint.get("run_id") != run_id:
            raise RuntimeError(f"checkpoint run ID mismatch: {checkpoint_path}")
        model.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        start_epoch = int(checkpoint["completed_epochs"])
        accumulated_runtime = float(checkpoint.get("runtime_seconds", 0.0))
        recovered = start_epoch > 0
    if start_epoch > epochs:
        raise RuntimeError("checkpoint exceeds the frozen training epoch count")

    offset_rng = np.random.default_rng(stable_seed(seed, "pdebench-window-offsets"))
    base_offsets = torch.from_numpy(
        offset_rng.integers(0, num_windows, size=trajectories.shape[0], dtype=np.int64)
    )
    grid_device = grid.to(device=device, dtype=torch.float32)
    checkpoint_interval = int(training_cfg["checkpoint_every_epochs"])
    started = time.perf_counter()
    model.train()
    for epoch in range(start_epoch, epochs):
        target_indices = history + (base_offsets + epoch) % num_windows
        order_generator = torch.Generator().manual_seed(
            stable_seed(seed, f"pdebench-minibatch-order:{epoch}")
        )
        order = torch.randperm(trajectories.shape[0], generator=order_generator)
        for start in range(0, trajectories.shape[0], batch_size):
            row_indices = order[start : start + batch_size]
            inputs, targets = extract_windows(trajectories, row_indices, target_indices, history)
            inputs = inputs.to(device=device, dtype=torch.float32)
            targets = targets.to(device=device, dtype=torch.float32)
            prediction = model(inputs, grid_device)
            loss = (prediction - targets).square().mean()
            if mechanism == "soft30":
                drift = prediction.mean(dim=-1) - inputs[..., -1].mean(dim=-1)
                loss = loss + soft_weight * drift.square().mean()
            if not bool(torch.isfinite(loss)):
                raise FloatingPointError("non-finite PDEBench training loss")
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
        scheduler.step()
        completed_epochs = epoch + 1
        if completed_epochs % checkpoint_interval == 0 or completed_epochs == epochs:
            elapsed = accumulated_runtime + time.perf_counter() - started
            _save_checkpoint(
                checkpoint_path,
                {
                    "schema_version": EXTERNAL_SCHEMA_VERSION,
                    "run_id": run_id,
                    "completed_epochs": completed_epochs,
                    "runtime_seconds": elapsed,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "scheduler_state_dict": scheduler.state_dict(),
                },
            )
    runtime = accumulated_runtime + time.perf_counter() - started
    return {
        "runtime_seconds": runtime,
        "resumed_from_checkpoint": recovered,
        "completed_epochs": epochs,
    }


def _empty_metric_accumulator() -> dict[str, float | int]:
    return {
        "total_squared_error": 0.0,
        "conserving_squared_error": 0.0,
        "elements": 0,
        "prediction_abs_mass_drift": 0.0,
        "prediction_max_abs_mass_drift": 0.0,
        "target_abs_mass_drift": 0.0,
        "target_max_abs_mass_drift": 0.0,
        "samples": 0,
    }


def _update_metric_accumulator(
    accumulator: dict[str, float | int],
    prediction: torch.Tensor,
    target: torch.Tensor,
    reference_mass: torch.Tensor,
) -> None:
    error = prediction - target
    conserving_error = error - error.mean(dim=-1, keepdim=True)
    prediction_drift = (prediction.mean(dim=-1) - reference_mass).abs()
    target_drift = (target.mean(dim=-1) - reference_mass).abs()
    accumulator["total_squared_error"] = float(accumulator["total_squared_error"]) + float(
        error.square().sum().detach().cpu()
    )
    accumulator["conserving_squared_error"] = float(accumulator["conserving_squared_error"]) + float(
        conserving_error.square().sum().detach().cpu()
    )
    accumulator["elements"] = int(accumulator["elements"]) + error.numel()
    accumulator["prediction_abs_mass_drift"] = float(accumulator["prediction_abs_mass_drift"]) + float(
        prediction_drift.sum().detach().cpu()
    )
    accumulator["prediction_max_abs_mass_drift"] = max(
        float(accumulator["prediction_max_abs_mass_drift"]),
        float(prediction_drift.max().detach().cpu()),
    )
    accumulator["target_abs_mass_drift"] = float(accumulator["target_abs_mass_drift"]) + float(
        target_drift.sum().detach().cpu()
    )
    accumulator["target_max_abs_mass_drift"] = max(
        float(accumulator["target_max_abs_mass_drift"]),
        float(target_drift.max().detach().cpu()),
    )
    accumulator["samples"] = int(accumulator["samples"]) + prediction.shape[0]


def _finalize_metric_accumulator(
    accumulator: Mapping[str, float | int],
) -> dict[str, float]:
    elements = int(accumulator["elements"])
    samples = int(accumulator["samples"])
    result = {
        "total_rmse": math.sqrt(float(accumulator["total_squared_error"]) / elements),
        "conserving_rmse": math.sqrt(float(accumulator["conserving_squared_error"]) / elements),
        "mean_abs_invariant_drift": float(accumulator["prediction_abs_mass_drift"]) / samples,
        "max_abs_invariant_drift": float(accumulator["prediction_max_abs_mass_drift"]),
        "mean_abs_target_invariant_drift": float(accumulator["target_abs_mass_drift"]) / samples,
        "max_abs_target_invariant_drift": float(accumulator["target_max_abs_mass_drift"]),
    }
    if not all(math.isfinite(value) for value in result.values()):
        raise FloatingPointError("non-finite PDEBench evaluation metric")
    return result


def evaluate_rollout(
    *,
    model: FNO1d,
    trajectories: torch.Tensor,
    grid: torch.Tensor,
    history: int,
    horizons: Sequence[int],
    batch_size: int,
    device: torch.device,
    projected: bool,
) -> dict[str, dict[str, float]]:
    requested = {int(value) for value in horizons}
    maximum = max(requested)
    if history + maximum > trajectories.shape[1]:
        raise RuntimeError("requested rollout horizon exceeds the available trajectory")
    accumulators = {horizon: _empty_metric_accumulator() for horizon in requested}
    grid_device = grid.to(device=device, dtype=torch.float32)
    model.eval()
    with torch.no_grad():
        for start in range(0, trajectories.shape[0], batch_size):
            batch = trajectories[start : start + batch_size]
            state = batch[:, :history].permute(0, 2, 1).to(device=device, dtype=torch.float32)
            reference_mass = batch[:, 0].mean(dim=-1).to(device=device, dtype=torch.float32)
            for horizon in range(1, maximum + 1):
                previous = state[..., -1]
                prediction = model(state, grid_device)
                if projected:
                    prediction = project_mass(previous, prediction)
                target = batch[:, history - 1 + horizon].to(device=device, dtype=torch.float32)
                if horizon in requested:
                    _update_metric_accumulator(accumulators[horizon], prediction, target, reference_mass)
                state = torch.cat((state[..., 1:], prediction.unsqueeze(-1)), dim=-1)
    return {
        str(horizon): _finalize_metric_accumulator(accumulators[horizon]) for horizon in sorted(requested)
    }


def projection_identity_max_error(
    *,
    model: FNO1d,
    trajectories: torch.Tensor,
    grid: torch.Tensor,
    history: int,
    batch_size: int,
    device: torch.device,
) -> float:
    maximum = 0.0
    grid_device = grid.to(device=device, dtype=torch.float32)
    model.eval()
    with torch.no_grad():
        for start in range(0, trajectories.shape[0], batch_size):
            batch = trajectories[start : start + batch_size]
            state = batch[:, :history].permute(0, 2, 1).to(device=device, dtype=torch.float32)
            target = batch[:, history].to(device=device, dtype=torch.float32)
            prediction = model(state, grid_device)
            projected = project_mass(state[..., -1], prediction)
            free_error = prediction - target
            projected_error = projected - target
            free_conserving = free_error - free_error.mean(dim=-1, keepdim=True)
            projected_conserving = projected_error - projected_error.mean(dim=-1, keepdim=True)
            maximum = max(
                maximum,
                float((free_conserving - projected_conserving).abs().max().cpu()),
            )
    return maximum


def evaluate_cases(
    *,
    model: FNO1d,
    native_trajectories: torch.Tensor,
    native_grid: torch.Tensor,
    evaluation_cfg: Mapping[str, Any],
    history: int,
    device: torch.device,
    projected: bool,
) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, float]]:
    strides = [int(value) for value in evaluation_cfg["spatial_strides"]]
    names = [str(value) for value in evaluation_cfg["case_names"]]
    if len(strides) != len(names):
        raise RuntimeError("evaluation spatial strides and case names must have equal length")
    horizons = [int(value) for value in evaluation_cfg["horizons"]]
    batch_size = int(evaluation_cfg["batch_size"])
    restriction_method = str(evaluation_cfg.get("restriction_method", "point"))
    cases: dict[str, dict[str, dict[str, float]]] = {}
    identities: dict[str, float] = {}
    for stride, name in zip(strides, names, strict=True):
        trajectories = restrict_spatial_torch(native_trajectories, stride, restriction_method).contiguous()
        grid = restrict_grid(native_grid, stride, restriction_method)
        cases[name] = evaluate_rollout(
            model=model,
            trajectories=trajectories,
            grid=grid,
            history=history,
            horizons=horizons,
            batch_size=batch_size,
            device=device,
            projected=projected,
        )
        if projected:
            identities[name] = projection_identity_max_error(
                model=model,
                trajectories=trajectories,
                grid=grid,
                history=history,
                batch_size=batch_size,
                device=device,
            )
    return cases, identities


def _existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    completed: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "run_id" in record:
            completed.add(str(record["run_id"]))
    return completed


def _validate_protocol(
    root: Path, resolved: Mapping[str, Any], *, required: bool
) -> tuple[Path | None, str | None]:
    raw_path = resolved.get("protocol_path")
    expected = resolved.get("protocol_sha256")
    if not raw_path or not expected:
        if required:
            raise RuntimeError("external confirmation/preflight requires a frozen protocol hash")
        return None, None
    path = resolve_path(root, str(raw_path))
    if not path.is_file():
        raise RuntimeError(f"frozen protocol does not exist: {path}")
    actual = sha256_file(path)
    if actual != str(expected):
        raise RuntimeError(f"protocol SHA-256 mismatch: expected {expected}, got {actual}")
    return path, actual


def _validate_schema_amendment(
    root: Path, resolved: Mapping[str, Any], *, required: bool
) -> tuple[Path | None, str | None]:
    raw_path = resolved.get("schema_amendment_path")
    expected = resolved.get("schema_amendment_sha256")
    if not raw_path or not expected:
        if required:
            raise RuntimeError("external confirmation/preflight requires the schema amendment hash")
        return None, None
    path = resolve_path(root, str(raw_path))
    if not path.is_file():
        raise RuntimeError(f"schema amendment does not exist: {path}")
    actual = sha256_file(path)
    if actual != str(expected):
        raise RuntimeError(f"schema-amendment SHA-256 mismatch: expected {expected}, got {actual}")
    return path, actual


def _smoke_dataset_identity(dataset_path: Path, dataset_cfg: Mapping[str, Any]) -> dict[str, Any]:
    return inspect_public_dataset(dataset_path, dataset_cfg)


def run(cfg: DictConfig) -> None:
    root = Path(__file__).resolve().parents[1]
    resolved = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(resolved, dict):
        raise TypeError("resolved Hydra config must be a mapping")
    stage = str(resolved["stage"])
    formal_stage = stage in {
        "external_confirmation",
        "external_preflight",
        "factorial_confirmation",
        "factorial_preflight",
    }
    if stage not in {
        "external_confirmation",
        "external_preflight",
        "factorial_confirmation",
        "factorial_preflight",
        "smoke",
    }:
        raise RuntimeError(f"unsupported PDEBench stage: {stage}")
    if stage == "factorial_confirmation" and resolved.get("formal_seed_universe"):
        universe = [int(value) for value in resolved["formal_seed_universe"]]
        if universe != list(range(7000, 7030)):
            raise RuntimeError("U-Net formal seed universe must remain 7000--7029")
        shards = resolved.get("formal_seed_shards")
        worker_id = str(resolved.get("worker_id"))
        if not isinstance(shards, Mapping) or worker_id not in shards:
            raise RuntimeError("U-Net formal worker must name a registered seed shard")
        seeds = [int(value) for value in resolved["seeds"]]
        if seeds != [int(value) for value in shards[worker_id]]:
            raise RuntimeError("U-Net worker seeds differ from the frozen shard")

    dataset_cfg = resolved["dataset"]
    split_cfg = resolved["split"]
    model_cfg = resolved["model"]
    training_cfg = resolved["training"]
    evaluation_cfg = resolved["evaluation"]
    if not all(
        isinstance(value, Mapping)
        for value in (dataset_cfg, split_cfg, model_cfg, training_cfg, evaluation_cfg)
    ):
        raise TypeError("nested PDEBench configs must resolve to mappings")
    dataset_path = resolve_path(root, str(dataset_cfg["path"]))
    protocol_path, protocol_sha256 = _validate_protocol(root, resolved, required=formal_stage)
    schema_amendment_path, schema_amendment_sha256 = _validate_schema_amendment(
        root, resolved, required=formal_stage
    )

    data_lock_path: Path | None = None
    data_lock_sha256: str | None = None
    if formal_stage:
        data_lock_path, data_lock_sha256, data_lock = validate_data_lock(
            root=root, resolved=resolved, dataset_path=dataset_path
        )
        dataset_identity = dict(data_lock["inspection"])
        data_lock_protocol_sha256 = str(resolved.get("data_lock_protocol_sha256") or protocol_sha256)
        if data_lock.get("protocol_sha256") != data_lock_protocol_sha256:
            raise RuntimeError("data lock is not bound to the active frozen protocol")
        if data_lock.get("schema_amendment_sha256") != schema_amendment_sha256:
            raise RuntimeError("data lock is not bound to the coordinate-schema amendment")
        decision_path = resolve_path(root, str(resolved["decision_path"]))
        if not decision_path.is_file():
            raise RuntimeError(f"external benchmark decision does not exist: {decision_path}")
        schema_decision_path = resolve_path(root, str(resolved["schema_decision_path"]))
        if not schema_decision_path.is_file():
            raise RuntimeError(f"coordinate-schema decision does not exist: {schema_decision_path}")
    else:
        dataset_identity = _smoke_dataset_identity(dataset_path, dataset_cfg)
        decision_path = None
        schema_decision_path = None

    device = torch.device(str(resolved["device"]))
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    if int(training_cfg["spatial_stride"]) != 4:
        raise RuntimeError("formal FNO training resolution is frozen at spatial stride 4")
    if int(training_cfg["temporal_stride"]) != 5:
        raise RuntimeError("formal FNO temporal stride is frozen at 5")
    restriction_methods = {
        str(dataset_cfg.get("restriction_method", "point")),
        str(training_cfg.get("restriction_method", "point")),
        str(evaluation_cfg.get("restriction_method", "point")),
    }
    if len(restriction_methods) != 1:
        raise RuntimeError("dataset, training, and evaluation restriction methods must match")
    restriction_method = restriction_methods.pop()

    output = resolve_path(root, str(resolved["output"]))
    checkpoint_dir = resolve_path(root, str(resolved["checkpoint_dir"]))
    incident_path = resolve_path(root, str(resolved["incident_path"]))
    source_files = [
        Path(__file__),
        root / "scripts/constraint_iclr_common.py",
        root / "scripts/prepare_constraint_iclr_pdebench.py",
        root / "scripts/analyze_constraint_iclr_pdebench.py",
        root / "scripts/launch_constraint_iclr_pdebench.py",
        root / "configs/constraint_iclr/pdebench_advection_fno.yaml",
        root / "configs/constraint_iclr/pdebench_advection_fno_v2.yaml",
        root / "configs/constraint_iclr/pdebench_advection_fno_confirmation.yaml",
        root / "configs/constraint_iclr/pdebench_advection_fno_v2_confirmation.yaml",
        incident_path,
    ]
    if stage.startswith("factorial_"):
        source_files.extend(
            [
                root / "configs/constraint_iclr/pdebench_advection_fno_factorial_20260901.yaml",
                root / "scripts/analyze_constraint_iclr_pdebench_factorial.py",
                root / "scripts/launch_constraint_iclr_pdebench_factorial.py",
            ]
        )
    for raw_path in resolved.get("source_artifact_paths", []):
        source_files.append(resolve_path(root, str(raw_path)))
    source_metadata_raw = resolved.get("source_metadata_path")
    if source_metadata_raw:
        source_files.append(resolve_path(root, str(source_metadata_raw)))
    if protocol_path is not None:
        source_files.append(protocol_path)
    if schema_amendment_path is not None:
        source_files.append(schema_amendment_path)
    if decision_path is not None:
        source_files.append(decision_path)
    if schema_decision_path is not None:
        source_files.append(schema_decision_path)
    v1_failure_raw = resolved.get("v1_failure_path")
    if v1_failure_raw:
        source_files.append(resolve_path(root, str(v1_failure_raw)))
    if data_lock_path is not None:
        source_files.append(data_lock_path)
    shared_provenance = provenance(root=root, resolved_config=resolved, source_files=source_files)
    shared_provenance["h5py"] = h5py.__version__

    temporal_stride = int(training_cfg["temporal_stride"])
    confirmation_indices = np.arange(
        int(split_cfg["confirmation_start"]),
        int(split_cfg["confirmation_start"]) + int(split_cfg["confirmation_count"]),
        dtype=np.int64,
    )
    evaluation_trajectories = load_trajectories(
        dataset_path,
        confirmation_indices,
        temporal_stride=temporal_stride,
        spatial_stride=1,
    )
    native_grid = load_x_coordinate(dataset_path, 1)
    history = int(model_cfg["history"])
    maximum_horizon = max(int(value) for value in evaluation_cfg["horizons"])
    if history + maximum_horizon > evaluation_trajectories.shape[1]:
        raise RuntimeError("frozen history and rollout horizons exceed the dataset")

    completed = _existing_ids(output)
    mechanisms = [str(value) for value in resolved["mechanisms"]]
    expected_mechanisms = (
        ["free", "free_res", "hard_abs", "hard"]
        if stage.startswith("factorial_")
        else ["free", "free_res", "hard", "soft30"]
    )
    if mechanisms != expected_mechanisms and formal_stage:
        raise RuntimeError(f"formal mechanisms must remain {expected_mechanisms} for stage {stage}")
    dataset_sha256 = str(dataset_identity["sha256"])
    training_spatial_stride = int(training_cfg["spatial_stride"])
    training_grid = restrict_grid(native_grid, training_spatial_stride, restriction_method)

    for seed in [int(value) for value in resolved["seeds"]]:
        training_indices = select_training_indices(seed, split_cfg)
        training_index_sha256 = hashlib.sha256(training_indices.tobytes()).hexdigest()
        identities: dict[str, tuple[dict[str, Any], str]] = {}
        for mechanism in mechanisms:
            identity = {
                "schema_version": EXTERNAL_SCHEMA_VERSION,
                "stage": stage,
                "benchmark_id": str(resolved["benchmark_id"]),
                "dataset_sha256": dataset_sha256,
                "data_lock_sha256": data_lock_sha256,
                "protocol_sha256": protocol_sha256,
                "schema_amendment_sha256": schema_amendment_sha256,
                "seed": seed,
                "mechanism": mechanism,
                "model": dict(model_cfg),
                "training": dict(training_cfg),
                "training_index_sha256": training_index_sha256,
            }
            identities[mechanism] = (identity, canonical_run_id(identity))
        free_identity = identities.get("free")
        projection_run_id: str | None = None
        if free_identity is not None:
            projection_run_id = canonical_run_id({**free_identity[0], "mechanism": "projection"})
        missing = [
            mechanism
            for mechanism, (_, run_id) in identities.items()
            if run_id not in completed or (mechanism == "free" and projection_run_id not in completed)
        ]
        if not missing:
            continue
        training_trajectories = load_trajectories(
            dataset_path,
            training_indices,
            temporal_stride=temporal_stride,
            spatial_stride=training_spatial_stride,
            restriction_method=restriction_method,
        )

        for mechanism in mechanisms:
            identity, run_id = identities[mechanism]
            needs_projection = mechanism == "free" and projection_run_id not in completed
            if run_id in completed and not needs_projection:
                continue
            seed_everything(stable_seed(seed, "pdebench-fno-initialization"))
            model = build_model(model_cfg, mechanism).to(device)
            initialization_sha256 = model_state_sha256(model)
            parameter_count = count_trainable_parameters(model)
            if device.type == "cuda":
                torch.cuda.reset_peak_memory_stats(device)
            checkpoint_path = checkpoint_dir / f"{run_id}.pt"
            training_report = train_model(
                model=model,
                mechanism=mechanism,
                trajectories=training_trajectories,
                grid=training_grid,
                training_cfg=training_cfg,
                soft_weight=float(resolved["soft_weight"]),
                seed=seed,
                run_id=run_id,
                checkpoint_path=checkpoint_path,
                device=device,
            )
            evaluation_started = time.perf_counter()
            cases, _ = evaluate_cases(
                model=model,
                native_trajectories=evaluation_trajectories,
                native_grid=native_grid,
                evaluation_cfg=evaluation_cfg,
                history=history,
                device=device,
                projected=False,
            )
            evaluation_runtime = time.perf_counter() - evaluation_started
            peak_memory = int(torch.cuda.max_memory_allocated(device)) if device.type == "cuda" else None
            examples_seen = int(split_cfg["train_trajectories_per_seed"]) * int(training_cfg["epochs"])
            compute = {
                "trainable_parameters": parameter_count,
                "examples_seen": examples_seen,
                "proxy": parameter_count * examples_seen,
                "training_runtime_seconds": float(training_report["runtime_seconds"]),
                "evaluation_runtime_seconds": evaluation_runtime,
                "peak_gpu_memory_bytes": peak_memory,
                "optimization_runs": 1,
            }
            record = {
                **identity,
                "run_id": run_id,
                "config_id": (
                    f"unet1d_c{model_cfg['channels']}_e{training_cfg['epochs']}_"
                    f"lr{float(training_cfg['learning_rate']):g}"
                    if str(model_cfg.get("architecture", "fno1d")) == "unet1d"
                    else f"fno_w{model_cfg['width']}_m{model_cfg['modes']}_"
                    f"e{training_cfg['epochs']}_lr{float(training_cfg['learning_rate']):g}"
                ),
                "derived_from": None,
                "training_subset": {
                    "count": int(training_indices.size),
                    "index_sha256": training_index_sha256,
                },
                "initialization_sha256": initialization_sha256,
                "compute": compute,
                "cases": cases,
                "checkpoint": {
                    "path": path_label(root, checkpoint_path),
                    **training_report,
                },
                "provenance": shared_provenance,
            }
            if run_id not in completed:
                append_jsonl(output, record)
                completed.add(run_id)
                print(f"completed {run_id} {mechanism} seed={seed}", flush=True)

            if mechanism == "free" and projection_run_id not in completed:
                projection_started = time.perf_counter()
                projected_cases, projection_identity = evaluate_cases(
                    model=model,
                    native_trajectories=evaluation_trajectories,
                    native_grid=native_grid,
                    evaluation_cfg=evaluation_cfg,
                    history=history,
                    device=device,
                    projected=True,
                )
                projection_runtime = time.perf_counter() - projection_started
                projection_identity_record = {
                    **identity,
                    "mechanism": "projection",
                    "run_id": projection_run_id,
                    "config_id": record["config_id"],
                    "derived_from": run_id,
                    "training_subset": record["training_subset"],
                    "initialization_sha256": record["initialization_sha256"],
                    "compute": {
                        "trainable_parameters": parameter_count,
                        "examples_seen": 0,
                        "proxy": 0,
                        "training_runtime_seconds": 0.0,
                        "parent_training_runtime_seconds": float(training_report["runtime_seconds"]),
                        "evaluation_runtime_seconds": projection_runtime,
                        "peak_gpu_memory_bytes": peak_memory,
                        "optimization_runs": 0,
                    },
                    "cases": projected_cases,
                    "projection_identity_max_abs_by_case": projection_identity,
                    "checkpoint": record["checkpoint"],
                    "provenance": shared_provenance,
                }
                append_jsonl(output, projection_identity_record)
                completed.add(projection_run_id)
                print(f"completed {projection_run_id} projection seed={seed}", flush=True)


@hydra.main(
    version_base=None,
    config_path="../configs/constraint_iclr",
    config_name="pdebench_advection_fno",
)
def main(cfg: DictConfig) -> None:
    run(cfg)


if __name__ == "__main__":
    main()
