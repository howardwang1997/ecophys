"""Run the frozen outcome-blind GitHub Dependabot cooldown D0 audit."""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import html
import json
import math
import os
import re
import subprocess
import threading
import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, TypeVar
from urllib.parse import quote

import requests
import yaml

from ecomd.data.github_verification_liquidity import (
    assert_outcome_blind_payload,
    canonical_json_sha256,
)
from ecomd.data.github_verification_liquidity_d0 import (
    D0RepositoryIdentityRecord,
    D0SchemaProbe,
    D0WorkflowJobSchema,
    D0WorkflowRunIdentity,
    WorkflowStructureKey,
    WorkflowStructureSummary,
    build_match_features,
    candidate_rows_by_id,
    deterministic_probe_runs,
    evaluate_d0_identity_prerequisites,
    evaluate_d0_support,
    finalize_d1_run_identities,
    is_prequalified,
    normalize_workflow_path,
    optimal_repository_match,
    parse_utc,
    repository_record_from_payload,
    sanitize_d0_workflow_job,
    sanitize_d0_workflow_run,
    select_d1_run_identities,
    selected_workflow_structure_key,
    summarize_workflow_structure,
    workflow_run_from_payload,
    workflow_structure_from_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs/agent_markets/github_dependabot_cooldown_d0_v3.yaml"
RUNTIME_PATH = REPO_ROOT / "configs/agent_markets/github_dependabot_cooldown_d0_runtime_v2.yaml"

ItemT = TypeVar("ItemT")
ResultT = TypeVar("ResultT")


def _run_bounded_stage(
    items: Sequence[ItemT],
    *,
    maximum_workers: int,
    worker: Callable[[ItemT, threading.Event], ResultT],
    on_success: Callable[[ItemT, ResultT], None],
    error_message: str,
) -> int:
    """Run at most maximum_workers tasks and preserve successes before failing."""
    if maximum_workers <= 0:
        raise ValueError("maximum_workers must be positive")
    stop_event = threading.Event()
    item_iterator = iter(items)
    futures: dict[Future[ResultT], ItemT] = {}
    first_error: Exception | None = None
    completed = 0
    executor = ThreadPoolExecutor(max_workers=maximum_workers)

    def submit_next() -> bool:
        try:
            item = next(item_iterator)
        except StopIteration:
            return False
        futures[executor.submit(worker, item, stop_event)] = item
        return True

    try:
        for _ in range(min(maximum_workers, len(items))):
            submit_next()
        while futures:
            done, _ = wait(futures, return_when=FIRST_COMPLETED)
            for future in done:
                item = futures.pop(future)
                try:
                    result = future.result()
                    on_success(item, result)
                    completed += 1
                except Exception as error:
                    if first_error is None:
                        first_error = error
                        stop_event.set()
                if first_error is None:
                    submit_next()
    finally:
        stop_event.set()
        executor.shutdown(wait=True, cancel_futures=True)
    if first_error is not None:
        raise RuntimeError(error_message) from first_error
    return completed


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"YAML root must be an object: {path}")
    return payload


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_without_digest(payload: Mapping[str, Any]) -> str:
    return canonical_json_sha256(
        {key: value for key, value in payload.items() if key != "canonical_payload_sha256"}
    )


def _resolve_repo_path(relative: Any) -> Path:
    path = (REPO_ROOT / str(relative)).resolve()
    if REPO_ROOT.resolve() not in path.parents:
        raise ValueError("runtime path escapes the repository")
    return path


def _mapping(value: Any, *, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _sequence(value: Any, *, label: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{label} must be an array")
    return value


def _optional_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _github_token() -> str:
    for variable in ("GH_TOKEN", "GITHUB_TOKEN"):
        value = os.environ.get(variable)
        if value:
            return value
    completed = subprocess.run(
        ["gh", "auth", "token"],
        check=True,
        capture_output=True,
        text=True,
    )
    token = completed.stdout.strip()
    if not token:
        raise RuntimeError("GitHub authentication token is unavailable")
    return token


def _verify_contract(
    config_path: Path,
    runtime_path: Path,
    *,
    formal: bool,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    config = _load_yaml(config_path)
    runtime = _load_yaml(runtime_path)
    contract = _mapping(config.get("contract"), label="scientific contract")
    runtime_contract = _mapping(runtime.get("contract"), label="runtime contract")
    if contract.get("status") != "frozen_before_formal_outcome_blind_d0_acquisition":
        raise RuntimeError("D0 scientific contract is not frozen")
    if runtime_contract.get("status") not in {
        "implementation_runtime_before_formal_acquisition",
        "implementation_runtime_before_formal_resume",
    }:
        raise RuntimeError("D0 runtime contract has an unexpected status")
    expected_path = config_path.relative_to(REPO_ROOT).as_posix()
    if runtime_contract.get("parent_config_path") != expected_path:
        raise RuntimeError("D0 runtime parent path mismatch")
    config_hash = _sha256_file(config_path)
    if runtime_contract.get("parent_config_sha256") != config_hash:
        raise RuntimeError("D0 runtime parent hash mismatch")
    preregistration_sha = str(runtime_contract.get("preregistration_git_sha"))
    committed_config = subprocess.run(
        ["git", "show", f"{preregistration_sha}:{expected_path}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    if hashlib.sha256(committed_config).hexdigest() != config_hash:
        raise RuntimeError("D0 scientific config differs from its pushed preregistration")
    if (
        runtime_contract.get("scientific_candidates_windows_estimand_gates_and_forbidden_fields_unchanged")
        is not True
    ):
        raise RuntimeError("D0 runtime does not preserve the scientific contract")
    if _git("branch", "--show-current") != contract.get("branch"):
        raise RuntimeError("D0 is running on the wrong branch")
    ledger_path = _resolve_repo_path(config["source"]["candidate_ledger_path"])
    ledger = _load_json(ledger_path)
    if _sha256_file(ledger_path) != config["source"]["candidate_ledger_file_sha256"]:
        raise RuntimeError("D0 candidate ledger file hash mismatch")
    if ledger.get("canonical_payload_sha256") != _canonical_without_digest(ledger):
        raise RuntimeError("D0 candidate ledger canonical hash mismatch")
    if ledger.get("canonical_payload_sha256") != config["source"]["candidate_ledger_canonical_sha256"]:
        raise RuntimeError("D0 candidate ledger does not match the scientific contract")
    if ledger.get("outcomes_opened") is not False:
        raise RuntimeError("D0 candidate ledger outcome seal is not intact")
    if formal and _git("status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("formal D0 requires a clean worktree")
    return config, runtime, ledger


class RequestStartLimiter:
    """Bound request starts across worker threads."""

    def __init__(self, interval_seconds: float) -> None:
        if interval_seconds <= 0:
            raise ValueError("request start interval must be positive")
        self.interval_seconds = interval_seconds
        self.next_start = 0.0
        self.lock = threading.Lock()

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()
            start = max(now, self.next_start)
            self.next_start = start + self.interval_seconds
        delay = start - now
        if delay > 0:
            time.sleep(delay)


@dataclass(frozen=True)
class TransportObservation:
    endpoint_class: str
    response_sha256: str
    etag: str | None
    rate_resource: str | None
    rate_remaining: int | None
    rate_reset: int | None
    http_code: int


class TransportJournal:
    """Append-only response-hash journal shared by all read-only clients."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.lock = threading.Lock()
        self.observations = self._load()

    def _load(self) -> list[TransportObservation]:
        if not self.path.exists():
            return []
        observations: list[TransportObservation] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            root = _mapping(json.loads(line), label="transport observation")
            assert_outcome_blind_payload(root)
            observations.append(TransportObservation(**dict(root)))
        return observations

    def append(self, endpoint_class: str, response: requests.Response) -> str:
        response_sha = hashlib.sha256(response.content).hexdigest()
        observation = TransportObservation(
            endpoint_class=endpoint_class,
            response_sha256=response_sha,
            etag=response.headers.get("ETag"),
            rate_resource=response.headers.get("X-RateLimit-Resource"),
            rate_remaining=_optional_int(response.headers.get("X-RateLimit-Remaining")),
            rate_reset=_optional_int(response.headers.get("X-RateLimit-Reset")),
            http_code=response.status_code,
        )
        assert_outcome_blind_payload(asdict(observation))
        with self.lock:
            self.observations.append(observation)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(asdict(observation), sort_keys=True, allow_nan=False) + "\n")
        return response_sha


class GitHubApiClient:
    """Authenticated GitHub client that journals hashes, never raw payloads."""

    def __init__(
        self,
        config: Mapping[str, Any],
        runtime: Mapping[str, Any],
        *,
        journal: TransportJournal,
    ) -> None:
        github = _mapping(config.get("github"), label="GitHub config")
        self.base_url = str(github["rest_base_url"]).rstrip("/")
        self.timeout = float(github["timeout_seconds"])
        self.attempts = int(github["attempts"])
        self.backoffs = [float(value) for value in github["backoff_seconds"]]
        self.minimum_remaining = int(github["minimum_remaining_core_requests"])
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {_github_token()}",
            "User-Agent": str(github["user_agent"]),
            "X-GitHub-Api-Version": str(github["api_version"]),
        }
        execution = _mapping(runtime.get("execution"), label="runtime execution")
        self.limiter = RequestStartLimiter(float(execution["request_start_interval_seconds"]))
        self.local = threading.local()
        self.journal = journal

    def _session(self) -> requests.Session:
        session = getattr(self.local, "session", None)
        if not isinstance(session, requests.Session):
            session = requests.Session()
            session.headers.update(self.headers)
            self.local.session = session
        return session

    def request_json(
        self,
        path: str,
        *,
        endpoint_class: str,
        params: Mapping[str, Any] | None = None,
        allow_not_found: bool = False,
    ) -> Any:
        """Read JSON with the frozen retry and rate-reserve policy."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        last_error: Exception | None = None
        for attempt in range(self.attempts):
            self.limiter.wait()
            try:
                response = self._session().get(url, params=params, timeout=self.timeout)
                if response.status_code == 404 and allow_not_found:
                    self.journal.append(endpoint_class, response)
                    self._guard_rate(response)
                    return None
                if (
                    response.status_code == 429 or response.status_code >= 500
                ) and attempt + 1 < self.attempts:
                    time.sleep(self.backoffs[min(attempt, len(self.backoffs) - 1)])
                    continue
                response.raise_for_status()
                self.journal.append(endpoint_class, response)
                payload = response.json()
                self._guard_rate(response)
                return payload
            except (requests.RequestException, ValueError) as error:
                last_error = error
                if attempt + 1 < self.attempts:
                    time.sleep(self.backoffs[min(attempt, len(self.backoffs) - 1)])
        raise RuntimeError(f"GitHub transport failed for {endpoint_class}") from last_error

    def _guard_rate(self, response: requests.Response) -> None:
        resource = response.headers.get("X-RateLimit-Resource")
        remaining = _optional_int(response.headers.get("X-RateLimit-Remaining"))
        if resource == "core" and remaining is not None and remaining < self.minimum_remaining:
            reset = response.headers.get("X-RateLimit-Reset", "unknown")
            raise RuntimeError(f"GitHub core rate budget below frozen reserve; reset={reset}")


class PublicStatusClient:
    """Unauthenticated status-page client that cannot leak the GitHub token."""

    def __init__(
        self, *, timeout: float, attempts: int, backoffs: Sequence[float], journal: TransportJournal
    ) -> None:
        self.timeout = timeout
        self.attempts = attempts
        self.backoffs = list(backoffs)
        self.journal = journal
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "EcoPhys-verification-liquidity-d0-status/1.0"})

    def get(self, url: str, *, endpoint_class: str) -> tuple[bytes, str]:
        """Return public bytes and their journaled response hash."""
        last_error: Exception | None = None
        for attempt in range(self.attempts):
            try:
                response = self.session.get(url, timeout=self.timeout)
                if (
                    response.status_code == 429 or response.status_code >= 500
                ) and attempt + 1 < self.attempts:
                    time.sleep(self.backoffs[min(attempt, len(self.backoffs) - 1)])
                    continue
                response.raise_for_status()
                response_sha = self.journal.append(endpoint_class, response)
                return response.content, response_sha
            except requests.RequestException as error:
                last_error = error
                if attempt + 1 < self.attempts:
                    time.sleep(self.backoffs[min(attempt, len(self.backoffs) - 1)])
        raise RuntimeError(f"public status transport failed for {endpoint_class}") from last_error


def _format_range(lower: datetime, upper: datetime) -> str:
    return f"{lower.strftime('%Y-%m-%dT%H:%M:%SZ')}..{upper.strftime('%Y-%m-%dT%H:%M:%SZ')}"


def _run_identity_map(raw_runs: Sequence[Any], *, dependabot_login: str) -> dict[int, D0WorkflowRunIdentity]:
    identities: dict[int, D0WorkflowRunIdentity] = {}
    for raw in raw_runs:
        run = sanitize_d0_workflow_run(
            _mapping(raw, label="workflow run"),
            dependabot_login=dependabot_login,
        )
        previous = identities.get(run.run_id)
        if previous is not None and previous != run:
            raise RuntimeError(f"conflicting duplicate workflow run ID {run.run_id}")
        identities[run.run_id] = run
    return identities


def _run_shard_checkpoint_path(
    directory: Path,
    *,
    repository_id: int,
    lower: datetime,
    upper: datetime,
) -> Path:
    digest = canonical_json_sha256([repository_id, lower.isoformat(), upper.isoformat()])
    return directory / str(repository_id) / f"{digest}.json"


def _write_run_shard_checkpoint(
    path: Path,
    *,
    repository_id: int,
    full_name: str,
    lower: datetime,
    upper: datetime,
    identities: Mapping[int, D0WorkflowRunIdentity],
    unresolved_truncation_count: int,
    conflicting_duplicate_run_ids: int,
    run_api_access: bool,
    reported_total_count: int | None,
) -> None:
    payload: dict[str, Any] = {
        "repository_id": repository_id,
        "full_name": full_name,
        "lower_utc": lower.isoformat(),
        "upper_utc": upper.isoformat(),
        "run_api_access": run_api_access,
        "reported_total_count": reported_total_count,
        "unresolved_truncation_count": unresolved_truncation_count,
        "conflicting_duplicate_run_ids": conflicting_duplicate_run_ids,
        "runs": [identities[run_id].allowed_payload() for run_id in sorted(identities)],
    }
    _write_json(path, payload)


def _load_run_shard_checkpoint(
    path: Path,
    *,
    repository_id: int,
    full_name: str,
    lower: datetime,
    upper: datetime,
) -> tuple[dict[int, D0WorkflowRunIdentity], int, int, bool]:
    payload = _load_json(path)
    assert_outcome_blind_payload(payload)
    if payload.get("canonical_payload_sha256") != _canonical_without_digest(payload):
        raise RuntimeError("workflow-run shard checkpoint hash mismatch")
    observed_source = (
        int(payload["repository_id"]),
        str(payload["full_name"]),
        parse_utc(str(payload["lower_utc"])),
        parse_utc(str(payload["upper_utc"])),
    )
    if observed_source != (repository_id, full_name, lower, upper):
        raise RuntimeError("workflow-run shard checkpoint source mismatch")
    identities: dict[int, D0WorkflowRunIdentity] = {}
    for raw in _sequence(payload.get("runs"), label="workflow-run shard identities"):
        run = workflow_run_from_payload(_mapping(raw, label="workflow-run shard identity"))
        if run.run_id in identities:
            raise RuntimeError("duplicate workflow-run ID in shard checkpoint")
        identities[run.run_id] = run
    reported_total = payload.get("reported_total_count")
    unresolved_truncation_count = int(payload["unresolved_truncation_count"])
    if (
        reported_total is not None
        and unresolved_truncation_count == 0
        and bool(payload["run_api_access"])
        and int(reported_total) != len(identities)
    ):
        raise RuntimeError("workflow-run shard checkpoint count mismatch")
    return (
        identities,
        unresolved_truncation_count,
        int(payload["conflicting_duplicate_run_ids"]),
        bool(payload["run_api_access"]),
    )


def _acquire_run_interval(
    client: GitHubApiClient,
    *,
    repository_id: int,
    full_name: str,
    lower: datetime,
    upper: datetime,
    config: Mapping[str, Any],
    shard_checkpoint_directory: Path,
    stop_event: threading.Event,
) -> tuple[dict[int, D0WorkflowRunIdentity], int, int, bool]:
    if stop_event.is_set():
        raise RuntimeError("workflow-run acquisition cancelled after a peer transport failure")
    checkpoint_path = _run_shard_checkpoint_path(
        shard_checkpoint_directory,
        repository_id=repository_id,
        lower=lower,
        upper=upper,
    )
    if checkpoint_path.exists():
        return _load_run_shard_checkpoint(
            checkpoint_path,
            repository_id=repository_id,
            full_name=full_name,
            lower=lower,
            upper=upper,
        )
    github = _mapping(config.get("github"), label="GitHub config")
    per_page = int(github["workflow_runs_per_page"])
    threshold = int(github["recursive_time_shard_threshold"])
    minimum_seconds = int(
        _mapping(config["run_identity"], label="run identity")["pagination"]["minimum_shard_seconds"]
    )
    dependabot_login = str(config["run_identity"]["bot_mapping"]["dependabot_login"])
    first_payload = client.request_json(
        f"/repos/{full_name}/actions/runs",
        endpoint_class="workflow_run_identity",
        params={"created": _format_range(lower, upper), "per_page": per_page, "page": 1},
        allow_not_found=True,
    )
    if first_payload is None:
        _write_run_shard_checkpoint(
            checkpoint_path,
            repository_id=repository_id,
            full_name=full_name,
            lower=lower,
            upper=upper,
            identities={},
            unresolved_truncation_count=0,
            conflicting_duplicate_run_ids=0,
            run_api_access=False,
            reported_total_count=None,
        )
        return {}, 0, 0, False
    first_root = _mapping(first_payload, label="workflow runs response")
    total_count = first_root.get("total_count")
    if isinstance(total_count, bool) or not isinstance(total_count, int) or total_count < 0:
        raise RuntimeError("workflow run total_count is invalid")
    span_seconds = int((upper - lower).total_seconds()) + 1
    if total_count > threshold:
        if span_seconds <= minimum_seconds:
            _write_run_shard_checkpoint(
                checkpoint_path,
                repository_id=repository_id,
                full_name=full_name,
                lower=lower,
                upper=upper,
                identities={},
                unresolved_truncation_count=1,
                conflicting_duplicate_run_ids=0,
                run_api_access=True,
                reported_total_count=total_count,
            )
            return {}, 1, 0, True
        left_seconds = span_seconds // 2
        left_upper = lower + timedelta(seconds=left_seconds - 1)
        right_lower = left_upper + timedelta(seconds=1)
        left, left_truncated, left_conflicts, left_access = _acquire_run_interval(
            client,
            repository_id=repository_id,
            full_name=full_name,
            lower=lower,
            upper=left_upper,
            config=config,
            shard_checkpoint_directory=shard_checkpoint_directory,
            stop_event=stop_event,
        )
        right, right_truncated, right_conflicts, right_access = _acquire_run_interval(
            client,
            repository_id=repository_id,
            full_name=full_name,
            lower=right_lower,
            upper=upper,
            config=config,
            shard_checkpoint_directory=shard_checkpoint_directory,
            stop_event=stop_event,
        )
        conflicts = left_conflicts + right_conflicts
        for run_id, run in right.items():
            previous = left.get(run_id)
            if previous is not None and previous != run:
                conflicts += 1
            else:
                left[run_id] = run
        return left, left_truncated + right_truncated, conflicts, left_access and right_access
    raw_runs = list(_sequence(first_root.get("workflow_runs", []), label="workflow runs"))
    pages = math.ceil(total_count / per_page) if total_count else 0
    for page in range(2, pages + 1):
        if stop_event.is_set():
            raise RuntimeError("workflow-run acquisition cancelled after a peer transport failure")
        payload = client.request_json(
            f"/repos/{full_name}/actions/runs",
            endpoint_class="workflow_run_identity",
            params={"created": _format_range(lower, upper), "per_page": per_page, "page": page},
        )
        root = _mapping(payload, label="workflow runs response")
        if root.get("total_count") != total_count:
            raise RuntimeError("workflow run total_count changed during one frozen shard")
        raw_runs.extend(_sequence(root.get("workflow_runs", []), label="workflow runs"))
    identities: dict[int, D0WorkflowRunIdentity] = {}
    conflicts = 0
    for run_id, run in _run_identity_map(raw_runs, dependabot_login=dependabot_login).items():
        previous = identities.get(run_id)
        if previous is not None and previous != run:
            conflicts += 1
        else:
            identities[run_id] = run
    if len(identities) != total_count:
        raise RuntimeError(
            f"workflow run identity count mismatch for {full_name}: {len(identities)} != {total_count}"
        )
    _write_run_shard_checkpoint(
        checkpoint_path,
        repository_id=repository_id,
        full_name=full_name,
        lower=lower,
        upper=upper,
        identities=identities,
        unresolved_truncation_count=0,
        conflicting_duplicate_run_ids=conflicts,
        run_api_access=True,
        reported_total_count=total_count,
    )
    return identities, 0, conflicts, True


def _acquire_repository_runs(
    client: GitHubApiClient,
    candidate: Mapping[str, Any],
    config: Mapping[str, Any],
    shard_checkpoint_directory: Path,
    stop_event: threading.Event,
) -> D0RepositoryIdentityRecord:
    windows = _mapping(config.get("windows"), label="windows")
    lower = parse_utc(str(windows["identity_acquisition_from_utc"]))
    upper = parse_utc(str(windows["identity_acquisition_to_utc"]))
    identities, truncation_count, conflict_count, run_api_access = _acquire_run_interval(
        client,
        repository_id=int(candidate["repository_id"]),
        full_name=str(candidate["full_name"]),
        lower=lower,
        upper=upper,
        config=config,
        shard_checkpoint_directory=shard_checkpoint_directory,
        stop_event=stop_event,
    )
    return D0RepositoryIdentityRecord(
        repository_id=int(candidate["repository_id"]),
        full_name=str(candidate["full_name"]),
        cohort=str(candidate["cohort"]),
        run_api_access=run_api_access,
        unresolved_truncation_count=truncation_count,
        conflicting_duplicate_run_ids=conflict_count,
        runs=tuple(sorted(identities.values(), key=lambda run: (run.created_at, run.run_id))),
        schema_probes=(),
    )


def _acquire_jobs(
    client: GitHubApiClient,
    *,
    full_name: str,
    run_id: int,
    config: Mapping[str, Any],
) -> tuple[bool, tuple[D0WorkflowJobSchema, ...]]:
    github = _mapping(config.get("github"), label="GitHub config")
    per_page = int(github["workflow_jobs_per_page"])
    page = 1
    jobs: dict[int, D0WorkflowJobSchema] = {}
    total_count: int | None = None
    while True:
        payload = client.request_json(
            f"/repos/{full_name}/actions/runs/{run_id}/jobs",
            endpoint_class="workflow_job_schema",
            params={"filter": str(github["workflow_jobs_filter"]), "per_page": per_page, "page": page},
            allow_not_found=True,
        )
        if payload is None:
            return False, ()
        root = _mapping(payload, label="workflow jobs response")
        observed_count = root.get("total_count")
        if isinstance(observed_count, bool) or not isinstance(observed_count, int) or observed_count < 0:
            raise RuntimeError("workflow job total_count is invalid")
        if total_count is None:
            total_count = observed_count
        elif total_count != observed_count:
            raise RuntimeError("workflow job total_count changed during pagination")
        raw_jobs = _sequence(root.get("jobs", []), label="workflow jobs")
        for raw in raw_jobs:
            job = sanitize_d0_workflow_job(_mapping(raw, label="workflow job"), run_id=run_id)
            previous = jobs.get(job.job_id)
            if previous is not None and previous != job:
                raise RuntimeError(f"conflicting duplicate workflow job ID {job.job_id}")
            jobs[job.job_id] = job
        if page * per_page >= observed_count:
            break
        page += 1
    if total_count is not None and len(jobs) != total_count:
        raise RuntimeError("workflow job identity count does not match total_count")
    return True, tuple(sorted(jobs.values(), key=lambda job: job.job_id))


def _acquire_workflow_structure(
    client: GitHubApiClient,
    *,
    full_name: str,
    run: D0WorkflowRunIdentity,
    maximum_bytes: int,
) -> WorkflowStructureSummary | None:
    try:
        normalized_path = normalize_workflow_path(run.workflow_path)
    except ValueError:
        return None
    payload = client.request_json(
        f"/repos/{full_name}/contents/{quote(normalized_path, safe='/')}",
        endpoint_class="workflow_structure",
        params={"ref": run.head_sha},
        allow_not_found=True,
    )
    if payload is None:
        return None
    root = _mapping(payload, label="workflow content response")
    if root.get("encoding") != "base64":
        return None
    encoded = str(root.get("content", "")).replace("\n", "")
    try:
        content_bytes = base64.b64decode(encoded, validate=True)
    except ValueError:
        return None
    if len(content_bytes) > maximum_bytes:
        return None
    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return summarize_workflow_structure(content)


def _acquire_repository_probes(
    client: GitHubApiClient,
    record: D0RepositoryIdentityRecord,
    config: Mapping[str, Any],
    runtime: Mapping[str, Any],
    stop_event: threading.Event,
) -> D0RepositoryIdentityRecord:
    windows = _mapping(config.get("windows"), label="windows")
    per_actor = int(config["runner_pool"]["preperiod_probe_runs_per_repository_actor_class"])
    selected = deterministic_probe_runs(
        record,
        pre_from_utc=str(windows["primary_pre_from_utc"]),
        pre_to_utc=str(windows["primary_pre_to_utc"]),
        per_actor_class=per_actor,
    )
    maximum_bytes = int(runtime["execution"]["workflow_content_maximum_bytes"])
    probes: list[D0SchemaProbe] = []
    for actor_class, run in selected:
        if stop_event.is_set():
            raise RuntimeError("schema-probe acquisition cancelled after a peer transport failure")
        access, jobs = _acquire_jobs(
            client,
            full_name=record.full_name,
            run_id=run.run_id,
            config=config,
        )
        structure = _acquire_workflow_structure(
            client,
            full_name=record.full_name,
            run=run,
            maximum_bytes=maximum_bytes,
        )
        probes.append(
            D0SchemaProbe(
                run_id=run.run_id,
                actor_class=actor_class,
                job_api_access=access,
                jobs=jobs,
                workflow_structure=structure,
            )
        )
    return replace(record, schema_probes=tuple(probes))


def _selected_structure_checkpoint_path(directory: Path, key: WorkflowStructureKey) -> Path:
    repository_id, head_sha, workflow_path = key
    digest = canonical_json_sha256([repository_id, head_sha, workflow_path])
    return directory / str(repository_id) / f"{digest}.json"


def _load_selected_structure_checkpoint(
    path: Path, expected_key: WorkflowStructureKey
) -> WorkflowStructureSummary | None:
    payload = _load_json(path)
    assert_outcome_blind_payload(payload)
    if payload.get("canonical_payload_sha256") != _canonical_without_digest(payload):
        raise RuntimeError("selected workflow-structure checkpoint hash mismatch")
    observed_key = (
        int(payload["repository_id"]),
        str(payload["head_sha"]),
        str(payload["workflow_path"]),
    )
    if observed_key != expected_key:
        raise RuntimeError("selected workflow-structure checkpoint source mismatch")
    raw_structure = payload.get("workflow_structure")
    if raw_structure is None:
        return None
    return workflow_structure_from_payload(_mapping(raw_structure, label="selected workflow structure"))


def _acquire_selected_primary_structures(
    client: GitHubApiClient,
    provisional_runs: Sequence[Mapping[str, Any]],
    records_by_id: Mapping[int, D0RepositoryIdentityRecord],
    runtime: Mapping[str, Any],
    *,
    raw_directory: Path,
    maximum_workers: int,
    started: float,
) -> dict[WorkflowStructureKey, WorkflowStructureSummary | None]:
    execution = _mapping(runtime.get("execution"), label="runtime execution")
    checkpoint_directory = raw_directory / str(execution["selected_workflow_structure_checkpoint_directory"])
    maximum_bytes = int(execution["workflow_content_maximum_bytes"])
    source_runs: dict[WorkflowStructureKey, tuple[str, D0WorkflowRunIdentity]] = {}
    run_maps = {
        repository_id: {run.run_id: run for run in record.runs}
        for repository_id, record in records_by_id.items()
    }
    for raw in provisional_runs:
        row = _mapping(raw, label="provisional selected run")
        if row.get("sample_class") != "primary":
            continue
        key = selected_workflow_structure_key(row)
        run_payload = _mapping(row.get("run"), label="selected run identity")
        run_id = int(run_payload["run_id"])
        record = records_by_id[key[0]]
        run = run_maps[key[0]].get(run_id)
        if run is None or (key[0], run.head_sha, run.workflow_path) != key:
            raise RuntimeError("selected workflow source does not match an identity record")
        source_runs.setdefault(key, (record.full_name, run))
    structures: dict[WorkflowStructureKey, WorkflowStructureSummary | None] = {}
    missing: dict[WorkflowStructureKey, tuple[str, D0WorkflowRunIdentity]] = {}
    for key, source in sorted(source_runs.items()):
        checkpoint_path = _selected_structure_checkpoint_path(checkpoint_directory, key)
        if checkpoint_path.exists():
            structures[key] = _load_selected_structure_checkpoint(checkpoint_path, key)
        else:
            missing[key] = source
    last_progress = time.monotonic()
    missing_items = [(key, full_name, run) for key, (full_name, run) in missing.items()]
    completed_structures = 0

    def acquire_structure_worker(
        item: tuple[WorkflowStructureKey, str, D0WorkflowRunIdentity],
        stop_event: threading.Event,
    ) -> WorkflowStructureSummary | None:
        if stop_event.is_set():
            raise RuntimeError("selected workflow-structure acquisition cancelled after a peer failure")
        _, full_name, run = item
        return _acquire_workflow_structure(
            client,
            full_name=full_name,
            run=run,
            maximum_bytes=maximum_bytes,
        )

    def persist_structure(
        item: tuple[WorkflowStructureKey, str, D0WorkflowRunIdentity],
        structure: WorkflowStructureSummary | None,
    ) -> None:
        nonlocal completed_structures, last_progress
        key, _, _ = item
        payload: dict[str, Any] = {
            "repository_id": key[0],
            "head_sha": key[1],
            "workflow_path": key[2],
            "workflow_structure": structure.allowed_payload() if structure is not None else None,
        }
        _write_json(_selected_structure_checkpoint_path(checkpoint_directory, key), payload)
        structures[key] = structure
        completed_structures += 1
        now = time.monotonic()
        if now - last_progress >= float(execution["progress_interval_seconds"]):
            print(
                json.dumps(
                    {
                        "stage": "selected_workflow_structures",
                        "completed_this_run": completed_structures,
                        "total_missing": len(missing),
                        "total_unique_sources": len(source_runs),
                        "elapsed_seconds": round(now - started, 1),
                    },
                    sort_keys=True,
                    allow_nan=False,
                ),
                flush=True,
            )
            last_progress = now

    _run_bounded_stage(
        missing_items,
        maximum_workers=maximum_workers,
        worker=acquire_structure_worker,
        on_success=persist_structure,
        error_message=("selected workflow-structure acquisition stopped after preserving checkpoints"),
    )
    if set(structures) != set(source_runs):
        raise RuntimeError("selected workflow-structure acquisition is incomplete")
    return structures


def _checkpoint_write(path: Path, record: D0RepositoryIdentityRecord) -> None:
    payload = record.allowed_payload()
    assert_outcome_blind_payload(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    partial.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(partial, path)


def _checkpoint_load(path: Path) -> D0RepositoryIdentityRecord:
    payload = _mapping(json.loads(path.read_text(encoding="utf-8")), label="repository checkpoint")
    assert_outcome_blind_payload(payload)
    return repository_record_from_payload(payload)


def _history_incident_codes(content: bytes) -> set[str]:
    text = content.decode("utf-8")
    match = re.search(r'data-react-class="HistoryIndex" data-react-props="([^"]+)"', text)
    if match is None:
        raise RuntimeError("GitHub Status history lacks HistoryIndex data")
    props = _mapping(json.loads(html.unescape(match.group(1))), label="status history props")
    codes: set[str] = set()
    keywords = ("actions", "workflow", "hosted runner", "job queue", "jobs were degraded")
    for raw_month in _sequence(props.get("months", []), label="status months"):
        month = _mapping(raw_month, label="status month")
        for raw_incident in _sequence(month.get("incidents", []), label="status incidents"):
            incident = _mapping(raw_incident, label="status incident")
            searchable = f"{incident.get('name', '')} {incident.get('message', '')}".lower()
            code = str(incident.get("code", ""))
            if code and any(keyword in searchable for keyword in keywords):
                codes.add(code)
    return codes


def _sanitize_status_incident(
    payload: Mapping[str, Any],
    *,
    response_sha256: str,
    lower: datetime,
    upper: datetime,
) -> dict[str, Any] | None:
    incident = _mapping(payload.get("incident"), label="status incident")
    started_at = str(incident.get("started_at", ""))
    resolved_raw = incident.get("resolved_at")
    resolved_at = str(resolved_raw) if resolved_raw is not None else None
    started = parse_utc(started_at)
    resolved = parse_utc(resolved_at) if resolved_at is not None else upper
    if resolved < lower or started > upper:
        return None
    component_names = {
        str(component.get("name", ""))
        for raw_update in _sequence(incident.get("incident_updates", []), label="incident updates")
        for component in (
            _mapping(raw, label="affected component")
            for raw in _sequence(
                _mapping(raw_update, label="incident update").get("affected_components") or [],
                label="affected components",
            )
        )
        if str(component.get("name", ""))
    }
    searchable = " ".join(
        [str(incident.get("name", ""))]
        + [
            str(_mapping(raw_update, label="incident update").get("body", ""))
            for raw_update in _sequence(incident.get("incident_updates", []), label="incident updates")
        ]
    ).lower()
    keywords = ("actions", "workflow", "hosted runner", "job queue", "jobs were degraded")
    if "Actions" not in component_names and not any(keyword in searchable for keyword in keywords):
        return None
    row = {
        "incident_id": str(incident.get("id", "")),
        "title": str(incident.get("name", "")),
        "reported_start_utc": started_at,
        "reported_resolution_utc": resolved_at,
        "affected_component_names": sorted(component_names),
        "source_response_sha256": response_sha256,
    }
    assert_outcome_blind_payload(row)
    return row


def _acquire_incident_ledger(
    client: PublicStatusClient,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    incident_config = _mapping(config.get("incident_sensitivity"), label="incident sensitivity")
    history_hashes: dict[str, str] = {}
    codes: set[str] = set()
    for url in _sequence(incident_config["official_source_history_pages"], label="status history URLs"):
        content, response_sha = client.get(str(url), endpoint_class="github_status_history")
        history_hashes[str(url)] = response_sha
        codes.update(_history_incident_codes(content))
    windows = _mapping(config.get("windows"), label="windows")
    lower = parse_utc(str(windows["identity_acquisition_from_utc"]))
    upper = parse_utc(str(windows["identity_acquisition_to_utc"]))
    incidents: list[dict[str, Any]] = []
    for code in sorted(codes):
        content, response_sha = client.get(
            f"https://www.githubstatus.com/api/v2/incidents/{code}.json",
            endpoint_class="github_status_incident",
        )
        payload = _mapping(json.loads(content), label="status incident response")
        row = _sanitize_status_incident(
            payload,
            response_sha256=response_sha,
            lower=lower,
            upper=upper,
        )
        if row is not None:
            incidents.append(row)
    ledger = {
        "history_page_response_sha256": dict(sorted(history_hashes.items())),
        "incidents": sorted(
            incidents,
            key=lambda row: (row["reported_start_utc"], row["incident_id"]),
        ),
        "sensitivity_padding_seconds_each_side": 3600,
    }
    assert_outcome_blind_payload(ledger)
    ledger["canonical_payload_sha256"] = canonical_json_sha256(ledger)
    return ledger


def _select_smoke_candidates(
    candidates: Mapping[int, Mapping[str, Any]], runtime: Mapping[str, Any]
) -> dict[int, Mapping[str, Any]]:
    smoke = _mapping(runtime.get("smoke"), label="smoke config")
    limits = {
        "default_treated_high_support": int(smoke["treated_repositories"]),
        "no_dependabot_candidate_controls": int(smoke["control_repositories"]),
        "already_cooled_high_support_negative_controls": int(smoke["negative_control_repositories"]),
    }
    selected: dict[int, Mapping[str, Any]] = {}
    for cohort, limit in limits.items():
        rows = sorted(
            (row for row in candidates.values() if row["cohort"] == cohort),
            key=lambda row: hashlib.sha256(str(row["repository_id"]).encode()).hexdigest(),
        )[:limit]
        selected.update({int(row["repository_id"]): row for row in rows})
    return selected


def _smoke_raw_directory(runtime: Mapping[str, Any], requested_directory: Path | None) -> Path:
    smoke = _mapping(runtime.get("smoke"), label="smoke config")
    root = Path(str(smoke["output_directory"])).resolve()
    if requested_directory is None:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        return root / stamp
    requested = requested_directory.resolve()
    if requested.parent != root:
        raise ValueError("smoke resume directory must be an immediate child of the configured smoke root")
    if not requested.is_dir():
        raise FileNotFoundError(f"smoke resume directory does not exist: {requested}")
    if (requested / "smoke_result.json").exists() or (requested / "smoke_manifest.json").exists():
        raise FileExistsError("refusing to resume a smoke with a final artifact")
    return requested


def _write_gzip_jsonl(path: Path, payloads: Sequence[Mapping[str, Any]]) -> tuple[str, str]:
    if path.exists() or path.with_name(path.name + ".partial").exists():
        raise FileExistsError(f"refusing to overwrite immutable gzip artifact: {path}")
    rows = [dict(payload) for payload in payloads]
    assert_outcome_blind_payload(rows)
    canonical_hash = canonical_json_sha256(rows)
    lines = [json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False) for row in rows]
    raw = (("\n".join(lines) + "\n") if lines else "").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    with (
        partial.open("xb") as raw_handle,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw_handle, mtime=0) as compressed,
    ):
        compressed.write(raw)
    os.replace(partial, path)
    return canonical_hash, _sha256_file(path)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    if path.exists() or path.with_name(path.name + ".partial").exists():
        raise FileExistsError(f"refusing to overwrite immutable JSON artifact: {path}")
    assert_outcome_blind_payload(payload)
    json.dumps(payload, allow_nan=False)
    body = {key: value for key, value in payload.items() if key != "canonical_payload_sha256"}
    digest = canonical_json_sha256(body)
    existing = payload.get("canonical_payload_sha256")
    if existing is not None and existing != digest:
        raise ValueError(f"existing canonical payload hash mismatch for {path}")
    payload["canonical_payload_sha256"] = digest
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    partial.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(partial, path)


def _transport_summary(observations: Sequence[TransportObservation]) -> dict[str, Any]:
    hashes = sorted(observation.response_sha256 for observation in observations)
    resources = sorted(
        {observation.rate_resource for observation in observations if observation.rate_resource is not None}
    )
    return {
        "request_count": len(observations),
        "endpoint_class_counts": dict(sorted(Counter(row.endpoint_class for row in observations).items())),
        "http_code_counts": dict(sorted(Counter(str(row.http_code) for row in observations).items())),
        "response_hashes_sha256": canonical_json_sha256(hashes),
        "last_rate_metadata": {
            resource: {
                "remaining": next(
                    row.rate_remaining for row in reversed(observations) if row.rate_resource == resource
                ),
                "reset": next(
                    row.rate_reset for row in reversed(observations) if row.rate_resource == resource
                ),
            }
            for resource in resources
        },
    }


def _run(
    config_path: Path,
    runtime_path: Path,
    *,
    smoke: bool,
    smoke_directory: Path | None = None,
) -> dict[str, Any]:
    if smoke_directory is not None and not smoke:
        raise ValueError("--smoke-directory requires --smoke")
    config, runtime, ledger = _verify_contract(config_path, runtime_path, formal=not smoke)
    candidates: dict[int, Mapping[str, Any]] = {
        repository_id: row for repository_id, row in candidate_rows_by_id(ledger).items()
    }
    if smoke:
        candidates = _select_smoke_candidates(candidates, runtime)
        raw_directory = _smoke_raw_directory(runtime, smoke_directory)
        result_path = raw_directory / "smoke_result.json"
        manifest_path = raw_directory / "smoke_manifest.json"
    else:
        raw_directory = _resolve_repo_path(runtime["execution"]["raw_directory"])
        result_path = _resolve_repo_path(runtime["execution"]["result_path"])
        manifest_path = _resolve_repo_path(runtime["execution"]["manifest_path"])
        if result_path.exists() or manifest_path.exists():
            raise FileExistsError("formal D0 result or manifest already exists")
    checkpoint_directory = raw_directory / str(runtime["execution"]["repository_checkpoint_directory"])
    journal = TransportJournal(raw_directory / "transport_observations.jsonl")
    github_client = GitHubApiClient(config, runtime, journal=journal)
    status_client = PublicStatusClient(
        timeout=float(config["github"]["timeout_seconds"]),
        attempts=int(config["github"]["attempts"]),
        backoffs=[float(value) for value in config["github"]["backoff_seconds"]],
        journal=journal,
    )
    records_by_id: dict[int, D0RepositoryIdentityRecord] = {}
    missing_runs: list[Mapping[str, Any]] = []
    for repository_id, candidate in sorted(candidates.items()):
        checkpoint_path = checkpoint_directory / f"{repository_id}.json"
        if checkpoint_path.exists():
            record = _checkpoint_load(checkpoint_path)
            if record.repository_id != repository_id or record.full_name != candidate["full_name"]:
                raise RuntimeError("D0 checkpoint does not match the frozen candidate")
            records_by_id[repository_id] = record
        else:
            missing_runs.append(candidate)
    max_workers = int(config["github"]["maximum_parallel_requests"])
    started = time.monotonic()
    last_progress = started
    shard_checkpoint_directory = raw_directory / str(
        runtime["execution"]["repository_time_shard_checkpoint_directory"]
    )
    completed_this_run = 0

    def acquire_runs_worker(
        candidate: Mapping[str, Any], stop_event: threading.Event
    ) -> D0RepositoryIdentityRecord:
        return _acquire_repository_runs(
            github_client,
            candidate,
            config,
            shard_checkpoint_directory,
            stop_event,
        )

    def persist_run_record(candidate: Mapping[str, Any], record: D0RepositoryIdentityRecord) -> None:
        nonlocal completed_this_run, last_progress
        if record.repository_id != int(candidate["repository_id"]):
            raise RuntimeError("D0 future returned the wrong repository")
        _checkpoint_write(checkpoint_directory / f"{record.repository_id}.json", record)
        records_by_id[record.repository_id] = record
        completed_this_run += 1
        now = time.monotonic()
        if now - last_progress >= float(runtime["execution"]["progress_interval_seconds"]):
            print(
                json.dumps(
                    {
                        "stage": "run_identities",
                        "completed_this_run": completed_this_run,
                        "total_missing": len(missing_runs),
                        "total_candidates": len(candidates),
                        "elapsed_seconds": round(now - started, 1),
                    },
                    sort_keys=True,
                    allow_nan=False,
                ),
                flush=True,
            )
            last_progress = now

    _run_bounded_stage(
        missing_runs,
        maximum_workers=max_workers,
        worker=acquire_runs_worker,
        on_success=persist_run_record,
        error_message=("workflow-run acquisition stopped after preserving every completed bounded task"),
    )
    identity_records = [records_by_id[repository_id] for repository_id in sorted(records_by_id)]
    windows = _mapping(config.get("windows"), label="windows")
    minimum_primary_runs = int(config["prequalification"]["minimum_primary_human_run_identities"])
    identity_stage = evaluate_d0_identity_prerequisites(
        identity_records,
        windows=windows,
        minimum_primary_runs=minimum_primary_runs,
        gates=config["gates"],
    )
    acquire_probes = smoke or bool(identity_stage["probe_stage_authorized"])
    missing_probes = (
        [record for record in identity_records if not record.schema_probes] if acquire_probes else []
    )
    completed_probes = 0

    def acquire_probe_worker(
        record: D0RepositoryIdentityRecord, stop_event: threading.Event
    ) -> D0RepositoryIdentityRecord:
        return _acquire_repository_probes(github_client, record, config, runtime, stop_event)

    def persist_probe_record(source: D0RepositoryIdentityRecord, record: D0RepositoryIdentityRecord) -> None:
        nonlocal completed_probes, last_progress
        if source.repository_id != record.repository_id:
            raise RuntimeError("schema-probe future returned the wrong repository")
        _checkpoint_write(checkpoint_directory / f"{record.repository_id}.json", record)
        records_by_id[record.repository_id] = record
        completed_probes += 1
        now = time.monotonic()
        if now - last_progress >= float(runtime["execution"]["progress_interval_seconds"]):
            print(
                json.dumps(
                    {
                        "stage": "schema_probes",
                        "completed_this_run": completed_probes,
                        "total_missing": len(missing_probes),
                        "total_candidates": len(candidates),
                        "elapsed_seconds": round(now - started, 1),
                    },
                    sort_keys=True,
                    allow_nan=False,
                ),
                flush=True,
            )
            last_progress = now

    _run_bounded_stage(
        missing_probes,
        maximum_workers=max_workers,
        worker=acquire_probe_worker,
        on_success=persist_probe_record,
        error_message="schema-probe acquisition stopped after preserving completed records",
    )
    records = [records_by_id[repository_id] for repository_id in sorted(records_by_id)]
    features = [
        build_match_features(
            record,
            candidates[record.repository_id],
            pre_from_utc=str(windows["primary_pre_from_utc"]),
            pre_to_utc=str(windows["primary_pre_to_utc"]),
            config_cutoff_utc=str(config["intervention"]["config_cutoff_utc"]),
        )
        for record in records
    ]
    treated = [
        feature
        for feature in features
        if feature.cohort == "default_treated_high_support"
        and is_prequalified(feature, minimum_primary_runs=minimum_primary_runs)
    ]
    controls = [
        feature
        for feature in features
        if feature.cohort == "no_dependabot_candidate_controls"
        and is_prequalified(feature, minimum_primary_runs=minimum_primary_runs)
    ]
    matching_config = _mapping(config.get("matching"), label="matching")
    minimum_match = int(config["gates"]["minimum_matched_treated_repositories"])
    if smoke:
        minimum_match = 1
    matching = optimal_repository_match(
        treated,
        controls,
        ratio=int(matching_config["ratio"]),
        minimum_treated=minimum_match,
        maximum_scaled_primary_difference=float(
            matching_config["distance_caliper"]["maximum_scaled_absolute_difference"]
        ),
    )
    included_ids = {
        int(value)
        for value in [
            *matching.get("matched_treated_repository_ids", []),
            *matching.get("matched_control_repository_ids", []),
        ]
    }
    included_ids.update(
        record.repository_id
        for record in records
        if record.cohort == "already_cooled_high_support_negative_controls"
    )
    sampling = _mapping(config["run_identity"]["deterministic_d1_sampling"], label="sampling")
    provisional_runs = select_d1_run_identities(
        records,
        included_repository_ids=included_ids,
        windows=windows,
        primary_events={str(value) for value in config["run_identity"]["primary_human"]["event_types"]},
        secondary_events={str(value) for value in config["run_identity"]["secondary_human"]["event_types"]},
        primary_daily_cap=int(sampling["maximum_primary_runs_per_repository_utc_date"]),
        secondary_daily_cap=int(sampling["maximum_secondary_runs_per_repository_utc_date"]),
    )
    raw_max_smd = matching.get("maximum_absolute_standardized_mean_difference")
    raw_mean_smd = matching.get("mean_absolute_standardized_mean_difference")
    maximum_smd = (
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
    maximum_allowed_smd = float(matching_config["maximum_absolute_standardized_mean_difference"])
    maximum_allowed_mean_smd = float(matching_config["maximum_mean_absolute_standardized_mean_difference"])
    structure_stage_authorized = (
        bool(matching.get("matching_complete"))
        and maximum_smd is not None
        and mean_smd is not None
        and maximum_smd <= maximum_allowed_smd
        and mean_smd <= maximum_allowed_mean_smd
    )
    if structure_stage_authorized:
        selected_structures = _acquire_selected_primary_structures(
            github_client,
            provisional_runs,
            records_by_id,
            runtime,
            raw_directory=raw_directory,
            maximum_workers=max_workers,
            started=started,
        )
        selected_runs, selection_metrics = finalize_d1_run_identities(provisional_runs, selected_structures)
        selection_status = "frozen_after_per_run_workflow_structure_exclusion"
    else:
        selected_runs = []
        selection_metrics = {
            "provisional_primary_runs": sum(
                _mapping(row, label="provisional run").get("sample_class") == "primary"
                for row in provisional_runs
            ),
            "primary_workflow_structures_recovered": 0,
            "primary_runs_excluded_missing_structure": 0,
            "primary_runs_excluded_intentional_wait": 0,
            "primary_workflow_structure_recovery_rate": 0.0,
            "final_selected_runs": 0,
        }
        selection_status = "not_frozen_because_matching_or_balance_prerequisite_failed"
    incident_ledger = _acquire_incident_ledger(status_client, config)
    incident_path = raw_directory / str(runtime["execution"]["incident_ledger_filename"])
    if incident_path.exists():
        existing_incidents = _load_json(incident_path)
        if existing_incidents != incident_ledger:
            raise RuntimeError("official incident ledger changed within one D0 execution")
    else:
        _write_json(incident_path, incident_ledger)
    record_payloads = [record.allowed_payload() for record in records]
    identity_path = raw_directory / str(runtime["execution"]["allowed_identity_records_filename"])
    identity_canonical, identity_file = _write_gzip_jsonl(identity_path, record_payloads)
    sample_path = raw_directory / str(runtime["execution"]["selected_d1_sample_filename"])
    sample_canonical, sample_file = _write_gzip_jsonl(sample_path, selected_runs)
    with gzip.open(identity_path, "rt", encoding="utf-8") as handle:
        identity_roundtrip = [json.loads(line) for line in handle]
    with gzip.open(sample_path, "rt", encoding="utf-8") as handle:
        sample_roundtrip = [json.loads(line) for line in handle]
    deterministic = (
        canonical_json_sha256(identity_roundtrip) == identity_canonical
        and canonical_json_sha256(sample_roundtrip) == sample_canonical
    )
    support = evaluate_d0_support(
        records,
        features,
        matching,
        selected_runs,
        gates=config["gates"],
        minimum_primary_runs=minimum_primary_runs,
        maximum_absolute_smd=maximum_allowed_smd,
        maximum_mean_smd=maximum_allowed_mean_smd,
        deterministic_hash_matches=deterministic,
        candidate_hashes_exact=True,
    )
    if smoke:
        support["scientific_decision"] = str(runtime["smoke"]["scientific_decision"])
    transport = _transport_summary(journal.observations)
    result: dict[str, Any] = {
        "schema_version": 1,
        "audit": "github_dependabot_cooldown_d0",
        "mode": "smoke" if smoke else "formal",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "git_sha": _git("rev-parse", "HEAD"),
        "worktree_clean_at_finalization": not bool(_git("status", "--porcelain", "--untracked-files=all")),
        "config_sha256": _sha256_file(config_path),
        "runtime_sha256": _sha256_file(runtime_path),
        "execution_history": dict(
            _mapping(runtime["contract"].get("execution_history", {}), label="execution history")
        ),
        "candidate_ledger": {
            "file_sha256": config["source"]["candidate_ledger_file_sha256"],
            "canonical_payload_sha256": config["source"]["candidate_ledger_canonical_sha256"],
            "candidate_count": len(candidates),
        },
        "outcome_seal": {
            "queue_first_stage_review_merge_security_values_persisted_or_analyzed": False,
            "identity_records_canonical_sha256": identity_canonical,
            "identity_records_file_sha256": identity_file,
            "selected_sample_canonical_sha256": sample_canonical,
            "selected_sample_file_sha256": sample_file,
        },
        "support": support,
        "matching": matching,
        "identity_stage": {
            **identity_stage,
            "probe_stage_state": (
                "completed_or_resumed"
                if acquire_probes
                else "not_run_because_a_necessary_identity_prerequisite_failed"
            ),
        },
        "d1_identity_freeze": {
            "state": selection_status,
            "provisional_sample_count": len(provisional_runs),
            **selection_metrics,
        },
        "selected_sample_count": len(selected_runs),
        "incident_ledger": {
            "canonical_payload_sha256": incident_ledger["canonical_payload_sha256"],
            "incident_count": len(incident_ledger["incidents"]),
        },
        "transport": transport,
        "elapsed_seconds": time.monotonic() - started,
    }
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "audit": "github_dependabot_cooldown_d0",
        "mode": result["mode"],
        "git_sha": result["git_sha"],
        "worktree_clean_at_finalization": result["worktree_clean_at_finalization"],
        "config_path": config_path.relative_to(REPO_ROOT).as_posix(),
        "config_sha256": result["config_sha256"],
        "runtime_path": runtime_path.relative_to(REPO_ROOT).as_posix(),
        "runtime_sha256": result["runtime_sha256"],
        "execution_history": result["execution_history"],
        "candidate_ledger_path": str(config["source"]["candidate_ledger_path"]),
        "candidate_ledger_file_sha256": config["source"]["candidate_ledger_file_sha256"],
        "raw_artifacts": {
            "identity_records": {
                "path": identity_path.relative_to(REPO_ROOT).as_posix()
                if REPO_ROOT in identity_path.parents
                else str(identity_path),
                "file_sha256": identity_file,
                "canonical_sha256": identity_canonical,
            },
            "selected_d1_sample": {
                "path": sample_path.relative_to(REPO_ROOT).as_posix()
                if REPO_ROOT in sample_path.parents
                else str(sample_path),
                "file_sha256": sample_file,
                "canonical_sha256": sample_canonical,
            },
            "incident_ledger": {
                "path": incident_path.relative_to(REPO_ROOT).as_posix()
                if REPO_ROOT in incident_path.parents
                else str(incident_path),
                "file_sha256": _sha256_file(incident_path),
                "canonical_sha256": incident_ledger["canonical_payload_sha256"],
            },
        },
        "forbidden_raw_or_derived_outcome_persisted": False,
        "transport": transport,
    }
    _write_json(result_path, result)
    _write_json(manifest_path, manifest)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--runtime", type=Path, default=RUNTIME_PATH)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument(
        "--smoke-directory",
        type=Path,
        help="resume an incomplete smoke from an existing child of the configured smoke root",
    )
    args = parser.parse_args()
    result = _run(
        args.config.resolve(),
        args.runtime.resolve(),
        smoke=bool(args.smoke),
        smoke_directory=args.smoke_directory,
    )
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
