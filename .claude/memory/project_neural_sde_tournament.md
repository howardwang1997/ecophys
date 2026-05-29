---
name: neural-sde-tournament-beyond-framework
description: "2026-05-29 program pivot: after Path A falsified + ABIDES 2-3/11 (paradigm-level ceiling), go BEYOND the Langevin framework via a tournament of new architectures, seeded by a scout. Hero = learned stochastic-vol / Neural-SDE diffusion."
metadata:
  type: project
---

**Why (2026-05-29):** Path A (per-fact surrogates, exp 107) was falsified (p=0.81) and
ABIDES — a different paradigm — scores only 2-3/11, so the ~5.1 ceiling is **paradigm-level,
not architecture-level**. The failing facts are ALL volatility-structure facts (fat tails #2,
agg-gaussianity #4, Fano #5, DFA long-memory #8). The simulator's volatility was fixed,
hand-designed, and **detached** (zero gradient). User directive: pursue the best result
**beyond the current architecture/framework**.

**Strategy (user choices):** a **tournament** of beyond-framework entrants on a 60h weekend,
seeded by a **5-6h scout** (exp 108). See plan `pull-adaptive-thacker.md` + addendum.

**Hero entrant = Neural-SDE stochastic-volatility head (BUILT + smoke-gated 2026-05-29):**
- `ecomd/models/stoch_vol.py` `StochVolProcess`: K-component mean-reverting **log-OU** latent.
  Multi-timescale (distinct kappa_k → DFA #8 / agg-gauss #4), stochastic innovation (tails #2 /
  Fano #5), asymmetric `relu(-r)` leverage coupling (#9/#11). `sigma_eff = sigma_price *
  exp(g·softmax(a)·v)`. Positivity (exp) + hard bound (tanh clamp) → no agg-gauss blow-up.
- Two placements, flag-gated: **price-level** (`price_formation_kwargs.sv_price_enabled`,
  primary — modulates the return scale) and **integrator-level** (`sv_integrator_enabled`,
  scales the Langevin noise → multiplicative-noise overdamped Langevin = Paper-B physics).
- **Key plumbing fact:** the vol latent rides in `PriceState` (the ONLY carrier surviving both
  the MMD/rollout-reg path and the custom-autograd packer). It is threaded through
  `EcoMDStepFunction` (has_vol flag, like h_global) and **must be detached in
  `train._detach_price`** — else the 512-step rollout-reg carries an O(512) graph → OOM/blow-up.
  Grouped-checkpoint path (bptt_checkpoint_every>0) raises (drops vol_latent); use 0.
- OFF (sv_price_enabled=False) = bit-exact prior behaviour (module not built, no extra RNG draw).
- **Build gate PASSED:** `tests/test_stoch_vol.py` (11 tests) + full suite 370 passed; N=500
  inference smoke: liveness (5/5 sv params get grad through custom-fn), loss 1.34→0.95,
  finite, **agg_gauss=411 (<1000), hill=4.20, DFA=0.800 in-band** — early vol-structure signal
  (NOT a result: n=1, N=500).

**Scout = exp 108** (`experiments/108_neural_sde_scout/`, launcher `h20_108_neural_sde_scout.sh
--probe`): 60 cfg = 5 cells × 12 seeds, SPX, N=10K fp32, reg_every=8 (~5h). Cells: baseline_mmd /
sv_d1 / sv_d3 / sv_d3_nolev / sv_d3_both. **Pre-registered scout gate (binds the weekend):** a
cell advances iff it lifts ≥1 hard floor (#2/#4/#5/#8) w/o ≥20pp collateral AND mean n/11 ≥
baseline_mmd. Attribution: d3−d1 = multi-timescale; d3−d3_nolev = leverage; both−d3 = placement.

**Not yet built (weekend Phase-0 stretch):** A2 heterogeneous-node MoE; A3 score/diffusion
return model (as a `ecomd/baselines/` fit/sample baseline for the deep-generative ceiling); the
ABIDES timescale-fair re-run (owed; intraday-scored-on-daily-bands + volume_vol_corr=1.0 artifact).

**Weekend (60h):** Bracket 1 SOLVE — surviving entrants at N=10K n=30 SPX+NDX + winner ablations;
Bracket 2 DIAGNOSE — three-paradigm ceiling map (TrajCast/WGAN/GARCH/AR1-SV/Lux-Marchesi/diffusion
+ ABIDES). Champion → 5-asset n=30 confirmation the FOLLOWING weekend (no claim off the tournament).

See [[project_paper_a_neurips_2027]], [[project_pareto_ceiling]],
[[project_surrogate_rolloutlen_trap]], [[project_chunk_oom_constraint]], [[feedback_no_downgrade]].
