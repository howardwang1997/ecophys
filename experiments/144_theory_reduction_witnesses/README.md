# Experiment 144 runbook

This is a completed data-free negative-control experiment for the theory search. It verified two hand-computable
fixtures and cannot admit a candidate or unlock data/GPU work. The immutable formal decision is
`NEGATIVE_CONTROLS_CONFIRMED`; see `RESULTS.md`.

The preregistration and configuration were committed before the runner existed. `FREEZE.yaml` records the permitted
implementation SHA. The formal command retained below is provenance only and must not be rerun because the runner
refuses to overwrite the raw artifact:

```bash
conda run -n ecophys python experiments/144_theory_reduction_witnesses/run_witnesses.py \
  --config experiments/144_theory_reduction_witnesses/config.yaml \
  --freeze experiments/144_theory_reduction_witnesses/FREEZE.yaml \
  --output experiments/144_theory_reduction_witnesses/artifacts/raw/witnesses.json
```

Do not rerun or overwrite the raw artifact.
