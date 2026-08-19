"""Outcome-blind qualification helpers for the dYdX fixed-carry study."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

EndpointKind = Literal["trades", "candles", "historical_funding"]


@dataclass(frozen=True)
class EndpointSpec:
    """Public response fields that D0 may retain as metadata."""

    collection_key: str
    timestamp_key: str
    height_key: str | None
    required_fields: frozenset[str]


ENDPOINT_SPECS: dict[EndpointKind, EndpointSpec] = {
    "trades": EndpointSpec(
        collection_key="trades",
        timestamp_key="createdAt",
        height_key="createdAtHeight",
        required_fields=frozenset(
            {"id", "side", "size", "price", "type", "createdAt", "createdAtHeight"}
        ),
    ),
    "candles": EndpointSpec(
        collection_key="candles",
        timestamp_key="startedAt",
        height_key=None,
        required_fields=frozenset(
            {
                "ticker",
                "resolution",
                "startedAt",
                "open",
                "high",
                "low",
                "close",
                "baseTokenVolume",
                "trades",
                "startingOpenInterest",
            }
        ),
    ),
    "historical_funding": EndpointSpec(
        collection_key="historicalFunding",
        timestamp_key="effectiveAt",
        height_key="effectiveAtHeight",
        required_fields=frozenset(
            {"ticker", "rate", "price", "effectiveAt", "effectiveAtHeight"}
        ),
    ),
}

PERPETUAL_UPDATE_TYPE = "/dydxprotocol.perpetuals.MsgUpdatePerpetualParams"
PAYLOAD_FIELDS = (
    "id",
    "ticker",
    "market_id",
    "atomic_resolution",
    "default_funding_ppm",
    "liquidity_tier",
    "market_type",
)


def canonical_sha256(value: Any) -> str:
    """Return a deterministic digest without exposing the encoded values."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _value_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _rows(payload: Mapping[str, Any], collection_key: str) -> list[Mapping[str, Any]]:
    raw_rows = payload.get(collection_key)
    if not isinstance(raw_rows, list):
        raise ValueError(f"response field {collection_key!r} is not a list")
    if not all(isinstance(row, Mapping) for row in raw_rows):
        raise ValueError(f"response field {collection_key!r} contains a non-object row")
    return list(raw_rows)


def row_identity_digests(payload: Mapping[str, Any], endpoint: EndpointKind) -> set[str]:
    """Create transient identities for overlap checks; no row value is returned."""
    spec = ENDPOINT_SPECS[endpoint]
    identities: set[str] = set()
    for row in _rows(payload, spec.collection_key):
        identity = row.get("id")
        identities.add(canonical_sha256(identity if identity is not None else row))
    return identities


def summarize_response(
    payload: Mapping[str, Any],
    *,
    raw_body: bytes,
    endpoint: EndpointKind,
    request_label: str,
) -> dict[str, Any]:
    """Summarize schema and coverage while retaining no market outcome value."""
    spec = ENDPOINT_SPECS[endpoint]
    rows = _rows(payload, spec.collection_key)
    row_keys = sorted({key for row in rows for key in row})
    field_types = {
        key: sorted({_value_type(row[key]) for row in rows if key in row}) for key in row_keys
    }
    timestamps = [
        str(row[spec.timestamp_key]) for row in rows if row.get(spec.timestamp_key) is not None
    ]
    heights: list[int] = []
    if spec.height_key is not None:
        for row in rows:
            value = row.get(spec.height_key)
            if value is not None:
                heights.append(int(value))
    identities = row_identity_digests(payload, endpoint)
    missing_required = {
        key: sum(key not in row or row[key] is None for row in rows)
        for key in sorted(spec.required_fields)
    }
    pagination = {
        key: payload[key]
        for key in ("pageSize", "totalResults", "offset")
        if isinstance(payload.get(key), int)
    }
    return {
        "request_label": request_label,
        "endpoint": endpoint,
        "http_body_bytes": len(raw_body),
        "raw_body_sha256": hashlib.sha256(raw_body).hexdigest(),
        "top_level_keys": sorted(payload),
        "row_count": len(rows),
        "row_keys": row_keys,
        "field_types": field_types,
        "missing_required_field_counts": missing_required,
        "unique_row_identity_count": len(identities),
        "duplicate_row_identity_count": len(rows) - len(identities),
        "minimum_timestamp": min(timestamps) if timestamps else None,
        "maximum_timestamp": max(timestamps) if timestamps else None,
        "minimum_height": min(heights) if heights else None,
        "maximum_height": max(heights) if heights else None,
        "pagination": pagination,
        "retained_market_outcome_values": False,
    }


def extract_passed_perpetual_updates(
    proposals: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Extract the complete passed governance ledger for perpetual-parameter messages."""
    updates: list[dict[str, Any]] = []
    for proposal in proposals:
        if proposal.get("status") != "PROPOSAL_STATUS_PASSED":
            continue
        for message in proposal.get("messages", []):
            if not isinstance(message, Mapping) or message.get("@type") != PERPETUAL_UPDATE_TYPE:
                continue
            params = message.get("perpetual_params")
            if not isinstance(params, Mapping):
                raise ValueError("perpetual update lacks perpetual_params")
            updates.append(
                {
                    "proposal_id": int(proposal["id"]),
                    "voting_end_time": str(proposal["voting_end_time"]),
                    "authority": str(message["authority"]),
                    "params": {key: params.get(key) for key in PAYLOAD_FIELDS},
                }
            )
    return sorted(updates, key=lambda row: (row["voting_end_time"], row["proposal_id"]))


def audit_funding_transition(
    updates: Sequence[Mapping[str, Any]],
    *,
    proposal_id: int,
    tickers: Sequence[str],
    expected_pre: int,
    expected_post: int,
) -> list[dict[str, Any]]:
    """Verify that each frozen transition changes only the funding payload field."""
    event_rows = [row for row in updates if int(row["proposal_id"]) == proposal_id]
    if not event_rows:
        raise ValueError(f"proposal {proposal_id} has no passed perpetual updates")
    event_time = str(event_rows[0]["voting_end_time"])
    audits: list[dict[str, Any]] = []
    for ticker in tickers:
        post_candidates = [row for row in event_rows if row["params"]["ticker"] == ticker]
        if len(post_candidates) != 1:
            raise ValueError(f"proposal {proposal_id} has {len(post_candidates)} updates for {ticker}")
        prior = [
            row
            for row in updates
            if str(row["voting_end_time"]) < event_time and row["params"]["ticker"] == ticker
        ]
        if not prior:
            raise ValueError(f"no prior passed full payload for {ticker}")
        pre = prior[-1]
        post = post_candidates[0]
        changed = [key for key in PAYLOAD_FIELDS if pre["params"].get(key) != post["params"].get(key)]
        pre_funding = int(pre["params"]["default_funding_ppm"])
        post_funding = int(post["params"]["default_funding_ppm"])
        clean = pre_funding == expected_pre and post_funding == expected_post and changed == [
            "default_funding_ppm"
        ]
        audits.append(
            {
                "ticker": ticker,
                "pre_proposal_id": int(pre["proposal_id"]),
                "post_proposal_id": proposal_id,
                "pre_default_funding_ppm": pre_funding,
                "post_default_funding_ppm": post_funding,
                "changed_payload_fields": changed,
                "clean": clean,
            }
        )
    return audits
