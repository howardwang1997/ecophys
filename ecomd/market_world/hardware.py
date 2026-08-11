"""Small deterministic CUDA continuation probe for Experiment 141."""

from __future__ import annotations

import io
import math
import os
import subprocess
import time
from dataclasses import asdict
from typing import cast

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import torch
from torch import Tensor, nn

from .protocol import HardwareProbeSettings


class ProbePolicy(nn.Module):
    def __init__(self, feature_dim: int, hidden_dim: int) -> None:
        super().__init__()
        self.recurrent = nn.GRU(feature_dim, hidden_dim, batch_first=True)
        self.output = nn.Linear(hidden_dim, 1)

    def forward(self, features: Tensor) -> Tensor:
        encoded, _ = self.recurrent(features)
        return cast(Tensor, self.output(encoded[:, -1]).squeeze(-1))


def _initialize_deterministically(model: nn.Module) -> None:
    with torch.no_grad():
        offset = 0
        for parameter in model.parameters():
            values = torch.arange(
                offset,
                offset + parameter.numel(),
                dtype=torch.float64,
            )
            initialized = 0.025 * torch.sin(values * 0.017 + 0.31)
            parameter.copy_(initialized.reshape(parameter.shape).to(parameter.dtype))
            offset += parameter.numel()


def _fixed_batch(settings: HardwareProbeSettings, device: torch.device) -> tuple[Tensor, Tensor]:
    count = settings.batch_size * settings.sequence_length * settings.feature_dim
    values = torch.arange(count, dtype=torch.float64)
    features = (
        torch.sin(values * 0.013) + 0.25 * torch.cos(values * 0.031)
    ).reshape(settings.batch_size, settings.sequence_length, settings.feature_dim)
    target = torch.tanh(features[:, :, 0].mean(dim=1) - 0.5 * features[:, :, 1].mean(dim=1))
    return features.to(dtype=torch.float32, device=device), target.to(dtype=torch.float32, device=device)


def _train_steps(
    model: ProbePolicy,
    optimizer: torch.optim.Optimizer,
    features: Tensor,
    target: Tensor,
    start: int,
    stop: int,
) -> tuple[list[float], bool]:
    losses: list[float] = []
    finite_gradients = True
    for _ in range(start, stop):
        optimizer.zero_grad(set_to_none=True)
        prediction = model(features)
        loss = torch.mean((prediction - target) ** 2)
        loss.backward()  # type: ignore[no-untyped-call]
        finite_gradients = finite_gradients and all(
            parameter.grad is None or bool(torch.isfinite(parameter.grad).all().item())
            for parameter in model.parameters()
        )
        optimizer.step()
        losses.append(float(loss.detach().cpu()))
    return losses, finite_gradients


def _new_model(
    settings: HardwareProbeSettings,
    device: torch.device,
) -> tuple[ProbePolicy, torch.optim.Adam]:
    model = ProbePolicy(settings.feature_dim, settings.hidden_dim)
    _initialize_deterministically(model)
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=settings.learning_rate)
    return model, optimizer


def _gpu_uuid(device_index: int) -> str:
    result = subprocess.run(
        [
            "nvidia-smi",
            f"--id={device_index}",
            "--query-gpu=uuid",
            "--format=csv,noheader",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def run_cuda_probe(
    settings: HardwareProbeSettings,
    *,
    worker: str,
    device_index: int = 0,
) -> dict[str, object]:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for the hardware probe")
    if device_index >= torch.cuda.device_count():
        raise ValueError("requested CUDA device does not exist")
    if settings.split_step <= 0 or settings.split_step >= settings.steps:
        raise ValueError("split_step must be strictly inside the training run")

    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    device = torch.device(f"cuda:{device_index}")
    torch.cuda.set_device(device)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats(device)
    features, target = _fixed_batch(settings, device)
    started = time.perf_counter()

    continuous_model, continuous_optimizer = _new_model(settings, device)
    continuous_losses, continuous_finite = _train_steps(
        continuous_model,
        continuous_optimizer,
        features,
        target,
        0,
        settings.steps,
    )

    split_model, split_optimizer = _new_model(settings, device)
    split_losses_a, split_finite_a = _train_steps(
        split_model,
        split_optimizer,
        features,
        target,
        0,
        settings.split_step,
    )
    checkpoint = io.BytesIO()
    torch.save(
        {
            "model": split_model.state_dict(),
            "optimizer": split_optimizer.state_dict(),
            "step": settings.split_step,
        },
        checkpoint,
    )
    checkpoint.seek(0)
    resumed_model, resumed_optimizer = _new_model(settings, device)
    payload = cast(
        dict[str, object],
        torch.load(checkpoint, map_location=device, weights_only=False),
    )
    resumed_model.load_state_dict(cast(dict[str, Tensor], payload["model"]))
    resumed_optimizer.load_state_dict(cast(dict[str, object], payload["optimizer"]))
    split_losses_b, split_finite_b = _train_steps(
        resumed_model,
        resumed_optimizer,
        features,
        target,
        settings.split_step,
        settings.steps,
    )
    torch.cuda.synchronize(device)

    maximum_parameter_delta = max(
        float(torch.max(torch.abs(left - right)).detach().cpu())
        for left, right in zip(
            continuous_model.parameters(),
            resumed_model.parameters(),
            strict=True,
        )
    )
    split_losses = split_losses_a + split_losses_b
    maximum_loss_delta = max(
        abs(left - right) for left, right in zip(continuous_losses, split_losses, strict=True)
    )
    properties = torch.cuda.get_device_properties(device)
    peak_reserved = torch.cuda.max_memory_reserved(device)
    memory_fraction = peak_reserved / properties.total_memory
    finite_losses = all(math.isfinite(loss) for loss in continuous_losses + split_losses)
    return {
        "schema": "exp141-hardware-probe-v1",
        "worker": worker,
        "settings": asdict(settings),
        "device": {
            "index": device_index,
            "name": properties.name,
            "uuid": _gpu_uuid(device_index),
            "total_memory_bytes": properties.total_memory,
            "compute_capability": [properties.major, properties.minor],
        },
        "software": {
            "torch": torch.__version__,
            "cuda_runtime": torch.version.cuda,
            "cudnn": torch.backends.cudnn.version(),  # type: ignore[no-untyped-call]
        },
        "continuous_losses": continuous_losses,
        "split_losses": split_losses,
        "final_loss": continuous_losses[-1],
        "finite_losses": finite_losses,
        "finite_gradients": continuous_finite and split_finite_a and split_finite_b,
        "maximum_resume_loss_delta": maximum_loss_delta,
        "maximum_resume_parameter_delta": maximum_parameter_delta,
        "exact_resume": maximum_loss_delta == 0.0 and maximum_parameter_delta == 0.0,
        "peak_reserved_bytes": peak_reserved,
        "peak_reserved_fraction": memory_fraction,
        "wall_seconds": time.perf_counter() - started,
    }


def merge_hardware_probes(
    settings: HardwareProbeSettings,
    probes: list[dict[str, object]],
) -> dict[str, object]:
    expected_workers = {"v100-a", "v100-b", "rtx2060"}
    workers = {str(probe["worker"]) for probe in probes}
    if workers != expected_workers:
        raise ValueError(f"expected {expected_workers}, received {workers}")

    def number(probe: dict[str, object], key: str) -> float:
        value = probe[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"probe field {key} is not numeric")
        return float(value)

    final_losses = [number(probe, "final_loss") for probe in probes]
    denominator = max(abs(float(np_mean(final_losses))), 1e-15)
    relative_spread = (max(final_losses) - min(final_losses)) / denominator
    per_worker = {
        str(probe["worker"]): {
            "finite_losses": bool(probe["finite_losses"]),
            "finite_gradients": bool(probe["finite_gradients"]),
            "exact_resume": bool(probe["exact_resume"]),
            "peak_reserved_fraction": number(probe, "peak_reserved_fraction"),
            "final_loss": number(probe, "final_loss"),
            "pass": (
                bool(probe["finite_losses"])
                and bool(probe["finite_gradients"])
                and bool(probe["exact_resume"])
                and number(probe, "peak_reserved_fraction") <= settings.maximum_memory_fraction
            ),
        }
        for probe in probes
    }
    cross_device_pass = relative_spread <= settings.cross_device_relative_loss_tolerance
    return {
        "schema": "exp141-hardware-merge-v1",
        "workers": per_worker,
        "cross_device_relative_loss_spread": relative_spread,
        "cross_device_tolerance": settings.cross_device_relative_loss_tolerance,
        "cross_device_pass": cross_device_pass,
        "hardware_pass": all(bool(value["pass"]) for value in per_worker.values())
        and cross_device_pass,
    }


def np_mean(values: list[float]) -> float:
    return sum(values) / len(values)
