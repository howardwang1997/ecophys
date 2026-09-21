---
name: project-d0-campaign-execution-2026-09-21
description: "GAMMA D0 campaign (alpha_cube_d0_20260921) live execution state — nodes, decisions, driver, structural through-M finding, next milestones"
metadata: 
  node_type: memory
  type: project
  originSessionId: c288fd15-32cc-4d46-b3af-8cf7ca9c5f5e
  modified: 2026-09-21T04:48:00.846Z
---

D0 campaign **alpha_cube_d0_20260921** is executing (freeze sha256 fd4a40b0…, freeze commit f4e61bafe, branch paper-d-iclr-2027-completion). Machine assignment frozen: **v100ts (100.80.236.112) = B1/L1** seeds 11000:11030 n_train 2048; **v100bts (100.123.220.57) = B3/L2** seeds 12000:12030 n_train 4096; **3080 node (100.70.122.100) = CPU channel** (corpus + validate). D0-S2 corpus complete: 23,040 sessions, 12/12 manifests, 3.6G; post_corpus.sh (R2 staging → 12-batch validate) ran from 2026-09-21.

Key decisions: `pi_d0s2_corpus_seed_pins_20260921` (draw tag, 64 episodes/seed); `pi_d0s3_train_constants_20260921` (through-M **differentiated** coordinate mode; n_train 2048/4096 at window [64, 64+n); n_iters 100; **device cuda** — PI overrode the CPU recommendation). Driver `scripts/reexploration/train_stage1_d0s3.py` (commits 3b692ec57 → a2090dc53), 31-agent adversarial check consumed (4 blockers + 3 gaps fixed, 12 refuted).

Durable facts:
- **Structural**: frozen `_predicted_channels` is coordinate-blind on the through-M path — blind training makes (absolute,through_m) ≡ (increment,through_m) byte-identical per seed, D_01 = D_11 ≡ 0, J degenerates to T_0. Differentiated mode (ratified) fixes the estimand; per-seed cost anchor ~1-1.5 h per through-M (arm,seed).
- **G9 exemption**: training records are G4-hash-covered and explicitly NOT a G9 re-execution class (analyzer contract Part 4.9 FLAG-7) — so CUDA training breaks no frozen pin; residual (non-bitwise voluntary retraining) accepted by PI.
- G4 hook per job: `training_log.json` with `checkpoint_sha256` (analyzer contract §4.4 pin).
- rclone IS installed on all three nodes at /usr/local/bin/rclone (memory saying "rclone on no host" was stale).

Next milestones: B1/B3 block manifests → Stage-2 B2/B4 eval + analyzer; R2-STAGED-OK → `v100_validate.sh` on both V100 nodes (byte-exact corpus re-derivation); reflexive cell only after four analyzer hashes; verification-liquidity embargo until 2026-10-17 UTC. See [[project-gamma-activation-2026-09-19]].
