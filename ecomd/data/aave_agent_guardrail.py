"""Pure decoding and support-gate logic for Aave automated-agent actions."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from statistics import median
from typing import Any

from ecomd.data.aave_qualification import normalize_address

EventPosition = tuple[int, int, int]


def normalize_topic(value: str) -> str:
    """Normalize and validate a 32-byte EVM log topic."""
    normalized = value.lower()
    if re.fullmatch(r"0x[0-9a-f]{64}", normalized) is None:
        raise ValueError(f"invalid EVM log topic: {value}")
    return normalized


def normalize_hex_data(value: str) -> str:
    """Normalize and validate an even-length EVM byte string."""
    normalized = value.lower()
    if re.fullmatch(r"0x(?:[0-9a-f]{2})*", normalized) is None:
        raise ValueError("invalid EVM byte string")
    return normalized


def uint_from_topic(value: str) -> int:
    """Decode an indexed unsigned integer."""
    return int(normalize_topic(value), 16)


def bool_from_topic(value: str) -> bool:
    """Decode an indexed ABI boolean with canonical-value validation."""
    decoded = uint_from_topic(value)
    if decoded not in {0, 1}:
        raise ValueError(f"indexed bool is not canonical: {decoded}")
    return bool(decoded)


def address_from_topic(value: str) -> str:
    """Decode an indexed EVM address and reject non-zero left padding."""
    topic = normalize_topic(value)
    if int(topic[2:26], 16) != 0:
        raise ValueError("indexed address has non-zero ABI padding")
    return normalize_address("0x" + topic[-40:])


def _abi_blob(data: str) -> bytes:
    return bytes.fromhex(normalize_hex_data(data)[2:])


def _word(blob: bytes, index: int) -> bytes:
    start = index * 32
    end = start + 32
    if index < 0 or end > len(blob):
        raise ValueError(f"ABI word {index} is out of bounds")
    return blob[start:end]


def _uint_word(blob: bytes, index: int) -> int:
    return int.from_bytes(_word(blob, index), "big")


def _bool_word(blob: bytes, index: int) -> bool:
    value = _uint_word(blob, index)
    if value not in {0, 1}:
        raise ValueError(f"ABI bool is not canonical: {value}")
    return bool(value)


def _dynamic_bytes(blob: bytes, head_index: int, head_words: int) -> bytes:
    offset = _uint_word(blob, head_index)
    if offset % 32 != 0 or offset < head_words * 32 or offset + 32 > len(blob):
        raise ValueError(f"invalid ABI dynamic offset: {offset}")
    length = int.from_bytes(blob[offset : offset + 32], "big")
    start = offset + 32
    end = start + length
    padded_end = start + ((length + 31) // 32) * 32
    if end > len(blob) or padded_end > len(blob):
        raise ValueError("ABI dynamic value is truncated")
    if any(blob[end:padded_end]):
        raise ValueError("ABI dynamic value has non-zero padding")
    return blob[start:end]


def decode_parameter_updated_data(data: str) -> dict[str, Any]:
    """Decode non-indexed fields of RiskOracle.ParameterUpdated."""
    blob = _abi_blob(data)
    if len(blob) < 5 * 32 or len(blob) % 32 != 0:
        raise ValueError("ParameterUpdated data has an invalid ABI length")
    try:
        reference_id = _dynamic_bytes(blob, 0, 5).decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("ParameterUpdated referenceId is not UTF-8") from error
    return {
        "reference_id": reference_id,
        "new_value": "0x" + _dynamic_bytes(blob, 1, 5).hex(),
        "previous_value": "0x" + _dynamic_bytes(blob, 2, 5).hex(),
        "oracle_timestamp": _uint_word(blob, 3),
        "additional_data": "0x" + _dynamic_bytes(blob, 4, 5).hex(),
    }


def decode_update_injected_data(data: str) -> dict[str, Any]:
    """Decode non-indexed fields of AgentHub.UpdateInjected."""
    blob = _abi_blob(data)
    if len(blob) < 2 * 32 or len(blob) % 32 != 0:
        raise ValueError("UpdateInjected data has an invalid ABI length")
    return {
        "update_id": _uint_word(blob, 0),
        "new_value": "0x" + _dynamic_bytes(blob, 1, 2).hex(),
    }


def _range_config(blob: bytes, start_word: int) -> dict[str, Any]:
    max_increase = _uint_word(blob, start_word)
    max_decrease = _uint_word(blob, start_word + 1)
    if max_increase >= 2**120 or max_decrease >= 2**120:
        raise ValueError("range configuration exceeds uint120")
    return {
        "max_increase": max_increase,
        "max_decrease": max_decrease,
        "is_increase_relative": _bool_word(blob, start_word + 2),
        "is_decrease_relative": _bool_word(blob, start_word + 3),
    }


def decode_default_range_config_data(data: str) -> dict[str, Any]:
    """Decode the static tuple in DefaultRangeConfigSet."""
    blob = _abi_blob(data)
    if len(blob) != 4 * 32:
        raise ValueError("DefaultRangeConfigSet data must contain four ABI words")
    return _range_config(blob, 0)


def decode_market_range_config_data(data: str) -> dict[str, Any]:
    """Decode updateType and the static tuple in MarketRangeConfigSet."""
    blob = _abi_blob(data)
    if len(blob) < 7 * 32 or len(blob) % 32 != 0:
        raise ValueError("MarketRangeConfigSet data has an invalid ABI length")
    try:
        update_type = _dynamic_bytes(blob, 0, 5).decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("MarketRangeConfigSet updateType is not UTF-8") from error
    return {"update_type": update_type, "range_config": _range_config(blob, 1)}


def event_position(event: Mapping[str, Any]) -> EventPosition:
    """Return the canonical within-chain order for a decoded event."""
    return (
        int(event["block_number"]),
        int(event["transaction_index"]),
        int(event["log_index"]),
    )


def _latest_config_value(
    events: Sequence[Mapping[str, Any]],
    *,
    agent_id: int,
    event_name: str,
    field: str,
    before: EventPosition,
) -> Any:
    matches = [
        event
        for event in events
        if int(event.get("agent_id", -1)) == agent_id
        and str(event.get("event_name")) == event_name
        and event_position(event) < before
    ]
    if not matches:
        return None
    return max(matches, key=event_position)[field]


def _effective_expiry_timestamp(
    *,
    oracle_timestamp: int,
    proposal_position: EventPosition,
    agent_id: int,
    initial_period: int,
    config_events: Sequence[Mapping[str, Any]],
) -> int:
    period = initial_period
    expiry = oracle_timestamp + period + 1
    changes = sorted(
        (
            event
            for event in config_events
            if int(event.get("agent_id", -1)) == agent_id
            and str(event.get("event_name")) == "ExpirationPeriodSet"
            and event_position(event) > proposal_position
        ),
        key=event_position,
    )
    for event in changes:
        event_timestamp = int(event["block_timestamp"])
        if expiry <= event_timestamp:
            return expiry
        period = int(event["expiration_period"])
        revised = oracle_timestamp + period + 1
        if revised <= event_timestamp:
            return event_timestamp
        expiry = revised
    return expiry


def _terminal_choice_key(candidate: Mapping[str, Any]) -> tuple[int, EventPosition]:
    raw_position = candidate.get("position")
    if raw_position is None:
        position = (2**63 - 1, 2**63 - 1, 2**63 - 1)
    elif isinstance(raw_position, tuple) and len(raw_position) == 3:
        position = (
            int(raw_position[0]),
            int(raw_position[1]),
            int(raw_position[2]),
        )
    else:
        raise ValueError("terminal candidate has an invalid event position")
    return int(candidate["timestamp"]), position


def build_action_ledger(
    hub_events: Sequence[Mapping[str, Any]],
    proposals: Sequence[Mapping[str, Any]],
    *,
    end_timestamp: int,
) -> list[dict[str, Any]]:
    """Match proposals to agents/injections and assign frozen terminal classes."""
    ordered_hub = sorted(hub_events, key=event_position)
    registrations = [event for event in ordered_hub if str(event.get("event_name")) == "AgentRegistered"]
    injections = [event for event in ordered_hub if str(event.get("event_name")) == "UpdateInjected"]
    config_events = [event for event in ordered_hub if event not in registrations + injections]
    registration_ids = [int(event["agent_id"]) for event in registrations]
    if len(registration_ids) != len(set(registration_ids)):
        raise ValueError("an agent ID was registered more than once")

    ordered_proposals = sorted(proposals, key=event_position)
    ledger: list[dict[str, Any]] = []
    for proposal in ordered_proposals:
        proposal_position = event_position(proposal)
        candidates = [
            registration
            for registration in registrations
            if event_position(registration) < proposal_position
            and str(registration["risk_oracle"]) == str(proposal["risk_oracle"])
            and str(registration["update_type_hash"]) == str(proposal["update_type_hash"])
        ]
        row = dict(proposal)
        row["source_unambiguous"] = len(candidates) == 1
        row["agent_id"] = int(candidates[0]["agent_id"]) if len(candidates) == 1 else None
        row["delay_exposed"] = None
        row["minimum_delay_score"] = None
        if len(candidates) != 1:
            row["terminal_class"] = "unmatched_or_ambiguous"
            ledger.append(row)
            continue

        agent_id = int(candidates[0]["agent_id"])
        enabled = _latest_config_value(
            config_events,
            agent_id=agent_id,
            event_name="AgentEnabledSet",
            field="enabled",
            before=proposal_position,
        )
        expiration_period = _latest_config_value(
            config_events,
            agent_id=agent_id,
            event_name="ExpirationPeriodSet",
            field="expiration_period",
            before=proposal_position,
        )
        minimum_delay = _latest_config_value(
            config_events,
            agent_id=agent_id,
            event_name="MinimumDelaySet",
            field="minimum_delay",
            before=proposal_position,
        )
        if enabled is None or expiration_period is None or minimum_delay is None:
            row["terminal_class"] = "unmatched_or_ambiguous"
            row["source_unambiguous"] = False
            ledger.append(row)
            continue

        prior_injections = [
            injection
            for injection in injections
            if int(injection["agent_id"]) == agent_id
            and str(injection["market"]) == str(proposal["market"])
            and event_position(injection) < proposal_position
        ]
        if prior_injections and int(minimum_delay) > 0:
            last_injection = max(prior_injections, key=event_position)
            elapsed = int(proposal["block_timestamp"]) - int(last_injection["block_timestamp"])
            margin = elapsed - int(minimum_delay)
            row["delay_exposed"] = margin < 0
            row["minimum_delay_score"] = {
                "boundary_id": f"agent_{agent_id}_delay_{int(minimum_delay)}s",
                "minimum_delay_seconds": int(minimum_delay),
                "elapsed_since_prior_injection_seconds": elapsed,
                "margin_seconds": margin,
                "normalized_margin": margin / int(minimum_delay),
                "prior_injection_update_id": int(last_injection["update_id"]),
            }

        structural_injections = [
            injection
            for injection in injections
            if int(injection["agent_id"]) == agent_id
            and str(injection["update_type_hash"]) == str(proposal["update_type_hash"])
            and int(injection["update_id"]) == int(proposal["update_id"])
            and str(injection["market"]) == str(proposal["market"])
            and event_position(injection) > proposal_position
        ]
        exact_injections = [
            injection
            for injection in structural_injections
            if str(injection["new_value"]) == str(proposal["new_value"])
        ]
        if len(structural_injections) > 1 or (
            structural_injections and len(exact_injections) != len(structural_injections)
        ):
            row["terminal_class"] = "unmatched_or_ambiguous"
            row["source_unambiguous"] = False
            ledger.append(row)
            continue

        resolution_candidates: list[dict[str, Any]] = []
        if exact_injections:
            injection = exact_injections[0]
            resolution_candidates.append(
                {
                    "terminal_class": "injected",
                    "timestamp": int(injection["block_timestamp"]),
                    "position": event_position(injection),
                    "injection": injection,
                }
            )
        next_proposals = [
            candidate
            for candidate in ordered_proposals
            if str(candidate["risk_oracle"]) == str(proposal["risk_oracle"])
            and str(candidate["update_type_hash"]) == str(proposal["update_type_hash"])
            and str(candidate["market"]) == str(proposal["market"])
            and event_position(candidate) > proposal_position
        ]
        if next_proposals:
            overwritten = min(next_proposals, key=event_position)
            resolution_candidates.append(
                {
                    "terminal_class": "overwritten_uninjected",
                    "timestamp": int(overwritten["block_timestamp"]),
                    "position": event_position(overwritten),
                }
            )

        disable_events = [
            event
            for event in config_events
            if int(event.get("agent_id", -1)) == agent_id
            and str(event.get("event_name")) == "AgentEnabledSet"
            and not bool(event["enabled"])
            and event_position(event) > proposal_position
        ]
        if not bool(enabled):
            resolution_candidates.append(
                {
                    "terminal_class": "disabled_or_offboarded",
                    "timestamp": int(proposal["block_timestamp"]),
                    "position": proposal_position,
                }
            )
        elif disable_events:
            disabled = min(disable_events, key=event_position)
            resolution_candidates.append(
                {
                    "terminal_class": "disabled_or_offboarded",
                    "timestamp": int(disabled["block_timestamp"]),
                    "position": event_position(disabled),
                }
            )

        expiry_timestamp = _effective_expiry_timestamp(
            oracle_timestamp=int(proposal["oracle_timestamp"]),
            proposal_position=proposal_position,
            agent_id=agent_id,
            initial_period=int(expiration_period),
            config_events=config_events,
        )
        resolution_candidates.append(
            {
                "terminal_class": "expired_uninjected",
                "timestamp": expiry_timestamp,
                "position": None,
            }
        )
        first = min(resolution_candidates, key=_terminal_choice_key)
        if int(first["timestamp"]) > end_timestamp:
            row["terminal_class"] = "right_censored"
            row["resolution_timestamp"] = None
        else:
            row["terminal_class"] = str(first["terminal_class"])
            row["resolution_timestamp"] = int(first["timestamp"])
            if first["terminal_class"] == "injected":
                injection = first["injection"]
                row["injection_block_number"] = int(injection["block_number"])
                row["injection_transaction_hash"] = str(injection["transaction_hash"])
                row["injection_log_index"] = int(injection["log_index"])
                row["injection_delay_seconds"] = int(injection["block_timestamp"]) - int(
                    proposal["block_timestamp"]
                )
        ledger.append(row)
    return ledger


def summarize_delay_boundaries(
    ledger: Sequence[Mapping[str, Any]],
    *,
    minimum_scores: int,
    minimum_each_side: int,
    neighborhood_fraction: float,
    minimum_near_each_side: int,
    bunching_minimum_count: int,
    bunching_minimum_fraction: float,
) -> list[dict[str, Any]]:
    """Assess two-sided local support around exact minimum-delay boundaries."""
    if not 0 < neighborhood_fraction <= 1:
        raise ValueError("neighborhood fraction must be in (0, 1]")
    if not 0 <= bunching_minimum_fraction <= 1:
        raise ValueError("bunching fraction must be in [0, 1]")
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for row in ledger:
        score = row.get("minimum_delay_score")
        if isinstance(score, Mapping):
            grouped.setdefault(str(score["boundary_id"]), []).append(score)

    summaries: list[dict[str, Any]] = []
    for boundary_id, scores in sorted(grouped.items()):
        minimum_delay = int(scores[0]["minimum_delay_seconds"])
        if any(int(score["minimum_delay_seconds"]) != minimum_delay for score in scores):
            raise ValueError(f"boundary {boundary_id} mixes minimum-delay values")
        margins = [int(score["margin_seconds"]) for score in scores]
        negative = [margin for margin in margins if margin < 0]
        positive = [margin for margin in margins if margin > 0]
        exact = [margin for margin in margins if margin == 0]
        radius = neighborhood_fraction * minimum_delay
        near_negative = [margin for margin in negative if abs(margin) <= radius]
        near_positive = [margin for margin in positive if margin <= radius]
        support_checks = {
            "minimum_scores": len(margins) >= minimum_scores,
            "minimum_each_side": (len(negative) >= minimum_each_side and len(positive) >= minimum_each_side),
            "minimum_near_each_side": (
                len(near_negative) >= minimum_near_each_side and len(near_positive) >= minimum_near_each_side
            ),
        }
        otherwise_eligible = all(support_checks.values())
        exact_fraction = len(exact) / len(margins) if margins else 0.0
        bunched = len(exact) >= bunching_minimum_count and exact_fraction >= bunching_minimum_fraction
        summaries.append(
            {
                "boundary_id": boundary_id,
                "minimum_delay_seconds": minimum_delay,
                "score_count": len(margins),
                "negative_count": len(negative),
                "positive_count": len(positive),
                "exact_boundary_count": len(exact),
                "exact_boundary_fraction": exact_fraction,
                "near_negative_count": len(near_negative),
                "near_positive_count": len(near_positive),
                "minimum_margin_seconds": min(margins),
                "maximum_margin_seconds": max(margins),
                "support_checks": support_checks,
                "otherwise_eligible_before_bunching_check": otherwise_eligible,
                "exact_boundary_bunching": bunched,
                "qualifies": otherwise_eligible and not bunched,
            }
        )
    return summaries


def assess_action_support(
    ledger: Sequence[Mapping[str, Any]],
    registrations: Sequence[Mapping[str, Any]],
    thresholds: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply all frozen D0 pass/stop criteria to a decoded action ledger."""
    unambiguous = [row for row in ledger if bool(row.get("source_unambiguous"))]
    exact_injected = [row for row in unambiguous if row.get("terminal_class") == "injected"]
    resolved_non_immediate = [
        row
        for row in unambiguous
        if row.get("terminal_class")
        in {"overwritten_uninjected", "expired_uninjected", "disabled_or_offboarded"}
        or (row.get("terminal_class") == "injected" and bool(row.get("delay_exposed")))
    ]
    non_right_censored = [row for row in ledger if row.get("terminal_class") != "right_censored"]
    classified = [row for row in non_right_censored if row.get("terminal_class") != "unmatched_or_ambiguous"]
    classification_rate = len(classified) / len(non_right_censored) if non_right_censored else 0.0
    boundaries = summarize_delay_boundaries(
        ledger,
        minimum_scores=int(thresholds["minimum_reconstructable_scores_for_one_boundary"]),
        minimum_each_side=int(thresholds["minimum_observations_each_side"]),
        neighborhood_fraction=float(thresholds["boundary_neighborhood_fraction"]),
        minimum_near_each_side=int(thresholds["minimum_near_boundary_each_side"]),
        bunching_minimum_count=int(thresholds["exact_boundary_bunching_minimum_count"]),
        bunching_minimum_fraction=float(thresholds["exact_boundary_bunching_minimum_fraction"]),
    )
    represented_agents = {int(row["agent_id"]) for row in unambiguous}
    registered_agent_ids = {int(row["agent_id"]) for row in registrations}
    terminal_counts = Counter(str(row["terminal_class"]) for row in ledger)
    checks = {
        "minimum_unambiguous_proposals": len(unambiguous) >= int(thresholds["minimum_unambiguous_proposals"]),
        "minimum_exact_injections": len(exact_injected) >= int(thresholds["minimum_exact_injections"]),
        "minimum_update_types": len({str(row["update_type_hash"]) for row in unambiguous})
        >= int(thresholds["minimum_update_types"]),
        "minimum_markets": len({str(row["market"]) for row in unambiguous})
        >= int(thresholds["minimum_markets"]),
        "minimum_registered_agents": len(represented_agents) >= int(thresholds["minimum_registered_agents"]),
        "minimum_resolved_non_immediate_proposals": len(resolved_non_immediate)
        >= int(thresholds["minimum_resolved_non_immediate_proposals"]),
        "one_boundary_has_two_sided_near_support": any(
            bool(boundary["qualifies"]) for boundary in boundaries
        ),
        "not_bunched_at_every_otherwise_eligible_boundary": any(
            bool(boundary["otherwise_eligible_before_bunching_check"])
            and not bool(boundary["exact_boundary_bunching"])
            for boundary in boundaries
        ),
        "minimum_terminal_classification_rate": classification_rate
        >= float(thresholds["minimum_terminal_classification_rate"]),
    }
    return {
        "proposal_count": len(ledger),
        "unambiguous_proposal_count": len(unambiguous),
        "exact_injection_count": len(exact_injected),
        "distinct_update_type_count": len({str(row["update_type_hash"]) for row in unambiguous}),
        "distinct_market_count": len({str(row["market"]) for row in unambiguous}),
        "registered_agent_count": len(registered_agent_ids),
        "represented_agent_count": len(represented_agents),
        "resolved_non_immediate_proposal_count": len(resolved_non_immediate),
        "terminal_counts": dict(sorted(terminal_counts.items())),
        "terminal_classification_rate_excluding_right_censoring": classification_rate,
        "delay_boundaries": boundaries,
        "range_boundary_scores_reconstructed": 0,
        "range_boundary_scores_unavailable_reason": (
            "agent validation reads contemporaneous protocol state; RiskOracle.previousValue is only "
            "the prior oracle proposal and is not a valid substitute"
        ),
        "decision_checks": checks,
        "passed": all(checks.values()),
    }


def _latest_config_event(
    events: Sequence[Mapping[str, Any]],
    *,
    agent_id: int,
    event_name: str,
    before: EventPosition,
) -> Mapping[str, Any] | None:
    matches = [
        event
        for event in events
        if int(event.get("agent_id", -1)) == agent_id
        and str(event.get("event_name")) == event_name
        and event_position(event) < before
    ]
    return max(matches, key=event_position) if matches else None


def _initialized_registration(
    registration: Mapping[str, Any],
    config_events: Sequence[Mapping[str, Any]],
    *,
    before: EventPosition,
) -> dict[str, Any] | None:
    agent_id = int(registration["agent_id"])
    agent_address = _latest_config_event(
        config_events,
        agent_id=agent_id,
        event_name="AgentAddressSet",
        before=before,
    )
    enabled_events = [
        event
        for event in config_events
        if int(event.get("agent_id", -1)) == agent_id
        and str(event.get("event_name")) == "AgentEnabledSet"
        and event_position(event) < before
    ]
    expiration = _latest_config_event(
        config_events,
        agent_id=agent_id,
        event_name="ExpirationPeriodSet",
        before=before,
    )
    minimum_delay = _latest_config_event(
        config_events,
        agent_id=agent_id,
        event_name="MinimumDelaySet",
        before=before,
    )
    if (
        agent_address is None
        or not any(bool(event["enabled"]) for event in enabled_events)
        or expiration is None
        or minimum_delay is None
    ):
        return None
    latest_enabled = max(enabled_events, key=event_position)
    return {
        "registration": registration,
        "agent_address": str(agent_address["agent_address"]),
        "enabled": bool(latest_enabled["enabled"]),
        "expiration_period": int(expiration["expiration_period"]),
        "minimum_delay": int(minimum_delay["minimum_delay"]),
        "minimum_delay_epoch_position": event_position(minimum_delay),
    }


def build_holdout_chain_ledger(
    hub_events: Sequence[Mapping[str, Any]],
    proposals: Sequence[Mapping[str, Any]],
    *,
    chain_id: int,
    chain_name: str,
    expected_risk_oracle: str,
    end_timestamp: int,
) -> dict[str, list[dict[str, Any]]]:
    """Build activation-conditioned eligible and exclusion ledgers for one chain."""
    if chain_id <= 0:
        raise ValueError("chain_id must be positive")
    normalized_oracle = normalize_address(expected_risk_oracle)
    ordered_hub = sorted(hub_events, key=event_position)
    registrations = [event for event in ordered_hub if event.get("event_name") == "AgentRegistered"]
    injections = [event for event in ordered_hub if event.get("event_name") == "UpdateInjected"]
    config_events = [event for event in ordered_hub if event not in registrations + injections]
    registration_ids = [int(event["agent_id"]) for event in registrations]
    if len(registration_ids) != len(set(registration_ids)):
        raise ValueError(f"an agent ID was registered more than once on {chain_name}")
    if any(normalize_address(str(proposal["risk_oracle"])) != normalized_oracle for proposal in proposals):
        raise ValueError(f"{chain_name} proposal came from a non-pinned Risk Oracle")

    ordered_proposals = sorted(proposals, key=event_position)
    eligible: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    for proposal in ordered_proposals:
        proposal_position = event_position(proposal)
        source_registrations = [
            registration
            for registration in registrations
            if normalize_address(str(registration["risk_oracle"])) == normalized_oracle
            and str(registration["update_type_hash"]) == str(proposal["update_type_hash"])
        ]
        prior_registrations = [
            registration
            for registration in source_registrations
            if event_position(registration) < proposal_position
        ]
        initialized = [
            state
            for registration in prior_registrations
            if (
                state := _initialized_registration(
                    registration,
                    config_events,
                    before=proposal_position,
                )
            )
            is not None
        ]
        base = {**proposal, "chain_id": chain_id, "chain_name": chain_name}
        if not initialized:
            if not source_registrations:
                reason = "never_registered"
            elif not prior_registrations:
                reason = "pre_registration"
            else:
                reason = "pre_initialization"
            exclusions.append(
                {
                    **base,
                    "eligible": False,
                    "exclusion_reason": reason,
                }
            )
            continue

        row: dict[str, Any] = {
            **base,
            "eligible": True,
            "source_unambiguous": len(initialized) == 1,
            "agent_id": int(initialized[0]["registration"]["agent_id"]) if len(initialized) == 1 else None,
            "delay_exposed": None,
            "minimum_delay_score": None,
        }
        if len(initialized) != 1:
            row["terminal_class"] = "unmatched_or_ambiguous"
            row["ambiguity_reason"] = "multiple_initialized_source_registrations"
            eligible.append(row)
            continue

        state = initialized[0]
        agent_id = int(state["registration"]["agent_id"])
        minimum_delay = int(state["minimum_delay"])
        prior_injections = [
            injection
            for injection in injections
            if int(injection["agent_id"]) == agent_id
            and str(injection["market"]) == str(proposal["market"])
            and event_position(injection) < proposal_position
        ]
        if prior_injections and minimum_delay > 0:
            last_injection = max(prior_injections, key=event_position)
            elapsed = int(proposal["block_timestamp"]) - int(last_injection["block_timestamp"])
            margin = elapsed - minimum_delay
            epoch = state["minimum_delay_epoch_position"]
            row["delay_exposed"] = margin < 0
            row["minimum_delay_score"] = {
                "boundary_id": (
                    f"chain_{chain_id}_agent_{agent_id}_delay_{minimum_delay}s_"
                    f"epoch_{epoch[0]}_{epoch[1]}_{epoch[2]}"
                ),
                "chain_id": chain_id,
                "chain_name": chain_name,
                "agent_id": agent_id,
                "minimum_delay_seconds": minimum_delay,
                "minimum_delay_epoch_position": list(epoch),
                "elapsed_since_prior_injection_seconds": elapsed,
                "margin_seconds": margin,
                "normalized_margin": margin / minimum_delay,
                "prior_injection_update_id": int(last_injection["update_id"]),
            }

        structural_injections = [
            injection
            for injection in injections
            if int(injection["agent_id"]) == agent_id
            and str(injection["update_type_hash"]) == str(proposal["update_type_hash"])
            and int(injection["update_id"]) == int(proposal["update_id"])
            and str(injection["market"]) == str(proposal["market"])
            and event_position(injection) > proposal_position
        ]
        exact_injections = [
            injection
            for injection in structural_injections
            if str(injection["new_value"]) == str(proposal["new_value"])
        ]
        if len(structural_injections) > 1 or (
            structural_injections and len(exact_injections) != len(structural_injections)
        ):
            row["terminal_class"] = "unmatched_or_ambiguous"
            row["source_unambiguous"] = False
            row["ambiguity_reason"] = "structural_injection_not_one_exact_value_match"
            eligible.append(row)
            continue

        resolution_candidates: list[dict[str, Any]] = []
        if exact_injections:
            injection = exact_injections[0]
            resolution_candidates.append(
                {
                    "terminal_class": "injected",
                    "timestamp": int(injection["block_timestamp"]),
                    "position": event_position(injection),
                    "injection": injection,
                }
            )
        next_proposals = [
            candidate
            for candidate in ordered_proposals
            if normalize_address(str(candidate["risk_oracle"])) == normalized_oracle
            and str(candidate["update_type_hash"]) == str(proposal["update_type_hash"])
            and str(candidate["market"]) == str(proposal["market"])
            and event_position(candidate) > proposal_position
        ]
        if next_proposals:
            overwritten = min(next_proposals, key=event_position)
            resolution_candidates.append(
                {
                    "terminal_class": "overwritten_uninjected",
                    "timestamp": int(overwritten["block_timestamp"]),
                    "position": event_position(overwritten),
                }
            )

        disable_events = [
            event
            for event in config_events
            if int(event.get("agent_id", -1)) == agent_id
            and event.get("event_name") == "AgentEnabledSet"
            and not bool(event["enabled"])
            and event_position(event) > proposal_position
        ]
        if not bool(state["enabled"]):
            resolution_candidates.append(
                {
                    "terminal_class": "disabled_or_offboarded",
                    "timestamp": int(proposal["block_timestamp"]),
                    "position": proposal_position,
                }
            )
        elif disable_events:
            disabled = min(disable_events, key=event_position)
            resolution_candidates.append(
                {
                    "terminal_class": "disabled_or_offboarded",
                    "timestamp": int(disabled["block_timestamp"]),
                    "position": event_position(disabled),
                }
            )

        expiry_timestamp = _effective_expiry_timestamp(
            oracle_timestamp=int(proposal["oracle_timestamp"]),
            proposal_position=proposal_position,
            agent_id=agent_id,
            initial_period=int(state["expiration_period"]),
            config_events=config_events,
        )
        resolution_candidates.append(
            {
                "terminal_class": "expired_uninjected",
                "timestamp": expiry_timestamp,
                "position": None,
            }
        )
        first = min(resolution_candidates, key=_terminal_choice_key)
        if int(first["timestamp"]) > end_timestamp:
            row["terminal_class"] = "right_censored"
            row["resolution_timestamp"] = None
        else:
            row["terminal_class"] = str(first["terminal_class"])
            row["resolution_timestamp"] = int(first["timestamp"])
            if first["terminal_class"] == "injected":
                injection = first["injection"]
                row["injection_block_number"] = int(injection["block_number"])
                row["injection_transaction_hash"] = str(injection["transaction_hash"])
                row["injection_log_index"] = int(injection["log_index"])
                row["injection_delay_seconds"] = int(injection["block_timestamp"]) - int(
                    proposal["block_timestamp"]
                )
        eligible.append(row)
    return {"eligible": eligible, "exclusions": exclusions}


def assign_action_batches(
    ledger: Sequence[Mapping[str, Any]],
    *,
    maximum_adjacent_gap_seconds: int,
) -> list[dict[str, Any]]:
    """Assign deterministic connected time batches across chains and update types."""
    if maximum_adjacent_gap_seconds < 0:
        raise ValueError("maximum adjacent batch gap cannot be negative")
    ordered = sorted(
        (dict(row) for row in ledger),
        key=lambda row: (
            int(row["oracle_timestamp"]),
            int(row["chain_id"]),
            event_position(row),
        ),
    )
    components: list[list[dict[str, Any]]] = []
    for row in ordered:
        if (
            not components
            or int(row["oracle_timestamp"]) - int(components[-1][-1]["oracle_timestamp"])
            > maximum_adjacent_gap_seconds
        ):
            components.append([])
        components[-1].append(row)

    for component_index, component in enumerate(components):
        identities = sorted(
            (
                int(row["chain_id"]),
                str(row["block_hash"]),
                str(row["transaction_hash"]),
                int(row["log_index"]),
            )
            for row in component
        )
        encoded = json.dumps(identities, separators=(",", ":")).encode()
        batch_id = hashlib.sha256(encoded).hexdigest()
        for row in component:
            row["action_batch_id"] = batch_id
            row["action_batch_index"] = component_index
            row["action_batch_size"] = len(component)
    return ordered


def summarize_holdout_delay_boundaries(
    ledger: Sequence[Mapping[str, Any]],
    rules: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Summarize row and conservative batch-median support for holdout boundaries."""
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in ledger:
        score = row.get("minimum_delay_score")
        if isinstance(score, Mapping):
            if not isinstance(row.get("action_batch_id"), str):
                raise ValueError("delay score lacks an action batch")
            grouped[str(score["boundary_id"])].append(row)

    summaries: list[dict[str, Any]] = []
    for boundary_id, rows in sorted(grouped.items()):
        scores = [row["minimum_delay_score"] for row in rows]
        minimum_delay = int(scores[0]["minimum_delay_seconds"])
        if any(int(score["minimum_delay_seconds"]) != minimum_delay for score in scores):
            raise ValueError(f"boundary {boundary_id} mixes minimum-delay values")
        margins = [int(score["margin_seconds"]) for score in scores]
        radius = float(rules["neighborhood_fraction"]) * minimum_delay
        negative = [margin for margin in margins if margin < 0]
        positive = [margin for margin in margins if margin > 0]
        exact = [margin for margin in margins if margin == 0]
        near_negative = [margin for margin in negative if abs(margin) <= radius]
        near_positive = [margin for margin in positive if margin <= radius]

        by_batch: dict[str, list[int]] = defaultdict(list)
        for row in rows:
            by_batch[str(row["action_batch_id"])].append(int(row["minimum_delay_score"]["margin_seconds"]))
        batch_margins = [float(median(values)) for _, values in sorted(by_batch.items())]
        batch_negative = [margin for margin in batch_margins if margin < 0]
        batch_positive = [margin for margin in batch_margins if margin > 0]
        batch_exact = [margin for margin in batch_margins if margin == 0]
        batch_near_negative = [margin for margin in batch_negative if abs(margin) <= radius]
        batch_near_positive = [margin for margin in batch_positive if margin <= radius]

        row_checks = {
            "minimum_scores": len(margins) >= int(rules["row_level_minimum_scores"]),
            "minimum_each_side": len(negative) >= int(rules["row_level_minimum_each_side"])
            and len(positive) >= int(rules["row_level_minimum_each_side"]),
            "minimum_near_each_side": len(near_negative) >= int(rules["row_level_minimum_near_each_side"])
            and len(near_positive) >= int(rules["row_level_minimum_near_each_side"]),
        }
        batch_checks = {
            "minimum_scores": len(batch_margins) >= int(rules["batch_level_minimum_scores"]),
            "minimum_each_side": len(batch_negative) >= int(rules["batch_level_minimum_each_side"])
            and len(batch_positive) >= int(rules["batch_level_minimum_each_side"]),
            "minimum_near_each_side": len(batch_near_negative)
            >= int(rules["batch_level_minimum_near_each_side"])
            and len(batch_near_positive) >= int(rules["batch_level_minimum_near_each_side"]),
        }
        row_bunched = len(exact) >= int(rules["exact_row_bunching_minimum_count"]) and len(exact) / len(
            margins
        ) >= float(rules["exact_bunching_minimum_fraction"])
        batch_bunched = len(batch_exact) >= int(rules["exact_batch_bunching_minimum_count"]) and len(
            batch_exact
        ) / len(batch_margins) >= float(rules["exact_bunching_minimum_fraction"])
        otherwise_eligible = all(row_checks.values()) and all(batch_checks.values())
        summaries.append(
            {
                "boundary_id": boundary_id,
                "chain_id": int(scores[0]["chain_id"]),
                "chain_name": str(scores[0]["chain_name"]),
                "agent_id": int(scores[0]["agent_id"]),
                "minimum_delay_seconds": minimum_delay,
                "row_score_count": len(margins),
                "row_negative_count": len(negative),
                "row_positive_count": len(positive),
                "row_exact_count": len(exact),
                "row_near_negative_count": len(near_negative),
                "row_near_positive_count": len(near_positive),
                "batch_score_count": len(batch_margins),
                "batch_negative_count": len(batch_negative),
                "batch_positive_count": len(batch_positive),
                "batch_exact_count": len(batch_exact),
                "batch_near_negative_count": len(batch_near_negative),
                "batch_near_positive_count": len(batch_near_positive),
                "minimum_row_margin_seconds": min(margins),
                "maximum_row_margin_seconds": max(margins),
                "minimum_batch_median_margin_seconds": min(batch_margins),
                "maximum_batch_median_margin_seconds": max(batch_margins),
                "row_support_checks": row_checks,
                "batch_support_checks": batch_checks,
                "otherwise_eligible_before_bunching_check": otherwise_eligible,
                "row_exact_boundary_bunching": row_bunched,
                "batch_exact_boundary_bunching": batch_bunched,
                "qualifies": otherwise_eligible and not row_bunched and not batch_bunched,
            }
        )
    return summaries


def assess_holdout_action_support(
    ledger: Sequence[Mapping[str, Any]],
    exclusions: Sequence[Mapping[str, Any]],
    *,
    thresholds: Mapping[str, Any],
    boundary_rules: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply the frozen multichain row, batch and boundary support gates."""
    eligible = list(ledger)
    batches = {str(row["action_batch_id"]) for row in eligible}
    exact_injected = [
        row
        for row in eligible
        if bool(row.get("source_unambiguous")) and row.get("terminal_class") == "injected"
    ]
    resolved_non_immediate = [
        row
        for row in eligible
        if bool(row.get("source_unambiguous"))
        and (
            row.get("terminal_class")
            in {"overwritten_uninjected", "expired_uninjected", "disabled_or_offboarded"}
            or (row.get("terminal_class") == "injected" and bool(row.get("delay_exposed")))
        )
    ]
    non_right_censored = [row for row in eligible if row.get("terminal_class") != "right_censored"]
    classified = [row for row in non_right_censored if row.get("terminal_class") != "unmatched_or_ambiguous"]
    classification_rate = len(classified) / len(non_right_censored) if non_right_censored else 0.0
    boundaries = summarize_holdout_delay_boundaries(eligible, boundary_rules)
    qualifying = [boundary for boundary in boundaries if bool(boundary["qualifies"])]
    represented_agents = {
        (int(row["chain_id"]), int(row["agent_id"])) for row in eligible if row.get("agent_id") is not None
    }
    represented_chains = {int(row["chain_id"]) for row in eligible}
    non_immediate_batches = {str(row["action_batch_id"]) for row in resolved_non_immediate}
    checks = {
        "minimum_eligible_proposals": len(eligible) >= int(thresholds["minimum_eligible_proposals"]),
        "minimum_exact_injections": len(exact_injected) >= int(thresholds["minimum_exact_injections"]),
        "minimum_update_types": len({str(row["update_type_hash"]) for row in eligible})
        >= int(thresholds["minimum_update_types"]),
        "minimum_chain_market_pairs": len({(int(row["chain_id"]), str(row["market"])) for row in eligible})
        >= int(thresholds["minimum_chain_market_pairs"]),
        "minimum_represented_chain_agents": len(represented_agents)
        >= int(thresholds["minimum_represented_chain_agents"]),
        "minimum_represented_chains": len(represented_chains)
        >= int(thresholds["minimum_represented_chains"]),
        "minimum_proposal_batches": len(batches) >= int(thresholds["minimum_proposal_batches"]),
        "minimum_resolved_non_immediate_proposals": len(resolved_non_immediate)
        >= int(thresholds["minimum_resolved_non_immediate_proposals"]),
        "minimum_resolved_non_immediate_batches": len(non_immediate_batches)
        >= int(thresholds["minimum_resolved_non_immediate_batches"]),
        "minimum_terminal_classification_rate": classification_rate
        >= float(thresholds["minimum_terminal_classification_rate"]),
        "minimum_qualifying_boundaries": len(qualifying)
        >= int(boundary_rules["minimum_qualifying_boundaries"]),
        "minimum_chains_with_qualifying_boundary": len({int(boundary["chain_id"]) for boundary in qualifying})
        >= int(boundary_rules["minimum_chains_with_qualifying_boundary"]),
    }
    return {
        "eligible_proposal_count": len(eligible),
        "excluded_proposal_count": len(exclusions),
        "exclusion_counts": dict(sorted(Counter(str(row["exclusion_reason"]) for row in exclusions).items())),
        "proposal_batch_count": len(batches),
        "exact_injection_count": len(exact_injected),
        "exact_injection_batch_count": len({str(row["action_batch_id"]) for row in exact_injected}),
        "distinct_update_type_count": len({str(row["update_type_hash"]) for row in eligible}),
        "distinct_chain_market_pair_count": len(
            {(int(row["chain_id"]), str(row["market"])) for row in eligible}
        ),
        "represented_chain_agent_count": len(represented_agents),
        "represented_chain_count": len(represented_chains),
        "resolved_non_immediate_proposal_count": len(resolved_non_immediate),
        "resolved_non_immediate_batch_count": len(non_immediate_batches),
        "terminal_counts": dict(sorted(Counter(str(row["terminal_class"]) for row in eligible).items())),
        "terminal_classification_rate_excluding_right_censoring": classification_rate,
        "delay_boundaries": boundaries,
        "qualifying_boundary_count": len(qualifying),
        "qualifying_boundary_chain_count": len({int(boundary["chain_id"]) for boundary in qualifying}),
        "range_boundary_scores_reconstructed": 0,
        "range_boundary_scores_unavailable_reason": (
            "agents validate contemporaneous protocol state; RiskOracle.previousValue is only the prior "
            "oracle proposal"
        ),
        "decision_checks": checks,
        "passed": all(checks.values()),
    }
