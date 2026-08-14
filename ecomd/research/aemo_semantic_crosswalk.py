"""Frozen AEMO semantic crosswalk and held-out object-resolution contract."""

from __future__ import annotations

import copy
import hashlib
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import cast
from urllib.parse import urlparse

import yaml

from ecomd.research.aemo_development_audit import inspect_aemo_archive

SCHEMA_VERSION = "ecophys-aemo-semantic-crosswalk/v2"
HEADER_SCHEMA_VERSION = "ecophys-aemo-semantic-crosswalk-heldout-headers/v2"
UNRESOLVED_STAGE = "crosswalk_and_exact_urls_frozen_no_validation_request"
RESOLVED_STAGE = "exact_head_metadata_resolved_no_archive_or_row_opened"
EXPECTED_SAMPLES = {
    "heldout-legacy-2021-09": ("2021-09", "2021-09-07", "legacy_public_dvd"),
    "heldout-current-2025-07": (
        "2025-07",
        "2025-07-01",
        "public_archive_hash_delimited",
    ),
}
EXPECTED_ROLES = (
    "BIDDAYOFFER_D",
    "BIDPEROFFER_D",
    "DISPATCHOFFERTRK",
    "DISPATCHLOAD",
    "DUDETAILSUMMARY",
)
EXPECTED_REGIMES = frozenset({"legacy_public_dvd", "public_archive_hash_delimited"})
ROOT_KEYS = frozenset(
    {
        "schema_version",
        "sample_id",
        "frozen_at",
        "parent_commit",
        "stage",
        "scientific_role",
        "discovery",
        "selection",
        "crosswalk",
        "objects",
        "resolution",
        "gates",
        "outputs",
    }
)
OBJECT_KEYS = frozenset(
    {
        "object_id",
        "sample_label",
        "logical_role",
        "url",
        "http_status",
        "expected_bytes",
        "etag",
        "last_modified",
    }
)


def load_crosswalk(path: str | Path) -> dict[str, object]:
    """Load a crosswalk manifest at an object-typed boundary."""

    payload: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("AEMO crosswalk root must be a mapping")
    return cast(dict[str, object], payload)


def manifest_sha256(path: str | Path) -> str:
    """Hash exact serialized manifest bytes."""

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


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


def _sha(value: object, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in "0123456789abcdef" for character in value)
    )


def _validate_crosswalk_entries(value: object, errors: list[str]) -> None:
    if not isinstance(value, list) or len(value) != len(EXPECTED_ROLES):
        errors.append("crosswalk must contain exactly five logical roles")
        return
    roles: list[str] = []
    for index, raw_entry in enumerate(value):
        if not isinstance(raw_entry, Mapping):
            errors.append(f"crosswalk[{index}] must be a mapping")
            continue
        entry = cast(Mapping[str, object], raw_entry)
        if set(entry) != {"logical_role", "canonical_fields", "regimes"}:
            errors.append(f"crosswalk[{index}] has unexpected keys")
        role = _text(entry.get("logical_role"))
        if role is not None:
            roles.append(role)
        fields = entry.get("canonical_fields")
        if not isinstance(fields, list) or not fields or any(_text(item) is None for item in fields):
            errors.append(f"crosswalk[{index}].canonical_fields must be non-empty text")
            canonical_fields: set[str] = set()
        else:
            canonical_fields = set(cast(list[str], fields))
            if len(canonical_fields) != len(fields):
                errors.append(f"crosswalk[{index}].canonical_fields must be unique")
        regimes = entry.get("regimes")
        if not isinstance(regimes, Mapping) or set(regimes) != EXPECTED_REGIMES:
            errors.append(f"crosswalk[{index}].regimes must contain both frozen regimes")
            continue
        for regime_name, raw_mapping in regimes.items():
            if not isinstance(raw_mapping, Mapping):
                errors.append(f"crosswalk[{index}].regimes.{regime_name} must be a mapping")
                continue
            mapping = cast(Mapping[str, object], raw_mapping)
            if set(mapping) != {
                "header_package",
                "header_table",
                "required_source_fields",
                "field_map",
            }:
                errors.append(f"crosswalk[{index}].regimes.{regime_name} has unexpected keys")
            required = mapping.get("required_source_fields")
            if (
                not isinstance(required, list)
                or not required
                or any(_text(item) is None for item in required)
            ):
                errors.append(f"crosswalk[{index}].regimes.{regime_name}.required_source_fields is invalid")
                required_fields: set[str] = set()
            else:
                required_fields = set(cast(list[str], required))
                if len(required_fields) != len(required):
                    errors.append(
                        f"crosswalk[{index}].regimes.{regime_name}.required_source_fields must be unique"
                    )
            field_map = mapping.get("field_map")
            if not isinstance(field_map, Mapping) or set(field_map) != canonical_fields:
                errors.append(
                    f"crosswalk[{index}].regimes.{regime_name}.field_map must cover canonical fields"
                )
                continue
            for canonical, raw_rule in field_map.items():
                if not isinstance(raw_rule, Mapping) or set(raw_rule) != {"sources", "transform"}:
                    errors.append(
                        f"crosswalk[{index}].regimes.{regime_name}.field_map.{canonical} is invalid"
                    )
                    continue
                sources = raw_rule.get("sources")
                if (
                    not isinstance(sources, list)
                    or not sources
                    or any(_text(item) is None for item in sources)
                    or not set(cast(list[str], sources)).issubset(required_fields)
                ):
                    errors.append(
                        f"crosswalk[{index}].regimes.{regime_name}.field_map.{canonical}.sources is invalid"
                    )
                if _text(raw_rule.get("transform")) is None:
                    errors.append(
                        f"crosswalk[{index}].regimes.{regime_name}.field_map.{canonical}.transform is invalid"
                    )
    if tuple(roles) != EXPECTED_ROLES:
        errors.append("crosswalk logical-role order changed")


def validate_crosswalk(manifest: Mapping[str, object]) -> tuple[str, ...]:
    """Validate the frozen discovery/held-out boundary and exact URL set."""

    errors: list[str] = []
    if set(manifest) != ROOT_KEYS:
        errors.append("root keys changed")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    stage = manifest.get("stage")
    if stage not in {UNRESOLVED_STAGE, RESOLVED_STAGE}:
        errors.append("stage is unsupported")
    if manifest.get("scientific_role") != "development_only_heldout_schema_validation":
        errors.append("scientific_role changed")
    if not _utc(manifest.get("frozen_at")):
        errors.append("frozen_at must be a UTC timestamp")
    if not _sha(manifest.get("parent_commit"), 40):
        errors.append("parent_commit must be a full SHA-1")

    discovery = manifest.get("discovery")
    if not isinstance(discovery, Mapping):
        errors.append("discovery must be a mapping")
    else:
        if discovery.get("use") != "schema_discovery_only":
            errors.append("discovery samples cannot be validation data")
        if discovery.get("sample_labels") != ["legacy-2021-03", "current-2025-01"]:
            errors.append("discovery sample labels changed")
        if not _sha(discovery.get("header_contract_sha256"), 64):
            errors.append("discovery header-contract hash is invalid")

    selection = manifest.get("selection")
    if not isinstance(selection, Mapping):
        errors.append("selection must be a mapping")
    else:
        if (
            selection.get("rule")
            != "add_six_calendar_months_to_each_discovery_month_then_use_first_gregorian_tuesday"
        ):
            errors.append("selection rule changed")
        if selection.get("no_replacement") is not True:
            errors.append("held-out samples cannot be replaced")
        samples = selection.get("validation_samples")
        observed: dict[str, tuple[object, object, object]] = {}
        if isinstance(samples, list):
            for sample in samples:
                if isinstance(sample, Mapping) and isinstance(sample.get("sample_label"), str):
                    observed[cast(str, sample["sample_label"])] = (
                        sample.get("month"),
                        sample.get("market_date"),
                        sample.get("naming_regime"),
                    )
        if observed != EXPECTED_SAMPLES:
            errors.append("held-out validation samples changed")

    _validate_crosswalk_entries(manifest.get("crosswalk"), errors)

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
            sample_label = _text(item.get("sample_label"))
            role = _text(item.get("logical_role"))
            if sample_label is not None and role is not None:
                observed_pairs.append((sample_label, role))
            url = _text(item.get("url"))
            if url is None:
                errors.append(f"objects[{index}].url is invalid")
            else:
                parsed = urlparse(url)
                if (
                    parsed.scheme != "https"
                    or parsed.hostname != "www.nemweb.com.au"
                    or not parsed.path.endswith(".zip")
                    or "/DATA/" not in parsed.path
                ):
                    errors.append(f"objects[{index}].url is outside the frozen AEMO boundary")
            status = item.get("http_status")
            size = item.get("expected_bytes")
            if stage == UNRESOLVED_STAGE:
                if any(
                    item.get(key) is not None
                    for key in ("http_status", "expected_bytes", "etag", "last_modified")
                ):
                    errors.append(f"objects[{index}] contains pre-resolution metadata")
            elif isinstance(status, bool) or not isinstance(status, int):
                errors.append(f"objects[{index}].http_status must be an integer after resolution")
            elif status == 200 and (isinstance(size, bool) or not isinstance(size, int) or size <= 0):
                errors.append(f"objects[{index}].expected_bytes must be positive for HTTP 200")
        expected_pairs = {
            (sample_label, role) for sample_label in EXPECTED_SAMPLES for role in EXPECTED_ROLES
        }
        if set(observed_pairs) != expected_pairs or len(observed_pairs) != len(expected_pairs):
            errors.append("objects must cover every held-out sample/role pair exactly once")

    resolution = manifest.get("resolution")
    if not isinstance(resolution, Mapping) or set(resolution) != {
        "source_manifest_sha256",
        "resolved_at",
        "resolver_git_commit",
        "all_head_requests_pass",
    }:
        errors.append("resolution metadata is invalid")
    elif stage == UNRESOLVED_STAGE:
        if any(value is not None for value in resolution.values()):
            errors.append("unresolved manifest contains resolution metadata")
    else:
        if not _sha(resolution.get("source_manifest_sha256"), 64):
            errors.append("resolved source-manifest hash is invalid")
        if not _sha(resolution.get("resolver_git_commit"), 40):
            errors.append("resolver commit is invalid")
        if not _utc(resolution.get("resolved_at")):
            errors.append("resolved_at must be a UTC timestamp")
        if not isinstance(resolution.get("all_head_requests_pass"), bool):
            errors.append("all_head_requests_pass must be boolean")

    gates = manifest.get("gates")
    if not isinstance(gates, Mapping):
        errors.append("gates must be a mapping")
    else:
        if gates.get("row_access_before_heldout_header_commit_allowed") is not False:
            errors.append("row access must remain locked")
        if gates.get("discovery_months_may_count_as_validation") is not False:
            errors.append("discovery months cannot count as validation")
        if gates.get("gpu_allowed") is not False:
            errors.append("GPU use is forbidden")

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


def resolve_head_metadata(
    manifest: Mapping[str, object],
    observations: Sequence[Mapping[str, object]],
    *,
    source_manifest_sha256: str,
    resolved_at: str,
    resolver_git_commit: str,
) -> dict[str, object]:
    """Create a resolved copy from an exact ordered HEAD ledger."""

    errors = validate_crosswalk(manifest)
    if errors or manifest.get("stage") != UNRESOLVED_STAGE:
        raise ValueError("source crosswalk is not a valid unresolved manifest: " + "; ".join(errors))
    objects = cast(list[dict[str, object]], manifest["objects"])
    if len(observations) != len(objects):
        raise ValueError("HEAD observation count differs from frozen object count")
    result = copy.deepcopy(dict(manifest))
    resolved_objects = cast(list[dict[str, object]], result["objects"])
    all_pass = True
    for index, (item, observation) in enumerate(zip(resolved_objects, observations, strict=True)):
        if observation.get("object_id") != item["object_id"]:
            raise ValueError(f"HEAD observation {index} is out of order")
        status = observation.get("http_status")
        content_length = observation.get("content_length")
        item["http_status"] = status
        item["expected_bytes"] = content_length if status == 200 else None
        item["etag"] = observation.get("etag")
        item["last_modified"] = observation.get("last_modified")
        all_pass = all_pass and status == 200 and isinstance(content_length, int) and content_length > 0
    result["stage"] = RESOLVED_STAGE
    result["resolution"] = {
        "source_manifest_sha256": source_manifest_sha256,
        "resolved_at": resolved_at,
        "resolver_git_commit": resolver_git_commit,
        "all_head_requests_pass": all_pass,
    }
    return result


def _sample_regime(manifest: Mapping[str, object], sample_label: str) -> str:
    selection = cast(Mapping[str, object], manifest["selection"])
    samples = cast(list[Mapping[str, object]], selection["validation_samples"])
    for sample in samples:
        if sample.get("sample_label") == sample_label:
            return cast(str, sample["naming_regime"])
    raise KeyError(f"unknown held-out sample label: {sample_label}")


def _role_mapping(
    manifest: Mapping[str, object], logical_role: str, naming_regime: str
) -> tuple[Mapping[str, object], list[str]]:
    entries = cast(list[Mapping[str, object]], manifest["crosswalk"])
    for entry in entries:
        if entry.get("logical_role") == logical_role:
            regimes = cast(Mapping[str, Mapping[str, object]], entry["regimes"])
            return regimes[naming_regime], cast(list[str], entry["canonical_fields"])
    raise KeyError(f"unknown crosswalk logical role: {logical_role}")


def inspect_crosswalk_archive(
    path: str | Path,
    spec: Mapping[str, object],
    manifest: Mapping[str, object],
) -> dict[str, object]:
    """Audit one held-out archive against the frozen semantic projection."""

    sample_label = cast(str, spec["sample_label"])
    logical_role = cast(str, spec["logical_role"])
    naming_regime = _sample_regime(manifest, sample_label)
    mapping, canonical_fields = _role_mapping(manifest, logical_role, naming_regime)
    expected_package = cast(str, mapping["header_package"])
    expected_table = cast(str, mapping["header_table"])
    required_fields = cast(list[str], mapping["required_source_fields"])
    base_spec = dict(spec)
    base_spec["archive_table"] = expected_table
    base_spec["minimum_header_fields"] = required_fields
    audit = inspect_aemo_archive(path, base_spec)
    errors = cast(list[str], list(cast(list[object], audit["errors"])))
    if audit.get("header_package") != expected_package:
        errors.append(f"header package {audit.get('header_package')} != frozen package {expected_package}")
    audit.update(
        {
            "naming_regime": naming_regime,
            "expected_header_package": expected_package,
            "expected_header_table": expected_table,
            "canonical_fields": canonical_fields,
            "crosswalk_field_map": dict(cast(Mapping[str, object], mapping["field_map"])),
            "errors": errors,
            "header_pass": not errors,
        }
    )
    return audit


def build_heldout_header_contract(
    audits: Sequence[Mapping[str, object]],
    *,
    source_manifest: str,
    source_manifest_sha256: str,
    generated_at: str,
    generator_git_commit: str,
) -> dict[str, object]:
    """Build the held-out header result while retaining the row lock."""

    return {
        "schema_version": HEADER_SCHEMA_VERSION,
        "generated_at": generated_at,
        "generator_git_commit": generator_git_commit,
        "source_manifest": source_manifest,
        "source_manifest_sha256": source_manifest_sha256,
        "scientific_role": "development_only_heldout_schema_validation",
        "all_headers_pass": len(audits) == 10 and all(audit.get("header_pass") is True for audit in audits),
        "discovery_samples_count_as_validation": False,
        "row_counts_opened": False,
        "row_join_authorized": False,
        "objects": [dict(audit) for audit in audits],
        "next_gate": "commit_this_heldout_result_before_any_row_filter_transform_or_join",
    }


def summarize_heldout_header_audit(
    downloads: Sequence[Mapping[str, object]],
    audits: Sequence[Mapping[str, object]],
    *,
    expected_count: int,
    download_ledger_sha256: str,
) -> dict[str, object]:
    """Summarize transport, integrity and crosswalk-header gates."""

    exact_count = len(downloads) == expected_count and len(audits) == expected_count
    http_200 = sum(download.get("http_status") == 200 for download in downloads)
    byte_matches = sum(
        download.get("observed_bytes") == download.get("expected_bytes") for download in downloads
    )
    sha_count = sum(isinstance(download.get("sha256"), str) for download in downloads)
    crc_passes = sum(audit.get("zip_crc_pass") is True for audit in audits)
    single_members = sum(audit.get("single_csv_member") is True for audit in audits)
    package_matches = sum(
        audit.get("header_package") == audit.get("expected_header_package") for audit in audits
    )
    table_matches = sum(audit.get("header_table") == audit.get("expected_header_table") for audit in audits)
    field_passes = sum(not audit.get("missing_minimum_header_fields") for audit in audits)
    header_passes = sum(audit.get("header_pass") is True for audit in audits)
    gates = {
        "exact_object_count": exact_count,
        "http_200_rate": http_200 == expected_count,
        "expected_byte_match_rate": byte_matches == expected_count,
        "sha256_present_rate": sha_count == expected_count,
        "zip_crc_pass_rate": crc_passes == expected_count,
        "single_csv_member_rate": single_members == expected_count,
        "header_package_match_rate": package_matches == expected_count,
        "header_table_match_rate": table_matches == expected_count,
        "crosswalk_source_field_rate": field_passes == expected_count,
        "all_headers_pass": header_passes == expected_count,
    }
    return {
        "schema": "ecophys-aemo-semantic-crosswalk-header-summary/v2",
        "scientific_role": "development_only_heldout_schema_validation",
        "expected_object_count": expected_count,
        "download_ledger_count": len(downloads),
        "header_audit_count": len(audits),
        "http_200_count": http_200,
        "expected_byte_match_count": byte_matches,
        "sha256_count": sha_count,
        "zip_crc_pass_count": crc_passes,
        "single_csv_member_count": single_members,
        "header_package_match_count": package_matches,
        "header_table_match_count": table_matches,
        "crosswalk_source_field_pass_count": field_passes,
        "header_pass_count": header_passes,
        "download_ledger_sha256": download_ledger_sha256,
        "gates": gates,
        "pass": all(gates.values()),
    }


def utc_now() -> str:
    """Return the canonical current UTC timestamp."""

    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
