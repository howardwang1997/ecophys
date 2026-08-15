# Official NEMDE RHS rule audit

**Date:** 2026-08-15

**Decision:** `FREEZE_RPN_ONLY_SCADA_ARM_BLOCKED_BY_PUBLIC_SPEC`

## Bottom line

The RPN-group repair is specification-grounded. AEMO's final 2023 Constraint Implementation Guidelines state that
each group is evaluated on a stack independent of the main RHS stack, after which the top group-stack value is
multiplied by the group factor and added to the main calculation. The pinned Nempy implementation violates that
contract in two observable ways: it performs unchecked next-term access at group boundaries and, for a leading
`G` term that shares the group ID, it references `group.pop` without executing a removal. The intended removal is
also the **first** member, so replacing the typo with an unqualified `group.pop()` would remove the wrong member.

The proposed SCADA/input repair is not yet specification-grounded. Public AEMO documents define which SPD types
come from SCADA and expose `EMSMASTER` identifiers, but the audited documents do not say how multiple XML records
for one SPD ID are selected, how `EMS_Good` or replacement flags affect selection, or when the term default is
used. Summing every record, selecting a flagged-good record, selecting the latest record and falling back to the
default are materially different mechanisms. None may be promoted to an AEMO rule without another authoritative
source or an outcome-blind identification protocol.

The next fresh validation must therefore compare only `baseline` and `RPN-group repair`. The earlier descriptive
2-by-2 proposal is narrowed rather than implemented speculatively. SCADA/input resolution remains a named blocked
arm, not an excuse to tune against production RHS.

## Sources and verification

### AEMO Constraint Implementation Guidelines

- Official final document: [Constraint Implementation Guidelines v3, April 2023](https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/nem-consultations/2023/constraints-implementation-guidelines/constraint-implementation-guidelines-v3-final-clean.pdf).
- The audited local copy is the PDF vendored in clean Nempy commit
  [`2d3cef0e5545c820067fecddfa2e2fd984ac5583`](https://github.com/UNSW-CEEM/nempy/commit/2d3cef0e5545c820067fecddfa2e2fd984ac5583),
  SHA-256 `6bf59cace1c2e50a085c24fd3141e76a945ad03d947566ad0e2d1a6e8364dd37`.
- The 54-page PDF was rendered and visually checked at its cover and pages 11, 38, 39 and 47. The cover identifies
  AEMO, the title and April 2023. The critical tables and equations were legible and agreed with extracted text.
- The older official 2015 guide independently states the same group-stack rule, so the semantic finding is not a
  change introduced only after the 2021 cases.

### Public AEMO data/interface documentation

- The current [MMS Data Model entry for `EMSMASTER`](https://visualisations.aemo.com.au/aemo/nemweb/MMSDataModelReport/Electricity/MMS%20Data%20Model%20Report_files/MMS_151.htm)
  exposes `SPD_ID`, `SPD_TYPE`, description, grouping and last-change metadata. It describes the SCADA point but
  has no value-quality, replacement or fallback field.
- AEMO's [NEMDE Queue page](https://www.aemo.com.au/energy-systems/market-it-systems/electricity-system-guides/nemde-queue-service)
  states that the production solver is fee-for-service and that the formulation documentation has restricted
  distribution. The public [Queue Users' Guide](https://www.aemo.com.au/-/media/files/electricity/nem/it-systems-and-change/nemde-queue/nemde_queue_users_guide.pdf)
  describes the combined XML sections and scenario workflow, but not the contested SCADA selection algorithm.

These are primary sources. Search and the public data-model hierarchy found no AEMO document defining the
semantics of the XML attributes `EMS_Good`, `EMS_Replaced` or `Can_Use_Value` for RHS reconstruction. This is a
bounded negative finding about the audited public sources, not proof that no internal or participant-only rule
exists.

## Normative findings

### Group/RPN semantics

The April 2023 guide fixes the following observable contract:

1. the stack begins with one element equal to zero;
2. group members are evaluated on a stack separate from the parent equation;
3. a group behaves like brackets in a mathematical expression;
4. the final group-stack top is multiplied once by the `G` term factor;
5. that value is then added once to the parent stack;
6. constraint functions use the same separate-stack idea and may contain groups, but cannot reference another
   constraint function.

Its page-38 known answer evaluates four group members to `326`, applies the `G` factor `4.197` to obtain
`1368.222`, and adds the final outside term `-250` for RHS `1118.222`. This is already present in Nempy's tests,
but it exercises only the simple `members -> G terminator -> outside term` shape. It does not cover terminal `G`,
leading/shared-ID `G`, nested groups or a group at the end of a generic equation—the shapes implicated by the
production failures.

### SPD input and default semantics

The guide says an RHS term contains an ID, type, factor, optional operator, term ID, group ID and default value.
It defines `A` and `S` as SCADA values and uses current SCADA values for several other dispatch types. It does not
define:

- whether duplicate XML `ScadaValues` records are alternatives, components or revisions;
- an ordering key for those records;
- the meaning or precedence of `EMS_Good`, `EMS_Replaced` and `Can_Use_Value`;
- the condition under which the term default replaces a missing or rejected value;
- whether quality handling differs by SPD type or run mode.

Consequently the observed association between multiple/flagged SCADA inputs and tail error is scientifically
useful localization, but it is not a repair specification.

## Code-to-rule comparison

At pinned Nempy source `rhs_calculator.py:553--566`:

- `equation[i + 1]` is read without checking `i + 1 < len(equation)`, causing all four observed terminal
  `IndexError` failures;
- the source comment requires removing the first member when a leading `G` term shares the group ID, but
  `group.pop` is a no-op expression;
- a literal change to `group.pop()` would remove the last member and still contradict the source comment;
- the nearby end-group path also reads `equation[i + len(group)]` without a boundary guard.

At `_resolve_term_value`, the current evaluator sums every SCADA row for a type/ID pair while its quality check is
commented out. The official public sources audited here neither validate that sum nor specify a replacement.

## Frozen design consequence

The next protocol may implement one independently switchable, minimal RPN repair:

- bounds-safe terminal and following-group handling;
- first-member removal by position for the documented leading/shared-ID shape;
- no change to input lookup, SCADA aggregation, default handling, generic expansion or numerical operators;
- known-answer tests for the AEMO page-38 example plus terminal, leading/shared-ID and nested/end-group shapes;
- development checks on the two consumed cases, with no claim attached;
- fresh deterministic interval selection before any new RHS is opened;
- paired `baseline`/`RPN` evaluation with identical sentinels and denominators.

Fresh validation must report coverage, exception IDs, median, p95, p99 and maximum normalized error for each arm,
plus paired per-equation changes. It must pre-register a non-degradation gate as well as improvement: a repair that
eliminates exceptions by worsening the bulk or changing unrelated equations fails.

The input/SCADA arm can be reopened only after one of these gates:

1. an authoritative AEMO rule is obtained with publication/quotation rights; or
2. an outcome-blind protocol identifies the rule on development intervals and validates it unchanged on fresh
   intervals, while labeling it an empirical reconstruction rather than an official rule.

Production RHS may be used only after prediction for scoring. It cannot select among candidate SCADA rules.

## Resources and claim boundary

- **New paid data:** zero.
- **Current development data:** the two consumed 1 MiB R2 ranges only.
- **Fresh evaluation data:** two or more mechanically selected interval members, exact byte budget to be frozen
  before access; likely 2--4 MiB total.
- **Compute:** Mac CPU, seconds to minutes; no solver required for the component gate.
- **GPU:** zero V100/2060 hours. All three GPUs remain idle.

Even a clean RPN pass validates only a bounded parser/evaluator component. It does not establish an independent
NEMDE replay, exact counterfactual engine, participant behavior model, EcoMD validity or the NCS/NMI headline.

## Development topology update

A structure-only inspection of the four already known failed equations was performed after this audit and before
running any repaired arm. It showed that a literal bounds/`pop(0)` patch is insufficient. When Nempy recursively
collects an outer group, nested sibling `G` anchors lose their outer `GroupTerm`; the adjacency heuristic can then
assign the following sibling's members to the preceding anchor and strand the actual terminal anchor. This is the
observed path to the boundary exception.

The implemented development adapter therefore follows the explicit identifiers instead of adjacency:
`child/@GroupTerm == anchor/@TermID`. It recursively evaluates direct children on independent stacks and delegates
all group-free numerical operations to the unchanged pinned evaluator. Self-marked leading anchors are handled as
the documented first-member-removal case. This is a refinement of implementation topology, not an empirical
threshold change or repair validation. Plan:
`experiments/v14_aemo_nemde_rpn_repair_development/DEVELOPMENT_PLAN.md`.
