# Paper G CfD identification resolution — September 9, 2026

Private/internal topic-selection result. This completes the bounded follow-up
to Cycle21 and the September 8 source preflight. It is not a new search cycle,
F3 audit, prospective forecast, experiment or public scientific result.

**Decision:** close `paper_g_cfd_cross_auction_realized_generation` and the
parent `paper_g_cfd_cross_auction_revelation` **under the screened public-source
causal formulation**. The immediate private-plan endpoint was already closed.
The stipulated stopping condition is now applied: this bounded audit did not
qualify an identification argument or an externally justified bound on
differential noncontractual jumps. This is a research-allocation decision,
not evidence that the contractual mechanism is absent or that all RD designs
with endogenous prices fail. No target price, generation or payment records
were accessed.

## 1. A concrete source asset survives

The [LCCC mapping catalogue](https://dp.lowcarboncontracts.uk/dataset/cfd-to-bm-unit-mapping)
provides a contract-to-BM-unit reference table with effective start and end
dates, updated when mappings change. The portal declares OGL v3. The actual
CSV and its field definitions were obtained as **non-outcome reference data**:
165 mapping rows, 119 distinct CfD IDs and 146 distinct BMU IDs; 156 rows have
blank end dates and nine have populated end dates. These are reference-table
counts, not eligible-event or statistical sample counts. The exact source
bytes, hashes, source URLs and acquisition provenance are retained in
`research/paper_g/source_reference/cfd_mapping_20260909/` and the structured
resolution record.

The published columns are `CFD_Id`, `BMU_Id`, `Effective_From` and
`Effective_date_to`. Portal metadata distinguishes transmission, embedded and
supplier BMUs. Mapping validity is therefore a supported join ingredient;
a BMU prefix does not guarantee coverage by a particular generation product.
Inclusive endpoint rules, time zone, blank-end semantics and complete historic
coverage still need source qualification. An effective date is not itself a
historical publication timestamp.

The [portfolio catalogue](https://dp.lowcarboncontracts.uk/dataset/cfd-contract-portfolio-status)
adds allocation round, technology, capacity and latest project status. Its
start date is explicitly an estimate. Neither that estimate nor mapping
validity proves the actual start of a particular negative-price clause,
amendment or exception. No portfolio outcome data or joined generation panel
was acquired. The declared licence for this reference asset does not settle
rights for the full multi-source event/revision panel.

This materially improves the earlier source assessment: a dated public
crosswalk exists. It removes neither the assignment blocker nor the missing
private-plan-history blocker, and does not qualify family re-entry.

## 2. The exact threshold is necessary but insufficient

Retain the already derived risk set: before the later auction, the older
delivery block has a terminal run of exactly `r` negative IMRP hours,
`1 <= r <= 5`, preceded by a nonnegative hour. Define `m=6-r` and
`R=max(P_1,...,P_m)` using the first `m` new-block IMRPs. Under the screened
operative six-hour contract, earlier-tail support is lost iff `R<0`.

The proposed response is delivered energy over that earlier tail, not the
private revision of a future plan. The proposed descriptive contrast is

\[
D=[\mu_6(0^-)-\mu_6(0^+)]-[\mu_c(0^-)-\mu_c(0^+)].
\]

For a specified direct contractual effect `tau`, write the decomposition
`D=tau+B`, where `B` contains the remaining differential jump, including
cohort-specific common-news responses, boundary composition and comparison
cohort spillovers. Defining this residual is accounting; it does not identify
either component. A total market-policy effect would require a different
intervention/exposure contract and cannot silently replace this direct target.

**Endogeneity alone is not a rejection of RD.** Continuity of the relevant
untreated response can support RD with a nonrandom score. Here, however, the
contract rule only establishes the eligibility jump. The reviewed material
does not justify continuity of the differential nuisance response at this
particular price boundary, nor a credible numerical bound. Common market
prices, unit fixed effects, a smooth score density and balanced measured
pre-states do not imply that restriction.

### A diagnostic counterexample, not a market theorem

Refine Cycle21's hidden-news example with `R` uniform on `(-1,1)`,
`T=1{R<0}`, a fixed cohort indicator `C`, constant observed pre-response `0.5`,
and observed post-response `Y=0.5-0.2*C*T`. All measured pre-covariates can be
constant. Consider two abstract potential-response specifications:

- A: `Y(a)=0.5-0.2*C*a`, with factual exposure `a=T`.
- B: `U=1{R<0}` and `Y(a)=0.5-0.2*C*U`, independent of `a`.

They produce the same observed contrast `D=-0.2`, smooth score density and
flat pre-responses. The exposed-cohort effect is `-0.2` in A and zero in B.
B violates the needed counterfactual continuity restriction while satisfying
the listed observable diagnostics. Thus those diagnostics cannot establish
identification on their own. These are elementary statistical specifications
in the minimally restricted response class, not equilibrium models or claims
that B describes actual generators. A justified institutional/model restriction
could exclude B. None was qualified in this audit; no new killer-test count is
claimed for this refinement.

## 3. Three econometric extensions do not yet supply a contribution

If external evidence supports `|B|<=b`, the decomposition implies
`tau in [D-b,D+b]`, intersected with any justified effect support. This is a
conditional population bound, not a confidence interval; a field analysis
would also need sampling uncertainty. We have no measured `D` and no
qualified `b`. A sensitivity curve may transparently report hypothetical
restrictions, but choosing `b` to preserve a desired sign cannot validate them.

[Picchetti, Pinto and Shinoki, version 2 dated January 27, 2026](https://arxiv.org/html/2405.18531v2),
already discuss confounder-stability assumptions, validity tests and bounded
variation sensitivity for difference-in-discontinuities. Their temporal design
is not this contract-cohort comparison, so its identification theorem cannot
be imported unchanged. It does establish that generic differencing and
sensitivity bounds are methodological parents, not our novelty claim.

[Choi and Lee (2018)](https://doi.org/10.1017/pan.2018.13) study multiple-score
RD with component-specific partial effects. For `m>1`, converting all prices
to their maximum does not automatically remove those effects or prove stable
boundary composition. This concern does not apply as a multiple-score issue
when `m=1`; the assignment restriction still remains.

[Kolesár and Rothe's discrete-score analysis](https://arxiv.org/abs/1606.04086v4)
shows why limited support requires explicit inference restrictions; clustering
by score is not a generic remedy for approximation bias. We have not inspected
the target IMRP support, established an atom at zero or inferred an index tick
from an exchange tick. This is a conditional inference requirement, not an
observed defect in the target data.

## 4. Measurement and precision limits remain separate

The [closest June 2026 revision](https://wps-feb.ugent.be/Papers/wp_25_1124_rev.pdf)
already studies realized generation and duration/time-of-day heterogeneity.
Appendix C supplies further published context about project aggregation and
daily settlement comparisons; those procedures do not establish this proposed
intraday endpoint's measurement truth. No claim here depends on an internal
implementation experience or on diagnosing another study's processing.

The relevant elementary measurement check is general. Let interval energy
`e_h` satisfy `0<=e_h<=c_h`, with **known energy caps**, and suppose only the
daily total `S=sum(e_h)` is independently verified. For the old-tail interval
set `T`, the sharp allocation bounds are

\[
\max(0,S-\sum_{h\notin T}c_h)
\leq \sum_{h\in T}e_h
\leq \min(S,\sum_{h\in T}c_h).
\]

They follow by filling capacity outside or inside the tail first; every
intermediate allocation is attainable with divisible energy. Daily agreement
therefore need not validate intraday timing. Ramp/availability constraints or
independent interval metering could tighten the bounds; they must be supplied,
not assumed. This is established allocation arithmetic, not a new measurement
paper. It does not assert that the available interval readings are wrong.

The prior study's reported 18 long negative-price events do not determine our
eligible, near-boundary episode count. We have neither demonstrated adequate
power nor proved inadequate power. Row multiplication cannot manufacture
independent auction episodes. No event-count, power or effect estimate was run.

## 5. Terminal scope and a specific reopening requirement

The current public-source causal formulation stops at F2. Its contractual
hypothesis remains scientifically unresolved. No theorem disproves all future
identification strategies, and the exact cross-auction empirical contrast has
not been certified either novel or an exact duplicate. Generic subsidy
response, time-of-day splits and econometric templates alone are insufficient
reasons to continue this proposal.

Reconsideration requires a new source-backed assignment argument for this same
state, exposure and response, or an independently justified informative bound
on `B`; an actual private revision archive could instead reopen that distinct
endpoint. Any future escalation must also resolve actual clause applicability,
information/revision clocks, interval measurement, interference, event-level
precision, untouched confirmation, replication and joined rights. A qualified
trigger must be recorded before harvesting from a closed/saturated family.
The crosswalk alone does not meet it. A different total-policy target is a new
formulation, not a repair already authorized here.

Seven source records, a reference-data snapshot and analytic audit assets are
retained. Cycle21's original counts and disposition history remain intact,
with this later resolution linked. There is no new cycle, trigger audit,
forecast, card, outcome permission, implementation, simulation, GPU work,
purchase, outreach or participant action. The separate recall and margin
leads retain their previous status.
