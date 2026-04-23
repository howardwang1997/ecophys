"""Smoke tests for vendor schema validation."""

from __future__ import annotations

import pandas as pd
import pytest

from ecomd.data.vendor_schemas import (
    REGISTRY,
    T1_1_MINUTE_OHLCV,
    T1_3_OPTIONS_EOD,
    validate,
)


def _good_minute_ohlcv(n_symbols: int = 600, rows_per: int = 120_000) -> pd.DataFrame:
    rows = []
    for i in range(n_symbols):
        sym = f"STK{i:04d}"
        ts = pd.date_range("2008-01-02", periods=rows_per, freq="1min", tz="UTC")
        for j in range(rows_per):
            pass
        # faster: build vectorized
        df = pd.DataFrame({
            "timestamp": ts,
            "symbol": sym,
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.5,
            "volume": pd.array([1000] * rows_per, dtype="Int64"),
        })
        rows.append(df)
    out = pd.concat(rows, ignore_index=True)
    out["symbol"] = out["symbol"].astype("string")
    # extend to 2024 for date range; easiest hack: clamp timestamps
    out.loc[out.index[-1], "timestamp"] = pd.Timestamp("2024-12-31", tz="UTC")
    return out


def test_registry_has_expected_schemas() -> None:
    assert "T1.1_us_equity_minute_ohlcv" in REGISTRY
    assert "T1.2_lob_messages" in REGISTRY
    assert "T1.2_lob_orderbook" in REGISTRY
    assert "T1.3_options_eod_chain" in REGISTRY


def test_validate_happy_path_minute_ohlcv() -> None:
    # Small synthetic frame — won't meet min_symbols/min_rows_per_symbol thresholds,
    # so we expect warnings but no schema-violation errors.
    n = 200
    df = pd.DataFrame({
        "timestamp": pd.date_range("2008-01-02", periods=n, freq="1min", tz="UTC"),
        "symbol": pd.array(["AAPL"] * n, dtype="string"),
        "open": 100.0,
        "high": 101.0,
        "low": 99.0,
        "close": 100.5,
        "volume": pd.array([1000] * n, dtype="Int64"),
    })
    rep = validate(df, T1_1_MINUTE_OHLCV)
    # Required cols present + dtypes ok → passed=True even though warnings exist
    assert rep.passed, rep.show()
    # But at least one warning due to being too small
    assert any("symbols" in w or "date" in w or "rows" in w for w in rep.warnings)


def test_validate_missing_column() -> None:
    df = pd.DataFrame({"timestamp": pd.date_range("2008-01-02", periods=100, freq="1min", tz="UTC")})
    rep = validate(df, T1_1_MINUTE_OHLCV)
    assert not rep.passed
    assert any("missing required columns" in e for e in rep.errors)


def test_validate_wrong_dtype() -> None:
    n = 100
    df = pd.DataFrame({
        "timestamp": pd.date_range("2008-01-02", periods=n, freq="1min", tz="UTC"),
        "symbol": ["AAPL"] * n,
        "open": "not-a-number",  # wrong dtype
        "high": 101.0,
        "low": 99.0,
        "close": 100.5,
        "volume": pd.array([1000] * n, dtype="Int64"),
    })
    rep = validate(df, T1_1_MINUTE_OHLCV)
    assert not rep.passed
    assert any("open" in e and "dtype" in e for e in rep.errors)


def test_validate_options_eod_missing_strike() -> None:
    df = pd.DataFrame({
        "trade_date": pd.to_datetime(["2020-01-02"] * 10),
        "underlying": ["SPX"] * 10,
        "underlying_price": [3200.0] * 10,
        "expiration": pd.to_datetime(["2020-03-20"] * 10),
        # strike missing
        "option_type": ["C"] * 10,
    })
    rep = validate(df, T1_3_OPTIONS_EOD)
    assert not rep.passed
    assert any("strike" in e for e in rep.errors)


def test_ranges_flag_outliers() -> None:
    n = 100
    df = pd.DataFrame({
        "timestamp": pd.date_range("2008-01-02", periods=n, freq="1min", tz="UTC"),
        "symbol": pd.array(["AAPL"] * n, dtype="string"),
        "open": [-5.0] + [100.0] * (n - 1),  # negative price
        "high": 101.0,
        "low": 99.0,
        "close": 100.5,
        "volume": pd.array([1000] * n, dtype="Int64"),
    })
    rep = validate(df, T1_1_MINUTE_OHLCV)
    assert rep.passed  # ranges are warnings, not errors
    assert any("outside" in w and "open" in w for w in rep.warnings)
