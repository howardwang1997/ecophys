"""Analyze experiment-127 held-out learned rollouts under frozen calibration gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path
from typing import Any, TypeAlias, cast

import numpy as np
import numpy.typing as npt

from ecomd.eval.canonical_bands import score_against_canonical_bands
from ecomd.eval.stationarity_gate import (
    evaluate_stationarity_gate,
    gate_fit_from_dict,
)
from ecomd.eval.stylized_facts import compute_all

ArrayF: TypeAlias = npt.NDArray[np.float64]
REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_ARTIFACT_ROOT = REPO_ROOT / "outputs" / "exp127_remote_artifacts"
DEFAULT_GATE_PATH = EXPERIMENT_DIR / "LEARNED_GATE_FITS.json"
DEFAULT_OUTPUT_PATH = EXPERIMENT_DIR / "LEARNED_RESULTS.json"
W_GRID = (0, 50, 100, 200, 500, 1000, 1500, 2000, 3000)
FIXED_LENGTH = 4000


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_trajectory(path: Path, expected_seed: int) -> tuple[ArrayF, ArrayF]:
    with np.load(path, allow_pickle=False) as payload:
        seed = int(payload["seed"])
        n_recorded = int(payload["n_recorded_returns"])
        returns = np.asarray(payload["log_returns"], dtype=np.float64)
        volumes = np.asarray(payload["volumes"], dtype=np.float64)
    if seed != expected_seed:
        raise RuntimeError(f"seed mismatch in {path}: {seed} != {expected_seed}")
    if n_recorded != 8000 or returns.shape != (8000,) or volumes.shape != (8000,):
        raise RuntimeError(
            f"trajectory schema mismatch in {path}: n={n_recorded}, "
            f"returns={returns.shape}, volumes={volumes.shape}"
        )
    if not np.all(np.isfinite(returns)) or not np.all(np.isfinite(volumes)):
        raise RuntimeError(f"non-finite trajectory values in {path}")
    return returns, volumes


def collect_heldout(
    artifact_root: Path,
    job_id: str,
    seed_manifest: dict[str, Any],
) -> tuple[ArrayF, ArrayF, list[dict[str, Any]]]:
    expected = [int(seed) for seed in seed_manifest["learned_rollouts"]["heldout"]]
    node_shards = seed_manifest["learned_rollouts"]["node_shards"]
    seed_to_node = {
        int(seed): node
        for node, splits in node_shards.items()
        for seed in splits["heldout"]
    }
    if set(seed_to_node) != set(expected):
        raise RuntimeError("node shards do not partition held-out seeds")
    returns_rows: list[ArrayF] = []
    volume_rows: list[ArrayF] = []
    provenance: list[dict[str, Any]] = []
    for seed in expected:
        node = seed_to_node[seed]
        path = artifact_root / "rollouts" / "heldout" / job_id / node / f"trajectory_seed{seed}.npz"
        returns, volumes = load_trajectory(path, seed)
        returns_rows.append(returns)
        volume_rows.append(volumes)
        provenance.append({"seed": seed, "node": node, "path": str(path), "sha256": sha256_file(path)})
    return np.stack(returns_rows), np.stack(volume_rows), provenance


def analyze(
    artifact_root: Path,
    gate_path: Path,
    output_path: Path,
    workers: int,
    allow_dirty: bool = False,
) -> dict[str, Any]:
    state = _repository_state()
    if not state["clean"] and not allow_dirty:
        raise RuntimeError("formal learned analysis requires a clean worktree")
    gate_payload = cast(dict[str, Any], json.loads(gate_path.read_text()))
    if gate_payload.get("status") != "calibration_frozen_before_heldout":
        raise RuntimeError("gate file was not frozen in the pre-heldout state")
    gate_by_job = {row["job_id"]: row for row in gate_payload["fits"]}
    assignments = cast(
        dict[str, Any], json.loads((EXPERIMENT_DIR / "NODE_ASSIGNMENTS.json").read_text())
    )
    seeds = cast(dict[str, Any], json.loads((EXPERIMENT_DIR / "SEEDS.json").read_text()))

    checkpoint_results: list[dict[str, Any]] = []
    for job in assignments["jobs"]:
        fit_record = gate_by_job[job["id"]]
        fit = gate_fit_from_dict(fit_record["gate_fit"])
        heldout_returns, heldout_volumes, provenance = collect_heldout(artifact_root, job["id"], seeds)
        evaluation = evaluate_stationarity_gate(heldout_returns, fit)
        starts = tuple(sorted(set(W_GRID) | ({fit.w_star} if fit.w_star is not None else set())))
        tasks = [
            (heldout_returns[index], heldout_volumes[index], starts)
            for index in range(heldout_returns.shape[0])
        ]
        if workers == 1:
            trajectory_scores = [_score_trajectory(task) for task in tasks]
        else:
            with ProcessPoolExecutor(max_workers=workers) as executor:
                trajectory_scores = list(executor.map(_score_trajectory, tasks))

        summaries = _summarize_sensitivity(trajectory_scores, starts)
        paired_deltas: list[float] = []
        if fit.w_star is not None:
            for trajectory in trajectory_scores:
                before = float(trajectory[0]["hill_tail_index"])
                after = float(trajectory[fit.w_star]["hill_tail_index"])
                paired_deltas.append(after - before)
        checkpoint_results.append({
            "job_id": job["id"],
            "config": job["config"],
            "config_sha256": job["config_sha256"],
            "calibration_w_star": fit.w_star,
            "heldout_gate_evaluation": evaluation.to_dict(),
            "heldout_provenance": provenance,
            "sensitivity": summaries,
            "paired_hill_differences": paired_deltas,
            "checkpoint_median_hill_difference": (
                float(np.median(paired_deltas)) if paired_deltas else None
            ),
        })

    primary = _primary_summary(checkpoint_results, bootstrap_seed=127901, replicates=2000)
    result = {
        "schema_version": 1,
        "repository": state,
        "gate_fit_path": str(gate_path),
        "gate_fit_sha256": sha256_file(gate_path),
        "seed_manifest_sha256": sha256_file(EXPERIMENT_DIR / "SEEDS.json"),
        "w_grid": list(W_GRID),
        "fixed_length": FIXED_LENGTH,
        "hill_k_frac": 0.05,
        "primary": primary,
        "checkpoints": checkpoint_results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2) + "\n")
    temporary.replace(output_path)
    return result


def _score_trajectory(task: tuple[ArrayF, ArrayF, tuple[int, ...]]) -> dict[int, dict[str, float]]:
    returns, volumes, starts = task
    scores: dict[int, dict[str, float]] = {}
    for start in starts:
        stop = start + FIXED_LENGTH
        if stop > returns.size:
            raise ValueError(f"fixed-length slice [{start}, {stop}) exceeds {returns.size}")
        facts = compute_all(returns[start:stop], volume=volumes[start:stop])
        estimates = {name: float(fact.estimate) for name, fact in facts.items()}
        if not all(np.isfinite(value) for value in estimates.values()):
            raise RuntimeError(f"non-finite stylized-fact estimate at W={start}")
        scores[start] = estimates
    return scores


def _summarize_sensitivity(
    trajectory_scores: list[dict[int, dict[str, float]]],
    starts: tuple[int, ...],
) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for start in starts:
        names = tuple(trajectory_scores[0][start])
        medians = {
            name: float(np.median([trajectory[start][name] for trajectory in trajectory_scores]))
            for name in names
        }
        band_score = score_against_canonical_bands(medians)
        summary[str(start)] = {
            "heldout_median_estimates": medians,
            "band_score": asdict(band_score),
            "per_trajectory_estimates": [trajectory[start] for trajectory in trajectory_scores],
        }
    return summary


def _primary_summary(
    checkpoints: list[dict[str, Any]],
    bootstrap_seed: int,
    replicates: int,
) -> dict[str, Any]:
    e1 = [checkpoint for checkpoint in checkpoints if checkpoint["job_id"].startswith("e1_")]
    e3 = [checkpoint for checkpoint in checkpoints if checkpoint["job_id"].startswith("e3_")]
    scorable_e1 = [checkpoint for checkpoint in e1 if checkpoint["paired_hill_differences"]]
    confirmed_e1 = [
        checkpoint
        for checkpoint in scorable_e1
        if checkpoint["heldout_gate_evaluation"]["frozen_w_star_passes"] is True
    ]
    point: float | None = None
    ci: tuple[float, float] | None = None
    if scorable_e1:
        point = float(np.mean([
            np.median(checkpoint["paired_hill_differences"])
            for checkpoint in scorable_e1
        ]))
        rng = np.random.default_rng(bootstrap_seed)
        bootstrap: ArrayF = np.empty(replicates, dtype=np.float64)
        for replicate in range(replicates):
            sampled_indices = rng.integers(0, len(scorable_e1), size=len(scorable_e1))
            checkpoint_statistics: list[float] = []
            for index in sampled_indices:
                differences = np.asarray(
                    scorable_e1[int(index)]["paired_hill_differences"], dtype=np.float64
                )
                sampled = rng.choice(differences, size=differences.size, replace=True)
                checkpoint_statistics.append(float(np.median(sampled)))
            bootstrap[replicate] = float(np.mean(checkpoint_statistics))
        ci = (float(np.quantile(bootstrap, 0.025)), float(np.quantile(bootstrap, 0.975)))

    e3_signs = [
        int(np.sign(float(checkpoint["checkpoint_median_hill_difference"])))
        for checkpoint in e3
        if checkpoint["checkpoint_median_hill_difference"] is not None
    ]
    positive_e3 = sum(sign > 0 for sign in e3_signs)
    return {
        "estimand": "equal-weight mean of checkpoint median paired Hill differences",
        "e1_total": len(e1),
        "e1_scorable": len(scorable_e1),
        "e1_heldout_gate_confirmed": len(confirmed_e1),
        "effect": point,
        "ci_95": list(ci) if ci is not None else None,
        "expected_positive_direction_passes": ci is not None and ci[0] > 0.0,
        "bootstrap_seed": bootstrap_seed,
        "bootstrap_replicates": replicates,
        "e3_scorable": len(e3_signs),
        "e3_positive_sign_count": positive_e3,
        "e3_same_positive_sign_2_of_3": len(e3_signs) == 3 and positive_e3 >= 2,
    }


def _repository_state() -> dict[str, Any]:
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO_ROOT, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    return {"git_sha": sha, "clean": not status, "status_entries": status}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--gate-fits", type=Path, default=DEFAULT_GATE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--allow-dirty", action="store_true", help="debug only; never formal")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be positive")
    result = analyze(
        args.artifact_root,
        args.gate_fits,
        args.output,
        args.workers,
        allow_dirty=args.allow_dirty,
    )
    print(json.dumps({"output": str(args.output), "sha256": sha256_file(args.output),
                      "primary": result["primary"]}, indent=2))


if __name__ == "__main__":
    main()
