"""Source-bound pressure identities for routed Morpho borrows."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def _nonnegative_vector(values: FloatArray, *, name: str) -> FloatArray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1 or array.size == 0:
        raise ValueError(f"{name} must be a nonempty one-dimensional array")
    if not np.all(np.isfinite(array)) or np.any(array < 0.0):
        raise ValueError(f"{name} must contain finite nonnegative values")
    return array


def routed_borrow_pressure_changes(
    donor_flows: FloatArray,
    borrow_assets: float,
    *,
    target_utilization: float = 0.9,
) -> FloatArray:
    """Return donor changes followed by the target change for a JIT borrow."""
    flows = _nonnegative_vector(donor_flows, name="donor_flows")
    if not np.isfinite(borrow_assets) or borrow_assets < 0.0:
        raise ValueError("borrow_assets must be finite and nonnegative")
    if not 0.0 < target_utilization < 1.0:
        raise ValueError("target_utilization must lie strictly between zero and one")
    routed = float(np.sum(flows, dtype=np.float64))
    tolerance = np.finfo(np.float64).eps * max(1.0, routed, borrow_assets) * flows.size
    if routed > borrow_assets + tolerance:
        raise ValueError("a JIT liquidity-shortfall fill cannot exceed the compatible borrow")
    donor_changes = target_utilization * flows
    target_change = borrow_assets - target_utilization * routed
    return np.concatenate((donor_changes, np.array([target_change], dtype=np.float64)))


def pure_routing_pressure_changes(
    donor_flows: FloatArray,
    *,
    target_utilization: float = 0.9,
) -> FloatArray:
    """Return pressure transport for a reallocation without a borrow source."""
    flows = _nonnegative_vector(donor_flows, name="donor_flows")
    if not 0.0 < target_utilization < 1.0:
        raise ValueError("target_utilization must lie strictly between zero and one")
    routed = float(np.sum(flows, dtype=np.float64))
    donor_changes = target_utilization * flows
    return np.concatenate((donor_changes, np.array([-target_utilization * routed], dtype=np.float64)))


def displaced_pressure_fraction(
    borrow_assets: float,
    routed_assets: float,
    *,
    target_utilization: float = 0.9,
) -> float:
    """Return the fraction of borrow-source pressure placed on donor markets."""
    if not np.isfinite(borrow_assets) or borrow_assets <= 0.0:
        raise ValueError("borrow_assets must be finite and positive")
    if not np.isfinite(routed_assets) or not 0.0 <= routed_assets <= borrow_assets:
        raise ValueError("routed_assets must lie between zero and borrow_assets")
    if not 0.0 < target_utilization < 1.0:
        raise ValueError("target_utilization must lie strictly between zero and one")
    return target_utilization * routed_assets / borrow_assets


def apply_flow_cap_reallocation(
    max_in: FloatArray,
    max_out: FloatArray,
    donor_flows: FloatArray,
    *,
    target_index: int,
) -> tuple[FloatArray, FloatArray]:
    """Apply the exact PublicAllocator directional cap transition."""
    incoming = _nonnegative_vector(max_in, name="max_in").copy()
    outgoing = _nonnegative_vector(max_out, name="max_out").copy()
    flows = np.asarray(donor_flows, dtype=np.float64)
    if incoming.shape != outgoing.shape or flows.shape != incoming.shape:
        raise ValueError("max_in, max_out and donor_flows must have identical shapes")
    if not np.all(np.isfinite(flows)) or np.any(flows < 0.0):
        raise ValueError("donor_flows must contain finite nonnegative values")
    if not 0 <= target_index < flows.size:
        raise ValueError("target_index is outside the market array")
    if flows[target_index] != 0.0:
        raise ValueError("target market cannot also be a donor")
    if np.any(flows > outgoing):
        raise ValueError("donor flow exceeds max_out")
    routed = float(np.sum(flows, dtype=np.float64))
    if routed > incoming[target_index]:
        raise ValueError("routed flow exceeds target max_in")

    donor_mask = np.arange(flows.size) != target_index
    incoming[donor_mask] += flows[donor_mask]
    outgoing[donor_mask] -= flows[donor_mask]
    incoming[target_index] -= routed
    outgoing[target_index] += routed
    return incoming, outgoing


def target_inflow_capacity(
    target_max_in: float,
    donor_max_out: FloatArray,
    donor_supply_assets: FloatArray,
) -> float:
    """Return the one-vault feasible target inflow under cap and supply bounds."""
    max_out = _nonnegative_vector(donor_max_out, name="donor_max_out")
    supply = _nonnegative_vector(donor_supply_assets, name="donor_supply_assets")
    if max_out.shape != supply.shape:
        raise ValueError("donor_max_out and donor_supply_assets must have identical shapes")
    if not np.isfinite(target_max_in) or target_max_in < 0.0:
        raise ValueError("target_max_in must be finite and nonnegative")
    donor_capacity = float(np.sum(np.minimum(max_out, supply), dtype=np.float64))
    return min(target_max_in, donor_capacity)


def independent_vault_target_capacity(
    target_max_in: FloatArray,
    donor_max_out: FloatArray,
    donor_supply_assets: FloatArray,
) -> float:
    """Sum target capacity across independent vault positions."""
    target_caps = _nonnegative_vector(target_max_in, name="target_max_in")
    max_out = np.asarray(donor_max_out, dtype=np.float64)
    supply = np.asarray(donor_supply_assets, dtype=np.float64)
    if max_out.ndim != 2 or supply.shape != max_out.shape:
        raise ValueError("donor cap and supply inputs must be equal two-dimensional arrays")
    if max_out.shape[0] != target_caps.size or max_out.shape[1] == 0:
        raise ValueError("each vault must have at least one aligned donor")
    if not np.all(np.isfinite(max_out)) or not np.all(np.isfinite(supply)):
        raise ValueError("donor cap and supply inputs must be finite")
    if np.any(max_out < 0.0) or np.any(supply < 0.0):
        raise ValueError("donor cap and supply inputs must be nonnegative")
    donor_capacity = np.sum(np.minimum(max_out, supply), axis=1, dtype=np.float64)
    return float(np.sum(np.minimum(target_caps, donor_capacity), dtype=np.float64))
