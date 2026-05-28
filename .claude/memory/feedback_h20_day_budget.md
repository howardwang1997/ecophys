---
name: feedback-h20-day-budget
description: "When an H20 run-day is available, use it — do quick Mac experiments first, then push to H20; don't defer to 'design only'"
metadata:
  type: feedback
---

When the user says an H20 run-day is available, the expectation is that the day's H20 capacity gets **used**, not left idle while we only write designs. The cadence the user wants: **(1) run the relatively-quick experiments on Mac first** (smoke / pre-flight / pipeline checks), **(2) then push to H20** for the heavy overnight run. A plan that says "produce generators + design docs, don't run on H20 today" is too conservative when a run-day is on the table.

**Why:** User explicit instruction 2026-05-28. H20 capacity is the scarce resource; an unused run-day is wasted. But a wasted *run-day-of-compute* on a broken config is worse — hence the Mac-first pre-flight gate.

**How to apply:**
- Default flow on an available H20 day: Mac AM (diagnostic + PRE-FLIGHT smoke that must pass 3 conditions: no OOM, gradients live, no numerical blowup) → commit/push → hand back SSH launch sequence → overnight run → next-morning pull + scored gate.
- The Mac smoke is the bug-firewall: never push a config to a multi-hour H20 run without a tiny N=500 smoke confirming it trains and doesn't OOM/explode (ties to [[project_mace_lite_failure]] pre-flight-gate discipline and [[project_chunk_oom_constraint]]).
- H20 is not reachable from the Claude session — produce runnable scripts + exact SSH commands for the user to execute. See [[feedback-workflow]].

**See also:** [[feedback-smoke-test-autonomous]], [[feedback-workflow]], [[feedback-no-downgrade]].
