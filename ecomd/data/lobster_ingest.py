"""LOBSTER free-sample downloader + Parquet converter.

Downloads the academic LOBSTER sample ZIPs (2012-06-21 NASDAQ ITCH
reconstruction for AAPL/AMZN/GOOG/INTC/MSFT/SPY), unpacks them, converts the
two CSVs inside each ZIP to Parquet+zstd, and leaves the result under

    data/raw/lobster/sample/symbol={SYM}/date=2012-06-21/level=L{N}/
        messages.parquet     # schema: time, event_type, order_id, size, price, direction
        orderbook.parquet    # schema: ask_price_1, ask_size_1, bid_price_1, bid_size_1, ...

Prices in Parquet are in dollars (LOBSTER ships prices as integer dollars
× 10000; we divide here so downstream analysis is clean). Time is
seconds-after-midnight float64. Sizes and counts stay as int64.

After ingestion, invoke ``ecomd.data.r2_sync upload data/raw/lobster/
lobster/`` to push to Cloudflare R2 (or call :func:`sync_to_r2` directly from
Python).
"""

from __future__ import annotations

import argparse
import io
import logging
import shutil
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

log = logging.getLogger("lobster_ingest")

BASE_URL = "https://data.lobsterdata.com/sample"
SAMPLE_DATE = "2012-06-21"

# (symbol, level) pairs published as free samples on LOBSTER as of 2026-04.
SAMPLES: list[tuple[str, int]] = [
    ("AMZN", 1), ("AMZN", 5), ("AMZN", 10),
    ("AAPL", 1), ("AAPL", 5), ("AAPL", 10), ("AAPL", 30), ("AAPL", 50),
    ("GOOG", 1), ("GOOG", 5), ("GOOG", 10),
    ("INTC", 1), ("INTC", 5), ("INTC", 10),
    ("MSFT", 1), ("MSFT", 5), ("MSFT", 10), ("MSFT", 30), ("MSFT", 50),
    ("SPY",  30), ("SPY",  50),
]

PRICE_DIVISOR = 10_000.0  # LOBSTER stores prices as int × 10_000 (= dollars)


@dataclass
class IngestResult:
    symbol: str
    level: int
    zip_bytes: int
    n_events: int
    messages_parquet: Path
    orderbook_parquet: Path


# ─────────────────────────────────────────────────────────────────────────────
# Download + unpack
# ─────────────────────────────────────────────────────────────────────────────


def _zip_url(symbol: str, level: int) -> str:
    return f"{BASE_URL}/LOBSTER_SampleFile_{symbol}_{SAMPLE_DATE}_{level}.zip"


def _download(url: str, timeout: float = 60.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "ecophys-research/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _find_csvs(zf: zipfile.ZipFile) -> tuple[str, str]:
    """Locate message and orderbook CSV names inside a LOBSTER sample ZIP."""
    names = zf.namelist()
    msg = next((n for n in names if "message" in n.lower() and n.endswith(".csv")), None)
    book = next((n for n in names if "orderbook" in n.lower() and n.endswith(".csv")), None)
    if msg is None or book is None:
        raise RuntimeError(f"could not locate message/orderbook CSVs in zip: {names}")
    return msg, book


# ─────────────────────────────────────────────────────────────────────────────
# Parse + write Parquet
# ─────────────────────────────────────────────────────────────────────────────


MSG_COLS = ["time", "event_type", "order_id", "size", "price", "direction"]


def _parse_messages(csv_bytes: bytes) -> pd.DataFrame:
    df = pd.read_csv(
        io.BytesIO(csv_bytes),
        header=None,
        names=MSG_COLS,
        dtype={"time": np.float64, "event_type": np.int8, "order_id": np.int64,
               "size": np.int64, "price": np.int64, "direction": np.int8},
    )
    df["price"] = df["price"].astype(np.float64) / PRICE_DIVISOR
    return df


def _parse_orderbook(csv_bytes: bytes, level: int) -> pd.DataFrame:
    cols: list[str] = []
    for k in range(1, level + 1):
        cols.extend([f"ask_price_{k}", f"ask_size_{k}", f"bid_price_{k}", f"bid_size_{k}"])
    df = pd.read_csv(io.BytesIO(csv_bytes), header=None, names=cols, dtype=np.int64)
    # convert prices to dollars in-place
    for k in range(1, level + 1):
        df[f"ask_price_{k}"] = df[f"ask_price_{k}"].astype(np.float64) / PRICE_DIVISOR
        df[f"bid_price_{k}"] = df[f"bid_price_{k}"].astype(np.float64) / PRICE_DIVISOR
    return df


def _write_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, path, compression="zstd", compression_level=10)


# ─────────────────────────────────────────────────────────────────────────────
# Top-level ingest
# ─────────────────────────────────────────────────────────────────────────────


def ingest_one(
    symbol: str,
    level: int,
    out_root: Path,
    *,
    overwrite: bool = False,
) -> IngestResult:
    sym_dir = out_root / "sample" / f"symbol={symbol}" / f"date={SAMPLE_DATE}" / f"level=L{level}"
    msg_path = sym_dir / "messages.parquet"
    book_path = sym_dir / "orderbook.parquet"

    if not overwrite and msg_path.exists() and book_path.exists():
        log.info(f"[skip] {symbol} L{level} already present at {sym_dir}")
        df_msg = pd.read_parquet(msg_path, columns=["time"])
        return IngestResult(symbol, level, 0, len(df_msg), msg_path, book_path)

    url = _zip_url(symbol, level)
    log.info(f"[download] {symbol} L{level} ← {url}")
    data = _download(url)
    log.info(f"[download] {symbol} L{level} got {len(data):_} bytes")

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        msg_name, book_name = _find_csvs(zf)
        df_msg = _parse_messages(zf.read(msg_name))
        df_book = _parse_orderbook(zf.read(book_name), level)

    if len(df_msg) != len(df_book):
        raise RuntimeError(
            f"{symbol} L{level}: message rows ({len(df_msg)}) != orderbook rows ({len(df_book)})"
        )

    _write_parquet(df_msg, msg_path)
    _write_parquet(df_book, book_path)
    log.info(
        f"[ok] {symbol} L{level}: {len(df_msg):_} events → "
        f"{msg_path.stat().st_size/1e6:.1f} MB msgs + {book_path.stat().st_size/1e6:.1f} MB book"
    )
    return IngestResult(symbol, level, len(data), len(df_msg), msg_path, book_path)


def ingest_all(
    out_root: Path,
    *,
    overwrite: bool = False,
    subset: list[tuple[str, int]] | None = None,
) -> list[IngestResult]:
    results: list[IngestResult] = []
    targets = subset or SAMPLES
    for sym, lev in targets:
        try:
            results.append(ingest_one(sym, lev, out_root, overwrite=overwrite))
        except Exception as e:  # noqa: BLE001
            log.error(f"[fail] {sym} L{lev}: {e}")
    return results


# ─────────────────────────────────────────────────────────────────────────────
# R2 upload helper (delegates to ecomd.data.r2_sync)
# ─────────────────────────────────────────────────────────────────────────────


def sync_to_r2(local_root: Path, remote_prefix: str = "lobster/") -> int:
    from .r2_sync import R2Config, upload
    cfg = R2Config.from_env()
    return upload(local_root, remote_prefix, cfg=cfg)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def _default_out_root() -> Path:
    # project root = two levels up from this file (ecomd/data/)
    return Path(__file__).resolve().parents[2] / "data" / "raw" / "lobster"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(_default_out_root()),
                        help="local Parquet root (default: data/raw/lobster)")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--upload", action="store_true",
                        help="after ingest, upload to R2 under lobster/")
    parser.add_argument("--only", nargs="*", default=None,
                        help="subset like 'AAPL:10 MSFT:5' to limit which files")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    out_root = Path(args.out).expanduser().resolve()

    subset: list[tuple[str, int]] | None = None
    if args.only:
        subset = []
        for item in args.only:
            sym, lev = item.split(":")
            subset.append((sym.upper(), int(lev)))

    results = ingest_all(out_root, overwrite=args.overwrite, subset=subset)
    total_events = sum(r.n_events for r in results)
    log.info(f"ingested {len(results)} files, {total_events:_} total events → {out_root}")

    if args.upload:
        log.info(f"uploading {out_root} → R2 bucket under lobster/ ...")
        n = sync_to_r2(out_root, remote_prefix="lobster/")
        log.info(f"uploaded {n} objects to R2")


if __name__ == "__main__":
    main()
