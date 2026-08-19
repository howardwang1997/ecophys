# dYdX fixed-funding-carry D1A activity result — 2026-08-20

## Decision

**STOP the dYdX-only causal paper before bulk tick acquisition.** Only 1 of 21 development markets passes the
pre-registered activity rule; the frozen stop line is 15. Proposal 317 cannot be opened to rescue this result,
and the threshold cannot be relaxed after seeing the counts.

The formal run used clean commit `fba2c9a2b` and 21 free Indexer requests. Its canonical result SHA-256 is
`536cfcd560dff4f4b130eab9122a5db074b7d19f9ef3f01246d2837ba4002d66`.

## Result

All markets have all 28 requested daily candles, so the failure is genuine low activity rather than missing
history.

| Market | Days with at least 100 trades | Decision |
|---|---:|---|
| HYPE | 28 | eligible |
| ENA | 20 | ineligible |
| SPX | 15 | ineligible |
| ASTER | 11 | ineligible |
| KAITO | 5 | ineligible |
| PAXG, POPCAT | 4 each | ineligible |
| MNT | 3 | ineligible |
| BERA, DRIFT | 2 each | ineligible |
| all remaining 11 markets | 0 | ineligible |

`ENA` misses by one day, but adding it post hoc would still leave only two markets and is forbidden. Aggregate
counts also cannot replace the frozen per-market activity rule.

## Semantic validation

The official dYdX candle generator increments `trades` by one for each `TradeContent` and initializes a new
trade-bearing candle at one; empty candles carry zero. Therefore D1A measured trade events, not volume or an
unrelated field. Every frozen window contains 28 distinct UTC daily rows.

The result retained only UTC dates and daily trade counts. It did not retain OHLC, volume, OI or midpoint values,
did not request any individual trade, and did not touch post-event candles, proposal 317 or the proposal-220
outcome window. No GPU, paid data or EcoMD was used.

## Scientific interpretation

This is a design-support failure, not evidence that fixed carry has no behavioral effect. The governance
intervention is unusually clean, but the treated markets are too thin for the frozen five-minute signed-flow
estimand and clustered multi-market inference. A one-market HYPE event study would be an anecdote and cannot
support the proposed switching-friction story, NMI or NCS.

The reusable assets are the fixed-dose identification logic, exact block reconstruction, taker-side semantics,
outcome-blind pipeline and stop discipline. The next search should require, before a hypothesis is frozen:

1. an on-chain or otherwise legally usable parameter intervention;
2. at least 15 demonstrably active treated units, or repeated independent interventions in highly liquid units;
3. a public event-level action stream; and
4. a claim stronger than generic activity around a scheduled clock.

Candidates should be screened by metadata-level activity first. High-liquidity lending-rate or carrying-cost
governance changes on Aave, Compound or Maker are plausible next domains, but none is authorized until a
nearest-work, intervention-count, data-rights and activity audit passes. The current dYdX D1B/GPU queue is empty.
