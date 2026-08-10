"""Download Binance public historical klines from data.binance.vision.

Pulls monthly ZIPs of 1m (default) klines per symbol and converts to Parquet.
Free, no API key, no rate limit on the static host.

Usage:
    conda run -n ecophys python -m ecomd.data.binance_ingest \\
        --symbols BTCUSDT,ETHUSDT,SOLUSDT \\
        --market spot \\
        --interval 1m \\
        --start 2019-01 --end 2026-04 \\
        --out-dir $ECOPHYS_DATA_DIR/raw/binance

Output: {out_dir}/market={market}/interval={interval}/symbol={symbol}/year={yyyy}/month={mm}.parquet
Columns: open_time (ms), open, high, low, close, volume, close_time (ms),
         quote_volume, trade_count, taker_buy_base, taker_buy_quote
"""

from __future__ import annotations

import argparse
import io
import logging
import os
import sys
import time
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import cast

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests

log = logging.getLogger("binance_ingest")

BASE_URL = "https://data.binance.vision/data"

# https://github.com/binance/binance-public-data/ documents the schema
KLINE_COLS = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_volume", "trade_count",
    "taker_buy_base", "taker_buy_quote", "ignore",
]

VALID_MARKETS = {"spot", "futures/um", "futures/cm"}
VALID_INTERVALS = {"1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1mo"}


@dataclass(frozen=True)
class IngestConfig:
    symbols: tuple[str, ...]
    market: str
    interval: str
    start: tuple[int, int]  # (year, month) inclusive
    end: tuple[int, int]    # (year, month) inclusive
    out_dir: Path
    retries: int = 3
    sleep_between: float = 0.3


def _iter_months(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    y, m = start
    out: list[tuple[int, int]] = []
    while (y, m) <= end:
        out.append((y, m))
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return out


def _url(symbol: str, market: str, interval: str, year: int, month: int) -> str:
    market_path = market  # e.g. "spot" or "futures/um"
    return f"{BASE_URL}/{market_path}/monthly/klines/{symbol}/{interval}/{symbol}-{interval}-{year:04d}-{month:02d}.zip"


def _download_zip(url: str, retries: int, sleep_between: float) -> bytes | None:
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=60)
            if resp.status_code == 404:
                log.info("not found (likely before listing): %s", url)
                return None
            resp.raise_for_status()
            return bytes(resp.content)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            log.warning("attempt %d failed for %s: %s", attempt, url, exc)
            time.sleep(sleep_between * attempt)
    log.error("giving up on %s: %s", url, last_err)
    return None


def _parse_zip(raw: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        names = zf.namelist()
        if len(names) != 1:
            raise ValueError(f"unexpected number of files in zip: {names}")
        with zf.open(names[0]) as f:
            # Some older archives have no header; newer ones do. Read both robustly.
            sample = f.read(256)
            f.close()
        with zf.open(names[0]) as f:
            header = 0 if sample.startswith(b"open_time") else None
            df = pd.read_csv(f, header=header, names=None if header == 0 else KLINE_COLS)
    # Cast
    df = df[KLINE_COLS].drop(columns=["ignore"])
    for col in ["open", "high", "low", "close", "volume", "quote_volume", "taker_buy_base", "taker_buy_quote"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["open_time", "close_time", "trade_count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    return df


def _write(df: pd.DataFrame, symbol: str, market: str, interval: str, year: int, month: int, out_dir: Path) -> Path:
    shard_dir = (
        out_dir
        / f"market={market.replace('/', '_')}"
        / f"interval={interval}"
        / f"symbol={symbol}"
        / f"year={year:04d}"
    )
    shard_dir.mkdir(parents=True, exist_ok=True)
    path = shard_dir / f"month={month:02d}.parquet"
    table = pa.Table.from_pandas(df, preserve_index=False)
    write_table = cast(Callable[..., None], pq.write_table)
    write_table(table, path, compression="zstd", compression_level=7)
    return path


def ingest_one(symbol: str, cfg: IngestConfig) -> list[Path]:
    written: list[Path] = []
    for year, month in _iter_months(cfg.start, cfg.end):
        url = _url(symbol, cfg.market, cfg.interval, year, month)
        raw = _download_zip(url, cfg.retries, cfg.sleep_between)
        if raw is None:
            continue
        try:
            df = _parse_zip(raw)
        except Exception as exc:  # noqa: BLE001
            log.error("parse failed for %s %d-%02d: %s", symbol, year, month, exc)
            continue
        path = _write(df, symbol, cfg.market, cfg.interval, year, month, cfg.out_dir)
        written.append(path)
        log.info("wrote %s (%d rows)", path, len(df))
        time.sleep(cfg.sleep_between)
    return written


def run(cfg: IngestConfig) -> dict[str, list[Path]]:
    if cfg.market not in VALID_MARKETS:
        raise ValueError(f"market={cfg.market!r} not in {VALID_MARKETS}")
    if cfg.interval not in VALID_INTERVALS:
        raise ValueError(f"interval={cfg.interval!r} not in {VALID_INTERVALS}")
    out: dict[str, list[Path]] = {}
    for sym in cfg.symbols:
        out[sym] = ingest_one(sym, cfg)
    return out


def _default_out_dir() -> Path:
    env = os.environ.get("ECOPHYS_DATA_DIR")
    if env:
        return Path(env) / "raw" / "binance"
    return Path.cwd() / "data" / "raw" / "binance"


def _parse_ym(s: str) -> tuple[int, int]:
    y, m = s.split("-")
    return int(y), int(m)


def _parse_args(argv: list[str] | None = None) -> IngestConfig:
    today = date.today()
    default_end = f"{today.year:04d}-{today.month:02d}"
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--symbols", required=True, help="comma-separated, e.g. BTCUSDT,ETHUSDT")
    p.add_argument("--market", default="spot", choices=sorted(VALID_MARKETS))
    p.add_argument("--interval", default="1m", choices=sorted(VALID_INTERVALS))
    p.add_argument("--start", default="2019-01", help="YYYY-MM inclusive")
    p.add_argument("--end", default=default_end, help="YYYY-MM inclusive")
    p.add_argument("--out-dir", type=Path, default=_default_out_dir())
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--sleep", type=float, default=0.3)
    p.add_argument("--log-level", default="INFO")
    args = p.parse_args(argv)
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    return IngestConfig(
        symbols=tuple(s.strip() for s in args.symbols.split(",") if s.strip()),
        market=args.market,
        interval=args.interval,
        start=_parse_ym(args.start),
        end=_parse_ym(args.end),
        out_dir=args.out_dir,
        retries=args.retries,
        sleep_between=args.sleep,
    )


def main(argv: list[str] | None = None) -> int:
    cfg = _parse_args(argv)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    results = run(cfg)
    succeeded = sum(1 for v in results.values() if v)
    log.info("done: %d/%d symbols had data", succeeded, len(results))
    return 0 if succeeded == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
