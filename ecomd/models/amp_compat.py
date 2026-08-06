"""Compatibility decorators for PyTorch 2.3 and newer AMP APIs."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar, cast

import torch

FunctionT = TypeVar("FunctionT", bound=Callable[..., Any])


def cuda_custom_fwd(function: FunctionT) -> FunctionT:
    modern = getattr(torch.amp, "custom_fwd", None)
    if modern is not None:
        return cast(FunctionT, modern(device_type="cuda")(function))
    return cast(FunctionT, torch.cuda.amp.custom_fwd(function))


def cuda_custom_bwd(function: FunctionT) -> FunctionT:
    modern = getattr(torch.amp, "custom_bwd", None)
    if modern is not None:
        return cast(FunctionT, modern(device_type="cuda")(function))
    return cast(FunctionT, torch.cuda.amp.custom_bwd(function))
