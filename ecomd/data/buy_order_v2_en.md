# Data Buy Order v2 — Path C (high-frequency commitment, 2026-04-24 rev.)

Supersedes v2 early-draft and v1. Aligned to plan v3 + Path C: user chose
to commit to high-frequency data to support Nature Physics flagship with
physics-defensible protocols. Paper-sequence: **Paper A → Paper B (NP) →
Paper B.5 (PRL) → Paper C**.

## Budget envelope

| Bucket | Amount |
|---|---|
| Total budget approved | $50,000 |
| **Committed (Path C)** | **$8–12k** |
| Reserve (Phase 4/5 contingency) | $38–42k |

Path C requires $3-5k more up-front than the daily-only path, but this unlocks
NP probability 10-15% → 15-22% by giving physics-defensible responses to the
three main reviewer attacks: Jarzynski work protocol, TUR stationarity,
T_eff novelty beyond Mantegna-Stanley 1995.

---

## Tier 0 — already in git / free (cost $0)

- **yfinance**: SPY + ^GSPC daily 2015-2026 (pipeline → any ticker)
- **Binance**: BTCUSDT + ETHUSDT 1-min Q1 2024 (pipeline → any spot pair)
- **LOBSTER samples**: 8 ZIPs, 2012-06-21 (free academic)

**Sufficient for**: v0 through v1 training on SPX daily, smoke tests,
all Mac development.

---

## Tier A — Paper A (methods, NeurIPS/ICML), Wk 28 arXiv

- **Required**: nothing additional beyond Tier 0 (v1 trains on SPX daily + BTC 1-min)
- **Recommended**: use Tier B LOBSTER once purchased (Wk 16-20) for a short microstructure appendix
- **Committed spend**: $0 (all LOB needs come from Tier B purchase)

---

## Tier B — Paper B (Nature Physics flagship), Wk 54 submission

**THIS IS WHERE THE MONEY GOES.** Paper B's flagship load requires:
- A1 universality tested on ≥3 timescales (daily, minute, L2 event-level)
- B2 Jarzynski with physics-defensible work protocol (FOMC / earnings at intraday)
- B3 TUR at L2 event-rate where steady-state approximation is cleanest
- Cross-asset coverage across equity + crypto

### B.1 — Tardis.dev crypto L2 (MUST BUY, Wk 16)
- **Scope**: BTCUSDT + ETHUSDT × **6 months** (was 3 months in earlier draft), full L2 book + trades
- **Target price**: **$4,000–$5,500**
- **Why**: Provides the cleanest L2 event-level data for B3 TUR and for cross-asset universality at microstructure timescales. 6 months (not 3) to include ≥2 regime shifts for stationarity checks.
- **Decision gate**: buy at Wk 16 after v1 converges on SPX daily.

### B.2 — FirstRate (or AlgoSeek) US equity minute (MUST BUY, Wk 16-17)
- **Scope**: 20 symbols × **3 years** (2019-2022 preferred, covers COVID + inflation + SVB), 1-minute OHLCV + survivorship-bias-free
- **Target price**: **$1,500–$2,500**
- **Why**: A1 universality claim at intraday-equity timescale. Required for the "multiple timescales" language in Paper B abstract. Also supports Paper C crash EWS at minute resolution.
- **Decision gate**: buy concurrently with B.1.

### B.3 — LOBSTER research subscription (MUST BUY, Wk 17-18)
- **Scope**: 20-50 symbols × **2-3 years**, L10, covering 2019-2022 or 2020-2023
- **Target price**: **$3,000–$4,500**
- **Why**: Event-level US equity LOB for B3 TUR saturation claim, B2 Jarzynski at market-open/close, A1 at event timescale. Also serves Paper C optimal execution (Tier C merged here).
- **Decision gate**: buy at Wk 17 after B.1 and B.2 negotiations underway.

### Skip
- Bloomberg/Refinitiv institutional feeds — overkill at our scale
- Full NASDAQ TotalView raw — covered by LOBSTER reconstruction
- FX vendors (OANDA/Refinitiv FX) — yfinance EURUSD=X free version is enough

**Paper B committed spend**: **$8.5–12.5k** (was $3k in pre-Path-C draft).

---

## Tier B.5 — Companion PRL (TUR), Wk 54

Reuses Tier B data. **$0 additional**.

---

## Tier C — Paper C (applications), Wk 52+

Uses data purchased in Tier B:
- LOBSTER (B.3) → optimal execution
- FirstRate minute (B.2) → crash EWS at minute resolution
- Tardis L2 (B.1) → crypto execution benchmark

**Paper C committed spend**: **$0** (all covered by Tier B).

### Optional Tier C extensions (only if Paper A/B going well)
- Bloomberg corporate event calendar (~$500–1000) — for precise FOMC/earnings timestamps
- Interactive Brokers / institutional execution tape (~$1-2k) — to benchmark against real brokers
- **Decision gate**: evaluate at Wk 40+, purchase only if flagship likely to succeed.

---

## Purchasing timeline (Path C aligned to plan v3 rev.)

| Wk | Trigger | What to buy | $ |
|---|---|---|---|
| **now (Wk 17)** | v1 training begins | Nothing (Tier 0 covers v1) | 0 |
| **Wk 17-18** | v1 on SPX daily works | **Tardis L2 6mo + FirstRate minute 3y + LOBSTER subscription** | **$8.5–12.5k** |
| Wk 18-20 | Data ingestion | Nothing (just processing) | 0 |
| **Wk 20 (M1.5)** | High-freq data ingested | Nothing (milestone, not purchase) | 0 |
| Wk 22-28 | v1 + high-freq experiments | Nothing | 0 |
| Wk 28 (M3) | Paper A arXiv | Nothing | 0 |
| Wk 34 (M3.5) | A1 pilot gate | Nothing (already bought) | 0 |
| Wk 40+ | Paper C applications | Optional corporate event vendor | $500–2k |
| Wk 54 (M6) | NP submission | Nothing | 0 |

**Total committed up-front**: **$8.5–12.5k** (Wk 17-18).
**Total if optional Tier C ext**: **$9–14.5k**.
**Remaining reserve**: **$35.5–41.5k** (71–83% of budget).

---

## Decision flow under Path C

```
Wk 17 now: v1 converged on SPX daily
  ↓ buy high-freq data package (Tier B.1 + B.2 + B.3)
Wk 18-20: ingest + validate (M1.5 gate)
  ↓ [M1.5 fail = supplier delay] fallback to Tardis 3mo only, shift M3 to Wk 30
Wk 28 (M3): Paper A arXiv + multi-scale stylized facts table
  ↓
Wk 34 (M3.5): A1 pilot on 3 markets × 3 timescales
  ├── PASS ──→ continue flagship to M6
  └── FAIL ──→ Paper A priority locked, retreat to 2-PRL + 1 QF
              (still full value from high-freq purchases — used in PRL/QF)
```

**Key property**: even if flagship fails at M3.5, the $8-12k high-freq purchases are not wasted — they feed into Paper C (Tier C merged here), PRL retreat papers, and the stylized-facts reference table in Paper A.

---

## Why this differs from v2 early draft

- v2 early (pre-Path-C): $3k Tardis L2 3-month was the only high-freq commitment. NP probability 10-15%.
- **v2 Path C** (this): $8-12k Tardis 6mo + FirstRate 3y + LOBSTER 3y. NP probability 15-22%.
- The extra $5-9k buys Jarzynski protocol defensibility + TUR stationarity + multi-timescale universality — the three load-bearing reviewer defenses for NP.

## Why this differs from v1 (plan v2 era)

- v1 listed similar datasets but front-loaded without paper-gate discipline.
- v2 Path C ties every purchase to a specific Paper B claim, and explicitly notes which Paper C deliverables are already covered.

---

## Operational notes

- Provenance file per vendor package (`PROVENANCE.md` per dir) per CLAUDE.md rule.
- Upload raw data to R2 first (`r2://ecophys/vendor/<vendor>/<date>/`), then `scripts/h20_pull_from_r2.sh` to H20 NFS.
- Inquiry template for vendors: `ecomd/data/data_wishlist.md`.
