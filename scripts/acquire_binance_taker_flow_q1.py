"""Acquire and audit frozen Binance Q1-2024 1m bars without response metrics."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd
import requests
import yaml

from ecomd.data.binance_ingest import _parse_zip
from ecomd.data.yfinance_provenance import (
    canonical_payload_sha256,
    repository_state,
    sha256_file,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOL = (
    REPO_ROOT / "configs/empirical_physics/taker_flow_response_feasibility_v1.yaml"
)
EXPECTED_COLUMNS = (
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_volume",
    "trade_count",
    "taker_buy_base",
    "taker_buy_quote",
)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def parse_checksum(raw: bytes, expected_filename: str) -> str:
    """Parse one official sha256sum-style CHECKSUM file."""
    text = raw.decode("utf-8").strip()
    match = re.fullmatch(r"([0-9a-fA-F]{64})\s+\*?([^\s]+)", text)
    if match is None or match.group(2) != expected_filename:
        raise ValueError(f"invalid checksum record for {expected_filename}: {text!r}")
    return match.group(1).lower()


def validate_kline_frame(
    frame: pd.DataFrame,
    *,
    start_ms: int,
    expected_rows: int,
) -> dict[str, int]:
    """Validate one exact, millisecond-resolution UTC minute grid."""
    if tuple(frame.columns) != EXPECTED_COLUMNS:
        raise ValueError("kline schema differs from the frozen registry")
    if len(frame) != expected_rows:
        raise ValueError(f"row count {len(frame)} differs from expected {expected_rows}")
    if frame.isna().any().any():
        raise ValueError("kline frame contains missing values")
    open_time = frame["open_time"].to_numpy(dtype=np.int64)
    expected_open = start_ms + np.arange(expected_rows, dtype=np.int64) * 60_000
    if not np.array_equal(open_time, expected_open):
        raise ValueError("open_time does not form the exact expected minute grid")
    close_time = frame["close_time"].to_numpy(dtype=np.int64)
    if not np.array_equal(close_time, open_time + 59_999):
        raise ValueError("close_time differs from open_time + 59999 ms")
    if int(np.max(open_time)) >= 10**15:
        raise ValueError("2024 timestamps appear to use microseconds rather than milliseconds")
    numeric_columns = (
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_volume",
        "taker_buy_base",
        "taker_buy_quote",
    )
    numeric = frame.loc[:, numeric_columns].to_numpy(dtype=np.float64)
    if not np.all(np.isfinite(numeric)):
        raise ValueError("kline numeric values are nonfinite")
    for column in ("open", "high", "low", "close"):
        if np.any(frame[column].to_numpy(dtype=np.float64) <= 0.0):
            raise ValueError(f"{column} contains a nonpositive value")
    for column in ("volume", "quote_volume", "taker_buy_base", "taker_buy_quote"):
        if np.any(frame[column].to_numpy(dtype=np.float64) < 0.0):
            raise ValueError(f"{column} contains a negative value")
    open_price = frame["open"].to_numpy(dtype=np.float64)
    high = frame["high"].to_numpy(dtype=np.float64)
    low = frame["low"].to_numpy(dtype=np.float64)
    close = frame["close"].to_numpy(dtype=np.float64)
    if np.any(high < np.maximum(open_price, close)) or np.any(
        low > np.minimum(open_price, close)
    ):
        raise ValueError("OHLC ordering is invalid")
    quote = frame["quote_volume"].to_numpy(dtype=np.float64)
    taker_quote = frame["taker_buy_quote"].to_numpy(dtype=np.float64)
    tolerance = np.maximum(1e-12, np.abs(quote) * 1e-12)
    if np.any(taker_quote > quote + tolerance):
        raise ValueError("taker-buy quote volume exceeds total quote volume")
    trades = frame["trade_count"].to_numpy(dtype=np.int64)
    if np.any(trades < 0):
        raise ValueError("trade_count contains a negative value")
    return {
        "rows": len(frame),
        "first_open_time_ms": int(open_time[0]),
        "last_open_time_ms": int(open_time[-1]),
    }


def _download(session: requests.Session, url: str, *, retries: int = 4) -> bytes:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=120)
            response.raise_for_status()
            return bytes(response.content)
        except Exception as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"failed to download {url}: {last_error}")


def _download_checked_archive(
    session: requests.Session,
    url: str,
    destination: Path,
) -> tuple[bytes, dict[str, Any]]:
    filename = url.rsplit("/", maxsplit=1)[-1]
    checksum_url = f"{url}.CHECKSUM"
    checksum_raw = _download(session, checksum_url)
    expected_sha = parse_checksum(checksum_raw, filename)
    archive_raw = _download(session, url)
    actual_sha = _sha256_bytes(archive_raw)
    if actual_sha != expected_sha:
        raise ValueError(f"official checksum mismatch for {filename}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(archive_raw)
    checksum_path = destination.with_name(destination.name + ".CHECKSUM")
    checksum_path.write_bytes(checksum_raw)
    return archive_raw, {
        "url": url,
        "checksum_url": checksum_url,
        "relative_path": str(destination),
        "bytes": len(archive_raw),
        "sha256": actual_sha,
        "official_checksum_sha256": expected_sha,
        "checksum_file_sha256": _sha256_bytes(checksum_raw),
    }


def _month_start_ms(month: str) -> int:
    return int(pd.Timestamp(f"{month}-01", tz="UTC").timestamp() * 1000)


def _day_start_ms(day: str) -> int:
    return int(pd.Timestamp(day, tz="UTC").timestamp() * 1000)


def acquire(
    *,
    protocol_path: Path,
    data_root: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    """Download exact frozen archives, crosscheck daily/monthly rows, and bind provenance."""
    if manifest_path.exists():
        raise FileExistsError(f"refusing to overwrite manifest: {manifest_path}")
    temporary = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    if temporary.exists():
        raise FileExistsError(f"refusing to overwrite stale temporary: {temporary}")
    if data_root.exists() and any(data_root.iterdir()):
        raise FileExistsError(f"data root must be absent or empty: {data_root}")
    state = repository_state(REPO_ROOT)
    if not state["clean"]:
        raise RuntimeError("formal acquisition requires a clean worktree")
    upstream = subprocess.run(
        ["git", "rev-parse", "@{u}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if upstream != state["git_sha"]:
        raise RuntimeError("acquisition source commit must already be pushed")
    protocol = _load_yaml(protocol_path)
    data = _mapping(protocol["data"], "data")
    validation = _mapping(protocol["archive_validation"], "archive_validation")
    if data["manifest_binding_status"] != "pending_result_blind_acquisition":
        raise ValueError("protocol is not in the pre-acquisition state")
    if data["manifest_path"] != str(manifest_path.relative_to(REPO_ROOT)):
        raise ValueError("manifest path differs from the frozen contract")
    symbols = [str(value) for value in cast(list[object], data["symbols"])]
    months = [str(value) for value in cast(list[object], data["months"])]
    expected_rows = {
        str(month): int(rows)
        for month, rows in _mapping(data["expected_rows"], "expected_rows").items()
    }
    crosscheck_dates = [
        str(value)
        for value in cast(
            list[object], validation["daily_monthly_exact_crosscheck_dates"]
        )
    ]
    if {value[:7] for value in crosscheck_dates} != set(months):
        raise ValueError("crosscheck dates do not cover exactly the frozen months")
    base_url = str(data["base_url"]).rstrip("/")
    monthly_template = str(data["monthly_url_template"])
    data_root.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "ecophys-research/0.1"
    monthly_frames: dict[tuple[str, str], pd.DataFrame] = {}
    monthly_records: list[dict[str, Any]] = []
    daily_records: list[dict[str, Any]] = []
    expected_files: set[Path] = set()

    for symbol in symbols:
        for month in months:
            relative_url = monthly_template.format(symbol=symbol, month=month)
            url = f"{base_url}/{relative_url}"
            filename = url.rsplit("/", maxsplit=1)[-1]
            destination = data_root / "monthly" / f"symbol={symbol}" / filename
            raw, record = _download_checked_archive(session, url, destination)
            frame = _parse_zip(raw)
            audit = validate_kline_frame(
                frame,
                start_ms=_month_start_ms(month),
                expected_rows=expected_rows[month],
            )
            record.update({"symbol": symbol, "month": month, **audit})
            record["relative_path"] = str(destination.relative_to(data_root))
            record["checksum_relative_path"] = str(
                destination.with_name(destination.name + ".CHECKSUM").relative_to(
                    data_root
                )
            )
            monthly_records.append(record)
            monthly_frames[(symbol, month)] = frame
            expected_files.update(
                {destination, destination.with_name(destination.name + ".CHECKSUM")}
            )

    for symbol in symbols:
        for day in crosscheck_dates:
            filename = f"{symbol}-1m-{day}.zip"
            url = (
                f"{base_url}/spot/daily/klines/{symbol}/1m/{filename}"
            )
            destination = data_root / "daily_crosscheck" / f"symbol={symbol}" / filename
            raw, record = _download_checked_archive(session, url, destination)
            daily = _parse_zip(raw)
            audit = validate_kline_frame(
                daily,
                start_ms=_day_start_ms(day),
                expected_rows=1440,
            )
            monthly = monthly_frames[(symbol, day[:7])]
            start_ms = _day_start_ms(day)
            monthly_slice = monthly.loc[
                (monthly["open_time"] >= start_ms)
                & (monthly["open_time"] < start_ms + 86_400_000)
            ].reset_index(drop=True)
            pd.testing.assert_frame_equal(
                daily.reset_index(drop=True),
                monthly_slice,
                check_dtype=False,
                check_exact=True,
            )
            record.update(
                {
                    "symbol": symbol,
                    "date": day,
                    "monthly_daily_exact_all_columns": True,
                    **audit,
                }
            )
            record["relative_path"] = str(destination.relative_to(data_root))
            record["checksum_relative_path"] = str(
                destination.with_name(destination.name + ".CHECKSUM").relative_to(
                    data_root
                )
            )
            daily_records.append(record)
            expected_files.update(
                {destination, destination.with_name(destination.name + ".CHECKSUM")}
            )
    actual_files = {path for path in data_root.rglob("*") if path.is_file()}
    if actual_files != expected_files:
        raise ValueError("physical acquisition file set differs from expected")
    payload: dict[str, Any] = {
        "schema_version": 1,
        "dataset_id": "binance_spot_1m_q1_2024_taker_flow",
        "acquired_at_utc": _utc_now(),
        "repository": {**state, "upstream_sha": upstream},
        "code": {
            "protocol_path": str(protocol_path.relative_to(REPO_ROOT)),
            "protocol_sha256": sha256_file(protocol_path),
            "acquisition_script_sha256": sha256_file(Path(__file__).resolve()),
            "binance_parser_sha256": sha256_file(
                REPO_ROOT / "ecomd/data/binance_ingest.py"
            ),
        },
        "source": {
            "provider": data["provider"],
            "official_documentation": data["official_documentation"],
            "base_url": base_url,
            "market": data["market"],
            "data_type": data["data_type"],
            "interval": data["interval"],
        },
        "policy": {
            "universe_and_dates_frozen_before_acquisition": True,
            "official_checksum_required": True,
            "monthly_daily_crosscheck_required": True,
            "manifest_contains_price_flow_or_response_values": False,
            "raw_bytes_committed_or_publicly_redistributed": False,
            "response_metrics_computed_during_acquisition": False,
        },
        "monthly_archives": monthly_records,
        "daily_crosschecks": daily_records,
        "summary": {
            "monthly_archives": len(monthly_records),
            "daily_crosscheck_archives": len(daily_records),
            "physical_files_including_checksums": len(actual_files),
            "all_official_checksums_passed": True,
            "all_monthly_daily_crosschecks_passed": True,
        },
    }
    payload["canonical_payload_sha256"] = canonical_payload_sha256(payload)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(manifest_path)
    return payload


def _mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return cast(dict[str, Any], value)


def _load_yaml(path: Path) -> dict[str, Any]:
    return _mapping(yaml.safe_load(path.read_text()), str(path))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT
        / "data/manifests/binance_spot_1m_q1_2024_taker_flow.json",
    )
    args = parser.parse_args()
    payload = acquire(
        protocol_path=args.protocol.resolve(),
        data_root=args.data_root.resolve(),
        manifest_path=args.manifest.resolve(),
    )
    print(
        json.dumps(
            {
                "canonical_payload_sha256": payload["canonical_payload_sha256"],
                "dataset_id": payload["dataset_id"],
                "manifest": str(args.manifest.resolve()),
                "summary": payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
