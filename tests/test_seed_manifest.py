"""Tests for explicit rollout-seed manifests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ecomd.inference.seed_manifest import load_seed_file, seeds_for_rank


def test_load_seed_list_and_object(tmp_path: Path) -> None:
    list_path = tmp_path / "list.json"
    list_path.write_text(json.dumps([10, 11, 12]))
    assert load_seed_file(list_path) == [10, 11, 12]

    object_path = tmp_path / "object.json"
    object_path.write_text(json.dumps({"seeds": [20, 21]}))
    assert load_seed_file(object_path) == [20, 21]


def test_seed_partition_preserves_union() -> None:
    seeds = list(range(17))
    shards = [seeds_for_rank(seeds, rank=rank, world_size=4) for rank in range(4)]
    assert sorted(seed for shard in shards for seed in shard) == seeds
    assert shards[0] == [0, 4, 8, 12, 16]


@pytest.mark.parametrize("payload", [[], [1, 1], [1, -2], [1, 2.5], {"wrong": [1]}])
def test_invalid_seed_files_rejected(tmp_path: Path, payload: object) -> None:
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        load_seed_file(path)


def test_invalid_rank_rejected() -> None:
    with pytest.raises(ValueError):
        seeds_for_rank([1, 2], rank=2, world_size=2)
