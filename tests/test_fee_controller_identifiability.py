from __future__ import annotations

import hashlib
import os
from pathlib import Path

import numpy as np
import pytest

from ecomd.research.fee_controller_identifiability import (
    FORMAL_EXPERIMENT_ID,
    construct_alias,
    controller_gains,
    evaluate_formal_cells,
    intervention_stack,
    load_config,
    reference_system,
    run_cell,
    seed_from_label,
    stack_diagnostics,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "experiments/151_fee_controller_identifiability_witness/config.yaml"


def test_alias_construction_matches_hand_calculation() -> None:
    config = load_config(CONFIG_PATH)
    reference = reference_system(config)
    delta = np.asarray([[0.25, 0.0], [-0.1, 0.0]], dtype=np.float64)
    gain = np.diag(np.asarray([0.02, 0.02], dtype=np.float64))
    transformed = construct_alias(reference, delta, gain)
    np.testing.assert_allclose(transformed.response, reference.response - delta, rtol=0.0, atol=0.0)
    np.testing.assert_allclose(
        transformed.latent_transition,
        reference.latent_transition + delta @ gain,
        rtol=0.0,
        atol=0.0,
    )
    expected_gamma = (
        reference.fee_to_latent
        - reference.latent_transition @ delta
        + delta @ (np.eye(2) + gain @ transformed.response)
    )
    np.testing.assert_allclose(
        transformed.fee_to_latent, expected_gamma, rtol=0.0, atol=0.0
    )


def test_reserved_development_seed_reproduces_alias_without_using_formal_seed() -> None:
    config = load_config(CONFIG_PATH)
    reference = reference_system(config)
    gains = controller_gains(config)
    seed_index = 10_000
    assert seed_index >= 128
    seed = seed_from_label(
        int(config["seed_root"]), "nonproportional", "execution_column", seed_index
    )
    expected_label = b"15120260813|nonproportional|execution_column|10000"
    assert seed == int.from_bytes(hashlib.sha256(expected_label).digest()[:8], "big")
    innovations = np.random.default_rng(seed).normal(0.0, 0.03, size=(8, 2))
    cell = run_cell(
        reference,
        np.asarray([[0.25, 0.0], [-0.1, 0.0]], dtype=np.float64),
        gains["generated_development"],
        gains["generated_nonproportional"],
        np.asarray([0.1, -0.08], dtype=np.float64),
        np.asarray([0.02, -0.015], dtype=np.float64),
        innovations,
        4,
    )
    assert cell.response_distance == pytest.approx(np.sqrt(0.25**2 + 0.1**2))
    assert cell.development_maximum_difference <= 1e-15
    assert cell.phi_residual <= 1e-17
    assert cell.gamma_residual <= 1e-17
    assert cell.intervention_maximum_divergence > 0.0
    assert cell.development_finite and cell.intervention_finite


def test_controller_geometry_separates_bpo_and_nonproportional_topologies() -> None:
    config = load_config(CONFIG_PATH)
    gains = controller_gains(config)
    bpo = stack_diagnostics(
        intervention_stack(
            gains["Prague_Osaka"], [gains["BPO1"], gains["BPO2"]]
        )
    )
    nonproportional = stack_diagnostics(
        intervention_stack(
            gains["generated_development"], [gains["generated_nonproportional"]]
        )
    )
    assert bpo["rank"] == 2
    assert float(bpo["minimum_singular_value"]) == 0.0
    assert nonproportional["rank"] == 4
    assert float(nonproportional["minimum_singular_value"]) == pytest.approx(0.012)


def test_formal_cells_refuse_execution_without_verified_freeze() -> None:
    config = load_config(CONFIG_PATH)
    assert config["experiment_id"] == FORMAL_EXPERIMENT_ID
    with pytest.raises(RuntimeError, match="freeze authorization"):
        evaluate_formal_cells(config, formal_authorized=False)


def test_import_locks_accelerators_and_threads() -> None:
    assert os.environ["CUDA_VISIBLE_DEVICES"] == "-1"
    assert os.environ["ROCR_VISIBLE_DEVICES"] == "-1"
    for variable in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        assert os.environ[variable] == "1"
