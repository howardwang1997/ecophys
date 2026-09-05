# Paper D — OpenReview submission steps for the PI (prepared 2026-09-05)

All dates and policies below were verified against the official ICLR 2027 pages
(`iclr.cc/Conferences/2027/AuthorGuidelines` and `CallForPapers`) on 2026-09-05.
Everything here is account-level PI action; no frozen scientific result changes.

## Hard deadlines (AoE = UTC−12)

| Date | Action |
|---|---|
| **2026-09-18 23:59 AoE** | Abstract deadline (genuine abstract; placeholders are deleted). No authors may be **added** after this. |
| **2026-09-25 23:59 AoE** | Full paper + supplementary material deadline. No edits of any kind after this. |
| 2026-11-05 | Reviews released; author–reviewer discussion opens. |
| 2026-11-18 | End of public discussion; paper revisions allowed until then. |
| 2026-12-16 | Decision notification. |

Submission system: https://openreview.net/group?id=ICLR.cc/2027/Conference

## Step 0 — do immediately: OpenReview profile

If no OpenReview profile exists yet, create it **now**: profiles created without an institutional
email go through moderation that can take **up to two weeks**, and the abstract deadline is
2026-09-18. An institutional email activates instantly. Ensure the profile's publication list is
accurate — incorrect profile information is grounds for desk rejection, and reciprocal-reviewer
eligibility is determined from the profile.

## Step 1 — reciprocal-reviewer eligibility (new 2027 policy; affects desk rejection)

- Every submission must have **at least one author registered to review ≥3 papers**.
- An author is *qualified* if they have at least one **accepted** primary publication at:
  ICLR / NeurIPS / ICML / UAI / AISTATS / JMLR / TMLR, ACL-family, COLM, CVPR-family, AAAI /
  IJCAI / JAIR, ICRA / IROS / RSS / CoRL, KDD, or COLT — accepted **by the abstract deadline**
  (workshop/findings-adjacent items like tiny papers, demos, and industry tracks do not count).
- **If the PI has such a publication**: list it on the OpenReview profile. After the abstract
  deadline OpenReview will notify all authors to register as reviewers; complete the registration
  (≥3 papers). If no author registers, the paper is desk-rejected.
- **If no author qualifies**: the submission is *exempt* from this requirement, but each author is
  then capped at one such paper — which this single submission satisfies. No action needed beyond
  the accurate profile.
- Other quota: max 20 papers per author (not binding here).

## Step 2 — by 2026-09-18 AoE: submit title + abstract

Title (paste):

> When Are Exact Conservation Layers Plug-and-Play? Identifying Training–Inference Path
> Dependence in Neural PDE Surrogates

Abstract (paste; macros expanded from the frozen figure macro files):

> Exact conservation layers are often treated as modular post-processors, but in autoregressive
> surrogates projection during training changes the learned representation and projection during
> inference changes future inputs. We separate these interventions with an eight-cell
> output-coordinate-by-training-by-inference cube and prove that projected training leaves the raw
> invariant channel gauge-nonidentifiable. In a prospectively frozen, 30-seed PDEBench Advection
> experiment, a small ordinary bundled interaction (-0.00189) conceals a three-way interaction of
> J=0.22974 [0.19644, 0.26345], material in 9/12 mandatory resolution–horizon cells.
> Opposite-signed training and inference path credits cancel, and damage from removing projection
> appears only after autoregressive feedback. An independently frozen 30-seed 2D shallow-water
> replication gives J=-86.69343 [-107.65055, -66.68345], material in 6/8 cells, while projection
> jointly improves conservation, conserving RMSE, and positivity. A separately registered larger
> U-Net transfer does not meet its gate: J=-0.08415 [-0.26665, 0.13334] is unresolved and only
> 3/12 cells are material. A direct same-checkpoint input-gauge intervention yields an OOD
> feedback-to-baseline ratio of 8.68398 [7.91007, 9.50538], above the frozen 0.10 threshold at all
> resolutions. Its seed-level association with final damage, like a local gradient association,
> remains unsupported. Exact enforcement can therefore become non-detachable: projected training
> can identify the deployed predictor while leaving its raw invariant component undefined in the
> tested FNOs, but the U-Net boundary precludes an architecture-general claim.

Only the abstract is mandatory at this stage; the PDF can be attached any time before 2026-09-25.
Title/abstract may be edited until the full-paper deadline (but must remain the same paper).

## Step 3 — by 2026-09-25 AoE: upload PDF + supplementary

| Upload | Path | Identity |
|---|---|---|
| PDF | `papers/paper_d_constraints/main.pdf` | SHA-256 `7d0e2d60b38ea5980c7df772e5b437e9de891bb0e98518beb14f8b7221b23d9c`; 16 pages total, main text ends p.9 (limit: main text ≤9 pages; statements/refs/appendix excluded) |
| Supplementary (zip) | `output/paper_d_constraints_artifact.tar.gz` | Built 2026-09-04 by the deterministic packager; passed 138 clean-extraction tests |

The supplementary single-archive form matches the author-guidelines option "anonymize your code,
put it in a .zip file and submit it as supplementary materials".

### Optional pre-upload re-verification (nothing has changed since the 2026-09-05 pass)

```bash
conda run -n ecophys-paper-d python scripts/build_paper_d_supplement.py --verify
cd papers/paper_d_constraints && env SOURCE_DATE_EPOCH=0 conda run -n ecophys-paper-d tectonic main.tex
```

Verifier passed with manifest `0cfa39d457dea1fa057cbf5f67eb64b475a7f160f3b4b31752191993565c3296`;
the rebuild was byte-identical. If either command now fails, stop and re-audit before uploading.

## Double-blind status

- Development repository `howardwang1997/ecophys` has been PRIVATE since 2026-09-05 (0 forks at
  the switch). Keep it private through the review, decision (2026-12-16), and ideally camera-ready
  (mid-February 2027). Formal records intentionally retain original Git commit identifiers; with
  the repository private these are not publicly resolvable during review.
- PDF metadata and title page verified anonymous on 2026-09-05; no identifying strings in tex/bib.
- arXiv posting is permitted during review but neither required nor currently planned.

## Warnings (from the official guidelines)

- No edits — however small — are possible after the full-paper deadline.
- Submissions are archival: even withdrawn papers remain public on OpenReview and are
  de-anonymized.
- Do not submit a placeholder abstract; duplicate/placeholder abstracts are removed.

## After submission

Reviews 2026-11-05 → author responses (OpenReview comments) and optional paper revisions until
2026-11-18 (pdfdiff is applied; large post-submission changes may be ignored by reviewers) →
decision 2026-12-16. Camera-ready instructions arrive mid-February 2027 (10-page main-text limit
at that stage).
