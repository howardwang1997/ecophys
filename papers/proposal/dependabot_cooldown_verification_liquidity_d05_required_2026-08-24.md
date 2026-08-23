# Verification-liquidity D0.5 required addendum

**Date:** 2026-08-24

**Status:** outcome-blind requirement before any D1 opening

## Scope

Formal D0 v3 checkpoint transport may continue unchanged. This addendum does not change its candidate IDs,
calendar windows, stored API fields, primary outcome, matching target or seal. It records issues found before any
queue, first-stage, review, merge, security or prospective value was opened.

A D0 GREEN under v3 is necessary but not sufficient for D1. Before the one-shot outcome opening, a new versioned
contract and tests must freeze every item below. If an item cannot be implemented from outcome-blind identities,
configuration and workflow metadata, stop the mechanism/causal route rather than inspect outcomes first.

## Outcome-blind feasibility audit

Source/schema inspection, without reading a checkpoint or outcome, gives the following boundary:

| Requirement | Feasibility from current v3 | Binding interpretation |
|---|---|---|
| Dynamic updater versus PR validation | Conditional | `event_type`, workflow path and PR links permit fail-closed coarse classes, but the current actor-only probe mixes them; exact run-name adequacy must be tested in a sidecar |
| New PR versus existing-PR revision | New public API fields required | Current checkpoints retain PR database IDs and head SHAs but not PR number/creation or revision history; retrospective webhook `opened`/`synchronize` semantics cannot be reconstructed exactly |
| Owner/account clustering | Owner proxy feasible; physical capacity account unavailable | Freeze stable owner IDs from the repository endpoint, but call owner an observable interference proxy, not GitHub's hidden enterprise/billing/runner-group account |
| Security versus version update | Authoritative public classification unavailable at current permissions | Dependabot job logs need repository write access and alerts need repository-specific permission; text rules are sensitivity only |
| Matched-treated label overlap | Code-only | Recompute on `matched_treated`; label equality remains descriptive support, not proof of one physical queue |
| Cohort × period workflow attrition | Derivable | Provisional rows already contain cohort/period; replace the pooled pre-probe rate with D1-cell accounting |
| Few-day support | Derivable after owner sidecar | Dates and matched sets exist, but finite-cluster inference is not implemented or frozen |

The sidecar must bind the v3 config, repository identities, matching and selected-sample hashes. It must never
rewrite a v3 checkpoint. Fields unavailable from those checkpoints require a separately preregistered API call and
a semantic allowlist; the current exact-key blacklist is not sufficient for new security-related schemas.

## Required pre-D1 changes

### 1. Decompose the policy first stage

Do not model cooldown as a uniform 72-hour translation. Identify, separately where the public schema permits:

- scheduled dynamic Dependabot updater jobs;
- newly opened version-update pull requests;
- commits or updates to existing version-update pull requests;
- root validation runs caused by those version-update events; and
- predeclared count and dispersion summaries of proposal and validation demand.

Freeze the exact first-stage estimand, mapping rules, denominator, missingness treatment and a practical-
equivalence margin before opening any post-policy value. Security updates must remain excluded or separately
blinded because the default cooldown does not apply to them. A version/security classifier must be validated on
outcome-blind metadata with a frozen error ceiling.

For run-class adequacy, no required cohort × period cell may have more than 5% ambiguous Dependabot runs or more
than a 5 percentage-point pre/post ambiguity change. A job-demand claim additionally requires at least 90% jobs-
API recovery and zero conflicting job identities. These are minimum floors for the later machine contract, not
statistics to be evaluated during this audit.

If the new-versus-revision distinction is retained, freeze an observable revision proxy rather than claim exact
historical webhook semantics. PR link/identity recovery must be at least 95% per required cell and revision
coverage at least 90%; otherwise close the coalescence estimand.

### 2. Make the interference unit explicit

Recover stable owner/account identifiers and report the number and concentration of effective owner clusters.
Freeze owner-clustered inference and a one-repository-per-owner sensitivity. Repository-level matching alone is
insufficient when organization/account concurrency quotas create cross-repository spillovers.

Owner recovery must be at least 99%. For treated owners require Kish effective support
\(G_{\mathrm{eff}}=1/\sum_g s_g^2\ge30\), no owner above 10% of matched treated repositories and at least 30
treated repositories after selecting one repository per owner. Any matched control sharing an owner with a
treated repository must receive an explicit interference exposure; if more than 10% do so and no defensible
mapping is available, stop causal wording.

The estimand must be named the **repository/account-local relative ITT**. Platform-wide total spillover is out of
scope unless later work obtains platform load/capacity telemetry, a defensible exposure mapping or an external
unexposed platform.

### 3. Repair support and attrition gates

- Compute shared-runner-pool support on `matched_treated`, not all frozen treated repositories.
- Freeze a minimum effective-owner count and a maximum owner-concentration threshold.
- Report workflow-structure recovery by cohort × period and gate differential attrition, not only the pooled
  recovery rate.
- Separate updater-workflow probes from pull-request validation probes; actor identity alone is insufficient.

This is a new versioned gate, not a silent reinterpretation of D0 v3.

Call the first item **matched-treated shared-label support**, not observed physical pool membership. Require at
least \(\max(30,\lceil0.5N_{\mathrm{matched,treated}}\rceil)\) supported treated repositories. For every required
cohort × period cell, workflow recovery must be at least 90%; treated-control attrition DiD, missing-only DiD and
equal-repository-weighted attrition DiD must each be no larger than 5 percentage points. The accounting identity
`provisional = missing + intentional_wait_excluded + eligible` must hold exactly.

### 4. Freeze finite-cluster inference

Because the primary design has only 28 pre and 28 post calendar days, freeze few-day-cluster and owner-aware
sensitivity procedures before outcome opening. They remain labelled sensitivities and cannot replace a failed
primary analysis.

Require at least 24 of 28 overlapping treated/control days in each primary period, count-based Kish day support
of at least 20 and no single day above 10% of its cell. Freeze restricted-null wild-cluster bootstrap-t by UTC
day, CR2/Satterthwaite and leave-one-day-out procedures, including seeds and failure rules.

## Security/version bifurcation

An authoritative version-specific mechanism claim requires at least 90% classifier coverage in every required
cell and one-sided 95% lower confidence bounds of at least 0.90 for both sensitivity and specificity against an
authorized ground-truth sample. Permission failure is missing ground truth, not evidence of no security update.

If this cannot be achieved, close the version-specific and top-venue mechanism claims before opening queue
outcomes. A software-engineering reduced form may continue only with all-Dependabot validation demand, explicit
security-update contamination and frozen worst-case bounds. It must not be called a version-specific first stage.

## Stop rules

Close the cooldown mechanism/causal route before D1 if any of the following occurs:

- updater activity cannot be separated from PR-validation demand at the frozen ambiguity/recovery floors;
- the version-update-specific first stage is practically equivalent to zero, or--under the reduced-form branch--
  all-Dependabot validation demand is practically equivalent to zero under its frozen contamination bounds;
- matched-treated shared-pool support or effective-owner support falls below its newly frozen threshold;
- owner concentration, cohort × period workflow attrition, field recovery or seal integrity fails its gate;
- the pretrend, placebo or already-cooled negative control fails; or
- a retrospective signal does not reproduce in direction and practical magnitude in the untouched prospective
  interval after 2026-10-17 UTC.

## Venue boundary

Passing D0.5 and D1 could support a carefully scoped GitHub/software-engineering field study. Dependabot is not a
generative coding agent. Reopening NMI requires a separately frozen genuine coding-agent intervention plus a
prospectively validated policy prediction. Reopening NCS additionally requires a new admission/scheduling method
with a nontrivial guarantee and transfer to a second independent computational domain.
