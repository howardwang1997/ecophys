# Aave V3 B0 transport repair canary v2 runbook

Do not issue a new RPC request until the manifest, v1 dependency, v2 implementation, tests, preregistration and
official-source audit are committed, pushed and the remote branch equals the exact protocol SHA.

## 1. Preflight at the pushed commit

Create a clean detached worktree at `<PROTOCOL_COMMIT>` and run:

```bash
conda run -n ecophys python -m pytest \
  tests/test_aave_b0_transport_canary.py \
  tests/test_aave_b0_transport_canary_repair.py -q
conda run -n ecophys python -m ruff format --check \
  ecomd/research/aave_b0_transport_canary.py \
  ecomd/research/aave_b0_transport_canary_repair.py \
  tests/test_aave_b0_transport_canary.py \
  tests/test_aave_b0_transport_canary_repair.py
conda run -n ecophys python -m ruff check \
  ecomd/research/aave_b0_transport_canary.py \
  ecomd/research/aave_b0_transport_canary_repair.py \
  tests/test_aave_b0_transport_canary.py \
  tests/test_aave_b0_transport_canary_repair.py
conda run -n ecophys python -m mypy --strict --explicit-package-bases \
  ecomd/research/aave_b0_transport_canary.py \
  ecomd/research/aave_b0_transport_canary_repair.py \
  tests/test_aave_b0_transport_canary.py \
  tests/test_aave_b0_transport_canary_repair.py
```

Load the duplicate-safe manifest and require both `validate_manifest(...)` and `validate_parent_files(..., ".")`
to return an empty list. Confirm the two host-output paths and aggregate-output path do not exist.

## 2. Stage byte-identical code

Stage only these committed files in a new isolated temporary directory on RTX 2060 and in the detached Mac
worktree:

- `ecomd/research/aave_b0_transport_canary.py` (the hash-pinned v1 dependency);
- `ecomd/research/aave_b0_transport_canary_repair.py`;
- `data/manifests/aave_v3_b0_transport_canary_repair_v2.json`.

Recompute all SHA-256 values after transfer. The RTX SSH target and Conda identity come only from the gitignored
`scripts/machines.local.json`. Do not install a dependency, copy target data or stage repository history.

## 3. Run both sealed hosts

Run RTX 2060 and Mac concurrently, with distinct absent output paths and CUDA hidden:

```bash
CUDA_VISIBLE_DEVICES="" conda run -n ecophys python -m \
  ecomd.research.aave_b0_transport_canary_repair run \
  data/manifests/aave_v3_b0_transport_canary_repair_v2.json \
  --host-id <rtx2060-or-local_mac> \
  --protocol-commit <PROTOCOL_COMMIT> \
  --output <UNIQUE_ABSENT_PATH>
```

Both hosts run even if RTX passes. Do not probe the six inherited routes, an Aave address/topic, a replacement BNB
endpoint, transaction, receipt, state, account, price or outcome. Do not use a V100 or GPU.

## 4. Retrieve and aggregate once

Hash-copy the RTX artifact into the clean detached worktree. Aggregate it with the Mac artifact only after both are
complete:

```bash
conda run -n ecophys python -m ecomd.research.aave_b0_transport_canary_repair aggregate \
  data/manifests/aave_v3_b0_transport_canary_repair_v2.json \
  --root . \
  --protocol-commit <PROTOCOL_COMMIT> \
  --host-result rtx2060=<PATH> \
  --host-result local_mac=<PATH> \
  --output experiments/v14_aave_v3_b0_transport_canary_repair/artifacts/summary.json
```

Independently rerun aggregation to a separate absent temporary path and require byte identity. Archive both host
artifacts, the aggregate and a result note. A PASS permits only a new, pushed B0 v2 design commit; it is not
permission to execute B0 v2 in the same step.
