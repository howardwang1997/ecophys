---
name: sandbox-launcher-hardening-2026-09-16
description: Sandbox launcher adversarial review fixes landed; terminal manifest pins now verify against git history; response-DX state committed; validator green with --base-ref HEAD
metadata:
  type: project
---

2026-09-16 Session 2 (sandbox preflight, PI-selected option after the strategy review):

- Adversarial launcher review: 14 findings → 13 distinct, all confirmed; fixes in commit 4173f9e6f (out-of-tree hash-chained anchor at `~/.ecomd/discovery_sandbox_anchors/<id>.jsonl`, triple config re-hash, manifest genesis re-check, receipt digest checks, expired-sandbox quarantine unlock via `as_of = min(now, expires_at - 1s)`, launcher provenance fields, lock hardening, capture ordering, resumable quarantine). Residuals: anchor erasable by same-uid; ms-scale config-swap window; first-launch `--base-ref` operator trust.
- Launcher-pin defect fixed: manifest execution-contract pins used to hash the working tree, freezing any shared script a terminal manifest pinned. Terminal sandboxes now also accept a committed version (git history, ≤64 commits); live sandboxes stay working-tree-strict. Prefer per-sandbox launcher copies (`sandbox_inputs/<id>/`) for future manifests over shared `scripts/` pins.
- The 2026-09-12 response-DX sandbox state was untracked; its freeze commits (9d9071196, ac49b0e21) are dangling on no branch. Landed as authorization-only commit 6727e7dad + terminal commit 52a328c01.
- Platform gate resolved 2026-09-16 (Session 3): PI chose the public-repository option and re-confirmed it after the 2026-09-05 private setting was traced to Paper D ICLR-2027 double-blind protection (abstract deadline 2026-09-18). Credential scan clean (tree + full history; only placeholder-empty example env files ever added). howardwang1997/ecophys is public; `main` carries the required `research-governance` check with force-push/deletion disabled and admin bypass off. Bourse preflight item 1 satisfied; its stale "now satisfies item 1" claim corrected in place.
- PI sandbox-target selection: g42 fixed-knot learned moves (g38 not selected).
- Validator green `--base-ref HEAD`; canonical counts now evidence 1390 / 191 raw questions / 38 cycles. No sandbox authorized; Paper G 107/31/0 unchanged. Before any execution authorization: Bourse 0.4.0 authorization-only merge, g42 manifest/decision, conformance rerun on the hardened launcher.

Related: [[paper-g-strategy-review-2026-09-16]]
