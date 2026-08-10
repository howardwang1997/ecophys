"""Exploratory lagged-regime tests for real-market volatility memory."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, cast

import numpy as np
import numpy.typing as npt

from ecomd.data.yfinance_provenance import sha256_float64
from ecomd.eval.evaluator_v2 import deterministic_seed
from ecomd.eval.stylized_facts import (
    acf_squared_returns,
    autocorr_returns,
    volume_volatility_corr,
)

ArrayF = npt.NDArray[np.float64]


@dataclass(frozen=True)
class HalfYearBlock:
    """One exact-length return/volume block contained in a calendar half-year."""

    symbol: str
    period: str
    returns: ArrayF
    volume: ArrayF


@dataclass(frozen=True)
class RegimeRow:
    """One previsible-regime predictor and its next-period targets."""

    symbol: str
    period: str
    era: str
    lagged_log_realized_volatility: float
    targets: dict[str, float]


@dataclass(frozen=True)
class _TargetCell:
    symbol: str
    period: str
    era: str
    predictor: float
    target: float


def period_key(year: int, half: int) -> str:
    """Return the canonical calendar-half identifier."""
    if year < 1 or half not in (1, 2):
        raise ValueError("year must be positive and half must be 1 or 2")
    return f"{year:04d}H{half}"


def previous_period(period: str) -> str:
    """Return the immediately preceding calendar half-year."""
    year, half = _parse_period(period)
    return period_key(year, 1) if half == 2 else period_key(year - 1, 2)


def expand_period_range(bounds: list[object]) -> tuple[str, ...]:
    """Expand two inclusive canonical half-year bounds."""
    if len(bounds) != 2:
        raise ValueError("period bounds must contain exactly two entries")
    start = _period_ordinal(str(bounds[0]))
    end = _period_ordinal(str(bounds[1]))
    if end < start:
        raise ValueError("period range end precedes start")
    return tuple(_period_from_ordinal(value) for value in range(start, end + 1))


def make_half_year_block(
    symbol: str,
    period: str,
    prices: npt.ArrayLike,
    volume: npt.ArrayLike,
    *,
    return_length: int,
) -> HalfYearBlock:
    """Take the earliest rows in one half-year and construct an exact block."""
    if return_length < 101:
        raise ValueError("return_length must exceed the estimator max lag")
    p = _finite_vector(prices, "prices")
    v = _finite_vector(volume, "volume")
    required = return_length + 1
    if p.size != v.size:
        raise ValueError("price and volume arrays must align")
    if p.size < required:
        raise ValueError(f"{symbol}/{period} has {p.size - 1} returns, needs {return_length}")
    selected_prices = p[:required]
    if np.any(selected_prices <= 0.0):
        raise ValueError("prices must be strictly positive")
    returns = np.diff(np.log(selected_prices)).astype(np.float64, copy=False)
    aligned_volume = v[1:required].astype(np.float64, copy=True)
    if returns.size != return_length or aligned_volume.size != return_length:
        raise RuntimeError("half-year block construction produced the wrong length")
    return HalfYearBlock(
        symbol=symbol,
        period=period,
        returns=returns,
        volume=aligned_volume,
    )


def build_regime_rows(
    blocks_by_symbol: dict[str, dict[str, HalfYearBlock]],
    protocol: dict[str, Any],
) -> tuple[RegimeRow, ...]:
    """Measure frozen targets using only the immediately prior regime block."""
    data = _mapping(protocol["data"], "data")
    periods = _mapping(protocol["periods"], "periods")
    balanced_symbols = [str(value) for value in cast(list[object], data["balanced_symbols"])]
    volume_symbols = {str(value) for value in cast(list[object], data["volume_symbols"])}
    eras = {
        "fit": expand_period_range(cast(list[object], periods["fit_target_period"])),
        "evaluation_1": expand_period_range(
            cast(list[object], periods["first_evaluation_period"])
        ),
        "evaluation_2": expand_period_range(
            cast(list[object], periods["second_evaluation_period"])
        ),
    }
    expected_counts = {
        "fit": int(periods["expected_fit_calendar_clusters"]),
        "evaluation_1": int(periods["expected_first_evaluation_calendar_clusters"]),
        "evaluation_2": int(periods["expected_second_evaluation_calendar_clusters"]),
    }
    for era, declared in eras.items():
        if len(declared) != expected_counts[era]:
            raise ValueError(f"{era} period count differs from the contract")
    if set(blocks_by_symbol) != set(balanced_symbols):
        raise ValueError("loaded symbol set differs from balanced_symbols")

    rows: list[RegimeRow] = []
    for era, target_periods in eras.items():
        for period in target_periods:
            predecessor = previous_period(period)
            if predecessor.startswith("2020"):
                raise ValueError("a target period depends on the sealed year")
            for symbol in balanced_symbols:
                symbol_blocks = blocks_by_symbol[symbol]
                if period not in symbol_blocks or predecessor not in symbol_blocks:
                    raise ValueError(f"missing target/predecessor block for {symbol}/{period}")
                prior = symbol_blocks[predecessor]
                target = symbol_blocks[period]
                realized_variance = float(np.mean(np.square(prior.returns)))
                if not np.isfinite(realized_variance) or realized_variance <= 0.0:
                    raise ValueError(f"invalid lagged realized variance for {symbol}/{period}")
                measured = {
                    "acf_squared_returns": float(
                        acf_squared_returns(target.returns).estimate
                    ),
                    "autocorr_returns": float(autocorr_returns(target.returns).estimate),
                }
                if symbol in volume_symbols:
                    measured["volume_volatility_corr"] = float(
                        volume_volatility_corr(target.returns, target.volume).estimate
                    )
                if not all(np.isfinite(value) for value in measured.values()):
                    raise ValueError(f"nonfinite target for {symbol}/{period}")
                rows.append(
                    RegimeRow(
                        symbol=symbol,
                        period=period,
                        era=era,
                        lagged_log_realized_volatility=0.5 * math.log(realized_variance),
                        targets=measured,
                    )
                )
    return tuple(rows)


def evaluate_regime_memory(
    rows: tuple[RegimeRow, ...],
    protocol: dict[str, Any],
) -> dict[str, Any]:
    """Fit frozen models, preserve calendar dependence, and apply nomination gates."""
    data = _mapping(protocol["data"], "data")
    targets = _mapping(protocol["targets"], "targets")
    model_contract = _mapping(protocol["models"], "models")
    if model_contract["inference_unit"] != "calendar_half_year_cluster_not_symbol_cell":
        raise ValueError("inference unit differs from implementation")
    balanced_symbols = [str(value) for value in cast(list[object], data["balanced_symbols"])]
    volume_symbols = [str(value) for value in cast(list[object], data["volume_symbols"])]
    target_symbols = {
        "acf_squared_returns": balanced_symbols,
        "volume_volatility_corr": volume_symbols,
        "autocorr_returns": balanced_symbols,
    }
    if set(targets) != set(target_symbols):
        raise ValueError("target registry differs from implementation")
    normalized, normalization = _normalize_predictors(rows, balanced_symbols)
    results: dict[str, Any] = {}
    for target_name, symbols in target_symbols.items():
        cells = _target_cells(rows, normalized, target_name, symbols)
        results[target_name] = _evaluate_target(
            target_name,
            cells,
            symbols,
            protocol,
        )

    primary = _mapping(results["acf_squared_returns"], "primary result")
    summary = _mapping(primary["summary"], "primary summary")
    eras = _mapping(primary["eras"], "primary eras")
    permutation = _mapping(primary["permutation_test"], "primary permutation")
    bootstrap = _mapping(primary["cluster_bootstrap"], "primary bootstrap")
    gate = _mapping(protocol["primary_nomination_gate"], "primary_nomination_gate")
    clauses = {
        "training_common_slope_strictly_positive": float(
            primary["training_common_regime_slope"]
        )
        > 0.0,
        "pooled_relative_mse_reduction_minimum": float(
            summary["relative_mse_reduction"]
        )
        >= float(gate["pooled_relative_mse_reduction_minimum"]),
        "pooled_mae_reduction_strictly_positive": float(summary["mae_reduction"])
        > 0.0,
        "first_evaluation_mse_reduction_strictly_positive": float(
            _mapping(eras["evaluation_1"], "evaluation_1")["relative_mse_reduction"]
        )
        > 0.0,
        "second_evaluation_mse_reduction_strictly_positive": float(
            _mapping(eras["evaluation_2"], "evaluation_2")["relative_mse_reduction"]
        )
        > 0.0,
        "calendar_cluster_wins_minimum_of_17": int(primary["calendar_cluster_wins"])
        >= int(gate["calendar_cluster_wins_minimum_of_17"]),
        "symbol_wins_minimum_of_11": int(primary["symbol_wins"])
        >= int(gate["symbol_wins_minimum_of_11"]),
        "permutation_p_maximum": float(permutation["p_value"])
        <= float(gate["permutation_p_maximum"]),
        "cluster_bootstrap_90pct_lower_relative_mse_reduction_strictly_positive": float(
            bootstrap["ci_low"]
        )
        > 0.0,
    }
    primary_nominated = all(clauses.values())
    return {
        "normalization": normalization,
        "targets": results,
        "primary_gate_clauses": clauses,
        "primary_nominated": primary_nominated,
        "decision": (
            protocol["decision"]["pass"]
            if primary_nominated
            else protocol["decision"]["fail"]
        ),
        "paper_claim_or_model_training_authorized": False,
        "sealed_year_loaded": False,
    }


def _evaluate_target(
    target_name: str,
    cells: tuple[_TargetCell, ...],
    symbols: list[str],
    protocol: dict[str, Any],
) -> dict[str, Any]:
    train = tuple(cell for cell in cells if cell.era == "fit")
    evaluation = tuple(cell for cell in cells if cell.era != "fit")
    if not train or not evaluation:
        raise ValueError("target lacks fit or evaluation cells")
    baseline_coefficients, _ = _fit_fixed_effects(train, symbols, include_regime=False)
    regime_coefficients, slope = _fit_fixed_effects(train, symbols, include_regime=True)
    y, baseline_prediction, regime_prediction = _predictions(
        evaluation,
        symbols,
        baseline_coefficients,
        regime_coefficients,
        slope,
    )
    summary = _losses(y, baseline_prediction, regime_prediction)
    era_summaries: dict[str, dict[str, float]] = {}
    for era in ("evaluation_1", "evaluation_2"):
        mask = np.asarray([cell.era == era for cell in evaluation], dtype=np.bool_)
        era_summaries[era] = _losses(
            y[mask], baseline_prediction[mask], regime_prediction[mask]
        )
    period_losses = _group_losses(
        evaluation,
        y,
        baseline_prediction,
        regime_prediction,
        group="period",
    )
    symbol_losses = _group_losses(
        evaluation,
        y,
        baseline_prediction,
        regime_prediction,
        group="symbol",
    )
    surrogate_contract = _mapping(protocol["surrogate_test"], "surrogate_test")
    surrogate_values = _permutation_distribution(
        target_name,
        train,
        evaluation,
        symbols,
        baseline_coefficients,
        replicates=int(surrogate_contract["replicates"]),
        root_seed=int(surrogate_contract["root_seed"]),
    )
    real_statistic = float(summary["relative_mse_reduction"])
    exceedances = int(np.sum(surrogate_values >= real_statistic))
    permutation_p = (1.0 + exceedances) / (surrogate_values.size + 1.0)
    bootstrap_contract = _mapping(protocol["cluster_bootstrap"], "cluster_bootstrap")
    bootstrap_values = _cluster_bootstrap_distribution(
        evaluation,
        y,
        baseline_prediction,
        regime_prediction,
        replicates=int(bootstrap_contract["replicates"]),
        root_seed=deterministic_seed(
            int(bootstrap_contract["root_seed"]), target_name
        ),
    )
    confidence = float(bootstrap_contract["confidence_level"])
    tail = (1.0 - confidence) / 2.0
    ci_low, ci_high = np.quantile(bootstrap_values, [tail, 1.0 - tail])
    cell_output = [
        {
            "symbol": cell.symbol,
            "period": cell.period,
            "era": cell.era,
            "normalized_lagged_log_realized_volatility": cell.predictor,
            "target": cell.target,
            "baseline_prediction": float(baseline_prediction[index]),
            "regime_prediction": float(regime_prediction[index]),
        }
        for index, cell in enumerate(evaluation)
    ]
    return {
        "training_cells": len(train),
        "evaluation_cells": len(evaluation),
        "training_common_regime_slope": slope,
        "summary": summary,
        "eras": era_summaries,
        "calendar_cluster_losses": period_losses,
        "calendar_cluster_wins": sum(
            value["regime_mse"] < value["baseline_mse"]
            for value in period_losses.values()
        ),
        "symbol_losses": symbol_losses,
        "symbol_wins": sum(
            value["regime_mse"] < value["baseline_mse"]
            for value in symbol_losses.values()
        ),
        "permutation_test": {
            "replicates": int(surrogate_values.size),
            "exceedances_at_or_above_real": exceedances,
            "p_value": permutation_p,
            "distribution_sha256": sha256_float64(surrogate_values),
            "minimum": float(np.min(surrogate_values)),
            "median": float(np.median(surrogate_values)),
            "maximum": float(np.max(surrogate_values)),
        },
        "cluster_bootstrap": {
            "replicates": int(bootstrap_values.size),
            "confidence_level": confidence,
            "ci_low": float(ci_low),
            "median": float(np.median(bootstrap_values)),
            "ci_high": float(ci_high),
            "distribution_sha256": sha256_float64(bootstrap_values),
        },
        "evaluation_cells_detail": cell_output,
    }


def _normalize_predictors(
    rows: tuple[RegimeRow, ...], symbols: list[str]
) -> tuple[dict[tuple[str, str], float], dict[str, dict[str, float]]]:
    normalized: dict[tuple[str, str], float] = {}
    statistics: dict[str, dict[str, float]] = {}
    for symbol in symbols:
        fit_values = np.asarray(
            [
                row.lagged_log_realized_volatility
                for row in rows
                if row.symbol == symbol and row.era == "fit"
            ],
            dtype=np.float64,
        )
        if fit_values.size == 0 or not np.all(np.isfinite(fit_values)):
            raise ValueError(f"{symbol} lacks finite fit predictors")
        median = float(np.median(fit_values))
        q25, q75 = np.quantile(fit_values, [0.25, 0.75])
        iqr = float(q75 - q25)
        if not np.isfinite(iqr) or iqr <= 0.0:
            raise ValueError(f"{symbol} has a nonpositive fit predictor IQR")
        statistics[symbol] = {"fit_median": median, "fit_iqr": iqr}
        for row in rows:
            if row.symbol == symbol:
                normalized[(symbol, row.period)] = (
                    row.lagged_log_realized_volatility - median
                ) / iqr
    return normalized, statistics


def _target_cells(
    rows: tuple[RegimeRow, ...],
    normalized: dict[tuple[str, str], float],
    target_name: str,
    symbols: list[str],
) -> tuple[_TargetCell, ...]:
    cells = tuple(
        _TargetCell(
            symbol=row.symbol,
            period=row.period,
            era=row.era,
            predictor=normalized[(row.symbol, row.period)],
            target=float(row.targets[target_name]),
        )
        for row in rows
        if row.symbol in symbols and target_name in row.targets
    )
    expected_eras = {"fit", "evaluation_1", "evaluation_2"}
    if {cell.era for cell in cells} != expected_eras:
        raise ValueError(f"{target_name} lacks a required era")
    return cells


def _fit_fixed_effects(
    cells: tuple[_TargetCell, ...],
    symbols: list[str],
    *,
    include_regime: bool,
) -> tuple[ArrayF, float]:
    index = {symbol: position for position, symbol in enumerate(symbols)}
    design = np.zeros((len(cells), len(symbols) + int(include_regime)), dtype=np.float64)
    for row_index, cell in enumerate(cells):
        design[row_index, index[cell.symbol]] = 1.0
        if include_regime:
            design[row_index, -1] = cell.predictor
    target = np.asarray([cell.target for cell in cells], dtype=np.float64)
    coefficients, _, rank, _ = np.linalg.lstsq(design, target, rcond=None)
    if rank != design.shape[1] or not np.all(np.isfinite(coefficients)):
        raise ValueError("fixed-effect design is rank deficient or nonfinite")
    slope = float(coefficients[-1]) if include_regime else 0.0
    intercepts = coefficients[: len(symbols)].astype(np.float64, copy=True)
    return intercepts, slope


def _predictions(
    cells: tuple[_TargetCell, ...],
    symbols: list[str],
    baseline_intercepts: ArrayF,
    regime_intercepts: ArrayF,
    regime_slope: float,
    *,
    predictor_override: ArrayF | None = None,
) -> tuple[ArrayF, ArrayF, ArrayF]:
    index = {symbol: position for position, symbol in enumerate(symbols)}
    predictor = (
        np.asarray([cell.predictor for cell in cells], dtype=np.float64)
        if predictor_override is None
        else predictor_override
    )
    if predictor.size != len(cells):
        raise ValueError("predictor override has the wrong length")
    target = np.asarray([cell.target for cell in cells], dtype=np.float64)
    baseline = np.asarray(
        [baseline_intercepts[index[cell.symbol]] for cell in cells], dtype=np.float64
    )
    regime = np.asarray(
        [regime_intercepts[index[cell.symbol]] for cell in cells], dtype=np.float64
    ) + regime_slope * predictor
    return target, baseline, regime


def _losses(target: ArrayF, baseline: ArrayF, regime: ArrayF) -> dict[str, float]:
    if target.size == 0 or target.shape != baseline.shape or target.shape != regime.shape:
        raise ValueError("loss arrays must have one common positive shape")
    baseline_error = target - baseline
    regime_error = target - regime
    baseline_mse = float(np.mean(np.square(baseline_error)))
    regime_mse = float(np.mean(np.square(regime_error)))
    if baseline_mse <= 0.0 or not np.isfinite(baseline_mse + regime_mse):
        raise ValueError("MSE must be finite and baseline MSE strictly positive")
    baseline_mae = float(np.mean(np.abs(baseline_error)))
    regime_mae = float(np.mean(np.abs(regime_error)))
    return {
        "baseline_mse": baseline_mse,
        "regime_mse": regime_mse,
        "relative_mse_reduction": 1.0 - regime_mse / baseline_mse,
        "baseline_mae": baseline_mae,
        "regime_mae": regime_mae,
        "mae_reduction": baseline_mae - regime_mae,
    }


def _group_losses(
    cells: tuple[_TargetCell, ...],
    target: ArrayF,
    baseline: ArrayF,
    regime: ArrayF,
    *,
    group: str,
) -> dict[str, dict[str, float]]:
    labels = [cell.period if group == "period" else cell.symbol for cell in cells]
    result: dict[str, dict[str, float]] = {}
    for label in sorted(set(labels)):
        mask = np.asarray([value == label for value in labels], dtype=np.bool_)
        losses = _losses(target[mask], baseline[mask], regime[mask])
        result[label] = losses
    return result


def _permutation_distribution(
    target_name: str,
    train: tuple[_TargetCell, ...],
    evaluation: tuple[_TargetCell, ...],
    symbols: list[str],
    baseline_intercepts: ArrayF,
    *,
    replicates: int,
    root_seed: int,
) -> ArrayF:
    if replicates <= 0:
        raise ValueError("permutation replicates must be positive")
    values = np.empty(replicates, dtype=np.float64)
    all_cells = (*train, *evaluation)
    lookup = {(cell.symbol, cell.period): cell.predictor for cell in all_cells}
    for replicate in range(replicates):
        mappings: dict[str, dict[str, str]] = {}
        for era in ("fit", "evaluation_1", "evaluation_2"):
            era_periods = sorted({cell.period for cell in all_cells if cell.era == era})
            rng = np.random.default_rng(
                deterministic_seed(root_seed, target_name, replicate, era)
            )
            permutation = rng.permutation(len(era_periods))
            while np.array_equal(permutation, np.arange(len(era_periods))):
                permutation = rng.permutation(len(era_periods))
            mappings[era] = {
                period: era_periods[int(permutation[index])]
                for index, period in enumerate(era_periods)
            }
        permuted_train = np.asarray(
            [lookup[(cell.symbol, mappings[cell.era][cell.period])] for cell in train],
            dtype=np.float64,
        )
        permuted_evaluation = np.asarray(
            [
                lookup[(cell.symbol, mappings[cell.era][cell.period])]
                for cell in evaluation
            ],
            dtype=np.float64,
        )
        surrogate_train = tuple(
            _TargetCell(
                symbol=cell.symbol,
                period=cell.period,
                era=cell.era,
                predictor=float(permuted_train[index]),
                target=cell.target,
            )
            for index, cell in enumerate(train)
        )
        regime_intercepts, slope = _fit_fixed_effects(
            surrogate_train, symbols, include_regime=True
        )
        target, baseline, regime = _predictions(
            evaluation,
            symbols,
            baseline_intercepts,
            regime_intercepts,
            slope,
            predictor_override=permuted_evaluation,
        )
        values[replicate] = _losses(target, baseline, regime)[
            "relative_mse_reduction"
        ]
    return values


def _cluster_bootstrap_distribution(
    cells: tuple[_TargetCell, ...],
    target: ArrayF,
    baseline: ArrayF,
    regime: ArrayF,
    *,
    replicates: int,
    root_seed: int,
) -> ArrayF:
    if replicates <= 0:
        raise ValueError("bootstrap replicates must be positive")
    periods = sorted({cell.period for cell in cells})
    if len(periods) < 2:
        raise ValueError("cluster bootstrap requires at least two periods")
    labels = np.asarray([cell.period for cell in cells])
    rng = np.random.default_rng(root_seed)
    values = np.empty(replicates, dtype=np.float64)
    for replicate in range(replicates):
        sampled = rng.choice(periods, size=len(periods), replace=True)
        indices = np.concatenate([np.flatnonzero(labels == period) for period in sampled])
        values[replicate] = _losses(
            target[indices], baseline[indices], regime[indices]
        )["relative_mse_reduction"]
    return values


def _parse_period(period: str) -> tuple[int, int]:
    if len(period) != 6 or period[4] != "H" or not period[:4].isdigit():
        raise ValueError(f"invalid half-year period: {period}")
    year = int(period[:4])
    half = int(period[5])
    if half not in (1, 2):
        raise ValueError(f"invalid half-year period: {period}")
    return year, half


def _period_ordinal(period: str) -> int:
    year, half = _parse_period(period)
    return 2 * year + half - 1


def _period_from_ordinal(value: int) -> str:
    year, offset = divmod(value, 2)
    return period_key(year, offset + 1)


def _finite_vector(values: npt.ArrayLike, name: str) -> ArrayF:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1 or array.size == 0 or not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be a nonempty finite vector")
    return array


def _mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return cast(dict[str, Any], value)


__all__ = [
    "HalfYearBlock",
    "RegimeRow",
    "build_regime_rows",
    "evaluate_regime_memory",
    "expand_period_range",
    "make_half_year_block",
    "period_key",
    "previous_period",
]
