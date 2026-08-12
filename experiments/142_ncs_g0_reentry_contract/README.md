# Experiment 142 runbook

Experiment 142 attempted to validate the Plan v4 G0 candidate-admission process using generated fixtures only. The
formal result is `FAIL_PROCESS_VALIDATION`: every case-level outcome matched, but the aggregate decision incorrectly
treated the compliant observation `actual_market_data_read=false` as a failed boolean gate. The raw result remains
immutable; see `RESULTS.md`. It is not an estimator benchmark and contains no real candidate.

The planning commit is `fd99b1262`; the contract implementation commit is `f33db765f`; the frozen formal runner is
at `48db22ef2`. The command below is retained for provenance and must not be used to rerun exp142.

```bash
conda run -n ecophys python experiments/142_ncs_g0_reentry_contract/run_contract.py \
  --output /private/tmp/exp142_contract_validation.json
```

No market file, network service or GPU was used. The process FAIL leaves Plan v4 G0 at FAIL and cannot authorize
candidate code, data purchase or compute expansion. Any repair uses a new experiment number.
