#!/usr/bin/env python3
"""Collect the exact frozen 100-auction CoW development sample."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import requests

from ecomd.market_world.provenance import require_clean_repository
from ecomd.research.cow_development_audit import (
    audit_competition_payload,
    canonical_json_sha256,
    parse_block_timestamp_response,
    summarize_initial_sample,
)
from ecomd.research.open_data_development import (
    RESOLVED_STAGE,
    contract_sha256,
    load_development_contract,
    validate_development_contract,
)

ETHEREUM_RPC_URL = "https://cloudflare-eth.com"
USER_AGENT = "EcoPhys-open-data-feasibility/1.0"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _append_json_line(path: Path, payload: dict[str, object]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()


def _read_ledger(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    entries: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        payload: object = json.loads(line)
        if not isinstance(payload, dict):
            raise RuntimeError(f"ledger line {line_number} is not an object")
        entries.append(cast(dict[str, object], payload))
    return entries


def _fetch_competition(
    session: requests.Session,
    *,
    url: str,
    retries: int,
) -> tuple[requests.Response | None, str | None, int]:
    last_error: str | None = None
    for attempt in range(1, retries + 2):
        try:
            response = session.get(url, timeout=60.0, allow_redirects=False)
        except requests.RequestException as error:
            last_error = f"{type(error).__name__}: {error}"
            if attempt <= retries:
                time.sleep(1.0)
                continue
            return None, last_error, attempt
        return response, None, attempt
    raise AssertionError("unreachable retry loop")


def _block_timestamps(
    session: requests.Session,
    blocks: list[int],
    *,
    raw_path: Path,
    resume: bool,
) -> tuple[dict[int, int], str, str | None]:
    request_payload = [
        {
            "jsonrpc": "2.0",
            "id": index,
            "method": "eth_getBlockByNumber",
            "params": [hex(block), False],
        }
        for index, block in enumerate(blocks)
    ]
    if raw_path.exists():
        if not resume:
            raise FileExistsError(f"refusing to overwrite {raw_path}")
        raw = raw_path.read_bytes()
    else:
        response = session.post(
            ETHEREUM_RPC_URL,
            json=request_payload,
            timeout=60.0,
            allow_redirects=False,
        )
        response.raise_for_status()
        raw = response.content
        raw_path.write_bytes(raw)
    timestamps, error = parse_block_timestamp_response(raw, blocks)
    return timestamps, hashlib.sha256(raw).hexdigest(), error


def _validate_collection_commit(value: str) -> None:
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise ValueError("collection commit must be a full lowercase Git SHA")
    subprocess.run(
        ["git", "cat-file", "-e", f"{value}^{{commit}}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT / "data/manifests/open_data_development_sample_v1_resolved.yaml",
    )
    parser.add_argument(
        "--raw-root",
        type=Path,
        default=ROOT / "artifacts/v14_open_data_feasibility/cow",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=ROOT / "experiments/v14_open_data_feasibility/artifacts/cow_initial_summary.json",
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--collection-commit")
    arguments = parser.parse_args()
    if arguments.summary.exists():
        raise FileExistsError(f"refusing to overwrite {arguments.summary}")

    commit = require_clean_repository(ROOT)
    contract = load_development_contract(arguments.contract)
    errors = validate_development_contract(contract)
    if errors or contract.get("stage") != RESOLVED_STAGE:
        raise RuntimeError("resolved development contract is invalid: " + "; ".join(errors))
    cow = cast(dict[str, object], contract["cow"])
    sample = cast(dict[str, object], cow["initial_sample"])
    ids = cast(list[int], sample["auction_ids"])
    base_url = cast(str, cow["base_url"]).rstrip("/")
    template = cast(str, cow["competition_endpoint_template"])
    rate = float(cast(float, cow["maximum_requests_per_second"]))
    retries = cast(int, cow["maximum_transport_retries"])
    cutoff = cast(str, cow["cutoff_utc"])
    minimum_coverage = float(
        cast(dict[str, object], cow["gates"])["initial_http_200_coverage_minimum"]
    )

    arguments.raw_root.mkdir(parents=True, exist_ok=True)
    payload_root = arguments.raw_root / "payloads"
    payload_root.mkdir(parents=True, exist_ok=True)
    ledger_path = arguments.raw_root / "request_ledger.jsonl"
    if ledger_path.exists() and not arguments.resume:
        raise FileExistsError(f"ledger already exists; use --resume: {ledger_path}")
    entries = _read_ledger(ledger_path)
    if entries and arguments.collection_commit is None:
        raise RuntimeError("resuming a nonempty ledger requires --collection-commit")
    collection_commit = arguments.collection_commit or commit
    _validate_collection_commit(collection_commit)
    completed_ids = [entry.get("auction_id") for entry in entries]
    if completed_ids != ids[: len(completed_ids)]:
        raise RuntimeError("existing ledger is not an exact prefix of the frozen ID list")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    minimum_interval = 1.0 / rate
    previous_start: float | None = None
    for index, auction_id in enumerate(ids[len(entries) :], start=len(entries)):
        if previous_start is not None:
            time.sleep(max(0.0, minimum_interval - (time.monotonic() - previous_start)))
        previous_start = time.monotonic()
        endpoint = template.format(auction_id=auction_id)
        url = base_url + "/" + endpoint.lstrip("/")
        retrieved_at = _utc_now()
        response, transport_error, attempts = _fetch_competition(
            session,
            url=url,
            retries=retries,
        )
        entry: dict[str, object] = {
            "request_index": index,
            "auction_id": auction_id,
            "url": url,
            "retrieved_at": retrieved_at,
            "attempts": attempts,
            "transport_error": transport_error,
            "http_status": None,
            "response_bytes": 0,
            "response_sha256": None,
            "parse_ok": False,
            "parse_errors": [],
            "payload_auction_id": None,
            "auction_start_block": None,
        }
        if response is not None:
            raw = response.content
            entry["http_status"] = response.status_code
            entry["response_bytes"] = len(raw)
            entry["response_sha256"] = hashlib.sha256(raw).hexdigest()
            if response.status_code == 200:
                raw_path = payload_root / f"{auction_id}.json"
                if raw_path.exists():
                    raise FileExistsError(f"refusing to overwrite {raw_path}")
                raw_path.write_bytes(raw)
                try:
                    payload: object = json.loads(raw)
                    if not isinstance(payload, dict):
                        raise ValueError("response root is not an object")
                    audit = audit_competition_payload(
                        cast(dict[str, object], payload),
                        requested_auction_id=auction_id,
                    )
                except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
                    entry["parse_errors"] = [f"{type(error).__name__}: {error}"]
                else:
                    entry.update(audit)
        _append_json_line(ledger_path, entry)
        entries.append(entry)
        print(
            json.dumps(
                {
                    "completed": len(entries),
                    "total": len(ids),
                    "auction_id": auction_id,
                    "http_status": entry["http_status"],
                    "parse_ok": entry["parse_ok"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    start_blocks = sorted(
        {
            cast(int, entry["auction_start_block"])
            for entry in entries
            if entry.get("parse_ok") is True and isinstance(entry.get("auction_start_block"), int)
        }
    )
    block_path = arguments.raw_root / "ethereum_start_blocks.json"
    block_timestamps, block_sha256, block_error = _block_timestamps(
        session,
        start_blocks,
        raw_path=block_path,
        resume=arguments.resume,
    )
    ledger_sha256 = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    summary = summarize_initial_sample(
        entries,
        expected_ids=ids,
        block_timestamps=block_timestamps,
        cutoff_utc=cutoff,
        minimum_http_200_coverage=minimum_coverage,
        ledger_sha256=ledger_sha256,
        block_response_sha256=block_sha256,
    )
    summary["block_lookup_error"] = block_error
    summary["ownership"] = {
        "collection_git_commit": collection_commit,
        "summary_git_commit": commit,
        "resolved_contract_sha256": contract_sha256(arguments.contract),
        "collected_at_utc": _utc_now(),
        "raw_root": arguments.raw_root.relative_to(ROOT).as_posix(),
        "ethereum_rpc_url": ETHEREUM_RPC_URL,
        "request_set_sha256": canonical_json_sha256(ids),
        "resume_deviation": (
            "The frozen 100-request ledger completed under collection_git_commit. The provider rejected the "
            "single batch timestamp lookup because its maximum batch size is ten. This summary commit reuses "
            "that immutable error response and makes no sample request."
            if entries
            else None
        ),
    }
    arguments.summary.parent.mkdir(parents=True, exist_ok=True)
    arguments.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
