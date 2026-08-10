"""Deterministic provenance records for physical Yahoo Finance Parquet shards."""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .parquet_io import read_single_parquet


@dataclass(frozen=True)
class TemporalSplit:
    """A time-only split over complete calendar-year shards."""

    name: str
    role: str
    year_lo: int
    year_hi: int
    sealed: bool = False

    def validate(self) -> None:
        if not self.name or not self.role:
            raise ValueError("split name and role must be non-empty")
        if self.year_lo > self.year_hi:
            raise ValueError(f"invalid split years: {self.year_lo}>{self.year_hi}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_float64(values: np.ndarray) -> str:
    """Hash a vector using a platform-independent little-endian float64 encoding."""
    array = np.ascontiguousarray(np.asarray(values, dtype="<f8"))
    header = json.dumps(
        {"dtype": "float64-le", "shape": list(array.shape)},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(header + b"\0" + array.tobytes(order="C")).hexdigest()


def repository_state(repo_root: Path) -> dict[str, Any]:
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    return {"git_sha": sha, "clean": not status, "status_entries": status}


def canonical_payload_sha256(payload: dict[str, Any]) -> str:
    """Hash a JSON payload excluding its non-recursive self-hash field."""
    canonical = dict(payload)
    canonical.pop("canonical_payload_sha256", None)
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def audit_daily_shards(
    data_root: Path,
    *,
    symbol: str,
    interval: str,
    expected_years: tuple[int, ...],
    splits: tuple[TemporalSplit, ...],
) -> dict[str, Any]:
    """Audit exact shard coverage and hash split-adjusted-close log returns."""
    if tuple(sorted(set(expected_years))) != expected_years:
        raise ValueError("expected_years must be sorted and unique")
    if not expected_years:
        raise ValueError("expected_years must not be empty")
    for split in splits:
        split.validate()

    shard_dir = data_root / f"interval={interval}" / f"symbol={symbol}"
    paths = sorted(shard_dir.glob("year=*.parquet"))
    path_by_year = {_year_from_path(path): path for path in paths}
    if tuple(sorted(path_by_year)) != expected_years:
        raise ValueError(
            "shard-year mismatch: "
            f"expected={list(expected_years)}, actual={sorted(path_by_year)}"
        )

    file_records: list[dict[str, Any]] = []
    frames: list[pd.DataFrame] = []
    required = {"timestamp", "close", "adjusted_close", "symbol"}
    for year in expected_years:
        path = path_by_year[year]
        frame = read_single_parquet(path)
        missing = sorted(required - set(frame.columns))
        if missing:
            raise ValueError(f"{path} is missing required columns: {missing}")
        timestamps = pd.to_datetime(frame["timestamp"], utc=True)
        if frame.empty:
            raise ValueError(f"{path} is empty")
        if timestamps.dt.year.nunique() != 1 or int(timestamps.dt.year.iloc[0]) != year:
            raise ValueError(f"{path} contains timestamps outside year {year}")
        if not timestamps.is_monotonic_increasing or bool(timestamps.duplicated().any()):
            raise ValueError(f"{path} timestamps are not strictly increasing and unique")
        if set(frame["symbol"].astype(str).unique()) != {symbol}:
            raise ValueError(f"{path} contains a symbol other than {symbol}")
        prices = frame["adjusted_close"].to_numpy(dtype=np.float64)
        if not np.all(np.isfinite(prices)) or np.any(prices <= 0.0):
            raise ValueError(f"{path} has invalid adjusted_close values")
        null_counts = {str(name): int(value) for name, value in frame.isna().sum().items()}
        if any(null_counts.values()):
            raise ValueError(f"{path} has null values: {null_counts}")
        audited = frame.copy()
        audited["timestamp"] = timestamps
        audited["_partition_year"] = year
        frames.append(audited)
        file_records.append(
            {
                "relative_path": str(path.relative_to(data_root)),
                "year": year,
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
                "rows": len(frame),
                "timestamp_first_utc": timestamps.iloc[0].isoformat(),
                "timestamp_last_utc": timestamps.iloc[-1].isoformat(),
                "schema": [
                    {"name": field.name, "type": str(field.type)}
                    for field in read_single_parquet_schema(path)
                ],
                "null_counts": null_counts,
                "duplicate_timestamps": 0,
            }
        )

    combined = pd.concat(frames, ignore_index=True).sort_values("timestamp")
    timestamps = pd.to_datetime(combined["timestamp"], utc=True)
    if not timestamps.is_monotonic_increasing or bool(timestamps.duplicated().any()):
        raise ValueError("combined timestamps are not strictly increasing and unique")

    split_records: list[dict[str, Any]] = []
    for split in splits:
        mask = combined["_partition_year"].between(split.year_lo, split.year_hi)
        selected = combined.loc[mask]
        if selected.empty:
            raise ValueError(f"split {split.name} selects no observations")
        prices = selected["adjusted_close"].to_numpy(dtype=np.float64)
        returns = np.diff(np.log(prices))
        if not np.all(np.isfinite(returns)):
            raise ValueError(f"split {split.name} produces non-finite returns")
        selected_timestamps = pd.to_datetime(selected["timestamp"], utc=True)
        split_records.append(
            {
                **asdict(split),
                "price_column": "adjusted_close",
                "preprocessing": "numpy.diff(numpy.log(adjusted_close_float64))",
                "price_rows": len(prices),
                "return_rows": len(returns),
                "price_timestamp_first_utc": selected_timestamps.iloc[0].isoformat(),
                "price_timestamp_last_utc": selected_timestamps.iloc[-1].isoformat(),
                "return_float64_le_sha256": sha256_float64(returns),
            }
        )

    return {
        "symbol": symbol,
        "interval": interval,
        "expected_years": list(expected_years),
        "files": file_records,
        "global": {
            "rows": len(combined),
            "timestamp_first_utc": timestamps.iloc[0].isoformat(),
            "timestamp_last_utc": timestamps.iloc[-1].isoformat(),
            "duplicate_timestamps": 0,
        },
        "splits": split_records,
    }


def verify_audited_daily_manifest(
    manifest_path: Path,
    data_root: Path,
    *,
    expected_manifest_sha256: str,
    expected_dataset_id: str,
) -> dict[str, Any]:
    """Fail closed unless a manifest and its physical/derived data still agree."""
    actual_manifest_sha = sha256_file(manifest_path)
    if actual_manifest_sha != expected_manifest_sha256:
        raise ValueError(
            "data manifest SHA-256 mismatch: "
            f"expected={expected_manifest_sha256}, actual={actual_manifest_sha}"
        )
    loaded = json.loads(manifest_path.read_text())
    if not isinstance(loaded, dict):
        raise ValueError("data manifest must contain a JSON object")
    payload: dict[str, Any] = loaded
    if payload.get("dataset_id") != expected_dataset_id:
        raise ValueError("data manifest dataset_id mismatch")
    if payload.get("status") != "acquired_and_audited_no_values_disclosed":
        raise ValueError("data manifest status is not an audited acquisition")
    stated_payload_sha = payload.get("canonical_payload_sha256")
    actual_payload_sha = canonical_payload_sha256(payload)
    if stated_payload_sha != actual_payload_sha:
        raise ValueError(
            "data manifest canonical payload hash mismatch: "
            f"stated={stated_payload_sha}, actual={actual_payload_sha}"
        )
    policy = payload.get("policy")
    if not isinstance(policy, dict) or policy != {
        "manifest_contains_prices_or_returns": False,
        "raw_bytes_committed_or_publicly_redistributed": False,
        "sealed_2020_not_used_for_training_or_selection": True,
        "time_split_only": True,
    }:
        raise ValueError("data manifest policy is missing or changed")
    expected_audit = payload.get("audit")
    if not isinstance(expected_audit, dict):
        raise ValueError("data manifest lacks an audit object")
    expected_years_raw = expected_audit.get("expected_years")
    split_records = expected_audit.get("splits")
    if not isinstance(expected_years_raw, list) or not isinstance(split_records, list):
        raise ValueError("data manifest audit lacks years or splits")
    splits: list[TemporalSplit] = []
    for record in split_records:
        if not isinstance(record, dict):
            raise ValueError("data manifest split record must be an object")
        splits.append(
            TemporalSplit(
                name=str(record["name"]),
                role=str(record["role"]),
                year_lo=int(record["year_lo"]),
                year_hi=int(record["year_hi"]),
                sealed=bool(record["sealed"]),
            )
        )
    actual_audit = audit_daily_shards(
        data_root,
        symbol=str(expected_audit["symbol"]),
        interval=str(expected_audit["interval"]),
        expected_years=tuple(int(year) for year in expected_years_raw),
        splits=tuple(splits),
    )
    if actual_audit != expected_audit:
        raise ValueError("physical or derived data no longer matches the frozen audit")
    return payload


def read_single_parquet_schema(path: Path) -> tuple[Any, ...]:
    """Return the physical Arrow schema fields without directory inference."""
    import pyarrow.parquet as pq

    return tuple(pq.ParquetFile(path).schema_arrow)  # type: ignore[no-untyped-call]


def _year_from_path(path: Path) -> int:
    prefix = "year="
    if not path.stem.startswith(prefix):
        raise ValueError(f"unexpected shard name: {path.name}")
    try:
        return int(path.stem[len(prefix):])
    except ValueError as exc:
        raise ValueError(f"invalid shard year: {path.name}") from exc


__all__ = [
    "TemporalSplit",
    "audit_daily_shards",
    "canonical_payload_sha256",
    "repository_state",
    "sha256_file",
    "sha256_float64",
    "verify_audited_daily_manifest",
]
