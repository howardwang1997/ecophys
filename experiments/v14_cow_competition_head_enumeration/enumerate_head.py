#!/usr/bin/env python3
"""Enumerate a frozen CoW candidate frame with status-only HEAD requests."""

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
import yaml

from ecomd.market_world.provenance import require_clean_repository
from ecomd.research.cow_competition_enumeration import (
    contract_sha256,
    derive_candidate_ids,
    load_contract,
    materialize_resolved_contract,
    summarize_head_enumeration,
    validate_frozen_contract,
)


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


def _validate_commit(repository: Path, value: str) -> None:
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise ValueError("collection commit must be a full lowercase Git SHA")
    subprocess.run(
        ["git", "cat-file", "-e", f"{value}^{{commit}}"],
        cwd=repository,
        check=True,
        capture_output=True,
    )


def _head_status(
    session: requests.Session,
    *,
    url: str,
    retries: int,
) -> tuple[int | None, list[int | None], list[str]]:
    statuses: list[int | None] = []
    errors: list[str] = []
    for attempt in range(retries + 1):
        try:
            response = session.head(url, timeout=60.0, allow_redirects=False, stream=True)
        except requests.RequestException as error:
            statuses.append(None)
            errors.append(f"{type(error).__name__}: {error}")
        else:
            status = response.status_code
            statuses.append(status)
            response.close()
            if status in {200, 404}:
                return status, statuses, errors
        if attempt < retries:
            time.sleep(float(attempt + 1))
    return statuses[-1], statuses, errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT / "data/manifests/cow_competition_head_enumeration_v1.yaml",
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=(
            ROOT / "experiments/v14_cow_competition_head_enumeration/artifacts/head_request_ledger.jsonl"
        ),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=(
            ROOT / "experiments/v14_cow_competition_head_enumeration/artifacts/head_enumeration_summary.json"
        ),
    )
    parser.add_argument(
        "--resolved-contract",
        type=Path,
        default=ROOT / "data/manifests/cow_competition_head_enumeration_v1_resolved.yaml",
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--collection-commit")
    parser.add_argument("--progress-every", type=int, default=25)
    arguments = parser.parse_args()
    if arguments.progress_every <= 0:
        raise ValueError("progress-every must be positive")
    if arguments.summary.exists() or arguments.resolved_contract.exists():
        raise FileExistsError("refusing to overwrite a summary or resolved contract")

    current_commit = require_clean_repository(ROOT)
    contract = load_contract(arguments.contract)
    errors = validate_frozen_contract(contract)
    if errors:
        raise RuntimeError("invalid frozen enumeration contract: " + "; ".join(errors))

    source = cast(dict[str, object], contract["source"])
    anchor = cast(dict[str, object], contract["anchor"])
    frame = cast(dict[str, object], contract["candidate_frame"])
    gates = cast(dict[str, object], contract["gates"])
    ids = derive_candidate_ids(
        cast(int, anchor["resolved_anchor_id"]),
        first_offset_below_anchor=cast(int, frame["first_offset_below_anchor"]),
        count=cast(int, frame["count"]),
        stride=cast(int, frame["stride"]),
    )
    base_url = cast(str, source["base_url"]).rstrip("/")
    template = cast(str, source["endpoint_template"])
    rate = float(cast(float, source["maximum_requests_per_second"]))
    retries = cast(int, source["maximum_transport_retries"])
    minimum_eligible = cast(int, gates["minimum_eligible_count"])

    arguments.ledger.parent.mkdir(parents=True, exist_ok=True)
    arguments.summary.parent.mkdir(parents=True, exist_ok=True)
    arguments.resolved_contract.parent.mkdir(parents=True, exist_ok=True)
    if arguments.ledger.exists() and not arguments.resume:
        raise FileExistsError(f"ledger already exists; use --resume: {arguments.ledger}")
    entries = _read_ledger(arguments.ledger)
    if entries and arguments.collection_commit is None:
        raise RuntimeError("resuming a nonempty ledger requires --collection-commit")
    collection_commit = arguments.collection_commit or current_commit
    _validate_commit(ROOT, collection_commit)
    completed_ids = [entry.get("auction_id") for entry in entries]
    if completed_ids != list(ids[: len(completed_ids)]):
        raise RuntimeError("existing ledger is not an exact prefix of the frozen candidate sequence")

    session = requests.Session()
    session.headers.update({"User-Agent": cast(str, source["user_agent"])})
    minimum_interval = 1.0 / rate
    previous_start: float | None = None
    for index, auction_id in enumerate(ids[len(entries) :], start=len(entries)):
        if previous_start is not None:
            time.sleep(max(0.0, minimum_interval - (time.monotonic() - previous_start)))
        previous_start = time.monotonic()
        endpoint = template.format(auction_id=auction_id)
        url = base_url + "/" + endpoint.lstrip("/")
        status, attempt_statuses, transport_errors = _head_status(
            session,
            url=url,
            retries=retries,
        )
        entry: dict[str, object] = {
            "request_index": index,
            "auction_id": auction_id,
            "request_method": "HEAD",
            "url": url,
            "retrieved_at_utc": _utc_now(),
            "attempt_count": len(attempt_statuses),
            "attempt_http_statuses": attempt_statuses,
            "transport_errors": transport_errors,
            "http_status": status,
            "response_body_bytes_read": 0,
        }
        _append_json_line(arguments.ledger, entry)
        entries.append(entry)
        completed = len(entries)
        if completed % arguments.progress_every == 0 or completed == len(ids) or status not in {200, 404}:
            print(
                json.dumps(
                    {
                        "completed": completed,
                        "total": len(ids),
                        "auction_id": auction_id,
                        "http_status": status,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )

    ledger_digest = hashlib.sha256(arguments.ledger.read_bytes()).hexdigest()
    summary = summarize_head_enumeration(
        entries,
        expected_ids=ids,
        minimum_eligible_count=minimum_eligible,
        ledger_sha256=ledger_digest,
    )
    collected_at = _utc_now()
    summary["ownership"] = {
        "collection_git_commit": collection_commit,
        "summary_git_commit": current_commit,
        "frozen_contract_sha256": contract_sha256(arguments.contract),
        "collected_at_utc": collected_at,
        "request_method": "HEAD",
        "response_headers_retained": False,
        "competition_response_bodies_opened": 0,
        "paid_data": False,
        "gpu_hours": 0,
    }
    arguments.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if summary["pass"] is True:
        resolved = materialize_resolved_contract(
            contract,
            summary=summary,
            collection_git_commit=collection_commit,
            collected_at_utc=collected_at,
        )
        arguments.resolved_contract.write_text(
            yaml.safe_dump(resolved, sort_keys=False, width=110),
            encoding="utf-8",
        )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
