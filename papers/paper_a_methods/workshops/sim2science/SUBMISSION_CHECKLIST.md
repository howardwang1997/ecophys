# Sim2Science submission checklist

Target: 5-page Workshop Paper, deadline 2026-08-29 23:59 AoE. Internal upload deadline: 2026-08-27.

## Scientific freeze

- [x] Claim is simulator discrepancy, not market physics.
- [x] Gate, windows, seeds, thresholds, controls, and decision tiers were frozen before held-out use.
- [x] Analytic positive, null, weak-sensitivity, and failed-baseline outcomes are reported.
- [ ] Ten learned checkpoints and 320 trajectories are complete and hash-verified.
- [ ] Calibration gate file was serialized and hashed before any held-out trajectory existed.
- [ ] `LEARNED_RESULTS.json`, result tier, manuscript numbers, and learned figure agree exactly.
- [ ] `LEARNED_ROBUSTNESS.json` is frozen and any primary/common-seed or leave-one-market-out
  disagreement is disclosed.
- [ ] Null, missing gate, and failed transfer outcomes remain in the denominator and prose.
- [ ] STODY rescue decision is recorded only after Paper E freezes.

## Manuscript

- [x] Official 2026 `dblblindworkshop` template and `\workshoptitle{Sim2Science}` are used.
- [x] References are verified against publisher or proceedings records.
- [x] NeurIPS checklist is after references and before the appendix.
- [ ] No `PENDING`, `TODO`, `TBD`, placeholder box, or provisional claim remains.
- [ ] Main scientific content ends by page 5; references and appendix are excluded from that count.
- [ ] Every quantitative sentence maps to a frozen JSON field or manifest hash.
- [ ] Final title, abstract, TL;DR, and keywords match OpenReview fields.

## Artifact and anonymity

- [x] Anonymous artifact builder refuses incomplete final results unless explicitly in test mode.
- [x] Artifact identity scan, deterministic ZIP test, and unpacked core tests pass.
- [ ] Final artifact includes synthetic rollout shards, checkpoints, gate/result JSON, and manifest.
- [ ] Artifact ZIP and manifest SHA-256 are inserted into the release record.
- [ ] PDF and artifact contain no author name, affiliation, email, personal URL, username, host, IP,
  W&B entity, R2 URI, acknowledgments, grant, or identifying Git history.
- [ ] `check_submission.py`, `pdfinfo`, `pdffonts`, and full visual page inspection pass.
- [ ] Final PDF is under 50 MB and copied to `output/pdf/` with its SHA-256 recorded.

## User-owned OpenReview actions

- [ ] Author profile, verified email, affiliation, conflict domains, and final author list are correct.
- [ ] User can serve as nominated reciprocal reviewer and complete two confidential reviews without
  using any LLM or sharing review material.
- [ ] Track is set to 5-page Workshop Paper.
- [ ] License, author-email sharing, and accepted-paper public-release confirmations are reviewed.
- [ ] Final PDF is uploaded, downloaded again, and rechecked; forum ID, paper number, receipt time,
  and downloaded-PDF hash are saved outside public git.
- [ ] Paris attendance plan is confirmed if accepted.
