# Sim2Science 2026 release candidate

Built: 2026-08-08 NZST

## Scientific decision

- Frozen tier: **E-B**, simulator-specific case study/protocol audit.
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

## PDF

- File: `output/pdf/sim2science_ecomd_2026_submission.pdf`
- SHA-256: `518cc620c04e2dbb3e9df2d88696f3f105d009656351c61cc4dca5a6827df8b4`
- Size: 145,971 bytes; 9 pages total; US Letter; references begin on page 5.
- Automated submission checks: all pass.
- Fonts: 24/24 embedded.
- Visual QA: all nine rendered pages inspected; no collision, clipping, missing glyph, or unreadable
  figure was found.

## Anonymous artifact

- File: `output/artifacts/sim2science_ecomd_2026_artifact.zip`
- ZIP SHA-256: `1b17784acf7fee16885331f1e13d2991fce4466e73d3b5540f097e7fc4f6c272`
- Manifest SHA-256: `74a2415a0ab79252450daa15ae9a0b395687b26f121fc370ba3e0f9dd9e51096`
- Manifest: complete, 596 files, derived outputs included, no missing final file.
- Two independent builds produced identical ZIP and manifest hashes.
- Archive integrity test and identity scan passed.
- Packaged test suite: 61/61 passed.

## Remaining user-owned release actions

- Confirm final author list, affiliations, conflicts, and OpenReview profiles.
- Confirm reciprocal reviewer identity and ability to complete the required confidential reviews.
- Host the anonymous artifact and insert its review URL in the submission form if the venue permits.
- Confirm the OpenReview title, abstract, TL;DR, keywords, license, and public-release selections.
- Upload the PDF, download the platform copy, rerun checks, and record the forum ID, paper number,
  receipt time, and downloaded-file SHA-256 outside public git.
