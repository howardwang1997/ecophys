---
name: Plan v5 interventional market world
description: Active mechanism-separated market-world iteration. Exp141 F1-F3 passed generated-data feasibility on 2026-08-12; R0 is active, while real-data work, paid data, NMI/NCS claims and scale-up remain locked.
type: project
---

# Plan v5 — Interventional market world

## Lineage and claim boundary

Branch `interventional-market-world-v1` descends from
`ncs-invariant-calibration-v4@a8bf89427f38d53cf0cb1ad836b133d74e9d6ecd`. It preserves EcoMD, Plan v3/4 and
negative experiments as history, but does not treat latent MD, thermodynamic variables, previous checkpoints or
spent datasets as evidence. The active object is exact exchange mechanism + event behavior + slower adaptation +
explicit institutional intervention.

NMI requires a transferable method result across mechanisms/environments. NCS requires a replicated real market
response law. Neither claim exists.

## Exp141 chronology

- Prereg/config: `613a14f26`.
- Implementation: `fd5accb41`; 170 full-repository tests passed, plus ruff and strict mypy.
- Development fit: source commit `fd5accb41`, artifact commit `2ffcb208e`; only seeds 100--115, 160 paths, zero
  violations, artifact SHA `4282ab93…`.
- Formal raw archive: `b525debf3`; 240 rows across three balanced seed shards, six remote/local SHA pairs exact.
- Workers: V100-A `100.80.236.112`, V100-B `100.123.220.57`, RTX2060 `100.105.21.7`; isolated checkouts and
  artifacts. RTX old ABIDES checkout/environment untouched.

## Exp141 result

- Mechanics violations: 0.
- Single-rate multiclock improvement vs frozen 94.53%, bootstrap lower 93.74%; vs instant 92.69%.
- Two-rate improvement vs frozen 93.49%, bootstrap lower 92.67%.
- No-adaptation degradation 0%.
- Confound detection 96.67%, clean FPR 0% at frozen |z|>3.
- Shared anchor exact across all hosts.
- CUDA exact resume all hosts; cross-device relative final-loss spread `2.113e-7`; peak reserved 0.357%, 0.357%,
  1.515%.

Overall F1--F3 PASS. Full result:
`experiments/141_multiclock_intervention_feasibility/RESULTS.md`.

## Critical limitation and next gate

The task is self-generated and family-conditioned. A one-rate candidate also improves 93.49% under two-rate truth
because the primary vector contains only early/middle/late averages of market/cancel fractions. Treat this as an
integration and controlled-identifiability smoke gate, not a synthetic SOTA benchmark or paper figure.

R0 is now active: identify one development intervention and one plausibly independent sealed replication with
exact rule timestamps, treated/control design, event-data schema/coverage, license, missing-sequence policy and a
pre-access response vector. Do not purchase data or expand compute until R0 passes and R1 is separately frozen.
