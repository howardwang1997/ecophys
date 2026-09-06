# E-2 — M0/M1-lumpable DGP request generator (D0 corpus generator)

Build item E-2 of the D0 register (code-only build + CPU smoke; stage D_minus_1,
outcome-blind freeze pinned 2026-09-19). Full machine-readable record:
`receipt.json` in this directory.

## What was built

- `scripts/lab_asset/dgp_request_generator.py` — the production corpus
  generator, superseding the calibration-grade
  `experiments/reexploration/k_preflight_20260906/dgp_stream.py` while keeping
  its evaluation surface (`build_episode` / `build_prestate` /
  `order_requests` / `derive_seed`, `EpisodeStream` field layout, walk-plan
  pool snapshots) so the E-2 preflight re-run is a one-line import swap.
- `tests/test_dgp_request_generator.py` — 22 tests (16 functions +
  parametrizations), all green, sub-second.

## Design in one paragraph

Episodes are built round-by-round against an internal shadow `ReferenceEngine`
whose anonymous aggregate book the policy reads (`M1`) or mirrors from the
generator-side stream ledger (`M0`; cross-checked against the engine after
every accepted submit, so M0 and M1 emit byte-identical streams). Makers post
only non-crossing resting orders at untainted levels; aggressors submit only
exactly-consumable walks that sweep tainted/sub-minimum leading levels and take
an interior V* from an untainted target pool. Endowments and per-(actor, side)
unit budgets make every engine validation channel slack — zero rejections by
construction — and no decision reads allocation identity, resting order ids,
or engine RNG state, so the executed request stream is byte-identical under
both allocation kernels (exact request-level CRN, contract C2(a)). All
stochastic consumers draw from the RNG-tree `data` substream via
`SeedSequence.spawn_key` semantics. C4 axes: `config_for_axis` with `id`,
`pop_2x` (2N actors, doubled budgets/schedules/replenish), `tick_2x`
(homogeneous price dilation, band width invariant in 2-delta ticks);
kernel-swap needs no generator change (streams are kernel-invariant). D2
wrappers drive the SAME generator/engine from frozen
`ecomd.eval.synthetic_dgps` series (`garch_student_t5` both lineages,
`multiscale_logvol` L2-only; `negative_jump_iid` defined-but-excluded per
D1_05).

## Verification (single-file spot checks only)

- `conda run -n ecophys python -m pytest tests/test_dgp_request_generator.py -q`
  — 22 passed (includes a `run_preflight` duck-typing run: all six preflight
  invariants hold against this generator).
- `conda run -n ecophys python -m mypy scripts/lab_asset/dgp_request_generator.py`
  — clean.
- `conda run -n ecophys python -m ruff check` on both files — clean.

The E-2 preflight re-run itself was **not** executed (separate PI-visible
remote step, per the hard rules). No GPU, no training, no batch batteries, no
market data, no outcome access.
