# ICLR confirmation deployment gate

Date: 2026-08-31, after the final ID-only pilot lock and before any confirmation seed or pilot OOD
outcome was accessed.

## Immutable payload

- Archive:
  `experiments/constraint_attribution_iclr/deployment/constraint_iclr_confirmation_snapshot_20260831.tar.gz`
- Archive size: 41,426 bytes.
- Archive SHA-256:
  `b70c000cdd1c70d676ce1846f74e66d147bcd8a03a0fc0a84564e8e0cbbb1305`
- The archive has 29 entries: six scripts, eleven Hydra configurations/manifests, seven frozen
  protocol documents, the focused test file, the selector-input manifest, the final lock, the
  payload file list, and the per-file SHA-256 manifest.
- A clean-room extraction passed all 28 per-file SHA-256 checks.
- Local quality gates passed: Ruff and all 25 focused tests.

The immutable final selection lock has SHA-256
`5100ae5ca6f757a5166fba3692fd912e19e7a0c7a4da65980488e92a402c604e`.
Every generated production command includes both its path and hash. Both runners independently
re-hash the lock before training, include it in source provenance and run identity, and fail closed
on absence or mismatch. The confirmation analyzer also rejects records whose top-level identity,
resolved configuration, or source hashes do not bind to that exact lock.

## Frozen execution allocation

| worker | systems | unique mechanism/cell jobs | expected JSONL records |
|---|---:|---:|---:|
| `root@100.80.236.112` (`v100a`) | 6 | 36 | 1,440 |
| `root@100.123.220.57` (`v100b`) | 4 | 22 | 870 |

The record totals include the derived projection record produced for every free run. Each selected
mechanism/cell job trains all 30 paired confirmation seeds 1000--1029. Pilot runtimes imply about
3.3 and 24.6 training-only V100-hours on `v100a` and `v100b`, respectively; rollout evaluation and
I/O are additional, so these are monitoring estimates rather than stopping limits.

## Deployment gate

The payload has not been copied and confirmation has not been launched. After explicit approval:

1. Copy the exact archive to both hosts and extract it only under
   `/root/ecophys_constraint_iclr_confirmation_20260831/`.
2. Verify the archive SHA-256 and all 28 per-file hashes on each host.
3. Run the 25 focused tests in `/data/ecophys_workshop/conda_env` on each host.
4. Run one isolated seed-999 CUDA record per host using `stage=confirmation`, the exact lock path
   and hash, one epoch, and a separate preflight output. Verify V100 identity, finite metrics, Git
   head `86dd76ee0127c5eb7945a5806bdad74548c62459`, `git_dirty=true`, and lock provenance.
5. If and only if both preflights pass, launch the frozen `v100a` and `v100b` workers with
   `ECOPHYS_GIT_HEAD=86dd76ee0127c5eb7945a5806bdad74548c62459` and `ECOPHYS_DIRTY=1`.
6. Use one exclusive GPU lock per host, append-only outputs, and run-ID skipping. Do not impose the
   superseded 25-hour stopping rule.

Pilot OOD remains unopened through deployment and execution. After both workers finish, verify
record coverage, provenance, finiteness, and local/remote file hashes before running the frozen
confirmation analyzer exactly once.
