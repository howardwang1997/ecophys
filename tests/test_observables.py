"""Tests for the trajectory recorder / EcoMDTrajectory dataclass."""

from __future__ import annotations

import pytest
import torch

from ecomd.physics.observables import EcoMDTrajectory, TrajectoryRecorder


def _fake_step(n: int, d: int, step_idx: int) -> dict[str, torch.Tensor]:
    t = float(step_idx)
    return {
        "s": torch.full((n, d), t),
        "f_cons": torch.full((n, d), t + 0.1),
        "f_diss": torch.full((n, d), t + 0.2),
        "f_stoch": torch.full((n, d), t + 0.3),
        "velocity": torch.full((n, d), t + 0.4),
        "log_price": torch.tensor(t * 0.01),
        "log_return": torch.tensor(t * 0.001),
        "volume": torch.tensor(t + 1.0),
        "excess_demand": torch.tensor(t - 0.5),
    }


def test_record_and_finalize_shapes():
    rec = TrajectoryRecorder(dt=0.01)
    n, d = 5, 4
    T = 10
    for i in range(T):
        rec.record(**_fake_step(n, d, i))
    traj = rec.finalize()
    assert isinstance(traj, EcoMDTrajectory)
    assert traj.states.shape == (T, n, d)
    assert traj.f_cons.shape == (T, n, d)
    assert traj.f_diss.shape == (T, n, d)
    assert traj.f_stoch.shape == (T, n, d)
    assert traj.velocities.shape == (T, n, d)
    assert traj.log_prices.shape == (T,)
    assert traj.log_returns.shape == (T,)
    assert traj.volumes.shape == (T,)
    assert traj.excess_demand.shape == (T,)
    assert traj.dt == 0.01


def test_empty_recorder_raises():
    rec = TrajectoryRecorder(dt=0.01)
    with pytest.raises(RuntimeError):
        rec.finalize()


def test_properties():
    rec = TrajectoryRecorder(dt=0.01)
    n, d = 3, 6
    for i in range(7):
        rec.record(**_fake_step(n, d, i))
    traj = rec.finalize()
    assert traj.n_steps == 7
    assert traj.n_agents == 3
    assert traj.d_state == 6


def test_numpy_conversions():
    rec = TrajectoryRecorder(dt=0.01)
    for i in range(4):
        rec.record(
            **_fake_step(2, 3, i),
            latent_flow_alignment=torch.tensor(0.1 * i),
        )
    traj = rec.finalize()
    arr = traj.log_returns_np()
    assert arr.shape == (4,)
    vol = traj.volumes_np()
    assert vol.shape == (4,)
    expected = torch.tensor([0.0, 0.1, 0.2, 0.3]).numpy()
    assert traj.latent_flow_alignment_np() == pytest.approx(expected)
    assert traj.ofi_np() == pytest.approx(expected)
    assert traj.ofi is traj.latent_flow_alignment


def test_recorder_accepts_legacy_ofi_keyword():
    rec = TrajectoryRecorder(dt=0.01)
    rec.record(**_fake_step(2, 3, 0), ofi=torch.tensor(0.25))
    traj = rec.finalize()
    assert traj.latent_flow_alignment.item() == pytest.approx(0.25)


def test_trajectory_constructor_accepts_legacy_ofi_keyword():
    rec = TrajectoryRecorder(dt=0.01)
    rec.record(**_fake_step(2, 3, 0), latent_flow_alignment=torch.tensor(0.25))
    traj = rec.finalize()
    legacy = EcoMDTrajectory(
        states=traj.states,
        f_cons=traj.f_cons,
        f_diss=traj.f_diss,
        f_stoch=traj.f_stoch,
        velocities=traj.velocities,
        log_prices=traj.log_prices,
        log_returns=traj.log_returns,
        volumes=traj.volumes,
        excess_demand=traj.excess_demand,
        ofi=traj.latent_flow_alignment,
        dt=traj.dt,
        meta=traj.meta,
    )
    assert legacy.latent_flow_alignment is traj.latent_flow_alignment


def test_recorder_rejects_ambiguous_alignment_aliases():
    rec = TrajectoryRecorder(dt=0.01)
    with pytest.raises(ValueError, match="not both"):
        rec.record(
            **_fake_step(2, 3, 0),
            latent_flow_alignment=torch.tensor(0.25),
            ofi=torch.tensor(0.25),
        )


def test_detach_preserves_shape():
    rec = TrajectoryRecorder(dt=0.01)
    for i in range(3):
        rec.record(**_fake_step(2, 3, i))
    traj = rec.finalize()
    traj_d = traj.detach()
    assert traj_d.states.shape == traj.states.shape
    assert not traj_d.states.requires_grad
