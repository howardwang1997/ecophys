# Paper G: gain-to-scale SCM embedding

PRIVATE / INTERNAL. September 11 Session 23. Decision:not_trigger.

- Primary Saha/Rathore/Garain NeurIPS2025 definitions1/8 and theorems1/2
  revisited; PDF pages2,4,6 visually checked. Theorem supplies solvability,
  not unknown-parameter identification or the preceding exact nuisance result.
- For Y=Phi D Y+LE and invertible known D, Z=DY satisfies Z=D(Phi Z+LE).
  This is a standard zero-shift scale intervention. Parameter-independent
  invertible observations preserve likelihood ratios, KL and regular Fisher
  information. Response contrasts must transform too; no cross-world coupling
  is newly identified from marginals.
- Product primitive E can feed several mechanisms via L, so correlated
  effective innovations are compatible with the source's general definition.
- Zero gains need care: Z=0 loses Y=epsilon at D=0. The relay SCM
  Y=Phi U+LE,U=Y, with scale intervention U=DY, retains the original Y for
  every D and adds no information. Deterministic relay laws are singular;
  learning-method density/faithfulness assumptions do not automatically transfer.
- If max|g_i|<=M and the class has M||Phi||_p<=r_bar<1, choose one fixed
  r_bar<c<1. Base maps fY=(M/c)Phi W+LE,fW=cY contract with bound
  max(r_bar/c,c)<1. Scaling W byD/M
  recovers the original gain model and meets the source's bounded-scale theorem.
  Small-theta two-arm ambiguity lies within this class for M=3.
- Merely invertible/noncontractive cases, transient actuation, additional
  temporal moments and estimator guarantees remain outside the theorem transfer.
- The earlier untransformed-formula distinction is not an irreducible novelty
  gap. Statistical problems remain open; no original method or topic qualified.
  Stop this semantic comparison without a substantive new trigger.

Formal: `papers/proposal/ecomd_paper_g_gain_scale_embedding_2026-09-11.md`.
Contract: `research/paper_g/gain_scale_embedding_20260911.yaml`.
Manifest: `research/paper_g/gain_scale_source_manifest_20260911.json`.

Model inclusion alone does not dismiss a new efficient-learning or inference
result within this class. It rules out the action-form distinction as sufficient
novelty. No such new method is established by this audit.

Verified by2026-09-10T19:26:48Z: graph293/274/1569,evidence1039,
triggers166/qualified0,cycles21/raw133/cards0. Scoped verifier,18 existing tests
and whitespace passed. PDF/three PNG hashes, predecessor records and
protocol/search/forecast hashes checked. These validate records, not theorem
novelty, statistical performance or an independent proof review.
