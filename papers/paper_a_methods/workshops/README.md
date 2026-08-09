# Paper A workshop status

Current decision (2026-08-09): **one workshop submission only**.

| route | status | role |
|---|---|---|
| `sim2science/` | active; E-B release candidate | simulator-specific stationarity/fidelity audit |
| STODY | cancelled; no manuscript directory | failed the independent-paper survival gate |
| `genai_finance/`, `ml4ps/` | superseded historical drafts | source material only; not submission-ready |

The active paper audits a previously unpublished EcoMD snapshot. It therefore defines that snapshot
inside the main paper and technical appendix instead of relying on the EcoMD name as prior art. The
paper’s claim remains evaluation: initialization relaxation contaminated an apparent tail-fidelity
score, and a frozen split-sample gate diagnoses that discrepancy. It does not present the transient
as market physics and does not claim that EcoMD is a validated market model.

The anonymous Sim2Science artifact is intentionally audit-only. It packages frozen synthetic
trajectories, exact configurations, estimators, analysis, results, and tests, but excludes the core
EcoMD simulator/training source and learned checkpoint binaries. A dedicated EcoMD model paper and
software release are deferred until stationary-fidelity defects are repaired and the model has a
credible positive validation story.

Binding records:

- `papers/proposal/workshop_submission_plan_2026-08-07.md` — venue and submission execution, with
  the 2026-08-09 single-paper override;
- `papers/proposal/workshop_claim_gates_and_merge_plan_2026-08-07.md` — frozen gates and the formal
  STODY cancellation;
- `papers/paper_a_methods/workshops/sim2science/RELEASE_RECORD.md` — current PDF and artifact hashes;
- `experiments/127_workshop_claim_gates/RESULTS.md` — frozen experimental result record.
