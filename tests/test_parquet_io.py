from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ecomd.data.parquet_io import read_single_parquet
from ecomd.training.train_distributed import load_yfinance_daily_any_rank


def _write_partitioned_yfinance_file(repo_root: Path) -> Path:
    path = (
        repo_root
        / "data"
        / "sample"
        / "yfinance"
        / "interval=1d"
        / "symbol=^GSPC"
        / "year=2015.parquet"
    )
    path.parent.mkdir(parents=True)
    frame = pd.DataFrame(
        {
            "timestamp": pd.date_range("2015-01-02", periods=3, tz="UTC"),
            "close": [100.0, 110.0, 121.0],
            "adjusted_close": [100.0, 120.0, 180.0],
            "symbol": pd.Series(["^GSPC"] * 3, dtype="string"),
        }
    )
    frame.to_parquet(path, index=False)
    return path


def test_single_file_reader_ignores_conflicting_hive_keys(tmp_path: Path) -> None:
    path = _write_partitioned_yfinance_file(tmp_path)
    frame = read_single_parquet(path)

    assert list(frame["symbol"]) == ["^GSPC"] * 3
    assert list(frame["adjusted_close"]) == [100.0, 120.0, 180.0]


def test_training_loader_uses_adjusted_close_and_year_filter(tmp_path: Path) -> None:
    _write_partitioned_yfinance_file(tmp_path)
    returns = load_yfinance_daily_any_rank(
        tmp_path,
        "^GSPC",
        year_lo=2015,
        year_hi=2015,
    )

    np.testing.assert_allclose(returns, np.diff(np.log([100.0, 120.0, 180.0])))
