# Dependabot cooldown verification-liquidity D-1 result — 2026-08-21

## Formal decision

**GREEN: the free public-data route has enough support to freeze D0 while all queue, review, merge and security
outcomes remain sealed.**

This is a data- and design-feasibility decision, not evidence that GitHub's cooldown changed human validation
delay. The formal run used the frozen preregistration at commit `9d365a98f` and the clean, pushed implementation
commit `bf23db8d3e5d5d7ea067fa301d34b099aac3fa45`. It completed in 1,469.34 seconds on Mac CPU with no GPU,
paid data, EcoMD or H20.

Canonical result payload SHA-256:
`e697028ee06bf5ef4f042bc5297e7c2449a9f15b54dc69ad21905d6c253fc37e`.

## Frozen-gate accounting

| Gate | Observed | Frozen requirement | Result |
|---|---:|---:|---|
| unique frame repositories | 1,000 | at least 800 | PASS |
| default-treated repositories with Actions | 226 | at least 100 | PASS |
| high-support default-treated repositories | 72 | at least 50 | PASS |
| pre-event Dependabot pull requests | 9,280 | at least 1,000 | PASS |
| within-repository 24-hour arrival clusters | 2,499 | at least 200 | PASS |
| eligible no-Dependabot controls | 447 | at least 100 | PASS |
| historical config recovery | 97.44% | at least 90% | PASS |
| workflow-run access in frozen probe | 100% | at least 90% | PASS |
| required job-start field presence | 100% | at least 95% | PASS |
| forbidden outcome persisted | none | none | PASS |
| deterministic derived-record hash | exact | exact | PASS |

The 1,000 repositories split into 226 default-treated, 63 already-cooled, nine ambiguous and 702 without a
cutoff Dependabot configuration. No repository in this frame was classified as an explicit zero-day opt-out.
Consequently, D0 may use no-Dependabot repositories as its frozen primary control pool and already-cooled
repositories as a negative-control cohort, but it may not invent an opt-out comparison after seeing outcomes.

The 72 high-support treated repositories contain at least 20 pre-event bot PRs each. Their median is 40 and their
observed range is 20--435. These values are exposure support only. They do not imply that the cooldown was obeyed,
that CI demand changed or that human work waited differently.

## Independent seal and integrity audit

After the formal process exited, a separate read-only verifier:

- recomputed the gzip file SHA-256 as
  `74dc95a2d9e20d0bfb86feb48bed4d1b741877f4d528880981e1427cb5212448`;
- decoded all 1,000 allowed records and recomputed their canonical SHA-256 as
  `ae7c9f3686f9da2f16dd2c3d32680bf8679de72c8d4c8a6316006cc97690b423`;
- recomputed the result and manifest canonical hashes exactly;
- recursively scanned 1,003 raw/checkpoint files and 4,573 transport-journal rows, finding no forbidden outcome
  key; and
- confirmed that the transport retained response hashes and HTTP/rate metadata rather than raw API payloads.

The tracked manifest canonical SHA-256 is
`c62cac4d02e8d4d1216d13f7f278fccadb41ed8f0856463aac706c678eb21c84`. Its absolute local path strings are
provenance from this Mac rather than portable locators; D0 artifacts must use repository-relative paths and R2
keys. This bookkeeping limitation does not change any scientific count or seal result.

## What GREEN does and does not authorize

GREEN authorizes an outcome-blind D0 that freezes repository identities, retrospective/prospective windows,
root-job linkage, matching, exclusions, effective-cluster requirements and a power/sensitivity rule. D0 can
retain event identities, run creation times, workflow paths, actor/event classes, PR links, head SHAs, runner
labels and Boolean field presence. It must discard before persistence every job start/completion value, run/job
status or conclusion, review response, merge state, duration, registry release age and security outcome.

GREEN does not authorize an effect estimate, a policy model, a GPU run or an NMI/NCS claim. In particular:

1. `run.created_at` to earliest `job.started_at` is a queue proxy, not a direct GitHub scheduler timestamp.
2. GitHub-hosted runners draw on platform-wide capacity that is only partially observable from one repository.
3. The public announcement date may not equal an instantaneous global backend rollout.
4. The star-ranked frame is transparent but not a historical probability sample.
5. Security and version-update PRs cannot yet be separated reliably in public metadata.

## Binding next step

Freeze and push D0 before any queue value is opened. D0 must use the 72 high-support treated IDs and 447 eligible
control IDs derived here as its candidate pools; specify one primary match and deterministic fallback; retain the
63 already-cooled repositories only as a negative control; define a rollout blackout; and set minimum human-run,
repository-day and effective-cluster support. If D0 cannot meet those requirements without inspecting queue
values, stop or narrow the claim. Only a passed and committed D0 may authorize the one-shot retrospective D1.
