# EcoPhys / EcoMD

EcoMD is research software for differentiable, stochastic, molecular-dynamics-style
multi-agent market simulation.

> **Pre-release status.** The simulator source is under active validation. There is
> currently no endorsed EcoMD model checkpoint, no claim that its latent dynamics are
> real market physics, and no claim of order-level execution fidelity. Historical
> checkpoints were trained under an incomplete state-continuation contract and are not
> release candidates.

## What is implemented

- Langevin-style multi-agent dynamics with learned stochastic interactions;
- differentiable rollout and moment-based calibration infrastructure;
- a versioned `SimulatorState` that carries recurrent, price, integrator, neighbour-cache,
  shock, clock, and RNG state across chunks and checkpoints;
- aggregate-bin observation operators and explicit semantic-contract tests;
- stationarity and stylized-fact diagnostics, baselines, and experiment provenance.

The repository also contains historical architectures and experiments. Their presence is
not evidence that they belong to the release model. In particular, MACE/equivariant,
universal heavy-tail, crash-precursor, and real-market-physics claims are not active claims.

## Current decision gates

The simulator-audit paper route failed its prior-art novelty gate. EcoMD work is therefore
focused on a narrower sequence:

1. produce a source-only research preview with synthetic smoke tests and no raw market data;
2. freeze one state-complete model specification and retrain from scratch;
3. require post-stationarity, time-out-of-sample fidelity before releasing a checkpoint or
   drafting a positive model-paper claim;
4. add strong baselines, ablations, generalization, gradient-utility, and scaling evidence.

See the [release scope](papers/proposal/ecomd_v1_release_scope_2026-08-10.md), the
[model-paper plan](papers/proposal/ecomd_model_paper_release_plan_2026-08-09.md), and the
[research-preview contract](docs/ecomd_research_preview_contract.md).

## CPU quick start

```bash
conda create -n ecophys python=3.11 -y
conda run -n ecophys pip install -e ".[dev]"
conda run -n ecophys python examples/ecomd_cpu_smoke.py
conda run -n ecophys python -m pytest tests/test_ecomd_smoke.py \
  tests/test_simulator_state.py tests/test_release_contract.py -q
```

The smoke path generates synthetic trajectories and downloads no data. New production
training is not launched until the release configuration passes the versioned training
contract. CPU validation comes first; the available V100 32 GB cards are reserved for the
subsequent frozen single-card reference run. H20 is not part of the forward compute plan.

## Data boundary

No raw Yahoo Finance, LOBSTER, or Binance files are part of the planned public release.
The historical `data/sample/` cache is research-internal pending redistribution review.
Public artifacts use generated synthetic inputs plus acquisition instructions and hashes
for data users obtain under their own terms. See [`data/sample/README.md`](data/sample/README.md).

## Repository layout

```text
ecomd/          simulator, training, observation, evaluation, and baseline code
experiments/    immutable experiment protocols and results
tests/          unit, semantic-contract, and exact-resume tests
examples/       data-free executable examples
docs/           release-facing technical contracts
papers/         paper drafts, proposal gates, and release plans
scripts/        current utilities plus clearly marked historical launch scripts
logs/           dated research work log
```

## License

Source code is licensed under the [MIT License](LICENSE). Dataset licenses and rights are
separate from the code license.
