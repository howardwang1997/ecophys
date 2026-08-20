from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = REPO_ROOT / "results/empirical_physics/aave_agent_guardrail_holdout_d0_v2_result.json"
ARBITRUM_REPLICATION_PATH = (
    REPO_ROOT
    / "results/empirical_physics/aave_agent_guardrail_holdout_d0_v2_arbitrum_official_replication.json"
)
CONFIG_PATH = REPO_ROOT / "configs/empirical_physics/aave_agent_guardrail_holdout_d0_v2.yaml"


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _canonical_sha256(value: Any) -> str:
    normalized = json.loads(json.dumps(value, allow_nan=False))
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _boundary_diagnostics(
    rows: list[dict[str, Any]],
    config: dict[str, Any],
    *,
    neighborhood_fraction: float | None = None,
    row_minimum_scores: int | None = None,
    row_minimum_each_side: int | None = None,
    row_minimum_near_each_side: int | None = None,
) -> dict[str, dict[str, Any]]:
    thresholds = config["boundary_support"]
    grouped_rows: dict[str, list[tuple[str, int, int]]] = defaultdict(list)
    for row in rows:
        score = row["minimum_delay_score"]
        if score is None:
            continue
        grouped_rows[str(score["boundary_id"])].append(
            (
                str(row["action_batch_id"]),
                int(score["margin_seconds"]),
                int(score["minimum_delay_seconds"]),
            )
        )

    diagnostics: dict[str, dict[str, Any]] = {}
    for boundary_id, observations in grouped_rows.items():
        delay_values = {observation[2] for observation in observations}
        assert len(delay_values) == 1
        minimum_delay = delay_values.pop()
        radius = (
            float(thresholds["neighborhood_fraction"])
            if neighborhood_fraction is None
            else neighborhood_fraction
        ) * minimum_delay
        row_margins = [observation[1] for observation in observations]
        grouped_batches: dict[str, list[int]] = defaultdict(list)
        for batch_id, margin, _ in observations:
            grouped_batches[batch_id].append(margin)
        batch_margins = [float(median(margins)) for margins in grouped_batches.values()]

        def support(values: list[int] | list[float], radius_seconds: float) -> dict[str, Any]:
            negative = [value for value in values if value < 0]
            positive = [value for value in values if value > 0]
            exact = [value for value in values if value == 0]
            return {
                "count": len(values),
                "negative_count": len(negative),
                "positive_count": len(positive),
                "exact_count": len(exact),
                "near_negative_count": len(
                    [value for value in negative if abs(value) <= radius_seconds]
                ),
                "near_positive_count": len(
                    [value for value in positive if value <= radius_seconds]
                ),
                "closest_negative": max(negative) if negative else None,
                "closest_positive": min(positive) if positive else None,
            }

        row_support = support(row_margins, radius)
        batch_support = support(batch_margins, radius)
        required_row_scores = (
            int(thresholds["row_level_minimum_scores"])
            if row_minimum_scores is None
            else row_minimum_scores
        )
        required_row_side = (
            int(thresholds["row_level_minimum_each_side"])
            if row_minimum_each_side is None
            else row_minimum_each_side
        )
        required_row_near = (
            int(thresholds["row_level_minimum_near_each_side"])
            if row_minimum_near_each_side is None
            else row_minimum_near_each_side
        )
        row_ok = (
            row_support["count"] >= required_row_scores
            and row_support["negative_count"] >= required_row_side
            and row_support["positive_count"] >= required_row_side
            and row_support["near_negative_count"] >= required_row_near
            and row_support["near_positive_count"] >= required_row_near
        )
        batch_ok = (
            batch_support["count"] >= int(thresholds["batch_level_minimum_scores"])
            and batch_support["negative_count"] >= int(thresholds["batch_level_minimum_each_side"])
            and batch_support["positive_count"] >= int(thresholds["batch_level_minimum_each_side"])
            and batch_support["near_negative_count"]
            >= int(thresholds["batch_level_minimum_near_each_side"])
            and batch_support["near_positive_count"]
            >= int(thresholds["batch_level_minimum_near_each_side"])
        )
        row_bunched = row_support["exact_count"] >= int(
            thresholds["exact_row_bunching_minimum_count"]
        ) and row_support["exact_count"] / row_support["count"] >= float(
            thresholds["exact_bunching_minimum_fraction"]
        )
        batch_bunched = batch_support["exact_count"] >= int(
            thresholds["exact_batch_bunching_minimum_count"]
        ) and batch_support["exact_count"] / batch_support["count"] >= float(
            thresholds["exact_bunching_minimum_fraction"]
        )
        score = observations[0]
        diagnostics[boundary_id] = {
            "chain_id": int(boundary_id.split("_")[1]),
            "agent_id": int(boundary_id.split("_")[3]),
            "minimum_delay_seconds": score[2],
            "radius_seconds": radius,
            "row": row_support,
            "batch": batch_support,
            "qualifies": row_ok and batch_ok and not row_bunched and not batch_bunched,
        }
    return diagnostics


def test_frozen_holdout_result_digest_repository_and_blinding() -> None:
    result = _load_json(RESULT_PATH)
    digest = result.pop("canonical_payload_sha256")

    assert _canonical_sha256(result) == digest
    assert digest == "89309106c370404049ad27247ee8e0efe3d01a787cb4e0f1feae689e2de960e8"
    assert result["repository"] == {
        "clean_worktree_at_start": True,
        "config_path": "configs/empirical_physics/aave_agent_guardrail_holdout_d0_v2.yaml",
        "config_sha256": "93be07281ff57e853d32f5caadc2f08d9a38e9e91728c35c8126a22aab25246c",
        "git_sha": "c9ab42a64295ec6bd3ea6868050cb9ca4dd05d15",
    }
    assert result["decision"] == "stop_multichain_threshold_route_before_d1_and_market_outcomes"
    assert result["chain_count"] == 9
    assert set(result["chains"]) == {
        "arbitrum",
        "avalanche",
        "base",
        "bnb",
        "gnosis",
        "linea",
        "optimism",
        "plasma",
        "polygon",
    }
    assert result["freeze_provenance"] == {
        "all_chains_must_rerun_under_one_v2_config_digest": True,
        "all_parent_config_chain_artifacts_are_diagnostic_only": True,
        "independent_full_union_transport_replication_required_before_market_outcomes": True,
        "market_outcomes_queried_before_amendment": False,
        "parent_config_sha256": "1c2eaa505b1993df153ff8cdd90ff698745fb4a7ec398aee8fa9f301e5a47eb9",
        "parent_contract_version": 1,
        "parent_repository_git_sha": "ac99559212dd0a0943c669b5d0981908e44d81e8",
        "status": "transport_amended_after_outcome_blind_policy_event_diagnostics_before_market_outcomes",
        "transport_only_amendment": True,
    }
    assert result["blinding"] == {
        "ethereum_pilot_rows_in_holdout_counts": False,
        "only_agent_configuration_proposal_injection_events_and_headers_queried": True,
        "pool_state_or_market_outcomes_queried": False,
        "raw_rpc_responses_retained": False,
    }
    assert result["compute"] == {
        "cpu_only": True,
        "ecomd_used": False,
        "gpu_used": False,
        "paid_data_used": False,
    }


def test_frozen_holdout_support_gate_recomputes_without_runner_helpers() -> None:
    result = _load_json(RESULT_PATH)
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    assert isinstance(config, dict)
    thresholds = config["pass_thresholds"]
    boundary_thresholds = config["boundary_support"]
    surface = result["combined_action_surface"]
    rows = surface["eligible_proposal_ledger_with_action_batches"]
    exclusions = surface["proposal_exclusion_ledger"]

    assert all(row["eligible"] is True and row["source_unambiguous"] is True for row in rows)
    injected = [row for row in rows if row["terminal_class"] == "injected"]
    resolved_non_immediate = [
        row
        for row in rows
        if row["terminal_class"]
        in {"overwritten_uninjected", "expired_uninjected", "disabled_or_offboarded"}
        or (row["terminal_class"] == "injected" and row["delay_exposed"] is True)
    ]
    non_right_censored = [row for row in rows if row["terminal_class"] != "right_censored"]
    classified = [
        row for row in non_right_censored if row["terminal_class"] != "unmatched_or_ambiguous"
    ]
    classification_rate = len(classified) / len(non_right_censored)
    diagnostics = _boundary_diagnostics(rows, config)
    qualifying = [diagnostic for diagnostic in diagnostics.values() if diagnostic["qualifies"]]
    qualifying_chains = {diagnostic["chain_id"] for diagnostic in qualifying}

    represented_chain_agents = {(int(row["chain_id"]), int(row["agent_id"])) for row in rows}
    checks = {
        "minimum_eligible_proposals": len(rows) >= int(thresholds["minimum_eligible_proposals"]),
        "minimum_exact_injections": len(injected) >= int(thresholds["minimum_exact_injections"]),
        "minimum_update_types": len({row["update_type_hash"] for row in rows})
        >= int(thresholds["minimum_update_types"]),
        "minimum_chain_market_pairs": len({(row["chain_id"], row["market"]) for row in rows})
        >= int(thresholds["minimum_chain_market_pairs"]),
        "minimum_represented_chain_agents": len(represented_chain_agents)
        >= int(thresholds["minimum_represented_chain_agents"]),
        "minimum_represented_chains": len({row["chain_id"] for row in rows})
        >= int(thresholds["minimum_represented_chains"]),
        "minimum_proposal_batches": len({row["action_batch_id"] for row in rows})
        >= int(thresholds["minimum_proposal_batches"]),
        "minimum_resolved_non_immediate_proposals": len(resolved_non_immediate)
        >= int(thresholds["minimum_resolved_non_immediate_proposals"]),
        "minimum_resolved_non_immediate_batches": len(
            {row["action_batch_id"] for row in resolved_non_immediate}
        )
        >= int(thresholds["minimum_resolved_non_immediate_batches"]),
        "minimum_terminal_classification_rate": classification_rate
        >= float(thresholds["minimum_terminal_classification_rate"]),
        "minimum_qualifying_boundaries": len(qualifying)
        >= int(boundary_thresholds["minimum_qualifying_boundaries"]),
        "minimum_chains_with_qualifying_boundary": len(qualifying_chains)
        >= int(boundary_thresholds["minimum_chains_with_qualifying_boundary"]),
    }

    assert len(rows) == 215
    assert len(exclusions) == 163
    assert len(rows) + len(exclusions) == 378
    assert len(injected) == 202
    assert len({row["action_batch_id"] for row in rows}) == 151
    assert len({row["action_batch_id"] for row in injected}) == 143
    assert len({row["update_type_hash"] for row in rows}) == 4
    assert len({(row["chain_id"], row["market"]) for row in rows}) == 49
    assert len(represented_chain_agents) == 18
    assert len({row["chain_id"] for row in rows}) == 9
    assert len(resolved_non_immediate) == 42
    assert len({row["action_batch_id"] for row in resolved_non_immediate}) == 28
    assert classification_rate == 1.0
    assert Counter(row["terminal_class"] for row in rows) == {
        "expired_uninjected": 13,
        "injected": 202,
    }
    assert Counter(row["exclusion_reason"] for row in exclusions) == {
        "never_registered": 75,
        "pre_registration": 88,
    }
    assert len(diagnostics) == 13
    assert len(qualifying) == 0
    assert len(qualifying_chains) == 0
    assert checks == result["support_gate"]["decision_checks"]
    assert [name for name, passed in checks.items() if not passed] == [
        "minimum_qualifying_boundaries",
        "minimum_chains_with_qualifying_boundary",
    ]
    assert result["support_gate"]["passed"] is False


def test_boundary_failure_geometry_and_posthoc_sensitivity_do_not_rescue_freeze() -> None:
    result = _load_json(RESULT_PATH)
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    assert isinstance(config, dict)
    rows = result["combined_action_surface"]["eligible_proposal_ledger_with_action_batches"]
    frozen = _boundary_diagnostics(rows, config)
    by_chain_agent = {
        (diagnostic["chain_id"], diagnostic["agent_id"]): diagnostic
        for diagnostic in frozen.values()
    }

    plasma = by_chain_agent[(9745, 0)]
    assert plasma["radius_seconds"] == 64_800
    assert plasma["row"] == {
        "count": 60,
        "negative_count": 18,
        "positive_count": 42,
        "exact_count": 0,
        "near_negative_count": 18,
        "near_positive_count": 0,
        "closest_negative": -7,
        "closest_positive": 85_767,
    }
    assert plasma["batch"]["count"] == 25
    assert plasma["batch"]["negative_count"] == 9
    assert plasma["batch"]["positive_count"] == 16
    assert plasma["batch"]["near_negative_count"] == 9
    assert plasma["batch"]["near_positive_count"] == 0

    optimism = by_chain_agent[(10, 0)]
    assert optimism["row"] == {
        "count": 16,
        "negative_count": 4,
        "positive_count": 12,
        "exact_count": 0,
        "near_negative_count": 4,
        "near_positive_count": 6,
        "closest_negative": -2,
        "closest_positive": 32,
    }
    assert optimism["batch"]["count"] == 16
    assert optimism["batch"]["negative_count"] == 4
    assert optimism["batch"]["positive_count"] == 12

    wider_neighborhood = _boundary_diagnostics(rows, config, neighborhood_fraction=1 / 3)
    relaxed_row_counts = _boundary_diagnostics(
        rows,
        config,
        row_minimum_scores=16,
        row_minimum_each_side=4,
        row_minimum_near_each_side=4,
    )
    both_relaxations = _boundary_diagnostics(
        rows,
        config,
        neighborhood_fraction=1 / 3,
        row_minimum_scores=16,
        row_minimum_each_side=4,
        row_minimum_near_each_side=4,
    )

    def qualifying_chain_agents(values: dict[str, dict[str, Any]]) -> set[tuple[int, int]]:
        return {
            (diagnostic["chain_id"], diagnostic["agent_id"])
            for diagnostic in values.values()
            if diagnostic["qualifies"]
        }

    assert qualifying_chain_agents(frozen) == set()
    assert qualifying_chain_agents(wider_neighborhood) == {(9745, 0)}
    assert qualifying_chain_agents(relaxed_row_counts) == {(10, 0)}
    assert qualifying_chain_agents(both_relaxations) == {(10, 0), (9745, 0)}
    assert result["support_gate"]["passed"] is False


def test_official_arbitrum_replication_matches_primary_complete_action_surface() -> None:
    result = _load_json(RESULT_PATH)
    replication = _load_json(ARBITRUM_REPLICATION_PATH)
    replication_digest = replication.pop("canonical_payload_sha256")
    primary = result["chains"]["arbitrum"]

    assert _canonical_sha256(replication) == replication_digest
    assert replication_digest == "d5eed01f2b6666a18e8c588c80fe5ea52ea82b5898df71cdcc11c7db5f22922b"
    assert primary["artifact_canonical_payload_sha256"] == (
        "1b02c48bd4d97655d651dec1fd2d549a9147e1e047dacd8dbc2789e87c9b7a9b"
    )
    assert replication["repository"] == result["repository"]
    assert replication["freeze_provenance"] == result["freeze_provenance"]
    assert replication["chain"]["name"] == "arbitrum"
    assert replication["transport"]["formal_rpc"] == "https://arb1.arbitrum.io/rpc"
    assert primary["transport"]["formal_rpc"] == "https://arbitrum.gateway.tenderly.co"
    assert replication["transport_qualification"]["reference_rpc"] == (
        "https://arbitrum.gateway.tenderly.co"
    )
    assert replication["action_surface"] == primary["action_surface"]
    assert _canonical_sha256(replication["action_surface"]) == (
        "11ee6f153425f1ddb34c692af9e2bf242ca2533f279af59856282248159237c2"
    )
    assert replication["action_surface"]["raw_proposal_count"] == 34
    assert replication["action_surface"]["eligible_proposal_count"] == 29
    assert replication["action_surface"]["excluded_proposal_count"] == 5
    assert replication["action_surface"]["injection_event_count"] == 27
    assert replication["blinding"] == {
        "only_agent_configuration_proposal_injection_events_and_headers_queried": True,
        "pool_state_or_market_outcomes_queried": False,
        "raw_rpc_responses_retained": False,
    }
    assert replication["compute"] == {
        "cpu_only": True,
        "ecomd_used": False,
        "gpu_used": False,
        "paid_data_used": False,
    }
