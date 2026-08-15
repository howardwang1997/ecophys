from __future__ import annotations

from collections.abc import Mapping

import pytest

from ecomd.research.cow_competition_enumeration import (
    FROZEN_STAGE,
    RESOLVED_STAGE,
    SCHEMA_VERSION,
    canonical_json_sha256,
    derive_candidate_ids,
    materialize_resolved_contract,
    summarize_head_enumeration,
    validate_frozen_contract,
)


def _contract() -> dict[str, object]:
    ids = derive_candidate_ids(1000, first_offset_below_anchor=100, count=4, stride=1)
    return {
        "schema_version": SCHEMA_VERSION,
        "stage": FROZEN_STAGE,
        "scientific_role": "development_only_no_confirmation_claim",
        "source": {
            "network": "mainnet",
            "base_url": "https://api.cow.fi/mainnet",
            "endpoint_template": "/api/v2/solver_competition/{auction_id}",
            "request_method": "HEAD",
            "retained_response_fields": ["http_status"],
            "discard_all_response_headers": True,
            "openapi_sha256": "a" * 64,
            "deployed_openapi_sha256": "b" * 64,
            "deployed_git_commit": "c" * 40,
            "maximum_requests_per_second": 1.0,
            "maximum_transport_retries": 2,
        },
        "anchor": {
            "resolved_anchor_id": 1000,
            "resolved_manifest_sha256": "d" * 64,
        },
        "candidate_frame": {
            "first_offset_below_anchor": 100,
            "count": 4,
            "stride": 1,
            "candidate_id_maximum": max(ids),
            "candidate_id_minimum": min(ids),
            "candidate_ids_sha256": canonical_json_sha256(ids),
            "previous_expansion_id_minimum": 950,
            "no_replacement": True,
        },
        "access_boundary": {
            "head_only_before_resolution_commit": True,
            "response_body_bytes_read_must_be_zero": True,
            "resolved_manifest_commit_required_before_get": True,
            "retain_every_request_outcome": True,
            "competition_bodies_opened": False,
        },
        "gates": {
            "minimum_eligible_count": 2,
            "eligible_http_status": 200,
            "allowed_terminal_http_statuses": [200, 404],
            "exact_candidate_order_required": True,
            "exact_request_count_required": 4,
            "zero_body_bytes_required": True,
            "no_headers_retained_required": True,
            "no_transport_or_unexpected_status_allowed": True,
        },
        "enumeration_result": None,
    }


def _entry(index: int, auction_id: int, status: int) -> dict[str, object]:
    return {
        "request_index": index,
        "auction_id": auction_id,
        "request_method": "HEAD",
        "http_status": status,
        "response_body_bytes_read": 0,
    }


def test_frozen_contract_and_exact_candidate_hash() -> None:
    contract = _contract()
    assert validate_frozen_contract(contract) == ()
    assert derive_candidate_ids(1000, first_offset_below_anchor=100, count=4, stride=1) == (
        900,
        899,
        898,
        897,
    )


@pytest.mark.parametrize("field", ["headers", "content_length", "response_body"])
def test_summary_rejects_any_retained_response_metadata(field: str) -> None:
    ids = [900, 899]
    entries = [_entry(0, 900, 200), _entry(1, 899, 404)]
    entries[0][field] = "forbidden"
    summary = summarize_head_enumeration(
        entries,
        expected_ids=ids,
        minimum_eligible_count=1,
        ledger_sha256="e" * 64,
    )
    assert summary["pass"] is False
    assert field in summary["forbidden_retained_fields"]


def test_summary_freezes_only_status_200_ids_in_request_order() -> None:
    ids = [900, 899, 898, 897]
    entries = [
        _entry(0, 900, 200),
        _entry(1, 899, 404),
        _entry(2, 898, 200),
        _entry(3, 897, 404),
    ]
    summary = summarize_head_enumeration(
        entries,
        expected_ids=ids,
        minimum_eligible_count=2,
        ledger_sha256="f" * 64,
    )
    assert summary["pass"] is True
    assert summary["eligible_auction_ids"] == [900, 898]
    assert summary["eligible_auction_ids_sha256"] == canonical_json_sha256([900, 898])
    assert summary["http_status_counts"] == {"200": 2, "404": 2}


def test_summary_fails_on_order_body_or_unexpected_status() -> None:
    entries = [_entry(0, 899, 200), _entry(1, 900, 503)]
    entries[0]["response_body_bytes_read"] = 1
    summary = summarize_head_enumeration(
        entries,
        expected_ids=[900, 899],
        minimum_eligible_count=1,
        ledger_sha256="1" * 64,
    )
    assert summary["pass"] is False
    gates = summary["gates"]
    assert isinstance(gates, Mapping)
    assert gates["exact_candidate_order"] is False
    assert gates["zero_response_body_bytes_read"] is False
    assert gates["terminal_statuses_only"] is False


def test_passing_summary_materializes_exact_get_set() -> None:
    contract = _contract()
    ids = [900, 899, 898, 897]
    entries = [
        _entry(0, 900, 200),
        _entry(1, 899, 404),
        _entry(2, 898, 200),
        _entry(3, 897, 404),
    ]
    summary = summarize_head_enumeration(
        entries,
        expected_ids=ids,
        minimum_eligible_count=2,
        ledger_sha256="2" * 64,
    )
    resolved = materialize_resolved_contract(
        contract,
        summary=summary,
        collection_git_commit="3" * 40,
        collected_at_utc="2026-08-15T00:00:00Z",
    )
    assert resolved["stage"] == RESOLVED_STAGE
    result = resolved["enumeration_result"]
    assert isinstance(result, Mapping)
    assert result["eligible_auction_ids"] == [900, 898]


def test_failed_summary_cannot_materialize_get_set() -> None:
    summary = summarize_head_enumeration(
        [_entry(0, 900, 404)],
        expected_ids=[900],
        minimum_eligible_count=1,
        ledger_sha256="4" * 64,
    )
    with pytest.raises(ValueError, match="failed HEAD enumeration"):
        materialize_resolved_contract(
            _contract(),
            summary=summary,
            collection_git_commit="5" * 40,
            collected_at_utc="2026-08-15T00:00:00Z",
        )
