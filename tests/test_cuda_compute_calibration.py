from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _module():
    path = Path(__file__).resolve().parents[1] / "experiments/139_cuda_compute_calibration/run_scaling.py"
    spec = importlib.util.spec_from_file_location("run_cuda_compute_calibration", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cells_for_pool_is_deterministic() -> None:
    module = _module()
    config = {
        "seed_root": 100,
        "pools": {"v100": {"n_agents": [500, 2000], "repeats": 2}},
    }
    assert module.cells_for_pool(config, "v100") == [
        (500, 0, 100),
        (500, 1, 101),
        (2000, 0, 10_100),
        (2000, 1, 10_101),
    ]


def test_cells_for_pool_rejects_unknown_pool() -> None:
    module = _module()
    with pytest.raises(ValueError):
        module.cells_for_pool({"seed_root": 1, "pools": {}}, "v100")
