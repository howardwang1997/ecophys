"""Metric-specific unseen-instrument confirmation for evaluator v2."""

from __future__ import annotations

from typing import Any, cast

import numpy as np

from .evaluator_v2 import (
    GATING_SPLITS,
    METRIC_NAMES,
    SplitSeries,
    SurrogateKind,
    assess_declared_relation,
    build_nonoverlapping_blocks,
    deterministic_seed,
    make_surrogate,
    safe_estimate,
    split_conformal_interval,
)


def evaluate_fresh_market_confirmation(
    series_by_symbol: dict[str, dict[str, SplitSeries]],
    protocol: dict[str, Any],
) -> dict[str, Any]:
    """Apply frozen block, coverage, surrogate, market-count, and core gates."""
    data_contract = _mapping(protocol["data"], "data")
    blocking = _mapping(protocol["blocking"], "blocking")
    conformal = _mapping(protocol["conformal"], "conformal")
    surrogate_contract = _mapping(protocol["surrogates"], "surrogates")
    metric_contract = _mapping(protocol["metric_contract"], "metric_contract")
    eligibility = _mapping(protocol["eligibility"], "eligibility")
    decision_contract = _mapping(protocol["decision"], "decision")
    symbols = [str(value) for value in cast(list[object], data_contract["all_symbols"])]
    lengths = [int(str(value)) for value in cast(list[object], blocking["all_lengths"])]
    minimum_blocks = int(blocking["minimum_blocks_per_gating_split_at_each_applicable_length"])
    generation_splits = [
        str(value) for value in cast(list[object], surrogate_contract["generation_splits"])
    ]
    replicates = int(surrogate_contract["replicates_per_real_block"])
    root_seed = int(surrogate_contract["root_seed"])
    if tuple(str(name) for name in eligibility["original_finiteness_splits"]) != GATING_SPLITS:
        raise ValueError("finiteness split registry differs from implementation")
    if not set(metric_contract).issubset(METRIC_NAMES):
        raise ValueError("fresh-market metric registry contains an unsupported estimator")
    if set(series_by_symbol) != set(symbols):
        raise ValueError("loaded symbol set differs from the frozen universe")
    if "sealed_crash" in {split for splits in series_by_symbol.values() for split in splits}:
        raise ValueError("sealed_crash must never be loaded")

    blocks: dict[str, dict[str, dict[int, tuple[Any, ...]]]] = {}
    inventory: dict[str, dict[str, dict[str, int]]] = {}
    block_eligible: dict[str, dict[int, bool]] = {}
    volume_observable: dict[str, bool] = {}
    for symbol in symbols:
        missing = sorted(set(GATING_SPLITS) - set(series_by_symbol[symbol]))
        if missing:
            raise ValueError(f"{symbol} lacks gating splits: {missing}")
        blocks[symbol] = {}
        inventory[symbol] = {}
        block_eligible[symbol] = {}
        volumes = []
        for split_name, split_series in series_by_symbol[symbol].items():
            blocks[symbol][split_name] = {}
            inventory[symbol][split_name] = {}
            for length in lengths:
                built = build_nonoverlapping_blocks(
                    split_series.returns,
                    split_series.volume,
                    length,
                )
                blocks[symbol][split_name][length] = built
                inventory[symbol][split_name][str(length)] = len(built)
            if split_name in GATING_SPLITS and split_series.volume is not None:
                volumes.append(split_series.volume)
        for length in lengths:
            block_eligible[symbol][length] = all(
                len(blocks[symbol][split_name][length]) >= minimum_blocks
                for split_name in GATING_SPLITS
            )
        if len(volumes) != len(GATING_SPLITS):
            volume_observable[symbol] = False
        else:
            joined = np.concatenate(volumes)
            volume_observable[symbol] = bool(
                np.all(np.isfinite(joined)) and np.ptp(joined) > 0.0
            )

    cells: dict[str, dict[str, dict[str, Any]]] = {}
    metric_decisions: dict[str, dict[str, Any]] = {}
    for metric_name, raw_spec in metric_contract.items():
        spec = _mapping(raw_spec, f"metric_contract.{metric_name}")
        role = str(spec["role"])
        diagnostic_only = role == "diagnostic_only"
        metric_lengths = [
            int(str(value)) for value in cast(list[object], spec["lengths"])
        ]
        if not set(metric_lengths).issubset(lengths):
            raise ValueError(f"{metric_name} declares a length outside blocking.all_lengths")
        applicable_symbols = _applicable_symbols(
            symbols,
            spec,
            volume_observable=volume_observable,
        )
        cells[metric_name] = {}
        for symbol in symbols:
            cells[metric_name][symbol] = {}
            for length in metric_lengths:
                if symbol not in applicable_symbols:
                    cells[metric_name][symbol][str(length)] = {
                        "applicable": False,
                        "reason": "outside_metric_scope_or_missing_observable",
                        "primary_gate_used": False,
                    }
                    continue
                if not block_eligible[symbol][length]:
                    cells[metric_name][symbol][str(length)] = {
                        "applicable": True,
                        "block_count_eligible": False,
                        "reason": "minimum_gating_split_block_count_failed",
                        "primary_gate_used": False,
                        "primary_gate_pass": False,
                    }
                    continue
                real_estimates: dict[str, list[float | None]] = {}
                real_errors: dict[str, list[str | None]] = {}
                for split_name, split_blocks in blocks[symbol].items():
                    estimates: list[float | None] = []
                    errors: list[str | None] = []
                    for block in split_blocks[length]:
                        estimate, error = safe_estimate(metric_name, block)
                        estimates.append(estimate)
                        errors.append(error)
                    real_estimates[split_name] = estimates
                    real_errors[split_name] = errors
                original_finite = all(
                    value is not None
                    for split_name in GATING_SPLITS
                    for value in real_estimates[split_name]
                )
                if original_finite:
                    report_values = real_estimates.get("report_only_guard", [])
                    report_for_coverage = (
                        [] if any(value is None for value in report_values) else _present(report_values)
                    )
                    conformal_result = split_conformal_interval(
                        _present(real_estimates["reference"]),
                        _present(real_estimates["conformal_calibration"]),
                        _present(real_estimates["confirmation"]),
                        _present(real_estimates["temporal_test"]),
                        report_for_coverage,
                        alpha=float(conformal["alpha"]),
                        minimum_confirmation_coverage=float(
                            conformal["minimum_observed_confirmation_coverage"]
                        ),
                        minimum_temporal_coverage=float(
                            conformal["minimum_observed_temporal_coverage"]
                        ),
                    ).to_dict()
                else:
                    conformal_result = {
                        "status": "nonfinite_original_estimate",
                        "pass_both": False,
                    }

                surrogate_real: list[float | None] = []
                surrogate_values: list[list[float | None]] = []
                surrogate_errors: list[list[str | None]] = []
                surrogate_kind = cast(SurrogateKind, str(spec["primary_surrogate"]))
                for split_name in generation_splits:
                    for block_index, block in enumerate(blocks[symbol][split_name][length]):
                        surrogate_real.append(real_estimates[split_name][block_index])
                        path_values: list[float | None] = []
                        path_errors: list[str | None] = []
                        for replicate in range(replicates):
                            seed = deterministic_seed(
                                root_seed,
                                metric_name,
                                symbol,
                                split_name,
                                length,
                                block_index,
                                surrogate_kind,
                                replicate,
                            )
                            try:
                                control = make_surrogate(block, surrogate_kind, seed=seed)
                                estimate, error = safe_estimate(metric_name, control)
                            except Exception as exc:
                                estimate, error = None, f"{type(exc).__name__}: {exc}"
                            path_values.append(estimate)
                            path_errors.append(error)
                        surrogate_values.append(path_values)
                        surrogate_errors.append(path_errors)
                surrogate_finite = bool(surrogate_real) and all(
                    value is not None for value in surrogate_real
                ) and all(
                    value is not None
                    for path_values in surrogate_values
                    for value in path_values
                )
                if surrogate_finite:
                    assessment = assess_declared_relation(
                        _present(surrogate_real),
                        [_present(values) for values in surrogate_values],
                        declared_relation=str(spec["relation"]),
                        diagnostic_only=diagnostic_only,
                        minimum_direction_fraction=float(
                            eligibility["directional_relation_minimum_paired_block_fraction"]
                        ),
                        minimum_abs_effect_iqr=float(
                            eligibility[
                                "directional_relation_minimum_abs_median_effect_in_pooled_iqr_units"
                            ]
                        ),
                        maximum_abs_equivalence_effect_iqr=float(
                            eligibility[
                                "equivalence_maximum_abs_median_effect_in_pooled_iqr_units"
                            ]
                        ),
                    )
                else:
                    assessment = {
                        "status": "nonfinite_original_or_surrogate_estimate",
                        "passed": None if diagnostic_only else False,
                    }
                gate_used = not diagnostic_only
                gate_pass = bool(
                    gate_used
                    and original_finite
                    and surrogate_finite
                    and conformal_result.get("pass_both", False)
                    and assessment.get("passed") is True
                )
                cells[metric_name][symbol][str(length)] = {
                    "applicable": True,
                    "block_count_eligible": True,
                    "primary_gate_used": gate_used,
                    "primary_gate_pass": gate_pass if gate_used else None,
                    "original_all_gating_splits_finite": original_finite,
                    "surrogate_all_development_estimates_finite": surrogate_finite,
                    "real_estimates_by_split": real_estimates,
                    "real_errors_by_split": real_errors,
                    "conformal": conformal_result,
                    "surrogate": {
                        "kind": surrogate_kind,
                        "real_estimates": surrogate_real,
                        "control_estimates": surrogate_values,
                        "control_errors": surrogate_errors,
                        "assessment": assessment,
                    },
                }

        if diagnostic_only:
            metric_decisions[metric_name] = {
                "role": role,
                "applicable_symbols": applicable_symbols,
                "eligible_symbols": [],
                "minimum_eligible_symbols": None,
                "metric_eligible": None,
                "reason": "diagnostic_only_no_eligibility_decision",
            }
            continue
        eligible_symbols = [
            symbol
            for symbol in applicable_symbols
            if all(
                cells[metric_name][symbol][str(length)].get("primary_gate_pass") is True
                for length in metric_lengths
            )
        ]
        required = int(spec["minimum_eligible_symbols"])
        metric_decisions[metric_name] = {
            "role": role,
            "lengths": metric_lengths,
            "applicable_symbols": applicable_symbols,
            "eligible_symbols": eligible_symbols,
            "minimum_eligible_symbols": required,
            "metric_eligible": len(eligible_symbols) >= required,
        }
    required_core = [
        str(value)
        for value in cast(list[object], decision_contract["core_suite_required_metrics"])
    ]
    core_qualified = all(
        metric_decisions[name]["metric_eligible"] is True for name in required_core
    )
    return {
        "sealed_split_loaded": False,
        "block_inventory": inventory,
        "block_count_eligible": {
            symbol: {str(length): passed for length, passed in by_length.items()}
            for symbol, by_length in block_eligible.items()
        },
        "volume_observable_applicable": volume_observable,
        "cells": cells,
        "metric_decisions": metric_decisions,
        "core_suite_required_metrics": required_core,
        "core_suite_qualified": core_qualified,
        "model_scoring_or_training_authorized": False,
    }


def _applicable_symbols(
    symbols: list[str],
    spec: dict[str, Any],
    *,
    volume_observable: dict[str, bool],
) -> list[str]:
    scope = str(spec["scope"])
    if scope == "all_symbols":
        return symbols
    explicit = [str(value) for value in cast(list[object], spec.get("symbols", []))]
    if scope == "equity_indices_only":
        return [symbol for symbol in symbols if symbol in explicit]
    if scope == "volume_etfs_only":
        return [
            symbol
            for symbol in symbols
            if symbol in explicit and volume_observable[symbol]
        ]
    raise ValueError(f"unknown metric scope: {scope}")


def _mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return cast(dict[str, Any], value)


def _present(values: list[float | None]) -> list[float]:
    if any(value is None for value in values):
        raise ValueError("expected every estimate to be present")
    return [float(value) for value in values if value is not None]


__all__ = ["evaluate_fresh_market_confirmation"]
