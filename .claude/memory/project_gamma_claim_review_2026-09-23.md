---
name: gamma-claim-review-2026-09-23
description: "Private Gamma claim review and ICLR plan; PI resolved submission identity, three-worker execution gaps checked"
type: project
---

# Gamma claim review (private/internal)

PI update 2026-09-23: Gamma targets **ICLR**, with abstract submitted and full paper pending according to the PI. This replaces the earlier ICML target as current intent; frozen experiment documents were not amended. The PI subsequently stated "投稿身份已经确定". Submission identity is resolved for planning; do not reopen the lookup or treat it as a blocker. The exact server-side title and abstract were not independently retrieved in this session; do not substitute the Paper D entry for Gamma.

Lookup evidence: Chrome's targeted OpenReview history records `https://openreview.net/forum?id=Ww3mQmX0nG` with Paper D's title, **When Are Exact Conservation Layers Plug-and-Play? Identifying Training--Inference Path Dependence in Neural PDE Surrogates**. The local submission abstract is in `papers/paper_d_constraints/OPENREVIEW_SUBMISSION_STEPS_20260905.md`, but its byte identity to the current server-side abstract is unverified. Original project chat on 2026-09-18 explicitly said Paper D was submitted and the next target was ICML. No Gamma entry was located in the inspected records. Browser history snapshots were deleted after the targeted read; cookies and credentials were not read.

ICLR 2027 full-paper deadline, checked against the official Call for Papers and Author Guidelines: **2026-09-25 23:59 AoE**, equivalent to **2026-09-26 23:59 NZST**. The October campaign ceiling cannot be used as the submission deadline.

Current Gamma manuscript is `papers/paper_e_matching_fiber/`, still a venue-neutral skeleton with empirical placeholders. The central candidate claim concerns which hidden order-book differences clearing records fail to identify and which specified deployment interventions expose them. Generic non-identifiability, conditional-variance bounds and train/infer crossings are not novelty claims.

The 2026-09-23 read-only claim review found that the current theorem package needs correction and independent rechecking before publication. Pre-existing `proven` labels are not sufficient review evidence. Detailed mathematical counterexamples and correction scope are private at `logs/private/gamma_claim_review_20260923.md`; do not export this audit as paper motivation, results, novelty or limitations. No frozen claim, experiment setting or manuscript was edited. Empirical J, estimator stability and architecture transfer remain unconfirmed; T4 remains conjectural.

Official sources: https://www.iclr.cc/Conferences/2027/CallForPapers and https://iclr.cc/Conferences/2027/AuthorGuidelines.

Submission plan: `logs/private/gamma_iclr_submission_plan_20260923.md`. It schedules proof/observation-contract review, B1 completion, S3/S1a/S2 controls, 30-seed A10, complete-records disposition and the one-shot analyzer before manuscript acceptance. The A10 runtime was subsequently deployed and tested; the Gamma analyzer remains a development dependency. Original dual-lineage D1 scope is a never-cut requirement; B3's halt needs explicit handling before B1 can be treated as a complete analysis scope. Stage 2 remains mechanical-gate dependent. The plan itself authorizes no experiment, protocol amendment or external submission; the PI subsequently instructed ordered execution and ratified the B1 record-version decision.

Three-worker readiness checked 2026-09-23 02:17-02:22 NZST: no Gamma training/evaluation driver or matching cron/systemd timer was found. V100s have the production training driver; bts also has the manifest merger. The 3080 worker has the CPU evaluation driver and scale materializer. Deployed driver hashes match the local files, despite older remote checkout HEADs. GPUs are occupied by other projects; capacity is shared, not reserved. The private plan now assigns B1 artifact handoff and A10 training to v100ts, B1 handoff and proposed theory/control checks to v100bts, and full B1 evaluation followed by accepted audit evaluation/replay/analysis to the 3080 CPU channel. Proposed allocations are not launched jobs. Checkpoint transfer, complete manifest acceptance, PAM runtime, theory/control production receipts and analyzer implementation remain before that sequence can finish.

Execution supersedes the 02:22 snapshot: at 03:42, all 120 B1 checkpoints and the R2 handoff are accepted; approved producer `29bee8139` is running four independent CPU seed jobs with 12/30 seed manifests complete. A10 producer `a93bade05` is deployed on v100ts and 3080 and passes 23 checks on each. The A10 training and evaluation waiters are running, gated by complete, hash-bound predecessor archives; production A10 has not started. Theory/control checks, B3 scope disposition and the formal analyzer remain outstanding. See [[project-d0-campaign-execution-2026-09-21]] and the private plan for paths and dependency details.
