# EcoMD Discovery Loop topic cycle 6: scaling-closure falsification audit

**Date:** 2026-08-26
**Scope:** simulated markets, market physics, and financial physics
**Stage:** D-2 theory-led falsification audit
**Literature cutoff:** 2026-08-26
**Outcome access:** none
**Decision:** passed-and-closed audit; zero topic cards and zero execution authorizations

## 1. Search question

Muhle-Karbe, Ouazzani Chahdi, Rosenbaum and Szymanski propose a 2026 order-flow model in
which one core-flow persistence parameter, `H0`, pins down four apparently separate market
regularities:

\[
H_{\mathrm{signed}}=H_0,\qquad
H_{\mathrm{volume}}=H_0-\tfrac12,\qquad
H_{\mathrm{volatility}}=2H_0-\tfrac32,\qquad
\beta_{\mathrm{impact}}=2-2H_0.
\]

This is a much better scientific starting point than another imported physics label: it is a
specific, recent and falsifiable closure claim. Cycle 6 asked whether EcoMD and independent
market simulators could turn the four equalities into a new joint stress test, and whether a
24/7 cryptocurrency market could remove the daily-break alternative to genuine long memory.

The answer is no under the currently available truth contracts. A same-unit joint test would
be useful, but the main theoretical relation is the direct 2026 claim, public trade tapes do
not identify real metaorders or the latent core/reaction assignment, and continuous trading
does not eliminate clock-phase regimes. The residual is an exacting replication or
falsification programme, not yet a new NCS/NMI-grade computational result.

## 2. What the anchor paper establishes

The anchor paper models core and reaction orders as coupled nearly unstable heavy-tailed
Hawkes processes. Its scaling limit yields mixed-fractional signed flow, rough unsigned
volume, rough volatility and power-law impact from one parameter. Its empirical section uses
trade-by-trade BMLL records for 40 large-cap stocks from 2021--2024 and estimates signed-flow
and unsigned-volume roughness. Volatility and impact consistency are then compared with
established empirical ranges; the paper does not report one prospectively frozen joint
four-residual test with tagged parent orders on the same units.

That gap is real but narrow. Jusselin and Rosenbaum already derive the impact--rough-volatility
link from no arbitrage. Sato and Kanazawa directly test the microscopic order-splitting account
and later document square-root impact across the Tokyo Stock Exchange. Maitrier and Bouchaud
jointly model order imbalance, impact and volatility, including a synthetic market generator.
Angstmann and Gebbie explicitly separate event-time sign memory from physical-time impact.

## 3. Four screened descendants

| Route | Proposed object | Decisive failure | Hostile T0 lower / point / upper |
|---|---|---|---:|
| Single-exponent closure residual | Jointly test all three residual equalities relative to `H0` on the same units and periods | Direct theory target; real impact residual needs tagged metaorders, and a positive fit does not identify the proposed mechanism | 5 / 12 / 24% |
| Core--reaction flow identification | Infer which trades are autonomous core flow and which are reactions from aggregate signed and unsigned trades | The labels are latent and non-unique without structural Hawkes assumptions or trader/metaorder identities; this is an observation-quotient problem | 1 / 4 / 9% |
| Sessionless crypto long-memory discriminator | Use 24/7 crypto to distinguish genuine order splitting from daily level shifts | Continuous trading still has hour, quarter-hour, funding, settlement and global-session periodicities; direct crypto periodicity work occupies the premise | 3 / 8 / 15% |
| Operational-clock closure | Test whether the exponent relations survive event, trade, volume and calendar time | Stochastic subordination can preserve event-time signs while changing calendar-time paths; the exact clock distinction is already explicit in 2026 prior work | 2 / 6 / 13% |

No conservative lower bound reaches the 15% activation floor.

## 4. Killer constructions

### 4.1 Same public tape, different parent-order truth

Take one sequence of signed child trades. In world A, every persistent run comes from one
institutional parent order. In world B, the identical sequence comes from conditionally
correlated but independent traders. All public trade-time statistics, returns and volume are
identical. Parent-order impact and the microscopic order-splitting explanation are different.
No estimator using only that tape can distinguish the worlds. This is exactly why public-data
metaorder reconstruction can generate qualitatively wrong impact trajectories.

### 4.2 Same aggregate flow, different core--reaction decomposition

Hold the joint law of aggregate signed and unsigned trades fixed. Reassign a persistent
component from autonomous core flow to common-information reaction flow and adjust the latent
intensities so their sum is unchanged. Aggregate Hurst and covariance statistics are fixed,
while the claimed causal meaning of `H0` changes. The decomposition becomes identified only
after imposing the structural model or observing trader/metaorder provenance; fitting the model
cannot independently validate that provenance.

### 4.3 Same event sequence, different physical clock

Keep the signed event sequence unchanged and attach either nearly constant durations or a
bursty heavy-tailed stochastic clock. Event-time sign memory is identical, while calendar-time
volume, volatility and impact paths can differ. A four-exponent equality mixing event and
physical time therefore needs an explicit clock theorem and a frozen estimator at each clock;
otherwise agreement can be created or removed by subordination.

### 4.4 Open-all-day but periodically resetting market

Let a venue trade continuously with no close, but schedule strategy refresh, funding,
settlement or execution batches at fixed quarter-hour boundaries. The flow has periodic level
and correlation changes despite 24/7 availability. Removing the equity close does not remove
the structural-break alternative. Recent cryptocurrency studies observe precisely such
within-hour and global-session periodicity.

## 5. Simulator and real-data contracts

- A reference Hawkes generator can reproduce the equalities because they are built into its
  kernel scaling. That is a theorem conformance fixture, not independent evidence.
- An agent-based LOB can manipulate parent-order length distributions and measure the four
  exponents, but the result is scientific only if the agents, matching engine and clock do not
  encode the target relation. ABIDES/PAMS/Bourse do not by themselves provide an external
  truth label for the core/reaction decomposition.
- Public crypto and equity trades can support signed-flow, volume and volatility estimators.
  They generally cannot support the same real-metaorder impact estimand. Naviglio et al. show
  why public-tape models misrepresent real metaorder paths.
- Donier and Bonart's historical Bitcoin dataset and Sato and Kanazawa's trader-resolved Tokyo
  data demonstrate what stronger provenance can achieve, but they are already analysed sources,
  not sealed prospective assets for this topic.

## 6. What remains reusable

1. The closure residual vector
   `(H_volume-H0+1/2, H_volatility-2H0+3/2, beta_impact+2H0-2)` is a strong falsifier once all
   components are measured on the same units with valid uncertainty.
2. Event time and physical time must be separate estimands; a stochastic clock is part of the
   mechanism rather than a harmless indexing choice.
3. A public trade tape does not identify metaorder impact or a core/reaction causal label.
4. A simulator that instantiates the Hawkes assumptions can verify implementation but cannot
   validate the assumptions that generated its own output.
5. A 24/7 venue removes the literal overnight closure, not periodic algorithm schedules,
   funding clocks, global-session effects or slow regime changes.
6. A decisive reopening asset would contain tagged parent orders or randomized known parent
   programmes, exact physical timestamps and a genuinely future confirmation period.

## 7. Decision

**Passed-and-closed theory-led audit; zero cards.** The strongest descendant has a 24% upper
bound because a rigorous four-way refutation could be scientifically useful, but its
conservative lower bound is only 5%. At present it is an underidentified replication of a
direct 2026 theory, not an activatable market-simulation topic. No sandbox, simulator run,
market-data download or purchase, EcoMD change, outreach or compute job is authorized.

Reopen only if two independent real-market lineages provide lawful tagged parent orders or an
equivalent randomized core-flow label, all four exponents can be estimated on the same frozen
units and clocks, the confirmation interval begins after the protocol freeze, and an independent
agent-based engine predicts the closure without imposing it through its generator or calibration
target. A revised novelty audit must then raise the hostile-T0 lower bound to at least 15%.

## 8. Primary-work manifest

1. Muhle-Karbe et al., *A unified theory of order flow, market impact, and volatility*: https://arxiv.org/abs/2601.23172
2. Jusselin and Rosenbaum, *No-arbitrage implies power-law market impact and rough volatility*: https://doi.org/10.1111/mafi.12254
3. Gatheral, Jaisson and Rosenbaum, *Volatility is rough*: https://doi.org/10.1080/14697688.2017.1393551
4. Bouchaud et al., *Fluctuations and response in financial markets*: https://doi.org/10.1088/1469-7688/4/2/007
5. Lillo and Farmer, *The long memory of the efficient market*: https://arxiv.org/abs/cond-mat/0311053
6. Sato and Kanazawa, *Inferring Microscopic Financial Information from the Long Memory in Market-Order Flow*: https://doi.org/10.1103/PhysRevLett.131.197401
7. Sato and Kanazawa, *Strict Universality of the Square-Root Law in Price Impact across Stocks*: https://doi.org/10.1103/65jz-81kv
8. Naviglio et al., *Why is the estimation of metaorder impact with public market data so challenging?*: https://arxiv.org/abs/2501.17096
9. Maitrier and Bouchaud, *The Subtle Interplay between Square-root Impact, Order Imbalance & Volatility*: https://arxiv.org/abs/2506.07711
10. Maitrier, Loeper and Bouchaud, *... II: An Artificial Market Generator*: https://arxiv.org/abs/2509.05065
11. Angstmann and Gebbie, *Revisiting Trade-sign Long-memory and Square-root Law price impact*: https://arxiv.org/abs/2606.16269
12. Axioglou and Skouras, *Markets change every day*: https://doi.org/10.1016/j.jempfin.2011.01.002
13. Gould, Porter and Howison, *The Long Memory of Order Flow in the Foreign Exchange Spot Market*: https://doi.org/10.1142/S2382626616500015
14. Donier and Bonart, *A Million Metaorder Analysis of Market Impact on the Bitcoin*: https://doi.org/10.1142/S2382626615500082
15. Hansen, Kim and Kimbrough, *Periodicity in Cryptocurrency Volatility and Liquidity*: https://doi.org/10.1093/jjfinec/nbac034
16. Kim and Hansen, *The Quarter-Hour Effect*: https://arxiv.org/abs/2607.09426
17. Filimonov and Sornette, *Apparent criticality and calibration issues in the Hawkes self-excited point process model*: https://doi.org/10.1080/14697688.2015.1032544
