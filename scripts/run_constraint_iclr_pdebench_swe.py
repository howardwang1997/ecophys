"""Run the frozen PDEBench 2D shallow-water FNO factorial."""

from __future__ import annotations

import hashlib
import json
import math
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
from prepare_constraint_iclr_pdebench_swe import LOCK_SCHEMA_VERSION, restrict_swe_numpy
from run_constraint_iclr_pdebench_fno import model_state_sha256, resolve_path
from torch import nn

SWE_SCHEMA_VERSION = "constraint-iclr-pdebench-swe-v1"
TRAINED_MECHANISMS = ("free", "free_res", "hard_abs", "hard")


def validate_swe_seed_assignment(resolved: Mapping[str, Any]) -> list[int]:
    """Validate either all formal seeds or one frozen distributed shard."""
    seeds = [int(value) for value in resolved["seeds"]]
    if str(resolved["stage"]) != "swe_factorial_confirmation":
        return seeds
    formal_universe = list(range(6000, 6030))
    raw_shards = resolved.get("formal_seed_shards")
    worker_id = resolved.get("worker_id")
    if raw_shards is None and worker_id is None:
        if seeds != formal_universe:
            raise RuntimeError("formal SWE seeds must remain 6000--6029")
        return seeds
    if [int(value) for value in resolved.get("formal_seed_universe", [])] != formal_universe:
        raise RuntimeError("distributed SWE seed universe must remain 6000--6029")
    if not isinstance(raw_shards, Mapping) or not raw_shards:
        raise RuntimeError("distributed SWE run requires frozen seed shards")
    shards = {
        str(name): [int(value) for value in values]
        for name, values in raw_shards.items()
    }
    flattened = [seed for values in shards.values() for seed in values]
    if sorted(flattened) != formal_universe or len(flattened) != len(set(flattened)):
        raise RuntimeError("distributed SWE shards must partition 6000--6029 exactly")
    if str(worker_id) not in shards:
        raise RuntimeError("distributed SWE worker ID is not registered")
    if seeds != shards[str(worker_id)]:
        raise RuntimeError("SWE worker seeds differ from its frozen shard")
    return seeds


def restrict_swe_torch(values: torch.Tensor, factor: int, method: str) -> torch.Tensor:
    if values.ndim < 2 or factor <= 0:
        raise ValueError("SWE restriction requires two spatial axes and a positive factor")
    nx, ny = values.shape[-2:]
    if nx % factor != 0 or ny % factor != 0:
        raise ValueError("SWE restriction factor must divide both spatial axes")
    if factor == 1:
        return values
    if method == "point":
        return values[..., ::factor, ::factor].contiguous()
    if method == "block_average":
        reshaped = values.reshape(
            *values.shape[:-2], nx // factor, factor, ny // factor, factor
        )
        return reshaped.to(torch.float64).mean(dim=(-3, -1)).to(values.dtype)
    raise ValueError(f"unsupported SWE restriction method: {method}")


def restrict_swe_coordinates(
    x: torch.Tensor, y: torch.Tensor, factor: int, method: str
) -> tuple[torch.Tensor, torch.Tensor]:
    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("SWE coordinates must be one-dimensional")
    if factor <= 0 or x.numel() % factor != 0 or y.numel() % factor != 0:
        raise ValueError("SWE coordinate restriction factor must divide both axes")
    if factor == 1:
        return x, y
    if method == "point":
        return x[::factor].contiguous(), y[::factor].contiguous()
    if method == "block_average":
        return (
            x.reshape(-1, factor).to(torch.float64).mean(dim=-1).to(x.dtype),
            y.reshape(-1, factor).to(torch.float64).mean(dim=-1).to(y.dtype),
        )
    raise ValueError(f"unsupported SWE coordinate restriction method: {method}")


def load_swe_trajectories(
    path: Path,
    indices: Sequence[int] | np.ndarray,
    *,
    temporal_stride: int,
    spatial_factor: int,
    restriction_method: str,
) -> torch.Tensor:
    requested = np.asarray(indices, dtype=np.int64)
    if (
        requested.ndim != 1
        or requested.size == 0
        or np.unique(requested).size != requested.size
    ):
        raise ValueError("SWE trajectory indices must be a non-empty unique vector")
    sort_order = np.argsort(requested)
    sorted_indices = requested[sort_order]
    trajectories: list[np.ndarray] = []
    with h5py.File(path, "r") as handle:
        group_count = len(handle)
        if sorted_indices[0] < 0 or sorted_indices[-1] >= group_count:
            raise IndexError("SWE trajectory index is outside the dataset")
        for index in sorted_indices:
            values = np.asarray(
                handle[f"{int(index):04d}/data"][::temporal_stride, ..., 0],
                dtype=np.float32,
            )
            trajectories.append(
                restrict_swe_numpy(values, spatial_factor, restriction_method)
            )
    sorted_values = np.stack(trajectories, axis=0)
    inverse = np.empty_like(sort_order)
    inverse[sort_order] = np.arange(sort_order.size)
    return torch.from_numpy(np.ascontiguousarray(sorted_values[inverse]))


def select_swe_training_indices(seed: int, split_cfg: Mapping[str, Any]) -> np.ndarray:
    start = int(split_cfg["train_pool_start"])
    stop = int(split_cfg["train_pool_stop"])
    count = int(split_cfg["train_trajectories_per_seed"])
    if count > stop - start:
        raise ValueError("SWE training subset is larger than the frozen pool")
    rng = np.random.default_rng(stable_seed(seed, "pdebench-swe-train-trajectories"))
    return rng.choice(np.arange(start, stop, dtype=np.int64), size=count, replace=False)


def project_swe_mass(previous: torch.Tensor, prediction: torch.Tensor) -> torch.Tensor:
    return (
        prediction
        + previous.mean(dim=(-2, -1), keepdim=True)
        - prediction.mean(dim=(-2, -1), keepdim=True)
    )


class SpectralConv2d(nn.Module):
    def __init__(
        self, in_channels: int, out_channels: int, modes_x: int, modes_y: int
    ) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.modes_x = modes_x
        self.modes_y = modes_y
        scale = 1.0 / (in_channels * out_channels)
        shape = (in_channels, out_channels, modes_x, modes_y)
        self.weights_positive = nn.Parameter(scale * torch.rand(*shape, dtype=torch.cfloat))
        self.weights_negative = nn.Parameter(scale * torch.rand(*shape, dtype=torch.cfloat))

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        spectrum = torch.fft.rfft2(inputs, dim=(-2, -1))
        if self.modes_x > spectrum.shape[-2] // 2 or self.modes_y > spectrum.shape[-1]:
            raise RuntimeError("requested 2D Fourier modes exceed the current resolution")
        output = torch.zeros(
            inputs.shape[0],
            self.out_channels,
            spectrum.shape[-2],
            spectrum.shape[-1],
            dtype=spectrum.dtype,
            device=inputs.device,
        )
        output[:, :, : self.modes_x, : self.modes_y] = torch.einsum(
            "bixy,ioxy->boxy",
            spectrum[:, :, : self.modes_x, : self.modes_y],
            self.weights_positive,
        )
        output[:, :, -self.modes_x :, : self.modes_y] = torch.einsum(
            "bixy,ioxy->boxy",
            spectrum[:, :, -self.modes_x :, : self.modes_y],
            self.weights_negative,
        )
        return torch.fft.irfft2(output, s=inputs.shape[-2:], dim=(-2, -1))


class FNO2dSWE(nn.Module):
    def __init__(
        self,
        *,
        history: int,
        modes_x: int,
        modes_y: int,
        width: int,
        padding: int,
        projection_width: int,
        coordinate_lower: float,
        coordinate_upper: float,
        mechanism: str,
    ) -> None:
        super().__init__()
        if mechanism not in TRAINED_MECHANISMS:
            raise ValueError(f"unsupported SWE mechanism: {mechanism}")
        if coordinate_upper <= coordinate_lower:
            raise ValueError("SWE coordinate interval must have positive width")
        self.history = history
        self.padding = padding
        self.coordinate_lower = coordinate_lower
        self.coordinate_upper = coordinate_upper
        self.mechanism = mechanism
        self.lift = nn.Linear(history + 2, width)
        self.spectral = nn.ModuleList(
            [SpectralConv2d(width, width, modes_x, modes_y) for _ in range(4)]
        )
        self.pointwise = nn.ModuleList(
            [nn.Conv2d(width, width, kernel_size=1) for _ in range(4)]
        )
        self.project1 = nn.Linear(width, projection_width)
        self.project2 = nn.Linear(projection_width, 1)

    def forward(
        self, history: torch.Tensor, grid_x: torch.Tensor, grid_y: torch.Tensor
    ) -> torch.Tensor:
        if history.ndim != 4 or history.shape[-1] != self.history:
            raise ValueError("SWE history must have shape [batch,x,y,time]")
        if history.shape[1:3] != (grid_x.numel(), grid_y.numel()):
            raise ValueError("SWE history and grid resolutions differ")
        scale = self.coordinate_upper - self.coordinate_lower
        x_normalized = (grid_x - self.coordinate_lower) / scale
        y_normalized = (grid_y - self.coordinate_lower) / scale
        x_feature = x_normalized.view(1, -1, 1, 1).expand(
            history.shape[0], -1, history.shape[2], -1
        )
        y_feature = y_normalized.view(1, 1, -1, 1).expand(
            history.shape[0], history.shape[1], -1, -1
        )
        features = self.lift(torch.cat((history, x_feature, y_feature), dim=-1))
        features = features.permute(0, 3, 1, 2)
        if self.padding:
            features = functional.pad(features, (0, self.padding, 0, self.padding))
        for index, (spectral, pointwise) in enumerate(
            zip(self.spectral, self.pointwise, strict=True)
        ):
            features = spectral(features) + pointwise(features)
            if index < 3:
                features = functional.gelu(features)
        if self.padding:
            features = features[..., : -self.padding, : -self.padding]
        raw = self.project2(
            functional.gelu(self.project1(features.permute(0, 2, 3, 1)))
        ).squeeze(-1)
        previous = history[..., -1]
        if self.mechanism == "free":
            return raw
        if self.mechanism == "free_res":
            return previous + raw
        if self.mechanism == "hard_abs":
            return project_swe_mass(previous, raw)
        return previous + raw - raw.mean(dim=(-2, -1), keepdim=True)


def build_swe_model(model_cfg: Mapping[str, Any], mechanism: str) -> FNO2dSWE:
    return FNO2dSWE(
        history=int(model_cfg["history"]),
        modes_x=int(model_cfg["modes_x"]),
        modes_y=int(model_cfg["modes_y"]),
        width=int(model_cfg["width"]),
        padding=int(model_cfg["padding"]),
        projection_width=int(model_cfg["projection_width"]),
        coordinate_lower=float(model_cfg["coordinate_lower"]),
        coordinate_upper=float(model_cfg["coordinate_upper"]),
        mechanism=mechanism,
    )


def extract_swe_windows(
    trajectories: torch.Tensor,
    row_indices: torch.Tensor,
    target_indices: torch.Tensor,
    history: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    rows = trajectories[row_indices]
    offsets = torch.arange(history, dtype=torch.long)
    times = target_indices[row_indices, None] - history + offsets[None, :]
    gather_index = times[..., None, None].expand(
        -1, -1, rows.shape[-2], rows.shape[-1]
    )
    inputs = rows.gather(1, gather_index).permute(0, 2, 3, 1).contiguous()
    targets = rows[torch.arange(rows.shape[0]), target_indices[row_indices]]
    return inputs, targets


def _save_checkpoint(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(dict(payload), temporary)
    temporary.replace(path)


def train_swe_model(
    *,
    model: FNO2dSWE,
    trajectories: torch.Tensor,
    grid_x: torch.Tensor,
    grid_y: torch.Tensor,
    training_cfg: Mapping[str, Any],
    seed: int,
    run_id: str,
    checkpoint_path: Path,
    device: torch.device,
) -> dict[str, Any]:
    epochs = int(training_cfg["epochs"])
    batch_size = int(training_cfg["batch_size"])
    num_windows = trajectories.shape[1] - model.history
    if num_windows <= 0:
        raise RuntimeError("SWE training trajectory is shorter than the frozen history")
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
            raise RuntimeError("SWE checkpoint run ID mismatch")
        model.load_state_dict(checkpoint["model_state_dict"], strict=True)
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        start_epoch = int(checkpoint["completed_epochs"])
        accumulated_runtime = float(checkpoint.get("runtime_seconds", 0.0))
        recovered = start_epoch > 0
    if start_epoch > epochs:
        raise RuntimeError("SWE checkpoint exceeds the frozen epoch count")

    offset_rng = np.random.default_rng(stable_seed(seed, "pdebench-swe-window-offsets"))
    base_offsets = torch.from_numpy(
        offset_rng.integers(0, num_windows, size=trajectories.shape[0], dtype=np.int64)
    )
    grid_x_device = grid_x.to(device=device, dtype=torch.float32)
    grid_y_device = grid_y.to(device=device, dtype=torch.float32)
    checkpoint_interval = int(training_cfg["checkpoint_every_epochs"])
    started = time.perf_counter()
    model.train()
    for epoch in range(start_epoch, epochs):
        target_indices = model.history + (base_offsets + epoch) % num_windows
        order_generator = torch.Generator().manual_seed(
            stable_seed(seed, f"pdebench-swe-minibatch-order:{epoch}")
        )
        order = torch.randperm(trajectories.shape[0], generator=order_generator)
        for start in range(0, trajectories.shape[0], batch_size):
            row_indices = order[start : start + batch_size]
            inputs, targets = extract_swe_windows(
                trajectories, row_indices, target_indices, model.history
            )
            inputs = inputs.to(device=device, dtype=torch.float32)
            targets = targets.to(device=device, dtype=torch.float32)
            prediction = model(inputs, grid_x_device, grid_y_device)
            loss = (prediction - targets).square().mean()
            if not bool(torch.isfinite(loss)):
                raise FloatingPointError("non-finite SWE training loss")
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
                    "schema_version": SWE_SCHEMA_VERSION,
                    "run_id": run_id,
                    "completed_epochs": completed_epochs,
                    "runtime_seconds": elapsed,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "scheduler_state_dict": scheduler.state_dict(),
                },
            )
    return {
        "runtime_seconds": accumulated_runtime + time.perf_counter() - started,
        "resumed_from_checkpoint": recovered,
        "completed_epochs": epochs,
    }


def _empty_accumulator() -> dict[str, float | int]:
    return {
        "squared_error": 0.0,
        "conserving_squared_error": 0.0,
        "elements": 0,
        "prediction_abs_drift": 0.0,
        "prediction_max_abs_drift": 0.0,
        "target_abs_drift": 0.0,
        "target_max_abs_drift": 0.0,
        "negative_count": 0,
        "negative_deficit": 0.0,
        "minimum_prediction": math.inf,
        "samples": 0,
    }


def _update_accumulator(
    accumulator: dict[str, float | int],
    prediction: torch.Tensor,
    target: torch.Tensor,
    reference_mean: torch.Tensor,
) -> None:
    error = prediction - target
    conserving_error = error - error.mean(dim=(-2, -1), keepdim=True)
    prediction_mean = prediction.mean(dim=(-2, -1))
    target_mean = target.mean(dim=(-2, -1))
    prediction_drift = (prediction_mean - reference_mean).abs()
    target_drift = (target_mean - reference_mean).abs()
    negative = torch.relu(-prediction)
    accumulator["squared_error"] = float(accumulator["squared_error"]) + float(
        error.square().sum().cpu()
    )
    accumulator["conserving_squared_error"] = float(
        accumulator["conserving_squared_error"]
    ) + float(conserving_error.square().sum().cpu())
    accumulator["elements"] = int(accumulator["elements"]) + error.numel()
    accumulator["prediction_abs_drift"] = float(
        accumulator["prediction_abs_drift"]
    ) + float(prediction_drift.sum().cpu())
    accumulator["prediction_max_abs_drift"] = max(
        float(accumulator["prediction_max_abs_drift"]),
        float(prediction_drift.max().cpu()),
    )
    accumulator["target_abs_drift"] = float(accumulator["target_abs_drift"]) + float(
        target_drift.sum().cpu()
    )
    accumulator["target_max_abs_drift"] = max(
        float(accumulator["target_max_abs_drift"]), float(target_drift.max().cpu())
    )
    accumulator["negative_count"] = int(accumulator["negative_count"]) + int(
        (prediction < 0.0).sum().cpu()
    )
    accumulator["negative_deficit"] = float(accumulator["negative_deficit"]) + float(
        negative.sum().cpu()
    )
    accumulator["minimum_prediction"] = min(
        float(accumulator["minimum_prediction"]), float(prediction.min().cpu())
    )
    accumulator["samples"] = int(accumulator["samples"]) + prediction.shape[0]


def _finalize_accumulator(accumulator: Mapping[str, float | int]) -> dict[str, float]:
    elements = int(accumulator["elements"])
    samples = int(accumulator["samples"])
    result = {
        "total_rmse": math.sqrt(float(accumulator["squared_error"]) / elements),
        "conserving_rmse": math.sqrt(
            float(accumulator["conserving_squared_error"]) / elements
        ),
        "mean_abs_invariant_drift": float(accumulator["prediction_abs_drift"])
        / samples,
        "max_abs_invariant_drift": float(accumulator["prediction_max_abs_drift"]),
        "mean_abs_target_invariant_drift": float(accumulator["target_abs_drift"])
        / samples,
        "max_abs_target_invariant_drift": float(accumulator["target_max_abs_drift"]),
        "negative_depth_fraction": int(accumulator["negative_count"]) / elements,
        "mean_negative_depth_deficit": float(accumulator["negative_deficit"])
        / elements,
        "minimum_predicted_depth": float(accumulator["minimum_prediction"]),
    }
    if not all(math.isfinite(value) for value in result.values()):
        raise FloatingPointError("non-finite SWE evaluation metric")
    return result


def evaluate_swe_rollout(
    *,
    model: FNO2dSWE,
    trajectories: torch.Tensor,
    grid_x: torch.Tensor,
    grid_y: torch.Tensor,
    horizons: Sequence[int],
    batch_size: int,
    device: torch.device,
    projected: bool,
) -> dict[str, dict[str, float]]:
    requested = {int(value) for value in horizons}
    maximum = max(requested)
    if model.history + maximum > trajectories.shape[1]:
        raise RuntimeError("SWE rollout horizon exceeds the available trajectory")
    accumulators = {horizon: _empty_accumulator() for horizon in requested}
    grid_x_device = grid_x.to(device=device, dtype=torch.float32)
    grid_y_device = grid_y.to(device=device, dtype=torch.float32)
    model.eval()
    with torch.no_grad():
        for start in range(0, trajectories.shape[0], batch_size):
            batch = trajectories[start : start + batch_size]
            state = batch[:, : model.history].permute(0, 2, 3, 1).to(
                device=device, dtype=torch.float32
            )
            reference_mean = batch[:, 0].mean(dim=(-2, -1)).to(
                device=device, dtype=torch.float32
            )
            for horizon in range(1, maximum + 1):
                previous = state[..., -1]
                prediction = model(state, grid_x_device, grid_y_device)
                if projected:
                    prediction = project_swe_mass(previous, prediction)
                target = batch[:, model.history - 1 + horizon].to(
                    device=device, dtype=torch.float32
                )
                if horizon in requested:
                    _update_accumulator(
                        accumulators[horizon], prediction, target, reference_mean
                    )
                state = torch.cat((state[..., 1:], prediction.unsqueeze(-1)), dim=-1)
    return {
        str(horizon): _finalize_accumulator(accumulators[horizon])
        for horizon in sorted(requested)
    }


def swe_projection_identity_max_error(
    *,
    model: FNO2dSWE,
    trajectories: torch.Tensor,
    grid_x: torch.Tensor,
    grid_y: torch.Tensor,
    batch_size: int,
    device: torch.device,
) -> float:
    maximum = 0.0
    grid_x_device = grid_x.to(device=device, dtype=torch.float32)
    grid_y_device = grid_y.to(device=device, dtype=torch.float32)
    model.eval()
    with torch.no_grad():
        for start in range(0, trajectories.shape[0], batch_size):
            batch = trajectories[start : start + batch_size]
            state = batch[:, : model.history].permute(0, 2, 3, 1).to(
                device=device, dtype=torch.float32
            )
            target = batch[:, model.history].to(device=device, dtype=torch.float32)
            prediction = model(state, grid_x_device, grid_y_device)
            projected = project_swe_mass(state[..., -1], prediction)
            free_error = prediction - target
            projected_error = projected - target
            free_conserving = free_error - free_error.mean(
                dim=(-2, -1), keepdim=True
            )
            projected_conserving = projected_error - projected_error.mean(
                dim=(-2, -1), keepdim=True
            )
            maximum = max(
                maximum,
                float((free_conserving - projected_conserving).abs().max().cpu()),
            )
    return maximum


def evaluate_swe_cases(
    *,
    model: FNO2dSWE,
    native_trajectories: torch.Tensor,
    native_grid_x: torch.Tensor,
    native_grid_y: torch.Tensor,
    evaluation_cfg: Mapping[str, Any],
    device: torch.device,
    projected: bool,
) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, float]]:
    factors = [int(value) for value in evaluation_cfg["spatial_factors"]]
    names = [str(value) for value in evaluation_cfg["case_names"]]
    if len(factors) != len(names):
        raise RuntimeError("SWE evaluation factors and names must have equal length")
    restriction_method = str(evaluation_cfg["restriction_method"])
    cases: dict[str, dict[str, dict[str, float]]] = {}
    identities: dict[str, float] = {}
    for factor, name in zip(factors, names, strict=True):
        trajectories = restrict_swe_torch(
            native_trajectories, factor, restriction_method
        ).contiguous()
        grid_x, grid_y = restrict_swe_coordinates(
            native_grid_x, native_grid_y, factor, restriction_method
        )
        cases[name] = evaluate_swe_rollout(
            model=model,
            trajectories=trajectories,
            grid_x=grid_x,
            grid_y=grid_y,
            horizons=evaluation_cfg["horizons"],
            batch_size=int(evaluation_cfg["batch_size"]),
            device=device,
            projected=projected,
        )
        if projected:
            identities[name] = swe_projection_identity_max_error(
                model=model,
                trajectories=trajectories,
                grid_x=grid_x,
                grid_y=grid_y,
                batch_size=int(evaluation_cfg["batch_size"]),
                device=device,
            )
    return cases, identities


def validate_swe_data_lock(
    *, root: Path, resolved: Mapping[str, Any], dataset_path: Path
) -> tuple[Path, str, dict[str, Any]]:
    dataset_cfg = resolved["dataset"]
    raw_lock = dataset_cfg.get("lock_path")
    expected_lock_sha256 = dataset_cfg.get("lock_sha256")
    if not raw_lock or not expected_lock_sha256:
        raise RuntimeError("SWE model activation requires a frozen data lock")
    lock_path = resolve_path(root, str(raw_lock))
    actual_lock_sha256 = sha256_file(lock_path)
    if actual_lock_sha256 != str(expected_lock_sha256):
        raise RuntimeError("SWE data-lock SHA-256 mismatch")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if lock.get("schema_version") != LOCK_SCHEMA_VERSION:
        raise RuntimeError("unsupported SWE data-lock schema")
    if lock.get("benchmark_id") != resolved["benchmark_id"]:
        raise RuntimeError("SWE data-lock benchmark mismatch")
    if lock.get("protocol", {}).get("sha256") != resolved["protocol_sha256"]:
        raise RuntimeError("SWE data lock is not bound to the model protocol")
    if lock.get("source_metadata", {}).get("sha256") != resolved[
        "source_metadata_sha256"
    ]:
        raise RuntimeError("SWE data lock is not bound to source metadata")
    if lock.get("transport_decision", {}).get("sha256") != resolved[
        "transport_decision_sha256"
    ]:
        raise RuntimeError("SWE data lock is not bound to the transport decision")
    inspection = lock.get("inspection", {})
    if not inspection.get("hdf5", {}).get("admitted", False):
        raise RuntimeError("SWE data lock does not contain a passing admission")
    if dataset_path.stat().st_size != int(inspection["bytes"]):
        raise RuntimeError("SWE dataset byte count changed after admission")
    if sha256_file(dataset_path) != inspection["sha256"]:
        raise RuntimeError("SWE dataset SHA-256 changed after admission")
    return lock_path, actual_lock_sha256, lock


def _validate_artifact(root: Path, raw_path: str, expected: str, label: str) -> Path:
    path = resolve_path(root, raw_path)
    if not path.is_file() or sha256_file(path) != expected:
        raise RuntimeError(f"{label} is missing or has the wrong SHA-256")
    return path


def _existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    completed: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"invalid SWE JSONL at line {line_number}") from error
        run_id = str(record["run_id"])
        if run_id in completed:
            raise RuntimeError(f"duplicate SWE run ID already present: {run_id}")
        completed.add(run_id)
    return completed


def _artifact_label(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def run_swe(cfg: DictConfig) -> None:
    root = Path(__file__).resolve().parents[1]
    resolved = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(resolved, dict):
        raise TypeError("resolved SWE config must be a mapping")
    stage = str(resolved["stage"])
    if stage not in {
        "swe_factorial_confirmation",
        "swe_factorial_preflight",
        "swe_factorial_smoke",
    }:
        raise RuntimeError("unsupported SWE stage")
    activation_gated = stage != "swe_factorial_smoke"
    mechanisms = [str(value) for value in resolved["mechanisms"]]
    if mechanisms != list(TRAINED_MECHANISMS):
        raise RuntimeError("SWE mechanisms differ from the frozen four-arm factorial")
    if stage == "swe_factorial_confirmation":
        validate_swe_seed_assignment(resolved)
        if len(resolved["evaluation"]["case_names"]) * len(
            resolved["evaluation"]["horizons"]
        ) != 8:
            raise RuntimeError("formal SWE evaluation must retain all eight cells")

    protocol_path = _validate_artifact(
        root, str(resolved["protocol_path"]), str(resolved["protocol_sha256"]), "SWE protocol"
    )
    source_metadata_path = _validate_artifact(
        root,
        str(resolved["source_metadata_path"]),
        str(resolved["source_metadata_sha256"]),
        "SWE source metadata",
    )
    data_decision_path = _validate_artifact(
        root,
        str(resolved["data_decision_path"]),
        str(resolved["data_decision_sha256"]),
        "SWE data decision",
    )
    transport_decision_path = _validate_artifact(
        root,
        str(resolved["transport_decision_path"]),
        str(resolved["transport_decision_sha256"]),
        "SWE transport decision",
    )
    distributed_runtime_path = None
    if resolved.get("formal_seed_shards"):
        distributed_runtime_path = _validate_artifact(
            root,
            str(resolved["distributed_runtime_path"]),
            str(resolved["distributed_runtime_sha256"]),
            "SWE distributed runtime registration",
        )
    model_decision_path = None
    if activation_gated:
        if not resolved.get("model_decision_path") or not resolved.get(
            "model_decision_sha256"
        ):
            raise RuntimeError("formal SWE activation requires a verified model decision")
        model_decision_path = _validate_artifact(
            root,
            str(resolved["model_decision_path"]),
            str(resolved["model_decision_sha256"]),
            "SWE model decision",
        )
    dataset_path = resolve_path(root, str(resolved["dataset"]["path"]))
    data_lock_path, data_lock_sha256, data_lock = validate_swe_data_lock(
        root=root, resolved=resolved, dataset_path=dataset_path
    )
    device = torch.device(str(resolved["device"]))
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    if int(resolved["training"]["spatial_factor"]) != 2:
        raise RuntimeError("SWE training resolution is frozen at factor 2")
    if int(resolved["training"]["temporal_stride"]) != 2:
        raise RuntimeError("SWE temporal stride is frozen at 2")
    if {
        str(resolved["dataset"]["restriction_method"]),
        str(resolved["training"]["restriction_method"]),
        str(resolved["evaluation"]["restriction_method"]),
    } != {"block_average"}:
        raise RuntimeError("SWE uses block-average restriction at every stage")

    active_config_path = resolve_path(root, str(resolved["active_config_path"]))
    source_files = [
        Path(__file__),
        root / "scripts/prepare_constraint_iclr_pdebench_swe.py",
        root / "scripts/constraint_iclr_common.py",
        root / "scripts/run_constraint_iclr_pdebench_fno.py",
        active_config_path,
        protocol_path,
        source_metadata_path,
        data_decision_path,
        transport_decision_path,
        data_lock_path,
    ]
    if distributed_runtime_path is not None:
        source_files.append(distributed_runtime_path)
    if model_decision_path is not None:
        source_files.append(model_decision_path)
    shared_provenance = provenance(
        root=root, resolved_config=resolved, source_files=source_files
    )
    if shared_provenance["git_head"] != str(resolved["expected_git_head"]):
        raise RuntimeError("unexpected Git HEAD for SWE factorial")
    if bool(shared_provenance["git_dirty"]) is not bool(
        resolved["expected_git_dirty"]
    ):
        raise RuntimeError("unexpected dirty flag for SWE factorial")

    confirmation_indices = np.arange(
        int(resolved["split"]["confirmation_start"]),
        int(resolved["split"]["confirmation_start"])
        + int(resolved["split"]["confirmation_count"]),
        dtype=np.int64,
    )
    temporal_stride = int(resolved["training"]["temporal_stride"])
    evaluation_trajectories = load_swe_trajectories(
        dataset_path,
        confirmation_indices,
        temporal_stride=temporal_stride,
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
    output_path = resolve_path(root, str(resolved["output"]))
    checkpoint_dir = resolve_path(root, str(resolved["checkpoint_dir"]))
    completed = _existing_ids(output_path)
    dataset_sha256 = str(data_lock["inspection"]["sha256"])
    training_factor = int(resolved["training"]["spatial_factor"])
    training_grid_x, training_grid_y = restrict_swe_coordinates(
        native_grid_x, native_grid_y, training_factor, "block_average"
    )

    for seed in validate_swe_seed_assignment(resolved):
        training_indices = select_swe_training_indices(seed, resolved["split"])
        training_index_sha256 = hashlib.sha256(training_indices.tobytes()).hexdigest()
        identities: dict[str, tuple[dict[str, Any], str]] = {}
        for mechanism in mechanisms:
            identity = {
                "schema_version": SWE_SCHEMA_VERSION,
                "stage": stage,
                "benchmark_id": resolved["benchmark_id"],
                "dataset_sha256": dataset_sha256,
                "data_lock_sha256": data_lock_sha256,
                "protocol_sha256": resolved["protocol_sha256"],
                "seed": seed,
                "mechanism": mechanism,
                "model": dict(resolved["model"]),
                "training": dict(resolved["training"]),
                "training_index_sha256": training_index_sha256,
            }
            identities[mechanism] = (identity, canonical_run_id(identity))
        free_identity, _ = identities["free"]
        projection_run_id = canonical_run_id(
            {**free_identity, "mechanism": "projection"}
        )
        if all(
            run_id in completed
            and (mechanism != "free" or projection_run_id in completed)
            for mechanism, (_, run_id) in identities.items()
        ):
            continue
        training_trajectories = load_swe_trajectories(
            dataset_path,
            training_indices,
            temporal_stride=temporal_stride,
            spatial_factor=training_factor,
            restriction_method="block_average",
        )
        for mechanism in mechanisms:
            identity, run_id = identities[mechanism]
            needs_projection = mechanism == "free" and projection_run_id not in completed
            if run_id in completed and not needs_projection:
                continue
            seed_everything(stable_seed(seed, "pdebench-swe-fno-initialization"))
            model = build_swe_model(resolved["model"], mechanism).to(device)
            initialization_sha256 = model_state_sha256(model)
            parameter_count = count_trainable_parameters(model)
            if device.type == "cuda":
                torch.cuda.reset_peak_memory_stats(device)
            checkpoint_path = checkpoint_dir / f"{run_id}.pt"
            training_report = train_swe_model(
                model=model,
                trajectories=training_trajectories,
                grid_x=training_grid_x,
                grid_y=training_grid_y,
                training_cfg=resolved["training"],
                seed=seed,
                run_id=run_id,
                checkpoint_path=checkpoint_path,
                device=device,
            )
            evaluation_started = time.perf_counter()
            cases, _ = evaluate_swe_cases(
                model=model,
                native_trajectories=evaluation_trajectories,
                native_grid_x=native_grid_x,
                native_grid_y=native_grid_y,
                evaluation_cfg=resolved["evaluation"],
                device=device,
                projected=False,
            )
            evaluation_runtime = time.perf_counter() - evaluation_started
            peak_memory = (
                int(torch.cuda.max_memory_allocated(device))
                if device.type == "cuda"
                else None
            )
            examples_seen = int(resolved["split"]["train_trajectories_per_seed"]) * int(
                resolved["training"]["epochs"]
            )
            checkpoint_sha256 = sha256_file(checkpoint_path)
            record = {
                **identity,
                "run_id": run_id,
                "derived_from": None,
                "training_subset": {
                    "count": int(training_indices.size),
                    "index_sha256": training_index_sha256,
                },
                "initialization_sha256": initialization_sha256,
                "compute": {
                    "trainable_parameters": parameter_count,
                    "examples_seen": examples_seen,
                    "proxy": parameter_count * examples_seen,
                    "training_runtime_seconds": float(training_report["runtime_seconds"]),
                    "evaluation_runtime_seconds": evaluation_runtime,
                    "peak_gpu_memory_bytes": peak_memory,
                    "optimization_runs": 1,
                },
                "cases": cases,
                "checkpoint": {
                    "path": _artifact_label(root, checkpoint_path),
                    "sha256": checkpoint_sha256,
                    "bytes": checkpoint_path.stat().st_size,
                    **training_report,
                },
                "provenance": shared_provenance,
            }
            if run_id not in completed:
                append_jsonl(output_path, record)
                completed.add(run_id)
                print(f"completed {run_id} {mechanism} seed={seed}", flush=True)
            if mechanism == "free" and projection_run_id not in completed:
                projection_started = time.perf_counter()
                projected_cases, projection_identity = evaluate_swe_cases(
                    model=model,
                    native_trajectories=evaluation_trajectories,
                    native_grid_x=native_grid_x,
                    native_grid_y=native_grid_y,
                    evaluation_cfg=resolved["evaluation"],
                    device=device,
                    projected=True,
                )
                projection_runtime = time.perf_counter() - projection_started
                projection_record = {
                    **identity,
                    "mechanism": "projection",
                    "run_id": projection_run_id,
                    "derived_from": run_id,
                    "training_subset": record["training_subset"],
                    "initialization_sha256": initialization_sha256,
                    "compute": {
                        "trainable_parameters": parameter_count,
                        "examples_seen": 0,
                        "proxy": 0,
                        "training_runtime_seconds": 0.0,
                        "parent_training_runtime_seconds": float(
                            training_report["runtime_seconds"]
                        ),
                        "evaluation_runtime_seconds": projection_runtime,
                        "peak_gpu_memory_bytes": peak_memory,
                        "optimization_runs": 0,
                    },
                    "cases": projected_cases,
                    "projection_identity_max_abs_by_case": projection_identity,
                    "checkpoint": record["checkpoint"],
                    "provenance": shared_provenance,
                }
                append_jsonl(output_path, projection_record)
                completed.add(projection_run_id)
                print(
                    f"completed {projection_run_id} projection seed={seed}", flush=True
                )


@hydra.main(
    version_base=None,
    config_path="../configs/constraint_iclr",
    config_name="pdebench_swe_rdb_factorial_20260902",
)
def main(cfg: DictConfig) -> None:
    run_swe(cfg)


if __name__ == "__main__":
    main()
