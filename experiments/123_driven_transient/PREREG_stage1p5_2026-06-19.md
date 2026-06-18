# Pre-registration — exp 123 Stage 1.5: sub-threshold dose sweep (frozen 2026-06-19)

Amends `PREREG_2026-06-18.md` after Stage-1 landed **P\*** (spx): revival ✓ (α_ED 4.75→0.5),
transient ✓, =burn-in ✓, but the dip **saturates** at the floor for mag ≥ 3 (0.51/0.49/0.58, not
dose-monotone). Stage 1.5 maps the dose-response **below** saturation to complete H2.

## Frozen spec

Identical to Stage-1 except the dose grid (reuse the spx concave_d050 checkpoint, control + the
mag 3/6/12 arms already run):

| param | value |
|---|---|
| asset | **spx** (decision); checkpoint = 113 concave_d050 seed0 (reuse) |
| new arms | state_kick **mag ∈ {0.3, 0.5, 1, 2}** (frac=0.10) → `kick0.3 kick0.5 kick1 kick2` |
| combined dose axis | {0.3, 0.5, 1, 2, 3, 6, 12} (with Stage-1) + control |
| seeds | n = 32/arm (NPROC×N_REAL); SEED_BASE 10000 (pairs with control) |
| rollout / shock / windows | n_steps=8000, T_shock=3000, W=500 stride=100 k_frac=0.1 (unchanged) |

## Pre-registered hypotheses (frozen before the run)

- **H2a (onset/dose-response).** Post-shock min α_ED is a **monotone non-increasing** function of dose
  across {0.3 … 12}: small kicks leave α_ED near the control value (≈4.7, no revival), and α_ED falls
  to the ~0.5 floor as dose increases. PASS iff the post-shock-min(dose) curve is monotone non-increasing
  AND spans from ≥3 (smallest dose, near-light) to ≤2 (large dose, revived).
- **H2b (threshold).** There exists a threshold mag\* where revival onsets (post-shock min crosses 2).
  Report mag\* (interpolated). Descriptive, not pass/fail.
- **H3/H4 unchanged** — every revived arm must still recover (H3) and match the burn-in template (H4).

## Decision

- **H2a PASS** (clean monotone dose-response below the floor) → **H2 fully satisfied → spx = P** (was P\*);
  the positive frontier paper's dose-response leg is earned. Proceed to Stage 2 (channels, multi-asset, τ).
- **Even the smallest dose (0.3) saturates** (post-shock min ≤2 at mag=0.3) → the response is a **step
  function / hard threshold**, not graded. Report it honestly as a threshold phenomenon (still physics:
  any supra-threshold drive triggers the same relaxation transient); note the dose-response is degenerate.
- **No arm below mag=3 revives** and the curve is flat-light then jumps → consistent with H2b threshold
  between the tested points; refine the grid around the jump.

Discipline ([[feedback_preregistration]], [[feedback_no_downgrade]]): grid + thresholds frozen here;
report the dose-response curve as measured, no post-hoc relabeling.
