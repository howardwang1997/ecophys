# Morpho Public Allocator pressure D0 v2 — formal result

**Decision:** **FAIL and stop before support interpretation, protocol values, or outcomes.**

**Formal run commit:** `78cfc09e08c7121dbdff998343d3b54576420ee5`

**Parent scientific config SHA-256:**
`bc6fc21cfd6b782280ace89d4d854b603dd19370bdad3c6d4803c72557333c60`

**Transport amendment SHA-256:**
`b549efa43be88d9ce9385224f61158767b042df824fef447f959b600c66634a4`

**Qualification canonical payload SHA-256:**
`d9b28e6549d120fd94acfc378946f1e5deb475abf67b2de3f4870acc18aa65de`

**Formal batch ID:**
`e35adb819faa8b8fb96885266ff6e87c6e73738e5c48e85645cf9e63ca0d6c59`

Ethereum and Base were provisioned from the same clean, upstream-matched commit and the same three pinned Morpho
source trees. The two CPU/network jobs were launched before either result was inspected. CUDA was hidden on both
workers and both V100s remained unused.

## Chain outcomes

| Chain | Worker | Start (UTC) | Wall time | Result | Canonical SHA-256 | File SHA-256 |
|---|---|---:|---:|---|---|---|
| Base | `v100_b_cpu_network_only` | 11:44:19 | 199.80 s | Portal shard 5 ended in `SqdPortalError` | `bb330b79…c16ca` | `b183ef85…e973` |
| Ethereum | `v100_a_cpu_network_only` | 11:44:24 | 243.06 s | Blockscout RPC connection timed out after configured retries | `181d11c9…1b2c1` | `8f90f2f…5313` |

Both chain artifacts have status `transport_fail_before_support_interpretation`, `support: null`, and
`merge_eligibility: false`. The Base aggregate records only the sanitized exception class and failing shard; it
does not establish whether the underlying cause was service overload, a stream interruption, or another Portal
failure. The Ethereum aggregate establishes a connection timeout, not an event-set discrepancy.

The exact aggregate-only chain artifacts are archived as:

- `results/empirical_physics/morpho_public_allocator_pressure_d0_base_chain_v2.json`;
- `results/empirical_physics/morpho_public_allocator_pressure_d0_ethereum_chain_v2.json`.

Their canonical payloads, file bytes, source hashes, qualification binding, worker assignments, hidden-CUDA
setting and common formal batch ID were independently rechecked after transfer.

## Merged decision artifact

The single local merge produced
`results/empirical_physics/morpho_public_allocator_pressure_d0_v2.json` with:

- canonical payload SHA-256
  `cf97beb874b855a07245ebf942f4ed8f21ffcf647ff06d677100ccc9378d8dab`;
- result-file SHA-256
  `6b261b7878d194aff5046ced2a626d2836c2b009ce69075c0bf8bdf98cc6a5c4`;
- `d0_pass: false`;
- decision `fail_stop_before_protocol_values_or_outcomes`;
- zero GPU hours and zero paid-data cost.

The frozen result contains pooled candidate and edge fields equal to `0`. These are legacy merger sentinels, not
observed counts: both authoritative chain-level support objects are `null`, so no candidate count, edge count,
time span, active-date count, vault count, classification rate or receipt-verification rate exists. The formal
artifact is retained byte-for-byte for auditability. Post-run maintenance changes the merger to emit `null` for
future unavailable pooled support and adds a regression test; it does not regenerate or reinterpret this run.

## Scientific interpretation and stop rule

This result says nothing about whether the frozen 500-pooled/100-per-chain support thresholds would have passed.
It neither finds zero candidates nor falsifies the proposed routed-liquidity mechanism. It establishes that the
one authorized, jointly launched D0 did not produce an admissible support dataset under its frozen transport
contract.

The pre-registered stop rule therefore closes this Public Allocator route before:

- decoding routed or borrowed amounts, balances, caps, utilization, rates, prices, liquidations, or outcomes;
- testing `0 < r <= x`, AdaptiveCurveIRM exposure, delayed memory, participant response, or causality;
- constructing D1, fitting EcoMD, using GPU compute, purchasing data, changing providers, or rerunning to seek a
  pass.

T0 remains a verified accounting implementation, but no empirical field result was obtained. It cannot support
an NMI or NCS paper claim. Any future route must be a newly justified and separately pre-registered question,
not a repair that selectively replaces this formal D0 after seeing its failure.
