from __future__ import annotations

import io
import tarfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from scripts.run_research_discovery_sandbox import (
    RuntimePlan,
    SandboxRuntimeError,
    build_docker_command,
    validate_tar_bundle,
)


def make_plan(tmp_path: Path) -> RuntimePlan:
    tmp_path.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "config.yaml"
    config_path.write_text("unit_ids:\n  - unit_a\n", encoding="utf-8")
    return RuntimePlan(
        repo_root=tmp_path,
        base_ref="origin/research-base",
        sandbox_id="sandbox_one",
        branch_id="branch_one",
        ledger_path=tmp_path / "events.jsonl",
        artifact_root=tmp_path / "artifacts",
        branch_root=tmp_path / "artifacts" / "branches" / "branch_one",
        request_path=tmp_path / "request.yaml",
        config_path=config_path,
        image_digest=f"sha256:{'1' * 64}",
        launcher_sha256="2" * 64,
        incident_handler_sha256="3" * 64,
        cpu_seconds=120,
        output_bytes=1_000_000,
        expires_at=datetime(2026, 8, 26, tzinfo=UTC),
        request={},
        execution={},
    )


def test_docker_command_is_fixed_and_has_only_one_read_only_file_mount(tmp_path: Path) -> None:
    plan = make_plan(tmp_path)
    command = build_docker_command(plan)

    assert command[:2] == ["docker", "run"]
    assert command[-1] == plan.image_digest
    assert command.count("--mount") == 1
    mount_index = command.index("--mount")
    assert command[mount_index + 1] == (
        f"type=bind,src={plan.config_path.resolve()},"
        "dst=/sandbox/config.yaml,readonly"
    )
    for required_pair in (
        ("--pull", "never"),
        ("--network", "none"),
        ("--cap-drop", "ALL"),
        ("--security-opt", "no-new-privileges"),
        ("--cpus", "1"),
        ("--user", "65534:65534"),
        ("--log-driver", "none"),
    ):
        index = command.index(required_pair[0])
        assert command[index + 1] == required_pair[1]
    assert "--read-only" in command
    assert "--gpus" not in command
    assert "/var/run/docker.sock" not in " ".join(command)


def test_docker_command_rejects_ambiguous_bind_source(tmp_path: Path) -> None:
    plan = make_plan(tmp_path / "comma,path")

    with pytest.raises(SandboxRuntimeError, match="cannot contain a comma"):
        build_docker_command(plan)


def test_tar_bundle_accepts_only_uncompressed_regular_tree(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle.tar"
    payload = b'{"screening":"exploratory_only"}\n'
    with tarfile.open(bundle, mode="w") as archive:
        directory = tarfile.TarInfo("artifacts")
        directory.type = tarfile.DIRTYPE
        archive.addfile(directory)
        member = tarfile.TarInfo("artifacts/summary.json")
        member.size = len(payload)
        archive.addfile(member, io.BytesIO(payload))

    validate_tar_bundle(bundle)


@pytest.mark.parametrize("unsafe_kind", ["traversal", "symlink", "compressed"])
def test_tar_bundle_rejects_unsafe_or_compressed_output(
    tmp_path: Path,
    unsafe_kind: str,
) -> None:
    bundle = tmp_path / "bundle.tar"
    if unsafe_kind == "compressed":
        with tarfile.open(bundle, mode="w:gz") as archive:
            member = tarfile.TarInfo("summary.txt")
            member.size = 1
            archive.addfile(member, io.BytesIO(b"x"))
    else:
        with tarfile.open(bundle, mode="w") as archive:
            if unsafe_kind == "traversal":
                member = tarfile.TarInfo("../escape.txt")
                member.size = 1
                archive.addfile(member, io.BytesIO(b"x"))
            else:
                member = tarfile.TarInfo("link")
                member.type = tarfile.SYMTYPE
                member.linkname = "summary.txt"
                archive.addfile(member)

    with pytest.raises(SandboxRuntimeError):
        validate_tar_bundle(bundle)
