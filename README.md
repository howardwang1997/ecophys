# EcoPhys / EcoMD

**A differentiable molecular-dynamics-style simulator for financial markets.**

> Research program: apply statistical-mechanics and ML-force-field methods (MACE/NequIP-family equivariant GNNs) to large-scale agent-based market simulation. Agents are "particles" in latent feature space; dynamics are Langevin; interaction potentials are learned end-to-end from real market data. Targets: NeurIPS/ICML main (methods), PRL/Nature Physics stretch (non-equilibrium thermodynamics of markets), QF/JEDC (applications).

Full research plan: [`papers/proposal/plan_v1.md`](papers/proposal/plan_v1.md).

## Status

Phase 0 — infrastructure setup + literature deep-read (Wk 1–4).

## Repository layout

```
ecophys/
├── CLAUDE.md                 # project instructions for Claude Code
├── .claude/                  # project-local Claude config
├── pyproject.toml            # conda env name: ecophys, Python 3.11
├── ecomd/                    # core package
│   ├── data/                 # data pipelines (yfinance, Binance, LOBSTER, S3 sync)
│   ├── models/               # EcoMD architecture (Langevin dynamics, equivariant GNN)
│   ├── training/             # training loops + losses
│   ├── physics/              # fluctuation theorems, entropy production, T_eff
│   ├── eval/                 # stylized-facts suite (Cont 2001 + distances)
│   └── baselines/            # ABIDES-lite, Lux-Marchesi, GARCH, LPPL
├── experiments/              # one dir per experiment: Hydra config + run + results
├── notebooks/                # exploratory analysis
├── logs/                     # dated work logs (YYYY-MM-DD.md)
├── papers/                   # LaTeX drafts (proposal, paper_a_methods, paper_b_physics, paper_c_finance)
└── references/               # literature notes + PDFs
```

## Setup

```bash
# Create conda env (per global CLAUDE.md, conda-only)
conda create -n ecophys python=3.11 -y
conda activate ecophys

# Install in dev mode
pip install -e ".[dev]"

# Optional: JAX + diffrax for certain physics modules
pip install -e ".[physics]"
```

## Workflow

- **Mac local**: small smoke tests, paper writing, data ingestion prototyping.
- **Cloudflare R2** (`r2://ecophys/...`): transit + offsite backup; H20 pulls from here into NFS.
- **GitHub**: canonical code store.
- **4×H20 remote**: all medium/large training runs.

Run `conda run -n ecophys python ...` for any Python commands (do not use bare `python`).

## License

See `LICENSE`.
