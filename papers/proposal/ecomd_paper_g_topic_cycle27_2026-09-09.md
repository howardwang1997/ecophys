# Paper G topic cycle 27 — Temporary carbon storage and path replication

**PRIVATE / INTERNAL — exploratory selection record, not public or confirmatory evidence.**

Date: 2026-09-09. Literature cutoff: 2026-09-09. One theory/mechanism
question, F1 quick-closed. No F2/F3, surviving program or machine card.
This is a compact source-led cycle, not a twelve-program sampling cycle.

## Question and source boundary

**G27-01:** Can a nonnegative portfolio of temporary carbon-storage
delivery contracts exactly compensate a short-lived emission's entire
temperature path, or does the permitted release schedule prevent this?

The native object is the delivered carbon stock over time. The action is
selection of quantities and release maturities from a declared contract
class. The rivals are exact replication through maturity diversification
and a residual caused by the class's delivery restrictions. An existence
result would specify a physical delivery target; an impossibility result
would identify which promise cannot be made. Neither establishes commercial
availability, lawful offset eligibility, cost efficiency or additionality.

The route registry contained no temporary-CDR/LWE formulation. This is
distinct from carbon-allowance inventory condensation and Cycle26 dispatch
emissions. No saturated parent is reopened and no re-entry trigger is issued.

Three retained primary anchors suffice for the stop:

- He et al., *Nature* 654, 391–397 (published 27 May 2026), define cumulative
  temperature compensation and explicitly discuss annual residuals and
  alternative release profiles. Their optimized two-parameter example is
  not a theorem about every possible storage portfolio.
  [Primary article](https://www.nature.com/articles/s41586-026-10607-3).
- Allen et al., *Environmental Research Letters* 16, 074009 (23 June 2021),
  derive linear warming equivalence by inverse impulse response and discuss
  corresponding offset obligations. Exactness is within the linear model.
  [Primary article](https://doi.org/10.1088/1748-9326/abfcf9).
- Powis, Oxford DPhil thesis, copyright 2023 and deposited 2 September 2025,
  pp.81–84, expressly discusses synthetic temporary-removal portfolios for
  LWE offsets. This is a direct conceptual collision, not evidence that an
  arbitrary finite contract menu delivers an exact hedge.
  [Repository record](https://ora.ox.ac.uk/objects/uuid%3A3a6b07c2-3709-4fb5-8ac3-1e525f57dcf1),
  [thesis text](https://fileserver-az.core.ac.uk/download/667871875.pdf).

No same-state disagreement between these sources was established. Broad
carbon finance, contracted durability, biochar and decay-model intake did
not become additional raw programs. Access scope is recorded separately
in the structured screen; this was not a full literature or proof audit.

## A. Exact delivery under an explicit idealized contract class

The following is our elementary paper-only fixture, **not an AR6 or
empirical methane calibration**. Time is in arbitrary consistent units;
radiative amplitude is normalized. Fix the CO2 atmospheric response and
short-lived forcing target as

\[
R(t)=\tfrac12+\tfrac12e^{-t},\qquad m(t)=e^{-3t/4},\quad t\ge0.
\]

One unit is removed at time zero. Its remaining stored stock is S(t),
with S(0)=1, S nonnegative and nonincreasing, and S(infinity)=0.
The nonnegative release density is f=-S'. No additional removals, short
positions, default or instantaneous release at time zero are permitted.
Initially available contracts may have arbitrarily large maturities;
there is no common hard expiry. A continuum of divisible contracts and
deterministic aggregate delivery are assumptions, not observed capabilities.

The cooling contribution in forcing units is B=R-R*f. Applying the same
causal temperature response h(t)=e^(-2t) to B and m gives exact temperature
matching if B=m. This convolution is injective on these causal functions,
since its Laplace transform is 1/(s+2).

Writing hats for Laplace transforms, integration by parts gives

\[
\widehat B=s\widehat R\widehat S,\qquad
\widehat R=\frac{s+1/2}{s(s+1)},\qquad
\widehat S=\frac{s+1}{(s+1/2)(s+3/4)}.
\]

Consequently an exact delivery schedule is

\[
S(t)=2e^{-t/2}-e^{-3t/4},\qquad
f(t)=e^{-t/2}-\tfrac34e^{-3t/4}.
\]

Both S and f are nonnegative; S decreases from one to zero and
integral(f)=2-1=1. Direct substitution gives B(t)=m(t). Equivalently,
allocate a fraction f(u)du to contracts releasing at maturity u. All
individual maturities are finite almost surely, but the portfolio has
unbounded maturity support. Expected duration is integral(S)=8/3.
This supplies an exact constructive truth fixture for the declared model.

The negative exponential coefficient in S is **not** a negative physical
holding. Nevertheless this S cannot be a positive mixture of constant-rate
exponential storage stocks: every such mixture is convex, whereas

\[
S''(0)=\tfrac12-\tfrac9{16}=-\tfrac1{16}.
\]

Thus freely selectable release maturities and positive mixtures of
memoryless decay contracts are different feasible classes. The latter
restriction has not been established as a binding market rule. This
elementary convexity observation is not a new physical universality claim
or a quantitative lower bound on approximate temperature matching.

## B. A common hard expiry changes exact feasibility

Keep R, m, initial quantity, temperature response and no-top-up rule fixed.
Now require every unit to be released by a finite T. Let U in [0,T] have
the portfolio's release distribution, including possible maturity atoms.
For t>T,

\[
B(t)=R(t)-\mathbb E[R(t-U)]
=\tfrac12e^{-t}\{1-\mathbb E[e^U]\}.
\]

This is strictly negative whenever some carbon is stored for positive
duration, while m(t)>0. Immediate release gives B=0 and also cannot match
m. Hence this contract class cannot replicate the entire temperature
path; injectivity of the shared response operator rules out concealing
the forcing mismatch through thermal smoothing.

The result does not rule out a finite evaluation-window hedge, useful
temporary cooling, overcompensation policies or contracts with replacement
removals. It establishes neither a practically important error magnitude
nor a finite-horizon pricing result. It uses the frozen linear toy, not
the full nonlinear carbon cycle. A's unbounded-support delivery and B's
hard expiry are not contradictory predictions for the same contract.

## Decision and retained value

**Close this formulation as an independent Paper G novelty claim.**
Inverse-response matching and the synthetic-portfolio proposal have
direct primary predecessors. The two exact diagnostics are elementary
consequences of linear convolution and a completed delivery contract.
Neither supplies an irreducible financial-market theorem, validated field
asset or publication-ready result. There is no reason for an F2/F3 audit
or computation after this hard stop.

Counts: **1 raw / 1 F1 / 0 F2 / 0 F3 / 0 cards**; two paper-only diagnostics.
Retain the constructive schedule, the convexity check and the hard-expiry
identity. Future evaluation must distinguish finite individual lifetimes
from a uniform maximum maturity and must specify whether top-ups are legal.
Re-entry needs an independently valuable result or qualified actual
delivery/control asset that removes the recorded blocker. Merely adding a
different decay family, optimizer, climate metric or carbon-market label
does not do so. No new forecast or authorization is created.

Formal ledger and long-term memory are updated. No target outcomes,
scientific implementation, solver, simulation, GPU work, account connection,
purchase, outreach, participants, publication, commit or push occurred.
