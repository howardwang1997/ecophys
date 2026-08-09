# Anonymous audit artifact

This artifact accompanies the double-blind Sim2Science submission “Is Simulator Fidelity an
Initialization Transient?” It is scoped to reproducing the paper’s audit, not to releasing the
broader EcoMD simulator.

It contains:

- the frozen synthetic calibration and held-out trajectories used in every learned-model result;
- analytic-control, stationarity-gate, stylized-fact, bootstrap, and figure code;
- frozen protocol records, seed manifests, exact simulator configurations, provenance, and hashes;
- the manuscript’s complete mathematical specification of the EcoMD snapshot; and
- tests for the bundled audit code.

It intentionally does **not** contain EcoMD’s core simulator/training implementation, raw market
files, learned checkpoint binaries, or repository history. Consequently, reviewers can recompute
every table, effect, interval, and figure reported in the paper from the frozen trajectories, but
cannot retrain a checkpoint or regenerate those trajectories from this bundle. This boundary is
stated in Appendix B of the paper; a separate model paper and software release are required for the
full EcoMD method.

The market-data inputs are documented in
`experiments/127_workshop_claim_gates/DATA_SNAPSHOT.json`. Daily SPX, NDX, GLD, and EUR/USD
observations came from Yahoo Finance; BTC/USDT one-minute klines came from Binance Data Vision. The
snapshot records date ranges, schemas, byte counts, and aggregate SHA-256 values.

## Integrity

`ARTIFACT_MANIFEST.json` lists the SHA-256 and byte count of every packaged file and declares the
release scope in machine-readable fields. Source Git and machine identifiers are replaced in text
files to preserve double blindness. Numerical arrays, configurations, seeds, and estimates are not
altered.

## Environment

```bash
conda env create -f environment_cpu.yml
conda run -n sim2science-cpu pip install -e .
```

The original learned-model execution used Python 3.11.15, PyTorch 2.3.1+cu121, FP32, and one 32 GiB
V100 per independent worker: 19.90 GPU-hours for ten training runs and 34.51 GPU-hours for 320
formal learned rollouts. No GPU dependency is needed to rerun the bundled audit.

## Fast verification

```bash
conda run -n sim2science-cpu pytest -q
conda run -n sim2science-cpu python \
  experiments/127_workshop_claim_gates/analyze_learned_results.py \
  --artifact-root derived \
  --gate-fits experiments/127_workshop_claim_gates/LEARNED_GATE_FITS.json \
  --output /tmp/learned_results_recomputed.json \
  --workers 4 --allow-dirty
conda run -n sim2science-cpu python \
  experiments/127_workshop_claim_gates/analyze_learned_robustness.py \
  --input /tmp/learned_results_recomputed.json \
  --artifact-root derived \
  --output /tmp/learned_robustness_recomputed.json
```

Compare numerical payloads with `LEARNED_RESULTS.json` and `LEARNED_ROBUSTNESS.json`. Provenance
fields referring to the review snapshot may differ from the original source-tree record. A missing
gate is an outcome, not an excluded checkpoint, and both Hill estimates use 4,000 returns.

To refit the gates without violating the staged protocol, first create a temporary artifact root
containing only `derived/rollouts/calibration`; run `fit_learned_calibration.py` there before exposing
the held-out directory. The archived gate file’s timestamp and hash show that this was the order used
for the formal run.

## Scope

This artifact supports a simulator-audit claim. It does not establish real-market physics,
universal stationarity detection, mixing, ergodicity, model validity, deployment safety, or financial
risk certification.
