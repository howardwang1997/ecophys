# Data Buy Order v1 — EcoPhys (2026-04-23)

> ⚠️ **SUPERSEDED**: Replaced by `buy_order_v2_en.md` (Path C, 2026-04-24 evening).
> v2 restructures purchases by paper sequence and commits to $8–12k high-freq
> data for the Nature Physics flagship. Kept here for historical reference.

**Context**: User has vendor contacts covering all markets we need. Budget $50k, planned spend $15k–25k. This doc = prioritized list for vendors.

## Priority 1 — buy immediately (estimated $6k–12k)

### P1.1 — US equity minute OHLCV, S&P 500 + Russell 1000, 2008→present
- **Specification**: 1-min bars; survivorship-bias-free; adjusted + raw; include delisted tickers; CSV or Parquet.
- **Time window non-negotiable**: must cover 2008-09 (GFC), 2010-05-06 (Flash Crash), 2020-03 (COVID), 2023-03 (SVB).
- **Expected size**: ~80–150 GB raw, ~20–30 GB Parquet+zstd.
- **Target price**: **$3k–6k**. If vendor quotes >$8k for S&P 500 alone, drop Russell 1000 to control scope.
- **Why #1**: Paper A training data. Everything else waits on this.

### P1.2 — US equity LOB (LOBSTER academic or NASDAQ ITCH raw)
- **Specification**: ~50 liquid symbols (AAPL, MSFT, NVDA, TSLA, GOOGL, META, AMZN, JPM, BAC, SPY, QQQ, NFLX, AMD, + 37 more), ≥ 3 months, depth ≥ 10 levels. Must include 2010-05-06 and 2022-11 windows.
- **Expected size**: ~150–300 GB raw, ~30–60 GB compressed.
- **Target price**: **$3k–5k**.
- **Why #2**: Paper B microstructure chapter; ABIDES-lite calibration.

## Priority 2 — buy in next 2–4 weeks (estimated $5k–10k)

### P2.1 — International equity indices + constituents (6 markets)
- **Specification**: FTSE 100 (UK), DAX 40 (Germany), Nikkei 225 (Japan), Hang Seng (HK), CSI 300 (CN), BOVESPA (Brazil) OR Kospi (Korea). Daily 10+ yr for index + constituents; minute bars for index + top 20 constituents since 2015.
- **Expected size**: ~10–40 GB compressed.
- **Target price**: **$2k–5k total**. Domestic (CSI 300, HSI) should be cheap via user's CN vendors ($200–1k). International likely needs Refinitiv-style vendor ($1k–4k).
- **Why critical**: **this is the Nature Physics lever** — 6 independent non-crypto markets + US + crypto = 8 systems to demonstrate universality of entropy-production crash precursor. Skipping this collapses us to "another S&P 500 paper."

### P2.2 — Crypto L2 book + liquidations, 4 exchanges, 2021–2025
- **Specification**: BTC-USDT, ETH-USDT, SOL-USDT (spot + perps). Exchanges: Binance, Coinbase, Bybit, OKX. L2 snapshots ≤ 100ms (can tolerate 1s if much cheaper). Funding rate + liquidation events. Cover Luna 2022-05, FTX 2022-11 in full.
- **Expected size**: ~200–400 GB compressed (largest single purchase by volume).
- **Target price**: **$3k–5k** (Tardis business 3 months ≈ $1.5k–3k but per-month; negotiate flat rate for one-time dump).
- **Why critical**: cross-exchange universality for Paper B; free Binance alone is one exchange only.

### P2.3 — CBOE EOD options chains (SPX, SPY, QQQ, VIX)
- **Specification**: Daily EOD chains 2005–present. All strikes, all expiries. IV, delta, OI + volume per strike. Put-call split.
- **Expected size**: ~5–15 GB compressed.
- **Target price**: **$1k–2k**.
- **Why**: put-call ratio + IV skew are mandatory baselines. Reviewer 2 will ask.

## Priority 3 — buy if bundle-cheap, otherwise skip ($2k–5k)

### P3.1 — A-share daily + 15min for SSE 50 / CSI 300 constituents 2010+
- Already sort of covered under P2.1's CSI 300, but deeper A-share coverage is useful for the universality section if user's domestic vendor quotes < $1k. A-share microstructure (T+1, price limits) is genuinely different from US/EU, strengthens universality story.

### P3.2 — Commodities + FX daily (gold, oil, copper; EUR/USD, USD/JPY, USD/CNY)
- Third control-group for Paper B. Cheap: expect < $500 via user's vendors.

## Explicitly SKIP

- Full TAQ (tick-level all US equities) — too big, marginal value
- OptionMetrics IvyDB intraday — CBOE EOD is enough
- News / sentiment / Twitter
- Bond tick, satellite, credit-card alternative data
- Anything without clear academic-publication license

## Procurement flow

1. Send this doc to vendor contact(s). Ask for quotes on **P1.1, P1.2, P2.3** first (total target $7k–13k).
2. Parallel: ask China-domestic vendor for **P2.1 CSI 300 + HSI** and **P3.1 A-share** (expect cheap, $500–2k total).
3. Once P1 arrives + preprocessed, order **P2.1 international + P2.2 crypto L2** (total $5k–10k).
4. P3 only if opportunistic.

## Delivery format (specify to vendor)

Strongly prefer:
- **Parquet** (with schema doc) or **CSV with explicit header + delimiter**
- **Compressed**: zstd or gzip
- **Delivery**: Google Drive / WeTransfer / vendor's own S3/R2 bucket with pre-signed URL. User will pull to Mac, preprocess, push to company NFS + R2 backup.
- **License terms in writing**: academic publication OK; derived results (plots, stats) publishable.

Avoid:
- Proprietary binary formats without conversion tools
- Web API-only access (we need bulk download, not 1000 req/day)
- Vendor lock-in that requires subscription renewal to keep using already-downloaded data

## Provenance file template

For each purchase, create `ecomd/data/provenance/<vendor-shortname>.md` with:
```
Vendor: <name>
Product: <sku / description>
Purchase date: YYYY-MM-DD
Invoice ref: <id>
License: <summary> (paste full terms into vendor_license.txt)
Coverage: <date range, symbols, frequency>
Delivered format: <schema>
Preprocessing script: ecomd/data/ingest_<vendor>.py
SHA256 of raw archive: <hash>
Stored at: nfs://<path>, r2://<bucket/path>
```
