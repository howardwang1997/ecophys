from copy import deepcopy
from pathlib import Path

from ecomd.research.intervention_registry import (
    load_registry,
    routing_summary,
    validate_registry,
)

REGISTRY_PATH = Path("research/theory_exploration/intervention_registry_v2.yaml")


def test_canonical_registry_is_valid_and_not_ready() -> None:
    registry = load_registry(REGISTRY_PATH)

    assert validate_registry(registry) == []
    summary = routing_summary(registry)
    assert summary["ready_for_data_contract"] is False
    assert summary["role_counts"] == {
        "development_only": 2,
        "reject": 8,
        "sealed_candidate": 0,
    }


def test_numeric_market_leaf_and_output_key_are_rejected() -> None:
    registry = load_registry(REGISTRY_PATH)
    broken = deepcopy(registry)
    cases = broken["cases"]
    assert isinstance(cases, list)
    cases[0]["outcome_estimate"] = 1.23

    errors = validate_registry(broken)
    assert any("unknown keys" in error for error in errors)
    assert any("prohibited market-output key token" in error for error in errors)
    assert any("numeric leaf" in error for error in errors)


def test_published_or_contaminated_case_cannot_be_sealed() -> None:
    registry = load_registry(REGISTRY_PATH)
    broken = deepcopy(registry)
    cases = broken["cases"]
    assert isinstance(cases, list)
    cases[0]["role"] = "sealed_candidate"

    errors = validate_registry(broken)
    assert any("published analysis" in error for error in errors)
    assert any("protocol contamination" in error for error in errors)

