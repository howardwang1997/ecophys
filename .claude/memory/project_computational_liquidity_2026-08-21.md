---
name: computational-liquidity-2026-08-21
description: "Fresh AMBER route: test whether nominal solver competition supplies functional fallback capability under coupled tasks, using CoW's official leave-one-winner scores. Formal T0 is frozen before blocks 25780000--25780499."
metadata:
  node_type: memory
  type: project
---

# Computational liquidity in autonomous-agent markets

After the Morpho Public Allocator D0 v2 transport failure, the next problem-first branch is
`problem-first-computational-liquidity-2026-08-21`. The candidate question is whether many nominally competing
agents remain functionally replaceable when tasks are coupled, not whether winner shares are concentrated.

CoW Protocol is the first deployed test system because its public competition response includes all proposed
solutions, order sets, winners, filtering and an official total score with each winning solver removed. Public
Ethereum `Settlement(address)` events can be enumerated through Blockscout and joined to the official
`by_tx_hash` endpoint without Dune, a vendor key or paid data. Exploratory checks used auctions `13600000`,
`13628466`, `13628554` and recent blocks near `25796557`; all are excluded from formal T0.

The formal T0 config is `configs/agent_markets/cow_computational_liquidity_t0_v1.yaml`, frozen before accessing
Ethereum blocks `25780000--25780499`. It tests transport, leave-one-winner counterfactual support and two fixed
coupling definitions. GREEN requires at least 30 submitted-coupled and 10 eligible-coupled competitions. If
submitted coupling survives but the fairness filter removes nearly all of it, the original route stops and only
a separately preregistered constraint-evaporation question may continue. Sparse coupling, unusable reference
scores or transport failure is RED; never widen the window or switch chains to rescue T0.

T0 uses Mac CPU only, below 5 core-hours and 1 GB. No V100, RTX 2060, H20, EcoMD or paid data is authorized. CoW
chains are replications, not independent-system transfer. NMI would require another deployed agent marketplace,
prospective policy value and an operator decision. NCS additionally needs an irreducible method with a guarantee
and a second independent, preferably non-finance or physically grounded system. Full plan:
`papers/proposal/computational_liquidity_t0_plan_2026-08-21.md`.

## Formal result

The formal run from clean implementation SHA `3b1ce6f3f` is **RED**. Blocks `25780000--25780499` contained 132
unique settlement transactions, 131 valid mappings and 119 distinct competitions. Reference coverage was
119/119 and all 132 winner removals were arithmetically valid, but settlement `132<200`, competition `119<180`,
low-criticality `12<20`, submitted coupling `12<30` and eligible coupling `2<10`. No association test was run.

The formal duplicate gate also flagged five auction IDs because the frozen canonical hash treated reversed
`transactionHashes` arrays as different. A post-run semantic audit found zero substantive duplicate conflicts;
future code sorts unordered arrays and has a regression test. The formal artifact remains unchanged and RED
still follows from the independent support failures. Do not widen the window, switch chains or start T1/GPU.

Result: `papers/proposal/computational_liquidity_t0_result_2026-08-21.md`. Post-route process decision: future
candidates require an outcome-blind event-rate/schema D-1 before freezing an absolute formal sample threshold.
