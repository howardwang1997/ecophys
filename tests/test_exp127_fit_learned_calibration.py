"""Tests for experiment-127 learned calibration loading."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest


def _module() -> ModuleType:
    path = (
        Path(__file__).resolve().parents[1]
        / "experiments"
        / "127_workshop_claim_gates"
        / "fit_learned_calibration.py"
    )
    spec = importlib.util.spec_from_file_location("exp127_fit_learned_calibration", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_load_trajectory_validates_schema(tmp_path: Path) -> None:
    module = _module()
    path = tmp_path / "trajectory_seed12.npz"
    np.savez(path, seed=12, n_recorded_returns=8000, log_returns=np.ones(8000))
    loaded = module.load_trajectory(path, expected_seed=12)
    assert loaded.shape == (8000,)
    with pytest.raises(RuntimeError, match="seed mismatch"):
        module.load_trajectory(path, expected_seed=13)


def test_load_trajectory_rejects_short_return_array(tmp_path: Path) -> None:
    module = _module()
    path = tmp_path / "trajectory_seed12.npz"
    np.savez(path, seed=12, n_recorded_returns=7999, log_returns=np.ones(7999))
    with pytest.raises(RuntimeError, match="schema mismatch"):
        module.load_trajectory(path, expected_seed=12)
