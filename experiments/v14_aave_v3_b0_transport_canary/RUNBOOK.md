# Aave V3 B0 transport canary v1 runbook

Do not execute this canary until its manifest, implementation, tests and preregistration are committed, pushed and
the remote branch matches the exact protocol SHA.

## 1. Preflight

From a clean detached worktree at `<PROTOCOL_COMMIT>`:

```bash
conda run -n ecophys python -m pytest tests/test_aave_b0_transport_canary.py -q
conda run -n ecophys python -m ruff format --check \
  ecomd/research/aave_b0_transport_canary.py tests/test_aave_b0_transport_canary.py
conda run -n ecophys python -m ruff check \
  ecomd/research/aave_b0_transport_canary.py tests/test_aave_b0_transport_canary.py
conda run -n ecophys python -m mypy --strict --explicit-package-bases \
  ecomd/research/aave_b0_transport_canary.py tests/test_aave_b0_transport_canary.py
```

Validate the duplicate-safe manifest and every v1 parent hash locally. Confirm all four host output paths and the
aggregate output are absent.

## 2. Stage identical code

Copy only the committed script and manifest to a new isolated temporary directory on each predeclared remote host.
Verify their SHA-256 values against the detached worktree. Host SSH targets remain in
`scripts/machines.local.json`, which is gitignored. Use the existing Conda interpreters:

- V100 hosts: `/root/miniconda3/bin/conda run -p /data/ecophys_workshop/conda_env python ...`
- RTX 2060 host: `/home/howardwang/anaconda3/bin/conda run -n ecophys python ...`
- Mac: `conda run -n ecophys python ...`

Set `CUDA_VISIBLE_DEVICES` to the empty string. Do not install a dependency or clone bulk repository history.

## 3. Run all four sealed host probes

On each host, substitute its frozen ID and unique absent output path:

```bash
conda run -n ecophys python aave_b0_transport_canary.py run \
  aave_v3_b0_transport_canary_v1.json \
  --host-id <HOST_ID> \
  --protocol-commit <PROTOCOL_COMMIT> \
  --output <HOST_ID>.json
```

Run all four even if an earlier host passes. Do not query an Aave address, add an endpoint, change order, retry a
completed host, or inspect target logs.

## 4. Aggregate once

Hash-copy the three remote artifacts back to the clean detached worktree and aggregate with the local result:

```bash
conda run -n ecophys python -m ecomd.research.aave_b0_transport_canary aggregate \
  data/manifests/aave_v3_b0_transport_canary_v1.json \
  --root . \
  --protocol-commit <PROTOCOL_COMMIT> \
  --host-result v100_a=<PATH> \
  --host-result v100_b=<PATH> \
  --host-result rtx2060=<PATH> \
  --host-result local_mac=<PATH> \
  --output experiments/v14_aave_v3_b0_transport_canary/artifacts/summary.json
```

Archive all four raw host artifacts, the aggregate summary and a result note. A PASS permits only a separately
committed B0 v2 protocol using the selected host/endpoints/range hints. It is not permission to run B0 v2 directly.
