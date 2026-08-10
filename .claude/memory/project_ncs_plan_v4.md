---
name: ncs-plan-v4-invariant-calibration
description: "Authoritative 2026-08-09 NCS plan: a gated invariant-measure/long-horizon calibration method beyond EcoMD, state/dynamics repair, validated L2 observation bridge, frozen real-data application, scalable non-H20 compute, and expandable data."
metadata:
  node_type: memory
  type: project
---

# NCS Plan v4 — lasting decisions

**Authoritative plan:** `papers/proposal/plan_v4_ncs.md`.

- The paper is not “EcoMD exists” and does not reinterpret simulator error as market physics. Its spine
  is a genuinely new invariant-measure/long-horizon calibration method with controlled error, validation
  on at least two independent model families beyond EcoMD, a repaired EcoMD, a validated model-to-L2
  observation bridge, and a frozen method-dependent real-data prediction.
- EcoMD's current `sum(dpos)/sum(abs(dpos))` is `latent_flow_alignment`, not empirical CKS OFI.
- Sim2Science remains an audit-only workshop artifact. If all gates pass, the NCS paper is EcoMD's first
  formal method/software release; otherwise the audited release follows the fallback archival paper.
- Hard gates: G0 novelty, G1 state/dynamics and five-arm causal confirmation, G2 cross-system method,
  G3 observation bridge, G4 held-out real data, G5 paper/release reproducibility. Do not submit NCS if
  any load-bearing gate fails.
- Current compute is two independent V100 32 GB nodes. Future capacity may expand to more GPU/CPU
  workers, but **H20 is excluded**. Use V100-equivalent GPU-hours, separate heterogeneous hardware pools,
  and never shrink seeds/horizons/baselines to fit the initial two cards.
- Full all-gates planning envelope: roughly 3,900–10,300 V100-eq GPU-hours and 9,000–30,400 CPU core-hours.
  Two V100s are enough for WP0–WP2; average 8 workers after G1 and 16-worker bursts after G3/G4 support
  the 42-week target.
- Three to five training seeds are screening only. Every stochastic headline uses at least 20 independent
  training seeds, with rollout seeds treated as nested repetitions rather than independent samples.
- Data are expandable: D0 current/free; D1 multi-exchange crypto L2; D2 US-equity L2; D3 minute panel;
  D4 event metadata; D5 external scientific benchmarks; D6 optional cross-market expansion. Purchases
  require current quotes, sample reconstruction, provenance/license review, preregistration, and the
  preceding scientific gate. Current holdings and old $8–12k quotes are not ceilings or fixed prices.
- Honest planning probability: about 7–12% joint from the current state, 20–35% conditional on all
  scientific gates passing. Fallback is TMLR/appropriate ML or microstructure venue without overclaiming.
- Zero-purchase preflight on 2026-08-09 left G0 **AMBER**: broad novelty claims are occupied by prior art.
  WP1 now has a state-complete single-process API, CPU/V100 mechanics evidence and a two-rank CPU/Gloo atomic
  exact-resume PASS; the single-V100 exact-resume and production data-cursor contract are still open. Exp128
  uses five arms because force semantics are a third defect alongside missing state
  and train/inference jump mismatch. Exp129 shows persistent detached state alone remains biased in a
  slow-mixing AR(1). Exp130 validates streaming reconstruction on 1,381,420 free LOBSTER sample events,
  not an EcoMD-to-L2 observation model. See `project_ncs_zero_cost_preflight_2026-08-09.md`.
- The 2026-08-10 continuation did not upgrade G0: exp131 passed only a known event-gradient baseline/harness
  audit, while exp132 failed its frozen easy-resolution diagnostic gate. Exp133 found and fixed missing initial
  rank-model broadcast, passed exact two-rank CPU continuation, and later passed all 12 single-V100 CUDA
  uninterrupted/resume comparisons with zero difference counts in 16.81 seconds. Production cursor,
  scheduler/scaler, W&B, multi-node NCCL and asynchronous durability remain separate gates. See
  `project_ncs_preflight_continuation_2026-08-10.md`.
- Exp134 passed a minimal correctly specified aggregate-L5 recovery test on 72 streams/2.16M events and proved
  the latent sign gauge. Exp135 passed preregistered misspecification/observation-only controls on 144 streams/
  4.32M events while exposing lag non-identifiability at `rho=0.98`. Exp136 passed a checkpointable,
  state-complete EcoMD adapter audit on eight random-weight CPU paths. Exp137 then passed all 9 frozen dynamic
  queue/price gates on 64 streams/2.56M events using the two V100 hosts as CPU-only workers: exact state and
  reconstruction, bidirectional depletion moves, queue-reactive/discrete marked-Hawkes-logit baselines,
  prospective 20% censoring, positive latent-incremental controls and negative observation-only/permutation
  controls.
- Exp138 added the previously missing external parser/sign anchor and an exact continuous-time six-mark
  queue--Hawkes likelihood on five free LOBSTER streams (2,641,557 messages). It passed generated Hawkes
  recovery, provenance, causal split/no-lookahead, training nesting, shifted-queue control and timestamp-tie
  robustness, but formally **FAILED 8/9 gates**: 19/20 combined real cells did not reach the frozen optimizer
  convergence requirement. Aligned-minus-shifted was positive for all 5 symbols under both tie policies, but
  it is diagnostic only because the fits are not converged. Any repair is a new preregistered training-only/
  generated experiment; the inspected test split cannot be reused as independent confirmation.
- G3 is not passed. The observation work still lacks a frozen EcoMD-to-external-message mapping, independently
  confirmed combined real fits, independent days/markets, an unseen real confirmation set and individual-order or
  explicitly limited aggregate semantics. Paid L2 stays gated.
- Exp139 froze the numerical repair rather than rewriting exp138: unchanged likelihood/features/splits/two
  starts, correct lower-bound projected KKT, deterministic staged refinement, generated equivalence anchors and
  real burn/training-prefix-only fits. Preregistration commits are `338e0165` and `732e1e7b`; implementation is
  `e6a7eaaf`. Both clean CPU-only shards completed after connectivity returned. The formal result is **FAIL
  (8/9 gates)**: all 120 real selected targets and all 240 starts met `1e-5`, with maximum selected KKT
  `8.91e-7` and maximum start gap `6.52e-9`; all 32 generated combined starts met `1e-7` and matched reference
  objectives within `1.79e-14`. However, two of 16 direct-Hawkes references stopped at `1.62e-8` and `2.02e-8`,
  above their stricter `1e-8` gate. This is a reference-solver boundary failure, but the frozen FAIL stands.
  Another numerical gate needs a separately preregistered solver family and fresh generated seeds; exp138's
  exposed test split remains ineligible for confirmation.
- Exp140 is preregistered at `6d3940b9` to test only that missing numerical component with 16 fresh generated
  streams, two fixed starts, an analytic-Hessian active-set Newton polish, `1e-10` KKT/complementarity gates and
  an algebraic direct/intercept-only identity check. A disclosed development prototype used only exp139's
  already exposed generated endpoints. Separate-root smoke reached maximum KKT `6.87e-12`, maximum start gap
  `2.22e-16` and objective-identity error `2.22e-16`; formal root `140202608` remains ungenerated until a clean
  implementation commit is launched. Even a PASS closes only the numerical reference sub-blocker.
