---
name: commit-autonomy
description: "2026-09-20 user pref: commit+push agent change sets without per-commit asks; private-content exclusions and frozen gates unaffected"
metadata:
  type: feedback
---

PI removed the per-commit-authorization ritual on 2026-09-20 ("去掉这个规矩，直接做", decision `pi_commit_autonomy_20260920`, parent `pi_disk_directive_20260920`).

**Why:** the agent had asked "commit 授权?" five times across recent sessions (analyzer ratification, items 9/10, battery dispositions, disk directive); the PI ended the ritual rather than granting one more.

**How to apply:** commit and push agent-executed change sets on the working branch directly — iCloud-safe one-shot flags (`core.checkStat=minimal core.trustctime=false`), explicit path adds, both fail-closed validators green before claiming consistency. Still binding (content/procedure rules, not asks): never commit `logs/private/` or private paper_d/output/pdf revision content; `scripts/lab_asset/` frozen; frozen prereg text not agent-amendable; deliberate-uncommitted list (e.g. `scripts/rfx_diag_20260919.py`); freeze-session mechanics per prereg §1.3. Not authorization for experiments/GPU. See [[gamma-activation-2026-09-19]] for the compute-location rule.
