# Experiment 142 runbook

Experiment 142 validates the Plan v4 G0 candidate-admission process using generated fixtures only. It is not an
estimator benchmark and contains no real candidate.

The planning commit is `fd99b1262`; the contract implementation commit is `f33db765f`. The preregistration,
fixture and runner must be committed and pushed before the formal command runs. The runner refuses a dirty checkout
and an existing output path.

```bash
conda run -n ecophys python experiments/142_ncs_g0_reentry_contract/run_contract.py \
  --output /private/tmp/exp142_contract_validation.json
```

No market file, network service or GPU is used. A PASS validates only exact process behavior. It leaves Plan v4 G0
at FAIL and cannot authorize candidate code, data purchase or compute expansion.
