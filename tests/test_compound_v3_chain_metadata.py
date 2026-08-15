from copy import deepcopy
from pathlib import Path
from typing import cast

from ecomd.research.compound_v3_chain_metadata import (
    ADMIN_SLOT,
    IMPLEMENTATION_SLOT,
    decode_word_address,
    decode_word_uint,
    evaluate_chain_metadata,
    load_chain_metadata_preflight,
    validate_chain_metadata_preflight,
)

MANIFEST_PATH = Path("data/manifests/compound_v3_chain_metadata_preflight_v1.yaml")


def _code(seed: str) -> dict[str, object]:
    return {"byte_count": 10, "sha256": seed * 64, "nonempty": True}


def _passing_records(manifest: dict[str, object]) -> tuple[list[dict[str, object]], dict[str, object]]:
    markets = cast(list[dict[str, object]], manifest["markets"])
    records: list[dict[str, object]] = []
    for index, market in enumerate(markets):
        records.append(
            {
                "market_id": market["market_id"],
                "proxy_code": _code("a"),
                "implementation": f"0x{index + 100:040x}",
                "implementation_code": _code("b"),
                "admin": "0x0000000000000000000000000000000000000999",
                "getters": {
                    "base_token": market["expected_base_token"],
                    "governor": market["expected_governor"],
                    "pause_guardian": market["expected_pause_guardian"],
                    "num_assets": index + 1,
                },
            }
        )
    configurator = {
        "proxy_code": _code("c"),
        "implementation": "0x0000000000000000000000000000000000000777",
        "implementation_code": _code("d"),
        "admin": "0x0000000000000000000000000000000000000999",
    }
    return records, configurator


def test_canonical_chain_metadata_manifest_is_valid_and_forbids_accounts() -> None:
    manifest = load_chain_metadata_preflight(MANIFEST_PATH)

    assert validate_chain_metadata_preflight(manifest) == []
    assert manifest["proxy_slots"] == {"implementation": IMPLEMENTATION_SLOT, "admin": ADMIN_SLOT}
    boundary = manifest["access_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["chain_rpc_used"] is True
    assert boundary["account_mapping_storage_used"] is False
    assert boundary["eth_get_logs_used"] is False
    assert boundary["participant_action_rows_opened"] is False


def test_abi_word_decoders_are_strict() -> None:
    address = "1234567890abcdef1234567890abcdef12345678"
    assert decode_word_address("0x" + "00" * 12 + address, path="address") == "0x" + address
    assert decode_word_uint("0x" + (17).to_bytes(32, "big").hex(), path="uint") == 17


def test_complete_synthetic_chain_metadata_passes_all_gates() -> None:
    manifest = load_chain_metadata_preflight(MANIFEST_PATH)
    market_records, configurator = _passing_records(manifest)
    archive_records = [
        {
            "market_id": record["market_id"],
            "proxy_code": record["proxy_code"],
            "implementation": record["implementation"],
            "implementation_code": record["implementation_code"],
        }
        for record in (market_records[0], market_records[4])
    ]
    request_summary = {
        "successful_request_count": 61,
        "http_attempt_count": 61,
        "response_byte_count": 100_000,
        "method_counts": {
            "eth_call": 24,
            "eth_chainId": 1,
            "eth_getBlockByNumber": 2,
            "eth_getCode": 18,
            "eth_getStorageAt": 16,
        },
    }

    gates = evaluate_chain_metadata(
        manifest,
        source_artifact_matches=True,
        chain_id="0x1",
        finalized_block={"number": 24_000_000, "timestamp_unix": 1_800_000_000},
        market_records=market_records,
        configurator_record=configurator,
        archive_block={"number": 17_000_000, "timestamp_unix": 1_680_000_000},
        archive_records=archive_records,
        request_summary=request_summary,
    )

    assert len(gates) == 12
    assert all(gates.values())


def test_getter_mismatch_and_archive_code_change_fail_scientific_gates() -> None:
    manifest = load_chain_metadata_preflight(MANIFEST_PATH)
    market_records, configurator = _passing_records(manifest)
    getters = market_records[0]["getters"]
    assert isinstance(getters, dict)
    getters["base_token"] = "0x0000000000000000000000000000000000000123"
    archive_records = [
        {
            "market_id": market_records[0]["market_id"],
            "proxy_code": _code("f"),
            "implementation": market_records[0]["implementation"],
            "implementation_code": market_records[0]["implementation_code"],
        },
        {
            "market_id": market_records[4]["market_id"],
            "proxy_code": market_records[4]["proxy_code"],
            "implementation": market_records[4]["implementation"],
            "implementation_code": market_records[4]["implementation_code"],
        },
    ]
    request_summary = {
        "successful_request_count": 61,
        "http_attempt_count": 61,
        "response_byte_count": 100_000,
        "method_counts": {
            "eth_call": 24,
            "eth_chainId": 1,
            "eth_getBlockByNumber": 2,
            "eth_getCode": 18,
            "eth_getStorageAt": 16,
        },
    }

    gates = evaluate_chain_metadata(
        manifest,
        source_artifact_matches=True,
        chain_id="0x1",
        finalized_block={"number": 24_000_000, "timestamp_unix": 1_800_000_000},
        market_records=market_records,
        configurator_record=configurator,
        archive_block={"number": 17_000_000, "timestamp_unix": 1_680_000_000},
        archive_records=archive_records,
        request_summary=request_summary,
    )

    assert gates["current_getters"] is False
    assert gates["historical_archive_state"] is False


def test_manifest_rejects_log_account_and_response_access() -> None:
    manifest = load_chain_metadata_preflight(MANIFEST_PATH)
    broken = deepcopy(manifest)
    boundary = broken["access_boundary"]
    rpc = broken["rpc"]
    assert isinstance(boundary, dict)
    assert isinstance(rpc, dict)
    boundary["account_mapping_storage_used"] = True
    boundary["eth_get_logs_used"] = True
    boundary["realized_response_rows_opened"] = True
    methods = rpc["allowed_methods"]
    assert isinstance(methods, list)
    methods.append("eth_getLogs")

    errors = validate_chain_metadata_preflight(broken)

    assert any("account_mapping_storage_used must be false" in error for error in errors)
    assert any("eth_get_logs_used must be false" in error for error in errors)
    assert any("realized_response_rows_opened must be false" in error for error in errors)
    assert any("allowed_methods must equal" in error for error in errors)
