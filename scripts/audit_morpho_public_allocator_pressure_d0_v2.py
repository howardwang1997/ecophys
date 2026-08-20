"""Run the transport-amended Morpho Public Allocator D0 audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import threading
import time
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path
from typing import Any

import requests

from ecomd.data.morpho_public_allocator_support import (
    ChainSupport,
    LogIdentity,
    TransactionClassification,
    canonical_identity_digest,
    canonical_log_identity,
    classify_transaction_logs,
    summarize_chain_support,
)
from ecomd.data.sqd_portal import SqdPortalError
from scripts.audit_aave_rate_response_d1b import RpcError, _RpcClient
from scripts.audit_morpho_public_allocator_pressure_d0 import (
    CONFIG_PATH,
    QUALIFICATION_PATH,
    _canonical_sha256,
    _check_transfer_budget,
    _event_topics,
    _git,
    _identity_set,
    _load_json,
    _load_yaml,
    _portal_client,
    _portal_logs,
    _receipt_logs,
    _refuse_existing_output,
    _rpc_client,
    _rpc_logs,
    _rpc_stats,
    _sha256_file,
    _source_audit,
    _validate_common,
    _verify_header,
    _verify_portal_metadata,
    _verify_qualification,
    _write_result,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
AMENDMENT_PATH = REPO_ROOT / "configs/empirical_physics/morpho_public_allocator_pressure_d0_transport_v2.yaml"
QUALIFICATION_V2_PATH = (
    REPO_ROOT / "results/empirical_physics/morpho_public_allocator_pressure_d0_qualification_v2.json"
)
FULL_RESULT_V2_PATH = REPO_ROOT / "results/empirical_physics/morpho_public_allocator_pressure_d0_v2.json"
RAW_EVM_IDENTITY = re.compile(r"(?<![0-9A-Fa-f])0x(?:[0-9A-Fa-f]{64}|[0-9A-Fa-f]{40})(?![0-9A-Fa-f])")


class ProgressReporter:
    """Emit outcome-blind technical progress at a bounded cadence."""

    def __init__(self, interval_seconds: float) -> None:
        if interval_seconds <= 0:
            raise ValueError("progress interval must be positive")
        self.interval_seconds = interval_seconds
        self.started = time.monotonic()
        self.last_emitted = 0.0
        self.lock = threading.Lock()

    def emit(
        self,
        stage: str,
        *,
        completed: int | None = None,
        total: int | None = None,
        force: bool = False,
    ) -> None:
        now = time.monotonic()
        with self.lock:
            if not force and now - self.last_emitted < self.interval_seconds:
                return
            payload: dict[str, Any] = {
                "stage": stage,
                "elapsed_seconds": round(now - self.started, 3),
            }
            if completed is not None:
                payload["completed_work_units"] = completed
            if total is not None:
                payload["total_work_units"] = total
            print(f"D0_PROGRESS {json.dumps(payload, sort_keys=True)}", flush=True)
            self.last_emitted = now


def inclusive_block_shards(from_block: int, to_block: int, span: int) -> list[tuple[int, int]]:
    """Return deterministic disjoint inclusive ranges covering an interval exactly."""
    if from_block < 0 or to_block < from_block or span <= 0:
        raise ValueError("invalid inclusive block-shard request")
    shards: list[tuple[int, int]] = []
    start = from_block
    while start <= to_block:
        end = min(to_block, start + span - 1)
        shards.append((start, end))
        start = end + 1
    if shards[0][0] != from_block or shards[-1][1] != to_block:
        raise AssertionError("block shards do not cover the requested endpoints")
    if any(left[1] + 1 != right[0] for left, right in pairwise(shards)):
        raise AssertionError("block shards contain a gap or overlap")
    return shards


def _verify_amendment(amendment_path: Path, parent_config_path: Path) -> dict[str, Any]:
    amendment = _load_yaml(amendment_path)
    contract = amendment.get("contract")
    if not isinstance(contract, Mapping):
        raise RuntimeError("transport amendment has no contract")
    if (
        int(contract.get("version", -1)) != 2
        or contract.get("name") != "morpho_public_allocator_pressure_d0_transport_amendment"
        or contract.get("status") != "frozen_before_completed_full_support_result"
    ):
        raise RuntimeError("transport amendment is not the frozen v2 contract")
    expected_parent = str(parent_config_path.relative_to(REPO_ROOT))
    if contract.get("parent_config_path") != expected_parent:
        raise RuntimeError("transport amendment parent path mismatch")
    if contract.get("parent_config_sha256") != _sha256_file(parent_config_path):
        raise RuntimeError("transport amendment parent hash mismatch")
    if contract.get("parent_qualification_path") != str(QUALIFICATION_PATH.relative_to(REPO_ROOT)):
        raise RuntimeError("transport amendment parent qualification path mismatch")

    execution = amendment.get("execution")
    invariance = amendment.get("transport_invariance")
    qualification_gate = amendment.get("qualification_gate")
    formal_run = amendment.get("formal_run")
    if not all(
        isinstance(value, Mapping) for value in (execution, invariance, qualification_gate, formal_run)
    ):
        raise RuntimeError("transport amendment lacks a required mapping")
    assert isinstance(execution, Mapping)
    assert isinstance(invariance, Mapping)
    assert isinstance(qualification_gate, Mapping)
    assert isinstance(formal_run, Mapping)
    required_true = (
        "block_shards_are_disjoint_inclusive_and_cover_parent_interval_exactly",
        "canonical_identity_union_is_order_independent",
        "duplicate_canonical_identity_is_fatal",
        "every_shard_uses_parent_portal_url_filter_fields_and_retry_policy",
        "full_rpc_receipt_and_support_rules_unchanged",
    )
    if any(invariance.get(key) is not True for key in required_true):
        raise RuntimeError("transport amendment weakens a required acquisition invariant")
    if invariance.get("raw_responses_or_event_identities_persisted") is not False:
        raise RuntimeError("transport amendment permits raw identity persistence")
    if any(value is not True for value in qualification_gate.values()):
        raise RuntimeError("transport amendment weakens qualification reproduction")
    if execution.get("mode") != "independent_chain_artifacts_then_exact_merge":
        raise RuntimeError("transport amendment execution mode mismatch")
    if execution.get("launch_all_required_chains_before_reading_any_chain_result") is not True:
        raise RuntimeError("transport amendment permits adaptive chain launch")
    if execution.get("cuda_visible_devices") != "":
        raise RuntimeError("transport amendment does not explicitly hide CUDA")
    if int(execution.get("maximum_chains_per_host", -1)) != 1:
        raise RuntimeError("transport amendment must assign at most one chain per host")
    if formal_run.get("required_chains") != ["ethereum", "base"]:
        raise RuntimeError("transport amendment required-chain universe changed")

    qualification = execution.get("qualification")
    full_chain = execution.get("full_chain")
    if not isinstance(qualification, Mapping) or not isinstance(full_chain, Mapping):
        raise RuntimeError("transport amendment lacks execution parameters")
    positive = (
        int(qualification.get("portal_block_shard_span", 0)),
        int(qualification.get("portal_max_workers", 0)),
        int(full_chain.get("portal_block_shard_span", 0)),
        int(full_chain.get("portal_max_workers", 0)),
        int(full_chain.get("receipt_max_workers", 0)),
        float(full_chain.get("receipt_minimum_request_interval_seconds_per_worker", 0)),
        float(execution.get("progress_interval_seconds", 0)),
    )
    if any(value <= 0 for value in positive):
        raise RuntimeError("transport amendment execution parameters must be positive")
    return amendment


def _verify_parent_qualification(amendment: Mapping[str, Any], parent_config_path: Path) -> dict[str, Any]:
    qualification = _verify_qualification(QUALIFICATION_PATH, parent_config_path)
    expected = str(amendment["contract"]["parent_qualification_canonical_sha256"])
    if qualification["canonical_payload_sha256"] != expected:
        raise RuntimeError("parent qualification canonical hash mismatch")
    return qualification


def _base_result_v2(
    *,
    phase: str,
    parent_config_path: Path,
    amendment_path: Path,
    source_audit: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 2,
        "experiment_id": f"morpho_public_allocator_pressure_d0_{phase}_v2",
        "phase": phase,
        "created_utc": datetime.now(UTC).isoformat(),
        "repository": {
            "git_sha": _git(REPO_ROOT, "rev-parse", "HEAD"),
            "worktree_clean_before_run": True,
        },
        "parent_config": {
            "path": str(parent_config_path.relative_to(REPO_ROOT)),
            "sha256": _sha256_file(parent_config_path),
        },
        "transport_amendment": {
            "path": str(amendment_path.relative_to(REPO_ROOT)),
            "sha256": _sha256_file(amendment_path),
        },
        "source_audit": dict(source_audit),
    }


def _assert_no_raw_evm_identities(value: Any) -> None:
    if isinstance(value, Mapping):
        for nested in value.values():
            _assert_no_raw_evm_identities(nested)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for nested in value:
            _assert_no_raw_evm_identities(nested)
        return
    if isinstance(value, str) and RAW_EVM_IDENTITY.search(value):
        raise RuntimeError("aggregate artifact would retain a raw EVM identity")


def _redact_raw_evm_identities(value: str) -> str:
    return RAW_EVM_IDENTITY.sub("<redacted_evm_identity>", value)


def _write_aggregate_result(path: Path, body: dict[str, Any]) -> dict[str, Any]:
    _assert_no_raw_evm_identities(body)
    return _write_result(path, body)


@dataclass(frozen=True)
class PortalShardResult:
    index: int
    logs: tuple[dict[str, Any], ...]
    stats: Mapping[str, int]


def _portal_shard(
    index: int,
    chain: Mapping[str, Any],
    transport: Mapping[str, Any],
    address: str,
    topics: Sequence[str],
    block_range: tuple[int, int],
) -> PortalShardResult:
    client = _portal_client(chain, transport)
    logs, stats = _portal_logs(
        client,
        address=address,
        topics=topics,
        from_block=block_range[0],
        to_block=block_range[1],
    )
    return PortalShardResult(index=index, logs=tuple(logs), stats=stats)


def parallel_portal_logs(
    chain: Mapping[str, Any],
    transport: Mapping[str, Any],
    *,
    address: str,
    topics: Sequence[str],
    from_block: int,
    to_block: int,
    shard_span: int,
    max_workers: int,
    progress: ProgressReporter | None = None,
    stage: str = "portal",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Read a finalized interval as a deterministic parallel union."""
    if max_workers <= 0:
        raise ValueError("Portal worker count must be positive")
    ranges = inclusive_block_shards(from_block, to_block, shard_span)
    results: list[PortalShardResult | None] = [None] * len(ranges)
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="d0-portal") as executor:
        futures: dict[Future[PortalShardResult], int] = {
            executor.submit(_portal_shard, index, chain, transport, address, topics, block_range): index
            for index, block_range in enumerate(ranges)
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            index = futures[future]
            try:
                results[index] = future.result()
            except Exception as error:
                for pending in futures:
                    pending.cancel()
                raise ValueError(f"Portal shard {index} failed with {type(error).__name__}") from error
            if progress is not None:
                progress.emit(stage, completed=completed, total=len(ranges))
    if any(result is None for result in results):
        raise AssertionError("Portal parallel collection is incomplete")

    logs: list[dict[str, Any]] = []
    totals: Counter[str] = Counter()
    for result in results:
        assert result is not None
        logs.extend(result.logs)
        totals.update({key: int(value) for key, value in result.stats.items()})
    logs.sort(
        key=lambda log: (
            int(log["block_number"]),
            int(log["transaction_index"]),
            int(log["log_index"]),
        )
    )
    identities = [canonical_log_identity(log) for log in logs]
    if len(identities) != len(set(identities)):
        raise ValueError("parallel Portal union contains a duplicate canonical identity")
    if progress is not None:
        progress.emit(stage, completed=len(ranges), total=len(ranges), force=True)
    return logs, {
        "block_shard_span": shard_span,
        "shard_count": len(ranges),
        "completed_shard_count": len(ranges),
        "max_workers": max_workers,
        "page_count": totals["page_count"],
        "header_count": totals["header_count"],
        "request_count": totals["request_count"],
        "retry_count": totals["retry_count"],
        "bytes_received": totals["bytes_received"],
    }


def _parent_shard_lookup(
    parent_qualification: Mapping[str, Any],
) -> dict[tuple[str, int, int], Mapping[str, Any]]:
    rows: dict[tuple[str, int, int], Mapping[str, Any]] = {}
    for chain_name, chain in parent_qualification["chains"].items():
        for shard in chain["qualification_shards"]:
            key = (str(chain_name), int(shard["from_block"]), int(shard["to_block"]))
            rows[key] = shard
    return rows


def run_qualification_v2(
    parent_config_path: Path,
    amendment_path: Path,
    output_path: Path,
    *,
    sdk_root: Path,
    public_allocator_root: Path,
    morpho_blue_root: Path,
) -> dict[str, Any]:
    """Reproduce the six frozen qualification identities under parallel partitioning."""
    _refuse_existing_output(output_path)
    started = time.monotonic()
    config, transport = _validate_common(parent_config_path)
    amendment = _verify_amendment(amendment_path, parent_config_path)
    parent_qualification = _verify_parent_qualification(amendment, parent_config_path)
    source = _source_audit(
        config,
        sdk_root=sdk_root,
        public_allocator_root=public_allocator_root,
        morpho_blue_root=morpho_blue_root,
    )
    execution = amendment["execution"]
    qualification_execution = execution["qualification"]
    reporter = ProgressReporter(float(execution["progress_interval_seconds"]))
    withdrawal_topic, terminal_topic, _ = _event_topics(config)
    expected_shards = _parent_shard_lookup(parent_qualification)
    chain_results: dict[str, Any] = {}
    for chain_name, chain in config["chains"].items():
        reporter.emit(f"qualification:{chain_name}:start", force=True)
        coordinator = _portal_client(chain, transport)
        full_rpc = _rpc_client(str(chain["full_scan_rpc"]), transport)
        receipt_rpc = _rpc_client(str(chain["receipt_rpc"]), transport)
        rpc_bytes = 0
        try:
            metadata = coordinator.metadata()
            _verify_portal_metadata(metadata, chain["portal_expected_metadata"])
            _verify_header(
                coordinator.finalized_block_header(int(chain["to_block"])),
                chain,
                label=f"{chain_name} SQD",
            )
            _verify_header(full_rpc.block(int(chain["to_block"])), chain, label=f"{chain_name} full RPC")
            _verify_header(
                receipt_rpc.block(int(chain["to_block"])), chain, label=f"{chain_name} receipt RPC"
            )
            shards: list[dict[str, Any]] = []
            portal_totals: Counter[str] = Counter()
            for outer_index, shard in enumerate(chain["qualification_shards"]):
                start = int(shard["from_block"])
                end = int(shard["to_block"])
                portal_logs, portal_stats = parallel_portal_logs(
                    chain,
                    transport,
                    address=str(chain["public_allocator"]),
                    topics=[withdrawal_topic, terminal_topic],
                    from_block=start,
                    to_block=end,
                    shard_span=int(qualification_execution["portal_block_shard_span"]),
                    max_workers=int(qualification_execution["portal_max_workers"]),
                    progress=reporter,
                    stage=f"qualification:{chain_name}:outer_shard_{outer_index}",
                )
                portal_totals.update(
                    {
                        "request_count": int(portal_stats["request_count"]),
                        "retry_count": int(portal_stats["retry_count"]),
                        "bytes_received": int(portal_stats["bytes_received"]),
                    }
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
                total_bytes = rpc_bytes + coordinator.bytes_received + portal_totals["bytes_received"]
                _check_transfer_budget(config, total_bytes)
                portal_identities = _identity_set(portal_logs)
                rpc_identities = _identity_set(rpc_logs)
                digest = canonical_identity_digest(portal_identities)
                expected = expected_shards[(str(chain_name), start, end)]
                parent_reproduced = len(portal_identities) == int(expected["event_count"]) and digest == str(
                    expected["canonical_identity_sha256"]
                )
                shards.append(
                    {
                        "from_block": start,
                        "to_block": end,
                        "event_count": len(portal_identities),
                        "canonical_identity_sha256": digest,
                        "portal_rpc_exact_identity_match": portal_identities == rpc_identities,
                        "parent_v1_identity_reproduced": parent_reproduced,
                        "parallel_portal_stats": portal_stats,
                    }
                )
            chain_pass = all(
                row["portal_rpc_exact_identity_match"] is True
                and row["parent_v1_identity_reproduced"] is True
                for row in shards
            )
            chain_results[str(chain_name)] = {
                "status": "pass" if chain_pass else "fail",
                "cutoff_header_match": True,
                "metadata_match": True,
                "qualification_shards": shards,
                "full_rpc_stats": _rpc_stats(full_rpc, observed_payload_bytes=rpc_bytes),
                "receipt_rpc_stats": _rpc_stats(receipt_rpc, observed_payload_bytes=0),
                "portal_coordinator_request_count": coordinator.request_count,
                "portal_coordinator_retry_count": coordinator.retry_count,
                "portal_coordinator_bytes_received": coordinator.bytes_received,
                "parallel_portal_request_count": portal_totals["request_count"],
                "parallel_portal_retry_count": portal_totals["retry_count"],
                "parallel_portal_bytes_received": portal_totals["bytes_received"],
            }
        except (requests.RequestException, SqdPortalError, RpcError, ValueError) as error:
            chain_results[str(chain_name)] = {
                "status": "fail",
                "transport_error_type": type(error).__name__,
                "transport_error": _redact_raw_evm_identities(str(error)),
            }
        reporter.emit(f"qualification:{chain_name}:complete", force=True)

    qualification_pass = all(row.get("status") == "pass" for row in chain_results.values())
    body = _base_result_v2(
        phase="qualification",
        parent_config_path=parent_config_path,
        amendment_path=amendment_path,
        source_audit=source,
    )
    body.update(
        {
            "parent_qualification": {
                "path": str(QUALIFICATION_PATH.relative_to(REPO_ROOT)),
                "canonical_payload_sha256": parent_qualification["canonical_payload_sha256"],
                "git_sha": parent_qualification["repository"]["git_sha"],
            },
            "chains": chain_results,
            "qualification_pass": qualification_pass,
            "scientific_decision": (
                "pass_to_single_distributed_full_support_audit"
                if qualification_pass
                else "fail_stop_before_full_support_counts_or_protocol_values"
            ),
            "data_contract": {
                "event_queries_limited_to_parent_six_qualification_shards": True,
                "decoded_log_data": False,
                "retained_raw_responses_or_event_identities": False,
                "protocol_values_or_outcomes_used": False,
                "gpu_used": False,
            },
            "resources": {
                "wall_seconds": time.monotonic() - started,
                "maximum_transferred_gb": float(config["resources"]["maximum_transferred_gb"]),
                "gpu_hours": 0,
                "paid_data_usd": 0,
            },
        }
    )
    return _write_aggregate_result(output_path, body)


def _verify_qualification_v2(path: Path, parent_config_path: Path, amendment_path: Path) -> dict[str, Any]:
    relative = str(path.relative_to(REPO_ROOT))
    _git(REPO_ROOT, "ls-files", "--error-unmatch", relative)
    payload = _load_json(path)
    claimed = str(payload.get("canonical_payload_sha256"))
    body = {key: value for key, value in payload.items() if key != "canonical_payload_sha256"}
    if _canonical_sha256(body) != claimed:
        raise RuntimeError("v2 qualification artifact canonical hash mismatch")
    if payload.get("qualification_pass") is not True:
        raise RuntimeError("v2 qualification did not authorize the full audit")
    if payload.get("parent_config", {}).get("sha256") != _sha256_file(parent_config_path):
        raise RuntimeError("v2 qualification used a different parent config")
    if payload.get("transport_amendment", {}).get("sha256") != _sha256_file(amendment_path):
        raise RuntimeError("v2 qualification used a different transport amendment")
    qualification_commit = str(payload["repository"]["git_sha"])
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", qualification_commit, "HEAD"],
        cwd=REPO_ROOT,
        check=False,
    )
    if ancestry.returncode != 0:
        raise RuntimeError("v2 qualification commit is not an ancestor of the full-run commit")
    return payload


def _formal_batch_id(*, amendment_path: Path, qualification: Mapping[str, Any], git_sha: str) -> str:
    payload = {
        "git_sha": git_sha,
        "transport_amendment_sha256": _sha256_file(amendment_path),
        "qualification_canonical_payload_sha256": qualification["canonical_payload_sha256"],
    }
    return _canonical_sha256(payload)


def _validate_worker_environment(chain_name: str, amendment: Mapping[str, Any]) -> str:
    expected = str(amendment["formal_run"][f"{chain_name}_worker"])
    observed = os.environ.get("ECOPHYS_D0_WORKER_ID")
    if observed != expected:
        raise RuntimeError(f"formal chain requires ECOPHYS_D0_WORKER_ID={expected}")
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise RuntimeError("formal chain requires CUDA_VISIBLE_DEVICES to be empty")
    return expected


@dataclass(frozen=True)
class ReceiptResult:
    index: int
    block_number: int
    receipt_pa_identities: frozenset[LogIdentity]
    verified_index_only: frozenset[LogIdentity]
    classification: TransactionClassification | None
    payload_bytes: int
    exact_match: bool


def _receipt_client_with_interval(
    url: str, transport: Mapping[str, Any], minimum_interval_seconds: float
) -> _RpcClient:
    amended = dict(transport)
    amended["rpc_minimum_request_interval_seconds"] = minimum_interval_seconds
    return _rpc_client(url, amended)


def parallel_receipt_classifications(
    by_transaction: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    chain: Mapping[str, Any],
    transport: Mapping[str, Any],
    allocator: str,
    withdrawal_topic: str,
    terminal_topic: str,
    borrow_topic: str,
    index_only: set[LogIdentity],
    max_workers: int,
    minimum_interval_seconds: float,
    progress: ProgressReporter | None = None,
    stage: str = "receipts",
) -> tuple[list[TransactionClassification], dict[int, set[LogIdentity]], set[LogIdentity], dict[str, Any]]:
    """Fetch and classify receipts concurrently without persisting identity-bearing rows."""
    if max_workers <= 0 or minimum_interval_seconds <= 0:
        raise ValueError("receipt concurrency and pacing must be positive")
    transactions = sorted(by_transaction.items())
    local = threading.local()
    clients: list[_RpcClient] = []
    clients_lock = threading.Lock()

    def client_for_thread() -> _RpcClient:
        client = getattr(local, "client", None)
        if not isinstance(client, _RpcClient):
            client = _receipt_client_with_interval(
                str(chain["receipt_rpc"]), transport, minimum_interval_seconds
            )
            local.client = client
            with clients_lock:
                clients.append(client)
        return client

    def work(index: int, transaction_hash: str, indexed_logs: Sequence[Mapping[str, Any]]) -> ReceiptResult:
        block_hashes = {str(log["block_hash"]) for log in indexed_logs}
        block_numbers = {int(log["block_number"]) for log in indexed_logs}
        timestamps = {int(log["block_timestamp"]) for log in indexed_logs}
        if len(block_hashes) != 1 or len(block_numbers) != 1 or len(timestamps) != 1:
            raise ValueError(f"receipt work unit {index} has inconsistent indexed block identity")
        try:
            receipt_logs, payload_bytes = _receipt_logs(
                client_for_thread(),
                transaction_hash=transaction_hash,
                expected_block_number=next(iter(block_numbers)),
                expected_block_hash=next(iter(block_hashes)),
                block_timestamp=next(iter(timestamps)),
            )
        except Exception as error:
            raise ValueError(f"receipt work unit {index} failed with {type(error).__name__}") from error
        indexed_tx_set = _identity_set(indexed_logs)
        receipt_pa_logs = [
            log
            for log in receipt_logs
            if str(log["contract_address"]).lower() == allocator
            and str(log["topic0"]).lower() in {withdrawal_topic, terminal_topic}
        ]
        receipt_tx_set = _identity_set(receipt_pa_logs)
        exact = receipt_tx_set == indexed_tx_set
        classification = None
        if exact:
            classification = classify_transaction_logs(
                receipt_logs,
                public_allocator=allocator,
                morpho=str(chain["morpho"]),
                withdrawal_topic0=withdrawal_topic,
                terminal_topic0=terminal_topic,
                borrow_topic0=borrow_topic,
            )
        return ReceiptResult(
            index=index,
            block_number=next(iter(block_numbers)),
            receipt_pa_identities=frozenset(receipt_tx_set),
            verified_index_only=frozenset(receipt_tx_set & index_only),
            classification=classification,
            payload_bytes=payload_bytes,
            exact_match=exact,
        )

    results: list[ReceiptResult | None] = [None] * len(transactions)
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="d0-receipt") as executor:
        futures: dict[Future[ReceiptResult], int] = {
            executor.submit(work, index, transaction_hash, indexed_logs): index
            for index, (transaction_hash, indexed_logs) in enumerate(transactions)
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            index = futures[future]
            try:
                results[index] = future.result()
            except Exception as error:
                for pending in futures:
                    pending.cancel()
                raise ValueError(f"receipt work unit {index} failed") from error
            if progress is not None:
                progress.emit(stage, completed=completed, total=len(transactions))
    if any(result is None for result in results):
        raise AssertionError("receipt parallel collection is incomplete")

    classifications: list[TransactionClassification] = []
    receipt_pa_by_block: dict[int, set[LogIdentity]] = defaultdict(set)
    verified_index_only: set[LogIdentity] = set()
    payload_bytes = 0
    mismatch_count = 0
    for result in results:
        assert result is not None
        payload_bytes += result.payload_bytes
        if not result.exact_match:
            mismatch_count += 1
            continue
        verified_index_only.update(result.verified_index_only)
        receipt_pa_by_block[result.block_number].update(result.receipt_pa_identities)
        assert result.classification is not None
        classifications.append(result.classification)
    stats = _aggregate_rpc_stats(clients, observed_payload_bytes=payload_bytes)
    stats.update(
        {
            "receipt_transaction_count": len(transactions),
            "verified_receipt_transaction_count": len(transactions) - mismatch_count,
            "receipt_mismatch_count": mismatch_count,
            "max_workers": max_workers,
            "minimum_request_interval_seconds_per_worker": minimum_interval_seconds,
        }
    )
    if progress is not None:
        progress.emit(stage, completed=len(transactions), total=len(transactions), force=True)
    return classifications, receipt_pa_by_block, verified_index_only, stats


def _aggregate_rpc_stats(clients: Sequence[_RpcClient], *, observed_payload_bytes: int) -> dict[str, Any]:
    methods: Counter[str] = Counter()
    totals: Counter[str] = Counter()
    rate_wait = 0.0
    server_wait = 0.0
    for client in clients:
        stats = _rpc_stats(client, observed_payload_bytes=0)
        methods.update({str(key): int(value) for key, value in stats["method_counts"].items()})
        for key in (
            "log_range_splits",
            "log_topic_splits",
            "rate_limit_retry_count",
            "server_error_retry_count",
        ):
            totals[key] += int(stats[key])
        rate_wait += float(stats["rate_limit_wait_seconds"])
        server_wait += float(stats["server_error_wait_seconds"])
    return {
        "method_counts": dict(sorted(methods.items())),
        "log_range_splits": totals["log_range_splits"],
        "log_topic_splits": totals["log_topic_splits"],
        "rate_limit_retry_count": totals["rate_limit_retry_count"],
        "rate_limit_wait_seconds": rate_wait,
        "server_error_retry_count": totals["server_error_retry_count"],
        "server_error_wait_seconds": server_wait,
        "observed_payload_bytes": observed_payload_bytes,
        "client_count": len(clients),
    }


def _full_chain_v2(
    chain_name: str,
    chain: Mapping[str, Any],
    config: Mapping[str, Any],
    transport: Mapping[str, Any],
    execution: Mapping[str, Any],
    reporter: ProgressReporter,
) -> tuple[dict[str, Any], ChainSupport | None]:
    withdrawal_topic, terminal_topic, borrow_topic = _event_topics(config)
    allocator = str(chain["public_allocator"]).lower()
    coordinator = _portal_client(chain, transport)
    full_rpc = _rpc_client(str(chain["full_scan_rpc"]), transport)
    receipt_header_rpc = _rpc_client(str(chain["receipt_rpc"]), transport)
    rpc_bytes = 0

    reporter.emit(f"full:{chain_name}:headers", force=True)
    metadata = coordinator.metadata()
    _verify_portal_metadata(metadata, chain["portal_expected_metadata"])
    _verify_header(
        coordinator.finalized_block_header(int(chain["to_block"])),
        chain,
        label=f"{chain_name} SQD",
    )
    _verify_header(full_rpc.block(int(chain["to_block"])), chain, label=f"{chain_name} full RPC")
    _verify_header(receipt_header_rpc.block(int(chain["to_block"])), chain, label=f"{chain_name} receipt RPC")

    reporter.emit(f"full:{chain_name}:portal", force=True)
    portal_logs, portal_stats = parallel_portal_logs(
        chain,
        transport,
        address=allocator,
        topics=[withdrawal_topic, terminal_topic],
        from_block=int(chain["from_block"]),
        to_block=int(chain["to_block"]),
        shard_span=int(execution["portal_block_shard_span"]),
        max_workers=int(execution["portal_max_workers"]),
        progress=reporter,
        stage=f"full:{chain_name}:portal",
    )
    reporter.emit(f"full:{chain_name}:full_rpc", force=True)
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
        "parallel_portal_stats": portal_stats,
        "full_rpc_stats": _rpc_stats(full_rpc, observed_payload_bytes=rpc_bytes),
        "portal_coordinator_request_count": coordinator.request_count,
        "portal_coordinator_retry_count": coordinator.retry_count,
        "portal_coordinator_bytes_received": coordinator.bytes_received,
    }
    total_bytes = rpc_bytes + int(portal_stats["bytes_received"]) + coordinator.bytes_received
    _check_transfer_budget(config, total_bytes)
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
    reporter.emit(f"full:{chain_name}:receipts", force=True)
    classifications, receipt_pa_by_block, index_only_verified, receipt_stats = (
        parallel_receipt_classifications(
            by_transaction,
            chain=chain,
            transport=transport,
            allocator=allocator,
            withdrawal_topic=withdrawal_topic,
            terminal_topic=terminal_topic,
            borrow_topic=borrow_topic,
            index_only=index_only,
            max_workers=int(execution["receipt_max_workers"]),
            minimum_interval_seconds=float(execution["receipt_minimum_request_interval_seconds_per_worker"]),
            progress=reporter,
            stage=f"full:{chain_name}:receipts",
        )
    )
    receipt_count = int(receipt_stats["receipt_transaction_count"])
    verified_count = int(receipt_stats["verified_receipt_transaction_count"])
    receipt_mismatch_count = int(receipt_stats["receipt_mismatch_count"])
    receipt_verification_rate = verified_count / receipt_count if receipt_count else 1.0
    all_index_only_verified = index_only_verified == index_only
    receipt_gate = (
        receipt_mismatch_count == 0 and receipt_verification_rate == 1.0 and all_index_only_verified
    )

    dense_count = int(transport["dense_blocks_checked_each_chain"])
    block_counts = Counter(int(log["block_number"]) for log in portal_logs)
    dense_blocks = [block for block, _ in sorted(block_counts.items(), key=lambda item: (-item[1], item[0]))][
        :dense_count
    ]
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
    receipt_bytes = int(receipt_stats["observed_payload_bytes"])
    total_bytes += receipt_bytes
    _check_transfer_budget(config, total_bytes)
    transport_summary.update(
        {
            "receipt_transaction_count": receipt_count,
            "verified_receipt_transaction_count": verified_count,
            "receipt_verification_rate": receipt_verification_rate,
            "receipt_mismatch_count": receipt_mismatch_count,
            "all_index_only_events_receipt_verified": all_index_only_verified,
            "dense_block_count_checked": len(dense_blocks),
            "dense_block_identity_sha256": hashlib.sha256(
                json.dumps(dense_blocks, separators=(",", ":")).encode()
            ).hexdigest(),
            "dense_block_unresolved_mismatch_count": dense_unresolved,
            "transport_pass": transport_pass,
            "receipt_rpc_stats": receipt_stats,
            "observed_total_payload_bytes": total_bytes,
        }
    )
    if not transport_pass:
        return {
            "status": "transport_fail_before_support_interpretation",
            "transport": transport_summary,
            "support": None,
        }, None
    support = summarize_chain_support(classifications)
    reporter.emit(f"full:{chain_name}:complete", force=True)
    return {
        "status": "transport_pass_support_computed",
        "transport": transport_summary,
        "support": support.summary(),
    }, support


def run_chain_v2(
    parent_config_path: Path,
    amendment_path: Path,
    qualification_path: Path,
    output_path: Path,
    *,
    chain_name: str,
    sdk_root: Path,
    public_allocator_root: Path,
    morpho_blue_root: Path,
) -> dict[str, Any]:
    """Run one required chain of the single distributed full audit."""
    _refuse_existing_output(output_path)
    started = time.monotonic()
    config, transport = _validate_common(parent_config_path)
    amendment = _verify_amendment(amendment_path, parent_config_path)
    qualification = _verify_qualification_v2(qualification_path, parent_config_path, amendment_path)
    if chain_name not in config["chains"] or chain_name not in amendment["formal_run"]["required_chains"]:
        raise ValueError(f"chain is outside the frozen v2 universe: {chain_name}")
    worker_id = _validate_worker_environment(chain_name, amendment)
    git_sha = _git(REPO_ROOT, "rev-parse", "HEAD")
    batch_id = _formal_batch_id(amendment_path=amendment_path, qualification=qualification, git_sha=git_sha)
    source = _source_audit(
        config,
        sdk_root=sdk_root,
        public_allocator_root=public_allocator_root,
        morpho_blue_root=morpho_blue_root,
    )
    reporter = ProgressReporter(float(amendment["execution"]["progress_interval_seconds"]))
    try:
        chain_result, _ = _full_chain_v2(
            chain_name,
            config["chains"][chain_name],
            config,
            transport,
            amendment["execution"]["full_chain"],
            reporter,
        )
    except (requests.RequestException, SqdPortalError, RpcError, ValueError) as error:
        chain_result = {
            "status": "transport_fail_before_support_interpretation",
            "transport_error_type": type(error).__name__,
            "transport_error": _redact_raw_evm_identities(str(error)),
            "support": None,
        }
    body = _base_result_v2(
        phase="full_chain",
        parent_config_path=parent_config_path,
        amendment_path=amendment_path,
        source_audit=source,
    )
    body.update(
        {
            "chain": chain_name,
            "formal_batch_id": batch_id,
            "worker": {"id": worker_id, "cuda_visible_devices": ""},
            "qualification_artifact": {
                "path": str(qualification_path.relative_to(REPO_ROOT)),
                "canonical_payload_sha256": qualification["canonical_payload_sha256"],
                "git_sha": qualification["repository"]["git_sha"],
            },
            "chain_result": chain_result,
            "merge_eligibility": chain_result["status"] == "transport_pass_support_computed",
            "data_contract": {
                "decoded_log_data": False,
                "retained_raw_responses_or_event_identities": False,
                "decoded_amounts_rates_utilization_prices_or_outcomes": False,
                "gpu_used": False,
                "paid_data_used": False,
            },
            "resources": {
                "wall_seconds": time.monotonic() - started,
                "single_process_cpu_core_hours_upper_bound": (time.monotonic() - started) / 3600.0,
                "maximum_transferred_gb": float(config["resources"]["maximum_transferred_gb"]),
                "gpu_hours": 0,
                "paid_data_usd": 0,
            },
            "claim_limit": (
                "This chain artifact is one outcome-blind component of a jointly launched two-chain D0. "
                "It is not a standalone support decision and does not establish genuine JIT events."
            ),
        }
    )
    return _write_aggregate_result(output_path, body)


def _load_verified_chain_artifact(
    path: Path, *, parent_config_path: Path, amendment_path: Path
) -> dict[str, Any]:
    payload = _load_json(path)
    claimed = str(payload.get("canonical_payload_sha256"))
    body = {key: value for key, value in payload.items() if key != "canonical_payload_sha256"}
    if _canonical_sha256(body) != claimed:
        raise RuntimeError(f"chain artifact canonical hash mismatch: {path}")
    if payload.get("schema_version") != 2 or payload.get("phase") != "full_chain":
        raise RuntimeError(f"invalid v2 chain artifact: {path}")
    if payload.get("repository", {}).get("git_sha") != _git(REPO_ROOT, "rev-parse", "HEAD"):
        raise RuntimeError("chain artifact was not produced from the merge commit")
    if payload.get("parent_config", {}).get("sha256") != _sha256_file(parent_config_path):
        raise RuntimeError("chain artifact parent config mismatch")
    if payload.get("transport_amendment", {}).get("sha256") != _sha256_file(amendment_path):
        raise RuntimeError("chain artifact transport amendment mismatch")
    _assert_no_raw_evm_identities(payload)
    return payload


def _support_gates(
    chain_results: Mapping[str, Mapping[str, Any]], thresholds: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], int, int]:
    chain_gates: dict[str, Any] = {}
    pooled_candidates = 0
    pooled_edges = 0
    for chain_name in thresholds["required_chains"]:
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
        transport = result["transport"]
        pooled_candidates += int(summary["candidate_transaction_count"])
        pooled_edges += int(summary["distinct_directed_edge_count"])
        chain_gates[str(chain_name)] = {
            "transport": transport["transport_pass"] is True,
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
            "receipts": float(transport["receipt_verification_rate"])
            >= float(thresholds["minimum_candidate_receipt_verification_rate"]),
        }
    pooled_gates = {
        "all_required_chains_available": set(chain_results) == set(map(str, thresholds["required_chains"])),
        "candidate_transactions": pooled_candidates
        >= int(thresholds["minimum_target_matched_candidate_transactions_total"]),
        "directed_edges": pooled_edges >= int(thresholds["minimum_distinct_edges_total"]),
    }
    return chain_gates, pooled_gates, pooled_candidates, pooled_edges


def run_merge_v2(
    parent_config_path: Path,
    amendment_path: Path,
    qualification_path: Path,
    chain_artifact_paths: Sequence[Path],
    output_path: Path,
    *,
    sdk_root: Path,
    public_allocator_root: Path,
    morpho_blue_root: Path,
) -> dict[str, Any]:
    """Merge the jointly launched required-chain artifacts and evaluate v1 gates once."""
    _refuse_existing_output(output_path)
    started = time.monotonic()
    config, _ = _validate_common(parent_config_path)
    amendment = _verify_amendment(amendment_path, parent_config_path)
    qualification = _verify_qualification_v2(qualification_path, parent_config_path, amendment_path)
    source = _source_audit(
        config,
        sdk_root=sdk_root,
        public_allocator_root=public_allocator_root,
        morpho_blue_root=morpho_blue_root,
    )
    artifact_records = [
        (
            path.resolve(),
            _load_verified_chain_artifact(
                path.resolve(), parent_config_path=parent_config_path, amendment_path=amendment_path
            ),
        )
        for path in chain_artifact_paths
    ]
    by_chain = {str(artifact["chain"]): artifact for _, artifact in artifact_records}
    path_by_chain = {str(artifact["chain"]): path for path, artifact in artifact_records}
    required = set(map(str, amendment["formal_run"]["required_chains"]))
    if len(by_chain) != len(artifact_records) or set(by_chain) != required:
        raise RuntimeError("merge does not contain exactly one artifact for each required chain")
    if any(artifact["source_audit"] != source for _, artifact in artifact_records):
        raise RuntimeError("chain artifacts do not share the merge source audit")
    if any(
        artifact["qualification_artifact"]["canonical_payload_sha256"]
        != qualification["canonical_payload_sha256"]
        for _, artifact in artifact_records
    ):
        raise RuntimeError("chain artifacts do not share the v2 qualification")
    expected_batch_id = _formal_batch_id(
        amendment_path=amendment_path,
        qualification=qualification,
        git_sha=_git(REPO_ROOT, "rev-parse", "HEAD"),
    )
    if any(artifact.get("formal_batch_id") != expected_batch_id for _, artifact in artifact_records):
        raise RuntimeError("chain artifacts do not share the expected formal batch")
    for chain_name, artifact in by_chain.items():
        expected_worker = str(amendment["formal_run"][f"{chain_name}_worker"])
        worker = artifact.get("worker")
        if not isinstance(worker, Mapping) or worker.get("id") != expected_worker:
            raise RuntimeError("chain artifact worker assignment mismatch")
        if worker.get("cuda_visible_devices") != "":
            raise RuntimeError("chain artifact did not hide CUDA")

    chain_results = {name: by_chain[name]["chain_result"] for name in sorted(by_chain)}
    chain_gates, pooled_gates, pooled_candidates, pooled_edges = _support_gates(
        chain_results, config["pass_thresholds"]
    )
    all_pass = all(all(gates.values()) for gates in chain_gates.values()) and all(pooled_gates.values())
    body = _base_result_v2(
        phase="full",
        parent_config_path=parent_config_path,
        amendment_path=amendment_path,
        source_audit=source,
    )
    body.update(
        {
            "qualification_artifact": {
                "path": str(qualification_path.relative_to(REPO_ROOT)),
                "canonical_payload_sha256": qualification["canonical_payload_sha256"],
                "git_sha": qualification["repository"]["git_sha"],
            },
            "chain_artifacts": {
                name: {
                    "canonical_payload_sha256": by_chain[name]["canonical_payload_sha256"],
                    "file_sha256": _sha256_file(path_by_chain[name]),
                }
                for name in sorted(by_chain)
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
                "merge_wall_seconds": time.monotonic() - started,
                "chain_wall_seconds": {
                    name: float(by_chain[name]["resources"]["wall_seconds"]) for name in sorted(by_chain)
                },
                "maximum_transferred_gb_each_chain": float(config["resources"]["maximum_transferred_gb"]),
                "gpu_hours": 0,
                "paid_data_usd": 0,
            },
        }
    )
    return _write_aggregate_result(output_path, body)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("qualification", "chain", "merge"), required=True)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--amendment", type=Path, default=AMENDMENT_PATH)
    parser.add_argument("--qualification-artifact", type=Path, default=QUALIFICATION_V2_PATH)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--chain", choices=("ethereum", "base"))
    parser.add_argument("--chain-artifact", action="append", type=Path, default=[])
    parser.add_argument("--sdk-root", type=Path, required=True)
    parser.add_argument("--public-allocator-root", type=Path, required=True)
    parser.add_argument("--morpho-blue-root", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    parent_config_path = args.config.resolve()
    amendment_path = args.amendment.resolve()
    common = {
        "sdk_root": args.sdk_root.resolve(),
        "public_allocator_root": args.public_allocator_root.resolve(),
        "morpho_blue_root": args.morpho_blue_root.resolve(),
    }
    if args.phase == "qualification":
        output = args.output.resolve() if args.output else QUALIFICATION_V2_PATH
        result = run_qualification_v2(parent_config_path, amendment_path, output, **common)
    elif args.phase == "chain":
        if args.chain is None:
            raise SystemExit("--chain is required for phase=chain")
        if args.output is None:
            raise SystemExit("--output outside the repository is required for phase=chain")
        chain_output = args.output.resolve()
        if chain_output.is_relative_to(REPO_ROOT):
            raise SystemExit("phase=chain output must be outside the repository")
        result = run_chain_v2(
            parent_config_path,
            amendment_path,
            args.qualification_artifact.resolve(),
            chain_output,
            chain_name=args.chain,
            **common,
        )
    else:
        if len(args.chain_artifact) != 2:
            raise SystemExit("exactly two --chain-artifact paths are required for phase=merge")
        output = args.output.resolve() if args.output else FULL_RESULT_V2_PATH
        result = run_merge_v2(
            parent_config_path,
            amendment_path,
            args.qualification_artifact.resolve(),
            [path.resolve() for path in args.chain_artifact],
            output,
            **common,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
