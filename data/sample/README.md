# `data/sample/` — Curated small samples (in-repo)

This directory contains **small, redistributable samples** of each data source
used by EcoPhys. They ship with the repo so anyone who clones can smoke-test
the pipelines without paying or waiting for multi-GB downloads.

## What's here

```
data/sample/
├── LOBSTER/     # NASDAQ ITCH reconstruction, 2012-06-21
├── yfinance/    # SPY daily bars, 2016–2026
└── binance/     # BTCUSDT + ETHUSDT 1-min bars, 2024 Q1
```

### LOBSTER (56 MB, 8 ZIPs)

Source: https://data.lobsterdata.com/info/DataSamples.php  
License: free academic sample, redistribution OK per LOBSTER terms
Date: 2012-06-21 (one trading day)

| Symbol | Levels present | Events (messages) |
|---|---|---|
| AAPL | L10, L50 | ~400k |
| AMZN | L10 | ~280k |
| GOOG | L10 | ~170k |
| MSFT | L1, L10, L50 | ~220k |
| SPY | L50 | ~1.1M |

Each ZIP contains two CSVs:
- `*_message_*.csv` — 6 columns: time, event_type, order_id, size, price, direction
- `*_orderbook_*.csv` — 4·L columns: (ask_price_k, ask_size_k, bid_price_k, bid_size_k) for k=1..L

Prices are integers in dollars × 10⁴; times are seconds after midnight.
See the readme inside each ZIP for full field semantics and event-type codes.

**Use for**: v1 architecture microstructure validation; Paper A's
microstructure appendix; debugging LOB ingestion pipelines before Tier-1
paid data arrives.

### yfinance (384 KB, 24 parquet)

`interval=1d/symbol={SPY,^GSPC}/year={2015..2026}.parquet` — daily adjusted
close + OHLCV for SPY (ETF) and ^GSPC (index). Produced by
`ecomd.data.yfinance_ingest`.

**Use for**: stylized-facts smoke tests, EcoMD v0.x training (what
Session 10–13 used).

### binance (14 MB, 6 parquet)

`market=spot/interval=1m/symbol={BTCUSDT,ETHUSDT}/year=2024/month={01,02,03}.parquet`  
Source: https://data.binance.vision (free, redistribution OK per Binance terms)

**Use for**: crypto stylized-facts reference + v0.x cross-asset sanity.

## When to use samples vs full data

| Task | Use this (`data/sample/`) | Use full data |
|---|---|---|
| CI / smoke tests | ✓ | |
| v0.x training (N ≤ 1000) | ✓ | |
| v1 architecture validation | ✓ (LOBSTER for LOB test) | |
| Paper A Table 1 (real reference values) | | full SPX/BTC history |
| Paper B cross-market universality | | 8 markets × multi-year |
| vendor-level microstructure experiments | | Tier 1 LOBSTER subscription |

## Full data flow

```
full data (not in git)     →   R2 bucket `ecophys/`   →   H20 NFS + hot cache
                           ↑                              ↓
                     `ecomd.data.r2_sync`             training
```

This `data/sample/` is the **only** data in git. Everything else lives in R2
(canonical) or H20 NFS (cache), managed via `ecomd.data.r2_sync`.
