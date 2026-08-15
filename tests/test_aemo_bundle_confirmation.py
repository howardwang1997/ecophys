from __future__ import annotations

import copy
from pathlib import Path
from typing import cast

from ecomd.research.aemo_bundle_confirmation import (
    DOWNLOAD_SCHEMA_VERSION,
    RETENTION_SCHEMA_VERSION,
    SOURCE_MANIFEST_PATH,
    load_bundle_manifest,
    summarize_bundle_confirmation,
    validate_bundle_manifest,
    validate_download_receipt,
    validate_retention_receipt,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / SOURCE_MANIFEST_PATH


def _receipts(manifest: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    objects = cast(list[dict[str, object]], manifest["objects"])
    downloaded = [
        {
            "object_id": item["object_id"],
            "request_count": 1,
            "http_status": 200,
            "expected_bytes": item["expected_bytes"],
            "observed_bytes": item["expected_bytes"],
            "sha256": str(index + 1) * 64,
            "download_pass": True,
        }
        for index, item in enumerate(objects)
    ]
    download: dict[str, object] = {
        "schema_version": DOWNLOAD_SCHEMA_VERSION,
        "generated_at": "2026-08-15T04:20:00Z",
        "protocol_git_commit": "a" * 40,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": "b" * 64,
        "request_policy": "exactly_one_get_per_frozen_object_no_retry_no_replacement",
        "objects": downloaded,
        "pass": True,
        "zip_opened": False,
        "csv_rows_opened": False,
    }
    retained = [
        {
            "object_id": item["object_id"],
            "r2_key": item["r2_key"],
            "observed_bytes": source["observed_bytes"],
            "sha256": source["sha256"],
            "remote_content_length": source["observed_bytes"],
            "remote_metadata_sha256": source["sha256"],
            "verified": True,
        }
        for item, source in zip(objects, downloaded, strict=True)
    ]
    retention: dict[str, object] = {
        "schema_version": RETENTION_SCHEMA_VERSION,
        "generated_at": "2026-08-15T04:21:00Z",
        "protocol_git_commit": "a" * 40,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": "b" * 64,
        "bucket": "ecophys",
        "prefix": "raw/aemo/v14_bundle_confirmation/market_date=2026-07-07/",
        "objects": retained,
        "all_verified": True,
        "zip_opened": False,
        "csv_rows_opened": False,
    }
    return download, retention


def _bid_day(duid: str, direction: str) -> dict[str, str]:
    return {
        "SETTLEMENTDATE": "2026/07/07 00:00:00",
        "DUID": duid,
        "BIDTYPE": "ENERGY",
        "DIRECTION": direction,
        "BIDSETTLEMENTDATE": "2026/07/07 00:00:00",
        "OFFERDATE": "2026/07/06 12:00:00",
        "PARTICIPANTID": "P1",
    }


def _bid_period(duid: str, direction: str) -> dict[str, str]:
    return {
        **_bid_day(duid, direction),
        "INTERVAL_DATETIME": "2026/07/07 04:05:00",
        "VERSIONNO": "1",
        "MAXAVAIL": "100",
    }


def _tracker(duid: str) -> dict[str, str]:
    return {
        "SETTLEMENTDATE": "2026/07/07 04:05:00",
        "DUID": duid,
        "BIDTYPE": "ENERGY",
        "BIDSETTLEMENTDATE": "2026/07/07 00:00:00",
        "BIDOFFERDATE": "2026/07/06 12:00:00",
    }


def _dispatch(duid: str, total_cleared: str) -> dict[str, str]:
    return {
        "SETTLEMENTDATE": "2026/07/07 04:05:00",
        "RUNNO": "1",
        "DUID": duid,
        "INTERVENTION": "0",
        "INITIALMW": "0",
        "TOTALCLEARED": total_cleared,
    }


def _identity(duid: str, dispatch_type: str) -> dict[str, str]:
    return {
        "DUID": duid,
        "START_DATE": "2020/01/01 00:00:00",
        "END_DATE": "2030/01/01 00:00:00",
        "DISPATCHTYPE": dispatch_type,
        "REGIONID": "NSW1",
        "PARTICIPANTID": "P1",
        "DISPATCHSUBTYPE": "SCHEDULED",
    }


def _tables() -> dict[str, list[dict[str, str]]]:
    return {
        "BIDDAYOFFER_D": [
            _bid_day("UNIT1", "GEN"),
            _bid_day("BDU1", "GEN"),
            _bid_day("BDU1", "LOAD"),
        ],
        "BIDPEROFFER_D": [
            _bid_period("UNIT1", "GEN"),
            _bid_period("BDU1", "GEN"),
            _bid_period("BDU1", "LOAD"),
        ],
        "DISPATCHOFFERTRK": [_tracker("UNIT1"), _tracker("BDU1")],
        "DISPATCHLOAD": [_dispatch("UNIT1", "50"), _dispatch("BDU1", "-10")],
        "DUDETAILSUMMARY": [
            _identity("UNIT1", "GENERATOR"),
            _identity("BDU1", "BIDIRECTIONAL"),
        ],
    }


def _observations() -> list[dict[str, object]]:
    role_groups = (
        ("BIDDAYOFFER_D", "BIDPEROFFER_D"),
        ("DISPATCHOFFERTRK", "DISPATCHLOAD"),
        ("DUDETAILSUMMARY",),
    )
    return [
        {
            "pass": True,
            "zip_crc_pass": True,
            "exact_byte_match": True,
            "total_data_rows": len(roles),
            "headers": [
                {
                    "logical_role": role,
                    "header_present": True,
                    "missing_required_fields": [],
                }
                for role in roles
            ],
            "object_id": f"object-{index}",
        }
        for index, roles in enumerate(role_groups)
    ]


def _summary(tables: dict[str, list[dict[str, str]]]) -> dict[str, object]:
    manifest = load_bundle_manifest(MANIFEST)
    download, retention = _receipts(manifest)
    return summarize_bundle_confirmation(
        tables,
        _observations(),
        manifest,
        download,
        retention,
        source_manifest_sha256="b" * 64,
        analyzer_git_commit="a" * 40,
        generated_at="2026-08-15T04:22:00Z",
    )


def test_manifest_is_valid_and_selection_is_fresh_cross_month() -> None:
    manifest = load_bundle_manifest(MANIFEST)

    assert validate_bundle_manifest(manifest) == ()
    selection = cast(dict[str, object], manifest["selection"])
    assert selection["development_month"] == "2026-06"
    assert selection["selected_market_date"] == "2026-07-07"
    assert selection["identity_snapshot_not_reused_from_development"] is True
    assert selection["target_event"] is False


def test_manifest_rejects_relation_or_source_mutation() -> None:
    invalid = copy.deepcopy(load_bundle_manifest(MANIFEST))
    cast(dict[str, object], invalid["relation_contract"])["allowed_candidate_cardinalities"] = [1, 2, 3]
    cast(list[dict[str, object]], invalid["objects"])[0]["expected_bytes"] = 1

    errors = validate_bundle_manifest(invalid)

    assert "relation_contract changed" in errors
    assert "objects changed" in errors


def test_synthetic_single_and_pair_relation_passes_every_gate() -> None:
    manifest = load_bundle_manifest(MANIFEST)
    download, retention = _receipts(manifest)

    assert validate_download_receipt(download, manifest) == ()
    assert validate_retention_receipt(retention, download, manifest) == ()
    summary = _summary(_tables())

    assert summary["decision"] == "PASS_FRESH_SET_VALUED_OFFER_BRIDGE_CONFIRMATION"
    assert summary["pass"] is True
    gates = cast(dict[str, bool], summary["gates"])
    assert len(gates) == 25
    assert all(gates.values())
    relation = cast(dict[str, object], summary["relation"])
    assert relation["candidate_cardinality"] == {"1": 1, "2": 1}
    assert relation["direction_sets"] == {"GEN": 1, "GEN|LOAD": 1}
    assert relation["pair_count"] == 1
    assert relation["realized_dispatch_used_to_select_leg"] is False


def test_pair_outside_frozen_bidtype_domain_fails() -> None:
    tables = _tables()
    for role in ("BIDDAYOFFER_D", "BIDPEROFFER_D"):
        for row in tables[role]:
            if row["DUID"] == "BDU1":
                row["BIDTYPE"] = "RAISE6SEC"
    tables["DISPATCHOFFERTRK"][1]["BIDTYPE"] = "RAISE6SEC"

    summary = _summary(tables)

    gates = cast(dict[str, bool], summary["gates"])
    relation = cast(dict[str, object], summary["relation"])
    assert gates["pair_bidtype_domain"] is False
    assert relation["invalid_pair_bidtype_count"] == 1
    assert summary["pass"] is False


def test_pair_requires_effective_bidirectional_identity() -> None:
    tables = _tables()
    tables["DUDETAILSUMMARY"][1]["DISPATCHTYPE"] = "GENERATOR"

    summary = _summary(tables)

    gates = cast(dict[str, bool], summary["gates"])
    assert gates["pair_effective_identity"] is False
    assert summary["pass"] is False


def test_receipts_reject_content_access_before_r2_retention() -> None:
    manifest = load_bundle_manifest(MANIFEST)
    download, retention = _receipts(manifest)
    download["zip_opened"] = True
    retention["csv_rows_opened"] = True

    assert any("content access" in error for error in validate_download_receipt(download, manifest))
    assert any(
        "content access" in error for error in validate_retention_receipt(retention, download, manifest)
    )
