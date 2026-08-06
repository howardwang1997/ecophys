"""Explicit rollout-seed loading and rank-stable partitioning."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any


def load_seed_file(path: str | Path) -> list[int]:
    source = Path(path)
    payload: Any = json.loads(source.read_text())
    if isinstance(payload, dict):
        payload = payload.get("seeds")
    if not isinstance(payload, list):
        raise ValueError("seed file must be a JSON list or an object containing a 'seeds' list")
    seeds: list[int] = []
    for value in payload:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"every seed must be an integer, got {value!r}")
        if value < 0:
            raise ValueError(f"seeds must be non-negative, got {value}")
        seeds.append(value)
    if not seeds:
        raise ValueError("seed file is empty")
    if len(set(seeds)) != len(seeds):
        raise ValueError("seed file contains duplicate seeds")
    return seeds


def seeds_for_rank(seeds: Sequence[int], rank: int, world_size: int) -> list[int]:
    if world_size < 1:
        raise ValueError("world_size must be positive")
    if not 0 <= rank < world_size:
        raise ValueError(f"rank {rank} is outside [0, {world_size})")
    return [int(seed) for seed in seeds[rank::world_size]]
