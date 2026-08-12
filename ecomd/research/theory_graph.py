"""Validation for the persistent theory-exploration knowledge graph."""

from __future__ import annotations

import argparse
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

import yaml

SCHEMA_VERSION = "ecophys-theory-graph/v1"
NODE_TYPES = frozenset(
    {
        "source",
        "known_result",
        "concept",
        "candidate",
        "proof_obligation",
        "counterexample",
        "benchmark",
        "dataset",
        "compute_gate",
        "venue_claim",
        "decision",
    }
)
EDGE_TYPES = frozenset(
    {
        "proves",
        "covers",
        "reduces_to",
        "requires",
        "falsified_by",
        "distinguished_by",
        "supports",
        "forbids",
        "branches_to",
        "retired_by",
    }
)
CANDIDATE_STATES = frozenset(
    {
        "SCOUT",
        "FORMALIZING",
        "ATTACKING",
        "RETIRED_PRIOR_ART",
        "RETIRED_IDENTIFIABILITY",
        "RETIRED_NO_WITNESS",
        "CONJECTURE",
        "READY_FOR_HUMAN_AUDIT",
    }
)
RETIRED_STATES = frozenset(
    {"RETIRED_PRIOR_ART", "RETIRED_IDENTIFIABILITY", "RETIRED_NO_WITNESS"}
)
TRACKS = frozenset({"shared", "nmi", "ncs", "both"})
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def load_graph(path: str | Path) -> dict[str, object]:
    """Load a YAML graph and retain an object-typed boundary for strict validation."""

    raw: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("theory graph root must be a mapping")
    return cast(dict[str, object], raw)


def _as_mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _as_mapping_list(value: object) -> list[Mapping[str, object]] | None:
    if not isinstance(value, list):
        return None
    result: list[Mapping[str, object]] = []
    for item in value:
        mapped = _as_mapping(item)
        if mapped is None:
            return None
        result.append(mapped)
    return result


def _nonempty_string(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def validate_graph(graph: Mapping[str, object]) -> list[str]:
    """Return all structural and process-contract violations in deterministic order."""

    errors: list[str] = []
    if graph.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION}")

    nodes = _as_mapping_list(graph.get("nodes"))
    edges = _as_mapping_list(graph.get("edges"))
    if nodes is None:
        errors.append("nodes must be a list of mappings")
        nodes = []
    if edges is None:
        errors.append("edges must be a list of mappings")
        edges = []

    node_by_id: dict[str, Mapping[str, object]] = {}
    candidate_ids: set[str] = set()
    for index, node in enumerate(nodes):
        prefix = f"nodes[{index}]"
        node_id = _nonempty_string(node.get("id"))
        node_type = _nonempty_string(node.get("type"))
        title = _nonempty_string(node.get("title"))
        track = _nonempty_string(node.get("track"))
        claim = _nonempty_string(node.get("claim"))
        if node_id is None:
            errors.append(f"{prefix}.id must be a non-empty string")
            continue
        if ID_PATTERN.fullmatch(node_id) is None:
            errors.append(f"{prefix}.id has invalid syntax: {node_id}")
        if node_id in node_by_id:
            errors.append(f"duplicate node id: {node_id}")
        node_by_id[node_id] = node
        if node_type not in NODE_TYPES:
            errors.append(f"{node_id}.type is invalid: {node_type}")
        if title is None:
            errors.append(f"{node_id}.title must be a non-empty string")
        if track not in TRACKS:
            errors.append(f"{node_id}.track is invalid: {track}")
        if claim is None:
            errors.append(f"{node_id}.claim must be a non-empty string")

        if node_type == "source":
            url = _nonempty_string(node.get("url"))
            if url is None or not url.startswith("https://"):
                errors.append(f"{node_id}.url must be an https primary-source URL")
            if node.get("primary") is not True:
                errors.append(f"{node_id}.primary must be true")

        if node_type == "candidate":
            candidate_ids.add(node_id)
            status = _nonempty_string(node.get("status"))
            if status not in CANDIDATE_STATES:
                errors.append(f"{node_id}.status is invalid: {status}")
            if status is not None and "PASS" in status:
                errors.append(f"{node_id}.status may not contain PASS")
            history = _as_mapping_list(node.get("history"))
            if not history:
                errors.append(f"{node_id}.history must contain at least one transition")
            else:
                previous_to: str | None = None
                for h_index, transition in enumerate(history):
                    h_prefix = f"{node_id}.history[{h_index}]"
                    to_state = _nonempty_string(transition.get("to"))
                    from_state = transition.get("from")
                    if to_state not in CANDIDATE_STATES:
                        errors.append(f"{h_prefix}.to is invalid: {to_state}")
                    if from_state is not None and from_state != previous_to:
                        errors.append(f"{h_prefix}.from does not match preceding state")
                    if _nonempty_string(transition.get("date")) is None:
                        errors.append(f"{h_prefix}.date is required")
                    if _nonempty_string(transition.get("reason")) is None:
                        errors.append(f"{h_prefix}.reason is required")
                    evidence = transition.get("evidence")
                    if not isinstance(evidence, list) or not evidence:
                        errors.append(f"{h_prefix}.evidence must be a non-empty list")
                    previous_to = to_state
                if previous_to != status:
                    errors.append(f"{node_id}.status does not match final history state")

    edge_keys: set[tuple[str, str, str]] = set()
    outgoing: dict[str, set[str]] = {node_id: set() for node_id in node_by_id}
    for index, edge in enumerate(edges):
        prefix = f"edges[{index}]"
        source = _nonempty_string(edge.get("source"))
        target = _nonempty_string(edge.get("target"))
        edge_type = _nonempty_string(edge.get("type"))
        if source is None or source not in node_by_id:
            errors.append(f"{prefix}.source is unknown: {source}")
        if target is None or target not in node_by_id:
            errors.append(f"{prefix}.target is unknown: {target}")
        if edge_type not in EDGE_TYPES:
            errors.append(f"{prefix}.type is invalid: {edge_type}")
        if _nonempty_string(edge.get("claim")) is None:
            errors.append(f"{prefix}.claim must be a non-empty string")
        if source is not None and target is not None and edge_type is not None:
            key = (source, target, edge_type)
            if key in edge_keys:
                errors.append(f"duplicate edge: {source} -[{edge_type}]-> {target}")
            edge_keys.add(key)
            if source in outgoing:
                outgoing[source].add(edge_type)

    for candidate_id in sorted(candidate_ids):
        node = node_by_id[candidate_id]
        status = _nonempty_string(node.get("status"))
        required = {"requires", "falsified_by", "distinguished_by"}
        missing = required - outgoing[candidate_id]
        for edge_type in sorted(missing):
            errors.append(f"{candidate_id} lacks outgoing {edge_type} edge")
        if status in RETIRED_STATES and "retired_by" not in outgoing[candidate_id]:
            errors.append(f"{candidate_id} is retired but lacks outgoing retired_by edge")
        if status not in RETIRED_STATES and "branches_to" not in outgoing[candidate_id]:
            errors.append(f"{candidate_id} is active but lacks outgoing branches_to edge")

    for node_id, node in sorted(node_by_id.items()):
        if node.get("type") == "venue_claim":
            required = {"requires"}
            if not required.issubset(outgoing[node_id]):
                errors.append(f"{node_id} must require explicit data and compute gates")

    return sorted(errors)


def assert_valid_graph(graph: Mapping[str, object]) -> None:
    """Raise one readable exception when the graph violates its process contract."""

    errors = validate_graph(graph)
    if errors:
        raise ValueError("invalid theory graph:\n- " + "\n- ".join(errors))


def main(argv: Sequence[str] | None = None) -> int:
    """Validate one canonical theory graph from the command line."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path)
    args = parser.parse_args(argv)
    graph = load_graph(args.graph)
    errors = validate_graph(graph)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"valid {SCHEMA_VERSION}: {len(cast(list[object], graph['nodes']))} nodes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
