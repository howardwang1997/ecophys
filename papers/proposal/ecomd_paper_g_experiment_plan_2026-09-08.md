---
document: Paper G prospective experiment plan
version: 0.1
date: 2026-09-08
status: proposed_not_frozen_not_execution_authority
parent_screen: discovery_cycle_17_20260908
candidate: paper_g_execution_constrained_online_market_making
depends_on_paper_e_results: false
depends_on_paper_f_results: false
outcomes_accessed: false
experiments_run: 0
---

# Paper G: prospective experiment plan

Execution follow-up, 2026-09-08: the PI subsequently requested execution. A separate
bounded development decision authorized reference implementation and the first pilot;
the [private development review](../../logs/private/paper_g_development_20260908/development_review.md) records
its completion and no-scale-up disposition. The full matrix below remains an unfrozen
proposal; it has not been run or promoted to confirmation.

## 1. Aim and decision sequence

Test whether execution-constrained inventory recovery changes the cost of learning a
market-making policy under limited feedback. Separate **the market's attainable value**
from **the learner's gap to that value**. A harder market can reduce both the learner's
and the oracle's wealth without making learning harder.

This plan completes the PI's experiment-planning request. It is a proposed design, not
a preregistration, execution decision or claim that the candidate has passed novelty.
G is independent of E/F results and confirmation data. Existing order/accounting code
may be reused after separate qualification for G's model.

The decision sequence is:

| Stage | Question and deliverable | Condition to proceed |
|---|---|---|
| G0: paper-only model/theory gate | Exact state, feed, comparator; parent reductions; a distinct proposition | A market-specific result beyond existing theory, with a credible proof route |
| G1: exact reference qualification | Transition table, dynamic-programming oracle, independent event implementation | Same estimand and legal transitions verified; reference error bounded |
| G2: development and precision pilot | Small factorial experiment; fixed algorithms; variance and runtime estimates | Identifying contrasts remain meaningful and confirmation fits budget |
| G3: frozen confirmation | Fixed sample size, all declared cells, interaction and regret estimates | Report the entire result, including nulls; no outcome-driven expansion |
| G4: one optional mechanism extension | An independently specified queue/depth or price-risk model | G3 supports the declared claim and the extension answers a named limitation |

Only G0 paper work is within the present planning/screening scope. Later execution
requires the applicable current machine decision. The concrete plan is provided now;
no permission request or experiment launch is part of this task.

**Important G0 check:** the minimal market below is deliberately a small, fully
observed controlled Markov model. Inventory and depth yield at most `4(Q+1)` states.
Merely deriving sublinear regret for that model is not a new result: generic
communicating-MDP theory already provides it
([Jaksch, Ortner and Auer, 2010](https://www.jmlr.org/papers/v11/jaksch10a.html)).
A sharper structural dependence or distinct lower bound must survive the parent
comparison. If it does not, stop the proposed G contribution before G1; do not enlarge
the market just to hide the reduction.

## 2. Minimal market M0: a dealer with an executable hedge venue

### Why start here

Use one asset, one learning dealer, exogenous customers and a separate hedge venue.
This is an explicitly segmented dealer market: customers contact the dealer, while
the dealer can submit orders to the hedge venue. It is **not** a single consolidated
public limit-order book, nor a model of strategic customer routing. This restriction
keeps the oracle exact and the information treatment interpretable.

Two channels also avoid an ill-posed execution ablation: changing hedge availability
does not silently change which competing quote a customer must execute against.
All customer transactions still transfer cash and inventory to funded counterparties.

### Proposed constants and laws

All prices are integer ticks; one order is one unit of the asset. Constants are
design choices, not fitted market estimates.

| Object | Proposed definition |
|---|---|
| Reference value | Fixed `m=100`; no price risk or adverse selection in M0 |
| Dealer quotes | Bid in `{off,98,99}`; ask in `{off,101,102}` |
| Hedge quotes | Bid 99 and ask 101, each with capacity zero or one |
| Inventory | Long-only `0 <= q <= Q`, `Q in {2,8}`, initial `q=1` in every core cell |
| Initial hedge depths | `(d_bid,d_ask)=(1,1)` |
| Replenishment | Each vacant hedge side independently refills by one with probability `rho`; occupied depth remains one |
| Scarcity treatment | `rho=0.1` versus `rho=1.0`; identical hedge prices and unit action size |
| Customer arrivals | Exactly one independent opportunity per round; customer buys with probability `nu`, otherwise sells |
| Customer willingness | Buyer accepts up to 102 with probability `theta_b`, otherwise 101; seller accepts down to 98 with probability `theta_s`, otherwise 99 |
| Regime R1 | `nu=0.5, theta_b=0.55, theta_s=0.55`: balanced, near quote indifference |
| Regime R2 | `nu=0.8, theta_b=0.75, theta_s=0.25`: directional flow and asymmetric willingness |
| Fees | Zero in M0; hedge spread remains a real transaction cost |
| Horizons | Independent horizon-aware runs at `T in {1024,4096,16384}` |

The customer parameters are unknown to the learners. They know the event grammar,
prices, capacity and the chosen replenishment rule. Regime labels and true parameter
values are evaluator metadata, not learner input. A declared common model class must
contain all confirmation regimes; the learner cannot be told the two true parameter
triples. The model class, estimator and prior are G0/G2 freeze dependencies.

Dealer cash is tracked, never borrowed. Set the same initial cash in every M0 cell to
`C0 = 103 * (2*T_max + Q_max)`. At most two dealer purchases can occur per round, each
costing less than 103, so this is a finite prefunding bound that makes cash nonbinding.
This deliberately isolates inventory capacity; M0 is not a joint cash-scarcity study.
Customer and hedge counterparties are also prefunded for the entire declared horizon;
replenishing displayed depth moves existing resources into orders, not into existence.

### Within-round event order

1. Observe the current hedge depth, own inventory/cash and all prior permitted receipts.
2. Choose a joint action: hedge one unit in either direction or do nothing, plus a
   bid/ask pair. There are at most `3*3*3=27` actions before feasibility filtering.
   Validate the hedge against visible depth and inventory, then validate quotes
   against the resulting inventory. A buy quote at Q and sell quote at zero are illegal.
3. Execute the selected hedge at 99 or 101 against available depth. No fill is invented
   if depth is absent. Post the feasible customer quotes.
4. Draw the customer side and private willingness. Reveal the request side after the
   dealer's action is committed, then execute at the posted quote if acceptable.
   No intra-round requoting is allowed. At most one customer unit trades; an unaccepted
   request does not rest.
5. Cancel any remaining dealer quotes. Settle and record all cash/inventory transfers.
6. Replenish vacant hedge depth according to the frozen rule and release the permitted
   feedback. The new depth is visible before the next action.

No inventory or learned state resets within a T-round run. Independent replications
start anew; algorithm replanning blocks do not. Each horizon run is initialized
separately and both learner and oracle know its horizon. Prefix plots from a long run
cannot be substituted for shorter horizon-aware experiments.

### Information treatments

- **F_actual:** own orders, fills, inventory/cash, displayed hedge quotes/depth, the
  fixed opportunity clock and each request's side after the action, including nontrades.
  Private customer willingness is not supplied. The dealer retains all implications
  of fills and nonfills; it does not receive shadow-strategy rewards. Request side is
  included because hiding it from a contacted dealer would be an artificial restriction.
- **F_reveal:** exactly F_actual plus the realized customer willingness,
  released only after the current action and execution. This is a labelled synthetic
  information-oracle arm, not an assertion that a normal market publishes valuations.

The latent customer draws are independent across rounds. Consequently, for a policy
that already knows their law, extra *past* willingness information does not improve
future decisions in M0. The known-law optimal value is therefore the same in the two
feedback arms at fixed Q/rho/regime. This is an analytic check of the information
treatment, not a promised result for persistent hidden-state extensions.

The complete evaluator tape and learner feed must be separate interfaces. If the
declared actual feed permits full counterfactual reconstruction, retain that fact and
reassess the question; do not conceal available fields to manufacture difficulty.
Private-valuation feedback has direct precedents, including
[Cesa-Bianchi et al., COLT 2025](https://proceedings.mlr.press/v291/cesa-bianchi25a.html)
and a different observation model in
[Maran and Restelli, 2026](https://arxiv.org/html/2605.19584v1).

## 3. Oracle, learning gap and statistical target

For known parameters, the observable decision state is `s=(q,d_bid,d_ask)`. Cash can
be removed from the dynamic program only after the prefunding proof above is checked.
The joint transition/reward kernel includes hedge consumption, customer response and
depth replenishment. Terminal excess reward is zero, with per-round reward

`r_t = C_(t+1)-C_t + 100*(q_(t+1)-q_t)`.

Thus total reward equals `W_T = C_T-C0 + 100*(q_T-q0)`. It is marked wealth, **not
realized liquidation profit**. Hedge trades lose one tick each; customer fills earn
one or two ticks. M0 per-round reward lies in `[-1,2]`.

Use finite-horizon backward induction:

`V_0(s)=0; V_h(s)=max_legal_a E[r(s,a,z)+V_(h-1)(s')].`

The oracle knows the probability law but not future customer or replenishment draws.
It obeys the same inventory, depth, prices, action grammar, horizon and terminal
objective. Do not optimize its actions against a realized future tape.

For method A, estimate `R_T^A = V_T(s0)-E[W_T^A]`, and report `r_T^A=R_T^A/T` in
ticks per opportunity. Sample regret can be negative through sampling noise; preserve
it. An uncertified approximate oracle yields an interval for regret, not an exact label.

The proposed primary *operational* contrast uses the predeclared structured posterior
sampler at `T=16384`:

`Delta = (r_actual,scarce - r_reveal,scarce)
       - (r_actual,abundant - r_reveal,abundant)`.

Average this contrast with equal weight across the four Q-by-regime strata. Report
each stratum as well. Positive Delta means the observed feedback disadvantage is
larger under scarce recovery **for that method and model**. It does not establish
a minimax lower bound, algorithm-independent impossibility, or real-market effect.
The theoretical claim must be supplied by G0, not inferred from an interaction plot.
Use a two-sided interval; do not assume the sign before a theorem warrants it.

Secondary measurements: each arm's oracle value and learner wealth; regret across
horizons; inventory-boundary occupancy; hedge use and cost; customer fill rate;
time to a feasible inventory recovery; planning time and peak memory. Recovery-time
summaries must retain right-censored episodes instead of dropping nonrecoveries.
Constraint violations must be zero for scientific runs. Endpoint definitions and
normalization stay fixed across methods.

## 4. Baselines and interpretation

| Method | Role and requirements |
|---|---|
| Known-law DP | Exact reference; privileged parameter knowledge, never a competitor trained on the same budget |
| Structured certainty-equivalent learner | Fit the declared censored likelihood, plan using its estimate; predeclared exploration schedule |
| Structured posterior sampler | Update the same model using the actual permitted likelihood; sample and replan on a frozen schedule; primary interaction probe |
| Tabular optimistic control | Strong generic MDP baseline using observable transitions and legal actions; UCRL2-type continuing control with assumptions and solver accuracy documented |
| Optional fourth learner | New algorithm only if G0 supplies one, otherwise a frozen inventory-skew rule; never an unnamed placeholder at freeze |

Posterior sampling is established methodology
([Osband, Russo and Van Roy, 2013](https://arxiv.org/abs/1306.0940)). A continuous-run
adaptation with replanning does not inherit an episodic theorem automatically.
Likelihoods must condition on the observed request side and marginalize any remaining
hidden willingness consistent with fills/nonfills; Bayesian parameter
uncertainty is distinct from a hidden physical market state. F_reveal learners must
actually use the extra observation; a tabular learner that discards it is labelled
as such and cannot measure its optimal information value.

Inventory-aware online market making is already covered by
[Xue, Du and Xu, AAAI 2025](https://ojs.aaai.org/index.php/AAAI/article/view/35492).
Stateful expert aggregation also appears in
[Abernethy and Kale, NeurIPS 2013](https://papers.neurips.cc/paper/4910-adaptive-market-making-via-online-learning.pdf).
Their algorithms can be reproduced in their own declared model as separate calibration
work. If their required counterfactual expert rewards or rebalancing actions are
unavailable in M0, do not silently modify them and label the modification the original
baseline. An adapted feasible expert method needs its own specification.

All learned policies receive the same number of environment interactions. Hyperparameter
search has the same proposed ceiling of eight settings per method, selected only on
development seeds by mean actual-feed regret over the declared development cells.
Share the chosen tuning across feedback/scarcity arms for the primary contrast.
Report planning time separately: equal samples do not mean equal compute. Freeze
optimizer accuracy, prior/model class, action mask, replanning schedule, tie-breaking
and exploration before confirmation. A PPO comparison is optional G4 work, not a
substitute for these small-model control baselines.

## 5. Staged experiment matrix

| Experiment | Design | Decisive use |
|---|---|---|
| E0: analytic and reference checks | Q=2; short horizons up to 8; enumerate all reachable legal transitions and small policy trees | Cash/inventory conservation, exact finite-horizon values, no clairvoyance; compare two independently written transition paths |
| E1: small development factorial | Q=2, R1, both feedback arms, both rho values; 8 independent development seeds; T=1024 | Does the contrast isolate information/recovery? Check parameter learning and whether oracle/learning separation is meaningful |
| E2: confirmation | 2 Q values × 2 regimes × 2 feedback levels × 2 rho values = 16 cells; three horizons; up to four methods | Regret and the prespecified feedback-by-recovery contrast |
| E3: one bounded robustness panel | Mirror R2's buy/sell law and transform initial inventory to `Q-q0`; then either a modest terminal-inventory penalty OR one replenishment-law change | Detect directional and objective/model dependence; select the panel before confirmation outcomes |
| E4: optional order-book extension | Single CDA, labelled queue positions, cancellations and a separately qualified comparator | Test a specific surviving mechanism beyond dealer segmentation; no automatic sim-to-real inference |

E0 is private reference qualification, not scientific evidence based on engineering
incidents. Public results come only from the valid frozen protocol. E1/E3 development
work remains labelled development; it is not independent confirmation.

For E0, compare exhaustive enumeration with the DP; proposed total oracle-value
error bound is `<=1e-8` ticks on the small rational-probability fixtures. For longer
horizons, certify accumulated numerical error below `0.001*T` ticks, one twentieth
of the proposed detectable contrast scale. Bellman residuals, numerical error bounds
and independent checks must justify the tolerance; solver termination alone cannot.
An event engine wrapping the same transition function is not an independent check.

## 6. Splits, uncertainty and stopping

Use distinct, disjoint namespaces for engineering fixtures, tuning, the variance pilot
and confirmation. Proposed seed coordinates are:

- Development/tuning root IDs: 710000–710015.
- Precision-pilot root IDs: 720000–720011; variance estimation only after methods lock.
- Confirmation root IDs: 730000–730127; an eventual frozen prefix of length N.
- Robustness-development root IDs: 740000–740015.

These are proposed identifiers, not generated data or sealed outcome files. Before
freeze, check namespace collisions and commit the exact manifest, generator, model
and analysis hashes. Never access E/F campaign or verification-liquidity holdouts.

Customer side, willingness, replenishment and algorithm randomness use separate keyed
streams. Derive each exogenous draw from replicate/stratum/stream/event index; common
uniforms couple treatments without depending on the policy's number of RNG calls.
This pairing is valid because M0's external innovations are exogenous by construction.
Replay the inputs through each policy's own state; do not reuse another policy's fills.
Different horizons are separate runs with common prefixes allowed; cluster analysis
at the independent root-replicate level, not at individual time steps.

Proposed practical contrast scale: `delta=0.02` ticks per opportunity. This is a
design precision target, not an estimate of likely effect or an economic-profit claim.
Target two-sided alpha=0.05 and nominal 80% power. Use the 12 pilot replicate-level
contrasts to obtain a conservative upper estimate of their standard deviation; under
the normal approximation, use the one-sided 95% chi-square variance bound. Plan

`N_required = ceil(((1.96+0.8416)*sigma_upper/delta)^2)`.

Choose the smallest of `{32,64,128}` meeting this rule and the runtime budget, then
freeze it before any confirmation outcomes. Pilot effect signs must not select cells
or the hypothesis. If none fits, report a precision/budget failure and revise
prospectively; do not quietly call N=32 adequately powered. Validate the approximation
using pilot diagnostics; rare-event or highly skewed contrasts require a different
prospectively documented precision calculation, not an unsupported power guarantee.

Report the primary paired mean and a 95% replicate-level t interval. The four stratum
contrasts are a declared secondary family with Holm correction if significance claims
are made. Other curves are descriptive intervals. The intervals quantify simulation
sampling uncertainty over the fixed design, not a population of real markets.
No optional stopping on p-values or selective removal of poorly performing seeds.

Infrastructure interruptions resume the same immutable run and random state. Record
all attempted cells. A scientific run with invalid protocol semantics is quarantined
in private records; a corrected protocol receives a new version and prospective
decision. Invalid development history is never scientific motivation or evidence.

## 7. Compute plan and reproducibility

M0 is principally CPU work. Use the CPU resources of the two V100 workers for batches;
the Mac handles editing and small metadata checks. GPU training is unnecessary for
E0–E2, regardless of the workers having V100s. This keeps G independent of E/F's
training schedule and avoids making a neural-network benchmark the core claim.

With four methods, E2 requires

`16 cells * 4 methods * N seeds * 3 horizons = 192*N runs`,

`16 * 4 * N * (1024+4096+16384) = 1,376,256*N dealer rounds`.

| N | Runs | Dealer rounds |
|---:|---:|---:|
| 32 | 6,144 | 44,040,192 |
| 64 | 12,288 | 88,080,384 |
| 128 | 24,576 | 176,160,768 |

A dealer round contains multiple engine messages; these are **not** raw engine-event
counts or runtime estimates. Oracle construction, replanning and tuning are additional.
Only eight Q/rho/regime DP problems are needed for M0 because the known-law value is
feedback-invariant; time-homogeneous value iteration over remaining horizon provides
all three T values. Cache certified oracle arrays by complete model hash.

Proposed budget ceilings, not measured requirements or authorization:

- E0 reference qualification: 8 CPU core-hours.
- E1, tuning, precision pilot and throughput calibration together: 32 CPU core-hours.
- E2: 64 CPU core-hours, including confirmation planning overhead and oracle work.
- E3/E4: outside the core budget; no implicit allocation.
- Optional later neural extension: first a 2 V100 GPU-hour throughput pilot, then at
  most 24 V100 GPU-hours including that pilot, only if a distinct experiment warrants it.

Use a representative maximum-Q, longest-horizon pilot on each prospective worker.
Estimate node wall time from measured end-to-end jobs, including planning, and allow
a 1.5 scheduling margin. If projected work exceeds a ceiling, reduce/revise before
confirmation freeze or obtain a changed budget; never drop completed unfavourable cells.
No worker availability or throughput has been measured in this planning session.

### Resource envelope and elapsed-time interpretation

For initial scheduling, propose eight single-thread CPU worker processes, 16--32 GiB
aggregate RAM and 50--100 GB free disk across the assigned workers. These are provisional
allocations, not measured minimum requirements or a claim of currently free capacity.
Use existing V100 hosts' CPU resources; no new GPU or server purchase is proposed.
Profile planning memory and I/O before fixing concurrency. Bound library thread pools
so eight processes do not each create an additional eight CPU threads.

The core data are synthetic customer/replenishment innovations, executions, inventory,
learner decisions and certified oracle arrays from this model. They require no purchased
tick data, external market-feed download or E/F result files. Small immutable seed/model
manifests specify replayable inputs; persist outputs and provenance separately.

Storage depends on logging granularity. For illustration, 128 bytes per dealer-round
record would occupy about 5.64 GB at N=32 and 22.55 GB at N=128, before checkpoints,
indexes and extra messages. This is an arithmetic scenario, not a measured record size.
Full JSON event logs can be much larger. Measure bytes per round in the pilot; set a
retention/storage contract before confirmation, never delete inconvenient outcomes.

The stage ceilings sum to 104 CPU core-hours. **If** the pilot shows the selected
campaign fits that ceiling and exposes eight effective parallel cores, the ideal
elapsed-time equivalent is 13 hours; applying the proposed 1.5 scheduling allowance
gives 19.5 hours. With sixteen effective cores the corresponding numbers are 6.5 and
9.75 hours. These are conditional budget conversions, not throughput forecasts:
serial oracle work, replanning, memory limits, idle capacity and I/O can change them.
No measured end-to-end completion date can be given before the implementation and pilot.
The G0 theory gate, implementation, reference qualification and result analysis are
additional work; an approximately one-day compute allocation is not a one-day Paper G
completion promise.

Later execution uses Conda, immutable code/config/input hashes, worker-local inputs
staged from R2, independent job arrays, recorded thread counts, and checkpoints at
least every 30 minutes containing market, learner and RNG state. No DDP is needed.
Keep the A800 in a separate optional pool and do not assume H20. Runtime credentials
and host inventory stay outside tracked research files. Local manifests are canonical;
W&B is optional, with a run URL or an explicit disabled value recorded.

## 8. Implementation boundaries and freeze checklist

Existing reusable components: `scripts/lab_asset/schema.py`, `matching.py`,
`replay.py` and their order/accounting tests. Read-only inspection confirms that
the engine checks cash and available inventory; a G-specific *current inventory*
upper bound must be explicitly enforced. Induced cumulative purchase capacity is
not equivalent to `q<=Q` after repeated buys and sells.

Prospective additions, not built by this plan: a two-channel M0 adapter, a learner-feed
projector, a separately implemented tabular kernel/DP oracle, method runners and an
analysis script. Existing G-independent frozen fixtures are not mutated. A marketable
limit order followed by cancellation may implement the required immediate-or-cancel
semantics only after its event and information timing are verified.

Before execution, freeze the model contract, action/event ordering, exact parameter
class/prior and inference, all method definitions, independent reference receipts,
oracle tolerances, sample size and seed hashes, primary/secondary estimands, budget,
hardware assignment, analysis outputs and applicable machine decision. These are
specific unresolved prerequisites; this draft is not labelled ready-to-run.

No new data purchase or empirical outcome access is needed for M0. Synthetic provenance
must record source protocol, authorship, code SHA, generation date, parameters and
preprocessing hash. Any later real-data or external-code use needs its own rights and
same-estimand contract. M0 cannot support claims about actual trading profitability,
collusion, crash response or cross-market universality.

## 9. Expected artifacts and interpretation of every outcome

1. A formal model/theorem or a documented parent reduction that stops G.
2. A qualified exact benchmark and the independent execution reference, if G0 passes.
3. Main figure: oracle value alongside learner regret across the four feedback/recovery
   arms, preventing wealth loss from being confused with learning loss.
4. Main figure: the primary interaction and all Q/regime strata with uncertainty.
5. Supporting figure: regret versus horizon and planning-cost frontier; fitted slopes
   alone are not evidence of an asymptotic exponent.

If the interaction is near zero with sufficient precision, rule out effects of the
declared magnitude for this method/model; do not conclude constraints never interact.
If it is large but generic control explains it, retain a benchmark result without a
new-theory claim. If a distinct theorem survives and the exact experiment supports its
specified boundary, proceed to a single predeclared extension. These outcomes all
change a research decision; only the last currently supports the intended Paper G case.

The companion YAML is a planning manifest for dimensions and budgets. No executable
Hydra config, training code, result, new search cycle, forecast or route activation
is created by this planning record.
