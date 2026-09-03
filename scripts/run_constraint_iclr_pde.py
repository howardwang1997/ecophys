"""Run the frozen ICLR extension for PDE and contraction-holdout systems."""

from __future__ import annotations

import json
import math
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import hydra
import numpy as np
import torch
import torch.nn.functional as functional
from constraint_iclr_common import (
    SCHEMA_VERSION,
    append_jsonl,
    canonical_run_id,
    count_trainable_parameters,
    pde_metrics,
    project_pde_output,
    provenance,
    seed_everything,
    stable_seed,
    validate_selection_lock,
)
from omegaconf import DictConfig, OmegaConf
from torch import nn

TensorMap = Callable[[torch.Tensor], torch.Tensor]


def _preserve_mean(inputs: torch.Tensor, outputs: torch.Tensor) -> torch.Tensor:
    dims = tuple(range(1, inputs.ndim))
    return outputs + inputs.mean(dim=dims, keepdim=True) - outputs.mean(dim=dims, keepdim=True)


def spectral_step_1d(
    inputs: torch.Tensor,
    *,
    system: str,
    c: float,
    nu: float,
    dt: float,
    gamma: float,
    burgers_substeps: int,
) -> torch.Tensor:
    """Advance a batch in float64 and enforce the analytic mean invariant."""
    work = inputs.to(dtype=torch.float64)
    n = work.shape[-1]
    k = torch.fft.fftfreq(n, d=1.0 / n, device=work.device, dtype=work.dtype)
    wave = 2.0 * torch.pi * k / n
    if system == "advection":
        multiplier = torch.exp(-1j * c * wave * dt)
        result = torch.fft.ifft(torch.fft.fft(work, dim=-1) * multiplier, dim=-1).real
    elif system == "diffusion":
        multiplier = torch.exp(-nu * wave.square() * dt)
        result = torch.fft.ifft(torch.fft.fft(work, dim=-1) * multiplier, dim=-1).real
    elif system in {"contraction_near", "contraction_strong"}:
        attenuation = torch.where(k == 0, torch.ones_like(k), torch.exp(torch.full_like(k, -gamma * dt)))
        multiplier = attenuation * torch.exp(-1j * c * wave * dt)
        result = torch.fft.ifft(torch.fft.fft(work, dim=-1) * multiplier, dim=-1).real
    elif system == "burgers":
        ik = (1j * wave).to(work.device)
        wave_sq = wave.square()

        def rhs(state: torch.Tensor) -> torch.Tensor:
            convective = torch.fft.ifft(
                torch.fft.fft(state.square(), dim=-1) * ik * -0.5,
                dim=-1,
            ).real
            diffusive = torch.fft.ifft(
                torch.fft.fft(state, dim=-1) * (-nu * wave_sq),
                dim=-1,
            ).real
            return convective + diffusive

        step = dt / burgers_substeps
        result = work
        for _ in range(burgers_substeps):
            k1 = rhs(result)
            k2 = rhs(result + 0.5 * step * k1)
            k3 = rhs(result + 0.5 * step * k2)
            k4 = rhs(result + step * k3)
            result = result + step * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
    else:
        raise ValueError(f"unknown 1D system: {system}")
    return _preserve_mean(work, result).to(dtype=inputs.dtype)


def spectral_step_2d(
    inputs: torch.Tensor,
    *,
    c: float,
    nu: float,
    dt: float,
) -> torch.Tensor:
    work = inputs.to(dtype=torch.float64)
    height, width = work.shape[-2:]
    ky = torch.fft.fftfreq(height, d=1.0 / height, device=work.device, dtype=work.dtype).view(-1, 1)
    kx = torch.fft.fftfreq(width, d=1.0 / width, device=work.device, dtype=work.dtype).view(1, -1)
    exponent = (
        -nu * 4.0 * torch.pi**2 * (kx.square() + ky.square()) - 0.5j * 2.0 * torch.pi * c * (kx + ky)
    ) * dt
    result = torch.fft.ifft2(torch.fft.fft2(work, dim=(-2, -1)) * torch.exp(exponent), dim=(-2, -1)).real
    return _preserve_mean(work, result).to(dtype=inputs.dtype)


def build_truth(cfg: Mapping[str, Any]) -> TensorMap:
    if cfg["family"] == "C":
        return lambda value: spectral_step_2d(
            value,
            c=float(cfg["c"]),
            nu=float(cfg["nu"]),
            dt=float(cfg["dt"]),
        )
    return lambda value: spectral_step_1d(
        value,
        system=str(cfg["system"]),
        c=float(cfg["c"]),
        nu=float(cfg["nu"]),
        dt=float(cfg["dt"]),
        gamma=float(cfg["gamma"]),
        burgers_substeps=int(cfg["burgers_substeps"]),
    )


def mode_sigma_1d(n: int, sigma_flat: float) -> np.ndarray:
    frequency = np.fft.fftfreq(n, d=1.0 / n).astype(int)
    sigma = np.full(n, 0.5, dtype=np.float64)
    sigma[frequency == 0] = 1.0
    sigma[np.abs(frequency) == 1] = sigma_flat
    sigma[np.abs(frequency) == n // 8] = 1.0
    return sigma


def make_samples_1d(
    n: int,
    n_samples: int,
    sigma_flat: float,
    rng: np.random.Generator,
) -> torch.Tensor:
    noise = rng.normal(size=(n_samples, n))
    filtered = np.fft.ifft(np.fft.fft(noise, axis=-1) * mode_sigma_1d(n, sigma_flat), axis=-1).real
    return torch.tensor(filtered, dtype=torch.float32)


def make_samples_2d(
    size: int,
    n_samples: int,
    sigma_flat: float,
    rng: np.random.Generator,
) -> torch.Tensor:
    ky, kx = np.meshgrid(
        np.fft.fftfreq(size, d=1.0 / size),
        np.fft.fftfreq(size, d=1.0 / size),
        indexing="ij",
    )
    norm = np.sqrt(kx**2 + ky**2)
    sigma = np.full((size, size), 0.5, dtype=np.float64)
    sigma[(kx == 0) & (ky == 0)] = 1.0
    sigma[(norm >= 4.0) & (norm <= 7.0)] = 1.0
    sigma[((np.abs(kx) == 1) & (ky == 0)) | ((kx == 0) & (np.abs(ky) == 1))] = sigma_flat
    noise = rng.normal(size=(n_samples, size, size))
    filtered = np.fft.ifft2(np.fft.fft2(noise, axes=(-2, -1)) * sigma, axes=(-2, -1)).real
    return torch.tensor(filtered, dtype=torch.float32)


def _mode_batch_1d(
    n: int,
    frequency: int,
    n_samples: int,
    scale: float,
    rng: np.random.Generator,
) -> torch.Tensor:
    grid = np.arange(n, dtype=np.float64)
    phase = rng.uniform(0.0, 2.0 * np.pi, size=(n_samples, 1))
    values = scale * np.cos(2.0 * np.pi * frequency * grid[None, :] / n + phase)
    return torch.tensor(values, dtype=torch.float32)


def _mode_batch_2d(
    size: int,
    kx: int,
    ky: int,
    n_samples: int,
    scale: float,
    rng: np.random.Generator,
) -> torch.Tensor:
    yy, xx = np.meshgrid(np.arange(size), np.arange(size), indexing="ij")
    phase = rng.uniform(0.0, 2.0 * np.pi, size=(n_samples, 1, 1))
    angle = 2.0 * np.pi * (kx * xx + ky * yy) / size
    values = scale * np.cos(angle[None, :, :] + phase)
    return torch.tensor(values, dtype=torch.float32)


def bandlimited_upsample(inputs: torch.Tensor, factor: int) -> torch.Tensor:
    n = inputs.shape[-1]
    spectrum = torch.fft.fft(inputs, dim=-1)
    upsampled = torch.zeros(*spectrum.shape[:-1], n * factor, dtype=spectrum.dtype, device=spectrum.device)
    half = n // 2
    upsampled[..., :half] = spectrum[..., :half]
    upsampled[..., -half:] = spectrum[..., -half:]
    return torch.fft.ifft(upsampled, dim=-1).real * factor


class MLP(nn.Module):
    def __init__(self, n: int, hidden: int, mode: str) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
            nn.Linear(hidden, n),
        )
        self.mode = mode

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        raw = self.net(inputs)
        if self.mode == "hard":
            return inputs + raw - raw.mean(dim=-1, keepdim=True)
        if self.mode == "residual":
            return inputs + raw
        return raw


def _conv_block(inputs: int, outputs: int, dimensions: int) -> nn.Module:
    convolution = nn.Conv1d if dimensions == 1 else nn.Conv2d
    groups = math.gcd(8, outputs)
    return nn.Sequential(
        convolution(inputs, outputs, kernel_size=5, padding=2),
        nn.GroupNorm(groups, outputs),
        nn.SiLU(),
        convolution(outputs, outputs, kernel_size=5, padding=2),
        nn.GroupNorm(groups, outputs),
        nn.SiLU(),
    )


class UNet(nn.Module):
    def __init__(self, channels: int, dimensions: int, mode: str) -> None:
        super().__init__()
        transpose = nn.ConvTranspose1d if dimensions == 1 else nn.ConvTranspose2d
        head = nn.Conv1d if dimensions == 1 else nn.Conv2d
        self.dimensions = dimensions
        self.mode = mode
        self.enc1 = _conv_block(1, channels, dimensions)
        self.enc2 = _conv_block(channels, channels * 2, dimensions)
        self.bottleneck = _conv_block(channels * 2, channels * 2, dimensions)
        self.up2 = transpose(channels * 2, channels * 2, kernel_size=2, stride=2)
        self.dec2 = _conv_block(channels * 4, channels * 2, dimensions)
        self.up1 = transpose(channels * 2, channels, kernel_size=2, stride=2)
        self.dec1 = _conv_block(channels * 2, channels, dimensions)
        self.head = head(channels, 1, kernel_size=1)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        expanded = inputs.unsqueeze(1)
        pool = functional.avg_pool1d if self.dimensions == 1 else functional.avg_pool2d
        encoded1 = self.enc1(expanded)
        encoded2 = self.enc2(pool(encoded1, 2))
        bottleneck = self.bottleneck(pool(encoded2, 2))
        decoded2 = self.dec2(torch.cat([self.up2(bottleneck), encoded2], dim=1))
        decoded1 = self.dec1(torch.cat([self.up1(decoded2), encoded1], dim=1))
        raw = self.head(decoded1).squeeze(1)
        if self.mode == "hard":
            dims = tuple(range(1, raw.ndim))
            return inputs + raw - raw.mean(dim=dims, keepdim=True)
        if self.mode == "residual":
            return inputs + raw
        return raw


def mechanism_mode(mechanism: str) -> str:
    if mechanism == "hard":
        return "hard"
    if mechanism == "free_res":
        return "residual"
    if mechanism in {"free", "soft30"}:
        return "absolute"
    raise ValueError(f"unsupported mechanism: {mechanism}")


def build_model(cfg: Mapping[str, Any], capacity: int, mechanism: str) -> nn.Module:
    mode = mechanism_mode(mechanism)
    if cfg["family"] in {"A", "H"}:
        return MLP(int(cfg["resolution"]), capacity, mode)
    dimensions = 1 if cfg["family"] == "B" else 2
    return UNet(capacity, dimensions, mode)


def build_dataset(
    cfg: Mapping[str, Any],
    seed: int,
    device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, dict[str, torch.Tensor]]:
    truth = build_truth(cfg)
    data_rng = np.random.default_rng(stable_seed(seed, "pde-data"))
    id_rng = np.random.default_rng(stable_seed(seed, "pde-id"))
    ood_rng = np.random.default_rng(stable_seed(seed, "pde-ood"))
    resolution = int(cfg["resolution"])
    sigma_flat = float(cfg["sigma_flat"])
    if cfg["family"] == "C":
        train = make_samples_2d(resolution, int(cfg["n_train"]), sigma_flat, data_rng).to(device)
        id_inputs = make_samples_2d(resolution, int(cfg["n_id"]), sigma_flat, id_rng).to(device)
        cases = {
            "ood_flat": _mode_batch_2d(resolution, 1, 0, int(cfg["n_ood"]), 2.5, ood_rng).to(device),
            "ood_rich": _mode_batch_2d(resolution, 4, 4, int(cfg["n_ood"]), 2.5, ood_rng).to(device),
            "ood_mass": _mode_batch_2d(resolution, 4, 4, int(cfg["n_ood"]), 1.0, ood_rng).to(device) + 2.0,
        }
    else:
        train = make_samples_1d(resolution, int(cfg["n_train"]), sigma_flat, data_rng).to(device)
        id_inputs = make_samples_1d(resolution, int(cfg["n_id"]), sigma_flat, id_rng).to(device)
        rich_frequency = resolution // 8
        cases = {
            "ood_flat": _mode_batch_1d(resolution, 1, int(cfg["n_ood"]), 2.5, ood_rng).to(device),
            "ood_rich": _mode_batch_1d(resolution, rich_frequency, int(cfg["n_ood"]), 2.5, ood_rng).to(
                device
            ),
            "ood_mass": _mode_batch_1d(resolution, rich_frequency, int(cfg["n_ood"]), 1.0, ood_rng).to(device)
            + 2.0,
        }
        if cfg["family"] == "B":
            amplitude = make_samples_1d(resolution, int(cfg["n_ood"]), sigma_flat, ood_rng).to(device) * 2.5
            cases["ood_amp"] = amplitude
            cases["ood_res"] = bandlimited_upsample(amplitude, 2)
    with torch.no_grad():
        train_target = truth(train)
        id_target = truth(id_inputs)
    return train, train_target, id_inputs, id_target, cases


def train_model(
    *,
    model: nn.Module,
    mechanism: str,
    inputs: torch.Tensor,
    targets: torch.Tensor,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    order_seed: int,
) -> None:
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    generator = torch.Generator(device=inputs.device)
    generator.manual_seed(order_seed)
    n_samples = inputs.shape[0]
    spatial_dims = tuple(range(1, inputs.ndim))
    model.train()
    for _ in range(epochs):
        order = torch.randperm(n_samples, generator=generator, device=inputs.device)
        for start in range(0, n_samples, batch_size):
            index = order[start : start + batch_size]
            batch_inputs = inputs[index]
            batch_targets = targets[index]
            prediction = model(batch_inputs)
            loss = (prediction - batch_targets).square().mean()
            if mechanism == "soft30":
                violation = prediction.mean(dim=spatial_dims) - batch_inputs.mean(dim=spatial_dims)
                loss = loss + 30.0 * violation.square().mean()
            if not torch.isfinite(loss):
                raise FloatingPointError("non-finite training loss")
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()


def evaluate_rollouts(
    model: nn.Module,
    initial: torch.Tensor,
    truth: TensorMap,
    horizons: list[int],
    *,
    projected: bool,
) -> dict[str, dict[str, float]]:
    requested = set(horizons)
    maximum = max(horizons)
    prediction = initial
    target = initial
    metrics: dict[str, dict[str, float]] = {}
    model.eval()
    with torch.no_grad():
        for horizon in range(1, maximum + 1):
            previous = prediction
            prediction = model(prediction)
            if projected:
                prediction = project_pde_output(previous, prediction)
            target = truth(target)
            if horizon in requested:
                metrics[str(horizon)] = pde_metrics(prediction, target)
    return metrics


def _existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "run_id" in record:
            ids.add(str(record["run_id"]))
    return ids


def run(cfg: DictConfig) -> None:
    root = Path(__file__).resolve().parents[1]
    resolved = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(resolved, dict):
        raise TypeError("resolved Hydra config must be a mapping")
    output = Path(str(resolved["output"]))
    if not output.is_absolute():
        output = root / output
    device = torch.device(str(resolved["device"]))
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    selection_lock_path = validate_selection_lock(root, resolved)
    truth = build_truth(resolved)
    source_files = [
        Path(__file__),
        root / "scripts/constraint_iclr_common.py",
        root / "scripts/launch_constraint_iclr_pilot.py",
        root / "scripts/launch_constraint_iclr_confirmation.py",
        root / "configs/constraint_iclr/pde.yaml",
        root / "configs/constraint_iclr/pde_pilot.yaml",
        root / "configs/constraint_iclr/pde_confirmation.yaml",
        root / "configs/constraint_iclr/pilot_manifest.yaml",
        root / "configs/constraint_iclr/pilot_manifest_bc_thin.yaml",
        root / "configs/constraint_iclr/pilot_manifest_bc_expand.yaml",
        root / "configs/constraint_iclr/pilot_manifest_ahm_expand.yaml",
        root / "configs/constraint_iclr/confirmation_manifest.yaml",
        root / "papers/proposal/ecomd_constraint_attribution_iclr_extension_freeze_2026-08-30.md",
        root
        / "papers/proposal/ecomd_constraint_attribution_iclr_pilot_timing_amendment_2026-08-30.md",
        root
        / "papers/proposal/ecomd_constraint_attribution_iclr_compute_authority_amendment_2026-08-30.md",
    ]
    if selection_lock_path is not None:
        source_files.append(selection_lock_path)
    shared_provenance = provenance(root=root, resolved_config=resolved, source_files=source_files)
    completed = _existing_ids(output)

    for seed in [int(value) for value in resolved["seeds"]]:
        train_inputs, train_targets, id_inputs, id_targets, cases = build_dataset(resolved, seed, device)
        for capacity in [int(value) for value in resolved["capacity_grid"]]:
            for epochs in [int(value) for value in resolved["epochs_grid"]]:
                for learning_rate in [float(value) for value in resolved["lr_grid"]]:
                    for mechanism in [str(value) for value in resolved["mechanisms"]]:
                        base_identity = {
                            "schema_version": SCHEMA_VERSION,
                            "stage": str(resolved["stage"]),
                            "family": str(resolved["family"]),
                            "system": str(resolved["system"]),
                            "seed": seed,
                            "mechanism": mechanism,
                            "capacity": capacity,
                            "epochs": epochs,
                            "learning_rate": learning_rate,
                            "n_train": int(resolved["n_train"]),
                            "protocol_sha256": shared_provenance["source_sha256"].get(
                                "papers/proposal/ecomd_constraint_attribution_iclr_extension_freeze_2026-08-30.md"
                            ),
                        }
                        if selection_lock_path is not None:
                            base_identity["selection_lock_sha256"] = str(
                                resolved["selection_lock_sha256"]
                            )
                        run_id = canonical_run_id(base_identity)
                        projection_id = canonical_run_id({**base_identity, "mechanism": "projection"})
                        if run_id in completed and (mechanism != "free" or projection_id in completed):
                            continue

                        model_seed = stable_seed(seed, f"model:{resolved['family']}:{capacity}")
                        seed_everything(model_seed)
                        model = build_model(resolved, capacity, mechanism).to(device)
                        parameter_count = count_trainable_parameters(model)
                        if device.type == "cuda":
                            torch.cuda.reset_peak_memory_stats(device)
                        started = time.perf_counter()
                        train_model(
                            model=model,
                            mechanism=mechanism,
                            inputs=train_inputs,
                            targets=train_targets,
                            epochs=epochs,
                            batch_size=int(resolved["batch_size"]),
                            learning_rate=learning_rate,
                            order_seed=stable_seed(seed, "minibatch-order"),
                        )
                        runtime = time.perf_counter() - started
                        model.eval()
                        with torch.no_grad():
                            id_metrics = pde_metrics(model(id_inputs), id_targets)
                        case_metrics = {
                            name: evaluate_rollouts(
                                model,
                                initial,
                                truth,
                                [int(value) for value in resolved["horizons"]],
                                projected=False,
                            )
                            for name, initial in cases.items()
                        }
                        peak_memory = (
                            int(torch.cuda.max_memory_allocated(device)) if device.type == "cuda" else None
                        )
                        compute = {
                            "trainable_parameters": parameter_count,
                            "examples_seen": int(resolved["n_train"]) * epochs,
                            "proxy": parameter_count * int(resolved["n_train"]) * epochs,
                            "runtime_seconds": runtime,
                            "peak_gpu_memory_bytes": peak_memory,
                        }
                        record = {
                            **base_identity,
                            "run_id": run_id,
                            "config_id": f"c{capacity}_e{epochs}_lr{learning_rate:g}",
                            "derived_from": None,
                            "compute": compute,
                            "id_metrics": id_metrics,
                            "cases": case_metrics,
                            "provenance": shared_provenance,
                        }
                        if run_id not in completed:
                            append_jsonl(output, record)
                            completed.add(run_id)
                            print(
                                f"completed {run_id} {mechanism} seed={seed} {record['config_id']}",
                                flush=True,
                            )

                        if mechanism == "free" and projection_id not in completed:
                            projected_id = pde_metrics(
                                project_pde_output(id_inputs, model(id_inputs)), id_targets
                            )
                            projected_cases = {
                                name: evaluate_rollouts(
                                    model,
                                    initial,
                                    truth,
                                    [int(value) for value in resolved["horizons"]],
                                    projected=True,
                                )
                                for name, initial in cases.items()
                            }
                            projected_record = {
                                **base_identity,
                                "mechanism": "projection",
                                "run_id": projection_id,
                                "config_id": record["config_id"],
                                "derived_from": run_id,
                                "compute": compute,
                                "id_metrics": projected_id,
                                "cases": projected_cases,
                                "provenance": shared_provenance,
                            }
                            append_jsonl(output, projected_record)
                            completed.add(projection_id)


@hydra.main(version_base=None, config_path="../configs/constraint_iclr", config_name="pde")
def main(cfg: DictConfig) -> None:
    run(cfg)


if __name__ == "__main__":
    main()
