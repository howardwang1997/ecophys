from __future__ import annotations

import copy
import csv
import io
from pathlib import Path
from typing import cast
from zipfile import ZIP_DEFLATED, ZipFile

from ecomd.research.aemo_row_conformance import (
    DOWNLOAD_SCHEMA_VERSION,
    RETENTION_SCHEMA_VERSION,
    SOURCE_MANIFEST_PATH,
    load_row_conformance_manifest,
    parse_mmsdm_archive,
    summarize_row_conformance,
    table_contracts_by_role,
    validate_download_receipt,
    validate_retention_receipt,
    validate_row_conformance_manifest,
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
        "generated_at": "2026-08-15T04:00:00Z",
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
        "generated_at": "2026-08-15T04:01:00Z",
        "protocol_git_commit": "a" * 40,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": "b" * 64,
        "bucket": "ecophys",
        "prefix": "raw/aemo/v14_row_conformance/market_date=2026-06-16/",
        "objects": retained,
        "all_verified": True,
        "zip_opened": False,
        "csv_rows_opened": False,
    }
    return download, retention


def _tables() -> dict[str, list[dict[str, str]]]:
    offer_date = "2026/06/15 12:00:00"
    bid_date = "2026/06/16 00:00:00"
    interval = "2026/06/16 04:05:00"
    return {
        "BIDDAYOFFER_D": [
            {
                "SETTLEMENTDATE": bid_date,
                "DUID": "UNIT1",
                "BIDTYPE": "ENERGY",
                "DIRECTION": "GEN",
                "BIDSETTLEMENTDATE": bid_date,
                "OFFERDATE": offer_date,
                "PARTICIPANTID": "P1",
            }
        ],
        "BIDPEROFFER_D": [
            {
                "SETTLEMENTDATE": bid_date,
                "DUID": "UNIT1",
                "BIDTYPE": "ENERGY",
                "DIRECTION": "GEN",
                "INTERVAL_DATETIME": interval,
                "BIDSETTLEMENTDATE": bid_date,
                "OFFERDATE": offer_date,
                "VERSIONNO": "1",
                "MAXAVAIL": "100",
            }
        ],
        "DISPATCHOFFERTRK": [
            {
                "SETTLEMENTDATE": interval,
                "DUID": "UNIT1",
                "BIDTYPE": "ENERGY",
                "BIDSETTLEMENTDATE": bid_date,
                "BIDOFFERDATE": offer_date,
            }
        ],
        "DISPATCHLOAD": [
            {
                "SETTLEMENTDATE": interval,
                "RUNNO": "1",
                "DUID": "UNIT1",
                "INTERVENTION": "0",
                "INITIALMW": "50",
                "TOTALCLEARED": "55",
            }
        ],
        "DUDETAILSUMMARY": [
            {
                "DUID": "UNIT1",
                "START_DATE": "2020/01/01 00:00:00",
                "END_DATE": "2030/01/01 00:00:00",
                "DISPATCHTYPE": "GENERATOR",
                "REGIONID": "NSW1",
                "PARTICIPANTID": "P1",
                "DISPATCHSUBTYPE": "SCHEDULED GENERATOR",
            }
        ],
    }


def _observations() -> list[dict[str, object]]:
    roles = (("BIDDAYOFFER_D", "BIDPEROFFER_D"), ("DISPATCHOFFERTRK", "DISPATCHLOAD"), ("DUDETAILSUMMARY",))
    observations: list[dict[str, object]] = []
    for index, archive_roles in enumerate(roles):
        observations.append(
            {
                "pass": True,
                "zip_crc_pass": True,
                "exact_byte_match": True,
                "total_data_rows": len(archive_roles),
                "headers": [
                    {
                        "logical_role": role,
                        "header_present": True,
                        "missing_required_fields": [],
                    }
                    for role in archive_roles
                ],
                "object_id": f"object-{index}",
            }
        )
    return observations


def test_frozen_manifest_is_valid_and_uses_mechanical_non_target_date() -> None:
    manifest = load_row_conformance_manifest(MANIFEST)

    assert validate_row_conformance_manifest(manifest) == ()
    selection = cast(dict[str, object], manifest["selection"])
    assert selection["selected_market_date"] == "2026-06-16"
    assert selection["target_event"] is False
    assert cast(dict[str, object], manifest["resource_contract"])["gpu_allowed"] is False


def test_manifest_rejects_source_or_threshold_mutation() -> None:
    invalid = copy.deepcopy(load_row_conformance_manifest(MANIFEST))
    cast(list[dict[str, object]], invalid["objects"])[0]["expected_bytes"] = 1
    cast(dict[str, object], invalid["gates"])["tracker_period_match_rate_min"] = 0.0

    errors = validate_row_conformance_manifest(invalid)

    assert any("expected_bytes" in error for error in errors)
    assert "gates changed" in errors


def test_parser_reads_only_contracted_mmsdm_table(tmp_path: Path) -> None:
    manifest = load_row_conformance_manifest(MANIFEST)
    contract = table_contracts_by_role(manifest)["BIDDAYOFFER_D"]
    fields = cast(list[str], contract["required_fields"])
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["I", "IGNORED", "TABLE", "1", "FIELD"])
    writer.writerow(["D", "IGNORED", "TABLE", "1", "value"])
    writer.writerow(["I", "BID", "BIDDAYOFFER_D", "3", *fields])
    writer.writerow(
        [
            "D",
            "BID",
            "BIDDAYOFFER_D",
            "3",
            "2026/06/16 00:00:00",
            "UNIT1",
            "ENERGY",
            "GEN",
            "2026/06/16 00:00:00",
            "2026/06/15 12:00:00",
            "P1",
        ]
    )
    archive_path = tmp_path / "sample.zip"
    with ZipFile(archive_path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("sample.CSV", output.getvalue())

    tables, observation = parse_mmsdm_archive(
        archive_path,
        [contract],
        maximum_uncompressed_bytes=100_000,
        maximum_data_rows=10,
    )

    assert observation["pass"] is True
    assert observation["zip_crc_pass"] is True
    assert observation["total_data_rows"] == 2
    assert len(tables["BIDDAYOFFER_D"]) == 1
    assert tables["BIDDAYOFFER_D"][0]["DUID"] == "UNIT1"


def test_end_to_end_synthetic_conformance_passes_all_frozen_gates() -> None:
    manifest = load_row_conformance_manifest(MANIFEST)
    download, retention = _receipts(manifest)

    assert validate_download_receipt(download, manifest) == ()
    assert validate_retention_receipt(retention, download, manifest) == ()
    summary = summarize_row_conformance(
        _tables(),
        _observations(),
        manifest,
        download,
        retention,
        source_manifest_sha256="b" * 64,
        analyzer_git_commit="a" * 40,
        generated_at="2026-08-15T04:02:00Z",
    )

    assert summary["decision"] == "PASS_MODERN_ROW_CONFORMANCE_SMOKE"
    assert summary["pass"] is True
    assert all(cast(dict[str, bool], summary["gates"]).values())


def test_duplicate_primary_key_fails_without_changing_other_rows() -> None:
    manifest = load_row_conformance_manifest(MANIFEST)
    download, retention = _receipts(manifest)
    tables = _tables()
    tables["BIDDAYOFFER_D"].append(dict(tables["BIDDAYOFFER_D"][0]))

    summary = summarize_row_conformance(
        tables,
        _observations(),
        manifest,
        download,
        retention,
        source_manifest_sha256="b" * 64,
        analyzer_git_commit="a" * 40,
        generated_at="2026-08-15T04:02:00Z",
    )

    gates = cast(dict[str, bool], summary["gates"])
    assert gates["primary_key_uniqueness"] is False
    assert summary["pass"] is False


def test_receipts_reject_content_access_before_r2_retention() -> None:
    manifest = load_row_conformance_manifest(MANIFEST)
    download, retention = _receipts(manifest)
    download["zip_opened"] = True
    retention["csv_rows_opened"] = True

    assert any("content access" in error for error in validate_download_receipt(download, manifest))
    assert any(
        "content access" in error for error in validate_retention_receipt(retention, download, manifest)
    )
