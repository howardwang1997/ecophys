"""Run the frozen Aave D1B identification and protocol-ledger audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ecomd.data.aave_qualification import (
    assess_clean_panel,
    canonical_sha256,
    classify_clean_policy_windows,
    extract_rate_strategy_updates,
    extract_solidity_event_definitions,
    find_payload_execution,
    reduce_policy_logs,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_CONTRACT = "0x9AEE0B04504CeF83A65AC3f0e838D0593BCb2BC7"


class RpcError(RuntimeError):
    """Raised when an Ethereum JSON-RPC request fails."""

    def __init__(
        self,
        message: str,
        *,
        rpc_code: int | None = None,
        http_status: int | None = None,
    ) -> None:
        super().__init__(message)
        self.rpc_code = rpc_code
        self.http_status = http_status


def _retryable_rpc_server_error(payload: Any) -> bool:
    if not isinstance(payload, Mapping):
        return False
    remote_error = payload.get("error")
    return (
        isinstance(remote_error, Mapping)
        and remote_error.get("code") == -32000
        and str(remote_error.get("message", "")).lower() == "method handler crashed"
    )


class _RpcClient:
    def __init__(
        self,
        *,
        url: str,
        timeout: int,
        transport_retries: int,
        minimum_request_interval_seconds: float,
        rate_limit_retries: int,
        rate_limit_backoff_initial_seconds: float,
        rate_limit_backoff_max_seconds: float,
    ) -> None:
        retry = Retry(
            total=transport_retries,
            connect=transport_retries,
            read=transport_retries,
            status=transport_retries,
            allowed_methods=frozenset({"POST"}),
            status_forcelist=(500, 502, 503, 504),
            backoff_factor=0.5,
            raise_on_status=False,
        )
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.session.headers.update({"User-Agent": "EcoPhys-Aave-D1B-audit/1.0"})
        self.url = url
        self.timeout = timeout
        self.minimum_request_interval_seconds = minimum_request_interval_seconds
        self.rate_limit_retries = rate_limit_retries
        self.rate_limit_backoff_initial_seconds = rate_limit_backoff_initial_seconds
        self.rate_limit_backoff_max_seconds = rate_limit_backoff_max_seconds
        self.next_request_id = 1
        self.method_counts: Counter[str] = Counter()
        self.log_range_splits = 0
        self.log_topic_splits = 0
        self.rate_limit_retry_count = 0
        self.rate_limit_wait_seconds = 0.0
        self.server_error_retry_count = 0
        self.server_error_wait_seconds = 0.0
        self._last_request_started: float | None = None
        self._block_cache: dict[int, dict[str, Any]] = {}

    def _pace(self) -> None:
        now = time.monotonic()
        if self._last_request_started is not None:
            remaining = self.minimum_request_interval_seconds - (now - self._last_request_started)
            if remaining > 0:
                time.sleep(remaining)
        self._last_request_started = time.monotonic()

    def call(self, method: str, params: list[Any]) -> Any:
        request_id = self.next_request_id
        self.next_request_id += 1
        response: requests.Response | None = None
        payload: Any = None
        for attempt in range(self.rate_limit_retries + 1):
            self._pace()
            self.method_counts[method] += 1
            response = self.session.post(
                self.url,
                json={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "method": method,
                    "params": params,
                },
                timeout=self.timeout,
            )
            try:
                payload = response.json()
            except requests.JSONDecodeError as error:
                raise RpcError(
                    f"RPC {method} returned non-JSON HTTP {response.status_code}",
                    http_status=response.status_code,
                ) from error
            retry_kind: str | None = None
            if response.status_code == 429:
                retry_kind = "rate_limit"
            elif response.status_code < 400 and _retryable_rpc_server_error(payload):
                retry_kind = "server_error"
            if retry_kind is None or attempt >= self.rate_limit_retries:
                break
            retry_after = response.headers.get("Retry-After") if retry_kind == "rate_limit" else None
            try:
                header_delay = max(0.0, float(retry_after)) if retry_after else 0.0
            except ValueError:
                header_delay = 0.0
            delay = min(
                max(self.rate_limit_backoff_initial_seconds * 2**attempt, header_delay),
                self.rate_limit_backoff_max_seconds,
            )
            if retry_kind == "rate_limit":
                self.rate_limit_retry_count += 1
                self.rate_limit_wait_seconds += delay
            else:
                self.server_error_retry_count += 1
                self.server_error_wait_seconds += delay
            time.sleep(delay)
        if response is None:
            raise AssertionError("RPC loop completed without a response")
        if response.status_code >= 400:
            remote_error = payload.get("error") if isinstance(payload, Mapping) else None
            raise RpcError(
                f"RPC {method} returned HTTP {response.status_code}: {remote_error}",
                http_status=response.status_code,
            )
        if not isinstance(payload, Mapping):
            raise RpcError(f"RPC {method} returned non-object JSON")
        if payload.get("error") is not None:
            remote_error = payload["error"]
            rpc_code = (
                int(remote_error["code"])
                if isinstance(remote_error, Mapping) and isinstance(remote_error.get("code"), int)
                else None
            )
            raise RpcError(f"RPC {method} failed: {remote_error}", rpc_code=rpc_code)
        if "result" not in payload:
            raise RpcError(f"RPC {method} returned no result")
        return payload["result"]

    def block(self, number: int) -> dict[str, Any]:
        if number < 0:
            raise ValueError("block number cannot be negative")
        cached = self._block_cache.get(number)
        if cached is not None:
            return cached
        result = self.call("eth_getBlockByNumber", [hex(number), False])
        if not isinstance(result, Mapping):
            raise RpcError(f"block {number} is absent or malformed")
        observed_number = _hex_quantity(result.get("number"), field="block number")
        if observed_number != number:
            raise RpcError(f"requested block {number}, received {observed_number}")
        header = {
            "number": number,
            "timestamp": _hex_quantity(result.get("timestamp"), field="block timestamp"),
            "hash": _hash(str(result.get("hash")), field="block hash"),
        }
        self._block_cache[number] = header
        return header


def _git(*args: str, root: Path = REPO_ROOT) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"YAML contract must be an object: {path}")
    return payload


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON artifact must be an object: {path}")
    return payload


def _hex_quantity(value: Any, *, field: str) -> int:
    if not isinstance(value, str) or re.fullmatch(r"0x[0-9a-fA-F]+", value) is None:
        raise RpcError(f"invalid {field}: {value}")
    return int(value, 16)


def _hash(value: str, *, field: str) -> str:
    normalized = value.lower()
    if re.fullmatch(r"0x[0-9a-f]{64}", normalized) is None:
        raise RpcError(f"invalid {field}: {value}")
    return normalized


def _utc(unix_seconds: int) -> str:
    return datetime.fromtimestamp(unix_seconds, UTC).isoformat()


def _unix(iso_timestamp: str) -> int:
    parsed = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp is not timezone-aware: {iso_timestamp}")
    return int(parsed.timestamp())


def _verify_digest(payload: Mapping[str, Any], expected: str, *, label: str) -> None:
    stored = str(payload.get("canonical_payload_sha256"))
    body = {key: value for key, value in payload.items() if key != "canonical_payload_sha256"}
    recomputed = canonical_sha256(body)
    if stored != expected or recomputed != expected:
        raise RuntimeError(
            f"{label} digest mismatch: stored={stored}, recomputed={recomputed}, expected={expected}"
        )


def _write_policy_checkpoint(
    path: Path,
    *,
    identity: Mapping[str, str],
    support_windows: Sequence[Mapping[str, Any]],
    merged_intervals: Sequence[tuple[int, int]],
    completed_interval_count: int,
    policy_events: Sequence[Mapping[str, Any]],
) -> None:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "identity": dict(identity),
        "support_windows": list(support_windows),
        "merged_intervals": [list(interval) for interval in merged_intervals],
        "completed_interval_count": completed_interval_count,
        "policy_events": list(policy_events),
        "contains_only_boundary_and_sanitized_policy_metadata": True,
        "contains_raw_logs_behavior_or_participants": False,
    }
    payload["canonical_payload_sha256"] = canonical_sha256(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _load_policy_checkpoint(
    path: Path,
    *,
    identity: Mapping[str, str],
) -> tuple[list[dict[str, Any]], list[tuple[int, int]], int, list[dict[str, Any]]] | None:
    if not path.exists():
        return None
    payload = _load_json(path)
    stored_digest = str(payload.get("canonical_payload_sha256"))
    body = {key: value for key, value in payload.items() if key != "canonical_payload_sha256"}
    if canonical_sha256(body) != stored_digest:
        raise RuntimeError("D1B policy checkpoint digest mismatch")
    if payload.get("identity") != dict(identity):
        raise RuntimeError("D1B policy checkpoint identity mismatch")
    if payload.get("contains_raw_logs_behavior_or_participants") is not False:
        raise RuntimeError("D1B policy checkpoint lacks the no-raw-data assertion")
    raw_windows = payload.get("support_windows")
    raw_intervals = payload.get("merged_intervals")
    raw_events = payload.get("policy_events")
    if (
        not isinstance(raw_windows, list)
        or any(not isinstance(row, dict) for row in raw_windows)
        or not isinstance(raw_intervals, list)
        or any(
            not isinstance(row, list) or len(row) != 2 or any(not isinstance(value, int) for value in row)
            for row in raw_intervals
        )
        or not isinstance(raw_events, list)
        or any(not isinstance(row, dict) for row in raw_events)
    ):
        raise RuntimeError("D1B policy checkpoint is malformed")
    intervals = [(int(row[0]), int(row[1])) for row in raw_intervals]
    completed = int(payload.get("completed_interval_count", -1))
    if not 0 <= completed <= len(intervals):
        raise RuntimeError("D1B checkpoint completed interval count is invalid")
    return list(raw_windows), intervals, completed, list(raw_events)


def _verify_repo(root: Path, expected_sha: str, *, label: str) -> dict[str, Any]:
    observed = _git("rev-parse", "HEAD", root=root)
    if observed != expected_sha:
        raise RuntimeError(f"{label} is at {observed}, expected {expected_sha}")
    dirty = _git("status", "--porcelain", root=root)
    if dirty:
        raise RuntimeError(f"{label} source repository is dirty")
    return {"git_sha": observed, "clean_worktree": True}


def _first_block_at_or_after(
    client: _RpcClient,
    *,
    target_timestamp: int,
    upper_block: int,
    search_back_blocks: int = 700_000,
) -> int:
    if client.block(upper_block)["timestamp"] < target_timestamp:
        raise RuntimeError("boundary target occurs after its supplied upper block")
    lower_block = max(0, upper_block - search_back_blocks)
    while client.block(lower_block)["timestamp"] >= target_timestamp:
        if lower_block == 0:
            return 0
        upper_block = lower_block
        lower_block = max(0, lower_block - search_back_blocks)
    while lower_block + 1 < upper_block:
        middle = (lower_block + upper_block) // 2
        if client.block(middle)["timestamp"] >= target_timestamp:
            upper_block = middle
        else:
            lower_block = middle
    return upper_block


def _splittable(error: RpcError) -> bool:
    if error.http_status in {408, 413, 504}:
        return True
    message = str(error).lower()
    return any(
        marker in message
        for marker in (
            "block range",
            "requested too many blocks",
            "range is too wide",
            "range limit",
            "ranges over",
            "exceeds limit of",
            "response size",
            "result size",
            "too many results",
            "query returned more than",
            "log response size exceeded",
        )
    )


def _prefer_topic_split(error: RpcError) -> bool:
    if error.http_status in {408, 413, 504}:
        return True
    message = str(error).lower()
    return any(
        marker in message
        for marker in (
            "method handler crashed",
            "response size",
            "result size",
            "too many results",
            "query returned more than",
            "log response size exceeded",
        )
    )


def _get_logs_with_split(
    client: _RpcClient,
    *,
    addresses: Sequence[str],
    topics: Sequence[str],
    start_block: int,
    end_block_inclusive: int,
    remaining_split_depth: int,
    split_topics_first: bool = False,
) -> list[Mapping[str, Any]]:
    try:
        payload = client.call(
            "eth_getLogs",
            [
                {
                    "address": addresses[0] if len(addresses) == 1 else list(addresses),
                    "fromBlock": hex(start_block),
                    "toBlock": hex(end_block_inclusive),
                    "topics": [list(topics)],
                }
            ],
        )
    except RpcError as error:
        if split_topics_first and len(topics) > 1 and _prefer_topic_split(error):
            client.log_topic_splits += 1
            middle_topic = len(topics) // 2
            return _get_logs_with_split(
                client,
                addresses=addresses,
                topics=topics[:middle_topic],
                start_block=start_block,
                end_block_inclusive=end_block_inclusive,
                remaining_split_depth=remaining_split_depth,
                split_topics_first=True,
            ) + _get_logs_with_split(
                client,
                addresses=addresses,
                topics=topics[middle_topic:],
                start_block=start_block,
                end_block_inclusive=end_block_inclusive,
                remaining_split_depth=remaining_split_depth,
                split_topics_first=True,
            )
        if not _splittable(error) or start_block >= end_block_inclusive or remaining_split_depth <= 0:
            raise
        client.log_range_splits += 1
        middle = (start_block + end_block_inclusive) // 2
        return _get_logs_with_split(
            client,
            addresses=addresses,
            topics=topics,
            start_block=start_block,
            end_block_inclusive=middle,
            remaining_split_depth=remaining_split_depth - 1,
            split_topics_first=split_topics_first,
        ) + _get_logs_with_split(
            client,
            addresses=addresses,
            topics=topics,
            start_block=middle + 1,
            end_block_inclusive=end_block_inclusive,
            remaining_split_depth=remaining_split_depth - 1,
            split_topics_first=split_topics_first,
        )
    if not isinstance(payload, list) or any(not isinstance(row, Mapping) for row in payload):
        raise RpcError("eth_getLogs returned a malformed result")
    return payload


def _merge_block_intervals(intervals: Sequence[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for start, end in sorted(intervals):
        if start < 0 or end < start:
            raise ValueError(f"invalid block interval {start}:{end}")
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _keccak_topic(signature: str) -> str:
    process = subprocess.run(
        ["openssl", "dgst", "-keccak-256", "-binary"],
        input=signature.encode(),
        check=True,
        capture_output=True,
    )
    if len(process.stdout) != 32:
        raise RuntimeError("OpenSSL returned a non-32-byte Keccak-256 digest")
    return "0x" + process.stdout.hex()


def _forum_timeline(
    session: requests.Session,
    *,
    base_url: str,
    topic_id: int,
) -> dict[str, Any]:
    response = session.get(f"{base_url.rstrip('/')}/t/{topic_id}.json", timeout=30)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, Mapping) or int(payload.get("id", -1)) != topic_id:
        raise RuntimeError(f"forum topic {topic_id} returned malformed metadata")
    post_stream = payload.get("post_stream")
    posts = post_stream.get("posts") if isinstance(post_stream, Mapping) else None
    if not isinstance(posts, list) or not posts:
        raise RuntimeError(f"forum topic {topic_id} has no first post")
    first_candidates = [post for post in posts if int(post.get("post_number", -1)) == 1]
    if len(first_candidates) != 1:
        raise RuntimeError(f"forum topic {topic_id} does not have one post number 1")
    first_post = first_candidates[0]
    created_at = str(first_post["created_at"])
    return {
        "topic_id": topic_id,
        "title": str(payload["title"]),
        "slug": str(payload["slug"]),
        "first_post_timestamp": _unix(created_at),
        "first_post_utc": _utc(_unix(created_at)),
        "forum_response_sha256": hashlib.sha256(response.content).hexdigest(),
        "raw_forum_content_persisted": False,
    }


def _source_file_at_commit(
    proposals_root: Path,
    *,
    commit: str,
    directory: str,
    chain_label: str,
) -> tuple[str, str] | None:
    tree = f"{commit}:src/{directory}"
    names = _git("ls-tree", "--name-only", tree, root=proposals_root).splitlines()
    prefix = f"AaveV3{chain_label}_"
    candidates = [
        name
        for name in names
        if name.startswith(prefix) and name.endswith(".sol") and not name.endswith(".t.sol")
    ]
    if not candidates:
        return None
    if len(candidates) != 1:
        raise RuntimeError(f"{commit}:src/{directory} has {len(candidates)} {chain_label} V3 sources")
    path = f"src/{directory}/{candidates[0]}"
    source = _git("show", f"{commit}:{path}", root=proposals_root)
    return path, source


def _audit_cross_chain(
    config: Mapping[str, Any],
    t0: Mapping[str, Any],
    governance_root: Path,
    proposals_root: Path,
) -> dict[str, Any]:
    payload_map = json.loads(
        (governance_root / "cache" / "ui" / "mainnet" / "proposals_payloads.json").read_text(encoding="utf-8")
    )["data"]
    chain_by_id = {int(chain_id): label for label, chain_id in config["chain_labels"].items()}
    aliases = {
        str(alias): str(canonical)
        for alias, canonical in config["cross_chain_gate"]["comparator_asset_aliases"].items()
    }
    t0_by_proposal = {int(event["proposal_id"]): event for event in t0["events"]}
    proposal_results: list[dict[str, Any]] = []
    for proposal in config["proposals"]:
        proposal_id = int(proposal["id"])
        t0_event = t0_by_proposal[proposal_id]
        rows = payload_map.get(str(proposal_id))
        if not isinstance(rows, list) or not rows:
            raise RuntimeError(f"proposal {proposal_id} has no payload mapping")
        chain_results: list[dict[str, Any]] = []
        for payload_row in rows:
            chain_id = int(payload_row["chainId"])
            if chain_id not in chain_by_id:
                raise RuntimeError(f"proposal {proposal_id} uses unfrozen chain ID {chain_id}")
            execution = find_payload_execution(
                governance_root,
                proposal_id=proposal_id,
                chain_id=chain_id,
            )
            if execution["implementation_commit"] != t0_event["implementation_commit"]:
                raise RuntimeError(f"proposal {proposal_id} implementation commit drift")
            if execution["implementation_directory"] != t0_event["implementation_directory"]:
                raise RuntimeError(f"proposal {proposal_id} implementation directory drift")
            source_record = _source_file_at_commit(
                proposals_root,
                commit=str(execution["implementation_commit"]),
                directory=str(execution["implementation_directory"]),
                chain_label=str(chain_by_id[chain_id]),
            )
            source_path: str | None = None
            source_sha256: str | None = None
            stable_updates: list[dict[str, Any]] = []
            if source_record is not None:
                source_path, source = source_record
                source_sha256 = hashlib.sha256(source.encode()).hexdigest()
                for update in extract_rate_strategy_updates(source):
                    canonical_symbol = aliases.get(str(update["asset_alias"]))
                    if canonical_symbol is not None:
                        stable_updates.append({**update, "canonical_symbol": canonical_symbol})
            comparable_updates = [update for update in stable_updates if bool(update["slope1_only"])]
            chain_results.append(
                {
                    **execution,
                    "chain_label": str(chain_by_id[chain_id]),
                    "execution_utc": _utc(int(execution["executed_at_unix"])),
                    "source_path": source_path,
                    "source_sha256": source_sha256,
                    "source_audited": source_record is not None,
                    "stablecoin_updates": stable_updates,
                    "comparable_stablecoin_updates": comparable_updates,
                    "source_audited_comparable": bool(comparable_updates),
                }
            )

        ethereum = [row for row in chain_results if int(row["chain_id"]) == 1]
        if len(ethereum) != 1:
            raise RuntimeError(f"proposal {proposal_id} does not have one Ethereum payload")
        if (
            int(ethereum[0]["execution_block"]) != int(t0_event["execution_block"])
            or int(ethereum[0]["executed_at_unix"]) != int(t0_event["executed_at_unix"])
            or str(ethereum[0]["execution_transaction_hash"]).lower()
            != str(t0_event["execution_transaction_hash"]).lower()
        ):
            raise RuntimeError(f"proposal {proposal_id} Ethereum payload differs from T0")
        t0_after = {str(asset["symbol"]): int(asset["slope1_after_bps"]) for asset in t0_event["assets"]}
        ethereum_after = {
            str(update["canonical_symbol"]): int(update["variable_rate_slope1_bps"])
            for update in ethereum[0]["comparable_stablecoin_updates"]
            if str(update["canonical_symbol"]) in t0_after
        }
        if ethereum_after != t0_after:
            raise RuntimeError(
                f"proposal {proposal_id} Ethereum source does not reproduce T0: "
                f"{ethereum_after} != {t0_after}"
            )

        comparable = [row for row in chain_results if row["source_audited_comparable"]]
        non_ethereum_comparable = [row for row in comparable if int(row["chain_id"]) != 1]
        comparable_times = [int(row["executed_at_unix"]) for row in comparable]
        stagger_hours = (
            (max(comparable_times) - min(comparable_times)) / 3600 if len(comparable_times) >= 2 else 0.0
        )
        gate = config["cross_chain_gate"]
        checks = {
            "minimum_executed_v3_payload_chains": len(chain_results)
            >= int(gate["minimum_executed_v3_payload_chains_per_qualifying_proposal"]),
            "minimum_non_ethereum_comparator_chains": len(non_ethereum_comparable)
            >= int(gate["minimum_non_ethereum_comparator_chains_per_qualifying_proposal"]),
            "has_source_audited_slope1_only_stablecoin_comparator": bool(comparable),
            "minimum_execution_stagger_hours": stagger_hours
            >= float(gate["minimum_execution_stagger_hours"]),
        }
        proposal_results.append(
            {
                "proposal_id": proposal_id,
                "cohort": str(proposal["cohort"]),
                "implementation_commit": str(t0_event["implementation_commit"]),
                "implementation_directory": str(t0_event["implementation_directory"]),
                "executed_v3_payload_chain_count": len(chain_results),
                "source_audited_comparable_chain_count": len(comparable),
                "non_ethereum_comparable_chain_count": len(non_ethereum_comparable),
                "earliest_comparable_execution_timestamp": min(comparable_times),
                "latest_comparable_execution_timestamp": max(comparable_times),
                "execution_stagger_hours": round(stagger_hours, 6),
                "decision_checks": checks,
                "qualifies": all(checks.values()),
                "chains": sorted(chain_results, key=lambda row: int(row["chain_id"])),
            }
        )
    qualifying_count = sum(bool(row["qualifies"]) for row in proposal_results)
    required = int(config["cross_chain_gate"]["minimum_qualifying_proposals"])
    return {
        "proposals": proposal_results,
        "qualifying_proposal_count": qualifying_count,
        "minimum_qualifying_proposals": required,
        "passed": qualifying_count >= required,
    }


def _build_event_topics(
    config: Mapping[str, Any],
    source_definitions: Mapping[str, Mapping[str, dict[str, Any]]],
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    global_pool_names = {
        "EModeCategoryAdded",
        "EModeCategoryIsolationChanged",
        "BridgeProtocolFeeUpdated",
        "FlashloanPremiumTotalUpdated",
        "FlashloanPremiumToProtocolUpdated",
    }
    topic_definitions: dict[str, dict[str, Any]] = {}
    signatures_by_group = config["ethereum_material_event_signatures"]
    group_keys = {
        "legacy_pool_configurator": "pool_configurator",
        "current_pool_configurator_additions": "pool_configurator",
        "oracle": "oracle",
        "addresses_provider": "addresses_provider",
        "rewards": "rewards",
    }
    for config_group, contract_group in group_keys.items():
        available = source_definitions[config_group]
        requested = [str(value) for value in signatures_by_group[config_group]]
        missing = sorted(set(requested) - set(available))
        if missing:
            raise RuntimeError(f"{config_group} frozen ABI signatures missing from source: {missing}")
        for signature in requested:
            definition = available[signature]
            name = str(definition["name"])
            topic = _keccak_topic(signature)
            if re.fullmatch(r"0x[0-9a-f]{64}", topic) is None:
                raise RuntimeError(f"web3_sha3 returned malformed topic for {signature}")
            if contract_group == "pool_configurator":
                if name == "BorrowableInIsolationChanged":
                    scope_rule = "asset_data_word_zero"
                elif name in global_pool_names:
                    scope_rule = "global"
                else:
                    scope_rule = "asset_topic"
            elif contract_group == "oracle":
                scope_rule = "global" if name == "FallbackOracleUpdated" else "asset_topic"
            elif contract_group == "addresses_provider":
                scope_rule = "global"
            else:
                scope_rule = "reward_asset_topic"
            record = {
                "signature": signature,
                "name": name,
                "contract_group": contract_group,
                "scope_rule": scope_rule,
            }
            previous = topic_definitions.get(topic)
            if previous is not None and previous != record:
                raise RuntimeError(f"event topic collision at {topic}")
            topic_definitions[topic] = record
    return sorted(topic_definitions), topic_definitions


def _load_source_definitions(
    config: Mapping[str, Any],
    historical_core_root: Path,
    origin_root: Path,
) -> tuple[dict[str, dict[str, dict[str, Any]]], dict[str, str]]:
    sources = config["official_sources"]
    paths = {
        "legacy_pool_configurator": historical_core_root / str(sources["historical_v3_core"]["abi_path"]),
        "current_pool_configurator_additions": origin_root
        / str(sources["current_v3_origin"]["configurator_abi_path"]),
        "oracle": origin_root / str(sources["current_v3_origin"]["oracle_abi_path"]),
        "addresses_provider": origin_root / str(sources["current_v3_origin"]["addresses_provider_abi_path"]),
        "rewards": origin_root / str(sources["current_v3_origin"]["rewards_abi_path"]),
    }
    definitions: dict[str, dict[str, dict[str, Any]]] = {}
    digests: dict[str, str] = {}
    for label, path in paths.items():
        source = path.read_text(encoding="utf-8")
        definitions[label] = extract_solidity_event_definitions(source)
        digests[label] = hashlib.sha256(source.encode()).hexdigest()
    return definitions, digests


def _audit_address_book(config: Mapping[str, Any], address_book_root: Path) -> str:
    path = address_book_root / str(config["official_sources"]["address_book"]["ethereum_path"])
    source = path.read_text(encoding="utf-8").lower()
    expected = [
        str(config["ethereum"][key])
        for key in (
            "pool",
            "pool_configurator",
            "pool_addresses_provider",
            "oracle",
            "rewards_controller",
        )
    ]
    for asset in config["ethereum"]["assets"].values():
        expected.extend([str(asset["underlying"]), str(asset["a_token"]), str(asset["variable_debt_token"])])
    missing = [address for address in expected if address.lower() not in source]
    if missing:
        raise RuntimeError(f"frozen Ethereum addresses absent from official address book: {missing}")
    return hashlib.sha256(source.encode()).hexdigest()


def audit(
    config_path: Path,
    t0_path: Path,
    d1a_path: Path,
    governance_root: Path,
    proposals_root: Path,
    historical_core_root: Path,
    origin_root: Path,
    address_book_root: Path,
    output_path: Path,
    checkpoint_path: Path,
) -> dict[str, Any]:
    """Execute D1B without reading behavioral outcomes."""
    if _git("status", "--porcelain"):
        raise RuntimeError("formal Aave D1B requires a clean EcoPhys worktree")
    if checkpoint_path.is_relative_to(REPO_ROOT):
        raise RuntimeError("formal D1B checkpoint must remain outside the repository")
    config = _load_yaml(config_path)
    t0 = _load_json(t0_path)
    d1a = _load_json(d1a_path)
    expected_d1a_digest = str(config["contract"]["parent_d1a_manifest_sha256"])
    _verify_digest(d1a, expected_d1a_digest, label="parent D1A")
    if d1a.get("decision") != "pass_to_separately_frozen_intervention_ledger_gate":
        raise RuntimeError("parent D1A did not authorize D1B")
    parent_commit = _git("rev-parse", f"{config['contract']['parent_d1a_artifact_commit']}^{{commit}}")
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", parent_commit, "HEAD"],
        cwd=REPO_ROOT,
        check=False,
    )
    if ancestry.returncode != 0:
        raise RuntimeError("parent D1A artifact commit is not an ancestor of D1B")

    official = config["official_sources"]
    source_repositories = {
        "governance_cache": _verify_repo(
            governance_root,
            str(official["governance_cache"]["expected_git_sha"]),
            label="governance cache",
        ),
        "proposals_repository": _verify_repo(
            proposals_root,
            str(official["proposals_repository"]["expected_git_sha"]),
            label="proposals repository",
        ),
        "historical_v3_core": _verify_repo(
            historical_core_root,
            str(official["historical_v3_core"]["expected_git_sha"]),
            label="historical V3 Core",
        ),
        "current_v3_origin": _verify_repo(
            origin_root,
            str(official["current_v3_origin"]["expected_git_sha"]),
            label="current V3 Origin",
        ),
        "address_book": _verify_repo(
            address_book_root,
            str(official["address_book"]["expected_git_sha"]),
            label="Aave address book",
        ),
    }
    source_definitions, abi_digests = _load_source_definitions(config, historical_core_root, origin_root)
    address_book_digest = _audit_address_book(config, address_book_root)

    governance_records = _load_json(
        governance_root / "cache" / "1" / "proposals" / f"{GOVERNANCE_CONTRACT}.json"
    )
    forum_retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        allowed_methods=frozenset({"GET"}),
        status_forcelist=(429, 500, 502, 503, 504),
        backoff_factor=1.0,
    )
    forum_session = requests.Session()
    forum_session.mount("https://", HTTPAdapter(max_retries=forum_retry))
    forum_session.headers.update({"User-Agent": "EcoPhys-Aave-D1B-audit/1.0"})

    cross_chain = _audit_cross_chain(config, t0, governance_root, proposals_root)
    t0_by_proposal = {int(event["proposal_id"]): event for event in t0["events"]}
    timelines: list[dict[str, Any]] = []
    for proposal in config["proposals"]:
        proposal_id = int(proposal["id"])
        forum = _forum_timeline(
            forum_session,
            base_url=str(config["transport"]["forum_base_url"]),
            topic_id=int(proposal["forum_topic_id"]),
        )
        governance = governance_records.get(str(proposal_id))
        if not isinstance(governance, Mapping) or int(governance.get("state", -1)) != 4:
            raise RuntimeError(f"proposal {proposal_id} is not resolved as executed")
        execution_timestamp = int(t0_by_proposal[proposal_id]["executed_at_unix"])
        announcement_timestamp = min(int(forum["first_post_timestamp"]), int(governance["creationTime"]))
        lead_hours = (execution_timestamp - announcement_timestamp) / 3600
        timelines.append(
            {
                "proposal_id": proposal_id,
                "cohort": str(proposal["cohort"]),
                "forum": forum,
                "governance": {
                    "creation_timestamp": int(governance["creationTime"]),
                    "creation_utc": _utc(int(governance["creationTime"])),
                    "voting_activation_timestamp": int(governance["votingActivationTime"]),
                    "voting_activation_utc": _utc(int(governance["votingActivationTime"])),
                    "queuing_timestamp": int(governance["queuingTime"]),
                    "queuing_utc": _utc(int(governance["queuingTime"])),
                    "voting_duration_seconds": int(governance["votingDuration"]),
                    "state": int(governance["state"]),
                },
                "ethereum_execution_timestamp": execution_timestamp,
                "ethereum_execution_utc": _utc(execution_timestamp),
                "public_announcement_timestamp": announcement_timestamp,
                "public_announcement_utc": _utc(announcement_timestamp),
                "announcement_to_execution_lead_hours": round(lead_hours, 6),
                "anticipated_by_frozen_24h_rule": lead_hours
                >= float(config["announcement_rule"]["lead_of_at_least_hours_is_anticipated"]),
            }
        )

    limits = config["limits"]
    transport = config["transport"]
    formal_rpc = str(transport["formal_rpc_after_primary_rate_limit_failure"])
    client = _RpcClient(
        url=formal_rpc,
        timeout=int(limits["request_timeout_seconds"]),
        transport_retries=int(limits["transport_retries"]),
        minimum_request_interval_seconds=float(transport["minimum_request_interval_seconds"]),
        rate_limit_retries=int(transport["rate_limit_retries"]),
        rate_limit_backoff_initial_seconds=float(transport["rate_limit_backoff_initial_seconds"]),
        rate_limit_backoff_max_seconds=float(transport["rate_limit_backoff_max_seconds"]),
    )
    if client.call("eth_chainId", []) != "0x1":
        raise RuntimeError("primary D1B RPC is not Ethereum mainnet")
    if _keccak_topic("Transfer(address,address,uint256)") != (
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    ):
        raise RuntimeError("local Keccak-256 implementation failed the frozen ERC-20 vector")
    event_topics, topic_definitions = _build_event_topics(config, source_definitions)

    for event in t0["events"]:
        header = client.block(int(event["execution_block"]))
        if (
            int(header["timestamp"]) != int(event["executed_at_unix"])
            or str(header["hash"]) != str(event["execution_block_hash"]).lower()
        ):
            raise RuntimeError(f"proposal {event['proposal_id']} execution header differs from T0")

    support = config["ledger_window"]
    support_pre_seconds = int(timedelta(days=int(support["support_pre_execution_days"])).total_seconds())
    support_post_seconds = int(timedelta(days=int(support["support_post_execution_days"])).total_seconds())
    latest_t0_block = max(int(event["execution_block"]) for event in t0["events"])
    repository_sha = _git("rev-parse", "HEAD")
    config_sha256 = hashlib.sha256(config_path.read_bytes()).hexdigest()
    checkpoint_identity = {
        "repository_sha": repository_sha,
        "config_sha256": config_sha256,
        "parent_t0_sha256": str(t0["canonical_payload_sha256"]),
        "parent_d1a_sha256": expected_d1a_digest,
        "formal_rpc": formal_rpc,
    }
    checkpoint = _load_policy_checkpoint(checkpoint_path, identity=checkpoint_identity)
    resumed_from_checkpoint = checkpoint is not None
    resumed_completed_interval_count = 0
    if checkpoint is None:
        support_windows: list[dict[str, Any]] = []
        intervals: list[tuple[int, int]] = []
        for event in t0["events"]:
            execution_timestamp = int(event["executed_at_unix"])
            start_timestamp = execution_timestamp - support_pre_seconds
            end_timestamp = execution_timestamp + support_post_seconds
            start_block = _first_block_at_or_after(
                client,
                target_timestamp=start_timestamp,
                upper_block=int(event["execution_block"]),
            )
            end_block = _first_block_at_or_after(
                client,
                target_timestamp=end_timestamp,
                upper_block=latest_t0_block + 900_000,
            )
            intervals.append((start_block, end_block))
            support_windows.append(
                {
                    "proposal_id": int(event["proposal_id"]),
                    "start_timestamp": start_timestamp,
                    "start_utc": _utc(start_timestamp),
                    "start_block": start_block,
                    "end_timestamp": end_timestamp,
                    "end_utc": _utc(end_timestamp),
                    "end_block_inclusive_for_boundary_safety": end_block,
                }
            )
        merged_intervals = _merge_block_intervals(intervals)
        completed_interval_count = 0
        policy_events: list[dict[str, Any]] = []
        _write_policy_checkpoint(
            checkpoint_path,
            identity=checkpoint_identity,
            support_windows=support_windows,
            merged_intervals=merged_intervals,
            completed_interval_count=completed_interval_count,
            policy_events=policy_events,
        )
    else:
        (
            support_windows,
            merged_intervals,
            completed_interval_count,
            policy_events,
        ) = checkpoint
        resumed_completed_interval_count = completed_interval_count
    ethereum = config["ethereum"]
    contract_addresses = {
        "pool_configurator": str(ethereum["pool_configurator"]),
        "addresses_provider": str(ethereum["pool_addresses_provider"]),
        "oracle": str(ethereum["oracle"]),
        "rewards": str(ethereum["rewards_controller"]),
    }
    for interval_index, (merged_start, merged_end) in enumerate(
        merged_intervals[completed_interval_count:], start=completed_interval_count
    ):
        raw_logs: list[Mapping[str, Any]] = []
        for chunk_start in range(merged_start, merged_end + 1, int(limits["block_chunk_size"])):
            chunk_end = min(merged_end, chunk_start + int(limits["block_chunk_size"]) - 1)
            raw_logs.extend(
                _get_logs_with_split(
                    client,
                    addresses=list(contract_addresses.values()),
                    topics=event_topics,
                    start_block=chunk_start,
                    end_block_inclusive=chunk_end,
                    remaining_split_depth=int(limits["maximum_log_range_split_depth"]),
                )
            )
        policy_blocks = sorted(
            {_hex_quantity(log.get("blockNumber"), field="blockNumber") for log in raw_logs}
        )
        block_timestamps = {block: int(client.block(block)["timestamp"]) for block in policy_blocks}
        assets = {str(symbol): str(record["underlying"]) for symbol, record in ethereum["assets"].items()}
        selected_tokens = {
            str(symbol): [str(record["a_token"]), str(record["variable_debt_token"])]
            for symbol, record in ethereum["assets"].items()
        }
        interval_events = reduce_policy_logs(
            raw_logs,
            contract_addresses=contract_addresses,
            topic_definitions=topic_definitions,
            selected_assets=assets,
            selected_tokens=selected_tokens,
            start_block=merged_start,
            end_block_inclusive=merged_end,
            block_timestamps=block_timestamps,
        )
        policy_events.extend(
            event
            for event in interval_events
            if any(
                int(window["start_timestamp"])
                <= int(event["block_timestamp"])
                <= int(window["end_timestamp"])
                for window in support_windows
            )
        )
        completed_interval_count = interval_index + 1
        _write_policy_checkpoint(
            checkpoint_path,
            identity=checkpoint_identity,
            support_windows=support_windows,
            merged_intervals=merged_intervals,
            completed_interval_count=completed_interval_count,
            policy_events=policy_events,
        )

    cohort_by_proposal = {int(proposal["id"]): str(proposal["cohort"]) for proposal in config["proposals"]}
    units = [
        {
            "proposal_id": int(event["proposal_id"]),
            "symbol": str(asset["symbol"]),
            "cohort": cohort_by_proposal[int(event["proposal_id"])],
            "execution_block": int(event["execution_block"]),
            "execution_timestamp": int(event["executed_at_unix"]),
            "execution_transaction_hash": str(event["execution_transaction_hash"]),
        }
        for event in t0["events"]
        for asset in event["assets"]
    ]
    clean_units = classify_clean_policy_windows(
        policy_events,
        units,
        exclusion_pre_seconds=int(
            timedelta(days=int(support["exclusion_pre_execution_days"])).total_seconds()
        ),
        minimum_clean_post_seconds=int(
            timedelta(days=int(support["minimum_clean_post_execution_days"])).total_seconds()
        ),
        target_post_seconds=support_post_seconds,
    )
    panel_gate = assess_clean_panel(
        clean_units,
        minimum_total=int(config["ethereum_panel_gate"]["minimum_total_clean_units"]),
        minimum_primary=int(config["ethereum_panel_gate"]["minimum_primary_clean_units"]),
        minimum_reverse=int(config["ethereum_panel_gate"]["minimum_reverse_sign_clean_units"]),
        minimum_assets_per_proposal=int(config["ethereum_panel_gate"]["minimum_clean_assets_per_proposal"]),
    )
    timeline_resolved = len(timelines) == len(config["proposals"])
    selected_targets_match = all(bool(unit["target_matches_exactly_once"]) for unit in clean_units)
    decision_checks = {
        "six_of_six_announcement_and_governance_timelines_resolved": timeline_resolved,
        "selected_ethereum_rate_events_match_exact_t0_blocks_and_transactions": selected_targets_match,
        "ethereum_panel_gate_passes_with_at_least_14_clean_post_days": bool(panel_gate["passed"]),
        "cross_chain_gate_passes_for_at_least_four_proposals": bool(cross_chain["passed"]),
    }
    passed = all(decision_checks.values())
    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "formal_aave_rate_response_d1b_identification_complete",
        "decision": (
            "pass_to_separately_frozen_cross_chain_preperiod_activity_d1c"
            if passed
            else "stop_ncs_causal_route_before_behavioral_outcomes"
        ),
        "repository": {
            "branch": _git("branch", "--show-current"),
            "git_sha": repository_sha,
        },
        "contract": {
            "config_sha256": config_sha256,
            "parent_d1a_artifact_commit": parent_commit,
            "parent_d1a_canonical_payload_sha256": expected_d1a_digest,
            "parent_d1a_digest_recomputed": True,
        },
        "official_source_verification": {
            "repositories": source_repositories,
            "abi_source_sha256": abi_digests,
            "address_book_source_sha256": address_book_digest,
            "event_topic_hash_method": "openssl_keccak_256",
            "event_topic_hash_known_vector_verified": True,
            "all_frozen_event_signatures_found_in_pinned_abis": True,
            "all_frozen_addresses_found_in_pinned_address_book": True,
        },
        "announcement_and_governance_timelines": timelines,
        "all_executions_classified_as_anticipated": all(
            bool(row["anticipated_by_frozen_24h_rule"]) for row in timelines
        ),
        "execution_as_unanticipated_shock_claim_allowed": False,
        "cross_chain_gate": cross_chain,
        "ethereum_policy_ledger": {
            "formal_rpc": formal_rpc,
            "support_windows": support_windows,
            "merged_query_block_intervals": [
                {"start_block": start, "end_block_inclusive": end} for start, end in merged_intervals
            ],
            "event_topic_count": len(event_topics),
            "sanitized_policy_event_count": len(policy_events),
            "events": policy_events,
            "raw_rpc_responses_persisted": False,
            "participant_addresses_or_behavioral_values_retained": False,
            "rpc_request_counts": dict(sorted(client.method_counts.items())),
            "log_range_splits": client.log_range_splits,
            "rate_limit_retry_count": client.rate_limit_retry_count,
            "rate_limit_wait_seconds": round(client.rate_limit_wait_seconds, 3),
        },
        "checkpoint": {
            "resumed_from_sanitized_checkpoint": resumed_from_checkpoint,
            "resumed_completed_interval_count": resumed_completed_interval_count,
            "completed_interval_count": completed_interval_count,
            "checkpoint_outside_repository": not checkpoint_path.is_relative_to(REPO_ROOT),
            "checkpoint_contains_only_boundary_and_sanitized_policy_metadata": True,
            "checkpoint_removed_after_success": True,
        },
        "clean_units": clean_units,
        "ethereum_panel_gate": panel_gate,
        "decision_checks": decision_checks,
        "blinding": {
            "post_execution_borrow_or_repay_queried": False,
            "reserve_data_updated_outcomes_queried": False,
            "positions_balances_utilization_realized_rates_prices_or_volumes_queried": False,
            "behavioral_participant_addresses_retained": False,
            "policy_transaction_hashes_retained_for_provenance": True,
        },
        "compute": {
            "cpu_only": True,
            "gpu_used": False,
            "paid_data_used": False,
            "ecomd_used": False,
        },
    }
    result["canonical_payload_sha256"] = canonical_sha256(result)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(output_path)
    checkpoint_path.unlink(missing_ok=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--t0-result", type=Path, required=True)
    parser.add_argument("--d1a-result", type=Path, required=True)
    parser.add_argument("--governance-cache-root", type=Path, required=True)
    parser.add_argument("--proposals-root", type=Path, required=True)
    parser.add_argument("--historical-core-root", type=Path, required=True)
    parser.add_argument("--origin-root", type=Path, required=True)
    parser.add_argument("--address-book-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()
    result = audit(
        args.config.resolve(),
        args.t0_result.resolve(),
        args.d1a_result.resolve(),
        args.governance_cache_root.resolve(),
        args.proposals_root.resolve(),
        args.historical_core_root.resolve(),
        args.origin_root.resolve(),
        args.address_book_root.resolve(),
        args.output.resolve(),
        args.checkpoint.resolve(),
    )
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "clean_units": result["ethereum_panel_gate"]["eligible_unit_count"],
                "cross_chain_qualifying_proposals": result["cross_chain_gate"]["qualifying_proposal_count"],
                "manifest": str(args.output.resolve()),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
