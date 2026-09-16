"""Outcome-free preparation checks; no campaign units, training or solver trajectories."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from research.paper_g.response_dx.model import (
    Dynamics,
    Network,
    forecast_nrmse,
    observation_indices,
    pulse,
    pulse_windows,
)


def test_galerkin_rhs_matches_independent_dealiased_grid() -> None:
    dynamics = Dynamics(modes=4, viscosity=.05)
    y = np.array([.3, -.1, .2, .07, -.2, .06, .09, -.04])
    x = np.arange(128) * (2 * np.pi / 128)
    k = np.arange(1, 5)[:, None]
    cosine, sine = np.sqrt(2) * np.cos(k * x), np.sqrt(2) * np.sin(k * x)
    u = y[:4] @ cosine + y[4:] @ sine
    ux = (-np.arange(1, 5) * y[:4]) @ sine + (np.arange(1, 5) * y[4:]) @ cosine
    uxx = (-(np.arange(1, 5) ** 2) * y[:4]) @ cosine + (-(np.arange(1, 5) ** 2) * y[4:]) @ sine
    grid_rhs = -u * ux + .05 * uxx
    projected = np.concatenate((cosine @ grid_rhs, sine @ grid_rhs)) / 128
    np.testing.assert_allclose(dynamics.rhs(0, y), projected, atol=1e-14, rtol=1e-13)
    assert abs(float(grid_rhs.mean())) < 1e-14
    dissipation = -.05 * np.sum(np.tile(np.arange(1, 5) ** 2, 2) * y * y)
    np.testing.assert_allclose(y @ dynamics.rhs(0, y), dissipation, atol=1e-14)


def test_pulse_changes_only_current_control_coordinate() -> None:
    y = np.arange(32, dtype=float)
    changed = pulse(y, 4, .02)
    difference = changed - y
    assert np.flatnonzero(difference).tolist() == [3]
    np.testing.assert_allclose(difference[3], .02)
    np.testing.assert_array_equal(y, np.arange(32))
    np.testing.assert_array_equal(observation_indices(16, 4), [0, 1, 2, 3, 16, 17, 18, 19])


def test_all_five_labels_use_correct_post_reset_history() -> None:
    class ExactTranslationFixture:
        def trajectory(self, state: Any, steps: int) -> Any:
            return np.stack([state + j for j in range(steps + 1)])

    trajectory = np.tile(np.arange(41, dtype=float)[:, None], (1, 32))
    h, targets = pulse_windows(trajectory, 15, 1, .04, ExactTranslationFixture())  # type: ignore[arg-type]
    np.testing.assert_array_equal(h[0, :3], trajectory[12:15])
    np.testing.assert_allclose(h[0, -1], pulse(trajectory[15], 1, .04))
    for j in range(5):
        np.testing.assert_allclose(targets[j], h[j, -1] + 1)
    for j in range(1, 5):
        np.testing.assert_array_equal(h[j, :-1], h[j - 1, 1:])
        np.testing.assert_array_equal(h[j, -1], targets[j - 1])


def test_manual_gradient_matches_central_differences_without_training() -> None:
    net = Network(3, 2, 4, 19)
    x = np.array([[.1, .3, -.7], [.2, -.4, .8]])
    target = np.array([[.2, .5], [-.3, .1]])
    _, gradients = net.loss_gradient(x, target)
    epsilon = 1e-6
    for parameter, gradient in zip(net.parameters, gradients, strict=True):
        for idx in np.ndindex(parameter.shape):
            original = parameter[idx]
            parameter[idx] = original + epsilon
            plus = np.mean((net.predict(x) - target) ** 2)
            parameter[idx] = original - epsilon
            minus = np.mean((net.predict(x) - target) ** 2)
            parameter[idx] = original
            np.testing.assert_allclose(gradient[idx], (plus - minus) / (2 * epsilon), atol=1e-9, rtol=1e-6)


def test_forecast_metric_uses_pooled_reference_norm() -> None:
    reference = np.array([[[1., 2.]], [[3., 4.]]])
    np.testing.assert_allclose(forecast_nrmse(1.1 * reference, reference), .1)
    assert forecast_nrmse(reference, reference) == 0


def test_frozen_architecture_counts() -> None:
    for inputs, outputs, width, count in ((32, 32, 92, 14568), (128, 32, 64, 14496),
                                          (8, 8, 74, 6816), (32, 8, 64, 6792)):
        assert sum(p.size for p in Network(inputs, outputs, width, 19).parameters) == count


def test_nonreference_branch_pipeline_with_fully_mocked_data(monkeypatch: pytest.MonkeyPatch) -> None:
    from research.paper_g.response_dx import runner

    path = Path(__file__).resolve().parents[1] / "research/paper_g/response_dx/preparation/configs/branch_02.json"
    config = json.loads(path.read_text())
    monkeypatch.setattr(runner, "unit_state", lambda unit, dynamics: np.ones(32))
    monkeypatch.setattr(Dynamics, "trajectory", lambda self, state, steps: np.tile(state, (steps + 1, 1)))
    monkeypatch.setattr(runner, "build_examples", lambda *args: (np.ones((4000, 4, 32)), np.ones((4000, 32))))
    monkeypatch.setattr(Network, "fit", lambda *args, **kwargs: {"mocked": True})
    monkeypatch.setattr(Network, "predict", lambda self, x: np.zeros((len(x), self.parameters[-1].size)))
    report = runner.execute(config)
    assert report["reference_check_cpu_seconds"] == 0
    assert report["forecast_nrmse"] == 0
    assert len(report["contrasts"]) == 4
    assert all(c["normalized_mean_error"] < 1e-12 for c in report["contrasts"])


def test_preparation_configs_exclude_confirmation_and_match_budget() -> None:
    directory = Path(__file__).resolve().parents[1] / "research/paper_g/response_dx/preparation"
    review = json.loads((directory / "campaign_review.json").read_text())
    assert len(review["branches"]) == 16
    assert sum(b["cpu_seconds"] for b in review["branches"]) == 10800
    for branch in review["branches"]:
        config = json.loads((directory / "configs" / (branch["branch_id"] + ".json")).read_text())
        assert len(config["unit_ids"]) == len(set(config["unit_ids"])) == 192
        assert all(u.startswith("g_response_dx_explore_") for u in config["unit_ids"])
        assert "confirm" not in json.dumps(config)


def test_image_config_reader_preserves_frozen_numeric_types(tmp_path: Path) -> None:
    from research.paper_g.response_dx.runner import load_config

    source = Path(__file__).resolve().parents[1] / "research/paper_g/response_dx/preparation/configs/branch_01.json"
    mounted = tmp_path / "config.yaml"
    mounted.write_bytes(source.read_bytes())
    config = load_config(mounted)
    assert config == json.loads(source.read_text())
    assert isinstance(config["dynamics"]["rtol"], float)
    assert isinstance(config["dynamics"]["atol"], float)
    mounted.write_text("mode: normal\n")
    assert load_config(mounted) == {"mode": "normal"}


def test_screen_requires_same_response_contrast_in_both_initializations() -> None:
    from research.paper_g.response_dx.assess import assess_regime

    records = {}
    for frames in (1, 4):
        for augmented in (False, True):
            for seed in (201, 202):
                records[(frames, augmented, seed)] = {
                    "forecast_nrmse": .07 if frames == 4 else .09,
                    "contrasts": [{"mode": k, "amplitude": a, "reference_response": .5,
                                   "normalized_mean_error": .05} for k in (1, 4) for a in (.02, .04)],
                }
    records[(4, True, 201)]["contrasts"][0]["normalized_mean_error"] = .3
    records[(4, True, 202)]["contrasts"][1]["normalized_mean_error"] = .3
    assert assess_regime(records, partial=True)["decision"] == "inconclusive"
    records[(4, True, 202)]["contrasts"][0]["normalized_mean_error"] = .3
    assert assess_regime(records, partial=True)["decision"] == "contribution_audit_only"
    assert assess_regime(records, partial=False)["decision"] == "inconclusive"


def test_reference_screen_rejects_nonfinite_rk4_without_generating_units(monkeypatch: pytest.MonkeyPatch) -> None:
    from research.paper_g.response_dx import model

    monkeypatch.setattr(model, "unit_state", lambda *args: np.ones(32))
    monkeypatch.setattr(Dynamics, "trajectory", lambda self, state, steps: np.tile(state, (steps + 1, 1)))
    monkeypatch.setattr(Dynamics, "rk4", lambda self, state, steps, dt: np.full((steps + 1, 32), np.nan))
    with pytest.raises(RuntimeError, match="non-finite RK4"):
        model.reference_check({"train": ["fixed_fixture"], "diagnostic": [], "response": []}, Dynamics())
