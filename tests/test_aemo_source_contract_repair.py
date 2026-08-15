from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from ecomd.research.aemo_source_contract_repair import (
    PREFIX_PROOF_SHA256,
    RANGE_BYTES,
    audit_source_contract_repair_response,
    load_source_contract_manifest,
    nearest_unconsumed_complete_month,
    summarize_source_contract_repair_audit,
    validate_source_contract_repair_manifest,
)
from experiments.v14_aemo_source_contract_repair.prove_prefix_budget import (
    SYNTHETIC_MEMBER,
    build_prefix_budget_proof,
    build_synthetic_archive,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/manifests/aemo_source_contract_repair_v2.yaml"
PROOF = ROOT / "experiments/v14_aemo_source_contract_repair/artifacts/prefix_budget_proof.json"


def _spec() -> dict[str, object]:
    return {
        "object_id": "synthetic-prefix-budget-proof",
        "sample_label": "offline-only",
        "month": "2021-12",
        "mechanism_phase": "A3_5MS_PLUS_WDR",
        "observation_phase": "O4_V51_CLUSTERED_RELEASE",
        "version_basis": "POST_V51_WDR",
        "delivery_channel": "PUBLIC_MONTHLY_ARCHIVE",
        "archive_family": "MMSDM_Historical_Data_SQLLoader/PUBLIC_DVD",
        "archive_file_id": "PUBLIC_DVD_DISPATCHOFFERTRK",
        "logical_role": "DISPATCHOFFERTRK",
        "sensitivity_class": "STABLE_APPLIED_OFFER_LINK",
        "url": "synthetic://offline-only",
        "expected_member": SYNTHETIC_MEMBER,
        "expected_package": "DISPATCH",
        "expected_table": "OFFERTRK",
        "expected_version": "1",
        "required_fields": ["FIELD_000", "FIELD_127"],
        "forbidden_fields": [],
    }


def _small_archive() -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["I", "DISPATCH", "OFFERTRK", "1", "FIELD_000", "FIELD_127"])
    writer.writerow(["D", "DISPATCH", "OFFERTRK", "1", "0", "0"])
    archive_buffer = io.BytesIO()
    with ZipFile(archive_buffer, "w", ZIP_DEFLATED) as archive:
        archive.writestr(SYNTHETIC_MEMBER, buffer.getvalue())
    return archive_buffer.getvalue()


def test_repair_manifest_is_valid_and_keeps_rows_locked() -> None:
    manifest = load_source_contract_manifest(MANIFEST)

    assert validate_source_contract_repair_manifest(manifest) == ()
    assert manifest["selection"]["anchors"][0]["selected_month"] == "2021-01"
    assert manifest["selection"]["anchors"][1]["selected_month"] == "2021-12"
    assert manifest["gates"]["row_access_allowed_after_pass"] is False


def test_repair_selection_skips_consumed_adjacent_months() -> None:
    consumed = ["2021-02", "2021-11"]

    assert nearest_unconsumed_complete_month("2021-03-08", "before", consumed) == "2021-01"
    assert nearest_unconsumed_complete_month("2021-10-24", "after", consumed) == "2021-12"


def test_repair_manifest_rejects_reusing_consumed_month() -> None:
    invalid = copy.deepcopy(load_source_contract_manifest(MANIFEST))
    invalid["selection"]["anchors"][0]["selected_month"] = "2021-02"

    assert any(
        "selection" in error for error in validate_source_contract_repair_manifest(invalid)
    )


def test_offline_prefix_budget_proof_is_deterministic() -> None:
    artifact = PROOF.read_bytes()

    assert hashlib.sha256(artifact).hexdigest() == PREFIX_PROOF_SHA256
    assert json.loads(artifact) == build_prefix_budget_proof(ROOT)


def test_repair_audit_passes_exact_partial_64_kib_response() -> None:
    archive = build_synthetic_archive()
    content = archive[:RANGE_BYTES]
    audit = audit_source_contract_repair_response(
        _spec(),
        http_status=206,
        content=content,
        response_headers={"Content-Range": f"bytes 0-{RANGE_BYTES - 1}/{len(archive)}"},
        retrieved_at="2026-08-15T02:45:00Z",
        transport_error=None,
    )

    assert audit["exact_range_contract_pass"] is True
    assert audit["source_header_contract_pass"] is True
    assert audit["source_contract_pass"] is True
    assert audit["full_archive_downloaded"] is False


def test_repair_audit_rejects_complete_small_object_but_preserves_scientific_pass() -> None:
    content = _small_archive()
    audit = audit_source_contract_repair_response(
        _spec(),
        http_status=206,
        content=content,
        response_headers={"Content-Range": f"bytes 0-{len(content) - 1}/{len(content)}"},
        retrieved_at="2026-08-15T02:45:00Z",
        transport_error=None,
    )

    assert audit["source_header_contract_pass"] is True
    assert audit["exact_range_contract_pass"] is False
    assert audit["source_contract_pass"] is False
    assert audit["full_archive_downloaded"] is True


def test_repair_summary_separates_scientific_and_transfer_gates() -> None:
    audits = [
        {
            "http_status": 206,
            "exact_range_contract_pass": index != 0,
            "zip_prefix_parse": True,
            "source_header_contract_pass": True,
            "source_contract_pass": index != 0,
            "full_archive_downloaded": index == 0,
            "data_row_opened": False,
            "response_bytes": RANGE_BYTES,
        }
        for index in range(10)
    ]
    summary = summarize_source_contract_repair_audit(
        audits,
        source_manifest="manifest.yaml",
        source_manifest_sha256="a" * 64,
        collector_git_commit="b" * 40,
        generated_at="2026-08-15T02:45:00Z",
    )

    assert summary["source_header_contract_pass_count"] == 10
    assert summary["complete_archive_transfer_count"] == 1
    assert summary["pass"] is False
