# Morpho allocator--IRM coupling — D0A v2 result

**Decision:** **FAIL; close the field route before reallocation history.**

**Formal run commit:** `c7b9fe3e85e48c17758bcdfc14cbf98cd3422a35`

**Config SHA-256:** `c7f04b14b6a628778e78cd604e7ad6a366d65e09fe4ff677e3b19ef92dce668e`

**Canonical result SHA-256:** `72cc38bdee28af7109e7e60e5d0ad7ebcb1d7a7876fb9730aca81e80463231b0`

The three exact GraphQL role queries succeeded, but the frozen unique-identity gate failed. This result was
reached before any reallocation history, amount, rate, utilization or market outcome was requested.

## Role-identity result

| Operator anchor | All allocators | Official Public Allocator | Non-public allocators | Unique private identity |
|---|---:|---:|---:|---|
| Steakhouse USDC V1 | 4 | 1 | 3 | **fail** |
| Gauntlet USDC Prime V1 | 2 | 1 | 1 | pass |
| sky.money USDS Flagship V2 | 1 | 0 | 1 | pass |

The three non-public Steakhouse addresses are:

- `0x0000aeb716a0df7a9a1aad119b772644bc089da8`;
- `0x9e9110cfd24cd851ea5bc73a27975b33e308f9e1`;
- `0xfeed46c11f57b7126a773eec6ae9ca7ae1c03c9a`.

The query does not identify which address, if any, is the proprietary automated engine described by Steakhouse.
They could represent automation, operational redundancy, a manual key or a changed role setup. Selecting one by
transaction cadence or favorable downstream behavior would violate the frozen protocol.

Gauntlet's unique non-public role is `0xf23ba16d8d577529b1db2c276ea40d9291d48579`; sky.money's is
`0xe4d5f54ce1830d5ecc49751021f306cfe7a52649`. Their individual passes cannot rescue the required three-cluster
design.

## Gate summary

Five of six gates passed: fixed candidate count, three independent operator labels, three operator-authored
automation statements, pairwise distinct observed private addresses and three declared policy families. The
binding gate `one_nonpublic_allocator_per_anchor` failed. Because every hard gate was conjunctive, the overall
decision is FAIL.

This is an identification failure, not evidence that allocation bots or allocator--IRM coupling are absent. It
shows that public documentary claims plus current role registries do not uniquely bind all three planned
transaction clusters to automated executors.

## Transport and data audit

The v1 REST endpoint returned HTTP 404 before any role payload and produced no artifact. V2 used the single
precommitted GraphQL transport amendment; all three responses returned HTTP 200 and exact frozen vault addresses.
Only current name and allocator addresses were parsed, and raw responses were discarded after their SHA-256
digests were computed.

- no reallocation or transaction history was queried;
- no cadence, amount, balance, rate, utilization, price, liquidation, yield or outcome was decoded;
- no candidate or threshold was changed after seeing roles;
- no paid data, EcoMD, GPU or remote compute worker was used.

## Binding stop decision

Do not run D0B, inspect the three addresses' transaction histories, add a different Steakhouse vault, or infer the
bot from periodicity. The current Morpho field route is closed. Reopening requires a genuinely new design with an
untouched prospective interval and one of:

1. operator-signed disclosure that binds executor address, vault and policy epoch;
2. an on-chain strategy contract whose code and authorization provide the binding directly; or
3. a scientific claim that does not require assigning transactions to a hidden automation implementation.

T0 remains valid reusable algebra, but it is infrastructure rather than a paper result.
