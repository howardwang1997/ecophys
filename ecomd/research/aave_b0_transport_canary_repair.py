"""Target-row-free v2 repair canary for the Aave V3 B0 transport gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from ecomd.research.aave_b0_transport_canary import (
    FAIL_DECISION as V1_FAIL_DECISION,
)
from ecomd.research.aave_b0_transport_canary import (
    ProbeClient,
    Transport,
    _canonical_bytes,
    _empty_log_outcome,
    _mapping,
    _sequence,
    load_json,
    sha256_file,
    urllib_transport,
)
from ecomd.research.aave_b0_transport_canary import (
    _validate_host_result as _validate_v1_host_result,
)
from ecomd.research.aave_b0_transport_canary import (
    validate_manifest as validate_v1_manifest,
)
from ecomd.research.aave_b0_transport_canary import (
    validate_parent_files as validate_v1_parent_files,
)

SCHEMA_VERSION = "ecophys-aave-v3-b0-transport-canary-repair/v2"
ARTIFACT_SCHEMA_VERSION = "ecophys-aave-v3-b0-transport-canary-repair-audit/v2"
AUDIT_ID = "aave_v3_b0_transport_canary_repair_v2"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
HEX_SHA_PATTERN = re.compile(r"[0-9a-f]{64}")
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")

HOST_PRIORITY = ("rtx2060", "local_mac")
V1_REQUIRED_PASSING = ("arbitrum", "avalanche", "gnosis", "linea", "optimism", "scroll")
DEPLOYMENT_ORDER = (
    "arbitrum",
    "avalanche",
    "optimism",
    "polygon",
    "base",
    "gnosis",
    "bnb",
    "linea",
    "scroll",
)
PASS_DECISION = "PASS_TARGET_ROW_FREE_TRANSPORT_REPAIR_AUTHORIZE_B0_V2_PROTOCOL_DESIGN_ONLY"
FAIL_DECISION = "FAIL_TARGET_ROW_FREE_TRANSPORT_REPAIR_KEEP_B0_V2_B1_G1_GPU_LOCKED"

EXPECTED_PARENTS: dict[str, object] = {
    "canary_v1_archive_commit": "fc9f9bff03ff9432cd76b60b314d7e561d15193e",
    "canary_v1_protocol_commit": "4f18e81850102023ce802109f47bb5727f6315a0",
    "canary_v1_manifest_path": "data/manifests/aave_v3_b0_transport_canary_v1.json",
    "canary_v1_manifest_sha256": "a524b694b761e324571c74f0d4131295722c0d6094e9fc2e0abe5f5e84864c33",
    "canary_v1_source_path": "ecomd/research/aave_b0_transport_canary.py",
    "canary_v1_source_sha256": "6f56b9fa956d7c8ab2cc7d48ab776bdeedc428211cb644c06ad0eeeea0a1155f",
    "canary_v1_result_path": "experiments/v14_aave_v3_b0_transport_canary/RESULTS_V1.md",
    "canary_v1_result_sha256": "f19d55771549d917482602a6949b023aa219c7fcda859f78edda356d352a0526",
    "canary_v1_summary_path": "experiments/v14_aave_v3_b0_transport_canary/artifacts/summary.json",
    "canary_v1_summary_sha256": "28946aa8439804b9a69f0e9a0793adece6e5903a33c8fba47f4475dfd917bab3",
    "canary_v1_rtx2060_artifact_path": (
        "experiments/v14_aave_v3_b0_transport_canary/artifacts/hosts/rtx2060.json"
    ),
    "canary_v1_rtx2060_artifact_sha256": ("c3aec5623eeed78c9be2987d65c8cef6abad1c208bf53f0b11094c62e740a25f"),
    "canary_v1_local_mac_artifact_path": (
        "experiments/v14_aave_v3_b0_transport_canary/artifacts/hosts/local_mac.json"
    ),
    "canary_v1_local_mac_artifact_sha256": (
        "61c6016d8bb9c25181f92b26d1e4b0bb489f3cc939a09f5a61983c1b05163600"
    ),
    "source_audit_path": "papers/proposal/v14_aave_b0_transport_repair_source_audit_2026-08-17.md",
    "source_audit_sha256": "9e91405a6b80d1f399fe92fe026faae5fc983b756a3186dae68d37c74509f0dc",
    "expected_canary_v1_decision": V1_FAIL_DECISION,
}

EXPECTED_INHERITED_ROUTES: tuple[tuple[str, str, str, int], ...] = (
    ("arbitrum", "replica", "https://arb1.arbitrum.io/rpc", 250_000),
    (
        "avalanche",
        "primary",
        "https://avalanche-c-chain-rpc.publicnode.com",
        31_250,
    ),
    ("optimism", "replica", "https://mainnet.optimism.io", 7_813),
    ("gnosis", "primary", "https://gnosis-rpc.publicnode.com", 7_813),
    ("linea", "primary", "https://linea-rpc.publicnode.com", 31_250),
    ("scroll", "primary", "https://scroll-rpc.publicnode.com", 31_250),
)

EXPECTED_REPAIRS: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "polygon",
        "0x89",
        "replica",
        "https://polygon.drpc.org",
        "canary_v1_single_block_pass_http_400_range_failure",
    ),
    (
        "base",
        "0x2105",
        "replica",
        "https://mainnet.base.org",
        "canary_v1_single_block_pass_http_413_range_failure",
    ),
    (
        "bnb",
        "0x38",
        "documented_provider",
        "https://bsc.drpc.org",
        "bnb_official_provider_list_and_drpc_eth_getlogs_documentation",
    ),
)


def _expected_inherited_routes() -> list[dict[str, object]]:
    return [
        {
            "deployment": deployment,
            "endpoint_role": role,
            "url": url,
            "initial_maximum_interval_span": span,
        }
        for deployment, role, url, span in EXPECTED_INHERITED_ROUTES
    ]


def _expected_repairs() -> list[dict[str, object]]:
    return [
        {
            "name": name,
            "chain_id_hex": chain_id,
            "endpoint_role": role,
            "url": url,
            "candidate_origin": origin,
        }
        for name, chain_id, role, url, origin in EXPECTED_REPAIRS
    ]


def validate_manifest(manifest: Mapping[str, object]) -> list[str]:
    """Validate the complete v2 repair contract without network access."""

    errors: list[str] = []
    expected_root_keys = {
        "schema_version",
        "audit_id",
        "as_of",
        "stage",
        "parents",
        "scientific_contract",
        "eligibility",
        "inherited_routes",
        "canary",
        "hosts",
        "rpc",
        "repair_endpoints",
        "decision_policy",
    }
    if set(manifest) != expected_root_keys:
        errors.append("manifest root keys differ from the frozen repair contract")
    if manifest.get("schema_version") != SCHEMA_VERSION or manifest.get("audit_id") != AUDIT_ID:
        errors.append("schema or audit ID differs from the frozen repair contract")
    if manifest.get("as_of") != "2026-08-17" or manifest.get("stage") != (
        "target_row_free_rpc_transport_canary_repair"
    ):
        errors.append("date or stage differs from the frozen repair contract")
    if manifest.get("parents") != EXPECTED_PARENTS:
        errors.append("parents differ from the frozen canary-v1 evidence")
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
        "b1_accounts_outcomes_g1_gpu_locked": True,
    }
    if manifest.get("scientific_contract") != expected_science:
        errors.append("scientific inheritance contract differs from the frozen values")
    expected_eligibility = {
        "host_priority": list(HOST_PRIORITY),
        "all_eligible_hosts_must_report": True,
        "required_v1_passing_deployments": list(V1_REQUIRED_PASSING),
        "excluded_v1_hosts": ["v100_a", "v100_b"],
        "exclusion_rule": "v1_coverage_below_six_cannot_reach_nine_from_three_repair_probes",
    }
    if manifest.get("eligibility") != expected_eligibility:
        errors.append("host eligibility differs from the outcome-blind v1 coverage rule")
    if manifest.get("inherited_routes") != _expected_inherited_routes():
        errors.append("inherited routes differ from the two v1 eligible-host artifacts")
    expected_canary = {
        "address": ZERO_ADDRESS,
        "expected_log_count": 0,
        "single_block_interval": [0, 0],
        "root_interval": [0, 249_999],
        "multiblock_bisection_allowed_after_single_empty": True,
        "bisection_eligible_final_outcomes": [
            "rpc_error",
            "persistent_http_400",
            "persistent_http_413",
        ],
        "all_other_outcomes_terminal": True,
        "nonempty_result_action": "contamination_fail_discard_rows",
        "allowed_methods": ["eth_chainId", "eth_getLogs"],
    }
    if manifest.get("canary") != expected_canary:
        errors.append("canary query or range-error contract differs from the frozen values")
    expected_hosts = {
        "priority": list(HOST_PRIORITY),
        "all_hosts_must_report_before_selection": True,
        "gpu_visible": False,
        "host_ids_are_bound_to_gitignored_local_inventory": True,
    }
    if manifest.get("hosts") != expected_hosts:
        errors.append("host execution contract differs from the frozen values")
    expected_rpc = {
        "maximum_requests_per_second_per_host": 2,
        "maximum_attempts_per_logical_call": 2,
        "maximum_http_attempts_per_host": 100,
        "maximum_response_bytes_per_host": 8_388_608,
        "timeout_seconds": 30,
        "user_agent": "EcoPhys-V14-Aave-B0-transport-canary-repair/2.0",
        "raw_response_payloads_retained": False,
    }
    if manifest.get("rpc") != expected_rpc:
        errors.append("RPC resource contract differs from the frozen values")
    if manifest.get("repair_endpoints") != _expected_repairs():
        errors.append("repair endpoint candidates differ from the frozen order")
    expected_decision = {
        "pass": PASS_DECISION,
        "fail": FAIL_DECISION,
        "all_hosts_required": True,
        "single_host_required_for_all_three_repairs": True,
        "select_first_passing_host_by_frozen_priority": True,
        "authorized_next_stage": "scientific_contract_preserving_b0_v2_protocol_design_only",
    }
    if manifest.get("decision_policy") != expected_decision:
        errors.append("decision policy differs from the frozen values")
    return errors


def _validate_parent_hashes(parents: Mapping[str, object], root: Path) -> list[str]:
    errors: list[str] = []
    pairs = (
        ("canary_v1_manifest_path", "canary_v1_manifest_sha256"),
        ("canary_v1_source_path", "canary_v1_source_sha256"),
        ("canary_v1_result_path", "canary_v1_result_sha256"),
        ("canary_v1_summary_path", "canary_v1_summary_sha256"),
        ("canary_v1_rtx2060_artifact_path", "canary_v1_rtx2060_artifact_sha256"),
        ("canary_v1_local_mac_artifact_path", "canary_v1_local_mac_artifact_sha256"),
        ("source_audit_path", "source_audit_sha256"),
    )
    for path_key, hash_key in pairs:
        relative = parents.get(path_key)
        expected_hash = parents.get(hash_key)
        if not isinstance(relative, str) or not isinstance(expected_hash, str):
            errors.append(f"invalid parent identity fields: {path_key}/{hash_key}")
            continue
        target = root / relative
        if not target.is_file():
            errors.append(f"missing parent file: {relative}")
        elif sha256_file(target) != expected_hash:
            errors.append(f"parent hash mismatch: {relative}")
    return errors


def _validate_v1_host_inheritance(
    host_result: Mapping[str, object],
    *,
    host_id: str,
    protocol_commit: str,
    manifest_sha256: str,
    source_sha256: str,
) -> list[str]:
    errors = _validate_v1_host_result(
        host_result,
        expected_host_id=host_id,
        protocol_commit=protocol_commit,
        manifest_sha256=manifest_sha256,
        source_sha256=source_sha256,
    )
    if host_result.get("passing_deployments") != list(V1_REQUIRED_PASSING):
        errors.append(f"{host_id}: v1 coverage differs from the frozen six-deployment eligibility")
    endpoints = _sequence(host_result.get("endpoint_results")) or []
    for deployment, role, url, span in EXPECTED_INHERITED_ROUTES:
        matches = [
            item
            for value in endpoints
            if (item := _mapping(value)) is not None
            and item.get("deployment") == deployment
            and item.get("endpoint_role") == role
            and item.get("url") == url
            and item.get("passed") is True
            and item.get("learned_maximum_interval_span") == span
        ]
        if len(matches) != 1:
            errors.append(f"{host_id}: inherited route does not reproduce for {deployment}")
    return errors


def validate_parent_files(manifest: Mapping[str, object], root: str | Path) -> list[str]:
    """Hash- and structure-check v1 evidence used by the repair selection."""

    parents = _mapping(manifest.get("parents"))
    if parents is None:
        return ["parents must be a mapping"]
    root_path = Path(root)
    errors = _validate_parent_hashes(parents, root_path)
    if errors:
        return errors
    manifest_path = root_path / cast(str, parents["canary_v1_manifest_path"])
    v1_manifest = load_json(manifest_path)
    errors.extend(f"v1 manifest: {item}" for item in validate_v1_manifest(v1_manifest))
    errors.extend(f"v1 parent: {item}" for item in validate_v1_parent_files(v1_manifest, root_path))
    protocol_commit = cast(str, parents["canary_v1_protocol_commit"])
    manifest_hash = cast(str, parents["canary_v1_manifest_sha256"])
    source_hash = cast(str, parents["canary_v1_source_sha256"])
    host_results: dict[str, dict[str, object]] = {}
    for host_id in HOST_PRIORITY:
        path = root_path / cast(str, parents[f"canary_v1_{host_id}_artifact_path"])
        host_result = load_json(path)
        host_results[host_id] = host_result
        errors.extend(
            _validate_v1_host_inheritance(
                host_result,
                host_id=host_id,
                protocol_commit=protocol_commit,
                manifest_sha256=manifest_hash,
                source_sha256=source_hash,
            )
        )
    summary = load_json(root_path / cast(str, parents["canary_v1_summary_path"]))
    if (
        summary.get("decision") != parents.get("expected_canary_v1_decision")
        or summary.get("validation_errors") != []
        or summary.get("selected_host") is not None
        or summary.get("protocol_commit") != protocol_commit
        or summary.get("manifest_sha256") != manifest_hash
        or summary.get("source_sha256") != source_hash
    ):
        errors.append("v1 aggregate summary differs from the frozen failed decision")
    summary_hosts = _sequence(summary.get("host_artifacts")) or []
    for host_id in HOST_PRIORITY:
        expected_hash = parents.get(f"canary_v1_{host_id}_artifact_sha256")
        matches = [
            item
            for value in summary_hosts
            if (item := _mapping(value)) is not None
            and item.get("host_id") == host_id
            and item.get("sha256") == expected_hash
            and item.get("passing_deployments") == list(V1_REQUIRED_PASSING)
        ]
        if len(matches) != 1:
            errors.append(f"v1 aggregate identity does not reproduce for {host_id}")
    result_text = (root_path / cast(str, parents["canary_v1_result_path"])).read_text(encoding="utf-8")
    if cast(str, parents["expected_canary_v1_decision"]) not in result_text:
        errors.append("v1 result note does not contain the frozen failed decision")
    return errors


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


def _persistent_range_http(record: Mapping[str, object], outcome: Mapping[str, object]) -> bool:
    if outcome.get("kind") != "http_or_transport_failure" or outcome.get("http_status") not in {
        400,
        413,
    }:
        return False
    attempts = _sequence(record.get("attempts"))
    if attempts is None or len(attempts) != 2:
        return False
    return all(
        (attempt := _mapping(value)) is not None
        and attempt.get("http_status") in {400, 413}
        and attempt.get("transport_error") is None
        for value in attempts
    )


def _bisection_eligible(record: Mapping[str, object], outcome: Mapping[str, object]) -> bool:
    return outcome.get("kind") == "rpc_error" or _persistent_range_http(record, outcome)


def probe_repair_endpoint(
    client: ProbeClient,
    *,
    deployment: str,
    expected_chain_id: str,
    endpoint_role: str,
    url: str,
    root_to_block: int = 249_999,
) -> dict[str, object]:
    """Probe one repair candidate under the frozen v2 error classification."""

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
        return _endpoint_result(
            client,
            first_record=first_record,
            deployment=deployment,
            endpoint_role=endpoint_role,
            url=url,
            chain_passed=False,
            single_passed=False,
            learned_span=None,
            failure_stage="chain_identity",
        )
    single = client.call(
        deployment=deployment,
        endpoint_role=endpoint_role,
        url=url,
        label="empty_zero_address_single_block:0-0",
        method="eth_getLogs",
        params=[{"address": ZERO_ADDRESS, "fromBlock": "0x0", "toBlock": "0x0"}],
    )
    if not _empty_log_outcome(single):
        return _endpoint_result(
            client,
            first_record=first_record,
            deployment=deployment,
            endpoint_role=endpoint_role,
            url=url,
            chain_passed=True,
            single_passed=False,
            learned_span=None,
            failure_stage="single_block_empty_log",
        )
    interval_to = root_to_block
    learned_span: int | None = None
    failure_stage = "range_terminal_error"
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
        last_record = client.records[-1]
        if not _bisection_eligible(last_record, outcome):
            break
        if interval_to == 0:
            failure_stage = "range_floor_failure"
            break
        interval_to //= 2
    return _endpoint_result(
        client,
        first_record=first_record,
        deployment=deployment,
        endpoint_role=endpoint_role,
        url=url,
        chain_passed=True,
        single_passed=True,
        learned_span=learned_span,
        failure_stage=None if learned_span is not None else failure_stage,
    )


def _endpoint_result(
    client: ProbeClient,
    *,
    first_record: int,
    deployment: str,
    endpoint_role: str,
    url: str,
    chain_passed: bool,
    single_passed: bool,
    learned_span: int | None,
    failure_stage: str | None,
) -> dict[str, object]:
    passed = learned_span is not None
    return {
        "deployment": deployment,
        "endpoint_role": endpoint_role,
        "url": url,
        "chain_identity_passed": chain_passed,
        "single_block_empty_passed": single_passed,
        "range_empty_passed": passed,
        "learned_maximum_interval_span": learned_span,
        "failure_stage": failure_stage,
        "logical_request_indices": list(range(first_record, len(client.records))),
        "passed": passed,
    }


def run_host_canary(
    manifest: Mapping[str, object],
    *,
    host_id: str,
    protocol_commit: str,
    manifest_sha256: str,
    source_sha256: str,
    transport: Transport = urllib_transport,
) -> dict[str, object]:
    """Run the three frozen repair probes on one eligible host."""

    errors = validate_manifest(manifest)
    if errors:
        raise ValueError("invalid repair manifest: " + "; ".join(errors))
    if host_id not in HOST_PRIORITY:
        raise ValueError(f"ineligible host ID: {host_id}")
    if COMMIT_PATTERN.fullmatch(protocol_commit) is None:
        raise ValueError("protocol commit must be a lowercase 40-hex Git SHA")
    if HEX_SHA_PATTERN.fullmatch(manifest_sha256) is None or HEX_SHA_PATTERN.fullmatch(source_sha256) is None:
        raise ValueError("manifest and source hashes must be lowercase SHA-256 values")
    started = datetime.now(UTC)
    client = _new_client(manifest, transport)
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
    passing_repairs = sorted(
        cast(str, item["deployment"]) for item in endpoint_results if item["passed"] is True
    )
    passed = set(passing_repairs) == {item[0] for item in EXPECTED_REPAIRS}
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
        "inherited_deployments": list(V1_REQUIRED_PASSING),
        "endpoint_results": endpoint_results,
        "passing_repairs": passing_repairs,
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


def _validate_request_ledger(
    result: Mapping[str, object], *, expected_host_id: str
) -> tuple[list[str], list[Mapping[str, object]]]:
    errors: list[str] = []
    ledger = _sequence(result.get("request_ledger"))
    if ledger is None:
        return [f"{expected_host_id}: request ledger is not a sequence"], []
    normalized: list[Mapping[str, object]] = []
    attempt_count = 0
    response_bytes = 0
    for index, value in enumerate(ledger):
        record = _mapping(value)
        if record is None or record.get("logical_request_index") != index:
            errors.append(f"{expected_host_id}: invalid logical request index {index}")
            continue
        normalized.append(record)
        method = record.get("method")
        params = record.get("params")
        request_id = record.get("request_id")
        if method not in {"eth_chainId", "eth_getLogs"} or not isinstance(request_id, int):
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
        normalized_attempts: list[Mapping[str, object]] = []
        for attempt_index, attempt_value in enumerate(attempts, start=1):
            attempt = _mapping(attempt_value)
            if attempt is None:
                errors.append(f"{expected_host_id}: malformed attempt at {index}")
                continue
            normalized_attempts.append(attempt)
            byte_count = attempt.get("response_byte_count")
            status = attempt.get("http_status")
            transport_error = attempt.get("transport_error")
            if (
                attempt.get("attempt_number") != attempt_index
                or not isinstance(byte_count, int)
                or byte_count < 0
                or (status is not None and not isinstance(status, int))
                or (transport_error is not None and not isinstance(transport_error, str))
            ):
                errors.append(f"{expected_host_id}: malformed attempt at {index}")
                continue
            response_bytes += byte_count
            response_hash = attempt.get("response_body_sha256")
            if not isinstance(response_hash, str) or HEX_SHA_PATTERN.fullmatch(response_hash) is None:
                errors.append(f"{expected_host_id}: invalid response hash at {index}")
        outcome = _mapping(record.get("outcome"))
        if outcome is None or not normalized_attempts:
            errors.append(f"{expected_host_id}: missing normalized outcome at {index}")
            continue
        kind = outcome.get("kind")
        allowed_kinds = {
            "http_or_transport_failure",
            "invalid_json",
            "invalid_envelope",
            "rpc_error",
            "scalar_result",
            "log_list_result",
            "invalid_result_type",
        }
        if kind not in allowed_kinds:
            errors.append(f"{expected_host_id}: invalid normalized outcome at {index}")
        last_attempt = normalized_attempts[-1]
        if kind == "http_or_transport_failure":
            if (
                outcome.get("http_status") != last_attempt.get("http_status")
                or outcome.get("transport_error") != last_attempt.get("transport_error")
                or (last_attempt.get("http_status") == 200 and last_attempt.get("transport_error") is None)
            ):
                errors.append(f"{expected_host_id}: HTTP outcome/attempt mismatch at {index}")
        elif last_attempt.get("http_status") != 200 or last_attempt.get("transport_error") is not None:
            errors.append(
                f"{expected_host_id}: JSON outcome lacks a successful final HTTP attempt at {index}"
            )
        if kind == "scalar_result" and not isinstance(outcome.get("value"), str):
            errors.append(f"{expected_host_id}: malformed scalar outcome at {index}")
        if kind == "log_list_result" and (
            not isinstance(outcome.get("log_count"), int) or cast(int, outcome["log_count"]) < 0
        ):
            errors.append(f"{expected_host_id}: malformed log-count outcome at {index}")
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
        if resources.get("http_attempt_cap") != 100 or resources.get("response_byte_cap") != 8_388_608:
            errors.append(f"{expected_host_id}: resource caps differ from the frozen values")
        http_count = resources.get("http_attempt_count")
        byte_count = resources.get("response_byte_count")
        if not isinstance(http_count, int) or http_count > 100:
            errors.append(f"{expected_host_id}: HTTP cap exceeded")
        if not isinstance(byte_count, int) or byte_count > 8_388_608:
            errors.append(f"{expected_host_id}: byte cap exceeded")
    return errors, normalized


def _record_log_query(record: Mapping[str, object]) -> Mapping[str, object] | None:
    params = _sequence(record.get("params"))
    return _mapping(params[0]) if params is not None and len(params) == 1 else None


def _validate_endpoint_records(
    records: Sequence[Mapping[str, object]],
    endpoint: Mapping[str, object],
    *,
    expected_chain_id: str,
) -> tuple[list[str], bool, bool, int | None, str | None]:
    errors: list[str] = []
    chain_outcome = _mapping(records[0].get("outcome")) if records else None
    chain_good = (
        bool(records)
        and records[0].get("method") == "eth_chainId"
        and records[0].get("label") == "chain_id"
        and chain_outcome is not None
        and chain_outcome.get("kind") == "scalar_result"
        and chain_outcome.get("value") == expected_chain_id
    )
    if not chain_good:
        if len(records) != 1:
            errors.append("chain failure did not terminate the endpoint probe")
        return errors, False, False, None, "chain_identity"
    if len(records) < 2:
        return [*errors, "passing chain identity lacks the single-block probe"], True, False, None, None
    single_outcome = _mapping(records[1].get("outcome"))
    single_query = _record_log_query(records[1])
    single_good = (
        records[1].get("method") == "eth_getLogs"
        and records[1].get("label") == "empty_zero_address_single_block:0-0"
        and single_query == {"address": ZERO_ADDRESS, "fromBlock": "0x0", "toBlock": "0x0"}
        and single_outcome is not None
        and _empty_log_outcome(single_outcome)
    )
    if not single_good:
        if len(records) != 2:
            errors.append("single-block failure incorrectly triggered range bisection")
        return errors, True, False, None, "single_block_empty_log"
    if len(records) < 3:
        return [*errors, "passing single block lacks a range probe"], True, True, None, None
    expected_to = 249_999
    learned_span: int | None = None
    failure_stage: str | None = None
    for offset, record in enumerate(records[2:]):
        query = _record_log_query(record)
        if (
            record.get("method") != "eth_getLogs"
            or record.get("label") != f"empty_zero_address_range:0-{expected_to}"
            or query is None
            or query.get("address") != ZERO_ADDRESS
            or query.get("fromBlock") != "0x0"
            or query.get("toBlock") != hex(expected_to)
        ):
            errors.append(f"invalid deterministic range sequence at offset {offset}")
        outcome = _mapping(record.get("outcome")) or {}
        is_last = offset == len(records[2:]) - 1
        if _empty_log_outcome(outcome):
            learned_span = expected_to + 1
            if not is_last:
                errors.append("range probing continued after an empty success")
            break
        eligible = _bisection_eligible(record, outcome)
        if not eligible:
            failure_stage = "range_terminal_error"
            if not is_last:
                errors.append("range probing continued after a terminal outcome")
            break
        if expected_to == 0:
            failure_stage = "range_floor_failure"
            if not is_last:
                errors.append("range probing continued below the single-block floor")
            break
        if is_last:
            errors.append("eligible range failure did not continue deterministic bisection")
            break
        expected_to //= 2
    if learned_span is None and failure_stage is None:
        errors.append("range endpoint ended without a reproducible decision")
    del endpoint
    return errors, True, True, learned_span, failure_stage


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
    runtime = _mapping(result.get("runtime"))
    if runtime is None or runtime.get("gpu_visible") is not False:
        errors.append(f"{expected_host_id}: runtime GPU boundary mismatch")
    if (
        result.get("canary_address") != ZERO_ADDRESS
        or result.get("target_row_count_retained") != 0
        or result.get("raw_response_payloads_retained") is not False
    ):
        errors.append(f"{expected_host_id}: target/raw retention boundary violated")
    if result.get("inherited_deployments") != list(V1_REQUIRED_PASSING):
        errors.append(f"{expected_host_id}: inherited deployment identity mismatch")
    ledger_errors, ledger = _validate_request_ledger(result, expected_host_id=expected_host_id)
    errors.extend(ledger_errors)
    endpoint_results = _sequence(result.get("endpoint_results"))
    if endpoint_results is None or len(endpoint_results) != len(EXPECTED_REPAIRS):
        errors.append(f"{expected_host_id}: endpoint result cardinality mismatch")
        endpoint_results = []
    expected_sequence = [(name, role, url) for name, _, role, url, _ in EXPECTED_REPAIRS]
    observed_sequence = [
        (item.get("deployment"), item.get("endpoint_role"), item.get("url"))
        for value in endpoint_results
        if (item := _mapping(value)) is not None
    ]
    if observed_sequence != expected_sequence:
        errors.append(f"{expected_host_id}: endpoint result ordering or identity mismatch")
    used_indices: list[int] = []
    passing: set[str] = set()
    expected_chain_ids = {name: chain_id for name, chain_id, _, _, _ in EXPECTED_REPAIRS}
    for value in endpoint_results:
        endpoint = _mapping(value)
        if endpoint is None:
            errors.append(f"{expected_host_id}: malformed endpoint result")
            continue
        indices_value = _sequence(endpoint.get("logical_request_indices"))
        if (
            indices_value is None
            or not indices_value
            or not all(isinstance(index, int) for index in indices_value)
        ):
            errors.append(f"{expected_host_id}: invalid endpoint ledger indices")
            continue
        indices = cast(Sequence[int], indices_value)
        if list(indices) != list(range(indices[0], indices[-1] + 1)) or any(
            index < 0 or index >= len(ledger) for index in indices
        ):
            errors.append(f"{expected_host_id}: noncontiguous endpoint ledger indices")
            continue
        used_indices.extend(indices)
        records = [ledger[index] for index in indices]
        deployment = cast(str, endpoint.get("deployment"))
        role = endpoint.get("endpoint_role")
        url = endpoint.get("url")
        if any(
            record.get("deployment") != deployment
            or record.get("endpoint_role") != role
            or record.get("url") != url
            for record in records
        ):
            errors.append(f"{expected_host_id}: endpoint/ledger identity mismatch")
        endpoint_errors, chain_good, single_good, learned_span, failure_stage = _validate_endpoint_records(
            records,
            endpoint,
            expected_chain_id=expected_chain_ids.get(deployment, ""),
        )
        errors.extend(f"{expected_host_id}/{deployment}: {item}" for item in endpoint_errors)
        passed = learned_span is not None
        if (
            endpoint.get("chain_identity_passed") is not chain_good
            or endpoint.get("single_block_empty_passed") is not single_good
            or endpoint.get("range_empty_passed") is not passed
            or endpoint.get("learned_maximum_interval_span") != learned_span
            or endpoint.get("failure_stage") != failure_stage
            or endpoint.get("passed") is not passed
        ):
            errors.append(f"{expected_host_id}: endpoint decision does not reproduce for {deployment}")
        if passed:
            passing.add(deployment)
    if sorted(used_indices) != list(range(len(ledger))):
        errors.append(f"{expected_host_id}: endpoint ledger coverage is not exact")
    expected_decision = PASS_DECISION if len(passing) == len(EXPECTED_REPAIRS) else FAIL_DECISION
    if result.get("decision") != expected_decision or result.get("passing_repairs") != sorted(passing):
        errors.append(f"{expected_host_id}: host decision or repair coverage mismatch")
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
    """Validate both eligible hosts and construct a nine-deployment transport plan."""

    errors = validate_manifest(manifest)
    if set(host_results) != set(HOST_PRIORITY) or set(host_artifact_hashes) != set(HOST_PRIORITY):
        errors.append("all and only the two eligible host results must be supplied")
    for host_id in HOST_PRIORITY:
        result = host_results.get(host_id)
        artifact_hash = host_artifact_hashes.get(host_id)
        if result is not None:
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
        repair_results = cast(Sequence[Mapping[str, object]], host_results[selected_host]["endpoint_results"])
        inherited = {
            route["deployment"]: {**route, "evidence_stage": "transport_canary_v1"}
            for route in _expected_inherited_routes()
        }
        repairs = {
            item["deployment"]: {
                "deployment": item["deployment"],
                "endpoint_role": item["endpoint_role"],
                "url": item["url"],
                "initial_maximum_interval_span": item["learned_maximum_interval_span"],
                "evidence_stage": "transport_canary_repair_v2",
            }
            for item in repair_results
            if item.get("passed") is True
        }
        selected_endpoints = [
            (inherited | repairs)[deployment]
            for deployment in DEPLOYMENT_ORDER
            if deployment in inherited or deployment in repairs
        ]
    passed = not errors and selected_host is not None and len(selected_endpoints) == len(DEPLOYMENT_ORDER)
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
                "passing_repairs": host_results.get(host_id, {}).get("passing_repairs"),
            }
            for host_id in HOST_PRIORITY
        ],
        "inherited_deployments": list(V1_REQUIRED_PASSING),
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
    """Run one sealed repair host or aggregate the two immutable artifacts."""

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
        raise ValueError("invalid repair parents: " + "; ".join(parent_errors))
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
