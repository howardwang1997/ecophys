# Post-discovery-loop simulated-market reselection

**Date:** 2026-08-25
**Stage:** D-3 to D-1, outcome blind
**Decision:** no newly screened route qualifies for a topic card or active work

## 1. Scope and decision rule

This rerun used the repository's discovery protocol after the generic transportable-law
card failed. It searched two information sources that were underrepresented in earlier
rounds:

1. controlled human--algorithm experimental markets, where treatment assignment and the
   complete market state could in principle be observed; and
2. on-chain markets, where protocol state and rule changes are public and replayable.

A final computational-science residual asked whether observationally realistic limit-order
book generators could be benchmarked on active interventional fidelity. No market outcomes,
simulator runs, model implementation, participant recruitment, data purchase, API model
calls, EcoMD changes or GPU work were used. The activation rule remained a conservative
hostile-T0 lower bound of at least 15%, no unresolved direct prior, two native simulator
lineages implementing the same estimand, and a qualified real-data bridge.

| Frozen formulation | Hostile T0 | Complete Nature-level route | Decision |
|---|---:|---:|---|
| randomized human-to-automation control handoff | 6--17% (10% point) | 1--4% | failed-closed |
| Solana staged slot-time compression | 12--17% (lower bound 12%) | 3--6% | failed-closed under the bundled formulation |
| shared-oracle liquidation dephasing | 4--8% | 1--3% | failed-closed |
| generalized AMM block-time response | below 5% | below 1% | failed-closed |
| AI-scientist hidden-law benchmark in simulated markets | 3--8% | 1--3% | failed-closed |
| interventional-fidelity benchmark for LOB generators | 4--10% | 1--3% | failed-closed |

The ranges are probabilities that the frozen formulation survives the next scientific gate,
not probabilities that a chosen empirical sign will be obtained. No formulation has a lower
bound at or above 15%; therefore this rerun creates no topic card.

## 2. Controlled human--algorithm markets

### 2.1 Strongest formulation

The strongest controlled-market question randomized one or two participant accounts at
predeclared event times from human to a frozen finite-state trading controller. With a full
LOB, inventory, controller state and RNG log, it would estimate both peer handoff response

\[
\Psi(\tau)=\sum_{j\ne i}\{P[m_j(e+\tau)=A\mid Z_{i,e}=1]
-P[m_j(e+\tau)=A\mid Z_{i,e}=0]\}
\]

and the non-additive two-account contrast

\[
\Gamma_Y(\tau)=E[Y_\tau\mid11]-E[Y_\tau\mid10]
-E[Y_\tau\mid01]+E[Y_\tau\mid00].
\]

The intended market-physics claim was that two local control handoffs cause a super-additive
withdrawal of depth and persistent peer handoffs after conditioning on the pre-event market
state.

### 2.2 Why it failed

[Asparouhova et al. (2024)](https://academic.oup.com/rof/article/28/4/1215/7630167)
already let experimental traders deploy, stop and replace trading robots, retained robot
logs, and studied the associated high-volatility and flash-event behavior. The remaining
micro-randomization is a stronger identification design, but it does not create a new
physical object beyond standard dynamic treatment and interference analysis.

Two exact counterexamples are decisive.

1. If the controller identity is not disclosed and the human and controller emit the same
   order/cancel path, the exchange and every peer observe identical histories. A latent
   `human`/`automation` label has no independent market channel.
2. Independent agents with a common spread, volatility or inventory stop threshold can
   generate synchronized withdrawal, positive \(\Gamma_Y\), and long recovery without
   social contagion or peer control handoff.

If automation is disclosed, the estimand instead becomes an announcement/belief treatment,
already separated from the action channel in hybrid-market experiments. A credible two-site
human experiment would also require roughly USD 35--45k in participant/platform cost before
development, ethics review and staffing, while the real-market bridge cannot observe armed
but inactive controllers or human override decisions. The value of information is therefore
negative at the Nature target.

## 3. On-chain clocks and shared oracles

### 3.1 Generalized block time is occupied

A random or staged block clock initially appeared to provide a native free-flight/collision
time. That broad question is directly occupied by
[Nezlobin and Tassy (2025)](https://arxiv.org/abs/2505.05113), which treats generalized
inter-block distributions for AMM loss-versus-rebalancing and establishes a universal
arbitrage-trade limit and the asymptotic optimality of constant spacing. Empirical AMM
arbitrage losses under different block times are also already measured by
[Fritsch and Canidio (2024)](https://arxiv.org/abs/2404.05803).

### 3.2 Solana SIMD-0525 does not isolate a clock

[SIMD-0525](https://github.com/solana-foundation/solana-improvement-documents/blob/main/proposals/0525-reduce-slot-times.md)
proposes feature-gated reductions from 400 ms to 350, 300, 250 and 200 ms. It is a strong
prospective repeated transition, but the treatment is a bundle: wall-clock slot duration,
the four-slot leader-window duration, per-slot compute/write/allocation/shred limits,
epoch wall time, annualized accounting and validator-admission payments change together.
The official document explicitly makes these changes to preserve per-second budgets and
protocol safety. Consequently a price-response change cannot be assigned to collision-clock
compression alone.

The two-runtime replication story is also incomplete. Agave and full Firedancer are
independently implemented execution clients, but they implement one consensus protocol and
do not by themselves create a second market mechanism. Cross-stage Bank-state conformance,
exact historical market-state export, and derived-data rights would have to be frozen before
a same-estimand claim. The formulation's 12--17% hostile T0 interval has a 12% lower bound
and therefore does not clear the activation floor. A future child would need a preregistered
factorial separation of slot granularity, leader-window duration, and per-second capacity,
not a regression that labels the whole bundle `slot-time`.

### 3.3 Oracle dephasing reduces to a familiar frontier

The oracle formulation held the external price path and terminal update fixed while
staggering when lending or perpetual protocols consume the update. Small dephasing can
split one threshold-crossing liquidation batch and reduce peak convex DEX impact or finite
blockspace demand. Larger lag creates stale-price exposure, bad debt and oracle-extractable
value. Under a convex impact function, the first effect is load smoothing; the second is a
delay-risk penalty. Their trade-off is not a new many-body law.

The direct empirical neighbors are unusually close. The
[BIS systemic-fragility study](https://www.bis.org/publ/work1062.pdf) already follows the
liquidation--DEX-price-impact--oracle feedback across Aave and Compound. The 2026
[Signals and Spoils](https://arxiv.org/abs/2606.03434) study maps independent Chainlink
DON timing across chains to predictable speculative liquidation and OEV windows. On-chain
borrower state, executed liquidations and DEX state are observable, but omitted/non-included
liquidator orders, private bundles, cross-venue inventory and the off-chain oracle input are
not. Observed phase differences are not randomized.

Two minimal worlds close the broad claim: with an external oracle and infinite DEX depth,
dephasing changes only the timing label; with a convex AMM and fixed liquidation quantities,
the peak reduction follows Jensen/load-splitting without a collective cascade. Endogenous
feedback requires a DEX-derived oracle and strategic liquidators, precisely the hidden-input
regime that loses the proposed complete-state advantage.

## 4. AI-scientist and simulator-fidelity residuals

### 4.1 A hidden market-parameter benchmark is already built

A benchmark in which an AI scientist proposes experiments in a simulated market, identifies
a hidden parameter and is scored for causal isolation would duplicate
[petri-bench](https://www.petri-labs.org/bench/report). Petri-bench already contains a
heterogeneous-agent asset market, procedurally fresh hidden changes, budgeted controlled
experiments, effect sizes, multiplicity correction, process-integrity auditing and objective
scoring. [DiscoverPhysics](https://sampsonml.github.io/DiscoverPhysicsLeaderboard/) and
[NewtonBench](https://arxiv.org/abs/2510.07172) already cover interactive hidden-law
discovery in modified physical worlds.

The possible descendants--persistent adaptive participants, multiple mechanisms, or a
law-or-counterexample verdict--are each compositions with dual control, performative
prediction, multi-environment transportability or the already closed proof-carrying
transportable-law route. A market-specific skin does not supply a new evaluation construct.

### 4.2 Interventional LOB fidelity has no qualified target counterfactual

[LOB-Bench](https://arxiv.org/abs/2502.09172) already evaluates generated message-level
LOBs using conditional statistics and event-response/market-impact metrics. A stronger
active-intervention benchmark would be scientifically useful only if a real target response
were observed. Historical L2/L3 records show the realized response to endogenous orders;
they do not reveal the counterfactual response to a forced order placed in the same state.
Matching cannot remove selection on private information, latency, queue position and
unobserved cross-venue state.

The generic method is also occupied: [Dyer et al. (2024)](https://proceedings.neurips.cc/paper_files/paper/2024/hash/26b8e3dc3a21fcd660d80c63b767f324-Abstract-Conference.html)
formalize interventionally consistent surrogates for complex agent-based simulators. ABIDES
and PAMS fail the stricter native same-estimand clock/RNG contract recorded in the preceding
D-1 audit. A laboratory target would replace the missing field counterfactual but would no
longer validate a real financial LOB, and would inherit the cost and external-validity limits
above.

## 5. Decision and reusable information

This search produced no active or candidate Nature-grade route. It does not show that the
phenomena are absent; it shows that the frozen claims lack irreducible novelty,
identification, same-estimand replication or a real bridge.

Reusable information is retained:

- hybrid-market controller identity has no channel beyond actions or disclosure;
- generalized block-time AMM response is a closed direct-prior family;
- SIMD-0525 is a prospective bundled market-structure transition, not a scalar clock shock;
- oracle phase diversity trades convex load smoothing against stale-price/OEV risk;
- petri-bench directly blocks a hidden-parameter market-science benchmark;
- observational LOB realism does not validate active counterfactual response.

The finite-noise liquidity-nucleus route was also rechecked for a unitization-invariant
descendant. Price-level share volume is invariant to splitting an order identifier, but
under anonymous replay its entire depletion response is already the cumulative-depth or
virtual-impact curve. Under native adaptive agents, cancel and modify actions depend on
order identity, age and strategy state, so the price-level quotient does not define an
autonomous intervention kernel. Adding nearest-neighbour withdrawal or replenishment
coupling would impose contact-process physics rather than discover it in a native CDA.
This closes the proposed descendant at 1--3% hostile T0 and creates no new card.

The only permitted next step is another D-3 question-generation round from a genuinely new
market-native contradiction. It must not implement any formulation above or relax the 15%
floor. The existing FCC candidate, DCRDEX parked route and separate verification-liquidity
protocol retain their prior statuses; this audit neither promotes nor reopens them.
