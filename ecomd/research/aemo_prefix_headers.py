"""Bounded ZIP-prefix inspection for AEMO MMSDM information headers."""

from __future__ import annotations

import csv
import hashlib
import io
import re
import struct
import zlib
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

import yaml

SCHEMA_VERSION = "ecophys-aemo-prefix-headers/v4"
SUMMARY_SCHEMA_VERSION = "ecophys-aemo-prefix-headers-summary/v4"
RANGE_BYTES = 262_144
MAX_UNCOMPRESSED_PREFIX = 65_536
LOCAL_FILE_SIGNATURE = 0x04034B50
LOCAL_FILE_HEADER = struct.Struct("<IHHHHHIIIHH")
EXPECTED_SAMPLES = {
    "r0-prefix-2020-09": ("2020-09", "A0_30_minute_only", "O0_legacy_reports"),
    "r2-prefix-2022-04": ("2022-04", "A2_5_minute_rule_live", "O3_5_minute_reports"),
}
EXPECTED_ROLES = (
    "BIDDAYOFFER",
    "BIDPEROFFER",
    "DISPATCHOFFERTRK",
    "DISPATCHLOAD",
    "DUDETAILSUMMARY",
)
EXPECTED_HEADERS = {
    ("r0-prefix-2020-09", "BIDDAYOFFER"): ("OFFER", "BIDDAYOFFER", "2"),
    ("r0-prefix-2020-09", "BIDPEROFFER"): ("OFFER", "BIDPEROFFER", "2"),
    ("r0-prefix-2020-09", "DISPATCHOFFERTRK"): ("DISPATCH", "OFFERTRK", "1"),
    ("r0-prefix-2020-09", "DISPATCHLOAD"): ("DISPATCH", "UNIT_SOLUTION", "2"),
    ("r0-prefix-2020-09", "DUDETAILSUMMARY"): (
        "PARTICIPANT_REGISTRATION",
        "DUDETAILSUMMARY",
        "4",
    ),
    ("r2-prefix-2022-04", "BIDDAYOFFER"): ("BIDS", "BIDDAYOFFER", "1"),
    ("r2-prefix-2022-04", "BIDPEROFFER"): ("BIDS", "BIDOFFERPERIOD", "1"),
    ("r2-prefix-2022-04", "DISPATCHOFFERTRK"): ("DISPATCH", "OFFERTRK", "1"),
    ("r2-prefix-2022-04", "DISPATCHLOAD"): ("DISPATCH", "UNIT_SOLUTION", "2"),
    ("r2-prefix-2022-04", "DUDETAILSUMMARY"): (
        "PARTICIPANT_REGISTRATION",
        "DUDETAILSUMMARY",
        "4",
    ),
}
ROOT_KEYS = frozenset(
    {
        "schema_version",
        "sample_id",
        "frozen_at",
        "parent_commit",
        "scientific_role",
        "loader_gate",
        "selection",
        "range_contract",
        "objects",
        "gates",
        "outputs",
    }
)
OBJECT_KEYS = frozenset(
    {
        "object_id",
        "sample_label",
        "month",
        "mechanism_phase",
        "observation_phase",
        "logical_role",
        "url",
        "expected_member",
        "expected_package",
        "expected_table",
        "expected_version",
        "required_fields",
    }
)


def load_prefix_manifest(path: str | Path) -> dict[str, object]:
    """Load a prefix-header manifest at an object-typed boundary."""

    payload: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("AEMO prefix-header manifest root must be a mapping")
    return cast(dict[str, object], payload)


def manifest_sha256(path: str | Path) -> str:
    """Hash exact manifest bytes."""

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


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


def validate_prefix_manifest(manifest: Mapping[str, object]) -> tuple[str, ...]:
    """Validate exact archive prefixes and header expectations."""

    errors: list[str] = []
    if set(manifest) != ROOT_KEYS:
        errors.append("root keys changed")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if manifest.get("scientific_role") != "development_only_bounded_prefix_header_validation":
        errors.append("scientific_role changed")
    if not _utc(manifest.get("frozen_at")):
        errors.append("frozen_at must be UTC")
    if not _sha(manifest.get("parent_commit"), 40):
        errors.append("parent_commit must be a full SHA-1")
    loader_gate = manifest.get("loader_gate")
    if not isinstance(loader_gate, Mapping) or dict(loader_gate) != {
        "decision": "PASS_TWO_CLOCK_LOADER_ENDPOINTS_ONLY",
        "result_commit": "2f650ab0753ce4a6f7bd0611dd9c42327f6e0137",
        "summary_sha256": "577e1815898acdbd750c7bc5e38c1c588195cc6262ac0144baa509dc427cfa13",
    }:
        errors.append("loader gate provenance changed")
    selection = manifest.get("selection")
    if not isinstance(selection, Mapping) or dict(selection) != {
        "rule": "reuse_loader_validated_months_at_new_unopened_zip_prefix_layer",
        "no_replacement": True,
        "zip_or_csv_previously_accessed_before_freeze": False,
    }:
        errors.append("selection changed")
    range_contract = manifest.get("range_contract")
    if not isinstance(range_contract, Mapping) or dict(range_contract) != {
        "request_header": "Range: bytes=0-262143",
        "required_http_status": 206,
        "maximum_response_bytes": RANGE_BYTES,
        "maximum_uncompressed_prefix_bytes": MAX_UNCOMPRESSED_PREFIX,
        "full_download_fallback_allowed": False,
        "data_row_before_information_header_allowed": False,
    }:
        errors.append("range contract changed")

    objects = manifest.get("objects")
    observed_pairs: list[tuple[str, str]] = []
    if not isinstance(objects, list) or len(objects) != 10:
        errors.append("objects must contain exactly ten entries")
    else:
        identifiers: set[str] = set()
        for index, raw_object in enumerate(objects):
            if not isinstance(raw_object, Mapping):
                errors.append(f"objects[{index}] must be a mapping")
                continue
            item = cast(Mapping[str, object], raw_object)
            if set(item) != OBJECT_KEYS:
                errors.append(f"objects[{index}] has unexpected keys")
            object_id = _text(item.get("object_id"))
            if object_id is None or object_id in identifiers:
                errors.append(f"objects[{index}].object_id must be unique")
            else:
                identifiers.add(object_id)
            sample = _text(item.get("sample_label"))
            role = _text(item.get("logical_role"))
            if sample is None or sample not in EXPECTED_SAMPLES:
                errors.append(f"objects[{index}].sample_label is invalid")
                continue
            month, mechanism_phase, observation_phase = EXPECTED_SAMPLES[sample]
            if item.get("month") != month:
                errors.append(f"objects[{index}].month changed")
            if item.get("mechanism_phase") != mechanism_phase:
                errors.append(f"objects[{index}].mechanism_phase changed")
            if item.get("observation_phase") != observation_phase:
                errors.append(f"objects[{index}].observation_phase changed")
            if role is None or role not in EXPECTED_ROLES:
                errors.append(f"objects[{index}].logical_role is invalid")
                continue
            observed_pairs.append((sample, role))
            package, table, version = EXPECTED_HEADERS[(sample, role)]
            if item.get("expected_package") != package:
                errors.append(f"objects[{index}].expected_package changed")
            if item.get("expected_table") != table:
                errors.append(f"objects[{index}].expected_table changed")
            if item.get("expected_version") != version:
                errors.append(f"objects[{index}].expected_version changed")
            url = _text(item.get("url"))
            expected_stem = f"PUBLIC_DVD_{role}_{month.replace('-', '')}010000"
            if url is None:
                errors.append(f"objects[{index}].url is invalid")
            else:
                parsed = urlparse(url)
                if (
                    parsed.scheme != "https"
                    or parsed.hostname != "www.nemweb.com.au"
                    or parsed.query
                    or parsed.fragment
                    or f"/MMSDM_{month.replace('-', '_')}/" not in parsed.path
                    or "/MMSDM_Historical_Data_SQLLoader/DATA/" not in parsed.path
                    or not parsed.path.endswith(expected_stem + ".zip")
                ):
                    errors.append(f"objects[{index}].url is outside the frozen AEMO boundary")
            if item.get("expected_member") != expected_stem + ".CSV":
                errors.append(f"objects[{index}].expected_member changed")
            fields = item.get("required_fields")
            if (
                not isinstance(fields, list)
                or not fields
                or any(_text(field) is None for field in fields)
                or len(set(cast(list[str], fields))) != len(fields)
            ):
                errors.append(f"objects[{index}].required_fields is invalid")
        expected_pairs = {
            (sample_label, role) for sample_label in EXPECTED_SAMPLES for role in EXPECTED_ROLES
        }
        if set(observed_pairs) != expected_pairs or len(observed_pairs) != len(expected_pairs):
            errors.append("objects must cover every sample/role pair exactly once")
    gates = manifest.get("gates")
    if not isinstance(gates, Mapping) or dict(gates) != {
        "required_http_206": 10,
        "required_zip_prefix_parse": 10,
        "required_header_contract_pass": 10,
        "row_access_allowed_after_pass": False,
        "full_archive_download_allowed_after_pass": False,
        "gpu_allowed": False,
        "replacement_allowed": False,
    }:
        errors.append("gates changed")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, Mapping) or set(outputs) != {"summary"}:
        errors.append("outputs must contain only summary")
    elif _text(outputs.get("summary")) is None:
        errors.append("summary output path is invalid")
    return tuple(errors)


def _decompress_prefix(method: int, payload: bytes) -> bytes:
    if method == 0:
        return payload[:MAX_UNCOMPRESSED_PREFIX]
    if method != 8:
        raise ValueError(f"unsupported ZIP compression method {method}")
    decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
    try:
        return decompressor.decompress(payload, MAX_UNCOMPRESSED_PREFIX)
    except zlib.error as error:
        raise ValueError(f"invalid deflate prefix: {error}") from error


def parse_aemo_zip_prefix(content: bytes) -> dict[str, object]:
    """Extract the first MMSDM information header from a bounded ZIP prefix."""

    if len(content) < LOCAL_FILE_HEADER.size:
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
    ) = LOCAL_FILE_HEADER.unpack_from(content)
    if signature != LOCAL_FILE_SIGNATURE:
        raise ValueError("ZIP prefix does not start with a local file header")
    if flags & 0x1:
        raise ValueError("encrypted ZIP member is unsupported")
    data_offset = LOCAL_FILE_HEADER.size + filename_length + extra_length
    if len(content) <= data_offset:
        raise ValueError("ZIP prefix does not contain member payload")
    filename_bytes = content[LOCAL_FILE_HEADER.size : LOCAL_FILE_HEADER.size + filename_length]
    encoding = "utf-8" if flags & 0x800 else "cp437"
    try:
        member = filename_bytes.decode(encoding)
    except UnicodeDecodeError as error:
        raise ValueError(f"invalid ZIP member filename: {error}") from error
    if not member.upper().endswith(".CSV"):
        raise ValueError(f"first ZIP member is not CSV: {member}")
    decompressed = _decompress_prefix(compression_method, content[data_offset:])
    last_newline = max(decompressed.rfind(b"\n"), decompressed.rfind(b"\r"))
    if last_newline < 0:
        raise ValueError("no complete CSV line in bounded ZIP prefix")
    try:
        text = decompressed[: last_newline + 1].decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError(f"invalid MMSDM CSV prefix: {error}") from error
    information_row: list[str] | None = None
    non_data_rows_before_header = 0
    try:
        for row in csv.reader(io.StringIO(text, newline="")):
            if not row:
                continue
            row_type = row[0].strip().upper()
            if row_type == "D":
                raise ValueError("data row encountered before MMSDM information header")
            if row_type == "I":
                information_row = row
                break
            non_data_rows_before_header += 1
    except csv.Error as error:
        raise ValueError(f"invalid MMSDM CSV prefix: {error}") from error
    if information_row is None or len(information_row) < 5:
        raise ValueError("no complete MMSDM information header in bounded ZIP prefix")
    return {
        "zip_version_needed": version_needed,
        "zip_flags": flags,
        "compression_method": compression_method,
        "member": member,
        "data_offset": data_offset,
        "compressed_prefix_bytes": len(content) - data_offset,
        "uncompressed_prefix_bytes": len(decompressed),
        "non_data_rows_before_header": non_data_rows_before_header,
        "header_package": information_row[1].strip(),
        "header_table": information_row[2].strip(),
        "header_version": information_row[3].strip(),
        "header_fields": [field.strip() for field in information_row[4:]],
        "data_row_opened": False,
    }


def audit_prefix_response(
    spec: Mapping[str, object],
    *,
    http_status: int | None,
    content: bytes,
    response_headers: Mapping[str, str],
    retrieved_at: str,
    transport_error: str | None,
) -> dict[str, object]:
    """Audit one bounded range response against its frozen header contract."""

    errors: list[str] = []
    parsed: dict[str, object] | None = None
    if http_status != 206:
        errors.append(f"HTTP status {http_status!r} != 206")
    if transport_error is not None:
        errors.append(transport_error)
    if len(content) > RANGE_BYTES:
        errors.append(f"response bytes {len(content)} exceed {RANGE_BYTES}")
    content_range = next(
        (value for key, value in response_headers.items() if key.lower() == "content-range"),
        None,
    )
    if http_status == 206 and (
        content_range is None or re.fullmatch(r"bytes 0-\d+/\d+", content_range) is None
    ):
        errors.append("missing or invalid Content-Range")
    if http_status == 206 and not errors:
        try:
            parsed = parse_aemo_zip_prefix(content)
        except ValueError as error:
            errors.append(f"ValueError: {error}")
    if parsed is not None:
        comparisons = {
            "member": "expected_member",
            "header_package": "expected_package",
            "header_table": "expected_table",
            "header_version": "expected_version",
        }
        for observed_key, expected_key in comparisons.items():
            if parsed[observed_key] != spec.get(expected_key):
                errors.append(
                    f"{observed_key} {parsed[observed_key]} != {spec.get(expected_key)}"
                )
        fields = set(cast(list[str], parsed["header_fields"]))
        required = set(cast(list[str], spec["required_fields"]))
        missing = sorted(required - fields)
        if missing:
            errors.append(f"missing required fields: {missing}")
    return {
        "object_id": spec.get("object_id"),
        "sample_label": spec.get("sample_label"),
        "month": spec.get("month"),
        "mechanism_phase": spec.get("mechanism_phase"),
        "observation_phase": spec.get("observation_phase"),
        "logical_role": spec.get("logical_role"),
        "url": spec.get("url"),
        "retrieved_at": retrieved_at,
        "http_status": http_status,
        "response_headers": dict(response_headers),
        "transport_error": transport_error,
        "response_bytes": len(content),
        "prefix_sha256": hashlib.sha256(content).hexdigest() if content else None,
        "parsed": parsed,
        "zip_prefix_parse": parsed is not None,
        "header_contract_pass": not errors,
        "errors": errors,
        "data_row_opened": False,
        "full_archive_downloaded": False,
        "gpu_used": False,
    }


def summarize_prefix_audit(
    audits: Sequence[Mapping[str, object]],
    *,
    source_manifest: str,
    source_manifest_sha256: str,
    collector_git_commit: str,
    generated_at: str,
) -> dict[str, object]:
    """Summarize the exact ten-prefix header audit."""

    expected = 10
    http_count = sum(item.get("http_status") == 206 for item in audits)
    parse_count = sum(item.get("zip_prefix_parse") is True for item in audits)
    contract_count = sum(item.get("header_contract_pass") is True for item in audits)
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "source_manifest": source_manifest,
        "source_manifest_sha256": source_manifest_sha256,
        "collector_git_commit": collector_git_commit,
        "generated_at": generated_at,
        "expected_count": expected,
        "observed_count": len(audits),
        "http_206_count": http_count,
        "zip_prefix_parse_count": parse_count,
        "header_contract_pass_count": contract_count,
        "total_response_bytes": sum(
            cast(int, item.get("response_bytes", 0)) for item in audits
        ),
        "pass": (
            len(audits) == expected
            and http_count == expected
            and parse_count == expected
            and contract_count == expected
        ),
        "audits": list(audits),
        "data_row_opened": False,
        "full_archive_downloaded": False,
        "gpu_used": False,
        "paid_data_used": False,
    }
