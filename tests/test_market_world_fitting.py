from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from ecomd.market_world import ResponseParameters, expected_market_probability
from ecomd.market_world.evaluation import merge_scientific_shards, run_evaluation_shard
from ecomd.market_world.fitting import DevelopmentObservation, fit_response
from ecomd.market_world.hardware import merge_hardware_probes
from ecomd.market_world.protocol import load_protocol

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/market_world/intervention_feasibility_v1.yaml"


def test_fit_recovers_an_exact_single_rate_response() -> None:
    protocol = load_protocol(CONFIG)
    expected_slope = -0.73
    expected_rate = 0.24
    response = ResponseParameters(
        kind="single_rate",
        target_slope=expected_slope,
        rate=expected_rate,
    )
    observations = [
        DevelopmentObservation(
            family="single_rate",
            seed=500 + seed,
            magnitude=magnitude,
            post_epoch=epoch,
            market_fraction=expected_market_probability(
                protocol.world,
                response,
                magnitude,
                epoch,
            ),
        )
        for seed in range(2)
        for magnitude in (0.5, 1.5)
        for epoch in range(12)
    ]

    fitted = fit_response(protocol, "single_rate", observations)

    assert fitted.target_slope == pytest.approx(expected_slope, abs=1e-6)
    assert fitted.rate == pytest.approx(expected_rate, abs=1e-6)
    assert fitted.objective_rmse < 1e-8


def test_tiny_nonformal_shards_merge_without_identity_leakage() -> None:
    original = load_protocol(CONFIG)
    protocol = replace(
        original,
        world=replace(original.world, events_per_epoch=16, pre_epochs=2, post_epochs=6),
        evaluation=replace(
            original.evaluation,
            intervention_magnitudes=(1.0,),
            seed_start=700,
            n_seeds=3,
        ),
        gates=replace(original.gates, bootstrap_replicates=10),
    )
    fit_bundle: dict[str, object] = {
        "development_fit": {
            "families": {
                "none": {"target_slope": 0.0, "rate": original.world.single_rate},
                "single_rate": {
                    "target_slope": original.world.target_slope,
                    "rate": original.world.single_rate,
                },
                "two_rate": {
                    "target_slope": original.world.target_slope,
                    "rate": original.world.single_rate,
                },
            },
            "standardizer": {
                "components": [
                    "market_early",
                    "market_middle",
                    "market_late",
                    "cancel_early",
                    "cancel_middle",
                    "cancel_late",
                ],
                "scale": [0.05] * 6,
            },
            "detector": {
                "target_slope": original.world.target_slope,
                "rate": original.world.single_rate,
            },
        }
    }
    shards = [run_evaluation_shard(protocol, fit_bundle, shard) for shard in range(3)]

    merged = merge_scientific_shards(protocol, fit_bundle, shards)

    assert merged["n_rows"] == 12
    assert merged["mechanics_violation_count"] == 0
    assert merged["anchor_sha256"] == shards[0]["anchor_sha256"]


def test_hardware_merge_enforces_resume_memory_and_cross_device_gates() -> None:
    protocol = load_protocol(CONFIG)
    probes = [
        {
            "worker": worker,
            "finite_losses": True,
            "finite_gradients": True,
            "exact_resume": True,
            "peak_reserved_fraction": 0.02,
            "final_loss": loss,
        }
        for worker, loss in (("v100-a", 0.1), ("v100-b", 0.10001), ("rtx2060", 0.10002))
    ]

    result = merge_hardware_probes(protocol.hardware_probe, probes)

    assert result["cross_device_pass"] is True
    assert result["hardware_pass"] is True
