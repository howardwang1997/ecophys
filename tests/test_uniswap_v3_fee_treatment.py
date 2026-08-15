from __future__ import annotations

from pathlib import Path

import pytest

from ecomd.research.uniswap_v3_fee_treatment import (
    BATCH_TRIGGER_SELECTOR,
    FEE_UPDATE_TOPIC,
    OWNER_CHANGED_TOPIC,
    SET_FEE_PROTOCOL_TOPIC,
    canonical_json_sha256,
    contract_sha256,
    decode_batch_trigger_calldata,
    parse_batch_treatment,
    summarize_treatment_conformance,
    validate_frozen_contract,
    validate_governance_execution,
)

ADAPTER = "0xf2371551fe3937db7c750f4dfabe5c2fffdcbf5a"
CALLER = "0x2cf8e5b175aa29c1fdf0e9fe572735c78eacce43"
GOVERNOR = "0x408ed6354d4973f66138c91495f2f2fcbd8724c3"
FACTORY = "0x1f98431c8ad98523631ae4a59f267346ea31f984"
OLD_ADAPTER = "0x5e74c9f42eed283bff3744fbd1889d398d40867d"
TX_HASH = "0x" + "1" * 64
GOVERNANCE_TX_HASH = "0x" + "2" * 64
BLOCK_HASH = "0x" + "3" * 64
POOL_A = "0x" + "a" * 40
POOL_B = "0x" + "b" * 40


def _word(value: int) -> str:
    return value.to_bytes(32, "big").hex()


def _address_word(address: str) -> str:
    return "0" * 24 + address[2:].lower()


def _topic_address(address: str) -> str:
    return "0x" + _address_word(address)


def _calldata(pools: list[str]) -> str:
    return (
        BATCH_TRIGGER_SELECTOR
        + _word(32)
        + _word(len(pools))
        + "".join(_address_word(pool) for pool in pools)
    )


def _set_fee_log(pool: str, log_index: int, values: tuple[int, int, int, int]) -> dict[str, object]:
    return {
        "address": pool,
        "topics": [SET_FEE_PROTOCOL_TOPIC],
        "data": "0x" + "".join(_word(value) for value in values),
        "logIndex": hex(log_index),
    }


def _update_log(pool: str, log_index: int, fee_value: int) -> dict[str, object]:
    return {
        "address": ADAPTER,
        "topics": [FEE_UPDATE_TOPIC, _topic_address(CALLER), _topic_address(pool)],
        "data": "0x" + _word(fee_value),
        "logIndex": hex(log_index),
    }


def _transaction() -> dict[str, object]:
    return {
        "hash": TX_HASH,
        "to": ADAPTER,
        "from": CALLER,
        "input": _calldata([POOL_A, POOL_B]),
        "blockNumber": "0x64",
        "blockHash": BLOCK_HASH,
        "transactionIndex": "0x3",
    }


def _receipt() -> dict[str, object]:
    return {
        "transactionHash": TX_HASH,
        "status": "0x1",
        "blockNumber": "0x64",
        "blockHash": BLOCK_HASH,
        "transactionIndex": "0x3",
        "logs": [
            _set_fee_log(POOL_A, 10, (0, 0, 4, 4)),
            _update_log(POOL_A, 11, 0x44),
            _set_fee_log(POOL_B, 12, (6, 6, 6, 6)),
            _update_log(POOL_B, 13, 0x66),
        ],
    }


def test_decode_batch_trigger_calldata_exact_array() -> None:
    assert decode_batch_trigger_calldata(_calldata([POOL_A, POOL_B])) == (POOL_A, POOL_B)
    with pytest.raises(ValueError, match="trailing or missing"):
        decode_batch_trigger_calldata(_calldata([POOL_A]) + _word(1))


def test_parse_batch_pairs_pool_and_adapter_events() -> None:
    result = parse_batch_treatment(
        _transaction(),
        _receipt(),
        adapter_address=ADAPTER,
        expected_tx_hash=TX_HASH,
    )
    assert result["calldata_pool_count"] == 2
    rows = result["rows"]
    assert isinstance(rows, list)
    assert rows[0]["transition"] == "activated_from_zero"
    assert rows[0]["packed_fee_value"] == 0x44
    assert rows[1]["transition"] == "reapplied_same_fee"


def test_parse_batch_rejects_order_or_packed_fee_mismatch() -> None:
    receipt = _receipt()
    logs = receipt["logs"]
    assert isinstance(logs, list)
    logs[1], logs[3] = logs[3], logs[1]
    with pytest.raises(ValueError, match="pool order differs"):
        parse_batch_treatment(
            _transaction(),
            receipt,
            adapter_address=ADAPTER,
            expected_tx_hash=TX_HASH,
        )
    receipt = _receipt()
    logs = receipt["logs"]
    assert isinstance(logs, list)
    update = logs[1]
    assert isinstance(update, dict)
    update["data"] = "0x" + _word(0x66)
    with pytest.raises(ValueError, match="packed fee"):
        parse_batch_treatment(
            _transaction(),
            receipt,
            adapter_address=ADAPTER,
            expected_tx_hash=TX_HASH,
        )


def test_parse_batch_rejects_transaction_receipt_block_hash_mismatch() -> None:
    receipt = _receipt()
    receipt["blockHash"] = "0x" + "4" * 64
    with pytest.raises(ValueError, match="block hashes differ"):
        parse_batch_treatment(
            _transaction(),
            receipt,
            adapter_address=ADAPTER,
            expected_tx_hash=TX_HASH,
        )


def test_validate_governance_execution_uses_owner_event_not_prose() -> None:
    transaction = {
        "hash": GOVERNANCE_TX_HASH,
        "to": GOVERNOR,
        "input": "0xfe0d94c1" + _word(94),
        "blockNumber": "0xc8",
        "blockHash": BLOCK_HASH,
    }
    receipt = {
        "transactionHash": GOVERNANCE_TX_HASH,
        "status": "0x1",
        "blockNumber": "0xc8",
        "blockHash": BLOCK_HASH,
        "logs": [
            {
                "address": FACTORY,
                "topics": [
                    OWNER_CHANGED_TOPIC,
                    _topic_address(OLD_ADAPTER),
                    _topic_address(ADAPTER),
                ],
                "data": "0x",
                "logIndex": "0x1",
            }
        ],
    }
    result = validate_governance_execution(
        transaction,
        receipt,
        governor_address=GOVERNOR,
        proposal_id=94,
        expected_tx_hash=GOVERNANCE_TX_HASH,
        expected_block=200,
        factory_address=FACTORY,
        old_owner=OLD_ADAPTER,
        new_owner=ADAPTER,
    )
    assert result["new_factory_owner"] == ADAPTER


def test_summary_requires_new_treatments_in_both_fee_groups() -> None:
    first = parse_batch_treatment(
        _transaction(),
        _receipt(),
        adapter_address=ADAPTER,
        expected_tx_hash=TX_HASH,
    )
    summary = summarize_treatment_conformance(
        {"proposal_id": 94},
        [first],
        expected_batch_hashes=[TX_HASH],
        expected_batch_size=2,
        minimum_activated_total=1,
        minimum_activated_per_fee_value=1,
    )
    assert summary["pass"] is False
    gates = summary["gates"]
    assert isinstance(gates, dict)
    assert gates["minimum_activated_fee_0x44"] is True
    assert gates["minimum_activated_fee_0x66"] is False


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_repository_frozen_contract_is_valid(version: str) -> None:
    root = Path(__file__).resolve().parents[1]
    import yaml

    contract_path = root / f"data/manifests/uniswap_v3_fee_treatment_conformance_{version}.yaml"
    payload = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    assert validate_frozen_contract(payload) == ()
    hashes = payload["propagation_frame"]["batch_transaction_hashes"]
    assert payload["propagation_frame"]["batch_transaction_hashes_sha256"] == canonical_json_sha256(
        [value.lower() for value in hashes]
    )
    if version == "v2":
        parent = root / payload["transport_repair"]["parent_contract"]
        assert payload["transport_repair"]["parent_contract_sha256"] == contract_sha256(parent)


def test_v2_changes_only_transport_and_bookkeeping_fields() -> None:
    root = Path(__file__).resolve().parents[1]
    import yaml

    v1 = yaml.safe_load(
        (root / "data/manifests/uniswap_v3_fee_treatment_conformance_v1.yaml").read_text(encoding="utf-8")
    )
    v2 = yaml.safe_load(
        (root / "data/manifests/uniswap_v3_fee_treatment_conformance_v2.yaml").read_text(encoding="utf-8")
    )
    for key in ("deployment", "mechanism", "propagation_frame", "reconnaissance_disclosure", "gates"):
        assert v2[key] == v1[key]
    assert v2["access_boundary"] == v1["access_boundary"]
    source_v1 = dict(v1["source"])
    source_v2 = dict(v2["source"])
    assert source_v1.pop("runtime_bytecode_block") == 24599177
    assert source_v2.pop("runtime_bytecode_block") == "latest"
    assert source_v2.pop("runtime_code_query_role") == "provenance_only_not_treatment_clock"
    assert source_v2 == source_v1
