# Endogenous market-rule feedback v5 — multi-year dynamics of data-dependent tick grids

**Frozen:** 2026-08-13

**Branch:** `endogenous-market-rule-feedback-v5`

**Base:** `main@268050126fda8276797f20fbca2f61bb112ca4c1`

**Inherited decisions:** v1 NMI `NO_SURVIVOR`; v2 NMI `NMI_NO_SURVIVOR`; v2 NCS
`NCS_C0_FAIL_IDENTIFICATION`; v3 `V3_NO_SURVIVOR`; v4 `V4_NO_SURVIVOR`

**Initial resource boundary:** primary literature, regulations and official data-catalog metadata only; <=30 Mac
CPU core-hours; 0 GPU-hours; no V100/RTX2060 contact; no instrument-level ADNT, price, spread, depth, order or
trade outcomes; no purchase

**Relationship to earlier Plan v5:** this is theory/topic iteration v5 and is unrelated to the archived
`plan_v5_interventional_market_world.md`/exp141 generated feasibility project. It does not relabel that project or
its results. Until the gates below pass, `plan_v4_ncs.md` remains the archival plan of record and this document is
only a bounded successor-topic audit.

## 1. Scientific question and claim boundary

MiFID-style regimes assign an instrument to a discrete tick-size liquidity band from its measured average daily
number of transactions (ADNT). The assigned tick grid can then change trading frequency, which becomes the running
variable for the next annual assignment. The candidate real-market mechanism is therefore the closed loop

\[
N_{i,y}\xrightarrow{b(\cdot)} B_{i,y+1}
\xrightarrow{\Delta(P,B)} \text{market dynamics}_{i,y+1}
\longrightarrow N_{i,y+1},
\]

where `N` is ADNT, `B` is the statutory liquidity band and `Delta` is the applicable tick. The question is whether
this data-dependent rule produces a replicated discontinuity in its own next-period input, yielding reinforcing
band persistence, corrective switching or no detectable feedback.

The candidate is not:

- the first tick-size regime, endogenous tick assignment or threshold rule;
- the first finding that tick size changes spreads, depth, volume, order size or cancellation behavior;
- the first observation that tick size and transaction count have a circular relationship;
- a universal physical law, a new regression-discontinuity design or evidence about latent trader beliefs; or
- an EcoMD validation study.

The possible NCS contribution is a real, multi-year, cross-jurisdiction computational-market finding: an
institutional controller measurably changes the future statistic that controls its own next setting. NMI is a
separate and much less likely route, admitted only if identification requires a new method or theorem that cannot
be reduced to multi-cutoff/fuzzy/dynamic regression discontinuity, threshold autoregression, panel event studies or
Markov jump systems.

## 2. Frozen estimands and scientific outcomes

For statutory cutoff `c_k`, define the centered running variable and next-period response

\[
X_{i,y,k}=\log(N_{i,y}/c_k),\qquad
Y^{(h)}_{i,y,k}=\log(N_{i,y+h}/c_k),\quad h\in\{1,2\}.
\]

Only observations for which `c_k` is the nearest applicable cutoff enter its local window. Let `Z=1[X>=0]`
denote assignment to the higher-liquidity column. The primary intent-to-treat discontinuity is

\[
\tau^{(1)}_k=
\lim_{x\downarrow 0}\mathbb E[Y^{(1)}\mid X=x]
-\lim_{x\uparrow 0}\mathbb E[Y^{(1)}\mid X=x].
\]

Here `tau > 0` is reinforcing feedback: the higher-band assignment raises the next running variable and makes the
same side of the threshold more persistent. `tau < 0` is corrective feedback. `tau = 0` means no locally
detectable loop at the declared resolution. The primary estimand is assignment ITT; an effect per log tick change
is secondary and is reported only when a preregistered reference-price construction gives a strong, nonzero first
stage.

Secondary outcomes, fixed before values, are:

1. the discontinuity in `Pr(N_{y+1} >= c_k)`;
2. the two-year policy-path discontinuity `tau^(2)`, explicitly not interpreted as a direct tick effect;
3. transition asymmetry between remaining above and returning below the cutoff; and
4. actual effective-tick first stage using the statutory table and a legally reusable, date-correct price.

“Lock-in” may be used only if the one-year ADNT discontinuity and same-side transition probability are both
positive, replicate across the sealed jurisdiction, survive every identification gate and have no dominant
year/cutoff. “Oscillation” requires a negative one-year discontinuity plus a prospectively specified alternating
two-year transition signature in both jurisdictions. Otherwise report reinforcing, corrective or undetected
feedback without dynamical-systems rhetoric.

## 3. Competing explanations

The analysis must distinguish the rule loop from:

- regression to the mean in an annually estimated running variable;
- smooth firm-specific liquidity growth or decline;
- manipulation, heaping or sorting near ADNT cutoffs;
- entry, delisting, identifier changes, venue migration and corporate actions;
- price-row changes that alter the effective tick without a liquidity-band change;
- simultaneous transparency, block-size or market-structure rules sharing a cutoff or application date;
- changes in the most relevant market, reporting coverage, measurement definition or Brexit jurisdiction;
- pandemic/event-year shocks, index reconstitutions and market-wide trends; and
- post-hoc bandwidth, cutoff, cohort, price or outcome selection.

A discontinuity rejects local smoothness only under the declared RD assumptions. It does not identify strategic
adaptation or a unique micro-level channel.

## 4. Pre-outcome gates

### G0 — exact legal mechanism

Pass only if official rules and technical documentation fix, by application period, the ADNT measurement window,
cutoffs, band assignment, price rows, exceptional updates and affected instruments. Every rule revision gets a
versioned machine-readable table. A regulator's interpretation is evidence for the rule, not novelty.

### D0 — free longitudinal data contract

Pass only if official public files provide stable instrument identifiers, ADNT and application dates for at least
five consecutive EU assignment cycles and at least three UK cycles, with terms permitting reproducible derived
research artifacts. The complete filename/date/schema inventory and hashes must be frozen before any
instrument-level value is parsed.

Development is EU/EEA through the application cycle ending in 2023. Later EU cycles are temporal validation.
Instrument-level UK cycles are sealed external replication and must not be parsed until code, signs, bandwidth
rules and exclusions are committed. Aggregate values already quoted by regulators are contamination metadata and
must be listed, not treated as our results. A future 2027 UK cycle may be prospective confirmation but is not
required to make a current feasibility decision.

### I0 — local identification feasibility

Pass only if metadata and rules show at least two usable statutory cutoffs with a real effective-tick contrast,
adequate instrument counts on both sides in multiple years, no coincident deterministic treatment at the same
cutoff and a feasible identifier/corporate-action history. Counts may be obtained from catalogs or schema queries;
ADNT and outcome values remain unopened until preregistration.

The mandatory design oracle is robust bias-corrected local-linear RD with year and cutoff strata. Polynomial global
fits are forbidden. Fixed attacks include density/sorting tests, predetermined-covariate continuity, placebo
cutoffs, donut exclusions, bandwidth sensitivity, leave-one-year/cutoff-out estimates and cluster-aware
uncertainty. Regression-to-the-mean simulations must reproduce the exact observation schedule before real values.

### N0 — nearest-result gate

Pass for NCS only if no primary study already estimates the discontinuity from annual band assignment to next
year's ADNT/next assignment across repeated cycles, and the free data contract permits a jurisdictional
replication. Studies of one reclassification's effect on spreads/depth/orders are mandatory baselines but do not
alone close this estimand.

Pass for NMI only if a formal card supplies assumptions, estimand, theorem, estimator and a symbolic difference
from standard multi-cutoff/fuzzy/dynamic RD and threshold-system identification. “Endogenous policy feedback” is
not a new method name.

Automation may return `NCS_FEASIBILITY_CANDIDATE`, `LOWER_VENUE_ONLY` or a retirement state. It may never issue a
novelty `PASS`.

## 5. Frozen evidence gates after D0/I0/N0

Before real values, create a separate preregistration and immutable analysis artifact. The primary Nature-scale
effect floor is `|tau^(1)| >= 0.05` log ADNT, approximately a five-percent local shift. Advancement requires:

1. the development pooled robust 95% confidence interval excludes zero and the estimate exceeds the effect floor;
2. at least 80% of estimable leave-one-year and leave-one-cutoff estimates retain the same sign;
3. no single year or cutoff contributes more than 40% of effective weight;
4. density, continuity, placebo, donut and bandwidth attacks do not reverse the sign or reveal a deterministic
   confound;
5. the sealed UK estimate has the same sign, its robust 95% interval excludes zero and `|tau^(1)| >= 0.05`;
6. the transition-probability discontinuity has the direction required by the chosen reinforcing/corrective label;
7. the conclusion survives stable-identifier, incumbent-only and documented corporate-action exclusions; and
8. all exclusions, weak first stages and unestimable cutoff-years are reported.

If development misses the floor or identification checks fail, do not open the sealed UK values. If UK fails,
the result is development-only and cannot support NCS. A smaller, heterogeneous or one-jurisdiction effect may be
reported internally or routed to a specialist venue but may not be narratively upgraded.

## 6. Work packages

### WP0 — rules, prior art and official catalog audit

- Version the EU/UK rule map and exceptional-update semantics.
- Search exact next-running-variable, annual transition, state dependence, persistence, hysteresis and chattering
  estimands, not only “tick-size effects.”
- Inventory official historical files, schemas, terms, identifiers and cycle coverage without parsing values.
- Produce an explicit nearest-result/equation table and a D0/I0/N0 decision.

### WP1 — generated identification preflight

Only after WP0 survives and its preregistration is pushed:

- generate smooth no-effect, reinforcing, corrective, sorting, regression-to-mean and coincident-rule cases;
- verify estimand signs, interval coverage, false-positive control and failure diagnostics;
- test identifier attrition, discrete running-variable support and weak/zero tick first stages;
- freeze schemas, manifests, hashes, exclusion reasons and sealed-jurisdiction guards.

Generated success validates code and the design boundary only. It is not market evidence or method novelty.

### WP2 — official-panel development and temporal validation

- Parse only frozen EU development files first.
- Run the committed primary and attacks without bandwidth or cutoff tuning.
- Open EU temporal validation only after the development report is committed.
- Stop before UK if development or identification gates fail.

### WP3 — sealed external replication

- Verify artifact hash and code immutability before unlocking UK instrument-level values.
- Run one scripted replication with no scientific hyperparameter changes.
- Treat FCA's published 2024 spread/depth/order results as prior context, not confirmation of the ADNT feedback
  estimand.

### WP4 — mechanism and policy consequences

Only after replication:

- estimate a transparent threshold-controller model and compare its transition distribution with a no-feedback
  counterfactual;
- quantify how much observed band persistence/switching is attributable to the local rule effect, with uncertainty;
- use EcoMD only if an independently validated observation bridge can implement the statutory assignment and
  reproduce the identified local estimand. EcoMD cannot create the empirical result;
- preregister prospective UK 2027 and, only if the rule survives review and implementation, U.S. post-2027 tests.

### WP5 — paper route

- NCS main: real closed-loop law, repeated-cycle identification, external replication, transparent computation and
  policy/dynamics interpretation.
- NMI conditional: a genuinely new transferable threshold-feedback estimator/theorem validated outside markets.
- Specialist fallback: careful multi-year market-microstructure application without Nature-scale replication or
  method novelty.

## 7. Data requirements

### T0 — authorized now

- EU delegated regulations, ESMA/FCA technical instructions, official data catalogs, schemas, legal notices and
  application calendars.
- Primary papers/preprints and metadata-only repository pages.
- No instrument-level values or bulk downloads.

### T1 — free feasibility after gates and preregistration

- Official annual FITRS/FCA instrument-level ADNT result files with ISIN, publication/application dates and most
  relevant market fields.
- Versioned tick tables and rule exceptions.
- Legally reusable end-of-day prices and corporate-action/identifier mappings for effective-tick construction.
- EU development/temporal validation and a separately encrypted or access-guarded UK replication manifest.

### T2 — paper-scale expansion after free-data replication

- Exchange or regulator order/trade data for spread, depth, cancellation, trade-size and queue outcomes; free
  regulator access is preferred, paid L2 requires a separate budget/licence gate.
- Additional European venues/jurisdictions with stable identifiers and independently administered files.
- Prospective 2027 UK data; U.S. Rule 612 data only if the delayed rule is actually implemented and stable.

Every dataset needs source, download time, licence, raw hash, schema version, transformation hash and immutable
time/jurisdiction split. Public availability does not make a previously inspected result sealed.

## 8. Compute requirements

### T0 — authorized now

- Mac CPU <=30 core-hours for documents, catalog/schema validation and generated unit tests.
- 0 GPU-hours; no V100 or RTX2060 contact; no remote queue.

### T1 — free official-panel analysis

- 200--2,000 CPU core-hours for parsing, RD bandwidth/coverage calibration, clustering, placebo grids and bootstrap
  uncertainty.
- The CPU portions may run on the two V100 hosts or RTX2060 host after authorization, but GPUs should remain idle.
- Expected storage 10--200 GB depending on retained official history and price/corporate-action sources.

### T2 — replicated microstructure expansion

- 5,000--100,000 CPU core-hours and 1--20 TB raw/derived storage for multi-venue order/trade reconstruction.
- 0--1,000 V100-equivalent GPU-hours only if a learned observation or counterfactual model beats transparent
  baselines under preregistered transfer tests.
- Parallelize by jurisdiction/year/cutoff/bootstrap seed; do not use multi-GPU training when independent arrays are
  sufficient.

### T3 — conditional method or simulator confirmation

- 1,000--10,000 V100-equivalent GPU-hours and 50,000--500,000 CPU core-hours only after measured T2 scaling and a
  surviving scientific claim.
- Capacity may expand beyond the current two V100 32 GB cards and one RTX2060 to additional compatible GPU/CPU
  workers. H20 is excluded from all budgets and execution assumptions.
- More compute cannot repair a failed discontinuity, invalid running variable, absent replication or occupied
  claim.

## 9. Stop rules

- Freeze and push this document before instrument-level outcomes or generated estimator results.
- Retire immediately if the exact next-ADNT/next-band feedback estimand is already established across repeated
  cycles, official histories are not reproducibly obtainable, or cutoff assignment is confounded by another rule.
- Do not call ordinary state dependence “hysteresis,” or a one-year reversal “oscillation.”
- Do not choose thresholds, years, bandwidths, price rows or outcomes after seeing signs.
- Do not use FCA's 2024 one-step market-quality result as our replication.
- Do not contact the V100/RTX2060 workers until a separate experiment preregistration authorizes a job.
- If v5 fails, preserve it append-only and change the scientific object again; do not rescue it by making EcoMD
  the source of the phenomenon.
