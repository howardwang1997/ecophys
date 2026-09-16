---
document: Paper G M0 resolution contract
date: 2026-09-08
evidence_label: development_not_confirmation
status_at_creation: prospective_before_v2_outcomes
---

# Paper G M0: bounded resolution contract

The PI requests continued work until a feasible/nonviable verdict. This contract
continues the existing M0 question; it does not create another candidate family or
use E/F outcomes. The original market rules, prices and inference are unchanged.

## Questions fixed before v2 execution

1. Does recovery availability change the feasible oracle value in the already planned
   directional flow, for Q=2 or 8? Audit both originally planned laws and capacities
   at T=4096, comparing rho=0.1/1 and the same model with hedge actions disabled.
2. Does the actual-feedback learner have a feasible information-acquisition strategy
   whose sample cost stays bounded when external replenishment disappears?
3. Only if the directional law's abundant-versus-scarce optimal-value difference
   exceeds 0.01 ticks/round for at least one capacity, execute the predeclared learning
   extension. Use both capacities, both feedback arms, both rho values, both existing
   methods, T=1024/4096 and sixteen new development seeds. Retain all cells regardless
   of sign. These are development measurements, not confirmation or minimax estimates.

## Constructive information probe (analytic, not a novelty claim)

Assume the stated M0 grammar, Q>=2, q0=1, fixed mark, prefunded cash and
0<nu<1. Work only at inventories 0,1,2. Never hedge.

- At q=1, post bid 98 / ask 102. The observed request side and fill/nonfill identify
  the current customer's binary willingness exactly. A buy fill means value 102;
  a buy nonfill means 101. A sell fill means cost 98; a sell nonfill means 99.
- If that round leaves q=0, post only bid 99 until a seller restores q=1.
- If it leaves q=2, post only ask 101 until a buyer restores q=1.
- Once q=1 is restored, take the next informative probe. Replanning does not reset
  the market; every inventory transition is an actual funded customer execution.

Let theta_b denote the probability of buyer value 102 and theta_s the probability
of seller cost 98. A cycle consists of one probe and the subsequent recovery to q=1.
Its mean length is

`E[L] = 1 + nu*theta_b/(1-nu) + (1-nu)*theta_s/nu`.

Proof: a probe exits down with probability nu*theta_b, followed by a geometric
seller-arrival wait of mean 1/(1-nu); it exits up with probability
(1-nu)*theta_s, followed by a geometric buyer-arrival wait of mean 1/nu. All other
probe outcomes stay at q=1. New arrivals after these stopping times remain iid,
so the probe samples have the original customer-type law. Since
`E[L] <= 1 + 1/min(nu,1-nu)`, finite expected information cost is uniform in rho,
including rho=0 and initially empty hedge depth. This is an information-acquisition
statement, not a theorem that this probing strategy minimizes regret or earns profit.

For the two predeclared laws, mean cycle lengths are 2.1 and 4.0625. These are analytic
predictions written before v2 outcomes. Simulate 32 fixed-length development replicates
per law/rho at T=4096, report completed and right-censored cycles, and compare the
probe rate with 1/E[L]. The policy ignores hedge depth; common customer innovations
must give identical inventory/probe histories across rho. No statement about rare
one-sided limits nu->0 or nu->1 follows from this uniform-in-rho argument.

## Existing-theory boundary and verdict rule

M0 has a fully observed physical state (q,d_bid,d_ask) and an unknown stationary
transition/reward law. It is not a partially observed physical-state process just
because private iid willingness is unobserved. For positive replenishment and two-sided
arrivals the relevant finite class is communicating; at rho=1 restrict to its reachable
full-depth states. Generic learning guarantees therefore already apply
([Jaksch et al., JMLR 2010](https://www.jmlr.org/papers/v11/jaksch10a.html)).
Finite-horizon oracle comparisons and average-reward bounds are different conventions;
relating them requires the appropriate finite bias-span term. Do not equate them silently.

Resource replenishment is also an established learning object
([Bernasconi et al., ICLR 2024](https://arxiv.org/abs/2306.08470)), although this contract
does not claim every market transition is exactly covered by that theorem. Market-making
feedback/value tradeoffs already have direct work
([Cesa-Bianchi et al., COLT 2025](https://proceedings.mlr.press/v291/cesa-bianchi25a.html)).

A nonzero interaction for either implemented algorithm is not the missing irreducible
result. If the construction above survives and all evidence remains within the existing
finite-control/parameter-learning account, close the **current M0-based independent
Paper G novelty formulation**. Preserve the benchmark and lemma as reusable assets.
This does not prove every inventory/feedback problem impossible to publish; reopening
requires a specific new proposition or native mechanism that defeats the construction
without simply withholding feasible customer recovery actions.

If a distinct proposition survives this hostile check, finish its proof/assumptions and
same-estimand validation before a feasible verdict. No publication probability, forecast
backfill, post-hoc parameter rescue or Nature-scale activation is authorized by this
contract. Operational qualification history remains private and is not public evidence.
