from pathlib import Path
from typing import cast

import numpy as np
import pytest
import yaml

from ecomd.research.stationary_drift_tomography import run_exact_drift_audit

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "experiments/152_multi_stationary_drift_tomography/config.yaml"


def _config() -> dict[str, object]:
    raw: object = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    return cast(dict[str, object], raw)


def _witnesses(result: dict[str, object]) -> dict[str, dict[str, object]]:
    witnesses = result["witnesses"]
    assert isinstance(witnesses, dict)
    return cast(dict[str, dict[str, object]], witnesses)


def test_exact_drift_audit_confirms_all_frozen_fixtures() -> None:
    result = run_exact_drift_audit(_config())
    witnesses = _witnesses(result)

    assert result["decision"] == "IDENTITY_AND_OBSTRUCTIONS_CONFIRMED"
    assert result["candidate_admission"] is False
    assert result["novelty_pass"] is False
    assert result["compute_unlock"] is False
    assert all(witness["matches_expected"] is True for witness in witnesses.values())


def test_rank_deficient_environments_admit_distinct_common_drifts() -> None:
    witnesses = _witnesses(run_exact_drift_audit(_config()))
    alias = witnesses["torus_rank_alias"]

    assert alias["rank"] == 1
    assert alias["observational_alias_confirmed"] is True
    assert alias["drift_separation"] == pytest.approx(1.0, abs=1.0e-12)
    assert alias["maximum_stationary_pde_residual"] == pytest.approx(0.0, abs=1.0e-12)


def test_invisible_intervention_and_diffusion_misspecification_are_detected() -> None:
    witnesses = _witnesses(run_exact_drift_audit(_config()))
    invisible = witnesses["invisible_rotation"]
    diffusion = witnesses["diffusion_misspecification"]

    assert invisible["score_difference_rank"] == 0
    assert invisible["intervention_norm_squared"] == pytest.approx(45.0, abs=1.0e-12)
    assert diffusion["maximum_correct_reconstruction_error"] == pytest.approx(0.0, abs=1.0e-12)
    assert diffusion["maximum_wrong_reconstruction_error"] == pytest.approx(0.5, abs=1.0e-12)


def test_coordinate_rank_survives_but_raw_conditioning_changes() -> None:
    witnesses = _witnesses(run_exact_drift_audit(_config()))
    coordinate = witnesses["coordinate_transform"]

    assert coordinate["original_rank"] == coordinate["affine_transformed_rank"] == 2
    assert coordinate["nonlinear_transformed_rank"] == 2
    assert coordinate["original_minimum_singular_value"] == pytest.approx(1.0, abs=1.0e-12)
    assert coordinate["affine_transformed_minimum_singular_value"] == pytest.approx(0.1, abs=1.0e-12)
    assert coordinate["ito_correction_norm"] == pytest.approx(6.0, abs=1.0e-12)
    assert coordinate["raw_conditioning_is_coordinate_invariant"] is False


def test_exact_drift_audit_rejects_nonpositive_tolerance() -> None:
    config = _config()
    config["absolute_tolerance"] = 0.0

    with pytest.raises(ValueError, match="absolute_tolerance must be positive"):
        run_exact_drift_audit(config)


def test_nonreversible_reconstruction_contains_rotational_drift() -> None:
    witnesses = _witnesses(run_exact_drift_audit(_config()))
    ou = witnesses["nonreversible_ou"]

    recovered = np.asarray(ou["recovered_drift"], dtype=np.float64)
    truth = np.asarray(ou["true_drift"], dtype=np.float64)
    assert np.allclose(recovered, truth, rtol=0.0, atol=1.0e-12)
    assert float(ou["drift_decay_antisymmetric_frobenius_norm"]) > 0.0

