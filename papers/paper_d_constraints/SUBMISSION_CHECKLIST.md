# Paper D submission checklist

## Required before reviewer-facing upload

- Confirm that the main paper, excluding references and the reproducibility/AI-use statements,
  remains within the ICLR 2027 nine-page limit.
- Confirm that the PDF author and metadata fields are anonymous and visually inspect every page.
- Verify the supplement manifest in a clean extraction and reproduce every released analysis,
  result-derived TeX file, and figure byte-for-byte.
- Keep public PDEBench data and trained checkpoint bytes out of the review bundle.
- Resolve the Git-provenance double-blind gate. Formal records intentionally retain the original
  Git commit identifier, and the development repository is currently public. Before uploading the
  artifact, either make the development repository and referenced commit objects inaccessible for
  the entire review period or issue a separately verified anonymous provenance transformation.
  The packager does not change repository visibility.

## External actions not performed by the build

- No Git push, OpenReview upload, repository-visibility change, or submission action is implied by
  a successful local build.
