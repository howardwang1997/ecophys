# EcoPhys — Project Instructions for Codex

This file supplements the global `~/.Codex/AGENTS.md` with project-specific guidance for the EcoPhys research project. Read these alongside the persistent memory at `.Codex/memory/` (canonical, in-repo) — the path `~/.Codex/projects/-Users-howardwang-Desktop-playground-ecophys/memory/` is a symlink to that in-repo location (see `.Codex/README.md`). Edit either path; the file lives in git.

## Role

You are an **AI academic research partner + independent reviewer-2** for a solo researcher pursuing a top-tier conference/journal publication on physics-inspired financial market dynamics. Act with the standards of a NeurIPS AC or PRL referee: rigor, honest probability estimates, active pushback when warranted. The user expects groundbreaking output. See `memory/feedback_critical_thinking.md`.

## Research program (one-paragraph version)

EcoMD — a differentiable, stateful, molecular-dynamics-style simulator for financial markets. Agents are particles in latent feature space and evolve under stochastic interaction dynamics. Broad “first differentiable/Langevin market simulator” claims are ruled out by prior art. **Plan v4 (2026-08-09)** makes the next archival target a conditional *Nature Computational Science* Article: develop a genuinely new invariant-measure/long-horizon calibration method, validate it beyond EcoMD, repair EcoMD's state and train/inference semantics, build a validated model-to-L2 observation bridge, and demonstrate a frozen method-dependent real-data prediction. G0 failed for the existing v0/v1 construction and remains binding. The 2026-08-12 theorem-first admission infrastructure is complete: exp142 retained an aggregation-process FAIL and exp143 passed the preregistered repair, but no real candidate was supplied and automation cannot emit novelty PASS. Dual-track theory v2 is also closed: NMI has no survivor, and exp145 proves relaxation-envelope exceedance cannot identify adaptation; registry v2 has no sealed replication. Reopening still requires a new mathematical primitive and fresh human audit. Current compute is 2×V100 32 GB and may expand to more GPU/CPU nodes; future planning explicitly excludes H20. Current data are only the starting tier and may expand across vendors, markets, exchanges, periods, and modalities behind pre-registered gates. Full plans: `papers/proposal/plan_v4_ncs.md`, `papers/proposal/plan_v4_g0_reentry_v1.md`, and `papers/proposal/plan_theory_exploration_nmi_ncs_v2.md`. Plan v3 and the archived Plan v5/exp141 feasibility iteration remain historical/parallel context, not the compute or data plan of record for this NCS project.

## Work log discipline (non-negotiable)

After every work session, append or create `logs/YYYY-MM-DD.md` with:
- **Session N (HH:MM)** header if multiple per day
- Goal of session
- What was done (decisions, code, experiments, papers read)
- Results / findings (metrics, unexpected observations)
- Open questions / blockers
- Next steps

Also update long-term memory in `.Codex/memory/` (in-repo; see `.Codex/README.md` for symlink story) when lasting facts change. See `memory/feedback_long_memory_and_logs.md`.

## Workflow (Mac + R2 + GitHub + scalable non-H20 compute)

- **Mac**: code editing, tests, small smoke training (N ≤ 500). Conda env `ecophys` (Python 3.11, per global AGENTS.md). Always use `conda run -n ecophys python …` not bare `python`.
- **Cloudflare R2**: transit + canonical bulk data store. Compute nodes stage immutable input shards from `r2://ecophys/` before a run and upload manifests/results afterward.
- **GitHub**: canonical code store. `main` stays runnable; experiments on feature branches.
- **GPU workers**: current production floor is two independent V100 32 GB nodes. Future capacity may add more compatible CUDA workers, but no active plan may assume H20 access. Keep heterogeneous GPU types in separate worker pools and benchmark each against canonical V100 jobs.
- Prefer independent config/seed/market job arrays. Use `ecomd/training/train_distributed.py` only when a scientific experiment truly requires multi-GPU training. Checkpoints save every 30 min; local manifests are canonical and W&B is optional with `resume="allow"`.

See `papers/proposal/plan_v4_ncs.md`, `papers/proposal/plan_v4_g0_reentry_v1.md`, `docs/research_lineage.md`, and
`memory/feedback_workflow.md` for full details.

## Code & experiment standards

- **Language**: Python 3.11, PyTorch 2.3+. JAX/diffrax allowed for specific physics modules (ODE integration, fluctuation-theorem batched analysis) when it's clearly the right tool.
- **Dependencies**: Add to `pyproject.toml`. Prefer `pip install` via `conda run -n ecophys pip install …`.
- **Types**: type annotations on all public functions; `mypy --strict` on the core package.
- **Tests**: `pytest` for any non-trivial logic. Especially: data schema validation, stylized-facts computations, physics quantities (energy conservation, fluctuation-theorem identities).
- **Configs**: Hydra for experiments. Never hardcode paths, hyperparams, or model sizes in scripts.
- **Reproducibility**: every experiment has a `config.yaml`, explicit `seed`, git SHA, and `wandb` run URL. Checkpoint formats compatible with `torch.load(..., map_location="cpu")`.
- **Comments**: Minimal per the global AGENTS.md. Only write a comment when the *why* is non-obvious. Never narrate what code does.

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

See `README.md` for the current layout. `papers/proposal/plan_v4_ncs.md` is authoritative for the
next NCS archival project; `papers/proposal/plan_v4_g0_reentry_v1.md` governs the current zero-cost
re-entry work. Plan v3 physics and Plan v5/exp141 are historical or parallel context and must not
override Plan v4's data or compute boundaries.
