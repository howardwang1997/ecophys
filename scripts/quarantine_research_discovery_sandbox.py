#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_research_discovery_sandbox import (
    DOCKER_CONTROL_TIMEOUT_SECONDS,
    SandboxRuntimeError,
    append_event,
    canonical_artifact,
    sandbox_lock,
    sha256_file,
    timestamp,
    utc_now,
)
from scripts.validate_research_discovery import (
    SANDBOX_STDERR_LIMIT_BYTES,
    DiscoveryValidationError,
    canonical_json_bytes,
    git_tree_files,
    load_canonical_event_log,
    load_canonical_json_mapping,
    load_yaml,
    require_id,
    require_mapping,
    require_nonnegative_integer,
    require_sha256,
    require_string,
    validate_discovery,
)

REASON_CODES = {
    "host_interruption",
    "launcher_exception",
    "operator_abort",
    "container_state_unknown_resolved",
}


@dataclass(frozen=True)
class QuarantinePlan:
    repo_root: Path
    base_ref: str
    sandbox_id: str
    branch_id: str
    ledger_path: Path
    artifact_root: Path
    branch_root: Path
    incident_path: Path
    result_path: Path
    registry_path: Path
    manifest_sha256: str
    partition_sha256: str
    campaign_id: str
    charged_usage: dict[str, int]
    prior_usage: dict[str, int]
    branch_ids: list[str]


def write_new_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        offset = 0
        while offset < len(payload):
            written = os.write(descriptor, payload[offset:])
            if written <= 0:
                raise SandboxRuntimeError(f"short write to {path}")
            offset += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_replace_bytes(path: Path, payload: bytes) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    write_new_bytes(temporary, payload)
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def receipt_usage(repo_root: Path, entry: dict[str, object]) -> dict[str, int]:
    receipt_ref = require_mapping(entry.get("receipt"), "finished branch receipt")
    receipt_path = repo_root / require_string(receipt_ref.get("ref"), "finished receipt.ref")
    receipt = load_canonical_json_mapping(receipt_path, f"receipt {receipt_path}")
    return {
        field: require_nonnegative_integer(receipt.get(field), f"receipt {receipt_path}.{field}")
        for field in (
            "cpu_seconds",
            "storage_bytes",
            "monetary_cost_usd_micros",
            "gpu_seconds",
        )
    }


def load_quarantine_plan(
    repo_root: Path,
    sandbox_id: str,
    branch_id: str,
    base_ref: str,
) -> QuarantinePlan:
    validate_discovery(repo_root, base_ref=base_ref)
    manifest_ref = f"research/discovery/sandboxes/{sandbox_id}.yaml"
    if manifest_ref not in set(git_tree_files(repo_root, base_ref, manifest_ref)):
        raise SandboxRuntimeError("sandbox authorization is absent from the protected base")
    manifest_path = repo_root / manifest_ref
    manifest = load_yaml(manifest_path, f"sandbox manifest {sandbox_id}")
    if manifest.get("id") != sandbox_id:
        raise SandboxRuntimeError("sandbox manifest identity mismatch")
    execution = require_mapping(
        manifest.get("execution_contract"),
        f"sandbox {sandbox_id}.execution_contract",
    )
    handler_ref = require_mapping(execution.get("incident_handler"), "incident handler")
    handler_path = repo_root / require_string(handler_ref.get("ref"), "incident handler.ref")
    expected_handler = repo_root / "scripts" / "quarantine_research_discovery_sandbox.py"
    if handler_path.resolve() != expected_handler.resolve():
        raise SandboxRuntimeError("sandbox is bound to a different incident handler")
    handler_sha256 = require_sha256(handler_ref.get("sha256"), "incident handler.sha256")
    if sha256_file(handler_path) != handler_sha256:
        raise SandboxRuntimeError("incident handler digest differs from the authorization")

    artifact_root = repo_root / "research" / "discovery" / "sandbox_artifacts" / sandbox_id
    branch_root = artifact_root / "branches" / branch_id
    ledger_path = artifact_root / "events.jsonl"
    entries = [dict(entry) for entry in load_canonical_event_log(ledger_path, "sandbox ledger")]
    opened: dict[str, dict[str, object]] = {}
    resolved: set[str] = set()
    prior_usage = {
        "cpu_seconds": 0,
        "storage_bytes": 0,
        "monetary_cost_usd_micros": 0,
        "gpu_seconds": 0,
    }
    for entry in entries:
        event_type = entry.get("event_type")
        event_branch = entry.get("branch_id")
        if event_type == "state_transition":
            raise SandboxRuntimeError("sandbox is already terminal")
        if event_type == "branch_opened":
            opened[require_id(event_branch, "opened branch id")] = entry
        elif event_type == "branch_finished":
            resolved_id = require_id(event_branch, "finished branch id")
            resolved.add(resolved_id)
            for field, value in receipt_usage(repo_root, entry).items():
                prior_usage[field] += value
        elif event_type == "branch_quarantined":
            raise SandboxRuntimeError("sandbox already contains a quarantine event")
    unfinished = set(opened) - resolved
    if unfinished != {branch_id}:
        raise SandboxRuntimeError(
            f"requested branch is not the sole unfinished branch: {sorted(unfinished)}"
        )
    branch_entry = opened[branch_id]
    cpu_seconds = require_nonnegative_integer(
        branch_entry.get("cpu_seconds"),
        f"branch {branch_id}.cpu_seconds",
    )
    output_bytes = require_nonnegative_integer(
        branch_entry.get("output_bytes"),
        f"branch {branch_id}.output_bytes",
    )
    charged_usage = {
        "cpu_seconds": cpu_seconds,
        "storage_bytes": output_bytes + SANDBOX_STDERR_LIMIT_BYTES,
        "monetary_cost_usd_micros": 0,
        "gpu_seconds": 0,
    }
    partition = require_mapping(manifest.get("partition"), f"sandbox {sandbox_id}.partition")
    return QuarantinePlan(
        repo_root=repo_root,
        base_ref=base_ref,
        sandbox_id=sandbox_id,
        branch_id=branch_id,
        ledger_path=ledger_path,
        artifact_root=artifact_root,
        branch_root=branch_root,
        incident_path=branch_root / "runtime_incident.json",
        result_path=artifact_root / "result.yaml",
        registry_path=repo_root / "research" / "discovery" / "sandbox_taint_registry.yaml",
        manifest_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        partition_sha256=require_sha256(partition.get("sha256"), "partition.sha256"),
        campaign_id=require_id(manifest.get("campaign_id"), "sandbox campaign_id"),
        charged_usage=charged_usage,
        prior_usage=prior_usage,
        branch_ids=sorted(opened),
    )


def container_name(sandbox_id: str, branch_id: str) -> str:
    return f"ecomd-dx-{sandbox_id}-{branch_id}"


def inspect_container(name: str) -> bool:
    try:
        completed = subprocess.run(
            ["docker", "container", "inspect", name],
            check=False,
            capture_output=True,
            timeout=DOCKER_CONTROL_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise SandboxRuntimeError("timed out inspecting the interrupted container") from exc
    if completed.returncode == 0:
        return True
    if completed.returncode == 1:
        return False
    raise SandboxRuntimeError("could not establish interrupted container state")


def cleanup_container(name: str) -> str:
    if not inspect_container(name):
        return "absent"
    try:
        completed = subprocess.run(
            ["docker", "rm", "-f", name],
            check=False,
            capture_output=True,
            timeout=DOCKER_CONTROL_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise SandboxRuntimeError("timed out removing the interrupted container") from exc
    if completed.returncode != 0 or inspect_container(name):
        raise SandboxRuntimeError("interrupted container could not be proven absent")
    return "removed"


def append_taint_registry(plan: QuarantinePlan, result_sha256: str) -> None:
    registry = dict(load_yaml(plan.registry_path, "sandbox taint registry"))
    raw_entries = registry.get("sandbox_results")
    if not isinstance(raw_entries, list):
        raise SandboxRuntimeError("sandbox taint registry entries are invalid")
    if any(
        isinstance(entry, dict) and entry.get("sandbox_id") == plan.sandbox_id
        for entry in raw_entries
    ):
        raise SandboxRuntimeError("sandbox already appears in the taint registry")
    raw_entries.append(
        {
            "id": f"{plan.sandbox_id}_result",
            "kind": "sandbox_result",
            "sandbox_id": plan.sandbox_id,
            "artifact_ref": plan.result_path.relative_to(plan.repo_root).as_posix(),
            "artifact_sha256": result_sha256,
            "derived_from": [],
            "epistemic_class": "sandbox_exploratory_tainted",
            "admissible_use": "screening_question_motivation_only",
        }
    )
    payload = yaml.safe_dump(registry, sort_keys=False, allow_unicode=True).encode("utf-8")
    atomic_replace_bytes(plan.registry_path, payload)


def execute_quarantine(
    plan: QuarantinePlan,
    reason_code: str,
    reason: str,
    operator: str,
) -> dict[str, object]:
    cleanup_status = cleanup_container(container_name(plan.sandbox_id, plan.branch_id))
    recorded_at = utc_now()
    occurred_at = timestamp(recorded_at)
    incident: dict[str, object] = {
        "schema_version": 1,
        "sandbox_id": plan.sandbox_id,
        "branch_id": plan.branch_id,
        "recorded_at": occurred_at,
        "reason_code": reason_code,
        "reason": reason,
        "outcome_exposure_assumed": True,
        "confirmation_accessed": False,
        "container_cleanup_status": cleanup_status,
        "charged_usage": plan.charged_usage,
        "operator": operator,
    }
    write_new_bytes(plan.incident_path, canonical_json_bytes(incident))
    quarantine_event = append_event(
        plan.ledger_path,
        {
            "event_type": "branch_quarantined",
            "occurred_at": occurred_at,
            "branch_id": plan.branch_id,
            "incident": canonical_artifact(
                plan.incident_path,
                plan.repo_root,
                include_bytes=False,
            ),
            "charged_usage": plan.charged_usage,
        },
    )
    usage = {
        field: plan.prior_usage[field] + plan.charged_usage[field]
        for field in plan.prior_usage
    }
    result: dict[str, object] = {
        "schema_version": 1,
        "sandbox_id": plan.sandbox_id,
        "campaign_id": plan.campaign_id,
        "created_at": occurred_at,
        "manifest_sha256": plan.manifest_sha256,
        "partition_sha256": plan.partition_sha256,
        "ledger_head_before_terminal_sha256": quarantine_event["entry_sha256"],
        "outcome_status": "quarantined",
        "taint": "sandbox_exploratory_tainted",
        "confirmation_accessed": False,
        "scientific_claim_support_allowed": False,
        "route_activation_allowed": False,
        "admissible_use": "screening_question_motivation_only",
        "branch_ids": plan.branch_ids,
        "usage": {**usage, "branches": len(plan.branch_ids)},
        "artifacts": [
            canonical_artifact(plan.incident_path, plan.repo_root, include_bytes=True)
        ],
        "summary": (
            "Sandbox quarantined after an ambiguous runtime interruption; all branch output "
            "is exploratory-tainted and the full ambiguous branch budget was charged."
        ),
    }
    result_payload = yaml.safe_dump(result, sort_keys=False, allow_unicode=True).encode("utf-8")
    write_new_bytes(plan.result_path, result_payload)
    result_sha256 = sha256_file(plan.result_path)
    append_event(
        plan.ledger_path,
        {
            "event_type": "state_transition",
            "occurred_at": occurred_at,
            "from_state": "authorized",
            "to_state": "quarantined",
            "reason": reason,
            "result": canonical_artifact(
                plan.result_path,
                plan.repo_root,
                include_bytes=False,
            ),
        },
    )
    append_taint_registry(plan, result_sha256)
    validate_discovery(plan.repo_root, base_ref=plan.base_ref)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Quarantine one interrupted Discovery sandbox and permanently taint it"
    )
    parser.add_argument("--sandbox-id", required=True)
    parser.add_argument("--branch-id", required=True)
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--reason-code", choices=sorted(REASON_CODES), required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--operator", required=True)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Remove any named container and append the irreversible quarantine records",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    try:
        sandbox_id = require_id(args.sandbox_id, "sandbox id")
        branch_id = require_id(args.branch_id, "branch id")
        base_ref = require_string(args.base_ref, "base ref")
        reason_code = require_string(args.reason_code, "reason code")
        reason = require_string(args.reason, "reason")
        operator = require_string(args.operator, "operator")
        with sandbox_lock("global_registry"), sandbox_lock(sandbox_id):
            plan = load_quarantine_plan(repo_root, sandbox_id, branch_id, base_ref)
            if not args.execute:
                print(
                    json.dumps(
                        {
                            "sandbox_id": sandbox_id,
                            "branch_id": branch_id,
                            "container_name": container_name(sandbox_id, branch_id),
                            "charged_usage": plan.charged_usage,
                            "action": "quarantine_dry_run_only",
                        },
                        sort_keys=True,
                    )
                )
                return 0
            result = execute_quarantine(plan, reason_code, reason, operator)
            print(json.dumps(result, sort_keys=True, ensure_ascii=False))
            return 0
    except (DiscoveryValidationError, SandboxRuntimeError, OSError, ValueError) as exc:
        print(f"Discovery sandbox quarantine REFUSED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
