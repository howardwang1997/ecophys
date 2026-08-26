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

## Why the search is staged

The process combines four ideas that solve different problems:

- [strong inference](https://doi.org/10.1126/science.146.3642.347) starts from rival
  explanations and a result that excludes at least one of them;
- [optimal model-discrimination design](https://doi.org/10.1093/biomet/62.2.289) chooses
  observations for their ability to separate models rather than for generic sample volume;
- [AutoDiscovery](https://proceedings.neurips.cc/paper_files/paper/2025/hash/23b127521af7ca7a42f5cdb7507be4f2-Abstract-Conference.html)
  uses progressive widening to allocate a fixed exploration budget, but its surprise reward
  is only an attention score and cannot confirm a claim; and
- [value of information](https://doi.org/10.1177/0272989X211026292) asks whether a proposed
  observation is likely to change a decision enough to justify its cost.

The [Heilmeier questions](https://www.darpa.mil/about/heilmeier-catechism) add the plain-language
tests: what is being attempted, what is new, who cares, what it costs, and what exams decide
success. None of these tools makes novelty automatic. Together they motivate a staged portfolio
in which cheap exclusions happen before full reviewer-style qualification.

## Scientific value before venue value

A question has scientific value when it can close a named uncertainty and remains useful under
both answers. Record value in three non-substitutable parts:

1. **Epistemic closure:** which rival explanation, theorem class, or measurement ambiguity can
   be removed by the result?
2. **Reusable residue:** what proof, counterexample, data contract, calibrated measurement,
   simulator fixture, or negative result remains if the headline is null?
3. **Decision or transfer value:** which future model choice, experiment, market-design claim,
   or cross-system prediction changes?

Publication probability is reported separately. A fashionable narrative, surprising plot, or
large benchmark score does not satisfy this definition.

## One bounded two-speed search cycle

The machine limits are 12 raw question programs, 6 quick screens, 3 collision/contract screens,
2 full hostile audits, and 1 machine card. Every raw question and final disposition is recorded in
[`search_cycle_ledger.yaml`](../research/discovery/search_cycle_ledger.yaml). Unselected ideas are
not silently discarded.

### F0 — harvest unresolved forks, not topic titles

Draw questions from four source lanes:

1. **Unresolved model disagreement:** two primary models explain the same observation but predict
   different responses under a controllable condition. Count an opposite-sign pair only when the
   state, legal intervention, response, and conditioning set are the same; different estimands are
   adjacent evidence, not a model fork.
2. **New truth or control capability:** a new field schema, exact simulator state, randomized rule,
   formal implementation, or sealed future asset can adjudicate a question that was previously
   untestable.
3. **Market-native action or constraint:** an executable priority, clearing, inventory, collateral,
   timing, or settlement rule creates a possible obstruction or response.
4. **Cross-domain theorem with a market-specific obstruction:** a parent theorem nearly applies,
   but priority, integer allocation, endogenous adaptation, or another exact market semantic may
   make a stronger statement false or require a new boundary.

Cross-engine disagreement is a validation instrument, not a source lane by itself. It becomes
scientific only after a named mechanism fork exists.

For each raw program record only:

- the native object;
- explanations `H1` and `H0`;
- one observation or theorem outcome that separates them;
- positive-answer and null-answer value; and
- the source lane and topic archetype.

Do not yet write a full five-part contract, search fifteen papers, or pin every simulator.

### F1 — quick screen at most six programs

Use at most three anchor primary works and at least one exact killer toy. Ask:

- Is this already a route-graph duplicate or an immediate parent-problem corollary?
- Can `H1` and `H0` actually predict different observables under a legal intervention?
- Does a positive or null answer remove a meaningful uncertainty?
- Is there a plausible truth source, without yet requiring the complete final contract?
- For a cross-domain effect, is its control parameter market-native, and does the residual survive
  changes of legal state representation, unit, clock, initial-condition family, and distance
  metric? An analyst-defined temperature, condensate, or relaxation ordering is not sufficient.
- For a proposed dimensionless law, can every proposed group be held fixed while one omitted legal
  event kernel or strategic state varies? A sign reversal kills the low-dimensional law; a repair
  that must encode the full kernel is a measurement reformulation, not a universal collapse.

Select by Pareto dominance on discriminative power, identifiability, residual novelty, positive/null
value, transfer, feasibility, and cost of the next decisive update. Do not use an arithmetic score
to average away a fatal weakness. Close or deduplicate cheap failures; advance at most three.

### F2 — route at most three programs by archetype

Assign one archetype before expanding the evidence contract:

| Archetype | Early truth contract | Evidence required only when the claim expands |
|---|---|---|
| Theory/mechanism | Analytic statement, proof route, and minimal counterexample | A theorem false in the parent class, matching boundary/lower bound, and executable falsifiers for computational claims |
| Measurement method | Analytic or synthetic truth, calibration/coverage, and failure regimes | A validated observation bridge and external system for claims beyond truth-defined benchmarks |
| Empirical intervention | Assignment, pre-state, outcome, interference, timing, and reuse-rights schema | Independent replication; simulators only if fidelity or transfer is claimed |
| Simulator method | Same-estimand analytic truth or gold simulator plus equal-budget baseline | Two independent lineages, hard negatives, cost--accuracy frontier, and a real bridge for sim-to-real claims |

Now search at least six primary works across the exact market object, parent mathematics,
identification design, and impossibility/counterexample neighborhoods. Build the full five-part
contract and a second killer twin only for the strongest programs. Advance at most two to F3; a
third unresolved program may be explicitly deferred rather than mislabelled failed.

### F3 — full hostile audit of at most two programs

Before opening the full evidence neighborhood, create the exact F3 subject node and append its
full-T0 forecast to `forecast_ledger.yaml`. If evidence has already been opened, any probability is
diagnostic only and is ineligible for calibration; never backfill it. Only here require the current
fifteen-primary-work manifest, at least two killer tests, exact
simulator/data contracts appropriate to the archetype, contamination plan, explicit failure events,
and hostile-T0 forecast. “No paper with the same title” is not novelty. A standard method applied to
a market needs a theorem, algorithmic boundary, or measurement result caused by hard market
semantics.

The search order remains:

1. route-graph duplicate and exact parent reduction;
2. algebraic counterexample or killer twin;
3. primary-work collision;
4. source, schema, licence, and state contract;
5. deterministic conformance fixture;
6. synthetic identifiability and sham controls;
7. equal-budget baseline and second independent system;
8. frozen prospective external test.

Stop at the first decisive hard failure and record it. A disposable DX sandbox is justified only
when steps 1--4 cannot resolve a named uncertainty and a tiny probe has positive decision value.
Its evidence remains permanently exploratory-tainted.

### Probability and action policy

`hostile T0` is the elicited probability that a frozen formulation survives all named T0 gates and
becomes eligible for an outcome-blind active decision. Its lower endpoint is not a confidence bound,
truth probability, venue probability, or novelty score.

The 15% lower-endpoint rule is retained only as a provisional portfolio brake on costly `active`
status. It has no prospective full-T0 calibration yet. It must not prune F0, close a question, or
block D-3/D-2 paper and theorem work. For a bounded D-1 or DX action with no failed hard gate, write
the robust information-value case

\[
S + p_L(B-S) - C > 0,
\]

where `B`, `S`, and `C` use one predeclared value unit. Equivalently, when `B>S`, the action-specific
break-even probability is `(C-S)/(B-S)`. A universal 15% cutoff is rational only in the special case
where that ratio is 15%; the threshold otherwise changes with cost and salvage. Record genuinely
prospective gate forecasts before resolution in
[`forecast_ledger.yaml`](../research/discovery/forecast_ledger.yaml). Review the floor only after at
least twenty comparable full-T0 forecasts resolve.

### Freeze before any confirmatory outcome

An advancing topic gets a machine card, novelty manifest, decision entry, exact estimand,
baselines, multiplicity family, stop rule, budget, code/config hashes, and confirmation split. It
becomes `active` only after every protocol gate passes. D1 branches remain exploratory; D2 uses a
held-out simulator lineage, mechanism, market, vendor, or future period that did not select the
claim.

## Search-efficiency metrics

Review the process after each cycle using:

- raw programs, quick screens, collision screens, full audits, and cards;
- where each idea was killed or deferred;
- primary sources opened and killer toys constructed;
- full-audit-to-card ratio and cost to the next decisive update;
- reusable proofs, counterexamples, schemas, fixtures, and watch assets; and
- prospective forecast calibration once outcomes resolve.

Do not optimize generated-idea count, source count, prose length, or fraction of ideas surviving.
Zero survivors is a successful cycle when important branches were cheaply and correctly closed.

## Review questions

Before advancing a topic, an independent hostile review should be able to answer yes to all
of these:

- Can the claim be falsified by one predeclared result?
- Is the proposed cause defined on the full native state rather than an observational
  quotient?
- Where the intended claim requires multiple engines, do they implement the same intervention
  and observable rather than merely share a label?
- Where a real bridge is claimed, does it measure the same estimand rather than a visual analogy?
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

Every new cycle uses the four F0 source lanes, records its portfolio pruning, and retains at most
one machine card. It must not begin by reopening criticality, generic surrogates, rare-event
sampling, hydrodynamic limits, entropy production, or another family already closed in the route
graph unless a newly available capability removes the recorded blocking condition.
