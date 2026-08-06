"""Resumable one-GPU worker for the experiment-127 V100 nodes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, cast

import torch
import yaml  # type: ignore[import-untyped]

DEFAULT_REPO_ROOT = Path("/data/ecophys_workshop/repo")
DEFAULT_ARTIFACT_ROOT = Path("/data/ecophys_workshop/artifacts/exp127")
EXPERIMENT_REL = Path("experiments/127_workshop_claim_gates")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hardware_snapshot() -> dict[str, Any]:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable on a required V100 worker")
    properties = torch.cuda.get_device_properties(0)
    architectures = torch.cuda.get_arch_list()
    if "sm_70" not in architectures:
        raise RuntimeError(f"PyTorch wheel lacks sm_70 support: {architectures}")
    return {
        "hostname": platform.node(),
        "python": platform.python_version(),
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "cuda_arch_list": architectures,
        "gpu_name": properties.name,
        "gpu_uuid": _gpu_uuid(),
        "compute_capability": list(torch.cuda.get_device_capability(0)),
        "total_memory_bytes": int(properties.total_memory),
    }


def validate_data_snapshot(repo_root: Path) -> list[dict[str, Any]]:
    snapshot_path = repo_root / EXPERIMENT_REL / "DATA_SNAPSHOT.json"
    snapshot = json.loads(snapshot_path.read_text())
    validated: list[dict[str, Any]] = []
    for asset in snapshot["assets"]:
        root = repo_root / asset["local_path"]
        files = sorted(path for path in root.rglob("*.parquet") if path.is_file())
        digest = hashlib.sha256()
        for path in files:
            relative = path.relative_to(root).as_posix().encode()
            digest.update(len(relative).to_bytes(4, "big"))
            digest.update(relative)
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
        actual = {
            "dataset": asset["dataset"],
            "file_count": len(files),
            "total_bytes": sum(path.stat().st_size for path in files),
            "aggregate_sha256": digest.hexdigest(),
        }
        expected = {key: asset[key] for key in ("dataset", "file_count", "total_bytes", "aggregate_sha256")}
        if actual != expected:
            raise RuntimeError(f"data snapshot mismatch for {asset['dataset']}: {actual} != {expected}")
        validated.append(actual)
    return validated


def run_probe(
    node: str,
    repo_root: Path,
    artifact_root: Path,
    python_path: Path,
    execution_sha: str,
) -> dict[str, Any]:
    assignments = _load_assignments(repo_root)
    original_path = repo_root / assignments["probe_config"]
    original = yaml.safe_load(original_path.read_text())
    training = dict(original["training"])
    required = {
        "n_agents": int(original["simulator"]["n_agents"]),
        "mixed_precision": training["mixed_precision"],
        "chunk_steps": int(training["chunk_steps"]),
    }
    if required != {"n_agents": 10000, "mixed_precision": "fp32", "chunk_steps": 24}:
        raise RuntimeError(f"probe invariants changed: {required}")
    training["n_iters"] = 10
    probe_config = {"simulator": original["simulator"], "training": training}
    out_dir = artifact_root / "probes" / node
    out_dir.mkdir(parents=True, exist_ok=True)
    probe_config_path = out_dir / "probe_config.yaml"
    probe_config_path.write_text(yaml.safe_dump(probe_config, sort_keys=False))
    checkpoint_path = out_dir / "checkpoint.pt"
    if not _checkpoint_complete(checkpoint_path, 10):
        _run_logged(
            [
                str(python_path),
                "-m",
                "ecomd.training.train_distributed",
                "--config",
                str(probe_config_path),
                "--out-dir",
                str(out_dir),
                "--resume",
            ],
            cwd=repo_root,
            log_path=out_dir / "probe.log",
        )
    if not _checkpoint_complete(checkpoint_path, 10):
        raise RuntimeError("probe did not produce an iteration-10 checkpoint")
    training_log = json.loads((out_dir / "training_log.json").read_text())
    result = {
        "node": node,
        "execution_sha": execution_sha,
        "hardware": hardware_snapshot(),
        "data_assets": validate_data_snapshot(repo_root),
        "original_config": str(original_path.relative_to(repo_root)),
        "original_config_sha256": sha256_file(original_path),
        "probe_config_sha256": sha256_file(probe_config_path),
        "checkpoint_sha256": sha256_file(checkpoint_path),
        "iterations": 10,
        "train_time_seconds": training_log["train_time_seconds"],
        "peak_hbm": training_log.get("peak_hbm", {}),
    }
    _write_json(out_dir / "probe_result.json", result)
    return result


def run_training(
    node: str,
    repo_root: Path,
    artifact_root: Path,
    python_path: Path,
    execution_sha: str,
) -> dict[str, Any]:
    assignments = _load_assignments(repo_root)
    jobs = [job for job in assignments["jobs"] if job["training_node"] == node]
    status_path = artifact_root / "training" / f"status_{node}.json"
    records: list[dict[str, Any]] = []
    for job in jobs:
        config_path = repo_root / job["config"]
        if sha256_file(config_path) != job["config_sha256"]:
            raise RuntimeError(f"config hash mismatch for {job['id']}")
        config = yaml.safe_load(config_path.read_text())
        expected_iterations = int(config["training"]["n_iters"])
        out_dir = artifact_root / "training" / job["id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_path = out_dir / "checkpoint.pt"
        started = time.time()
        if not _checkpoint_complete(checkpoint_path, expected_iterations):
            _run_logged(
                [
                    str(python_path),
                    "-m",
                    "ecomd.training.train_distributed",
                    "--config",
                    str(config_path),
                    "--out-dir",
                    str(out_dir),
                    "--resume",
                ],
                cwd=repo_root,
                log_path=out_dir / "training.log",
            )
        if not _checkpoint_complete(checkpoint_path, expected_iterations):
            raise RuntimeError(f"training incomplete for {job['id']}")
        training_log_path = out_dir / "training_log.json"
        training_log = json.loads(training_log_path.read_text())
        record = {
            "job_id": job["id"],
            "node": node,
            "execution_sha": execution_sha,
            "config": job["config"],
            "config_sha256": job["config_sha256"],
            "checkpoint_sha256": sha256_file(checkpoint_path),
            "training_log_sha256": sha256_file(training_log_path),
            "iterations": expected_iterations,
            "elapsed_this_invocation_seconds": time.time() - started,
            "train_time_seconds": training_log["train_time_seconds"],
            "peak_hbm": training_log.get("peak_hbm", {}),
        }
        records.append(record)
        _write_json(status_path, {"node": node, "complete": False, "jobs": records})
    result = {
        "node": node,
        "complete": True,
        "execution_sha": execution_sha,
        "hardware": hardware_snapshot(),
        "data_assets": validate_data_snapshot(repo_root),
        "jobs": records,
    }
    _write_json(status_path, result)
    return result


def run_rollouts(
    node: str,
    split: str,
    repo_root: Path,
    artifact_root: Path,
    python_path: Path,
    execution_sha: str,
) -> dict[str, Any]:
    assignments = _load_assignments(repo_root)
    seeds_manifest = json.loads((repo_root / EXPERIMENT_REL / "SEEDS.json").read_text())
    seeds = seeds_manifest["learned_rollouts"]["node_shards"][node][split]
    status_path = artifact_root / "rollouts" / split / f"status_{node}.json"
    records: list[dict[str, Any]] = []
    for job in assignments["jobs"]:
        checkpoint_path = artifact_root / "shared_checkpoints" / job["id"] / "checkpoint.pt"
        if not checkpoint_path.is_file():
            raise FileNotFoundError(f"missing shared checkpoint {checkpoint_path}")
        config_path = repo_root / job["config"]
        if sha256_file(config_path) != job["config_sha256"]:
            raise RuntimeError(f"config hash mismatch for {job['id']}")
        out_dir = artifact_root / "rollouts" / split / job["id"] / node
        out_dir.mkdir(parents=True, exist_ok=True)
        seed_path = out_dir / "seeds.json"
        _write_json(seed_path, {"seeds": seeds})
        expected_files = [out_dir / f"trajectory_seed{seed}.npz" for seed in seeds]
        started = time.time()
        if not _rollouts_complete(expected_files, out_dir / "inference_merged.json", len(seeds)):
            _run_logged(
                [
                    str(python_path),
                    "-m",
                    "ecomd.inference.run_large",
                    "--ckpt",
                    str(checkpoint_path),
                    "--config",
                    str(config_path),
                    "--n-steps",
                    "8001",
                    "--expected-recorded-returns",
                    "8000",
                    "--seeds-file",
                    str(seed_path),
                    "--save-trajectory",
                    "--out-dir",
                    str(out_dir),
                ],
                cwd=repo_root,
                log_path=out_dir / "inference.log",
            )
        merged_path = out_dir / "inference_merged.json"
        if not _rollouts_complete(expected_files, merged_path, len(seeds)):
            raise RuntimeError(f"rollouts incomplete for {job['id']} {node} {split}")
        record = {
            "job_id": job["id"],
            "node": node,
            "split": split,
            "execution_sha": execution_sha,
            "config_sha256": job["config_sha256"],
            "checkpoint_sha256": sha256_file(checkpoint_path),
            "seeds": seeds,
            "seed_manifest_sha256": sha256_file(seed_path),
            "inference_merged_sha256": sha256_file(merged_path),
            "trajectory_sha256": {path.name: sha256_file(path) for path in expected_files},
            "elapsed_this_invocation_seconds": time.time() - started,
        }
        records.append(record)
        _write_json(status_path, {"node": node, "split": split, "complete": False, "jobs": records})
    result = {
        "node": node,
        "split": split,
        "complete": True,
        "execution_sha": execution_sha,
        "hardware": hardware_snapshot(),
        "jobs": records,
    }
    _write_json(status_path, result)
    return result


def _load_assignments(repo_root: Path) -> dict[str, Any]:
    return cast(
        dict[str, Any],
        json.loads((repo_root / EXPERIMENT_REL / "NODE_ASSIGNMENTS.json").read_text()),
    )


def _gpu_uuid() -> str:
    completed = subprocess.run(
        ["nvidia-smi", "--query-gpu=uuid", "--format=csv,noheader"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip().splitlines()[0]


def _checkpoint_complete(path: Path, expected_iterations: int) -> bool:
    if not path.is_file():
        return False
    checkpoint = torch.load(path, map_location="cpu")
    return int(checkpoint.get("iter_idx", -1)) == expected_iterations


def _rollouts_complete(paths: list[Path], merged_path: Path, expected_count: int) -> bool:
    if not all(path.is_file() for path in paths) or not merged_path.is_file():
        return False
    payload = json.loads(merged_path.read_text())
    return int(payload.get("n_total_rollouts", -1)) == expected_count


def _run_logged(command: list[str], cwd: Path, log_path: Path) -> None:
    environment = dict(os.environ)
    environment["PYTHONUNBUFFERED"] = "1"
    with log_path.open("a") as log_handle:
        log_handle.write(f"\nCOMMAND {json.dumps(command)}\n")
        log_handle.flush()
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError(f"command failed with exit code {completed.returncode}; see {log_path}")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n")
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("probe", "train", "rollouts"))
    parser.add_argument("--node", required=True, choices=("v100_a", "v100_b"))
    parser.add_argument("--split", choices=("calibration", "heldout"))
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    parser.add_argument("--execution-sha", required=True)
    args = parser.parse_args()
    if args.mode == "rollouts" and args.split is None:
        parser.error("rollouts mode requires --split")
    if args.mode != "rollouts" and args.split is not None:
        parser.error("--split is valid only for rollouts mode")

    if args.mode == "probe":
        result = run_probe(args.node, args.repo_root, args.artifact_root, args.python, args.execution_sha)
    elif args.mode == "train":
        result = run_training(args.node, args.repo_root, args.artifact_root, args.python, args.execution_sha)
    else:
        assert args.split is not None
        result = run_rollouts(
            args.node,
            args.split,
            args.repo_root,
            args.artifact_root,
            args.python,
            args.execution_sha,
        )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
