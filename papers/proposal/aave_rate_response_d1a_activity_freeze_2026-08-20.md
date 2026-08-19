# Aave rate-step response spectroscopy — D1A activity freeze

**Status:** frozen before the first Aave `Borrow` or `Repay` log request.

**Parent T0 artifact commit:** `e29230ce9`

**Parent T0 canonical SHA-256:**
`9db209180d036091c48eb2dc05b4c3eef1e23f50ae97a937ab227e920823ed8b`

This screen asks only whether the frozen singleton panel has enough pre-intervention activity to justify the
next identification audit. Activity is power metadata. It is not a response estimate, a causal result, evidence
for response spectroscopy, or permission to inspect post-execution outcomes.

## Frozen panel and source

The panel is the 18 Ethereum Core asset-event units qualified at T0: proposals 3, 94, 130, 159, 247 and 271,
each crossed with DAI, USDC and USDT. Proposals 94, 130, 159, 247 and 271 form the 15-unit primary rate-decrease
cohort; proposal 3 supplies three reverse-sign probes.

The script queries the Aave V3 Ethereum Core Pool at
`0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2` through the replaceable public Ethereum endpoint recorded in the
YAML contract. PublicNode is transport, not the source of ownership or a claim that a packaged dataset has been
licensed. Before distributing a bulk snapshot, provider terms and an independent RPC reproduction must be
archived separately. This aggregate screen does not distribute provider responses.

Only the `Borrow` and `Repay` event signatures frozen and independently derived at T0 are allowed. One RPC call
may OR-filter the two signatures and the three reserve-address topics. No `ReserveDataUpdated`, position,
balance, price, oracle, utilization or post-event query is allowed.

## Time rule

For each proposal, construct four consecutive seven-day bins covering the 28 days immediately before the exact
payload execution timestamp. A boundary is the first Ethereum block whose timestamp is greater than or equal
to its target UTC time. The start block is included and the end block is excluded. The execution block is the
final exclusive boundary and must never be queried.

The script rechecks the execution block timestamp and block hash against T0. It requests logs in fixed
5,000-block chunks. A transport or JSON-RPC range failure may recursively split a chunk, but cannot change the
scientific time window, event topics, assets or thresholds.

## Retained information

For each asset-event unit and each week, retain only:

- the block interval;
- number of `Borrow` events;
- number of `Repay` events;
- number of distinct debt users (`onBehalfOf` for `Borrow`, `user` for `Repay`).

Across the 28-day window, retain the corresponding totals and the union count of distinct debt users. User
topics are used only in memory to form sets. Participant addresses, amounts, realized rates, utilization,
transaction hashes, per-log block identifiers, raw logs and raw response bodies must not be serialized. The
pure reducer rejects removed, duplicate, out-of-window, wrong-contract, wrong-event and wrong-reserve logs; a
regression test inserts recognizable forbidden values and proves they do not survive serialization.

## Frozen unit rule

An asset-event unit is eligible only when all four weeks independently have at least:

- 10 `Borrow` events;
- 10 `Repay` events;
- 10 distinct debt users;

and the full 28-day window has at least 200 combined `Borrow`/`Repay` actions and at least 50 distinct debt
users. Missing or insufficient activity fails the unit. These modest floors are intended to reject visibly
underpowered units, not to guarantee user-level causal power. They will not be weakened after counts are seen.

## Frozen panel decision

D1A passes only if all four conditions hold:

1. at least 15 of 18 total asset-event units are eligible;
2. at least 12 of 15 primary rate-decrease units are eligible;
3. at least two of three reverse-sign units are eligible;
4. every proposal retains at least two eligible assets.

Any failure stops this Aave singleton panel before post-event acquisition. There is no threshold-tuned amber
rescue. A pass authorizes only a separately frozen D1B intervention-ledger and anticipation/identification
audit. It does not authorize a behavioral event study, GPU training, EcoMD calibration or a paper claim.

## Compute budget

D1A is a CPU/network audit capped at four CPU-core hours and 500 MB of temporary in-memory responses. It uses
no paid data, GPU, V100, RTX 2060, H20 or EcoMD simulation. Keeping the GPUs idle at this stage is an explicit
scientific gate, not a capacity shortage.
