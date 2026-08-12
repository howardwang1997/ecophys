# Plan v4 G0 re-entry v1 — theorem-first admission before implementation

**Frozen:** 2026-08-12  
**Status:** R1--R3 process infrastructure complete; G0 remains FAIL; R4 blocked without a real candidate
**Plan of record:** `papers/proposal/plan_v4_ncs.md`  
**Binding negative decision:** `papers/proposal/ncs_g0_forward_audit_2026-08-10.md`  
**Development branch:** `ncs-plan-v4-g0-reentry-v1`  
**Immutable predecessor archive:** `archive/plan-v5-exp141-feasibility-20260812@436dad6e7f80999584e44c4a616a1f213b9c814d`

**Execution update (2026-08-12):** R1--R3 are complete as process infrastructure. Exp142 retained a formal
`FAIL_PROCESS_VALIDATION` caused by an inverted raw-observation boolean; exp143 preregistered the one-defect repair
and passed all ten positive aggregation gates. All eight candidate fixtures matched, but none is a real candidate.
G0 therefore remains FAIL, R4 has no admitted input, and data/GPU scale-up remains locked.

**Integration update:** the verified result tree `81866a73f` was fast-forwarded into remote `main` on 2026-08-12;
the immutable predecessor archive remained at `436dad6e7f80999584e44c4a616a1f213b9c814d`.

Repository integration was verified separately from the immutable formal runs: 659 collected tests passed across
resource-bounded shards after the affected paths were rerun, strict mypy passed 91 source files, and scoped
diff-relevant Ruff checks passed. The repository-wide Ruff backlog is not part of this gate and remains open.

## 1. Decision and scope

Plan v4 remains the authoritative NCS plan, but its existing v0/v1 invariant-gradient candidate failed G0. This
branch does **not** reverse that decision. It builds a reproducible admission gate for a future mathematical
candidate and tests that the rejected construction cannot pass by renaming or recombining its known components.

The only permissible positive outcome of the automated work is `READY_FOR_HUMAN_AUDIT`. It is not a novelty
PASS, theorem proof, benchmark win or paper claim. A G0 PASS still requires a written identity or theorem,
equation-level comparison with primary prior art, specialist mathematical review and a falsifiable benchmark that
can distinguish the claimed difference. If no such object is supplied, the scientifically correct result is
`NO_ADMISSIBLE_CANDIDATE`, and NCS method experiments remain stopped.

Plan v5 and experiment 141 are preserved as independent historical feasibility work. Their generated-data PASS
cannot serve as evidence for this route, and no Plan v5 code or result is silently relabelled as an invariant-
calibration contribution.

## 2. Research question and non-claim

The immediate research question is:

> Can a proposed long-horizon calibration method be specified precisely enough that an adversarial audit can
> distinguish a genuinely new mathematical object from a composition of persistent chains, steady-state
> pathwise/LR gradients, SMC/Jarzynski reweighting, coupled debiasing and empirical mixing diagnostics?

This phase makes no claim that such a method already exists. It also cannot establish novelty by automation: the
software checks completeness, internal consistency and predeclared rejection rules, while the scientific verdict
remains a literature-and-proof decision.

## 3. Frozen candidate-admission contract

A candidate manifest must contain all of the following before candidate code or performance tuning:

1. **Mathematical object:** state space, parameterized transition law, invariant/path measure, target derivative,
   estimator or identity, assumptions and exact statement of the proposed difference.
2. **Irreducible primitive:** at least one claimed difference that is not merely a new application or composition.
   It must fall under a concrete theorem obligation, such as a new cross-parameter coupling/staleness correction,
   a computable finite-budget residual under materially weaker assumptions, or a variance--cost result not
   inherited from known estimators.
3. **Nearest-method matrix:** primary-source identifiers and equation/theorem-level coverage for persistent MCMC/
   PCD/SOUL, SMC/Jarzynski/SOSMC, steady-state LR/pathwise sensitivity, stochastic adjoints/StochasticAD/GGE,
   coupled unbiased MCMC/Rhee--Glynn and long/full/truncated BPTT where applicable.
4. **Non-equivalence witness:** a symbolic distinction plus a controlled problem on which the claimed primitive and
   the nearest composition make different quantitative predictions.
5. **Failure cases:** at least two counterexample families, including a slow-mixing or metastable case, with an
   outcome that rejects the candidate.
6. **Benchmark blueprint:** compute-matched baselines, accuracy, bias, variance, simulator steps, wall time, peak
   memory and failure rate on at least two non-EcoMD systems. EcoMD may appear only after cross-system evidence.
7. **Claim boundary:** explicit statements of what is not proved, what is diagnostic only and which result would
   stop the route.

The gate must reject the old v0/v1 composition, manifests with missing theorem obligations, EcoMD-only proposals,
performance-only novelty arguments and any request to open real data or GPU production before G0.

## 4. Work packages and chronology

| Work package | Work | Deliverable | Entry condition | Exit rule |
|---|---|---|---|---|
| R0 archive and lineage | Preserve the predecessor and merge the latest `main` history into an isolated branch | Archive pointer, branch topology, this plan | None | Plan committed before implementation |
| R1 contract schema | Implement typed parsing, canonical hashing and deterministic admission states | `ecomd/invariant_calibration/g0_contract.py` plus YAML template | R0 complete | Invalid/incomplete manifests fail visibly |
| R2 adversarial equivalence gate | Represent component coverage, interaction claims, theorem obligations and non-equivalence witnesses | Unit-tested assessment report | R1 complete | Old v0/v1 fixture is rejected; automation never emits novelty PASS |
| R3 exp142 controlled validation | Preregister and run data-free positive/negative fixtures | `experiments/142_ncs_g0_reentry_contract/` | R1--R2 committed | All frozen fixture outcomes match; otherwise repair software, not thresholds |
| R4 human mathematical audit | Supply a real candidate statement, update the forward literature audit and obtain equation-level review | Signed G0 re-entry report | A candidate reaches `READY_FOR_HUMAN_AUDIT` | PASS only if an irreducible object survives; otherwise stop |
| R5 scientific benchmark | Implement candidate and strong baselines on two independent systems | New preregistered experiment, not exp142 | R4 G0 PASS | Accuracy--cost/failure gate fixed before runs |
| R6 observation/fallback work | Continue the state-to-message map and cross-defect simulator audit allowed by the 2026-08-10 decision | Separate preregistration and claim ledger | Can proceed without a method candidate | Never counted as G0 method evidence |

The plan commit is a chronology boundary. R1 code, the exp142 preregistration, raw result and derived decision are
separate commits so that no result can be used to rewrite its own gate.

## 5. Experiment 142 protocol outline

Experiment 142 is a software/scientific-process validation, not an estimator benchmark. Its frozen fixture classes
are:

- `rejected_v0_composition`: all known components are present but no irreducible interaction theorem exists;
- `incomplete_new_label`: novel naming and a claimed gain are present but the formal object/witness is missing;
- `ecomd_only_performance`: an EcoMD improvement has no independent-system or non-equivalence evidence;
- `review_ready_hypothetical`: a deliberately synthetic, structurally complete manifest may reach
  `READY_FOR_HUMAN_AUDIT`, but never `PASS`;
- malformed, reordered and semantically identical manifests for deterministic validation and hash tests.

Primary metrics are exact expected status, exact reason-code set, stable canonical SHA-256 under mapping-order
changes and zero cases in which an automated assessment returns a novelty PASS. There is no accuracy metric and no
post-hoc threshold.

## 6. Data requirements

### R0--R3: available now, no purchase

- Existing Plan v4 specifications, the 33-source G0 audit and repository claim/failure ledgers.
- Hand-authored YAML fixtures and generated toy metadata only.
- No market observations, LOBSTER/Binance/Yahoo values, historical checkpoints or exp141 paths.
- No sealed test period is opened. No dataset license or redistribution decision changes.

### R4: literature, still no market data

- Primary papers and supplements needed for equation/theorem-level comparison.
- Each source records stable URL/DOI, access date, scoped claim and the exact candidate element it covers.
- A fresh search is required only after a concrete candidate exists; searching without a candidate cannot create
  method novelty.

### R5 and later: gated expansion

- At least two state-complete non-EcoMD benchmark systems with analytic or high-precision long-run ground truth.
- Generated benchmark trajectories first; public scientific-system data only if the benchmark requires them.
- Real market/L2 data are a later application gate, use temporal splits and independent markets, and require
  provenance/licence records. Current holdings are only the starting tier; vendors, exchanges, assets, periods and
  modalities may expand after the method and observation gates pass.
- Crash periods remain final evaluation only and are never tuning data.

## 7. Compute requirements

| Stage | Current resource | Frozen budget | Expansion rule |
|---|---|---:|---|
| R0--R3 | Mac `ecophys` Conda environment, CPU | <= 2 core-h; 0 GPU-h | No expansion |
| R4 | CPU for symbolic/numerical counterexamples | <= 20 core-h; 0 GPU-h by default | A tiny single-V100 profiling job requires a written reason; it is not evidence |
| R5 pilot | Current 2xV100 32 GB as independent workers; RTX2060 8 GB only for compatibility if still available | Initially <= 20 V100-equivalent h | Unlock only after written G0 PASS and preregistration |
| R5 full | Additional compatible GPU/CPU workers may be added | Determined from pilot throughput and power analysis | Preserve scientific settings; shard jobs by seed/system |

No current or future plan assumes H20. Heterogeneous GPU types remain separate worker pools and are benchmarked
against a canonical V100 job. Multi-GPU distributed training is allowed only if the scientific method actually
requires shared-state training; otherwise use independent config/seed/system arrays. Every production run records
config, seed, git SHA, host/GPU type, environment and artifact hashes, and checkpoints at most 30 minutes apart.

## 8. Binding gates

| Gate | PASS requirement | Failure consequence |
|---|---|---|
| P0 chronology | Plan and fixtures are frozen before implementation/result commits | Recreate on a fresh experiment number |
| C0 completeness | All contract fields, source scopes, theorem obligations and stop rules validate | `INCOMPLETE`; no coding |
| C1 irreducibility | Human audit finds a formal object not reduced to the covered composition | `REJECTED_EQUIVALENT`; G0 remains FAIL |
| C2 falsifiability | A witness and counterexamples distinguish the claim quantitatively | `NOT_FALSIFIABLE`; no benchmark |
| C3 independence | Two non-EcoMD benchmark families and all strong baselines are frozen | `ECO_MD_ONLY` or `BASELINES_MISSING` |
| G0 re-entry | C0--C3 plus primary-literature and proof review pass | NCS method route stays stopped; no data/GPU scale-up |

Only the human G0 re-entry report can change Plan v4's G0 status. Passing exp142 merely demonstrates that the
admission mechanism behaves as specified.

## 9. Risks and controls

- **Process infrastructure mistaken for research novelty:** label exp142 as a contract validation and exclude it
  from paper evidence.
- **Automation laundering a novelty judgment:** the state machine has no `PASS` output; final review is human.
- **Component checklist misses an equivalent formulation:** require a new primary-source audit for a real candidate,
  not only keyword matching.
- **A decorative theorem statement passes completeness:** require a counterexample, quantitative witness and
  nearest-method mapping; completeness still only unlocks review.
- **EcoMD complexity hides non-novelty:** require two independent systems before EcoMD benchmarking.
- **Synthetic success is overread:** fixtures validate code paths only; they do not update venue probabilities.
- **Compute/data expansion precedes scientific justification:** R0--R4 default to zero GPU and no market data.
- **Branch histories silently mix claims:** preserve the Plan v5 archive pointer and never modify exp141 artifacts.

## 10. Immediate execution order

1. Commit this plan, project instructions, lineage, work log and durable-memory update.
2. Push `ncs-plan-v4-g0-reentry-v1` so the planning chronology is externally visible.
3. Add the typed contract and focused unit tests.
4. Freeze exp142 preregistration and fixtures before running the formal validation.
5. Run focused lint/type/tests, then the full repository regression suite in Conda.
6. Record the formal exp142 result, artifact hash, data/compute usage and honest `NO_ADMISSIBLE_CANDIDATE` status
   unless a separately supplied mathematical object has actually survived review.
7. Merge into `main` only after the branch is clean, pushed and verified; retain the archive branch permanently.
