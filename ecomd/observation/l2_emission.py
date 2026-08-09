"""Minimal aggregate-depth emission and recovery primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

import numpy as np
from numpy.typing import NDArray

FloatArray: TypeAlias = NDArray[np.float64]
IntArray: TypeAlias = NDArray[np.int64]


@dataclass(frozen=True)
class AggregateL2EmissionConfig:
    """Parameters of the synthetic aggregate L2 observation operator."""

    n_levels: int = 5
    initial_queue: int = 100_000
    best_bid: int = 10_000
    best_ask: int = 10_001
    p_hidden: float = 0.08
    p_add: float = 0.50
    removal_probabilities: tuple[float, float, float] = (0.45, 0.15, 0.40)
    eta: float = 0.70
    log_mu: float = float(np.log(7.0))
    gamma: float = 0.25

    def __post_init__(self) -> None:
        if self.n_levels < 1:
            raise ValueError("n_levels must be positive")
        if self.initial_queue < 1:
            raise ValueError("initial_queue must be positive")
        if self.best_ask <= self.best_bid:
            raise ValueError("best ask must exceed best bid")
        if not 0.0 <= self.p_hidden < 1.0:
            raise ValueError("p_hidden must be in [0,1)")
        if not 0.0 < self.p_add < 1.0:
            raise ValueError("p_add must be in (0,1)")
        probabilities = np.asarray(self.removal_probabilities, dtype=np.float64)
        if probabilities.shape != (3,) or np.any(probabilities <= 0.0):
            raise ValueError("three positive removal probabilities are required")
        if not np.isclose(probabilities.sum(), 1.0, rtol=0.0, atol=1e-12):
            raise ValueError("removal probabilities must sum to one")


@dataclass(frozen=True)
class SyntheticL2Stream:
    """One emitted message stream and its exact after-event snapshots."""

    latent: FloatArray
    time: FloatArray
    event_type: IntArray
    order_id: IntArray
    size: IntArray
    price: IntArray
    direction: IntArray
    initial_book: IntArray
    snapshots: IntArray

    @property
    def n_events(self) -> int:
        return int(self.event_type.size)


@dataclass(frozen=True)
class ParameterFit:
    """A numerical maximum-likelihood fit."""

    values: FloatArray
    converged: bool
    iterations: int


def simulate_latent_ar1(
    n_events: int,
    rho: float,
    generator: np.random.Generator,
) -> FloatArray:
    """Draw a stationary unit-variance Gaussian AR(1) path."""
    if n_events < 1:
        raise ValueError("n_events must be positive")
    if abs(rho) >= 1.0:
        raise ValueError("rho must have absolute value below one")
    innovations = generator.standard_normal(n_events)
    latent: FloatArray = np.empty(n_events, dtype=np.float64)
    latent[0] = innovations[0]
    innovation_scale = float(np.sqrt(1.0 - rho * rho))
    for index in range(1, n_events):
        latent[index] = rho * latent[index - 1] + innovation_scale * innovations[index]
    return latent


def _initial_book(config: AggregateL2EmissionConfig) -> IntArray:
    book: IntArray = np.empty(4 * config.n_levels, dtype=np.int64)
    levels: IntArray = np.arange(config.n_levels, dtype=np.int64)
    book[0::4] = config.best_ask + levels
    book[1::4] = config.initial_queue
    book[2::4] = config.best_bid - levels
    book[3::4] = config.initial_queue
    return book


def _level_probabilities(n_levels: int, eta: float) -> FloatArray:
    logits = -eta * np.arange(n_levels, dtype=np.float64)
    logits -= float(logits.max())
    probabilities = np.exp(logits)
    probabilities /= probabilities.sum()
    return probabilities


def _book_from_deltas(
    initial_book: IntArray,
    deltas: IntArray,
) -> IntArray:
    n_events, n_queue_cells = deltas.shape
    n_levels = n_queue_cells // 2
    queue_paths = np.cumsum(deltas, axis=0, dtype=np.int64)
    initial_queues = np.concatenate(
        (initial_book[1::4], initial_book[3::4])
    ).astype(np.int64, copy=False)
    queue_paths += initial_queues[None, :]
    if np.any(queue_paths <= 0):
        first = np.argwhere(queue_paths <= 0)[0]
        raise RuntimeError(
            "emission produced a non-positive queue at "
            f"event={int(first[0])}, cell={int(first[1])}"
        )
    snapshots = np.broadcast_to(initial_book, (n_events, initial_book.size)).copy()
    snapshots[:, 1::4] = queue_paths[:, :n_levels]
    snapshots[:, 3::4] = queue_paths[:, n_levels:]
    return snapshots


def emit_aggregate_l2(
    latent: FloatArray,
    beta: float,
    config: AggregateL2EmissionConfig,
    generator: np.random.Generator,
) -> SyntheticL2Stream:
    """Emit LOBSTER-shaped aggregate messages conditional on ``latent``."""
    z = np.asarray(latent, dtype=np.float64)
    if z.ndim != 1 or z.size < 1 or not np.isfinite(z).all():
        raise ValueError("latent must be a finite one-dimensional array")
    n_events = z.size
    hidden = generator.random(n_events) < config.p_hidden
    additions = generator.random(n_events) < config.p_add
    probability_positive = 1.0 / (1.0 + np.exp(-np.clip(2.0 * beta * z, -40.0, 40.0)))
    signed_flow = np.where(generator.random(n_events) < probability_positive, 1, -1)
    action = np.where(additions, 1, -1)
    direction = (signed_flow * action).astype(np.int64)

    event_type = np.ones(n_events, dtype=np.int64)
    removal = ~additions
    event_type[removal] = generator.choice(
        np.asarray((2, 3, 4), dtype=np.int64),
        size=int(np.count_nonzero(removal)),
        p=np.asarray(config.removal_probabilities, dtype=np.float64),
    )
    event_type[hidden] = 5

    levels = generator.choice(
        np.arange(config.n_levels, dtype=np.int64),
        size=n_events,
        p=_level_probabilities(config.n_levels, config.eta),
    )
    poisson_mean = np.exp(
        np.clip(config.log_mu + config.gamma * np.abs(z), -20.0, 20.0)
    )
    size: IntArray = np.asarray(1 + generator.poisson(poisson_mean), dtype=np.int64)
    price = np.where(
        direction == 1,
        config.best_bid - levels,
        config.best_ask + levels,
    ).astype(np.int64)

    initial_book = _initial_book(config)
    deltas = np.zeros((n_events, 2 * config.n_levels), dtype=np.int64)
    visible = ~hidden
    ask = visible & (direction == -1)
    bid = visible & (direction == 1)
    indices = np.arange(n_events)
    deltas[indices[ask], levels[ask]] = action[ask] * size[ask]
    deltas[indices[bid], config.n_levels + levels[bid]] = action[bid] * size[bid]
    snapshots = _book_from_deltas(initial_book, deltas)
    return SyntheticL2Stream(
        latent=z.copy(),
        time=np.arange(n_events, dtype=np.float64) / 1_000.0,
        event_type=event_type,
        order_id=np.arange(1, n_events + 1, dtype=np.int64),
        size=size,
        price=price,
        direction=direction,
        initial_book=initial_book,
        snapshots=snapshots,
    )


def reconstruct_aggregate_book(
    stream: SyntheticL2Stream,
) -> IntArray:
    """Reconstruct after-event snapshots using only the initial book and messages."""
    n_levels = stream.initial_book.size // 4
    if stream.initial_book.size != 4 * n_levels or n_levels < 1:
        raise ValueError("initial book does not have LOBSTER 4L layout")
    if any(
        array.size != stream.n_events
        for array in (
            stream.time,
            stream.order_id,
            stream.size,
            stream.price,
            stream.direction,
        )
    ):
        raise ValueError("message arrays have inconsistent lengths")
    if np.any(stream.size <= 0):
        raise ValueError("message sizes must be positive")
    if np.any(~np.isin(stream.direction, (-1, 1))):
        raise ValueError("message directions must be -1 or +1")
    if np.any(~np.isin(stream.event_type, (1, 2, 3, 4, 5))):
        raise ValueError("unknown event type")

    ask_prices = stream.initial_book[0::4]
    bid_prices = stream.initial_book[2::4]
    ask_lookup = {int(price): level for level, price in enumerate(ask_prices)}
    bid_lookup = {int(price): level for level, price in enumerate(bid_prices)}
    snapshots = np.empty((stream.n_events, stream.initial_book.size), dtype=np.int64)
    current = stream.initial_book.copy()
    for index in range(stream.n_events):
        event_type = int(stream.event_type[index])
        if event_type == 5:
            snapshots[index] = current
            continue
        direction = int(stream.direction[index])
        price = int(stream.price[index])
        lookup = bid_lookup if direction == 1 else ask_lookup
        if price not in lookup:
            raise ValueError(f"event price {price} is outside the displayed book")
        level = lookup[price]
        size_column = 4 * level + (3 if direction == 1 else 1)
        action = 1 if event_type == 1 else -1
        current[size_column] += action * int(stream.size[index])
        if current[size_column] <= 0:
            raise RuntimeError(
                f"reconstruction produced a non-positive queue at event={index}"
            )
        snapshots[index] = current
    return snapshots


def fit_flow_slope(latent: FloatArray, signed_flow: IntArray) -> ParameterFit:
    """Fit ``P(q=1|z)=sigmoid(2 beta z)`` by Newton iteration."""
    z = np.asarray(latent, dtype=np.float64)
    q = np.asarray(signed_flow, dtype=np.int64)
    if z.ndim != 1 or q.shape != z.shape or z.size < 2:
        raise ValueError("latent and signed_flow must be aligned vectors")
    if np.any(~np.isin(q, (-1, 1))) or not np.isfinite(z).all():
        raise ValueError("invalid signed-flow regression data")
    target = (q + 1.0) / 2.0
    beta = 0.0
    for iteration in range(1, 101):
        logits = np.clip(2.0 * beta * z, -40.0, 40.0)
        probability = 1.0 / (1.0 + np.exp(-logits))
        score = float(np.sum(2.0 * z * (target - probability)))
        information = float(np.sum(4.0 * z * z * probability * (1.0 - probability)))
        if not np.isfinite(information) or information <= 0.0:
            return ParameterFit(np.asarray((beta,)), False, iteration)
        step = score / information
        beta += step
        if abs(step) <= 1e-12 * (1.0 + abs(beta)):
            return ParameterFit(np.asarray((beta,), dtype=np.float64), True, iteration)
    return ParameterFit(np.asarray((beta,), dtype=np.float64), False, 100)


def bernoulli_log_likelihood(
    beta: float,
    latent: FloatArray,
    signed_flow: IntArray,
) -> float:
    """Return the Bernoulli log likelihood for the signed-flow model."""
    z = np.asarray(latent, dtype=np.float64)
    q = np.asarray(signed_flow, dtype=np.int64)
    if z.shape != q.shape:
        raise ValueError("latent and signed_flow shapes differ")
    target = (q + 1.0) / 2.0
    logits = 2.0 * beta * z
    return float(np.sum(target * -np.logaddexp(0.0, -logits) + (1.0 - target) * -np.logaddexp(0.0, logits)))


def fit_logistic_features(
    features: FloatArray,
    signed_flow: IntArray,
    *,
    add_intercept: bool = True,
) -> ParameterFit:
    """Fit a Bernoulli logistic model to arbitrary fixed features."""
    x = np.asarray(features, dtype=np.float64)
    q = np.asarray(signed_flow, dtype=np.int64)
    if x.ndim != 2 or q.ndim != 1 or x.shape[0] != q.size or q.size < 2:
        raise ValueError("features and signed_flow must have aligned rows")
    if np.any(~np.isin(q, (-1, 1))) or not np.isfinite(x).all():
        raise ValueError("invalid logistic regression data")
    design = np.column_stack((np.ones(q.size), x)) if add_intercept else x
    if design.shape[1] < 1:
        raise ValueError("logistic model has no coefficients")
    target = (q.astype(np.float64) + 1.0) / 2.0
    values = np.zeros(design.shape[1], dtype=np.float64)
    for iteration in range(1, 101):
        logits = np.clip(design @ values, -40.0, 40.0)
        probability = 1.0 / (1.0 + np.exp(-logits))
        score = design.T @ (target - probability)
        information = design.T @ (
            (probability * (1.0 - probability))[:, None] * design
        )
        try:
            step = np.linalg.solve(information, score)
        except np.linalg.LinAlgError:
            return ParameterFit(values, False, iteration)
        values = values + step
        if float(np.max(np.abs(step))) <= 1e-11 * (
            1.0 + float(np.max(np.abs(values)))
        ):
            return ParameterFit(values, True, iteration)
    return ParameterFit(values, False, 100)


def logistic_feature_log_likelihood(
    coefficients: FloatArray,
    features: FloatArray,
    signed_flow: IntArray,
    *,
    add_intercept: bool = True,
) -> float:
    """Score a fixed-feature Bernoulli logistic model."""
    values = np.asarray(coefficients, dtype=np.float64)
    x = np.asarray(features, dtype=np.float64)
    q = np.asarray(signed_flow, dtype=np.int64)
    if x.ndim != 2 or q.ndim != 1 or x.shape[0] != q.size:
        raise ValueError("features and signed_flow must have aligned rows")
    design = np.column_stack((np.ones(q.size), x)) if add_intercept else x
    if values.shape != (design.shape[1],):
        raise ValueError("coefficient and feature dimensions differ")
    if np.any(~np.isin(q, (-1, 1))) or not np.isfinite(design).all():
        raise ValueError("invalid logistic regression data")
    target = (q.astype(np.float64) + 1.0) / 2.0
    logits = design @ values
    return float(
        np.sum(
            target * -np.logaddexp(0.0, -logits)
            + (1.0 - target) * -np.logaddexp(0.0, logits)
        )
    )


def fit_level_decay(levels: IntArray, n_levels: int) -> ParameterFit:
    """Fit the truncated level law proportional to ``exp(-eta level)``."""
    observed = np.asarray(levels, dtype=np.int64)
    if observed.ndim != 1 or observed.size < 2:
        raise ValueError("at least two level observations are required")
    if np.any((observed < 0) | (observed >= n_levels)):
        raise ValueError("level observation outside support")
    target_mean = float(observed.mean())
    support: FloatArray = np.arange(n_levels, dtype=np.float64)
    low, high = -10.0, 10.0
    for iteration in range(1, 101):
        eta = (low + high) / 2.0
        probabilities = _level_probabilities(n_levels, eta)
        model_mean = float(np.dot(support, probabilities))
        if model_mean > target_mean:
            low = eta
        else:
            high = eta
        if high - low <= 1e-12:
            return ParameterFit(
                np.asarray(((low + high) / 2.0,), dtype=np.float64),
                True,
                iteration,
            )
    return ParameterFit(np.asarray(((low + high) / 2.0,)), False, 100)


def fit_size_model(latent: FloatArray, sizes: IntArray) -> ParameterFit:
    """Fit ``size-1 ~ Poisson(exp(log_mu + gamma |z|))``."""
    z = np.asarray(latent, dtype=np.float64)
    size = np.asarray(sizes, dtype=np.int64)
    if z.ndim != 1 or size.shape != z.shape or z.size < 2:
        raise ValueError("latent and size must be aligned vectors")
    if np.any(size < 1) or not np.isfinite(z).all():
        raise ValueError("invalid size regression data")
    response = size.astype(np.float64) - 1.0
    design = np.column_stack((np.ones(z.size), np.abs(z)))
    values = np.asarray((np.log(max(float(response.mean()), 1e-12)), 0.0))
    for iteration in range(1, 101):
        linear = np.clip(design @ values, -20.0, 20.0)
        mean = np.exp(linear)
        score = design.T @ (response - mean)
        information = design.T @ (mean[:, None] * design)
        try:
            step = np.linalg.solve(information, score)
        except np.linalg.LinAlgError:
            return ParameterFit(values.astype(np.float64), False, iteration)
        values = values + step
        if float(np.max(np.abs(step))) <= 1e-11 * (
            1.0 + float(np.max(np.abs(values)))
        ):
            return ParameterFit(values.astype(np.float64), True, iteration)
    return ParameterFit(values.astype(np.float64), False, 100)


def poisson_log_likelihood_without_constant(
    log_mu: float,
    gamma: float,
    latent: FloatArray,
    sizes: IntArray,
) -> float:
    """Return Poisson log likelihood with the parameter-free factorial omitted."""
    z = np.asarray(latent, dtype=np.float64)
    size = np.asarray(sizes, dtype=np.int64)
    if z.shape != size.shape:
        raise ValueError("latent and size shapes differ")
    response = size.astype(np.float64) - 1.0
    linear = np.clip(log_mu + gamma * np.abs(z), -20.0, 20.0)
    return float(np.sum(response * linear - np.exp(linear)))
