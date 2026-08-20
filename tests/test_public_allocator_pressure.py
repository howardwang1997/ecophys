from __future__ import annotations

import numpy as np
import pytest

from ecomd.physics.public_allocator_pressure import (
    apply_flow_cap_reallocation,
    displaced_pressure_fraction,
    independent_vault_target_capacity,
    pure_routing_pressure_changes,
    routed_borrow_pressure_changes,
    target_inflow_capacity,
)


def test_full_jit_borrow_displaces_ninety_percent_to_donors() -> None:
    changes = routed_borrow_pressure_changes(np.array([30.0, 70.0]), 100.0)
    np.testing.assert_allclose(changes, np.array([27.0, 63.0, 10.0]))
    assert displaced_pressure_fraction(100.0, 100.0) == pytest.approx(0.9)
    assert np.sum(changes) == pytest.approx(100.0)


def test_partial_jit_partition_and_pure_transport() -> None:
    flows = np.array([10.0, 20.0])
    pure = pure_routing_pressure_changes(flows)
    jit = routed_borrow_pressure_changes(flows, 50.0)
    np.testing.assert_allclose(pure, np.array([9.0, 18.0, -27.0]))
    np.testing.assert_allclose(jit, np.array([9.0, 18.0, 23.0]))
    assert displaced_pressure_fraction(50.0, 30.0) == pytest.approx(0.54)


def test_routed_fill_cannot_exceed_compatible_borrow() -> None:
    with pytest.raises(ValueError, match="cannot exceed"):
        routed_borrow_pressure_changes(np.array([60.0, 50.0]), 100.0)


def test_flow_cap_transition_preserves_pair_budgets() -> None:
    max_in = np.array([3.0, 4.0, 100.0])
    max_out = np.array([20.0, 30.0, 5.0])
    flows = np.array([10.0, 25.0, 0.0])
    new_in, new_out = apply_flow_cap_reallocation(
        max_in,
        max_out,
        flows,
        target_index=2,
    )
    np.testing.assert_allclose(new_in, np.array([13.0, 29.0, 65.0]))
    np.testing.assert_allclose(new_out, np.array([10.0, 5.0, 40.0]))
    np.testing.assert_allclose(new_in + new_out, max_in + max_out)


@pytest.mark.parametrize(
    ("max_in", "max_out", "flows", "message"),
    [
        ([0.0, 4.0], [5.0, 0.0], [6.0, 0.0], "max_out"),
        ([0.0, 4.0], [5.0, 0.0], [5.0, 0.0], "max_in"),
        ([0.0, 4.0], [5.0, 0.0], [0.0, 1.0], "cannot also be a donor"),
    ],
)
def test_flow_cap_transition_rejects_infeasible_moves(
    max_in: list[float], max_out: list[float], flows: list[float], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        apply_flow_cap_reallocation(
            np.array(max_in),
            np.array(max_out),
            np.array(flows),
            target_index=1,
        )


def test_one_vault_capacity_is_target_or_donor_cut() -> None:
    assert target_inflow_capacity(50.0, np.array([100.0, 20.0]), np.array([10.0, 40.0])) == 30.0
    assert target_inflow_capacity(25.0, np.array([100.0, 20.0]), np.array([10.0, 40.0])) == 25.0


def test_independent_vault_capacities_add() -> None:
    capacity = independent_vault_target_capacity(
        np.array([25.0, 100.0]),
        np.array([[100.0, 20.0], [5.0, 40.0]]),
        np.array([[10.0, 40.0], [50.0, 30.0]]),
    )
    assert capacity == 60.0


def test_pressure_inputs_are_validated() -> None:
    with pytest.raises(ValueError, match="positive"):
        displaced_pressure_fraction(0.0, 0.0)
    with pytest.raises(ValueError, match="nonnegative"):
        pure_routing_pressure_changes(np.array([-1.0]))
