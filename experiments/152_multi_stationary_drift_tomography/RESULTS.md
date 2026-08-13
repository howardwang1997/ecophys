# Experiment 152 result — exact identity plus exact obstructions

**Formal decision:** `IDENTITY_AND_OBSTRUCTIONS_CONFIRMED`

**Candidate admission:** false

**Novelty pass:** false

**Compute unlock:** false

**Raw SHA-256:** `ee08eb70ed8551c8b7ff8cd8e98d9e93cda1a50ce1d1419be2210f0718a5862a`

## Chronology

- V11 plan frozen at `df75a5c0166bbb7e933bdb0692a536cd8680c983`.
- Experiment preregistered at `4b899285b19997bbbf37265f9ecf91ebc8f431a7`.
- Implementation committed at `aa5f90ba039c7cb4258be12d6d6f8a476ce61eea`.
- Hash freeze and sole formal-run checkout: `0ab9cba6594b1354447aa28e1f5e8cccce91b4a4`.
- The guarded runner executed once from a clean checkout and wrote the raw artifact without overwrite.

## Exact witnesses

| Witness | Formal result | Consequence |
|---|---:|---|
| W1 one-dimensional sign | identity and drift errors `0.0` | The frozen Fokker--Planck sign convention is internally consistent. |
| W2 nonreversible OU | rank `2`, `sigma_min=1`, recovery error `0.0` | Spanning score differences recover the full drift, including rotation, at population level. |
| W3 torus alias | rank `1`, PDE residual `0.0`, drift separation `1.0` | Multiple environments do not identify drift when induced score differences fail to span. |
| W4 invisible rotation | intervention norm squared `45`, score rank `0`, residual `0.0` | Large intervention magnitude does not imply stationary-density excitation. |
| W5 unequal diffusion | correct error `0.0`, wrong-common-diffusion error `0.5` | Common known diffusion is a substantive identifying assumption, not bookkeeping. |
| W6 coordinate change | rank preserved; `sigma_min 1 -> 0.1`; Itô correction norm `6` | Raw singular-value conditioning is chart dependent, and nonlinear drift transforms need the Itô correction. |

All frozen expected values matched at absolute tolerance `1e-12`.

## Binding interpretation

Experiment 152 verifies only deterministic algebra and counterexamples. It does not show that the pointwise inverse
is novel, statistically usable or scientifically observable. In particular:

- the strong reconstruction differentiates stationary densities twice;
- the weak formulation is a stationary-generator moment condition already represented by KDS/Stein/Galerkin
  approaches;
- excitation must be measured from the induced density ratios, not intervention-vector magnitude;
- raw Euclidean conditioning cannot support a coordinate-free experimental-design claim; and
- an unknown or environment-dependent diffusion can alias the inferred drift even with exact densities.

The formal result therefore cannot unlock Experiment 153, generated samples, real outcomes or worker use. A
separate equation-level novelty audit must first isolate a theorem or estimator not equivalent to existing
stationary-diffusion inversion.

## Resource audit

- Inputs: committed analytic constants only; generated samples: `0`.
- Market or scientific data files read: `0`; sealed periods opened: `0`.
- Network access: none; device: Mac CPU; wall time: `0.02385` s.
- GPU use: `0.0` hours. Neither V100 worker nor the RTX2060 was contacted or queued.
