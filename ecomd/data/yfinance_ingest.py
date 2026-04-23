"""Download US equity daily/minute OHLCV from Yahoo Finance and write Parquet shards.

Usage:
    conda run -n ecophys python -m ecomd.data.yfinance_ingest \\
        --symbols SPY,^GSPC,AAPL,MSFT \\
        --start 1990-01-01 --end 2026-04-23 \\
        --interval 1d \\
        --out-dir $ECOPHYS_DATA_DIR/raw/yfinance

Output schema: one Parquet file per (symbol, year) at
    {out_dir}/interval={interval}/symbol={symbol}/year={yyyy}.parquet
Columns: timestamp (UTC), open, high, low, close, volume, adjusted_close, dividends, splits
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

log = logging.getLogger("yfinance_ingest")


@dataclass(frozen=True)
class IngestConfig:
    symbols: tuple[str, ...]
    start: str
    end: str
    interval: str  # 1d, 1h, 30m, 15m, 5m, 1m — note yfinance 1m only ~6mo back
    out_dir: Path
    retries: int = 3
    sleep_between: float = 0.5


def _normalise(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Yahoo returns multi-index columns when auto_adjust=False; flatten + rename."""
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df = df.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adjusted_close",
            "Volume": "volume",
            "Dividends": "dividends",
            "Stock Splits": "splits",
        }
    )
    keep = [c for c in ["open", "high", "low", "close", "adjusted_close", "volume", "dividends", "splits"] if c in df.columns]
    df = df[keep].copy()
    df.index = pd.to_datetime(df.index, utc=True)
    df.index.name = "timestamp"
    df["symbol"] = symbol
    return df.reset_index()


def _write_shards(df: pd.DataFrame, symbol: str, interval: str, out_dir: Path) -> list[Path]:
    written: list[Path] = []
    df["year"] = df["timestamp"].dt.year
    for year, year_df in df.groupby("year"):
        shard_dir = out_dir / f"interval={interval}" / f"symbol={symbol}"
        shard_dir.mkdir(parents=True, exist_ok=True)
        path = shard_dir / f"year={year}.parquet"
        table = pa.Table.from_pandas(year_df.drop(columns=["year"]), preserve_index=False)
        pq.write_table(table, path, compression="zstd", compression_level=7)
        written.append(path)
    return written


def ingest_one(symbol: str, cfg: IngestConfig) -> list[Path]:
    import yfinance as yf  # imported lazily so `--help` works without the dep

    last_err: Exception | None = None
    for attempt in range(1, cfg.retries + 1):
        try:
            df = yf.download(
                symbol,
                start=cfg.start,
                end=cfg.end,
                interval=cfg.interval,
                auto_adjust=False,
                actions=True,
                progress=False,
                threads=False,
            )
            if df.empty:
                log.warning("empty frame for %s (attempt %d)", symbol, attempt)
                time.sleep(cfg.sleep_between * attempt)
                continue
            df = _normalise(df, symbol)
            shards = _write_shards(df, symbol, cfg.interval, cfg.out_dir)
            log.info("wrote %d shards for %s (%d rows)", len(shards), symbol, len(df))
            return shards
        except Exception as exc:  # noqa: BLE001 — we want to retry anything transient
            last_err = exc
            log.warning("attempt %d for %s failed: %s", attempt, symbol, exc)
            time.sleep(cfg.sleep_between * attempt)
    assert last_err is not None
    raise RuntimeError(f"failed to ingest {symbol} after {cfg.retries} attempts") from last_err


def run(cfg: IngestConfig) -> dict[str, list[Path]]:
    out: dict[str, list[Path]] = {}
    for sym in cfg.symbols:
        try:
            out[sym] = ingest_one(sym, cfg)
        except Exception as exc:  # noqa: BLE001 — log and continue; don't abort whole batch
            log.error("giving up on %s: %s", sym, exc)
            out[sym] = []
    return out


def _default_out_dir() -> Path:
    env = os.environ.get("ECOPHYS_DATA_DIR")
    if env:
        return Path(env) / "raw" / "yfinance"
    return Path.cwd() / "data" / "raw" / "yfinance"


def _parse_args(argv: list[str] | None = None) -> IngestConfig:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--symbols", required=True, help="comma-separated tickers, e.g. SPY,^GSPC,AAPL")
    p.add_argument("--start", required=True, help="YYYY-MM-DD inclusive")
    p.add_argument("--end", required=True, help="YYYY-MM-DD exclusive")
    p.add_argument("--interval", default="1d", help="1d, 1h, 30m, 15m, 5m, 1m")
    p.add_argument("--out-dir", type=Path, default=_default_out_dir())
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--sleep", type=float, default=0.5)
    p.add_argument("--log-level", default="INFO")
    args = p.parse_args(argv)
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    return IngestConfig(
        symbols=tuple(s.strip() for s in args.symbols.split(",") if s.strip()),
        start=args.start,
        end=args.end,
        interval=args.interval,
        out_dir=args.out_dir,
        retries=args.retries,
        sleep_between=args.sleep,
    )


def main(argv: list[str] | None = None) -> int:
    cfg = _parse_args(argv)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    results = run(cfg)
    failed = [s for s, paths in results.items() if not paths]
    succeeded = len(results) - len(failed)
    log.info("done: %d succeeded, %d failed; failures=%s", succeeded, len(failed), failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
