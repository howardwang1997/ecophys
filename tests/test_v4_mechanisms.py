"""Unit tests for V4 mechanisms — Lévy noise, asymmetric drag, memory kernel.

These three knobs add structural physics to the v3 baseline, each
targeting one of the three hardest stylized facts:

    Lévy noise    → hill_tail_index   (heavy-tail noise reproduces α∈[2,4])
    asym drag     → leverage_effect   (γ shrinks after down-moves)
    memory kernel → zumbach_asymmetry (slow EMA of |Δs| modulates noise)

We test each in isolation, the composition, and reproducibility under
seed control. Backward-compat: defaults reproduce baseline behaviour
bit-identically.
"""

from __future__ import annotations

import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.physics.integrator import OverdampedLangevin, _sample_levy_symmetric


def _baseline_config(**overrides) -> EcoMDConfig:
    base = dict(
        n_agents=64, d_state=8, hidden=16, dt=0.01,
        gamma_init=10.0, temperature_init=0.05, init_state_scale=0.1,
        pairwise_kind="stochastic_mlp", sps_k_random=8,
        learn_gamma=False, learn_temperature=False,
    )
    base.update(overrides)
    return EcoMDConfig(**base)


def test_levy_sampler_tails_grow_as_alpha_decreases() -> None:
    """Heavier tail (smaller α) ⇒ more samples beyond a fixed threshold.

    Use tail-probability rather than kurtosis: kurtosis estimates are
    extremely noisy when the underlying distribution has infinite fourth
    moment (which is true for any α<2). P(|X|>5) is a far more stable
    summary statistic for the ordering test.
    """
    g = torch.Generator().manual_seed(0)
    tail_probs = []
    for alpha in [1.95, 1.7, 1.4]:
        x = _sample_levy_symmetric((50_000,), alpha, generator=g,
                                   device=torch.device("cpu"), dtype=torch.float32)
        tail_probs.append((x.abs() > 5.0).float().mean().item())
    assert tail_probs[0] < tail_probs[1] < tail_probs[2], \
        f"P(|X|>5) must grow as α↓: {tail_probs}"


def test_levy_step_finite() -> None:
    itg = OverdampedLangevin(noise_dist="levy", levy_alpha=1.7)
    s = torch.zeros(8, 4)
    f = torch.zeros_like(s)
    out = itg.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01,
                   generator=torch.Generator().manual_seed(0))
    assert torch.isfinite(out.s_next).all()


def test_asym_drag_amplifies_noise_after_down_move() -> None:
    """Leverage sign: Δp<0 ⇒ next-step γ↓ ⇒ noise ↑. This must be the case
    for the leverage_effect band [-6, -0.5] to be reachable.
    """
    s, f = torch.zeros(64, 4), torch.zeros(64, 4)
    seed = 11

    itg_neg = OverdampedLangevin(asym_drag_alpha=0.5)
    itg_neg.update_price_signal(-0.01)
    out_neg = itg_neg.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01,
                           generator=torch.Generator().manual_seed(seed))
    itg_pos = OverdampedLangevin(asym_drag_alpha=0.5)
    itg_pos.update_price_signal(+0.01)
    out_pos = itg_pos.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01,
                           generator=torch.Generator().manual_seed(seed))
    assert out_neg.s_next.std() > out_pos.s_next.std()


def test_memory_kernel_ema_grows_under_volatility() -> None:
    itg = OverdampedLangevin(memory_kernel_lambda=0.9, memory_kernel_strength=2.0)
    s, f = torch.zeros(8, 4), torch.zeros(8, 4)
    stds = []
    for i in range(6):
        o = itg.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01,
                     generator=torch.Generator().manual_seed(i))
        stds.append(o.s_next.std().item())
        s = o.s_next
    assert stds[-1] > stds[0], f"EMA should grow as |Δs| accumulates: {stds}"
    itg.reset_state()
    assert itg._mem_ema is None


def test_v4_defaults_match_baseline_bit_identically() -> None:
    """No knobs set ⇒ trajectory must equal baseline (Gaussian, no drag, no kernel)."""
    g_a = torch.Generator().manual_seed(7)
    g_b = torch.Generator().manual_seed(7)
    itg_a = OverdampedLangevin()  # baseline
    itg_b = OverdampedLangevin(noise_dist="normal", asym_drag_alpha=0.0,
                               memory_kernel_lambda=0.0, memory_kernel_strength=0.0)
    s, f = torch.zeros(8, 4), torch.zeros(8, 4)
    out_a = itg_a.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g_a)
    out_b = itg_b.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g_b)
    assert torch.allclose(out_a.s_next, out_b.s_next)


def test_v4_simulator_levy_finite_run() -> None:
    sim = EcoMDSimulator(_baseline_config(noise_dist="levy", noise_levy_alpha=1.7)).eval()
    with torch.no_grad():
        traj = sim.run(n_steps=80, seed=42)
    r = traj.log_returns_np()[1:]
    assert r.size > 0 and (r == r).all()


def test_v4_simulator_combined_finite_run() -> None:
    cfg = _baseline_config(
        noise_dist="levy", noise_levy_alpha=1.8,
        asym_drag_alpha=0.3,
        memory_kernel_lambda=0.9, memory_kernel_strength=1.0,
        inner_steps_per_price=3,
    )
    sim = EcoMDSimulator(cfg).eval()
    with torch.no_grad():
        traj = sim.run(n_steps=80, seed=42)
    r = traj.log_returns_np()[1:]
    assert r.size > 0 and (r == r).all()


def test_v4_integrator_seed_reproducible() -> None:
    s, f = torch.zeros(8, 4), torch.zeros(8, 4)
    out = []
    for _ in range(2):
        itg = OverdampedLangevin(noise_dist="levy", levy_alpha=1.7,
                                 asym_drag_alpha=0.3,
                                 memory_kernel_lambda=0.9,
                                 memory_kernel_strength=1.0)
        itg.update_price_signal(-0.005)
        out.append(itg.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01,
                            generator=torch.Generator().manual_seed(42)).s_next)
    assert torch.allclose(out[0], out[1])
