# Aave rate-step response spectroscopy — formal D1B result

**Decision:** STOP the NCS causal route before behavioral outcomes.

**Formal run commit:** `3a4fe2196`

**Canonical result SHA-256:**
`e7a1b74ff68c3011257698e9e3da60a2aefc7e14b0b3fabfe0831bc691be5586`

The read-back recomputation matches the stored digest. The result is not close to either frozen threshold:
only 3/18 Ethereum asset-event units are clean, versus the required 15, and only 2/6 proposals have the
required cross-chain execution stagger, versus the required four. D1C, post-execution behavior and all GPU
experiments remain unauthorized.

## Four binding checks

| Frozen check | Result | Pass? |
|---|---:|:---:|
| Six forum/governance timelines resolved | 6/6 | yes |
| Selected Ethereum rate events match exact T0 block and transaction | 18/18, exactly once each | yes |
| Clean Ethereum panel | 3/18 total; 3/15 primary; 0/3 reverse | **no** |
| Cross-chain stagger panel | 2/6 proposals | **no** |

All six executions are anticipated under the frozen 24-hour rule. Public announcement leads range from
255.82 to 784.20 hours (10.7 to 32.7 days). Execution therefore cannot be presented as an unanticipated shock,
independently of the other failures.

## Protocol-side clean windows

Only proposal 159 is clean for DAI, USDC and USDT. Its three units are administratively censored after
27.688 days by the Aave v3.2 upgrade, so they still exceed the required 14 clean post days. Every other
proposal has a material event inside day −14 through +14:

| Target proposal | Clean assets | Binding nearby protocol changes |
|---:|---:|---|
| 3 | 0/3 | `Aave Pool update` affects all assets; USDT also has borrow- and supply-cap changes |
| 94 | 0/3 | DAI, USDC and USDT collateral configuration changes; official cache links the major transactions to proposals 87 and 100 |
| 130 | 0/3 | Aave v3.1 upgrade (proposal 132): pool/configurator upgrades and selected-asset rate-data migration |
| 159 | 3/3 | no event through day +14; Aave v3.2 upgrade (proposal 178) censors at day 27.688 |
| 247 | 0/3 | selected-asset rate-data changes before T0 and Aave v3.3 upgrade (proposal 252) after T0 |
| 271 | 0/3 | repeated selected-asset rate-data changes plus global eMode-category changes, including proposal 264 |

The official governance cache independently identifies the major contaminating transactions by proposal and
title. Direct risk-steward rate/cap changes are supported by the ABI-derived on-chain policy ledger. Thus the
3/18 result is real policy overlap, not a missing-target or wrong-topic artifact.

## Cross-chain stagger

Every proposal has enough executed V3 payload chains and enough non-Ethereum source-audited slope1-only
stablecoin comparators. The binding failure is timing:

| Proposal | Comparable execution stagger (hours) | Qualifies at ≥24 h? |
|---:|---:|:---:|
| 3 | 48.924 | yes |
| 94 | 13.088 | no |
| 130 | 14.383 | no |
| 159 | 8.731 | no |
| 247 | 13.779 | no |
| 271 | 43.060 | yes |

The common-announcement/different-implementation idea therefore has only two usable proposal clusters. Lowering
the threshold after seeing these times would be post-hoc and would still leave chain comparability, spillovers
and policy endogeneity unresolved.

## Reproducibility and blinding

The formal run retained 669 sanitized policy events over four merged support intervals. It made 519 block-header
and 546 log calls through the public dRPC endpoint, with 157 HTTP-429 retries, 484 seconds of explicit backoff
and no range split. The repository-external checkpoint completed all four intervals and was deleted on success.

Only policy event name/signature, selected-asset/global scope, block/time, policy transaction hash and a digest
of event data are retained. No raw log, behavioral participant, Borrow/Repay response, reserve-state outcome,
utilization, realized rate, position/balance, price or volume was queried or persisted. The run used CPU and
free official/public sources only; it used no V100, RTX 2060, H20, paid data or EcoMD.

## Research consequence

D1A proved that the selected markets are active; D1B proves that activity is not the limiting factor. The
limiting facts are anticipated treatment, frequent overlapping protocol control and insufficient cross-chain
implementation delay. A single clean proposal with three assets is not an independent 18-unit panel and cannot
support the proposed response-spectroscopy inversion or an NCS causal claim.

Do not rescue this line by relaxing 24 hours, narrowing ±14 days after inspection, treating asset rows from one
proposal as independent experiments, or silently reclassifying upgrades/rate migrations as harmless. A
specialist descriptive study would require a new, explicit scope decision; it is not the default next step.

