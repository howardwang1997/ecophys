# FCC randomized-rank cascade — D−1 result

**Date:** 2026-09-05

**Archetype:** empirical intervention / simulator method

**Decision:** **FAIL — CLOSE.** Structural support and one observed-row accounting contract are
real, but the proposed ICLR contribution is either deterministic mechanism replay, standard
sequential causal inference under interference, or an unidentified same-state paired
counterfactual. The exact FCC executor is also described in a 2026 patent publication, while the
auction-simulation, order-of-addition, interference, off-policy-evaluation, and neural-execution
neighborhoods are already populated. No effect analysis, simulator implementation, EcoMD
integration, SSH, or GPU work is authorized.

## 1. Question and rival explanations

Within a round and price point, the FCC assigns bid-specific pseudorandom numbers and processes
bids sequentially. Applied bids update aggregate demand, activity, and a rejection queue. The
candidate asked whether changing only this microscopic order creates a reproducible response
cascade and whether a mechanism-faithful simulator can predict its distribution in later auctions.

- **H1 — irreducible cascade:** random micro-order creates a scientifically distinct, identifiable
  path-distribution object whose prediction requires a new market-simulator method.
- **H0a — executable rule:** conditional on complete rule state, immediate application and posted
  prices are deterministic outputs of an ordinary auction executor.
- **H0b — ordinary causal design:** later bidder responses are potential outcomes under a sequential
  randomized treatment with interference and carryover.
- **H0c — unidentified coupling:** the desired distance between two outcomes from the same market
  state depends on the unobserved joint coupling of potential paths, not only on their randomized
  marginals.

A useful positive result would have needed to reject all three null reductions. A null result would
still have shown robustness of the allocation rule, but would not have supported a new ICLR method.

## 2. What the source and contract audit established

### 2.1 Common abstract queue grammar, not one frozen mechanism

Official procedures for [Auction 103](https://docs.fcc.gov/public/attachments/FCC-19-63A1_Rcd.pdf),
[105](https://docs.fcc.gov/public/attachments/FCC-20-18A1.pdf),
[107](https://docs.fcc.gov/public/attachments/FCC-20-110A1.pdf),
[110](https://docs.fcc.gov/public/attachments/DA-21-655A1.pdf),
[108](https://docs.fcc.gov/public/attachments/DA-22-120A1_Rcd.pdf), and
[113](https://docs.fcc.gov/public/attachments/DA-25-1075A1_Rcd.pdf) describe pseudorandom
tie ordering and sequential reconsideration. The public schemas for
[103](https://auctiondata.fcc.gov/public/projects/auction103/static_files/Auction_103_PRS_File_Formats_1.1.pdf/download),
[107](https://auctiondata.fcc.gov/public/projects/auction107/static_files/auction_107_prs_file_formats.pdf/download),
[108](https://auctiondata.fcc.gov/public/projects/auction108/static_files/auction_108_prs_file_formats.pdf/download),
and [113](https://auctiondata.fcc.gov/public/projects/auction113/static_files/auction_113_prs_file_formats_final.pdf/download)
expose related reporting fields.

This is not yet a cross-auction treatment identity. Auctions 103/105/107/110 use generic
multi-block processing with partial application and switching. Auctions 108/113 are clock-1,
supply-one systems with binary demand and proxy-specific rules. A researcher-authored common DSL
would have to prove that the sorting unit, random-number lifecycle, queue update, feasibility
constraints, partial-application semantics, state, and response are preserved. No such bridge was
found. The attempted Auction 102 technical-guide retrieval returned an access-denied HTML payload
and is not counted as retrieved evidence.

### 2.2 Structural support passed only as an upper-bound prefilter

The frozen aggregate-only program found the following counts of structurally coupled
round–price-point blocks:

| Auction | Role | Upper bound $U$ | Provisional floor | Result |
|---|---|---:|---:|---|
| 108 | clock-1 development family | 244 | 30 | prefilter pass |
| 113 | clock-1 replication family | 53 | 30 | prefilter pass |
| 110 | generic-mechanism comparator | 362 | not a replication gate | descriptive only |

These counts are not counts of independent experimental units and not counts of order-sensitive
effects. Eligibility and aggregate demand carry across blocks and rounds, so one auction may be one
large interference cluster. The program SHA-256 is
`2b08b286ded49c520f8feb9c5e2d56398630fa97a4eff8a272e757c7641a0cdf`; the final support
specification SHA-256 is
`d377ca000fdfaad944021ecefaf823c3256d6de822c021b58b36184b24de6bdb`.

### 2.3 The Auction 108 observed-row accounting contract closed

The restricted join contained 665,637 bid-product keys and 657,524 result-product keys. Exactly
8,113 bid keys lacked a result row; every one was a Round-1 simple quantity-zero bid whose price
equaled the start-of-round price. All 12,202 Round-1 quantity-one keys matched a fully applied
demand-one result, no impossible matched transition was found, and the accounting exhausted all
keys. Under the official schema, the unmatched records are system-created zero-demand missing-bid
placeholders rather than unexplained failures.

This validates a narrow observed-row interpretation; it is not a source-code equivalence proof for
the whole processor, queue, or future response process. The program SHA-256 is
`7f2750b12e65b6be3bd7835d3e02ccd57583d7498455c773793bfcd6399a1cfd`; the final diagnostic
specification SHA-256 is
`c77a629c5f265e2fefe9c31db3d79e64029e52c46566ca61fcf5e75384899942`.

### 2.4 Randomization semantics did not pass

The documents establish a bid-specific pseudorandom ordering. They do not freeze a public PRNG,
seed, persistence rule across bids/rounds, or an auditable assignment probability for every
admissible permutation. A retrospective balance or randomness check cannot prove exchangeability.
The D−1 freeze required this uncertainty to be resolved rather than assumed, so this conjunctive
gate remains failed.

## 3. Identification theorem: paired damage spreading is not observed

Let $g$ be a complete pre-processing state, $\Omega_g$ the admissible permutations, $\Pi_g$ the
realized random permutation, and $Y_g(\pi)$ the future response path under permutation $\pi$. The
field record observes one path $Y_g(\Pi_g)$.

The physics-style target is naturally a same-state paired dispersion such as

\[
D_g(\pi,\pi')=d\!\left(Y_g(\pi),Y_g(\pi')\right),
\qquad E[D_g(\Pi_g,\Pi'_g)\mid g].
\]

**Proposition.** Random assignment of one permutation per state does not nonparametrically identify
this paired dispersion, even when both marginal potential-outcome laws are identified.

**Proof by embedded binary subcase.** Consider two permutations, treatment $T\in\{0,1\}$ randomized
independently of $U\sim\mathrm{Bernoulli}(1/2)$, and binary outcomes.

- World A has $(Y(0),Y(1))=(U,U)$, hence $E|Y(1)-Y(0)|=0$.
- World B has $(Y(0),Y(1))=(U,1-U)$, hence $E|Y(1)-Y(0)|=1$.

In both worlds, $Y\mid T=0$ and $Y\mid T=1$ are Bernoulli$(1/2)$, so the complete randomized
observed law of $(T,Y)$ is identical. The target differs. Any two permutations inside a larger
permutation set embed this construction. Therefore no data-only estimator can recover same-state
path coupling without extra structural assumptions, repeated branchable realizations of the same
state, or valid bounds.

This does **not** deny identification of a marginal average rank effect under a known assignment
law, positivity, a fixed exposure mapping, and a valid sequential-interference design. It separates
that standard estimand from the stronger damage-spreading claim.

## 4. Why the apparent repairs do not create the missing ICLR result

1. **Exact replay.** If the complete state and deterministic processor are available, replaying all
   permutations identifies immediate applied demand mechanically. That is algorithm execution, not
   the unobserved strategic response of humans in later rounds.
2. **Rank as an instrument.** Priority randomization can instrument realized allocation under stated
   conditions, but exclusion is not automatic here because order changes aggregate demand,
   eligibility, prices, and other bidders' exposures.
3. **Exposure mapping.** A fixed graph/exposure map enables standard randomization inference; it
   does not identify individual paired paths and is itself a substantive assumption under global
   auction state.
4. **Monotonicity or structural coupling.** Queue reconsideration, product switching, eligibility,
   and adaptive bids can reverse responses. No defensible monotone coupling was found. Assumption-
   dependent bounds would be a different, narrower econometric paper.
5. **Factual held-out scoring.** A proper score can test predictions under the logging policy. It
   cannot validate the joint counterfactual coupling or performance on unsupported permutations.
6. **Order-policy OPE.** Reweighting to a new permutation distribution is ordinary off-policy
   evaluation with a factorial action space and severe support constraints.
7. **Neural executor.** Learning the public processor is neural algorithm execution. It needs a new
   generalization theorem or failure mode beyond existing multiple-solution NAR, causal
   regularization, and order-of-addition design; none survived this audit.

## 5. Hostile novelty audit

The frozen minimum of twenty primary works was exceeded. The nearest neighborhood is not one empty
field but five mature parent fields:

| # | Primary work | What it already owns relative to this route |
|---:|---|---|
| 1 | Csirik et al., [FAucS](https://www.cs.utexas.edu/~pstone/Papers/bib2html/b2hd-FCC01.html) (2001) | FCC spectrum-auction simulation for autonomous agents |
| 2 | Weiss et al., [SATS](https://people.bu.edu/blubin/papers/md/SATS2017AAMAS.pdf) (2017) | spectrum-auction instances and valuation models |
| 3 | Newman et al., [simulated reverse clock auctions](https://arxiv.org/abs/1706.04324) (2017) | sequential FCC-style clock processing with random-seed tie breaking |
| 4 | Soumalias et al., [ML-CCA](https://ojs.aaai.org/index.php/AAAI/article/view/28850) (2024) | ML-powered combinatorial clock-auction execution |
| 5 | Lee et al., [priority-queue randomization](https://arxiv.org/abs/2605.25169) (2026) | causal effects and instruments under randomized queue allocation |
| 6 | Aronow and Samii, [general interference](https://arxiv.org/abs/1305.6156) (2017) | design, exposure mappings, IPW, and variance under interference |
| 7 | Basse et al., [conditional randomization under interference](https://arxiv.org/abs/1709.08036) (2019) | valid conditional randomization tests |
| 8 | Puelz et al., [graph-theoretic randomization tests](https://academic.oup.com/jrsssb/article/84/1/174/7056130) (2022) | exposure graphs and constructive interference tests |
| 9 | Bojinov et al., [panel experiments and dynamic causal effects](https://arxiv.org/abs/2003.09915) (2021) | finite-population sequential causal effects |
| 10 | Han et al., [population interference in panel experiments](https://arxiv.org/abs/2103.00553) (2024) | temporal experiments with population interference |
| 11 | Abdulkadiroğlu et al., [Research Design Meets Market Design](https://onlinelibrary.wiley.com/doi/abs/10.3982/ECTA13925) (2017) | impact evaluation through centralized assignment |
| 12 | Abdulkadiroğlu et al., [Breaking Ties](https://arxiv.org/abs/2101.01093) (2021) | causal identification from lottery tie breakers in assignment mechanisms |
| 13 | Munro, [Designed Markets](https://arxiv.org/abs/2504.07217) (2026 revision) | interference-aware causal estimation through a mechanism |
| 14 | Ganju and Lucas, [randomized versus random run order](https://www.sciencedirect.com/science/article/pii/S0378375804001119) (2005) | carryover and dependence when treatments are not reset |
| 15 | Peng et al., [Design of Order-of-Addition Experiments](https://arxiv.org/abs/1805.04648) (2019) | factorial permutation treatments and fractional designs |
| 16 | Piepho and Williams, [Regression Models for Order-of-Addition Experiments](https://arxiv.org/abs/2101.10769) (2021) | pairwise-order, position, and response-surface models |
| 17 | Rios and Lin, [Graphical methods for Order-of-Addition experiments](https://academic.oup.com/jrsssb/article/87/5/1309/8116800) (2025) | constrained permutations represented by DAGs |
| 18 | Sondhi et al., [Balanced Off-Policy Evaluation](https://proceedings.mlr.press/v108/sondhi20a.html) (2020) | OPE in general action spaces |
| 19 | Rebello et al., [factored-action OPE](https://arxiv.org/abs/2307.07014) (2023) | decomposed importance sampling in combinatorial actions |
| 20 | Sachdeva et al., [policy-convolution OPE](https://arxiv.org/abs/2310.15433) (2023) | support/bias–variance tradeoff in large action spaces |
| 21 | Saito and Yasui, [Counterfactual Cross-Validation](https://proceedings.mlr.press/v119/saito20a.html) (2020) | model selection when individual counterfactuals are missing |
| 22 | Boyer et al., [counterfactual prediction evaluation](https://arxiv.org/abs/2308.13026) (2025 revision) | identification of policy-specific predictive performance, not paired paths |
| 23 | Firpo and Ridder, [treatment-effect-distribution partial identification](https://www.sciencedirect.com/science/article/pii/S0304407619300673) (2019) | marginal potential outcomes do not identify their joint effect distribution |
| 24 | Frandsen and Lefgren, [distribution-of-effects bounds](https://onlinelibrary.wiley.com/doi/abs/10.3982/QE1273) (2021) | assumption-dependent bounds for individual effect distributions |
| 25 | Kujawa et al., [NAR with Multiple Correct Solutions](https://arxiv.org/abs/2409.06953) (2025) | distributional neural execution when algorithms have multiple outputs |
| 26 | Bevilacqua et al., [NAR with Causal Regularisation](https://proceedings.mlr.press/v202/bevilacqua23a.html) (2023) | causal invariance for algorithmic OOD generalization |

In addition, U.S. application publication
[20260141450](https://patents.justia.com/patent/20260141450) gives an explicit ascending-clock
executor: add missing bids and pseudorandom numbers, compute price points, apply maintenance bids,
sort remaining bids, maximally apply subject to supply/eligibility, and repeatedly sort and process
the rejection queue. It uses Auction 107 context. The document does not by itself claim causal
identification or counterfactual cascade science, so it is not a complete anticipation of H1; it
does remove novelty from “first executable FCC auction engine.”

The repository's prior 55-work
[partial-order audit](ecomd_partial_order_event_t0_result_2026-08-23.md) independently closed the
commutator, partial-order reduction, linearizability, reachability, counting, and confluence exits.

## 6. D−1 gate decision

| Frozen gate | Result | Reason |
|---|---|---|
| Binding support | partial pass | $U_{108}=244$ and $U_{113}=53$, but these are dependent structural upper bounds, not binding causal units |
| Randomization semantics | fail | public PRNG, seed, persistence, and exact permutation probabilities are not frozen |
| First-stage replay | partial pass | observed Auction 108 row accounting closes; whole-processor source equivalence does not |
| Replication contract | fail | clock-1 supply-one and generic multi-block mechanisms lack a proved common action/state map |
| Novelty | fail | standard causal/OofA/OPE/NAR reductions plus direct executor collision |
| Simulator feasibility | fail for paper claim | an executor is feasible, but no independent faithful simulator lineages or field-response truth exist |

Because the pass conditions were conjunctive, one failure suffices. Four substantive failures are
present. The automatic-stop clause is met exactly: the surviving formulations are ordinary
randomization inference plus auction execution, or a nonidentified paired-path target.

## 7. Publication and compute decision

A standalone ICLR main-track paper from this route is assessed at **2–3%** after the hostile audit.
This is a diagnostic judgment, not a calibrated forecast and not the reason for closure. The hard
reasons are identification, standard-parent reduction, cross-mechanism mismatch, and simulator
validation failure.

A narrower auction/econometrics study of a marginal randomized-rank effect might be publishable if
the assignment law and exposure design can be defended, but it is not the requested new EcoMD/ICLR
contribution. Outcome access would now also need to account for the separately recorded
[Auction 102/105 incident](fcc_clock1_historical_family_outcome_access_incident_2026-09-05.md).

No experiment plan is created. The A800 worker at `100.113.230.38` and V100 workers at
`100.80.236.112` and `100.123.220.57` receive no job.

## 8. Re-entry conditions

Reopen only if at least one of the following new objects is available and independently audited:

1. prospectively repeated, independently randomized and reset realizations of the same complete
   market state, or a branchable human/laboratory protocol observing both paired paths;
2. a theorem that nontrivially identifies or sharply bounds same-state path divergence under
   assumptions defensible for switching, queues, eligibility, and adaptive bidders; or
3. two independently governed exact-mechanism simulator lineages plus a sealed field confirmation
   source for the same action, state, and response.

A new FCC auction number, a larger count of tie blocks, a learned executor, or a renamed
damage-spreading metric is not a re-entry trigger.
