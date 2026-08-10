"""Result-blind finite-sample qualification primitives for evaluator v2."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from typing import Any, Literal, cast

import numpy as np
import numpy.typing as npt

from .stylized_facts import (
    acf_squared_returns,
    aggregational_gaussianity,
    autocorr_returns,
    conditional_kurtosis,
    dfa_hurst,
    gain_loss_asymmetry,
    hill_tail_index,
    intermittency_fano,
    leverage_effect,
    volume_volatility_corr,
    zumbach_asymmetry,
)

ArrayF = npt.NDArray[np.float64]
Relation = Literal["real_higher", "real_lower", "equivalent"]
SurrogateKind = Literal[
    "temporal_joint_permutation",
    "sign_randomization",
    "volume_alignment_break",
    "gaussian_iid",
]

METRIC_NAMES = (
    "autocorr_returns",
    "hill_tail_index",
    "gain_loss_asymmetry",
    "aggregational_gaussianity",
    "intermittency_fano",
    "acf_squared_returns",
    "conditional_kurtosis",
    "dfa_hurst_abs_r",
    "leverage_effect",
    "volume_volatility_corr",
    "zumbach_asymmetry",
)
GATING_SPLITS = (
    "reference",
    "conformal_calibration",
    "confirmation",
    "temporal_test",
)


@dataclass(frozen=True)
class SplitSeries:
    """Aligned returns and observables for one symbol/time split."""

    returns: ArrayF
    volume: ArrayF | None


@dataclass(frozen=True)
class SeriesBlock:
    """One non-overlapping evaluation block."""

    returns: ArrayF
    volume: ArrayF | None


@dataclass(frozen=True)
class ConformalResult:
    status: str
    center: float | None
    radius: float | None
    alpha: float
    calibration_order_index: int
    reference_blocks: int
    calibration_blocks: int
    confirmation_blocks: int
    temporal_blocks: int
    report_only_blocks: int
    confirmation_coverage: float | None
    temporal_coverage: float | None
    report_only_coverage: float | None
    confirmation_pass: bool
    temporal_pass: bool
    pass_both: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RelationResult:
    status: str
    relation: Relation
    paired_blocks: int
    replicates_per_block: int
    direction_fraction: float | None
    median_raw_effect: float | None
    pooled_iqr: float | None
    median_effect_pooled_iqr_units: float | None
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_nonoverlapping_blocks(
    returns: npt.ArrayLike,
    volume: npt.ArrayLike | None,
    length: int,
) -> tuple[SeriesBlock, ...]:
    """Build sequential blocks and drop the final remainder."""
    if length <= 0:
        raise ValueError("block length must be positive")
    r = _finite_vector(returns, "returns")
    v = None if volume is None else _finite_vector(volume, "volume")
    if v is not None and v.size != r.size:
        raise ValueError(f"returns/volume length mismatch: {r.size}!={v.size}")
    count = r.size // length
    return tuple(
        SeriesBlock(
            returns=r[index * length : (index + 1) * length].copy(),
            volume=None
            if v is None
            else v[index * length : (index + 1) * length].copy(),
        )
        for index in range(count)
    )


def finite_sample_order_index(n_calibration_blocks: int, alpha: float) -> int:
    """Return the one-indexed split-conformal finite-sample order statistic."""
    if n_calibration_blocks < 0:
        raise ValueError("n_calibration_blocks must be non-negative")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    return math.ceil((n_calibration_blocks + 1) * (1.0 - alpha))


def split_conformal_interval(
    reference: Sequence[float],
    calibration: Sequence[float],
    confirmation: Sequence[float],
    temporal: Sequence[float],
    report_only: Sequence[float],
    *,
    alpha: float,
    minimum_confirmation_coverage: float,
    minimum_temporal_coverage: float,
) -> ConformalResult:
    """Fit a median-centered interval and evaluate independent time coverage."""
    ref = _finite_sequence(reference, "reference")
    cal = _finite_sequence(calibration, "calibration")
    conf = _finite_sequence(confirmation, "confirmation")
    temp = _finite_sequence(temporal, "temporal")
    report = _finite_sequence(report_only, "report_only")
    k = finite_sample_order_index(len(cal), alpha)
    if not ref or not cal or not conf or not temp:
        return ConformalResult(
            status="insufficient_required_blocks",
            center=None,
            radius=None,
            confirmation_coverage=None,
            temporal_coverage=None,
            report_only_coverage=None,
            confirmation_pass=False,
            temporal_pass=False,
            pass_both=False,
            alpha=alpha,
            calibration_order_index=k,
            reference_blocks=len(ref),
            calibration_blocks=len(cal),
            confirmation_blocks=len(conf),
            temporal_blocks=len(temp),
            report_only_blocks=len(report),
        )
    if k > len(cal):
        return ConformalResult(
            status="finite_sample_order_exceeds_calibration_blocks",
            center=None,
            radius=None,
            confirmation_coverage=None,
            temporal_coverage=None,
            report_only_coverage=None,
            confirmation_pass=False,
            temporal_pass=False,
            pass_both=False,
            alpha=alpha,
            calibration_order_index=k,
            reference_blocks=len(ref),
            calibration_blocks=len(cal),
            confirmation_blocks=len(conf),
            temporal_blocks=len(temp),
            report_only_blocks=len(report),
        )
    center = float(np.median(ref))
    scores = np.sort(np.abs(np.asarray(cal, dtype=np.float64) - center))
    radius = float(scores[k - 1])
    confirmation_coverage = _coverage(conf, center, radius)
    temporal_coverage = _coverage(temp, center, radius)
    report_coverage = _coverage(report, center, radius) if report else None
    confirmation_pass = confirmation_coverage >= minimum_confirmation_coverage
    temporal_pass = temporal_coverage >= minimum_temporal_coverage
    return ConformalResult(
        status="ok",
        center=center,
        radius=radius,
        confirmation_coverage=confirmation_coverage,
        temporal_coverage=temporal_coverage,
        report_only_coverage=report_coverage,
        confirmation_pass=confirmation_pass,
        temporal_pass=temporal_pass,
        pass_both=confirmation_pass and temporal_pass,
        alpha=alpha,
        calibration_order_index=k,
        reference_blocks=len(ref),
        calibration_blocks=len(cal),
        confirmation_blocks=len(conf),
        temporal_blocks=len(temp),
        report_only_blocks=len(report),
    )


def deterministic_seed(root_seed: int, *parts: object) -> int:
    """Derive a stable NumPy seed without depending on process hash randomization."""
    encoded = "|".join([str(root_seed), *(str(part) for part in parts)]).encode()
    return int.from_bytes(hashlib.sha256(encoded).digest()[:8], "little", signed=False)


def make_surrogate(
    block: SeriesBlock,
    kind: SurrogateKind,
    *,
    seed: int,
) -> SeriesBlock:
    """Generate one frozen surrogate while preserving declared invariants."""
    rng = np.random.default_rng(seed)
    r = block.returns
    v = block.volume
    if kind == "temporal_joint_permutation":
        permutation = rng.permutation(r.size)
        return SeriesBlock(
            returns=r[permutation].copy(),
            volume=None if v is None else v[permutation].copy(),
        )
    if kind == "sign_randomization":
        signs = rng.choice(np.asarray([-1.0, 1.0]), size=r.size)
        return SeriesBlock(
            returns=(r * signs).astype(np.float64, copy=False),
            volume=None if v is None else v.copy(),
        )
    if kind == "volume_alignment_break":
        if v is None:
            raise ValueError("volume_alignment_break requires volume")
        if v.size < 2:
            raise ValueError("volume_alignment_break requires at least two observations")
        shift = int(rng.integers(1, v.size))
        return SeriesBlock(returns=r.copy(), volume=np.roll(v, shift).copy())
    if kind == "gaussian_iid":
        mean = float(np.mean(r))
        std = float(np.std(r, ddof=0))
        if std == 0.0:
            gaussian = np.full(r.size, mean, dtype=np.float64)
        else:
            standard = rng.normal(size=r.size)
            standard = (standard - standard.mean()) / standard.std(ddof=0)
            gaussian = np.asarray(mean + std * standard, dtype=np.float64)
        shuffled_volume = None if v is None else v[rng.permutation(v.size)].copy()
        return SeriesBlock(returns=gaussian, volume=shuffled_volume)
    raise ValueError(f"unknown surrogate kind: {kind}")


def assess_relation(
    real: Sequence[float],
    controls: Sequence[Sequence[float]],
    *,
    relation: Relation,
    minimum_direction_fraction: float,
    minimum_abs_effect_iqr: float,
    maximum_abs_equivalence_effect_iqr: float,
) -> RelationResult:
    """Assess paired block effects against a primary surrogate family."""
    real_values = _finite_sequence(real, "real")
    if len(real_values) != len(controls) or not real_values:
        raise ValueError("real and controls must contain the same positive block count")
    control_values = [_finite_sequence(values, "controls") for values in controls]
    replicate_counts = {len(values) for values in control_values}
    if len(replicate_counts) != 1 or 0 in replicate_counts:
        raise ValueError("each real block must have the same positive surrogate count")
    control_medians = np.asarray([np.median(values) for values in control_values])
    effects = np.asarray(real_values, dtype=np.float64) - control_medians
    pooled = np.asarray(
        [*real_values, *(value for values in control_values for value in values)],
        dtype=np.float64,
    )
    q25, q75 = np.quantile(pooled, [0.25, 0.75])
    pooled_iqr = float(q75 - q25)
    raw_effect = float(np.median(effects))
    replicates = replicate_counts.pop()
    if not np.isfinite(pooled_iqr) or pooled_iqr <= 0.0:
        return RelationResult(
            status="nonpositive_pooled_iqr",
            relation=relation,
            paired_blocks=len(real_values),
            replicates_per_block=replicates,
            direction_fraction=None,
            median_raw_effect=raw_effect,
            pooled_iqr=pooled_iqr,
            median_effect_pooled_iqr_units=None,
            passed=False,
        )
    standardized = raw_effect / pooled_iqr
    if relation == "real_higher":
        direction_fraction = float(np.mean(effects > 0.0))
        passed = (
            direction_fraction >= minimum_direction_fraction
            and standardized >= minimum_abs_effect_iqr
        )
    elif relation == "real_lower":
        direction_fraction = float(np.mean(effects < 0.0))
        passed = (
            direction_fraction >= minimum_direction_fraction
            and standardized <= -minimum_abs_effect_iqr
        )
    elif relation == "equivalent":
        direction_fraction = None
        passed = abs(standardized) <= maximum_abs_equivalence_effect_iqr
    else:
        raise ValueError(f"unknown relation: {relation}")
    return RelationResult(
        status="ok",
        relation=relation,
        paired_blocks=len(real_values),
        replicates_per_block=replicates,
        direction_fraction=direction_fraction,
        median_raw_effect=raw_effect,
        pooled_iqr=pooled_iqr,
        median_effect_pooled_iqr_units=standardized,
        passed=passed,
    )


def assess_declared_relation(
    real: Sequence[float],
    controls: Sequence[Sequence[float]],
    *,
    declared_relation: str,
    diagnostic_only: bool,
    minimum_direction_fraction: float,
    minimum_abs_effect_iqr: float,
    maximum_abs_equivalence_effect_iqr: float,
) -> dict[str, Any]:
    """Keep report-only relations outside the eligibility relation algebra."""
    if diagnostic_only:
        if declared_relation != "report_no_eligibility_decision":
            raise ValueError("diagnostic metric must declare report-only relation semantics")
        real_values = _finite_sequence(real, "real")
        control_values = [_finite_sequence(values, "controls") for values in controls]
        if len(real_values) != len(control_values) or not real_values:
            raise ValueError("diagnostic real/control block count mismatch")
        replicate_counts = {len(values) for values in control_values}
        if len(replicate_counts) != 1 or 0 in replicate_counts:
            raise ValueError("diagnostic controls need equal positive replicate counts")
        return {
            "status": "diagnostic_only_no_eligibility_relation",
            "declared_relation": declared_relation,
            "paired_blocks": len(real_values),
            "replicates_per_block": replicate_counts.pop(),
            "passed": None,
        }
    if declared_relation not in {"real_higher", "real_lower", "equivalent"}:
        raise ValueError(f"unknown eligibility relation: {declared_relation}")
    return assess_relation(
        real,
        controls,
        relation=cast(Relation, declared_relation),
        minimum_direction_fraction=minimum_direction_fraction,
        minimum_abs_effect_iqr=minimum_abs_effect_iqr,
        maximum_abs_equivalence_effect_iqr=maximum_abs_equivalence_effect_iqr,
    ).to_dict()


def estimate_metric(name: str, block: SeriesBlock) -> float:
    """Compute one scalar under the unchanged legacy estimator semantics."""
    r = block.returns
    if name == "autocorr_returns":
        estimate = autocorr_returns(r).estimate
    elif name == "hill_tail_index":
        estimate = hill_tail_index(r, side="both").estimate
    elif name == "gain_loss_asymmetry":
        estimate = gain_loss_asymmetry(r).estimate
    elif name == "aggregational_gaussianity":
        estimate = aggregational_gaussianity(r).estimate
    elif name == "intermittency_fano":
        estimate = intermittency_fano(r).estimate
    elif name == "acf_squared_returns":
        estimate = acf_squared_returns(r).estimate
    elif name == "conditional_kurtosis":
        estimate = conditional_kurtosis(r).estimate
    elif name == "dfa_hurst_abs_r":
        estimate = dfa_hurst(np.abs(r)).estimate
    elif name == "leverage_effect":
        estimate = leverage_effect(r).estimate
    elif name == "volume_volatility_corr":
        if block.volume is None:
            raise ValueError("volume_volatility_corr requires aligned volume")
        estimate = volume_volatility_corr(r, block.volume).estimate
    elif name == "zumbach_asymmetry":
        estimate = zumbach_asymmetry(r).estimate
    else:
        raise ValueError(f"unsupported metric: {name}")
    if not np.isfinite(estimate):
        raise ValueError(f"{name} produced a non-finite estimate")
    return float(estimate)


def safe_estimate(name: str, block: SeriesBlock) -> tuple[float | None, str | None]:
    """Return a scalar or a stable error string without hiding estimator failure."""
    try:
        return estimate_metric(name, block), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def evaluate_feasibility(
    series_by_symbol: dict[str, dict[str, SplitSeries]],
    protocol: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate every frozen metric cell without reading the sealed split."""
    data_contract = cast(dict[str, Any], protocol["data"])
    blocking = cast(dict[str, Any], protocol["blocking"])
    conformal = cast(dict[str, Any], protocol["conformal"])
    surrogate_contract = cast(dict[str, Any], protocol["surrogates"])
    metric_contract = cast(dict[str, dict[str, Any]], protocol["metric_contract"])
    eligibility = cast(dict[str, Any], protocol["eligibility"])
    symbols = [str(symbol) for symbol in data_contract["symbols"]]
    lengths = [int(length) for length in blocking["lengths"]]
    primary_lengths = {int(length) for length in blocking["primary_lengths"]}
    generation_splits = [str(name) for name in surrogate_contract["generation_splits"]]
    replicates = int(surrogate_contract["replicates_per_real_block"])
    root_seed = int(surrogate_contract["root_seed"])
    if tuple(metric_contract) != METRIC_NAMES:
        raise ValueError("metric contract order/content differs from the frozen 11-metric registry")
    if tuple(str(name) for name in eligibility["original_finiteness_splits"]) != GATING_SPLITS:
        raise ValueError("original-finiteness split registry differs from the implementation")
    if eligibility["paired_effect"] != (
        "real_estimate_minus_within_block_surrogate_median"
    ):
        raise ValueError("paired-effect definition differs from the implementation")
    if eligibility["pooled_iqr_population"] != (
        "all_real_and_all_surrogate_replicate_estimates"
    ):
        raise ValueError("pooled-IQR population differs from the implementation")
    if eligibility["pooled_iqr_quantile_method"] != "numpy_linear":
        raise ValueError("pooled-IQR quantile method differs from the implementation")
    if "sealed_crash" in {split for splits in series_by_symbol.values() for split in splits}:
        raise ValueError("sealed_crash must never be loaded into evaluator-v2")

    block_map: dict[str, dict[str, dict[int, tuple[SeriesBlock, ...]]]] = {}
    inventory: dict[str, dict[str, dict[str, int]]] = {}
    volume_applicable: dict[str, bool] = {}
    for symbol in symbols:
        split_series = series_by_symbol[symbol]
        missing = sorted(set(GATING_SPLITS) - set(split_series))
        if missing:
            raise ValueError(f"{symbol} lacks gating splits: {missing}")
        block_map[symbol] = {}
        inventory[symbol] = {}
        gate_volumes: list[ArrayF] = []
        for split_name, split in split_series.items():
            block_map[symbol][split_name] = {}
            inventory[symbol][split_name] = {}
            for length in lengths:
                blocks = build_nonoverlapping_blocks(split.returns, split.volume, length)
                block_map[symbol][split_name][length] = blocks
                inventory[symbol][split_name][str(length)] = len(blocks)
            if split_name in GATING_SPLITS and split.volume is not None:
                gate_volumes.append(split.volume)
        if len(gate_volumes) != len(GATING_SPLITS):
            volume_applicable[symbol] = False
        else:
            joined = np.concatenate(gate_volumes)
            volume_applicable[symbol] = bool(
                np.all(np.isfinite(joined)) and np.ptp(joined) > 0.0
            )

    cells: dict[str, dict[str, dict[str, Any]]] = {name: {} for name in metric_contract}
    metric_decisions: dict[str, dict[str, Any]] = {}
    for metric_name, spec in metric_contract.items():
        scope = str(spec["scope"])
        applicable_symbols = _applicable_symbols(
            symbols,
            scope=scope,
            explicit_symbols=[str(value) for value in spec.get("symbols", [])],
            volume_applicable=volume_applicable,
        )
        for symbol in symbols:
            cells[metric_name][symbol] = {}
            for length in lengths:
                if symbol not in applicable_symbols:
                    cells[metric_name][symbol][str(length)] = {
                        "applicable": False,
                        "reason": "outside_metric_scope_or_missing_observable",
                        "primary_gate_used": False,
                    }
                    continue
                real_estimates: dict[str, list[float | None]] = {}
                real_errors: dict[str, list[str | None]] = {}
                for split_name, length_blocks in block_map[symbol].items():
                    values: list[float | None] = []
                    errors: list[str | None] = []
                    for block in length_blocks[length]:
                        value, error = safe_estimate(metric_name, block)
                        values.append(value)
                        errors.append(error)
                    real_estimates[split_name] = values
                    real_errors[split_name] = errors

                original_finite = all(
                    value is not None
                    for split_name in GATING_SPLITS
                    for value in real_estimates[split_name]
                ) and all(real_estimates[split_name] for split_name in GATING_SPLITS)
                conformal_result: dict[str, Any]
                if original_finite:
                    conformal_result = split_conformal_interval(
                        _present(real_estimates["reference"]),
                        _present(real_estimates["conformal_calibration"]),
                        _present(real_estimates["confirmation"]),
                        _present(real_estimates["temporal_test"]),
                        _present(real_estimates.get("report_only_guard", [])),
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
                        "status": "nonfinite_or_missing_original_estimate",
                        "pass_both": False,
                    }

                surrogate_values: list[list[float | None]] = []
                surrogate_errors: list[list[str | None]] = []
                surrogate_real: list[float | None] = []
                surrogate_kind = cast(SurrogateKind, str(spec["primary_surrogate"]))
                for split_name in generation_splits:
                    for block_index, block in enumerate(block_map[symbol][split_name][length]):
                        real_index_value = real_estimates[split_name][block_index]
                        surrogate_real.append(real_index_value)
                        block_values: list[float | None] = []
                        block_errors: list[str | None] = []
                        for replicate in range(replicates):
                            seed = deterministic_seed(
                                root_seed,
                                symbol,
                                split_name,
                                length,
                                block_index,
                                surrogate_kind,
                                replicate,
                            )
                            try:
                                control = make_surrogate(block, surrogate_kind, seed=seed)
                                value, error = safe_estimate(metric_name, control)
                            except Exception as exc:
                                value, error = None, f"{type(exc).__name__}: {exc}"
                            block_values.append(value)
                            block_errors.append(error)
                        surrogate_values.append(block_values)
                        surrogate_errors.append(block_errors)
                surrogate_finite = bool(surrogate_real) and all(
                    value is not None for value in surrogate_real
                ) and all(
                    value is not None
                    for block_values in surrogate_values
                    for value in block_values
                )
                diagnostic_only = scope == "diagnostic_only_at_daily_frequency"
                if surrogate_finite:
                    relation_result = assess_declared_relation(
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
                    relation_result = {
                        "status": "nonfinite_or_missing_original_or_surrogate_estimate",
                        "passed": None if diagnostic_only else False,
                    }
                primary_gate_used = length in primary_lengths and not diagnostic_only
                gate_pass = bool(
                    primary_gate_used
                    and original_finite
                    and surrogate_finite
                    and conformal_result.get("pass_both", False)
                    and relation_result.get("passed", False)
                )
                cells[metric_name][symbol][str(length)] = {
                    "applicable": True,
                    "primary_gate_used": primary_gate_used,
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
                        "assessment": relation_result,
                    },
                    "primary_gate_pass": gate_pass,
                }

        if scope == "diagnostic_only_at_daily_frequency":
            metric_decisions[metric_name] = {
                "scope": scope,
                "applicable_symbols": applicable_symbols,
                "eligible_symbols": [],
                "required_eligible_symbols": None,
                "metric_eligible": None,
                "reason": "diagnostic_only_no_eligibility_decision",
            }
            continue
        eligible_symbols = [
            symbol
            for symbol in applicable_symbols
            if all(
                bool(cells[metric_name][symbol][str(length)]["primary_gate_pass"])
                for length in primary_lengths
            )
        ]
        if scope == "equity_indices_only":
            required_symbols = int(
                eligibility["minimum_eligible_symbols_for_equity_only_metric"]
            )
        elif scope == "symbols_with_finite_nonconstant_volume":
            required_symbols = int(
                eligibility["minimum_eligible_symbols_for_volume_metric"]
            )
        else:
            required_symbols = int(
                eligibility["minimum_eligible_symbols_for_all_symbol_metric"]
            )
        metric_decisions[metric_name] = {
            "scope": scope,
            "applicable_symbols": applicable_symbols,
            "eligible_symbols": eligible_symbols,
            "required_eligible_symbols": required_symbols,
            "metric_eligible": len(eligible_symbols) >= required_symbols,
            "requires_every_applicable_primary_length": True,
        }

    return {
        "sealed_split_loaded": False,
        "block_inventory": inventory,
        "volume_observable_applicable": volume_applicable,
        "cells": cells,
        "metric_decisions": metric_decisions,
        "eligible_metric_names": [
            name
            for name, decision in metric_decisions.items()
            if decision["metric_eligible"] is True
        ],
    }


def _applicable_symbols(
    symbols: list[str],
    *,
    scope: str,
    explicit_symbols: list[str],
    volume_applicable: dict[str, bool],
) -> list[str]:
    if scope in {"all_symbols", "diagnostic_only_at_daily_frequency"}:
        return symbols
    if scope == "equity_indices_only":
        if not explicit_symbols:
            raise ValueError("equity_indices_only requires explicit symbols")
        return [symbol for symbol in symbols if symbol in explicit_symbols]
    if scope == "symbols_with_finite_nonconstant_volume":
        return [symbol for symbol in symbols if volume_applicable[symbol]]
    raise ValueError(f"unknown metric scope: {scope}")


def _finite_vector(values: npt.ArrayLike, name: str) -> ArrayF:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    return array


def _finite_sequence(values: Sequence[float], name: str) -> list[float]:
    converted = [float(value) for value in values]
    if not all(np.isfinite(value) for value in converted):
        raise ValueError(f"{name} contains a non-finite value")
    return converted


def _present(values: Sequence[float | None]) -> list[float]:
    if any(value is None for value in values):
        raise ValueError("expected every estimate to be present")
    return [float(value) for value in values if value is not None]


def _coverage(values: Sequence[float], center: float, radius: float) -> float:
    array = np.asarray(values, dtype=np.float64)
    return float(np.mean(np.abs(array - center) <= radius))


__all__ = [
    "GATING_SPLITS",
    "METRIC_NAMES",
    "ConformalResult",
    "RelationResult",
    "SeriesBlock",
    "SplitSeries",
    "assess_declared_relation",
    "assess_relation",
    "build_nonoverlapping_blocks",
    "deterministic_seed",
    "estimate_metric",
    "evaluate_feasibility",
    "finite_sample_order_index",
    "make_surrogate",
    "safe_estimate",
    "split_conformal_interval",
]
