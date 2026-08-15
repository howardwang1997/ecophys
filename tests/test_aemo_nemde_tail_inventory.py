from __future__ import annotations

import copy
import hashlib
import io
import zipfile
from pathlib import Path

from ecomd.research.aemo_nemde_tail_inventory import (
    DOWNLOAD_SCHEMA_VERSION,
    RETENTION_SCHEMA_VERSION,
    SOURCE_MANIFEST_PATH,
    TAIL_BYTES,
    load_manifest,
    manifest_sha256,
    parse_zip_tail,
    summarize_inventory,
    validate_download_receipt,
    validate_manifest,
    validate_retention_receipt,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / SOURCE_MANIFEST_PATH


def _synthetic_tail(path: Path) -> tuple[int, dict[str, object]]:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("padding.bin", b"x" * (TAIL_BYTES + 4096))
        for interval in range(1, 289):
            archive.writestr(
                f"NemSpdOutputs_20210101{interval:03d}00.loaded",
                f"interval={interval}".encode(),
            )
    payload = buffer.getvalue()
    path.write_bytes(payload[-TAIL_BYTES:])
    return len(payload), {
        "object_id": "synthetic",
        "expected_archive_bytes": len(payload),
        "expected_member_date": "20210101",
    }


def _download(manifest: dict[str, object]) -> dict[str, object]:
    objects = []
    for index, spec in enumerate(manifest["objects"]):
        total = spec["expected_archive_bytes"]
        objects.append(
            {
                "request_index": index,
                "request_count": 1,
                "object_id": spec["object_id"],
                "url": spec["url"],
                "retrieved_at": "2026-08-15T06:20:00Z",
                "http_status": 206,
                "response_headers": {
                    "Content-Range": f"bytes {total - TAIL_BYTES}-{total - 1}/{total}"
                },
                "transport_error": None,
                "observed_bytes": TAIL_BYTES,
                "sha256": hashlib.sha256(f"tail-{index}".encode()).hexdigest(),
                "local_filename": spec["expected_filename"],
                "download_pass": True,
                "zip_metadata_opened": False,
                "xml_member_opened": False,
            }
        )
    return {
        "schema_version": DOWNLOAD_SCHEMA_VERSION,
        "generated_at": "2026-08-15T06:20:00Z",
        "protocol_git_commit": "a" * 40,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": manifest_sha256(MANIFEST),
        "request_policy": "one_fixed_suffix_range_per_object_no_retry_no_extension",
        "objects": objects,
        "pass": True,
        "zip_metadata_opened": False,
        "xml_member_opened": False,
    }


def _retention(manifest: dict[str, object], download: dict[str, object]) -> dict[str, object]:
    objects = []
    for spec, source in zip(manifest["objects"], download["objects"], strict=True):
        objects.append(
            {
                "object_id": spec["object_id"],
                "r2_key": spec["r2_key"],
                "observed_bytes": TAIL_BYTES,
                "sha256": source["sha256"],
                "remote_content_length": TAIL_BYTES,
                "remote_metadata_sha256": source["sha256"],
                "verified": True,
            }
        )
    return {
        "schema_version": RETENTION_SCHEMA_VERSION,
        "generated_at": "2026-08-15T06:21:00Z",
        "protocol_git_commit": download["protocol_git_commit"],
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": download["source_manifest_sha256"],
        "bucket": "ecophys",
        "prefix": "raw/aemo/v14_nemde_tail_inventory/",
        "objects": objects,
        "all_verified": True,
        "zip_metadata_opened": False,
        "xml_member_opened": False,
    }


def test_manifest_is_valid_and_keeps_claims_and_redistribution_locked() -> None:
    manifest = load_manifest(MANIFEST)

    assert validate_manifest(manifest) == ()
    assert manifest["gates"]["model_claim_allowed"] is False
    assert manifest["source_contract"]["raw_redistribution_allowed_by_this_protocol"] is False


def test_manifest_rejects_xml_access_and_range_extension() -> None:
    manifest = load_manifest(MANIFEST)
    invalid = copy.deepcopy(manifest)
    invalid["range_contract"]["xml_member_access_allowed"] = True

    assert "range contract changed" in validate_manifest(invalid)


def test_receipt_chain_requires_exact_suffix_and_r2_hash() -> None:
    manifest = load_manifest(MANIFEST)
    download = _download(manifest)
    retention = _retention(manifest, download)

    assert validate_download_receipt(download, manifest) == ()
    assert validate_retention_receipt(retention, download, manifest) == ()

    invalid = copy.deepcopy(download)
    invalid["objects"][0]["response_headers"]["Content-Range"] = "bytes 0-1/2"
    assert any("Content-Range" in error for error in validate_download_receipt(invalid, manifest))


def test_tail_parser_recovers_complete_288_interval_inventory(tmp_path: Path) -> None:
    path = tmp_path / "tail.bin"
    _, spec = _synthetic_tail(path)

    parsed = parse_zip_tail(path, spec)

    assert parsed["central_directory_complete"] is True
    assert parsed["member_count"] == 289
    assert parsed["matching_member_count"] == 288
    assert parsed["complete_interval_set"] is True
    assert parsed["target_candidate_count"] == 1
    assert parsed["target_range_within_cap"] is True


def test_summary_requires_both_archives_and_keeps_semantic_claims_locked() -> None:
    manifest = load_manifest(MANIFEST)
    download = _download(manifest)
    retention = _retention(manifest, download)
    parsed = [
        {
            "eocd_found": True,
            "central_directory_complete": True,
            "complete_interval_set": True,
            "target_range_within_cap": True,
            "encrypted_member_count": 0,
            "unsupported_compression_member_count": 0,
            "wrong_member_date_count": 0,
        }
        for _ in range(2)
    ]

    summary = summarize_inventory(
        parsed,
        retention,
        manifest,
        source_manifest_sha256="b" * 64,
        analyzer_git_commit="c" * 40,
        generated_at="2026-08-15T06:22:00Z",
    )

    assert summary["decision"] == "PASS_NEMDE_TAIL_INVENTORY"
    assert summary["claim_boundary"]["xml_schema_validated"] is False
    assert summary["claim_boundary"]["raw_redistribution_allowed"] is False
