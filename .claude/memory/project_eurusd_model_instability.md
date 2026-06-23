---
name: project-eurusd-model-instability
description: "exp-123 eurusd EcoMD checkpoint is seed-unstable: equilibrated geometry varies ~50x across training seeds, |rho| kick response 0.07 (production) vs 0.6 (fresh, same ckpt) -> treat eurusd order-flow readouts as unreliable; the tail revival (kick12) is the one real eurusd result"
metadata:
  type: project
---

**Finding (2026-06-24, diagnosed on the 8-card H20 with the exact exp-123 eurusd checkpoint
`experiments/114_concave_confirm/results_eurusd_concave_d050_seed0/checkpoint.pt`).**

eurusd's order-flow imbalance |ρ| coordination spike is anomalously weak and **not reproducible**:
- **Production (committed) exp-123 data:** at the coordinated kick, |ρ| peak = spx 0.70 / ndx 0.66 /
  gold 0.68 / btc 0.68 (tight across rollouts) but **eurusd only 0.069 (kick6), 0.115 (kick12)** —
  robust across 58 eurusd trajectories.
- **NOT smoothing** (raw 0.069 ≈ 9-smoothed 0.045; lightened `rho_abs` smoothing 9→3, barely moved).
- **NOT config** (eurusd vs spx configs identical except `target_dataset`), **NOT within-step damping**
  (kick survives ~80–95% of intended net flow in both assets; shock is applied pre-force at `ecomd.py:790`).
- **It is eurusd model instability:** the SAME checkpoint gives |ρ| = **0.61 in a fresh rollout** vs
  **0.069 in production** (only the rollout RNG seed / equilibration trajectory differs). Across
  checkpoint seeds the equilibrated **gross flow varies ~50×** (seed0 net=108 vs seed1 net=8833;
  |ρ| 0.61–0.99). spx is tight everywhere; **eurusd's trained dynamics are seed-unstable / metastable.**
- Caveat: my diagnostic ρ (outer-step Δstate) may also not exactly equal the model's internal `ofi`
  (possible inner-step mismatch) — another reason eurusd's |ρ| is not a clean readout.

**How to apply.**
- For the **order-flow signature** (|ρ| / memory burst, Fig 4), report it as a **robust four-asset
  result** (spx/ndx/gold/btc, |ρ| ≈0.66–0.70); **exclude eurusd's |ρ|** as anomalous/seed-unstable — do
  NOT call it "FX sub-threshold" (implies more dose fixes it; it does not). Done in NCS/ML4PS/GenAI drafts
  (commit b4fa169e6).
- The eurusd **tail** revival at kick12 IS real (verdict P at mag12) — "sub-threshold FX, tracks intrinsic
  volatility" stays correct for the *tail* dose-response only.
- More broadly: be wary of any eurusd-specific EcoMD result; re-check it against spx/the other 4 before
  trusting it. Related: [[project_burnin_artifact]] (sim-only transient), the exp-123 trajectories live on
  GPFS at `/AI4S/Users/howardwang/h204/ecophys/` (see [[project-h20-fleet-scheduling]]).
