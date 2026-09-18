---
name: v100-disk-migration-2026-09-19
description: V100 cold-data migration to data disks completed 2026-09-19 (both nodes verified); symlinks preserve original paths; bulk physics data intentionally not moved
metadata:
  type: project
---

2026-09-19 (session spanning 2026-09-18 23:05 → 09-19 01:18 local): migrated clearly-cold data to data disks on both V100 nodes so GAMMA training volumes would fit. Pattern: free-space guard → `rsync -aH` copy → `rsync -aHnc --itemize-changes` verify (empty output = identical) → `rm -rf` source → symlink back → MANIFEST.txt line.

- **v100bts** → `/data/ecophys_migrated_20260919/` (6 entries, ~26.8G): `/root/.cache` (19.5G), five `ecophys_constraint_iclr_*` dirs. `/`: 100% (0 free) → 87% (25G free); `/data` 68% (153G free).
- **v100ts** → `/data2/migrated_20260919/` (2 entries, ~76G): `/root/nvhpc_2024_245_Linux_x86_64_cuda_12.4` (13.6G), `/data/graphene_k_cusp_nosmear` (62.3G). `/`: 94% → 87% (27G free); `/data` 99% (8.9G free) → 86% (70G free); `/data2` 90% (20G free — now the fullest disk on ts).

Original paths all work through symlinks. NOT moved (other projects / live processes; needs PI decision before any GAMMA claim on that space): `/root/phonon` trees (live lane A/B monitors), `miniconda3`, v100ts `/data/results` 107G (unknown owner), `/data/graphene_physical_fd_dfpt` 84G, `/data/phonon_offload` 35-48G, `/data/cognition_iclr2027` 26.7G, `/data2/huggingface` 42G.

Operational lesson (also in the 2026-09-18 log, Session 5): the first v100ts launch silently moved nothing — the script was truncated in ssh-heredoc transfer AND the space guard used `df -sm` (invalid; df has no `-s`), so empty `free_mb` made every guard SKIP. Rule: never hand-assemble scripts through ssh heredocs; Write locally, `scp`, `md5sum` byte-compare, then execute. A "LAUNCHED" confirmation only means the process started — verify actual data movement early (ps + df delta).

Related: [[sandbox-launcher-hardening-2026-09-16]]
