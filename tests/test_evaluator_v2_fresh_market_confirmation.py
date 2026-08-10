from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pytest
import yaml

import ecomd.eval.fresh_market_confirmation as confirmation_module
from ecomd.eval.evaluator_v2 import SplitSeries
from ecomd.eval.fresh_market_confirmation import evaluate_fresh_market_confirmation

REPO_ROOT = Path(__file__).resolve().parents[1]


def _protocol() -> dict[str, Any]:
    loaded = yaml.safe_load(
        (REPO_ROOT / "configs/evaluator_v2/fresh_market_confirmation_v1.yaml").read_text()
    )
    assert isinstance(loaded, dict)
    return loaded


def _series(protocol: dict[str, Any], length: int) -> dict[str, dict[str, SplitSeries]]:
    out: dict[str, dict[str, SplitSeries]] = {}
    split_names = [
        "reference",
        "conformal_calibration",
        "confirmation",
        "report_only_guard",
        "temporal_test",
    ]
    for symbol_index, symbol in enumerate(protocol["data"]["all_symbols"]):
        rng = np.random.default_rng(10_000 + symbol_index)
        out[symbol] = {}
        for split_index, split_name in enumerate(split_names):
            returns = rng.normal(size=length) * (1.0 + 0.05 * split_index)
            volume = np.abs(returns) + 0.5 * np.abs(rng.normal(size=length))
            out[symbol][split_name] = SplitSeries(
                returns=np.asarray(returns, dtype=np.float64),
                volume=np.asarray(volume, dtype=np.float64),
            )
    return out


def test_block_count_gate_precedes_every_metric_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol = _protocol()
    series = _series(protocol, 100)

    def forbidden_estimate(name: str, block: object) -> tuple[float, None]:
        raise AssertionError(f"metric {name} ran before block eligibility")

    monkeypatch.setattr(confirmation_module, "safe_estimate", forbidden_estimate)
    result = evaluate_fresh_market_confirmation(series, protocol)
    assert not result["core_suite_qualified"]
    assert not any(
        passed
        for by_length in result["block_count_eligible"].values()
        for passed in by_length.values()
    )


def test_reduced_confirmation_smoke_runs_every_declared_metric() -> None:
    protocol = _protocol()
    protocol["blocking"]["minimum_blocks_per_gating_split_at_each_applicable_length"] = 1
    protocol["surrogates"]["replicates_per_real_block"] = 1
    result = evaluate_fresh_market_confirmation(_series(protocol, 300), protocol)
    assert set(result["cells"]) == set(protocol["metric_contract"])
    assert result["sealed_split_loaded"] is False
    assert result["model_scoring_or_training_authorized"] is False
    assert set(
        result["metric_decisions"]["volume_volatility_corr"]["applicable_symbols"]
    ) == set(protocol["data"]["instrument_groups"]["volume_etfs"])
    assert set(
        result["metric_decisions"]["gain_loss_asymmetry"]["applicable_symbols"]
    ) == set(protocol["data"]["instrument_groups"]["equity_indices"])
