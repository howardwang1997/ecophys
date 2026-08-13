# Experiment 152 runbook

This experiment is the completed deterministic obstruction suite for V11. It checks exact identities and failure
modes only; it cannot pass novelty, admit a candidate or unlock data/GPU work.

Chronology at implementation time:

- Plan freeze: `df75a5c0166bbb7e933bdb0692a536cd8680c983`.
- Preregistration: `4b899285b`.
- Implementation: `aa5f90ba039c7cb4258be12d6d6f8a476ce61eea`.
- Implementation freeze: `0ab9cba6594b1354447aa28e1f5e8cccce91b4a4`; `FREEZE.yaml` pins all four executable inputs.
- Formal result: `IDENTITY_AND_OBSTRUCTIONS_CONFIRMED` from the sole formal run at the clean freeze commit.
- Raw result SHA-256: `ee08eb70ed8551c8b7ff8cd8e98d9e93cda1a50ce1d1419be2210f0718a5862a`.

The command below is preserved for provenance. It has already been executed exactly once and must not be run
again because the immutable raw artifact exists:

```bash
conda run -n ecophys python experiments/152_multi_stationary_drift_tomography/run_exact_audit.py \
  --config experiments/152_multi_stationary_drift_tomography/config.yaml \
  --freeze experiments/152_multi_stationary_drift_tomography/FREEZE.yaml \
  --output experiments/152_multi_stationary_drift_tomography/artifacts/raw/exact_audit.json
```

See `RESULTS.md` and `artifacts/RAW_MANIFEST.yaml`. Do not rerun or overwrite Experiment 152; any repair requires a
new experiment number.
