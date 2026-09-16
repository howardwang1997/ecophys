# Paper G: finite local sampling resolution

PRIVATE / INTERNAL. September 11 Session 21. Decision: not_trigger.

- Resolves the finite-grid question left by flux/locality audit. In Ye/Li/Yan
  2504.09807v1 Eq11, five distinct period-two samples give a rank4 trigonometric
  matrix. A 5-by-5 subgrid identifies16 coefficients per velocity,32 total.
  The declared54-by-54 input contains such a subgrid. Exact initial samples
  therefore admit no distinct same-family exterior-only twin.
- This is existence of a decoder for the declared observation, not proof of
  actual architecture expressivity, learning, numerical robustness or locality.
- Constant-coefficient continuum linearization preserves these modes. Sampling
  all four fields recovers the full current linearized state without knowing
  observation time. Finite-time Fourier evolution is invertible.
- Conditional on C1 regular nonlinear solution dependence, the initial-parameter
  observation derivative is injective at rest at any fixed finite time. A32-row
  minor and inverse-function theorem give local fixed-time recoverability.
  No global/Gaussian-wide or mixed-time nonlinear injectivity established.
- Noise amplification bounded by1/[0.6 sigma_min(Bx) sigma_min(By)] in Frobenius
  norm; no numerical singular values or practical performance inferred.
- Standard paper-only consequences, no original theorem/method. Closed numerical
  teacher route remains closed. Stop sampling-pattern/conditioning variants as
  candidate generators absent a nonstandard matched-contract residual.
- Reuses one primary source and its intact HTML cache. No new source record,
  question, cycle, forecast, outcome access, scientific computation or execution.

Formal: `papers/proposal/ecomd_paper_g_local_sampling_resolution_2026-09-11.md`.
Contract: `research/paper_g/local_sampling_resolution_20260911.yaml`.
Manifest: `research/paper_g/local_sampling_source_manifest_20260911.json`.

Verified by2026-09-10T19:01:08Z: graph293/274/1562,evidence1038,
re-entry164/qualified0,cycles21/raw133/cards0. Scoped verifier,18 existing
tests and tracked whitespace passed. Existing article cache and predecessor
formal/contract hashes unchanged; protocol/search/forecast unchanged. Record
checks do not establish theorem novelty or provide independent proof review.
