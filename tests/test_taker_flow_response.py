from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import yaml

from ecomd.physics.taker_flow_response import (
    MinuteMonth,
    evaluate_taker_flow_response,
    taker_flow_imbalance,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _protocol() -> dict[str, object]:
    return yaml.safe_load(
        (REPO_ROOT / "configs/empirical_physics/taker_flow_response_feasibility_v1.yaml").read_text()
    )


def _synthetic_month(symbol: str, month: str, symbol_index: int) -> MinuteMonth:
    day_count = 4
    minute = np.arange(1440, dtype=np.float64)
    imbalance = np.tile(0.10 * np.sin(minute / 17.0), (day_count, 1))
    log_close = np.empty((day_count, 1440), dtype=np.float64)
    shock_indices = (120, 320, 520, 720, 920, 1120, 1320)
    for day in range(day_count):
        returns = 0.0001 * np.where(np.arange(1440) % 2 == 0, 1.0, -1.0)
        for event_number, index in enumerate(shock_indices):
            sign = 1.0 if (event_number + day + symbol_index) % 2 == 0 else -1.0
            imbalance[day, index] = sign
            returns[index] += sign * 0.0005
            returns[index + 1] += sign * 0.001
            returns[index + 20] -= sign * 0.001
            returns[index + 61] -= sign * 0.0005
        log_close[day] = np.log(100.0 + 10.0 * symbol_index) + np.cumsum(returns)
    quote = np.full((day_count, 1440), 1000.0, dtype=np.float64)
    taker = quote * (imbalance + 1.0) / 2.0
    dates = tuple(f"{month}-{day:02d}" for day in range(1, day_count + 1))
    return MinuteMonth(
        symbol=symbol,
        month=month,
        dates=dates,
        close=np.exp(log_close),
        quote_volume=quote,
        taker_buy_quote=taker,
    )


def test_taker_flow_imbalance_has_explicit_trade_flow_semantics() -> None:
    result = taker_flow_imbalance(
        np.asarray([10.0, 10.0, 10.0, 0.0]),
        np.asarray([10.0, 5.0, 0.0, 0.0]),
    )
    np.testing.assert_allclose(result[:3], np.asarray([1.0, 0.0, -1.0]))
    assert np.isnan(result[3])


def test_strong_short_response_and_relaxation_passes_all_gates() -> None:
    protocol = copy.deepcopy(_protocol())
    protocol["dependence_aware_inference"]["circular_sign_null"]["replicates"] = 99
    protocol["dependence_aware_inference"]["calendar_day_bootstrap"]["replicates"] = 200
    symbols = protocol["data"]["symbols"]
    months = protocol["data"]["months"]
    series = {
        symbol: {
            month: _synthetic_month(symbol, month, symbol_index)
            for month in months
        }
        for symbol_index, symbol in enumerate(symbols)
    }
    result = evaluate_taker_flow_response(series, protocol)
    assert result["feasibility_passed"] is True
    assert all(result["primary_gate_clauses"].values())
    for month in ("2024-02", "2024-03"):
        pooled = result["evaluation_months"][month]["pooled"]
        assert pooled["early_response"] > 0.05
        assert pooled["decay_fraction_of_early"] > 0.20
        assert result["evaluation_months"][month]["circular_sign_null"]["p_value"] <= 0.05
