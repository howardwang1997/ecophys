"""AEMO SQLLoader metadata contract for the 5MS two-clock audit."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

import yaml

SCHEMA_VERSION = "ecophys-aemo-loader-controls/v3"
EXPECTED_SAMPLES = {
    "r0-validation-2020-09": (
        "2020-09",
        "A0_30_minute_only",
        "O0_legacy_reports",
    ),
    "r2-validation-2022-04": (
        "2022-04",
        "A2_5_minute_rule_live",
        "O3_5_minute_reports",
    ),
}
EXPECTED_ROLES = ("BIDDAYOFFER", "BIDPEROFFER", "DISPATCHOFFERTRK")
EXPECTED_TARGETS = {
    ("r0-validation-2020-09", "BIDDAYOFFER"): ("BIDDAYOFFER", "BIDDAYOFFER"),
    ("r0-validation-2020-09", "BIDPEROFFER"): ("BIDPEROFFER", "BIDPEROFFER"),
    ("r0-validation-2020-09", "DISPATCHOFFERTRK"): (
        "DISPATCHOFFERTRK",
        "DISPATCHOFFERTRK",
    ),
    ("r2-validation-2022-04", "BIDDAYOFFER"): ("BIDDAYOFFER", "BIDDAYOFFER"),
    ("r2-validation-2022-04", "BIDPEROFFER"): (
        "BIDOFFERPERIOD",
        "BIDOFFERPERIOD",
    ),
    ("r2-validation-2022-04", "DISPATCHOFFERTRK"): (
        "DISPATCHOFFERTRK",
        "DISPATCHOFFERTRK",
    ),
}
ROOT_KEYS = frozenset(
    {
        "schema_version",
        "sample_id",
        "frozen_at",
        "parent_commit",
        "scientific_role",
        "selection",
        "phase_clocks",
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
        "expected_owner",
        "expected_target_table",
        "required_columns",
        "required_non_filler_columns",
    }
)


def load_loader_manifest(path: str | Path) -> dict[str, object]:
    """Load a loader-control manifest at an object-typed boundary."""

    payload: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("AEMO loader-control manifest root must be a mapping")
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


def validate_loader_manifest(manifest: Mapping[str, object]) -> tuple[str, ...]:
    """Validate the frozen two-clock metadata boundary and exact URL set."""

    errors: list[str] = []
    if set(manifest) != ROOT_KEYS:
        errors.append("root keys changed")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if manifest.get("scientific_role") != "development_only_loader_metadata_validation":
        errors.append("scientific_role changed")
    if not _utc(manifest.get("frozen_at")):
        errors.append("frozen_at must be a UTC timestamp")
    if not _sha(manifest.get("parent_commit"), 40):
        errors.append("parent_commit must be a full SHA-1")

    selection = manifest.get("selection")
    if not isinstance(selection, Mapping):
        errors.append("selection must be a mapping")
    else:
        if selection.get("rule") != (
            "six_calendar_months_before_2021_03_reporting_deployment_month_and_"
            "six_calendar_months_after_2021_10_rule_commencement_month"
        ):
            errors.append("selection rule changed")
        if selection.get("no_replacement") is not True:
            errors.append("validation controls cannot be replaced")
        if selection.get("previously_accessed_before_freeze") is not False:
            errors.append("validation controls must be unopened at freeze")

    phase_clocks = manifest.get("phase_clocks")
    if not isinstance(phase_clocks, Mapping) or set(phase_clocks) != {
        "reporting_production_deployment",
        "bidding_transition_start",
        "rule_commencement",
    }:
        errors.append("phase clocks changed")
    elif dict(phase_clocks) != {
        "reporting_production_deployment": "2021-03-08",
        "bidding_transition_start": "2021-04-01",
        "rule_commencement": "2021-10-01",
    }:
        errors.append("phase clock dates changed")

    objects = manifest.get("objects")
    observed_pairs: list[tuple[str, str]] = []
    if not isinstance(objects, list) or len(objects) != 6:
        errors.append("objects must contain exactly six entries")
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
            if sample_label is None or sample_label not in EXPECTED_SAMPLES:
                errors.append(f"objects[{index}].sample_label is invalid")
                continue
            month, mechanism_phase, observation_phase = EXPECTED_SAMPLES[sample_label]
            if item.get("month") != month:
                errors.append(f"objects[{index}].month changed")
            if item.get("mechanism_phase") != mechanism_phase:
                errors.append(f"objects[{index}].mechanism_phase changed")
            if item.get("observation_phase") != observation_phase:
                errors.append(f"objects[{index}].observation_phase changed")
            if role is None or role not in EXPECTED_ROLES:
                errors.append(f"objects[{index}].logical_role is invalid")
                continue
            observed_pairs.append((sample_label, role))
            expected_owner, expected_target = EXPECTED_TARGETS[(sample_label, role)]
            if item.get("expected_owner") != expected_owner:
                errors.append(f"objects[{index}].expected_owner changed")
            if item.get("expected_target_table") != expected_target:
                errors.append(f"objects[{index}].expected_target_table changed")
            url = _text(item.get("url"))
            if url is None:
                errors.append(f"objects[{index}].url is invalid")
            else:
                parsed = urlparse(url)
                expected_suffix = f"PUBLIC_DVD_{role}_{month.replace('-', '')}.ctl"
                if (
                    parsed.scheme != "https"
                    or parsed.hostname != "www.nemweb.com.au"
                    or parsed.query
                    or f"/MMSDM_{month.replace('-', '_')}/" not in parsed.path
                    or not parsed.path.endswith(expected_suffix)
                    or "/MMSDM_Historical_Data_SQLLoader/CTL/" not in parsed.path
                ):
                    errors.append(f"objects[{index}].url is outside the frozen AEMO boundary")
            required = item.get("required_columns")
            non_filler = item.get("required_non_filler_columns")
            if (
                not isinstance(required, list)
                or not required
                or any(_text(column) is None for column in required)
                or len(set(cast(list[str], required))) != len(required)
            ):
                errors.append(f"objects[{index}].required_columns is invalid")
            if (
                not isinstance(non_filler, list)
                or not non_filler
                or any(_text(column) is None for column in non_filler)
                or not set(cast(list[str], non_filler)).issubset(
                    set(cast(list[str], required)) if isinstance(required, list) else set()
                )
            ):
                errors.append(f"objects[{index}].required_non_filler_columns is invalid")
        expected_pairs = {
            (sample_label, role) for sample_label in EXPECTED_SAMPLES for role in EXPECTED_ROLES
        }
        if set(observed_pairs) != expected_pairs or len(observed_pairs) != len(expected_pairs):
            errors.append("objects must cover every sample/role pair exactly once")

    gates = manifest.get("gates")
    if not isinstance(gates, Mapping) or dict(gates) != {
        "required_http_200": 6,
        "required_parse_pass": 6,
        "required_contract_pass": 6,
        "row_access_allowed_after_pass": False,
        "archive_download_allowed_after_pass": False,
        "gpu_allowed": False,
        "replacement_allowed": False,
    }:
        errors.append("gates changed")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, Mapping) or set(outputs) != {"summary"}:
        errors.append("outputs must declare only summary")
    elif _text(outputs.get("summary")) is None:
        errors.append("summary output path is invalid")
    return tuple(errors)


def parse_loader_control(text: str) -> dict[str, object]:
    """Parse the structural metadata in one AEMO SQLLoader control file."""

    normalized = text.replace("\r\n", "\n")
    patterns = {
        "title": r"-- Title:\s*([^\n]+)",
        "owner": r"USER TO CONNECT AS ([A-Z0-9_]+) owner",
        "infile": r"^INFILE\s+([^\s]+)",
        "target_table": r"^APPEND INTO TABLE\s+([A-Z0-9_]+)",
    }
    values: dict[str, str] = {}
    for name, pattern in patterns.items():
        match = re.search(pattern, normalized, flags=re.MULTILINE)
        if match is None:
            raise ValueError(f"missing loader-control {name}")
        values[name] = match.group(1).strip()
    block = re.search(
        r"TRAILING NULLCOLS\s*\n\((.*)\)\s*-- End of Script",
        normalized,
        flags=re.DOTALL,
    )
    if block is None:
        raise ValueError("missing loader-control column block")
    columns: list[str] = []
    filler_columns: list[str] = []
    for raw_line in block.group(1).splitlines():
        line = raw_line.strip().rstrip(",").strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2 or re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", parts[0]) is None:
            raise ValueError(f"invalid loader-control column line: {raw_line!r}")
        column = parts[0].upper()
        if column in columns:
            raise ValueError(f"duplicate loader-control column: {column}")
        columns.append(column)
        if re.search(r"\bFILLER\b", parts[1], flags=re.IGNORECASE):
            filler_columns.append(column)
    if not columns:
        raise ValueError("loader-control column block is empty")
    filler_set = set(filler_columns)
    return {
        **values,
        "columns": columns,
        "filler_columns": filler_columns,
        "non_filler_columns": [column for column in columns if column not in filler_set],
    }


def audit_loader_control(
    spec: Mapping[str, object],
    *,
    http_status: int | None,
    content: bytes,
    response_headers: Mapping[str, str],
    retrieved_at: str,
    transport_error: str | None,
) -> dict[str, object]:
    """Audit one retrieved control file against its frozen contract."""

    errors: list[str] = []
    parsed: dict[str, object] | None = None
    if http_status != 200:
        errors.append(f"HTTP status {http_status!r} != 200")
    if transport_error is not None:
        errors.append(transport_error)
    if len(content) > 65_536:
        errors.append("control file exceeds 65536-byte metadata cap")
    if http_status == 200 and not errors:
        try:
            parsed = parse_loader_control(content.decode("utf-8-sig"))
        except (UnicodeDecodeError, ValueError) as error:
            errors.append(f"{type(error).__name__}: {error}")
    if parsed is not None:
        if parsed["owner"] != spec.get("expected_owner"):
            errors.append(f"owner {parsed['owner']} != {spec.get('expected_owner')}")
        if parsed["target_table"] != spec.get("expected_target_table"):
            errors.append(
                f"target table {parsed['target_table']} != {spec.get('expected_target_table')}"
            )
        columns = set(cast(list[str], parsed["columns"]))
        required = set(cast(list[str], spec["required_columns"]))
        missing = sorted(required - columns)
        if missing:
            errors.append(f"missing required columns: {missing}")
        filler = set(cast(list[str], parsed["filler_columns"]))
        required_non_filler = set(cast(list[str], spec["required_non_filler_columns"]))
        invalid_filler = sorted(required_non_filler & filler)
        if invalid_filler:
            errors.append(f"required columns marked FILLER: {invalid_filler}")
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
        "content_bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest() if content else None,
        "parsed": parsed,
        "parse_pass": parsed is not None,
        "contract_pass": not errors,
        "errors": errors,
        "row_opened": False,
        "archive_opened": False,
        "gpu_used": False,
    }


def summarize_loader_audit(
    audits: Sequence[Mapping[str, object]],
    *,
    source_manifest: str,
    source_manifest_sha256: str,
    collector_git_commit: str,
    generated_at: str,
) -> dict[str, object]:
    """Summarize the exact six-control metadata audit."""

    expected_count = 6
    http_200_count = sum(item.get("http_status") == 200 for item in audits)
    parse_pass_count = sum(item.get("parse_pass") is True for item in audits)
    contract_pass_count = sum(item.get("contract_pass") is True for item in audits)
    return {
        "schema_version": "ecophys-aemo-loader-controls-summary/v3",
        "source_manifest": source_manifest,
        "source_manifest_sha256": source_manifest_sha256,
        "collector_git_commit": collector_git_commit,
        "generated_at": generated_at,
        "expected_count": expected_count,
        "observed_count": len(audits),
        "http_200_count": http_200_count,
        "parse_pass_count": parse_pass_count,
        "contract_pass_count": contract_pass_count,
        "pass": (
            len(audits) == expected_count
            and http_200_count == expected_count
            and parse_pass_count == expected_count
            and contract_pass_count == expected_count
        ),
        "audits": list(audits),
        "row_opened": False,
        "archive_opened": False,
        "gpu_used": False,
        "paid_data_used": False,
    }
