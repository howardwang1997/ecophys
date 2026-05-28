---
name: surrogate-rollout-length-trap
description: "Per-fact surrogates (fano/dfa/agg) silently die or degrade when the training rollout is shorter than their estimator needs — the trap that made exp 102 a non-test"
metadata:
  type: project
---

**The trap (diagnosed 2026-05-28, exp 102 review):** the multi-fact differentiable
surrogates in `ecomd/training/fact_surrogates.py` have length guards that return a
**constant (zero-gradient)** or a **degraded signal** when called on too few returns.
The main training loss sees only `chunk_steps - warmup ≈ 7` returns
(`train_distributed.py:490-493`, `start = 1 + warmup_steps`), so:

- `soft_fano` (`fact_surrogates.py:111-113`): n < `n_windows` (50) → `return torch.ones(())` → DEAD.
- `dfa_hurst_surrogate` (`:147-149`): `0.1·n ≤ min_scale` (16), i.e. n ≤ ~200 → `torch.zeros(())` → DEAD.
- `agg_gaussianity` (`:81-82`): < 8 aggregation blocks (n < 8·scale_large = 400) → returns k1 only (raw
  small-scale kurtosis), the WRONG target — actively harmful (mf_agg fell to 4.33).
- `gain_loss_skew`: works at any n → the only cleanly-active surrogate.

Empirical liveness (verified, `scripts/diagnose_surrogate_coverage.py` part (c)): all 4 live only
at **n ≥ 400**. Symptom that exposed it: `mf_fano`/`mf_dfa` were **bit-identical to baseline_v3**
across all 30 seeds (max-abs-diff = 0) — three different cells, same seed, identical 11-fact output.

**Why it matters:** exp 102's null result was an *invalid test* of the objective-coverage
hypothesis, not a refutation. 3 of 4 surrogates contributed no usable gradient.

**How to apply / fix:**
- Any experiment putting fano/dfa/agg in the loss MUST feed the surrogate a rollout ≥ 400 returns.
- The fix is config-only, no `ecomd/` change: enable the existing rollout-reg path
  (`_compute_rollout_reg_loss`, "057") with `rollout_reg_steps ≥ 512`. It computes the SF loss on a
  multi-chunk truncated-BPTT rollout, peak memory ≈ one chunk — so it does NOT trip
  [[project_chunk_oom_constraint]] (do NOT instead crank `chunk_steps`, which OOMs). Exp 107 does this.
- Before trusting any surrogate-loss experiment, run `diagnose_surrogate_coverage.py` on it: if a
  `mf_*` cell is bit-identical to baseline, its surrogate was dead.
- General lesson: a differentiable surrogate that passes its rank-correlation kill-test (ρ>0.6 on
  random inputs) can STILL be dead in training if its minimum-sample guard exceeds the rollout length.

**See also:** [[project_chunk_oom_constraint]] (why we use rollout-reg not long chunks),
[[project_mace_lite_failure]] (pre-flight-gate discipline), [[feedback_no_downgrade]] (this turned a
"negative result" into a recoverable non-test before any narrative downgrade).
