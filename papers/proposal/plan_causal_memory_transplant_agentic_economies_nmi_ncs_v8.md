# Plan v8 — Causal memory transplantation in agentic economies

**Frozen:** 2026-08-13

**Branch:** `observable-state-mechanism-search-v8`

**Parent:** `main@132640630d1e71257642cba967e5ecc3a15c0f3f`

**Initial state:** `SCOUT`; primary literature and protocol design only; no generated outcome, model inference,
remote-host or GPU authorization

## 1. Why the target changes again

V6 showed that known market feedback does not identify adaptive demand when latent dynamics can change across
regimes. V7 then closed three generic repairs: an observable gauge quotient is standard input--output behavior, a
bounded drift model is standard set membership, and a finite randomized loop identifies assignment effects rather
than adaptation against unrestricted fixed hidden memory.

V8 changes the information source rather than the name of the estimand. In a stateless computational agent, the
episode-specific external memory can be read, randomized, erased or transplanted after a true process restart while
model weights, system instructions and executable economic rules remain fixed. The scientific question is:

> Does transferring only an agent's recorded episode memory transfer a signed micro-to-macro response into an
> otherwise reset artificial economy, and which information in the memory is causally responsible?

The admissible claim is about computational agents with audited state boundaries. It is not evidence about human
memory, real-market trader beliefs or a universal economic law.

## 2. Information-budget screen

| Information source | Readable? | Manipulable/resettable? | V8 role |
|---|---:|---:|---|
| exact exchange/resource mechanism state | yes | yes | deterministic transition oracle and common recipient environment |
| generated agent actions/rewards/inventory | yes | yes | direct outcome and mediation variables |
| external episodic memory supplied to a stateless model call | yes | yes, including semantic and length-matched shams | active causal treatment |
| model weights/system prompt/decoder/version | hashable | fixed, or randomized only in declared blocks | population definition and blocking variables |
| hidden activations/provider state | generally no | only excluded by local stateless execution or audited API contract | fail-closed eligibility check |
| real trader private state or strategy memory | no | no | excluded from every V8 claim |
| prospective real-market mechanism assignment | currently no | no | excluded from T0/T1 |

One nearby idea is rejected before candidacy. A phase boundary from price-controller gain interacting with agent
learning rate is already directly covered by resource-centric pricing for competitive online learners, online
load balancing in monotone games and safe pricing under time-varying utilities. It is a baseline, not V8's main
contribution.

## 3. Frozen computational object

For agent `i`, let `theta_i` denote fixed policy weights and system instructions, `M_i,t` the explicit external
episode memory, `O_i,t` the observation and `A_i,t` the primitive action. Let the economic mechanism be executable:

\[
A_{i,t}\sim\pi_{\theta_i}(\cdot\mid O_{i,t},M_{i,t};U_{i,t}),
\qquad
X_{t+1}=G(X_t,A_{1:N,t}),
\qquad
M_{i,t+1}=W(M_{i,t},O_{i,t},A_{i,t},R_{i,t}).
\]

`U` contains explicitly logged decoding or policy randomness. A source agent experiences randomized source regime
`Z in {-1,+1}` and produces a memory capsule `C_Z`. After a fresh recipient process and common mechanism reset,
the capsule treatment is randomized:

\[
do(M_{i,0}=T_c(C_Z)),
\qquad
c\in\{\text{intact},\text{semantic-scramble},\text{erased},\text{unrelated}\}.
\]

The semantic-scramble arm must preserve the serialization schema, token/byte-length bin, recency positions and
nonsemantic identifiers while breaking the donor experience/action relation. It may not be selected after outcomes.

For a preregistered complete outcome vector `Y`, define the memory-carried response

\[
\tau_{mem}
=\{E[Y\mid Z=+1,c=intact]-E[Y\mid Z=-1,c=intact]\}
-\{E[Y\mid Z=+1,c=scramble]-E[Y\mid Z=-1,c=scramble]\}.
\]

Randomization and inference occur at the independently restarted economy level. Agent rows inside one economy are
not independent replicates.

## 4. Candidate and claim ladder

### V8-C1 — causal carrier of episode history

**Candidate phenomenon:** signed source-regime information moves with an intact memory capsule into recipient
actions and aggregate dynamics after process/mechanism reset, while length-matched semantic shams do not.

**L0 implementation claim:** the memory intervention changes only the declared capsule and every hidden cache,
conversation state, RNG stream and mechanism state is auditable.

**L1 micro claim:** `tau_mem` is nonzero for a frozen action/reward vector and is mediated by declared memory
content under randomized source and capsule assignments.

**L2 macro claim:** the transferred action response induces a preregistered signed change in price, allocation,
congestion, volatility or coordination under exact mechanism accounting.

**L3 cross-system claim:** direction and normalized magnitude transfer across at least two economically distinct
mechanisms and at least four policy/model families, including a transparent non-LLM agent.

Only L0--L1 are eligible for the first feasibility gate. No human or real-market inference is allowed at any
generated tier.

## 5. Nearest-result attack before code

The candidate must be compared equation by equation against:

1. external-memory, retrieval-augmented and reflective LLM agents;
2. in-context learning, context editing, activation/causal tracing and prompt-ablation studies;
3. machine teaching, policy/checkpoint transfer and experience replay;
4. causal mediation, separable effects and factorial encouragement designs;
5. interference-aware marketplace and network experiments;
6. operational causal breaks, process tensors and memory-channel tests;
7. dynamic human/LLM market experiments and multi-agent institution studies;
8. mechanism design with learning agents, dynamic pricing and congestion control.

Ablating a memory module, observing a performance change or making a market more realistic is not enough. V8
survives N0 only if randomized donor history plus memory-content transplantation supplies a distinct causal object
or a previously unreported, signed and cross-mechanism computational phenomenon.

## 6. Identification and falsification gates

### N0 — novelty/non-equivalence

- Freeze the nearest-result matrix and exact residual claim before model inference.
- Retire if `tau_mem` is ordinary prompt/context ablation, causal mediation or experience transfer with no distinct
  phenomenon or guarantee.
- Search failure and a paper's stated future work are not novelty evidence.

### I0 — state-boundary validity

- Use a local stateless inference path or prove through an executable audit that provider-side session state is
  absent.
- Hash model weights, tokenizer, system prompt, generation parameters, memory writer and mechanism code.
- Fresh process, fresh mechanism state and disjoint RNG substreams per economy.
- Include intact, erased, unrelated, serialization-sham and semantic-scramble arms.
- Freeze source-regime generation separately from recipient scoring; no source/recipient seed reuse that couples
  outcomes mechanically.
- Treat the economy as the statistical unit and use randomization inference or cluster-valid uncertainty.

### S0 — signed scientific specificity

- Predeclare which donor experience should move which primitive action and through what exact mechanism equation it
  should affect the aggregate vector.
- Require a sign-reversal or content-swap prediction, not only `performance changes`.
- Reject the proposed explanation if a bag-of-tokens, explicit regime label, prompt-length or recent-action oracle
  reproduces the effect.

### F0 — free feasibility

- First use transparent finite-state, tabular or small neural policies to validate the design and negative controls.
- An open-weight language model may enter only after N0/I0/S0 and a separately committed preregistration.
- Stop if effect recovery is unstable at the minimum scientifically meaningful effect under economy-level
  replication available on current hardware.

## 7. Baselines and mandatory ablations

- no-memory and full-history oracles;
- explicit source-regime label and donor-last-action shortcuts;
- same-length random text, shuffled records and timestamp/identity permutation;
- recipient policy with frozen weights but no memory reader;
- fixed finite-state and Bayesian learners with analytically known sufficient state;
- retrieval-only, summary-only and raw-event memory writers;
- common-random-number paired runs reported alongside independent-seed inference, never substituted for it;
- at least one mechanism where the hypothesized memory should have zero effect.

The learned memory system must beat the shortest transparent sufficient-statistic oracle. Otherwise the result is
an implementation study of a verbose state encoding.

## 8. Venue routing

### Nature Machine Intelligence

Requires a broadly useful causal audit method or theorem for stateful agents that is not ordinary mediation,
factorial randomization, context ablation or process-state testing; validation must span non-economic agent systems.
The current phenomenon alone is insufficient.

### Nature Computational Science

Requires a robust new computational-science result about how explicit agent memory moves causal response across
economic mechanisms, with exact state audits, multiple open model families, transparent agent oracles and an
independent implementation replication. A single LLM market demo is insufficient.

### Honest planning priors

- NMI-ready non-equivalent method after N0: `1%--3%`.
- NCS-ready cross-mechanism phenomenon after full evidence: `3%--8%`.
- Strong specialist/agent-evaluation paper after replicated causal effects: `15%--30%`.

These are planning priors, not acceptance forecasts.

## 9. Data requirements

### T0 — authorized now

- primary papers, open-source repository metadata and model documentation;
- protocol/schema design and hand-derived transparent-agent fixtures;
- no model-generated action/outcome, human data, API call, market outcome or paid data.

### T1 — after N0/I0/S0 and separate preregistration

- fully generated source memories, recipient actions and exact mechanism traces;
- immutable model/tokenizer hashes, prompts, seed maps and environment manifests;
- public open-weight models with redistribution-compatible metadata; generated content stored with provenance;
- no human subject claim and no real-market calibration requirement.

### T2 — after generated feasibility

- additional open model families and a second independently implemented mechanism;
- optional public human experimental data only for explicitly lower-scope external comparison, never as evidence of
  human memory transplantation;
- any API or closed model requires a frozen version/retention/privacy contract and separate cost approval.

## 10. Compute requirements

### T0 — current authorization

- <=30 local Mac CPU core-hours for literature, symbolic work, deterministic fixtures and graph validation;
- zero remote-host contact, zero V100/RTX2060 use and zero GPU-hours.

### T1 — transparent-agent feasibility

- 100--1,000 CPU core-hours, <=64 GB RAM and <=100 GB artifacts;
- CPU work may use the V100/RTX2060 hosts with GPUs idle only after a separate preregistration;
- no GPU is justified for a tabular/finite-state design.

### T2 — open-weight agent feasibility

- initial ceiling 100--400 V100-equivalent GPU-hours and 1--5 TB generated traces/checkpoints;
- current 2xV100 32 GB can run independent 3B--8B inference/adapter jobs; the RTX2060 is limited to small models,
  transparent baselines or CPU orchestration;
- future capacity may expand to additional compatible non-H20 workers, with each GPU type benchmarked separately;
  H20 is excluded.

### T3 — cross-model confirmation

- provisional 1,000--10,000 V100-equivalent GPU-hours, 10k--100k CPU core-hours and 5--30 TB only after T2 power,
  novelty and artifact audits pass;
- expand model count and independent economies before increasing parameter count.

Compute cannot repair prompt confounding, hidden provider state, pseudoreplication or a prior-art collision.

## 11. Immediate queue

1. Commit and push this plan alone before extending the graph or generating any agent action.
2. Complete the eight-neighborhood primary-source audit and write one formal candidate card.
3. Specify a minimal transparent-agent source/transplant/recipient design and analytic sufficient-state oracle.
4. If N0/I0/S0 survive, preregister the smallest CPU-only feasibility experiment in a separate commit.
5. Contact no worker and download/run no model until that preregistration is frozen.

## 12. Stop rules

- Do not call prompt ablation, context sensitivity or memory-module performance a causal memory-transplant result.
- Do not count agents, time steps or tokens inside one economy as independent samples.
- Do not interpret generated artificial-agent behavior as human or real-market physics.
- Do not tune memory serialization, source regimes, outcome signs or model families after viewing the full vector.
- Retire if an explicit regime-label or shortest sufficient-state oracle matches the memory capsule.
- Close before compute if the candidate reduces to standard mediation/interference or if no signed cross-mechanism
  claim survives the literature audit.
