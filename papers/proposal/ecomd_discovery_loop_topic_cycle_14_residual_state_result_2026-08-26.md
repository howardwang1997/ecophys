# EcoMD Discovery Loop topic cycle 14: residual state and loss transfer

**Date:** 2026-08-26
**Literature cutoff:** 2026-08-26
**Mode:** outcome-blind, paper/source-only topic search
**Decision:** zero F3 audits and zero machine cards; two F2 formulations closed and four F1
formulations closed or deduplicated
**Authorization:** no simulator run, outcome access, dataset action, implementation, outreach,
sandbox, purchase, EcoMD edit, or compute

## 1. Decision

Cycle 14 deliberately did not search for another named physical analogy. It resolved the strongest
paper-only question deferred by Cycle 10 and then tested exact protocol state that appeared after
the earlier route-graph audit: order age under paired liquidity pulses, ranked auto-deleveraging,
GMX pending price impact, Vega parked pegged orders, and Eurex synthetic-path allocation.

No formulation survived. The important results are structural rather than probabilistic:

1. the paired-pulse difference proposed as a liquidity echo is exactly a second-order Volterra
   response for any smooth weakly nonlinear causal system; observable order age is transported at
   one common velocity and does not by itself supply the frequency distribution needed for phase
   mixing and rephasing;
2. auto-deleveraging is now directly occupied by impossibility, sequential online-control, and
   risk-minimization work, including production-queue counterfactuals;
3. GMX's pending-impact state creates a real closeability gap, but the protocol itself documents
   it and, conditional on complete state, the gap is an execution-feasibility inequality rather
   than a new collective law; and
4. Vega parked-order release and Eurex direct-versus-synthetic path allocation are exact replay or
   previously closed conditional-order and implied-liquidity problems.

The 15% active-status brake played no role in closing a program. No program reached F3, so no
prospective full-T0 forecast was elicited.

## 2. Funnel accounting

| Stage | Limit | Used | Result |
|---|---:|---:|---|
| F0 raw question programs | 12 | 12 | Complete portfolio recorded |
| F1 quick screens | 6 | 6 | Three closed, one deduplicated, two advanced |
| F2 collision/contract screens | 3 | 2 | Both closed |
| F3 full hostile audits | 2 | 0 | No program warranted a full manifest |
| Machine cards | 1 | 0 | No authorization |

Six programs were portfolio-pruned, three failed quick screens, one was deduplicated during the
quick screen, and two failed six-work collision screens. No program was terminalized by a
probability label.

## 3. F0 portfolio: twelve question programs

| ID | Native object and rival explanations | Discriminating result | Value under either answer | Lane / archetype | Disposition |
|---|---|---|---|---|---|
| P1 `observable_order_age_liquidity_echo` | A price-time-priority book with order age and two weak exogenous liquidity-removal pulses. **H1:** age heterogeneity phase-mixes and later rephases into a delayed bilinear echo. **H0:** the paired-pulse residual is an ordinary second-order Volterra kernel or renewal delay without a rephasing variable. | Require both single-pulse responses to decay, an amplitude-bilinear delayed cross-term, a timing law fixed before search, and a legal age-scramble sham that preserves every non-phase state. | A positive result would be a rare market-native nonlinear-response mechanism; a null precisely closes the strongest deferred Cycle 10 question. | cross-domain theorem with market-specific obstruction / theory-mechanism | F2 closed |
| P2 `ranked_adl_loss_transfer_front` | Profitable leveraged positions are forcibly reduced in rank order after bad debt exceeds the insurance fund. **H1:** rank depletion creates a new many-body propagation front. **H0:** it is the directly studied ADL allocation/control problem. | Map the proposed front, objective, and intervention to recent ADL impossibility, online-learning, and risk-minimization formulations. | A residual could inform a safer loss-transfer rule; a collision prevents relabeling allocation dynamics as physics. | market-native action or constraint / theory-mechanism | F1 direct-prior close |
| P3 `insurance_fund_depletion_recovery_loop` | Liquidation fees replenish a buffer that later absorbs default losses. **H1:** the buffer produces a new endogenous recovery transition. **H0:** it is a risk reserve/ruin and default-waterfall process whose sign depends on loss and fee arrival kernels. | Match the current fund balance while varying future loss and fee-arrival laws. | A positive result would inform capital design; a null identifies the missing kernel and prevents a balance-only phase claim. | unresolved model disagreement / theory-mechanism | F1 parent close |
| P4 `cross_market_adl_contagion` | Cross-margin portfolios and shared solvency resources couple forced reductions across assets. **H1:** an ADL shock propagates through a novel market network. **H0:** the full exposure matrix and loss-allocation rule give existing cross-margin/default-network contagion. | Hold aggregate exposure and fund size fixed while permuting labelled cross-asset portfolios. | A surviving invariant could support systemic-risk design; a null identifies labelled exposure as the necessary state. | market-native action or constraint / theory-mechanism | F1 direct-prior close |
| P5 `gmx_pending_impact_closeability_gap` | Each GMX position stores pending price impact and realizes its proportional share on decrease. **H1:** impact debt creates a new trapped-liquidity or jamming state. **H0:** closeability is a protocol-specific feasibility inequality, while dynamics require future oracle, order-flow, acceptable-price, and policy state. | Match visible collateral, size and current oracle state while varying pending impact or impact-pool capacity, then complete the state and test whether anything remains beyond deterministic feasibility. | A residual could expose a protocol-native memory mechanism; a null yields a reusable liveness invariant and prevents a false collective-law claim. | new truth or control capability / theory-mechanism | F2 closed |
| P6 `vega_parked_peg_release_avalanche` | Pegged orders are parked during auctions and reinserted in entry order after repricing. **H1:** release creates a self-amplifying liquidity avalanche. **H0:** it is deterministic event-condition-action processing plus ordinary subsequent order flow. | Replay identical complete pegged-order and auction state with and without later adaptive submissions. | A residual could identify exchange-hosted state feedback; a null deduplicates an exact hosted-conditional-order route. | market-native action or constraint / simulator-method | F1 graph/replay close |
| P7 `eurex_synthetic_path_priority_response` | Direct and synthetic paths at the same price changed from direct-first to pro-rata sharing in STIR futures. **H1:** the rule creates an autonomous cross-book response. **H0:** immediate effects are mechanical allocation and longer effects need order-flow response. | Hold all path quantities and later submissions fixed while switching only the path allocation rule. | A residual could inform matching design; a null distinguishes a fill identity from a dynamic law. | new truth or control capability / empirical-intervention | portfolio-pruned: graph duplicate |
| P8 `simultaneous_synthetic_capacity` | Several displayed implied quotations share primitive source orders. **H1:** a new shadow-liquidity capacity controls fragility. **H0:** simultaneous execution is path packing or multicommodity flow and displayed sums are listing-dependent. | Add an economically redundant spread listing without changing the primitive feasible set. | A null preserves the correct demand-conditioned capacity object. | cross-domain theorem with market-specific obstruction / theory-mechanism | portfolio-pruned: exact graph duplicate |
| P9 `adl_score_chattering` | PnL-times-leverage ranks change after each forced reduction. **H1:** repeated reranking creates a new chattering law. **H0:** it is a state-dependent sequential allocation policy already covered by ADL control work. | Compare continuous water-filling with discrete reranking under the same loss objective. | Could identify implementation error; a null leaves an optimization discretization. | market-native action or constraint / theory-mechanism | portfolio-pruned: direct primary work |
| P10 `bankruptcy_price_reflecting_boundary` | Liquidation and bankruptcy prices create distinct account boundaries. **H1:** their gap generates a universal reflected process. **H0:** first-passage and post-hit behavior depend on the protocol's liquidation kernel and oracle. | Match both boundaries while changing liquidation delay and executable liquidity. | A null prevents a boundary-only universality claim. | unresolved model disagreement / theory-mechanism | portfolio-pruned: parameter-completion failure |
| P11 `socialized_haircut_vs_tearup_relaxation` | VM gains haircutting, cash calls, auctions and partial tear-up allocate the same residual default loss differently. **H1:** one mechanism has a universal relaxation advantage. **H0:** participation, incentives, portfolio labels, collateral liquidity and bidder capacity determine the ranking. | Hold loss size fixed while reversing participant portfolio direction or bidder capacity. | A null still identifies the state required for waterfall comparison. | market-native action or constraint / empirical-intervention | portfolio-pruned: default-waterfall prior |
| P12 `default_waterfall_mechanism_phase_map` | Insurance, auctions, forced sales and ADL form a staged loss waterfall. **H1:** mechanism order produces a new phase map. **H0:** recent equilibrium and systemic-loss work already studies the same ranking. | Exact title/object search before constructing a simulator. | Immediate collision saves implementation and outcome cost. | unresolved model disagreement / theory-mechanism | portfolio-pruned: exact current prior |

## 4. F1 quick screens

### P2: ranked ADL front -- direct-prior close

The central object is no longer open. Chitra formalizes ADL allocation, proves a
solvency--revenue--fairness trilemma, and evaluates the production Hyperliquid queue.
Chitra et al. formulate repeated ADL as online learning over profitable-account haircuts and give
regret bounds and production counterfactuals. Campbell et al. formulate single- and multi-asset ADL
as risk minimization and derive leverage water-filling and cross-margin algorithms. A rank front,
overshoot statistic, or alternative queue simulated in EcoMD would be a specialization of those
objects, not a new law.

### P3: insurance-fund recovery -- parent close

The current balance is not a sufficient control variable. Two systems with the same fund balance
but different future liquidation-loss, fee-income, volatility, or participant-exit kernels have
opposite ruin and recovery probabilities. Adding those kernels gives a reserve-risk or dynamic
default-waterfall model. Central-counterparty work already studies how waterfall resources,
participant behavior, network exposures and fire sales affect systemic loss. No market-specific
invariance remained.

### P4: cross-market ADL contagion -- direct-parent close

Aggregate leverage, open interest and fund size do not identify cross-asset loss propagation. A
permutation of the same marginal positions across accounts preserves those summaries but changes
which cross-margin accounts fail together. Risk-Based ADL already treats multi-asset cross-margin
allocation through account portfolios and asset shadow prices; CCP network work already treats
shared-member contagion and waterfall loss allocation. The complete labelled exposure matrix is
the state, not an omitted physical order parameter.

### P6: Vega parked pegged orders -- graph/replay close

Vega's public specification is unusually complete: pegged orders are removed and parked during an
auction, repriced and reinserted in original entry order at the back of their new price levels, and
some amendments reset that ordering. Given the full parked list, offsets, sides, sizes, margins,
reference prices and persistent book, release is deterministic replay. A response beyond replay is
later adaptive order flow. This is the exact hosted conditional-order/confluence route already
closed in the graph, so no second literature expansion was warranted.

## 5. F2 collision and truth-contract screens

### 5.1 P1: observable-order-age liquidity echo

The five-part contract was:

- `X`: a full order-ID book with price, side, quantity, queue position, entry time, order age,
  observable time-in-force state, and all agent/controller variables used by cancellation or refill;
- `do(A)`: two predeclared weak, zero-net liquidity pulses at times zero and `tau`, plus each pulse
  alone and a legal phase-scramble sham;
- `Y`: a frozen price-level depth or executable-impact functional in physical time;
- `H1:H0`: age-driven dephasing/rephasing versus generic nonlinear response or renewal delay; and
- `T`: a theorem on a legal price-time-priority process, followed only if it survived by two native
  engines and order-lifecycle data exposing the same state.

For a smooth causal system near a stationary law, write the weak-input expansion

\[
Y[u](t)=Y_0+\int K_1(t-s)u(s)\,ds+
\frac12\iint K_2(t-s,t-r)u(s)u(r)\,ds\,dr+O(\lVert u\rVert^3).
\]

With `u=epsilon_1 delta_0 + epsilon_2 delta_tau`, the paired-pulse subtraction

\[
E(t)=Y[u_1+u_2](t)-Y[u_1](t)-Y[u_2](t)+Y_0
\]

is, to second order, `epsilon_1 epsilon_2` times the off-diagonal second-order Volterra
kernel, up to the kernel's symmetry convention. It may peak after both linear responses decay in
an entirely ordinary nonlinear system. Paired-pulse system identification uses exactly this fact.
Amplitude bilinearity and a delayed maximum therefore do not identify phase rephasing.

The native age-density equation has the characteristic form

\[
\partial_t n(a,t)+\partial_a n(a,t)=-\mu(a,X_t)n(a,t),\qquad n(0,t)=\lambda(X_t).
\]

All cohorts advance with `da/dt=1`. Age changes survival weights and renewal delays, but age alone
does not provide the heterogeneous velocities or frequencies whose phases mix and later rephase in
a Vlasov plasma echo. One can add type-specific periods, latent refresh clocks, or a nonlinear phase
map, but that inserts the parent mechanism rather than deriving it from price-time priority.

The proposed sham also fails a dichotomy:

1. shuffling ages across orders changes FIFO priority, age-dependent cancellation hazard, expiry,
   or agent state, so it is a real state intervention rather than a phase-only sham; or
2. the shuffle preserves the complete conditional future law, in which case it cannot change the
   response and cannot diagnose an echo.

**Hard closure:** `paired_pulse_residual_is_second_order_volterra_kernel`,
`order_age_has_common_transport_velocity`, `phase_scramble_not_state_preserving`,
`observable_echo_discriminator_missing`, `age_cancellation_and_resiliency_prior`, and
`native_two_engine_phase_state_missing`.

Diagnostic post-screen hostile-T0 was 2--7% with a 4% point estimate. It was elicited after the
hard failures and is not a prospective forecast.

### 5.2 P5: GMX pending-impact closeability gap

The five-part contract was:

- `X`: position size, collateral, pending-impact amount, long/short open interest, market and
  virtual inventories, impact pools and lendable amount, caps, fees, acceptable price and oracle;
- `do(A)`: alter or settle a frozen pending-impact balance while preserving the rest of the full
  protocol state;
- `Y`: whether a partial or full decrease executes, returned collateral, claimable rebate, or
  liquidation occurs;
- `H1:H0`: an autonomous impact-debt jamming mechanism versus exact execution feasibility plus
  future order-flow and oracle state; and
- `T`: bit-exact versioned contract replay and a second independently maintained implementation of
  the same stored-impact semantics.

GMX v2.2 stores price impact on position increase and charges a proportional share together with
current close impact on decrease. The official changelog states the exact corner case: full impact
funds may be required for a close even when part later becomes claimable, while liquidation ignores
pending impact and applies zero liquidation impact. A position can therefore be economically
liquidatable yet not trigger liquidation and can fail a voluntary close.

This is a useful protocol liveness invariant, but not an unidentified physical phenomenon. Given
the complete state, closeability is the Boolean result of the published execution-price,
acceptable-price, collateral, cap and pool-availability checks. Holding only position size and
collateral fixed while varying pending impact proves that the new field matters; restoring the
field closes the apparent memory. Holding pending impact fixed while varying acceptable price,
oracle, current imbalance or lendable pool flips feasibility again, so pending impact alone is not
an order parameter.

Nor does the static gap imply a cascade. Identical current states followed by favorable balancing
flow versus adverse same-side flow have opposite close and liquidation outcomes. A dynamic claim
must specify the future order/oracle/policy kernel, at which point it belongs to established
perpetual-demand-pool, liquidation and reachability models. No independent protocol with the same
stored-on-entry, proportionally-realized impact debt was qualified. The v2.2 bundle also changes
liquidation factors, positive-impact caps, pool lending, withdrawals, callbacks and gasless state,
so a version event is not a one-variable field intervention.

**Hard closure:** `official_protocol_documents_closeability_gap`,
`complete_state_execution_feasibility_reduction`, `pending_impact_not_sufficient_state`,
`future_flow_required_for_cascade`, `bundled_v22_mechanism_change`, and
`same_estimand_second_protocol_missing`.

Diagnostic post-screen hostile-T0 was 3--9% with a 5% point estimate. It is not a prospective
forecast.

## 6. Six-work collision manifests

### P1: paired pulses, age state and market resiliency

1. Large, *Measuring the resiliency of an electronic limit order book*,
   [DOI](https://doi.org/10.1016/j.finmar.2006.09.001).
2. Lo and Hall, *Resiliency of the limit order book*,
   [DOI](https://doi.org/10.1016/j.jedc.2015.09.012).
3. Dahlström, *The determinants of limit order cancellations*,
   [DOI](https://doi.org/10.1111/fire.12363).
4. Diekmann and Scarabel, *Age-Structured Population Dynamics*,
   [primary manuscript](https://arxiv.org/abs/2506.03405).
5. Arunajadai, *Quadratic System Identification: a statistical framework for the paired-pulse
   paradigm*, [DOI](https://doi.org/10.1016/j.mbs.2009.11.010).
6. Grenier, Nguyen, and Rodnianski, *Plasma Echoes Near Stable Penrose Data*,
   [DOI](https://doi.org/10.1137/21M1392553).
7. Meng et al., *A mathematical formulation of order cancellation for the agent-based modelling
   of financial markets*, [publisher record](https://www.sciencedirect.com/science/article/pii/S0378437119314372).

The market works establish impulse response, recovery and age/priority-dependent cancellation;
the parent works establish renewal transport, generic paired-pulse quadratic response and genuine
phase-mixing echoes. Their intersection leaves no identified echo certificate from observable age.

### P5: stored impact, closeability and perpetual-pool mechanics

1. GMX, *v2.2 changelog*,
   [official version record](https://github.com/gmx-io/gmx-synthetics/blob/main/changelogs/v2.2.md).
2. GMX, `PositionUtils.sol`,
   [official implementation](https://github.com/gmx-io/gmx-synthetics/blob/main/contracts/position/PositionUtils.sol).
3. GMX, *Fees and net price impact*,
   [official documentation](https://docs.gmx.io/docs/trading/fees/).
4. Chitra et al., *Perpetual Demand Lending Pools*,
   [primary manuscript](https://arxiv.org/abs/2502.06028).
5. Bartoletti et al., *Solvent: Liquidity Verification of Smart Contracts*,
   [DOI](https://doi.org/10.1007/978-3-031-76554-4_14).
6. Campbell et al., *Risk-Based Auto-Deleveraging*,
   [primary manuscript](https://arxiv.org/abs/2603.15963).
7. Chitra, *Autodeleveraging: Impossibilities and Optimization*,
   [primary manuscript](https://arxiv.org/abs/2512.01112).

The exact implementation is valuable as a formal-verification target, but the protocol authors
already state the gap, generic liquidity reachability covers liveness, and perpetual-pool and ADL
work cover the surrounding economic mechanisms.

## 7. Reusable gates

Cycle 14 adds four cheap gates to future searches:

1. **Paired-pulse gate.** Subtracting two single-pulse responses estimates a nonlinear cross-kernel;
   do not call a delayed cross-term an echo without an independently observed phase coordinate,
   a frozen timing law and a state-preserving phase reversal or scramble.
2. **Age-transport gate.** Order age has common unit velocity. A true phase-mixing claim must derive
   heterogeneous native frequencies or velocities rather than insert private oscillator types.
3. **Documented-corner-case gate.** An exact protocol limitation documented by its authors is a
   verification target, not automatically a new scientific phenomenon.
4. **Loss-transfer gate.** ADL, haircut and waterfall questions must first map against current ADL
   impossibility/optimization, online-control, risk-minimization and CCP systemic-loss work.

## 8. What this cycle says about the 15% floor

Cycle 14 adds no prospective forecast resolution. The 15% lower endpoint remains a provisional,
uncalibrated brake on costly active status, not a topic-quality score. It did not block the cheap
paper/source work in this cycle and did not close any formulation. Exact parent reductions,
non-discriminating observations, graph duplicates and missing same-estimand contracts did.

The next cycle should therefore not lower the threshold to manufacture a survivor. It should
prefer mechanisms with all three of: public complete native state, an intervention that is not
selected by the same state, and a claim whose conclusion is false for the nearest queue,
reachability, nonlinear-response or network parent. Until such a program reaches F3, no active
topic, outcome access, simulation, data purchase, outreach, EcoMD modification or compute is
authorized.
