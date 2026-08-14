from __future__ import annotations

import csv
import io
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from ecomd.research.aemo_development_audit import (
    build_header_contract,
    inspect_aemo_archive,
    load_aemo_object_manifest,
    summarize_header_audit,
    validate_aemo_object_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/manifests/aemo_development_objects_v1.yaml"


def test_frozen_aemo_object_manifest_is_valid() -> None:
    manifest = load_aemo_object_manifest(MANIFEST)

    assert validate_aemo_object_manifest(manifest) == ()
    assert manifest["full_month_bundle_allowed"] is False
    assert manifest["no_object_replacement"] is True


def _archive(path: Path) -> tuple[Path, dict[str, object]]:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["C", "Synthetic"])
    writer.writerow(["I", "DISPATCH", "DISPATCHLOAD", "3", "SETTLEMENTDATE", "RUNNO", "DUID", "INTERVENTION"])
    writer.writerow(["D", "DISPATCH", "DISPATCHLOAD", "3", "2025/01/07 04:05:00", "1", "UNIT", "0"])
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("PUBLIC_DISPATCHLOAD.CSV", buffer.getvalue())
    spec: dict[str, object] = {
        "object_id": "object-1",
        "sample_label": "current-2025-01",
        "market_date": "2025-01-07",
        "logical_role": "DISPATCHLOAD",
        "archive_table": "DISPATCHLOAD",
        "url": "https://www.nemweb.com.au/DATA/object.zip",
        "expected_bytes": path.stat().st_size,
        "minimum_header_fields": ["SETTLEMENTDATE", "RUNNO", "DUID", "INTERVENTION"],
    }
    return path, spec


def test_archive_header_and_crc_are_audited_without_counting_rows(tmp_path: Path) -> None:
    path, spec = _archive(tmp_path / "sample.zip")

    audit = inspect_aemo_archive(path, spec)

    assert audit["header_pass"] is True
    assert audit["bad_crc_member"] is None
    assert audit["zip_crc_pass"] is True
    assert audit["header_table"] == "DISPATCHLOAD"
    assert audit["row_count_opened"] is False


def test_missing_header_field_fails_and_propagates_to_summary(tmp_path: Path) -> None:
    path, spec = _archive(tmp_path / "sample.zip")
    spec["minimum_header_fields"] = ["SETTLEMENTDATE", "NOT_A_FIELD"]

    audit = inspect_aemo_archive(path, spec)
    download = {
        "http_status": 200,
        "observed_bytes": path.stat().st_size,
        "expected_bytes": path.stat().st_size,
        "sha256": "a" * 64,
    }
    summary = summarize_header_audit(
        [download],
        [audit],
        expected_count=1,
        download_ledger_sha256="b" * 64,
    )

    assert audit["header_pass"] is False
    assert summary["pass"] is False


def test_header_contract_keeps_rows_and_joins_locked(tmp_path: Path) -> None:
    path, spec = _archive(tmp_path / "sample.zip")
    audit = inspect_aemo_archive(path, spec)

    contract = build_header_contract(
        [audit],
        source_manifest="data/manifests/aemo_development_objects_v1.yaml",
        source_manifest_sha256="a" * 64,
        generated_at="2026-08-14T07:30:00Z",
        generator_git_commit="b" * 40,
    )

    assert contract["row_counts_opened"] is False
    assert contract["row_join_authorized"] is False
    assert contract["all_headers_pass"] is False
