# L1-5 — Lock-checkpoint variant + binding sidecar (D0 build receipt)

Build item L1-5 of the D0 build register
(`papers/proposal/ecomd_reexploration_simulator_contracts_2026-09-06.md` section 4),
spec-grounded in section 2.5 [D0 BUILD] L1-5 and the surgery-cell authorities
prereg v2 clause C11 (+ C12 reflexive cells), ops section 3 item 4, and gates
G4/G5/G8/G10. Code-only pre-D0 build: CPU smoke tests and static checks only;
no GPU, no training, no batch batteries, no market data, no outcome access.

## What was built

`ecomd/training/lock_checkpoint.py` — the optimizer-stripped, CPU-offloaded
**lock flavor** of the format_version-2 trainer checkpoint pattern
(`ecomd/training/train_fact_surrogate.py`): same key vocabulary minus
`optim_state_dict` plus `checkpoint_flavor="lock"` and `lock_binding`, same
atomic pid-suffixed temp + `os.replace` write, `torch.load(...,
map_location="cpu", weights_only=False)` load, same validation posture. A lock
freezes a model **plus its RNG runtime plus its corpus binding** so a surgery
cell (C11) or reflexive-firewall cell (C12) can be proven to start from the
byte-identical locked state:

- rank runtime carries the named-substream generator states (C1 seed tree,
  names validated against `SUBSTREAM_NAMES`), the torch/numpy/python global
  states, and the optional recurrent hidden at the save boundary;
- `LockCorpusBinding` records `seed_root`, E-1-vocabulary
  `corpus_hash`/`prestate_hash` (+ optional `tape_hash`/`manifest_hash`),
  `allocation_rule` (validated against the engine kernel set — pro_rata is
  exact-arithmetic only, C3/C16 item 12, and can never be locked) and
  `n_draws` (hard-validated == 16, C16 item 11 / G8/G10).

The **binding sidecar** (`<checkpoint>.lock.json`) records the model sha256,
config sha256, corpus binding fields, checkpoint file sha256, and a hash chain
(sha256 over the canonical JSON of the binding) so the lock is verifiable
without loading weights: `verify_lock(..., deep=False)` never calls
`torch.load`. Deep mode additionally proves weights/config/runtime inside the
file match the sidecar (catches a weights rewrite with a repaired file hash;
the D0 lock manifest G4 `checkpoint_lock_sha256` anchors fully self-consistent
rewrites, which no self-contained instrument can detect). The sidecar is
path-free, so the (checkpoint, sidecar) pair stays verifiable after relocation.

`load_lock_checkpoint` defaults to verify-first (raises `ValueError` listing
every failure), restores each named-substream generator to continue its exact
pre-lock stream, and returns (does not auto-apply) the global RNG states.

Serialization is canonical via `io.BytesIO`: `torch.save` to a path embeds the
destination filename as the zip archive root, so path-based writes are not
byte-reproducible across destinations/pids; the buffer form is (verified
cross-process, identical checkpoint sha256
`cff0fe2ede27538da81b1561376e2e1dac25aafec704b8764b1ce433c135d5c4` in two
independent processes under a seeded ambient runtime).

## Verification (CPU smoke, second-scale)

- `conda run -n ecophys python -m pytest tests/test_lock_checkpoint.py -q`
  → **34 passed (~1.6 s)**: trainer-vocabulary payload adoption,
  optimizer-stripped + CPU-offload, parameter round-trip byte identity,
  restored-generator exact-stream continuation (interrupted prefix + resumed
  suffix == uninterrupted 48-draw run), torch/numpy/python global-runtime
  continuation vs an uninterrupted reference, plain-`nn.Module`
  lineage-genericity, deep + shallow verify (shallow proven `torch.load`-free
  by monkeypatch), checkpoint byte tamper, sidecar binding tamper x5,
  weights-vs-binding deep-only mismatch with repaired file hash, missing
  sidecar, in-payload `lock_binding` drift, loader rejection of
  trainer/optimizer-carrying/stale-version payloads, kernel-set and
  n_draws=16 and hash-format validation, unknown/empty-substream rejection,
  in-process byte determinism, stale crash leftovers inert, failed save
  leaves no artifacts, failed re-save leaves previous lock verifiable,
  sidecar-write failure loudly detected.
- `conda run -n ecophys python -m mypy ecomd/training/lock_checkpoint.py`
  → strict clean. `ruff check` clean on both files.

## Deviations / ambiguity resolutions

See `receipt.json` `spec_deviations` (payload key-set resolution — trainer
vocabulary minus optimizer plus two lock marks; BytesIO canonicalization;
numpy 2.4 live-aliased `get_state()` keys copied; trainer-loop emission
deferred to the D0 training window — `train_distributed.py` untouched; E-1
hash vocabulary adopted; `n_draws` hard-validated). All resolutions take the
narrower, more deterministic reading.

## Not done by design

Trainer-loop wiring ("emitted alongside the state-complete format" happens at
authorized training time, D0 training-window step), E-2 preflight re-run
(separate PI-visible remote step), any cell/evaluation/endpoint execution
(zero outcome access).
