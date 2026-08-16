"""Target-row-free transport canary for the Aave V3 B0 repair."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

SCHEMA_VERSION = "ecophys-aave-v3-b0-transport-canary/v1"
ARTIFACT_SCHEMA_VERSION = "ecophys-aave-v3-b0-transport-canary-audit/v1"
AUDIT_ID = "aave_v3_b0_transport_canary_v1"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
HEX_SHA_PATTERN = re.compile(r"[0-9a-f]{64}")
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")

EXPECTED_PARENTS: dict[str, object] = {
    "b0_v1_archive_commit": "da29a8e0ec9f7c318eafccc5c1aee571ff9d700e",
    "b0_v1_protocol_commit": "7079562919b039f69927a916ccc08281e1d2462b",
    "b0_v1_manifest_path": "data/manifests/aave_v3_cross_deployment_program_directory_v1.yaml",
    "b0_v1_manifest_sha256": "1136d03e39fdc4e518f6f77b71a8929e579b31ca2979c50caadf874e7f9dedb1",
    "b0_v1_result_path": "experiments/v14_aave_v3_cross_deployment_program_directory/RESULTS_V1.md",
    "b0_v1_result_sha256": "9aa6fe25ea25f98e7f15bde2cdd0d6269120221eae8c65ffacc65aba6b939aa1",
    "b0_v1_failure_path": (
        "experiments/v14_aave_v3_cross_deployment_program_directory/artifacts/failure.json"
    ),
    "b0_v1_failure_sha256": "714c3ed29acd92df19fab1b1eedadc52c46f61db321f13756284b0b35ceeffdf",
    "b0_v1_ledger_path": (
        "experiments/v14_aave_v3_cross_deployment_program_directory/artifacts/rpc_response_hashes.json"
    ),
    "b0_v1_ledger_sha256": "0784cb7bf2383f4b4df20d6754265cea3e3dd5eb022ab7ae654360b9d2c987d8",
    "expected_b0_v1_decision": "INFRASTRUCTURE_FAILURE_NO_B0_SCIENTIFIC_DECISION",
}

EXPECTED_ENDPOINTS: tuple[tuple[str, str, str, str], ...] = (
    (
        "arbitrum",
        "0xa4b1",
        "https://arbitrum-one-rpc.publicnode.com",
        "https://arb1.arbitrum.io/rpc",
    ),
    (
        "avalanche",
        "0xa86a",
        "https://avalanche-c-chain-rpc.publicnode.com",
        "https://api.avax.network/ext/bc/C/rpc",
    ),
    (
        "optimism",
        "0xa",
        "https://optimism-rpc.publicnode.com",
        "https://mainnet.optimism.io",
    ),
    (
        "polygon",
        "0x89",
        "https://polygon-bor-rpc.publicnode.com",
        "https://polygon.drpc.org",
    ),
    (
        "base",
        "0x2105",
        "https://base-rpc.publicnode.com",
        "https://mainnet.base.org",
    ),
    (
        "gnosis",
        "0x64",
        "https://gnosis-rpc.publicnode.com",
        "https://rpc.gnosischain.com",
    ),
    (
        "bnb",
        "0x38",
        "https://bsc-rpc.publicnode.com",
        "https://bsc-dataseed.bnbchain.org",
    ),
    (
        "linea",
        "0xe708",
        "https://linea-rpc.publicnode.com",
        "https://rpc.linea.build",
    ),
    (
        "scroll",
        "0x82750",
        "https://scroll-rpc.publicnode.com",
        "https://rpc.scroll.io",
    ),
)

HOST_PRIORITY = ("v100_a", "v100_b", "rtx2060", "local_mac")
ALLOWED_METHODS = frozenset({"eth_chainId", "eth_getLogs"})
PASS_DECISION = "PASS_TARGET_ROW_FREE_TRANSPORT_CANARY_AUTHORIZE_B0_V2_PROTOCOL_DESIGN_ONLY"
FAIL_DECISION = "FAIL_TARGET_ROW_FREE_TRANSPORT_CANARY_KEEP_B0_V2_B1_G1_GPU_LOCKED"


class DuplicateKeyError(ValueError):
    """Raised when a JSON object repeats a key."""


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: str | Path) -> dict[str, object]:
    """Load a JSON mapping while rejecting duplicate keys."""

    value: object = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return cast(dict[str, object], value)


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 of one file."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _sequence(value: object) -> Sequence[object] | None:
    if isinstance(value, str) or not isinstance(value, Sequence):
        return None
    return cast(Sequence[object], value)


def _expected_deployments() -> list[dict[str, object]]:
    return [
        {
            "name": name,
            "chain_id_hex": chain_id,
            "endpoints": [
                {"role": "primary", "url": primary},
                {"role": "replica", "url": replica},
            ],
        }
        for name, chain_id, primary, replica in EXPECTED_ENDPOINTS
    ]


def validate_manifest(manifest: Mapping[str, object]) -> list[str]:
    """Validate the complete target-free transport contract."""

    errors: list[str] = []
    expected_root_keys = {
        "schema_version",
        "audit_id",
        "as_of",
        "stage",
        "parents",
        "scientific_contract",
        "canary",
        "hosts",
        "selection_policy",
        "rpc",
        "deployments",
        "decision_policy",
    }
    if set(manifest) != expected_root_keys:
        errors.append("manifest root keys differ from the frozen contract")
    if manifest.get("schema_version") != SCHEMA_VERSION or manifest.get("audit_id") != AUDIT_ID:
        errors.append("schema or audit ID differs from the frozen contract")
    if manifest.get("as_of") != "2026-08-17" or manifest.get("stage") != (
        "target_row_free_rpc_transport_canary"
    ):
        errors.append("date or stage differs from the frozen contract")
    if manifest.get("parents") != EXPECTED_PARENTS:
        errors.append("parents differ from the frozen B0 v1 failure contract")
    expected_science = {
        "deployment_universe_unchanged": True,
        "deployment_split_unchanged": True,
        "cutoff_unchanged": True,
        "program_inclusion_rule_unchanged": True,
        "support_thresholds_unchanged": True,
        "scientific_resource_caps_unchanged": True,
        "target_addresses_forbidden": True,
        "target_event_rows_forbidden": True,
        "b0_v2_execution_not_authorized": True,
    }
    if manifest.get("scientific_contract") != expected_science:
        errors.append("scientific inheritance contract differs from the frozen values")
    expected_canary = {
        "address": ZERO_ADDRESS,
        "expected_log_count": 0,
        "single_block_interval": [0, 0],
        "root_interval": [0, 249_999],
        "range_error_action": "bisect_left_prefix_until_empty_success_or_single_block_failure",
        "http_error_action": "retry_then_fail_without_bisection",
        "nonempty_result_action": "contamination_fail_discard_rows",
        "allowed_methods": ["eth_chainId", "eth_getLogs"],
    }
    if manifest.get("canary") != expected_canary:
        errors.append("canary query contract differs from the frozen empty-address values")
    expected_hosts = {
        "priority": list(HOST_PRIORITY),
        "all_hosts_must_report_before_selection": True,
        "gpu_visible": False,
        "host_ids_are_bound_to_gitignored_local_inventory": True,
    }
    if manifest.get("hosts") != expected_hosts:
        errors.append("host contract differs from the frozen values")
    expected_selection = {
        "single_host_required_for_all_deployments": True,
        "select_first_passing_host_by_frozen_priority": True,
        "within_selected_host_prefer_primary_then_replica_per_deployment": True,
        "no_partial_host_or_target_result_selection": True,
    }
    if manifest.get("selection_policy") != expected_selection:
        errors.append("selection policy differs from the frozen values")
    expected_rpc = {
        "maximum_requests_per_second_per_host": 2,
        "maximum_attempts_per_logical_call": 2,
        "maximum_http_attempts_per_host": 500,
        "maximum_response_bytes_per_host": 33_554_432,
        "timeout_seconds": 30,
        "user_agent": "EcoPhys-V14-Aave-B0-transport-canary/1.0",
        "raw_response_payloads_retained": False,
    }
    if manifest.get("rpc") != expected_rpc:
        errors.append("RPC contract differs from the frozen values")
    if manifest.get("deployments") != _expected_deployments():
        errors.append("deployment endpoint candidates differ from the frozen order")
    expected_decision = {
        "pass": PASS_DECISION,
        "fail": FAIL_DECISION,
        "all_hosts_required": True,
        "authorized_next_stage": "scientific_contract_preserving_b0_v2_protocol_design_only",
    }
    if manifest.get("decision_policy") != expected_decision:
        errors.append("decision policy differs from the frozen values")
    return errors


def validate_parent_files(manifest: Mapping[str, object], root: str | Path) -> list[str]:
    """Hash-check the immutable v1 failure parents without importing its collector."""

    parents = _mapping(manifest.get("parents"))
    if parents is None:
        return ["parents must be a mapping"]
    errors: list[str] = []
    root_path = Path(root)
    for path_key, hash_key in (
        ("b0_v1_manifest_path", "b0_v1_manifest_sha256"),
        ("b0_v1_result_path", "b0_v1_result_sha256"),
        ("b0_v1_failure_path", "b0_v1_failure_sha256"),
        ("b0_v1_ledger_path", "b0_v1_ledger_sha256"),
    ):
        relative = parents.get(path_key)
        expected_hash = parents.get(hash_key)
        if not isinstance(relative, str) or not isinstance(expected_hash, str):
            errors.append(f"invalid parent identity fields: {path_key}/{hash_key}")
            continue
        target = root_path / relative
        if not target.is_file():
            errors.append(f"missing parent file: {relative}")
        elif sha256_file(target) != expected_hash:
            errors.append(f"parent hash mismatch: {relative}")
    result_path = parents.get("b0_v1_result_path")
    if isinstance(result_path, str) and (root_path / result_path).is_file():
        text = (root_path / result_path).read_text(encoding="utf-8")
        if cast(str, parents["expected_b0_v1_decision"]) not in text:
            errors.append("B0 v1 result decision differs from the frozen failure")
    return errors


@dataclass(frozen=True)
class HttpObservation:
    """One bounded HTTP observation before JSON normalization."""

    status: int | None
    body: bytes
    transport_error: str | None = None


Transport = Callable[[str, bytes, Mapping[str, str], float], HttpObservation]


def urllib_transport(url: str, body: bytes, headers: Mapping[str, str], timeout: float) -> HttpObservation:
    """POST one JSON-RPC request and retain only the returned bytes in memory."""

    request = urllib.request.Request(url, data=body, headers=dict(headers), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return HttpObservation(status=response.status, body=response.read())
    except urllib.error.HTTPError as exc:
        return HttpObservation(status=exc.code, body=exc.read())
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return HttpObservation(
            status=None,
            body=b"",
            transport_error=f"{type(exc).__name__}: {exc}",
        )


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


class ProbeClient:
    """Globally rate-limited target-free JSON-RPC probe with a hash-only ledger."""

    def __init__(
        self,
        *,
        transport: Transport,
        maximum_requests_per_second: float,
        maximum_attempts_per_logical_call: int,
        maximum_http_attempts: int,
        maximum_response_bytes: int,
        timeout_seconds: float,
        user_agent: str,
    ) -> None:
        self._transport = transport
        self._minimum_interval = 1.0 / maximum_requests_per_second
        self._maximum_attempts_per_logical_call = maximum_attempts_per_logical_call
        self._maximum_http_attempts = maximum_http_attempts
        self._maximum_response_bytes = maximum_response_bytes
        self._timeout_seconds = timeout_seconds
        self._headers = {"Content-Type": "application/json", "User-Agent": user_agent}
        self._last_start: float | None = None
        self._next_id = 1
        self.http_attempts = 0
        self.response_bytes = 0
        self.records: list[dict[str, object]] = []

    def call(
        self,
        *,
        deployment: str,
        endpoint_role: str,
        url: str,
        label: str,
        method: str,
        params: Sequence[object],
    ) -> dict[str, object]:
        """Execute one logical canary request and normalize no event row."""

        if method not in ALLOWED_METHODS:
            raise ValueError(f"forbidden canary method: {method}")
        request_id = self._next_id
        self._next_id += 1
        request = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": list(params)}
        body = _canonical_bytes(request)
        attempts: list[dict[str, object]] = []
        outcome: dict[str, object] | None = None
        for _ in range(self._maximum_attempts_per_logical_call):
            if self.http_attempts >= self._maximum_http_attempts:
                raise RuntimeError("maximum canary HTTP-attempt cap reached")
            if self._last_start is not None:
                time.sleep(max(0.0, self._minimum_interval - (time.monotonic() - self._last_start)))
            self._last_start = time.monotonic()
            self.http_attempts += 1
            observation = self._transport(url, body, self._headers, self._timeout_seconds)
            self.response_bytes += len(observation.body)
            if self.response_bytes > self._maximum_response_bytes:
                raise RuntimeError("maximum canary response-byte cap reached")
            attempt: dict[str, object] = {
                "attempt_number": len(attempts) + 1,
                "http_status": observation.status,
                "response_byte_count": len(observation.body),
                "response_body_sha256": hashlib.sha256(observation.body).hexdigest(),
                "transport_error": observation.transport_error,
            }
            attempts.append(attempt)
            if observation.transport_error is not None or observation.status != 200:
                outcome = {
                    "kind": "http_or_transport_failure",
                    "http_status": observation.status,
                    "transport_error": observation.transport_error,
                }
                continue
            try:
                envelope_value: object = json.loads(
                    observation.body.decode("utf-8"), object_pairs_hook=_unique_object
                )
            except (UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
                outcome = {"kind": "invalid_json", "detail": f"{type(exc).__name__}: {exc}"}
                continue
            envelope = _mapping(envelope_value)
            if envelope is None or envelope.get("jsonrpc") != "2.0" or envelope.get("id") != request_id:
                outcome = {"kind": "invalid_envelope"}
                continue
            error = _mapping(envelope.get("error"))
            if error is not None:
                message = error.get("message")
                outcome = {
                    "kind": "rpc_error",
                    "code": error.get("code"),
                    "message": str(message)[:500],
                }
                break
            if "result" not in envelope:
                outcome = {"kind": "invalid_envelope"}
                continue
            result = envelope["result"]
            if method == "eth_chainId" and isinstance(result, str):
                outcome = {"kind": "scalar_result", "value": result}
                break
            if method == "eth_getLogs" and isinstance(result, list):
                outcome = {"kind": "log_list_result", "log_count": len(result)}
                break
            outcome = {"kind": "invalid_result_type", "type": type(result).__name__}
        if outcome is None:
            last = attempts[-1]
            outcome = {
                "kind": "http_or_transport_failure",
                "http_status": last["http_status"],
                "transport_error": last["transport_error"],
            }
        record = {
            "logical_request_index": len(self.records),
            "request_id": request_id,
            "deployment": deployment,
            "endpoint_role": endpoint_role,
            "url": url,
            "label": label,
            "method": method,
            "params": list(params),
            "request_sha256": hashlib.sha256(body).hexdigest(),
            "attempts": attempts,
            "outcome": outcome,
        }
        self.records.append(record)
        return outcome


def _empty_log_outcome(outcome: Mapping[str, object]) -> bool:
    return outcome.get("kind") == "log_list_result" and outcome.get("log_count") == 0


def probe_endpoint(
    client: ProbeClient,
    *,
    deployment: str,
    expected_chain_id: str,
    endpoint_role: str,
    url: str,
    root_to_block: int = 249_999,
) -> dict[str, object]:
    """Probe chain identity, an empty single block, and a left-prefix range."""

    first_record = len(client.records)
    chain = client.call(
        deployment=deployment,
        endpoint_role=endpoint_role,
        url=url,
        label="chain_id",
        method="eth_chainId",
        params=[],
    )
    chain_passed = chain.get("kind") == "scalar_result" and chain.get("value") == expected_chain_id
    if not chain_passed:
        return {
            "deployment": deployment,
            "endpoint_role": endpoint_role,
            "url": url,
            "chain_identity_passed": False,
            "single_block_empty_passed": False,
            "range_empty_passed": False,
            "learned_maximum_interval_span": None,
            "failure_stage": "chain_identity",
            "logical_request_indices": list(range(first_record, len(client.records))),
            "passed": False,
        }
    single = client.call(
        deployment=deployment,
        endpoint_role=endpoint_role,
        url=url,
        label="empty_zero_address_single_block:0-0",
        method="eth_getLogs",
        params=[{"address": ZERO_ADDRESS, "fromBlock": "0x0", "toBlock": "0x0"}],
    )
    if not _empty_log_outcome(single):
        return {
            "deployment": deployment,
            "endpoint_role": endpoint_role,
            "url": url,
            "chain_identity_passed": True,
            "single_block_empty_passed": False,
            "range_empty_passed": False,
            "learned_maximum_interval_span": None,
            "failure_stage": "single_block_empty_log",
            "logical_request_indices": list(range(first_record, len(client.records))),
            "passed": False,
        }
    interval_to = root_to_block
    learned_span: int | None = None
    range_failure = "range_empty_log"
    while True:
        outcome = client.call(
            deployment=deployment,
            endpoint_role=endpoint_role,
            url=url,
            label=f"empty_zero_address_range:0-{interval_to}",
            method="eth_getLogs",
            params=[
                {
                    "address": ZERO_ADDRESS,
                    "fromBlock": "0x0",
                    "toBlock": hex(interval_to),
                }
            ],
        )
        if _empty_log_outcome(outcome):
            learned_span = interval_to + 1
            break
        if outcome.get("kind") != "rpc_error" or interval_to == 0:
            range_failure = "range_non_rpc_or_single_block_failure"
            break
        interval_to //= 2
    passed = learned_span is not None
    return {
        "deployment": deployment,
        "endpoint_role": endpoint_role,
        "url": url,
        "chain_identity_passed": True,
        "single_block_empty_passed": True,
        "range_empty_passed": passed,
        "learned_maximum_interval_span": learned_span,
        "failure_stage": None if passed else range_failure,
        "logical_request_indices": list(range(first_record, len(client.records))),
        "passed": passed,
    }


def _new_client(manifest: Mapping[str, object], transport: Transport) -> ProbeClient:
    rpc = cast(Mapping[str, object], manifest["rpc"])
    return ProbeClient(
        transport=transport,
        maximum_requests_per_second=float(cast(int, rpc["maximum_requests_per_second_per_host"])),
        maximum_attempts_per_logical_call=cast(int, rpc["maximum_attempts_per_logical_call"]),
        maximum_http_attempts=cast(int, rpc["maximum_http_attempts_per_host"]),
        maximum_response_bytes=cast(int, rpc["maximum_response_bytes_per_host"]),
        timeout_seconds=float(cast(int, rpc["timeout_seconds"])),
        user_agent=cast(str, rpc["user_agent"]),
    )


def run_host_canary(
    manifest: Mapping[str, object],
    *,
    host_id: str,
    protocol_commit: str,
    manifest_sha256: str,
    source_sha256: str,
    transport: Transport = urllib_transport,
) -> dict[str, object]:
    """Run all frozen endpoint candidates on one predeclared host."""

    errors = validate_manifest(manifest)
    if errors:
        raise ValueError("invalid transport manifest: " + "; ".join(errors))
    if host_id not in HOST_PRIORITY:
        raise ValueError(f"unknown host ID: {host_id}")
    if COMMIT_PATTERN.fullmatch(protocol_commit) is None:
        raise ValueError("protocol commit must be a lowercase 40-hex Git SHA")
    if HEX_SHA_PATTERN.fullmatch(manifest_sha256) is None or HEX_SHA_PATTERN.fullmatch(source_sha256) is None:
        raise ValueError("manifest and source hashes must be lowercase SHA-256 values")
    started = datetime.now(UTC)
    client = _new_client(manifest, transport)
    endpoint_results: list[dict[str, object]] = []
    deployments = cast(Sequence[Mapping[str, object]], manifest["deployments"])
    for deployment in deployments:
        endpoints = cast(Sequence[Mapping[str, object]], deployment["endpoints"])
        for endpoint in endpoints:
            endpoint_results.append(
                probe_endpoint(
                    client,
                    deployment=cast(str, deployment["name"]),
                    expected_chain_id=cast(str, deployment["chain_id_hex"]),
                    endpoint_role=cast(str, endpoint["role"]),
                    url=cast(str, endpoint["url"]),
                )
            )
    passing_deployments = {
        name
        for name, _, _, _ in EXPECTED_ENDPOINTS
        if any(item["deployment"] == name and item["passed"] is True for item in endpoint_results)
    }
    passed = passing_deployments == {item[0] for item in EXPECTED_ENDPOINTS}
    ended = datetime.now(UTC)
    rpc = cast(Mapping[str, object], manifest["rpc"])
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "host_id": host_id,
        "runtime": {
            "hostname": platform.node(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "gpu_visible": False,
        },
        "protocol_commit": protocol_commit,
        "manifest_sha256": manifest_sha256,
        "source_sha256": source_sha256,
        "started_at_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_at_utc": ended.isoformat().replace("+00:00", "Z"),
        "canary_address": ZERO_ADDRESS,
        "endpoint_results": endpoint_results,
        "passing_deployments": sorted(passing_deployments),
        "request_ledger": client.records,
        "resource_use": {
            "logical_request_count": len(client.records),
            "http_attempt_count": client.http_attempts,
            "response_byte_count": client.response_bytes,
            "http_attempt_cap": rpc["maximum_http_attempts_per_host"],
            "response_byte_cap": rpc["maximum_response_bytes_per_host"],
        },
        "target_row_count_retained": 0,
        "raw_response_payloads_retained": False,
        "decision": PASS_DECISION if passed else FAIL_DECISION,
    }


def _validate_host_result(
    result: Mapping[str, object],
    *,
    expected_host_id: str,
    protocol_commit: str,
    manifest_sha256: str,
    source_sha256: str,
) -> list[str]:
    errors: list[str] = []
    if result.get("schema_version") != ARTIFACT_SCHEMA_VERSION or result.get("audit_id") != AUDIT_ID:
        errors.append(f"{expected_host_id}: artifact schema or audit ID mismatch")
    if result.get("host_id") != expected_host_id:
        errors.append(f"{expected_host_id}: host identity mismatch")
    if result.get("protocol_commit") != protocol_commit:
        errors.append(f"{expected_host_id}: protocol commit mismatch")
    if result.get("manifest_sha256") != manifest_sha256 or result.get("source_sha256") != source_sha256:
        errors.append(f"{expected_host_id}: code or manifest hash mismatch")
    if result.get("canary_address") != ZERO_ADDRESS:
        errors.append(f"{expected_host_id}: canary address mismatch")
    runtime = _mapping(result.get("runtime"))
    if runtime is None or runtime.get("gpu_visible") is not False:
        errors.append(f"{expected_host_id}: runtime GPU boundary mismatch")
    if (
        result.get("target_row_count_retained") != 0
        or result.get("raw_response_payloads_retained") is not False
    ):
        errors.append(f"{expected_host_id}: target/raw retention boundary violated")
    ledger = _sequence(result.get("request_ledger"))
    if ledger is None:
        errors.append(f"{expected_host_id}: request ledger is not a sequence")
        return errors
    attempt_count = 0
    response_bytes = 0
    for index, value in enumerate(ledger):
        record = _mapping(value)
        if record is None or record.get("logical_request_index") != index:
            errors.append(f"{expected_host_id}: invalid logical request index {index}")
            continue
        method = record.get("method")
        params = record.get("params")
        request_id = record.get("request_id")
        if method not in ALLOWED_METHODS or not isinstance(request_id, int):
            errors.append(f"{expected_host_id}: forbidden method or request ID at {index}")
            continue
        if method == "eth_chainId":
            if params != []:
                errors.append(f"{expected_host_id}: nonempty chain-ID params at {index}")
        else:
            values = _sequence(params)
            query = _mapping(values[0]) if values is not None and len(values) == 1 else None
            if (
                query is None
                or query.get("address") != ZERO_ADDRESS
                or set(query)
                != {
                    "address",
                    "fromBlock",
                    "toBlock",
                }
            ):
                errors.append(f"{expected_host_id}: non-canary log params at {index}")
        request = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        if record.get("request_sha256") != hashlib.sha256(_canonical_bytes(request)).hexdigest():
            errors.append(f"{expected_host_id}: request hash mismatch at {index}")
        attempts = _sequence(record.get("attempts"))
        if attempts is None or not 1 <= len(attempts) <= 2:
            errors.append(f"{expected_host_id}: invalid attempts at {index}")
            continue
        attempt_count += len(attempts)
        for attempt_value in attempts:
            attempt = _mapping(attempt_value)
            if attempt is None or not isinstance(attempt.get("response_byte_count"), int):
                errors.append(f"{expected_host_id}: malformed attempt at {index}")
                continue
            response_bytes += cast(int, attempt["response_byte_count"])
            if (
                not isinstance(attempt.get("response_body_sha256"), str)
                or HEX_SHA_PATTERN.fullmatch(cast(str, attempt["response_body_sha256"])) is None
            ):
                errors.append(f"{expected_host_id}: invalid response hash at {index}")
    resources = _mapping(result.get("resource_use"))
    if resources is None:
        errors.append(f"{expected_host_id}: resource summary missing")
    else:
        if resources.get("logical_request_count") != len(ledger):
            errors.append(f"{expected_host_id}: logical request count mismatch")
        if resources.get("http_attempt_count") != attempt_count:
            errors.append(f"{expected_host_id}: HTTP attempt count mismatch")
        if resources.get("response_byte_count") != response_bytes:
            errors.append(f"{expected_host_id}: response-byte count mismatch")
        if resources.get("http_attempt_cap") != 500 or resources.get("response_byte_cap") != 33_554_432:
            errors.append(f"{expected_host_id}: resource caps differ from the frozen values")
        if not isinstance(resources.get("http_attempt_count"), int) or cast(
            int, resources["http_attempt_count"]
        ) > cast(int, resources.get("http_attempt_cap", -1)):
            errors.append(f"{expected_host_id}: HTTP cap exceeded")
        if not isinstance(resources.get("response_byte_count"), int) or cast(
            int, resources["response_byte_count"]
        ) > cast(int, resources.get("response_byte_cap", -1)):
            errors.append(f"{expected_host_id}: byte cap exceeded")
    endpoint_results = _sequence(result.get("endpoint_results"))
    if endpoint_results is None or len(endpoint_results) != 18:
        errors.append(f"{expected_host_id}: endpoint result cardinality mismatch")
        endpoint_results = []
    expected_sequence = [
        (name, role, url)
        for name, _, primary, replica in EXPECTED_ENDPOINTS
        for role, url in (("primary", primary), ("replica", replica))
    ]
    observed_sequence = [
        (item.get("deployment"), item.get("endpoint_role"), item.get("url"))
        for value in endpoint_results
        if (item := _mapping(value)) is not None
    ]
    if observed_sequence != expected_sequence:
        errors.append(f"{expected_host_id}: endpoint result ordering mismatch")
    observed_keys = {
        (item.get("deployment"), item.get("endpoint_role"), item.get("url"))
        for value in endpoint_results
        if (item := _mapping(value)) is not None
    }
    expected_keys = {
        (name, role, url)
        for name, _, primary, replica in EXPECTED_ENDPOINTS
        for role, url in (("primary", primary), ("replica", replica))
    }
    if observed_keys != expected_keys:
        errors.append(f"{expected_host_id}: endpoint identity set mismatch")
    expected_chain_ids = {name: chain_id for name, chain_id, _, _ in EXPECTED_ENDPOINTS}
    ledger_records = [_mapping(value) for value in ledger]
    used_indices: list[int] = []
    for value in endpoint_results:
        endpoint = _mapping(value)
        if endpoint is None:
            errors.append(f"{expected_host_id}: malformed endpoint result")
            continue
        index_values = _sequence(endpoint.get("logical_request_indices"))
        if (
            index_values is None
            or not index_values
            or not all(isinstance(index, int) for index in index_values)
        ):
            errors.append(f"{expected_host_id}: invalid endpoint ledger indices")
            continue
        indices = cast(Sequence[int], index_values)
        if list(indices) != list(range(indices[0], indices[-1] + 1)) or any(
            index < 0 or index >= len(ledger_records) for index in indices
        ):
            errors.append(f"{expected_host_id}: noncontiguous endpoint ledger indices")
            continue
        used_indices.extend(indices)
        records = [ledger_records[index] for index in indices]
        if any(record is None for record in records):
            errors.append(f"{expected_host_id}: endpoint references malformed ledger rows")
            continue
        normalized = cast(list[Mapping[str, object]], records)
        deployment = endpoint.get("deployment")
        role = endpoint.get("endpoint_role")
        url = endpoint.get("url")
        if any(
            record.get("deployment") != deployment
            or record.get("endpoint_role") != role
            or record.get("url") != url
            for record in normalized
        ):
            errors.append(f"{expected_host_id}: endpoint/ledger identity mismatch")
        first_outcome = _mapping(normalized[0].get("outcome"))
        chain_good = (
            normalized[0].get("method") == "eth_chainId"
            and first_outcome is not None
            and first_outcome.get("kind") == "scalar_result"
            and first_outcome.get("value") == expected_chain_ids.get(cast(str, deployment))
        )
        second_outcome = _mapping(normalized[1].get("outcome")) if len(normalized) >= 2 else None
        single_good = (
            len(normalized) >= 2
            and normalized[1].get("method") == "eth_getLogs"
            and second_outcome is not None
            and _empty_log_outcome(second_outcome)
        )
        last_outcome = _mapping(normalized[-1].get("outcome")) if len(normalized) >= 3 else None
        range_good = (
            len(normalized) >= 3
            and normalized[-1].get("method") == "eth_getLogs"
            and last_outcome is not None
            and _empty_log_outcome(last_outcome)
        )
        if len(normalized) > 3 and any(
            (_mapping(record.get("outcome")) or {}).get("kind") != "rpc_error" for record in normalized[2:-1]
        ):
            errors.append(f"{expected_host_id}: non-RPC intermediate range outcome")
        learned_span: int | None = None
        if range_good:
            params = _sequence(normalized[-1].get("params"))
            query = _mapping(params[0]) if params is not None and len(params) == 1 else None
            to_block = query.get("toBlock") if query is not None else None
            if isinstance(to_block, str):
                try:
                    learned_span = int(to_block, 16) + 1
                except ValueError:
                    learned_span = None
        computed_pass = chain_good and single_good and range_good and learned_span is not None
        if (
            endpoint.get("chain_identity_passed") is not chain_good
            or endpoint.get("single_block_empty_passed") is not single_good
            or endpoint.get("range_empty_passed") is not range_good
            or endpoint.get("learned_maximum_interval_span") != learned_span
            or endpoint.get("passed") is not computed_pass
        ):
            errors.append(f"{expected_host_id}: endpoint decision does not reproduce from ledger")
    if sorted(used_indices) != list(range(len(ledger_records))):
        errors.append(f"{expected_host_id}: endpoint ledger coverage is not exact")
    passing = {
        name
        for name, _, _, _ in EXPECTED_ENDPOINTS
        if any(
            item.get("deployment") == name and item.get("passed") is True
            for value in endpoint_results
            if (item := _mapping(value)) is not None
        )
    }
    expected_decision = PASS_DECISION if len(passing) == len(EXPECTED_ENDPOINTS) else FAIL_DECISION
    if result.get("decision") != expected_decision or result.get("passing_deployments") != sorted(passing):
        errors.append(f"{expected_host_id}: host decision or coverage mismatch")
    return errors


def aggregate_results(
    manifest: Mapping[str, object],
    *,
    host_results: Mapping[str, Mapping[str, object]],
    host_artifact_hashes: Mapping[str, str],
    protocol_commit: str,
    manifest_sha256: str,
    source_sha256: str,
) -> dict[str, object]:
    """Validate all four hosts and select one without target-result conditioning."""

    errors = validate_manifest(manifest)
    if set(host_results) != set(HOST_PRIORITY) or set(host_artifact_hashes) != set(HOST_PRIORITY):
        errors.append("all and only the four frozen host results must be supplied")
    for host_id in HOST_PRIORITY:
        result = host_results.get(host_id)
        artifact_hash = host_artifact_hashes.get(host_id)
        if result is None:
            continue
        errors.extend(
            _validate_host_result(
                result,
                expected_host_id=host_id,
                protocol_commit=protocol_commit,
                manifest_sha256=manifest_sha256,
                source_sha256=source_sha256,
            )
        )
        if artifact_hash is None or HEX_SHA_PATTERN.fullmatch(artifact_hash) is None:
            errors.append(f"{host_id}: invalid host artifact hash")
    selected_host = next(
        (
            host_id
            for host_id in HOST_PRIORITY
            if host_results.get(host_id, {}).get("decision") == PASS_DECISION
        ),
        None,
    )
    selected_endpoints: list[dict[str, object]] = []
    if not errors and selected_host is not None:
        endpoint_results = cast(
            Sequence[Mapping[str, object]], host_results[selected_host]["endpoint_results"]
        )
        for name, _, _, _ in EXPECTED_ENDPOINTS:
            candidates = [
                item
                for role in ("primary", "replica")
                for item in endpoint_results
                if item.get("deployment") == name
                and item.get("endpoint_role") == role
                and item.get("passed") is True
            ]
            if not candidates:
                errors.append(f"selected host lacks a passing endpoint for {name}")
                continue
            chosen = candidates[0]
            selected_endpoints.append(
                {
                    "deployment": name,
                    "endpoint_role": chosen["endpoint_role"],
                    "url": chosen["url"],
                    "initial_maximum_interval_span": chosen["learned_maximum_interval_span"],
                }
            )
    passed = not errors and selected_host is not None and len(selected_endpoints) == len(EXPECTED_ENDPOINTS)
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "protocol_commit": protocol_commit,
        "manifest_sha256": manifest_sha256,
        "source_sha256": source_sha256,
        "host_priority": list(HOST_PRIORITY),
        "host_artifacts": [
            {
                "host_id": host_id,
                "sha256": host_artifact_hashes.get(host_id),
                "decision": host_results.get(host_id, {}).get("decision"),
                "passing_deployments": host_results.get(host_id, {}).get("passing_deployments"),
            }
            for host_id in HOST_PRIORITY
        ],
        "selected_host": selected_host if passed else None,
        "selected_endpoints": selected_endpoints if passed else [],
        "validation_errors": errors,
        "target_row_count_retained": 0,
        "gpu_used": False,
        "decision": PASS_DECISION if passed else FAIL_DECISION,
        "authorized_next_stage": (
            "scientific_contract_preserving_b0_v2_protocol_design_only" if passed else None
        ),
    }


def _write_json(path: Path, value: object) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _parse_host_inputs(values: Sequence[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        host_id, separator, path = value.partition("=")
        if not separator or host_id in result:
            raise ValueError(f"invalid or duplicate --host-result: {value}")
        result[host_id] = Path(path)
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run")
    run.add_argument("manifest", type=Path)
    run.add_argument("--host-id", required=True)
    run.add_argument("--protocol-commit", required=True)
    run.add_argument("--output", type=Path, required=True)
    aggregate = subparsers.add_parser("aggregate")
    aggregate.add_argument("manifest", type=Path)
    aggregate.add_argument("--root", type=Path, default=Path.cwd())
    aggregate.add_argument("--protocol-commit", required=True)
    aggregate.add_argument("--host-result", action="append", default=[], required=True)
    aggregate.add_argument("--output", type=Path, required=True)
    return parser


def main() -> None:
    """Run one host canary or aggregate all sealed host artifacts."""

    args = _build_parser().parse_args()
    manifest = load_json(args.manifest)
    manifest_sha256 = sha256_file(args.manifest)
    source_sha256 = sha256_file(Path(__file__))
    if args.command == "run":
        result = run_host_canary(
            manifest,
            host_id=cast(str, args.host_id),
            protocol_commit=cast(str, args.protocol_commit),
            manifest_sha256=manifest_sha256,
            source_sha256=source_sha256,
        )
        _write_json(args.output, result)
        print(json.dumps({"host_id": result["host_id"], "decision": result["decision"]}))
        return
    parent_errors = validate_parent_files(manifest, args.root)
    if parent_errors:
        raise ValueError("invalid transport parents: " + "; ".join(parent_errors))
    input_paths = _parse_host_inputs(cast(Sequence[str], args.host_result))
    host_results = {host_id: load_json(path) for host_id, path in input_paths.items()}
    host_hashes = {host_id: sha256_file(path) for host_id, path in input_paths.items()}
    summary = aggregate_results(
        manifest,
        host_results=host_results,
        host_artifact_hashes=host_hashes,
        protocol_commit=cast(str, args.protocol_commit),
        manifest_sha256=manifest_sha256,
        source_sha256=source_sha256,
    )
    _write_json(args.output, summary)
    print(json.dumps({"decision": summary["decision"], "selected_host": summary["selected_host"]}))


if __name__ == "__main__":
    main()
