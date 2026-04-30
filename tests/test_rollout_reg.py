"""Tests for stop-grad rollout regularization (057) and bf16 mixed precision."""
from __future__ import annotations

import numpy as np
import pytest
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.training.losses import LossWeights, build_targets_from_returns
from ecomd.training.train_distributed import _compute_rollout_reg_loss


def _build_tiny_sim() -> EcoMDSimulator:
    return EcoMDSimulator(EcoMDConfig(
        n_agents=200, d_state=16, hidden=32, dt=0.01,
        gamma_init=1.0, temperature_init=0.05, init_state_scale=0.1,
        noise_dist="t", noise_df=5,
        pairwise_kind="stochastic_mlp", sps_k_random=8,
        sps_resample_per_step=True,
        twopop_enabled=True,
        twopop_gamma_scale=[0.7, 1.5, 1.0, 0.5],
        twopop_temp_scale=[0.5, 2.0, 1.0, 0.3],
        v2_type_seed=42,
        bptt_custom_function=True,
        edge_gating_enabled=True, edge_gating_init_p=0.7,
        edge_gating_input_u=True,
        global_state_enabled=True, global_state_d=16,
        global_state_into_pair=True,
        pair_input_layernorm=True,
        jump_lambda=0.5, jump_scale=0.01,
    ))


def _build_targets():
    rng = np.random.default_rng(0)
    real = (rng.standard_normal(50) * 0.01).astype(np.float64)
    return build_targets_from_returns(real, max_lag=4, k_frac=0.05)


def _weights() -> LossWeights:
    return LossWeights(
        w_acf_sq=1.0, max_lag=4, hill_k_frac=0.05,
        loss_family="moments", distance_mode="l1",
        tail_estimator="soft_hill", balance_mode="fixed",
    )


def test_rollout_reg_fp32_finite_and_grad():
    sim = _build_tiny_sim()
    ts = _build_targets()
    w = _weights()
    gen = torch.Generator(); gen.manual_seed(0)

    loss = _compute_rollout_reg_loss(
        sim, [("default", ts, 1.0)], w, gen,
        steps=24, chunk=8, warmup_steps=2,
        use_amp=False, amp_device_type="cpu", amp_dtype=torch.float32,
    )
    assert loss is not None
    assert torch.isfinite(loss).item()
    loss.backward()
    n_grad = sum(1 for p in sim.parameters()
                 if p.grad is not None and p.grad.abs().sum() > 0)
    n_total = sum(1 for _ in sim.parameters())
    # Most params should receive grad from a multi-chunk fresh-init rollout.
    assert n_grad >= n_total - 2, f"grad-receiving params {n_grad}/{n_total}"


def test_rollout_reg_bf16_autocast_runs():
    """bf16 autocast on CPU works in recent PyTorch. We don't assert
    numerical match against fp32 (bf16 mantissa is 7 bit) — only finite
    + gradient flow."""
    sim = _build_tiny_sim()
    ts = _build_targets()
    w = _weights()
    gen = torch.Generator(); gen.manual_seed(0)

    loss = _compute_rollout_reg_loss(
        sim, [("default", ts, 1.0)], w, gen,
        steps=24, chunk=8, warmup_steps=2,
        use_amp=True, amp_device_type="cpu", amp_dtype=torch.bfloat16,
    )
    assert loss is not None
    assert torch.isfinite(loss).item()
    loss.backward()
    n_grad = sum(1 for p in sim.parameters()
                 if p.grad is not None and p.grad.abs().sum() > 0)
    n_total = sum(1 for _ in sim.parameters())
    assert n_grad >= n_total - 2, f"bf16 grad-receiving params {n_grad}/{n_total}"


def test_rollout_reg_chunked_independent():
    """Memory-bounded: backward through multi-chunk rollout doesn't
    require remembering state across chunks. Verify that the backward
    pass completes without holding the intermediate state's autograd
    graph (no implicit OOM on smoke-size models)."""
    sim = _build_tiny_sim()
    ts = _build_targets()
    w = _weights()
    gen = torch.Generator(); gen.manual_seed(1)

    # 4 chunks of 6 = 24 steps total. If chunk-detach works, peak memory
    # stays at 1 chunk's V-graph; if not, we'd see ~4× memory.
    loss = _compute_rollout_reg_loss(
        sim, [("default", ts, 1.0)], w, gen,
        steps=24, chunk=6, warmup_steps=1,
        use_amp=False, amp_device_type="cpu", amp_dtype=torch.float32,
    )
    assert loss is not None
    loss.backward()
    # Smoke: just ensure no exception and non-zero gradient on at least
    # one parameter.
    g_sum = sum(p.grad.abs().sum().item() for p in sim.parameters()
                if p.grad is not None)
    assert g_sum > 0
