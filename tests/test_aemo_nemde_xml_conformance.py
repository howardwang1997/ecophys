from __future__ import annotations

import copy
import hashlib
import io
import zipfile
from pathlib import Path

from ecomd.research.aemo_nemde_xml_conformance import (
    DOWNLOAD_SCHEMA_VERSION,
    RANGE_BYTES,
    RETENTION_SCHEMA_VERSION,
    SOURCE_MANIFEST_PATH,
    load_manifest,
    manifest_sha256,
    parse_member_range,
    summarize_conformance,
    validate_download_receipt,
    validate_manifest,
    validate_retention_receipt,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / SOURCE_MANIFEST_PATH


def _xml_range(path: Path) -> dict[str, object]:
    xml = b"""<?xml version="1.0"?>
<NEMSPDCaseFile>
  <NemSpdInputs PriceBand1="1" BandAvail1="2" MaxAvail="3" RampUpRate="4" RampDnRate="5">
    <Case/><RegionCollection/><TraderCollection/><PeriodCollection/>
    <InterconnectorCollection/><GenericConstraintCollection/>
  </NemSpdInputs>
  <NemSpdOutputs>
    <CaseSolution/><PeriodSolution/><RegionSolution/><InterconnectorSolution/>
    <TraderSolution/><ConstraintSolution/>
  </NemSpdOutputs>
  <SolutionAnalysis><PriceSetting/></SolutionAnalysis>
</NEMSPDCaseFile>"""
    buffer = io.BytesIO()
    member_name = "NEMSPDOutputs_2021010114400.loaded"
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member_name, xml)
    archive_bytes = buffer.getvalue()
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        info = archive.getinfo(member_name)
    payload = archive_bytes + b"\x00" * (RANGE_BYTES - len(archive_bytes))
    path.write_bytes(payload[:RANGE_BYTES])
    return {
        "object_id": "synthetic",
        "member_name": member_name,
        "member_flags": info.flag_bits,
        "compression_method": info.compress_type,
        "crc32": f"{info.CRC:08x}",
        "compressed_bytes": info.compress_size,
        "uncompressed_bytes": info.file_size,
    }


def _download(manifest: dict[str, object]) -> dict[str, object]:
    objects = []
    for index, spec in enumerate(manifest["objects"]):
        objects.append(
            {
                "request_index": index,
                "request_count": 1,
                "object_id": spec["object_id"],
                "url": spec["url"],
                "retrieved_at": "2026-08-15T06:35:00Z",
                "http_status": 206,
                "response_headers": {
                    "Content-Range": (
                        f"bytes {spec['range_start']}-{spec['range_end']}/"
                        f"{spec['expected_archive_bytes']}"
                    )
                },
                "transport_error": None,
                "observed_bytes": RANGE_BYTES,
                "sha256": hashlib.sha256(f"range-{index}".encode()).hexdigest(),
                "local_filename": spec["expected_filename"],
                "download_pass": True,
                "local_header_opened": False,
                "xml_opened": False,
            }
        )
    return {
        "schema_version": DOWNLOAD_SCHEMA_VERSION,
        "generated_at": "2026-08-15T06:35:00Z",
        "protocol_git_commit": "a" * 40,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": manifest_sha256(MANIFEST),
        "request_policy": "one_exact_member_range_per_object_no_retry_no_extension",
        "objects": objects,
        "pass": True,
        "local_header_opened": False,
        "xml_opened": False,
    }


def _retention(manifest: dict[str, object], download: dict[str, object]) -> dict[str, object]:
    objects = []
    for spec, source in zip(manifest["objects"], download["objects"], strict=True):
        objects.append(
            {
                "object_id": spec["object_id"],
                "r2_key": spec["r2_key"],
                "observed_bytes": RANGE_BYTES,
                "sha256": source["sha256"],
                "remote_content_length": RANGE_BYTES,
                "remote_metadata_sha256": source["sha256"],
                "verified": True,
            }
        )
    return {
        "schema_version": RETENTION_SCHEMA_VERSION,
        "generated_at": "2026-08-15T06:36:00Z",
        "protocol_git_commit": download["protocol_git_commit"],
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": download["source_manifest_sha256"],
        "bucket": "ecophys",
        "prefix": "raw/aemo/v14_nemde_xml_conformance/",
        "objects": objects,
        "all_verified": True,
        "local_header_opened": False,
        "xml_opened": False,
    }


def test_manifest_is_valid_and_keeps_all_scientific_claims_locked() -> None:
    manifest = load_manifest(MANIFEST)

    assert validate_manifest(manifest) == ()
    assert manifest["selection"]["interval_id"] == 144
    assert manifest["gates"]["exact_solver_replay_claim_allowed"] is False


def test_manifest_rejects_retry_or_following_member_access() -> None:
    invalid = copy.deepcopy(load_manifest(MANIFEST))
    invalid["range_contract"]["retry_allowed"] = True

    assert "range contract changed" in validate_manifest(invalid)


def test_receipt_chain_requires_exact_range_and_r2_hashes() -> None:
    manifest = load_manifest(MANIFEST)
    download = _download(manifest)
    retention = _retention(manifest, download)

    assert validate_download_receipt(download, manifest) == ()
    assert validate_retention_receipt(retention, download, manifest) == ()

    invalid = copy.deepcopy(download)
    invalid["objects"][0]["observed_bytes"] = 1
    assert any("bytes or SHA" in error for error in validate_download_receipt(invalid, manifest))


def test_member_parser_validates_deflate_crc_and_documented_sections(tmp_path: Path) -> None:
    path = tmp_path / "member-range.bin"
    spec = _xml_range(path)

    parsed = parse_member_range(path, spec)

    assert parsed["local_header_pass"] is True
    assert parsed["deflate_eof"] is True
    assert parsed["crc_pass"] is True
    assert parsed["xml_parse_pass"] is True
    assert parsed["section_contract_pass"] is True
    assert parsed["input_group_contract_pass"] is True
    assert parsed["output_group_contract_pass"] is True
    assert parsed["nonempty_price_section_pass"] is True
    assert parsed["action_attribute_vocabulary_present"] == [
        "BandAvail1",
        "MaxAvail",
        "PriceBand1",
        "RampDnRate",
        "RampUpRate",
    ]


def test_summary_requires_both_cases_and_keeps_replay_locked() -> None:
    manifest = load_manifest(MANIFEST)
    download = _download(manifest)
    retention = _retention(manifest, download)
    parsed = [
        {
            "local_header_pass": True,
            "deflate_eof": True,
            "crc_pass": True,
            "xml_parse_pass": True,
            "section_contract_pass": True,
            "input_group_contract_pass": True,
            "output_group_contract_pass": True,
            "nonempty_price_section_pass": True,
            "input_attribute_names": ["MaxAvail"],
            "output_attribute_names": ["EnergyPrice"],
            "price_attribute_names": ["Price"],
        }
        for _ in range(2)
    ]

    summary = summarize_conformance(
        parsed,
        retention,
        manifest,
        source_manifest_sha256="b" * 64,
        analyzer_git_commit="c" * 40,
        generated_at="2026-08-15T06:37:00Z",
    )

    assert summary["decision"] == "PASS_NEMDE_XML_CONFORMANCE"
    assert summary["claim_boundary"]["exact_solver_replay_validated"] is False
    assert summary["claim_boundary"]["raw_redistribution_allowed"] is False
