---
name: research-goal
description: >
  Drives the long-term EcoPhys research goal autonomously: reach one executable, experimentable,
  publishable topic. Use when the user says "research goal", "goal", "继续研究目标", "推进研究",
  "run/continue a discovery cycle", "explore new research topics", "find a publishable topic",
  "maintain/update the knowledge graph", "audit a re-entry trigger", or "check goal progress".
  Covers route-knowledge-graph maintenance, bounded F0-F3 topic-search cycles, and
  activation-gate advancement under research/discovery/protocol.yaml.
---

# Research goal loop

You are the driver of ONE persistent objective, not an assistant for this session only:

> Advance the EcoPhys research program until exactly one frozen topic holds `active` status with
> a machine card that passed every gate in `research/discovery/protocol.yaml` (`activation_gate`),
> an executable budgeted experiment plan inside the current compute envelope (2x V100 32GB +
> A800 40GB, never H20), and a venue-consistent evidence contract.

The goal is NOT an idea list, a narrative, a workshop draft, or a "promising direction".
Zero-survivor cycles are successful progress when they cheaply and correctly close a family.

Each invocation of this skill is one iteration of
**Orient -> Select -> Execute (bounded) -> Record -> Report**. Never skip Record.

## Authoritative sources (derive at runtime; never duplicate their content)

| Fact | Canonical source |
|---|---|
| Machine authority, stages D-3..D2, activation gates, funnel limits | `research/discovery/protocol.yaml` |
| Route statuses, failure lineage, reopen conditions | `.claude/memory/research_route_knowledge_graph.yaml` |
| Search procedure, five-part topic contract, archetype contracts, saturation rule | `docs/research_topic_exploration_runbook.md` |
| Currently authorized actions | `research/discovery/current_machine_decision.yaml` |
| Cycle history | `research/discovery/search_cycle_ledger.yaml` |
| Re-entry triggers | `research/discovery/reentry_trigger_ledger.yaml` |
| Prospective T0 forecasts | `research/discovery/forecast_ledger.yaml` |
| Topic worksheet template | `research/discovery/templates/screening_topic_worksheet.md` |
| Long-term memory index | `.claude/memory/MEMORY.md` |

The route graph is ~14k lines: query it with targeted searches (route id, `status:`,
`failure_codes`, family keywords). Never read it end to end.

## Persistent goal state

`research/discovery/goal_state.yaml` is this loop's only own artifact; create it if missing.
It records ONLY what cannot be derived elsewhere: current `mode`, a ranked `next_action_queue`
(each item: action, rationale, cost estimate), per-family cycle counters for the saturation
rule, and `session_history` pointers (date, mode, ledger/log refs). Never copy route statuses,
counts, or failure history into it — those belong in the canonical files above. Re-derive
`mode` from `current_machine_decision.yaml` and the ledger tail at the start of every session.

## 1. Orient (read-only, cheapest first)

1. `research/discovery/goal_state.yaml` (initialize if absent).
2. `research/discovery/current_machine_decision.yaml` — does authorized work exist right now?
3. Tail of `search_cycle_ledger.yaml` (last two cycles): counts, dispositions, survivors.
4. `research/discovery/reentry_trigger_ledger.yaml` — pending or qualified triggers.
5. Targeted route-graph queries for the families the queue touches (duplicates, blockers).
6. Today's and the most recent `logs/*.md` for in-flight work.

## 2. Select the next action — first match wins

| # | Condition | Action |
|---|---|---|
| A | `current_machine_decision.yaml` has `status: authorized` | Execute exactly its authorized scope; this outranks new exploration. Follow the AGENTS.md workflow for any compute work. |
| B | A machine card exists without an activation decision yet | Advance its outcome-blind D0 freeze: exact estimand, stop rules, budget, confirmation split; then present the activation case to the PI. |
| C | An F3 audit survived with a frozen pre-audit forecast | Draft the machine card outcome-blind from the worksheet/template; real evidence paths only. |
| D | Saturation: last two cycles in a family produced no machine card | Do NOT run a third relabelled cycle. Audit `reentry_trigger_ledger.yaml`; with no qualified trigger, either open a paper-only truth-asset preflight (named blocker + all contract parts in the runbook) or switch source lane/archetype. |
| E | Otherwise | Run ONE bounded F0-F3 cycle per the runbook. |

F0 sampling targets for any new 12-program cycle: >=2 `measurement_method`, >=2
`empirical_intervention`, <=6 `theory_mechanism`. Record a source-scarcity exception instead of
inventing weak questions.

## 3. Execute (one bounded unit per session)

- Funnel limits are hard ceilings: <=12 raw programs, <=6 quick screens, <=3 collision screens,
  <=2 full hostile audits, <=1 machine card. Stop earlier whenever a decisive result lands.
- Every raw program needs: market-native object, rival explanations H1/H0, one separating
  result, positive-answer AND null-answer value, source lane, archetype. An analogy or a method
  name is not a question.
- Escalation search order (stop at the first decisive hard failure): route-graph duplicate ->
  exact reduction / killer toy -> primary-work collision -> source/schema contract. Use web
  search for collision checks and cite specific primary works; never write "no paper to our
  knowledge" without a searched manifest.
- Freeze the F3 subject node and its full-T0 forecast in `forecast_ledger.yaml` BEFORE opening
  the fifteen-work manifest. A probability written after evidence opened is diagnostic only;
  never backfill it into calibration history.

## 4. Record (non-negotiable, before reporting)

1. Append the cycle — including zero-survivor cycles — to `search_cycle_ledger.yaml`, matching
   the existing entry shape (counts, dispositions, source_lane_counts, archetype_counts,
   efficiency, record_quality, notes).
2. On any terminal route decision, add or extend nodes/edges in the route graph following its
   own embedded `schema:` block (required fields, allowed statuses and edge types); pin evidence
   to immutable commits.
3. Run both validators and fix failures before ending the session:
   ```bash
   conda run -n ecophys python scripts/validate_research_discovery.py
   conda run -n ecophys python scripts/validate_research_route_graph.py
   ```
4. Append `logs/YYYY-MM-DD.md` (Session header if multiple per day; goal, what was done,
   results, open questions, next steps) per AGENTS.md work-log discipline.
5. Update `.claude/memory/` when a lasting fact changed; update `goal_state.yaml` (mode,
   counters, queue) last.

## Hard rails

- Forbidden before `active` status (protocol `forbidden_before_active`): outcome inspection,
  simulator execution, model implementation, EcoMD integration, dataset purchase, GPU use. A
  current machine decision file is the only override.
- Never reopen a `failed_closed` family by relabelling venue, mechanism, or method. Re-entry
  requires a qualified ledger entry; `candidate_harvest_authorized: true` only when a named
  blocker is actually removed.
- Never add placeholder evidence to a registry; a card exists only when its evidence paths are
  real files.
- Probability floors (e.g. the 15% hostile-T0 brake) are not truth thresholds; never
  terminalize on probability alone.
- Ask the PI (user) before: any activation-gate decision, sandbox authorization, purchase,
  outreach, or anything the protocol marks `require_explicit_authorization`. Present the
  outcome-blind case and stop.

## 5. Report format

End every run of this skill with exactly these four lines of content:

- Mode executed (A-E) and what was done.
- Goal distance: current best programs/cards and the specific gate each still fails.
- Cheapest next decisive action (top of `next_action_queue`).
- Any PI decision required now.
