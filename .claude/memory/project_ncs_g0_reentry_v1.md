---
name: Plan v4 G0 re-entry v1
description: Theorem-first, zero-cost candidate-admission work on ncs-plan-v4-g0-reentry-v1. The old v0/v1 G0 FAIL remains binding; automation may only return READY_FOR_HUMAN_AUDIT, never novelty PASS.
type: project
---

# Plan v4 G0 re-entry v1

On 2026-08-12 the pre-iteration Plan v5/exp141 state was frozen at
`archive/plan-v5-exp141-feasibility-20260812@436dad6e7f80999584e44c4a616a1f213b9c814d`.
The new `ncs-plan-v4-g0-reentry-v1` branch joins that history with `origin/main@51466a703` at merge
`720c35717080bc15f0bba122b9beb76503b90bfd`.

Plan v4 is authoritative, but the 2026-08-10 G0 FAIL remains binding. The branch first implements a typed,
machine-readable candidate-admission and adversarial-equivalence gate. It must reject the old composition and may
only produce `READY_FOR_HUMAN_AUDIT`; it cannot decide novelty or reopen NCS automatically.

R0--R3 use existing documents and generated YAML fixtures on the Mac CPU only, capped at 2 core-hours and zero
GPU-hours. They open no market or sealed data. Current 2xV100 32 GB resources and any future non-H20 expansion stay
locked until a new theorem/identity survives primary-literature and proof review. Plan and gates:
`papers/proposal/plan_v4_g0_reentry_v1.md`.

R1--R3 completed on 2026-08-12. Exp142's eight cases all matched, but its raw `actual_market_data_read=false` was
incorrectly folded through `all(gates.values())`, so the immutable formal result is `FAIL_PROCESS_VALIDATION` (raw
SHA `ec41af58…`). Exp143 was separately preregistered and changed only aggregation semantics; 10/10 positive gates
passed (raw SHA `56084cbc…`). The suite has no real candidate, so G0 remains FAIL and both V100s remain locked.

The verified result tree `81866a73f` was fast-forwarded into remote `main` on 2026-08-12. At integration time the
development branch and `main` matched exactly, and the predecessor archive remained fixed at full commit
`436dad6e7f80999584e44c4a616a1f213b9c814d`. Post-merge documentation does not change the scientific verdict.
