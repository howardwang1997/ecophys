"""Unit tests for experiment-127 analytic-control helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest


def _module() -> ModuleType:
    path = (
        Path(__file__).resolve().parents[1]
        / "experiments"
        / "127_workshop_claim_gates"
        / "run_analytic_controls.py"
    )
    spec = importlib.util.spec_from_file_location("exp127_analytic_controls", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_wilson_interval_boundaries() -> None:
    module = _module()
    low_zero, high_zero = module._wilson_interval(0, 62)
    low_all, high_all = module._wilson_interval(62, 62)
    assert low_zero == 0.0
    assert 0.0 < high_zero < 0.1
    assert 0.9 < low_all < 1.0
    assert high_all == pytest.approx(1.0)


def test_frozen_parameter_sources_match() -> None:
    module = _module()
    frozen = module.load_frozen_parameters()
    assert frozen["trajectories_per_condition"] == 1000


def test_hill_uses_fixed_length() -> None:
    module = _module()
    rng = np.random.default_rng(5)
    returns = rng.standard_t(df=5, size=8000)
    assert np.isfinite(module._hill(returns, 3000))
    with pytest.raises(ValueError):
        module._hill(returns, 5000)
