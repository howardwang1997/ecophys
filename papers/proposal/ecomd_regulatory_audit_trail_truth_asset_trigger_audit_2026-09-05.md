# EcoMD regulatory audit-trail truth-asset trigger audit

**Date:** 2026-09-05  
**Archetype:** `measurement_method`  
**Decision:** `not_trigger`  
**Candidate harvesting:** not authorized  
**Regulatory/outcome access, outreach, implementation, SSH, and GPU work:** not authorized

## 1. Executive decision

The US Consolidated Audit Trail (CAT) contains almost exactly the observation object that an
actor-resolved EcoMD validation program would need: linked origination, routing, modification,
cancellation and execution events across markets, together with broker, account and customer
identifiers. It is a real truth capability.

It is not an available research asset. The SEC's April 2026 concept release states that CAT access
is role-controlled and that Rule 613 and the CAT NMS Plan prohibit use by non-regulators and for
non-regulatory purposes. The same release asks whether any CAT information should later be made
available to market participants and, if so, only under conditions and potentially at an aggregate
level. That is a policy question, not a current public-data endpoint.

The SEC's public MIDAS downloads sit on the other side of the boundary. They expose security-,
exchange-, decile- and time-bucket metrics such as order-to-trade activity and quote-lifetime
distributions. The SEC explicitly states that MIDAS combines consolidated and proprietary feeds but
does not provide a comprehensive cross-market order lifecycle. Public aggregates neither identify
actors nor recover routing, parent-child relations, rejections, account state, or an assigned
counterfactual.

The two capabilities cannot be combined by software: the complete rows are legally restricted and
the public rows are a many-to-one aggregation of them. Reconstructing or learning a latent audit
trail from MIDAS would select one member of an observational equivalence class, not recover CAT
truth. That reduction is already covered by the repository's observation-quotient results.

The new 2026 documents therefore confirm the exact external-truth blocker rather than remove it.
The route is `not_trigger`; no outcome row, authenticated portal, outreach, simulator, or GPU is
authorized.

## 2. Exact question and rival explanations

**Market-native object.** Let `C` be a complete linked audit trail containing order origination,
routing, venue arrival, modification, cancellation, execution and stable regulatory actor/account
keys. Let `S=T(C)` be the public SEC market-structure statistics. The question was whether public
regulatory data now permit training or validating an EcoMD simulator against actor-level response to
market-rule interventions.

- **H1 — public regulatory truth:** current SEC releases expose a lawful, immutable subset of CAT
  with enough lifecycle, actor and assignment state to identify the relevant response.
- **H0 — access-separated capabilities:** CAT has the needed semantics but is restricted to
  regulatory use; MIDAS is public but only exposes non-injective aggregate summaries. Neither alone
  or together gives a public actor-level intervention target.

**Cheapest discriminator.** Require an unauthenticated or formally approved research endpoint whose
schema exposes linked lifecycle and actor keys under publishable reuse terms. If official policy
forbids non-regulatory CAT use and the public schema contains only aggregates, H1 fails before any
row access or method review.

A positive result would remove the project's most persistent real-market truth blocker. A null result
matters because it prevents “the regulator has the data” from being conflated with “the data are a
lawful scientific asset.”

## 3. What CAT contains

Rule 613 and the 2026 concept release describe CAT as a linked regulatory database covering the full
lifecycle of orders in NMS and OTC equity securities. Reportable events include origination or
receipt, routing and routed receipt, executions, modifications and cancellations. Regulatory IDs
include broker-dealer and exchange codes, Firm Designated Identifiers for trading accounts, account-
holder types, and transformed customer identifiers.

This is substantially closer to a stable actor/action observation map than public exchange feeds:

- events are linked across brokers and venues rather than only inside one displayed book;
- origin and route state exist rather than only accepted destination messages;
- account and customer linkage is distinct from voluntary displayed MPID attribution; and
- regulator-side corrections and linkage processing explicitly address lifecycle errors.

The contract is not perfect. The 2026 review discusses linkage errors, delayed corrections,
retention reductions, exemptions for some floor verbal activity, and possible changes to customer-ID
generation. Those issues would require a field-level audit if access ever became lawful. They are not
the current killer.

## 4. Why CAT is not an authorized research asset

The April 2026 SEC concept release is explicit:

1. CAT uses role-based access, individual authentication, multifactor authentication, information
   barriers, encryption, monitoring and remote-access controls.
2. Rule 613 and the CAT NMS Plan prohibit CAT use for commercial purposes, by parties that are not
   regulators, and in non-regulatory contexts.
3. Participants' regulatory staff and the SEC receive access solely for regulatory and oversight
   responsibilities; users must agree not to use CAT data outside surveillance and regulation.
4. The Commission asks under what future circumstances CAT data *should* be made available to
   interested market participants in rulemaking and at what aggregation level. This confirms that a
   general public or academic row-level release is not currently established.

The user's blanket authorization for public/open data does not override federal market-data access,
privacy, confidentiality, or regulatory-purpose restrictions. Contacting the SEC, an SRO, FINRA CAT,
or an industry member to seek access would be external coordination and is not authorized by this
preflight. Even such outreach could not substitute for a formally lawful research-use pathway.

## 5. What public MIDAS downloads contain

The June 2026 SEC download page offers useful descriptive datasets:

- metrics by individual security;
- metrics by security and exchange;
- exchange-level summaries;
- quote-life hazard, survivor and conditional cancel/trade distributions;
- metrics by market-capitalization, price, volatility and turnover groups; and
- historical spread and depth panels.

These data are public and potentially useful as stylized-fact checks. They are not public CAT. The
SEC says MIDAS processes consolidated tapes and separate proprietary exchange feeds, but does not
provide the comprehensive cross-market audit trail needed to follow an order from origination through
routing, execution, modification or cancellation.

The public downloads therefore omit the exact information this discovery program needs: persistent
actor/account keys, parent-child and cross-venue order linkage, private route decisions, rejected
intent, inventory and information state, and assigned potential outcomes.

## 6. Aggregation cannot recover the restricted truth

For any released statistic `S=T(C)`, all complete trails in the fibre

\[
\mathcal F_s=\{C:T(C)=s\}
\]

are observationally equivalent. Security-exchange activity counts and quote-life distributions can
be held fixed while reallocating messages among customers, changing routing graphs, pairing parent
and child orders differently, or reversing actor-conditioned response to a rule change.

A generative model fitted to `S` can produce a plausible element of `F_s`; it cannot establish which
element generated the data. A learned CAT imputer is likewise untestable without accessible linked
targets. This is the repository's existing fibre-factorization/observation-quotient boundary, not a
new theorem or ICLR method.

Public CAT-derived aggregates could add moments beyond a narrower tape dataset, but their legitimate
interpretation would remain aggregate compatibility. They cannot be called participant truth,
mechanism recovery, or prospective counterfactual validation.

## 7. Gate matrix

| Gate | CAT | Public MIDAS | Decision |
|---|---|---|---|
| Complete linked order lifecycle | Designed to pass | Explicitly fails | Needed rows restricted |
| Stable regulatory actor/account keys | Present with caveats | Absent | Public actor truth fails |
| Cross-market routes and parent-child links | Present with linkage QA | Absent | Public state incomplete |
| Public/open row-level access | Fail | Pass for aggregates | Capabilities are separated |
| Publishable non-regulatory use | Fail under current rule | Pass subject to SEC site terms | CAT cannot be used |
| Assigned rule intervention/potential outcome | Not supplied by access alone | Absent | Causal field contract fails |
| Independent confirmation system | Absent | Absent | Replication fails |
| New identification method | No | No | Aggregate inverse is observation quotient |

The source-access gate fails before a full nearest-work review. Under the discovery protocol, further
paper harvesting would have negative value until this gate changes.

## 8. Exact re-entry conditions

Re-audit only after an official, dated change creates a lawful scientific-use asset with:

1. row-level linked lifecycle fields and stable de-identified actor/account keys through a public
   release or an explicitly approved research enclave;
2. written rights for the proposed analysis, derived-output publication, retention and independent
   replication, plus an ethics/privacy determination;
3. a frozen market-rule assignment and complete immediate pre-state, with a defensible interference
   unit and untouched confirmation families;
4. schema-level evidence that relevant linkage errors, corrections, exclusions and retention windows
   do not destroy the estimand; and
5. an independently governed second truth system or a theorem giving an identified response despite
   the remaining projection.

A new MIDAS month, an additional aggregate metric, a CAT technical specification, a regulator paper
reporting summary coefficients, or the mere existence of CAT is not a trigger.

## 9. Sources

1. SEC, *Market Structure Data Downloads*,
   https://www.sec.gov/data-research/market-structure-data
2. SEC, *Concept Release on Consolidated Audit Trail and Other Audit Trails and Data Sources*,
   Release 34-105251 (16 April 2026),
   https://www.sec.gov/files/rules/concept/2026/34-105251.pdf
3. SEC, *Rule 613 (Consolidated Audit Trail)*,
   https://www.sec.gov/about/divisions-offices/division-trading-markets/rule-613-consolidated-audit-trail
4. FINRA, *Account Holder Type Consistency Interactive Report Card*,
   https://www.finra.org/compliance-tools/report-center/account-holder-type-consistency-report-card

## 10. Compute decision

This audit is `not_trigger`; `candidate_harvest_authorized=false`. Do not access CAT or an
authenticated regulatory portal, contact a regulator or industry member, download MIDAS outcomes,
construct synthetic customer IDs, modify EcoMD, SSH to a worker, or schedule an A800/V100 job under
this route.
