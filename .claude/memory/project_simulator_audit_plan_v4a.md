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
- TMLR was conditional on F0 audit novelty. F0 failed on 2026-08-10, so the active route is now an EcoMD
  software/model release without a general simulator-audit claim.
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
- Exp142 is the frozen CPU-only contract firewall protocol. It has three valid declarations, twelve isolated
  semantic mutations, a no-fit-before-validation callback guard and a direct probe of the current adapter.
  Passing enforces vocabulary only; it does not establish empirical mapping, identifiability or novelty.
- Exp142 formally PASSed 9/9 once from clean implementation `44daf531` (result JSON SHA-256
  `57fa2bf3...f1e9cc`). All 12 invalid callbacks ran zero times. The adapter probe found 256 unique event
  counters and zero prior-ID references among 132 removal/execution rows. This preserves the message/order
  FAIL and advances only the prospective aggregate-bin P3 declaration to a code-enforced specification.
- F1 remains AMBER pending a separately preregistered aggregate-bin measurement/reconstruction implementation,
  train-only scale fitting and identifiability checks. No real held-out data, paid data or GPU is unlocked.
- Exp143 freezes that next CPU-only gate: 60-second half-open bins, exact six-mark/share-volume aggregation,
  streaming/checkpoint parity, generated P3 return/volume/direction recovery, held-out-corruption invariance,
  observation-only/sign-flip controls and an explicit latent-scale gauge. Formal root is `143202608`; no real
  archive or current event adapter is permitted.
- Exp143 formally PASSed 10/10 once from clean implementation `2b54170e` (result JSON SHA-256
  `f1c34143...f1bf0`). It reconstructed 4,096 bins from 104,160 generated rows with exact integer aggregates
  and `1.70e-16` maximum return error. Held-out corruption left the fit exact; training corruption changed it.
- F1 is therefore PASS only for synthetic implementation/semantics of aggregate-bin P3. Event/order support
  remains FAIL and the self-generated RMSE/likelihood gains are plumbing, not market evidence. F0 subsequently
  failed, so no E-B or external-validation expansion follows from F1.
- The former pre-F0 cap of about 10 V100-equivalent hours and 1,150 CPU core-hours is void. Release work uses
  local/CPU smoke and only a necessary single-V100 reference after its scope is frozen. H20 remains excluded;
  no data purchase or capacity expansion is authorized by this route.
- Existing exp128--140 artifacts are preflight/development evidence. Paper-level claims require new fallback
  preregistrations and independent seeds; all archived FAIL decisions remain unchanged.
- F0 prior-art closure is `papers/proposal/simulator_audit_f0_prior_art_2026-08-10.md` and is **FAIL**. ODD,
  TRACE, context-adequate validation, TDSM, ABM/scientific-software mutation testing, ProbFuzz,
  differentiable-gradient audits/Mosaic, observation-operator/model-discrepancy work, and 2026 silent-PINN
  experiments collectively occupy A1--A4 and their key causal endpoints. The fact that no one paper uses the
  exact same checklist is insufficient novelty.
- Consequently the general simulator-audit/TMLR route, E-B production, external-simulator adapters, and its
  V100/data expansion are stopped. Exp128--143 remain EcoMD release QA and failure disclosure. The active
  fallback is an EcoMD-specific transparent software/model release; it must not claim validated market-digital-
  twin status before stationary fidelity and real held-out aggregate evidence are repaired.
- A general audit route may be re-audited only after a new theorem/algorithm/metric, or preregistered evidence
  in two systems of a non-tuned composite state/law/observation defect that survives standard diagnostics and
  reverses a predefined scientific conclusion. No exploratory E-B run is authorized merely to search for it.
