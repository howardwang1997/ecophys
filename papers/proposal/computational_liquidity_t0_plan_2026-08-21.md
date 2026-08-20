# Computational liquidity in agent markets — T0 plan

## Decision

Start a new **AMBER, problem-first** route on branch
`problem-first-computational-liquidity-2026-08-21`. The immediate system is the live CoW Protocol solver
competition. The plain-language question is:

> When many autonomous agents compete for the same task, how many are actually capable of replacing the best
> agent when the task becomes coupled or difficult?

The candidate object is **computational liquidity**: near-optimal fallback capability available inside the
platform's fixed decision deadline. It is not participant count, winner concentration, a crypto-return signal or
a renamed stylized fact. The first formal experiment is deliberately small and can close the route before any
GPU job, paid data, EcoMD model or large download.

ERCOT RTC+B remains a parked alternative, not a parallel experiment. Its two live 2025 production switches are
physically important, but each two-hour event bundles real-time co-optimization, battery state representation
and load-frequency-control changes. Two announced, manually coordinated event clusters cannot support the
current causal or mechanism claim without pseudo-replication. CoW instead exposes repeated task instances and an
official leave-one-winner counterfactual for each auction.

## Deployed mechanism and observable counterfactual

For auction `a`, let `S_a` be the submitted solutions, `i(s)` the solver that submitted solution `s`, `O_s` the
orders covered by `s` and `v_s` its score. The protocol selects a compatible set of winning solutions. Define

```text
V_a       = sum of scores of the recorded winning solutions,
V_a(-i)   = official reference score when winning solver i is absent,
c_ai      = 1 - V_a(-i) / V_a.
```

`c_ai` is the observed welfare dependence on one winning solver, conditional on the submitted solution set and
the protocol rule. The one-failure survival score is

```text
L_a(1) = 1 - max_i c_ai.
```

This definition is useful but is **not a new theorem**. Participant count cannot identify `L_a(1)`: arbitrarily
many weak duplicate agents can coexist with one indispensable agent, while two equal alternatives can give zero
single-agent loss. The scientific question is whether task coupling predicts this measured replaceability in
live autonomous-agent markets, whether that relationship survives protocol epochs and held-out time, and whether
it supports a decision about admission, incentives or fallback routing.

The public API's `referenceScores` are the protocol's total auction scores with a winning solver removed; they
are not scores invented by this project. Proposed solution order sets permit a task-overlap graph. In T0, an
auction is:

- **submitted-coupled** when a submitted multi-order solution covers at least two orders and at least one of
  those orders is also covered by a different solver;
- **eligible-coupled** when the same condition holds after removing `filteredOut=true` solutions.

This is only an observable support definition. A graph decomposition, phase transition or universal law is not
claimed in T0.

## What is occupied already

| Nearest work | Already established | Boundary for this route |
|---|---|---|
| [Chitra et al., *An Analysis of Intent-Based Markets*](https://arxiv.org/abs/2403.02525) | solver entry can be restricted by cost and congestion | no broad “solver markets become concentrated” claim |
| [Canidio and Henneke, fair combinatorial auctions](https://arxiv.org/abs/2408.12225) | mechanism design for fair selection and solver rewards | no claim that the CoW selection rule is new |
| [Yuminaga et al., execution welfare](https://arxiv.org/abs/2503.00738) | empirical welfare comparison across solver-based exchanges | average execution quality alone is occupied |
| [Zhang, solver-reward reform](https://arxiv.org/abs/2607.21955) | CIP-74 changed solver market shares by order size | no CIP-74 concentration/event-study paper |
| [Marfinetz, hybrid CoW solver](https://arxiv.org/abs/2510.21647) | algorithm performance under a tight auction deadline | no “first solver for CoW” or generic deadline claim |
| [CoW solver rewards](https://cowswap.mintlify.app/cow-protocol/reference/core/auctions/rewards) | reference scores, second-price logic and revert penalties | the official counterfactual is data, not our novelty |

The nearest-work search found no direct empirical study of complexity-conditioned leave-one-solver welfare in a
live intent auction, but that is a provisional audit result, not a novelty claim. A forward search must be rerun
before any paper title or abstract is frozen.

## T0 is frozen before the formal window

Configuration `configs/agent_markets/cow_computational_liquidity_t0_v1.yaml` freezes an untouched Ethereum block
window, exact contract and event identity, endpoints, retries, retained fields and gates. Exploratory transport
checks touched auctions `13600000`, `13628466` and `13628554` and recent blocks near `25796557`; none may enter
the formal T0 sample. The formal interval `25780000--25780499` was selected before querying its events or
competitions.

The acquisition path is:

1. enumerate `Settlement(address)` events from the deterministic settlement contract with Blockscout's public
   event-filter API;
2. sort and deduplicate settlement transaction hashes;
3. query CoW's official `api/v2/solver_competition/by_tx_hash/{hash}` endpoint for every retained hash;
4. require the queried hash to occur in the returned `transactionHashes` and deduplicate identical auction IDs;
5. store the raw API responses as an immutable T0 source shard plus a provenance manifest and a derived summary.

Blockscout is an indexer, not canonical consensus. T0 therefore checks transport and support only. A larger study
must independently reconcile the event identities against canonical receipts or a second finalized index before
making empirical claims.

## Frozen gates and decision tree

T0 passes transport only if all of the following hold:

- the formal block interval returns at least 200 unique settlement transactions;
- at least 98% of those hashes map to valid CoW competition responses;
- every accepted response contains its queried transaction hash, a positive auction ID, solutions and auction
  orders, with no conflicting duplicate payload for one auction ID;
- at least 180 distinct competitions survive; and
- at least 90% of competitions have an official reference score for every distinct winning solver.

The counterfactual is usable only if at least 100 winning-solver removals satisfy
`0 <= V_a - V_a(-i) <= V_a` exactly. Support for a non-degenerate response additionally requires at least 20
removals with `c_ai <= 0.001` and at least 20 with `c_ai >= 0.01`. These are support gates, not hypothesis tests.

The mechanism decision is prospectively forked:

1. **GREEN for a new T1 freeze:** at least 30 auctions are submitted-coupled and at least 10 are
   eligible-coupled. T0 still cannot claim that coupling causes fragility.
2. **AMBER constraint-evaporation fork:** at least 30 are submitted-coupled but fewer than 10 are
   eligible-coupled. The original complexity route stops; a separate preregistration may ask whether platform
   validation systematically removes combinatorial alternatives.
3. **RED:** fewer than 30 submitted-coupled auctions, an unusable reference-score distribution, or any transport
   failure. Do not enlarge the window, switch chains, relax the definition or train a model to rescue it.

No comparison between coupling and criticality is evaluated until after these support gates are immutable. This
prevents a mechanism story from being selected after seeing its association.

## If T0 passes

### T1: retrospective field regularity

- Freeze at least 90 days on Ethereum plus three protocol-operated chains, stratified by scoring-rule/source
  epoch.
- Reconstruct solution-order overlap, solver capability overlap, filtering, winner criticality and settlement
  outcomes.
- Fit transparent count/size/time baselines first. Test whether coupling adds held-out information about
  `L_a(1)` beyond order count, notional proxies, solver count, gas regime and fixed time effects.
- Use chronological train/validation/test splits. No causal wording is allowed because task difficulty and solver
  participation are endogenous.

### T2: intervention and decision value

- Locate a source- and governance-dated change to deadline, validation or solution-selection mechanics that was
  not chosen from the outcome plot. Pre-trends, concurrent changes and protocol anticipation are mandatory.
- Evaluate a predeclared fallback/admission/incentive policy on held-out auctions. The target is reduced
  winner-removal loss or failed-settlement loss, not better price prediction.
- Seal a prospective future interval before the policy is run.

### Transfer and venue ladder

- Multiple CoW chains establish replication, not independent-system transfer.
- **NMI** requires the computational-liquidity object to transfer to another deployed agent marketplace, a
  prospective failure/policy result and a real operator decision.
- **NCS** additionally requires an irreducible inference or optimization method with a proof/finite-sample
  guarantee and a second non-finance or physically grounded multi-agent system. A CoW-only graph metric is not an
  NCS contribution.

## Data and compute requirements

| Stage | Data | CPU and storage | GPU |
|---|---|---|---|
| T0 | 500 Ethereum blocks; public settlement events and competition JSON | below 5 core-hours, below 1 GB on Mac | forbidden |
| T1 | 90+ days, four CoW-operated chains, source/governance epochs, canonical receipt reconciliation | 100--1,000 core-hours, 20--200 GB; CPU may run on V100 hosts | forbidden unless a frozen learned model is later justified |
| T2 | intervention metadata, settlement failures, sealed future interval | 500--5,000 core-hours, 0.2--2 TB | 20--200 V100-equivalent hours only after non-neural baselines |
| NMI | independent agent marketplace plus prospective policy trial | 2,000--20,000 core-hours, 1--10 TB | 100--1,000 V100-equivalent hours as measured |
| NCS | second independent domain and method-level simulation/uncertainty study | 10,000--100,000 core-hours, 5--50 TB | 500--10,000 V100-equivalent hours across expandable non-H20 pools |

Current two V100 32 GB nodes and the RTX 2060 are not needed for T0. They may later run CPU acquisition or
analysis, but idling GPUs is preferable to training before the empirical object exists. Future scaling may add
heterogeneous CUDA/CPU workers; no plan assumes H20.

## Pinned primary sources

- CoW Orderbook OpenAPI tag
  [`v2.375.0`](https://raw.githubusercontent.com/cowprotocol/services/v2.375.0/crates/orderbook/openapi.yml);
- CoW database schema for `competition_auctions`, `proposed_solutions`, `reference_scores` and `settlements`
  ([official repository](https://github.com/cowprotocol/services/blob/main/database/README.md));
- CoW's mathematical description of the solving problem
  ([official documentation](https://cowswap.mintlify.app/cow-protocol/reference/core/auctions/the-problem));
- deterministic settlement contract source and deployment documentation
  ([official repository](https://github.com/cowprotocol/contracts/blob/main/src/contracts/GPv2Settlement.sol));
- Ethereum settlement contract `0x9008d19f58aabd9ed0d60971565aa8510560ab41`;
- `Settlement(address)` topic
  `0x40338ce1a7c49204f0099533b1e9a7ee0a3d261f84974ab7af36105b8c4e9db4`.
