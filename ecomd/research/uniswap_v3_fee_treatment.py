"""Exact treatment-ledger checks for the Uniswap v3 protocol-fee expansion."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

import yaml

CONTRACT_SCHEMA_V1 = "ecophys-uniswap-v3-fee-treatment-conformance/v1"
CONTRACT_SCHEMA_V2 = "ecophys-uniswap-v3-fee-treatment-conformance/v2"
RESULT_SCHEMA_VERSION = "ecophys-uniswap-v3-fee-treatment-conformance-result/v1"
FROZEN_STAGE = "frozen_before_old_new_fee_transition_decoding"
BATCH_TRIGGER_SELECTOR = "0x08f4779e"
EXECUTE_SELECTOR = "0xfe0d94c1"
FEE_UPDATE_TOPIC = "0xa38b98e5166edaa11e3ca8a9decd55d5a224db2efb90ec8329d980e46857bcd1"
SET_FEE_PROTOCOL_TOPIC = "0x973d8d92bb299f4af6ce49b52a8adb85ae46b9f214c4c4fc06ac77401237b133"
OWNER_CHANGED_TOPIC = "0xb532073b38c83145e3e5135377a08bf9aab55bc0fd7c1179cd4fb995d2a5159c"
HEX_40 = re.compile(r"0x[0-9a-fA-F]{40}")
HEX_64 = re.compile(r"0x[0-9a-fA-F]{64}")
SHA256 = re.compile(r"[0-9a-f]{64}")
GIT_SHA = re.compile(r"[0-9a-f]{40}")


def canonical_json_sha256(payload: object) -> str:
    """Hash a JSON-safe value using the project's stable JSON representation."""

    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_contract(path: Path) -> dict[str, object]:
    """Load one frozen Uniswap treatment contract."""

    payload: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("treatment contract root must be a mapping")
    return cast(dict[str, object], payload)


def contract_sha256(path: Path) -> str:
    """Hash the exact frozen contract bytes."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_address(value: object, *, path: str = "address") -> str:
    """Validate and normalize one EVM address."""

    if not isinstance(value, str) or HEX_40.fullmatch(value) is None:
        raise ValueError(f"{path} must be a 20-byte hexadecimal address")
    return value.lower()


def normalize_hash(value: object, *, path: str = "hash") -> str:
    """Validate and normalize one 32-byte EVM hash."""

    if not isinstance(value, str) or HEX_64.fullmatch(value) is None:
        raise ValueError(f"{path} must be a 32-byte hexadecimal hash")
    return value.lower()


def decode_quantity(value: object, *, path: str) -> int:
    """Decode one canonical JSON-RPC hexadecimal quantity."""

    if not isinstance(value, str) or re.fullmatch(r"0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)", value) is None:
        raise ValueError(f"{path} must be a canonical JSON-RPC quantity")
    return int(value, 16)


def _hex_payload(value: object, *, path: str) -> bytes:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"{path} must be 0x-prefixed hex")
    body = value[2:]
    if len(body) % 2 or re.fullmatch(r"[0-9a-fA-F]*", body) is None:
        raise ValueError(f"{path} must contain complete hexadecimal bytes")
    return bytes.fromhex(body)


def _word_uint(word: bytes, *, path: str) -> int:
    if len(word) != 32:
        raise ValueError(f"{path} must be one ABI word")
    return int.from_bytes(word, "big")


def _word_address(word: bytes, *, path: str) -> str:
    if len(word) != 32 or any(word[:12]):
        raise ValueError(f"{path} must be a canonical ABI address word")
    return "0x" + word[12:].hex()


def address_from_topic(value: object, *, path: str) -> str:
    """Decode an indexed address topic."""

    return _word_address(_hex_payload(value, path=path), path=path)


def decode_batch_trigger_calldata(value: object) -> tuple[str, ...]:
    """Decode the exact ``batchTriggerFeeUpdateByPool(address[])`` call."""

    payload = _hex_payload(value, path="transaction.input")
    selector = bytes.fromhex(BATCH_TRIGGER_SELECTOR[2:])
    if payload[:4] != selector:
        raise ValueError("transaction selector is not batchTriggerFeeUpdateByPool(address[])")
    body = payload[4:]
    if len(body) < 64 or len(body) % 32:
        raise ValueError("batch calldata has invalid ABI length")
    offset = _word_uint(body[:32], path="transaction.input.offset")
    if offset != 32:
        raise ValueError("batch calldata address-array offset must be 32")
    count = _word_uint(body[32:64], path="transaction.input.length")
    if len(body) != 64 + 32 * count:
        raise ValueError("batch calldata has trailing or missing address words")
    return tuple(
        _word_address(body[64 + index * 32 : 96 + index * 32], path=f"pool[{index}]")
        for index in range(count)
    )


def decode_fee_update_data(value: object) -> int:
    """Decode the non-indexed packed fee from ``FeeUpdateTriggered``."""

    fee = _word_uint(_hex_payload(value, path="FeeUpdateTriggered.data"), path="feeValue")
    if fee > 255:
        raise ValueError("FeeUpdateTriggered feeValue exceeds uint8")
    return fee


def decode_set_fee_protocol_data(value: object) -> tuple[int, int, int, int]:
    """Decode old/new token-side denominators from ``SetFeeProtocol``."""

    payload = _hex_payload(value, path="SetFeeProtocol.data")
    if len(payload) != 128:
        raise ValueError("SetFeeProtocol data must contain four ABI words")
    values = tuple(
        _word_uint(payload[index * 32 : (index + 1) * 32], path=f"fee[{index}]") for index in range(4)
    )
    if any(value_ > 255 for value_ in values):
        raise ValueError("SetFeeProtocol value exceeds uint8")
    return cast(tuple[int, int, int, int], values)


def _mapping(value: object, *, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be a mapping")
    return cast(Mapping[str, object], value)


def _sequence(value: object, *, path: str) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{path} must be a sequence")
    return cast(Sequence[object], value)


def _topics(log: Mapping[str, object], *, path: str) -> tuple[str, ...]:
    topics = _sequence(log.get("topics"), path=f"{path}.topics")
    normalized = tuple(normalize_hash(topic, path=f"{path}.topics") for topic in topics)
    if not normalized:
        raise ValueError(f"{path}.topics cannot be empty")
    return normalized


def _transition_label(old0: int, old1: int, new0: int, new1: int) -> str:
    if old0 == 0 and old1 == 0 and (new0 != 0 or new1 != 0):
        return "activated_from_zero"
    if old0 == new0 and old1 == new1:
        return "reapplied_same_fee"
    if new0 == 0 and new1 == 0:
        return "disabled_to_zero"
    return "changed_nonzero_fee"


def parse_batch_treatment(
    transaction: Mapping[str, object],
    receipt: Mapping[str, object],
    *,
    adapter_address: str,
    expected_tx_hash: str,
) -> dict[str, object]:
    """Validate one batch transaction and build its exact pool-treatment rows."""

    adapter = normalize_address(adapter_address, path="adapter_address")
    expected_hash = normalize_hash(expected_tx_hash, path="expected_tx_hash")
    transaction_hash = normalize_hash(transaction.get("hash"), path="transaction.hash")
    receipt_hash = normalize_hash(receipt.get("transactionHash"), path="receipt.transactionHash")
    if transaction_hash != expected_hash or receipt_hash != expected_hash:
        raise ValueError("transaction/receipt hash does not match the frozen batch hash")
    if normalize_address(transaction.get("to"), path="transaction.to") != adapter:
        raise ValueError("batch transaction is not addressed directly to the frozen adapter")
    caller = normalize_address(transaction.get("from"), path="transaction.from")
    if decode_quantity(receipt.get("status"), path="receipt.status") != 1:
        raise ValueError("batch receipt is not successful")
    transaction_block = decode_quantity(transaction.get("blockNumber"), path="transaction.blockNumber")
    receipt_block = decode_quantity(receipt.get("blockNumber"), path="receipt.blockNumber")
    if transaction_block != receipt_block:
        raise ValueError("transaction and receipt block numbers differ")
    transaction_block_hash = normalize_hash(transaction.get("blockHash"), path="transaction.blockHash")
    receipt_block_hash = normalize_hash(receipt.get("blockHash"), path="receipt.blockHash")
    if transaction_block_hash != receipt_block_hash:
        raise ValueError("transaction and receipt block hashes differ")
    transaction_index = decode_quantity(
        transaction.get("transactionIndex"), path="transaction.transactionIndex"
    )
    if transaction_index != decode_quantity(receipt.get("transactionIndex"), path="receipt.transactionIndex"):
        raise ValueError("transaction and receipt indexes differ")

    calldata_pools = decode_batch_trigger_calldata(transaction.get("input"))
    if len(set(calldata_pools)) != len(calldata_pools):
        raise ValueError("batch calldata contains duplicate pools")
    logs = _sequence(receipt.get("logs"), path="receipt.logs")
    updates: dict[str, tuple[int, str, int]] = {}
    update_order: list[str] = []
    pool_events: dict[str, tuple[int, tuple[int, int, int, int]]] = {}
    pool_event_order: list[str] = []
    for position, raw_log in enumerate(logs):
        log = _mapping(raw_log, path=f"receipt.logs[{position}]")
        address = normalize_address(log.get("address"), path=f"receipt.logs[{position}].address")
        topics = _topics(log, path=f"receipt.logs[{position}]")
        log_index = decode_quantity(log.get("logIndex"), path=f"receipt.logs[{position}].logIndex")
        if address == adapter and topics[0] == FEE_UPDATE_TOPIC:
            if len(topics) != 3:
                raise ValueError("FeeUpdateTriggered must contain caller and pool topics")
            event_caller = address_from_topic(topics[1], path="FeeUpdateTriggered.caller")
            pool = address_from_topic(topics[2], path="FeeUpdateTriggered.pool")
            if event_caller != caller:
                raise ValueError("FeeUpdateTriggered caller differs from transaction sender")
            if pool in updates:
                raise ValueError("duplicate FeeUpdateTriggered event for one pool")
            updates[pool] = (log_index, event_caller, decode_fee_update_data(log.get("data")))
            update_order.append(pool)
        elif topics[0] == SET_FEE_PROTOCOL_TOPIC:
            if len(topics) != 1:
                raise ValueError("SetFeeProtocol should not contain indexed arguments")
            if address in pool_events:
                raise ValueError("duplicate SetFeeProtocol event for one pool")
            pool_events[address] = (log_index, decode_set_fee_protocol_data(log.get("data")))
            pool_event_order.append(address)

    if tuple(update_order) != calldata_pools:
        raise ValueError("FeeUpdateTriggered pool order differs from calldata")
    if tuple(pool_event_order) != calldata_pools:
        raise ValueError("SetFeeProtocol pool order differs from calldata")
    if set(updates) != set(pool_events):
        raise ValueError("adapter and pool event sets differ")

    rows: list[dict[str, object]] = []
    for calldata_index, pool in enumerate(calldata_pools):
        update_log_index, event_caller, fee_value = updates[pool]
        pool_log_index, values = pool_events[pool]
        old0, old1, new0, new1 = values
        if new0 != fee_value % 16 or new1 != fee_value >> 4:
            raise ValueError("adapter packed fee does not match pool new-fee event")
        if pool_log_index >= update_log_index:
            raise ValueError("pool SetFeeProtocol must precede adapter FeeUpdateTriggered")
        rows.append(
            {
                "transaction_hash": transaction_hash,
                "block_number": transaction_block,
                "transaction_index": transaction_index,
                "calldata_index": calldata_index,
                "pool_address": pool,
                "caller_address": event_caller,
                "pool_event_log_index": pool_log_index,
                "adapter_event_log_index": update_log_index,
                "old_fee_protocol0": old0,
                "old_fee_protocol1": old1,
                "new_fee_protocol0": new0,
                "new_fee_protocol1": new1,
                "packed_fee_value": fee_value,
                "transition": _transition_label(old0, old1, new0, new1),
            }
        )
    return {
        "transaction_hash": transaction_hash,
        "block_number": transaction_block,
        "block_hash": transaction_block_hash,
        "transaction_index": transaction_index,
        "caller_address": caller,
        "selector": BATCH_TRIGGER_SELECTOR,
        "calldata_pool_count": len(calldata_pools),
        "receipt_log_count": len(logs),
        "rows": rows,
    }


def validate_governance_execution(
    transaction: Mapping[str, object],
    receipt: Mapping[str, object],
    *,
    governor_address: str,
    proposal_id: int,
    expected_tx_hash: str,
    expected_block: int,
    factory_address: str,
    old_owner: str,
    new_owner: str,
) -> dict[str, object]:
    """Verify Proposal 94 execution and its authoritative factory-owner transition."""

    tx_hash = normalize_hash(transaction.get("hash"), path="governance.transaction.hash")
    frozen_hash = normalize_hash(expected_tx_hash, path="expected_governance_tx_hash")
    if (
        tx_hash != frozen_hash
        or normalize_hash(receipt.get("transactionHash"), path="governance.receipt.transactionHash")
        != frozen_hash
    ):
        raise ValueError("governance transaction hash differs from the frozen hash")
    if normalize_address(transaction.get("to"), path="governance.transaction.to") != normalize_address(
        governor_address, path="governor_address"
    ):
        raise ValueError("governance transaction target differs from the frozen governor")
    expected_input = EXECUTE_SELECTOR + proposal_id.to_bytes(32, "big").hex()
    if transaction.get("input") != expected_input:
        raise ValueError("governance calldata is not execute(frozen proposal id)")
    block_number = decode_quantity(transaction.get("blockNumber"), path="governance.blockNumber")
    if (
        block_number != expected_block
        or decode_quantity(receipt.get("blockNumber"), path="governance.receipt.blockNumber")
        != expected_block
    ):
        raise ValueError("governance execution block differs from the frozen block")
    transaction_block_hash = normalize_hash(
        transaction.get("blockHash"), path="governance.transaction.blockHash"
    )
    receipt_block_hash = normalize_hash(receipt.get("blockHash"), path="governance.receipt.blockHash")
    if transaction_block_hash != receipt_block_hash:
        raise ValueError("governance transaction and receipt block hashes differ")
    if decode_quantity(receipt.get("status"), path="governance.receipt.status") != 1:
        raise ValueError("governance execution receipt is not successful")

    factory = normalize_address(factory_address, path="factory_address")
    expected_old = normalize_address(old_owner, path="old_owner")
    expected_new = normalize_address(new_owner, path="new_owner")
    matching: list[Mapping[str, object]] = []
    for position, raw_log in enumerate(_sequence(receipt.get("logs"), path="governance.receipt.logs")):
        log = _mapping(raw_log, path=f"governance.receipt.logs[{position}]")
        if normalize_address(log.get("address"), path="governance.log.address") != factory:
            continue
        topics = _topics(log, path="governance.OwnerChanged")
        if topics[0] == OWNER_CHANGED_TOPIC:
            matching.append(log)
    if len(matching) != 1:
        raise ValueError("governance receipt must contain exactly one factory OwnerChanged event")
    topics = _topics(matching[0], path="governance.OwnerChanged")
    if len(topics) != 3:
        raise ValueError("OwnerChanged must contain old/new owner topics")
    observed_old = address_from_topic(topics[1], path="OwnerChanged.oldOwner")
    observed_new = address_from_topic(topics[2], path="OwnerChanged.newOwner")
    if observed_old != expected_old or observed_new != expected_new:
        raise ValueError("factory OwnerChanged does not match the frozen old/new adapters")
    return {
        "transaction_hash": tx_hash,
        "block_number": block_number,
        "block_hash": transaction_block_hash,
        "proposal_id": proposal_id,
        "old_factory_owner": observed_old,
        "new_factory_owner": observed_new,
    }


def summarize_treatment_conformance(
    governance: Mapping[str, object],
    batches: Sequence[Mapping[str, object]],
    *,
    expected_batch_hashes: Sequence[str],
    expected_batch_size: int,
    minimum_activated_total: int,
    minimum_activated_per_fee_value: int,
) -> dict[str, object]:
    """Apply the frozen treatment-ledger feasibility gates."""

    expected_hashes = [normalize_hash(value, path="expected_batch_hash") for value in expected_batch_hashes]
    observed_hashes = [
        normalize_hash(batch.get("transaction_hash"), path="batch.transaction_hash") for batch in batches
    ]
    rows: list[Mapping[str, object]] = []
    batch_sizes: list[int] = []
    for index, batch in enumerate(batches):
        batch_rows = _sequence(batch.get("rows"), path=f"batches[{index}].rows")
        typed_rows = [_mapping(row, path=f"batches[{index}].rows") for row in batch_rows]
        rows.extend(typed_rows)
        batch_sizes.append(len(typed_rows))
    pools = [normalize_address(row.get("pool_address"), path="row.pool_address") for row in rows]
    transitions = Counter(str(row.get("transition")) for row in rows)
    fee_values = Counter(int(cast(int, row.get("packed_fee_value"))) for row in rows)
    activated_by_fee = Counter(
        int(cast(int, row.get("packed_fee_value")))
        for row in rows
        if row.get("transition") == "activated_from_zero"
    )
    allowed_new_pairs = {(4, 4), (6, 6)}
    all_allowed_symmetric = all(
        (row.get("new_fee_protocol0"), row.get("new_fee_protocol1")) in allowed_new_pairs for row in rows
    )
    gates = {
        "exact_batch_hash_order": observed_hashes == expected_hashes,
        "exact_batch_count": len(batches) == len(expected_hashes),
        "exact_batch_sizes": batch_sizes == [expected_batch_size] * len(expected_hashes),
        "exact_total_rows": len(rows) == expected_batch_size * len(expected_hashes),
        "unique_pool_rows": len(set(pools)) == len(pools),
        "allowed_symmetric_new_fees": all_allowed_symmetric,
        "minimum_activated_total": transitions["activated_from_zero"] >= minimum_activated_total,
        "minimum_activated_fee_0x44": activated_by_fee[0x44] >= minimum_activated_per_fee_value,
        "minimum_activated_fee_0x66": activated_by_fee[0x66] >= minimum_activated_per_fee_value,
        "governance_owner_change_verified": governance.get("proposal_id") == 94,
    }
    passed = all(gates.values())
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "scientific_role": "historical_development_treatment_metadata_only",
        "decision": (
            "PASS_EXACT_TREATMENT_FRAME_FREEZE_PREPERIOD_DESIGN"
            if passed
            else "FAIL_TREATMENT_CONFORMANCE_NO_LP_RESPONSE_ACCESS"
        ),
        "pass": passed,
        "governance": dict(governance),
        "expected_batch_hashes": expected_hashes,
        "observed_batch_hashes": observed_hashes,
        "batch_sizes": batch_sizes,
        "treatment_row_count": len(rows),
        "unique_pool_count": len(set(pools)),
        "transition_counts": dict(sorted(transitions.items())),
        "packed_fee_value_counts": {f"0x{key:02x}": value for key, value in sorted(fee_values.items())},
        "activated_by_fee_value": {f"0x{key:02x}": value for key, value in sorted(activated_by_fee.items())},
        "treatment_rows_sha256": canonical_json_sha256(rows),
        "gates": gates,
    }


def validate_frozen_contract(contract: Mapping[str, object]) -> tuple[str, ...]:
    """Validate the immutable pre-transition-decoding contract."""

    errors: list[str] = []
    schema_version = contract.get("schema_version")
    if schema_version not in (CONTRACT_SCHEMA_V1, CONTRACT_SCHEMA_V2):
        errors.append(f"schema_version must be {CONTRACT_SCHEMA_V1} or {CONTRACT_SCHEMA_V2}")
    if contract.get("stage") != FROZEN_STAGE:
        errors.append(f"stage must be {FROZEN_STAGE}")
    if contract.get("scientific_role") != "historical_development_treatment_metadata_only":
        errors.append("scientific_role must remain historical_development_treatment_metadata_only")
    try:
        source = _mapping(contract.get("source"), path="source")
        mechanism = _mapping(contract.get("mechanism"), path="mechanism")
        frame = _mapping(contract.get("propagation_frame"), path="propagation_frame")
        reconnaissance = _mapping(contract.get("reconnaissance_disclosure"), path="reconnaissance_disclosure")
        gates = _mapping(contract.get("gates"), path="gates")
        access = _mapping(contract.get("access_boundary"), path="access_boundary")
    except ValueError as error:
        errors.append(str(error))
        return tuple(errors)

    if source.get("chain_id") != 1 or source.get("network") != "ethereum_mainnet":
        errors.append("source must remain Ethereum mainnet chain 1")
    if source.get("expected_rpc_request_count") != 11:
        errors.append("source.expected_rpc_request_count must remain 11")
    if schema_version == CONTRACT_SCHEMA_V1 and source.get("runtime_bytecode_block") != 24599177:
        errors.append("v1 source.runtime_bytecode_block must remain the first propagation block")
    if schema_version == CONTRACT_SCHEMA_V2 and source.get("runtime_bytecode_block") != "latest":
        errors.append("v2 source.runtime_bytecode_block must remain latest")
    for key in ("rpc_url", "verified_source_url", "proposal_url"):
        value = source.get(key)
        if not isinstance(value, str) or not value.startswith("https://"):
            errors.append(f"source.{key} must be HTTPS")
    for key in ("verified_source_sha256", "runtime_bytecode_sha256", "runtime_bytecode_keccak256"):
        value = source.get(key)
        if not isinstance(value, str) or SHA256.fullmatch(value) is None:
            errors.append(f"source.{key} must be a lowercase 64-hex digest")
    for key in ("protocol_fees_commit", "seatbelt_commit"):
        value = source.get(key)
        if not isinstance(value, str) or GIT_SHA.fullmatch(value) is None:
            errors.append(f"source.{key} must be a full Git SHA")

    if schema_version == CONTRACT_SCHEMA_V2:
        try:
            repair = _mapping(contract.get("transport_repair"), path="transport_repair")
        except ValueError as error:
            errors.append(str(error))
        else:
            expected_repair = {
                "parent_contract": "data/manifests/uniswap_v3_fee_treatment_conformance_v1.yaml",
                "parent_contract_sha256": (
                    "3bf8d454f1c2fa8ef091c4ac4fc00e8d6c9c99d7084e52314a925a121d194279"
                ),
                "parent_protocol_commit": "647da77a3987f3009af1c5a9462d574c1ce353d4",
                "parent_decision": ("FAIL_RPC_HISTORICAL_STATE_FORBIDDEN_BEFORE_TRANSITION_ACCESS"),
                "parent_successful_rpc_calls": 1,
                "parent_failed_method": "eth_getCode",
                "parent_failed_http_status": 403,
                "parent_failed_attempt_count": 3,
                "governance_or_propagation_receipts_accessed_by_parent_run": False,
                "only_changed_scientific_input": "none",
                "only_changed_transport_field": "source.runtime_bytecode_block",
            }
            if dict(repair) != expected_repair:
                errors.append("v2 transport repair must preserve the exact v1 failure and repair scope")

    try:
        if mechanism.get("governance_proposal_id") != 94:
            errors.append("mechanism.governance_proposal_id must remain 94")
        if mechanism.get("governance_execution_block") != 24596885:
            errors.append("mechanism.governance_execution_block must remain 24596885")
        normalize_hash(mechanism.get("governance_execution_tx"), path="governance_execution_tx")
        normalize_address(mechanism.get("factory_address"), path="factory_address")
        old_owner = normalize_address(mechanism.get("old_adapter_address"), path="old_adapter_address")
        new_owner = normalize_address(
            mechanism.get("executed_adapter_address"), path="executed_adapter_address"
        )
        prose_owner = normalize_address(
            mechanism.get("proposal_prose_adapter_address"), path="proposal_prose_adapter_address"
        )
        if old_owner == new_owner or prose_owner == new_owner:
            errors.append("old/prose/executed adapter roles must remain distinguishable")
        if mechanism.get("owner_changed_topic") != OWNER_CHANGED_TOPIC:
            errors.append("mechanism.owner_changed_topic changed")
    except ValueError as error:
        errors.append(str(error))

    hashes = frame.get("batch_transaction_hashes")
    if not isinstance(hashes, list) or len(hashes) != 2:
        errors.append("propagation_frame.batch_transaction_hashes must contain exactly two hashes")
    else:
        try:
            normalized = [normalize_hash(value, path="batch_transaction_hash") for value in hashes]
            if len(set(normalized)) != len(normalized):
                errors.append("batch transaction hashes must be unique")
            if frame.get("batch_transaction_hashes_sha256") != canonical_json_sha256(normalized):
                errors.append("batch_transaction_hashes_sha256 does not match")
        except ValueError as error:
            errors.append(str(error))
    if frame.get("selector") != BATCH_TRIGGER_SELECTOR:
        errors.append("propagation_frame.selector changed")
    if frame.get("expected_batch_size") != 500 or frame.get("expected_total_pool_rows") != 1000:
        errors.append("propagation frame must remain two 500-pool batches")
    expected_blocks = frame.get("expected_blocks")
    expected_timestamps = frame.get("expected_batch_timestamps_utc")
    if not isinstance(expected_blocks, list) or expected_blocks != [24599177, 24599179]:
        errors.append("propagation_frame.expected_blocks changed")
    if not isinstance(expected_timestamps, list) or len(expected_timestamps) != 2:
        errors.append("propagation_frame.expected_batch_timestamps_utc must contain two values")
    if frame.get("no_replacement") is not True:
        errors.append("propagation_frame.no_replacement must be true")

    expected_reconnaissance = {
        "calldata_lengths_accessed": True,
        "receipt_event_type_counts_accessed": True,
        "old_new_fee_arguments_decoded": False,
        "activation_classes_decoded": False,
        "lp_response_events_accessed": False,
        "frame_is_pristine": False,
    }
    if dict(reconnaissance) != expected_reconnaissance:
        errors.append("reconnaissance disclosure must preserve the actual pre-freeze access history")

    for key in (
        "exact_owner_change",
        "exact_batch_hash_order",
        "exact_event_pairing",
        "unique_pools",
        "one_set_fee_protocol_per_pool",
        "one_fee_update_triggered_per_pool",
        "calldata_event_order_must_match",
    ):
        if gates.get(key) is not True:
            errors.append(f"gates.{key} must be true")
    if gates.get("exact_batch_size") != 500 or gates.get("exact_total_pool_rows") != 1000:
        errors.append("gates must retain the exact 500/1,000 frame sizes")
    if gates.get("allowed_new_fee_pairs") != [[4, 4], [6, 6]]:
        errors.append("gates.allowed_new_fee_pairs must remain [[4,4],[6,6]]")
    for key in ("minimum_activated_total", "minimum_activated_per_fee_value"):
        value = gates.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            errors.append(f"gates.{key} must be a positive integer")

    required_false = (
        "lp_action_events_opened",
        "swap_events_opened",
        "liquidity_outcomes_opened",
        "price_or_volume_outcomes_opened",
        "post_treatment_response_window_opened",
        "preperiod_selection_opened",
        "outcome_model_training_authorized",
    )
    for key in required_false:
        if access.get(key) is not False:
            errors.append(f"access_boundary.{key} must be false")
    if access.get("mechanism_transactions_and_receipts_only") is not True:
        errors.append("access_boundary.mechanism_transactions_and_receipts_only must be true")
    if access.get("gpu_hours_authorized") != 0 or access.get("paid_data_authorized") is not False:
        errors.append("GPU hours and paid data must remain unauthorized")
    if contract.get("result") is not None:
        errors.append("result must be null before old/new fee-transition decoding")
    return tuple(errors)
