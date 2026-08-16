# Executable Shock Trace IR feasibility v1 runbook

Do not create the formal summary until the implementation, tests and this runbook are committed, pushed and the
remote branch exactly matches `<PROTOCOL_COMMIT>`.

## 1. Clean detached preflight

Create a clean detached worktree at the remotely verified protocol commit. Ensure the ESTIR manifest, bundle
parents and transport-repair parents are present in its sparse view, then run:

```bash
conda run -n ecophys python -m pytest tests/test_executable_shock_trace_ir.py -q
conda run -n ecophys python -m ruff format --check \
  ecomd/research/executable_shock_trace_ir.py \
  tests/test_executable_shock_trace_ir.py
conda run -n ecophys python -m ruff check \
  ecomd/research/executable_shock_trace_ir.py \
  tests/test_executable_shock_trace_ir.py
conda run -n ecophys python -m mypy --strict --explicit-package-bases \
  ecomd/research/executable_shock_trace_ir.py \
  tests/test_executable_shock_trace_ir.py
```

Require `validate_manifest(...)` and `validate_parent_files(..., root)` to return empty lists. Confirm the formal
output path does not exist and the detached worktree is clean. No package installation is authorized.

## 2. Execute once on Mac CPU

No remote worker or network call is needed. Hide CUDA and run:

```bash
CUDA_VISIBLE_DEVICES="" conda run -n ecophys python -m \
  ecomd.research.executable_shock_trace_ir run \
  data/manifests/executable_shock_trace_ir_feasibility_v1.json \
  --root . \
  --protocol-commit <PROTOCOL_COMMIT> \
  --output experiments/v14_executable_shock_trace_ir_feasibility/artifacts/summary.json
```

The runner refuses a dirty worktree, wrong HEAD, existing output, runtime over 60 seconds, more than 100,000 cases
or output above 1 MiB.

## 3. Reconstruct independently

After the summary exists, run the complete deterministic reconstruction:

```bash
conda run -n ecophys python -m ecomd.research.executable_shock_trace_ir verify \
  data/manifests/executable_shock_trace_ir_feasibility_v1.json \
  experiments/v14_executable_shock_trace_ir_feasibility/artifacts/summary.json \
  --root .
```

The verifier recomputes all 72,000 cases, witnesses, gates and the case-ledger hash, and rejects a source or
manifest hash that differs from the repository file. Record wall time and artifact SHA-256 outside the
deterministic summary, then archive a result note.

## 4. Interpretation boundary

A PASS permits only compiler fixture/specification extension. It does not authorize a new theorem claim, a full
EVM/compiler conformance claim, B0 v2, B1 empirical access, accounts, outcomes, G1 or GPU training. A FAIL means the
IR semantics must be repaired under a new version before acquiring compiler data.
