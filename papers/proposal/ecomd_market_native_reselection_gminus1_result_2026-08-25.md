# EcoMD market-native problem reselection: G-1 result

**Frozen:** 2026-08-25
**Scope:** simulated markets, mechanism-native market physics, financial physics, and a real-state bridge
**Outcome access:** none
**Decision:** no qualifying route; all five finalists failed before simulation

## 1. Decision

This screen changed the search rule. A candidate had to begin with a market-native state variable or admissible
operation--pending messages, occupied price cells, capital-preserving actor refinement, concentrated-liquidity
positions, or initialized-tick crossing--rather than import a named phenomenon from another branch of physics.
It then had to survive four gates:

1. the proposed physical object is invariant to arbitrary units, labels, clocks and equivalent protocol actions;
2. the central theorem is not an instance of branching, lumpability, queue first-passage, fixed-charge control,
   convex optimization or another mature parent problem;
3. two independently maintained mechanisms expose the state and intervention needed to test the same estimand;
4. the hostile probability of surviving T0 is at least 15% before outcomes, implementation or compute.

No finalist passed. In particular, the two last paper-only candidates failed exact reductions on the same day.
No simulator, dataset outcome, EcoMD model, purchased data or GPU was used.

| Finalist | Irreducible claim tested | Hostile T0 | Complete NCS | Decision |
|---|---|---:|---:|---|
| capital-preserving actor refinement | agent number as a physical system-size axis | 4% | 0.5% | failed-closed |
| CLMM range-coupled burn robustness | position decomposition changes the withdrawal action set | 2--5% | below 1--2% | failed-closed |
| initialized-tick pinning | liquidity jump and crossing cost create depinning/hysteresis | 10--14% | 1--3% | failed-closed |
| in-flight liquidity phase space | pending orders form a ballistic pre-collision reservoir | about 3% | below 1% | failed-closed |
| empty-tick void split--merge kinetics | void geometry controls depletion and price jumps | 4--8% | 1--2% | failed-closed |

These are planning probabilities, not empirical posterior estimates.

## 2. Capital-preserving actor refinement

The scientific question was whether simulator particle count can be made physical. Split an actor of capital
\(c\) into independent clones with \(c_1+\cdots+c_k=c\), split every extensive state in the same proportions,
hold intensive policy parameters fixed, and forget clone labels after the run. Exact invariance of the conditional
order random measure requires

\[
\mu^h_{c_1+\cdots+c_k}
=\mu^h_{c_1}*\cdots*\mu^h_{c_k}.
\]

Weak continuity in \(c\) makes \(\{\mu_c^h\}\) a convolution semigroup, with Laplace functional

\[
\mathbb E[\exp(-\langle f,N_c\rangle)\mid H=h]
=\exp[-c\Psi_h(f)].
\]

This is the classical branching/infinite-divisibility property, not a new market thermodynamic limit. In closed
loop, exact equality of the label-forgetting path law is the usual generator intertwining condition

\[
\mathcal L'(g\circ\pi)=(\mathcal Lg)\circ\pi,
\]

or strong Markov lumpability in finite state. Sharing the parent's random clock and mechanically splitting every
parent order can make invariance hold pathwise, but that is a compiler identity written into the coupling.

Matching does not leave a nontrivial common invariant. In FIFO, compare the parent queue
\([A(2),C(1)]\) with the clone queue \([A_1(1),C(1),A_2(1)]\). A market order of size two fills the parent group
by two units in the first book and only one in the second. Continuous pro-rata is additive by definition; lot
rounding and FIFO residual allocation break it. Aggregate call auctions preserve only aggregate supply and demand
under proportional marginal rationing; strategic clones lead to the established false-name problem.

The exact reduction is reinforced by [Lamperti's continuous-state branching
classification](https://doi.org/10.1090/S0002-9904-1967-11762-2), standard Markov lumpability, and the direct
financial axiom of [invariance to mitosis](https://doi.org/10.1287/mnsc.2020.3700). The reusable result is a
three-layer audit--quantity measure, ordered order records, and full-state lumpability--plus the FIFO interleaving
counterexample. It is not a Nature-level centerpiece.

## 3. CLMM range-coupled withdrawal robustness

For a fixed swap direction and barrier \(z\), let position \(r\) supply liquidity \(\ell_r\) over a tick interval.
In the continuous Uniswap-v3 kernel, a partial burn vector \(u\) changes the input capacity to the barrier by

\[
C_z(u)=C_z(0)-\sum_r u_rw_r(z),
\qquad
w_r(z)=\frac{\ell_r}{1-\gamma}\sum_{j\subset I_r\cap\mathrm{path}(z)}\alpha_j.
\]

Minimizing a chosen withdrawal budget \(\sum_r c_ru_r\) subject to removing enough barrier capacity is fractional
knapsack: sort \(w_r/c_r\), take full positions in order, and at most one partial position. The lemma is correct
but elementary. More importantly, \(c_r\) is withdrawn principal, not an economic cost: burning returns assets;
true cost needs gas, foregone fees, hedging and future flow.

The proposed broad-versus-narrow-position residual also used the wrong action grammar. Uniswap v3 permits partial
liquidity reduction, collection, minting and multicall through its official [position
manager](https://github.com/Uniswap/v3-periphery/blob/main/contracts/NonfungiblePositionManager.sol). Because
interval token amounts telescope, a broad position can be reduced and its unwanted complement reminted,
reproducing the continuous effect of atomic narrow ranges. The decomposition-dependent feasible set exists only
under an artificial burn-only/no-remint restriction.

[Fan et al.](https://arxiv.org/abs/2204.00464) already prove interval decomposition and optimize allocation while
making the gas--partition trade-off explicit. The more direct 2026 study [Structure Over
Scale](https://doi.org/10.1145/3774904.3792867) already combines position lifecycle, ownership concentration,
buffer liquidity, withdrawal and crash risk. Bit-exact swap rounding perturbs the continuous certificate only in
an \(O(J)\)-atomic-unit band for \(J\) crossed cells; this is implementation error, not a new collective law.

The sole reusable object is a `single_pool_fixed_swap_continuous_barrier_capacity_fractional_cover_lemma`, labeled
as a static capacity diagnostic with withdrawn principal rather than attack cost.

## 4. Initialized-tick pinning

The proposed effect coupled a liquidity jump \(\Delta L\) to the extra execution cost of crossing an initialized
tick. For external fair price \(M>b^2\), starting at square-root price \(b\), the gross arbitrage surplus after
crossing into liquidity \(L_+\) is

\[
S_+(M)=\frac{L_+}{b}(\sqrt M-b)^2.
\]

A fixed incremental charge \(c\) therefore gives the familiar threshold

\[
|\sqrt M-b|_c=\sqrt{cb/L_+}.
\]

Two native counterexamples separate the proposed mechanism.

1. If \(\Delta L\ne0\) but \(c=0\), the optimal price endpoint remains \(\sqrt M\); the liquidity jump changes
   quantity and curvature but creates no finite barrier. A liquidity jump is not sufficient.
2. Two adjacent equal-liquidity positions can leave `liquidityNet=0` while `liquidityGross>0`. The tick remains
   initialized and executes the crossing state update although liquidity is continuous. A fixed charge creates
   the same threshold without a liquidity jump, so the jump is not necessary.

The residue is a one-body fixed-charge/no-trade-band problem. Uniswap's contracts already expose initialized-tick
crossing; [Fan et al.](https://arxiv.org/abs/2204.00464) connect finer partitions to more crossings and gas, while
[Li, Dahmani and Cai](https://arxiv.org/abs/2605.06060) explicitly study price tracking with fees and fixed
execution costs. Cross-runtime replication would test billing design rather than universal market physics:
Ethereum charges realized gas, whereas [Solana priority fees depend on the requested compute-unit
limit](https://solana.com/docs/core/fees/fee-structure).

## 5. In-flight liquidity and empty-price voids

The in-flight-order candidate represented pending add/cancel messages by an age or residual-latency measure. Its
transport law is the standard PDMP equation \(\partial_t\mu-\partial_r\mu=S\). More decisively, the 2026
[*Neutrinos* study](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7162966) already reports rejected post-only
messages and spread refill by orders that were already in flight, while a [latency-aware interactive
queue-reactive simulator](https://arxiv.org/abs/2603.24137) already models races and delayed actions. Public
exchange records observe receipt, not the private decision/send time or all residual flight, and no second open
real system supplies the complete attempts/rejections/send--receive contract. The object therefore hits both
direct prior art and the existing observation-quotient veto.

For empty ticks, the first order in a gap splits a void and the last unit at a separating level merges adjacent
voids. But the projection is not state sufficient. Books with the same occupied/empty pattern and separator depth
one versus depth \(M\) have different merge hazards; books with the same gap-size multiset but a large gap at the
best quote versus deep in the book have different price-jump risk. Adding queue sizes and hazards returns the
standard queue-reactive LOB. [Farmer et al.](https://arxiv.org/abs/cond-mat/0312703) already connect the first gap
to large price changes, and [Cont, Stoikov and Talreja](https://doi.org/10.1287/opre.1090.0780) provide the parent
queue-state first-passage model.

## 6. Closure and next search boundary

No route from this round is parked, candidate or active. The result is not permission to combine the failed
pieces. In particular, do not join a void field, a committor and an s-ensemble; do not call clone count a
thermodynamic size; and do not call fixed gas a depinning force.

A future Nature-level search should now require the following before a topic is named:

- one protocol-native intervention with a complete admissible action grammar;
- a state variable invariant to labels, units, event batching and equivalent transaction sequences;
- a theorem that fails in a standard parent model but holds because of a precisely stated market mechanism;
- the same estimand in two independent implementations and a real observation contract;
- hostile T0 at or above 15% after direct-primary-work and counterexample audit.

Until such an object is found, numerical market simulation, EcoMD modification, data purchase and GPU work remain
disabled for these five formulations. The pre-existing FCC, DCRDEX and verification-liquidity statuses are not
changed by this screen.
