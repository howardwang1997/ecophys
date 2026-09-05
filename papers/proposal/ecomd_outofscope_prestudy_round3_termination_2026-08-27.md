# Out-of-scope pre-study round 3: formal/numerical-systems axis — and series termination

Date: 2026-08-27 (round 3)

Status: **bounded paper-only pre-study, axis-shifted per governance (no relabelling); not a
discovery cycle; no cards, forecasts, implementation, outcome access, or compute**

## Why an axis shift

Rounds 1--2 searched AI-systems lanes (thermodynamics of learning, gradient access, checkpoints,
evidence contracts, EWS, leakage). Under the repo's own rule, a third round relabelling the same
families is forbidden. Round 3 therefore shifts to the formal-methods / numerical-analysis /
systems axis where the researcher's stack (differentiable simulation, determinism tooling,
statistical-mechanics identities) also fits.

## Programs and collision checks

| # | Program | Collision result | Ceiling |
|---|---|---|---|
| R3-1 | Gradients of long-time-averaged objectives in chaotic differentiable simulators (e.g., market-lab engine as testbed) | **Direct, mature collision**: Least-Squares Shadowing / NILSS / NILSAS line (JCP 2017/2019, MIT/Berkeley), fast adjoint response for hyperbolic chaos (SIMA 2023), shipped in SciMLSensitivity | Occupied for a decade; incremental JCP-class at best |
| R3-2 | Certified/verified gradients or certificates for differentiable simulators | Adjacent occupants (certifiable design optimization RSS 2022; verified SciML fragments); no single definitive occupant | PL/FM venues (CAV/ICFP-class); **sub-NMI** — NMI does not take this contribution type |
| R3-3 | Deterministic-replay contracts for systems (beyond scientific software) | Occupied by industrial deterministic-execution and testing literature (FoundationDB/TigerBeetle-style simulation testing, Jepsen lineage) | Systems venues; sub-NMI |
| R3-4 | Stochastic-thermodynamics diagnostics of MCMC/samplers | Merges into round-1's occupied thermodynamics-of-learning lane (arXiv:2606.17252 and antecedents) | Collided (round 1) |

## Series conclusion: terminate

Three axes screened (AI-systems ×2 rounds; formal/numerical/systems this round) return the same
verdict, matching the round-2 structural finding:

- self-controlled truth ⇒ crowded lanes; residuals are narrow specialist increments;
- every candidate lands at workshop / specialist-journal / FM-venue ceilings, none at NMI/NCS;
- solo scale cannot win the breadth arms race in these domains today.

Continuing to round 4+ in the same exploratory pattern would be idea-count farming — the exact
failure mode the discovery protocol's epistemic-progress-per-effort rule exists to prevent. The
out-of-scope pre-study series is therefore **terminated** (three strikes across three genuinely
different axes), with the standing watch items retained:

1. descendants of arXiv:2606.17252 crossing into training dynamics with new identifications;
2. adoption of branchable-checkpoint / branching standards by a major framework;
3. stalling of the EWS-for-training preprint program leaving census-style gaps.

Re-entry into out-of-scope topic search requires a qualified trigger from that list (recorded
here as the de-facto watch ledger) or a PI scope amendment with a fresh protocol.

## Posture

The lean market path (variance pilot → human experiment → Paper 1 on the economics ladder)
remains the sole recommended execution path. Its gating input is unchanged: the four PI freeze
decisions for the pilot ethics package.
