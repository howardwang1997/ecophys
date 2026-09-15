from __future__ import annotations

import hashlib
import io
import subprocess
import tarfile
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from scripts import run_research_discovery_sandbox as runtime
from scripts.run_research_discovery_sandbox import (
    RUNTIME_OVERHEAD_BYTES,
    STDERR_LIMIT_BYTES,
    RuntimePlan,
    SandboxRuntimeError,
    anchor_record,
    append_anchor_record,
    build_docker_command,
    enforce_anchor,
    existing_usage,
    load_anchor_records,
    validate_tar_bundle,
)


def make_plan(tmp_path: Path) -> RuntimePlan:
    tmp_path.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "config.yaml"
    config_bytes = b"unit_ids:\n  - unit_a\n"
    config_path.write_bytes(config_bytes)
    return RuntimePlan(
        repo_root=tmp_path,
        base_ref="origin/research-base",
        base_commit="a" * 64,
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
        request={
            "config": {
                "ref": "config.yaml",
                "sha256": hashlib.sha256(config_bytes).hexdigest(),
            }
        },
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
    assert command[command.index("--ulimit") + 1] == "cpu=120:120"


@pytest.mark.parametrize("status,elapsed", [("timeout", 125), ("output_limit", 20), ("container_failed", 20), ("completed", 125)])
def test_failed_or_over_budget_branch_stays_unfinished(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, status: str, elapsed: int,
) -> None:
    monkeypatch.setattr(runtime, "ANCHOR_ROOT", tmp_path / "anchors")
    plan = replace(make_plan(tmp_path), expires_at=datetime(2099, 1, 1, tzinfo=UTC))
    plan.request_path.write_text("{}\n")
    events: list[dict[str, object]] = []

    def append(path: Path, payload: dict[str, object]) -> dict[str, object]:
        appended = dict(payload)
        appended["seq"] = len(events)
        appended["entry_sha256"] = f"{len(events):064d}"
        events.append(appended)
        return appended

    monkeypatch.setattr(runtime, "append_event", append)
    monkeypatch.setattr(runtime, "inspect_local_image", lambda plan: None)
    monkeypatch.setattr(runtime, "capture_container", lambda plan: (status, 0, elapsed, 0, []))
    with pytest.raises(SandboxRuntimeError, match="leave it unfinished and quarantine"):
        runtime.execute_plan(plan)
    assert [event["event_type"] for event in events] == ["branch_opened"]
    assert not (plan.branch_root / "receipt.json").exists()


def test_execute_plan_refuses_swapped_config_before_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = make_plan(tmp_path)
    plan.config_path.write_bytes(b"unit_ids:\n  - confirmation_unit\n")
    monkeypatch.setattr(runtime, "inspect_local_image", lambda plan: None)
    monkeypatch.setattr(
        runtime, "append_event", lambda *args, **kwargs: pytest.fail("branch_opened must not be appended")
    )
    with pytest.raises(SandboxRuntimeError, match="no longer matches its authorized digest"):
        runtime.execute_plan(plan)


def test_execute_plan_refuses_config_swap_between_open_and_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runtime, "ANCHOR_ROOT", tmp_path / "anchors")
    plan = replace(make_plan(tmp_path), expires_at=datetime(2099, 1, 1, tzinfo=UTC))
    plan.request_path.write_text("{}\n")
    events: list[dict[str, object]] = []

    def append(path: Path, payload: dict[str, object]) -> dict[str, object]:
        appended = dict(payload)
        appended["seq"] = len(events)
        appended["entry_sha256"] = f"{len(events):064d}"
        events.append(appended)
        plan.config_path.write_bytes(b"unit_ids:\n  - swapped\n")
        return appended

    monkeypatch.setattr(runtime, "append_event", append)
    monkeypatch.setattr(runtime, "inspect_local_image", lambda plan: None)
    with pytest.raises(SandboxRuntimeError, match="changed between authorization and container start"):
        runtime.execute_plan(plan)


def test_execute_plan_refuses_config_swap_during_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runtime, "ANCHOR_ROOT", tmp_path / "anchors")
    plan = replace(make_plan(tmp_path), expires_at=datetime(2099, 1, 1, tzinfo=UTC))
    plan.request_path.write_text("{}\n")
    events: list[dict[str, object]] = []

    def append(path: Path, payload: dict[str, object]) -> dict[str, object]:
        appended = dict(payload)
        appended["seq"] = len(events)
        appended["entry_sha256"] = f"{len(events):064d}"
        events.append(appended)
        return appended

    def capture(plan: RuntimePlan) -> tuple[str, int, int, int, list[Path]]:
        plan.config_path.write_bytes(b"unit_ids:\n  - swapped_during_run\n")
        return "completed", 0, 10, 0, []

    monkeypatch.setattr(runtime, "append_event", append)
    monkeypatch.setattr(runtime, "inspect_local_image", lambda plan: None)
    monkeypatch.setattr(runtime, "capture_container", capture)
    with pytest.raises(SandboxRuntimeError, match="changed during execution"):
        runtime.execute_plan(plan)
    assert not (plan.branch_root / "receipt.json").exists()


def test_daemon_failure_is_not_container_absence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: subprocess.CompletedProcess([], 1, "", "daemon unavailable"))
    with pytest.raises(SandboxRuntimeError, match="absence is unproven"):
        runtime.container_exists("owned-container")


def test_container_absence_uses_successful_exact_name_query(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: subprocess.CompletedProcess([], 0, "owned-container-other\n", ""))
    assert runtime.container_exists("owned-container") is False
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: subprocess.CompletedProcess([], 0, "owned-container\n", ""))
    assert runtime.container_exists("owned-container") is True


def test_cleanup_rejects_surviving_container(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: subprocess.CompletedProcess([], 0, "", ""))
    monkeypatch.setattr(runtime, "container_exists", lambda name: True)
    with pytest.raises(SandboxRuntimeError, match="remains after cleanup"):
        runtime.remove_container(make_plan(tmp_path))


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


def anchor_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[str, str, list[dict[str, object]]]:
    monkeypatch.setattr(runtime, "ANCHOR_ROOT", tmp_path / "anchors")
    sandbox_id = "anchor_sandbox"
    base_commit = "f" * 64
    entries = [
        {"event_type": "authorized", "seq": 0, "entry_sha256": "0" * 64},
        {"event_type": "branch_opened", "seq": 1, "entry_sha256": "1" * 64},
    ]
    for event in entries:
        append_anchor_record(
            sandbox_id,
            anchor_record("origin/research-base", base_commit, event, terminal=False),
        )
    return sandbox_id, base_commit, entries


def test_anchor_round_trip_accepts_a_matching_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    sandbox_id, base_commit, entries = anchor_fixture(tmp_path, monkeypatch)
    assert len(load_anchor_records(sandbox_id)) == 2
    enforce_anchor(sandbox_id, entries, base_commit)


def test_anchor_refuses_erased_or_rewritten_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    sandbox_id, base_commit, _ = anchor_fixture(tmp_path, monkeypatch)
    with pytest.raises(SandboxRuntimeError, match="diverges from its out-of-tree anchor"):
        enforce_anchor(sandbox_id, [], base_commit)
    rewritten = [
        {"event_type": "authorized", "seq": 0, "entry_sha256": "0" * 64},
        {"event_type": "branch_opened", "seq": 1, "entry_sha256": "e" * 64},
    ]
    with pytest.raises(SandboxRuntimeError, match="diverges from its out-of-tree anchor"):
        enforce_anchor(sandbox_id, rewritten, base_commit)


def test_anchor_refuses_terminal_and_rotated_base(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    sandbox_id, base_commit, entries = anchor_fixture(tmp_path, monkeypatch)
    append_anchor_record(
        sandbox_id,
        anchor_record(
            "origin/research-base",
            base_commit,
            {"seq": 2, "entry_sha256": "2" * 64},
            terminal=True,
        ),
    )
    grown = [*entries, {"event_type": "state_transition", "seq": 2, "entry_sha256": "2" * 64}]
    with pytest.raises(SandboxRuntimeError, match="terminal according to its out-of-tree anchor"):
        enforce_anchor(sandbox_id, grown, base_commit)
    fresh_id, _, fresh_entries = anchor_fixture(tmp_path / "fresh", monkeypatch)
    with pytest.raises(SandboxRuntimeError, match="protected base commit changed"):
        enforce_anchor(fresh_id, fresh_entries, "b" * 64)


def test_anchor_refuses_corrupted_chain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    sandbox_id, _, _ = anchor_fixture(tmp_path, monkeypatch)
    path = tmp_path / "anchors" / f"{sandbox_id}.jsonl"
    lines = path.read_bytes().splitlines()
    assert b'"terminal":false' in lines[0]
    lines[0] = lines[0].replace(b'"terminal":false', b'"terminal":true')
    path.write_bytes(b"\n".join(lines) + b"\n")
    with pytest.raises(SandboxRuntimeError, match="anchor chain is broken"):
        load_anchor_records(sandbox_id)


def test_existing_usage_refuses_receipt_that_left_its_ledger_digest(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_bytes(b'{"cpu_seconds": 10, "storage_bytes": 5}')
    entries: list[dict[str, object]] = [
        {"event_type": "branch_opened", "branch_id": "branch_one"},
        {
            "event_type": "branch_finished",
            "branch_id": "branch_one",
            "receipt": {"ref": "receipt.json", "sha256": "0" * 64},
        },
    ]
    with pytest.raises(SandboxRuntimeError, match="no longer matches its ledger digest"):
        existing_usage(tmp_path, entries)


def test_runtime_overhead_reserves_room_beyond_stderr_limit() -> None:
    assert RUNTIME_OVERHEAD_BYTES > STDERR_LIMIT_BYTES


def test_sandbox_lock_is_exclusive_and_lives_outside_tmp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runtime, "ANCHOR_ROOT", tmp_path / "anchors")
    with runtime.sandbox_lock("locked_sandbox"):
        assert (tmp_path / "anchors" / "locks" / "locked_sandbox.lock").is_file()
        with pytest.raises(SandboxRuntimeError, match="already has a running launcher"), runtime.sandbox_lock(
            "locked_sandbox"
        ):
            pass
