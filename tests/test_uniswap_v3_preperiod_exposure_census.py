from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ecomd.research.uniswap_v3_preperiod_support import (
    MINT_TOPIC,
    POOL_EVENT_TOPICS,
    build_exposure_census_row,
    canonical_json_sha256,
    census_population_rows,
    hash_file,
    load_contract,
    load_jsonl,
    normalize_rpc_pool_log,
    summarize_exposure_census,
    validate_exposure_census_contract,
)

NPM = "0xc36442b4a4522e871399cd717abdd847ab11fe88"
POOL = "0x" + "a" * 40
OTHER_MANAGER = "0x" + "b" * 40
TX_HASH = "0x" + "1" * 64
BLOCK_HASH = "0x" + "2" * 64


def _topic_address(address: str) -> str:
    return "0x" + "0" * 24 + address[2:]


def _rpc_mint_log() -> dict[str, object]:
    return {
        "address": POOL,
        "blockNumber": "0x64",
        "blockHash": BLOCK_HASH,
        "transactionIndex": "0x2",
        "logIndex": "0x5",
        "transactionHash": TX_HASH,
        "topics": [MINT_TOPIC, _topic_address(NPM), "0x" + "0" * 64, "0x" + "f" * 64],
        "data": "0x" + "00" * 96,
        "removed": False,
    }


def test_repository_contract_reproduces_full_u0_population() -> None:
    root = Path(__file__).resolve().parents[1]
    contract = load_contract(root / "data/manifests/uniswap_v3_preperiod_exposure_census_v1.yaml")
    parents = contract["parents"]
    assert isinstance(parents, dict)
    treatment_path = root / parents["u0_treatment_ledger"]
    u1a_summary_path = root / parents["u1a_summary"]
    treatment_rows = load_jsonl(treatment_path)

    assert (
        validate_exposure_census_contract(
            contract,
            treatment_rows,
            treatment_ledger_sha256=hash_file(treatment_path),
            u1a_summary_sha256=hash_file(u1a_summary_path),
        )
        == ()
    )
    population = census_population_rows(treatment_rows)
    assert len(population) == 1000
    assert len({row["pool_address"] for row in population}) == 1000
    contract_population = contract["population"]
    assert isinstance(contract_population, dict)
    assert canonical_json_sha256(population) == contract_population["population_rows_sha256"]

    mutated = deepcopy(contract)
    mutated["access_boundary"]["post_treatment_responses_opened"] = True
    assert (
        "access_boundary.post_treatment_responses_opened must remain false"
        in validate_exposure_census_contract(
            mutated,
            treatment_rows,
            treatment_ledger_sha256=hash_file(treatment_path),
            u1a_summary_sha256=hash_file(u1a_summary_path),
        )
    )

    endpoint_mutation = deepcopy(contract)
    endpoint_mutation["sources"]["blockscout_eth_rpc_url"] = "https://example.invalid"
    assert "sources.blockscout_eth_rpc_url changed" in validate_exposure_census_contract(
        endpoint_mutation,
        treatment_rows,
        treatment_ledger_sha256=hash_file(treatment_path),
        u1a_summary_sha256=hash_file(u1a_summary_path),
    )


def test_rpc_log_normalization_discards_payload_and_rejects_removed_log() -> None:
    raw = _rpc_mint_log()
    event = normalize_rpc_pool_log(
        raw,
        expected_pool=POOL,
        allowed_topics=POOL_EVENT_TOPICS,
        from_block=90,
        to_block=110,
    )
    assert event["event_type"] == "mint"
    assert event["manager_owner"] == NPM
    assert event["block_number"] == 100
    assert "data" not in event
    assert len(event["data_sha256"]) == 64

    removed = dict(raw)
    removed["removed"] = True
    with pytest.raises(ValueError, match="not removed"):
        normalize_rpc_pool_log(
            removed,
            expected_pool=POOL,
            allowed_topics=POOL_EVENT_TOPICS,
            from_block=90,
            to_block=110,
        )


def test_exposure_row_retains_counts_but_not_manager_addresses() -> None:
    mint = normalize_rpc_pool_log(
        _rpc_mint_log(),
        expected_pool=POOL,
        allowed_topics=POOL_EVENT_TOPICS,
        from_block=90,
        to_block=110,
    )
    burn = dict(mint)
    burn["event_type"] = "burn"
    burn["manager_owner"] = OTHER_MANAGER
    burn["log_index"] = 6
    swap = dict(mint)
    swap["event_type"] = "swap"
    swap["manager_owner"] = None
    swap["log_index"] = 7
    row = build_exposure_census_row(
        {
            "pool_address": POOL,
            "packed_fee_value": 68,
            "treatment_transaction_hash": "0x" + "3" * 64,
            "calldata_index": 0,
        },
        [mint, burn, swap],
        npm_address=NPM,
    )
    assert row["swap_count"] == 1
    assert row["position_action_count"] == 2
    assert row["npm_position_action_count"] == 1
    assert row["npm_position_action_share"] == 0.5
    assert row["distinct_manager_owner_count"] == 2
    assert "manager_owner_counts" not in row


def test_summary_applies_population_fee_support_and_concentration_gates() -> None:
    rows: list[dict[str, object]] = []
    for index in range(1000):
        fee = 68 if index < 107 else 102
        within_fee = index if fee == 68 else index - 107
        swap_active = within_fee < 25
        position_active = within_fee < 10
        rows.append(
            {
                "packed_fee_value": fee,
                "swap_count": 1 if swap_active else 0,
                "position_action_count": 10 if position_active else 0,
                "npm_position_action_count": 8 if position_active else 0,
                "swap_active": swap_active,
                "position_active": position_active,
                "economically_exposed_preperiod": swap_active or position_active,
            }
        )

    result = summarize_exposure_census(
        rows,
        duplicate_log_count=0,
        conflicting_log_count=0,
        complete_unsaturated_partitions=True,
        minimum_swap_active_pools=50,
        minimum_position_active_pools=20,
        minimum_position_action_logs=200,
        minimum_swap_active_pools_per_fee_value=5,
        minimum_position_active_pools_per_fee_value=2,
        minimum_npm_position_action_share=0.5,
        maximum_single_pool_swap_count_share=0.25,
        maximum_single_pool_position_action_count_share=0.5,
    )
    assert result["pass"] is True
    assert result["swap_active_pool_count"] == 50
    assert result["position_active_pool_count"] == 20
    assert result["npm_position_action_share"] == 0.8
    assert result["control_source_status"] == "UNRESOLVED_SEPARATE_GATE_REQUIRED"

    rows[0]["swap_count"] = 100
    concentrated = summarize_exposure_census(
        rows,
        duplicate_log_count=0,
        conflicting_log_count=0,
        complete_unsaturated_partitions=True,
        minimum_swap_active_pools=50,
        minimum_position_active_pools=20,
        minimum_position_action_logs=200,
        minimum_swap_active_pools_per_fee_value=5,
        minimum_position_active_pools_per_fee_value=2,
        minimum_npm_position_action_share=0.5,
        maximum_single_pool_swap_count_share=0.25,
        maximum_single_pool_position_action_count_share=0.5,
    )
    assert concentrated["pass"] is False
    assert concentrated["gates"]["maximum_single_pool_swap_count_share"] is False
