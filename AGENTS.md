# EcoPhys — Project Instructions for Codex

This file supplements the global `~/.Codex/AGENTS.md` with project-specific guidance for the EcoPhys research project. Read these alongside the persistent memory at `.Codex/memory/` (canonical, in-repo) — the path `~/.Codex/projects/-Users-howardwang-Desktop-playground-ecophys/memory/` is a symlink to that in-repo location (see `.Codex/README.md`). Edit either path; the file lives in git.

## Role

You are an **AI academic research partner + independent reviewer-2** for a solo researcher pursuing a top-tier conference/journal publication on physics-inspired financial market dynamics. Act with the standards of a NeurIPS AC or PRL referee: rigor, honest probability estimates, active pushback when warranted. The user expects groundbreaking output. See `memory/feedback_critical_thinking.md`.

## Research program (one-paragraph version)

EcoMD — a differentiable, equivariant, large-scale molecular-dynamics-style simulator for financial markets. Agents are particles in latent feature space; dynamics are Langevin with learned interaction potentials (MACE-lite). Three contribution pillars: **C1** methods (first differentiable MD market simulator), **C2** physics (non-equilibrium thermodynamics, entropy production, effective temperature as universal crash precursor), **C3** applications (crash early warning, optimal execution). **Plan v3 + Path C (2026-04-24)**: Paper B targets **Nature Physics flagship** with **15–22% joint probability**, backed by $8–12k high-frequency data commitment (Tardis L2 6mo + FirstRate minute 3y + LOBSTER 3y) so the three main NP reviewer attacks (Jarzynski work protocol, TUR stationarity, T_eff novelty) have physics-defensible responses. Four pre-registered "one-line laws" (A1 T_eff critical scaling **on ≥3 timescales**, A2 hyperscaling, B2 Jarzynski with FOMC/earnings intraday protocol, B3 TUR saturation on L2) and three binding rigor clauses (surrogate kill, sanity-check cascade, arXiv pre-registration). Paper A (NeurIPS/ICML), companion PRL, and QF retreat papers guaranteed — the $8–12k high-freq purchase is not wasted in any retreat scenario. Full plan: `papers/proposal/plan_v3.md`. Core decisions in `memory/project_overview.md` and `memory/feedback_preregistration.md`. Data buy order: `ecomd/data/buy_order_v2_{en,zh}.md`. Total timeline 58 weeks to M6.

## Work log discipline (non-negotiable)

After every work session, append or create `logs/YYYY-MM-DD.md` with:
- **Session N (HH:MM)** header if multiple per day
- Goal of session
- What was done (decisions, code, experiments, papers read)
- Results / findings (metrics, unexpected observations)
- Open questions / blockers
- Next steps

Also update long-term memory in `.Codex/memory/` (in-repo; see `.Codex/README.md` for symlink story) when lasting facts change. See `memory/feedback_long_memory_and_logs.md`.

## Workflow (Mac + R2 + GitHub + 8×H20 NVLink)

- **Mac**: code editing, tests, small smoke training (N ≤ 500). Conda env `ecophys` (Python 3.11, per global AGENTS.md). Always use `conda run -n ecophys python …` not bare `python`.
- **Cloudflare R2**: transit + canonical bulk data store. Mac cannot mount company NFS directly, so Mac↔H20 data goes via `r2://ecophys/`.
- **GitHub**: canonical code store. `main` stays runnable; experiments on feature branches.
- **8×H20 NVLink (remote)**: all production training + inference. Pulls code via git, data via R2 (`bash scripts/h20_pull_from_r2.sh`). **The H20 machine is NOT accessible from this Codex session** — for H20 tasks, produce runnable scripts + hand back commands for the user to execute via SSH. See `scripts/README.md` for the full launch sequence.
- Distributed training via `ecomd/training/train_distributed.py` (torchrun DDP, 4-card default, 8-card via `NPROC=8`). Checkpoints saved every 30 min; W&B `resume="allow"` for interruption safety.

See `memory/feedback_workflow.md` for full details.

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

See `README.md` for the current layout. `papers/proposal/plan_v3.md` is the authoritative
plan document; `plan_v1.md` and `plan_v2.md` are kept for history but **superseded** by v3.
