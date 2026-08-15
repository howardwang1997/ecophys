"""Post-hoc concentration diagnostics for mechanism-to-exposure routing."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import cast

SCHEMA_VERSION = "ecophys-exposure-routing-exploratory/v1"


def _mapping(value: object, *, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be a mapping")
    return cast(Mapping[str, object], value)


def _sequence(value: object, *, path: str) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{path} must be a sequence")
    return cast(Sequence[object], value)


def validate_routing_contract(
    contract: Mapping[str, object], *, exposure_census_sha256: str, summary_sha256: str
) -> tuple[str, ...]:
    """Validate the post-hoc metric freeze and its no-new-access boundary."""

    errors: list[str] = []
    if contract.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if contract.get("stage") != "frozen_posthoc_before_routing_metric_computation":
        errors.append("routing analysis stage changed")
    if contract.get("scientific_status") != "post_hoc_description_no_inferential_gate":
        errors.append("routing analysis must remain explicitly post hoc")
    if contract.get("result") is not None:
        errors.append("routing result must be null before computation")
    try:
        parent = _mapping(contract.get("parent"), path="parent")
        metrics = _mapping(contract.get("metrics"), path="metrics")
        identity = _mapping(contract.get("mathematical_identity"), path="mathematical_identity")
        access = _mapping(contract.get("access_boundary"), path="access_boundary")
        artifacts = _mapping(contract.get("artifacts"), path="artifacts")
    except ValueError as error:
        errors.append(str(error))
        return tuple(errors)

    if parent.get("exposure_census_sha256") != exposure_census_sha256:
        errors.append("parent exposure-census hash changed")
    if parent.get("summary_sha256") != summary_sha256:
        errors.append("parent summary hash changed")
    if parent.get("input_already_consumed") is not True:
        errors.append("routing input must remain disclosed as already consumed")
    expected_parent: dict[str, object] = {
        "protocol_commit": "ab722229d305220c23ec53d268a91d854a6a4e31",
        "result_commit": "6e71239366b1b1f64006a1cfc2cc563d13b9423e",
        "exposure_census": (
            "experiments/v14_uniswap_v3_preperiod_exposure_census/artifacts/exposure_census.jsonl"
        ),
        "summary": "experiments/v14_uniswap_v3_preperiod_exposure_census/artifacts/summary.json",
    }
    for key, expected_value in expected_parent.items():
        if parent.get(key) != expected_value:
            errors.append(f"parent.{key} changed")
    if parent.get("u1r_decision_remains_binding") != (
        "FAIL_FULL_PREPERIOD_EXPOSURE_SUPPORT_KEEP_UNISWAP_M2_ONLY"
    ):
        errors.append("binding U1R decision changed")
    if list(_sequence(metrics.get("channels"), path="metrics.channels")) != [
        "swap_count",
        "position_action_count",
        "combined_event_count",
    ]:
        errors.append("routing channels changed")
    if list(_sequence(metrics.get("top_k"), path="metrics.top_k")) != [1, 3, 5, 10, 20]:
        errors.append("routing top-k set changed")
    if list(_sequence(metrics.get("partitions"), path="metrics.partitions")) != [
        "packed_fee_68",
        "packed_fee_102",
        "propagation_batch_1",
        "propagation_batch_2",
    ]:
        errors.append("routing partitions changed")
    if metrics.get("top_pool_rows_per_channel") != 10:
        errors.append("top-pool row count changed")
    if list(_sequence(metrics.get("concentration"), path="metrics.concentration")) != [
        "active_fraction",
        "top_k_shares",
        "hhi",
        "inverse_hhi_effective_count",
        "entropy_effective_count",
        "gini_population",
        "gini_active",
        "uniform_to_event_total_variation",
        "exposure_multiplier_variance",
    ]:
        errors.append("routing concentration metrics changed")
    if list(_sequence(metrics.get("channel_comparison"), path="metrics.channel_comparison")) != [
        "support_overlap",
        "weight_total_variation",
        "jensen_shannon_divergence",
        "cosine_similarity",
    ]:
        errors.append("routing channel-comparison metrics changed")
    expected_identity: dict[str, object] = {
        "uniform_measure": "u_i_equals_1_over_N",
        "event_measure": "p_i_equals_event_count_i_over_total_event_count",
        "exposure_multiplier": "g_i_equals_N_times_p_i",
        "exact_mean_gap": "E_p_response_minus_E_u_response_equals_Cov_u_g_response",
        "total_variation_bound": "absolute_mean_gap_at_most_TV_times_response_range",
        "cauchy_bound": ("absolute_mean_gap_at_most_sqrt_N_HHI_minus_1_times_response_variance"),
        "status": "algebraic_identity_not_novel_theorem",
    }
    for key, expected_value in expected_identity.items():
        if identity.get(key) != expected_value:
            errors.append(f"mathematical_identity.{key} changed")
    required_true = ("source_is_only_committed_u1r_counts",)
    required_false = (
        "new_network_or_chain_access",
        "post_treatment_data_opened",
        "control_data_opened",
        "identity_data_opened",
        "amount_price_liquidity_decoded",
        "u1r_reanalysis_changes_decision",
        "inferential_pass_fail_gate",
        "paid_data",
    )
    for key in required_true:
        if access.get(key) is not True:
            errors.append(f"access_boundary.{key} must remain true")
    for key in required_false:
        if access.get(key) is not False:
            errors.append(f"access_boundary.{key} must remain false")
    if access.get("gpu_hours") != 0:
        errors.append("routing analysis GPU hours must remain zero")
    expected_artifacts = {
        "plan": "experiments/v14_uniswap_v3_exposure_routing_exploratory/EXPLORATORY_PLAN.md",
        "summary": (
            "experiments/v14_uniswap_v3_exposure_routing_exploratory/artifacts/exploratory_summary.json"
        ),
    }
    for key, expected_value in expected_artifacts.items():
        if artifacts.get(key) != expected_value:
            errors.append(f"artifacts.{key} changed")
    return tuple(errors)


def _counts(values: Sequence[object], *, path: str) -> list[int]:
    counts: list[int] = []
    for index, value in enumerate(values):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{path}[{index}] must be a non-negative integer")
        counts.append(value)
    if not counts:
        raise ValueError(f"{path} cannot be empty")
    return counts


def concentration_metrics(values: Sequence[object], *, top_k: Sequence[int]) -> dict[str, object]:
    """Describe one non-negative event-count measure without inferential gates."""

    counts = _counts(values, path="counts")
    requested_top_k = sorted(set(top_k))
    if not requested_top_k or requested_top_k[0] <= 0:
        raise ValueError("top_k must contain positive integers")
    population = len(counts)
    active = [value for value in counts if value > 0]
    total = sum(counts)
    if total == 0:
        return {
            "population_count": population,
            "active_count": 0,
            "inactive_count": population,
            "active_fraction": 0.0,
            "total_count": 0,
            "maximum_count": 0,
            "maximum_share": None,
            "top_k_shares": {str(k): None for k in requested_top_k},
            "hhi": None,
            "inverse_hhi_effective_count": None,
            "entropy_effective_count": None,
            "gini_population": None,
            "gini_active": None,
            "uniform_to_event_total_variation": None,
            "exposure_multiplier_variance": None,
            "cauchy_gap_multiplier": None,
        }

    probabilities = [value / total for value in counts]
    ordered = sorted(counts, reverse=True)
    hhi = sum(probability * probability for probability in probabilities)
    entropy = -sum(probability * math.log(probability) for probability in probabilities if probability > 0)

    def gini(sample: Sequence[int]) -> float:
        ordered_sample = sorted(sample)
        sample_total = sum(ordered_sample)
        n = len(ordered_sample)
        return (
            2.0 * sum((index + 1) * value for index, value in enumerate(ordered_sample)) / (n * sample_total)
            - (n + 1.0) / n
        )

    uniform_probability = 1.0 / population
    total_variation = 0.5 * sum(abs(probability - uniform_probability) for probability in probabilities)
    exposure_multiplier_variance = population * hhi - 1.0
    return {
        "population_count": population,
        "active_count": len(active),
        "inactive_count": population - len(active),
        "active_fraction": len(active) / population,
        "total_count": total,
        "maximum_count": ordered[0],
        "maximum_share": ordered[0] / total,
        "top_k_shares": {str(k): sum(ordered[: min(k, population)]) / total for k in requested_top_k},
        "hhi": hhi,
        "inverse_hhi_effective_count": 1.0 / hhi,
        "entropy_effective_count": math.exp(entropy),
        "gini_population": gini(counts),
        "gini_active": gini(active),
        "uniform_to_event_total_variation": total_variation,
        "exposure_multiplier_variance": exposure_multiplier_variance,
        "cauchy_gap_multiplier": math.sqrt(exposure_multiplier_variance),
    }


def compare_event_channels(first: Sequence[object], second: Sequence[object]) -> dict[str, object]:
    """Compare support and normalized mass for two event-count channels."""

    first_counts = _counts(first, path="first")
    second_counts = _counts(second, path="second")
    if len(first_counts) != len(second_counts):
        raise ValueError("event channels must have equal population length")
    first_total = sum(first_counts)
    second_total = sum(second_counts)
    if first_total == 0 or second_total == 0:
        raise ValueError("event-channel comparisons require positive totals")
    first_probability = [value / first_total for value in first_counts]
    second_probability = [value / second_total for value in second_counts]
    mixture = [
        (left + right) / 2.0 for left, right in zip(first_probability, second_probability, strict=True)
    ]

    def kl_divergence(probability: Sequence[float], reference: Sequence[float]) -> float:
        return sum(
            value * math.log(value / target)
            for value, target in zip(probability, reference, strict=True)
            if value > 0
        )

    first_support = {index for index, value in enumerate(first_counts) if value > 0}
    second_support = {index for index, value in enumerate(second_counts) if value > 0}
    intersection = first_support & second_support
    union = first_support | second_support
    dot_product = sum(left * right for left, right in zip(first_probability, second_probability, strict=True))
    first_norm = math.sqrt(sum(value * value for value in first_probability))
    second_norm = math.sqrt(sum(value * value for value in second_probability))
    jensen_shannon = 0.5 * (
        kl_divergence(first_probability, mixture) + kl_divergence(second_probability, mixture)
    )
    return {
        "first_active_count": len(first_support),
        "second_active_count": len(second_support),
        "intersection_active_count": len(intersection),
        "union_active_count": len(union),
        "support_jaccard": len(intersection) / len(union) if union else None,
        "first_support_covered_by_second": (
            len(intersection) / len(first_support) if first_support else None
        ),
        "second_support_covered_by_first": (
            len(intersection) / len(second_support) if second_support else None
        ),
        "weight_total_variation": 0.5
        * sum(abs(left - right) for left, right in zip(first_probability, second_probability, strict=True)),
        "jensen_shannon_nats": jensen_shannon,
        "jensen_shannon_normalized": jensen_shannon / math.log(2.0),
        "cosine_similarity": dot_product / (first_norm * second_norm),
    }


def summarize_exposure_routing(
    rows: Sequence[Mapping[str, object]], *, top_k: Sequence[int]
) -> dict[str, object]:
    """Build the frozen post-hoc routing description from U1R census rows."""

    if len(rows) != 1000:
        raise ValueError("routing summary requires the exact 1,000-row U1R population")
    pools: list[str] = []
    for index, row in enumerate(rows):
        pool = row.get("pool_address")
        if not isinstance(pool, str):
            raise ValueError(f"rows[{index}].pool_address must be a string")
        pools.append(pool)
    if len(set(pools)) != 1000:
        raise ValueError("routing summary requires 1,000 unique pool addresses")
    if (
        sum(row.get("packed_fee_value") == 68 for row in rows) != 107
        or sum(row.get("packed_fee_value") == 102 for row in rows) != 893
    ):
        raise ValueError("routing summary requires the exact U1R fee composition")
    swap = _counts([row.get("swap_count") for row in rows], path="swap_count")
    position = _counts([row.get("position_action_count") for row in rows], path="position_action_count")
    combined = [left + right for left, right in zip(swap, position, strict=True)]
    channel_counts = {
        "swap_count": swap,
        "position_action_count": position,
        "combined_event_count": combined,
    }
    channel_totals = {name: sum(values) for name, values in channel_counts.items()}
    channels = {
        "swap_count": concentration_metrics(swap, top_k=top_k),
        "position_action_count": concentration_metrics(position, top_k=top_k),
        "combined_event_count": concentration_metrics(combined, top_k=top_k),
    }

    partitions: dict[str, dict[str, object]] = {}
    partition_specs = {
        "packed_fee_68": [index for index, row in enumerate(rows) if row.get("packed_fee_value") == 68],
        "packed_fee_102": [index for index, row in enumerate(rows) if row.get("packed_fee_value") == 102],
        "propagation_batch_1": list(range(500)),
        "propagation_batch_2": list(range(500, 1000)),
    }
    for name, indices in partition_specs.items():
        population_share = len(indices) / len(rows)
        partition_channel_totals = {
            "swap_count": sum(swap[index] for index in indices),
            "position_action_count": sum(position[index] for index in indices),
            "combined_event_count": sum(combined[index] for index in indices),
        }
        partitions[name] = {
            "pool_count": len(indices),
            "population_share": population_share,
            "swap_active_count": sum(swap[index] > 0 for index in indices),
            "position_active_count": sum(position[index] > 0 for index in indices),
            "event_active_count": sum(combined[index] > 0 for index in indices),
            "channel_totals": partition_channel_totals,
            "channel_global_shares": {
                channel: total / channel_totals[channel]
                for channel, total in partition_channel_totals.items()
            },
            "representation_ratios": {
                channel: total / channel_totals[channel] / population_share
                for channel, total in partition_channel_totals.items()
            },
        }

    top_pools: dict[str, list[dict[str, object]]] = {}
    for channel, counts in channel_counts.items():
        order = sorted(range(len(rows)), key=lambda index: (-counts[index], index))[:10]
        top_pools[channel] = [
            {
                "rank": rank,
                "pool_address": pools[index],
                "packed_fee_value": rows[index].get("packed_fee_value"),
                "calldata_index": rows[index].get("calldata_index"),
                "count": counts[index],
                "share": counts[index] / sum(counts),
            }
            for rank, index in enumerate(order, start=1)
        ]

    return {
        "schema_version": "ecophys-exposure-routing-exploratory-result/v1",
        "scientific_status": "POST_HOC_DESCRIPTION_NO_INFERENTIAL_GATE",
        "population_pool_count": len(rows),
        "channels": channels,
        "swap_vs_position": compare_event_channels(swap, position),
        "partitions": partitions,
        "top_pools": top_pools,
        "routing_identity": {
            "definitions": "u_i=1/N; p_i=a_i/sum_j(a_j); g_i=N*p_i",
            "exact_identity": "E_p[r]-E_u[r]=Cov_u(g,r)",
            "total_variation_bound_for_unit_range_response": ("abs(E_p[r]-E_u[r])<=TV(p,u)*range(r)"),
            "cauchy_bound": "abs(E_p[r]-E_u[r])<=sqrt((N*HHI(p)-1)*Var_u(r))",
            "interpretation": (
                "technical activation and event-weighted economic incidence are different measures"
            ),
        },
        "claim_locks": {
            "u1r_reopened": False,
            "causal_effect_claimed": False,
            "event_count_called_volume_or_liquidity": False,
            "all_uniswap_prevalence_claimed": False,
            "post_treatment_data_opened": False,
            "new_network_data_opened": False,
            "gpu_hours": 0,
        },
    }
