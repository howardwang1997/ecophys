"""Frozen modern AEMO row-level conformance smoke test."""

from __future__ import annotations

import csv
import hashlib
import io
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import cast
from urllib.parse import unquote, urlparse
from zipfile import BadZipFile, ZipFile

import yaml

SCHEMA_VERSION = "ecophys-aemo-row-conformance/v1"
DOWNLOAD_SCHEMA_VERSION = "ecophys-aemo-row-download/v1"
RETENTION_SCHEMA_VERSION = "ecophys-aemo-row-retention/v1"
SUMMARY_SCHEMA_VERSION = "ecophys-aemo-row-conformance-summary/v1"
PARENT_COMMIT = "8a2d236276f440e17da9c74be9033643558d7ac8"
SAMPLE_DATE = "2026-06-16"
SOURCE_MANIFEST_PATH = "data/manifests/aemo_row_conformance_v1.yaml"

EXPECTED_SELECTION = {
    "rule": "first_tuesday_in_earliest_seven_day_shared_daily_report_window",
    "shared_window_start": "2026-06-13",
    "shared_window_end": "2026-06-19",
    "selected_market_date": SAMPLE_DATE,
    "selection_inputs": "directory_metadata_only_no_zip_or_market_row",
    "target_event": False,
    "causal_outcome": False,
    "no_replacement": True,
    "previously_consumed_months": [
        "2020-09",
        "2021-01",
        "2021-02",
        "2021-03",
        "2021-09",
        "2021-11",
        "2021-12",
        "2022-04",
        "2025-01",
        "2025-07",
    ],
}

EXPECTED_OBJECTS: dict[str, dict[str, object]] = {
    "bidmove-complete-2026-06-16": {
        "source_role": "BIDMOVE_COMPLETE",
        "expected_filename": "PUBLIC_BIDMOVE_COMPLETE_20260616_0000000522858228.zip",
        "expected_bytes": 9_095_887,
        "maximum_uncompressed_bytes": 536_870_912,
        "required_table_roles": ["BIDDAYOFFER_D", "BIDPEROFFER_D"],
        "r2_key": (
            "raw/aemo/v14_row_conformance/market_date=2026-06-16/"
            "PUBLIC_BIDMOVE_COMPLETE_20260616_0000000522858228.zip"
        ),
    },
    "next-day-dispatch-2026-06-16": {
        "source_role": "NEXT_DAY_DISPATCH",
        "expected_filename": "PUBLIC_NEXT_DAY_DISPATCH_20260616_0000000522854663.zip",
        "expected_bytes": 8_611_556,
        "maximum_uncompressed_bytes": 536_870_912,
        "required_table_roles": ["DISPATCHOFFERTRK", "DISPATCHLOAD"],
        "r2_key": (
            "raw/aemo/v14_row_conformance/market_date=2026-06-16/"
            "PUBLIC_NEXT_DAY_DISPATCH_20260616_0000000522854663.zip"
        ),
    },
    "dudetailsummary-2026-06": {
        "source_role": "DUDETAILSUMMARY_MONTHLY_SNAPSHOT",
        "expected_filename": "PUBLIC_ARCHIVE#DUDETAILSUMMARY#FILE01#202606010000.zip",
        "expected_bytes": 378_528,
        "maximum_uncompressed_bytes": 33_554_432,
        "required_table_roles": ["DUDETAILSUMMARY"],
        "r2_key": (
            "raw/aemo/v14_row_conformance/market_date=2026-06-16/"
            "PUBLIC_ARCHIVE#DUDETAILSUMMARY#FILE01#202606010000.zip"
        ),
    },
}

EXPECTED_TABLES: dict[str, dict[str, object]] = {
    "BIDDAYOFFER_D": {
        "source_object_id": "bidmove-complete-2026-06-16",
        "expected_package": "BID",
        "expected_table": "BIDDAYOFFER_D",
        "expected_version": "3",
        "required_fields": [
            "SETTLEMENTDATE",
            "DUID",
            "BIDTYPE",
            "DIRECTION",
            "BIDSETTLEMENTDATE",
            "OFFERDATE",
            "PARTICIPANTID",
        ],
        "primary_key": ["SETTLEMENTDATE", "BIDTYPE", "DUID", "DIRECTION"],
    },
    "BIDPEROFFER_D": {
        "source_object_id": "bidmove-complete-2026-06-16",
        "expected_package": "BID",
        "expected_table": "BIDPEROFFER_D",
        "expected_version": "4",
        "required_fields": [
            "SETTLEMENTDATE",
            "DUID",
            "BIDTYPE",
            "DIRECTION",
            "INTERVAL_DATETIME",
            "BIDSETTLEMENTDATE",
            "OFFERDATE",
            "VERSIONNO",
            "MAXAVAIL",
        ],
        "primary_key": [
            "SETTLEMENTDATE",
            "BIDTYPE",
            "DUID",
            "DIRECTION",
            "INTERVAL_DATETIME",
        ],
    },
    "DISPATCHOFFERTRK": {
        "source_object_id": "next-day-dispatch-2026-06-16",
        "expected_package": "DISPATCH",
        "expected_table": "OFFERTRK",
        "expected_version": "1",
        "required_fields": [
            "SETTLEMENTDATE",
            "DUID",
            "BIDTYPE",
            "BIDSETTLEMENTDATE",
            "BIDOFFERDATE",
        ],
        "primary_key": ["SETTLEMENTDATE", "DUID", "BIDTYPE"],
    },
    "DISPATCHLOAD": {
        "source_object_id": "next-day-dispatch-2026-06-16",
        "expected_package": "DISPATCH",
        "expected_table": "UNIT_SOLUTION",
        "expected_version": "6",
        "required_fields": [
            "SETTLEMENTDATE",
            "RUNNO",
            "DUID",
            "INTERVENTION",
            "INITIALMW",
            "TOTALCLEARED",
        ],
        "primary_key": ["SETTLEMENTDATE", "RUNNO", "DUID", "INTERVENTION"],
    },
    "DUDETAILSUMMARY": {
        "source_object_id": "dudetailsummary-2026-06",
        "expected_package": "PARTICIPANT_REGISTRATION",
        "expected_table": "DUDETAILSUMMARY",
        "expected_version": "7",
        "required_fields": [
            "DUID",
            "START_DATE",
            "END_DATE",
            "DISPATCHTYPE",
            "REGIONID",
            "PARTICIPANTID",
            "DISPATCHSUBTYPE",
        ],
        "primary_key": ["DUID", "START_DATE"],
    },
}

EXPECTED_TIME_CONTRACT = {
    "timezone_semantics": "AEMO_MARKET_TIME_AS_PUBLISHED_NO_UTC_CONVERSION",
    "market_date_field_value": "2026-06-16",
    "dispatch_interval_start_inclusive": "2026-06-16T04:05:00",
    "dispatch_interval_end_inclusive": "2026-06-17T04:00:00",
    "identity_interval": "START_DATE <= SETTLEMENTDATE < END_DATE",
    "future_identity_rows_may_not_override_as_of_match": True,
}

EXPECTED_JOIN_CONTRACT = {
    "bid_period_to_day_parent": ["SETTLEMENTDATE", "DUID", "BIDTYPE", "DIRECTION"],
    "tracker_to_period": {
        "DISPATCHOFFERTRK.SETTLEMENTDATE": "BIDPEROFFER_D.INTERVAL_DATETIME",
        "DISPATCHOFFERTRK.DUID": "BIDPEROFFER_D.DUID",
        "DISPATCHOFFERTRK.BIDTYPE": "BIDPEROFFER_D.BIDTYPE",
        "DISPATCHOFFERTRK.BIDSETTLEMENTDATE": "BIDPEROFFER_D.BIDSETTLEMENTDATE",
        "DISPATCHOFFERTRK.BIDOFFERDATE": "BIDPEROFFER_D.OFFERDATE",
    },
    "direction_limitation": ("DISPATCHOFFERTRK_HAS_NO_DIRECTION; retain all matches and report multiplicity"),
    "tracker_to_physical_dispatch": ["SETTLEMENTDATE", "DUID"],
    "physical_dispatch_filter": {"RUNNO": 1, "INTERVENTION": 0},
    "dispatch_to_identity": ["DUID", "effective_half_open_interval"],
}

EXPECTED_RESOURCE_CONTRACT = {
    "exact_compressed_bytes": 18_085_971,
    "maximum_total_uncompressed_bytes": 1_107_296_256,
    "maximum_total_data_rows": 4_000_000,
    "cpu_only": True,
    "gpu_allowed": False,
    "paid_data_allowed": False,
    "remote_worker_required": False,
}

EXPECTED_RETENTION_CONTRACT = {
    "bucket": "ecophys",
    "prefix": "raw/aemo/v14_row_conformance/market_date=2026-06-16/",
    "upload_before_any_csv_row_parse": True,
    "remote_sha256_metadata_required": True,
    "overwrite_mismatched_remote_object_allowed": False,
    "raw_rows_committed_to_git": False,
}

EXPECTED_GATES = {
    "required_object_count": 3,
    "required_r2_verified_count": 3,
    "required_archive_crc_count": 3,
    "required_table_count": 5,
    "required_nonempty_table_count": 5,
    "maximum_total_data_rows": 4_000_000,
    "timestamp_parse_rate_min": 1.0,
    "primary_key_duplicate_count_max": 0,
    "bid_market_date_rate_min": 1.0,
    "dispatch_window_rate_min": 1.0,
    "bid_period_parent_match_rate_min": 1.0,
    "tracker_offer_reference_non_null_rate_min": 0.99,
    "tracker_period_match_rate_min": 0.995,
    "tracker_period_ambiguous_rate_max": 0.05,
    "tracker_dispatch_match_rate_min": 0.995,
    "dispatch_identity_match_rate_min": 0.995,
    "dispatch_identity_overlap_count_max": 0,
    "replacement_allowed": False,
    "causal_claim_allowed": False,
    "model_claim_allowed": False,
}

ROOT_KEYS = frozenset(
    {
        "schema_version",
        "sample_id",
        "frozen_at",
        "parent_commit",
        "scientific_role",
        "prior_gate",
        "selection",
        "source_metadata",
        "objects",
        "table_contracts",
        "time_contract",
        "join_contract",
        "resource_contract",
        "retention_contract",
        "gates",
        "outputs",
    }
)
OBJECT_KEYS = frozenset(
    {
        "object_id",
        "source_role",
        "url",
        "listing_url",
        "expected_filename",
        "expected_bytes",
        "maximum_uncompressed_bytes",
        "required_table_roles",
        "r2_key",
    }
)
TABLE_KEYS = frozenset(
    {
        "logical_role",
        "source_object_id",
        "expected_package",
        "expected_table",
        "expected_version",
        "required_fields",
        "primary_key",
    }
)


def load_row_conformance_manifest(path: str | Path) -> dict[str, object]:
    """Load the frozen row-level conformance manifest."""

    payload: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("AEMO row-conformance manifest root must be a mapping")
    return cast(dict[str, object], payload)


def manifest_sha256(path: str | Path) -> str:
    """Hash exact manifest bytes."""

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def file_sha256(path: str | Path, *, chunk_bytes: int = 1 << 20) -> str:
    """Hash a file with bounded memory."""

    if chunk_bytes <= 0:
        raise ValueError("chunk_bytes must be positive")
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_bytes):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _text(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _sha(value: object, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in "0123456789abcdef" for character in value)
    )


def _utc(value: object) -> bool:
    text = _text(value)
    if text is None or not text.endswith("Z"):
        return False
    try:
        parsed = datetime.fromisoformat(text.removesuffix("Z") + "+00:00")
    except ValueError:
        return False
    return parsed.tzinfo == UTC


def _safe_relative_path(value: object) -> bool:
    text = _text(value)
    if text is None:
        return False
    path = PurePosixPath(text)
    return not path.is_absolute() and ".." not in path.parts


def _sequence_of_unique_text(value: object) -> tuple[str, ...] | None:
    if not isinstance(value, list) or not value or any(_text(item) is None for item in value):
        return None
    items = tuple(cast(str, item).strip() for item in value)
    return items if len(set(items)) == len(items) else None


def _expected_object_payload(object_id: str) -> dict[str, object]:
    payload = dict(EXPECTED_OBJECTS[object_id])
    payload["object_id"] = object_id
    return payload


def _expected_table_payload(logical_role: str) -> dict[str, object]:
    payload = dict(EXPECTED_TABLES[logical_role])
    payload["logical_role"] = logical_role
    return payload


def validate_row_conformance_manifest(manifest: Mapping[str, object]) -> tuple[str, ...]:
    """Validate exact sources, row contracts, joins, limits and retention gates."""

    errors: list[str] = []
    if set(manifest) != ROOT_KEYS:
        errors.append("root keys changed")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if manifest.get("sample_id") != "aemo-modern-daily-row-conformance-2026-06-16-v1":
        errors.append("sample_id changed")
    if manifest.get("scientific_role") != "development_only_modern_row_join_conformance_smoke":
        errors.append("scientific_role changed")
    if not _utc(manifest.get("frozen_at")):
        errors.append("frozen_at must be UTC")
    if manifest.get("parent_commit") != PARENT_COMMIT:
        errors.append("parent_commit changed")
    prior = manifest.get("prior_gate")
    if not isinstance(prior, Mapping) or dict(prior) != {
        "decision": "PASS_TRANSFER_REPAIR_AND_SOURCE_HEADER_CONFIRMATION",
        "result_commit": PARENT_COMMIT,
        "raw_summary_sha256": ("e4bac4ac57b8b25b8d91a3465eba544c9c9e22050c47750c89344e339f6417c4"),
        "rows_opened": 0,
    }:
        errors.append("prior gate provenance changed")
    if manifest.get("selection") != EXPECTED_SELECTION:
        errors.append("selection changed")
    source_metadata = manifest.get("source_metadata")
    if not isinstance(source_metadata, Mapping):
        errors.append("source_metadata must be a mapping")
    else:
        required_metadata_keys = {
            "audited_at",
            "nemweb_current_reports",
            "bidmove_listing",
            "next_day_dispatch_listing",
            "monthly_identity_listing",
            "official_data_model",
            "official_table_triggers",
        }
        if set(source_metadata) != required_metadata_keys:
            errors.append("source_metadata keys changed")
        if not _utc(source_metadata.get("audited_at")):
            errors.append("source_metadata.audited_at must be UTC")
        for key in required_metadata_keys - {"audited_at"}:
            url = _text(source_metadata.get(key))
            if url is None or urlparse(url).scheme != "https":
                errors.append(f"source_metadata.{key} must be HTTPS")

    objects = manifest.get("objects")
    if not isinstance(objects, list) or len(objects) != len(EXPECTED_OBJECTS):
        errors.append("objects must contain exactly three entries")
    else:
        observed_ids: list[str] = []
        for index, raw in enumerate(objects):
            if not isinstance(raw, Mapping):
                errors.append(f"objects[{index}] must be a mapping")
                continue
            item = cast(Mapping[str, object], raw)
            if set(item) != OBJECT_KEYS:
                errors.append(f"objects[{index}] keys changed")
            object_id = _text(item.get("object_id"))
            if object_id is None or object_id not in EXPECTED_OBJECTS:
                errors.append(f"objects[{index}].object_id is invalid")
                continue
            observed_ids.append(object_id)
            expected = _expected_object_payload(object_id)
            for key, value in expected.items():
                if item.get(key) != value:
                    errors.append(f"objects[{index}].{key} changed")
            url = _text(item.get("url"))
            listing_url = _text(item.get("listing_url"))
            if url is None or listing_url is None:
                errors.append(f"objects[{index}] URL is invalid")
            else:
                parsed = urlparse(url)
                if (
                    parsed.scheme != "https"
                    or parsed.hostname != "www.nemweb.com.au"
                    or parsed.query
                    or parsed.fragment
                    or unquote(Path(parsed.path).name) != item.get("expected_filename")
                ):
                    errors.append(f"objects[{index}].url is outside the frozen boundary")
                if urlparse(listing_url).hostname != "www.nemweb.com.au":
                    errors.append(f"objects[{index}].listing_url is outside AEMO")
        if observed_ids != list(EXPECTED_OBJECTS):
            errors.append("object order or coverage changed")

    contracts = manifest.get("table_contracts")
    if not isinstance(contracts, list) or len(contracts) != len(EXPECTED_TABLES):
        errors.append("table_contracts must contain exactly five entries")
    else:
        observed_roles: list[str] = []
        for index, raw in enumerate(contracts):
            if not isinstance(raw, Mapping):
                errors.append(f"table_contracts[{index}] must be a mapping")
                continue
            item = cast(Mapping[str, object], raw)
            if set(item) != TABLE_KEYS:
                errors.append(f"table_contracts[{index}] keys changed")
            role = _text(item.get("logical_role"))
            if role is None or role not in EXPECTED_TABLES:
                errors.append(f"table_contracts[{index}].logical_role is invalid")
                continue
            observed_roles.append(role)
            expected = _expected_table_payload(role)
            if dict(item) != expected:
                errors.append(f"table_contracts[{index}] changed")
            if _sequence_of_unique_text(item.get("required_fields")) is None:
                errors.append(f"table_contracts[{index}].required_fields is invalid")
            if _sequence_of_unique_text(item.get("primary_key")) is None:
                errors.append(f"table_contracts[{index}].primary_key is invalid")
        if observed_roles != list(EXPECTED_TABLES):
            errors.append("table contract order or coverage changed")

    if manifest.get("time_contract") != EXPECTED_TIME_CONTRACT:
        errors.append("time_contract changed")
    if manifest.get("join_contract") != EXPECTED_JOIN_CONTRACT:
        errors.append("join_contract changed")
    if manifest.get("resource_contract") != EXPECTED_RESOURCE_CONTRACT:
        errors.append("resource_contract changed")
    if manifest.get("retention_contract") != EXPECTED_RETENTION_CONTRACT:
        errors.append("retention_contract changed")
    if manifest.get("gates") != EXPECTED_GATES:
        errors.append("gates changed")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, Mapping) or set(outputs) != {
        "raw_root",
        "download_receipt",
        "retention_receipt",
        "summary",
    }:
        errors.append("outputs changed")
    elif any(not _safe_relative_path(value) for value in outputs.values()):
        errors.append("all output paths must be safe and repository-relative")
    return tuple(errors)


def table_contracts_by_role(
    manifest: Mapping[str, object],
) -> dict[str, dict[str, object]]:
    """Index validated table contracts by logical role."""

    contracts = cast(list[dict[str, object]], manifest["table_contracts"])
    return {cast(str, item["logical_role"]): item for item in contracts}


def object_specs_by_id(manifest: Mapping[str, object]) -> dict[str, dict[str, object]]:
    """Index validated source objects by identifier."""

    objects = cast(list[dict[str, object]], manifest["objects"])
    return {cast(str, item["object_id"]): item for item in objects}


def parse_aemo_timestamp(value: str) -> datetime | None:
    """Parse the finite set of timestamp formats used by the frozen AEMO feeds."""

    text = value.strip()
    if not text:
        return None
    for pattern in (
        "%Y/%m/%d %H:%M:%S.%f",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(text, pattern)
        except ValueError:
            continue
    return None


def _table_key(contract: Mapping[str, object]) -> tuple[str, str, str]:
    return (
        cast(str, contract["expected_package"]),
        cast(str, contract["expected_table"]),
        cast(str, contract["expected_version"]),
    )


def parse_mmsdm_archive(
    path: str | Path,
    contracts: Sequence[Mapping[str, object]],
    *,
    maximum_uncompressed_bytes: int,
    maximum_data_rows: int,
) -> tuple[dict[str, list[dict[str, str]]], dict[str, object]]:
    """Read only contracted MMSDM tables from one retained ZIP archive."""

    if maximum_uncompressed_bytes <= 0 or maximum_data_rows <= 0:
        raise ValueError("archive resource limits must be positive")
    archive_path = Path(path)
    roles_by_key = {_table_key(item): cast(str, item["logical_role"]) for item in contracts}
    contracts_by_role = {cast(str, item["logical_role"]): item for item in contracts}
    selected: dict[str, list[dict[str, str]]] = {role: [] for role in contracts_by_role}
    headers: dict[tuple[str, str, str], tuple[str, ...]] = {}
    errors: list[str] = []
    csv_member: str | None = None
    member_uncompressed_bytes: int | None = None
    member_compressed_bytes: int | None = None
    bad_crc_member: str | None = None
    crc_test_completed = False
    total_data_rows = 0
    target_data_rows = 0
    try:
        with ZipFile(archive_path) as archive:
            members = [name for name in archive.namelist() if name.upper().endswith(".CSV")]
            if len(members) != 1:
                errors.append(f"expected one CSV member, found {len(members)}")
            else:
                csv_member = members[0]
                info = archive.getinfo(csv_member)
                member_uncompressed_bytes = info.file_size
                member_compressed_bytes = info.compress_size
                if info.file_size > maximum_uncompressed_bytes:
                    errors.append(
                        f"member uncompressed bytes {info.file_size} exceed cap {maximum_uncompressed_bytes}"
                    )
                else:
                    bad_crc_member = archive.testzip()
                    crc_test_completed = True
                    if bad_crc_member is not None:
                        errors.append(f"ZIP CRC failed for member {bad_crc_member}")
                    with (
                        archive.open(csv_member) as binary,
                        io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as text,
                    ):
                        for raw_row in csv.reader(text):
                            if not raw_row:
                                continue
                            row = [value.strip() for value in raw_row]
                            record_type = row[0]
                            if record_type == "I" and len(row) >= 5:
                                key = (row[1], row[2], row[3])
                                fields = tuple(row[4:])
                                previous = headers.get(key)
                                if previous is not None and previous != fields:
                                    errors.append(f"conflicting information headers for {key}")
                                headers[key] = fields
                            elif record_type == "D":
                                total_data_rows += 1
                                if total_data_rows > maximum_data_rows:
                                    errors.append(f"data row count exceeded cap {maximum_data_rows}")
                                    break
                                if len(row) < 4:
                                    errors.append("data row has fewer than four envelope fields")
                                    continue
                                key = (row[1], row[2], row[3])
                                role = roles_by_key.get(key)
                                if role is None:
                                    continue
                                data_fields = headers.get(key)
                                if data_fields is None:
                                    errors.append(f"data row preceded information header for {key}")
                                    continue
                                values = row[4:]
                                if len(values) != len(data_fields):
                                    errors.append(
                                        f"row width {len(values)} != header width "
                                        f"{len(data_fields)} for {key}"
                                    )
                                    continue
                                selected[role].append(dict(zip(data_fields, values, strict=True)))
                                target_data_rows += 1
    except (BadZipFile, OSError, UnicodeError, csv.Error) as error:
        errors.append(f"archive parse failed: {type(error).__name__}: {error}")

    header_observations: list[dict[str, object]] = []
    for role, contract in contracts_by_role.items():
        key = _table_key(contract)
        header_fields = headers.get(key)
        required = cast(list[str], contract["required_fields"])
        missing = required if header_fields is None else sorted(set(required) - set(header_fields))
        if header_fields is None:
            errors.append(f"missing contracted information header for {role}")
        elif missing:
            errors.append(f"{role} missing required fields {missing}")
        header_observations.append(
            {
                "logical_role": role,
                "package": key[0],
                "table": key[1],
                "version": key[2],
                "header_present": header_fields is not None,
                "header_field_count": (len(header_fields) if header_fields is not None else 0),
                "missing_required_fields": missing,
                "row_count": len(selected[role]),
            }
        )
    observation: dict[str, object] = {
        "archive_path": archive_path.name,
        "archive_bytes": archive_path.stat().st_size,
        "archive_sha256": file_sha256(archive_path),
        "csv_member": csv_member,
        "single_csv_member": csv_member is not None,
        "member_uncompressed_bytes": member_uncompressed_bytes,
        "member_compressed_bytes": member_compressed_bytes,
        "bad_crc_member": bad_crc_member,
        "crc_test_completed": crc_test_completed,
        "zip_crc_pass": crc_test_completed and bad_crc_member is None,
        "total_data_rows": total_data_rows,
        "target_data_rows": target_data_rows,
        "headers": header_observations,
        "errors": errors,
        "pass": not errors,
    }
    return selected, observation


def parse_conformance_archives(
    raw_root: str | Path,
    manifest: Mapping[str, object],
) -> tuple[dict[str, list[dict[str, str]]], list[dict[str, object]]]:
    """Parse all exact retained objects under the manifest resource caps."""

    root = Path(raw_root)
    contracts_by_role = table_contracts_by_role(manifest)
    all_tables: dict[str, list[dict[str, str]]] = {role: [] for role in contracts_by_role}
    observations: list[dict[str, object]] = []
    maximum_total_rows = cast(dict[str, object], manifest["resource_contract"])["maximum_total_data_rows"]
    remaining_rows = cast(int, maximum_total_rows)
    for spec in cast(list[dict[str, object]], manifest["objects"]):
        roles = cast(list[str], spec["required_table_roles"])
        contracts = [contracts_by_role[role] for role in roles]
        path = root / cast(str, spec["expected_filename"])
        tables, observation = parse_mmsdm_archive(
            path,
            contracts,
            maximum_uncompressed_bytes=cast(int, spec["maximum_uncompressed_bytes"]),
            maximum_data_rows=max(remaining_rows, 1),
        )
        observation["object_id"] = spec["object_id"]
        observation["expected_bytes"] = spec["expected_bytes"]
        observation["exact_byte_match"] = observation["archive_bytes"] == spec["expected_bytes"]
        observations.append(observation)
        remaining_rows -= cast(int, observation["total_data_rows"])
        for role, rows in tables.items():
            all_tables[role].extend(rows)
    return all_tables, observations


def _load_mapping(path: str | Path) -> dict[str, object]:
    import json

    payload: object = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"receipt root must be a mapping: {path}")
    return cast(dict[str, object], payload)


def load_download_receipt(path: str | Path) -> dict[str, object]:
    """Load a row-source download receipt."""

    return _load_mapping(path)


def load_retention_receipt(path: str | Path) -> dict[str, object]:
    """Load an R2 retention receipt."""

    return _load_mapping(path)


def validate_download_receipt(
    receipt: Mapping[str, object],
    manifest: Mapping[str, object],
) -> tuple[str, ...]:
    """Validate exact one-request downloads without opening ZIP members."""

    errors: list[str] = []
    if receipt.get("schema_version") != DOWNLOAD_SCHEMA_VERSION:
        errors.append("download receipt schema changed")
    if not _utc(receipt.get("generated_at")):
        errors.append("download receipt generated_at must be UTC")
    if not _sha(receipt.get("protocol_git_commit"), 40):
        errors.append("download receipt protocol commit is invalid")
    if receipt.get("source_manifest") != SOURCE_MANIFEST_PATH:
        errors.append("download receipt source manifest changed")
    if not _sha(receipt.get("source_manifest_sha256"), 64):
        errors.append("download receipt manifest hash is invalid")
    if receipt.get("request_policy") != ("exactly_one_get_per_frozen_object_no_retry_no_replacement"):
        errors.append("download receipt request policy changed")
    if receipt.get("zip_opened") is not False or receipt.get("csv_rows_opened") is not False:
        errors.append("download receipt claims pre-retention content access")
    objects = receipt.get("objects")
    specs = cast(list[dict[str, object]], manifest["objects"])
    if not isinstance(objects, list) or len(objects) != len(specs):
        errors.append("download receipt object count changed")
        return tuple(errors)
    for index, (raw, spec) in enumerate(zip(objects, specs, strict=True)):
        if not isinstance(raw, Mapping):
            errors.append(f"download receipt objects[{index}] is invalid")
            continue
        item = cast(Mapping[str, object], raw)
        if item.get("object_id") != spec["object_id"]:
            errors.append(f"download receipt objects[{index}] order changed")
        if item.get("request_count") != 1:
            errors.append(f"download receipt objects[{index}] request count is not one")
        if item.get("http_status") != 200:
            errors.append(f"download receipt objects[{index}] HTTP status is not 200")
        if item.get("expected_bytes") != spec["expected_bytes"]:
            errors.append(f"download receipt objects[{index}] expected bytes changed")
        if item.get("observed_bytes") != spec["expected_bytes"]:
            errors.append(f"download receipt objects[{index}] observed bytes mismatch")
        if not _sha(item.get("sha256"), 64):
            errors.append(f"download receipt objects[{index}] SHA-256 is invalid")
        if item.get("download_pass") is not True:
            errors.append(f"download receipt objects[{index}] did not pass")
    if receipt.get("pass") is not True:
        errors.append("download receipt overall decision did not pass")
    return tuple(errors)


def validate_retention_receipt(
    retention: Mapping[str, object],
    download: Mapping[str, object],
    manifest: Mapping[str, object],
) -> tuple[str, ...]:
    """Validate that exact local bytes were retained and verified in R2."""

    errors: list[str] = []
    if retention.get("schema_version") != RETENTION_SCHEMA_VERSION:
        errors.append("retention receipt schema changed")
    if not _utc(retention.get("generated_at")):
        errors.append("retention receipt generated_at must be UTC")
    if retention.get("protocol_git_commit") != download.get("protocol_git_commit"):
        errors.append("retention protocol commit differs from download")
    if retention.get("source_manifest_sha256") != download.get("source_manifest_sha256"):
        errors.append("retention manifest hash differs from download")
    if retention.get("source_manifest") != SOURCE_MANIFEST_PATH:
        errors.append("retention source manifest changed")
    if retention.get("zip_opened") is not False or retention.get("csv_rows_opened") is not False:
        errors.append("retention receipt claims pre-retention content access")
    contract = cast(dict[str, object], manifest["retention_contract"])
    if retention.get("bucket") != contract["bucket"]:
        errors.append("retention bucket changed")
    if retention.get("prefix") != contract["prefix"]:
        errors.append("retention prefix changed")
    retained_objects = retention.get("objects")
    downloaded_objects = download.get("objects")
    specs = cast(list[dict[str, object]], manifest["objects"])
    if not isinstance(retained_objects, list) or not isinstance(downloaded_objects, list):
        errors.append("retention or download objects are invalid")
        return tuple(errors)
    if len(retained_objects) != len(specs) or len(downloaded_objects) != len(specs):
        errors.append("retention object count changed")
        return tuple(errors)
    for index, (raw_retained, raw_downloaded, spec) in enumerate(
        zip(retained_objects, downloaded_objects, specs, strict=True)
    ):
        if not isinstance(raw_retained, Mapping) or not isinstance(raw_downloaded, Mapping):
            errors.append(f"retention objects[{index}] is invalid")
            continue
        retained = cast(Mapping[str, object], raw_retained)
        downloaded = cast(Mapping[str, object], raw_downloaded)
        if retained.get("object_id") != spec["object_id"]:
            errors.append(f"retention objects[{index}] order changed")
        if retained.get("r2_key") != spec["r2_key"]:
            errors.append(f"retention objects[{index}] R2 key changed")
        if retained.get("observed_bytes") != downloaded.get("observed_bytes"):
            errors.append(f"retention objects[{index}] byte count differs from download")
        if retained.get("sha256") != downloaded.get("sha256"):
            errors.append(f"retention objects[{index}] SHA-256 differs from download")
        if retained.get("remote_content_length") != downloaded.get("observed_bytes"):
            errors.append(f"retention objects[{index}] remote size mismatch")
        if retained.get("remote_metadata_sha256") != downloaded.get("sha256"):
            errors.append(f"retention objects[{index}] remote SHA metadata mismatch")
        if retained.get("verified") is not True:
            errors.append(f"retention objects[{index}] is not verified")
    if retention.get("all_verified") is not True:
        errors.append("retention overall decision did not pass")
    return tuple(errors)


def verify_local_downloads(
    raw_root: str | Path,
    download: Mapping[str, object],
    manifest: Mapping[str, object],
) -> tuple[str, ...]:
    """Verify retained local inputs still match their immutable download receipt."""

    errors: list[str] = []
    root = Path(raw_root)
    downloaded = cast(list[dict[str, object]], download["objects"])
    specs = cast(list[dict[str, object]], manifest["objects"])
    for index, (item, spec) in enumerate(zip(downloaded, specs, strict=True)):
        path = root / cast(str, spec["expected_filename"])
        if not path.is_file():
            errors.append(f"local object {index} is absent")
            continue
        if path.stat().st_size != item["observed_bytes"]:
            errors.append(f"local object {index} byte count changed")
        elif file_sha256(path) != item["sha256"]:
            errors.append(f"local object {index} SHA-256 changed")
    return tuple(errors)


def _key_duplicate_count(rows: Sequence[Mapping[str, str]], fields: Sequence[str]) -> int:
    seen: set[tuple[str, ...]] = set()
    duplicates = 0
    for row in rows:
        key = tuple(row.get(field, "") for field in fields)
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)
    return duplicates


def _canonical_timestamp(value: str) -> str | None:
    parsed = parse_aemo_timestamp(value)
    return parsed.isoformat(timespec="microseconds") if parsed is not None else None


def _integer_equals(value: str, expected: int) -> bool:
    try:
        return Decimal(value.strip()) == expected
    except InvalidOperation:
        return False


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _timestamp_metrics(
    tables: Mapping[str, Sequence[Mapping[str, str]]],
) -> tuple[int, int]:
    fields: dict[str, tuple[tuple[str, bool], ...]] = {
        "BIDDAYOFFER_D": (
            ("SETTLEMENTDATE", True),
            ("BIDSETTLEMENTDATE", True),
            ("OFFERDATE", True),
        ),
        "BIDPEROFFER_D": (
            ("SETTLEMENTDATE", True),
            ("INTERVAL_DATETIME", True),
            ("BIDSETTLEMENTDATE", True),
            ("OFFERDATE", True),
        ),
        "DISPATCHOFFERTRK": (
            ("SETTLEMENTDATE", True),
            ("BIDSETTLEMENTDATE", False),
            ("BIDOFFERDATE", False),
        ),
        "DISPATCHLOAD": (("SETTLEMENTDATE", True),),
        "DUDETAILSUMMARY": (("START_DATE", True), ("END_DATE", True)),
    }
    parsed_count = 0
    expected_count = 0
    for role, specifications in fields.items():
        for row in tables[role]:
            for field, required in specifications:
                value = row.get(field, "")
                if not required and not value.strip():
                    continue
                expected_count += 1
                if parse_aemo_timestamp(value) is not None:
                    parsed_count += 1
    return parsed_count, expected_count


def summarize_row_conformance(
    tables: Mapping[str, Sequence[Mapping[str, str]]],
    archive_observations: Sequence[Mapping[str, object]],
    manifest: Mapping[str, object],
    download_receipt: Mapping[str, object],
    retention_receipt: Mapping[str, object],
    *,
    source_manifest_sha256: str,
    analyzer_git_commit: str,
    generated_at: str,
) -> dict[str, object]:
    """Evaluate immutable schema, time, key, join and identity conformance gates."""

    contracts = table_contracts_by_role(manifest)
    counts = {role: len(tables[role]) for role in contracts}
    total_target_rows = sum(counts.values())
    total_data_rows = sum(cast(int, item["total_data_rows"]) for item in archive_observations)
    archive_pass_count = sum(item.get("pass") is True for item in archive_observations)
    crc_pass_count = sum(item.get("zip_crc_pass") is True for item in archive_observations)
    exact_byte_count = sum(item.get("exact_byte_match") is True for item in archive_observations)
    header_pass_count = sum(
        header.get("header_present") is True and not header.get("missing_required_fields")
        for item in archive_observations
        for header in cast(list[dict[str, object]], item["headers"])
    )
    nonempty_count = sum(count > 0 for count in counts.values())

    timestamp_parsed, timestamp_expected = _timestamp_metrics(tables)
    timestamp_rate = _rate(timestamp_parsed, timestamp_expected)
    duplicates_by_role = {
        role: _key_duplicate_count(tables[role], cast(list[str], contract["primary_key"]))
        for role, contract in contracts.items()
    }
    duplicate_count = sum(duplicates_by_role.values())

    selected_date = date.fromisoformat(SAMPLE_DATE)
    bid_rows = list(tables["BIDDAYOFFER_D"]) + list(tables["BIDPEROFFER_D"])
    bid_market_date_matches = 0
    for row in bid_rows:
        parsed = parse_aemo_timestamp(row.get("SETTLEMENTDATE", ""))
        if parsed is not None and parsed.date() == selected_date:
            bid_market_date_matches += 1
    bid_market_date_rate = _rate(bid_market_date_matches, len(bid_rows))

    window_start = datetime.combine(selected_date, datetime.min.time()) + timedelta(hours=4, minutes=5)
    window_end = datetime.combine(selected_date + timedelta(days=1), datetime.min.time()) + timedelta(hours=4)
    interval_field = {
        "BIDPEROFFER_D": "INTERVAL_DATETIME",
        "DISPATCHOFFERTRK": "SETTLEMENTDATE",
        "DISPATCHLOAD": "SETTLEMENTDATE",
    }
    dispatch_window_expected = 0
    dispatch_window_matches = 0
    for role, field in interval_field.items():
        for row in tables[role]:
            dispatch_window_expected += 1
            parsed = parse_aemo_timestamp(row.get(field, ""))
            if parsed is not None and window_start <= parsed <= window_end:
                dispatch_window_matches += 1
    dispatch_window_rate = _rate(dispatch_window_matches, dispatch_window_expected)

    day_parent_keys = {
        (
            row.get("SETTLEMENTDATE", ""),
            row.get("DUID", ""),
            row.get("BIDTYPE", ""),
            row.get("DIRECTION", ""),
        )
        for row in tables["BIDDAYOFFER_D"]
    }
    period_parent_matches = sum(
        (
            row.get("SETTLEMENTDATE", ""),
            row.get("DUID", ""),
            row.get("BIDTYPE", ""),
            row.get("DIRECTION", ""),
        )
        in day_parent_keys
        for row in tables["BIDPEROFFER_D"]
    )
    period_parent_rate = _rate(period_parent_matches, counts["BIDPEROFFER_D"])

    period_index: defaultdict[tuple[str, str, str, str, str], int] = defaultdict(int)
    for row in tables["BIDPEROFFER_D"]:
        interval = _canonical_timestamp(row.get("INTERVAL_DATETIME", ""))
        bid_settlement = _canonical_timestamp(row.get("BIDSETTLEMENTDATE", ""))
        offer = _canonical_timestamp(row.get("OFFERDATE", ""))
        if interval is None or bid_settlement is None or offer is None:
            continue
        key = (
            interval,
            row.get("DUID", ""),
            row.get("BIDTYPE", ""),
            bid_settlement,
            offer,
        )
        period_index[key] += 1

    tracker_count = counts["DISPATCHOFFERTRK"]
    tracker_eligible = 0
    tracker_matched = 0
    tracker_ambiguous = 0
    for row in tables["DISPATCHOFFERTRK"]:
        interval = _canonical_timestamp(row.get("SETTLEMENTDATE", ""))
        bid_settlement = _canonical_timestamp(row.get("BIDSETTLEMENTDATE", ""))
        offer = _canonical_timestamp(row.get("BIDOFFERDATE", ""))
        if interval is None or bid_settlement is None or offer is None:
            continue
        tracker_eligible += 1
        matches = period_index.get(
            (
                interval,
                row.get("DUID", ""),
                row.get("BIDTYPE", ""),
                bid_settlement,
                offer,
            ),
            0,
        )
        if matches:
            tracker_matched += 1
        if matches > 1:
            tracker_ambiguous += 1
    tracker_reference_rate = _rate(tracker_eligible, tracker_count)
    tracker_period_match_rate = _rate(tracker_matched, tracker_eligible)
    tracker_period_ambiguous_rate = _rate(tracker_ambiguous, tracker_eligible)

    physical_dispatch_rows = [
        row
        for row in tables["DISPATCHLOAD"]
        if _integer_equals(row.get("RUNNO", ""), 1) and _integer_equals(row.get("INTERVENTION", ""), 0)
    ]
    physical_dispatch_keys = {
        (canonical, row.get("DUID", ""))
        for row in physical_dispatch_rows
        if (canonical := _canonical_timestamp(row.get("SETTLEMENTDATE", ""))) is not None
    }
    tracker_dispatch_expected = 0
    tracker_dispatch_matched = 0
    for row in tables["DISPATCHOFFERTRK"]:
        interval = _canonical_timestamp(row.get("SETTLEMENTDATE", ""))
        if interval is None:
            continue
        tracker_dispatch_expected += 1
        if (interval, row.get("DUID", "")) in physical_dispatch_keys:
            tracker_dispatch_matched += 1
    tracker_dispatch_rate = _rate(tracker_dispatch_matched, tracker_dispatch_expected)

    identity_intervals: defaultdict[str, list[tuple[datetime, datetime]]] = defaultdict(list)
    for row in tables["DUDETAILSUMMARY"]:
        start = parse_aemo_timestamp(row.get("START_DATE", ""))
        end = parse_aemo_timestamp(row.get("END_DATE", ""))
        if start is not None and end is not None and start < end:
            identity_intervals[row.get("DUID", "")].append((start, end))
    identity_expected = len(physical_dispatch_keys)
    identity_matched = 0
    identity_overlap = 0
    for interval_text, duid in physical_dispatch_keys:
        identity_timestamp = datetime.fromisoformat(interval_text)
        matches = sum(start <= identity_timestamp < end for start, end in identity_intervals.get(duid, []))
        if matches:
            identity_matched += 1
        if matches > 1:
            identity_overlap += 1
    identity_match_rate = _rate(identity_matched, identity_expected)

    downloaded_objects = cast(list[dict[str, object]], download_receipt["objects"])
    retained_objects = cast(list[dict[str, object]], retention_receipt["objects"])
    download_pass_count = sum(item.get("download_pass") is True for item in downloaded_objects)
    r2_verified_count = sum(item.get("verified") is True for item in retained_objects)
    thresholds = cast(dict[str, object], manifest["gates"])
    required_object_count = cast(int, thresholds["required_object_count"])
    required_r2_verified_count = cast(int, thresholds["required_r2_verified_count"])
    required_archive_crc_count = cast(int, thresholds["required_archive_crc_count"])
    required_table_count = cast(int, thresholds["required_table_count"])
    required_nonempty_table_count = cast(int, thresholds["required_nonempty_table_count"])
    maximum_total_data_rows = cast(int, thresholds["maximum_total_data_rows"])
    timestamp_parse_rate_min = cast(float, thresholds["timestamp_parse_rate_min"])
    primary_key_duplicate_count_max = cast(int, thresholds["primary_key_duplicate_count_max"])
    bid_market_date_rate_min = cast(float, thresholds["bid_market_date_rate_min"])
    dispatch_window_rate_min = cast(float, thresholds["dispatch_window_rate_min"])
    bid_period_parent_match_rate_min = cast(float, thresholds["bid_period_parent_match_rate_min"])
    tracker_offer_reference_non_null_rate_min = cast(
        float, thresholds["tracker_offer_reference_non_null_rate_min"]
    )
    tracker_period_match_rate_min = cast(float, thresholds["tracker_period_match_rate_min"])
    tracker_period_ambiguous_rate_max = cast(float, thresholds["tracker_period_ambiguous_rate_max"])
    tracker_dispatch_match_rate_min = cast(float, thresholds["tracker_dispatch_match_rate_min"])
    dispatch_identity_match_rate_min = cast(float, thresholds["dispatch_identity_match_rate_min"])
    dispatch_identity_overlap_count_max = cast(int, thresholds["dispatch_identity_overlap_count_max"])
    gates: dict[str, bool] = {
        "exact_download_object_count": download_pass_count == required_object_count,
        "exact_archive_byte_count": exact_byte_count == required_object_count,
        "r2_retention_verified": r2_verified_count == required_r2_verified_count,
        "archive_crc": crc_pass_count == required_archive_crc_count,
        "archive_parse": archive_pass_count == required_object_count,
        "required_headers": header_pass_count == required_table_count,
        "required_tables_nonempty": nonempty_count == required_nonempty_table_count,
        "row_cap": total_data_rows <= maximum_total_data_rows,
        "timestamp_parse": timestamp_rate >= timestamp_parse_rate_min,
        "primary_key_uniqueness": (duplicate_count <= primary_key_duplicate_count_max),
        "bid_market_date": bid_market_date_rate >= bid_market_date_rate_min,
        "dispatch_market_window": dispatch_window_rate >= dispatch_window_rate_min,
        "bid_period_parent_join": (period_parent_rate >= bid_period_parent_match_rate_min),
        "tracker_offer_reference": (tracker_reference_rate >= tracker_offer_reference_non_null_rate_min),
        "tracker_period_join": tracker_period_match_rate >= tracker_period_match_rate_min,
        "tracker_direction_multiplicity": (
            tracker_period_ambiguous_rate <= tracker_period_ambiguous_rate_max
        ),
        "tracker_dispatch_join": (tracker_dispatch_rate >= tracker_dispatch_match_rate_min),
        "dispatch_identity_join": (identity_match_rate >= dispatch_identity_match_rate_min),
        "identity_nonoverlap": identity_overlap <= dispatch_identity_overlap_count_max,
    }
    overall_pass = all(gates.values())
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "generated_at": generated_at,
        "analyzer_git_commit": analyzer_git_commit,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": source_manifest_sha256,
        "sample_date": SAMPLE_DATE,
        "scientific_role": manifest["scientific_role"],
        "decision": (
            "PASS_MODERN_ROW_CONFORMANCE_SMOKE" if overall_pass else "FAIL_MODERN_ROW_CONFORMANCE_SMOKE"
        ),
        "pass": overall_pass,
        "raw": {
            "download_pass_count": download_pass_count,
            "r2_verified_count": r2_verified_count,
            "archive_parse_pass_count": archive_pass_count,
            "archive_crc_pass_count": crc_pass_count,
            "exact_archive_byte_count": exact_byte_count,
            "compressed_bytes": sum(cast(int, item["observed_bytes"]) for item in downloaded_objects),
            "archive_sha256": {cast(str, item["object_id"]): item["sha256"] for item in downloaded_objects},
        },
        "tables": {
            "row_counts": counts,
            "total_target_rows": total_target_rows,
            "total_data_rows_all_tables": total_data_rows,
            "required_header_pass_count": header_pass_count,
            "primary_key_duplicates": duplicates_by_role,
            "primary_key_duplicate_count": duplicate_count,
        },
        "timestamps": {
            "parsed_count": timestamp_parsed,
            "expected_count": timestamp_expected,
            "parse_rate": timestamp_rate,
            "bid_market_date_match_count": bid_market_date_matches,
            "bid_market_date_expected_count": len(bid_rows),
            "bid_market_date_rate": bid_market_date_rate,
            "dispatch_window_match_count": dispatch_window_matches,
            "dispatch_window_expected_count": dispatch_window_expected,
            "dispatch_window_rate": dispatch_window_rate,
        },
        "joins": {
            "bid_period_parent_match_count": period_parent_matches,
            "bid_period_parent_expected_count": counts["BIDPEROFFER_D"],
            "bid_period_parent_match_rate": period_parent_rate,
            "tracker_count": tracker_count,
            "tracker_offer_reference_count": tracker_eligible,
            "tracker_offer_reference_rate": tracker_reference_rate,
            "tracker_period_match_count": tracker_matched,
            "tracker_period_match_rate": tracker_period_match_rate,
            "tracker_period_ambiguous_count": tracker_ambiguous,
            "tracker_period_ambiguous_rate": tracker_period_ambiguous_rate,
            "physical_dispatch_row_count": len(physical_dispatch_rows),
            "tracker_dispatch_match_count": tracker_dispatch_matched,
            "tracker_dispatch_expected_count": tracker_dispatch_expected,
            "tracker_dispatch_match_rate": tracker_dispatch_rate,
            "dispatch_identity_match_count": identity_matched,
            "dispatch_identity_expected_count": identity_expected,
            "dispatch_identity_match_rate": identity_match_rate,
            "dispatch_identity_overlap_count": identity_overlap,
        },
        "archive_observations": [dict(item) for item in archive_observations],
        "gates": gates,
        "claim_boundary": {
            "validates": "one modern public-report parser/time/key/join pipeline",
            "does_not_validate": [
                "raw participant submission history or rejected actions",
                "historical pre/post-5MS semantic equivalence",
                "dispatch optimization replay",
                "causal effects",
                "model prediction or policy fidelity",
            ],
            "direction_field_absent_from_tracker": True,
        },
        "gpu_used": False,
        "paid_data_used": False,
        "target_outcome_used": False,
        "model_run": False,
    }
