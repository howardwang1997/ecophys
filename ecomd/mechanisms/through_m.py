"""Through-M gradient estimators for the lab-asset-v3 clearing kernels.

Implements the frozen two-estimator menu of PI decision D1_07 (KT-A4): a
straight-through estimator with pinned scale (primary) and a perturb-and-MAP
estimator with pinned noise (audit). Forward passes are the exact integer
clearing operations of the reference kernels (``fifo`` and
``random_unit_within_price`` of ``scripts/lab_asset/matching.py``); backward
passes are the preregistered surrogate Jacobians documented in
``papers/proposal/ecomd_reexploration_estimator_menu_2026-09-06.md``.

The straight-through backward generalizes Paper D's projected-training gauge
(``papers/paper_d_constraints/main.tex`` appendix "Proof of the projected-training
gauge"; the ``hard`` enforcement path in ``scripts/run_constraint_iclr_pde.py``
and ``scripts/run_constraint_iclr_pdebench_fno.py``): there the enforcement
Jacobian is exactly ``I - P`` (identity on the constraint complement, zero on the
rank-one gauge direction); here it is a pinned-scale identity on the
cleared/executed coordinates and exactly zero on the never-cleared coordinates,
which are precisely the fiber directions of the T2/T3 theory package.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, cast

import torch

PINNED_STRAIGHT_THROUGH_SCALE: Final[float] = 1.0
PINNED_PERTURB_AND_MAP_SIGMA: Final[float] = 1.0
PINNED_PERTURB_AND_MAP_SEED: Final[int] = 20260906
_INTEGER_TOLERANCE: Final[float] = 1e-6


class Kernel(Enum):
    """Clearing kernels of the lab-asset-v3 engine, by schema value."""

    FIFO = "fifo"
    RANDOM_UNIT_WITHIN_PRICE = "random_unit_within_price"


KERNEL_BY_RULE: Final[dict[str, Kernel]] = {
    Kernel.FIFO.value: Kernel.FIFO,
    Kernel.RANDOM_UNIT_WITHIN_PRICE.value: Kernel.RANDOM_UNIT_WITHIN_PRICE,
}


@dataclass(frozen=True)
class Fill:
    """One engine execution: a maker slot's filled quantity and its residual.

    ``eligible_units``/``selected_unit`` are populated only for per-unit draws,
    mirroring the ``allocation_draw`` payload of the schema.
    """

    queue_index: int
    quantity: int
    maker_remaining_after: int
    eligible_units: int | None = None
    selected_unit: int | None = None


@dataclass(frozen=True)
class ClearingOutcome:
    """Exact (or perturbed-MAP) clearing result for one touched level."""

    allocation: torch.Tensor
    fills: tuple[Fill, ...]
    filled_mask: torch.Tensor


def _require_cpu(values: torch.Tensor) -> None:
    if values.device.type != "cpu":
        raise ValueError(f"through-M estimators are CPU-only, got device {values.device}")


def _validated_quantities(quantities: torch.Tensor) -> list[int]:
    if quantities.ndim != 1 or quantities.numel() < 1:
        raise ValueError("resting quantities must be a non-empty 1-D tensor")
    _require_cpu(quantities)
    floats = quantities.detach().to(dtype=torch.float64)
    if not bool(floats.isfinite().all()):
        raise ValueError("resting quantities must be finite")
    rounded = torch.round(floats)
    if not bool((floats - rounded).abs().le(_INTEGER_TOLERANCE).all()):
        raise ValueError("resting quantities must be integer-valued (engine lattice)")
    as_ints = rounded.to(dtype=torch.int64).tolist()
    resting = [int(value) for value in as_ints]
    if any(value < 0 for value in resting):
        raise ValueError("resting quantities must be nonnegative")
    return resting


def exact_clearing(
    quantities: torch.Tensor,
    demand: int,
    kernel: Kernel,
    draws: Sequence[int] | None = None,
) -> ClearingOutcome:
    """Exact engine clearing for one touched price level.

    ``fifo`` fills queue slots in arrival order to the cumulative threshold;
    ``random_unit_within_price`` consumes the caller-supplied draw stream (the
    training-time kernel stream of contract v1) unit by unit, exactly mirroring
    ``ReferenceEngine._select_maker``.
    """

    resting = _validated_quantities(quantities)
    if demand < 1:
        raise ValueError("incoming demand must be a positive integer")
    executed_total = min(demand, sum(resting))
    allocation = [0] * len(resting)
    fills: list[Fill] = []

    if kernel is Kernel.FIFO:
        remaining_demand = executed_total
        for index, resting_quantity in enumerate(resting):
            if remaining_demand == 0:
                break
            fill = min(remaining_demand, resting_quantity)
            if fill > 0:
                allocation[index] += fill
                remaining_demand -= fill
                fills.append(Fill(index, fill, resting_quantity - fill))
    else:
        if draws is None:
            raise ValueError("random_unit_within_price requires the kernel draw stream")
        if len(draws) != executed_total:
            raise ValueError(
                f"draw stream length {len(draws)} does not match executed units {executed_total}"
            )
        remaining = list(resting)
        for selected_unit in draws:
            eligible_units = sum(remaining)
            if not 0 <= selected_unit < eligible_units:
                raise ValueError(
                    f"draw {selected_unit} outside eligible units [0, {eligible_units})"
                )
            cumulative = 0
            for index, resting_quantity in enumerate(remaining):
                cumulative += resting_quantity
                if selected_unit < cumulative:
                    allocation[index] += 1
                    remaining[index] -= 1
                    fills.append(
                        Fill(
                            index,
                            1,
                            remaining[index],
                            eligible_units=eligible_units,
                            selected_unit=selected_unit,
                        )
                    )
                    break

    allocation_tensor = torch.tensor(allocation, dtype=torch.int64)
    return ClearingOutcome(
        allocation=allocation_tensor,
        fills=tuple(fills),
        filled_mask=allocation_tensor > 0,
    )


def _perturbed_clearing(
    quantities: torch.Tensor,
    demand: int,
    kernel: Kernel,
    *,
    sigma: float,
    seed: int,
) -> ClearingOutcome:
    """Perturb-and-MAP clearing: exact M applied to perturbed priority scores.

    The priority score is a kernel-fixed frozen function of the raw flow:
    ``-queue_position`` for FIFO (arrival priority) and the depleting remaining
    quantity for ``random_unit_within_price`` (the engine's
    probability-proportional-to-remaining-quantity ranking). Frozen-sigma
    Gaussian noise perturbs the scores; the exact decision rule (stable
    descending argsort for FIFO, per-draw argmax with unit depletion for
    random-unit) is applied to the perturbed scores. The noise stream is drawn
    up front from a seeded CPU generator, so identical seeds give identical
    allocations.
    """

    resting = _validated_quantities(quantities)
    if demand < 1:
        raise ValueError("incoming demand must be a positive integer")
    executed_total = min(demand, sum(resting))
    slots = len(resting)
    allocation = [0] * slots
    fills: list[Fill] = []
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed)

    if kernel is Kernel.FIFO:
        scores = -torch.arange(slots, dtype=torch.float64)
        noise = torch.randn(slots, generator=generator, dtype=torch.float64)
        order = torch.argsort(scores + sigma * noise, descending=True, stable=True).tolist()
        remaining_demand = executed_total
        for position in order:
            index = int(position)
            if remaining_demand == 0:
                break
            fill = min(remaining_demand, resting[index])
            if fill > 0:
                allocation[index] += fill
                remaining_demand -= fill
                fills.append(Fill(index, fill, resting[index] - fill))
    else:
        remaining = list(resting)
        noise = torch.randn(
            (executed_total, slots), generator=generator, dtype=torch.float64
        )
        for draw in range(executed_total):
            scores = torch.tensor(remaining, dtype=torch.float64) + sigma * noise[draw]
            index = int(torch.argmax(scores))
            allocation[index] += 1
            remaining[index] -= 1
            fills.append(Fill(index, 1, remaining[index]))

    allocation_tensor = torch.tensor(allocation, dtype=torch.int64)
    return ClearingOutcome(
        allocation=allocation_tensor,
        fills=tuple(fills),
        filled_mask=allocation_tensor > 0,
    )


class _StraightThrough(torch.autograd.Function):
    """Forward: the exact mechanism output. Backward: pinned-scale masked identity."""

    @staticmethod
    def forward(
        ctx: Any,
        quantities: torch.Tensor,
        allocation: torch.Tensor,
        filled_mask: torch.Tensor,
        scale: float,
    ) -> torch.Tensor:
        ctx.save_for_backward(filled_mask)
        ctx.pinned_scale = scale
        return allocation.to(dtype=quantities.dtype)

    @staticmethod
    def backward(
        ctx: Any, grad_output: torch.Tensor
    ) -> tuple[torch.Tensor, None, None, None]:
        (filled_mask,) = ctx.saved_tensors
        scaled = grad_output * filled_mask.to(dtype=grad_output.dtype)
        return scaled * ctx.pinned_scale, None, None, None


class _PerturbAndMap(torch.autograd.Function):
    """Forward: the perturbed-MAP allocation. Backward: perturbed-MAP surrogate.

    The surrogate is the perturb-argmax family Jacobian: unit-scale identity on
    the coordinates the perturbed MAP selected (received at least one unit),
    exactly zero elsewhere.
    """

    @staticmethod
    def forward(
        ctx: Any,
        quantities: torch.Tensor,
        allocation: torch.Tensor,
        filled_mask: torch.Tensor,
    ) -> torch.Tensor:
        ctx.save_for_backward(filled_mask)
        return allocation.to(dtype=quantities.dtype)

    @staticmethod
    def backward(ctx: Any, grad_output: torch.Tensor) -> tuple[torch.Tensor, None, None]:
        (filled_mask,) = ctx.saved_tensors
        return grad_output * filled_mask.to(dtype=grad_output.dtype), None, None


def straight_through_through_m(
    quantities: torch.Tensor,
    demand: int,
    kernel: Kernel,
    draws: Sequence[int] | None = None,
) -> torch.Tensor:
    """Primary through-M estimator: exact forward, straight-through backward.

    The backward surrogate is ``PINNED_STRAIGHT_THROUGH_SCALE`` times the
    identity on cleared/executed coordinates and exactly zero on uncleared
    coordinates. The scale is pinned to a module-level frozen constant; there is
    no learned or caller-configured scale.
    """

    _require_cpu(quantities)
    outcome = exact_clearing(quantities, demand, kernel, draws)
    return cast(
        torch.Tensor,
        _StraightThrough.apply(  # type: ignore[no-untyped-call]
            quantities,
            outcome.allocation,
            outcome.filled_mask,
            PINNED_STRAIGHT_THROUGH_SCALE,
        ),
    )


def perturb_and_map_through_m(
    quantities: torch.Tensor,
    demand: int,
    kernel: Kernel,
    seed: int = PINNED_PERTURB_AND_MAP_SEED,
) -> torch.Tensor:
    """Audit through-M estimator: pinned-noise perturb-and-MAP.

    The noise law (standard normal), sigma (``PINNED_PERTURB_AND_MAP_SIGMA``)
    and generator discipline are pinned module-level constants; the seed is
    supplied by the frozen RNG-tree derivation of contract v1 and defaults to
    the frozen standalone constant.
    """

    _require_cpu(quantities)
    outcome = _perturbed_clearing(
        quantities,
        demand,
        kernel,
        sigma=PINNED_PERTURB_AND_MAP_SIGMA,
        seed=seed,
    )
    return cast(
        torch.Tensor,
        _PerturbAndMap.apply(  # type: ignore[no-untyped-call]
            quantities, outcome.allocation, outcome.filled_mask
        ),
    )
