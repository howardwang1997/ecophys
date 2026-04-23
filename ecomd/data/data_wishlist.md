# Data Wishlist — EcoPhys (v2, 2026-04-23)

**Budget**: up to $50,000. Planned spend: $15k–30k on Tier 1 + 1.5; reserve $20k+ for Phase 4/5 contingencies.

**Use**: hand this to data vendors / contacts. Priority-ordered by research ROI.

---

## Buy/skip decision rule at a glance

| Priority | What | Target price | Decision |
|---|---|---|---|
| Tier 0 | Free (yfinance, Binance, LOBSTER samples, VIX) | $0 | Already in Phase 0 plan |
| **Tier 1** | US minute 15yr + LOBSTER/ITCH full + CBOE EOD options | **$7k–15k** | **Buy all three** |
| **Tier 1.5** | International equity + Tardis crypto L2 | **$5k–10k** | **Buy — strengthens Nature Physics universality claim** |
| Tier 2 | CRSP, commodities, FX | $2k–5k | Buy only if WRDS access or cheap bundle |
| Tier 3 | Full TAQ, sentiment, news, alternative | — | Skip |

Total aiming: **$15k–30k**. Do not rush all $50k — keep Phase 4/5 contingency.

---

## Tier 0 — Free, already planned

| Dataset | Source | Status |
|---|---|---|
| SPX daily OHLCV 30+ yr | `yfinance` | Free; Phase 0 |
| BTC/ETH/SOL 1m + tick aggTrades 5+ yr | Binance `data.binance.vision` | Free bulk |
| NASDAQ LOB sample (10 stocks × ~10 days) | LOBSTER free | Free |
| VIX daily | CBOE public / yfinance | Free |

---

## Tier 1 — Core paid data ($7k–15k, **buy all**)

### T1.a — US equity minute OHLCV, 2008→present, survivorship-bias-free
- **Specification**:
  - S&P 500 + Russell 1000 constituents (expand to Russell 3000 if bundle cheap)
  - 1-minute OHLCV + Volume
  - 2008-01-01 → present (covers GFC, Flash Crash, COVID, SVB crashes)
  - Must include **delisted tickers** during their trading lifetime
  - Split/dividend adjusted + raw (both if possible)
- **Why critical**: Paper A training data. yfinance minute only ~6mo; this unlocks long-horizon training + proper train/val/test splits.
- **Size**: ~80–150 GB raw, ~20–30 GB Parquet+zstd
- **Target price**: **$3k–8k** (FirstRate bundle, or via user's vendor contacts at below-retail)

### T1.b — US equity LOB (LOBSTER full or raw NASDAQ ITCH)
- **Specification**:
  - LOBSTER message + order book files for ~50 liquid symbols (AAPL, MSFT, NVDA, TSLA, GOOGL, META, AMZN, JPM, BAC, SPY, etc.)
  - OR raw NASDAQ ITCH 5.0 pcap archive
  - Depth ≥ 10 levels
  - At least 3 months of trading days, including the Flash Crash 2010 window and the 2022 regime-shift window
- **Why critical**: Paper B microstructure→macro coarse-graining needs rich multi-stock LOB. ABIDES-lite calibration also needs this.
- **Size**: ~150–300 GB raw, ~30–60 GB compressed
- **Target price**: **$3k–5k** (LOBSTER academic full year ~$3–5k; or resold academic slice)

### T1.c — CBOE EOD options on SPX/SPY/QQQ/VIX
- **Specification**:
  - Daily EOD chain: strike × expiry grid for SPX, SPY, QQQ 2005→present
  - Implied volatility, delta, put/call OI + volume
  - Underlying: VIX included
- **Why critical**: put-call ratio and implied vol skew are **mandatory baselines** for crash prediction (Paper B/C). Reviewer 2 will ask.
- **Size**: ~5–15 GB compressed
- **Target price**: **$1k–2k** (CBOE DataShop directly)

---

## Tier 1.5 — Nature Physics amplifier ($5k–10k, **strongly recommend buy**)

### T1.5.a — International equity indices + constituents
- **Specification**:
  - **5 non-US markets**: FTSE 100 (UK), DAX 40 (Germany), Nikkei 225 (Japan), Hang Seng (HK), SSE 50 (China) [or CSI 300]
  - Constituents list + daily OHLCV 10+ yr
  - Minute-level bars for index + top 20 constituents of each, 2015+
- **Why this is the Nature Physics lever**: Cross-market universality is hard gate #2 for Nature Physics (§3.1.1 of plan). Having **5 independent markets + US + crypto = 7 independent systems** to show universal entropy-production → crash precursor is what differentiates us from "another S&P 500 paper".
- **Size**: ~10–30 GB compressed
- **Target price**: **$2k–5k** (multiple vendors; some regional data is cheaper locally — user's China vendor contacts might get CSI 300 / HSI near-free)

### T1.5.b — Tardis.dev crypto L2 (3-month business access)
- **Specification**:
  - BTC-USDT, ETH-USDT, SOL-USDT perpetuals + spot on Binance, Coinbase, Bybit, OKX, Kraken
  - L2 book snapshots ≤ 100ms
  - Trade + liquidation + funding data
  - Coverage: 2021-2025 including Luna (2022-05), FTX (2022-11)
- **Why important**: cross-exchange crypto L2 is needed to demonstrate that the physics quantity (entropy production / T_eff) is **not exchange-specific** but a property of the asset's collective trader dynamics. Free Binance data only gives one exchange.
- **Size**: ~200–400 GB → bulk download to R2, then selective pull to H20
- **Target price**: **$3k–5k** (Tardis business tier for 3 months is enough to do one big pull; or negotiate academic $450/mo × 3–6 mo)

---

## Tier 2 — Opportunistic, buy only if cheap

### T2.a — CRSP daily US equity (survivorship-bias-free, factor-adjusted), 1990–present
- **Why**: long-horizon stylized facts (Hurst exponent, long memory) need 20+ yr clean data. yfinance's survivorship bias + adjustment issues hurt rigor.
- **Problem**: CRSP is sold only through WRDS, which typically requires university affiliation. Independent researcher access is limited.
- **Workaround**: (1) ask user's university-affiliated contact if possible; (2) fallback is to carefully sanity-check yfinance against the Tier 1 minute data (which has dividends handled)
- **Target price**: $2k–5k if accessible; else **skip**

### T2.b — Commodities + FX daily (non-equity, non-crypto control group)
- **Why**: if Paper B needs extra evidence of universality beyond equity+crypto. Commodities (gold, oil, copper) and major FX pairs (EUR/USD, USD/JPY) are different microstructures.
- **Target price**: < $1k via Refinitiv / similar retail; or use Yahoo Finance for free (lower quality)
- **Decision**: buy only if T1.5.a doesn't give enough market diversity

### T2.c — Refinitiv Tick History or similar single-crash windows
- **Why**: only if our Tier 1.a minute data's granularity is insufficient for specific Flash Crash 2010 / COVID 2020-03-16 / SVB experiments
- **Target price**: $500–2k for specific event windows
- **Decision**: deferred until Phase 4 shows need

---

## Tier 3 — Skip entirely

- Full TAQ (tick-level US equity, all stocks): too big, marginal value
- Sentiment / news / Twitter data: out of scope
- Alternative data (credit card, satellite, etc.): out of scope
- Bond tick data: out of scope
- Full OptionMetrics IvyDB (intraday options chain): overkill; CBOE EOD is enough

---

## What to ask vendors / user's contacts

Paste this into the chat with your vendor contacts:

> Hi, I'm doing academic research on financial market simulation. Looking for the following data bundles. Interested in legitimate academic/research pricing and willing to sign NDAs. Rough budget $15k–30k across all items.
>
> 1. **US equity minute OHLCV, survivorship-bias-free, S&P 500 + Russell 1000, 2008 to present, adjusted + raw.** — target $3k–8k
> 2. **LOBSTER full (academic) or raw NASDAQ ITCH, ~50 liquid symbols, ≥ 3 months including 2010-05-06 + 2022-11.** — target $3k–5k
> 3. **CBOE EOD options chains for SPX/SPY/QQQ/VIX, 2005 to present, IV + put-call OI/volume.** — target $1k–2k
> 4. **International equity: FTSE 100 / DAX 40 / Nikkei 225 / HSI / CSI 300 constituents, daily 10+ yr + minute for top 20 each 2015+.** — target $2k–5k (might be cheapest from regional sources)
> 5. **Crypto L2 book data across 4–5 major exchanges, 2021–2025, BTC/ETH/SOL. Tardis.dev access 3 months or equivalent dump.** — target $3k–5k
>
> Willing to work with: (a) direct vendor invoice, (b) resold academic subscription slices, (c) custom data extracts. Not interested in: grey-market copies, scraped data without license, anything that can't be reproducibly cited in a published paper.

---

## Provenance & license discipline (non-negotiable)

For anything we buy:
- Record vendor name, purchase date, license terms, invoice reference in `ecomd/data/provenance/<vendor>.md`
- Preprocess scripts open-sourced; raw data never shared publicly
- In papers, cite vendor per license terms
- Before buying, verify license permits: (a) use in academic publication, (b) publication of derived results (e.g., plots, summary statistics)
- If a vendor forbids publication of derived results → do not buy, regardless of price
