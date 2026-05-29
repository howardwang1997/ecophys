"""Conditional diffusion (DDPM) baseline for autoregressive returns — exp 111.

The deep-generative paradigm leg of the three-paradigm ceiling map. Directly
learns the return distribution, so it can place the tail index (hill #2) inside
[2,4] where the mechanistic EcoMD overshoots to α<2 (exp 108 diagnosis).

Design (conditional autoregressive DDPM, recommended over a pure 1D marginal):
the denoiser ε_θ(r_noisy, t, context) is conditioned on a window of the past K
returns [r,|r|] (same context idea as trajcast_lite), so it has a shot at the
TEMPORAL facts (acf² #6, DFA #8, leverage #9, zumbach #11) too — a pure marginal
sampler would ace tails but fail every dynamics fact. `conditional=False` recovers
the marginal sampler as a one-line paper ablation.

Sklearn-style API matching wgan_lp / trajcast_lite (so scripts/run_baseline_fit_eval.py
and score_phase.py work unchanged):
    model = ScoreDiffusionSimulator(context=64, n_diffusion_steps=50)
    model.fit(returns, n_epochs=200)
    synth = model.sample(n_steps=2520, seed=0)
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn


def _sinusoidal_embed(t: torch.Tensor, dim: int) -> torch.Tensor:
    """t: (B,) in [0,1] → (B, dim) sinusoidal embedding."""
    half = dim // 2
    freqs = torch.exp(
        -np.log(10000.0) * torch.arange(half, device=t.device, dtype=t.dtype) / max(half - 1, 1)
    )
    ang = t[:, None] * freqs[None, :] * 1000.0
    return torch.cat([torch.sin(ang), torch.cos(ang)], dim=-1)


class _Denoiser(nn.Module):
    """ε_θ(x_t, t, context) — predicts the noise added to the standardized next
    return x_0, conditioned on a context window and the diffusion timestep."""

    def __init__(self, context: int, hidden: int, t_embed: int, conditional: bool) -> None:
        super().__init__()
        self.conditional = conditional
        self.t_embed = t_embed
        if conditional:
            # Encode the (context, 2) window [r, |r|] → cond vector.
            self.ctx_enc = nn.Sequential(
                nn.Linear(context * 2, hidden), nn.SiLU(), nn.Linear(hidden, hidden)
            )
            cond_dim = hidden
        else:
            self.ctx_enc = None
            cond_dim = 0
        self.net = nn.Sequential(
            nn.Linear(1 + t_embed + cond_dim, hidden), nn.SiLU(),
            nn.Linear(hidden, hidden), nn.SiLU(),
            nn.Linear(hidden, 1),
        )

    def forward(self, x_t: torch.Tensor, t_frac: torch.Tensor, ctx: torch.Tensor) -> torch.Tensor:
        # x_t: (B,1); t_frac: (B,); ctx: (B, context, 2)
        te = _sinusoidal_embed(t_frac, self.t_embed)
        parts = [x_t, te]
        if self.conditional and self.ctx_enc is not None:
            parts.append(self.ctx_enc(ctx.reshape(ctx.size(0), -1)))
        return self.net(torch.cat(parts, dim=-1))


class ScoreDiffusionSimulator:
    """Conditional DDPM over standardized log-returns, sampled autoregressively."""

    def __init__(
        self,
        context: int = 64,
        hidden: int = 128,
        n_diffusion_steps: int = 50,
        t_embed: int = 16,
        conditional: bool = True,
        beta_start: float = 1e-4,
        beta_end: float = 2e-2,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ) -> None:
        self.context = context
        self.conditional = conditional
        self.T = n_diffusion_steps
        self.device = torch.device(device)
        self.net = _Denoiser(context, hidden, t_embed, conditional).to(self.device)
        betas = torch.linspace(beta_start, beta_end, self.T, device=self.device)
        self.betas = betas
        self.alphas = 1.0 - betas
        self.alpha_bar = torch.cumprod(self.alphas, dim=0)
        self._mean: float = 0.0
        self._std: float = 1.0

    def fit(
        self,
        returns: np.ndarray,
        n_epochs: int = 200,
        batch_size: int = 256,
        lr: float = 3e-4,
        seed: int = 0,
    ) -> "ScoreDiffusionSimulator":
        r = np.asarray(returns, dtype=np.float32).ravel()
        if r.size < self.context * 4:
            raise ValueError(f"need ≥ {self.context * 4} returns, got {r.size}")
        self._mean = float(r.mean())
        self._std = float(r.std() + 1e-12)
        rs = (r - self._mean) / self._std
        n_pairs = rs.size - self.context
        X = np.empty((n_pairs, self.context, 2), dtype=np.float32)
        Y = np.empty((n_pairs, 1), dtype=np.float32)
        for i in range(n_pairs):
            w = rs[i : i + self.context]
            X[i, :, 0] = w
            X[i, :, 1] = np.abs(w)
            Y[i, 0] = rs[i + self.context]
        X_t = torch.from_numpy(X).to(self.device)
        Y_t = torch.from_numpy(Y).to(self.device)

        torch.manual_seed(seed)
        opt = torch.optim.AdamW(self.net.parameters(), lr=lr, weight_decay=1e-4)
        self.net.train()
        for _ in range(n_epochs):
            perm = torch.randperm(X_t.size(0), device=self.device)
            for i in range(0, X_t.size(0), batch_size):
                idx = perm[i : i + batch_size]
                x0 = Y_t[idx]                              # (B,1)
                ctx = X_t[idx]                             # (B,context,2)
                B = x0.size(0)
                t = torch.randint(0, self.T, (B,), device=self.device)
                ab = self.alpha_bar[t].unsqueeze(-1)       # (B,1)
                eps = torch.randn_like(x0)
                x_t = torch.sqrt(ab) * x0 + torch.sqrt(1.0 - ab) * eps
                eps_pred = self.net(x_t, t.float() / self.T, ctx)
                loss = ((eps_pred - eps) ** 2).mean()
                opt.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.net.parameters(), 1.0)
                opt.step()
        return self

    @torch.no_grad()
    def _sample_one(self, ctx: torch.Tensor, gen: torch.Generator) -> float:
        """One reverse-diffusion sample of the next standardized return given ctx (1,context,2)."""
        x = torch.randn(1, 1, generator=gen, device=self.device)
        for t in reversed(range(self.T)):
            t_frac = torch.full((1,), t / self.T, device=self.device)
            eps = self.net(x, t_frac, ctx)
            alpha = self.alphas[t]
            ab = self.alpha_bar[t]
            coef = (1.0 - alpha) / torch.sqrt(1.0 - ab)
            mean = (x - coef * eps) / torch.sqrt(alpha)
            if t > 0:
                z = torch.randn(1, 1, generator=gen, device=self.device)
                x = mean + torch.sqrt(self.betas[t]) * z
            else:
                x = mean
        return float(x.item())

    @torch.no_grad()
    def sample(self, n_steps: int, seed: int = 0) -> np.ndarray:
        self.net.eval()
        gen = torch.Generator(device=self.device).manual_seed(seed)
        ctx = (torch.randn(1, self.context, 2, generator=gen, device=self.device) * 0.5)
        if not self.conditional:
            ctx = torch.zeros_like(ctx)  # marginal ablation: denoiser ignores it anyway
        out = np.empty(n_steps, dtype=np.float32)
        for i in range(n_steps):
            r_new = self._sample_one(ctx, gen)
            out[i] = r_new
            if self.conditional:
                ctx = torch.roll(ctx, -1, dims=1)
                ctx[0, -1, 0] = r_new
                ctx[0, -1, 1] = abs(r_new)
        return out * self._std + self._mean


__all__ = ["ScoreDiffusionSimulator"]
