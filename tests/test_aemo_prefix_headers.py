from __future__ import annotations

import copy
import csv
import io
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from ecomd.research.aemo_prefix_headers import (
    audit_prefix_response,
    load_prefix_manifest,
    parse_aemo_zip_prefix,
    summarize_prefix_audit,
    validate_prefix_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/manifests/aemo_prefix_header_audit_v4.yaml"


def _archive(path: Path, *, data_first: bool = False) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    if data_first:
        writer.writerow(["D", "OFFER", "BIDDAYOFFER", "2", "UNIT"])
    writer.writerow(["I", "OFFER", "BIDDAYOFFER", "2", "DUID", "BIDTYPE"])
    writer.writerow(["D", "OFFER", "BIDDAYOFFER", "2", "UNIT", "ENERGY"])
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("PUBLIC_DVD_BIDDAYOFFER_202009010000.CSV", buffer.getvalue())
    return path.read_bytes()


def _spec() -> dict[str, object]:
    return {
        "object_id": "test",
        "sample_label": "r0-prefix-2020-09",
        "month": "2020-09",
        "mechanism_phase": "A0_30_minute_only",
        "observation_phase": "O0_legacy_reports",
        "logical_role": "BIDDAYOFFER",
        "url": "https://www.nemweb.com.au/test.zip",
        "expected_member": "PUBLIC_DVD_BIDDAYOFFER_202009010000.CSV",
        "expected_package": "OFFER",
        "expected_table": "BIDDAYOFFER",
        "expected_version": "2",
        "required_fields": ["DUID", "BIDTYPE"],
    }


def test_frozen_prefix_manifest_is_valid_and_keeps_rows_locked() -> None:
    manifest = load_prefix_manifest(MANIFEST)

    assert validate_prefix_manifest(manifest) == ()
    assert manifest["gates"]["row_access_allowed_after_pass"] is False
    assert manifest["gates"]["full_archive_download_allowed_after_pass"] is False
    assert len(manifest["objects"]) == 10


def test_prefix_manifest_rejects_object_replacement() -> None:
    manifest = load_prefix_manifest(MANIFEST)
    invalid = copy.deepcopy(manifest)
    invalid["objects"][0]["month"] = "2021-03"

    assert any("month changed" in error for error in validate_prefix_manifest(invalid))


def test_zip_prefix_extracts_information_header_without_data_row(tmp_path: Path) -> None:
    parsed = parse_aemo_zip_prefix(_archive(tmp_path / "header.zip"))

    assert parsed["header_package"] == "OFFER"
    assert parsed["header_table"] == "BIDDAYOFFER"
    assert parsed["header_version"] == "2"
    assert parsed["header_fields"] == ["DUID", "BIDTYPE"]
    assert parsed["data_row_opened"] is False


def test_zip_prefix_rejects_data_before_information_header(tmp_path: Path) -> None:
    try:
        parse_aemo_zip_prefix(_archive(tmp_path / "data-first.zip", data_first=True))
    except ValueError as error:
        assert "data row encountered" in str(error)
    else:
        raise AssertionError("data-first archive prefix was accepted")


def test_prefix_audit_requires_exact_header_contract(tmp_path: Path) -> None:
    content = _archive(tmp_path / "header.zip")
    audit = audit_prefix_response(
        _spec(),
        http_status=206,
        content=content,
        response_headers={"Content-Range": f"bytes 0-{len(content) - 1}/{len(content) + 10}"},
        retrieved_at="2026-08-14T10:00:00Z",
        transport_error=None,
    )

    assert audit["zip_prefix_parse"] is True
    assert audit["header_contract_pass"] is True
    assert audit["data_row_opened"] is False


def test_prefix_audit_preserves_wrong_package_failure(tmp_path: Path) -> None:
    content = _archive(tmp_path / "header.zip")
    spec = _spec()
    spec["expected_package"] = "BIDS"
    audit = audit_prefix_response(
        spec,
        http_status=206,
        content=content,
        response_headers={"Content-Range": f"bytes 0-{len(content) - 1}/{len(content) + 10}"},
        retrieved_at="2026-08-14T10:00:00Z",
        transport_error=None,
    )

    assert audit["header_contract_pass"] is False
    assert "header_package OFFER != BIDS" in audit["errors"]


def test_prefix_audit_rejects_range_that_contains_complete_archive(tmp_path: Path) -> None:
    content = _archive(tmp_path / "complete.zip")
    audit = audit_prefix_response(
        _spec(),
        http_status=206,
        content=content,
        response_headers={"Content-Range": f"bytes 0-{len(content) - 1}/{len(content)}"},
        retrieved_at="2026-08-14T10:00:00Z",
        transport_error=None,
    )

    assert audit["zip_prefix_parse"] is True
    assert audit["full_archive_downloaded"] is True
    assert audit["header_contract_pass"] is False
    assert "range response contains the complete archive" in audit["errors"]


def test_prefix_summary_requires_all_ten() -> None:
    audits = [
        {
            "http_status": 206,
            "zip_prefix_parse": True,
            "header_contract_pass": True,
            "response_bytes": 100,
        }
        for _ in range(9)
    ]
    summary = summarize_prefix_audit(
        audits,
        source_manifest="manifest.yaml",
        source_manifest_sha256="a" * 64,
        collector_git_commit="b" * 40,
        generated_at="2026-08-14T10:00:00Z",
    )

    assert summary["pass"] is False
    assert summary["total_response_bytes"] == 900


def test_prefix_summary_fails_when_one_complete_archive_was_transferred() -> None:
    audits = [
        {
            "http_status": 206,
            "zip_prefix_parse": True,
            "header_contract_pass": True,
            "full_archive_downloaded": index == 0,
            "response_bytes": 100,
        }
        for index in range(10)
    ]
    summary = summarize_prefix_audit(
        audits,
        source_manifest="manifest.yaml",
        source_manifest_sha256="a" * 64,
        collector_git_commit="b" * 40,
        generated_at="2026-08-14T10:00:00Z",
    )

    assert summary["pass"] is False
    assert summary["full_archive_downloaded"] is True
