from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from analyze_constraint_iclr_pdebench import load_config  # noqa: E402
from merge_constraint_iclr_pdebench_factorial import (  # noqa: E402
    registered_merge_settings,
)
from run_constraint_iclr_pdebench_enforcement_cube import (  # noqa: E402
    formal_cube_seeds,
)


def test_registered_merge_requires_exact_disjoint_seed_partition() -> None:
    config = {
        "seeds": [7, 8, 9, 10],
        "formal_seed_universe": [7, 8, 9, 10],
        "formal_seed_shards": {"a": [7, 8], "b": [9, 10]},
        "benchmark_id": "pdebench_advection_beta0.4_unet_factorial_v1",
    }
    with pytest.raises(RuntimeError, match="immutable registry"):
        registered_merge_settings(config)
    config["seeds"] = list(range(7000, 7030))
    config["formal_seed_universe"] = list(range(7000, 7030))
    config["formal_seed_shards"] = {
        "a": list(range(7000, 7015)),
        "b": list(range(7015, 7030)),
    }
    assert registered_merge_settings(config) == (
        tuple(range(7000, 7030)),
        "pdebench_advection_beta0.4_unet_factorial_v1",
    )
    config["formal_seed_shards"] = {
        "a": list(range(7000, 7015)),
        "b": [7014, *range(7015, 7030)],
    }
    with pytest.raises(RuntimeError, match="overlap"):
        registered_merge_settings(config)


def test_formal_cube_uses_explicit_registered_seed_universe() -> None:
    registered = list(range(7000, 7030))
    assert formal_cube_seeds(
        {
            "benchmark_id": "pdebench_advection_beta0.4_unet_factorial_v1",
            "seeds": registered,
            "formal_seed_universe": registered,
        }
    ) == registered
    with pytest.raises(RuntimeError, match="differ"):
        formal_cube_seeds(
            {
                "benchmark_id": "pdebench_advection_beta0.4_unet_factorial_v1",
                "seeds": list(range(3000, 3030)),
                "formal_seed_universe": registered,
            }
        )


def test_frozen_unet_cube_config_resolves_registered_contract() -> None:
    config = load_config(
        Path(
            "configs/constraint_iclr/"
            "pdebench_advection_unet_enforcement_cube_20260903.yaml"
        )
    )
    assert config["benchmark_id"] == "pdebench_advection_beta0.4_unet_factorial_v1"
    assert config["model"]["architecture"] == "unet1d"
    assert formal_cube_seeds(config) == list(range(7000, 7030))
    assert config["cube"]["expected_core_records"] == 150
    assert config["cube"]["expected_trained_checkpoints"] == 120
    assert config["cube"]["expected_derived_records"] == 90
    assert len(config["evaluation"]["case_names"]) * len(
        config["evaluation"]["horizons"]
    ) == 12
