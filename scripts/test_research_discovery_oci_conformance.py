#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_research_discovery_sandbox import (
    RuntimePlan,
    SandboxRuntimeError,
    capture_container,
    inspect_local_image,
)

PINNED_BASE_IMAGE = "python:3.11-slim-bookworm"
PINNED_BASE_IMAGE_ID = (
    "sha256:2e32f7d302adc1c37428355c1e646897c0c53f4fd60b6a551245fb90ee129f91"
)
RECORDED_REPORT_REF = (
    "research/discovery/conformance/local_colima_arm64_report_2026-09-12.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_command(argv: list[str], *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            argv,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise SandboxRuntimeError(f"command timed out: {argv[0]}") from exc


def inspect_image_id(reference: str) -> str:
    completed = run_command(
        ["docker", "image", "inspect", "--format", "{{.Id}}", reference],
        timeout=10,
    )
    if completed.returncode != 0:
        raise SandboxRuntimeError(f"local image is unavailable: {reference}")
    return completed.stdout.strip()


def build_probe_image(repo_root: Path, iid_file: Path) -> str:
    observed_base = inspect_image_id(PINNED_BASE_IMAGE)
    if observed_base != PINNED_BASE_IMAGE_ID:
        raise SandboxRuntimeError(
            f"base image ID mismatch: expected {PINNED_BASE_IMAGE_ID}, observed {observed_base}"
        )
    context = repo_root / "research" / "discovery" / "conformance"
    completed = run_command(
        [
            "docker",
            "build",
            "--pull=false",
            "--no-cache",
            "--network",
            "none",
            "--build-arg",
            f"BASE_IMAGE={PINNED_BASE_IMAGE_ID}",
            "--iidfile",
            str(iid_file),
            str(context),
        ]
    )
    if completed.returncode != 0:
        raise SandboxRuntimeError(f"probe image build failed: {completed.stderr.strip()}")
    image_id = iid_file.read_text(encoding="utf-8").strip()
    if not image_id.startswith("sha256:") or inspect_image_id(image_id) != image_id:
        raise SandboxRuntimeError("probe image did not resolve to one exact local image ID")
    return image_id


def make_plan(
    root: Path,
    image_id: str,
    case_id: str,
    *,
    mode: str,
    cpu_seconds: int,
    output_bytes: int,
) -> RuntimePlan:
    case_root = root / case_id
    config_path = case_root / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=False)
    config_path.write_text(
        json.dumps({"mode": mode}, separators=(",", ":"), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return RuntimePlan(
        repo_root=root,
        base_ref="conformance-only",
        sandbox_id=f"oci_{case_id}",
        branch_id="probe",
        ledger_path=case_root / "unused-events.jsonl",
        artifact_root=case_root / "artifacts",
        branch_root=case_root / "artifacts" / "branches" / "probe",
        request_path=case_root / "unused-request.yaml",
        config_path=config_path,
        image_digest=image_id,
        launcher_sha256="0" * 64,
        incident_handler_sha256="1" * 64,
        cpu_seconds=cpu_seconds,
        output_bytes=output_bytes,
        expires_at=datetime.now(UTC) + timedelta(minutes=5),
        request={},
        execution={},
    )


def read_probe_report(bundle_path: Path) -> dict[str, Any]:
    with tarfile.open(bundle_path, mode="r:") as archive:
        member = archive.getmember("conformance.json")
        extracted = archive.extractfile(member)
        if extracted is None:
            raise SandboxRuntimeError("probe report is absent from the tar bundle")
        value = json.loads(extracted.read())
    if not isinstance(value, dict):
        raise SandboxRuntimeError("probe report is not a mapping")
    return value


def validate_probe_report(report: dict[str, Any]) -> None:
    checks = report.get("checks")
    if report.get("schema_version") != 1 or report.get("passed") is not True:
        raise SandboxRuntimeError("OCI isolation probe reported a failed invariant")
    if not isinstance(checks, dict) or not checks or any(value is not True for value in checks.values()):
        raise SandboxRuntimeError("OCI isolation probe checks are incomplete or failed")


def validate_recorded_report(repo_root: Path) -> dict[str, Any]:
    report_path = repo_root / RECORDED_REPORT_REF
    value = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SandboxRuntimeError("recorded OCI report is not a mapping")
    report = dict(value)
    validate_probe_report(
        {
            "schema_version": report.get("schema_version"),
            "passed": report.get("passed"),
            "checks": report.get("isolation_checks"),
        }
    )
    expected_values = {
        "base_image": PINNED_BASE_IMAGE,
        "base_image_id": PINNED_BASE_IMAGE_ID,
        "probe_source_sha256": sha256_file(
            repo_root / "research/discovery/conformance/oci_probe.py"
        ),
        "dockerfile_sha256": sha256_file(
            repo_root / "research/discovery/conformance/Dockerfile"
        ),
        "launcher_sha256": sha256_file(
            repo_root / "scripts/run_research_discovery_sandbox.py"
        ),
        "incident_handler_sha256": sha256_file(
            repo_root / "scripts/quarantine_research_discovery_sandbox.py"
        ),
        "conformance_runner_sha256": sha256_file(Path(__file__)),
        "scientific_outcomes_accessed": False,
    }
    for field, expected in expected_values.items():
        if report.get(field) != expected:
            raise SandboxRuntimeError(f"recorded OCI report is stale at {field}")
    failure_checks = report.get("failure_mode_checks")
    if not isinstance(failure_checks, dict) or set(failure_checks) != {
        "invalid_tar_rejected",
        "stdout_limit_enforced",
        "wall_time_limit_enforced",
    }:
        raise SandboxRuntimeError("recorded OCI failure-mode checks are incomplete")
    if any(check is not True for check in failure_checks.values()):
        raise SandboxRuntimeError("recorded OCI failure-mode check failed")
    probe_image_id = report.get("probe_image_id")
    if not isinstance(probe_image_id, str) or not probe_image_id.startswith("sha256:"):
        raise SandboxRuntimeError("recorded OCI probe image ID is invalid")
    return report


def remove_image(image_id: str) -> None:
    run_command(["docker", "image", "rm", image_id], timeout=30)


def run_conformance(repo_root: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=".oci-conformance-", dir=repo_root) as raw_root:
        root = Path(raw_root)
        image_id = ""
        try:
            image_id = build_probe_image(repo_root, root / "image.id")
            normal = make_plan(
                root,
                image_id,
                "normal",
                mode="normal",
                cpu_seconds=120,
                output_bytes=262_144,
            )
            inspect_local_image(normal)
            normal_status, normal_exit, _, _, normal_artifacts = capture_container(normal)
            bundle_path = next(
                path for path in normal_artifacts if path.name == "bundle.tar"
            )
            probe_report = read_probe_report(bundle_path)
            validate_probe_report(probe_report)
            if normal_status != "completed" or normal_exit != 0:
                raise SandboxRuntimeError("normal OCI conformance case did not complete")

            output_limited = make_plan(
                root,
                image_id,
                "output_limit",
                mode="normal",
                cpu_seconds=120,
                output_bytes=128,
            )
            output_status, _, _, _, _ = capture_container(output_limited)
            if output_status != "output_limit":
                raise SandboxRuntimeError("stdout byte limit did not fail closed")

            invalid_tar = make_plan(
                root,
                image_id,
                "invalid_tar",
                mode="invalid_tar",
                cpu_seconds=120,
                output_bytes=262_144,
            )
            invalid_status, _, _, _, _ = capture_container(invalid_tar)
            if invalid_status != "container_failed":
                raise SandboxRuntimeError("invalid tar output did not fail closed")

            timed_out = make_plan(
                root,
                image_id,
                "timeout",
                mode="sleep",
                cpu_seconds=1,
                output_bytes=262_144,
            )
            timeout_status, _, _, _, _ = capture_container(timed_out)
            if timeout_status != "timeout":
                raise SandboxRuntimeError("wall-time limit did not fail closed")

            return {
                "schema_version": 1,
                "probe": "ecomd_discovery_oci_runtime",
                "passed": True,
                "tested_at": datetime.now(UTC).isoformat(timespec="seconds").replace(
                    "+00:00", "Z"
                ),
                "host_machine": "local_colima_arm64",
                "base_image": PINNED_BASE_IMAGE,
                "base_image_id": PINNED_BASE_IMAGE_ID,
                "probe_image_id": image_id,
                "probe_source_sha256": sha256_file(
                    repo_root / "research/discovery/conformance/oci_probe.py"
                ),
                "dockerfile_sha256": sha256_file(
                    repo_root / "research/discovery/conformance/Dockerfile"
                ),
                "launcher_sha256": sha256_file(
                    repo_root / "scripts/run_research_discovery_sandbox.py"
                ),
                "incident_handler_sha256": sha256_file(
                    repo_root / "scripts/quarantine_research_discovery_sandbox.py"
                ),
                "conformance_runner_sha256": sha256_file(Path(__file__)),
                "isolation_checks": probe_report["checks"],
                "failure_mode_checks": {
                    "invalid_tar_rejected": True,
                    "stdout_limit_enforced": True,
                    "wall_time_limit_enforced": True,
                },
                "observed": probe_report["observed"],
                "scientific_outcomes_accessed": False,
            }
        finally:
            if image_id:
                remove_image(image_id)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build and execute the outcome-free Discovery OCI isolation probe"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Build and run the local probe; omission only describes the pinned base",
    )
    parser.add_argument(
        "--verify-recorded-report",
        action="store_true",
        help="Verify that the committed report matches the current runtime sources",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    try:
        if args.execute and args.verify_recorded_report:
            raise SandboxRuntimeError("choose either execution or recorded-report verification")
        if args.verify_recorded_report:
            report = validate_recorded_report(repo_root)
            print(
                json.dumps(
                    {
                        "action": "recorded_conformance_report_verified",
                        "probe_image_id": report["probe_image_id"],
                        "tested_at": report["tested_at"],
                    },
                    sort_keys=True,
                )
            )
            return 0
        if not args.execute:
            print(
                json.dumps(
                    {
                        "action": "conformance_dry_run_only",
                        "base_image": PINNED_BASE_IMAGE,
                        "base_image_id": PINNED_BASE_IMAGE_ID,
                    },
                    sort_keys=True,
                )
            )
            return 0
        print(json.dumps(run_conformance(repo_root), sort_keys=True))
        return 0
    except (OSError, SandboxRuntimeError, ValueError) as exc:
        print(f"Discovery OCI conformance REFUSED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
