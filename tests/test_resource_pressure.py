from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import yaml

from ecomd.physics.resource_pressure import (
    advance_log_rate_at_target,
    apply_allocation_flows,
    control_pressure,
    equalized_supply,
    morpho_normalized_error,
    pressure_continuity_residual,
    utilization,
    utilization_minimax_lower_bound,
)
from scripts.probe_morpho_controller_coupling_t0 import _gate, _run_checks, _validate_contract


def test_allocation_transports_pressure_without_changing_total() -> None:
    borrowed = np.array([70.0, 36.0, 18.0])
    supplied = np.array([80.0, 60.0, 40.0])
    flows = np.array([[0.0, 4.0, 2.0], [1.0, 0.0, 0.0], [0.0, 3.0, 0.0]])
    updated = apply_allocation_flows(supplied, flows)
    before = control_pressure(borrowed, supplied, 0.9)
    after = control_pressure(borrowed, updated, 0.9)

    np.testing.assert_allclose(
        pressure_continuity_residual(borrowed, supplied, flows, 0.9),
        0.0,
        atol=2e-15,
    )
    assert after.sum() == pytest.approx(before.sum())
    assert updated.sum() == pytest.approx(supplied.sum())


def test_equalization_attains_unavoidable_common_error_bound() -> None:
    borrowed = np.array([40.0, 30.0, 20.0])
    equal_supply = equalized_supply(borrowed, total_supplied_assets=120.0)
    equal_utilization = utilization(borrowed, equal_supply)
    lower_bound = utilization_minimax_lower_bound(borrowed, equal_supply, 0.9)

    np.testing.assert_allclose(equal_utilization, 0.75)
    assert np.max(np.abs(equal_utilization - 0.9)) == pytest.approx(lower_bound)
    assert control_pressure(borrowed, equal_supply, 0.9).sum() == pytest.approx(-18.0)


def test_equalization_freezes_pairwise_log_rate_memory() -> None:
    borrowed = np.array([60.0, 30.0, 15.0])
    supplied = equalized_supply(borrowed, total_supplied_assets=120.0)
    utilizations = utilization(borrowed, supplied)
    log_rates = np.log(np.array([0.03, 0.05, 0.08]))
    advanced = advance_log_rate_at_target(
        log_rates,
        utilizations,
        target_utilization=0.9,
        adjustment_speed_per_second=50.0 / (365.0 * 24.0 * 60.0 * 60.0),
        elapsed_seconds=900.0,
    )

    np.testing.assert_allclose(advanced[:, None] - advanced[None, :], log_rates[:, None] - log_rates[None, :])
    assert not np.allclose(advanced, log_rates)


def test_morpho_error_uses_asymmetric_normalization() -> None:
    errors = morpho_normalized_error(np.array([0.45, 0.9, 0.95, 1.0]), 0.9)
    np.testing.assert_allclose(errors, np.array([-0.5, 0.0, 0.5, 1.0]))


def test_frozen_t0_contract_passes_small_deterministic_probe() -> None:
    config = yaml.safe_load(
        Path("configs/empirical_physics/morpho_controller_coupling_t0_v1.yaml").read_text(encoding="utf-8")
    )
    config["trials"] = 32
    _validate_contract(config)
    metrics = _run_checks(config)
    assert all(_gate(config, metrics).values())
    assert metrics["nonzero_common_mode_trials"] > 0


@pytest.mark.parametrize(
    ("supplied", "flows", "message"),
    [
        ([1.0, 1.0], [[0.0, 1.0], [0.0, 0.0]], "retain positive"),
        ([1.0, 1.0], [[0.1, 0.0], [0.0, 0.0]], "zero diagonal"),
    ],
)
def test_invalid_allocation_flows_fail(supplied: list[float], flows: list[list[float]], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        apply_allocation_flows(supplied, flows)
