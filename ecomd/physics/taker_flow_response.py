"""Dependence-aware taker-flow response feasibility on minute bars."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, cast

import numpy as np
import numpy.typing as npt

from ecomd.data.yfinance_provenance import sha256_float64
from ecomd.eval.evaluator_v2 import deterministic_seed

ArrayF = npt.NDArray[np.float64]
ArrayI = npt.NDArray[np.int64]


@dataclass(frozen=True)
class MinuteMonth:
    """One exact UTC-month panel represented as day-by-minute arrays."""

    symbol: str
    month: str
    dates: tuple[str, ...]
    close: ArrayF
    quote_volume: ArrayF
    taker_buy_quote: ArrayF


@dataclass(frozen=True)
class DayEvents:
    """Selected event indices and unsigned future responses for one asset-day."""

    symbol: str
    month: str
    date: str
    sign_sequence: ArrayF
    event_indices: ArrayI
    unsigned_responses: ArrayF
    contemporaneous_unsigned_response: ArrayF


def taker_flow_imbalance(
    quote_volume: npt.ArrayLike,
    taker_buy_quote: npt.ArrayLike,
) -> ArrayF:
    """Return signed aggressive quote-volume share without calling it L2 OFI."""
    quote = np.asarray(quote_volume, dtype=np.float64)
    taker = np.asarray(taker_buy_quote, dtype=np.float64)
    if quote.shape != taker.shape or quote.ndim not in (1, 2):
        raise ValueError("quote and taker arrays must share a one- or two-dimensional shape")
    if not np.all(np.isfinite(quote)) or not np.all(np.isfinite(taker)):
        raise ValueError("quote and taker arrays must be finite")
    if np.any(quote < 0.0) or np.any(taker < 0.0) or np.any(taker > quote + 1e-12):
        raise ValueError("invalid taker/total quote-volume bounds")
    result = np.full(quote.shape, np.nan, dtype=np.float64)
    positive = quote > 0.0
    result[positive] = (2.0 * taker[positive] - quote[positive]) / quote[positive]
    if np.any(np.abs(result[positive]) > 1.0 + 1e-12):
        raise ValueError("taker-flow imbalance lies outside [-1, 1]")
    return result


def evaluate_taker_flow_response(
    series: dict[str, dict[str, MinuteMonth]],
    protocol: dict[str, Any],
) -> dict[str, Any]:
    """Apply frozen thresholds, response curves, nulls, bootstraps, and hard gates."""
    data = _mapping(protocol["data"], "data")
    split = _mapping(protocol["time_split"], "time_split")
    selection = _mapping(protocol["event_selection"], "event_selection")
    preprocessing = _mapping(protocol["preprocessing"], "preprocessing")
    inference = _mapping(
        protocol["dependence_aware_inference"], "dependence_aware_inference"
    )
    symbols = [str(value) for value in cast(list[object], data["symbols"])]
    months = [str(value) for value in cast(list[object], data["months"])]
    fit_month = str(split["threshold_fit"])
    evaluation_months = [str(split["confirmation"]), str(split["temporal_test"])]
    if set(series) != set(symbols):
        raise ValueError("loaded symbols differ from the frozen universe")
    if any(set(series[symbol]) != set(months) for symbol in symbols):
        raise ValueError("loaded months differ from the frozen universe")
    if fit_month in evaluation_months or set([fit_month, *evaluation_months]) != set(months):
        raise ValueError("time split does not partition the frozen months")

    horizons = tuple(
        int(str(value))
        for value in cast(list[object], preprocessing["response_horizons_minutes"])
    )
    if horizons != (1, 2, 5, 10, 30, 60):
        raise ValueError("response horizons differ from the implementation")
    thresholds = _fit_thresholds(
        series,
        symbols,
        fit_month,
        quantile=float(selection["january_absolute_imbalance_quantile"]),
    )
    day_events: dict[str, dict[str, tuple[DayEvents, ...]]] = {}
    for month in months:
        day_events[month] = {}
        for symbol in symbols:
            day_events[month][symbol] = _select_month_events(
                series[symbol][month],
                threshold=thresholds[symbol],
                horizons=horizons,
                pre_window=int(preprocessing["pre_volatility_window_minutes"]),
                first_index=int(selection["first_eligible_minute_index"]),
                last_index=int(selection["last_eligible_minute_index"]),
                minimum_separation=int(
                    selection["minimum_selected_event_separation_minutes"]
                ),
            )

    january_sanity: dict[str, dict[str, float | int | bool]] = {}
    for symbol in symbols:
        days = day_events[fit_month][symbol]
        values = [
            float(
                np.mean(
                    day.sign_sequence[day.event_indices]
                    * day.contemporaneous_unsigned_response
                )
            )
            for day in days
            if day.event_indices.size > 0
        ]
        mean_response = float(np.mean(values)) if values else float("nan")
        january_sanity[symbol] = {
            "selected_events": sum(int(day.event_indices.size) for day in days),
            "asset_days_with_events": len(values),
            "mean_contemporaneous_signed_response": mean_response,
            "passed": bool(np.isfinite(mean_response) and mean_response > 0.0),
        }

    month_results: dict[str, Any] = {}
    for month in evaluation_months:
        month_results[month] = _evaluate_month(
            month,
            day_events[month],
            symbols,
            horizons,
            inference,
        )

    gate = _mapping(protocol["primary_gate"], "primary_gate")
    minimum_events = int(selection["minimum_selected_events_per_symbol_month"])
    all_asset_summaries = [
        _mapping(
            _mapping(month_results[month], month)["by_symbol"][symbol],
            f"{month}/{symbol}",
        )
        for month in evaluation_months
        for symbol in symbols
    ]
    january_clause = all(bool(value["passed"]) for value in january_sanity.values())
    event_count_clause = all(
        int(summary["selected_events"]) >= minimum_events
        for summary in all_asset_summaries
    )
    early_clause = all(
        float(summary["early_response"]) > 0.0 for summary in all_asset_summaries
    )
    decay_clause = all(
        float(summary["decay_statistic"]) > 0.0 for summary in all_asset_summaries
    )
    early_floor = float(gate["pooled_early_response_minimum_each_evaluation_month"])
    decay_fraction_floor = float(
        gate["pooled_decay_fraction_of_early_minimum_each_evaluation_month"]
    )
    p_maximum = float(
        gate["circular_sign_permutation_p_maximum_each_evaluation_month"]
    )
    early_floor_clause = all(
        float(_mapping(month_results[month], month)["pooled"]["early_response"])
        >= early_floor
        for month in evaluation_months
    )
    decay_fraction_clause = all(
        float(
            _mapping(month_results[month], month)["pooled"][
                "decay_fraction_of_early"
            ]
        )
        >= decay_fraction_floor
        for month in evaluation_months
    )
    permutation_clause = all(
        float(_mapping(month_results[month], month)["circular_sign_null"]["p_value"])
        <= p_maximum
        for month in evaluation_months
    )
    bootstrap_clause = all(
        float(_mapping(month_results[month], month)["calendar_day_bootstrap"]["ci_low"])
        > 0.0
        for month in evaluation_months
    )
    clauses = {
        "january_contemporaneous_signed_response_positive_each_symbol": january_clause,
        "every_symbol_month_meets_minimum_event_count": event_count_clause,
        "every_symbol_month_early_response_positive": early_clause,
        "every_symbol_month_decay_positive": decay_clause,
        "pooled_early_response_floor_each_month": early_floor_clause,
        "pooled_decay_fraction_floor_each_month": decay_fraction_clause,
        "circular_sign_permutation_p_each_month": permutation_clause,
        "calendar_day_bootstrap_lower_decay_each_month": bootstrap_clause,
    }
    passed = all(clauses.values())
    decision = _mapping(protocol["decision"], "decision")
    return {
        "thresholds": thresholds,
        "january_measurement_sanity": january_sanity,
        "evaluation_months": month_results,
        "primary_gate_clauses": clauses,
        "feasibility_passed": passed,
        "decision": decision["pass"] if passed else decision["fail"],
        "paper_claim_or_model_training_authorized": False,
    }


def _fit_thresholds(
    series: dict[str, dict[str, MinuteMonth]],
    symbols: list[str],
    fit_month: str,
    *,
    quantile: float,
) -> dict[str, float]:
    if not 0.0 < quantile < 1.0:
        raise ValueError("imbalance quantile must lie in (0, 1)")
    thresholds: dict[str, float] = {}
    for symbol in symbols:
        month = _validate_month(series[symbol][fit_month])
        imbalance = taker_flow_imbalance(month.quote_volume, month.taker_buy_quote)
        finite = np.abs(imbalance[np.isfinite(imbalance)])
        if finite.size == 0:
            raise ValueError(f"{symbol} lacks finite fit imbalances")
        threshold = float(np.quantile(finite, quantile, method="linear"))
        if not np.isfinite(threshold) or threshold <= 0.0 or threshold > 1.0:
            raise ValueError(f"{symbol} has an invalid imbalance threshold")
        thresholds[symbol] = threshold
    return thresholds


def _select_month_events(
    month: MinuteMonth,
    *,
    threshold: float,
    horizons: tuple[int, ...],
    pre_window: int,
    first_index: int,
    last_index: int,
    minimum_separation: int,
) -> tuple[DayEvents, ...]:
    checked = _validate_month(month)
    imbalance = taker_flow_imbalance(checked.quote_volume, checked.taker_buy_quote)
    selected: list[DayEvents] = []
    for day_index, date in enumerate(checked.dates):
        close = checked.close[day_index]
        signed_flow = imbalance[day_index]
        log_close = np.log(close)
        returns = np.full(close.size, np.nan, dtype=np.float64)
        returns[1:] = np.diff(log_close)
        indices: list[int] = []
        unsigned: list[list[float]] = []
        contemporaneous: list[float] = []
        last_selected = -minimum_separation
        for minute_index in range(first_index, last_index + 1):
            value = signed_flow[minute_index]
            if (
                not np.isfinite(value)
                or abs(value) <= threshold
                or minute_index - last_selected < minimum_separation
            ):
                continue
            past = returns[minute_index - pre_window : minute_index]
            if past.size != pre_window or not np.all(np.isfinite(past)):
                continue
            pre_volatility = float(np.sqrt(np.mean(np.square(past))))
            if not np.isfinite(pre_volatility) or pre_volatility <= 0.0:
                continue
            response = [
                float(
                    (log_close[minute_index + horizon] - log_close[minute_index])
                    / (pre_volatility * math.sqrt(horizon))
                )
                for horizon in horizons
            ]
            if not all(np.isfinite(item) for item in response):
                continue
            indices.append(minute_index)
            unsigned.append(response)
            contemporaneous.append(float(returns[minute_index] / pre_volatility))
            last_selected = minute_index
        response_array = np.asarray(unsigned, dtype=np.float64)
        if not unsigned:
            response_array = np.empty((0, len(horizons)), dtype=np.float64)
        selected.append(
            DayEvents(
                symbol=checked.symbol,
                month=checked.month,
                date=date,
                sign_sequence=np.sign(signed_flow).astype(np.float64, copy=False),
                event_indices=np.asarray(indices, dtype=np.int64),
                unsigned_responses=response_array,
                contemporaneous_unsigned_response=np.asarray(
                    contemporaneous, dtype=np.float64
                ),
            )
        )
    return tuple(selected)


def _evaluate_month(
    month: str,
    events_by_symbol: dict[str, tuple[DayEvents, ...]],
    symbols: list[str],
    horizons: tuple[int, ...],
    inference: dict[str, Any],
) -> dict[str, Any]:
    if set(events_by_symbol) != set(symbols):
        raise ValueError("month event registry differs from symbols")
    dates_by_symbol = {
        symbol: tuple(day.date for day in events_by_symbol[symbol]) for symbol in symbols
    }
    unique_date_sets = {values for values in dates_by_symbol.values()}
    if len(unique_date_sets) != 1:
        raise ValueError("symbols do not share the same UTC calendar days")
    dates = next(iter(unique_date_sets))
    real_day_curves: dict[tuple[str, str], ArrayF] = {}
    by_symbol: dict[str, dict[str, Any]] = {}
    for symbol in symbols:
        total_events = 0
        curves: list[ArrayF] = []
        day_output: dict[str, Any] = {}
        for day in events_by_symbol[symbol]:
            count = int(day.event_indices.size)
            total_events += count
            if count == 0:
                day_output[day.date] = {"selected_events": 0, "curve": None}
                continue
            curve = _real_day_curve(day)
            real_day_curves[(symbol, day.date)] = curve
            curves.append(curve)
            day_output[day.date] = {
                "selected_events": count,
                "curve": curve.tolist(),
            }
        if not curves:
            summary = _curve_summary(np.full(len(horizons), np.nan), horizons)
        else:
            summary = _curve_summary(np.mean(np.vstack(curves), axis=0), horizons)
        by_symbol[symbol] = {
            "selected_events": total_events,
            "asset_days_with_events": len(curves),
            **summary,
            "days": day_output,
        }
    if not real_day_curves:
        raise ValueError(f"{month} has no selected events")
    pooled_curve = np.mean(np.vstack(list(real_day_curves.values())), axis=0)
    pooled = _curve_summary(pooled_curve, horizons)

    null_contract = _mapping(inference["circular_sign_null"], "circular_sign_null")
    null_values = _circular_null(
        month,
        events_by_symbol,
        symbols,
        dates,
        horizons,
        replicates=int(null_contract["replicates"]),
        root_seed=int(null_contract["root_seed"]),
        shift_bounds=tuple(
            int(str(value))
            for value in cast(list[object], null_contract["shift_range_minutes_inclusive"])
        ),
    )
    real_decay = float(pooled["decay_statistic"])
    exceedances = int(np.sum(null_values >= real_decay))
    p_value = (1.0 + exceedances) / (null_values.size + 1.0)

    bootstrap_contract = _mapping(
        inference["calendar_day_bootstrap"], "calendar_day_bootstrap"
    )
    bootstrap_values = _calendar_bootstrap(
        month,
        real_day_curves,
        symbols,
        dates,
        horizons,
        replicates=int(bootstrap_contract["replicates"]),
        root_seed=int(bootstrap_contract["root_seed"]),
    )
    confidence = float(bootstrap_contract["confidence_level"])
    tail = (1.0 - confidence) / 2.0
    ci_low, ci_high = np.quantile(bootstrap_values, [tail, 1.0 - tail])
    return {
        "by_symbol": by_symbol,
        "pooled": pooled,
        "calendar_days": len(dates),
        "asset_days_with_events": len(real_day_curves),
        "circular_sign_null": {
            "replicates": int(null_values.size),
            "exceedances_at_or_above_real": exceedances,
            "p_value": p_value,
            "minimum": float(np.min(null_values)),
            "median": float(np.median(null_values)),
            "maximum": float(np.max(null_values)),
            "distribution_sha256": sha256_float64(null_values),
        },
        "calendar_day_bootstrap": {
            "replicates": int(bootstrap_values.size),
            "confidence_level": confidence,
            "ci_low": float(ci_low),
            "median": float(np.median(bootstrap_values)),
            "ci_high": float(ci_high),
            "distribution_sha256": sha256_float64(bootstrap_values),
        },
    }


def _real_day_curve(day: DayEvents) -> ArrayF:
    if day.event_indices.size == 0:
        raise ValueError("cannot build a curve for an empty event day")
    signs = day.sign_sequence[day.event_indices]
    return np.asarray(
        np.mean(signs[:, None] * day.unsigned_responses, axis=0),
        dtype=np.float64,
    )


def _curve_summary(curve: ArrayF, horizons: tuple[int, ...]) -> dict[str, Any]:
    index = {horizon: position for position, horizon in enumerate(horizons)}
    early = float(np.mean(curve[[index[1], index[2], index[5]]]))
    late = float(curve[index[60]])
    decay = early - late
    fraction = decay / early if np.isfinite(early) and early > 0.0 else float("nan")
    return {
        "curve": curve.tolist(),
        "early_response": early,
        "late_response": late,
        "decay_statistic": decay,
        "decay_fraction_of_early": fraction,
    }


def _circular_null(
    month: str,
    events_by_symbol: dict[str, tuple[DayEvents, ...]],
    symbols: list[str],
    dates: tuple[str, ...],
    horizons: tuple[int, ...],
    *,
    replicates: int,
    root_seed: int,
    shift_bounds: tuple[int, ...],
) -> ArrayF:
    if replicates <= 0 or len(shift_bounds) != 2:
        raise ValueError("invalid circular-null configuration")
    low, high = shift_bounds
    if low <= 0 or high < low or high >= 1440:
        raise ValueError("invalid circular-shift bounds")
    lookup = {
        (symbol, day.date): day
        for symbol in symbols
        for day in events_by_symbol[symbol]
    }
    values = np.empty(replicates, dtype=np.float64)
    for replicate in range(replicates):
        curves: list[ArrayF] = []
        for date in dates:
            rng = np.random.default_rng(
                deterministic_seed(root_seed, month, replicate, date)
            )
            shift = int(rng.integers(low, high + 1))
            for symbol in symbols:
                day = lookup[(symbol, date)]
                if day.event_indices.size == 0:
                    continue
                shifted_indices = (day.event_indices - shift) % day.sign_sequence.size
                shifted_signs = day.sign_sequence[shifted_indices]
                curves.append(
                    np.mean(shifted_signs[:, None] * day.unsigned_responses, axis=0)
                )
        if not curves:
            raise ValueError("a circular-null replicate has no event curves")
        pooled = np.mean(np.vstack(curves), axis=0)
        values[replicate] = float(_curve_summary(pooled, horizons)["decay_statistic"])
    return values


def _calendar_bootstrap(
    month: str,
    day_curves: dict[tuple[str, str], ArrayF],
    symbols: list[str],
    dates: tuple[str, ...],
    horizons: tuple[int, ...],
    *,
    replicates: int,
    root_seed: int,
) -> ArrayF:
    if replicates <= 0 or len(dates) < 2:
        raise ValueError("invalid calendar bootstrap configuration")
    rng = np.random.default_rng(deterministic_seed(root_seed, month))
    values = np.empty(replicates, dtype=np.float64)
    for replicate in range(replicates):
        sampled = rng.choice(dates, size=len(dates), replace=True)
        curves = [
            day_curves[(symbol, str(date))]
            for date in sampled
            for symbol in symbols
            if (symbol, str(date)) in day_curves
        ]
        if not curves:
            raise ValueError("a calendar-bootstrap replicate has no event curves")
        pooled = np.mean(np.vstack(curves), axis=0)
        values[replicate] = float(_curve_summary(pooled, horizons)["decay_statistic"])
    return values


def _validate_month(month: MinuteMonth) -> MinuteMonth:
    expected_shape = (len(month.dates), 1440)
    if not month.dates or len(set(month.dates)) != len(month.dates):
        raise ValueError("month dates must be nonempty and unique")
    for name, values in (
        ("close", month.close),
        ("quote_volume", month.quote_volume),
        ("taker_buy_quote", month.taker_buy_quote),
    ):
        if values.shape != expected_shape or not np.all(np.isfinite(values)):
            raise ValueError(f"{name} must be a finite day-by-1440 matrix")
    if np.any(month.close <= 0.0):
        raise ValueError("close prices must be positive")
    return month


def _mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return cast(dict[str, Any], value)


__all__ = [
    "DayEvents",
    "MinuteMonth",
    "evaluate_taker_flow_response",
    "taker_flow_imbalance",
]
