# D0-S4 B1 eval PI decision package (2026-09-22)

Driver `scripts/reexploration/eval_draws_d0s4.py` is rewritten, adversarially
verified (69-agent workflow: 1 blocker + 1 major + 3 minors confirmed and
fixed; refutations logged), and smoke-green on the 3080 node — evidence in
`d0s4_eval_driver_audit_20260922/`. No production eval record exists yet.
This package lists every constant the frozen text does not pin. Items marked
DEFAULT are already implemented in the driver; ratification makes them the
decision-record values, and any override is a one-line change before first
production execution.

Execution timing: full-seed eval needs all four arm checkpoints per seed, so
production launches when B1 reaches 60/60 (watcher armed; ETA ~19 h from
2026-09-21 evening). The driver fails fast on any missing checkpoint; no
partial seed grid is ever written.

## D1 — horizon mode (FORK)

- `chained` (recommended): pool the first h rounds across episodes in episode-index
  order; the filling episode contributes the remainder. Every h in {1,4,16,31}
  materializes; h=31 pools the first ~2-5 episodes.
- `within_cap`: every episode contributes min(h, T_e) rounds.

Degeneracy facts (decision inputs, verified against the corpus): episode
T ∈ [6,24]; no mode measures within-session round indices ≥ ~24; chained h=1
is a single round; within_cap h=31 pools all rounds of all 64 episodes and
coincides with the h=64 descriptive set. h-stratified Holm-family
comparability depends on this choice.

## D2 — stream_hashes preimage (DEFAULT: 4-name)

sha256 over the canonical JSON of `{data, init, minibatch, train_kernel}`
from `derive_substream_seeds(seed_root)` — training's exact recipe
(train_stage1_d0s3.py L805-807) and §5.2's named set, so G2's per-seed
pairing holds across record classes. Alternative rejected: hashing all 20
substream names (diverges from training digests for the same seed).

## D3 — fixture_manifest_sha256 semantics (DEFAULT: stream-manifest sha)

sha256 of the per-(corpus-axis, seed) `stream_manifest.json` actually
consumed. The lab-asset-v3 bundle anchor fea8a136… stays the bundle-level
canonical value under the Annex C typo inventory; the per-record value is the
stream member.

## D4 — record literals + run_id formats (DEFAULT)

condition `id` (training records used `train` — per-record-class literals);
record_class `RC1`/`RC4`; cell_id dash-joined
`{coordinate}-{training}-{inference}`; run_id
`{block}.eval.{arm}.{axis}.{cell}.{seed:05d}.{draw:02d}`; probe run_id
`{block}.probe.{axis}.{seed}`; kswap duplicate suffix `.kswap`; G8
byte-identity exempt fields {record_key, run_id, axis}. G2 pins uniqueness
and pairing, not formats; these are pinned here.

## D5 — window_hash + pooled BBO scope (DEFAULT)

window_hash = sha256 over canonical JSON of
`[{episode_index, rounds, **boundaries}, …]` in episode-index order (the
coverage pair makes chained h=1/4/16 distinguishable); the same digest fills
all four state-hash fields. pre/post_best_bid/ask carry the last window
episode's session boundaries (G10 is presence-only; no frozen text assigns
pooled-span semantics).

## D6 — config_sha256 preimage (DEFAULT)

Per-record canonical dict: runtime, horizon_mode, coordinate,
training/inference enforcement, axis, horizon, estimator
(straight_through), mechanism_backend (engine_bridge),
checkpoint_lock_sha256, scales_sha256. Fully record-scoped; G2's "8 cells
share config hashes" reading is the stream_hashes pairing (D2), not this
field.

## D7 — mechanism cadence (DEFAULT; the blocker fix)

Fresh `build_inference_mechanism` per (cell, axis, horizon, draw) record;
the kernel:k substream is consumed from position 0 in record order, so draw
k replays identically across cells, axes, horizons, and resume boundaries
(C2(b), contract line 48 "the same K streams are replayed for every cell
that consumes draws, within a seed, across all axes"). Selfcheck evidence
7/7 (`scripts/reexploration/selfcheck_eval_streams_d0s4.py`).

## D8 — RC4 probe conventions (DEFAULT)

cell_id `engine-replay-probe`; draw_index 0; horizon 1; n_draws 16;
checkpoint_lock_sha256 null; allocation_rule fifo on every axis (incl.
kswap-axis probes — deployment-kernel swap is a through-M-inference concept,
probes replay the fifo corpus); episode 0; replay failure aborts the seed.
Probes are K-independent (§5.1, Part 4.1: 420 campaign-wide = 4 axes × seed
units; B1 share 120).

## D9 — s_ch materialization (WORK ITEM, plan for ratification)

Annex B(e)/§C5 pin: s_ch = DGP-native per-event innovation std from the
hash-sealed DGP-only sample branch — DGP-truth side only, D0-hash-committed
generator sample, never simulator output, never the paired corpus. Plan: on
the 3080 CPU node, frozen `generate_episode` + frozen lab_asset.yaml
DGPConfig, reserved seed namespace 20260977 (disjoint from 11000+/12000+),
512 episodes (episode_index 0..511), s_ch = per-channel std of the per-round
channel increments (channels_delta) pooled over all rounds of all episodes;
write `{s_ch, provenance{…derivation, n_episodes, seed_namespace, generator
pins…}}`; the file's sha256 is recorded in the decision record (the seal);
the driver refuses the [1.0, 1.0] training placeholder.

## D10 — RC2 truncation records (FORK)

B1's D0-S4 scope includes 30,720 RC2 truncation-pass records (Part 4.1) with
no producer: no trunc_lag/trunc_cap deployment-pass logic exists and the W
grid is unpinned in every frozen authority.

- (a) Defer to a dedicated D0-S4 sub-session with its own PI decision after
  B1's RC1 records land (recommended — the W-grid choice deserves its own
  evidence table, and RC1 is the confirmatory long pole).
- (b) Extend this driver now (requires the W-grid decision today).

## D11 — execution site (DEFAULT: 3080 CPU node)

The driver is CPU-only (deterministic kernels for G8/G9 byte-identity); the
3080 node is the assigned CPU channel; eval is not inside a
V100-benchmarked block, so the heterogeneous-pool rule is not engaged. Full
seed ≈ minutes single-thread; 30 seeds + probes fits trivially; G9
re-execution byte-identity verified on-node.

## D12 — scope guards (DEFAULT)

No L2/B3 eval (invalid test, pi_d0s3_l2_invalid_test_20260921 — unchanged);
B4 disposition at the mechanical gate, flagged honestly (t4 "≥28/30 finite
loss" passes trivially at zero learning). Estimator STRAIGHT_THROUGH +
ENGINE_BRIDGE on every through-M eval cell (KT-A4 primary; PAM is the A10
audit only). Through-M coordinate composition: engine-increment cumulation
from a per-episode zero base for both coordinates (mirrors training's
ratified differentiated mode; the abs head is not read on the through-M
path). Freeze pin-set: 3-file sha256 pins + FREEZE_COMMIT ancestry (drivers
carry no whole-freeze-list duty). conservation_violation_steps:
per-step float integrality of the volume/cash increments (raw cells carry
zeros — G7 does not apply). Input-scope validation against
campaign.BLOCKS_BY_ID enforced in-driver.

## On ratification

1. Record the decision id; write scales file per D9 on the 3080 node; seal.
2. At B1 60/60: full-grid eval 11000:11030 on the 3080 node
   (`--production-decision <id>`), resume-safe.
3. R2 staging of records + eval manifest under
   `alpha_cube_d0_20260921/eval/B1/`.
4. Analyzer A_B1 runs only when all four blocks' records exist; reflexive
   cell ordering unchanged (after four analyzer hashes).
