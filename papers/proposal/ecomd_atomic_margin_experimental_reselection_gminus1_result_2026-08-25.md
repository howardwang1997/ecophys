# EcoMD atomic, margin and experimental-market reselection: G-1 result

**Date:** 2026-08-25
**Stage:** D-3 to D-1, outcome-blind
**Decision:** no new topic card; no implementation or outcome access authorized

## Question

After the exchange-state structural-complement screen closed, this round searched three
different parts of the simulated-market state space:

1. atomic multi-protocol transactions and temporary credit;
2. cross-margin risk surfaces and protocol-native liquidation actions; and
3. randomized human double-auction records that could provide an external experimental
   truth target.

A fourth audit examined exchange-native implied matching across outright and spread order
books. This was the strongest market-mechanism complement found locally, because one resting
order may support several synthetic quotes while the matching engine prevents double fills.
The search remained outcome-blind. It inspected rules, code, schemas, licences and primary
work only; it did not download result data, run a simulator, implement a model, contact a
data owner, purchase data, change EcoMD or use a GPU.

## Decision table

| Formulation | Hostile T0 lower / point / upper | Complete NCS | Decision |
|---|---:|---:|---|
| Public randomized full-state laboratory-market bridge | 10 / 12 / 14% | 2--5% | failed-closed |
| Cross-margin action-grammar liquidation viability | 8 / 11 / 14% | 2--5% | failed-closed |
| Atomic temporary-credit capital-barrier catalysis | 5 / 9 / 14% | 1--3% | failed-closed |
| Shared-source synthetic/implied-liquidity fragility | 4 / 7 / 11% | 1--3% | failed-closed |

No conservative lower bound reaches the protocol's 15% activation floor. No formulation
has all of a non-reducible central theorem, two same-estimand simulator lineages and a
qualified real or experimental bridge. Combining the four modules does not repair any of
these failures and would change the estimand.

## A. Atomic temporary credit is a resource-constrained path problem

Let an admissible atomic call word \(w\) take protocol state \(x\) to \(y\). In a fixed
settlement numeraire, define its transient funding deficit and the minimum capital barrier
by

\[
 B(w)=\max_t[-b_t(w)]_+,\qquad
 B^\star(x,y)=\inf_{w:x\leadsto y} B(w).
\]

The word must start and finish with zero flash-loan debt and satisfy the protocol's fee,
permission, oracle and terminal-repayment rules. With owned capital \(C\) and available
temporary credit \(F\), reachability changes at \(C+F\geq B^\star\). This is a useful exact
diagnostic, but it is minimax resource-constrained reachability rather than a new collective
law.

The central components are already occupied. [Qin et al.](https://arxiv.org/abs/2003.03810)
optimize atomic flash-loan attacks; [FlashSyn](https://arxiv.org/abs/2206.10708) and
[FORAY](https://arxiv.org/abs/2407.06348) synthesize cross-protocol paths; a 2026
[eligibility study](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5932835) treats
flash access as a capital-constraint intervention; and
[Lehar and Parlour](https://www.bis.org/publ/work1062.pdf) connect flash-liquidation
mechanics to system fragility.

Two frozen killers make the boundary explicit:

1. If every agent is prefunded above \(B^\star\), a pure flash-capacity effect must vanish.
   A remaining effect is fees, permissions, selection or search technology.
2. Wrapping calls, changing call-graph depth or inserting a zero-net semantic detour while
   preserving the balance path, total fee and \(B^\star\) must not change the prediction.

[Aave V3](https://github.com/aave/aave-v3-core/blob/master/contracts/protocol/pool/Pool.sol)
and the independent [Balancer V3
Vault](https://github.com/balancer/balancer-v3-monorepo/blob/main/pkg/vault/contracts/Vault.sol)
provide executable lineages. They do not supply an orthogonal field assignment, and the
chain records successful submitted paths rather than the full opportunity and search
exposure. Announced Aave V4 deployments are therefore monitoring targets, not treatments.

## B. Cross-margin action grammar remains reachability or liquidation optimization

For portfolio state \(x\), collateral \(c\), native margin function \(M\), target safe set
\(S\), and protocol action grammar \(A(x)\), the proposed property was

> every positive-MtM state below maintenance margin has a finite sequence of admissible
> actions that reaches \(S\) without violating an intermediate execution constraint.

The potentially market-specific residual is that proportional basket transfers, leg-wise
liquidation and partial auctions have different reachable sets even at the same static
margin. It did not survive as a new theorem.
[Risk-based portfolio liquidation](https://www.slcg.com/files/research-papers/PortfolioLiquidation.pdf),
[convex cross-margin liquidation](https://research.vest.xyz/t/optimal-liquidations-via-convex-optimization/201)
and a [unified portfolio-margin/liquidation/ADL
formulation](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6868141) already occupy the
optimization core; [Solvent](https://doi.org/10.1007/978-3-031-76554-4_14) occupies generic
smart-contract liquidity reachability.

The required killers are:

1. holding state and static margin fixed, changing leg-wise actions to proportional basket
   actions must reverse the liveness result; and
2. holding state and action grammar fixed, replacing nonseparable portfolio risk with a
   separable risk function having the same static value must remove the claimed obstruction.

The certificate must also survive an economically equivalent split of one contract into
smaller units. Otherwise minimum action arity is a unitization artifact.

[Derive PM2](https://docs.derive.xyz/docs/pm2) and
[Derive liquidation](https://docs.derive.xyz/docs/liquidations-1) can be executed alongside
the independent Apache-licensed [Drift](https://github.com/drift-labs/protocol-v2) code.
Their risk surfaces, admissible actions and price formation are different, so this is a
cross-mechanism comparison rather than a same-estimand fixture. On-chain history can test a
mechanical path certificate, but not latent bidder willingness, omitted attempts or
counterfactual executable liquidity.

## C. Implied liquidity is real market structure but not yet a new physical law

Futures exchanges couple outright, calendar-spread, butterfly and inter-product books. In
a graph representation, a real order is a capacitated directed edge; an implied quote is
an admissible path, its price is the path-weight sum and its quantity is the path bottleneck.
This is not merely an analogy. CME's own
[implied-order patent](https://patents.justia.com/patent/11216878) explicitly uses contract
graphs and shortest-path trees, while [CME priority
rules](https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457096650)
order competing implied sources. Eurex calls the same operation
[synthetic matching](https://www.eurex.com/ex-en/trade/order-book-trading/matching-principles),
and [MOEX](https://www.moex.com/en/spreads) documents linked outright/spread books and
multi-leg trade identifiers.

The attractive hypothesis was that a primitive edge can support many displayed synthetic
quotes, so consuming or cancelling it deletes liquidity across several books. Two exact
reductions close the broad claim:

1. The sum of displayed implied depth is not invariant to listing economically redundant
   spread instruments. On a chain of \(n\) unit-capacity legs, listing every pair produces
   \(O(n^2)\) virtual pair depths from \(O(n)\) primitive capacity without changing the
   feasible portfolio set. A scalar amplification factor is therefore coordinate- and
   catalogue-dependent.
2. Once a demand portfolio is fixed, simultaneously executable quantity is a capacitated
   path-packing or multicommodity-flow problem. Removal sensitivity is a cut or replacement-
   path statistic. Those are valid diagnostics, but not a new market-dynamics theorem.

Static implied state also does not identify persistence: two engines can start from the
same complete books and implied paths but use immediate replenishment versus cancellation
after a primitive fill, producing opposite downstream responses.

The broad empirical claim is now directly crowded by
[Arzandeh et al.](https://doi.org/10.2139/ssrn.5622396), who measure the contribution of
implied functionality to futures spreads, depth, volatility and resilience, and by
[Peng](https://doi.org/10.1002/fut.22494), who reconstructs interconnected outright and
calendar-spread books around a rule change. The field contract also remains incomplete:
CME states that not all calculated implied orders are disseminated, MOEX's public historical
page is daily aggregate rather than a licensed event archive, and a versioned cross-venue
source-path history was not established.

## D. Public laboratory markets do not yet provide an uncontaminated truth bridge

The strongest asset was Weitzel et al.,
[*Bubbles and Financial Professionals*](https://doi.org/10.1093/rfs/hhz093), with
[a public replication catalogue](https://research.vu.nl/en/datasets/replication-data-for-bubbles-and-financial-professionals/)
and a linked [OSF project](https://osf.io/265dp/) labelled CC BY 4.0.
It includes 116 continuous-double-auction markets, randomized treatment factors, financial
professionals and students, and multiple collection locations. A possible estimand is a
cross-treatment and cross-site crash-before-recovery committor conditional on a frozen,
dimensionless liquidity state.

The asset fails the present contract before result access:

- public metadata did not establish that the raw files contain every add, modify, cancel,
  partial fill, inventory update, treatment, session and site field needed to reconstruct
  the state;
- professional versus student is a selected subject-pool contrast, not randomized
  assignment; and
- multiple collection locations do not constitute two independent replication teams, while
  all reported treatments have already been used by the source paper.

The closest event-rich alternative,
[*Trading in a Black Box*](https://github.com/ikicab/Trading-in-a-Black-Box), exposes 86,386
events and manual/automatic status fields under an MIT repository, but remains one study
whose information-feedback and convergence effects are the original claim. Other broad
laboratory assets fail explicit reuse licensing, complete queue-state, randomization or
independent-holdout requirements. Agent-based reproduction of a known double-auction result
is also an established paradigm, not a central novelty claim.

## Terminal decision and reusable gates

All four formulations are failed-closed under their frozen wording. This is not a claim
that temporary credit, portfolio margin, implied matching or laboratory markets are
unimportant. It means that the current versions do not provide the irreducible theorem plus
same-estimand external evidence required for a Nature-scale simulated-market paper.

Reusable gates are:

- temporary-credit effects must vanish under prefunding above the exact capital barrier;
- liquidation-action results must change under action grammar, not merely under static
  margin, and must survive contract-unit refinement;
- implied-liquidity metrics must be invariant to redundant instrument listing or be stated
  explicitly as demand-conditioned flow problems;
- laboratory bridges must expose the full event ledger, lawful reuse, randomized market-
  level assignment, an independent execution team and a sealed holdout; and
- different protocols or laboratories count as external validation only when the same
  state, action, observation and estimand are implemented.

No topic card, D0 manifest, experiment, implementation, data download, data purchase,
outcome inspection, EcoMD change or GPU use is authorized by this result.
