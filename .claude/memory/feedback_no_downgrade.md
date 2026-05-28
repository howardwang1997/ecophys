---
name: feedback-no-downgrade
description: "User rejects narrative downgrade on negative results; escalate ambition (change more / discard more) via a pre-registered A→B→C ladder"
metadata:
  type: feedback
---

When an experiment falls short (e.g. ceiling not broken, hypothesis unsupported), the user does **not** accept retreating to a lower-ambition framing — e.g. "pivot Paper A to the capabilities-baselines-can't-do story" is treated as a downgrade and rejected. Instead: if a small/tuning fix can't deliver, **change bigger things and discard bigger things** (drop default constraints like N=10K, swap the loss family, replace the core framework), each gated by a pre-registered failure definition so it can't silently slide into a weaker claim.

**Why:** User explicit instruction 2026-05-28 (Batch 1 102/103 review). They want maximum-ambition pursuit of the actual target (break the 5/11 ceiling, top venue), not graceful retreat. A "negative result" must first be checked for being an invalid test (see the surrogate-rollout-length trap that turned the 102 null into a non-test) before it's allowed to lower ambition.

**How to apply:**
- After any negative/underwhelming result, default to proposing an *upgrade* path, not a narrative softening. Present an escalation ladder with binding triggers: A (proper test of current idea) → B (discard the framing: adversarial/MMD, heterogeneous-node MoE, big-system modules) → C (replace core framework: Neural SDE / score-based).
- "Shift the optimization target" only counts as non-downgrade if data justifies it as a *harder* claim (e.g. ABIDES ceiling probe shows 11/11 is unreachable for the paradigm → reframe as paradigm-SOTA + physics rigor). Tie it to a measurement, not to convenience.
- Each architectural escalation must bind to specific failing facts + carry a stability/ablation gate — not "add structure and hope".

**See also:** [[feedback-critical-thinking]] (honest pushback still applies — escalating ambition is not the same as overclaiming; say when something genuinely failed), [[feedback-h20-day-budget]], [[project_surrogate_rolloutlen_trap]].
