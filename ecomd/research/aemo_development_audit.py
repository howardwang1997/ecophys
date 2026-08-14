"""Frozen AEMO archive-object and header audit for development-only samples."""

from __future__ import annotations

import csv
import hashlib
import io
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import cast
from urllib.parse import urlparse
from zipfile import BadZipFile, ZipFile

import yaml

SCHEMA_VERSION = "ecophys-aemo-development-objects/v1"
HEADER_SCHEMA_VERSION = "ecophys-aemo-development-headers/v1"
EXPECTED_SAMPLE_DATES = {
    "legacy-2021-03": "2021-03-02",
    "current-2025-01": "2025-01-07",
}
EXPECTED_LOGICAL_ROLES = (
    "BIDDAYOFFER_D",
    "BIDPEROFFER_D",
    "DISPATCHOFFERTRK",
    "DISPATCHLOAD",
    "DUDETAILSUMMARY",
)
OBJECT_KEYS = frozenset(
    {
        "object_id",
        "sample_label",
        "market_date",
        "logical_role",
        "archive_table",
        "url",
        "expected_bytes",
        "minimum_header_fields",
    }
)


def load_aemo_object_manifest(path: str | Path) -> dict[str, object]:
    """Load the exact-object contract at an object-typed boundary."""

    payload: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("AEMO object manifest root must be a mapping")
    return cast(dict[str, object], payload)


def manifest_sha256(path: str | Path) -> str:
    """Hash exact serialized manifest bytes."""

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def file_sha256(path: str | Path, *, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    """Hash a potentially large archive with bounded memory."""

    if chunk_bytes <= 0:
        raise ValueError("chunk_bytes must be positive")
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_bytes):
            digest.update(chunk)
    return digest.hexdigest()


def _text(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _sequence_of_text(value: object) -> tuple[str, ...] | None:
    if not isinstance(value, list) or any(_text(item) is None for item in value):
        return None
    return tuple(cast(str, item).strip() for item in value)


def validate_aemo_object_manifest(manifest: Mapping[str, object]) -> tuple[str, ...]:
    """Validate the exact ten-object acquisition boundary without opening an archive."""

    errors: list[str] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if manifest.get("stage") != "exact_objects_frozen_no_aemo_archives_downloaded":
        errors.append("stage must remain exact_objects_frozen_no_aemo_archives_downloaded")
    if manifest.get("scientific_role") != "development_only_schema_and_provenance":
        errors.append("scientific_role changed")
    if manifest.get("full_month_bundle_allowed") is not False:
        errors.append("full_month_bundle_allowed must be false")
    if manifest.get("no_object_replacement") is not True:
        errors.append("no_object_replacement must be true")
    parent = manifest.get("parent_commit")
    if not isinstance(parent, str) or len(parent) != 40 or any(
        character not in "0123456789abcdef" for character in parent
    ):
        errors.append("parent_commit must be a full lowercase Git SHA")

    objects_raw = manifest.get("objects")
    if not isinstance(objects_raw, list) or len(objects_raw) != 10:
        errors.append("objects must contain exactly ten entries")
        objects: list[Mapping[str, object]] = []
    else:
        objects = []
        for index, item in enumerate(objects_raw):
            if not isinstance(item, Mapping):
                errors.append(f"objects[{index}] must be a mapping")
            else:
                objects.append(cast(Mapping[str, object], item))
    object_ids: set[str] = set()
    observed_pairs: list[tuple[str, str]] = []
    for index, item in enumerate(objects):
        if set(item) != OBJECT_KEYS:
            errors.append(f"objects[{index}] must contain exactly {sorted(OBJECT_KEYS)}")
        object_id = _text(item.get("object_id"))
        sample_label = _text(item.get("sample_label"))
        market_date = _text(item.get("market_date"))
        logical_role = _text(item.get("logical_role"))
        archive_table = _text(item.get("archive_table"))
        if object_id is None or object_id in object_ids:
            errors.append(f"objects[{index}].object_id must be unique")
        else:
            object_ids.add(object_id)
        if sample_label not in EXPECTED_SAMPLE_DATES:
            errors.append(f"objects[{index}].sample_label is not frozen")
        elif market_date != EXPECTED_SAMPLE_DATES[sample_label]:
            errors.append(f"objects[{index}].market_date differs from the frozen date")
        if logical_role not in EXPECTED_LOGICAL_ROLES:
            errors.append(f"objects[{index}].logical_role is unsupported")
        elif sample_label is not None:
            observed_pairs.append((sample_label, logical_role))
        if archive_table is None:
            errors.append(f"objects[{index}].archive_table must be non-empty")
        url = _text(item.get("url"))
        if url is None:
            errors.append(f"objects[{index}].url must be non-empty")
        else:
            parsed = urlparse(url)
            if (
                parsed.scheme != "https"
                or parsed.hostname not in {"www.nemweb.com.au", "nemweb.com.au"}
                or parsed.fragment
                or parsed.query
                or not parsed.path.endswith(".zip")
                or "/DATA/" not in parsed.path
            ):
                errors.append(f"objects[{index}].url is outside the frozen individual-archive boundary")
        size = item.get("expected_bytes")
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            errors.append(f"objects[{index}].expected_bytes must be positive")
        fields = _sequence_of_text(item.get("minimum_header_fields"))
        if not fields or len(set(fields)) != len(fields):
            errors.append(f"objects[{index}].minimum_header_fields must be unique and non-empty")

    expected_pairs = {
        (sample_label, role)
        for sample_label in EXPECTED_SAMPLE_DATES
        for role in EXPECTED_LOGICAL_ROLES
    }
    if set(observed_pairs) != expected_pairs or len(observed_pairs) != len(expected_pairs):
        errors.append("objects must contain every frozen sample/role pair exactly once")

    gates = manifest.get("gates")
    if not isinstance(gates, Mapping):
        errors.append("gates must be a mapping")
    else:
        if gates.get("exact_object_count_required") != 10:
            errors.append("gates.exact_object_count_required must be ten")
        if gates.get("row_join_allowed_before_header_contract_commit") is not False:
            errors.append("row joins must remain locked before header-contract commit")
        if gates.get("gpu_allowed") is not False:
            errors.append("AEMO header audit cannot use GPU")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, Mapping):
        errors.append("outputs must be a mapping")
    else:
        for key, value in outputs.items():
            text = _text(value)
            if text is None:
                errors.append(f"outputs.{key} must be non-empty")
                continue
            path = PurePosixPath(text)
            if path.is_absolute() or ".." in path.parts:
                errors.append(f"outputs.{key} must be repository-relative")
    return tuple(errors)


def inspect_aemo_archive(path: str | Path, spec: Mapping[str, object]) -> dict[str, object]:
    """Verify bytes, CRC and the MMSDM information header without joining data rows."""

    archive_path = Path(path)
    errors: list[str] = []
    raw_size = archive_path.stat().st_size
    expected_bytes = spec.get("expected_bytes")
    if raw_size != expected_bytes:
        errors.append(f"archive bytes {raw_size} != expected {expected_bytes}")
    raw_sha256 = file_sha256(archive_path)
    members: list[str] = []
    bad_crc_member: str | None = None
    crc_test_completed = False
    selected_member: str | None = None
    member_uncompressed_bytes: int | None = None
    member_compressed_bytes: int | None = None
    member_crc32: str | None = None
    header_package: str | None = None
    header_table: str | None = None
    header_version: str | None = None
    header_fields: list[str] = []
    try:
        with ZipFile(archive_path) as archive:
            members = archive.namelist()
            csv_members = [name for name in members if name.upper().endswith(".CSV")]
            if len(csv_members) != 1:
                errors.append(f"expected exactly one CSV member, found {len(csv_members)}")
            else:
                selected_member = csv_members[0]
                info = archive.getinfo(selected_member)
                member_uncompressed_bytes = info.file_size
                member_compressed_bytes = info.compress_size
                member_crc32 = f"{info.CRC:08x}"
                with (
                    archive.open(selected_member) as binary,
                    io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as text,
                ):
                    for row in csv.reader(text):
                        if row and row[0].strip() == "I":
                            if len(row) < 5:
                                errors.append("information header has fewer than five fields")
                            else:
                                header_package = row[1].strip()
                                header_table = row[2].strip()
                                header_version = row[3].strip()
                                header_fields = [field.strip() for field in row[4:]]
                            break
                if not header_fields:
                    errors.append("no MMSDM information header was found")
            bad_crc_member = archive.testzip()
            crc_test_completed = True
            if bad_crc_member is not None:
                errors.append(f"ZIP CRC failed for member {bad_crc_member}")
    except (BadZipFile, OSError, UnicodeError, csv.Error) as error:
        errors.append(f"archive inspection failed: {type(error).__name__}: {error}")

    archive_table = spec.get("archive_table")
    if header_table is not None and header_table != archive_table:
        errors.append(f"header table {header_table} != frozen archive table {archive_table}")
    required = _sequence_of_text(spec.get("minimum_header_fields")) or ()
    missing_fields = sorted(set(required) - set(header_fields))
    if missing_fields:
        errors.append(f"missing minimum header fields: {missing_fields}")
    return {
        "object_id": spec.get("object_id"),
        "sample_label": spec.get("sample_label"),
        "market_date": spec.get("market_date"),
        "logical_role": spec.get("logical_role"),
        "archive_table": archive_table,
        "url": spec.get("url"),
        "expected_bytes": expected_bytes,
        "observed_bytes": raw_size,
        "raw_sha256": raw_sha256,
        "zip_members": members,
        "single_csv_member": len([name for name in members if name.upper().endswith(".CSV")]) == 1,
        "selected_member": selected_member,
        "member_uncompressed_bytes": member_uncompressed_bytes,
        "member_compressed_bytes": member_compressed_bytes,
        "member_crc32": member_crc32,
        "bad_crc_member": bad_crc_member,
        "zip_crc_pass": crc_test_completed and bad_crc_member is None,
        "header_package": header_package,
        "header_table": header_table,
        "header_version": header_version,
        "header_fields": header_fields,
        "minimum_header_fields": list(required),
        "missing_minimum_header_fields": missing_fields,
        "row_count_opened": False,
        "header_pass": not errors,
        "errors": errors,
    }


def build_header_contract(
    audits: Sequence[Mapping[str, object]],
    *,
    source_manifest: str,
    source_manifest_sha256: str,
    generated_at: str,
    generator_git_commit: str,
) -> dict[str, object]:
    """Build the next-stage header contract while keeping row joins locked."""

    return {
        "schema_version": HEADER_SCHEMA_VERSION,
        "generated_at": generated_at,
        "generator_git_commit": generator_git_commit,
        "source_manifest": source_manifest,
        "source_manifest_sha256": source_manifest_sha256,
        "scientific_role": "development_only_header_contract",
        "all_headers_pass": len(audits) == 10
        and all(audit.get("header_pass") is True for audit in audits),
        "row_counts_opened": False,
        "row_join_authorized": False,
        "objects": [dict(audit) for audit in audits],
        "next_gate": "commit_this_header_contract_before_any_row_filter_join_or_replay",
    }


def summarize_header_audit(
    downloads: Sequence[Mapping[str, object]],
    audits: Sequence[Mapping[str, object]],
    *,
    expected_count: int,
    download_ledger_sha256: str,
) -> dict[str, object]:
    """Evaluate the frozen object/header gates and report every failure."""

    http_200 = sum(download.get("http_status") == 200 for download in downloads)
    byte_matches = sum(
        download.get("observed_bytes") == download.get("expected_bytes") for download in downloads
    )
    sha_count = sum(isinstance(download.get("sha256"), str) for download in downloads)
    crc_passes = sum(audit.get("zip_crc_pass") is True for audit in audits)
    single_members = sum(audit.get("single_csv_member") is True for audit in audits)
    table_matches = sum(audit.get("header_table") == audit.get("archive_table") for audit in audits)
    minimum_fields = sum(not audit.get("missing_minimum_header_fields") for audit in audits)
    header_passes = sum(audit.get("header_pass") is True for audit in audits)
    denominators_ok = len(downloads) == expected_count and len(audits) == expected_count
    gates = {
        "exact_object_count": denominators_ok,
        "http_200_rate": http_200 == expected_count,
        "expected_byte_match_rate": byte_matches == expected_count,
        "sha256_present_rate": sha_count == expected_count,
        "zip_crc_pass_rate": crc_passes == expected_count,
        "single_csv_member_rate": single_members == expected_count,
        "archive_table_match_rate": table_matches == expected_count,
        "minimum_header_field_rate": minimum_fields == expected_count,
        "all_headers_pass": header_passes == expected_count,
    }
    return {
        "schema": "ecophys-aemo-header-audit-summary/v1",
        "scientific_role": "development_only_schema_and_provenance",
        "expected_object_count": expected_count,
        "download_ledger_count": len(downloads),
        "header_audit_count": len(audits),
        "http_200_count": http_200,
        "expected_byte_match_count": byte_matches,
        "sha256_count": sha_count,
        "zip_crc_pass_count": crc_passes,
        "single_csv_member_count": single_members,
        "archive_table_match_count": table_matches,
        "minimum_header_field_pass_count": minimum_fields,
        "header_pass_count": header_passes,
        "download_ledger_sha256": download_ledger_sha256,
        "gates": gates,
        "pass": all(gates.values()),
    }


def utc_now() -> str:
    """Return the canonical audit timestamp."""

    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
