---
name: mac-icloud-eviction-2026-09-19
description: Mac repo files (experiments/ era) are iCloud-FileProvider-evicted; git stat-refresh blocks on reads; one-shot core.checkStat=minimal unblocks commits; durable fix pending PI decision before D0 freeze
metadata:
  type: project
---

Diagnosed 2026-09-19 while committing the GAMMA activation set (commit 21359e930):

- Old experiment files under `experiments/` are evicted to iCloud (FileProvider). `stat` and `xattr` succeed; content reads block indefinitely until `fileproviderd` materializes the file (evidence: ctimes bumped to the probe moment while mtimes stayed 2026-06-19; fileproviderd at 85% CPU). `git status` hung 45+ min; `git commit` wedged twice in `refresh_index` → `ce_modified_check_fs` → read/mmap.
- Eviction bumps ctime only, so git's default stat check (ctime included) flags every evicted file as modified and re-reads it → hang. mtime+size still match the index cache.
- Workaround (one-shot, does not change repo config): `git -c core.checkStat=minimal -c core.trustctime=false commit ...`. Do NOT run bare `git status` / `git add -A` until fixed — they walk the same path.
- Durable fix needs a PI decision: `fileproviderctl materialize -r` (or `brctl download`) on the repo, or exclude the repo from iCloud Desktop & Documents sync. Must land BEFORE the 2026-10-09 D0 freeze session (freeze = byte-exact git commit of the frozen file set; a mid-freeze hang is a freeze-integrity risk).
- Killing a wedged git leaves `.git/index.lock`; remove it before retrying.

Related: [[gamma-activation-2026-09-19]]
