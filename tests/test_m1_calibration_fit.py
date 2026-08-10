from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from ecomd.data.yfinance_provenance import sha256_file
from ecomd.eval.m1_calibration_fit import (
    collect_calibration_shard,
    load_calibration_trajectory,
)


def _write_shard(root: Path, *, seed: int = 811000) -> tuple[str, str]:
    root.mkdir()
    trajectory_path = root / f"trajectory_seed{seed}.npz"
    np.savez_compressed(
        trajectory_path,
        seed=seed,
        n_steps=8001,
        n_recorded_returns=8000,
        log_returns=np.linspace(-0.1, 0.1, 8000),
    )
    realization = {
        "rank": 0,
        "seed": seed,
        "n_steps": 8001,
        "n_recorded_returns": 8000,
    }
    rank_path = root / "inference_rank_0.json"
    merged_path = root / "inference_merged.json"
    rank_path.write_text(json.dumps([realization]))
    merged_path.write_text(json.dumps({
        "n_total_rollouts": 1,
        "realizations": [realization],
    }))
    binding_sha = "a" * 64
    checkpoint_sha = "b" * 64
    manifest = {
        "schema_version": 1,
        "status": "calibration_shard_complete_heldout_still_locked",
        "node": "v100_a",
        "repository": {"git_sha": "c" * 40, "clean": True, "status_entries": []},
        "binding_sha256": binding_sha,
        "checkpoint_sha256": checkpoint_sha,
        "seeds": [seed],
        "trajectory_records": [{
            "seed": seed,
            "sha256": sha256_file(trajectory_path),
            "bytes": trajectory_path.stat().st_size,
        }],
        "inference_rank_0_sha256": sha256_file(rank_path),
        "inference_merged_sha256": sha256_file(merged_path),
        "manifest_contains_trajectory_values": False,
    }
    (root / "calibration_shard_manifest.json").write_text(json.dumps(manifest))
    return binding_sha, checkpoint_sha


def test_load_calibration_trajectory_rejects_wrong_shape(tmp_path: Path) -> None:
    path = tmp_path / "trajectory_seed7.npz"
    np.savez(path, seed=7, n_steps=8001, n_recorded_returns=7999,
             log_returns=np.ones(7999))
    with pytest.raises(ValueError, match="schema mismatch"):
        load_calibration_trajectory(path, 7)


def test_collect_calibration_shard_validates_hashes_and_metadata(tmp_path: Path) -> None:
    shard = tmp_path / "v100_a"
    binding_sha, checkpoint_sha = _write_shard(shard)
    matrix, provenance = collect_calibration_shard(
        shard,
        node="v100_a",
        expected_seeds=[811000],
        binding_sha256=binding_sha,
        checkpoint_sha256=checkpoint_sha,
    )
    assert matrix.shape == (1, 8000)
    assert provenance["execution_git_sha"] == "c" * 40
    assert provenance["trajectory_records"][0]["seed"] == 811000


def test_collect_calibration_shard_rejects_manifest_hash_mutation(tmp_path: Path) -> None:
    shard = tmp_path / "v100_a"
    binding_sha, checkpoint_sha = _write_shard(shard)
    manifest_path = shard / "calibration_shard_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["trajectory_records"][0]["sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="hash/size mismatch"):
        collect_calibration_shard(
            shard,
            node="v100_a",
            expected_seeds=[811000],
            binding_sha256=binding_sha,
            checkpoint_sha256=checkpoint_sha,
        )
