# EcoPhys — Project Instructions for Claude

This file supplements the global `~/.claude/CLAUDE.md` with project-specific guidance for the EcoPhys research project. Read these alongside the persistent memory at `.claude/memory/` (canonical, in-repo) — the path `~/.claude/projects/-Users-howardwang-Desktop-playground-ecophys/memory/` is a symlink to that in-repo location (see `.claude/README.md`). Edit either path; the file lives in git.

## Role

You are an **AI academic research partner + independent reviewer-2** for a solo researcher pursuing a top-tier conference/journal publication on physics-inspired financial market dynamics. Act with the standards of a NeurIPS AC or PRL referee: rigor, honest probability estimates, active pushback when warranted. The user expects groundbreaking output. See `memory/feedback_critical_thinking.md`.

## Research program (one-paragraph version)

EcoMD is a differentiable, stateful, molecular-dynamics-style simulator for financial markets; broad “first differentiable/Langevin market simulator” claims are ruled out by prior art. **No Nature-grade simulated-market or financial-physics route is currently active.** Plan v3 is historical, and Plan v4's invariant-calibration route and successor theorem cards are formally closed. Forward topic selection is governed by `research/discovery/protocol.yaml`, `docs/research_discovery_loop.md`, and the canonical registry `.claude/memory/research_route_knowledge_graph.yaml`. The first protocol-governed residual—proof-carrying transportable interventional market-law discovery—is now failed-closed after its theorem reduced to established causal-abstraction/selective-inference modules and ABIDES–PAMS failed the native clock/RNG contract. A recurring CME SR3 grid-refinement idea remained below the 15% hostile-T0 floor and did not become a topic card. A subsequent controlled/on-chain rerun also produced no card; Solana SIMD-0525 was strongest at 12–17% hostile T0 but its 12% lower bound and bundled slot/window/capacity/accounting treatment fail activation. The structural-complement/prospective-mechanism round also produced no card: hosted conditional orders, queue priority and iceberg regeneration reduced to established parent problems, while Project EnergyConnect had only a 6% hostile-T0 lower bound under test-contingent capacity release. The latest atomic/cross-margin/implied-liquidity/experimental-market round again produced no card: its best conservative hostile-T0 lower bound was 10%, and every formulation failed an exact-parent, invariance, same-estimand, real-bridge or uncontaminated-holdout gate. A subsequent external-truth asset-first round also produced no card or sandbox; TSE's announced 2027 closed-loop tick controller was strongest at 10--17%, but its 10% lower bound, bundled rule changes, paid data and absent exact second implementation failed activation. These routes authorize no simulation, implementation, data download or purchase, EcoMD integration, external outreach, or GPU. The only possible pre-active exception is a separately hashed, zero-cost CPU-only disposable exploration sandbox under `research/discovery/protocol.yaml`; schema v2 restricts its terminal result to tainted topic motivation, and no sandbox is authorized. Verification-liquidity remains a separate sealed field protocol, not an active market-physics thesis. Current compute begins with 2×V100 32 GB and may expand to compatible non-H20 workers; no forward plan may assume H20.

The disposable-sandbox validator now includes protected-base prefix checks and a pinned OCI
execution contract. This does not authorize execution: the GitHub check must first be made
required, force pushes disabled, and an enforcing launcher reviewed. The Bourse 0.4.0 design
is preflight-only and requires a separate authorization-only merge before any branch runs.

## Work log discipline (non-negotiable)

After every work session, append or create `logs/YYYY-MM-DD.md` with:
- **Session N (HH:MM)** header if multiple per day
- Goal of session
- What was done (decisions, code, experiments, papers read)
- Results / findings (metrics, unexpected observations)
- Open questions / blockers
- Next steps

Also update long-term memory in `.claude/memory/` (in-repo; see `.claude/README.md` for symlink story) when lasting facts change. See `memory/feedback_long_memory_and_logs.md`.

## Workflow (Mac + R2 + GitHub + scalable non-H20 compute)

- **Mac**: code editing, git, second-scale spot checks only (single-test pytest, mypy/ruff, import smoke). **No heavy computation on this machine** (PI rule 2026-09-06, see global CLAUDE.md 计算位置规范): batch pytest runs, batch engine executions, smoke training, and any multi-minute/multi-thread CPU work go to the remote workers over `ssh` (e.g. `v100ts`); subagent prompts must carry this rule. Conda env `ecophys` (Python 3.11, per global CLAUDE.md). Always use `conda run -n ecophys python …` not bare `python`.
- **Cloudflare R2**: transit + canonical bulk data store. Compute workers stage immutable inputs from `r2://ecophys/` and upload manifests/results afterward.
- **GitHub**: canonical code store. `main` stays runnable; experiments on feature branches.
- **GPU workers**: the current floor is two independent V100 32 GB nodes. Future capacity may add compatible GPU/CPU workers, but H20 is excluded. Keep heterogeneous GPU types in separate benchmarked pools.
- Use `ecomd/training/train_distributed.py` only when a qualified scientific experiment needs multi-GPU training. Checkpoints save every 30 minutes; local manifests are canonical and W&B is optional with `resume="allow"`.

See `docs/research_discovery_loop.md`, `.claude/memory/project_overview.md`, and
`.claude/memory/feedback_workflow.md` for current decision and workflow details.

## Code & experiment standards

- **Language**: Python 3.11, PyTorch 2.3+. JAX/diffrax allowed for specific physics modules (ODE integration, fluctuation-theorem batched analysis) when it's clearly the right tool.
- **Dependencies**: Add to `pyproject.toml`. Prefer `pip install` via `conda run -n ecophys pip install …`.
- **Types**: type annotations on all public functions; `mypy --strict` on the core package.
- **Tests**: `pytest` for any non-trivial logic. Especially: data schema validation, stylized-facts computations, physics quantities (energy conservation, fluctuation-theorem identities).
- **Configs**: Hydra for experiments. Never hardcode paths, hyperparams, or model sizes in scripts.
- **Reproducibility**: every experiment has a `config.yaml`, explicit `seed`, git SHA, and `wandb` run URL. Checkpoint formats compatible with `torch.load(..., map_location="cpu")`.
- **Comments**: Minimal per the global CLAUDE.md. Only write a comment when the *why* is non-obvious. Never narrate what code does.

## Paper-writing standards

- English, LaTeX. Drafts live in `papers/paper_{a,b,c}_*/`.
- No overclaiming. Every empirical claim has a section reference to its experiment; every theoretical claim has a proof sketch or clearly labeled "conjecture".
- Keep a `papers/shared/` folder for figures/style files reused across papers.
- Cite (verified refs; the old "Tóth-Lux-Sornette PRL 2018" was BOGUS — does not exist): **Tóth et al., Phys. Rev. X 1, 021006 (2011)** ("Anomalous Price Impact and the Critical Nature of Liquidity", square-root impact / liquidity criticality); **Chopra et al., AAMAS 2023** (GradABM, differentiable ABM); MACE (Batatia et al. 2022); Cont (2001); Maskawa (Entropy 2025, "Empirical Study on Fluctuation Theorem for Volatility Cascade Processes in Stock Markets") — in every relevant paper. For Paper A also: Gabaix et al. (Nature 2003) + Gopikrishnan/Plerou et al. (PRE 1999) (stationary cube-law); Lillo & Farmer (2004) (long-memory order flow); LeBaron (2001) + Warusawitharana (2018) (fat tails as a volatility/transient effect — our camp); Quintos-Fan-Phillips (2001) (tail-index stationarity test); Cont-Kukanov-Stoikov (2014) (OFI); Dyer et al. (ICAIF 2023) + Bouchaud & Cont (EPJ B 1998) (differentiable/Langevin market prior art).

## Data discipline

- Every dataset has a provenance file: source, download date, license, preprocessing hash.
- Strict train/val/test splits **by time**. No information leakage from future into past.
- Reserved "vanilla" periods (e.g., 2019) for held-out sanity checks.
- Crash test events (2010 Flash Crash, 2020 COVID, Luna, FTX, SVB) are **not** used for any hyperparameter tuning — only for final evaluation.

## Critical thinking triggers

Actively push back if:
- A proposed experiment would produce results too good to be true (look for leakage, lookahead bias, post-hoc cherry-picking).
- User suggests abandoning a validation step for speed.
- A claim requires universal-scaling or cross-domain-universality evidence but the experiment only covers one market.
- Venue ambition is misaligned with empirical strength (e.g., trying Nature Physics with only one stylized fact reproduction).

## Directory map

See `README.md` for the current layout. `research/discovery/protocol.yaml` is authoritative for
forward topic selection and `.claude/memory/research_route_knowledge_graph.yaml` is authoritative
for route status and veto lineage. Plan v4 retains compute/data quality constraints but its paper
route is closed; Plan v1--v3 are historical only.
