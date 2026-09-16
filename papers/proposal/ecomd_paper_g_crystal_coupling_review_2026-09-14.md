# Paper G crystal-coupling candidate — methods and contribution review

PRIVATE / INTERNAL. 2026-09-14 NZ. This is a bounded research decision record,
not publishable scientific evidence. Subject: `g40_learned_mode_coupling_repair`.

## Decision

**Park nonterminally.** The fixed-composition crystal-repair question remains plausible,
but a specific transferable learning contribution and total-cost advantage are unqualified.
Do not initiate implementation or expand routine literature collection for this candidate.
This decision does not establish that mode-aware learning cannot help or that crystal ML
is exhausted. The original Cycle40 candidate record remains historical and unchanged.

The strongest update is that the existing GA is itself mode-informed. A comparison
against an uninformed GA would fail to test the proposed contribution. Two hand controls
also strengthen the required local-fitting comparator and distinguish constrained from
relaxed anharmonic energy. Neither is a new theorem or a measured material result.

## Exact parent comparison

| Parent and reading scope | Existing action/information | Remaining distinction |
|---|---|---|
| [VibroML, Appendix S.1 and selected S.8 settings](https://arxiv.org/html/2604.27685v1) | GA initializes from combinations of soft-mode displacements and cell deformations. Variation includes structural crossover and mutations that can couple another soft mode; phonons are recomputed. Search can continue after stability to explore further polymorphs. | Learning a transferable anharmonic prior is not specified by this workflow, but mode-informed search itself is already present. Match stopping targets; first stable repair and continued polymorph exploration are different workloads. |
| [RL-CSP, selected indexed primary methods and conclusion](https://pubs.rsc.org/en/content/articlehtml/2023/dd/d3dd00063j) | REINFORCE adapts probabilities over existing basin-hopping actions during a run; the tested policy conditions on energy. Local relaxation follows trial generation. | Online adaptation already exists. Cross-structure mode coupling is a different representation, not automatically a contribution. The paper's CSP objective is not the exact phonon-stability repair contract. |
| [CASTING, selected representation and continuous MCTS methods](https://www.nature.com/articles/s41524-023-01128-y) | Continuous tree search perturbs coordinates/lattice, uses local relaxation, adaptive depth-dependent radii and node selection. Composition-preserving atom-count changes are among its actions. | A mode prior could alter proposals, but learning/adapting continuous crystal search is occupied. Match allowable atom counts, cell support and final objective before performance comparison. |
| [Learn2Hop, sections 2.3 and 3.1, Table 1](https://proceedings.mlr.press/v139/merchant21a/merchant21a.pdf) | The atomic optimizer receives forces, positions, optimizer state, species and radial neighborhood features; its learned updates target low final energy. | The selected formulation does not supply this candidate's explicit anharmonic mode model. Chemistry/geometry conditioning and learning search are nevertheless existing contributions. |

Two new works (RL-CSP, CASTING), plus two deeper readings of existing works; not four
new works or four full reviews. Cycle40's initial three-work allocation is preserved;
this separate follow-up has a two-new-work cap, now consumed. Five unique primary works
have been retained for this route including PhononBench. No code, model or data payload
was accessed. No matched primary prediction disagreement has been established.

## R1 — forces make a stronger local baseline than pair enumeration

Assume an exact local family with known harmonic and self-quartic terms,

\[
V(x)=-\frac12\sum_i a_i x_i^2+\frac14\sum_i b_i x_i^4
       +\frac12\sum_{i<j}\Gamma_{ij}x_i^2x_j^2,
\quad \Gamma=\Gamma^\top,\quad \Gamma_{ii}=0.
\]

For a probe with every x_i nonzero, the complete gradient gives

\[
y_i=\frac{\partial_i V+a_i x_i-b_i x_i^3}{x_i}
    =\sum_j\Gamma_{ij}z_j,\qquad z_j=x_j^2.
\]

For m modes choose m probes with columns
z^(j)=t²(1+epsilon e_j), t>0 and epsilon>0. Then
Z=t²(11^T+epsilon I) is invertible, and **Gamma=YZ^{-1}**.
Thus m complete force evaluations suffice in this noiseless restricted family;
one does not need a separately evaluated grid for every mode pair. This is a sufficient
construction, not a minimal-query theorem or a real-crystal complexity guarantee.

Unknown self-quartic terms can instead be included on the diagonal of the fitted
symmetric coefficient matrix. General cubic/quartic tensors, noisy forces and locality
constraints require different designs. Small t worsens signal conditioning; keeping the
probe inside a fixed displacement radius constrains t as m grows. A full force vector
has a real computation cost, not the cost of a free scalar observation. Low rank is a
possible assumption for both learned and online-fit methods, not a learner-only privilege.

Inference: the proposed learner must beat information-efficient force fitting, not just
exhaustive pair scanning. This construction supplies no observed advantage for either.

## R2 — unstable-subspace energy is not the relaxed energy

Let x be initially unstable and s initially stable, and take a,k,d>0:

\[
W_c(x,s)=-\frac a2x^2+\frac b4x^4+\frac d6x^6
          +\frac k2s^2+csx^2.
\]

At the origin the Hessian is diag(-a,k) for every c. The restricted curve W_c(x,0)
also does not depend on c. But exact stable-coordinate relaxation gives

\[
s_*(x)=-cx^2/k,\qquad
W_c(x,s_*)=-\frac a2x^2+\frac14(b-2c^2/k)x^4+\frac d6x^6.
\]

For a=b=k=d=1, c=0 yields stable minima with x²=(sqrt(5)-1)/2;
c=1 yields x²=(1+sqrt(5))/2 and s=-x². The positive sixth-order term keeps
this family bounded below. Identical initial harmonic state and restricted curves
therefore need not predict the same relaxed distortion amplitude or structure.

This does not defeat the original candidate, which permits full relaxation; it means
its fitting target must distinguish constrained energies from relaxation-conditioned
energies. Moreover, at (x,0), the full stable-coordinate force is -c x², so a nonzero
probe already exposes c in this family. No hidden-information advantage follows for ML.
The same distinction applies to relaxed cell strain and other stable coordinates.

## What would change the decision

A return should supply a concrete construction or primary mechanism result explaining
transfer beyond mode-informed GA, online action adaptation, capable learned optimizers
and same-information local fitting. For example, a specified cross-chemistry structure
in the relaxation-conditioned coupling, together with why the prior saves enough probes
to pay for training and repeated mode construction, could justify another bounded review.
This is a condition for reconsideration, not a claim that such structure has been found.

The comparison would need matched success/energy/stability targets and action support;
first-use and declared amortized costs; independent final stability validation; and an
untouched chemical/prototype split. Those contracts and an economical concrete method
remain unresolved. A new neural architecture or more candidate metadata alone does not
remove the present blocker. Do not replace the scientific question with a generic
calibration exercise or present these standard controls as a stand-alone new paper.

No new formulation, cycle, forecast, F2 qualification, F3 audit or machine card. No
implementation, outcome payload, simulation, training, GPU, laboratory work, outreach,
delegation or publication. Paper G remains 84 formulations / 24 cycles / 0 cards;
detailed ledger 31 / 168 and historical-inclusive 40 / 224. After recording: graph
328 nodes / 279 edges / 1920 locators, evidence1197; candidate0 / parked10.
Next general allocation should start from a different unsaturated native scientific
obstruction unless this route receives the named contribution-changing result.
