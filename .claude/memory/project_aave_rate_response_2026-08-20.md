---
name: aave-rate-response-2026-08-20
description: "Outcome-blind Aave borrowing-rate intervention candidate: rate-step response spectroscopy rather than aggregate elasticity."
metadata:
  node_type: memory
  type: project
---

# Aave rate-step response spectroscopy — frozen 2026-08-20

After the dYdX activity failure, the next zero-cost candidate moves to repeated Aave V3 borrowing-rate
interventions. The eligible story is not aggregate demand elasticity or rate optimization: Aave's Chaos Labs
Interest Rate Curve Risk Oracle already fits aggregate demand curves from 10--15 minute observations and uses
them for constrained welfare optimization.

The candidate mechanism is response spectroscopy. A discrete rate-curve execution applies an exactly timed
carry step. In a non-interacting threshold limit, adjustment occurs when integrated incremental carry crosses a
latent barrier, so survival in integrated-carry coordinates identifies a friction/barrier distribution. Multiple
step sizes test a scaling collapse; censoring, endogenous utilization feedback and cross-chain stagger require a
new inversion method if this is ever to support NCS. A specialist event study alone is not NCS.

T0 is frozen in `configs/empirical_physics/aave_rate_response_t0_v1.yaml` before any Aave `Borrow`, `Repay`,
`ReserveDataUpdated`, position-balance or post-event value. The singleton panel has proposals 3, 94, 130, 159,
247 and 271 on Ethereum Core, crossed with DAI/USDC/USDT: 15 primary rate-decrease units plus three reverse-sign
units. Official proposal diffs indicate only `variableRateSlope1` is configured for those assets; derived maximum
rates, the legacy identity `baseStableBorrowRate = variableRateSlope1 + baseStableRateOffset`, and strategy-
address replacement are not extra policy fields. Proposals 69 and 216 are rate-curve-only but non-singleton and
stay secondary.

Official data infrastructure is unusually strong: `aave-governance-cache` maps proposal IDs to target-chain
payloads and exact execution blocks/transactions, while `aave-proposals-v3` supplies executable source and
before/after diffs. However, the separate 50-million-record Aave preprint's claimed Zenodo DOI
`10.5281/zenodo.17898640` currently returns an unregistered-identifier 404 and an exact-title Zenodo search finds
zero records. Do not describe that bulk dataset as acquired. Direct public chain logs are the free fallback.

Formal T0 passed from clean commit `479534f16`; canonical result SHA `9db20918…` is verified after JSON read-back.
All six proposals map to a unique exact Ethereum payload execution, all 18 asset-event diffs pass the singleton
configured-change audit, and the public RPC metadata probe passes without opening a market log. The Zenodo DOI
remains unavailable.

Commit a separate 28-day pre-period activity gate before querying any response. Later hard risks
are anticipation, endogenous policy, incomplete risk-steward intervention history, repeated-unit dependence,
the at-risk population for new borrowing, and utilization feedback. No GPU, paid data or EcoMD run is
authorized by T0.

## D1A activity gate frozen before logs

D1A uses four consecutive seven-day bins immediately before each exact payload execution and excludes the
execution block. For each asset-event unit it retains only weekly Borrow/Repay counts and distinct debt-user
counts, plus their 28-day totals. User topics exist only in memory; no participant, amount, rate, transaction
hash, per-log identifier, raw log or response is serialized. The pure reducer rejects duplicates, removed logs,
wrong contracts/reserves/events and out-of-window rows; targeted tests, Ruff and strict mypy guard the runner.

An eligible unit needs every week to have at least 10 Borrows, 10 Repays and 10 distinct debt users, and the
full period to have at least 200 combined actions and 50 distinct debt users. The panel passes only with at
least 15/18 total, 12/15 primary decreases, 2/3 reverse-sign probes and two assets in every proposal. Any miss
stops post-event acquisition; thresholds cannot be weakened after inspection. Passing authorizes only a
separately frozen complete intervention-ledger and anticipation/identification audit. D1A is CPU/RPC-only and
does not authorize V100, RTX 2060, paid data or EcoMD.

The first formal D1A attempt from `4ed11b638` returned no logs and wrote no artifact: PublicNode requires a
personal token for historical `eth_getLogs`. An outcome-blind empty-address probe verified that dRPC's documented
public Ethereum endpoint supports the frozen 5,000-block historical query. The transport is amended to dRPC
before retry; thresholds and scientific queries are unchanged. HTTP 403 is fatal rather than recursively split;
only recognized range/result-size errors may split chunks.

The retry from `e617f85aa` reached the authorized pre-period request sequence but stopped on dRPC HTTP 429; no
aggregate was printed or persisted. Before another retry, freeze 0.5-second request pacing and six bounded 429
backoffs, and retain retry/wait diagnostics. This is transport scheduling only: no scientific query or threshold
changes. Partial pre-period responses may have existed transiently, so do not claim that no Aave log has ever
been returned; the correct claim is that no D1A aggregate result or post-event value exists yet.

The paced run from `1115109ab` later stopped on dRPC HTTP 408 and again wrote no final artifact. Treat
408/413/exhausted-504 as deterministic transport-chunk bisection conditions without changing the block union.
Future retries use an outside-repository, digest-bound checkpoint after each complete proposal containing only
allowed boundary metadata and aggregate counts; it must be a frozen-order prefix and is deleted after success.
This prevents infrastructure failures from repeatedly consuming the public endpoint while preserving the
no-raw-log contract.

## Formal D1A result

D1A passed from clean commit `c0ebdf50d`; canonical result SHA is `f3ca5d19…` and matches an independent JSON
read-back recomputation. All 18/18 units qualify: 15/15 primary decreases, 3/3 reverse-sign probes and all three
assets in every proposal. The weakest weekly cells have 42 Borrows, 46 Repays and 49 distinct debt users; the
weakest 28-day cells have 564 combined actions and 210 distinct users, so the pass is well away from the
10/10/10 and 200/50 thresholds.

The completed run used 481 historical block calls and 306 log calls, with one deterministic range split, 107
HTTP-429 retries and 720 seconds of backoff. The sanitized checkpoint was removed after success. No raw response,
participant, amount, rate, per-log transaction/block identifier, execution/post-event log, reserve update,
position value, paid data, GPU or EcoMD was retained or queried beyond the authorized pre-period events.

The next authorized step is only a separately committed D1B: complete reserve-intervention ledger,
announcement-to-execution timing, cross-chain stagger/control audit and frozen falsification rules. Do not open
post-event outcomes yet. Main risks remain anticipation, endogenous policy, other reserve changes, repeated
asset dependence, at-risk-population definition and utilization feedback. Independently reproduce extraction
against Flashbots or a controlled archive node before the main study.

## D1B identification gate frozen

Execution cannot be framed as an unanticipated shock: governance proposal creation already leads Ethereum
execution by several days, and the linked forum discussion is earlier. D1B therefore treats any public lead of
at least 24 hours as anticipated and forbids the surprise-event-study claim.

D1B audits a union of historical/current PoolConfigurator events plus oracle-source, addresses-provider and
reward-configuration events from day −35 to +28. A unit requires exact T0 rate-event matching and no other
material protocol event from day −14 through +14. A later material event administratively right-censors the
target 28-day follow-up. The clean Ethereum panel still requires 15/18 total, 12/15 primary, 2/3 reverse and two
assets per proposal.

The candidate identification rescue is common announcement with asynchronous cross-chain implementation. At
least four of six proposals must each have three executed V3 chains, two non-Ethereum comparators, a
source-audited slope1-only stablecoin update and at least 24 hours of execution stagger. Passing authorizes only
a separately frozen cross-chain pre-period activity/comparability gate D1C; failure stops the NCS route before
behavioral outcomes. Pinned ABI/source SHAs and full rules live in
`configs/empirical_physics/aave_rate_response_d1b_identification_v1.yaml`.

Before formal D1B, the executable interpretation is fixed: DAI/DAIe, USDC/USDCe/USDCn and USDT/USDTe are
the only cross-chain aliases, and a chain counts as comparable only when its historical, commit-pinned Solidity
source changes exactly `variableRateSlope1` for at least one such asset. Stagger is measured across executed,
source-audited comparable chains including Ethereum. Missing per-chain source is non-comparable, not inferred.
The pure audit layer extracts event signatures from the pinned ABIs, parses both legacy `_bpsToRay(...)` and
current direct-bps config forms, sanitizes policy logs, and applies exact-target/contamination/censoring rules.
The implementation has targeted regression tests; no behavioral outcome has been opened.

Flashbots proved unsuitable as the formal D1B transport: it blocks `web3_sha3` and then exhausted six 429
backoffs during boundary-only block reads, both before `eth_getLogs`. Topics now use locally vector-checked
OpenSSL Keccak-256, and the formal ledger uses the already D1A-validated dRPC endpoint at 0.5-second pacing.
An outside-repository identity-bound checkpoint keeps only boundaries and sanitized policy-event metadata and
is deleted on success; this is transport/recoverability only, not a scientific amendment.

## Formal D1B hard stop

D1B ran from clean commit `3a4fe2196`; canonical result SHA is `e7a1b74f…` and independently recomputes. All
six timelines and all 18 exact T0 targets resolve, but all executions are anticipated by 10.7--32.7 days. Only
proposal 159's DAI/USDC/USDT units are clean (3/18 versus the frozen 15); they are censored at 27.688 days by
the v3.2 upgrade. Other proposals overlap genuine pool upgrades, collateral/cap/eMode changes or repeated rate
updates. Official governance metadata corroborates the major contaminating transactions.

Only proposals 3 and 271 exceed the 24-hour source-audited comparable cross-chain stagger (2/6 versus the
required four); the other four span only 8.73--14.38 hours. Formal decision is
`stop_ncs_causal_route_before_behavioral_outcomes`. Do not run D1C, open response data, lower the stagger/window
rules, treat three assets from one proposal as independent evidence, or launch GPU/EcoMD. D1A's activity pass
survives only as infrastructure. Any specialist descriptive rescue requires a new explicit scope decision.
