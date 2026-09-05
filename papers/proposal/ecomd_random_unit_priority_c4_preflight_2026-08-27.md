# C4 preflight: payoff scale, variance-anchor plan, and cost-feasibility envelope

Date: 2026-08-27

Status: **outcome-blind preflight under the reopened C4; no sample size frozen; no participant,
platform, ethics, or outreach authority created**

This preflight executes the next step ordered by
`ecomd_random_unit_priority_scientific_repair_2026-08-27.md` against the six requirements of
`ecomd_random_unit_priority_precision_contract_v2_2026-08-27.md`. Numbers below are planning
values computed with `statsmodels.stats.power.TTestIndPower` (superiority, two-sided 5%) and a
normal-approximation TOST assurance at true difference zero (90% interval, two one-sided 5%
tests).

## 1. Payoff-scale framework (freeze candidate, not yet frozen)

Module-A race with `N=8` participants per session, each resting one unit at the common price;
the taker order demands `k=4` units after all units rest.

- **Latency endowment:** 100 tokens per incentivized race round; tokens convert at
  `c = $0.10/token` (full endowment = $10/round).
- **Arrival mapping:** arrival rank is decreasing in token spend; ties broken by an announced
  uniform draw. Under FIFO, ranks 1--4 of 8 fill; under random-unit allocation, execution is a
  uniform draw without replacement (probability `4/8 = 0.5` regardless of rank).
- **Filled-unit prize:** induced surplus `V = $2.00` per filled unit.
- **Welfare reading of `δ = 0.10`:** ten tokens = $1.00, which equals the entire marginal speed
  rent available to a median-ranked participant under FIFO
  (`(1 - 0.5) · V = $1.00`). The SESOI is therefore "the whole queue rent", not a small
  fraction of it. This is conservative against the closest empirical magnitude anchor:
  [Khapko--Zoican (2021)](https://doi.org/10.1016/j.finmar.2020.100601) find asymmetric speed
  bumps reduce speed investment by only ~20% (one SD of bump magnitude: a further 8.33%), while
  random-unit allocation removes the *entire* return to speed, so a true effect at or above the
  full FIFO rent share is the theory-coherent expectation.

Freezing this schedule (including round count and endowment replenishment) is a prerequisite for
any registration; the numbers above are the freeze candidate.

## 2. Variance anchor (the binding open input)

No published source identifies the between-session SD `σ_s` of a first-round investment share
under between-session rule assignment:

- Khapko--Zoican: 56 participants, 18 groups, *repeated within-group* treatments; establishes
  feasibility and effect magnitude, not `σ_s` for this estimand.
- del Rio-Chanona--Pangallo--Hommes (arXiv:2505.07457): LLM agents, no human session variance.
- Classical institution experiments (Aldrich--López Vargas and predecessors): different
  endpoints and institution changes; transportability judged poor.

Lawful anchor plan (in order):

1. **Human internal pilot** (requires ethics/site authority, which is *not* yet requested):
   `n₀ = 6` sessions per arm, variance-only, with the analysis plan and treatment assignment
   frozen before any outcome inspection; the pilot estimate updates `σ_s` and triggers the stop
   rule below. Robot-pilot variance cannot calibrate human precision.
2. If no human pilot is authorized, the study must be planned at the conservative end of the
   envelope (`σ_s = 0.15`), which the ceiling does not support (Section 4); C4 then stays open
   and no two-site feasibility claim may be made.

## 3. Planning envelope (superiority 80% / 90% per arm; TOST assurance at Δ=0)

Per-participant cost model: 8 participants × ~$40 (show-up + expected earnings) ≈ $320/session,
inflated 15% for whole-session attrition and platform failures (≈ $368/session).

| `σ_s` | `d=δ/σ_s` | 80%/arm | 90%/arm | TOST 80%/arm | cost/site (80%) |
|---:|---:|---:|---:|---:|---:|
| 0.08 | 1.25 | 12 | 15 | 8 | $8,832 |
| 0.10 | 1.00 | 17 | 23 | 13 | $12,512 |
| 0.12 | 0.83 | 24 | 32 | 18 | $17,664 |
| 0.13 | 0.77 | 28 | 37 | 21 | $20,608 |
| 0.15 | 0.67 | 37 | 49 | 28 | $27,232 |
| 0.20 | 0.50 | 64 | 86 | 50 | $47,104 |

Pooling two independently governed sites (site fixed effects, pre-registered) doubles per-arm
sessions: at `σ_s = 0.12` the pooled 80% detectable effect is `d ≈ 0.58`; the per-site
assurance requirement from the precision contract still applies to each site separately.

## 4. Feasibility verdict against the USD 20,000/site ceiling

- **Superiority at 80% power per site: feasible iff `σ_s ≤ 0.12`** (24 sessions/arm,
  $17,664). At `σ_s = 0.13` the site cost is already $20,608 > ceiling.
- **TOST assurance (equivalence) per site: feasible only if `σ_s ≤ 0.12`** (18 sessions/arm);
  at `σ_s = 0.15` TOST needs 28 sessions/arm ≈ $20,736, at the ceiling boundary, and
  superiority is already infeasible there.
- Sensitivity to the cost model: the verdict inverts if per-participant cost exceeds ~$41 at
  `σ_s = 0.12`.

**Stop rule (frozen):** if the lawful anchor yields `σ̂_s > 0.12`, or the payoff freeze makes
`δ = 0.10` worth less than one marginal FIFO speed rent, C4 terminates as
*not executable under the ceiling*. The margin is never enlarged to fit the budget, and Module-B
secondaries never rescue the primary.

## 5. Requirements ledger

| Precision-contract requirement | Status |
|---|---|
| 1. Endowment/cost/arrival/prize freeze with welfare `δ` | Candidate schedule supplied; final freeze pending platform economics |
| 2. Lawful between-session variance anchor | Open; human internal pilot plan specified, requires ethics/site authority |
| 3. Attrition/platform-failure inflation | Included (15%, whole-session) |
| 4. Per-site superiority and TOST assurance | Computed (Section 3) |
| 5. Cost comparison vs USD 20,000/site ceiling | Feasible iff `σ_s ≤ 0.12` |
| 6. Stop rule | Frozen (Section 4) |

C4 therefore remains **open**, now with a sharp, quantitative go/no-go input: the variance
anchor. No A-1/A0 work is authorized by this preflight.
