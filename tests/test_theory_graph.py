from copy import deepcopy
from pathlib import Path

from ecomd.research.theory_graph import load_graph, validate_graph

GRAPH_PATH = Path("research/theory_exploration/knowledge_graph.yaml")


def test_canonical_theory_graph_is_valid() -> None:
    graph = load_graph(GRAPH_PATH)
    assert validate_graph(graph) == []


def test_candidate_pass_and_missing_attack_edges_are_rejected() -> None:
    graph = load_graph(GRAPH_PATH)
    broken = deepcopy(graph)
    nodes = broken["nodes"]
    assert isinstance(nodes, list)
    candidate = next(node for node in nodes if node["id"] == "cand.nmi.mechanism_excitation")
    candidate["status"] = "PASS"
    candidate["history"][-1]["to"] = "PASS"
    edges = broken["edges"]
    assert isinstance(edges, list)
    broken["edges"] = [
        edge
        for edge in edges
        if not (
            edge["source"] == "cand.nmi.mechanism_excitation"
            and edge["type"] == "falsified_by"
        )
    ]

    errors = validate_graph(broken)
    assert any("status is invalid" in error for error in errors)
    assert any("lacks outgoing falsified_by" in error for error in errors)


def test_unknown_endpoint_and_duplicate_node_are_rejected() -> None:
    graph = load_graph(GRAPH_PATH)
    broken = deepcopy(graph)
    nodes = broken["nodes"]
    edges = broken["edges"]
    assert isinstance(nodes, list)
    assert isinstance(edges, list)
    nodes.append(deepcopy(nodes[0]))
    edges[0]["target"] = "missing.node"

    errors = validate_graph(broken)
    assert any("duplicate node id" in error for error in errors)
    assert any("target is unknown" in error for error in errors)
