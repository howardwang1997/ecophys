# Sim2Science 2026 release candidate

Built: 2026-08-09 NZST

## Scientific decision

- Frozen tier: **E-B**, simulator-specific case study/protocol audit.
- Submission strategy: **one Sim2Science paper only**. The conditional STODY paper is cancelled; its
  unpublished-simulator dependency and independent-evidence gate were not defensible in four pages.
- Audit object: the frozen EcoMD snapshot is previously unpublished. The manuscript now defines it as
  the object under audit rather than treating it as an established model, and gives the complete
  scientific specification in Appendix A.
- Scientific execution SHA: `22a6e41628d7cca7688ecdf5513e5a5bb014e462`.
- Calibration/held-out trajectories: 160/160; all retrieved and hash-verified.
- Gate frozen at `2026-08-07T16:42:36.931108+00:00` with zero held-out trajectories.
- Earliest held-out trajectory timestamp: `2026-08-07T16:49:13+00:00`.
- Raw gate SHA-256: `8c3ac123c999dc1bffee03b7bc31083312ffc13f60294879ff7aaa693e02f074`.
- Raw learned-result SHA-256: `2c3d3c5e266b7327482867146edccf3799cd681d88ce1c334e9fd6622aae1b8e`.
- Anonymous review-result SHA-256: `0af68915b481b7fbc75f8285b9189b0e85065a19d42a65dcf737ba9033ddc8e1`.
- Anonymous robustness-result SHA-256:
  `155a663a2eae4dc28a9c6115e0a101a063cf405d95cd98d58cc7e62324bc5e7e`.

Primary E1 effect: `+6.1192`, hierarchical-bootstrap 95% interval `[+5.4287, +6.9879]`.
Seven of seven primary checkpoints were scorable; six passed held-out gate transfer. The
dependence-aware common-seed interval was `[+5.4437, +7.0558]`; all five leave-one-market-out effects
and all three frozen Hill-fraction intervals were positive. E-A is blocked by the primary gold transfer
failure, one unresolved E3 gate, one E3 transfer failure, and mixed baseline performance.

The audit also discloses two implementation mismatches rather than interpreting them as market
physics: the training drift proxy versus inference compound-Poisson jumps, and a global-state reset
every 24 training steps versus persistent state over 8,000-step inference. Repairing these mismatches
is a hard gate for a later, separate EcoMD model paper.

The ten training runs consumed 19.90 V100 GPU-hours and the 320 formal learned rollouts consumed 34.51,
for 54.40 V100 GPU-hours in total.

## PDF

- File: `output/pdf/sim2science_ecomd_2026_submission.pdf`
- SHA-256: `dec8c7f01a268d38e7530602719b897d6110023c6631d826484af9f4d5661e88`
- Size: 191,295 bytes; 11 pages total; US Letter; references begin on page 5 and the main
  scientific content ends on page 5.
- Automated submission checks: all pass.
- Fonts: 28/28 embedded.
- Visual QA: all eleven rendered pages inspected; no collision, clipping, missing glyph, or unreadable
  figure was found.

## Anonymous artifact

- File: `output/artifacts/sim2science_ecomd_2026_artifact.zip`
- ZIP SHA-256: `884147a89bbfe5b5c021e08440e644cb078fcdd954a83fd2fb7c94851d301a19`
- Manifest SHA-256: `de6f5549d2af5df0e0c49238071a1810483b6c6bdc9db93c070daef8d68157a5`
- Size: 52,856,652 bytes; manifest complete with 538 files and no missing final file.
- Scope: audit analysis from frozen synthetic trajectories. The archive contains audit code, exact
  configs, gate/result JSON, trajectories, and derived outputs, but intentionally contains zero
  checkpoint binaries and zero core simulator, model, or training-source files.
- Two independent builds produced identical ZIP and manifest hashes.
- Archive integrity test and identity scan passed.
- Packaged test suite: 63/63 passed after clean extraction. The repository release suite, including
  artifact-builder boundary tests, passed 68/68.
- Independent re-analysis from the extracted archive reproduced the primary effect and interval
  exactly (`+6.1191501988`, `[+5.4286617158,+6.9879206340]`) and matched every numeric field in the
  frozen learned and robustness result files.

## Remaining user-owned release actions

- Confirm final author list, affiliations, conflicts, and OpenReview profiles.
- Confirm reciprocal reviewer identity and ability to complete the required confidential reviews.
- Host the anonymous artifact and insert its review URL in the submission form if the venue permits.
- Confirm the OpenReview title, abstract, TL;DR, keywords, license, and public-release selections.
- Upload the PDF, download the platform copy, rerun checks, and record the forum ID, paper number,
  receipt time, and downloaded-file SHA-256 outside public git.
- Confirm Paris attendance if the paper is accepted.
