"""Fixed-physical-time aggregate observations and train-only P3 links."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, TypeAlias, cast

import numpy as np
from numpy.typing import NDArray

from .continuous_time import LOBSTER_MARK_NAMES, lobster_mark_ids

FloatArray: TypeAlias = NDArray[np.float64]
IntArray: TypeAlias = NDArray[np.int64]

FIT_WARNING = "COEFFICIENTS_CONDITIONAL_ON_FROZEN_LATENT_SCALE"


class MarketSizeUnit(StrEnum):
    SHARES = "shares"
    CONTRACTS = "contracts"


class ModelFamily(StrEnum):
    LATENT = "latent"
    OBSERVATION_ONLY = "observation_only"
    COMBINED = "combined"


@dataclass(frozen=True)
class AggregateEventRows:
    """Order-free external rows used only for fixed-time aggregation."""

    time_seconds: FloatArray
    event_type: IntArray
    size: IntArray
    direction: IntArray
    midpoint_after: FloatArray

    def __post_init__(self) -> None:
        time = np.asarray(self.time_seconds, dtype=np.float64)
        midpoint = np.asarray(self.midpoint_after, dtype=np.float64)
        raw_event = np.asarray(self.event_type)
        raw_size = np.asarray(self.size)
        raw_direction = np.asarray(self.direction)
        if not np.issubdtype(raw_event.dtype, np.integer):
            raise ValueError("event_type must use an integer dtype")
        if not np.issubdtype(raw_size.dtype, np.integer):
            raise ValueError("size must use an integer dtype")
        if not np.issubdtype(raw_direction.dtype, np.integer):
            raise ValueError("direction must use an integer dtype")
        event = raw_event.astype(np.int64, copy=False)
        size = raw_size.astype(np.int64, copy=False)
        direction = raw_direction.astype(np.int64, copy=False)
        if time.ndim != 1 or time.size < 1:
            raise ValueError("event rows must contain a nonempty time vector")
        if any(array.shape != time.shape for array in (event, size, direction, midpoint)):
            raise ValueError("event row arrays must have identical shapes")
        if not np.isfinite(time).all() or not np.isfinite(midpoint).all():
            raise ValueError("time and midpoint must be finite")
        if np.any(np.diff(time) < 0.0):
            raise ValueError("event time must be nondecreasing")
        if np.any(size <= 0):
            raise ValueError("event size must be positive")
        if np.any(midpoint <= 0.0):
            raise ValueError("after-event midpoint must be positive")
        lobster_mark_ids(event, direction)
        object.__setattr__(self, "time_seconds", time.copy())
        object.__setattr__(self, "event_type", event.copy())
        object.__setattr__(self, "size", size.copy())
        object.__setattr__(self, "direction", direction.copy())
        object.__setattr__(self, "midpoint_after", midpoint.copy())

    @property
    def n_events(self) -> int:
        return int(self.time_seconds.size)

    def slice(self, start: int, end: int) -> AggregateEventRows:
        """Return an independent contiguous row slice."""
        if not 0 <= start < end <= self.n_events:
            raise ValueError("invalid event-row slice")
        return AggregateEventRows(
            time_seconds=self.time_seconds[start:end],
            event_type=self.event_type[start:end],
            size=self.size[start:end],
            direction=self.direction[start:end],
            midpoint_after=self.midpoint_after[start:end],
        )


@dataclass(frozen=True)
class AggregateBinConfig:
    """Physical clock and units of an aggregate observation window."""

    start_seconds: float
    end_seconds: float
    bin_width_seconds: float
    initial_midpoint: float
    size_unit: MarketSizeUnit

    def __post_init__(self) -> None:
        values = (
            self.start_seconds,
            self.end_seconds,
            self.bin_width_seconds,
            self.initial_midpoint,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("aggregate-bin clock and midpoint must be finite")
        if self.end_seconds <= self.start_seconds:
            raise ValueError("aggregate-bin end must exceed start")
        if self.bin_width_seconds <= 0.0:
            raise ValueError("aggregate-bin width must be positive")
        if self.initial_midpoint <= 0.0:
            raise ValueError("initial midpoint must be positive")
        ratio = (self.end_seconds - self.start_seconds) / self.bin_width_seconds
        nearest = round(ratio)
        if nearest < 1 or not math.isclose(ratio, nearest, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("aggregate-bin window must contain an integral number of bins")
        if not isinstance(self.size_unit, MarketSizeUnit):
            raise ValueError("size_unit must be shares or contracts")

    @property
    def n_bins(self) -> int:
        return round((self.end_seconds - self.start_seconds) / self.bin_width_seconds)

    def to_dict(self) -> dict[str, object]:
        return {
            "start_seconds": self.start_seconds,
            "end_seconds": self.end_seconds,
            "bin_width_seconds": self.bin_width_seconds,
            "initial_midpoint": self.initial_midpoint,
            "size_unit": self.size_unit.value,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> AggregateBinConfig:
        expected = {
            "start_seconds",
            "end_seconds",
            "bin_width_seconds",
            "initial_midpoint",
            "size_unit",
        }
        if set(payload) != expected:
            raise ValueError("aggregate-bin config keys differ")
        size_unit = payload["size_unit"]
        if not isinstance(size_unit, str):
            raise ValueError("size_unit must be a string")
        try:
            parsed_unit = MarketSizeUnit(size_unit)
        except ValueError as error:
            raise ValueError("size_unit must be shares or contracts") from error
        numeric: dict[str, float] = {}
        for key in expected - {"size_unit"}:
            value = payload[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{key} must be numeric")
            numeric[key] = float(value)
        return cls(size_unit=parsed_unit, **numeric)


@dataclass
class AggregateBinAccumulatorState:
    """Complete mutable accumulation state with a versioned checkpoint."""

    config: AggregateBinConfig
    mark_counts: IntArray
    executed_volume: IntArray
    last_midpoint_by_bin: FloatArray
    current_midpoint: float
    last_time_seconds: float | None
    next_unfinalized_bin: int
    events_processed: int
    finalized: bool

    def clone(self) -> AggregateBinAccumulatorState:
        return AggregateBinAccumulatorState(
            config=self.config,
            mark_counts=self.mark_counts.copy(),
            executed_volume=self.executed_volume.copy(),
            last_midpoint_by_bin=self.last_midpoint_by_bin.copy(),
            current_midpoint=float(self.current_midpoint),
            last_time_seconds=(
                None if self.last_time_seconds is None else float(self.last_time_seconds)
            ),
            next_unfinalized_bin=int(self.next_unfinalized_bin),
            events_processed=int(self.events_processed),
            finalized=bool(self.finalized),
        )

    def to_checkpoint(self) -> dict[str, object]:
        last_midpoint = [
            None if not np.isfinite(value) else float(value)
            for value in self.last_midpoint_by_bin
        ]
        return {
            "format_version": 1,
            "config": self.config.to_dict(),
            "mark_counts": self.mark_counts.tolist(),
            "executed_volume": self.executed_volume.tolist(),
            "last_midpoint_by_bin": last_midpoint,
            "current_midpoint": self.current_midpoint,
            "last_time_seconds": self.last_time_seconds,
            "next_unfinalized_bin": self.next_unfinalized_bin,
            "events_processed": self.events_processed,
            "finalized": self.finalized,
        }

    @classmethod
    def from_checkpoint(cls, payload: dict[str, object]) -> AggregateBinAccumulatorState:
        expected = {
            "format_version",
            "config",
            "mark_counts",
            "executed_volume",
            "last_midpoint_by_bin",
            "current_midpoint",
            "last_time_seconds",
            "next_unfinalized_bin",
            "events_processed",
            "finalized",
        }
        if set(payload) != expected or payload["format_version"] != 1:
            raise ValueError("unsupported aggregate-bin checkpoint")
        config_payload = payload["config"]
        if not isinstance(config_payload, dict) or not all(
            isinstance(key, str) for key in config_payload
        ):
            raise ValueError("checkpoint config must be an object")
        config = AggregateBinConfig.from_dict(cast(dict[str, object], config_payload))
        mark_counts = np.asarray(payload["mark_counts"])
        executed_volume = np.asarray(payload["executed_volume"])
        if not np.issubdtype(mark_counts.dtype, np.integer) or not np.issubdtype(
            executed_volume.dtype, np.integer
        ):
            raise ValueError("checkpoint counts and volume must be integer")
        mark_counts = mark_counts.astype(np.int64, copy=False)
        executed_volume = executed_volume.astype(np.int64, copy=False)
        raw_midpoint = payload["last_midpoint_by_bin"]
        if not isinstance(raw_midpoint, list):
            raise ValueError("checkpoint midpoint state must be an array")
        parsed_midpoint: list[float] = []
        for value in raw_midpoint:
            if value is None:
                parsed_midpoint.append(float("nan"))
            elif isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("checkpoint midpoint entry must be numeric or null")
            else:
                parsed_midpoint.append(float(value))
        last_midpoint = np.asarray(parsed_midpoint, dtype=np.float64)
        if mark_counts.shape != (config.n_bins, len(LOBSTER_MARK_NAMES)):
            raise ValueError("checkpoint mark-count shape differs")
        if executed_volume.shape != (config.n_bins,) or last_midpoint.shape != (
            config.n_bins,
        ):
            raise ValueError("checkpoint bin-vector shape differs")
        if np.any(mark_counts < 0) or np.any(executed_volume < 0):
            raise ValueError("checkpoint counts and volume must be nonnegative")
        current_midpoint = _checkpoint_float(payload, "current_midpoint", allow_none=False)
        last_time = _checkpoint_float(payload, "last_time_seconds", allow_none=True)
        next_bin = _checkpoint_int(payload, "next_unfinalized_bin")
        events_processed = _checkpoint_int(payload, "events_processed")
        finalized = payload["finalized"]
        if not isinstance(finalized, bool):
            raise ValueError("checkpoint finalized flag must be boolean")
        if current_midpoint is None or current_midpoint <= 0.0:
            raise ValueError("checkpoint current midpoint must be positive")
        if not 0 <= next_bin <= config.n_bins or events_processed < 0:
            raise ValueError("checkpoint counters are invalid")
        return cls(
            config=config,
            mark_counts=mark_counts.copy(),
            executed_volume=executed_volume.copy(),
            last_midpoint_by_bin=last_midpoint,
            current_midpoint=current_midpoint,
            last_time_seconds=last_time,
            next_unfinalized_bin=next_bin,
            events_processed=events_processed,
            finalized=finalized,
        )


def _checkpoint_float(
    payload: dict[str, object], key: str, *, allow_none: bool
) -> float | None:
    value = payload[key]
    if value is None and allow_none:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"checkpoint {key} must be numeric")
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"checkpoint {key} must be finite")
    return parsed


def _checkpoint_int(payload: dict[str, object], key: str) -> int:
    value = payload[key]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"checkpoint {key} must be integer")
    return value


@dataclass(frozen=True)
class AggregateBinObservations:
    """Order-free fixed-time-bin observables in declared market units."""

    bin_start_seconds: FloatArray
    bin_end_seconds: FloatArray
    close_midpoint: FloatArray
    log_mid_return: FloatArray
    executed_volume: IntArray
    mark_counts: IntArray
    size_unit: MarketSizeUnit

    def __post_init__(self) -> None:
        starts = np.asarray(self.bin_start_seconds, dtype=np.float64)
        ends = np.asarray(self.bin_end_seconds, dtype=np.float64)
        closes = np.asarray(self.close_midpoint, dtype=np.float64)
        returns = np.asarray(self.log_mid_return, dtype=np.float64)
        volume = np.asarray(self.executed_volume)
        counts = np.asarray(self.mark_counts)
        n_bins = starts.size
        if starts.ndim != 1 or n_bins < 1:
            raise ValueError("aggregate observations require at least one bin")
        if any(array.shape != (n_bins,) for array in (ends, closes, returns, volume)):
            raise ValueError("aggregate observation vectors differ in shape")
        if counts.shape != (n_bins, len(LOBSTER_MARK_NAMES)):
            raise ValueError("aggregate mark-count shape differs")
        if not np.issubdtype(volume.dtype, np.integer) or not np.issubdtype(
            counts.dtype, np.integer
        ):
            raise ValueError("aggregate volume and counts must be integer")
        volume = volume.astype(np.int64, copy=False)
        counts = counts.astype(np.int64, copy=False)
        if (
            not np.isfinite(starts).all()
            or not np.isfinite(ends).all()
            or not np.isfinite(closes).all()
            or not np.isfinite(returns).all()
        ):
            raise ValueError("aggregate floating fields must be finite")
        if np.any(ends <= starts) or np.any(closes <= 0.0):
            raise ValueError("aggregate clock/midpoint is invalid")
        if np.any(volume < 0) or np.any(counts < 0):
            raise ValueError("aggregate counts and volume must be nonnegative")
        if not isinstance(self.size_unit, MarketSizeUnit):
            raise ValueError("aggregate size unit must be shares or contracts")
        object.__setattr__(self, "bin_start_seconds", starts.copy())
        object.__setattr__(self, "bin_end_seconds", ends.copy())
        object.__setattr__(self, "close_midpoint", closes.copy())
        object.__setattr__(self, "log_mid_return", returns.copy())
        object.__setattr__(self, "executed_volume", volume.copy())
        object.__setattr__(self, "mark_counts", counts.copy())

    @property
    def n_bins(self) -> int:
        return int(self.bin_start_seconds.size)

    @property
    def positive_mark_counts(self) -> IntArray:
        return cast(IntArray, self.mark_counts[:, (0, 3, 4)].sum(axis=1, dtype=np.int64))

    @property
    def total_mark_counts(self) -> IntArray:
        return cast(IntArray, self.mark_counts.sum(axis=1, dtype=np.int64))


class AggregateBinAccumulator:
    """State-complete ordered-row accumulator for half-open physical bins."""

    def __init__(self, config: AggregateBinConfig) -> None:
        self.config = config

    def init_state(self) -> AggregateBinAccumulatorState:
        n_bins = self.config.n_bins
        return AggregateBinAccumulatorState(
            config=self.config,
            mark_counts=np.zeros((n_bins, len(LOBSTER_MARK_NAMES)), dtype=np.int64),
            executed_volume=np.zeros(n_bins, dtype=np.int64),
            last_midpoint_by_bin=np.full(n_bins, np.nan, dtype=np.float64),
            current_midpoint=self.config.initial_midpoint,
            last_time_seconds=None,
            next_unfinalized_bin=0,
            events_processed=0,
            finalized=False,
        )

    def update(
        self, state: AggregateBinAccumulatorState, rows: AggregateEventRows
    ) -> AggregateBinAccumulatorState:
        if state.config != self.config:
            raise ValueError("accumulator state config differs")
        if state.finalized:
            raise RuntimeError("cannot update a finalized aggregate-bin state")
        if state.last_time_seconds is not None and rows.time_seconds[0] < state.last_time_seconds:
            raise ValueError("chunk time precedes the accumulated stream")
        if rows.time_seconds[0] < self.config.start_seconds or rows.time_seconds[-1] >= self.config.end_seconds:
            raise ValueError("event time is outside the half-open aggregate window")
        relative = (rows.time_seconds - self.config.start_seconds) / self.config.bin_width_seconds
        bin_index = np.floor(relative).astype(np.int64)
        if np.any((bin_index < 0) | (bin_index >= self.config.n_bins)):
            raise ValueError("event mapped outside the aggregate bins")
        marks = lobster_mark_ids(rows.event_type, rows.direction)
        result = state.clone()
        np.add.at(result.mark_counts, (bin_index, marks), 1)
        executions = np.isin(rows.event_type, (4, 5))
        np.add.at(result.executed_volume, bin_index[executions], rows.size[executions])
        for target_bin, midpoint in zip(bin_index, rows.midpoint_after, strict=True):
            result.last_midpoint_by_bin[int(target_bin)] = float(midpoint)
        result.current_midpoint = float(rows.midpoint_after[-1])
        result.last_time_seconds = float(rows.time_seconds[-1])
        result.next_unfinalized_bin = int(bin_index[-1])
        result.events_processed += rows.n_events
        return result

    def finalize(
        self, state: AggregateBinAccumulatorState
    ) -> tuple[AggregateBinAccumulatorState, AggregateBinObservations]:
        if state.config != self.config:
            raise ValueError("accumulator state config differs")
        if state.finalized:
            raise RuntimeError("aggregate-bin state was already finalized")
        result = state.clone()
        closes = np.empty(self.config.n_bins, dtype=np.float64)
        current = self.config.initial_midpoint
        for index, observed in enumerate(result.last_midpoint_by_bin):
            if np.isfinite(observed):
                current = float(observed)
            closes[index] = current
        preceding = np.concatenate(
            (np.asarray((self.config.initial_midpoint,), dtype=np.float64), closes[:-1])
        )
        returns = np.log(closes / preceding)
        starts = self.config.start_seconds + self.config.bin_width_seconds * np.arange(
            self.config.n_bins, dtype=np.float64
        )
        result.current_midpoint = float(closes[-1])
        result.next_unfinalized_bin = self.config.n_bins
        result.finalized = True
        observations = AggregateBinObservations(
            bin_start_seconds=starts,
            bin_end_seconds=starts + self.config.bin_width_seconds,
            close_midpoint=closes,
            log_mid_return=returns,
            executed_volume=result.executed_volume,
            mark_counts=result.mark_counts,
            size_unit=self.config.size_unit,
        )
        return result, observations


def aggregate_event_rows(
    rows: AggregateEventRows, config: AggregateBinConfig
) -> tuple[AggregateBinAccumulatorState, AggregateBinObservations]:
    """Aggregate a complete row batch through the streaming implementation."""
    accumulator = AggregateBinAccumulator(config)
    state = accumulator.update(accumulator.init_state(), rows)
    return accumulator.finalize(state)


@dataclass(frozen=True)
class SimulatorBinPredictors:
    """EcoMD-derived predictors already aligned one-to-one with physical bins."""

    log_return: FloatArray
    volume_model_units: FloatArray
    latent_flow_alignment: FloatArray

    def __post_init__(self) -> None:
        returns = np.asarray(self.log_return, dtype=np.float64)
        volume = np.asarray(self.volume_model_units, dtype=np.float64)
        alignment = np.asarray(self.latent_flow_alignment, dtype=np.float64)
        if returns.ndim != 1 or returns.size < 3:
            raise ValueError("simulator predictors require at least three bins")
        if volume.shape != returns.shape or alignment.shape != returns.shape:
            raise ValueError("simulator predictor shapes differ")
        if not np.isfinite(returns).all() or not np.isfinite(volume).all() or not np.isfinite(
            alignment
        ).all():
            raise ValueError("simulator predictors must be finite")
        if np.any(volume < 0.0) or np.any(np.abs(alignment) > 1.0):
            raise ValueError("simulator volume/alignment is outside support")
        object.__setattr__(self, "log_return", returns.copy())
        object.__setattr__(self, "volume_model_units", volume.copy())
        object.__setattr__(self, "latent_flow_alignment", alignment.copy())

    @property
    def n_bins(self) -> int:
        return int(self.log_return.size)

    @property
    def log_volume_predictor(self) -> FloatArray:
        return np.log1p(self.volume_model_units)


@dataclass(frozen=True)
class FrozenPrefixSplit:
    """A chronological prefix split; arbitrary masks are intentionally unsupported."""

    n_bins: int
    train_end: int

    def __post_init__(self) -> None:
        if self.n_bins < 4 or not 2 <= self.train_end < self.n_bins:
            raise ValueError("invalid chronological training prefix")

    @property
    def test_start(self) -> int:
        return self.train_end


@dataclass(frozen=True)
class GaussianChannelFit:
    family: ModelFamily
    coefficients: FloatArray
    sigma: float
    rank: int
    converged: bool


@dataclass(frozen=True)
class BinomialChannelFit:
    family: ModelFamily
    coefficients: FloatArray
    iterations: int
    converged: bool


@dataclass(frozen=True)
class P3MeasurementFit:
    return_fits: tuple[GaussianChannelFit, ...]
    volume_fits: tuple[GaussianChannelFit, ...]
    direction_fits: tuple[BinomialChannelFit, ...]
    n_bins: int
    train_end: int
    test_start: int
    training_prefix_sha256: str
    warning: str


def _family_features(
    family: ModelFamily, latent: FloatArray, observed: FloatArray
) -> FloatArray:
    current = latent[1:]
    lagged = observed[:-1]
    if family is ModelFamily.LATENT:
        return current[:, None]
    if family is ModelFamily.OBSERVATION_ONLY:
        return lagged[:, None]
    return np.column_stack((current, lagged))


def _fit_gaussian(
    family: ModelFamily,
    features: FloatArray,
    response: FloatArray,
    train_rows: slice,
) -> GaussianChannelFit:
    x = features[train_rows]
    y = response[1:][train_rows]
    design = np.column_stack((np.ones(y.size, dtype=np.float64), x))
    coefficients, _, rank, _ = np.linalg.lstsq(design, y, rcond=None)
    residual = y - design @ coefficients
    sigma = float(np.sqrt(np.mean(residual * residual)))
    converged = bool(
        rank == design.shape[1]
        and np.isfinite(coefficients).all()
        and math.isfinite(sigma)
        and sigma > 0.0
    )
    return GaussianChannelFit(
        family=family,
        coefficients=np.asarray(coefficients, dtype=np.float64),
        sigma=sigma,
        rank=int(rank),
        converged=converged,
    )


def _fit_grouped_binomial(
    family: ModelFamily,
    features: FloatArray,
    positive: IntArray,
    total: IntArray,
    train_rows: slice,
) -> BinomialChannelFit:
    x = features[train_rows]
    successes = positive[1:][train_rows].astype(np.float64)
    trials = total[1:][train_rows].astype(np.float64)
    if np.any(trials <= 0.0) or np.any((successes < 0.0) | (successes > trials)):
        raise ValueError("grouped directional counts are invalid")
    design = np.column_stack((np.ones(successes.size, dtype=np.float64), x))
    values = np.zeros(design.shape[1], dtype=np.float64)
    converged = False
    iteration = 0
    for _iteration in range(1, 101):
        iteration = _iteration
        logits = np.clip(design @ values, -40.0, 40.0)
        probability = 1.0 / (1.0 + np.exp(-logits))
        score = design.T @ (successes - trials * probability)
        information = design.T @ (
            (trials * probability * (1.0 - probability))[:, None] * design
        )
        try:
            step = np.linalg.solve(information, score)
        except np.linalg.LinAlgError:
            break
        values += step
        if float(np.max(np.abs(step))) <= 1e-11 * (
            1.0 + float(np.max(np.abs(values)))
        ):
            converged = True
            break
    return BinomialChannelFit(
        family=family,
        coefficients=values,
        iterations=iteration,
        converged=bool(converged and np.isfinite(values).all()),
    )


def _update_array_hash(digest: Any, name: str, array: NDArray[Any]) -> None:
    contiguous = np.ascontiguousarray(array)
    digest.update(name.encode())
    digest.update(str(contiguous.dtype).encode())
    digest.update(json.dumps(contiguous.shape).encode())
    digest.update(contiguous.tobytes())


def training_prefix_hash(
    predictors: SimulatorBinPredictors,
    observations: AggregateBinObservations,
    split: FrozenPrefixSplit,
) -> str:
    """Hash every predictor and response available to the frozen training prefix."""
    _validate_alignment(predictors, observations, split)
    digest = hashlib.sha256()
    end = split.train_end
    arrays: tuple[tuple[str, NDArray[Any]], ...] = (
        ("predictor_return", predictors.log_return[:end]),
        ("predictor_volume", predictors.volume_model_units[:end]),
        ("predictor_alignment", predictors.latent_flow_alignment[:end]),
        ("observed_return", observations.log_mid_return[:end]),
        ("observed_volume", observations.executed_volume[:end]),
        ("observed_marks", observations.mark_counts[:end]),
    )
    for name, array in arrays:
        _update_array_hash(digest, name, array)
    digest.update(str(split.train_end).encode())
    return digest.hexdigest()


def _validate_alignment(
    predictors: SimulatorBinPredictors,
    observations: AggregateBinObservations,
    split: FrozenPrefixSplit,
) -> None:
    if predictors.n_bins != observations.n_bins or split.n_bins != observations.n_bins:
        raise ValueError("predictor, observation and split lengths differ")
    if np.any(observations.total_mark_counts <= 0):
        raise ValueError("directional measurement requires positive mark count in every bin")


def fit_p3_measurement(
    predictors: SimulatorBinPredictors,
    observations: AggregateBinObservations,
    split: FrozenPrefixSplit,
) -> P3MeasurementFit:
    """Fit the three preregistered families on one frozen chronological prefix."""
    _validate_alignment(predictors, observations, split)
    observed_return = observations.log_mid_return
    observed_log_volume = np.log1p(observations.executed_volume.astype(np.float64))
    positive = observations.positive_mark_counts
    total = observations.total_mark_counts
    signed_fraction = (2.0 * positive.astype(np.float64) - total) / total
    train_rows = slice(0, split.train_end - 1)
    families = (
        ModelFamily.LATENT,
        ModelFamily.OBSERVATION_ONLY,
        ModelFamily.COMBINED,
    )
    return_fits = tuple(
        _fit_gaussian(
            family,
            _family_features(family, predictors.log_return, observed_return),
            observed_return,
            train_rows,
        )
        for family in families
    )
    volume_fits = tuple(
        _fit_gaussian(
            family,
            _family_features(family, predictors.log_volume_predictor, observed_log_volume),
            observed_log_volume,
            train_rows,
        )
        for family in families
    )
    direction_fits = tuple(
        _fit_grouped_binomial(
            family,
            _family_features(
                family, predictors.latent_flow_alignment, signed_fraction
            ),
            positive,
            total,
            train_rows,
        )
        for family in families
    )
    return P3MeasurementFit(
        return_fits=return_fits,
        volume_fits=volume_fits,
        direction_fits=direction_fits,
        n_bins=split.n_bins,
        train_end=split.train_end,
        test_start=split.test_start,
        training_prefix_sha256=training_prefix_hash(predictors, observations, split),
        warning=FIT_WARNING,
    )


def _fit_by_family(
    fits: tuple[GaussianChannelFit, ...] | tuple[BinomialChannelFit, ...],
    family: ModelFamily,
) -> GaussianChannelFit | BinomialChannelFit:
    matches = [fit for fit in fits if fit.family is family]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one fit for {family.value}")
    return matches[0]


def evaluate_p3_measurement(
    fit: P3MeasurementFit,
    predictors: SimulatorBinPredictors,
    observations: AggregateBinObservations,
    split: FrozenPrefixSplit,
    *,
    directional_sign: float = 1.0,
) -> dict[str, dict[str, float]]:
    """Score frozen fits on the chronological held-out suffix."""
    _validate_alignment(predictors, observations, split)
    if fit.n_bins != split.n_bins or fit.train_end != split.train_end:
        raise ValueError("fit and split differ")
    if directional_sign not in (-1.0, 1.0):
        raise ValueError("directional_sign must be -1 or +1")
    observed_return = observations.log_mid_return
    observed_log_volume = np.log1p(observations.executed_volume.astype(np.float64))
    positive = observations.positive_mark_counts
    total = observations.total_mark_counts
    signed_fraction = (2.0 * positive.astype(np.float64) - total) / total
    test_rows = slice(split.test_start - 1, split.n_bins - 1)
    output: dict[str, dict[str, float]] = {}
    for family in ModelFamily:
        return_fit = _fit_by_family(fit.return_fits, family)
        volume_fit = _fit_by_family(fit.volume_fits, family)
        direction_fit = _fit_by_family(fit.direction_fits, family)
        if not isinstance(return_fit, GaussianChannelFit) or not isinstance(
            volume_fit, GaussianChannelFit
        ) or not isinstance(direction_fit, BinomialChannelFit):
            raise TypeError("channel fit type differs")
        return_features = _family_features(
            family, predictors.log_return, observed_return
        )[test_rows]
        volume_features = _family_features(
            family, predictors.log_volume_predictor, observed_log_volume
        )[test_rows]
        direction_latent = directional_sign * predictors.latent_flow_alignment
        direction_features = _family_features(
            family, direction_latent, signed_fraction
        )[test_rows]
        return_design = np.column_stack(
            (np.ones(return_features.shape[0]), return_features)
        )
        volume_design = np.column_stack(
            (np.ones(volume_features.shape[0]), volume_features)
        )
        direction_design = np.column_stack(
            (np.ones(direction_features.shape[0]), direction_features)
        )
        return_target = observed_return[split.test_start :]
        volume_target = observed_log_volume[split.test_start :]
        positive_test = positive[split.test_start :].astype(np.float64)
        total_test = total[split.test_start :].astype(np.float64)
        return_residual = return_target - return_design @ return_fit.coefficients
        volume_residual = volume_target - volume_design @ volume_fit.coefficients
        logits = direction_design @ direction_fit.coefficients
        direction_ll = np.sum(
            positive_test * -np.logaddexp(0.0, -logits)
            + (total_test - positive_test) * -np.logaddexp(0.0, logits)
        )
        output[family.value] = {
            "return_rmse": float(np.sqrt(np.mean(return_residual * return_residual))),
            "log_volume_rmse": float(np.sqrt(np.mean(volume_residual * volume_residual))),
            "direction_log_likelihood_nats_per_event": float(
                direction_ll / np.sum(total_test)
            ),
        }
    return output


def _gaussian_fit_to_dict(fit: GaussianChannelFit) -> dict[str, object]:
    return {
        "family": fit.family.value,
        "coefficients": [float(value) for value in fit.coefficients],
        "sigma": fit.sigma,
        "rank": fit.rank,
        "converged": fit.converged,
    }


def _binomial_fit_to_dict(fit: BinomialChannelFit) -> dict[str, object]:
    return {
        "family": fit.family.value,
        "coefficients": [float(value) for value in fit.coefficients],
        "iterations": fit.iterations,
        "converged": fit.converged,
    }


def measurement_fit_to_dict(fit: P3MeasurementFit) -> dict[str, object]:
    """Return a JSON-safe complete fit record."""
    return {
        "return_fits": [_gaussian_fit_to_dict(item) for item in fit.return_fits],
        "volume_fits": [_gaussian_fit_to_dict(item) for item in fit.volume_fits],
        "direction_fits": [_binomial_fit_to_dict(item) for item in fit.direction_fits],
        "n_bins": fit.n_bins,
        "train_end": fit.train_end,
        "test_start": fit.test_start,
        "training_prefix_sha256": fit.training_prefix_sha256,
        "warning": fit.warning,
    }


def measurement_fit_hash(fit: P3MeasurementFit) -> str:
    """Hash every fitted value and frozen temporal provenance field."""
    payload = json.dumps(
        measurement_fit_to_dict(fit), sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    return hashlib.sha256(payload.encode()).hexdigest()
