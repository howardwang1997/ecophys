# A-2 iteration 1 record — Part 4 gap audit and implementation (2026-09-05)

Machine decision: `research/discovery/decisions/truth_asset_a2_platform_qualification_20260905.yaml`
(SHA-256 `d4007a212fe6222df14859959dea6c2371524336e06f0e287263b372f5e64712`).
Governing contract: A-3 plan Part 4
(`papers/proposal/ecomd_truth_asset_capability_build_plan_2026-08-26.md`, SHA-256
`553f773be7ce39f3a8b331a8d1f354e544c2e460b4334d03e4088f5a134c2431`).
Status: **iteration 1 completed; conformance and replay PASS; engineering iteration count 1 of 2
before the Part 8 stop rule.**

## Field-by-field Part 4 gap audit of the platform seed

| Part 4 requirement | Seed state (lab-asset-v2) | Iteration-1 action |
|---|---|---|
| `request_id`, `order_id`, `execution_id`, `actor_id`, `session_id` | present | none |
| `rejection_id` | absent | added engine-level `R%08d` counter on every rejection family |
| replacement/parent chain IDs | absent (no replace operation) | added `REPLACE_REQUEST`/`ORDER_REPLACED`/`REPLACE_REJECTED` events, `order_parent` map, `lineage_root`, `parent_order_id` |
| `role` | absent | added `actor_roles` to the prestate (default `trader`), validated, recorded on request/execution payloads |
| client/receipt/matching timestamps | present (`ThreeClocks`) | none |
| original/executed/residual quantity; maker/taker flags | present | none |
| reason-coded rejections | order/cancel/latency families present | added 13-code replace family; all rejections carry `rejection_id` |
| pre/post best bid/ask per accepted action | absent from payloads (only hashes) | added `pre/post_best_bid/ask` to `ORDER_ACCEPTED`, `EXECUTION`, `ORDER_CANCELLED`, `ORDER_REPLACED` |
| full-book state hash per accepted action | present (identity + aggregate hashes) | extended with `order_parent` and `rejection_counter` |
| replay prestate | endowments, induced values, schedule, initial book, rule config, RNG state, assignment-key commitment present | none |
| deterministic replay check | present (`replay.py`) | extended to re-issue replace requests |

Schema version bumped `lab-asset-v2` → `lab-asset-v3` (grammar additions). The versioned schema
artifact is frozen at A-2 exit, not now.

## Replace semantics (frozen by this iteration)

Atomic cancel-and-resubmit validated with the old order's reservations temporarily removed by
exact positional pop/restore (queue position is index-exact; no sorting is used, so initial-book
identifier ordering cannot perturb FIFO). On success the old order becomes `replaced`, the new
order carries `parent_order_id` = the old order's lineage root, and the new order may cross and
execute against the opposite book. Rejections are reason-coded, leave the old order resting
byte-identically, and record pre/post quotes.

## Fixture and pilot results (Mac CPU, engineering-only)

- `scripts/lab_asset/run_conformance.py`: `lab_asset_conformance_suite=PASS` (31 tests; prior 23
  plus 8 new covering replace lifecycle, crossing replace, rejection families, sequential
  `rejection_id`, resource-freeing validation, pre/post quotes, roles, and replace-tape replay
  plus tamper detection).
- Ruff clean on `scripts/lab_asset/` and both test files.
- Robot pilot: 4 paired-seed sessions per arm, 5,000 steps, both arms `all_replays_ok: true`
  with the replace grammar exercised (mean replace intensity 6.4%/6.0% of tape records; FIFO arm
  mean spread 1.112 ticks, random-unit arm 1.126 ticks). Manifest:
  `experiments/lab_asset_a2/iteration1_20260905/robot_pilot_manifest.json` (SHA-256
  `705b628080a07b46a5cf466a1c8e7d9307e6f7e41f9987bfd67210663fec6882`), labeled
  `engineering_only`, `not_route_evidence`.
- Pilot outputs are pipeline evidence only; they are not laboratory outcomes and not route
  evidence, per the A-3 plan and the machine decision.

## Deviations recorded

- `session_id` is a tape-level attribute (SESSION_START payload + prestate hash) rather than a
  per-event field; the tape belongs to exactly one session. Recorded as a deliberate schema
  decision, revisitable at A-2 exit freeze.
- `role` is resolved from the prestate (not client-supplied) so it cannot be spoofed in flight.

## Stop-rule evaluation

No conformance or replay failure occurred; engineering iteration counter = 1. Remaining known
Part 4 residuals for iteration 2: none identified in the tape grammar; the A-2 exit checklist
(schema freeze as a versioned artifact plus a published conformance fixture set) is the next unit.

## Authorization boundary (unchanged)

No human participants, outreach, ethics filing, treatment adjudication, candidate harvesting,
topic card, route re-entry, EcoMD integration, GPU use, or market-data outcome access occurred or
is authorized by this record.
