# Precision contract v2: session-level latency investment

Date: 2026-08-27

Status: **C4 reopened; sensitivity analysis only, no frozen sample size**

This record supersedes the scientific use of
`ecomd_tie_priority_c4_precision_floor_2026-08-27.md` and
`ecomd_truth_asset_cost_ceiling_addendum_2026-08-27.md`. Those files remain historical
provenance. The USD 20,000/site ceiling remains a user budget boundary, but it no longer proves
that the experiment is adequately powered.

## Primary estimand and analysis unit

For session `s`, let `Y_s` be the mean across participants of first-incentivized-round latency
investment divided by the available latency endowment. The session is the assignment,
interference and analysis unit. Repeated participants and rounds do not manufacture additional
independent sample size.

The primary contrast is

`Δ = E[Y_s | random unit] - E[Y_s | FIFO]`.

Analysis uses a prespecified session-level regression with assignment-stratum indicators and a
heteroskedasticity-robust interval. The first-round contrast is untouched by own fill feedback.
Later rounds, participants and order events are secondary repeated observations only.

## Decision rule

Let `δ = 0.10` of the latency endowment be the provisional smallest effect of scientific interest.
The final payoff schedule must show that ten percentage points correspond to a meaningful expected
cost before `δ` can be frozen.

- **Evidence of a material decrease:** the two-sided 95% interval excludes zero in the negative
  direction and the point estimate is at most `-δ`.
- **Practical equivalence:** both one-sided 5% tests place the 90% interval wholly inside
  `[-δ, +δ]`.
- **Inconclusive:** every other interval configuration.

A nonsignificant difference is not equivalence. Module-B liquidity outcomes cannot rescue an
inconclusive primary result.

## Why the old count fails

The former calculation used a two-tick spread standard deviation and two-tick effect borrowed from
a larger institution change, even though the claimed theorem concerned depth. It then offered to
increase the MDE to fit the budget. That reverses the purpose of a precision floor.

For two independent arms, a two-sided 5% t test with 80% power and `n=16` sessions per arm detects
only approximately standardized `d=1.024` (`d=1.185` for 90% power). Those are very large
session-level effects.

The scale-free sensitivity below was computed with `statsmodels.stats.power.TTestIndPower`; counts
are per arm and rounded up:

| Standardized effect `d` | 80% power | 90% power |
|---:|---:|---:|
| 0.25 | 253 | 338 |
| 0.50 | 64 | 86 |
| 0.75 | 29 | 39 |
| 1.00 | 17 | 23 |

For the provisional raw effect `δ=0.10`, the implication depends entirely on the unknown
between-session standard deviation `σ_s`:

| `σ_s` | `d=δ/σ_s` | sessions/arm at 80% | sessions/arm at 90% |
|---:|---:|---:|---:|
| 0.10 | 1.00 | 17 | 23 |
| 0.15 | 0.67 | 37 | 49 |
| 0.20 | 0.50 | 64 | 86 |
| 0.25 | 0.40 | 100 | 133 |
| 0.30 | 0.33 | 143 | 191 |

These are superiority sensitivities, not an equivalence-power guarantee. TOST assurance and the
independent confirmation-site criterion must be computed after `σ_s`, attrition and the payoff
mapping are frozen.

[Khapko and Zoican (2021)](https://doi.org/10.1016/j.finmar.2020.100601) is the closest human
latency-investment design: 56 participants formed 18 interacting groups over repeated treatments.
Its participant/group/round clustered panel coefficients establish feasibility and economic scale,
but they do not identify the between-session variance for this new between-session allocation
treatment. Aldrich--López Vargas and broader institution experiments are even less transportable.

## Requirements for a new C4 decision

1. Freeze the latency endowment, cost curve, arrival-time mapping and prize so `δ=0.10` has a
   welfare interpretation.
2. Obtain a lawful relevant between-session variance anchor. A human internal pilot would require
   ethics and a new explicit authorization; robot variance cannot calibrate human precision.
3. Include whole-session attrition and platform-failure inflation.
4. Compute superiority and TOST assurance separately at each independently governed site.
5. Compare the resulting session and participant cost with the unchanged USD 20,000/site ceiling.
6. Stop if the ceiling cannot support the frozen scientifically meaningful margin; never enlarge
   the margin to make the budget pass.

Until all six are complete, C4 is **open**, A-1/A0 remain unauthorized, and no claim of executable
two-site feasibility is permitted.
