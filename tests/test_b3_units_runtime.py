"""Revised L2 units, recurrent evaluation and training-record binding."""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest
import torch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts/reexploration"))
import eval_draws_d0s4 as evaluation
import train_b3_units as revised
import train_stage1_d0s3 as training

from ecomd.mechanisms.fifo_cache import cached_fifo_hook
from ecomd.mechanisms.through_m import Kernel
from ecomd.mechanisms.through_m_wrapper import TrainKernelStream, straight_through_hook
from ecomd.models.fact_surrogate import FactSurrogateBatch, FactSurrogateConfig, RecurrentFactSurrogate
from ecomd.models.unit_fact_surrogate import UnitRecurrentFactSurrogate, fit_training_units


def example() -> tuple[FactSurrogateBatch, UnitRecurrentFactSurrogate]:
    torch.set_num_threads(1)
    features = torch.arange(84).view(1, 6, 14).float() / 10
    volume = torch.tensor([[3., 7., 5., 11., 4., 8.]])
    channels = torch.stack((volume, 1000 * volume), dim=-1).cumsum(1)
    batch = FactSurrogateBatch(features, channels, torch.full((1, 6, 8), 1000.0))
    model = UnitRecurrentFactSurrogate(FactSurrogateConfig(), fit_training_units([batch]),
                                      generator=torch.Generator().manual_seed(2026092304))
    return batch, model


def test_training_units_causal_heads_and_reload() -> None:
    batch, model = example()
    units = fit_training_units([batch])
    assert units["volume_max"] == 11
    assert units["volume_mean"] == pytest.approx(38 / 6)
    original = RecurrentFactSurrogate(FactSurrogateConfig(), generator=torch.Generator().manual_seed(2026092304))
    assert all(torch.equal(a, b) for a, b in zip(original.parameters(), model.parameters(), strict=True))
    observed = model(batch)
    other = replace(batch, channels=batch.channels * 100, features=batch.features.clone())
    other.features[:, 3:] += 1e4
    changed = model(other)
    for key in ("abs_channels", "inc_channels", "flow", "demand"):
        assert torch.equal(getattr(observed, key)[:, :4], getattr(changed, key)[:, :4])
    clone = UnitRecurrentFactSurrogate(FactSurrogateConfig(), units, generator=torch.Generator().manual_seed(1))
    clone.load_state_dict(model.state_dict(), strict=True)
    assert torch.equal(clone(batch).abs_channels, observed.abs_channels)
    assert torch.equal(observed.flow, observed.flow.round()) and (observed.flow >= 0).all()
    with pytest.raises(ValueError, match="feature scales"):
        UnitRecurrentFactSurrogate(FactSurrogateConfig(), {**units, "feature_scale": torch.zeros(14)},
                                  generator=torch.Generator().manual_seed(1))


@pytest.mark.parametrize("coordinate", ["absolute", "increment"])
@pytest.mark.parametrize("kernel", [None, Kernel.FIFO, Kernel.RANDOM_UNIT_WITHIN_PRICE])
def test_recurrent_rollout_keeps_history_and_resets_episodes(coordinate: str, kernel: Kernel | None) -> None:
    batch, model = example()
    surface = evaluation.load_surface(REPO)
    episode = {"features": batch.features[0], "channels_cumulative": batch.channels[0],
               "slot_prices": batch.slot_prices[0]}

    def run(rounds: int) -> dict:
        mechanism = None if kernel is None else straight_through_hook(kernel=kernel, seed_root=999)
        return evaluation.rollout_episode(surface, model, mechanism, episode, rounds,
                                          inference_enforcement="raw" if kernel is None else "through_m",
                                          coordinate=coordinate)

    full = run(6)
    assert torch.equal(full["prediction"][:3], run(3)["prediction"])
    assert torch.equal(full["prediction"], run(6)["prediction"])
    assert full["volume_violations"] == full["cash_violations"] == 0
    if kernel is None:
        output = model(replace(batch, channels=torch.zeros_like(batch.channels)))
        expected = output.abs_channels[0] if coordinate == "absolute" else output.inc_channels[0].cumsum(0)
        torch.testing.assert_close(full["prediction"], expected)
    modified = replace(batch, features=batch.features.clone())
    modified.features[:, 0] += 100
    assert torch.equal(model(batch).abs_channels[:, 0], model(modified).abs_channels[:, 0])
    assert not torch.equal(model(batch).abs_channels[:, 1], model(modified).abs_channels[:, 1])


def test_fifo_cache_preserves_gradient_and_call_stream() -> None:
    a, b = TrainKernelStream(999), TrainKernelStream(999)
    reference, cached = straight_through_hook(kernel=Kernel.FIFO, stream=a), cached_fifo_hook(b)
    for values, demand in (([0., 2., 3.], 4), ([0., 2., 3.], 4), ([0., 0., 0.], 1), ([100., 1., 0.], 1000)):
        left, right = [torch.tensor(values, requires_grad=True) for _ in range(2)]
        x, y = reference(left, demand), cached(right, demand)
        assert torch.equal(x, y)
        weights = torch.tensor([1., 2., 3.])
        x.backward(weights)
        y.backward(weights)
        assert torch.equal(left.grad, right.grad)
    for callback in (reference, cached):
        with pytest.raises(ValueError):
            callback(torch.ones(3), True)
    assert a.calls == b.calls and a.next_call_seeds() == b.next_call_seeds()


def test_revised_training_binding_and_old_checkpoint_rejection(tmp_path: Path) -> None:
    torch.set_num_threads(1)
    data = tmp_path / "data"
    training.stage_seed_episodes({"job": {
        "repo_root": str(REPO), "seed_root": 999, "lineage": "l2",
        "config": training.load_dgp_config(REPO), "dir": str(data),
        "episode_start": 64, "n_train": 2, "workers": 1,
    }})
    units = revised.prepare_units(REPO, data, 999, 2)
    arm_id = "increment_through_m"
    job = {"repo_root": str(REPO), "arm": training.load_arm(REPO, arm_id), "arm_id": arm_id,
           "lineage": "l2", "block_id": "B3", "seed_root": 999, "n_train": 2, "n_iters": 2,
           "episode_start": 64, "through_m_coordinate_mode": "differentiated", "device": "cpu",
           "train_dir": str(data), "job_dir": str(tmp_path / "revised"), "git_sha": training.git_head(REPO),
           "production_constants_decision": revised.DECISION, "l2_units": units, "cache_fifo": True}
    training.train_one(job)
    receipt = revised.accept_job(job)
    assert receipt["revision"] == revised.REVISION
    assert revised.accept_job(job) == receipt
    with pytest.raises(RuntimeError, match="unit/runtime"):
        revised.accept_job({**job, "l2_units": {**units, "seed": 998}})
    old_dir = tmp_path / "B3" / f"arm_{arm_id}" / "seed_000999"
    old_job = {k: v for k, v in job.items() if k not in ("l2_units", "cache_fifo")}
    training.train_one({**old_job, "job_dir": str(old_dir)})
    with pytest.raises(RuntimeError, match="accepted revised L2"):
        evaluation.load_arm_surface(evaluation.load_surface(REPO), tmp_path / "B3", arm_id, 999)
    manifest = data / "train_episodes_manifest.json"
    document = json.loads(manifest.read_text())
    document["episodes"][0]["episode_index"] = 0
    manifest.write_text(json.dumps(document))
    with pytest.raises(RuntimeError, match="authorized window"):
        revised.prepare_units(REPO, data, 999, 2)


def test_b3_decision_and_record_namespace() -> None:
    assert evaluation.require_run_id_decision(REPO, revised.DECISION, "B3") == revised.require_decision(REPO)
    with pytest.raises(RuntimeError, match="production requires"):
        evaluation.require_run_id_decision(REPO, evaluation.RUN_ID_DECISION, "B3")
    record = evaluation.make_record(block_id="B3", record_class="RC1", run_id="B3.fixture", horizon=16)
    assert record["run_id"].endswith(".h16") and record["protocol_amendment"] == revised.DECISION
