# Paper G M0 — completed development resolution

**704 trajectories, 2,097,152 dealer opportunities; development evidence only.**
The current M0 independent-paper novelty formulation is closed. The simulator,
exact reference and customer-only information probe remain reusable. See the
[formal result](../../../papers/proposal/ecomd_paper_g_m0_resolution_result_2026-09-08.md)
for the theorem's scope, all eight learning contrasts and the research decision.

- `audit/`: eight exact finite-horizon cells and the prospective learning-gate result.
- `probe/`: 192 paired trajectories summarized by law, root and replenishment arm.
- `learning/`: 512 per-run JSON records and compressed event trajectories, grouped
  by capacity/horizon, plus the aggregate result.
- `summary.json`, `learning_cells.csv`, `probe_summary.csv`, `resolution_summary.png`:
  descriptive analysis, retaining every specified configuration.
- `source_bundle.tar.gz`, `input_manifest.json`: the exact pre-outcome 12-file
  implementation/config/contract bundle over the recorded Git base. The Git SHA
  alone does not contain the newly added source.
- `analyze_resolution_snapshot.py`, `verification_receipt.json`: separately pinned
  post-outcome analysis code, output hashes and completed integrity checks.

Each phase has its own config, source manifest, file hashes and completion marker.
Keep the snapshot intact. Reproduction uses a fresh directory extracted from the
source bundle, the recorded Conda dependencies and single-thread BLAS settings.
The phase entry point is `conda run -n ecophys python -m ecomd.paper_g.resolve`;
run `audit`, then `probe`, then conditionally `learn` with
`--config configs/paper_g/resolution_v2.yaml --manifest input_manifest.json` and
separate `--output` directories. The learning phase additionally requires
`--audit <audit-directory>/audit.json`. Install the analysis snapshot as
`ecomd/paper_g/analyze_resolution.py` and run
`conda run -n ecophys python -m ecomd.paper_g.analyze_resolution <phase-root>`.
This describes reproducibility; it does not initiate or reauthorize another campaign.

All data are generated from the declared synthetic law and fixed seed partitions;
there is no external dataset, held-out real-market test or E/F dependency. Reusing
these seeds reproduces development data and cannot constitute independent
confirmation. Intervals are descriptive across independent roots, paired across
treatment arms. No empirical minimax or real-market profitability claim follows.
