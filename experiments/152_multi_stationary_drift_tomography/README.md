# Experiment 152 runbook

This experiment is an unexecuted deterministic obstruction suite for V11. It checks exact identities and failure
modes only; it cannot pass novelty, admit a candidate or unlock data/GPU work.

Chronology at implementation time:

- Plan freeze: `df75a5c0166bbb7e933bdb0692a536cd8680c983`.
- Preregistration: `4b899285b`.
- Implementation freeze and formal result: not yet created.

The formal command below is forbidden until a committed `FREEZE.yaml` records the implementation SHA and exact
file hashes:

```bash
conda run -n ecophys python experiments/152_multi_stationary_drift_tomography/run_exact_audit.py \
  --config experiments/152_multi_stationary_drift_tomography/config.yaml \
  --freeze experiments/152_multi_stationary_drift_tomography/FREEZE.yaml \
  --output experiments/152_multi_stationary_drift_tomography/artifacts/raw/exact_audit.json
```

Do not invoke the formal runner before the freeze or rerun it after the raw artifact exists.
