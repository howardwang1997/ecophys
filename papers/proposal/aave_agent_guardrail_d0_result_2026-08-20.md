# Aave Agent Guardrail D0 Result — 2026-08-20

## Decision

The frozen Ethereum D0 audit **stops the threshold-causal route before D1 and before all market outcomes**.
The machine-readable result is
`results/empirical_physics/aave_agent_guardrail_d0_result.json`, with canonical payload SHA-256
`764f08a7a02c550f28f8b7ace275cf4e451ba5430ea5768aff55f374c1226460`.

This is a narrow stop, not evidence that the automated-agent mechanism is absent. Eight of nine frozen support
checks pass. The only failure is terminal-classification coverage: 133 of 155 proposals are unambiguous,
`85.81%`, below the frozen `90%` threshold. The stop rule is conjunctive, so no exact validation replay, Pool
state, utilization, rates, prices, positions, liquidations, user transactions or response windows may be opened
for this route.

## Frozen result

| Check | Frozen minimum | Observed | Result |
|---|---:|---:|---|
| unambiguous proposals | 30 | 133 | pass |
| exact injections | 20 | 127 | pass |
| update types | 2 | 5 | pass |
| markets | 5 | 17 | pass |
| represented agents | 3 | 5 | pass |
| resolved non-immediate proposals | 10 | 38 | pass |
| one two-sided near-supported boundary | required | agent 0, 259,200 s | pass |
| an otherwise eligible boundary is not exactly bunched | required | 1/68 exact-zero margins | pass |
| terminal-classification rate | 90% | 133/155 = 85.81% | **fail** |

The qualifying three-day minimum-delay boundary has 68 reconstructable scores: 28 negative, 39 positive and one
exactly zero. Within 25% of the boundary there are 28 negative and 13 positive scores. This is useful action-side
support, but it is not yet a causal estimate and is not permission to inspect outcomes.

Terminal classes are 127 injected, four expired without injection, two overwritten without injection and 22
unmatched or ambiguous. There are no administratively right-censored rows. The formal scan used 540
`eth_getLogs` calls and 281 block-header calls with no retries, range splits or topic splits. It persisted no raw
RPC responses, used no paid data, no EcoMD simulation and no GPU. The external decoded-event checkpoint was
deleted after success.

## Independent verification

`tests/test_aave_agent_guardrail_result.py` does not call the D0 runner's gate or ledger helpers. It independently
recomputes the payload digest, all nine gate booleans, exact injection links, event-identity uniqueness and the
absence of market-outcome fields. It binds the result to clean implementation commit
`cce8d234e7eb8d208c4bb2731bb61f63baee5ad7` and to the frozen configuration digest
`50574c9e764fa4674a947ada2035fff273f207a6db3298e16d6143e0b3fdfd59`.

The formal result and the independent audit agree exactly. The audit also localizes all 22 unmatched rows without
changing their frozen classification:

- 21 proposals precede the unique registration of their eventual Risk Oracle/update-type agent;
- one proposal belongs to an update type never registered in this AgentHub;
- every proposal after a matching unique registration is classified, 133 of 133.

The last statistic is explicitly **post-hoc diagnostic evidence**. It exposes left truncation in the D0 risk-set
definition, but it cannot retroactively turn the failed D0 into a pass. Replacing “every observed Risk Oracle
proposal” with “every proposal after an initialized unique registration” after seeing these rows would be an
outcome-dependent protocol revision.

## Scientific interpretation

The Ethereum audit answers two different questions:

1. Is the public automated action surface large enough to remain scientifically interesting? **Yes.** It contains
   many exact executions, multiple agents, update types and markets, plus a well-populated delay boundary.
2. Did the pre-registered Ethereum D0 license a threshold-causal analysis? **No.** Its terminal-classification gate
   failed, so the current route ends here.

This result is therefore infrastructure and design evidence, not a paper claim. It weakens neither the broader
question of how machine-mediated policy changes propagate through an economic system nor the requirement for a
real-world outcome. It does show that a defensible study must define the at-risk action population from mechanism
activation, not from an arbitrary chain-history start block.

## Allowed next experiment

A new holdout protocol may be frozen before reading proposal values on any untouched deployment. It must:

1. predeclare the full deployment panel rather than select chains after activity screening;
2. define eligibility prospectively as a proposal strictly after one unique agent registration and after all
   required initial configuration is observable;
3. retain pre-registration and never-registered proposals as audited exclusions, not silently drop them;
4. deduplicate synchronized cross-chain proposals so replicated oracle actions are not treated as independent;
5. repeat the same support, bunching and classification gates before any protocol state or market outcome;
6. treat a pass as permission only for D1 exact validation replay, not as a causal result.

The natural free-data holdout panel is the complete non-Ethereum set present in the pinned Aave Risk Agents deploy
script and address book. Cross-chain observations may share one off-chain proposer and therefore do not provide
independent economic shocks by themselves; they are a prospective validation of measurement and support. A future
time holdout on Ethereum is cleaner but slower. Both routes require a new frozen document and implementation
commit before event values are opened.

## Resource decision

The next support audit remains CPU/network-only and fits the current machines without buying data or expanding
compute. The two V100s and RTX 2060 should remain free for other already justified work. GPU jobs become relevant
only after a holdout D0 and exact D1 replay pass and a market-outcome design is separately frozen. No plan assumes
H20 access.
