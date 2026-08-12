from __future__ import annotations

import pytest

from ecomd.invariant_calibration.g0_gate_aggregation import (
    ResourceObservations,
    aggregate_positive_gates,
    has_positive_gate_namespace,
    resource_pass_gates,
)


def test_zero_resource_observations_map_to_positive_passes() -> None:
    observations = ResourceObservations(
        market_data_files_read=0,
        sealed_periods_opened=0,
        gpu_hours=0.0,
    )

    gates = resource_pass_gates(observations)

    assert gates == {
        "no_market_data_read": True,
        "no_sealed_period_opened": True,
        "no_gpu_usage": True,
    }
    assert has_positive_gate_namespace(gates)
    assert aggregate_positive_gates(gates)


@pytest.mark.parametrize(
    ("observations", "failed_gate"),
    [
        (ResourceObservations(1, 0, 0.0), "no_market_data_read"),
        (ResourceObservations(0, 1, 0.0), "no_sealed_period_opened"),
        (ResourceObservations(0, 0, 0.25), "no_gpu_usage"),
    ],
)
def test_nonzero_resource_observation_fails_its_positive_gate(
    observations: ResourceObservations, failed_gate: str
) -> None:
    gates = resource_pass_gates(observations)

    assert gates[failed_gate] is False
    assert not aggregate_positive_gates(gates)


def test_raw_actual_observation_cannot_enter_gate_namespace() -> None:
    invalid = {"actual_market_data_read": False}

    assert not has_positive_gate_namespace(invalid)
    with pytest.raises(ValueError, match="positive literal boolean"):
        aggregate_positive_gates(invalid)


@pytest.mark.parametrize(
    "invalid",
    [
        {},
        {"no_gpu_usage": 1},
        {"no_gpu_usage": None},
        {"": True},
    ],
)
def test_only_nonempty_literal_boolean_pass_predicates_are_accepted(
    invalid: dict[str, object],
) -> None:
    assert not has_positive_gate_namespace(invalid)
    with pytest.raises(ValueError):
        aggregate_positive_gates(invalid)


@pytest.mark.parametrize(
    "arguments",
    [(-1, 0, 0.0), (0, -1, 0.0), (0, 0, -0.1), (0, 0, float("inf"))],
)
def test_invalid_resource_observations_are_rejected(
    arguments: tuple[int, int, float],
) -> None:
    with pytest.raises(ValueError):
        ResourceObservations(*arguments)
