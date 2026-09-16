# Paper G: transaction-triggered protection and recovery scope

PRIVATE / INTERNAL. `public_evidence_eligible: false`. Paper-only source and
theorem-scope audit, not a new discovery cycle or experiment authorization.

The Deribit protection rules do not instantiate the external, one-way recovery
clock in the existing inventory theorem. They also do not establish a new
learning contribution. The existing `market_maker_protection_quote_purge` route
remains `failed_closed`; this audit is `not_trigger`.

## Named blocker and repository connection

The August 25 [MMP worksheet](ecomd_discovery_loop_topic_cycle_1_result_2026-08-25.md)
already identified threshold/reset reduction and unobserved participant counters,
settings and quote ownership. It did not prove that every participant-level
learning question is closed. Its exact purge claim must not be reopened by a
different venue name or by treating private account documentation as public truth.

The recent [modewise upper bound](ecomd_paper_g_access_modewise_bound_2026-09-11.md)
uses an external restoration time, at most two segments and a common occupation
baseline for learner and oracle. The [quote lower bound](ecomd_paper_g_inventory_quote_lower_bound_2026-09-11.md)
already occurs at zero restoration. The remaining scope question is whether a
documented transaction-triggered pause supplies the missing lawful coupling and
truth asset. This audit checks that proposed bridge, without harvesting candidates.

## Selected official evidence

1. The [Deribit configuration guide](https://docs.deribit.com/articles/market-maker-protection)
   describes transaction exposure limits and an interval anchored to its first
   trade. A zero freeze setting disables automatic restoration; manual reset is
   still available. Configuration/status and trigger messages have participant
   interfaces. These descriptions are not evidence that a public observer has
   the participant's complete counter history. Only the selected configuration,
   reset and monitoring sections were examined.
2. The [Starbase MMP specification](https://docs.deribit.com/starbase/mmp)
   distinguishes tagged orders from mandatory protection on mass quotes, with
   portfolio/index or group scope. Reset cannot override the first second of
   freezing, but can shorten a longer freeze. Fill and cancellation notifications
   need not arrive together. Pending speed-bumped orders can become IOC and still
   execute after triggering. These are documented lifecycle rules, not measured
   latency or empirical frequency estimates. Selected scope, reset, messaging
   and pending-order paragraphs were read; linked implementation details were not.
3. The [Deribit FZE rulebook](https://support.deribit.com/hc/en-us/articles/25944555524125-Deribit-Exchange-Rulebook-Deribit-FZE),
   rules 3.6 and 7.24–7.28, requires market makers to comply with protection
   settings, describes discretionary activation and limits cancellation to tagged
   orders. An editable API flag therefore does not establish that a particular
   participant may freely discard its protection obligations. No participant
   agreement or account authorization was inspected.

These are three pages from one provider, not independent engines or an opposing
pair of scientific models. Reading date: September 11, 2026 local time. No stable
historical protocol version or byte snapshot is certified by this HTML reading.

## What carries over, and what fails

The scientific object would have to include the participant's lawful quotes,
inventory, exposure counters, interval phase, protection group and reset state.
A complete replay would also need pending orders and ordered receipts. This is
a **necessary-state checklist**, not a claim that these fields alone have been
proved Markov or that the required account data are available.

There is a genuine action-to-state path: quote choices affect executions, which
can reach a threshold and affect later quoting. But a selective, resettable
protection state is not equivalent to a complete loss of every hedge channel.
Nor does a manual reset restore the earlier inventory or erase prior executions.
The formal learner and oracle must share the same permitted resets, message
timing and costs. No lower bound may manufacture a recovery bottleneck by
withholding a reset that its chosen native contract permits.

The earlier upper proof cannot simply be restarted at each endogenous switch.
Write a putative mode-gain baseline for policy pi as

\[
B_\pi=\mathbb E_\pi\sum_{t=1}^T g_{m_t}.
\]

Whenever such gains and expectations are well defined, elementary add-and-subtract
gives, for the common return objective J and comparator pi-star,

\[
J(\pi^*)-J(\pi)
=\{J(\pi^*)-B_{\pi^*}\}
+\{B_{\pi^*}-B_\pi\}
+\{B_\pi-J(\pi)\}.
\]

With the previously proved independent, one-way clock, the middle term vanishes
because the mode law is policy independent. With execution-triggered protection,
that equality has not been established. Even hypothetical within-segment bounds
leave the occupation term and potentially many segment boundaries to control.
Conditioning on an endogenous switch time also need not preserve the earlier
independence argument. This identity is standard algebra; it is **not** a proof
of a harder minimax rate, linear regret, SCAL failure, or a new MMP theorem.
Finite bias spans for the completed protection state remain unproved.

## Decision and next decisive evidence

No recorded blocker is removed. Current documentation does not supply randomized
threshold assignment, a complete participant replay, independent implementation,
or a proposition beyond the existing threshold/control parents. The historic
activation probability is not updated or treated as a scientific rejection test.

Stop venue-by-venue collection for this formulation. A useful future update must
first identify an already accessible, lawfully usable participant truth/control
asset or a precise theorem eliminating a named blocker. It must specify a common
oracle/learner action set and preserve reset and pending-execution semantics.
Any proposed learning advantage must be separated from the known-law optimal
control value of avoiding protection. This is a condition for re-entry review,
not permission to acquire accounts, contact participants, access outcomes or run
a simulator. Paper G's publication-level objective remains unmet.

## Access and recording

Three official documentation sources; one standard algebraic scope diagnostic;
zero new questions, cycles, forecasts, machine cards or scientific outcomes.
Embedded API examples were visible as documentation; no source repository,
private endpoint, account, notebook or scientific program was accessed/executed.
Formal result, source manifest, contract, existing route and re-entry audit,
daily log and long-term memory are maintained together. Registration checks
verify record consistency, not mathematical novelty or production behavior.
