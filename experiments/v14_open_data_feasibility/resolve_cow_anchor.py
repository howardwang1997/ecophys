#!/usr/bin/env python3
"""Resolve the single permitted CoW anchor field after contract freeze."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import requests
import yaml

from ecomd.market_world.provenance import require_clean_repository
from ecomd.research.open_data_development import (
    load_development_contract,
    resolve_cow_anchor,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT / "data/manifests/open_data_development_sample_v1.yaml",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/manifests/open_data_development_sample_v1_resolved.yaml",
    )
    arguments = parser.parse_args()
    if arguments.output.exists():
        raise FileExistsError(f"refusing to overwrite {arguments.output}")

    commit = require_clean_repository(ROOT)
    contract = load_development_contract(arguments.contract)
    cow_raw = contract.get("cow")
    if not isinstance(cow_raw, dict):
        raise RuntimeError("contract cow section is invalid")
    cow = cast(dict[str, object], cow_raw)
    anchor_raw = cow.get("anchor")
    if not isinstance(anchor_raw, dict):
        raise RuntimeError("contract cow.anchor section is invalid")
    anchor = cast(dict[str, object], anchor_raw)
    base_url = cow.get("base_url")
    endpoint = anchor.get("endpoint")
    if not isinstance(base_url, str) or not isinstance(endpoint, str):
        raise RuntimeError("contract CoW URL is invalid")
    url = base_url.rstrip("/") + "/" + endpoint.lstrip("/")
    response = requests.get(
        url,
        headers={"User-Agent": "EcoPhys-open-data-feasibility/1.0"},
        timeout=30.0,
        allow_redirects=False,
    )
    response.raise_for_status()
    payload: object = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("CoW latest endpoint did not return an object")
    body = response.content
    resolved_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    resolved = resolve_cow_anchor(
        contract,
        anchor_payload=cast(dict[str, object], payload),
        resolved_at=resolved_at,
        response_sha256=hashlib.sha256(body).hexdigest(),
        response_bytes=len(body),
        resolver_git_commit=commit,
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        yaml.safe_dump(resolved, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    resolved_cow = cast(dict[str, object], resolved["cow"])
    resolved_anchor = cast(dict[str, object], resolved_cow["anchor"])
    initial = cast(dict[str, object], resolved_cow["initial_sample"])
    expansion = cast(dict[str, object], resolved_cow["expansion_sample"])
    print(
        json.dumps(
            {
                "anchor_id": resolved_anchor["resolved_anchor_id"],
                "resolved_at": resolved_anchor["resolved_at"],
                "response_sha256": resolved_anchor["response_sha256"],
                "response_bytes": resolved_anchor["response_bytes"],
                "initial_count": initial["count"],
                "initial_ids_sha256": initial["auction_ids_sha256"],
                "expansion_count": expansion["count"],
                "expansion_ids_sha256": expansion["auction_ids_sha256"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
