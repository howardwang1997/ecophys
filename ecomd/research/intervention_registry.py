"""Validation for the metadata-only intervention registry."""

from __future__ import annotations

import argparse
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

import yaml

SCHEMA_VERSION = "ecophys-intervention-registry/v2"
ROLES = frozenset({"development_only", "sealed_candidate", "reject"})
DATE_STATUSES = frozenset({"exact", "not_single_date", "not_implemented", "not_applicable", "unresolved"})
DATE_PHASES = frozenset({"announcement", "implementation", "end_or_reversal", "transition"})
TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "as_of",
        "contains_market_data",
        "sealed_periods_opened",
        "data_purchased",
        "workers_contacted",
        "protocol_deviations",
        "cases",
    }
)
CASE_KEYS = frozenset(
    {
        "id",
        "rule",
        "jurisdiction",
        "venue",
        "mechanism_family",
        "dates",
        "design",
        "required_data",
        "access",
        "risks",
        "role",
        "rationale",
        "sources",
    }
)
REQUIRED_DESIGN_KEYS = frozenset({"description", "treatment", "control", "published_analysis", "independence"})
REQUIRED_DATA_KEYS = frozenset({"event_fields", "depth", "clock_precision", "identifiers"})
REQUIRED_ACCESS_KEYS = frozenset({"public", "vendor", "licence", "records_opened"})
PROHIBITED_KEY_TOKENS = frozenset(
    {
        "coefficient",
        "effect",
        "estimate",
        "metric",
        "outcome",
        "pvalue",
        "result",
        "statistic",
        "value",
    }
)
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load_registry(path: str | Path) -> dict[str, object]:
    """Load a YAML registry and retain an object-typed validation boundary."""

    raw: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("intervention registry root must be a mapping")
    return cast(dict[str, object], raw)


def _mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _mapping_list(value: object) -> list[Mapping[str, object]] | None:
    if not isinstance(value, list):
        return None
    result: list[Mapping[str, object]] = []
    for item in value:
        mapped = _mapping(item)
        if mapped is None:
            return None
        result.append(mapped)
    return result


def _string(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _key_tokens(key: object) -> set[str]:
    if not isinstance(key, str):
        return set()
    normalized = re.sub(r"[^a-z0-9]+", "_", key.lower())
    return {token for token in normalized.split("_") if token}


def _validate_metadata_tree(value: object, *, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for raw_key, nested in value.items():
            if not isinstance(raw_key, str):
                errors.append(f"{path} contains a non-string key")
                continue
            prohibited = sorted(_key_tokens(raw_key) & PROHIBITED_KEY_TOKENS)
            if prohibited:
                errors.append(f"{path}.{raw_key} uses prohibited market-output key token: {prohibited[0]}")
            _validate_metadata_tree(nested, path=f"{path}.{raw_key}", errors=errors)
        return
    if isinstance(value, list):
        for index, nested in enumerate(value):
            _validate_metadata_tree(nested, path=f"{path}[{index}]", errors=errors)
        return
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return
    if isinstance(value, (int, float)):
        errors.append(f"{path} contains a numeric leaf; registry cases must contain metadata only")
        return
    errors.append(f"{path} contains unsupported metadata type {type(value).__name__}")


def _validate_string_list(value: object, *, path: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not value or any(_string(item) is None for item in value):
        errors.append(f"{path} must be a non-empty list of strings")
        return []
    return [cast(str, item).strip() for item in value]


def validate_registry(registry: Mapping[str, object]) -> list[str]:
    """Return deterministic structural and data-governance violations."""

    errors: list[str] = []
    unknown_top = sorted(set(registry) - TOP_LEVEL_KEYS)
    if unknown_top:
        errors.append(f"unknown top-level keys: {unknown_top}")
    if registry.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION}")
    if _string(registry.get("as_of")) is None or DATE_PATTERN.fullmatch(cast(str, registry.get("as_of", ""))) is None:
        errors.append("as_of must be an ISO date")
    for flag in ("contains_market_data", "sealed_periods_opened", "data_purchased", "workers_contacted"):
        if registry.get(flag) is not False:
            errors.append(f"{flag} must be false")

    deviations = _mapping_list(registry.get("protocol_deviations"))
    if deviations is None:
        errors.append("protocol_deviations must be a list of mappings")
        deviations = []
    contaminated_ids: set[str] = set()
    for index, deviation in enumerate(deviations):
        prefix = f"protocol_deviations[{index}]"
        if _string(deviation.get("id")) is None or _string(deviation.get("description")) is None:
            errors.append(f"{prefix} requires id and description")
        deviation_case_ids = _validate_string_list(
            deviation.get("case_ids"), path=f"{prefix}.case_ids", errors=errors
        )
        contaminated_ids.update(deviation_case_ids)

    cases = _mapping_list(registry.get("cases"))
    if not cases:
        errors.append("cases must be a non-empty list of mappings")
        cases = []
    registry_case_ids: set[str] = set()
    for index, case in enumerate(cases):
        prefix = f"cases[{index}]"
        unknown_case = sorted(set(case) - CASE_KEYS)
        if unknown_case:
            errors.append(f"{prefix} has unknown keys: {unknown_case}")
        _validate_metadata_tree(case, path=prefix, errors=errors)
        case_id = _string(case.get("id"))
        if case_id is None or ID_PATTERN.fullmatch(case_id) is None:
            errors.append(f"{prefix}.id is invalid: {case_id}")
            continue
        if case_id in registry_case_ids:
            errors.append(f"duplicate case id: {case_id}")
        registry_case_ids.add(case_id)
        for key in ("rule", "jurisdiction", "venue", "mechanism_family", "rationale"):
            if _string(case.get(key)) is None:
                errors.append(f"{case_id}.{key} must be a non-empty string")

        role = _string(case.get("role"))
        if role not in ROLES:
            errors.append(f"{case_id}.role is invalid: {role}")
        dates = _mapping(case.get("dates"))
        if dates is None or set(dates) != DATE_PHASES:
            errors.append(f"{case_id}.dates must contain exactly {sorted(DATE_PHASES)}")
            dates = {}
        sources = _mapping_list(case.get("sources"))
        if not sources:
            errors.append(f"{case_id}.sources must be a non-empty list")
            sources = []
        source_ids: set[str] = set()
        for s_index, source in enumerate(sources):
            s_prefix = f"{case_id}.sources[{s_index}]"
            source_id = _string(source.get("id"))
            url = _string(source.get("url"))
            accessed = _string(source.get("accessed"))
            if source_id is None or source_id in source_ids:
                errors.append(f"{s_prefix}.id must be non-empty and unique within the case")
            else:
                source_ids.add(source_id)
            if url is None or not url.startswith("https://"):
                errors.append(f"{s_prefix}.url must be https")
            if accessed is None or DATE_PATTERN.fullmatch(accessed) is None:
                errors.append(f"{s_prefix}.accessed must be an ISO date")
            if source.get("primary") is not True:
                errors.append(f"{s_prefix}.primary must be true")
            if _string(source.get("supports")) is None:
                errors.append(f"{s_prefix}.supports must be non-empty")

        for phase, entry_object in dates.items():
            entry = _mapping(entry_object)
            if entry is None:
                errors.append(f"{case_id}.dates.{phase} must be a mapping")
                continue
            status = _string(entry.get("status"))
            date = entry.get("date")
            if status not in DATE_STATUSES:
                errors.append(f"{case_id}.dates.{phase}.status is invalid: {status}")
            if status == "exact":
                if not isinstance(date, str) or DATE_PATTERN.fullmatch(date) is None:
                    errors.append(f"{case_id}.dates.{phase}.date must be an ISO date when exact")
            elif date is not None:
                errors.append(f"{case_id}.dates.{phase}.date must be null unless status is exact")
            if status != "exact" and _string(entry.get("note")) is None:
                errors.append(f"{case_id}.dates.{phase}.note is required for non-exact status")
            referenced_sources = _validate_string_list(
                entry.get("source_ids"), path=f"{case_id}.dates.{phase}.source_ids", errors=errors
            )
            unknown_sources = sorted(set(referenced_sources) - source_ids)
            if unknown_sources:
                errors.append(f"{case_id}.dates.{phase} references unknown sources: {unknown_sources}")

        design = _mapping(case.get("design"))
        if design is None or set(design) != REQUIRED_DESIGN_KEYS:
            errors.append(f"{case_id}.design must contain exactly {sorted(REQUIRED_DESIGN_KEYS)}")
            design = {}
        required_data = _mapping(case.get("required_data"))
        if required_data is None or set(required_data) != REQUIRED_DATA_KEYS:
            errors.append(f"{case_id}.required_data must contain exactly {sorted(REQUIRED_DATA_KEYS)}")
        access = _mapping(case.get("access"))
        if access is None or set(access) != REQUIRED_ACCESS_KEYS:
            errors.append(f"{case_id}.access must contain exactly {sorted(REQUIRED_ACCESS_KEYS)}")
            access = {}
        if access.get("records_opened") is not False:
            errors.append(f"{case_id}.access.records_opened must be false")
        _validate_string_list(case.get("risks"), path=f"{case_id}.risks", errors=errors)
        if role == "sealed_candidate":
            if design.get("published_analysis") is not False:
                errors.append(f"{case_id} cannot be sealed_candidate after a published analysis")
            if case_id in contaminated_ids:
                errors.append(f"{case_id} cannot be sealed_candidate after protocol contamination")

    unknown_contaminated = sorted(contaminated_ids - registry_case_ids)
    if unknown_contaminated:
        errors.append(f"protocol deviations reference unknown cases: {unknown_contaminated}")
    return sorted(errors)


def routing_summary(registry: Mapping[str, object]) -> dict[str, object]:
    """Summarize roles and whether the development-plus-sealed C1 prerequisite exists."""

    errors = validate_registry(registry)
    if errors:
        raise ValueError("invalid intervention registry:\n- " + "\n- ".join(errors))
    cases = cast(list[Mapping[str, object]], registry["cases"])
    counts = {role: 0 for role in sorted(ROLES)}
    for case in cases:
        role = cast(str, case["role"])
        counts[role] += 1
    ready = counts["development_only"] >= 1 and counts["sealed_candidate"] >= 1
    return {
        "case_count": len(cases),
        "role_counts": counts,
        "ready_for_data_contract": ready,
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Validate one metadata-only intervention registry."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", type=Path)
    args = parser.parse_args(argv)
    registry = load_registry(args.registry)
    errors = validate_registry(registry)
    if errors:
        for error in errors:
            print(error)
        return 1
    summary = routing_summary(registry)
    print(yaml.safe_dump(summary, sort_keys=True).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
