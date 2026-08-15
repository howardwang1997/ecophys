from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest

from ecomd.research.compound_candidate_mechanics import (
    ADMIN_DEPLOY_SELECTORS,
    DEPLOY_SELECTOR,
    PROXY_UPGRADE_SELECTORS,
    SETTER_SELECTORS,
    _beacon_finalized_execution,
    _failure_artifact,
    _getter_conformance,
    _receipt_matches_d0,
    _receipt_record,
    analyze_mechanism_trace,
    build_http_transport,
    decode_asset_info,
    derive_d0_candidates,
    expected_operation_plan,
    load_candidate_mechanics,
    normalize_blockscout_raw_trace,
    validate_candidate_mechanics,
    validate_parent_evidence,
)
from ecomd.research.compound_governance_inventory import EVENT_CONTRACT

MANIFEST_PATH = Path("data/manifests/compound_v3_candidate_mechanics_preflight_v2.yaml")
D0_SUMMARY_PATH = Path("experiments/v14_compound_v3_governance_log_inventory/artifacts/summary.json")
D0_INVENTORY_PATH = Path(
    "experiments/v14_compound_v3_governance_log_inventory/artifacts/governance_logs.json"
)
CONFIGURATOR = "0x316f9708bb98af7da9c68c1c3b5e79039cd336e3"
PROXY = "0x5d409e56d886231adaf00c8775665ad0f9897b56"
ASSET = "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0"
IMPLEMENTATION = "0xb7dabef05ab656123d0274c4c39e4ce4eb894b89"
ADMIN = "0x1ec63b5883c3481134fd50d5daebc83ecd2e8779"
GOVERNOR = "0x1111111111111111111111111111111111111111"
SENDER = "0x2222222222222222222222222222222222222222"


def _word(value: int) -> str:
    return value.to_bytes(32, "big").hex()


def _address_word(address: str) -> str:
    return "00" * 12 + address[2:]


def _static_call(selector: str, *arguments: str) -> str:
    return selector + "".join(arguments)


def _raw_call(
    *,
    from_address: str,
    to_address: str,
    input_data: str,
    trace_address: list[int],
    subtraces: int = 0,
    call_type: str = "call",
) -> dict[str, object]:
    return {
        "action": {
            "callType": call_type,
            "from": from_address,
            "to": to_address,
            "value": "0x0",
            "gas": "0x100000",
            "input": input_data,
        },
        "result": {"gasUsed": "0x1000", "output": "0x"},
        "subtraces": subtraces,
        "traceAddress": trace_address,
        "type": "call",
    }


def _candidate() -> dict[str, object]:
    return {
        "candidate_id": "borrow_cf_22273296_0080d1f7",
        "priority_rank": 1,
        "block_number": 22_273_296,
        "transaction_hash": "0x" + "33" * 32,
        "market_id": "mainnet_usds",
        "comet_proxy": PROXY,
        "asset": ASSET,
        "event_type": "update_asset_borrow_collateral_factor",
        "old_value": 820_000_000_000_000_000,
        "new_value": 800_000_000_000_000_000,
        "implementation": IMPLEMENTATION,
        "nearby_other_governance_blocks": [],
    }


def _clean_trace() -> tuple[list[dict[str, object]], dict[str, object]]:
    setter_input = _static_call(
        SETTER_SELECTORS["update_asset_borrow_collateral_factor"],
        _address_word(PROXY),
        _address_word(ASSET),
        _word(800_000_000_000_000_000),
    )
    deploy_input = _static_call(DEPLOY_SELECTOR, _address_word(PROXY))
    admin_input = _static_call(
        ADMIN_DEPLOY_SELECTORS[0],
        _address_word(CONFIGURATOR),
        _address_word(PROXY),
    )
    upgrade_input = _static_call(PROXY_UPGRADE_SELECTORS[0], _address_word(IMPLEMENTATION))
    root_input = "0x12345678" + _word(7)
    raw = [
        _raw_call(
            from_address=SENDER,
            to_address=GOVERNOR,
            input_data=root_input,
            trace_address=[],
            subtraces=3,
        ),
        _raw_call(
            from_address=GOVERNOR,
            to_address=CONFIGURATOR,
            input_data=setter_input,
            trace_address=[0],
        ),
        _raw_call(
            from_address=GOVERNOR,
            to_address=ADMIN,
            input_data=admin_input,
            trace_address=[1],
            subtraces=2,
        ),
        _raw_call(
            from_address=ADMIN,
            to_address=CONFIGURATOR,
            input_data=deploy_input,
            trace_address=[1, 0],
        ),
        _raw_call(
            from_address=ADMIN,
            to_address=PROXY,
            input_data=upgrade_input,
            trace_address=[1, 1],
        ),
        _raw_call(
            from_address=GOVERNOR,
            to_address="0x4444444444444444444444444444444444444444",
            input_data="0xabcdef01",
            trace_address=[2],
            call_type="staticcall",
        ),
    ]
    transaction = {"from": SENDER, "to": GOVERNOR, "value": 0, "input": root_input}
    nodes = normalize_blockscout_raw_trace(raw, maximum_nodes=100, maximum_input_bytes=10_000)
    return nodes, transaction


def test_canonical_manifest_parent_hashes_and_d0_derivation_are_valid() -> None:
    manifest = load_candidate_mechanics(MANIFEST_PATH)

    assert validate_candidate_mechanics(manifest) == []
    assert validate_parent_evidence(manifest, Path.cwd()) == []


def test_candidate_order_and_neighbor_blocks_are_derived_without_responses() -> None:
    import json

    summary = json.loads(D0_SUMMARY_PATH.read_text(encoding="utf-8"))
    inventory = json.loads(D0_INVENTORY_PATH.read_text(encoding="utf-8"))

    derived = derive_d0_candidates(summary, inventory)

    assert len(derived) == 14
    assert [candidate["priority_rank"] for candidate in derived] == list(range(1, 15))
    assert derived[0]["candidate_id"] == "borrow_cf_22273296_0080d1f7"
    assert derived[1]["candidate_id"] == "borrow_cf_25571051_fdbdc6fc"
    assert derived[9]["nearby_other_governance_blocks"] == [20_721_442]
    assert derived[10]["nearby_other_governance_blocks"] == [20_878_779]
    assert derived[11]["nearby_other_governance_blocks"] == [21_237_796]


def test_asset_info_decoder_enforces_widths_asset_and_field_order() -> None:
    words = [
        _word(3),
        _address_word(ASSET),
        _address_word("0x5555555555555555555555555555555555555555"),
        _word(10**18),
        _word(820_000_000_000_000_000),
        _word(880_000_000_000_000_000),
        _word(950_000_000_000_000_000),
        _word(10**24),
    ]

    decoded = decode_asset_info("0x" + "".join(words), expected_asset=ASSET)

    assert decoded == {
        "offset": 3,
        "asset": ASSET,
        "price_feed": "0x5555555555555555555555555555555555555555",
        "scale": 10**18,
        "borrow_collateral_factor": 820_000_000_000_000_000,
        "liquidate_collateral_factor": 880_000_000_000_000_000,
        "liquidation_factor": 950_000_000_000_000_000,
        "supply_cap": 10**24,
    }

    overflow = list(words)
    overflow[4] = _word(2**64)
    with pytest.raises(ValueError, match="uint64"):
        decode_asset_info("0x" + "".join(overflow), expected_asset=ASSET)
    with pytest.raises(ValueError, match="requested asset"):
        decode_asset_info(
            "0x" + "".join(words),
            expected_asset="0x6666666666666666666666666666666666666666",
        )


def test_clean_trace_has_exact_required_calls_and_no_stateful_sibling() -> None:
    nodes, transaction = _clean_trace()

    analysis = analyze_mechanism_trace(
        nodes,
        transaction=transaction,
        candidate=_candidate(),
        admin_address=ADMIN,
    )

    assert analysis["root_matches_transaction"] is True
    assert analysis["exact_required_calls"] is True
    assert analysis["required_call_counts"] == {
        "exact_configurator_setter": 1,
        "exact_configurator_deploy": 1,
        "exact_proxy_admin_deploy_and_upgrade": 1,
        "exact_target_proxy_upgrade": 1,
    }
    assert analysis["exact_required_call_counts"] is True
    assert analysis["required_call_topology_conforms"] is True
    assert analysis["unclassified_successful_stateful_calls"] == []
    assert analysis["payload_call_cone_isolated"] is True


def test_raw_trace_requires_complete_unique_parent_child_topology() -> None:
    nodes, _ = _clean_trace()
    assert nodes[0]["path"] == []
    assert nodes[0]["source_subtraces"] == 3

    raw = [
        _raw_call(
            from_address=SENDER,
            to_address=GOVERNOR,
            input_data="0x12345678",
            trace_address=[],
            subtraces=1,
        ),
        _raw_call(
            from_address=GOVERNOR,
            to_address=CONFIGURATOR,
            input_data="0xabcdef01",
            trace_address=[0],
        ),
    ]
    duplicate = [*raw, deepcopy(raw[1])]
    with pytest.raises(ValueError, match="unique"):
        normalize_blockscout_raw_trace(
            duplicate,
            maximum_nodes=100,
            maximum_input_bytes=10_000,
        )

    missing_parent = deepcopy(raw)
    missing_parent[1]["traceAddress"] = [0, 0]
    with pytest.raises(ValueError, match=r"parent|subtrace"):
        normalize_blockscout_raw_trace(
            missing_parent,
            maximum_nodes=100,
            maximum_input_bytes=10_000,
        )

    wrong_subtraces = deepcopy(raw)
    wrong_subtraces[0]["subtraces"] = 2
    with pytest.raises(ValueError, match="subtrace"):
        normalize_blockscout_raw_trace(
            wrong_subtraces,
            maximum_nodes=100,
            maximum_input_bytes=10_000,
        )

    selfdestruct = deepcopy(raw[:1])
    selfdestruct[0]["subtraces"] = 1
    selfdestruct.append(
        {
            "action": {
                "address": GOVERNOR,
                "balance": "0x1",
                "refundAddress": "0x7777777777777777777777777777777777777777",
            },
            "subtraces": 0,
            "traceAddress": [0],
            "type": "selfdestruct",
        }
    )
    normalized_selfdestruct = normalize_blockscout_raw_trace(
        selfdestruct,
        maximum_nodes=100,
        maximum_input_bytes=10_000,
    )
    assert normalized_selfdestruct[1]["type"] == "SELFDESTRUCT"
    assert normalized_selfdestruct[1]["value"] == 1


def test_required_calls_must_be_calls_with_proxy_admin_topology() -> None:
    nodes, transaction = _clean_trace()
    deploy = next(node for node in nodes if node["selector"] == DEPLOY_SELECTOR)
    deploy["from"] = GOVERNOR

    wrong_caller = analyze_mechanism_trace(
        nodes,
        transaction=transaction,
        candidate=_candidate(),
        admin_address=ADMIN,
    )

    assert wrong_caller["exact_required_call_counts"] is True
    assert wrong_caller["required_call_topology_conforms"] is False
    assert wrong_caller["exact_required_calls"] is False

    nodes, transaction = _clean_trace()
    setter = next(node for node in nodes if node["selector"] == SETTER_SELECTORS[_candidate()["event_type"]])
    setter["type"] = "STATICCALL"
    static_setter = analyze_mechanism_trace(
        nodes,
        transaction=transaction,
        candidate=_candidate(),
        admin_address=ADMIN,
    )
    assert static_setter["required_call_counts"]["exact_configurator_setter"] == 0
    assert static_setter["exact_required_calls"] is False


def test_successful_stateful_sibling_fails_call_cone_isolation() -> None:
    nodes, transaction = _clean_trace()
    nodes.append(
        {
            "path": [3],
            "type": "CALL",
            "from": GOVERNOR,
            "to": "0x7777777777777777777777777777777777777777",
            "value": 0,
            "gas": 1,
            "gas_used": 1,
            "input": "0xdeadbeef",
            "input_byte_count": 4,
            "input_sha256": "0" * 64,
            "selector": "0xdeadbeef",
            "output_byte_count": 0,
            "output_sha256": "0" * 64,
            "success": True,
            "error": None,
            "revert_reason": None,
        }
    )

    analysis = analyze_mechanism_trace(
        nodes,
        transaction=transaction,
        candidate=_candidate(),
        admin_address=ADMIN,
    )

    assert analysis["exact_required_calls"] is True
    assert len(analysis["unclassified_successful_stateful_calls"]) == 1
    assert analysis["payload_call_cone_isolated"] is False


def test_selfdestruct_sibling_is_conservatively_stateful() -> None:
    nodes, transaction = _clean_trace()
    nodes.append(
        {
            "path": [3],
            "type": "SELFDESTRUCT",
            "source_type": "selfdestruct",
            "source_subtraces": 0,
            "from": GOVERNOR,
            "to": "0x7777777777777777777777777777777777777777",
            "value": 1,
            "gas": 0,
            "gas_used": 0,
            "input": "0x",
            "input_byte_count": 0,
            "input_sha256": "0" * 64,
            "selector": None,
            "output_byte_count": 0,
            "output_sha256": "0" * 64,
            "own_success": True,
            "success": True,
            "error": None,
            "revert_reason": None,
        }
    )

    analysis = analyze_mechanism_trace(
        nodes,
        transaction=transaction,
        candidate=_candidate(),
        admin_address=ADMIN,
    )

    assert analysis["exact_required_calls"] is True
    assert analysis["unclassified_successful_stateful_calls"][0]["type"] == "SELFDESTRUCT"
    assert analysis["payload_call_cone_isolated"] is False


def test_receipt_must_reproduce_every_d0_relevant_log_without_extras() -> None:
    key = {
        "block_hash": "0x" + "aa" * 32,
        "transaction_hash": "0x" + "bb" * 32,
        "log_index": 3,
    }
    parent = {
        **key,
        "address": CONFIGURATOR,
        "topic0": "0x" + "cc" * 32,
        "topic_count": 3,
        "data_sha256": "dd" * 32,
    }
    observed = {
        **key,
        "address": CONFIGURATOR,
        "topics": ["0x" + "cc" * 32, "0x" + "11" * 32, "0x" + "22" * 32],
        "topic_count": 3,
        "data_sha256": "dd" * 32,
        "governance_record": parent,
    }

    clean = _receipt_matches_d0({"logs": [observed]}, [parent])
    extra = dict(observed)
    extra["log_index"] = 4
    with_extra = _receipt_matches_d0({"logs": [observed, extra]}, [parent])

    assert clean["d0_logs_conform"] is True
    assert with_extra["d0_logs_conform"] is False
    assert len(with_extra["extra_relevant_log_keys"]) == 1


def test_receipt_redecodes_indexed_fields_and_enforces_log_identity() -> None:
    candidate = _candidate()
    block_hash = "0x" + "aa" * 32
    tx_hash = candidate["transaction_hash"]
    transaction_index = 7
    event = EVENT_CONTRACT["update_asset_borrow_collateral_factor"]
    raw_log = {
        "address": CONFIGURATOR,
        "blockHash": block_hash,
        "blockNumber": hex(candidate["block_number"]),
        "transactionHash": tx_hash,
        "transactionIndex": hex(transaction_index),
        "logIndex": "0x3",
        "topics": [
            event["topic0"],
            "0x" + _address_word(PROXY),
            "0x" + _address_word(ASSET),
        ],
        "data": "0x" + _word(candidate["old_value"]) + _word(candidate["new_value"]),
        "removed": False,
    }
    raw_receipt = {
        "transactionHash": tx_hash,
        "blockHash": block_hash,
        "blockNumber": hex(candidate["block_number"]),
        "transactionIndex": hex(transaction_index),
        "from": SENDER,
        "to": GOVERNOR,
        "status": "0x1",
        "gasUsed": "0x1000",
        "logs": [raw_log],
    }

    receipt = _receipt_record(raw_receipt, candidate=candidate, maximum_logs=10)
    governance_record = receipt["logs"][0]["governance_record"]
    assert governance_record["asset"] == ASSET
    assert _receipt_matches_d0(receipt, [governance_record])["d0_logs_conform"] is True

    altered_log = deepcopy(raw_log)
    altered_log["topics"][2] = "0x" + _address_word("0x6666666666666666666666666666666666666666")
    altered_receipt = deepcopy(raw_receipt)
    altered_receipt["logs"] = [altered_log]
    decoded_altered = _receipt_record(altered_receipt, candidate=candidate, maximum_logs=10)
    assert _receipt_matches_d0(decoded_altered, [governance_record])["d0_logs_conform"] is False

    inconsistent_log = deepcopy(raw_log)
    inconsistent_log["transactionIndex"] = "0x8"
    inconsistent_receipt = deepcopy(raw_receipt)
    inconsistent_receipt["logs"] = [inconsistent_log]
    with pytest.raises(ValueError, match="identity differs"):
        _receipt_record(inconsistent_receipt, candidate=candidate, maximum_logs=10)


def test_finality_getter_and_exact_ordered_operation_plan() -> None:
    finalized = _beacon_finalized_execution(
        {
            "version": "deneb",
            "execution_optimistic": False,
            "data": {
                "finalized_header": {
                    "beacon": {"slot": "12345"},
                    "execution": {
                        "block_number": "25000000",
                        "block_hash": "0x" + "ab" * 32,
                    },
                }
            },
        }
    )
    assert finalized["block_number"] == 25_000_000
    assert finalized["beacon_slot"] == 12_345

    pre = {
        "offset": 1,
        "asset": ASSET,
        "price_feed": "0x5555555555555555555555555555555555555555",
        "scale": 10**18,
        "borrow_collateral_factor": 820_000_000_000_000_000,
        "liquidate_collateral_factor": 880_000_000_000_000_000,
        "liquidation_factor": 950_000_000_000_000_000,
        "supply_cap": 10**24,
    }
    post = {**pre, "borrow_collateral_factor": 800_000_000_000_000_000}
    assert _getter_conformance(pre, post, _candidate())["exact_getter_conformance"] is True
    assert (
        _getter_conformance(pre, {**post, "supply_cap": 2 * 10**24}, _candidate())["exact_getter_conformance"]
        is False
    )

    manifest = load_candidate_mechanics(MANIFEST_PATH)
    plan = expected_operation_plan(manifest, beacon_finalized_block_number=25_000_000)
    assert len(plan) == 188
    assert Counter(item["provider"] for item in plan) == {
        "blockscout": 156,
        "blockscout_raw_trace": 14,
        "publicnode_execution": 17,
        "publicnode_beacon": 1,
    }
    assert plan[0]["label"] == "chain_id"
    assert plan[2]["label"] == "beacon_finality_update"
    assert plan[6]["label"] == "borrow_cf_22273296_0080d1f7:transaction"
    assert plan[10] == {
        "operation_type": "blockscout_raw_trace_rest",
        "provider": "blockscout_raw_trace",
        "label": "borrow_cf_22273296_0080d1f7:raw_trace",
        "path": (
            "/api/v2/transactions/"
            "0x0080d1f75c7193799b5e1f00028f51239da8da0d0e3192db1f0af5f1edc7bfda/"
            "raw-trace"
        ),
    }
    assert plan[-1]["label"] == "supply_cap_25148942_be6aa6fa:asset_info_post"


def test_failure_artifact_bounds_error_and_retains_attempt_ledgers() -> None:
    manifest = load_candidate_mechanics(MANIFEST_PATH)
    transport = build_http_transport(manifest)
    transport.http_attempts = 1
    transport.response_bytes = 17
    transport.records.append({"label": "chain_id", "response_body_sha256": "a" * 64})
    transport.attempt_records.append(
        {
            "label": "chain_id",
            "outcome": "success",
            "response_body_sha256": "a" * 64,
        }
    )

    artifact = _failure_artifact(
        manifest=manifest,
        manifest_sha256="b" * 64,
        collection_commit="c" * 40,
        transport=transport,
        error=RuntimeError("x" * 2_100),
    )

    assert artifact["decision"] == "INFRASTRUCTURE_FAILURE_NO_CANDIDATE_MECHANICS_RESULT"
    assert artifact["scientific_gate_decision_reached"] is False
    assert artifact["successful_operation_count"] == 1
    assert artifact["http_attempt_count"] == artifact["http_attempt_record_count"] == 1
    assert len(artifact["exception"]["message"]) == 2_000
    assert artifact["exception"]["message_truncated"] is True
    assert "raw_response" not in artifact


def test_validator_rejects_participant_access_candidate_replacement_and_cap_drift() -> None:
    manifest = load_candidate_mechanics(MANIFEST_PATH)
    broken = deepcopy(manifest)
    access = broken["access_boundary"]
    selection = broken["selection_contract"]
    requests = broken["expected_request_contract"]
    assert isinstance(access, dict)
    assert isinstance(selection, dict)
    assert isinstance(requests, dict)
    access["account_state_rows_opened"] = True
    access["gpu_used"] = True
    selection["candidate_replacement_after_freeze"] = True
    requests["json_rpc_success_count_without_retry"] = 186

    errors = validate_candidate_mechanics(broken)

    assert any("account_state_rows_opened must be false" in error for error in errors)
    assert any("gpu_used must be false" in error for error in errors)
    assert "selection_contract differs from the frozen contract" in errors
    assert "expected_request_contract differs from the frozen plan" in errors
