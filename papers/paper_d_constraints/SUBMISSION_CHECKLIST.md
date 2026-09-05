# Paper D submission checklist

Verification state as of 2026-09-05: items below re-verified against the committed
`main.pdf` (SHA-256 `7d0e2d60…b23d9c`, byte-identical deterministic rebuild) and the
clean-extraction supplement verifier (manifest `0cfa39d4…65c3296`). See
`OPENREVIEW_SUBMISSION_STEPS_20260905.md` for the PI-facing OpenReview procedure.

## Required before reviewer-facing upload

- [x] Confirm that the main paper, excluding references and the reproducibility/AI-use statements,
  remains within the ICLR 2027 nine-page limit. (Main text ends on p. 9; statements, references,
  and appendices follow.)
- [x] Confirm that the PDF author and metadata fields are anonymous and visually inspect every page.
  (Metadata carries no author/title fields; title page renders "Anonymous authors / Paper under
  double-blind review".)
- [x] Verify the supplement manifest in a clean extraction and reproduce every released analysis,
  result-derived TeX file, and figure byte-for-byte.
- [x] Keep public PDEBench data and trained checkpoint bytes out of the review bundle.
- [x] Resolve the Git-provenance double-blind gate. The development repository
  `howardwang1997/ecophys` was made PRIVATE on 2026-09-05 (0 forks at the time of the switch), so
  the retained original Git commit identifiers are no longer publicly resolvable during review.
  The gate stays resolved only if the repository remains private through the entire review and
  decision period (decision notification 2026-12-16; keep private through camera-ready,
  mid-February 2027, to be safe). The packager does not change repository visibility; the
  verification_liquidity protocol reads an external repository API and is unaffected.

## External actions not performed by the build

- No Git push, OpenReview upload, repository-visibility change, or submission action is implied by
  a successful local build.
