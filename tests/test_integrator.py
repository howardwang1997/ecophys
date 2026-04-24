"""Tests for the overdamped Langevin integrator.

Key physics gates:
- Energy conservation at T=0 under a simple harmonic V_cons (drift only).
- Fluctuation-dissipation relation: equilibrium ⟨s²⟩ ≈ T / k (for V = 0.5 k s²).
- Seed reproducibility.
"""

from __future__ import annotations

import math

import pytest
import torch

from ecomd.physics.integrator import OverdampedLangevin, UnderdampedLangevin


# ── Simple harmonic test fixture ─────────────────────────────────────────────


def harmonic_forces(s: torch.Tensor, k: float = 1.0) -> torch.Tensor:
    """F = -k s. Conservative."""
    return -k * s


# ── Basic shape / finite ─────────────────────────────────────────────────────


def test_step_shape_and_finite():
    integ = OverdampedLangevin()
    s = torch.zeros(5, 3)
    f = harmonic_forces(s)
    out = integ.step(
        s, f, torch.zeros_like(s), T=0.1, gamma=1.0, dt=0.01,
        generator=torch.Generator().manual_seed(0),
    )
    assert out.s_next.shape == s.shape
    assert out.velocity.shape == s.shape
    assert torch.isfinite(out.s_next).all()


def test_shape_mismatch_raises():
    integ = OverdampedLangevin()
    s = torch.zeros(5, 3)
    with pytest.raises(ValueError):
        integ.step(
            s, torch.zeros(4, 3), torch.zeros_like(s), T=0.1, gamma=1.0, dt=0.01,
        )


# ── Physics: energy conservation at T=0 ──────────────────────────────────────


def test_overdamped_relaxation_T0():
    """With T=0 and harmonic V, overdamped dynamics must relax to the origin.

    For V=0.5 k s², overdamped: ds/dt = -k s / γ → s(t) = s(0) exp(-k t/γ).
    Energy 0.5 k |s|² must decay monotonically, not grow.
    """
    integ = OverdampedLangevin()
    torch.manual_seed(0)
    s = torch.randn(20, 4)
    k = 1.0
    gamma = 1.0
    dt = 0.01

    E_init = 0.5 * k * (s ** 2).sum()
    E_prev = E_init.item()

    for _ in range(1000):
        f = harmonic_forces(s, k)
        out = integ.step(s, f, torch.zeros_like(s), T=0.0, gamma=gamma, dt=dt)
        s = out.s_next
        E = 0.5 * k * (s ** 2).sum().item()
        assert E <= E_prev + 1e-7, f"energy grew: {E_prev} -> {E}"
        E_prev = E

    # After 10 time-units of relaxation s should be essentially zero.
    E_final = 0.5 * k * (s ** 2).sum().item()
    assert E_final < E_init.item() * 1e-3


# ── Physics: fluctuation-dissipation ─────────────────────────────────────────


def test_fluctuation_dissipation_relation():
    """Equilibrium of ds/dt = -k s / γ + √(2T/γ) ξ: ⟨s²⟩ = T/k per dim."""
    integ = OverdampedLangevin()
    torch.manual_seed(1)
    n, d = 500, 3
    s = torch.zeros(n, d)
    k = 1.0
    T = 0.5
    gamma = 1.0
    dt = 0.02

    # equilibrate first
    gen = torch.Generator().manual_seed(1)
    for _ in range(2000):
        f = harmonic_forces(s, k)
        s = integ.step(s, f, torch.zeros_like(s), T=T, gamma=gamma, dt=dt, generator=gen).s_next

    # then sample for averaging
    s2_sum = 0.0
    n_samples = 1000
    for _ in range(n_samples):
        f = harmonic_forces(s, k)
        s = integ.step(s, f, torch.zeros_like(s), T=T, gamma=gamma, dt=dt, generator=gen).s_next
        s2_sum += s.pow(2).mean().item()  # per-coordinate variance estimator

    s2_avg = s2_sum / n_samples
    expected = T / k
    rel_err = abs(s2_avg - expected) / expected
    # Euler-Maruyama has O(dt) bias; with dt=0.02, k=1 expect a few %.
    assert rel_err < 0.10, f"⟨s²⟩ = {s2_avg:.4f}, expected T/k = {expected:.4f}, rel err {rel_err:.3f}"


# ── Reproducibility ─────────────────────────────────────────────────────────


def test_seed_reproducibility():
    integ = OverdampedLangevin()
    s0 = torch.randn(6, 2)

    def run(seed: int) -> torch.Tensor:
        s = s0.clone()
        gen = torch.Generator().manual_seed(seed)
        for _ in range(50):
            f = harmonic_forces(s)
            s = integ.step(s, f, torch.zeros_like(s), T=0.2, gamma=1.0, dt=0.01, generator=gen).s_next
        return s

    assert torch.allclose(run(0), run(0))
    assert not torch.allclose(run(0), run(1))


def test_zero_temperature_no_noise():
    integ = OverdampedLangevin()
    s = torch.zeros(4, 2)
    out = integ.step(s, torch.zeros_like(s), torch.zeros_like(s), T=0.0, gamma=1.0, dt=0.01)
    assert torch.allclose(out.s_next, s)


# ── Underdamped placeholder ─────────────────────────────────────────────────


def test_underdamped_stub_raises():
    u = UnderdampedLangevin()
    s = torch.zeros(3, 2)
    with pytest.raises(NotImplementedError):
        u.step(s, torch.zeros_like(s), torch.zeros_like(s), T=0.1, gamma=1.0, dt=0.01)
