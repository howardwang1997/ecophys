# Aave Agent Guardrail Multichain Holdout D0 v2 Result — 2026-08-20

## Decision

**Hard stop.** The prospectively frozen nine-chain holdout does not support the proposed threshold-causal
design. Do not proceed to D1 exact-state replay, do not retrieve market outcomes, and do not launch EcoMD or a
GPU experiment for this route.

The merged result was produced from clean commit
`c9ab42a64295ec6bd3ea6868050cb9ca4dd05d15` and version-2 configuration SHA-256
`93be07281ff57e853d32f5caadc2f08d9a38e9e91728c35c8126a22aab25246c`. Its machine decision is
`stop_multichain_threshold_route_before_d1_and_market_outcomes`.

## Immutable artifacts

| Artifact | Canonical payload SHA-256 | Physical file SHA-256 |
|---|---|---|
| `results/empirical_physics/aave_agent_guardrail_holdout_d0_v2_result.json` | `89309106c370404049ad27247ee8e0efe3d01a787cb4e0f1feae689e2de960e8` | `f4a2a614dbf1e3455e104288a8134141ca538c41c9d7636757383b4b95acd199` |
| `results/empirical_physics/aave_agent_guardrail_holdout_d0_v2_arbitrum_official_replication.json` | `d5eed01f2b6666a18e8c588c80fe5ea52ea82b5898df71cdcc11c7db5f22922b` | `30e8ee713e4079f8747226000cb81d6944a80e79080ecc43ce706b7750f7a929` |

`tests/test_aave_agent_guardrail_holdout_result.py` recomputes both canonical digests, the complete global gate,
the row- and batch-level boundary geometry, the post-hoc sensitivity audit and the official-Arbitrum action
surface equality without importing the runner or its gate helpers.

## Acquisition and blinding audit

Every chain artifact has the exact clean code SHA and configuration digest. The Ethereum pilot contributes zero
holdout observations. Extraction retained decoded AgentHub configuration/injection events, Risk Oracle proposals
and canonical headers only. It did not query pool state, prices, utilization, rates, balances, positions,
liquidations, user transactions or response windows. Raw RPC responses were not retained. The run used public
data and CPU/network only: zero paid data, zero EcoMD execution and zero GPU hours.

| Chain | Formal transport | Raw proposals | Eligible | Excluded | Exact injections |
|---|---|---:|---:|---:|---:|
| Arbitrum | Tenderly | 34 | 29 | 5 | 27 |
| Avalanche | Tenderly | 49 | 22 | 27 | 20 |
| Base | Tenderly | 43 | 29 | 14 | 28 |
| BNB | Sentio | 12 | 4 | 8 | 4 |
| Gnosis | Tenderly | 1 | 1 | 0 | 1 |
| Linea | Tenderly | 54 | 14 | 40 | 14 |
| Optimism | Tenderly | 44 | 32 | 12 | 32 |
| Plasma | Sentio | 116 | 69 | 47 | 61 |
| Polygon | Tenderly | 25 | 15 | 10 | 15 |
| **Total** | — | **378** | **215** | **163** | **202** |

The 163 exclusions are fully accounted for by 88 pre-registration and 75 never-registered proposals. Among the
215 eligible proposals, 202 are injected and 13 expire without injection. Terminal classification excluding
right censoring is 100%.

## Frozen support gate

The panel has ample global action data. It fails only the local overlap needed to interpret the deterministic
minimum-delay boundary as a quasi-experimental threshold.

| Frozen check | Required | Observed | Pass |
|---|---:|---:|:---:|
| Eligible proposals | 30 | 215 | yes |
| Exact injections | 20 | 202 | yes |
| Update types | 2 | 4 | yes |
| Chain–market pairs | 5 | 49 | yes |
| Represented chain–agents | 3 | 18 | yes |
| Represented chains | 3 | 9 | yes |
| Proposal batches | 10 | 151 | yes |
| Resolved non-immediate proposals | 10 | 42 | yes |
| Resolved non-immediate batches | 5 | 28 | yes |
| Terminal classification rate | 0.90 | 1.00 | yes |
| Qualifying delay boundaries | 2 | 0 | **no** |
| Chains with a qualifying boundary | 2 | 0 | **no** |

Thirteen distinct chain/agent/delay epochs have at least one reconstructable score. None passes the jointly frozen
row and independent-batch conditions. The two closest cases fail for different reasons:

| Boundary | Row scores (−/+) | Near rows (−/+) | Batch medians (−/+) | Near batches (−/+) | Decisive failure |
|---|---:|---:|---:|---:|---|
| Plasma, agent 0, 259,200 s | 60 (18/42) | 18/0 | 25 (9/16) | 9/0 | no positive observation inside the frozen 64,800 s radius |
| Optimism, agent 0, 259,200 s | 16 (4/12) | 4/6 | 16 (4/12) | 4/6 | misses the frozen row minima of 20 total and 5 negative/near-negative |

For Plasma, the closest negative margin is −7 seconds but the closest positive margin is 85,767 seconds. The
frozen positive neighborhood ends at 64,800 seconds. The subsequent positive margins follow an approximately
daily lattice, consistent with scheduled/discrete action generation rather than continuous local variation
around the three-day delay. This is a support hole, not a low-total-sample problem. For Optimism, the closest
negative and positive margins are −2 and +32 seconds, respectively, but the row count and negative side remain
below their prospectively fixed minima.

## Post-hoc sensitivity audit

This audit is diagnostic only and cannot change the frozen decision:

| Non-authorized change | Qualifying chain/agent boundaries |
|---|---|
| None | none |
| Increase neighborhood from 25% to one third only | Plasma agent 0 only |
| Reduce row minima from 20/5/5 to 16/4/4 only | Optimism agent 0 only |
| Make both changes | Plasma agent 0 and Optimism agent 0 |

Thus no single defensible perturbation recovers the required two-chain result. Passing would require two
coordinated, outcome-informed changes after seeing the support geometry. Reclassifying that construction as the
original confirmatory design would be threshold hacking. It is not permitted.

## Full-union transport audit

The initial independent Arbitrum diagnostic exposed one scientifically material provider omission. Blockscout
matched the frozen 10,000-block qualification shard but omitted the `UpdateInjected` log at block 436,939,422,
transaction `0xbf1e4f224eca8081e0d4699008f48de384e41521799ab9e58ce014682a81da1a`, log index 1. Tenderly and the
official Arbitrum RPC return the same identity, payload and block hash; Blockscout returns no log for that exact
block.

A complete formal-window replication through `https://arb1.arbitrum.io/rpc` is byte-for-byte equal to the
Tenderly primary action surface. Their shared canonical action-surface SHA-256 is
`11ee6f153425f1ddb34c692af9e2bf242ca2533f279af59856282248159237c2`. This confirms the primary Arbitrum
ledger, isolates the omission to Blockscout, and shows why local qualification-shard agreement cannot certify a
complete historical union. Gnosis and Linea also had exact no-new-RPC full-surface agreement between independent
providers in the earlier transport diagnostic.

Because the scientific gate already fails, additional full-window provider replications on the remaining chains
cannot authorize D1 and should not consume more public-service capacity. The completed Arbitrum replication is
retained as a transport-method validation, not as a rescue of the causal design.

## Scientific interpretation and disposition

The deployed automated-agent system produces a rich, auditable multichain action ledger, but its deterministic
minimum-delay rule does not create the prospectively required continuous two-sided local variation on two
chains. The data are compatible with scheduled and discretized proposer behavior that skips across the nominal
threshold. Therefore the observed injected-versus-expired actions cannot be treated as locally quasi-random, and
no causal market-response claim is identified by this design.

Close the threshold-causal route. Preserve the source audit, event decoder, exact proposal/injection matcher,
activation-conditioned risk set, cross-chain batch construction and transport-completeness checks as reusable
measurement infrastructure. A future descriptive study of automated risk governance would require a new
question and freeze; it must not inherit a causal label from this failed design. For an NCS-scale main article,
return to problem selection and require the next candidate to prove its real-data identification or prediction
surface before any simulator-scale computation.
