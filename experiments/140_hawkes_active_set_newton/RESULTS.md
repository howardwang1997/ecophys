# Experiment 140 — independent active-set Newton reference gate

**Formal result:** **FAIL (7/9 hard gates passed)**

**Frozen protocol:** `6d3940b9024b2eb05a7728b4ee5619ed603d1212`, before implementation or any
formal-seed generation

**Formal implementation:** `1312b5bef6748a8363cfb0326b3a91a2c51d27f7`

**Protocol hash:** `670f47cc3501681575a21b00ea8864b9afde7e455c019ae39f13730cc57a2111`

## Decision

The active-set Newton polish solved 62/64 fresh-seed endpoints to the frozen `1e-10` projected-KKT and
complementarity criterion, usually to approximately `1e-15`. Two endpoints stopped at `2.449e-10` and
`2.987e-10`, so the all-endpoint convergence gate failed. Because each belonged to a different target pair,
only 30/32 targets had both starts qualified; the start-robustness gate therefore also failed even though the
maximum two-start objective gap was only `2.22e-16` nats/event.

The failure is a double-precision stagnation case in the frozen line search, not an ill-conditioned Hessian.
For each failed endpoint, the Newton direction had predicted decrease around `1e-20`; Armijo backtracking
reduced the step to `5.96e-8` or `2.38e-7`, at which point the candidate parameters were bit-identical to the
current parameters. The implementation accepted this zero-displacement candidate eight times, leaving the KKT
residual unchanged. This diagnosed defect does not permit a PASS or a post-hoc tolerance change.

## Hard gates

| Frozen gate | Result | Evidence |
|---|---:|---|
| Chronology and provenance | PASS | Clean exact-SHA shards, frozen constants, ownership and one-thread environments |
| Fresh generated isolation | PASS | 16/16 expected fresh streams; no exp139 seed and no real archive |
| Derivative and KKT correctness | PASS | Gradient/Hessian/bound checks passed by wide margins on both nodes |
| Newton convergence | **FAIL** | 62/64 endpoints met `1e-10`; two stopped at `2.449e-10` and `2.987e-10` |
| Monotone repair | PASS | No endpoint exceeded its warm objective by `1e-13`; every recorded step met the frozen float predicate |
| Start robustness | **FAIL** | 30/32 target pairs were dual-qualified, below the required 32/32 |
| Algebraic equivalence | PASS | Objective, gradient-chain and inverse-transform checks all passed |
| Cross-node determinism | PASS | Complete shared-anchor records and hashes were identical |
| Complete unfavorable reporting | PASS | All streams, starts, warm fits, Newton traces and resource records are retained |

All nine gates were required, so the formal experiment is FAIL. The start-gap maximum and median themselves
passed (`2.22e-16` and `0`); start robustness fails only because two endpoints missed convergence.

## Fresh generated results

The 16 untouched streams contained 24,311--25,000 retained events. With two target marks and two fixed starts,
the formal suite contains 64 endpoints.

| Diagnostic | Formal result | Frozen requirement |
|---|---:|---:|
| Qualified endpoints | 62/64 | 64/64 |
| Endpoints reaching stricter `1e-11` stop | 62/64 | descriptive |
| Maximum / median final projected KKT | `2.9868e-10` / `3.1661e-15` | maximum `<=1e-10` |
| Maximum complementarity | `5.1366e-11` | `<=1e-10` |
| Maximum / median start objective gap | `2.2204e-16` / `0` | `<=1e-11` / `<=1e-12` |
| Warm projected KKT range | `1.0762e-11--2.2974e-8` | descriptive |
| Hessian condition-number range | `6.73--7.98` | descriptive |
| Minimum Hessian eigenvalue | `1.2251` | descriptive |

The selected target solution came from the rate-zero start in 30/32 targets and the positive start in 2/32.
All selected target solutions are numerically equivalent across starts at objective precision; selection does
not rescue the all-endpoint gate.

## Algebraic and derivative checks

The independent direct-Hawkes and intercept-only combined implementations agreed at every polished endpoint.

| Diagnostic | Maximum error | Frozen requirement |
|---|---:|---:|
| Direct/combined objective | `3.3307e-16` nats/event | `<=1e-12` |
| Gradient chain rule | `4.3656e-16` | `<=1e-12` |
| Inverse parameter transform | `5.5511e-17` | `<=1e-14` |
| Analytic gradient finite difference | `1.7214e-11` | `<=5e-7` |
| Analytic Hessian finite difference | `4.5578e-11` | `<=5e-7` |
| Hessian symmetry | exactly `0` on formal nodes | `<=1e-14` |
| Hand lower-bound case | exactly `0` | `<=1e-15` |

These results validate the objective, Hessian and parameterization identity. They do not override the solver's
all-endpoint failure.

## Floating-point stagnation postmortem

The failed endpoint on replicate 5, target 1, rate-zero start remained at KKT `2.9868e-10` for all eight Newton
iterations. Each iteration backtracked 25 times to step `5.9605e-8`; its stored parameter displacement was
exactly zero. The failed endpoint on replicate 8, target 1, positive start behaved identically at KKT
`2.4487e-10`, with 23 backtracks to step `2.3842e-7` and zero stored displacement.

At both points the objective and Hessian were finite, the Hessian condition number was below 7.0 and the
minimum eigenvalue was positive. The Newton directional derivatives were about `-2.03e-20` and `-1.28e-20`,
below the scale at which the objective's Armijo decrease can be resolved in float64. A software guard should
reject a bit-identical candidate as stagnated instead of recording it as an accepted step. Such a guard would
make the termination honest but would not turn these frozen endpoints into passes.

## Compute and reproducibility

- Shard 0: even replicates; 3.853 worker seconds and 8.143 systemd CPU seconds.
- Shard 1: odd replicates; 3.765 worker seconds and 7.702 systemd CPU seconds.
- Both clean clones used Python 3.11.15, NumPy 2.4.6 and SciPy 1.17.1 at exact commit `1312b5be`.
- One CPU process and one BLAS thread ran per host with `CUDA_VISIBLE_DEVICES=-1`; both V100s stayed at 0% and
  5 MiB. Peak RSS was about 108 MiB per shard.
- Shard 0 SHA-256: `c1d7f0edd027511b32b9630d29471fa6270efbccde73d571fa89666a491a69f5`.
- Shard 1 SHA-256: `598b7510501bdd9e9d19d9c11f59086af1bc09dee245e9510196f3f97df14719`.
- Merged SHA-256: `7216af08c55cfe00fa93d1c80b96cd31c5635312dea7a69d44db71cb0c832871`.
- A second merge to a temporary path was byte-identical to the archived merged artifact.

## Claim boundary and next action

Exp140 does not formally close exp139's direct-reference blocker and cannot change either prior FAIL. It also
contains no real data, EcoMD latent or market-physics evidence. The practical discrepancy is only a few
`1e-10`, far below exp139's already passed `1e-5` real-fit requirement, so another formal optimizer chase would
have negligible scientific value and would distract from the load-bearing NCS blockers.

The post-result software now has a tested zero-displacement/stagnation guard, recorded after this immutable
formal artifact without rerunning exp140. The research program then returns to G0 method novelty and G3's
frozen EcoMD-to-message semantics plus genuinely unseen dates/markets. Paid L2 remains locked, and exp138's
exposed test split remains ineligible for confirmation.
