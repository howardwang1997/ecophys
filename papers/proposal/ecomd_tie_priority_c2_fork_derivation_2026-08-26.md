# C2 fork derivation: exchangeable-tie invariance versus strategic queue-value response

> **Reinterpreted (2026-08-27):** Lemma 1 is now only the M0 aggregate-lumpability case and Lemma
> 2 only a restricted threshold-family comparative static. Neither identifies a binary strategic
> class or a universal depth sign; see `ecomd_random_unit_priority_thesis_v2_2026-08-27.md`.

Date: 2026-08-26 (Session 18)

Precondition C2 of the frozen treatment selection
(`ecomd_truth_asset_treatment_selection_audit_2026-08-26.md`), executed after C1
(`ecomd_tie_priority_c1_collision_manifest_2026-08-26.md`) passed. Paper and CPU-trivial
fixtures only; executable at `scripts/tie_priority_fork_fixtures.py` (deterministic, stdlib
only, fixed seed 20260826; mypy --strict and ruff clean).

## 1. The object

One continuous-double-auction grammar; the treatment varies only the allocation of an incoming
aggressive order among *equal-price resting orders* (the tie set): strict FIFO time priority
versus uniform random priority. Everything else — quotes, arrivals, cancellations, fees,
information — is arm-invariant by construction, so the tape grammar and the aggregate event
space are identical across arms.

## 2. Lemma 1 (pathwise aggregate invariance under exchangeable populations)

**Assumptions.** (A1) Order-level arrival and cancellation intensities may depend on the
aggregate book state (counts per level, spread, recent trades) but not on order identity or
age. (A2) Each resting order carries the same cancellation hazard; the cancellation victim is
uniform among resting orders (exchangeability). (A3) Arrival price distributions depend only on
the aggregate state. (A4) The allocation rule consumes from the tie set without feeding back
into any intensity.

**Statement.** Under A1–A4, for any pair of allocation rules R, R′ (including FIFO and
uniform random), there is a coupling under which the *aggregate* book process — best quotes,
per-level counts, event times, types and volumes — is pathwise identical across rules; only
the identity of filled orders, and hence trader-level inventories and payoffs, differs. Every
aggregate observable therefore has the same law under both rules.

**Proof sketch.** The aggregate process is a lumped chain whose generator uses only the
aggregate state. Induct on event times: each event's aggregate effect (level count ±1, quote
update) and its rate are measurable in the aggregate state alone; a fill decrements the
executed level by the executed quantity regardless of which member is chosen; a uniform
cancellation victim contributes the same aggregate decrement under every rule. Allocation
choice is measurable in a sigma-field the aggregate generator never queries, so the natural
coupling (shared clocks, shared aggregate-relevant draws, rule-dependent victim draws) makes
aggregate paths equal with probability one. ∎

**Failure channels (any breaks invariance — this is the experiment's point).** (i) age-dependent
cancellation hazards; (ii) trader heterogeneity (inventory, budget, attention); (iii) agents
conditioning on queue composition; (iv) strategic repositioning (cancel-and-replace to regain
priority, penny-jumping); (v) any response to the *perceived fairness* of the rule itself
([Perry & Zarsky 2014](https://ilr.law.uiowa.edu/sites/ilr.law.uiowa.edu/files/2023-01/Perry-Zarsky.pdf)
document FIFO fairness perceptions). Human populations plausibly violate all five; ZI
populations violate none.

## 3. Lemma 2 (depth sign in the threshold family)

Unit orders; fill events race an adverse-move event, ρ = λ_f/(λ_f+λ_a) ∈ (0,1) the chance a
fill event occurs first; makers pay quoting cost c per order and earn h per fill. Under FIFO a
joiner with n−1 orders ahead fills with probability ρⁿ; under random allocation with n at the
touch the marginal joiner's expected fill share is f_R(n) = (ρ/n)·Σ_{k=0}^{n−1} ρᵏ.

**Claim.** f_R(n) ≥ ρⁿ = f_F(n−1), with equality only at n = 1 or ρ → 1, because the
arithmetic mean of {ρᵏ} weakly exceeds its minimum term. Hence every threshold equilibrium
satisfies n*_R ≥ n*_F: within this canonical family, **randomized priority provably sustains
weakly deeper touch queues** (equal-share free-riding dominates back-of-queue rent decay).
Spread and repositioning directions are not pinned in this family and stay exploratory.

## 4. Fixtures (deterministic; seed 20260826)

**Fixture A — exchangeable ZI population (200k events).** One aggregate engine drives two
counterfactual identity worlds. Aggregates: 129,718 arrivals, 41,079 cancels, 71,935 fills,
mean spread 1.77 ticks, mean touch depth 6.59 — *identical across worlds by the coupling, as
Lemma 1 requires* (the implementation shares every aggregate-relevant draw). Identity level:
front(rank-0) minus back(rank≥1) fill-rate gap is 0.122 under FIFO versus 0.065 under random
allocation; the residual 0.065 is compositional (rank-0 arrivals occur in thinner books), so
the ≈0.057 differential isolates the priority channel. Interpretation: aggregate invariance
holds exactly while individual outcomes redistribute — H0 is non-vacuous but sharp.

**Fixture B — strategic threshold equilibria.** ρ = 0.625: n*_F = 6 vs n*_R = 33. ρ = 0.9:
n*_F = 28 vs n*_R = 179. Order-one depth response to the rule, in the provable direction of
Lemma 2.

## 5. Pre-registered fork for the laboratory asset

- **H0 (exchangeable-population invariance).** All aggregate session statistics of the frozen
  estimand vector — impact slopes, time-weighted spread, touch depth, cancel/replace
  intensity, volume-volatility covariance — are invariant across arms up to a pre-frozen
  equivalence band. Supports statistical-queue simulators for rule response; falsifies
  strategic extrapolation to rule changes.
- **H1 (strategic response).** At least one aggregate statistic moves beyond the band.
  Primary directional prediction (Lemma 2 family): **touch depth increases under randomized
  priority**. Secondary exploratory: spread, cancel/replace intensity, improve-rate; the
  arrival-rent channel predicts reduced early-arrival clustering under randomization.
- **Manipulation check (not discriminating):** the identity-level rank-fill differential
  collapses under random allocation.
- Both resolutions are informative: H0 validates a large simulator class and kills another;
  H1 with the Lemma-2 direction validates strategic (queue-value) simulators and directly
  motivates the simulator-prediction asset use — frozen simulators fitted on passive paths
  predicting a held-out assigned human-market response, the unoccupied gap identified by
  Cycle 16.

## 6. Scope and boundary

Fixtures are mechanism demonstrations, not calibrations; no claim about magnitudes in human
markets. In-silico execution-quality evidence for randomized priority is occupied by
Lim (SSRN 6574208); the proposal lane by Hersch (RSS) and Haeringer–Melton (RSD); this
derivation claims only the formal invariance null, the threshold-family depth sign, and the
laboratory fork. Nothing here creates topic status, a card, or any authorization; A-2 platform
qualification still requires explicit user authorization (C3) and the precision floor (C4).
No GPU use; fixtures are CPU-trivial by design and the protocol forbids GPU before active
status.
