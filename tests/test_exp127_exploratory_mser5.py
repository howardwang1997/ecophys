from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import numpy as np
import numpy.typing as npt


def _load_module() -> ModuleType:
    root = Path(__file__).resolve().parents[1]
    path = root / "experiments/127_workshop_claim_gates/run_exploratory_mser5.py"
    spec = importlib.util.spec_from_file_location("exp127_exploratory_mser5", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mser5_selects_zero_for_constant_series() -> None:
    module = _load_module()
    calibration: npt.NDArray[np.float64] = np.ones((4, 100), dtype=np.float64)
    assert module.mser5_w(calibration, batch_size=5, max_w=50) == 0


def test_mser5_removes_known_mean_absolute_transient() -> None:
    module = _load_module()
    calibration: npt.NDArray[np.float64] = np.ones((4, 100), dtype=np.float64)
    calibration[:, :20] = 10.0
    assert module.mser5_w(calibration, batch_size=5, max_w=50) == 20
