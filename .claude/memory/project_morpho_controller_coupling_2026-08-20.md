---
name: morpho-controller-coupling-2026-08-20
description: "Fresh AMBER T0 for conserved control pressure and signal shielding between Morpho vault allocators and stateful AdaptiveCurveIRMs."
metadata:
  node_type: memory
  type: project
---

# Morpho allocator--IRM coupling — 2026-08-20

This project starts after the Liquity D0 route closed and is not a rerun, provider repair or reuse of its observed
interval. The branch is `morpho-signal-shielding-feasibility-2026-08-20`. It also does not reopen the failed NCS
invariant-gradient route.

The candidate systems question is whether a supervisory allocation agent can suppress the error signals used by
local adaptive mechanisms while merely transporting, rather than removing, aggregate stress. For market `i`,
define `q_i=B_i-0.9 S_i`. A pure flow `F_ij` of supplied assets from `i` to `j` changes
`q_i` by `+0.9 F_ij` and `q_j` by `-0.9 F_ij`; total pressure is fixed at
`B_total-0.9 S_total`. The supply-weighted mean utilization error is therefore fixed. Exact utilization
equalisation attains the lower bound on maximum raw local error but leaves a common error whenever aggregate
utilization differs from 90%.

Away from hard bounds, Morpho's AdaptiveCurveIRM evolves the log rate anchor by the normalized utilization error.
When an allocator equalises utilization, every local error and log-rate increment is identical, so pairwise log
rate-anchor differences remain invariant. In graph language, differential modes inside an equalised connected
component are suppressed and one common adaptive mode remains. This is a useful deployed-mechanism lemma, not yet
a novel theorem; conservation, consensus, persistent excitation and integral windup are established prior art.

Official source audit:

- reallocation bot commit `564eafde188ae81b1439b01da9c356d0964dbb35`;
- IRM commit `7f32443bf6dd1e9d1cf9afd51a8d626b2f38267f`;
- the bot retains `EquilizeUtilizations` and `ApyRange` implementations;
- the audited checked-in config selects `ApyRange` on Ethereum and Base, with explicit vault/market bands;
- the bot reads `rateAtTarget`, so the current policy is state-aware rather than a simple utilization equalizer.

The nearest direct DeFi work is Bertucci et al. on optimal/PID IRMs, AgileRate on adaptive rate control, and
Chitra's 2026 curation model on dynamic pricing and resource allocation. Chitra directly covers Morpho-like
multi-market curation but not AdaptiveCurveIRM, `rateAtTarget`, PID or allocator--IRM coupling. Classic adaptive
control already covers lack of parameter convergence without persistent excitation. A high-impact claim must
therefore be a prospective field result about interaction modes and pressure displacement, not the identity.

T0 is complete. The clean formal run from pushed commit `7bb63f2d811de1211cdd60c5eed69e8ca7b52240`
passed all seven gates in 10,000 trials; canonical result SHA-256 is
`91a4738beff17da6d16972faa1ddcbc844a76643678aec300ec9c6ca0cc3f64e`. Maximum normalized continuity/global
residuals are `2.65e-16`/`3.78e-16`, equalisation spread is `2.22e-16`, differential-memory residual is
`2.66e-15`, and 9,846 trials have a nonzero common-mode update. This is a PASS for implementation only; novelty,
field support and venue fit remain AMBER.

No historical reallocation event, amount, rate, utilization history, price, liquidation or outcome has been
queried. No EcoMD or GPU job is authorized.

D0A is frozen before current allocator-role queries in
`papers/proposal/morpho_controller_coupling_d0a_freeze_2026-08-20.md`. Primary operator sources support three
fixed documentary anchors: Steakhouse USDC (`0xBEEF017…`), Gauntlet USDC Prime (`0xdd0f28…`) and sky.money USDS
Flagship (`0xE15fcC…`). The first describes an off-chain/proprietary reallocation bot, the second an automatic
optimization engine, and the third an allocator bot under exposure constraints. These are operator self-reports,
not strategy-code proofs. The official open bot's vault-specific config cannot prove deployment because its EOA
key and vault whitelist are environment secrets.

D0A requires each fixed anchor to have exactly one current non-public explicit allocator after excluding the
official Public Allocator, all three private addresses to differ, and all documentary bindings to remain fixed.
Any failure closes the field route before history. A pass authorizes only a separately frozen D0B for event
identity/support: at least 12 active edges, 300 complete reallocations, 90 days, 50 multi-non-idle-market
transactions and receipt/finalized-index equality. Periodicity and repeated senders never establish bot identity.
