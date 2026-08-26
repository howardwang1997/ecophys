# EcoMD Re-entry Capability Trigger Audit

**Date:** 2026-08-26

**Scope:** outcome-blind source, model, and licence audit after Discovery Cycle 16

**Decision:** **zero qualified re-entry triggers; do not open Cycle 17**

## Question

The discovery protocol forbids a third search cycle in a saturated parent or failure family unless
one exogenous development first removes a recorded blocker. This audit asks whether newly surfaced
market simulators or model papers do that. It is not a topic-search cycle: no candidate harvesting,
full novelty manifest, forecast, outcome access, simulator run, implementation, data action,
purchase, outreach, EcoMD change, or compute was authorized.

The binding closed formulations are:

- `cross_simulator_disagreement_intervention_certificate` and
  `adaptive_scheduler_information_filtration_response` from Cycle 8;
- `interventional_lob_fidelity_benchmark`; and
- `prospective_counterfactual_market_simulator_validity` from Cycle 16.

Their relevant blockers are complete branchable state, a common legal action and clock, independent
system lineage, an observed real interventional target, and a contribution beyond generic causal
abstraction, simulator discrepancy, and interventional-surrogate theory.

## Trigger decisions

| Development | What is genuinely new | Decisive audit | Decision |
|---|---|---|---|
| QuantReplay v12 | Apache-2.0 company-maintained FIX venue, seeded order generation, continuous/auction matching, L2, replay, and recovery | Its persisted object is venue plus instrument data; instrument state is last trade, summary information, and the resting limit-order book. It does not persist generator RNG, the future execution schedule, external client/strategy state, or current phase. Source explicitly skips resting market orders during auctions and Trade-at-Last orders. | **Partial capability, not a trigger** |
| `orderbook` v0.26.0 | Strong matching-engine snapshot/WAL contract covering the book, pending/conditional orders, sequence counters, duplicate guard, and recovery | The snapshot is deliberately an **engine** snapshot. The research harness passes an external `rand.Rand` into agents, while the engine holds phase permissions but no calendar. Population, RNG, scheduler, latency, and adaptive-policy state are outside the checkpoint. | **Partial capability, not a trigger** |
| `lobsim` pinned commit | Deterministic L3 replay, a canonical event language, strategy injection, fills, and diagnostics | It is a historical/paper-execution state machine, not a checkpoint-complete adaptive market population and not an external intervention truth asset. | **Not a trigger** |
| DiffLOB | A current diffusion model that conditions generated LOB paths on future trend, volatility, liquidity, and OFI regimes | A future regime is a functional of the future path, not a legal exchange or trader action. Matching `P(path | regime)` and moving the label internally do not identify `P(path | do(action))`. Generic causal diffusion and interventionally consistent surrogate work already supplies the parent distinction. | **Not a trigger** |
| Noble--Rosenbaum--Souilmi QR simulator | A current interactive queue-reactive model with latency races and a power-law impact-memory mechanism | It strengthens the occupied interactive-simulator neighborhood but supplies neither a randomized field action nor complete external counterfactual truth. It therefore adds a model, not an adjudicating capability. | **Not a trigger** |

## Exact checkpoint boundary

QuantReplay's README advertises reproducible seeded order generation and on-demand state recovery.
The source narrows that claim:

1. [`market_state::Snapshot`](https://github.com/Quod-Financial/quantreplay/blob/a58c7c6d5436601d447129a7a81e662ba102cd9c/project/trading_system/ih/state_persistence/snapshot.hpp)
   contains only `venue_id` and instrument records.
2. [`InstrumentState`](https://github.com/Quod-Financial/quantreplay/blob/a58c7c6d5436601d447129a7a81e662ba102cd9c/project/trading_system/components/common/include/common/instrument_state.hpp)
   contains last trade, instrument information, and buy/sell resting limit orders.
3. [`order_book_state_converter.cpp`](https://github.com/Quod-Financial/quantreplay/blob/a58c7c6d5436601d447129a7a81e662ba102cd9c/project/trading_system/components/matching_engine/src/orders/tools/order_book_state_converter.cpp)
   explicitly omits resting auction market orders and Trade-at-Last orders because recovery of those
   in-progress phases is unsupported.
4. The [random order generator](https://github.com/Quod-Financial/quantreplay/blob/a58c7c6d5436601d447129a7a81e662ba102cd9c/project/generator/ih/random/instrument_generator.hpp)
   can be reseeded but is not part of the persistence snapshot.

Thus two branches restored from one file can begin with the same resting book yet receive different
subsequent generated messages or phase transitions. That is insufficient for a common-random-number
market counterfactual.

The `orderbook` engine is stronger inside its narrower boundary. Its
[`EngineSnapshot`](https://github.com/intrepidkarthi/orderbook/blob/51d480cdb68b9989febb0b075d291cf891f425b3/pkg/matching/snapshot.go)
captures detailed matching state and supports exact command-log recovery. But its
[`NoiseTrader`](https://github.com/intrepidkarthi/orderbook/blob/51d480cdb68b9989febb0b075d291cf891f425b3/pkg/sim/agents.go)
receives RNG from the simulator harness, and the documented matching engine deliberately owns no
calendar. It therefore cannot substitute for a full simulator checkpoint containing agents, all
RNG namespaces, event queue, timers, information filtration, inventories, and external strategy
state.

## Why the apparent DiffLOB fork does not reopen interventional fidelity

Let `R=R(X_{1:T})` denote a future trend, volatility, liquidity, or OFI regime and let `A` be a
legal order or market-rule action. DiffLOB targets an observational conditional law

`P(X_{1:T} | R=r)`.

An interventional simulator must instead target

`P(X_{1:T} | do(A=a), S_0=s)`.

Two causal systems can share the first law for every regime while an unobserved information state
causes both the regime and order flow; changing the sign of the structural response to `A` then
reverses the second law without changing the first. In Markov language, conditioning on a future
path event yields a Doob-transformed process, but that transform generally changes many
state-dependent transitions and need not lie in the exchange's admissible action grammar. The
distinction is therefore real and useful for claim hygiene, but it is not a new Nature-scale method:
the generic interventionally consistent surrogate and causal-generative parents are already in the
route graph, and no new field target or market-specific theorem was supplied.

## Re-entry conditions

A later source may supersede this audit, but it must create a new append-only trigger entry and
satisfy at least one exact condition:

1. **Full simulator state:** two independent lineages persist and restore matching state, all agent
   and inventory state, isolated RNG namespaces, event queue, timers/phase calendar, information
   filtration, external strategy state, and versioned rounding/action semantics.
2. **Field truth:** a licensed prospective or randomized market action exposes assignment,
   pre-state, treatment, outcome, timing, interference unit, and a deterministic action mapping
   shared by the simulators.
3. **Theory:** a theorem or counterexample invalidates the existing conformance, causal-abstraction,
   Doob-conditioning, or off-support-transport reduction for a precisely declared market class.

Another matching engine, a larger replay tape, an outcome-conditioned generator, or another
interactive simulator does not qualify by itself. All five developments remain useful watch assets,
but none authorizes candidate harvesting or execution.

## Primary and official sources

1. QuantReplay v12, Apache-2.0, pinned commit:
   https://github.com/Quod-Financial/quantreplay/tree/a58c7c6d5436601d447129a7a81e662ba102cd9c
2. `orderbook` v0.26.0, MIT, pinned commit:
   https://github.com/intrepidkarthi/orderbook/tree/51d480cdb68b9989febb0b075d291cf891f425b3
3. `lobsim`, Apache-2.0, pinned commit:
   https://github.com/kpetridis24/lobsim/tree/0cb48ed89a9cd5568e974d988214cfbebf51ca51
4. Wang and Ventre, *DiffLOB: Diffusion Models for Counterfactual Generation in Limit Order
   Books*: https://arxiv.org/abs/2602.03776
5. Noble, Rosenbaum and Souilmi, *Bridging the Reality Gap in Limit Order Book Simulation*:
   https://arxiv.org/abs/2603.24137
6. Dyer et al., *Interventionally Consistent Surrogates for Agent-based Simulators*:
   https://proceedings.neurips.cc/paper_files/paper/2024/hash/26b8e3dc3a21fcd660d80c63b767f324-Abstract-Conference.html
7. Coletta et al., *Conditional Generators for Limit Order Book Environments: Explainability,
   Challenges, and Robustness*: https://doi.org/10.1145/3604237.3626854
