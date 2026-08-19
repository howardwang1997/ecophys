from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = REPO_ROOT / "results/empirical_physics/aave_agent_guardrail_d0_result.json"
CONFIG_PATH = REPO_ROOT / "configs/empirical_physics/aave_agent_guardrail_d0_v1.yaml"


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _canonical_sha256(value: Any) -> str:
    normalized = json.loads(json.dumps(value, allow_nan=False))
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _position(event: dict[str, Any]) -> tuple[int, int, int]:
    return (
        int(event["block_number"]),
        int(event["transaction_index"]),
        int(event["log_index"]),
    )


def test_frozen_d0_result_digest_repository_and_blinding() -> None:
    result = _load_json(RESULT_PATH)
    digest = result.pop("canonical_payload_sha256")

    assert _canonical_sha256(result) == digest
    assert digest == "764f08a7a02c550f28f8b7ace275cf4e451ba5430ea5768aff55f374c1226460"
    assert result["repository"]["git_sha"] == "cce8d234e7eb8d208c4bb2731bb61f63baee5ad7"
    assert result["decision"] == "stop_threshold_causal_route_before_market_outcomes"
    assert result["checkpoint"]["checkpoint_removed_after_success"] is True
    assert result["blinding"] == {
        "only_configuration_proposal_injection_events_and_headers_queried": True,
        "pool_balances_utilization_rates_positions_prices_liquidations_queried": False,
        "raw_rpc_responses_retained": False,
        "risk_oracle_previous_value_used_as_protocol_state": False,
        "user_transactions_or_market_response_windows_queried": False,
    }
    assert result["compute"] == {
        "cpu_only": True,
        "ecomd_used": False,
        "gpu_used": False,
        "paid_data_used": False,
    }


def test_frozen_d0_support_gate_recomputes_without_runner_helpers() -> None:
    result = _load_json(RESULT_PATH)
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    thresholds = config["pass_thresholds"]
    surface = result["action_surface"]
    ledger = surface["proposal_ledger"]
    registrations = [event for event in surface["hub_events"] if event["event_name"] == "AgentRegistered"]

    unambiguous = [row for row in ledger if row["source_unambiguous"]]
    injected = [row for row in unambiguous if row["terminal_class"] == "injected"]
    resolved_non_immediate = [
        row
        for row in unambiguous
        if row["terminal_class"] in {"overwritten_uninjected", "expired_uninjected", "disabled_or_offboarded"}
        or (row["terminal_class"] == "injected" and row["delay_exposed"] is True)
    ]
    non_right_censored = [row for row in ledger if row["terminal_class"] != "right_censored"]
    classified = [row for row in non_right_censored if row["terminal_class"] != "unmatched_or_ambiguous"]
    classification_rate = len(classified) / len(non_right_censored)

    grouped_scores: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in ledger:
        score = row["minimum_delay_score"]
        if score is not None:
            grouped_scores[str(score["boundary_id"])].append(score)
    qualifying_boundaries = 0
    eligible_unbunched_boundaries = 0
    for scores in grouped_scores.values():
        minimum_delay = int(scores[0]["minimum_delay_seconds"])
        margins = [int(score["margin_seconds"]) for score in scores]
        radius = float(thresholds["boundary_neighborhood_fraction"]) * minimum_delay
        negative = [margin for margin in margins if margin < 0]
        positive = [margin for margin in margins if margin > 0]
        exact = [margin for margin in margins if margin == 0]
        near_negative = [margin for margin in negative if abs(margin) <= radius]
        near_positive = [margin for margin in positive if margin <= radius]
        otherwise_eligible = (
            len(margins) >= int(thresholds["minimum_reconstructable_scores_for_one_boundary"])
            and len(negative) >= int(thresholds["minimum_observations_each_side"])
            and len(positive) >= int(thresholds["minimum_observations_each_side"])
            and len(near_negative) >= int(thresholds["minimum_near_boundary_each_side"])
            and len(near_positive) >= int(thresholds["minimum_near_boundary_each_side"])
        )
        bunched = len(exact) >= int(thresholds["exact_boundary_bunching_minimum_count"]) and len(exact) / len(
            margins
        ) >= float(thresholds["exact_boundary_bunching_minimum_fraction"])
        qualifying_boundaries += int(otherwise_eligible and not bunched)
        eligible_unbunched_boundaries += int(otherwise_eligible and not bunched)

    represented_agents = {int(row["agent_id"]) for row in unambiguous}
    checks = {
        "minimum_unambiguous_proposals": len(unambiguous) >= int(thresholds["minimum_unambiguous_proposals"]),
        "minimum_exact_injections": len(injected) >= int(thresholds["minimum_exact_injections"]),
        "minimum_update_types": len({row["update_type_hash"] for row in unambiguous})
        >= int(thresholds["minimum_update_types"]),
        "minimum_markets": len({row["market"] for row in unambiguous}) >= int(thresholds["minimum_markets"]),
        "minimum_registered_agents": len(represented_agents) >= int(thresholds["minimum_registered_agents"]),
        "minimum_resolved_non_immediate_proposals": len(resolved_non_immediate)
        >= int(thresholds["minimum_resolved_non_immediate_proposals"]),
        "one_boundary_has_two_sided_near_support": qualifying_boundaries > 0,
        "not_bunched_at_every_otherwise_eligible_boundary": eligible_unbunched_boundaries > 0,
        "minimum_terminal_classification_rate": classification_rate
        >= float(thresholds["minimum_terminal_classification_rate"]),
    }

    assert len(ledger) == surface["proposal_event_count"] == 155
    assert len(registrations) == surface["registration_count"] == 5
    assert len(injected) == surface["injection_event_count"] == 127
    assert len(unambiguous) == 133
    assert len(resolved_non_immediate) == 38
    assert len({row["market"] for row in unambiguous}) == 17
    assert len({row["update_type_hash"] for row in unambiguous}) == 5
    assert classification_rate == 133 / 155
    assert checks == result["support_gate"]["decision_checks"]
    assert [name for name, passed in checks.items() if not passed] == ["minimum_terminal_classification_rate"]
    assert result["support_gate"]["passed"] is False


def test_injected_rows_have_one_exact_later_hub_event() -> None:
    result = _load_json(RESULT_PATH)
    surface = result["action_surface"]
    injections = [event for event in surface["hub_events"] if event["event_name"] == "UpdateInjected"]
    injected_rows = [
        row
        for row in surface["proposal_ledger"]
        if row["source_unambiguous"] and row["terminal_class"] == "injected"
    ]

    for row in injected_rows:
        matches = [
            event
            for event in injections
            if event["agent_id"] == row["agent_id"]
            and event["update_type_hash"] == row["update_type_hash"]
            and event["update_id"] == row["update_id"]
            and event["market"] == row["market"]
            and event["new_value"] == row["new_value"]
            and _position(event) > _position(row)
        ]
        assert len(matches) == 1
        match = matches[0]
        assert (
            row["injection_block_number"],
            row["injection_transaction_hash"],
            row["injection_log_index"],
        ) == (
            match["block_number"],
            match["transaction_hash"],
            match["log_index"],
        )


def test_unmatched_rows_are_pre_registration_or_never_registered() -> None:
    result = _load_json(RESULT_PATH)
    surface = result["action_surface"]
    registrations = [event for event in surface["hub_events"] if event["event_name"] == "AgentRegistered"]
    registrations_by_source = {
        (event["risk_oracle"], event["update_type_hash"]): event for event in registrations
    }
    unmatched = [
        row for row in surface["proposal_ledger"] if row["terminal_class"] == "unmatched_or_ambiguous"
    ]
    pre_registration = []
    never_registered = []
    for row in unmatched:
        registration = registrations_by_source.get((row["risk_oracle"], row["update_type_hash"]))
        if registration is None:
            never_registered.append(row)
        else:
            assert _position(row) < _position(registration)
            pre_registration.append(row)

    assert all(row["agent_id"] is None for row in unmatched)
    assert len(pre_registration) == 21
    assert len(never_registered) == 1
    assert Counter(row["update_type_hash"] for row in unmatched).most_common()[0][1] == 19

    post_registration = [
        row
        for row in surface["proposal_ledger"]
        if (registration := registrations_by_source.get((row["risk_oracle"], row["update_type_hash"])))
        is not None
        and _position(registration) < _position(row)
    ]
    assert len(post_registration) == 133
    assert all(row["terminal_class"] != "unmatched_or_ambiguous" for row in post_registration)


def test_action_surface_contains_no_market_outcome_fields_or_duplicate_logs() -> None:
    result = _load_json(RESULT_PATH)
    surface = result["action_surface"]
    event_groups = [
        surface["hub_events"],
        surface["range_configuration_events"],
        surface["proposal_ledger"],
    ]
    forbidden_keys = {
        "borrow_rate",
        "liquidation",
        "pool_balance",
        "position",
        "price",
        "supply_rate",
        "user_transaction",
        "utilization",
    }
    identities: set[tuple[str, str, int]] = set()
    for events in event_groups:
        for event in events:
            assert forbidden_keys.isdisjoint(event)
            identity = (event["block_hash"], event["transaction_hash"], event["log_index"])
            assert identity not in identities
            identities.add(identity)
    assert len(identities) == 405
