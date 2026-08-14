"""Deterministic, outcome-blind selection for prospective intervention events."""

from __future__ import annotations

import argparse
import hashlib
import re
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

import yaml

SCHEMA_VERSION = "ecophys-prospective-event-selection/v1"
STAGE = "metadata_only"
SELECTION_STATUSES = frozenset({"frozen_no_event_selected", "event_selected"})
CANDIDATE_STATUSES = frozenset({"pending_audit", "audited_ineligible", "qualified", "selected"})
REQUIRED_CRITERIA = frozenset(
    {
        "binding_specification",
        "common_response_ladder",
        "economic_treatment",
        "identity_history",
        "independent_governance",
        "licence_and_retention",
        "minimum_lead_time",
        "null_failure_capture",
        "observable_actions",
        "observable_outcomes",
        "post_freeze_origin",
        "pre_event_precision_feasible",
    }
)
TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "selection_id",
        "as_of",
        "stage",
        "status",
        "access_boundary",
        "freeze",
        "universe",
        "qualification",
        "ordering",
        "candidate_registry",
        "selection",
        "failure_policy",
        "monitoring",
        "outputs",
    }
)
ACCESS_FLAGS = frozenset(
    {
        "candidate_effects_compared",
        "external_workers_used",
        "paid_data_used",
        "target_outcomes_opened",
        "target_rows_opened",
    }
)
FREEZE_KEYS = frozenset(
    {
        "effective_at",
        "parent_commit",
        "authority",
        "proposal_publication_rule",
        "outcome_blind_rule",
    }
)
QUALIFICATION_KEYS = frozenset({"all_required", "minimum_lead_days", "audit_sla_hours", "criteria"})
ORDERING_KEYS = frozenset(
    {"primary_key", "secondary_key", "canonical_event_id", "no_replacement", "late_audit_policy"}
)
SELECTION_KEYS = frozenset({"event_id", "selected_at", "evidence_hash", "reason"})
FAILURE_POLICY_KEYS = frozenset(
    {
        "selected_event_failure_counts",
        "first_event_never_erased",
        "secondary_event_labelled_separately",
        "no_inconvenience_replacement",
    }
)
MONITORING_KEYS = frozenset({"cadence", "permitted_metadata", "forbidden_before_activation"})
CANDIDATE_KEYS = frozenset(
    {
        "candidate_id",
        "platform_id",
        "official_proposal_id",
        "proposal_published_at",
        "final_package_at",
        "activation_at",
        "audit_completed_at",
        "outcome_accessed",
        "status",
        "criteria",
        "evidence_hash",
        "exclusion_reason",
    }
)
PLATFORM_KEYS = frozenset({"platform_id", "governance_authority", "independence_basis", "status", "sources"})
SOURCE_KEYS = frozenset({"id", "role", "url"})
SAFE_SOURCE_PATHS: Mapping[str, tuple[str, ...]] = {
    "docs.cow.fi": ("/",),
    "docs.uniswap.org": ("/",),
    "forum.cow.fi": ("/c/", "/t/"),
    "github.com": ("/cowprotocol/", "/Uniswap/"),
    "gov.uniswap.org": ("/c/", "/t/"),
}
EXPECTED_PLATFORMS = frozenset({"cow_protocol", "uniswap_protocol"})
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
EVIDENCE_SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def load_selection_contract(path: str | Path) -> dict[str, object]:
    """Load a YAML selection contract at an object-typed boundary."""

    raw: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("selection contract root must be a mapping")
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


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    return _string(value)


def _string_list(value: object, *, path: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not value or any(_string(item) is None for item in value):
        errors.append(f"{path} must be a non-empty list of strings")
        return []
    return [cast(str, item).strip() for item in value]


def _utc_timestamp(value: object, *, path: str, errors: list[str]) -> datetime | None:
    text = _string(value)
    if text is None or not text.endswith("Z"):
        errors.append(f"{path} must be a UTC timestamp ending in Z")
        return None
    try:
        parsed = datetime.fromisoformat(text.removesuffix("Z") + "+00:00")
    except ValueError:
        errors.append(f"{path} must be an ISO-8601 UTC timestamp")
        return None
    if parsed.tzinfo != UTC:
        errors.append(f"{path} must use UTC")
        return None
    return parsed


def _optional_utc_timestamp(value: object, *, path: str, errors: list[str]) -> datetime | None:
    if value is None:
        return None
    return _utc_timestamp(value, path=path, errors=errors)


def source_url_error(url: str) -> str | None:
    """Return why a governance metadata URL is outside the frozen source boundary."""

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


def _validate_source(
    source: Mapping[str, object], *, path: str, source_ids: set[str], errors: list[str]
) -> None:
    if set(source) != SOURCE_KEYS:
        errors.append(f"{path} must contain exactly {sorted(SOURCE_KEYS)}")
    source_id = _string(source.get("id"))
    url = _string(source.get("url"))
    if source_id is None or ID_PATTERN.fullmatch(source_id) is None or source_id in source_ids:
        errors.append(f"{path}.id must be unique and stable")
    else:
        source_ids.add(source_id)
    if _string(source.get("role")) is None:
        errors.append(f"{path}.role must be non-empty")
    if url is None:
        errors.append(f"{path}.url must be non-empty")
    else:
        url_error = source_url_error(url)
        if url_error is not None:
            errors.append(f"{path}.url {url_error}")


def _validate_candidate(
    candidate: Mapping[str, object],
    *,
    index: int,
    freeze_at: datetime | None,
    minimum_lead_days: int,
    audit_sla_hours: int,
    platform_ids: set[str],
    candidate_ids: set[str],
    errors: list[str],
) -> None:
    path = f"candidate_registry[{index}]"
    if set(candidate) != CANDIDATE_KEYS:
        errors.append(f"{path} must contain exactly {sorted(CANDIDATE_KEYS)}")
    candidate_id = _string(candidate.get("candidate_id"))
    if candidate_id is None or ID_PATTERN.fullmatch(candidate_id) is None or candidate_id in candidate_ids:
        errors.append(f"{path}.candidate_id must be unique and stable")
    else:
        candidate_ids.add(candidate_id)
    platform_id = _string(candidate.get("platform_id"))
    if platform_id not in platform_ids:
        errors.append(f"{path}.platform_id is unknown: {platform_id}")
    if _string(candidate.get("official_proposal_id")) is None:
        errors.append(f"{path}.official_proposal_id must be non-empty")
    published_at = _utc_timestamp(
        candidate.get("proposal_published_at"), path=f"{path}.proposal_published_at", errors=errors
    )
    final_at = _optional_utc_timestamp(
        candidate.get("final_package_at"), path=f"{path}.final_package_at", errors=errors
    )
    activation_at = _optional_utc_timestamp(
        candidate.get("activation_at"), path=f"{path}.activation_at", errors=errors
    )
    audit_at = _optional_utc_timestamp(
        candidate.get("audit_completed_at"), path=f"{path}.audit_completed_at", errors=errors
    )
    if freeze_at is not None and published_at is not None and published_at <= freeze_at:
        errors.append(f"{path}.proposal_published_at must be strictly after freeze.effective_at")
    if candidate.get("outcome_accessed") is not False:
        errors.append(f"{path}.outcome_accessed must be false before activation")

    criteria = _mapping(candidate.get("criteria"))
    if criteria is None or set(criteria) != REQUIRED_CRITERIA:
        errors.append(f"{path}.criteria must contain exactly {sorted(REQUIRED_CRITERIA)}")
        criteria = {}
    for criterion_id, value in criteria.items():
        if value is not None and not isinstance(value, bool):
            errors.append(f"{path}.criteria.{criterion_id} must be boolean or null")
    if (
        published_at is not None
        and freeze_at is not None
        and published_at > freeze_at
        and criteria.get("post_freeze_origin") is not True
    ):
        errors.append(f"{path}.criteria.post_freeze_origin contradicts the registry boundary")

    status = _string(candidate.get("status"))
    if status not in CANDIDATE_STATUSES:
        errors.append(f"{path}.status is invalid: {status}")
    complete_times = final_at is not None and activation_at is not None and audit_at is not None
    all_criteria_true = bool(criteria) and all(value is True for value in criteria.values())
    any_criterion_false = any(value is False for value in criteria.values())
    if status == "pending_audit":
        if audit_at is not None or all_criteria_true or any_criterion_false:
            errors.append(f"{path} pending_audit cannot contain a completed eligibility decision")
    elif status in {"audited_ineligible", "qualified", "selected"} and not complete_times:
        errors.append(f"{path} audited status requires final, activation, and audit timestamps")
    if status == "audited_ineligible" and not any_criterion_false:
        errors.append(f"{path} audited_ineligible requires at least one false criterion")
    if status in {"qualified", "selected"} and not all_criteria_true:
        errors.append(f"{path} {status} requires every criterion to be true")

    if final_at is not None and published_at is not None and final_at < published_at:
        errors.append(f"{path}.final_package_at cannot precede proposal publication")
    if final_at is not None and activation_at is not None:
        lead_passes = activation_at - final_at >= timedelta(days=minimum_lead_days)
        if criteria.get("minimum_lead_time") is not lead_passes:
            errors.append(f"{path}.criteria.minimum_lead_time contradicts the frozen lead-time rule")
    if final_at is not None and audit_at is not None:
        if audit_at < final_at:
            errors.append(f"{path}.audit_completed_at cannot precede the final package")
        if audit_at > final_at + timedelta(hours=audit_sla_hours):
            errors.append(f"{path}.audit_completed_at exceeds the frozen audit SLA")

    evidence_hash = _optional_string(candidate.get("evidence_hash"))
    if status == "pending_audit":
        if evidence_hash is not None:
            errors.append(f"{path}.evidence_hash must be null while pending")
    elif evidence_hash is None or EVIDENCE_SHA_PATTERN.fullmatch(evidence_hash) is None:
        errors.append(f"{path}.evidence_hash must be a 64-character lowercase SHA-256")
    exclusion_reason = _optional_string(candidate.get("exclusion_reason"))
    if status == "pending_audit" and exclusion_reason is not None:
        errors.append(f"{path}.exclusion_reason must be null while pending")
    if status == "audited_ineligible" and exclusion_reason is None:
        errors.append(f"{path}.exclusion_reason must explain ineligibility")
    if status in {"qualified", "selected"} and exclusion_reason is not None:
        errors.append(f"{path}.exclusion_reason must be null for eligible candidates")


def _candidate_rank(candidate: Mapping[str, object]) -> tuple[datetime, str]:
    final_text = candidate.get("final_package_at")
    if not isinstance(final_text, str) or not final_text.endswith("Z"):
        raise ValueError("candidate final-package timestamp is not rankable")
    final_at = datetime.fromisoformat(final_text.removesuffix("Z") + "+00:00")
    canonical_id = f"{candidate['platform_id']}:{candidate['official_proposal_id']}".lower()
    return final_at, hashlib.sha256(canonical_id.encode("utf-8")).hexdigest()


def first_qualifying_candidate(
    candidates: Sequence[Mapping[str, object]],
) -> Mapping[str, object] | None:
    """Return the frozen first qualifying candidate, without inspecting outcomes."""

    eligible: list[Mapping[str, object]] = []
    for candidate in candidates:
        criteria = candidate.get("criteria")
        if (
            candidate.get("status") not in {"qualified", "selected"}
            or not isinstance(criteria, Mapping)
            or not criteria
            or not all(value is True for value in criteria.values())
        ):
            continue
        try:
            _candidate_rank(candidate)
        except ValueError:
            continue
        eligible.append(candidate)
    if not eligible:
        return None
    return min(eligible, key=_candidate_rank)


def validate_selection_contract(contract: Mapping[str, object]) -> list[str]:
    """Return deterministic structural, timing, and outcome-blindness violations."""

    errors: list[str] = []
    unknown_top = sorted(set(contract) - TOP_LEVEL_KEYS)
    missing_top = sorted(TOP_LEVEL_KEYS - set(contract))
    if unknown_top:
        errors.append(f"unknown top-level keys: {unknown_top}")
    if missing_top:
        errors.append(f"missing top-level keys: {missing_top}")
    if contract.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION}")
    selection_id = _string(contract.get("selection_id"))
    if selection_id is None or ID_PATTERN.fullmatch(selection_id) is None:
        errors.append("selection_id must be a lowercase stable identifier")
    as_of = _string(contract.get("as_of"))
    if as_of is None or DATE_PATTERN.fullmatch(as_of) is None:
        errors.append("as_of must be an ISO date")
    if contract.get("stage") != STAGE:
        errors.append(f"stage must equal {STAGE}")
    status = _string(contract.get("status"))
    if status not in SELECTION_STATUSES:
        errors.append(f"status is invalid: {status}")

    boundary = _mapping(contract.get("access_boundary"))
    if boundary is None or set(boundary) != ACCESS_FLAGS:
        errors.append(f"access_boundary must contain exactly {sorted(ACCESS_FLAGS)}")
        boundary = {}
    for flag in ACCESS_FLAGS:
        if boundary.get(flag) is not False:
            errors.append(f"access_boundary.{flag} must be false")

    freeze = _mapping(contract.get("freeze"))
    freeze_at: datetime | None = None
    if freeze is None or set(freeze) != FREEZE_KEYS:
        errors.append(f"freeze must contain exactly {sorted(FREEZE_KEYS)}")
        freeze = {}
    else:
        freeze_at = _utc_timestamp(freeze.get("effective_at"), path="freeze.effective_at", errors=errors)
        parent_commit = _string(freeze.get("parent_commit"))
        if parent_commit is None or SHA_PATTERN.fullmatch(parent_commit) is None:
            errors.append("freeze.parent_commit must be a 40-character lowercase git SHA")
        if freeze.get("authority") != "commit_containing_this_contract":
            errors.append("freeze.authority must equal commit_containing_this_contract")
        for key in ("proposal_publication_rule", "outcome_blind_rule"):
            if _string(freeze.get(key)) is None:
                errors.append(f"freeze.{key} must be non-empty")

    universe = _mapping_list(contract.get("universe"))
    if not universe:
        errors.append("universe must be a non-empty list of mappings")
        universe = []
    platform_ids: set[str] = set()
    source_ids: set[str] = set()
    for index, platform in enumerate(universe):
        path = f"universe[{index}]"
        if set(platform) != PLATFORM_KEYS:
            errors.append(f"{path} must contain exactly {sorted(PLATFORM_KEYS)}")
        platform_id = _string(platform.get("platform_id"))
        if platform_id is None or platform_id in platform_ids:
            errors.append(f"{path}.platform_id must be unique")
        else:
            platform_ids.add(platform_id)
        for key in ("governance_authority", "independence_basis"):
            if _string(platform.get(key)) is None:
                errors.append(f"{path}.{key} must be non-empty")
        if platform.get("status") != "future_only":
            errors.append(f"{path}.status must equal future_only")
        sources = _mapping_list(platform.get("sources"))
        if not sources:
            errors.append(f"{path}.sources must be a non-empty list of mappings")
        else:
            for source_index, source in enumerate(sources):
                _validate_source(
                    source,
                    path=f"{path}.sources[{source_index}]",
                    source_ids=source_ids,
                    errors=errors,
                )
    if platform_ids != EXPECTED_PLATFORMS:
        errors.append(f"universe platform IDs must equal {sorted(EXPECTED_PLATFORMS)}")

    qualification = _mapping(contract.get("qualification"))
    minimum_lead_days = 28
    audit_sla_hours = 72
    if qualification is None or set(qualification) != QUALIFICATION_KEYS:
        errors.append(f"qualification must contain exactly {sorted(QUALIFICATION_KEYS)}")
        qualification = {}
    else:
        if qualification.get("all_required") is not True:
            errors.append("qualification.all_required must be true")
        if qualification.get("minimum_lead_days") != minimum_lead_days:
            errors.append("qualification.minimum_lead_days must equal 28")
        if qualification.get("audit_sla_hours") != audit_sla_hours:
            errors.append("qualification.audit_sla_hours must equal 72")
        criteria = _mapping(qualification.get("criteria"))
        if criteria is None or set(criteria) != REQUIRED_CRITERIA:
            errors.append(f"qualification.criteria must contain exactly {sorted(REQUIRED_CRITERIA)}")
        else:
            for criterion_id, rule in criteria.items():
                if _string(rule) is None:
                    errors.append(f"qualification.criteria.{criterion_id} must be non-empty")

    ordering = _mapping(contract.get("ordering"))
    if ordering is None or set(ordering) != ORDERING_KEYS:
        errors.append(f"ordering must contain exactly {sorted(ORDERING_KEYS)}")
    else:
        required_values: Mapping[str, object] = {
            "primary_key": "official_final_package_timestamp_utc",
            "secondary_key": "sha256_of_canonical_event_id",
            "canonical_event_id": "lower(platform_id + ':' + official_proposal_id)",
            "no_replacement": True,
        }
        for key, expected in required_values.items():
            if ordering.get(key) != expected:
                errors.append(f"ordering.{key} must equal {expected}")
        if _string(ordering.get("late_audit_policy")) is None:
            errors.append("ordering.late_audit_policy must be non-empty")

    candidates = _mapping_list(contract.get("candidate_registry"))
    if candidates is None:
        errors.append("candidate_registry must be a list of mappings")
        candidates = []
    candidate_ids: set[str] = set()
    for index, candidate in enumerate(candidates):
        _validate_candidate(
            candidate,
            index=index,
            freeze_at=freeze_at,
            minimum_lead_days=minimum_lead_days,
            audit_sla_hours=audit_sla_hours,
            platform_ids=platform_ids,
            candidate_ids=candidate_ids,
            errors=errors,
        )

    selection = _mapping(contract.get("selection"))
    if selection is None or set(selection) != SELECTION_KEYS:
        errors.append(f"selection must contain exactly {sorted(SELECTION_KEYS)}")
        selection = {}
    winner = first_qualifying_candidate(candidates)
    selected_event_id = _optional_string(selection.get("event_id"))
    selected_at = _optional_string(selection.get("selected_at"))
    selected_evidence = _optional_string(selection.get("evidence_hash"))
    if _string(selection.get("reason")) is None:
        errors.append("selection.reason must be non-empty")
    if winner is None:
        if status != "frozen_no_event_selected":
            errors.append("status must be frozen_no_event_selected when no candidate qualifies")
        if selected_event_id is not None or selected_at is not None or selected_evidence is not None:
            errors.append("selection identifiers and timestamps must be null when no event is selected")
        if any(candidate.get("status") == "selected" for candidate in candidates):
            errors.append("no candidate may be selected when no candidate qualifies")
    else:
        winner_id = cast(str, winner["candidate_id"])
        if status != "event_selected":
            errors.append("status must be event_selected when a candidate qualifies")
        if selected_event_id != winner_id:
            errors.append(f"selection.event_id must equal the first qualifying candidate: {winner_id}")
        selected_at_value = _utc_timestamp(
            selection.get("selected_at"), path="selection.selected_at", errors=errors
        )
        if selected_evidence != winner.get("evidence_hash"):
            errors.append("selection.evidence_hash must match the selected candidate")
        selected_candidates = [candidate for candidate in candidates if candidate.get("status") == "selected"]
        if len(selected_candidates) != 1 or selected_candidates[0].get("candidate_id") != winner_id:
            errors.append("exactly the first qualifying candidate must have selected status")
        winner_audit = _optional_utc_timestamp(
            winner.get("audit_completed_at"), path="selected_candidate.audit_completed_at", errors=errors
        )
        winner_activation = _optional_utc_timestamp(
            winner.get("activation_at"), path="selected_candidate.activation_at", errors=errors
        )
        if selected_at_value is not None and winner_audit is not None and selected_at_value < winner_audit:
            errors.append("selection.selected_at cannot precede the eligibility audit")
        if (
            selected_at_value is not None
            and winner_activation is not None
            and selected_at_value >= winner_activation
        ):
            errors.append("selection.selected_at must precede activation")
        winner_rank = _candidate_rank(winner)
        for candidate in candidates:
            if candidate.get("status") == "pending_audit" and candidate.get("final_package_at") is not None:
                try:
                    final_at = _candidate_rank(candidate)[0]
                except ValueError:
                    continue
                if final_at <= winner_rank[0]:
                    errors.append("an earlier final package remains pending audit; selection is premature")

    failure_policy = _mapping(contract.get("failure_policy"))
    if failure_policy is None or set(failure_policy) != FAILURE_POLICY_KEYS:
        errors.append(f"failure_policy must contain exactly {sorted(FAILURE_POLICY_KEYS)}")
    else:
        for key in FAILURE_POLICY_KEYS:
            if failure_policy.get(key) is not True:
                errors.append(f"failure_policy.{key} must be true")

    monitoring = _mapping(contract.get("monitoring"))
    if monitoring is None or set(monitoring) != MONITORING_KEYS:
        errors.append(f"monitoring must contain exactly {sorted(MONITORING_KEYS)}")
    else:
        if _string(monitoring.get("cadence")) is None:
            errors.append("monitoring.cadence must be non-empty")
        _string_list(
            monitoring.get("permitted_metadata"), path="monitoring.permitted_metadata", errors=errors
        )
        _string_list(
            monitoring.get("forbidden_before_activation"),
            path="monitoring.forbidden_before_activation",
            errors=errors,
        )
    _string_list(contract.get("outputs"), path="outputs", errors=errors)
    return sorted(errors)


def selection_summary(contract: Mapping[str, object]) -> dict[str, object]:
    """Summarize the frozen registry without reading event outcomes."""

    errors = validate_selection_contract(contract)
    if errors:
        raise ValueError("invalid prospective selection contract:\n- " + "\n- ".join(errors))
    candidates = cast(list[Mapping[str, object]], contract["candidate_registry"])
    counts = {candidate_status: 0 for candidate_status in sorted(CANDIDATE_STATUSES)}
    for candidate in candidates:
        counts[cast(str, candidate["status"])] += 1
    selection = cast(Mapping[str, object], contract["selection"])
    return {
        "selection_id": contract["selection_id"],
        "status": contract["status"],
        "freeze_effective_at": cast(Mapping[str, object], contract["freeze"])["effective_at"],
        "candidate_counts": counts,
        "selected_event_id": selection["event_id"],
        "outcome_blind": True,
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Validate and summarize a prospective event-selection contract."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    args = parser.parse_args(argv)
    contract = load_selection_contract(args.contract)
    errors = validate_selection_contract(contract)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(yaml.safe_dump({"summary": selection_summary(contract)}, sort_keys=False).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
