"""AR(1) + stochastic-volatility baseline.

A step up from GBM: returns have first-order autocorrelation (which is
the AR(1) drift artifact ECoMD v3 itself exhibits — useful as a sanity
check) and log-variance follows its own AR(1) process (a discrete
analogue of the continuous-time SV model of Heston 1993).

    r_t       = mu + rho * r_{t-1} + sigma_t * epsilon_t
    log sigma_t^2 = alpha + phi * log sigma_{t-1}^2 + nu * eta_t

Reproduces volatility clustering (acf_squared_returns) more faithfully
than GBM but lacks heavy tails (returns are conditionally Gaussian) and
leverage (no return-to-volatility feedback). Therefore expected to fail
hill_tail_index, leverage_effect, zumbach_asymmetry — the same three
facts that v3 struggles with.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

import numpy as np
import numpy.typing as npt

ArrayF: TypeAlias = npt.NDArray[np.float64]


@dataclass
class AR1SVParams:
    mu: float = 0.0
    rho: float = 0.0       # AR(1) coefficient on returns; absolute value below 1
    alpha: float = -10.0   # log-variance intercept; long-run mean = alpha / (1 - phi)
    phi: float = 0.95      # AR(1) on log-variance; in [0, 1)
    nu: float = 0.3        # log-variance innovation std

    def __post_init__(self) -> None:
        if not -1.0 < self.rho < 1.0:
            raise ValueError(f"|rho|<1 required; got {self.rho}")
        if not 0.0 <= self.phi < 1.0:
            raise ValueError(f"phi in [0, 1) required; got {self.phi}")
        if self.nu <= 0:
            raise ValueError(f"nu>0 required; got {self.nu}")


class AR1SV:
    def __init__(self, mu: float = 0.0, rho: float = 0.0,
                 alpha: float = -10.0, phi: float = 0.95, nu: float = 0.3) -> None:
        self.params = AR1SVParams(mu=mu, rho=rho, alpha=alpha, phi=phi, nu=nu)

    @classmethod
    def fit(cls, returns: ArrayF) -> AR1SV:
        """Quasi-MLE fit: rho from sample autocorrelation and SV from log squared returns.

        This is intentionally lightweight (no full state-space EM) so the
        baseline is fast and reproducible. For Paper A we report this as
        a "moment-matched SV" rather than full SV-MLE.
        """
        r = np.asarray(returns, dtype=np.float64)
        r = r[np.isfinite(r)]
        if r.size < 200:
            raise ValueError(f"need at least 200 observations to fit AR(1)+SV; got {r.size}")
        mu = float(r.mean())
        r_demeaned = r - mu
        rho_hat = float(np.corrcoef(r_demeaned[:-1], r_demeaned[1:])[0, 1])
        rho_hat = float(np.clip(rho_hat, -0.95, 0.95))
        # SV: regress log(r²+ε) on its own lag.
        eps = 1e-10
        log_r2 = np.log(r_demeaned ** 2 + eps)
        x = log_r2[:-1] - log_r2[:-1].mean()
        y = log_r2[1:] - log_r2[1:].mean()
        denom = float((x * x).sum())
        phi_hat = float(np.clip((x * y).sum() / max(denom, eps), 0.0, 0.99))
        residuals = log_r2[1:] - phi_hat * log_r2[:-1]
        alpha_hat = float(residuals.mean())
        nu_hat = float(max(residuals.std(ddof=1), 1e-3))
        return cls(mu=mu, rho=rho_hat, alpha=alpha_hat, phi=phi_hat, nu=nu_hat)

    def simulate(
        self,
        n_steps: int,
        seed: int | None = None,
        burn_in: int = 500,
        initial_variance_multiplier: float = 1.0,
    ) -> ArrayF:
        """Generate returns after an optional burn-in.

        The initial log variance is sampled from its stationary Gaussian law.
        ``initial_variance_multiplier`` then shifts that variance by a fixed
        factor, enabling pre-specified cold-start controls.
        """
        if n_steps < 1:
            raise ValueError("n_steps must be positive")
        if burn_in < 0:
            raise ValueError("burn_in must be nonnegative")
        if not np.isfinite(initial_variance_multiplier) or initial_variance_multiplier <= 0.0:
            raise ValueError("initial_variance_multiplier must be finite and positive")
        p = self.params
        rng = np.random.default_rng(seed)
        n = n_steps + burn_in
        r: ArrayF = np.empty(n, dtype=np.float64)
        log_v: ArrayF = np.empty(n, dtype=np.float64)
        stationary_log_v_mean = p.alpha / (1.0 - p.phi)
        stationary_log_v_std = p.nu / np.sqrt(1.0 - p.phi ** 2)
        log_v[0] = (
            stationary_log_v_mean
            + stationary_log_v_std * rng.standard_normal()
            + np.log(initial_variance_multiplier)
        )
        initial_return_std = np.exp(0.5 * log_v[0]) / np.sqrt(1.0 - p.rho ** 2)
        r[0] = p.mu + initial_return_std * rng.standard_normal()
        for t in range(1, n):
            log_v[t] = p.alpha + p.phi * log_v[t - 1] + p.nu * rng.standard_normal()
            sigma_t = float(np.exp(0.5 * log_v[t]))
            r[t] = p.mu + p.rho * (r[t - 1] - p.mu) + sigma_t * rng.standard_normal()
        return r[burn_in:]
