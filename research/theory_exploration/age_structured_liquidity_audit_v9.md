# Age-structured liquidity resilience — V9 novelty and evidence audit

**Audit date:** 2026-08-13
**Branch:** `age-structured-liquidity-audit-v9`
**Final decision:** `V9_NO_SURVIVOR_SCOPE_AND_PRIOR_ART`
**Candidate state:** `RETIRED_NO_WITNESS`
**Outcome access:** no V9 target aggregate, shock response, fitted hazard or predictive result was computed

## 1. Candidate that was attacked

The observable starting point was an order-level limit order book, not an EcoMD residual. Let
`J_t` be the displayed orders in a frozen near-touch region at time `t`, with remaining size `q_j`, age `a_j(t)`
and predeclared observable covariates `x_j(t)`. For horizon `h`, a prospective competing-risk model would define

\[
S_j(h\mid\mathcal F_t)
=\Pr(T_j>t+h\mid x_j(t),a_j(t),\mathcal F_t),
\qquad
Q(t)=\sum_{j\in J_t}q_j,
\]

and the survival-weighted standing depth

\[
D_h(t)=\sum_{j\in J_t}q_j S_j(h\mid\mathcal F_t)
=\mathbb E\!\left[
\sum_{j\in J_t}q_j\mathbf 1\{T_j>t+h\}
\middle|\mathcal F_t
\right].
\]

The equality is conditional-expectation linearity, not a new identity. `T_j` is exit by either displayed execution
or cancellation, so `D_h` means expected *future standing volume*. It is not automatically willingness to trade:
execution removes an order precisely because it supplied liquidity, whereas cancellation removes it without doing
so. Any economic interpretation therefore requires a predeclared competing-risk decomposition rather than one
undifferentiated survival score.

The narrow empirical hypothesis was a post-depletion separation:

> after a large marketable-order shock, raw depth `Q` may return to its pre-shock reference before
> survival-weighted standing depth `D_h`; a prospectively defined recovery gap may predict a second depletion or
> price continuation beyond raw depth, deeper-book shape, order flow and cancellation-rate baselines.

This would concern real observable market structure. It would not make a simulator error into market physics.

## 2. Direct prior-art map

| Neighbourhood | Direct result | Consequence for V9 |
|---|---|---|
| path-dependent queue survival | Noble, Rosenbaum and Souilmi, [*Bridging the Reality Gap in Limit Order Book Simulation*](https://arxiv.org/abs/2603.24137), explicitly state that equal-sized queues can have different depletion times depending on how they formed and contrast gradually depleted, conviction-rich queues with recently placed orders | The central state-completeness motivation is already stated directly. Adding age/path features to a queue-reactive state is not a new method claim. |
| fleeting/static depth decomposition | Roseman, [*Order Behavior in High Frequency Markets*](https://egrove.olemiss.edu/etd/562/), reconstructs total, fleeting and static books, decomposes displayed depth and studies their different liquidity contributions | “Displayed depth is not equally durable” and an ex-post lifetime partition of depth are occupied empirical objects. |
| equilibrium overshooting liquidity | Zhou, [*Queuing Uncertainty of Limit Orders*](https://ink.library.smu.edu.sg/lkcsb_research/7748/), derives clustered new submissions followed by immediate cancellations and a rapidly reverting depth overshoot from latency-driven queue uncertainty | A young replenishment cohort that creates apparent depth and then disappears already has a direct equilibrium mechanism. |
| lifecycle filtering | Anantha, Jain and Maiti, [*Order-Flow Filtration and Directional Association with Short-Horizon Returns*](https://arxiv.org/abs/2507.22712), filter by lifetime, modification count and modification timing | Simple lifetime filtering is not a method contribution. Their standing-book result is also a hard negative baseline: lifetime filtering changes directional association only modestly and heterogeneously. |
| cancellation hazard and queue position | Dahlström, [*The determinants of limit order cancellations*](https://onlinelibrary.wiley.com/doi/10.1111/fire.12363), estimates competing termination hazards with time-varying depth and queue-position covariates | Age-conditioned cancellation/execution risk belongs to established duration and competing-risk analysis. |
| shock recovery of raw depth | Xu et al., [*Limit-order book resiliency after effective market orders*](https://arxiv.org/abs/1602.00731), measure spread, depth and order-intensity recovery after market-order shocks | Raw depth recovery and its link to replenishing order flow are established empirical targets. |
| flow/cancellation resilience beyond snapshots | Bechler and Ludkovski, [*Order Flows and Limit Order Book Resiliency on the Meso-Scale*](https://arxiv.org/abs/1708.02715), find limit flows and relative addition/cancellation rates more predictive than shallow depth | A V9 predictor must beat direct flow, cancellation and deeper-shape baselines; raw depth alone is not a credible comparator. |
| queue-flow accounting | Muni Toke, [*The order book as a queueing system*](https://arxiv.org/abs/1311.5661), relates average depth, execution probability and conservation of order flows in a birth--death model | Cohort mass balance or survival-weighted flow accounting is not automatically an irreducible mathematical mechanism. |

The two most decision-relevant PDF pages were rendered and visually inspected: page 11 of Noble et al. for the
path-dependent queue-survival statement and page 13 of Anantha et al. for the weak, heterogeneous standing-book
filter result. The depth-recovery section of Xu et al. and the depth-versus-flow result of Bechler--Ludkovski were
also rendered and inspected. Roseman's open dissertation was extracted directly; its introduction and empirical
sections explicitly construct separate fleeting and static books.

## 3. Why the exact residual gap is not promoted

The audit did not find a paper with the exact phrase “recovery-time gap between raw and prospectively
survival-weighted depth.” That absence is not a novelty pass.

1. **The proposed statistic composes occupied objects.** Queue-path dependence, lifetime-conditioned filtration,
   fleeting/static depth, overshooting new liquidity and post-shock depth recovery are all explicit. The residual
   gap is a reasonable empirical recombination, not yet a new law or computational method.
2. **There is no theoretically fixed sign.** Fresh orders can be fleeting because of queue uncertainty, but they
   can also be aggressive replenishment by committed liquidity providers. Old orders can be persistent, stale or
   close to execution. Competing cancellation and execution risks can reverse an undifferentiated age effect.
3. **Ex-post labels would leak the future.** Classifying current depth with each order's realized future lifetime
   uses the target interval. A valid real-time `D_h` must be estimated only on earlier dates and evaluated without
   refitting. The ex-post fleeting/static decomposition is a descriptive oracle, not a deployable predictor.
4. **Shock conditioning is endogenous.** Large depletions occur in unusual depth, imbalance, volatility and order-
   flow states. Event averages cannot establish that an age-composition gap causes a second depletion. Matching,
   overlap, non-overlapping shocks and day-level inference are mandatory.
5. **The current free sample cannot support the headline.** The five useful LOBSTER streams provide one trading
   day per AAPL, AMZN, GOOG and MSFT plus one SPY hour. Shock counts inside a day are not independent market/day
   replications, and a one-day stream cannot provide clean train/validation/test days for the survival model.

The exact gap could still support a specialist market-microstructure paper after a fresh multi-day, multi-venue
market-by-order data contract. It is not admitted as a Nature-level candidate on the present evidence.

## 4. Data and implementation boundary retained

The existing LOBSTER samples are technically sufficient for a future *development-only* reconstruction:

- submissions, partial cancellations, deletions and visible executions carry order identifiers, timestamps,
  prices, sizes and sides;
- an order's birth, remaining quantity, age, queue position and visible exit type can be tracked;
- start-of-window orders are left-censored and must not be assigned artificial births;
- hidden executions do not expose the same displayed-order lifecycle and must not be silently merged;
- a partial cancellation preserves the original birth time while changing remaining quantity;
- training, calibration and evaluation must be split by date, not by messages or randomly selected shocks.

A credible specialist confirmation would require at least two independent venue/asset families, enough dates to
fit hazards before evaluation, day or venue-day as the sampling unit, frozen horizons and shocks, competing-risk
calibration, raw/deeper depth, OFI, order-flow, cancellation-rate and queue-position baselines, and an untouched
replication period. Those requirements imply data expansion; more GPU compute cannot replace them.

## 5. Venue and resource decision

- **Nature Machine Intelligence:** `NO_SURVIVOR`. An age/lifecycle state lift, competing-risk model or
  survival-weighted sum is established survival/queueing machinery. No non-equivalent learning method, theorem or
  cross-domain guarantee remains.
- **Nature Computational Science:** `NO_SURVIVOR_SCOPE_AND_PRIOR_ART`. The narrow dynamic gap was not found
  verbatim, but its ingredients and mechanism neighbourhood are occupied, it has no fixed signed prediction, and
  the current data cannot provide independent confirmation.
- **Specialist route:** conditional. A prospectively trained age-structured hazard plus post-shock recovery and
  incremental-risk study could be useful for market microstructure or execution, provided it is framed as a new
  empirical measurement rather than first durable depth or first path-dependent queue model.
- **Compute:** no V9 experiment is justified. No V100, RTX2060, remote CPU, model API or GPU job was contacted or
  queued. A future order reconstruction is CPU/I/O dominated; GPUs become relevant only for a separately frozen
  neural survival baseline after adequate dates exist.

## 6. Binding closure and reopen condition

V9 stops before a plan freeze or experiment because the novelty/data admission gate failed. No target aggregate,
shock response, hazard estimate or predictive metric was opened. Previously inspected vendor schema and example
message rows are metadata/format checks and do not constitute a V9 result.

Do not reopen V9 by changing the age threshold, shock percentile, horizon, predictor or asset after seeing the
current samples. Re-entry requires all of:

1. a prospectively written claim distinct from path-dependent queue survival, fleeting/static depth and
   overshooting-liquidity prior work;
2. either a signed mechanism with a hard falsifier or a non-equivalent estimator/guarantee;
3. a multi-day development panel and an untouched independent market/venue replication contract;
4. a committed analysis plan before any target recovery or future-risk value is computed.

Until then, the order-lifecycle reconstruction specification is reusable infrastructure, not the main NMI/NCS
paper.
