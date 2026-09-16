# Paper G CfD source preflight — September 8, 2026

**Current resolution (September 9):** the bounded follow-up closes the screened public-source
causal parent and realized-generation branch; the contractual mechanism remains unresolved.
See `papers/proposal/ecomd_paper_g_cfd_identification_result_2026-09-09.md`. The account below preserves the earlier decision history.

Private/internal selection result. Follow-up to Cycle21, not a new search cycle,
F3 audit, prospective experiment freeze or authorization.

**September 8 decision (historical):** close the **public-FPN before/after plan-revision endpoint** at
`paper_g_cfd_cross_auction_public_pn_revision`. Retain the underlying question
`paper_g_cfd_cross_auction_revelation` as **F2-deferred**, with an explicitly
separate realized-generation endpoint contract below. Its causal assignment and
incremental novelty are not qualified. No empirical response has been measured.

## 1. The observation gate has a concrete answer

The [BMRA service description, version 25, Section 7](https://bscdocs.elexon.co.uk/service-descriptions/balancing-mechanism-reporting-agent-service-description/v-25-0/id-62e3e0ecd3ac240007c4a54d)
describes FPN transmission around Gate Closure. The
[NETA public interface, BMRA-I004, Section 4.1.1](https://bscdocs.elexon.co.uk/interface-definition-documents/neta-interface-definition-and-design-document-part-1-interfaces-with-bsc-parties-and-their-agents)
classifies point FPN records as Gate Closure data. The
[Elexon FPN definition](https://www.elexon.co.uk/bsc/glossary/final-physical-notification/)
connects those final notifications with public Insights reporting. Indexed
primary text was inspected for these sources; the dated BMRA specification is
not silently presented as the current version of every interface.

Consequently, retrieving superseded **published** PN messages does not recover
all private notifications submitted before publication. An affected late-day
delivery tail may remain physically adjustable after the morning auction while
its eventual public FPN is still many hours away. The existence of private
revisions is consistent with the [February 2025 NESO guidance, pages 6 and 9](https://www.neso.energy/document/354736/download),
which distinguishes pre-Gate-Closure expectations and their updates from final
notification accuracy. Submission to NESO and public disclosure are different
events. The guidance is a dated requirement/context source, not a release licence.

Two possible substitutes also fail this specific observation contract:

- [Non-BM PN metadata](https://www.neso.energy/data-portal/obp-non-bm-physical-notifications/non-bm_physical_notifications)
  labels its output levels at Gate Closure. Continuous publication does not
  imply a private revision archive, and its unit population is different.
- [NESO's April 22, 2026 forum, slide 29](https://www.neso.energy/document/380756/download)
  describes a day-ahead flows/limits snapshot, usually published around 16:30,
  with later adjustments outside that dataset's scope. It does not supply the
  required unit-level pre/post-auction plan history.

This is a source-semantic failure of the proposed public-FPN endpoint. It is
not a claim that lawful operator or participant archives can never exist, or
that all public electricity research is impossible.

### Exact information-loss check

Take a declared future-period plan class with capacity `C=100` and identical
final FPN `40`. One history has pre/post-auction plans `100 -> 0`; another has
`0 -> 100`; both subsequently converge to `40` before Gate Closure. Keep
published prices, final FPN, later generation and other observed records equal.
The immediate revisions are `-100` and `+100` despite identical public records.

More generally, with no restrictions beyond both private plans lying in
`[0,C]`, a final-only archive leaves the immediate revision in the full sharp
interval `[-C,C]`. For any proposed difference `d` in that interval, choose
`p_before=max(-d,0)` and `p_after=max(d,0)`, then converge to the same final
notification. This is an elementary observation-map result for the declared
plan class, not a new theorem, equilibrium model or claim about a particular
plant's actual forecasting conduct. More public final-FPN rows cannot invert
this map without additional restrictions or observations.

## 2. The closest revision narrows novelty further

The complete file for [Van Steenberghe and Ovaere's June 3, 2026 revision](https://wps-feb.ugent.be/Papers/wp_25_1124_rev.pdf)
was obtained. The title/date, Sections 2.2, 3, 4.1–4.2, 5.1.2, conclusion and
Appendix H were inspected; not every appendix estimate was independently
audited. The acquisition hash and reading scope are in the structured preflight.

Its main response is realized unit generation around negative-price delivery
events. Equation (3) interacts support cohort with event membership, while
Appendix H includes duration and time-of-day heterogeneity. Neither that
specification nor its time-of-day split is the proposed cross-auction threshold
contrast. This comparison does **not** prove that the exact contrast is novel.
It does close the shortcut of relabelling an overnight or longer-event output
comparison as an independent new mechanism. The paper's explicit discussion of
time-varying unit heterogeneity also prevents treating its fixed effects as an
automatic identification certificate for our different contrast.

The published study reports 18 long negative-price events in the AR2 comparison
period. This is prior-study context, not a newly counted eligible sample. The
number of usable cross-boundary, near-threshold episodes is unknown and cannot
be inferred from the number of unit/half-hour rows.

## 3. A distinct endpoint contract, with a native threshold

Realized old-tail generation is a different response from an immediate private
plan revision. The [official B1610 documentation](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/B1610/stream)
identifies a public actual-generation product, and the revised paper describes
unit-level generation and contract joins. These establish a plausible source
class, not a verified complete panel, historical unit/schema crosswalk, research
release contract or causal design. No outcome endpoint was called.

The candidate risk set can be defined **before** the later auction: an older
delivery block ends with exactly `r` negative reference-price hours, where
`1 <= r <= 5`, preceded by a nonnegative hour. Let `b` be the correctly mapped
delivery-block boundary. Write the first `m=6-r` new reference prices as
`P_1,...,P_m` and define

\[
R=\max(P_1,\ldots,P_m).
\]

Under the [screened six-hour contract](https://assets.publishing.service.gov.uk/media/5a8198f040f0b62305b8fcff/FINAL_CFD_Standard_Terms_and_Conditions_V2-_13_March_2017_.pdf),
the old tail loses support exactly when `R<0`. If `R>=0`, the first nonnegative
new hour breaks the run before it reaches six. Equality at zero breaks the run.
This avoids selecting only favorable realized prefixes after the auction. It
does not turn the jointly determined price vector into an assigned intervention.
The score uses the contractual IMRP, not an arbitrarily chosen exchange price.

| Element | Explicit alternative contract |
|---|---|
| Object | Generation during the already priced old delivery tail, for actual six-hour-clause units |
| Pre-state | Old tail and contract status, capacity/operating scope, information and forecasts available before revelation; actual unit mappings still required |
| Response | Capacity-and-duration-normalized delivered energy over that old tail; final-vintage and missingness rules remain unfrozen |
| Contrast | Difference in the two cohorts' generation jumps as the new-block score crosses zero |
| Rivals | Incremental contractual supply response versus all apparent changes arising from information, physical constraints, sorting and trading opportunities |
| Truth | Exact eligibility mapping only; causal design, field schema, support and rights unqualified |

For cohort means `mu_6(R)` and `mu_control(R)`, the descriptive target is

\[
D=[\mu_6(0^-)-\mu_6(0^+)]
  -[\mu_{control}(0^-)-\mu_{control}(0^+)].
\]

Calling `D` a contract effect additionally requires a justified restriction on
the *difference* in noncontractual jumps. It need not vanish merely because both
groups see the same market. The controls may react differently to common news,
and share price-mediated spillovers. Contract selection is not random.

The zero boundary can have strategic bids, atoms, ties among several component
prices and sparse local support. The maximum maps a multidimensional boundary
into one score; it does not establish comparable boundary composition. Do not
assume a single exchange's tick size is the tick of a weighted IMRP.
[RD identification conditions](https://arxiv.org/html/2108.09400v2) must be
supported independently. Density, balance and placebo checks can reject a
design; passing them does not by itself prove it. Eventual revised prices also
cannot replace the price information known when dispatch was still adjustable.

### A sign check does not supply innovation or universal curtailment

With zero operating marginal cost, capacity `C`, lawful positive subsidy `a`,
and fixed net marginal market revenue `m`, ordinary optimization gives full
output when `m+a*eligibility>0` and zero when it is negative. Removing support
changes output in the strict interior `-a<m<0`; if `m>0`, both cases produce at
capacity, and if `m<-a`, both cases produce zero. Thus even this standard parent
model allows a null response. This is a conditional baseline, not a market
equilibrium or a new economic result. Field wind availability, network limits,
hedging and endogenous market revenue add further state requirements.

A useful empirical null must therefore be tied to a predeclared eligible state
and meaningful precision bound. It cannot refute all contractual transmission
merely because average output does not move.

## 4. Decision boundaries and next decisive work

The public plan-revision branch is terminal. The original question's
realized-generation branch remains **F2-deferred**, not qualified for outcome
access or implementation. This is an explicit endpoint refinement within
Cycle21's already stated supply question, not a new raw-program harvest.

Before any escalation, a bounded source/identification audit must establish:

1. Actual contract-to-unit applicability and a versioned B1610/IMRP join,
   including source clock, publication/revision lifecycle, missingness, rights
   and an untouched confirmation partition. A forecast available only after
   the auction is not a pre-state control.
2. A defensible local assignment or an externally justified bound on differential
   noncontractual jumps. The zero threshold alone does not pass this gate.
3. Independent event support and a useful precision contract. The observed
   source count from a prior paper is not a power calculation. Comparable
   replication must retain contract, boundary and information/action semantics.
4. An incremental identification or measurement contribution beyond the
   revised paper and standard RD/optimal-dispatch parents. No exact-novelty
   claim has passed a full audit.

If these cannot be supplied, close the realized-generation design as well;
do not recycle final-FPN plots, time-of-day subsets, a renamed country or a
synthetic subsidy response as its substitute. No fifteen-work F3 audit or
forecast is justified yet.

Nine source records were added; existing BMRA, portal, contract and RD sources
were reused. Published prior results are development context. No raw target
outcome, simulator, GPU, participant action, outreach, purchase, implementation
or machine decision was used or created. The earlier closed families and the
separate recall/margin leads are unchanged. Private verification records carry
engineering provenance; it is not research evidence.
