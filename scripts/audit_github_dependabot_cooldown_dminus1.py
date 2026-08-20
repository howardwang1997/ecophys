"""Run the frozen outcome-blind GitHub Dependabot cooldown D-1 audit."""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import os
import subprocess
import threading
import time
from collections import Counter
from collections.abc import Mapping, Sequence
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
import yaml

from ecomd.data.github_verification_liquidity import (
    DependabotConfigSummary,
    PullRequestEvent,
    RepositoryFrameEntry,
    RepositorySupport,
    WorkflowJobSchema,
    assert_outcome_blind_payload,
    canonical_json_sha256,
    evaluate_dminus1_support,
    sanitize_pull_request_node,
    sanitize_repository,
    sanitize_workflow_job,
    sanitize_workflow_run,
    summarize_dependabot_config,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs/agent_markets/github_dependabot_cooldown_dminus1_v1.yaml"
RUNTIME_PATH = REPO_ROOT / "configs/agent_markets/github_dependabot_cooldown_dminus1_runtime_v1.yaml"


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


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _resolve_repo_path(relative: Any) -> Path:
    path = (REPO_ROOT / str(relative)).resolve()
    if REPO_ROOT.resolve() not in path.parents:
        raise ValueError("runtime path escapes the repository")
    return path


def _verify_contract(config_path: Path, runtime_path: Path, *, formal: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    config = _load_yaml(config_path)
    runtime = _load_yaml(runtime_path)
    contract = config.get("contract")
    runtime_contract = runtime.get("contract")
    if not isinstance(contract, Mapping) or not isinstance(runtime_contract, Mapping):
        raise RuntimeError("D-1 config lacks a contract")
    expected_status = "frozen_before_formal_frame_acquisition"
    if contract.get("status") != expected_status or runtime_contract.get("status") != expected_status:
        raise RuntimeError("D-1 contract is not frozen")
    expected_parent_path = str(config_path.relative_to(REPO_ROOT))
    if runtime_contract.get("parent_config_path") != expected_parent_path:
        raise RuntimeError("runtime parent config path mismatch")
    observed_parent_hash = _sha256_file(config_path)
    if runtime_contract.get("parent_config_sha256") != observed_parent_hash:
        raise RuntimeError("runtime parent config hash mismatch")
    preregistration_sha = str(runtime_contract.get("preregistration_git_sha"))
    committed_config = subprocess.run(
        ["git", "show", f"{preregistration_sha}:{expected_parent_path}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    if hashlib.sha256(committed_config).hexdigest() != observed_parent_hash:
        raise RuntimeError("scientific config differs from the pushed preregistration")
    if _git("branch", "--show-current") != contract.get("branch"):
        raise RuntimeError("D-1 is running on the wrong branch")
    if runtime_contract.get("scientific_frame_metrics_gates_and_forbidden_fields_unchanged") is not True:
        raise RuntimeError("runtime contract does not preserve the scientific contract")
    if formal and _git("status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("formal D-1 requires a clean worktree")
    return config, runtime


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


class GitHubApiClient:
    """Minimal authenticated client that records hashes but never raw outcome payloads."""

    def __init__(
        self,
        config: Mapping[str, Any],
        runtime: Mapping[str, Any],
        *,
        transport_journal_path: Path,
    ) -> None:
        github = config["github"]
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
        self.limiter = RequestStartLimiter(float(runtime["execution"]["request_start_interval_seconds"]))
        self.local = threading.local()
        self.transport_journal_path = transport_journal_path
        self.transport: list[TransportObservation] = self._load_transport_journal()
        self.transport_lock = threading.Lock()

    def _load_transport_journal(self) -> list[TransportObservation]:
        if not self.transport_journal_path.exists():
            return []
        observations: list[TransportObservation] = []
        for line in self.transport_journal_path.read_text(encoding="utf-8").splitlines():
            payload = json.loads(line)
            root = _mapping(payload, label="transport checkpoint")
            assert_outcome_blind_payload(root)
            observations.append(TransportObservation(**dict(root)))
        return observations

    def _session(self) -> requests.Session:
        session = getattr(self.local, "session", None)
        if not isinstance(session, requests.Session):
            session = requests.Session()
            session.headers.update(self.headers)
            self.local.session = session
        return session

    def request_json(
        self,
        method: str,
        path: str,
        *,
        endpoint_class: str,
        params: Mapping[str, Any] | None = None,
        body: Mapping[str, Any] | None = None,
        allow_not_found: bool = False,
    ) -> Any:
        """Request JSON with the frozen retry policy and rate-budget guard."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        last_error: Exception | None = None
        for attempt in range(self.attempts):
            self.limiter.wait()
            try:
                response = self._session().request(
                    method,
                    url,
                    params=params,
                    json=body,
                    timeout=self.timeout,
                )
                if response.status_code == 404 and allow_not_found:
                    self._record_transport(endpoint_class, response)
                    return None
                if (response.status_code == 429 or response.status_code >= 500) and attempt + 1 < self.attempts:
                    time.sleep(self.backoffs[min(attempt, len(self.backoffs) - 1)])
                    continue
                response.raise_for_status()
                self._record_transport(endpoint_class, response)
                payload = response.json()
                self._guard_rate(response)
                return payload
            except (requests.RequestException, ValueError) as error:
                last_error = error
                if attempt + 1 < self.attempts:
                    time.sleep(self.backoffs[min(attempt, len(self.backoffs) - 1)])
        raise RuntimeError(f"GitHub transport failed for {endpoint_class}") from last_error

    def graphql(self, query: str, variables: Mapping[str, Any], *, endpoint_class: str) -> Mapping[str, Any]:
        """Execute a read-only GraphQL query and reject API-level errors."""
        payload = self.request_json(
            "POST",
            "/graphql",
            endpoint_class=endpoint_class,
            body={"query": query, "variables": dict(variables)},
        )
        root = _mapping(payload, label="GraphQL response")
        if root.get("errors"):
            raise RuntimeError(f"GraphQL returned errors for {endpoint_class}")
        return _mapping(root.get("data"), label="GraphQL data")

    def _record_transport(self, endpoint_class: str, response: requests.Response) -> None:
        content_hash = hashlib.sha256(response.content).hexdigest()
        observation = TransportObservation(
            endpoint_class=endpoint_class,
            response_sha256=content_hash,
            etag=response.headers.get("ETag"),
            rate_resource=response.headers.get("X-RateLimit-Resource"),
            rate_remaining=_optional_int(response.headers.get("X-RateLimit-Remaining")),
            rate_reset=_optional_int(response.headers.get("X-RateLimit-Reset")),
            http_code=response.status_code,
        )
        with self.transport_lock:
            self.transport.append(observation)
            self.transport_journal_path.parent.mkdir(parents=True, exist_ok=True)
            with self.transport_journal_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(asdict(observation), sort_keys=True) + "\n")

    def _guard_rate(self, response: requests.Response) -> None:
        resource = response.headers.get("X-RateLimit-Resource")
        remaining = _optional_int(response.headers.get("X-RateLimit-Remaining"))
        if resource in {"core", "graphql"} and remaining is not None and remaining < self.minimum_remaining:
            reset = response.headers.get("X-RateLimit-Reset", "unknown")
            raise RuntimeError(f"GitHub {resource} rate budget below frozen reserve; reset={reset}")


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


def _acquire_frame(
    client: GitHubApiClient,
    config: Mapping[str, Any],
    *,
    limit: int | None,
) -> tuple[RepositoryFrameEntry, ...]:
    frame = config["frame"]
    entries: list[RepositoryFrameEntry] = []
    identities: set[int] = set()
    for page in range(1, int(frame["pages"]) + 1):
        payload = client.request_json(
            "GET",
            "/search/repositories",
            endpoint_class="repository_frame",
            params={
                "q": str(frame["query"]),
                "sort": str(frame["sort"]),
                "order": str(frame["order"]),
                "per_page": int(frame["per_page"]),
                "page": page,
            },
        )
        root = _mapping(payload, label="repository search")
        if root.get("incomplete_results") is not False:
            raise RuntimeError("repository search is incomplete")
        items = _sequence(root.get("items"), label="repository search items")
        for raw in items:
            entry = sanitize_repository(_mapping(raw, label="repository"), frame_rank=len(entries) + 1)
            if entry.id in identities:
                raise RuntimeError("repository frame contains a duplicate ID")
            identities.add(entry.id)
            entries.append(entry)
            if limit is not None and len(entries) >= limit:
                return tuple(entries)
        if len(items) < int(frame["per_page"]):
            break
    return tuple(entries)


def _write_frame(path: Path, frame: Sequence[RepositoryFrameEntry]) -> None:
    payload = [repository.allowed_payload() for repository in frame]
    assert_outcome_blind_payload(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    if path.exists() or partial.exists():
        raise FileExistsError(f"refusing to overwrite frozen frame: {path}")
    partial.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(partial, path)


def _load_frame(path: Path) -> tuple[RepositoryFrameEntry, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = _sequence(payload, label="frozen repository frame")
    frame = tuple(
        RepositoryFrameEntry(**dict(_mapping(raw, label="frozen repository"))) for raw in rows
    )
    assert_outcome_blind_payload([repository.allowed_payload() for repository in frame])
    if len({repository.id for repository in frame}) != len(frame):
        raise RuntimeError("frozen repository frame contains duplicate IDs")
    return frame


def _historical_config(
    client: GitHubApiClient,
    repository: RepositoryFrameEntry,
    config: Mapping[str, Any],
) -> DependabotConfigSummary:
    github = config["github"]
    commits_payload = client.request_json(
        "GET",
        f"/repos/{repository.full_name}/commits",
        endpoint_class="historical_config_commit",
        params={
            "path": str(github["dependabot_config_path"]),
            "until": str(config["intervention"]["config_cutoff_utc"]),
            "per_page": 1,
        },
        allow_not_found=True,
    )
    if commits_payload is None:
        return summarize_dependabot_config(None, commit_sha=None, commit_timestamp=None)
    commits = _sequence(commits_payload, label="config commits")
    if not commits:
        return summarize_dependabot_config(None, commit_sha=None, commit_timestamp=None)
    latest = _mapping(commits[0], label="latest config commit")
    commit_sha = str(latest.get("sha", ""))
    commit = _mapping(latest.get("commit"), label="config commit detail")
    committer = _mapping(commit.get("committer"), label="config commit committer")
    commit_timestamp = str(committer.get("date", ""))
    content_payload = client.request_json(
        "GET",
        f"/repos/{repository.full_name}/contents/{github['dependabot_config_path']}",
        endpoint_class="historical_config_content",
        params={"ref": commit_sha},
        allow_not_found=True,
    )
    if content_payload is None:
        return summarize_dependabot_config(
            None,
            commit_sha=commit_sha,
            commit_timestamp=commit_timestamp,
            known_absent_at_cutoff=True,
        )
    content_root = _mapping(content_payload, label="config content")
    if str(content_root.get("encoding")) != "base64":
        raise RuntimeError("historical config content is not base64")
    encoded = str(content_root.get("content", "")).replace("\n", "")
    content = base64.b64decode(encoded, validate=True).decode("utf-8")
    return summarize_dependabot_config(
        content,
        commit_sha=commit_sha,
        commit_timestamp=commit_timestamp,
    )


def _workflow_paths(client: GitHubApiClient, repository: RepositoryFrameEntry) -> tuple[str, ...]:
    payload = client.request_json(
        "GET",
        f"/repos/{repository.full_name}/actions/workflows",
        endpoint_class="workflow_schema",
        params={"per_page": 100},
        allow_not_found=True,
    )
    if payload is None:
        return ()
    root = _mapping(payload, label="workflow response")
    workflows = _sequence(root.get("workflows", []), label="workflows")
    paths = {
        str(_mapping(raw, label="workflow").get("path", ""))
        for raw in workflows
        if str(_mapping(raw, label="workflow").get("path", ""))
    }
    return tuple(sorted(paths))


PR_SEARCH_QUERY = """
query($query: String!, $cursor: String, $first: Int!) {
  search(query: $query, type: ISSUE, first: $first, after: $cursor) {
    issueCount
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on PullRequest {
        id
        number
        createdAt
        author { __typename login }
      }
    }
  }
}
"""


def _search_pr_nodes(
    client: GitHubApiClient,
    *,
    search_query: str,
    endpoint_class: str,
    maximum_nodes: int,
) -> tuple[int, tuple[Mapping[str, Any], ...]]:
    nodes: list[Mapping[str, Any]] = []
    cursor: str | None = None
    issue_count: int | None = None
    while len(nodes) < maximum_nodes:
        first = min(100, maximum_nodes - len(nodes))
        data = client.graphql(
            PR_SEARCH_QUERY,
            {"query": search_query, "cursor": cursor, "first": first},
            endpoint_class=endpoint_class,
        )
        search = _mapping(data.get("search"), label="PR search")
        observed_count = search.get("issueCount")
        if isinstance(observed_count, bool) or not isinstance(observed_count, int):
            raise RuntimeError("PR search issueCount is invalid")
        issue_count = observed_count
        for raw in _sequence(search.get("nodes"), label="PR search nodes"):
            if isinstance(raw, Mapping):
                nodes.append(raw)
        page_info = _mapping(search.get("pageInfo"), label="PR search pageInfo")
        if page_info.get("hasNextPage") is not True or len(nodes) >= issue_count:
            break
        next_cursor = page_info.get("endCursor")
        if not isinstance(next_cursor, str) or not next_cursor or next_cursor == cursor:
            raise RuntimeError("PR search pagination cursor is invalid")
        cursor = next_cursor
    return issue_count or 0, tuple(nodes)


def _pr_support(
    client: GitHubApiClient,
    repository: RepositoryFrameEntry,
    config: Mapping[str, Any],
    runtime: Mapping[str, Any],
) -> tuple[tuple[PullRequestEvent, ...], int]:
    window = config["calibration_window"]
    from_date = str(window["from_utc"])[:10]
    to_date = str(window["to_utc"])[:10]
    login = str(config["github"]["dependabot_login"])
    maximum_bot = int(runtime["execution"]["maximum_bot_pr_events_per_repository"])
    _, bot_nodes = _search_pr_nodes(
        client,
        search_query=(
            f"repo:{repository.full_name} is:pr author:app/dependabot "
            f"created:{from_date}..{to_date} sort:created-asc"
        ),
        endpoint_class="dependabot_pr_search",
        maximum_nodes=maximum_bot,
    )
    bot_events = tuple(sanitize_pull_request_node(node, dependabot_login=login) for node in bot_nodes)
    maximum_human = int(runtime["execution"]["maximum_pr_nodes_for_human_support"])
    _, candidate_nodes = _search_pr_nodes(
        client,
        search_query=f"repo:{repository.full_name} is:pr created:{from_date}..{to_date} sort:created-asc",
        endpoint_class="human_pr_support_search",
        maximum_nodes=maximum_human,
    )
    human_lower_bound = 0
    for node in candidate_nodes:
        author = node.get("author")
        if not isinstance(author, Mapping):
            continue
        login_value = str(author.get("login", ""))
        if author.get("__typename") == "User" and login_value.lower() != login.lower():
            human_lower_bound += 1
    return bot_events, human_lower_bound


def _acquire_repository(
    client: GitHubApiClient,
    repository: RepositoryFrameEntry,
    config: Mapping[str, Any],
    runtime: Mapping[str, Any],
) -> RepositorySupport:
    config_summary = _historical_config(client, repository, config)
    workflow_paths = _workflow_paths(client, repository)
    bot_events, human_count = _pr_support(client, repository, config, runtime)
    return RepositorySupport(
        repository=repository,
        config=config_summary,
        workflow_paths=workflow_paths,
        bot_pull_requests=bot_events,
        human_pull_request_count=human_count,
        workflow_schema_access=None,
        job_schemas=(),
    )


def _record_from_payload(payload: Mapping[str, Any]) -> RepositorySupport:
    repository_raw = _mapping(payload.get("repository"), label="checkpoint repository")
    config_raw = _mapping(payload.get("configuration"), label="checkpoint config")
    events = tuple(
        PullRequestEvent(**dict(_mapping(raw, label="checkpoint PR")))
        for raw in _sequence(payload.get("bot_pull_requests"), label="checkpoint PRs")
    )
    jobs = tuple(
        WorkflowJobSchema(
            run_id=int(_mapping(raw, label="checkpoint job")["run_id"]),
            job_id=int(_mapping(raw, label="checkpoint job")["job_id"]),
            runner_labels=tuple(_mapping(raw, label="checkpoint job")["runner_labels"]),
            required_field_presence=dict(_mapping(raw, label="checkpoint job")["required_field_presence"]),
        )
        for raw in _sequence(payload.get("job_schemas"), label="checkpoint jobs")
    )
    return RepositorySupport(
        repository=RepositoryFrameEntry(**dict(repository_raw)),
        config=DependabotConfigSummary(
            commit_sha=config_raw.get("commit_sha"),
            commit_timestamp=config_raw.get("commit_timestamp"),
            content_sha256=config_raw.get("content_sha256"),
            parse_status=str(config_raw["parse_status"]),
            treatment_class=str(config_raw["treatment_class"]),
            schedule_schema=tuple(config_raw["schedule_schema"]),
            grouping_present=config_raw.get("grouping_present"),
        ),
        workflow_paths=tuple(str(value) for value in _sequence(payload.get("workflow_paths"), label="paths")),
        bot_pull_requests=events,
        human_pull_request_count=(
            int(payload["human_pull_request_count"])
            if payload.get("human_pull_request_count") is not None
            else None
        ),
        workflow_schema_access=(
            bool(payload["workflow_schema_access"])
            if payload.get("workflow_schema_access") is not None
            else None
        ),
        job_schemas=jobs,
    )


def _write_checkpoint(path: Path, record: RepositorySupport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    payload = record.allowed_payload()
    assert_outcome_blind_payload(payload)
    partial.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(partial, path)


def _load_checkpoint(path: Path) -> RepositorySupport:
    payload = json.loads(path.read_text(encoding="utf-8"))
    root = _mapping(payload, label="checkpoint")
    assert_outcome_blind_payload(root)
    return _record_from_payload(root)


def _probe_key(repository: RepositoryFrameEntry) -> str:
    return hashlib.sha256(str(repository.id).encode()).hexdigest()


def _probe_schema(
    client: GitHubApiClient,
    record: RepositorySupport,
    config: Mapping[str, Any],
    runtime: Mapping[str, Any],
) -> RepositorySupport:
    execution = runtime["execution"]
    payload = client.request_json(
        "GET",
        f"/repos/{record.repository.full_name}/actions/runs",
        endpoint_class="workflow_run_schema_probe",
        params={
            "created": f"{execution['schema_probe_from_utc']}..{execution['schema_probe_to_utc']}",
            "per_page": int(execution["schema_probe_runs_per_page"]),
        },
        allow_not_found=True,
    )
    if payload is None:
        return replace(record, workflow_schema_access=False)
    root = _mapping(payload, label="workflow run probe")
    raw_runs = _sequence(root.get("workflow_runs", []), label="workflow runs")
    selected_raw: Mapping[str, Any] | None = None
    for raw in raw_runs:
        run = _mapping(raw, label="workflow run")
        actor = run.get("actor")
        if isinstance(actor, Mapping) and actor.get("type") == "User":
            selected_raw = run
            break
    if selected_raw is None:
        return replace(record, workflow_schema_access=True)
    run = sanitize_workflow_run(
        selected_raw,
        dependabot_login=str(config["github"]["dependabot_login"]),
    )
    jobs_payload = client.request_json(
        "GET",
        f"/repos/{record.repository.full_name}/actions/runs/{run.id}/jobs",
        endpoint_class="workflow_job_schema_probe",
        params={"per_page": 100},
        allow_not_found=True,
    )
    if jobs_payload is None:
        return replace(record, workflow_schema_access=False)
    jobs_root = _mapping(jobs_payload, label="workflow jobs response")
    job_schemas = tuple(
        sanitize_workflow_job(_mapping(raw, label="workflow job"), run_id=run.id)
        for raw in _sequence(jobs_root.get("jobs", []), label="workflow jobs")
    )
    return replace(record, workflow_schema_access=True, job_schemas=job_schemas)


def _schema_probe_selection(
    records: Sequence[RepositorySupport],
    *,
    per_arm: int,
) -> tuple[RepositorySupport, ...]:
    treated = sorted(
        (
            record
            for record in records
            if record.config.treatment_class == "default_treated" and record.workflow_paths
        ),
        key=lambda record: _probe_key(record.repository),
    )[:per_arm]
    controls = sorted(
        (
            record
            for record in records
            if record.config.treatment_class == "no_dependabot_control"
            and record.workflow_paths
            and not record.bot_pull_requests
            and bool(record.human_pull_request_count)
        ),
        key=lambda record: _probe_key(record.repository),
    )[:per_arm]
    return tuple(treated + controls)


def _write_gzip_jsonl(path: Path, records: Sequence[RepositorySupport]) -> tuple[str, str]:
    if path.exists() or path.with_name(path.name + ".partial").exists():
        raise FileExistsError(f"refusing to overwrite final allowed-record artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    payloads = [record.allowed_payload() for record in records]
    assert_outcome_blind_payload(payloads)
    canonical_hash = canonical_json_sha256(payloads)
    lines = [json.dumps(payload, sort_keys=True, separators=(",", ":")) for payload in payloads]
    raw = ("\n".join(lines) + "\n").encode()
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
        raise FileExistsError(f"refusing to overwrite immutable artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload["canonical_payload_sha256"] = canonical_json_sha256(payload)
    partial = path.with_name(path.name + ".partial")
    partial.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(partial, path)


def _transport_summary(observations: Sequence[TransportObservation]) -> dict[str, Any]:
    hashes = sorted(observation.response_sha256 for observation in observations)
    return {
        "request_count": len(observations),
        "endpoint_class_counts": dict(sorted(Counter(obs.endpoint_class for obs in observations).items())),
        "http_code_counts": dict(sorted(Counter(str(obs.http_code) for obs in observations).items())),
        "response_hashes_sha256": canonical_json_sha256(hashes),
        "last_rate_metadata": {
            resource: {
                "remaining": next(
                    obs.rate_remaining for obs in reversed(observations) if obs.rate_resource == resource
                ),
                "reset": next(obs.rate_reset for obs in reversed(observations) if obs.rate_resource == resource),
            }
            for resource in sorted({obs.rate_resource for obs in observations if obs.rate_resource is not None})
        },
    }


def _run(
    config_path: Path,
    runtime_path: Path,
    *,
    smoke: bool,
    max_repositories: int | None,
) -> dict[str, Any]:
    config, runtime = _verify_contract(config_path, runtime_path, formal=not smoke)
    if not smoke and max_repositories is not None:
        raise RuntimeError("formal D-1 forbids a repository limit")
    if smoke:
        smoke_config = runtime["smoke"]
        limit = int(smoke_config["repository_limit"]) if max_repositories is None else max_repositories
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        raw_directory = Path(str(smoke_config["output_directory"])) / stamp
        result_path = raw_directory / "smoke_result.json"
        manifest_path = raw_directory / "smoke_manifest.json"
        probe_per_arm = int(smoke_config["schema_probe_repositories_per_arm"])
    else:
        execution = runtime["execution"]
        limit = None
        raw_directory = _resolve_repo_path(execution["raw_directory"])
        result_path = _resolve_repo_path(execution["result_path"])
        manifest_path = _resolve_repo_path(execution["manifest_path"])
        probe_per_arm = int(execution["schema_probe_repositories_per_arm"])
        if result_path.exists() or manifest_path.exists():
            raise FileExistsError("formal D-1 result or manifest already exists")
    client = GitHubApiClient(
        config,
        runtime,
        transport_journal_path=raw_directory / "transport_observations.jsonl",
    )
    checkpoint_directory = raw_directory / "repository_checkpoints"
    raw_directory.mkdir(parents=True, exist_ok=True)
    frame_path = raw_directory / "frozen_frame.json"
    if frame_path.exists():
        frame = _load_frame(frame_path)
    else:
        frame = _acquire_frame(client, config, limit=limit)
        _write_frame(frame_path, frame)
    records_by_id: dict[int, RepositorySupport] = {}
    missing: list[RepositoryFrameEntry] = []
    for repository in frame:
        checkpoint = checkpoint_directory / f"{repository.id}.json"
        if checkpoint.exists():
            record = _load_checkpoint(checkpoint)
            if record.repository != repository:
                raise RuntimeError("checkpoint repository does not match the current frozen frame")
            records_by_id[repository.id] = record
        else:
            missing.append(repository)

    max_workers = int(config["github"]["maximum_parallel_requests"])
    started = time.monotonic()
    last_progress = started
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures: dict[Future[RepositorySupport], RepositoryFrameEntry] = {
            executor.submit(_acquire_repository, client, repository, config, runtime): repository
            for repository in missing
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            repository = futures[future]
            record = future.result()
            _write_checkpoint(checkpoint_directory / f"{repository.id}.json", record)
            records_by_id[repository.id] = record
            now = time.monotonic()
            if now - last_progress >= float(runtime["execution"]["progress_interval_seconds"]):
                print(
                    json.dumps(
                        {
                            "stage": "repository_support",
                            "completed_this_run": completed,
                            "total_missing": len(missing),
                            "total_frame": len(frame),
                            "elapsed_seconds": round(now - started, 1),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
                last_progress = now
    ordered = [records_by_id[repository.id] for repository in frame]
    selected = _schema_probe_selection(ordered, per_arm=probe_per_arm)
    selected_ids = {record.repository.id for record in selected}
    for index, record in enumerate(ordered):
        if record.repository.id not in selected_ids or record.workflow_schema_access is not None:
            continue
        probed = _probe_schema(client, record, config, runtime)
        ordered[index] = probed
        records_by_id[record.repository.id] = probed
        _write_checkpoint(checkpoint_directory / f"{record.repository.id}.json", probed)

    allowed_filename = str(runtime["execution"]["allowed_records_filename"])
    allowed_path = raw_directory / allowed_filename
    records_canonical_hash, records_file_hash = _write_gzip_jsonl(allowed_path, ordered)
    roundtrip_payloads: list[Any] = []
    with gzip.open(allowed_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            roundtrip_payloads.append(json.loads(line))
    deterministic = canonical_json_sha256(roundtrip_payloads) == records_canonical_hash
    support = evaluate_dminus1_support(
        ordered,
        gates=config["gates"],
        minimum_bot_prs_for_high_support_repository=int(
            config["calibration_window"]["minimum_bot_prs_for_high_support_repository"]
        ),
        cluster_gap_hours=float(config["calibration_window"]["cluster_gap_hours"]),
        deterministic_summary_hash_matches=deterministic,
    )
    result = {
        "schema_version": 1,
        "audit": "github_dependabot_cooldown_dminus1",
        "mode": "smoke" if smoke else "formal",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "git_sha": _git("rev-parse", "HEAD"),
        "config_sha256": _sha256_file(config_path),
        "runtime_sha256": _sha256_file(runtime_path),
        "frame": {
            "query": config["frame"]["query"],
            "repository_count": len(frame),
            "first_repository": frame[0].full_name if frame else None,
            "last_repository": frame[-1].full_name if frame else None,
        },
        "outcome_seal": {
            "queue_review_merge_security_values_opened": False,
            "allowed_records_canonical_sha256": records_canonical_hash,
            "allowed_records_file_sha256": records_file_hash,
        },
        "support": support,
        "treatment_class_counts": dict(sorted(Counter(record.config.treatment_class for record in ordered).items())),
        "transport": _transport_summary(client.transport),
        "elapsed_seconds": time.monotonic() - started,
    }
    manifest = {
        "schema_version": 1,
        "audit": "github_dependabot_cooldown_dminus1",
        "mode": "smoke" if smoke else "formal",
        "git_sha": result["git_sha"],
        "config_path": str(config_path),
        "config_sha256": result["config_sha256"],
        "runtime_path": str(runtime_path),
        "runtime_sha256": result["runtime_sha256"],
        "allowed_records_path": str(allowed_path),
        "allowed_records_file_sha256": records_file_hash,
        "allowed_records_canonical_sha256": records_canonical_hash,
        "forbidden_raw_outcome_payload_persisted": False,
        "transport": result["transport"],
    }
    _write_json(result_path, result)
    _write_json(manifest_path, manifest)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--runtime", type=Path, default=RUNTIME_PATH)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--max-repositories", type=int)
    args = parser.parse_args()
    if args.max_repositories is not None and args.max_repositories <= 0:
        raise ValueError("repository limit must be positive")
    result = _run(
        args.config.resolve(),
        args.runtime.resolve(),
        smoke=bool(args.smoke),
        max_repositories=args.max_repositories,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
