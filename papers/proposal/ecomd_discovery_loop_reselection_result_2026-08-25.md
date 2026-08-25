# EcoMD discovery-loop audit and first successor-topic selection

**Date:** 2026-08-25
**Outcome access:** none
**Execution:** no simulator, model implementation, dataset download, EcoMD change, or GPU
**Initial decision:** install a forward-only discovery contract; park one narrow residual below the activation floor
**D-1 continuation:** the generic residual is failed-closed after theorem, simulator-contract, and real-bridge audit

## 1. Identity and capability audit

[Discovery Loop](https://www.discoveryloop.com/) is a new organization whose public page
describes large-scale propose--run--learn loops. It currently supplies a vision rather than
a public implementation or benchmark. It has no verified organizational relationship to
the [Science-Discovery](https://github.com/Science-Discovery) GitHub organization.

Science-Discovery's [Aether](https://github.com/Science-Discovery/Aether) is a research
workbench, while [AI-Newton](https://github.com/Science-Discovery/AI-Newton) stores concepts
and symbolic laws and rediscovers classical mechanics inside a supplied experiment library
and DSL. Both contain reusable design ideas; neither validates open topic selection.

The requested title [*Measuring AI Scientists: From Exams to
Discovery*](https://doi.org/10.26434/chemrxiv.15007582/v1) is a ChemRxiv v1 Perspective
posted on 2026-08-18, not a released benchmark. Its formal metadata lists nine authors and
does not include Frances H. Arnold; the earlier MIRA reference list contains a ten-author
version and should not replace the formal v1 record. The Perspective proposes the
`discovery episode`--hypothesis generation, computational or experimental execution,
interpretation, revision, nulls, failures, and provenance--as the evaluation unit. It
provides no task set, scorer, code, leaderboard, or reliability study.

The executable landscape supplies different pieces:

- [HLE](https://doi.org/10.1038/s41586-025-09962-4) measures expert closed-ended
  academic knowledge and calibration, while
  [FrontierScience](https://arxiv.org/abs/2601.21165) supplies original problems and
  PhD-level research subtasks. Neither tests autonomous topic choice plus experiment and
  revision.
- [Scientific Discovery Evaluation](https://arxiv.org/abs/2512.15567) separates scenario
  questions from eight project-level propose--oracle--refine loops. Supplied oracle
  optimization is not topic novelty or causal validity.
- [ResearchBench](https://aclanthology.org/2026.findings-acl.644/) decomposes ideation into
  inspiration retrieval, hypothesis composition, and ranking, but uses published successful
  hypotheses as gold and stops before execution or external feedback.
- [AutoDiscovery](https://github.com/allenai/asta-autodiscovery) searches a hypothesis tree
  with belief change as an acquisition score. Surprise may prioritize exploration but does
  not confirm truth, novelty, or importance.
- [AI Scientist v2](https://github.com/SakanaAI/AI-Scientist-v2) contributes an experiment
  tree, parallel branches, debugging, and abandonment. Its own documentation reports lower
  success than a strong template, warns about model-written code, and uses a custom license;
  EcoMD does not vendor it.
- [DiscoveryWorld](https://github.com/allenai/discoveryworld),
  [DiscoveryBench](https://github.com/allenai/discoverybench), and
  [ScienceAgentBench](https://github.com/OSU-NLP-Group/ScienceAgentBench) make actions,
  workflow, outputs, and cost measurable, but largely evaluate fixed worlds or
  rediscovery of published work.
- [BAISBench](https://doi.org/10.1093/bioinformatics/btag227) and
  [ResearchClawBench](https://arxiv.org/abs/2606.07591) are stronger data/code/report
  evaluations, but their scientific targets are established conclusions from published
  studies. [NLPCC 2026 Task 9 AISB](https://github.com/ResearAI/NLPCC-2026-Task9-AISB)
  is a separate shared task with replay and fabrication checks, not the implementation of
  the ChemRxiv Perspective.
- [petri-bench](https://www.petri-labs.org/bench/report) already provides procedurally fresh
  causal-discovery tasks over five simulations including a market, objective process
  scoring, and a multiplicity audit. Its simple controlled-design baseline substantially
  outperforms the reported frontier agents. A new hidden-parameter MarketScienceBench is
  therefore closed as a topic.

The exact version, license, use, and limitation of every adopted source are frozen in
`research/discovery/evidence_registry.yaml`.

## 2. Installed discovery contract

The new forward-only protocol separates six stages:

1. D-3 freezes a market-native object, intervention, observable, invariances, exact
   question, directional claim, and nonclaims.
2. D-2 runs literature- and data-driven exploration separately, compiles at least 15
   primary works, and maps the route graph's failures to canonical families.
3. D-1 applies exact-prior and parent-problem reductions, at least two killer tests,
   two-system and real-observation contracts, contamination controls, and hostile
   probabilities before outcomes.
4. D0 freezes the estimand, budgets, baselines, splits, hashes, stop rules, and authorized
   actions.
5. D1 preserves every exploratory branch without using it as confirmation.
6. D2 reveals a simulator-family, mechanism, time, market, or vendor holdout and produces a
   claim-to-evidence ledger with calibrated abstention.

An active card needs a hostile T0 lower bound of at least 15%, no unresolved direct
collision, two survived killer tests, two independent simulator lineages, a qualified real
bridge, distinguished inherited failures, contamination control, and an outcome-blind
decision. Active authorizes only listed actions. The protocol, topic cards, novelty
manifest, evidence registry, failure-family registry, decision, validator, and mutation
tests are separate from the terminal route graph.

## 3. First question generated under the contract

The broad question “Can an AI scientist discover laws in a simulated market?” fails. In
addition to petri-bench, [NewtonBench](https://arxiv.org/abs/2510.07172) already tests fresh
interactive law discovery, [CausaLab](https://arxiv.org/abs/2605.26029) tests active
mechanism recovery and transfer, [CausalDS](https://arxiv.org/abs/2607.08093) scores causal
identifiability and abstention, and [CausalGame](https://arxiv.org/abs/2607.04293) adds
confounding, selection, and measurement failures.

The only retained residual is narrower:

> Given independent adaptive market simulators with different states, clocks, and action
> grammars, discover a common interventional response law and its valid domain, or return a
> machine-checkable pair of worlds that are indistinguishable under the allowed experiments
> but separate under a target intervention.

For simulator \(M_k=(X_k,A_k,K_k,O_k)\), a state map
\(\tau_k:X_k\rightarrow Z\), intervention compiler
\(\omega_k:I\rightarrow A_k\), and response
\(R_k(i)=(\tau_k)_\#P_{M_k}^{\omega_k(i)}\), a law \(L\) would require a frozen bound

\[
\sup_{k,i\in I_{\mathrm{hold}}}d(R_k(i),L(i))\leq\epsilon.
\]

An abstention certificate instead supplies \(M,M'\), an allowed policy class
\(\Pi_B\), and \(i^\star\) such that accessible transcripts are within \(\eta\) for every
\(\pi\in\Pi_B\), while the target responses differ by more than \(\delta\).

The basic commuting diagram is already close to [causal exact
transformations](https://arxiv.org/abs/1707.00819), and generic cross-environment effects
are covered by [transportability](https://doi.org/10.1214/14-STS486). Recent
[multi-level causal embeddings](https://arxiv.org/abs/2602.22287) and
[unsupervised causal abstraction discovery](https://arxiv.org/abs/2606.19594) further
occupy common-model construction and learned macro-state maps. The residual would need a
new finite-sample selective guarantee for dependent market trajectories, unknown clock
maps, adaptive agents, partial observation, and approximate adapters. A Le Cam bound,
rank test, ordinary system identification, or causal abstraction restatement is a failure.

## 4. Frozen killer tests and contracts

`schedule_nullspace_alias` holds training schedules in a rank-deficient design. Two impact
kernels agree on every accessible schedule but differ on a hidden schedule. The system must
return the null-space direction and separating schedule, not a universal impact law.

`identity_clock_erasure` gives two markets identical aggregate flow and price tapes. One
responds to parent identity, splitting, and physical latency; the other responds only to
aggregate flow and event index. A held-out split/merge or event-rate intervention separates
them. Deleting identity or conflating event and physical time must force abstention.

Both tests are pending deterministic verifiers. The proposed independent lineages are
ABIDES at `f9cbe51342b7dedd9587e4e069040d68a5c6477f` and PAMS 0.2.2 at
`28cbb86192a019ddff00f9192d27e1ba87d381a8`. Their common state/intervention adapter is not
frozen, and no real L2/L3 intervention bridge is qualified. EcoMD remains ineligible for
identity-sensitive laws until its order-level observation semantics are established.

## 5. Decision

The narrow card is **parked**, not active. Its hostile T0 point estimate is 12%, with a
planning range of 7--18%; complete-paper probabilities are 3--4% for NMI and 1--2% for NCS.
These are judgmental planning probabilities, not empirical posteriors. The lower bound is
below the 15% activation gate, four close primary families remain unresolved, both killer
tests are pending, the two adapters are unverified, and the real bridge is absent.

No work is authorized under the parked card. Reconsideration requires, in this order:

1. a theorem skeleton demonstrably beyond causal abstraction, transportability, and
   ordinary system identification;
2. deterministic verifiers for both killer tests, each paired with an identifiable twin so
   that always-abstain cannot win;
3. a frozen ABIDES--PAMS same-estimand contract;
4. a credible real market observation and intervention bridge;
5. a recomputed hostile T0 lower bound at or above 15%.

## 6. D-1 continuation: terminal audit of the parked residual

The initial parked decision is retained above as the contemporaneous first-pass result. Its
frozen card hash was
`4637d74f6ad3a3af5922cbe87d9c0c3502d83986da70c255c4d4f481625b8c04`, and the parked
decision-file hash was
`ac9d31ba7ebba694c48650e542ec248556986c7d1044f3eb490292ff5586f5b6`. A second
outcome-blind D-1 audit then tested the four reopen requirements rather than treating
`parked` as a reserve that should eventually run.

### 6.1 The generic theorem does not survive reduction

For a budget-B adaptive transcript, a valid procedure must distinguish unconditional
false-law control from conditional selective risk. A genuine non-identification witness
must also separate the allowed probe set from the claim set: if the separating intervention
itself is queryable, exact transcript equivalence under every allowed policy is impossible.

Once this distinction is made, the strongest general construction is confidence-set
inversion. If `C_B` is a simultaneous world confidence set, output a law only when the
radius of its response image is at most the declared tolerance; otherwise return two
separated members. That is identified-set diameter plus reject-option inference. For two
worlds whose target responses are more than `2 epsilon` apart, standard Le Cam reasoning
bounds law coverage by transcript total variation plus `2 alpha`; exact-equivalent worlds
therefore make validity by nontrivial coverage impossible. The frozen schedule-nullspace
example is a rank certificate, while identity/clock erasure is a controlled probabilistic-
bisimulation or semi-Markov homomorphism witness.

The missing literature was decisive. [Dyer et al.](https://proceedings.neurips.cc/paper_files/paper/2024/hash/26b8e3dc3a21fcd660d80c63b767f324-Abstract-Conference.html)
already learn interventionally consistent abstractions for complex simulators and give
high-probability consistency over interventions of interest. [Acartürk et
al.](https://proceedings.neurips.cc/paper_files/paper/2024/hash/458fa8ee331566383d8e74bdb647f829-Abstract-Conference.html)
give finite-sample guarantees for interventional causal representation learning. UAI 2026
then directly combines multi-environment transport with adaptive causal-bandit intervention
([Park and Lee](https://proceedings.mlr.press/v337/park26a.html)), supplies anytime-valid
certification under adaptive intervention sampling ([Asiaee](https://proceedings.mlr.press/v337/asiaee26d.html)),
and corrects selective coverage when intervention invariances are learned
([Asiaee, Aryan and Long](https://proceedings.mlr.press/v337/asiaee26b.html)). The remaining
claim was therefore a composition of established modules inside market simulators, not a
new theorem class.

### 6.2 ABIDES and PAMS do not implement the frozen same estimand

The source-level contract fails without executing either simulator. ABIDES has nanosecond
send and arrival time, explicit latency, and asynchronous message delivery. PAMS 0.2.2 has
only a dimensionless market step and step-local order sequence. Multiplying a PAMS step by
an arbitrary number of seconds would fabricate rather than observe a physical clock.

PAMS also consumes one global scheduler RNG while permuting nonempty agent order lists and
deciding high-frequency admission. An intervention arm that emits an order and a sham arm
that emits an empty list therefore shift all subsequent scheduler draws. Repair requires a
new runner, clock, and RNG namespace, which would make the second mechanism our own fork
rather than an independent native validation system. ABIDES and PAMS are now rejected for
this strict card under `clock_domain_nonisomorphism`, `runner_rng_entanglement`, and
`parent_action_semantics_mismatch`.

### 6.3 No real bridge passes all contracts

The strongest field residual is a recurring CME Three-Month SOFR futures price-grid change:
contracts mechanically move from a 0.005 to 0.0025 IMM-index-point minimum increment when
they enter the final four months. It offers repeated known dates and possible future
holdouts. It is not a bridge for the generic card. CME's direct Market-by-Order feed omits
implied order-book liquidity, the intervention is nonrandom and coincides with maturity and
roll, neither simulator has the native CME allocation-plus-implied engine, and publication
rights for purchased and derived data are not frozen.

The ordinary headline is already saturated by futures tick-change studies, price-grid
clustering, pro-rata queue models, ex-ante optimal-tick prediction, and a recent CME SOFR
LOB simulator. The only residual worth hostile screening was a prospective transient law:
predict the full post-refinement response path from pre-change state and physical units,
then abstain under maturity, hidden-implied-liquidity, or grid-rebin aliases. An independent
20-work screen then found that the state and aggregate-flow inputs do not identify the
post-change placement policy, maturity is exactly collinear with treatment, and FIFO
simulator engines do not implement CME's allocation semantics. Its hostile T0 is only
4--12% (point 8%). No topic card was created, and it authorizes neither external outreach,
data purchase nor simulation.

### 6.4 Final decision

`transportable_interventional_market_law_discovery` is **failed-closed** at D-1. Revised
hostile T0 is 1--7% with a 3.5% point estimate; complete NMI is approximately 0.5--1.5% and
complete NCS 0.2--1%. No simulator, outcome, dataset, EcoMD model, or GPU was used.

A descendant can be considered only after a paper theorem supplies a market-specific
priority-and-clock criterion that is formally not ordinary controlled bisimulation, causal
abstraction, or transportability; provides polynomial law/separation certificates and
matching information bounds with nontrivial law coverage; and uses two native engines with
compatible physical clocks, action semantics, isolated RNG namespaces, and a qualified
prospective field bridge. Adding more adjectives to the generic card does not reopen it.
