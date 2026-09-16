---
document: Paper G initial topic screen
date: 2026-09-08
cycle: discovery_cycle_17_20260908
status: screening_only_F2_deferred
candidate: paper_g_execution_constrained_online_market_making
literature_cutoff: 2026-09-08
outcome_accessed: false
simulator_runs: 0
machine_cards: 0
---

# Paper G: Learning to Provide Liquidity under Execution and Inventory Constraints

## Subsequent resolution, 2026-09-08

The separately PI-authorized M0 investigation is now **closed as insufficient for
an independent innovative Paper G**. See the [formal resolution](ecomd_paper_g_m0_resolution_result_2026-09-08.md)
for the constructive probe, valid development results and precise reopening scope.
The front matter and initial decision below preserve the original paper-only screen;
they are not the current execution status. Maran–Restelli's publication status is
now verified as [COLT 2026, PMLR 336](https://proceedings.mlr.press/v336/maran26a.html).

## Initial screening decision

**Retain one conditional candidate; no topic has yet passed novelty qualification.**
The question is whether a market maker can learn a competitive quoting policy when
feedback comes from its actual information feed and fills, inventory is bounded along
the entire path, and changing inventory requires executable orders. The central output
would be a learning bound and a matching obstruction under a declared market model,
supported by an exact simulator experiment. This is a proposed result, not a finding.

Generic algorithmic collusion, inventory-aware learning, stateful expert switching,
and the value of order-book observations already have direct precedents. Combining
their names does not establish a contribution. The remaining candidate is worth a
bounded theorem/reduction investigation, not a GPU campaign or an announcement of
first-of-its-kind work. Its weakest link is an irreducible result beyond the parent
online-learning and control theories.

The PI's current request authorizes this paper-only screen. This record does not
replace the Paper E machine decision, change its preregistration, open a sandbox,
or authorize simulator execution, outcome access, implementation, or GPU work.

## Repository fit and route exclusions

- Paper E studies matching-fiber non-identifiability and its preregistered attribution
  experiment. Paper F is a concept about recording design and validation relative to
  an information floor. G would study **sequential trading decisions and their
  executable inventory paths**, not a new name for either recording problem.
- The existing lab-asset-v3 order lifecycle, integer quantities, matching, cash and
  inventory accounting provide relevant engineering assets. They do not yet supply
  the proposed learning algorithm, optimal-policy oracle, feedback contract, or
  independently certified second implementation.
- Exact event simulation would adjudicate a specified decision problem. EcoMD can
  become a downstream approximation only if that question survives; its learned
  output is not the truth oracle for the initial theorem.
- Route-graph screening excludes generic simulator audit, task-conditioned adequacy,
  prospective counterfactual validity, cross-simulator disagreement certificates,
  fixed-intent-tape field counterfactuals, differentiable counterfactual coupling,
  and renamed market-physics laws. No failed-closed formulation is reopened here.
  A new online learning estimand is being screened, not a new claim that a simulator
  identifies real-market policy responses. No qualified re-entry trigger is asserted.

## F0/F1 portfolio: six questions, five literature duplicates

This is a compact six-question cycle, not an unsaturated twelve-question harvest.
The twelve-program archetype sampling targets therefore do not apply. There are two
theory/mechanism, two measurement, and two simulator-method questions. No empirical
intervention is invented in the absence of an assignment/truth asset. Opposite
headlines in different trading games are not counted as a primary model disagreement.
The toys below are analytic screen witnesses constructed during this review; none
is a new theorem or a computational result.

### G01 — Learned coordination or ordinary competition?

- Native object: repeated quotes and one-agent quote deviations in a fixed dealer game.
  H1: a high-margin policy is sustained by future punishment; H0: margins arise from
  current inventory, adverse selection or the stage-game incentives.
- Discriminator: hold the game and information fixed and evaluate profitable unilateral
  deviations and their continuation responses. Positive value: identify a mechanism
  of coordination. Null value: rule out margins alone as evidence of collusion.
- Toy: in a repeated two-action game with payoffs CC=(2,2), DC=(3,0),
  CD=(0,3), DD=(1,1), grim-trigger cooperation requires
  `2/(1-delta) >= 3 + delta/(1-delta)`, hence `delta >= 1/2`.
  A payoff observation without continuation incentives cannot settle this condition.
- F1 anchors: S1, S2, S5. **Deduplicated**: broad collusion mechanisms and diagnostic
  ambiguity are occupied. Informed-speculator and dealer models cannot be combined
  as an opposite-sign same-estimand fork.
- Lane: market-native action or constraint. Archetype: theory_mechanism.

### G02 — Can ticks and execution priority suppress coordination?

- Native object: quote grid and allocation priority. H1: a finer grid increases the
  immediate gain from undercutting enough to disrupt coordination; H0: continuation
  incentives or allocation rules preserve it.
- Discriminator: a fixed repeated game with an explicit grid/priority intervention.
  Positive value: a mechanism-design condition; null value: a limit to tick-only policy.
- Toy: two zero-cost sellers split a unit demand at common price p, each earning p/2.
  A price-priority undercut by one tick earns p-tau, which exceeds p/2 iff tau<p/2.
  This is a stage-game incentive calculation, not a theorem about learning dynamics.
- F1 anchors: S3, S2. **Deduplicated**: tick size and execution competition are direct
  prior objects; changing a soft allocation parameter is not a new market mechanism.
- Lane: market-native action or constraint. Archetype: theory_mechanism.

### G03 — Do anonymous book messages still reveal coordinating identities?

- Native object: order sizes, displayed identities and subsequent quote responses.
  H1: size signals recover identity; H0: responses depend only on anonymous book state.
- Discriminator: preserve executable orders and permute labels in a declared model.
  Positive value: identify an information channel; null value: exclude that channel.
- Toy: if every policy is a function only of the unlabelled state and the matching
  kernel is label-equivariant, relabelling agents exactly permutes trajectories and
  leaves aggregate executions unchanged. A nonzero response needs a specified
  identity-dependent channel, not merely an anonymity label.
- F1 anchors: S4, S3. **Deduplicated**: anonymity and volume signalling already have a
  direct limit-order-book treatment. No new trader-identity truth asset was acquired.
- Lane: market-native action or constraint. Archetype: measurement_method.

### G04 — How costly is learning when inventory changes require actual execution?

- Native object: a feasible quote/order policy, its inventory path and received feedback.
  H1: jointly constrained execution and feedback create a distinct learning obstruction;
  H0: after correct state/comparator completion, existing control or resource-bandit
  guarantees already give the result.
- Discriminator: a proved separation or a constructive reduction on the same legal
  market model. Positive value: a necessary condition and attainable learning bound;
  null value: a precise applicability map for existing algorithms.
- First toy: with initial inventory Q, no borrowing and only customer buy arrivals,
  any feasible maker can sell at most Q units. Comparing it with an unlimited-inventory
  strategy that sells every round manufactures a linear gap. The same-constrained
  oracle also sells at most Q; that toy cannot prove linear learning regret.
- F1 anchors: S6, S7, S8. **Proceed to one F2 collision screen, then defer.** The broad
  components are occupied; the joint, market-specific residual is unresolved.
- Lane: new truth or control capability (existing exact event semantics, not a newly
  certified G oracle). Archetype: simulator_method.

### G05 — Can a spread/profit score certify collusion?

- Native object: a measured policy and its feasible deviation gain. H1: elevated
  spread/profit identifies coordination; H0: the same score is compatible with
  profitable deviations and non-collusive incentives.
- Discriminator: replace an outcome-only label by a same-game deviation calculation.
  Positive value: calibrated mechanism attribution; null value: invalidity of the score.
- Toy: in G02 with p=2 and tau=0.1, each tied maker earns 1, but unilateral undercutting
  earns 1.9. The observed positive profit does not certify even a stage-game equilibrium.
  This does not exclude a repeated-game equilibrium with credible punishment.
- F1 anchors: S5, S2. **Deduplicated**: generic genuine-versus-spurious collusion
  diagnosis is occupied; a benchmark without a new identifying contract is insufficient.
- Lane: market-native action or constraint. Archetype: measurement_method.

### G06 — Does observing more of the book improve learning?

- Native object: a declared observation feed with fixed order actions and rewards.
  H1: added observations strictly reduce learning difficulty; H0: they are redundant
  for the relevant decision problem.
- Discriminator: an information comparison with fixed environment and comparator.
  Positive value: justify a specific feed; null value: avoid unnecessary observation cost.
- Toy: if the richer observation deterministically contains the poorer one, every
  poor-feed policy is emulable by discarding fields. Optimal achievable regret cannot
  worsen with the richer feed under the same benchmark. Strict improvement requires
  a model-specific argument; the monotonicity itself is not a contribution.
- F1 anchors: S7, S6. **Deduplicated**: online market making and observation value have
  direct primary work. This is also too close to Paper F if recast as recording design.
- Lane: cross-domain theorem with market-specific obstruction.
  Archetype: simulator_method.

## G04 F2 contract and unresolved scientific boundary

### Native decision problem

Use a single-asset, finite-tick, unit-order market first. The scientific state contains
inventory, cash, outstanding orders, labelled queue position and external order state.
Actions are submit/cancel/replace and, if enabled, market orders that consume available
opposite-side depth at executable prices. No action resets inventory or creates a
counterparty. A hard capacity Q applies at every event. Cash feasibility and any short
inventory facility must be specified explicitly rather than inferred from a reward penalty.

Start with a declared stationary exogenous customer-order law. This is a tractable
laboratory model, not a claim about real strategic adaptation. Competing background
orders, cancellation and queue priority must be included in that law if used. Do not
add endogenous opponents, nonstationarity and market impact merely to evade a reduction.

The learner's feed is a named filtration: for example, top-of-book messages plus its
own accepted orders and fills. Hidden private valuations and counterfactual fill rewards
are not supplied implicitly. Whether queue position is observed is a material choice.
**This observation contract is still unresolved.** A full event feed under an exogenous
replayable order model may reconstruct counterfactual fills, eliminating the proposed
censoring. Artificially hiding information already available in the chosen feed would
not justify the claim. Coarser and richer feeds are different model contracts, not
evidence of implementation failure.

The comparator is the best feasible causal policy with knowledge of the order-arrival
law, the same initial resources, execution rules, observation feed and terminal rule.
It does not know future realized orders. Let

`R_T = V_T*(P, initial_state, feed, feasible_actions) - E_P[V_T(learner)]`.

Here V includes a declared common inventory valuation or liquidation rule. Marking
inventory to a reference price is an accounting objective, not an executable liquidation.
A liquidation objective must specify the auction/order process and what happens to
unfilled inventory. Comparing to best fixed feasible experts is an alternative narrower
problem and must be labelled separately; their counterfactual states are not free data.

### Competing explanations and decisive result

H0 is strong: correct state completion gives an ordinary controlled Markov model,
partial-monitoring problem, replenishable-resource bandit, or bounded-cost expert
switching problem. Their existing results suffice after parameter translation.
H1 requires something more specific: legal queue/execution constraints yield a provable
learning boundary or quantitatively sharper guarantee not supplied by those reductions.

Do not predeclare a new exponent, universal liquidity threshold or phase transition.
Capacity Q, the side-specific replenishment kernel, queue state and feasible recovery
orders are native controls. A fitted scalar called liquidity is not a complete state.
Changing the feed is an observation experiment; changing capacity or priority is a
market-rule intervention. These treatments must not be conflated.

**Second exact witness (not novelty evidence):** an own unit bid and one background unit
bid at the same price yield the same total displayed depth whether the background unit
is ahead or behind. A unit sell arrival fills the maker only in the latter case under
FIFO. Thus top price, total depth and own inventory do not determine the next fill.
Completing the state with queue rank repairs this example. If all proposed novelty is
this repair or a generic MDP reachability parameter, stop the G formulation.

**Third reduction check:** in a finite fully observed communicating model, generic
finite-state RL already supplies sublinear regret with state/action/reachability
dependence. An experimental square-root curve is not a new theorem. Conversely, an
irrecoverable inventory trap does not automatically establish a novel impossibility;
the same information and feasibility constraints must apply to the oracle, and the
result must be compared with existing noncommunicating-control lower bounds.

### Closest primary collisions

| Parent | What is already occupied | What G would still have to establish |
|---|---|---|
| S9, Abernethy–Kale (2013) | Stateful spread experts, inventory adjustment and low-regret aggregation; declared frictionless market-order execution | A result requiring actual depth/queue-limited recovery, beyond changing an assumption |
| S8, Xue–Du–Xu (2025) | Online market making with hard/soft inventory constraints and feasible reference strategies | A bound with the selected actual feedback and executable adaptation, rather than a renamed inventory constraint |
| S6, Cesa-Bianchi et al. (2025) | Regret guarantees and impossibilities with private valuations and limited feedback | Joint pathwise inventory/execution structure with a genuinely different theorem |
| S7, Maran–Restelli (2026) | Value of observation in online market making; an explicitly stipulated valuation-revelation model | A separately justified feed, not a claim that their stipulated observation is an error |
| S10, Cao et al. | Learning an unknown parameter in inventory-based Avellaneda–Stoikov control | Residual beyond parametric intensity learning |
| S11, replenishable knapsacks | Learning with resources that may replenish | Why inventory consumption/replenishment is not a direct instance with matching guarantees |
| S12, finite-state RL | Learning unknown communicating dynamics | A sharper market-semantic boundary, not just a larger state space |
| S13, switching-cost bandits | Costly adaptation and an established adversarial regret exponent | Why an executable inventory path is not reducible to the relevant switching-cost result |

This is an F2 collision screen, not a completed F3 audit. No prospective full-T0 forecast
was made; none is retroactively added. The number of primary works across the whole
portfolio does not imply a fifteen-work hostile audit of an exact G subject.

## Bounded next investigation and stop rules

1. **One model-contract session:** fix one feed, finite action/state model, feasibility
   rule, comparator and terminal objective. Check whether full replay supplies the
   supposedly missing counterfactual feedback. Deliver a two-page formal statement.
2. **At most two theorem sessions:** attempt the parent reductions and a smallest
   same-comparator counterexample. Continue only with a market-specific proposition
   and plausible proof route that survives S6–S13; otherwise close this formulation
   and retain the applicability map. A null reduction can be useful without becoming
   a standalone publishable paper.
3. **Only after qualification and the applicable machine decision:** implement a tiny
   exact dynamic-programming oracle and an independent event-level reference. Compare
   algorithms under equal interaction and tuning budgets, with explicit inventory
   violations, regret, queue accessibility and resource use. Factor feedback and
   recovery assumptions separately; idealized oracle arms are labelled ablations.
   Frozen development and untouched confirmation seeds/regimes precede outcomes.
4. **Scale only after a decisive small result:** current V100 workers can later run
   independent configurations if GPU training is actually needed. No defensible GPU-hour
   estimate exists before the model, algorithm and throughput are fixed. The first two
   steps require literature and proofs, not market data or training. A real-market or
   sim-to-real claim would require a separate qualified bridge and replication contract.

Stop if the result is a direct parent theorem; if superiority depends on free inventory
resets, fictitious liquidation, an infeasible oracle or a gratuitously censored feed; if
only one RL implementation performs poorly; or if no theorem distinguishes the proposed
mechanism from ordinary partial observation/reachability. Do not rescue a failure with
more agents, a different venue, a physics metaphor or a different neural architecture.

## Primary-source manifest

Accessed 2026-09-08. Full-text review and abstract-only checks are distinguished. This
is a targeted novelty screen, not an exhaustive literature review. No dataset outcomes
were acquired. Page-access counts below conservatively count nine retained successful
primary landing/full-text pages; search-only metadata and repeated page versions are
not included in that efficiency count.

| ID | Primary source | Access and scope |
|---|---|---|
| S1 | Dou, Goldstein, Ji, [AI-Powered Trading, Algorithmic Collusion, and Price Efficiency](https://www.nber.org/papers/w34054), NBER 34054 (2025) | Primary abstract through search; landing access blocked. Broad informed-speculator collision only |
| S2 | Cont, Xiong, [Dynamics of market making algorithms in dealer markets: Learning and tacit collusion](https://doi.org/10.1111/mafi.12401), Mathematical Finance (2024) | Primary indexed text; full landing access timed out. Broad dealer-learning collision |
| S3 | Cartea, Chang, Penalva, Algorithmic Collusion in Electronic Markets: The Impact of Tick Size; [author research page](https://patrickchang.net/research/) | Author abstract; publication status not asserted beyond working paper |
| S4 | Cartea, Chang, Graumans, [Anonymity, Signaling, and Collusion in Limit Order Books](https://doi.org/10.2139/ssrn.5080700) (2025) | Primary abstract and author page; [conference manuscript](https://microstructure.exchange/papers/Signaling.pdf) located |
| S5 | Calvano, Calzolari, Denicolò, Pastorello, [Algorithmic collusion: Genuine or spurious?](https://doi.org/10.1016/j.ijindorg.2023.102973), IJIO 90 (2023) | Primary indexed abstract/text; broad diagnostic collision |
| S6 | Cesa-Bianchi, Cesari, Colomboni, Foscari, Pathak, [Market Making without Regret](https://proceedings.mlr.press/v291/cesa-bianchi25a.html), COLT (2025) | Proceedings abstract and primary paper text |
| S7 | Maran, Restelli, [Online Market Making and the Value of Observing the Order Book](https://arxiv.org/html/2605.19584v1) (2026) | Full HTML; model/observation assumptions checked. Preprint status used |
| S8 | Xue, Du, Xu, [Adaptive Market Making with Inventory Constraints via Online Learning](https://ojs.aaai.org/index.php/AAAI/article/view/35492), AAAI (2025) | Full primary PDF; reference strategies, inventory and aggregation assumptions checked |
| S9 | Abernethy, Kale, [Adaptive Market Making via Online Learning](https://papers.neurips.cc/paper/4910-adaptive-market-making-via-online-learning.pdf), NeurIPS (2013) | Full primary PDF; execution framework and inventory rebalancing checked |
| S10 | Cao, Šiška, Szpruch, Treetanthiploet, [Logarithmic regret in the ergodic Avellaneda–Stoikov market making model](https://arxiv.org/abs/2409.02025) | Primary abstract; parametric-control collision, not full theorem audit |
| S11 | Bernasconi, Castiglioni, Celli, Fusco, [Bandits with Replenishable Knapsacks: the Best of both Worlds](https://arxiv.org/abs/2306.08470), ICLR (2024) | Primary abstract; exact reduction remains open |
| S12 | Jaksch, Ortner, Auer, [Near-optimal Regret Bounds for Reinforcement Learning](https://www.jmlr.org/papers/v11/jaksch10a.html), JMLR (2010) | Primary statement; generic finite communicating-state collision |
| S13 | Dekel, Ding, Koren, Peres, [Bandits with Switching Costs: T^{2/3} Regret](https://arxiv.org/abs/1310.2997), STOC (2014) | Primary abstract; not asserted to cover every state-dependent execution model |

Additional boundary searches located general partial monitoring, controlled-Markov-chain
adaptive control and closing-auction learning. These remain dependencies for a later
exact-subject audit, not completed reductions. The competition-without-collusion ICAIF
paper ([Wang, Ventre, Polukarov](https://arxiv.org/abs/2510.25929)) was checked at abstract
level; it is not counted as an opposite-sign fork with S1 because its game differs.

## Cycle receipt

Six raw questions; six quick screens; one F2 collision/contract screen; zero F3 audits;
zero cards. Five literature duplicates and one deferred candidate G04. Eight analytic
screen witnesses are recorded (six F1 plus two additional G04 checks); zero simulator
runs and zero outcome assets. Two reusable assets: the collision/applicability map and
the same-feasibility comparator/feedback checklist.

The route graph is unchanged: literature duplicates are not newly terminalized research
routes, and the deferred question has no machine status decision. No forecast is added.
The search-cycle ledger, daily log and canonical memory retain this nonterminal result.

Follow-up: the PI requested experiment planning. The separate
[prospective experiment plan](ecomd_paper_g_experiment_plan_2026-09-08.md) specifies a
minimal segmented dealer/hedge market, same-feasible DP oracle, feedback/recovery
factorial, sample-size rule and conditional compute ceilings. It is not frozen or
execution-authorizing and does not resolve the novelty gate above.
