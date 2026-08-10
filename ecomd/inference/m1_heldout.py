"""Gate-bound held-out rollout launcher for EcoMD v1 M1."""

from __future__ import annotations

import argparse
import json
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
from .m1_calibration import _git_object, _mapping, _validate_checkpoint
from .seed_manifest import load_seed_file


@dataclass(frozen=True)
class HeldoutPreflight:
    binding: dict[str, Any]
    checkpoint: dict[str, Any]
    gate: dict[str, Any]
    seeds: tuple[int, ...]
    seeds_path: Path
    config_path: Path
    repository: dict[str, Any]
    binding_freeze_git_sha: str


def validate_frozen_gate(gate: dict[str, Any], expected: dict[str, Any]) -> None:
    """Reject any gate other than the exact calibration-only frozen result."""
    required = {
        "status": "calibration_gate_frozen_before_heldout",
        "calibration_execution_git_sha": expected["calibration_execution_git_sha"],
        "calibration_input_float64_le_sha256": expected[
            "calibration_input_float64_le_sha256"
        ],
        "n_calibration_trajectories": 16,
        "returns_per_trajectory": 8000,
        "heldout_trajectory_count_at_fit": expected["heldout_trajectory_count_at_fit"],
        "binding_sha256": expected["calibration_binding_sha256"],
        "checkpoint_sha256": expected["checkpoint_sha256"],
        "protocol_sha256": expected["protocol_sha256"],
    }
    for key, value in required.items():
        if gate.get(key) != value:
            raise ValueError(f"frozen gate mismatch: {key}")
    repository = gate.get("repository")
    if not isinstance(repository, dict):
        raise ValueError("frozen gate lacks fitting repository metadata")
    if repository.get("git_sha") != expected["fit_repository_git_sha"]:
        raise ValueError("frozen gate fitting Git SHA mismatch")
    if repository.get("clean") is not True:
        raise ValueError("frozen gate was not fitted from a clean repository")
    energy = gate.get("energy_gate")
    if not isinstance(energy, dict):
        raise ValueError("frozen gate lacks the energy fit")
    if energy.get("w_star") != expected["frozen_w_star"]:
        raise ValueError("frozen W-star mismatch")
    if energy.get("n_calibration_trajectories") != 16:
        raise ValueError("frozen gate calibration count mismatch")
    if gate.get("record_contains_trajectory_values") is not False:
        raise ValueError("frozen gate trajectory-value disclosure flag changed")


def preflight_heldout(
    *,
    binding_path: Path,
    checkpoint_path: Path,
    node: str,
    repo_root: Path,
) -> HeldoutPreflight:
    """Validate the committed gate, source, checkpoint and held-out node seeds."""
    loaded = yaml.safe_load(binding_path.read_text())
    if not isinstance(loaded, dict):
        raise ValueError("held-out binding must be a YAML mapping")
    binding: dict[str, Any] = loaded
    contract = _mapping(binding, "contract")
    if contract != {
        "name": "ecomd_v1_m1_heldout",
        "version": 1,
        "status": "frozen_after_calibration_gate_before_heldout",
        "freeze_commit_rule": "first_git_commit_containing_this_file",
        "gate_committed_before_heldout": True,
        "result_selection_forbidden": True,
    }:
        raise ValueError("held-out contract is not the frozen v1")
    if node not in {"v100_a", "v100_b"}:
        raise ValueError(f"unsupported held-out node: {node}")

    repository = repository_state(repo_root)
    if not repository["clean"]:
        raise RuntimeError("formal held-out rollout requires a clean worktree")
    binding_freeze_git_sha = binding_freeze_commit(binding_path, repo_root)
    training = _mapping(binding, "training")
    config_path = repo_root / str(training["config_path"])
    protocol_path = repo_root / str(training["protocol_path"])
    if sha256_file(config_path) != training["config_sha256"]:
        raise ValueError("held-out M0 config hash mismatch")
    if sha256_file(protocol_path) != training["protocol_sha256"]:
        raise ValueError("held-out M1 protocol hash mismatch")
    config_loaded = yaml.safe_load(config_path.read_text())
    if not isinstance(config_loaded, dict):
        raise ValueError("M0 config must be a mapping")
    config: dict[str, Any] = config_loaded
    validate_m0_config(config)
    protocol = load_and_validate_m1_protocol(protocol_path, repo_root)

    gate_binding = _mapping(binding, "gate")
    gate_path = repo_root / str(gate_binding["path"])
    if sha256_file(gate_path) != gate_binding["sha256"]:
        raise ValueError("held-out frozen-gate file hash mismatch")
    gate_commit = str(gate_binding["commit_sha"])
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", gate_commit, "HEAD"],
        cwd=repo_root,
        check=False,
    )
    if ancestor.returncode != 0:
        raise ValueError("frozen gate commit is not an ancestor of held-out execution")
    gate_relative_path = str(gate_binding["path"])
    if _git_object(repo_root, f"HEAD:{gate_relative_path}") != _git_object(
        repo_root, f"{gate_commit}:{gate_relative_path}"
    ):
        raise ValueError("held-out gate blob differs from its committed freeze")
    gate_loaded = json.loads(gate_path.read_text())
    if not isinstance(gate_loaded, dict):
        raise ValueError("frozen gate must contain a JSON object")
    gate: dict[str, Any] = gate_loaded
    validate_frozen_gate(
        gate,
        {
            **gate_binding,
            "checkpoint_sha256": training["checkpoint_sha256"],
            "protocol_sha256": training["protocol_sha256"],
        },
    )

    implementation = _mapping(binding, "implementation")
    if _git_object(repo_root, "HEAD:ecomd/models") != implementation["model_tree_git_oid"]:
        raise ValueError("current model tree differs from the frozen training implementation")
    if _git_object(repo_root, "HEAD:ecomd/physics") != implementation["physics_tree_git_oid"]:
        raise ValueError("current physics tree differs from the frozen training implementation")
    source_hashes = {
        "stylized_facts_sha256": sha256_file(repo_root / "ecomd/eval/stylized_facts.py"),
        "canonical_bands_sha256": sha256_file(repo_root / "ecomd/eval/canonical_bands.py"),
        "stationarity_gate_sha256": sha256_file(repo_root / "ecomd/eval/stationarity_gate.py"),
        "run_large_sha256": sha256_file(repo_root / "ecomd/inference/run_large.py"),
        "seed_manifest_sha256": sha256_file(repo_root / "ecomd/inference/seed_manifest.py"),
        "heldout_analysis_sha256": sha256_file(repo_root / "ecomd/eval/m1_heldout_analysis.py"),
    }
    expected_source_hashes = {key: implementation[key] for key in source_hashes}
    if source_hashes != expected_source_hashes:
        raise ValueError("held-out inference/scoring implementation hash mismatch")

    if sha256_file(checkpoint_path) != training["checkpoint_sha256"]:
        raise ValueError("held-out checkpoint hash mismatch")
    checkpoint_loaded = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    if not isinstance(checkpoint_loaded, dict):
        raise ValueError("checkpoint must contain a mapping")
    checkpoint: dict[str, Any] = checkpoint_loaded
    _validate_checkpoint(checkpoint, training, config)

    rollout = _mapping(binding, "rollout")
    heldout = _mapping(rollout, "heldout")
    node_record = _mapping(heldout, node)
    seeds_path = repo_root / str(node_record["seeds_path"])
    if sha256_file(seeds_path) != node_record["seeds_sha256"]:
        raise ValueError("held-out seed-file hash mismatch")
    seeds = tuple(load_seed_file(seeds_path))
    expected_seeds = tuple(
        int(seed) for seed in protocol["rollout"]["node_shards"][node]["heldout"]
    )
    if seeds != expected_seeds:
        raise ValueError("held-out seed file differs from the frozen protocol node shard")
    if rollout.get("simulator_steps") != 8001:
        raise ValueError("held-out simulator_steps changed")
    if rollout.get("expected_recorded_returns") != 8000:
        raise ValueError("held-out return count changed")
    if rollout.get("save_trajectory") is not True:
        raise ValueError("held-out must save trajectories")
    if rollout.get("shocks_or_overrides") != "forbidden":
        raise ValueError("held-out shocks/overrides must be forbidden")

    simulator = EcoMDSimulator(EcoMDConfig(**dict(config["simulator"])))
    if sum(parameter.numel() for parameter in simulator.parameters()) != int(
        training["parameter_count"]
    ):
        raise ValueError("held-out model parameter count mismatch")
    return HeldoutPreflight(
        binding=binding,
        checkpoint=checkpoint,
        gate=gate,
        seeds=seeds,
        seeds_path=seeds_path,
        config_path=config_path,
        repository=repository,
        binding_freeze_git_sha=binding_freeze_git_sha,
    )


def run_heldout_shard(
    *,
    binding_path: Path,
    checkpoint_path: Path,
    node: str,
    out_dir: Path,
    repo_root: Path,
) -> dict[str, Any]:
    preflight = preflight_heldout(
        binding_path=binding_path,
        checkpoint_path=checkpoint_path,
        node=node,
        repo_root=repo_root,
    )
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"held-out output directory is not empty: {out_dir}")
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
            volumes = np.asarray(payload["volumes"], dtype=np.float64)
        if (
            observed_seed != seed
            or observed_count != 8000
            or returns.shape != (8000,)
            or volumes.shape != (8000,)
        ):
            raise RuntimeError(f"held-out trajectory schema mismatch for seed {seed}")
        if not np.all(np.isfinite(returns)) or not np.all(np.isfinite(volumes)):
            raise RuntimeError(f"held-out trajectory is non-finite for seed {seed}")
        trajectory_records.append(
            {"seed": seed, "sha256": sha256_file(path), "bytes": path.stat().st_size}
        )
    merged_path = out_dir / "inference_merged.json"
    merged_loaded = json.loads(merged_path.read_text())
    if not isinstance(merged_loaded, dict) or int(
        merged_loaded.get("n_total_rollouts", -1)
    ) != len(preflight.seeds):
        raise RuntimeError("held-out merged result count mismatch")
    gate_binding = _mapping(preflight.binding, "gate")
    report = {
        "schema_version": 1,
        "status": "heldout_shard_complete_under_frozen_gate",
        "node": node,
        "repository": preflight.repository,
        "binding_freeze_git_sha": preflight.binding_freeze_git_sha,
        "binding_sha256": sha256_file(binding_path),
        "checkpoint_sha256": sha256_file(checkpoint_path),
        "gate_sha256": gate_binding["sha256"],
        "frozen_w_star": gate_binding["frozen_w_star"],
        "seeds": list(preflight.seeds),
        "trajectory_records": trajectory_records,
        "inference_rank_0_sha256": sha256_file(out_dir / "inference_rank_0.json"),
        "inference_merged_sha256": sha256_file(merged_path),
        "manifest_contains_trajectory_values": False,
    }
    report_path = out_dir / "heldout_shard_manifest.json"
    temporary = report_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    temporary.replace(report_path)
    return report


def binding_freeze_commit(binding_path: Path, repo_root: Path) -> str:
    """Return the sole add commit after verifying the binding blob never changed."""
    relative_path = str(binding_path.resolve().relative_to(repo_root.resolve()))
    completed = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%H", "--", relative_path],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    commits = completed.stdout.splitlines()
    if len(commits) != 1:
        raise ValueError("held-out binding must have exactly one Git add commit")
    freeze_commit = commits[0]
    if _git_object(repo_root, f"HEAD:{relative_path}") != _git_object(
        repo_root, f"{freeze_commit}:{relative_path}"
    ):
        raise ValueError("held-out binding differs from its first committed freeze")
    return freeze_commit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binding", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--node", choices=("v100_a", "v100_b"), required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    report = run_heldout_shard(
        binding_path=args.binding.resolve(),
        checkpoint_path=args.checkpoint.resolve(),
        node=args.node,
        out_dir=args.out_dir.resolve(),
        repo_root=repo_root,
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
