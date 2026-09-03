"""Shared utilities for the frozen 2026-08-30 ICLR constraint audit."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np
import torch

SCHEMA_VERSION = "constraint-iclr-v1"


def stable_seed(seed: int, namespace: str) -> int:
    """Derive a stable 31-bit seed without coupling data to model hyperparameters."""
    digest = hashlib.sha256(f"{seed}:{namespace}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % (2**31 - 1)


def seed_everything(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_selection_lock(root: Path, resolved_config: Mapping[str, Any]) -> Path | None:
    """Bind every confirmation record to the exact frozen pilot-selection lock."""
    if str(resolved_config.get("stage")) != "confirmation":
        return None
    raw_path = resolved_config.get("selection_lock_path")
    expected = resolved_config.get("selection_lock_sha256")
    if not raw_path or not expected:
        raise RuntimeError("confirmation requires selection_lock_path and selection_lock_sha256")
    path = Path(str(raw_path))
    if not path.is_absolute():
        path = root / path
    if not path.is_file():
        raise RuntimeError(f"selection lock does not exist: {path}")
    actual = sha256_file(path)
    if actual != str(expected):
        raise RuntimeError(f"selection lock SHA-256 mismatch: expected {expected}, got {actual}")
    return path


def _git_output(root: Path, args: Sequence[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def provenance(
    *,
    root: Path,
    resolved_config: Mapping[str, Any],
    source_files: Iterable[Path],
) -> dict[str, Any]:
    """Capture executable identity, environment, and the fully resolved configuration."""
    head = os.environ.get("ECOPHYS_GIT_HEAD") or _git_output(root, ["rev-parse", "HEAD"])
    if not head:
        raise RuntimeError(
            "git HEAD is unavailable; set ECOPHYS_GIT_HEAD explicitly before remote execution"
        )
    dirty_env = os.environ.get("ECOPHYS_DIRTY")
    if dirty_env is None:
        status = _git_output(root, ["status", "--porcelain", "--untracked-files=normal"])
        if status is None:
            raise RuntimeError(
                "git dirty state is unavailable; set ECOPHYS_DIRTY explicitly before remote execution"
            )
        dirty = bool(status)
    else:
        dirty = dirty_env.lower() not in {"0", "false", "no"}
    hashes: dict[str, str] = {}
    for raw_path in source_files:
        path = raw_path if raw_path.is_absolute() else root / raw_path
        if path.exists():
            try:
                label = str(path.relative_to(root))
            except ValueError:
                label = str(path)
            hashes[label] = sha256_file(path)

    gpu: dict[str, Any] | None = None
    if torch.cuda.is_available():
        index = torch.cuda.current_device()
        props = torch.cuda.get_device_properties(index)
        gpu = {
            "index": index,
            "name": props.name,
            "total_memory_bytes": props.total_memory,
            "capability": [int(props.major), int(props.minor)],
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "git_head": head,
        "git_dirty": dirty,
        "source_sha256": hashes,
        "command": [sys.executable, *sys.argv],
        "resolved_config": dict(resolved_config),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "torch": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "gpu": gpu,
        "wandb_url": None,
    }


def canonical_run_id(identity: Mapping[str, Any]) -> str:
    payload = json.dumps(identity, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:20]


def append_jsonl(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, default=str, allow_nan=False))
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def count_trainable_parameters(model: torch.nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)


def pde_metrics(prediction: torch.Tensor, target: torch.Tensor) -> dict[str, float]:
    error = prediction - target
    spatial_dims = tuple(range(1, error.ndim))
    drift = error.mean(dim=spatial_dims, keepdim=True)
    conserving = error - drift
    return {
        "total_rmse": float(error.square().mean().sqrt().detach().cpu()),
        "invariant_drift": float(drift.abs().mean().detach().cpu()),
        "conserving_rmse": float(conserving.square().mean().sqrt().detach().cpu()),
    }


def project_pde_output(inputs: torch.Tensor, outputs: torch.Tensor) -> torch.Tensor:
    spatial_dims = tuple(range(1, outputs.ndim))
    return (
        outputs + inputs.mean(dim=spatial_dims, keepdim=True) - outputs.mean(dim=spatial_dims, keepdim=True)
    )


def bootstrap_mean_ci(
    differences: np.ndarray,
    *,
    confidence: float,
    draws: int = 50_000,
    seed: int = 20_260_830,
) -> tuple[float, float]:
    values = np.asarray(differences, dtype=np.float64)
    if values.ndim != 1 or values.size < 2 or not np.isfinite(values).all():
        raise ValueError("paired bootstrap requires at least two finite seed differences")
    rng = np.random.default_rng(seed)
    sampled = rng.choice(values, size=(draws, values.size), replace=True).mean(axis=1)
    tail = (1.0 - confidence) / 2.0
    low, high = np.quantile(sampled, [tail, 1.0 - tail])
    return float(low), float(high)


def holm_adjust(p_values: Sequence[float]) -> list[float]:
    """Return Holm-adjusted p-values in the original order."""
    count = len(p_values)
    order = sorted(range(count), key=lambda idx: p_values[idx])
    adjusted = [0.0] * count
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (count - rank) * float(p_values[idx]))
        adjusted[idx] = min(1.0, running)
    return adjusted
