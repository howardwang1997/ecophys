# L1-2 — ABS/INC supervised coordinate heads + init/minibatch substream bindings

Build item L1-2 of the D0 build register (simulator contracts §2.2 + §2.4 gap
closures; prereg v2 C3/C5, C2(d)). Stage D_minus_1 pre-D0; freeze pinned
2026-09-19.

## What was built

`ecomd/models/l1_coordinate_heads.py` — the two coordinate heads of lineage L1
on the reexploration cube (contract C3 axis `c`): an ABS head predicting the
absolute next conserving-channel state `x_{t+1}` and an INC head predicting
the increment `x_{t+1} - x_t`, over the lineage-invariant corpus grammar
(`FactSurrogateBatch`, features = the frozen 14-feature
`FEXEC_ROUND_FEATURES` map emitted by E-1). Stateless per-round MLP encoder
(`concat(features_t, x_t)`, SiLU/xavier potentials.py idiom) with strictly
pre-round information (no within-round leakage); deterministic decode
(C2(d), no sampling heads); integer-lattice flow `z_t` / demand decodes in
the exact grammar the frozen through-M estimators consume (mechanism
execution itself is E-3/L1-3a/b scope). Construction with a generator makes
the init substream the sole effective parameter-init randomness source
(global-RNG snapshot/restore, the §2.4 day-one lesson).

`ecomd/training/l1_supervised.py` — the C5 supervised rollout-error loss and
the two §2.4 RNG bindings:

- `build_coordinate_targets` — both target families from one observed channel
  path; exact-inverse algebra (`abs == base + inc` identically).
- `l1_supervised_terms` — scaled conserving-channel error terms
  (`Y = sqrt(mean_ch mean_t ((x̂-x)/s_ch)^2)` exposed as `c5_endpoint`;
  training term = the squared form, same minimizer).
- `coordinate_state_prediction` — INCREMENT lifted by the observed base so
  C3's `D_te` subtracts commensurate endpoints (mirrors the L2 surface).
- `combine_supervised_and_fact_terms` — the composition point with the
  existing `multi_fact_terms` path (adds, never replaces).
- **(i)** `init_substream_seed` / `bind_v2_type_seed` — opt-in
  `spawn(seed,'init')` binding for `v2_type_seed` (default-42 behavior
  untouched; active only via the new training path).
- **(ii)** `MinibatchOrderStream` — the shared C1/G2 minibatch-order stream
  from `spawn(seed,'minibatch')`, consumed by
  `train_l1_coordinate_heads` (CPU Adam loop, grad clip, history records).
- RNG-tree derivation is the single shared frozen point
  (`train_fact_surrogate.derive_substream_seeds`); no second derivation.

## Verification (CPU spot checks only; no GPU, no training, no batteries)

- `conda run -n ecophys python -m pytest tests/test_l1_coordinate_heads.py -q`
  — **21 passed**: ABS/INC exact-inverse algebra (targets + head-level lift),
  hand-computed C5 statistic, decode determinism by double execution,
  construction determinism from the init substream, global-torch-RNG-untouched
  for init/forward/minibatch/training-loop (mirroring
  `tests/test_ecomd_v2_sps_rng_binding.py`), supervised gradient flow with a
  single synthetic-batch gradient step for both coordinates (finite loss and
  grads, parameters move), composition with `multi_fact_terms`, byte-identical
  training reproducibility from one seed root, and loud shape/lattice/config
  validation.
- `conda run -n ecophys python -m mypy ecomd/models/l1_coordinate_heads.py
  ecomd/training/l1_supervised.py tests/test_l1_coordinate_heads.py` — Success,
  no issues (strict scope).
- `conda run -n ecophys python -m ruff check …` — all checks passed.

## Files

- `ecomd/models/l1_coordinate_heads.py` (new)
- `ecomd/training/l1_supervised.py` (new)
- `tests/test_l1_coordinate_heads.py` (new)

See `receipt.json` for sha256 hashes, the full deviation list with reasons,
and interface notes for the L1-1 / E-3 / E-5 / L1-5 consumers. The E-2
preflight re-run was NOT executed (separate PI-visible remote step).
