"""Run the frozen pre-period-only Aave D1A activity screen."""

from __future__ import annotations

import argparse
import json
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
    address_topic,
    canonical_sha256,
    normalize_address,
    summarize_preperiod_activity,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


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
        if minimum_request_interval_seconds < 0:
            raise ValueError("minimum request interval cannot be negative")
        if rate_limit_retries < 0:
            raise ValueError("rate-limit retries cannot be negative")
        if rate_limit_backoff_initial_seconds <= 0 or rate_limit_backoff_max_seconds <= 0:
            raise ValueError("rate-limit backoff values must be positive")
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
        self.session.headers.update({"User-Agent": "EcoPhys-Aave-D1A-screen/1.0"})
        self.url = url
        self.timeout = timeout
        self.minimum_request_interval_seconds = minimum_request_interval_seconds
        self.rate_limit_retries = rate_limit_retries
        self.rate_limit_backoff_initial_seconds = rate_limit_backoff_initial_seconds
        self.rate_limit_backoff_max_seconds = rate_limit_backoff_max_seconds
        self.next_request_id = 1
        self.method_counts: Counter[str] = Counter()
        self.log_range_splits = 0
        self.rate_limit_retry_count = 0
        self.rate_limit_wait_seconds = 0.0
        self._last_request_started: float | None = None
        self._block_cache: dict[int, dict[str, Any]] = {}

    def call(self, method: str, params: list[Any]) -> Any:
        request_id = self.next_request_id
        self.next_request_id += 1
        payload: Any = None
        response: requests.Response | None = None
        for rate_limit_attempt in range(self.rate_limit_retries + 1):
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
            if response.status_code != 429 or rate_limit_attempt >= self.rate_limit_retries:
                break
            delay = _rate_limit_delay(
                attempt=rate_limit_attempt,
                initial_seconds=self.rate_limit_backoff_initial_seconds,
                maximum_seconds=self.rate_limit_backoff_max_seconds,
                retry_after=response.headers.get("Retry-After"),
            )
            self.rate_limit_retry_count += 1
            self.rate_limit_wait_seconds += delay
            time.sleep(delay)
        if response is None:
            raise AssertionError("RPC loop completed without an HTTP response")
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
            raise RpcError(
                f"RPC {method} failed: {remote_error}",
                rpc_code=rpc_code,
            )
        if "result" not in payload:
            raise RpcError(f"RPC {method} returned no result")
        return payload["result"]

    def _pace(self) -> None:
        now = time.monotonic()
        if self._last_request_started is not None:
            remaining = self.minimum_request_interval_seconds - (
                now - self._last_request_started
            )
            if remaining > 0:
                time.sleep(remaining)
        self._last_request_started = time.monotonic()

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
            "number": observed_number,
            "timestamp": _hex_quantity(result.get("timestamp"), field="block timestamp"),
            "hash": _hash(str(result.get("hash")), field="block hash"),
        }
        self._block_cache[number] = header
        return header


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("D1A config must be a mapping")
    return payload


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON artifact must be an object: {path}")
    return payload


def _hex_quantity(value: Any, *, field: str) -> int:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise RpcError(f"invalid {field}: {value}")
    try:
        return int(value, 16)
    except ValueError as error:
        raise RpcError(f"invalid {field}: {value}") from error


def _hash(value: str, *, field: str) -> str:
    normalized = value.lower()
    if len(normalized) != 66 or not normalized.startswith("0x"):
        raise RpcError(f"invalid {field}: {value}")
    try:
        int(normalized[2:], 16)
    except ValueError as error:
        raise RpcError(f"invalid {field}: {value}") from error
    return normalized


def _utc(unix_seconds: int) -> str:
    return datetime.fromtimestamp(unix_seconds, UTC).isoformat()


def _rate_limit_delay(
    *,
    attempt: int,
    initial_seconds: float,
    maximum_seconds: float,
    retry_after: str | None,
) -> float:
    if attempt < 0 or initial_seconds <= 0 or maximum_seconds <= 0:
        raise ValueError("rate-limit backoff parameters must be positive")
    header_delay = 0.0
    if retry_after is not None:
        try:
            header_delay = max(0.0, float(retry_after))
        except ValueError:
            header_delay = 0.0
    exponential = initial_seconds * float(2**attempt)
    return float(min(max(exponential, header_delay), maximum_seconds))


def _verify_parent_t0(config: Mapping[str, Any], t0: Mapping[str, Any]) -> None:
    expected_digest = str(config["contract"]["parent_t0_manifest_sha256"])
    stored_digest = str(t0.get("canonical_payload_sha256"))
    digest_payload = {key: value for key, value in t0.items() if key != "canonical_payload_sha256"}
    recomputed_digest = canonical_sha256(digest_payload)
    if stored_digest != expected_digest or recomputed_digest != expected_digest:
        raise RuntimeError(
            "parent T0 digest mismatch: "
            f"stored={stored_digest}, recomputed={recomputed_digest}, expected={expected_digest}"
        )
    if t0.get("decision") != "pass_to_separately_committed_preperiod_activity_freeze":
        raise RuntimeError("parent T0 did not authorize D1A")


def _first_block_at_or_after(
    client: _RpcClient,
    *,
    target_timestamp: int,
    upper_block: int,
    search_back_blocks: int,
) -> int:
    if client.block(upper_block)["timestamp"] < target_timestamp:
        raise RuntimeError("boundary target occurs after the supplied upper block")
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


def _get_logs_with_split(
    client: _RpcClient,
    *,
    pool_address: str,
    topic0: Sequence[str],
    topic1: Sequence[str],
    start_block: int,
    end_block_inclusive: int,
    remaining_split_depth: int,
) -> list[Mapping[str, Any]]:
    query = {
        "address": pool_address,
        "fromBlock": hex(start_block),
        "toBlock": hex(end_block_inclusive),
        "topics": [list(topic0), list(topic1)],
    }
    try:
        payload = client.call("eth_getLogs", [query])
    except RpcError as error:
        if (
            not _is_splittable_log_error(error)
            or start_block >= end_block_inclusive
            or remaining_split_depth <= 0
        ):
            raise
        client.log_range_splits += 1
        middle = (start_block + end_block_inclusive) // 2
        return _get_logs_with_split(
            client,
            pool_address=pool_address,
            topic0=topic0,
            topic1=topic1,
            start_block=start_block,
            end_block_inclusive=middle,
            remaining_split_depth=remaining_split_depth - 1,
        ) + _get_logs_with_split(
            client,
            pool_address=pool_address,
            topic0=topic0,
            topic1=topic1,
            start_block=middle + 1,
            end_block_inclusive=end_block_inclusive,
            remaining_split_depth=remaining_split_depth - 1,
        )
    if not isinstance(payload, list) or any(not isinstance(row, Mapping) for row in payload):
        raise RpcError("eth_getLogs returned a malformed result")
    return payload


def _is_splittable_log_error(error: RpcError) -> bool:
    if error.http_status == 413:
        return True
    message = str(error).lower()
    range_markers = (
        "block range",
        "range is too wide",
        "range limit",
        "response size",
        "result size",
        "too many results",
        "query returned more than",
        "log response size exceeded",
    )
    return any(marker in message for marker in range_markers)


def _get_window_logs(
    client: _RpcClient,
    *,
    pool_address: str,
    topic0: Sequence[str],
    topic1: Sequence[str],
    start_block: int,
    end_block_exclusive: int,
    block_chunk_size: int,
    maximum_split_depth: int,
) -> list[Mapping[str, Any]]:
    logs: list[Mapping[str, Any]] = []
    for chunk_start in range(start_block, end_block_exclusive, block_chunk_size):
        chunk_end = min(end_block_exclusive - 1, chunk_start + block_chunk_size - 1)
        logs.extend(
            _get_logs_with_split(
                client,
                pool_address=pool_address,
                topic0=topic0,
                topic1=topic1,
                start_block=chunk_start,
                end_block_inclusive=chunk_end,
                remaining_split_depth=maximum_split_depth,
            )
        )
    return logs


def screen(config_path: Path, t0_path: Path, output_path: Path) -> dict[str, Any]:
    """Run D1A and persist only frozen pre-period activity aggregates."""
    if _git("status", "--porcelain"):
        raise RuntimeError("formal Aave D1A requires a clean worktree")
    config = _load_yaml(config_path)
    t0 = _load_json(t0_path)
    _verify_parent_t0(config, t0)
    parent_artifact_commit = str(config["contract"]["parent_t0_artifact_commit"])
    resolved_parent = _git("rev-parse", f"{parent_artifact_commit}^{{commit}}")
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", resolved_parent, "HEAD"],
        cwd=REPO_ROOT,
        check=False,
    )
    if ancestry.returncode != 0:
        raise RuntimeError("parent T0 artifact commit is not an ancestor of the D1A run")

    source = config["source"]
    market = config["market"]
    activity_rule = config["activity_rule"]
    selection = config["selection"]
    limits = config["limits"]
    if int(t0["market"]["chain_id"]) != int(market["chain_id"]):
        raise RuntimeError("D1A chain differs from parent T0")
    if normalize_address(str(t0["market"]["pool"])) != normalize_address(str(market["pool"])):
        raise RuntimeError("D1A pool differs from parent T0")
    t0_assets = {
        str(symbol): normalize_address(str(address))
        for symbol, address in t0["market"]["assets"].items()
    }
    assets = {
        str(symbol): normalize_address(str(address))
        for symbol, address in market["assets"].items()
    }
    if t0_assets != assets:
        raise RuntimeError("D1A assets differ from parent T0")

    t0_topics = t0["public_rpc_metadata"]["event_topics"]
    borrow_topic = str(source["borrow_topic"]).lower()
    repay_topic = str(source["repay_topic"]).lower()
    if borrow_topic != str(t0_topics["borrow_topic"]).lower():
        raise RuntimeError("D1A Borrow topic differs from parent T0")
    if repay_topic != str(t0_topics["repay_topic"]).lower():
        raise RuntimeError("D1A Repay topic differs from parent T0")

    primary_ids = {int(value) for value in selection["primary_rate_decrease_proposals"]}
    reverse_ids = {int(value) for value in selection["reverse_sign_probe_proposals"]}
    if primary_ids & reverse_ids:
        raise RuntimeError("primary and reverse-sign proposal sets overlap")
    included_ids = primary_ids | reverse_ids
    event_lookup = {int(event["proposal_id"]): event for event in t0["events"]}
    if included_ids != set(event_lookup):
        raise RuntimeError("D1A proposal set differs from parent T0")
    expected_counts = (
        len(primary_ids) * len(assets),
        len(reverse_ids) * len(assets),
        len(included_ids) * len(assets),
    )
    frozen_counts = (
        int(selection["expected_primary_units"]),
        int(selection["expected_reverse_sign_units"]),
        int(selection["expected_total_units"]),
    )
    if expected_counts != frozen_counts:
        raise RuntimeError(
            f"D1A unit arithmetic differs from freeze: {expected_counts} != {frozen_counts}"
        )

    client = _RpcClient(
        url=str(source["rpc_url"]),
        timeout=int(limits["request_timeout_seconds"]),
        transport_retries=int(limits["transport_retries"]),
        minimum_request_interval_seconds=float(limits["minimum_request_interval_seconds"]),
        rate_limit_retries=int(limits["rate_limit_retries"]),
        rate_limit_backoff_initial_seconds=float(
            limits["rate_limit_backoff_initial_seconds"]
        ),
        rate_limit_backoff_max_seconds=float(limits["rate_limit_backoff_max_seconds"]),
    )
    chain_id = client.call("eth_chainId", [])
    if chain_id != str(source["expected_chain_id_hex"]):
        raise RuntimeError(f"unexpected RPC chain ID: {chain_id}")

    preperiod_days = int(activity_rule["preperiod_days"])
    weekly_bin_days = int(activity_rule["weekly_bin_days"])
    if preperiod_days <= 0 or weekly_bin_days <= 0 or preperiod_days % weekly_bin_days != 0:
        raise RuntimeError("preperiod must divide into positive, complete weekly bins")
    week_count = preperiod_days // weekly_bin_days
    event_results: list[dict[str, Any]] = []
    pool_address = normalize_address(str(market["pool"]))
    asset_topic_values = [address_topic(address) for address in assets.values()]

    for proposal_id in sorted(included_ids):
        event = event_lookup[proposal_id]
        execution_block = int(event["execution_block"])
        execution_timestamp = int(event["executed_at_unix"])
        execution_header = client.block(execution_block)
        if (
            execution_header["timestamp"] != execution_timestamp
            or execution_header["hash"] != str(event["execution_block_hash"]).lower()
        ):
            raise RuntimeError(f"proposal {proposal_id} execution header differs from T0")

        boundary_targets = [
            execution_timestamp
            - int(timedelta(days=preperiod_days - index * weekly_bin_days).total_seconds())
            for index in range(week_count)
        ]
        boundary_blocks = [
            _first_block_at_or_after(
                client,
                target_timestamp=target,
                upper_block=execution_block,
                search_back_blocks=int(limits["boundary_search_back_blocks"]),
            )
            for target in boundary_targets
        ] + [execution_block]
        if boundary_blocks != sorted(set(boundary_blocks)):
            raise RuntimeError(f"proposal {proposal_id} has invalid time-to-block boundaries")

        windows: list[dict[str, Any]] = []
        boundaries: list[dict[str, Any]] = []
        for index, target in enumerate(boundary_targets):
            block = boundary_blocks[index]
            header = client.block(block)
            previous_timestamp = client.block(block - 1)["timestamp"] if block > 0 else None
            if header["timestamp"] < target or (
                previous_timestamp is not None and previous_timestamp >= target
            ):
                raise RuntimeError(f"proposal {proposal_id} boundary search invariant failed")
            boundaries.append(
                {
                    "boundary_index": index,
                    "target_timestamp": target,
                    "target_utc": _utc(target),
                    "first_block_at_or_after": block,
                    "first_block_timestamp": int(header["timestamp"]),
                    "first_block_utc": _utc(int(header["timestamp"])),
                }
            )
            end_block_exclusive = boundary_blocks[index + 1]
            logs = _get_window_logs(
                client,
                pool_address=pool_address,
                topic0=[borrow_topic, repay_topic],
                topic1=asset_topic_values,
                start_block=block,
                end_block_exclusive=end_block_exclusive,
                block_chunk_size=int(limits["block_chunk_size"]),
                maximum_split_depth=int(limits["maximum_log_range_split_depth"]),
            )
            windows.append(
                {
                    "start_block": block,
                    "end_block_exclusive": end_block_exclusive,
                    "logs": logs,
                }
            )

        summaries = summarize_preperiod_activity(
            windows,
            pool_address=pool_address,
            assets=assets,
            borrow_topic=borrow_topic,
            repay_topic=repay_topic,
            minimum_weekly_borrow_events=int(activity_rule["minimum_weekly_borrow_events"]),
            minimum_weekly_repay_events=int(activity_rule["minimum_weekly_repay_events"]),
            minimum_weekly_unique_debt_users=int(
                activity_rule["minimum_weekly_unique_debt_users"]
            ),
            minimum_total_actions=int(activity_rule["minimum_total_combined_actions"]),
            minimum_total_unique_debt_users=int(
                activity_rule["minimum_total_unique_debt_users"]
            ),
        )
        event_results.append(
            {
                "proposal_id": proposal_id,
                "cohort": "primary_rate_decrease" if proposal_id in primary_ids else "reverse_sign",
                "execution_block": execution_block,
                "execution_timestamp": execution_timestamp,
                "execution_utc": _utc(execution_timestamp),
                "execution_block_excluded_from_activity_query": True,
                "execution_header_matches_t0": True,
                "boundaries": boundaries,
                "assets": summaries,
            }
        )

    eligible_units = [
        {
            "proposal_id": int(event["proposal_id"]),
            "symbol": str(symbol),
            "cohort": str(event["cohort"]),
        }
        for event in event_results
        for symbol, summary in event["assets"].items()
        if bool(summary["activity_eligible"])
    ]
    ineligible_units = [
        {
            "proposal_id": int(event["proposal_id"]),
            "symbol": str(symbol),
            "cohort": str(event["cohort"]),
        }
        for event in event_results
        for symbol, summary in event["assets"].items()
        if not bool(summary["activity_eligible"])
    ]
    eligible_primary = sum(unit["proposal_id"] in primary_ids for unit in eligible_units)
    eligible_reverse = sum(unit["proposal_id"] in reverse_ids for unit in eligible_units)
    eligible_by_proposal = {
        str(proposal_id): sum(
            unit["proposal_id"] == proposal_id for unit in eligible_units
        )
        for proposal_id in sorted(included_ids)
    }
    decision_checks = {
        "minimum_total_units": len(eligible_units)
        >= int(config["decision"]["minimum_total_eligible_units"]),
        "minimum_primary_units": eligible_primary
        >= int(config["decision"]["minimum_primary_eligible_units"]),
        "minimum_reverse_sign_units": eligible_reverse
        >= int(config["decision"]["minimum_reverse_sign_eligible_units"]),
        "minimum_assets_per_proposal": all(
            count >= int(config["decision"]["minimum_eligible_assets_per_proposal"])
            for count in eligible_by_proposal.values()
        ),
    }
    passed = all(decision_checks.values())
    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "formal_aave_rate_response_d1a_activity_complete",
        "decision": (
            "pass_to_separately_frozen_intervention_ledger_gate"
            if passed
            else "stop_aave_singleton_panel_before_postevent_outcomes"
        ),
        "repository": {
            "branch": _git("branch", "--show-current"),
            "git_sha": _git("rev-parse", "HEAD"),
        },
        "parent_t0": {
            "artifact_commit": parent_artifact_commit,
            "artifact_commit_resolved": resolved_parent,
            "artifact_commit_is_ancestor": True,
            "formal_run_commit": str(t0["repository"]["git_sha"]),
            "canonical_payload_sha256": str(t0["canonical_payload_sha256"]),
            "digest_recomputed_before_d1a": True,
        },
        "source": {
            "rpc_url": str(source["rpc_url"]),
            "chain_id": chain_id,
            "pool": pool_address,
            "assets": assets,
            "event_topics": {"borrow": borrow_topic, "repay": repay_topic},
            "rpc_request_counts": dict(sorted(client.method_counts.items())),
            "log_range_splits": client.log_range_splits,
            "rate_limit_retry_count": client.rate_limit_retry_count,
            "rate_limit_wait_seconds": round(client.rate_limit_wait_seconds, 3),
            "raw_rpc_responses_persisted": False,
        },
        "activity_rule": activity_rule,
        "selection": selection,
        "events": event_results,
        "eligible_unit_count": len(eligible_units),
        "eligible_primary_unit_count": eligible_primary,
        "eligible_reverse_sign_unit_count": eligible_reverse,
        "eligible_units_by_proposal": eligible_by_proposal,
        "eligible_units": eligible_units,
        "ineligible_units": ineligible_units,
        "decision_checks": decision_checks,
        "blinding": {
            "preperiod_only": True,
            "execution_block_excluded": True,
            "postevent_logs_queried": False,
            "reserve_data_updated_logs_queried": False,
            "position_or_balance_calls_made": False,
            "retained_participant_addresses": False,
            "retained_amounts_rates_transaction_hashes_or_raw_logs": False,
            "retained_market_values": [
                "weekly_borrow_event_count",
                "weekly_repay_event_count",
                "weekly_unique_debt_user_count",
                "total_event_counts",
                "total_unique_debt_user_count",
            ],
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
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--t0-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = screen(
        args.config.resolve(),
        args.t0_result.resolve(),
        args.output.resolve(),
    )
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "eligible_unit_count": result["eligible_unit_count"],
                "eligible_primary_unit_count": result["eligible_primary_unit_count"],
                "eligible_reverse_sign_unit_count": result["eligible_reverse_sign_unit_count"],
                "manifest": str(args.output.resolve()),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
