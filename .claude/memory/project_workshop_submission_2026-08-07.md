---
name: project_workshop_submission_2026-08-07
description: Verified STODY/Sim2Science submission rules, in-person conflict, and August submission workflow
metadata:
  type: project
---

## Final strategy override (2026-08-09)

- Submit **only the Sim2Science workshop paper**. Paper S/STODY is formally cancelled, not
  conditional: it did not have an independent evidence chain and a four-page paper could not both
  introduce an unpublished simulator and defend a separate dynamics claim.
- Paper E remains tier **E-B**, an explicitly simulator-specific stationarity/audit result. EcoMD is
  identified as a previously unpublished frozen audit object, not an established baseline or a claim
  about real-market physics.
- The five-page body contains a compact method definition; Appendix A specifies initialization,
  stochastic pair potential, global state, dissipation, price map, training objective/horizons, and
  all audited variants. It also discloses the training/inference jump mismatch and the 24-step
  training-state-reset versus 8,000-step inference-state persistence mismatch.
- The anonymous artifact is deliberately audit-only. It contains frozen trajectories, exact configs,
  gates/results, analysis, and tests, but no EcoMD core model/training source and no checkpoint
  binaries. Final ZIP SHA-256 is
  `884147a89bbfe5b5c021e08440e644cb078fcdd954a83fd2fb7c94851d301a19`; manifest SHA-256 is
  `de6f5549d2af5df0e0c49238071a1810483b6c6bdc9db93c070daef8d68157a5`.
- A later EcoMD model paper/software release is gated by stationary-fidelity repair,
  training/inference alignment, strong baselines, generalization, and a demonstrated differentiability
  benefit. Plan: `papers/proposal/ecomd_model_paper_release_plan_2026-08-09.md`.

## Superseded two-paper submission plan

The historical operational source is `papers/proposal/workshop_submission_plan_2026-08-07.md`. Its
final override records the one-paper decision above. Internal submission is 2026-08-27; the hard
deadline is 2026-08-29 23:59 AoE / 2026-08-30 23:59 Auckland.

- Paper E targets the 5-page Sim2Science Workshop Paper track. It requires the NeurIPS 2026
  `dblblindworkshop` template, `\workshoptitle{Sim2Science}`, full anonymization, the standard checklist,
  and a nominated author who reviews two other submissions. Failure to complete reciprocal reviews can
  desk-reject the paper.
- Paper S formerly conditionally targeted the 4-page STODY Short Paper track. It is now cancelled.
- Both forms require complete OpenReview author profiles, PDF, metadata, CC BY 4.0, email sharing, and
  consent to public release if accepted. Sim2Science does not allow authors to be added after reviewing
  begins and discourages parallel submission of the same paper to multiple NeurIPS workshops.

## Historical presentation conflict

STODY is in Sydney on Dec 11 or 12; Sim2Science is in Paris on Dec 12 or 13. NeurIPS workshops are
one-day in-person events. The one-hour-per-workshop remote capacity is for unforeseen emergencies and
cannot be assumed for a planned solo-author location conflict.

The one-paper decision resolves this conflict: plan only for Paris attendance if Sim2Science is
accepted.

## Remaining administrative gates

- Ask Sim2Science for reciprocal-review dates and confirm that the solo author satisfies reviewer
  eligibility; a non-author cannot be nominated merely to satisfy the requirement.
- Check OpenReview profile, Paris travel feasibility, author list, license/public-release consent, and
  artifact hosting.
- Confidential reciprocal-review material must never be provided to Codex/LLMs; NeurIPS workshop
  reviewers are prohibited from using LLMs.

## Repository correction

The stored ML4PS and GenAI-in-Finance drafts use stale `neurips_2024.sty` fallback logic. They are source
material only. Build new `workshops/sim2science/` and conditional `workshops/stody/` projects from the
official NeurIPS 2026 template, with local submission checklists, anonymization/PDF QA, metadata examples,
and private non-git receipts/profile information.

## EcoMD disclosure versus model-paper boundary (2026-08-09 audit)

- The completed Sim2Science paper is explicitly an evaluation/audit paper. It says its contribution is
  not a first-of-kind model and does not serve as a dedicated EcoMD model-release paper.
- The conditional STODY paper has no completed submission directory and never passed its independent
  survival gate; its planned contribution is model-internal driven dynamics, not a full simulator
  release.
- The superseded GenAI-in-Finance draft is the only existing draft explicitly titled and framed as
  presenting EcoMD, but it is not submission-ready and predates the exp127 stationary-fidelity audit.
- **Resolved 2026-08-09:** the final Sim2Science artifact is narrowed to frozen trajectory audit
  reproduction. It packages audit/evaluation code and configs but excludes `ecomd/models`,
  `ecomd/training`, simulator implementation files, and checkpoint binaries. Public hosting therefore
  does not constitute the full EcoMD method/software release.
- Exp127's secondary held-out scores make a positive simulator-fidelity launch premature: across seven
  E1 checkpoints, early-window band scores are 4--6/11, whereas post-gate equal-length scores are only
  1--2/11. A dedicated EcoMD model paper needs stationary-training repair, held-out validation,
  baselines, and a demonstrated benefit from differentiability.
- **Resolved 2026-08-09:** Sim2Science no longer uses EcoMD's name as a citation substitute. The body
  and Appendix A now state the exact audit-object architecture, initialization, learned/fixed
  quantities, loss, horizons, observation map, and variant equations. STODY is cancelled. This
  scientific specification is sufficient to interpret the audit, but it is intentionally not a
  software/checkpoint release or a positive simulator-fidelity paper.
