from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from ecomd.eval.m1_contract import validate_m1_protocol
from ecomd.inference.seed_manifest import load_seed_file

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = REPO_ROOT / "configs/ecomd_v1/m1_stationarity_screen.yaml"


def _payload() -> dict[str, object]:
    payload = yaml.safe_load(PROTOCOL_PATH.read_text())
    assert isinstance(payload, dict)
    return payload


def test_frozen_m1_protocol_passes() -> None:
    validate_m1_protocol(_payload(), REPO_ROOT)


@pytest.mark.parametrize(
    ("section", "key", "value"),
    [
        ("training", "final_iter", 599),
        ("rollout", "usable_returns", 7999),
        ("energy_gate", "max_w_star", 3500),
        ("scoring", "fixed_length", 3999),
        ("decision", "stop_positive_model_paper_if_post_or_late_pass_count_at_most", 1),
        ("compute", "h20_forbidden", False),
    ],
)
def test_frozen_m1_protocol_rejects_mutations(
    section: str,
    key: str,
    value: object,
) -> None:
    payload = deepcopy(_payload())
    nested = payload[section]
    assert isinstance(nested, dict)
    nested[key] = value
    with pytest.raises(ValueError):
        validate_m1_protocol(payload, REPO_ROOT)


def test_frozen_m1_protocol_rejects_seed_reassignment() -> None:
    payload = deepcopy(_payload())
    rollout = payload["rollout"]
    assert isinstance(rollout, dict)
    shards = rollout["node_shards"]
    assert isinstance(shards, dict)
    node = shards["v100_a"]
    assert isinstance(node, dict)
    node["calibration"][0] = 999
    with pytest.raises(ValueError, match="do not partition"):
        validate_m1_protocol(payload, REPO_ROOT)


@pytest.mark.parametrize(
    ("split", "node", "filename"),
    [
        ("calibration", "v100_a", "m1_calibration_v100a_seeds.json"),
        ("calibration", "v100_b", "m1_calibration_v100b_seeds.json"),
        ("heldout", "v100_a", "m1_heldout_v100a_seeds.json"),
        ("heldout", "v100_b", "m1_heldout_v100b_seeds.json"),
    ],
)
def test_rollout_seed_files_match_frozen_node_shards(
    split: str,
    node: str,
    filename: str,
) -> None:
    payload = _payload()
    rollout = payload["rollout"]
    assert isinstance(rollout, dict)
    shards = rollout["node_shards"]
    assert isinstance(shards, dict)
    node_payload = shards[node]
    assert isinstance(node_payload, dict)
    expected = node_payload[split]
    assert load_seed_file(REPO_ROOT / "configs/ecomd_v1" / filename) == expected
