# Paper G development pilot v1

**Development only; not confirmatory evidence or a novelty claim.**

One predeclared parameterization: Q=2, initial inventory 1, balanced customer flow,
willingness probabilities 0.55/0.55, T=1024. Eight seeds, two feedback levels,
two replenishment probabilities and two learners give 64 runs/65,536 dealer rounds.

`config.yaml` and `input_manifest.json` were fixed before simulator outcomes. The
manifest identifies the base Git commit plus the exact added source files; the
complete source snapshot is `source_bundle.tar.gz`.

- `results.json`: every run, its objective, reference value, timing and learner state.
- `*.csv.gz`: compact per-round audit records. The `audit_willingness` column is
  evaluator truth, not input to the actual-feedback learner. Its projected feedback
  is specified in the frozen source/config.
- `summary.json` / `cell_summary.csv`: cell means, paired interaction and descriptive
  t intervals across the eight independent seed roots.
- `development_summary.png`: development-labelled visualization.
- `oracle_values.json`: same-feasible known-law finite-horizon reference values.
- `receipt_sha256.json`: original run artifacts; `local_artifact_sha256.json` additionally
  covers retrieved analysis and documentation, excluding itself.

The full pilot took 6.964 seconds of runner wall time and 26.679 summed job CPU
seconds on the recorded host; these exclude setup, testing, transfer and analysis.
Peak reported worker RSS was 36.48 MiB. They do not forecast the larger-Q/longer-horizon
or additional-baseline campaign. W&B was disabled; local receipts are canonical.

Neither learner's feedback-by-recovery interaction interval excludes zero. One
capacity, one regime and a short development horizon cannot establish minimax rates,
algorithm-independent barriers, real-market profitability or a publication claim.
This is not the separately planned 12-seed precision pilot, and it does not select
the confirmation sample size.

Private reference qualification and operational interpretation are in
`logs/private/paper_g_development_20260908/` and the internal review note. They are
not scientific evidence for a public paper. No formal confirmation run is started.
