from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _load_figures() -> ModuleType:
    root = Path(__file__).resolve().parents[1]
    path = root / "papers/paper_a_methods/workshops/sim2science/make_figures.py"
    spec = importlib.util.spec_from_file_location("sim2science_figures", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _checkpoint(job_id: str, w_star: int | None, transfer: bool | None) -> dict[str, Any]:
    differences = [0.4, 0.6, 0.7, 0.5] if w_star is not None else []
    sensitivity = {
        "0": {"heldout_median_estimates": {"hill_tail_index": 3.0}},
        "500": {"heldout_median_estimates": {"hill_tail_index": 3.55}},
    }
    return {
        "job_id": job_id,
        "calibration_w_star": w_star,
        "heldout_gate_evaluation": {"frozen_w_star_passes": transfer},
        "paired_hill_differences": differences,
        "sensitivity": sensitivity,
    }


def test_learned_result_panels_accept_missing_and_failed_gates() -> None:
    figures = _load_figures()
    checkpoints = [
        _checkpoint("e1_spx_concave", 500, True),
        _checkpoint("e1_btc_base", 500, False),
        _checkpoint("e3_sv_0", None, None),
    ]
    primary = {"effect": 0.55, "ci_95": [0.2, 0.9]}
    fig, axes = plt.subplots(1, 2)
    figures._learned_forest_panel(axes[0], checkpoints, primary)
    figures._learned_slope_panel(axes[1], checkpoints)
    assert axes[0].get_ylabel() == ""
    assert axes[1].get_ylabel() == "held-out median Hill index"
    plt.close(fig)


def test_bootstrap_median_interval_is_deterministic() -> None:
    figures = _load_figures()
    values = np.array([0.1, 0.2, 0.3, 0.4], dtype=float)
    assert figures._bootstrap_median_interval(values, 128000) == figures._bootstrap_median_interval(
        values, 128000
    )


def test_wilson_interval_contains_observed_rate() -> None:
    figures = _load_figures()
    low, high = figures._wilson_interval(16, 62)
    assert low < 16 / 62 < high
    assert np.isclose(low, 0.1655, atol=1e-4)
    assert np.isclose(high, 0.3788, atol=1e-4)
