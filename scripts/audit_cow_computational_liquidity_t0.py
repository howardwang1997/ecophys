"""Run the frozen CoW computational-liquidity T0 support audit."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import subprocess
import threading
import time
from collections import Counter
from collections.abc import Mapping, Sequence
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
import yaml

from ecomd.data.cow_solver_competition import (
    CompetitionSummary,
    canonical_json_sha256,
    evaluate_t0_support,
    parse_blockscout_settlement_events,
    summarize_competition,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs/agent_markets/cow_computational_liquidity_t0_v1.yaml"
RUNTIME_PATH = REPO_ROOT / "configs/agent_markets/cow_computational_liquidity_t0_runtime_v1.yaml"


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"YAML root must be an object: {path}")
    return payload


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _resolve_repo_path(relative: Any) -> Path:
    path = (REPO_ROOT / str(relative)).resolve()
    if REPO_ROOT.resolve() not in path.parents:
        raise ValueError("runtime output path escapes repository")
    return path


def _verify_contract(config_path: Path, runtime_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    config = _load_yaml(config_path)
    runtime = _load_yaml(runtime_path)
    contract = config.get("contract")
    runtime_contract = runtime.get("contract")
    if not isinstance(contract, Mapping) or not isinstance(runtime_contract, Mapping):
        raise RuntimeError("T0 config lacks a contract")
    if contract.get("status") != "frozen_before_formal_window_event_or_competition_access":
        raise RuntimeError("scientific T0 contract is not frozen")
    if runtime_contract.get("status") != "frozen_before_formal_window_access":
        raise RuntimeError("runtime T0 contract is not frozen")
    expected_parent_path = str(config_path.relative_to(REPO_ROOT))
    if runtime_contract.get("parent_config_path") != expected_parent_path:
        raise RuntimeError("runtime parent config path mismatch")
    observed_parent_hash = _sha256_file(config_path)
    if runtime_contract.get("parent_config_sha256") != observed_parent_hash:
        raise RuntimeError("runtime parent config hash mismatch")
    if runtime_contract.get("scientific_window_metrics_and_gates_unchanged") is not True:
        raise RuntimeError("runtime contract does not preserve scientific gates")
    preregistration_sha = str(runtime_contract.get("preregistration_git_sha"))
    committed_config = subprocess.run(
        ["git", "show", f"{preregistration_sha}:{expected_parent_path}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    if hashlib.sha256(committed_config).hexdigest() != observed_parent_hash:
        raise RuntimeError("current scientific config differs from preregistration commit")
    if _git("branch", "--show-current") != contract.get("branch"):
        raise RuntimeError("formal T0 is running on the wrong branch")
    window = config.get("formal_window")
    if not isinstance(window, Mapping):
        raise RuntimeError("formal window is missing")
    start = int(window["from_block"])
    end = int(window["to_block"])
    exclusions = window.get("exploratory_exclusions")
    if not isinstance(exclusions, Mapping):
        raise RuntimeError("exploratory exclusions are missing")
    exclusion_start = int(exclusions["block_from"])
    exclusion_end = int(exclusions["block_to"])
    if start > end or not (end < exclusion_start or start > exclusion_end):
        raise RuntimeError("formal interval is invalid or overlaps exploratory access")
    execution = runtime.get("execution")
    if not isinstance(execution, Mapping) or int(execution.get("cow_max_workers", 0)) <= 0:
        raise RuntimeError("runtime execution parameters are invalid")
    if int(execution.get("blockscout_offset", 0)) <= 0:
        raise RuntimeError("Blockscout offset must be positive")
    return config, runtime


class StartRateLimiter:
    """Space request starts globally while allowing network waits to overlap."""

    def __init__(self, interval_seconds: float) -> None:
        if interval_seconds <= 0:
            raise ValueError("request interval must be positive")
        self.interval_seconds = interval_seconds
        self.next_start = 0.0
        self.lock = threading.Lock()

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()
            start = max(now, self.next_start)
            self.next_start = start + self.interval_seconds
        delay = start - now
        if delay > 0:
            time.sleep(delay)


class ProgressReporter:
    """Emit bounded-cadence progress without inspecting scientific outcomes."""

    def __init__(self, interval_seconds: float) -> None:
        if interval_seconds <= 0:
            raise ValueError("progress interval must be positive")
        self.interval_seconds = interval_seconds
        self.started = time.monotonic()
        self.last = 0.0
        self.lock = threading.Lock()

    def emit(self, stage: str, completed: int, total: int, *, force: bool = False) -> None:
        now = time.monotonic()
        with self.lock:
            if not force and now - self.last < self.interval_seconds:
                return
            print(
                "T0_PROGRESS "
                + json.dumps(
                    {
                        "stage": stage,
                        "completed_work_units": completed,
                        "total_work_units": total,
                        "elapsed_seconds": round(now - self.started, 3),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            self.last = now


@dataclass(frozen=True)
class FetchRecord:
    transaction_hash: str
    status_code: int | None
    payload: Mapping[str, Any] | None
    error: str | None
    attempts: int
    bytes_received: int


def _request_blockscout(config: Mapping[str, Any], runtime: Mapping[str, Any]) -> Mapping[str, Any]:
    source = config["source"]
    window = config["formal_window"]
    transport = config["transport"]
    execution = runtime["execution"]
    params: dict[str, str | int] = {
        "module": "logs",
        "action": "getLogs",
        "fromBlock": int(window["from_block"]),
        "toBlock": int(window["to_block"]),
        "address": str(source["settlement_contract"]),
        "topic0": str(source["settlement_topic0"]),
        "page": int(execution["blockscout_page"]),
        "offset": int(execution["blockscout_offset"]),
    }
    attempts = int(transport["attempts"])
    backoffs = [float(value) for value in transport["backoff_seconds"]]
    timeout = float(transport["timeout_seconds"])
    headers = {"User-Agent": str(transport["user_agent"])}
    last_error: Exception | None = None
    with requests.Session() as session:
        for attempt in range(attempts):
            try:
                response = session.get(
                    str(source["blockscout_logs_endpoint"]),
                    params=params,
                    headers=headers,
                    timeout=timeout,
                )
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, Mapping):
                    raise ValueError("Blockscout JSON root is not an object")
                return payload
            except (requests.RequestException, ValueError) as error:
                last_error = error
                if attempt + 1 < attempts:
                    time.sleep(backoffs[min(attempt, len(backoffs) - 1)])
    raise RuntimeError("Blockscout transport failed under the frozen retry policy") from last_error


def _fetch_competition(
    transaction_hash: str,
    *,
    config: Mapping[str, Any],
    limiter: StartRateLimiter,
) -> FetchRecord:
    source = config["source"]
    transport = config["transport"]
    url = str(source["cow_competition_endpoint_template"]).format(transaction_hash=transaction_hash)
    attempts = int(transport["attempts"])
    backoffs = [float(value) for value in transport["backoff_seconds"]]
    timeout = float(transport["timeout_seconds"])
    headers = {"User-Agent": str(transport["user_agent"])}
    bytes_received = 0
    last_error = "unattempted"
    last_status: int | None = None
    with requests.Session() as session:
        for attempt in range(attempts):
            limiter.wait()
            try:
                response = session.get(url, headers=headers, timeout=timeout)
                last_status = response.status_code
                bytes_received += len(response.content)
                if response.status_code == 404:
                    return FetchRecord(
                        transaction_hash=transaction_hash,
                        status_code=404,
                        payload=None,
                        error="http_404",
                        attempts=attempt + 1,
                        bytes_received=bytes_received,
                    )
                if response.status_code == 429 or response.status_code >= 500:
                    last_error = f"retryable_http_{response.status_code}"
                    if attempt + 1 < attempts:
                        time.sleep(backoffs[min(attempt, len(backoffs) - 1)])
                        continue
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, Mapping):
                    raise ValueError("CoW competition JSON root is not an object")
                return FetchRecord(
                    transaction_hash=transaction_hash,
                    status_code=response.status_code,
                    payload=payload,
                    error=None,
                    attempts=attempt + 1,
                    bytes_received=bytes_received,
                )
            except (requests.RequestException, ValueError) as error:
                last_error = type(error).__name__
                if attempt + 1 < attempts:
                    time.sleep(backoffs[min(attempt, len(backoffs) - 1)])
    return FetchRecord(
        transaction_hash=transaction_hash,
        status_code=last_status,
        payload=None,
        error=last_error,
        attempts=attempts,
        bytes_received=bytes_received,
    )


def _write_gzip(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    if path.exists() or partial.exists():
        raise FileExistsError(f"refusing to overwrite immutable raw artifact: {path}")
    with (
        partial.open("xb") as raw_handle,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw_handle, mtime=0) as compressed,
    ):
        compressed.write(payload)
    os.replace(partial, path)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    if path.exists() or partial.exists():
        raise FileExistsError(f"refusing to overwrite immutable result artifact: {path}")
    payload["canonical_payload_sha256"] = canonical_json_sha256(payload)
    partial.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(partial, path)


def _raw_competition_bytes(records: Sequence[FetchRecord]) -> bytes:
    lines: list[str] = []
    for record in records:
        row = {
            "transaction_hash": record.transaction_hash,
            "status_code": record.status_code,
            "error": record.error,
            "attempts": record.attempts,
            "bytes_received": record.bytes_received,
            "payload": record.payload,
        }
        lines.append(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    return ("\n".join(lines) + "\n").encode()


def run_t0(config_path: Path, runtime_path: Path) -> dict[str, Any]:
    """Acquire the frozen interval and write raw, provenance and support artifacts."""
    config, runtime = _verify_contract(config_path, runtime_path)
    if _git("status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("formal T0 requires a clean worktree")
    execution = runtime["execution"]
    raw_directory = _resolve_repo_path(execution["raw_directory"])
    blockscout_path = raw_directory / str(execution["blockscout_raw_filename"])
    cow_path = raw_directory / str(execution["cow_raw_filename"])
    manifest_path = _resolve_repo_path(execution["manifest_path"])
    result_path = _resolve_repo_path(execution["result_path"])
    for path in (blockscout_path, cow_path, manifest_path, result_path):
        if path.exists() or path.with_name(path.name + ".partial").exists():
            raise FileExistsError(f"formal T0 target already exists: {path}")

    reporter = ProgressReporter(float(execution["progress_interval_seconds"]))
    blockscout_payload = _request_blockscout(config, runtime)
    source = config["source"]
    window = config["formal_window"]
    events = parse_blockscout_settlement_events(
        blockscout_payload,
        expected_contract=str(source["settlement_contract"]),
        expected_topic0=str(source["settlement_topic0"]),
        from_block=int(window["from_block"]),
        to_block=int(window["to_block"]),
    )
    if (
        execution["reject_blockscout_result_at_offset_cap"] is True
        and len(events) >= int(execution["blockscout_offset"])
    ):
        raise RuntimeError("Blockscout result reached its frozen offset cap; completeness is unknown")
    transaction_hashes = tuple(dict.fromkeys(event.transaction_hash for event in events))
    reporter.emit("blockscout_complete", len(transaction_hashes), len(transaction_hashes), force=True)

    limiter = StartRateLimiter(float(config["transport"]["cow_minimum_request_interval_seconds"]))
    records_by_hash: dict[str, FetchRecord] = {}
    max_workers = int(execution["cow_max_workers"])
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="cow-t0") as executor:
        futures: dict[Future[FetchRecord], str] = {
            executor.submit(_fetch_competition, tx, config=config, limiter=limiter): tx
            for tx in transaction_hashes
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            tx = futures[future]
            try:
                records_by_hash[tx] = future.result()
            except Exception as error:
                records_by_hash[tx] = FetchRecord(
                    transaction_hash=tx,
                    status_code=None,
                    payload=None,
                    error=f"worker_{type(error).__name__}",
                    attempts=0,
                    bytes_received=0,
                )
            reporter.emit("cow_competitions", completed, len(transaction_hashes))
    reporter.emit("cow_competitions", len(transaction_hashes), len(transaction_hashes), force=True)
    records = tuple(records_by_hash[tx] for tx in transaction_hashes)

    blockscout_bytes = json.dumps(
        blockscout_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode()
    cow_bytes = _raw_competition_bytes(records)
    _write_gzip(blockscout_path, blockscout_bytes)
    _write_gzip(cow_path, cow_bytes)

    retention = config["retention"]
    definitions = config["definitions"]
    summaries: list[CompetitionSummary] = []
    parse_failures: Counter[str] = Counter()
    membership_failures = 0
    for record in records:
        if record.payload is None:
            parse_failures[record.error or "missing_payload"] += 1
            continue
        try:
            summaries.append(
                summarize_competition(
                    record.payload,
                    queried_transaction_hash=record.transaction_hash,
                    required_competition_fields=[str(value) for value in retention["required_competition_fields"]],
                    required_solution_fields=[str(value) for value in retention["required_solution_fields"]],
                    minimum_orders_for_multi_order_solution=int(
                        definitions["minimum_orders_for_multi_order_solution"]
                    ),
                )
            )
        except ValueError as error:
            message = str(error)
            if "queried transaction hash is absent" in message:
                membership_failures += 1
            parse_failures[f"schema_{message}"] += 1

    evaluation = evaluate_t0_support(
        summaries,
        attempted_transaction_count=len(transaction_hashes),
        membership_failure_count=membership_failures,
        gates=config["gates"],
        low_criticality_maximum=float(definitions["low_criticality_maximum"]),
        high_criticality_minimum=float(definitions["high_criticality_minimum"]),
    )
    created_utc = datetime.now(UTC).isoformat()
    repository_sha = _git("rev-parse", "HEAD")
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "dataset_id": "cow_computational_liquidity_t0_v1",
        "downloaded_utc": created_utc,
        "provenance": {
            "chain": "ethereum",
            "block_interval_inclusive": [int(window["from_block"]), int(window["to_block"])],
            "settlement_contract": str(source["settlement_contract"]),
            "settlement_topic0": str(source["settlement_topic0"]),
            "blockscout_endpoint": str(source["blockscout_logs_endpoint"]),
            "cow_endpoint_template": str(source["cow_competition_endpoint_template"]),
            "cow_openapi_tag": str(source["cow_openapi_tag"]),
            "cow_openapi_url": str(source["cow_openapi_url"]),
            "blockscout_license_status": "public_index_of_factual_onchain_events_no_dataset_license_identified",
            "cow_api_data_license_status": "public_api_data_license_not_explicitly_identified",
            "code_licenses": "cow_services_Apache-2.0_and_settlement_contract_LGPL-3.0-or-later",
        },
        "binding": {
            "repository_git_sha": repository_sha,
            "preregistration_git_sha": str(runtime["contract"]["preregistration_git_sha"]),
            "scientific_config_path": str(config_path.relative_to(REPO_ROOT)),
            "scientific_config_sha256": _sha256_file(config_path),
            "runtime_config_path": str(runtime_path.relative_to(REPO_ROOT)),
            "runtime_config_sha256": _sha256_file(runtime_path),
        },
        "raw_artifacts": {
            "blockscout_path": str(blockscout_path.relative_to(REPO_ROOT)),
            "blockscout_sha256": _sha256_file(blockscout_path),
            "blockscout_compressed_bytes": blockscout_path.stat().st_size,
            "cow_path": str(cow_path.relative_to(REPO_ROOT)),
            "cow_sha256": _sha256_file(cow_path),
            "cow_compressed_bytes": cow_path.stat().st_size,
        },
        "counts": {
            "settlement_event_count": len(events),
            "unique_settlement_transaction_count": len(transaction_hashes),
            "valid_competition_response_count": len(summaries),
            "parse_failure_counts": dict(sorted(parse_failures.items())),
            "request_count": sum(record.attempts for record in records) + 1,
            "cow_bytes_received": sum(record.bytes_received for record in records),
        },
        "data_contract": {
            "paid_data_used": False,
            "gpu_used": False,
            "EcoMD_used": False,
            "formal_window_only": True,
        },
    }
    _write_json(manifest_path, manifest)

    event_identities = [event.identity() for event in events]
    result: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": "cow_computational_liquidity_t0_v1",
        "created_utc": created_utc,
        "repository": {
            "git_sha": repository_sha,
            "worktree_clean_before_run": True,
        },
        "contract": {
            "scientific_config_path": str(config_path.relative_to(REPO_ROOT)),
            "scientific_config_sha256": _sha256_file(config_path),
            "runtime_config_path": str(runtime_path.relative_to(REPO_ROOT)),
            "runtime_config_sha256": _sha256_file(runtime_path),
            "preregistration_git_sha": str(runtime["contract"]["preregistration_git_sha"]),
        },
        "formal_window": {
            "from_block": int(window["from_block"]),
            "to_block": int(window["to_block"]),
            "settlement_event_count": len(events),
            "settlement_event_identity_sha256": canonical_json_sha256(event_identities),
            "unique_settlement_transaction_count": len(transaction_hashes),
            "settlement_transaction_identity_sha256": canonical_json_sha256(transaction_hashes),
        },
        "transport": {
            "cow_max_workers": max_workers,
            "request_start_interval_seconds": float(
                config["transport"]["cow_minimum_request_interval_seconds"]
            ),
            "cow_request_attempt_count": sum(record.attempts for record in records),
            "cow_bytes_received": sum(record.bytes_received for record in records),
            "failure_counts": dict(sorted(parse_failures.items())),
        },
        "data_manifest": {
            "path": str(manifest_path.relative_to(REPO_ROOT)),
            "sha256": _sha256_file(manifest_path),
            "canonical_payload_sha256": manifest["canonical_payload_sha256"],
        },
        **evaluation,
        "data_contract": {
            "paid_data_used": False,
            "gpu_used": False,
            "EcoMD_used": False,
            "association_test_run": False,
            "window_or_chain_expansion_used": False,
        },
        "claim_limit": str(config["contract"]["claim_limit"]),
    }
    _write_json(result_path, result)
    reporter.emit("artifacts_complete", len(transaction_hashes), len(transaction_hashes), force=True)
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--runtime", type=Path, default=RUNTIME_PATH)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = run_t0(args.config.resolve(), args.runtime.resolve())
    print(json.dumps({"scientific_decision": result["scientific_decision"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
