from __future__ import annotations

from typing import Any

import pytest

from ecomd.data.liquity_agentic_queue import (
    decode_support_log,
    log_identity,
    summarize_agentic_queue_support,
)

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
