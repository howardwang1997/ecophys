# E-3 — Through-M wrapper (torch composition bridge onto ReferenceEngine)

Build register item E-3, stage D_minus_1 pre-D0, 2026-09-07.
Full receipt: `receipt.json` (same directory).

## What was built

- `ecomd/mechanisms/through_m_wrapper.py` — the composition layer EXTERNAL to
  `ecomd/models/ecomd_v2.py` / `ecomd.py` (both untouched). Intercepts a
  predicted round-t flow tensor, executes it through the exact integer engine
  `M` (`ReferenceEngine.submit`, kernel `fifo` or
  `random_unit_within_price`), and returns the engine's post-round anonymous
  state + conserving channels as torch tensors:
  - `engine_execute_level(...)` — pure forward bridge (one touched price
    level per call, the frozen `MechanismEstimator` granularity; multi-level
    rounds compose by per-level calls threading the engine RNG state).
  - `straight_through_level` / `perturb_and_map_level` — torch autograd
    composition: forward ALWAYS the engine's exact integer output; backward
    reuses `through_m._StraightThrough` (pinned scale 1.0) and
    `through_m._PerturbAndMap` (perturbed-MAP mask, pinned sigma 1.0) —
    single source of truth, zero re-implementation.
  - `straight_through_hook` / `perturb_and_map_hook` — factories matching
    `MechanismEstimator = Callable[[Tensor, int], Tensor]` exactly, so L2-2
    attaches them directly to `RecurrentFactSurrogate.forward(mechanism=...)`.
  - `TrainKernelStream` / `train_kernel_substream_seed` — the `train_kernel`
    substream of the C1 RNG tree (spawn_key=(3, k), one estimator-blind child
    per mechanism call, split into engine/PAM seeds); derivation cross-checked
    against E-2's `named_substream_seed` in tests.
- `tests/test_through_m_wrapper.py` — `[D0 BUILD]` fixture competence gate +
  bridge tests (16 tests, 0.97 s CPU):
  (i) ST forward reproduces both frozen-bundle recorded tapes byte-exactly at
  horizon one (G6 semantics via the lab-asset replay validator, all four
  state hashes per record) PLUS fill-by-fill bridge reproduction with engine
  RNG-state threading; (ii) PAM at noise 0 reduces to the exact kernel on the
  deterministic arm; plus ST hand-checked masked-identity gradient, PAM
  gradient finiteness + substream determinism, kernel-blindness of the input
  interface, integer-exact conservation (zero-sum engine settlement), byte
  determinism, invalid-input rejection, and hook attachment to
  `RecurrentFactSurrogate`.

## Verification (CPU spot checks only, per PI no-heavy-compute rule)

- `conda run -n ecophys python -m pytest tests/test_through_m_wrapper.py`
  — 16 passed (0.97 s).
- `MYPYPATH=scripts conda run -n ecophys python -m mypy
  ecomd/mechanisms/through_m_wrapper.py tests/test_through_m_wrapper.py`
  — both files clean under the project strict config (remaining diagnostics
  in the combined run are pre-existing in the imported sibling
  `tests/test_through_m_estimators.py`, outside E-3 scope).
- `conda run -n ecophys python -m ruff check
  ecomd/mechanisms/through_m_wrapper.py tests/test_through_m_wrapper.py`
  — all checks passed.

## Read-only / frozen inputs

- `experiments/lab_asset_a2/a2_exit_20260905/` — per-file sha256 re-verified
  against `bundle_manifest.json` inside the test before any claim; fixtures
  replayed in memory only; nothing written.
- `ecomd/mechanisms/through_m.py`, `scripts/lab_asset/**`,
  `ecomd/models/ecomd_v2.py`, `ecomd.py` — consumed, never modified.

No GPU, no training, no batch test battery, no market data, no outcome
access; the E-2 preflight re-run was not executed. Deviations and their
reasons: see `spec_deviations` in `receipt.json`.
