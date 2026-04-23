"""GARCH(1,1) simulator — classical econometric baseline.

Bollerslev (1986) GARCH(1,1):
    r_t     = σ_t · z_t,        z_t ~ iid (Normal or Student-t)
    σ_t²    = ω + α · r_{t-1}² + β · σ_{t-1}²

Two usage modes:

  1. Ad-hoc parameters  — `GARCH11(omega=1e-6, alpha=0.08, beta=0.90)`
     Canonical "pure GARCH" simulator for stylized-facts benchmarking
     independent of any particular asset.

  2. Fit from data      — `GARCH11.fit(returns, dist='t')`
     Uses the `arch` package to fit GARCH(1,1) to real returns, then
     samples synthetic trajectories from the fitted model.

The simulator returns 1-D log returns (not prices). Use `np.cumsum`
if you need a price path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import numpy.typing as npt

ArrayF = npt.NDArray[np.float64]


@dataclass
class GARCH11Params:
    omega: float
    alpha: float
    beta: float
    dist: Literal["normal", "t"] = "normal"
    nu: float | None = None   # degrees of freedom for Student-t; required if dist='t'
    mean: float = 0.0         # constant mean (usually 0 for demeaned returns)
    scale: float = 1.0        # multiplier if data was rescaled before fit (e.g. 100×)

    def __post_init__(self) -> None:
        if self.omega <= 0:
            raise ValueError("omega must be > 0")
        if self.alpha < 0 or self.beta < 0:
            raise ValueError("alpha, beta must be ≥ 0")
        if self.alpha + self.beta >= 1.0:
            raise ValueError(f"alpha+beta={self.alpha + self.beta} must be < 1 for stationarity")
        if self.dist == "t" and (self.nu is None or self.nu <= 2):
            raise ValueError("Student-t dist requires nu > 2")

    def unconditional_variance(self) -> float:
        return self.omega / (1.0 - self.alpha - self.beta)


class GARCH11:
    """GARCH(1,1) simulator."""

    def __init__(self, omega: float, alpha: float, beta: float,
                 dist: Literal["normal", "t"] = "normal",
                 nu: float | None = None,
                 mean: float = 0.0,
                 scale: float = 1.0) -> None:
        self.params = GARCH11Params(omega=omega, alpha=alpha, beta=beta,
                                    dist=dist, nu=nu, mean=mean, scale=scale)

    # ── Fit from data ───────────────────────────────────────────────────

    @classmethod
    def fit(cls, returns: ArrayF, dist: Literal["normal", "t"] = "t",
            rescale_to_percent: bool = True) -> "GARCH11":
        """Fit GARCH(1,1) with the `arch` package. Returns a simulator loaded
        with the fitted parameters.

        `rescale_to_percent=True` multiplies input by 100 before fit (recommended
        for log returns) to avoid numerical warnings and rescaling side-effects.
        The simulator remembers the scale and de-scales when sampling.
        """
        from arch import arch_model
        r = np.asarray(returns, dtype=np.float64)
        r = r[np.isfinite(r)]
        if r.size < 100:
            raise ValueError(f"need at least 100 observations to fit GARCH(1,1); got {r.size}")
        scale = 100.0 if rescale_to_percent else 1.0
        distribution = "t" if dist == "t" else "normal"
        model = arch_model(r * scale, vol="GARCH", p=1, q=1,
                           mean="Constant", dist=distribution, rescale=False)
        res = model.fit(disp="off", show_warning=False)
        params = res.params
        omega = float(params["omega"])
        alpha = float(params["alpha[1]"])
        beta = float(params["beta[1]"])
        mu = float(params.get("mu", 0.0))
        nu = float(params["nu"]) if distribution == "t" else None
        return cls(omega=omega, alpha=alpha, beta=beta,
                   dist=dist, nu=nu, mean=mu, scale=scale)

    # ── Simulate ───────────────────────────────────────────────────────

    def simulate(self, n_steps: int, seed: int | None = None,
                 burn_in: int = 500) -> ArrayF:
        """Generate `n_steps` log returns. `burn_in` discarded upfront."""
        p = self.params
        rng = np.random.default_rng(seed)

        n_total = n_steps + burn_in
        sigma2 = np.empty(n_total, dtype=np.float64)
        r_scaled = np.empty(n_total, dtype=np.float64)

        # Initial variance = unconditional
        sigma2[0] = p.unconditional_variance()
        r_scaled[0] = np.sqrt(sigma2[0]) * self._sample_innov(rng, 1)[0]

        for t in range(1, n_total):
            sigma2[t] = p.omega + p.alpha * r_scaled[t - 1] ** 2 + p.beta * sigma2[t - 1]
            r_scaled[t] = np.sqrt(sigma2[t]) * self._sample_innov(rng, 1)[0]

        # Add mean, de-rescale to original units
        r = (r_scaled + p.mean) / p.scale
        return r[burn_in:]

    def _sample_innov(self, rng: np.random.Generator, n: int) -> ArrayF:
        p = self.params
        if p.dist == "normal":
            return rng.standard_normal(n)
        elif p.dist == "t":
            # Unit-variance Student-t: divide samples by sqrt(nu/(nu-2))
            assert p.nu is not None
            raw = rng.standard_t(df=p.nu, size=n)
            return raw / np.sqrt(p.nu / (p.nu - 2.0))
        raise AssertionError(p.dist)

    # ── Utilities ──────────────────────────────────────────────────────

    def __repr__(self) -> str:
        p = self.params
        base = f"GARCH11(ω={p.omega:.3e}, α={p.alpha:.3f}, β={p.beta:.3f}, dist={p.dist}"
        if p.dist == "t":
            base += f", ν={p.nu:.2f}"
        return base + f", μ={p.mean:.2e}, scale={p.scale}, α+β={p.alpha + p.beta:.3f})"
