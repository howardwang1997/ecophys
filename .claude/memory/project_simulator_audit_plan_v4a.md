---
name: simulator-audit-release-plan-v4a
description: "Active post-G0 plan: falsifiable state/law/observation audits across EcoMD and two external simulators, plus EcoMD's first formal release."
metadata:
  node_type: memory
  type: project
---

# Simulator audit + EcoMD release — lasting decisions

- Active plan: `papers/proposal/plan_v4a_simulator_audit_release.md`.
- The proposed paper studies whether incomplete state continuation, gradient-dependent transition laws and
  invalid latent-to-observation substitutions can change calibration/scientific conclusions. It does not claim
  a new invariant-gradient estimator or real-market physics.
- TMLR is conditional on F0 audit novelty, causal defect effects and replication in two public non-financial
  stateful stochastic simulators. If those fail, retreat to an EcoMD software/model venue without generality.
- F1 requires a field-level observation map with units, clock, sign, price and identity semantics. Current
  synthetic aggregate emitters do not support individual-order or price-time-priority claims, and current real
  test data cannot be reused as unseen confirmation.
- The frozen field audit is `papers/proposal/ecomd_observation_map_spec_v0.md`. As of 2026-08-10, the current
  adapter FAILs real aggregate-event/individual-order semantics: it emits one event per step, uses model-unit
  sizes, creates a new ID for every removal/execution, and evolves a book price independently of EcoMD's
  internal price. It remains a `synthetic_fixture` only.
- The only immediately recoverable observation route is `aggregate_bin` with price choice P3. It remains
  AMBER until a preregistered machine-readable semantic contract accepts the scoped declaration and rejects
  dual-price, clock, unit, identity, latent/OFI and test-conditioned-latent defects before fitting.
- Immediate resource cap before F0--F2: about 10 V100-equivalent hours and 1,150 CPU core-hours. The current
  two V100 32 GB hosts are sufficient and may also run CPU jobs. H20 is excluded. No purchase or expansion is
  unlocked before the corresponding gates.
- Existing exp128--140 artifacts are preflight/development evidence. Paper-level claims require new fallback
  preregistrations and independent seeds; all archived FAIL decisions remain unchanged.
