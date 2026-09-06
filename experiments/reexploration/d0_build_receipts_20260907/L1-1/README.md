# L1-1 — L1 corpus adapter (F_exec projection -> L1 input surface)

Build item **L1-1** of the D0 build register (simulator contracts doc
`papers/proposal/ecomd_reexploration_simulator_contracts_2026-09-06.md`
section 2.1 / section 4). Code-only, CPU-smoke verified, outcome-blind.

## What was built

- `ecomd/corpus/l1_corpus_adapter.py` — `build_l1_corpus(prestate, tape, seed,
  *, series=None, n_slots=8, dtype=torch.float32) -> L1Corpus`. Maps a
  lab-asset-v3 tape to lineage L1's input surface (`EcoMDSimulator` /
  `EcoMDv2Potential`) **without re-projecting the tape**: features, payload
  tuples and slot tensors are E-1's `FexecCorpus` verbatim; conserving
  channels are E-4's `ConservingChannelSeries` verbatim (grid and content
  agreement enforced at build time).
- `tests/test_l1_corpus_adapter.py` — 15 tests, single-file CPU scope.

## The four spec'd surfaces per clearing round t

| surface | field(s) | semantics |
|---|---|---|
| INPUT (strictly pre-round) | `agent_states (R, N, d_state=6)`, `context (R, 3)` | anonymous book-state summary + conserving channels; `context` is the `ecomd.py:1110-1116` triple `[log_price, volatility, last_log_return]`; round t sees only rounds < t (t=0 = all-zero no-event token) |
| EXPOSED SLOT | `flow_slot (R, N)` zero-filled | the `z_t` slot L1-2 writes its resting-quantity prediction into; the adapter never predicts |
| SUPERVISION | `features (R, 14)`, `rounds` payload tuples, `slot_prices` / `slot_quantities (R, N)` int64 | the F_exec event records of round t (1:1 via `schema_spec.json` payload fields) |
| CONSERVING CHANNELS | `channels_inc` / `channels_abs (R, 2)` int64 | E-4 pass-through, integer-exact (C5's two aggregate channels) |

Fixed agent-state mapping (documented in the module docstring): one anonymous
level-agent per E-1 queue slot (`N = n_slots`), `d_state = 6` named channels
(`L1_AGENT_STATE_CHANNELS`).

## Verification (this Mac, second-scale only)

- `conda run -n ecophys python -m pytest tests/test_l1_corpus_adapter.py -q`
  — **15 passed in 0.60s** (hand-checked example, shapes/dtypes, E-4 exact
  pass-through, byte-identity + `regenerate()` safety, request-side
  exclusion, pre-round-state-only rule, supervision alignment, consumability
  by `EcoMDSimulator` (v2 pair kernel, one finite step), frozen-bundle
  end-to-end read-only, malformed/mismatch rejection, missing-emitter path).
- `mypy` strict clean on both files; package-scope mypy clean (102 files).
- `ruff` clean on both files.
- One cross-process determinism spot check: `adapter_hash` / `content_hash`
  identical across two independent processes.

## Guardrails respected

No GPU, no training runs, no batch/regression battery, no market data, no
outcome access, no trained-model persistence. The frozen A-2 bundle was
consumed strictly read-only (per-file sha256 re-verified against
`bundle_manifest.json` in-test). The E-2 preflight re-run was NOT executed.
No file under `papers/proposal/`, `papers/paper_d_constraints/`,
`papers/paper_e_matching_fiber/`, `experiments/lab_asset_a2/` or `.claude/`
was modified.

See `receipt.json` for the full record (hashes, deviations, interface notes).
