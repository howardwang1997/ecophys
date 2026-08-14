from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np

from ecomd.research.open_data_calibration import (
    canonical_result_sha256,
    ensemble_energy_score,
    paired_randomization_p_value,
    run_synthetic_calibration,
    settings_from_contract,
)
from ecomd.research.open_data_development import load_development_contract

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/manifests/open_data_development_sample_v1.yaml"


def test_energy_score_is_zero_for_a_deterministic_exact_ensemble() -> None:
    outcome = np.asarray([[1.0, -1.0], [0.5, 2.0]], dtype=np.float64)
    ensemble = np.repeat(outcome[:, None, :], 3, axis=1)

    assert np.array_equal(ensemble_energy_score(outcome, ensemble), np.zeros(2))


def test_paired_randomization_is_deterministic_and_one_sided() -> None:
    differences = np.ones(20, dtype=np.float64)
    first = paired_randomization_p_value(
        differences,
        draws=255,
        rng=np.random.default_rng(7),
    )
    second = paired_randomization_p_value(
        differences,
        draws=255,
        rng=np.random.default_rng(7),
    )

    assert first == second
    assert first <= 0.01


def test_small_calibration_is_reproducible_and_detects_structural_failures() -> None:
    settings = settings_from_contract(load_development_contract(CONTRACT))
    smoke = replace(settings, replicates=12, permutation_draws=31)

    first = run_synthetic_calibration(smoke)
    second = run_synthetic_calibration(smoke)

    assert canonical_result_sha256(first) == canonical_result_sha256(second)
    structural = first["structural_contract"]
    assert isinstance(structural, dict)
    assert set(structural.values()) == {1.0}
