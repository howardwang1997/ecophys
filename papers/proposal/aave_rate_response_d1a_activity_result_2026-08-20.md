# Aave rate-step response spectroscopy — D1A activity result

**Decision:** PASS to a separately frozen intervention-ledger and identification gate.

**Formal run commit:** `c0ebdf50d`

**Canonical result SHA-256:**
`f3ca5d19539f0da3aa13ad509ceb4b2968365423d411241a69ca9e770714d1b9`
(independently verified after JSON read-back)

This result establishes that the frozen singleton panel is not visibly underpowered by pre-execution event
activity. It is not a behavioral response, causal effect, scaling collapse, inferred friction distribution,
at-risk borrower count, or paper claim.

## Decision

All 18 asset-event units pass the frozen rule:

- 18/18 total, versus the required 15;
- 15/15 primary rate-decrease units, versus the required 12;
- 3/3 reverse-sign units, versus the required two;
- 3/3 assets in every proposal, versus the required two.

The weakest weekly cells across the entire panel still contain 42 Borrows, 46 Repays and 49 distinct debt
users, compared with the frozen 10/10/10 floors. The weakest 28-day cells contain 564 combined actions and 210
distinct debt users, compared with the 200/50 floors. The pass is therefore not a threshold-edge accident.

| Proposal | Cohort | Asset | 28d Borrow | 28d Repay | 28d users | Min weekly B/R/users |
|---:|---|---|---:|---:|---:|---:|
| 3 | reverse | DAI | 611 | 490 | 386 | 64 / 60 / 84 |
| 3 | reverse | USDC | 2,572 | 1,471 | 1,442 | 452 / 228 / 409 |
| 3 | reverse | USDT | 2,395 | 1,212 | 1,275 | 481 / 222 / 390 |
| 94 | decrease | DAI | 217 | 347 | 262 | 42 / 46 / 50 |
| 94 | decrease | USDC | 2,892 | 2,311 | 1,758 | 442 / 348 / 418 |
| 94 | decrease | USDT | 2,674 | 1,807 | 1,718 | 579 / 299 / 501 |
| 130 | decrease | DAI | 293 | 290 | 210 | 55 / 49 / 49 |
| 130 | decrease | USDC | 3,825 | 2,416 | 1,844 | 628 / 395 / 496 |
| 130 | decrease | USDT | 4,627 | 2,607 | 2,214 | 977 / 438 / 702 |
| 159 | decrease | DAI | 358 | 324 | 223 | 77 / 74 / 64 |
| 159 | decrease | USDC | 4,140 | 3,117 | 1,931 | 996 / 656 / 674 |
| 159 | decrease | USDT | 5,083 | 2,919 | 2,316 | 986 / 583 / 700 |
| 247 | decrease | DAI | 343 | 355 | 306 | 60 / 53 / 77 |
| 247 | decrease | USDC | 6,947 | 5,542 | 3,356 | 1,292 / 952 / 1,003 |
| 247 | decrease | USDT | 6,700 | 5,181 | 3,425 | 1,228 / 962 / 1,074 |
| 271 | decrease | DAI | 350 | 600 | 359 | 60 / 67 / 76 |
| 271 | decrease | USDC | 9,026 | 8,846 | 4,157 | 1,766 / 1,190 / 1,097 |
| 271 | decrease | USDT | 8,399 | 8,620 | 4,552 | 1,580 / 1,234 / 1,133 |

Every weekly target timestamp maps exactly to an Ethereum block timestamp in this panel. The complete block
boundaries and four weekly cells for every unit are in the machine-readable result.

## Integrity and transport audit

The complete run made 481 `eth_getBlockByNumber` and 306 `eth_getLogs` calls through dRPC. One slow log range
was bisected without changing its block union. The public endpoint required 107 HTTP-429 retries and 720 seconds
of recorded backoff. This fragility is a reason to reproduce D1A against Flashbots or a controlled archive node
before relying on chain extraction for the main study; it does not alter the completed aggregates.

The outside-repository checkpoint was never needed for resume in the successful invocation and was deleted
after the final artifact was atomically written. The serialized result contains only boundary metadata,
Borrow/Repay counts, distinct debt-user counts and eligibility decisions. A key scan finds no raw `data`,
participant, amount, per-log block/transaction identifier, realized rate or utilization field.

No execution-block or post-execution log, `ReserveDataUpdated` event, position/balance call, paid dataset, GPU
or EcoMD run was used.

## What remains unresolved

High activity does not make the design causal. Governance proposals are announced before payload execution;
rate changes are endogenous to market conditions; risk-steward and other reserve changes may contaminate the
windows; the same assets recur across events; event participants are not automatically the correct at-risk
population; and utilization feedback makes the realized borrower-rate step state dependent.

The next gate must therefore build a complete reserve-intervention ledger, quantify announcement-to-execution
timing, search for clean cross-chain stagger or unaffected controls, and define falsification/negative-control
rules before any post-event response is opened. Passing D1A does not authorize GPU training or a paper claim.
