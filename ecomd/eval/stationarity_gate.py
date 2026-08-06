"""Calibration-only stationarity gate and fixed-length scoring."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from typing import Any, TypeAlias

import numpy as np
import numpy.typing as npt
from scipy.spatial.distance import cdist, pdist

from .stylized_facts import compute_all

ArrayF: TypeAlias = npt.NDArray[np.float64]


@dataclass(frozen=True)
class GateConfig:
    block_length: int = 500
    gate_starts: tuple[int, ...] = (0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000)
    late_starts: tuple[int, ...] = (6000, 6500, 7000, 7500)
    max_w_star: int = 3000
    persistence_blocks: int = 3
    tolerance_quantile: float = 0.95
    bootstrap_replicates: int = 2000
    bootstrap_seed: int = 127900
    mad_floor: float = 1e-12

    def validate(self) -> None:
        if self.block_length < 3:
            raise ValueError("block_length must be at least 3")
        if self.persistence_blocks < 1:
            raise ValueError("persistence_blocks must be positive")
        if not 0.0 < self.tolerance_quantile < 1.0:
            raise ValueError("tolerance_quantile must lie in (0, 1)")
        if self.bootstrap_replicates < 1:
            raise ValueError("bootstrap_replicates must be positive")
        if len(self.late_starts) < 2:
            raise ValueError("at least two late blocks are required")
        if tuple(sorted(set(self.gate_starts))) != self.gate_starts:
            raise ValueError("gate_starts must be sorted and unique")
        if tuple(sorted(set(self.late_starts))) != self.late_starts:
            raise ValueError("late_starts must be sorted and unique")


@dataclass(frozen=True)
class GateFit:
    config: GateConfig
    location: tuple[float, float, float]
    scale: tuple[float, float, float]
    tolerance: float
    calibration_distance_medians: tuple[float, ...]
    w_star: int | None
    n_calibration_trajectories: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "config": asdict(self.config),
            "location": list(self.location),
            "scale": list(self.scale),
            "tolerance": self.tolerance,
            "calibration_distance_medians": list(self.calibration_distance_medians),
            "w_star": self.w_star,
            "n_calibration_trajectories": self.n_calibration_trajectories,
        }


@dataclass(frozen=True)
class GateEvaluation:
    distance_medians: tuple[float, ...]
    within_tolerance: tuple[bool, ...]
    frozen_w_star: int | None
    frozen_w_star_passes: bool | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def gate_fit_from_dict(payload: dict[str, Any]) -> GateFit:
    config_payload = payload.get("config")
    if not isinstance(config_payload, dict):
        raise ValueError("serialized gate fit lacks a config object")
    config = GateConfig(
        block_length=int(config_payload["block_length"]),
        gate_starts=tuple(int(value) for value in config_payload["gate_starts"]),
        late_starts=tuple(int(value) for value in config_payload["late_starts"]),
        max_w_star=int(config_payload["max_w_star"]),
        persistence_blocks=int(config_payload["persistence_blocks"]),
        tolerance_quantile=float(config_payload["tolerance_quantile"]),
        bootstrap_replicates=int(config_payload["bootstrap_replicates"]),
        bootstrap_seed=int(config_payload["bootstrap_seed"]),
        mad_floor=float(config_payload["mad_floor"]),
    )
    config.validate()
    location_values = tuple(float(value) for value in payload["location"])
    scale_values = tuple(float(value) for value in payload["scale"])
    if len(location_values) != 3 or len(scale_values) != 3:
        raise ValueError("serialized location and scale must each contain three values")
    return GateFit(
        config=config,
        location=(location_values[0], location_values[1], location_values[2]),
        scale=(scale_values[0], scale_values[1], scale_values[2]),
        tolerance=float(payload["tolerance"]),
        calibration_distance_medians=tuple(
            float(value) for value in payload["calibration_distance_medians"]
        ),
        w_star=int(payload["w_star"]) if payload["w_star"] is not None else None,
        n_calibration_trajectories=int(payload["n_calibration_trajectories"]),
    )


def delay_vectors(returns: ArrayF) -> ArrayF:
    r = np.asarray(returns, dtype=np.float64)
    if r.ndim != 1:
        raise ValueError(f"returns must be one-dimensional, got shape {r.shape}")
    if r.size < 3:
        raise ValueError("at least three returns are required")
    if not np.all(np.isfinite(r)):
        raise ValueError("returns contain non-finite values")
    return np.column_stack((r[:-1], np.abs(r[:-1]), np.abs(r[1:])))


def multivariate_energy_distance(x: ArrayF, y: ArrayF) -> float:
    a = np.asarray(x, dtype=np.float64)
    b = np.asarray(y, dtype=np.float64)
    if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[1]:
        raise ValueError(f"x and y must be 2-D with equal feature count, got {a.shape} and {b.shape}")
    if a.shape[0] < 2 or b.shape[0] < 2:
        raise ValueError("energy distance needs at least two rows per sample")
    cross = float(cdist(a, b, metric="euclidean").mean())
    within_a = float(2.0 * pdist(a, metric="euclidean").sum() / (a.shape[0] ** 2))
    within_b = float(2.0 * pdist(b, metric="euclidean").sum() / (b.shape[0] ** 2))
    return max(0.0, 2.0 * cross - within_a - within_b)


def fit_stationarity_gate(calibration_returns: ArrayF, config: GateConfig | None = None) -> GateFit:
    cfg = config or GateConfig()
    cfg.validate()
    trajectories = _trajectory_matrix(calibration_returns, cfg)
    location, scale = _fit_robust_scale(trajectories, cfg)
    candidate, late_null = _distance_tables(trajectories, location, scale, cfg)

    rng = np.random.default_rng(cfg.bootstrap_seed)
    n_trajectories, n_pairs = late_null.shape
    bootstrap: ArrayF = np.empty(cfg.bootstrap_replicates, dtype=np.float64)
    for replicate in range(cfg.bootstrap_replicates):
        trajectory_idx = rng.integers(0, n_trajectories, size=n_trajectories)
        pair_idx = rng.integers(0, n_pairs, size=n_trajectories)
        bootstrap[replicate] = float(np.median(late_null[trajectory_idx, pair_idx]))
    tolerance = float(np.quantile(bootstrap, cfg.tolerance_quantile))

    medians = np.median(candidate, axis=0)
    w_star = _select_w_star(medians, tolerance, cfg)
    location_tuple = (float(location[0]), float(location[1]), float(location[2]))
    scale_tuple = (float(scale[0]), float(scale[1]), float(scale[2]))
    return GateFit(
        config=cfg,
        location=location_tuple,
        scale=scale_tuple,
        tolerance=tolerance,
        calibration_distance_medians=tuple(float(v) for v in medians),
        w_star=w_star,
        n_calibration_trajectories=n_trajectories,
    )


def evaluate_stationarity_gate(heldout_returns: ArrayF, fit: GateFit) -> GateEvaluation:
    trajectories = _trajectory_matrix(heldout_returns, fit.config)
    candidate, _ = _distance_tables(
        trajectories,
        np.asarray(fit.location, dtype=np.float64),
        np.asarray(fit.scale, dtype=np.float64),
        fit.config,
    )
    medians = np.median(candidate, axis=0)
    passes = medians <= fit.tolerance
    frozen_pass: bool | None = None
    if fit.w_star is not None:
        frozen_pass = _w_passes(fit.w_star, passes, fit.config)
    return GateEvaluation(
        distance_medians=tuple(float(v) for v in medians),
        within_tolerance=tuple(bool(v) for v in passes),
        frozen_w_star=fit.w_star,
        frozen_w_star_passes=frozen_pass,
    )


def score_fixed_length(
    returns: ArrayF,
    w: int,
    length: int = 4000,
    volume: ArrayF | None = None,
) -> dict[str, dict[str, Any]]:
    r = np.asarray(returns, dtype=np.float64)
    if r.ndim != 1:
        raise ValueError("returns must be one-dimensional")
    if w < 0 or length < 1 or w + length > r.size:
        raise ValueError(f"invalid fixed-length slice [{w}, {w + length}) for {r.size} returns")
    v_slice: ArrayF | None = None
    if volume is not None:
        v = np.asarray(volume, dtype=np.float64)
        if v.shape != r.shape:
            raise ValueError(f"volume shape {v.shape} does not match returns shape {r.shape}")
        v_slice = v[w:w + length]
    facts = compute_all(r[w:w + length], volume=v_slice)
    return {name: result.to_dict() for name, result in facts.items()}


def score_fixed_length_grid(
    returns: ArrayF,
    starts: Iterable[int],
    length: int = 4000,
    volume: ArrayF | None = None,
) -> dict[int, dict[str, dict[str, Any]]]:
    return {int(w): score_fixed_length(returns, int(w), length=length, volume=volume) for w in starts}


def _trajectory_matrix(returns: ArrayF, config: GateConfig) -> ArrayF:
    x = np.asarray(returns, dtype=np.float64)
    if x.ndim != 2:
        raise ValueError(f"trajectory input must have shape (n, T), got {x.shape}")
    required = max((*config.gate_starts, *config.late_starts)) + config.block_length
    if x.shape[0] < 2:
        raise ValueError("at least two trajectories are required")
    if x.shape[1] < required:
        raise ValueError(f"need at least {required} returns per trajectory, got {x.shape[1]}")
    if not np.all(np.isfinite(x)):
        raise ValueError("trajectory matrix contains non-finite values")
    return x


def _block(returns: ArrayF, start: int, block_length: int, location: ArrayF, scale: ArrayF) -> ArrayF:
    vectors = delay_vectors(returns[start:start + block_length])
    return (vectors - location) / scale


def _fit_robust_scale(trajectories: ArrayF, config: GateConfig) -> tuple[ArrayF, ArrayF]:
    late = np.concatenate(
        [delay_vectors(row[start:start + config.block_length]) for row in trajectories for start in config.late_starts],
        axis=0,
    )
    location = np.median(late, axis=0)
    mad = np.median(np.abs(late - location), axis=0)
    scale = np.where(mad < config.mad_floor, 1.0, mad)
    return location.astype(np.float64), scale.astype(np.float64)


def _distance_tables(
    trajectories: ArrayF,
    location: ArrayF,
    scale: ArrayF,
    config: GateConfig,
) -> tuple[ArrayF, ArrayF]:
    late_pairs = [(left, right) for left in range(len(config.late_starts))
                  for right in range(left + 1, len(config.late_starts))]
    candidate: ArrayF = np.empty(
        (trajectories.shape[0], len(config.gate_starts)), dtype=np.float64
    )
    late_null: ArrayF = np.empty((trajectories.shape[0], len(late_pairs)), dtype=np.float64)
    for trajectory_idx, row in enumerate(trajectories):
        late_blocks = [
            _block(row, start, config.block_length, location, scale) for start in config.late_starts
        ]
        for start_idx, start in enumerate(config.gate_starts):
            current = _block(row, start, config.block_length, location, scale)
            candidate[trajectory_idx, start_idx] = float(np.median([
                multivariate_energy_distance(current, late) for late in late_blocks
            ]))
        for pair_idx, (left, right) in enumerate(late_pairs):
            late_null[trajectory_idx, pair_idx] = multivariate_energy_distance(
                late_blocks[left], late_blocks[right]
            )
    return candidate, late_null


def _select_w_star(medians: ArrayF, tolerance: float, config: GateConfig) -> int | None:
    passes = medians <= tolerance
    for start in config.gate_starts:
        if start > config.max_w_star:
            break
        if _w_passes(start, passes, config):
            return start
    return None


def _w_passes(start: int, passes: npt.NDArray[np.bool_], config: GateConfig) -> bool:
    index = {value: idx for idx, value in enumerate(config.gate_starts)}
    needed = [start + offset * config.block_length for offset in range(config.persistence_blocks)]
    return all(value in index and bool(passes[index[value]]) for value in needed)
