# Experiment 141 development fit

**Status:** frozen development artifact; formal held-out seeds were not generated.

**Source implementation:** `fd5accb41ddf42f7c31f87470bdfada84709a9e8`

**Artifact:** `development_fit.json`

**Artifact SHA-256:** `4282ab93652900d4ef74fb323eb99e67728d9840b60a75343bfd544272a7ca14`

## Audit

- Seeds: 100--115 only.
- Magnitudes: 0.5, 1.0 and 1.5 only.
- Generated paths: 160, including paired no-intervention paths.
- Mechanically invalid paths: 0.
- Config SHA-256: `2e52c5d0f15ed47bfb961b59360a96fb746360f79bf6b6a907910e1b2452186d`.
- Research-code SHA-256: `55e61a1f20f95e95c5d73172bd3315f43fd73cf6dfd91124142d9a676336ac52`.
- Wall time on the Mac: 103.85 seconds.

The runner records `formal_seeds_touched=false`; configured formal seeds begin at 10,000.

## Frozen parameters

| Controlled family | Target slope | Relaxation rate | Development probability RMSE |
|---|---:|---:|---:|
| No adaptation | 0 | 0.202858 | 0 |
| Single rate | -0.774816 | 0.202858 | 0.019104 |
| Two-rate truth, one-rate fit | -0.620881 | 0.197219 | 0.020201 |

For reference, the single-rate generator uses slope -0.80 and rate 0.18. The fitted values are not altered to the
known generator values. The deliberate two-rate misspecification remains a one-rate candidate in formal evaluation.

The six development standardization scales and the clean single-rate parameters for the absolute-z residual
detector are stored at full precision in the JSON artifact. This file reports development behavior only and does
not imply that any formal F1/F2 gate passes.
