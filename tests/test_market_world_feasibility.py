from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from ecomd.market_world import (
    ResponseParameters,
    anchor_signature,
    expected_market_probability,
    simulate_path,
    truth_response,
)
from ecomd.market_world.protocol import load_protocol

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/market_world/intervention_feasibility_v1.yaml"


def test_response_clocks_are_distinct_and_bounded() -> None:
    protocol = load_protocol(CONFIG)
    world = protocol.world
    single = truth_response(world, "single_rate")
    two_rate = truth_response(world, "two_rate")

    single_path = [single.shift(epoch, 1.0) for epoch in range(world.post_epochs)]
    two_path = [two_rate.shift(epoch, 1.0) for epoch in range(world.post_epochs)]

    assert single_path[0] != pytest.approx(single_path[-1])
    assert two_path != pytest.approx(single_path)
    assert all(world.target_slope <= shift <= 0.0 for shift in single_path)
    assert expected_market_probability(world, single, 1.0, 5) < world.baseline_market_probability


def test_small_world_is_deterministic_and_mechanically_valid() -> None:
    protocol = load_protocol(CONFIG)
    world = replace(
        protocol.world,
        events_per_epoch=32,
        pre_epochs=3,
        post_epochs=6,
    )
    response = truth_response(world, "single_rate")

    first = simulate_path(world, 44, 1.0, response, intervention=True)
    second = simulate_path(world, 44, 1.0, response, intervention=True)
    counterfactual = simulate_path(
        world,
        44,
        1.0,
        ResponseParameters(kind="frozen"),
        intervention=False,
    )

    assert first.mechanics_violations == ()
    assert first.event_digest == second.event_digest
    assert anchor_signature(first) == anchor_signature(second)
    assert len(first.primary_effect(counterfactual)) == 6
    assert sum(epoch.rule_cancellations for epoch in first.epochs) > 0


def test_confound_changes_only_the_early_probability() -> None:
    protocol = load_protocol(CONFIG)
    world = protocol.world
    response = truth_response(world, "confounded")

    clean_early = expected_market_probability(world, response, 1.0, 0)
    shifted_early = expected_market_probability(world, response, 1.0, 0, confounded=True)
    clean_late = expected_market_probability(world, response, 1.0, world.confound_epochs)
    shifted_late = expected_market_probability(
        world,
        response,
        1.0,
        world.confound_epochs,
        confounded=True,
    )

    assert shifted_early - clean_early == pytest.approx(world.confound_probability_shift)
    assert shifted_late == clean_late
