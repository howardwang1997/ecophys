"""WGAN-LP baseline (Wiese 2020 QuantGAN-style) for synthetic returns.

A simpler stand-in for TimeGAN (Yoon 2019) — same paper-quality story
(generative model trained on real returns, sample synthetic trajectories
and score on the 11 Cont stylized facts) at ~3× less impl complexity.

Architecture: temporal-convolutional generator + critic, WGAN with
Lipschitz penalty (gradient penalty) loss. Trained to match the
distribution of K-step log-return windows.

Sklearn-style API:
    model = WGANLPSimulator(window=64, latent_dim=16)
    model.fit(returns, n_epochs=200)
    synth = model.sample(n_steps=2520, seed=0)  # ~10y of daily

We deliberately keep this small: 1D temporal-conv blocks, ~50k params.
Goal is a defensible "GAN-family baseline" for §5 of the paper, not a
SOTA generative model.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


def _tcn_block(c_in: int, c_out: int, k: int = 3, dilation: int = 1) -> nn.Sequential:
    pad = (k - 1) * dilation // 2
    return nn.Sequential(
        nn.Conv1d(c_in, c_out, kernel_size=k, padding=pad, dilation=dilation),
        nn.LeakyReLU(0.2, inplace=True),
    )


class _Generator(nn.Module):
    def __init__(self, latent_dim: int = 16, window: int = 64, hidden: int = 32) -> None:
        super().__init__()
        self.latent_dim = latent_dim
        self.window = window
        self.net = nn.Sequential(
            _tcn_block(latent_dim, hidden, k=3, dilation=1),
            _tcn_block(hidden,     hidden, k=3, dilation=2),
            _tcn_block(hidden,     hidden, k=3, dilation=4),
            nn.Conv1d(hidden, 1, kernel_size=1),
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        # z: (B, latent_dim, window)
        return self.net(z).squeeze(1)  # (B, window)


class _Critic(nn.Module):
    def __init__(self, window: int = 64, hidden: int = 32) -> None:
        super().__init__()
        self.net = nn.Sequential(
            _tcn_block(1,      hidden, k=3, dilation=1),
            _tcn_block(hidden, hidden, k=3, dilation=2),
            _tcn_block(hidden, hidden, k=3, dilation=4),
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
            nn.Linear(hidden, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x.unsqueeze(1)).squeeze(-1)


def _gradient_penalty(critic: _Critic, real: torch.Tensor, fake: torch.Tensor,
                       device: torch.device) -> torch.Tensor:
    bs = real.size(0)
    alpha = torch.rand(bs, 1, device=device)
    interp = (alpha * real + (1 - alpha) * fake).requires_grad_(True)
    d_interp = critic(interp)
    grads = torch.autograd.grad(
        outputs=d_interp.sum(), inputs=interp,
        create_graph=True, retain_graph=True,
    )[0]
    return ((grads.norm(2, dim=1) - 1) ** 2).mean()


class WGANLPSimulator:
    """WGAN-LP trained on rolling windows of log returns.

    Note: this is the *minimal* viable GAN-baseline. It learns the marginal
    + windowed dependence structure but is not state-of-the-art. Acceptable
    for the "GAN-family ablation" cell in Paper A's baseline table.
    """

    def __init__(
        self,
        window: int = 64,
        latent_dim: int = 16,
        hidden: int = 32,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ) -> None:
        self.window = window
        self.latent_dim = latent_dim
        self.hidden = hidden
        self.device = torch.device(device)
        self.G = _Generator(latent_dim=latent_dim, window=window, hidden=hidden).to(self.device)
        self.D = _Critic(window=window, hidden=hidden).to(self.device)
        self._mean: float = 0.0
        self._std: float = 1.0

    def fit(
        self,
        returns: np.ndarray,
        n_epochs: int = 200,
        batch_size: int = 128,
        n_critic: int = 5,
        lr: float = 1e-4,
        gp_weight: float = 10.0,
        seed: int = 0,
    ) -> "WGANLPSimulator":
        r = np.asarray(returns, dtype=np.float32).ravel()
        if r.size < self.window * 2:
            raise ValueError(f"need ≥ {self.window * 2} returns, got {r.size}")
        # Per-fit standardization (saved for sampling)
        self._mean = float(r.mean())
        self._std = float(r.std() + 1e-12)
        r_std = (r - self._mean) / self._std
        # Build rolling windows
        n_win = r_std.size - self.window + 1
        windows = np.lib.stride_tricks.as_strided(
            r_std, shape=(n_win, self.window),
            strides=(r_std.strides[0], r_std.strides[0]),
        ).copy()
        ds = TensorDataset(torch.from_numpy(windows))
        dl = DataLoader(ds, batch_size=batch_size, shuffle=True, drop_last=True)

        torch.manual_seed(seed)
        opt_G = torch.optim.Adam(self.G.parameters(), lr=lr, betas=(0.5, 0.9))
        opt_D = torch.optim.Adam(self.D.parameters(), lr=lr, betas=(0.5, 0.9))

        for epoch in range(n_epochs):
            for (real_batch,) in dl:
                real = real_batch.to(self.device)
                bs = real.size(0)
                # Critic update
                for _ in range(n_critic):
                    z = torch.randn(bs, self.latent_dim, self.window, device=self.device)
                    with torch.no_grad():
                        fake = self.G(z)
                    d_real = self.D(real).mean()
                    d_fake = self.D(fake).mean()
                    gp = _gradient_penalty(self.D, real, fake, self.device)
                    d_loss = d_fake - d_real + gp_weight * gp
                    opt_D.zero_grad()
                    d_loss.backward()
                    opt_D.step()
                # Generator update
                z = torch.randn(bs, self.latent_dim, self.window, device=self.device)
                fake = self.G(z)
                g_loss = -self.D(fake).mean()
                opt_G.zero_grad()
                g_loss.backward()
                opt_G.step()
        return self

    @torch.no_grad()
    def sample(self, n_steps: int, seed: int = 0) -> np.ndarray:
        torch.manual_seed(seed)
        # Generate enough windows to cover n_steps, then concatenate non-overlapping segments
        n_win = (n_steps + self.window - 1) // self.window
        z = torch.randn(n_win, self.latent_dim, self.window, device=self.device)
        out = self.G(z).cpu().numpy().reshape(-1)[:n_steps]
        return out * self._std + self._mean


__all__ = ["WGANLPSimulator"]
