# Cross-family synthesis: conservation-constraint attribution audit (all four families)

Date: 2026-08-29 (updated after family C)

Status: **synthesis of all four confirmatory families under the D0 and family-M freezes;
family C triggered the freeze-and-review clause; its mechanism review (contraction boundary
test) runs as an explicitly-exploratory branch. All comparisons are same-cell matched-pair.**

## The audited practice

Embedding exact invariants (conservation laws in physical surrogates; accounting identities /
no-arbitrage and martingale constraints in financial models) in learned simulators is a
widespread, citation-dense practice. **No prior work separates the constraint's contribution
from the output-parameterization change that typically accompanies it, at matched controls,
with an error decomposition.**

## The four findings

1. **The constraint never matters — in either direction.** In every adjudicated setting of
   every family (42 settings), the exactly-enforcing `hard` arm is statistically
   indistinguishable from its parameterization twin `free_res` on conserving-channel OOD
   error — including family C, where the twin is the *losing* arm. The constraint's entire
   effect is exact zeroing of invariant violations. Credit for OOD accuracy (positive in
   A/B/M, negative in C) belongs to the parameterization alone.
2. **The parameterization effect is dominant and its sign is predictable.** Near-identity
   dynamics (A, B, M: one-step maps close to the identity) favor residual output by
   12.7–5225×; a strongly contractive operator (C: high-wavenumber content annihilated in one
   step) *inverts* the effect — absolute output wins by 4.6–6.3×, because the residual head
   must learn a large cancelling update that extrapolates poorly off-support. Boundary
   prediction verified by single-factor manipulation (ν sweep): mild contraction keeps the
   residual advantage, strong contraction flips it.
3. **Strong soft penalties are dominated, with damage scaling in target stochasticity.**
   Deterministic PDE targets: +15–33% conserving-error inflation, no drift benefit (A, B, C).
   Stochastic market targets: +100–370% inflation with genuine laundering (M) — the
   conjunction holds only there.
4. **Post-hoc projection implements the decoupling theorem exactly** (0.00% deviation in
   46/46 settings) — the audit's built-in negative control.

## Scoreboard

| Family | Learner | Regime | Winner | Attribution | Laundering | Decoupling |
|---|---|---|---|---|---|---|
| A | MLP | 3 PDEs, near-identity | free_res | PASS 6/6 | 2/6; dominated | exact |
| B | 1D U-Net | same + amp/res-shift | free_res | PASS 18/18 | fail; dominated | exact 18/18 |
| C | 2D U-Net | contractive 2D ad-diff | **free** | **inverted** | fail; dominated | exact |
| M | MLP | CDA market, stochastic | free_res | PASS (140×) | **PASS (4.7×)** | exact |
| E (review) | MLP | ν-sweep mechanism test | **flip at ν=10** (dose-response: 0.02→free_res 100×; 2.0→free_res 1.5×; 10.0→free 1.9×) | exploratory | — | exact |

## Practical prescription (paper takeaway)

- Enforce exact invariants **architecturally on the parameterization you already chose** — it
  is free (never changes accuracy) and exact.
- **Choose the parameterization by the map's distance from identity** (near-identity →
  residual; contractive → absolute), not by folklore.
- **No strong soft penalties**; damage grows with target stochasticity.
- **Report the decomposition, not the constraint residual** (M's 4.7× inflation is invisible
  to the constraint metric).

## What is not claimed

No claim about market physics or conservation laws determining dynamics (Cycle-7 closure
untouched); no field-data or transfer claims (Cycle-16 closure untouched); nonlinear
invariants (energy-type) untested; statements concern exact linear invariants under the
frozen probes.
