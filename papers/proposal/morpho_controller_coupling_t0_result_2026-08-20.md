# Morpho allocator--IRM coupling — T0 result

**Decision:** PASS for the mathematical encoding; the research route remains **AMBER**.

**Formal run commit:** `7bb63f2d811de1211cdd60c5eed69e8ca7b52240`

**Canonical result SHA-256:** `91a4738beff17da6d16972faa1ddcbc844a76643678aec300ec9c6ca0cc3f64e`

The formal run used 10,000 deterministic synthetic trials from the clean, pushed source commit. All seven
numerical gates passed. This establishes only that the source-bound accounting and AdaptiveCurveIRM update have
been encoded consistently; it is not evidence of novelty, deployment prevalence, causal effects or venue fit.

## Numerical result

| Gate | Maximum residual or support | Result |
|---|---:|---|
| pressure continuity | `2.6485e-16` | pass |
| global pressure conservation | `3.7847e-16` | pass |
| minimax lower-bound violation | `0` | pass |
| minimax attainment | `1.1102e-16` | pass |
| equalised-utilization spread | `2.2204e-16` | pass |
| differential rate-memory invariance | `2.6645e-15` | pass |
| nonzero common-mode update | 9,846 / 10,000 trials | pass |

The smallest nonzero common-mode log-rate shift was `3.1716e-05`. Trial systems contained between two and twelve
markets. The exact machine-readable values, pinned source commits and file digests are in
`results/empirical_physics/morpho_controller_coupling_t0_v1.json`.

## What was established

For `q_i = B_i - 0.9 S_i`, a pure movement of supplied assets obeys the implemented graph continuity equation
and preserves total pressure. Exact utilization equalisation attains the unavoidable lower bound on maximum raw
utilization error. When aggregate utilization differs from 90%, it leaves a common error and produces a common
AdaptiveCurveIRM log-rate update while suppressing differential updates away from hard bounds.

These are exact consequences of the definitions, not a new theorem. Conservation, consensus, persistent
excitation and integral-memory arguments already cover the generic mathematical structure. A paper still needs a
nontrivial field prediction about where pressure and controller memory are displaced, plus evidence that the
prediction transfers beyond one protocol or one curator.

## Blinding and compute audit

- used only synthetic arrays and constants from pinned official source;
- did not query a historical reallocation, amount, rate, utilization, price, liquidation or market outcome;
- did not use EcoMD, a GPU, paid data or a remote compute worker;
- ran from a clean worktree whose commit was already pushed.

## Authorized next action

Freeze a documentary/on-chain-role identity gate before any reallocation history. It must distinguish a source
repository that *can* run a bot from evidence that a named operator actually runs automation on a named vault.
Periodic timing, an EOA role, a vault-specific example configuration or repeated transaction sender is
insufficient by itself. Passing that identity gate authorizes only a separately frozen event-support audit; it
does not authorize numerical market outcomes.
