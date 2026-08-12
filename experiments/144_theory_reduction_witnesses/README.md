# Experiment 144 runbook

This is a data-free negative-control experiment for the theory search. It verifies two hand-computable fixtures and
cannot admit a candidate or unlock data/GPU work.

The preregistration and configuration are committed before the runner exists. After implementation is committed,
`FREEZE.yaml` will record the permitted implementation SHA. The formal command will then be:

```bash
conda run -n ecophys python experiments/144_theory_reduction_witnesses/run_witnesses.py \
  --config experiments/144_theory_reduction_witnesses/config.yaml \
  --freeze experiments/144_theory_reduction_witnesses/FREEZE.yaml \
  --output experiments/144_theory_reduction_witnesses/artifacts/raw/witnesses.json
```

Do not run the formal command before the implementation freeze exists. Do not rerun or overwrite the raw artifact.
