"""Outcome-blind D0 schemas, matching and support logic for verification liquidity."""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any, cast

import numpy as np
import yaml
from scipy.optimize import linear_sum_assignment

from ecomd.data.github_verification_liquidity import (
    assert_outcome_blind_payload,
    canonical_json_sha256,
)


def _mapping(value: Any, *, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _sequence(value: Any, *, label: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{label} must be an array")
    return value


def _nonnegative_int(value: Any, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a nonnegative integer")
    return cast(int, value)


def parse_utc(value: str) -> datetime:
    """Parse a timezone-aware ISO timestamp."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp is not timezone aware: {value}")
    return parsed.astimezone(UTC)


def normalize_workflow_path(value: str) -> str:
    """Remove the API's optional @ref suffix from a workflow path."""
    path = value.split("@", 1)[0]
    if not path or path.startswith("/") or ".." in path.split("/"):
        raise ValueError(f"unsafe workflow path: {value}")
    return path


@dataclass(frozen=True)
class D0WorkflowRunIdentity:
    """A workflow-run identity with every timing/status outcome removed."""

    run_id: int
    workflow_id: int
    run_number: int
    run_attempt: int
    created_at: str
    actor_class: str
    event_type: str
    workflow_path: str
    head_sha: str
    head_branch: str | None
    pull_request_ids: tuple[int, ...]
    check_suite_id: int

    def allowed_payload(self) -> dict[str, Any]:
        """Return the contract-approved persisted representation."""
        payload = asdict(self)
        assert_outcome_blind_payload(payload)
        return payload


def sanitize_d0_workflow_run(payload: Mapping[str, Any], *, dependabot_login: str) -> D0WorkflowRunIdentity:
    """Sanitize a GitHub workflow-run response before any persistence."""
    run_id = _nonnegative_int(payload.get("id"), label="workflow run id")
    workflow_id = _nonnegative_int(payload.get("workflow_id"), label="workflow run workflow_id")
    run_number = _nonnegative_int(payload.get("run_number"), label="workflow run run_number")
    run_attempt = _nonnegative_int(payload.get("run_attempt"), label="workflow run run_attempt")
    check_suite_id = _nonnegative_int(payload.get("check_suite_id"), label="workflow run check_suite_id")
    actor = payload.get("actor")
    actor_map = actor if isinstance(actor, Mapping) else {}
    actor_login = str(actor_map.get("login", ""))
    actor_type = str(actor_map.get("type", ""))
    if actor_login.lower() == dependabot_login.lower():
        actor_class = "dependabot"
    elif actor_type == "User":
        actor_class = "user"
    elif actor_type in {"Bot", "App"}:
        actor_class = "other_bot"
    else:
        actor_class = "other"
    raw_pull_requests = _sequence(payload.get("pull_requests", []), label="run pull requests")
    pull_request_ids: list[int] = []
    for raw in raw_pull_requests:
        pull_request = _mapping(raw, label="run pull request")
        value = pull_request.get("id", pull_request.get("number"))
        if isinstance(value, int) and not isinstance(value, bool):
            pull_request_ids.append(value)
    head_branch = payload.get("head_branch")
    if head_branch is not None and not isinstance(head_branch, str):
        raise ValueError("workflow run head_branch must be a string or null")
    run = D0WorkflowRunIdentity(
        run_id=run_id,
        workflow_id=workflow_id,
        run_number=run_number,
        run_attempt=run_attempt,
        created_at=str(payload.get("created_at", "")),
        actor_class=actor_class,
        event_type=str(payload.get("event", "")),
        workflow_path=str(payload.get("path", "")),
        head_sha=str(payload.get("head_sha", "")),
        head_branch=head_branch,
        pull_request_ids=tuple(sorted(set(pull_request_ids))),
        check_suite_id=check_suite_id,
    )
    parse_utc(run.created_at)
    if not run.workflow_path or not run.head_sha:
        raise ValueError("workflow run path and head SHA are required")
    return run


@dataclass(frozen=True)
class D0WorkflowJobSchema:
    """A job identity and runner-label schema with timing values sealed."""

    run_id: int
    job_id: int
    job_name: str
    runner_labels: tuple[str, ...]
    required_field_presence: dict[str, bool]

    def allowed_payload(self) -> dict[str, Any]:
        """Return the contract-approved persisted representation."""
        payload = asdict(self)
        assert_outcome_blind_payload(payload)
        return payload


def sanitize_d0_workflow_job(payload: Mapping[str, Any], *, run_id: int) -> D0WorkflowJobSchema:
    """Sanitize a GitHub workflow-job response before any persistence."""
    job_id = payload.get("id")
    if isinstance(job_id, bool) or not isinstance(job_id, int) or job_id < 0:
        raise ValueError("workflow job ID must be a nonnegative integer")
    labels = tuple(
        sorted(
            {str(value) for value in _sequence(payload.get("labels", []), label="job labels") if str(value)}
        )
    )
    job = D0WorkflowJobSchema(
        run_id=run_id,
        job_id=job_id,
        job_name=str(payload.get("name", "")),
        runner_labels=labels,
        required_field_presence={
            "job_start_present": payload.get("started_at") is not None,
            "job_completion_present": payload.get("completed_at") is not None,
        },
    )
    if not job.job_name:
        raise ValueError("workflow job name is required")
    return job


def canonical_runner_label_set(labels: Sequence[str]) -> tuple[str, ...]:
    """Canonicalize a runner label set for exact within-repository overlap."""
    return tuple(sorted({str(value) for value in labels if str(value)}))


@dataclass(frozen=True)
class WorkflowStructureSummary:
    """Outcome-free workflow structure relevant to intentional waiting."""

    content_sha256: str
    root_job_keys: tuple[str, ...]
    runs_on_schema: tuple[dict[str, Any], ...]
    intentional_wait_flags: tuple[str, ...]

    def allowed_payload(self) -> dict[str, Any]:
        """Return the contract-approved persisted representation."""
        payload = asdict(self)
        assert_outcome_blind_payload(payload)
        return payload


def workflow_structure_from_payload(payload: Mapping[str, Any]) -> WorkflowStructureSummary:
    """Restore a sanitized workflow-structure summary."""
    summary = WorkflowStructureSummary(
        content_sha256=str(payload["content_sha256"]),
        root_job_keys=tuple(str(value) for value in payload["root_job_keys"]),
        runs_on_schema=tuple(dict(_mapping(value, label="runs-on")) for value in payload["runs_on_schema"]),
        intentional_wait_flags=tuple(str(value) for value in payload["intentional_wait_flags"]),
    )
    assert_outcome_blind_payload(summary.allowed_payload())
    return summary


def _json_compatible(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {
            str(key): _json_compatible(item) for key, item in sorted(value.items(), key=lambda x: str(x[0]))
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_json_compatible(item) for item in value]
    return str(value)


def summarize_workflow_structure(content: str) -> WorkflowStructureSummary | None:
    """Parse only root-job, runner and intentional-wait structure from workflow YAML."""
    digest = hashlib.sha256(content.encode()).hexdigest()
    try:
        root = yaml.safe_load(content)
    except yaml.YAMLError:
        return None
    if not isinstance(root, Mapping):
        return None
    jobs = root.get("jobs")
    if not isinstance(jobs, Mapping) or not jobs:
        return None
    workflow_concurrency = root.get("concurrency") not in (None, "", {}, [])
    root_jobs: list[str] = []
    runs_on: list[dict[str, Any]] = []
    root_concurrency = False
    root_environment = False
    for raw_key, raw_job in sorted(jobs.items(), key=lambda item: str(item[0])):
        if not isinstance(raw_job, Mapping):
            return None
        job_key = str(raw_key)
        needs = raw_job.get("needs")
        is_root = needs in (None, "", [], ())
        if not is_root:
            continue
        root_jobs.append(job_key)
        root_concurrency = root_concurrency or raw_job.get("concurrency") not in (None, "", {}, [])
        root_environment = root_environment or raw_job.get("environment") not in (None, "", {}, [])
        runs_on.append({"job_key": job_key, "runs_on": _json_compatible(raw_job.get("runs-on"))})
    if not root_jobs:
        return None
    flags: list[str] = []
    if workflow_concurrency:
        flags.append("workflow_level_concurrency")
    if root_concurrency:
        flags.append("root_job_concurrency")
    if root_environment:
        flags.append("root_job_environment")
    summary = WorkflowStructureSummary(
        content_sha256=digest,
        root_job_keys=tuple(root_jobs),
        runs_on_schema=tuple(runs_on),
        intentional_wait_flags=tuple(flags),
    )
    assert_outcome_blind_payload(summary.allowed_payload())
    return summary


@dataclass(frozen=True)
class D0SchemaProbe:
    """Outcome-blind job/workflow probe for one selected pre-period run."""

    run_id: int
    actor_class: str
    job_api_access: bool
    jobs: tuple[D0WorkflowJobSchema, ...]
    workflow_structure: WorkflowStructureSummary | None

    def allowed_payload(self) -> dict[str, Any]:
        """Return the contract-approved persisted representation."""
        payload = {
            "run_id": self.run_id,
            "actor_class": self.actor_class,
            "job_api_access": self.job_api_access,
            "jobs": [job.allowed_payload() for job in self.jobs],
            "workflow_structure": (
                self.workflow_structure.allowed_payload() if self.workflow_structure is not None else None
            ),
        }
        assert_outcome_blind_payload(payload)
        return payload


@dataclass(frozen=True)
class D0RepositoryIdentityRecord:
    """All allowed D0 identity data for a frozen candidate repository."""

    repository_id: int
    full_name: str
    cohort: str
    run_api_access: bool
    unresolved_truncation_count: int
    conflicting_duplicate_run_ids: int
    runs: tuple[D0WorkflowRunIdentity, ...]
    schema_probes: tuple[D0SchemaProbe, ...]

    def allowed_payload(self) -> dict[str, Any]:
        """Return the contract-approved persisted representation."""
        payload = {
            "repository_id": self.repository_id,
            "full_name": self.full_name,
            "cohort": self.cohort,
            "run_api_access": self.run_api_access,
            "unresolved_truncation_count": self.unresolved_truncation_count,
            "conflicting_duplicate_run_ids": self.conflicting_duplicate_run_ids,
            "runs": [run.allowed_payload() for run in self.runs],
            "schema_probes": [probe.allowed_payload() for probe in self.schema_probes],
        }
        assert_outcome_blind_payload(payload)
        return payload


def repository_record_from_payload(payload: Mapping[str, Any]) -> D0RepositoryIdentityRecord:
    """Restore a sanitized repository checkpoint."""
    runs = tuple(
        D0WorkflowRunIdentity(
            run_id=int(_mapping(raw, label="run")["run_id"]),
            workflow_id=int(_mapping(raw, label="run")["workflow_id"]),
            run_number=int(_mapping(raw, label="run")["run_number"]),
            run_attempt=int(_mapping(raw, label="run")["run_attempt"]),
            created_at=str(_mapping(raw, label="run")["created_at"]),
            actor_class=str(_mapping(raw, label="run")["actor_class"]),
            event_type=str(_mapping(raw, label="run")["event_type"]),
            workflow_path=str(_mapping(raw, label="run")["workflow_path"]),
            head_sha=str(_mapping(raw, label="run")["head_sha"]),
            head_branch=(
                str(_mapping(raw, label="run")["head_branch"])
                if _mapping(raw, label="run").get("head_branch") is not None
                else None
            ),
            pull_request_ids=tuple(int(value) for value in _mapping(raw, label="run")["pull_request_ids"]),
            check_suite_id=int(_mapping(raw, label="run")["check_suite_id"]),
        )
        for raw in _sequence(payload.get("runs"), label="runs")
    )
    probes: list[D0SchemaProbe] = []
    for raw_probe in _sequence(payload.get("schema_probes"), label="schema probes"):
        probe = _mapping(raw_probe, label="schema probe")
        jobs = tuple(
            D0WorkflowJobSchema(
                run_id=int(_mapping(raw, label="job")["run_id"]),
                job_id=int(_mapping(raw, label="job")["job_id"]),
                job_name=str(_mapping(raw, label="job")["job_name"]),
                runner_labels=tuple(str(value) for value in _mapping(raw, label="job")["runner_labels"]),
                required_field_presence={
                    str(key): bool(value)
                    for key, value in _mapping(
                        _mapping(raw, label="job")["required_field_presence"], label="field presence"
                    ).items()
                },
            )
            for raw in _sequence(probe.get("jobs"), label="probe jobs")
        )
        raw_structure = probe.get("workflow_structure")
        structure: WorkflowStructureSummary | None = None
        if raw_structure is not None:
            structure = workflow_structure_from_payload(_mapping(raw_structure, label="workflow structure"))
        probes.append(
            D0SchemaProbe(
                run_id=int(probe["run_id"]),
                actor_class=str(probe["actor_class"]),
                job_api_access=bool(probe["job_api_access"]),
                jobs=jobs,
                workflow_structure=structure,
            )
        )
    record = D0RepositoryIdentityRecord(
        repository_id=int(payload["repository_id"]),
        full_name=str(payload["full_name"]),
        cohort=str(payload["cohort"]),
        run_api_access=bool(payload["run_api_access"]),
        unresolved_truncation_count=int(payload["unresolved_truncation_count"]),
        conflicting_duplicate_run_ids=int(payload["conflicting_duplicate_run_ids"]),
        runs=runs,
        schema_probes=tuple(probes),
    )
    assert_outcome_blind_payload(record.allowed_payload())
    return record


def deterministic_probe_runs(
    record: D0RepositoryIdentityRecord,
    *,
    pre_from_utc: str,
    pre_to_utc: str,
    per_actor_class: int,
) -> tuple[tuple[str, D0WorkflowRunIdentity], ...]:
    """Select pre-period human and Dependabot schema probes without outcomes."""
    lower = parse_utc(pre_from_utc)
    upper = parse_utc(pre_to_utc)
    selected: list[tuple[str, D0WorkflowRunIdentity]] = []
    classes = {
        "human": [
            run
            for run in record.runs
            if run.actor_class == "user"
            and run.event_type == "push"
            and run.run_attempt == 1
            and lower <= parse_utc(run.created_at) <= upper
        ],
        "dependabot": [
            run
            for run in record.runs
            if run.actor_class == "dependabot" and lower <= parse_utc(run.created_at) <= upper
        ],
    }
    for actor_class, runs in classes.items():
        ordered = sorted(
            runs,
            key=lambda run: hashlib.sha256(
                f"{record.repository_id}:{run.run_id}:{actor_class}".encode()
            ).hexdigest(),
        )[:per_actor_class]
        selected.extend((actor_class, run) for run in ordered)
    return tuple(selected)


def repository_runner_pool_class(record: D0RepositoryIdentityRecord) -> str:
    """Classify the observed pre-period human runner pool."""
    label_sets = [
        canonical_runner_label_set(job.runner_labels)
        for probe in record.schema_probes
        if probe.actor_class == "human" and probe.job_api_access
        for job in probe.jobs
        if job.runner_labels
    ]
    if any("self-hosted" in labels for labels in label_sets):
        return "self_hosted_present"
    if label_sets:
        return "nonself_hosted_observed"
    return "unknown"


def repository_has_shared_pool(record: D0RepositoryIdentityRecord) -> bool:
    """Return whether sampled bot and human jobs use an identical nonempty label set."""
    human = {
        canonical_runner_label_set(job.runner_labels)
        for probe in record.schema_probes
        if probe.actor_class == "human" and probe.job_api_access
        for job in probe.jobs
        if job.runner_labels
    }
    bot = {
        canonical_runner_label_set(job.runner_labels)
        for probe in record.schema_probes
        if probe.actor_class == "dependabot" and probe.job_api_access
        for job in probe.jobs
        if job.runner_labels
    }
    return bool(human.intersection(bot))


MATCHING_COVARIATES = (
    "log1p_pre_primary_human_run_count",
    "log1p_pre_all_human_run_count",
    "log1p_pre_human_pr_lower_bound_capped_100",
    "log1p_workflow_path_count",
    "log1p_stargazers_count",
    "repository_age_days_at_cutoff",
    "pre_push_fraction_of_human_runs",
    "pre_pull_request_fraction_of_human_runs",
    "pre_workflow_dispatch_fraction_of_human_runs",
)


@dataclass(frozen=True)
class RepositoryMatchFeatures:
    """Frozen pre-period matching features for one repository."""

    repository_id: int
    full_name: str
    cohort: str
    runner_pool_class: str
    values: dict[str, float]
    pre_primary_human_run_count: int
    successful_human_schema_probe: bool

    def allowed_payload(self) -> dict[str, Any]:
        """Return the outcome-blind matching representation."""
        payload = asdict(self)
        assert_outcome_blind_payload(payload)
        return payload


def build_match_features(
    record: D0RepositoryIdentityRecord,
    candidate: Mapping[str, Any],
    *,
    pre_from_utc: str,
    pre_to_utc: str,
    config_cutoff_utc: str,
) -> RepositoryMatchFeatures:
    """Construct only frozen pre-period covariates."""
    lower = parse_utc(pre_from_utc)
    upper = parse_utc(pre_to_utc)
    human = [
        run
        for run in record.runs
        if run.actor_class == "user" and run.run_attempt == 1 and lower <= parse_utc(run.created_at) <= upper
    ]
    event_counts: defaultdict[str, int] = defaultdict(int)
    for run in human:
        event_counts[run.event_type] += 1
    primary_count = event_counts["push"]
    total = len(human)
    denominator = float(total) if total else 1.0
    repository_age = (
        parse_utc(config_cutoff_utc) - parse_utc(str(candidate["created_at"]))
    ).total_seconds() / 86400.0
    values = {
        "log1p_pre_primary_human_run_count": math.log1p(primary_count),
        "log1p_pre_all_human_run_count": math.log1p(total),
        "log1p_pre_human_pr_lower_bound_capped_100": math.log1p(
            int(candidate["pre_human_pr_lower_bound_capped_100"])
        ),
        "log1p_workflow_path_count": math.log1p(int(candidate["workflow_path_count"])),
        "log1p_stargazers_count": math.log1p(int(candidate["stargazers_count"])),
        "repository_age_days_at_cutoff": repository_age,
        "pre_push_fraction_of_human_runs": event_counts["push"] / denominator,
        "pre_pull_request_fraction_of_human_runs": (
            event_counts["pull_request"] + event_counts["pull_request_target"]
        )
        / denominator,
        "pre_workflow_dispatch_fraction_of_human_runs": event_counts["workflow_dispatch"] / denominator,
    }
    if set(values) != set(MATCHING_COVARIATES) or not all(math.isfinite(value) for value in values.values()):
        raise ValueError("matching covariates are incomplete or nonfinite")
    successful_human_probe = any(
        probe.actor_class == "human" and probe.job_api_access and bool(probe.jobs)
        for probe in record.schema_probes
    )
    features = RepositoryMatchFeatures(
        repository_id=record.repository_id,
        full_name=record.full_name,
        cohort=record.cohort,
        runner_pool_class=repository_runner_pool_class(record),
        values=values,
        pre_primary_human_run_count=primary_count,
        successful_human_schema_probe=successful_human_probe,
    )
    assert_outcome_blind_payload(features.allowed_payload())
    return features


def is_prequalified(features: RepositoryMatchFeatures, *, minimum_primary_runs: int) -> bool:
    """Apply the frozen prequalification rule."""
    return (
        features.pre_primary_human_run_count >= minimum_primary_runs
        and features.runner_pool_class != "unknown"
        and features.successful_human_schema_probe
        and all(math.isfinite(value) for value in features.values.values())
    )


def _tie_break(treated_id: int, control_id: int) -> float:
    digest = hashlib.sha256(f"{treated_id}:{control_id}".encode()).hexdigest()
    return int(digest[:12], 16) / float(16**12) * 1e-9


def optimal_repository_match(
    treated: Sequence[RepositoryMatchFeatures],
    controls: Sequence[RepositoryMatchFeatures],
    *,
    ratio: int,
    minimum_treated: int,
    maximum_scaled_primary_difference: float,
) -> dict[str, Any]:
    """Find the largest deterministic complete-prefix optimal assignment."""
    if ratio <= 0 or minimum_treated <= 0:
        raise ValueError("matching ratio and minimum treated must be positive")
    all_features = [*treated, *controls]
    if not all_features:
        return {
            "matched_treated_repository_ids": [],
            "matched_control_repository_ids": [],
            "pairs": [],
            "balance": {},
            "matching_complete": False,
        }
    raw = np.asarray(
        [[feature.values[name] for name in MATCHING_COVARIATES] for feature in all_features],
        dtype=np.float64,
    )
    median = np.median(raw, axis=0)
    mad = np.median(np.abs(raw - median), axis=0)
    scale = np.where(mad > 0.0, 1.4826 * mad, 1.0)
    scaled = (raw - median) / scale
    covariance = np.cov(scaled, rowvar=False)
    inverse_covariance = np.linalg.pinv(np.atleast_2d(covariance), hermitian=True)
    treated_scaled = scaled[: len(treated)]
    control_scaled = scaled[len(treated) :]
    cost = np.full((len(treated), len(controls)), np.inf, dtype=np.float64)
    primary_index = MATCHING_COVARIATES.index("log1p_pre_primary_human_run_count")
    for treated_index, treated_feature in enumerate(treated):
        for control_index, control_feature in enumerate(controls):
            if treated_feature.runner_pool_class != control_feature.runner_pool_class:
                continue
            if (
                abs(
                    treated_scaled[treated_index, primary_index]
                    - control_scaled[control_index, primary_index]
                )
                > maximum_scaled_primary_difference
            ):
                continue
            difference = treated_scaled[treated_index] - control_scaled[control_index]
            distance = float(math.sqrt(max(0.0, difference @ inverse_covariance @ difference)))
            cost[treated_index, control_index] = distance + _tie_break(
                treated_feature.repository_id, control_feature.repository_id
            )
    feasible_counts = np.isfinite(cost).sum(axis=1)
    treated_order = sorted(
        range(len(treated)),
        key=lambda index: (
            -int(feasible_counts[index]),
            hashlib.sha256(str(treated[index].repository_id).encode()).hexdigest(),
        ),
    )
    selected_rows: list[int] | None = None
    assigned_columns: np.ndarray[Any, np.dtype[np.int64]] | None = None
    assigned_costs: np.ndarray[Any, np.dtype[np.float64]] | None = None
    for count in range(len(treated_order), minimum_treated - 1, -1):
        selected = treated_order[:count]
        if len(controls) < count * ratio:
            continue
        repeated = np.repeat(np.asarray(selected, dtype=np.int64), ratio)
        subcost = cost[repeated]
        finite_cost = np.where(np.isfinite(subcost), subcost, 1e12)
        assigned_rows, columns = linear_sum_assignment(finite_cost)
        selected_costs = subcost[assigned_rows, columns]
        if len(columns) == count * ratio and np.isfinite(selected_costs).all():
            selected_rows = selected
            assigned_columns = columns.astype(np.int64)
            assigned_costs = selected_costs.astype(np.float64)
            break
    if selected_rows is None or assigned_columns is None or assigned_costs is None:
        return {
            "matched_treated_repository_ids": [],
            "matched_control_repository_ids": [],
            "pairs": [],
            "balance": {},
            "matching_complete": False,
            "feasible_control_counts": {
                str(treated[index].repository_id): int(feasible_counts[index]) for index in treated_order
            },
        }
    repeated_rows = np.repeat(np.asarray(selected_rows, dtype=np.int64), ratio)
    pairs = [
        {
            "treated_repository_id": treated[int(treated_index)].repository_id,
            "control_repository_id": controls[int(control_index)].repository_id,
            "scaled_mahalanobis_distance": float(distance),
        }
        for treated_index, control_index, distance in zip(
            repeated_rows, assigned_columns, assigned_costs, strict=True
        )
    ]
    selected_treated = [treated[index] for index in selected_rows]
    selected_controls = [controls[int(index)] for index in assigned_columns]
    pre_match_std = np.std(raw, axis=0, ddof=1)
    treated_values = np.asarray(
        [[feature.values[name] for name in MATCHING_COVARIATES] for feature in selected_treated],
        dtype=np.float64,
    )
    control_values = np.asarray(
        [[feature.values[name] for name in MATCHING_COVARIATES] for feature in selected_controls],
        dtype=np.float64,
    )
    differences = treated_values.mean(axis=0) - control_values.mean(axis=0)
    smd: list[float | None] = []
    nonfinite_balance_covariates: list[str] = []
    for name, difference, denominator in zip(MATCHING_COVARIATES, differences, pre_match_std, strict=True):
        if denominator == 0.0:
            if difference == 0.0:
                smd.append(0.0)
            else:
                smd.append(None)
                nonfinite_balance_covariates.append(name)
        else:
            smd.append(abs(float(difference / denominator)))
    balance = {name: value for name, value in zip(MATCHING_COVARIATES, smd, strict=True)}
    finite_smd = [value for value in smd if value is not None]
    maximum_smd = max(finite_smd) if len(finite_smd) == len(smd) else None
    mean_smd = float(np.mean(finite_smd)) if len(finite_smd) == len(smd) else None
    result = {
        "matched_treated_repository_ids": sorted(feature.repository_id for feature in selected_treated),
        "matched_control_repository_ids": sorted(feature.repository_id for feature in selected_controls),
        "pairs": sorted(
            pairs,
            key=lambda row: (row["treated_repository_id"], row["control_repository_id"]),
        ),
        "balance": balance,
        "nonfinite_balance_covariates": nonfinite_balance_covariates,
        "maximum_absolute_standardized_mean_difference": maximum_smd,
        "mean_absolute_standardized_mean_difference": mean_smd,
        "matching_complete": True,
        "feasible_control_counts": {
            str(treated[index].repository_id): int(feasible_counts[index]) for index in treated_order
        },
    }
    assert_outcome_blind_payload(result)
    return result


def _run_period(created_at: str, windows: Mapping[str, Any]) -> str | None:
    timestamp = parse_utc(created_at)
    intervals = (
        ("extended_pre", windows["extended_pre_from_utc"], windows["primary_pre_from_utc"], False),
        ("primary_pre", windows["primary_pre_from_utc"], windows["primary_pre_to_utc"], True),
        ("primary_post", windows["primary_post_from_utc"], windows["primary_post_to_utc"], True),
    )
    for label, lower_raw, upper_raw, inclusive_upper in intervals:
        lower = parse_utc(str(lower_raw))
        upper = parse_utc(str(upper_raw))
        if label == "extended_pre":
            if lower <= timestamp < upper:
                return label
        elif inclusive_upper and lower <= timestamp <= upper:
            return label
    return None


def select_d1_run_identities(
    records: Sequence[D0RepositoryIdentityRecord],
    *,
    included_repository_ids: set[int],
    windows: Mapping[str, Any],
    primary_events: set[str],
    secondary_events: set[str],
    primary_daily_cap: int,
    secondary_daily_cap: int,
) -> list[dict[str, Any]]:
    """Freeze deterministic D1 run identities without opening their outcomes."""
    strata: defaultdict[tuple[int, str, str, str], list[D0WorkflowRunIdentity]] = defaultdict(list)
    cohort_by_repository: dict[int, str] = {}
    for record in records:
        if record.repository_id not in included_repository_ids:
            continue
        cohort_by_repository[record.repository_id] = record.cohort
        for run in record.runs:
            if run.actor_class != "user" or run.run_attempt != 1:
                continue
            period = _run_period(run.created_at, windows)
            if period is None:
                continue
            if run.event_type in primary_events:
                sample_class = "primary"
            elif run.event_type in secondary_events:
                sample_class = "secondary"
            else:
                continue
            utc_date = parse_utc(run.created_at).date().isoformat()
            strata[(record.repository_id, utc_date, sample_class, period)].append(run)
    selected: list[dict[str, Any]] = []
    for (repository_id, utc_date, sample_class, period), runs in sorted(strata.items()):
        cap = primary_daily_cap if sample_class == "primary" else secondary_daily_cap
        ordered = sorted(
            runs,
            key=lambda run: hashlib.sha256(f"{repository_id}:{run.run_id}".encode()).hexdigest(),
        )[:cap]
        for rank, run in enumerate(ordered, start=1):
            selected.append(
                {
                    "repository_id": repository_id,
                    "cohort": cohort_by_repository[repository_id],
                    "utc_date": utc_date,
                    "sample_class": sample_class,
                    "period": period,
                    "selection_rank": rank,
                    "run": run.allowed_payload(),
                }
            )
    assert_outcome_blind_payload(selected)
    return selected


WorkflowStructureKey = tuple[int, str, str]


def selected_workflow_structure_key(row: Mapping[str, Any]) -> WorkflowStructureKey:
    """Return the immutable source key for a provisionally selected run's workflow YAML."""
    run = _mapping(row.get("run"), label="selected run identity")
    return (
        int(row["repository_id"]),
        str(run["head_sha"]),
        str(run["workflow_path"]),
    )


def finalize_d1_run_identities(
    provisional_runs: Sequence[Mapping[str, Any]],
    structures: Mapping[WorkflowStructureKey, WorkflowStructureSummary | None],
) -> tuple[list[dict[str, Any]], dict[str, int | float]]:
    """Exclude primary runs with unknown or intentional workflow waits before outcomes open."""
    selected: list[dict[str, Any]] = []
    primary_total = 0
    primary_recovered = 0
    primary_intentional_wait = 0
    primary_missing_structure = 0
    for raw in provisional_runs:
        row = dict(_mapping(raw, label="provisional selected run"))
        if row.get("sample_class") != "primary":
            selected.append(row)
            continue
        primary_total += 1
        structure = structures.get(selected_workflow_structure_key(row))
        if structure is None:
            primary_missing_structure += 1
            continue
        primary_recovered += 1
        if structure.intentional_wait_flags:
            primary_intentional_wait += 1
            continue
        row["workflow_structure"] = structure.allowed_payload()
        selected.append(row)
    metrics: dict[str, int | float] = {
        "provisional_primary_runs": primary_total,
        "primary_workflow_structures_recovered": primary_recovered,
        "primary_runs_excluded_missing_structure": primary_missing_structure,
        "primary_runs_excluded_intentional_wait": primary_intentional_wait,
        "primary_workflow_structure_recovery_rate": (
            primary_recovered / primary_total if primary_total else 0.0
        ),
        "final_selected_runs": len(selected),
    }
    assert_outcome_blind_payload(selected)
    assert_outcome_blind_payload(metrics)
    return selected, metrics


def evaluate_d0_identity_prerequisites(
    records: Sequence[D0RepositoryIdentityRecord],
    *,
    windows: Mapping[str, Any],
    minimum_primary_runs: int,
    gates: Mapping[str, Any],
) -> dict[str, Any]:
    """Prove necessary identity gates before spending requests on schema probes."""
    pre_lower = parse_utc(str(windows["primary_pre_from_utc"]))
    pre_upper = parse_utc(str(windows["primary_pre_to_utc"]))

    def has_minimum_primary_support(record: D0RepositoryIdentityRecord) -> bool:
        return (
            sum(
                run.actor_class == "user"
                and run.event_type == "push"
                and run.run_attempt == 1
                and pre_lower <= parse_utc(run.created_at) <= pre_upper
                for run in record.runs
            )
            >= minimum_primary_runs
        )

    cohorts = (
        "default_treated_high_support",
        "no_dependabot_candidate_controls",
    )
    exact_support = {
        cohort: sum(
            record.cohort == cohort
            and record.run_api_access
            and record.unresolved_truncation_count == 0
            and has_minimum_primary_support(record)
            for record in records
        )
        for cohort in cohorts
    }
    upper_bounds = {
        cohort: sum(
            record.cohort == cohort
            and (
                not record.run_api_access
                or record.unresolved_truncation_count > 0
                or has_minimum_primary_support(record)
            )
            for record in records
        )
        for cohort in cohorts
    }
    access_rate = sum(record.run_api_access for record in records) / len(records) if records else 0.0
    prerequisite_gates = {
        "repository_run_api_access": access_rate >= float(gates["minimum_repository_run_api_access_rate"]),
        "no_unresolved_truncation": sum(record.unresolved_truncation_count for record in records)
        <= int(gates["maximum_unresolved_truncated_run_queries"]),
        "no_conflicting_run_ids": sum(record.conflicting_duplicate_run_ids for record in records)
        <= int(gates["maximum_conflicting_duplicate_run_ids"]),
        "treated_prequalification_upper_bound": upper_bounds["default_treated_high_support"]
        >= int(gates["minimum_prequalified_treated_repositories"]),
        "control_prequalification_upper_bound": upper_bounds["no_dependabot_candidate_controls"]
        >= int(gates["minimum_prequalified_control_candidates"]),
    }
    result = {
        "repository_run_api_access_rate": access_rate,
        "exact_complete_repository_primary_support": exact_support,
        "prequalification_upper_bounds": upper_bounds,
        "prerequisite_gates": prerequisite_gates,
        "probe_stage_authorized": all(prerequisite_gates.values()),
    }
    assert_outcome_blind_payload(result)
    return result


def evaluate_d0_support(
    records: Sequence[D0RepositoryIdentityRecord],
    features: Sequence[RepositoryMatchFeatures],
    matching: Mapping[str, Any],
    selected_runs: Sequence[Mapping[str, Any]],
    *,
    gates: Mapping[str, Any],
    minimum_primary_runs: int,
    maximum_absolute_smd: float,
    maximum_mean_smd: float,
    deterministic_hash_matches: bool,
    candidate_hashes_exact: bool,
) -> dict[str, Any]:
    """Apply all frozen D0 support and seal gates."""
    treated_features = [feature for feature in features if feature.cohort == "default_treated_high_support"]
    control_features = [
        feature for feature in features if feature.cohort == "no_dependabot_candidate_controls"
    ]
    prequalified_treated = [
        feature
        for feature in treated_features
        if is_prequalified(feature, minimum_primary_runs=minimum_primary_runs)
    ]
    prequalified_controls = [
        feature
        for feature in control_features
        if is_prequalified(feature, minimum_primary_runs=minimum_primary_runs)
    ]
    matched_treated = {int(value) for value in matching.get("matched_treated_repository_ids", [])}
    matched_controls = {int(value) for value in matching.get("matched_control_repository_ids", [])}
    selected_counts: defaultdict[tuple[str, str], int] = defaultdict(int)
    per_repo_primary: defaultdict[tuple[int, str], int] = defaultdict(int)
    for raw in selected_runs:
        row = _mapping(raw, label="selected run")
        if row.get("sample_class") != "primary" or row.get("period") not in {"primary_pre", "primary_post"}:
            continue
        cohort = str(row["cohort"])
        period = str(row["period"])
        selected_counts[(cohort, period)] += 1
        per_repo_primary[(int(row["repository_id"]), period)] += 1
    treated_with_five = sum(
        per_repo_primary[(repository_id, "primary_pre")] >= 5
        and per_repo_primary[(repository_id, "primary_post")] >= 5
        for repository_id in matched_treated
    )
    controls_with_five = sum(
        per_repo_primary[(repository_id, "primary_pre")] >= 5
        and per_repo_primary[(repository_id, "primary_post")] >= 5
        for repository_id in matched_controls
    )
    negative_ids = {
        record.repository_id
        for record in records
        if record.cohort == "already_cooled_high_support_negative_controls"
    }
    negative_with_five = sum(
        per_repo_primary[(repository_id, "primary_pre")] >= 5
        and per_repo_primary[(repository_id, "primary_post")] >= 5
        for repository_id in negative_ids
    )
    treated_shared_pool = sum(
        repository_has_shared_pool(record)
        for record in records
        if record.cohort == "default_treated_high_support"
    )
    probes = [probe for record in records for probe in record.schema_probes]
    successful_probes = [probe for probe in probes if probe.job_api_access]
    jobs = [job for probe in successful_probes for job in probe.jobs]
    structure_denominator = sum(
        1
        for record in records
        for probe in record.schema_probes
        if next((run for run in record.runs if run.run_id == probe.run_id), None) is not None
    )
    structure_recovered = sum(probe.workflow_structure is not None for probe in probes)
    access_rate = sum(record.run_api_access for record in records) / len(records) if records else 0.0
    schema_access_rate = len(successful_probes) / len(probes) if probes else 0.0
    job_start_presence_rate = (
        sum(job.required_field_presence.get("job_start_present") is True for job in jobs) / len(jobs)
        if jobs
        else 0.0
    )
    structure_rate = structure_recovered / structure_denominator if structure_denominator else 0.0
    no_forbidden = True
    try:
        assert_outcome_blind_payload([record.allowed_payload() for record in records])
        assert_outcome_blind_payload(list(selected_runs))
        assert_outcome_blind_payload(dict(matching))
    except ValueError:
        no_forbidden = False
    raw_max_smd = matching.get("maximum_absolute_standardized_mean_difference")
    raw_mean_smd = matching.get("mean_absolute_standardized_mean_difference")
    max_smd = (
        float(raw_max_smd)
        if isinstance(raw_max_smd, (int, float))
        and not isinstance(raw_max_smd, bool)
        and math.isfinite(float(raw_max_smd))
        else None
    )
    mean_smd = (
        float(raw_mean_smd)
        if isinstance(raw_mean_smd, (int, float))
        and not isinstance(raw_mean_smd, bool)
        and math.isfinite(float(raw_mean_smd))
        else None
    )
    matching_balance = (
        bool(matching.get("matching_complete"))
        and max_smd is not None
        and mean_smd is not None
        and max_smd <= maximum_absolute_smd
        and mean_smd <= maximum_mean_smd
    )
    metrics: dict[str, int | float | bool | None] = {
        "repository_run_api_access_rate": access_rate,
        "unresolved_truncated_run_queries": sum(record.unresolved_truncation_count for record in records),
        "conflicting_duplicate_run_ids": sum(record.conflicting_duplicate_run_ids for record in records),
        "prequalified_treated_repositories": len(prequalified_treated),
        "prequalified_control_candidates": len(prequalified_controls),
        "matched_treated_repositories": len(matched_treated),
        "matched_control_repositories": len(matched_controls),
        "treated_primary_selected_runs_pre": selected_counts[("default_treated_high_support", "primary_pre")],
        "treated_primary_selected_runs_post": selected_counts[
            ("default_treated_high_support", "primary_post")
        ],
        "control_primary_selected_runs_pre": selected_counts[
            ("no_dependabot_candidate_controls", "primary_pre")
        ],
        "control_primary_selected_runs_post": selected_counts[
            ("no_dependabot_candidate_controls", "primary_post")
        ],
        "matched_treated_with_five_primary_runs_each_period": treated_with_five,
        "matched_controls_with_five_primary_runs_each_period": controls_with_five,
        "negative_controls_with_five_primary_runs_each_period": negative_with_five,
        "treated_repositories_with_shared_bot_human_pool": treated_shared_pool,
        "workflow_structure_recovery_rate": structure_rate,
        "schema_probe_job_start_presence_rate": job_start_presence_rate,
        "schema_probe_access_rate": schema_access_rate,
        "maximum_absolute_standardized_mean_difference": max_smd,
        "mean_absolute_standardized_mean_difference": mean_smd,
        "candidate_hashes_exact": candidate_hashes_exact,
        "no_forbidden_persisted_field": no_forbidden,
        "deterministic_derived_hash": deterministic_hash_matches,
    }
    gate_results = {
        "repository_run_api_access": access_rate >= float(gates["minimum_repository_run_api_access_rate"]),
        "no_unresolved_truncation": sum(record.unresolved_truncation_count for record in records)
        <= int(gates["maximum_unresolved_truncated_run_queries"]),
        "no_conflicting_run_ids": sum(record.conflicting_duplicate_run_ids for record in records)
        <= int(gates["maximum_conflicting_duplicate_run_ids"]),
        "prequalified_treated": len(prequalified_treated)
        >= int(gates["minimum_prequalified_treated_repositories"]),
        "prequalified_controls": len(prequalified_controls)
        >= int(gates["minimum_prequalified_control_candidates"]),
        "matched_treated": len(matched_treated) >= int(gates["minimum_matched_treated_repositories"]),
        "matched_controls": len(matched_controls) >= int(gates["minimum_matched_control_repositories"]),
        "treated_primary_runs": min(
            selected_counts[("default_treated_high_support", "primary_pre")],
            selected_counts[("default_treated_high_support", "primary_post")],
        )
        >= int(gates["minimum_treated_primary_selected_runs_each_period"]),
        "control_primary_runs": min(
            selected_counts[("no_dependabot_candidate_controls", "primary_pre")],
            selected_counts[("no_dependabot_candidate_controls", "primary_post")],
        )
        >= int(gates["minimum_control_primary_selected_runs_each_period"]),
        "treated_repeated_support": treated_with_five
        >= int(gates["minimum_matched_treated_with_five_primary_runs_each_period"]),
        "control_repeated_support": controls_with_five
        >= int(gates["minimum_matched_controls_with_five_primary_runs_each_period"]),
        "negative_control_support": negative_with_five
        >= int(gates["minimum_negative_controls_with_five_primary_runs_each_period"]),
        "shared_pool_support": treated_shared_pool
        >= int(gates["minimum_treated_repositories_with_shared_bot_human_pool"]),
        "workflow_structure_recovery": structure_rate
        >= float(gates["minimum_workflow_structure_recovery_rate"]),
        "schema_job_start_presence": job_start_presence_rate
        >= float(gates["minimum_schema_probe_job_start_presence_rate"]),
        "schema_access": schema_access_rate >= float(gates["minimum_schema_probe_access_rate"]),
        "matching_balance": matching_balance and bool(gates["require_matching_balance"]),
        "candidate_hashes": candidate_hashes_exact and bool(gates["require_candidate_hashes_exact"]),
        "outcome_seal": no_forbidden and bool(gates["require_no_forbidden_persisted_field"]),
        "deterministic_hash": deterministic_hash_matches
        and bool(gates["require_deterministic_derived_hash"]),
    }
    if all(gate_results.values()):
        decision = "green_freeze_exact_d1_ids_before_outcomes"
    elif not gate_results["shared_pool_support"] and all(
        value for key, value in gate_results.items() if key != "shared_pool_support"
    ):
        decision = "amber_freeze_narrower_reduced_form_before_d1"
    else:
        decision = "red_stop_before_outcomes_or_rescue"
    return {"metrics": metrics, "gates": gate_results, "scientific_decision": decision}


def candidate_rows_by_id(ledger: Mapping[str, Any]) -> dict[int, dict[str, Any]]:
    """Flatten the frozen candidate cohorts and preserve their ledger key."""
    cohorts = _mapping(ledger.get("cohorts"), label="candidate cohorts")
    result: dict[int, dict[str, Any]] = {}
    for cohort, raw_rows in cohorts.items():
        for raw in _sequence(raw_rows, label=f"candidate cohort {cohort}"):
            row = dict(_mapping(raw, label="candidate row"))
            repository_id = int(row["repository_id"])
            if repository_id in result:
                raise ValueError("candidate repository appears in multiple cohorts")
            row["cohort"] = str(cohort)
            result[repository_id] = row
    assert_outcome_blind_payload(result)
    return result


def canonical_records_hash(records: Sequence[D0RepositoryIdentityRecord]) -> str:
    """Hash repository records in frozen repository-ID order."""
    payloads = [record.allowed_payload() for record in sorted(records, key=lambda item: item.repository_id)]
    return canonical_json_sha256(payloads)
