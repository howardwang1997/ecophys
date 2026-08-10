from __future__ import annotations

import json
from pathlib import Path

import yaml

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


def test_canonical_sha_excludes_only_self_hash() -> None:
    payload = {"a": 1, "nested": {"b": 2}}
    first = _canonical_sha(payload)
    payload["canonical_payload_sha256"] = "wrong"
    assert _canonical_sha(payload) == first
    payload["nested"]["b"] = 3
    assert _canonical_sha(payload) != first
    json.dumps(payload)
