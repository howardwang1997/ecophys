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

    assert "227 route nodes" in result
    assert "235 typed edges" in result
    assert "804 evidence/artifact locators" in result
    assert "git_ref=35" in result


def test_only_declared_routes_remain_open() -> None:
    document = load_document()
    open_routes: dict[str, str] = {}
    for node in document_nodes(document):
        route_id = node["id"]
        status = node["status"]
        assert isinstance(route_id, str)
        assert isinstance(status, str)
        if status in {"candidate", "active", "parked"}:
            open_routes[route_id] = status

    assert open_routes == {
        "dcrdex_verifiable_sequencing_response": "parked",
        "fcc_clock1_random_rank_cascade": "candidate",
        "verification_liquidity": "active",
    }


def test_capability_first_cycle_is_terminal_and_creates_no_open_route() -> None:
    document = load_document()
    cycle = node_by_id(document, "discovery_loop_topic_cycle_3_capability_first_20260825")
    assert cycle["status"] == "passed_closed"

    child_ids = {
        "shared_capital_global_order_exclusion",
        "bonded_executable_liquidity_promises",
        "deferred_settlement_event_heap_backpressure",
        "lazy_expiry_matching_maintenance_debt",
        "regenerative_reverse_order_lattice",
        "tickless_priority_inversion",
        "global_account_lock_contention_liquidity",
        "programmable_offer_liquidity_oracle",
    }
    assert {node_id: node_by_id(document, node_id)["status"] for node_id in child_ids} == {
        node_id: "failed_closed" for node_id in child_ids
    }

    aggregate_targets = {
        edge["target"]
        for edge in document_edges(document)
        if edge["source"] == "discovery_loop_topic_cycle_3_capability_first_20260825"
        and edge["type"] == "aggregates"
    }
    assert aggregate_targets == child_ids


def test_shared_capital_trilemma_is_a_closed_parent_reduction() -> None:
    document = load_document()
    cycle = node_by_id(
        document, "discovery_loop_topic_cycle_4_shared_capital_trilemma_20260825"
    )
    route = node_by_id(document, "shared_capital_quote_integrity_coordination_trilemma")

    assert cycle["status"] == "passed_closed"
    assert route["status"] == "failed_closed"
    failure_codes = route["failure_codes"]
    assert isinstance(failure_codes, list)
    assert "bounded_counter_decrement_not_invariant_confluent" in failure_codes
    assert "escrow_rights_exact_remedy" in failure_codes

    matching_edges = [
        edge
        for edge in document_edges(document)
        if edge["source"]
        == "discovery_loop_topic_cycle_4_shared_capital_trilemma_20260825"
        and edge["target"] == "shared_capital_quote_integrity_coordination_trilemma"
        and edge["type"] == "aggregates"
    ]
    assert len(matching_edges) == 1


def test_intent_truth_cycle_is_terminal_and_creates_no_open_route() -> None:
    document = load_document()
    cycle_id = "discovery_loop_topic_cycle_5_intent_truth_20260826"
    cycle = node_by_id(document, cycle_id)
    assert cycle["status"] == "passed_closed"

    child_ids = {
        "rejected_intent_shadow_pressure",
        "constraint_boundary_rejection_local_time",
        "rejected_intent_retry_avalanche",
        "fixed_intent_tape_rule_counterfactual",
        "failed_intent_latent_demand_curve",
        "intent_commit_compression_ratio",
        "winner_loser_race_susceptibility",
        "constraint_release_intent_overshoot",
    }
    assert {node_id: node_by_id(document, node_id)["status"] for node_id in child_ids} == {
        node_id: "failed_closed" for node_id in child_ids
    }

    aggregate_targets = {
        edge["target"]
        for edge in document_edges(document)
        if edge["source"] == cycle_id and edge["type"] == "aggregates"
    }
    assert aggregate_targets == child_ids

    predecessor_edges = [
        edge
        for edge in document_edges(document)
        if edge["source"]
        == "discovery_loop_topic_cycle_4_shared_capital_trilemma_20260825"
        and edge["target"] == cycle_id
        and edge["type"] == "next_selected_route"
    ]
    assert len(predecessor_edges) == 1


def test_scaling_closure_cycle_is_terminal_and_creates_no_open_route() -> None:
    document = load_document()
    cycle_id = "discovery_loop_topic_cycle_6_scaling_closure_20260826"
    cycle = node_by_id(document, cycle_id)
    assert cycle["status"] == "passed_closed"

    child_ids = {
        "single_exponent_orderflow_roughness_impact_closure",
        "core_reaction_orderflow_identification",
        "sessionless_crypto_long_memory_discriminator",
        "operational_clock_scaling_closure",
    }
    assert {node_id: node_by_id(document, node_id)["status"] for node_id in child_ids} == {
        node_id: "failed_closed" for node_id in child_ids
    }

    aggregate_targets = {
        edge["target"]
        for edge in document_edges(document)
        if edge["source"] == cycle_id and edge["type"] == "aggregates"
    }
    assert aggregate_targets == child_ids

    predecessor_edges = [
        edge
        for edge in document_edges(document)
        if edge["source"] == "discovery_loop_topic_cycle_5_intent_truth_20260826"
        and edge["target"] == cycle_id
        and edge["type"] == "next_selected_route"
    ]
    assert len(predecessor_edges) == 1


def test_conservation_symmetry_cycle_is_terminal_and_creates_no_open_route() -> None:
    document = load_document()
    cycle_id = "discovery_loop_topic_cycle_7_conservation_symmetry_20260826"
    cycle = node_by_id(document, cycle_id)
    assert cycle["status"] == "passed_closed"

    child_ids = {
        "transaction_stoichiometric_market_charge",
        "open_interest_reaction_channel_response",
        "self_trade_prevention_identity_partition_response",
        "conservation_constrained_cross_impact_reciprocity",
        "l2_order_identity_lumpability_taxonomy",
        "cfmm_invariant_curvature_response",
    }
    assert {node_id: node_by_id(document, node_id)["status"] for node_id in child_ids} == {
        node_id: "failed_closed" for node_id in child_ids
    }

    aggregate_targets = {
        edge["target"]
        for edge in document_edges(document)
        if edge["source"] == cycle_id and edge["type"] == "aggregates"
    }
    assert aggregate_targets == child_ids

    predecessor_edges = [
        edge
        for edge in document_edges(document)
        if edge["source"]
        == "discovery_loop_topic_cycle_6_scaling_closure_20260826"
        and edge["target"] == cycle_id
        and edge["type"] == "next_selected_route"
    ]
    assert len(predecessor_edges) == 1


def test_cross_engine_discrepancy_cycle_is_terminal_and_creates_no_open_route() -> None:
    document = load_document()
    cycle_id = "discovery_loop_topic_cycle_8_cross_engine_discrepancy_20260826"
    cycle = node_by_id(document, cycle_id)
    assert cycle["status"] == "passed_closed"

    child_ids = {
        "hard_boundary_batch_shadow_generator",
        "adaptive_scheduler_information_filtration_response",
        "cross_simulator_disagreement_intervention_certificate",
    }
    assert {node_id: node_by_id(document, node_id)["status"] for node_id in child_ids} == {
        node_id: "failed_closed" for node_id in child_ids
    }

    aggregate_targets = {
        edge["target"]
        for edge in document_edges(document)
        if edge["source"] == cycle_id and edge["type"] == "aggregates"
    }
    assert aggregate_targets == child_ids

    predecessor_edges = [
        edge
        for edge in document_edges(document)
        if edge["source"] == "discovery_loop_topic_cycle_7_conservation_symmetry_20260826"
        and edge["target"] == cycle_id
        and edge["type"] == "next_selected_route"
    ]
    assert len(predecessor_edges) == 1


def test_asset_portfolio_cycle_is_terminal_and_probability_is_not_a_failure_code() -> None:
    document = load_document()
    cycle_id = "discovery_loop_topic_cycle_9_asset_portfolio_probability_gate_20260826"
    cycle = node_by_id(document, cycle_id)
    assert cycle["status"] == "passed_closed"

    child_ids = {
        "expanded_rule605_execution_truth_bridge",
        "laboratory_information_filtration_relaxation",
        "treasury_central_clearing_liquidity_quench",
        "uniswap_v4_fee_family_relaxation",
        "solana_compute_capacity_quench",
    }
    for node_id in child_ids:
        node = node_by_id(document, node_id)
        assert node["status"] == "failed_closed"
        failure_codes = node["failure_codes"]
        assert isinstance(failure_codes, list)
        assert "hostile_t0_lower_bound_below_activation_floor" not in failure_codes

    aggregate_targets = {
        edge["target"]
        for edge in document_edges(document)
        if edge["source"] == cycle_id and edge["type"] == "aggregates"
    }
    assert aggregate_targets == child_ids

    predecessor_edges = [
        edge
        for edge in document_edges(document)
        if edge["source"] == "discovery_loop_topic_cycle_8_cross_engine_discrepancy_20260826"
        and edge["target"] == cycle_id
        and edge["type"] == "next_selected_route"
    ]
    assert len(predecessor_edges) == 1


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


def test_probability_alone_cannot_close_graph_node(tmp_path: Path) -> None:
    document = load_document()
    node = node_by_id(document, "expanded_rule605_execution_truth_bridge")
    node["failure_codes"] = ["hostile_t0_lower_bound_below_activation_floor"]
    graph_path = write_document(tmp_path, document)

    with pytest.raises(GraphValidationError, match="cannot terminalize from probability alone"):
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
