#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import selectors
import subprocess
import sys
import tarfile
import time
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, cast

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.validate_research_discovery import (
    DiscoveryValidationError,
    canonical_json_bytes,
    git_tree_files,
    load_canonical_event_log,
    load_json_schema,
    load_yaml,
    require_id,
    require_mapping,
    require_nonnegative_integer,
    require_positive_integer,
    require_sha256,
    require_string,
    require_utc_timestamp,
    sha256_mapping_without,
    tree_file_bytes,
    validate_branch_request_v1,
    validate_discovery,
    validate_partition_v2,
)

STDERR_LIMIT_BYTES = 1_000_000
RUNTIME_OVERHEAD_BYTES = 1_000_000
DOCKER_TMPFS_BYTES = 67_108_864
DOCKER_CONTROL_TIMEOUT_SECONDS = 10
DOCKER_CLEANUP_RESERVE_SECONDS = 4 * DOCKER_CONTROL_TIMEOUT_SECONDS + 2
MAX_TAR_MEMBERS = 10_000


class SandboxRuntimeError(RuntimeError):
    """Raised when a disposable sandbox cannot execute under the frozen contract."""


@dataclass(frozen=True)
class RuntimePlan:
    repo_root: Path
    base_ref: str
    sandbox_id: str
    branch_id: str
    ledger_path: Path
    artifact_root: Path
    branch_root: Path
    request_path: Path
    config_path: Path
    image_digest: str
    launcher_sha256: str
    incident_handler_sha256: str
    cpu_seconds: int
    output_bytes: int
    expires_at: datetime
    request: dict[str, object]
    execution: dict[str, object]


@contextmanager
def sandbox_lock(sandbox_id: str) -> Iterator[None]:
    lock_path = Path("/tmp") / f"ecomd_discovery_{sandbox_id}.lock"
    with lock_path.open("a+b") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SandboxRuntimeError(f"sandbox {sandbox_id} already has a running launcher") from exc
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_artifact(path: Path, repo_root: Path, *, include_bytes: bool) -> dict[str, object]:
    relative = path.relative_to(repo_root).as_posix()
    artifact: dict[str, object] = {"ref": relative, "sha256": sha256_file(path)}
    if include_bytes:
        artifact["bytes"] = path.stat().st_size
    return artifact


def append_event(ledger_path: Path, payload: dict[str, object]) -> dict[str, object]:
    entries = load_canonical_event_log(ledger_path, f"event ledger {ledger_path}")
    event = dict(payload)
    event["schema_version"] = 1
    event["seq"] = len(entries)
    event["previous_entry_sha256"] = entries[-1]["entry_sha256"]
    event["entry_sha256"] = sha256_mapping_without(event, "entry_sha256")
    encoded = canonical_json_bytes(event) + b"\n"
    descriptor = os.open(ledger_path, os.O_WRONLY | os.O_APPEND)
    try:
        written = os.write(descriptor, encoded)
        if written != len(encoded):
            raise SandboxRuntimeError("short append to sandbox event ledger")
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return event


def existing_usage(repo_root: Path, entries: list[dict[str, object]]) -> tuple[int, int, int]:
    cpu_seconds = 0
    storage_bytes = 0
    opened = 0
    finished: set[str] = set()
    for entry in entries:
        event_type = entry.get("event_type")
        if event_type == "branch_opened":
            opened += 1
        elif event_type == "branch_finished":
            branch_id = require_id(entry.get("branch_id"), "existing branch id")
            receipt = require_mapping(entry.get("receipt"), f"receipt ref for {branch_id}")
            receipt_ref = require_string(receipt.get("ref"), f"receipt ref for {branch_id}.ref")
            receipt_path = repo_root / receipt_ref
            receipt_value = cast(
                dict[str, object],
                json.loads(receipt_path.read_text(encoding="utf-8")),
            )
            cpu_seconds += require_nonnegative_integer(
                receipt_value.get("cpu_seconds"), f"receipt {branch_id}.cpu_seconds"
            )
            storage_bytes += require_nonnegative_integer(
                receipt_value.get("storage_bytes"), f"receipt {branch_id}.storage_bytes"
            )
            finished.add(branch_id)
    unfinished = {
        cast(str, entry["branch_id"])
        for entry in entries
        if entry.get("event_type") == "branch_opened"
    } - finished
    if unfinished:
        raise SandboxRuntimeError(f"sandbox has an unfinished branch: {sorted(unfinished)}")
    return cpu_seconds, storage_bytes, opened


def load_runtime_plan(
    repo_root: Path,
    sandbox_id: str,
    request_ref: str,
    base_ref: str,
) -> RuntimePlan:
    validate_discovery(repo_root, base_ref=base_ref)
    manifest_ref = f"research/discovery/sandboxes/{sandbox_id}.yaml"
    if manifest_ref not in set(git_tree_files(repo_root, base_ref, manifest_ref)):
        raise SandboxRuntimeError(
            "sandbox authorization is not yet present in the protected base revision"
        )
    manifest_path = repo_root / manifest_ref
    manifest = load_yaml(manifest_path, f"sandbox manifest {sandbox_id}")
    if manifest.get("id") != sandbox_id:
        raise SandboxRuntimeError("sandbox manifest identity mismatch")
    asset = require_mapping(manifest.get("asset"), f"sandbox {sandbox_id}.asset")
    if asset.get("kind") != "synthetic_simulator":
        raise SandboxRuntimeError("this launcher accepts only synthetic-simulator sandboxes")
    confirmation = require_mapping(
        manifest.get("confirmation_contract"), f"sandbox {sandbox_id}.confirmation_contract"
    )
    if confirmation.get("mode") != "future_public_randomness":
        raise SandboxRuntimeError("synthetic confirmation is not protected by future randomness")

    artifact_root = repo_root / "research" / "discovery" / "sandbox_artifacts" / sandbox_id
    ledger_path = artifact_root / "events.jsonl"
    entries = [dict(entry) for entry in load_canonical_event_log(ledger_path, "sandbox ledger")]
    if any(entry.get("event_type") == "state_transition" for entry in entries):
        raise SandboxRuntimeError("sandbox is already terminal")

    raw_request_path = repo_root / request_ref
    if not raw_request_path.is_file() or raw_request_path.is_symlink():
        raise SandboxRuntimeError("branch request is missing or symlinked")
    request_value = load_yaml(raw_request_path, "sandbox branch request")
    branch_id = require_id(request_value.get("branch_id"), "branch request.branch_id")
    if request_value.get("sandbox_id") != sandbox_id:
        raise SandboxRuntimeError("branch request sandbox identity mismatch")
    if any(entry.get("branch_id") == branch_id for entry in entries):
        raise SandboxRuntimeError(f"branch {branch_id} already appears in the ledger")
    branch_root = artifact_root / "branches" / branch_id
    expected_request = branch_root / "request.yaml"
    if raw_request_path.resolve() != expected_request.resolve():
        raise SandboxRuntimeError("branch request does not use its canonical artifact path")

    partition_ref = require_mapping(manifest.get("partition"), f"sandbox {sandbox_id}.partition")
    partition_path = repo_root / require_string(partition_ref.get("ref"), "partition.ref")
    partition_schema = load_json_schema(
        repo_root / "research" / "discovery" / "exploration_partition.schema.json",
        "exploration partition schema",
    )
    _, exploration_units, _ = validate_partition_v2(
        partition_path,
        repo_root,
        partition_schema,
        sandbox_id,
        require_sha256(asset.get("fingerprint_sha256"), "asset fingerprint"),
        repo_root / "research" / "discovery" / "sandbox_inputs" / sandbox_id,
    )
    reservation_raw = require_mapping(
        manifest.get("reservation"), f"sandbox {sandbox_id}.reservation"
    )
    reservation = {
        field: require_nonnegative_integer(reservation_raw.get(field), f"reservation.{field}")
        for field in ("cpu_seconds", "storage_bytes", "branches")
    }
    branch_schema = load_json_schema(
        repo_root / "research" / "discovery" / "exploration_branch_request.schema.json",
        "exploration branch request schema",
    )
    request = dict(
        validate_branch_request_v1(
            canonical_artifact(raw_request_path, repo_root, include_bytes=False),
            repo_root,
            branch_schema,
            sandbox_id,
            branch_id,
            exploration_units,
            artifact_root,
            reservation,
            "runtime branch",
        )
    )
    cpu_seconds = require_positive_integer(request.get("cpu_seconds"), "request.cpu_seconds")
    output_bytes = require_positive_integer(request.get("output_bytes"), "request.output_bytes")
    prior_cpu, _, prior_branches = existing_usage(repo_root, entries)
    if prior_cpu + cpu_seconds > reservation["cpu_seconds"]:
        raise SandboxRuntimeError("branch CPU request exceeds remaining sandbox budget")
    if prior_branches + 1 > reservation["branches"]:
        raise SandboxRuntimeError("branch count exceeds remaining sandbox budget")
    measured_storage = tree_file_bytes(
        repo_root / "research" / "discovery" / "sandbox_inputs" / sandbox_id,
        "sandbox input tree",
    ) + tree_file_bytes(artifact_root, "sandbox artifact tree")
    if measured_storage + output_bytes + RUNTIME_OVERHEAD_BYTES > reservation["storage_bytes"]:
        raise SandboxRuntimeError("branch output request exceeds remaining measured storage budget")

    execution = dict(
        require_mapping(manifest.get("execution_contract"), f"sandbox {sandbox_id}.execution")
    )
    launcher_ref = require_mapping(execution.get("launcher"), "execution.launcher")
    launcher_path = repo_root / require_string(launcher_ref.get("ref"), "execution.launcher.ref")
    if launcher_path.resolve() != Path(__file__).resolve():
        raise SandboxRuntimeError("sandbox is bound to a different runtime launcher")
    launcher_sha256 = require_sha256(
        launcher_ref.get("sha256"), "execution.launcher.sha256"
    )
    if sha256_file(launcher_path) != launcher_sha256:
        raise SandboxRuntimeError("runtime launcher digest differs from the authorization")
    incident_handler_ref = require_mapping(
        execution.get("incident_handler"),
        "execution.incident_handler",
    )
    incident_handler_path = repo_root / require_string(
        incident_handler_ref.get("ref"),
        "execution.incident_handler.ref",
    )
    expected_incident_handler = repo_root / "scripts" / "quarantine_research_discovery_sandbox.py"
    if incident_handler_path.resolve() != expected_incident_handler.resolve():
        raise SandboxRuntimeError("sandbox is bound to a different incident handler")
    incident_handler_sha256 = require_sha256(
        incident_handler_ref.get("sha256"),
        "execution.incident_handler.sha256",
    )
    if sha256_file(incident_handler_path) != incident_handler_sha256:
        raise SandboxRuntimeError("incident handler digest differs from the authorization")
    image_digest = require_string(execution.get("image_digest"), "execution.image_digest")
    expires_at = require_utc_timestamp(manifest.get("expires_at"), "sandbox.expires_at")
    remaining_ttl = (expires_at - datetime.now(UTC)).total_seconds()
    if remaining_ttl <= cpu_seconds + 30:
        raise SandboxRuntimeError("sandbox lacks enough TTL for the requested run and cleanup")
    config_ref = require_mapping(request.get("config"), "branch request.config")
    config_path = repo_root / require_string(config_ref.get("ref"), "branch request.config.ref")
    return RuntimePlan(
        repo_root=repo_root,
        base_ref=base_ref,
        sandbox_id=sandbox_id,
        branch_id=branch_id,
        ledger_path=ledger_path,
        artifact_root=artifact_root,
        branch_root=branch_root,
        request_path=raw_request_path,
        config_path=config_path,
        image_digest=image_digest,
        launcher_sha256=launcher_sha256,
        incident_handler_sha256=incident_handler_sha256,
        cpu_seconds=cpu_seconds,
        output_bytes=output_bytes,
        expires_at=expires_at,
        request=request,
        execution=execution,
    )


def docker_container_name(plan: RuntimePlan) -> str:
    return f"ecomd-dx-{plan.sandbox_id}-{plan.branch_id}"


def build_docker_command(plan: RuntimePlan) -> list[str]:
    config_path = str(plan.config_path.resolve())
    if "," in config_path:
        raise SandboxRuntimeError("Docker bind source cannot contain a comma")
    return [
        "docker",
        "run",
        "--name",
        docker_container_name(plan),
        "--pull",
        "never",
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--pids-limit",
        "128",
        "--memory",
        "2g",
        "--cpus",
        "1",
        "--ulimit",
        f"cpu={plan.cpu_seconds}:{plan.cpu_seconds}",
        "--user",
        "65534:65534",
        "--log-driver",
        "none",
        "--stop-timeout",
        "5",
        "--tmpfs",
        f"/tmp:rw,noexec,nosuid,nodev,size={DOCKER_TMPFS_BYTES}",
        "--mount",
        f"type=bind,src={config_path},dst=/sandbox/config.yaml,readonly",
        "--workdir",
        "/sandbox",
        "--env",
        "ECOMD_DX_CONFIG=/sandbox/config.yaml",
        "--env",
        f"ECOMD_DX_SANDBOX_ID={plan.sandbox_id}",
        "--env",
        f"ECOMD_DX_BRANCH_ID={plan.branch_id}",
        plan.image_digest,
    ]


def inspect_local_image(plan: RuntimePlan) -> None:
    try:
        completed = subprocess.run(
            ["docker", "image", "inspect", "--format", "{{.Id}}", plan.image_digest],
            check=False,
            capture_output=True,
            text=True,
            timeout=DOCKER_CONTROL_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise SandboxRuntimeError("timed out inspecting the pinned OCI image") from exc
    if completed.returncode != 0:
        raise SandboxRuntimeError("pinned OCI image is not available locally")
    if completed.stdout.strip() != plan.image_digest:
        raise SandboxRuntimeError("local OCI image ID differs from the frozen digest")


def validate_tar_bundle(path: Path) -> None:
    try:
        with tarfile.open(path, mode="r:") as archive:
            names: set[str] = set()
            declared_file_bytes = 0
            members = archive.getmembers()
            if len(members) > MAX_TAR_MEMBERS:
                raise SandboxRuntimeError("container output tar contains too many members")
            for member in members:
                pure = Path(member.name)
                if pure.is_absolute() or ".." in pure.parts or not member.name:
                    raise SandboxRuntimeError("container output tar contains an unsafe path")
                if member.name in names:
                    raise SandboxRuntimeError("container output tar contains duplicate paths")
                names.add(member.name)
                if not (member.isfile() or member.isdir()):
                    raise SandboxRuntimeError("container output tar contains a non-file entry")
                if member.sparse:
                    raise SandboxRuntimeError("container output tar contains a sparse file")
                if member.isfile():
                    declared_file_bytes += member.size
            if declared_file_bytes > path.stat().st_size:
                raise SandboxRuntimeError("container output tar declares oversized file content")
    except (OSError, tarfile.TarError) as exc:
        raise SandboxRuntimeError(f"container stdout is not a valid tar bundle: {exc}") from exc


def kill_container(plan: RuntimePlan) -> None:
    with suppress(subprocess.TimeoutExpired):
        subprocess.run(
            ["docker", "kill", docker_container_name(plan)],
            check=False,
            capture_output=True,
            timeout=DOCKER_CONTROL_TIMEOUT_SECONDS,
        )


def container_exists(name: str) -> bool:
    try:
        completed = subprocess.run(
            ["docker", "container", "ls", "--all", "--filter", f"name={name}", "--format", "{{.Names}}"],
            check=False, capture_output=True, text=True, timeout=DOCKER_CONTROL_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise SandboxRuntimeError("timed out checking named-container absence") from exc
    if completed.returncode != 0:
        raise SandboxRuntimeError("Docker control query failed; container absence is unproven")
    return name in completed.stdout.splitlines()


def remove_container(plan: RuntimePlan) -> None:
    try:
        completed = subprocess.run(
            ["docker", "rm", "-f", docker_container_name(plan)],
            check=False,
            capture_output=True,
            timeout=DOCKER_CONTROL_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise SandboxRuntimeError("timed out removing named container; absence is unproven") from exc
    if container_exists(docker_container_name(plan)):
        raise SandboxRuntimeError(f"named container remains after cleanup (return code {completed.returncode})")


def capture_container(plan: RuntimePlan) -> tuple[str, int | None, int, int, list[Path]]:
    plan.branch_root.mkdir(parents=True, exist_ok=True)
    bundle_path = plan.branch_root / "bundle.tar.partial"
    stderr_path = plan.branch_root / "stderr.log"
    command = build_docker_command(plan)
    started = time.monotonic()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.stdout is None or process.stderr is None:
        raise SandboxRuntimeError("Docker process did not expose output pipes")
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ, (bundle_path, plan.output_bytes))
    selector.register(process.stderr, selectors.EVENT_READ, (stderr_path, STDERR_LIMIT_BYTES))
    handles: dict[Path, IO[bytes]] = {
        bundle_path: bundle_path.open("xb"),
        stderr_path: stderr_path.open("xb"),
    }
    status: str | None = None
    forced_exit_at: float | None = None
    deadline = min(
        started + max(1, plan.cpu_seconds - DOCKER_CLEANUP_RESERVE_SECONDS),
        started + max(0.0, (plan.expires_at - datetime.now(UTC)).total_seconds()),
    )
    try:
        while selector.get_map():
            if time.monotonic() >= deadline and status is None:
                status = "timeout"
                forced_exit_at = time.monotonic() + DOCKER_CONTROL_TIMEOUT_SECONDS
                kill_container(plan)
            if forced_exit_at is not None and time.monotonic() >= forced_exit_at:
                if process.poll() is None:
                    process.kill()
                break
            for key, _ in selector.select(timeout=0.1):
                stream = cast(IO[bytes], key.fileobj)
                destination, limit = cast(tuple[Path, int], key.data)
                chunk = os.read(stream.fileno(), 65_536)
                if not chunk:
                    selector.unregister(stream)
                    continue
                handle = handles[destination]
                remaining = limit - handle.tell()
                if remaining <= 0:
                    if status is None:
                        status = "output_limit"
                        forced_exit_at = time.monotonic() + DOCKER_CONTROL_TIMEOUT_SECONDS
                        kill_container(plan)
                    continue
                handle.write(chunk[:remaining])
                if len(chunk) > remaining and status is None:
                    status = "output_limit"
                    forced_exit_at = time.monotonic() + DOCKER_CONTROL_TIMEOUT_SECONDS
                    kill_container(plan)
            if process.poll() is not None and not selector.get_map():
                break
        exit_code = process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        status = status or "timeout"
        kill_container(plan)
        process.kill()
        exit_code = process.wait(timeout=10)
    finally:
        selector.close()
        for handle in handles.values():
            handle.flush()
            os.fsync(handle.fileno())
            handle.close()
        remove_container(plan)
    elapsed = max(1, math.ceil(time.monotonic() - started))
    if status is None:
        status = "completed" if exit_code == 0 else "container_failed"
    if status == "completed":
        try:
            validate_tar_bundle(bundle_path)
        except SandboxRuntimeError:
            status = "container_failed"
        else:
            final_bundle = plan.branch_root / "bundle.tar"
            bundle_path.rename(final_bundle)
            bundle_path = final_bundle
    artifacts = [path for path in (bundle_path, stderr_path) if path.stat().st_size > 0]
    storage_bytes = sum(path.stat().st_size for path in artifacts)
    return status, exit_code, elapsed, storage_bytes, artifacts


def utc_now() -> datetime:
    return datetime.now(UTC)


def timestamp(value: datetime) -> str:
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def execute_plan(plan: RuntimePlan) -> dict[str, object]:
    inspect_local_image(plan)
    request_ref = canonical_artifact(plan.request_path, plan.repo_root, include_bytes=False)
    opened_payload = {
        "event_type": "branch_opened",
        "occurred_at": timestamp(utc_now()),
        **{
            field: plan.request[field]
            for field in plan.request
            if field not in {"schema_version", "sandbox_id"}
        },
        "request": request_ref,
    }
    append_event(plan.ledger_path, opened_payload)
    started_at = utc_now()
    status, exit_code, wall_seconds, storage_bytes, artifacts = capture_container(plan)
    finished_at = utc_now()
    if status != "completed" or wall_seconds > plan.cpu_seconds or finished_at >= plan.expires_at:
        raise SandboxRuntimeError(
            "branch did not complete within its execution contract; leave it unfinished and quarantine, never retry"
        )
    receipt_path = plan.branch_root / "receipt.json"
    receipt = {
        "schema_version": 1,
        "sandbox_id": plan.sandbox_id,
        "branch_id": plan.branch_id,
        "started_at": timestamp(started_at),
        "finished_at": timestamp(finished_at),
        "cpu_seconds": wall_seconds,
        "storage_bytes": storage_bytes,
        "monetary_cost_usd_micros": 0,
        "gpu_seconds": 0,
        "run_status": status,
        "container_exit_code": exit_code,
        "wall_seconds": wall_seconds,
        "executor": plan.execution["executor"],
        "launcher_sha256": plan.launcher_sha256,
        "incident_handler_sha256": plan.incident_handler_sha256,
        "image_digest": plan.image_digest,
        "network": plan.execution["network"],
        "root_filesystem": plan.execution["root_filesystem"],
        "repository_tree_mount": plan.execution["repository_tree_mount"],
        "input_channel": plan.execution["input_channel"],
        "confirmation_materialization": plan.execution["confirmation_materialization"],
        "output_channel": plan.execution["output_channel"],
        "secrets": plan.execution["secrets"],
        "device_access": plan.execution["device_access"],
    }
    receipt_path.write_bytes(canonical_json_bytes(receipt))
    finished_payload: dict[str, object] = {
        "event_type": "branch_finished",
        "occurred_at": timestamp(finished_at),
        "branch_id": plan.branch_id,
        "receipt": canonical_artifact(receipt_path, plan.repo_root, include_bytes=False),
        "artifacts": [
            canonical_artifact(path, plan.repo_root, include_bytes=True) for path in artifacts
        ],
    }
    append_event(plan.ledger_path, finished_payload)
    validate_discovery(plan.repo_root, base_ref=plan.base_ref)
    return receipt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one authorized disposable synthetic-market branch in a locked OCI container"
    )
    parser.add_argument("--sandbox-id", required=True)
    parser.add_argument("--request-ref", required=True)
    parser.add_argument("--base-ref", required=True)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute after validation; omission prints the exact Docker argv only",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    try:
        sandbox_id = require_id(args.sandbox_id, "sandbox id")
        request_ref = require_string(args.request_ref, "request ref")
        base_ref = require_string(args.base_ref, "base ref")
        with sandbox_lock(sandbox_id):
            plan = load_runtime_plan(repo_root, sandbox_id, request_ref, base_ref)
            if not args.execute:
                print(json.dumps(build_docker_command(plan), ensure_ascii=False))
                return 0
            receipt = execute_plan(plan)
            print(json.dumps(receipt, sort_keys=True, ensure_ascii=False))
            return 0
    except (DiscoveryValidationError, SandboxRuntimeError, OSError, ValueError) as exc:
        print(f"Discovery sandbox runtime REFUSED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
