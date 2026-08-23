# Partially ordered hard-event dynamics — T0 prior-art matrix

**Audit closed:** 2026-08-23

**Search scope:** primary papers, author versions and official protocol/rule documents

**Outcome/data lock:** no market outcome, event-window statistic, data download, fit, benchmark or GPU

## 1. Coverage accounting

Each source below is assigned to exactly one frozen bucket; there is no double counting across minima.

| Frozen bucket | Required | Audited unique sources |
|---|---:|---:|
| probabilistic concurrency, event structures and trace monoids | 6 | 6 |
| stateful/dynamic partial-order reduction and model checking | 6 | 8 |
| uncertain event logs and partial-order process mining | 5 | 6 |
| interval-censored, tied or simultaneous point processes | 5 | 7 |
| linear-extension counting, sampling and parameterized complexity | 4 | 5 |
| operator splitting and commutator weak-error theory | 4 | 7 |
| market timestamp, packet, sequence and matching semantics | 5 | 8 |
| event-driven MD, contact and hybrid-event simulation | 5 | 8 |
| **Total** | **40** | **55** |

The 55 entries comprise 49 scholarly papers or primary technical reports and six official exchange protocol
documents. Additional exact-reduction controls in Section 10 are not used to satisfy these counts.

## 2. Probabilistic concurrency, event structures and trace monoids — 6/6

| ID | Primary work | Exact result, algorithm or guarantee | Collision with the frozen card |
|---|---|---|---|
| PC1 | [Varacca, Völzer and Winskel, *Probabilistic Event Structures and Domains* (2006)](https://doi.org/10.1016/j.tcs.2006.01.015) | Representation results connect supported probability on confusion-free event structures with continuous valuations on configuration domains; two extensions cover general event structures. | Probabilities on partial-order configurations are established semantics, not a new E2 object. |
| PC2 | [Abbes and Benveniste, *True-concurrency probabilistic models: Branching cells and distributed probabilities for event structures* (2006)](https://doi.org/10.1016/j.ic.2005.10.001) | Locally finite event structures are tiled by minimal branching cells; local probability choices compose while independent concurrent components remain probabilistically independent. | Local probabilistic resolution of concurrency predates the proposed learned order law. |
| PC3 | [Abbes and Benveniste, *True-concurrency probabilistic models: Markov nets and a law of large numbers* (2008)](https://doi.org/10.1016/j.tcs.2007.09.018) | Uses traces rather than firing sequences as the probabilistic object for safe Petri nets, takes branching cells as local states and proves a law of large numbers for Markov nets. | Stateful probability on partial-order executions is already formalized. |
| PC4 | [Abbes and Mairesse, *Uniform and Bernoulli measures on the boundary of trace monoids* (2015)](https://doi.org/10.1016/j.jcta.2015.05.003) | Characterizes Bernoulli measures by Möbius valuations, proves uniqueness of the uniform measure and realizes it with a Cartier--Foata-clique Markov chain. | Uniform or learned distributions over traces are frozen baselines. |
| PC5 | [Abbes, *Markovian dynamics of concurrent systems* (2019)](https://doi.org/10.1007/s10626-019-00291-z) | Treats trace-monoid partial actions on finite states, including 1-safe nets; the uniform Markov measure for an irreducible action has support exactly on state-enabled traces. | Directly covers state-dependent enabledness plus probabilistic traces. |
| PC6 | [Abbes, *Markov two-components processes* (2013)](https://doi.org/10.2168/LMCS-9(2:14)2013) | Builds asynchronous two-component trace processes without a total clock and proves an asynchronous strong Markov property and conditional independence around synchronization sequences. | Absence of a total order is already a first-class stochastic-process semantics. |

## 3. Stateful/dynamic POR and model checking — 8/6

| ID | Primary work | Exact result, algorithm or guarantee | Collision with the frozen card |
|---|---|---|---|
| PR1 | [Flanagan and Godefroid, *Dynamic Partial-Order Reduction for Model Checking Software* (2005)](https://doi.org/10.1145/1040305.1040315) | Dynamically records conflicts/happens-before and inserts backtracking so sequentially consistent executions retain representatives of Mazurkiewicz classes. | Basic state-dependent conflict exploration is DPOR. |
| PR2 | [Abdulla et al., *Optimal Dynamic Partial Order Reduction* (2014)](https://doi.org/10.1145/2535838.2535845) | Source sets and wakeup trees explore exactly one execution per Mazurkiewicz trace. | Eliminates redundant order enumeration optimally at the trace level. |
| PR3 | [Albert et al., *Context-Sensitive Dynamic Partial Order Reduction* (2017)](https://doi.org/10.1007/978-3-319-63387-9_26) | Allows independence to hold only in the reached context/state, gives a sound CSDPOR and constructs exponential separations from context-insensitive DPOR. | “Semantic” or state-local conflict is not a new parameter by itself. |
| PR4 | [Chalupa et al., *Data-Centric Dynamic Partial Order Reduction* (2018)](https://doi.org/10.1145/3158119) | Partitions executions by which write each read observes; on acyclic communication architectures it explores one representative per observation class with polynomial per-class work. | Property/observation-specific execution quotients are established. |
| PR5 | [Nguyen et al., *Quasi-Optimal Partial Order Reduction* (2018)](https://doi.org/10.1007/978-3-319-96142-2_22) | Alternative existence after a configuration is NP-complete for finite prime event structures; fixed-$k$ partial alternatives are polynomial and interpolate toward exact alternatives. | A direct algorithm/hardness frontier near a proposed conflict-width parameter. |
| PR6 | [Trimananda et al., *Stateful DPOR for Model Checking Event-Driven Applications that Do Not Terminate* (2022)](https://doi.org/10.1007/978-3-030-94583-1_20) | Gives a sound stateful DPOR for nonterminating event-driven applications, explicitly handling enabled events and revisited states. | Event-driven state and enabledness do not escape POR. |
| PR7 | [Wang et al., *Dynamic Model Checking with Property Driven Pruning to Detect Race Conditions* (2008)](https://doi.org/10.1007/978-3-540-88387-6_11) | Proves subspaces race-free with a lockset analysis and prunes states irrelevant to the declared property while preserving race detection. | Property-specific pruning is an E3 baseline. |
| PR8 | [Herbreteau, Larroze-Jardiné and Walukiewicz, *Partial-Order Reduction Is Hard* (2025)](https://doi.org/10.4230/LIPIcs.CONCUR.2025.22) | Rules out, unless P=NP, input-plus-output polynomial stateful POR whose reduced system is within a polynomial factor of the smallest sound/complete one, even for restricted acyclic programs; its key alternative test is NP-hard. | Supplies a modern matching-hardness warning for E1. |

## 4. Uncertain event logs and partial-order process mining — 6/5

| ID | Primary work | Exact result, algorithm or guarantee | Collision with the frozen card |
|---|---|---|---|
| UL1 | [Lu, Fahland and van der Aalst, *Conformance Checking Based on Partially Ordered Event Data* (2015)](https://doi.org/10.1007/978-3-319-15895-2_7) | Aligns a partially ordered trace directly to a Petri-net model without first choosing an arbitrary total order. | Direct partial-order analysis is established. |
| UL2 | [Pegoraro and van der Aalst, *Mining Uncertain Event Data in Process Mining* (2019)](https://doi.org/10.1109/ICPM.2019.00023) | Formalizes strong/weak uncertainty in activities, timestamp intervals and event existence, with realization and behavior-graph semantics. | Supplies a mature uncertain-event data model. |
| UL3 | [Pegoraro, Uysal and van der Aalst, *Discovering Process Models from Uncertain Event Data* (2019)](https://doi.org/10.1007/978-3-030-37453-2_20) | Builds uncertain directly-follows graphs with minimum and maximum possible relation frequencies and adapts inductive mining to them. | Best/worst quantities over realizations are already computed. |
| UL4 | [van der Aa, Leopold and Weidlich, *Partial Order Resolution of Event Logs for Process Conformance Checking* (2020)](https://doi.org/10.1016/j.dss.2020.113347) | Learns a distribution over total-order resolutions using exact-trace, n-gram or behavioral abstractions, computes expected conformance and gives controlled sampling approximation. | Directly occupies learning/sampling an order-resolution distribution. |
| UL5 | [Pegoraro, Uysal and van der Aalst, *Efficient Construction of Behavior Graphs for Uncertain Event Data* (2020)](https://doi.org/10.1007/978-3-030-53337-3_6) | Constructs the behavior DAG of every timestamp-interval-compatible realization in $O(n^2)$, improving the earlier cubic construction. | All compatible realizations already have a compact graph representation. |
| UL6 | [Pegoraro, Uysal and van der Aalst, *Conformance Checking over Uncertain Event Data* (2021)](https://doi.org/10.1016/j.is.2021.101810) | A behavior net accepts exactly all realizations of an uncertain trace; minimum and maximum optimal-alignment costs give lower/upper conformance bounds. | Extremely close to E1 extrema across legal realizations. |

## 5. Interval-censored, tied or simultaneous point processes — 7/5

| ID | Primary work | Exact result, algorithm or guarantee | Collision with the frozen card |
|---|---|---|---|
| TP1 | [Rizoiu et al., *Interval-censored Hawkes Processes* (2022)](https://www.jmlr.org/papers/v23/21-0917.html) | Replaces unavailable exact-time Hawkes likelihoods with a mean-behavior Poisson process and interval-censored count likelihood whose parameters map back to Hawkes parameters. | Binned event times do not by themselves create a new likelihood problem. |
| TP2 | [Cheysson and Lang, *Spectral estimation of Hawkes processes from count data* (2022)](https://doi.org/10.1214/22-AOS2173) | Gives a Bartlett-spectrum Whittle estimator for fixed-bin Hawkes counts and proves consistency and asymptotic normality. | Another rigorous count-only Hawkes route. |
| TP3 | [Wellner and Zhang, *Two estimators of the mean of a counting process with panel count data* (2000)](https://doi.org/10.1214/aos/1015951998) | Constructs NPMLE and pseudo-MLE estimators from cumulative counts at inspection times, proving consistency and pointwise limits beyond a Poisson assumption. | Interval observation of event counts has long-established inference. |
| TP4 | [Zhang, *A semiparametric pseudolikelihood estimation method for panel count data* (2002)](https://doi.org/10.1093/biomet/89.1.39) | Estimates a proportional-mean counting-process model and retains regression consistency even when the conditional counting process is not Poisson. | General semiparametric interval-count inference is occupied. |
| TP5 | [Chen and Hall, *Inference for a nonstationary self-exciting point process with an application in ultra-high frequency financial data modeling* (2013)](https://doi.org/10.1239/jap/1389370096) | Proves MLE consistency/asymptotic normality and analyzes how merging equal-time transactions versus jitter/simultaneous marks changes estimation. | Equal timestamps and modelling choices are explicit prior concerns. |
| TP6 | [Ba, Temereanca and Brown, *Algorithms for the analysis of ensemble neural spiking activity using simultaneous-event multivariate point-process models* (2014)](https://doi.org/10.3389/fncom.2014.00006) | Represents all nonempty simultaneous subsets of $C$ components as $2^C-1$ compound marks and gives an exact multinomial GLM, simulation and time-rescaling checks. | Simultaneous events can be primitive compound marks rather than permuted rows. |
| TP7 | [Kunitomo, Kurisu and Awaya, *Simultaneous multivariate Hawkes-type point processes and their application to financial markets* (2018)](https://doi.org/10.1007/s42081-018-0017-3) | Uses $2^d-1$ marginal/co-jump processes for simultaneous jumps and defines tests for Granger and instantaneous-Granger noncausality. | Explicit simultaneous-jump point-process semantics are established. |

## 6. Linear-extension counting, sampling and parameterized complexity — 5/4

| ID | Primary work | Exact result, algorithm or guarantee | Collision with the frozen card |
|---|---|---|---|
| LE1 | [Brightwell and Winkler, *Counting Linear Extensions is #P-complete* (1991)](https://doi.org/10.1145/103418.103441) | Proves exact linear-extension counting is #P-complete. | A FIFO-add embedding makes distinct-response counting #P-hard on an arbitrary-poset, add-only injective subclass; it does not establish general distinct-output membership in #P. |
| LE2 | [Bubley and Dyer, *Faster Random Generation of Linear Extensions* (1999)](https://doi.org/10.1016/S0012-365X(98)00333-1) | An adjacent-swap Markov chain with path coupling mixes in $O(n^3\log n)$, yielding near-uniform samples. | Random tie-order sampling is non-novel. |
| LE3 | [Huber, *Fast Perfect Sampling from Linear Extensions* (2006)](https://doi.org/10.1016/j.disc.2006.01.003) | A bounding chain and non-Markovian coupling-from-the-past give exact uniform linear extensions in expected $O(n^3\log n)$. | Even exact uniform order sampling is established. |
| LE4 | [Kangas et al., *Counting Linear Extensions of Sparse Posets* (2016)](https://www.ijcai.org/Proceedings/16/Papers/091.pdf) | Gives component-recursive $O(2^n n)$ counting and an $O(n^{t+4})$ variable-elimination algorithm for cover-graph treewidth $t$. | Sparse/treewidth dynamic programming is a frozen baseline. |
| LE5 | [Eiben et al., *Counting Linear Extensions: Parameterizations by Treewidth* (2016)](https://doi.org/10.4230/LIPIcs.ESA.2016.39) | Shows no cover-graph-treewidth FPT algorithm unless FPT=W[1], proves FPT for incomparability-graph treewidth, and records width-based ideal DP. | Supplies both tractability and hardness boundaries for obvious structural parameters. |

## 7. Operator splitting and commutator weak-error theory — 7/4

| ID | Primary work | Exact result, algorithm or guarantee | Collision with the frozen card |
|---|---|---|---|
| OS1 | [Trotter, *On the Product of Semi-Groups of Operators* (1959)](https://doi.org/10.1090/S0002-9939-1959-0108732-6) | Shows the semigroup generated by (A+B) is the strong limit of alternating products of the (A)- and (B)-semigroups under its conditions. | Lie--Trotter ordering is foundational, not new MD machinery. |
| OS2 | [Strang, *On the Construction and Comparison of Difference Schemes* (1968)](https://doi.org/10.1137/0705041) | The symmetric half-step/full-step/half-step composition cancels the leading asymmetric error and yields second-order splitting. | Symmetrizing order effects is a standard baseline. |
| OS3 | [Jahnke and Lubich, *Error Bounds for Exponential Operator Splittings* (2000)](https://doi.org/10.1023/A:1022396519656) | Controls Lie/Strang error for unbounded operators with commutators and nested commutators under explicit regularity conditions. | Generic commutator bounds cannot pass E1. |
| OS4 | [Hellander, Lawson and Drawert, *Local error estimates for adaptive simulation of the reaction-diffusion master equation via operator splitting* (2014)](https://doi.org/10.1016/j.jcp.2014.02.004) | Derives local distributional and observable weak-error estimates from reaction/diffusion generator commutators and uses them for adaptive stepping. | Direct stochastic hard-event/observable commutator collision. |
| OS5 | [Abdulle, Vilmart and Zygalakis, *Long Time Accuracy of Lie--Trotter Splitting Methods for Langevin Dynamics* (2015)](https://doi.org/10.1137/140962644) | Backward-error conditions characterize long-time invariant-measure accuracy, which need not equal finite-time weak order. | Long-horizon Langevin splitting accuracy is established. |
| OS6 | [Alamo and Sanz-Serna, *A Technique for Studying Strong and Weak Local Errors of Splitting Stochastic Integrators* (2016)](https://doi.org/10.1137/16M1058765) | Word series systematically derive strong/weak local errors and order conditions for Stratonovich-SDE splittings. | Stochastic order effects already have a calculus. |
| OS7 | [Gourgoulias, Katsoulakis and Rey-Bellet, *Information Metrics for Long-Time Errors in Splitting Schemes for Stochastic Dynamics and Parallel Kinetic Monte Carlo* (2016)](https://doi.org/10.1137/15M1047271) | Path-space relative-entropy rate and generator commutators quantify long-time splitting error in stochastic dynamics and parallel KMC. | Provides both dynamics and information-theoretic long-time error measures. |

## 8. Market timestamp, packet, sequence and matching semantics — 8/5

These are primary protocol/rule sources because the question is what the feed contract actually guarantees, not
what an empirical paper infers from prices.

| ID | Primary source | Exact rule or schema guarantee | Consequence for the frozen object |
|---|---|---|---|
| MS1 | [Nasdaq, *TotalView-ITCH 5.0 Specification*](https://nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHSpecification.pdf) | Add/cancel/delete/replace/execution messages share a day-unique Order Reference Number; executions have unique Match Numbers, but split fills lack a public common aggressor-parent ID. | Persistent lifecycle is available; aggressor grouping is not automatically recoverable. |
| MS2 | [Nasdaq, *MoldUDP64 Specification*](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/moldudp64.pdf) | Packet blocks carry Session, a 64-bit first-message Sequence Number and Message Count; later message numbers follow packet position. | Equal timestamps in the raw sequenced feed do not imply unknown row order. |
| MS3 | [NYSE, *Pillar Integrated Feed Client Specification v2.5*](https://beta.nyse.com/publicdocs/nyse/data/NYSE_Pillar_Integrated_Feed_Client_Specification_v2.5.pdf) | SourceTimeNS is distinct from SymbolSeqNum, which orders all messages for a symbol; OrderID connects the lifecycle. | Timestamp equality must not erase authoritative sequence. |
| MS4 | [CME, *MDP 3.0 Event-Based Market Data Messaging*](https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457325420/MDP%2B3.0%2B-%2BEvent%2BBased%2BMarket%2BData%2BMessaging) | Messages caused by one incoming action share TransactTime; MatchEventIndicator marks the end of the atomic matching event. | Supplies an authoritative macro-event boundary for split messages. |
| MS5 | [CME, *Market by Order FAQ*](https://www.cmegroup.com/articles/faqs/market-by-order-mbo.html) | MBO publishes OrderID/PriorityID while MBP aggregates quantity and order count by price. | The coarse product loses identities/content and is not automatically the required content-preserving coarsening. |
| MS6 | [Deutsche Börse/Eurex, *T7 Enhanced Order Book Interface Manual, Release 14.0*](https://www.eurex.com/resource/blob/4597908/bf8b02f4f4d1f220e54aa1a93f0482df/data/T7_R.14.0_%20EOBI_Manual_Version_1.pdf) | ApplSeqNum/MsgSeqNum provide channel/product order; atomic matching units use datagram placement or CompletionIndicator across datagrams. | Supplies both authoritative order and group-completion metadata. |
| MS7 | [Morariu-Patrichi and Pakkanen, *State-dependent Hawkes processes and their application to limit order book modelling* (2022)](https://doi.org/10.1080/14697688.2021.1983199) | Records that LOBSTER represents one market order matching $n$ resting orders as $n$ equal-timestamp rows and aggregates them back to one event. | Direct empirical-data-semantics support for mandatory toy case 4. |
| MS8 | [LOBSTER, *Reconstruction of Limit Order Books using LOBSTER* (2013)](https://data.lobsterdata.com/info/docs/LobsterReport.pdf) | Reconstructs Nasdaq order lifecycles from ITCH and keeps message/book files synchronized event by event. | LOBSTER row order inherits a sequenced source; it is ground truth to coarsen, not an intrinsically unordered feed. |

## 9. Event-driven MD, contact and hybrid-event simulation — 8/5

| ID | Primary work | Exact result, algorithm or guarantee | Collision with the frozen card |
|---|---|---|---|
| MD1 | [Rapaport, *The event scheduling problem in molecular dynamic simulation* (1980)](https://doi.org/10.1016/0021-9991(80)90104-7) | Uses a binary-tree future-event list and local updates for hard-particle event selection. | Event scheduling is foundational EDMD machinery. |
| MD2 | [Lubachevsky, *How to simulate billiards and similar systems* (1991)](https://doi.org/10.1016/0021-9991(91)90222-7) | Processes asynchronous pair events in nondecreasing time and attains $O(\log N)$ scheduling per event under locality assumptions. | Asynchronous hard-event simulation is established. |
| MD3 | [Miller and Luding, *Event-driven molecular dynamics in parallel* (2004)](https://doi.org/10.1016/j.jcp.2003.08.009) | Gives parallel EDMD with dynamic load balancing and synchronization of predicted cross-processor collisions. | Distributed event order/synchronization is old MD territory. |
| MD4 | [Donev, Torquato and Stillinger, *Neighbor list collision-driven molecular dynamics simulation for nonspherical hard particles. I* (2005)](https://doi.org/10.1016/j.jcp.2004.08.014) | Partial-update neighbor lists and bounding-sphere complexes support reliable collision prediction for nonspherical hard particles. | Collision detection itself is not a residual contribution. |
| MD5 | [Bannerman, Sargant and Lue, *DynamO: a free O(N) general event-driven molecular dynamics simulator* (2011)](https://doi.org/10.1002/jcc.21915) | Implements general EDMD for hard-core and stepped potentials with reported $O(N)$ total scaling. | A mature simulator baseline exists. |
| MD6 | [Bannerman et al., *Stable algorithm for event detection in event-driven particle dynamics* (2014)](https://doi.org/10.1007/s40571-014-0021-8) | Handles floating-point-created invalid geometry by explicitly defining invalid-state dynamics and recovery. | State validity and event enabledness are explicit MD concerns. |
| MD7 | [Strobl, Bannerman and Pöschel, *Stable algorithm for event detection in event-driven particle dynamics: logical states* (2016)](https://doi.org/10.1007/s40571-016-0106-7) | Shows positions alone may not identify a stepped-potential interaction state and introduces a separate logical state governing the next legal event. | Direct analogue of state-dependent legal-event semantics. |
| MD8 | [Halm and Posa, *Set-valued rigid-body dynamics for simultaneous, inelastic, frictional impacts* (2024)](https://doi.org/10.1177/02783649241236860) | A set-valued differential inclusion covers arbitrary impact ordering; existence, dissipation and finite termination are proved, and an LCP sampling method gives a probabilistic ε-net approximation of the post-impact set. | Directly occupies “do not choose one unknown order; return a certified outcome set” in the transfer domain. |

## 10. Exact-reduction controls beyond the eight minima

These sources decide E1--E3 but are deliberately not recounted above.

| ID | Primary work | Exact reduction pressure |
|---|---|---|
| XR1 | [Herlihy and Wing, *Linearizability: A Correctness Condition for Concurrent Objects* (1990)](https://doi.org/10.1145/78969.78972) | A history is legal when some sequential ADT history preserves its real-time partial order; this is the exact state-enabled legal-order object on interval histories. |
| XR2 | [Gibbons and Korach, *Testing Shared Memories* (1997)](https://doi.org/10.1137/S0097539794279614) | General single-history linearizability checking is NP-complete, with restricted tractable cases. |
| XR3 | [Bouajjani, Enea and Wang, *Checking Linearizability of Concurrent Priority Queues* (2017)](https://doi.org/10.4230/LIPIcs.CONCUR.2017.16) | Treats histories as interval orders, the sequential priority queue as a stateful LTS, reduces violations to reachability and obtains small-data-value witnesses and PSPACE/EXPSPACE bounds. |
| XR4 | [Bouajjani et al., *On Reducing Linearizability to State Reachability* (2018)](https://doi.org/10.1016/j.ic.2018.02.014) | Reduces linearizability to control-state reachability for fixed co-regular/step-by-step-linearizable specifications including common queues/stacks. |
| XR5 | [Horn and Kroening, *Faster Linearizability Checking via P-Compositionality* (2015)](https://doi.org/10.1007/978-3-319-19195-9_4) | A semantically partitioned history is linearizable iff its P-parts are, supplying within-ADT semantic decomposition. |
| XR6 | [Lee and Mathur, *Fixed Parameter Tractable Linearizability Monitoring* (2026)](https://doi.org/10.1145/3808315) | Gives $O(k2^{2k}n^2)$ FIFO-queue and $O(k2^k n\log n)$ priority-queue monitors in the number-of-processes parameter $k$. |
| XR7 | [Amarilli et al., *Computing possible and certain answers over order-incomplete data* (2019)](https://doi.org/10.1016/j.tcs.2019.05.013) | Takes all linear extensions as possible worlds, computes order-aware accumulation result sets, asks POSS/CERT, proves NP/coNP completeness and bounded-width/operator tractability. |
| XR8 | [de Colnet, Meel and Mathur, *Counting and Sampling Traces in Regular Languages* (2026)](https://doi.org/10.1145/3776723) | Trace counting is #P-hard even for DFAs, but admits an FPRAS and fully polynomial almost-uniform sampler. |
| XR9 | [Balasubramanian et al., *State Space Estimation for DPOR-Based Model Checkers* (2026)](https://doi.org/10.1145/3808291) | DPOR trace-space counting is #P-hard and subexponentially inapproximable unless P=NP; a polynomial-time unbiased estimator is derived from optimal-DPOR trees. |
| XR10 | [Zdancewic and Myers, *Observational Determinism for Concurrent Program Security* (2003)](https://doi.org/10.1109/CSFW.2003.1212703) | Formalizes scheduler-independent observable behavior across concurrent executions. |
| XR11 | [Huisman, Worah and Sunesen, *A Temporal Logic Characterisation of Observational Determinism* (2006)](https://doi.org/10.1109/CSFW.2006.6) | Gives sound/complete self-composed temporal-logic characterizations for finite-state observational determinism; failures yield counterexamples. |
| XR12 | [Timmer, Stoelinga and van de Pol, *Confluence Reduction for Probabilistic Systems* (2011)](https://doi.org/10.1007/978-3-642-19835-9_29) | Defines probabilistic confluence and an on-the-fly reduction preserving branching probabilistic bisimulation. |
| XR13 | [Beer et al., *Explaining Counterexamples Using Causality* (2012)](https://doi.org/10.1007/s10703-011-0132-2) | Formalizes causal explanations of property counterexamples; exact causal-set computation is NP-complete and a polynomial over-approximation wraps generic model checkers. |
| XR14 | [Ashok, Křetínský and Weininger, *PAC Statistical Model Checking for Markov Decision Processes and Stochastic Games* (2019)](https://doi.org/10.1007/978-3-030-25540-4_29) | Gives PAC reachability bounds for MDPs and stochastic games with unknown transition probabilities in black- and grey-box settings. |
| XR15 | [He and Parker, *Robust Verification of Concurrent Stochastic Games* (2026)](https://arxiv.org/abs/2601.12003) | Interval concurrent stochastic games combine player nondeterminism with epistemic transition uncertainty and compute finite/infinite-horizon robust reachability/reward values. |
| XR16 | [Leemans et al., *Partially ordered stochastic conformance checking* (2025)](https://doi.org/10.1007/s10115-024-02280-7) | Treats equal timestamps as uncertain partial-order traces and produces stochastic conformance bounds; worst-case uncertain-order traversal is factorial. |
| XR17 | [Tunç, Dong and Pavlogiannis, *Fast Atomicity Monitoring* (2026)](https://doi.org/10.1145/3808248) | Current atomicity monitoring covers conflict-serializable transactional blocks, the semantic object needed to prevent interleaving within split event groups. |
| XR18 | [Asynchronous Wait-Free Runtime Verification and Enforcement of Linearizability (2026)](https://doi.org/10.1145/3777409) | Defines runtime verification against a partial sequential transition function and proves wait-free verification impossibilities for queues, stacks, sets and priority queues under its model. |

## 11. Matrix verdict

The collision is not merely that separate fields contain ingredients. Four works occupy the proposed interfaces
at the correct abstraction level:

1. legal state-dependent queue orders are linearizability/sequential-specification histories (XR1--XR6);
2. all possible accumulation results plus possible/certain decisions already have exact complexity boundaries
   for order-incomplete possible worlds (XR7);
3. learned transition uncertainty plus an order scheduler is PAC/robust stochastic-game verification
   (XR14--XR15); and
4. the MD transfer domain already returns a certified set over arbitrary simultaneous-impact ordering (MD8).

The matrix therefore leaves no frozen E1--E3 result intact. A future theorem would need a formally distinct
object and proof; a market application or conjunction of these occupied properties cannot create novelty.
