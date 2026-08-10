from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ecomd.data.parquet_io import read_single_parquet
from ecomd.data.yfinance_ingest import _write_shards
from ecomd.data.yfinance_provenance import (
    TemporalSplit,
    audit_daily_shards,
    canonical_payload_sha256,
    sha256_file,
    sha256_float64,
    verify_audited_daily_manifest,
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


def _write_test_manifest(data_root: Path, manifest_path: Path) -> str:
    audit = audit_daily_shards(
        data_root,
        symbol="^GSPC",
        interval="1d",
        expected_years=(2015, 2016),
        splits=(TemporalSplit("train", "fit", 2015, 2016),),
    )
    payload: dict[str, object] = {
        "dataset_id": "test_spx",
        "status": "acquired_and_audited_no_values_disclosed",
        "audit": audit,
        "policy": {
            "manifest_contains_prices_or_returns": False,
            "raw_bytes_committed_or_publicly_redistributed": False,
            "sealed_2020_not_used_for_training_or_selection": True,
            "time_split_only": True,
        },
    }
    payload["canonical_payload_sha256"] = canonical_payload_sha256(payload)
    manifest_path.write_text(json.dumps(payload, sort_keys=True) + "\n")
    return sha256_file(manifest_path)


def test_manifest_verifier_recomputes_physical_and_derived_hashes(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _write_two_years(data_root)
    manifest_path = tmp_path / "manifest.json"
    manifest_sha = _write_test_manifest(data_root, manifest_path)

    payload = verify_audited_daily_manifest(
        manifest_path,
        data_root,
        expected_manifest_sha256=manifest_sha,
        expected_dataset_id="test_spx",
    )
    assert payload["dataset_id"] == "test_spx"

    shard = data_root / "interval=1d/symbol=^GSPC/year=2015.parquet"
    frame = read_single_parquet(shard)
    frame.loc[0, "adjusted_close"] = 101.0
    frame.to_parquet(shard, index=False)
    with pytest.raises(ValueError, match="no longer matches"):
        verify_audited_daily_manifest(
            manifest_path,
            data_root,
            expected_manifest_sha256=manifest_sha,
            expected_dataset_id="test_spx",
        )


def test_manifest_verifier_rejects_manifest_hash_mismatch(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _write_two_years(data_root)
    manifest_path = tmp_path / "manifest.json"
    _write_test_manifest(data_root, manifest_path)
    with pytest.raises(ValueError, match="manifest SHA-256 mismatch"):
        verify_audited_daily_manifest(
            manifest_path,
            data_root,
            expected_manifest_sha256="0" * 64,
            expected_dataset_id="test_spx",
        )
