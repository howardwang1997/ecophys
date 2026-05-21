---
name: feedback-smoke-test-autonomous
description: "Run smoke tests autonomously — no permission asks, fail-loop up to 3 rounds before escalating"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d8f75917-cbc6-43cc-814b-11508430a13a
---

When implementing new code that requires a smoke test (training-loop change, model architecture refactor, integration of a new module into the rollout pipeline), **run the smoke test without asking for permission**. If the smoke fails:

1. Print the error and diagnose.
2. Apply a fix and re-run.
3. Repeat up to **3 rounds** total within the same session, autonomously.
4. Only after 3 failed rounds, escalate to the user with a summary and ask for guidance.

**Why:** User explicit instruction 2026-05-22 — they want continuous execution during smoke-test debugging so they can review final state at end of session, not interrupt every loop. The user is willing to accept 3 wasted iterations on a smoke as the cost of not being interrupted. Save power user mode for when implementation is non-trivial.

**How to apply:**
- "Smoke test" = small fast verification run (e.g. N=200 agents, 1 seed, 30 iter, single-card, ~1 min wall-clock). NOT a full pilot or production run.
- This applies to **smoke tests**, not to: production training launches, anything pushing to remote, anything spending serious GPU-hours. Production launches still need user confirmation per default risky-action protocol.
- Also applies to regression tests run as part of smoke (e.g. `regime_kind="gru"` numerical bit-exact check) — same 3-round fail loop.
- After 3 failed rounds, write the failure trace to `logs/YYYY-MM-DD.md`, then surface a focused question to the user. Do not silently abandon.

**See also:** [[feedback-critical-thinking]] (honest pushback principle still applies — if 3 rounds shows the approach is fundamentally wrong, say so instead of mechanically trying a 4th).
