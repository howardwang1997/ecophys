"""Analyze EcoMD v1 M1 held-out rollouts under the committed frozen gate."""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
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
from ..inference.m1_calibration import _mapping
from ..inference.m1_heldout import binding_freeze_commit, validate_frozen_gate
from .canonical_bands import CANONICAL_FACT_BANDS, score_against_canonical_bands
from .m1_contract import load_and_validate_m1_protocol
from .stationarity_gate import evaluate_stationarity_gate, gate_fit_from_dict
from .stylized_facts import compute_all

ArrayF: TypeAlias = npt.NDArray[np.float64]


def load_heldout_trajectory(path: Path, expected_seed: int) -> tuple[ArrayF, ArrayF]:
    """Load one exact 8,000-return held-out trajectory and aligned volume."""
    with np.load(path, allow_pickle=False) as payload:
        seed = int(payload["seed"])
        n_steps = int(payload["n_steps"])
        n_recorded = int(payload["n_recorded_returns"])
        returns = np.asarray(payload["log_returns"], dtype=np.float64)
        volumes = np.asarray(payload["volumes"], dtype=np.float64)
    if seed != expected_seed:
        raise ValueError(f"held-out seed mismatch in {path}: {seed} != {expected_seed}")
    if (
        n_steps != 8001
        or n_recorded != 8000
        or returns.shape != (8000,)
        or volumes.shape != (8000,)
    ):
        raise ValueError(
            f"held-out schema mismatch in {path}: n_steps={n_steps}, "
            f"n_recorded={n_recorded}, returns={returns.shape}, volumes={volumes.shape}"
        )
    if not np.all(np.isfinite(returns)) or not np.all(np.isfinite(volumes)):
        raise ValueError(f"held-out trajectory contains non-finite values: {path}")
    return returns, volumes


def collect_heldout_shard(
    shard_dir: Path,
    *,
    node: str,
    expected_seeds: list[int],
    binding_sha256: str,
    checkpoint_sha256: str,
    gate_sha256: str,
    frozen_w_star: int,
    binding_freeze_git_sha: str,
) -> tuple[ArrayF, ArrayF, dict[str, Any]]:
    """Verify a complete held-out shard and return rows in node-seed order."""
    manifest_path = shard_dir / "heldout_shard_manifest.json"
    manifest = _json_object(manifest_path)
    if manifest.get("schema_version") != 1:
        raise ValueError(f"unsupported held-out manifest version for {node}")
    if manifest.get("status") != "heldout_shard_complete_under_frozen_gate":
        raise ValueError(f"held-out shard is not complete for {node}")
    if manifest.get("node") != node or manifest.get("seeds") != expected_seeds:
        raise ValueError(f"held-out node/seed order mismatch for {node}")
    repository = manifest.get("repository")
    if not isinstance(repository, dict) or repository.get("clean") is not True:
        raise ValueError(f"held-out execution repository was not clean for {node}")
    if not isinstance(repository.get("git_sha"), str):
        raise ValueError(f"held-out execution Git SHA is missing for {node}")
    expected_bindings = {
        "binding_sha256": binding_sha256,
        "checkpoint_sha256": checkpoint_sha256,
        "gate_sha256": gate_sha256,
        "frozen_w_star": frozen_w_star,
        "binding_freeze_git_sha": binding_freeze_git_sha,
        "manifest_contains_trajectory_values": False,
    }
    for key, expected in expected_bindings.items():
        if manifest.get(key) != expected:
            raise ValueError(f"held-out manifest binding mismatch for {node}: {key}")

    records = manifest.get("trajectory_records")
    if not isinstance(records, list) or len(records) != len(expected_seeds):
        raise ValueError(f"held-out trajectory record count mismatch for {node}")
    record_by_seed: dict[int, dict[str, Any]] = {}
    for untyped_record in records:
        if not isinstance(untyped_record, dict):
            raise ValueError(f"invalid held-out trajectory record for {node}")
        seed = int(untyped_record.get("seed", -1))
        if seed in record_by_seed:
            raise ValueError(f"duplicate held-out trajectory seed {seed} for {node}")
        record_by_seed[seed] = untyped_record
    if set(record_by_seed) != set(expected_seeds):
        raise ValueError(f"held-out trajectory records do not match seeds for {node}")

    return_rows: list[ArrayF] = []
    volume_rows: list[ArrayF] = []
    provenance: list[dict[str, Any]] = []
    for seed in expected_seeds:
        path = shard_dir / f"trajectory_seed{seed}.npz"
        record = record_by_seed[seed]
        actual_sha = sha256_file(path)
        actual_bytes = path.stat().st_size
        if record.get("sha256") != actual_sha or int(record.get("bytes", -1)) != actual_bytes:
            raise ValueError(f"held-out trajectory hash/size mismatch for seed {seed}")
        returns, volumes = load_heldout_trajectory(path, seed)
        return_rows.append(returns)
        volume_rows.append(volumes)
        provenance.append({"seed": seed, "sha256": actual_sha, "bytes": actual_bytes})

    rank_path = shard_dir / "inference_rank_0.json"
    merged_path = shard_dir / "inference_merged.json"
    if manifest.get("inference_rank_0_sha256") != sha256_file(rank_path):
        raise ValueError(f"held-out rank-result hash mismatch for {node}")
    if manifest.get("inference_merged_sha256") != sha256_file(merged_path):
        raise ValueError(f"held-out merged-result hash mismatch for {node}")
    _validate_inference_results(rank_path, merged_path, expected_seeds, node)
    return np.stack(return_rows), np.stack(volume_rows), {
        "node": node,
        "execution_git_sha": repository["git_sha"],
        "manifest_sha256": sha256_file(manifest_path),
        "trajectory_records": provenance,
        "inference_rank_0_sha256": manifest["inference_rank_0_sha256"],
        "inference_merged_sha256": manifest["inference_merged_sha256"],
    }


def analyze_heldout(
    *,
    binding_path: Path,
    heldout_root: Path,
    output_path: Path,
    repo_root: Path,
    workers: int,
) -> dict[str, Any]:
    """Verify, score and classify all frozen held-out trajectories."""
    if workers < 1:
        raise ValueError("workers must be positive")
    state = repository_state(repo_root)
    if not state["clean"]:
        raise RuntimeError("formal M1 held-out analysis requires a clean worktree")
    binding_freeze_git_sha = binding_freeze_commit(binding_path, repo_root)
    binding_loaded = yaml.safe_load(binding_path.read_text())
    if not isinstance(binding_loaded, dict):
        raise ValueError("held-out binding must be a YAML mapping")
    binding: dict[str, Any] = binding_loaded
    if _mapping(binding, "contract") != {
        "name": "ecomd_v1_m1_heldout",
        "version": 1,
        "status": "frozen_after_calibration_gate_before_heldout",
        "freeze_commit_rule": "first_git_commit_containing_this_file",
        "gate_committed_before_heldout": True,
        "result_selection_forbidden": True,
    }:
        raise ValueError("held-out analysis contract is not frozen v1")
    training = _mapping(binding, "training")
    protocol_path = repo_root / str(training["protocol_path"])
    if sha256_file(protocol_path) != training["protocol_sha256"]:
        raise ValueError("held-out analysis protocol hash mismatch")
    protocol = load_and_validate_m1_protocol(protocol_path, repo_root)
    implementation = _mapping(binding, "implementation")
    source_hashes = {
        "stylized_facts_sha256": sha256_file(repo_root / "ecomd/eval/stylized_facts.py"),
        "canonical_bands_sha256": sha256_file(repo_root / "ecomd/eval/canonical_bands.py"),
        "stationarity_gate_sha256": sha256_file(repo_root / "ecomd/eval/stationarity_gate.py"),
        "run_large_sha256": sha256_file(repo_root / "ecomd/inference/run_large.py"),
        "seed_manifest_sha256": sha256_file(repo_root / "ecomd/inference/seed_manifest.py"),
        "heldout_analysis_sha256": sha256_file(repo_root / "ecomd/eval/m1_heldout_analysis.py"),
    }
    if source_hashes != {key: implementation[key] for key in source_hashes}:
        raise ValueError("held-out analysis implementation hash mismatch")

    gate_binding = _mapping(binding, "gate")
    gate_path = repo_root / str(gate_binding["path"])
    if sha256_file(gate_path) != gate_binding["sha256"]:
        raise ValueError("held-out analysis gate hash mismatch")
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
    gate_fit = gate_fit_from_dict(_mapping(gate, "energy_gate"))
    if gate_fit.w_star != gate_binding["frozen_w_star"]:
        raise ValueError("deserialized held-out W-star mismatch")

    binding_hash = sha256_file(binding_path)
    rollout_protocol = _mapping(protocol, "rollout")
    node_shards = _mapping(rollout_protocol, "node_shards")
    returns_by_seed: dict[int, ArrayF] = {}
    volumes_by_seed: dict[int, ArrayF] = {}
    provenance: list[dict[str, Any]] = []
    execution_shas: set[str] = set()
    for node in ("v100_a", "v100_b"):
        expected = [int(seed) for seed in _mapping(node_shards, node)["heldout"]]
        returns, volumes, record = collect_heldout_shard(
            heldout_root / node,
            node=node,
            expected_seeds=expected,
            binding_sha256=binding_hash,
            checkpoint_sha256=str(training["checkpoint_sha256"]),
            gate_sha256=str(gate_binding["sha256"]),
            frozen_w_star=int(gate_binding["frozen_w_star"]),
            binding_freeze_git_sha=binding_freeze_git_sha,
        )
        for seed, return_row, volume_row in zip(expected, returns, volumes, strict=True):
            if seed in returns_by_seed:
                raise ValueError(f"duplicate held-out seed across shards: {seed}")
            returns_by_seed[seed] = return_row
            volumes_by_seed[seed] = volume_row
        provenance.append(record)
        execution_shas.add(str(record["execution_git_sha"]))
    if len(execution_shas) != 1:
        raise ValueError("held-out shards were generated from different Git revisions")
    expected_order = [int(seed) for seed in rollout_protocol["heldout_seeds"]]
    if set(returns_by_seed) != set(expected_order):
        raise ValueError("held-out shards do not partition the frozen seeds")
    heldout_returns = np.stack([returns_by_seed[seed] for seed in expected_order])
    heldout_volumes = np.stack([volumes_by_seed[seed] for seed in expected_order])
    if heldout_returns.shape != (16, 8000) or heldout_volumes.shape != (16, 8000):
        raise ValueError("held-out shards do not form frozen 16-by-8000 matrices")

    gate_evaluation = evaluate_stationarity_gate(heldout_returns, gate_fit)
    analysis_binding = _mapping(binding, "analysis")
    starts = tuple(int(start) for start in analysis_binding["scoring_starts"])
    fixed_length = int(analysis_binding["fixed_length"])
    tasks = [
        (heldout_returns[index], heldout_volumes[index], starts, fixed_length)
        for index in range(heldout_returns.shape[0])
    ]
    if workers == 1:
        trajectory_scores = [_score_trajectory(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            trajectory_scores = list(executor.map(_score_trajectory, tasks))
    summaries = _summarize_scores(trajectory_scores, expected_order, starts)
    decision = classify_m1_result(
        frozen_w_star=int(gate_binding["frozen_w_star"]),
        gate_transfer_passes=gate_evaluation.frozen_w_star_passes is True,
        summaries=summaries,
    )
    result = {
        "schema_version": 1,
        "status": "heldout_analysis_complete_frozen_protocol",
        "repository": state,
        "heldout_execution_git_sha": next(iter(execution_shas)),
        "binding_sha256": binding_hash,
        "binding_freeze_git_sha": binding_freeze_git_sha,
        "gate_sha256": sha256_file(gate_path),
        "checkpoint_sha256": training["checkpoint_sha256"],
        "heldout_return_matrix_float64_le_sha256": sha256_float64(heldout_returns),
        "heldout_volume_matrix_float64_le_sha256": sha256_float64(heldout_volumes),
        "n_heldout_trajectories": int(heldout_returns.shape[0]),
        "returns_per_trajectory": int(heldout_returns.shape[1]),
        "frozen_w_star": gate_binding["frozen_w_star"],
        "heldout_gate_evaluation": gate_evaluation.to_dict(),
        "heldout_provenance": provenance,
        "fixed_length": fixed_length,
        "scoring_starts": list(starts),
        "sensitivity": summaries,
        "decision": decision,
        "record_contains_raw_returns_or_volumes": False,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    temporary.replace(output_path)
    return result


def classify_m1_result(
    *,
    frozen_w_star: int,
    gate_transfer_passes: bool,
    summaries: dict[str, Any],
) -> dict[str, Any]:
    """Apply the frozen M1 stationarity/fidelity continuation rule."""
    post_score = summaries[str(frozen_w_star)]["band_score"]
    late_score = summaries["4000"]["band_score"]
    post_count = int(post_score["pass_count"])
    late_count = int(late_score["pass_count"])
    post_distance = float(post_score["mean_normalized_distance"])
    late_distance = float(late_score["mean_normalized_distance"])
    ratio: float | None = (
        (1.0 if late_distance == 0.0 else None)
        if post_distance == 0.0
        else late_distance / post_distance
    )
    ratio_passes = ratio is not None and ratio <= 1.10
    next_stage = False
    if not gate_transfer_passes:
        tier = "stationarity_fail_stop"
    elif min(post_count, late_count) <= 2:
        tier = "stop_positive_model_paper"
    elif min(post_count, late_count) <= 4:
        tier = "diagnostic_only"
    elif ratio_passes:
        tier = "authorize_next_stage_not_paper_claim"
        next_stage = True
    else:
        tier = "diagnostic_only_late_degradation"
    return {
        "tier": tier,
        "stationarity_transfer_passes": gate_transfer_passes,
        "post_w_star": frozen_w_star,
        "post_pass_count": post_count,
        "late_w": 4000,
        "late_pass_count": late_count,
        "post_mean_normalized_distance": post_distance,
        "late_mean_normalized_distance": late_distance,
        "late_to_post_mean_normalized_distance_ratio": ratio,
        "maximum_authorized_ratio": 1.10,
        "next_stage_authorized": next_stage,
        "positive_model_paper_claim_authorized": False,
    }


def _score_trajectory(
    task: tuple[ArrayF, ArrayF, tuple[int, ...], int],
) -> dict[int, dict[str, float]]:
    returns, volumes, starts, fixed_length = task
    scores: dict[int, dict[str, float]] = {}
    expected_facts = set(CANONICAL_FACT_BANDS)
    for start in starts:
        stop = start + fixed_length
        if stop > returns.size:
            raise ValueError(f"fixed-length slice [{start}, {stop}) exceeds {returns.size}")
        facts = compute_all(returns[start:stop], volume=volumes[start:stop])
        if set(facts) != expected_facts:
            raise RuntimeError(f"stylized-fact set mismatch at W={start}")
        estimates = {name: float(fact.estimate) for name, fact in facts.items()}
        if not all(np.isfinite(value) for value in estimates.values()):
            raise RuntimeError(f"non-finite stylized-fact estimate at W={start}")
        scores[start] = estimates
    return scores


def _summarize_scores(
    trajectory_scores: list[dict[int, dict[str, float]]],
    seeds: list[int],
    starts: tuple[int, ...],
) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for start in starts:
        medians = {
            name: float(np.median([
                trajectory[start][name] for trajectory in trajectory_scores
            ]))
            for name in CANONICAL_FACT_BANDS
        }
        band_score = score_against_canonical_bands(medians)
        summary[str(start)] = {
            "heldout_median_estimates": medians,
            "band_score": asdict(band_score),
            "per_trajectory_estimates": [
                {"seed": seed, "estimates": trajectory[start]}
                for seed, trajectory in zip(seeds, trajectory_scores, strict=True)
            ],
        }
    return summary


def _validate_inference_results(
    rank_path: Path,
    merged_path: Path,
    expected_seeds: list[int],
    node: str,
) -> None:
    rank_loaded = json.loads(rank_path.read_text())
    if not isinstance(rank_loaded, list) or len(rank_loaded) != len(expected_seeds):
        raise ValueError(f"held-out rank-result count mismatch for {node}")
    observed: list[int] = []
    for row in rank_loaded:
        if not isinstance(row, dict):
            raise ValueError(f"invalid held-out rank-result row for {node}")
        observed.append(int(row.get("seed", -1)))
        if row.get("rank") != 0 or row.get("n_steps") != 8001:
            raise ValueError(f"held-out rank/step metadata mismatch for {node}")
        if row.get("n_recorded_returns") != 8000:
            raise ValueError(f"held-out return count mismatch for {node}")
    if observed != expected_seeds:
        raise ValueError(f"held-out inference seed order mismatch for {node}")
    merged = _json_object(merged_path)
    if merged.get("n_total_rollouts") != len(expected_seeds):
        raise ValueError(f"held-out merged rollout count mismatch for {node}")
    realizations = merged.get("realizations")
    if not isinstance(realizations, list):
        raise ValueError(f"held-out merged realizations missing for {node}")
    if [int(row.get("seed", -1)) for row in realizations if isinstance(row, dict)] != expected_seeds:
        raise ValueError(f"held-out merged seed order mismatch for {node}")


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
        default=Path("configs/ecomd_v1/m1_heldout_binding.yaml"),
    )
    parser.add_argument("--heldout-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    result = analyze_heldout(
        binding_path=args.binding.resolve(),
        heldout_root=args.heldout_root.resolve(),
        output_path=args.output.resolve(),
        repo_root=repo_root,
        workers=args.workers,
    )
    print(json.dumps({
        "output": str(args.output.resolve()),
        "sha256": sha256_file(args.output.resolve()),
        "decision": result["decision"],
    }, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
