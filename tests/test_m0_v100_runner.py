from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

import pytest

from scripts.run_m0_cpu_feasibility import DEFAULT_CONFIG, _load_config
from scripts.run_m0_v100_pilot import _is_v100_32gb, _pilot_config

PILOT_CONFIG_SHA256 = "0adb0ef6a5a3e9693e9b91fe301ab1ada19360a2b58de3bc0ec2173580937a88"


def _effective_hash(config: dict[str, Any]) -> str:
    payload = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def test_v100_pilot_only_overrides_iteration_count() -> None:
    reference = _load_config(DEFAULT_CONFIG)
    pilot = _pilot_config(reference)

    assert pilot["simulator"] == reference["simulator"]
    assert pilot["training"] == {
        **reference["training"],
        "n_iters": 10,
    }
    assert _effective_hash(pilot) == PILOT_CONFIG_SHA256


@pytest.mark.parametrize(
    ("section", "key", "value", "message"),
    [
        ("compute_protocol", "v100_pilot_n_iters", 11, "10 iterations"),
        ("training", "mixed_precision", "bf16", "FP32"),
        ("simulator", "n_agents", 128, "N=256"),
    ],
)
def test_v100_pilot_rejects_protocol_mutations(
    section: str,
    key: str,
    value: object,
    message: str,
) -> None:
    reference = copy.deepcopy(_load_config(DEFAULT_CONFIG))
    reference[section][key] = value
    with pytest.raises(ValueError, match=message):
        _pilot_config(reference)


@pytest.mark.parametrize("name", ["Tesla V100-SXM2-32GB", "Tesla PG503-216"])
def test_v100_pilot_accepts_deployed_v100_names(name: str) -> None:
    assert _is_v100_32gb({"name": name, "total_memory_gib": 32.0})


def test_v100_pilot_rejects_wrong_model_or_capacity() -> None:
    assert not _is_v100_32gb({"name": "Tesla V100-SXM2-16GB", "total_memory_gib": 16.0})
    assert not _is_v100_32gb({"name": "NVIDIA H20", "total_memory_gib": 96.0})
