"""Recurrent surrogate with fixed units fitted on its training partition."""
from __future__ import annotations
from dataclasses import replace
from typing import cast

import torch
from torch import Tensor, nn

from ecomd.models.fact_surrogate import (
    FactSurrogateBatch, FactSurrogateConfig, FactSurrogateOutput,
    MechanismEstimator, RecurrentFactSurrogate,
)


def fit_training_units(batches: list[FactSurrogateBatch]) -> dict[str, Tensor]:
    """Fit once on declared training batches; callers must verify split provenance."""
    if not batches:
        raise ValueError("training batches are required")
    features, absolute, increments = [], [], []
    for batch in batches:
        x = batch.features.detach().cpu().double().flatten(0, 1)
        y = batch.channels.detach().cpu().double()
        base = (torch.zeros_like(y[:, :1]) if batch.channels_init is None
                else batch.channels_init.detach().cpu().double().unsqueeze(1))
        delta = y - torch.cat((base, y[:, :-1]), dim=1)
        if (not torch.isfinite(x).all() or not torch.isfinite(y).all()
                or not torch.isfinite(delta).all() or (delta < 0).any()):
            raise ValueError("nonfinite inputs or nonmonotone conserving channels")
        if x.shape[0] != y.shape[0] * y.shape[1]:
            raise ValueError("feature/channel round mismatch")
        features.append(x)
        absolute.append(y.flatten(0, 1))
        increments.append(delta.flatten(0, 1))
    x, y, delta = map(torch.cat, (features, absolute, increments))
    units = {
        "feature_center": x.mean(0), "feature_scale": x.std(0, unbiased=False).clamp_min(1),
        "absolute_center": y.mean(0), "absolute_scale": y.std(0, unbiased=False).clamp_min(1),
        "increment_center": delta.mean(0), "increment_scale": delta.std(0, unbiased=False).clamp_min(1),
        "volume_mean": delta[:, 0].mean().clamp_min(1),
        "volume_max": delta[:, 0].max().clamp_min(1),
    }
    return {key: value.float() for key, value in units.items()}


class _UnitHead(nn.Module):
    def __init__(self, head: nn.Linear, scale: Tensor, center: Tensor) -> None:
        super().__init__()
        if not torch.isfinite(scale).all() or not (scale > 0).all():
            raise ValueError("head scales must be finite and positive")
        if not torch.isfinite(center).all():
            raise ValueError("head centers must be finite")
        self.head = head
        self.register_buffer("scale", scale.clone())
        self.register_buffer("center", center.clone())

    @property
    def weight(self) -> Tensor:
        return self.head.weight

    @property
    def bias(self) -> Tensor | None:
        return self.head.bias

    def forward(self, hidden: Tensor) -> Tensor:
        return cast(Tensor, self.center + self.scale * self.head(hidden))


class UnitRecurrentFactSurrogate(RecurrentFactSurrogate):
    """Original recurrent forward with fixed training-only affine units."""
    def __init__(self, config: FactSurrogateConfig, units: dict[str, Tensor],
                 *, generator: torch.Generator) -> None:
        super().__init__(config, generator=generator)
        for name in ("feature_center", "feature_scale"):
            value = units[name]
            if value.shape != (self.cell.input_size,) or not torch.isfinite(value).all():
                raise ValueError(f"invalid {name}")
            if name == "feature_scale" and not (value > 0).all():
                raise ValueError("feature scales must be positive")
            self.register_buffer(name, value.clone())
        for name in ("absolute", "increment"):
            for suffix in ("center", "scale"):
                if units[f"{name}_{suffix}"].shape != (config.n_channels,):
                    raise ValueError(f"invalid {name}_{suffix}")
        self.abs_head = _UnitHead(self.abs_head, units["absolute_scale"], units["absolute_center"])  # type: ignore[assignment]
        self.inc_head = _UnitHead(self.inc_head, units["increment_scale"], units["increment_center"])  # type: ignore[assignment]
        flow_unit = (units["volume_mean"] / config.n_slots).clamp_min(1)
        demand_unit = units["volume_max"]
        for name, unit in (("flow_head", flow_unit), ("demand_head", demand_unit)):
            if unit.ndim != 0 or not torch.isfinite(unit) or unit < 1:
                raise ValueError(f"invalid {name} unit")
            # softplus(center) equals the training-derived physical unit.
            center = unit + torch.log(-torch.expm1(-unit))
            setattr(self, name, _UnitHead(getattr(self, name), demand_unit, center))

    def forward(self, batch: FactSurrogateBatch, *,
                mechanism: MechanismEstimator | None = None) -> FactSurrogateOutput:
        normalized = (batch.features - self.feature_center) / self.feature_scale
        return super().forward(replace(batch, features=normalized), mechanism=mechanism)
