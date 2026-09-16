# Paper G: reference budgets and symmetry-scope audit

PRIVATE / INTERNAL — source qualification and development mathematics only.
Session 3 began 2026-09-10 00:29 NZST (2026-09-09 12:29 UTC).
Decision: **partial capability, zero removed contribution blockers**.

## Reference capability resolved to its supported scale

The 4TU versioned metadata now pins the jet release to
`10.4121/13649885.v1`, dataset UUID `e6658c09-fec0-4a4c-9c32-085aed5a9e64`.
It lists one 781,569,028-byte archive, `Turbulent region.zip`, under CC0.
The archive and its internal documentation were not opened. This establishes
an outer file identity, not an inspected inner manifest or verified data checksum.
[Versioned RO-Crate metadata](https://data.4tu.nl/v3/datasets/e6658c09-fec0-4a4c-9c32-085aed5a9e64/versions/1/ro-crate-metadata.json).

Sciacchitano and Wieneke's 2016 paper provides the previously missing method
context: §§2.1 and 2.3.1 propagate covariance into derived quantities; §4.2
uses nominal and HDR jet measurements at approximately matched spatial
resolution. The reported reference precision advantage is an empirical property
of that setup, not a universal certificate. Its vorticity comparison uses the
same discrete derivative construction. Known systematic corrections, random
error, spatial correlation and derivative truncation remain distinct. Selected
formulae and acquisition passages were read and visually checked; no published
result was independently reproduced. [Primary paper](https://doi.org/10.1088/0957-0233/27/8/084006).

For a fixed linear derivative matrix A and a declared measurement-error
covariance Σ, the propagated covariance is AΣAᵀ. This standard identity is exact
for that discrete observable. It does not determine the difference between that
observable and a continuum derivative. Conversely, not every model-ranking
question requires a full covariance matrix: the paired squared-risk identity
and its conditional-mean requirements were already recorded in cycle 30.
Requiring an unnecessarily strong truth object would also be a mistake.

The useful asset is a reference comparison with a stated observation scale and
precision model. The remaining contribution blockers are not repaired by
collecting more calibration metadata. Routine expansion of this generic
measurement branch stops here. Its records remain reusable when a specific
new scientific estimand requires them.

## Separate source intake: alignment is not a demonstrated model disagreement

PACE-FNO v1 separates learned spatial-frame estimation, an observed-field
kinematic reduction, and terminal-frame restoration. Its theorem includes
alignment error. Appendix B.5 explicitly limits arbitrary rotations on the
discretized torus to its rotated-field construction; it does not assert that
every angle is an exact square-torus automorphism. The inspected scope was
introduction, §§2–3, selected Appendix A, B.5 and limitations; Appendix E was
not audited. [Primary preprint](https://arxiv.org/html/2605.18606v1).

Dym, Lawrence and Siegel establish continuity obstructions and weighted-frame
remedies in equivariant learning. Only their publisher abstract and metadata
were read here. A bounded learned frame construction and a global
canonicalization impossibility result cannot be treated as opposite predictions
for the same physical state merely from these descriptions.
[ICML 2024 primary record](https://proceedings.mlr.press/v235/dym24a.html).

An elementary boundary check makes the scope distinction concrete. On the
square torus R²/Z², a linear rotation descends to a well-defined map only when
RZ²=Z². Orientation-preserving orthogonal integer matrices give the four
quarter-turn rotations. For f(x)=cos(2πx₁), rotation by θ=π/6 gives
g(x)=cos(2π(cosθ x₁+sinθ x₂)); g(0)=1 but g(e₂)=−1 although 0 and e₂ denote
the same torus point. Quarter turns and arbitrary translations supply lawful
controls. This is ordinary lattice geometry, not a new theorem, a finding
about code, or a failure of all canonicalization methods. It is consistent
with the explicit Appendix B.5 qualification.

No same-state primary disagreement is qualified. In particular, the abstract
wording does not justify a new “symmetry failure” paper, and the constant-field
or ambiguous-frame cases would need the correct stabilizer and action contract
before any future audit. No candidate harvesting occurred.

## Decision and next source lane

The repository connection remains Paper D's neural PDE prediction and physical
constraint work. These sources do not reinterpret its experimental results.
The named blockers remain
`exact_and_stochastic_physical_supervision_have_direct_parents` and
`no_new_variance_cost_result`.

Further work should prioritize a primary model disagreement with matched
state, forcing, boundary conditions, response and conditioning, or an
identifying theorem that escapes the recorded parent reductions. A larger
reference archive or a coordinate-transformed benchmark alone is not that
trigger. This closes neither the entire neural-PDE field nor the Paper G goal.

No new raw question, cycle, F3 audit, forecast, machine card, scientific
implementation or outcome-asset access. Contract:
`research/paper_g/reference_budget_scope_audit_20260910.yaml`.
