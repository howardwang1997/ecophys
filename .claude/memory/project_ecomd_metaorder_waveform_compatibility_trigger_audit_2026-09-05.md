# EcoMD metaorder, waveform and compatibility trigger audit — 2026-09-05

## Decision

Three post-closure sources were audited and all are `not_trigger`. No candidate card, machine card,
implementation, outcome access, simulation, SSH or GPU work is authorized. The A800 and both V100
workers remain idle for these routes.

## Durable findings

### Anonymous metaorder reconstruction

- Goliath--Gebbie 2026 correctly finds that impact-targeted synthetic partitions do not recover the
  LMF relation, while LMF-targeted partitions recover it by construction.
- If public tape is `X`, true parent partition is `Z`, independent reconstruction randomness is
  `U`, and synthetic labels are `A(X,U)`, then `I(Z; A(X,U) | X)=0`. Random assignment cannot add
  latent-parent information absent from the tape.
- Cross-fitting can test prediction or target transfer but cannot convert a synthetic partition into
  identification. Re-entry still needs authoritative parent/child truth or a sharp theorem under
  testable restrictions with an untouched labelled replication.

### Whole-trajectory learned composition

- Time Without Timesteps is a genuine new capability: learned trajectory operators are assembled by
  waveform self-consistency and solved/differentiated with JFNK/GMRES.
- It explicitly reports that a near-zero learned-model residual can coexist with large physical
  error and that coupling-induced training-distribution coverage is the dominant failure mode.
- In the linear case, coupled error is multiplied by
  `[I-(A+E)W]^{-1}`. Isolated MSE and spectral radius therefore do not control true error or
  nonnormal resolvent amplification.
- Waveform relaxation, compositional operators, DAgger-like dataset aggregation, goal-oriented SDE
  losses and nonnormal-rollout regularization occupy the obvious repairs. Event-driven stochastic
  EcoMD is outside the demonstrated contract and supplies no external trajectory truth.

### Decision-compatible scenarios

- Hashimoto et al. 2026 correctly replace one global realism scalar by
  `Gamma(P,Q;H)=sup_h |rho_P(h)-rho_Q(h)|`; under expected loss this is an IPM over hedger-induced
  losses.
- Estimating that IPM from independent price-taking paths is standard empirical-process/GAN work.
  Training a generator against it is directly occupied by Gen-DFL, Diff2SP, decision-focused
  scenario generation and adversarial/robust deep hedging.
- Interactive EcoMD requires policy-induced laws `P_h`, because actions can change the path. A
  passive tape cannot evaluate losses for actions that would have changed that tape; repeated
  assigned same-prestate response truth remains missing.

## Re-entry boundaries

1. Metaorders: authoritative parent links or a sharp identifiable functional plus matching lower
   bound and independent labelled confirmation.
2. Waveform composition: an inference-observable true-error theorem for dependent stochastic hard
   events beyond waveform relaxation, DAgger, goal-oriented learning and nonnormal control.
3. Compatibility: a theorem not reducible to a loss-class IPM/decision-focused generation, or a
   lawful interactive-market panel with common actions and untouched response truth.

Formal report:
`papers/proposal/ecomd_metaorder_waveform_compatibility_trigger_audit_2026-09-05.md`.
Registry totals after this session: 563 evidence records and 68 trigger audits, zero qualified.
