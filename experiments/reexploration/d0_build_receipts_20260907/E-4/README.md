# E-4 — Conserving-channel emitter (D0 build receipt)

Build item E-4 of the D0 build register
(`papers/proposal/ecomd_reexploration_simulator_contracts_2026-09-06.md` section 4),
spec-grounded in section 1 "Conservation and settlement" and endpoint authority
prereg v2 clause C5 (panel R2-6). Code-only pre-D0 build: CPU smoke tests and
static checks only; no GPU, no training, no batch batteries, no market data, no
outcome access.

## What was built

`scripts/lab_asset/conserving_emitter.py` — a pure function of
`(prestate, tape)` that re-executes the recorded request stream exactly as
`lab_asset.replay.regenerate` does (reusing replay.py's own coercion helpers and
enforcing `replay`'s record-by-record byte/hash comparison), keeps the engine
handle, snapshots the per-actor integer ledgers (cash, inventory,
units_bought, units_sold) at every request boundary, and emits per clearing
round:

- the two C5 **primary aggregate channels**: `volume_units`, `cash_ticks`
  (pinned order `CHANNEL_ORDER`);
- cumulative (ABS-state) channels after each round;
- auxiliary partition series: buy/sell aggressor side,
  `aggressor_role`/`maker_role` volume and cash, per-actor net ledger deltas —
  each a partition/conservation identity, none in the primary endpoint;
- `conservation_violations(series)` and
  `settlement_violations(prestate, tape, series)`: the integer-exact
  conservation identities (zero-sum cash/inventory transfers per round; gross
  units_bought/units_sold equal executed volume; partitions; running sums;
  constant totals at every boundary; payload-settlement vs engine-state
  agreement). Empty list = all hold.

Round grid: **E-1's frozen corpus grammar** (`ecomd/corpus/fexec_projector.py`,
PI decision D1_01) — a clearing round is the set of execution records sharing
one `execution.clocks.match_ts` (the engine's `last_match_ts`), indexed by the
distinct execution match ticks in ascending order; requests landing on one tick
merge into one round; execution-free ticks are not rounds (sessions without
executions emit an empty series). The client-supplied `round_id` — including
the latency-namespace ids of the frozen bundle — is carried per round as sorted
metadata only. Cross-item agreement with the projector
(`increment_matrix`/`cumulative_matrix`/`match_ts` vs
`channels_delta`/`channels_cumulative`/`match_ticks`) is test-enforced, which
is what keeps the corpus contract lineage-invariant
(`FactSurrogateBatch.channels` row-for-row).

Ledger windows are exact because `ReferenceEngine._settle` is the ONLY mutator
of the four per-actor ledgers outside construction and runs once per
execution: each round's ledger delta is the boundary state after its last
execution minus the previous round's (construction baseline before round 0).

Corpus consumer surface: `ConservingChannelSeries.increment_matrix()` /
`.cumulative_matrix()` give per-round `[volume, cash]` rows — the INC targets
and post-round ABS state for `FactSurrogateBatch.channels` (E-1 / L1-1 /
L2-1).

## Verification (CPU smoke, second-scale)

- `conda run -n ecophys python -m pytest tests/test_conserving_emitter.py -q`
  → **33 passed in 0.99s** (synthetic both-kernel sessions; frozen A-2 exit
  bundle `fixture_fifo` / `fixture_random_unit_within_price`; all 10
  lab-asset-v3.1 enrichment fixtures; the 5 enrichment arm pairs — aggregate
  conserving series identical across fifo/random_unit, the C2(a) CRN premise;
  cross-item agreement with `project_fexec_corpus` on synthetic + frozen
  fixtures; byte-exact determinism incl. cross-process; replay-guard tamper
  rejection; execution-free-round/empty-session handling; violation detectors
  fire on corrupted series).
- `conda run -n ecophys python -m mypy scripts/lab_asset/conserving_emitter.py`
  → strict clean. `ruff check` clean on both files.
- Fixtures consumed strictly read-only:
  `experiments/lab_asset_a2/a2_exit_20260905/` (never mutated) and
  `experiments/lab_asset_a2/enrichment_20260906/`.

## Deviations / ambiguity resolutions

See `receipt.json` `spec_deviations` (enrichment location; aggregate-primary vs
role-attribution resolution; round-grid authority = E-1's engine-clock grammar
with `round_id` as metadata; `regenerate_with_engine` mirror of `regenerate`;
`s_ch` out of scope). All resolutions take the narrower, more deterministic
reading.

## Not done by design

E-2 preflight re-run (separate PI-visible remote step), channel scaling
`s_ch` (hash-sealed DGP-only branch, D0-freeze side), any cell/evaluation/
endpoint execution (zero outcome access).
