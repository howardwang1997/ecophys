# L2-2 — through-M attachment for the L2 recurrent fact-surrogate (via E-3)

Build-register item L2-2 of `papers/proposal/ecomd_reexploration_simulator_contracts_2026-09-06.md`
section 3.3 / section 4: attach the SAME lineage-agnostic composition layer as L1-3
(item E-3, the shared `ReferenceEngine`-backed Python↔torch bridge at
`ecomd/mechanisms/through_m_wrapper.py`) at the recurrent head's per-step flow
output, with the same two estimators (straight-through pinned scale = primary;
perturb-and-MAP pinned noise = audit), estimator/kernel selections shared across
lineages.

## What changed

`ecomd/training/train_fact_surrogate.py` (additive; no existing behavior removed):

- `MechanismBackend` enum — `ENGINE_BRIDGE` (production: construct the shared E-3
  wrapper via `build_engine_bridge_mechanism`; wrapper absence or a missing hook
  factory is a hard `RuntimeError`, never a silent mirror fallback) and `MIRROR`
  (the documented fallback for tests: the pre-L2-2 estimator composition kept
  verbatim in `_build_mirror_mechanism` + `engine_draw_supplier`).
- `FactSurrogateTrainConfig.mechanism_backend` field (default `MIRROR` so every
  pre-existing caller keeps byte-identical behavior; production through-M arms —
  the E-5 frozen configs — select `ENGINE_BRIDGE` explicitly), serialized in
  `config_payload`/`config_sha256`.
- `build_engine_bridge_mechanism(config, *, seed_root)` — dispatches the config's
  estimator to the E-3 hook factory (`straight_through_hook` primary /
  `perturb_and_map_hook` audit) with the E-3 `TrainKernelStream` rooted at
  `seed_root`, binding the config's kernel. The stream derives BOTH the engine
  draw seed and the PAM noise seed from the `train_kernel` node of the seed tree
  (one estimator-blind child per mechanism call), so the same call sequence
  replays identically across through-M arms within a seed (contract C2 note 3).
- `build_mechanism` now takes `train_kernel_generator=None, seed_root=None` and
  dispatches per backend: `ENGINE_BRIDGE` requires `seed_root`, `MIRROR` requires
  the torch generator, RAW still returns `None`.
- `train_fact_surrogate` passes `seed_root` through to `build_mechanism`, so the
  production trainer constructs the real bridge when its config selects it.
- `build_inference_mechanism(config, *, seed_root, draw_index)` and
  `inference_kernel_draw_mechanisms(config, *, seed_root)` — the K = 16
  inference-side draw loop of contract C2(b): draw k's randomness derives from
  substream `kernel:k` (not `train_kernel`) — both backends seed from that
  node's derived integer (MIRROR seeds a torch generator from it; ENGINE_BRIDGE
  roots the E-3 stream at it) — replayed identically across cells within a seed;
  estimator/kernel — not the training-enforcement axis — pick the mechanism, so
  raw-trained cells evaluated under through-M inference construct it here too.

`tests/test_l2_through_m_attachment.py` — new single-file CPU test battery
(coverage map enumerated in `receipt.json`): engine-replay equivalence on a
certified small tape (FIFO exact integer match; random-unit law closed through
the E-3 stream seed and the frozen `exact_clearing`), substream discipline on
both backtracks (same-root byte-identity, seed-root liveness, global
torch/python/numpy RNG untouched), estimator/kernel selectability with the
frozen backward contracts, K = 16 draw order + hand-built seeding equality,
byte-identity of two identically-seeded builds on both backends, and the model
hook attachment through the real bridge (integer-exact cumulating channels,
gradient reaching `flow_head`).

## What did NOT change

`ecomd/models/fact_surrogate.py` (the L2-1 model and its `MechanismEstimator`
hook), `ecomd/mechanisms/through_m.py` (the frozen estimator menu),
`ecomd/mechanisms/through_m_wrapper.py` (E-3, consumed read-only),
`scripts/lab_asset/*`, the frozen A-2 bundle
(`experiments/lab_asset_a2/a2_exit_20260905/`, read-only), and every other build
item.

## Verification scope (PI no-heavy-compute rule)

Single-file pytest runs only (`tests/test_l2_through_m_attachment.py`: 18/18 and
the pre-existing `tests/test_fact_surrogate.py`: 20/20 untouched), single-file
mypy (strict: Success) + ruff (clean) — all via `conda run -n ecophys python …`.
No GPU, no training run, no batch/regression battery, no market data, no
endpoint/outcome access, no trained-model persistence.
