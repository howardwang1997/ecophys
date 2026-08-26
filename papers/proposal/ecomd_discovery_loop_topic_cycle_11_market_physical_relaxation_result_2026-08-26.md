# EcoMD Discovery Loop topic cycle 11: market--physical relaxation

**Date:** 2026-08-26
**Literature cutoff:** 2026-08-26
**Mode:** outcome-blind, paper-only topic search
**Decision:** zero F3 audits and zero machine cards; three F2 formulations closed on hard
reduction, invariance, or direct-prior gates
**Authorization:** no simulator run, outcome access, dataset action, implementation, outreach,
sandbox, or compute

## 1. Search question

Cycle 11 tested whether moving from ordinary limit-order-book analogies to markets coupled to a
physical inventory or controller produces a stronger scientific question. The portfolio covered
soft liquidation, anomalous relaxation, electricity-market feedback, derivative hedging,
stablecoin control, emissions banking, mobility, perishability, halts, and thermal ramping.

The cycle also added one cheap guardrail to the funnel. A cross-domain phenomenon must have a
market-native control parameter or survive changes of representation, initial-condition family,
unit, clock, and distance metric. A phenomenon that can be manufactured by choosing an analyst's
temperature, condensate, or relaxation metric is not yet market physics.

## 2. Funnel accounting

| Stage | Count | Programs retained |
|---|---:|---|
| F0 raw portfolio | 12 | P1--P12 below |
| F1 quick screens | 6 | P1, P3, P4, P6, P7, P9 |
| F2 collision/contract screens | 3 | P1, P3, P9 |
| F3 full hostile audits | 0 | none |
| Machine cards | 0 | none |

Six programs were pruned from the portfolio, three failed quick screens, and three failed the
six-work collision screen. No probability estimate terminalized a program. Because no program
reached F3, no full-T0 forecast was elicited and no fifteen-work manifest was opened.

## 3. F0 portfolio: twelve question programs

| ID | Native object and rival explanations | Discriminating result | Value under either answer | Lane / archetype | Disposition |
|---|---|---|---|---|---|
| P1 `llamma_finite_rate_soft_liquidation_loop` | LLAMMA band inventory under a closed oracle-price cycle. **H1:** band conversion creates protocol-native rate-independent dissipation. **H0:** finite arbitrage arrival, gas, fee, and oracle lag create ordinary tracking loss. | Hold the price path and extrema fixed, stretch its duration, and test whether round-trip loss has a nonzero quasistatic limit distinct from the finite-rate correction. | Separates geometric soft-liquidation cost from execution friction; a null prevents calling latency loss a new collective law. | market-native action or constraint / theory-mechanism | F2 closed |
| P2 `llamma_kovacs_band_memory` | Two LLAMMA histories with the same oracle price and aggregate collateral/stablecoin. **H1:** the protocol retains a Kovacs-like memory. **H0:** omitted per-band inventory creates an observation-quotient artifact. | Match the complete band state as well as aggregates and compare future response. | A difference would locate genuine hidden protocol state; equality identifies the sufficient state. | unresolved model disagreement / theory-mechanism | portfolio-pruned |
| P3 `lob_mpemba_rule_relaxation` | Relaxation of a Markov order book after a rule or flow quench. **H1:** price-time priority and irreversible clearing cause a farther initial state to mix faster. **H0:** generic slow-mode overlap and analyst-chosen initial states create the crossing. | Preserve the generator and stationary law while changing only the initial family; separately vary the matching rule while matching modal overlap. | Could classify a rule-induced relaxation shortcut; a null prevents importing a generic Markov effect as market physics. | cross-domain theorem with market-specific obstruction / theory-mechanism | F2 closed |
| P4 `transactive_energy_cadence_synchronization` | Market-clearing cadence coupled to flexible physical loads. **H1:** price feedback synchronizes devices and destabilizes the grid. **H0:** physical controller dynamics and common exogenous load shocks explain oscillations. | Randomize clearing cadence or phase while preserving the physical load path and response curves. | Would identify a market-induced physical mode; a null rules out the market as the source. | unresolved model disagreement / theory-mechanism | F1 closed |
| P5 `market_grid_multirate_cosimulation_bias` | Coupled market and power-flow simulation at different clocks. **H1:** hard clearing events create a market-specific multirate error boundary. **H0:** ordinary operator-splitting and co-simulation error explain the discrepancy. | Compare against an event-resolved gold solver under clock refinement and boundary-aligned versus unaligned steps. | Could certify numerical fidelity; a null reduces the issue to standard co-simulation practice. | new truth or control capability / simulator method | portfolio-pruned |
| P6 `option_delta_hedge_liquidity_feedback` | Option inventory, delta hedging, and spot-book liquidity. **H1:** negative dealer gamma creates endogenous volatility amplification. **H0:** common information and exogenous volatility drive both hedge flow and spot moves. | Randomize signed option inventory in a controlled two-market simulator while holding the fundamental path fixed. | Would separate feedback from correlation; a null rejects a hedge-driven instability story. | unresolved model disagreement / theory-mechanism | F1 closed |
| P7 `stablecoin_multiloop_peg_mode_localization` | PegKeeper, borrow-rate, arbitrage, and liquidation loops. **H1:** controller-network topology localizes a slow peg-recovery mode. **H0:** arbitrage opportunity and user response, not the controller graph, determine recovery. | Hold controller state fixed and change only admissible arbitrage arrival/capital; then hold arbitrage policy fixed and rewire controller exposure. | Could identify a protocol-design bottleneck; a null rejects graph-only stability claims. | market-native action or constraint / theory-mechanism | F1 closed |
| P8 `ridehail_matching_radius_congestion_transition` | Driver--rider matching radius coupled to road congestion. **H1:** thicker matching creates a market-induced jamming transition through empty pickup miles. **H0:** ordinary demand load and routing generate congestion. | Randomize matching radius with the same requests, fleet, road network, and routing policy. | Could connect market design to physical throughput; a null bounds the externality of matching. | market-native action or constraint / empirical intervention | portfolio-pruned |
| P9 `carbon_compliance_inventory_condensation` | Banked emissions allowances approaching a compliance deadline. **H1:** a finite-cap inventory condenses among a small set of firms and creates a collective price mode. **H0:** standard intertemporal banking, market power, and firm-size heterogeneity explain concentration and price paths. | Split or merge economically identical firms while preserving aggregate endowments, abatement costs, and actions; test whether the proposed condensate and law remain invariant. | Could expose a new finite-resource mechanism; a null returns the problem to established banking economics. | new truth or control capability / theory-mechanism | F2 closed |
| P10 `perishable_market_expiry_wave` | Goods with expiring inventory in a double auction. **H1:** synchronized expiry produces an endogenous reaction front in prices and inventory. **H0:** a deterministic terminal-value schedule plus ordinary inventory optimization explains the wave. | Desynchronize expiry while preserving total remaining shelf life and demand. | Could classify a perishable-market collective mode; a null identifies a scheduling artifact. | cross-domain theorem with market-specific obstruction / theory-mechanism | portfolio-pruned |
| P11 `price_limit_reopening_history_response` | A halted market's reopening book and order history. **H1:** the halt stores path-dependent market memory beyond the reopening book. **H0:** the complete queued-order and participant state is Markov, while public aggregates omit it. | Match the complete frozen queue and participant state across different halt histories before reopening. | A difference would locate missing native state; equality closes a history-only narrative. | new truth or control capability / empirical intervention | portfolio-pruned |
| P12 `unit_commitment_ramp_hysteresis` | Electricity bids, commitment states, minimum run times, and ramp limits. **H1:** market clearing creates a rate-independent physical hysteresis law. **H0:** mixed-integer active-set path dependence fully explains it. | Compare two bid paths with the same endpoints under an exact unit-commitment oracle and under a convexified dispatch. | Could isolate a market-specific obstruction; a null reduces it to parametric optimization. | cross-domain theorem with market-specific obstruction / theory-mechanism | portfolio-pruned |

P2, P5, P8, P10, P11, and P12 were pruned before literature expansion. P2 and P11 are exact
full-state Markov versus aggregate-observation twins; P5 is generic multirate co-simulation unless a
new market boundary theorem is stated; P8 has direct wild-goose-chase and matching-radius theory;
P10 is ordinary perishable-inventory scheduling without a new market interaction; and P12 is
mixed-integer active-set path dependence unless a non-optimization residual is first proved.

## 4. F1 quick screens

### P4: transactive-energy cadence synchronization -- close

This is an important physical-market problem, but not an open headline. Alvarado et al. analyzed
power systems coupled to market dynamics and the effect of faster dispatch updates in 2001.
Krause, Boerries, and Bornholdt showed that adaptive power markets can amplify fluctuations through
consumer synchronization. Nazir and Hiskens directly studied sustained oscillations induced by
transactive control. The proposed cadence intervention is a good validation fixture, not a new
Nature-level mechanism.

### P6: option-delta-hedge feedback -- close

The exact fork is already occupied. Illiquid-market option theory derives nonlinear price feedback
from dynamic hedging; Kawakubo, Izumi, and Yoshimura use a two-market artificial market and vary
hedging frequency; Anderegg, Uhlmann, and Sornette quantify the sign of spot-volatility feedback
from aggregate option gamma. A new simulator would reproduce an established mechanism unless it
had external randomized dealer-inventory truth, which is not available here.

### P7: stablecoin multi-loop mode localization -- close

The controller graph alone does not determine peg recovery. Two systems with identical PegKeeper,
rate, debt, and pool state but arbitrageurs with zero versus ample capital have opposite recovery.
Recent work already models stablecoin peg restoration as a mean-field game and designs peg controls
as dynamic games. The remaining crvUSD-specific exercise is protocol risk analysis, not a new
controller-network law.

## 5. F2 collision and truth-contract screens

### 5.1 P1: finite-rate LLAMMA loop

The five-part contract was:

- `X`: oracle price, active band, per-band collateral/stablecoin inventory, fees, debt, and
  arbitrage capacity;
- `do(A)`: a closed external-price path with fixed extrema and shape, executed at several durations;
- `Y`: round-trip borrower value loss and signed band-flow loop area;
- `H1:H0`: a nonzero protocol-geometric quasistatic term versus a finite-rate tracking/LVR term;
- `T`: bit-exact Curve contracts or the official simulator under an exogenous price path and a
  separately declared arbitrage scheduler.

The minimal decomposition is decisive. Under instantaneous arbitrage, a closed price path produces
the protocol's adiabatic band-conversion result; the Curve whitepaper and official LLAMMA simulator
already define and optimize those losses. Once arbitrage is delayed, the extra term is stale-price
loss, fee, gas, and optimal timing, covered by AMM LVR and arbitrage-timing theory. Stretching time
does not reveal a third mechanism: it separates two occupied terms.

The collision neighborhood included the Curve stablecoin whitepaper, the official
`curvefi/llamma-simulator`, `crvUSDsim`, general LVR theory, optimal arbitrage timing, and recent
dynamic-AMM path-cost geometry. The exact implementation can still support useful risk engineering,
but the frozen scientific claim is not irreducible.

**Hard closure:** `adiabatic_loss_defined_by_protocol`, `official_loss_simulator_direct_artifact`,
`finite_rate_term_reduces_to_lvr_and_arbitrage_timing`, and
`independent_same_mechanism_system_missing`.

Diagnostic post-screen hostile-T0 was 4--9% with a 6% point estimate. The estimate did not cause
closure and is not a prospective forecast.

### 5.2 P3: matching-rule Mpemba relaxation

The five-part contract was:

- `X`: a finite-state Markov order book and its stationary law after a flow-parameter quench;
- `do(A)`: initialize from two market-native pre-quench stationary families, then apply the same
  post-quench generator;
- `Y`: first crossing and asymptotic decay of a predeclared distance to stationarity;
- `H1:H0`: price-time-priority nonnormality versus generic modal-overlap cancellation;
- `T`: an exact generator and spectral decomposition, followed only later by simulator fixtures if
  a market-specific theorem survived.

The strong effect occurs whenever one initial distribution has zero overlap with the slowest mode
while another, nominally closer distribution does not. That is the generic Markovian Mpemba
mechanism already formalized by Lu--Raz and Klich et al. It neither requires an order book nor
price-time priority. Conversely, fixing the same matching rule but choosing a one-parameter initial
family that never crosses the slow-mode-zero surface removes the effect.

There is also no market-native analogue of temperature in the formulation. Initial distance,
family, and observable can be changed without altering the exchange. Markovian order-book
ergodicity supplies the generator but not a new cause. Nonequilibrium active Markov chains already
cover broken detailed balance, complex modes, and oscillatory crossings.

**Hard closure:** `generic_markov_mode_overlap_exact_parent`,
`market_temperature_and_initial_family_not_native`, `distance_metric_and_observable_dependence`,
and `matching_rule_neither_necessary_nor_sufficient`.

Diagnostic post-screen hostile-T0 was 2--7% with a 4% point estimate. It is not a prospective
forecast.

### 5.3 P9: carbon-compliance inventory condensation

The five-part contract was:

- `X`: firm allowance banks, expected emissions, abatement costs, cap, and compliance time;
- `do(A)`: banking versus no banking, or a frozen compliance-calendar change;
- `Y`: allowance concentration, price volatility, emissions volatility, and compliance shortfall;
- `H1:H0`: finite-resource condensation versus established strategic intertemporal banking;
- `T`: a controlled emissions-market experiment or exact equilibrium model with complete
  endowments, actions, and compliance.

The proposed condensate is not invariant to the economic unit. Splitting one firm into two
subsidiaries with proportional endowments, costs, and coordinated actions changes holder counts,
largest-holder share, and many participation-ratio statistics while preserving the aggregate
allocation, feasible trades, price path, emissions, and compliance. Aggregate bank concentration
can instead be made identical under different market power and expectations.

The substantive questions are already direct emissions-market economics. Laboratory experiments
study bankable allowances, price controls, uncertainty, compliance, price volatility, and emissions
volatility; dynamic equilibrium and structural work model banking and investment. Rebranding
concentration as condensation does not create a unit-invariant collective law.

**Hard closure:** `holder_unit_refinement_changes_condensate`,
`banking_equilibrium_and_experiment_direct_prior`, `concentration_does_not_identify_collective_mode`,
and `market_power_expectations_alias`.

Diagnostic post-screen hostile-T0 was 1--5% with a 3% point estimate. It is not a prospective
forecast.

## 6. Six-work collision manifests

Each F2 program was checked against at least six primary or official sources. These are collision
screens, not fifteen-work F3 manifests.

### P1: LLAMMA and AMM loss

1. Curve, *Curve Stablecoin Design* ([official whitepaper](https://resources.curve.fi/pdf/curve-stablecoin.pdf)).
2. Curve, [`llamma-simulator`](https://github.com/curvefi/llamma-simulator).
3. Curve research tooling, [`crvUSDsim`](https://crvusdsim.readthedocs.io/en/latest/).
4. Milionis et al., *Automated Market Making and Loss-Versus-Rebalancing*
   ([manuscript](https://arxiv.org/abs/2208.06046)).
5. Milionis et al., *Optimal Arbitrage Timing between Decentralized and Centralized Exchanges*
   ([primary manuscript](https://pages.stern.nyu.edu/~jreed/papers/paper29.pdf)).
6. Willetts, *Riemannian Geometry of Optimal Rebalancing in Dynamic Weight Automated Market
   Makers* ([manuscript](https://arxiv.org/abs/2603.05326)).

### P3: anomalous Markov relaxation and LOB generators

1. Lu and Raz, *Nonequilibrium thermodynamics of the Markovian Mpemba effect and its inverse*
   ([DOI](https://doi.org/10.1073/pnas.1701264114)).
2. Klich et al., *Mpemba Index and Anomalous Relaxation*
   ([DOI](https://doi.org/10.1103/PhysRevX.9.021060)).
3. Biswas and Pal, *Mpemba effect on nonequilibrium active Markov chains*
   ([DOI](https://doi.org/10.1103/PhysRevE.111.054136)).
4. Huang and Rosenbaum, *Ergodicity and Diffusivity of Markovian Order Book Models*
   ([DOI](https://doi.org/10.1137/16M1064337)).
5. Cont and de Larrard, *Price Dynamics in a Markovian Limit Order Market*
   ([DOI](https://doi.org/10.1137/110856605)).
6. Klich et al., *The Mpemba index and anomalous relaxation*
   ([original manuscript](https://arxiv.org/abs/1711.05829)).

### P9: emissions banking and compliance

1. Olson, Hoffman, and Houser, *An Experimental Investigation of Repeated Auctions and Secondary
   Market Trading in Emissions Markets with Bankable Allowances*
   ([primary record](https://www.mitre.org/news-insights/publication/experimental-investigation-repeated-auctions-and-secondary-market-trading)).
2. Stranlund, Costello, and Chavez, *Price controls and banking in emissions trading*
   ([DOI](https://doi.org/10.1016/j.jeem.2014.04.002)).
3. Godby et al., *Emissions Trading with Shares and Coupons when Control over Discharges Is
   Uncertain* ([DOI](https://doi.org/10.1006/jeem.1997.0977)).
4. Stranlund, Chavez, and Field, *Emissions variability in tradable permit markets with imperfect
   enforcement and banking* ([DOI](https://doi.org/10.1016/j.jebo.2005.02.007)).
5. Kollenberg and Taschini, *Business cycles and emission trading with banking*
   ([DOI](https://doi.org/10.1016/j.euroecorev.2017.10.015)).
6. Fowlie, Reguant, and Ryan, *Dynamic Incentives and Permit Market Equilibrium in Cap-and-Trade
   Regulation* ([DOI](https://doi.org/10.1257/mic.20190377)).

## 7. What this cycle says about the 15% floor

Cycle 11 supplies no new calibration observation for the 15% hostile-T0 lower-endpoint rule.
There is still no resolved prospective full-T0 forecast. None of the three F2 programs reached the
point at which a forecast should be frozen, because each failed an independent hard gate before a
full evidence neighborhood was opened.

This is precisely why the floor must not be used in F0--F2. P1, P3, and P9 were closed by exact
decomposition, non-invariance, and direct prior, respectively; changing their probability
intervals would not change the decision. The 15% rule remains only an uncalibrated brake on costly
`active` status until at least twenty comparable prospective full-T0 forecasts resolve. A bounded
information action remains governed by its own break-even probability `(C-S)/(B-S)` and is
inapplicable after a hard gate has failed.

## 8. Decision and next search move

No Cycle 11 formulation merits a card, F3 forecast, simulator experiment, or data action. The
reusable outputs are:

- a quasistatic-versus-finite-rate decomposition test for protocol mechanisms;
- a native-control-parameter and representation-invariance gate for imported physical effects;
- a slow-mode-overlap counterexample for anomalous market relaxation; and
- an entity-split invariance test for market concentration or condensation claims.

The next cycle should not search for another named statistical-physics effect. It should begin from
one of two sources: a newly available complete-state intervention that changes a scientific
decision, or a concrete mismatch between two primary market models that predict opposite outcomes
under the same legal action. No Cycle 11 result authorizes execution.
