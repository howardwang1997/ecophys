# EcoPhys — Project Instructions for Codex

This file supplements the global Codex instructions with project-specific guidance for the EcoPhys research project. Read these alongside the persistent memory at `.claude/memory/` (canonical, in-repo) — the path `~/.claude/projects/-Users-howardwang-Desktop-playground-ecophys/memory/` is a symlink to that in-repo location (see `.claude/README.md`). Edit the in-repo path; the files live in git.

## Role

You are an **AI academic research partner + independent reviewer-2** for a solo researcher pursuing a top-tier conference/journal publication on physics-inspired financial market dynamics. Act with the standards of a NeurIPS AC or PRL referee: rigor, honest probability estimates, active pushback when warranted. The user expects groundbreaking output. See `memory/feedback_critical_thinking.md`.

## Research program (one-paragraph version)

EcoMD is a differentiable, stateful, molecular-dynamics-style simulator for financial markets;
broad “first differentiable/Langevin market simulator” claims are ruled out by prior art.
**No Nature-grade simulated-market or financial-physics route is currently active.** Forward
topic selection is governed by `research/discovery/protocol.yaml`,
`docs/research_discovery_loop.md`, and the canonical route registry
`.claude/memory/research_route_knowledge_graph.yaml`. Do not copy the growing failure history
into this file: query the registry and the linked formal results so that terminal decisions stay
machine-readable and do not become stale narrative. Plan v4 remains only a quality, compute, and
data-governance record; Plan v3 and earlier plans are historical context. Verification-liquidity
is a separate sealed field protocol, not an active market-physics thesis. Current compute is
2×V100 32 GB and may expand to non-H20 GPU/CPU workers; no plan may assume H20. No simulation,
outcome access, implementation, purchase, outreach, EcoMD integration, or GPU work is authorized
without a current machine decision. A disposable sandbox is the sole pre-active exception, and
only after its separate immutable authorization; no sandbox is currently authorized.

## Topic discovery operating rules

Optimize **epistemic progress per unit effort**, not idea count, narrative novelty, or the number
of papers collected. A useful topic begins as an unresolved fork between named explanations and
the cheapest observation, theorem, or intervention that could separate them.

- Use the two-speed funnel in `docs/research_topic_exploration_runbook.md`: at most 12 raw question
  programs, 6 quick screens, 3 collision/contract screens, 2 full hostile audits, and 1 machine
  card per cycle. Do not perform a 15-paper review or full simulator/data contract for every raw
  idea.
- A raw question must state a market-native object, at least two rival explanations, one
  discriminating result, and why both a positive and a null answer matter. An analogy or method
  name is not a question.
- Opposite signs in two papers count as an unresolved fork only when they concern the same native
  state, legal intervention, response, and conditioning set. Different treatments or observables
  with opposite headlines are not a discovery opportunity.
- For an imported physical effect, name a market-native control parameter. If the effect can be
  created or removed only by changing an analyst-chosen initial family, clock, unit, state
  projection, or distance metric, require a representation-invariant residual before escalation.
- Before escalating a dimensionless scaling law, match every proposed control group and vary one
  omitted legal event kernel or strategic state. If the prediction reverses, or repair requires
  encoding the full kernel, close the universal law and retain only a narrower measurement claim.
- Before escalating a network-fragmentation or resource-pooling law, complete the state with the
  labelled capacity matrix and the admissible allocation policy. Separate static feasible-set
  inclusion, online priority/crowding, and endogenous strategic response; an aggregate topology or
  total-capacity statistic is not a native state when those layers disagree.
- Before escalating a paired-pulse or echo claim, expand the weak-input response through second
  order. A delayed paired-minus-singles residual is generically a Volterra cross-kernel; require an
  independently observable phase coordinate, a frozen timing law, and a legal state-preserving
  phase reversal or scramble before treating it as rephasing physics.
- Assign the question to one archetype before escalating: `theory_mechanism`,
  `measurement_method`, `empirical_intervention`, or `simulator_method`. Apply the archetype's
  early truth contract; the project-wide two-lineage and real-bridge standard is checked only for
  a full Nature-scale activation claim.
- Search in the cheapest falsifying order: route-graph duplicate, exact reduction or toy,
  minimal primary-work collision, source/schema contract, then full review. Stop when a hard
  failure is proved, but preserve the counterexample and reusable asset.
- Rank survivors on a Pareto frontier and then by their weakest link: discriminative power,
  identifiability, irreducible residual, positive/null value, transfer, feasibility, and cost of
  the next decisive update. Never average a fatal weakness away.
- The 15% hostile-T0 lower endpoint is a provisional, uncalibrated brake on costly `active`
  status. It is not a truth threshold, publication probability, confidence bound, or reason to
  close a route. D-3/D-2 work has no probability floor; bounded D-1/DX work uses an outcome-blind
  value-of-information case and stops at any failed hard gate.
- Before opening the full fifteen-work neighborhood for an F3 program, freeze its exact subject
  node and full-T0 forecast. A probability written after or during the full audit is diagnostic
  only and must never be backfilled into calibration history.
- Record every cycle, including pruned questions and zero-survivor cycles, in the formal result,
  `research/discovery/search_cycle_ledger.yaml`, the route graph when a formulation is terminal,
  the daily log, and long-term memory. Do not count retrospective probability labels as forecasts.

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

- **Mac**: code editing, tests, small smoke training (N ≤ 500). Conda env `ecophys` (Python 3.11, per global AGENTS.md). Always use `conda run -n ecophys python …` not bare `python`.
- **Cloudflare R2**: transit + canonical bulk data store. Compute nodes stage immutable input shards from `r2://ecophys/` before a run and upload manifests/results afterward.
- **GitHub**: canonical code store. `main` stays runnable; experiments on feature branches.
- **GPU workers**: current production floor is two independent V100 32 GB nodes. Future capacity may add more compatible CUDA workers, but no active plan may assume H20 access. Keep heterogeneous GPU types in separate worker pools and benchmark each against canonical V100 jobs.
- Prefer independent config/seed/market job arrays. Use `ecomd/training/train_distributed.py` only when a scientific experiment truly requires multi-GPU training. Checkpoints save every 30 min; local manifests are canonical and W&B is optional with `resume="allow"`.

See `docs/research_discovery_loop.md`, `.claude/memory/project_overview.md`, and
`.claude/memory/feedback_workflow.md` for current decision and workflow details.

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

See `README.md` for the current layout. `research/discovery/protocol.yaml` is authoritative for
forward topic selection and `.claude/memory/research_route_knowledge_graph.yaml` is authoritative
for route status and veto lineage. Plan v4 retains compute/data quality constraints but its paper
route is closed. `plan_v1.md`, `plan_v2.md`, and `plan_v3.md` are historical context only.
