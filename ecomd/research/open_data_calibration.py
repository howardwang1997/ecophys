"""Generated null, power and clock calibration for the open-data preflight."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime, timedelta
from typing import cast

import numpy as np
from numpy.typing import NDArray
from scipy.stats import binomtest

from .open_data_development import CommonObservation, observation_violations

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class CalibrationSettings:
    """Frozen settings for paired proper-score calibration."""

    protocol: str
    root_seed: int
    replicates: int
    independent_blocks: int
    response_dimension: int
    ensemble_size: int
    permutation_draws: int
    alpha: float
    null_symmetric_bias: float
    effect_scale: float
    forecast_standard_deviation: float
    outcome_standard_deviation: float
    clock_shift_blocks: int
    structural_cases_per_replicate: int
    null_false_positive_rate_maximum: float
    null_binomial_calibration_p_minimum: float
    effect_power_minimum: float
    correct_clock_selection_rate_minimum: float
    leakage_detection_rate_required: float
    identity_violation_detection_rate_required: float
    status_contract_detection_rate_required: float


def _number(value: object, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _integer(value: object, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    return value


def settings_from_contract(contract: dict[str, object]) -> CalibrationSettings:
    """Extract the frozen generated-data settings from a validated contract."""

    raw = contract.get("synthetic_calibration")
    if not isinstance(raw, dict):
        raise ValueError("synthetic_calibration must be a mapping")
    calibration = cast(dict[str, object], raw)
    gates_raw = calibration.get("gates")
    if not isinstance(gates_raw, dict):
        raise ValueError("synthetic_calibration.gates must be a mapping")
    gates = cast(dict[str, object], gates_raw)
    protocol = calibration.get("protocol")
    if not isinstance(protocol, str) or not protocol:
        raise ValueError("synthetic_calibration.protocol must be non-empty")
    settings = CalibrationSettings(
        protocol=protocol,
        root_seed=_integer(calibration.get("root_seed"), name="root_seed"),
        replicates=_integer(calibration.get("replicates"), name="replicates"),
        independent_blocks=_integer(
            calibration.get("independent_blocks"), name="independent_blocks"
        ),
        response_dimension=_integer(
            calibration.get("response_dimension"), name="response_dimension"
        ),
        ensemble_size=_integer(calibration.get("ensemble_size"), name="ensemble_size"),
        permutation_draws=_integer(
            calibration.get("permutation_draws"), name="permutation_draws"
        ),
        alpha=_number(calibration.get("alpha"), name="alpha"),
        null_symmetric_bias=_number(
            calibration.get("null_symmetric_bias"), name="null_symmetric_bias"
        ),
        effect_scale=_number(calibration.get("effect_scale"), name="effect_scale"),
        forecast_standard_deviation=_number(
            calibration.get("forecast_standard_deviation"),
            name="forecast_standard_deviation",
        ),
        outcome_standard_deviation=_number(
            calibration.get("outcome_standard_deviation"), name="outcome_standard_deviation"
        ),
        clock_shift_blocks=_integer(
            calibration.get("clock_shift_blocks"), name="clock_shift_blocks"
        ),
        structural_cases_per_replicate=_integer(
            calibration.get("structural_cases_per_replicate"),
            name="structural_cases_per_replicate",
        ),
        null_false_positive_rate_maximum=_number(
            gates.get("null_false_positive_rate_maximum"),
            name="null_false_positive_rate_maximum",
        ),
        null_binomial_calibration_p_minimum=_number(
            gates.get("null_binomial_calibration_p_minimum"),
            name="null_binomial_calibration_p_minimum",
        ),
        effect_power_minimum=_number(
            gates.get("effect_power_minimum"), name="effect_power_minimum"
        ),
        correct_clock_selection_rate_minimum=_number(
            gates.get("correct_clock_selection_rate_minimum"),
            name="correct_clock_selection_rate_minimum",
        ),
        leakage_detection_rate_required=_number(
            gates.get("leakage_detection_rate_required"),
            name="leakage_detection_rate_required",
        ),
        identity_violation_detection_rate_required=_number(
            gates.get("identity_violation_detection_rate_required"),
            name="identity_violation_detection_rate_required",
        ),
        status_contract_detection_rate_required=_number(
            gates.get("status_contract_detection_rate_required"),
            name="status_contract_detection_rate_required",
        ),
    )
    if settings.replicates <= 0 or settings.independent_blocks < 8:
        raise ValueError("replicates must be positive and at least eight blocks are required")
    if settings.response_dimension < 2 or settings.ensemble_size < 2:
        raise ValueError("at least two response dimensions and ensemble members are required")
    if settings.permutation_draws <= 0 or settings.clock_shift_blocks <= 0:
        raise ValueError("permutation draws and clock shift must be positive")
    if not 0.0 < settings.alpha < 1.0:
        raise ValueError("alpha must lie in (0, 1)")
    return settings


def _rng(root_seed: int, scenario: str, replicate: int) -> np.random.Generator:
    label = f"{root_seed}|{scenario}|{replicate}".encode()
    digest = hashlib.sha256(label).digest()
    entropy = [int.from_bytes(digest[offset : offset + 4], "big") for offset in range(0, 16, 4)]
    return np.random.default_rng(np.random.SeedSequence(entropy))


def ensemble_energy_score(outcome: FloatArray, ensemble: FloatArray) -> FloatArray:
    """Return the multivariate ensemble energy score for each independent block."""

    observed = np.asarray(outcome, dtype=np.float64)
    forecasts = np.asarray(ensemble, dtype=np.float64)
    if observed.ndim != 2 or forecasts.ndim != 3:
        raise ValueError("outcome must be [block, dimension] and ensemble [block, member, dimension]")
    if observed.shape[0] != forecasts.shape[0] or observed.shape[1] != forecasts.shape[2]:
        raise ValueError("outcome and ensemble shapes disagree")
    if forecasts.shape[1] < 2 or not np.all(np.isfinite(observed)) or not np.all(np.isfinite(forecasts)):
        raise ValueError("energy score requires finite values and at least two ensemble members")
    observation_term = np.linalg.norm(forecasts - observed[:, None, :], axis=-1).mean(axis=1)
    pairwise = forecasts[:, :, None, :] - forecasts[:, None, :, :]
    ensemble_term = 0.5 * np.linalg.norm(pairwise, axis=-1).mean(axis=(1, 2))
    return cast(FloatArray, observation_term - ensemble_term)


def paired_randomization_p_value(
    loss_difference: FloatArray,
    *,
    draws: int,
    rng: np.random.Generator,
) -> float:
    """One-sided paired sign-randomization p-value for positive baseline-minus-candidate loss."""

    differences = np.asarray(loss_difference, dtype=np.float64)
    if differences.ndim != 1 or differences.size < 2 or not np.all(np.isfinite(differences)):
        raise ValueError("loss_difference must be a finite vector with at least two blocks")
    if draws <= 0:
        raise ValueError("draws must be positive")
    observed = float(np.mean(differences))
    signs = rng.integers(0, 2, size=(draws, differences.size), dtype=np.int8) * 2 - 1
    permuted = np.mean(signs * differences[None, :], axis=1)
    return float((1 + np.count_nonzero(permuted >= observed)) / (draws + 1))


def _direction(dimension: int) -> FloatArray:
    signs = np.where(np.arange(dimension) % 2 == 0, 1.0, -1.0)
    weights = 1.0 / np.sqrt(np.arange(1, dimension + 1, dtype=np.float64))
    direction = signs * weights
    return cast(FloatArray, direction / np.linalg.norm(direction))


def _effect_path(settings: CalibrationSettings) -> FloatArray:
    block_index = np.arange(1, settings.independent_blocks + 1, dtype=np.float64)
    relaxation = 1.0 - np.exp(-4.0 * block_index / settings.independent_blocks)
    return settings.effect_scale * relaxation[:, None] * _direction(
        settings.response_dimension
    )[None, :]


def _forecast_ensemble(
    mean: FloatArray,
    residuals: FloatArray,
) -> FloatArray:
    if mean.ndim != 2 or residuals.ndim != 3:
        raise ValueError("forecast mean or residual shape is invalid")
    return mean[:, None, :] + residuals


def _structural_detection(replicate: int) -> tuple[bool, bool, bool, bool]:
    freeze = datetime(2025, 1, 1, tzinfo=UTC) + timedelta(days=replicate)
    valid = CommonObservation(
        system_id="generated",
        event_id=f"event-{replicate}",
        participant_id=f"participant-{replicate}",
        forecast_frozen_at=freeze,
        feature_as_of=freeze - timedelta(minutes=5),
        action_at=freeze + timedelta(minutes=5),
        outcome_at=freeze + timedelta(minutes=10),
        identity_valid_from=freeze - timedelta(days=30),
        identity_valid_to=freeze + timedelta(days=30),
        action_status="submitted",
        action_value=1.0,
        failure_code=None,
    )
    leaked = replace(valid, feature_as_of=valid.outcome_at)
    stale_identity = replace(valid, identity_valid_to=valid.action_at)
    malformed_status = replace(
        valid,
        action_status="failed",
        action_value=None,
        failure_code=None,
    )
    return (
        not observation_violations(valid),
        "feature timestamp exceeds forecast freeze" in observation_violations(leaked),
        "participant identity is not effective at action time"
        in observation_violations(stale_identity),
        "failed action requires a failure code" in observation_violations(malformed_status),
    )


def _sha256_float64(values: FloatArray) -> str:
    contiguous = np.ascontiguousarray(values, dtype="<f8")
    return hashlib.sha256(contiguous.tobytes()).hexdigest()


def run_synthetic_calibration(settings: CalibrationSettings) -> dict[str, object]:
    """Execute the frozen generated-data false-positive and power calibration."""

    null_p_values = np.empty(settings.replicates, dtype=np.float64)
    effect_p_values = np.empty(settings.replicates, dtype=np.float64)
    clock_improvements = np.empty(settings.replicates, dtype=np.float64)
    valid_acceptance = 0
    leakage_detection = 0
    identity_detection = 0
    status_detection = 0
    direction = _direction(settings.response_dimension)
    effect_mean = _effect_path(settings)
    shifted_mean = np.concatenate(
        (
            np.repeat(effect_mean[[0]], settings.clock_shift_blocks, axis=0),
            effect_mean[: -settings.clock_shift_blocks],
        ),
        axis=0,
    )
    zero_mean = np.zeros_like(effect_mean)
    null_positive_mean = np.repeat(
        (settings.null_symmetric_bias * direction)[None, :],
        settings.independent_blocks,
        axis=0,
    )
    null_negative_mean = -null_positive_mean

    for replicate in range(settings.replicates):
        null_rng = _rng(settings.root_seed, "null", replicate)
        null_outcome = null_rng.normal(
            0.0,
            settings.outcome_standard_deviation,
            size=(settings.independent_blocks, settings.response_dimension),
        )
        null_residuals = null_rng.normal(
            0.0,
            settings.forecast_standard_deviation,
            size=(settings.independent_blocks, settings.ensemble_size, settings.response_dimension),
        )
        null_positive_loss = ensemble_energy_score(
            null_outcome,
            _forecast_ensemble(null_positive_mean, null_residuals),
        )
        null_negative_loss = ensemble_energy_score(
            null_outcome,
            _forecast_ensemble(null_negative_mean, null_residuals),
        )
        null_p_values[replicate] = paired_randomization_p_value(
            null_positive_loss - null_negative_loss,
            draws=settings.permutation_draws,
            rng=_rng(settings.root_seed, "null-randomization", replicate),
        )

        effect_rng = _rng(settings.root_seed, "effect", replicate)
        effect_outcome = effect_mean + effect_rng.normal(
            0.0,
            settings.outcome_standard_deviation,
            size=(settings.independent_blocks, settings.response_dimension),
        )
        effect_residuals = effect_rng.normal(
            0.0,
            settings.forecast_standard_deviation,
            size=(settings.independent_blocks, settings.ensemble_size, settings.response_dimension),
        )
        baseline_loss = ensemble_energy_score(
            effect_outcome,
            _forecast_ensemble(zero_mean, effect_residuals),
        )
        correct_loss = ensemble_energy_score(
            effect_outcome,
            _forecast_ensemble(effect_mean, effect_residuals),
        )
        shifted_loss = ensemble_energy_score(
            effect_outcome,
            _forecast_ensemble(shifted_mean, effect_residuals),
        )
        effect_p_values[replicate] = paired_randomization_p_value(
            baseline_loss - correct_loss,
            draws=settings.permutation_draws,
            rng=_rng(settings.root_seed, "effect-randomization", replicate),
        )
        clock_improvements[replicate] = float(np.mean(shifted_loss - correct_loss))

        valid, leaked, stale_identity, malformed_status = _structural_detection(replicate)
        valid_acceptance += int(valid)
        leakage_detection += int(leaked)
        identity_detection += int(stale_identity)
        status_detection += int(malformed_status)

    null_rejections = int(np.count_nonzero(null_p_values < settings.alpha))
    effect_rejections = int(np.count_nonzero(effect_p_values < settings.alpha))
    false_positive_rate = null_rejections / settings.replicates
    effect_power = effect_rejections / settings.replicates
    calibration_p = float(
        binomtest(null_rejections, settings.replicates, settings.alpha).pvalue
    )
    clock_selection_rate = float(np.mean(clock_improvements > 0.0))
    valid_acceptance_rate = valid_acceptance / settings.replicates
    leakage_detection_rate = leakage_detection / settings.replicates
    identity_detection_rate = identity_detection / settings.replicates
    status_detection_rate = status_detection / settings.replicates
    gates = {
        "null_false_positive_rate": (
            false_positive_rate <= settings.null_false_positive_rate_maximum
        ),
        "null_binomial_calibration": (
            calibration_p >= settings.null_binomial_calibration_p_minimum
        ),
        "effect_power": effect_power >= settings.effect_power_minimum,
        "correct_clock_selection": (
            clock_selection_rate >= settings.correct_clock_selection_rate_minimum
        ),
        "leakage_detection": (
            leakage_detection_rate >= settings.leakage_detection_rate_required
        ),
        "identity_violation_detection": (
            identity_detection_rate >= settings.identity_violation_detection_rate_required
        ),
        "status_contract_detection": (
            status_detection_rate >= settings.status_contract_detection_rate_required
        ),
        "valid_record_acceptance": valid_acceptance_rate == 1.0,
    }
    return {
        "schema": "ecophys-open-data-synthetic-calibration/v1",
        "protocol": settings.protocol,
        "settings": asdict(settings),
        "statistical_unit": "independent_generated_block",
        "null": {
            "rejections": null_rejections,
            "replicates": settings.replicates,
            "false_positive_rate": false_positive_rate,
            "binomial_calibration_p_value": calibration_p,
            "p_values_sha256": _sha256_float64(null_p_values),
        },
        "effect": {
            "rejections": effect_rejections,
            "replicates": settings.replicates,
            "power": effect_power,
            "p_values_sha256": _sha256_float64(effect_p_values),
        },
        "clock": {
            "correct_selection_rate": clock_selection_rate,
            "mean_shifted_minus_correct_energy_score": float(np.mean(clock_improvements)),
            "improvements_sha256": _sha256_float64(clock_improvements),
        },
        "structural_contract": {
            "valid_record_acceptance_rate": valid_acceptance_rate,
            "leakage_detection_rate": leakage_detection_rate,
            "identity_violation_detection_rate": identity_detection_rate,
            "status_contract_detection_rate": status_detection_rate,
        },
        "gates": gates,
        "pass": all(gates.values()),
    }


def canonical_result_sha256(result: dict[str, object]) -> str:
    """Hash the deterministic scientific result before runtime ownership fields."""

    payload = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
