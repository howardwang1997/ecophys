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

Plan v4 is the current NCS plan of record, but its v0/v1 invariant-calibration construction remains
closed at G0: it reduced to known components and supplied no new coupling, weaker-assumption residual
theorem or variance--cost result. The active re-entry branch therefore starts with a theorem-first
candidate-admission contract, not another estimator implementation. It uses no market data or GPU and
cannot emit an automated novelty PASS. Exp142 preserved a process FAIL caused by inverted boolean aggregation;
the separately preregistered exp143 repair passed all ten process gates. No real candidate was present, so G0 and
the data/GPU locks are unchanged. See the [Plan v4 proposal](papers/proposal/plan_v4_ncs.md),
[G0 decision](papers/proposal/ncs_g0_forward_audit_2026-08-10.md), [re-entry plan](papers/proposal/plan_v4_g0_reentry_v1.md),
and [research lineage](docs/research_lineage.md).

Plan v5 and experiment 141 are independently archived feasibility context. Exp141 passed generated-data
mechanism, controlled-identifiability and cross-hardware gates, but its family-conditioned task is not
real-market or method evidence and is not promoted into Plan v4.

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

Plan v5 components under `ecomd/market_world/` and historical EcoMD checkpoints remain available as
archived research artifacts; their presence does not validate a market-world model or a Plan v4 method claim.

## License

Source code is licensed under the [MIT License](LICENSE). Dataset licenses and rights are
separate from the code license.
