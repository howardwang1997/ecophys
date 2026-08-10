from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import yaml

from ecomd.data.yfinance_provenance import sha256_file
from ecomd.eval.m1_heldout_analysis import (
    classify_m1_result,
    load_heldout_trajectory,
)
from ecomd.inference.m1_heldout import validate_frozen_gate

REPO_ROOT = Path(__file__).resolve().parents[1]


def _gate_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    binding = yaml.safe_load(
        (REPO_ROOT / "configs/ecomd_v1/m1_heldout_binding.yaml").read_text()
    )
    gate = json.loads((REPO_ROOT / binding["gate"]["path"]).read_text())
    expected = {
        **binding["gate"],
        "checkpoint_sha256": binding["training"]["checkpoint_sha256"],
        "protocol_sha256": binding["training"]["protocol_sha256"],
    }
    return gate, expected


def _summaries(
    post_count: int,
    late_count: int,
    post_distance: float,
    late_distance: float,
) -> dict[str, Any]:
    return {
        "500": {"band_score": {
            "pass_count": post_count,
            "mean_normalized_distance": post_distance,
        }},
        "4000": {"band_score": {
            "pass_count": late_count,
            "mean_normalized_distance": late_distance,
        }},
    }


def test_heldout_binding_pins_gate_and_analysis_source() -> None:
    gate, expected = _gate_inputs()
    validate_frozen_gate(gate, expected)
    binding = yaml.safe_load(
        (REPO_ROOT / "configs/ecomd_v1/m1_heldout_binding.yaml").read_text()
    )
    assert sha256_file(REPO_ROOT / binding["gate"]["path"]) == binding["gate"]["sha256"]
    assert (
        sha256_file(REPO_ROOT / "ecomd/eval/m1_heldout_analysis.py")
        == binding["implementation"]["heldout_analysis_sha256"]
    )


@pytest.mark.parametrize(
    ("key", "value", "message"),
    [
        ("heldout_trajectory_count_at_fit", 1, "heldout_trajectory_count_at_fit"),
        ("calibration_input_float64_le_sha256", "wrong", "calibration_input"),
    ],
)
def test_validate_frozen_gate_rejects_mutation(key: str, value: Any, message: str) -> None:
    gate, expected = _gate_inputs()
    mutated = deepcopy(gate)
    mutated[key] = value
    with pytest.raises(ValueError, match=message):
        validate_frozen_gate(mutated, expected)


def test_validate_frozen_gate_rejects_w_star_mutation() -> None:
    gate, expected = _gate_inputs()
    mutated = deepcopy(gate)
    mutated["energy_gate"]["w_star"] = 0
    with pytest.raises(ValueError, match="W-star"):
        validate_frozen_gate(mutated, expected)


def test_load_heldout_trajectory_requires_aligned_volume(tmp_path: Path) -> None:
    path = tmp_path / "trajectory_seed811100.npz"
    np.savez_compressed(
        path,
        seed=811100,
        n_steps=8001,
        n_recorded_returns=8000,
        log_returns=np.ones(8000),
        volumes=np.ones(7999),
    )
    with pytest.raises(ValueError, match="schema mismatch"):
        load_heldout_trajectory(path, 811100)


@pytest.mark.parametrize(
    ("transfer", "post", "late", "post_distance", "late_distance", "tier", "authorized"),
    [
        (False, 8, 8, 0.2, 0.2, "stationarity_fail_stop", False),
        (True, 2, 8, 0.2, 0.2, "stop_positive_model_paper", False),
        (True, 4, 8, 0.2, 0.2, "diagnostic_only", False),
        (True, 5, 5, 0.2, 0.21, "authorize_next_stage_not_paper_claim", True),
        (True, 5, 5, 0.2, 0.23, "diagnostic_only_late_degradation", False),
    ],
)
def test_classify_m1_result_applies_frozen_rule(
    transfer: bool,
    post: int,
    late: int,
    post_distance: float,
    late_distance: float,
    tier: str,
    authorized: bool,
) -> None:
    decision = classify_m1_result(
        frozen_w_star=500,
        gate_transfer_passes=transfer,
        summaries=_summaries(post, late, post_distance, late_distance),
    )
    assert decision["tier"] == tier
    assert decision["next_stage_authorized"] is authorized
    assert decision["positive_model_paper_claim_authorized"] is False
