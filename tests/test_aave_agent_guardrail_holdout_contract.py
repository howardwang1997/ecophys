from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs/empirical_physics/aave_agent_guardrail_holdout_d0_v1.yaml"
EXPECTED_CHAIN_IDS = {
    "arbitrum": 42161,
    "avalanche": 43114,
    "base": 8453,
    "bnb": 56,
    "gnosis": 100,
    "linea": 59144,
    "optimism": 10,
    "plasma": 9745,
    "polygon": 137,
}
ADDRESS_BOOK_SUFFIXES = {
    **{name: name.title() for name in EXPECTED_CHAIN_IDS},
    "bnb": "BNB",
}


def _config() -> dict[str, Any]:
    value = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_holdout_is_frozen_before_events_and_excludes_ethereum_pilot() -> None:
    config = _config()
    contract = config["contract"]

    assert contract["status"] == "frozen_before_any_non_ethereum_agent_event_query"
    assert contract["ethereum_pilot_is_excluded_from_all_holdout_counts"] is True
    assert config["pilot_binding"] == {
        "result_path": "results/empirical_physics/aave_agent_guardrail_d0_result.json",
        "canonical_payload_sha256": ("764f08a7a02c550f28f8b7ace275cf4e451ba5430ea5768aff55f374c1226460"),
        "decision": "stop_threshold_causal_route_before_market_outcomes",
        "diagnostic_used_for_design_only": "pre_registration_left_truncation",
        "pilot_cannot_be_reclassified_or_pooled_into_holdout": True,
    }
    assert set(config["chains"]) == set(EXPECTED_CHAIN_IDS)
    assert "ethereum" not in config["chains"]


def test_all_chain_anchors_and_source_addresses_are_explicit() -> None:
    config = _config()
    chains = config["chains"]
    hash_pattern = re.compile(r"0x[0-9a-f]{64}")
    address_pattern = re.compile(r"0x[0-9A-Fa-f]{40}")

    for name, expected_chain_id in EXPECTED_CHAIN_IDS.items():
        chain = chains[name]
        assert chain["chain_id"] == expected_chain_id
        assert 0 <= chain["from_block"] < chain["to_block"]
        assert hash_pattern.fullmatch(chain["from_block_hash"])
        assert hash_pattern.fullmatch(chain["to_block_hash"])
        assert address_pattern.fullmatch(chain["agent_hub"])
        assert address_pattern.fullmatch(chain["range_validation_module"])
        assert address_pattern.fullmatch(chain["edge_risk_oracle"])
        suffix = ADDRESS_BOOK_SUFFIXES[name]
        assert chain["address_book_modules"] == [f"Misc{suffix}", f"AaveV3{suffix}"]
        assert len(chain["expected_agent_types"]) in {1, 2}
        assert chain["anchor_rpc"].startswith("https://")
        assert len(chain["formal_rpc_candidates"]) >= 2
        assert all(url.startswith("https://") for url in chain["formal_rpc_candidates"])

    assert config["time_window"]["start_timestamp"] == 1763942400
    assert config["time_window"]["start_utc"] == "2025-11-24T00:00:00Z"
    assert chains["bnb"]["anchor_rpc_eth_get_logs_disabled_by_provider"] is True


def test_activation_batch_boundary_and_stop_rules_are_conservative() -> None:
    config = _config()
    eligibility = config["eligibility"]
    batching = config["batching"]
    boundary = config["boundary_support"]
    thresholds = config["pass_thresholds"]
    stop = config["stop_rules"]

    assert eligibility["require_exactly_one_prior_agent_registration"] is True
    assert eligibility["require_registered_risk_oracle_equals_address_book_edge_risk_oracle"] is True
    assert eligibility["required_prior_initialization"] == [
        "AgentAddressSet",
        "AgentEnabledSet_true",
        "ExpirationPeriodSet",
        "MinimumDelaySet",
    ]
    assert eligibility["pre_activation_or_never_registered_proposals"]["retained_in_exclusion_ledger"]
    assert eligibility["pre_activation_or_never_registered_proposals"][
        "excluded_from_support_and_terminal_classification_denominators"
    ]
    assert eligibility["post_activation_ambiguous_proposals"]["count_against_terminal_classification"]

    assert batching["connected_component_rule"] == ("adjacent_oracle_timestamps_at_most_120_seconds_apart")
    assert batching["update_type_or_chain_need_not_match"] is True
    assert batching["inference_must_cluster_by_batch"] is True
    assert boundary["never_pool_boundaries_across_chains_or_agents"] is True
    assert boundary["minimum_qualifying_boundaries"] == 2
    assert boundary["minimum_chains_with_qualifying_boundary"] == 2
    assert thresholds["minimum_represented_chains"] == 3
    assert thresholds["minimum_proposal_batches"] == 10
    assert thresholds["minimum_terminal_classification_rate"] == 0.90
    assert stop == {
        "any_pass_or_boundary_threshold_failure_stops_before_d1": True,
        "no_chain_may_be_dropped_for_low_activity": True,
        "unavailable_transport_requires_replacement_not_panel_selection": True,
        "no_market_outcomes_on_failure": True,
        "no_synthetic_rejected_actions": True,
        "no_gpu_or_ecomd": True,
    }


def test_holdout_transport_and_resource_caps_remain_free_and_cpu_only() -> None:
    config = _config()
    transport = config["transport"]
    resources = config["resources"]

    assert transport["qualification_occurs_only_after_this_freeze"] is True
    assert transport["require_nonempty_hub_shard_identity_crosscheck"] is True
    assert transport["identity_crosscheck_sources"] == 2
    assert transport["no_api_keys_or_paid_endpoints"] is True
    assert transport["raw_rpc_responses_retained"] is False
    assert resources == {
        "maximum_cpu_core_hours": 50,
        "maximum_retained_derived_gb": 5,
        "gpu_hours": 0,
        "paid_data_budget_usd": 0,
        "current_gpu_pool_held_idle": ["v100_32gb_a", "v100_32gb_b", "rtx2060"],
        "h20_assumed": False,
    }
