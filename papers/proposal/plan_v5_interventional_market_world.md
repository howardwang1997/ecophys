# Plan v5 — Interventional Multi-clock Market World Model

**Status (2026-08-12):** feasibility only; no positive model, market-science, NMI, or NCS claim is authorized.

**Branch:** `interventional-market-world-v1`

**Lineage base:** `ncs-invariant-calibration-v4@a8bf89427f38d53cf0cb1ad836b133d74e9d6ecd`

**Immediate protocol:** `experiments/141_multiclock_intervention_feasibility/PREREGISTRATION.md`

## 1. Research question

Can a market simulator whose known exchange mechanism is exact, whose event-generating behavior is learned, and
whose behavior updates on a slower clock predict an unseen institutional intervention better than observationally
fitted frozen or instantaneous-response models?

This reverses the old EcoMD workflow. The program starts from a real intervention and a sealed response estimand;
the simulator is a replaceable hypothesis engine. Latent molecular dynamics, effective temperature, entropy,
Jarzynski relations, TUR saturation, universal heavy tails, and crash precursors are not active hypotheses.

## 2. Core separation

The event transition is

\[
a_n^i \sim \pi_\theta(a\mid q_n,z_n^i,b_k^i,I_r),\qquad
(q_{n+1},z_{n+1})=G_{I_r}(q_n,z_n,a_n).
\]

- `G`: exact order validation, price--time priority, matching, cancellation, settlement, fees, cash and inventory
  accounting. Published rules are not relearned.
- `pi`: probabilistic order arrival, side, placement, size, cancellation, latency and heterogeneous response. These
  components may be learned.
- `U`: slower belief/policy update from realized outcomes. It is evaluated against frozen and instantaneous
  alternatives.
- `I`: versioned institutional rules and explicit interventions. The target post-intervention data remain sealed.

An unknown effective mechanism may enter only as a constrained residual with uncertainty. A learned emulator of
`G` is a speed approximation, not the scientific ground truth, and must pass eventwise and interventional
equivalence tests.

## 3. Claims and non-claims

### Conditional NMI claim

An asynchronous, constraint-preserving, multi-clock world-model method improves unseen-intervention generalization
across mechanisms or environments under equal tuning and compute budgets.

This route requires a method contribution beyond a market-specific hybrid, broad learned-world-model and ABM
baselines, multiple mechanisms or environments, and a blinded real intervention.

### Conditional NCS claim

A validated adaptive market digital twin separates immediate mechanical response from slower behavioral
re-centering and reveals a response pattern that replicates across independent real market-rule interventions.

This route requires multiple real interventions, treated/control designs, uncertainty propagation, numerical
verification and a scientific result beyond simulator fidelity.

### Forbidden claims during feasibility

- that EcoMD is validated against a real order book;
- that latent particles are real traders or physical particles;
- that a synthetic fast/slow recovery proves a real market law;
- that online correction on a target post-period is blind prediction;
- that a hybrid event simulator is novel by itself;
- that one historical event supports universality.

## 4. Work packages and hard gates

| Gate | Work | Data | Compute | Pass condition | Failure action |
|---|---|---|---|---|---|
| R0 | Current prior-art and intervention-data shortlist | Rule documents and vendor/public coverage only | CPU, no GPU | One development intervention plus one plausibly independent sealed replication with exact timestamps, controls and event data | Stop the Nature routes; do not buy data |
| F1 | Exact minimal exchange kernel | Generated orders only | Local CPU | Zero matching, tick, priority, settlement, cash or inventory invariant violations | Repair before any model run |
| F2 | Synthetic multi-clock identifiability, exp141 | Fresh generated streams only | Three hosts, CPU shards | All preregistered core gates pass | Do not acquire real intervention data or scale models |
| F3 | Cross-hardware learned-policy probe | Generated tensors only | 2xV100 32 GB + RTX 2060 8 GB | Finite training, exact same-device continuation, bounded memory and cross-device metric tolerance | Repair environment/model size; no scientific interpretation |
| R1 | One small blind real-intervention pilot | New, frozen event window | CPU plus at most 100--400 V100-eq h | Predefined response vector beats fixed, point-process and statistical controls without post-event fitting | Stop Nature route or narrow to an audit/benchmark |
| R2 | Independent sealed replication | New event/venue/period | Expand only after R1 | Direction, magnitude and uncertainty transfer under the frozen protocol | No universal or cross-market claim |
| R3 | Venue fork | R0--R2 artifacts | Evidence-dependent | Algorithmic transfer selects NMI; replicated market mechanism selects NCS | Use a specialist venue if neither burden is met |

F1--F3 are engineering and identifiability feasibility. They cannot pass R0, R1 or R2.

## 5. Experiment 141 allocation

Experiment 141 uses three balanced seed shards rather than assigning a truth family to a machine. This prevents a
hardware difference from being confounded with a scientific arm.

- V100-A: evaluation seeds with index modulo 3 equal to 0, plus the shared deterministic anchor and CUDA probe.
- V100-B: evaluation seeds with index modulo 3 equal to 1, plus the same anchor and CUDA probe.
- RTX2060: evaluation seeds with index modulo 3 equal to 2, plus the same anchor and an 8 GB CUDA probe.

The two V100 jobs must check the existing Graphene queue record, absent release marker, no compute PID and stable
low utilization before launch. The RTX2060 job must not alter the dirty historical ABIDES checkout; it uses a new
isolated sparse clone and a separate Conda environment. Results record exact Git/config/protocol hashes, GPU UUID,
software versions, peak memory and wall time.

## 6. Data contract

### D0 — generated feasibility data

Generated from committed code and seeds. Public and reproducible. It is the only input to F1--F3.

### D1 — spent development data

The existing free LOBSTER samples, Binance 2024 Q1 data, daily panels, crash windows and prior EcoMD rollouts have
already influenced estimands or diagnostics. They may be used for schema regression and debugging, never relabeled
as independent confirmation.

### D2 — new intervention pilot

Not yet selected or acquired. Before access, freeze source, license, venue, rule version, treated/control universe,
timestamps, pre/post windows, missing-data policy, checksums, response vector and stopping rule.

### D3 — confirmatory expansion

Acquire only after R1. Capacity planning is 2--10 TB and roughly USD 10k--25k for a core package, expanding to
10--30 TB and USD 25k--50k only after a positive preregistered pilot. These are planning envelopes, not quotes.

## 7. Compute contract

No H20 is used or assumed.

| Stage | GPU | CPU / RAM | Storage |
|---|---:|---:|---:|
| F1--F3 | 100--400 V100-eq h ceiling, expected far below ceiling | 2k--10k core-h ceiling; current 16-core hosts | <1 TB |
| NMI campaign, conditional | 4k--12k V100-eq h; recommend 8--16 workers | 10k--50k core-h; 256--512 GB RAM | 2--10 TB |
| NCS campaign, conditional | 1k--4k V100-eq h; recommend 4--8 workers | 50k--250k core-h; 128--512 cores and 256 GB--1 TB RAM | 10--30 TB |

GPU expansion is forbidden before a real response estimand and data contract exist. Event reconstruction and Monte
Carlo use CPU workers; GPU workers do not wait on CSV/Parquet preparation.

## 8. Repository and artifact boundaries

- `ecomd/market_world/`: new typed market-world components. It may import generic observation/provenance utilities,
  but old EcoMD dynamics do not become the default mechanism.
- `experiments/141_*`: immutable preregistration, runners, raw shards, merger and result report.
- `configs/market_world/`: versioned experiment configuration.
- `data/manifests/`: data eligibility and spent/unused state; no commercial raw data in Git.
- `docs/research_lineage.md`: authoritative relationship between old and new work.
- `.claude/memory/`: durable decisions for this branch; historical failure memories remain unchanged.

Results are committed only after raw shard hashes are archived. A failed gate is preserved as failed; a repaired
protocol receives a new experiment number, seeds and preregistration commit.

## 9. Decision risks

The dominant risk is not compute. It is building a complex observational simulator without an identifiable and
replicated intervention result. NMI additionally risks being judged market-specific engineering; NCS additionally
risks confounding and non-transfer across historical interventions. Anonymous L2 cannot identify real trader
beliefs or identities, so the first real model may claim only latent behavioral adaptation or typed agent classes.

Current subjective end-to-end probabilities are 3--7% for NMI and 5--10% for NCS. Conditional on at least two
blinded independent interventions, strong baselines, a stable transfer result and complete artifacts, they rise to
approximately 10--18% and 15--25%. These are project judgments, not journal acceptance-rate estimates.
