"""Outcome-blind qualification helpers for Aave rate interventions."""

from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path
from typing import Any


def canonical_sha256(value: Any) -> str:
    """Return a deterministic SHA-256 digest for a JSON-compatible value."""
    normalized = json.loads(json.dumps(value, allow_nan=False))
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def normalize_address(value: str) -> str:
    """Normalize and validate an EVM address without applying a checksum transform."""
    normalized = value.lower()
    if re.fullmatch(r"0x[0-9a-f]{40}", normalized) is None:
        raise ValueError(f"invalid EVM address: {value}")
    return normalized


def address_topic(value: str) -> str:
    """Encode an indexed address as a 32-byte EVM log topic."""
    return "0x" + "0" * 24 + normalize_address(value)[2:]


def _percent_to_bps(value: str) -> int:
    match = re.fullmatch(r"(-?[0-9]+(?:\.[0-9]+)?)\s*%", value.strip())
    if match is None:
        raise ValueError(f"not a percentage: {value}")
    bps = Decimal(match.group(1)) * 100
    if bps != bps.to_integral_value():
        raise ValueError(f"percentage is not an integral number of basis points: {value}")
    return int(bps)


def _asset_section(markdown: str, symbol: str) -> str:
    pattern = re.compile(
        rf"^####\s+{re.escape(symbol)}\s+\([^\n]*\)\s*$\n(.*?)(?=^####\s+|^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise ValueError(f"expected one diff section for {symbol}, found {len(matches)}")
    return str(matches[0])


def audit_asset_rate_change(
    markdown: str,
    *,
    symbol: str,
    expected_before_bps: int,
    expected_after_bps: int,
) -> dict[str, Any]:
    """Verify that an asset section changes only the configured slope-1 policy field."""
    section = _asset_section(markdown, symbol)
    changed_rows: list[dict[str, str]] = []
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 3 or cells[0] in {"description", "---"}:
            continue
        if cells[1] != cells[2]:
            changed_rows.append({"field": cells[0], "before": cells[1], "after": cells[2]})

    policy_rows = [
        row
        for row in changed_rows
        if row["field"]
        not in {
            "baseStableBorrowRate",
            "interestRate",
            "interestRateStrategy",
            "maxVariableBorrowRate",
        }
    ]
    if len(policy_rows) != 1 or policy_rows[0]["field"] != "variableRateSlope1":
        raise ValueError(f"{symbol} has unexpected configured changes: {policy_rows}")
    row = policy_rows[0]
    before_bps = _percent_to_bps(row["before"])
    after_bps = _percent_to_bps(row["after"])
    if (before_bps, after_bps) != (expected_before_bps, expected_after_bps):
        raise ValueError(
            f"{symbol} slope-1 change is {before_bps}->{after_bps} bps, expected "
            f"{expected_before_bps}->{expected_after_bps}"
        )
    return {
        "symbol": symbol,
        "slope1_before_bps": before_bps,
        "slope1_after_bps": after_bps,
        "slope1_delta_bps": after_bps - before_bps,
        "configured_change_fields": ["variableRateSlope1"],
        "derived_or_deployment_rows": [
            row for row in changed_rows if row["field"] != "variableRateSlope1"
        ],
        "clean_singleton_configured_change": True,
    }


def extract_implementation_reference(description: str) -> tuple[str, str]:
    """Extract the unique proposal-source commit and directory from cached AIP text."""
    commits = set(re.findall(r"/blob/([0-9a-f]{40})/", description))
    directories = set(re.findall(r"/src/([^/]+)/", description))
    if len(commits) != 1 or len(directories) != 1:
        raise ValueError(
            f"expected one implementation commit/directory, found {commits} and {directories}"
        )
    return next(iter(commits)), next(iter(directories))


def load_json(path: Path) -> Any:
    """Load a JSON file with an explicit UTF-8 contract."""
    return json.loads(path.read_text(encoding="utf-8"))


def find_payload_execution(
    cache_root: Path,
    *,
    proposal_id: int,
    chain_id: int,
) -> dict[str, Any]:
    """Resolve one executed proposal payload to its exact target-chain event."""
    ui_root = cache_root / "cache" / "ui" / "mainnet"
    proposals = load_json(
        cache_root
        / "cache"
        / "1"
        / "proposals"
        / "0x9AEE0B04504CeF83A65AC3f0e838D0593BCb2BC7.json"
    )
    proposal = proposals.get(str(proposal_id))
    if not isinstance(proposal, dict) or proposal.get("state") != 4:
        raise ValueError(f"proposal {proposal_id} is not in executed state 4")

    payload_map = load_json(ui_root / "proposals_payloads.json")["data"]
    candidates = [
        row for row in payload_map.get(str(proposal_id), []) if int(row["chainId"]) == chain_id
    ]
    if len(candidates) != 1:
        raise ValueError(
            f"proposal {proposal_id} has {len(candidates)} payloads on chain {chain_id}"
        )
    payload = candidates[0]
    controller = normalize_address(str(payload["payloadsController"]))
    payload_id = int(payload["id"])

    payload_files = [
        path
        for path in (cache_root / "cache" / str(chain_id) / "payloads").glob("*.json")
        if normalize_address(path.stem) == controller
    ]
    if len(payload_files) != 1:
        raise ValueError(f"could not uniquely resolve payload cache for {controller}")
    payload_record = load_json(payload_files[0]).get(str(payload_id))
    if not isinstance(payload_record, dict) or int(payload_record.get("executedAt", 0)) <= 0:
        raise ValueError(f"payload {payload_id} has no execution timestamp")

    matches: list[dict[str, Any]] = []
    for event_file in (cache_root / "cache" / str(chain_id) / "events").glob("*.json"):
        for event in load_json(event_file):
            args = event.get("args", {})
            if (
                event.get("eventName") == "PayloadExecuted"
                and normalize_address(str(event["address"])) == controller
                and int(args.get("payloadId", -1)) == payload_id
            ):
                matches.append(event)
    if len(matches) != 1:
        raise ValueError(f"payload {payload_id} has {len(matches)} PayloadExecuted events")
    event = matches[0]

    list_rows = load_json(ui_root / "list_view_proposals.json")["proposals"]
    list_matches = [row for row in list_rows if int(row["id"]) == proposal_id]
    if len(list_matches) != 1:
        raise ValueError(f"proposal {proposal_id} is absent or duplicated in the list cache")
    list_row = list_matches[0]
    ipfs_record = load_json(ui_root / "ipfs" / f"{list_row['ipfsHash']}.json")
    implementation_commit, implementation_directory = extract_implementation_reference(
        str(ipfs_record["description"])
    )
    return {
        "proposal_id": proposal_id,
        "title": str(list_row["title"]),
        "ipfs_digest": str(list_row["ipfsHash"]),
        "ipfs_description_sha256": hashlib.sha256(
            str(ipfs_record["description"]).encode()
        ).hexdigest(),
        "discussion": ipfs_record.get("discussions"),
        "implementation_commit": implementation_commit,
        "implementation_directory": implementation_directory,
        "chain_id": chain_id,
        "payload_id": payload_id,
        "payloads_controller": controller,
        "executed_at_unix": int(payload_record["executedAt"]),
        "execution_block": int(event["blockNumber"]),
        "execution_transaction_hash": str(event["transactionHash"]),
        "execution_block_hash": str(event["blockHash"]),
    }
