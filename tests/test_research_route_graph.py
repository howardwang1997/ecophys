from pathlib import Path
from typing import Any, cast

import pytest
import yaml

from scripts.validate_research_route_graph import (
    GraphValidationError,
    validate_declared_schema,
    validate_edges,
    validate_graph,
    validate_nodes,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = REPO_ROOT / ".claude" / "memory" / "research_route_knowledge_graph.yaml"


def load_mutable_graph() -> dict[str, Any]:
    loaded = yaml.safe_load(GRAPH_PATH.read_text(encoding="utf-8"))
    return cast(dict[str, Any], loaded)


def test_current_research_route_graph_is_valid() -> None:
    result = validate_graph(GRAPH_PATH)
    assert result.startswith("OK: 17 route nodes")
    assert "missing_legacy=0" in result


def test_unknown_route_status_is_rejected() -> None:
    graph = load_mutable_graph()
    graph["nodes"][0]["status"] = "quietly_reopened"
    scope_start, updated_at = validate_declared_schema(graph)

    with pytest.raises(GraphValidationError, match="status is unknown"):
        validate_nodes(graph, REPO_ROOT, scope_start, updated_at)


def test_edge_to_unknown_route_is_rejected() -> None:
    graph = load_mutable_graph()
    scope_start, updated_at = validate_declared_schema(graph)
    nodes, opened, closed, locator_ids, _, _ = validate_nodes(
        graph,
        REPO_ROOT,
        scope_start,
        updated_at,
    )
    graph["edges"][0]["target"] = "unregistered_route"

    with pytest.raises(GraphValidationError, match="target has no node"):
        validate_edges(graph, nodes, opened, closed, locator_ids)
