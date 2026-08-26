# EcoMD Discovery Loop topic cycle 13: bilateral-credit liquidity

**Date:** 2026-08-26
**Literature cutoff:** 2026-08-26
**Mode:** outcome-blind, paper-only topic search
**Decision:** zero F3 audits and zero machine cards; three F2 formulations closed on state,
parent-problem, or observation-contract gates
**Authorization:** no simulator run, outcome access, dataset action, implementation, outreach,
sandbox, purchase, or compute

## 1. Decision

Cycle 13 began from a genuinely market-native many-body mechanism. EBS Market is a
quasi-centralized limit order book: orders share a global matching venue, but executable
liquidity is filtered by bilateral credit. The current CME protocol adds daily gross and Net Open
Position (NOP) limits, one- or two-pool credit profiles, participant-specific dealable books,
partial fills at the credit boundary, cross-venue rebalancing, and distributed netting. This is a
stronger physical object than another fitted volatility or impact analogy.

It still does not yield a qualifying topic in the formulations tested here. The three strongest
questions fail for different reasons:

1. aggregate graph connectivity, total remaining credit, and the global book are not a sufficient
   state for executable liquidity; the full **labelled** residual-capacity matrix and its alignment
   with quoted prices are needed;
2. one-pool versus two-pool credit is standard resource pooling: static aggregate feasibility is
   monotone, while online class-specific effects depend on arrival order and allocation policy;
3. gross versus NOP credit exhaustion is, in the simplest exact model, total path variation versus
   net displacement. The apparent aging separation follows from the triangle inequality rather
   than a new collective law.

The broad domain is also directly occupied by the primary QCLOB literature, dynamic credit-network
theory, resource-pooling/loss-system results, bilateral-credit agent models, OTC network models,
and netting theory. The official mechanism does not expose a public, population-wide credit
matrix, utilization history, pool profile, or rebalancing clock. A custom credit layer in EcoMD or
two ordinary LOB simulators would therefore reproduce a researcher-defined mechanism rather than
validate the field estimand.

## 2. Funnel accounting

| Stage | Limit | Used | Result |
|---|---:|---:|---|
| F0 raw question programs | 12 | 12 | Complete portfolio recorded |
| F1 quick screens | 6 | 6 | Three closed, three advanced |
| F2 collision/contract screens | 3 | 3 | All three closed |
| F3 full hostile audits | 2 | 0 | No program warranted a full manifest |
| Machine cards | 1 | 0 | No authorization |

Six programs were pruned before literature expansion, three failed quick screens, and three failed
six-work collision screens. No probability estimate terminalized a route. Because no program
reached F3, no full-T0 forecast was elicited and no fifteen-work manifest was opened.

## 3. F0 portfolio: twelve question programs

| ID | Native object and rival explanations | Discriminating result | Value under either answer | Lane / archetype | Disposition |
|---|---|---|---|---|---|
| P1 `qclob_bilateral_credit_depletion_fragmentation` | Global book plus time-varying bilateral residual capacities. **H1:** credit depletion creates a collective executable-liquidity fragmentation law beyond static QCLOB state. **H0:** the response is ordinary capacitated matching once the full labelled capacity matrix, order state, and policy state are included. | Match global quotes, aggregate remaining credit, degree sequence, and binary topology while swapping residual capacity between the best and second-best quote providers. | A surviving residual would identify genuinely market-specific network dynamics; a null defines the sufficient state and closes graph-summary claims. | market-native action or constraint / theory-mechanism | F2 closed |
| P2 `ebs_one_two_credit_pool_resource_coupling` | One global Spot--NDF credit pool versus separate Spot and NDF pools with the same total capacity. **H1:** shared credit universally stabilizes executable liquidity. **H0:** static pooling only expands aggregate feasibility, while online product-specific protection depends on demand order, correlation, and allocation policy. | Compare simultaneous optimal allocation with an online first-come sequence that exhausts shared capacity before the other product arrives. | A positive theorem could guide market credit design; a null separates aggregate throughput from class-specific crowd-out. | unresolved model disagreement / theory-mechanism | F2 closed |
| P3 `ebs_gross_nop_credit_path_geometry` | Gross and NOP limits on the same bilateral trade path. **H1:** gross-credit depletion produces a market-native aging class distinct from net exposure. **H0:** the separation is total variation versus endpoint displacement, with all additional behavior supplied by the order-flow kernel. | Compare monotone signed flow with an alternating flow having the same volume and endpoints under gross and NOP accounting. | A residual would isolate a new path-dependent mechanism; a null gives an exact accounting decomposition and prevents false aging claims. | cross-domain theorem with market-specific obstruction / theory-mechanism | F2 closed |
| P4 `credit_screened_price_disagreement` | Global best prices versus participant-specific best-dealable prices. **H1:** credit geometry creates a new price-disagreement phase. **H0:** this is the defining QCLOB phenomenon already measured in trade-relative coordinates. | Hold global quotes fixed and remove only one participant's credit to the best quote. | Could define a participant-level measurement; a null confirms a direct QCLOB reduction. | new truth or control capability / measurement method | F1 direct-prior close |
| P5 `credit_scaling_factor_liquidity_boundary` | Product-specific gross-utilization scaling factors. **H1:** scaling creates a cross-product phase boundary. **H0:** it is a weighted capacity coordinate whose effect is determined by the full demand and quote mix. | Match weighted utilization while changing which product and quote provider consumes it. | A residual could define an invariant product coupling; a null identifies a unit/weighting artefact. | market-native action or constraint / theory-mechanism | F1 state-completion close |
| P6 `global_credit_rebalancing_wave` | Locally allocated credit across EBS instances with later compression and rebalancing. **H1:** delayed redistribution creates a propagating liquidity wave. **H0:** this is distributed resource balancing whose response depends on a private controller and demand process. | Hold total global capacity fixed while changing the undisclosed rebalancing policy or regional demand phase. | A positive result could expose a market-control mode; a null prevents inferring dynamics from an undocumented controller. | cross-domain theorem with market-specific obstruction / theory-mechanism | F1 contract close |
| P7 `daily_credit_reset_liquidity_quench` | The 5 p.m. credit reset with working orders retained even when a new limit is insufficient. **H1:** reset creates protocol memory. **H0:** complete order, limit, and utilization state is Markov and the apparent memory is a projection. | Match the complete post-reset state across histories. | A difference would locate omitted native state; equality closes the history narrative. | market-native action or constraint / theory-mechanism | portfolio-pruned |
| P8 `liquidation_only_credit_boundary` | A mode allowing only NOP-reducing trades. **H1:** the action cone creates a new liquidation transition. **H0:** it is an existing reduce-only/reachability grammar. | Compare exact reachable safe sets under unrestricted and NOP-reducing action alphabets. | Could classify a native action obstruction; a null deduplicates against closed liquidation-grammar routes. | market-native action or constraint / theory-mechanism | portfolio-pruned: graph duplicate |
| P9 `credit_kill_switch_order_cascade` | Credit-parent kill instructions cancel all affected working orders. **H1:** identity-tree deletion has a novel cascade law. **H0:** it is a common-shock batch deletion whose outcome requires the hidden owner/order map. | Match the public L2 book while changing the owner partition targeted by the switch. | A difference proves public-state nonidentification; a null would bound the role of identity. | market-native action or constraint / empirical intervention | portfolio-pruned: graph duplicate |
| P10 `capital_preserving_order_unitization_kernel` | Split one economic order or agent into equivalent child units. **H1:** a universal collision kernel is invariant to the split. **H0:** this is the already-closed branching, lumpability, and matching-rule problem. | Query the route graph before any new literature search. | Deduplication saves a full audit and preserves prior counterexamples. | cross-domain theorem with market-specific obstruction / theory-mechanism | portfolio-pruned: exact graph duplicate |
| P11 `combinatorial_allocation_landscape_degeneracy` | Near-optimal allocations in a combinatorial market. **H1:** a market-specific glassy landscape controls clearing sensitivity. **H0:** statistical mechanics of combinatorial auctions already occupies the object. | Check the exact title/object neighborhood before constructing a simulator. | A null closes a seductive analogy at negligible cost. | cross-domain theorem with market-specific obstruction / theory-mechanism | portfolio-pruned: direct primary work |
| P12 `maker_rebate_negative_friction` | Maker rebates and volume tiers. **H1:** negative effective friction creates a new nonequilibrium phase. **H0:** no-arbitrage bounds, fee-tier optimization, and direct maker--taker evidence explain it. | Hold the action and fill process fixed and test whether any effect remains after net fee cash flows are accounted for. | A residual could isolate strategic feedback; a null returns the problem to execution economics. | unresolved model disagreement / empirical intervention | portfolio-pruned: saturated parent |

## 4. F1 quick screens

### P4: credit-screened price disagreement -- close

The object is already explicit in the direct literature. Gould, Porter, and Howison define a QCLOB
as a book in which institutions access only counterparties with sufficient bilateral credit. They
measure order flow and state in a high-quality FX QCLOB data set, document negative global spreads,
and introduce trade-relative coordinates and a semiparametric model. Earlier individual-trader EBS
work already distinguishes the common EBS Best from an idiosyncratic Best Dealable price. A new
simulator plot of participant-specific prices would be a reproduction, not a new law.

### P5: scaling-factor liquidity boundary -- close

The official gross-utilization rule multiplies traded base-currency amount by a participant- and
product-dependent scaling factor and a conversion rate. A proposed scalar utilization coordinate
therefore omits which quote, counterparty, and product consumed capacity. Two states with the same
weighted total can expose different best-dealable prices when the residual capacity is attached to
different quote providers. Adding the labelled product--counterparty state removes the proposed
compression. There is no invariant phase variable at F1.

### P6: global credit rebalancing wave -- close

CME documents local instance decisions, a single global compression location, and redistribution
of excess credit, but not a public event-level controller, cadence, regional residual-capacity
state, or randomized policy assignment. With those objects specified, the problem is distributed
resource pooling and load balancing; without them, a wave speed or propagation kernel is not
identified. The route fails before simulation because a researcher-chosen controller would define
the result.

## 5. F2 collision and truth-contract screens

### 5.1 P1: bilateral-credit depletion fragmentation

The five-part contract was:

- `X`: the labelled global order book, bilateral gross/NOP residual-capacity matrices, credit-group
  membership, participant inventory/policy state, and event history needed by those policies;
- `do(A)`: consume or restore a frozen bilateral capacity while preserving all submitted orders
  and exogenous events;
- `Y`: participant-specific executable spread/depth, next-order fill, and time to loss of a
  predeclared executable-liquidity component;
- `H1:H0`: a reduced network-fragmentation law versus full capacitated matching plus adaptive
  policy state; and
- `T`: an exact QCLOB engine and a field record of the same labelled capacity intervention and
  participant-specific book.

Two minimal twins are decisive.

**Label-alignment twin.** A taker sees two sellers at prices `p` and `p + delta`. Give both
bilateral relationships positive residual credit, but make only one residual amount large enough
for the minimum trade. Swapping those two amounts preserves total credit, degree sequence, binary
credit topology, global book, spread, and quote sizes, but changes the taker's best-dealable price
by `delta`. Aggregate network statistics are not a state variable.

**Complete-state twin.** If two histories end in the same labelled order book, residual-capacity
matrices, credit groups, inventories, and agent policy states, the next event has the same law under
a Markov simulator. Any remaining history effect resides in omitted policy state. Thus a claimed
hysteresis either fails or reopens the already-closed observation-quotient problem.

Once the complete state is retained, the exogenous-flow version is a capacitated matching or
credit/loss network. Dandekar et al. already analyze steady-state transaction failure under dynamic
bilateral capacities; Ramseyer, Goel, and Mazieres add aggregate constraints and show exact network
reductions; Bewaji directly builds an agent-based stochastic game of bilateral-credit decisions.
OTC-intermediary models already connect network constraints to prices and risk sharing. The market
label does not create an irreducible theorem.

The field truth contract also fails. CME states that each subscriber receives its own
credit-screened book plus the potentially nondealable global best. It does not publish the
population-wide bilateral limit matrix, remaining balances, credit-group map, profile changes,
intraday adjustments, or rebalancing events. The direct QCLOB data are high quality but not a
public prospective assignment of those states.

**Hard closure:** `aggregate_credit_topology_not_state_sufficient`,
`complete_state_history_effect_reduces_to_policy_state`, `qclob_direct_primary_collision`,
`capacitated_credit_network_parent`, `population_credit_matrix_not_public`, and
`same_estimand_field_intervention_missing`.

Diagnostic post-screen hostile-T0 was 3--8% with a 5% point estimate. It was elicited after the
hard failures and is not a prospective forecast.

### 5.2 P2: one-pool versus two-pool credit

The five-part contract was:

- `X`: Spot and NDF demands, quotes, residual capacities, allocation policy, and one- or two-pool
  profile;
- `do(A)`: replace two capacities `C_S,C_N` by one capacity `C=C_S+C_N` without changing demand;
- `Y`: aggregate accepted notional, product-specific blocking, and executable depth;
- `H1:H0`: universal stabilization from shared credit versus ordinary pooling with class-specific
  crowd-out; and
- `T`: exact allocation mathematics plus an assigned profile change with complete capacity state.

For simultaneous demand and an optimizer concerned only with total accepted volume, every
allocation feasible under split pools is feasible under the shared pool. The aggregate result is
simple feasible-set inclusion. It is not a new phase law.

For an online policy, no universal product-specific sign remains. Let `C_S=C_N=1`, so the shared
pool has capacity two. Under arrivals `S_1,S_2,N_1`, a first-come shared pool accepts both Spot
requests and blocks the NDF request, while split pools accept `S_1` and `N_1`. Both accept two
requests, but the NDF response has the opposite interpretation. Priority, reservation, demand
correlation, and outcome weights determine the result. Partial-resource-pooling theory already
shows that full pooling need not benefit every provider even when a Pareto-improving partial share
exists, and multilateral-versus-bilateral netting theory makes the same dependence on cross-class
heterogeneity and correlation explicit.

EBS profile choice is not a field assignment. A grantor uses one profile for a trading week, and
the Global Command Center enacts changes over the weekend. The public protocol provides no
participant-profile panel, capacity split, demand state, or independent randomized switch.

**Hard closure:** `static_pooling_feasible_set_inclusion`, `online_class_crowding_policy_dependent`,
`partial_resource_pooling_direct_parent`, `cross_class_netting_correlation_direct_parent`,
`credit_profile_selection_not_assigned`, and `profile_capacity_state_not_public`.

Diagnostic post-screen hostile-T0 was 2--6% with a 4% point estimate. It is not a prospective
forecast.

### 5.3 P3: gross versus NOP credit path geometry

The five-part contract was:

- `X`: a bilateral signed trade sequence, product weights, currency exposures, gross and NOP
  limits, and the book/policy state;
- `do(A)`: apply gross, NOP, or both limit methodologies to the same frozen sequence;
- `Y`: time to credit exhaustion, blocked notional, and executable depth;
- `H1:H0`: a distinct gross-credit aging universality class versus accounting path geometry; and
- `T`: an exact utilization calculation followed by a same-sequence field or native-engine test
  only if an irreducible residual survived.

In the one-currency, unit-weight toy, signed trades are `x_1,...,x_T`. Gross utilization is

\[
  U_G(T)=\sum_{t=1}^{T}|x_t|,
\]

whereas the net exposure underlying the simplified NOP limit is

\[
  U_N(T)=\left|\sum_{t=1}^{T}x_t\right|.
\]

The inequality `U_N <= U_G` is the triangle inequality. For `x=(+1,-1,+1,-1,...)`, gross
utilization grows linearly while net exposure returns to zero. For a monotone path, the two are
equal. Product scaling and multiple currencies replace these expressions by weighted total
variation and a vector exposure norm; they do not create a new mechanism.

Any response beyond this identity comes from the signed-flow kernel, quote placement, agent
adaptation, reset/netting rule, and labelled counterparty capacities. Credit-network and OTC
netting theory already study how direction, path, network, cross-asset correlation, and
multilateral compression change liquidity and exposure. The official population state needed to
test an EBS-specific residual is not public.

**Hard closure:** `gross_credit_is_weighted_path_variation`, `nop_credit_is_net_exposure`,
`triangle_inequality_exact_parent`, `flow_kernel_required_for_dynamic_response`,
`netting_credit_network_prior`, and `same_sequence_field_state_absent`.

Diagnostic post-screen hostile-T0 was 1--4% with a 2% point estimate. It is not a prospective
forecast.

## 6. Six-work collision manifests

The three F2 programs share a tightly connected primary neighborhood. Each was checked against at
least six primary or official sources; this is not an F3 fifteen-work manifest.

### P1: QCLOB state and dynamic credit networks

1. CME, *EBS Credit Overview on CME Globex*
   ([official protocol](https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457085891)).
2. Gould, Porter, and Howison, *Quasi-Centralized Limit Order Books*
   ([primary manuscript](https://arxiv.org/abs/1502.00680)).
3. Moore, Payne, and others, *Individual trader records on EBS Spot*
   ([primary manuscript](https://www.snb.ch/dam/jcr%3A1b9a0d97-e06f-48b9-a250-1a90fae20752/sem_2009_10_08_moore.n.pdf)).
4. Dandekar et al., *Liquidity in Credit Networks: A Little Trust Goes a Long Way*
   ([primary manuscript](https://arxiv.org/abs/1007.0515)).
5. Ramseyer, Goel, and Mazieres, *Liquidity in Credit Networks with Constrained Agents*
   ([DOI](https://doi.org/10.1145/3366423.3380276)).
6. Bewaji, *A computational model of bilateral credit limits in payment systems and other
   financial market infrastructures* ([DOI](https://doi.org/10.1016/j.latcb.2023.100115)).
7. Eisfeldt et al., *OTC Intermediaries*
   ([official primary record](https://www.financialresearch.gov/working-papers/2018/08/29/otc-intermediaries/)).

### P2: resource pooling and cross-class netting

1. CME's one-pool/two-pool and global-rebalancing rules in the official EBS credit protocol.
2. CME, *EBS Direct*, documenting a shared global credit model
   ([official product page](https://www.cmegroup.com/markets/ebs/ebs-direct.html)).
3. Nandigam et al., *Sharing within limits: Partial resource pooling in loss systems*
   ([primary manuscript](https://arxiv.org/abs/1808.06175)).
4. Cont and Kokholm, *Central Clearing of OTC Derivatives: Bilateral vs Multilateral Netting*
   ([DOI](https://doi.org/10.1515/strm-2013-1161)).
5. Ramseyer, Goel, and Mazieres, constrained credit-network theory above.
6. Dandekar et al., dynamic credit-network liquidity above.
7. Vuillemey and Breton, *Endogenous Derivative Networks*
   ([official primary record](https://publications.banque-france.fr/en/economic-and-financial-publications-working-papers/endogenous-derivative-networks)).

### P3: gross/net path dependence and market liquidity

1. CME's official gross, NOP, scaling, reset, compression, and distributed-netting rules.
2. Dandekar et al., dynamic bilateral-capacity and route-independence analysis above.
3. Ramseyer, Goel, and Mazieres, constrained credit-network reductions above.
4. Cont and Kokholm, cross-asset bilateral versus multilateral netting above.
5. Bewaji, bilateral-credit stochastic-game model above.
6. Eisfeldt et al., incomplete OTC networks, prices, and risk sharing above.
7. Huang et al., *Constrained liquidity provision in currency markets*
   ([official primary record](https://www.bis.org/publ/work1073.htm)).

## 7. Observation and simulator contracts

The official protocol is unusually detailed about rules but does not provide the field truth needed
for these claims. A market participant sees only counterparties for which sufficient credit is
available, along with a possibly nondealable global best. Limit values, current balances, credit
groups, pool profiles, intraday adjustments, product scaling factors, and the global rebalancing
state are private risk-management objects. Public price-level market data cannot reconstruct the
population's matrix of counterfactual dealable books.

ABIDES, PAMS, and Bourse do not natively implement this EBS credit state. Adding the same
researcher-authored credit module to two engines would not produce independent mechanism truth;
adding different modules would violate the same-estimand contract. The direct QCLOB study uses a
valuable proprietary historical data set, but its published result and semiparametric model do not
supply a prospective, manipulable credit-matrix holdout.

Therefore simulation can support a future theorem only after the theorem is proved to be false in
generic capacitated matching, credit networks, and loss systems. It cannot repair the current
novelty or field-state failures.

## 8. What this cycle says about the 15% floor

Cycle 13 adds no calibration observation. No route reached F3, so no prospective full-T0 forecast
was eligible to be frozen. The three diagnostic intervals were written only after their hard gates
failed and cannot be scored.

The 15% lower-endpoint rule remains defensible only as a conservative **activation-cost brake**,
not as a scientific truth threshold. There is still one resolved comparable full-T0 forecast,
whereas the protocol requires twenty before review. Lowering the floor would not rescue any Cycle
13 route: exact state insufficiency, parent reductions, and absent field contracts remain true at
any probability label. Conversely, the floor did not prevent this inexpensive D-3/D-2 audit.

## 9. Reusable scientific and process residue

Cycle 13 adds four reusable assets:

1. **Labelled-capacity sufficiency twin.** Preserve aggregate capacity, topology, quotes, and
   degrees while moving capacity between differently priced providers. A response difference
   proves that a graph summary is not the native state.
2. **Static--online--endogenous pooling split.** Separate static feasible-set inclusion, online
   priority/crowding, and strategic response before claiming a universal sign from resource
   pooling.
3. **Path-length--displacement decomposition.** Gross utilization is weighted path variation;
   NOP utilization is net exposure. Any claimed new aging law must survive after this identity is
   removed.
4. **Private-control-state contract.** A detailed public rulebook is not an observation bridge when
   participant-specific capacities, controller events, and counterfactual dealable views remain
   private.

The next cycle should search for a native mechanism with either a public complete state and
assigned intervention, or a theorem whose conclusion is false for generic capacitated matching,
loss networks, credit networks, and accounting path geometry. Cycle 13 creates no card and
authorizes no outcome access, simulation, data action, sandbox, outreach, implementation, purchase,
EcoMD edit, or compute.
