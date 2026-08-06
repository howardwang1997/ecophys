"""Canonical 11-fact acceptance bands and band-normalized scoring."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np

CANONICAL_FACT_BANDS: dict[str, tuple[float, float]] = {
    "autocorr_returns": (-0.1, 0.20),
    "hill_tail_index": (2.0, 4.0),
    "gain_loss_asymmetry": (-30.0, -3.0),
    "aggregational_gaussianity": (10.0, 200.0),
    "intermittency_fano": (5.0, 100.0),
    "acf_squared_returns": (0.15, 0.55),
    "conditional_kurtosis": (-1.0, 3.0),
    "dfa_hurst_abs_r": (0.6, 0.9),
    "leverage_effect": (-6.0, -0.5),
    "volume_volatility_corr": (0.3, 0.8),
    "zumbach_asymmetry": (0.001, 0.5),
}


@dataclass(frozen=True)
class BandScore:
    pass_count: int
    fact_count: int
    mean_normalized_distance: float
    per_fact_normalized_distance: dict[str, float]
    per_fact_pass: dict[str, bool]


def normalized_band_distance(value: float, lower: float, upper: float) -> float:
    if not np.isfinite(value):
        raise ValueError("value must be finite")
    if not np.isfinite(lower) or not np.isfinite(upper) or lower >= upper:
        raise ValueError("band must contain finite ordered bounds")
    if lower <= value <= upper:
        return 0.0
    nearest = lower if value < lower else upper
    return float(abs(value - nearest) / (upper - lower))


def score_against_canonical_bands(estimates: Mapping[str, float]) -> BandScore:
    missing = set(CANONICAL_FACT_BANDS) - set(estimates)
    if missing:
        raise ValueError(f"missing canonical facts: {sorted(missing)}")
    distances = {
        name: normalized_band_distance(float(estimates[name]), *band)
        for name, band in CANONICAL_FACT_BANDS.items()
    }
    passes = {name: distance == 0.0 for name, distance in distances.items()}
    return BandScore(
        pass_count=sum(passes.values()),
        fact_count=len(CANONICAL_FACT_BANDS),
        mean_normalized_distance=float(np.mean(list(distances.values()))),
        per_fact_normalized_distance=distances,
        per_fact_pass=passes,
    )
