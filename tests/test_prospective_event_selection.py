from copy import deepcopy
from pathlib import Path

from ecomd.research.prospective_event_selection import (
    REQUIRED_CRITERIA,
    first_qualifying_candidate,
    load_selection_contract,
    selection_summary,
    source_url_error,
    validate_selection_contract,
)

CONTRACT_PATH = Path("data/manifests/onchain_prospective_event_selection_v1.yaml")


def _candidate(
    candidate_id: str,
    *,
    platform_id: str,
    proposal_id: str,
    final_at: str,
    activation_at: str,
    audit_at: str,
    status: str,
    evidence_character: str,
) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "platform_id": platform_id,
        "official_proposal_id": proposal_id,
        "proposal_published_at": "2026-08-20T12:00:00Z",
        "final_package_at": final_at,
        "activation_at": activation_at,
        "audit_completed_at": audit_at,
        "outcome_accessed": False,
        "status": status,
        "criteria": {criterion_id: True for criterion_id in REQUIRED_CRITERIA},
        "evidence_hash": evidence_character * 64,
        "exclusion_reason": None,
    }


def test_canonical_selection_contract_is_frozen_and_empty() -> None:
    contract = load_selection_contract(CONTRACT_PATH)

    assert validate_selection_contract(contract) == []
    assert selection_summary(contract) == {
        "selection_id": "v14_onchain_independent_event",
        "status": "frozen_no_event_selected",
        "freeze_effective_at": "2026-08-14T07:00:00Z",
        "candidate_counts": {
            "audited_ineligible": 0,
            "pending_audit": 0,
            "qualified": 0,
            "selected": 0,
        },
        "selected_event_id": None,
        "outcome_blind": True,
    }


def test_outcome_access_and_effect_comparison_are_rejected() -> None:
    contract = load_selection_contract(CONTRACT_PATH)
    broken = deepcopy(contract)
    boundary = broken["access_boundary"]
    assert isinstance(boundary, dict)
    boundary["target_outcomes_opened"] = True
    boundary["candidate_effects_compared"] = True

    errors = validate_selection_contract(broken)

    assert any("target_outcomes_opened must be false" in error for error in errors)
    assert any("candidate_effects_compared must be false" in error for error in errors)


def test_only_frozen_official_metadata_hosts_are_allowed() -> None:
    assert source_url_error("https://forum.cow.fi/t/cow-dao-governance-process/27") is None
    assert source_url_error("https://gov.uniswap.org/c/governance-meta/8") is None
    assert source_url_error("https://github.com/Uniswap/v4-core") is None
    assert source_url_error("https://github.com/random-owner/private-indexer") is not None
    assert source_url_error("https://api.cow.fi/mainnet/api/v1/solver_competition/latest") is not None

    contract = load_selection_contract(CONTRACT_PATH)
    broken = deepcopy(contract)
    universe = broken["universe"]
    assert isinstance(universe, list)
    sources = universe[0]["sources"]
    assert isinstance(sources, list)
    sources[0]["outcome_url"] = "https://forum.cow.fi/t/post-treatment-dashboard/9999"
    assert any("must contain exactly" in error for error in validate_selection_contract(broken))


def test_first_final_package_is_selected_without_outcome_information() -> None:
    contract = load_selection_contract(CONTRACT_PATH)
    selected = deepcopy(contract)
    first = _candidate(
        "cow.cip_future_a",
        platform_id="cow_protocol",
        proposal_id="CIP-FUTURE-A",
        final_at="2026-09-01T12:00:00Z",
        activation_at="2026-10-01T12:00:00Z",
        audit_at="2026-09-02T12:00:00Z",
        status="selected",
        evidence_character="a",
    )
    second = _candidate(
        "uniswap.future_b",
        platform_id="uniswap_protocol",
        proposal_id="FUTURE-B",
        final_at="2026-09-03T12:00:00Z",
        activation_at="2026-10-03T12:00:00Z",
        audit_at="2026-09-04T12:00:00Z",
        status="qualified",
        evidence_character="b",
    )
    selected["candidate_registry"] = [second, first]
    selected["status"] = "event_selected"
    selection = selected["selection"]
    assert isinstance(selection, dict)
    selection.update(
        {
            "event_id": first["candidate_id"],
            "selected_at": "2026-09-02T12:00:00Z",
            "evidence_hash": first["evidence_hash"],
            "reason": "First complete qualifying package under the frozen ordering.",
        }
    )

    assert first_qualifying_candidate([second, first]) == first
    assert validate_selection_contract(selected) == []


def test_later_convenient_candidate_cannot_replace_first_qualifier() -> None:
    contract = load_selection_contract(CONTRACT_PATH)
    broken = deepcopy(contract)
    first = _candidate(
        "cow.cip_future_a",
        platform_id="cow_protocol",
        proposal_id="CIP-FUTURE-A",
        final_at="2026-09-01T12:00:00Z",
        activation_at="2026-10-01T12:00:00Z",
        audit_at="2026-09-02T12:00:00Z",
        status="qualified",
        evidence_character="a",
    )
    second = _candidate(
        "uniswap.future_b",
        platform_id="uniswap_protocol",
        proposal_id="FUTURE-B",
        final_at="2026-09-03T12:00:00Z",
        activation_at="2026-10-03T12:00:00Z",
        audit_at="2026-09-04T12:00:00Z",
        status="selected",
        evidence_character="b",
    )
    broken["candidate_registry"] = [first, second]
    broken["status"] = "event_selected"
    selection = broken["selection"]
    assert isinstance(selection, dict)
    selection.update(
        {
            "event_id": second["candidate_id"],
            "selected_at": "2026-09-04T12:00:00Z",
            "evidence_hash": second["evidence_hash"],
            "reason": "Invalid replacement.",
        }
    )

    errors = validate_selection_contract(broken)

    assert any("must equal the first qualifying candidate" in error for error in errors)
    assert any("exactly the first qualifying candidate" in error for error in errors)


def test_prefreeze_origin_and_short_lead_are_rejected_or_ineligible() -> None:
    contract = load_selection_contract(CONTRACT_PATH)
    broken = deepcopy(contract)
    candidate = _candidate(
        "cow.cip_old",
        platform_id="cow_protocol",
        proposal_id="CIP-OLD",
        final_at="2026-08-25T12:00:00Z",
        activation_at="2026-09-01T12:00:00Z",
        audit_at="2026-08-26T12:00:00Z",
        status="qualified",
        evidence_character="c",
    )
    candidate["proposal_published_at"] = "2026-08-01T12:00:00Z"
    broken["candidate_registry"] = [candidate]

    errors = validate_selection_contract(broken)

    assert any("strictly after freeze.effective_at" in error for error in errors)
    assert any("minimum_lead_time contradicts" in error for error in errors)


def test_an_earlier_pending_final_package_blocks_selection() -> None:
    contract = load_selection_contract(CONTRACT_PATH)
    broken = deepcopy(contract)
    pending = _candidate(
        "cow.pending_a",
        platform_id="cow_protocol",
        proposal_id="PENDING-A",
        final_at="2026-09-01T12:00:00Z",
        activation_at="2026-10-01T12:00:00Z",
        audit_at="2026-09-02T12:00:00Z",
        status="pending_audit",
        evidence_character="d",
    )
    pending["audit_completed_at"] = None
    pending["criteria"] = {criterion_id: None for criterion_id in REQUIRED_CRITERIA}
    pending_criteria = pending["criteria"]
    assert isinstance(pending_criteria, dict)
    pending_criteria["post_freeze_origin"] = True
    pending_criteria["minimum_lead_time"] = True
    pending["evidence_hash"] = None
    later = _candidate(
        "uniswap.future_b",
        platform_id="uniswap_protocol",
        proposal_id="FUTURE-B",
        final_at="2026-09-02T12:00:00Z",
        activation_at="2026-10-02T12:00:00Z",
        audit_at="2026-09-03T12:00:00Z",
        status="selected",
        evidence_character="e",
    )
    broken["candidate_registry"] = [pending, later]
    broken["status"] = "event_selected"
    selection = broken["selection"]
    assert isinstance(selection, dict)
    selection.update(
        {
            "event_id": later["candidate_id"],
            "selected_at": "2026-09-03T12:00:00Z",
            "evidence_hash": later["evidence_hash"],
            "reason": "Premature selection.",
        }
    )

    errors = validate_selection_contract(broken)

    assert any("earlier final package remains pending" in error for error in errors)


def test_malformed_qualified_candidate_returns_errors_instead_of_crashing() -> None:
    contract = load_selection_contract(CONTRACT_PATH)
    broken = deepcopy(contract)
    candidate = _candidate(
        "cow.malformed",
        platform_id="cow_protocol",
        proposal_id="MALFORMED",
        final_at="2026-09-01T12:00:00Z",
        activation_at="2026-10-01T12:00:00Z",
        audit_at="2026-09-02T12:00:00Z",
        status="qualified",
        evidence_character="f",
    )
    candidate["final_package_at"] = None
    broken["candidate_registry"] = [candidate]

    errors = validate_selection_contract(broken)

    assert any("audited status requires final" in error for error in errors)
