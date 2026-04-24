"""Tests for the overdamped Langevin integrator.

Key physics gates:
- Energy conservation at T=0 under a simple harmonic V_cons (drift only).
- Fluctuation-dissipation relation: equilibrium ⟨s²⟩ ≈ T / k (for V = 0.5 k s²).
- Seed reproducibility.
- v0.6: Student-t noise has unit variance and excess kurtosis > 0.
"""

from __future__ import annotations

import math

import pytest
import torch

from ecomd.physics.integrator import OverdampedLangevin, UnderdampedLangevin, _sample_unit_t


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


# ── v0.6: Student-t noise ────────────────────────────────────────────────────


def test_sample_unit_t_is_unit_variance():
    """Unit-variance normalization: ⟨ε²⟩ ≈ 1 over large sample."""
    gen = torch.Generator().manual_seed(0)
    samples = _sample_unit_t((20000,), df=5, generator=gen,
                              device=torch.device("cpu"), dtype=torch.float32)
    assert abs(samples.var().item() - 1.0) < 0.10


def test_sample_unit_t_has_heavy_tails():
    """Student-t(df=5) unit-variance has excess kurtosis 6/(df-4) = 6. Gaussian has 0."""
    gen = torch.Generator().manual_seed(0)
    samples = _sample_unit_t((30000,), df=5, generator=gen,
                              device=torch.device("cpu"), dtype=torch.float32)
    # 4th central moment / var² - 3 = excess kurtosis
    m = samples.mean()
    var = samples.var(unbiased=False)
    excess_kurt = ((samples - m) ** 4).mean() / var.pow(2) - 3.0
    assert excess_kurt > 2.0, f"expected heavy tail kurtosis > 2, got {excess_kurt.item():.2f}"


def test_sample_unit_t_reproducible():
    def draw(seed: int):
        gen = torch.Generator().manual_seed(seed)
        return _sample_unit_t((100,), df=5, generator=gen,
                               device=torch.device("cpu"), dtype=torch.float32)
    assert torch.allclose(draw(7), draw(7))
    assert not torch.allclose(draw(7), draw(8))


def test_overdamped_t_noise_preserves_fdt():
    """Student-t noise at unit variance must still satisfy ⟨s²⟩ ≈ T/k."""
    integ = OverdampedLangevin(noise_dist="t", noise_df=5)
    torch.manual_seed(11)
    n, d = 500, 3
    s = torch.zeros(n, d)
    k, T, gamma, dt = 1.0, 0.5, 1.0, 0.02
    gen = torch.Generator().manual_seed(11)
    for _ in range(2500):
        f = -k * s
        s = integ.step(s, f, torch.zeros_like(s), T=T, gamma=gamma, dt=dt, generator=gen).s_next
    s2 = 0.0
    for _ in range(1000):
        f = -k * s
        s = integ.step(s, f, torch.zeros_like(s), T=T, gamma=gamma, dt=dt, generator=gen).s_next
        s2 += s.pow(2).mean().item()
    s2 /= 1000
    # FDT should hold for any unit-variance noise (is the key reason we want unit-variance)
    assert abs(s2 - T / k) / (T / k) < 0.12


def test_overdamped_t_noise_has_heavier_tail_than_gaussian():
    """Integrated trajectory kurtosis: Student-t driver > Gaussian driver."""
    kurts = {}
    for name, integ in [("normal", OverdampedLangevin("normal")),
                        ("t5",     OverdampedLangevin("t", noise_df=5))]:
        torch.manual_seed(3)
        s = torch.zeros(200, 2)
        gen = torch.Generator().manual_seed(3)
        # weak restoring force → noise dominates; let it run long
        increments = []
        for _ in range(500):
            f = -0.1 * s
            out = integ.step(s, f, torch.zeros_like(s), T=1.0, gamma=1.0, dt=0.01, generator=gen)
            increments.append((out.s_next - s).flatten())
            s = out.s_next
        inc = torch.cat(increments)
        m = inc.mean()
        var = inc.var(unbiased=False)
        kurts[name] = ((inc - m) ** 4).mean() / var.pow(2) - 3.0
    assert kurts["t5"] > kurts["normal"] + 0.3, (
        f"t-noise trajectory kurtosis {kurts['t5']:.2f} not clearly above Gaussian {kurts['normal']:.2f}"
    )


def test_overdamped_noise_dist_validation():
    with pytest.raises(ValueError):
        OverdampedLangevin(noise_dist="cauchy")
    with pytest.raises(ValueError):
        OverdampedLangevin(noise_dist="t", noise_df=2)
    with pytest.raises(ValueError):
        OverdampedLangevin(noise_dist="t", noise_df=1.5)  # type: ignore[arg-type]
