---
name: liquity-agentic-priority-queue-2026-08-20
description: "Outcome-blind Liquity V2 D0: qualify a public human-versus-autonomous priority-queue field study before any numerical outcomes, queue reconstruction, EcoMD, or GPU work."
metadata:
  node_type: memory
  type: project
---

# Liquity V2 agentic priority queue — 2026-08-20

After the formal Aave threshold route stopped, screened several free public-data systems without retuning the
failed design. Ethereum blob-fee feedback has excellent data but broad synchronization/controller claims collide
with EIP-1559 and blob-market dynamics work. Oracle-latency liquidations and x402/ERC-8004 agent economies are
already directly crowded by 2025–2026 studies. Morpho AdaptiveCurveIRM remains a fallback, but its controller
memory and vault-linked propagation are explicit in official design documents.

The selected candidate is Liquity V2. Borrowers choose rates and lower-rate Troves are redeemed first; borrowers
may self-manage or delegate a batch. Liquity's official ARM is an autonomous Internet Computer canister operating
three Ethereum batch-manager contracts, one per WETH/wstETH/rETH branch. It monitors debt in front, redemption
fees and adjustment timing. This supplies a real field setting in which human and autonomous controllers act on
the same ranked allocation mechanism.

The candidate NMI question is whether autonomous management reduces its users' rank exposure by exporting risk
to self-managed borrowers, and whether common strategies create synchronized adjustments or crowding. For fixed
debts, `sum_i d_i Q_i = 1/2[(sum_i d_i)^2 - sum_i d_i^2]`; a managed block of debt `D` crossing debt `C`
transfers exactly `D*C` pairwise exposure. Treat this as a standard-accounting-derived protocol lens, never as a
new theorem. Separate rank redistribution, BOLD demand/price effects and premature-fee/timing effects.

Branch `liquity-agentic-queue-feasibility-2026-08-20` freezes D0 before event-support counts in
`configs/empirical_physics/liquity_agentic_queue_d0_v1.yaml`. Pinned sources are `liquity/bold` at
`c8a5a4ee...` and `liquity/bold-ir-management` at `5877a9e0...`; the immutable end is Ethereum block
25,792,512, hash `608302fd...106d`, 2026-08-19 23:42:11 UTC. The official documentation binds ARM addresses
`e507...b60a`, `8869...bc14`, and `7700...a82b` to WETH, wstETH, and rETH.

D0 decodes only event type, operation code, Trove/manager identity, canonical log identity, branch and time from
TroveOperation, BatchedTroveUpdated, BatchUpdated and Redemption. It must not decode rates, debt, collateral,
redemption values/prices, queue rank, adjustment direction, liquidation outcomes or market prices. Blockscout
and OnFinality must reproduce the complete log-identity union exactly, while dRPC independently witnesses
historical deployment bytecode. Frozen support minima include 500 opened Troves,
100 ever-batched, 50 official-ARM Troves, 30 ARM rate updates, 200 manual adjustments, 50 redemption transactions
and 20 same-branch redemption-proximal ARM updates, with explicit cross-branch/date requirements.

Any source, deployment, transport or support failure closes this route before D1, numerical outcomes, queue
reconstruction, EcoMD and GPU. A pass authorizes only a separately frozen D1. The current two V100s and RTX remain
idle because D0 is a free public-RPC CPU audit. NMI requires a robust field externality plus held-out prospective
test; NCS additionally requires a genuinely new stochastic-priority identification/calibration method and
cross-system validation. Full plan: `papers/proposal/liquity_agentic_queue_d0_freeze_2026-08-20.md`.

## Transport-only v2 amendment (16:28 NZST)

The clean v1 run saw Blockscout's complete allowed-event count of 24,291, but no support breakdown. dRPC matched
through chunk 109, then returned only 15 versus Blockscout's 42 identities in blocks 23,573,043–23,583,042; an
identical repeat returned 14. dRPC is disqualified as a log witness. OnFinality exactly reproduced all 42
identities and all three frozen qualification shards (0/50/38), but its public endpoint lacks historical state at
the end block. Version 2 therefore uses Blockscout formal logs, OnFinality full log replication and dRPC only for
header/bytecode state. The runner proves source, chain, event, window, thresholds, forbidden fields, stop rules and
resources identical to parent SHA-256 `b4a45e62...90c14`. No numerical outcome, queue rank, support-gate breakdown,
EcoMD or GPU was opened. Amendment: `papers/proposal/liquity_agentic_queue_d0_transport_amendment_2026-08-20.md`.

## Resumable transport recovery v3 (17:30 NZST)

The clean v2 run reproduced qualification counts 0/50/38, completed Blockscout's 24,291-event formal scan and
matched OnFinality exactly at cumulative chunks 25/50/75/100 (2,507/3,939/6,110/8,126). Before printed
checkpoint 125, OnFinality returned HTTP 429 after all seven frozen retries. The runner exited without a result
manifest and before timestamps or the support summarizer, so this is an incomplete transport witness, not a
sample-gate or hypothesis failure.

Version 3 binds parent SHA-256 `221145272f...d7be`, leaves every scientific and existing transport field equal,
and adds only two recovery mechanisms: query OnFinality's three TroveManagers in one standard address-array
filter, and atomically checkpoint every completed chunk outside Git. The checkpoint stores only block number and
canonical log identity fields, binds config hash/Git SHA/provider/range/addresses/topics, and rejects any
non-contiguous, duplicate, non-canonical or digest-mismatched state. A capability diagnostic on already disclosed
chunk 110 returned the same 42 identities under Blockscout's three filters and OnFinality's combined filter,
digest `c42e2b7...6649d`. Ten focused tests, Ruff and strict mypy pass. No support breakdown, numerical outcome,
EcoMD or GPU has been opened. Recovery amendment:
`papers/proposal/liquity_agentic_queue_d0_recovery_amendment_2026-08-20.md`.

## Weight-aware public-limit recovery v4 (18:01 NZST)

The clean v3 attempt again matched qualification 0/50/38 and Blockscout total 24,291, then checkpointed four
OnFinality chunks/129 identities before chunk 5 exhausted the public HTTP 429 retry budget. No result, timestamp
attachment or support summary was produced. Official OnFinality documentation lists Ethereum's public limit as
10 response units/minute with burst 10 and says intensive Ethereum methods may carry higher response-unit
weights. The inherited 0.25-second replica pacing was therefore unsuitable.

Chunk 5 contains 105 already allowed events (WETH/wstETH/rETH 45/50/10). A post-cooldown combined query returned
all 105 and exactly matched Blockscout, digest `355a754e...31e6`, so the response is not intrinsically above the
burst cap; the narrow diagnosis is insufficient bucket balance at v3 retry times. Version 4 keeps every parent
field and adds a replica-only 6.1-second interval, two retries, then deterministic address-first/range-second
partitioning on exhausted 429/-32029. The outer 10,000-block chunk is checkpointed only after all disjoint
subqueries succeed. The four v3 chunks are not migrated across the config/Git binding. Thirteen tests, Ruff and
strict mypy pass. No scientific gate or forbidden outcome has been opened. Amendment:
`papers/proposal/liquity_agentic_queue_d0_weighted_rate_limit_amendment_2026-08-20.md`.
