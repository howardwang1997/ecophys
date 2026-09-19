---
name: mac-icloud-eviction-2026-09-19
description: Mac repo files (experiments/ era) are iCloud-FileProvider-evicted; git stat-refresh blocks on reads; one-shot core.checkStat=minimal unblocks commits; PI declined the durable fix 2026-09-19 — freeze session proceeds on the one-shot flags
metadata: 
  node_type: memory
  type: project
  originSessionId: da87b048-5e7f-42b6-8c8a-309a11f55da1
  modified: 2026-09-19T02:24:46.139Z
---

Diagnosed 2026-09-19 while committing the GAMMA activation set (commit 21359e930):

- Old experiment files under `experiments/` are evicted to iCloud (FileProvider). `stat` and `xattr` succeed; content reads block indefinitely until `fileproviderd` materializes the file (evidence: ctimes bumped to the probe moment while mtimes stayed 2026-06-19; fileproviderd at 85% CPU). `git status` hung 45+ min; `git commit` wedged twice in `refresh_index` → `ce_modified_check_fs` → read/mmap.
- Eviction bumps ctime only, so git's default stat check (ctime included) flags every evicted file as modified and re-reads it → hang. mtime+size still match the index cache.
- Workaround (one-shot, does not change repo config): `git -c core.checkStat=minimal -c core.trustctime=false commit ...`. Do NOT run bare `git status` / `git add -A` until fixed — they walk the same path.
- Durable fix options were `fileproviderctl materialize -r` (or `brctl download`) on the repo, or excluding the repo from iCloud Desktop & Documents sync. **PI declined further management 2026-09-19** ("bulk和icloud不用管", decision `pi_bulk_icloud_no_action_20260919`): no durable-fix work; the 2026-10-09 D0 freeze session proceeds on the one-shot safe flags, with `.git/index.lock` pre-cleaned and no bare `git status` / `git add -A`.
- Killing a wedged git leaves `.git/index.lock`; remove it before retrying.

Related: [[gamma-activation-2026-09-19]]
