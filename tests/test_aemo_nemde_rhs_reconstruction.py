from __future__ import annotations

import copy
import hashlib
import io
import zipfile
from pathlib import Path

from ecomd.research.aemo_nemde_rhs_reconstruction import (
    MATERIALIZATION_SCHEMA_VERSION,
    RANGE_BYTES,
    SOURCE_MANIFEST_PATH,
    extract_member_xml,
    load_manifest,
    manifest_sha256,
    score_case,
    seal_reference_and_make_sentinels,
    summarize_reconstruction,
    validate_manifest,
    validate_materialization_receipt,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / SOURCE_MANIFEST_PATH


def _materialization(manifest: dict[str, object]) -> dict[str, object]:
    objects = []
    for spec in manifest["objects"]:
        objects.append(
            {
                "object_id": spec["object_id"],
                "r2_key": spec["r2_key"],
                "local_filename": spec["expected_filename"],
                "remote_content_length": RANGE_BYTES,
                "remote_metadata_sha256": spec["range_sha256"],
                "remote_etag": "etag",
                "local_bytes": RANGE_BYTES,
                "local_sha256": spec["range_sha256"],
                "verified": True,
                "local_header_opened": False,
                "xml_opened": False,
            }
        )
    return {
        "schema_version": MATERIALIZATION_SCHEMA_VERSION,
        "generated_at": "2026-08-15T07:00:00Z",
        "protocol_git_commit": "a" * 40,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": manifest_sha256(MANIFEST),
        "bucket": "ecophys",
        "new_aemo_request_count": 0,
        "objects": objects,
        "all_verified": True,
    }


def _synthetic_range(path: Path) -> tuple[dict[str, object], bytes]:
    xml = b"<NEMSPDCaseFile><NemSpdInputs/><NemSpdOutputs/></NEMSPDCaseFile>"
    member_name = "NEMSPDOutputs_2021010114400.loaded"
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member_name, xml)
    archive_bytes = buffer.getvalue()
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        info = archive.getinfo(member_name)
    path.write_bytes((archive_bytes + b"\x00" * RANGE_BYTES)[:RANGE_BYTES])
    return (
        {
            "member_name": member_name,
            "member_flags": info.flag_bits,
            "compression_method": info.compress_type,
            "crc32": f"{info.CRC:08x}",
            "compressed_bytes": info.compress_size,
            "uncompressed_bytes": info.file_size,
            "xml_sha256": hashlib.sha256(xml).hexdigest(),
        },
        xml,
    )


def _document() -> dict[str, object]:
    return {
        "NEMSPDCaseFile": {
            "NemSpdInputs": {"Keep": "unchanged"},
            "NemSpdOutputs": {
                "ConstraintSolution": [
                    {"@ConstraintID": "A", "@Intervention": "0", "@RHS": "10"},
                    {"@ConstraintID": "A", "@Intervention": "1", "@RHS": "11"},
                    {"@ConstraintID": "B", "@Intervention": "0", "@RHS": "-2"},
                ]
            },
        }
    }


def _successful_results() -> list[dict[str, object]]:
    return [
        {"constraint_id": "A", "status": "ok", "value": 10.0, "value_hex": (10.0).hex()},
        {"constraint_id": "B", "status": "ok", "value": -2.0, "value_hex": (-2.0).hex()},
    ]


def test_manifest_is_exact_r2_only_and_keeps_replay_locked() -> None:
    manifest = load_manifest(MANIFEST)

    assert validate_manifest(manifest) == ()
    assert manifest["source_access_contract"]["new_aemo_request_count"] == 0
    assert manifest["claim_locks"]["full_input_only_replay_claim_allowed"] is False


def test_manifest_rejects_source_fallback_or_threshold_change() -> None:
    invalid = copy.deepcopy(load_manifest(MANIFEST))
    invalid["source_access_contract"]["source_fallback_allowed"] = True
    invalid["metrics"]["per_case_gates"]["minimum_evaluation_coverage"] = 0.5

    errors = validate_manifest(invalid)

    assert "source access contract changed" in errors
    assert "metric contract changed" in errors


def test_materialization_requires_exact_r2_hashes_and_no_content_access() -> None:
    manifest = load_manifest(MANIFEST)
    receipt = _materialization(manifest)

    assert validate_materialization_receipt(receipt, manifest) == ()

    invalid = copy.deepcopy(receipt)
    invalid["objects"][0]["xml_opened"] = True
    assert any("accessed content" in error for error in validate_materialization_receipt(invalid, manifest))


def test_extract_member_reproduces_header_deflate_crc_and_xml_sha(tmp_path: Path) -> None:
    path = tmp_path / "range.bin"
    spec, expected = _synthetic_range(path)

    assert extract_member_xml(path, spec) == expected


def test_seal_reference_replaces_every_output_rhs_without_mutating_input() -> None:
    document = _document()
    references, left, right, count = seal_reference_and_make_sentinels(document)

    assert references == {"A": 10.0, "B": -2.0}
    assert count == 3
    assert document["NEMSPDCaseFile"]["NemSpdInputs"] == {"Keep": "unchanged"}
    assert {row["@RHS"] for row in left["NEMSPDCaseFile"]["NemSpdOutputs"]["ConstraintSolution"]} == {
        "-1e100"
    }
    assert {row["@RHS"] for row in right["NEMSPDCaseFile"]["NemSpdOutputs"]["ConstraintSolution"]} == {
        "1e100"
    }


def test_score_passes_exact_dual_sentinel_predictions_and_frozen_errors() -> None:
    spec = {"object_id": "case", "market_date": "2021-01-01", "mechanism_phase": "A0"}
    results = _successful_results()

    scored = score_case(spec, {"A": 10.0, "B": -2.0}, results, copy.deepcopy(results), 3)

    assert scored["pass"] is True
    assert scored["evaluation_coverage"] == 1.0
    assert scored["errors"]["normalized_p95"] == 0.0


def test_score_rejects_sentinel_value_dependence_without_dropping_equation() -> None:
    spec = {"object_id": "case", "market_date": "2021-01-01", "mechanism_phase": "A0"}
    left = _successful_results()
    right = copy.deepcopy(left)
    right[0]["value"] = 9.0
    right[0]["value_hex"] = (9.0).hex()

    scored = score_case(spec, {"A": 10.0, "B": -2.0}, left, right, 3)

    assert scored["pass"] is False
    assert scored["sentinel_success_value_match_rate"] == 0.5
    assert scored["failed_constraint_ids"] == ["A"]


def test_aggregate_pass_still_locks_full_replay_and_gpu() -> None:
    manifest = load_manifest(MANIFEST)
    receipt = _materialization(manifest)
    spec = {"object_id": "case", "market_date": "2021-01-01", "mechanism_phase": "A0"}
    results = _successful_results()
    case = score_case(spec, {"A": 10.0, "B": -2.0}, results, copy.deepcopy(results), 3)

    summary = summarize_reconstruction(
        [case, copy.deepcopy(case)],
        receipt,
        {"pass": True, "observed_commit": "b" * 40},
        source_manifest_sha256="c" * 64,
        analyzer_git_commit="d" * 40,
        generated_at="2026-08-15T07:01:00Z",
    )

    assert summary["decision"] == "PASS_INPUT_SIDE_DYNAMIC_RHS_RECONSTRUCTION"
    assert summary["claim_boundary"]["full_input_only_replay_validated"] is False
    assert summary["resources"]["gpu_hours"] == 0
