# D0-S1 campaign launch receipts (2026-09-21)

Per-stage launch receipts per the frozen verifier machinery (ops plan §187:
focused tests ≥25, seed-999 CUDA preflight, env sync pip-freeze hash, source
git head, disk gate read). Three nodes staged from the GitHub canonical branch
`paper-d-iclr-2027-completion` at `9b8bba834` (descends from freeze commit
`f4e61bafe`; freeze sha256 `fd4a40b0…9981f57`).

- `receipt_v100ts.json` — 100.80.236.112, L1 channel (B1 + A10 + Stage-2 B2).
  Both offline fail-closed validators re-run GREEN on the full-history clone,
  discharging the freeze-session node-only git-history red. The two
  `logs/private/` locator reds are the battery-v3 dispositioned gitignored
  files, worktree-bound on the node exactly as dispositioned.
- `receipt_v100bts.json` — 100.123.220.57, L2 channel (B3 + Stage-2 B4).
  B3 training additionally waits on the L2 surrogate build (fact_surrogates).
- `receipt_node3080.json` — 100.70.122.100, CPU channel (corpus/DGP/F_exec
  core-capped, nice 10, 6 workers). Rate gate PASSED (probe 8 episodes in 4 s
  single-worker ≈ 0.4 s/episode; full grid 23,040 sessions ≈ 2.6 CPU-h vs the
  18 V100-h basis). Full corpus grid launched 2026-09-21 ~10:55 UTC; log
  `/data/ecophys-campaign/corpus_launch.log`, output
  `/data/ecophys-campaign/corpus/`.

Section 8.3 ≥40%-free STOP gate reads `pi_disk_directive_20260920` at D0-S1
(scratch spread across /data + /data2, R2-canonical final checkpoints, physics
bulk untouched); no single-volume floor is enforced per that directive.
Corpus seed pins per `pi_d0s2_corpus_seed_pins_20260921` (draw tag, 64
episodes). Heterogeneous rule in force: no 3080 cell in V100-benchmarked
blocks; B1 never on the 3080s; A10 seeds from the frozen RNG tree.
