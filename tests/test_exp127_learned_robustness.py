"""Tests for experiment-127 dependence-aware learned robustness checks."""

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
        / "analyze_learned_robustness.py"
    )
    spec = importlib.util.spec_from_file_location("exp127_learned_robustness", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _payload(module: ModuleType, *, mismatched_seed: bool = False) -> dict[str, object]:
    checkpoints = []
    common_component = np.linspace(-0.03, 0.03, 16)
    effects = []
    for index, job_id in enumerate(module.MARKET_BY_JOB):
        values = 0.2 + 0.02 * index + common_component
        seeds = list(range(16))
        if mismatched_seed and index == 1:
            seeds[-1] = 99
        checkpoints.append(
            {
                "job_id": job_id,
                "paired_hill_differences": values.tolist(),
                "heldout_provenance": [{"seed": seed} for seed in seeds],
            }
        )
        effects.append(float(np.median(values)))
    return {
        "primary": {"e1_scorable": 7, "effect": float(np.mean(effects))},
        "checkpoints": checkpoints,
    }


def test_crossed_bootstrap_and_market_leave_one_out() -> None:
    module = _module()
    result = module.analyze(_payload(module), "a" * 64)
    crossed = result["crossed_checkpoint_seed_bootstrap"]
    market = result["market_balanced_sensitivity"]
    assert crossed["positive_direction_passes"]
    assert crossed["ci_95"][0] > 0.0
    assert set(market["market_effects"]) == set(module.MARKET_ORDER)
    assert market["all_leave_one_out_positive"]


def test_common_seed_order_is_enforced() -> None:
    module = _module()
    with pytest.raises(ValueError, match="identical held-out seed order"):
        module.analyze(_payload(module, mismatched_seed=True), "b" * 64)
