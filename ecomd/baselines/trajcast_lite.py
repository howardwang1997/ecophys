"""TrajCast-lite baseline (Thiemann et al. 2025-inspired) for autoregressive returns.

A minimal stand-in for the autoregressive-equivariant TrajCast model.
The full TrajCast is a 3D-equivariant GNN for atomic systems; for
financial returns the relevant symmetry is permutation over agents
(which collapses to a no-op when we operate on aggregate market state),
so this baseline is a 1D autoregressive transformer over the past K
returns + volatility proxy.

Architecture: K-step context → 2-layer transformer encoder → linear head
producing (μ, log σ) of the next-step return. Sampling rolls out
autoregressively under teacher-forcing during training, scheduled
sampling during late epochs (TrajCast trick #1 for long-rollout stability).

Sklearn-style API:
    model = TrajCastLiteSimulator(context=64, hidden=64)
    model.fit(returns, n_epochs=100)
    synth = model.sample(n_steps=2520, seed=0)
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class _ARTransformer(nn.Module):
    def __init__(self, context: int = 64, hidden: int = 64, n_layers: int = 2,
                 n_heads: int = 4) -> None:
        super().__init__()
        self.context = context
        self.hidden = hidden
        # Channel embedding: each step is (r, |r|) — return + magnitude proxy
        self.in_proj = nn.Linear(2, hidden)
        self.pos = nn.Parameter(torch.randn(1, context, hidden) * 0.02)
        layer = nn.TransformerEncoderLayer(
            d_model=hidden, nhead=n_heads, dim_feedforward=hidden * 2,
            dropout=0.1, batch_first=True, activation="gelu",
        )
        self.enc = nn.TransformerEncoder(layer, num_layers=n_layers)
        self.head_mu = nn.Linear(hidden, 1)
        self.head_logsig = nn.Linear(hidden, 1)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        # x: (B, context, 2)
        h = self.in_proj(x) + self.pos[:, : x.size(1)]
        h = self.enc(h)
        last = h[:, -1]
        mu = self.head_mu(last).squeeze(-1)
        log_sig = self.head_logsig(last).squeeze(-1).clamp(-6.0, 2.0)
        return mu, log_sig


class TrajCastLiteSimulator:
    """Autoregressive 1D transformer surrogate for log returns.

    Trained with Gaussian NLL. At sample time, rolls out autoregressively,
    sampling r_{t+1} ~ N(μ_θ(history), σ_θ(history)²).

    Differs from TrajCast (NMI 2025) in three ways:
      1. No E(3) equivariance — the symmetry here is agent permutation,
         which is satisfied trivially by aggregating to scalar return.
      2. No force decomposition — we predict r_{t+1} directly, no
         intermediate "velocity"/"position" split.
      3. Smaller (~30k params vs TrajCast's ~1M).

    What we keep: autoregressive structure, transformer backbone,
    scheduled sampling in late epochs for rollout stability.
    """

    def __init__(
        self,
        context: int = 64,
        hidden: int = 64,
        n_layers: int = 2,
        n_heads: int = 4,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ) -> None:
        self.context = context
        self.device = torch.device(device)
        self.net = _ARTransformer(
            context=context, hidden=hidden, n_layers=n_layers, n_heads=n_heads,
        ).to(self.device)
        self._mean: float = 0.0
        self._std: float = 1.0

    def fit(
        self,
        returns: np.ndarray,
        n_epochs: int = 100,
        batch_size: int = 256,
        lr: float = 3e-4,
        ss_start_epoch: int | None = None,
        ss_max_prob: float = 0.25,
        seed: int = 0,
    ) -> "TrajCastLiteSimulator":
        r = np.asarray(returns, dtype=np.float32).ravel()
        if r.size < self.context * 4:
            raise ValueError(f"need ≥ {self.context * 4} returns, got {r.size}")
        self._mean = float(r.mean())
        self._std = float(r.std() + 1e-12)
        r_std = (r - self._mean) / self._std
        # Build (context, target) pairs
        n_pairs = r_std.size - self.context
        X = np.empty((n_pairs, self.context, 2), dtype=np.float32)
        Y = np.empty(n_pairs, dtype=np.float32)
        for i in range(n_pairs):
            window = r_std[i : i + self.context]
            X[i, :, 0] = window
            X[i, :, 1] = np.abs(window)
            Y[i] = r_std[i + self.context]
        X_t = torch.from_numpy(X).to(self.device)
        Y_t = torch.from_numpy(Y).to(self.device)

        torch.manual_seed(seed)
        opt = torch.optim.AdamW(self.net.parameters(), lr=lr, weight_decay=1e-4)
        if ss_start_epoch is None:
            ss_start_epoch = n_epochs // 2

        self.net.train()
        for epoch in range(n_epochs):
            perm = torch.randperm(X_t.size(0), device=self.device)
            ss_prob = 0.0
            if epoch >= ss_start_epoch:
                # Linear ramp from 0 → ss_max_prob between ss_start and end
                frac = (epoch - ss_start_epoch) / max(n_epochs - ss_start_epoch, 1)
                ss_prob = ss_max_prob * frac
            for i in range(0, X_t.size(0), batch_size):
                idx = perm[i : i + batch_size]
                xb = X_t[idx]
                yb = Y_t[idx]
                if ss_prob > 0.0:
                    # Scheduled sampling: with prob ss_prob, replace the last
                    # context step with our own prediction (long-rollout regularizer).
                    with torch.no_grad():
                        mu_prev, log_sig_prev = self.net(xb)
                    mask = torch.rand(xb.size(0), device=self.device) < ss_prob
                    if mask.any():
                        xb = xb.clone()
                        sampled = mu_prev + torch.randn_like(mu_prev) * log_sig_prev.exp()
                        xb[mask, -1, 0] = sampled[mask]
                        xb[mask, -1, 1] = sampled[mask].abs()
                mu, log_sig = self.net(xb)
                # Gaussian NLL
                loss = (log_sig + 0.5 * ((yb - mu) / log_sig.exp()) ** 2).mean()
                opt.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.net.parameters(), 1.0)
                opt.step()
        return self

    @torch.no_grad()
    def sample(self, n_steps: int, seed: int = 0) -> np.ndarray:
        torch.manual_seed(seed)
        self.net.eval()
        # Seed the context with samples from N(0, 1) (in the standardized space).
        # We discard the first `context` outputs as burn-in.
        ctx = torch.randn(1, self.context, 2, device=self.device) * 0.5
        out_std = np.empty(n_steps + self.context, dtype=np.float32)
        out_std[: self.context] = ctx[0, :, 0].cpu().numpy()
        for t in range(n_steps):
            mu, log_sig = self.net(ctx)
            r_new = (mu + torch.randn_like(mu) * log_sig.exp()).item()
            out_std[self.context + t] = r_new
            ctx = torch.roll(ctx, -1, dims=1)
            ctx[0, -1, 0] = r_new
            ctx[0, -1, 1] = abs(r_new)
        synth = out_std[self.context :]  # discard burn-in
        return synth * self._std + self._mean


__all__ = ["TrajCastLiteSimulator"]
