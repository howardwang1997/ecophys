"""Run the frozen outcome-blind Morpho Public Allocator D0 support audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
import yaml

from ecomd.data.morpho_public_allocator_support import (
    ChainSupport,
    LogIdentity,
    canonical_identity_digest,
    canonical_log_identity,
    classify_transaction_logs,
    sanitize_rpc_log,
    summarize_chain_support,
)
from ecomd.data.sqd_portal import SqdPortalClient, SqdPortalError
from scripts.audit_aave_rate_response_d1b import (
    RpcError,
    _get_logs_with_split,
    _keccak_topic,
    _RpcClient,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs/empirical_physics/morpho_public_allocator_pressure_d0_v1.yaml"
QUALIFICATION_PATH = (
    REPO_ROOT / "results/empirical_physics/morpho_public_allocator_pressure_d0_qualification_v1.json"
)
FULL_RESULT_PATH = REPO_ROOT / "results/empirical_physics/morpho_public_allocator_pressure_d0_v1.json"


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("D0 config must be an object")
    return payload


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON artifact must be an object: {path}")
    return payload


def _verify_repo(root: Path, expected_sha: str, *, label: str) -> dict[str, Any]:
    observed = _git(root, "rev-parse", "HEAD")
    if observed != expected_sha:
        raise RuntimeError(f"{label} source commit mismatch: {observed}")
    if _git(root, "status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError(f"{label} source worktree is dirty")
    return {"git_sha": observed, "clean_tracked_worktree": True}


def _verify_source_files(root: Path, files: Mapping[str, Any], *, label: str) -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, expected in files.items():
        path = root / str(relative)
        if not path.is_file():
            raise RuntimeError(f"{label} source file is absent: {relative}")
        digest = _sha256_file(path)
        if digest != str(expected):
            raise RuntimeError(f"{label} source file hash mismatch: {relative}")
        observed[str(relative)] = digest
    return dict(sorted(observed.items()))


def _source_audit(
    config: Mapping[str, Any],
    *,
    sdk_root: Path,
    public_allocator_root: Path,
    morpho_blue_root: Path,
) -> dict[str, Any]:
    official = config["official_sources"]
    roots = {
        "morpho_sdks": sdk_root,
        "public_allocator": public_allocator_root,
        "morpho_blue": morpho_blue_root,
    }
    repositories: dict[str, Any] = {}
    file_hashes: dict[str, Any] = {}
    for label, root in roots.items():
        expected = official[label]
        repositories[label] = _verify_repo(root, str(expected["expected_git_sha"]), label=label)
        file_hashes[label] = _verify_source_files(root, expected["files"], label=label)

    sdk_addresses = (sdk_root / "packages/morpho-ts/src/addresses.ts").read_text(encoding="utf-8")
    required_sdk_fragments = (
        'publicAllocator: "0xfd32fA2ca22c76dD6E550706Ad913FC6CE91c75D"',
        'publicAllocator: "0xA090dD1a701408Df1d4d0B85b716c87565f90467"',
        "publicAllocator: 19375099n",
        "publicAllocator: 13979545n",
    )
    if any(fragment not in sdk_addresses for fragment in required_sdk_fragments):
        raise RuntimeError("official SDK lacks a frozen Public Allocator deployment fragment")
    for chain in config["chains"].values():
        for key in ("morpho", "public_allocator"):
            if str(chain[key]).lower() not in sdk_addresses.lower():
                raise RuntimeError(f"frozen {key} is absent from official SDK source")

    allocator_events = (public_allocator_root / "src/libraries/EventsLib.sol").read_text(encoding="utf-8")
    blue_events = (morpho_blue_root / "src/libraries/EventsLib.sol").read_text(encoding="utf-8")
    sdk_abis = (sdk_root / "packages/morpho-ts/src/abis.ts").read_text(encoding="utf-8")
    for name in ("PublicWithdrawal", "PublicReallocateTo"):
        if f"event {name}(" not in allocator_events or f'name: "{name}"' not in sdk_abis:
            raise RuntimeError(f"{name} is absent from pinned official source")
    if "event Borrow(" not in blue_events:
        raise RuntimeError("Borrow is absent from pinned Morpho Blue source")

    for record in config["event_signatures"].values():
        if _keccak_topic(str(record["signature"])) != str(record["topic0"]).lower():
            raise RuntimeError(f"frozen event topic mismatch: {record['signature']}")
    return {
        "repositories": repositories,
        "file_sha256": file_hashes,
        "sdk_deployments_match": True,
        "event_names_and_topics_match": True,
    }


def _rpc_client(url: str, transport: Mapping[str, Any]) -> _RpcClient:
    return _RpcClient(
        url=url,
        timeout=int(transport["rpc_timeout_seconds"]),
        transport_retries=int(transport["rpc_retry_attempts"]),
        minimum_request_interval_seconds=float(transport["rpc_minimum_request_interval_seconds"]),
        rate_limit_retries=int(transport["rpc_retry_attempts"]),
        rate_limit_backoff_initial_seconds=float(transport["rpc_retry_backoff_seconds"]),
        rate_limit_backoff_max_seconds=30.0,
    )


def _rpc_stats(client: _RpcClient, *, observed_payload_bytes: int) -> dict[str, Any]:
    return {
        "method_counts": dict(sorted(client.method_counts.items())),
        "log_range_splits": client.log_range_splits,
        "log_topic_splits": client.log_topic_splits,
        "rate_limit_retry_count": client.rate_limit_retry_count,
        "rate_limit_wait_seconds": client.rate_limit_wait_seconds,
        "server_error_retry_count": client.server_error_retry_count,
        "server_error_wait_seconds": client.server_error_wait_seconds,
        "observed_payload_bytes": observed_payload_bytes,
    }


def _event_topics(config: Mapping[str, Any]) -> tuple[str, str, str]:
    events = config["event_signatures"]
    return (
        str(events["PublicWithdrawal"]["topic0"]).lower(),
        str(events["PublicReallocateTo"]["topic0"]).lower(),
        str(events["Borrow"]["topic0"]).lower(),
    )


def _portal_logs(
    client: SqdPortalClient,
    *,
    address: str,
    topics: Sequence[str],
    from_block: int,
    to_block: int,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    logs, stats = client.finalized_log_identities(
        addresses=[address],
        topics=topics,
        from_block=from_block,
        to_block=to_block,
        include_topics=True,
        include_block_timestamp=True,
    )
    for log in logs:
        raw_topics = log.get("topics")
        if not isinstance(raw_topics, list) or len(raw_topics) != 4:
            raise ValueError("Public Allocator event does not have four topics")
        canonical_log_identity(log)
    return logs, stats


def _rpc_logs(
    client: _RpcClient,
    *,
    address: str,
    topics: Sequence[str],
    from_block: int,
    to_block: int,
    initial_span: int,
) -> tuple[list[dict[str, Any]], int]:
    if initial_span <= 0:
        raise ValueError("initial RPC log span must be positive")
    sanitized: list[dict[str, Any]] = []
    observed_bytes = 0
    start = from_block
    while start <= to_block:
        end = min(to_block, start + initial_span - 1)
        raw_logs = _get_logs_with_split(
            client,
            addresses=[address],
            topics=topics,
            start_block=start,
            end_block_inclusive=end,
            remaining_split_depth=32,
            split_topics_first=True,
        )
        observed_bytes += len(json.dumps(raw_logs, separators=(",", ":")).encode())
        sanitized.extend(sanitize_rpc_log(raw) for raw in raw_logs)
        start = end + 1
    sanitized.sort(
        key=lambda log: (
            int(log["block_number"]),
            int(log["transaction_index"]),
            int(log["log_index"]),
        )
    )
    identities = [canonical_log_identity(log) for log in sanitized]
    if len(identities) != len(set(identities)):
        raise ValueError("RPC returned duplicate canonical log identities")
    return sanitized, observed_bytes


def _identity_set(logs: Sequence[Mapping[str, Any]]) -> set[LogIdentity]:
    return {canonical_log_identity(log) for log in logs}


def _verify_header(header: Mapping[str, Any], chain: Mapping[str, Any], *, label: str) -> None:
    if (
        int(header["number"]) != int(chain["to_block"])
        or str(header["hash"]).lower() != str(chain["to_block_hash"]).lower()
        or int(header["timestamp"]) != int(chain["to_block_timestamp"])
    ):
        raise ValueError(f"{label} cutoff header mismatch")


def _portal_client(chain: Mapping[str, Any], transport: Mapping[str, Any]) -> SqdPortalClient:
    return SqdPortalClient(
        str(chain["portal_url"]),
        timeout_seconds=float(transport["portal_timeout_seconds"]),
        retry_attempts=int(transport["portal_retry_attempts"]),
        retry_backoff_seconds=float(transport["portal_retry_backoff_seconds"]),
    )


def _verify_portal_metadata(observed: Mapping[str, Any], expected: Mapping[str, Any]) -> None:
    for key, value in expected.items():
        if observed.get(key) != value:
            raise ValueError(f"SQD metadata mismatch for {key}")


def _write_result(path: Path, body: dict[str, Any]) -> dict[str, Any]:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite formal artifact: {path}")
    body["canonical_payload_sha256"] = _canonical_sha256(body)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return body


def _refuse_existing_output(path: Path) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite formal artifact: {path}")


def _check_transfer_budget(config: Mapping[str, Any], observed_bytes: int) -> None:
    maximum = float(config["resources"]["maximum_transferred_gb"]) * 1024**3
    if observed_bytes > maximum:
        raise ValueError("frozen transferred-data budget exceeded")


def _base_result(*, phase: str, config_path: Path, source_audit: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "experiment_id": f"morpho_public_allocator_pressure_d0_{phase}_v1",
        "phase": phase,
        "created_utc": datetime.now(UTC).isoformat(),
        "repository": {
            "git_sha": _git(REPO_ROOT, "rev-parse", "HEAD"),
            "worktree_clean_before_run": True,
        },
        "config": {
            "path": str(config_path.relative_to(REPO_ROOT)),
            "sha256": _sha256_file(config_path),
        },
        "source_audit": dict(source_audit),
    }


def _validate_common(config_path: Path) -> tuple[dict[str, Any], Mapping[str, Any]]:
    if _git(REPO_ROOT, "status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("formal D0 phase requires a clean EcoPhys worktree")
    config = _load_yaml(config_path)
    contract = config["contract"]
    if (
        int(contract["version"]) != 1
        or str(contract["status"]) != "frozen_before_public_allocator_event_counts_or_protocol_values"
    ):
        raise RuntimeError("D0 contract is not the frozen v1")
    if set(config["chains"]) != set(config["pass_thresholds"]["required_chains"]):
        raise RuntimeError("frozen required-chain universe differs from configured chains")
    return config, config["transport"]


def run_qualification(
    config_path: Path,
    output_path: Path,
    *,
    sdk_root: Path,
    public_allocator_root: Path,
    morpho_blue_root: Path,
) -> dict[str, Any]:
    """Run only the six frozen transport qualification shards."""
    _refuse_existing_output(output_path)
    started = time.monotonic()
    config, transport = _validate_common(config_path)
    source = _source_audit(
        config,
        sdk_root=sdk_root,
        public_allocator_root=public_allocator_root,
        morpho_blue_root=morpho_blue_root,
    )
    withdrawal_topic, terminal_topic, _ = _event_topics(config)
    chain_results: dict[str, Any] = {}
    for chain_name, chain in config["chains"].items():
        portal = _portal_client(chain, transport)
        full_rpc = _rpc_client(str(chain["full_scan_rpc"]), transport)
        receipt_rpc = _rpc_client(str(chain["receipt_rpc"]), transport)
        rpc_bytes = 0
        try:
            metadata = portal.metadata()
            _verify_portal_metadata(metadata, chain["portal_expected_metadata"])
            portal_header = portal.finalized_block_header(int(chain["to_block"]))
            _verify_header(portal_header, chain, label=f"{chain_name} SQD")
            full_header = full_rpc.block(int(chain["to_block"]))
            receipt_header = receipt_rpc.block(int(chain["to_block"]))
            _verify_header(full_header, chain, label=f"{chain_name} full RPC")
            _verify_header(receipt_header, chain, label=f"{chain_name} receipt RPC")
            shards: list[dict[str, Any]] = []
            for shard in chain["qualification_shards"]:
                start = int(shard["from_block"])
                end = int(shard["to_block"])
                portal_logs, portal_stats = _portal_logs(
                    portal,
                    address=str(chain["public_allocator"]),
                    topics=[withdrawal_topic, terminal_topic],
                    from_block=start,
                    to_block=end,
                )
                rpc_logs, observed_bytes = _rpc_logs(
                    full_rpc,
                    address=str(chain["public_allocator"]),
                    topics=[withdrawal_topic, terminal_topic],
                    from_block=start,
                    to_block=end,
                    initial_span=end - start + 1,
                )
                rpc_bytes += observed_bytes
                _check_transfer_budget(config, rpc_bytes + portal.bytes_received)
                portal_identities = _identity_set(portal_logs)
                rpc_identities = _identity_set(rpc_logs)
                exact = portal_identities == rpc_identities
                shards.append(
                    {
                        "from_block": start,
                        "to_block": end,
                        "event_count": len(portal_identities),
                        "canonical_identity_sha256": canonical_identity_digest(portal_identities),
                        "portal_rpc_exact_identity_match": exact,
                        "portal_stats": portal_stats,
                    }
                )
            chain_pass = all(bool(shard["portal_rpc_exact_identity_match"]) for shard in shards)
            chain_results[str(chain_name)] = {
                "status": "pass" if chain_pass else "fail",
                "cutoff_header_match": True,
                "metadata_match": True,
                "qualification_shards": shards,
                "full_rpc_stats": _rpc_stats(full_rpc, observed_payload_bytes=rpc_bytes),
                "receipt_rpc_stats": _rpc_stats(receipt_rpc, observed_payload_bytes=0),
                "portal_request_count": portal.request_count,
                "portal_retry_count": portal.retry_count,
                "portal_bytes_received": portal.bytes_received,
            }
        except (requests.RequestException, SqdPortalError, RpcError, ValueError) as error:
            chain_results[str(chain_name)] = {
                "status": "fail",
                "transport_error_type": type(error).__name__,
                "transport_error": str(error),
            }
    qualification_pass = all(row.get("status") == "pass" for row in chain_results.values())
    elapsed = time.monotonic() - started
    body = _base_result(phase="qualification", config_path=config_path, source_audit=source)
    body.update(
        {
            "chains": chain_results,
            "qualification_pass": qualification_pass,
            "scientific_decision": (
                "pass_to_single_frozen_full_support_audit"
                if qualification_pass
                else "fail_stop_before_full_support_counts_or_protocol_values"
            ),
            "data_contract": {
                "event_queries_limited_to_six_frozen_qualification_shards": True,
                "decoded_log_data": False,
                "retained_raw_responses_or_event_identities": False,
                "protocol_values_or_outcomes_used": False,
                "gpu_used": False,
            },
            "resources": {
                "wall_seconds": elapsed,
                "single_process_cpu_core_hours_upper_bound": elapsed / 3600.0,
                "maximum_transferred_gb": float(config["resources"]["maximum_transferred_gb"]),
                "gpu_hours": 0,
                "paid_data_usd": 0,
            },
        }
    )
    return _write_result(output_path, body)


def _verify_qualification(path: Path, config_path: Path) -> dict[str, Any]:
    relative = str(path.relative_to(REPO_ROOT))
    _git(REPO_ROOT, "ls-files", "--error-unmatch", relative)
    payload = _load_json(path)
    claimed = str(payload.get("canonical_payload_sha256"))
    body = {key: value for key, value in payload.items() if key != "canonical_payload_sha256"}
    if _canonical_sha256(body) != claimed:
        raise RuntimeError("qualification artifact canonical hash mismatch")
    if payload.get("qualification_pass") is not True:
        raise RuntimeError("qualification artifact did not authorize the full audit")
    if payload.get("config", {}).get("sha256") != _sha256_file(config_path):
        raise RuntimeError("qualification artifact used a different frozen config")
    qualification_commit = str(payload["repository"]["git_sha"])
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", qualification_commit, "HEAD"],
        cwd=REPO_ROOT,
        check=False,
    )
    if ancestry.returncode != 0:
        raise RuntimeError("qualification commit is not an ancestor of the full-run commit")
    return payload


def _receipt_logs(
    client: _RpcClient,
    *,
    transaction_hash: str,
    expected_block_number: int,
    expected_block_hash: str,
    block_timestamp: int,
) -> tuple[list[dict[str, Any]], int]:
    raw = client.call("eth_getTransactionReceipt", [transaction_hash])
    if not isinstance(raw, Mapping):
        raise ValueError(f"transaction receipt is absent: {transaction_hash}")
    observed_bytes = len(json.dumps(raw, separators=(",", ":")).encode())
    if str(raw.get("transactionHash", "")).lower() != transaction_hash.lower():
        raise ValueError("receipt transaction hash mismatch")
    if str(raw.get("blockHash", "")).lower() != expected_block_hash.lower():
        raise ValueError("receipt block hash mismatch")
    try:
        receipt_block_number = int(str(raw.get("blockNumber")), 16)
    except ValueError as error:
        raise ValueError("receipt block number is malformed") from error
    if receipt_block_number != expected_block_number:
        raise ValueError("receipt block number mismatch")
    if raw.get("status") not in {None, "0x1"}:
        raise ValueError("receipt is not successful")
    raw_logs = raw.get("logs")
    if not isinstance(raw_logs, list) or any(not isinstance(log, Mapping) for log in raw_logs):
        raise ValueError("receipt has malformed logs")
    logs = [sanitize_rpc_log(log, block_timestamp=block_timestamp) for log in raw_logs]
    if any(str(log["transaction_hash"]).lower() != transaction_hash.lower() for log in logs):
        raise ValueError("receipt contains a log with another transaction hash")
    return logs, observed_bytes


def _full_chain(
    chain_name: str,
    chain: Mapping[str, Any],
    config: Mapping[str, Any],
    transport: Mapping[str, Any],
) -> tuple[dict[str, Any], ChainSupport | None]:
    withdrawal_topic, terminal_topic, borrow_topic = _event_topics(config)
    allocator = str(chain["public_allocator"]).lower()
    portal = _portal_client(chain, transport)
    full_rpc = _rpc_client(str(chain["full_scan_rpc"]), transport)
    receipt_rpc = _rpc_client(str(chain["receipt_rpc"]), transport)
    rpc_bytes = 0
    receipt_bytes = 0

    metadata = portal.metadata()
    _verify_portal_metadata(metadata, chain["portal_expected_metadata"])
    _verify_header(portal.finalized_block_header(int(chain["to_block"])), chain, label=f"{chain_name} SQD")
    _verify_header(full_rpc.block(int(chain["to_block"])), chain, label=f"{chain_name} full RPC")
    _verify_header(receipt_rpc.block(int(chain["to_block"])), chain, label=f"{chain_name} receipt RPC")

    portal_logs, portal_stats = _portal_logs(
        portal,
        address=allocator,
        topics=[withdrawal_topic, terminal_topic],
        from_block=int(chain["from_block"]),
        to_block=int(chain["to_block"]),
    )
    rpc_logs, rpc_bytes = _rpc_logs(
        full_rpc,
        address=allocator,
        topics=[withdrawal_topic, terminal_topic],
        from_block=int(chain["from_block"]),
        to_block=int(chain["to_block"]),
        initial_span=int(chain["initial_get_logs_span"]),
    )
    portal_set = _identity_set(portal_logs)
    rpc_set = _identity_set(rpc_logs)
    index_only = portal_set - rpc_set
    rpc_only = rpc_set - portal_set
    index_only_fraction = len(index_only) / len(portal_set) if portal_set else 0.0
    preliminary_transport_pass = (
        len(rpc_only) <= int(transport["maximum_rpc_only_events_each_chain"])
        and len(index_only) <= int(transport["maximum_index_only_events_each_chain"])
        and index_only_fraction <= float(transport["maximum_index_only_fraction_each_chain"])
    )
    transport_summary: dict[str, Any] = {
        "portal_event_count": len(portal_set),
        "full_rpc_event_count": len(rpc_set),
        "portal_identity_sha256": canonical_identity_digest(portal_set),
        "full_rpc_identity_sha256": canonical_identity_digest(rpc_set),
        "index_only_event_count": len(index_only),
        "index_only_fraction": index_only_fraction,
        "rpc_only_event_count": len(rpc_only),
        "preliminary_transport_pass": preliminary_transport_pass,
        "portal_stats": portal_stats,
        "full_rpc_stats": _rpc_stats(full_rpc, observed_payload_bytes=rpc_bytes),
        "portal_request_count": portal.request_count,
        "portal_retry_count": portal.retry_count,
        "portal_bytes_received": portal.bytes_received,
    }
    _check_transfer_budget(config, rpc_bytes + portal.bytes_received)
    if not preliminary_transport_pass:
        transport_summary["transport_pass"] = False
        return {
            "status": "transport_fail_before_receipts_or_support",
            "transport": transport_summary,
            "support": None,
        }, None

    by_transaction: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for log in portal_logs:
        by_transaction[str(log["transaction_hash"])].append(log)
    classifications = []
    verified_transactions = 0
    receipt_mismatch_count = 0
    index_only_verified: set[LogIdentity] = set()
    receipt_pa_by_block: dict[int, set[LogIdentity]] = defaultdict(set)
    for transaction_hash, indexed_logs in sorted(by_transaction.items()):
        block_hashes = {str(log["block_hash"]) for log in indexed_logs}
        block_numbers = {int(log["block_number"]) for log in indexed_logs}
        timestamps = {int(log["block_timestamp"]) for log in indexed_logs}
        if len(block_hashes) != 1 or len(block_numbers) != 1 or len(timestamps) != 1:
            raise ValueError("indexed transaction logs disagree on block identity")
        receipt_logs, payload_bytes = _receipt_logs(
            receipt_rpc,
            transaction_hash=transaction_hash,
            expected_block_number=next(iter(block_numbers)),
            expected_block_hash=next(iter(block_hashes)),
            block_timestamp=next(iter(timestamps)),
        )
        receipt_bytes += payload_bytes
        _check_transfer_budget(config, rpc_bytes + receipt_bytes + portal.bytes_received)
        indexed_tx_set = _identity_set(indexed_logs)
        receipt_pa_logs = [
            log
            for log in receipt_logs
            if str(log["contract_address"]).lower() == allocator
            and str(log["topic0"]).lower() in {withdrawal_topic, terminal_topic}
        ]
        receipt_tx_set = _identity_set(receipt_pa_logs)
        if receipt_tx_set != indexed_tx_set:
            receipt_mismatch_count += 1
            continue
        verified_transactions += 1
        index_only_verified.update(indexed_tx_set & index_only)
        for identity in receipt_tx_set:
            receipt_pa_by_block[int(indexed_logs[0]["block_number"])].add(identity)
        classifications.append(
            classify_transaction_logs(
                receipt_logs,
                public_allocator=allocator,
                morpho=str(chain["morpho"]),
                withdrawal_topic0=withdrawal_topic,
                terminal_topic0=terminal_topic,
                borrow_topic0=borrow_topic,
            )
        )

    receipt_verification_rate = verified_transactions / len(by_transaction) if by_transaction else 1.0
    all_index_only_verified = index_only_verified == index_only
    receipt_gate = (
        receipt_mismatch_count == 0 and receipt_verification_rate == 1.0 and all_index_only_verified
    )
    dense_count = int(transport["dense_blocks_checked_each_chain"])
    block_counts = Counter(int(log["block_number"]) for log in portal_logs)
    dense_blocks = [block for block, _ in sorted(block_counts.items(), key=lambda item: (-item[1], item[0]))]
    dense_blocks = dense_blocks[:dense_count]
    portal_by_block: dict[int, set[LogIdentity]] = defaultdict(set)
    rpc_by_block: dict[int, set[LogIdentity]] = defaultdict(set)
    for log in portal_logs:
        portal_by_block[int(log["block_number"])].add(canonical_log_identity(log))
    for log in rpc_logs:
        rpc_by_block[int(log["block_number"])].add(canonical_log_identity(log))
    dense_unresolved = 0
    for block in dense_blocks:
        indexed = portal_by_block[block]
        rpc_block = rpc_by_block.get(block, set())
        receipt_block = receipt_pa_by_block.get(block, set())
        if rpc_block - indexed or receipt_block != indexed:
            dense_unresolved += 1

    transport_pass = preliminary_transport_pass and receipt_gate and dense_unresolved == 0
    transport_summary.update(
        {
            "receipt_transaction_count": len(by_transaction),
            "verified_receipt_transaction_count": verified_transactions,
            "receipt_verification_rate": receipt_verification_rate,
            "receipt_mismatch_count": receipt_mismatch_count,
            "all_index_only_events_receipt_verified": all_index_only_verified,
            "dense_block_count_checked": len(dense_blocks),
            "dense_block_identity_sha256": hashlib.sha256(
                json.dumps(dense_blocks, separators=(",", ":")).encode()
            ).hexdigest(),
            "dense_block_unresolved_mismatch_count": dense_unresolved,
            "transport_pass": transport_pass,
            "full_rpc_stats": _rpc_stats(full_rpc, observed_payload_bytes=rpc_bytes),
            "receipt_rpc_stats": _rpc_stats(receipt_rpc, observed_payload_bytes=receipt_bytes),
            "portal_request_count": portal.request_count,
            "portal_retry_count": portal.retry_count,
            "portal_bytes_received": portal.bytes_received,
            "observed_total_payload_bytes": rpc_bytes + receipt_bytes + portal.bytes_received,
        }
    )
    if not transport_pass:
        return {
            "status": "transport_fail_before_support_interpretation",
            "transport": transport_summary,
            "support": None,
        }, None
    support = summarize_chain_support(classifications)
    return {
        "status": "transport_pass_support_computed",
        "transport": transport_summary,
        "support": support.summary(),
    }, support


def run_full(
    config_path: Path,
    qualification_path: Path,
    output_path: Path,
    *,
    sdk_root: Path,
    public_allocator_root: Path,
    morpho_blue_root: Path,
) -> dict[str, Any]:
    """Run the single full two-chain support audit after qualification."""
    _refuse_existing_output(output_path)
    started = time.monotonic()
    config, transport = _validate_common(config_path)
    qualification = _verify_qualification(qualification_path, config_path)
    source = _source_audit(
        config,
        sdk_root=sdk_root,
        public_allocator_root=public_allocator_root,
        morpho_blue_root=morpho_blue_root,
    )
    chain_results: dict[str, Any] = {}
    supports: dict[str, ChainSupport] = {}
    for chain_name, chain in config["chains"].items():
        try:
            result, support = _full_chain(str(chain_name), chain, config, transport)
        except (requests.RequestException, SqdPortalError, RpcError, ValueError) as error:
            result = {
                "status": "transport_fail_before_support_interpretation",
                "transport_error_type": type(error).__name__,
                "transport_error": str(error),
                "support": None,
            }
            support = None
        chain_results[str(chain_name)] = result
        if support is not None:
            supports[str(chain_name)] = support

    thresholds = config["pass_thresholds"]
    chain_gates: dict[str, Any] = {}
    for chain_name in config["pass_thresholds"]["required_chains"]:
        result = chain_results[str(chain_name)]
        summary = result.get("support")
        if not isinstance(summary, Mapping):
            chain_gates[str(chain_name)] = {
                "transport": False,
                "candidate_transactions": False,
                "active_span": False,
                "active_dates": False,
                "vaults": False,
                "edges": False,
                "classification": False,
                "receipts": False,
            }
            continue
        transport_result = result["transport"]
        chain_gates[str(chain_name)] = {
            "transport": transport_result["transport_pass"] is True,
            "candidate_transactions": int(summary["candidate_transaction_count"])
            >= int(thresholds["minimum_target_matched_candidate_transactions_each_chain"]),
            "active_span": float(summary["active_span_days"])
            >= float(thresholds["minimum_active_span_days_each_chain"]),
            "active_dates": int(summary["active_utc_date_count"])
            >= int(thresholds["minimum_active_utc_dates_each_chain"]),
            "vaults": int(summary["distinct_vault_count"])
            >= int(thresholds["minimum_distinct_vaults_each_chain"]),
            "edges": int(summary["distinct_directed_edge_count"])
            >= int(thresholds["minimum_distinct_edges_each_chain"]),
            "classification": float(summary["classification_rate"])
            >= float(thresholds["minimum_public_allocator_sequence_classification_rate"]),
            "receipts": float(transport_result["receipt_verification_rate"])
            >= float(thresholds["minimum_candidate_receipt_verification_rate"]),
        }
    pooled_candidates = sum(len(supports[name].candidate_transactions) for name in supports)
    pooled_edges = sum(len(supports[name].edges) for name in supports)
    pooled_gates = {
        "all_required_chains_available": set(supports) == set(map(str, thresholds["required_chains"])),
        "candidate_transactions": pooled_candidates
        >= int(thresholds["minimum_target_matched_candidate_transactions_total"]),
        "directed_edges": pooled_edges >= int(thresholds["minimum_distinct_edges_total"]),
    }
    all_pass = all(all(gates.values()) for gates in chain_gates.values()) and all(pooled_gates.values())
    elapsed = time.monotonic() - started
    body = _base_result(phase="full", config_path=config_path, source_audit=source)
    body.update(
        {
            "qualification_artifact": {
                "path": str(qualification_path.relative_to(REPO_ROOT)),
                "canonical_payload_sha256": qualification["canonical_payload_sha256"],
                "git_sha": qualification["repository"]["git_sha"],
            },
            "chains": chain_results,
            "pooled_support": {
                "candidate_transaction_count": pooled_candidates,
                "distinct_chain_qualified_edge_count": pooled_edges,
            },
            "gates": {"chains": chain_gates, "pooled": pooled_gates},
            "d0_pass": all_pass,
            "scientific_decision": (
                "pass_to_separately_frozen_d1_exact_replay"
                if all_pass
                else "fail_stop_before_protocol_values_or_outcomes"
            ),
            "data_contract": {
                "decoded_log_data": False,
                "retained_raw_responses_or_event_identities": False,
                "decoded_amounts_rates_utilization_prices_or_outcomes": False,
                "gpu_used": False,
                "paid_data_used": False,
            },
            "claim_limit": (
                "D0 measures source-exact identity support only. Candidate transactions are not genuine JIT "
                "events until D1 verifies amount compatibility and the official AdaptiveCurveIRM."
            ),
            "resources": {
                "wall_seconds": elapsed,
                "single_process_cpu_core_hours_upper_bound": elapsed / 3600.0,
                "maximum_transferred_gb": float(config["resources"]["maximum_transferred_gb"]),
                "gpu_hours": 0,
                "paid_data_usd": 0,
            },
        }
    )
    return _write_result(output_path, body)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("qualification", "full"), required=True)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--qualification-artifact", type=Path, default=QUALIFICATION_PATH)
    parser.add_argument("--sdk-root", type=Path, required=True)
    parser.add_argument("--public-allocator-root", type=Path, required=True)
    parser.add_argument("--morpho-blue-root", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config_path = args.config.resolve()
    common = {
        "sdk_root": args.sdk_root.resolve(),
        "public_allocator_root": args.public_allocator_root.resolve(),
        "morpho_blue_root": args.morpho_blue_root.resolve(),
    }
    if args.phase == "qualification":
        output = args.output.resolve() if args.output else QUALIFICATION_PATH
        result = run_qualification(config_path, output, **common)
    else:
        output = args.output.resolve() if args.output else FULL_RESULT_PATH
        result = run_full(
            config_path,
            args.qualification_artifact.resolve(),
            output,
            **common,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
