from __future__ import annotations

import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from ecomd.data.liquity_agentic_queue import (
    decode_support_log,
    log_identity,
    summarize_agentic_queue_support,
)
from scripts import audit_liquity_agentic_queue_d0 as runner

TM = "0x" + "11" * 20
ARM_WETH = "0x" + "22" * 20
ARM_WSTETH = "0x" + "33" * 20
TOPICS = {
    "TroveOperation": "0x962110f281c1213763cd97a546b337b3cbfd25a31ea9723e9d8b7376ba45da1a",
    "BatchedTroveUpdated": "0x6464838e073667756f10746b26734b60870fdcad31d7861c6e5603430bccac61",
    "BatchUpdated": "0xecf6daab6f1facdfdd8dfe32b525744d8a7a940824dd52e2b53c24028ee5faa0",
    "Redemption": "0x84ec8e1674d62e3a8ff294b1a7f53527d2d10291765fadf94e0ce431b2334334",
}
TROVE_OPERATIONS = {
    0: "open_trove",
    1: "close_trove",
    2: "adjust_trove",
    3: "adjust_trove_interest_rate",
    4: "apply_pending_debt",
    5: "liquidate",
    6: "redeem_collateral",
    7: "open_trove_and_join_batch",
    8: "set_interest_batch_manager",
    9: "remove_from_batch",
}
BATCH_OPERATIONS = {
    0: "register_batch_manager",
    1: "lower_batch_manager_annual_fee",
    2: "set_batch_manager_annual_interest_rate",
    3: "apply_batch_interest_and_fee",
    4: "join_batch",
    5: "exit_batch",
    6: "trove_change",
}


def _word(value: int) -> bytes:
    return value.to_bytes(32, "big")


def _address_word(address: str) -> bytes:
    return b"\x00" * 12 + bytes.fromhex(address[2:])


def _topic(value: int) -> str:
    return "0x" + f"{value:064x}"


def _address_topic(address: str) -> str:
    return "0x" + "0" * 24 + address[2:]


def _raw_log(event_name: str, topics: list[str], words: list[bytes]) -> dict[str, Any]:
    return {
        "address": TM,
        "topics": [TOPICS[event_name], *topics],
        "data": "0x" + b"".join(words).hex(),
        "blockNumber": "0xa",
        "blockHash": "0x" + "aa" * 32,
        "transactionHash": "0x" + "bb" * 32,
        "transactionIndex": "0x1",
        "logIndex": "0x2",
        "removed": False,
    }


def _decode(raw: dict[str, Any]) -> dict[str, Any]:
    return decode_support_log(
        raw,
        branches_by_trove_manager={TM: "WETH"},
        signatures_by_topic={topic: name for name, topic in TOPICS.items()},
        trove_operations_by_code=TROVE_OPERATIONS,
        batch_operations_by_code=BATCH_OPERATIONS,
        from_block=1,
        to_block=20,
    )


def test_decodes_only_frozen_support_fields() -> None:
    trove = _decode(_raw_log("TroveOperation", [_topic(7)], [_word(3), *[_word(99)] * 6]))
    assert trove["trove_id"] == _topic(7)
    assert trove["operation"] == 3
    assert trove["operation_name"] == "adjust_trove_interest_rate"

    batched = _decode(
        _raw_log(
            "BatchedTroveUpdated",
            [_topic(8)],
            [_address_word(ARM_WETH), *[_word(88)] * 5],
        )
    )
    assert batched["interest_batch_manager"] == ARM_WETH

    batch = _decode(
        _raw_log(
            "BatchUpdated",
            [_address_topic(ARM_WETH)],
            [_word(2), *[_word(77)] * 6],
        )
    )
    assert batch["interest_batch_manager"] == ARM_WETH
    assert batch["operation"] == 2

    redemption = _decode(_raw_log("Redemption", [], [_word(66)] * 6))
    assert redemption["event_name"] == "Redemption"
    for event in (trove, batched, batch, redemption):
        serialized_keys = " ".join(event)
        assert "debt" not in serialized_keys
        assert "coll" not in serialized_keys
        assert "rate" not in serialized_keys
        assert "price" not in serialized_keys
        assert "data" not in serialized_keys


def test_rejects_malformed_abi_unknown_operations_and_removed_logs() -> None:
    short = _raw_log("Redemption", [], [_word(0)] * 5)
    with pytest.raises(ValueError, match="expected 6"):
        _decode(short)

    unknown = _raw_log("TroveOperation", [_topic(1)], [_word(10), *[_word(0)] * 6])
    with pytest.raises(ValueError, match="unknown TroveOperation"):
        _decode(unknown)

    bad_padding = bytearray(_address_word(ARM_WETH))
    bad_padding[0] = 1
    malformed_address = _raw_log(
        "BatchedTroveUpdated",
        [_topic(1)],
        [bytes(bad_padding), *[_word(0)] * 5],
    )
    with pytest.raises(ValueError, match="padding"):
        _decode(malformed_address)

    removed = _raw_log("Redemption", [], [_word(0)] * 6)
    removed["removed"] = True
    with pytest.raises(ValueError, match="not removed"):
        _decode(removed)


def test_log_identity_uses_chain_identity_not_outcome_data() -> None:
    event = _decode(_raw_log("Redemption", [], [_word(1)] * 6))
    assert log_identity(event) == (
        "0x" + "aa" * 32,
        "0x" + "bb" * 32,
        2,
        TM,
        TOPICS["Redemption"],
    )


def _event(event_name: str, branch: str, **fields: Any) -> dict[str, Any]:
    return {
        "event_name": event_name,
        "branch": branch,
        "block_number": 1,
        "block_hash": "0x" + "aa" * 32,
        "transaction_hash": "0x" + f"{fields.pop('tx', 1):064x}",
        "transaction_index": 0,
        "log_index": fields.pop("log_index", 0),
        "contract_address": TM,
        "topic0": TOPICS[event_name],
        **fields,
    }


def _thresholds() -> dict[str, int | float]:
    return {
        "minimum_unique_opened_troves": 3,
        "minimum_unique_ever_batched_troves": 2,
        "minimum_unique_official_arm_troves": 2,
        "minimum_official_arm_troves_each_qualifying_branch": 1,
        "minimum_official_arm_trove_branches": 2,
        "minimum_registered_batch_managers": 2,
        "minimum_distinct_batch_managers_with_two_rate_updates": 2,
        "minimum_official_arm_rate_updates": 4,
        "minimum_official_arm_rate_updates_each_qualifying_branch": 2,
        "minimum_official_arm_update_branches": 2,
        "minimum_manual_interest_rate_adjustments": 2,
        "minimum_unique_manual_interest_rate_troves": 2,
        "minimum_redemption_transactions": 2,
        "minimum_redemption_utc_dates": 1,
        "minimum_redemption_branches": 2,
        "minimum_redemption_proximal_official_arm_updates": 4,
        "minimum_proximal_update_utc_dates": 1,
        "minimum_proximal_update_branches": 2,
        "minimum_event_classification_rate": 1.0,
    }


def test_support_gate_counts_human_agent_and_same_branch_proximity() -> None:
    events = [
        _event("TroveOperation", "WETH", trove_id=_topic(1), operation=0, tx=1),
        _event("TroveOperation", "WETH", trove_id=_topic(2), operation=0, tx=2),
        _event("TroveOperation", "wstETH", trove_id=_topic(3), operation=7, tx=3),
        _event("TroveOperation", "WETH", trove_id=_topic(1), operation=3, tx=4),
        _event("TroveOperation", "wstETH", trove_id=_topic(3), operation=3, tx=5),
        _event(
            "BatchedTroveUpdated",
            "WETH",
            trove_id=_topic(2),
            interest_batch_manager=ARM_WETH,
            tx=6,
        ),
        _event(
            "BatchedTroveUpdated",
            "wstETH",
            trove_id=_topic(3),
            interest_batch_manager=ARM_WSTETH,
            tx=7,
        ),
        _event(
            "BatchUpdated",
            "WETH",
            interest_batch_manager=ARM_WETH,
            operation=0,
            tx=8,
        ),
        _event(
            "BatchUpdated",
            "wstETH",
            interest_batch_manager=ARM_WSTETH,
            operation=0,
            tx=9,
        ),
        _event(
            "BatchUpdated",
            "WETH",
            interest_batch_manager=ARM_WETH,
            operation=2,
            block_timestamp=1_000,
            tx=10,
        ),
        _event(
            "BatchUpdated",
            "WETH",
            interest_batch_manager=ARM_WETH,
            operation=2,
            block_timestamp=1_020,
            tx=11,
        ),
        _event(
            "BatchUpdated",
            "wstETH",
            interest_batch_manager=ARM_WSTETH,
            operation=2,
            block_timestamp=2_000,
            tx=12,
        ),
        _event(
            "BatchUpdated",
            "wstETH",
            interest_batch_manager=ARM_WSTETH,
            operation=2,
            block_timestamp=2_020,
            tx=13,
        ),
        _event("Redemption", "WETH", block_timestamp=1_050, tx=14),
        _event("Redemption", "wstETH", block_timestamp=2_050, tx=15),
    ]
    result = summarize_agentic_queue_support(
        events,
        official_arms_by_branch={"WETH": ARM_WETH, "wstETH": ARM_WSTETH},
        thresholds=_thresholds(),
        redemption_proximity_seconds=100,
        raw_event_count=len(events),
    )
    assert result["passed"] is True
    assert result["metrics"]["redemption_proximal_official_arm_updates"] == 4
    assert result["metrics"]["distinct_batch_managers_with_two_rate_updates"] == 2
    assert result["by_branch"]["unique_official_arm_troves"] == {
        "WETH": 1,
        "wstETH": 1,
    }
    assert result["contains_numerical_protocol_outcomes"] is False


def test_support_gate_fails_without_frozen_sample_size() -> None:
    thresholds = _thresholds()
    thresholds["minimum_unique_opened_troves"] = 4
    events = [
        _event("TroveOperation", "WETH", trove_id=_topic(1), operation=0),
    ]
    result = summarize_agentic_queue_support(
        events,
        official_arms_by_branch={"WETH": ARM_WETH},
        thresholds=thresholds,
        redemption_proximity_seconds=100,
        raw_event_count=1,
    )
    assert result["passed"] is False
    failed = {check["name"] for check in result["checks"] if not check["passed"]}
    assert "unique_opened_troves" in failed


def test_runner_queries_each_trove_manager_as_a_single_address(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[tuple[str, ...]] = []

    def fake_get_logs(
        client: object,
        *,
        addresses: list[str],
        topics: list[str],
        start_block: int,
        end_block_inclusive: int,
        remaining_split_depth: int,
        split_topics_first: bool,
    ) -> list[dict[str, Any]]:
        del client, topics, start_block, end_block_inclusive
        del remaining_split_depth, split_topics_first
        observed.append(tuple(addresses))
        return []

    monkeypatch.setattr(runner, "_get_logs_with_split", fake_get_logs)
    runner._query_logs(  # type: ignore[arg-type]
        object(),
        addresses=[TM, "0x" + "44" * 20],
        topics=list(TOPICS.values()),
        from_block=1,
        to_block=20,
        maximum_span=10,
        label="test",
    )
    assert observed == [(TM,), ("0x" + "44" * 20,), (TM,), ("0x" + "44" * 20,)]


def test_runner_can_query_replica_addresses_together(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: list[tuple[str, ...]] = []

    def fake_get_logs(
        client: object,
        *,
        addresses: list[str],
        topics: list[str],
        start_block: int,
        end_block_inclusive: int,
        remaining_split_depth: int,
        split_topics_first: bool,
    ) -> list[dict[str, Any]]:
        del client, topics, start_block, end_block_inclusive
        del remaining_split_depth, split_topics_first
        observed.append(tuple(addresses))
        return []

    other = "0x" + "44" * 20
    monkeypatch.setattr(runner, "_get_logs_with_split", fake_get_logs)
    runner._query_logs(  # type: ignore[arg-type]
        object(),
        addresses=[TM, other],
        topics=list(TOPICS.values()),
        from_block=1,
        to_block=20,
        maximum_span=10,
        label="test",
        addresses_together=True,
    )
    assert observed == [(TM, other), (TM, other)]


def test_replica_checkpoint_is_bound_tamper_evident_and_resumable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    checkpoint = tmp_path / "replica.json"
    addresses = [TM, "0x" + "44" * 20]
    topics = list(TOPICS.values())
    identity = {
        "config_path": "configs/test.yaml",
        "config_sha256": "ab" * 32,
        "git_sha": "cd" * 20,
        "replication_rpc": "https://example.invalid",
        "from_block": 1,
        "to_block": 20,
        "maximum_get_logs_span": 10,
        "addresses": addresses,
        "topics": topics,
        "addresses_together": True,
    }
    payload = runner._load_replica_checkpoint(
        checkpoint,
        expected_identity=identity,
        from_block=1,
        to_block=20,
        maximum_span=10,
        addresses=addresses,
        topics=topics,
    )
    payload["completed_chunks"] = [
        {
            "chunk_index": 1,
            "from_block": 1,
            "to_block": 10,
            "event_count": 0,
            "events": [],
            "canonical_log_identity_sha256": runner._identity_digest([]),
        }
    ]
    runner._write_replica_checkpoint(checkpoint, payload)

    observed_ranges: list[tuple[int, int, tuple[str, ...]]] = []

    def fake_get_logs(
        client: object,
        *,
        addresses: list[str],
        topics: list[str],
        start_block: int,
        end_block_inclusive: int,
        remaining_split_depth: int,
        split_topics_first: bool,
    ) -> list[dict[str, Any]]:
        del client, topics, remaining_split_depth, split_topics_first
        observed_ranges.append((start_block, end_block_inclusive, tuple(addresses)))
        return []

    monkeypatch.setattr(runner, "_get_logs_with_split", fake_get_logs)
    events, audit = runner._query_replica_with_checkpoint(  # type: ignore[arg-type]
        object(),
        checkpoint_path=checkpoint,
        checkpoint_identity=identity,
        addresses=addresses,
        topics=topics,
        branches_by_trove_manager={TM: "WETH", addresses[1]: "wstETH"},
        signatures_by_topic={topic: name for name, topic in TOPICS.items()},
        trove_operations_by_code=TROVE_OPERATIONS,
        batch_operations_by_code=BATCH_OPERATIONS,
        from_block=1,
        to_block=20,
        maximum_span=10,
        split_on_exhausted_rate_limit=False,
        maximum_rate_limit_split_depth=0,
    )
    assert events == []
    assert observed_ranges == [(11, 20, tuple(addresses))]
    assert audit["resumed_chunks_at_start"] == 1
    assert audit["completed_chunks"] == 2

    tampered = json.loads(checkpoint.read_text(encoding="utf-8"))
    tampered["completed_chunks"][0]["event_count"] = 1
    checkpoint.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(RuntimeError, match="payload digest"):
        runner._load_replica_checkpoint(
            checkpoint,
            expected_identity=identity,
            from_block=1,
            to_block=20,
            maximum_span=10,
            addresses=addresses,
            topics=topics,
        )


def test_transport_amendment_preserves_every_scientific_section() -> None:
    config_path = Path("configs/empirical_physics/liquity_agentic_queue_d0_v2.yaml").resolve()
    config = runner._load_yaml(config_path)
    audit = runner._validate_freeze_contract(config, config_path=config_path)
    assert audit["is_transport_amendment"] is True
    assert audit["scientific_sections_equal_to_parent"] is True

    tampered = deepcopy(config)
    tampered["pass_thresholds"]["minimum_unique_opened_troves"] = 499
    with pytest.raises(RuntimeError, match="pass_thresholds"):
        runner._validate_freeze_contract(tampered, config_path=config_path)

    tampered = deepcopy(config)
    tampered["transport"]["state_witness_rpc"] = "https://example.invalid"
    with pytest.raises(RuntimeError, match="state witness"):
        runner._validate_freeze_contract(tampered, config_path=config_path)


def test_transport_recovery_v3_preserves_parent_and_scientific_contract() -> None:
    config_path = Path("configs/empirical_physics/liquity_agentic_queue_d0_v3.yaml").resolve()
    config = runner._load_yaml(config_path)
    audit = runner._validate_freeze_contract(config, config_path=config_path)
    assert audit["is_resumable_transport_recovery"] is True
    assert audit["scientific_sections_equal_to_parent"] is True

    tampered = deepcopy(config)
    tampered["pass_thresholds"]["minimum_unique_opened_troves"] = 499
    with pytest.raises(RuntimeError, match="pass_thresholds"):
        runner._validate_freeze_contract(tampered, config_path=config_path)

    tampered = deepcopy(config)
    tampered["transport"]["minimum_request_interval_seconds"] = 0.5
    with pytest.raises(RuntimeError, match="parent transport"):
        runner._validate_freeze_contract(tampered, config_path=config_path)

    tampered = deepcopy(config)
    tampered["transport"]["replication_checkpoint_every_chunks"] = 2
    with pytest.raises(RuntimeError, match="recovery transport"):
        runner._validate_freeze_contract(tampered, config_path=config_path)


def test_rate_limit_recovery_splits_addresses_before_block_range(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[tuple[str, ...], int, int]] = []

    def fake_get_logs(
        client: object,
        *,
        addresses: list[str],
        topics: list[str],
        start_block: int,
        end_block_inclusive: int,
        remaining_split_depth: int,
        split_topics_first: bool,
    ) -> list[dict[str, Any]]:
        del client, topics, remaining_split_depth, split_topics_first
        calls.append((tuple(addresses), start_block, end_block_inclusive))
        if len(addresses) > 1:
            raise runner.RpcError("limited", http_status=429)
        return []

    monkeypatch.setattr(runner, "_get_logs_with_split", fake_get_logs)
    counts: Counter[str] = Counter()
    addresses = [TM, "0x" + "44" * 20, "0x" + "55" * 20]
    result = runner._get_replica_logs_with_rate_limit_split(  # type: ignore[arg-type]
        object(),
        addresses=addresses,
        topics=list(TOPICS.values()),
        start_block=1,
        end_block_inclusive=10,
        remaining_split_depth=4,
        split_counts=counts,
    )
    assert result == []
    assert calls == [
        (tuple(addresses), 1, 10),
        ((addresses[0],), 1, 10),
        ((addresses[1], addresses[2]), 1, 10),
        ((addresses[1],), 1, 10),
        ((addresses[2],), 1, 10),
    ]
    assert counts == {"address": 2}


def test_rate_limit_recovery_bisects_single_address_block_range(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[int, int]] = []

    def fake_get_logs(
        client: object,
        *,
        addresses: list[str],
        topics: list[str],
        start_block: int,
        end_block_inclusive: int,
        remaining_split_depth: int,
        split_topics_first: bool,
    ) -> list[dict[str, Any]]:
        del client, addresses, topics, remaining_split_depth, split_topics_first
        calls.append((start_block, end_block_inclusive))
        if start_block < end_block_inclusive:
            raise runner.RpcError("limited", rpc_code=-32029)
        return []

    monkeypatch.setattr(runner, "_get_logs_with_split", fake_get_logs)
    counts: Counter[str] = Counter()
    result = runner._get_replica_logs_with_rate_limit_split(  # type: ignore[arg-type]
        object(),
        addresses=[TM],
        topics=list(TOPICS.values()),
        start_block=1,
        end_block_inclusive=4,
        remaining_split_depth=4,
        split_counts=counts,
    )
    assert result == []
    assert calls == [(1, 4), (1, 2), (1, 1), (2, 2), (3, 4), (3, 3), (4, 4)]
    assert counts == {"block_range": 3}


def test_weight_aware_transport_recovery_v4_preserves_every_parent_field() -> None:
    config_path = Path("configs/empirical_physics/liquity_agentic_queue_d0_v4.yaml").resolve()
    config = runner._load_yaml(config_path)
    audit = runner._validate_freeze_contract(config, config_path=config_path)
    assert audit["is_weight_aware_transport_recovery"] is True
    assert audit["scientific_sections_equal_to_parent"] is True

    tampered = deepcopy(config)
    tampered["support_window"]["redemption_proximity_seconds"] = 86_399
    with pytest.raises(RuntimeError, match="support_window"):
        runner._validate_freeze_contract(tampered, config_path=config_path)

    tampered = deepcopy(config)
    tampered["transport"]["maximum_get_logs_span"] = 5_000
    with pytest.raises(RuntimeError, match="parent transport"):
        runner._validate_freeze_contract(tampered, config_path=config_path)

    tampered = deepcopy(config)
    tampered["transport"]["replication_minimum_request_interval_seconds"] = 6.0
    with pytest.raises(RuntimeError, match="weight-aware recovery"):
        runner._validate_freeze_contract(tampered, config_path=config_path)
