# Family M (market): accounting-conservation attribution in learned CDA simulators

Date: 2026-08-28 (D-3 contract + D0 extension freeze, written before any market-family outcome)

Status: **child extension of the D0 freeze
`ecomd_constraint_attribution_audit_d0_freeze_2026-08-27.md` under the PI's blanket
authorization and explicit 2026-08-28 direction that the audit be applied to financial
markets. In-scope (simulated_markets), archetype `simulator_method`: analytic truth is a
constructed engine; no field-data claim, no participant work, no EcoMD codebase use.**

## Distinction from closed families (anti-relabel statement)

- Cycle 7 closed *market-native conservation laws as topic claims* ("transaction balances are
  bookkeeping, not dynamics"). Family M makes no physics claim about conservation determining
  market dynamics; it audits a **simulator-design practice** (adding accounting constraints to
  learned simulators) on constructed synthetic truth — the Cycle 7 closure is unaffected.
- Cycle 16 closed *simulator validity against field rule changes*. Family M makes no field or
  transfer claim; truth is self-generated.
- The frozen priority-rent route stays frozen and untouched.

## Native object and invariant

A synthetic continuous-double-auction market (Gode–Sunder-class zero-intelligence-plus agents
with heterogeneous induced values, price-time FIFO matching, exact settlement, fixed fee to a
fee account). Exact accounting invariants:

- `Σ_i inv_i = S₀` (shares are only transferred);
- `Σ_i cash_i + fee_account = C₀` (cash moves only through trades and fees).

Learned task: one-step transition of per-agent `(cash, inv)` and book features. Error vector
decomposed into the non-conserving component (deviations of `Σ`, i.e., invented/destroyed
shares or cash) and the conserving component (redistributive, zero-sum errors) — identical
decomposition mathematics to families A–C.

## Arms (identical to the frozen six)

`free` (absolute next-state), `free_res` (residual), `soft`/`soft_res` (λ ∈ {3, 30} penalty on
both Σ-violations), `hard` (residual + zero-sum projection of per-agent deltas — conservation
by construction), `projection` (post-hoc mean-error removal on `free`).

## Regime control (flatness analogue)

Training episodes mix agent-aggressiveness and imbalance regimes; the frozen OOD probes are
(i) a held-out high-imbalance regime (one-sided flow, underrepresented in training — the data-
flat direction), (ii) a volatility-shock regime, (iii) an in-support regime check. Regime
labels are part of the input features; OOD = feature values outside the training envelope.

## Frozen decision rules (inherited verbatim from the parent D0)

1. Attribution: |ΔOOD conserving_err(free vs free_res)| ≥ 2×|Δ(free_res vs hard)| with
   non-overlapping seed bands (rule evaluated per OOD probe; primary = high-imbalance).
2. Laundering: soft(λ) conserving error > free with reduced Σ-drift.
3. Decoupling control: projection ≡ free within 1%.
4. Matched-ID ±5% with non-overlap branch; capacity cells {hidden 64, 128} × {400, 800} epochs,
   5 seeds; budget cap 40 device-hours.

## Honest prior

The market invariant is bookkeeping (Cycle 7's finding), so the *constraint* side is expected
to matter even less than in physics; the parameterization side (residual next-state
prediction) is expected to dominate again. Scientific value: (a) cross-domain replication
strengthens the audit's claim from "physics simulators" to "learned simulators with exact
invariants, physical and financial"; (b) direct internal relevance to EcoMD's design (learned
market interactions without architectural accounting); (c) the practice being audited
(no-arbitrage/martingale-constrained market models) is established and citation-dense, with no
matched-parameterization attribution anywhere in its literature (checked 2026-08-28:
Cohen–Reisinger 2023; ARBITER 2025; martingale-constrained pricing frameworks).

## Authorized actions

Run on the authorized pool (generated data only; howard-pc first while the V100s finish
families B/C). No outreach, no participant work, no field-data claims, no EcoMD codebase
changes.
