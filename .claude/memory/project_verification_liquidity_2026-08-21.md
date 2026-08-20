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

Venue ceiling: a single GitHub result is a software/agent-systems paper. NMI requires a general agent-validation
externality plus prospective policy value and transfer to coding agents. NCS additionally requires a genuinely
new admission/scheduling result with a guarantee and a second independent computational domain.
