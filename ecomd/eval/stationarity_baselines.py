"""Pre-specified classical stationarity comparator for experiment 127."""

from __future__ import annotations

import warnings
from dataclasses import asdict, dataclass
from typing import Any, TypeAlias

import numpy as np
import numpy.typing as npt
from statsmodels.tools.sm_exceptions import InterpolationWarning
from statsmodels.tsa.stattools import adfuller, kpss

ArrayF: TypeAlias = npt.NDArray[np.float64]
ArrayB: TypeAlias = npt.NDArray[np.bool_]


@dataclass(frozen=True)
class ADFKPSSConfig:
    block_length: int = 500
    gate_starts: tuple[int, ...] = (0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000)
    max_w_star: int = 3000
    persistence_blocks: int = 3
    trajectory_pass_fraction: float = 0.5
    adf_alpha: float = 0.05
    kpss_alpha: float = 0.05
    adf_maxlag: int = 10

    def validate(self) -> None:
        if self.block_length < 3:
            raise ValueError("block_length must be at least 3")
        if self.persistence_blocks < 1:
            raise ValueError("persistence_blocks must be positive")
        if not 0.0 < self.trajectory_pass_fraction <= 1.0:
            raise ValueError("trajectory_pass_fraction must lie in (0, 1]")
        if not 0.0 < self.adf_alpha < 1.0 or not 0.0 < self.kpss_alpha < 1.0:
            raise ValueError("test alpha values must lie in (0, 1)")
        if self.adf_maxlag < 0:
            raise ValueError("adf_maxlag must be nonnegative")
        if tuple(sorted(set(self.gate_starts))) != self.gate_starts:
            raise ValueError("gate_starts must be sorted and unique")


@dataclass(frozen=True)
class ADFKPSSFit:
    config: ADFKPSSConfig
    block_pass_fractions: tuple[float, ...]
    within_stationarity_rule: tuple[bool, ...]
    w_star: int | None
    n_calibration_trajectories: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def fit_adf_kpss_gate(
    calibration_returns: ArrayF,
    config: ADFKPSSConfig | None = None,
) -> ADFKPSSFit:
    cfg = config or ADFKPSSConfig()
    cfg.validate()
    trajectories = np.asarray(calibration_returns, dtype=np.float64)
    if trajectories.ndim != 2 or trajectories.shape[0] < 2:
        raise ValueError("calibration_returns must have shape (n>=2, T)")
    required = max(cfg.gate_starts) + cfg.block_length
    if trajectories.shape[1] < required:
        raise ValueError(f"need at least {required} returns, got {trajectories.shape[1]}")
    if not np.all(np.isfinite(trajectories)):
        raise ValueError("calibration_returns contains non-finite values")

    fractions: list[float] = []
    block_passes: list[bool] = []
    for start in cfg.gate_starts:
        trajectory_passes = [
            _trajectory_block_pass(row[start:start + cfg.block_length], cfg)
            for row in trajectories
        ]
        fraction = float(np.mean(trajectory_passes))
        fractions.append(fraction)
        block_passes.append(fraction >= cfg.trajectory_pass_fraction)

    pass_array: ArrayB = np.asarray(block_passes, dtype=np.bool_)
    w_star = select_persistent_start(pass_array, cfg.gate_starts, cfg.max_w_star,
                                     cfg.block_length, cfg.persistence_blocks)
    return ADFKPSSFit(
        config=cfg,
        block_pass_fractions=tuple(fractions),
        within_stationarity_rule=tuple(block_passes),
        w_star=w_star,
        n_calibration_trajectories=int(trajectories.shape[0]),
    )


def select_persistent_start(
    block_passes: ArrayB,
    starts: tuple[int, ...],
    max_start: int,
    block_length: int,
    persistence_blocks: int,
) -> int | None:
    passes = np.asarray(block_passes, dtype=np.bool_)
    if passes.ndim != 1 or passes.size != len(starts):
        raise ValueError("block_passes must be one-dimensional and aligned with starts")
    index = {value: idx for idx, value in enumerate(starts)}
    for start in starts:
        if start > max_start:
            break
        needed = [start + offset * block_length for offset in range(persistence_blocks)]
        if all(value in index and bool(passes[index[value]]) for value in needed):
            return start
    return None


def _trajectory_block_pass(block: ArrayF, config: ADFKPSSConfig) -> bool:
    return _series_pass(block, config) and _series_pass(np.abs(block), config)


def _series_pass(series: ArrayF, config: ADFKPSSConfig) -> bool:
    if np.ptp(series) <= np.finfo(np.float64).eps:
        return False
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", InterpolationWarning)
            adf_p = float(adfuller(
                series,
                maxlag=config.adf_maxlag,
                regression="c",
                autolag="AIC",
            )[1])
            kpss_p = float(kpss(series, regression="c", nlags="auto")[1])
    except (ValueError, np.linalg.LinAlgError):
        return False
    return adf_p < config.adf_alpha and kpss_p > config.kpss_alpha
