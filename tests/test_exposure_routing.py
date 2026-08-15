from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ecomd.research.exposure_routing import (
    compare_event_channels,
    concentration_metrics,
    summarize_exposure_routing,
    validate_routing_contract,
)
from ecomd.research.uniswap_v3_preperiod_support import hash_file, load_contract


def test_uniform_and_concentrated_measures_have_expected_geometry() -> None:
    uniform = concentration_metrics([1, 1, 1, 1], top_k=[1, 2])
    assert uniform["hhi"] == 0.25
    assert uniform["inverse_hhi_effective_count"] == 4.0
    assert uniform["gini_population"] == 0.0
    assert uniform["uniform_to_event_total_variation"] == 0.0
    assert uniform["exposure_multiplier_variance"] == 0.0

    concentrated = concentration_metrics([4, 0, 0, 0], top_k=[1, 2])
    assert concentrated["hhi"] == 1.0
    assert concentrated["inverse_hhi_effective_count"] == 1.0
    assert concentrated["gini_population"] == 0.75
    assert concentrated["uniform_to_event_total_variation"] == 0.75
    assert concentrated["exposure_multiplier_variance"] == 3.0


def test_zero_measure_is_described_without_inventing_weights() -> None:
    result = concentration_metrics([0, 0], top_k=[1])
    assert result["active_count"] == 0
    assert result["hhi"] is None
    assert result["top_k_shares"] == {"1": None}


def test_channel_comparison_recovers_identical_and_disjoint_limits() -> None:
    identical = compare_event_channels([1, 2, 0], [1, 2, 0])
    assert identical["weight_total_variation"] == pytest.approx(0.0)
    assert identical["jensen_shannon_normalized"] == pytest.approx(0.0)
    assert identical["cosine_similarity"] == pytest.approx(1.0)

    disjoint = compare_event_channels([1, 0], [0, 1])
    assert disjoint["support_jaccard"] == 0.0
    assert disjoint["weight_total_variation"] == pytest.approx(1.0)
    assert disjoint["jensen_shannon_normalized"] == pytest.approx(1.0)
    assert disjoint["cosine_similarity"] == pytest.approx(0.0)


def test_full_summary_uses_exact_fee_and_batch_partitions() -> None:
    rows = [
        {
            "pool_address": f"0x{index:040x}",
            "packed_fee_value": 68 if index < 107 else 102,
            "calldata_index": index % 500,
            "swap_count": 1,
            "position_action_count": 2 if index < 10 else 0,
        }
        for index in range(1000)
    ]
    result = summarize_exposure_routing(rows, top_k=[1, 3, 5, 10, 20])
    assert result["population_pool_count"] == 1000
    partitions = result["partitions"]
    assert partitions["packed_fee_68"]["pool_count"] == 107
    assert partitions["packed_fee_102"]["pool_count"] == 893
    assert partitions["propagation_batch_1"]["pool_count"] == 500
    assert partitions["propagation_batch_2"]["pool_count"] == 500
    assert result["channels"]["swap_count"]["uniform_to_event_total_variation"] == 0.0


def test_routing_contract_pins_parent_and_no_new_access() -> None:
    root = Path(__file__).resolve().parents[1]
    contract = load_contract(root / "data/manifests/uniswap_v3_exposure_routing_exploratory_v1.yaml")
    parent = contract["parent"]
    assert isinstance(parent, dict)
    census_path = root / parent["exposure_census"]
    summary_path = root / parent["summary"]
    assert (
        validate_routing_contract(
            contract,
            exposure_census_sha256=hash_file(census_path),
            summary_sha256=hash_file(summary_path),
        )
        == ()
    )

    mutated = deepcopy(contract)
    mutated["access_boundary"]["post_treatment_data_opened"] = True
    assert "access_boundary.post_treatment_data_opened must remain false" in validate_routing_contract(
        mutated,
        exposure_census_sha256=hash_file(census_path),
        summary_sha256=hash_file(summary_path),
    )
