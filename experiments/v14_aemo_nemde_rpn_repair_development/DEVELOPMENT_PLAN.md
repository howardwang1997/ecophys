# NEMDE RPN-group repair development plan

**Fixed:** 2026-08-15, before executing the structural repair on the two consumed cases

**Scientific role:** development-only mechanism localization; no pass/fail claim

## Motivation

The official-rule audit established the independent-stack semantics of an AEMO RHS group. A subsequent
structure-only inspection of the four already known exceptions showed why a three-line bounds patch is
insufficient: nested equations contain sibling `G` anchors, and the pinned evaluator guesses group ownership from
adjacency after stripping an outer `GroupTerm`. This can associate the preceding sibling anchor with the following
group and strand the real terminal anchor.

No RHS or SCADA value was used to reach this structural conclusion. The repair must use the explicit identifier
relation: a term belongs to the group named by its `GroupTerm`, and the group anchor is the `G` term whose `TermID`
matches that identifier.

## Fixed repair

The development arm wraps only the pinned Nempy `_rpn_calc` entry point:

1. deep-copy the resolved equation;
2. map unique `G/@TermID` anchors;
3. map every non-self `@GroupTerm` to its anchor, preserving source order among direct children;
4. treat `G` with `TermID == GroupTerm` as a leading self-marked anchor, not its own child;
5. recursively evaluate direct children on independent stacks;
6. replace each computed `G` anchor by an in-memory constant term carrying the group value, original factor and
   original operation;
7. remove all group annotations and delegate every numerical/RPN operation to the unchanged pinned evaluator;
8. retain missing anchors, duplicate anchors, cycles, empty groups and unreachable terms as explicit errors.

Input lookup, SCADA aggregation, defaults, generic-equation expansion and every non-group operator remain
unchanged. The arm is installed only in memory and does not modify the Nempy checkout.

## Fixed development outputs

For each consumed case and each arm (`baseline`, `rpn_tree`), report:

- dual-sentinel outcome and exact successful-value invariance;
- equation/reference/evaluation counts;
- normalized median, p95, p99 and maximum error;
- all failure IDs and error types;
- baseline-to-repair recovered and new-failure IDs;
- counts of strict error improvements, worsenings and exact ties;
- crossings below and above the original `1e-3` boundary;
- top 25 improvements and worsenings by paired normalized-error change;
- structural call/group/self-marker/depth/error counters.

The baseline must exactly reproduce the committed partial-result aggregate before the repair output is accepted.
No equation may be dropped, retried or replaced. No individual predicted, reference or SCADA value is retained.

## Interpretation lock

This run is allowed to reject or refine the repair implementation. It cannot validate the repair, change the
original partial decision, set fresh-sample thresholds, unlock a full day/solver, or support a paper claim. A
promising development result permits only a separately committed fresh-interval protocol with paired improvement
and non-degradation gates fixed before new RHS access.

## Data and compute

- Reuse the two consumed local 1 MiB ranges; zero AEMO and zero R2 requests.
- Use the clean pinned Nempy checkout and existing `ecophys` Conda environment.
- Mac CPU only, expected under one minute and under 1 GB RAM.
- Zero paid data and zero V100/2060 hours.
