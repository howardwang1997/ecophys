# Data Buy Order v2 — Paper-Aligned (2026-04-24)

Supersedes `buy_order_v1.md`. Priority ordering is realigned to the plan v3
paper-submission sequence: **Paper A → Paper B (Nature Physics) → Paper B.5
(companion PRL) → Paper C**. We buy only what each paper load-bears on, in
the order those papers ship.

## Budget envelope

| Bucket | Amount |
|---|---|
| Total budget approved | $50,000 |
| **Committed up-front** (below) | **$6–10k** |
| Reserve (Phase 4/5 contingency) | $40–44k |

Reserve-heavy by design: v3 puts real probability on flagship failure. Keeping
most of the budget liquid lets us pivot data buys if Gate 2 (M3.5) reroutes us
away from Nature Physics into a PRL-only path.

---

## Tier 0 — already in git / free (cost $0)

Already committed to the repo under `data/sample/`:

- **yfinance**: SPY + ^GSPC daily, 2015–2026. Pipeline extensible to any ticker.
- **Binance**: BTCUSDT + ETHUSDT 1-min, 2024 Q1. Pipeline extensible to any spot pair.
- **LOBSTER academic samples**: 8 ZIPs (AAPL, AMZN, GOOG, MSFT, SPY) on 2012-06-21.

**Sufficient for**: v0 through v1 training, smoke tests, all development work
through M2 (Wk 16).

---

## Tier A — Paper A (methods, NeurIPS/ICML main), Wk 26 arXiv

Paper A ships at M3 (Wk 26). It needs:

- SPX + BTC returns for v1 training (✓ already in Tier 0)
- Stylized-facts tables across 11 Cont metrics (✓ already produced, exp 000–005)
- Optional: microstructure appendix with LOB comparison

### Required
**None**. Paper A can ship entirely on free data.

### Recommended (if LOB microstructure section desired)
- **LOBSTER academic subscription**: 10–20 symbols × 1 month, L10
  - **Target price**: $500–$1,500
  - **Why**: Paper A reviewer-2 will ask "does your agent simulator match real
    LOB microstructure?" Answer needs ≥20k events on 5+ symbols.
  - **Decision gate**: Only buy after v1 converges ≥7/11 on SPX (M2, ~Wk 16).
    If v1 stalls, this money stays in reserve.

### Skip
- Any vendor quote > $2k just for LOB samples — the free LOBSTER samples + a
  Tier C purchase later are cheaper and cover the same claim.

**Paper A committed spend**: $0 guaranteed; $500–1500 contingent on M2 success.

---

## Tier B — Paper B (Nature Physics flagship), Wk 48

Paper B carries the flagship. Its load-bearing claim is cross-market
universality (A1: T_eff scaling) + Jarzynski self-consistency (B2). Gate 2
at Wk 30 kills the paper if universality fails, so data must be in place by
Wk 28–30.

### Required
8 markets × multi-year returns. Most yfinance-free:

| Market | Ticker | Cost |
|---|---|---|
| S&P 500 | ^GSPC | $0 (✓ have) |
| Russell 2000 | ^RUT | $0 (yfinance) |
| Nikkei 225 | ^N225 | $0 (yfinance) |
| DAX 30 | ^GDAXI | $0 (yfinance) |
| FTSE 100 | ^FTSE | $0 (yfinance) |
| Hang Seng | ^HSI | $0 (yfinance) |
| Bitcoin | BTCUSDT | $0 (✓ have) |
| Ether | ETHUSDT | $0 (✓ have) |
| (FX optional) | EURUSD=X | $0 (yfinance) |

Just extend the existing yfinance ingest to the new tickers. No vendor required.

### Strongly recommended
- **Tardis.dev crypto L2 data**: BTCUSDT + ETHUSDT × 3 months, full order-book changes
  - **Target price**: $2,500–$3,500
  - **Why**: A1 universality claim on daily-only data is vulnerable to
    "you didn't test at microstructure timescales" critique. Tardis L2 for crypto
    (cheapest path to L2 across asset classes) closes this attack vector.
  - **Decision gate**: Buy at Wk 27 if Gate 2 (A1 pilot on 3 markets at daily) looks promising.

### Skip
- Higher-tier equity LOB for universality (e.g., $10k+ minute data vendors).
  Daily + crypto L2 is enough for the universality claim; don't overbuy.

**Paper B committed spend**: $0 guaranteed; **$3k contingent** on Gate 2 pilot showing promise.

---

## Tier B.5 — Companion PRL (TUR saturation)

Reuses the same data as Paper B. **No additional spend**.

---

## Tier C — Paper C (applications, QF/JEDC), Wk 45+

Paper C has two deliverables: crash EWS (shares Paper B data) + optimal
execution (needs LOB messages).

### Required (for optimal-execution deliverable only)
- **LOBSTER research subscription** OR **AlgoSeek LOB feed**
  - 20–50 symbols × 2–3 years, L10, covering 2019–2022 or 2020–2023
  - **Target price**: $3,000–$5,000
  - **Why**: You can't benchmark execution strategies without real LOB messages.
    Free LOBSTER samples cover 1 day × 8 symbols — insufficient for robust RL
    training or Almgren-Chriss backtest.
  - **Decision gate**: Only buy if Paper A is accepted or clearly on track (Wk 34).

### Skip
- Tier-1 institutional feeds (NASDAQ TotalView direct) — overkill at our scale
- Alt-data / news / sentiment — outside Paper C scope

**Paper C committed spend**: $3–5k contingent on Paper A trajectory.

---

## Purchasing timeline (aligned to plan v3 gates)

| Wk | Trigger | What to buy | $ |
|---|---|---|---|
| **now (Wk ~17)** | v1 training begins on H20 | nothing | 0 |
| Wk 22–24 | v1 converged ≥7/11 | nothing (run on existing data) | 0 |
| Wk 26 | **M3 arXiv submission** | yfinance tickers extended to 8 markets (free) | 0 |
| Wk 27–28 | **before Gate 2 A1 pilot** | (optional) Tardis crypto L2 | $3k |
| Wk 30 | **Gate 2 outcome** | (contingent) small LOBSTER for Paper A revision | $500–1500 |
| Wk 34–36 | Paper C starts, A1 full proceeding | (contingent) LOBSTER subscription | $3–5k |
| Wk 48+ | Paper B/B.5 submission | nothing (data locked in) | 0 |

**Maximum total committed**: $6.5–9.5k out of $50k.

---

## Flowchart — decision points

```
Now ───── v1 on free data ─────────────┐
                                        │
                              v1 ≥ 7/11 ?
                                ├── NO ──→ Stay on free data, iterate architecture
                                └── YES ──→ Wk 26: arXiv Paper A preprint
                                            │
                                            ↓
                              Wk 27: Buy Tardis crypto L2? ($3k)
                                ├── (Gate 2 pilot looks good) YES ─→ Buy
                                └── (Gate 2 pilot weak)       NO  ─→ Save for reserve
                                            │
                                            ↓
                              Wk 30 Gate 2: A1 pilot universality?
                                ├── PASS ──→ Continue Paper B flagship;
                                │            Wk 34: Buy LOBSTER ($3–5k) for Paper C
                                └── FAIL ──→ Retreat to 2-PRL split;
                                             DO NOT buy LOBSTER yet
                                             (Paper C deferred)
```

---

## Contacts / operational notes

- Your vendor-facing inquiry template for quotes lives in
  `ecomd/data/data_wishlist.md`.
- All purchases store data first in R2 (`r2://ecophys/vendor/<vendor>/<date>/`),
  then rsync to H20 NFS via `scripts/h20_pull_from_r2.sh`.
- Every vendor package gets a provenance file (`PROVENANCE.md` in its dir) per
  `CLAUDE.md` data-discipline rules.

---

## Why this differs from buy_order_v1

- v1 was written under plan v2 (series-paper, no Nature Physics commitment).
  It front-loaded US equity minute + LOB purchases.
- v2 is written under plan v3 (Nature Physics flagship with retreat).
  It defers the bigger LOB spend to Paper C / Tier C, and adds Tardis crypto L2
  as the strongest single-purchase bet for Paper B's universality claim.
- Net effect: less money committed up front, more reserve for Phase 4/5
  contingencies, purchases gated by actual research milestones.
