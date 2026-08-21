from __future__ import annotations

import base64
import json
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from ecomd.data.github_verification_liquidity_d0 import (
    MATCHING_COVARIATES,
    D0RepositoryIdentityRecord,
    D0SchemaProbe,
    D0WorkflowJobSchema,
    D0WorkflowRunIdentity,
    RepositoryMatchFeatures,
    deterministic_probe_runs,
    evaluate_d0_identity_prerequisites,
    evaluate_d0_support,
    finalize_d1_run_identities,
    normalize_workflow_path,
    optimal_repository_match,
    parse_utc,
    repository_has_shared_pool,
    repository_record_from_payload,
    repository_runner_pool_class,
    sanitize_d0_workflow_job,
    sanitize_d0_workflow_run,
    select_d1_run_identities,
    selected_workflow_structure_key,
    summarize_workflow_structure,
)
from scripts.audit_github_dependabot_cooldown_d0 import (
    _acquire_selected_primary_structures,
    _sanitize_status_incident,
    _smoke_raw_directory,
)


def _run(
    run_id: int,
    created_at: str,
    *,
    actor_class: str = "user",
    event_type: str = "push",
    attempt: int = 1,
) -> D0WorkflowRunIdentity:
    return D0WorkflowRunIdentity(
        run_id=run_id,
        workflow_id=10,
        run_number=run_id,
        run_attempt=attempt,
        created_at=created_at,
        actor_class=actor_class,
        event_type=event_type,
        workflow_path=".github/workflows/ci.yml@main",
        head_sha=f"{run_id:040x}",
        head_branch="main",
        pull_request_ids=(),
        check_suite_id=run_id + 100,
    )


def _job(run_id: int, job_id: int, labels: tuple[str, ...]) -> D0WorkflowJobSchema:
    return D0WorkflowJobSchema(
        run_id=run_id,
        job_id=job_id,
        job_name="test",
        runner_labels=labels,
        required_field_presence={"job_start_present": True, "job_completion_present": True},
    )


def _features(repository_id: int, cohort: str, offset: float) -> RepositoryMatchFeatures:
    return RepositoryMatchFeatures(
        repository_id=repository_id,
        full_name=f"owner/repo-{repository_id}",
        cohort=cohort,
        runner_pool_class="nonself_hosted_observed",
        values={name: float(index) + offset for index, name in enumerate(MATCHING_COVARIATES)},
        pre_primary_human_run_count=10,
        successful_human_schema_probe=True,
    )


def test_d0_run_and_job_sanitizers_drop_all_timing_and_status_values() -> None:
    raw_run: dict[str, Any] = {
        "id": 1,
        "workflow_id": 2,
        "run_number": 3,
        "run_attempt": 1,
        "check_suite_id": 4,
        "created_at": "2026-07-01T00:00:00Z",
        "run_started_at": "2026-07-01T00:01:00Z",
        "updated_at": "2026-07-01T00:02:00Z",
        "status": "completed",
        "conclusion": "success",
        "actor": {"login": "alice", "type": "User"},
        "event": "push",
        "path": ".github/workflows/ci.yml@main",
        "head_sha": "a" * 40,
        "head_branch": "main",
        "pull_requests": [{"id": 9}],
    }
    run = sanitize_d0_workflow_run(raw_run, dependabot_login="dependabot[bot]")
    assert run.actor_class == "user"
    assert run.pull_request_ids == (9,)
    assert set(run.allowed_payload()) == {
        "run_id",
        "workflow_id",
        "run_number",
        "run_attempt",
        "created_at",
        "actor_class",
        "event_type",
        "workflow_path",
        "head_sha",
        "head_branch",
        "pull_request_ids",
        "check_suite_id",
    }

    raw_job = {
        "id": 7,
        "name": "test",
        "labels": ["ubuntu-latest", "ubuntu-latest"],
        "started_at": "2026-07-01T00:03:00Z",
        "completed_at": "2026-07-01T00:04:00Z",
        "status": "completed",
        "conclusion": "success",
        "steps": [{"started_at": "sealed"}],
    }
    job = sanitize_d0_workflow_job(raw_job, run_id=run.run_id)
    assert job.runner_labels == ("ubuntu-latest",)
    assert job.required_field_presence == {
        "job_start_present": True,
        "job_completion_present": True,
    }
    assert "started_at" not in str(job.allowed_payload())


def test_external_incident_times_use_contract_names_without_weakening_the_seal() -> None:
    payload = {
        "incident": {
            "id": "incident-1",
            "name": "Actions jobs delayed",
            "started_at": "2026-07-01T00:00:00Z",
            "resolved_at": "2026-07-01T01:00:00Z",
            "incident_updates": [
                {
                    "body": "Actions queues recovered",
                    "affected_components": [{"name": "Actions"}],
                }
            ],
        }
    }
    row = _sanitize_status_incident(
        payload,
        response_sha256="a" * 64,
        lower=parse_utc("2026-06-16T00:00:00Z"),
        upper=parse_utc("2026-08-13T23:59:59Z"),
    )
    assert row is not None
    assert row["reported_start_utc"] == "2026-07-01T00:00:00Z"
    assert row["reported_resolution_utc"] == "2026-07-01T01:00:00Z"
    assert "started_at" not in row
    assert "resolved_at" not in row


def test_smoke_resume_accepts_only_an_incomplete_immediate_child(tmp_path: Path) -> None:
    root = tmp_path / "smokes"
    child = root / "frozen-smoke"
    child.mkdir(parents=True)
    runtime = {"smoke": {"output_directory": str(root)}}
    assert _smoke_raw_directory(runtime, child) == child
    outside = tmp_path / "outside"
    outside.mkdir()
    with pytest.raises(ValueError, match="immediate child"):
        _smoke_raw_directory(runtime, outside)
    (child / "smoke_result.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(FileExistsError, match="final artifact"):
        _smoke_raw_directory(runtime, child)


def test_empty_matching_support_is_strict_json_with_null_balance_metrics() -> None:
    import yaml

    config_path = (
        Path(__file__).resolve().parents[1] / "configs/agent_markets/github_dependabot_cooldown_d0_v3.yaml"
    )
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    support = evaluate_d0_support(
        [],
        [],
        {"matching_complete": False},
        [],
        gates=config["gates"],
        minimum_primary_runs=int(config["prequalification"]["minimum_primary_human_run_identities"]),
        maximum_absolute_smd=float(config["matching"]["maximum_absolute_standardized_mean_difference"]),
        maximum_mean_smd=float(config["matching"]["maximum_mean_absolute_standardized_mean_difference"]),
        deterministic_hash_matches=True,
        candidate_hashes_exact=True,
    )
    assert support["metrics"]["maximum_absolute_standardized_mean_difference"] is None
    assert support["metrics"]["mean_absolute_standardized_mean_difference"] is None
    json.dumps(support, allow_nan=False)


def test_final_sample_excludes_unknown_and_intentional_primary_waits() -> None:
    clean = summarize_workflow_structure("jobs:\n  test:\n    runs-on: ubuntu-latest\n")
    waiting = summarize_workflow_structure(
        "concurrency: one-at-a-time\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
    )
    assert clean is not None
    assert waiting is not None
    rows = [
        {
            "repository_id": 42,
            "sample_class": "primary",
            "period": "primary_pre",
            "run": _run(1, "2026-07-01T00:00:00Z").allowed_payload(),
        },
        {
            "repository_id": 42,
            "sample_class": "primary",
            "period": "primary_pre",
            "run": _run(2, "2026-07-01T01:00:00Z").allowed_payload(),
        },
        {
            "repository_id": 42,
            "sample_class": "primary",
            "period": "primary_pre",
            "run": _run(3, "2026-07-01T02:00:00Z").allowed_payload(),
        },
        {
            "repository_id": 42,
            "sample_class": "secondary",
            "period": "primary_pre",
            "run": _run(4, "2026-07-01T03:00:00Z", event_type="pull_request").allowed_payload(),
        },
    ]
    structures = {
        selected_workflow_structure_key(rows[0]): clean,
        selected_workflow_structure_key(rows[1]): waiting,
        selected_workflow_structure_key(rows[2]): None,
    }
    selected, metrics = finalize_d1_run_identities(rows, structures)
    assert [row["run"]["run_id"] for row in selected] == [1, 4]
    assert selected[0]["workflow_structure"]["intentional_wait_flags"] == ()
    assert metrics == {
        "provisional_primary_runs": 3,
        "primary_workflow_structures_recovered": 2,
        "primary_runs_excluded_missing_structure": 1,
        "primary_runs_excluded_intentional_wait": 1,
        "primary_workflow_structure_recovery_rate": 2 / 3,
        "final_selected_runs": 2,
    }


def test_selected_structure_acquisition_is_checkpointed_and_resumable(tmp_path: Path) -> None:
    run = _run(1, "2026-07-01T00:00:00Z")
    record = D0RepositoryIdentityRecord(
        repository_id=42,
        full_name="owner/repo",
        cohort="default_treated_high_support",
        run_api_access=True,
        unresolved_truncation_count=0,
        conflicting_duplicate_run_ids=0,
        runs=(run,),
        schema_probes=(),
    )
    row = {
        "repository_id": 42,
        "sample_class": "primary",
        "period": "primary_pre",
        "run": run.allowed_payload(),
    }
    content = "jobs:\n  test:\n    runs-on: ubuntu-latest\n"

    class FakeClient:
        def __init__(self) -> None:
            self.calls = 0

        def request_json(self, *_: Any, **__: Any) -> dict[str, str]:
            self.calls += 1
            return {
                "encoding": "base64",
                "content": base64.b64encode(content.encode()).decode(),
            }

    client = FakeClient()
    runtime = {
        "execution": {
            "selected_workflow_structure_checkpoint_directory": "structure-checkpoints",
            "workflow_content_maximum_bytes": 1000,
            "progress_interval_seconds": 60.0,
        }
    }
    first = _acquire_selected_primary_structures(
        client,  # type: ignore[arg-type]
        [row],
        {42: record},
        runtime,
        raw_directory=tmp_path,
        maximum_workers=1,
        started=time.monotonic(),
    )
    second = _acquire_selected_primary_structures(
        client,  # type: ignore[arg-type]
        [row],
        {42: record},
        runtime,
        raw_directory=tmp_path,
        maximum_workers=1,
        started=time.monotonic(),
    )
    assert first == second
    assert client.calls == 1
    assert first[selected_workflow_structure_key(row)] is not None


def test_identity_prerequisite_uses_conservative_upper_bounds() -> None:
    supported_runs = tuple(_run(index, f"2026-07-{index:02d}T00:00:00Z") for index in range(1, 6))

    def record(
        repository_id: int,
        cohort: str,
        *,
        access: bool,
        runs: tuple[D0WorkflowRunIdentity, ...],
    ) -> D0RepositoryIdentityRecord:
        return D0RepositoryIdentityRecord(
            repository_id=repository_id,
            full_name=f"owner/repo-{repository_id}",
            cohort=cohort,
            run_api_access=access,
            unresolved_truncation_count=0,
            conflicting_duplicate_run_ids=0,
            runs=runs,
            schema_probes=(),
        )

    records = [
        record(1, "default_treated_high_support", access=True, runs=supported_runs),
        record(2, "no_dependabot_candidate_controls", access=True, runs=supported_runs),
        record(3, "no_dependabot_candidate_controls", access=False, runs=()),
    ]
    windows = {
        "primary_pre_from_utc": "2026-06-16T00:00:00Z",
        "primary_pre_to_utc": "2026-07-13T23:59:59Z",
    }
    gates = {
        "minimum_repository_run_api_access_rate": 0.5,
        "maximum_unresolved_truncated_run_queries": 0,
        "maximum_conflicting_duplicate_run_ids": 0,
        "minimum_prequalified_treated_repositories": 1,
        "minimum_prequalified_control_candidates": 2,
    }
    result = evaluate_d0_identity_prerequisites(
        records,
        windows=windows,
        minimum_primary_runs=5,
        gates=gates,
    )
    assert result["exact_complete_repository_primary_support"] == {
        "default_treated_high_support": 1,
        "no_dependabot_candidate_controls": 1,
    }
    assert result["prequalification_upper_bounds"] == {
        "default_treated_high_support": 1,
        "no_dependabot_candidate_controls": 2,
    }
    assert result["probe_stage_authorized"] is True


def test_workflow_structure_flags_intentional_waits_without_persisting_yaml() -> None:
    content = """
name: CI
concurrency: build-${{ github.ref }}
jobs:
  root:
    runs-on: [self-hosted, linux]
    environment: production
    steps: []
  downstream:
    needs: root
    runs-on: ubuntu-latest
    steps: []
"""
    summary = summarize_workflow_structure(content)
    assert summary is not None
    assert summary.root_job_keys == ("root",)
    assert summary.intentional_wait_flags == (
        "workflow_level_concurrency",
        "root_job_environment",
    )
    assert summary.runs_on_schema == ({"job_key": "root", "runs_on": ["self-hosted", "linux"]},)
    assert normalize_workflow_path(".github/workflows/ci.yml@refs/heads/main") == (".github/workflows/ci.yml")


def test_probe_selection_runner_class_and_checkpoint_roundtrip_are_deterministic() -> None:
    runs = (
        _run(1, "2026-07-01T00:00:00Z"),
        _run(2, "2026-07-02T00:00:00Z"),
        _run(3, "2026-07-03T00:00:00Z", actor_class="dependabot", event_type="pull_request"),
        _run(4, "2026-07-04T00:00:00Z", actor_class="dependabot", event_type="pull_request"),
    )
    record = D0RepositoryIdentityRecord(
        repository_id=42,
        full_name="owner/repo",
        cohort="default_treated_high_support",
        run_api_access=True,
        unresolved_truncation_count=0,
        conflicting_duplicate_run_ids=0,
        runs=runs,
        schema_probes=(),
    )
    first = deterministic_probe_runs(
        record,
        pre_from_utc="2026-06-16T00:00:00Z",
        pre_to_utc="2026-07-13T23:59:59Z",
        per_actor_class=1,
    )
    assert first == deterministic_probe_runs(
        record,
        pre_from_utc="2026-06-16T00:00:00Z",
        pre_to_utc="2026-07-13T23:59:59Z",
        per_actor_class=1,
    )
    human_run = next(run for actor, run in first if actor == "human")
    bot_run = next(run for actor, run in first if actor == "dependabot")
    structure = summarize_workflow_structure("jobs:\n  test:\n    runs-on: ubuntu-latest\n")
    probes = (
        D0SchemaProbe(
            human_run.run_id, "human", True, (_job(human_run.run_id, 1, ("ubuntu-latest",)),), structure
        ),
        D0SchemaProbe(
            bot_run.run_id, "dependabot", True, (_job(bot_run.run_id, 2, ("ubuntu-latest",)),), structure
        ),
    )
    probed = replace(record, schema_probes=probes)
    assert repository_runner_pool_class(probed) == "nonself_hosted_observed"
    assert repository_has_shared_pool(probed) is True
    assert repository_record_from_payload(probed.allowed_payload()) == probed


def test_optimal_matching_is_complete_distinct_and_deterministic() -> None:
    treated = [
        _features(1, "default_treated_high_support", 0.00),
        _features(2, "default_treated_high_support", 0.10),
    ]
    controls = [
        _features(10, "no_dependabot_candidate_controls", 0.01),
        _features(11, "no_dependabot_candidate_controls", 0.02),
        _features(12, "no_dependabot_candidate_controls", 0.11),
        _features(13, "no_dependabot_candidate_controls", 0.12),
    ]
    first = optimal_repository_match(
        treated,
        controls,
        ratio=2,
        minimum_treated=2,
        maximum_scaled_primary_difference=2.0,
    )
    second = optimal_repository_match(
        treated,
        controls,
        ratio=2,
        minimum_treated=2,
        maximum_scaled_primary_difference=2.0,
    )
    assert first == second
    assert first["matching_complete"] is True
    assert first["matched_treated_repository_ids"] == [1, 2]
    assert len(first["matched_control_repository_ids"]) == 4
    assert len(set(first["matched_control_repository_ids"])) == 4
    assert len(first["pairs"]) == 4


def test_d1_identity_sampling_uses_only_user_first_attempts_and_frozen_windows() -> None:
    runs = (
        _run(1, "2026-06-20T00:00:00Z"),
        _run(2, "2026-06-20T01:00:00Z"),
        _run(3, "2026-06-20T02:00:00Z"),
        _run(4, "2026-07-14T02:00:00Z"),
        _run(5, "2026-07-20T00:00:00Z"),
        _run(6, "2026-07-20T01:00:00Z", attempt=2),
        _run(7, "2026-07-21T00:00:00Z", actor_class="dependabot"),
        _run(8, "2026-05-25T00:00:00Z", event_type="pull_request"),
    )
    record = D0RepositoryIdentityRecord(
        repository_id=42,
        full_name="owner/repo",
        cohort="default_treated_high_support",
        run_api_access=True,
        unresolved_truncation_count=0,
        conflicting_duplicate_run_ids=0,
        runs=runs,
        schema_probes=(),
    )
    windows = {
        "extended_pre_from_utc": "2026-05-19T00:00:00Z",
        "primary_pre_from_utc": "2026-06-16T00:00:00Z",
        "primary_pre_to_utc": "2026-07-13T23:59:59Z",
        "primary_post_from_utc": "2026-07-17T00:00:00Z",
        "primary_post_to_utc": "2026-08-13T23:59:59Z",
    }
    selected = select_d1_run_identities(
        [record],
        included_repository_ids={42},
        windows=windows,
        primary_events={"push"},
        secondary_events={"pull_request", "pull_request_target", "workflow_dispatch"},
        primary_daily_cap=2,
        secondary_daily_cap=1,
    )
    selected_ids = {row["run"]["run_id"] for row in selected}
    assert len(selected_ids.intersection({1, 2, 3})) == 2
    assert 5 in selected_ids
    assert 8 in selected_ids
    assert not selected_ids.intersection({4, 6, 7})
    assert {row["period"] for row in selected} == {"extended_pre", "primary_pre", "primary_post"}
