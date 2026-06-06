---
name: project-h20-fleet-scheduling
description: "H20 fleet inventory (8+2+2 GPU + 1 CPU node) and GPU scheduling calibration: 62 min/cfg/card measured (exp 114), reserve 6-8h EVAL at window end, plan from measured rates not estimates"
metadata: 
  node_type: memory
  type: project
  originSessionId: f3a85399-5c6f-453a-9576-26ce31fbcae4
---

**Fleet (2026-06-06, user-stated):**
- **H20-1**: 8 cards — main queue (anything with sequential dependencies)
- **H20-2**: 2 cards, **H20-3**: 2 cards — side queues for dependency-free short experiments
- **H20-4**: CPU-only — ABIDES / CPU jobs
- H20-2/3/4 are all SSH-reachable **from H20-1** (not from Mac). Machine IPs/roots live in
  `scripts/machines.local.json` (gitignored; template `scripts/machines.example.json`), read by
  `h20_sprint_driver.sh` / `h20_side_queue.sh` / `h20_abides_remote.sh`.

**Scheduling calibration (lasting):**
- **Throughput: 62 min/config/card** including the eval pass — exp 114 measured 390 cfg / 50h
  on 8 cards. Use this, not ad-hoc estimates; user feedback 2026-06-06: my time estimates run
  SHORT — always benchmark plans against a measured reference run.
- **Reserve 6–8h of every window for evaluation** (user requirement): no new training config
  after `BUDGET_H − EVAL_H`; the tail is for catch-up evals + scoring + packaging + push.
- Unattended windows: the user CANNOT pull results mid-window and relaunch — encode decision
  trees into an H20-side driver (`scripts/h20_sprint_driver.sh` pattern: probe → phase →
  on-machine scoring → conditional branch → EVAL window).
- Partial-queue trick: seed-major config naming (`config_s00_*`, `config_s01_*` …) + per-config
  train+eval (`scripts/side_worker.sh`) so a wall-clock cutoff leaves balanced, fully-scored cells.

**Why:** the weekend-sprint planning session went through three corrections (budget 36–48h not
7 days; no mid-window decisions; eval reserve) — all were user-known constraints I didn't ask
about up front.

**How to apply:** before designing any H20 batch, (1) state the window length and EVAL reserve,
(2) compute configs = (window − eval) × cards / 62min, (3) assign dependency-free work to
H20-2/3, (4) if unattended, put all conditionals into the driver script.
