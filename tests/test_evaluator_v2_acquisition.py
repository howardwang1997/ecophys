from __future__ import annotations

import json
from pathlib import Path

import yaml

from ecomd.data.yfinance_provenance import sha256_file
from scripts.acquire_evaluator_v2_free_data import (
    END,
    EXPECTED_YEARS,
    SPLITS,
    START,
    SYMBOLS,
    _canonical_sha,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_evaluator_v2_protocol_and_acquisition_constants_match() -> None:
    protocol = yaml.safe_load(
        (REPO_ROOT / "configs/evaluator_v2/feasibility_v1.yaml").read_text()
    )
    assert tuple(protocol["data"]["symbols"]) == SYMBOLS
    assert protocol["data"]["start_inclusive"] == START
    assert protocol["data"]["end_exclusive"] == END
    assert tuple(range(2005, 2025)) == EXPECTED_YEARS
    assert {split.name: [split.year_lo, split.year_hi] for split in SPLITS} == protocol[
        "data"
    ]["splits"]
    assert protocol["contract"]["current_ecomd_v1_heldout_for_threshold_selection"] == (
        "forbidden"
    )
    assert protocol["compute"] == {
        "cpu_only": True,
        "gpu_forbidden": True,
        "paid_data_forbidden": True,
        "h20_forbidden": True,
    }
    assert protocol["eligibility"]["minimum_eligible_symbols_for_volume_metric"] == 3
    assert protocol["eligibility"]["original_finiteness_splits"] == [
        "reference",
        "conformal_calibration",
        "confirmation",
        "temporal_test",
    ]
    assert protocol["eligibility"]["paired_effect"] == (
        "real_estimate_minus_within_block_surrogate_median"
    )


def test_canonical_sha_excludes_only_self_hash() -> None:
    payload = {"a": 1, "nested": {"b": 2}}
    first = _canonical_sha(payload)
    payload["canonical_payload_sha256"] = "wrong"
    assert _canonical_sha(payload) == first
    payload["nested"]["b"] = 3
    assert _canonical_sha(payload) != first
    json.dumps(payload)


def test_bound_manifest_matches_result_blind_acquisition() -> None:
    protocol = yaml.safe_load(
        (REPO_ROOT / "configs/evaluator_v2/feasibility_v1.yaml").read_text()
    )
    data_contract = protocol["data"]
    manifest_path = REPO_ROOT / data_contract["manifest_path"]
    manifest = json.loads(manifest_path.read_text())

    assert data_contract["manifest_binding_status"] == (
        "bound_after_result_blind_acquisition_before_metric_outputs"
    )
    assert _canonical_sha(manifest) == manifest["canonical_payload_sha256"]
    assert manifest["canonical_payload_sha256"] == data_contract[
        "manifest_canonical_payload_sha256"
    ]
    assert sha256_file(manifest_path) == data_contract["manifest_file_sha256"]
    assert manifest["repository"] == {
        "clean": True,
        "git_sha": data_contract["acquisition_protocol_git_sha"],
        "status_entries": [],
    }
    assert manifest["code"]["protocol_sha256"] == data_contract[
        "acquisition_protocol_sha256"
    ]
    assert manifest["policy"]["manifest_contains_prices_or_returns"] is False
    assert manifest["policy"]["sealed_2020_not_used_for_training_or_selection"] is True
