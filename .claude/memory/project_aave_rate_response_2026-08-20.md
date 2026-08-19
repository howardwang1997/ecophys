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
