"""Cache deterministic FIFO allocations while preserving estimator streams."""
from __future__ import annotations
from collections.abc import Callable
from typing import cast
from functools import lru_cache

import torch
from ecomd.mechanisms.through_m import (
    Kernel, PINNED_STRAIGHT_THROUGH_SCALE, _StraightThrough, _validated_quantities,
)
from ecomd.mechanisms.through_m_wrapper import (
    NOMINAL_LEVEL_PRICE, TrainKernelStream, _require_floating,
    engine_execute_level,
)


def cached_fifo_hook(stream: TrainKernelStream) -> Callable[[torch.Tensor, int], torch.Tensor]:
    """FIFO allocations ignore the seed; paired kernel streams still advance."""
    @lru_cache(maxsize=8192)
    def allocation(resting: tuple[int, ...], demand: int) -> tuple[torch.Tensor, torch.Tensor]:
        outcome = engine_execute_level(torch.tensor(resting, dtype=torch.int64), demand,
            level_price=NOMINAL_LEVEL_PRICE, kernel=Kernel.FIFO, engine_seed=0)
        return outcome.allocation_exact, outcome.filled_mask

    def mechanism(quantities: torch.Tensor, demand: int) -> torch.Tensor:
        stream.next_call_seeds()
        _require_floating(quantities)
        resting = tuple(_validated_quantities(quantities))
        if not isinstance(demand, int) or isinstance(demand, bool) or demand < 1:
            raise ValueError('incoming demand must be a positive integer')
        exact, mask = allocation(resting, demand)
        return cast(torch.Tensor, _StraightThrough.apply(  # type: ignore[no-untyped-call]
            quantities, exact, mask, PINNED_STRAIGHT_THROUGH_SCALE))

    return mechanism
