# EcoMD queue-reactive impact-calibration trigger audit — lasting decisions

- Formal result:
  `papers/proposal/ecomd_queue_reactive_impact_calibration_trigger_audit_2026-09-05.md`.
- This was a bounded D-3 superseding trigger audit, not a discovery cycle. No raw market data,
  simulator output, implementation, notebook, SSH session or GPU was used.
- Decision: `not_trigger`, zero removed blockers, no candidate harvesting, graph unchanged.

## Lasting source correction

The Noble--Rosenbaum--Souilmi Queue-Reactive engine is genuinely open and useful: its official MIT
repository is pinned at `3080096cc0c79f43f1b82112cbde713710c014f6`, contains seeded C++
metaorder simulation plus a Python/C++ estimation pipeline, and exposes impact/no-impact strategy
comparisons. It is not a new post-audit release. GitHub records creation on 2026-03-23 and only two
commits, completed by 2026-03-26, before the existing August audits.

## Lasting scientific findings

1. QR's action is a signed, timed tape of executable child trades. EcoMD's historical
   `state_kick` is a latent-coordinate displacement; `price_jump`, `news`, `temperature_spike` and
   `liquidity_drop` also have different semantics. The engines therefore do not yet form a
   same-action comparison.
2. The QR main result chooses a `t^(-3/2)`-tail feedback kernel from a theoretical impact target and
   calibrates its multiplier against the same target response. Its MLE alternative uses anonymous
   trade history. Concavity, reversion and self-impact under that channel are valid internal model
   behavior but not independent mechanism or field-counterfactual evidence.
3. A finite linear intervention-basis audit reduces to design rank and persistent excitation. If
   the calibration design is rank deficient, a nullspace perturbation matches it and changes a
   held-out action; if sufficiently persistently exciting, standard system identification already
   supplies the span condition. For unrestricted nonlinear simulators, a finite action family
   admits the existing off-support twin.
4. A single temporal TWAP need not be only one scalar direction; shifted windows may identify a
   finite convolution kernel. The rigorous objection is target reuse and missing transport truth,
   not an automatic one-profile/one-dimension slogan.
5. The public-feed 29-microsecond timing mode is consistent with races but does not identify them:
   participant identity, losing attempts and private send time are absent, and exact winner/loser
   race measurement is direct prior work.
6. The paper has a small provenance discrepancy: main text 100,000 paths/`m=0.036`, Appendix D
   50,000 paths/`m=0.035`; the fixed executable defaults to 100,000. Record this if the engine is
   ever used, but do not turn it into a research claim.

## Re-entry and compute boundary

Re-entry requires a licensed assigned parent-metaorder response with complete state and intended
children, an untouched independently governed exact-action replication, frozen same-action adapters
for EcoMD and an external engine, calibration-family separation, and a transport/abstention result
beyond persistent excitation, inverse-crime avoidance, model discrepancy, LOB-Bench and current
interventional-fidelity inference. A card and new machine decision remain mandatory before any
implementation, outcome access, SSH or A800/V100 work.

