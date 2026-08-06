# Anonymous reproducibility artifact

This artifact accompanies the double-blind Sim2Science submission "Is Simulator Fidelity an
Initialization Transient?" It contains the frozen protocol, estimator code, analytic controls,
learned-model analysis, exact configurations and seeds, paper figure code, and tests. It contains no
raw market data and no author-identifying repository history.

The public-data inputs are described by `experiments/127_workshop_claim_gates/DATA_SNAPSHOT.json`.
Daily SPX, NDX, GLD, and EUR/USD observations come from Yahoo Finance; BTC/USDT one-minute klines
come from Binance Data Vision. The snapshot records date ranges, schemas, byte counts, and aggregate
SHA-256 values. Reviewers can verify the analysis from the bundled synthetic trajectories without
redistributing those source files; retraining additionally requires recreating the hashed inputs.

## Integrity

`ARTIFACT_MANIFEST.json` lists the SHA-256 and byte count of every packaged file. Source Git commit
identifiers and machine identifiers are replaced in the review copy to preserve double blindness.
This does not change executable code, numerical arrays, configurations, seeds, checkpoints, or
reported estimates. The manifest cryptographically covers the exact review snapshot.

## Environment

For the CPU analytic controls:

```bash
conda env create -f environment_cpu.yml
conda run -n sim2science-cpu pip install -e .
```

For V100 reproduction, use `environment_v100.yml`. The original execution used Python 3.11.15,
PyTorch 2.3.1+cu121, CUDA 12.1, FP32, and one 32 GiB V100 per worker. The two workers are independent;
this is not a multi-node distributed job.

## Fast verification

```bash
conda run -n sim2science-cpu pytest -q tests/test_stationarity_gate.py \
  tests/test_stationarity_baselines.py tests/test_exp127_analytic_controls.py \
  tests/test_exp127_fit_learned_calibration.py tests/test_exp127_analyze_learned.py \
  tests/test_sim2science_figures.py
conda run -n sim2science-cpu python experiments/127_workshop_claim_gates/run_analytic_controls.py \
  --help
```

The archived `ANALYTIC_RESULTS.json` can be checked immediately. Regenerating all seven analytic
conditions requires 7,000 trajectories of 8,000 returns and is intentionally separate from this
fast verification. The full-source `test_exp127_v100_worker.py` also validates the frozen raw-data
hashes, so it is intentionally not bundled with this no-raw-data review artifact.

## Learned-model audit

The bundled learned trajectories are synthetic simulator outputs, split into calibration and held-out
directories by the frozen seed manifest. The order is binding:

1. Fit calibration-only gates with `fit_learned_calibration.py`.
2. Verify the resulting gate-file SHA-256 against the artifact manifest.
3. Analyze held-out trajectories with `analyze_learned_results.py`.
4. Regenerate figures with
   `papers/paper_a_methods/workshops/sim2science/make_figures.py`.

Exact commands and expected hashes are recorded in the final `RESULTS.md`. A missing gate is an
outcome, not an excluded checkpoint. Both Hill estimates always use 4,000 returns.

## Scope

This artifact supports a model-audit claim. It does not establish real-market physics, universal
stationarity detection, mixing, or ergodicity. Passing the gate is not a deployment or financial-risk
certificate.
