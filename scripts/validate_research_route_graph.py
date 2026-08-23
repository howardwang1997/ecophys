#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import cast

import yaml

EXPECTED_SCHEMA_VERSION = 2
EXPECTED_NODE_TYPES = {"research_route", "research_subroute"}
EXPECTED_STATUSES = {
    "candidate",
    "active",
    "parked",
    "passed_closed",
    "failed_closed",
    "superseded",
}
EXPECTED_EDGE_TYPES = {
    "next_selected_route",
    "derived_from",
    "supersedes",
    "aggregates",
    "blocks",
}
EXPECTED_AVAILABILITY = {"present", "missing_legacy", "external", "git_ref"}
EXPECTED_NODE_FIELDS = {
    "id",
    "node_type",
    "title",
    "status",
    "opened_at",
    "closed_at",
    "phase",
    "terminal_gate",
    "failure_codes",
    "summary",
    "evidence",
    "artifacts",
    "reusable_assets",
    "reopen_conditions",
    "forbidden_actions",
}
EXPECTED_EDGE_FIELDS = {
    "id",
    "source",
    "type",
    "target",
    "rationale",
    "evidence_refs",
}
EXPECTED_LOCATOR_FIELDS = {"id", "kind", "availability"}
TERMINAL_STATUSES = {"failed_closed", "passed_closed", "superseded"}
OPEN_STATUSES = {"candidate", "active", "parked"}
TERMINAL_EVIDENCE_KINDS = {"formal_result", "closure_decision", "formal_audit"}
ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
REF_PATTERN = re.compile(r"^refs/(?:heads|remotes|tags)/[A-Za-z0-9._/-]+$")
EXPECTED_LOCATOR_AVAILABILITY_FIELDS = {
    "present": {"path"},
    "missing_legacy": {"path", "note"},
    "external": {"uri"},
    "git_ref": {"ref", "commit", "path"},
}


class GraphValidationError(ValueError):
    """Raised when the route graph violates its declared contract."""


def require_mapping(value: object, context: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise GraphValidationError(f"{context} must be a mapping")
    if not all(isinstance(key, str) for key in value):
        raise GraphValidationError(f"{context} must use string keys")
    return cast(Mapping[str, object], value)


def require_list(value: object, context: str) -> list[object]:
    if not isinstance(value, list):
        raise GraphValidationError(f"{context} must be a list")
    return cast(list[object], value)


def require_string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GraphValidationError(f"{context} must be a non-empty string")
    return value


def require_string_list(
    value: object,
    context: str,
    *,
    allow_empty: bool = True,
) -> list[str]:
    raw_items = require_list(value, context)
    if not allow_empty and not raw_items:
        raise GraphValidationError(f"{context} must not be empty")
    items: list[str] = []
    for index, item in enumerate(raw_items):
        items.append(require_string(item, f"{context}[{index}]"))
    if len(items) != len(set(items)):
        raise GraphValidationError(f"{context} contains duplicate values")
    return items


def require_id(value: object, context: str) -> str:
    identifier = require_string(value, context)
    if ID_PATTERN.fullmatch(identifier) is None:
        raise GraphValidationError(
            f"{context} must match {ID_PATTERN.pattern!r}: {identifier!r}"
        )
    return identifier


def require_iso_date(value: object, context: str) -> date:
    raw = require_string(value, context)
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise GraphValidationError(f"{context} is not an ISO date: {raw!r}") from exc


def load_graph(path: Path) -> Mapping[str, object]:
    try:
        loaded = cast(object, yaml.safe_load(path.read_text(encoding="utf-8")))
    except (OSError, yaml.YAMLError) as exc:
        raise GraphValidationError(f"cannot load {path}: {exc}") from exc
    return require_mapping(loaded, "root")


def validate_declared_schema(root: Mapping[str, object]) -> tuple[date, date]:
    version = root.get("schema_version")
    if type(version) is not int or version != EXPECTED_SCHEMA_VERSION:
        raise GraphValidationError(
            f"schema_version must be integer {EXPECTED_SCHEMA_VERSION}"
        )

    graph = require_mapping(root.get("graph"), "graph")
    require_id(graph.get("id"), "graph.id")
    updated_at = require_iso_date(graph.get("updated_at"), "graph.updated_at")
    scope = require_mapping(graph.get("scope"), "graph.scope")
    scope_start = require_iso_date(scope.get("start_date"), "graph.scope.start_date")
    if scope.get("end_date") is not None:
        scope_end = require_iso_date(scope.get("end_date"), "graph.scope.end_date")
        if scope_end < scope_start:
            raise GraphValidationError("graph.scope.end_date precedes start_date")
    require_string(scope.get("granularity"), "graph.scope.granularity")
    completeness = require_string(scope.get("completeness"), "graph.scope.completeness")
    if completeness == "complete" and scope.get("historical_backfill_complete") is not True:
        raise GraphValidationError(
            "scope cannot claim complete coverage while historical_backfill_complete is false"
        )
    if type(scope.get("historical_backfill_complete")) is not bool:
        raise GraphValidationError(
            "graph.scope.historical_backfill_complete must be boolean"
        )
    require_string_list(scope.get("notes"), "graph.scope.notes", allow_empty=False)

    schema = require_mapping(root.get("schema"), "schema")
    node_types = set(
        require_string_list(
            schema.get("allowed_node_types"),
            "schema.allowed_node_types",
            allow_empty=False,
        )
    )
    if node_types != EXPECTED_NODE_TYPES:
        raise GraphValidationError(
            f"schema.allowed_node_types must equal {sorted(EXPECTED_NODE_TYPES)}"
        )
    statuses = set(
        require_string_list(
            schema.get("allowed_statuses"),
            "schema.allowed_statuses",
            allow_empty=False,
        )
    )
    if statuses != EXPECTED_STATUSES:
        raise GraphValidationError(
            f"schema.allowed_statuses must equal {sorted(EXPECTED_STATUSES)}"
        )
    edge_types = set(
        require_string_list(
            schema.get("allowed_edge_types"),
            "schema.allowed_edge_types",
            allow_empty=False,
        )
    )
    if edge_types != EXPECTED_EDGE_TYPES:
        raise GraphValidationError(
            f"schema.allowed_edge_types must equal {sorted(EXPECTED_EDGE_TYPES)}"
        )
    availability = set(
        require_string_list(
            schema.get("allowed_locator_availability"),
            "schema.allowed_locator_availability",
            allow_empty=False,
        )
    )
    if availability != EXPECTED_AVAILABILITY:
        raise GraphValidationError(
            "schema.allowed_locator_availability must equal "
            f"{sorted(EXPECTED_AVAILABILITY)}"
        )

    node_schema = require_mapping(schema.get("node"), "schema.node")
    declared_node_fields = set(
        require_string_list(
            node_schema.get("required_fields"),
            "schema.node.required_fields",
            allow_empty=False,
        )
    )
    if declared_node_fields != EXPECTED_NODE_FIELDS:
        raise GraphValidationError(
            f"schema.node.required_fields must equal {sorted(EXPECTED_NODE_FIELDS)}"
        )

    edge_schema = require_mapping(schema.get("edge"), "schema.edge")
    declared_edge_fields = set(
        require_string_list(
            edge_schema.get("required_fields"),
            "schema.edge.required_fields",
            allow_empty=False,
        )
    )
    if declared_edge_fields != EXPECTED_EDGE_FIELDS:
        raise GraphValidationError(
            f"schema.edge.required_fields must equal {sorted(EXPECTED_EDGE_FIELDS)}"
        )

    locator_schema = require_mapping(schema.get("locator"), "schema.locator")
    declared_locator_fields = set(
        require_string_list(
            locator_schema.get("required_fields"),
            "schema.locator.required_fields",
            allow_empty=False,
        )
    )
    if declared_locator_fields != EXPECTED_LOCATOR_FIELDS:
        raise GraphValidationError(
            "schema.locator.required_fields must equal "
            f"{sorted(EXPECTED_LOCATOR_FIELDS)}"
        )
    availability_fields = require_mapping(
        locator_schema.get("availability_fields"),
        "schema.locator.availability_fields",
    )
    if set(availability_fields) != set(EXPECTED_LOCATOR_AVAILABILITY_FIELDS):
        raise GraphValidationError(
            "schema.locator.availability_fields must declare every availability"
        )
    for availability_name, expected_fields in EXPECTED_LOCATOR_AVAILABILITY_FIELDS.items():
        declared_fields = set(
            require_string_list(
                availability_fields.get(availability_name),
                f"schema.locator.availability_fields.{availability_name}",
                allow_empty=False,
            )
        )
        if declared_fields != expected_fields:
            raise GraphValidationError(
                "schema.locator.availability_fields."
                f"{availability_name} must equal {sorted(expected_fields)}"
            )
    return scope_start, updated_at


def validate_local_path(repo_root: Path, raw_path: str, context: str) -> Path:
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise GraphValidationError(f"{context} must be a safe repository-relative path")
    resolved_root = repo_root.resolve()
    resolved = (resolved_root / relative).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise GraphValidationError(f"{context} resolves outside the repository") from exc
    return resolved


def run_offline_git(repo_root: Path, args: list[str], context: str) -> str:
    environment = os.environ.copy()
    environment.update(
        {
            "GIT_NO_LAZY_FETCH": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise GraphValidationError(f"{context}: cannot execute git: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "git failed"
        raise GraphValidationError(f"{context}: {detail}")
    return completed.stdout.strip()


def validate_git_ref_locator(
    locator: Mapping[str, object],
    context: str,
    repo_root: Path,
) -> None:
    ref = require_string(locator.get("ref"), f"{context}.ref")
    if REF_PATTERN.fullmatch(ref) is None:
        raise GraphValidationError(
            f"{context}.ref must be a full local heads/remotes/tags ref"
        )
    commit = require_string(locator.get("commit"), f"{context}.commit")
    if COMMIT_PATTERN.fullmatch(commit) is None:
        raise GraphValidationError(
            f"{context}.commit must be a full lowercase 40-hex object id"
        )
    raw_path = require_string(locator.get("path"), f"{context}.path")
    validate_local_path(repo_root, raw_path, f"{context}.path")

    resolved_ref = run_offline_git(
        repo_root,
        ["rev-parse", "--verify", f"{ref}^{{commit}}"],
        f"{context}.ref is not an available commit",
    )
    run_offline_git(
        repo_root,
        ["rev-parse", "--verify", f"{commit}^{{commit}}"],
        f"{context}.commit is not locally available",
    )
    run_offline_git(
        repo_root,
        ["merge-base", "--is-ancestor", commit, resolved_ref],
        f"{context}.commit is not reachable from ref {ref!r}",
    )
    object_type = run_offline_git(
        repo_root,
        ["cat-file", "-t", f"{commit}:{raw_path}"],
        f"{context}.path is not available at pinned commit",
    )
    if object_type != "blob":
        raise GraphValidationError(
            f"{context}.path at pinned commit must resolve to a blob"
        )


def validate_locator(
    raw_locator: object,
    context: str,
    repo_root: Path,
    global_locator_ids: set[str],
) -> tuple[str, str, str]:
    locator = require_mapping(raw_locator, context)
    missing = EXPECTED_LOCATOR_FIELDS - set(locator)
    if missing:
        raise GraphValidationError(f"{context} lacks fields: {sorted(missing)}")

    locator_id = require_id(locator.get("id"), f"{context}.id")
    if locator_id in global_locator_ids:
        raise GraphValidationError(f"duplicate locator id: {locator_id}")
    global_locator_ids.add(locator_id)
    kind = require_string(locator.get("kind"), f"{context}.kind")
    availability = require_string(
        locator.get("availability"), f"{context}.availability"
    )
    if availability not in EXPECTED_AVAILABILITY:
        raise GraphValidationError(
            f"{context}.availability has unknown value {availability!r}"
        )

    if availability in {"present", "missing_legacy"}:
        raw_path = require_string(locator.get("path"), f"{context}.path")
        resolved = validate_local_path(repo_root, raw_path, f"{context}.path")
        if availability == "present" and not resolved.is_file():
            raise GraphValidationError(
                f"{context}.path is not a reachable local file: {raw_path}"
            )
        if availability == "missing_legacy":
            require_string(locator.get("note"), f"{context}.note")
            if resolved.exists():
                raise GraphValidationError(
                    f"{context} is marked missing_legacy but exists: {raw_path}"
                )
    elif availability == "external":
        uri = require_string(locator.get("uri"), f"{context}.uri")
        if not uri.startswith(("https://", "http://")):
            raise GraphValidationError(
                f"{context}.uri must be an HTTP(S) URI for external evidence"
            )
    else:
        validate_git_ref_locator(locator, context, repo_root)
    return locator_id, kind, availability


def validate_nodes(
    root: Mapping[str, object],
    repo_root: Path,
    scope_start: date,
    graph_updated_at: date,
) -> tuple[
    dict[str, Mapping[str, object]],
    dict[str, date],
    dict[str, date | None],
    set[str],
    Counter[str],
    int,
    int,
]:
    raw_nodes = require_list(root.get("nodes"), "nodes")
    if not raw_nodes:
        raise GraphValidationError("nodes must not be empty")

    nodes: dict[str, Mapping[str, object]] = {}
    opened_dates: dict[str, date] = {}
    closed_dates: dict[str, date | None] = {}
    locator_ids: set[str] = set()
    status_counts: Counter[str] = Counter()
    missing_legacy_count = 0
    git_ref_count = 0

    for index, raw_node in enumerate(raw_nodes):
        context = f"nodes[{index}]"
        node = require_mapping(raw_node, context)
        missing = EXPECTED_NODE_FIELDS - set(node)
        if missing:
            raise GraphValidationError(f"{context} lacks fields: {sorted(missing)}")

        node_id = require_id(node.get("id"), f"{context}.id")
        if node_id in nodes:
            raise GraphValidationError(f"duplicate node id: {node_id}")
        node_type = require_string(node.get("node_type"), f"{context}.node_type")
        if node_type not in EXPECTED_NODE_TYPES:
            raise GraphValidationError(
                f"{context}.node_type is unknown: {node_type!r}"
            )
        require_string(node.get("title"), f"{context}.title")
        status = require_string(node.get("status"), f"{context}.status")
        if status not in EXPECTED_STATUSES:
            raise GraphValidationError(f"{context}.status is unknown: {status!r}")
        opened_at = require_iso_date(node.get("opened_at"), f"{context}.opened_at")
        if opened_at < scope_start:
            raise GraphValidationError(
                f"{context}.opened_at predates declared graph scope: {opened_at}"
            )
        if opened_at > graph_updated_at:
            raise GraphValidationError(
                f"{context}.opened_at is after graph.updated_at: {opened_at}"
            )

        raw_closed_at = node.get("closed_at")
        closed_at: date | None
        if status in TERMINAL_STATUSES:
            closed_at = require_iso_date(raw_closed_at, f"{context}.closed_at")
            if closed_at < opened_at:
                raise GraphValidationError(f"{context}.closed_at precedes opened_at")
            if closed_at > graph_updated_at:
                raise GraphValidationError(
                    f"{context}.closed_at is after graph.updated_at"
                )
        else:
            if raw_closed_at is not None:
                raise GraphValidationError(
                    f"{context}.closed_at must be null for open status {status!r}"
                )
            closed_at = None

        require_string(node.get("phase"), f"{context}.phase")
        if status in TERMINAL_STATUSES:
            require_string(node.get("terminal_gate"), f"{context}.terminal_gate")
        elif node.get("terminal_gate") is not None:
            raise GraphValidationError(
                f"{context}.terminal_gate must be null for open status {status!r}"
            )

        failure_codes = require_string_list(
            node.get("failure_codes"), f"{context}.failure_codes"
        )
        if status == "failed_closed" and not failure_codes:
            raise GraphValidationError(
                f"{context}.failure_codes must not be empty for failed_closed"
            )
        if status in OPEN_STATUSES and failure_codes:
            raise GraphValidationError(
                f"{context}.failure_codes must be empty for open status {status!r}"
            )
        require_string(node.get("summary"), f"{context}.summary")
        require_string_list(
            node.get("reusable_assets"), f"{context}.reusable_assets"
        )
        reopen_conditions = require_string_list(
            node.get("reopen_conditions"), f"{context}.reopen_conditions"
        )
        if status == "failed_closed" and not reopen_conditions:
            raise GraphValidationError(
                f"{context}.reopen_conditions must not be empty for failed_closed"
            )
        require_string_list(
            node.get("forbidden_actions"),
            f"{context}.forbidden_actions",
            allow_empty=False,
        )

        terminal_evidence = False
        for field in ("evidence", "artifacts"):
            raw_locators = require_list(node.get(field), f"{context}.{field}")
            if not raw_locators:
                raise GraphValidationError(f"{context}.{field} must not be empty")
            for locator_index, raw_locator in enumerate(raw_locators):
                locator_id, kind, availability = validate_locator(
                    raw_locator,
                    f"{context}.{field}[{locator_index}]",
                    repo_root,
                    locator_ids,
                )
                del locator_id
                if availability == "missing_legacy":
                    missing_legacy_count += 1
                if availability == "git_ref":
                    git_ref_count += 1
                if kind in TERMINAL_EVIDENCE_KINDS:
                    terminal_evidence = True
        if status in TERMINAL_STATUSES and not terminal_evidence:
            raise GraphValidationError(
                f"{context} lacks formal terminal evidence of kind "
                f"{sorted(TERMINAL_EVIDENCE_KINDS)}"
            )

        nodes[node_id] = node
        opened_dates[node_id] = opened_at
        closed_dates[node_id] = closed_at
        status_counts[status] += 1

    return (
        nodes,
        opened_dates,
        closed_dates,
        locator_ids,
        status_counts,
        missing_legacy_count,
        git_ref_count,
    )


def validate_next_route_acyclic(adjacency: Mapping[str, set[str]]) -> None:
    state: dict[str, int] = {}

    def visit(node_id: str) -> None:
        marker = state.get(node_id, 0)
        if marker == 1:
            raise GraphValidationError(
                f"next_selected_route contains a cycle through {node_id}"
            )
        if marker == 2:
            return
        state[node_id] = 1
        for target in adjacency.get(node_id, set()):
            visit(target)
        state[node_id] = 2

    for node_id in adjacency:
        visit(node_id)


def validate_edges(
    root: Mapping[str, object],
    nodes: Mapping[str, Mapping[str, object]],
    opened_dates: Mapping[str, date],
    closed_dates: Mapping[str, date | None],
    locator_ids: set[str],
) -> int:
    raw_edges = require_list(root.get("edges"), "edges")
    edge_ids: set[str] = set()
    triples: set[tuple[str, str, str]] = set()
    next_route_adjacency: dict[str, set[str]] = {}

    for index, raw_edge in enumerate(raw_edges):
        context = f"edges[{index}]"
        edge = require_mapping(raw_edge, context)
        missing = EXPECTED_EDGE_FIELDS - set(edge)
        if missing:
            raise GraphValidationError(f"{context} lacks fields: {sorted(missing)}")
        edge_id = require_id(edge.get("id"), f"{context}.id")
        if edge_id in edge_ids:
            raise GraphValidationError(f"duplicate edge id: {edge_id}")
        edge_ids.add(edge_id)

        source = require_id(edge.get("source"), f"{context}.source")
        target = require_id(edge.get("target"), f"{context}.target")
        if source not in nodes:
            raise GraphValidationError(f"{context}.source has no node: {source}")
        if target not in nodes:
            raise GraphValidationError(f"{context}.target has no node: {target}")
        if source == target:
            raise GraphValidationError(f"{context} cannot be a self-edge")
        edge_type = require_string(edge.get("type"), f"{context}.type")
        if edge_type not in EXPECTED_EDGE_TYPES:
            raise GraphValidationError(
                f"{context}.type is unknown: {edge_type!r}"
            )
        triple = (source, edge_type, target)
        if triple in triples:
            raise GraphValidationError(f"duplicate semantic edge: {triple}")
        triples.add(triple)
        require_string(edge.get("rationale"), f"{context}.rationale")
        refs = require_string_list(
            edge.get("evidence_refs"),
            f"{context}.evidence_refs",
            allow_empty=False,
        )
        unknown_refs = set(refs) - locator_ids
        if unknown_refs:
            raise GraphValidationError(
                f"{context}.evidence_refs has unknown locators: {sorted(unknown_refs)}"
            )

        if edge_type == "next_selected_route":
            source_status = require_string(
                nodes[source].get("status"), f"node {source}.status"
            )
            if source_status not in TERMINAL_STATUSES:
                raise GraphValidationError(
                    f"{context}: next_selected_route source must be terminal"
                )
            source_closed = closed_dates[source]
            if source_closed is None or source_closed > opened_dates[target]:
                raise GraphValidationError(
                    f"{context}: target opened before source route closed"
                )
            next_route_adjacency.setdefault(source, set()).add(target)

    validate_next_route_acyclic(next_route_adjacency)
    return len(raw_edges)


def validate_graph(path: Path, repo_root: Path | None = None) -> str:
    resolved_repo_root = (
        path.resolve().parents[2] if repo_root is None else repo_root.resolve()
    )
    root = load_graph(path)
    required_top_level = {"schema_version", "graph", "schema", "nodes", "edges"}
    missing_top_level = required_top_level - set(root)
    if missing_top_level:
        raise GraphValidationError(
            f"root lacks fields: {sorted(missing_top_level)}"
        )
    scope_start, graph_updated_at = validate_declared_schema(root)
    (
        nodes,
        opened_dates,
        closed_dates,
        locator_ids,
        status_counts,
        missing_legacy_count,
        git_ref_count,
    ) = validate_nodes(
        root,
        resolved_repo_root,
        scope_start,
        graph_updated_at,
    )
    edge_count = validate_edges(
        root,
        nodes,
        opened_dates,
        closed_dates,
        locator_ids,
    )
    counts = ", ".join(
        f"{status}={count}" for status, count in sorted(status_counts.items())
    )
    return (
        f"OK: {len(nodes)} route nodes ({counts}), {edge_count} typed edges, "
        f"{len(locator_ids)} evidence/artifact locators verified, "
        f"git_ref={git_ref_count}, missing_legacy={missing_legacy_count}"
    )


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) > 1:
        print(
            "usage: validate_research_route_graph.py [GRAPH_PATH]",
            file=sys.stderr,
        )
        return 2
    default_path = (
        Path(__file__).resolve().parents[1]
        / ".claude"
        / "memory"
        / "research_route_knowledge_graph.yaml"
    )
    graph_path = Path(args[0]).resolve() if args else default_path
    try:
        result = validate_graph(graph_path)
    except GraphValidationError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
