# Staged g42 authorization payload — DRAFT, NON-OPERATIVE

Everything under this directory is a draft. No validator scans it; no
canonical `research/discovery/` file exists for g42; no branch can run. The
sandbox becomes real only through the PI's authorization-only merge, which is
the promotion step below. Design rationale: `papers/proposal/
ecomd_g42_fixed_knot_moves_sandbox_preflight_2026-09-16.md`.

## Promotion mapping (the authorization-only merge)

| staged file (under this directory) | canonical target |
|---|---|
| manifest.yaml | research/discovery/sandboxes/g42_fixed_knot_moves_20260916.yaml |
| decision.yaml | research/discovery/sandbox_decisions/g42_fixed_knot_moves_20260916.yaml |
| genesis/events.jsonl | research/discovery/sandbox_artifacts/g42_fixed_knot_moves_20260916/events.jsonl |
| confirmation_derivation.json | research/discovery/sandbox_inputs/g42_fixed_knot_moves_20260916/confirmation_derivation.json |
| partition.yaml | research/discovery/sandbox_inputs/g42_fixed_knot_moves_20260916/partition.yaml |
| members/exploration.txt | research/discovery/sandbox_inputs/g42_fixed_knot_moves_20260916/members/exploration.txt |
| members/confirmation.txt | research/discovery/sandbox_inputs/g42_fixed_knot_moves_20260916/members/confirmation.txt |
| unit_contract.json | research/discovery/sandbox_inputs/g42_fixed_knot_moves_20260916/unit_contract.json |
| configs/g42_b01..b07.json | research/discovery/sandbox_inputs/g42_fixed_knot_moves_20260916/configs/g42_b01..b07.json |
| dependency_provenance.json | research/discovery/sandbox_inputs/g42_fixed_knot_moves_20260916/dependency_provenance.json |
| provenance.json | research/discovery/sandbox_inputs/g42_fixed_knot_moves_20260916/provenance.json |
| snapshot_manifest.json | research/discovery/sandbox_inputs/g42_fixed_knot_moves_20260916/snapshot_manifest.json |
| pre_execution_verification.json | research/discovery/sandbox_inputs/g42_fixed_knot_moves_20260916/pre_execution_verification.json |

All refs inside the payload already point at the canonical targets, so the
promoted bytes must equal the staged bytes at merge time.

## Promotion procedure

1. PI orders the authorization-only merge and fixes the authorization instant
   `STAMP` (UTC, `YYYY-MM-DDTHH:MM:SSZ`) and the preparation commit sha
   `COMMIT` (the commit carrying the engine, tests, image qualification,
   appendix, and this payload).
2. Refresh the verification record if needed, then re-freeze with:
   `conda run -n ecophys python research/paper_g/g42_fixed_knot_moves/stage_authorization.py --stamp STAMP --preparation-commit COMMIT --operative`
   (recomputes members → unit contract/configs/derivation → provenance →
   snapshot → asset fingerprint → partition → manifest → genesis entry →
   decision hashes, stamps `preparation_commit` into the snapshot, and emits
   operative decision wording; nothing else changes).
3. Copy each staged file to its canonical target exactly as mapped above.
4. Run both offline validators
   (`scripts/validate_research_discovery.py`, `scripts/validate_research_route_graph.py`).
5. Commit on the protected branch with the research-governance check; record
   the out-of-tree anchor copy under `~/.ecomd/discovery_sandbox_anchors/` as
   the launcher does on first event append.

After promotion, branch requests are opened per launcher mechanics (request
yaml + config under sandbox_artifacts/…/branches/<branch_id>/, CPU accounting
cumulative against the 14,400-second reservation, 8-branch cap).

## Frozen facts recorded here

- Image `sha256:3428e3025c64a17173365290951b780fcf9a0b2e998ffaa8e3445057cc31deda`
  (engine 1.1.1 + branch-aggregate runner); qualification report:
  `../image_conformance.json`.
- Launcher and incident handler are pinned by CANONICAL scripts/ paths — the
  launcher verifies its own path, so per-sandbox launcher copies are
  impossible by construction (memo §6 residual, resolved).
- Confirmation seeding needs no engine change: full confirmation unit ids form
  only after the designated NIST Beacon v2 pulse (see
  confirmation_derivation.json; status future_rule_only_no_pulse_access).
- Stop rule: any non-completed container quarantines the sandbox, charges the
  full reservation, forbids retry.
- Timestamps and hashes in this draft were stamped 2026-09-16T06:43:08Z
  (draft, re-staged after the 2026-09-16 adversarial audit and engine 1.1.1);
  they are replaced wholesale by the promotion re-stamp above.
