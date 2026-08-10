"""VaR sampler implementations: Historical, GARCH, ECoMD.

Each sampler follows the protocol expected by ``rolling_backtest``:
    sample(past_returns: np.ndarray, horizon: int, n_paths: int, seed: int)
        → np.ndarray of shape (n_paths, horizon)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, cast

import numpy as np

if TYPE_CHECKING:
    from ecomd.baselines.garch import GARCH11
    from ecomd.models.ecomd import EcoMDSimulator


class HistoricalSampler:
    """Bootstrap from the most recent ``window`` returns (Historical Simulation).

    Standard non-parametric VaR baseline. Captures empirical fat tails but
    has no time dynamics — the sampled paths are iid draws from the past
    window's empirical distribution.
    """

    def __init__(self, window: int = 250) -> None:
        if window < 50:
            raise ValueError(f"window must be ≥ 50, got {window}")
        self.window = window

    def sample(self, past: np.ndarray, horizon: int, n_paths: int, seed: int = 0) -> np.ndarray:
        past = np.asarray(past, dtype=np.float64).ravel()
        if past.size < self.window:
            raise ValueError(f"need ≥ {self.window} past returns, got {past.size}")
        recent = past[-self.window:]
        rng = np.random.default_rng(seed)
        return rng.choice(recent, size=(n_paths, horizon), replace=True)


class GARCHSampler:
    """GARCH(1,1)-conditional VaR sampler.

    Two modes:
      - ``refit_every == 0``: fit GARCH(1,1) once on the first window and
        reuse parameters across the whole backtest. Fast, common in
        practice (analogous to "rolling-window GARCH" with a static fit).
      - ``refit_every > 0``: refit every k backtest steps. More accurate
        but ~10× slower.

    Either way, at each backtest call we use the model's filtered
    conditional variance at time T (end of past_returns) as the projection
    starting point, then run forward for ``horizon`` steps.
    """

    def __init__(self,
                 dist: str = "t",
                 fit_window: int = 1000,
                 refit_every: int = 0) -> None:
        if dist not in ("normal", "t"):
            raise ValueError(f"dist must be 'normal' or 't', got {dist!r}")
        if fit_window < 100:
            raise ValueError(f"fit_window must be ≥ 100, got {fit_window}")
        self.dist = cast(Literal["normal", "t"], dist)
        self.fit_window = fit_window
        self.refit_every = int(refit_every)
        self._model: GARCH11 | None = None
        self._step_counter: int = 0
        self._n_calls: int = 0

    def _maybe_refit(self, past: np.ndarray) -> None:
        from ecomd.baselines.garch import GARCH11
        if self._model is None:
            window = past[-self.fit_window:] if past.size >= self.fit_window else past
            self._model = GARCH11.fit(window, dist=self.dist, rescale_to_percent=True)
            self._step_counter = 0
            return
        if self.refit_every > 0 and self._step_counter % self.refit_every == 0:
            window = past[-self.fit_window:] if past.size >= self.fit_window else past
            self._model = GARCH11.fit(window, dist=self.dist, rescale_to_percent=True)
        self._step_counter += 1

    def sample(self, past: np.ndarray, horizon: int, n_paths: int, seed: int = 0) -> np.ndarray:
        past = np.asarray(past, dtype=np.float64).ravel()
        self._maybe_refit(past)
        m = self._model
        assert m is not None
        p = m.params
        # Filter through past returns to get current sigma² at end of `past`.
        # (rescale_to_percent=True means the fitted model expects 100×returns)
        scale = p.scale
        r_sc = past * scale
        n = r_sc.size
        sigma2 = np.empty(n)
        sigma2[0] = p.unconditional_variance()
        for t in range(1, n):
            sigma2[t] = p.omega + p.alpha * r_sc[t - 1] ** 2 + p.beta * sigma2[t - 1]
        sigma2_t = float(sigma2[-1])
        last_r2 = float(r_sc[-1] ** 2)

        # Project n_paths × horizon steps forward
        rng = np.random.default_rng(seed)
        if p.dist == "normal":
            innov = rng.standard_normal((n_paths, horizon))
        else:
            assert p.nu is not None
            innov = rng.standard_t(df=p.nu, size=(n_paths, horizon)) / np.sqrt(p.nu / (p.nu - 2.0))

        out = np.empty((n_paths, horizon))
        sigma2_path = np.full(n_paths, sigma2_t)
        last_r2_path = np.full(n_paths, last_r2)
        for h in range(horizon):
            sigma2_path = p.omega + p.alpha * last_r2_path + p.beta * sigma2_path
            r_h_sc = np.sqrt(sigma2_path) * innov[:, h] + p.mean
            out[:, h] = r_h_sc / scale
            last_r2_path = r_h_sc ** 2
        return out


class EcoMDSampler:
    """Sample paths from a trained ECoMD checkpoint.

    Loads the checkpoint once (lazy), then on each call runs ``n_paths``
    independent rollouts of length ``horizon`` from random initial states
    with seed offsetting. Returns the per-step log returns.

    Note: v3 ECoMD does not natively *condition* on past returns —
    each sample is an unconditional draw from the trained generative
    distribution. This is a known limitation and is reported in the paper
    as a Future Work item (conditional generation via warm-start agent
    state).

    For now the past_returns argument is IGNORED but kept in the signature
    for compatibility with the Sampler protocol.
    """

    def __init__(self,
                 checkpoint_path: str | Path,
                 config_path: str | Path,
                 device: str = "cpu") -> None:
        self.checkpoint_path = Path(checkpoint_path)
        self.config_path = Path(config_path)
        self.device = device
        self._sim: EcoMDSimulator | None = None

    def _load(self) -> None:
        if self._sim is not None:
            return
        import yaml
        import torch
        from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
        cfg_dict = yaml.safe_load(self.config_path.read_text())
        sim_keys = EcoMDConfig.__dataclass_fields__.keys()
        sim_cfg = {k: v for k, v in cfg_dict["simulator"].items() if k in sim_keys}
        sim = EcoMDSimulator(EcoMDConfig(**sim_cfg))
        ckpt = torch.load(self.checkpoint_path, map_location=self.device)
        # Checkpoint format compatibility: try several common keys
        state = ckpt.get("model_state_dict") or ckpt.get("state_dict") or ckpt
        sim.load_state_dict(state, strict=False)
        sim.to(self.device).eval()
        self._sim = sim

    def sample(self, past: np.ndarray, horizon: int, n_paths: int, seed: int = 0) -> np.ndarray:
        import torch
        self._load()
        sim = self._sim
        assert sim is not None
        # Burn in long enough that "initial transient" doesn't bias VaR;
        # use `horizon` itself as a minimum, plus 50 steps of buffer.
        burn = max(50, horizon)
        out = np.empty((n_paths, horizon))
        with torch.no_grad():
            for k in range(n_paths):
                traj = sim.run(n_steps=burn + horizon, seed=seed + k)
                r = traj.log_returns_np()[1:]  # discard initial NaN
                # Take the LAST `horizon` steps so we sample post-burn.
                out[k] = r[-horizon:]
        return out
