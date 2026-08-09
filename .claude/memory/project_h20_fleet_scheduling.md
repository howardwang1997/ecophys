---
name: project-h20-fleet-scheduling
description: "Historical H20 fleet record, superseded for future planning on 2026-08-09. Current compute starts at 2×V100 32 GB and may expand only through non-H20 GPU/CPU pools. Historical throughput remains provenance, not a scheduling assumption."
metadata: 
  node_type: memory
  type: project
  originSessionId: f3a85399-5c6f-453a-9576-26ce31fbcae4
---

> **SUPERSEDED FOR SCHEDULING (2026-08-09).** The user explicitly removed H20 from all future
> compute plans. Current production capacity is two independent V100 32 GB nodes and may expand to
> more non-H20 GPU/CPU workers. The inventory and paths below are retained only to interpret historical
> experiments. Do not schedule, budget, or write new runbooks against these H20 machines. Use measured
> V100-equivalent GPU-hours and re-benchmark every new device type.

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

**howard-pc as an ABIDES CPU node (2026-06-13, provisioned this session):**
- `100.105.21.7` = **howard-pc**, the user's personal desktop (16 cores), NOT a pre-configured
  fleet node. **SSH from Mac works as `howardwang@` (key auth)** — contradicts the old "remote not
  reachable from this session" note for THIS box (Tailscale 100.x). conda at `~/anaconda3`.
- Provisioned: **partial+sparse clone** `~/ecophys` (`git clone --depth 1 --filter=blob:none
  --no-checkout … && git sparse-checkout set scripts ecomd`) — avoids the **multi-GB committed
  result-JSON tree / 81k-object history** (a full clone was 2.3G+ and climbing; sparse = 14M).
  **The repo bloat will bite any fresh clone — always sparse/shallow on new boxes.**
- abides env: `conda create -n abides python=3.10` + `pip install numpy pandas scipy tqdm matplotlib
  seaborn jsons joblib psutil pprofile` (runbook's "only numpy/pandas" is WRONG); `PYTHONPATH=
  ~/abides`; **patch vanilla abides for pandas 2.x**: `from pandas.io.json import json_normalize`
  → `from pandas import json_normalize` (3 files). ecophys env: py3.11 + `pip install -e .` (scoring).
- **ABIDES RMSC03 daily cost (MEASURED): ~41 min/sim concurrent (14-way on 16 cores)** because
  `book_freq="S"` logs per-second OB (23,401 rows/sim) — pure waste for a close-to-close daily
  return. Full daily 250 seeds × 5 cells (1250 sims) ≈ **58h**, +sbi serial ~8h ≈ **66h / 2.75d**.
  **Coarsening book_freq → ~1–3h with identical daily returns** (user chose to run as-is anyway).
- **Resume:** `~/abides_resume.sh` (idempotent — calibrate skips done CSVs) wired as an **@reboot
  cron** (`@reboot sleep 60 && bash ~/abides_resume.sh`); pgrep+flock guards prevent double-launch;
  self-removes the cron when daily(1250)+`sbi_cost_report.json` are both done. Bootstrap +
  resume scripts live at `~/abides_bootstrap.sh` / `~/abides_resume.sh` on the box.
- Reusable scripts on branch `feature/abides-cpu-paperA`: `scripts/cpu_paperA_abides.sh {daily|sbi|all}`.

**Two H20 boxes SSH-reachable from THIS Claude session (2026-06-23, user-provided + verified):**
- `100.80.123.104` = **2× H20**, `100.91.194.14` = **8× H20**, user **root**, **key auth works directly
  from the Mac Claude session** (`ssh -o BatchMode=yes root@…`) — so the CLAUDE.md "H20 NOT accessible
  from this Claude session" is NOT absolute; these specific Tailscale-100.x boxes ARE reachable. (Don't
  assume; verify per box — reachability is network/session-dependent.)
- 8-card box: `ecophys` conda env at `/root/miniconda3/envs/ecophys` (torch 2.4.0+cu124, 8 H20), internet
  OK, 192 cores / 2 TB RAM. `which conda` is empty in non-login shell — call `/root/miniconda3/...` paths
  or `bash -lc`. Both boxes mount the **GPFS NFS `/AI4S`**.
- **CANONICAL working tree + data on GPFS: `/AI4S/Users/howardwang/h204/ecophys/`** — the full repo (.git
  at an older commit), **`raw/` data, and the saved exp-123 trajectory npz** (`experiments/123_driven_
  transient/results_{asset}_{control,kick6,jump6,…}/ofi/trajectory_*.npz`, ~2,730 files, all 5 assets).
  Fresh boxes have NO local repo/checkpoints — use this NFS path. (NB `/AI4S/Users/howardwang/ecophys/`
  WITHOUT `h204/` only has `raw/` — wrong path.)
- **To run analysis on existing trajectories (no retrain):** `scp` the new script(s) into the NFS repo,
  `cd /AI4S/Users/howardwang/h204/ecophys && /root/miniconda3/envs/ecophys/bin/python scripts/<x>.py …`,
  `scp` the small result JSONs back to the Mac. Checkpoints are NOT on R2 by default (`INCLUDE_CKPT=0`);
  the exp-123 calibrated `concave_d050` ckpts were on the original box's disk, not these fresh nodes.
