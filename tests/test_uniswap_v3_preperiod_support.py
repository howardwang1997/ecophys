from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ecomd.research.uniswap_v3_preperiod_support import (
    INCREASE_TOPIC,
    MINT_TOPIC,
    TRANSFER_TOPIC,
    build_pool_support_rows,
    canonical_json_sha256,
    deduplicate_pool_events,
    hash_file,
    load_contract,
    load_jsonl,
    normalize_legacy_log,
    normalize_transaction_log,
    pair_sampled_pool_actions,
    resolve_transfer_owners,
    select_hash_stratified_pools,
    select_identity_transactions,
    split_inclusive_interval,
    summarize_preperiod_support,
    validate_frozen_contract,
)

NPM = "0xc36442b4a4522e871399cd717abdd847ab11fe88"
POOL_A = "0x" + "a" * 40
POOL_B = "0x" + "b" * 40
OWNER_A = "0x" + "c" * 40
OWNER_B = "0x" + "d" * 40
TX_HASH = "0x" + "1" * 64


def _topic_address(address: str) -> str:
    return "0x" + "0" * 24 + address[2:]


def _topic_uint(value: int) -> str:
    return "0x" + value.to_bytes(32, "big").hex()


def _legacy_pool_log(*, pool: str = POOL_A, tx_hash: str = TX_HASH, log_index: int = 5) -> dict[str, object]:
    return {
        "address": pool,
        "blockNumber": "0x64",
        "transactionIndex": "0x2",
        "logIndex": hex(log_index),
        "transactionHash": tx_hash,
        "topics": [MINT_TOPIC, _topic_address(NPM), _topic_uint(1), _topic_uint(2)],
        "data": "0x" + "00" * 32,
    }


def _normalized_pool_event() -> dict[str, object]:
    return normalize_legacy_log(
        _legacy_pool_log(),
        event_type="mint",
        expected_address=POOL_A,
        expected_topic0=MINT_TOPIC,
        from_block=90,
        to_block=110,
    )


def test_repository_contract_reproduces_hash_stratified_sample() -> None:
    root = Path(__file__).resolve().parents[1]
    contract_path = root / "data/manifests/uniswap_v3_preperiod_support_v1.yaml"
    contract = load_contract(contract_path)
    parent = contract["parent"]
    assert isinstance(parent, dict)
    treatment_path = root / parent["treatment_ledger"]
    treatment_rows = load_jsonl(treatment_path)
    assert (
        validate_frozen_contract(
            contract,
            treatment_rows,
            treatment_ledger_sha256=hash_file(treatment_path),
        )
        == ()
    )
    selection = contract["selection"]
    assert isinstance(selection, dict)
    observed = select_hash_stratified_pools(
        treatment_rows,
        salt=selection["salt"],
        allowed_fee_values=selection["allowed_packed_fee_values"],
        pools_per_fee_value=selection["pools_per_fee_value"],
    )
    assert observed == selection["pools"]
    assert canonical_json_sha256(observed) == selection["sample_rows_sha256"]

    mutated = deepcopy(contract)
    mutated["access_boundary"]["post_treatment_responses_opened"] = True
    assert "access_boundary.post_treatment_responses_opened must remain false" in validate_frozen_contract(
        mutated,
        treatment_rows,
        treatment_ledger_sha256=hash_file(treatment_path),
    )


def test_interval_split_has_no_gap_or_overlap() -> None:
    assert split_inclusive_interval(10, 15) == ((10, 12), (13, 15))


def test_legacy_log_normalization_extracts_manager_without_amounts() -> None:
    raw = _legacy_pool_log()
    topics = raw["topics"]
    assert isinstance(topics, list)
    topics.append(None)
    event = normalize_legacy_log(
        raw,
        event_type="mint",
        expected_address=POOL_A,
        expected_topic0=MINT_TOPIC,
        from_block=90,
        to_block=110,
    )
    assert event["manager_owner"] == NPM
    assert event["block_number"] == 100
    assert "data" not in event
    assert len(event["data_sha256"]) == 64


def test_deduplication_counts_exact_and_conflicting_repeats() -> None:
    event = _normalized_pool_event()
    conflict = dict(event)
    conflict["data_sha256"] = "f" * 64
    rows, duplicates, conflicts = deduplicate_pool_events([event, event, conflict])
    assert len(rows) == 1
    assert duplicates == 1
    assert conflicts == 1


def test_pool_support_and_identity_transaction_selection() -> None:
    first = _normalized_pool_event()
    second = dict(first)
    second["pool_address"] = POOL_B
    second["transaction_hash"] = "0x" + "2" * 64
    second["log_index"] = 6
    sample = [
        {"pool_address": POOL_A, "packed_fee_value": 68},
        {"pool_address": POOL_B, "packed_fee_value": 102},
    ]
    support = build_pool_support_rows(sample, [first, second], npm_address=NPM)
    assert [row["npm_position_action_share"] for row in support] == [1.0, 1.0]
    selected, eligible = select_identity_transactions(
        [first, second], npm_address=NPM, salt="fixed", maximum_transactions=1
    )
    assert eligible == 2
    assert len(selected) == 1


def test_transaction_log_normalization_allows_anonymous_log() -> None:
    raw = {
        "address": {"hash": POOL_A},
        "block_number": 100,
        "index": 4,
        "transaction_hash": TX_HASH,
        "topics": [],
    }
    assert normalize_transaction_log(raw, expected_tx_hash=TX_HASH)["topics"] == []


def test_pairing_uses_following_npm_token_event() -> None:
    sampled = _normalized_pool_event()
    transaction_logs = [
        {
            "address": POOL_A,
            "block_number": 100,
            "log_index": 5,
            "transaction_hash": TX_HASH,
            "topics": [MINT_TOPIC, _topic_address(NPM)],
        },
        {
            "address": NPM,
            "block_number": 100,
            "log_index": 8,
            "transaction_hash": TX_HASH,
            "topics": [INCREASE_TOPIC, _topic_uint(42)],
        },
    ]
    result = pair_sampled_pool_actions(transaction_logs, [sampled], npm_address=NPM)
    assert result[(POOL_A, 5)] == {"pair_status": "exact", "token_id": 42}


def test_transfer_history_resolves_before_and_after_transaction() -> None:
    transfers = [
        {
            "topics": [
                TRANSFER_TOPIC,
                _topic_address("0x" + "0" * 40),
                _topic_address(OWNER_A),
                _topic_uint(42),
            ],
            "block_number": 90,
            "transaction_index": 1,
            "log_index": 2,
        },
        {
            "topics": [TRANSFER_TOPIC, _topic_address(OWNER_A), _topic_address(OWNER_B), _topic_uint(42)],
            "block_number": 100,
            "transaction_index": 2,
            "log_index": 9,
        },
    ]
    result = resolve_transfer_owners(
        transfers,
        token_id=42,
        action_block=100,
        action_transaction_index=2,
        action_log_index=5,
    )
    assert result["owner_before_action"] == OWNER_A
    assert result["owner_after_transaction"] == OWNER_B


def test_summary_applies_support_and_identity_gates() -> None:
    support = [
        {
            "swap_count": 1,
            "position_action_count": 10,
            "npm_position_action_count": 8,
        }
        for _ in range(16)
    ]
    identity = [{"pair_status": "exact", "owner_after_transaction": OWNER_A} for _ in range(40)]
    result = summarize_preperiod_support(
        support,
        identity,
        expected_pool_count=16,
        eligible_identity_transaction_count=40,
        selected_identity_transaction_count=40,
        maximum_identity_transactions=64,
        duplicate_log_count=0,
        conflicting_log_count=0,
        complete_unsaturated_partitions=True,
        minimum_swap_active_pools=8,
        minimum_position_active_pools=8,
        minimum_position_action_logs=64,
        minimum_npm_position_action_share=0.5,
        minimum_eligible_npm_action_transactions=32,
        minimum_exact_pool_to_token_pair_rate=0.8,
        minimum_owner_after_transaction_resolution_rate=0.95,
    )
    assert result["pass"] is True
    assert result["control_source_status"] == "UNRESOLVED_NOT_PART_OF_U1A"
