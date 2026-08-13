"""Exact identities and obstructions for multi-stationary drift recovery."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import cast

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]

RESULT_SCHEMA = "exp152-exact-drift-audit-result/v1"
CONFIG_SCHEMA = "exp152-multi-stationary-drift-tomography/v1"


def _mapping(payload: Mapping[str, object], key: str) -> dict[str, object]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a mapping")
    return cast(dict[str, object], value)


def _number(payload: Mapping[str, object], key: str) -> float:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key} must be numeric")
    number = float(value)
    if not np.isfinite(number):
        raise ValueError(f"{key} must be finite")
    return number


def _integer(payload: Mapping[str, object], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _array(payload: Mapping[str, object], key: str, *, ndim: int) -> FloatArray:
    value = payload.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{key} must be an array")
    array = np.asarray(value, dtype=np.float64)
    if array.ndim != ndim or not np.isfinite(array).all():
        raise ValueError(f"{key} must be a finite {ndim}-dimensional array")
    return array


def _maximum_absolute(value: FloatArray) -> float:
    return float(np.max(np.abs(value))) if value.size else 0.0


def _one_dimensional_sign(config: Mapping[str, object], tolerance: float) -> dict[str, object]:
    kappa = _number(config, "kappa")
    decay = _number(config, "decay")
    intervention = _number(config, "intervention")
    points = _array(config, "points", ndim=1)
    expected_score_difference = _number(config, "expected_score_difference")
    expected_drift = _array(config, "expected_drift", ndim=1)
    if kappa <= 0.0 or decay <= 0.0 or points.shape != expected_drift.shape:
        raise ValueError("one_dimensional_sign has inconsistent positive parameters")

    variance = kappa / decay
    mean = intervention / decay
    baseline_score = -points / variance
    intervened_score = -(points - mean) / variance
    score_difference = intervened_score - baseline_score
    score_divergence = -1.0 / variance
    baseline_g = kappa * (score_divergence + baseline_score**2)
    intervened_g = (
        kappa * (score_divergence + intervened_score**2) - intervention * intervened_score
    )
    right_hand_side = intervened_g - baseline_g
    recovered = right_hand_side / score_difference
    true_drift = -decay * points
    identity_error = _maximum_absolute(true_drift * score_difference - right_hand_side)
    reconstruction_error = _maximum_absolute(recovered - true_drift)
    matches = bool(
        np.allclose(score_difference, expected_score_difference, rtol=0.0, atol=tolerance)
        and np.allclose(true_drift, expected_drift, rtol=0.0, atol=tolerance)
        and identity_error <= tolerance
        and reconstruction_error <= tolerance
    )
    return {
        "score_difference": score_difference.tolist(),
        "right_hand_side": right_hand_side.tolist(),
        "recovered_drift": recovered.tolist(),
        "true_drift": true_drift.tolist(),
        "maximum_identity_error": identity_error,
        "maximum_reconstruction_error": reconstruction_error,
        "matches_expected": matches,
    }


def _nonreversible_ou(config: Mapping[str, object], tolerance: float) -> dict[str, object]:
    kappa = _number(config, "kappa")
    decay_matrix = _array(config, "drift_decay", ndim=2)
    means = _array(config, "invariant_means", ndim=2)
    points = _array(config, "points", ndim=2)
    expected_rank = _integer(config, "expected_rank")
    expected_minimum = _number(config, "expected_minimum_singular_value")
    if decay_matrix.shape != (2, 2) or means.shape != (3, 2) or points.shape[1:] != (2,):
        raise ValueError("nonreversible_ou fixture requires the frozen two-dimensional shapes")

    interventions = means @ decay_matrix.T
    score_difference_matrix = means[1:] - means[0]
    singular_values = np.linalg.svd(score_difference_matrix, compute_uv=False)
    rank = int(np.linalg.matrix_rank(score_difference_matrix))
    recovered_rows: list[FloatArray] = []
    right_hand_rows: list[FloatArray] = []
    for point in points:
        scores = means - point
        g_values = kappa * (-2.0 + np.sum(scores**2, axis=1)) - np.sum(interventions * scores, axis=1)
        right_hand_side = g_values[1:] - g_values[0]
        right_hand_rows.append(right_hand_side)
        recovered_rows.append(np.linalg.solve(score_difference_matrix, right_hand_side))
    recovered = np.vstack(recovered_rows)
    right_hand_sides = np.vstack(right_hand_rows)
    true_drift = -(points @ decay_matrix.T)
    identity_error = _maximum_absolute(
        true_drift @ score_difference_matrix.T - right_hand_sides
    )
    reconstruction_error = _maximum_absolute(recovered - true_drift)
    antisymmetric = 0.5 * (decay_matrix - decay_matrix.T)
    minimum_singular_value = float(np.min(singular_values))
    matches = bool(
        rank == expected_rank
        and np.isclose(minimum_singular_value, expected_minimum, rtol=0.0, atol=tolerance)
        and identity_error <= tolerance
        and reconstruction_error <= tolerance
        and float(np.linalg.norm(antisymmetric)) > tolerance
    )
    return {
        "score_difference_matrix": score_difference_matrix.tolist(),
        "rank": rank,
        "singular_values": singular_values.tolist(),
        "minimum_singular_value": minimum_singular_value,
        "drift_decay_antisymmetric_frobenius_norm": float(np.linalg.norm(antisymmetric)),
        "known_interventions": interventions.tolist(),
        "recovered_drift": recovered.tolist(),
        "true_drift": true_drift.tolist(),
        "maximum_identity_error": identity_error,
        "maximum_reconstruction_error": reconstruction_error,
        "matches_expected": matches,
    }


def _torus_rank_alias(config: Mapping[str, object], tolerance: float) -> dict[str, object]:
    kappa = _number(config, "kappa")
    concentrations = _array(config, "concentrations", ndim=1)
    x1_points = _array(config, "x1_points", ndim=1)
    baseline_drift = _array(config, "baseline_drift", ndim=1)
    alternative_drift = _array(config, "alternative_drift", ndim=1)
    evaluation_x1 = _number(config, "rank_evaluation_x1")
    expected_rank = _integer(config, "expected_rank")
    expected_separation = _number(config, "expected_drift_separation")
    if concentrations.size < 2 or baseline_drift.shape != (2,) or alternative_drift.shape != (2,):
        raise ValueError("torus_rank_alias has inconsistent dimensions")

    residuals: list[float] = []
    for concentration in concentrations:
        for x1 in x1_points:
            score = np.array([-concentration * np.sin(x1), 0.0], dtype=np.float64)
            score_divergence = -concentration * np.cos(x1)
            intervention = score.copy()
            intervention_divergence = score_divergence
            for drift in (baseline_drift, alternative_drift):
                total_drift = drift + intervention
                residual = (
                    -intervention_divergence
                    - float(total_drift @ score)
                    + kappa * (score_divergence + float(score @ score))
                )
                residuals.append(residual)

    evaluation_scores = np.column_stack(
        (-concentrations * np.sin(evaluation_x1), np.zeros_like(concentrations))
    )
    score_difference_matrix = evaluation_scores[1:] - evaluation_scores[0]
    rank = int(np.linalg.matrix_rank(score_difference_matrix))
    drift_separation = float(np.linalg.norm(alternative_drift - baseline_drift))
    maximum_residual = float(np.max(np.abs(np.asarray(residuals, dtype=np.float64))))
    matches = bool(
        rank == expected_rank
        and np.isclose(drift_separation, expected_separation, rtol=0.0, atol=tolerance)
        and maximum_residual <= tolerance
    )
    return {
        "score_difference_matrix": score_difference_matrix.tolist(),
        "rank": rank,
        "baseline_drift": baseline_drift.tolist(),
        "alternative_drift": alternative_drift.tolist(),
        "drift_separation": drift_separation,
        "maximum_stationary_pde_residual": maximum_residual,
        "observational_alias_confirmed": matches,
        "matches_expected": matches,
    }


def _invisible_rotation(config: Mapping[str, object], tolerance: float) -> dict[str, object]:
    rotation_rate = _number(config, "rotation_rate")
    point = _array(config, "evaluation_point", ndim=1)
    expected_rank = _integer(config, "expected_score_difference_rank")
    expected_norm_squared = _number(config, "expected_intervention_norm_squared")
    if point.shape != (2,):
        raise ValueError("invisible_rotation evaluation_point must have dimension two")

    rotation = np.array([[0.0, -1.0], [1.0, 0.0]], dtype=np.float64)
    intervention = rotation_rate * (rotation @ point)
    score = -point
    weighted_divergence = rotation_rate * float(np.trace(rotation)) + float(intervention @ score)
    score_difference_matrix = np.zeros((1, 2), dtype=np.float64)
    rank = int(np.linalg.matrix_rank(score_difference_matrix))
    intervention_norm_squared = float(intervention @ intervention)
    matches = bool(
        rank == expected_rank
        and abs(weighted_divergence) <= tolerance
        and np.isclose(
            intervention_norm_squared,
            expected_norm_squared,
            rtol=0.0,
            atol=tolerance,
        )
    )
    return {
        "evaluation_point": point.tolist(),
        "intervention": intervention.tolist(),
        "intervention_norm_squared": intervention_norm_squared,
        "weighted_divergence_residual": weighted_divergence,
        "score_difference_rank": rank,
        "matches_expected": matches,
    }


def _diffusion_misspecification(config: Mapping[str, object], tolerance: float) -> dict[str, object]:
    decay = _number(config, "decay")
    intervention = _number(config, "intervention")
    baseline_kappa = _number(config, "baseline_kappa")
    intervention_kappa = _number(config, "intervention_kappa")
    assumed_kappa = _number(config, "incorrectly_assumed_kappa")
    points = _array(config, "points", ndim=1)
    expected_true = _array(config, "expected_true_drift", ndim=1)
    expected_wrong = _array(config, "expected_wrong_reconstruction", ndim=1)
    expected_wrong_error = _number(config, "expected_wrong_maximum_error")
    if min(decay, baseline_kappa, intervention_kappa, assumed_kappa) <= 0.0:
        raise ValueError("diffusion_misspecification requires positive decay and diffusion")
    if points.shape != expected_true.shape or points.shape != expected_wrong.shape:
        raise ValueError("diffusion_misspecification arrays must have equal shape")

    baseline_variance = baseline_kappa / decay
    intervention_variance = intervention_kappa / decay
    intervention_mean = intervention / decay
    baseline_score = -points / baseline_variance
    intervened_score = -(points - intervention_mean) / intervention_variance
    baseline_divergence = -1.0 / baseline_variance
    intervened_divergence = -1.0 / intervention_variance
    score_difference = intervened_score - baseline_score
    baseline_g = baseline_kappa * (baseline_divergence + baseline_score**2)
    intervened_g = intervention_kappa * (
        intervened_divergence + intervened_score**2
    ) - intervention * intervened_score
    correct_reconstruction = (intervened_g - baseline_g) / score_difference
    wrong_baseline_g = assumed_kappa * (baseline_divergence + baseline_score**2)
    wrong_intervened_g = assumed_kappa * (
        intervened_divergence + intervened_score**2
    ) - intervention * intervened_score
    wrong_reconstruction = (wrong_intervened_g - wrong_baseline_g) / score_difference
    true_drift = -decay * points
    correct_error = _maximum_absolute(correct_reconstruction - true_drift)
    wrong_error = _maximum_absolute(wrong_reconstruction - true_drift)
    matches = bool(
        np.allclose(true_drift, expected_true, rtol=0.0, atol=tolerance)
        and np.allclose(wrong_reconstruction, expected_wrong, rtol=0.0, atol=tolerance)
        and correct_error <= tolerance
        and np.isclose(wrong_error, expected_wrong_error, rtol=0.0, atol=tolerance)
    )
    return {
        "score_difference": score_difference.tolist(),
        "correct_reconstruction": correct_reconstruction.tolist(),
        "wrong_common_diffusion_reconstruction": wrong_reconstruction.tolist(),
        "true_drift": true_drift.tolist(),
        "maximum_correct_reconstruction_error": correct_error,
        "maximum_wrong_reconstruction_error": wrong_error,
        "matches_expected": matches,
    }


def _coordinate_transform(config: Mapping[str, object], tolerance: float) -> dict[str, object]:
    affine_scale = _array(config, "affine_scale", ndim=2)
    expected_original_rank = _integer(config, "expected_original_rank")
    expected_transformed_rank = _integer(config, "expected_transformed_rank")
    expected_original_minimum = _number(config, "expected_original_minimum_singular_value")
    expected_transformed_minimum = _number(config, "expected_transformed_minimum_singular_value")
    expected_condition = _number(config, "expected_transformed_condition_number")
    point = _array(config, "nonlinear_evaluation_point", ndim=1)
    expected_jacobian = _array(config, "expected_nonlinear_jacobian", ndim=2)
    expected_correction = _array(config, "expected_ito_correction", ndim=1)
    expected_correction_norm = _number(config, "expected_ito_correction_norm")
    if affine_scale.shape != (2, 2) or point.shape != (2,):
        raise ValueError("coordinate_transform requires two-dimensional fixtures")

    original_scores = np.eye(2, dtype=np.float64)
    transformed_scores = original_scores @ np.linalg.inv(affine_scale)
    original_singular_values = np.linalg.svd(original_scores, compute_uv=False)
    transformed_singular_values = np.linalg.svd(transformed_scores, compute_uv=False)
    original_rank = int(np.linalg.matrix_rank(original_scores))
    transformed_rank = int(np.linalg.matrix_rank(transformed_scores))
    original_minimum = float(np.min(original_singular_values))
    transformed_minimum = float(np.min(transformed_singular_values))
    transformed_condition = float(np.linalg.cond(transformed_scores))

    x1 = float(point[0])
    jacobian = np.array([[1.0 + 3.0 * x1**2, 0.0], [0.0, 1.0]], dtype=np.float64)
    ito_correction = np.array([6.0 * x1, 0.0], dtype=np.float64)
    nonlinear_transformed_scores = original_scores @ np.linalg.inv(jacobian)
    nonlinear_rank = int(np.linalg.matrix_rank(nonlinear_transformed_scores))
    correction_norm = float(np.linalg.norm(ito_correction))
    matches = bool(
        original_rank == expected_original_rank
        and transformed_rank == expected_transformed_rank
        and nonlinear_rank == expected_transformed_rank
        and np.isclose(original_minimum, expected_original_minimum, rtol=0.0, atol=tolerance)
        and np.isclose(transformed_minimum, expected_transformed_minimum, rtol=0.0, atol=tolerance)
        and np.isclose(transformed_condition, expected_condition, rtol=0.0, atol=tolerance)
        and np.allclose(jacobian, expected_jacobian, rtol=0.0, atol=tolerance)
        and np.allclose(ito_correction, expected_correction, rtol=0.0, atol=tolerance)
        and np.isclose(correction_norm, expected_correction_norm, rtol=0.0, atol=tolerance)
    )
    return {
        "original_score_difference_matrix": original_scores.tolist(),
        "affine_transformed_score_difference_matrix": transformed_scores.tolist(),
        "original_rank": original_rank,
        "affine_transformed_rank": transformed_rank,
        "original_minimum_singular_value": original_minimum,
        "affine_transformed_minimum_singular_value": transformed_minimum,
        "affine_transformed_condition_number": transformed_condition,
        "nonlinear_jacobian": jacobian.tolist(),
        "nonlinear_transformed_score_difference_matrix": nonlinear_transformed_scores.tolist(),
        "nonlinear_transformed_rank": nonlinear_rank,
        "ito_correction": ito_correction.tolist(),
        "ito_correction_norm": correction_norm,
        "raw_conditioning_is_coordinate_invariant": False,
        "matches_expected": matches,
    }


def run_exact_drift_audit(config: Mapping[str, object]) -> dict[str, object]:
    """Evaluate all preregistered deterministic Experiment 152 fixtures."""

    if config.get("schema") != CONFIG_SCHEMA:
        raise ValueError(f"config schema must be {CONFIG_SCHEMA}")
    tolerance = _number(config, "absolute_tolerance")
    if tolerance <= 0.0:
        raise ValueError("absolute_tolerance must be positive")

    witnesses = {
        "one_dimensional_sign": _one_dimensional_sign(
            _mapping(config, "one_dimensional_sign"), tolerance
        ),
        "nonreversible_ou": _nonreversible_ou(_mapping(config, "nonreversible_ou"), tolerance),
        "torus_rank_alias": _torus_rank_alias(_mapping(config, "torus_rank_alias"), tolerance),
        "invisible_rotation": _invisible_rotation(
            _mapping(config, "invisible_rotation"), tolerance
        ),
        "diffusion_misspecification": _diffusion_misspecification(
            _mapping(config, "diffusion_misspecification"), tolerance
        ),
        "coordinate_transform": _coordinate_transform(
            _mapping(config, "coordinate_transform"), tolerance
        ),
    }
    all_match = all(witness.get("matches_expected") is True for witness in witnesses.values())
    decision = (
        "IDENTITY_AND_OBSTRUCTIONS_CONFIRMED" if all_match else "IMPLEMENTATION_OR_SPEC_FAILURE"
    )
    return {
        "schema": RESULT_SCHEMA,
        "experiment": 152,
        "decision": decision,
        "candidate_admission": False,
        "novelty_pass": False,
        "compute_unlock": False,
        "witnesses": witnesses,
    }

