from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any

import pytest
import torch
import yaml

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.models.potentials import StochasticPairwisePotential
from ecomd.training.m0_contract import validate_m0_config

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "ecomd_v1" / "m0_reference.yaml"
CONFIG_SHA256 = "8e161bee28a4712e9a152539894ad6a9193d2311498fa066d24e16427e9ffa33"


def _load_config() -> dict[str, Any]:
    payload = yaml.safe_load(CONFIG_PATH.read_text())
    assert isinstance(payload, dict)
    return payload


def test_m0_config_hash_and_contract_are_frozen() -> None:
    assert hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest() == CONFIG_SHA256
    validate_m0_config(_load_config())


def test_m0_config_builds_only_the_frozen_modules() -> None:
    config = _load_config()
    torch.manual_seed(int(config["training"]["seed"]))
    simulator = EcoMDSimulator(EcoMDConfig(**config["simulator"]))

    assert sum(parameter.numel() for parameter in simulator.parameters()) == 36_541
    assert isinstance(simulator.potential.pairwise, StochasticPairwisePotential)
    assert simulator.potential.pairwise.kac_normalize
    assert simulator.global_state is not None
    assert simulator.agent_memory is None
    assert simulator.regime_gru is None
    assert simulator.moe_router is None
    assert simulator.twopop_type_idx is not None


@pytest.mark.parametrize(
    ("section", "key", "value", "message"),
    [
        ("simulator", "noise_dist", "t", "noise_dist"),
        ("simulator", "pairwise_kac_normalize", False, "pairwise_kac_normalize"),
        ("training", "state_complete", False, "state_complete"),
        ("training", "chunk_steps", 32, "chunk_steps"),
    ],
)
def test_m0_contract_rejects_scientific_mutations(
    section: str,
    key: str,
    value: object,
    message: str,
) -> None:
    config = copy.deepcopy(_load_config())
    config[section][key] = value
    with pytest.raises(ValueError, match=message):
        validate_m0_config(config)
