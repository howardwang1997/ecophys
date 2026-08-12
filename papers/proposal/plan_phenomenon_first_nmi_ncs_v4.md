# Phenomenon-first NMI/NCS exploration v4 — intervention transport across human, algorithmic and agentic economies

**Frozen:** 2026-08-13

**Branch:** `phenomenon-first-nmi-ncs-v4`

**Base:** `main@8283e77f75e1b4c1b11fe805db00159c25fb0812`

**Inherited decisions:** v1 NMI `NO_SURVIVOR`; v2 NMI `NMI_NO_SURVIVOR`; v2 NCS
`NCS_C0_FAIL_IDENTIFICATION`; v3 `V3_NO_SURVIVOR`

**Initial resource boundary:** primary literature and dataset metadata only; <=30 Mac CPU core-hours, 0 GPU-hours,
no V100/RTX2060 contact, no market outcome inspection, no API purchase and no human-subject interaction

## 1. Objective and strategic change

The venue targets remain Nature Machine Intelligence and Nature Computational Science. The topic may change.
V1--V3 searched for a generic theorem or diagnostic first and repeatedly reduced to known identifiability,
predictive-state, memory or operator theory. V4 reverses the order: select a concrete, important and falsifiable
scientific phenomenon with observable or randomized discriminators, then ask whether solving it also demands a new
method.

The primary scientific family is:

> How do human, classical algorithmic and agentic-AI populations change their strategy and collective market
> dynamics when the same executable market mechanism is changed, and what information is lost when participant-
> level adaptation is viewed only through anonymous aggregate order flow?

This is a search question, not a claim. Existing experimental-market, algorithmic-agent or LLM-agent results may
occupy it. EcoMD is at most one controlled classical-agent population and must not define the phenomenon.

## 2. Binding interpretation and ethics rules

- Adaptation must be tied to participant-level actions, randomized treatment, declared strategy parameters or
  inspectable agent state. Anonymous aggregate persistence alone is never sufficient.
- A treatment effect and a behavioral mechanism label are separate estimands. Randomization can identify the
  former without uniquely identifying the latter.
- Human experimental data are used only under their existing licence/consent. V4 authorizes no new recruitment,
  deception, intervention or personally identifiable data processing.
- LLM agents are computational populations, not evidence about humans. Vendor/API model drift, hidden prompts and
  contamination are explicit threats to replication.
- A simulator-to-human agreement is descriptive until a preregistered cross-population prediction transfers to an
  untouched experiment.
- Existing PSR, process-tensor, causal-inference and system-identification tools may be used honestly as baselines.
  Their use does not make the method novel.
- NCS may survive through a replicated computational social-science discovery even if the estimator is standard.
  NMI additionally requires a transferable method, estimator or theorem beyond direct composition.

## 3. Candidate phenomena

### P1 — intervention response spectrum across population types

For population class `g` in `{human, classical algorithmic, agentic AI}`, randomized mechanism `m`, participant
actions `A`, market state `Q` and preregistered statistic family `F`, define a treatment-response vector

\[
R_g(m,m_0;\mathcal F)
=\left(
\mathbb E[f_j(A,Q)\mid do(m)]-
\mathbb E[f_j(A,Q)\mid do(m_0)]
\right)_{j=1}^J.
\]

The candidate phenomenon is not merely that mechanisms matter. It asks whether response directions, adaptation
times, heterogeneity and cross-session transfer obey a reproducible population ordering or decomposition under
matched executable rules.

Kill P1 if existing studies already establish the same cross-population law, if tasks/rules cannot be made
commensurate, or if only aggregate synthetic outcomes are available. A survivor needs participant-level or
inspectable-agent evidence, at least two mechanism families and an untouched replication population/task.

### P2 — causal adaptation loss under anonymous aggregation

Let `X_t` denote participant-level state/action histories and `Y_t=a(X_t)` an anonymous aggregate observation.
For a declared intervention and outcome query, compare identified sets or predictive risks using `X` and `Y`:

\[
\mathcal I_X(\tau)\subseteq\mathcal I_Y(\tau),
\qquad
\Gamma_a(\tau)=\operatorname{diam}\mathcal I_Y(\tau)-
\operatorname{diam}\mathcal I_X(\tau).
\]

The generic data-processing inequality is not novelty. The scientific question is whether real experimental
markets exhibit a stable, mechanism-dependent aggregation-loss profile that predicts when anonymous field data
cannot transport an intervention result.

Kill P2 if it is only mutual-information loss, ecological fallacy or ordinary partial identification. A survivor
needs a preregistered estimand, participant-to-aggregate paired data, exact aggregation and a new cross-mechanism
empirical regularity or a quantitatively non-equivalent bound.

### P3 — strategic memory under causal breaks and rule transfer

In repeated controlled sessions, insert a randomized reset or information/strategy causal break before a rule
change and compare future action laws. The candidate asks whether human, classical and agentic populations differ
systematically in which memory survives a declared break and whether that profile predicts transfer to a new
market rule.

Kill P3 if it reduces to standard carryover, repeated-game learning, change-point, process-tensor backflow or
prompt-memory evaluation without a new population-level law. A survivor needs ethically available reset/replay
data or an existing randomized design; observational session boundaries do not count as causal breaks.

## 4. Mandatory audits before data values

### Scientific prior art

- experimental asset markets, double auctions, bubbles/crashes, experience effects and market-design treatments;
- zero-intelligence, reinforcement-learning and algorithmic-trading populations under rule changes;
- LLM/agentic economic simulations, market games, strategic reasoning and model-to-human behavioral comparison;
- human-algorithm interaction and heterogeneous-agent experimental economics;
- carryover, learning, causal breaks, mediation, principal stratification and dynamic treatment effects.

### Method prior art

- hierarchical treatment-effect and transportability models;
- ecological inference, aggregation bias and partial identification;
- behavioral cloning, inverse RL, cognitive models and strategy classification;
- PSR/OOM/process tensor/finite Markov order;
- multi-agent evaluation, agent-based model calibration and simulation-based inference.

### Dataset metadata

For every possible dataset record source, licence, participant/action resolution, randomized treatment arms,
session structure, raw-versus-summary availability, contamination from published analyses and whether an untouched
replication can be sealed. Metadata may be inspected before outcome values; numerical results move the dataset to
development-only.

## 5. Admission gates

### Gate S0 — scientific importance and specificity

Pass only if one sentence states the phenomenon, discriminating observation, competing explanations and why the
answer changes understanding of computational or agentic economies. “Agents behave differently” fails.

### Gate D0 — no-cost data contract

Pass only if at least one participant-level development dataset and one independently sealable replication or
cross-population dataset are legally available without purchase. Summary tables alone fail.

### Gate I0 — identification

Pass only if randomization, declared agent state or an exact controlled design distinguishes the headline from
fixed hidden-state, task-difficulty, prompt, model-version and aggregation alternatives. Residual persistence
alone fails.

### Gate N0 — novelty routing

- `NCS_PHENOMENON_CANDIDATE`: a new, consequential and replicated scientific law may proceed with standard methods.
- `NMI_METHOD_CANDIDATE`: additionally needs a method/theorem non-equivalent to mandatory baselines in at least two
  non-market domains.
- `LOWER_VENUE_ONLY`: useful benchmark/application without a Nature-scale discovery or method.
- `RETIRED_PRIOR_ART`, `RETIRED_NO_DATA`, `RETIRED_IDENTIFICATION`: stop immediately.

Automation and the agent may route candidates but never issue a novelty `PASS`.

## 6. Zero-cost feasibility protocol

The initial v4 pass is literature and metadata only. If exactly one candidate clears S0/D0/I0 on paper, create a
separate preregistered experiment for:

1. schema/provenance validation without opening sealed outcomes;
2. exact participant-to-aggregate reconstruction;
3. estimator sanity on generated treatment assignments and known nulls;
4. development-only effect/heterogeneity estimation with fixed signs and exclusions;
5. untouched replication only after the analysis artifact is committed.

No LLM API calls, EcoMD training, V100 jobs or RTX2060 jobs are authorized by this plan alone. A metadata-only
candidate list is not a queue.

## 7. Conditional data needs

### T0 — authorized now

- Primary papers, official dataset repositories, codebooks, licences and treatment metadata.
- No outcome-value inspection; no personal data; no new human experiment.

### T1 — after S0/D0/I0 and preregistration

- Free participant-level experimental-market trajectories with treatment assignment, session timing and stable
  participant pseudonyms.
- Inspectable source/config/seed/action traces for classical agents.
- Reproducible agentic-AI traces with complete prompts, model identifier, decoding settings, tool state and API
  date; open-weight models are preferred for confirmation.
- One development dataset and one sealed independent replication; previously published numerical summaries are
  development-only.

### T2 — paper-scale expansion

- Multiple laboratories, mechanism families and participant populations; at least one non-market strategic
  environment for an NMI route.
- Paid proprietary order-level or laboratory data only after free-data transfer succeeds and licensing permits
  reproducible derived artifacts.
- Human data require ethics/licence review before any processing beyond public de-identified replication files.

## 8. Conditional compute needs

### T0 — authorized now

- Mac CPU <=30 core-hours; 0 GPU-hours; no remote worker contact.

### T1 — free-data development after gates

- 200--1,000 CPU core-hours for hierarchical inference, resampling and reconstruction.
- Up to 100 aggregate V100-equivalent hours only if a learned representation is scientifically necessary.
- The RTX2060 may run compatibility smoke jobs or CPU analysis; it is not a required worker.

### T2 — controlled agent-population generation

- Classical agents: 500--5,000 CPU core-hours and 100--500 V100-equivalent hours depending on policy learning.
- Open-weight agentic AI: provisional 500--5,000 V100-equivalent hours after a measured tokens/episode benchmark;
  independent model/task/seed arrays, exact prompt/version logging and no H20 assumption.
- Commercial APIs require a separate monetary and reproducibility gate; no purchase is implied.

### T3 — Nature-scale confirmation

- Budget from measured T2 scaling, potentially 5,000--30,000 V100-equivalent hours plus 50,000--500,000 CPU
  core-hours across additional heterogeneous non-H20 workers.
- Compute scale cannot substitute for human replication, treatment identification or open traceability.

## 9. Stop rules and chronology

- Freeze and push this plan before reading candidate outcome values or forming a preferred empirical direction.
- Complete primary-source and official-repository audits before downloading any dataset.
- If all P1--P3 fail S0, D0 or I0, close v4 with no experiment and choose a genuinely different phenomenon.
- Do not run LLM populations to generate an attractive result before fixing the human/classical comparator and
  discriminating estimand.
- Do not make humans, algorithms and LLM agents commensurate by z-scoring incomparable tasks after seeing results.
- Preserve v1--v3 and all failed candidates append-only in the source/failure ledgers and knowledge graph.
- Update `docs/research_lineage.md`, `logs/2026-08-13.md` and `.claude/memory/` after every v4 work session.

## 10. Post-freeze outcome — 2026-08-13

**Decision:** `V4_NO_SURVIVOR`. Full audit: `research/theory_exploration/phenomenon_audit_v4.md`.

- P1 is `RETIRED_PRIOR_ART`: dynamic human/LLM market comparison, institution-dependent human/LLM differences,
  large-scale treatment-effect prediction and classical-agent market comparisons occupy the broad response-spectrum
  framing. V4 specified no new signed cross-population law, and no free development-plus-sealed matched pair exists.
- P2 is `RETIRED_PRIOR_ART`: a direct matched-protocol study already reports aggregate cooperation agreement with
  individual heterogeneity and conditional-rule mismatch. Generic aggregation loss remains standard information,
  ecological-inference or partial-identification theory.
- P3 is `RETIRED_NO_WITNESS`: no free randomized memory-break/replay market dataset with raw trajectories and an
  independent replication was identified. A session or price reset is not a causal erasure of strategy memory.
- Interference-aware LLM surrogacy is a legitimate open technical extension, but the obvious route is a composition
  of existing surrogacy and marketplace/network-interference results. No non-equivalent NMI theorem or NCS data
  contract survived.

No experiment was preregistered or run. No outcome file, paid data, API, worker, V100, RTX2060 or GPU queue was
opened. A successor iteration may audit endogenous market-rule feedback, but v4 does not admit or authorize it.
