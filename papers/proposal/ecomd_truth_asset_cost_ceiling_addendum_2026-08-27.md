# Cost-ceiling addendum: terminal closure of precondition C4

> **Terminal-pass conclusion withdrawn (2026-08-27):** USD 20,000/site remains a budget ceiling,
> but the superseded sample-size calculation does not establish feasibility. C4 is open under
> `ecomd_random_unit_priority_precision_contract_v2_2026-08-27.md`.

Date: 2026-08-27 (Session 21)

Companion to `ecomd_tie_priority_c4_precision_floor_2026-08-27.md`. The C4 gate was
conditionally passed pending a frozen cost ceiling (stop condition 3 of the capability-build
plan). Under the user's sequential execution instruction ("按顺序做"), the ceiling below is
frozen now; the user may override it in writing before any A-1 spend, and no spend occurs at
A-2.

## Frozen ceiling

**USD 20,000 per site, all-inclusive of participant payments** (show-up fees plus
performance earnings). Two sites: discovery and confirmation, each ≤ USD 20,000.

## Derivation (outcome-blind, published anchors only)

- Requirement from C4 at frozen defaults: 16 sessions per arm = **32 sessions per site**;
  8–12 paid participants per session (frozen design) = 256–384 participant-sessions per site.
- Published anchor: [Aldrich & López Vargas (2019)](https://doi.org/10.1007/s10683-019-09605-2)
  paid a **USD 7 show-up fee** plus performance earnings at 2 ECU = USD 1, in 12-trader
  sessions of eight 4-minute periods — the same architecture class as the frozen asset.
- Experimental-economics payment norms for 60–90 minute trading sessions with performance
  incentives commonly land at USD 20–40 per participant all-in; USD 20,000 / 384
  participant-sessions = **USD 52 per participant-session**, and USD 20,000 / 256 = USD 78,
  both above the anchor range. The ceiling therefore accommodates the C4 requirement with
  margin at either enrollment extreme.
- Not included in the ceiling (tracked separately): operator time, engineering time (already
  spent at A-2), ethics filing fees if any, and compute (local CPU; no GPU authorized).

## Terminal verdict

At ceiling = USD 20,000/site ≥ the C4 requirement's cost envelope, **precondition C4 passes
terminally**: 32 sessions per site (16 per arm) at σ = 2 ticks, MDE = 2 ticks, α = 0.05,
power = 0.8. If A-1 quotes exceed the ceiling, stop condition 3 fires and the design either
stops or returns to the user for a revised ceiling.

## Boundary

This addendum authorizes no spending, recruitment, or outreach. It freezes a number so that
stop condition 3 is mechanically checkable at A-1. All A-1 actions remain separately
unauthorized.
