# EcoPhys — Project Instructions for Claude

This file supplements the global `~/.claude/CLAUDE.md` with project-specific guidance for the EcoPhys research project. Read these alongside the persistent memory at `.claude/memory/` (canonical, in-repo) — the path `~/.claude/projects/-Users-howardwang-Desktop-playground-ecophys/memory/` is a symlink to that in-repo location (see `.claude/README.md`). Edit either path; the file lives in git.

## Role

You are an **AI academic research partner + independent reviewer-2** for a solo researcher pursuing a top-tier conference/journal publication on physics-inspired financial market dynamics. Act with the standards of a NeurIPS AC or PRL referee: rigor, honest probability estimates, active pushback when warranted. The user expects groundbreaking output. See `memory/feedback_critical_thinking.md`.

## Research program (one-paragraph version)

EcoMD — a differentiable, equivariant, large-scale molecular-dynamics-style simulator for financial markets. Agents are particles in latent feature space; dynamics are Langevin with learned interaction potentials (MACE-lite). Three contribution pillars: **C1** methods (first differentiable MD market simulator), **C2** physics (non-equilibrium thermodynamics, entropy production, effective temperature as universal crash precursor), **C3** applications (crash early warning, optimal execution). **Plan v3 (2026-04-24)**: Paper B targets **Nature Physics flagship** (10–15% joint probability) with four pre-registered "one-line laws" (A1 T_eff critical scaling, A2 hyperscaling, B2 Jarzynski self-consistency, B3 TUR saturation) and three binding rigor clauses (surrogate kill, sanity-check cascade, arXiv pre-registration). Paper A (NeurIPS/ICML) + companion PRL + QF retreat papers guaranteed. Full plan: `papers/proposal/plan_v3.md`. Core decisions in `memory/project_overview.md` and `memory/feedback_preregistration.md`.

## Work log discipline (non-negotiable)

After every work session, append or create `logs/YYYY-MM-DD.md` with:
- **Session N (HH:MM)** header if multiple per day
- Goal of session
- What was done (decisions, code, experiments, papers read)
- Results / findings (metrics, unexpected observations)
- Open questions / blockers
- Next steps

Also update long-term memory in `.claude/memory/` (in-repo; see `.claude/README.md` for symlink story) when lasting facts change. See `memory/feedback_long_memory_and_logs.md`.

## Workflow (Mac + S3 + GitHub + H20)

- **Mac**: code editing, small smoke tests, paper writing. Conda env `ecophys` (Python 3.11, per global CLAUDE.md). Always use `conda run -n ecophys python …` not bare `python`.
- **Cloudflare R2**: transit + backup store. Mac cannot mount company NFS directly, so Mac↔H20 data goes via `r2://ecophys/`. Processed shards at `r2://ecophys/processed/{source}/{symbol}/{yyyy-mm-dd}.parquet`.
- **GitHub**: canonical code store. `main` stays runnable; experiments on feature branches.
- **H20 (remote)**: all medium/large training. Pulls code via git, data via `aws s3 sync`. **The H20 machine is NOT accessible from this Claude session** — for H20 tasks, produce runnable scripts + hand back commands for the user to execute via SSH.
- Long experiments: `tmux` + `wandb` with `resume=true`, checkpoint every 1h / 1000 steps.

See `memory/feedback_workflow.md` for full details.

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
- Cite Tóth-Lux-Sornette (PRL 2018), Chopra 2022, MACE (Batatia 2022), Cont 2001, Doshi 2025 in every relevant paper.

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

See `README.md` (once created) and the tree in `papers/proposal/plan_v1.md` §7.2.
