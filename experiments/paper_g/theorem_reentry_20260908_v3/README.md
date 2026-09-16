# Paper G theorem re-entry — deterministic development results

The PI-authorized audit is complete: 101,376 exhaustive event cases, 96 M0
dynamic-programming cells and ten access-gate cells (four reported horizons).
There are no sampled learner trajectories or confirmatory observations in this
bundle. Uniform conclusions rely on the analytic proof, not finite-grid coverage.

See the [theory result](../../../papers/proposal/ecomd_paper_g_reentry_theory_result_2026-09-08.md)
and [prospective contract](../../../papers/proposal/ecomd_paper_g_reentry_theorem_contract_2026-09-08.md).
The later transfer and explore-then-plan learning corollaries are mathematical
derivations, not part of the frozen computational campaign.

- `results/result.json`: every specified cell and the complete event-count receipt.
- `results/config.yaml`, `results/input_manifest.json`, `results/receipt_sha256.json`:
  frozen inputs and output hashes; `results/COMPLETE` marks successful completion.
- `source_bundle.tar.gz`: exact executed source/config/contract bytes, including
  their manifest; the base Git SHA alone does not identify the uncommitted additions.
- `verification_receipt.json`: source/output integrity checks after retrieval.
- `render_summary.py`, the two CSVs and `theorem_boundary.png`: post-computation
  presentation of all frozen cells; neither the figure nor the tests certify novelty.

For reproduction, extract the source bundle to a fresh directory. Use the recorded
Conda dependencies and one BLAS thread, then run the entry point
`conda run -n ecophys python -m ecomd.paper_g.theorem_audit` with
`--config configs/paper_g/theorem_reentry_v3.yaml --manifest input_manifest.json
--output results`. The existing output directory must not be overwritten. The
configured seed is a provenance field only; all computations are deterministic.
