from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from copy import deepcopy
from pathlib import Path
from typing import cast

from ecomd.research.aave_b0_transport_canary import HttpObservation, ProbeClient, load_json
from ecomd.research.aave_b0_transport_canary_repair import (
    ARTIFACT_SCHEMA_VERSION,
    AUDIT_ID,
    EXPECTED_REPAIRS,
    FAIL_DECISION,
    HOST_PRIORITY,
    PASS_DECISION,
    V1_REQUIRED_PASSING,
    ZERO_ADDRESS,
    aggregate_results,
    probe_repair_endpoint,
    validate_manifest,
    validate_parent_files,
)

MANIFEST_PATH = Path("data/manifests/aave_v3_b0_transport_canary_repair_v2.json")
PROTOCOL_COMMIT = "1" * 40
MANIFEST_SHA = "2" * 64
SOURCE_SHA = "3" * 64


class FakeTransport:
    def __init__(
        self,
        handler: Callable[[str, Mapping[str, object]], HttpObservation],
    ) -> None:
        self.handler = handler
        self.calls: list[tuple[str, dict[str, object]]] = []

    def __call__(self, url: str, body: bytes, headers: Mapping[str, str], timeout: float) -> HttpObservation:
        del headers, timeout
        request = cast(dict[str, object], json.loads(body))
        self.calls.append((url, request))
        return self.handler(url, request)


def _rpc_result(request: Mapping[str, object], result: object) -> HttpObservation:
    body = json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": result}).encode()
    return HttpObservation(status=200, body=body)


def _rpc_error(request: Mapping[str, object], message: str) -> HttpObservation:
    body = json.dumps(
        {"jsonrpc": "2.0", "id": request["id"], "error": {"code": -32005, "message": message}}
    ).encode()
    return HttpObservation(status=200, body=body)


def _client(transport: FakeTransport) -> ProbeClient:
    return ProbeClient(
        transport=transport,
        maximum_requests_per_second=1_000_000_000,
        maximum_attempts_per_logical_call=2,
        maximum_http_attempts=100,
        maximum_response_bytes=8_388_608,
        timeout_seconds=1,
        user_agent="test",
    )


def test_manifest_and_all_v1_inheritance_are_valid() -> None:
    manifest = load_json(MANIFEST_PATH)

    assert validate_manifest(manifest) == []
    assert validate_parent_files(manifest, Path.cwd()) == []

    changed = deepcopy(manifest)
    repairs = cast(list[dict[str, object]], changed["repair_endpoints"])
    repairs[-1]["url"] = "https://observed-after-freeze.invalid"
    assert "repair endpoint candidates differ from the frozen order" in validate_manifest(changed)


def test_bnb_candidate_is_the_single_documented_drpc_endpoint() -> None:
    manifest = load_json(MANIFEST_PATH)
    repairs = cast(list[dict[str, object]], manifest["repair_endpoints"])

    assert [item["name"] for item in repairs] == ["polygon", "base", "bnb"]
    assert repairs[-1] == {
        "name": "bnb",
        "chain_id_hex": "0x38",
        "endpoint_role": "documented_provider",
        "url": "https://bsc.drpc.org",
        "candidate_origin": "bnb_official_provider_list_and_drpc_eth_getlogs_documentation",
    }


def test_persistent_http_400_and_413_are_bisected_only_after_single_pass() -> None:
    for range_status in (400, 413):

        def handler(
            _url: str,
            request: Mapping[str, object],
            status: int = range_status,
        ) -> HttpObservation:
            if request["method"] == "eth_chainId":
                return _rpc_result(request, "0x2a")
            query = cast(list[dict[str, str]], request["params"])[0]
            span = int(query["toBlock"], 16) + 1
            if span > 1_954:
                return HttpObservation(status=status, body=b"bounded range failure")
            return _rpc_result(request, [])

        transport = FakeTransport(handler)
        client = _client(transport)
        result = probe_repair_endpoint(
            client,
            deployment="synthetic",
            expected_chain_id="0x2a",
            endpoint_role="repair",
            url="https://rpc.invalid",
        )

        assert result["passed"] is True
        assert result["learned_maximum_interval_span"] == 1_954
        assert client.http_attempts == 17
        range_queries = [
            cast(list[dict[str, str]], request["params"])[0]
            for _, request in transport.calls
            if request["method"] == "eth_getLogs"
            and cast(list[dict[str, str]], request["params"])[0]["toBlock"] != "0x0"
        ]
        assert range_queries[-1]["toBlock"] == "0x7a1"


def test_http_403_is_terminal_and_never_bisected() -> None:
    def handler(_url: str, request: Mapping[str, object]) -> HttpObservation:
        if request["method"] == "eth_chainId":
            return _rpc_result(request, "0x2a")
        query = cast(list[dict[str, str]], request["params"])[0]
        if query["toBlock"] == "0x0":
            return _rpc_result(request, [])
        return HttpObservation(status=403, body=b"forbidden")

    client = _client(FakeTransport(handler))
    result = probe_repair_endpoint(
        client,
        deployment="synthetic",
        expected_chain_id="0x2a",
        endpoint_role="repair",
        url="https://rpc.invalid",
    )

    assert result["passed"] is False
    assert result["failure_stage"] == "range_terminal_error"
    assert len(client.records) == 3
    assert client.http_attempts == 4


def test_http_400_on_single_block_is_terminal() -> None:
    def handler(_url: str, request: Mapping[str, object]) -> HttpObservation:
        if request["method"] == "eth_chainId":
            return _rpc_result(request, "0x2a")
        return HttpObservation(status=400, body=b"single failure")

    client = _client(FakeTransport(handler))
    result = probe_repair_endpoint(
        client,
        deployment="synthetic",
        expected_chain_id="0x2a",
        endpoint_role="repair",
        url="https://rpc.invalid",
    )

    assert result["passed"] is False
    assert result["failure_stage"] == "single_block_empty_log"
    assert len(client.records) == 2


def test_rpc_range_error_is_bisected_but_nonempty_rows_are_discarded() -> None:
    def range_handler(_url: str, request: Mapping[str, object]) -> HttpObservation:
        if request["method"] == "eth_chainId":
            return _rpc_result(request, "0x2a")
        query = cast(list[dict[str, str]], request["params"])[0]
        if int(query["toBlock"], 16) + 1 > 62_500:
            return _rpc_error(request, "range too wide")
        return _rpc_result(request, [])

    passed = probe_repair_endpoint(
        _client(FakeTransport(range_handler)),
        deployment="synthetic",
        expected_chain_id="0x2a",
        endpoint_role="repair",
        url="https://rpc.invalid",
    )
    assert passed["passed"] is True
    assert passed["learned_maximum_interval_span"] == 62_500

    def contaminated(_url: str, request: Mapping[str, object]) -> HttpObservation:
        if request["method"] == "eth_chainId":
            return _rpc_result(request, "0x2a")
        return _rpc_result(request, [{"forbidden_row": "discard-me"}])

    client = _client(FakeTransport(contaminated))
    failed = probe_repair_endpoint(
        client,
        deployment="synthetic",
        expected_chain_id="0x2a",
        endpoint_role="repair",
        url="https://rpc.invalid",
    )
    assert failed["passed"] is False
    assert failed["failure_stage"] == "single_block_empty_log"
    assert "discard-me" not in json.dumps(client.records)


def _sealed_host_result(host_id: str, *, failed_deployment: str | None = None) -> dict[str, object]:
    chain_ids = {url: chain_id for _, chain_id, _, url, _ in EXPECTED_REPAIRS}

    def handler(url: str, request: Mapping[str, object]) -> HttpObservation:
        if request["method"] == "eth_chainId":
            expected = chain_ids[url]
            deployment = next(name for name, _, _, endpoint, _ in EXPECTED_REPAIRS if endpoint == url)
            return _rpc_result(request, "0xdead" if deployment == failed_deployment else expected)
        return _rpc_result(request, [])

    client = _client(FakeTransport(handler))
    endpoint_results = [
        probe_repair_endpoint(
            client,
            deployment=name,
            expected_chain_id=chain_id,
            endpoint_role=role,
            url=url,
        )
        for name, chain_id, role, url, _ in EXPECTED_REPAIRS
    ]
    passing = sorted(cast(str, item["deployment"]) for item in endpoint_results if item["passed"] is True)
    complete = len(passing) == len(EXPECTED_REPAIRS)
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "host_id": host_id,
        "runtime": {"gpu_visible": False},
        "protocol_commit": PROTOCOL_COMMIT,
        "manifest_sha256": MANIFEST_SHA,
        "source_sha256": SOURCE_SHA,
        "canary_address": ZERO_ADDRESS,
        "inherited_deployments": list(V1_REQUIRED_PASSING),
        "endpoint_results": endpoint_results,
        "passing_repairs": passing,
        "request_ledger": client.records,
        "resource_use": {
            "logical_request_count": len(client.records),
            "http_attempt_count": client.http_attempts,
            "response_byte_count": client.response_bytes,
            "http_attempt_cap": 100,
            "response_byte_cap": 8_388_608,
        },
        "target_row_count_retained": 0,
        "raw_response_payloads_retained": False,
        "decision": PASS_DECISION if complete else FAIL_DECISION,
    }


def test_aggregate_requires_both_hosts_and_uses_frozen_priority() -> None:
    manifest = load_json(MANIFEST_PATH)
    results = {
        "rtx2060": _sealed_host_result("rtx2060"),
        "local_mac": _sealed_host_result("local_mac"),
    }
    hashes = {host_id: "a" * 64 for host_id in HOST_PRIORITY}

    summary = aggregate_results(
        manifest,
        host_results=results,
        host_artifact_hashes=hashes,
        protocol_commit=PROTOCOL_COMMIT,
        manifest_sha256=MANIFEST_SHA,
        source_sha256=SOURCE_SHA,
    )

    assert summary["decision"] == PASS_DECISION
    assert summary["selected_host"] == "rtx2060"
    selected = cast(list[dict[str, object]], summary["selected_endpoints"])
    assert [item["deployment"] for item in selected] == [
        "arbitrum",
        "avalanche",
        "optimism",
        "polygon",
        "base",
        "gnosis",
        "bnb",
        "linea",
        "scroll",
    ]
    assert len(selected) == 9

    missing = dict(results)
    del missing["local_mac"]
    incomplete = aggregate_results(
        manifest,
        host_results=missing,
        host_artifact_hashes=hashes,
        protocol_commit=PROTOCOL_COMMIT,
        manifest_sha256=MANIFEST_SHA,
        source_sha256=SOURCE_SHA,
    )
    assert incomplete["decision"] == FAIL_DECISION
    assert incomplete["selected_host"] is None


def test_aggregate_rejects_tampered_address_and_selects_second_host() -> None:
    manifest = load_json(MANIFEST_PATH)
    results = {
        "rtx2060": _sealed_host_result("rtx2060", failed_deployment="bnb"),
        "local_mac": _sealed_host_result("local_mac"),
    }
    hashes = {host_id: hashlib.sha256(host_id.encode()).hexdigest() for host_id in HOST_PRIORITY}
    summary = aggregate_results(
        manifest,
        host_results=results,
        host_artifact_hashes=hashes,
        protocol_commit=PROTOCOL_COMMIT,
        manifest_sha256=MANIFEST_SHA,
        source_sha256=SOURCE_SHA,
    )
    assert summary["decision"] == PASS_DECISION
    assert summary["selected_host"] == "local_mac"

    tampered = deepcopy(results)
    ledger = cast(list[dict[str, object]], tampered["local_mac"]["request_ledger"])
    log_record = next(record for record in ledger if record["method"] == "eth_getLogs")
    cast(list[dict[str, str]], log_record["params"])[0]["address"] = "0x" + "ff" * 20
    rejected = aggregate_results(
        manifest,
        host_results=tampered,
        host_artifact_hashes=hashes,
        protocol_commit=PROTOCOL_COMMIT,
        manifest_sha256=MANIFEST_SHA,
        source_sha256=SOURCE_SHA,
    )
    assert rejected["decision"] == FAIL_DECISION
    assert rejected["selected_host"] is None
    assert any("non-canary log params" in item for item in cast(list[str], rejected["validation_errors"]))

    status_tampered = deepcopy(results)
    status_ledger = cast(list[dict[str, object]], status_tampered["local_mac"]["request_ledger"])
    attempts = cast(list[dict[str, object]], status_ledger[0]["attempts"])
    attempts[-1]["http_status"] = 500
    status_rejected = aggregate_results(
        manifest,
        host_results=status_tampered,
        host_artifact_hashes=hashes,
        protocol_commit=PROTOCOL_COMMIT,
        manifest_sha256=MANIFEST_SHA,
        source_sha256=SOURCE_SHA,
    )
    assert status_rejected["decision"] == FAIL_DECISION
    assert any(
        "JSON outcome lacks a successful final HTTP attempt" in item
        for item in cast(list[str], status_rejected["validation_errors"])
    )
