"""Expected schemas for vendor-delivered data (T1.1, T1.2, T1.3).

When vendor data arrives (~2026-04-26), each delivery is validated against the
relevant schema before ingestion. Validation catches: missing columns, wrong
dtypes, out-of-range values, date gaps, survivorship-bias red flags.

Per plan v2 §5.1 (buy_order_zh.md):
  T1.1: US equity minute OHLCV, SP500+R1000, 2008→present, survivorship-bias-free
  T1.2: LOBSTER/ITCH, ≥50 symbols × ≥3 months, depth ≥10
  T1.3: CBOE EOD options chains for SPX/SPY/QQQ/VIX, 2005→present
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    dtype: str          # pandas dtype: float64, int64, datetime64[ns, UTC], string, Int64
    nullable: bool = False
    description: str = ""
    range: tuple[float, float] | None = None  # (min, max), inclusive


@dataclass(frozen=True)
class SchemaSpec:
    name: str
    description: str
    required_columns: tuple[ColumnSpec, ...]
    optional_columns: tuple[ColumnSpec, ...] = field(default_factory=tuple)
    min_rows_per_symbol: int = 0
    min_symbols: int = 0
    date_range_required: tuple[date, date] | None = None
    notes: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# T1.1 — US equity minute OHLCV
# ─────────────────────────────────────────────────────────────────────────────

T1_1_MINUTE_OHLCV = SchemaSpec(
    name="T1.1_us_equity_minute_ohlcv",
    description="US equity 1-minute OHLCV, S&P 500 + Russell 1000 constituents, survivorship-bias-free, 2008-01-01 → present",
    required_columns=(
        ColumnSpec("timestamp", "datetime64[ns, UTC]", description="bar open time, UTC"),
        ColumnSpec("symbol", "string", description="ticker"),
        ColumnSpec("open", "float64", range=(0, 1e7)),
        ColumnSpec("high", "float64", range=(0, 1e7)),
        ColumnSpec("low", "float64", range=(0, 1e7)),
        ColumnSpec("close", "float64", range=(0, 1e7)),
        ColumnSpec("volume", "Int64", nullable=True, range=(0, 1e12)),
    ),
    optional_columns=(
        ColumnSpec("adjusted_close", "float64", nullable=True, description="split+dividend adjusted"),
        ColumnSpec("vwap", "float64", nullable=True),
        ColumnSpec("trade_count", "Int64", nullable=True),
        ColumnSpec("dividends", "float64", nullable=True),
        ColumnSpec("splits", "float64", nullable=True),
        ColumnSpec("is_delisted", "bool", nullable=True, description="True if row is from a ticker that later delisted"),
    ),
    min_rows_per_symbol=100_000,
    min_symbols=500,
    date_range_required=(date(2008, 1, 1), date(2023, 12, 31)),
    notes=(
        "MUST be survivorship-bias-free: include rows for tickers that delisted during 2008+. "
        "Red flag: if 'symbol' column unique-count ≈ current SP500 count (~500) then vendor gave survivors only. "
        "Acceptable: ~700+ unique symbols across the full window including delisted."
    ),
)

# ─────────────────────────────────────────────────────────────────────────────
# T1.2 — LOB messages + order book
# ─────────────────────────────────────────────────────────────────────────────

T1_2_LOB_MESSAGES = SchemaSpec(
    name="T1.2_lob_messages",
    description="LOBSTER-style message stream: every add/cancel/execute event",
    required_columns=(
        ColumnSpec("timestamp", "float64", description="seconds since market open, or UTC datetime64 - both accepted"),
        ColumnSpec("event_type", "Int64", description="LOBSTER code: 1=submission 2=cancel 3=delete 4=execute-visible 5=execute-hidden 6=crosses 7=trading-halt"),
        ColumnSpec("order_id", "Int64"),
        ColumnSpec("size", "Int64", range=(0, 1e9)),
        ColumnSpec("price", "float64", range=(0, 1e7), description="price × 10000 if LOBSTER native; we normalise on ingest"),
        ColumnSpec("side", "Int64", description="1=buy -1=sell (LOBSTER uses 1 / -1)"),
    ),
    optional_columns=(
        ColumnSpec("symbol", "string", nullable=True, description="if multi-symbol file; single-symbol files often omit"),
    ),
    min_rows_per_symbol=1_000_000,
    min_symbols=50,
    notes="If delivered as ITCH .pcap, we convert to this schema via a preprocessor.",
)

T1_2_LOB_BOOK = SchemaSpec(
    name="T1.2_lob_orderbook",
    description="LOBSTER-style orderbook snapshot: top-K levels after every event",
    required_columns=(
        ColumnSpec("timestamp", "float64"),
        ColumnSpec("ask_price_1", "float64", range=(0, 1e7)),
        ColumnSpec("ask_size_1", "Int64", range=(0, 1e9)),
        ColumnSpec("bid_price_1", "float64", range=(0, 1e7)),
        ColumnSpec("bid_size_1", "Int64", range=(0, 1e9)),
        # expect levels 2..10
    ),
    min_rows_per_symbol=1_000_000,
    min_symbols=50,
    notes="10-level depth required. Level 2..10 columns follow the same naming pattern.",
)

# ─────────────────────────────────────────────────────────────────────────────
# T1.3 — CBOE EOD options chains
# ─────────────────────────────────────────────────────────────────────────────

T1_3_OPTIONS_EOD = SchemaSpec(
    name="T1.3_options_eod_chain",
    description="Daily EOD options chain for SPX/SPY/QQQ/VIX, 2005→present",
    required_columns=(
        ColumnSpec("trade_date", "datetime64[ns]", description="session date"),
        ColumnSpec("underlying", "string", description="SPX, SPY, QQQ, VIX, etc."),
        ColumnSpec("underlying_price", "float64", range=(0, 1e7)),
        ColumnSpec("expiration", "datetime64[ns]"),
        ColumnSpec("strike", "float64", range=(0, 1e7)),
        ColumnSpec("option_type", "string", description="'C' or 'P'"),
        ColumnSpec("bid", "float64", nullable=True, range=(0, 1e6)),
        ColumnSpec("ask", "float64", nullable=True, range=(0, 1e6)),
        ColumnSpec("last", "float64", nullable=True, range=(0, 1e6)),
        ColumnSpec("volume", "Int64", nullable=True, range=(0, 1e10)),
        ColumnSpec("open_interest", "Int64", nullable=True, range=(0, 1e10)),
        ColumnSpec("implied_vol", "float64", nullable=True, range=(0, 10), description="annualised IV, 0.2 = 20%"),
        ColumnSpec("delta", "float64", nullable=True, range=(-1, 1)),
    ),
    optional_columns=(
        ColumnSpec("gamma", "float64", nullable=True),
        ColumnSpec("theta", "float64", nullable=True),
        ColumnSpec("vega", "float64", nullable=True),
        ColumnSpec("rho", "float64", nullable=True),
    ),
    date_range_required=(date(2005, 1, 1), date(2023, 12, 31)),
    notes="SPX + SPY + QQQ + VIX required; other underlyings optional.",
)

# ─────────────────────────────────────────────────────────────────────────────
# Registry
# ─────────────────────────────────────────────────────────────────────────────

REGISTRY: dict[str, SchemaSpec] = {
    schema.name: schema for schema in (
        T1_1_MINUTE_OHLCV,
        T1_2_LOB_MESSAGES,
        T1_2_LOB_BOOK,
        T1_3_OPTIONS_EOD,
    )
}


# ─────────────────────────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class ValidationReport:
    schema_name: str
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    def show(self) -> str:
        lines = [f"Schema: {self.schema_name}  passed={self.passed}"]
        for e in self.errors:
            lines.append(f"  ERROR   {e}")
        for w in self.warnings:
            lines.append(f"  WARN    {w}")
        for k, v in self.stats.items():
            lines.append(f"  stat    {k}: {v}")
        return "\n".join(lines)


def validate(df: pd.DataFrame, schema: SchemaSpec) -> ValidationReport:
    rep = ValidationReport(schema_name=schema.name, passed=True)

    # Column presence
    have = set(df.columns)
    need = {c.name for c in schema.required_columns}
    missing = need - have
    if missing:
        rep.passed = False
        rep.errors.append(f"missing required columns: {sorted(missing)}")

    # Dtype + range
    for col in schema.required_columns:
        if col.name not in df.columns:
            continue
        actual = str(df[col.name].dtype)
        if not _dtype_compatible(actual, col.dtype):
            rep.passed = False
            rep.errors.append(f"column {col.name!r} dtype {actual!r} != expected {col.dtype!r}")
        if col.range is not None and pd.api.types.is_numeric_dtype(df[col.name]):
            lo, hi = col.range
            bad = (df[col.name].notna() & ((df[col.name] < lo) | (df[col.name] > hi))).sum()
            if bad > 0:
                rep.warnings.append(f"column {col.name!r} has {bad} values outside [{lo}, {hi}]")
        if not col.nullable and df[col.name].isna().any():
            n = int(df[col.name].isna().sum())
            rep.passed = False
            rep.errors.append(f"column {col.name!r} is non-nullable but has {n} NaNs")

    # Symbol / row thresholds
    if "symbol" in df.columns:
        syms = df["symbol"].nunique()
        rep.stats["n_symbols"] = int(syms)
        if schema.min_symbols and syms < schema.min_symbols:
            rep.warnings.append(f"only {syms} unique symbols, expected ≥ {schema.min_symbols} (possible survivorship bias)")
        if schema.min_rows_per_symbol:
            counts = df.groupby("symbol").size()
            too_small = int((counts < schema.min_rows_per_symbol).sum())
            if too_small:
                rep.warnings.append(f"{too_small} symbols have < {schema.min_rows_per_symbol} rows")

    # Date range coverage
    if schema.date_range_required is not None:
        date_col = (
            "trade_date"
            if "trade_date" in df.columns
            else "timestamp" if "timestamp" in df.columns else None
        )
        if date_col:
            ts = pd.to_datetime(df[date_col])
            lo_req, hi_req = schema.date_range_required
            actual_lo, actual_hi = ts.min(), ts.max()
            rep.stats["date_range"] = (str(actual_lo), str(actual_hi))
            if actual_lo.date() > lo_req:
                rep.warnings.append(f"data starts at {actual_lo.date()}, required ≤ {lo_req}")
            if actual_hi.date() < hi_req:
                rep.warnings.append(f"data ends at {actual_hi.date()}, required ≥ {hi_req}")

    rep.stats["n_rows"] = int(len(df))
    return rep


def _dtype_compatible(actual: str, expected: str) -> bool:
    if actual == expected:
        return True
    # Loose matching for commonly-interchangeable dtypes
    compat = {
        ("int64", "Int64"),
        ("Int64", "int64"),
        ("object", "string"),
        ("string", "object"),
        ("datetime64[ns]", "datetime64[ns, UTC]"),
        ("datetime64[ns, UTC]", "datetime64[ns]"),
    }
    return (actual, expected) in compat or (
        expected.startswith("datetime64") and actual.startswith("datetime64")
    )
