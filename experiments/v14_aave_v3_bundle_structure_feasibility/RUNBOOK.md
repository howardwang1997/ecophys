# Aave V3 bundle-structure feasibility v1 runbook

Run from a clean detached worktree at the first pushed commit containing the manifest, implementation, tests and
development protocol. Materialize the hash-pinned A1a artifact paths without changing tracked content.

```bash
conda run -n ecophys python -m pytest tests/test_aave_bundle_structure.py -q
conda run -n ecophys python -m ruff format --check \
  ecomd/research/aave_bundle_structure.py tests/test_aave_bundle_structure.py
conda run -n ecophys python -m ruff check \
  ecomd/research/aave_bundle_structure.py tests/test_aave_bundle_structure.py
conda run -n ecophys python -m mypy --strict --explicit-package-bases \
  ecomd/research/aave_bundle_structure.py
```

Confirm the output is absent and the worktree is clean. Replace `<PROTOCOL_COMMIT>` with the pushed SHA and run:

```bash
conda run -n ecophys python -m ecomd.research.aave_bundle_structure \
  data/manifests/aave_v3_bundle_structure_feasibility_v1.yaml \
  --summary experiments/v14_aave_v3_bundle_structure_feasibility/artifacts/summary.json \
  --collection-commit <PROTOCOL_COMMIT>
```

Do not describe the output as preregistered or blind. Verify the artifact independently from the immutable parent,
then write `RESULTS.md`, update the research topology and preserve the scalar-route failure unchanged.
