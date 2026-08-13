# Multi-stationary drift tomography — V11 equation and novelty audit

**Audit date:** 2026-08-13

**Branch:** `multi-stationary-drift-tomography-audit-v11`

**Final decision:** `V11_CONJECTURE_ONLY`

**Candidate states:** ambiguity-current claim `RETIRED_PRIOR_ART`; exact-coframe/immersion claim `CONJECTURE`

**Compute state:** Experiment 153 locked; no remote worker contacted or queued

## 1. Outcome

V11 does not currently supply an NMI or NCS paper candidate. Experiment 152 verified the frozen pointwise
Fokker--Planck identity and all six exact obstructions, but the closest-source audit closes the ordinary estimator
route:

- the single-density weighted divergence-free ambiguity is a published theorem;
- local score/Fokker--Planck residual fitting, global Stein/KSD fitting, affine-parameter rank conditions and
  sensitivity analysis are already supplied together by DyNoSeD;
- learning stationary diffusions jointly across interventions with an RKHS stationarity loss is established KDS;
- interventional stationary-SDE identifiability counts and nonlinear recovery bounds are already explicit; and
- controlled single-cell stationary diffusions already fit shared dynamics across perturbations and identify
  linearized effects under stated assumptions.

One narrow mathematical residual survives as `CONJECTURE`: the score-difference family is the differential of a
density-ratio map, so uniformly stable pointwise recovery on a closed state manifold is possible only when that
map is an immersion. In particular, exactly `d` nonbaseline densities can never span everywhere on a closed
`d`-manifold; at least `d+1` nonbaseline densities (`d+2` total environments) are necessary. The minimal abstract
density-family count is the Euclidean immersion dimension of the state manifold.

The proof is complete in `formal_cards_v11.md`, but this is not yet a paper claim. It is elementary, applies only
to uniformly conditioned pointwise inversion, and has no drift-blind feasible intervention design, finite-sample
rate or scientific witness. An exact circle construction is globally identifiable from two environments despite
the unavoidable pointwise rank defects, so T4 cannot be promoted to a general environment-count lower bound.

## 2. Exact equation-level disposition

| V11 object | Exact reduction or obstruction | State |
|---|---|---|
| pointwise drift formula | subtract stationary Fokker--Planck equations and solve `S b=q` | retained lemma; no novelty claim |
| weak estimator | stationary generator moments followed by basis expansion/least squares | `RETIRED_PRIOR_ART` |
| multi-density ambiguity current | `div j=0` and `j dot grad(rho_m/rho_0)=0` for every environment | `RETIRED_PRIOR_ART`; exact diagnostic |
| raw `sigma_min(S)` | changes under coordinate rescaling although rank is preserved | falsified as an intrinsic quantity |
| diffusion-metric frame operator | standard coordinate-invariant tensor/frame normalization | retained correction; no novelty claim |
| exact-coframe/immersion count | a closed `d`-manifold cannot immerse in `R^d`; abstract minimum is `imm(M)` | `CONJECTURE`; proof complete, novelty/value unverified |
| global drift identification | zero is the only admissible divergence-free current tangent to all ratio levels | open beyond the exact criterion; a two-environment circle example is globally unique despite unavoidable pointwise rank defects |

## 3. Primary-source comparison

| Primary source | Audited result | Consequence for V11 |
|---|---|---|
| Liu and Liu, [*Inversions of stochastic processes from ergodic measures of nonlinear SDEs*](https://arxiv.org/abs/2512.01307), Theorem 3.2 | With fixed diffusion in dimension at least two, two drifts share an invariant density iff their density-weighted difference is divergence free; the paper gives a skew-current counterexample. | The baseline ambiguity and rotational witness are occupied. V11's ratio tangency is the intersection of these known ambiguity spaces. |
| Lu, Kusmierz and Mihalas, [*Identifying Stochastic Dynamics from Non-Sequential Data (DyNoSeD)*](https://arxiv.org/abs/2502.17690), Eqs. 7--27 and Theorem 1 | Gives a local score-based Fokker--Planck residual, a global density-free Stein/KSD route, necessary-and-sufficient affine-parameter rank identification and Gram sensitivity, including non-gradient Lorenz dynamics. | Closes the proposed weak/local/global estimator and ordinary conditioning claims. A basis-expanded V11 is not a new method. |
| Lorch, Krause and Schölkopf, [*Causal Modeling with Stationary Diffusions*](https://proceedings.mlr.press/v238/lorch24a.html) | Learns nonlinear stationary SDEs across interventions with a generator RKHS stationarity condition (KDS) and tests unseen interventions. | Cross-environment weak stationarity loss is established. |
| Zweig et al., [*Towards Identifiability of Interventional Stochastic Differential Equations*](https://arxiv.org/abs/2505.15987), v5 | Gives tight intervention counts for a structured linear SDE family and nonlinear small-noise recovery bounds from stationary distributions under known shifts. | Broad “multiple interventions identify stationary SDE dynamics” and intervention-count framing are occupied. T4 must remain explicitly nonparametric, topological and pointwise. |
| Lorch et al., [*Latent Causal Diffusions for Single-Cell Perturbation Modeling*](https://arxiv.org/abs/2601.15341) | Fits latent stationary densities and shared perturbation-conditioned drifts; CLIPR identifies linear effects. The score objective restricts the fitted drift to a gradient field and lists nonzero curl as future work. | A non-gradient residual exists, but “apply a general FP/KDS objective” is already covered by DyNoSeD and does not establish novelty. |
| Nie et al., [*Solving the inverse Frobenius--Perron problem using stationary densities with input perturbations*](https://eprints.whiterose.ac.uk/id/eprint/161682/) | Recovers a one-dimensional discrete map from stationary densities generated by linearly independent input distributions. | Input diversity and stationary-density inversion are older principles, not V11 primitives. |
| Nucci and Leach, [*Jacobi Last Multiplier and Lie Symmetries*](https://doi.org/10.2991/jnmp.2005.12.2.9) | Reviews the Jacobi multiplier equation; the ratio of two multipliers is a first integral. | The density-ratio first-integral interpretation is classical. |
| Dumachev, [*Vector Hamiltonians in Nambu mechanics*](https://arxiv.org/abs/1802.01037) | Represents divergence-free phase flows through generalized Nambu mechanics and integral invariants. | The explicit tangent-current construction is established geometric machinery. |
| Anonymous ICLR 2026 submission, [*One Intervention per Component Is Enough*](https://openreview.net/pdf?id=vjI9tsebtP) | Studies OU recovery from observational/interventional steady states, with graph-structured intervention counts and regularized least squares. | Additional crowding for linear snapshot recovery; not relied on for the closure because it is anonymous and under review. |

The decision-relevant theorem/equation pages of the first four PDF sources were rendered and visually inspected,
not inferred from abstracts alone.

## 4. What Experiment 152 established

The sole formal run from `0ab9cba6594b1354447aa28e1f5e8cccce91b4a4` produced immutable raw SHA-256
`ee08eb70ed8551c8b7ff8cd8e98d9e93cda1a50ce1d1419be2210f0718a5862a` and decision
`IDENTITY_AND_OBSTRUCTIONS_CONFIRMED`.

- A full-rank two-dimensional nonreversible OU fixture recovered the exact rotational drift.
- A rank-one torus family preserved two common drifts separated by norm `1`.
- A rotational intervention with squared norm `45` did not move the stationary density at all.
- Incorrectly imposing a common diffusion produced maximum drift error `0.5`.
- A coordinate rescaling preserved rank but changed raw `sigma_min` from `1` to `0.1`; a nonlinear transform
  required a nonzero Itô correction.

These witnesses validate the equations and kill overbroad claims. They do not support novelty, empirical truth or
venue readiness.

## 5. NMI and NCS gates

### Nature Machine Intelligence

Current state: `NO_ADMITTED_CANDIDATE`. The exact-coframe result is at most the beginning of a theory paper. NMI
would require a non-equivalent estimator or intervention-design method, a global or minimax theorem with real
statistical consequence, and validation in at least two non-financial controlled systems. DyNoSeD, KDS and the
interventional-SDE paper are mandatory comparators.

### Nature Computational Science

Current state: `NO_ADMITTED_CANDIDATE`. NCS additionally needs quantitatively calibrated physical perturbation
fields, independently verified stationary ensembles, a substantive recovered non-gradient mechanism and a frozen
unseen-intervention prediction with independent replication. EcoMD and ordinary market regimes cannot supply
those semantics.

## 6. Resource and re-entry decision

- Experiment 153 remains locked because N0 did not pass and the surviving topology statement has not passed a
  human novelty/value audit.
- No generated sample, real-system outcome, market file or paid dataset was opened.
- The two V100 32 GB workers and RTX2060 were not contacted or queued; GPU use was `0.0` hours.
- More compute cannot create a theorem distinction, known intervention operator or stationary data contract.

Re-entry requires all of the following before computation:

1. an expert literature audit that confirms the immersion-dimension connection is not a known corollary in this
   inverse-SDE setting and is substantial enough to develop;
2. a statement stronger than a pointwise compactness obstruction, preferably a sharp global or minimax result;
3. a perturbation-design rule that does not presuppose the unknown drift or desired stationary densities; and
4. an equation-level distinction from DyNoSeD/KDS plus a credible controlled-system data path.

Absent those conditions, V11 is archived as `V11_CONJECTURE_ONLY` and the broader topic search may continue
without spending remote compute.
