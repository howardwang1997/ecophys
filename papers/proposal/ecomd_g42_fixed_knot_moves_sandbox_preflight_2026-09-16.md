# g42 fixed-knot learned moves — disposable exploration sandbox preflight appendix (2026-09-16)

Status: PRE-AUTHORIZATION ONLY. This appendix freezes the g42 sandbox design and
records the preparation evidence. It authorizes nothing. Execution requires the
separate authorization-only merge of the staged manifest/decision/genesis payload
ordered by the PI (Bourse preflight precondition 6). No branch has run. No pulse
has been accessed. No scientific outcome exists.

Companion records: `papers/proposal/ecomd_sandbox_preflight_memo_2026-09-16.md`
(launcher hardening, conformance, platform gate), `papers/proposal/
bourse_disposable_market_counterexample_preflight_2026-08-25.md` (campaign
envelope), `papers/proposal/ecomd_paper_g_response_dx_preflight_2026-09-11.md`
(the g_response_dx precedent this staging follows).

## 1. Scope: engine-contract alignment with the Bourse preflight

The Bourse memo freezes a contract STRUCTURE (pinned engine + OCI digest +
isolation + public-randomness confirmation + authorization-only merge), not a
specific engine. g42 satisfies it item by item:

1. **Pinned engine, hashed.** `research/paper_g/g42_fixed_knot_moves/model.py`,
   engine `g42_fixed_knot_moves_engine_1.1.1`, source sha256
   `ae483e95fc4d7c1746b0742527082b0e49fcd326151b8690e19a2b254883bd27`. Pure
   Python standard library; the only randomness source is a pure-integer
   PCG64-XSL-RR generator; bit-exact replay of every deterministic report field.
2. **Pinned OCI image.** `ecomd-g42-fixed-knot-moves:preflight` =
   `sha256:3428e3025c64a17173365290951b780fcf9a0b2e998ffaa8e3445057cc31deda`,
   base `python:3.11-slim-bookworm` pinned at
   `sha256:2e32f7d302adc1c37428355c1e646897c0c53f4fd60b6a551245fb90ee129f91`.
   Image qualification (outcome-free: 14 isolation checks, 4 conformance cases,
   docker-cp byte-identity of image sources) re-run green after the final
   rebuild: `research/paper_g/g42_fixed_knot_moves/preparation/image_conformance.json`.
3. **Isolation.** Launcher `scripts/run_research_discovery_sandbox.py`
   (sha256 `4e8ae8a7aa1a3ed2b5d26fd765c5fa524d9167873218bfa2f4421ff0b33654ef`),
   incident handler `scripts/quarantine_research_discovery_sandbox.py` (sha256
   `5cda87cf44ac50e78f9dd23ee4e268ec4099252d3536bdb1841db62bc2d67e4e`):
   network none, read-only rootfs, cap-drop ALL, no-new-privileges, pids 128,
   cpu ulimit per branch, non-root uid, no secrets, no repo tree mount.
4. **Beacon/pulse/domain-separator/seed-derivation freeze.** Section 4 below;
   all pulse values strictly future; no pulse access at preparation.
5. **v2 manifest + decision + immutable inputs + single authorized genesis
   event.** Staged draft payload under
   `research/paper_g/g42_fixed_knot_moves/preparation/authorization/`;
   promotion mapping and re-hash procedure in its README. The merge is the PI's
   authorization act.
6. **Authorization-only merge before any branch.** No canonical
   `research/discovery/` file has been created for g42; validators stay green on
   the pre-merge tree.

Campaign envelope (stricter than schema): 14,400 CPU-s / 1e9 bytes / 0 GPU /
$0 / ≤ 8 branches / 7 days. Planned consumption: 7 branches, 12,960 CPU-s
(Section 3); 1,440 CPU-s plus the 8th branch slot remain as in-envelope
contingency. A positive result yields at most a permanently tainted D-3 child
card (screening-question motivation only); this estimate is unchanged from the
Bourse memo's 5-10%.

## 2. Engine v1.0.0 → v1.1.0 defect record (found in preflight, fixed before freeze)

During local rate probing (measurement only, outside any sandbox), a
`g42_probe_uniform_000` unit (0_1, N=128, T=1.0, uniform, ≤10k proposals)
raised `EngineError("all projection directions ambiguous: [vertex projection
coincidence x4]")` from the PERIODIC corner-flip recertification. Root cause:
a trajectory-dependent tail event — the accepted conformation happened to be
uncertifiable under all four frozen projection directions at the moment of the
832nd accepted corner flip — the 13th periodic recertification (the engine
rechecks the certificate at every 64th accepted corner flip). Seed constructors
and the frozen test sizes are unaffected; a different unit_id seed completed.

Why this was campaign-fatal under v1.0.0: the launcher runs one container per
branch, and ANY non-completed container quarantines the sandbox with the full
reservation charged and retry forbidden (g_response_dx precedent, 3-minute
lifespan). A single tail ambiguity in 224 units would end the campaign.

Fix (engine 1.1.0, all changes pre-authorization):

- New `certify_current(vertices) -> int | None` seam: returns None when every
  frozen projection direction is ambiguous; any other certification error is a
  genuine defect and still propagates.
- Periodic corner recertification and the final conformation check now map
  ambiguity to a graceful terminal: `completed_reason =
  "certification_ambiguous"`, partial samples preserved, `final.determinant`
  null. An unambiguous WRONG determinant remains a fatal invariant violation.
- Pivot-proposal ambiguity handling no longer swallows non-ambiguity
  EngineErrors into `ambiguity_rejected` (v1.0.0's bare `except EngineError`
  could mask real bugs); only true all-direction ambiguity counts.
- New tail statistics `rg2_tau_int_tail` / `rg2_ess_tail` computed on the
  second half of the thinned Rg^2 series: a transient-robust screening
  criterion. Rationale: full-trajectory means made T=1.0 and T=3.0 units
  nearly indistinguishable in probing because the equilibration transient
  dominates; this is the same failure mode as the project's zeta_ED burn-in
  artifact, and the frozen assess rule therefore uses tail-tau ratios, not raw
  means.
- Trajectory and draw order unchanged from 1.0.0 by construction: the new code
  paths draw no variates and are unreachable on trajectories that never hit
  certification ambiguity, so the RNG stream is identical. No archived 1.0.0
  report exists for a field-by-field comparison; the replay instead pins the
  shared trajectory point: the same `g42_probe_uniform_000` config that
  crashed under 1.0.0 now terminates gracefully at the identical point
  (proposal 9680, 387 samples retained, `certification_ambiguous`, 0.92 s
  wall).

Tests: `tests/test_paper_g_g42_engine.py` 38 passed at the 1.1.0 freeze (32
prior + 6 new: seam delegation, graceful terminal, wrong-determinant fatality,
tail statistics, branch-envelope execution and mismatch rejection); ruff and
`mypy --strict` clean on model.py and runner.py; image rebuilt and re-qualified
after the runner change.

### Engine 1.1.1 hardening (found by the 2026-09-16 adversarial audit; Section 7)

Four confirmed engine-level defects, all fixed before the payload was
re-staged; version bumped to `g42_fixed_knot_moves_engine_1.1.1`:

- Low-temperature acceptance could raise `OverflowError`: at small T the
  Boltzmann factor `math.exp(-beta * dE)` overflows for downhill moves before
  the `min(1, …)` clamp. The product exceeding max float is mathematically
  greater than 1, so the clamp now maps the overflow to acceptance 1.0 —
  bit-identical in every case where 1.1.0 did not raise, and 1.1.0 would have
  crashed the container (quarantine) on such a trajectory.
- A context policy whose multipliers made some bucket's total weight zero was
  accepted at construction and only failed at draw time; construction now
  rejects any non-positive bucket total.
- The frozen assess rule now also excludes units whose `rg2_var_tail` is 0
  (degenerate tail: the tau estimator's 0.5 floor is indistinguishable from
  ideal decorrelation); the report gained the marker.
- The runner now rejects a unit envelope whose inner `unit_id` disagrees with
  its key (key/body binding), closing a swap-between-units path.

Tests grew to 44 (the 6 new cover each fix plus runner-main tar emission and
branch-mismatch rejection); ruff and `mypy --strict` clean on the package;
image rebuilt and re-qualified at the digest pinned above.

## 3. Frozen question space

Hypothesis id: `context_move_selection_matched_budget_decorrelation`.
Hypothesis: context-bucket proposal selection (P3) reduces the integrated
autocorrelation time of Rg^2 relative to uniform proposals (P0) at matched
total proposal budget in fixed-knot lattice rings.
Multiplicity family: `g42_fixed_knot_moves_7_cells_4_policies_8_seeds`.
Frozen test ids: `rg2_tau_int_tail_ratio_p0_over_p3` (primary),
`rg2_ess_tail_ratio_p0_over_p3`, `contacts_mean_equilibrium_consistency`
(secondary).
Falsifier (frozen assess rule): apply only to completed paired units; primary
statistic is the per-cell tail-tau ratio P0/P3 pooled across seeds; secondary
are the ESS-tail ratio and contacts-mean equilibrium consistency. Units ending
`certification_ambiguous` or `cpu_budget` are excluded per the frozen exclusion
rule, as are units whose `rg2_var_tail` is 0 (degenerate tail: the tau
estimator's 0.5 floor is indistinguishable from ideal decorrelation); if >50%
of a cell's units are excluded the cell is void. No threshold, seed, or policy
replacement. Either answer is screening-question motivation only (D-3 child
card at most); no topic-status promotion.

Cells and policies (7 x 4 x 8 = 224 exploration units, ids
`g42_explore_<cell>_p<p>_s<k>`, k = 0..7):

| cell | knot | N | T | proposals | thin | branch | branch CPU-s | unit CPU-s |
|---|---|---|---|---|---|---|---|---|
| n96_01_t1 | 0_1 | 96 | 1.0 | 500,000 | 1000 | g42_b07 | 1440 | 41 |
| n128_01_t1 | 0_1 | 128 | 1.0 | 400,000 | 1000 | g42_b01 | 1920 | 56 |
| n128_01_t3 | 0_1 | 128 | 3.0 | 400,000 | 1000 | g42_b02 | 1920 | 56 |
| n160_31_t1 | 3_1 | 160 | 1.0 | 400,000 | 1000 | g42_b03 | 1760 | 51 |
| n160_31_t3 | 3_1 | 160 | 3.0 | 400,000 | 1000 | g42_b04 | 1760 | 51 |
| n256_41_t1 | 4_1 | 256 | 1.0 | 180,000 | 500 | g42_b05 | 2080 | 61 |
| n256_41_t3 | 4_1 | 256 | 3.0 | 180,000 | 500 | g42_b06 | 2080 | 61 |

Measured single-unit wall times on the qualification host: 0_1@96 ~25 s,
0_1@128 ~32-40 s, 3_1@160 ~32 s, 4_1@256 ~24-40 s; every unit CPU cap keeps
~1.4x or more headroom over the slowest measured unit. Per-unit cap =
(branch CPU − 128) // 32 = 41/56/56/51/51/61/61 s in branch order b07,
b01..b06: the 128 s branch-level reserve keeps the worst-case all-capped
branch (32 x unit cap + container startup) inside the launcher wall deadline
of branch CPU − 42 s, so even a branch where every unit runs to its internal
cpu cap completes instead of being wall-killed and quarantined. The container
cpu ulimit equals the branch CPU (14400-s reservation accounting is
cumulative); per-unit deadlines are additionally enforced inside the engine
(checked every 64 proposals) and end the unit gracefully at `cpu_budget`.

Policies: P0 uniform; P1 corner-heavy {corner 4, pivot 1, self_loop 1}; P2
pivot-heavy {1, 4, 1}; P3 context table {1, 1, 1} with multipliers corner
[4, 2, 1], pivot [1, 2, 4], self_loop [1, 1, 1] over Rg^2 buckets. The bucket
thresholds are frozen design constants rounded to one decimal at preparation
and consumed by the engine as exactly these literals (any scaling-law origin
is motivational only, not evaluated at runtime): N=96 [20.6, 107.2], N=128
[25.4, 150.5], N=160 [29.5, 195.4], N=256 [40.3, 339.7]. A context table whose
multipliers zero out a bucket's total weight is rejected at policy
construction. Exact-Fraction MH ratio throughout.

Confirmation templates: P0 and P3 only, all 7 cells, 8 seeds → 112 templates
(Section 4).

Runner: branch-aggregate mode mirroring g_response_dx — one container per
branch executes the 32 frozen unit configs in `unit_ids` order and emits a
single deterministic tar member `exploratory_response.json`
({"branch_id", "epistemic_class", "units": {unit_id: report}}); any fatal unit
error kills the container (quarantine); graceful terminals
(`proposal_budget`, `cpu_budget`, `certification_ambiguous`) land per-unit.

## 4. Item-4 freeze: beacon, pulse rule, domain separator, seed derivation, outage fallback

`preparation/authorization/confirmation_derivation.json` freezes the g_response_dx
NIST Beacon v2 contract with the g42 domain construction:

- Provider NIST Randomness Beacon v2; endpoint
  `https://beacon.nist.gov/beacon/2.0/pulse/time/next/{unix_milliseconds}`;
  pulse rule "first signed pulse strictly after T; query pulse/time/next/{1000*T}".
- T = ceil(max(g42 sandbox terminal UTC epoch seconds, D0 freeze UTC epoch
  seconds)) + 600. Anti-selection: D0 timestamp, unit templates, and protocol
  immutable before T; no refreeze, pulse replacement, or template reordering
  after observing a pulse.
- Derivation: unit_id = `g42_confirm_` + first 16 hex characters of
  pulse.outputValue + `_` + template; engine initstate =
  int(SHA256(UTF8(unit_id)).digest()[:16], "big") with the frozen
  INITSEQ_EXPLORATION stream tag. The domain separator is the fixed
  `g42_confirm_` prefix; templates are frozen in members/confirmation.txt and
  are exactly the P0/P3 x 7 cells x 8 seeds enumeration. No engine change was
  needed for confirmation seeding.
- Failure policy: if the designated pulse or its verification is unavailable,
  confirmation stays sealed; no alternate pulse/provider/seed/template.
- Release gate: g42 sandbox terminal receipt AND independently frozen D0 both
  required (schema-const `after_sandbox_terminal_and_d0_freeze`).
- Status at freeze: `future_rule_only_no_pulse_access`. No confirmation
  generator or retrieval code exists in the scientific image; no pulse has
  been queried.

## 5. Staged authorization payload and promotion procedure

Staged under `research/paper_g/g42_fixed_knot_moves/preparation/authorization/`
(draft, non-operative): manifest.yaml (schema v2), decision.yaml (schema v2
draft), genesis/events.jsonl (seq-0 `authorized` event only),
confirmation_derivation.json, partition.yaml (224 exploration / 112
confirmation), members/{exploration,confirmation}.txt, unit_contract.json,
configs/g42_b01..b07.json, provenance.json, snapshot_manifest.json,
pre_execution_verification.json, README (promotion mapping + re-stamp/re-hash).

Promotion = the PI's authorization-only merge: copy each file to its canonical
`research/discovery/` path per the README mapping, re-stamp created_at /
decided_at / occurred_at to the authorization instant, re-run
`stage_authorization.py --stamp <instant> --preparation-commit <sha>
--operative` to recompute the hash chain (members → unit
contract/configs/derivation → provenance → snapshot → asset fingerprint →
partition → manifest → genesis entry → decision) with the preparation commit
stamped into the snapshot and operative decision wording, commit. Then and
only then may a branch request be opened.

Mechanical constraint discovered at preparation (memo §6 residual, resolved):
the launcher verifies that the manifest's launcher and incident_handler refs
resolve to ITS OWN canonical scripts/ paths, so per-sandbox launcher copies
under sandbox_inputs/ are impossible by construction. The manifest pins the
canonical scripts by sha256; snapshot_manifest.json records the same digests
as the freeze-time provenance.

Stop-rule reminder: any non-completed container quarantines the sandbox, the
full reservation is charged, and retry is forbidden. With engine 1.1.1 the
only remaining non-completed causes are a fatal invariant violation (real
defect — correct to stop) or host-level interruption.

## 6. Named residuals and PI decision points

1. Beacon reuse: confirmation uses NIST Beacon v2 exactly as g_response_dx
   (same provider/endpoint family, new domain separator). Confirm or name an
   alternative before the merge.
2. D0-freeze anchor wording in the derivation's time_rule/release_gate
   ("independently frozen D0"): the D0 record is the verification-liquidity
   sealed transport; confirm the g42 confirmation may anchor to it.
3. Commit batching: engine v1.1.1 + runner + tests + image reconformance +
   this appendix + staged payload in one preparation commit, or split
   (engine/tests first, staging second). Snapshot manifest stamps the chosen
   commit at promotion via `--preparation-commit`.
4. Anchor backup (memo §6): whether to mirror the out-of-tree anchor
   ~/.ecomd/discovery_sandbox_anchors/ to a second medium.
5. Remaining launcher residuals from the memo (same-uid anchor erase,
   ms-scale config-swap window, first-launch --base-ref operator trust) are
   accepted as-is for g42; no new residual was introduced by this staging.

## 7. Adversarial audit record (2026-09-16, pre-remediation of this appendix)

A five-dimension adversarial audit workflow (27 agents: 5 dimension finders,
per-finding refuters, synthesis) swept all g42 deliverables — engine, runner,
staged payload, this appendix, the memo, and the launcher contract. 22
findings survived adversarial refutation (2 blockers, 6 majors, 14 minors);
every one was fixed before the payload was re-staged. The two blockers were
both in my own staged payload, not in the engine:

1. The asset fingerprint was `sha256(model.py)` — a formula the sandbox
   validator does not use — and the snapshot hashed partition/provenance,
   creating a fingerprint ↔ snapshot ↔ partition cycle. Fixed by restructuring
   to the dx-precedent shape: the snapshot covers source + preparation files
   only, and the fingerprint is derived at staging as
   `sha256(canonical_json({asset_key, kind, snapshot_sha256, source, version}))`
   per `scripts/validate_research_discovery.py`.
2. The manifest's `evidence_refs` named an id no registry or route-graph node
   carries. Fixed by registering the `g42_fixed_knot_moves_preflight` locator
   (kind `private_asset_preflight`) on the g42 route-graph node, mirroring the
   `response_dx_preflight_formal` precedent.

Other fixed findings: the per-unit CPU caps left no structural headroom (a
fully cpu-capped branch would be wall-killed and quarantined — hence the
(branch − 128)//32 redesign in Section 3); the low-temperature
`OverflowError` and zero-bucket acceptance (Section 2, engine 1.1.1); the
corner-flip ordinal in Section 2 (832nd, not 64th); threshold wording that
read as runtime-derived instead of frozen constants; missing promotion-time
`--preparation-commit`/`--operative` steps; the memo §6 item-2 claim that
per-sandbox launcher copies are "preferred" when the launcher's canonical-path
self-verification makes them impossible (corrected in place). No finding
touched the frozen question space: cells, sizes, temperatures, proposal
budgets, thinning, policies, seeds, and the primary/secondary statistics are
unchanged from the original freeze; the only budget-contract change is the
per-unit cap formula above.

Post-fix state: 44/44 engine tests, ruff and `mypy --strict` clean on the
package, image rebuilt and re-qualified (digest in Section 1), payload
re-staged and its chain independently re-verified against the validator
formula, both offline validators green on the pre-merge tree.

No compute beyond seconds-scale local spot checks was used at preparation.
All rates were measured on the qualification host outside any sandbox; no
scientific outcome of the frozen question space was observed.
