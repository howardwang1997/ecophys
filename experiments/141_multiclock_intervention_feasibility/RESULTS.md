# Experiment 141 result

**Decision:** PASS for generated-data feasibility F1--F3.

**Scientific status:** no real-market, model-novelty, NMI or NCS claim is authorized. R0 may start; R1 remains locked.

## Provenance

- Preregistration/config commit: `613a14f26`.
- Implementation commit: `fd5accb41`.
- Frozen development-fit commit: `2ffcb208e`.
- Raw-artifact archive commit: `b525debf3`.
- Config SHA-256: `2e52c5d0f15ed47bfb961b59360a96fb746360f79bf6b6a907910e1b2452186d`.
- Research-code SHA-256: `55e61a1f20f95e95c5d73172bd3315f43fd73cf6dfd91124142d9a676336ac52`.
- All three shards reproduced shared anchor
  `1f54df518a02036f8bde07d64c3b7752872eb21e4e3d309d20b9d00c2ca1ce04`.
- Six remote/local raw-file SHA-256 pairs matched exactly; see `artifacts/RAW_MANIFEST.yaml`.
- The three shards contained 240 unique held-out rows: 30 seeds × 2 magnitudes × 4 truth families.

## Frozen gates

| Gate | Observed | Required | Result |
|---|---:|---:|---|
| Mechanics violations | 0 | 0 | PASS |
| Single-rate improvement vs frozen | 94.53% | ≥25% | PASS |
| Single-rate seed-bootstrap 95% lower | 93.74% | >10% | PASS |
| Single-rate improvement vs instant | 92.69% | ≥10% descriptive | PASS |
| Two-rate improvement vs frozen | 93.49% | ≥10% | PASS |
| Two-rate seed-bootstrap 95% lower | 92.67% | >0% | PASS |
| No-adaptation degradation vs frozen | 0% | ≤5% | PASS |
| Confound detection | 96.67% | ≥90% | PASS |
| Clean single-rate false positives | 0% | ≤10% | PASS |
| Cross-host anchor equality | exact | exact | PASS |
| Cross-device relative loss spread | 2.113×10⁻⁷ | ≤10⁻³ | PASS |

Standardized effect-vector RMSEs were 2.4252 / 1.8149 / 0.1327 for frozen / instant / multiclock under
single-rate truth, and 2.1196 / 1.5496 / 0.1380 under two-rate truth. No-adaptation paths were exactly identical
under frozen, instant and multiclock because their development-conditioned slope was frozen at zero.

## Hardware result

| Worker | Scientific shard wall time | Final probe loss | Exact resume | Peak reserved memory |
|---|---:|---:|---|---:|
| V100-A 32 GB | 302.45 s | 0.0176299177 | yes | 0.357% |
| V100-B 32 GB | 325.00 s | 0.0176299177 | yes | 0.357% |
| RTX 2060 8 GB | 198.63 s | 0.0176299140 | yes | 1.515% |

All losses and gradients were finite. The 2060 used an isolated clone of a CUDA-12.4-compatible Conda environment;
the historical dirty ABIDES checkout and its incompatible CUDA-13 environment were not modified.

## What this establishes

1. The minimal exchange kernel can execute the controlled intervention without price--time, tick, crossed-book,
   depth, cash or inventory violations in this generated workload.
2. With the controlled family known and development observations available, a slower response clock is identifiable
   from held-out magnitudes and seeds in this generator.
3. The frozen implementation and continuation path execute consistently on the two V100s and the 2060 without a
   device-specific scientific setting.

## What this does not establish

The result is intentionally self-generated and family-conditioned. It does not show that the family is identifiable
from real pre-intervention data, that one-rate adaptation is a real market mechanism, that the model predicts a real
rule change, or that the method is novel.

The very large two-rate improvement is a warning, not extra evidence. The six primary components average only early,
middle and late order-type fractions, so a one-rate curve can absorb much of the deliberately misspecified two-rate
truth. The controlled family label also supplies information unavailable in a blind deployment. Therefore exp141 is
best interpreted as an integration/identifiability smoke gate, not a hard synthetic benchmark or paper figure.

## Operational deviation

The V100 launch shell misquoted the `idle_for_new_primary_task: true` grep: it verified the field text but emitted a
missing-file warning for the token `true`. A read-only preflight immediately before launch had verified both values
as true; the same launch chains separately verified absent release markers, empty compute-process lists and zero GPU
utilization. The jobs ran alone. This did not alter scientific code or seeds, but it is retained in the raw manifest
instead of being silently described as a perfect launch.

## Decision

F1--F3 are closed PASS. The next active gate is R0: select one development intervention and one plausibly independent
sealed replication with exact rule timestamps, controls, event-data coverage and licenses. No paid data, large model,
paper claim or GPU expansion is authorized until R0 passes and an R1 protocol is frozen.
