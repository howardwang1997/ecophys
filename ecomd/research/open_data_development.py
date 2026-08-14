"""Outcome-blind contracts and common records for open-data development."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path, PurePosixPath
from typing import Literal, cast
from urllib.parse import urlparse

import yaml

SCHEMA_VERSION = "ecophys-open-data-development-sample/v1"
UNRESOLVED_STAGE = "rules_frozen_no_historical_rows_opened"
RESOLVED_STAGE = "cow_anchor_resolved_no_sample_rows_opened"
SHA1_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

ROOT_KEYS = frozenset(
    {
        "schema_version",
        "sample_id",
        "frozen_at",
        "parent_commit",
        "stage",
        "scientific_role",
        "access_boundary",
        "synthetic_calibration",
        "cow",
        "aemo",
        "gates",
        "outputs",
    }
)
ACCESS_KEYS = frozenset(
    {
        "paid_data_used",
        "target_event_rows_opened",
        "target_event_outcomes_opened",
        "anchor_metadata_opened",
        "historical_sample_rows_opened",
        "prospective_registry_changed",
        "forbidden_before_separate_activation",
    }
)
REQUIRED_FORBIDDEN = frozenset(
    {
        "gc0166_mdo_mdb_rows",
        "gc0166_controlled_rollout_rows",
        "post_cutoff_governance_event_responses",
        "experiment_156",
    }
)
SAMPLE_KEYS = frozenset(
    {
        "count",
        "first_offset_below_anchor",
        "stride",
        "auction_ids",
        "auction_ids_sha256",
    }
)
EXPECTED_AEMO_DATES = {
    "legacy-2021-03": ("2021-03", "2021-03-02", "legacy_public_dvd"),
    "current-2025-01": ("2025-01", "2025-01-07", "public_archive_hash_delimited"),
}
EXPECTED_INITIAL_TABLES = (
    "BIDDAYOFFER_D",
    "BIDPEROFFER_D",
    "DISPATCHOFFERTRK",
    "DISPATCHLOAD",
    "DUDETAILSUMMARY",
)

ActionStatus = Literal["submitted", "failed", "missing"]


@dataclass(frozen=True)
class CommonObservation:
    """Minimal clock, identity and action-status record shared across domains."""

    system_id: str
    event_id: str
    participant_id: str
    forecast_frozen_at: datetime
    feature_as_of: datetime
    action_at: datetime
    outcome_at: datetime
    identity_valid_from: datetime
    identity_valid_to: datetime | None
    action_status: ActionStatus
    action_value: float | None
    failure_code: str | None


def load_development_contract(path: str | Path) -> dict[str, object]:
    """Load a development contract at an object-typed boundary."""

    payload: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("development contract root must be a mapping")
    return cast(dict[str, object], payload)


def contract_sha256(path: str | Path) -> str:
    """Hash the exact serialized contract bytes."""

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _mapping(value: object, *, path: str, errors: list[str]) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        errors.append(f"{path} must be a mapping")
        return None
    return cast(Mapping[str, object], value)


def _mapping_sequence(value: object, *, path: str, errors: list[str]) -> list[Mapping[str, object]]:
    if not isinstance(value, list):
        errors.append(f"{path} must be a list")
        return []
    result: list[Mapping[str, object]] = []
    for index, item in enumerate(value):
        mapping = _mapping(item, path=f"{path}[{index}]", errors=errors)
        if mapping is not None:
            result.append(mapping)
    return result


def _text(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _positive_int(value: object, *, path: str, errors: list[str]) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        errors.append(f"{path} must be a positive integer")
        return None
    return value


def _finite_float(value: object, *, path: str, errors: list[str]) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{path} must be numeric")
        return None
    result = float(value)
    if not math.isfinite(result):
        errors.append(f"{path} must be finite")
        return None
    return result


def _utc_timestamp(value: object, *, path: str, errors: list[str]) -> datetime | None:
    text = _text(value)
    if text is None or not text.endswith("Z"):
        errors.append(f"{path} must be an ISO-8601 UTC timestamp ending in Z")
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


def _https_url(value: object, *, path: str, errors: list[str]) -> None:
    text = _text(value)
    if text is None:
        errors.append(f"{path} must be non-empty")
        return
    parsed = urlparse(text)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        errors.append(f"{path} must be an absolute credential-free HTTPS URL")


def _relative_path(value: object, *, path: str, errors: list[str]) -> None:
    text = _text(value)
    if text is None:
        errors.append(f"{path} must be non-empty")
        return
    candidate = PurePosixPath(text)
    if candidate.is_absolute() or ".." in candidate.parts:
        errors.append(f"{path} must be a repository-relative path without '..'")


def auction_ids_sha256(auction_ids: Sequence[int]) -> str:
    """Hash a canonical exact auction-ID list."""

    payload = json.dumps(list(auction_ids), separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def derive_cow_auction_ids(
    anchor_id: int,
    *,
    count: int,
    first_offset_below_anchor: int,
    stride: int,
) -> tuple[int, ...]:
    """Derive the exact outcome-blind CoW sample from its frozen arithmetic rule."""

    if anchor_id <= 0 or count <= 0 or first_offset_below_anchor <= 0 or stride <= 0:
        raise ValueError("anchor, count, offset and stride must be positive")
    result = tuple(anchor_id - first_offset_below_anchor - index * stride for index in range(count))
    if result[-1] <= 0:
        raise ValueError("frozen sampling rule produced a nonpositive auction ID")
    if len(set(result)) != count:
        raise ValueError("frozen sampling rule produced duplicate auction IDs")
    return result


def _validate_sample(
    sample: Mapping[str, object],
    *,
    path: str,
    anchor_id: int | None,
    resolved: bool,
    errors: list[str],
) -> tuple[int, ...]:
    if set(sample) != SAMPLE_KEYS:
        errors.append(f"{path} must contain exactly {sorted(SAMPLE_KEYS)}")
    count = _positive_int(sample.get("count"), path=f"{path}.count", errors=errors)
    offset = _positive_int(
        sample.get("first_offset_below_anchor"),
        path=f"{path}.first_offset_below_anchor",
        errors=errors,
    )
    stride = _positive_int(sample.get("stride"), path=f"{path}.stride", errors=errors)
    ids_value = sample.get("auction_ids")
    digest = sample.get("auction_ids_sha256")
    if not resolved:
        if ids_value is not None or digest is not None:
            errors.append(f"{path} IDs and hash must be null before anchor resolution")
        return ()
    if anchor_id is None or count is None or offset is None or stride is None:
        return ()
    expected = derive_cow_auction_ids(
        anchor_id,
        count=count,
        first_offset_below_anchor=offset,
        stride=stride,
    )
    if not isinstance(ids_value, list) or any(
        isinstance(item, bool) or not isinstance(item, int) for item in ids_value
    ):
        errors.append(f"{path}.auction_ids must be an integer list after resolution")
        return ()
    actual = tuple(cast(list[int], ids_value))
    if actual != expected:
        errors.append(f"{path}.auction_ids do not match the frozen arithmetic rule")
    if not isinstance(digest, str) or SHA256_PATTERN.fullmatch(digest) is None:
        errors.append(f"{path}.auction_ids_sha256 must be a SHA-256 digest after resolution")
    elif digest != auction_ids_sha256(actual):
        errors.append(f"{path}.auction_ids_sha256 does not match the exact ID list")
    return actual


def validate_development_contract(contract: Mapping[str, object]) -> tuple[str, ...]:
    """Return every contract violation without opening an external source row."""

    errors: list[str] = []
    if set(contract) != ROOT_KEYS:
        errors.append(f"root must contain exactly {sorted(ROOT_KEYS)}")
    if contract.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if contract.get("scientific_role") != "development_only_no_confirmation_claim":
        errors.append("scientific_role must remain development_only_no_confirmation_claim")
    if _text(contract.get("sample_id")) is None:
        errors.append("sample_id must be non-empty")
    frozen_at = _utc_timestamp(contract.get("frozen_at"), path="frozen_at", errors=errors)
    parent = _text(contract.get("parent_commit"))
    if parent is None or SHA1_PATTERN.fullmatch(parent) is None:
        errors.append("parent_commit must be a full lowercase Git SHA")
    stage = contract.get("stage")
    if stage not in (UNRESOLVED_STAGE, RESOLVED_STAGE):
        errors.append("stage is unsupported")
    resolved = stage == RESOLVED_STAGE

    access = _mapping(contract.get("access_boundary"), path="access_boundary", errors=errors)
    if access is not None:
        if set(access) != ACCESS_KEYS:
            errors.append(f"access_boundary must contain exactly {sorted(ACCESS_KEYS)}")
        always_false = (
            "paid_data_used",
            "target_event_rows_opened",
            "target_event_outcomes_opened",
            "historical_sample_rows_opened",
            "prospective_registry_changed",
        )
        for key in always_false:
            if access.get(key) is not False:
                errors.append(f"access_boundary.{key} must be false")
        if access.get("anchor_metadata_opened") is not resolved:
            errors.append("access_boundary.anchor_metadata_opened must match resolution stage")
        forbidden = access.get("forbidden_before_separate_activation")
        if (
            not isinstance(forbidden, list)
            or any(not isinstance(item, str) for item in forbidden)
            or frozenset(cast(list[str], forbidden)) != REQUIRED_FORBIDDEN
        ):
            errors.append("access_boundary.forbidden_before_separate_activation changed")

    synthetic = _mapping(
        contract.get("synthetic_calibration"), path="synthetic_calibration", errors=errors
    )
    if synthetic is not None:
        for key in (
            "root_seed",
            "replicates",
            "independent_blocks",
            "response_dimension",
            "ensemble_size",
            "permutation_draws",
            "clock_shift_blocks",
            "structural_cases_per_replicate",
        ):
            _positive_int(synthetic.get(key), path=f"synthetic_calibration.{key}", errors=errors)
        for key in (
            "alpha",
            "null_symmetric_bias",
            "effect_scale",
            "forecast_standard_deviation",
            "outcome_standard_deviation",
        ):
            value = _finite_float(
                synthetic.get(key), path=f"synthetic_calibration.{key}", errors=errors
            )
            if value is not None and value <= 0.0:
                errors.append(f"synthetic_calibration.{key} must be positive")

    cow = _mapping(contract.get("cow"), path="cow", errors=errors)
    if cow is not None:
        if cow.get("network") != "mainnet":
            errors.append("cow.network must remain mainnet")
        _https_url(cow.get("base_url"), path="cow.base_url", errors=errors)
        _https_url(cow.get("openapi_url"), path="cow.openapi_url", errors=errors)
        anchor = _mapping(cow.get("anchor"), path="cow.anchor", errors=errors)
        anchor_id: int | None = None
        if anchor is not None:
            resolved_id = anchor.get("resolved_anchor_id")
            resolved_at = anchor.get("resolved_at")
            if resolved:
                anchor_id = _positive_int(
                    resolved_id, path="cow.anchor.resolved_anchor_id", errors=errors
                )
                timestamp = _utc_timestamp(
                    resolved_at, path="cow.anchor.resolved_at", errors=errors
                )
                if timestamp is not None and frozen_at is not None and timestamp <= frozen_at:
                    errors.append("cow.anchor.resolved_at must be after frozen_at")
            elif resolved_id is not None or resolved_at is not None:
                errors.append("cow anchor resolution fields must be null before resolution")
        initial = _mapping(cow.get("initial_sample"), path="cow.initial_sample", errors=errors)
        expansion = _mapping(
            cow.get("expansion_sample"), path="cow.expansion_sample", errors=errors
        )
        initial_ids: tuple[int, ...] = ()
        expansion_ids: tuple[int, ...] = ()
        if initial is not None:
            initial_ids = _validate_sample(
                initial,
                path="cow.initial_sample",
                anchor_id=anchor_id,
                resolved=resolved,
                errors=errors,
            )
        if expansion is not None:
            expansion_ids = _validate_sample(
                expansion,
                path="cow.expansion_sample",
                anchor_id=anchor_id,
                resolved=resolved,
                errors=errors,
            )
        if resolved and not set(initial_ids).issubset(expansion_ids):
            errors.append("cow initial auction IDs must be an exact subset of expansion IDs")
        if cow.get("no_replacement_for_missing_or_failed_requests") is not True:
            errors.append("cow missing or failed requests cannot be replaced")
        if cow.get("initial_is_subset_of_expansion") is not True:
            errors.append("cow.initial_is_subset_of_expansion must be true")
        _utc_timestamp(cow.get("cutoff_utc"), path="cow.cutoff_utc", errors=errors)

    aemo = _mapping(contract.get("aemo"), path="aemo", errors=errors)
    if aemo is not None:
        _https_url(aemo.get("archive_root"), path="aemo.archive_root", errors=errors)
        if aemo.get("date_selection_rule") != (
            "first_Gregorian_Tuesday_no_holiday_adjustment_no_replacement"
        ):
            errors.append("aemo.date_selection_rule changed")
        samples = _mapping_sequence(aemo.get("samples"), path="aemo.samples", errors=errors)
        seen_labels: set[str] = set()
        for index, sample in enumerate(samples):
            label = _text(sample.get("sample_label"))
            month = _text(sample.get("archive_month"))
            market_date = _text(sample.get("market_date"))
            regime = _text(sample.get("naming_regime"))
            if label is None or label in seen_labels:
                errors.append(f"aemo.samples[{index}].sample_label must be unique")
                continue
            seen_labels.add(label)
            if EXPECTED_AEMO_DATES.get(label) != (month, market_date, regime):
                errors.append(f"aemo.samples[{index}] differs from the frozen date tuple")
            if market_date is not None:
                try:
                    parsed_date = date.fromisoformat(market_date)
                except ValueError:
                    errors.append(f"aemo.samples[{index}].market_date is invalid")
                else:
                    if parsed_date.weekday() != 1 or parsed_date.day > 7:
                        errors.append(f"aemo.samples[{index}] is not the first Gregorian Tuesday")
        if set(seen_labels) != set(EXPECTED_AEMO_DATES):
            errors.append("aemo.samples must contain exactly the two frozen sample labels")
        initial_tables = aemo.get("initial_tables")
        if not isinstance(initial_tables, list) or tuple(initial_tables) != EXPECTED_INITIAL_TABLES:
            errors.append("aemo.initial_tables differs from the frozen ordered table set")
        if aemo.get("no_replacement_for_empty_or_incomplete_dates") is not True:
            errors.append("aemo empty or incomplete dates cannot be replaced")

    gates = _mapping(contract.get("gates"), path="gates", errors=errors)
    if gates is not None:
        required_true = (
            "contract_validation_required_before_network_access",
            "contract_commit_required_before_network_access",
            "cow_anchor_commit_required_before_competition_sample_access",
            "aemo_header_contract_required_before_row_join",
            "scale_only_after_initial_gates_pass",
        )
        for key in required_true:
            if gates.get(key) is not True:
                errors.append(f"gates.{key} must be true")
        if gates.get("gpu_allowed_before_initial_data_gates") is not False:
            errors.append("gates.gpu_allowed_before_initial_data_gates must be false")

    outputs = _mapping(contract.get("outputs"), path="outputs", errors=errors)
    if outputs is not None:
        for key, output_value in outputs.items():
            _relative_path(output_value, path=f"outputs.{key}", errors=errors)
    return tuple(errors)


def resolve_cow_anchor(
    contract: Mapping[str, object],
    *,
    anchor_payload: Mapping[str, object],
    resolved_at: str,
) -> dict[str, object]:
    """Resolve only the permitted CoW anchor field and materialize exact ID lists."""

    errors = validate_development_contract(contract)
    if errors:
        raise ValueError("cannot resolve invalid contract: " + "; ".join(errors))
    if contract.get("stage") != UNRESOLVED_STAGE:
        raise ValueError("contract is not at the unresolved anchor stage")
    anchor_value = anchor_payload.get("auctionId")
    if isinstance(anchor_value, bool) or not isinstance(anchor_value, int) or anchor_value <= 0:
        raise ValueError("anchor payload auctionId must be a positive integer")
    timestamp_errors: list[str] = []
    _utc_timestamp(resolved_at, path="resolved_at", errors=timestamp_errors)
    if timestamp_errors:
        raise ValueError(timestamp_errors[0])

    resolved = copy.deepcopy(dict(contract))
    resolved["stage"] = RESOLVED_STAGE
    access = cast(dict[str, object], resolved["access_boundary"])
    access["anchor_metadata_opened"] = True
    cow = cast(dict[str, object], resolved["cow"])
    anchor = cast(dict[str, object], cow["anchor"])
    anchor["resolved_anchor_id"] = anchor_value
    anchor["resolved_at"] = resolved_at
    for key in ("initial_sample", "expansion_sample"):
        sample = cast(dict[str, object], cow[key])
        ids = derive_cow_auction_ids(
            anchor_value,
            count=cast(int, sample["count"]),
            first_offset_below_anchor=cast(int, sample["first_offset_below_anchor"]),
            stride=cast(int, sample["stride"]),
        )
        sample["auction_ids"] = list(ids)
        sample["auction_ids_sha256"] = auction_ids_sha256(ids)
    resolved_errors = validate_development_contract(resolved)
    if resolved_errors:
        raise AssertionError("resolved contract is invalid: " + "; ".join(resolved_errors))
    return resolved


def observation_violations(observation: CommonObservation) -> tuple[str, ...]:
    """Audit causality, effective-dated identity and explicit action status."""

    errors: list[str] = []
    timestamps = (
        observation.forecast_frozen_at,
        observation.feature_as_of,
        observation.action_at,
        observation.outcome_at,
        observation.identity_valid_from,
    )
    if any(value.tzinfo is None or value.utcoffset() is None for value in timestamps):
        errors.append("all required timestamps must be timezone-aware")
        return tuple(errors)
    if observation.identity_valid_to is not None and (
        observation.identity_valid_to.tzinfo is None
        or observation.identity_valid_to.utcoffset() is None
    ):
        errors.append("identity_valid_to must be timezone-aware")
        return tuple(errors)
    if observation.feature_as_of > observation.forecast_frozen_at:
        errors.append("feature timestamp exceeds forecast freeze")
    if observation.forecast_frozen_at > observation.action_at:
        errors.append("forecast freeze occurs after action")
    if observation.action_at > observation.outcome_at:
        errors.append("action occurs after outcome")
    if observation.action_at < observation.identity_valid_from or (
        observation.identity_valid_to is not None
        and observation.action_at >= observation.identity_valid_to
    ):
        errors.append("participant identity is not effective at action time")
    if observation.action_status == "submitted":
        if observation.action_value is None or not math.isfinite(observation.action_value):
            errors.append("submitted action requires a finite value")
        if observation.failure_code is not None:
            errors.append("submitted action cannot carry a failure code")
    elif observation.action_status == "failed":
        if not observation.failure_code:
            errors.append("failed action requires a failure code")
    elif observation.action_status == "missing":
        if observation.action_value is not None:
            errors.append("missing action cannot carry a value")
        if observation.failure_code != "missing":
            errors.append("missing action requires the canonical missing code")
    else:
        errors.append("unsupported action status")
    return tuple(errors)
