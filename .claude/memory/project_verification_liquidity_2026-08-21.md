---
name: verification-liquidity-2026-08-21
description: "GREEN through formal outcome-blind D-1: GitHub's 2026-07-14 default Dependabot cooldown has enough public support for D0, while all queue/review/merge/security outcomes remain sealed."
metadata:
  node_type: memory
  type: project
---

# Verification liquidity after an agent safety throttle

The active branch is `dependabot-cooldown-verification-liquidity-2026-08-21`, forked from the immutable CoW RED
archive head. The candidate is not the occupied claim that dependency bots create PR/CI burden. It asks whether
GitHub's platform-wide default three-day Dependabot version-update cooldown, announced 2026-07-14, changes
autonomous arrival timing and spills over to the validation service received by unrelated human work.

The larger construct is **verification liquidity**: immediately available computational and human capacity to
check an agent proposal without delaying other proposals. GitHub is a first deployed test system, not a market
analogy and not an EcoMD rescue. The primary future outcome is earliest job start minus workflow-run creation for
human-triggered runs. The event study must use the historical `.github/dependabot.yml` at the 2026-07-13 cutoff,
pre-period bot-load exposure, matched non-Dependabot controls, runner-pool overlap, pre-trend and placebo tests.

Exploratory outcome-blind calibration used a top-100 active/high-star frame. It found 34 repositories with both
Dependabot configuration and Actions, 1,493 bot PRs in 2026-06-01--2026-07-31, 16 repositories with at least 20,
and a conservative 195 within-repository clusters separated by 24 hours. Public workflow/job schema and both
hosted and custom/self-hosted runner labels were observable. Timing, conclusion, review and merge outcomes were
not inspected.

The formal D-1 contract is
`configs/agent_markets/github_dependabot_cooldown_dminus1_v1.yaml`. It freezes a ten-page top-star frame, a
pre-event 2026-05-19--2026-07-13 rate window, allowed fields, forbidden outcome persistence and stop gates.
D-1 is Mac CPU only, under 20 core-hours/5 GB, with no GPU, paid data, H20 or EcoMD. Commit and push the plan before
the formal frame query. Full plan:
`papers/proposal/dependabot_cooldown_verification_liquidity_plan_2026-08-21.md`.

Implementation now includes `ecomd/data/github_verification_liquidity.py` and
`scripts/audit_github_dependabot_cooldown_dminus1.py`: typed sanitizers, historical config classification, a
recursive forbidden-key guard, deterministic per-repository checkpoints and immutable allowed-record manifests.
The final ten-repository smoke used 49 public requests in 21.25 seconds, saw 51 bot PRs/20 24-hour clusters and
passed outcome-seal, config-recovery, workflow-access, queue-field-presence and hash checks. Its scale gates failed
by design. Allowed-record canonical SHA is `7d9af87a…c62b`; no queue/review/merge/security value was persisted.
Because live star counts changed across smoke snapshots, formal acquisition now freezes its first frame to disk and
keeps an append-only response-hash journal; resume cannot silently select a new repository ranking.

Formal D-1 ran from clean pushed implementation commit `bf23db8d3` and passed all eleven frozen gates. The fixed
1,000-repository frame contains 226 default-treated repositories with Actions, 72 high-support treated
repositories, 447 eligible no-Dependabot controls, 9,280 pre-event bot PRs and 2,499 24-hour arrival clusters.
Historical-config recovery is 97.44%; workflow access and required queue-field presence are both 100% in the
frozen probe. The outcome seal and independent 1,003-file recursive scan pass. Allowed-record canonical SHA is
`ae7c9f36…b423`; formal result canonical SHA is `e697028e…c37e`. No explicit zero-day opt-out exists in the frame,
so D0 must match against the frozen no-Dependabot pool and use the 63 already-cooled repositories only as a
negative control. GREEN authorizes freezing D0, not opening outcomes or claiming an effect. Full result:
`papers/proposal/dependabot_cooldown_verification_liquidity_dminus1_result_2026-08-21.md`.

D0 is now drafted and machine-frozen before its formal identity acquisition. The deterministic candidate ledger
contains 72 treated, 447 primary-control candidates and 33 high-support already-cooled negative controls; canonical SHA is
`b6c21ed8…5c62`. Primary pre/post windows are 2026-06-16--07-13 and 2026-07-17--08-13 with 07-14--07-16 blacked
out. Primary human runs are first-attempt user `push` runs; PR/manual runs are secondary. D0 fixes hash-based daily
sampling, pre-only optimal 1:3 matching, intentional workflow-wait flags, official incident sensitivity and a
30-treated shared-runner-pool gate. The 2026-08-22--10-16 prospective holdout cannot be opened before 10-17 UTC.
D0 remains outcome-blind and CPU/API-only. Full freeze:
`papers/proposal/dependabot_cooldown_verification_liquidity_d0_freeze_2026-08-21.md`.
Before any D0 API acquisition, v2 superseded v1 to resolve one implementation ambiguity: prequalification now
requires five pre primary runs, finite covariates, known human runner class and a successful human schema probe;
the matched treated set is the largest deterministic feasible prefix of at least 60. V2 does not change candidate
IDs, windows, estimand, forbidden outcomes or numerical gates. The first deterministic 11-repository smoke then
completed its identity checkpoints but generated no result because the generic outcome guard rejected the external
GitHub Status field name `started_at`. RSSHub alone exposed 21,024 run identities in the frozen window, so formal
collection is expected to cross several API-rate windows and must use checkpoints rather than excluding large
repositories. V3 renames only the external incident fields to `reported_start_utc` and
`reported_resolution_utc`; it is now authoritative and leaves all scientific design content unchanged.

The v3 resume completed end to end over 46,862 run identities, 28 schema/workflow probes, 22 official incidents
and 692 journaled responses. Its deterministic 3/6/2 smoke subset has two prequalified treated and zero
prequalified controls, which is an engineering observation only. The resulting `/tmp` artifact exposed Python
`Infinity` on the empty-match path and is superseded as non-strict JSON. Before formal D0, writers now reject
non-finite JSON; missing balance is `null`. A second contract audit found that probe-only workflow parsing did not
exclude intentional waits for every selected primary D1 run. The implementation now checkpoints historical
workflow structure per unique repository/head-SHA/path and freezes IDs only after missing/flagged primary runs are
removed. Formal acquisition may stop before probes only when a conservative identity-support upper bound—counting
inaccessible/truncated repositories as possible passes—already fails a frozen necessary gate.

Formal D0 first started from clean pushed `c98b4ed86` at 2026-08-21 04:41 UTC. It preserved nine complete
repository checkpoints and 3,095 response hashes but produced no result/manifest: one `rust-lang/rust` shard hit
three consecutive SSL EOFs. Runtime v1 had eagerly submitted every missing repository, so executor shutdown kept
using requests after the failed future while the main loop no longer persisted completions. Runtime v2 is a
transport-only supersession: at most four tasks are in flight, peer successes are drained/persisted, and each
completed ≤900-run time shard is immutable. The nine whole-repository checkpoints and journal remain valid;
uncheckpointed responses will be repeated. A new end-to-end v2 engineering smoke reused all 11 sanitized smoke
checkpoints, completed with 43 status responses, strict `null` balance, a zero-line gzip sample and a passing
recursive seal scan. Canonical/file SHAs are `b097af1f…55ef`/`ce81d11d…8e67`. It is non-scientific. All 38 related
tests, Ruff, strict mypy and compilation pass.

Formal runtime-v2 acquisition resumed from clean pushed `f64d3c509` and has crossed seven GitHub core-rate
windows/resumes. As of 2026-08-22 17:39 NZST it has 134/552 complete repository checkpoints, 3,470 immutable
completed time-shard checkpoints and 32,375 append-only transport observations. The first three window boundaries
preserved 40/670/7,847, 76/1,303/12,598 and 102/1,931/17,349 whole/shard/journal counts. A later `nodejs/node` leaf
exhausted the SSL EOF retry policy at 116/2,430/21,644; bounded shutdown preserved peer successes, and the next
window retried that leaf successfully. The sixth resume ended at 127/2,987/27,621 before its terminal console
buffer could be retained; all 1,223 new journal rows were HTTP 200, but its exact exception is unknowable. The
seventh resume therefore persisted complete stdout/stderr and stopped normally at the frozen reserve with
134/3,470/32,375 and a final core balance of 246; all 4,754 new rows were HTTP 200. Every observed rate-reserve
stop was fail-closed. No formal result or manifest exists, the worktree was clean during acquisition, and all D1
outcomes remain sealed. These counts are transport progress, not a feasibility or effect result.

Venue ceiling: a single GitHub result is a software/agent-systems paper. NMI requires a general agent-validation
externality plus prospective policy value and transfer to coding agents. NCS additionally requires a genuinely
new admission/scheduling result with a guarantee and a second independent computational domain.
