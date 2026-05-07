"""AR(1) + stochastic-volatility baseline.

A step up from GBM: returns have first-order autocorrelation (which is
the AR(1) drift artifact ECoMD v3 itself exhibits — useful as a sanity
check) and log-variance follows its own AR(1) process (a discrete
analogue of the continuous-time SV model of Heston 1993).

    r_t       = μ + ρ · r_{t-1} + σ_t · ε_t,        ε_t ~ N(0, 1)
    log σ_t²  = α + φ · log σ_{t-1}² + ν · η_t,     η_t ~ N(0, 1)

Reproduces volatility clustering (acf_squared_returns) more faithfully
than GBM but lacks heavy tails (returns are conditionally Gaussian) and
leverage (no Δp → σ feedback). Therefore expected to fail
hill_tail_index, leverage_effect, zumbach_asymmetry — the same three
facts that v3 struggles with.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass
class AR1SVParams:
    mu: float = 0.0
    rho: float = 0.0       # AR(1) coefficient on returns; |ρ|<1
    alpha: float = -10.0   # log-variance intercept; ⟨log σ²⟩ ≈ α / (1 - φ)
    phi: float = 0.95      # AR(1) on log-variance; |φ|<1
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
    def fit(cls, returns: npt.NDArray[np.float64]) -> "AR1SV":
        """Quasi-MLE fit. ρ from sample autocorr; SV params from log r² regression.

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

    def simulate(self, n_steps: int, seed: int | None = None,
                 burn_in: int = 500) -> npt.NDArray[np.float64]:
        p = self.params
        rng = np.random.default_rng(seed)
        n = n_steps + burn_in
        r = np.zeros(n)
        log_v = np.full(n, p.alpha / max(1.0 - p.phi, 1e-3))
        for t in range(1, n):
            log_v[t] = p.alpha + p.phi * log_v[t - 1] + p.nu * rng.standard_normal()
            sigma_t = float(np.exp(0.5 * log_v[t]))
            r[t] = p.mu + p.rho * (r[t - 1] - p.mu) + sigma_t * rng.standard_normal()
        return r[burn_in:]
