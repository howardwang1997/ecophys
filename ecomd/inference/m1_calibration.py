"""Frozen calibration-only rollout launcher for EcoMD v1 M1."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml

from ..data.yfinance_provenance import repository_state, sha256_file
from ..eval.m1_contract import load_and_validate_m1_protocol
from ..models.ecomd import EcoMDConfig, EcoMDSimulator
from ..training.m0_contract import validate_m0_config
from . import run_large
from .seed_manifest import load_seed_file


@dataclass(frozen=True)
class CalibrationPreflight:
    binding: dict[str, Any]
    checkpoint: dict[str, Any]
    seeds: tuple[int, ...]
    seeds_path: Path
    config_path: Path
    repository: dict[str, Any]


def _mapping(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"missing mapping: {key}")
    return value


def _git_object(repo_root: Path, revision_and_path: str) -> str:
    return subprocess.run(
        ["git", "rev-parse", revision_and_path],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def preflight_calibration(
    *,
    binding_path: Path,
    checkpoint_path: Path,
    node: str,
    repo_root: Path,
) -> CalibrationPreflight:
    """Validate the calibration-only source, checkpoint and node-seed binding."""
    loaded = yaml.safe_load(binding_path.read_text())
    if not isinstance(loaded, dict):
        raise ValueError("calibration binding must be a YAML mapping")
    binding: dict[str, Any] = loaded
    contract = _mapping(binding, "contract")
    training = _mapping(binding, "training")
    implementation = _mapping(binding, "implementation")
    rollout = _mapping(binding, "rollout")
    if contract != {
        "name": "ecomd_v1_m1_calibration_only",
        "version": 1,
        "status": "frozen_before_calibration_rollouts",
        "freeze_commit_rule": "first_git_commit_containing_this_file",
        "heldout_locked": True,
    }:
        raise ValueError("calibration contract is not the frozen held-out-locked v1")
    if node not in {"v100_a", "v100_b"}:
        raise ValueError(f"unsupported calibration node: {node}")

    repository = repository_state(repo_root)
    if not repository["clean"]:
        raise RuntimeError("formal calibration requires a clean worktree")
    config_path = repo_root / str(training["config_path"])
    protocol_path = repo_root / str(training["protocol_path"])
    if sha256_file(config_path) != training["config_sha256"]:
        raise ValueError("calibration M0 config hash mismatch")
    if sha256_file(protocol_path) != training["protocol_sha256"]:
        raise ValueError("calibration M1 protocol hash mismatch")
    config = yaml.safe_load(config_path.read_text())
    if not isinstance(config, dict):
        raise ValueError("M0 config must be a mapping")
    validate_m0_config(config)
    protocol = load_and_validate_m1_protocol(protocol_path, repo_root)

    if _git_object(repo_root, "HEAD:ecomd/models") != implementation["model_tree_git_oid"]:
        raise ValueError("current model tree differs from the frozen training implementation")
    if _git_object(repo_root, "HEAD:ecomd/physics") != implementation["physics_tree_git_oid"]:
        raise ValueError("current physics tree differs from the frozen training implementation")
    source_hashes = {
        "stylized_facts_sha256": sha256_file(repo_root / "ecomd/eval/stylized_facts.py"),
        "run_large_sha256": sha256_file(repo_root / "ecomd/inference/run_large.py"),
        "seed_manifest_sha256": sha256_file(repo_root / "ecomd/inference/seed_manifest.py"),
    }
    if source_hashes != implementation:
        comparable = {key: implementation[key] for key in source_hashes}
        if source_hashes != comparable:
            raise ValueError("calibration inference/scoring implementation hash mismatch")

    if sha256_file(checkpoint_path) != training["checkpoint_sha256"]:
        raise ValueError("calibration checkpoint hash mismatch")
    checkpoint_loaded = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    if not isinstance(checkpoint_loaded, dict):
        raise ValueError("checkpoint must contain a mapping")
    checkpoint: dict[str, Any] = checkpoint_loaded
    _validate_checkpoint(checkpoint, training, config)

    calibration = _mapping(rollout, "calibration")
    node_record = _mapping(calibration, node)
    seeds_path = repo_root / str(node_record["seeds_path"])
    if sha256_file(seeds_path) != node_record["seeds_sha256"]:
        raise ValueError("calibration seed-file hash mismatch")
    seeds = tuple(load_seed_file(seeds_path))
    protocol_nodes = protocol["rollout"]["node_shards"]
    expected_seeds = tuple(int(seed) for seed in protocol_nodes[node]["calibration"])
    if seeds != expected_seeds:
        raise ValueError("calibration seed file differs from the frozen protocol node shard")
    if rollout.get("simulator_steps") != 8001:
        raise ValueError("calibration simulator_steps changed")
    if rollout.get("expected_recorded_returns") != 8000:
        raise ValueError("calibration return count changed")
    if rollout.get("save_trajectory") is not True:
        raise ValueError("calibration must save trajectories")
    if rollout.get("shocks_or_overrides") != "forbidden":
        raise ValueError("calibration shocks/overrides must be forbidden")

    simulator = EcoMDSimulator(EcoMDConfig(**dict(config["simulator"])))
    if sum(parameter.numel() for parameter in simulator.parameters()) != int(training["parameter_count"]):
        raise ValueError("calibration model parameter count mismatch")
    return CalibrationPreflight(
        binding=binding,
        checkpoint=checkpoint,
        seeds=seeds,
        seeds_path=seeds_path,
        config_path=config_path,
        repository=repository,
    )


def _validate_checkpoint(
    checkpoint: dict[str, Any],
    training: dict[str, Any],
    config: dict[str, Any],
) -> None:
    if int(checkpoint.get("format_version", -1)) != 2:
        raise ValueError("calibration requires checkpoint format 2")
    if int(checkpoint.get("iter_idx", -1)) != int(training["checkpoint_iter"]):
        raise ValueError("calibration checkpoint iteration mismatch")
    if checkpoint.get("state_complete") is not True or int(checkpoint.get("world_size", -1)) != 1:
        raise ValueError("calibration checkpoint is not single-rank state-complete")
    if checkpoint.get("sim_config") != config["simulator"]:
        raise ValueError("checkpoint simulator config mismatch")
    if checkpoint.get("train_config") != config["training"]:
        raise ValueError("checkpoint training config mismatch")
    metadata = checkpoint.get("execution_metadata")
    if not isinstance(metadata, dict):
        raise ValueError("checkpoint lacks execution metadata")
    expected_metadata = {
        "git_sha": training["git_sha"],
        "m0_config_sha256": training["config_sha256"],
        "m1_protocol_sha256": training["protocol_sha256"],
        "data_manifest_sha256": training["data_manifest_sha256"],
        "train_return_float64_le_sha256": training["train_return_float64_le_sha256"],
        "train_return_rows": training["train_return_rows"],
    }
    for key, expected in expected_metadata.items():
        if metadata.get(key) != expected:
            raise ValueError(f"checkpoint execution metadata mismatch: {key}")
    runtimes = checkpoint.get("rank_runtimes")
    if not isinstance(runtimes, list) or len(runtimes) != 1:
        raise ValueError("checkpoint lacks its single rank runtime")
    history = runtimes[0].get("history")
    if not isinstance(history, list) or len(history) != int(training["checkpoint_iter"]):
        raise ValueError("checkpoint history length mismatch")
    numeric_keys = ("total_rank0", "total_world_mean", "acf_sim", "leverage_sim", "hill_sim", "grad_norm")
    if not all(
        math.isfinite(float(row[key]))
        for row in history
        for key in numeric_keys
    ):
        raise ValueError("checkpoint history contains non-finite values")
    if not all(float(row["grad_norm"]) > 0.0 for row in history):
        raise ValueError("checkpoint history contains a zero gradient row")


def run_calibration_shard(
    *,
    binding_path: Path,
    checkpoint_path: Path,
    node: str,
    out_dir: Path,
    repo_root: Path,
) -> dict[str, Any]:
    preflight = preflight_calibration(
        binding_path=binding_path,
        checkpoint_path=checkpoint_path,
        node=node,
        repo_root=repo_root,
    )
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"calibration output directory is not empty: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)
    rollout = _mapping(preflight.binding, "rollout")
    original_argv = sys.argv
    try:
        sys.argv = [
            "ecomd.inference.run_large",
            "--ckpt",
            str(checkpoint_path),
            "--config",
            str(preflight.config_path),
            "--n-steps",
            str(rollout["simulator_steps"]),
            "--seeds-file",
            str(preflight.seeds_path),
            "--expected-recorded-returns",
            str(rollout["expected_recorded_returns"]),
            "--out-dir",
            str(out_dir),
            "--save-trajectory",
        ]
        run_large.main()
    finally:
        sys.argv = original_argv

    trajectory_records: list[dict[str, Any]] = []
    for seed in preflight.seeds:
        path = out_dir / f"trajectory_seed{seed}.npz"
        with np.load(path, allow_pickle=False) as payload:
            observed_seed = int(payload["seed"])
            observed_count = int(payload["n_recorded_returns"])
            returns = np.asarray(payload["log_returns"], dtype=np.float64)
        if observed_seed != seed or observed_count != 8000 or returns.shape != (8000,):
            raise RuntimeError(f"calibration trajectory schema mismatch for seed {seed}")
        if not np.all(np.isfinite(returns)):
            raise RuntimeError(f"calibration trajectory is non-finite for seed {seed}")
        trajectory_records.append(
            {"seed": seed, "sha256": sha256_file(path), "bytes": path.stat().st_size}
        )
    merged_path = out_dir / "inference_merged.json"
    merged_loaded = json.loads(merged_path.read_text())
    if not isinstance(merged_loaded, dict) or int(merged_loaded.get("n_total_rollouts", -1)) != len(preflight.seeds):
        raise RuntimeError("calibration merged result count mismatch")
    report = {
        "schema_version": 1,
        "status": "calibration_shard_complete_heldout_still_locked",
        "node": node,
        "repository": preflight.repository,
        "binding_sha256": sha256_file(binding_path),
        "checkpoint_sha256": sha256_file(checkpoint_path),
        "seeds": list(preflight.seeds),
        "trajectory_records": trajectory_records,
        "inference_rank_0_sha256": sha256_file(out_dir / "inference_rank_0.json"),
        "inference_merged_sha256": sha256_file(merged_path),
        "manifest_contains_trajectory_values": False,
    }
    report_path = out_dir / "calibration_shard_manifest.json"
    temporary = report_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    temporary.replace(report_path)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binding", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--node", choices=("v100_a", "v100_b"), required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    report = run_calibration_shard(
        binding_path=args.binding.resolve(),
        checkpoint_path=args.checkpoint.resolve(),
        node=args.node,
        out_dir=args.out_dir.resolve(),
        repo_root=repo_root,
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["CalibrationPreflight", "preflight_calibration", "run_calibration_shard"]
