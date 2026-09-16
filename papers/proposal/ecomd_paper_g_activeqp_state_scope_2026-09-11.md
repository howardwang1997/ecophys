# Paper G: ActiveQP control and layered restoration scope

PRIVATE / INTERNAL. `public_evidence_eligible: false`. Existing-parent source
audit; `not_trigger`. No new question cycle or scientific execution.

**Result:** the selected current Phlx rule distinguishes active counter control,
class-level restoration and staff-enabled restoration after a Multi-Trigger
event. A class counter of zero is not a complete normal-state certificate.
No bounded native recovery time or new learning contribution is established.

## Source scopes

The existing graph citation to [Lehoczky et al., Dead Man's Switch: Making
Options Markets Safer with Active Quote Protection](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3675849)
was revisited at its abstract/metadata level only. The abstract proposes an
active communication-based protection protocol. This supports the existing
protocol-design prior; it does not certify a stochastic control model, regret
theorem, counterfactual welfare estimate or their absence from the full paper.
The full 23-page text was not verified in this session. No claim is made that
the paper's proposed protocol equals a current exchange implementation.

The [current Phlx Options 3 rulebook](https://listingcenter.nasdaq.com/rulebook/phlx/rules/Phlx%20Options%203),
Section 15(c)(2)(B)–(G), supplies the substantive native scope evidence. It
allows partial/full decrement of the active class counter. Class-limit purge
requires full decrement for re-entry. Multi-Trigger instead aggregates purge
events over overlapping windows and requires staff-enabled re-entry. A voluntary
class-wide removal does not automatically reset its windows. Executable
interest received before triggering can execute beyond the limit. At least
one primary protection is required; optional Multi-Trigger and alternative
primary protections are distinct configuration choices. Selected clauses were
read as current HTML on September 11, 2026 local time; historical versions,
member settings, packet protocol and live behavior were not verified.

## Consequences for the current proof target

The [recovery lemma](ecomd_paper_g_recovery_span_scope_2026-09-11.md) explicitly
assumes a uniform legal quiescence procedure that restores a normal state.
The source does not certify that assumption. A full target state would need
to retain the applicable class and aggregate protection states, outstanding
events and restoration permissions. The existence of a class-counter decrement
message cannot establish a bound on the other restoration path.

In particular, a projection onto inventory, current class counter and a generic
“can quote” flag is not proved sufficient: two otherwise similar snapshots can
have different remaining aggregate trigger histories. A later class purge can
then have a different aggregate consequence. This is a direct state-completion
requirement from the documented rule, not a new cascade law or an empirical
hidden-state discovery. No exact Markov representation is certified here.

Likewise, a Contract Limit cannot silently become a strict pre-execution inventory
cap. Native admissibility and the event order must preserve the clause about
previously received executable interest. Altering that rule would change the
market and could manufacture a favorable recovery or learning theorem.

A model restricted to a particular permitted configuration could exclude an
optional layer, but that restriction needs a frozen native contract. The audit
does not choose such a configuration or authorize turning off protection. It
also does not infer that staff-enabled restoration is unbounded, adversarial,
unknown to participants, or impossible: those would require additional evidence.
What remains unproved is a uniform bound over the proposed market-law class.

## Decision and stopping rule

The selected source resolves a narrow uncertainty about control semantics.
It does not supply the missing participant truth/control asset, independent
implementation, bias advantage bound K or pair of unknown laws inducing a
nonstandard learning problem. Existing route
`market_maker_protection_quote_purge` remains `failed_closed`; no recorded
blocker is removed and no publication forecast is created.

Stop adding exchange analogues for this formulation. Further useful work must
either establish the exact permitted configuration and complete event state,
with a verifiable uniform recovery/value certificate, or obtain a qualified
source/model disagreement under the same contract. An abstract-level prior
check cannot decide full-paper theorem coverage. The broader Paper G objective
remains unmet.

## Access accounting

One newly registered official rule source, one existing abstract citation
revisited; no new scientific paper fulltext or paper-only theorem diagnostic.
No local PDF/cache, account call, participant data, model payload or scientific
code. Formal, contract, manifest, existing route, re-entry record, log and memory
are maintained together. Record checks do not validate production behavior.
