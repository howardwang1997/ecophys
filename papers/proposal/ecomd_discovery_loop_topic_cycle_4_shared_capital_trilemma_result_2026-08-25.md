# EcoMD Discovery Loop topic cycle 4: shared-capital quote trilemma audit

**Date:** 2026-08-25
**Scope:** simulated markets, market physics, and financial physics
**Stage:** D-2 theorem-residual audit
**Literature cutoff:** 2026-08-25
**Outcome access:** none
**Decision:** exact parent reduction; zero topic cards and zero execution authorizations

## 1. Candidate residual

Cycle 3 found a real mechanism but no qualifying topic: one deposited balance can support
offers in several markets, so a fill in one market can make displayed liquidity elsewhere
unexecutable. This audit asked whether a narrower theorem survives:

> Can a market simultaneously provide capital amplification, strong executable-quote
> integrity, and coordination-free cross-market composability under one conserved balance?

The answer is no in the smallest two-market system. The result is valid, but it is an exact
application of escrow transactions and invariant confluence rather than a new market theorem.

## 2. Definitions

Let a conserved resource have capacity `B>0`, and let markets A and B publish offers drawing
from that resource.

- **Capital amplification:** both markets may advertise locally executable amounts whose sum
  exceeds `B`.
- **Strong quote integrity:** a locally valid take of an advertised amount commits without
  later failure, rollback, or removal caused by another market's use of the same resource.
- **Coordination-free composability:** takes in distinct markets may commit from their local
  state without a shared lock, serialization point, synchronous rights transfer, or consensus
  round; independently valid results must merge to a valid global state.
- **Safety:** total committed resource never exceeds `B`.

The claim concerns simultaneous guarantees, not average landing probability or a particular
blockchain scheduler.

## 3. Two-market proof

Set `B=1` and let each market advertise a one-unit take. Capital amplification makes both
takes locally admissible. Execute the A take and B take concurrently from the common initial
state. Each local branch preserves safety because it consumes exactly one unit. If the two
branches merge without coordination, total consumption is two units and violates safety.

Therefore the decrement operations are not invariant-confluent for the nonnegative-resource
invariant. Every safe implementation must give up at least one property:

1. **Coordinate or serialize.** A global account lock or total order selects one winner, so
   execution is not coordination-free.
2. **Escrow rights.** Preallocate rights `b_A+b_B<=B`. Each market can execute locally, but it
   cannot strongly guarantee displayed commitments summing above `B`.
3. **Permit failure or repair.** Let one take fail, remove an unbacked order, compensate a
   taker, or roll back. Capital amplification remains, but strong quote integrity is false.

O'Neil's escrow method already reserves bounded aggregate resources so concurrent updates can
commit safely. Bailis et al.'s invariant-confluence result gives the necessary-and-sufficient
coordination boundary for invariant-preserving transactions. Bounded-counter CRDTs implement
the same rights-partition idea for numeric invariants. The proof above is their two-decrement
example with market labels.

## 4. Why price priority does not rescue novelty

Price and time priority can choose which take should win once a serial order or shared state
is available. They do not make two independently valid resource decrements merge safely.
Changing prices, queues, or market labels therefore changes allocation or welfare after the
coordination decision, not the trilemma's safety core.

Manifest chooses a shared global balance and synchronous account access, then removes an
order that has become unbacked. Mangrove permits programmed sourcing, sibling retraction, or
failure with a bounty. These are different engineering points in the known design space; they
are not two replications of a new law.

## 5. Killer twins and empirical boundary

- **Rights-partition twin:** split one unit into escrow rights `(1,0)` or `(1/2,1/2)`. Safety
  and local execution become possible, while the advertised strongly guaranteed total never
  exceeds one. Any claimed counterexample must identify where extra resource enters.
- **Serialization twin:** keep both one-unit offers but impose one atomic global lock. One
  succeeds and one is removed or rejected. The mechanism preserves safety only by dropping
  coordination-free execution or quote integrity.
- **Quote-label twin:** swap prices and priority labels while preserving the two decrements.
  The safety conclusion is unchanged, showing that the core theorem is not price formation.

Confirmed chain history can reveal which branch committed, but not all dropped, privately
forwarded, replaced, or never-included takes. It therefore cannot identify a coordination or
failure probability without a submission denominator. A local workload would demonstrate a
chosen scheduler rather than discover the theorem.

## 6. Decision

**Failed-closed at hostile T0 1/3/6%.** The statement is correct but is a direct corollary of
escrow and invariant confluence. It supplies a useful design checklist, not a Nature-grade
market-physics contribution.

Reopen only if a descendant proves a quantitative market result that is not implied by
invariant preservation or escrow rights—for example, a tight price/priority-dependent bound
that survives token and order refinement—and validates that same object in two independent
native mechanisms with complete attempted-transaction exposure. Merely calling the result a
liquidity CAP theorem does not reopen it.

## 7. Primary and official sources

1. O'Neil, *The Escrow Transactional Method*: https://doi.org/10.1145/7239.7265
2. Bailis et al., *Coordination Avoidance in Database Systems*: https://arxiv.org/abs/1402.2237
3. Balegas et al., *Extending Eventually Consistent Cloud Databases for Enforcing Numeric Invariants*: https://arxiv.org/abs/1503.09052
4. Manifest, *The Orderbook Manifesto*: https://www.manifest.trade/assets/The_Orderbook_Manifesto.pdf
5. Manifest global-order matching source: https://github.com/Bonasa-Tech/manifest/blob/bad2e6bb16ebb35349a373083933bb2f9fcd6354/programs/manifest/src/state/market.rs
6. Mangrove amplified-liquidity implementation guide: https://docs.mangrove.exchange/dev/strat-lib/guides/creating-a-direct-contract
