# Morpho Public Allocator pressure displacement — T0 result

**Decision:** PASS for the source-bound mathematical encoding; the research route remains **AMBER**.

**Formal run commit:** `4a480108e1090dc88460b52c4f8ffd6a81738b72`

**Config SHA-256:** `aac2a7c87d8d40a9fbae9405abb4014453f8a5f0b1928ff3e3ec5dbaa3a4f409`

**Canonical payload SHA-256:** `f6b765d249ca75a0355db3007508201b41eab257367a15194c0e52a8625ea2a6`

**Result-file SHA-256:** `810b3125adfdcd808170c97f0ae0ad174f1846abf9a874ce288e22079407d671`

The formal run used 10,000 deterministic synthetic trials from a clean commit already matched to its upstream
branch. It also verified clean tracked worktrees and pinned commits for the official Public Allocator and
AdaptiveCurveIRM sources, exact hashes for the three frozen allocator files, the source-level 90% target and the
four cap-transition statements. All seven gates passed. An independent read-back reproduced the canonical
payload hash exactly.

## Numerical result

| Frozen gate | Maximum normalized residual or statistic | Result |
|---|---:|---|
| pure-routing pressure continuity | `3.9871e-16` | pass |
| JIT network source equals borrow | `4.3482e-16` | pass |
| donor/target pressure partition | `3.7950e-16` | pass |
| full-JIT displaced fraction equals `0.9` | `1.1102e-16` | pass |
| per-market `maxIn + maxOut` invariance | `2.2196e-16` | pass |
| capacity bound and independent-vault additivity | `2.7906e-16` | pass |
| nonnegative touched-market JIT pressure | minimum `23.2945` | pass |

All residuals are below the frozen `1e-12` ceilings. The positive minimum is a property of the frozen random
support, whose donor flows start at `1e-3`; the analytical nonnegativity statement itself follows from
`0 <= r <= x` and is not inferred from this minimum.

## What was established

For pressure `q_i = B_i - 0.9 S_i`, a target borrow `x` supported by routed supply `r=sum_i f_i` changes donor
pressure by `0.9 f_i`, target pressure by `x-0.9r`, and total pressure by exactly `x`. A fully JIT-funded borrow
therefore places 90% of the new pressure on donor markets and 10% on the target. The exact Public Allocator
transition also preserves every market's `maxIn+maxOut`, and the implemented one-vault capacity equals

```text
min(maxIn_target, sum_i min(maxOut_i, vault_supply_i))
```

under the assumptions stated in the frozen plan.

These are source-bound accounting lemmas and a tested implementation. They are not an irreducible theorem or a
paper-level discovery. Public documentation already describes shared liquidity and donor-rate effects; prior
curator-network work already covers mutualized stress; known-incident analyses already discuss Public Allocator
amplification. The T0 pass therefore does not raise the route above AMBER.

## Blinding and compute audit

- used only deterministic synthetic arrays and pinned official source;
- did not query historical events, calldata, receipts, flow-cap values, balances, rates, utilization, prices,
  liquidations or outcomes;
- did not inspect the Resolv incident data;
- did not use EcoMD, paid data, a GPU or any remote worker;
- generated the artifact once from a clean, pushed commit.

## Authorized next action

Freeze a D0 transport/support audit before retrieving event history. D0 may inspect only exact transaction and
event identities needed to decide whether the field design has at least two chains, 300 atomic JIT-borrow
transactions, 90 days and 12 donor--target edges. It must compare canonical receipts against an independent
finalized index and include dense-block adversarial checks. It must not compute amounts, rates, utilization,
prices, liquidations, controller response or any market outcome.

A D0 pass would authorize exact state reconstruction, not a paper claim or GPU training. A D0 failure closes the
route without threshold relaxation. Even after D0, viability requires a delayed effect not implied by the
contemporaneous identity and, for NCS, a general inference method plus a genuinely independent second system.
