from copy import deepcopy
from pathlib import Path

from ecomd.research.m3m4_source_selection import (
    REQUIRED_CRITERIA,
    load_source_selection,
    source_selection_summary,
    source_url_error,
    validate_source_selection,
)

MANIFEST_PATH = Path("data/manifests/v14_m3m4_source_selection_v1.yaml")


def test_canonical_source_selection_is_valid_but_not_g1_admitted() -> None:
    selection = load_source_selection(MANIFEST_PATH)

    assert validate_source_selection(selection) == []
    assert source_selection_summary(selection) == {
        "selection_id": "v14_m3m4_replacement_source",
        "selected_candidate_id": "compound_v3",
        "authorized_stage": "zero_row_metadata_preflight",
        "g1_admitted": False,
        "selected_state_counts": {"fail": 0, "partial": 5, "pass": 5, "unresolved": 2},
        "unresolved_kill_switches": [
            "exposure_denominator",
            "licence_and_retention",
            "outcome_blind_controls",
        ],
        "outcome_blind": True,
    }


def test_access_boundary_rejects_chain_or_response_access() -> None:
    selection = load_source_selection(MANIFEST_PATH)
    broken = deepcopy(selection)
    boundary = broken["access_boundary"]
    assert isinstance(boundary, dict)
    boundary["chain_rpc_used"] = True
    boundary["realized_response_rows_opened"] = True

    errors = validate_source_selection(broken)

    assert any("chain_rpc_used must be false" in error for error in errors)
    assert any("realized_response_rows_opened must be false" in error for error in errors)


def test_selection_must_follow_complete_frozen_ordering() -> None:
    selection = load_source_selection(MANIFEST_PATH)
    broken = deepcopy(selection)
    broken["ordering"] = ["aave_v3", "compound_v3"]

    errors = validate_source_selection(broken)

    assert any("ordering must contain every candidate exactly once" in error for error in errors)
    assert any("must equal the first frozen ordering entry" in error for error in errors)


def test_candidate_must_assess_every_criterion() -> None:
    selection = load_source_selection(MANIFEST_PATH)
    broken = deepcopy(selection)
    candidates = broken["candidates"]
    assert isinstance(candidates, list)
    assessments = candidates[0]["criteria"]
    assert isinstance(assessments, dict)
    assessments.pop(next(iter(REQUIRED_CRITERIA)))

    assert any("must contain exactly" in error for error in validate_source_selection(broken))


def test_only_frozen_official_source_hosts_are_allowed() -> None:
    assert source_url_error("https://docs.compound.finance/governance/") is None
    assert source_url_error("https://github.com/aave-dao/aave-address-book") is None
    assert source_url_error("https://random-indexer.example/api/accounts") is not None
    assert source_url_error("https://github.com/random-owner/fork") is not None
