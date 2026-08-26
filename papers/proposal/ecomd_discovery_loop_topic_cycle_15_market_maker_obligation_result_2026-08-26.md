# EcoMD Discovery Loop topic cycle 15: market-maker obligations and liquidity rewards

**Date:** 2026-08-26
**Literature cutoff:** 2026-08-26
**Mode:** outcome-blind, paper/source-only topic search
**Decision:** zero F3 audits and zero machine cards; three F2 formulations and three F1
formulations closed
**Authorization:** no simulator run, outcome access, dataset action, implementation, outreach,
sandbox, purchase, EcoMD edit, or compute

## 1. Decision

Cycle 15 asked whether publicly specified market-making obligations or reward controllers create a
market-native many-body mechanism that is both scientifically new and testable without private
agent state. The search covered role-level quote-compliance aggregation, daily versus monthly
sponsored incentives, volume-triggered obligation release, quote-presence constraints, and
relative liquidity-reward formulas.

No formulation survived. The decisive reductions were:

1. aggregating two 90-percent quote obligations into one weighted compliance bucket strictly
   enlarges a feasible set and permits cross-subsidization, but it does not force any particular
   quote migration; the response is an ordinary resource-pooling/control problem;
2. JPX's daily sponsor option jointly exposes selectable weights, target periods, payment methods,
   rankings, obligations and securities, so it is neither a scalar clock intervention nor an
   exogenous assignment; its response is a contract-and-cost comparative static;
3. normalized liquidity rewards allocate a fixed pool as a relative-share or contest payoff;
   common scaling leaves shares unchanged, while relabelling quote ownership changes rewards
   without changing the anonymous book; and
4. reaching a sufficient-volume threshold merely releases an obligation. It does not compel a
   market maker to withdraw, and the hitting time is endogenous to the same flow being studied.

Direct work already covers designated-market-maker resiliency, synchronized withdrawal, natural
experiments, exchange--market-maker contracting, multi-maker competition, and the dYdX reward
formula. No program reached F3, so no prospective full-T0 forecast was elicited. The 15-percent
active-status brake did not close any program.

## 2. Funnel accounting

| Stage | Limit | Used | Result |
|---|---:|---:|---|
| F0 raw question programs | 12 | 12 | Complete portfolio recorded |
| F1 quick screens | 6 | 6 | Three closed and three advanced |
| F2 collision/contract screens | 3 | 3 | All three closed |
| F3 full hostile audits | 2 | 0 | No program warranted a full manifest |
| Machine cards | 1 | 0 | No authorization |

Six programs were portfolio-pruned, three failed quick screens, and three failed six-work
collision or truth-contract screens. No program was terminalized by a probability label.

## 3. F0 portfolio: twelve question programs

| ID | Native object and rival explanations | Discriminating result | Value under either answer | Lane / archetype | Disposition |
|---|---|---|---|---|---|
| P1 `mrx_cross_role_quote_obligation_pooling` | MRX proposes to count PMM and Preferred-MM quoting in one 90-percent bucket. **H1:** compliance pooling causes a collective migration of liquidity from hard to easy option series. **H0:** it only enlarges the member's feasible set; realized migration depends on its private cost and control policy. | Prove the feasible-set relation, then require member-role quote identity and a rule change isolated from the firm's policy. | A residual could inform obligation design; the null yields a reusable resource-pooling gate. | new truth or control capability / theory-mechanism | F2 closed |
| P2 `phlx_cross_role_quote_obligation_pooling` | Phlx filed the same aggregation change. **H1:** it independently reproduces P1. **H0:** it is the same Nasdaq rule family and implementation logic, not an independent mechanism. | Compare rule text, ownership, implementation date and data semantics before calling it replication. | Prevents corporate duplicates from masquerading as cross-system validation. | new truth or control capability / empirical-intervention | portfolio-pruned: same-family duplicate |
| P3 `jpx_daily_monthly_sponsor_temporal_pooling` | Sponsored ETF market making can be assessed daily rather than by monthly accumulation. **H1:** temporal de-pooling suppresses liquidity droughts and interday synchronization. **H0:** sign and magnitude depend on selectable rewards, weights, thresholds and market-maker costs. | Freeze one treatment axis and show an assignment independent of expected hard days and sponsor choice. | A clean residual could improve thin-ETF market design; failure identifies the missing causal contract. | market-native action or constraint / empirical-intervention | F2 closed |
| P4 `jpx_auction_targeted_sponsor_boundary` | Sponsors may target all-day, opening or closing-auction quoting. **H1:** localized obligations create a new temporal liquidity boundary. **H0:** they are direct auction incentives bundled with selected securities and thresholds. | Match the complete sponsor contract while changing only the target interval. | Could identify when liquidity support transfers across sessions; a null avoids a boundary metaphor. | market-native action or constraint / empirical-intervention | portfolio-pruned: bundled selection |
| P5 `jpx_weighted_hard_day_liquidity_response` | Daily sponsor weights can vary from 0.1 to 999.9. **H1:** high-weight days act as exogenous fields on liquidity. **H0:** asset managers choose weights using anticipated demand and risk. | Require a frozen weight rule independent of future state or randomized weights. | Would make the field interpretation causal; failure exposes endogenous assignment. | unresolved model disagreement / theory-mechanism | portfolio-pruned: assignment failure |
| P6 `moex_sufficient_volume_obligation_release` | A market maker may be released after reaching a daily sufficient-volume threshold. **H1:** threshold crossing creates a post-hit liquidity cliff. **H0:** release is permission, not an action, and the stopping time is endogenous. | Compare continuation and withdrawal policies at an identical post-threshold state and require maker identity. | A causal cliff could guide quota design; the twin identifies policy state as necessary. | new truth or control capability / theory-mechanism | F1 control close |
| P7 `hkex_minimum_display_time_exception` | HKEX obligations combine quote coverage, spread, size and minimum display time with exceptions. **H1:** the display-time rule creates a holding-time response. **H0:** it is a minimum-quote-life constraint already screened, with bundled exceptions. | Isolate display duration from spread, size, coverage and exception state. | A clean result would inform temporal commitment; a collision avoids reopening Cycle 12. | market-native action or constraint / simulator-method | portfolio-pruned: graph duplicate |
| P8 `cboe_canada_quote_presence_synchronization` | A common quote-presence percentage leaves a shared fraction of unconstrained time. **H1:** market makers synchronize their permitted absences. **H0:** the rule does not coordinate absence timing; common state and private policies do. | Match the compliance statistic while assigning different legal absence schedules. | A survivor could identify a coordination externality; failure localizes it to policy and state. | unresolved model disagreement / theory-mechanism | portfolio-pruned: state insufficiency |
| P9 `polymarket_relative_liquidity_reward_contest` | Rewards are based on normalized relative quote scores. **H1:** normalization produces liquidity condensation and fragile winner concentration. **H0:** it is a proportional contest whose equilibrium depends on costs, ownership and strategic response. | Apply common-scale and ownership-permutation twins, then require historical losing-quote and sample-state observability. | A residual could improve reward design; failure distinguishes book physics from score attribution. | market-native action or constraint / theory-mechanism | F2 closed |
| P10 `dydx_epoch_uptime_reward_memory` | dYdX aggregates randomized minute samples into epoch-level relative rewards. **H1:** the epoch creates a new liquidity-memory process. **H0:** the cumulative score is a finite-horizon controller state and the formula has already been reviewed directly. | Augment the state with current score and remaining horizon; test whether any non-Markov residual remains. | A null prevents relabelling accounting memory as physical aging. | market-native action or constraint / theory-mechanism | F1 state close |
| P11 `relative_reward_cross_market_migration` | A maker can shift effort toward markets with better reward coefficients. **H1:** coupled relative rewards create a universal migration law. **H0:** it is allocation under budget and heterogeneous costs, with no invariant sign. | Hold total budget and market states fixed while swapping maker-specific costs. | A residual could guide multi-market subsidy allocation; a null supplies a cost-completion test. | cross-domain theorem with market-specific obstruction / theory-mechanism | portfolio-pruned: generic allocation parent |
| P12 `eurex_overfulfilment_multiplier_tournament` | Coverage over-fulfilment and multi-product support earn multipliers. **H1:** the multiplier creates collective crowding or phase separation. **H0:** it is a rank/tier contract among strategic market makers. | Match score and budget while changing cost heterogeneity and rank eligibility. | Could expose a robust contest externality; failure maps it to established multi-maker contracting. | market-native action or constraint / simulator-method | F1 contract close |

## 4. F1 quick screens

### P6: sufficient-volume release -- permission is not intervention

The MOEX specification is mechanically clear: after sufficient market-maker transaction volume is
reached, the participant may be discharged from further quoting obligations or may quote only one
side under stated conditions. The rule does not cancel its quotes or force it to stop. Two market
makers at the same threshold-crossing state can follow opposite legal policies: one keeps quoting
because spreads remain profitable; the other withdraws because inventory risk dominates. The
post-hit response therefore is not determined by the threshold.

The hit time is also selected by executions and order flow. An event study around it conditions on
the very demand and liquidity state that generates the outcome. Without an assigned threshold,
maker identity, complete quote history and a policy model, this is a stopping-time/control problem,
not a market-physics quench.

### P10: epoch reward memory -- finite controller state

dYdX's published methodology accumulates sampled quote scores and allocates a relative reward pool
over an epoch. Adding current cumulative score, eligibility, remaining time and the current reward
coefficient to the state makes the rule Markov. Any slow response then comes from maker inventory,
beliefs, costs or learning, not from an unidentified physical memory. A primary review already
reconstructs the order books, evaluates the program and proposes parameter changes.

### P12: multiplier tournament -- established contract problem

Eurex's multiplier pays for coverage over-fulfilment and broad product support. Given participant
cost functions, inventory state, eligibility and the published score, the strategic problem is a
tiered principal--multi-agent contract or contest. Existing optimal make--take and multi-market-
maker work already derives exchange contracts and Nash quote policies. A new multiplier schedule
may be economically useful, but simulating it does not create a new physical law.

## 5. F2 collision and truth-contract screens

### 5.1 P1: MRX cross-role quote-obligation pooling

Abstract the eligible PMM and Preferred-MM quote seconds as totals `T_P,T_R` and fulfilled shares
`q_P,q_R`. Separate assessment requires

\[
q_P\geq 0.9,\qquad q_R\geq 0.9,
\]

whereas a combined bucket tests

\[
\frac{T_Pq_P+T_Rq_R}{T_P+T_R}\geq 0.9.
\]

The separate feasible set is contained in the combined one. For equal eligible time, `q_P=1` and
`q_R=0.8` fails separate assessment but passes the combined test. The SEC filing itself says that
the proposal permits quoting activity across roles to count together and publishes worked examples
whose numerators and denominators are combined across many symbols.

This is a genuine policy relaxation, but not a signed dynamic prediction. A member may keep every
quote unchanged, move effort from costly to cheap series, or use the freed compliance margin to
reduce total effort. Those responses are all compatible with the rule and are selected by private
inventory, adverse-selection risk, capital, technology and objectives. The static theorem is
feasible-set inclusion; the dynamic problem is partial resource pooling and constrained control.

The proposed implementation date is 2026-09-01, after this audit. Public consolidated options data
do not expose the member, badge, PMM and Preferred-MM attribution needed to reproduce the treatment
state. The parallel Phlx filing uses the same Nasdaq family and date, so it is not an independent
system replication.

**Hard closure:** `compliance_bucket_feasible_set_inclusion`,
`dynamic_response_requires_private_member_policy`, `public_role_attribution_absent`,
`future_post_period_absent`, `phlx_same_exchange_family_not_replication`, and
`resource_pooling_and_dmm_contract_prior`.

Diagnostic post-screen hostile-T0 was 4--10% with a 7% point estimate. It was elicited after hard
closure and is not a prospective forecast.

### 5.2 P3: JPX daily versus monthly sponsor assessment

The April 2026 JPX revision is unusually explicit, but it is not a one-dimensional temporal
intervention. An asset manager may choose the ETF, all-day/opening/closing target, daily or monthly
calculation, daily weights, fixed or volume-proportional payment, maximum number of rewarded market
makers, priority ranking, spread, size and quote-time obligations. Different sponsor conditions may
coexist on the same ETF. The daily option therefore changes the contract grammar, not merely a
clock.

A two-day control toy shows why no direction follows from aggregation alone. Let quoting costs be
`c_1,c_2`. A monthly pooled bonus and two daily bonuses with the same total budget can induce none,
one or both days depending on the thresholds, weights and the relation between each reward and
`c_d`. Swapping `c_1,c_2` while holding the public reward budget fixed reverses the favored day.
Inventory carry and adverse-selection risk add further state dependence. Thus neither lower
variance nor stronger hard-day liquidity is mechanically implied.

Assignment is also endogenous: asset managers select securities, dates, weights and targets using
anticipated market conditions. The official public statistics are aggregate spread/depth reports;
they do not by themselves provide a randomized sponsor assignment, market-maker cost state, or an
untouched same-contract holdout. Panayi et al. already argue that time-average obligations can be
misaligned with intraday demand and directly study replenishment duration. Contract theory and
multi-maker work occupy the general incentive-design core.

**Hard closure:** `daily_monthly_axis_bundled_with_contract_choices`,
`asset_manager_assignment_endogenous`, `reward_response_requires_private_cost_and_inventory`,
`public_statistics_not_member_contract_state`, `designated_market_maker_resiliency_direct_prior`,
and `market_making_contract_theory_parent`.

Diagnostic post-screen hostile-T0 was 5--12% with an 8% point estimate. It is not a prospective
forecast.

### 5.3 P9: Polymarket relative liquidity-reward contest

At a sample, the documented score has the normalized form

\[
r_i=B\frac{q_i}{\sum_j q_j},
\]

after a nonlinear transformation of spread, two-sided depth and configured cutoffs. A strategic
maker solves a payoff such as `r_i-C_i(q_i,X_i)`. This is a proportional contest. The market-wide
scale of quoting is determined by the cost functions and constraints, not by normalization itself.

Two invariance tests are fatal to a book-physics interpretation:

1. multiplying every `q_i` by the same positive factor preserves all reward shares while changing
   absolute displayed liquidity; and
2. permuting quote ownership preserves an anonymous limit-order book and every execution path but
   changes individual rewards and incentives.

Reward concentration is therefore neither necessary nor sufficient for depth concentration. It is
an attribution-and-contest statistic. The same broad formula is explicitly inspired by dYdX, and a
dYdX primary review already analyzes the methodology. Current Polymarket documentation exposes the
formula, but public executed transactions do not reconstruct every losing/resting quote and random
sample used for historical rewards; recent work also directly studies reward manipulation and
quote-attributed supply.

**Hard closure:** `normalized_score_is_proportional_contest`,
`common_scale_reward_invariance`, `owner_permutation_book_invariance`,
`strategic_cost_state_required`, `historical_sampled_quote_state_not_closed`, and
`dydx_formula_and_review_direct_prior`.

Diagnostic post-screen hostile-T0 was 3--9% with a 6% point estimate. It is not a prospective
forecast.

## 6. Collision manifests

### P1: quote obligations, pooling and liquidity fragility

1. Nasdaq MRX, *Notice of Filing and Immediate Effectiveness of Proposed Rule Change to Amend
   Market Maker Quoting Obligations*,
   [SEC release](https://www.sec.gov/files/rules/sro/mrx/2026/34-106065.pdf).
2. Nasdaq Phlx, parallel quoting-obligation amendment,
   [SEC release](https://www.sec.gov/files/rules/sro/phlx/2026/34-106064.pdf).
3. Anand and Venkataraman, *Market conditions, fragility, and the economics of market making*,
   [DOI](https://doi.org/10.1016/j.jfineco.2016.03.006).
4. Clark-Joseph, Ye, and Zi, *Designated market makers still matter: Evidence from two natural
   experiments*, [DOI](https://doi.org/10.1016/j.jfineco.2017.09.001).
5. Panayi et al., *Designating market maker behaviour in limit order book markets*,
   [DOI](https://doi.org/10.1016/j.ecosta.2016.10.008).
6. El Euch et al., *Optimal make--take fees for market making regulation*,
   [DOI](https://doi.org/10.1111/mafi.12295).
7. Baldacci, Possamaï, and Rosenbaum, *Optimal Make-Take Fees in a Multi Market-Maker Environment*,
   [DOI](https://doi.org/10.1137/19M1277412).

The first two sources define the exact policy change. The remaining work occupies obligation
effects, correlated liquidity withdrawal, replenishment, natural experiments and exchange--maker
contracting. The residual needs member-role state and a policy response not fixed by the rule.

### P3: sponsored ETF market-making contracts

1. JPX, *Revision of Sponsored ETF Market Making Scheme from April 2026*,
   [official specification](https://www.jpx.co.jp/english/equities/products/etfs/market-making/b5b4pj000001zbcx-att/vk0khi000000u5aa.pdf).
2. JPX, *Market Making Incentive Scheme Q&A*,
   [official page](https://www.jpx.co.jp/english/equities/products/etfs/market-making/04.html).
3. JPX, *Business Regulations*, Rule 69,
   [official regulation](https://www.jpx.co.jp/english/rules-participants/rules/regulations/tvdivq0000001vyt-att/business_regs_20250507.pdf).
4. Panayi et al., [designated-market-maker resiliency study](https://doi.org/10.1016/j.ecosta.2016.10.008).
5. El Euch et al., [single-maker optimal contract](https://doi.org/10.1111/mafi.12295).
6. Baldacci et al., [multi-maker optimal contract](https://doi.org/10.1137/19M1277412).
7. Bellia et al., *Paying for Market Liquidity: Competition and Incentives*,
   [working paper](https://doi.org/10.2139/ssrn.3354400).

The JPX documents provide a rich future market-design setting, but the many selectable contract
dimensions and endogenous sponsor assignment prevent a clean temporal-quench interpretation.

### P9: relative liquidity rewards

1. Polymarket, *Liquidity Rewards*,
   [official documentation](https://docs.polymarket.com/programs/liquidity-rewards).
2. dYdX Foundation, *Liquidity Provider Rewards*,
   [official methodology](https://www.dydx.foundation/blog/liquidity-provider-rewards).
3. Chan, *dYdX: Liquidity Providers' Incentive Programme Review*,
   [primary manuscript](https://arxiv.org/abs/2307.03935).
4. El Euch et al., [market-making contract parent](https://doi.org/10.1111/mafi.12295).
5. Baldacci et al., [multi-maker contract parent](https://doi.org/10.1137/19M1277412).
6. Anand and Venkataraman, [synchronized-liquidity-withdrawal evidence](https://doi.org/10.1016/j.jfineco.2016.03.006).
7. Shen et al., *The Ghosts of Polymarket: When Off-Chain Matches Meet On-Chain Reverts*,
   [primary manuscript](https://arxiv.org/abs/2606.16852).

The reward formula is public and useful for mechanism audit, but its normalized share is a contest
payoff rather than an absolute liquidity state, and the complete historical exposure state is not
publicly established.

## 7. Reusable gates

Cycle 15 adds four reusable discriminators without changing the machine protocol:

1. **Compliance-versus-action gate.** Relaxing or aggregating an obligation changes a feasible set;
   it does not assign the participant's action. A dynamic claim needs the response policy or an
   exogenous action assignment.
2. **Contract-axis gate.** A daily/monthly label is not a clock intervention when target, weight,
   payment, ranking, security and threshold are jointly selectable.
3. **Normalized-reward gate.** Test common scaling and ownership permutation before treating a
   relative score as a market state or order parameter.
4. **Stopping-time gate.** Releasing an obligation at an endogenous volume hit neither forces
   withdrawal nor provides an exogenous event time.

These are applications of the existing labelled resource-pooling, state-completion, intervention-
assignment and economic-unit invariance gates, so no new protocol field or validator rule is
needed.

## 8. What this cycle says about the 15% floor

Cycle 15 adds no prospective forecast resolution. The 15-percent lower endpoint remains an
uncalibrated budget brake for promotion to costly active status, not a score for whether an idea is
interesting. Applying it at F0 or F1 would be too early; cheap theorem, official-rule and truth-
contract work must remain unrestricted. Applying it only after a program survives F3 is still
reasonable because no current evidence supports a numerical change, and this cycle's closures were
exact reductions or missing assignments rather than pessimistic probability judgments.

Only one comparable full-T0 forecast has resolved. Re-estimation should wait for the preregistered
minimum number of independent resolutions and should examine calibration, not survivor count.
Lowering the threshold now would manufacture activity without repairing novelty or identification.

The next search should avoid incentives that merely score behavior. It should prioritize a public,
versioned market rule that directly executes or randomizes an action, exposes the complete native
state needed for replay, and has a predicted consequence false for standard constrained control,
resource pooling, proportional contests and designated-market-maker contracting. Until a program
reaches F3, no active topic, outcome access, simulation, purchase, outreach, EcoMD modification or
compute is authorized.
