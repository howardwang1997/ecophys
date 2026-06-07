---
name: project-paper-b-gates
description: "Paper B (Nature Physics) 2026-06-07 claim review: M3 gate contradiction must be resolved in plan v3.1 BEFORE arXiv pre-registration; S8 verdict = B2 raw Jarzynski infeasible at realistic event budgets; $8-12k purchase gated on three checks; B3 reframed as measurement"
metadata: 
  node_type: memory
  type: project
  originSessionId: f3a85399-5c6f-453a-9576-26ce31fbcae4
---

**2026-06-07 reviewer-2 claim review of Paper B (NP flagship) — standing decisions:**

1. **M3 gate contradiction (unresolved, blocking)**: plan v3 M3 gate says "≥9/11 on ≥2 markets,
   ≤7/11 → abandon NP" — but Paper A proved ~5–6/11 is a paradigm-level ceiling (NO paradigm
   reaches 9/11). By pre-registered logic NP is already triggered OFF. Must be resolved in
   **plan v3.1 BEFORE the arXiv pre-registration**: either (a) accept → §7.2 retreat (2×PRL+QF),
   or (b) rewrite as dynamics-sector fidelity gate (defensible post-113: the physics observables
   depend on clustering/long-memory/leverage/zumbach + tails, which EcoMD now hits). Revising an
   internal gate before any Paper B experiment ran is legitimate; after = cheating.

2. **S8 verdict (run 2026-06-07, `scripts/s8_jarzynski_power.py`): B2-as-written is
   statistically infeasible.** At the realistic event budget (FOMC≈24, earnings≈240), the raw
   Jarzynski estimator ΔF̂=−(1/β)ln⟨e^(−βW)⟩ meets B2's 15% criterion only for near-Gaussian W
   with βσ_W ≲ 1; truncated-t df=3, crash-mixture, and GARCH-t aggregate W all give ZERO power
   cells (GARCH reference non-convergent even at 1e7 draws). Analytic: polynomial left tail ⇒
   E[e^(−βW)]=∞. B2 must be redesigned (block-averaged protocol / small-work-sector integral FT)
   or demoted; A1 then needs a replacement validation leg (toy-model ΔF recovery + B3 cross).

3. **Purchase gating (user decision 2026-06-07)**: $8–12k high-freq buy only after ① weekend
   115/116 readouts, ② plan v3.1 resolves the gate contradiction, ③ S8 — already returned NO
   for B2-as-written. If NP demoted → shrink buy to PRL needs (Tardis-first).

4. **Claim probability updates (mine vs plan v3)**: A1 25–40% (LPPL minefield: t_c must be FIXED
   at pre-registered event times, never fitted; ±0.05 → CI-overlap + Cochran's Q), B2 30–45%
   pre-S8 / near-0 as-written post-S8, A2 20–30%, **B3 ~80% if reframed from "TUR saturation"
   to "first measurement of the TUR ratio Q in markets"** (any Q publishable, zero literature).
   NP joint today ~8–15% (plan said 15–22%); was always the 78–85%-fail moonshot with paid-for
   retreats.

5. **C2 pipeline status**: only `ecomd/eval/entropy_production.py` exists; T_eff extractor,
   Jarzynski W path-integral, TUR estimators, shared-θ multi-market, N=5×10⁵ tensor-parallel
   all unbuilt.

**How to apply**: any Paper B discussion starts from the three-gate state (① pending weekend,
② pending v3.1, ③ DONE=NO for raw B2). Do not let pre-registration proceed until the M3 gate
contradiction is resolved in writing. Work on branch `feature/paper-b-s8-jarzynski`.
Related: [[paper-a-target-neurips-2027-problem-diagnose-solve-framing]], [[project-h20-fleet-scheduling]].
