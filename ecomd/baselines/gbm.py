"""Geometric Brownian motion — null baseline.

Simplest possible price model: r_t ~ iid N(μ, σ²). Reproduces NONE of the
non-trivial Cont-2001 stylized facts (no volatility clustering, no fat
tails beyond Gaussian, no leverage, no zumbach). Used as the "no-physics"
floor on the baseline comparison table.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass
class GBMParams:
    mu: float = 0.0
    sigma: float = 0.01

    def __post_init__(self) -> None:
        if self.sigma <= 0:
            raise ValueError("sigma must be > 0")


class GBM:
    """Geometric Brownian motion. ``simulate(n)`` returns ``n`` log returns."""

    def __init__(self, mu: float = 0.0, sigma: float = 0.01) -> None:
        self.params = GBMParams(mu=mu, sigma=sigma)

    @classmethod
    def fit(cls, returns: npt.NDArray[np.float64]) -> "GBM":
        r = np.asarray(returns, dtype=np.float64)
        r = r[np.isfinite(r)]
        if r.size < 50:
            raise ValueError(f"need at least 50 observations to fit GBM; got {r.size}")
        return cls(mu=float(r.mean()), sigma=float(r.std(ddof=1)))

    def simulate(self, n_steps: int, seed: int | None = None) -> npt.NDArray[np.float64]:
        rng = np.random.default_rng(seed)
        return self.params.mu + self.params.sigma * rng.standard_normal(n_steps)
