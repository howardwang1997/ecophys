"""Development-only fitting for Experiment 141."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import least_squares

from .feasibility import (
    PRIMARY_COMPONENTS,
    ResponseParameters,
    SimulationResult,
    expected_market_probability,
    simulate_path,
    truth_response,
)
from .protocol import Protocol

FitFamily = Literal["none", "single_rate", "two_rate"]


@dataclass(frozen=True)
class DevelopmentObservation:
    family: FitFamily
    seed: int
    magnitude: float
    post_epoch: int
    market_fraction: float


@dataclass(frozen=True)
class FittedResponse:
    target_slope: float
    rate: float
    objective_rmse: float
    n_observations: int


def fit_response(
    protocol: Protocol,
    family: Literal["single_rate", "two_rate"],
    observations: list[DevelopmentObservation],
) -> FittedResponse:
    selected = [observation for observation in observations if observation.family == family]
    if not selected:
        raise ValueError(f"no development observations for {family}")

    def residuals(parameters: NDArray[np.float64]) -> NDArray[np.float64]:
        slope, rate = (float(parameters[0]), float(parameters[1]))
        response = ResponseParameters(kind="single_rate", target_slope=slope, rate=rate)
        return np.asarray(
            [
                expected_market_probability(
                    protocol.world,
                    response,
                    observation.magnitude,
                    observation.post_epoch,
                )
                - observation.market_fraction
                for observation in selected
            ],
            dtype=np.float64,
        )

    result = least_squares(
        residuals,
        x0=np.asarray([-0.5, 0.2], dtype=np.float64),
        bounds=(
            np.asarray(
                [protocol.fit.target_slope_bounds[0], protocol.fit.rho_bounds[0]],
                dtype=np.float64,
            ),
            np.asarray(
                [protocol.fit.target_slope_bounds[1], protocol.fit.rho_bounds[1]],
                dtype=np.float64,
            ),
        ),
        method="trf",
    )
    errors = residuals(result.x)
    return FittedResponse(
        target_slope=float(result.x[0]),
        rate=float(result.x[1]),
        objective_rmse=float(np.sqrt(np.mean(errors**2))),
        n_observations=len(selected),
    )


def _post_observations(
    family: FitFamily,
    seed: int,
    magnitude: float,
    result: SimulationResult,
) -> list[DevelopmentObservation]:
    post = [epoch for epoch in result.epochs if epoch.is_post]
    return [
        DevelopmentObservation(
            family=family,
            seed=seed,
            magnitude=magnitude,
            post_epoch=index,
            market_fraction=epoch.market_fraction,
        )
        for index, epoch in enumerate(post)
    ]


def run_development_fit(protocol: Protocol) -> dict[str, object]:
    """Use only the configured development seeds and magnitudes."""

    observations: list[DevelopmentObservation] = []
    effects: list[tuple[float, ...]] = []
    violation_paths = 0
    path_count = 0
    counterfactuals: dict[int, SimulationResult] = {}
    truth_results: dict[tuple[FitFamily, int, float], SimulationResult] = {}
    families: tuple[FitFamily, ...] = ("none", "single_rate", "two_rate")

    for seed in range(
        protocol.development.seed_start,
        protocol.development.seed_start + protocol.development.n_seeds,
    ):
        counterfactual = simulate_path(
            protocol.world,
            seed,
            0.0,
            ResponseParameters(kind="frozen"),
            intervention=False,
        )
        counterfactuals[seed] = counterfactual
        path_count += 1
        violation_paths += int(bool(counterfactual.mechanics_violations))
        for magnitude in protocol.development.intervention_magnitudes:
            for family in families:
                result = simulate_path(
                    protocol.world,
                    seed,
                    magnitude,
                    truth_response(protocol.world, family),
                    intervention=True,
                )
                truth_results[(family, seed, magnitude)] = result
                observations.extend(_post_observations(family, seed, magnitude, result))
                effects.append(result.primary_effect(counterfactual))
                path_count += 1
                violation_paths += int(bool(result.mechanics_violations))

    single = fit_response(protocol, "single_rate", observations)
    two_rate = fit_response(protocol, "two_rate", observations)
    effect_array = np.asarray(effects, dtype=np.float64)
    standard_deviations = np.std(effect_array, axis=0, ddof=1)
    minimum_scale = 1.0 / protocol.world.events_per_epoch
    standard_deviations = np.maximum(standard_deviations, minimum_scale)

    fitted: dict[str, FittedResponse] = {
        "none": FittedResponse(
            target_slope=0.0,
            rate=single.rate,
            objective_rmse=0.0,
            n_observations=sum(observation.family == "none" for observation in observations),
        ),
        "single_rate": single,
        "two_rate": two_rate,
    }
    return {
        "fit_protocol": "development-only-family-conditioned-v1",
        "families": {
            family: {
                "target_slope": fit.target_slope,
                "rate": fit.rate,
                "objective_rmse": fit.objective_rmse,
                "n_observations": fit.n_observations,
            }
            for family, fit in fitted.items()
        },
        "standardizer": {
            "components": list(PRIMARY_COMPONENTS),
            "scale": standard_deviations.tolist(),
            "minimum_scale": minimum_scale,
            "n_vectors": int(effect_array.shape[0]),
        },
        "detector": {
            "reference_family": "single_rate",
            "target_slope": single.target_slope,
            "rate": single.rate,
            "early_epochs": protocol.world.confound_epochs,
            "absolute_z_threshold": protocol.gates.confound_residual_z_threshold,
        },
        "development_audit": {
            "seed_start": protocol.development.seed_start,
            "n_seeds": protocol.development.n_seeds,
            "magnitudes": list(protocol.development.intervention_magnitudes),
            "path_count": path_count,
            "mechanics_violation_paths": violation_paths,
            "formal_seed_minimum": protocol.evaluation.seed_start,
            "formal_seeds_touched": False,
        },
    }


def detector_z_score(
    protocol: Protocol,
    result: SimulationResult,
    target_slope: float,
    rate: float,
) -> float:
    response = ResponseParameters(kind="single_rate", target_slope=target_slope, rate=rate)
    post = [epoch for epoch in result.epochs if epoch.is_post]
    early = post[: protocol.world.confound_epochs]
    expected = [
        expected_market_probability(protocol.world, response, result.magnitude, index)
        for index in range(len(early))
    ]
    expected_count = protocol.world.events_per_epoch * sum(expected)
    variance = protocol.world.events_per_epoch * sum(
        probability * (1.0 - probability) for probability in expected
    )
    observed_count = sum(epoch.market_orders for epoch in early)
    if variance <= 0.0:
        return math.inf if observed_count != expected_count else 0.0
    return float((observed_count - expected_count) / math.sqrt(variance))
