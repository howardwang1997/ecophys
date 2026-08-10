"""Fit and freeze the EcoMD v1 M1 gate from calibration trajectories only."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, TypeAlias

import numpy as np
import numpy.typing as npt
import yaml

from ..data.yfinance_provenance import (
    repository_state,
    sha256_file,
    sha256_float64,
)
from .m1_contract import load_and_validate_m1_protocol
from .stationarity_baselines import ADFKPSSConfig, fit_adf_kpss_gate
from .stationarity_gate import GateConfig, fit_stationarity_gate

ArrayF: TypeAlias = npt.NDArray[np.float64]


def load_calibration_trajectory(path: Path, expected_seed: int) -> ArrayF:
    """Load one exact 8,000-return calibration trajectory."""
    with np.load(path, allow_pickle=False) as payload:
        seed = int(payload["seed"])
        n_steps = int(payload["n_steps"])
        n_recorded = int(payload["n_recorded_returns"])
        returns = np.asarray(payload["log_returns"], dtype=np.float64)
    if seed != expected_seed:
        raise ValueError(f"trajectory seed mismatch in {path}: {seed} != {expected_seed}")
    if n_steps != 8001 or n_recorded != 8000 or returns.shape != (8000,):
        raise ValueError(
            f"trajectory schema mismatch in {path}: "
            f"n_steps={n_steps}, n_recorded={n_recorded}, shape={returns.shape}"
        )
    if not np.all(np.isfinite(returns)):
        raise ValueError(f"trajectory contains non-finite returns: {path}")
    return returns


def collect_calibration_shard(
    shard_dir: Path,
    *,
    node: str,
    expected_seeds: Sequence[int],
    binding_sha256: str,
    checkpoint_sha256: str,
) -> tuple[ArrayF, dict[str, Any]]:
    """Verify a calibration shard manifest and return its ordered trajectories."""
    manifest_path = shard_dir / "calibration_shard_manifest.json"
    manifest = _json_object(manifest_path)
    expected_seed_list = [int(seed) for seed in expected_seeds]
    if manifest.get("schema_version") != 1:
        raise ValueError(f"unsupported calibration manifest version for {node}")
    if manifest.get("status") != "calibration_shard_complete_heldout_still_locked":
        raise ValueError(f"calibration shard is not complete for {node}")
    if manifest.get("node") != node:
        raise ValueError(f"calibration node mismatch for {node}")
    repository = manifest.get("repository")
    if not isinstance(repository, dict) or repository.get("clean") is not True:
        raise ValueError(f"calibration execution repository was not clean for {node}")
    if not isinstance(repository.get("git_sha"), str):
        raise ValueError(f"calibration execution Git SHA is missing for {node}")
    if manifest.get("binding_sha256") != binding_sha256:
        raise ValueError(f"calibration binding hash mismatch for {node}")
    if manifest.get("checkpoint_sha256") != checkpoint_sha256:
        raise ValueError(f"calibration checkpoint hash mismatch for {node}")
    if manifest.get("seeds") != expected_seed_list:
        raise ValueError(f"calibration seed order mismatch for {node}")
    if manifest.get("manifest_contains_trajectory_values") is not False:
        raise ValueError(f"calibration manifest value-disclosure flag changed for {node}")

    records = manifest.get("trajectory_records")
    if not isinstance(records, list) or len(records) != len(expected_seed_list):
        raise ValueError(f"calibration trajectory record count mismatch for {node}")
    record_by_seed: dict[int, dict[str, Any]] = {}
    for untyped_record in records:
        if not isinstance(untyped_record, dict):
            raise ValueError(f"invalid calibration trajectory record for {node}")
        seed = int(untyped_record.get("seed", -1))
        if seed in record_by_seed:
            raise ValueError(f"duplicate calibration trajectory seed {seed} for {node}")
        record_by_seed[seed] = untyped_record
    if set(record_by_seed) != set(expected_seed_list):
        raise ValueError(f"calibration trajectory records do not match seeds for {node}")

    rows: list[ArrayF] = []
    provenance: list[dict[str, Any]] = []
    for seed in expected_seed_list:
        path = shard_dir / f"trajectory_seed{seed}.npz"
        record = record_by_seed[seed]
        actual_sha = sha256_file(path)
        actual_bytes = path.stat().st_size
        if record.get("sha256") != actual_sha or int(record.get("bytes", -1)) != actual_bytes:
            raise ValueError(f"calibration trajectory hash/size mismatch for seed {seed}")
        rows.append(load_calibration_trajectory(path, seed))
        provenance.append({"seed": seed, "sha256": actual_sha, "bytes": actual_bytes})

    rank_path = shard_dir / "inference_rank_0.json"
    merged_path = shard_dir / "inference_merged.json"
    if manifest.get("inference_rank_0_sha256") != sha256_file(rank_path):
        raise ValueError(f"calibration rank-result hash mismatch for {node}")
    if manifest.get("inference_merged_sha256") != sha256_file(merged_path):
        raise ValueError(f"calibration merged-result hash mismatch for {node}")
    _validate_inference_results(rank_path, merged_path, expected_seed_list, node)
    return np.stack(rows), {
        "node": node,
        "execution_git_sha": repository["git_sha"],
        "manifest_sha256": sha256_file(manifest_path),
        "trajectory_records": provenance,
        "inference_rank_0_sha256": manifest["inference_rank_0_sha256"],
        "inference_merged_sha256": manifest["inference_merged_sha256"],
    }


def fit_and_write_calibration_gate(
    *,
    binding_path: Path,
    calibration_root: Path,
    heldout_root: Path,
    output_path: Path,
    repo_root: Path,
) -> dict[str, Any]:
    """Fit the frozen M1 gates and atomically write a no-return-values record."""
    state = repository_state(repo_root)
    if not state["clean"]:
        raise RuntimeError("formal M1 gate fitting requires a clean worktree")
    if heldout_root.exists() and any(heldout_root.rglob("trajectory_seed*.npz")):
        raise RuntimeError("held-out trajectories exist before the calibration gate was frozen")

    binding_loaded = yaml.safe_load(binding_path.read_text())
    if not isinstance(binding_loaded, dict):
        raise ValueError("M1 calibration binding must be a YAML mapping")
    binding: dict[str, Any] = binding_loaded
    contract = _mapping(binding, "contract")
    if contract != {
        "name": "ecomd_v1_m1_calibration_only",
        "version": 1,
        "status": "frozen_before_calibration_rollouts",
        "freeze_commit_rule": "first_git_commit_containing_this_file",
        "heldout_locked": True,
    }:
        raise ValueError("M1 calibration binding is not the frozen held-out-locked v1")
    training = _mapping(binding, "training")
    protocol_path = repo_root / str(training["protocol_path"])
    if sha256_file(protocol_path) != training.get("protocol_sha256"):
        raise ValueError("M1 protocol hash differs from the calibration binding")
    protocol = load_and_validate_m1_protocol(protocol_path, repo_root)
    binding_hash = sha256_file(binding_path)
    checkpoint_hash = str(training["checkpoint_sha256"])
    rollout = _mapping(protocol, "rollout")
    node_shards = _mapping(rollout, "node_shards")

    rows_by_seed: dict[int, ArrayF] = {}
    provenance: list[dict[str, Any]] = []
    execution_shas: set[str] = set()
    for node in ("v100_a", "v100_b"):
        node_payload = _mapping(node_shards, node)
        matrix, record = collect_calibration_shard(
            calibration_root / node,
            node=node,
            expected_seeds=[int(seed) for seed in node_payload["calibration"]],
            binding_sha256=binding_hash,
            checkpoint_sha256=checkpoint_hash,
        )
        for seed, row in zip(node_payload["calibration"], matrix, strict=True):
            parsed_seed = int(seed)
            if parsed_seed in rows_by_seed:
                raise ValueError(f"duplicate calibration seed across shards: {parsed_seed}")
            rows_by_seed[parsed_seed] = row
        provenance.append(record)
        execution_shas.add(str(record["execution_git_sha"]))
    if len(execution_shas) != 1:
        raise ValueError("calibration shards were generated from different Git revisions")
    expected_calibration_order = [int(seed) for seed in rollout["calibration_seeds"]]
    expected_calibration_seeds = set(expected_calibration_order)
    observed_calibration_seeds = {
        int(record["seed"])
        for shard in provenance
        for record in shard["trajectory_records"]
    }
    if observed_calibration_seeds != expected_calibration_seeds:
        raise ValueError("calibration shards do not partition the frozen calibration seeds")
    calibration = np.stack([rows_by_seed[seed] for seed in expected_calibration_order])
    if calibration.shape != (16, 8000):
        raise ValueError("calibration shards do not form the frozen 16-by-8000 matrix")

    energy_config = _energy_config(_mapping(protocol, "energy_gate"))
    comparator_config = _comparator_config(_mapping(protocol, "adf_kpss_comparator"))
    energy_fit = fit_stationarity_gate(calibration, energy_config)
    comparator_fit = fit_adf_kpss_gate(calibration, comparator_config)
    result = {
        "schema_version": 1,
        "status": "calibration_gate_frozen_before_heldout",
        "repository": state,
        "calibration_execution_git_sha": next(iter(execution_shas)),
        "binding_sha256": binding_hash,
        "protocol_sha256": sha256_file(protocol_path),
        "checkpoint_sha256": checkpoint_hash,
        "calibration_input_float64_le_sha256": sha256_float64(calibration),
        "n_calibration_trajectories": int(calibration.shape[0]),
        "returns_per_trajectory": int(calibration.shape[1]),
        "heldout_trajectory_count_at_fit": 0,
        "calibration_provenance": provenance,
        "energy_gate": energy_fit.to_dict(),
        "adf_kpss_comparator": comparator_fit.to_dict(),
        "record_contains_trajectory_values": False,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    temporary.replace(output_path)
    return result


def _validate_inference_results(
    rank_path: Path,
    merged_path: Path,
    expected_seeds: list[int],
    node: str,
) -> None:
    rank_loaded = json.loads(rank_path.read_text())
    if not isinstance(rank_loaded, list) or len(rank_loaded) != len(expected_seeds):
        raise ValueError(f"calibration rank-result count mismatch for {node}")
    observed: list[int] = []
    for row in rank_loaded:
        if not isinstance(row, dict):
            raise ValueError(f"invalid calibration rank-result row for {node}")
        observed.append(int(row.get("seed", -1)))
        if row.get("rank") != 0 or row.get("n_steps") != 8001:
            raise ValueError(f"calibration rank/step metadata mismatch for {node}")
        if row.get("n_recorded_returns") != 8000:
            raise ValueError(f"calibration return count mismatch for {node}")
    if observed != expected_seeds:
        raise ValueError(f"calibration inference seed order mismatch for {node}")
    merged = _json_object(merged_path)
    if merged.get("n_total_rollouts") != len(expected_seeds):
        raise ValueError(f"calibration merged rollout count mismatch for {node}")
    realizations = merged.get("realizations")
    if not isinstance(realizations, list):
        raise ValueError(f"calibration merged realizations missing for {node}")
    if [int(row.get("seed", -1)) for row in realizations if isinstance(row, dict)] != expected_seeds:
        raise ValueError(f"calibration merged seed order mismatch for {node}")


def _energy_config(payload: Mapping[str, Any]) -> GateConfig:
    return GateConfig(
        block_length=int(payload["block_length"]),
        gate_starts=tuple(int(value) for value in payload["gate_starts"]),
        late_starts=tuple(int(value) for value in payload["late_starts"]),
        max_w_star=int(payload["max_w_star"]),
        persistence_blocks=int(payload["persistence_blocks"]),
        tolerance_quantile=float(payload["tolerance_quantile"]),
        bootstrap_replicates=int(payload["bootstrap_replicates"]),
        bootstrap_seed=int(payload["bootstrap_seed"]),
        mad_floor=float(payload["mad_floor"]),
    )


def _comparator_config(payload: Mapping[str, Any]) -> ADFKPSSConfig:
    return ADFKPSSConfig(
        block_length=int(payload["block_length"]),
        gate_starts=tuple(int(value) for value in payload["gate_starts"]),
        max_w_star=int(payload["max_w_star"]),
        persistence_blocks=int(payload["persistence_blocks"]),
        trajectory_pass_fraction=float(payload["trajectory_pass_fraction"]),
        adf_alpha=float(payload["adf_alpha"]),
        kpss_alpha=float(payload["kpss_alpha"]),
        adf_maxlag=int(payload["adf_maxlag"]),
    )


def _mapping(parent: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"missing mapping: {key}")
    return value


def _json_object(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text())
    if not isinstance(loaded, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return loaded


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--binding",
        type=Path,
        default=Path("configs/ecomd_v1/m1_calibration_binding.yaml"),
    )
    parser.add_argument("--calibration-root", type=Path, required=True)
    parser.add_argument("--heldout-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    result = fit_and_write_calibration_gate(
        binding_path=args.binding.resolve(),
        calibration_root=args.calibration_root.resolve(),
        heldout_root=args.heldout_root.resolve(),
        output_path=args.output.resolve(),
        repo_root=repo_root,
    )
    print(json.dumps({
        "output": str(args.output.resolve()),
        "sha256": sha256_file(args.output.resolve()),
        "w_star": result["energy_gate"]["w_star"],
        "adf_kpss_w_star": result["adf_kpss_comparator"]["w_star"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
