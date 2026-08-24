from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest
import yaml

from scripts.validate_research_route_graph import GraphValidationError, validate_graph

REPO_ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = REPO_ROOT / ".claude" / "memory" / "research_route_knowledge_graph.yaml"


def load_document() -> dict[str, object]:
    loaded = cast(object, yaml.safe_load(GRAPH_PATH.read_text(encoding="utf-8")))
    assert isinstance(loaded, dict)
    assert all(isinstance(key, str) for key in loaded)
    return cast(dict[str, object], loaded)


def write_document(tmp_path: Path, document: dict[str, object]) -> Path:
    graph_path = tmp_path / "research_route_knowledge_graph.yaml"
    graph_path.write_text(
        yaml.safe_dump(document, sort_keys=False),
        encoding="utf-8",
    )
    return graph_path


def document_nodes(document: dict[str, object]) -> list[dict[str, object]]:
    raw_nodes = document["nodes"]
    assert isinstance(raw_nodes, list)
    return [cast(dict[str, object], node) for node in raw_nodes]


def document_edges(document: dict[str, object]) -> list[dict[str, object]]:
    raw_edges = document["edges"]
    assert isinstance(raw_edges, list)
    return [cast(dict[str, object], edge) for edge in raw_edges]


def node_by_id(document: dict[str, object], node_id: str) -> dict[str, object]:
    return next(node for node in document_nodes(document) if node["id"] == node_id)


def node_locators(node: dict[str, object], field: str) -> list[dict[str, object]]:
    raw_locators = node[field]
    assert isinstance(raw_locators, list)
    return [cast(dict[str, object], locator) for locator in raw_locators]


def test_canonical_graph_validates_offline() -> None:
    result = validate_graph(GRAPH_PATH, REPO_ROOT)

    assert "54 route nodes" in result
    assert "git_ref=35" in result


def test_unknown_edge_endpoint_is_rejected(tmp_path: Path) -> None:
    document = load_document()
    document_edges(document)[0]["target"] = "nonexistent_route"
    graph_path = write_document(tmp_path, document)

    with pytest.raises(GraphValidationError, match="target has no node"):
        validate_graph(graph_path, REPO_ROOT)


def test_terminal_node_requires_formal_evidence(tmp_path: Path) -> None:
    document = load_document()
    node = node_by_id(document, "mace_lite_v1_architecture")
    for field in ("evidence", "artifacts"):
        for locator in node_locators(node, field):
            locator["kind"] = "supporting_material"
    graph_path = write_document(tmp_path, document)

    with pytest.raises(GraphValidationError, match="lacks formal terminal evidence"):
        validate_graph(graph_path, REPO_ROOT)


def test_missing_present_artifact_is_rejected(tmp_path: Path) -> None:
    document = load_document()
    node = node_by_id(document, "mace_lite_v1_architecture")
    artifact = node_locators(node, "artifacts")[0]
    artifact["path"] = "archive/does_not_exist/formal_result.md"
    graph_path = write_document(tmp_path, document)

    with pytest.raises(GraphValidationError, match="not a reachable local file"):
        validate_graph(graph_path, REPO_ROOT)


def test_explicit_missing_legacy_artifact_is_accepted(tmp_path: Path) -> None:
    document = load_document()
    node = node_by_id(document, "mace_lite_v1_architecture")
    artifact = node_locators(node, "artifacts")[0]
    artifact.update(
        {
            "availability": "missing_legacy",
            "path": "archive/missing_legacy/mace_v1_formal_result.md",
            "note": "The formal legacy result is absent; the closure memory remains reachable.",
        }
    )
    graph_path = write_document(tmp_path, document)

    result = validate_graph(graph_path, REPO_ROOT)

    assert "missing_legacy=1" in result


def test_unknown_git_commit_is_rejected(tmp_path: Path) -> None:
    document = load_document()
    node = node_by_id(document, "theory_reduction_nmi_v1")
    locator = node_locators(node, "evidence")[0]
    locator["commit"] = "0" * 40
    graph_path = write_document(tmp_path, document)

    with pytest.raises(GraphValidationError, match="commit is not locally available"):
        validate_graph(graph_path, REPO_ROOT)
