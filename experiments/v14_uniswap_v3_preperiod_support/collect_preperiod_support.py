#!/usr/bin/env python3
"""Collect the frozen Uniswap U1a preperiod support and identity sample."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from collections import defaultdict
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
    decode_quantity,
    normalize_address,
    normalize_hash,
)
from ecomd.research.uniswap_v3_preperiod_support import (
    POOL_EVENT_TOPICS,
    TRANSFER_TOPIC,
    build_pool_support_rows,
    contract_sha256,
    deduplicate_pool_events,
    hash_file,
    load_contract,
    load_jsonl,
    normalize_legacy_log,
    normalize_transaction_log,
    pair_sampled_pool_actions,
    resolve_transfer_owners,
    select_identity_transactions,
    split_inclusive_interval,
    summarize_preperiod_support,
    validate_frozen_contract,
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


def _integer(value: object, *, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RuntimeError(f"{path} must be an integer")
    return value


class AuditedHttpClient:
    """Rate-limited HTTP client with immutable request/response hash accounting."""

    def __init__(
        self,
        *,
        user_agent: str,
        maximum_requests_per_second: float,
        maximum_transport_retries: int,
        maximum_http_attempts: int,
        maximum_response_bytes: int,
    ) -> None:
        self._minimum_interval = 1.0 / maximum_requests_per_second
        self._maximum_transport_retries = maximum_transport_retries
        self._maximum_http_attempts = maximum_http_attempts
        self._maximum_response_bytes = maximum_response_bytes
        self._last_start: float | None = None
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})
        self.http_attempt_count = 0
        self.response_bytes = 0
        self.response_records: list[dict[str, object]] = []

    def _wait(self) -> None:
        if self._last_start is not None:
            delay = self._minimum_interval - (time.monotonic() - self._last_start)
            time.sleep(max(0.0, delay))
        self._last_start = time.monotonic()

    def request_json(
        self,
        *,
        method: str,
        url: str,
        role: str,
        params: Mapping[str, object] | None = None,
        json_payload: Mapping[str, object] | None = None,
    ) -> object:
        request_descriptor = {
            "method": method,
            "url": url,
            "params": dict(params or {}),
            "json": dict(json_payload or {}),
            "role": role,
        }
        request_params = cast(dict[str, str | int], dict(params or {}))
        prior_errors: list[str] = []
        for attempt in range(self._maximum_transport_retries + 1):
            if self.http_attempt_count >= self._maximum_http_attempts:
                raise RuntimeError("frozen maximum_http_attempts exhausted")
            self._wait()
            self.http_attempt_count += 1
            try:
                response = self._session.request(
                    method,
                    url,
                    params=request_params,
                    json=dict(json_payload) if json_payload is not None else None,
                    timeout=60.0,
                )
                body = response.content
                self.response_bytes += len(body)
                if self.response_bytes > self._maximum_response_bytes:
                    raise RuntimeError("frozen maximum_response_bytes exceeded")
                response.raise_for_status()
                payload: object = response.json()
            except (requests.RequestException, ValueError) as error:
                prior_errors.append(f"{type(error).__name__}: {error}")
            else:
                self.response_records.append(
                    {
                        "request_index": len(self.response_records),
                        "role": role,
                        "method": method,
                        "url": url,
                        "params": dict(params or {}),
                        "request_sha256": canonical_json_sha256(request_descriptor),
                        "response_body_sha256": hashlib.sha256(body).hexdigest(),
                        "response_canonical_json_sha256": canonical_json_sha256(payload),
                        "response_bytes": len(body),
                        "retrieved_at_utc": _utc_now(),
                        "attempt_count": attempt + 1,
                        "prior_transport_errors": prior_errors,
                    }
                )
                return payload
            if attempt < self._maximum_transport_retries:
                time.sleep(float(attempt + 1))
        raise RuntimeError(f"{role} failed after all transport attempts: {prior_errors}")


def _validate_commit(repository: Path, value: str) -> None:
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise ValueError("collection commit must be a full lowercase Git SHA")
    subprocess.run(
        ["git", "cat-file", "-e", f"{value}^{{commit}}"],
        cwd=repository,
        check=True,
        capture_output=True,
    )


def _rpc_call(
    client: AuditedHttpClient,
    *,
    url: str,
    request_id: int,
    method: str,
    params: Sequence[object],
    role: str,
) -> object:
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": list(params),
    }
    response = _mapping(
        client.request_json(method="POST", url=url, role=role, json_payload=payload),
        path=f"rpc.{role}",
    )
    if response.get("error") is not None:
        raise RuntimeError(f"{role} returned JSON-RPC error: {response['error']}")
    if "result" not in response or response.get("result") is None:
        raise RuntimeError(f"{role} returned null/missing result")
    return response["result"]


def _legacy_result(payload: object, *, role: str, limit: int) -> list[Mapping[str, object]]:
    envelope = _mapping(payload, path=f"{role}.envelope")
    raw_result = envelope.get("result")
    if isinstance(raw_result, list):
        result = [_mapping(item, path=f"{role}.result") for item in raw_result]
        if len(result) > limit:
            raise RuntimeError(f"{role} exceeded documented response limit")
        if envelope.get("status") == "1" or not result:
            return result
    raise RuntimeError(
        f"{role} returned non-success logical response: "
        f"status={envelope.get('status')} message={envelope.get('message')}"
    )


def _collect_complete_legacy_logs(
    client: AuditedHttpClient,
    *,
    url: str,
    address: str,
    event_type: str,
    topic0: str,
    from_block: int,
    to_block: int,
    response_limit: int,
    extra_topics: Mapping[str, object] | None = None,
) -> tuple[list[dict[str, object]], int, int]:
    accepted: list[dict[str, object]] = []
    query_count = 0
    saturated_count = 0

    def visit(interval_from: int, interval_to: int) -> None:
        nonlocal query_count, saturated_count
        params: dict[str, object] = {
            "module": "logs",
            "action": "getLogs",
            "fromBlock": interval_from,
            "toBlock": interval_to,
            "address": address,
            "topic0": topic0,
        }
        params.update(dict(extra_topics or {}))
        query_count += 1
        role = f"legacy_logs:{event_type}:{address}:{interval_from}-{interval_to}"
        result = _legacy_result(
            client.request_json(method="GET", url=url, role=role, params=params),
            role=role,
            limit=response_limit,
        )
        if len(result) == response_limit:
            saturated_count += 1
            if interval_from == interval_to:
                raise RuntimeError(f"single-block legacy log response remains saturated: {role}")
            left, right = split_inclusive_interval(interval_from, interval_to)
            visit(*left)
            visit(*right)
            return
        accepted.extend(
            normalize_legacy_log(
                raw,
                event_type=event_type,
                expected_address=address,
                expected_topic0=topic0,
                from_block=interval_from,
                to_block=interval_to,
            )
            for raw in result
        )

    visit(from_block, to_block)
    return accepted, query_count, saturated_count


def _collect_transaction_logs(
    client: AuditedHttpClient,
    *,
    url_template: str,
    transaction_hash: str,
) -> tuple[list[dict[str, object]], int]:
    url = url_template.format(transaction_hash=transaction_hash)
    params: dict[str, object] = {}
    pages = 0
    seen_page_params: set[str] = set()
    logs: list[dict[str, object]] = []
    while True:
        page_key = canonical_json_sha256(params)
        if page_key in seen_page_params:
            raise RuntimeError("Blockscout transaction-log pagination cycle detected")
        seen_page_params.add(page_key)
        payload = _mapping(
            client.request_json(
                method="GET",
                url=url,
                role=f"transaction_logs:{transaction_hash}:page{pages}",
                params=params,
            ),
            path="transaction_logs.envelope",
        )
        items = _sequence(payload.get("items"), path="transaction_logs.items")
        logs.extend(
            normalize_transaction_log(
                _mapping(item, path="transaction_logs.item"),
                expected_tx_hash=transaction_hash,
            )
            for item in items
        )
        pages += 1
        if pages > 100:
            raise RuntimeError("transaction-log pagination exceeded 100 pages")
        next_page = payload.get("next_page_params")
        if next_page is None:
            break
        params = dict(_mapping(next_page, path="transaction_logs.next_page_params"))
    by_index: dict[int, dict[str, object]] = {}
    for log in logs:
        index = _integer(log.get("log_index"), path="transaction_log.log_index")
        prior = by_index.get(index)
        if prior is not None and prior != log:
            raise RuntimeError("conflicting transaction logs share one log index")
        by_index[index] = log
    return [by_index[index] for index in sorted(by_index)], pages


def _block_metadata(block: Mapping[str, object], *, expected_number: int) -> dict[str, object]:
    number = decode_quantity(block.get("number"), path="block.number")
    if number != expected_number:
        raise RuntimeError("block header number differs from requested number")
    timestamp = decode_quantity(block.get("timestamp"), path="block.timestamp")
    return {
        "number": number,
        "hash": normalize_hash(block.get("hash"), path="block.hash"),
        "timestamp_unix": timestamp,
        "timestamp_utc": datetime.fromtimestamp(timestamp, UTC).isoformat().replace("+00:00", "Z"),
    }


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    with path.open("x", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row), sort_keys=True, separators=(",", ":")) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT / "data/manifests/uniswap_v3_preperiod_support_v1.yaml",
    )
    artifact_root = ROOT / "experiments/v14_uniswap_v3_preperiod_support/artifacts"
    parser.add_argument("--pool-support", type=Path, default=artifact_root / "pool_support.jsonl")
    parser.add_argument("--identity-sample", type=Path, default=artifact_root / "identity_sample.jsonl")
    parser.add_argument("--response-hashes", type=Path, default=artifact_root / "http_response_hashes.json")
    parser.add_argument("--summary", type=Path, default=artifact_root / "summary.json")
    parser.add_argument("--collection-commit")
    arguments = parser.parse_args()
    for output in (
        arguments.pool_support,
        arguments.identity_sample,
        arguments.response_hashes,
        arguments.summary,
    ):
        if output.exists():
            raise FileExistsError(f"refusing to overwrite {output}")

    current_commit = require_clean_repository(ROOT)
    collection_commit = arguments.collection_commit or current_commit
    _validate_commit(ROOT, collection_commit)
    if collection_commit != current_commit:
        raise ValueError("collection commit must equal the clean worktree HEAD")

    contract = load_contract(arguments.contract)
    parent = _mapping(contract["parent"], path="parent")
    treatment_path = ROOT / cast(str, parent["treatment_ledger"])
    treatment_rows = load_jsonl(treatment_path)
    treatment_sha256 = hash_file(treatment_path)
    errors = validate_frozen_contract(
        contract,
        treatment_rows,
        treatment_ledger_sha256=treatment_sha256,
    )
    if errors:
        raise RuntimeError("invalid frozen U1a contract: " + "; ".join(errors))

    selection = _mapping(contract["selection"], path="selection")
    sample_rows = [
        dict(_mapping(row, path="selection.pool"))
        for row in _sequence(selection["pools"], path="selection.pools")
    ]
    window = _mapping(contract["window"], path="window")
    contracts = _mapping(contract["contracts"], path="contracts")
    identity = _mapping(contract["identity_sample"], path="identity_sample")
    sources = _mapping(contract["sources"], path="sources")
    gates = _mapping(contract["gates"], path="gates")
    npm = normalize_address(contracts["nonfungible_position_manager"], path="nonfungible_position_manager")
    from_block = cast(int, window["from_block"])
    to_block = cast(int, window["to_block"])
    response_limit = cast(int, sources["log_response_limit"])

    client = AuditedHttpClient(
        user_agent=cast(str, sources["user_agent"]),
        maximum_requests_per_second=float(cast(float, sources["maximum_requests_per_second_across_sources"])),
        maximum_transport_retries=cast(int, sources["maximum_transport_retries"]),
        maximum_http_attempts=cast(int, sources["maximum_http_attempts"]),
        maximum_response_bytes=cast(int, sources["maximum_response_bytes"]),
    )
    publicnode_url = cast(str, sources["publicnode_rpc_url"])
    rpc_id = 1
    chain_id = _rpc_call(
        client,
        url=publicnode_url,
        request_id=rpc_id,
        method="eth_chainId",
        params=[],
        role="chain_id",
    )
    rpc_id += 1
    if chain_id != "0x1":
        raise RuntimeError("PublicNode did not return Ethereum mainnet chain ID")
    start_block = _mapping(
        _rpc_call(
            client,
            url=publicnode_url,
            request_id=rpc_id,
            method="eth_getBlockByNumber",
            params=[hex(from_block), False],
            role="preperiod_start_block",
        ),
        path="preperiod_start_block",
    )
    rpc_id += 1
    end_block = _mapping(
        _rpc_call(
            client,
            url=publicnode_url,
            request_id=rpc_id,
            method="eth_getBlockByNumber",
            params=[hex(to_block), False],
            role="preperiod_end_block",
        ),
        path="preperiod_end_block",
    )
    rpc_id += 1
    start_metadata = _block_metadata(start_block, expected_number=from_block)
    end_metadata = _block_metadata(end_block, expected_number=to_block)
    treatment_timestamp = int(
        datetime.fromisoformat(
            cast(str, window["treatment_timestamp_utc"]).replace("Z", "+00:00")
        ).timestamp()
    )
    if cast(int, end_metadata["timestamp_unix"]) >= treatment_timestamp:
        raise RuntimeError("preperiod end block is not strictly before treatment timestamp")

    all_pool_events: list[Mapping[str, object]] = []
    legacy_query_count = 0
    saturated_query_count = 0
    blockscout_logs_url = cast(str, sources["blockscout_legacy_logs_url"])
    maximum_events = cast(int, sources["maximum_normalized_pool_events"])
    for sample in sample_rows:
        pool = normalize_address(sample["pool_address"], path="sample.pool_address")
        for event_type, topic0 in POOL_EVENT_TOPICS.items():
            events, queries, saturated = _collect_complete_legacy_logs(
                client,
                url=blockscout_logs_url,
                address=pool,
                event_type=event_type,
                topic0=topic0,
                from_block=from_block,
                to_block=to_block,
                response_limit=response_limit,
            )
            all_pool_events.extend(events)
            legacy_query_count += queries
            saturated_query_count += saturated
            if len(all_pool_events) > maximum_events:
                raise RuntimeError("frozen maximum_normalized_pool_events exceeded")
            print(
                json.dumps(
                    {
                        "pool": pool,
                        "event_type": event_type,
                        "event_count": len(events),
                        "query_count": queries,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )

    pool_events, duplicate_count, conflict_count = deduplicate_pool_events(all_pool_events)
    pool_support_rows = build_pool_support_rows(sample_rows, pool_events, npm_address=npm)
    selected_transactions, eligible_transaction_count = select_identity_transactions(
        pool_events,
        npm_address=npm,
        salt=cast(str, identity["salt"]),
        maximum_transactions=cast(int, identity["maximum_transactions"]),
    )

    actions_by_transaction: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for event in pool_events:
        if event.get("event_type") not in {"mint", "burn", "collect"}:
            continue
        if event.get("manager_owner") != npm:
            continue
        tx_hash = normalize_hash(event.get("transaction_hash"), path="event.transaction_hash")
        if tx_hash in selected_transactions:
            actions_by_transaction[tx_hash].append(event)

    identity_rows: list[dict[str, object]] = []
    transaction_log_page_count = 0
    tx_log_template = cast(str, sources["blockscout_transaction_logs_url_template"])
    for tx_hash in selected_transactions:
        transaction = _mapping(
            _rpc_call(
                client,
                url=publicnode_url,
                request_id=rpc_id,
                method="eth_getTransactionByHash",
                params=[tx_hash],
                role=f"identity_transaction:{tx_hash}",
            ),
            path="identity_transaction",
        )
        rpc_id += 1
        if normalize_hash(transaction.get("hash"), path="transaction.hash") != tx_hash:
            raise RuntimeError("identity transaction hash mismatch")
        tx_from = normalize_address(transaction.get("from"), path="transaction.from")
        tx_block = decode_quantity(transaction.get("blockNumber"), path="transaction.blockNumber")
        tx_index = decode_quantity(transaction.get("transactionIndex"), path="transaction.transactionIndex")
        if tx_block > to_block:
            raise RuntimeError("identity transaction falls outside the frozen preperiod")
        transaction_logs, pages = _collect_transaction_logs(
            client,
            url_template=tx_log_template,
            transaction_hash=tx_hash,
        )
        transaction_log_page_count += pages
        sampled_actions = actions_by_transaction[tx_hash]
        if any(
            event.get("block_number") != tx_block or event.get("transaction_index") != tx_index
            for event in sampled_actions
        ):
            raise RuntimeError("sampled action location differs from its transaction")
        pairings = pair_sampled_pool_actions(
            transaction_logs,
            sampled_actions,
            npm_address=npm,
        )
        for sampled_action in sampled_actions:
            pool = normalize_address(sampled_action.get("pool_address"), path="identity.pool_address")
            log_index = cast(int, sampled_action["log_index"])
            pairing = pairings[(pool, log_index)]
            identity_rows.append(
                {
                    "pool_address": pool,
                    "event_type": sampled_action["event_type"],
                    "block_number": tx_block,
                    "transaction_index": tx_index,
                    "pool_event_log_index": log_index,
                    "transaction_hash": tx_hash,
                    "transaction_from": tx_from,
                    "manager_owner": npm,
                    "pair_status": pairing["pair_status"],
                    "token_id": pairing.get("token_id"),
                    "owner_before_action": None,
                    "owner_after_transaction": None,
                    "transfer_event_count_through_action_block": None,
                    "transfer_history_identity_sha256": None,
                }
            )

    transfer_queries = 0
    transfer_saturated_queries = 0
    rows_by_token: defaultdict[int, list[dict[str, object]]] = defaultdict(list)
    for row in identity_rows:
        token_id = row.get("token_id")
        if isinstance(token_id, int):
            rows_by_token[token_id].append(row)
    for token_id, token_rows in sorted(rows_by_token.items()):
        maximum_action_block = max(cast(int, row["block_number"]) for row in token_rows)
        transfer_events, queries, saturated = _collect_complete_legacy_logs(
            client,
            url=blockscout_logs_url,
            address=npm,
            event_type="transfer",
            topic0=TRANSFER_TOPIC,
            from_block=cast(int, identity["transfer_history_from_block"]),
            to_block=maximum_action_block,
            response_limit=response_limit,
            extra_topics={
                "topic3": "0x" + token_id.to_bytes(32, "big").hex(),
                "topic0_3_opr": "and",
            },
        )
        transfer_queries += queries
        transfer_saturated_queries += saturated
        transfer_events, transfer_duplicates, transfer_conflicts = deduplicate_pool_events(transfer_events)
        duplicate_count += transfer_duplicates
        conflict_count += transfer_conflicts
        transfer_hash = canonical_json_sha256(transfer_events)
        for row in token_rows:
            owner_result = resolve_transfer_owners(
                transfer_events,
                token_id=token_id,
                action_block=cast(int, row["block_number"]),
                action_transaction_index=cast(int, row["transaction_index"]),
                action_log_index=cast(int, row["pool_event_log_index"]),
            )
            row.update(owner_result)
            row["transfer_history_identity_sha256"] = transfer_hash

    summary = summarize_preperiod_support(
        pool_support_rows,
        identity_rows,
        expected_pool_count=cast(int, selection["total_pools"]),
        eligible_identity_transaction_count=eligible_transaction_count,
        selected_identity_transaction_count=len(selected_transactions),
        maximum_identity_transactions=cast(int, identity["maximum_transactions"]),
        duplicate_log_count=duplicate_count,
        conflicting_log_count=conflict_count,
        complete_unsaturated_partitions=True,
        minimum_swap_active_pools=cast(int, gates["minimum_swap_active_pools"]),
        minimum_position_active_pools=cast(int, gates["minimum_position_active_pools"]),
        minimum_position_action_logs=cast(int, gates["minimum_position_action_logs"]),
        minimum_npm_position_action_share=float(cast(float, gates["minimum_npm_position_action_share"])),
        minimum_eligible_npm_action_transactions=cast(int, gates["minimum_eligible_npm_action_transactions"]),
        minimum_exact_pool_to_token_pair_rate=float(
            cast(float, gates["minimum_exact_pool_to_token_pair_rate"])
        ),
        minimum_owner_after_transaction_resolution_rate=float(
            cast(float, gates["minimum_owner_after_transaction_resolution_rate"])
        ),
    )
    summary["window"] = {
        "from_block": start_metadata,
        "to_block": end_metadata,
        "inclusive_block_count": to_block - from_block + 1,
        "duration_seconds_between_headers": cast(int, end_metadata["timestamp_unix"])
        - cast(int, start_metadata["timestamp_unix"]),
        "strictly_before_treatment": True,
    }
    summary["source_usage"] = {
        "successful_http_response_count": len(client.response_records),
        "http_attempt_count": client.http_attempt_count,
        "response_bytes": client.response_bytes,
        "pool_legacy_log_query_count": legacy_query_count,
        "pool_saturated_query_count": saturated_query_count,
        "transaction_log_page_count": transaction_log_page_count,
        "transfer_legacy_log_query_count": transfer_queries,
        "transfer_saturated_query_count": transfer_saturated_queries,
        "raw_response_payloads_retained": False,
    }
    summary["access"] = {
        "swap_amount_or_price_fields_decoded": False,
        "liquidity_or_token_amount_fields_decoded": False,
        "transaction_calldata_decoded": False,
        "post_treatment_pool_events_opened": False,
        "post_treatment_responses_opened": False,
        "control_pool_behavior_opened": False,
        "paid_data": False,
        "gpu_hours": 0,
    }
    summary["ownership"] = {
        "collection_git_commit": collection_commit,
        "summary_git_commit": current_commit,
        "collected_at_utc": _utc_now(),
        "contract_sha256": contract_sha256(arguments.contract),
        "parent_treatment_ledger_sha256": treatment_sha256,
    }

    arguments.pool_support.parent.mkdir(parents=True, exist_ok=True)
    _write_jsonl(arguments.pool_support, pool_support_rows)
    _write_jsonl(arguments.identity_sample, identity_rows)
    response_manifest = {
        "schema_version": "ecophys-http-response-hash-manifest/v1",
        "records": client.response_records,
        "successful_response_count": len(client.response_records),
        "http_attempt_count": client.http_attempt_count,
        "response_bytes": client.response_bytes,
        "records_sha256": canonical_json_sha256(client.response_records),
        "raw_response_payloads_retained": False,
    }
    _write_json(arguments.response_hashes, response_manifest)
    summary["artifacts"] = {
        "pool_support_sha256": hash_file(arguments.pool_support),
        "pool_support_row_count": len(pool_support_rows),
        "identity_sample_sha256": hash_file(arguments.identity_sample),
        "identity_sample_row_count": len(identity_rows),
        "http_response_hash_manifest_sha256": hash_file(arguments.response_hashes),
        "pool_events_canonical_sha256": canonical_json_sha256(pool_events),
    }
    _write_json(arguments.summary, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
