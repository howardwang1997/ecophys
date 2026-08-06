"""Freeze learned-checkpoint stationarity gates before held-out rollouts are inspected."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, TypeAlias, cast

import numpy as np
import numpy.typing as npt

from ecomd.eval.stationarity_gate import GateConfig, fit_stationarity_gate

ArrayF: TypeAlias = npt.NDArray[np.float64]
REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_ARTIFACT_ROOT = REPO_ROOT / "outputs" / "exp127_remote_artifacts"
DEFAULT_OUTPUT_PATH = EXPERIMENT_DIR / "LEARNED_GATE_FITS.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_trajectory(path: Path, expected_seed: int) -> ArrayF:
    with np.load(path, allow_pickle=False) as payload:
        seed = int(payload["seed"])
        n_recorded = int(payload["n_recorded_returns"])
        returns = np.asarray(payload["log_returns"], dtype=np.float64)
    if seed != expected_seed:
        raise RuntimeError(f"seed mismatch in {path}: {seed} != {expected_seed}")
    if n_recorded != 8000 or returns.shape != (8000,):
        raise RuntimeError(f"trajectory schema mismatch in {path}: n={n_recorded}, shape={returns.shape}")
    if not np.all(np.isfinite(returns)):
        raise RuntimeError(f"non-finite returns in {path}")
    return returns


def collect_split(
    artifact_root: Path,
    job_id: str,
    split: str,
    seed_manifest: dict[str, Any],
) -> tuple[ArrayF, list[dict[str, Any]]]:
    expected = [int(seed) for seed in seed_manifest["learned_rollouts"][split]]
    node_shards = seed_manifest["learned_rollouts"]["node_shards"]
    seed_to_node = {
        int(seed): node
        for node, splits in node_shards.items()
        for seed in splits[split]
    }
    if set(seed_to_node) != set(expected):
        raise RuntimeError(f"node shards do not partition the {split} seeds")
    rows: list[ArrayF] = []
    provenance: list[dict[str, Any]] = []
    for seed in expected:
        node = seed_to_node[seed]
        path = artifact_root / "rollouts" / split / job_id / node / f"trajectory_seed{seed}.npz"
        rows.append(load_trajectory(path, seed))
        provenance.append({
            "seed": seed,
            "node": node,
            "path": str(path),
            "sha256": sha256_file(path),
        })
    return np.stack(rows), provenance


def fit_all(artifact_root: Path, output_path: Path, allow_dirty: bool = False) -> dict[str, Any]:
    state = _repository_state()
    if not state["clean"] and not allow_dirty:
        raise RuntimeError("formal calibration fitting requires a clean worktree")
    heldout_root = artifact_root / "rollouts" / "heldout"
    if heldout_root.exists() and any(heldout_root.rglob("trajectory_seed*.npz")):
        raise RuntimeError("held-out trajectories already exist; calibration must be frozen first")
    assignments = cast(
        dict[str, Any], json.loads((EXPERIMENT_DIR / "NODE_ASSIGNMENTS.json").read_text())
    )
    seeds = cast(dict[str, Any], json.loads((EXPERIMENT_DIR / "SEEDS.json").read_text()))
    fits: list[dict[str, Any]] = []
    for job in assignments["jobs"]:
        calibration, provenance = collect_split(artifact_root, job["id"], "calibration", seeds)
        fit = fit_stationarity_gate(calibration, GateConfig(bootstrap_seed=127900))
        fits.append({
            "job_id": job["id"],
            "config": job["config"],
            "config_sha256": job["config_sha256"],
            "calibration_provenance": provenance,
            "gate_fit": fit.to_dict(),
        })
    result = {
        "schema_version": 1,
        "status": "calibration_frozen_before_heldout",
        "repository": state,
        "seed_manifest_sha256": sha256_file(EXPERIMENT_DIR / "SEEDS.json"),
        "assignments_sha256": sha256_file(EXPERIMENT_DIR / "NODE_ASSIGNMENTS.json"),
        "fits": fits,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2) + "\n")
    temporary.replace(output_path)
    return result


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
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--allow-dirty", action="store_true", help="debug only; never formal")
    args = parser.parse_args()
    result = fit_all(args.artifact_root, args.output, allow_dirty=args.allow_dirty)
    print(json.dumps({
        "output": str(args.output),
        "sha256": sha256_file(args.output),
        "w_star": {row["job_id"]: row["gate_fit"]["w_star"] for row in result["fits"]},
    }, indent=2))


if __name__ == "__main__":
    main()
