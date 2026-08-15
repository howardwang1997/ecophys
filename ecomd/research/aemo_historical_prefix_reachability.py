"""Bounded historical AEMO ZIP-prefix reachability audit."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import struct
import zlib
from collections import OrderedDict
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime
from pathlib import Path, PurePosixPath
from typing import BinaryIO, cast
from urllib.parse import urlparse

import yaml

from ecomd.research.aemo_row_conformance import file_sha256

SCHEMA_VERSION = "ecophys-aemo-historical-prefix-reachability/v1"
DOWNLOAD_SCHEMA_VERSION = "ecophys-aemo-historical-prefix-reachability-download/v1"
RETENTION_SCHEMA_VERSION = "ecophys-aemo-historical-prefix-reachability-retention/v1"
SUMMARY_SCHEMA_VERSION = "ecophys-aemo-historical-prefix-reachability-summary/v1"
SOURCE_MANIFEST_PATH = "data/manifests/aemo_historical_prefix_reachability_v1.yaml"
EXPECTED_PARENT_COMMIT = "0fc24416bd6c0a0ab2a2865d3d7d817c25b60a34"
RANGE_BYTES = 64 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 1024 * 1024 * 1024
INFLATE_INPUT_CHUNK_BYTES = 64 * 1024
INFLATE_OUTPUT_CHUNK_BYTES = 1024 * 1024
LOCAL_FILE_SIGNATURE = 0x04034B50
LOCAL_FILE_HEADER = struct.Struct("<IHHHHHIIIHH")
EXPECTED_OBJECTS: tuple[dict[str, object], ...] = (
    {
        "object_id": "pre-bridge-bidperoffer-prefix-2021-01",
        "sample_label": "consumed-development-pre-bridge-2021-01",
        "month": "2021-01",
        "mechanism_phase": "A0_30_MINUTE_ONLY",
        "observation_phase": "O0_LEGACY_REPORTS",
        "logical_role": "BIDPEROFFER",
        "url": "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/2021/MMSDM_2021_01/MMSDM_Historical_Data_SQLLoader/DATA/PUBLIC_DVD_BIDPEROFFER_202101010000.zip",
        "expected_filename": "PUBLIC_DVD_BIDPEROFFER_202101010000.prefix-67108864.bin",
        "expected_member": "PUBLIC_DVD_BIDPEROFFER_202101010000.CSV",
        "expected_archive_bytes": 95_238_254,
        "expected_package": "OFFER",
        "expected_table": "BIDPEROFFER",
        "expected_version": "1",
        "market_day_field": "SETTLEMENTDATE",
        "expected_first_market_day": "2021-01-01",
        "required_fields": [
            "SETTLEMENTDATE",
            "OFFERDATE",
            "PERIODID",
            "VERSIONNO",
            "DUID",
            "BIDTYPE",
            "MAXAVAIL",
        ],
        "r2_key": "raw/aemo/v14_historical_prefix_reachability/pre-bridge-bidperoffer-prefix-2021-01.prefix-67108864.bin",
    },
    {
        "object_id": "post-v51-bidperoffer-prefix-2021-12",
        "sample_label": "consumed-development-post-v51-2021-12",
        "month": "2021-12",
        "mechanism_phase": "A3_5MS_PLUS_WDR",
        "observation_phase": "O4_V51_CLUSTERED_RELEASE",
        "logical_role": "BIDPEROFFER",
        "url": "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/2021/MMSDM_2021_12/MMSDM_Historical_Data_SQLLoader/DATA/PUBLIC_DVD_BIDPEROFFER_202112010000.zip",
        "expected_filename": "PUBLIC_DVD_BIDPEROFFER_202112010000.prefix-67108864.bin",
        "expected_member": "PUBLIC_DVD_BIDPEROFFER_202112010000.CSV",
        "expected_archive_bytes": 1_610_349_080,
        "expected_package": "BIDS",
        "expected_table": "BIDOFFERPERIOD",
        "expected_version": "1",
        "market_day_field": "TRADINGDATE",
        "expected_first_market_day": "2021-12-01",
        "required_fields": [
            "TRADINGDATE",
            "OFFERDATETIME",
            "PERIODID",
            "DUID",
            "BIDTYPE",
            "MAXAVAIL",
        ],
        "r2_key": "raw/aemo/v14_historical_prefix_reachability/post-v51-bidperoffer-prefix-2021-12.prefix-67108864.bin",
    },
)


def load_manifest(path: str | Path) -> dict[str, object]:
    """Load the frozen reachability manifest."""

    payload: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical-prefix manifest root must be a mapping")
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
    """Validate the exact development-only prefix experiment boundary."""

    errors: list[str] = []
    expected_root = {
        "schema_version",
        "sample_id",
        "frozen_at",
        "parent_commit",
        "scientific_role",
        "prior_evidence",
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
    if manifest.get("scientific_role") != "development_only_historical_prefix_reachability":
        errors.append("manifest scientific role changed")
    prior = manifest.get("prior_evidence")
    if not isinstance(prior, Mapping) or (
        prior.get("source_contract_decision") != "PASS_TRANSFER_REPAIR_AND_SOURCE_HEADER_CONFIRMATION"
        or prior.get("source_contract_summary_sha256")
        != "e4bac4ac57b8b25b8d91a3465eba544c9c9e22050c47750c89344e339f6417c4"
        or prior.get("modern_panel_decision") != "PASS_MODERN_BUNDLE_STABILITY_PANEL"
        or prior.get("modern_panel_summary_sha256")
        != "d939fffd8bc7673eb0aac78e06ae2abf38b1ea27e81cba67d03c355bec77ec88"
    ):
        errors.append("prior evidence changed")
    selection = manifest.get("selection")
    if not isinstance(selection, Mapping) or dict(selection) != {
        "rule": "reuse_consumed_header_only_months_for_order_feasibility_not_confirmation",
        "months": ["2021-01", "2021-12"],
        "previous_market_rows_opened": False,
        "held_out_status": "development_consumed_not_eligible_for_confirmation",
        "replacement_allowed": False,
    }:
        errors.append("selection contract changed")
    range_contract = manifest.get("range_contract")
    if not isinstance(range_contract, Mapping) or dict(range_contract) != {
        "request_header": "Range: bytes=0-67108863",
        "exact_response_bytes_per_object": RANGE_BYTES,
        "maximum_total_response_bytes": 2 * RANGE_BYTES,
        "maximum_uncompressed_bytes_per_object": MAX_UNCOMPRESSED_BYTES,
        "full_download_fallback_allowed": False,
        "range_extension_allowed": False,
        "parse_before_r2_retention_allowed": False,
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
        "prefix": "raw/aemo/v14_historical_prefix_reachability/",
        "upload_before_any_csv_row_parse": True,
        "remote_sha256_metadata_required": True,
        "overwrite_mismatched_remote_object_allowed": False,
        "raw_prefixes_committed_to_git": False,
    }:
        errors.append("retention contract changed")
    gates = manifest.get("gates")
    if not isinstance(gates, Mapping) or dict(gates) != {
        "required_object_count": 2,
        "required_r2_verified_count": 2,
        "required_header_contract_count": 2,
        "required_first_market_day_count": 2,
        "required_second_market_day_reached_count": 2,
        "required_chronological_prefix_count": 2,
        "timestamp_parse_rate_min": 1.0,
        "malformed_row_count_max": 0,
        "complete_archive_transfer_count_max": 0,
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
    """Validate two exact opaque prefix downloads without inspecting content."""

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
    if receipt.get("request_policy") != "one_fixed_range_get_per_object_no_retry_no_extension":
        errors.append("download request policy changed")
    if receipt.get("zip_opened") is not False or receipt.get("csv_rows_opened") is not False:
        errors.append("download accessed content")
    raw_objects = receipt.get("objects")
    specs = cast(list[dict[str, object]], manifest["objects"])
    if not isinstance(raw_objects, list) or len(raw_objects) != len(specs):
        errors.append("download object count changed")
        return tuple(errors)
    for index, (raw, spec) in enumerate(zip(raw_objects, specs, strict=True)):
        if not isinstance(raw, Mapping):
            errors.append(f"download objects[{index}] is invalid")
            continue
        if raw.get("request_index") != index or raw.get("request_count") != 1:
            errors.append(f"download objects[{index}] request count changed")
        for key in ("object_id", "url", "local_filename"):
            expected_key = "expected_filename" if key == "local_filename" else key
            if raw.get(key) != spec[expected_key]:
                errors.append(f"download objects[{index}] {key} changed")
        if raw.get("http_status") != 206:
            errors.append(f"download objects[{index}] HTTP status changed")
        if raw.get("transport_error") is not None:
            errors.append(f"download objects[{index}] transport failed")
        if raw.get("observed_bytes") != RANGE_BYTES:
            errors.append(f"download objects[{index}] byte count changed")
        if not _sha(raw.get("sha256"), 64):
            errors.append(f"download objects[{index}] SHA is invalid")
        headers = raw.get("response_headers")
        parsed_range = _content_range(cast(Mapping[str, str], headers)) if isinstance(headers, Mapping) else None
        expected_range = (0, RANGE_BYTES - 1, cast(int, spec["expected_archive_bytes"]))
        if parsed_range != expected_range:
            errors.append(f"download objects[{index}] Content-Range changed")
        if raw.get("download_pass") is not True:
            errors.append(f"download objects[{index}] did not pass")
        if raw.get("zip_opened") is not False or raw.get("csv_rows_opened") is not False:
            errors.append(f"download objects[{index}] accessed content")
    if receipt.get("pass") is not True:
        errors.append("download overall pass is false")
    return tuple(errors)


def validate_retention_receipt(
    receipt: Mapping[str, object],
    download: Mapping[str, object],
    manifest: Mapping[str, object],
) -> tuple[str, ...]:
    """Validate R2 retention of both exact prefixes."""

    errors: list[str] = []
    if receipt.get("schema_version") != RETENTION_SCHEMA_VERSION:
        errors.append("retention schema changed")
    if not _utc(receipt.get("generated_at")):
        errors.append("retention generated_at is invalid")
    if receipt.get("protocol_git_commit") != download.get("protocol_git_commit"):
        errors.append("retention protocol commit differs from download")
    if receipt.get("source_manifest") != SOURCE_MANIFEST_PATH:
        errors.append("retention source manifest changed")
    if receipt.get("source_manifest_sha256") != download.get("source_manifest_sha256"):
        errors.append("retention manifest SHA differs from download")
    if receipt.get("bucket") != "ecophys":
        errors.append("retention bucket changed")
    if receipt.get("zip_opened") is not False or receipt.get("csv_rows_opened") is not False:
        errors.append("retention accessed content")
    retained = receipt.get("objects")
    downloaded = cast(list[dict[str, object]], download["objects"])
    specs = cast(list[dict[str, object]], manifest["objects"])
    if not isinstance(retained, list) or len(retained) != len(specs):
        errors.append("retention object count changed")
        return tuple(errors)
    for index, (raw, source, spec) in enumerate(zip(retained, downloaded, specs, strict=True)):
        if not isinstance(raw, Mapping):
            errors.append(f"retention objects[{index}] is invalid")
            continue
        if raw.get("object_id") != spec["object_id"] or raw.get("r2_key") != spec["r2_key"]:
            errors.append(f"retention objects[{index}] identity changed")
        if raw.get("observed_bytes") != source["observed_bytes"]:
            errors.append(f"retention objects[{index}] bytes changed")
        if raw.get("sha256") != source["sha256"]:
            errors.append(f"retention objects[{index}] SHA changed")
        if raw.get("remote_content_length") != source["observed_bytes"]:
            errors.append(f"retention objects[{index}] remote bytes changed")
        if raw.get("remote_metadata_sha256") != source["sha256"]:
            errors.append(f"retention objects[{index}] remote SHA changed")
        if raw.get("verified") is not True:
            errors.append(f"retention objects[{index}] is not verified")
    if receipt.get("all_verified") is not True:
        errors.append("retention overall verification failed")
    return tuple(errors)


def verify_local_prefixes(
    raw_root: str | Path,
    download: Mapping[str, object],
    manifest: Mapping[str, object],
) -> tuple[str, ...]:
    """Verify local prefix paths, exact byte counts and hashes."""

    errors: list[str] = []
    root = Path(raw_root)
    downloaded = cast(list[dict[str, object]], download["objects"])
    specs = cast(list[dict[str, object]], manifest["objects"])
    for index, (raw, spec) in enumerate(zip(downloaded, specs, strict=True)):
        path = root / cast(str, spec["expected_filename"])
        if not path.is_file():
            errors.append(f"local prefix absent: {path}")
            continue
        if path.stat().st_size != raw["observed_bytes"]:
            errors.append(f"local prefix bytes changed at objects[{index}]")
        elif file_sha256(path) != raw["sha256"]:
            errors.append(f"local prefix SHA changed at objects[{index}]")
    return tuple(errors)


def _read_local_header(handle: BinaryIO) -> dict[str, object]:
    header = handle.read(LOCAL_FILE_HEADER.size)
    if len(header) != LOCAL_FILE_HEADER.size:
        raise ValueError("ZIP prefix is shorter than the local file header")
    (
        signature,
        version_needed,
        flags,
        compression_method,
        _modification_time,
        _modification_date,
        _crc32,
        _compressed_size,
        _uncompressed_size,
        filename_length,
        extra_length,
    ) = LOCAL_FILE_HEADER.unpack(header)
    if signature != LOCAL_FILE_SIGNATURE:
        raise ValueError("ZIP prefix does not start with a local file header")
    if flags & 0x1:
        raise ValueError("encrypted ZIP member is unsupported")
    if compression_method != 8:
        raise ValueError(f"ZIP compression method {compression_method} is not deflate")
    filename_bytes = handle.read(filename_length)
    extra = handle.read(extra_length)
    if len(filename_bytes) != filename_length or len(extra) != extra_length:
        raise ValueError("ZIP local header is truncated")
    encoding = "utf-8" if flags & 0x800 else "cp437"
    try:
        member = filename_bytes.decode(encoding)
    except UnicodeDecodeError as error:
        raise ValueError(f"invalid ZIP member filename: {error}") from error
    return {
        "zip_version_needed": version_needed,
        "zip_flags": flags,
        "compression_method": compression_method,
        "member": member,
        "data_offset": LOCAL_FILE_HEADER.size + filename_length + extra_length,
    }


def _parse_market_day(value: str) -> date:
    text = value.strip()[:10]
    for pattern in ("%Y/%m/%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    raise ValueError(f"invalid AEMO market day {value!r}")


def _row(line: bytes) -> list[str]:
    try:
        text = line.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError(f"invalid MMSDM UTF-8 row: {error}") from error
    try:
        rows = list(csv.reader(io.StringIO(text, newline=""), strict=True))
    except csv.Error as error:
        raise ValueError(f"invalid MMSDM CSV row: {error}") from error
    if len(rows) != 1:
        raise ValueError("MMSDM physical line did not contain exactly one CSV row")
    return rows[0]


def parse_offer_prefix(path: str | Path, spec: Mapping[str, object]) -> dict[str, object]:
    """Stream a retained partial ZIP and measure whether it reaches a second market day."""

    prefix_path = Path(path)
    information_row: list[str] | None = None
    header_fields: list[str] = []
    market_day_index: int | None = None
    day_counts: OrderedDict[str, int] = OrderedDict()
    data_row_count = 0
    timestamp_parse_count = 0
    timestamp_failure_count = 0
    malformed_row_count = 0
    non_data_rows_before_header = 0
    previous_day: date | None = None
    chronological = True
    first_transition_compressed_upper_bound: int | None = None
    trailing = b""
    uncompressed_bytes = 0
    compressed_bytes_fed = 0
    uncompressed_cap_hit = False
    deflate_eof = False
    with prefix_path.open("rb") as handle:
        local = _read_local_header(handle)
        decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
        while chunk := handle.read(INFLATE_INPUT_CHUNK_BYTES):
            compressed_bytes_fed += len(chunk)
            pending = chunk
            while pending:
                remaining = MAX_UNCOMPRESSED_BYTES - uncompressed_bytes
                if remaining <= 0:
                    uncompressed_cap_hit = True
                    break
                try:
                    output = decompressor.decompress(
                        pending,
                        min(INFLATE_OUTPUT_CHUNK_BYTES, remaining),
                    )
                except zlib.error as error:
                    raise ValueError(f"invalid deflate prefix: {error}") from error
                pending = decompressor.unconsumed_tail
                uncompressed_bytes += len(output)
                lines = (trailing + output).split(b"\n")
                trailing = lines.pop()
                for raw_line in lines:
                    line = raw_line.removesuffix(b"\r")
                    if not line:
                        continue
                    try:
                        row = _row(line)
                    except ValueError:
                        malformed_row_count += 1
                        continue
                    if not row:
                        continue
                    row_type = row[0].strip().lstrip("\ufeff").upper()
                    if information_row is None:
                        if row_type == "D":
                            raise ValueError("data row encountered before information header")
                        if row_type != "I":
                            non_data_rows_before_header += 1
                            continue
                        if len(row) < 5:
                            raise ValueError("information header has fewer than five fields")
                        information_row = row
                        header_fields = [field.strip() for field in row[4:]]
                        market_day_field = cast(str, spec["market_day_field"])
                        if market_day_field not in header_fields:
                            raise ValueError(f"missing market-day field {market_day_field}")
                        market_day_index = 4 + header_fields.index(market_day_field)
                        continue
                    if row_type != "D":
                        continue
                    data_row_count += 1
                    if market_day_index is None or market_day_index >= len(row):
                        malformed_row_count += 1
                        continue
                    try:
                        market_day = _parse_market_day(row[market_day_index])
                    except ValueError:
                        timestamp_failure_count += 1
                        continue
                    timestamp_parse_count += 1
                    if previous_day is not None and market_day < previous_day:
                        chronological = False
                    previous_day = market_day
                    day_text = market_day.isoformat()
                    if (
                        day_text not in day_counts
                        and day_counts
                        and first_transition_compressed_upper_bound is None
                    ):
                        first_transition_compressed_upper_bound = (
                            cast(int, local["data_offset"]) + compressed_bytes_fed
                        )
                    day_counts[day_text] = day_counts.get(day_text, 0) + 1
                if uncompressed_bytes >= MAX_UNCOMPRESSED_BYTES:
                    uncompressed_cap_hit = True
                    break
                if not pending:
                    break
            if uncompressed_cap_hit or decompressor.eof:
                deflate_eof = decompressor.eof
                break
    if information_row is None:
        raise ValueError("no information header in retained ZIP prefix")
    days = list(day_counts)
    return {
        **local,
        "compressed_prefix_bytes": prefix_path.stat().st_size,
        "compressed_payload_bytes_fed": compressed_bytes_fed,
        "uncompressed_bytes": uncompressed_bytes,
        "uncompressed_cap_hit": uncompressed_cap_hit,
        "deflate_eof": deflate_eof,
        "trailing_partial_bytes": len(trailing),
        "non_data_rows_before_header": non_data_rows_before_header,
        "header_package": information_row[1].strip(),
        "header_table": information_row[2].strip(),
        "header_version": information_row[3].strip(),
        "header_fields": header_fields,
        "data_row_count": data_row_count,
        "timestamp_parse_count": timestamp_parse_count,
        "timestamp_failure_count": timestamp_failure_count,
        "timestamp_parse_rate": timestamp_parse_count / data_row_count if data_row_count else 0.0,
        "malformed_row_count": malformed_row_count,
        "distinct_market_days": days,
        "market_day_counts": dict(day_counts),
        "first_market_day": days[0] if days else None,
        "last_market_day": days[-1] if days else None,
        "chronological_non_decreasing": chronological,
        "second_market_day_reached": len(days) >= 2,
        "first_market_day_complete": len(days) >= 2 and chronological,
        "first_market_day_row_count": day_counts[days[0]] if len(days) >= 2 else None,
        "first_transition_compressed_upper_bound": first_transition_compressed_upper_bound,
        "data_row_opened": data_row_count > 0,
    }


def _header_contract(parsed: Mapping[str, object], spec: Mapping[str, object]) -> bool:
    comparisons = {
        "member": "expected_member",
        "header_package": "expected_package",
        "header_table": "expected_table",
        "header_version": "expected_version",
    }
    if any(parsed.get(observed) != spec.get(expected) for observed, expected in comparisons.items()):
        return False
    fields = set(cast(list[str], parsed.get("header_fields", [])))
    return set(cast(list[str], spec["required_fields"])) <= fields


def summarize_reachability(
    parsed_prefixes: Sequence[Mapping[str, object]],
    retention: Mapping[str, object],
    manifest: Mapping[str, object],
    *,
    source_manifest_sha256: str,
    analyzer_git_commit: str,
    generated_at: str,
) -> dict[str, object]:
    """Apply the frozen per-object and overall reachability gates."""

    specs = cast(list[dict[str, object]], manifest["objects"])
    retained = cast(list[dict[str, object]], retention["objects"])
    audits: list[dict[str, object]] = []
    total_rows = 0
    total_parsed = 0
    for parsed, spec, retained_item in zip(parsed_prefixes, specs, retained, strict=True):
        gates = {
            "r2_materialization_verified": retained_item.get("verified") is True,
            "header_contract": _header_contract(parsed, spec),
            "data_rows_nonempty": cast(int, parsed.get("data_row_count", 0)) > 0,
            "first_market_day": parsed.get("first_market_day") == spec["expected_first_market_day"],
            "second_market_day_reached": parsed.get("second_market_day_reached") is True,
            "chronological_prefix": parsed.get("chronological_non_decreasing") is True,
            "first_market_day_complete": parsed.get("first_market_day_complete") is True,
            "timestamp_parse": parsed.get("timestamp_parse_rate") == 1.0,
            "malformed_rows": parsed.get("malformed_row_count") == 0,
            "partial_archive_only": parsed.get("deflate_eof") is False,
        }
        audits.append(
            {
                "object_id": spec["object_id"],
                "sample_label": spec["sample_label"],
                "month": spec["month"],
                "mechanism_phase": spec["mechanism_phase"],
                "observation_phase": spec["observation_phase"],
                "parsed": dict(parsed),
                "gates": gates,
                "pass": all(gates.values()),
            }
        )
        total_rows += cast(int, parsed.get("data_row_count", 0))
        total_parsed += cast(int, parsed.get("timestamp_parse_count", 0))
    all_pass = len(audits) == 2 and all(item["pass"] is True for item in audits)
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": source_manifest_sha256,
        "analyzer_git_commit": analyzer_git_commit,
        "generated_at": generated_at,
        "scientific_role": manifest["scientific_role"],
        "decision": (
            "PASS_HISTORICAL_PREFIX_REACHABILITY" if all_pass else "FAIL_HISTORICAL_PREFIX_REACHABILITY"
        ),
        "pass": all_pass,
        "aggregate": {
            "object_count": len(audits),
            "passing_object_count": sum(1 for item in audits if item["pass"] is True),
            "retained_prefix_bytes": sum(cast(int, item["observed_bytes"]) for item in retained),
            "data_row_count": total_rows,
            "timestamp_parse_count": total_parsed,
            "timestamp_parse_rate": total_parsed / total_rows if total_rows else 0.0,
            "gpu_hours": 0,
            "paid_data_spend": 0,
        },
        "audits": audits,
        "claim_boundary": {
            "historical_row_join_validated": False,
            "historical_action_semantics_validated": False,
            "causal_effect_allowed": False,
            "model_claim_allowed": False,
            "fresh_confirmation_months_consumed": False,
        },
        "gpu_used": False,
        "paid_data_used": False,
        "model_run": False,
        "target_outcome_used": False,
    }


def load_json(path: str | Path) -> dict[str, object]:
    """Load a JSON object from disk."""

    payload: object = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return cast(dict[str, object], payload)


__all__ = [
    "DOWNLOAD_SCHEMA_VERSION",
    "MAX_UNCOMPRESSED_BYTES",
    "RANGE_BYTES",
    "RETENTION_SCHEMA_VERSION",
    "SOURCE_MANIFEST_PATH",
    "load_json",
    "load_manifest",
    "manifest_sha256",
    "parse_offer_prefix",
    "summarize_reachability",
    "utc_now",
    "validate_download_receipt",
    "validate_manifest",
    "validate_retention_receipt",
    "verify_local_prefixes",
]
