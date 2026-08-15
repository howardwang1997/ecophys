#!/usr/bin/env python3
"""Collect the frozen full-population Uniswap preperiod exposure census."""

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
    decode_quantity,
    normalize_address,
    normalize_hash,
)
from ecomd.research.uniswap_v3_preperiod_support import (
    build_exposure_census_row,
    census_population_rows,
    contract_sha256,
    deduplicate_pool_events,
    hash_file,
    load_contract,
    load_jsonl,
    normalize_rpc_pool_log,
    split_inclusive_interval,
    summarize_exposure_census,
    validate_exposure_census_contract,
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


class AuditedRpcClient:
    """Rate-limited JSON-RPC client with response-hash and hard-cap accounting."""

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
        self._next_rpc_id = 1
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})
        self.http_attempt_count = 0
        self.response_bytes = 0
        self.response_records: list[dict[str, object]] = []

    def call(self, *, url: str, method: str, params: Sequence[object], role: str) -> object:
        request_id = self._next_rpc_id
        self._next_rpc_id += 1
        request_payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": list(params),
        }
        prior_errors: list[str] = []
        for attempt in range(self._maximum_transport_retries + 1):
            if self.http_attempt_count >= self._maximum_http_attempts:
                raise RuntimeError("frozen maximum_http_attempts exhausted")
            if self._last_start is not None:
                delay = self._minimum_interval - (time.monotonic() - self._last_start)
                time.sleep(max(0.0, delay))
            self._last_start = time.monotonic()
            self.http_attempt_count += 1
            try:
                response = self._session.post(url, json=request_payload, timeout=60.0)
                body = response.content
                self.response_bytes += len(body)
                if self.response_bytes > self._maximum_response_bytes:
                    raise RuntimeError("frozen maximum_response_bytes exceeded")
                response.raise_for_status()
                payload: object = response.json()
            except (requests.RequestException, ValueError) as error:
                prior_errors.append(f"{type(error).__name__}: {error}")
            else:
                envelope = _mapping(payload, path=f"rpc.{role}")
                if envelope.get("error") is not None:
                    raise RuntimeError(f"{role} returned JSON-RPC error: {envelope['error']}")
                if "result" not in envelope or envelope.get("result") is None:
                    raise RuntimeError(f"{role} returned null/missing result")
                self.response_records.append(
                    {
                        "request_index": len(self.response_records),
                        "role": role,
                        "url": url,
                        "method": method,
                        "params": list(params),
                        "request_sha256": canonical_json_sha256(request_payload),
                        "response_body_sha256": hashlib.sha256(body).hexdigest(),
                        "response_canonical_json_sha256": canonical_json_sha256(payload),
                        "response_bytes": len(body),
                        "retrieved_at_utc": _utc_now(),
                        "attempt_count": attempt + 1,
                        "prior_transport_errors": prior_errors,
                    }
                )
                return envelope["result"]
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


def _collect_pool_logs(
    client: AuditedRpcClient,
    *,
    url: str,
    pool_address: str,
    topics_by_event: Mapping[str, str],
    from_block: int,
    to_block: int,
    response_limit: int,
) -> tuple[list[dict[str, object]], int, int]:
    accepted: list[dict[str, object]] = []
    query_count = 0
    saturated_count = 0
    ordered_topics = [topics_by_event[name] for name in ("swap", "mint", "burn", "collect")]

    def visit(interval_from: int, interval_to: int) -> None:
        nonlocal query_count, saturated_count
        query_count += 1
        role = f"pool_logs:{pool_address}:{interval_from}-{interval_to}"
        raw_result = client.call(
            url=url,
            method="eth_getLogs",
            params=[
                {
                    "fromBlock": hex(interval_from),
                    "toBlock": hex(interval_to),
                    "address": pool_address,
                    "topics": [ordered_topics],
                }
            ],
            role=role,
        )
        result = _sequence(raw_result, path=f"{role}.result")
        if len(result) > response_limit:
            raise RuntimeError("eth_getLogs response exceeded frozen/documented limit")
        if len(result) == response_limit:
            saturated_count += 1
            if interval_from == interval_to:
                raise RuntimeError(f"single-block pool log response remains saturated: {role}")
            left, right = split_inclusive_interval(interval_from, interval_to)
            visit(*left)
            visit(*right)
            return
        accepted.extend(
            normalize_rpc_pool_log(
                _mapping(log, path=f"{role}.log"),
                expected_pool=pool_address,
                allowed_topics=topics_by_event,
                from_block=interval_from,
                to_block=interval_to,
            )
            for log in result
        )

    visit(from_block, to_block)
    return accepted, query_count, saturated_count


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
        default=ROOT / "data/manifests/uniswap_v3_preperiod_exposure_census_v1.yaml",
    )
    artifact_root = ROOT / "experiments/v14_uniswap_v3_preperiod_exposure_census/artifacts"
    parser.add_argument("--exposure-census", type=Path, default=artifact_root / "exposure_census.jsonl")
    parser.add_argument("--response-hashes", type=Path, default=artifact_root / "http_response_hashes.json")
    parser.add_argument("--summary", type=Path, default=artifact_root / "summary.json")
    parser.add_argument("--collection-commit")
    arguments = parser.parse_args()
    for output in (arguments.exposure_census, arguments.response_hashes, arguments.summary):
        if output.exists():
            raise FileExistsError(f"refusing to overwrite {output}")

    current_commit = require_clean_repository(ROOT)
    collection_commit = arguments.collection_commit or current_commit
    _validate_commit(ROOT, collection_commit)
    if collection_commit != current_commit:
        raise ValueError("collection commit must equal the clean worktree HEAD")

    contract = load_contract(arguments.contract)
    parents = _mapping(contract["parents"], path="parents")
    treatment_path = ROOT / cast(str, parents["u0_treatment_ledger"])
    u1a_summary_path = ROOT / cast(str, parents["u1a_summary"])
    treatment_rows = load_jsonl(treatment_path)
    treatment_sha256 = hash_file(treatment_path)
    u1a_summary_sha256 = hash_file(u1a_summary_path)
    errors = validate_exposure_census_contract(
        contract,
        treatment_rows,
        treatment_ledger_sha256=treatment_sha256,
        u1a_summary_sha256=u1a_summary_sha256,
    )
    if errors:
        raise RuntimeError("invalid frozen exposure census contract: " + "; ".join(errors))

    population_rows = census_population_rows(treatment_rows)
    window = _mapping(contract["window"], path="window")
    events = _mapping(contract["events"], path="events")
    sources = _mapping(contract["sources"], path="sources")
    gates = _mapping(contract["gates"], path="gates")
    from_block = cast(int, window["from_block"])
    to_block = cast(int, window["to_block"])
    topics_by_event = {
        name: normalize_hash(events[name], path=f"events.{name}")
        for name in ("swap", "mint", "burn", "collect")
    }
    npm = normalize_address(events["nonfungible_position_manager"], path="npm")
    client = AuditedRpcClient(
        user_agent=cast(str, sources["user_agent"]),
        maximum_requests_per_second=float(cast(float, sources["maximum_requests_per_second_across_sources"])),
        maximum_transport_retries=cast(int, sources["maximum_transport_retries"]),
        maximum_http_attempts=cast(int, sources["maximum_http_attempts"]),
        maximum_response_bytes=cast(int, sources["maximum_response_bytes"]),
    )
    publicnode_url = cast(str, sources["publicnode_rpc_url"])
    if client.call(url=publicnode_url, method="eth_chainId", params=[], role="chain_id") != "0x1":
        raise RuntimeError("PublicNode did not return Ethereum mainnet chain ID")
    start_block = _mapping(
        client.call(
            url=publicnode_url,
            method="eth_getBlockByNumber",
            params=[hex(from_block), False],
            role="preperiod_start_block",
        ),
        path="preperiod_start_block",
    )
    end_block = _mapping(
        client.call(
            url=publicnode_url,
            method="eth_getBlockByNumber",
            params=[hex(to_block), False],
            role="preperiod_end_block",
        ),
        path="preperiod_end_block",
    )
    start_metadata = _block_metadata(start_block, expected_number=from_block)
    end_metadata = _block_metadata(end_block, expected_number=to_block)
    treatment_timestamp = int(
        datetime.fromisoformat(
            cast(str, window["treatment_timestamp_utc"]).replace("Z", "+00:00")
        ).timestamp()
    )
    if cast(int, end_metadata["timestamp_unix"]) >= treatment_timestamp:
        raise RuntimeError("census end block is not strictly before treatment")

    census_rows: list[dict[str, object]] = []
    query_count = 0
    saturated_query_count = 0
    duplicate_count = 0
    conflict_count = 0
    normalized_event_count = 0
    maximum_events = cast(int, sources["maximum_normalized_events"])
    log_url = cast(str, sources["blockscout_eth_rpc_url"])
    response_limit = cast(int, sources["log_response_limit"])
    for index, population_row in enumerate(population_rows):
        pool = cast(str, population_row["pool_address"])
        pool_events, pool_queries, pool_saturated = _collect_pool_logs(
            client,
            url=log_url,
            pool_address=pool,
            topics_by_event=topics_by_event,
            from_block=from_block,
            to_block=to_block,
            response_limit=response_limit,
        )
        pool_events, pool_duplicates, pool_conflicts = deduplicate_pool_events(pool_events)
        query_count += pool_queries
        saturated_query_count += pool_saturated
        duplicate_count += pool_duplicates
        conflict_count += pool_conflicts
        normalized_event_count += len(pool_events)
        if normalized_event_count > maximum_events:
            raise RuntimeError("frozen maximum_normalized_events exceeded")
        row = build_exposure_census_row(population_row, pool_events, npm_address=npm)
        census_rows.append(row)
        if (index + 1) % 25 == 0 or bool(row["economically_exposed_preperiod"]):
            print(
                json.dumps(
                    {
                        "completed_pools": index + 1,
                        "pool": pool,
                        "event_count": len(pool_events),
                        "swap_count": row["swap_count"],
                        "position_action_count": row["position_action_count"],
                        "query_count": pool_queries,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )

    summary = summarize_exposure_census(
        census_rows,
        duplicate_log_count=duplicate_count,
        conflicting_log_count=conflict_count,
        complete_unsaturated_partitions=True,
        minimum_swap_active_pools=cast(int, gates["minimum_swap_active_pools"]),
        minimum_position_active_pools=cast(int, gates["minimum_position_active_pools"]),
        minimum_position_action_logs=cast(int, gates["minimum_position_action_logs"]),
        minimum_swap_active_pools_per_fee_value=cast(int, gates["minimum_swap_active_pools_per_fee_value"]),
        minimum_position_active_pools_per_fee_value=cast(
            int, gates["minimum_position_active_pools_per_fee_value"]
        ),
        minimum_npm_position_action_share=float(cast(float, gates["minimum_npm_position_action_share"])),
        maximum_single_pool_swap_count_share=float(
            cast(float, gates["maximum_single_pool_swap_count_share"])
        ),
        maximum_single_pool_position_action_count_share=float(
            cast(float, gates["maximum_single_pool_position_action_count_share"])
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
        "pool_log_query_count": query_count,
        "saturated_pool_log_query_count": saturated_query_count,
        "normalized_event_count": normalized_event_count,
        "raw_response_payloads_retained": False,
    }
    summary["access"] = {
        "amount_price_or_liquidity_fields_decoded": False,
        "transaction_sender_or_calldata_opened": False,
        "indexed_pool_participant_fields_transferred_but_discarded": True,
        "non_npm_manager_addresses_retained": False,
        "token_id_or_transfer_history_opened": False,
        "control_pool_behavior_opened": False,
        "post_treatment_pool_events_opened": False,
        "post_treatment_responses_opened": False,
        "paid_data": False,
        "gpu_hours": 0,
    }
    summary["ownership"] = {
        "collection_git_commit": collection_commit,
        "summary_git_commit": current_commit,
        "collected_at_utc": _utc_now(),
        "contract_sha256": contract_sha256(arguments.contract),
        "parent_treatment_ledger_sha256": treatment_sha256,
        "parent_u1a_summary_sha256": u1a_summary_sha256,
    }

    arguments.exposure_census.parent.mkdir(parents=True, exist_ok=True)
    _write_jsonl(arguments.exposure_census, census_rows)
    response_manifest = {
        "schema_version": "ecophys-json-rpc-response-hash-manifest/v2",
        "records": client.response_records,
        "successful_response_count": len(client.response_records),
        "http_attempt_count": client.http_attempt_count,
        "response_bytes": client.response_bytes,
        "records_sha256": canonical_json_sha256(client.response_records),
        "raw_response_payloads_retained": False,
    }
    _write_json(arguments.response_hashes, response_manifest)
    summary["artifacts"] = {
        "exposure_census_sha256": hash_file(arguments.exposure_census),
        "exposure_census_row_count": len(census_rows),
        "http_response_hash_manifest_sha256": hash_file(arguments.response_hashes),
        "census_rows_canonical_sha256": canonical_json_sha256(census_rows),
    }
    _write_json(arguments.summary, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
