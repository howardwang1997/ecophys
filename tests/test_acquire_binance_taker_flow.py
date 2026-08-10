from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.acquire_binance_taker_flow_q1 import (
    EXPECTED_COLUMNS,
    parse_checksum,
    validate_kline_frame,
)


def _frame(start_ms: int, rows: int) -> pd.DataFrame:
    open_time = start_ms + np.arange(rows, dtype=np.int64) * 60_000
    open_price = 100.0 + np.arange(rows, dtype=np.float64)
    return pd.DataFrame(
        {
            "open_time": open_time,
            "open": open_price,
            "high": open_price + 1.0,
            "low": open_price - 1.0,
            "close": open_price + 0.25,
            "volume": np.full(rows, 10.0),
            "close_time": open_time + 59_999,
            "quote_volume": np.full(rows, 1000.0),
            "trade_count": np.full(rows, 20, dtype=np.int64),
            "taker_buy_base": np.full(rows, 4.0),
            "taker_buy_quote": np.full(rows, 400.0),
        },
        columns=EXPECTED_COLUMNS,
    )


def test_parse_checksum_requires_exact_filename() -> None:
    digest = "a" * 64
    assert parse_checksum(f"{digest}  BTC.zip\n".encode(), "BTC.zip") == digest
    with pytest.raises(ValueError, match="invalid checksum"):
        parse_checksum(f"{digest}  ETH.zip\n".encode(), "BTC.zip")


def test_validate_kline_frame_enforces_exact_grid_and_taker_bounds() -> None:
    start_ms = 1_704_067_200_000
    frame = _frame(start_ms, 3)
    assert validate_kline_frame(frame, start_ms=start_ms, expected_rows=3) == {
        "rows": 3,
        "first_open_time_ms": start_ms,
        "last_open_time_ms": start_ms + 120_000,
    }
    broken = frame.copy()
    broken.loc[1, "open_time"] += 1
    with pytest.raises(ValueError, match="minute grid"):
        validate_kline_frame(broken, start_ms=start_ms, expected_rows=3)
    broken = frame.copy()
    broken.loc[1, "taker_buy_quote"] = 1001.0
    with pytest.raises(ValueError, match="exceeds total"):
        validate_kline_frame(broken, start_ms=start_ms, expected_rows=3)
