# EcoPhys / EcoMD

**A differentiable molecular-dynamics-style simulator for financial markets.**

> Research program: apply statistical-mechanics and ML-force-field methods (MACE/NequIP-family equivariant GNNs) to large-scale agent-based market simulation. Agents are "particles" in latent feature space; dynamics are Langevin; interaction potentials are learned end-to-end from real market data.

**Current strategy (plan v3 + Path C, 2026-04-24)**: Paper B targets **Nature Physics flagship** (15–22% joint probability) with three pre-registered "one-line laws": A1 (T_eff critical scaling on ≥3 timescales), B2 (Jarzynski with FOMC/earnings intraday protocol), B3 (TUR saturation at L2 event-level). Paper A (NeurIPS/ICML main), Paper B.5 (PRL, TUR), and Paper C (QF/JEDC, applications) are guaranteed retreat outputs.

**Full plan**: [`papers/proposal/plan_v3.md`](papers/proposal/plan_v3.md). Earlier versions
[`plan_v1.md`](papers/proposal/plan_v1.md) and [`plan_v2.md`](papers/proposal/plan_v2.md) kept
for history; they are **superseded** and should not be used for current decisions.

## Status

Phase 2 → Phase 3 transition (Wk 17). EcoMD v0 → v0.5 → v0.6 → v1 (MACE-lite) built
on Mac, distributed H20 training scripts ready. Next: high-frequency data procurement
(Wk 17–18) + first H20 production run.

| Version | Stylized facts hit | Status |
|---|---|---|
| v0 smoke / v0.5 / v0.6 / v1 Mac | 5 / 5 / 6 / 6 / 11 | committed |
| v1 H20 production | (target ≥ 7/11 for M2, ≥ 9/11 for M3) | pending user run |
| v1+ H20 (MACE + v0.6 improvements) | (target ≥ 9/11) | pending user run |

## Repository layout

```
ecophys/
├── CLAUDE.md                    # project instructions for Claude Code
├── .claude/                     # project-local Claude config + memory
│   ├── memory/                  # long-term research memory (in-repo, symlinked)
│   └── README.md                # memory layout explanation
├── pyproject.toml               # conda env name: ecophys, Python 3.11
├── ecomd/                       # core package
│   ├── data/                    # data pipelines (yfinance, Binance, LOBSTER, R2 sync)
│   ├── models/                  # EcoMD architecture (potentials, MACE-lite, price formation)
│   ├── physics/                 # Langevin integrator, trajectory observables
│   ├── training/                # loss fns + local + distributed training loops
│   ├── inference/               # multi-rank long-rollout evaluation
│   ├── eval/                    # Cont 2001 stylized-facts suite (11 metrics)
│   └── baselines/               # Lux-Marchesi 1999, GARCH(1,1)-t
├── experiments/                 # one dir per experiment: config.yaml + run.py + results/
├── data/sample/                 # curated samples in git (SPY, ^GSPC, BTC/ETH, LOBSTER)
├── scripts/                     # H20 launch + inference + R2 push scripts
├── logs/                        # dated work logs (YYYY-MM-DD.md)
├── papers/                      # LaTeX drafts + proposals (plan_v1/v2/v3)
└── references/                  # literature notes
```

## Setup

```bash
conda create -n ecophys python=3.11 -y
conda activate ecophys
pip install -e ".[dev]"
# Optional physics extras:
pip install -e ".[physics]"
```

Then verify:
```bash
conda run -n ecophys python -m pytest tests/ -q   # 135 tests should pass
```

## Workflow

- **Mac local**: code editing, tests, small smoke training (N ≤ 500). 
- **Cloudflare R2** (`r2://ecophys/...`): transit + offsite backup; canonical bulk data.
- **GitHub**: canonical code store.
- **8×H20 NVLink remote**: all production training + inference.

H20 launch scripts live in `scripts/`; see [`scripts/README.md`](scripts/README.md) for the full
invocation sequence. Claude Code sessions work on Mac only — H20 commands are handed
back to the user to run via SSH.

Run `conda run -n ecophys python ...` for any Python commands (conda-only policy per global CLAUDE.md).

## License

See `LICENSE`.
