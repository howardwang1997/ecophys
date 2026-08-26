# EcoMD Discovery Loop Topic Cycle 12: Price--Time Commitment

**Date:** 2026-08-26  
**Terminal status:** bounded cycle complete; zero cards; the sole F3 route is failed-closed  
**Scientific scope:** simulated markets, market microstructure, and financial physics  
**Outcome discipline:** no simulation, market outcome, paid data, sandbox, outreach, EcoMD
implementation, or compute was used

## 1. Decision

Cycle 12 began from a genuine market-design tension rather than a named physical analogy. EBS
Conditional Price Increments (CPI) let eligible orders use a finer price grid and a potentially
different minimum quote life in the same book. This created a plausible question: can finer price
resolution and longer commitment be summarized by a low-dimensional, transportable regime law?

The answer at T0 is **no**. The strongest frozen formulation,
`price_time_commitment_cpi_scaling`, proposed

\[
  \chi=\frac{\sigma\sqrt{\tau}}{\delta},\qquad
  \rho=\lambda\tau,
\]

with tick increment \(\delta\), minimum quote life \(\tau\), short-horizon reference-price
diffusion \(\sigma\), and aggressive-order intensity \(\lambda\). It fails for four independent
reasons:

1. under a Brownian reference price, the apparent \(\chi\) boundary is exactly an ordinary
   first-passage calculation;
2. matching \(\chi\) and \(\rho\) does not fix the sign or magnitude of liquidity response once
   informed-flow composition, jump tails, queue position, inventory, and bilateral credit vary;
3. CPI mode is trader-chosen and state-gated rather than assigned, while public EBS market data are
   price-level aggregates without EBS order identifiers or priority; and
4. neither two independent native physical-time simulators nor a second independent real
   fine-price/slow-cancel mechanism satisfy the same-estimand contract.

The full-T0 forecast was genuinely frozen before the full evidence neighborhood at 5--25%, with a
12% point forecast. It resolves **false**. The Brier score is \((0.12-0)^2=0.0144\). One resolved
forecast is evidence about this forecast only; it is not enough to calibrate or revise the 15%
active-status brake.

## 2. Funnel and complete portfolio

| Stage | Limit | Used | Result |
|---|---:|---:|---|
| F0 raw question programs | 12 | 12 | Complete portfolio recorded |
| F1 quick screens | 6 | 6 | Three cheap closes, three advanced |
| F2 collision/contract screens | 3 | 3 | Two closed, one advanced |
| F3 full hostile audits | 2 | 1 | One failed-closed |
| Machine cards | 1 | 0 | No authorization |

| ID | Question program | Lane | Archetype | Terminal disposition |
|---|---|---|---|---|
| P1 | Price--time commitment under EBS CPI | native action | theory/mechanism | F3 full close |
| P2 | Trading-frequency liquidity bifurcation | model disagreement | theory/mechanism | F1 direct-parent close |
| P3 | Asymmetric speed-bump sign map | model disagreement | empirical intervention | F1 saturated close |
| P4 | Hidden-liquidity transparency sign | model disagreement | empirical intervention | portfolio prune |
| P5 | Venue-outage direction of price discovery | truth capability | empirical intervention | F2 direct-prior/assignment close |
| P6 | Settlement-cycle liquidity--risk response | native constraint | empirical intervention | F1 mature comparative statics close |
| P7 | Volatility-adaptive minimum quote life | cross-domain obstruction | theory/mechanism | F2 absorbed into P1/direct prior |
| P8 | CPI mode-occupancy metastability | native action | theory/mechanism | portfolio prune: endogenous choice |
| P9 | Message-efficiency quota control | native constraint | measurement method | portfolio prune: standard controller |
| P10 | Joint tick--fee liquidity grid | native action | theory/mechanism | portfolio prune: saturated design space |
| P11 | Quote age as a sufficient MQL state | cross-domain obstruction | theory/mechanism | portfolio prune: observation quotient |
| P12 | Cross-venue clock-mismatch resonance | cross-domain obstruction | theory/mechanism | portfolio prune: graph duplicate |

P2 closed because the direct theory of trading frequency already contains the relevant opposing
liquidity effects. P3 closed because speed, speed bumps, and fast/slow trader composition already
have theory, laboratory, and exchange evidence; the sign depends on the news and liquidity-supply
environment. P6 did not expose a mechanism-specific theorem beyond established settlement-risk and
liquidity comparative statics.

P5 had a scientifically meaningful real-system question, but an outage is not an assigned
intervention and recent direct work already studies market outages and price discovery. P7 was not
independent of P1: minimum-resting-time theory and the official UK assessment already state the
opposing stale-quote, fill, depth, spread, and volatility forces. Only P1 therefore justified F3.

## 3. Prospective F3 freeze

The F3 subject, hypotheses, controls, outcome restrictions, and full-T0 forecast were frozen at
2026-08-26T03:53:57Z before opening the fifteen-work neighborhood.

- **H1:** \(\chi\) and \(\rho\) define a nontrivial price--time commitment regime boundary that
  survives changes of units, event clock, simulator lineage, and market scale.
- **H0:** the proposed collapse is either ordinary barrier/queue mathematics or fails when the
  omitted marked event kernel, strategic state, and CPI selection rule vary.
- **Discriminating result:** hold \(\chi\) and \(\rho\) fixed while changing only a legal omitted
  mechanism. A sign reversal kills the low-dimensional law; a repair requiring the full event
  kernel kills the claimed compression.
- **Forecast:** lower 0.05, point 0.12, upper 0.25 for full T0 activation eligibility.

The pre-audit basis used only the official CPI rule, the official EBS Ultra data catalog, and
Cartea--Wang minimum-resting-time theory. No retrospective probability was inserted into the
forecast ledger.

## 4. Analytic audit

### 4.1 The positive toy is an exact parent reduction

Let the efficient reference price follow \(dV_t=\sigma\,dW_t\), and let a resting quote become
economically stale when \(V\) crosses a barrier \(h=m\delta\) before cancellation is permitted at
time \(\tau\). By the reflection principle,

\[
 \Pr\!\left(\sup_{0\le t\le\tau}(V_t-V_0)\ge m\delta\right)
 =2\left[1-\Phi\!\left(\frac{m\delta}{\sigma\sqrt{\tau}}\right)\right].
\]

Thus the cleanest possible dependence on \(\chi\) is not a new market-physics theorem. It is the
standard Brownian first-passage probability written in market units. Adding a Poisson aggressive
flow with intensity \(\lambda\) supplies ordinary exposure \(1-e^{-\lambda\tau}\), which explains
why \(\rho\) appears but does not create a collective law.

### 4.2 Parameter-completion twin A: marked flow reverses the response

Construct two legal books with identical \(\delta,\tau,\sigma,\lambda\), queue depth, spread, and
hence identical \(\chi,\rho\).

- In system A, aggressive arrivals are predominantly liquidity-motivated. Longer commitment raises
  the probability of a profitable fill and can support fine-price depth.
- In system B, the same total arrival intensity is predominantly informed and conditional on an
  impending price move. Longer commitment raises adverse selection and makes the same fine-price
  mode loss-making.

The response sign changes while both proposed controls are fixed. Adding the informed fraction is
not a harmless third coordinate: its state dependence, signal quality, queue selectivity, and
credit filtering require the marked order-arrival kernel. Gao--Wang's latency model already makes
profit depend on uninformed arrival mass relative to price-jump intensity, and the broader fast/slow
market literature contains the same opposing force.

### 4.3 Parameter-completion twin B: matched variance does not match first passage

Construct a Brownian reference price and a symmetric compound-jump price with the same
short-horizon variance \(\sigma^2\tau\), the same \(\delta,\tau,\lambda\), and therefore the same
\(\chi,\rho\). In the jump model, choose rare jumps of magnitude proportional to
\(\sigma\sqrt{\tau/q}\) with probability of order \(q\). As \(q\) changes, the barrier-crossing
probability and overshoot distribution change by order one relative to the Brownian formula while
the variance-based control is unchanged.

Replacing \(\sigma\) by a full first-passage functional would make prediction possible but would
also remove the proposed scaling result: the "control parameter" would then contain the answer.

### 4.4 The native CPI state is not a two-mode randomized material

The official mechanism is more complex than a fixed coarse/fast versus fine/slow choice. A sub-pip
order is accepted only under spread and improvement constraints, subject to trade, crossing, and
join exceptions; an accepted order can remain after the book changes. Bilateral credit and
self-match prevention can also let a crossing order rest. Traders choose whether and when to use
the alternate grid. Consequently, occupancy of the fine grid is a selected response to the same
state that predicts subsequent liquidity. It is not an assignment variable.

This closes the causal interpretation even before considering inventory, participant identity,
latency, and adaptive strategies. A simulator can randomize the choice, but that would answer a
different question from observed CPI use.

## 5. Direct-prior neighborhood

The completed F3 neighborhood contains more than fifteen primary or official sources:

1. CME's CPI rule: conditional sub-pip eligibility, alternate MQL, exceptions, and persistence.
2. CME's 2024 EBS notice: standard-MQL reduction, CPI launch, EBS Ultra, and conflation changes.
3. CME's 2025 notice: pair-specific alternate-MQL changes.
4. CME's 2026 notice: further standard and alternate MQL reductions.
5. CME's EBS Ultra historical-data catalog.
6. CME MDP 3.0 EBS MBP schema.
7. Cartea and Wang, *Market Making with Minimum Resting Times*.
8. Chaboud, Hjalmarsson, and Zikes, *The Evolution of Price Discovery in an Electronic Market*.
9. Chaboud, Dao, Vega, and Zikes, *What Makes HFTs Tick?*.
10. Yueshen, *Queuing Uncertainty of Limit Orders*.
11. Menkveld and Zoican, *Need for Speed? Exchange Latency and Liquidity*.
12. Hoffmann, *A Dynamic Limit Order Market with Fast and Slow Traders*.
13. Baldauf and Mollner, *High-Frequency Trading and Market Performance*.
14. Pagnotta and Philippon, *Competing on Speed*.
15. Budish, Cramton, and Shim, *The High-Frequency Trading Arms Race*.
16. Gao and Wang, *Optimal Market Making in the Presence of Latency*.
17. Bonart and Gould, *Latency and Liquidity Provision in a Limit Order Book*.
18. Gayduk and Nadtochiy, *Liquidity Effects of Trading Frequency*.
19. the UK Foresight minimum-quote-life impact assessment.
20. the Eurex speed-bump field study and the randomized-versus-fixed speed-bump laboratory study.

This neighborhood does not contain a paper with the exact title "CPI scaling law." That lexical
gap is immaterial. The proposed positive result is an exact barrier/arrival reduction, and the
remaining sign question is already the central object of minimum-resting-time, latency, speed, and
fast/slow market-making theory.

## 6. Data and simulator contracts

### 6.1 EBS observation contract fails at order lifecycle

The official EBS MDP template reports price-level price, quantity, order count, and update action.
Its `NoOrderIDEntries` field has valid value zero and is explicitly "not used for EBS markets."
Therefore the public contract does not expose individual EBS order IDs, execution priority,
submission-to-cancel age, locked cancellation attempts, or participant inventory. Alternate price
levels and trades can be observed, but the proposed commitment exposure cannot be reconstructed as
an order-level treatment.

EBS Ultra history also requires a CME information licence. The public catalog does not establish
the exact CPI historical coverage, acquisition price, derived-data publication rights, or a
participant-level treatment key. Moreover, the 2024 CPI introduction coincided with standard-MQL,
market-data, and EBS Ultra changes. The field transition is bundled.

EUR/USD, AUD/USD, and USD/TWD are products on one CME/EBS mechanism lineage, not independent field
replications. No second public real venue was found with the same fine-price eligibility plus
alternate minimum-quote-life action and lawful complete lifecycle data.

### 6.2 Two-native-simulator contract also fails

- **ABIDES** has nanosecond event scheduling and latency, so a custom exchange agent could implement
  CPI and MQL. That would be one researcher-authored implementation rather than native independent
  validation.
- **PAMS 0.2.2** has a step clock rather than a physical latency domain. Its native runner also
  consumes shared scheduler randomness as order-list activity changes. Adding a physical MQL and
  separate random streams changes the core control semantics.
- **Bourse 0.4.0** is an independent fixed-step book, but the mapping from steps to milliseconds is
  analyst-chosen and it has no native CPI/MQL mechanism.

ABIDES plus modified PAMS or Bourse would show that two custom programs can reproduce a chosen toy;
it would not establish a shared native \(\tau\)-estimand. The two-lineage gate therefore fails.

## 7. Terminal verdict and forecast resolution

`price_time_commitment_cpi_scaling` is **failed-closed** with the following independent failure
codes:

- `brownian_barrier_crossing_exact_parent`;
- `marked_arrival_and_jump_kernel_missing_controls`;
- `endogenous_cpi_mode_selection`;
- `ebs_mbp_order_lifecycle_absent`;
- `single_exchange_lineage_no_independent_real_mechanism`;
- `two_native_physical_time_simulator_contract_missing`;
- `mrt_tick_latency_direct_prior_saturated`; and
- `frozen_full_t0_forecast_resolved_false`.

The forecast resolves false because multiple named hard gates failed, not because its 5% lower
endpoint or 12% point estimate was below 15%. The forecast policy remains unchanged: review the
active-status floor only after at least twenty comparable full-T0 resolutions and examine
calibration, discrimination, and action cost rather than selecting a cutoff from one success or
failure.

Reopening requires a child theorem that is false for Brownian barrier crossing and ordinary marked
queue models, remains predictive after holding all proposed dimensionless groups fixed while the
event kernel varies, and has two native physical-time implementations plus an independent real
price--time mechanism with lawful order-lifecycle or randomized-assignment data.

No market outcome, simulator run, dataset purchase, sandbox, outreach, model implementation,
EcoMD edit, or compute is authorized by this result.

## 8. Reusable scientific and process residue

Cycle 12 adds two reusable screening tools.

1. **Same-estimand sign-disagreement gate.** Two papers count as an unresolved fork only if their
   opposite signs concern the same native state, legal intervention, response, and conditioning
   set. Opposite headlines under different treatments are not a discovery opportunity.
2. **Dimensionless parameter-completion twin.** Before escalating a proposed scaling law, match all
   proposed dimensionless groups and vary one omitted legal event kernel or strategic state. If the
   prediction reverses, or repair requires encoding the full kernel, close the universal law and
   retain only the narrower measurement question.

The Brownian first-passage calculation, the marked-flow twin, the matched-variance jump twin, and
the official EBS order-lifecycle schema audit remain reusable negative assets. The next cycle should
seek a market-native intervention whose assignment and complete state are observable, or a theorem
whose conclusion is false for the generic parent class, rather than another fitted dimensional
collapse.
