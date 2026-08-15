from copy import deepcopy
from pathlib import Path

import pytest

from ecomd.research.compound_exposure_design import (
    compute_exposure_residuals,
    load_exposure_control_design,
    validate_design_evidence,
    validate_exposure_control_design,
)

MANIFEST_PATH = Path("data/manifests/compound_v3_exposure_control_design_v1.yaml")


def test_canonical_zero_row_design_and_evidence_are_valid() -> None:
    manifest = load_exposure_control_design(MANIFEST_PATH)

    assert validate_exposure_control_design(manifest) == []
    assert validate_design_evidence(manifest, Path.cwd()) == []
    access = manifest["access_boundary"]
    assert isinstance(access, dict)
    assert access["official_code_blobs_opened"] is True
    assert access["governance_payload_rows_opened"] is False
    assert access["account_state_rows_opened"] is False
    assert access["participant_action_rows_opened"] is False
    assert access["gpu_used"] is False


def test_exact_aggregate_residuals_certify_enumerated_position_set() -> None:
    residuals = compute_exposure_residuals(
        {"alice": 120, "bob": -70, "carol": 0},
        {
            "alice": {"weth": 2, "wbtc": 0},
            "bob": {"weth": 3, "wbtc": 5},
            "carol": {"weth": 0, "wbtc": 1},
        },
        total_supply_base=120,
        total_borrow_base=70,
        totals_collateral={"weth": 5, "wbtc": 6},
    )

    assert residuals.complete is True
    assert residuals.supply_base == 0
    assert residuals.borrow_base == 0
    assert residuals.collateral == {"wbtc": 0, "weth": 0}


def test_omitted_or_overcounted_state_fails_without_tolerance() -> None:
    omitted = compute_exposure_residuals(
        {"alice": 120, "bob": -70},
        {"alice": {"weth": 2}, "bob": {"weth": 3}},
        total_supply_base=125,
        total_borrow_base=71,
        totals_collateral={"weth": 7},
    )
    overcounted = compute_exposure_residuals(
        {"alice": 126, "bob": -72},
        {"alice": {"weth": 4}, "bob": {"weth": 4}},
        total_supply_base=125,
        total_borrow_base=71,
        totals_collateral={"weth": 7},
    )

    assert omitted.complete is False
    assert (omitted.supply_base, omitted.borrow_base, omitted.collateral["weth"]) == (5, 1, 2)
    assert overcounted.complete is False
    assert (overcounted.supply_base, overcounted.borrow_base, overcounted.collateral["weth"]) == (
        -1,
        -1,
        -1,
    )


def test_residual_computation_rejects_invalid_collateral_domain() -> None:
    with pytest.raises(ValueError, match="principal record"):
        compute_exposure_residuals(
            {"alice": 1},
            {"bob": {"weth": 1}},
            total_supply_base=1,
            total_borrow_base=0,
            totals_collateral={"weth": 1},
        )
    with pytest.raises(ValueError, match="unknown collateral assets"):
        compute_exposure_residuals(
            {"alice": 1},
            {"alice": {"wbtc": 1}},
            total_supply_base=1,
            total_borrow_base=0,
            totals_collateral={"weth": 0},
        )
    with pytest.raises(ValueError, match="nonnegative integers"):
        compute_exposure_residuals(
            {"alice": 1},
            {"alice": {"weth": -1}},
            total_supply_base=1,
            total_borrow_base=0,
            totals_collateral={"weth": 0},
        )


def test_design_rejects_row_access_clock_relaxation_and_event_only_claim() -> None:
    manifest = load_exposure_control_design(MANIFEST_PATH)
    broken = deepcopy(manifest)
    access = broken["access_boundary"]
    treatment = broken["treatment_contract"]
    action = broken["action_contract"]
    assert isinstance(access, dict)
    assert isinstance(treatment, dict)
    assert isinstance(action, dict)
    access["account_state_rows_opened"] = True
    access["gpu_used"] = True
    treatment["operative_clock"] = "proposal_created"
    action["logged_event_only_panel_is_complete_claim"] = True
    action["require_complete_successful_call_traces"] = False

    errors = validate_exposure_control_design(broken)

    assert any("account_state_rows_opened must be false" in error for error in errors)
    assert any("gpu_used must be false" in error for error in errors)
    assert any("operative_clock must equal comet_proxy_upgraded_log" in error for error in errors)
    assert any("logged_event_only_panel_is_complete_claim must be false" in error for error in errors)
    assert any("require_complete_successful_call_traces must be true" in error for error in errors)
