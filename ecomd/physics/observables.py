"""Trajectory recording for EcoMD.

``EcoMDTrajectory`` stores every quantity Phase 4 will need:
- conservative / dissipative / stochastic forces, separately
- velocities (finite difference v_t = (s_{t+1} - s_t)/dt)
- states, prices, log returns, volume, excess-demand

The per-step recorder ``TrajectoryRecorder`` accumulates these as lists and
stacks them on ``finalize()``. This is intentionally simple — for larger
runs (N=10^5 on H20) we'll swap to a ring buffer + on-disk chunks, but v0
fits in memory.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt
import torch
from torch import Tensor

ArrayF = npt.NDArray[np.float64]


@dataclass
class EcoMDTrajectory:
    """Immutable snapshot of a simulation run.

    Shapes (T = number of recorded steps):
    - states, f_cons, f_diss, f_stoch, velocities: (T, N, d)
    - log_prices: (T,)
    - log_returns: (T,) — includes step 0 which is 0 by convention
    - volumes, excess_demand: (T,)
    """

    states: Tensor
    f_cons: Tensor
    f_diss: Tensor
    f_stoch: Tensor
    velocities: Tensor
    log_prices: Tensor
    log_returns: Tensor
    volumes: Tensor
    excess_demand: Tensor
    dt: float
    meta: dict[str, float | int | str] = field(default_factory=dict)

    @property
    def n_steps(self) -> int:
        return self.states.shape[0]

    @property
    def n_agents(self) -> int:
        return self.states.shape[1]

    @property
    def d_state(self) -> int:
        return self.states.shape[2]

    def log_returns_np(self) -> ArrayF:
        return self.log_returns.detach().cpu().numpy().astype(np.float64)

    def volumes_np(self) -> ArrayF:
        return self.volumes.detach().cpu().numpy().astype(np.float64)

    def to(self, device: torch.device | str) -> EcoMDTrajectory:
        return EcoMDTrajectory(
            states=self.states.to(device),
            f_cons=self.f_cons.to(device),
            f_diss=self.f_diss.to(device),
            f_stoch=self.f_stoch.to(device),
            velocities=self.velocities.to(device),
            log_prices=self.log_prices.to(device),
            log_returns=self.log_returns.to(device),
            volumes=self.volumes.to(device),
            excess_demand=self.excess_demand.to(device),
            dt=self.dt,
            meta=dict(self.meta),
        )

    def detach(self) -> EcoMDTrajectory:
        return EcoMDTrajectory(
            states=self.states.detach(),
            f_cons=self.f_cons.detach(),
            f_diss=self.f_diss.detach(),
            f_stoch=self.f_stoch.detach(),
            velocities=self.velocities.detach(),
            log_prices=self.log_prices.detach(),
            log_returns=self.log_returns.detach(),
            volumes=self.volumes.detach(),
            excess_demand=self.excess_demand.detach(),
            dt=self.dt,
            meta=dict(self.meta),
        )


class TrajectoryRecorder:
    """Append per-step tensors; build an :class:`EcoMDTrajectory` at the end."""

    def __init__(self, dt: float, meta: dict[str, float | int | str] | None = None) -> None:
        self.dt = dt
        self.meta = meta or {}
        self._states: list[Tensor] = []
        self._f_cons: list[Tensor] = []
        self._f_diss: list[Tensor] = []
        self._f_stoch: list[Tensor] = []
        self._velocities: list[Tensor] = []
        self._log_prices: list[Tensor] = []
        self._log_returns: list[Tensor] = []
        self._volumes: list[Tensor] = []
        self._excess_demand: list[Tensor] = []

    def record(
        self,
        s: Tensor,
        f_cons: Tensor,
        f_diss: Tensor,
        f_stoch: Tensor,
        velocity: Tensor,
        log_price: Tensor,
        log_return: Tensor,
        volume: Tensor,
        excess_demand: Tensor,
    ) -> None:
        self._states.append(s)
        self._f_cons.append(f_cons)
        self._f_diss.append(f_diss)
        self._f_stoch.append(f_stoch)
        self._velocities.append(velocity)
        self._log_prices.append(log_price)
        self._log_returns.append(log_return)
        self._volumes.append(volume)
        self._excess_demand.append(excess_demand)

    def finalize(self) -> EcoMDTrajectory:
        if not self._states:
            raise RuntimeError("recorder is empty; call record() at least once")
        return EcoMDTrajectory(
            states=torch.stack(self._states),
            f_cons=torch.stack(self._f_cons),
            f_diss=torch.stack(self._f_diss),
            f_stoch=torch.stack(self._f_stoch),
            velocities=torch.stack(self._velocities),
            log_prices=torch.stack(self._log_prices),
            log_returns=torch.stack(self._log_returns),
            volumes=torch.stack(self._volumes),
            excess_demand=torch.stack(self._excess_demand),
            dt=self.dt,
            meta=self.meta,
        )
