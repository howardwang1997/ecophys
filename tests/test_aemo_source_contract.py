from __future__ import annotations

import copy
import csv
import io
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from ecomd.research.aemo_source_contract import (
    adjacent_complete_month,
    audit_source_contract_response,
    load_source_contract_manifest,
    summarize_source_contract_audit,
    validate_source_contract_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/manifests/aemo_source_contract_v1.yaml"


def _archive(path: Path, fields: list[str]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["I", "DISPATCH", "UNIT_SOLUTION", "2", *fields])
    writer.writerow(["D", "DISPATCH", "UNIT_SOLUTION", "2", *["0"] * len(fields)])
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("PUBLIC_DVD_DISPATCHLOAD_202102010000.CSV", buffer.getvalue())
    return path.read_bytes()


def _spec() -> dict[str, object]:
    return {
        "object_id": "test",
        "sample_label": "pre-bridge-prefix-2021-02",
        "month": "2021-02",
        "mechanism_phase": "A0_30_MINUTE_ONLY",
        "observation_phase": "O0_LEGACY_REPORTS",
        "version_basis": "PRE_REPORTING_BRIDGE",
        "delivery_channel": "PUBLIC_MONTHLY_ARCHIVE",
        "archive_family": "MMSDM_Historical_Data_SQLLoader/PUBLIC_DVD",
        "archive_file_id": "PUBLIC_DVD_DISPATCHLOAD",
        "logical_role": "DISPATCHLOAD",
        "sensitivity_class": "FAST_START_STATE_OBSERVABILITY",
        "url": "https://www.nemweb.com.au/test.zip",
        "expected_member": "PUBLIC_DVD_DISPATCHLOAD_202102010000.CSV",
        "expected_package": "DISPATCH",
        "expected_table": "UNIT_SOLUTION",
        "expected_version": "2",
        "required_fields": ["DUID", "SETTLEMENTDATE"],
        "forbidden_fields": ["DISPATCHMODETIME"],
    }


def test_adjacent_month_selection_is_boundary_deterministic() -> None:
    assert adjacent_complete_month("2021-03-08", "before") == "2021-02"
    assert adjacent_complete_month("2021-10-24", "after") == "2021-11"


def test_source_contract_manifest_is_valid_and_keeps_data_locked() -> None:
    manifest = load_source_contract_manifest(MANIFEST)

    assert validate_source_contract_manifest(manifest) == ()
    assert manifest["gates"]["row_access_allowed_after_pass"] is False
    assert manifest["gates"]["gpu_allowed"] is False
    assert len(manifest["objects"]) == 10


def test_source_contract_rejects_channel_transfer() -> None:
    invalid = copy.deepcopy(load_source_contract_manifest(MANIFEST))
    invalid["objects"][0]["delivery_channel"] = "NEXT_DAY_OFFER_ENERGY"

    assert any("delivery_channel changed" in error for error in validate_source_contract_manifest(invalid))


def test_source_contract_rejects_version_relaxation() -> None:
    invalid = copy.deepcopy(load_source_contract_manifest(MANIFEST))
    invalid["objects"][1]["expected_version"] = "2"

    assert any("expected_version changed" in error for error in validate_source_contract_manifest(invalid))


def test_source_contract_rejects_report_shape_interface_proxy() -> None:
    invalid = copy.deepcopy(load_source_contract_manifest(MANIFEST))
    invalid["provenance_limits"]["public_report_shape_as_interface_proxy_allowed"] = True

    assert "provenance limits changed" in validate_source_contract_manifest(invalid)


def test_source_contract_rejects_missing_v51_observable() -> None:
    invalid = copy.deepcopy(load_source_contract_manifest(MANIFEST))
    invalid["objects"][8]["required_fields"].remove("DISPATCHMODETIME")

    assert any("required_fields changed" in error for error in validate_source_contract_manifest(invalid))


def test_source_response_rejects_pre_v51_dynamic_state_field(tmp_path: Path) -> None:
    content = _archive(tmp_path / "unexpected-state.zip", ["DUID", "SETTLEMENTDATE", "DISPATCHMODETIME"])
    audit = audit_source_contract_response(
        _spec(),
        http_status=206,
        content=content,
        response_headers={"Content-Range": f"bytes 0-{len(content) - 1}/{len(content)}"},
        retrieved_at="2026-08-14T15:00:00Z",
        transport_error=None,
    )

    assert audit["zip_prefix_parse"] is True
    assert audit["source_contract_pass"] is False
    assert audit["forbidden_fields_present"] == ["DISPATCHMODETIME"]


def test_source_summary_requires_all_ten_contracts() -> None:
    audits = [
        {
            "http_status": 206,
            "zip_prefix_parse": True,
            "source_contract_pass": True,
            "forbidden_fields_present": [],
            "response_bytes": 100,
        }
        for _ in range(9)
    ]
    summary = summarize_source_contract_audit(
        audits,
        source_manifest="manifest.yaml",
        source_manifest_sha256="a" * 64,
        collector_git_commit="b" * 40,
        generated_at="2026-08-14T15:00:00Z",
    )

    assert summary["pass"] is False
    assert summary["total_response_bytes"] == 900
