# Endogenous market-rule feedback v5 — WP0 audit

**Audited:** 2026-08-13

**Frozen parent:** `papers/proposal/plan_endogenous_market_rule_feedback_nmi_ncs_v5.md`

**Scope:** rules, primary literature, official schemas/licences and aggregate register queries only

**Decision:** `NCS_FEASIBILITY_CANDIDATE`; NMI `NO_SURVIVOR`; real values and all remote compute remain locked

## 1. Result in one paragraph

The candidate survives only as a bounded NCS feasibility study. RTS 11 creates a real feedback channel: calendar
year `y` ADNT assigns the liquidity column applied in the following April, the column changes the permitted price
grid, and trading under that grid contributes to calendar year `y+1` ADNT. ESMA's public register contains annual
share/depositary-receipt records for 2017--2025 and blind aggregate counts show support on both sides of every
statutory cutoff in every regular year checked. No primary study found in the exact-result search estimates the
annual assignment discontinuity in the next ADNT/next assignment across repeated cycles. This is not a new feedback
concept: AMF stated the circular tick--transaction-count relationship in 2018, and FCA already estimates one 2024
reclassification's effects on spreads, cancellation, depth and order behavior. It is also not an NMI method: robust,
multi-cutoff and discrete-running-variable RD are established. The next admissible action is therefore a separately
committed CPU-only generated identification preflight. Instrument values, the UK replication, workers and GPUs stay
closed.

## 2. Exact rule and observation clock

Let `N_y` be the published ADNT on the most relevant market calculated from trading in calendar year `y`. For a
regular incumbent share or depositary receipt, the rule is

\[
B_{y+1}=b(N_y),\qquad
\Delta_t=\Delta(P_t,B_{y+1}),
\]

with cutoffs `10`, `80`, `600`, `2,000` and `9,000` transactions per day. Before the 2023 amendment the annual
column applied from 1 April; from the first regular cycle after the amendment it applies from the first Monday of
April. The official result is published by 1 March. The date must be obtained from the applicable rule version and
file, never inferred from a generic fixed month.

The free next input is not a full-year treated outcome. Calendar-year `N_{y+1}` contains roughly January--March
under the old column and April--December under the column assigned by `N_y`:

\[
N_{y+1}=\frac{
  \sum_{t\in\mathrm{Jan:Mar}} n_t(B_y)
  +\sum_{t\in\mathrm{Apr:Dec}} n_t(B_{y+1})
}{D_{y+1}}.
\]

The frozen `tau^(1)` is consequently an assignment ITT on the actual next annual controller input, with about
nine months of exposure, not a twelve-month structural tick elasticity. It is likely attenuated relative to a full
exposure effect. `tau^(2)` also passes through a subsequent endogenous assignment and remains a policy-path
contrast, not a direct tick effect.

### Rule exceptions that require deterministic exclusions

- New instruments use an estimate and then a four-week calculation; they do not follow the regular annual rule.
- A competent authority may update the band after a corporate action.
- Shares whose highest-turnover venue is in a third country can receive an adjusted ADNT; current EU/UK rules also
  contain third-country tick derogations.
- If the most relevant market operates only an automated periodic-auction system, the lowest liquidity column is
  used instead of the ordinary assignment.
- Corrections and superseded records must be resolved by `(ISIN, reporting period, calculation time)` before a
  panel is formed.
- ETFs do not use share ADNT assignment and are excluded.

These are treatment-definition failures, not optional robustness filters.

## 3. Cutoff audit

| Cutoff | Column move | Tick contrast from the statutory table | Other deterministic boundary | Frozen role |
|---:|---|---|---|---|
| 10 | LB1 -> LB2 | Nonzero in every price row | None found in the audited rule set | Clean primary cutoff |
| 80 | LB2 -> LB3 | Nonzero in every price row | RTS 28 grouped annual execution reporting at 80 | Joint-rule sensitivity, not clean primary evidence |
| 600 | LB3 -> LB4 | Zero only for `P < 0.1`; nonzero otherwise | None found | Second primary candidate only with date-correct `P >= 0.1` |
| 2,000 | LB4 -> LB5 | Zero for `P < 0.2`; nonzero otherwise | RTS 28 grouped reporting at 2,000 | Exclude from primary pooling |
| 9,000 | LB5 -> LB6 | Zero for `P < 0.5`; nonzero otherwise | None found | Tertiary candidate only with date-correct `P >= 0.5` |

RTS 28 changes an investment firm's reporting group rather than the exchange tick itself, so it need not cause a
stock-level outcome jump. It nevertheless violates the clean “only one deterministic rule changes here” story.
The preflight must therefore succeed using cutoff 10 plus a price-qualified 600 cutoff. Cutoffs 80 and 2,000 can
only diagnose whether a broader rule bundle behaves differently. A price source with explicit research-reuse terms
is still required before real analysis.

## 4. Official data contract

### 4.1 ESMA development and temporal validation

The public FITRS equity register exposes `ISIN`, MiFIR identifier, methodology, calculation period, calculation
time, ADNT, ADNT on the most relevant market and the most relevant market. Annual records use methodology `YEAR`.
The register legal notice authorizes reproduction of register information with source acknowledgement and a
statement when information is transformed. The 2026 schema adds explicit application-period fields; earlier
application dates must be reconstructed from the versioned rule.

Aggregate Solr facets over `SHRS` and `DPRS`, with `rows=0`, found one unique annual record per ISIN/year and the
following raw support in symmetric 20% windows. These are eligibility upper bounds, not analysis samples: the same
ISIN can recur across years, no exception/corporate-action filter has run, and no outcome or sign was returned.

| Input year | Annual records | c=10 below/above | c=80 below/above | c=600 below/above | c=2,000 below/above | c=9,000 below/above |
|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 12,246 | 128 / 128 | 108 / 89 | 69 / 88 | 86 / 85 | 85 / 103 |
| 2019 | 12,531 | 122 / 106 | 117 / 90 | 68 / 66 | 86 / 73 | 84 / 100 |
| 2020 | 13,446 | 113 / 90 | 138 / 111 | 115 / 90 | 158 / 150 | 124 / 78 |
| 2021 | 16,123 | 144 / 151 | 191 / 233 | 118 / 131 | 113 / 166 | 111 / 168 |
| 2022 | 17,588 | 192 / 211 | 166 / 136 | 165 / 131 | 143 / 133 | 101 / 50 |
| 2023 | 19,049 | 211 / 203 | 181 / 153 | 138 / 122 | 158 / 150 | 162 / 111 |
| 2024 | 20,122 | 248 / 208 | 226 / 171 | 154 / 116 | 142 / 129 | 151 / 105 |
| 2025 | 19,599 | 230 / 201 | 165 / 132 | 168 / 133 | 194 / 171 | 149 / 99 |

The frozen split is retained. Regular assignment cycles ending by 2023 form development; later EU cycles are
temporal validation. The 2017-to-2018 transition is not pooled with regular cycles because it overlaps initial
MiFID II implementation. Exact pair labels and the treatment-day fraction will be frozen in the real-data
preregistration.

### 4.2 Sealed UK replication

FCA FITRS instructions state that a full equity file contains the latest result for every `(ISIN, reporting
period)`, including ADNT on the most relevant market and reporting-period dates. The documented file API lists
weekly full files and daily deltas. Metadata-only catalog queries found full equity files in the March--April window
for every 2021--2026 publication year; the respective file counts were `32, 36, 36, 36, 36, 32`. These are ZIP-file
counts, not instruments.

FCA's legal terms place numerical datasets in its Data section under the UK Open Government Licence when FCA owns
the copyright. The same terms prohibit unconsented automated scraping, while the FITRS technical specification
explicitly supplies a machine-to-machine API, rate limiting and direct file links for automated download. The
replication contract is therefore conditional on using only that documented API/download path, respecting its
limits, archiving the applicable terms and not redistributing raw files. UI scraping is forbidden. UK
instrument-level records remain sealed.

### 4.3 Protocol deviation and containment

During schema discovery, a `q=*`, `rows=1` query accidentally returned one 2021 instrument record,
`ROROCEACNOR1`, including `mrmtl_adnte=20.75`. No adjacent year, outcome pair, cutoff-selected record or estimate
was opened. This breaches the frozen zero-value T0 boundary even though it cannot reveal the planned discontinuity.
The query is retained in the work log; the ISIN is permanently excluded from development, temporal validation, UK
replication, plots and examples. All subsequent feasibility queries used `rows=0`. This deviation must appear in
any paper or artifact audit; it is not silently waived.

## 5. Nearest-result and method audit

| Work | What it establishes | What remains for v5 |
|---|---|---|
| AMF (2018), *MiFID II: Impact of the New Tick Size Regime* | States that tick can change trade count and explicitly calls the tick--liquidity relation circular; argues wide annual bands should prevent material impact. | Directly blocks “first feedback” language; creates a falsifiable regulator prediction but does not estimate next-ADNT discontinuities across cycles. |
| FCA (2025/2026), *A closer look at the UK tick size* | Uses the April 2024 reclassification and DiD; 44 of 68 larger-tick stocks enter the treated sample. Finds wider spreads, fewer cancellations/orders and greater depth, with acknowledged selection risk. | Mandatory one-step baseline; it does not use statutory ADNT cutoffs to estimate the following annual ADNT or reclassification. |
| Chen (2024), *Essays on trading and informational efficiency* | Uses annual liquidity-status changes to study systematic-internalizer quote disclosure and explicitly addresses reverse causality. | Identification precedent around annual MiFID calculations, but not the tick-band-to-next-ADNT loop. |
| Derksen et al. (2020), *Effects of MiFID II on stock price formation* | Studies the 2018 regime shift and tick-size effects on price formation and volume. | Initial-regime evidence, not repeated endogenous annual feedback. |
| Calonico--Cattaneo--Titiunik (2014) and multi-cutoff RD | Robust bias-corrected local-polynomial inference and pooled/cutoff-specific designs are standard. | Blocks an NMI claim based on renaming multi-cutoff RD. |
| Kolesar--Rothe (2018) | Conventional inference can undercover with a moderately discrete running variable; clustering by score does not solve misspecification. | Requires an honest/discrete-support attack in addition to the frozen robust local-linear oracle. |
| RTS 28 | Uses 80 and 2,000 ADNT boundaries for grouped annual execution reporting. | Makes those cutoffs joint-rule sensitivities rather than clean tick-only primary cutoffs. |

Exact searches included annual reclassification, next-year ADNT, next assignment, liquidity-band persistence,
hysteresis/chattering and regression discontinuity at each statutory cutoff. No direct repeated-cycle estimate was
found as of the audit date. That is a bounded search result, not a novelty certificate. A venue submission still
requires a conventional citation review by a market-microstructure specialist.

## 6. Gate decisions

| Gate | Decision | Reason and remaining condition |
|---|---|---|
| G0 exact legal mechanism | `PASS` | The calendar-year measurement, publication/application dates, cutoffs, tick table and major exception classes are fixed by official sources. Every analysis row still needs a rule-version tag. |
| D0 free longitudinal contract | `CONDITIONAL_PASS` | ESMA provides reusable 2017--2025 annual records and FCA provides 2021--2026 full-file history. UK use is restricted to the documented API/OGL path; a reusable date-correct price and corporate-action source remain to be frozen before real values. |
| I0 local identification | `GENERATED_ONLY` | Blind counts are ample and cutoff 10 always changes the grid. A second clean cutoff depends on price qualification; score discreteness, mixed exposure, corrections and shared RTS 28 thresholds need generated attacks. Real-data analysis is not authorized. |
| N0 NCS exact-result | `NCS_FEASIBILITY_CANDIDATE` | Circularity and one-step effects are known, but no direct repeated next-ADNT discontinuity was found. A surprising, replicated effect is still required; null or ordinary heterogeneous effects route lower. |
| N0 NMI method | `NMI_NO_SURVIVOR` | The proposed estimator is a multi-cutoff/dynamic RD application with a discrete-score complication covered by existing theory. No non-equivalent theorem or method card exists. |

## 7. Authorized next action and stop conditions

The audit authorizes only a new generated-data experiment after its preregistration is committed and pushed. It
must compare robust local-linear and honest discrete-support inference under smooth null, reinforcing/corrective
effects, rounding, regression to the mean, sorting, mixed exposure, attrition and shared-cutoff contamination. It
must not use an instrument identifier, downloaded FITRS ZIP, market price, UK value, remote host or GPU.

Real values remain locked until all of the following hold:

1. generated null false-positive and interval-coverage gates pass for both continuous and rounded ADNT;
2. the 5% annual effect floor has adequate power under the observed aggregate support envelope;
3. a licence-safe, date-correct price/corporate-action contract makes cutoff 600 usable independently of cutoff 10;
4. the exact development/temporal-validation pairs and the contaminated-ISIN exclusion are committed; and
5. the UK API/OGL interpretation and sealed artifact procedure are frozen.

Failure of discrete-score coverage, absence of a second clean first stage, or a nearest paper with the same
repeated next-ADNT estimand retires v5 before any market outcome is opened. Generated success validates the design
code only and cannot raise the Nature-scale probability by itself.

## 8. Primary sources

- [RTS 11 consolidated text](https://eur-lex.europa.eu/eli/reg_del/2017/588/2023-06-05/eng)
- [2023 application-date amendment](https://eur-lex.europa.eu/eli/reg_del/2023/960/oj/eng)
- [AMF tick-size impact report](https://www.amf-france.org/sites/institutionnel/files/contenu_simple/lettre_ou_cahier/risques_tendances/MiFID%20II%20Impact%20of%20the%20New%20Tick%20Size%20Regime.pdf)
- [FCA annual reclassification study](https://www.fca.org.uk/publications/research-articles/uk-tick-size)
- [FCA FITRS instructions](https://www.fca.org.uk/publication/systems-information/fca-fitrs-tech-spec.pdf)
- [FCA data/legal terms](https://www.fca.org.uk/legal)
- [ESMA MiFIR/FITRS schemas](https://www.esma.europa.eu/data-reporting/mifir-reporting)
- [ESMA register legal notice](https://registers.esma.europa.eu/publication/legalNoticePage)
- [RTS 28 grouped boundaries](https://eur-lex.europa.eu/eli/reg_del/2017/576/oj/eng)
- [Chen dissertation](https://minerva-access.unimelb.edu.au/server/api/core/bitstreams/d52f7773-e09d-4f50-8cca-1d4eab6aa649/content)
- [Robust RD inference](https://doi.org/10.3982/ECTA11757)
- [Discrete-running-variable RD](https://www.aeaweb.org/articles?id=10.1257/aer.20160945)
- [Multi-cutoff RD analysis](https://arxiv.org/abs/1912.07346)
