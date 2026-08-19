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
wrong contracts/reserves/events and out-of-window rows; eight targeted tests plus Ruff and strict mypy pass
after the transport amendment and before the first returned log.

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
