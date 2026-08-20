# Morpho Public Allocator D0 transport v2 — qualification result

**Decision:** PASS to the single jointly launched Ethereum/Base full D0.

**Formal run commit:** `68bf0ecef75f8993bf22a44391bf907630c0ca11`

**Parent scientific config SHA-256:**
`bc6fc21cfd6b782280ace89d4d854b603dd19370bdad3c6d4803c72557333c60`

**Transport amendment SHA-256:**
`b549efa43be88d9ce9385224f61158767b042df824fef447f959b600c66634a4`

**Canonical payload SHA-256:**
`d9b28e6549d120fd94acfc378946f1e5deb475abf67b2de3f4870acc18aa65de`

**Result-file SHA-256:**
`4c42da0ef988da9798b35b5f1c17c5747b14e1baae38475989710402fe934343`

The eight-way deterministic Portal acquisition reproduced every v1 qualification count and canonical identity
digest exactly. Every resulting Portal identity set also remained exactly equal to the fixed full-RPC set.
Cutoff headers matched the Portal, full-scan RPC and separate receipt RPC on both chains.

## Exact reproduction

| Chain | Frozen shard | Events | Parent-v1 digest reproduced | Portal/RPC exact |
|---|---:|---:|---|---|
| Ethereum | deployment | 0 | pass | pass |
| Ethereum | midpoint | 335 | pass | pass |
| Ethereum | cutoff | 231 | pass | pass |
| Base | deployment | 0 | pass | pass |
| Base | midpoint | 220 | pass | pass |
| Base | cutoff | 2 | pass | pass |

Each original 10,000-block shard was covered by eight disjoint inclusive 1,250-block pieces. All 48 pieces
completed, the canonical unions contained no duplicate identity, and their endpoints covered the six parent
intervals exactly. The identity digests are unchanged from the immutable v1 qualification artifact
`d59b0184cc2a3e616abbbd158d47dc6952643dd9fecd31567e37811728b3edfe`.

## Transport observations

Ethereum used 33 parallel Portal requests plus two coordinator requests and one transparent retry. Base used 61
parallel requests plus two coordinator requests and one retry. Both full RPCs used one header request and three
`eth_getLogs` calls with no range split, topic split, rate-limit retry or server-error retry. Each receipt RPC was
used only for the frozen cutoff header.

Wall time was 96.62 seconds versus 111.05 seconds for v1. This small-shard qualification is an equivalence and
concurrency-safety test, not evidence of an eightfold full-range speedup: fixed headers/RPC work and short tasks
dominate it, while the formal full ranges have hundreds of 100,000-block shards. Full runtime therefore remains
uncertain and must be reported from both workers rather than inferred from the qualification ratio.

## Data and claim boundary

- No transaction receipt, Morpho Borrow event, non-indexed log data, amount, balance, cap, utilization, interest
  rate, price, liquidation, incident label or outcome was opened.
- No raw response or event identity is retained in the artifact; only counts, canonical digests and transport
  summaries remain.
- No paid data, EcoMD or GPU was used.
- The repeated shard counts are transport fixtures, not full candidate counts and not genuine JIT events.

The canonical payload digest was independently recomputed from the saved JSON and matched exactly. The result
file digest was computed independently from the saved bytes.

## Authorized next step

Commit and push this immutable qualification artifact and report. From the next clean upstream-matched SHA,
launch Ethereum on V100-A and Base on V100-B before inspecting either chain result. Both jobs must use their
frozen worker IDs and empty `CUDA_VISIBLE_DEVICES`, write aggregate-only artifacts outside their repositories,
and share the automatically derived formal batch id. Pull both artifacts, verify their payload and file hashes,
then merge once under the original v1 gates.

A D0 failure still closes the route before amounts, outcomes, D1, EcoMD, GPU work or paid data. A pass authorizes
only a separately frozen exact replay; it does not establish delayed memory, causality, novelty, NMI fit or NCS
fit.
