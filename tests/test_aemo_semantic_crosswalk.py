from __future__ import annotations

import copy
import csv
import io
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from ecomd.research.aemo_semantic_crosswalk import (
    RESOLVED_STAGE,
    build_heldout_header_contract,
    inspect_crosswalk_archive,
    load_crosswalk,
    resolve_head_metadata,
    summarize_heldout_header_audit,
    validate_crosswalk,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/manifests/aemo_semantic_crosswalk_v2.yaml"


def test_frozen_aemo_crosswalk_is_valid_and_unresolved() -> None:
    manifest = load_crosswalk(MANIFEST)

    assert validate_crosswalk(manifest) == ()
    assert manifest["gates"]["row_access_before_heldout_header_commit_allowed"] is False
    assert manifest["gates"]["gpu_allowed"] is False
    assert len(manifest["objects"]) == 10


def _observations(manifest: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            "object_id": item["object_id"],
            "http_status": 200,
            "content_length": 1000 + index,
            "etag": None,
            "last_modified": "Fri, 14 Aug 2026 00:00:00 GMT",
        }
        for index, item in enumerate(manifest["objects"])
    ]


def test_exact_ordered_head_resolution_produces_valid_manifest() -> None:
    manifest = load_crosswalk(MANIFEST)

    resolved = resolve_head_metadata(
        manifest,
        _observations(manifest),
        source_manifest_sha256="a" * 64,
        resolved_at="2026-08-14T08:30:00Z",
        resolver_git_commit="b" * 40,
    )

    assert validate_crosswalk(resolved) == ()
    assert resolved["stage"] == RESOLVED_STAGE
    assert resolved["resolution"]["all_head_requests_pass"] is True


def test_out_of_order_head_resolution_is_rejected() -> None:
    manifest = load_crosswalk(MANIFEST)
    observations = _observations(manifest)
    observations[0], observations[1] = observations[1], observations[0]

    try:
        resolve_head_metadata(
            manifest,
            observations,
            source_manifest_sha256="a" * 64,
            resolved_at="2026-08-14T08:30:00Z",
            resolver_git_commit="b" * 40,
        )
    except ValueError as error:
        assert "out of order" in str(error)
    else:
        raise AssertionError("out-of-order HEAD observations were accepted")


def test_discovery_month_cannot_be_reused_as_validation() -> None:
    manifest = load_crosswalk(MANIFEST)
    invalid = copy.deepcopy(manifest)
    invalid["selection"]["validation_samples"][0]["month"] = "2021-03"

    assert "held-out validation samples changed" in validate_crosswalk(invalid)


def test_crosswalk_sources_must_be_declared_required_fields() -> None:
    manifest = load_crosswalk(MANIFEST)
    invalid = copy.deepcopy(manifest)
    invalid["crosswalk"][0]["regimes"]["legacy_public_dvd"]["field_map"]["duid"]["sources"] = ["UNDECLARED"]

    assert any("sources is invalid" in error for error in validate_crosswalk(invalid))


def _dispatch_archive(path: Path, *, package: str = "DISPATCH") -> Path:
    fields = [
        "SETTLEMENTDATE",
        "RUNNO",
        "DUID",
        "INTERVENTION",
        "INITIALMW",
        "TOTALCLEARED",
        "AVAILABILITY",
    ]
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["I", package, "UNIT_SOLUTION", "5", *fields])
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("PUBLIC_UNIT_SOLUTION.CSV", buffer.getvalue())
    return path


def _dispatch_spec(path: Path) -> dict[str, object]:
    return {
        "object_id": "heldout-current-test-dispatchload",
        "sample_label": "heldout-current-2025-07",
        "logical_role": "DISPATCHLOAD",
        "url": "https://www.nemweb.com.au/DATA/object.zip",
        "http_status": 200,
        "expected_bytes": path.stat().st_size,
        "etag": None,
        "last_modified": None,
    }


def test_heldout_archive_passes_frozen_package_table_and_field_projection(tmp_path: Path) -> None:
    manifest = load_crosswalk(MANIFEST)
    path = _dispatch_archive(tmp_path / "dispatch.zip")

    audit = inspect_crosswalk_archive(path, _dispatch_spec(path), manifest)

    assert audit["header_pass"] is True
    assert audit["expected_header_package"] == "DISPATCH"
    assert audit["expected_header_table"] == "UNIT_SOLUTION"
    assert audit["row_count_opened"] is False


def test_wrong_package_fails_heldout_projection_and_summary(tmp_path: Path) -> None:
    manifest = load_crosswalk(MANIFEST)
    path = _dispatch_archive(tmp_path / "dispatch.zip", package="WRONG")
    spec = _dispatch_spec(path)
    audit = inspect_crosswalk_archive(path, spec, manifest)
    download = {
        "http_status": 200,
        "observed_bytes": path.stat().st_size,
        "expected_bytes": path.stat().st_size,
        "sha256": "a" * 64,
    }

    summary = summarize_heldout_header_audit(
        [download],
        [audit],
        expected_count=1,
        download_ledger_sha256="b" * 64,
    )

    assert audit["header_pass"] is False
    assert summary["header_package_match_count"] == 0
    assert summary["pass"] is False


def test_heldout_header_contract_keeps_rows_locked(tmp_path: Path) -> None:
    manifest = load_crosswalk(MANIFEST)
    path = _dispatch_archive(tmp_path / "dispatch.zip")
    audit = inspect_crosswalk_archive(path, _dispatch_spec(path), manifest)

    contract = build_heldout_header_contract(
        [audit],
        source_manifest="resolved.yaml",
        source_manifest_sha256="a" * 64,
        generated_at="2026-08-14T08:40:00Z",
        generator_git_commit="b" * 40,
    )

    assert contract["all_headers_pass"] is False
    assert contract["row_counts_opened"] is False
    assert contract["row_join_authorized"] is False
