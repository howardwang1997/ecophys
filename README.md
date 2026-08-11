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

EcoMD v1 failed its stationary-fidelity gate, the invariant-calibration route failed its
novelty gate, and the real-market thermodynamic hypotheses failed their empirical or
identifiability gates. These failures remain binding.

The active Plan v5 feasibility branch asks a different question: can a model with an exact
exchange mechanism, learned event behavior, slower behavioral adaptation and explicit
institutional interventions predict a sealed market-rule change? Initial work is generated
data only and carries no positive market claim. See the [Plan v5 proposal](papers/proposal/plan_v5_interventional_market_world.md),
[research lineage](docs/research_lineage.md), and [experiment 141 preregistration](experiments/141_multiclock_intervention_feasibility/PREREGISTRATION.md).

The EcoMD source-preview boundary is unchanged; see the [release scope](papers/proposal/ecomd_v1_release_scope_2026-08-10.md)
and [research-preview contract](docs/ecomd_research_preview_contract.md).

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

New Plan v5 components live under `ecomd/market_world/`; their presence does not turn
historical EcoMD checkpoints into validated market-world models.

## License

Source code is licensed under the [MIT License](LICENSE). Dataset licenses and rights are
separate from the code license.
