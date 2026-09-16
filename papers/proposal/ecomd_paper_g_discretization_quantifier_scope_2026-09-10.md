# Paper G: representation equivalence and continuous discretization

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

Decision: `not_trigger`. This is a bounded primary-theorem scope audit, not a
new search cycle, candidate, theorem or experiment. The repository connection
is its neural-PDE discretization work and cycle 30's distinction between
model-grid consistency and numerical-label fidelity. The last record-only
turn was `no_progress`; this audit checks a previously unregistered source pair.

## Primary statements actually inspected

[Bartolucci et al., ReNO, NeurIPS 2023](https://papers.nips.cc/paper_files/paper/2023/file/dc35c593e61f6df62db541b976d09dcf-Paper-Conference.pdf):
selected formal definitions and conclusions; PDF pages 5 and 6 visually checked.
Definition 3.4 conditions equivalence on frames covering the operator domain
and range. Remark 3.5 identifies the compatible representation; Proposition
3.6 compares admissible representations of that operator. Discrete objects
are maps between coefficient ranges, potentially infinite sequences; they are
not stipulated to be finite-dimensional diffeomorphisms. Section 4's CNO
example preserves prescribed bandwidth. The conclusion separates aliasing
from approximation, training and generalization error. The earlier arXiv v1
has a different title; the proceedings text governs this audit.

[Furuya et al., arXiv:2412.03393v1](https://arxiv.org/html/2412.03393v1):
selected Definitions 1, 4, 5-8, Theorem 2, Proposition 1, and Theorems 3-4.
The no-go result rules out a continuous approximation functor over the stated
category of general Hilbert-space diffeomorphisms, with finite-dimensional
diffeomorphic outputs and property (A). It concerns a rule across operators,
not the impossibility of approximating every individual fixed map. The proof
overview uses orientation along a path. Proposition 1 gives the weaker,
projected-target approximation for strongly monotone diffeomorphisms;
Theorem 3 gives property (A) for strongly monotone layers of the specified
identity-plus-compact architecture. Theorem 4's decomposition is for a
bilipschitz layer of that architecture on a bounded ball, allowing a reflection.
It is not a theorem about every bilipschitz Hilbert-space map. Full proofs
were not independently checked.

## Compatibility test and consequence

The comparison must freeze four requirements before using opposite headlines:

| Requirement | ReNO statement | General no-go statement |
|---|---|---|
| Object varied | Admissible representations of an operator | A discretization rule over an operator category |
| Representation | Frames covering domain and range | Finite-dimensional subspaces and diffeomorphisms |
| Required property | Vanishing representation/aliasing discrepancy | Approximation plus continuity of the rule and categorical compatibility |
| Invertibility | Not required in Definition 3.4 | Required of original and discretized maps |

Our inference: these are compatible statements. Applying the no-go theorem
requires proving that a proposed construction satisfies its entire hypothesis
set. Treating any sampled neural predictor as such a functor is insufficient.
Conversely, a ReNO certificate does not establish accuracy relative to the
physical solution or the numerical teacher. Thus neither source removes
cycle 30's contribution blockers: elementary supplied-reference propagation
and direct parents for exact/stochastic supervision.

No physical state, legal intervention and response with opposed quantitative
predictions has been qualified here. No trained-model failure, implementation
defect, topology-driven empirical effect or novel remedy is asserted.

## Stop and reusable result

Stop this broad equivalence-versus-impossibility pairing. Do not generate a
coarse-grid counterexample outside the frame assumptions, present an arbitrary
noninvertible PDE predictor as a diffeomorphism, or relabel the cited monotone
construction as a new method. Preserve the four-requirement comparison for
future screening. Re-entry requires a specific repository-relevant operator
and common approximation contract producing an unresolved contradiction, or
a new result removing a recorded blocker. No candidate harvesting is authorized.

The audit used two primary works, one local article PDF and two rendered pages;
no scientific code, models, outcome arrays or new data assets were accessed.
Search-cycle, protocol and forecast records remain unchanged. The full Paper G
objective remains unachieved.
