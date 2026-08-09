"""Checkpointable aggregate-L2 emission from EcoMD latent flow."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .l2_emission import AggregateL2EmissionConfig, SyntheticL2Stream

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


def _initial_book(config: AggregateL2EmissionConfig) -> IntArray:
    levels = np.arange(config.n_levels, dtype=np.int64)
    book = np.empty(4 * config.n_levels, dtype=np.int64)
    book[0::4] = config.best_ask + levels
    book[1::4] = config.initial_queue
    book[2::4] = config.best_bid - levels
    book[3::4] = config.initial_queue
    return book


def _level_probabilities(config: AggregateL2EmissionConfig) -> FloatArray:
    logits = -config.eta * np.arange(config.n_levels, dtype=np.float64)
    weights = np.exp(logits - float(logits.max()))
    return weights / weights.sum()


@dataclass(frozen=True)
class EcoMDL2AdapterConfig:
    """Fixed model-to-schema semantics for aggregate-L2 emission."""

    dt: float
    beta_emit: float = 2.0
    l2: AggregateL2EmissionConfig = field(default_factory=AggregateL2EmissionConfig)
    sign_anchor: str = "positive_raw_excess_demand_is_buy_pressure"

    def __post_init__(self) -> None:
        if self.dt <= 0.0:
            raise ValueError("dt must be positive")
        if self.beta_emit <= 0.0:
            raise ValueError("beta_emit must be positive under the fixed sign anchor")
        if self.sign_anchor != "positive_raw_excess_demand_is_buy_pressure":
            raise ValueError("unsupported sign anchor")


@dataclass
class EcoMDL2AdapterState:
    """Complete state needed for exact chunked message emission."""

    current_book: IntArray
    next_step: int
    next_order_id: int
    rng_state: dict[str, Any]

    def clone(self) -> EcoMDL2AdapterState:
        return EcoMDL2AdapterState(
            current_book=self.current_book.copy(),
            next_step=int(self.next_step),
            next_order_id=int(self.next_order_id),
            rng_state=copy.deepcopy(self.rng_state),
        )

    def to_checkpoint(self) -> dict[str, Any]:
        return {
            "format_version": 1,
            "current_book": self.current_book.copy(),
            "next_step": int(self.next_step),
            "next_order_id": int(self.next_order_id),
            "rng_state": copy.deepcopy(self.rng_state),
        }

    @classmethod
    def from_checkpoint(cls, payload: dict[str, Any]) -> EcoMDL2AdapterState:
        version = int(payload.get("format_version", -1))
        if version != 1:
            raise ValueError(f"unsupported adapter format_version={version}")
        return cls(
            current_book=np.asarray(payload["current_book"], dtype=np.int64).copy(),
            next_step=int(payload["next_step"]),
            next_order_id=int(payload["next_order_id"]),
            rng_state=copy.deepcopy(payload["rng_state"]),
        )


class EcoMDL2Adapter:
    """Emit one aggregate-L2 message after each EcoMD transition."""

    def __init__(self, config: EcoMDL2AdapterConfig) -> None:
        self.config = config

    def init_state(
        self,
        *,
        seed: int,
        start_step: int = 0,
        start_order_id: int = 1,
    ) -> EcoMDL2AdapterState:
        if start_step < 0:
            raise ValueError("start_step must be nonnegative")
        if start_order_id < 1:
            raise ValueError("start_order_id must be positive")
        generator = np.random.default_rng(seed)
        return EcoMDL2AdapterState(
            current_book=_initial_book(self.config.l2),
            next_step=start_step,
            next_order_id=start_order_id,
            rng_state=copy.deepcopy(generator.bit_generator.state),
        )

    def emit(
        self,
        state: EcoMDL2AdapterState,
        latent_flow_alignment: FloatArray,
        *,
        start_step: int,
    ) -> tuple[EcoMDL2AdapterState, SyntheticL2Stream]:
        z = np.asarray(latent_flow_alignment, dtype=np.float64)
        if z.ndim != 1 or z.size < 1 or not np.isfinite(z).all():
            raise ValueError("latent_flow_alignment must be a finite vector")
        if start_step != state.next_step:
            raise ValueError(
                f"adapter clock mismatch: start_step={start_step}, next_step={state.next_step}"
            )
        l2 = self.config.l2
        if state.current_book.shape != (4 * l2.n_levels,):
            raise ValueError("adapter book shape is incompatible with its configuration")

        generator = np.random.default_rng()
        generator.bit_generator.state = copy.deepcopy(state.rng_state)
        levels_probability = _level_probabilities(l2)
        removal_types = np.asarray((2, 3, 4), dtype=np.int64)
        removal_probability = np.asarray(l2.removal_probabilities, dtype=np.float64)
        n_events = z.size
        event_type = np.empty(n_events, dtype=np.int64)
        size = np.empty(n_events, dtype=np.int64)
        price = np.empty(n_events, dtype=np.int64)
        direction = np.empty(n_events, dtype=np.int64)
        snapshots = np.empty((n_events, state.current_book.size), dtype=np.int64)
        current = state.current_book.copy()

        for index, value in enumerate(z):
            hidden = generator.random() < l2.p_hidden
            addition = generator.random() < l2.p_add
            probability_positive = 1.0 / (
                1.0 + np.exp(-np.clip(2.0 * self.config.beta_emit * value, -40.0, 40.0))
            )
            signed_flow = 1 if generator.random() < probability_positive else -1
            action = 1 if addition else -1
            event_direction = signed_flow * action
            kind = 1 if addition else int(
                generator.choice(removal_types, p=removal_probability)
            )
            if hidden:
                kind = 5
            level = int(generator.choice(l2.n_levels, p=levels_probability))
            poisson_mean = float(
                np.exp(np.clip(l2.log_mu + l2.gamma * abs(value), -20.0, 20.0))
            )
            event_size = 1 + int(generator.poisson(poisson_mean))
            event_price = (
                l2.best_bid - level
                if event_direction == 1
                else l2.best_ask + level
            )
            if not hidden:
                size_column = 4 * level + (3 if event_direction == 1 else 1)
                current[size_column] += action * event_size
                if current[size_column] <= 0:
                    raise RuntimeError(
                        "adapter produced a non-positive queue at "
                        f"step={start_step + index}, column={size_column}"
                    )
            event_type[index] = kind
            size[index] = event_size
            price[index] = event_price
            direction[index] = event_direction
            snapshots[index] = current

        order_id = np.arange(
            state.next_order_id,
            state.next_order_id + n_events,
            dtype=np.int64,
        )
        absolute_steps = start_step + np.arange(n_events, dtype=np.int64)
        stream = SyntheticL2Stream(
            latent=z.copy(),
            time=(absolute_steps.astype(np.float64) + 1.0) * self.config.dt,
            event_type=event_type,
            order_id=order_id,
            size=size,
            price=price,
            direction=direction,
            initial_book=state.current_book.copy(),
            snapshots=snapshots,
        )
        next_state = EcoMDL2AdapterState(
            current_book=current,
            next_step=start_step + n_events,
            next_order_id=state.next_order_id + n_events,
            rng_state=copy.deepcopy(generator.bit_generator.state),
        )
        return next_state, stream
