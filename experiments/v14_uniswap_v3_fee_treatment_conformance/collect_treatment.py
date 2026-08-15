#!/usr/bin/env python3
"""Collect the frozen Proposal 94 treatment metadata frame."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import requests

from ecomd.market_world.provenance import require_clean_repository
from ecomd.research.uniswap_v3_fee_treatment import (
    canonical_json_sha256,
    contract_sha256,
    load_contract,
    normalize_address,
    normalize_hash,
    parse_batch_treatment,
    summarize_treatment_conformance,
    validate_frozen_contract,
    validate_governance_execution,
)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _mapping(value: object, *, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise RuntimeError(f"{path} must be a mapping")
    return cast(Mapping[str, object], value)


def _sequence(value: object, *, path: str) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise RuntimeError(f"{path} must be a sequence")
    return cast(Sequence[object], value)


def _quantity(value: int) -> str:
    if value < 0:
        raise ValueError("JSON-RPC quantities cannot be negative")
    return hex(value)


class RpcCollector:
    """Rate-limited JSON-RPC collector that retains response hashes, not raw payload files."""

    def __init__(
        self,
        *,
        url: str,
        user_agent: str,
        maximum_requests_per_second: float,
        maximum_transport_retries: int,
    ) -> None:
        self._url = url
        self._minimum_interval = 1.0 / maximum_requests_per_second
        self._maximum_transport_retries = maximum_transport_retries
        self._last_start: float | None = None
        self._next_id = 1
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})
        self.response_records: list[dict[str, object]] = []

    def call(self, method: str, params: Sequence[object]) -> object:
        request_id = self._next_id
        self._next_id += 1
        request_payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": list(params),
        }
        errors: list[str] = []
        for attempt in range(self._maximum_transport_retries + 1):
            if self._last_start is not None:
                time.sleep(max(0.0, self._minimum_interval - (time.monotonic() - self._last_start)))
            self._last_start = time.monotonic()
            try:
                response = self._session.post(self._url, json=request_payload, timeout=60.0)
                response.raise_for_status()
                payload: object = response.json()
            except (requests.RequestException, ValueError) as error:
                errors.append(f"{type(error).__name__}: {error}")
            else:
                envelope = _mapping(payload, path=f"rpc.{method}")
                if envelope.get("error") is not None:
                    errors.append(f"rpc error: {envelope['error']}")
                elif "result" not in envelope or envelope.get("result") is None:
                    errors.append("rpc result is missing or null")
                else:
                    retrieved_at = _utc_now()
                    self.response_records.append(
                        {
                            "request_index": len(self.response_records),
                            "method": method,
                            "params": list(params),
                            "request_sha256": canonical_json_sha256(request_payload),
                            "response_sha256": canonical_json_sha256(envelope),
                            "retrieved_at_utc": retrieved_at,
                            "attempt_count": attempt + 1,
                            "prior_transport_or_rpc_errors": errors,
                        }
                    )
                    return envelope["result"]
            if attempt < self._maximum_transport_retries:
                time.sleep(float(attempt + 1))
        raise RuntimeError(f"{method} failed after all attempts: {errors}")


def _validate_commit(repository: Path, value: str) -> None:
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise ValueError("collection commit must be a full lowercase Git SHA")
    subprocess.run(
        ["git", "cat-file", "-e", f"{value}^{{commit}}"],
        cwd=repository,
        check=True,
        capture_output=True,
    )


def _block_metadata(block: Mapping[str, object]) -> dict[str, object]:
    number = block.get("number")
    timestamp = block.get("timestamp")
    block_hash = block.get("hash")
    if not isinstance(number, str) or not isinstance(timestamp, str):
        raise RuntimeError("block number/timestamp must be JSON-RPC quantities")
    unix_seconds = int(timestamp, 16)
    return {
        "number": int(number, 16),
        "hash": normalize_hash(block_hash, path="block.hash"),
        "timestamp_unix": unix_seconds,
        "timestamp_utc": datetime.fromtimestamp(unix_seconds, UTC).isoformat().replace("+00:00", "Z"),
    }


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT / "data/manifests/uniswap_v3_fee_treatment_conformance_v1.yaml",
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=(
            ROOT / "experiments/v14_uniswap_v3_fee_treatment_conformance/artifacts/treatment_ledger.jsonl"
        ),
    )
    parser.add_argument(
        "--response-hashes",
        type=Path,
        default=(
            ROOT / "experiments/v14_uniswap_v3_fee_treatment_conformance/artifacts/rpc_response_hashes.json"
        ),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=(
            ROOT / "experiments/v14_uniswap_v3_fee_treatment_conformance/artifacts/treatment_summary.json"
        ),
    )
    parser.add_argument("--collection-commit")
    arguments = parser.parse_args()
    for output in (arguments.ledger, arguments.response_hashes, arguments.summary):
        if output.exists():
            raise FileExistsError(f"refusing to overwrite {output}")

    current_commit = require_clean_repository(ROOT)
    collection_commit = arguments.collection_commit or current_commit
    _validate_commit(ROOT, collection_commit)
    if collection_commit != current_commit:
        raise ValueError("collection commit must equal the clean worktree HEAD")
    contract = load_contract(arguments.contract)
    errors = validate_frozen_contract(contract)
    if errors:
        raise RuntimeError("invalid frozen treatment contract: " + "; ".join(errors))

    source = _mapping(contract["source"], path="source")
    mechanism = _mapping(contract["mechanism"], path="mechanism")
    frame = _mapping(contract["propagation_frame"], path="propagation_frame")
    gates = _mapping(contract["gates"], path="gates")
    rpc = RpcCollector(
        url=cast(str, source["rpc_url"]),
        user_agent=cast(str, source["user_agent"]),
        maximum_requests_per_second=float(cast(float, source["maximum_requests_per_second"])),
        maximum_transport_retries=cast(int, source["maximum_transport_retries"]),
    )

    chain_id = rpc.call("eth_chainId", [])
    if chain_id != "0x1":
        raise RuntimeError(f"RPC endpoint returned unexpected chain ID: {chain_id}")
    adapter = normalize_address(mechanism["executed_adapter_address"], path="executed_adapter_address")
    runtime_code_block = cast(int, source["runtime_bytecode_block"])
    runtime_code = rpc.call("eth_getCode", [adapter, _quantity(runtime_code_block)])
    if not isinstance(runtime_code, str) or not runtime_code.startswith("0x"):
        raise RuntimeError("eth_getCode returned malformed runtime bytecode")
    runtime_bytes = bytes.fromhex(runtime_code[2:])
    if len(runtime_bytes) != source["runtime_bytecode_size_bytes"]:
        raise RuntimeError("runtime bytecode size differs from frozen source metadata")
    runtime_sha256 = hashlib.sha256(runtime_bytes).hexdigest()
    if runtime_sha256 != source["runtime_bytecode_sha256"]:
        raise RuntimeError("runtime bytecode SHA-256 differs from the frozen verified contract")

    governance_tx_hash = normalize_hash(mechanism["governance_execution_tx"])
    governance_tx = _mapping(
        rpc.call("eth_getTransactionByHash", [governance_tx_hash]), path="governance_transaction"
    )
    governance_receipt = _mapping(
        rpc.call("eth_getTransactionReceipt", [governance_tx_hash]), path="governance_receipt"
    )
    governance_block_number = cast(int, mechanism["governance_execution_block"])
    governance_block = _mapping(
        rpc.call("eth_getBlockByNumber", [_quantity(governance_block_number), False]),
        path="governance_block",
    )
    governance = validate_governance_execution(
        governance_tx,
        governance_receipt,
        governor_address=cast(str, mechanism["governor_address"]),
        proposal_id=cast(int, mechanism["governance_proposal_id"]),
        expected_tx_hash=governance_tx_hash,
        expected_block=governance_block_number,
        factory_address=cast(str, mechanism["factory_address"]),
        old_owner=cast(str, mechanism["old_adapter_address"]),
        new_owner=adapter,
    )
    governance_block_metadata = _block_metadata(governance_block)
    if governance_block_metadata["hash"] != normalize_hash(mechanism["governance_execution_block_hash"]):
        raise RuntimeError("governance block hash differs from the frozen block hash")
    if governance_block_metadata["hash"] != governance["block_hash"]:
        raise RuntimeError("governance transaction/receipt block hash differs from the fetched block")
    if governance_block_metadata["timestamp_utc"] != mechanism["governance_execution_chain_timestamp_utc"]:
        raise RuntimeError("governance block timestamp differs from the frozen chain timestamp")

    raw_hashes = _sequence(frame["batch_transaction_hashes"], path="batch_transaction_hashes")
    expected_hashes = [normalize_hash(value, path="batch_transaction_hash") for value in raw_hashes]
    expected_blocks = [
        cast(int, value) for value in _sequence(frame["expected_blocks"], path="expected_blocks")
    ]
    expected_timestamps = [
        cast(str, value)
        for value in _sequence(frame["expected_batch_timestamps_utc"], path="expected_batch_timestamps_utc")
    ]
    batches: list[dict[str, object]] = []
    batch_blocks: list[dict[str, object]] = []
    for index, tx_hash in enumerate(expected_hashes):
        transaction = _mapping(
            rpc.call("eth_getTransactionByHash", [tx_hash]), path=f"batch_transaction[{index}]"
        )
        receipt = _mapping(rpc.call("eth_getTransactionReceipt", [tx_hash]), path=f"batch_receipt[{index}]")
        block = _mapping(
            rpc.call("eth_getBlockByNumber", [_quantity(expected_blocks[index]), False]),
            path=f"batch_block[{index}]",
        )
        block_metadata = _block_metadata(block)
        if block_metadata["number"] != expected_blocks[index]:
            raise RuntimeError("batch block number differs from the frozen frame")
        if block_metadata["timestamp_utc"] != expected_timestamps[index]:
            raise RuntimeError("batch block timestamp differs from the frozen frame")
        batch = parse_batch_treatment(
            transaction,
            receipt,
            adapter_address=adapter,
            expected_tx_hash=tx_hash,
        )
        if batch["block_number"] != expected_blocks[index]:
            raise RuntimeError("parsed batch block differs from the frozen frame")
        if batch["block_hash"] != block_metadata["hash"]:
            raise RuntimeError("batch transaction/receipt block hash differs from the fetched block")
        if batch["caller_address"] != normalize_address(frame["expected_direct_caller"]):
            raise RuntimeError("batch caller differs from the frozen direct caller")
        batches.append(batch)
        batch_blocks.append(block_metadata)
        print(
            json.dumps(
                {
                    "batch": index,
                    "transaction_hash": tx_hash,
                    "pool_rows": batch["calldata_pool_count"],
                    "block_number": batch["block_number"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    summary = summarize_treatment_conformance(
        governance,
        batches,
        expected_batch_hashes=expected_hashes,
        expected_batch_size=cast(int, frame["expected_batch_size"]),
        minimum_activated_total=cast(int, gates["minimum_activated_total"]),
        minimum_activated_per_fee_value=cast(int, gates["minimum_activated_per_fee_value"]),
    )
    governance_unix = cast(int, governance_block_metadata["timestamp_unix"])
    summary["mechanism_clock"] = {
        "governance_block": governance_block_metadata,
        "batch_blocks": batch_blocks,
        "first_pool_activation_delay_blocks": expected_blocks[0] - governance_block_number,
        "first_pool_activation_delay_seconds": cast(int, batch_blocks[0]["timestamp_unix"]) - governance_unix,
        "proposal_display_time_is_not_authoritative": True,
        "pool_activation_clock": "per_pool_SetFeeProtocol_event",
    }
    all_rows: list[Mapping[str, object]] = []
    for batch in batches:
        all_rows.extend(
            _mapping(row, path="batch.rows") for row in _sequence(batch["rows"], path="batch.rows")
        )
    expected_request_count = cast(int, source["expected_rpc_request_count"])
    if len(rpc.response_records) != expected_request_count:
        raise RuntimeError(
            f"expected exactly {expected_request_count} successful RPC calls, "
            f"observed {len(rpc.response_records)}"
        )

    arguments.ledger.parent.mkdir(parents=True, exist_ok=True)
    with arguments.ledger.open("x", encoding="utf-8") as handle:
        for row in all_rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    ledger_sha256 = hashlib.sha256(arguments.ledger.read_bytes()).hexdigest()
    response_manifest = {
        "schema_version": "ecophys-json-rpc-response-hash-manifest/v1",
        "source_url": source["rpc_url"],
        "chain_id": 1,
        "records": rpc.response_records,
        "record_count": len(rpc.response_records),
        "records_sha256": canonical_json_sha256(rpc.response_records),
        "raw_response_payloads_retained": False,
        "normalized_mechanism_rows_retained": True,
    }
    _write_json(arguments.response_hashes, response_manifest)
    summary["artifacts"] = {
        "treatment_ledger_sha256": ledger_sha256,
        "treatment_ledger_row_count": len(all_rows),
        "rpc_response_hash_manifest_sha256": hashlib.sha256(
            arguments.response_hashes.read_bytes()
        ).hexdigest(),
        "frozen_contract_sha256": contract_sha256(arguments.contract),
    }
    summary["ownership"] = {
        "collection_git_commit": collection_commit,
        "summary_git_commit": current_commit,
        "collected_at_utc": _utc_now(),
        "runtime_bytecode_sha256": runtime_sha256,
        "lp_action_events_opened": 0,
        "swap_events_opened": 0,
        "liquidity_outcomes_opened": 0,
        "price_or_volume_outcomes_opened": 0,
        "paid_data": False,
        "gpu_hours": 0,
    }
    _write_json(arguments.summary, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
