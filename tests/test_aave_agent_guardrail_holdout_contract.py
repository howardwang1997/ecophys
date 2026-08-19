from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs/empirical_physics/aave_agent_guardrail_holdout_d0_v1.yaml"
V2_CONFIG_PATH = REPO_ROOT / "configs/empirical_physics/aave_agent_guardrail_holdout_d0_v2.yaml"
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


def _config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
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


def test_v2_is_an_outcome_blind_transport_only_amendment() -> None:
    parent = _config()
    amended = _config(V2_CONFIG_PATH)
    contract = amended["contract"]
    ledger = amended["transport"][
        "amendment_2026_08_20_after_outcome_blind_formal_transport_diagnostics"
    ]

    assert contract["version"] == 2
    assert contract["status"] == (
        "transport_amended_after_outcome_blind_policy_event_diagnostics_before_market_outcomes"
    )
    assert ledger["parent_config_sha256"] == (
        "1c2eaa505b1993df153ff8cdd90ff698745fb4a7ec398aee8fa9f301e5a47eb9"
    )
    assert ledger["parent_repository_git_sha"] == "ac99559212dd0a0943c669b5d0981908e44d81e8"
    assert ledger["market_outcomes_queried_before_amendment"] is False
    assert ledger["fixed_block_unions_and_scientific_rules_unchanged"] is True
    assert ledger["all_parent_config_chain_artifacts_are_diagnostic_only"] is True
    assert ledger["all_chains_must_rerun_under_one_v2_config_digest"] is True

    invariant_sections = (
        "pilot_binding",
        "official_sources",
        "time_window",
        "allowed_event_families",
        "eligibility",
        "batching",
        "matching",
        "boundary_support",
        "pass_thresholds",
        "forbidden_data",
        "stop_rules",
        "resources",
    )
    for section in invariant_sections:
        assert amended[section] == parent[section]

    transport_only_chain_keys = {
        "formal_rpc_candidates",
        "qualification_from_block",
        "qualification_to_block",
        "qualification_expected_canonical_log_identity_sha256",
    }
    for chain_name, parent_chain in parent["chains"].items():
        amended_chain = amended["chains"][chain_name]
        assert {
            key: value for key, value in amended_chain.items() if key not in transport_only_chain_keys
        } == {key: value for key, value in parent_chain.items() if key not in transport_only_chain_keys}

    expected_qualification = {
        "arbitrum": (
            421_201_737,
            421_211_736,
            "653120b418d86137a073b761c34e87a195cbe9879abedfb1545c2f33ecc69bda",
            "https://arbitrum.gateway.tenderly.co",
        ),
        "avalanche": (
            75_715_069,
            75_725_068,
            "8ab51afad9e6c4b3bae7b1a207721e35270cd36cee85d3758e24225707311fca",
            "https://avalanche.gateway.tenderly.co",
        ),
        "base": (
            40_786_527,
            40_796_526,
            "31b2e41e624cc194fc7d8950560ab8fb7fea652e275383ce72ff2c1b0f212090",
            "https://base.gateway.tenderly.co",
        ),
        "bnb": (
            75_184_723,
            75_194_722,
            "2d50fe7fd5bcb03ca93f6783a94047a9664c28daf21acfc490e168f5591985a4",
            "https://rpc.sentio.xyz/bsc",
        ),
        "gnosis": (
            44_149_823,
            44_159_822,
            "50c3b3df7595fb2b80da568394fd97be5eaa4a6aaa3ec7fdd130cfe5d8c3f52a",
            "https://gnosis.gateway.tenderly.co",
        ),
        "linea": (
            27_827_319,
            27_837_318,
            "5fe9ba21f7fb6104045d109368a425fb2393351a8100aabcf14e10eaf8293ff0",
            "https://linea.gateway.tenderly.co",
        ),
        "optimism": (
            146_381_812,
            146_391_811,
            "5f54a0071b178010925103a6c7bb3f955b111e06c0a7bc915e5900a13350fb54",
            "https://optimism.gateway.tenderly.co",
        ),
        "plasma": (
            11_441_827,
            11_451_826,
            "2968ed416e3328759c2269861ddbfaa195fd74a870408f56d76a24cef319f65b",
            "https://rpc.sentio.xyz/plasma-mainnet",
        ),
        "polygon": (
            81_628_684,
            81_638_683,
            "e93d23930d503f9099fdb99734fcfa2f278d0151b39a83ef7d8739788aba2b0b",
            "https://polygon.gateway.tenderly.co",
        ),
    }
    for chain_name, (start, end, digest, primary) in expected_qualification.items():
        chain = amended["chains"][chain_name]
        assert chain["qualification_from_block"] == start
        assert chain["qualification_to_block"] == end
        assert chain["qualification_expected_canonical_log_identity_sha256"] == digest
        assert chain["formal_rpc_candidates"][0] == primary
    assert set(expected_qualification) == set(EXPECTED_CHAIN_IDS)
    assert amended["chains"]["bnb"]["formal_rpc_candidates"][:3] == [
        "https://rpc.sentio.xyz/bsc",
        "https://bsc.rpc.blxrbdn.com",
        "https://rpc.nodeflare.app/bnb/public",
    ]
    assert amended["chains"]["polygon"]["formal_rpc_candidates"][:3] == [
        "https://polygon.gateway.tenderly.co",
        "https://rpc.sentio.xyz/matic",
        "https://polygon.drpc.org",
    ]
    assert ledger[
        "fast_primary_transport_concentration_requires_full_union_independent_replication_"
        "before_market_outcomes"
    ] is True
    assert {
        key: value
        for key, value in amended["contract"].items()
        if key not in {"version", "status"}
    } == {
        key: value
        for key, value in parent["contract"].items()
        if key not in {"version", "status"}
    }


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
        assert chain["formal_initial_get_logs_span"] >= 10_000
        assert chain["anchor_rpc"].startswith("https://")
        assert len(chain["formal_rpc_candidates"]) >= 2
        assert all(url.startswith("https://") for url in chain["formal_rpc_candidates"])

    assert config["time_window"]["start_timestamp"] == 1763942400
    assert config["time_window"]["start_utc"] == "2025-11-24T00:00:00Z"
    assert chains["bnb"]["anchor_rpc_eth_get_logs_disabled_by_provider"] is True
    assert "https://avalanche.drpc.org" in chains["avalanche"]["formal_rpc_candidates"]
    assert "https://bnb.api.onfinality.io/public" in chains["bnb"]["formal_rpc_candidates"]
    bnb = chains["bnb"]
    assert bnb["formal_initial_get_logs_span"] == 10_000
    assert bnb["qualification_from_block"] == 75_184_723
    assert bnb["qualification_to_block"] == 75_194_722
    assert (bnb["qualification_from_block"] - bnb["from_block"]) % 10_000 == 0
    assert bnb["qualification_state_transition"] == {
        "method_signature": "getAgentCount()",
        "last_zero_block": 75_187_733,
        "last_zero_count": 0,
        "first_positive_block": 75_187_734,
        "first_positive_count": 2,
    }
    assert bnb["formal_rpc_candidates"][:2] == [
        "https://rpc.nodeflare.app/bnb/public",
        "https://bsc.rpc.blxrbdn.com",
    ]
    assert bnb["qualification_expected_canonical_log_identity_sha256"] == (
        "2d50fe7fd5bcb03ca93f6783a94047a9664c28daf21acfc490e168f5591985a4"
    )


def test_activation_batch_boundary_and_stop_rules_are_conservative() -> None:
    config = _config()
    eligibility = config["eligibility"]
    batching = config["batching"]
    boundary = config["boundary_support"]
    thresholds = config["pass_thresholds"]
    stop = config["stop_rules"]

    assert eligibility["activation_requires_at_least_one_prior_initialized_registration"] is True
    assert eligibility["source_unambiguous_requires_exactly_one_prior_initialized_registration"] is True
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
    assert batching["maximum_adjacent_gap_seconds"] == 120
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
    assert transport["qualification_get_logs_span"] == 10_000
    assert transport["formal_initial_span_rule"] == (
        "approximate_seven_utc_days_unless_transport_amendment_records_smaller_provider_cap"
    )
    assert transport["formal_range_errors_split_recursively_without_changing_union"] is True
    assert transport["require_nonempty_hub_shard_identity_crosscheck"] is True
    assert transport["identity_crosscheck_sources"] == 2
    assert transport["no_api_keys_or_paid_endpoints"] is True
    assert transport["raw_rpc_responses_retained"] is False
    amendment = transport["amendment_2026_08_20_after_first_qualification_attempt"]
    assert amendment["fixed_10000_block_qualification_union_unchanged"] is True
    assert amendment["anchor_rpc_verifies_chain_and_hashes"] is True
    assert (
        amendment["first_archive_capable_anchor_or_formal_candidate_verifies_agent_hub_code_at_to_block"]
        is True
    )
    assert amendment["no_chain_sample_event_family_threshold_or_stop_rule_changed"] is True
    assert resources == {
        "maximum_cpu_core_hours": 50,
        "maximum_retained_derived_gb": 5,
        "gpu_hours": 0,
        "paid_data_budget_usd": 0,
        "current_gpu_pool_held_idle": ["v100_32gb_a", "v100_32gb_b", "rtx2060"],
        "h20_assumed": False,
    }
