# E-2 preflight re-run — the actual D0 corpus generator (2026-09-07)

Freeze contingency #3 of the prereg v2 five-item list (C2(e) as rewritten at v2,
panel R1-8/R2-4): re-run the frozen K-preflight protocol against the ACTUAL D0
corpus generator (build item E-2, `scripts/lab_asset/dgp_request_generator.py`)
rather than the calibration generator. Executed remotely on v100ts
(env `ecophys-d0v2`, numpy 2.4.6) per the PI compute-location rule (2026-09-07,
"直接执行").

## Protocol identity

`run_preflight_e2.py` imports every statistical/invariant/decomposition/bootstrap/
rule component from `k_preflight_20260906/run_preflight.py` unchanged and rebinds
only the generator module (`run_preflight.dgp_stream = dgp_request_generator`).
`derive_seed` is byte-compatible between the two modules by construction. Protocol
parameters identical to the calibration run: seeds 31000–31031 (32), 6
episodes/seed, K grid {4, 8, 16}, thresholds {0.10, 0.05}, bootstrap 2000 draws
@ 31099. Generator config: `DGPConfig()` production defaults — ID axis, N=16
actors, 32 rounds/episode, M1 feedback (anonymous book state via shadow engine),
lab_asset family.

## Result (caveat-and-reporting-only; K=16 immutable per D1_11)

- **Conservative rule (every random_unit draw-dependent statistic has bootstrap
  95% UB of ratio_vs_between ≤ 0.10): K = 16 CLEARS** (`ci_upper` rule output
  "16", not `none_in_set`). Point-estimate variant would allow K = 8; the frozen
  conservative rule governs.
- Per-statistic K=16 CI95 upper bounds: c_lat_exec 0.0177, alloc_hhi_mean 0.0544,
  alloc_l2_mean 0.0155, **alloc_proprata_dev_mean 0.0815**, n_maker_orders_filled
  0.0039. All ≤ 0.10 → **the STOP-class condition (any UB > 0.10) does NOT fire.**
- The calibration run's insufficiency flag on alloc_proprata_dev_mean
  (K=16 CI [0.1182, 0.4703], ratio 0.1958 — draw-dominated at every authorized K)
  is **resolved by measurement on the real generator**: K=16 CI [0.0270, 0.0815].
  Mechanism: 32-round M1 episodes average 2311 walks over 192 episodes, so the
  within-seed draw variance of walk-mean statistics shrinks ~1/rounds while
  between-seed design variance persists. The frozen K=16 decision (D1_11, taken
  under the conservative rule's `none_in_set` on the calibration generator) is
  retroactively validated as sufficient, not merely maximal.
- Invariants: all 6 at 0 failures (fifo payload-projection identity, boundary
  aggregate-hash identity, ru accepted-stream identity, cleared-volume-matches-plan,
  zero rejections, ru null-stat draw variance zero).
- Determinism probes: episode rebuild canonical-JSON byte-identical; engine replay
  projection byte-identical (seed 31000, episode 0, random_unit, draw k=3).
- Episode descriptives: 192 episodes, 2311 walks, V* ∈ {1..12}
  (v*=2: 1067, v*=3: 470, v*=1: 410, v*=4: 184, v*=5: 105, tail 6..12: 73).
- Runtime: 642.4 s single-thread remote CPU. Zero GPU, zero outcome access, zero
  market data, frozen bundle untouched.

## Provenance

- results sha256: see `results.json` provenance block; generator module sha256
  `2cef5a334c7f002…` (E-2 receipt: `../d0_build_receipts_20260907/E-2/`).
- Files: `run_preflight_e2.py` (runner), `preflight_config.json` (protocol config
  as executed), `results.json` (full payload), `determinism_check.json`,
  `remote_run.log` (v100ts console log).
- The five freeze contingencies of prereg v2 now stand: (1) L1-4 RNG fix LANDED;
  (2) L2 CPU smoke + anchors DONE; (3) THIS RE-RUN discharged (STOP not raised);
  (4) Annex B RATIFIED (D1_15); (5) freeze-mechanics execution 2026-09-19 remains.
- Recording route: this directory is the canonical record; the D0 freeze
  inventory should hash `results.json` alongside the calibration preflight's
  `f61e410c…`. prereg v2 itself is NOT edited (freeze candidate; C2(e) already
  specifies this run and its caveat-only status).
