---
name: scheduled-funding-carry-2026-08-19
description: "Intervention-first dYdX fixed-carry candidate frozen before any trade, candle, price, OI, basis or realized-funding outcome row."
metadata:
  node_type: memory
  type: project
---

# Scheduled funding-carry intervention — updated 2026-08-20

The post-dispatch intervention search found one AMBER candidate. dYdX proposal 220 raised
`default_funding_ppm` from 0 to 100 ppm per eight hours (0.125 bp/hour) while the settlement clock stayed hourly;
proposals 314--318 later reset it to zero in staggered waves. A complete governance-payload audit gives ten
traceable `0 -> 100 -> 0` markets and 28 conservative clean November `100 -> 0` markets. `AVNT`, `CRO`, `PUMP`,
`WLFI` and `XPL` lack a reconstructed immediately preceding full state and are excluded. FARTCOIN is permanently
excluded because proposal 318 bundled funding with market-type/liquidity-tier changes before proposal 319
repaired them.

The eligible claim is not that activity is periodic at funding times. It is that a fixed carry change at an
unchanged clock causally changes a signed pre-boundary taker-sell/post-boundary taker-buy dipole. A threshold
model links the pulse change to the mass of trader round-trip frictions crossed by the fee step. Proposals
314--316 are development waves, proposal 317 is an untouched six-market confirmation, and the ten-market
proposal-220 forward change is locked until the reverse result is immutable. ZORA is secondary only.

The protocol is frozen in `configs/empirical_physics/dydx_funding_carry_t0_v1.yaml`; narrative protocol and
candidate map are `papers/proposal/dydx_funding_carry_t0_freeze_2026-08-19.md` and
`papers/proposal/intervention_first_candidate_map_2026-08-19.md`. No intervention-window outcomes have been
read. D0 must recover exact execution block/state, verify historical Indexer coverage and taker-side semantics,
and record terms. Public nodes tested so far prune the relevant historical blocks, so governance transitions or
an archive/explorer route must supply independent state verification. Initial work is CPU-only; no V100,
RTX2060, H20, paid data or EcoMD is authorized.

OKX cadence/formula changes are scientifically attractive but currently blocked for an archival zero-cost paper:
its 2026 API agreement limits market-data use and publication/redistribution. Ahmed and Bhuyan (SSRN 7143718,
2026) directly study fixed carry versus convergence intensity, but their abstract does not use governance
discontinuities or signed boundary-flow response; it narrows rather than closes the candidate. A clean dYdX
event study alone is specialist/NMI-feasibility work, not NCS. NCS would still require a general inversion method
with guarantees and independent multi-system validation.

## T0 result and D0 lock — 2026-08-20

T0 passed without opening a market outcome row. A counted public Cosmos REST query returned all 391 governance
proposals. For the ten paired markets, the full passed-message payload changes only `default_funding_ppm` from
0 to 100 at proposal 220; for all 28 eligible November reversals, the immediately prior and event payloads
change only that field from 100 to 0. Official source at commit
`91316e6a6c9d8bdf46370ee4661c40767caf3bff` establishes that `MsgUpdatePerpetualParams` is internal/governance-
only. The trades controller filters to `Liquidity.TAKER`, so its public `side` is taker direction.

Historical block headers and block results locate EndBlock execution exactly: proposal 220 at 38694464; 314 at
63326127; 315 at 63626789; 316 at 63626888; 317 at 63981005; and 318 at 63981519. This is a transition-ledger
proof plus execution event, not a claim that a pruned public RPC served historical state directly. The outcome
design drops the partial execution hour.

Formal result is `papers/proposal/dydx_funding_carry_t0_result_2026-08-20.md`. D0 is frozen in
`configs/empirical_physics/dydx_funding_carry_d0_v1.yaml` with a tested no-values reducer. It may query only the
21 proposal-314--316 development markets and retain schemas, counts, timestamps, heights and hashes. Proposal
317 and the March proposal-220 outcome window remain sealed. A D0 pass still requires a separately committed D1
freeze before bulk acquisition or analysis. GPU, paid data and EcoMD remain unauthorized.
