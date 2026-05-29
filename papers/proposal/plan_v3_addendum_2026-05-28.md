# Plan v3 Addendum — 2026-05-28: ceiling-break escalation ladder

Supplements `plan_v3.md`. Triggered by the Batch 1 (exp 102/103) review. Establishes
a **pre-registered A→B→C escalation ladder** with binding failure definitions, so a
shortfall escalates ambition (change more / discard more) rather than sliding into a
narrative downgrade. See memory `feedback_no_downgrade`.

## STATUS 2026-05-29 — Path A FALSIFIED, now executing Path B0 (MMD = exp 104)

Path A (exp 107, per-fact surrogates with rollout-reg=512) **failed its
pre-registered gate**: `mf_all_mse_longroll` Δ=+0.13 vs baseline_v3, **p=0.81**
(surrogates verified live this time — a fair null). Per trigger #1 we escalate to
Path B, starting at **B0 = exp 104 MMD long-rollout** (built 2026-05-29):
- MMD wired into the rollout-reg path only (losses.py skips the distribution term
  when `target_returns is None`; `target_returns_map` threaded into
  `_compute_rollout_reg_loss`). MMD fires on 512 returns, never the ~7-return main loop.
- **w_mmd swept {20,50,100}** — calibration showed raw MMD ≈0.012 vs structural ≈1.16,
  so `w_mmd=1` would be negligible (an invalid test, the surrogate trap in a new guise).
- **N=10K, fp32** (NOT 107's N=2000+bf16, which destabilised agg-gaussianity: baseline
  rejects 2/30→8/30). rollout-reg is truncated BPTT so N=10K is free on memory.
- 150 cfg, launcher `scripts/h20_104_mmd_2026-05-29.sh --probe` (timing+stability gate).
- Binding: if NO `w_mmd` cell beats `hybrid_nomm_longroll` (Bonferroni p<0.05/3) AND none
  exceeds `baseline_v3` → distribution-matching falsified across a 5× weight range → **B2 (MoE)**.

ABIDES (exp 105) = **2–3/11** on all 5 RMSC03 variants → the ≤4/11 "paradigm-SOTA"
branch of the decision tree below is in play, but PENDING a timescale-fair re-run
(ABIDES ran intraday 60s/390-bar, scored on daily bands; `volume_vol_corr=1.0` is an
extraction artifact). Do not put the ABIDES comparison in the paper until re-run fairly.

## What the 5-28 review actually found

The exp-102 "negative result" (0/14 cells beat baseline at the Bonferroni gate) was
**not a fair test** of the objective-coverage hypothesis:

- The training rollout feeds only ~7 returns (`chunk_steps=24`, `warmup_steps=16`,
  `sim_returns = traj.log_returns[1+warmup:]`).
- Surrogate length guards then fire: `soft_fano` returns a constant for n<50,
  `dfa_hurst_surrogate` for n<~200, `agg_gaussianity` degrades to a k1-only signal
  for n<400. So `mf_fano`/`mf_dfa` were **bit-identical to baseline** (zero gradient,
  confirmed 30/30 seeds, `scripts/diagnose_surrogate_coverage.py`) and `mf_agg`
  optimised the wrong quantity. Only `gain_loss_skew` was live.
- Where surrogates *were* active they moved the target fact toward its band **with
  zero collateral** (no in-band fact left its band) — weak positive signal, not a
  refutation.

103: ISAB pairwise is dead (2.2–3.1/11); `inner_steps>1`/`agent_memory` blow up
`aggregational_gaussianity` on ~40–50% of seeds (a real dynamical instability, not
noise); the apparent 5.41 winner (`agentmem_inner4`) is survivorship bias (13/30
rejected). No promotion justified.

**Verdict: objective-coverage is untested, not falsified.** Path A tests it properly.

## Path A — first fair test of objective-coverage (exp 107, running 2026-05-28)

`experiments/107_multifact_longroll_n30/`. Configuration-only fix (no `ecomd/`
change): enable the existing rollout-reg path (`_compute_rollout_reg_loss`, 057) at
`rollout_reg_steps=512`, so the surrogate loss is computed on a 512-return truncated-
BPTT rollout where all four surrogates are live, while peak memory stays at one chunk
(respects `project_chunk_oom_constraint`). N dropped 10K→2000 + bf16 for budget.
Verified on Mac (N=500): all 4 surrogates `grad_fn=LIVE`, gradient reaches params.

Deconfounded 3-cell ladder (SPX, n=30): `baseline_v3` (new-N control, no reg) →
`longroll_moments` (reg on, moments only: isolates long-rollout-alone) →
`mf_all_mse_longroll` (reg on + 4 surrogates: full test).

**PRE-REGISTERED FAILURE (binding):** if `mf_all_mse_longroll` does **not** beat
`baseline_v3` at Bonferroni p<0.05 (2 comparisons) on the SPX 11-fact mean →
objective-coverage is **formally falsified** → trigger Path B. If it beats the gate →
promote to the 5-asset n=30 confirmation (exp 106) before any paper claim.

## Ceiling-attribution probe — ABIDES (exp 105, parallel to A)

`experiments/105_abides_ceiling/`. Score ABIDES (rmsc04 variants) with the SAME
11-fact evaluator + daily bands. Sets the Paper A narrative independent of A's result:

| ABIDES 11-fact score | Reading | Paper A narrative |
|---|---|---|
| ≤ 4/11 | 11/11 unreachable for the paradigm | **paradigm-SOTA** + EcoMD-only capabilities (differentiable, fluctuation theorems, multi-asset). *Upgrade, not downgrade.* |
| 6–7/11 | we lag a known sim | concrete fact-level gap → Path B targets it |
| ≥ 9/11 | framework is the bottleneck | trigger Path C |

## Path B — discard the moment-matching framing (if A fails)

Pre-registered candidates, each **bound to specific failing facts** with a stability +
single-fact ablation gate; "add structure and hope" is not accepted. Order:

- **B0 — MMD with long rollout = exp 104 (FIRST Path B move).** The distribution-distance
  loss families (`mmd_gaussian_multi_bandwidth`, `wasserstein_multi_scale`, sinkhorn) are
  **already implemented in `losses.py`** but unwired in `train_distributed.py` (both
  `compute_loss` calls pass `target_returns=None`, so MMD/W raise). The prior negative
  (exp 085 Wasserstein, 4.46 < baseline) is **suspect — same rollout-length trap as 102**:
  085 ran at chunk_steps=24 (~7 sim returns), so the distribution distance was estimated on
  ~7 samples. MMD on multi-scale windows deserves a FAIR re-test. Work needed (small): thread
  the real-returns tensor as `target_returns` into the main + rollout-reg `compute_loss` calls,
  then run `loss_family=mmd` (or hybrid moments+mmd) with `rollout_reg_steps≥512`. Cheapest
  Path B move and re-tests a likely-invalid negative — do it before the heavier MoE.
  See [[project_surrogate_rolloutlen_trap]].
- **B2 — heterogeneous-node MoE (~35–50%).** Per-agent soft routing over K
  expert drift/diffusion strategies + load-balancing reg; information-asymmetry channel
  (Kyle/Glosten-Milgrom prior). Targets `intermittency_fano`, tails. Dual-use: hetero
  agents are a non-equilibrium-steady-state source → feeds Paper B entropy-production /
  T_eff (C2). Watch: expert collapse; OOM × long-rollout budget.
- **B1 — mechanism-bound big-system modules (~55–65%, conditional).** Independent volume
  channel → `volume_volatility_corr`; sign-aware fear/greed drag → `leverage_effect` +
  `zumbach_asymmetry`; multi-frequency layer → `aggregational_gaussianity` + DFA. Each
  module ships with a stability test (103 showed added modules destabilise).
- **B3 — leader-follower dynamic graph ONLY (~20–30%).** Explicit price-leader subset →
  lead-lag autocorr. Other dyngraph variants are excluded (ISAB 2.2/11; k-NN-biased
  MACE-lite). Must pass `project_mace_lite_failure` pre-flight gates first.
- **B-loss — adversarial / feature-space objective.** Distinct from B0 (which is MMD on the
  return samples): here a WGAN-GP discriminator or RBF-MMD on multi-scale **feature vectors**
  (11 facts + ACF/multifractal spectra) lets the net learn what to match. Run only if B0's
  raw-return MMD is also insufficient. Replaces hand-built surrogates entirely.

## Path C — replace the core framework (only if A and B both fail their gates)

C1 Neural SDE (learn drift+diffusion, drop the potential-symmetry constraint); C2
latent score-based generative dynamics; C3 MACE-lite v2 under the
`project_mace_lite_failure` pre-flight gates. Cost: forfeits the Langevin-potential
physical readability that Paper B's Nature Physics reviewers rely on — taken only after
A and B are exhausted by their pre-registered gates, never on a hunch.

## Binding triggers (summary)

1. A's `mf_all_mse_longroll` ≤ `baseline_v3` (Bonferroni p<0.05) ⇒ enter Path B at **B0**
   (exp 104 = MMD long-rollout re-test; cheapest + re-tests the suspect 085 negative), then
   B2 (MoE) if B0 also misses. Exp 104 stays reserved for this — its trigger is "107 fails".
2. ABIDES ≤ 4/11 ⇒ Paper A reframes to paradigm-SOTA + capabilities (not a downgrade);
   ABIDES ≥ 9/11 ⇒ jump to Path C.
3. Any winning cell promotes to 5-asset n=30 (exp 106) before a paper claim — no
   best-of-N, per `feedback_seed_count_lottery` and `feedback_preregistration`.
