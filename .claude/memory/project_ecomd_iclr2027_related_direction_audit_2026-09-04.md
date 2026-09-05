# EcoMD-related ICLR 2027 direction audit (2026-09-04)

## Canonical decision

The requested second ICLR 2027 direction from the molecular-dynamics-style market-simulation program is
**killed at re-entry**. No qualified trigger exists, Cycle 17 remains unopened, and no machine card, simulator
run, implementation, data action, outcome access, SSH session, or GPU job was authorized or performed.

The formal record is
`papers/proposal/ecomd_iclr2027_related_direction_reentry_audit_2026-09-04.md`.

## Durable reasons

- EcoMD v1's frozen stationary held-out result is 2/11 in every window, with robust failures in tails,
  volatility clustering, DFA, leverage, and volume coupling. Scaling or adding seeds is not a mechanism.
- A new long-horizon-gradient paper currently reduces to ARTBP, unrolled neural-physics training,
  differentiable-simulator gradient estimators, and the 2026 temporal-learnability theorem. No irreducible
  estimator or market-specific theorem exists.
- Stochastic pair sampling reduces to Random Batch Method. Established work covers the method, long-time
  invariant-law error, and phase-transition shifts; an EcoMD example alone is not an ICLR contribution.
- Exact market allocation remains discontinuous at ties and event-order changes. Smoothing is not exact rule
  preservation.
- Interactive LOB generators and LOB-Bench do not supply the assigned, complete-state, same-estimand field
  counterfactual needed to reopen prospective simulator validity.
- ICLR 2027 deadlines are 2026-09-18 AoE for abstracts and 2026-09-25 AoE for papers. The repository already
  contains the much stronger, substantially completed Paper D submission.

## Re-entry conditions

Reopen only after either:

1. a genuinely new estimator/theorem with analytic bias--variance--cost guarantees, a hard boundary, and
   validation on at least two non-EcoMD systems; or
2. a licensed truth/control asset with assigned legal actions, replay-complete pre-state, interference and
   outcome schemas, untouched confirmation, and independent same-estimand replication.

Any later three-worker plan requires a new active machine decision. Keep V100 and A800 pools separate and
reproduce a canonical V100 cell before using the A800 for scale or OOD work.

