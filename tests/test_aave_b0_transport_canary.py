from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from copy import deepcopy
from pathlib import Path
from typing import cast

import pytest

from ecomd.research.aave_b0_transport_canary import (
    ARTIFACT_SCHEMA_VERSION,
    AUDIT_ID,
    EXPECTED_ENDPOINTS,
    FAIL_DECISION,
    HOST_PRIORITY,
    PASS_DECISION,
    ZERO_ADDRESS,
    HttpObservation,
    ProbeClient,
    aggregate_results,
    load_json,
    probe_endpoint,
    validate_manifest,
    validate_parent_files,
)

MANIFEST_PATH = Path("data/manifests/aave_v3_b0_transport_canary_v1.json")
PROTOCOL_COMMIT = "1" * 40
MANIFEST_SHA = "2" * 64
SOURCE_SHA = "3" * 64


class FakeTransport:
    def __init__(self, handler: Callable[[Mapping[str, object]], HttpObservation]) -> None:
        self.handler = handler
        self.calls: list[dict[str, object]] = []

    def __call__(self, url: str, body: bytes, headers: Mapping[str, str], timeout: float) -> HttpObservation:
        del url, headers, timeout
        request = cast(dict[str, object], json.loads(body))
        self.calls.append(request)
        return self.handler(request)


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
        maximum_response_bytes=1_000_000,
        timeout_seconds=1,
        user_agent="test",
    )


def test_manifest_and_v1_failure_parents_are_valid() -> None:
    manifest = load_json(MANIFEST_PATH)

    assert validate_manifest(manifest) == []
    assert validate_parent_files(manifest, Path.cwd()) == []

    changed = deepcopy(manifest)
    cast(dict[str, object], changed["canary"])["address"] = "0x" + "ff" * 20
    assert "canary query contract differs from the frozen empty-address values" in validate_manifest(changed)


def test_duplicate_json_keys_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.json"
    path.write_text('{"key": 1, "key": 2}', encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate JSON key"):
        load_json(path)


def test_endpoint_canary_passes_direct_empty_root() -> None:
    def handler(request: Mapping[str, object]) -> HttpObservation:
        if request["method"] == "eth_chainId":
            return _rpc_result(request, "0x2a")
        return _rpc_result(request, [])

    transport = FakeTransport(handler)
    result = probe_endpoint(
        _client(transport),
        deployment="synthetic",
        expected_chain_id="0x2a",
        endpoint_role="primary",
        url="https://rpc.invalid",
    )

    assert result["passed"] is True
    assert result["learned_maximum_interval_span"] == 250_000
    assert len(transport.calls) == 3
    query = cast(list[dict[str, str]], transport.calls[-1]["params"])[0]
    assert query == {"address": ZERO_ADDRESS, "fromBlock": "0x0", "toBlock": "0x3d08f"}


def test_endpoint_canary_learns_range_only_from_rpc_errors() -> None:
    def handler(request: Mapping[str, object]) -> HttpObservation:
        if request["method"] == "eth_chainId":
            return _rpc_result(request, "0x2a")
        query = cast(list[dict[str, str]], request["params"])[0]
        span = int(query["toBlock"], 16) + 1
        if span > 62_500:
            return _rpc_error(request, "range too wide")
        return _rpc_result(request, [])

    transport = FakeTransport(handler)
    result = probe_endpoint(
        _client(transport),
        deployment="synthetic",
        expected_chain_id="0x2a",
        endpoint_role="primary",
        url="https://rpc.invalid",
    )

    assert result["passed"] is True
    assert result["learned_maximum_interval_span"] == 62_500
    assert len(transport.calls) == 5


def test_http_403_is_retried_then_fails_without_range_bisection() -> None:
    def handler(request: Mapping[str, object]) -> HttpObservation:
        if request["method"] == "eth_chainId":
            return _rpc_result(request, "0x2a")
        return HttpObservation(status=403, body=b"forbidden")

    transport = FakeTransport(handler)
    client = _client(transport)
    result = probe_endpoint(
        client,
        deployment="synthetic",
        expected_chain_id="0x2a",
        endpoint_role="primary",
        url="https://rpc.invalid",
    )

    assert result["passed"] is False
    assert result["failure_stage"] == "single_block_empty_log"
    assert len(client.records) == 2
    assert client.http_attempts == 3
    assert len(transport.calls) == 3


def test_nonempty_zero_address_result_fails_without_retaining_rows() -> None:
    def handler(request: Mapping[str, object]) -> HttpObservation:
        if request["method"] == "eth_chainId":
            return _rpc_result(request, "0x2a")
        return _rpc_result(request, [{"forbidden_row": "discard-me"}])

    client = _client(FakeTransport(handler))
    result = probe_endpoint(
        client,
        deployment="synthetic",
        expected_chain_id="0x2a",
        endpoint_role="primary",
        url="https://rpc.invalid",
    )

    assert result["passed"] is False
    assert result["failure_stage"] == "single_block_empty_log"
    assert cast(dict[str, object], client.records[-1]["outcome"])["log_count"] == 1
    assert "discard-me" not in json.dumps(client.records)


def _host_result(host_id: str, *, passed: bool) -> dict[str, object]:
    endpoint_results: list[dict[str, object]] = []
    ledger: list[dict[str, object]] = []

    def add_record(
        *,
        deployment: str,
        role: str,
        url: str,
        method: str,
        params: list[object],
        outcome: dict[str, object],
    ) -> int:
        request_id = len(ledger) + 1
        request = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        ledger.append(
            {
                "logical_request_index": len(ledger),
                "request_id": request_id,
                "deployment": deployment,
                "endpoint_role": role,
                "url": url,
                "label": "synthetic",
                "method": method,
                "params": params,
                "request_sha256": hashlib.sha256(
                    json.dumps(request, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest(),
                "attempts": [
                    {
                        "attempt_number": 1,
                        "http_status": 200,
                        "response_byte_count": 0,
                        "response_body_sha256": hashlib.sha256(b"").hexdigest(),
                        "transport_error": None,
                    }
                ],
                "outcome": outcome,
            }
        )
        return len(ledger) - 1

    for name, chain_id, primary, replica in EXPECTED_ENDPOINTS:
        for role, url in (("primary", primary), ("replica", replica)):
            endpoint_pass = passed and role == "replica"
            indices = [
                add_record(
                    deployment=name,
                    role=role,
                    url=url,
                    method="eth_chainId",
                    params=[],
                    outcome={
                        "kind": "scalar_result",
                        "value": chain_id if endpoint_pass else "0xdead",
                    },
                )
            ]
            if endpoint_pass:
                indices.append(
                    add_record(
                        deployment=name,
                        role=role,
                        url=url,
                        method="eth_getLogs",
                        params=[{"address": ZERO_ADDRESS, "fromBlock": "0x0", "toBlock": "0x0"}],
                        outcome={"kind": "log_list_result", "log_count": 0},
                    )
                )
                indices.append(
                    add_record(
                        deployment=name,
                        role=role,
                        url=url,
                        method="eth_getLogs",
                        params=[
                            {
                                "address": ZERO_ADDRESS,
                                "fromBlock": "0x0",
                                "toBlock": "0xf423",
                            }
                        ],
                        outcome={"kind": "log_list_result", "log_count": 0},
                    )
                )
            endpoint_results.append(
                {
                    "deployment": name,
                    "endpoint_role": role,
                    "url": url,
                    "chain_identity_passed": endpoint_pass,
                    "single_block_empty_passed": endpoint_pass,
                    "range_empty_passed": endpoint_pass,
                    "learned_maximum_interval_span": 62_500 if endpoint_pass else None,
                    "failure_stage": None if endpoint_pass else "chain_identity",
                    "logical_request_indices": indices,
                    "passed": endpoint_pass,
                }
            )
    passing = sorted(item[0] for item in EXPECTED_ENDPOINTS) if passed else []
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "host_id": host_id,
        "runtime": {"gpu_visible": False},
        "protocol_commit": PROTOCOL_COMMIT,
        "manifest_sha256": MANIFEST_SHA,
        "source_sha256": SOURCE_SHA,
        "canary_address": ZERO_ADDRESS,
        "endpoint_results": endpoint_results,
        "passing_deployments": passing,
        "request_ledger": ledger,
        "resource_use": {
            "logical_request_count": len(ledger),
            "http_attempt_count": len(ledger),
            "response_byte_count": 0,
            "http_attempt_cap": 500,
            "response_byte_cap": 33_554_432,
        },
        "target_row_count_retained": 0,
        "raw_response_payloads_retained": False,
        "decision": PASS_DECISION if passed else FAIL_DECISION,
    }


def test_aggregate_waits_for_all_hosts_and_uses_frozen_priority() -> None:
    manifest = load_json(MANIFEST_PATH)
    results = {host_id: _host_result(host_id, passed=host_id != "v100_a") for host_id in HOST_PRIORITY}
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
    assert summary["selected_host"] == "v100_b"
    selected = cast(list[dict[str, object]], summary["selected_endpoints"])
    assert len(selected) == 9
    assert {item["endpoint_role"] for item in selected} == {"replica"}

    incomplete = dict(results)
    del incomplete["local_mac"]
    failed = aggregate_results(
        manifest,
        host_results=incomplete,
        host_artifact_hashes=hashes,
        protocol_commit=PROTOCOL_COMMIT,
        manifest_sha256=MANIFEST_SHA,
        source_sha256=SOURCE_SHA,
    )
    assert failed["decision"] == FAIL_DECISION
    assert failed["selected_host"] is None

    tampered = deepcopy(results)
    tampered_ledger = cast(list[dict[str, object]], tampered["v100_b"]["request_ledger"])
    first_log = next(record for record in tampered_ledger if record["method"] == "eth_getLogs")
    cast(list[dict[str, str]], first_log["params"])[0]["address"] = "0x" + "ff" * 20
    rejected = aggregate_results(
        manifest,
        host_results=tampered,
        host_artifact_hashes=hashes,
        protocol_commit=PROTOCOL_COMMIT,
        manifest_sha256=MANIFEST_SHA,
        source_sha256=SOURCE_SHA,
    )
    assert rejected["decision"] == FAIL_DECISION
    assert any("non-canary log params" in item for item in cast(list[str], rejected["validation_errors"]))
