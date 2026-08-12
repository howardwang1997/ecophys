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

## 10. WP0 audit outcome (appended 2026-08-13; frozen sections above unchanged)

The completed rules/data/prior-art audit is
`research/theory_exploration/market_rule_feedback_audit_v5.md`. Its decision is:

- G0 `PASS`: the regular annual clock, statutory cutoffs, tick grid and exception classes are specified in
  official rules. The 2023 amendment changed application from 1 April to the first Monday of April.
- D0 `CONDITIONAL_PASS`: ESMA provides reusable annual 2017--2025 records; FCA provides 2021--2026 full-file
  history through a documented API. A licence-safe price/corporate-action source and the UK API/OGL archive are
  still required before real analysis.
- I0 `GENERATED_ONLY`: blind `rows=0` counts show support around all cutoffs, but mixed nine-month exposure,
  discrete ADNT, shared RTS 28 boundaries and price-dependent zero first stages require generated attacks.
- N0 is `NCS_FEASIBILITY_CANDIDATE` and NMI `NO_SURVIVOR`. AMF already named the circular relationship, FCA
  already estimated one-step market-quality effects, and standard robust/multi-cutoff/discrete RD occupies the
  method. No direct repeated-cycle next-ADNT discontinuity was found in the bounded search.

Cutoff 10 is the clean primary candidate. Cutoff 600 is the required independent second candidate only when a
date-correct price establishes a nonzero tick contrast. Cutoffs 80 and 2,000 coincide with RTS 28 reporting-group
boundaries and are sensitivity analyses; 9,000 is tertiary and price-qualified. Calendar-year `N_(y+1)` contains
roughly nine treated months and must be described as the next-controller-input ITT, not a full-year structural tick
elasticity.

One protocol deviation is permanent: a schema-discovery query returned one 2021 value for ISIN `ROROCEACNOR1`.
That ISIN is excluded from every future split, plot and example. No adjacent year or outcome pair was opened, and
all subsequent metadata queries returned counts only. The deviation does not authorize other values.

The only newly authorized work is a separately frozen, pushed, CPU-only generated identification preflight. All
FITRS ZIPs, real prices, UK instrument records, remote hosts and GPUs remain locked.

## 11. Experiment 147 preregistration and implementation state (appended 2026-08-13)

Experiment 147 was preregistered and pushed at `3febf132d` before its estimator module, tests, runner, freeze or
generated result existed. Its immutable contract is
`experiments/147_generated_market_rule_feedback_rd/PREREGISTRATION.md`: 300 replicates per cell, ten gated null
cells, six gated `sigma=0.10` effect cells, six descriptive `sigma=0.20` cells, three stochastic design diagnostics
and deterministic shared-rule/tick-first-stage guards. It uses official `rdrobust==2.0.0` HC3/CR3 robust
bias-corrected inference plus a declared fixed-design curvature oracle. Passing is code/design feasibility only.

The implementation has 13 deterministic micro-tests covering stream stability, standard/regression-to-mean/
clustered generators, HC3 and CR3 extraction, the bias-bound oracle, sorting/attrition/mass-point diagnostics,
the full 19-by-6 statutory tick table, Wilson summaries, gate aggregation and fail-closed network behavior. Focused
pytest, Ruff and strict mypy pass. No Monte Carlo cell has run. The formal runner still requires a separately
committed and pushed `FREEZE.yaml`; it refuses dirty trees, hash/version mismatches, existing output, exposed GPUs,
socket activity or resource-limit violations. Its four-process ceiling is one controller plus three single-threaded
workers. Real values, remote workers and GPUs remain locked.

## 12. Experiment 147 execution decision (appended 2026-08-13)

The implementation freeze was pushed at `2d14357fb`. The one authorized formal attempt then stopped inside the
`ProcessPoolExecutor` constructor because the managed sandbox denied `os.sysconf("SC_SEM_NSEMS_MAX")`. This was
before any worker, generated panel, `_fit_task` call or `rdrobust` fit; the raw output is absent. Experiment 147 is
therefore closed as `IMPLEMENTATION_OR_SPEC_FAILURE`, not a statistical preflight failure. Full evidence is
`experiments/147_generated_market_rule_feedback_rd/FORMAL_ATTEMPT_FAILURE.md`.

The only admissible continuation is Experiment 148, preregistered and pushed before its runner exists. It may
replace the process pool with a serial in-process backend, but must reuse the exact Experiment 147 scientific
configuration and frozen random streams, DGPs, estimator options, gates and failure mappings. Experiment 147 may
not be rerun. Market values, remote workers and GPUs remain locked.

## 13. Experiment 148 serial-repair state (appended 2026-08-13)

Experiment 148 was preregistered and pushed at `9d05559de` before its runner, focused test, freeze or result
existed. It references Experiment 147's configuration, preregistration, research module, pure runner helpers and
failure record by SHA256. The only allowed change is serial in-process scheduling: one controller, zero workers,
one numerical thread, no executor, multiprocessing, thread pool, subprocess worker, semaphore or task queue.

The implementation computes and verifies exactly 6,600 primary-fit tasks and 1,800 oracle tasks, preserves cell
then replicate order, and checks that every task stays in the controller PID. Five repeatable deterministic tests
pass, as do Ruff and strict mypy. One pre-freeze adapter probe executed a single frozen `smooth_null` task and read
only its success/failure flags; it was removed from the repeatable suite and is not a formal result. The complete
300-replicate suite remains unrun. A separately pushed `FREEZE.yaml` is still required before the sole formal
attempt. Real data and remote/GPU compute remain locked.

## 14. Experiment 148 final decision (appended 2026-08-13)

Experiment 148 froze at `b396d40fc` and its sole formal serial run completed from that clean checkout. The raw
artifact is `experiments/148_generated_market_rule_feedback_rd_serial/artifacts/raw/preflight.json`, SHA256
`6b5f0ba9fd594c241a4e4977299d2e90a8c45371418b30acaaf6a27ba401532b`. The decision is
`GENERATED_RD_PREFLIGHT_FAIL`:

- 6,600/6,600 primary fits and 1,800/1,800 oracle constructions succeeded; all five deterministic/stochastic
  diagnostic guards passed and no fit or oracle failure occurred.
- Only 9/16 gated cells passed. At cutoff 10, the rounded null rejected 25/300 times (`8.33%`) with Wilson 95%
  upper bound `12.01%`, failing the frozen `<=8%` point and `<=11%` upper-bound requirements.
- Every `|tau|=0.05`, `sigma=0.10` effect cell failed the 80% power gate. Non-clustered power was
  `48.67%--56.33%`; clustered reinforcing power was `33.67%`.
- The run used one controller, zero workers, one numerical thread, about `0.02135` CPU core-hours and `0.1965 GB`
  peak RSS. It opened no market/FITRS/price/paid/sealed data, made no network call, contacted no remote host and
  used zero GPU-hours.

The failure is therefore about statistical identification at the blind metadata-supported sample scale, not
software instability and not evidence that the real feedback mechanism is absent. The preregistered stop rule
retires the current V5 design before any market outcome is opened. Experiment 148 may not be rerun, and the design
may not be rescued by changing seeds, relaxing gates, inspecting real signs, adding ordinary years post hoc,
buying data with the same independent-unit structure or adding GPUs. Re-entry requires a prospectively new
data/design opportunity with substantially denser independent cutoff support or a stronger exogenous first stage.
Final iteration decision: `V5_NO_SURVIVOR` for NMI and NCS.
