from __future__ import annotations

from dataclasses import replace
from typing import Any

import pytest

from ecomd.data.github_verification_liquidity import (
    DependabotConfigSummary,
    PullRequestEvent,
    RepositoryFrameEntry,
    RepositorySupport,
    assert_outcome_blind_payload,
    canonical_json_sha256,
    count_arrival_clusters,
    evaluate_dminus1_support,
    sanitize_pull_request_node,
    sanitize_repository,
    sanitize_workflow_job,
    sanitize_workflow_run,
    summarize_dependabot_config,
)


def _repository(index: int = 1) -> RepositoryFrameEntry:
    return RepositoryFrameEntry(
        id=index,
        node_id=f"R_{index}",
        full_name=f"owner/repo-{index}",
        created_at="2020-01-01T00:00:00Z",
        archived=False,
        fork=False,
        stargazers_count=10_000 - index,
        default_branch="main",
        frame_rank=index,
    )


def _config(treatment_class: str = "default_treated") -> DependabotConfigSummary:
    return DependabotConfigSummary(
        commit_sha="a" * 40,
        commit_timestamp="2026-01-01T00:00:00Z",
        content_sha256="b" * 64,
        parse_status="ok",
        treatment_class=treatment_class,
        schedule_schema=(),
        grouping_present=False,
    )


def _event(number: int, day: int) -> PullRequestEvent:
    return PullRequestEvent(
        id=f"PR_{number}",
        number=number,
        created_at=f"2026-06-{day:02d}T00:00:00Z",
        actor_class="dependabot",
    )


def _support(
    index: int,
    *,
    treatment: str = "default_treated",
    bot_events: tuple[PullRequestEvent, ...] = (),
    human_prs: int | None = 10,
) -> RepositorySupport:
    job = sanitize_workflow_job(
        {"id": 1000 + index, "labels": ["ubuntu-latest"], "started_at": "sealed"},
        run_id=2000 + index,
    )
    return RepositorySupport(
        repository=_repository(index),
        config=_config(treatment),
        workflow_paths=(".github/workflows/ci.yml",),
        bot_pull_requests=bot_events,
        human_pull_request_count=human_prs,
        workflow_schema_access=True,
        job_schemas=(job,),
    )


def test_repository_sanitizer_selects_only_allowed_fields() -> None:
    raw: dict[str, Any] = {
        "id": 1,
        "node_id": "R_1",
        "full_name": "owner/repo",
        "created_at": "2020-01-01T00:00:00Z",
        "updated_at": "sealed",
        "archived": False,
        "fork": False,
        "stargazers_count": 1234,
        "default_branch": "main",
    }
    sanitized = sanitize_repository(raw, frame_rank=1).allowed_payload()
    assert "updated_at" not in sanitized
    assert sanitized["full_name"] == "owner/repo"


@pytest.mark.parametrize(
    ("cooldown", "expected"),
    [
        ("", "default_treated"),
        ("\n    cooldown:\n      default-days: 0", "opt_out"),
        ("\n    cooldown:\n      default-days: 7", "already_cooled"),
    ],
)
def test_dependabot_config_treatment_classes(cooldown: str, expected: str) -> None:
    content = f"""version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly{cooldown}
"""
    summary = summarize_dependabot_config(
        content,
        commit_sha="a" * 40,
        commit_timestamp="2026-01-01T00:00:00Z",
    )
    assert summary.parse_status == "ok"
    assert summary.treatment_class == expected


def test_dependabot_config_mixed_entries_are_ambiguous() -> None:
    content = """version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule: {interval: weekly}
  - package-ecosystem: pip
    directory: /
    schedule: {interval: monthly}
    cooldown: {default-days: 7}
"""
    summary = summarize_dependabot_config(
        content,
        commit_sha="a" * 40,
        commit_timestamp="2026-01-01T00:00:00Z",
    )
    assert summary.treatment_class == "ambiguous"
    assert summary.parse_status == "mixed_or_invalid_cooldown"


def test_absent_cutoff_config_is_a_control() -> None:
    summary = summarize_dependabot_config(
        None,
        commit_sha=None,
        commit_timestamp=None,
    )
    assert summary.treatment_class == "no_dependabot_control"
    assert summary.parse_status == "no_path_commit_before_cutoff"


def test_pr_and_workflow_sanitizers_never_persist_outcomes() -> None:
    event = sanitize_pull_request_node(
        {
            "id": "PR_1",
            "number": 5,
            "createdAt": "2026-06-01T00:00:00Z",
            "author": {"login": "dependabot[bot]"},
            "mergedAt": "sealed",
        },
        dependabot_login="dependabot[bot]",
    )
    run = sanitize_workflow_run(
        {
            "id": 9,
            "created_at": "2026-06-01T00:00:00Z",
            "run_started_at": "sealed",
            "conclusion": "sealed",
            "actor": {"login": "human"},
            "event": "pull_request",
            "path": ".github/workflows/ci.yml@main",
            "head_sha": "c" * 40,
            "pull_requests": [{"id": 88, "number": 4}],
        },
        dependabot_login="dependabot[bot]",
    )
    job = sanitize_workflow_job(
        {
            "id": 10,
            "labels": ["ubuntu-latest"],
            "started_at": "sealed",
            "completed_at": "sealed",
            "conclusion": "sealed",
        },
        run_id=9,
    )
    payload = {"event": event.allowed_payload(), "run": run.allowed_payload(), "job": job.allowed_payload()}
    assert_outcome_blind_payload(payload)
    encoded = str(payload)
    assert "sealed" not in encoded
    assert job.required_field_presence["job_start_present"] is True


def test_outcome_guard_fails_closed() -> None:
    with pytest.raises(ValueError, match="forbidden persisted outcome key"):
        assert_outcome_blind_payload({"safe": {"started_at": "2026-01-01"}})


def test_cluster_count_uses_frozen_consecutive_gap() -> None:
    times = [
        "2026-06-01T00:00:00Z",
        "2026-06-01T00:30:00Z",
        "2026-06-02T00:30:00Z",
        "2026-06-04T00:30:00Z",
    ]
    assert count_arrival_clusters(times, gap_hours=24) == 3


def test_canonical_hash_is_order_stable() -> None:
    assert canonical_json_sha256({"a": 1, "b": 2}) == canonical_json_sha256({"b": 2, "a": 1})


def test_support_evaluator_can_pass_and_fail_without_outcomes() -> None:
    gates = {
        "minimum_unique_frame_repositories": 2,
        "minimum_default_treated_with_actions": 1,
        "minimum_high_support_default_treated": 1,
        "minimum_pre_event_dependabot_pull_requests": 2,
        "minimum_pre_event_24h_clusters": 2,
        "minimum_eligible_no_dependabot_controls": 1,
        "minimum_historical_config_recovery_rate": 0.9,
        "minimum_workflow_run_access_rate": 0.9,
        "minimum_required_queue_field_presence_rate": 0.9,
        "require_no_forbidden_persisted_field": True,
        "require_deterministic_derived_summary_hash": True,
    }
    treated = _support(1, bot_events=(_event(1, 1), _event(2, 3)))
    control = replace(
        _support(2, treatment="no_dependabot_control"),
        config=summarize_dependabot_config(
            None,
            commit_sha=None,
            commit_timestamp=None,
        ),
    )
    green = evaluate_dminus1_support(
        [treated, control],
        gates=gates,
        minimum_bot_prs_for_high_support_repository=2,
        cluster_gap_hours=24,
        deterministic_summary_hash_matches=True,
    )
    assert green["scientific_decision"] == "green_freeze_d0_before_opening_queue_outcomes"
    assert all(green["gates"].values())

    red = evaluate_dminus1_support(
        [treated],
        gates=gates,
        minimum_bot_prs_for_high_support_repository=2,
        cluster_gap_hours=24,
        deterministic_summary_hash_matches=True,
    )
    assert red["scientific_decision"].startswith("red_stop")
