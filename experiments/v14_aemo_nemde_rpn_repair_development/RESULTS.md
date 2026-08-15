# NEMDE RPN-group repair development result

**Disposition:** `REJECT_GLOBAL_TERM_ID_TREE_REPAIR_NO_FRESH_VALIDATION`

**Development commit:** `76ca78133c77938ac895b8bbd9818ee1012fb4b6`

**Artifact SHA-256:** `07298146e9bc1075fbdb0b9fa010cc837ac6d1d0709b56e23a9771b6d178ff19`

## Bottom line

The explicit `GroupTerm -> G/TermID` tree is computationally complete but semantically wrong as a global NEMDE
RHS rule. It recovered all four baseline `IndexError` equations and introduced no new exception, but it severely
worsened the error distribution in both consumed regimes. No fresh validation is justified.

This is a useful kill result. AEMO's public guideline specifies the mathematics of an independent group stack, but
the audited public sources do not fully specify how nested/overlapping group structure is encoded in the production
XML. A plain parent-child interpretation cannot replace Nempy's adjacency/state-machine behavior. Continuing to
patch individual production errors would be target-conditioned reverse engineering, not a fair mechanism test.

The original decision remains `PARTIAL_INPUT_SIDE_DYNAMIC_RHS_RECONSTRUCTION`. Input-only replay is still
unavailable. The safe free-data boundary is solution-assisted replay with production RHS explicitly labeled as an
observed mechanical state; exact counterfactual NEMDE requires authoritative formulation access or a validated
engine obtained through collaboration/Queue access.

## Integrity

- Both baseline cases exactly reproduced the committed parent summary.
- Both repaired arms retained 100% dual-sentinel outcome and successful-value invariance.
- The repaired evaluator scored all `774/774` and `884/884` equations with zero structure errors.
- It evaluated 3,550 groups across 1,872 grouped RPN calls, with maximum depth four.
- The two consumed cases exercised no self-marked leading anchor.
- No AEMO/R2 request, solver, paid data or GPU was used.

The negative result is therefore not caused by a failed run, missing raw byte, output-RHS leakage or nondeterminism.
It is a semantic non-equivalence.

## Paired results

| Metric | Pre-5MS baseline | Pre-5MS tree | Post-change baseline | Post-change tree |
|---|---:|---:|---:|---:|
| scored / total | 772 / 774 | 774 / 774 | 882 / 884 | 884 / 884 |
| normalized median | `4.11e-10` | `7.22e-10` | `1.34e-10` | `2.06e-10` |
| normalized p95 | `0.00416664` | `0.50073642` | `0.00194488` | `0.31578724` |
| normalized p99 | `0.988812` | `1.08775588` | `0.00668113` | `1.47256155` |
| normalized maximum | `0.996800` | `27.50529515` | `0.50000078` | `17.87066458` |
| recovered exceptions | -- | 2 | -- | 2 |
| strict improvements | -- | 0 | -- | 1 |
| strict worsenings | -- | 57 | -- | 63 |
| crossed below `1e-3` | -- | 0 | -- | 1 |
| crossed above `1e-3` | -- | 42 | -- | 59 |

The p95 error increased by roughly 120-fold pre-5MS and 162-fold post-change. Median error remained tiny, again
demonstrating why a median-only validation would accept a badly wrong mechanical evaluator.

The sole strict improvement among equations scored in both arms was post-change `Q>YLTX_DS`, which moved from
normalized error `0.50000078` to zero. That isolated success does not license selecting a subset of group families:
the same global rule created 63 strict regressions in that case. In the pre case every changed jointly scored
prediction was worse.

## What was falsified

The development hypothesis assumed that every `GroupTerm` is an ordinary parent pointer to the unique `G` term
with matching `TermID`. The result falsifies that assumption as a complete production encoding rule. At least one
of the following must also matter:

- sequence position and implicit stack state;
- distinct leading, trailing, nested or overlapping group conventions;
- context-dependent reuse of term/group identifiers;
- a production formulation rule absent from the public Constraint Implementation Guidelines.

The result does not show that Nempy's current implementation is correct: its original p95 gate still fails and it
still throws four boundary exceptions. It shows that the proposed public-source repair is worse than the pinned
baseline and must be rejected.

## Research decision

1. Do not run this adapter on fresh intervals.
2. Do not repair only the four recovered constraints or the one improved family using their production errors.
3. Do not reopen the SCADA arm; its normative selection rule is also unresolved.
4. Treat open NEMDE recreation as solution-assisted unless production RHS is withheld from formulation and the
   full input-only path passes fresh gates.
5. If exact NEMDE counterfactuals become essential, seek authoritative formulation/Queue access and publication
   rights through an AEMO participant or qualified power-market collaborator.
6. For the V14 Lucas-test model ladder, prioritize a domain with a fully public executable mechanism, such as a
   permissionless on-chain market, rather than making unpublished NEMDE internals the critical path.

This is an engineering/mechanism-boundary result, not a paper claim. It changes no prospective outcome lock and
does not unlock model training or GPUs.
