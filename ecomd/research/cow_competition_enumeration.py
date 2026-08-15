"""Outcome-blind enumeration of persisted CoW solver competitions."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

import yaml

SCHEMA_VERSION = "ecophys-cow-competition-head-enumeration/v1"
FROZEN_STAGE = "frozen_before_head_enumeration"
RESOLVED_STAGE = "head_enumerated_no_competition_bodies_opened"
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
SHA1_PATTERN = re.compile(r"[0-9a-f]{40}")
FORBIDDEN_LEDGER_FIELDS = frozenset(
    {
        "body",
        "content_length",
        "headers",
        "response_body",
        "response_headers",
        "response_sha256",
    }
)


def canonical_json_sha256(payload: object) -> str:
    """Hash a JSON-safe value with stable separators and key ordering."""

    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def derive_candidate_ids(
    anchor_id: int,
    *,
    first_offset_below_anchor: int,
    count: int,
    stride: int,
) -> tuple[int, ...]:
    """Derive the exact candidate-ID sequence without source access."""

    if anchor_id <= 0 or first_offset_below_anchor <= 0 or count <= 0 or stride <= 0:
        raise ValueError("anchor, offset, count and stride must be positive")
    ids = tuple(anchor_id - first_offset_below_anchor - index * stride for index in range(count))
    if ids[-1] <= 0:
        raise ValueError("candidate rule produced a nonpositive ID")
    if len(set(ids)) != count:
        raise ValueError("candidate rule produced duplicate IDs")
    return ids


def load_contract(path: Path) -> dict[str, object]:
    """Load one YAML enumeration contract."""

    payload: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("enumeration contract root must be a mapping")
    return cast(dict[str, object], payload)


def contract_sha256(path: Path) -> str:
    """Hash the exact contract bytes."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mapping(value: object, *, path: str, errors: list[str]) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        errors.append(f"{path} must be a mapping")
        return None
    return cast(Mapping[str, object], value)


def _positive_int(value: object, *, path: str, errors: list[str]) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        errors.append(f"{path} must be a positive integer")
        return None
    return value


def _strict_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_frozen_contract(contract: Mapping[str, object]) -> tuple[str, ...]:
    """Validate the pre-access HEAD enumeration contract."""

    errors: list[str] = []
    if contract.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if contract.get("stage") != FROZEN_STAGE:
        errors.append(f"stage must be {FROZEN_STAGE}")
    if contract.get("scientific_role") != "development_only_no_confirmation_claim":
        errors.append("scientific_role must remain development_only_no_confirmation_claim")

    source = _mapping(contract.get("source"), path="source", errors=errors)
    if source is not None:
        if source.get("network") != "mainnet":
            errors.append("source.network must remain mainnet")
        if source.get("request_method") != "HEAD":
            errors.append("source.request_method must remain HEAD")
        retained = source.get("retained_response_fields")
        if retained != ["http_status"]:
            errors.append("source.retained_response_fields must be exactly ['http_status']")
        if source.get("discard_all_response_headers") is not True:
            errors.append("source.discard_all_response_headers must be true")
        for key in ("openapi_sha256", "deployed_openapi_sha256"):
            value = source.get(key)
            if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
                errors.append(f"source.{key} must be a SHA-256 digest")
        commit = source.get("deployed_git_commit")
        if not isinstance(commit, str) or SHA1_PATTERN.fullmatch(commit) is None:
            errors.append("source.deployed_git_commit must be a full Git SHA")
        rate = source.get("maximum_requests_per_second")
        if isinstance(rate, bool) or not isinstance(rate, (int, float)) or rate <= 0:
            errors.append("source.maximum_requests_per_second must be positive")
        retries = source.get("maximum_transport_retries")
        if isinstance(retries, bool) or not isinstance(retries, int) or retries < 0:
            errors.append("source.maximum_transport_retries must be a nonnegative integer")
        if not isinstance(source.get("base_url"), str) or not cast(str, source["base_url"]).startswith(
            "https://"
        ):
            errors.append("source.base_url must be HTTPS")
        if source.get("endpoint_template") != "/api/v2/solver_competition/{auction_id}":
            errors.append("source.endpoint_template must remain the audited competition route")

    anchor = _mapping(contract.get("anchor"), path="anchor", errors=errors)
    anchor_id = None
    if anchor is not None:
        anchor_id = _positive_int(
            anchor.get("resolved_anchor_id"), path="anchor.resolved_anchor_id", errors=errors
        )
        digest = anchor.get("resolved_manifest_sha256")
        if not isinstance(digest, str) or SHA256_PATTERN.fullmatch(digest) is None:
            errors.append("anchor.resolved_manifest_sha256 must be a SHA-256 digest")

    frame_count: int | None = None
    frame = _mapping(contract.get("candidate_frame"), path="candidate_frame", errors=errors)
    if frame is not None:
        offset = _positive_int(
            frame.get("first_offset_below_anchor"),
            path="candidate_frame.first_offset_below_anchor",
            errors=errors,
        )
        count = _positive_int(frame.get("count"), path="candidate_frame.count", errors=errors)
        frame_count = count
        stride = _positive_int(frame.get("stride"), path="candidate_frame.stride", errors=errors)
        if anchor_id is not None and offset is not None and count is not None and stride is not None:
            ids = derive_candidate_ids(
                anchor_id,
                first_offset_below_anchor=offset,
                count=count,
                stride=stride,
            )
            if frame.get("candidate_id_maximum") != max(ids):
                errors.append("candidate_frame.candidate_id_maximum does not match the rule")
            if frame.get("candidate_id_minimum") != min(ids):
                errors.append("candidate_frame.candidate_id_minimum does not match the rule")
            if frame.get("candidate_ids_sha256") != canonical_json_sha256(ids):
                errors.append("candidate_frame.candidate_ids_sha256 does not match the rule")
            previous_minimum = frame.get("previous_expansion_id_minimum")
            if isinstance(previous_minimum, bool) or not isinstance(previous_minimum, int):
                errors.append("candidate_frame.previous_expansion_id_minimum must be an integer")
            elif max(ids) >= previous_minimum:
                errors.append("candidate frame must be strictly below the previous expansion frame")
        if frame.get("no_replacement") is not True:
            errors.append("candidate_frame.no_replacement must be true")

    access = _mapping(contract.get("access_boundary"), path="access_boundary", errors=errors)
    if access is not None:
        required_true = (
            "head_only_before_resolution_commit",
            "response_body_bytes_read_must_be_zero",
            "resolved_manifest_commit_required_before_get",
            "retain_every_request_outcome",
        )
        for key in required_true:
            if access.get(key) is not True:
                errors.append(f"access_boundary.{key} must be true")
        if access.get("competition_bodies_opened") is not False:
            errors.append("access_boundary.competition_bodies_opened must be false")

    gates = _mapping(contract.get("gates"), path="gates", errors=errors)
    if gates is not None:
        minimum_eligible = _positive_int(
            gates.get("minimum_eligible_count"),
            path="gates.minimum_eligible_count",
            errors=errors,
        )
        if frame_count is not None and minimum_eligible is not None and minimum_eligible > frame_count:
            errors.append("gates.minimum_eligible_count cannot exceed candidate count")
        if gates.get("eligible_http_status") != 200:
            errors.append("gates.eligible_http_status must be 200")
        if gates.get("allowed_terminal_http_statuses") != [200, 404]:
            errors.append("gates.allowed_terminal_http_statuses must be exactly [200, 404]")
        if gates.get("exact_candidate_order_required") is not True:
            errors.append("gates.exact_candidate_order_required must be true")
        if frame_count is not None and gates.get("exact_request_count_required") != frame_count:
            errors.append("gates.exact_request_count_required must equal candidate count")
        if gates.get("zero_body_bytes_required") is not True:
            errors.append("gates.zero_body_bytes_required must be true")
        if gates.get("no_headers_retained_required") is not True:
            errors.append("gates.no_headers_retained_required must be true")
        if gates.get("no_transport_or_unexpected_status_allowed") is not True:
            errors.append("gates.no_transport_or_unexpected_status_allowed must be true")

    if contract.get("enumeration_result") is not None:
        errors.append("enumeration_result must be null before HEAD access")
    return tuple(errors)


def summarize_head_enumeration(
    entries: Sequence[Mapping[str, object]],
    *,
    expected_ids: Sequence[int],
    minimum_eligible_count: int,
    ledger_sha256: str,
) -> dict[str, object]:
    """Summarize a status-only HEAD ledger without opening result fields."""

    requested_ids = [entry.get("auction_id") for entry in entries]
    exact_order = all(_strict_int(value) for value in requested_ids) and requested_ids == list(expected_ids)
    request_indexes = [entry.get("request_index") for entry in entries]
    exact_indexes = all(_strict_int(value) for value in request_indexes) and request_indexes == list(
        range(len(expected_ids))
    )
    head_only = all(entry.get("request_method") == "HEAD" for entry in entries)
    zero_body = all(entry.get("response_body_bytes_read") == 0 for entry in entries)
    forbidden_fields = sorted(
        {field for entry in entries for field in FORBIDDEN_LEDGER_FIELDS.intersection(entry)}
    )
    statuses = [entry.get("http_status") for entry in entries]
    terminal_statuses = all(
        isinstance(status, int) and not isinstance(status, bool) and status in {200, 404}
        for status in statuses
    )
    eligible_ids = [
        cast(int, entry["auction_id"])
        for entry in entries
        if entry.get("http_status") == 200 and _strict_int(entry.get("auction_id"))
    ]
    status_counts = Counter(str(status) if status is not None else "transport_error" for status in statuses)
    gates = {
        "complete_candidate_count": len(entries) == len(expected_ids),
        "exact_candidate_order": exact_order,
        "exact_request_indexes": exact_indexes,
        "head_only": head_only,
        "zero_response_body_bytes_read": zero_body,
        "no_forbidden_response_fields_retained": not forbidden_fields,
        "terminal_statuses_only": terminal_statuses,
        "minimum_eligible_count": len(eligible_ids) >= minimum_eligible_count,
    }
    passed = all(gates.values())
    return {
        "schema": SCHEMA_VERSION,
        "scientific_role": "development_only_no_confirmation_claim",
        "decision": (
            "PASS_HEAD_ENUMERATION_FREEZE_EXACT_GET_SET"
            if passed
            else "FAIL_HEAD_ENUMERATION_DO_NOT_OPEN_COMPETITION_BODIES"
        ),
        "pass": passed,
        "candidate_count": len(expected_ids),
        "ledger_count": len(entries),
        "ledger_sha256": ledger_sha256,
        "candidate_ids_sha256": canonical_json_sha256(expected_ids),
        "eligible_count": len(eligible_ids),
        "eligible_auction_ids": eligible_ids,
        "eligible_auction_ids_sha256": canonical_json_sha256(eligible_ids),
        "http_status_counts": dict(sorted(status_counts.items())),
        "forbidden_retained_fields": forbidden_fields,
        "gates": gates,
    }


def materialize_resolved_contract(
    frozen: Mapping[str, object],
    *,
    summary: Mapping[str, object],
    collection_git_commit: str,
    collected_at_utc: str,
) -> dict[str, object]:
    """Create the exact GET-set contract after a passing HEAD-only enumeration."""

    frozen_errors = validate_frozen_contract(frozen)
    if frozen_errors:
        raise ValueError("invalid frozen contract: " + "; ".join(frozen_errors))
    if summary.get("pass") is not True:
        raise ValueError("cannot resolve a failed HEAD enumeration")
    eligible = summary.get("eligible_auction_ids")
    if not isinstance(eligible, list) or any(
        isinstance(value, bool) or not isinstance(value, int) for value in eligible
    ):
        raise ValueError("summary eligible_auction_ids must be an integer list")
    if SHA1_PATTERN.fullmatch(collection_git_commit) is None:
        raise ValueError("collection_git_commit must be a full Git SHA")

    resolved = copy.deepcopy(dict(frozen))
    resolved["stage"] = RESOLVED_STAGE
    resolved["enumeration_result"] = {
        "decision": summary["decision"],
        "collected_at_utc": collected_at_utc,
        "collection_git_commit": collection_git_commit,
        "ledger_sha256": summary["ledger_sha256"],
        "candidate_count": summary["candidate_count"],
        "http_status_counts": summary["http_status_counts"],
        "eligible_count": summary["eligible_count"],
        "eligible_auction_ids": eligible,
        "eligible_auction_ids_sha256": summary["eligible_auction_ids_sha256"],
    }
    return resolved
