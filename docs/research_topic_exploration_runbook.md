# Research topic exploration runbook

This runbook turns the [Discovery Loop](research_discovery_loop.md) into a repeatable way
to search for a publishable question in simulated markets, market physics, and financial
physics. It does not authorize an experiment. The machine authority remains
[`research/discovery/protocol.yaml`](../research/discovery/protocol.yaml).

## What counts as a topic

A topic is not a method name, physics analogy, interesting plot, or broad application area.
It is the five-part contract

\[
(X,\;\operatorname{do}(A),\;Y,\;H_1\!:\!H_0,\;T),
\]

where `X` is a market-native state, `do(A)` is an admissible intervention, `Y` is a
measurable response, `H1:H0` is a prediction that distinguishes the proposed mechanism
from at least one serious alternative, and `T` is an analytic, simulator, or real-system
truth contract for the same estimand. The topic has scientific value only if its residual
claim survives reduction to established mathematics and remains useful when the result is
null.

Examples of valid starting objects are queue priority, matching, clearing, inventory,
latency, liquidation, collateral, executable order grammar, and liquidity replenishment.
“Phase transition,” “molecular dynamics,” “AI discovery,” and “digital twin” are not starting
objects; they may become interpretations only after a native mechanism and limit are proved.

## One bounded search cycle

Each cycle produces at most twelve worksheets and at most three machine topic cards. A large
idea count is not progress.

### 1. Choose three independent source lanes

Generate two to four questions from each lane:

1. **Mechanism-native lane:** start from an exchange or protocol action that changes the
   executable state transition, such as priority loss on amendment or a liquidation action
   grammar. Ask what invariant, obstruction, or response follows from that exact rule.
2. **Cross-engine discrepancy lane:** specify one intervention and observable in two
   independently maintained simulators. Treat disagreement as a question about missing
   state or mechanism, not as evidence that either engine is true.
3. **Prospective truth-asset lane:** start from a future randomized, staggered, or exactly
   scheduled real rule with observable assignment, pre-state, response, reuse rights, and a
   sealed future period. Derive the simulator question from that contract.

Do not combine lanes until each has a precise native object. This prevents a convenient
simulator effect from being retrofitted to an unrelated real event.

### 2. Write the claim before searching for support

For every worksheet, freeze:

- the native state and smallest admissible intervention;
- the primary observable, horizon, direction, and minimum scientifically meaningful effect;
- units, clocks, aggregation choices, and representation changes under which the claim
  should be invariant;
- two explicit nonclaims;
- two competing explanations with different predictions; and
- the result that would close the route.

Use the [screening worksheet](../research/discovery/templates/screening_topic_worksheet.md).
Reject a question that cannot be expressed without naming the desired algorithm or result.

### 3. Build killer twins before the novelty narrative

Construct at least two minimal pairs. One should hold the proposed summary fixed while
changing the outcome; the other should change the proposed cause while holding the outcome
law fixed. Add a unit-refinement, clock, label, or order-splitting test when relevant.

Typical failures are:

- same observed L2 state, opposite response because queue age or identity is hidden;
- same local influence, opposite global failure because high-order dependence differs;
- same aggregate liquidity, opposite executable action set;
- same event-index law, different physical-time law; and
- apparent criticality created by finite size, regime mixing, or a chosen observable.

If a three-state or two-queue toy kills the claim, record it in the route graph and stop.
Do not run a simulator to rediscover the counterexample.

### 4. Search four prior-art neighborhoods

Freeze the cutoff, verbatim queries, and inclusion rules before ranking the topic. Search
primary sources in four neighborhoods:

1. the exact market object and intervention;
2. the parent mathematical problem without market terminology;
3. the closest empirical or experimental identification design; and
4. hardness, impossibility, counterexample, and negative-result literature.

For every work record `problem`, `method`, `estimand`, `evidence`, `overlap`, and the exact
residual. “No paper with the same title” is not novelty. A standard method transplanted to a
market is not an irreducible contribution unless the hard market semantics force a new
theorem, algorithmic boundary, or measurement result.

### 5. Rank by the weakest link

Apply hard gates before scoring. A direct-prior reduction, non-identification twin, missing
same-estimand engine, absent real bridge, contamination, or unlawful data closes the current
formulation.

For survivors, score 1--5 on:

- residual novelty;
- falsifiability;
- identifiability;
- same-estimand two-engine feasibility;
- prospective real-bridge quality;
- value of either positive or null result; and
- information gain per unit cost.

Use the minimum score, not an arithmetic average. Retain only topics with every component at
least 3 and novelty and falsifiability at least 4. Then estimate a hostile T0 interval from
explicit failure events. Only its conservative lower bound matters for the 15% activation
gate.

### 6. Escalate evidence in the cheapest falsifying order

The default order is:

1. algebraic reduction or exact toy;
2. source and schema contract;
3. deterministic conformance fixture;
4. synthetic identifiability test;
5. negative and sham control;
6. strongest equal-budget simple baseline;
7. second independent simulator;
8. frozen prospective external test.

Stop at the first decisive failure. A disposable DX sandbox is justified only when a named
uncertainty cannot be resolved by steps 1--3 and a tiny outcome probe has positive decision
value. Its result is permanently exploratory-tainted and may only motivate a new D-3 card.

### 7. Freeze before any confirmatory outcome

An advancing topic gets a machine card, novelty manifest, decision entry, exact estimand,
baselines, multiplicity family, stop rule, budget, code/config hashes, and confirmation split.
It becomes `active` only after every protocol gate passes. D1 branches remain exploratory;
D2 must use a held-out simulator lineage, mechanism, market, vendor, or future period that
did not select the claim.

## Review questions

Before advancing a topic, an independent hostile review should be able to answer yes to all
of these:

- Can the claim be falsified by one predeclared result?
- Is the proposed cause defined on the full native state rather than an observational
  quotient?
- Do two independent engines implement the same intervention and observable?
- Is the real bridge a measurement of the same estimand rather than a visual analogy?
- Does the contribution remain after removing the market vocabulary?
- Is a null result informative enough to publish or permanently close a family?
- Is the confirmation asset genuinely unavailable to the selection process?

## Repository workflow

Do worksheet and paper-only screening first. Create a YAML card only when its object and
evidence paths are real; never add placeholder evidence to the registry.

```bash
conda run -n ecophys python scripts/validate_research_discovery.py
conda run -n ecophys python scripts/validate_research_discovery.py \
  --base-ref origin/dependabot-cooldown-verification-liquidity-2026-08-21
conda run -n ecophys python scripts/validate_research_route_graph.py
conda run -n ecophys python scripts/test_research_discovery_oci_conformance.py \
  --verify-recorded-report
```

The first new search cycle should use the three lanes above in parallel conceptually, then
retain at most one D-1 candidate. It should not begin by reopening criticality, generic
surrogates, rare-event sampling, hydrodynamic limits, entropy production, or other families
already closed in the route graph.
