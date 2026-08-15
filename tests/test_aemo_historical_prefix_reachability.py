from __future__ import annotations

import copy
import csv
import hashlib
import io
import struct
import zlib
from pathlib import Path

from ecomd.research.aemo_historical_prefix_reachability import (
    DOWNLOAD_SCHEMA_VERSION,
    RANGE_BYTES,
    RETENTION_SCHEMA_VERSION,
    SOURCE_MANIFEST_PATH,
    load_manifest,
    manifest_sha256,
    parse_offer_prefix,
    summarize_reachability,
    validate_download_receipt,
    validate_manifest,
    validate_retention_receipt,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / SOURCE_MANIFEST_PATH


def _prefix(path: Path) -> None:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    fields = ["SETTLEMENTDATE", "OFFERDATE", "PERIODID", "VERSIONNO", "DUID", "BIDTYPE", "MAXAVAIL"]
    writer.writerow(["I", "OFFER", "BIDPEROFFER", "1", *fields])
    for day in ("2021/01/01 00:00:00", "2021/01/01 00:00:00", "2021/01/02 00:00:00"):
        writer.writerow(
            ["D", "OFFER", "BIDPEROFFER", "1", day, day, "1", "1", "UNIT", "ENERGY", "100"]
        )
    payload = buffer.getvalue().encode()
    compressor = zlib.compressobj(level=6, wbits=-zlib.MAX_WBITS)
    compressed = compressor.compress(payload) + compressor.flush()
    member = b"PUBLIC_DVD_BIDPEROFFER_202101010000.CSV"
    header = struct.pack(
        "<IHHHHHIIIHH",
        0x04034B50,
        20,
        0,
        8,
        0,
        0,
        0,
        len(compressed),
        len(payload),
        len(member),
        0,
    )
    path.write_bytes(header + member + compressed)


def _download(manifest: dict[str, object]) -> dict[str, object]:
    objects = []
    for index, spec in enumerate(manifest["objects"]):
        content = f"prefix-{index}".encode()
        objects.append(
            {
                "request_index": index,
                "request_count": 1,
                "object_id": spec["object_id"],
                "url": spec["url"],
                "retrieved_at": "2026-08-15T06:00:00Z",
                "http_status": 206,
                "response_headers": {
                    "Content-Range": f"bytes 0-{RANGE_BYTES - 1}/{spec['expected_archive_bytes']}"
                },
                "transport_error": None,
                "observed_bytes": RANGE_BYTES,
                "sha256": hashlib.sha256(content).hexdigest(),
                "local_filename": spec["expected_filename"],
                "download_pass": True,
                "zip_opened": False,
                "csv_rows_opened": False,
            }
        )
    return {
        "schema_version": DOWNLOAD_SCHEMA_VERSION,
        "generated_at": "2026-08-15T06:00:00Z",
        "protocol_git_commit": "a" * 40,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": manifest_sha256(MANIFEST),
        "request_policy": "one_fixed_range_get_per_object_no_retry_no_extension",
        "objects": objects,
        "pass": True,
        "zip_opened": False,
        "csv_rows_opened": False,
    }


def _retention(manifest: dict[str, object], download: dict[str, object]) -> dict[str, object]:
    objects = []
    for spec, source in zip(manifest["objects"], download["objects"], strict=True):
        objects.append(
            {
                "object_id": spec["object_id"],
                "r2_key": spec["r2_key"],
                "observed_bytes": source["observed_bytes"],
                "sha256": source["sha256"],
                "remote_content_length": source["observed_bytes"],
                "remote_metadata_sha256": source["sha256"],
                "verified": True,
            }
        )
    return {
        "schema_version": RETENTION_SCHEMA_VERSION,
        "generated_at": "2026-08-15T06:01:00Z",
        "protocol_git_commit": download["protocol_git_commit"],
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": download["source_manifest_sha256"],
        "bucket": "ecophys",
        "objects": objects,
        "all_verified": True,
        "zip_opened": False,
        "csv_rows_opened": False,
    }


def test_frozen_manifest_is_valid_and_keeps_scientific_claims_locked() -> None:
    manifest = load_manifest(MANIFEST)

    assert validate_manifest(manifest) == ()
    assert manifest["selection"]["held_out_status"] == "development_consumed_not_eligible_for_confirmation"
    assert manifest["gates"]["model_claim_allowed"] is False


def test_manifest_rejects_range_extension() -> None:
    invalid = copy.deepcopy(load_manifest(MANIFEST))
    invalid["range_contract"]["range_extension_allowed"] = True

    assert "range contract changed" in validate_manifest(invalid)


def test_receipt_chain_requires_exact_range_and_r2_hashes() -> None:
    manifest = load_manifest(MANIFEST)
    download = _download(manifest)
    retention = _retention(manifest, download)

    assert validate_download_receipt(download, manifest) == ()
    assert validate_retention_receipt(retention, download, manifest) == ()

    invalid = copy.deepcopy(download)
    invalid["objects"][0]["response_headers"]["Content-Range"] = "bytes 0-1/2"
    assert any("Content-Range" in error for error in validate_download_receipt(invalid, manifest))


def test_streaming_parser_reaches_second_chronological_day(tmp_path: Path) -> None:
    path = tmp_path / "prefix.bin"
    _prefix(path)
    spec = load_manifest(MANIFEST)["objects"][0]

    parsed = parse_offer_prefix(path, spec)

    assert parsed["header_package"] == "OFFER"
    assert parsed["header_table"] == "BIDPEROFFER"
    assert parsed["data_row_count"] == 3
    assert parsed["timestamp_parse_rate"] == 1.0
    assert parsed["distinct_market_days"] == ["2021-01-01", "2021-01-02"]
    assert parsed["chronological_non_decreasing"] is True
    assert parsed["first_market_day_complete"] is True
    assert parsed["first_market_day_row_count"] == 2


def test_summary_requires_both_partial_prefixes_to_reach_second_day() -> None:
    manifest = load_manifest(MANIFEST)
    download = _download(manifest)
    retention = _retention(manifest, download)
    parsed = []
    for index, spec in enumerate(manifest["objects"]):
        parsed.append(
            {
                "member": spec["expected_member"],
                "header_package": spec["expected_package"],
                "header_table": spec["expected_table"],
                "header_version": spec["expected_version"],
                "header_fields": spec["required_fields"],
                "data_row_count": 10,
                "timestamp_parse_count": 10,
                "timestamp_parse_rate": 1.0,
                "malformed_row_count": 0,
                "first_market_day": spec["expected_first_market_day"],
                "second_market_day_reached": index == 0,
                "chronological_non_decreasing": True,
                "first_market_day_complete": index == 0,
                "deflate_eof": False,
            }
        )

    summary = summarize_reachability(
        parsed,
        retention,
        manifest,
        source_manifest_sha256="b" * 64,
        analyzer_git_commit="c" * 40,
        generated_at="2026-08-15T06:02:00Z",
    )

    assert summary["decision"] == "FAIL_HISTORICAL_PREFIX_REACHABILITY"
    assert summary["pass"] is False
    assert summary["claim_boundary"]["historical_row_join_validated"] is False
