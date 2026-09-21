# D0-S4 eval-draw driver adversarial audit (2026-09-22)

Target: `scripts/reexploration/eval_draws_d0s4.py` (B1/L1 eval-draw driver, RC1
61,440 + RC4 120 records per analyzer-contract Part 4.1/4.9).

Workflow wf_86e9b2ee-be5 (task wr8qrsvsc): 5 review dimensions (envelope,
arithmetic, determinism, io-resume, spec-gaps) x 2 adversarial refuters per
finding, 69 agents, 5.44M tokens. Full result:
`workflow_result_wr8qrsvsc.json`.

## Confirmed and fixed (all in this commit)

| Severity | Site | Defect | Fix |
|---|---|---|---|
| blocker (4/5 dims) | mechanism cache ~L611 | one shared advancing TrainKernelStream per (kernel, draw) across all through-M cells/horizons -> draw k does NOT replay identically across cells (C2(b)); resume-skip shifts stream offsets | fresh `build_inference_mechanism` per (cell, axis, horizon, draw) record at the use site |
| major | L726 | kswap through-M records run-history-dependent under resume | subsumed by the per-record construction |
| major/minor | `load_scales` L229 | docstring promised refusal of the (1.0, 1.0) training placeholder; not implemented | explicit RuntimeError on exact [1.0, 1.0] |
| minor | manifest/CLI L835+ | empty seed range crashed at `min(seeds)`; no-colon `--seeds N` silently became `range(N)`; `rc1_written` conflated grid + duplicates | strict START:STOP parsing, manifest seeds from parsed bounds, separate `rc1_kswap_duplicates` count |

Also hardened while consolidating PI-package gaps: block/seed namespace
validation against `campaign.BLOCKS_BY_ID`; `stream_hashes` switched to the
4-name `{data,init,minibatch,train_kernel}` preimage (training's recipe,
§5.2); `config_sha256` preimage extended (axis, horizon, estimator,
mechanism_backend); `window_hash` preimage now embeds `(episode_index, rounds)`
so chained h=1/4/16 no longer hash identically; manifest carries a
`pinned_constants` block recording every PI-gated convention verbatim.

## Refuted (kept as-is, with refs in the workflow result)

run_id horizon component (G2 pins pairing not format), pooled BBO scope
(G10 presence-only), `finite` NaN-only idiom (metrics contract value-check is
analyzer-side), RC4 draw_index=0/cell_id/fifo-on-kswap-probe conventions
(probes are K-independent, §5.1), freeze pin-set scope (no driver duty over
unpinned code files), seeds-namespace crash-before-emission claims, kswap
duplicate silent-skip semantics, atomic-write tmp orphan/durability.

## Verification evidence (3080 node, CPU)

- selfcheck `scripts/reexploration/selfcheck_eval_streams_d0s4.py`: 7/7 PASS
  (fifo deterministic; random_unit advancing mechanism yields distinct
  successive calls while fresh per-cell mechanisms replay identically; draw 3
  != draw 4).
- smoke (seed 11000, arm absolute_raw, axes id+kswap, h in {1,4}): 128 RC1 +
  32 kswap duplicates + 2 RC4 in 2 s; independent re-run byte-identical
  (G9); resume into the same tree skips all 130 with zero writes; draw
  payload classes correct (raw and fifo-through-M cells: 1 distinct payload
  over 16 draws; kswap through-M: 2/5 distinct at h=1/4); window_hash and
  config_sha256 now distinguish horizons; stream_hashes matches training's
  4-name recipe on all 130 records; (1.0, 1.0) scales file refused.
- CLI negatives: no-colon and empty-range seeds rejected with clear errors;
  out-of-namespace seeds fail fast.

Remaining open items are PI decisions, not driver defects: see
`../d0s4_eval_pi_package_20260922.md`. All were decided 2026-09-22 in
`../../../decisions/pi_d0s4_eval_constants_20260922.yaml` (horizon chained,
D2-D12 blanket, RC2 extend-now with cap=40/lag=20 + the mechanical package,
production authorization at B1 60/60).

## RC2 extension (same day, post-decision)

`eval_draws_d0s4.py` extended with the 30,720 RC2 truncation-pass records:
D_trunc^W removes initial resting orders with arrival_clock > W from the
deployed book, then replays the recorded request stream from the truncated
prestate (lemma writeup kt_g4_g5 §4). Corpus prestates do not serialize
arrival clocks, so every episode is re-derived from the seed with the frozen
generator under an episode_canonical_json_sha256 guard against the corpus
manifest (ID re-execution reproduces the disk corpus byte-exactly — verified
on the node); E-4 conservation + settlement gates re-run on every truncated
tape. Smoke (seed 11000, arm absolute_raw, both cells, horizons 1/4/16/31,
both conditions): 1 payload class over 16 draws per (cell, condition,
horizon); independent re-run byte-identical including the re-derivation path;
resume skips all pre-existing records. Exposure structure matches the frozen
prediction: truncation invisible at h=1/4 (early rounds do not touch removed
followers), trunc != ID at h=16, lag != cap at h=31. s_ch sealed separately
by `scripts/reexploration/materialize_s_ch_d0s4.py` (namespace 20260977, 512
episodes, sha256 debb15a7…).
