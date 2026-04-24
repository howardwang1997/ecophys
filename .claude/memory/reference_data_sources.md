---
name: Data source registry (EcoPhys)
description: Ranked list of financial data sources for US equity (daily/minute/LOB) and crypto (minute/tick/L2). Includes free tiers for development plus the Path C paid stack (Tardis L2, FirstRate minute, LOBSTER) committed 2026-04-24 for Nature Physics flagship. Cost, coverage, and access mechanism notes.
type: reference
originSessionId: c6748c05-53ac-462d-9535-154e95f91d9f
---
# Data Source Registry — EcoPhys

## Path C paid stack (committed 2026-04-24, $8–12k)

| Source | Price target | Coverage | Paper dependency |
|---|---|---|---|
| **Tardis.dev crypto L2** | $4–5.5k | BTC + ETH × 6 months, full L2 book changes + trades | Paper B (B3 TUR + cross-asset universality), Paper B.5 |
| **FirstRate / AlgoSeek US equity minute** | $1.5–2.5k | 20 symbols × 3 years, 1m OHLCV, survivorship-bias-free | Paper B (A1 intraday-equity scale), Paper C (crash EWS) |
| **LOBSTER research subscription** | $3–4.5k | 20–50 symbols × 2–3 years, L10 reconstruction | Paper B (B3 event-level), Paper C (optimal execution) |

See `ecomd/data/buy_order_v2_{en,zh}.md` for purchasing decision flow tied to plan v3 gates.

## US Equity

| Source | Cost | Frequency | Access | Notes |
|---|---|---|---|---|
| yfinance | Free | Daily (full history), 1m (~6mo) | `pip install yfinance` | Use as default daily source. No official API — be polite with scraping rate. |
| Polygon.io | Free tier → $79/mo | EOD free; 10yr at $79 | REST API | Good step-up when yfinance insufficient. |
| Alpha Vantage | Free (5 req/min, 25/day) → $429/mo | Daily/minute | REST API | Free limits too tight for serious work. |
| Databento | $125 free credit → tiered | Tick, 1m, daily | Python SDK | **Recommended for initial minute-level experiments** — the $125 credit covers a meaningful prototype. |
| FirstRate Data | ~$60–100/mo per ticker or bulk discount | 1m, tick (10–15yr) | One-time CSV purchase | **Path C: committed.** Primary source for US equity minute (20 symbols × 3 yr ~ $1.5–2.5k). |
| Kibot | $350–500 per symbol | 1m, tick (17+ yr) | One-time download | Alternative to FirstRate; older. |
| LOBSTER | Free samples (in `data/sample/`); full ~$3–4.5k for 2–3 yr | NASDAQ LOB reconstruction | Direct download | **Path C: committed.** Free samples still useful for pipeline development. |
| CRSP/WRDS | Institutional (via university) | Daily since 1925, TAQ tick since 1997/2003 | WRDS portal | Only if user has university affiliation. |
| FRED | Free | Daily indices | REST API | Macro/indices only. |
| Stooq | Free | Daily, hourly, 1m | Manual CSV | 30+ yr some stocks. No API — fine for one-off downloads. |

**Default starting stack**: yfinance (daily) + Databento ($125 trial for minute prototypes) + LOBSTER sample (LOB).

## Crypto

| Source | Cost | Frequency | Access | Notes |
|---|---|---|---|---|
| Binance data.binance.vision | **Free** | 1m klines, aggTrades (tick) | HTTPS bulk download | **Main source**: https://data.binance.vision/ — monthly ZIP files per symbol. BTC/ETH/SOL 1yr ≈ 50–200 GB zstd compressed. |
| CryptoDataDownload | Free | Minute OHLCV | CSV download | 400+ exchanges. Convenient for cross-exchange replicates. |
| Tardis.dev | Academic $450/mo; biz $3.5k+ | L2 book, trades, liquidations, options | Python SDK | **Path C: committed.** BTC + ETH × 6 months (~$4–5.5k). Paper B B3 TUR + universality at microstructure scale rely on this. |
| Kaiko | Institutional (expensive) | Standardized OHLCV + indices | API | Regulatory-grade; skip unless specific need. |
| Databento | $125 credit → tiered | Tick, 1m | Python SDK | Also has crypto. |
| CoinAPI.io | Free 100 req/day → $10–500/mo | OHLCV, quotes, L2/L3 | REST | Flexible for spot-checking individual pairs. |

**Default starting stack**: Binance `data.binance.vision` (free bulk tick/klines) + CryptoDataDownload (cross-exchange minute).

## Evaluation benchmarks / reference values

- **Cont (2001) stylized facts** — 11 canonical properties. Paper: http://rama.cont.perso.math.cnrs.fr/pdf/empirical.pdf. Our stylized_facts suite (Phase 1) must implement all 11.
- **ABIDES** — agent-based reference simulator (JP Morgan / CMU). GitHub baseline. https://github.com/jpmorganchase/abides-jpmc-public
- **Tick data processing**: zstd-compressed Parquet. Typical compression ~3–4× over raw CSV. Schema: `timestamp, symbol, price, volume, side, trade_id`.

## Storage cost estimates

- S&P 500 minute (1 yr, Parquet+zstd): ~100–400 MB → <$0.01/mo on S3.
- BTC/ETH/SOL tick (1 yr, 5 exchanges): ~50–200 GB compressed → ~$1–5/mo on S3 Standard, negligible on Glacier.
- Full-scale multi-year crypto+equity: stay under 1 TB on S3 Standard — ~$20/mo.

## Crash test-case data availability

| Event | Dates | Equity (yfinance/CRSP) | Crypto |
|---|---|---|---|
| Black Monday 1987 | 1987-10-19 | CRSP: yes | N/A |
| Asian crisis | 1997-07..11 | CRSP: yes | N/A |
| 2008 GFC | 2008-09..2009-03 | yfinance: yes | N/A |
| Flash Crash 2010 | 2010-05-06 | yfinance intraday: yes | N/A |
| COVID crash | 2020-02..03 | yfinance: yes | Binance: yes (2020-) |
| Luna/UST | 2022-05 | N/A | Binance, Tardis |
| FTX | 2022-11 | N/A | Binance, Tardis |
| SVB | 2023-03 | yfinance: yes | Binance: limited spillover |
