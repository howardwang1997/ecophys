"""Tests for experiment-127 learned held-out analysis helpers."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import numpy as np


def _module() -> ModuleType:
    path = (
        Path(__file__).resolve().parents[1]
        / "experiments"
        / "127_workshop_claim_gates"
        / "analyze_learned_results.py"
    )
    spec = importlib.util.spec_from_file_location("exp127_analyze_learned", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_primary_summary_hierarchical_bootstrap() -> None:
    module = _module()
    checkpoints = []
    for index in range(7):
        checkpoints.append({
            "job_id": f"e1_case_{index}",
            "paired_hill_differences": [0.4 + 0.01 * index] * 16,
            "checkpoint_median_hill_difference": 0.4 + 0.01 * index,
            "heldout_gate_evaluation": {"frozen_w_star_passes": True},
        })
    for index, value in enumerate((0.3, 0.2, -0.1)):
        checkpoints.append({
            "job_id": f"e3_case_{index}",
            "paired_hill_differences": [value] * 16,
            "checkpoint_median_hill_difference": value,
            "heldout_gate_evaluation": {"frozen_w_star_passes": True},
        })
    summary = module._primary_summary(checkpoints, bootstrap_seed=7, replicates=200)
    assert summary["e1_scorable"] == 7
    assert summary["e1_heldout_gate_confirmed"] == 7
    assert summary["expected_positive_direction_passes"]
    assert summary["e3_same_positive_sign_2_of_3"]


def test_load_trajectory_with_volume(tmp_path: Path) -> None:
    module = _module()
    path = tmp_path / "trajectory_seed9.npz"
    np.savez(
        path,
        seed=9,
        n_recorded_returns=8000,
        log_returns=np.ones(8000),
        volumes=np.full(8000, 2.0),
    )
    returns, volumes = module.load_trajectory(path, expected_seed=9)
    assert returns.shape == volumes.shape == (8000,)
