# Experiment 141 runbook

Experiment 141 is the generated-data feasibility gate for Plan v5. It tests implementation correctness,
single-clock identifiability, deliberate two-clock misspecification, confound rejection and bounded execution on
the currently authorized non-H20 workers. It is not a market-data experiment.

## Ownership boundary

The execution order is binding:

1. `PREREGISTRATION.md` and the YAML configuration were committed as `613a14f26` before implementation.
2. All implementation, tests and runners are committed and pushed before development fitting.
3. `fit_development.py` reads only seeds 100--115 and magnitudes 0.5, 1.0 and 1.5. Its JSON artifact is committed
   before any seed at or above 10,000 is generated.
4. Formal shards run from that unchanged research-code hash. Each host writes outside its Git checkout.
5. Raw JSON artifacts are copied back without transformation, checksummed and merged once.

Changing scientific code or configuration after step 3 invalidates exp141. A repair uses a new experiment number
and fresh seeds.

## Machine allocation

| Worker | Host | Formal shard | Isolated checkout | Conda environment | Artifact root |
|---|---|---:|---|---|---|
| V100-A | `100.80.236.112` | 0 | `/data/ecophys_imwm_v1_a` | `/data/ecophys_workshop/conda_env` | `/data/exp141_imwm_v1/a` |
| V100-B | `100.123.220.57` | 1 | `/data/ecophys_imwm_v1_b` | `/data/ecophys_workshop/conda_env` | `/data/exp141_imwm_v1/b` |
| RTX2060 | `100.105.21.7` | 2 | `/home/howardwang/ecophys_imwm_v1` | isolated `ecophys-imwm` clone | `/home/howardwang/exp141_imwm_v1/rtx2060` |

The RTX worker's historical `/home/howardwang/ecophys` checkout is out of scope and must remain untouched. The
V100 launch guard must confirm the Graphene monitor still reports idle, the held release marker is absent, no
compute PID exists and GPU utilization is low in the same shell that starts the job.

## Commands

From a clean implementation commit, freeze development parameters on the Mac:

```bash
conda run -n ecophys python experiments/141_multiclock_intervention_feasibility/fit_development.py \
  --output experiments/141_multiclock_intervention_feasibility/development_fit.json
```

After committing that JSON, each worker runs one shard and one CUDA probe:

```bash
conda run -n ecophys python experiments/141_multiclock_intervention_feasibility/run_shard.py \
  --shard 0 \
  --fit experiments/141_multiclock_intervention_feasibility/development_fit.json \
  --output /absolute/artifact/root/shard_0.json

conda run -n ecophys python experiments/141_multiclock_intervention_feasibility/run_hardware_probe.py \
  --worker v100-a \
  --output /absolute/artifact/root/hardware_v100_a.json
```

The worker name and shard index change according to the allocation table. V100 packed environments use
`conda run -p /data/ecophys_workshop/conda_env`; the RTX worker uses its isolated named environment.

After retrieving the six immutable raw artifacts, merge them locally:

```bash
conda run -n ecophys python experiments/141_multiclock_intervention_feasibility/merge_results.py \
  --fit experiments/141_multiclock_intervention_feasibility/development_fit.json \
  --shards artifacts/exp141/raw/shard_0.json artifacts/exp141/raw/shard_1.json \
    artifacts/exp141/raw/shard_2.json \
  --output artifacts/exp141/derived/scientific_merge.json

conda run -n ecophys python experiments/141_multiclock_intervention_feasibility/merge_hardware.py \
  --probes artifacts/exp141/raw/hardware_v100_a.json artifacts/exp141/raw/hardware_v100_b.json \
    artifacts/exp141/raw/hardware_rtx2060.json \
  --output artifacts/exp141/derived/hardware_merge.json
```

The raw artifacts are generated data, not source data. Git stores their checksum inventory and compact derived
results; bulk or intermediate event streams remain outside Git. No existing LOBSTER, Binance, daily or crash file
is read by these runners.
