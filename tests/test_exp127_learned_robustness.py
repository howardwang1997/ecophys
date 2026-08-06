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


def test_hill_fraction_grid_summary() -> None:
    module = _module()
    job_ids = list(module.MARKET_BY_JOB)
    matrices = {
        module._fraction_key(fraction): np.full((7, 16), 0.1 + fraction)
        for fraction in module.HILL_K_FRACTIONS
    }
    result = module.summarize_hill_fraction_sensitivity(job_ids, matrices)
    assert result["positive_point_effect_count"] == 3
    assert result["positive_common_seed_interval_count"] == 3
    assert result["all_point_effects_positive"]


def test_hill_fraction_recomputation_matches_primary(tmp_path: Path) -> None:
    module = _module()
    rng = np.random.default_rng(19)
    checkpoints = []
    checkpoint_effects = []
    for job_id in module.MARKET_BY_JOB:
        provenance = []
        differences = []
        directory = tmp_path / "rollouts/heldout" / job_id / "v100_a"
        directory.mkdir(parents=True)
        for seed in range(16):
            returns = np.concatenate(
                (rng.standard_t(4.0, 4000), rng.standard_t(10.0, 4000))
            )
            path = directory / f"trajectory_seed{seed}.npz"
            np.savez(path, seed=seed, log_returns=returns)
            early = module.hill_tail_index(returns[:4000], k_frac=0.05).estimate
            post = module.hill_tail_index(returns[3000:7000], k_frac=0.05).estimate
            differences.append(post - early)
            provenance.append({"seed": seed, "node": "v100_a"})
        checkpoints.append(
            {
                "job_id": job_id,
                "calibration_w_star": 3000,
                "paired_hill_differences": differences,
                "heldout_provenance": provenance,
            }
        )
        checkpoint_effects.append(float(np.median(differences)))
    payload = {
        "primary": {
            "e1_scorable": 7,
            "effect": float(np.mean(checkpoint_effects)),
        },
        "checkpoints": checkpoints,
    }
    job_ids, matrices = module.compute_hill_fraction_matrices(payload, tmp_path)
    sensitivity = module.summarize_hill_fraction_sensitivity(job_ids, matrices)
    result = module.analyze(payload, "c" * 64, sensitivity)
    assert result["hill_fraction_sensitivity"]["fractions"] == [0.025, 0.05, 0.1]
