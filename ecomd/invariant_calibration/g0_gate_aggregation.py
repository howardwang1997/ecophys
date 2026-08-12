"""Positive-predicate aggregation for G0 process gates."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceObservations:
    market_data_files_read: int
    sealed_periods_opened: int
    gpu_hours: float

    def __post_init__(self) -> None:
        if self.market_data_files_read < 0:
            raise ValueError("market_data_files_read must be non-negative")
        if self.sealed_periods_opened < 0:
            raise ValueError("sealed_periods_opened must be non-negative")
        if not math.isfinite(self.gpu_hours) or self.gpu_hours < 0.0:
            raise ValueError("gpu_hours must be finite and non-negative")

    def to_dict(self) -> dict[str, object]:
        return {
            "market_data_files_read": self.market_data_files_read,
            "sealed_periods_opened": self.sealed_periods_opened,
            "gpu_hours": self.gpu_hours,
        }


def resource_pass_gates(observations: ResourceObservations) -> dict[str, bool]:
    """Convert raw resource observations into positively named pass predicates."""
    return {
        "no_market_data_read": observations.market_data_files_read == 0,
        "no_sealed_period_opened": observations.sealed_periods_opened == 0,
        "no_gpu_usage": observations.gpu_hours == 0.0,
    }


def has_positive_gate_namespace(gates: Mapping[str, object]) -> bool:
    """Return whether every gate is a positive, literal boolean predicate."""
    return bool(gates) and all(
        isinstance(key, str)
        and bool(key)
        and not key.startswith("actual_")
        and type(value) is bool
        for key, value in gates.items()
    )


def aggregate_positive_gates(gates: Mapping[str, object]) -> bool:
    """Aggregate gates only after enforcing positive boolean semantics."""
    if not has_positive_gate_namespace(gates):
        raise ValueError("gate mapping must contain only positive literal boolean predicates")
    return all(value is True for value in gates.values())


__all__ = [
    "ResourceObservations",
    "aggregate_positive_gates",
    "has_positive_gate_namespace",
    "resource_pass_gates",
]
