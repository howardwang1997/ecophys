# Aave V3 Ethereum LT event directory v1 runbook

Run only after the protocol commit is pushed and the remote ref reproduces it. Use a clean detached worktree at
that exact commit. Materialize the manifest, both parent-artifact directories, the module, tests and this
experiment directory without changing tracked content.

Before network access:

```bash
conda run -n ecophys python -m pytest \
  tests/test_aave_lt_event_directory.py \
  tests/test_aave_liquidation_threshold_source.py -q
conda run -n ecophys python -m ruff format --check \
  ecomd/research/aave_lt_event_directory.py \
  tests/test_aave_lt_event_directory.py
conda run -n ecophys python -m ruff check \
  ecomd/research/aave_lt_event_directory.py \
  tests/test_aave_lt_event_directory.py
conda run -n ecophys python -m mypy --strict --explicit-package-bases \
  ecomd/research/aave_lt_event_directory.py
```

Confirm that the worktree is clean and all four output paths are absent. Then execute exactly once, replacing
`<PROTOCOL_COMMIT>` with the pushed SHA:

```bash
conda run -n ecophys python -m ecomd.research.aave_lt_event_directory \
  data/manifests/aave_v3_ethereum_lt_event_directory_v1.yaml \
  --summary experiments/v14_aave_v3_lt_event_directory/artifacts/summary.json \
  --directory experiments/v14_aave_v3_lt_event_directory/artifacts/event_directory.json \
  --response-hashes experiments/v14_aave_v3_lt_event_directory/artifacts/rpc_response_hashes.json \
  --failure experiments/v14_aave_v3_lt_event_directory/artifacts/failure.json \
  --collection-commit <PROTOCOL_COMMIT>
```

On success, preserve `summary.json`, `event_directory.json` and `rpc_response_hashes.json`; `failure.json` must not
exist. On failure, preserve the first `failure.json` and any completed request evidence, do not substitute an
endpoint or rerun v1, and freeze a new transport-only protocol if warranted. Copy first-run artifacts byte-for-
byte into the active branch, verify them independently without importing the collector, and only then write
`RESULTS.md`.
