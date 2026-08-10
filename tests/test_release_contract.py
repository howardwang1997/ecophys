from __future__ import annotations

import pytest

from ecomd.training.train_distributed import validate_release_training_contract


def _valid_configs() -> tuple[dict[str, object], dict[str, object]]:
    simulator = {
        "jump_legacy_train_proxy": False,
        "bptt_checkpoint_every": 0,
        "bptt_custom_function": False,
    }
    training = {
        "release_contract_version": 1,
        "state_complete": True,
        "persistent_state": True,
    }
    return simulator, training


def test_release_training_contract_accepts_complete_state() -> None:
    simulator, training = _valid_configs()
    validate_release_training_contract(simulator, training)


@pytest.mark.parametrize(
    ("section", "key", "value", "message"),
    [
        ("training", "state_complete", False, "state_complete"),
        ("training", "persistent_state", False, "persistent_state"),
        ("training", "release_contract_version", 2, "release_contract_version"),
        ("simulator", "jump_legacy_train_proxy", True, "jump_legacy_train_proxy"),
        ("simulator", "bptt_checkpoint_every", 4, "bptt_checkpoint_every"),
        ("simulator", "bptt_custom_function", True, "bptt_custom_function"),
    ],
)
def test_release_training_contract_rejects_unsafe_configuration(
    section: str,
    key: str,
    value: object,
    message: str,
) -> None:
    simulator, training = _valid_configs()
    target = simulator if section == "simulator" else training
    target[key] = value

    with pytest.raises(ValueError, match=message):
        validate_release_training_contract(simulator, training)
