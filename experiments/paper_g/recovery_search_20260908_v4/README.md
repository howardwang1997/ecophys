# Paper G unknown-channel exact benchmark (v4)

Deterministic synthetic development checks, completed 2026-09-08. No market data,
simulation trajectories, confirmation, GPU computation or Paper E/F inputs.
The reduced search formulation is closed for independent-paper novelty; the exact
theorem and reproducible benchmark remain useful.

- Formal result and proof: `papers/proposal/ecomd_paper_g_recovery_search_result_2026-09-08.md`.
- `source_bundle.tar.gz` freezes 17 source/test/config/contract files and their
  `input_manifest.json`; Git base alone does not identify these uncommitted sources.
- `results/result.json`: 36 rational cells (12,285 policy sequences), including
  30 minimax LPs; 18 Bayesian DPs; all 72 scaling cells. No filtered runs.
- `results/receipt_sha256.json` and `verification_receipt.json`: source/result integrity.
- `scaling_cells.csv`: all reported scaling values.
- `render_summary.py` / `recovery_search_boundary.png`: presentation made after
  computation, plotting only frozen values at the explicitly labelled alpha=0.5.

Reproduce in an authorized Conda environment after unpacking the source bundle:

```sh
conda run -n ecophys python -m ecomd.paper_g.recovery_search --config configs/paper_g/recovery_search_v4.yaml --manifest input_manifest.json --output fresh_results
```

Execution used the existing V100 worker's CPU, 3.132216 seconds for the audit.
The machine decision caps further work and does not authorize larger experiments.
Implementation qualification records are private and supply no scientific claim.
