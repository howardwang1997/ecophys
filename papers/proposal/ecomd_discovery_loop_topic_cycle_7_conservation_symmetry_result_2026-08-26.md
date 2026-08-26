# EcoMD Discovery Loop topic cycle 7: conservation and symmetry audit

**Date:** 2026-08-26
**Scope:** simulated markets, market physics, and financial physics
**Stage:** D-2 theorem-led reduction audit
**Literature cutoff:** 2026-08-26
**Outcome access:** none
**Decision:** passed-and-closed audit; zero topic cards and zero execution authorizations

## 1. Search question

Cycle 7 asked whether a market-native conservation law or exact symmetry could support a
nontrivial response theorem without relying on latent trader intent, parent-order labels, an
arbitrary clock, or an unobserved market state. The candidate had to satisfy four conditions:

1. the charge or group action is defined on the mechanism's complete state;
2. it is unchanged by economically equivalent account, order, lot, token-wrapper, and
   numeraire representations;
3. it forces a falsifiable response rather than merely restricting accounting reachability;
4. the same estimand exists in two independent engines and has a lawful prospective real-state
   bridge.

No screened formulation passed. Exact balances and symmetries are useful implementation
oracles, but their market dynamics still depend on transition rates, policies, margin state,
priority records, and admissible actions. The strongest residual, a reaction-channel
decomposition of perpetual-futures open interest, is exact bookkeeping rather than an
identified kinetic law.

## 2. General reduction

Write an event-driven market as

\[
x_{n+1}=x_n+\nu_{e_n}, \qquad B\nu_e=0,
\]

where each column \(\nu_e\) is the state increment of one admissible transaction and the rows
of \(B\) are conserved charges. This is the standard left-nullspace construction for a
stoichiometric or Petri-net incidence matrix. It fixes the affine compatibility class
\(Bx=Bx_0\), but it does not fix the event rates \(\lambda_e(x)\), the matching priority, or a
price observable \(p(x)\). Two generators can therefore share exactly the same \(B\) and
\(\nu\) while having opposite intervention responses.

The representation is also not automatically economic. A direct transfer `A -> B` and an
equivalent `A -> escrow -> B` settlement have different intermediate species and incidence
matrices. Splitting one economic account into two protocol accounts can change the raw
nullspace basis while preserving aggregate wealth and every external payoff. A publishable
charge must descend to that economic quotient; counting null vectors or conserved ledgers
does not do so.

## 3. Screened descendants

| Route | Proposed object | Decisive failure | Hostile T0 lower / point / upper |
|---|---|---|---:|
| Transaction-stoichiometric market charge | Derive conserved cash, asset, escrow, fee, and position charges from the event-incidence matrix and use them to predict response modes | Left-nullspace conservation is generic reaction-network/Petri-net algebra; rates and prices remain free, and the raw charge basis changes under account and settlement refinement | 1 / 3 / 7% |
| Open-interest reaction-channel response | Label each perpetual trade as position creation, annihilation, or transfer and predict subsequent liquidation or price response | The channel is a deterministic decomposition of signed positions; identical volume and open-interest change permit opposite margin risk, while full augmentation returns ordinary stateful liquidation dynamics | 4 / 9 / 16% |
| Self-trade-prevention identity response | Treat the STP identity partition as a symmetry-breaking field and measure cancellation cascades | Changing the identity partition changes the mechanism, beneficial ownership is not protocol invariant, wallet/account splitting defeats the proposed quotient, and direct STP market-design work already studies price instability | 2 / 6 / 12% |
| Conservation-constrained cross-impact reciprocity | Infer symmetric or low-rank cross-impact response from cash and inventory conservation | Exact settlement permits arbitrary asymmetric price maps; reciprocity follows only under no-dynamic-arbitrage and impact-kernel assumptions already treated in the literature | 1 / 4 / 9% |
| L2 order-identity lumpability taxonomy | Characterize when market-by-order dynamics project exactly to a Markov market-by-price process | The necessary and sufficient condition is classical strong lumpability; FIFO age, owner, and cancellation state give immediate counterexamples, while queue-reactive Markovity is an imposed model restriction | 3 / 7 / 14% |
| CFMM invariant-curvature response | Use a trading invariant and its curvature as a coordinate-free response law | CFMM geometry, scaling axioms, curvature, price sensitivity, composition, and path independence are direct prior art | 0 / 2 / 5% |

No conservative lower bound reaches the 15% activation floor.

Bid--ask reflection was screened but not registered as another graph node. If the complete
generator and initial law are reflection-equivariant, the mirrored path law is an immediate
group-action identity. If policies, short constraints, news, fees, or the reference price break
the action, no identity follows. Empirical bid--ask symmetry and approximate-equivariant RL are
already established, and the formulation duplicates the closed
`market_automorphism_defect_certificate` route.

## 4. Killer constructions

### 4.1 Same conservation law, opposite response

Consider two agents with one unit of stock and fixed total cash. Both engines settle every
trade by transferring stock from seller to buyer and cash from buyer to seller, so they have
identical conserved totals. Engine A raises its quote after a buy; engine B lowers it because a
designated liquidity supplier mean-reverts the quote. Conservation holds pathwise in both.
It places no sign restriction on price response.

### 4.2 Same trade volume and open-interest change, opposite liquidation risk

Let signed positions satisfy \(\sum_i z_i=0\) and define

\[
\mathrm{OI}(z)=\frac12\sum_i |z_i|.
\]

A bilateral trade of size \(q\) changes OI by an amount in \([-q,q]\): two opening legs create
OI, two closing legs annihilate it, and a position transfer leaves it unchanged. This identity
is exact. Now place the newly opened long and short in two accounts one tick from maintenance
in world A and in deeply collateralized accounts in world B. The trade, price, volume, and
\(\Delta\mathrm{OI}\) are identical, but the same oracle move liquidates A and not B. Adding the
full collateral, account concentration, oracle, book, and liquidation grammar removes the
ambiguity but also removes the proposed low-dimensional law.

### 4.3 Same economic owner, different STP partition

One trader posts a sell order and then submits a crossing buy. With both orders under one STP
identifier, `cancel-provide` removes the resting sell before matching. Split the same balances
and controller across two protocol identifiers and the orders trade. The external economic
owner and intended messages are unchanged, but the path changes because the protocol partition
changed. Public identifiers therefore do not define an owner-invariant physical charge.

### 4.4 Same L2 book, different next-state law

Take two unit orders at one price. Microstate A has ordered queue `[old_owner_1,
new_owner_2]`; microstate B reverses the ages or owners. Both project to L2 depth two. If old
orders cancel faster, owners have different reactive policies, or a targeted cancel arrives,
the total transition rate from depth two to depth one differs. For a projection \(\pi\) to be
strongly lumpable, every pair \(x,x'\) in the same L2 cell must satisfy

\[
\sum_{y:\pi(y)=z}Q(x,y)=\sum_{y:\pi(y)=z}Q(x',y)
\]

for every aggregate cell \(z\). This is the classical criterion, not a new market theorem.
Assuming rates depend only on aggregate queue sizes makes the criterion hold by construction
and yields the established queue-reactive model.

### 4.5 Same balances, asymmetric cross-impact

Two multi-asset engines can settle identical quantity transfers while using response matrices
\(G\) and \(G'\), one symmetric and one asymmetric. Cash and inventory conservation hold in
both because those constraints act on transfers, not on the quote-update map. Symmetry of
cross-impact can follow from a declared transient-impact model plus no dynamic arbitrage, but
that is the established Schneider--Lillo/Gatheral line, not a Noether consequence of settlement.

## 5. Simulator and real-state contracts

- Phoenix exposes explicit `Abort`, `CancelProvide`, and `DecrementTake` self-trade behaviours
  in an MIT-licensed on-chain FIFO engine. That makes a clean conformance fixture, but the
  on-chain trader key is not beneficial ownership and other venues expose different STP
  partitions and actions.
- Drift provides an Apache-2.0 on-chain perpetual implementation and account/position state.
  It can compute the OI identity exactly. A second perpetual engine would still have different
  margin, AMM/DLOB, oracle, funding, and liquidation semantics, so the proposed response is not
  yet one cross-engine estimand.
- CME MBO publishes anonymous OrderID and PriorityID while MBP aggregates quantity and order
  count. It is an excellent witness that L2 deletes state, but historical MBO is commercial and
  contains no owner identity; it does not create a controlled rule intervention.
- On-chain CFMM reserve and swap state is complete enough to verify invariant and rounding
  identities. The candidate fails because the corresponding geometry and curvature response
  theory are already direct prior art, not because the state is hidden.
- ABIDES, PAMS, and Bourse can enforce ledger balances or emit aggregate books, but none turns a
  conserved quantity into the missing response law. Agreement after imposing the same rate or
  symmetry restriction would be theorem conformance rather than independent discovery.

No simulator, real-data, or disposable-sandbox action has positive decision value before a
nontrivial theorem survives these reductions.

## 6. Reusable results

1. Every proposed market conservation law must be audited under account splitting, order
   splitting, settlement intermediaries, token wrappers, lot refinement, and numeraire change.
2. A conserved left-nullspace restricts reachability but does not determine rates, prices,
   committors, impact, or relaxation.
3. Open-interest creation, annihilation, and transfer are exact event labels only when the full
   signed account positions are available. They are diagnostics, not sufficient state for
   liquidation or price response.
4. A symmetry theorem must state the action on the complete state, intervention, policy,
   randomness, and observable. Symmetry of a matching kernel alone does not symmetrize an
   asymmetric environment.
5. L2 Markov sufficiency is a strong-lumpability question. MBO-to-MBP information loss should be
   tested with the classical rate-to-cell criterion before proposing a coarse market physics.
6. Cross-impact reciprocity is a no-arbitrage/model restriction, not a consequence of cash and
   inventory conservation.

## 7. Decision

**Passed-and-closed theorem-led audit; zero cards.** The only route with an upper bound above
15% is the open-interest reaction-channel formulation, but its conservative lower bound is 4%.
Its exact component is a bookkeeping identity and its dynamic component is underidentified
without the full margin and policy state. The other formulations are direct applications of
reaction-network conservation, Markov lumpability, no-dynamic-arbitrage, equivariance testing,
or CFMM geometry.

Reopen only if a candidate supplies a representation-invariant charge or symmetry, proves a
market-specific response theorem that is not inherited from those parent classes, survives two
complete-state killer twins, compiles to the same native estimand in two independent engines,
and has a prospectively frozen full-state field bridge or orthogonal rule intervention. A new
hostile audit must put the conservative T0 lower bound at or above 15%. No sandbox, simulator
run, market-data action, outreach, EcoMD change, or compute job is authorized by this cycle.

## 8. Primary-work and official-semantics manifest

1. Mahdi et al., *Conservation Laws in Biochemical Reaction Networks*: https://doi.org/10.1137/17M1138418
2. Avanzini, Freitas and Esposito, *Geometry of Nonequilibrium Reaction Networks*: https://doi.org/10.1103/PhysRevX.13.021040
3. Cont, Degond and Xuan, *A Mathematical Framework for Modeling Order Book Dynamics*: https://doi.org/10.1137/22M1541538
4. Carrasquel and Lomazova, *Searching for Deviations in Trading Systems*: https://arxiv.org/abs/2210.16800
5. Buchholz, *Exact and Ordinary Lumpability in Finite Markov Chains*: https://doi.org/10.2307/3215235
6. Derisavi, Hermanns and Sanders, *Optimal State-Space Lumping in Markov Chains*: https://doi.org/10.1016/S0020-0190(03)00343-0
7. Huang, Lehalle and Rosenbaum, *Simulating and Analyzing Order Book Data: The Queue-Reactive Model*: https://doi.org/10.1080/01621459.2014.982278
8. Cont et al., *Analysis and Modeling of Client Order Flow in Limit Order Markets*: https://doi.org/10.1080/14697688.2022.2150282
9. CME Group, *Market by Order FAQ*: https://www.cmegroup.com/articles/faqs/market-by-order-mbo.html
10. Hedvall, Niemeyer and Rosenqvist, *Do Buyers and Sellers Behave Similarly in a Limit Order Book?*: https://doi.org/10.1016/S0927-5398(97)00011-X
11. Morariu-Patrichi and Pakkanen, *State-Dependent Hawkes Processes and Their Application to Limit Order Book Modelling*: https://doi.org/10.1080/14697688.2021.1983199
12. Gatheral, *No-Dynamic-Arbitrage and Market Impact*: https://doi.org/10.1080/14697680903373692
13. Schneider and Lillo, *Cross-Impact and No-Dynamic-Arbitrage*: https://doi.org/10.1080/14697688.2018.1467033
14. Giagkiozis and Said, *Reconciling Open Interest with Traded Volume in Perpetual Swaps*: https://doi.org/10.5195/LEDGER.2024.325
15. Chen et al., *Exploring the Impact: How Decentralized Exchange Designs Shape Traders' Behavior on Perpetual Future Contracts*: https://arxiv.org/abs/2402.03953
16. Bohl et al., *Volatility, Trading Volume and Open Interest in Futures Markets*: https://doi.org/10.1108/IJMF-04-2015-0071
17. Wan, *Forced or Frantic? Deleveraging Cascades and Price Dislocation on a Transparent Perpetual-Futures Venue* (working paper and replication): https://github.com/edwinyeeshunwan/forced-or-frantic
18. Trossi, *Market Manipulation and the Design of Self-Trade Prevention Tools*: https://pedrotrossi.github.io/JMP/trossi_jmp_manipulation.pdf
19. Phoenix FIFO self-trade implementation: https://docs.rs/phoenix-common/latest/src/phoenix/state/markets/fifo.rs.html
20. FIA, *Guide to the Development and Operation of Automated Trading Systems*: https://www.fia.org/sites/default/files/2019-09/FIA-Guide-to-the-Development-and-Operation-of-Automated-Trading-Systems_1.pdf
21. Angeris et al., *The Geometry of Constant Function Market Makers*: https://arxiv.org/abs/2308.08066
22. Schlegel, Kwaśnicki and Mamageishvili, *Axioms for Constant Function Market Makers*: https://arxiv.org/abs/2210.00048
23. Angeris, Evans and Chitra, *When Does the Tail Wag the Dog? Curvature and Market Making*: https://doi.org/10.21428/58320208.e9e6b7ce
24. Ramseyer et al., *Augmenting Batch Exchanges with Constant Function Market Makers*: https://doi.org/10.1145/3670865.3673569
