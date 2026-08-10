from __future__ import annotations

import json
from pathlib import Path

import yaml

from ecomd.data.yfinance_provenance import canonical_payload_sha256, sha256_file

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_regime_memory_exploratory_contract_is_source_bound_and_complete() -> None:
    protocol = yaml.safe_load(
        (REPO_ROOT / "configs/empirical_physics/regime_memory_exploratory_v1.yaml").read_text()
    )
    contract = protocol["contract"]
    assert contract["status"] == (
        "frozen_after_evaluator_v2_failures_before_any_regime_target_outputs"
    )
    source_path = REPO_ROOT / "results/evaluator_v2/fresh_market_confirmation_v1.json"
    source = json.loads(source_path.read_text())
    assert sha256_file(source_path) == contract["source_fresh_result_file_sha256"]
    assert canonical_payload_sha256(source) == contract[
        "source_fresh_result_canonical_sha256"
    ]

    for key in ("first_manifest", "second_manifest"):
        binding = protocol["data"][key]
        path = REPO_ROOT / binding["path"]
        manifest = json.loads(path.read_text())
        assert sha256_file(path) == binding["file_sha256"]
        assert canonical_payload_sha256(manifest) == binding["canonical_payload_sha256"]

    assert len(protocol["data"]["balanced_symbols"]) == 11
    assert len(protocol["data"]["volume_symbols"]) == 5
    assert set(protocol["data"]["coverage_excluded_symbols"]) == {
        "EURUSD=X",
        "^HSI",
        "^N225",
    }
    assert protocol["periods"]["return_length"] == 120
    assert protocol["periods"]["expected_fit_calendar_clusters"] == 19
    assert protocol["periods"]["expected_first_evaluation_calendar_clusters"] == 10
    assert protocol["periods"]["expected_second_evaluation_calendar_clusters"] == 7
    assert protocol["regime"]["previsible_relative_to_target"] is True
    assert protocol["regime"]["contemporaneous_regime_not_used"] is True
    assert protocol["surrogate_test"]["replicates"] == 999
    assert protocol["cluster_bootstrap"]["replicates"] == 5000
    assert protocol["primary_nomination_gate"]["every_clause_required"] is True
    assert protocol["decision"]["new_macro_time_or_independent_data_confirmation_required"] is True
    assert protocol["compute"] == {
        "cpu_only": True,
        "gpu_forbidden": True,
        "paid_data_forbidden": True,
        "h20_forbidden": True,
    }
