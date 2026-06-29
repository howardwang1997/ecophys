---
name: project_light_tail_rootcause
description: Root cause of EcoMD's light steady-state tail (CLT self-averaging) is FUNDAMENTAL, not a bug — reframe it as the positive mechanism; exp 125 ablations
metadata:
  type: project
---

**2026-06-29 root-cause verdict (user asked: why the negatives? fixable? fundamental?).** EcoMD's
**light steady-state tail (Hill α_ED≈4.7, not cube-law) is FUNDAMENTAL**, from three first-principles
reasons: (P1) Boltzmann light tail of a smooth confining learned potential (power law needs U∼log|s|);
(P2) **CLT self-averaging** — ED=κΣΔs over N≈10⁴ finite-variance, short-correlation agents → Gaussian
aggregate → light, *stronger pull as N grows* (the dominant effect); (P3) sub-critical coupling (exp
116/120 smooth crossover, no N_c). Heavy tail is a **driven transient** because a shock imposes
system-spanning coordination transiently; CLT reasserts on relaxation. **This is the mechanism, not a
failure** — the central reframe: lead with *EcoMD-the-laboratory + the interventional mechanism of fat
tails* (we can switch the heavy tail on/off, which observation of real markets cannot).

**Solvability:** (A) heavy micro-noise (Lévy/Student-t — **in code & runnable**: `noise_dist∈{normal,t,
levy}`, `noise_levy_alpha`, CMS sampler) CAN install a stationary heavy tail but the index is hand-set
and trades off volatility clustering = the **Pareto cost**; (B) SV/multiplicative — explored, hit the
ceiling (exp 119 4.90; MoE/diffusion); (C) criticality — explored, no sharp N_c. ⇒ N1 is "fixable only
by changing the model class, at the cost of the temporal facts" = the Pareto-frontier finding itself.

**Negatives handling (user directive — fix-or-deemphasize, don't headline; honors [[feedback_no_downgrade]]):**
N1 light tail → reframe as the positive CLT mechanism; N2 (real return tails stationary, z=+1.03) is a
**DATA fact** (real markets carry the always-on heavy source EcoMD lacks), the *predicted boundary* →
demote to a one-paragraph scope note + order-flow handoff; N3 EP-flat → one sentence (Paper-B carve-out);
N4 Pareto ceiling → present as a positive structural result.

**exp 125** (`experiments/125_rootcause_controllability/`, binding PREREG, no data buy, reuses
concave_d050 ckpts): G-A rigor n=30 CIs; G-B controllability atlas (new non-mechanical channels
`temperature_spike`/`liquidity_drop` — rebut "state_kick is mechanical", GenAI lead); G-C τ(dose) law
(ML4PS); **G-D root-cause ablations = the new core** (D1 heavy-noise→stationary tail? cost to clustering;
**D2 steady α_ED vs N at FIXED trained dynamics = the clean CLT self-averaging proof** exp 120's
train-at-N confounded); G-E 2nd-generator pitfall. Driver `scripts/gpu_exp125_atlas.sh` (worker/ablate/
eval/fanout). PREREG pre-commits every arm to positive content either way (anti-gate-shopping guardrail).
Doc: `papers/proposal/paper_a_rootcause_and_reframe_2026-06-29.md`. See [[project_burnin_artifact]],
[[project_pareto_ceiling]], [[project_neural_sde_tournament]].
