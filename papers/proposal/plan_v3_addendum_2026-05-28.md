# Plan v3 Addendum — 2026-05-28: ceiling-break escalation ladder

Supplements `plan_v3.md`. Triggered by the Batch 1 (exp 102/103) review. Establishes
a **pre-registered A→B→C escalation ladder** with binding failure definitions, so a
shortfall escalates ambition (change more / discard more) rather than sliding into a
narrative downgrade. See memory `feedback_no_downgrade`.

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
single-fact ablation gate; "add structure and hope" is not accepted. Priority by
estimated P(lift ceiling) and dual-use for Paper B physics:

- **B2 — heterogeneous-node MoE (FIRST, ~35–50%).** Per-agent soft routing over K
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
- **B-loss — adversarial / MMD objective.** WGAN-GP or RBF-MMD on multi-scale feature
  vectors (11 facts + ACF/multifractal spectra), letting the net learn what to match.
  MMD preferred over Wasserstein (exp 085 lost). Replaces hand-built surrogates entirely.

## Path C — replace the core framework (only if A and B both fail their gates)

C1 Neural SDE (learn drift+diffusion, drop the potential-symmetry constraint); C2
latent score-based generative dynamics; C3 MACE-lite v2 under the
`project_mace_lite_failure` pre-flight gates. Cost: forfeits the Langevin-potential
physical readability that Paper B's Nature Physics reviewers rely on — taken only after
A and B are exhausted by their pre-registered gates, never on a hunch.

## Binding triggers (summary)

1. A's `mf_all_mse_longroll` ≤ `baseline_v3` (Bonferroni p<0.05) ⇒ enter Path B at B2.
2. ABIDES ≤ 4/11 ⇒ Paper A reframes to paradigm-SOTA + capabilities (not a downgrade);
   ABIDES ≥ 9/11 ⇒ jump to Path C.
3. Any winning cell promotes to 5-asset n=30 (exp 106) before a paper claim — no
   best-of-N, per `feedback_seed_count_lottery` and `feedback_preregistration`.
