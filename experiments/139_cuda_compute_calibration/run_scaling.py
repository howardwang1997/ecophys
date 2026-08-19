"""Run the frozen heterogeneous CUDA scaling matrix using the exp128 probe."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import torch
from omegaconf import OmegaConf

ROOT = Path(__file__).resolve().parents[2]


def cells_for_pool(config: Mapping[str, Any], pool: str) -> list[tuple[int, int, int]]:
    """Return deterministic ``(N, repeat, seed)`` cells for one device pool."""

    pools = config.get("pools")
    if not isinstance(pools, Mapping) or pool not in pools or not isinstance(pools[pool], Mapping):
        raise ValueError(f"unknown CUDA pool: {pool}")
    pool_config = pools[pool]
    sizes = pool_config.get("n_agents")
    repeats = pool_config.get("repeats")
    seed_root = config.get("seed_root")
    if not isinstance(sizes, list) or not all(isinstance(value, int) and value > 0 for value in sizes):
        raise ValueError("n_agents must be a positive integer list")
    if not isinstance(repeats, int) or repeats <= 0 or not isinstance(seed_root, int):
        raise ValueError("repeats and seed_root must be positive integers")
    return [
        (size, repeat, seed_root + 10_000 * index + repeat)
        for index, size in enumerate(sizes)
        for repeat in range(repeats)
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--pool", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--git-sha", required=True)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required")

    raw_config = OmegaConf.to_container(OmegaConf.load(args.config), resolve=True)
    if not isinstance(raw_config, dict):
        raise ValueError("configuration must be a mapping")
    cells = cells_for_pool(raw_config, args.pool)
    probe_script = ROOT / str(raw_config["probe_script"])
    if not probe_script.is_file():
        raise FileNotFoundError(probe_script)
    args.work_root.mkdir(parents=True, exist_ok=True)
    device = torch.cuda.current_device()
    device_properties = torch.cuda.get_device_properties(device)
    total_memory = int(device_properties.total_memory)
    maximum_fraction = float(raw_config["maximum_reserved_memory_fraction"])

    cell_results: list[dict[str, Any]] = []
    started = time.perf_counter()
    for n_agents, repeat, seed in cells:
        cell_out = args.work_root / f"n{n_agents}_repeat{repeat}.json"
        command = [
            sys.executable,
            str(probe_script),
            "--out",
            str(cell_out),
            "--n-agents",
            str(n_agents),
            "--parity-steps",
            str(raw_config["parity_steps"]),
            "--long-steps",
            str(raw_config["long_steps"]),
            "--seed",
            str(seed),
            "--dt",
            str(raw_config["dt"]),
            "--parity-atol",
            str(raw_config["parity_atol"]),
            "--git-sha",
            args.git_sha,
        ]
        completed = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
        if completed.returncode != 0:
            raise RuntimeError(
                f"probe failed for N={n_agents}, repeat={repeat}: {completed.stderr[-2000:]}"
            )
        result = json.loads(cell_out.read_text())
        reserved_fraction = float(result["peak_reserved_bytes"]) / total_memory
        result["calibration_cell"] = {
            "n_agents": n_agents,
            "repeat": repeat,
            "seed": seed,
            "reserved_memory_fraction": reserved_fraction,
            "memory_gate_pass": reserved_fraction < maximum_fraction,
        }
        cell_results.append(result)

    checks = {
        "declared_matrix_complete": len(cell_results) == len(cells),
        "all_mechanics_checks_pass": all(bool(item["all_checks_pass"]) for item in cell_results),
        "all_memory_gates_pass": all(
            bool(item["calibration_cell"]["memory_gate_pass"]) for item in cell_results
        ),
    }
    payload = {
        "experiment": raw_config["experiment"],
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_sha": args.git_sha,
        "pool": args.pool,
        "platform": platform.platform(),
        "python": sys.version,
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(device),
        "device_total_memory_bytes": total_memory,
        "wall_seconds": time.perf_counter() - started,
        "cells": cell_results,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": "compute calibration only; no scientific gate upgraded",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: payload[key] for key in ("pool", "checks", "wall_seconds")}, indent=2))


if __name__ == "__main__":
    main()
