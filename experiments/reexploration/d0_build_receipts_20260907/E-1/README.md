# E-1 — F_exec corpus projector (tape → per-round tensors)

Build item E-1 of the D0 build register (simulator contracts §4; spec §1, PI decision
D1_01). Stage D_minus_1 pre-D0; freeze pinned 2026-09-19.

## What was built

`ecomd/corpus/fexec_projector.py` — a pure function
`project_fexec_corpus(prestate, tape, seed, *, n_slots=8, dtype=torch.float32) -> FexecCorpus`
mapping a lab-asset-v3 (prestate, tape, seed) to per-clearing-round tensors:

- **Pure selection** (D1_01): the corpus content is exactly the frozen `schema_spec.json`
  execution field list `[execution, aggressor_role, maker_role, allocation_draw?,
  pre_best_bid, pre_best_ask, post_best_bid, post_best_ask]`. Request-side events and
  `order_accepted.resting_quantity` are excluded by construction — extra keys are
  *rejected*, not silently dropped, and perturbing request-side payloads leaves
  `content_hash` and every tensor bit-identical.
- **Lineage-invariant grammar**: `features` (R, 14) is emitted by the frozen
  `ecomd.models.fact_surrogate.fexec_round_features` / `FEXEC_ROUND_FEATURES` itself.
- **L1/L2 batch slots**: `channels_delta`/`channels_cumulative` (R, 2) int64 — the two
  C5 aggregate conserving channels (executed volume units, executed cash ticks) with a
  zero-base cumsum; `slot_prices`/`slot_quantities` (R, n_slots) int64 under the
  ragged-round padding contract: distinct execution prices ascending in slots 0..k-1,
  right-padded to `n_slots` (default 8, matching `FactSurrogateConfig.n_slots`) with
  quantity-0 never-clearable slots; > n_slots levels raises (never truncates).
- **Round grid**: grouped by distinct `execution.clocks.match_ts` ascending (engine
  clock); `round_id` is metadata only.
- **Determinism**: no stochastic consumer (`seed` binds identity only); regenerated
  tapes project to byte-identical corpora (verified via `lab_asset.replay.regenerate`
  on the frozen bundle); three-hash identity (`tape_hash` provenance /
  `content_hash` selection-only / `corpus_hash` binding everything).

## Verification (CPU spot checks only; no GPU, no training, no batch batteries)

- `conda run -n ecophys python -m pytest tests/test_fexec_projector.py` — **10 passed**
  (hand-computed projections, round grouping, padding determinism + overflow,
  replay byte-identity, exclusion correctness, None-quote fallback, malformed-payload
  rejection, shapes/dtypes, and 2 read-only frozen-bundle fixture tests with in-test
  sha256 verification against `bundle_manifest.json`).
- `conda run -n ecophys python -m mypy ecomd/corpus/fexec_projector.py
  ecomd/corpus/__init__.py tests/test_fexec_projector.py` — Success, no issues.
- `conda run -n ecophys python -m ruff check ecomd/corpus/ tests/test_fexec_projector.py`
  — all checks passed.

## Files

- `ecomd/corpus/__init__.py` (new)
- `ecomd/corpus/fexec_projector.py` (new)
- `tests/test_fexec_projector.py` (new)

See `receipt.json` for sha256 hashes, the full deviation list with reasons, and
interface notes for E-2/E-3/E-4 consumers. The frozen A-2 bundle
(`experiments/lab_asset_a2/a2_exit_20260905/`) was consumed strictly read-only.
