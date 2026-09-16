---
document: Paper G deferred policy leads — bounded source resolution
date: 2026-09-09
visibility: private/internal research selection record; not a manuscript or public claim
status: two_screened_public_source_formulations_failed_closed
literature_cutoff: 2026-09-09
target_outcome_accessed: false
simulator_runs: 0
gpu_hours: 0
prospective_freeze: false
---

# Paper G: resolving the two remaining deferred policy leads

The Cycle18 intraday-margin enforcement program and Cycle20 Clearstream recall
program both stop at their previously stated bounded source/identification gate.
**Neither screened public-source formulation qualifies as an independent Paper G.**
Their economic hypotheses remain unresolved. This decision neither proves that
a private institutional study is impossible nor establishes a novelty collision
for the exact causal effects.

This is a follow-up to existing F2 screens, not Cycle23, candidate harvesting,
a full hostile audit, an activation decision, or an empirical result. The PI's
continued-discovery request is recorded in the September 9 work log. Earlier
cycle counts and initial dispositions remain historical; the route graph and
this resolution carry the current decisions.

## 1. Recall: a real operational schema, still no qualified causal panel

**Unchanged fork:** an earlier contractual return requirement raises borrower
return/cover pressure, versus substitution by other lenders absorbs it. Retain
the original common-horizon response and the eligible risk set before
substitution; do not condition entry on receiving a borrower notice.

The [May 2024 operator notice](https://www.clearstream.com/clearstream-en/newsroom/240514-3961802)
announces June 8 availability, a move from 15:00 to 19:30 in the source-labelled
clock, and a shorter return period. It separates initial instructions,
substitution and borrower notification. The earlier conditional 1/2/1-day
compression calculation remains calendar arithmetic.

The [March 2026 ASL Product Guide](https://www.clearstream.com/resource/blob/1316370/5b4a7f8b762ac8fdae022b5fe64a8df0/asl-product-guide-data.pdf),
printed pp. 36–38 and its introduction, adds current operational documentation:
the relevant T+1 category includes DTC-eligible and Canadian securities and
Mexican equities; the cutoff is 19:30, with a one-business-day recall period.
The guide labels times CET without resolving historical DST conversion. It
describes substitutions, partial reimbursement under the same loan reference,
and recycling of the short loan identifier. Client settings can exclude some
unmatched instructions. These are useful schema facts, not confirmation of the
exact June 2024 deployment, participant coverage, or historical settings.

The [March 27, 2026 Reporting Guide](https://www.clearstream.com/resource/blob/1314412/a61028668486093f24f7fc19b8b39814/cbl-reporting-guide-data.pdf),
printed pp. 1–3, 46–47, 55–57 and 81–83, documents client reporting channels and
loan opening/closing messages. It includes a transaction identifier distinct
from the short loan reference. A transit counterparty preserves lending
anonymity; it is not the ultimate lender–borrower crosswalk. Xact supports
historical positions and movement/instruction views. Those capabilities must
be acknowledged: this is **not** a finding that no historical records exist.
The inspected specification does not supply a public, complete, lawfully
joinable panel from initial instructions through substitutions, borrower
notices, partial returns and cover/financing outcomes.

| Contract part | What the present screen establishes | Remaining requirement |
|---|---|---|
| Native policy | Announced change plus a later operational rule | Historical release/eligibility, clock conversion, boundary and calendar semantics |
| Units and lifecycle | Loan and transaction references; client movement views | Collision-safe identity scope and complete instruction-to-borrower lifecycle, including no-notice cases |
| Assignment | A notification-time cutoff exists | Sorting/cointervention justification; pre-instruction risk set |
| Interference | Substitution is operationally relevant | Shared lendable pools, concurrent recalls, allocation/settings and overlap exposure |
| Rights | Documentation may be read | Account data, cross-party joins, privacy and derived-release authority |
| Confirmation and replication | None reserved or established | Untouched partition and independently governed same-estimand replication |

**A retained analytic guardrail.** Consider two equally weighted pre-existing
loans H and L, with return fractions 1 and 0 under either policy. Under policy
0 only L receives a notice; under policy 1 both receive notices. The mean among
notified loans rises from 0 to 1/2, while the mean over the original two-loan
risk set remains 1/2 under both policies. Notice selection is monotone in this
fixture. Thus even a monotone expansion of notices can create a positive
conditional contrast with zero effect on either loan. This is a standard
post-treatment selection example, not a new theorem, equilibrium construction
or observation of Clearstream.

**Decision:** `paper_g_clearstream_recall_deadline_discontinuity` becomes
`failed_closed` for the screened public-source causal formulation. The
predeclared event-join/rights and credible-contrast requirements remain
unqualified after the bounded follow-up. Do not equate an unqualified contract
with proof that a lawful institutional asset can never be obtained. Exact
novelty also remains unqualified; no additional literature expansion is
justified before the source gate is removed.

## 2. Margin: protocol capability does not establish treatment exposure

**Unchanged fork:** transaction-time admission control reduces later external
funding needs, versus displacement of trades/funding explains the change.
Replaying accepted transactions cannot answer that behavioral question.

[FINRA Notice 26-10](https://www.finra.org/rules-guidance/notices/26-10)
sets June 4, 2026 effectiveness and transition through October 20, 2027.
Real-time blocking is optional. The reform also changes the previous PDT
framework, while valuation and activity-normalization choices affect
calculation. A reform date therefore does not itself specify the retained
admission-control treatment.

The current [Lightspeed intraday FAQ](https://lightspeed.com/trading/intraday-trading-faqs)
states that platform readiness and account eligibility can differ. Its
[margin page](https://lightspeed.com/trading/margin) also makes offered leverage
depend on account/platform conditions and permits lower leverage for some
new users. These statements motivate account-specific exposure validation;
they are not a verified historical allocation or a natural experiment.
Use the regulator's notice for the regulatory transition date.

The [Lightspeed Connect product page](https://lightspeed.com/trading/api-trading)
identifies an account trading/risk interface. The
[Connect IBKR v2.0.4 guide](https://d31x4u3ydvpof.cloudfront.net/manuals/Lightspeed_Connect_API_Getting_Started_Guide_IBKR_Prod.pdf),
PDF pp. 5–7, 20–23 and 44, supplies meaningful message capabilities:
initial open orders/positions, subsequent order statuses including rejection,
and monetary/ledger updates. Production needs account credentials;
certification uses simulated executions/risk. The guide explicitly describes
an IBKR-linked service. Its customer population and policy must not be
silently equated with every account covered by a broker-wide reform statement.
The inspected sections do not certify a complete historical event export,
a control-policy assignment/version field, or research/release rights.

[FINRA's margin reporting documentation](https://www.finra.org/rules-guidance/key-topics/margin-accounts)
describes month-end balances published in aggregate. That observation schema
cannot replace attempted/rejected activities, policy exposure and subsequent
funding histories for the retained account-level estimand. No statistics
table or account outcome was queried for this analysis.

**An exact bundle-identification guardrail.** Suppose the observed rollout
support is only $(A,B)=(0,0),(1,1)$, where A is admission control and B is
another reform component. In the illustrative additive model
$Y=\alpha A+\beta B+U$, even randomized rollout identifies only
$\alpha+\beta$. The worlds $(\alpha,\beta)=(1,0)$ and $(0,1)$
give the same observed law on that support but opposite allocations of the
effect to the two components. This is a standard restricted-support argument,
not a claim that all actual brokers change A and B together. Independent
variation or additional justified structure is needed for the retained
component effect. Switching to the total reform effect changes the question.

| Contract part | What the present screen establishes | Remaining requirement |
|---|---|---|
| Native policy | Optional real-time control under an actual reform | Dated account-level assigned and implemented control policy, separated from other components |
| State and events | A relevant production message interface exists | Same-population, complete multi-channel history, reconnect/backfill guarantees, rejects and policy state |
| Response | Existing five-business-day funding target retained | Complete deposits, financing and cross-account displacement |
| Assignment/interference | Platform/account heterogeneity is documented | Defensible assignment law/design and cross-account spillover contract |
| Rights and confirmation | No applicable contract obtained | Lawful linked panel, release/ethics, untouched confirmation and independent replication |

**Decision:** `paper_g_intraday_margin_enforcement_contract` becomes
`failed_closed` at the bounded public-source assignment/state gate.
API existence is a capability lead, not a qualified observational or
experimental panel. No certification environment, account, live endpoint,
order, participant or outcome was accessed.

## 3. What would justify another update

The two minimal admission requirements are now concrete:

- **Recall:** an authoritative historical instruction/substitution/notice/
  return linkage, including the original risk set and allocation context,
  lawful access/release terms, and a credible timing contrast.
- **Margin:** a dated account-policy assignment asset linked to complete
  attempted-order and funding histories in the same customer population,
  with the reform components distinguished.

Both also need untouched confirmation, independent replication and cost
qualification before empirical escalation. Their current acquisition cost
and independent sample count are unknown; no power calculation or compute
budget is invented. One new document with only another advertised cutoff,
API message name or rollout date does not remove these blockers. A complete
new asset must be recorded and validated under the applicable re-entry rules
before harvesting resumes.

Further Paper G discovery should first inspect an eligible new primary-model
disagreement or an already available truth/control asset. This is a search
priority, not a new candidate. No saturation rule is relaxed. The known
partial-order, information-rent, CfD and crypto-ETP closures remain intact.

Nine distinct substantive primary documents/pages were opened in this
follow-up: seven were new to these screens and two were revisited. Eight
source-access records are added to the evidence registry, including the
FINRA notice already cited in Cycle18 but not previously registered there.
No new primary research paper, raw question, cycle, original-cycle killer
count, F3 audit, prospective forecast, re-entry audit, card or scientific run
is added. The two elementary guardrails and the source-contract matrix are
reusable selection assets, not independent scientific discoveries.

