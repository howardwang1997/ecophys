"""Repaired small-range AEMO source-contract validation."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime
from typing import cast
from urllib.parse import urlparse

from ecomd.research.aemo_source_contract import (
    ARCHIVE_FAMILY,
    DELIVERY_CHANNEL,
    EXPECTED_FORBIDDEN_FIELDS,
    EXPECTED_HEADERS,
    EXPECTED_PROVENANCE_LIMITS,
    EXPECTED_REQUIRED_FIELDS,
    EXPECTED_ROLES,
    EXPECTED_SENSITIVITY_CLASS,
    EXPECTED_TIMELINE,
    OBJECT_KEYS,
    audit_source_contract_response,
    load_source_contract_manifest,
    manifest_sha256,
    utc_now,
)

SCHEMA_VERSION = "ecophys-aemo-source-contract-repair/v2"
SUMMARY_SCHEMA_VERSION = "ecophys-aemo-source-contract-repair-summary/v2"
PARENT_COMMIT = "1bf6b734eb4c607095a64f43107930fe85fb22c8"
RANGE_BYTES = 65_536
MAX_UNCOMPRESSED_PREFIX = 65_536
PREFIX_PROOF_SHA256 = "0be682973ed75bc65c630c8ac650cb839cffc60baa3fa4d256d5a4816ca3c8d5"
CONSUMED_MONTHS = (
    "2020-09",
    "2021-02",
    "2021-03",
    "2021-09",
    "2021-11",
    "2022-04",
    "2025-01",
    "2025-07",
)
EXPECTED_SAMPLES = {
    "pre-bridge-repair-prefix-2021-01": (
        "2021-01",
        "A0_30_MINUTE_ONLY",
        "O0_LEGACY_REPORTS",
        "PRE_REPORTING_BRIDGE",
        "pre-bridge-prefix-2021-02",
    ),
    "post-v51-repair-prefix-2021-12": (
        "2021-12",
        "A3_5MS_PLUS_WDR",
        "O4_V51_CLUSTERED_RELEASE",
        "POST_V51_WDR",
        "post-v51-prefix-2021-11",
    ),
}
EXPECTED_PRIOR_GATE = {
    "frozen_protocol_commit": "39c45dddf736e418a3e112a5a4689a782e918466",
    "result_commit": PARENT_COMMIT,
    "manifest_sha256": "42cc9a940b68847aba1719c1f9568b3c1f9ee07785061080ba286be9e9e60296",
    "raw_summary_sha256": "e7abbcf530d8d75a0f69c5885dfcbdc74a84f743ff9a7134754e6e8b28d8a239",
    "adjudication_sha256": "4111fd31ed2f55a29aa34bf2c6538b2970d0a064565a4b56471ed40201ecb743",
    "scientific_subgate": "PASS_SOURCE_CONTRACT_10_OF_10",
    "authoritative_decision": "FAIL_FULL_ARCHIVE_TRANSFER_GUARD",
    "complete_archive_transfer_count": 2,
}
EXPECTED_OFFLINE_PROOF = {
    "path": "experiments/v14_aemo_source_contract_repair/artifacts/prefix_budget_proof.json",
    "sha256": PREFIX_PROOF_SHA256,
    "decision": "PASS_64_KIB_PREFIX_BUDGET",
    "prior_object_count": 20,
    "range_bytes": RANGE_BYTES,
    "network_used": False,
}
EXPECTED_SELECTION = {
    "rule": "nearest_complete_calendar_month_outside_boundary_not_previously_consumed",
    "anchors": [
        {
            "sample_label": "pre-bridge-repair-prefix-2021-01",
            "boundary": "2021-03-08",
            "side": "before",
            "selected_month": "2021-01",
        },
        {
            "sample_label": "post-v51-repair-prefix-2021-12",
            "boundary": "2021-10-24",
            "side": "after",
            "selected_month": "2021-12",
        },
    ],
    "consumed_months": list(CONSUMED_MONTHS),
    "no_replacement": True,
    "selected_zip_prefix_or_csv_previously_accessed_before_freeze": False,
    "mixed_boundary_month_allowed": False,
}
EXPECTED_RANGE_CONTRACT = {
    "request_header": "Range: bytes=0-65535",
    "required_http_status": 206,
    "exact_response_bytes": RANGE_BYTES,
    "required_final_byte": RANGE_BYTES - 1,
    "required_total_strictly_greater_than_response_bytes": True,
    "maximum_uncompressed_prefix_bytes": MAX_UNCOMPRESSED_PREFIX,
    "smallest_known_complete_archive_bytes": 148_577,
    "known_archive_safety_margin_bytes": 83_041,
    "full_download_fallback_allowed": False,
    "data_row_before_information_header_allowed": False,
}
ROOT_KEYS = frozenset(
    {
        "schema_version",
        "sample_id",
        "frozen_at",
        "parent_commit",
        "scientific_role",
        "prior_gate",
        "offline_prefix_proof",
        "selection",
        "timeline",
        "provenance_limits",
        "range_contract",
        "objects",
        "gates",
        "outputs",
    }
)


def _text(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _utc(value: object) -> bool:
    text = _text(value)
    if text is None or not text.endswith("Z"):
        return False
    try:
        parsed = datetime.fromisoformat(text.removesuffix("Z") + "+00:00")
    except ValueError:
        return False
    return parsed.tzinfo == UTC


def _shift_month(month: date, direction: int) -> date:
    index = month.year * 12 + month.month - 1 + direction
    return date(index // 12, index % 12 + 1, 1)


def nearest_unconsumed_complete_month(
    boundary: str,
    side: str,
    consumed_months: Sequence[str],
) -> str:
    """Select the nearest complete outside month absent from preserved evidence."""

    parsed = date.fromisoformat(boundary).replace(day=1)
    if side == "before":
        direction = -1
    elif side == "after":
        direction = 1
    else:
        raise ValueError("side must be before or after")
    consumed = set(consumed_months)
    candidate = _shift_month(parsed, direction)
    while candidate.strftime("%Y-%m") in consumed or candidate.strftime("%Y-%m") == "2021-10":
        candidate = _shift_month(candidate, direction)
    return candidate.strftime("%Y-%m")


def validate_source_contract_repair_manifest(
    manifest: Mapping[str, object],
) -> tuple[str, ...]:
    """Validate the immutable v2 samples, range repair and source projections."""

    errors: list[str] = []
    if set(manifest) != ROOT_KEYS:
        errors.append("root keys changed")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if manifest.get("sample_id") != "aemo-channel-source-contract-transfer-repair-v2":
        errors.append("sample_id changed")
    if manifest.get("scientific_role") != "development_only_transfer_repair_confirmation":
        errors.append("scientific_role changed")
    if not _utc(manifest.get("frozen_at")):
        errors.append("frozen_at must be UTC")
    if manifest.get("parent_commit") != PARENT_COMMIT:
        errors.append("parent_commit changed")
    prior = manifest.get("prior_gate")
    if not isinstance(prior, Mapping) or dict(prior) != EXPECTED_PRIOR_GATE:
        errors.append("prior gate provenance changed")
    proof = manifest.get("offline_prefix_proof")
    if not isinstance(proof, Mapping) or dict(proof) != EXPECTED_OFFLINE_PROOF:
        errors.append("offline prefix proof changed")
    selection = manifest.get("selection")
    if not isinstance(selection, Mapping) or dict(selection) != EXPECTED_SELECTION:
        errors.append("selection changed")
    else:
        anchors = cast(list[dict[str, object]], selection["anchors"])
        for index, anchor in enumerate(anchors):
            selected = nearest_unconsumed_complete_month(
                cast(str, anchor["boundary"]),
                cast(str, anchor["side"]),
                cast(list[str], selection["consumed_months"]),
            )
            if selected != anchor["selected_month"]:
                errors.append(f"selection anchor {index} is not mechanically derived")
    if manifest.get("timeline") != EXPECTED_TIMELINE:
        errors.append("timeline changed")
    if manifest.get("provenance_limits") != EXPECTED_PROVENANCE_LIMITS:
        errors.append("provenance limits changed")
    range_contract = manifest.get("range_contract")
    if not isinstance(range_contract, Mapping) or dict(range_contract) != EXPECTED_RANGE_CONTRACT:
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
            if role is None or role not in EXPECTED_ROLES:
                errors.append(f"objects[{index}].logical_role is invalid")
                continue
            observed_pairs.append((sample, role))
            month, mechanism, observation, version_basis, template = EXPECTED_SAMPLES[sample]
            expected_values = {
                "month": month,
                "mechanism_phase": mechanism,
                "observation_phase": observation,
                "version_basis": version_basis,
                "delivery_channel": DELIVERY_CHANNEL,
                "archive_family": ARCHIVE_FAMILY,
                "archive_file_id": f"PUBLIC_DVD_{role}",
                "sensitivity_class": EXPECTED_SENSITIVITY_CLASS[role],
            }
            for key, expected in expected_values.items():
                if item.get(key) != expected:
                    errors.append(f"objects[{index}].{key} changed")
            package, table, version = EXPECTED_HEADERS[(template, role)]
            if item.get("expected_package") != package:
                errors.append(f"objects[{index}].expected_package changed")
            if item.get("expected_table") != table:
                errors.append(f"objects[{index}].expected_table changed")
            if item.get("expected_version") != version:
                errors.append(f"objects[{index}].expected_version changed")
            if item.get("required_fields") != list(EXPECTED_REQUIRED_FIELDS[(template, role)]):
                errors.append(f"objects[{index}].required_fields changed")
            expected_forbidden = list(EXPECTED_FORBIDDEN_FIELDS.get((template, role), ()))
            if item.get("forbidden_fields") != expected_forbidden:
                errors.append(f"objects[{index}].forbidden_fields changed")
            compact_month = month.replace("-", "")
            expected_stem = f"PUBLIC_DVD_{role}_{compact_month}010000"
            url = _text(item.get("url"))
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
        expected_pairs = {
            (sample, role) for sample in EXPECTED_SAMPLES for role in EXPECTED_ROLES
        }
        if set(observed_pairs) != expected_pairs or len(observed_pairs) != len(expected_pairs):
            errors.append("objects must cover every sample/role pair exactly once")

    gates = manifest.get("gates")
    if not isinstance(gates, Mapping) or dict(gates) != {
        "required_http_206": 10,
        "required_exact_range_contract_pass": 10,
        "required_zip_prefix_parse": 10,
        "required_source_header_contract_pass": 10,
        "required_complete_archive_transfer_count": 0,
        "row_access_allowed_after_pass": False,
        "full_archive_download_allowed_after_pass": False,
        "gpu_allowed": False,
        "paid_data_allowed": False,
        "replacement_allowed": False,
    }:
        errors.append("gates changed")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, Mapping) or dict(outputs) != {
        "summary": "experiments/v14_aemo_source_contract_repair/artifacts/summary.json"
    }:
        errors.append("outputs changed")
    return tuple(errors)


def _source_header_projection_pass(
    spec: Mapping[str, object],
    parsed: object,
) -> bool:
    if not isinstance(parsed, Mapping):
        return False
    comparisons = {
        "member": "expected_member",
        "header_package": "expected_package",
        "header_table": "expected_table",
        "header_version": "expected_version",
    }
    if any(parsed.get(observed) != spec.get(expected) for observed, expected in comparisons.items()):
        return False
    fields = set(cast(list[str], parsed.get("header_fields", [])))
    required = set(cast(list[str], spec["required_fields"]))
    forbidden = set(cast(list[str], spec["forbidden_fields"]))
    return required <= fields and not fields.intersection(forbidden)


def audit_source_contract_repair_response(
    spec: Mapping[str, object],
    *,
    http_status: int | None,
    content: bytes,
    response_headers: Mapping[str, str],
    retrieved_at: str,
    transport_error: str | None,
) -> dict[str, object]:
    """Audit exact 64 KiB transport separately from the scientific header projection."""

    audit = audit_source_contract_response(
        spec,
        http_status=http_status,
        content=content,
        response_headers=response_headers,
        retrieved_at=retrieved_at,
        transport_error=transport_error,
    )
    errors = cast(list[str], audit["errors"])
    range_errors: list[str] = []
    content_range = next(
        (value for key, value in response_headers.items() if key.lower() == "content-range"),
        None,
    )
    match = re.fullmatch(r"bytes 0-(\d+)/(\d+)", content_range) if content_range else None
    if len(content) != RANGE_BYTES:
        range_errors.append(f"response bytes {len(content)} != {RANGE_BYTES}")
    if match is None:
        range_errors.append("missing exact zero-based Content-Range")
    else:
        final_byte = int(match.group(1))
        total_bytes = int(match.group(2))
        if final_byte != RANGE_BYTES - 1:
            range_errors.append(f"Content-Range final byte {final_byte} != {RANGE_BYTES - 1}")
        if total_bytes <= RANGE_BYTES:
            range_errors.append(f"Content-Range total {total_bytes} <= {RANGE_BYTES}")
    for error in range_errors:
        if error not in errors:
            errors.append(error)
    source_header_contract_pass = _source_header_projection_pass(spec, audit.get("parsed"))
    exact_range_contract_pass = not range_errors and audit["full_archive_downloaded"] is False
    source_contract_pass = not errors
    audit.update(
        {
            "source_header_contract_pass": source_header_contract_pass,
            "exact_range_contract_pass": exact_range_contract_pass,
            "source_contract_pass": source_contract_pass,
            "header_contract_pass": source_contract_pass,
        }
    )
    return audit


def summarize_source_contract_repair_audit(
    audits: Sequence[Mapping[str, object]],
    *,
    source_manifest: str,
    source_manifest_sha256: str,
    collector_git_commit: str,
    generated_at: str,
) -> dict[str, object]:
    """Summarize the ten-object repaired transport and scientific subgates."""

    expected = 10
    http_count = sum(item.get("http_status") == 206 for item in audits)
    range_count = sum(item.get("exact_range_contract_pass") is True for item in audits)
    parse_count = sum(item.get("zip_prefix_parse") is True for item in audits)
    header_count = sum(item.get("source_header_contract_pass") is True for item in audits)
    contract_count = sum(item.get("source_contract_pass") is True for item in audits)
    complete_count = sum(item.get("full_archive_downloaded") is True for item in audits)
    data_row_opened = any(item.get("data_row_opened") is True for item in audits)
    passed = (
        len(audits) == expected
        and http_count == expected
        and range_count == expected
        and parse_count == expected
        and header_count == expected
        and contract_count == expected
        and complete_count == 0
        and not data_row_opened
    )
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "source_manifest": source_manifest,
        "source_manifest_sha256": source_manifest_sha256,
        "collector_git_commit": collector_git_commit,
        "generated_at": generated_at,
        "expected_count": expected,
        "observed_count": len(audits),
        "http_206_count": http_count,
        "exact_range_contract_pass_count": range_count,
        "zip_prefix_parse_count": parse_count,
        "source_header_contract_pass_count": header_count,
        "source_contract_pass_count": contract_count,
        "complete_archive_transfer_count": complete_count,
        "total_response_bytes": sum(
            cast(int, item.get("response_bytes", 0)) for item in audits
        ),
        "pass": passed,
        "audits": list(audits),
        "data_row_opened": data_row_opened,
        "full_archive_downloaded": complete_count > 0,
        "gpu_used": False,
        "paid_data_used": False,
    }


__all__ = [
    "PREFIX_PROOF_SHA256",
    "RANGE_BYTES",
    "audit_source_contract_repair_response",
    "load_source_contract_manifest",
    "manifest_sha256",
    "nearest_unconsumed_complete_month",
    "summarize_source_contract_repair_audit",
    "utc_now",
    "validate_source_contract_repair_manifest",
]
