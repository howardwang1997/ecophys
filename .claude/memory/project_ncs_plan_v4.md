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
  WP1 now has a state-complete single-process API and CPU/V100 mechanics evidence, but atomic DDP resume
  is still open. Exp128 uses five arms because force semantics are a third defect alongside missing state
  and train/inference jump mismatch. Exp129 shows persistent detached state alone remains biased in a
  slow-mixing AR(1). Exp130 validates streaming reconstruction on 1,381,420 free LOBSTER sample events,
  not an EcoMD-to-L2 observation model. See `project_ncs_zero_cost_preflight_2026-08-09.md`.
