from __future__ import annotations

import copy
from pathlib import Path
from typing import cast

from ecomd.research.aemo_bundle_stability_panel import (
    DOWNLOAD_SCHEMA_VERSION,
    EXPECTED_MANIFEST_SHA256,
    EXPECTED_STAGED_BYTES,
    RETENTION_SCHEMA_VERSION,
    SOURCE_MANIFEST_PATH,
    build_day_manifest,
    build_day_receipts,
    load_panel_manifest,
    manifest_sha256,
    summarize_panel,
    validate_download_receipt,
    validate_panel_manifest,
    validate_retention_receipt,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / SOURCE_MANIFEST_PATH


def _receipts(manifest: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    new_specs = cast(list[dict[str, object]], manifest["new_objects"])
    reused_specs = cast(list[dict[str, object]], manifest["reused_objects"])
    downloaded = [
        {
            "object_id": spec["object_id"],
            "url": spec["url"],
            "local_filename": spec["expected_filename"],
            "request_count": 1,
            "http_status": 200,
            "observed_bytes": spec["expected_bytes"],
            "sha256": str(index + 1) * 64,
            "download_pass": True,
            "zip_opened": False,
            "csv_rows_opened": False,
        }
        for index, spec in enumerate(new_specs)
    ]
    download: dict[str, object] = {
        "schema_version": DOWNLOAD_SCHEMA_VERSION,
        "generated_at": "2026-08-15T04:40:00Z",
        "protocol_git_commit": "a" * 40,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "request_policy": "exactly_one_get_per_new_object_no_retry_no_replacement",
        "objects": downloaded,
        "pass": True,
        "zip_opened": False,
        "csv_rows_opened": False,
    }
    retained: list[dict[str, object]] = []
    for item, spec in zip(downloaded, new_specs, strict=True):
        retained.append(
            {
                "object_id": spec["object_id"],
                "observed_bytes": spec["expected_bytes"],
                "sha256": item["sha256"],
                "remote_content_length": spec["expected_bytes"],
                "remote_metadata_sha256": item["sha256"],
                "materialization": "source_download_uploaded_to_frozen_r2",
                "verified": True,
            }
        )
    for spec in reused_specs:
        retained.append(
            {
                "object_id": spec["object_id"],
                "observed_bytes": spec["expected_bytes"],
                "sha256": spec["sha256"],
                "remote_content_length": spec["expected_bytes"],
                "remote_metadata_sha256": spec["sha256"],
                "materialization": "verified_prior_r2_download_no_source_get",
                "source_get_performed": False,
                "verified": True,
            }
        )
    retention: dict[str, object] = {
        "schema_version": RETENTION_SCHEMA_VERSION,
        "generated_at": "2026-08-15T04:41:00Z",
        "protocol_git_commit": "a" * 40,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "objects": retained,
        "all_verified": True,
        "zip_opened": False,
        "csv_rows_opened": False,
    }
    return download, retention


def _day_summary(market_date: str, *, passed: bool = True) -> dict[str, object]:
    return {
        "sample_date": market_date,
        "pass": passed,
        "relation": {
            "tracker_count": 100,
            "pair_count": 10,
            "candidate_cardinality": {"1": 90, "2": 10},
            "direction_sets": {"GEN": 50, "LOAD": 40, "GEN|LOAD": 10},
            "pair_bidtypes": {"ENERGY": 10},
            "invalid_candidate_cardinality_count": 0,
            "invalid_single_direction_count": 0,
            "invalid_pair_direction_count": 0,
            "duplicate_pair_direction_count": 0,
            "invalid_pair_identity_count": 0,
            "invalid_pair_bidtype_count": 0,
        },
        "tables": {
            "total_target_rows": 200,
            "total_data_rows_all_tables": 220,
        },
        "timestamps": {"expected_count": 500},
    }


def test_frozen_manifest_is_exact_and_uses_four_untouched_tuesdays() -> None:
    manifest = load_panel_manifest(MANIFEST)

    assert manifest_sha256(MANIFEST) == EXPECTED_MANIFEST_SHA256
    assert validate_panel_manifest(manifest, source_sha256=manifest_sha256(MANIFEST)) == ()
    selection = cast(dict[str, object], manifest["selection"])
    assert selection["selected_dates"] == [
        "2026-06-23",
        "2026-06-30",
        "2026-07-14",
        "2026-07-28",
    ]
    assert selection["august_identity_snapshot_status"] == ("HTTP_404_NOT_PUBLISHED_AT_PANEL_FREEZE")
    assert (
        cast(dict[str, object], manifest["resource_contract"])["exact_staged_compressed_bytes"]
        == EXPECTED_STAGED_BYTES
    )


def test_any_manifest_content_mutation_is_rejected() -> None:
    manifest = load_panel_manifest(MANIFEST)
    invalid = copy.deepcopy(manifest)
    cast(dict[str, object], invalid["relation_contract"])["allowed_candidate_cardinalities"] = [1, 2, 3]

    errors = validate_panel_manifest(invalid, source_sha256=manifest_sha256(MANIFEST))

    assert "manifest content changed" in errors


def test_day_manifest_assigns_sources_and_date_window() -> None:
    manifest = load_panel_manifest(MANIFEST)
    day = cast(list[dict[str, object]], manifest["days"])[0]

    projected = build_day_manifest(manifest, day)

    objects = cast(list[dict[str, object]], projected["objects"])
    assert [item["object_id"] for item in objects] == [
        "bidmove-2026-06-23",
        "dispatch-2026-06-23",
        "identity-2026-06",
    ]
    time_contract = cast(dict[str, object], projected["time_contract"])
    assert time_contract["market_date_field_value"] == "2026-06-23"
    assert time_contract["dispatch_interval_end_inclusive"] == ("2026-06-24T04:00:00")
    contracts = cast(list[dict[str, object]], projected["table_contracts"])
    sources = {cast(str, item["logical_role"]): item["source_object_id"] for item in contracts}
    assert sources["BIDPEROFFER_D"] == "bidmove-2026-06-23"
    assert sources["DISPATCHLOAD"] == "dispatch-2026-06-23"
    assert sources["DUDETAILSUMMARY"] == "identity-2026-06"


def test_receipt_chain_distinguishes_new_downloads_from_r2_reuse() -> None:
    manifest = load_panel_manifest(MANIFEST)
    download, retention = _receipts(manifest)

    assert validate_download_receipt(download, manifest) == ()
    assert validate_retention_receipt(retention, download, manifest) == ()
    day = cast(list[dict[str, object]], manifest["days"])[0]
    day_download, day_retention = build_day_receipts(manifest, day, download, retention)

    projected = cast(list[dict[str, object]], day_download["objects"])
    assert len(projected) == 3
    assert all(item["download_pass"] is True for item in projected)
    assert len(cast(list[dict[str, object]], day_retention["objects"])) == 3


def test_receipts_reject_source_get_for_reused_identity() -> None:
    manifest = load_panel_manifest(MANIFEST)
    download, retention = _receipts(manifest)
    retained = cast(list[dict[str, object]], retention["objects"])
    retained[-1]["source_get_performed"] = True

    errors = validate_retention_receipt(retention, download, manifest)

    assert any("reuse path" in error for error in errors)


def test_panel_pass_requires_all_four_days() -> None:
    manifest = load_panel_manifest(MANIFEST)
    download, retention = _receipts(manifest)
    days = [
        _day_summary(market_date) for market_date in ("2026-06-23", "2026-06-30", "2026-07-14", "2026-07-28")
    ]

    summary = summarize_panel(
        days,
        manifest,
        download,
        retention,
        source_manifest_sha256=EXPECTED_MANIFEST_SHA256,
        analyzer_git_commit="a" * 40,
        generated_at="2026-08-15T04:42:00Z",
    )

    assert summary["decision"] == "PASS_MODERN_BUNDLE_STABILITY_PANEL"
    assert summary["pass"] is True
    assert all(cast(dict[str, bool], summary["gates"]).values())
    aggregate = cast(dict[str, object], summary["aggregate"])
    assert aggregate["tracker_count"] == 400
    assert aggregate["pair_count"] == 40


def test_one_failed_day_fails_panel_without_pooled_exception() -> None:
    manifest = load_panel_manifest(MANIFEST)
    download, retention = _receipts(manifest)
    days = [
        _day_summary("2026-06-23"),
        _day_summary("2026-06-30"),
        _day_summary("2026-07-14", passed=False),
        _day_summary("2026-07-28"),
    ]

    summary = summarize_panel(
        days,
        manifest,
        download,
        retention,
        source_manifest_sha256=EXPECTED_MANIFEST_SHA256,
        analyzer_git_commit="a" * 40,
        generated_at="2026-08-15T04:42:00Z",
    )

    gates = cast(dict[str, bool], summary["gates"])
    assert gates["all_days_pass"] is False
    assert gates["zero_failed_days"] is False
    assert summary["pass"] is False
