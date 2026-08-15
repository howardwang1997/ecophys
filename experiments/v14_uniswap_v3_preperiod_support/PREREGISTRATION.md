# Uniswap v3 U1a preperiod support and identity feasibility

**Frozen:** 2026-08-15 10:21:30 UTC

**Role:** historical development; pre-treatment observability only

**Response lock:** no event at or after the first pool treatment block may be queried

## Question

Can free public chain infrastructure recover enough strictly pre-treatment pool activity and NPM identity history
to justify a larger U1 design, without selecting pools from realized post-treatment behavior?

This is not an effect study and does not construct a control group. U0 already established that all first 1,000
pools were newly activated, so no within-frame always-treated control exists. U1a tests only treated-pool support
and one identity layer. Even a pass leaves the control-source problem open.

## Frozen sample

Starting from the committed U0 1,000-row ledger, compute
`SHA256("u1a-v1|" + lowercase_pool_address)` and take the eight lowest hashes separately for packed fees `0x44`
and `0x66`. The exact 16 rows and their canonical hash are sealed in the manifest. Fee stratification is for
coverage, not population weighting; this small development sample is not representative.

No sampled pool's preperiod log was accessed before freeze. Transport was checked only on already consumed U0
mechanism data: 500 adapter events in the first treatment block and 28 logs in the governance transaction.
An impossible adapter topic on the consumed treatment block also confirmed the explicit `status=0`, empty-list
response schema. None of these calls touched a sampled pool's preperiod.

## Frozen window

Read only blocks 24,548,777 through 24,599,176 inclusive—50,400 blocks immediately preceding the first treatment
block 24,599,177. Fetch both boundary headers and require the end timestamp to be strictly earlier than treatment.
No treatment-block or post-treatment pool log may be opened.

## Pool support layer

For each sample pool, query four event signatures separately: `Swap`, `Mint`, `Burn` and pool `Collect`.
Blockscout documents a 1,000-log response maximum. A response of exactly 1,000 is therefore treated as saturated
and its inclusive block interval is recursively bisected. Only leaves below 1,000 are accepted; a saturated
single block fails the run. No endpoint substitution is allowed.

Retain counts, event-identity hashes and manager-owner addresses from the indexed owner topic. Do not decode or
retain swap amounts, price, ticks, liquidity amounts or token amounts. Manager-owner shares are action-count
shares, not economic-liquidity shares.

## NPM identity layer

Among preperiod `Mint/Burn/Collect` pool events whose manager owner is the official
NonfungiblePositionManager (`0xC364...`), hash-rank unique transaction IDs with frozen salt and take at most 64.
At least 32 eligible transactions are required.

For these transactions only:

1. open the transaction envelope only to retain `from`, block and transaction index; calldata is not decoded;
2. paginate Blockscout transaction logs;
3. pair each NPM event with the closest preceding unmatched same-action pool event and recover indexed token ID;
4. query that token's ERC-721 Transfer history only through the action block;
5. report owner immediately before the pool event and owner after the action transaction.

The transaction sender is an operational public key, not automatically a human or beneficial owner. The NPM NFT
owner is one observable ownership layer; vault beneficiaries, smart-wallet aliases and private intent remain
unresolved.

## Gates

All gates are frozen and conjunctive:

1. exact 16-pool sample and exact pre-treatment window;
2. complete unsaturated partitions, with zero duplicate/conflicting normalized logs;
3. at least eight swap-active and eight position-action-active pools;
4. at least 64 position-action logs;
5. NPM manager share at least 0.50 by position-action count;
6. at least 32 eligible NPM action transactions;
7. exact pool-action to NPM-token pairing rate at least 0.80;
8. post-transaction token-owner resolution at least 0.95 among exact pairs.

A pass unlocks design of a larger pre-treatment U1b coverage panel and a separate outcome-blind control-source
audit. It does not unlock U2. A failure narrows the project to pool-level M2 or requires a different identity/data
route; thresholds and sample cannot be repaired on this frame.

## Resource ceiling

- maximum HTTP attempts: 2,000 at no more than one per second across sources;
- maximum response bytes: 128 MiB;
- maximum normalized pool events: 250,000;
- expected wall time: several minutes, CPU/network only;
- paid data: zero;
- GPU: zero; both V100s and RTX 2060 remain idle;
- H20: excluded.
