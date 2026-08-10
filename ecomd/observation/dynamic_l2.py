"""State-complete aggregate book dynamics with reconstructible price moves."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, TypeAlias, cast

import numpy as np
from numpy.typing import NDArray

FloatArray: TypeAlias = NDArray[np.float64]
IntArray: TypeAlias = NDArray[np.int64]
BoolArray: TypeAlias = NDArray[np.bool_]
TruthFamily: TypeAlias = Literal["latent_incremental", "observation_only"]

OBSERVED_TRACE_DECAYS = np.asarray((0.50, 0.80, 0.95), dtype=np.float64)


def _copy_rng_state(state: Mapping[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(dict(state))


@dataclass(frozen=True)
class DynamicL2Config:
    """Frozen aggregate-book and mark parameters."""

    n_levels: int = 5
    initial_queue: int = 32
    initial_mid_tick: int = 10_000
    p_hidden: float = 0.05
    p_add: float = 0.45
    removal_probabilities: tuple[float, float, float] = (0.45, 0.15, 0.40)
    eta: float = 0.70
    log_mu: float = float(np.log(7.0))
    size_gamma: float = 0.15
    true_trace_decay: float = 0.80

    def __post_init__(self) -> None:
        if self.n_levels < 1:
            raise ValueError("n_levels must be positive")
        if self.initial_queue < 2:
            raise ValueError("initial_queue must be at least two")
        if not 0.0 <= self.p_hidden < 1.0:
            raise ValueError("p_hidden must be in [0,1)")
        if not 0.0 < self.p_add < 1.0:
            raise ValueError("p_add must be in (0,1)")
        probabilities = np.asarray(self.removal_probabilities, dtype=np.float64)
        if probabilities.shape != (3,) or np.any(probabilities <= 0.0):
            raise ValueError("three positive removal probabilities are required")
        if not np.isclose(probabilities.sum(), 1.0, rtol=0.0, atol=1e-12):
            raise ValueError("removal probabilities must sum to one")
        if not 0.0 < self.true_trace_decay < 1.0:
            raise ValueError("true_trace_decay must be in (0,1)")


def reset_book(config: DynamicL2Config, mid_tick: int) -> IntArray:
    """Return the deterministic five-level book centered on ``mid_tick``."""
    levels: IntArray = np.arange(config.n_levels, dtype=np.int64)
    book: IntArray = np.empty(4 * config.n_levels, dtype=np.int64)
    book[0::4] = mid_tick + 1 + levels
    book[1::4] = config.initial_queue
    book[2::4] = mid_tick - levels
    book[3::4] = config.initial_queue
    return book


def _level_probabilities(config: DynamicL2Config) -> FloatArray:
    logits = -config.eta * np.arange(config.n_levels, dtype=np.float64)
    weights = np.exp(logits - float(logits.max()))
    return cast(FloatArray, weights / weights.sum())


def book_features(book: IntArray) -> tuple[float, float]:
    """Return pre-event best-queue imbalance and log depth ratio."""
    ask = float(book[1])
    bid = float(book[3])
    imbalance = (bid - ask) / (bid + ask)
    log_ratio = float(np.log((bid + 1.0) / (ask + 1.0)))
    return imbalance, log_ratio


@dataclass
class DynamicL2State:
    """All mutable state needed for exact continuation."""

    current_book: IntArray
    mid_tick: int
    next_event: int
    next_order_id: int
    true_trace: float
    observed_traces: FloatArray
    previous_signed_flow: int
    rng_state: dict[str, Any]

    def clone(self) -> DynamicL2State:
        return DynamicL2State(
            current_book=self.current_book.copy(),
            mid_tick=int(self.mid_tick),
            next_event=int(self.next_event),
            next_order_id=int(self.next_order_id),
            true_trace=float(self.true_trace),
            observed_traces=self.observed_traces.copy(),
            previous_signed_flow=int(self.previous_signed_flow),
            rng_state=_copy_rng_state(self.rng_state),
        )

    def to_checkpoint(self) -> dict[str, Any]:
        return {
            "format_version": 1,
            "current_book": self.current_book.copy(),
            "mid_tick": int(self.mid_tick),
            "next_event": int(self.next_event),
            "next_order_id": int(self.next_order_id),
            "true_trace": float(self.true_trace),
            "observed_traces": self.observed_traces.copy(),
            "previous_signed_flow": int(self.previous_signed_flow),
            "rng_state": _copy_rng_state(self.rng_state),
        }

    @classmethod
    def from_checkpoint(cls, payload: Mapping[str, Any]) -> DynamicL2State:
        version = int(payload.get("format_version", -1))
        if version != 1:
            raise ValueError(f"unsupported dynamic-L2 format_version={version}")
        return cls(
            current_book=np.asarray(payload["current_book"], dtype=np.int64).copy(),
            mid_tick=int(payload["mid_tick"]),
            next_event=int(payload["next_event"]),
            next_order_id=int(payload["next_order_id"]),
            true_trace=float(payload["true_trace"]),
            observed_traces=np.asarray(
                payload["observed_traces"], dtype=np.float64
            ).copy(),
            previous_signed_flow=int(payload["previous_signed_flow"]),
            rng_state=_copy_rng_state(payload["rng_state"]),
        )


@dataclass(frozen=True)
class DynamicL2Stream:
    """Generated messages, pre-event features and exact after-event state."""

    latent: FloatArray
    pre_imbalance: FloatArray
    pre_log_depth_ratio: FloatArray
    pre_true_trace: FloatArray
    pre_observed_traces: FloatArray
    event_index: IntArray
    event_type: IntArray
    order_id: IntArray
    size: IntArray
    price: IntArray
    direction: IntArray
    signed_flow: IntArray
    retained: BoolArray
    price_move: IntArray
    mid_tick: IntArray
    snapshots: IntArray

    @property
    def n_events(self) -> int:
        return int(self.event_type.size)


class DynamicL2Generator:
    """Generate one reconstructible aggregate message per latent step."""

    def __init__(
        self,
        config: DynamicL2Config,
        truth: TruthFamily,
        censor_rate: float,
    ) -> None:
        if truth not in ("latent_incremental", "observation_only"):
            raise ValueError(f"unknown truth family: {truth}")
        if not 0.0 <= censor_rate < 1.0:
            raise ValueError("censor_rate must be in [0,1)")
        self.config = config
        self.truth = truth
        self.censor_rate = censor_rate

    def init_state(
        self,
        *,
        seed: int,
        start_event: int = 0,
        start_order_id: int = 1,
    ) -> DynamicL2State:
        if start_event < 0:
            raise ValueError("start_event must be nonnegative")
        if start_order_id < 1:
            raise ValueError("start_order_id must be positive")
        generator = np.random.default_rng(seed)
        return DynamicL2State(
            current_book=reset_book(self.config, self.config.initial_mid_tick),
            mid_tick=self.config.initial_mid_tick,
            next_event=start_event,
            next_order_id=start_order_id,
            true_trace=0.0,
            observed_traces=np.zeros(OBSERVED_TRACE_DECAYS.size, dtype=np.float64),
            previous_signed_flow=0,
            rng_state=_copy_rng_state(generator.bit_generator.state),
        )

    def emit(
        self,
        state: DynamicL2State,
        latent: FloatArray,
        *,
        start_event: int,
    ) -> tuple[DynamicL2State, DynamicL2Stream]:
        z = np.asarray(latent, dtype=np.float64)
        if z.ndim != 1 or z.size < 1 or not np.isfinite(z).all():
            raise ValueError("latent must be a finite vector")
        if start_event != state.next_event:
            raise ValueError(
                f"dynamic-L2 clock mismatch: start={start_event}, "
                f"next={state.next_event}"
            )
        config = self.config
        expected_shape = (4 * config.n_levels,)
        if state.current_book.shape != expected_shape:
            raise ValueError("dynamic-L2 book shape is incompatible with config")
        if state.observed_traces.shape != OBSERVED_TRACE_DECAYS.shape:
            raise ValueError("dynamic-L2 trace shape is incompatible with config")
        if np.any(state.current_book[1::4] <= 0) or np.any(
            state.current_book[3::4] <= 0
        ):
            raise ValueError("dynamic-L2 queues must be positive")

        generator = np.random.default_rng()
        generator.bit_generator.state = _copy_rng_state(state.rng_state)
        current = state.current_book.copy()
        mid_tick = int(state.mid_tick)
        true_trace = float(state.true_trace)
        observed_traces = state.observed_traces.copy()
        previous_signed_flow = int(state.previous_signed_flow)
        n_events = z.size

        pre_imbalance = np.empty(n_events, dtype=np.float64)
        pre_log_depth_ratio = np.empty(n_events, dtype=np.float64)
        pre_true_trace = np.empty(n_events, dtype=np.float64)
        pre_observed_traces = np.empty(
            (n_events, OBSERVED_TRACE_DECAYS.size), dtype=np.float64
        )
        event_type = np.empty(n_events, dtype=np.int64)
        size = np.empty(n_events, dtype=np.int64)
        price = np.empty(n_events, dtype=np.int64)
        direction = np.empty(n_events, dtype=np.int64)
        signed_flow = np.empty(n_events, dtype=np.int64)
        retained = np.empty(n_events, dtype=np.bool_)
        price_move = np.zeros(n_events, dtype=np.int64)
        mid_path = np.empty(n_events, dtype=np.int64)
        snapshots = np.empty((n_events, current.size), dtype=np.int64)

        level_probabilities = _level_probabilities(config)
        removal_types = np.asarray((2, 3, 4), dtype=np.int64)
        removal_probabilities = np.asarray(
            config.removal_probabilities, dtype=np.float64
        )

        for index, value in enumerate(z):
            imbalance, log_ratio = book_features(current)
            pre_imbalance[index] = imbalance
            pre_log_depth_ratio[index] = log_ratio
            pre_true_trace[index] = true_trace
            pre_observed_traces[index] = observed_traces

            if self.truth == "latent_incremental":
                logit = 2.0 * (
                    0.65 * value + 0.50 * true_trace + 0.40 * imbalance
                )
            else:
                logit = 2.0 * (0.70 * true_trace + 0.55 * imbalance)
            probability_positive = 1.0 / (
                1.0 + np.exp(-np.clip(logit, -40.0, 40.0))
            )
            flow = 1 if generator.random() < probability_positive else -1
            addition = generator.random() < config.p_add
            action = 1 if addition else -1
            side = flow * action
            hidden = generator.random() < config.p_hidden
            kind = 1 if addition else int(
                generator.choice(removal_types, p=removal_probabilities)
            )
            if hidden:
                kind = 5
            event_level_probabilities = level_probabilities
            if not hidden and not addition:
                event_level_probabilities = level_probabilities.copy()
                for candidate_level in range(1, config.n_levels):
                    candidate_column = 4 * candidate_level + (
                        3 if side == 1 else 1
                    )
                    if current[candidate_column] <= 1:
                        event_level_probabilities[candidate_level] = 0.0
                event_level_probabilities /= event_level_probabilities.sum()
            level = int(
                generator.choice(config.n_levels, p=event_level_probabilities)
            )
            poisson_mean = float(
                np.exp(
                    np.clip(
                        config.log_mu + config.size_gamma * abs(value), -20.0, 20.0
                    )
                )
            )
            requested_size = 1 + int(generator.poisson(poisson_mean))
            size_column = 4 * level + (3 if side == 1 else 1)
            event_price = int(current[4 * level + (2 if side == 1 else 0)])
            actual_size = requested_size
            move = 0

            if not hidden:
                if addition:
                    current[size_column] += actual_size
                else:
                    available = int(current[size_column])
                    if level == 0 and actual_size >= available:
                        actual_size = available
                        move = flow
                        mid_tick += move
                        current = reset_book(config, mid_tick)
                    else:
                        actual_size = min(actual_size, available - 1)
                        if actual_size < 1:
                            raise RuntimeError(
                                "non-best queue cannot support a positive removal at "
                                f"event={start_event + index}, level={level}"
                            )
                        current[size_column] -= actual_size

            keep = (not hidden) and generator.random() >= self.censor_rate
            if not hidden:
                true_trace = (
                    config.true_trace_decay * true_trace
                    + (1.0 - config.true_trace_decay) * flow
                )
            if keep:
                observed_traces = (
                    OBSERVED_TRACE_DECAYS * observed_traces
                    + (1.0 - OBSERVED_TRACE_DECAYS) * flow
                )
            previous_signed_flow = flow

            event_type[index] = kind
            size[index] = actual_size
            price[index] = event_price
            direction[index] = side
            signed_flow[index] = flow
            retained[index] = keep
            price_move[index] = move
            mid_path[index] = mid_tick
            snapshots[index] = current

        event_index: IntArray = start_event + np.arange(n_events, dtype=np.int64)
        order_id = np.arange(
            state.next_order_id,
            state.next_order_id + n_events,
            dtype=np.int64,
        )
        stream = DynamicL2Stream(
            latent=z.copy(),
            pre_imbalance=pre_imbalance,
            pre_log_depth_ratio=pre_log_depth_ratio,
            pre_true_trace=pre_true_trace,
            pre_observed_traces=pre_observed_traces,
            event_index=event_index,
            event_type=event_type,
            order_id=order_id,
            size=size,
            price=price,
            direction=direction,
            signed_flow=signed_flow,
            retained=retained,
            price_move=price_move,
            mid_tick=mid_path,
            snapshots=snapshots,
        )
        next_state = DynamicL2State(
            current_book=current,
            mid_tick=mid_tick,
            next_event=start_event + n_events,
            next_order_id=state.next_order_id + n_events,
            true_trace=true_trace,
            observed_traces=observed_traces,
            previous_signed_flow=previous_signed_flow,
            rng_state=_copy_rng_state(generator.bit_generator.state),
        )
        return next_state, stream


def reconstruct_dynamic_l2(
    stream: DynamicL2Stream,
    config: DynamicL2Config,
    *,
    initial_mid_tick: int | None = None,
) -> tuple[IntArray, IntArray, IntArray]:
    """Reconstruct books, mid ticks and moves from displayed message fields."""
    mid_tick = config.initial_mid_tick if initial_mid_tick is None else initial_mid_tick
    current = reset_book(config, mid_tick)
    snapshots = np.empty_like(stream.snapshots)
    mid_path = np.empty_like(stream.mid_tick)
    moves = np.zeros_like(stream.price_move)

    for index in range(stream.n_events):
        kind = int(stream.event_type[index])
        side = int(stream.direction[index])
        if side not in (-1, 1):
            raise ValueError("message direction must be -1 or +1")
        if kind not in (1, 2, 3, 4, 5):
            raise ValueError("unknown dynamic-L2 event type")
        if int(stream.size[index]) < 1:
            raise ValueError("dynamic-L2 message sizes must be positive")
        if kind != 5:
            price_columns = current[2::4] if side == 1 else current[0::4]
            matches = np.flatnonzero(price_columns == int(stream.price[index]))
            if matches.size != 1:
                raise ValueError("event price is outside the displayed dynamic book")
            level = int(matches[0])
            size_column = 4 * level + (3 if side == 1 else 1)
            action = 1 if kind == 1 else -1
            if action == 1:
                current[size_column] += int(stream.size[index])
            else:
                available = int(current[size_column])
                event_size = int(stream.size[index])
                if event_size > available:
                    raise ValueError("removal exceeds displayed queue")
                if level == 0 and event_size == available:
                    flow = side * action
                    moves[index] = flow
                    mid_tick += flow
                    current = reset_book(config, mid_tick)
                else:
                    current[size_column] -= event_size
                    if current[size_column] <= 0:
                        raise RuntimeError("non-best reconstruction queue is non-positive")
        snapshots[index] = current
        mid_path[index] = mid_tick
    return snapshots, mid_path, moves
