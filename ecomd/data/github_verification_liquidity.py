"""Outcome-blind schemas and support gates for GitHub verification liquidity."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime
from itertools import pairwise
from typing import Any

import yaml

FORBIDDEN_PERSISTED_KEYS = frozenset(
    {
        "run_started_at",
        "updated_at",
        "started_at",
        "completed_at",
        "status",
        "conclusion",
        "closed_at",
        "merged_at",
        "reviewed_at",
        "duration",
        "queue_wait",
        "release_age",
        "vulnerability",
    }
)


def _mapping(value: Any, *, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _sequence(value: Any, *, label: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{label} must be an array")
    return value


def canonical_json_sha256(payload: Any) -> str:
    """Hash a JSON-compatible payload using canonical separators and key order."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def assert_outcome_blind_payload(payload: Any) -> None:
    """Reject persisted output that contains a sealed outcome key at any depth."""
    if isinstance(payload, Mapping):
        for raw_key, value in payload.items():
            key = str(raw_key).lower()
            if key in FORBIDDEN_PERSISTED_KEYS:
                raise ValueError(f"forbidden persisted outcome key: {key}")
            assert_outcome_blind_payload(value)
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        for value in payload:
            assert_outcome_blind_payload(value)


@dataclass(frozen=True)
class RepositoryFrameEntry:
    """Allowed repository identity and frame-selection metadata."""

    id: int
    node_id: str
    full_name: str
    created_at: str
    archived: bool
    fork: bool
    stargazers_count: int
    default_branch: str
    frame_rank: int

    def allowed_payload(self) -> dict[str, Any]:
        """Return the contract-approved persisted representation."""
        payload = asdict(self)
        assert_outcome_blind_payload(payload)
        return payload


def sanitize_repository(payload: Mapping[str, Any], *, frame_rank: int) -> RepositoryFrameEntry:
    """Select only repository fields permitted by the D-1 contract."""
    if frame_rank <= 0:
        raise ValueError("frame rank must be positive")
    repository_id = payload.get("id")
    stars = payload.get("stargazers_count")
    if isinstance(repository_id, bool) or not isinstance(repository_id, int):
        raise ValueError("repository ID must be an integer")
    if isinstance(stars, bool) or not isinstance(stars, int) or stars < 0:
        raise ValueError("repository star count must be a nonnegative integer")
    archived = payload.get("archived")
    fork = payload.get("fork")
    if not isinstance(archived, bool) or not isinstance(fork, bool):
        raise ValueError("repository archived/fork fields must be Boolean")
    entry = RepositoryFrameEntry(
        id=repository_id,
        node_id=str(payload.get("node_id", "")),
        full_name=str(payload.get("full_name", "")),
        created_at=str(payload.get("created_at", "")),
        archived=archived,
        fork=fork,
        stargazers_count=stars,
        default_branch=str(payload.get("default_branch", "")),
        frame_rank=frame_rank,
    )
    if not entry.node_id or "/" not in entry.full_name or not entry.default_branch:
        raise ValueError("repository identity fields are incomplete")
    return entry


@dataclass(frozen=True)
class DependabotConfigSummary:
    """Historical Dependabot treatment schema without downstream outcomes."""

    commit_sha: str | None
    commit_timestamp: str | None
    content_sha256: str | None
    parse_status: str
    treatment_class: str
    schedule_schema: tuple[dict[str, str | bool | None], ...]
    grouping_present: bool | None

    def allowed_payload(self) -> dict[str, Any]:
        """Return the contract-approved persisted representation."""
        payload = asdict(self)
        assert_outcome_blind_payload(payload)
        return payload


def _cooldown_mode(update: Mapping[str, Any]) -> str:
    cooldown = update.get("cooldown")
    if cooldown is None:
        return "default"
    if not isinstance(cooldown, Mapping):
        return "invalid"
    days = cooldown.get("default-days")
    if days is None:
        return "default"
    if isinstance(days, bool) or not isinstance(days, int) or days < 0:
        return "invalid"
    return "zero" if days == 0 else "positive"


def summarize_dependabot_config(
    content: str | None,
    *,
    commit_sha: str | None,
    commit_timestamp: str | None,
    known_absent_at_cutoff: bool = False,
) -> DependabotConfigSummary:
    """Parse a cutoff configuration and classify exposure to the new default."""
    if content is None:
        status = "known_absent_at_cutoff" if known_absent_at_cutoff else "no_path_commit_before_cutoff"
        return DependabotConfigSummary(
            commit_sha=commit_sha,
            commit_timestamp=commit_timestamp,
            content_sha256=None,
            parse_status=status,
            treatment_class="no_dependabot_control",
            schedule_schema=(),
            grouping_present=None,
        )
    digest = hashlib.sha256(content.encode()).hexdigest()
    try:
        root = yaml.safe_load(content)
    except yaml.YAMLError:
        root = None
    if not isinstance(root, Mapping):
        return DependabotConfigSummary(
            commit_sha=commit_sha,
            commit_timestamp=commit_timestamp,
            content_sha256=digest,
            parse_status="invalid_yaml_root",
            treatment_class="ambiguous",
            schedule_schema=(),
            grouping_present=None,
        )
    raw_updates = root.get("updates")
    if not isinstance(raw_updates, Sequence) or isinstance(raw_updates, (str, bytes)):
        return DependabotConfigSummary(
            commit_sha=commit_sha,
            commit_timestamp=commit_timestamp,
            content_sha256=digest,
            parse_status="invalid_updates",
            treatment_class="ambiguous",
            schedule_schema=(),
            grouping_present=None,
        )
    schedules: list[dict[str, str | bool | None]] = []
    cooldown_modes: list[str] = []
    grouping_present = False
    for raw_update in raw_updates:
        if not isinstance(raw_update, Mapping):
            return DependabotConfigSummary(
                commit_sha=commit_sha,
                commit_timestamp=commit_timestamp,
                content_sha256=digest,
                parse_status="invalid_update_entry",
                treatment_class="ambiguous",
                schedule_schema=(),
                grouping_present=None,
            )
        schedule = raw_update.get("schedule")
        schedule_map = schedule if isinstance(schedule, Mapping) else {}
        mode = _cooldown_mode(raw_update)
        cooldown_modes.append(mode)
        has_groups = isinstance(raw_update.get("groups"), Mapping) and bool(raw_update.get("groups"))
        grouping_present = grouping_present or has_groups
        schedules.append(
            {
                "package_ecosystem": str(raw_update.get("package-ecosystem", "")),
                "interval": str(schedule_map.get("interval", "")),
                "day": str(schedule_map["day"]) if "day" in schedule_map else None,
                "time": str(schedule_map["time"]) if "time" in schedule_map else None,
                "timezone": str(schedule_map["timezone"]) if "timezone" in schedule_map else None,
                "cooldown_mode": mode,
                "groups_present": has_groups,
            }
        )
    if not cooldown_modes:
        treatment_class = "ambiguous"
        parse_status = "no_update_entries"
    elif set(cooldown_modes) == {"default"}:
        treatment_class = "default_treated"
        parse_status = "ok"
    elif set(cooldown_modes) == {"zero"}:
        treatment_class = "opt_out"
        parse_status = "ok"
    elif set(cooldown_modes) == {"positive"}:
        treatment_class = "already_cooled"
        parse_status = "ok"
    else:
        treatment_class = "ambiguous"
        parse_status = "mixed_or_invalid_cooldown"
    return DependabotConfigSummary(
        commit_sha=commit_sha,
        commit_timestamp=commit_timestamp,
        content_sha256=digest,
        parse_status=parse_status,
        treatment_class=treatment_class,
        schedule_schema=tuple(schedules),
        grouping_present=grouping_present,
    )


@dataclass(frozen=True)
class PullRequestEvent:
    """Outcome-blind PR identity and arrival timestamp."""

    id: str
    number: int
    created_at: str
    actor_class: str

    def allowed_payload(self) -> dict[str, Any]:
        """Return the contract-approved persisted representation."""
        payload = asdict(self)
        assert_outcome_blind_payload(payload)
        return payload


def sanitize_pull_request_node(payload: Mapping[str, Any], *, dependabot_login: str) -> PullRequestEvent:
    """Select PR identity, actor class and creation time from a GraphQL node."""
    number = payload.get("number")
    if isinstance(number, bool) or not isinstance(number, int) or number <= 0:
        raise ValueError("pull request number must be positive")
    actor = payload.get("author")
    login = str(actor.get("login", "")) if isinstance(actor, Mapping) else ""
    return PullRequestEvent(
        id=str(payload.get("id", "")),
        number=number,
        created_at=str(payload.get("createdAt", "")),
        actor_class="dependabot" if login.lower() == dependabot_login.lower() else "other",
    )


def count_arrival_clusters(timestamps: Sequence[str], *, gap_hours: float) -> int:
    """Count clusters separated by at least the frozen consecutive-event gap."""
    if gap_hours <= 0:
        raise ValueError("cluster gap must be positive")
    parsed = sorted(datetime.fromisoformat(value.replace("Z", "+00:00")) for value in timestamps)
    if not parsed:
        return 0
    threshold_seconds = gap_hours * 3600.0
    clusters = 1
    for previous, current in pairwise(parsed):
        if (current - previous).total_seconds() >= threshold_seconds:
            clusters += 1
    return clusters


@dataclass(frozen=True)
class WorkflowRunSchema:
    """Allowed workflow-run identity fields; all timing outcomes are omitted."""

    id: int
    created_at: str
    actor_class: str
    event_type: str
    workflow_path: str
    head_sha: str
    pull_request_ids: tuple[int, ...]

    def allowed_payload(self) -> dict[str, Any]:
        """Return the contract-approved persisted representation."""
        payload = asdict(self)
        assert_outcome_blind_payload(payload)
        return payload


def sanitize_workflow_run(payload: Mapping[str, Any], *, dependabot_login: str) -> WorkflowRunSchema:
    """Discard workflow timing/status outcomes while retaining linkage schema."""
    run_id = payload.get("id")
    if isinstance(run_id, bool) or not isinstance(run_id, int):
        raise ValueError("workflow run ID must be an integer")
    actor = payload.get("actor")
    login = str(actor.get("login", "")) if isinstance(actor, Mapping) else ""
    raw_prs = payload.get("pull_requests", [])
    prs = _sequence(raw_prs, label="workflow pull_requests")
    pr_ids: list[int] = []
    for raw_pr in prs:
        pr = _mapping(raw_pr, label="workflow pull request")
        pr_id = pr.get("id", pr.get("number"))
        if isinstance(pr_id, int) and not isinstance(pr_id, bool):
            pr_ids.append(pr_id)
    return WorkflowRunSchema(
        id=run_id,
        created_at=str(payload.get("created_at", "")),
        actor_class="dependabot" if login.lower() == dependabot_login.lower() else "other",
        event_type=str(payload.get("event", "")),
        workflow_path=str(payload.get("path", "")),
        head_sha=str(payload.get("head_sha", "")),
        pull_request_ids=tuple(sorted(set(pr_ids))),
    )


@dataclass(frozen=True)
class WorkflowJobSchema:
    """Allowed job identity, runner labels and sealed-field missingness."""

    run_id: int
    job_id: int
    runner_labels: tuple[str, ...]
    required_field_presence: dict[str, bool]

    def allowed_payload(self) -> dict[str, Any]:
        """Return the contract-approved persisted representation."""
        payload = asdict(self)
        assert_outcome_blind_payload(payload)
        return payload


def sanitize_workflow_job(payload: Mapping[str, Any], *, run_id: int) -> WorkflowJobSchema:
    """Retain only job labels and Boolean presence of sealed queue fields."""
    job_id = payload.get("id")
    if isinstance(job_id, bool) or not isinstance(job_id, int):
        raise ValueError("workflow job ID must be an integer")
    labels = tuple(sorted(str(value) for value in _sequence(payload.get("labels", []), label="job labels")))
    return WorkflowJobSchema(
        run_id=run_id,
        job_id=job_id,
        runner_labels=labels,
        required_field_presence={
            "run_created_at_present": True,
            "job_start_present": payload.get("started_at") is not None,
        },
    )


@dataclass(frozen=True)
class RepositorySupport:
    """One repository's outcome-blind support record for gate evaluation."""

    repository: RepositoryFrameEntry
    config: DependabotConfigSummary
    workflow_paths: tuple[str, ...]
    bot_pull_requests: tuple[PullRequestEvent, ...]
    human_pull_request_count: int | None
    workflow_schema_access: bool | None
    job_schemas: tuple[WorkflowJobSchema, ...]

    def allowed_payload(self) -> dict[str, Any]:
        """Return a JSON-compatible contract-approved representation."""
        payload = {
            "repository": self.repository.allowed_payload(),
            "configuration": self.config.allowed_payload(),
            "workflow_paths": list(self.workflow_paths),
            "bot_pull_requests": [event.allowed_payload() for event in self.bot_pull_requests],
            "human_pull_request_count": self.human_pull_request_count,
            "workflow_schema_access": self.workflow_schema_access,
            "job_schemas": [schema.allowed_payload() for schema in self.job_schemas],
        }
        assert_outcome_blind_payload(payload)
        return payload


def evaluate_dminus1_support(
    records: Sequence[RepositorySupport],
    *,
    gates: Mapping[str, Any],
    minimum_bot_prs_for_high_support_repository: int,
    cluster_gap_hours: float,
    deterministic_summary_hash_matches: bool,
) -> dict[str, Any]:
    """Apply the frozen D-1 scale, transport and outcome-seal gates."""
    unique_ids = {record.repository.id for record in records}
    default_treated = [
        record
        for record in records
        if record.config.treatment_class == "default_treated" and bool(record.workflow_paths)
    ]
    high_support = [
        record
        for record in default_treated
        if len(record.bot_pull_requests) >= minimum_bot_prs_for_high_support_repository
    ]
    bot_pull_requests = sum(len(record.bot_pull_requests) for record in records)
    clusters = sum(
        count_arrival_clusters(
            [event.created_at for event in record.bot_pull_requests],
            gap_hours=cluster_gap_hours,
        )
        for record in records
    )
    controls = [
        record
        for record in records
        if record.config.treatment_class == "no_dependabot_control"
        and bool(record.workflow_paths)
        and record.human_pull_request_count is not None
        and record.human_pull_request_count > 0
        and not record.bot_pull_requests
    ]
    config_denominator = sum(record.config.commit_sha is not None for record in records)
    config_recovered = sum(
        record.config.commit_sha is not None and record.config.parse_status in {"ok", "known_absent_at_cutoff"}
        for record in records
    )
    config_recovery_rate = config_recovered / config_denominator if config_denominator else 1.0
    workflow_probes = [record for record in records if record.workflow_schema_access is not None]
    workflow_access_rate = (
        sum(record.workflow_schema_access is True for record in workflow_probes) / len(workflow_probes)
        if workflow_probes
        else 0.0
    )
    jobs = [job for record in records for job in record.job_schemas]
    field_presence_rate = (
        sum(job.required_field_presence.get("job_start_present") is True for job in jobs) / len(jobs)
        if jobs
        else 0.0
    )
    persisted_payload = [record.allowed_payload() for record in records]
    no_forbidden = True
    try:
        assert_outcome_blind_payload(persisted_payload)
    except ValueError:
        no_forbidden = False
    metrics: dict[str, int | float | bool] = {
        "unique_frame_repositories": len(unique_ids),
        "default_treated_with_actions": len(default_treated),
        "high_support_default_treated": len(high_support),
        "pre_event_dependabot_pull_requests": bot_pull_requests,
        "pre_event_clusters": clusters,
        "eligible_no_dependabot_controls": len(controls),
        "historical_config_recovery_rate": config_recovery_rate,
        "workflow_run_access_rate": workflow_access_rate,
        "required_queue_field_presence_rate": field_presence_rate,
        "no_forbidden_persisted_field": no_forbidden,
        "deterministic_derived_summary_hash": deterministic_summary_hash_matches,
    }
    gate_results = {
        "frame": len(unique_ids) >= int(gates["minimum_unique_frame_repositories"]),
        "default_treated": len(default_treated) >= int(gates["minimum_default_treated_with_actions"]),
        "high_support": len(high_support) >= int(gates["minimum_high_support_default_treated"]),
        "bot_prs": bot_pull_requests >= int(gates["minimum_pre_event_dependabot_pull_requests"]),
        "clusters": clusters >= int(gates["minimum_pre_event_24h_clusters"]),
        "controls": len(controls) >= int(gates["minimum_eligible_no_dependabot_controls"]),
        "config_recovery": config_recovery_rate >= float(gates["minimum_historical_config_recovery_rate"]),
        "workflow_access": workflow_access_rate >= float(gates["minimum_workflow_run_access_rate"]),
        "queue_field_presence": field_presence_rate
        >= float(gates["minimum_required_queue_field_presence_rate"]),
        "outcome_seal": no_forbidden and bool(gates["require_no_forbidden_persisted_field"]),
        "deterministic_hash": deterministic_summary_hash_matches
        and bool(gates["require_deterministic_derived_summary_hash"]),
    }
    if all(gate_results.values()):
        decision = "green_freeze_d0_before_opening_queue_outcomes"
    elif all(value for key, value in gate_results.items() if key != "controls"):
        decision = "amber_narrow_control_claim_before_d0"
    else:
        decision = "red_stop_before_queue_outcomes_model_gpu_or_window_rescue"
    return {"metrics": metrics, "gates": gate_results, "scientific_decision": decision}
