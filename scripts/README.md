# `scripts/`

This directory contains current utilities and historical experiment launchers. A filename
is not an endorsement of a current compute target.

## Current policy

- Run Python through `conda run -n ecophys python ...`.
- Use CPU for package, state-contract, synthetic-smoke, and small feasibility checks.
- Use one V100 32 GB only after the model/config/release contract is frozen.
- Use the second V100 for an independent seed or cross-host reproducibility run after the
  single-card reference passes.
- Do not schedule new H20 work. Files named `h20_*` are retained only as historical
  provenance for old experiments.

The current remote addresses and credentials are deliberately not stored in public
documentation.

## Release checks

Build the allow-listed source preview from a committed revision:

```bash
conda run -n ecophys python scripts/build_source_preview.py \
  --output-dir output/source-preview
```

Run the data-free CPU checks:

```bash
conda run -n ecophys python examples/ecomd_cpu_smoke.py
conda run -n ecophys python -m pytest tests/test_ecomd_smoke.py \
  tests/test_simulator_state.py tests/test_release_contract.py -q
conda run -n ecophys python scripts/run_m0_cpu_feasibility.py --require-clean
```

The M0 feasibility command uses the frozen reference architecture with only the
pre-registered CPU overrides (`n_agents=64`, `n_iters=2`). It compares continuous
training against exact interrupt/resume and does not measure market fidelity.

Production training configurations intended for a future checkpoint release must include
`training.release_contract_version: 1`. The loader then hard-fails unless complete and
persistent state is enabled and legacy training/inference-law shortcuts are disabled.

## Historical launchers

Most older launchers encode a particular machine, experiment number, checkpoint layout,
or superseded hardware assumption. Preserve them for reproducibility, but do not copy one
into a new experiment without revalidating:

- simulator and training configuration;
- full-state chunk continuation and exact resume;
- input-data provenance and time split;
- output paths and checkpoint format;
- current hardware and memory budget.

Active experiment-specific instructions belong in that experiment's `DESIGN.md` or
`README.md`, not in this directory-level document.
