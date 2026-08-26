---
name: EcoMD Discovery Loop topic cycle 4
description: Narrow shared-capital quote-integrity trilemma proved but failed-closed as an exact escrow and invariant-confluence reduction; no topic card.
type: project
---

# EcoMD Discovery Loop topic cycle 4 — shared-capital trilemma

The strongest cycle-3 near miss was narrowed to one theorem residual before any outcome or
implementation work. The formal result is
`papers/proposal/ecomd_discovery_loop_topic_cycle_4_shared_capital_trilemma_result_2026-08-25.md`.

For one conserved balance, three properties cannot all hold:

1. displayed locally executable commitments across markets exceed the balance;
2. every displayed quote remains strongly executable; and
3. distinct markets commit takes without shared coordination.

The two-market proof is immediate: with balance one and a one-unit offer in each market,
both concurrent decrements are locally valid but their merge overspends. A safe mechanism
must serialize/global-lock, partition escrow rights whose sum is at most the balance, or let
one quote fail/remove/rollback. Price and time priority only select the winner after
coordination; they do not change resource safety.

The result is valid but not new. It is exactly the bounded-counter non-confluence covered by
Bailis et al.'s necessary-and-sufficient invariant-confluence framework, with O'Neil's escrow
transactions and bounded-counter CRDTs as the established rights-partition remedy. Manifest
and Mangrove occupy different engineering points in that design space.

Status is failed-closed at hostile T0 1--6%, point 3%. Do not relabel the corollary as a
liquidity CAP theorem. Reopen only for a quantitative price/priority-dependent result that is
not implied by invariant preservation or escrow, survives token/order refinement, and has
two same-estimand native mechanisms plus complete attempted-transaction exposure. No topic
card, sandbox, outcomes, chain query, data action, outreach, EcoMD edit or compute is
authorized.
