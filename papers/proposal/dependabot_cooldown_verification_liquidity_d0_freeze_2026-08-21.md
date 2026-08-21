# Dependabot cooldown verification-liquidity D0 freeze — 2026-08-21

## Decision

Formal D-1 is GREEN, so the next authorized step is an **outcome-blind D0 identity, workflow-structure and matching
audit**. D0 does not estimate whether queueing improved. It freezes exactly which repositories and workflow runs
would enter a later one-shot D1, while queue start values, conclusions, reviews, merges, release ages and security
outcomes remain sealed.

The authoritative machine-readable contract is
`configs/agent_markets/github_dependabot_cooldown_d0_v3.yaml`. V2 had superseded v1 before any D0 API acquisition:
v1 froze the right candidate IDs, windows, estimand and numerical gates but did not fully define which prequalified
treated repositories survive if a complete 1:3 match is infeasible. V2 preserved every scientific field and
threshold while fixing prequalification, the deterministic maximal-prefix rule and schema denominators. The first
deterministic 11-repository smoke then completed its identity checkpoints but deliberately produced no final
artifact: the generic outcome-seal guard rejected the external GitHub Status field name `started_at`, even though
that value describes a public incident rather than a sampled workflow/job outcome. V3 changes only the external
incident ledger names to `reported_start_utc` and `reported_resolution_utc`. Candidate IDs, time windows, estimand,
matching, forbidden sample outcomes, thresholds and gates are unchanged.
The candidate ledger is
`data/manifests/github_dependabot_cooldown_d0_candidate_ids_v1.json`, with file SHA-256
`b5dc728cd79d42a6be9b5107b3fa6e1f02247680c0b41bc8485687b85680cd82` and canonical payload SHA-256
`b6c21ed897594471051f8f21cdaef009e6f98416f0980324fdc1b791d65c5c62`.

## Frozen cohorts

The ledger was generated mechanically from the immutable D-1 allowed-record artifact; no new API response or
outcome was used.

| Cohort | Frozen candidates | Definition |
|---|---:|---|
| default-treated | 72 | cutoff config omitted cooldown, Actions present, at least 20 pre-event bot PRs and positive human-PR support |
| primary control pool | 447 | no cutoff Dependabot config, Actions present, no pre-event bot PR and positive human-PR support |
| negative control | 33 | explicit positive cooldown before the intervention, Actions present and at least 20 pre-event bot PRs |
| explicit zero-day opt-out | 0 | unavailable and forbidden as an invented comparison |

The primary controls remain the pre-frozen no-Dependabot repositories because the original plan fixed that
comparison before D-1. Already-cooled repositories supply a more comparable falsification cohort: they had
Dependabot load but should not change when GitHub alters only the omitted default. Both comparisons must be
reported; neither may be chosen after looking at queue outcomes.

## Frozen time design

The retrospective primary comparison uses equal 28-day windows:

- pre: `2026-06-16T00:00:00Z` through `2026-07-13T23:59:59Z`;
- rollout blackout: all of 2026-07-14 through 2026-07-16 UTC;
- post: `2026-07-17T00:00:00Z` through `2026-08-13T23:59:59Z`.

The longer outcome-blind identity acquisition begins 2026-05-19 so D1 can show pre-trends and a 2026-06-16
placebo. Data from 2026-08-14 onward cannot be added to the retrospective estimate. The independent temporal
holdout is 2026-08-22 through 2026-10-16 and cannot be opened before 2026-10-17 UTC.

The three-day blackout is conservative: GitHub says the new default waits until a release has been present for at
least three days, applies only to version updates, and leaves security updates immediate. The official post does
not supply an hour-level rollout log, so D0 does not pretend that the backend switched atomically at midnight.

## Human work and the queue proxy

The primary human sample is deliberately narrow: first-attempt workflow runs with `actor.type == User` and
`event == push`. Pull-request, pull-request-target and manual-dispatch runs are secondary. This avoids making the
main estimate depend on GitHub's separate 2026-07-28 change that can hold potentially malicious fork workflows
for approval.

For a later eligible run, D1 would define

\[
Q=\min_j t^{\mathrm{start}}_j-t^{\mathrm{created}}_{\mathrm{run}}.
\]

The earliest observed job is used because a job downstream of `needs:` mixes runner waiting with intentional DAG
delay. This remains a proxy: GitHub documents the run creation and job start fields but does not document their
difference as a pure scheduler timestamp. D0 therefore parses the workflow definition at the run's head SHA and
flags workflow concurrency, root-job concurrency and root-job environments. Any flagged run is excluded from the
primary D1 population before its timing value is opened.

Runs are selected within repository × UTC date × event-class × period strata by the smallest SHA-256 of
`repository_id:run_id`, capped at two primary and one secondary run per repository-day. This deterministic,
outcome-independent cap prevents a few very active projects from exhausting the public API or dominating the
run-level estimate.

## Matching and identification

D0 uses only pre-period covariates. It globally matches three no-Dependabot controls without replacement to each
treated repository using robust-scaled Mahalanobis distance, exact runner-pool class and a pre-human-run activity
caliper. The covariates are frozen in the YAML contract and include pre human-run volume and event mix, the capped
human-PR lower bound, workflow count, stars and repository age. Tie-breaking is a hash of repository IDs.

Prequalification requires at least five pre-period primary human run identities, finite covariates, a known
pre-period human runner-pool class and a successful human job-schema probe. It never uses a post-period count or
field-presence flag. Repositories are ordered by the number of feasible controls and then a repository-ID hash;
the globally optimal assignment is solved for the largest deterministic prefix with a complete 1:3 match. If no
prefix of at least 60 treated repositories is feasible, D0 fails.

GREEN requires at least 60 matched treated and 180 distinct controls, maximum absolute standardized mean
difference at most 0.20 and mean absolute standardized mean difference at most 0.10. Matching never uses a post
count, a field-presence pattern from the post period or a queue value. The matched identities remain fixed even if
some repositories have sparse post observations.

The later D1 reduced form is a matched difference-in-differences/event study on `log1p(Q seconds)`, with repository,
UTC calendar-day, hour-of-week and workflow-path effects and two-way repository/day clustered uncertainty. Raw
seconds, medians and p95s must also be shown without winsorization. A mechanism claim additionally requires a
Dependabot-arrival first stage, runner-pool overlap and no analogous change in the already-cooled negative control.
A failed pre-trend, placebo, first stage or negative control is reported as a failed causal/mechanism claim rather
than repaired by another window or estimator.

## Runner-pool mechanism

D0 samples three pre-period bot and human runs per repository and retains only job IDs, names, label sets and
Boolean field presence. Exact nonempty canonical label-set overlap defines the pre-registered shared-pool subset.
At least 30 treated repositories must exhibit bot/human overlap for the full mechanism route. If the identity,
matching and field gates pass but overlap does not, the result is AMBER: stop and separately freeze a narrower
reduced-form claim before D1. It is not acceptable to drop the mechanism test silently.

This distinction matters. A platform-wide hosted-runner effect can benefit treated and control repositories alike,
while repository/organization concurrency can generate a local differential effect. Runner labels do not expose
GitHub's internal capacity allocation, so overlap is supporting evidence, not proof of a scheduler channel.

## Incident handling

The primary model keeps all hours and absorbs global load with UTC-day and hour-of-week effects. Before D1, D0
also freezes an official GitHub Status incident ledger. A pre-specified sensitivity excludes each Actions-related
incident from reported start through resolution, padded by one hour. This prevents choosing outage exclusions
after seeing large queue values. The known 2026-08-17 major GitHub incident is outside the retrospective post
window by construction.

## D0 gates

D0 is GREEN only if all frozen transport, identity, matching, run support, negative-control support, workflow
structure, field-presence, shared-pool, seal and deterministic-hash gates pass. Key minimums are 60/180 matched
treated/controls; 750/1,500 selected primary runs in each period; 50/120 matched treated/controls with at least five
primary runs in both periods; 20 supported already-cooled negative controls; and 30 treated repositories with
pre-period bot/human runner-label overlap.

An AMBER is permitted only for the single predeclared shared-pool shortage while every reduced-form gate passes.
Every other failure is RED. Neither decision permits widening dates, lowering D-1's 20-bot-PR threshold, adding an
opt-out cohort, choosing controls after outcomes, replacing queue time with merge latency, or using GPU/model
training as a rescue.

## Data and compute

D0 uses only public GitHub REST metadata, historical public workflow YAML and official GitHub Status history. Raw
responses are sanitized in memory; only approved identity/schema records and response hashes may persist. The
first smoke's largest repository, RSSHub, alone has 21,024 workflow-run identities in the fixed acquisition window;
this is transport-scale evidence only and is not an outcome. Formal acquisition must therefore preserve per-repo
checkpoints and may span several authenticated API-rate windows; it may not drop high-load repositories after
observing their size. Expected storage is below 50 GB and work below 100 CPU core-hours. The Mac or CPUs on the two
V100 hosts may perform collection, but the run is API-bound. V100/RTX 2060 GPU execution, H20, paid data and EcoMD
are forbidden.

## Implementation verification before formal D0

The v3 resume completed the original 11-repository engineering smoke from its immutable identity checkpoints. It
covered 46,862 run identities, 28 schema/workflow probes, 22 official Actions-related incidents and 692 journaled
responses in total. The sanitizer and outcome seal passed, but the deterministic smoke subset contained two
prequalified treated repositories and zero prequalified controls. That is neither a D0 estimate nor a formal gate:
the smoke deliberately contains only 3/6/2 treated/control/negative-control candidates and cannot stand in for the
frozen 72/447/33 cohorts.

The resume exposed two implementation defects before formal acquisition. First, an empty match serialized a
Python `Infinity`; all output writers now reject non-finite JSON and report unavailable balance metrics as `null`.
The old `/tmp` smoke result is therefore an engineering trace only and cannot be cited as a scientific artifact.
Second, schema probes alone did not implement the frozen rule that primary D1 runs with workflow concurrency,
root-job concurrency or root-job environments must be removed before timing outcomes open. The collector now
deduplicates every provisionally selected primary run by repository, head SHA and workflow path, checkpoints its
historical workflow structure, excludes missing or intentionally waiting structures, and only then writes exact D1
IDs. This stage is not run when matching or balance has already failed.

Formal execution also applies a logically necessary outcome-blind stop before schema probes: it counts repositories
with at least five pre-period primary run identities and treats every inaccessible/truncated repository as if it
could still qualify. Only if even this conservative upper bound clears the frozen 60 treated/250 control minima
may schema probes proceed. This changes no candidate, threshold, estimand or gate; it prevents spending later API
windows after a failure has already been mathematically established. The complete verification-liquidity suite is
34/34 passing, with Ruff, strict mypy and bytecode compilation also passing.

## Venue boundary

A passed D0 still is not a result. A credible retrospective effect plus the untouched prospective interval could
support a strong software/agent-systems submission. NMI additionally needs a transferable verification-externality
mechanism and policy value on coding-agent work. NCS additionally needs a genuinely new admission/scheduling method
with a nontrivial guarantee and validation in a second independent computational domain.

## Verified official references

- GitHub, [default package cooldown announcement](https://github.blog/changelog/2026-07-14-dependabot-version-updates-introduce-default-package-cooldown/).
- GitHub, [why the three-day default applies only to version updates](https://github.blog/security/supply-chain-security/the-case-for-a-cooldown-why-dependabot-now-waits-before-issuing-version-updates/).
- GitHub, [workflow-run REST endpoint and fields](https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28).
- GitHub, [workflow-job REST endpoint and fields](https://docs.github.com/en/rest/actions/workflow-jobs?apiVersion=2022-11-28).
- GitHub Status, [official incident history](https://www.githubstatus.com/history).
