"""Deterministic scale audit for the declared Ethereum BPO schedules."""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Sequence
from dataclasses import dataclass

from ecomd.research.fee_controller_oracle import BlobSchedule, calculate_blob_base_fee


@dataclass(frozen=True)
class DeclaredSchedule:
    """One protocol-declared blob schedule used by the scale audit."""

    name: str
    target: int
    maximum: int
    update_fraction: int

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("schedule name must be nonempty")
        BlobSchedule(self.target, self.maximum, self.update_fraction)

    @property
    def oracle(self) -> BlobSchedule:
        """Return the bit-exact fee-controller schedule."""

        return BlobSchedule(self.target, self.maximum, self.update_fraction)


DECLARED_SCHEDULES: tuple[DeclaredSchedule, ...] = (
    DeclaredSchedule("Prague/Osaka", 6, 9, 5_007_716),
    DeclaredSchedule("BPO1", 10, 15, 8_346_193),
    DeclaredSchedule("BPO2", 14, 21, 11_684_671),
)


def continuous_schedule_metrics(schedule: DeclaredSchedule) -> dict[str, object]:
    """Calculate normalized continuous-relaxation metrics for one schedule."""

    gas_per_blob = schedule.oracle.gas_per_blob
    full_log_step = gas_per_blob * (schedule.maximum - schedule.target) / schedule.update_fraction
    empty_log_step = -gas_per_blob * schedule.target / schedule.update_fraction
    return {
        "name": schedule.name,
        "target": schedule.target,
        "maximum": schedule.maximum,
        "update_fraction": schedule.update_fraction,
        "maximum_over_target": schedule.maximum / schedule.target,
        "update_fraction_over_target": schedule.update_fraction / schedule.target,
        "full_block_log_step": full_log_step,
        "full_block_relative_change": math.expm1(full_log_step),
        "empty_block_relative_change": math.expm1(empty_log_step),
    }


def standardized_fee(
    schedule: DeclaredSchedule,
    state_numerator: int,
    state_denominator: int = 1,
) -> int:
    """Evaluate the exact fee at standardized excess ``s=numerator/denominator``."""

    if state_numerator < 0 or state_denominator <= 0:
        raise ValueError("standardized state requires numerator >= 0 and denominator > 0")
    unscaled = schedule.oracle.gas_per_blob * schedule.target * state_numerator
    excess, remainder = divmod(unscaled, state_denominator)
    if remainder:
        raise ValueError("standardized state does not map to an integer excess")
    return calculate_blob_base_fee(excess, schedule.oracle)


def exact_grid_audit(
    schedules: Sequence[DeclaredSchedule] = DECLARED_SCHEDULES,
    *,
    quarter_grid_max: int = 64,
    integer_grid_max: int = 2_000,
) -> dict[str, object]:
    """Compare exact standardized fees on the two declared deterministic grids."""

    if len(schedules) < 2:
        raise ValueError("scale audit requires at least two schedules")
    if quarter_grid_max < 0 or integer_grid_max < 0:
        raise ValueError("grid maxima must be nonnegative")

    quarter_all_equal = True
    for numerator in range(4 * quarter_grid_max + 1):
        values = [standardized_fee(schedule, numerator, 4) for schedule in schedules]
        quarter_all_equal = quarter_all_equal and len(set(values)) == 1

    first_difference_state: int | None = None
    first_difference_values: list[int] | None = None
    maximum_relative_spread = 0.0
    maximum_spread_state = 0
    maximum_spread_values: list[int] = []
    for state in range(integer_grid_max + 1):
        values = [standardized_fee(schedule, state) for schedule in schedules]
        if first_difference_state is None and len(set(values)) > 1:
            first_difference_state = state
            first_difference_values = values
        relative_spread = (max(values) - min(values)) / max(values)
        if relative_spread > maximum_relative_spread:
            maximum_relative_spread = relative_spread
            maximum_spread_state = state
            maximum_spread_values = values

    return {
        "quarter_grid": {
            "minimum": 0.0,
            "maximum": float(quarter_grid_max),
            "step": 0.25,
            "all_exact_fees_equal": quarter_all_equal,
        },
        "integer_grid": {
            "minimum": 0,
            "maximum": integer_grid_max,
            "first_difference_state": first_difference_state,
            "first_difference_values": first_difference_values,
            "maximum_relative_spread": maximum_relative_spread,
            "maximum_spread_state": maximum_spread_state,
            "maximum_spread_values": maximum_spread_values,
        },
    }


def build_scale_audit() -> dict[str, object]:
    """Build the complete deterministic BPO scale-audit payload."""

    metrics = [continuous_schedule_metrics(schedule) for schedule in DECLARED_SCHEDULES]
    baseline = DECLARED_SCHEDULES[0].update_fraction / DECLARED_SCHEDULES[0].target
    for schedule, metric in zip(DECLARED_SCHEDULES, metrics, strict=True):
        value = schedule.update_fraction / schedule.target
        metric["relative_update_fraction_over_target_difference"] = value / baseline - 1.0
    return {
        "schema_version": "ecophys-fee-controller-scale-audit/v1",
        "scope": "protocol constants only; no chain outcomes",
        "schedules": metrics,
        "exact_grid_audit": exact_grid_audit(),
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Print the deterministic scale audit as canonical JSON."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    print(json.dumps(build_scale_audit(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
