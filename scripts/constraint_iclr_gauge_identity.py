"""Numerical integrity gates for the direct gauge-feedback intervention."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

FLOAT32_EPSILON = 2.0**-23


def gauge_identity_gate(
    metrics: Mapping[str, Any], gauge_config: Mapping[str, Any]
) -> tuple[float, float, bool]:
    """Return roundoff tolerance, contamination fraction, and joint pass flag."""

    absolute_floor = float(gauge_config["identity_atol"])
    roundoff_ulps = int(gauge_config["identity_roundoff_ulps"])
    relative_limit = float(gauge_config["identity_relative_baseline_atol"])
    scale = float(metrics["step_one_identity_scale_max_abs"])
    baseline = float(metrics["projected_history_conserving_rmse"])
    residual = max(
        float(metrics["step_one_q_identity_max_abs"]),
        float(metrics["step_one_gauge_nonconstant_max_abs"]),
    )
    values = (absolute_floor, relative_limit, scale, baseline, residual)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("gauge identity gate received a non-finite value")
    if absolute_floor < 0.0 or roundoff_ulps < 0 or relative_limit < 0.0:
        raise ValueError("gauge identity tolerances must be nonnegative")
    if scale < 0.0 or residual < 0.0 or baseline <= 0.0:
        raise ValueError("gauge identity metrics have an invalid sign")
    roundoff_tolerance = absolute_floor + float(roundoff_ulps) * FLOAT32_EPSILON * max(1.0, scale)
    contamination_fraction = residual / baseline
    passed = residual <= roundoff_tolerance and contamination_fraction <= relative_limit
    return roundoff_tolerance, contamination_fraction, passed
