from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ecomd.data.yfinance_ingest import _write_shards
from ecomd.data.yfinance_provenance import (
    TemporalSplit,
    audit_daily_shards,
    sha256_float64,
)


def _write_two_years(root: Path) -> None:
    frame = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                ["2015-01-02", "2015-12-31", "2016-01-04", "2016-12-30"],
                utc=True,
            ),
            "open": [99.0, 109.0, 119.0, 129.0],
            "high": [101.0, 111.0, 121.0, 131.0],
            "low": [98.0, 108.0, 118.0, 128.0],
            "close": [100.0, 110.0, 120.0, 130.0],
            "adjusted_close": [100.0, 110.0, 120.0, 130.0],
            "volume": [1, 2, 3, 4],
            "symbol": ["^GSPC"] * 4,
        }
    )
    _write_shards(frame, "^GSPC", "1d", root)


def test_daily_audit_records_exact_files_and_derived_hash(tmp_path: Path) -> None:
    _write_two_years(tmp_path)
    audit = audit_daily_shards(
        tmp_path,
        symbol="^GSPC",
        interval="1d",
        expected_years=(2015, 2016),
        splits=(TemporalSplit("train", "fit", 2015, 2016),),
    )

    assert [record["year"] for record in audit["files"]] == [2015, 2016]
    assert audit["global"]["rows"] == 4
    split = audit["splits"][0]
    assert split["return_rows"] == 3
    expected = np.diff(np.log(np.array([100.0, 110.0, 120.0, 130.0])))
    assert split["return_float64_le_sha256"] == sha256_float64(expected)
    assert "returns" not in split


def test_daily_audit_rejects_unexpected_or_missing_years(tmp_path: Path) -> None:
    _write_two_years(tmp_path)
    with pytest.raises(ValueError, match="shard-year mismatch"):
        audit_daily_shards(
            tmp_path,
            symbol="^GSPC",
            interval="1d",
            expected_years=(2015,),
            splits=(TemporalSplit("train", "fit", 2015, 2015),),
        )
