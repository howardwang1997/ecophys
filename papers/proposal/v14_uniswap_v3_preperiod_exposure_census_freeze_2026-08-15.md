# V14 Uniswap v3 full-population exposure-census freeze

**Frozen:** 2026-08-15

**Decision:** run one bounded full-U0-population preperiod census; do not top up U1a or open responses

## Why this is a new design rather than a repaired pilot

U1a failed cleanly: only 3/16 pools swapped and 1/16 had a position action in the selected preperiod. Adding pools
until the old gate passed would be post-hoc sample repair. The admissible alternative changes the estimand to the
entire exact U0 propagation prefix and applies the same event query to all 1,000 pools. The original 16 are
included, not replaced. Because U1a informed the support thresholds, the result remains development evidence and
will not be described as fresh confirmation.

## Design

The census reads only the 50,400 blocks immediately before the first pool activation and counts pool
`Swap/Mint/Burn/Collect` events. It asks whether enough pools and position actions exist in both activated fee
classes, whether NPM covers a usable fraction of actions and whether activity is too concentrated in one pool.
It does not decode economic amounts or construct participant identities.

Blockscout's deployed Ethereum JSON-RPC accepted a topic-0 OR query but rejected an address array in preflights
restricted to consumed U0 mechanism data. The frozen transport therefore uses one address per base request and
recursively bisects exact-1,000-log responses. This costs about 1,003 successful requests on the unsaturated path.

## Claim boundary

A pass means only that this non-representative 1,000-pool prefix contains enough preperiod event support to design
controls and an identity layer. It does not imply that contract activation caused later behavior, that the prefix
represents Uniswap, or that NPM is a beneficial-owner ontology. A failure means Uniswap remains useful for exact
M2 mechanism execution but not the current M3/M4 behavioral route.

All response variables, controls, transaction senders, token IDs and transfer histories remain closed. The
experiment is free, local CPU/network-only and authorizes zero GPU-hours. Full protocol:
`experiments/v14_uniswap_v3_preperiod_exposure_census/PREREGISTRATION.md`.

## Result

U1R completed cleanly but failed one conjunctive gate. It found 89 swap-active pools, 25 position-active pools,
8,722 swaps and 353 position actions; NPM covered 212/353 actions. Both fee classes met their support minima. The
largest pool, however, supplied 2,625/8,722 swaps (30.096%), above the frozen 25% event-count concentration cap.

The 1,009 responses all succeeded on one attempt, and all 16 U1a pool counts reproduced exactly. This is therefore
a scientific design failure rather than a transport failure. Do not remove the dominant pool or relax the gate.
Uniswap remains exact M2; M3/M4 moves to another system or a genuinely new prospective frame. Full result:
`experiments/v14_uniswap_v3_preperiod_exposure_census/RESULTS.md`.
