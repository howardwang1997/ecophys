from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from ecomd.data.aave_agent_guardrail import (
    address_from_topic,
    assess_holdout_action_support,
    assign_action_batches,
    bool_from_topic,
    build_action_ledger,
    build_holdout_chain_ledger,
    decode_default_range_config_data,
    decode_market_range_config_data,
    decode_parameter_updated_data,
    decode_update_injected_data,
    summarize_delay_boundaries,
    summarize_holdout_delay_boundaries,
)
from scripts import audit_aave_agent_guardrail_d0 as guardrail_runner
from scripts.audit_aave_agent_guardrail_d0 import (
    HUB_SIGNATURES,
    RISK_ORACLE_SIGNATURE,
    _decode_hub_log,
    _decode_proposal_log,
    _keccak_topic,
    _load_checkpoint,
    _write_checkpoint,
)


def _word(value: int) -> bytes:
    return value.to_bytes(32, "big")


def _dynamic(value: bytes) -> bytes:
    padding = (-len(value)) % 32
    return _word(len(value)) + value + b"\x00" * padding


def _topic_uint(value: int) -> str:
    return "0x" + f"{value:064x}"


def _topic_address(value: str) -> str:
    return "0x" + "0" * 24 + value[2:].lower()


def _raw_log(address: str, topics: list[str], data: str = "0x") -> dict[str, Any]:
    return {
        "address": address,
        "topics": topics,
        "data": data,
        "blockNumber": "0xa",
        "blockHash": "0x" + "aa" * 32,
        "transactionHash": "0x" + "bb" * 32,
        "transactionIndex": "0x1",
        "logIndex": "0x2",
        "removed": False,
    }


def _parameter_data(
    reference: bytes,
    new_value: bytes,
    previous_value: bytes,
    timestamp: int,
    additional_data: bytes,
) -> str:
    values = [reference, new_value, previous_value, additional_data]
    offsets: list[int] = []
    tail = b""
    for value in values:
        offsets.append(5 * 32 + len(tail))
        tail += _dynamic(value)
    head = b"".join(
        [
            _word(offsets[0]),
            _word(offsets[1]),
            _word(offsets[2]),
            _word(timestamp),
            _word(offsets[3]),
        ]
    )
    return "0x" + (head + tail).hex()


def _event(name: str, block: int, timestamp: int, **values: Any) -> dict[str, Any]:
    return {
        "event_name": name,
        "block_number": block,
        "transaction_index": 0,
        "log_index": 0,
        "block_timestamp": timestamp,
        **values,
    }


def _proposal(block: int, timestamp: int, update_id: int, value: str) -> dict[str, Any]:
    return _event(
        "ParameterUpdated",
        block,
        timestamp,
        risk_oracle="0x" + "11" * 20,
        update_type_hash="0x" + "22" * 32,
        update_id=update_id,
        market="0x" + "33" * 20,
        new_value=value,
        oracle_timestamp=timestamp,
    )


def _injection(block: int, timestamp: int, update_id: int, value: str) -> dict[str, Any]:
    return _event(
        "UpdateInjected",
        block,
        timestamp,
        agent_id=0,
        update_type_hash="0x" + "22" * 32,
        update_id=update_id,
        market="0x" + "33" * 20,
        new_value=value,
        transaction_hash="0x" + f"{update_id:064x}",
    )


def test_decodes_dynamic_proposal_and_injection_fields() -> None:
    proposal = decode_parameter_updated_data(_parameter_data(b"ref-7", b"\x01\x02", b"", 123456, b"metadata"))
    assert proposal == {
        "reference_id": "ref-7",
        "new_value": "0x0102",
        "previous_value": "0x",
        "oracle_timestamp": 123456,
        "additional_data": "0x6d65746164617461",
    }

    value = b"\xaa\xbb\xcc"
    injection_data = "0x" + (_word(9) + _word(64) + _dynamic(value)).hex()
    assert decode_update_injected_data(injection_data) == {
        "update_id": 9,
        "new_value": "0xaabbcc",
    }


def test_decodes_range_configurations_without_eth_abi() -> None:
    static = b"".join([_word(500), _word(250), _word(1), _word(0)])
    assert decode_default_range_config_data("0x" + static.hex()) == {
        "max_increase": 500,
        "max_decrease": 250,
        "is_increase_relative": True,
        "is_decrease_relative": False,
    }

    update_type = b"VariableRateSlope2"
    market_data = _word(160) + static + _dynamic(update_type)
    assert decode_market_range_config_data("0x" + market_data.hex()) == {
        "update_type": "VariableRateSlope2",
        "range_config": {
            "max_increase": 500,
            "max_decrease": 250,
            "is_increase_relative": True,
            "is_decrease_relative": False,
        },
    }


def test_runner_decodes_indexed_agent_and_proposal_identity() -> None:
    hub = "0x" + "44" * 20
    oracle = "0x" + "11" * 20
    market = "0x" + "33" * 20
    update_type_hash = "0x" + "22" * 32
    hub_topics = {_keccak_topic(signature): signature for signature in HUB_SIGNATURES}
    registered_topic = _keccak_topic("AgentRegistered(uint256,address,string)")
    registration = _decode_hub_log(
        _raw_log(
            hub,
            [registered_topic, _topic_uint(7), _topic_address(oracle), update_type_hash],
        ),
        hub_address=hub,
        signatures_by_topic=hub_topics,
    )
    assert registration["agent_id"] == 7
    assert registration["risk_oracle"] == oracle
    assert registration["update_type_hash"] == update_type_hash

    proposal_topic = _keccak_topic(RISK_ORACLE_SIGNATURE)
    proposal = _decode_proposal_log(
        _raw_log(
            oracle,
            [proposal_topic, update_type_hash, _topic_uint(9), _topic_address(market)],
            _parameter_data(b"ref", b"\x09", b"\x08", 100, b""),
        ),
        oracle_addresses={oracle},
        expected_topic=proposal_topic,
    )
    assert proposal["update_id"] == 9
    assert proposal["market"] == market
    assert proposal["new_value"] == "0x09"


def test_rejects_noncanonical_indexed_values_and_dynamic_padding() -> None:
    with pytest.raises(ValueError, match="indexed bool"):
        bool_from_topic("0x" + f"{2:064x}")
    with pytest.raises(ValueError, match="padding"):
        address_from_topic("0x01" + "00" * 31)

    malformed = bytearray.fromhex(_parameter_data(b"x", b"y", b"z", 1, b"q")[2:])
    malformed[-1] = 1
    with pytest.raises(ValueError, match="padding"):
        decode_parameter_updated_data("0x" + malformed.hex())


def test_action_ledger_distinguishes_injected_overwritten_and_expired() -> None:
    hub_events = [
        _event(
            "AgentRegistered",
            1,
            1,
            agent_id=0,
            risk_oracle="0x" + "11" * 20,
            update_type_hash="0x" + "22" * 32,
        ),
        _event("AgentEnabledSet", 1, 1, agent_id=0, enabled=True, log_index=1),
        _event("ExpirationPeriodSet", 1, 1, agent_id=0, expiration_period=50, log_index=2),
        _event("MinimumDelaySet", 1, 1, agent_id=0, minimum_delay=100, log_index=3),
        _injection(12, 120, 1, "0x01"),
        _injection(23, 230, 2, "0x02"),
    ]
    proposals = [
        _proposal(10, 100, 1, "0x01"),
        _proposal(20, 200, 2, "0x02"),
        _proposal(24, 240, 3, "0x03"),
        _proposal(25, 250, 4, "0x04"),
    ]
    ledger = build_action_ledger(hub_events, proposals, end_timestamp=400)

    assert [row["terminal_class"] for row in ledger] == [
        "injected",
        "injected",
        "overwritten_uninjected",
        "expired_uninjected",
    ]
    assert ledger[1]["delay_exposed"] is True
    assert ledger[1]["minimum_delay_score"]["margin_seconds"] == -20
    assert ledger[2]["delay_exposed"] is True
    assert ledger[3]["resolution_timestamp"] == 301


def _identified_proposal(
    block: int,
    timestamp: int,
    update_id: int,
    value: str,
    *,
    update_type_hash: str = "0x" + "22" * 32,
    market: str = "0x" + "33" * 20,
) -> dict[str, Any]:
    return {
        **_proposal(block, timestamp, update_id, value),
        "block_hash": "0x" + f"{block:064x}",
        "transaction_hash": "0x" + f"{update_id:064x}",
        "update_type_hash": update_type_hash,
        "market": market,
    }


def _initialized_agent(
    *,
    agent_id: int,
    block: int,
    oracle: str = "0x" + "11" * 20,
    update_type_hash: str = "0x" + "22" * 32,
) -> list[dict[str, Any]]:
    return [
        _event(
            "AgentRegistered",
            block,
            block,
            agent_id=agent_id,
            risk_oracle=oracle,
            update_type_hash=update_type_hash,
        ),
        _event(
            "AgentAddressSet",
            block,
            block,
            agent_id=agent_id,
            agent_address="0x" + f"{agent_id + 10:040x}",
            log_index=1,
        ),
        _event("AgentEnabledSet", block, block, agent_id=agent_id, enabled=True, log_index=2),
        _event(
            "ExpirationPeriodSet",
            block,
            block,
            agent_id=agent_id,
            expiration_period=50,
            log_index=3,
        ),
        _event(
            "MinimumDelaySet",
            block,
            block,
            agent_id=agent_id,
            minimum_delay=100,
            log_index=4,
        ),
    ]


def test_holdout_ledger_excludes_only_pre_activation_rows() -> None:
    hub_events = [
        *_initialized_agent(agent_id=0, block=10),
        _injection(30, 130, 2, "0x02"),
    ]
    proposals = [
        _identified_proposal(5, 5, 1, "0x01"),
        _identified_proposal(20, 100, 2, "0x02"),
    ]

    result = build_holdout_chain_ledger(
        hub_events,
        proposals,
        chain_id=10,
        chain_name="optimism",
        expected_risk_oracle="0x" + "11" * 20,
        end_timestamp=500,
    )

    assert len(result["exclusions"]) == 1
    assert result["exclusions"][0]["exclusion_reason"] == "pre_registration"
    assert len(result["eligible"]) == 1
    assert result["eligible"][0]["source_unambiguous"] is True
    assert result["eligible"][0]["terminal_class"] == "injected"
    assert result["eligible"][0]["chain_id"] == 10


def test_holdout_ledger_keeps_post_activation_source_ambiguity_in_denominator() -> None:
    hub_events = [
        *_initialized_agent(agent_id=0, block=1),
        *_initialized_agent(agent_id=1, block=2),
    ]
    proposal = _identified_proposal(10, 100, 7, "0x07")

    result = build_holdout_chain_ledger(
        hub_events,
        [proposal],
        chain_id=137,
        chain_name="polygon",
        expected_risk_oracle="0x" + "11" * 20,
        end_timestamp=500,
    )

    assert result["exclusions"] == []
    assert len(result["eligible"]) == 1
    assert result["eligible"][0]["source_unambiguous"] is False
    assert result["eligible"][0]["terminal_class"] == "unmatched_or_ambiguous"
    assert result["eligible"][0]["ambiguity_reason"] == ("multiple_initialized_source_registrations")


def test_holdout_batching_uses_connected_timestamp_components() -> None:
    rows = [
        {**_identified_proposal(1, 100, 1, "0x01"), "chain_id": 10},
        {**_identified_proposal(2, 220, 2, "0x02"), "chain_id": 137},
        {**_identified_proposal(3, 341, 3, "0x03"), "chain_id": 42161},
    ]

    forward = assign_action_batches(rows, maximum_adjacent_gap_seconds=120)
    reverse = assign_action_batches(list(reversed(rows)), maximum_adjacent_gap_seconds=120)

    assert forward[0]["action_batch_id"] == forward[1]["action_batch_id"]
    assert forward[1]["action_batch_id"] != forward[2]["action_batch_id"]
    assert [row["action_batch_id"] for row in forward] == [row["action_batch_id"] for row in reverse]
    assert [row["action_batch_size"] for row in forward] == [2, 2, 1]


def test_holdout_support_requires_two_chain_specific_row_and_batch_boundaries() -> None:
    ledger: list[dict[str, Any]] = []
    for chain_index, chain_id in enumerate([10, 137]):
        for index in range(20):
            margin = -10 if index < 10 else 10
            ledger.append(
                {
                    "chain_id": chain_id,
                    "chain_name": f"chain-{chain_id}",
                    "agent_id": chain_index,
                    "market": "0x" + f"{index + 1:040x}",
                    "update_type_hash": "0x" + f"{chain_index + 1:064x}",
                    "source_unambiguous": True,
                    "terminal_class": "injected",
                    "delay_exposed": margin < 0,
                    "action_batch_id": f"batch-{chain_id}-{index}",
                    "minimum_delay_score": {
                        "boundary_id": f"boundary-{chain_id}",
                        "chain_id": chain_id,
                        "chain_name": f"chain-{chain_id}",
                        "agent_id": chain_index,
                        "minimum_delay_seconds": 100,
                        "margin_seconds": margin,
                    },
                }
            )
    boundary_rules = {
        "row_level_minimum_scores": 20,
        "row_level_minimum_each_side": 5,
        "neighborhood_fraction": 0.25,
        "row_level_minimum_near_each_side": 5,
        "batch_level_minimum_scores": 10,
        "batch_level_minimum_each_side": 3,
        "batch_level_minimum_near_each_side": 3,
        "exact_row_bunching_minimum_count": 5,
        "exact_batch_bunching_minimum_count": 3,
        "exact_bunching_minimum_fraction": 0.5,
        "minimum_qualifying_boundaries": 2,
        "minimum_chains_with_qualifying_boundary": 2,
    }
    thresholds = {
        "minimum_eligible_proposals": 30,
        "minimum_exact_injections": 20,
        "minimum_update_types": 2,
        "minimum_chain_market_pairs": 5,
        "minimum_represented_chain_agents": 2,
        "minimum_represented_chains": 2,
        "minimum_proposal_batches": 10,
        "minimum_resolved_non_immediate_proposals": 10,
        "minimum_resolved_non_immediate_batches": 5,
        "minimum_terminal_classification_rate": 0.9,
    }

    boundaries = summarize_holdout_delay_boundaries(ledger, boundary_rules)
    support = assess_holdout_action_support(
        ledger,
        [],
        thresholds=thresholds,
        boundary_rules=boundary_rules,
    )

    assert len(boundaries) == 2
    assert all(boundary["qualifies"] for boundary in boundaries)
    assert support["qualifying_boundary_count"] == 2
    assert support["qualifying_boundary_chain_count"] == 2
    assert support["passed"] is True


def test_delay_boundary_requires_both_local_sides_and_rejects_bunching() -> None:
    ledger: list[dict[str, Any]] = []
    for margin in [-20, -15, -10, -5, -1, 1, 5, 10, 15, 20] * 2:
        ledger.append(
            {
                "minimum_delay_score": {
                    "boundary_id": "agent_0_delay_100s",
                    "minimum_delay_seconds": 100,
                    "margin_seconds": margin,
                }
            }
        )
    summary = summarize_delay_boundaries(
        ledger,
        minimum_scores=20,
        minimum_each_side=5,
        neighborhood_fraction=0.25,
        minimum_near_each_side=5,
        bunching_minimum_count=5,
        bunching_minimum_fraction=0.5,
    )[0]
    assert summary["qualifies"] is True

    for _ in range(20):
        ledger.append(
            {
                "minimum_delay_score": {
                    "boundary_id": "agent_0_delay_100s",
                    "minimum_delay_seconds": 100,
                    "margin_seconds": 0,
                }
            }
        )
    bunched = summarize_delay_boundaries(
        ledger,
        minimum_scores=20,
        minimum_each_side=5,
        neighborhood_fraction=0.25,
        minimum_near_each_side=5,
        bunching_minimum_count=5,
        bunching_minimum_fraction=0.5,
    )[0]
    assert bunched["exact_boundary_bunching"] is True
    assert bunched["qualifies"] is False


def test_decoded_checkpoint_round_trip_is_identity_bound(tmp_path: Path) -> None:
    path = tmp_path / "d0.json"
    identity = {
        "repository_sha": "a" * 40,
        "config_sha256": "b" * 64,
        "formal_rpc": "https://example.test",
    }
    state = {
        "completed_through": {"hub": 12, "range": 9, "proposals": 9},
        "events": {
            "hub": [{"event_name": "AgentRegistered"}],
            "range": [],
            "proposals": [],
        },
        "block_headers": {"12": {"number": 12, "hash": "0x" + "aa" * 32}},
    }
    _write_checkpoint(path, identity=identity, state=state)
    loaded, resumed = _load_checkpoint(path, identity=identity, from_block=10)
    assert resumed is True
    assert loaded == state
    with pytest.raises(RuntimeError, match="identity"):
        _load_checkpoint(path, identity={**identity, "formal_rpc": "changed"}, from_block=10)


def test_log_queries_partition_blocks_and_allowed_topics(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[int, int, tuple[str, ...]]] = []

    def fake_get_logs(
        client: Any,
        *,
        addresses: Any,
        topics: Any,
        start_block: int,
        end_block_inclusive: int,
        remaining_split_depth: int,
        split_topics_first: bool,
    ) -> list[dict[str, Any]]:
        del client, addresses, remaining_split_depth
        assert split_topics_first is True
        calls.append((start_block, end_block_inclusive, tuple(topics)))
        return []

    monkeypatch.setattr(guardrail_runner, "_get_logs_with_split", fake_get_logs)
    topics = ["0x" + f"{index:064x}" for index in range(10)]
    assert (
        guardrail_runner._query_logs(
            object(),
            addresses=["0x" + "11" * 20],
            topics=topics,
            from_block=10,
            to_block=19,
            maximum_span=5,
            maximum_topics_per_query=4,
        )
        == []
    )
    assert calls == [
        (10, 14, tuple(topics[:4])),
        (10, 14, tuple(topics[4:8])),
        (10, 14, tuple(topics[8:])),
        (15, 19, tuple(topics[:4])),
        (15, 19, tuple(topics[4:8])),
        (15, 19, tuple(topics[8:])),
    ]
