# EcoMD action-counterfactual trigger audit (2026-09-04)

## Canonical decision

No qualified re-entry trigger was found. Candidate harvesting, Cycle 17, implementation, outcome
access, EcoMD changes, SSH and all three GPU workers remain closed for these leads. The formal result
is `papers/proposal/ecomd_action_counterfactual_trigger_audit_2026-09-04.md`.

## Durable findings

- ACIF (arXiv:2608.06427v1) directly occupies disagreement-driven intervention selection for
  structural generators. Its prospective algorithm selects where surviving models disagree, then
  conducts that intervention and collects real-system outcomes. It identifies only relative to a
  separating admissible intervention family. Finite balanced-separation theory does not extend the
  guarantee to continuous neural markets; that extension is named future work.
- ACT (arXiv:2506.02084v2) directly occupies adversarial tuning of causal time-series simulators and
  optimized discriminators. It explicitly says distributional fit is not causal fit and causal fit
  requires experiments. Cross-simulator disagreement remains an acquisition rule, not external
  truth.
- CAER (arXiv:2608.30897v1) uses a detached action-versus-null prediction difference to weight
  action-conditioned world-model loss. The paper itself says the quantity is a predictive contrast,
  not a do-interventional estimand, and its advantage is conditional on unproved weight--utility
  alignment.
- Exact paper-spec boundary: with `rho=S/max(mean(S),eps)`, `mean(rho)<1` whenever
  `0<=mean(S)<eps`; at `S=0`, all weights are zero. If an action-only pathway is zero-initialized,
  non-dropped samples then weight its gradient by zero and dropped samples disable it, so the
  action-blind manifold is absorbing under a zero-gradient-preserving optimizer.
- The pinned Apache-2.0 CAER implementation at
  `1f46972f1b15a12e82626a0b4a0e0be385cafc99` already fixes that boundary by replacing
  zero/sub-epsilon effect maps with uniform weights and normalizing by realized coefficient mass;
  it tests the zero-map fallback. The obvious repair is therefore already released.
- TEMPO, Policy-Shaped Prediction and World Action Verifier occupy generic task-aware weighting,
  sparse action relevance and self-improving forward--inverse verification. WAV still requires new
  environment interactions. None certifies an unseen market action from a passive tape.
- CAER improves reported aggregate metrics but camera trajectory accuracy falls `0.6211 -> 0.5474`
  and RoboTwin trajectory accuracy falls `0.2781 -> 0.2610`; every experiment uses eight H20 GPUs.
  This motivates claim-specific falsification, not an EcoMD port. Reweighting also does not remove
  Experiment 107's fixed-mechanism ceiling.
- ScratchWorld supplies a real pinned-VM exact-counterfactual capability and copy-resistant
  changed-field metric, but no public repository/raw-project fixture is identified and it has no
  common gradient/action semantics with DoTime or EcoMD. DSGE-Gym supplies structured economic
  off-path tests but its artifact is reviewer-anonymous at the cutoff and its continuous macro
  policy tasks are not hard-event market truth.
- Three append-only audits were added: ACIF `not_trigger`, CAER `not_trigger`, and executable-testbed
  extension `partial_capability`. They remove zero blockers. Canonical totals are 305 evidence
  records and 28 trigger audits, zero qualified.

## Re-entry condition

Require one of: (1) lawful assigned market action truth with complete state, propensity,
interference, independent confirmation and two same-action simulator lineages; (2) a nontrivial
self-weighting theorem that survives a positive action-present floor and an irreducible estimator
validated at equal cost on two open executable systems; or (3) a second licensed pinned hard-event
system with the same intervention, replay and gradient semantics plus a market-native mapping. A
zero-map fallback, another internal simulator score or another semantically different exact world
does not qualify.
