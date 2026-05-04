---
name: AR(1) drift artifact in p_4_2__2_1 returns (2026-05-04)
description: Trained EcoMD returns are essentially AR(1) with rho_hat=0.904 (median 0.935), not random walk. autocorr_returns fails 95% of the time pre-whitening, passes 94% post AR(1)-whitening. Likely inflates acf_squared and Hurst pass rates by drift artifact.
type: project
originSessionId: 6929e7db-e7e9-4079-9f5e-564e7b32f7b4
---
**As of 2026-05-04, after 50-seed deep-dive on `p_4_2__2_1`:**

The simulator's log_returns are not a random walk. They are AR(1) with mean
ρ̂ = **0.904**, median 0.935, range [0.45, 0.99] across 200 realizations
(50 seeds × 4 reps). The autocorr structure is ~85% pure AR(1) decay ρ^k
with a small slow-memory component (+0.07 excess at lag 20).

**Why it's NOT a learned T-suppression cheat:**
All 50 064 checkpoints kept their thermodynamic params at init (T_eff≈0.052
vs init 0.05; γ_eff≈0.98 vs init 1.0). Per-step noise std ≈ 0.0324, init
0.0316 — basically unchanged. See `experiments/067_ar1_diagnostics/thermo_params.md`.

**Likely structural cause:**
- `dt=0.01, gamma_init=1.0` → per-step relaxation γ·dt = 0.01.
- Velocity memory time = 1/(γ·dt) = 100 steps → deeply underdamped.
- Force field f_θ(s) is smooth in s-space → drift correlated step-to-step.
- `w_autocorr_r=0.5` loss term too weak; chunk_steps=24 statistical noise
  ~0.21 swamps gradient signal.

**Implications for paper claims:**
1. `autocorr_returns` 4–5% pass rate is honest, but 94% pass rate AFTER
   AR(1) whitening — the failure is curable by trivial whitening.
2. `acf_squared_returns` ~0.40 mean has baseline ρ²=0.36 contribution from
   AR(1) drift. True vol clustering after whitening likely <0.10 → FAIL
   lower band 0.15. (Empirical confirmation pending E3b.)
3. `dfa_hurst_abs_r` consistently > 1.0 — physically impossible for stationary
   process — smoking gun for "smooth drift not fluctuating series".
4. **True architectural pass count likely ~3/11, not 5/11.** The 5/11 includes
   2 facts that are AR(1) artifacts.

**How to apply:**
- ANY paper draft must report a "post AR(1)-whitening" companion column
  alongside the raw 11-fact pass count. Reviewer-2 will demand this.
- For new architectures, autocorr_returns is the **first** fact to check —
  if ac_r > 0.20 the rest of the analysis is contaminated.
- Don't celebrate "vol clustering passes" without checking ρ̂; for ρ > 0.3
  most of the acf_sq² signal is drift.
- Architecture fix priorities: increase γ·dt to ≥1 (overdamped), add force-noise
  injection, raise w_autocorr_r to 5+, use longer-horizon ACF estimator
  (the 057 rollout_reg horizon=120-240 already shows partial improvement).

**Diagnostic scripts (branch `diagnostics/autocorr-ar1`):**
- `scripts/diagnose_thermo_postrain.py` — extract T_eff, γ_eff from ckpts
- `scripts/diagnose_ar1_residual_acf.py` — analytical AR(1) on stored ACF
- `scripts/diagnose_ar1_residual_full_from_traj.py` — full re-eval on saved traj
- `scripts/h20_e1_freeze_thermo.sh` — train with frozen (T,γ) at 4 cells (24 cfgs)
- `scripts/h20_e3b_save_trajectories.sh` — re-run 064 inference saving raw returns

**Outliers worth understanding:** seeds 74 and 82 in 064 hit ρ̂ ≈ 0.47 (vs
population 0.9) and DO pass autocorr_returns. Both scored mid (5/11). They
may have stumbled into a different basin of the loss landscape.
