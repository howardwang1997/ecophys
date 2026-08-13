# Prediction-market coherence dynamics — V10 novelty and data audit

**Audit date:** 2026-08-13
**Branch:** `prediction-market-coherence-audit-v10`
**Final decision:** `V10_NO_SURVIVOR_NONINTRINSIC_AND_PRIOR_ART`
**Candidate state:** `RETIRED_IDENTIFIABILITY`
**Outcome access:** no market catalog row, live price, book event, trade, inconsistency episode or fitted response was opened

## 1. Candidate that was attacked

The candidate moved outside EcoMD to a real computational market. Let `p(t) in [0,1]^d` collect executable
probability-like prices for logically related contracts and let the exactly known payoff logic impose

\[
\mathcal C=\{p:Ap=b\}.
\]

For a weighted executable-price metric `W`, define the coherent projection and normal inconsistency

\[
p^{\mathcal C}=\arg\min_{q\in\mathcal C}\lVert p-q\rVert_W^2,
\qquad
r=p-p^{\mathcal C}.
\]

The proposed empirical phenomenon was that after an information shock the logical-normal component `r(t)` would
relax in a topology-dependent modal order, while the tangent component of price change would represent coherent
belief revision. A Nature Machine Intelligence route would have required a new theorem or learning method for
this decomposition; a Nature Computational Science route would have required a prospectively signed recovery law
replicated across independently administered prediction-market mechanisms.

The candidate is about actual market coherence, not simulator error. It nevertheless fails both the mathematical
object and executable-data admission gates below.

## 2. Exact mathematical reduction and counterexample

### 2.1 Global projection has no nontrivial relaxation spectrum

If the mechanism applies the full projection `p -> p^C`, then `r` is eliminated in one update. There is no
multi-mode recovery law to estimate from the constraint topology.

### 2.2 Local row corrections are randomized Kaczmarz

If one normalized row `a_i^T p=b_i` is selected with probability `pi_i` and corrected exactly,

\[
p^+=p-\frac{a_i^Tp-b_i}{\lVert a_i\rVert_2^2}a_i,
\]

then this is the Kaczmarz projection step. Its expected error contraction is governed by the standard weighted
row Gram operator

\[
K=\sum_i\pi_i\frac{a_i a_i^T}{\lVert a_i\rVert_2^2},
\]

with the usual condition-number/smallest-positive-eigenvalue dependence. Block constraints give block Kaczmarz or
alternating convex projections. Calling the operator a logical Laplacian does not produce a non-equivalent theorem.

### 2.3 The proposed spectrum is not intrinsic to the coherent set

Equivalent equation systems can define exactly the same `C` while changing the row-selection dynamics and its
spectrum. For `C={0}` in two dimensions, take `A=I_2` with uniform row selection. Then `K=I_2/2`. The invertible
row recombination

\[
A'=\begin{bmatrix}1&0\\1&1\end{bmatrix}
\]

defines the same `C`, but its two normalized row projectors give

\[
K'=\begin{bmatrix}3/4&1/4\\1/4&1/4\end{bmatrix},
\qquad
\lambda(K')=\left\{\frac{1+1/\sqrt2}{2},\frac{1-1/\sqrt2}{2}\right\},
\]

instead of `{1/2,1/2}`. More generally `A` and `RA` define the same affine set for invertible `R`, while local
projection operators and their eigenvalues need not agree. Thus a constraint-graph spectral rate is not an
invariant of market logic unless the actual atomic arbitrage operations and their arrival intensities are
independently fixed.

Once those operations are fixed, the empirical generator depends on liquidity, spreads, fees, latency, capital,
priority and heterogeneous trader arrival rates. It is a market-microstructure object, not a topology-only law.

## 3. Direct prior-art map

| Neighbourhood | Direct result | Consequence for V10 |
|---|---|---|
| logically related price misalignment | Rothschild and Pennock, [*The Extent of Price Misalignment in Prediction Markets*](https://researchdmr.com/files/PriceMisalignment.pdf), document same- and cross-exchange inconsistencies, persistent cross-exchange lags, secondary-contract illiquidity under high information flow and a randomized field trial revealing a shadow order book | The substantive phenomenon—news-linked failure of logical propagation and observed-book undermeasurement—is already direct empirical prior art. |
| current Polymarket arbitrage | Saguillo et al., [*Unravelling the Probabilistic Forest*](https://arxiv.org/abs/2508.03474), identify market-rebalancing and combinatorial arbitrage using temporal, topical and logical relationship matching | Cross-contract logical graph construction and realized arbitrage on Polymarket are occupied. |
| high-frequency duration and depth | Cheng, Yang and Zou, [*Arbitrage Analysis in Polymarket NBA Markets*](https://arxiv.org/abs/2605.00864), reconstruct more than 75 million book snapshots and measure frequency, duration, profitability and executable depth | Seconds-scale recovery duration and liquidity-limited executable inconsistency are already direct measured targets. |
| coherent price projection | Kroer et al., [*Arbitrage-Free Combinatorial Market Making via Integer Programming*](https://arxiv.org/abs/1606.02825), implement Bregman projection onto an arbitrage-free combinatorial price set via Frank--Wolfe and an integer-program oracle | Projection onto a coherent price set is established market-design machinery. |
| information propagation by constraints | Dudik, Lahaie and Pennock, [*A Tractable Combinatorial Market Maker Using Constraint Generation*](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/DudikLaPe12.pdf), use convex optimization and constraint generation to propagate information among related securities | Constraint-driven logical information propagation is not a new computational objective. |
| arbitrary-set-system geometry | Hossain, Wang and Yu, [*Designing Automated Market Makers for Combinatorial Securities: A Geometric Viewpoint*](https://arxiv.org/abs/2411.08972), characterize price-query/update complexity through set-system geometry | Logical topology and efficient combinatorial market design already have a modern geometric treatment. |
| local projection rate | Strohmer and Vershynin, [*A Randomized Kaczmarz Algorithm with Exponential Convergence*](https://arxiv.org/abs/math/0702226), give the exponential expected convergence rate for random row projections | The proposed spectral relaxation theorem is a direct Kaczmarz specialization once local row corrections are assumed. |
| forecast coherence | [*Arbitrage-Free Forecasts from Language Models via Coherence Projection*](https://openreview.net/pdf?id=Tqos7VqQhH) projects forecasts onto logical coherence polytopes, including partition simplexes and Frechet constraints | An NMI route based on learning then coherence projection is also directly occupied. |

The decision-relevant pages of Rothschild--Pennock were rendered and visually inspected. The paper explicitly
attributes within-exchange misalignment to inability to update related contracts concurrently during rapid
information flow, reports lagged cross-exchange propagation, and warns that quoted-book snapshots miss shadow
liquidity. Those are not abstract analogies to V10; they are the proposed empirical neighborhood.

## 4. Platform and data audit

Polymarket's official [negative-risk documentation](https://docs.polymarket.com/concepts/negative-risk) supplies a
precise `negRisk` flag and an atomic conversion for one mutually exclusive multi-outcome event. Its public
[real-time market feed](https://docs.polymarket.com/market-data/realtime-data) can stream books, price changes and
trades without a trading action. This is useful for prospective data collection, but one complete event supplies
only the simplex constraint `sum_i p_i=1`: one independent equality and therefore one normal mode. A nontrivial
constraint spectrum requires cross-event implication, nesting or equivalence edges that are not certified by the
flag. Augmented negative-risk events also change the meaning of placeholders and “Other” as outcomes are named.

Kalshi's official [multivariate-event endpoint](https://docs.kalshi.com/api-reference/events/get-multivariate-events)
exposes market collections and a `mutually_exclusive` field, while its order-book WebSocket has matching-engine
timestamps. The full WebSocket handshake requires an account API key. More importantly, the multivariate metadata
does not itself provide a complete, versioned cross-contract payoff-logic graph comparable with an audited
constraint matrix `A`.

Therefore the free exact-mechanism graph is either:

1. **certified but rank-one per event**, so the headline topology spectrum is degenerate; or
2. **nontrivial but semantic/manual**, so contract equivalence, implication and resolution-rule drift become a
   measurement model whose errors can create or erase the target inconsistency.

Saguillo et al. already use timeliness, topical similarity, combinatorial relationships and expert validation for
the second route. Building a new semantic matcher would be an engineering extension, not a sealed physical law.

## 5. Venue and resource decision

- **Nature Machine Intelligence:** `NO_SURVIVOR`. Coherence projection, convex constraint generation and local
  projection convergence are established. The proposed spectral theorem is not invariant to an equivalent
  constraint representation and reduces to Kaczmarz after an operation basis is chosen.
- **Nature Computational Science:** `NO_SURVIVOR_NONINTRINSIC_AND_PRIOR_ART`. Information-flow-linked logical
  misalignment, lags, executable duration and liquidity limits are already measured. The only sharper spectral law
  lacks a certified nontrivial graph and is not topology-intrinsic.
- **Specialist route:** a prospective Polymarket/Kalshi market-microstructure replication could still measure
  executable coherence, but it would need versioned payoff equivalence, full fee/depth accounting, semantic-match
  error bounds, news timestamps and independent events. It should be framed as a modern replication or platform
  comparison, not first logical propagation or a universal spectral law.
- **Compute/data:** no collector, API credential, market catalog, WebSocket, outcome, local experiment, remote host
  or GPU job was opened. The two V100s and RTX2060 remain uncontacted and unqueued. A future collector would be
  CPU/network/storage dominated; GPU scale cannot repair a non-intrinsic quantity or missing certified graph.

## 6. Binding closure and reopen condition

V10 stops before a plan freeze or feasibility run. Do not reopen it by choosing a different graph normalization,
projection metric, news detector, semantic embedding, event category or platform after seeing prices.

Re-entry requires all of:

1. an operation-basis-invariant quantity or theorem demonstrably outside coherent projection, Kaczmarz and
   combinatorial-market-making results;
2. a platform-certified, versioned, rank-at-least-two logical constraint system rather than semantic similarity;
3. a signed prediction that separates topology from spreads, fees, liquidity, latency and arbitrageur arrival;
4. a prospectively collected development period and untouched independently administered replication fixed before
   any inconsistency or recovery outcome is computed.

Until then, prediction-market feeds remain an interesting future data opportunity, not the main NMI/NCS paper.
