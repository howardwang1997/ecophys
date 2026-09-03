"""Run the frozen first-minibatch gradient-coupling mechanism audit."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import hydra
import numpy as np
import torch
from constraint_iclr_common import (
    append_jsonl,
    canonical_run_id,
    provenance,
    seed_everything,
    sha256_file,
    stable_seed,
)
from omegaconf import DictConfig, OmegaConf
from run_constraint_iclr_pdebench_fno import (
    FNO1d,
    build_model,
    extract_windows,
    load_trajectories,
    load_x_coordinate,
    model_state_sha256,
    resolve_path,
    restrict_grid,
    select_training_indices,
    validate_data_lock,
)
from torch import nn

DIAGNOSTIC_SCHEMA_VERSION = "constraint-iclr-gradient-coupling-v1"
COORDINATES = ("absolute", "residual")


def tensor_sha256(tensor: torch.Tensor) -> str:
    values = tensor.detach().cpu().contiguous()
    digest = hashlib.sha256()
    digest.update(str(values.dtype).encode("ascii"))
    digest.update(np.asarray(values.shape, dtype=np.int64).tobytes())
    digest.update(values.view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()


def channel_losses(
    prediction: torch.Tensor, target: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Return total, conserving, and violating MSE under the spatial-mean projector."""
    error = prediction - target
    violating = error.mean(dim=-1, keepdim=True)
    conserving = error - violating
    total_loss = error.square().mean()
    conserving_loss = conserving.square().mean()
    violating_loss = violating.square().mean()
    discrepancy = (total_loss - conserving_loss - violating_loss).abs()
    tolerance = 1e-9 + 1e-6 * total_loss.detach().abs()
    if bool(discrepancy > tolerance):
        raise RuntimeError(
            "orthogonal loss decomposition failed: "
            f"discrepancy={float(discrepancy.detach().cpu())}"
        )
    return total_loss, conserving_loss, violating_loss


def gradient_coupling(
    model: nn.Module, conserving_loss: torch.Tensor, violating_loss: torch.Tensor
) -> dict[str, float]:
    parameters = tuple(parameter for parameter in model.parameters() if parameter.requires_grad)
    gradients_q = torch.autograd.grad(
        conserving_loss, parameters, retain_graph=True, allow_unused=True
    )
    gradients_p = torch.autograd.grad(
        violating_loss, parameters, retain_graph=False, allow_unused=True
    )
    dot = torch.zeros((), device=conserving_loss.device, dtype=torch.float64)
    norm_q_squared = torch.zeros_like(dot)
    norm_p_squared = torch.zeros_like(dot)
    for parameter, gradient_q, gradient_p in zip(
        parameters, gradients_q, gradients_p, strict=True
    ):
        q = torch.zeros_like(parameter) if gradient_q is None else gradient_q
        p = torch.zeros_like(parameter) if gradient_p is None else gradient_p
        dot = dot + (q.conj() * p).real.to(torch.float64).sum()
        norm_q_squared = norm_q_squared + q.abs().square().to(torch.float64).sum()
        norm_p_squared = norm_p_squared + p.abs().square().to(torch.float64).sum()
    norm_q = norm_q_squared.sqrt()
    norm_p = norm_p_squared.sqrt()
    if not bool(norm_q > 0.0) or not bool(norm_p > 0.0):
        raise RuntimeError("zero channel-gradient norm fails the frozen diagnostic gate")
    cosine = dot / (norm_q * norm_p)
    values = {
        "q_norm": float(norm_q.detach().cpu()),
        "p_norm": float(norm_p.detach().cpu()),
        "inner_product": float(dot.detach().cpu()),
        "cosine": float(cosine.detach().cpu()),
    }
    if not all(math.isfinite(value) for value in values.values()):
        raise FloatingPointError("non-finite channel-gradient diagnostic")
    return values


def coordinate_mechanisms(coordinate: str) -> tuple[str, str]:
    if coordinate == "absolute":
        return "free", "hard_abs"
    if coordinate == "residual":
        return "free_res", "hard"
    raise ValueError(f"unsupported output coordinate: {coordinate}")


def _prediction(
    model: FNO1d, inputs: torch.Tensor, grid: torch.Tensor
) -> torch.Tensor:
    return model(inputs, grid)


def exact_one_adam_step(
    *,
    initial_state: Mapping[str, torch.Tensor],
    model_cfg: Mapping[str, Any],
    training_cfg: Mapping[str, Any],
    coordinate: str,
    inputs: torch.Tensor,
    targets: torch.Tensor,
    grid: torch.Tensor,
) -> dict[str, float]:
    free_mechanism, hard_mechanism = coordinate_mechanisms(coordinate)

    def step(mechanism: str) -> tuple[float, float]:
        model = build_model(model_cfg, mechanism).to(inputs.device)
        model.load_state_dict(initial_state)
        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=float(training_cfg["learning_rate"]),
            weight_decay=float(training_cfg["weight_decay"]),
        )
        model.train()
        before = _prediction(model, inputs, grid)
        loss = (before - targets).square().mean()
        if not bool(torch.isfinite(loss)):
            raise FloatingPointError("non-finite one-step training loss")
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        with torch.no_grad():
            after = _prediction(model, inputs, grid)
            _, conserving_after, _ = channel_losses(after, targets)
        return float(loss.detach().cpu()), float(conserving_after.detach().cpu())

    free_training_loss, free_q_after = step(free_mechanism)
    hard_training_loss, hard_q_after = step(hard_mechanism)
    values = {
        "free_training_loss": free_training_loss,
        "hard_training_loss": hard_training_loss,
        "free_conserving_loss_after": free_q_after,
        "hard_conserving_loss_after": hard_q_after,
        "one_step_enforcement_credit": free_q_after - hard_q_after,
    }
    if not all(math.isfinite(value) for value in values.values()):
        raise FloatingPointError("non-finite exact one-step diagnostic")
    return values


def reconstruct_first_minibatch(
    *,
    dataset_path: Path,
    seed: int,
    split_cfg: Mapping[str, Any],
    model_cfg: Mapping[str, Any],
    training_cfg: Mapping[str, Any],
) -> tuple[torch.Tensor, torch.Tensor, dict[str, str | int]]:
    training_indices = select_training_indices(seed, split_cfg)
    temporal_stride = int(training_cfg["temporal_stride"])
    expected_time_steps = int(training_cfg["source_time_steps"])
    sampled_time_steps = len(range(0, expected_time_steps, temporal_stride))
    history = int(model_cfg["history"])
    num_windows = sampled_time_steps - history
    if num_windows <= 0:
        raise RuntimeError("frozen temporal sampling leaves no training window")
    offset_rng = np.random.default_rng(stable_seed(seed, "pdebench-window-offsets"))
    base_offsets = torch.from_numpy(
        offset_rng.integers(0, num_windows, size=training_indices.size, dtype=np.int64)
    )
    target_indices = history + base_offsets
    order_generator = torch.Generator().manual_seed(
        stable_seed(seed, "pdebench-minibatch-order:0")
    )
    order = torch.randperm(training_indices.size, generator=order_generator)
    batch_size = int(training_cfg["batch_size"])
    rows = order[:batch_size]
    selected_indices = training_indices[rows.numpy()]
    selected_targets = target_indices[rows].contiguous()
    trajectories = load_trajectories(
        dataset_path,
        selected_indices,
        temporal_stride=temporal_stride,
        spatial_stride=int(training_cfg["spatial_stride"]),
        restriction_method=str(training_cfg["restriction_method"]),
    )
    inputs, targets = extract_windows(
        trajectories,
        torch.arange(selected_indices.size),
        selected_targets,
        history,
    )
    hashes: dict[str, str | int] = {
        "training_index_sha256": hashlib.sha256(training_indices.tobytes()).hexdigest(),
        "first_batch_trajectory_sha256": hashlib.sha256(
            np.ascontiguousarray(selected_indices).tobytes()
        ).hexdigest(),
        "first_batch_target_index_sha256": hashlib.sha256(
            selected_targets.numpy().tobytes()
        ).hexdigest(),
        "inputs_sha256": tensor_sha256(inputs),
        "targets_sha256": tensor_sha256(targets),
        "batch_size": int(selected_indices.size),
    }
    return inputs, targets, hashes


def _existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        ids.add(str(record["run_id"]))
    return ids


def run(cfg: DictConfig) -> None:
    root = Path(__file__).resolve().parents[1]
    resolved = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(resolved, dict):
        raise TypeError("resolved diagnostic config must be a mapping")
    if resolved.get("diagnostic_stage") != "gradient_coupling":
        raise RuntimeError("diagnostic_stage must be gradient_coupling")
    if [str(value) for value in resolved["mechanisms"]] != [
        "free",
        "free_res",
        "hard_abs",
        "hard",
    ]:
        raise RuntimeError("gradient audit requires the exact four-cell factorial")

    dataset_cfg = resolved["dataset"]
    split_cfg = resolved["split"]
    model_cfg = resolved["model"]
    training_cfg = dict(resolved["training"])
    if not all(
        isinstance(value, Mapping)
        for value in (dataset_cfg, split_cfg, model_cfg, training_cfg)
    ):
        raise TypeError("nested diagnostic config sections must be mappings")
    training_cfg["source_time_steps"] = int(dataset_cfg["expected_shape"][1])
    dataset_path = resolve_path(root, str(dataset_cfg["path"]))
    lock_path, lock_sha256, lock = validate_data_lock(
        root=root, resolved=resolved, dataset_path=dataset_path
    )
    dataset_sha256 = str(lock["inspection"]["sha256"])

    protocol_path = resolve_path(root, str(resolved["gradient_protocol_path"]))
    protocol_sha256 = sha256_file(protocol_path)
    if protocol_sha256 != str(resolved["gradient_protocol_sha256"]):
        raise RuntimeError("gradient-coupling protocol SHA-256 mismatch")
    factorial_protocol_path = resolve_path(root, str(resolved["protocol_path"]))
    factorial_protocol_sha256 = sha256_file(factorial_protocol_path)
    if factorial_protocol_sha256 != str(resolved["protocol_sha256"]):
        raise RuntimeError("factorial protocol SHA-256 mismatch")
    decision_path = resolve_path(root, str(resolved["gradient_decision_path"]))
    if not decision_path.is_file():
        raise RuntimeError("gradient-coupling decision is missing")

    source_files = [
        Path(__file__),
        root / "scripts/constraint_iclr_common.py",
        root / "scripts/run_constraint_iclr_pdebench_fno.py",
        protocol_path,
        factorial_protocol_path,
        decision_path,
        lock_path,
    ]
    for raw_path in resolved.get("gradient_source_artifact_paths", []):
        source_files.append(resolve_path(root, str(raw_path)))
    shared_provenance = provenance(
        root=root, resolved_config=resolved, source_files=source_files
    )
    if shared_provenance["git_head"] != str(resolved["expected_git_head"]):
        raise RuntimeError("unexpected Git HEAD for gradient audit")
    if bool(shared_provenance["git_dirty"]) is not bool(resolved["expected_git_dirty"]):
        raise RuntimeError("unexpected dirty-worktree state for gradient audit")

    device = torch.device(str(resolved["device"]))
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    native_grid = load_x_coordinate(dataset_path, 1)
    training_grid = restrict_grid(
        native_grid,
        int(training_cfg["spatial_stride"]),
        str(training_cfg["restriction_method"]),
    ).to(device=device, dtype=torch.float32)
    output = resolve_path(root, str(resolved["gradient_output"]))
    completed = _existing_ids(output)

    for seed in [int(value) for value in resolved["seeds"]]:
        inputs_cpu, targets_cpu, batch_hashes = reconstruct_first_minibatch(
            dataset_path=dataset_path,
            seed=seed,
            split_cfg=split_cfg,
            model_cfg=model_cfg,
            training_cfg=training_cfg,
        )
        inputs = inputs_cpu.to(device=device, dtype=torch.float32)
        targets = targets_cpu.to(device=device, dtype=torch.float32)
        for coordinate in COORDINATES:
            identity = {
                "schema_version": DIAGNOSTIC_SCHEMA_VERSION,
                "benchmark_id": str(resolved["benchmark_id"]),
                "dataset_sha256": dataset_sha256,
                "data_lock_sha256": lock_sha256,
                "gradient_protocol_sha256": protocol_sha256,
                "factorial_protocol_sha256": factorial_protocol_sha256,
                "seed": seed,
                "coordinate": coordinate,
                "batch": batch_hashes,
            }
            run_id = canonical_run_id(identity)
            if run_id in completed:
                continue
            free_mechanism, _ = coordinate_mechanisms(coordinate)
            seed_everything(stable_seed(seed, "pdebench-fno-initialization"))
            model = build_model(model_cfg, free_mechanism).to(device)
            initialization_sha256 = model_state_sha256(model)
            initial_state = {
                name: value.detach().clone() for name, value in model.state_dict().items()
            }
            prediction = _prediction(model, inputs, training_grid)
            total_loss, conserving_loss, violating_loss = channel_losses(
                prediction, targets
            )
            coupling = gradient_coupling(model, conserving_loss, violating_loss)
            one_step = exact_one_adam_step(
                initial_state=initial_state,
                model_cfg=model_cfg,
                training_cfg=training_cfg,
                coordinate=coordinate,
                inputs=inputs,
                targets=targets,
                grid=training_grid,
            )
            record: dict[str, Any] = {
                **identity,
                "run_id": run_id,
                "initialization_sha256": initialization_sha256,
                "losses_before": {
                    "total": float(total_loss.detach().cpu()),
                    "conserving": float(conserving_loss.detach().cpu()),
                    "violating": float(violating_loss.detach().cpu()),
                    "decomposition_abs_error": float(
                        (total_loss - conserving_loss - violating_loss)
                        .abs()
                        .detach()
                        .cpu()
                    ),
                },
                "gradients": coupling,
                "one_step": one_step,
                "optimizer": {
                    "name": "Adam",
                    "learning_rate": float(training_cfg["learning_rate"]),
                    "weight_decay": float(training_cfg["weight_decay"]),
                },
                "provenance": shared_provenance,
            }
            append_jsonl(output, record)
            completed.add(run_id)
            print(f"completed {run_id} {coordinate} seed={seed}", flush=True)


@hydra.main(
    version_base=None,
    config_path="../configs/constraint_iclr",
    config_name="pdebench_advection_fno_gradient_coupling_20260901",
)
def main(cfg: DictConfig) -> None:
    run(cfg)


if __name__ == "__main__":
    main()
