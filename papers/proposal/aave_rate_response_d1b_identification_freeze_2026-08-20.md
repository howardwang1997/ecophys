# Aave rate-step response spectroscopy — D1B identification freeze

**Status:** frozen before the formal protocol-intervention ledger, forum timeline and cross-chain execution
stagger are opened as a joint result. No post-execution behavioral outcome is authorized.

**Parent D1A artifact commit:** `6371defe9`

**Parent D1A canonical SHA-256:**
`f3ca5d19539f0da3aa13ad509ceb4b2968365423d411241a69ca9e770714d1b9`

D1A establishes abundant activity, not identification. D1B asks whether the six Ethereum rate steps sit in
protocol-side clean windows and whether the same governance announcements produce sufficiently staggered
executions across Aave V3 chains to distinguish an implemented field step from a common public announcement.

## The key correction: execution is anticipated

The official governance cache already shows that proposal creation precedes Ethereum execution by several
days. The linked ARFC discussions are generally earlier still. The paper therefore cannot call execution an
unanticipated natural experiment or invoke a standard no-anticipation event-study assumption.

For each proposal, D1B resolves the first forum-post time, governance creation, voting activation, queue time
and every payload execution. Public announcement is the earlier of the forum first post and proposal creation.
An announcement lead of at least 24 hours is classified as anticipated. This classification is descriptive and
cannot be overridden after seeing response data.

The viable identification hypothesis is instead common-announcement/different-implementation timing: a single
proposal creates a shared information event, while cross-chain payload bridges and executors implement the
same class of rate update asynchronously. This is only a candidate design. Chain-specific liquidity, gas,
asset variants and users remain confounders and require a separate pre-period activity/comparability gate.

## Complete protocol-side ledger

For every selected Ethereum execution, scan from day −35 through day +28. The ledger uses the union of the
official historical V3 Core and current V3 Origin ABIs, because the study spans legacy strategy-address events
and later data-based rate interfaces. It queries only policy/configuration contracts:

- the PoolConfigurator for every reserve, cap, collateral, status, eMode, rate-strategy and token-upgrade event;
- the AaveOracle for selected-asset source changes and fallback-oracle changes;
- the PoolAddressesProvider for pool/configurator/oracle and other registered-contract changes;
- the RewardsController for reward-configuration changes on the selected aTokens and variable-debt tokens.

The query cannot filter only on indexed asset topics: the historical
`BorrowableInIsolationChanged(address,bool)` asset is unindexed, and global eMode/upgrade events need separate
classification. All matching policy logs may exist transiently in memory, but the artifact retains only event
name, affected scope, policy values or their digest, block/timestamp and policy transaction hash. It retains no
behavioral participant or market outcome.

For a selected asset, every protocol configuration, oracle-source or token reward-configuration change is
material by default. Pool/configurator/oracle upgrades are material for all three assets. Global eMode changes
require a source-backed asset mapping; unresolved scope is treated as material, not silently ignored. The exact
selected slope-1 transaction from T0 is the sole allowed target intervention.

## Clean-window and censoring rule

An asset-event unit is eligible only if:

1. the rate-strategy event matches the exact T0 block and transaction;
2. no other material event affects it during days −14 through +14 around execution;
3. it therefore has at least 14 clean post-execution days.

The intended maximum follow-up is 28 days. A first material event after day +14 but before day +28 produces
administrative right censoring at its exact timestamp; it does not retroactively fail the unit. This is not a
convenience adjustment: a censoring-aware likelihood is part of the proposed response-spectroscopy method.
Events before day −14 remain in the support ledger for provenance but do not fail the local clean window.

The Ethereum panel passes only with at least 15/18 clean units, including 12/15 primary decreases, 2/3
reverse-sign probes and at least two clean assets in every proposal. Thresholds match the existing story-size
floor and cannot be relaxed.

## Cross-chain source and timing gate

For each proposal, D1B audits the pinned source directory, proposal-to-payload mapping and exact
`PayloadExecuted` event on every available V3 chain. A comparator counts only if source proves that its relevant
stablecoin change is slope-1-only; a same-title payload is insufficient.

A proposal qualifies for the cross-chain gate only when it has:

- at least three executed V3 payload chains in total;
- at least two non-Ethereum comparator chains;
- at least one source-audited comparable stablecoin update;
- at least 24 hours between earliest and latest qualifying executions.

At least four of the six proposals must qualify. The 24-hour threshold is chosen before execution times are
aggregated because shorter staggering is weak for an adjustment process expected to unfold over days. Passing
does not assume those chains are active or comparable; it authorizes only a separately frozen D1C pre-period
activity and comparability screen.

## Binding decision

D1B passes to D1C only if all of the following hold:

1. all six forum/governance timelines are resolved;
2. all selected Ethereum rate events match T0 exactly;
3. the frozen Ethereum clean-panel gate passes;
4. at least four proposals pass the frozen cross-chain source/stagger gate.

Failure stops the NCS causal/structural route before behavioral outcomes. A smaller specialist descriptive
analysis is not an automatic rescue and requires a separate explicit scope decision. Passing D1B still does not
authorize post-event Borrow/Repay, reserve-state, utilization, realized-rate, position, price or volume data.

## Reproducibility and compute

Official repository SHAs, ABIs, addresses, event signatures, proposal IDs, forum topics, chain labels and
decision thresholds are pinned in the YAML contract. Flashbots is the primary replaceable transport; dRPC is
reserved for independent finalized-chain reproduction. Transport splitting may change request size but never
the block union.

D1B is a CPU/network metadata audit capped at eight CPU-core hours and 500 MB of temporary memory. It uses no
paid data, GPU, V100, RTX 2060, H20 or EcoMD simulation. GPU work remains scientifically unauthorized.
