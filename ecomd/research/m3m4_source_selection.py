"""Outcome-blind source selection for V14 participant-response development."""

from __future__ import annotations

import argparse
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

import yaml

SCHEMA_VERSION = "ecophys-m3m4-source-selection/v1"
STAGE = "metadata_only"
CRITERION_STATES = frozenset({"pass", "partial", "unresolved", "fail"})
REQUIRED_CRITERIA = frozenset(
    {
        "exact_executable_mechanism",
        "exposure_denominator",
        "observable_null_action",
        "stable_action_unit",
        "same_unit_action_outcome",
        "outcome_blind_controls",
        "treatment_clock",
        "independent_interventions",
        "revision_failure_completeness",
        "licence_and_retention",
        "state_reconstruction",
        "sample_size_concentration",
    }
)
REQUIRED_KILL_SWITCHES = frozenset(
    {
        "exposure_denominator",
        "outcome_blind_controls",
        "treatment_clock",
        "licence_and_retention",
        "state_reconstruction",
    }
)
ACCESS_FLAGS = frozenset(
    {
        "chain_rpc_used",
        "external_workers_used",
        "gpu_used",
        "paid_data_used",
        "participant_action_rows_opened",
        "private_data_used",
        "realized_response_rows_opened",
        "source_code_metadata_opened",
    }
)
TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "selection_id",
        "as_of",
        "stage",
        "access_boundary",
        "criteria",
        "kill_switches",
        "candidates",
        "ordering",
        "selection",
        "next_actions",
    }
)
CANDIDATE_KEYS = frozenset(
    {"candidate_id", "system", "current_disposition", "criteria", "rationale", "sources"}
)
SOURCE_KEYS = frozenset({"id", "role", "url"})
SELECTION_KEYS = frozenset(
    {"candidate_id", "authorized_stage", "g1_admitted", "decision", "rationale"}
)
SAFE_SOURCE_PATHS: Mapping[str, tuple[str, ...]] = {
    "aave.com": ("/help/",),
    "aemo.com.au": ("/",),
    "bmrs.elexon.co.uk": ("/api-documentation/",),
    "bscdocs.elexon.co.uk": ("/",),
    "docs.compound.finance": ("/",),
    "forum.cow.fi": ("/",),
    "github.com": ("/compound-finance/", "/aave-dao/", "/cowprotocol/", "/Uniswap/"),
    "gov.uniswap.org": ("/",),
    "www.aemo.com.au": ("/",),
    "www.elexon.co.uk": ("/",),
    "www.neso.energy": ("/",),
}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def load_source_selection(path: str | Path) -> dict[str, object]:
    """Load a V14 source-selection manifest."""

    raw: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("source-selection root must be a mapping")
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


def _string_list(value: object, *, path: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not value or any(_string(item) is None for item in value):
        errors.append(f"{path} must be a non-empty list of strings")
        return []
    return [cast(str, item).strip() for item in value]


def source_url_error(url: str) -> str | None:
    """Return why a claimed official source is outside the frozen source boundary."""

    parsed = urlparse(url)
    if parsed.scheme != "https":
        return "URL must use https"
    if parsed.query or parsed.fragment or parsed.username or parsed.password:
        return "URL cannot contain query, fragment, or credentials"
    prefixes = SAFE_SOURCE_PATHS.get(parsed.hostname or "")
    if prefixes is None:
        return f"host is not allowlisted: {parsed.hostname}"
    if not any(parsed.path.startswith(prefix) for prefix in prefixes):
        return f"path is not allowlisted for that host: {parsed.path}"
    return None


def validate_source_selection(selection: Mapping[str, object]) -> list[str]:
    """Return structural and outcome-access violations for a source selection."""

    errors: list[str] = []
    if set(selection) != TOP_LEVEL_KEYS:
        errors.append(f"top level must contain exactly {sorted(TOP_LEVEL_KEYS)}")
    if selection.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION}")
    selection_id = _string(selection.get("selection_id"))
    if selection_id is None or ID_PATTERN.fullmatch(selection_id) is None:
        errors.append("selection_id must be a stable lowercase identifier")
    as_of = _string(selection.get("as_of"))
    if as_of is None or DATE_PATTERN.fullmatch(as_of) is None:
        errors.append("as_of must be an ISO date")
    if selection.get("stage") != STAGE:
        errors.append(f"stage must equal {STAGE}")

    boundary = _mapping(selection.get("access_boundary"))
    if boundary is None or set(boundary) != ACCESS_FLAGS:
        errors.append(f"access_boundary must contain exactly {sorted(ACCESS_FLAGS)}")
        boundary = {}
    for flag in ACCESS_FLAGS - {"source_code_metadata_opened"}:
        if boundary.get(flag) is not False:
            errors.append(f"access_boundary.{flag} must be false")
    if boundary.get("source_code_metadata_opened") is not True:
        errors.append("access_boundary.source_code_metadata_opened must be true and disclosed")

    criteria = _mapping(selection.get("criteria"))
    if criteria is None or set(criteria) != REQUIRED_CRITERIA:
        errors.append(f"criteria must contain exactly {sorted(REQUIRED_CRITERIA)}")
        criteria = {}
    for criterion_id, definition in criteria.items():
        if _string(definition) is None:
            errors.append(f"criteria.{criterion_id} must define the criterion")

    kill_switches = set(_string_list(selection.get("kill_switches"), path="kill_switches", errors=errors))
    if kill_switches != REQUIRED_KILL_SWITCHES:
        errors.append(f"kill_switches must equal {sorted(REQUIRED_KILL_SWITCHES)}")

    candidates = _mapping_list(selection.get("candidates"))
    if not candidates:
        errors.append("candidates must be a non-empty list of mappings")
        candidates = []
    candidate_ids: set[str] = set()
    source_ids: set[str] = set()
    for index, candidate in enumerate(candidates):
        path = f"candidates[{index}]"
        if set(candidate) != CANDIDATE_KEYS:
            errors.append(f"{path} must contain exactly {sorted(CANDIDATE_KEYS)}")
        candidate_id = _string(candidate.get("candidate_id"))
        if candidate_id is None or ID_PATTERN.fullmatch(candidate_id) is None or candidate_id in candidate_ids:
            errors.append(f"{path}.candidate_id must be unique and stable")
        else:
            candidate_ids.add(candidate_id)
        for key in ("system", "current_disposition", "rationale"):
            if _string(candidate.get(key)) is None:
                errors.append(f"{path}.{key} must be non-empty")
        assessments = _mapping(candidate.get("criteria"))
        if assessments is None or set(assessments) != REQUIRED_CRITERIA:
            errors.append(f"{path}.criteria must contain exactly {sorted(REQUIRED_CRITERIA)}")
            assessments = {}
        for criterion_id, assessment_object in assessments.items():
            assessment = _mapping(assessment_object)
            if assessment is None or set(assessment) != {"state", "reason"}:
                errors.append(f"{path}.criteria.{criterion_id} must contain state and reason")
                continue
            if assessment.get("state") not in CRITERION_STATES:
                errors.append(f"{path}.criteria.{criterion_id}.state is invalid")
            if _string(assessment.get("reason")) is None:
                errors.append(f"{path}.criteria.{criterion_id}.reason must be non-empty")
        sources = _mapping_list(candidate.get("sources"))
        if not sources:
            errors.append(f"{path}.sources must be a non-empty list")
            continue
        for source_index, source in enumerate(sources):
            source_path = f"{path}.sources[{source_index}]"
            if set(source) != SOURCE_KEYS:
                errors.append(f"{source_path} must contain exactly {sorted(SOURCE_KEYS)}")
            source_id = _string(source.get("id"))
            if source_id is None or ID_PATTERN.fullmatch(source_id) is None or source_id in source_ids:
                errors.append(f"{source_path}.id must be globally unique and stable")
            else:
                source_ids.add(source_id)
            if _string(source.get("role")) is None:
                errors.append(f"{source_path}.role must be non-empty")
            url = _string(source.get("url"))
            if url is None:
                errors.append(f"{source_path}.url must be non-empty")
            else:
                url_error = source_url_error(url)
                if url_error is not None:
                    errors.append(f"{source_path}.url {url_error}")

    ordering = _string_list(selection.get("ordering"), path="ordering", errors=errors)
    if len(ordering) != len(set(ordering)) or set(ordering) != candidate_ids:
        errors.append("ordering must contain every candidate exactly once")

    selected = _mapping(selection.get("selection"))
    if selected is None or set(selected) != SELECTION_KEYS:
        errors.append(f"selection must contain exactly {sorted(SELECTION_KEYS)}")
        selected = {}
    selected_id = _string(selected.get("candidate_id"))
    if selected_id not in candidate_ids:
        errors.append("selection.candidate_id must identify a candidate")
    if ordering and selected_id != ordering[0]:
        errors.append("selection.candidate_id must equal the first frozen ordering entry")
    if selected.get("authorized_stage") != "zero_row_metadata_preflight":
        errors.append("selection.authorized_stage must equal zero_row_metadata_preflight")
    if selected.get("g1_admitted") is not False:
        errors.append("selection.g1_admitted must remain false")
    for key in ("decision", "rationale"):
        if _string(selected.get(key)) is None:
            errors.append(f"selection.{key} must be non-empty")
    _string_list(selection.get("next_actions"), path="next_actions", errors=errors)
    return sorted(errors)


def source_selection_summary(selection: Mapping[str, object]) -> dict[str, object]:
    """Summarize ranking and unresolved kill switches without admitting a source."""

    selected = cast(Mapping[str, object], selection["selection"])
    selected_id = cast(str, selected["candidate_id"])
    candidates = cast(Sequence[Mapping[str, object]], selection["candidates"])
    candidate = next(item for item in candidates if item["candidate_id"] == selected_id)
    assessments = cast(Mapping[str, Mapping[str, object]], candidate["criteria"])
    blockers = sorted(
        criterion_id
        for criterion_id in REQUIRED_KILL_SWITCHES
        if assessments[criterion_id]["state"] != "pass"
    )
    counts = {state: 0 for state in sorted(CRITERION_STATES)}
    for assessment in assessments.values():
        counts[cast(str, assessment["state"])] += 1
    return {
        "selection_id": selection["selection_id"],
        "selected_candidate_id": selected_id,
        "authorized_stage": selected["authorized_stage"],
        "g1_admitted": False,
        "selected_state_counts": counts,
        "unresolved_kill_switches": blockers,
        "outcome_blind": True,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    return parser


def main() -> None:
    """Validate and summarize a frozen source-selection manifest."""

    args = _build_parser().parse_args()
    selection = load_source_selection(args.manifest)
    errors = validate_source_selection(selection)
    if errors:
        raise SystemExit("\n".join(errors))
    print(yaml.safe_dump(source_selection_summary(selection), sort_keys=True), end="")


if __name__ == "__main__":
    main()
