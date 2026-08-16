# Aave liquidation-threshold shocks as a candidate exact intervention layer

**Status:** A0 source/effect identity passed; the A1a zero-account deployment/version/event-directory protocol is
frozen but not yet executed; Aave is not admitted to G1.

## Why this is cleaner than the retired Compound cap route

Compound's surviving cap increases did not mechanically change existing accounts, while would-be blocked
suppliers had no enumerable pre-event denominator. An Aave base-reserve liquidation-threshold (LT) decrease can
change an already open borrower's health factor immediately, with account-specific dose computable from the last
pre-event state. The candidate story is therefore:

> Can an economic world model combine an exact institutional intervention operator with a learned multiscale
> response model and predict how heterogeneous agents restore solvency after an unforeseen rule shock?

This remains a candidate. No qualifying event, complete cohort or causal response has been demonstrated.

## Exact mechanism and learned behavior

The event layer is deterministic and version-matched to deployed code. For changed reserve `j`,

\[
\Delta W_u = C_{uj}^{-}(L_j^{-}-L_j^{+}), \qquad
H_u^{+}=H(W_u^{-}-\Delta W_u,D_u^{-}),
\]

using source integer rounding. The dose is zero if the account does not use the reserve as collateral or eMode
overrides its base LT. The event layer should not be learned: approximating a known transition weakens
counterfactual validity.

Learning begins after the shock. A marked competing-risk model predicts repayment, collateral addition/removal,
borrowing, eMode change, liquidation and exit, conditional on exact dose, distance to HF=1, portfolio composition,
market state, gas and governance exposure. Longer-horizon heads predict survival, portfolio reallocation and
market-level liquidity. The hybrid architecture is:

1. exact event transition;
2. account-level marked point process or survival model;
3. market aggregation constrained by reconstructed accounting identities; and
4. slow regime/context state for transfer across assets, deployments and protocols.

## Admission ladder and kill gates

### A0 — source/effect identity

Pin Aave V3.7 source; verify config-engine routing, exact HF accumulation, eMode routing, state views, HF boundary
and licence. The sealed audit passed 12/12 gates over fourteen files and 63 markers at protocol commit
`fdb1dc41497a4eca9e740dbd196061208e61c584`; independent raw-source replay passed. No chain row was used. This
authorizes A1 design only.

### A1 — deployment and event inventory

Freeze Ethereum market addresses, proxy/implementation histories, configurator/config-engine signatures,
governance clocks and block range before reading events. Inventory every LT update, version-match deployed code,
and decode pre/post configuration and proposal payloads.

Exclude any event where:

- LT is not a strict decrease or becomes zero;
- actual LTV or liquidation bonus changes;
- a ConfigEngine route explicitly changes LTV or `liqBonus` instead of using its pinned `KEEP_CURRENT` flag;
- the reserve is frozen;
- eMode, oracle, index rule, pause/grace state or another account-relevant parameter changes in the same execution;
- payload/transaction path or operative state clock is ambiguous; or
- development reconnaissance leaves no untouched confirmation pool.

If no eligible event survives, retire the Aave LT route before accounts are opened.

ConfigEngine encodes `liqBonus` as the increment above 100% and adds `100_00` when calling PoolConfigurator. A1
must normalize that payload representation to actual reserve configuration before applying the unchanged-bonus
filter.

The first empirical subgate is now A1a, a deliberately narrower directory. It freezes Ethereum blocks
0--25,760,572, official address-book/source commits, three complete log streams and the ERC-1967 implementation
slot before opening any chain event. PoolAddressesProvider and PoolConfigurator are scanned without a topic
filter; the Pool proxy is scanned only for `Upgraded`. Provider transitions must form a continuous implementation
chain and match proxy upgrades one-for-one. Fixed-end getters, slots and code come from Blockscout; PublicNode
replicates only chain ID and headers because its free historical-state limitation is already known.

A1a compares each configuration row only with the previous **emitted** configuration. A provisional directory
row needs a strict positive LT decrease, unchanged emitted LTV/bonus, exactly one Configurator log in its
transaction and no provider/proxy upgrade. At least three rows, two assets and three transactions are required.
This is not authoritative T−1 state or payload isolation. A pass authorizes an all-candidate A1b protocol; only
A1b may open historical configuration, receipts, calldata/call paths and version-matched implementation source.
Full preregistration: `experiments/v14_aave_v3_lt_event_directory/PREREGISTRATION.md`.

### A2 — enumerable denominator and pre-event reconstruction

The account unit is an on-chain borrower address, not a person. Enumerate every address with potentially nonzero
collateral or debt from protocol events, then reconcile account aggregates to authoritative reserve totals at
fixed blocks. Reconstruct reserve configuration, indexes, oracle prices, user configuration and eMode. Every dose
must replay deployed `getUserAccountData` arithmetic exactly.

Hard failures include aggregate residuals, missing historical state, proxy-version ambiguity, account-identity
conflation or outcome-informed cohort construction. Zero-dose eMode and non-collateral routes must be reported,
not mixed silently with direct exposure.

### A3 — outcome-blind controls and response panel

Choose controls from pre-event support: unaffected reserve exposures in the same market, same-reserve borrowers
outside the direct route, and preferably other Aave deployments without simultaneous shocks. Screen overlap,
concentration, anticipation, shared payload spillovers and oracle discontinuities before outcomes. Pre-register
competing risks, horizons and censoring.

Open actions, liquidations and market responses only after cohort and controls pass. Primary causal objects should
be dose-response and boundary-crossing contrasts, not one treated-versus-control mean. Governance endogeneity is
central because LT often changes while risk is already evolving.

### G1 — data admission

G1 requires an eligible development event and untouched confirmation event or defensible cross-deployment
replication; complete account reconciliation; exact dose replay; support/overlap; unbundled execution; and a
frozen response protocol. Only G1 authorizes account modeling and GPU work.

## Data requirements

| Stage | Required data | Cost assumption | Participant outcomes? |
|---|---|---|---|
| A0 | 14 pinned official Solidity/licence files | Free GitHub source | No |
| A1 | deployment/proxy history, configuration/governance logs, transactions, receipts, payload source, headers | Free public sources first | No |
| A2 | historical user/reserve/config/index/oracle state, state-owner events and aggregate totals | Free archive sources for feasibility; scalable archive access may later be needed | No |
| A3 | pre-event covariates across assets/deployments, proposal overlap, gas and market state | Free first; vendor data only behind a new gate | No, until controls freeze |
| Post-G1 | successful calls/actions, liquidations, price/liquidity response and confirmation events | Public chain plus optional purchased/partner data under provenance | Yes |

Each dataset needs source, retrieval date, licence/terms, immutable block range, content hash and preprocessing
hash. Time and event splits must be frozen; development-only proposal 204 cannot become confirmation.

## Compute requirements

- A0: Mac CPU, under one minute after checkout; zero GPU.
- A1: local CPU/network, minutes to hours depending on range partitioning; zero GPU.
- A2: parallel CPU/archive-I/O jobs by deployment, block shard and address batch. Feasibility can use the Mac,
  either V100 host as a CPU worker, or the RTX 2060 host; GPU is unnecessary.
- A3: CPU-heavy reconstruction and inference; memory, disk and network are likely bottlenecks first.
- Post-G1 baselines: the two current 32-GB V100 workers suffice for small account-event models and seed
  feasibility. Expanded non-H20 CPU/GPU workers become useful for multi-event, multi-market sweeps.
- Full NCS model: independent event/seed/market jobs scale across heterogeneous non-H20 pools, with GPU types kept
  in separate benchmarked pools. No plan assumes H20.

No job is queued on the V100s or RTX 2060: A0 is source-only and G1 has not passed.

## What could make this NCS-level

A single Aave event study is insufficient. The stronger contribution is a general method for **mechanism-exact,
adaptation-learned economic world models**: code-derived interventions, invariant account reconstruction,
long-horizon calibration under accounting constraints and frozen out-of-event prediction. It must validate beyond
EcoMD and preferably beyond Aave—for example another lending protocol, exchange rule or market mechanism with an
exact local operator. EcoMD then becomes one backend in a broader method paper, not the sole evidence.

Retire or reframe the route if eligible events are absent, full state cannot be reconciled, governance endogeneity
destroys support, or prediction fails against strong survival/point-process baselines on untouched events. These
are scientific outcomes, not reasons to relax gates.
