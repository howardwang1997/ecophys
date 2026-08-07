"""Resume-safe Mac-side orchestration for the two-node experiment-127 execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_REL = Path("experiments/127_workshop_claim_gates")
DEFAULT_MACHINE_FILE = REPO_ROOT / "scripts/machines.local.json"
DEFAULT_LOCAL_ROOT = REPO_ROOT / "outputs/exp127_remote_artifacts"
REMOTE_REPO = Path("/data/ecophys_workshop/repo")
REMOTE_ARTIFACT_ROOT = Path("/data/ecophys_workshop/artifacts/exp127")
REMOTE_PYTHON = Path("/data/ecophys_workshop/conda_env/bin/python")

TRAINING_SERVICES = {
    "v100_a": "ecophys-exp127-train-a.service",
    "v100_b": "ecophys-exp127-train-b.service",
}
ACTIVE_SERVICE_STATES = frozenset({"active", "activating", "reloading"})
WAITABLE_SERVICE_STATES = ACTIVE_SERVICE_STATES | {"unreachable"}
TERMINAL_STATUS_GRACE_ATTEMPTS = 5
TERMINAL_STATUS_GRACE_SECONDS = 2.0


@dataclass(frozen=True)
class Node:
    name: str
    host: str
    user: str

    @property
    def target(self) -> str:
        return f"{self.user}@{self.host}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_nodes(path: Path) -> dict[str, Node]:
    payload = cast(dict[str, Any], json.loads(path.read_text()))
    expected = {"v100_a", "v100_b"}
    if set(payload) != expected:
        raise ValueError(f"machine inventory must contain exactly {sorted(expected)}")
    nodes = {
        name: Node(name=name, host=str(record["host"]), user=str(record.get("user", "root")))
        for name, record in payload.items()
    }
    if len({node.host for node in nodes.values()}) != len(nodes):
        raise ValueError("machine inventory contains duplicate hosts")
    return nodes


def run(command: Sequence[str], *, check: bool = True, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        check=check,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def ssh(node: Node, command: Sequence[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(
        [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=20",
            node.target,
            *command,
        ],
        check=check,
    )


def remote_json(node: Node, path: Path) -> dict[str, Any] | None:
    completed = ssh(node, ["cat", str(path)], check=False)
    if completed.returncode != 0:
        return None
    return cast(dict[str, Any], json.loads(completed.stdout))


def service_state(node: Node, service: str) -> str:
    completed = ssh(node, ["systemctl", "is-active", service], check=False)
    state = completed.stdout.strip()
    if completed.returncode == 255 and not state:
        return "unreachable"
    return state or "unknown"


def log(message: str) -> None:
    timestamp = datetime.now(UTC).isoformat(timespec="seconds")
    print(f"[{timestamp}] {message}", flush=True)


def observe_stage(
    node: Node,
    status_path: Path,
    service: str,
) -> tuple[dict[str, Any] | None, str]:
    payload = remote_json(node, status_path)
    if payload is not None and payload.get("complete") is True:
        return payload, "complete"
    state = service_state(node, service)
    if state in WAITABLE_SERVICE_STATES:
        return None, state
    for _ in range(TERMINAL_STATUS_GRACE_ATTEMPTS):
        time.sleep(TERMINAL_STATUS_GRACE_SECONDS)
        payload = remote_json(node, status_path)
        if payload is not None and payload.get("complete") is True:
            return payload, "complete"
        state = service_state(node, service)
        if state in WAITABLE_SERVICE_STATES:
            return None, state
    return payload, state


def wait_for_stage(
    nodes: dict[str, Node],
    status_paths: dict[str, Path],
    services: dict[str, str],
    poll_seconds: int,
) -> dict[str, dict[str, Any]]:
    while True:
        records: dict[str, dict[str, Any]] = {}
        states: list[str] = []
        for name, node in nodes.items():
            payload, state = observe_stage(node, status_paths[name], services[name])
            if payload is not None and payload.get("complete") is True:
                records[name] = payload
                states.append(f"{name}=complete")
                continue
            states.append(f"{name}={state}")
            if state not in WAITABLE_SERVICE_STATES:
                raise RuntimeError(
                    f"{name} service {services[name]} is {state} before a complete status was written"
                )
        log(", ".join(states))
        if len(records) == len(nodes):
            return records
        time.sleep(poll_seconds)


def rsync_pull(node: Node, remote: Path, local: Path) -> None:
    local.mkdir(parents=True, exist_ok=True)
    run(
        [
            "rsync",
            "-a",
            "--partial",
            "-e",
            "ssh -o BatchMode=yes -o ConnectTimeout=20",
            f"{node.target}:{remote.as_posix().rstrip('/')}/",
            f"{local.as_posix().rstrip('/')}/",
        ]
    )


def rsync_push(node: Node, local: Path, remote: Path) -> None:
    ssh(node, ["mkdir", "-p", str(remote.parent)])
    run(
        [
            "rsync",
            "-a",
            "--partial",
            "-e",
            "ssh -o BatchMode=yes -o ConnectTimeout=20",
            str(local),
            f"{node.target}:{remote}",
        ]
    )


def fetch_training(
    nodes: dict[str, Node],
    assignments: dict[str, Any],
    local_root: Path,
    statuses: dict[str, dict[str, Any]],
) -> None:
    for name, node in nodes.items():
        job_ids = {str(job["id"]) for job in assignments["jobs"] if job["training_node"] == name}
        status_by_job = {str(row["job_id"]): row for row in statuses[name]["jobs"]}
        if set(status_by_job) != job_ids:
            raise RuntimeError(f"{name} training status job mismatch")
        for job_id in sorted(job_ids):
            remote = REMOTE_ARTIFACT_ROOT / "training" / job_id
            local = local_root / "training" / job_id
            rsync_pull(node, remote, local)
            checkpoint = local / "checkpoint.pt"
            training_log = local / "training_log.json"
            record = status_by_job[job_id]
            if sha256_file(checkpoint) != record["checkpoint_sha256"]:
                raise RuntimeError(f"checkpoint hash mismatch after pull: {job_id}")
            if sha256_file(training_log) != record["training_log_sha256"]:
                raise RuntimeError(f"training-log hash mismatch after pull: {job_id}")
        status_path = local_root / "training" / f"status_{name}.json"
        write_json(status_path, statuses[name])


def distribute_checkpoints(
    nodes: dict[str, Node], assignments: dict[str, Any], local_root: Path
) -> None:
    for job in assignments["jobs"]:
        job_id = str(job["id"])
        local = local_root / "training" / job_id / "checkpoint.pt"
        expected = sha256_file(local)
        for name, node in nodes.items():
            remote = REMOTE_ARTIFACT_ROOT / "shared_checkpoints" / job_id / "checkpoint.pt"
            actual_record = ssh(node, ["sha256sum", str(remote)], check=False)
            if actual_record.returncode == 0 and actual_record.stdout.split()[0] == expected:
                continue
            rsync_push(node, local, remote)
            actual = ssh(node, ["sha256sum", str(remote)]).stdout.split()[0]
            if actual != expected:
                raise RuntimeError(f"checkpoint hash mismatch after push: {job_id} on {name}")
    log("all ten checkpoints are hash-verified on both nodes")


def rollout_service_name(split: str, node_name: str) -> str:
    suffix = "a" if node_name == "v100_a" else "b"
    return f"ecophys-exp127-{split}-{suffix}.service"


def start_rollouts(nodes: dict[str, Node], split: str, execution_sha: str) -> dict[str, str]:
    services: dict[str, str] = {}
    for name, node in nodes.items():
        unit = rollout_service_name(split, name)
        services[name] = unit
        status_path = REMOTE_ARTIFACT_ROOT / "rollouts" / split / f"status_{name}.json"
        payload = remote_json(node, status_path)
        if payload is not None and payload.get("complete") is True:
            log(f"{name} {split} rollouts already complete")
            continue
        state = service_state(node, unit)
        if state in {"active", "activating", "reloading"}:
            log(f"{name} {split} rollout service already {state}")
            continue
        command = [
            "systemd-run",
            f"--unit={unit}",
            "--collect",
            "--setenv=PYTHONUNBUFFERED=1",
            "--",
            str(REMOTE_PYTHON),
            str(REMOTE_REPO / EXPERIMENT_REL / "v100_worker.py"),
            "rollouts",
            "--node",
            name,
            "--split",
            split,
            "--execution-sha",
            execution_sha,
            "--repo-root",
            str(REMOTE_REPO),
            "--artifact-root",
            str(REMOTE_ARTIFACT_ROOT),
            "--python",
            str(REMOTE_PYTHON),
        ]
        ssh(node, command)
        log(f"started {split} rollouts on {name}")
    return services


def fetch_rollouts(
    nodes: dict[str, Node],
    split: str,
    local_root: Path,
    statuses: dict[str, dict[str, Any]],
) -> None:
    local_split = local_root / "rollouts" / split
    for name, node in nodes.items():
        rsync_pull(node, REMOTE_ARTIFACT_ROOT / "rollouts" / split, local_split)
        write_json(local_split / f"status_{name}.json", statuses[name])
    validate_rollouts(nodes, split, local_root, statuses)


def validate_rollouts(
    nodes: dict[str, Node],
    split: str,
    local_root: Path,
    statuses: dict[str, dict[str, Any]],
) -> None:
    for name in nodes:
        for record in statuses[name]["jobs"]:
            job_id = str(record["job_id"])
            directory = local_root / "rollouts" / split / job_id / name
            if sha256_file(directory / "seeds.json") != record["seed_manifest_sha256"]:
                raise RuntimeError(f"seed-manifest hash mismatch: {split} {job_id} {name}")
            if sha256_file(directory / "inference_merged.json") != record["inference_merged_sha256"]:
                raise RuntimeError(f"merged-result hash mismatch: {split} {job_id} {name}")
            for filename, expected in record["trajectory_sha256"].items():
                if sha256_file(directory / filename) != expected:
                    raise RuntimeError(f"trajectory hash mismatch: {split} {job_id} {name} {filename}")
    log(f"all {split} rollout shards passed local hash verification")


def freeze_calibration(execution_worktree: Path, local_root: Path, execution_sha: str) -> Path:
    control = local_root / "control"
    gate_path = control / "LEARNED_GATE_FITS.json"
    freeze_path = control / "CALIBRATION_FREEZE.json"
    heldout_root = local_root / "rollouts" / "heldout"
    if gate_path.is_file() and freeze_path.is_file():
        freeze = cast(dict[str, Any], json.loads(freeze_path.read_text()))
        if sha256_file(gate_path) != freeze["gate_sha256"]:
            raise RuntimeError("existing calibration freeze hash does not match gate file")
        return gate_path
    if heldout_root.exists() and any(heldout_root.rglob("trajectory_seed*.npz")):
        raise RuntimeError("held-out trajectories exist before a calibration freeze")
    control.mkdir(parents=True, exist_ok=True)
    script = execution_worktree / EXPERIMENT_REL / "fit_learned_calibration.py"
    completed = run(
        [
            sys.executable,
            str(script),
            "--artifact-root",
            str(local_root),
            "--output",
            str(gate_path),
        ],
        cwd=execution_worktree,
    )
    log(completed.stdout.strip())
    freeze = {
        "schema_version": 1,
        "frozen_at": datetime.now(UTC).isoformat(),
        "execution_sha": execution_sha,
        "gate_path": str(gate_path),
        "gate_sha256": sha256_file(gate_path),
        "heldout_trajectory_count_at_freeze": 0,
    }
    write_json(freeze_path, freeze)
    log(f"calibration gate frozen at SHA-256 {freeze['gate_sha256']}")
    return gate_path


def analyze_heldout(
    execution_worktree: Path,
    local_root: Path,
    gate_path: Path,
    workers: int,
) -> Path:
    control = local_root / "control"
    output = control / "LEARNED_RESULTS.json"
    if output.is_file():
        return output
    script = execution_worktree / EXPERIMENT_REL / "analyze_learned_results.py"
    completed = run(
        [
            sys.executable,
            str(script),
            "--artifact-root",
            str(local_root),
            "--gate-fits",
            str(gate_path),
            "--output",
            str(output),
            "--workers",
            str(workers),
        ],
        cwd=execution_worktree,
    )
    log(completed.stdout.strip())
    return output


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n")
    temporary.replace(path)


def verify_execution_worktree(path: Path, execution_sha: str) -> None:
    actual = run(["git", "rev-parse", "HEAD"], cwd=path).stdout.strip()
    dirty = run(["git", "status", "--porcelain"], cwd=path).stdout.strip()
    if actual != execution_sha or dirty:
        raise RuntimeError(f"execution worktree is not clean at {execution_sha}")


def orchestrate(args: argparse.Namespace) -> dict[str, Any]:
    nodes = load_nodes(args.machine_file)
    manifest = cast(
        dict[str, Any], json.loads((REPO_ROOT / EXPERIMENT_REL / "MANIFEST.json").read_text())
    )
    execution_sha = str(args.execution_sha or manifest["scientific_execution_git_sha"])
    execution_worktree = args.execution_worktree or Path("/private/tmp") / f"ecophys-exp127-{execution_sha[:8]}"
    verify_execution_worktree(execution_worktree, execution_sha)
    assignments = cast(
        dict[str, Any],
        json.loads((execution_worktree / EXPERIMENT_REL / "NODE_ASSIGNMENTS.json").read_text()),
    )

    training_status_paths = {
        name: REMOTE_ARTIFACT_ROOT / "training" / f"status_{name}.json" for name in nodes
    }
    training = wait_for_stage(nodes, training_status_paths, TRAINING_SERVICES, args.poll_seconds)
    fetch_training(nodes, assignments, args.local_root, training)
    distribute_checkpoints(nodes, assignments, args.local_root)

    calibration_services = start_rollouts(nodes, "calibration", execution_sha)
    calibration_status_paths = {
        name: REMOTE_ARTIFACT_ROOT / "rollouts/calibration" / f"status_{name}.json"
        for name in nodes
    }
    calibration = wait_for_stage(
        nodes, calibration_status_paths, calibration_services, args.poll_seconds
    )
    fetch_rollouts(nodes, "calibration", args.local_root, calibration)
    gate_path = freeze_calibration(execution_worktree, args.local_root, execution_sha)

    heldout_services = start_rollouts(nodes, "heldout", execution_sha)
    heldout_status_paths = {
        name: REMOTE_ARTIFACT_ROOT / "rollouts/heldout" / f"status_{name}.json" for name in nodes
    }
    heldout = wait_for_stage(nodes, heldout_status_paths, heldout_services, args.poll_seconds)
    fetch_rollouts(nodes, "heldout", args.local_root, heldout)
    result_path = analyze_heldout(
        execution_worktree, args.local_root, gate_path, workers=args.analysis_workers
    )
    result = {
        "schema_version": 1,
        "completed_at": datetime.now(UTC).isoformat(),
        "execution_sha": execution_sha,
        "gate_path": str(gate_path),
        "gate_sha256": sha256_file(gate_path),
        "result_path": str(result_path),
        "result_sha256": sha256_file(result_path),
    }
    write_json(args.local_root / "control/CONTROLLER_COMPLETE.json", result)
    log(json.dumps(result, indent=2))
    return result


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--machine-file", type=Path, default=DEFAULT_MACHINE_FILE)
    parser.add_argument("--local-root", type=Path, default=DEFAULT_LOCAL_ROOT)
    parser.add_argument("--execution-sha")
    parser.add_argument("--execution-worktree", type=Path)
    parser.add_argument("--poll-seconds", type=int, default=60)
    parser.add_argument("--analysis-workers", type=int, default=4)
    args = parser.parse_args(argv)
    if args.poll_seconds < 10:
        parser.error("--poll-seconds must be at least 10")
    if args.analysis_workers < 1:
        parser.error("--analysis-workers must be positive")
    return args


def main() -> None:
    orchestrate(parse_args())


if __name__ == "__main__":
    main()
