from __future__ import annotations

from pathlib import Path

import yaml

from scripts.acquire_evaluator_v2_fresh_markets import (
    END,
    EQUITY_INDICES,
    EXPECTED_YEARS,
    SPLITS,
    START,
    SYMBOLS,
    VOLUME_ETFS,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_fresh_market_protocol_and_acquisition_constants_match() -> None:
    protocol = yaml.safe_load(
        (REPO_ROOT / "configs/evaluator_v2/fresh_market_confirmation_v1.yaml").read_text()
    )
    assert tuple(protocol["data"]["instrument_groups"]["equity_indices"]) == EQUITY_INDICES
    assert tuple(protocol["data"]["instrument_groups"]["volume_etfs"]) == VOLUME_ETFS
    assert tuple(protocol["data"]["all_symbols"]) == SYMBOLS
    assert protocol["data"]["start_inclusive"] == START
    assert protocol["data"]["end_exclusive"] == END
    assert tuple(range(2005, 2025)) == EXPECTED_YEARS
    assert {split.name: [split.year_lo, split.year_hi] for split in SPLITS} == protocol[
        "data"
    ]["splits"]
    assert not set(protocol["data"]["excluded_spent_symbols"]) & set(SYMBOLS)
    assert protocol["decision"]["core_suite_required_metrics"] == [
        "autocorr_returns",
        "acf_squared_returns",
        "aggregational_gaussianity",
        "volume_volatility_corr",
    ]
    assert protocol["contract"]["model_scoring_or_training_authorization"] == (
        "forbidden"
    )
    assert protocol["compute"]["gpu_forbidden"] is True
