# Verification-liquidity active audit — 2026-08-24

## Decision

**Keep the frozen D0 acquisition active only as a sealed value-of-information exercise, and do not let a D0 GREEN
automatically authorize D1.** The defensible field estimand is narrow: whether GitHub's platform-wide default
Dependabot cooldown changed the validation service received by unrelated human-triggered work, relative to
controls, within repository/account interference clusters that can be observed. It does not establish a general
AI-verification law or the platform-wide total effect, and the cooldown cannot be assumed to reduce or smooth
validation demand.

This audit is outcome-blind. It did not open a workflow/job start value, conclusion, review, merge, release-age or
security outcome, and it does not amend the frozen D0 candidate IDs, windows, estimator or numerical gates.

## Gate 1: the pure-delay null

Let the uncensored agent-proposal process be a stationary marked point process

\[
\mathcal A=\{(T_i,M_i)\}_{i\in\mathbb Z}.
\]

Suppose a policy only delays every proposal by the same constant \(d\), without deleting, combining, reordering or
changing its validation-service mark:

\[
\mathcal A_d=\{(T_i+d,M_i)\}_{i\in\mathbb Z}.
\]

Then \(\mathcal A_d\) has the same stationary law as \(\mathcal A\). Its long-run intensity, count distribution in
a fixed-length window, inter-arrival dependence, Fano factor and service-work distribution are unchanged. A
time-homogeneous single-stream queue driven entirely by \(\mathcal A_d\) therefore has the same steady-state law
as one driven by \(\mathcal A\), apart from initialization or observation-window boundary effects. The same
conclusion holds for a superposed queue only if the other arrival streams and capacity are jointly stationary in
the required sense--for example, independent stationary background inputs--or are shifted with \(\mathcal A\).

The proof is just translation invariance: for every finite collection of Borel windows
\(B_1,\ldots,B_k\), stationarity makes the joint law of the marked counts in
\((B_1-d),\ldots,(B_k-d)\) equal to that in \((B_1,\ldots,B_k)\). A time-homogeneous queue is a measurable
shift-equivariant functional of its complete arrival, service and capacity processes.

This is not an unconditional null for a shared GitHub queue. Shifting only bot work can change its phase relative
to human work, correlated background traffic, capacity schedules and account-level concurrency constraints. A
72-hour delay also moves an arrival three weekdays forward. Weekly nonstationarity or dependence between streams
is enough to invalidate the simple invariance argument even when bot counts and service marks are unchanged.

This proposition is a null model, not a claim that GitHub implements a one-to-one translation. GitHub's current
documentation says that scheduled update checks continue, releases inside the cooldown are skipped, and when
eligibility resumes Dependabot selects the latest eligible version according to its update strategy. A version-
update job can open a new pull request or update an existing one. Multiple upstream releases can therefore be
collapsed into one candidate, while a surviving pull request can receive new commits and retrigger validation.
This is selection, batching and coalescence--not the map \(T_i\mapsto T_i+72\mathrm h\).

Consequently, a verification-liquidity mechanism claim requires a measured first stage in at least one of:

- scheduled dynamic Dependabot updater-job activity;
- newly opened version-update pull requests;
- updates or commits to existing version-update pull requests;
- the root validation jobs triggered by those pull-request events; and
- proposal and validation clustering or another predeclared dispersion statistic.

A queue-delay contrast without such a first stage is not evidence that cooldown relieved verification demand. A
timing first stage with unchanged mean demand can still matter under a nonlinear finite-capacity queue, but that
claim must be stated as redistribution of burstiness rather than workload reduction.

## Gate 2: identify the estimand that the design can support

The frozen matched event study can at best identify a **repository/account-local relative ITT**: the post-policy
change in a human run's initial validation delay in treated repositories relative to matched repositories without
Dependabot. It does not identify the platform-wide total effect of the default on all GitHub-hosted-runner users.

The distinction follows from interference. A global reduction in hosted-runner load could benefit treated and
control repositories simultaneously and be absorbed by calendar-day effects. Conversely, repository,
organization or account concurrency limits can produce a local differential even when global hosted capacity is
unchanged. GitHub documents account-level concurrent-job limits and notes that Dependabot can increase concurrent
jobs for an account. The natural observable interference cluster is therefore at least the owner/account, not
only the repository. Runner-label overlap is neither necessary nor sufficient for physical co-queueing: distinct
labels can consume a common account quota, while a common `ubuntu-latest` label does not reveal the hidden
scheduler or prove competition for one finite pool.

| Claim | What the frozen design can say | What it cannot say |
|---|---|---|
| Repository/account-local relative spillover | Matched differential change, conditional on owner-aware support, pre-trends, first stage and negative control | A randomized causal effect without parallel-trend and interference assumptions |
| Shared hosted-runner spillover | A pattern consistent with shared capacity | The platform-wide total effect, because controls may also be exposed |
| Scheduler mechanism | Label overlap and heterogeneity evidence | Physical co-queueing or GitHub's hidden capacity allocation |
| Human validation service | Run creation to earliest job start as a reproducible proxy | Pure runner waiting, because hidden orchestration may precede job start |

The main residual identification risks remain:

1. The primary controls have no Dependabot configuration and can differ structurally from treated repositories;
   pre-period balance is necessary but not sufficient for parallel counterfactual trends.
2. The public announcement time may not be the exact backend rollout time.
3. Hosted-runner interference can attenuate the differential comparison, while repository/organization/account
   quotas can create a different local estimand. Controls in other accounts do not identify same-account quota
   spillovers.
4. Twenty-eight pre and twenty-eight post calendar days provide few day clusters for conventional asymptotic
   two-way clustered inference.
5. Reusable workflows, organization-level concurrency and hidden orchestration are not completely observable
   from repository workflow YAML and public job fields.

None of these issues justifies changing the frozen primary analysis after outcomes are opened. They instead
require an outcome-blind D0.5 addendum before D1. Owner-level and few-day-cluster sensitivity analyses must be
frozen there and must not replace a failed primary result.

Official mechanism references:

- GitHub's [cooldown option reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference#cooldown)
  defines the eligible-version rules rather than a constant time shift.
- GitHub's [Dependabot job-log documentation](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-job-logs)
  distinguishes update jobs that opened or updated pull requests.
- GitHub's [Dependabot on Actions documentation](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-on-actions)
  states that Dependabot can increase concurrent jobs for an account.
- GitHub's [Actions limits](https://docs.github.com/en/actions/reference/limits) document plan-level total
  concurrent-job limits.
- Hudgens and Halloran, [*Toward Causal Inference With Interference*](https://pmc.ncbi.nlm.nih.gov/articles/PMC2600548/),
  separate direct, indirect, total and overall causal effects under interference. Xu,
  [*Difference-in-differences with interference*](https://doi.org/10.1016/j.jeconom.2026.106304), gives the
  corresponding warning for DiD designs.

## Gate 3: outcome-blind implementation audit

Two current implementation details can produce a nominal GREEN without supporting the intended mechanism:

1. `ecomd/data/github_verification_liquidity_d0.py:973` computes the shared-pool count over all frozen treated
   repositories rather than the final `matched_treated` analysis set. Treated repositories excluded by matching
   can therefore satisfy the mechanism-support gate.
2. `ecomd/data/github_verification_liquidity_d0.py:396` samples the deterministic Dependabot probe by actor and
   pre-period only. It does not separate dynamic updater jobs from pull-request-triggered validation jobs, whose
   responses to cooldown have different meanings.

The workflow-structure recovery check is also global rather than cohort-by-period. Differential missing or
unparseable workflow YAML could therefore create post-treatment selection without tripping the existing gate.
These findings do not invalidate checkpoint transport or reveal outcomes, but they block D1 until a versioned
D0.5 contract freezes corrected support and attrition gates.

A second source/schema audit found that four D0.5 requirements are derivable from the current identity records or
an independent evaluator, while exact PR-open-versus-revision history and stable owner IDs require new public API
sidecars. The hardest boundary is version-versus-security ground truth: public cross-repository workflow runs do
not distinguish them, Dependabot job logs require write access and alert metadata require repository-specific
permission. Accordingly, failure of authoritative classification closes the version-specific mechanism and
top-venue branch; only an explicitly contaminated all-Dependabot reduced form with worst-case bounds may remain.
The precise feasibility matrix and outcome-blind floors are frozen as requirements in the D0.5 artifact.

## Gate 4: novelty after the 2026 literature update

The broad narrative is now occupied. Prior work already measures Dependabot adoption, lag and notification
fatigue; bot-versus-human review latency; and dependency-induced CI waste. Recent work also directly formulates
scarce downstream human verification as a queueing bottleneck for AI-assisted workflows. Large 2026 studies of
real agent-authored pull requests cover CI results, review dynamics and human intervention.

The remaining empirical novelty is narrower and more defensible: a pre-registered evaluation of a deployed
agent-side safety policy, with an unrelated-human validation outcome, a mechanical first stage, an already-cooled
negative control and a prospective replication. The audit found no primary study that directly estimates this
July 2026 policy contrast or its human-job spillover. Absence from the searched corpus is not proof of novelty.

Relevant primary and official sources:

- GitHub's [July 2026 announcement](https://github.blog/changelog/2026-07-14-dependabot-version-updates-introduce-default-package-cooldown/)
  defines the three-day default and excludes security updates.
- GitHub's [configuration documentation](https://docs.github.com/en/code-security/tutorials/secure-your-dependencies/optimizing-pr-creation-version-updates)
  states both that default check times are randomized and that a version is not considered until cooldown ends.
- GitHub's [mechanism rationale](https://github.blog/security/supply-chain-security/the-case-for-a-cooldown-why-dependabot-now-waits-before-issuing-version-updates/)
  is supply-chain safety, not CI-load control.
- He et al., [*Automating Dependency Updates in Practice*](https://arxiv.org/abs/2206.07230), study Dependabot lag,
  receptivity, configuration and notification fatigue.
- Wyrich et al., [*Bots Don't Mind Waiting, Do They?*](https://arxiv.org/abs/2103.03591), compare bot and human PR
  interaction and merge latency.
- Weeraddana et al., [*Dependency-Induced Waste in Continuous Integration*](https://doi.org/10.1145/3660823),
  quantify unused-dependency CI waste and propose build skipping.
- Bartolucci and Vivo, [*Queue & AI: When Faster Tasks Slow Down the Workflow*](https://arxiv.org/abs/2605.27202),
  already provide a queueing theory of scarce review, rework and congestion in AI-assisted workflows.
- Pan et al., [*AIDev*](https://arxiv.org/abs/2602.09185), assemble 932,791 agent-authored pull requests from
  116,211 repositories, sharply raising the empirical bar for generic agent-PR claims.
- Ehsani et al., [*Where Do AI Coding Agents Fail?*](https://arxiv.org/abs/2601.15195), study CI and review outcomes
  in 33,000 agent-authored pull requests.
- Recent work already studies [concurrent agent pull requests](https://arxiv.org/abs/2607.04697) and
  [human review themes](https://arxiv.org/abs/2601.19287) at scale.
- Google's [*Taming Google-Scale Continuous Testing*](https://research.google/pubs/taming-google-scale-continuous-testing/)
  establishes workload control and delayed validation feedback as mature CI problems.

## Binding route decisions

1. Continue the D0 transport exactly from immutable checkpoints and do not open sealed outcomes during transport.
2. D0 GREEN is not authorization to open D1 outcomes. Before D1, freeze and implement the separate D0.5 contract
   in `dependabot_cooldown_verification_liquidity_d05_required_2026-08-24.md`.
3. Stop before D1 if any frozen identity, matching, run-support, workflow-structure, field-presence, corrected
   matched-treated shared-pool, owner-support, attrition, seal or deterministic-hash gate fails.
4. Require version-update-specific proposal/update/root-job first stages with a frozen practical-equivalence
   margin. If authoritative version/security classification is unavailable, close that claim and permit only a
   labelled all-Dependabot reduced form with contamination bounds. A first stage equivalent to zero closes the
   cooldown mechanism even if a queue contrast is significant.
5. Report the repository/account-local relative ITT separately from platform-wide total spillover. Permanently
   close the total-effect claim absent platform load/capacity telemetry, an explicit exposure mapping or an
   unexposed external platform.
6. A successful retrospective result still requires the untouched prospective interval through 2026-10-16.
7. Do not use Dependabot alone to claim an AI-agent law. An NMI continuation needs a separately frozen transfer to
   genuine coding-agent proposals and a policy prediction that survives prospective testing.
8. An NCS continuation additionally needs a new admission/scheduling result with a nontrivial guarantee and a
   second independent computational domain. Classical queueing or replay optimization alone is insufficient.

## Current probability assessment

These are conditional research-planning probabilities, not statistical estimates:

| Milestone from the current state | Probability |
|---|---:|
| D0 passes all frozen feasibility gates | 35–55% |
| Credible, non-null account-local cooldown effect after all causal/mechanism gates | 3–10% |
| Strong software-engineering publication | 5–12% |
| NMI-quality package in the current single-system form | 0.3–1.5% |
| NCS-quality package in the current single-system form | <0.5% |

The route remains worth completing because it is already frozen, inexpensive, unusually falsifiable and capable
of producing a clean null. It should not displace search for a stronger top-venue problem.
