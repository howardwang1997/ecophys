"""Tests for cross-version AMP decorator selection."""

from __future__ import annotations

from ecomd.models.amp_compat import cuda_custom_bwd, cuda_custom_fwd
from ecomd.models.bptt_step_function import EcoMDStepFunction


def test_amp_compat_decorators_preserve_callables() -> None:
    def forward(value: int) -> int:
        return value + 1

    def backward(value: int) -> int:
        return value - 1

    assert callable(cuda_custom_fwd(forward))
    assert callable(cuda_custom_bwd(backward))
    assert callable(EcoMDStepFunction.forward)
    assert callable(EcoMDStepFunction.backward)
