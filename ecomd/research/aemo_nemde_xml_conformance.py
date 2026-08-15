"""Bounded XML conformance audit for two production AEMO NEMDE cases."""

from __future__ import annotations

import binascii
import hashlib
import json
import re
import struct
import xml.etree.ElementTree as ET
import zlib
from collections import Counter
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import cast
from urllib.parse import urlparse

import yaml

from ecomd.research.aemo_row_conformance import file_sha256

SCHEMA_VERSION = "ecophys-aemo-nemde-xml-conformance/v1"
DOWNLOAD_SCHEMA_VERSION = "ecophys-aemo-nemde-xml-conformance-download/v1"
RETENTION_SCHEMA_VERSION = "ecophys-aemo-nemde-xml-conformance-retention/v1"
SUMMARY_SCHEMA_VERSION = "ecophys-aemo-nemde-xml-conformance-summary/v1"
SOURCE_MANIFEST_PATH = "data/manifests/aemo_nemde_xml_conformance_v1.yaml"
EXPECTED_PARENT_COMMIT = "a20d778626523eb6546fce9629680ab1fed7fc53"
RANGE_BYTES = 1024 * 1024
LOCAL_HEADER = struct.Struct("<4s5H3I2H")
LOCAL_SIGNATURE = b"PK\x03\x04"
EXPECTED_OBJECTS: tuple[dict[str, object], ...] = (
    {
        "object_id": "pre-5ms-nemde-xml-2021-01-01-144",
        "market_date": "2021-01-01",
        "mechanism_phase": "A0_30_MINUTE_ONLY",
        "url": "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/NEMDE/2021/NEMDE_2021_01/NEMDE_Market_Data/NEMDE_Files/NemSpdOutputs_20210101_loaded.zip",
        "expected_archive_bytes": 116_002_085,
        "range_start": 57_637_442,
        "range_end": 58_686_017,
        "expected_filename": "NEMSPDOutputs_2021010114400.loaded.range-57637442-58686017.bin",
        "member_name": "NEMSPDOutputs_2021010114400.loaded",
        "member_flags": 0,
        "compression_method": 8,
        "crc32": "11f971a8",
        "compressed_bytes": 404_030,
        "uncompressed_bytes": 7_851_704,
        "r2_key": "raw/aemo/v14_nemde_xml_conformance/NEMSPDOutputs_2021010114400.loaded.range-57637442-58686017.bin",
    },
    {
        "object_id": "post-5ms-nemde-xml-2021-12-01-144",
        "market_date": "2021-12-01",
        "mechanism_phase": "A3_5MS_PLUS_WDR",
        "url": "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/NEMDE/2021/NEMDE_2021_12/NEMDE_Market_Data/NEMDE_Files/NemSpdOutputs_20211201_loaded.zip",
        "expected_archive_bytes": 132_455_595,
        "range_start": 65_590_506,
        "range_end": 66_639_081,
        "expected_filename": "NEMSPDOutputs_2021120114400.loaded.range-65590506-66639081.bin",
        "member_name": "NEMSPDOutputs_2021120114400.loaded",
        "member_flags": 0,
        "compression_method": 8,
        "crc32": "ebbea93d",
        "compressed_bytes": 459_136,
        "uncompressed_bytes": 8_895_016,
        "r2_key": "raw/aemo/v14_nemde_xml_conformance/NEMSPDOutputs_2021120114400.loaded.range-65590506-66639081.bin",
    },
)
REQUIRED_SECTIONS = ("NemSpdInputs", "NemSpdOutputs", "SolutionAnalysis")
REQUIRED_INPUT_GROUPS = (
    "Case",
    "RegionCollection",
    "TraderCollection",
    "PeriodCollection",
    "InterconnectorCollection",
    "GenericConstraintCollection",
)
REQUIRED_OUTPUT_GROUPS = (
    "CaseSolution",
    "PeriodSolution",
    "RegionSolution",
    "InterconnectorSolution",
    "TraderSolution",
    "ConstraintSolution",
)
ACTION_ATTRIBUTES = ("PriceBand1", "BandAvail1", "MaxAvail", "RampUpRate", "RampDnRate")


def load_manifest(path: str | Path) -> dict[str, object]:
    """Load the frozen XML conformance manifest."""

    payload: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("NEMDE XML manifest root must be a mapping")
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
    """Validate the exact two-member XML audit boundary."""

    errors: list[str] = []
    expected_root = {
        "schema_version",
        "sample_id",
        "frozen_at",
        "parent_commit",
        "scientific_role",
        "prior_inventory",
        "selection",
        "range_contract",
        "objects",
        "retention_contract",
        "xml_contract",
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
    if manifest.get("scientific_role") != "development_only_nemde_xml_section_conformance":
        errors.append("manifest scientific role changed")
    prior = manifest.get("prior_inventory")
    if not isinstance(prior, Mapping) or dict(prior) != {
        "protocol_commit": "0787be5f04f7d66e80c497f85051ce2b742bcc11",
        "result_commit": EXPECTED_PARENT_COMMIT,
        "decision": "PASS_NEMDE_TAIL_INVENTORY",
        "summary_sha256": "9fca06c5e627960499f0e045dbbf77de174ac8a99b3f5fe46d975dfdbb1e1bb8",
    }:
        errors.append("prior inventory changed")
    selection = manifest.get("selection")
    if not isinstance(selection, Mapping) or dict(selection) != {
        "rule": "exact_unique_interval_144_members_from_frozen_tail_inventory",
        "dates": ["2021-01-01", "2021-12-01"],
        "interval_id": 144,
        "held_out_status": "development_consumed_not_eligible_for_confirmation",
        "replacement_allowed": False,
    }:
        errors.append("selection contract changed")
    ranges = manifest.get("range_contract")
    if not isinstance(ranges, Mapping) or dict(ranges) != {
        "exact_response_bytes_per_object": RANGE_BYTES,
        "maximum_total_response_bytes": 2 * RANGE_BYTES,
        "request_starts_at_frozen_local_header_offset": True,
        "full_download_fallback_allowed": False,
        "retry_allowed": False,
        "range_extension_allowed": False,
        "parse_before_r2_retention_allowed": False,
        "following_member_parse_allowed": False,
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
            if cast(int, item["range_end"]) - cast(int, item["range_start"]) + 1 != RANGE_BYTES:
                errors.append(f"objects[{index}] range length changed")
    retention = manifest.get("retention_contract")
    if not isinstance(retention, Mapping) or dict(retention) != {
        "bucket": "ecophys",
        "prefix": "raw/aemo/v14_nemde_xml_conformance/",
        "upload_before_local_header_or_xml_parse": True,
        "remote_sha256_metadata_required": True,
        "overwrite_mismatched_remote_object_allowed": False,
        "raw_ranges_or_xml_committed_to_git": False,
    }:
        errors.append("retention contract changed")
    xml_contract = manifest.get("xml_contract")
    if not isinstance(xml_contract, Mapping) or dict(xml_contract) != {
        "prohibited_tokens": ["<!DOCTYPE", "<!ENTITY"],
        "required_sections": list(REQUIRED_SECTIONS),
        "required_occurrences_per_section": 1,
        "required_input_groups": list(REQUIRED_INPUT_GROUPS),
        "required_output_groups": list(REQUIRED_OUTPUT_GROUPS),
        "price_section_min_descendants": 1,
        "action_attribute_vocabulary": list(ACTION_ATTRIBUTES),
        "action_attribute_presence_is_gate": False,
    }:
        errors.append("XML contract changed")
    gates = manifest.get("gates")
    if not isinstance(gates, Mapping) or dict(gates) != {
        "required_object_count": 2,
        "required_r2_verified_count": 2,
        "required_local_header_count": 2,
        "required_deflate_eof_count": 2,
        "required_crc_count": 2,
        "required_xml_parse_count": 2,
        "required_section_contract_count": 2,
        "required_input_group_contract_count": 2,
        "required_output_group_contract_count": 2,
        "required_nonempty_price_section_count": 2,
        "licence_clarification_required_before_raw_redistribution": True,
        "raw_submission_claim_allowed": False,
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
    value = next((raw for key, raw in headers.items() if key.lower() == "content-range"), None)
    match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", value) if value else None
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def validate_download_receipt(
    receipt: Mapping[str, object], manifest: Mapping[str, object]
) -> tuple[str, ...]:
    """Validate exact opaque member-range downloads."""

    errors: list[str] = []
    if receipt.get("schema_version") != DOWNLOAD_SCHEMA_VERSION:
        errors.append("download schema changed")
    if not _utc(receipt.get("generated_at")) or not _sha(receipt.get("protocol_git_commit"), 40):
        errors.append("download provenance is invalid")
    if receipt.get("source_manifest") != SOURCE_MANIFEST_PATH or not _sha(
        receipt.get("source_manifest_sha256"), 64
    ):
        errors.append("download manifest provenance changed")
    if receipt.get("request_policy") != "one_exact_member_range_per_object_no_retry_no_extension":
        errors.append("download request policy changed")
    if receipt.get("local_header_opened") is not False or receipt.get("xml_opened") is not False:
        errors.append("download accessed content")
    raw_objects = receipt.get("objects")
    specs = cast(list[dict[str, object]], manifest["objects"])
    if not isinstance(raw_objects, list) or len(raw_objects) != len(specs):
        errors.append("download object count changed")
        return tuple(errors)
    for index, (raw, spec) in enumerate(zip(raw_objects, specs, strict=True)):
        if not isinstance(raw, Mapping):
            errors.append(f"download object {index} is invalid")
            continue
        expected_range = (
            cast(int, spec["range_start"]),
            cast(int, spec["range_end"]),
            cast(int, spec["expected_archive_bytes"]),
        )
        headers = raw.get("response_headers")
        if raw.get("request_index") != index or raw.get("request_count") != 1:
            errors.append(f"download object {index} request count changed")
        if raw.get("object_id") != spec["object_id"] or raw.get("url") != spec["url"]:
            errors.append(f"download object {index} identity changed")
        if raw.get("http_status") != 206 or not isinstance(headers, Mapping) or _content_range(
            cast(Mapping[str, str], headers)
        ) != expected_range:
            errors.append(f"download object {index} response range changed")
        if raw.get("observed_bytes") != RANGE_BYTES or not _sha(raw.get("sha256"), 64):
            errors.append(f"download object {index} bytes or SHA changed")
        if raw.get("local_filename") != spec["expected_filename"]:
            errors.append(f"download object {index} filename changed")
        if raw.get("transport_error") is not None or raw.get("download_pass") is not True:
            errors.append(f"download object {index} did not pass")
        if raw.get("local_header_opened") is not False or raw.get("xml_opened") is not False:
            errors.append(f"download object {index} accessed content")
    if receipt.get("pass") is not True:
        errors.append("download did not pass")
    return tuple(errors)


def validate_retention_receipt(
    receipt: Mapping[str, object], download: Mapping[str, object], manifest: Mapping[str, object]
) -> tuple[str, ...]:
    """Validate exact R2 retention before member parsing."""

    errors: list[str] = []
    if receipt.get("schema_version") != RETENTION_SCHEMA_VERSION or not _utc(receipt.get("generated_at")):
        errors.append("retention schema or timestamp changed")
    if receipt.get("protocol_git_commit") != download.get("protocol_git_commit"):
        errors.append("retention protocol commit changed")
    if (
        receipt.get("source_manifest") != SOURCE_MANIFEST_PATH
        or receipt.get("source_manifest_sha256") != download.get("source_manifest_sha256")
    ):
        errors.append("retention manifest provenance changed")
    if receipt.get("bucket") != "ecophys" or receipt.get("prefix") != "raw/aemo/v14_nemde_xml_conformance/":
        errors.append("retention location changed")
    if receipt.get("local_header_opened") is not False or receipt.get("xml_opened") is not False:
        errors.append("retention accessed content")
    retained = receipt.get("objects")
    downloaded = download.get("objects")
    specs = cast(list[dict[str, object]], manifest["objects"])
    if not isinstance(retained, list) or not isinstance(downloaded, list):
        errors.append("retention objects are invalid")
        return tuple(errors)
    if len(retained) != len(specs) or len(downloaded) != len(specs):
        errors.append("retention object count changed")
        return tuple(errors)
    for index, (item, source, spec) in enumerate(zip(retained, downloaded, specs, strict=True)):
        if not isinstance(item, Mapping) or not isinstance(source, Mapping):
            errors.append(f"retention object {index} is invalid")
            continue
        sha = source.get("sha256")
        if item.get("object_id") != spec["object_id"] or item.get("r2_key") != spec["r2_key"]:
            errors.append(f"retention object {index} identity changed")
        if (
            item.get("observed_bytes") != RANGE_BYTES
            or item.get("remote_content_length") != RANGE_BYTES
            or item.get("sha256") != sha
            or item.get("remote_metadata_sha256") != sha
            or item.get("verified") is not True
        ):
            errors.append(f"retention object {index} was not hash-verified")
    if receipt.get("all_verified") is not True:
        errors.append("retention did not verify every object")
    return tuple(errors)


def verify_local_ranges(
    raw_root: str | Path, download: Mapping[str, object], manifest: Mapping[str, object]
) -> tuple[str, ...]:
    """Verify local member ranges against the download receipt."""

    errors: list[str] = []
    downloaded = cast(list[dict[str, object]], download["objects"])
    specs = cast(list[dict[str, object]], manifest["objects"])
    for index, (item, spec) in enumerate(zip(downloaded, specs, strict=True)):
        path = Path(raw_root) / cast(str, spec["expected_filename"])
        if not path.is_file():
            errors.append(f"local range {index} is absent")
        elif path.stat().st_size != RANGE_BYTES or file_sha256(path) != item["sha256"]:
            errors.append(f"local range {index} differs from receipt")
    return tuple(errors)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", maxsplit=1)[-1]


def _error_result(spec: Mapping[str, object], error: str) -> dict[str, object]:
    return {
        "object_id": spec["object_id"],
        "parse_error": error,
        "local_header_pass": False,
        "deflate_eof": False,
        "crc_pass": False,
        "xml_parse_pass": False,
        "section_contract_pass": False,
        "input_group_contract_pass": False,
        "output_group_contract_pass": False,
        "nonempty_price_section_pass": False,
    }


def parse_member_range(path: str | Path, spec: Mapping[str, object]) -> dict[str, object]:
    """Validate one local ZIP member and inventory its XML schema without values."""

    data = Path(path).read_bytes()
    if len(data) != RANGE_BYTES or len(data) < LOCAL_HEADER.size:
        return _error_result(spec, "range byte count differs from contract")
    (
        signature,
        _version_needed,
        flags,
        method,
        _modified_time,
        _modified_date,
        crc32,
        compressed_bytes,
        uncompressed_bytes,
        filename_bytes,
        extra_bytes,
    ) = LOCAL_HEADER.unpack_from(data)
    if signature != LOCAL_SIGNATURE:
        return _error_result(spec, "local ZIP header signature changed")
    name_end = LOCAL_HEADER.size + filename_bytes
    payload_start = name_end + extra_bytes
    payload_end = payload_start + compressed_bytes
    if payload_end > len(data):
        return _error_result(spec, "member payload exceeds frozen range")
    encoding = "utf-8" if flags & 0x800 else "cp437"
    try:
        member_name = data[LOCAL_HEADER.size:name_end].decode(encoding)
    except UnicodeDecodeError:
        return _error_result(spec, "local member name cannot be decoded")
    expected_crc = int(cast(str, spec["crc32"]), 16)
    local_header_pass = (
        member_name == spec["member_name"]
        and flags == spec["member_flags"]
        and method == spec["compression_method"]
        and crc32 == expected_crc
        and compressed_bytes == spec["compressed_bytes"]
        and uncompressed_bytes == spec["uncompressed_bytes"]
    )
    compressed = data[payload_start:payload_end]
    inflater = zlib.decompressobj(-zlib.MAX_WBITS)
    try:
        xml_bytes = inflater.decompress(compressed) + inflater.flush()
        deflate_error: str | None = None
    except zlib.error as error:
        xml_bytes = b""
        deflate_error = f"{type(error).__name__}: {error}"
    deflate_eof = (
        deflate_error is None
        and inflater.eof
        and not inflater.unconsumed_tail
        and not inflater.unused_data
        and len(xml_bytes) == uncompressed_bytes
    )
    observed_crc = binascii.crc32(xml_bytes) & 0xFFFFFFFF
    crc_pass = deflate_eof and observed_crc == expected_crc
    prohibited = [token for token in (b"<!DOCTYPE", b"<!ENTITY") if token in xml_bytes.upper()]
    root: ET.Element[str] | None = None
    xml_error: str | None = deflate_error
    if deflate_eof and crc_pass and not prohibited:
        try:
            root = ET.fromstring(xml_bytes)
        except ET.ParseError as error:
            xml_error = f"{type(error).__name__}: {error}"
    elif prohibited:
        xml_error = "prohibited DTD/entity token present"
    xml_parse_pass = root is not None
    if root is None:
        result = _error_result(spec, xml_error or "XML parse precondition failed")
        result.update(
            {
                "member_name": member_name,
                "local_header_pass": local_header_pass,
                "deflate_eof": deflate_eof,
                "crc32_observed": f"{observed_crc:08x}",
                "crc_pass": crc_pass,
                "xml_sha256": hashlib.sha256(xml_bytes).hexdigest() if xml_bytes else None,
            }
        )
        return result

    all_elements = list(root.iter())
    tag_counts = Counter(_local_name(element.tag) for element in all_elements)
    section_elements: dict[str, ET.Element[str] | None] = {
        section: next(
            (element for element in all_elements if _local_name(element.tag) == section), None
        )
        for section in REQUIRED_SECTIONS
    }
    section_counts = {section: tag_counts[section] for section in REQUIRED_SECTIONS}

    def section_inventory(section: str) -> tuple[dict[str, int], list[str], int]:
        element = section_elements[section]
        if element is None:
            return {}, [], 0
        descendants = list(element.iter())
        tags = Counter(_local_name(item.tag) for item in descendants)
        attributes = sorted({attribute for item in descendants for attribute in item.attrib})
        return dict(sorted(tags.items())), attributes, max(0, len(descendants) - 1)

    input_tags, input_attributes, input_descendants = section_inventory("NemSpdInputs")
    output_tags, output_attributes, output_descendants = section_inventory("NemSpdOutputs")
    price_tags, price_attributes, price_descendants = section_inventory("SolutionAnalysis")
    section_contract_pass = all(count == 1 for count in section_counts.values())
    input_group_contract_pass = all(input_tags.get(group, 0) > 0 for group in REQUIRED_INPUT_GROUPS)
    output_group_contract_pass = all(output_tags.get(group, 0) > 0 for group in REQUIRED_OUTPUT_GROUPS)
    nonempty_price_section_pass = price_descendants >= 1
    return {
        "object_id": spec["object_id"],
        "parse_error": None,
        "member_name": member_name,
        "local_header_pass": local_header_pass,
        "local_filename_bytes": filename_bytes,
        "local_extra_bytes": extra_bytes,
        "compressed_payload_offset_within_range": payload_start,
        "compressed_payload_end_within_range": payload_end,
        "following_bytes_ignored": len(data) - payload_end,
        "deflate_eof": deflate_eof,
        "uncompressed_bytes": len(xml_bytes),
        "crc32_observed": f"{observed_crc:08x}",
        "crc_pass": crc_pass,
        "xml_sha256": hashlib.sha256(xml_bytes).hexdigest(),
        "xml_parse_pass": xml_parse_pass,
        "root_tag": _local_name(root.tag),
        "total_element_count": len(all_elements),
        "total_unique_tag_count": len(tag_counts),
        "section_counts": section_counts,
        "section_contract_pass": section_contract_pass,
        "input_descendant_count": input_descendants,
        "input_tag_counts": input_tags,
        "input_attribute_names": input_attributes,
        "input_group_contract_pass": input_group_contract_pass,
        "action_attribute_vocabulary_present": sorted(set(input_attributes) & set(ACTION_ATTRIBUTES)),
        "output_descendant_count": output_descendants,
        "output_tag_counts": output_tags,
        "output_attribute_names": output_attributes,
        "output_group_contract_pass": output_group_contract_pass,
        "price_descendant_count": price_descendants,
        "price_tag_counts": price_tags,
        "price_attribute_names": price_attributes,
        "nonempty_price_section_pass": nonempty_price_section_pass,
    }


def summarize_conformance(
    parsed: list[dict[str, object]],
    retention: Mapping[str, object],
    manifest: Mapping[str, object],
    *,
    source_manifest_sha256: str,
    analyzer_git_commit: str,
    generated_at: str,
) -> dict[str, object]:
    """Apply frozen gates and report cross-regime schema overlap."""

    retained = retention.get("objects")
    r2_verified = (
        sum(item.get("verified") is True for item in retained)
        if isinstance(retained, list) and all(isinstance(item, Mapping) for item in retained)
        else 0
    )
    gate_names = (
        "local_header_pass",
        "deflate_eof",
        "crc_pass",
        "xml_parse_pass",
        "section_contract_pass",
        "input_group_contract_pass",
        "output_group_contract_pass",
        "nonempty_price_section_pass",
    )
    counts = {name: sum(item.get(name) is True for item in parsed) for name in gate_names}
    passed = len(parsed) == 2 and r2_verified == 2 and all(count == 2 for count in counts.values())

    def common_values(key: str) -> list[str]:
        if len(parsed) != 2:
            return []
        left = parsed[0].get(key)
        right = parsed[1].get(key)
        if not isinstance(left, list) or not isinstance(right, list):
            return []
        return sorted(set(cast(list[str], left)) & set(cast(list[str], right)))

    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "generated_at": generated_at,
        "analyzer_git_commit": analyzer_git_commit,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": source_manifest_sha256,
        "decision": "PASS_NEMDE_XML_CONFORMANCE" if passed else "FAIL_NEMDE_XML_CONFORMANCE",
        "pass": passed,
        "counts": {"object_count": len(parsed), "r2_verified_count": r2_verified, **counts},
        "cross_regime": {
            "common_input_attribute_names": common_values("input_attribute_names"),
            "common_output_attribute_names": common_values("output_attribute_names"),
            "common_price_attribute_names": common_values("price_attribute_names"),
        },
        "objects": parsed,
        "claim_boundary": {
            "production_case_sections_validated": passed,
            "one_day_alignment_design_unlocked": passed,
            "raw_submission_history_validated": False,
            "exact_solver_replay_validated": False,
            "participant_adaptation_validated": False,
            "causal_or_model_claim_allowed": False,
            "raw_redistribution_allowed": False,
            "licence_clarification_still_required": True,
        },
        "resources": {
            "downloaded_bytes": 2 * RANGE_BYTES,
            "gpu_hours": 0,
            "paid_data_spend": 0,
            "target_outcomes_used": False,
        },
    }
