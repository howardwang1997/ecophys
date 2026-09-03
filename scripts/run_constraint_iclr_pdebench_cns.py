"""Run the frozen multi-field PDEBench compressible-NS FNO factorial."""

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
from prepare_constraint_iclr_pdebench_cns import LOCK_SCHEMA_VERSION
from run_constraint_iclr_pdebench_fno import (
    SpectralConv1d,
    model_state_sha256,
    resolve_path,
    restrict_grid,
)
from torch import nn

CNS_SCHEMA_VERSION = "constraint-iclr-pdebench-cns-v1"
TRAINED_MECHANISMS = ("free", "free_res", "hard_abs", "hard")


def validate_cns_seed_assignment(resolved: Mapping[str, Any]) -> list[int]:
    """Validate either the full formal seed list or a frozen disjoint worker shard."""
    seeds = [int(value) for value in resolved["seeds"]]
    if str(resolved["stage"]) != "cns_factorial_confirmation":
        return seeds
    formal_universe = list(range(5000, 5030))
    raw_shards = resolved.get("formal_seed_shards")
    worker_id = resolved.get("worker_id")
    if raw_shards is None and worker_id is None:
        if seeds != formal_universe:
            raise RuntimeError("formal CNS seeds must remain 5000--5029")
        return seeds
    if [int(value) for value in resolved.get("formal_seed_universe", [])] != (
        formal_universe
    ):
        raise RuntimeError("distributed CNS seed universe must remain 5000--5029")
    if not isinstance(raw_shards, Mapping) or not raw_shards:
        raise RuntimeError("distributed CNS run requires frozen seed shards")
    shards = {
        str(name): [int(value) for value in values]
        for name, values in raw_shards.items()
    }
    flattened = [seed for values in shards.values() for seed in values]
    if sorted(flattened) != formal_universe or len(flattened) != len(set(flattened)):
        raise RuntimeError("distributed CNS shards must partition 5000--5029 exactly")
    if str(worker_id) not in shards:
        raise RuntimeError("distributed CNS worker ID is not registered")
    if seeds != shards[str(worker_id)]:
        raise RuntimeError("CNS worker seeds differ from its frozen shard")
    return seeds


def restrict_cns_numpy(
    values: np.ndarray, factor: int, method: str
) -> np.ndarray:
    if values.ndim < 2 or factor <= 0 or values.shape[-2] % factor != 0:
        raise ValueError("CNS restriction factor must divide the spatial axis")
    if factor == 1:
        return np.asarray(values, dtype=np.float32)
    if method == "point":
        return np.asarray(values[..., ::factor, :], dtype=np.float32)
    if method == "block_average":
        reshaped = values.reshape(
            *values.shape[:-2], values.shape[-2] // factor, factor, values.shape[-1]
        )
        return np.mean(reshaped, axis=-2, dtype=np.float64).astype(np.float32)
    raise ValueError(f"unsupported CNS restriction method: {method}")


def restrict_cns_torch(
    values: torch.Tensor, factor: int, method: str
) -> torch.Tensor:
    if values.ndim < 2 or factor <= 0 or values.shape[-2] % factor != 0:
        raise ValueError("CNS restriction factor must divide the spatial axis")
    if factor == 1:
        return values
    if method == "point":
        return values[..., ::factor, :].contiguous()
    if method == "block_average":
        reshaped = values.reshape(
            *values.shape[:-2], values.shape[-2] // factor, factor, values.shape[-1]
        )
        return reshaped.to(dtype=torch.float64).mean(dim=-2).to(dtype=values.dtype)
    raise ValueError(f"unsupported CNS restriction method: {method}")


def load_cns_trajectories(
    path: Path,
    indices: Sequence[int] | np.ndarray,
    *,
    fields: Sequence[str],
    temporal_stride: int,
    spatial_stride: int,
    restriction_method: str = "point",
    read_chunk: int = 32,
) -> torch.Tensor:
    requested = np.asarray(indices, dtype=np.int64)
    if (
        requested.ndim != 1
        or requested.size == 0
        or np.unique(requested).size != requested.size
    ):
        raise ValueError("CNS trajectory indices must be a non-empty unique vector")
    sort_order = np.argsort(requested)
    sorted_indices = requested[sort_order]
    chunks: list[np.ndarray] = []
    with h5py.File(path, "r") as handle:
        trajectory_count = int(handle[str(fields[0])].shape[0])
        if sorted_indices[0] < 0 or sorted_indices[-1] >= trajectory_count:
            raise IndexError("CNS trajectory index is outside the dataset")
        for start in range(0, sorted_indices.size, read_chunk):
            chunk_indices = sorted_indices[start : start + read_chunk].tolist()
            channel_values = [
                np.asarray(
                    handle[str(field)][chunk_indices, ::temporal_stride, :],
                    dtype=np.float32,
                )
                for field in fields
            ]
            values = np.stack(channel_values, axis=-1)
            values = restrict_cns_numpy(
                values, spatial_stride, restriction_method
            )
            chunks.append(values)
    sorted_values = np.concatenate(chunks, axis=0)
    inverse = np.empty_like(sort_order)
    inverse[sort_order] = np.arange(sort_order.size)
    return torch.from_numpy(np.ascontiguousarray(sorted_values[inverse]))


def select_cns_training_indices(seed: int, split_cfg: Mapping[str, Any]) -> np.ndarray:
    start = int(split_cfg["train_pool_start"])
    stop = int(split_cfg["train_pool_stop"])
    count = int(split_cfg["train_trajectories_per_seed"])
    if count > stop - start:
        raise ValueError("CNS training subset is larger than the frozen pool")
    rng = np.random.default_rng(stable_seed(seed, "pdebench-cns-train-trajectories"))
    return rng.choice(np.arange(start, stop, dtype=np.int64), size=count, replace=False)


def _replace_channel(
    values: torch.Tensor, channel: int, replacement: torch.Tensor
) -> torch.Tensor:
    return torch.stack(
        [replacement if index == channel else values[..., index] for index in range(values.shape[-1])],
        dim=-1,
    )


def project_density(
    previous: torch.Tensor, prediction: torch.Tensor, invariant_channel: int
) -> torch.Tensor:
    density = prediction[..., invariant_channel]
    corrected = (
        density
        + previous[..., invariant_channel].mean(dim=-1, keepdim=True)
        - density.mean(dim=-1, keepdim=True)
    )
    return _replace_channel(prediction, invariant_channel, corrected)


class FNO1dMulti(nn.Module):
    def __init__(
        self,
        *,
        history: int,
        channels: int,
        invariant_channel: int,
        modes: int,
        width: int,
        padding: int,
        projection_width: int,
        mechanism: str,
    ) -> None:
        super().__init__()
        if mechanism not in TRAINED_MECHANISMS:
            raise ValueError(f"unsupported CNS mechanism: {mechanism}")
        if not 0 <= invariant_channel < channels:
            raise ValueError("CNS invariant channel is outside the output channels")
        self.history = history
        self.channels = channels
        self.invariant_channel = invariant_channel
        self.padding = padding
        self.mechanism = mechanism
        self.lift = nn.Linear(history * channels + 1, width)
        self.spectral = nn.ModuleList(
            [SpectralConv1d(width, width, modes) for _ in range(4)]
        )
        self.pointwise = nn.ModuleList(
            [nn.Conv1d(width, width, 1) for _ in range(4)]
        )
        self.project1 = nn.Linear(width, projection_width)
        self.project2 = nn.Linear(projection_width, channels)

    def forward(self, history: torch.Tensor, grid: torch.Tensor) -> torch.Tensor:
        if history.ndim != 4:
            raise ValueError("CNS history must have shape [batch,x,time,channel]")
        if history.shape[-2:] != (self.history, self.channels):
            raise ValueError("CNS history shape does not match the frozen model")
        coordinate = grid.view(1, -1, 1).expand(history.shape[0], -1, -1)
        flattened = history.reshape(history.shape[0], history.shape[1], -1)
        features = self.lift(torch.cat((flattened, coordinate), dim=-1)).permute(
            0, 2, 1
        )
        if self.padding:
            features = functional.pad(features, (0, self.padding))
        for index, (spectral, pointwise) in enumerate(
            zip(self.spectral, self.pointwise, strict=True)
        ):
            features = spectral(features) + pointwise(features)
            if index < 3:
                features = functional.gelu(features)
        if self.padding:
            features = features[..., : -self.padding]
        raw = self.project2(
            functional.gelu(self.project1(features.permute(0, 2, 1)))
        )
        previous = history[..., -1, :]
        if self.mechanism == "free":
            return raw
        if self.mechanism == "free_res":
            return previous + raw
        if self.mechanism == "hard_abs":
            return project_density(previous, raw, self.invariant_channel)
        residual = _replace_channel(
            raw,
            self.invariant_channel,
            raw[..., self.invariant_channel]
            - raw[..., self.invariant_channel].mean(dim=-1, keepdim=True),
        )
        return previous + residual


def build_cns_model(model_cfg: Mapping[str, Any], mechanism: str) -> FNO1dMulti:
    return FNO1dMulti(
        history=int(model_cfg["history"]),
        channels=int(model_cfg["channels"]),
        invariant_channel=int(model_cfg["invariant_channel"]),
        modes=int(model_cfg["modes"]),
        width=int(model_cfg["width"]),
        padding=int(model_cfg["padding"]),
        projection_width=int(model_cfg["projection_width"]),
        mechanism=mechanism,
    )


def extract_cns_windows(
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
    inputs = rows.gather(1, gather_index).permute(0, 2, 1, 3).contiguous()
    targets = rows[torch.arange(rows.shape[0]), target_indices[row_indices]]
    return inputs, targets


def _save_checkpoint(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(dict(payload), temporary)
    temporary.replace(path)


def train_cns_model(
    *,
    model: FNO1dMulti,
    trajectories: torch.Tensor,
    grid: torch.Tensor,
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
        raise RuntimeError("CNS training trajectory is shorter than the frozen history")
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
        checkpoint = torch.load(
            checkpoint_path, map_location=device, weights_only=False
        )
        if checkpoint.get("run_id") != run_id:
            raise RuntimeError("CNS checkpoint run ID mismatch")
        model.load_state_dict(checkpoint["model_state_dict"], strict=True)
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        start_epoch = int(checkpoint["completed_epochs"])
        accumulated_runtime = float(checkpoint.get("runtime_seconds", 0.0))
        recovered = start_epoch > 0
    if start_epoch > epochs:
        raise RuntimeError("CNS checkpoint exceeds the frozen epoch count")

    offset_rng = np.random.default_rng(stable_seed(seed, "pdebench-cns-window-offsets"))
    base_offsets = torch.from_numpy(
        offset_rng.integers(0, num_windows, size=trajectories.shape[0], dtype=np.int64)
    )
    grid_device = grid.to(device=device, dtype=torch.float32)
    checkpoint_interval = int(training_cfg["checkpoint_every_epochs"])
    started = time.perf_counter()
    model.train()
    for epoch in range(start_epoch, epochs):
        target_indices = model.history + (base_offsets + epoch) % num_windows
        order_generator = torch.Generator().manual_seed(
            stable_seed(seed, f"pdebench-cns-minibatch-order:{epoch}")
        )
        order = torch.randperm(trajectories.shape[0], generator=order_generator)
        for start in range(0, trajectories.shape[0], batch_size):
            row_indices = order[start : start + batch_size]
            inputs, targets = extract_cns_windows(
                trajectories, row_indices, target_indices, model.history
            )
            inputs = inputs.to(device=device, dtype=torch.float32)
            targets = targets.to(device=device, dtype=torch.float32)
            prediction = model(inputs, grid_device)
            loss = (prediction - targets).square().mean()
            if not bool(torch.isfinite(loss)):
                raise FloatingPointError("non-finite CNS training loss")
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
                    "schema_version": CNS_SCHEMA_VERSION,
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


def _empty_accumulator(field_names: Sequence[str]) -> dict[str, Any]:
    return {
        "total_squared_error": 0.0,
        "total_elements": 0,
        "field_squared_error": {name: 0.0 for name in field_names},
        "field_elements": 0,
        "density_conserving_squared_error": 0.0,
        "density_abs_drift": 0.0,
        "density_max_abs_drift": 0.0,
        "target_density_abs_drift": 0.0,
        "target_density_max_abs_drift": 0.0,
        "density_elements": 0,
        "samples": 0,
    }


def _update_accumulator(
    accumulator: dict[str, Any],
    prediction: torch.Tensor,
    target: torch.Tensor,
    reference_density_mean: torch.Tensor,
    field_names: Sequence[str],
    invariant_channel: int,
) -> None:
    error = prediction - target
    density_error = error[..., invariant_channel]
    conserving_density_error = density_error - density_error.mean(
        dim=-1, keepdim=True
    )
    prediction_density_mean = prediction[..., invariant_channel].mean(dim=-1)
    target_density_mean = target[..., invariant_channel].mean(dim=-1)
    prediction_drift = (prediction_density_mean - reference_density_mean).abs()
    target_drift = (target_density_mean - reference_density_mean).abs()
    accumulator["total_squared_error"] += float(error.square().sum().cpu())
    accumulator["total_elements"] += error.numel()
    for channel, name in enumerate(field_names):
        accumulator["field_squared_error"][name] += float(
            error[..., channel].square().sum().cpu()
        )
    accumulator["field_elements"] += density_error.numel()
    accumulator["density_conserving_squared_error"] += float(
        conserving_density_error.square().sum().cpu()
    )
    accumulator["density_abs_drift"] += float(prediction_drift.sum().cpu())
    accumulator["density_max_abs_drift"] = max(
        accumulator["density_max_abs_drift"], float(prediction_drift.max().cpu())
    )
    accumulator["target_density_abs_drift"] += float(target_drift.sum().cpu())
    accumulator["target_density_max_abs_drift"] = max(
        accumulator["target_density_max_abs_drift"], float(target_drift.max().cpu())
    )
    accumulator["density_elements"] += density_error.numel()
    accumulator["samples"] += prediction.shape[0]


def _finalize_accumulator(
    accumulator: Mapping[str, Any], field_names: Sequence[str], invariant_channel: int
) -> dict[str, float]:
    field_elements = int(accumulator["field_elements"])
    samples = int(accumulator["samples"])
    result = {
        "total_rmse": math.sqrt(
            float(accumulator["total_squared_error"])
            / int(accumulator["total_elements"])
        ),
        "density_conserving_rmse": math.sqrt(
            float(accumulator["density_conserving_squared_error"])
            / int(accumulator["density_elements"])
        ),
        "mean_abs_invariant_drift": float(accumulator["density_abs_drift"])
        / samples,
        "max_abs_invariant_drift": float(accumulator["density_max_abs_drift"]),
        "mean_abs_target_invariant_drift": float(
            accumulator["target_density_abs_drift"]
        )
        / samples,
        "max_abs_target_invariant_drift": float(
            accumulator["target_density_max_abs_drift"]
        ),
    }
    for channel, name in enumerate(field_names):
        result[f"{name}_rmse"] = math.sqrt(
            float(accumulator["field_squared_error"][name]) / field_elements
        )
        if channel == invariant_channel:
            result["density_rmse"] = result[f"{name}_rmse"]
    if not all(math.isfinite(value) for value in result.values()):
        raise FloatingPointError("non-finite CNS evaluation metric")
    return result


def evaluate_cns_rollout(
    *,
    model: FNO1dMulti,
    trajectories: torch.Tensor,
    grid: torch.Tensor,
    horizons: Sequence[int],
    batch_size: int,
    field_names: Sequence[str],
    device: torch.device,
    projected: bool,
) -> dict[str, dict[str, float]]:
    requested = {int(value) for value in horizons}
    maximum = max(requested)
    if model.history + maximum > trajectories.shape[1]:
        raise RuntimeError("CNS rollout horizon exceeds the available trajectory")
    accumulators = {
        horizon: _empty_accumulator(field_names) for horizon in requested
    }
    grid_device = grid.to(device=device, dtype=torch.float32)
    model.eval()
    with torch.no_grad():
        for start in range(0, trajectories.shape[0], batch_size):
            batch = trajectories[start : start + batch_size]
            state = batch[:, : model.history].permute(0, 2, 1, 3).to(
                device=device, dtype=torch.float32
            )
            reference_density_mean = batch[:, 0, :, model.invariant_channel].mean(
                dim=-1
            ).to(device=device, dtype=torch.float32)
            for horizon in range(1, maximum + 1):
                previous = state[..., -1, :]
                prediction = model(state, grid_device)
                if projected:
                    prediction = project_density(
                        previous, prediction, model.invariant_channel
                    )
                target = batch[:, model.history - 1 + horizon].to(
                    device=device, dtype=torch.float32
                )
                if horizon in requested:
                    _update_accumulator(
                        accumulators[horizon],
                        prediction,
                        target,
                        reference_density_mean,
                        field_names,
                        model.invariant_channel,
                    )
                state = torch.cat((state[..., 1:, :], prediction.unsqueeze(-2)), dim=-2)
    return {
        str(horizon): _finalize_accumulator(
            accumulators[horizon], field_names, model.invariant_channel
        )
        for horizon in sorted(requested)
    }


def cns_projection_identity_max_error(
    *,
    model: FNO1dMulti,
    trajectories: torch.Tensor,
    grid: torch.Tensor,
    batch_size: int,
    device: torch.device,
) -> float:
    maximum = 0.0
    grid_device = grid.to(device=device, dtype=torch.float32)
    model.eval()
    with torch.no_grad():
        for start in range(0, trajectories.shape[0], batch_size):
            batch = trajectories[start : start + batch_size]
            state = batch[:, : model.history].permute(0, 2, 1, 3).to(
                device=device, dtype=torch.float32
            )
            target = batch[:, model.history].to(device=device, dtype=torch.float32)
            prediction = model(state, grid_device)
            projected = project_density(
                state[..., -1, :], prediction, model.invariant_channel
            )
            free_error = prediction[..., model.invariant_channel] - target[
                ..., model.invariant_channel
            ]
            projected_error = projected[..., model.invariant_channel] - target[
                ..., model.invariant_channel
            ]
            free_conserving = free_error - free_error.mean(dim=-1, keepdim=True)
            projected_conserving = projected_error - projected_error.mean(
                dim=-1, keepdim=True
            )
            maximum = max(
                maximum,
                float((free_conserving - projected_conserving).abs().max().cpu()),
            )
    return maximum


def evaluate_cns_cases(
    *,
    model: FNO1dMulti,
    native_trajectories: torch.Tensor,
    native_grid: torch.Tensor,
    evaluation_cfg: Mapping[str, Any],
    field_names: Sequence[str],
    device: torch.device,
    projected: bool,
) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, float]]:
    strides = [int(value) for value in evaluation_cfg["spatial_strides"]]
    names = [str(value) for value in evaluation_cfg["case_names"]]
    if len(strides) != len(names):
        raise RuntimeError("CNS evaluation strides and names must have equal length")
    restriction_method = str(evaluation_cfg["restriction_method"])
    cases: dict[str, dict[str, dict[str, float]]] = {}
    identities: dict[str, float] = {}
    for stride, name in zip(strides, names, strict=True):
        trajectories = restrict_cns_torch(
            native_trajectories, stride, restriction_method
        ).contiguous()
        grid = restrict_grid(native_grid, stride, restriction_method)
        cases[name] = evaluate_cns_rollout(
            model=model,
            trajectories=trajectories,
            grid=grid,
            horizons=evaluation_cfg["horizons"],
            batch_size=int(evaluation_cfg["batch_size"]),
            field_names=field_names,
            device=device,
            projected=projected,
        )
        if projected:
            identities[name] = cns_projection_identity_max_error(
                model=model,
                trajectories=trajectories,
                grid=grid,
                batch_size=int(evaluation_cfg["batch_size"]),
                device=device,
            )
    return cases, identities


def validate_cns_data_lock(
    *, root: Path, resolved: Mapping[str, Any], dataset_path: Path
) -> tuple[Path, str, dict[str, Any]]:
    dataset_cfg = resolved["dataset"]
    raw_lock = dataset_cfg.get("lock_path")
    expected_lock_sha256 = dataset_cfg.get("lock_sha256")
    if not raw_lock or not expected_lock_sha256:
        raise RuntimeError("CNS model activation requires a frozen data lock")
    lock_path = resolve_path(root, str(raw_lock))
    actual_lock_sha256 = sha256_file(lock_path)
    if actual_lock_sha256 != str(expected_lock_sha256):
        raise RuntimeError("CNS data-lock SHA-256 mismatch")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if lock.get("schema_version") != LOCK_SCHEMA_VERSION:
        raise RuntimeError("unsupported CNS data-lock schema")
    if lock.get("benchmark_id") != resolved["benchmark_id"]:
        raise RuntimeError("CNS data-lock benchmark mismatch")
    if lock.get("protocol", {}).get("sha256") != resolved["protocol_sha256"]:
        raise RuntimeError("CNS data lock is not bound to the model protocol")
    if lock.get("source_metadata", {}).get("sha256") != resolved[
        "source_metadata_sha256"
    ]:
        raise RuntimeError("CNS data lock is not bound to source metadata")
    inspection = lock.get("inspection", {})
    if not inspection.get("hdf5", {}).get("admitted", False):
        raise RuntimeError("CNS data lock does not contain a passing admission")
    if dataset_path.stat().st_size != int(inspection["bytes"]):
        raise RuntimeError("CNS dataset byte count changed after admission")
    if sha256_file(dataset_path) != inspection["sha256"]:
        raise RuntimeError("CNS dataset SHA-256 changed after admission")
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
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"invalid CNS JSONL at line {line_number}") from error
        completed.add(str(record["run_id"]))
    return completed


def _artifact_label(root: Path, path: Path) -> str:
    """Use stable relative labels in deployments and explicit paths in tests."""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def run_cns(cfg: DictConfig) -> None:
    root = Path(__file__).resolve().parents[1]
    resolved = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(resolved, dict):
        raise TypeError("resolved CNS config must be a mapping")
    stage = str(resolved["stage"])
    if stage not in {
        "cns_factorial_confirmation",
        "cns_factorial_preflight",
        "cns_factorial_smoke",
    }:
        raise RuntimeError("unsupported CNS stage")
    formal = stage != "cns_factorial_smoke"
    mechanisms = [str(value) for value in resolved["mechanisms"]]
    if mechanisms != list(TRAINED_MECHANISMS):
        raise RuntimeError("CNS mechanisms differ from the frozen four-cell factorial")
    if formal and stage == "cns_factorial_confirmation":
        validate_cns_seed_assignment(resolved)
        if len(resolved["evaluation"]["case_names"]) * len(
            resolved["evaluation"]["horizons"]
        ) != 12:
            raise RuntimeError("formal CNS evaluation must retain all 12 cells")
    protocol_path = _validate_artifact(
        root,
        str(resolved["protocol_path"]),
        str(resolved["protocol_sha256"]),
        "CNS protocol",
    )
    source_metadata_path = _validate_artifact(
        root,
        str(resolved["source_metadata_path"]),
        str(resolved["source_metadata_sha256"]),
        "CNS source metadata",
    )
    data_decision_path = _validate_artifact(
        root,
        str(resolved["data_decision_path"]),
        str(resolved["data_decision_sha256"]),
        "CNS data decision",
    )
    if resolved.get("formal_seed_shards"):
        distributed_runtime_path = _validate_artifact(
            root,
            str(resolved["distributed_runtime_path"]),
            str(resolved["distributed_runtime_sha256"]),
            "CNS distributed runtime registration",
        )
    else:
        distributed_runtime_path = None
    if formal:
        if not resolved.get("model_decision_path") or not resolved.get(
            "model_decision_sha256"
        ):
            raise RuntimeError("formal CNS run requires a verified model decision")
        model_decision_path = _validate_artifact(
            root,
            str(resolved["model_decision_path"]),
            str(resolved["model_decision_sha256"]),
            "CNS model decision",
        )
    else:
        model_decision_path = None
    dataset_path = resolve_path(root, str(resolved["dataset"]["path"]))
    data_lock_path, data_lock_sha256, data_lock = validate_cns_data_lock(
        root=root, resolved=resolved, dataset_path=dataset_path
    )
    device = torch.device(str(resolved["device"]))
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    if int(resolved["training"]["spatial_stride"]) != 4:
        raise RuntimeError("CNS training resolution is frozen at spatial factor 4")
    if int(resolved["training"]["temporal_stride"]) != 2:
        raise RuntimeError("CNS temporal stride is frozen at 2")
    if {
        str(resolved["dataset"]["restriction_method"]),
        str(resolved["training"]["restriction_method"]),
        str(resolved["evaluation"]["restriction_method"]),
    } != {"block_average"}:
        raise RuntimeError("CNS uses block-average restriction at every stage")

    active_config_path = resolve_path(root, str(resolved["active_config_path"]))
    source_files = [
        Path(__file__),
        root / "scripts/prepare_constraint_iclr_pdebench_cns.py",
        root / "scripts/analyze_constraint_iclr_pdebench_cns.py",
        root / "scripts/constraint_iclr_common.py",
        root / "scripts/run_constraint_iclr_pdebench_fno.py",
        active_config_path,
        protocol_path,
        source_metadata_path,
        data_decision_path,
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
        raise RuntimeError("unexpected Git HEAD for CNS factorial")
    if bool(shared_provenance["git_dirty"]) is not bool(
        resolved["expected_git_dirty"]
    ):
        raise RuntimeError("unexpected dirty flag for CNS factorial")

    fields = [str(value) for value in resolved["dataset"]["fields"]]
    if fields != [str(value) for value in resolved["model"]["channel_names"]]:
        raise RuntimeError("CNS dataset and model channel order differ")
    confirmation_indices = np.arange(
        int(resolved["split"]["confirmation_start"]),
        int(resolved["split"]["confirmation_start"])
        + int(resolved["split"]["confirmation_count"]),
        dtype=np.int64,
    )
    temporal_stride = int(resolved["training"]["temporal_stride"])
    evaluation_trajectories = load_cns_trajectories(
        dataset_path,
        confirmation_indices,
        fields=fields,
        temporal_stride=temporal_stride,
        spatial_stride=1,
    )
    with h5py.File(dataset_path, "r") as handle:
        native_grid = torch.from_numpy(
            np.asarray(handle["x-coordinate"], dtype=np.float32)
        )
    output_path = resolve_path(root, str(resolved["output"]))
    checkpoint_dir = resolve_path(root, str(resolved["checkpoint_dir"]))
    completed = _existing_ids(output_path)
    dataset_sha256 = str(data_lock["inspection"]["sha256"])
    training_grid = restrict_grid(native_grid, 4, "block_average")

    for seed in validate_cns_seed_assignment(resolved):
        training_indices = select_cns_training_indices(seed, resolved["split"])
        training_index_sha256 = hashlib.sha256(training_indices.tobytes()).hexdigest()
        identities: dict[str, tuple[dict[str, Any], str]] = {}
        for mechanism in mechanisms:
            identity = {
                "schema_version": CNS_SCHEMA_VERSION,
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
        missing = [
            mechanism
            for mechanism, (_, run_id) in identities.items()
            if run_id not in completed
            or (mechanism == "free" and projection_run_id not in completed)
        ]
        if not missing:
            continue
        training_trajectories = load_cns_trajectories(
            dataset_path,
            training_indices,
            fields=fields,
            temporal_stride=temporal_stride,
            spatial_stride=4,
            restriction_method="block_average",
        )
        for mechanism in mechanisms:
            identity, run_id = identities[mechanism]
            needs_projection = mechanism == "free" and projection_run_id not in completed
            if run_id in completed and not needs_projection:
                continue
            seed_everything(stable_seed(seed, "pdebench-cns-fno-initialization"))
            model = build_cns_model(resolved["model"], mechanism).to(device)
            initialization_sha256 = model_state_sha256(model)
            parameter_count = count_trainable_parameters(model)
            if device.type == "cuda":
                torch.cuda.reset_peak_memory_stats(device)
            checkpoint_path = checkpoint_dir / f"{run_id}.pt"
            training_report = train_cns_model(
                model=model,
                trajectories=training_trajectories,
                grid=training_grid,
                training_cfg=resolved["training"],
                seed=seed,
                run_id=run_id,
                checkpoint_path=checkpoint_path,
                device=device,
            )
            evaluation_started = time.perf_counter()
            cases, _ = evaluate_cns_cases(
                model=model,
                native_trajectories=evaluation_trajectories,
                native_grid=native_grid,
                evaluation_cfg=resolved["evaluation"],
                field_names=fields,
                device=device,
                projected=False,
            )
            evaluation_runtime = time.perf_counter() - evaluation_started
            peak_memory = (
                int(torch.cuda.max_memory_allocated(device))
                if device.type == "cuda"
                else None
            )
            compute = {
                "trainable_parameters": parameter_count,
                "examples_seen": int(
                    resolved["split"]["train_trajectories_per_seed"]
                )
                * int(resolved["training"]["epochs"]),
                "proxy": parameter_count
                * int(resolved["split"]["train_trajectories_per_seed"])
                * int(resolved["training"]["epochs"]),
                "training_runtime_seconds": float(training_report["runtime_seconds"]),
                "evaluation_runtime_seconds": evaluation_runtime,
                "peak_gpu_memory_bytes": peak_memory,
                "optimization_runs": 1,
            }
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
                "compute": compute,
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
                projected_cases, projection_identity = evaluate_cns_cases(
                    model=model,
                    native_trajectories=evaluation_trajectories,
                    native_grid=native_grid,
                    evaluation_cfg=resolved["evaluation"],
                    field_names=fields,
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
                    f"completed {projection_run_id} projection seed={seed}",
                    flush=True,
                )


@hydra.main(
    version_base=None,
    config_path="../configs/constraint_iclr",
    config_name="pdebench_cns_eta0p01_factorial_20260901",
)
def main(cfg: DictConfig) -> None:
    run_cns(cfg)


if __name__ == "__main__":
    main()
