from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

from ecomd.research.open_data_development import (
    CommonObservation,
    auction_ids_sha256,
    derive_cow_auction_ids,
    load_development_contract,
    observation_violations,
    resolve_cow_anchor,
    validate_development_contract,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/manifests/open_data_development_sample_v1.yaml"


def test_frozen_development_contract_is_valid_and_unopened() -> None:
    contract = load_development_contract(CONTRACT)

    assert validate_development_contract(contract) == ()
    assert contract["stage"] == "rules_frozen_no_historical_rows_opened"
    access = cast(dict[str, object], contract["access_boundary"])
    assert access["anchor_metadata_opened"] is False
    assert access["historical_sample_rows_opened"] is False
    assert access["target_event_rows_opened"] is False


def test_cow_resolution_materializes_nested_exact_samples() -> None:
    contract = load_development_contract(CONTRACT)
    resolved = resolve_cow_anchor(
        contract,
        anchor_payload={"auctionId": 3_000_000, "solutions": [{"outcome": "discarded"}]},
        resolved_at="2026-08-14T06:53:00Z",
        response_sha256="a" * 64,
        response_bytes=1234,
        resolver_git_commit="b" * 40,
    )

    assert validate_development_contract(resolved) == ()
    cow = cast(dict[str, object], resolved["cow"])
    initial = cast(dict[str, object], cow["initial_sample"])
    expansion = cast(dict[str, object], cow["expansion_sample"])
    initial_ids = cast(list[int], initial["auction_ids"])
    expansion_ids = cast(list[int], expansion["auction_ids"])
    assert initial_ids[0] == 2_900_000
    assert initial_ids[-1] == 2_801_000
    assert set(initial_ids).issubset(expansion_ids)
    assert initial["auction_ids_sha256"] == auction_ids_sha256(initial_ids)
    anchor = cast(dict[str, object], cow["anchor"])
    assert anchor["response_sha256"] == "a" * 64
    assert "solutions" not in anchor


def test_cow_rule_rejects_invalid_range_and_contract_tampering() -> None:
    try:
        derive_cow_auction_ids(
            100,
            count=2,
            first_offset_below_anchor=99,
            stride=2,
        )
    except ValueError as error:
        assert "nonpositive" in str(error)
    else:
        raise AssertionError("nonpositive auction ID was accepted")

    contract = load_development_contract(CONTRACT)
    tampered = deepcopy(contract)
    aemo = cast(dict[str, object], tampered["aemo"])
    samples = cast(list[dict[str, object]], aemo["samples"])
    samples[0]["market_date"] = "2021-03-03"
    assert any("frozen date tuple" in error for error in validate_development_contract(tampered))


def _observation() -> CommonObservation:
    freeze = datetime(2025, 1, 1, tzinfo=UTC)
    return CommonObservation(
        system_id="synthetic",
        event_id="event-1",
        participant_id="participant-1",
        forecast_frozen_at=freeze,
        feature_as_of=freeze - timedelta(hours=1),
        action_at=freeze + timedelta(hours=1),
        outcome_at=freeze + timedelta(hours=2),
        identity_valid_from=freeze - timedelta(days=10),
        identity_valid_to=freeze + timedelta(days=10),
        action_status="submitted",
        action_value=1.0,
        failure_code=None,
    )


def test_common_observation_detects_leakage_identity_and_status_failures() -> None:
    valid = _observation()
    assert observation_violations(valid) == ()

    leaked = CommonObservation(**{**valid.__dict__, "feature_as_of": valid.outcome_at})
    stale_identity = CommonObservation(
        **{**valid.__dict__, "identity_valid_to": valid.action_at}
    )
    malformed_failure = CommonObservation(
        **{
            **valid.__dict__,
            "action_status": "failed",
            "action_value": None,
            "failure_code": None,
        }
    )
    malformed_missing = CommonObservation(
        **{
            **valid.__dict__,
            "action_status": "missing",
            "action_value": 1.0,
            "failure_code": None,
        }
    )

    assert "feature timestamp exceeds forecast freeze" in observation_violations(leaked)
    assert "participant identity is not effective at action time" in observation_violations(
        stale_identity
    )
    assert "failed action requires a failure code" in observation_violations(malformed_failure)
    assert len(observation_violations(malformed_missing)) == 2
