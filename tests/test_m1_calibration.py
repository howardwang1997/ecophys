from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
import yaml

from ecomd.inference.m1_calibration import _validate_checkpoint

REPO_ROOT = Path(__file__).resolve().parents[1]


def _inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    config = yaml.safe_load((REPO_ROOT / "configs/ecomd_v1/m0_reference.yaml").read_text())
    binding = yaml.safe_load(
        (REPO_ROOT / "configs/ecomd_v1/m1_calibration_binding.yaml").read_text()
    )
    training = binding["training"]
    metadata = {
        "git_sha": training["git_sha"],
        "m0_config_sha256": training["config_sha256"],
        "m1_protocol_sha256": training["protocol_sha256"],
        "data_manifest_sha256": training["data_manifest_sha256"],
        "train_return_float64_le_sha256": training["train_return_float64_le_sha256"],
        "train_return_rows": training["train_return_rows"],
    }
    history = [
        {
            "iter": index,
            "total_rank0": 1.0,
            "total_world_mean": 1.0,
            "acf_sim": 0.1,
            "leverage_sim": -0.1,
            "hill_sim": 3.0,
            "grad_norm": 0.5,
        }
        for index in range(600)
    ]
    checkpoint = {
        "format_version": 2,
        "iter_idx": 600,
        "world_size": 1,
        "state_complete": True,
        "sim_config": config["simulator"],
        "train_config": config["training"],
        "execution_metadata": metadata,
        "rank_runtimes": [{"history": history}],
    }
    return checkpoint, training, config


def test_calibration_checkpoint_contract_accepts_frozen_shape() -> None:
    checkpoint, training, config = _inputs()
    _validate_checkpoint(checkpoint, training, config)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("iteration", "iteration mismatch"),
        ("metadata", "execution metadata mismatch"),
        ("nonfinite", "non-finite"),
        ("zero_gradient", "zero gradient"),
    ],
)
def test_calibration_checkpoint_contract_rejects_mutations(
    mutation: str,
    message: str,
) -> None:
    checkpoint, training, config = _inputs()
    candidate = deepcopy(checkpoint)
    if mutation == "iteration":
        candidate["iter_idx"] = 599
    elif mutation == "metadata":
        candidate["execution_metadata"]["git_sha"] = "wrong"
    elif mutation == "nonfinite":
        candidate["rank_runtimes"][0]["history"][0]["total_rank0"] = float("nan")
    else:
        candidate["rank_runtimes"][0]["history"][0]["grad_norm"] = 0.0
    with pytest.raises(ValueError, match=message):
        _validate_checkpoint(candidate, training, config)
