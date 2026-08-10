from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import yaml

from ecomd.physics.regime_memory import (
    RegimeRow,
    evaluate_regime_memory,
    expand_period_range,
    make_half_year_block,
    previous_period,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _protocol() -> dict[str, object]:
    return yaml.safe_load(
        (REPO_ROOT / "configs/empirical_physics/regime_memory_exploratory_v1.yaml").read_text()
    )


def test_period_range_and_predecessor_are_calendar_exact() -> None:
    assert expand_period_range(["2005H2", "2006H2"]) == (
        "2005H2",
        "2006H1",
        "2006H2",
    )
    assert previous_period("2006H1") == "2005H2"
    assert previous_period("2006H2") == "2006H1"


def test_half_year_block_uses_only_the_earliest_declared_rows() -> None:
    log_prices = np.cumsum(np.linspace(-0.02, 0.03, 130))
    prices = np.exp(log_prices)
    volume = np.linspace(100.0, 1000.0, 130)
    block = make_half_year_block(
        "TEST",
        "2010H1",
        prices,
        volume,
        return_length=120,
    )
    np.testing.assert_allclose(block.returns, np.diff(log_prices[:121]))
    np.testing.assert_allclose(block.volume, volume[1:121])
    assert block.returns.size == 120


def test_strong_previsible_common_slope_passes_exploratory_gate() -> None:
    protocol = copy.deepcopy(_protocol())
    protocol["surrogate_test"]["replicates"] = 99
    protocol["cluster_bootstrap"]["replicates"] = 200
    balanced = protocol["data"]["balanced_symbols"]
    volume_symbols = set(protocol["data"]["volume_symbols"])
    era_periods = {
        "fit": expand_period_range(protocol["periods"]["fit_target_period"]),
        "evaluation_1": expand_period_range(
            protocol["periods"]["first_evaluation_period"]
        ),
        "evaluation_2": expand_period_range(
            protocol["periods"]["second_evaluation_period"]
        ),
    }
    rows: list[RegimeRow] = []
    global_periods = [period for values in era_periods.values() for period in values]
    period_index = {period: index for index, period in enumerate(global_periods)}
    for symbol_index, symbol in enumerate(balanced):
        for era, periods in era_periods.items():
            for period in periods:
                index = period_index[period]
                predictor = -5.0 + 0.06 * index + 0.01 * symbol_index
                noise = 0.002 * np.sin(0.7 * index + symbol_index)
                targets = {
                    "acf_squared_returns": 0.01 * symbol_index + 0.35 * predictor + noise,
                    "autocorr_returns": 0.03 + 0.002 * np.cos(index + symbol_index),
                }
                if symbol in volume_symbols:
                    targets["volume_volatility_corr"] = (
                        0.02 * symbol_index + 0.20 * predictor + noise
                    )
                rows.append(
                    RegimeRow(
                        symbol=symbol,
                        period=period,
                        era=era,
                        lagged_log_realized_volatility=predictor,
                        targets=targets,
                    )
                )
    result = evaluate_regime_memory(tuple(rows), protocol)
    assert result["primary_nominated"] is True
    assert all(result["primary_gate_clauses"].values())
    primary = result["targets"]["acf_squared_returns"]
    assert primary["training_common_regime_slope"] > 0.0
    assert primary["summary"]["relative_mse_reduction"] > 0.95
    assert primary["permutation_test"]["p_value"] <= 0.05
