"""Bounded inventory of date-partitioned historical AEMO NEMDE archives."""

from __future__ import annotations

import hashlib
import json
import re
import struct
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import cast
from urllib.parse import urlparse

import yaml

from ecomd.research.aemo_row_conformance import file_sha256

SCHEMA_VERSION = "ecophys-aemo-nemde-tail-inventory/v1"
DOWNLOAD_SCHEMA_VERSION = "ecophys-aemo-nemde-tail-inventory-download/v1"
RETENTION_SCHEMA_VERSION = "ecophys-aemo-nemde-tail-inventory-retention/v1"
SUMMARY_SCHEMA_VERSION = "ecophys-aemo-nemde-tail-inventory-summary/v1"
SOURCE_MANIFEST_PATH = "data/manifests/aemo_nemde_tail_inventory_v1.yaml"
EXPECTED_PARENT_COMMIT = "c208f199da24338b9a61dae6cdd1c8967108cab1"
TAIL_BYTES = 1024 * 1024
LATER_MEMBER_RANGE_CAP_BYTES = 2 * 1024 * 1024
EOCD = struct.Struct("<4s4H2LH")
CENTRAL_HEADER = struct.Struct("<4s6H3I5H2I")
EOCD_SIGNATURE = b"PK\x05\x06"
CENTRAL_SIGNATURE = b"PK\x01\x02"
MEMBER_PATTERN = re.compile(
    r"(?:^|/)NemSpdOutputs_(?P<date>\d{8})(?P<interval>\d{3}).*\.loaded$",
    re.IGNORECASE,
)
EXPECTED_OBJECTS: tuple[dict[str, object], ...] = (
    {
        "object_id": "pre-5ms-nemde-tail-2021-01-01",
        "sample_label": "consumed-development-pre-5ms-2021-01-01",
        "market_date": "2021-01-01",
        "mechanism_phase": "A0_30_MINUTE_ONLY",
        "url": "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/NEMDE/2021/NEMDE_2021_01/NEMDE_Market_Data/NEMDE_Files/NemSpdOutputs_20210101_loaded.zip",
        "expected_archive_bytes": 116_002_085,
        "expected_filename": "NemSpdOutputs_20210101_loaded.tail-1048576.bin",
        "expected_member_date": "20210101",
        "r2_key": "raw/aemo/v14_nemde_tail_inventory/NemSpdOutputs_20210101_loaded.tail-1048576.bin",
    },
    {
        "object_id": "post-5ms-nemde-tail-2021-12-01",
        "sample_label": "consumed-development-post-5ms-2021-12-01",
        "market_date": "2021-12-01",
        "mechanism_phase": "A3_5MS_PLUS_WDR",
        "url": "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/NEMDE/2021/NEMDE_2021_12/NEMDE_Market_Data/NEMDE_Files/NemSpdOutputs_20211201_loaded.zip",
        "expected_archive_bytes": 132_455_595,
        "expected_filename": "NemSpdOutputs_20211201_loaded.tail-1048576.bin",
        "expected_member_date": "20211201",
        "r2_key": "raw/aemo/v14_nemde_tail_inventory/NemSpdOutputs_20211201_loaded.tail-1048576.bin",
    },
)


def load_manifest(path: str | Path) -> dict[str, object]:
    """Load the frozen NEMDE tail manifest."""

    payload: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("NEMDE tail manifest root must be a mapping")
    return cast(dict[str, object], payload)


def load_json(path: str | Path) -> dict[str, object]:
    """Load a JSON mapping."""

    payload: object = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be a mapping")
    return cast(dict[str, object], payload)


def manifest_sha256(path: str | Path) -> str:
    """Hash exact manifest bytes."""

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _utc(value: object) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        parsed = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError:
        return False
    return parsed.tzinfo == UTC


def _sha(value: object, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in "0123456789abcdef" for character in value)
    )


def _safe_relative(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts


def validate_manifest(manifest: Mapping[str, object]) -> tuple[str, ...]:
    """Validate the immutable NEMDE metadata-only experiment boundary."""

    errors: list[str] = []
    expected_root = {
        "schema_version",
        "sample_id",
        "frozen_at",
        "parent_commit",
        "scientific_role",
        "source_contract",
        "selection",
        "range_contract",
        "objects",
        "retention_contract",
        "gates",
        "outputs",
    }
    if set(manifest) != expected_root:
        errors.append("manifest root keys changed")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append("manifest schema changed")
    if manifest.get("parent_commit") != EXPECTED_PARENT_COMMIT:
        errors.append("manifest parent commit changed")
    if not _utc(manifest.get("frozen_at")):
        errors.append("manifest frozen_at is invalid")
    if manifest.get("scientific_role") != "development_only_nemde_archive_addressability":
        errors.append("manifest scientific role changed")
    source = manifest.get("source_contract")
    if not isinstance(source, Mapping) or dict(source) != {
        "official_archive_role": "production_nemde_input_output_and_price_setter_files_per_dispatch_interval",
        "archive_access": "public_unauthenticated_no_charge_at_freeze",
        "current_general_permission_url": "https://www.aemo.com.au/privacy-and-legal-notices/copyright-permissions",
        "current_general_permission_requires_attribution": True,
        "archive_specific_notice_url": "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/NEMDE/2021/NEMDE_2021_12/NEMDE_Market_Data/disclaimer.htm",
        "archive_specific_notice_is_more_restrictive": True,
        "redistribution_status": "ambiguous_pending_written_clarification",
        "raw_redistribution_allowed_by_this_protocol": False,
        "solver_executable_or_queue_access_implied": False,
    }:
        errors.append("source contract changed")
    selection = manifest.get("selection")
    if not isinstance(selection, Mapping) or dict(selection) != {
        "rule": "first_daily_nemde_output_archive_in_each_consumed_development_month",
        "months": ["2021-01", "2021-12"],
        "dates": ["2021-01-01", "2021-12-01"],
        "held_out_status": "development_consumed_not_eligible_for_confirmation",
        "replacement_allowed": False,
        "target_interval_id_for_later_protocol": 144,
    }:
        errors.append("selection contract changed")
    ranges = manifest.get("range_contract")
    if not isinstance(ranges, Mapping) or dict(ranges) != {
        "request_header": "Range: bytes=-1048576",
        "exact_response_bytes_per_object": TAIL_BYTES,
        "maximum_total_response_bytes": 2 * TAIL_BYTES,
        "full_download_fallback_allowed": False,
        "range_extension_allowed": False,
        "parse_before_r2_retention_allowed": False,
        "xml_member_access_allowed": False,
    }:
        errors.append("range contract changed")
    objects = manifest.get("objects")
    if not isinstance(objects, list) or objects != list(EXPECTED_OBJECTS):
        errors.append("object contract changed")
    else:
        for index, item in enumerate(cast(list[dict[str, object]], objects)):
            parsed = urlparse(cast(str, item["url"]))
            if (
                parsed.scheme != "https"
                or parsed.hostname != "www.nemweb.com.au"
                or parsed.query
                or parsed.fragment
            ):
                errors.append(f"objects[{index}] URL is outside AEMO")
    retention = manifest.get("retention_contract")
    if not isinstance(retention, Mapping) or dict(retention) != {
        "bucket": "ecophys",
        "prefix": "raw/aemo/v14_nemde_tail_inventory/",
        "upload_before_zip_metadata_parse": True,
        "remote_sha256_metadata_required": True,
        "overwrite_mismatched_remote_object_allowed": False,
        "raw_tails_committed_to_git": False,
    }:
        errors.append("retention contract changed")
    gates = manifest.get("gates")
    if not isinstance(gates, Mapping) or dict(gates) != {
        "required_object_count": 2,
        "required_r2_verified_count": 2,
        "required_eocd_count": 2,
        "required_complete_central_directory_count": 2,
        "required_interval_set": {"start": 1, "end": 288},
        "encrypted_member_count_max": 0,
        "allowed_compression_methods": [0, 8],
        "later_member_range_cap_bytes": LATER_MEMBER_RANGE_CAP_BYTES,
        "licence_clarification_required_before_raw_redistribution": True,
        "exact_solver_replay_claim_allowed": False,
        "participant_adaptation_claim_allowed": False,
        "causal_claim_allowed": False,
        "model_claim_allowed": False,
        "gpu_allowed": False,
        "paid_data_allowed": False,
    }:
        errors.append("gate contract changed")
    outputs = manifest.get("outputs")
    required_outputs = {"raw_root", "download_receipt", "retention_receipt", "summary"}
    if not isinstance(outputs, Mapping) or set(outputs) != required_outputs:
        errors.append("output contract changed")
    elif any(not _safe_relative(value) for value in outputs.values()):
        errors.append("output path is unsafe")
    return tuple(errors)


def _content_range(headers: Mapping[str, str]) -> tuple[int, int, int] | None:
    value = next(
        (raw for key, raw in headers.items() if key.lower() == "content-range"),
        None,
    )
    match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", value) if value else None
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def validate_download_receipt(
    receipt: Mapping[str, object], manifest: Mapping[str, object]
) -> tuple[str, ...]:
    """Validate exact opaque suffix downloads without parsing ZIP metadata."""

    errors: list[str] = []
    if receipt.get("schema_version") != DOWNLOAD_SCHEMA_VERSION:
        errors.append("download schema changed")
    if not _utc(receipt.get("generated_at")):
        errors.append("download generated_at is invalid")
    if not _sha(receipt.get("protocol_git_commit"), 40):
        errors.append("download protocol commit is invalid")
    if receipt.get("source_manifest") != SOURCE_MANIFEST_PATH:
        errors.append("download source manifest changed")
    if not _sha(receipt.get("source_manifest_sha256"), 64):
        errors.append("download manifest SHA is invalid")
    if receipt.get("request_policy") != "one_fixed_suffix_range_per_object_no_retry_no_extension":
        errors.append("download request policy changed")
    if receipt.get("zip_metadata_opened") is not False or receipt.get("xml_member_opened") is not False:
        errors.append("download accessed archive content")
    raw_objects = receipt.get("objects")
    specs = cast(list[dict[str, object]], manifest["objects"])
    if not isinstance(raw_objects, list) or len(raw_objects) != len(specs):
        errors.append("download object count changed")
        return tuple(errors)
    for index, (raw, spec) in enumerate(zip(raw_objects, specs, strict=True)):
        if not isinstance(raw, Mapping):
            errors.append(f"download object {index} is not a mapping")
            continue
        total = cast(int, spec["expected_archive_bytes"])
        expected_range = (total - TAIL_BYTES, total - 1, total)
        if raw.get("request_index") != index or raw.get("request_count") != 1:
            errors.append(f"download object {index} request count changed")
        if raw.get("object_id") != spec["object_id"] or raw.get("url") != spec["url"]:
            errors.append(f"download object {index} identity changed")
        if raw.get("http_status") != 206:
            errors.append(f"download object {index} HTTP status is not 206")
        headers = raw.get("response_headers")
        if not isinstance(headers, Mapping) or _content_range(cast(Mapping[str, str], headers)) != expected_range:
            errors.append(f"download object {index} Content-Range changed")
        if raw.get("observed_bytes") != TAIL_BYTES or not _sha(raw.get("sha256"), 64):
            errors.append(f"download object {index} bytes or SHA changed")
        if raw.get("local_filename") != spec["expected_filename"]:
            errors.append(f"download object {index} filename changed")
        if raw.get("transport_error") is not None or raw.get("download_pass") is not True:
            errors.append(f"download object {index} did not pass")
        if raw.get("zip_metadata_opened") is not False or raw.get("xml_member_opened") is not False:
            errors.append(f"download object {index} accessed content")
    if receipt.get("pass") is not True:
        errors.append("download did not pass")
    return tuple(errors)


def validate_retention_receipt(
    receipt: Mapping[str, object],
    download: Mapping[str, object],
    manifest: Mapping[str, object],
) -> tuple[str, ...]:
    """Validate the R2 retention chain for exact suffix bytes."""

    errors: list[str] = []
    if receipt.get("schema_version") != RETENTION_SCHEMA_VERSION:
        errors.append("retention schema changed")
    if not _utc(receipt.get("generated_at")):
        errors.append("retention generated_at is invalid")
    if receipt.get("protocol_git_commit") != download.get("protocol_git_commit"):
        errors.append("retention protocol commit changed")
    if receipt.get("source_manifest") != SOURCE_MANIFEST_PATH:
        errors.append("retention source manifest changed")
    if receipt.get("source_manifest_sha256") != download.get("source_manifest_sha256"):
        errors.append("retention manifest SHA changed")
    if receipt.get("bucket") != "ecophys" or receipt.get("prefix") != "raw/aemo/v14_nemde_tail_inventory/":
        errors.append("retention location changed")
    if receipt.get("zip_metadata_opened") is not False or receipt.get("xml_member_opened") is not False:
        errors.append("retention accessed archive content")
    raw_retained = receipt.get("objects")
    raw_downloaded = download.get("objects")
    specs = cast(list[dict[str, object]], manifest["objects"])
    if not isinstance(raw_retained, list) or not isinstance(raw_downloaded, list):
        errors.append("retention objects are invalid")
        return tuple(errors)
    if len(raw_retained) != len(specs) or len(raw_downloaded) != len(specs):
        errors.append("retention object count changed")
        return tuple(errors)
    for index, (retained, downloaded, spec) in enumerate(
        zip(raw_retained, raw_downloaded, specs, strict=True)
    ):
        if not isinstance(retained, Mapping) or not isinstance(downloaded, Mapping):
            errors.append(f"retention object {index} is invalid")
            continue
        expected_sha = downloaded.get("sha256")
        if retained.get("object_id") != spec["object_id"] or retained.get("r2_key") != spec["r2_key"]:
            errors.append(f"retention object {index} identity changed")
        if (
            retained.get("observed_bytes") != TAIL_BYTES
            or retained.get("remote_content_length") != TAIL_BYTES
            or retained.get("sha256") != expected_sha
            or retained.get("remote_metadata_sha256") != expected_sha
            or retained.get("verified") is not True
        ):
            errors.append(f"retention object {index} was not hash-verified")
    if receipt.get("all_verified") is not True:
        errors.append("retention did not verify every object")
    return tuple(errors)


def verify_local_tails(
    raw_root: str | Path,
    download: Mapping[str, object],
    manifest: Mapping[str, object],
) -> tuple[str, ...]:
    """Verify local opaque suffixes against the download receipt."""

    errors: list[str] = []
    downloaded = cast(list[dict[str, object]], download["objects"])
    specs = cast(list[dict[str, object]], manifest["objects"])
    for index, (item, spec) in enumerate(zip(downloaded, specs, strict=True)):
        path = Path(raw_root) / cast(str, spec["expected_filename"])
        if not path.is_file():
            errors.append(f"local tail {index} is absent")
        elif path.stat().st_size != TAIL_BYTES or file_sha256(path) != item["sha256"]:
            errors.append(f"local tail {index} differs from receipt")
    return tuple(errors)


def _parse_error_result(spec: Mapping[str, object], message: str) -> dict[str, object]:
    return {
        "object_id": spec["object_id"],
        "eocd_found": False,
        "central_directory_complete": False,
        "parse_error": message,
        "member_count": 0,
        "matching_member_count": 0,
        "interval_ids": [],
        "complete_interval_set": False,
        "encrypted_member_count": 0,
        "unsupported_compression_member_count": 0,
        "target_member": None,
        "target_range_within_cap": False,
    }


def parse_zip_tail(path: str | Path, spec: Mapping[str, object]) -> dict[str, object]:
    """Parse an EOCD and complete central directory from one retained ZIP suffix."""

    data = Path(path).read_bytes()
    if len(data) != TAIL_BYTES:
        return _parse_error_result(spec, "tail byte count differs from frozen range")
    eocd_relative = data.rfind(EOCD_SIGNATURE)
    if eocd_relative < 0 or eocd_relative + EOCD.size > len(data):
        return _parse_error_result(spec, "EOCD not found in retained suffix")
    (
        signature,
        disk_number,
        central_disk,
        entries_on_disk,
        total_entries,
        central_bytes,
        central_offset,
        comment_bytes,
    ) = EOCD.unpack_from(data, eocd_relative)
    archive_bytes = cast(int, spec["expected_archive_bytes"])
    tail_start = archive_bytes - TAIL_BYTES
    if signature != EOCD_SIGNATURE:
        return _parse_error_result(spec, "EOCD signature changed")
    if eocd_relative + EOCD.size + comment_bytes != len(data):
        return _parse_error_result(spec, "EOCD does not terminate the declared archive")
    if (
        disk_number != 0
        or central_disk != 0
        or entries_on_disk != total_entries
        or total_entries == 0xFFFF
        or central_bytes == 0xFFFFFFFF
        or central_offset == 0xFFFFFFFF
    ):
        return _parse_error_result(spec, "multi-disk or ZIP64 archive is outside v1")
    central_relative = central_offset - tail_start
    central_end_relative = central_relative + central_bytes
    if central_relative < 0 or central_end_relative > eocd_relative:
        result = _parse_error_result(spec, "central directory is not complete in suffix")
        result["eocd_found"] = True
        result["eocd_absolute_offset"] = tail_start + eocd_relative
        result["declared_member_count"] = total_entries
        result["declared_central_directory_bytes"] = central_bytes
        return result

    cursor = central_relative
    entries: list[dict[str, object]] = []
    parse_error: str | None = None
    for _ in range(total_entries):
        if cursor + CENTRAL_HEADER.size > central_end_relative:
            parse_error = "central directory entry header is truncated"
            break
        fields = CENTRAL_HEADER.unpack_from(data, cursor)
        if fields[0] != CENTRAL_SIGNATURE:
            parse_error = "central directory signature changed"
            break
        flags = fields[3]
        compression_method = fields[4]
        crc32 = fields[7]
        compressed_bytes = fields[8]
        uncompressed_bytes = fields[9]
        filename_bytes = fields[10]
        extra_bytes = fields[11]
        member_comment_bytes = fields[12]
        disk_start = fields[13]
        local_header_offset = fields[16]
        entry_end = cursor + CENTRAL_HEADER.size + filename_bytes + extra_bytes + member_comment_bytes
        if entry_end > central_end_relative:
            parse_error = "central directory variable fields are truncated"
            break
        raw_name = data[cursor + CENTRAL_HEADER.size : cursor + CENTRAL_HEADER.size + filename_bytes]
        encoding = "utf-8" if flags & 0x800 else "cp437"
        try:
            name = raw_name.decode(encoding)
        except UnicodeDecodeError:
            parse_error = "central directory filename cannot be decoded"
            break
        entries.append(
            {
                "name": name,
                "flags": flags,
                "compression_method": compression_method,
                "crc32": f"{crc32:08x}",
                "compressed_bytes": compressed_bytes,
                "uncompressed_bytes": uncompressed_bytes,
                "disk_start": disk_start,
                "local_header_offset": local_header_offset,
            }
        )
        cursor = entry_end
    if parse_error is None and cursor != central_end_relative:
        parse_error = "central directory byte count differs from EOCD"

    inventory_lines = [
        "\t".join(
            str(entry[key])
            for key in (
                "name",
                "flags",
                "compression_method",
                "crc32",
                "compressed_bytes",
                "uncompressed_bytes",
                "disk_start",
                "local_header_offset",
            )
        )
        for entry in entries
    ]
    matching: list[tuple[int, dict[str, object]]] = []
    wrong_date_count = 0
    expected_date = cast(str, spec["expected_member_date"])
    for entry in entries:
        match = MEMBER_PATTERN.search(cast(str, entry["name"]))
        if match is None:
            continue
        if match.group("date") != expected_date:
            wrong_date_count += 1
        matching.append((int(match.group("interval")), entry))
    interval_ids = sorted({interval for interval, _ in matching})
    target_candidates = sorted(
        (entry for interval, entry in matching if interval == 144),
        key=lambda item: (cast(str, item["name"]), cast(int, item["local_header_offset"])),
    )
    target = target_candidates[0] if target_candidates else None
    target_range_upper_bound = (
        30 + 65535 + cast(int, target["compressed_bytes"]) if target is not None else None
    )
    encrypted = sum(bool(cast(int, entry["flags"]) & 1) for entry in entries)
    unsupported = sum(cast(int, entry["compression_method"]) not in {0, 8} for entry in entries)
    complete = parse_error is None and len(entries) == total_entries
    return {
        "object_id": spec["object_id"],
        "eocd_found": True,
        "eocd_absolute_offset": tail_start + eocd_relative,
        "central_directory_absolute_offset": central_offset,
        "central_directory_bytes": central_bytes,
        "central_directory_complete": complete,
        "parse_error": parse_error,
        "member_count": len(entries),
        "declared_member_count": total_entries,
        "member_inventory_sha256": hashlib.sha256("\n".join(inventory_lines).encode()).hexdigest(),
        "matching_member_count": len(matching),
        "wrong_member_date_count": wrong_date_count,
        "interval_ids": interval_ids,
        "complete_interval_set": interval_ids == list(range(1, 289)),
        "encrypted_member_count": encrypted,
        "unsupported_compression_member_count": unsupported,
        "target_candidate_count": len(target_candidates),
        "target_member": target,
        "target_range_upper_bound_bytes": target_range_upper_bound,
        "target_range_within_cap": (
            target_range_upper_bound is not None
            and target_range_upper_bound <= LATER_MEMBER_RANGE_CAP_BYTES
        ),
        "first_member_name": entries[0]["name"] if entries else None,
        "last_member_name": entries[-1]["name"] if entries else None,
    }


def summarize_inventory(
    parsed: list[dict[str, object]],
    retention: Mapping[str, object],
    manifest: Mapping[str, object],
    *,
    source_manifest_sha256: str,
    analyzer_git_commit: str,
    generated_at: str,
) -> dict[str, object]:
    """Apply immutable gates and summarize archive addressability."""

    retained = retention.get("objects")
    r2_verified = (
        sum(item.get("verified") is True for item in retained)
        if isinstance(retained, list) and all(isinstance(item, Mapping) for item in retained)
        else 0
    )
    eocd_count = sum(item.get("eocd_found") is True for item in parsed)
    central_count = sum(item.get("central_directory_complete") is True for item in parsed)
    complete_interval_count = sum(item.get("complete_interval_set") is True for item in parsed)
    target_count = sum(item.get("target_range_within_cap") is True for item in parsed)
    encrypted_count = sum(cast(int, item.get("encrypted_member_count", 0)) for item in parsed)
    unsupported_count = sum(
        cast(int, item.get("unsupported_compression_member_count", 0)) for item in parsed
    )
    wrong_date_count = sum(cast(int, item.get("wrong_member_date_count", 0)) for item in parsed)
    passed = (
        len(parsed) == 2
        and r2_verified == 2
        and eocd_count == 2
        and central_count == 2
        and complete_interval_count == 2
        and target_count == 2
        and encrypted_count == 0
        and unsupported_count == 0
        and wrong_date_count == 0
    )
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "generated_at": generated_at,
        "analyzer_git_commit": analyzer_git_commit,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": source_manifest_sha256,
        "decision": "PASS_NEMDE_TAIL_INVENTORY" if passed else "FAIL_NEMDE_TAIL_INVENTORY",
        "pass": passed,
        "counts": {
            "object_count": len(parsed),
            "r2_verified_count": r2_verified,
            "eocd_count": eocd_count,
            "complete_central_directory_count": central_count,
            "complete_288_interval_set_count": complete_interval_count,
            "target_range_within_cap_count": target_count,
            "encrypted_member_count": encrypted_count,
            "unsupported_compression_member_count": unsupported_count,
            "wrong_member_date_count": wrong_date_count,
        },
        "objects": parsed,
        "claim_boundary": {
            "daily_archive_structure_validated": passed,
            "single_interval_range_sampling_unlocked": passed,
            "xml_schema_validated": False,
            "input_output_semantics_validated": False,
            "exact_solver_replay_validated": False,
            "participant_adaptation_validated": False,
            "causal_or_model_claim_allowed": False,
            "raw_redistribution_allowed": False,
            "licence_clarification_still_required": True,
        },
        "resources": {
            "downloaded_bytes": 2 * TAIL_BYTES,
            "gpu_hours": 0,
            "paid_data_spend": 0,
            "target_outcomes_used": False,
        },
    }
