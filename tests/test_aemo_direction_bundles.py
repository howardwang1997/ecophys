from __future__ import annotations

from typing import cast

import pytest

from ecomd.research.aemo_direction_bundles import summarize_direction_bundles


def _tables() -> dict[str, list[dict[str, str]]]:
    interval = "2026/06/16 04:05:00"
    bid_date = "2026/06/16 00:00:00"
    offer_date = "2026/06/15 12:00:00"
    base_period = {
        "INTERVAL_DATETIME": interval,
        "DUID": "BDU1",
        "BIDTYPE": "ENERGY",
        "BIDSETTLEMENTDATE": bid_date,
        "OFFERDATE": offer_date,
    }
    return {
        "BIDPEROFFER_D": [
            {**base_period, "DIRECTION": "GEN"},
            {**base_period, "DIRECTION": "LOAD"},
        ],
        "DISPATCHOFFERTRK": [
            {
                "SETTLEMENTDATE": interval,
                "DUID": "BDU1",
                "BIDTYPE": "ENERGY",
                "BIDSETTLEMENTDATE": bid_date,
                "BIDOFFERDATE": offer_date,
            }
        ],
        "DISPATCHLOAD": [
            {
                "SETTLEMENTDATE": interval,
                "RUNNO": "1",
                "INTERVENTION": "0",
                "DUID": "BDU1",
                "TOTALCLEARED": "-12.5",
            }
        ],
        "DUDETAILSUMMARY": [
            {
                "DUID": "BDU1",
                "START_DATE": "2020/01/01 00:00:00",
                "END_DATE": "2030/01/01 00:00:00",
                "DISPATCHTYPE": "BIDIRECTIONAL",
                "DISPATCHSUBTYPE": "BATTERY",
            }
        ],
    }


def _frozen_summary(*, ambiguous_count: int = 1) -> dict[str, object]:
    return {
        "joins": {
            "tracker_count": 1,
            "tracker_period_ambiguous_count": ambiguous_count,
        }
    }


def test_exact_gen_load_bundle_is_described_without_resolution() -> None:
    summary = summarize_direction_bundles(
        _tables(),
        _frozen_summary(),
        analyzer_git_commit="a" * 40,
        generated_at="2026-08-15T04:00:00Z",
        frozen_summary_sha256="b" * 64,
    )

    structure = cast(dict[str, object], summary["candidate_structure"])
    flags = cast(dict[str, bool], summary["diagnostic_flags"])
    context = cast(dict[str, object], summary["realized_dispatch_context"])
    signs = cast(dict[str, dict[str, int]], context["totalcleared_sign_by_bid_type"])
    assert structure["candidate_cardinality"] == {"2": 1}
    assert structure["direction_sets"] == {"GEN|LOAD": 1}
    assert flags["all_ambiguous_are_gen_load_pairs"] is True
    assert flags["all_ambiguous_identities_are_bidirectional"] is True
    assert signs == {"ENERGY": {"NEGATIVE": 1}}
    boundary = cast(dict[str, bool], summary["interpretation_boundary"])
    assert boundary["e1a_failure_overridden"] is False
    assert context["sign_is_descriptive_not_an_action_selector"] is True


def test_repeated_same_direction_is_flagged() -> None:
    tables = _tables()
    tables["BIDPEROFFER_D"][1]["DIRECTION"] = "GEN"

    summary = summarize_direction_bundles(
        tables,
        _frozen_summary(),
        analyzer_git_commit="a" * 40,
        generated_at="2026-08-15T04:00:00Z",
        frozen_summary_sha256="b" * 64,
    )

    structure = cast(dict[str, object], summary["candidate_structure"])
    flags = cast(dict[str, bool], summary["diagnostic_flags"])
    assert structure["ambiguous_duplicate_direction_count"] == 1
    assert flags["all_ambiguous_are_gen_load_pairs"] is False


def test_diagnostic_must_reproduce_frozen_multiplicity() -> None:
    with pytest.raises(ValueError, match="does not reproduce"):
        summarize_direction_bundles(
            _tables(),
            _frozen_summary(ambiguous_count=0),
            analyzer_git_commit="a" * 40,
            generated_at="2026-08-15T04:00:00Z",
            frozen_summary_sha256="b" * 64,
        )
