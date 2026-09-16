# Paper G: unknown-nuisance gain identification

Successor `project_paper_g_gain_scale_embedding_2026-09-11.md` places this
equilibrium experiment inside existing cyclic scale-intervention SCMs, including
a sufficiently small uniform neighborhood of its exact two-arm ambiguity.
Solvability and identification remain separate; the results below are unchanged.

PRIVATE / INTERNAL. September 11 Session 22. Decision:not_trigger.

- Existing known-gain notes left nuisance-projected information open. For iid
  Gaussian equilibrium precision `(I-Phi D)^T K(I-Phi D)`, common unknown K,
  Phi=[[p1,b+a],[b-a,p2]], at K=I,a=b=0 set h_i=g_i/(1-p_i g_i),s=h1+h2,d=h1-h2.
  Efficient information for physical-coordinate a is min_uv sum n_e(d-u-vs)^2.
  Diagonal nuisance scores are orthogonal at this base. Generic two-arm designs
  with distinct s are locally blind; equal-s special cases require separate care.
- Exact two-arm curve: D1=I,D2=diag(2,3),R=exp(theta J),
  Phi=(I-R)(D2-R)^-1,K=(I-Phi)^-T(I-Phi)^-1. Both precisions equal I for all
  small theta, while a=-3theta/4+O(theta²). Opposite directions have identical
  laws at all sample sizes despite inverse-gain differences0 and1/6. K is common
  across arms, not held fixed across competing unknown-parameter models.
- Adding D3=diag(3,2) at zero feedback gives s=(2,5,5),d=(0,-1,1),
  efficient information2n for n/arm and full seven-parameter local rank.
  Three-arm noncollinearity is a local criterion, not global/uniform inference.
- Precision-weighted q=skew(K Phi) is distinct from a when K unknown. Its
  information projects d on t=1+p1*h1+p2*h2 and s, not silently on1 and s.
- The previous known-K/diagonal-reciprocal results remain valid; richer temporal
  moments in the primary output-only paper are not part of this equilibrium
  experiment. No contradiction of that paper's theorem or empirical claim.
- Standard score/Gram/rank consequences; no new independent method, uniform
  inference, truth asset or contribution blocker removed. Stop variants of this
  two-channel calculation absent a nonstandard residual. No execution authority.

Formal: `papers/proposal/ecomd_paper_g_gain_nuisance_resolution_2026-09-11.md`.
Contract: `research/paper_g/gain_nuisance_resolution_20260911.yaml`.
Manifest: `research/paper_g/gain_nuisance_source_manifest_20260911.json`.

Verified by2026-09-10T19:16:48Z: graph293/274/1565,evidence1038,
triggers165/qualified0,cycles21/raw133/cards0. Scoped verifier,18 existing tests
and whitespace passed. Both predecessor formals and protocol/search/forecast
hashes intact; evidence registry preserved. Record checks are not independent
proof verification or scientific novelty clearance.
