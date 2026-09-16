# Paper G: dynamic-PDE truth-source preflight

**PRIVATE / INTERNAL — source qualification, not public research evidence.**
Started 2026-09-09T08:02:38Z. Literature cutoff 2026-09-09. Written after
source inspection and algebra; no prospective freeze or forecast.

The preceding goal-error turn made progress by specifying an elliptic pairwise
risk bound and its observation/integration requirements. This preflight addresses
its remaining `same_observable_physical_bridge_unqualified` issue, while retaining
cycle30's contribution blocker. It is not a third neural-PDE question cycle.

**Partial capability.** A fixed public source version and six text-file hashes
are now available. Constant-speed advection admits a direct dynamic truth
identity under a complete initial-state/observation contract. The existing
released data do not yet have a qualified link to that continuous initial state;
the one-dimensional shock estimate inspected does not supply a ready numerical
radius for the repository's two-dimensional depth-only shallow-water task.
No closed contribution gate is reopened.

## 1. What was verified in the repository and public source

Read only the existing loader/restriction source and configurations:

- `scripts/run_constraint_iclr_pdebench_fno.py` distinguishes point restriction
  from arithmetic block averaging of stored grid values.
- `configs/constraint_iclr/pdebench_advection_fno_v2.yaml` names the beta0.4
  file, native1024 grid and block-average evaluation at256/512/1024.
- `configs/constraint_iclr/pdebench_swe_rdb_factorial_20260902.yaml` declares
  a two-dimensional dataset with the single observed channel `water_depth`.

These are protocol/source facts, not new data inspections or empirical findings.
Block averaging stored point values is not automatically exact integration of
a continuum field over a cell. Existing Paper D targets and evidence roles are
unchanged.

The official PDEBench repository was inspected at commit
`4ff3e3a4aa1561721b5571fa3a048a0a463e0568`. A filtered checkout-free source clone
was used; only six named source/config/license text blobs were extracted. No
source code was executed, and no data arrays, checkpoints or notebook outputs
were opened. Hashes and exact URLs are retained in
`research/paper_g/dynamic_truth_source_manifest_20260909.json`.

| Fixed source | Relevant contract |
|---|---|
| [Multisample advection generator](https://github.com/pdebench/PDEBench/blob/4ff3e3a4aa1561721b5571fa3a048a0a463e0568/pdebench/data_gen/data_gen_NLE/AdvectionEq/advection_multi_solution_Hydra.py) | Initializes cell-center arrays through `init_multi`, then evolves a conservative flux scheme. The selected beta0.4 config enables second-order reconstruction; cycle30's first-order upwind toy was not this implementation. |
| [Initial-condition helper](https://github.com/pdebench/PDEBench/blob/4ff3e3a4aa1561721b5571fa3a048a0a463e0568/pdebench/data_gen/data_gen_NLE/utils.py) | Selected `init_multi` forms trigonometric mixtures with optional absolute-value and window operations. Coordinates enter the recipe, so changing a grid with a fixed seed does not by itself freeze a continuous initial field. |
| [Exact-solution script](https://github.com/pdebench/PDEBench/blob/4ff3e3a4aa1561721b5571fa3a048a0a463e0568/pdebench/data_gen/data_gen_NLE/AdvectionEq/advection_exact_Hydra.py) | Its displayed solution family is one translated sine. It is an analytic control, not a demonstrated exact replay of the multisample release. |
| [beta0.4 configuration](https://github.com/pdebench/PDEBench/blob/4ff3e3a4aa1561721b5571fa3a048a0a463e0568/pdebench/data_gen/data_gen_NLE/AdvectionEq/config/multi/beta4e-1.yaml) and [base configuration](https://github.com/pdebench/PDEBench/blob/4ff3e3a4aa1561721b5571fa3a048a0a463e0568/pdebench/data_gen/data_gen_NLE/AdvectionEq/config/multi/config.yaml) | The specific file declares beta0.4,nx1024,t=0..2,save interval0.01,initial seed2022. Parameter agreement with a data file is not a generation-provenance proof. |

The current source pin does not establish which historical generator version,
dependency/RNG implementation, metadata conversion or per-trajectory latent
parameters produced the released file. No source defect is alleged or used as
motivation. Optional initial transformations are legitimate model choices; the
requirement is to preserve their resulting physical initial field when changing
solver fidelity.

## 2. Exact dynamic identity and its assumptions

On a periodic domain, let u_t+c u_x=f with known constant c. Let v be periodic,
spatially smooth and piecewise smooth in time, with residual
r=v_t+c v_x-f on each time slab and jumps j_k=v(t_k+)-v(t_k-). Then e=u-v obeys

    <e(T),g> = <e(0),z(0)> - integral_0^T <r(t),z(t)> dt
               - sum_k <j_k,z(t_k)>,
    z(t,x) = g(x+c(T-t)).

The identity follows by differentiating <e,z>, integrating the spatial transport
term by parts, and adding each time jump. No coercivity or elliptic approximation
is needed. With g=2(m1-m2), the terminal continuum-L2 risk-difference correction
is minus this expression. For bounded linear observation maps, use the adjoint
observation load; point-sample targets need their own regularity contract.

An elementary norm bound is

    ||e(T)||_2 <= ||e(0)||_2 + integral_0^T ||r(t)||_2 dt + sum_k ||j_k||_2.

Spatially discontinuous reconstructions require their distributional interface
terms as well. Numerical integration still needs enclosures for a rigorous
bound. This is standard transport/Duhamel analysis, not a new estimator.

With f=0 and the complete continuous initial function u0 known, physical truth
is simply u0(x-cT). A declared finite band-limited initial family can therefore
support exact Fourier evolution and sufficiently exact quadrature. The exact
solution of a chosen interpolation is not automatically truth for the original
unknown continuous initial field. Resetting truth to the last numerical frame
also changes the initial-state target and must be separately declared.

## 3. Exact observation controls

**Point observations.** On a periodic unit domain with h=1/N and x_j=jh,
w(x)=sin(2*pi*x/h) vanishes at every observed initial point. After a shift
s=cT that is not an integer multiple of h, its observed values are the constant
-sin(2*pi*s/h), which can be nonzero. Thus point observations alone do not
identify a shifted continuum field without an initial-family restriction.
A translated grid origin gives the same construction. Grid-aligned shifts and
a correctly resolved frozen band limit are explicit nulls.

**True cell averages.** In cell j take w=a_j on its first half and w=-a_j on
its second half, with periodic nonconstant coefficients a_j. Every initial cell
average is zero. After translation by h/2, cell j has average
(a_j-a_(j-1))/2, generally nonzero. The full spatial mass stays zero. This is an
observation-completeness control, not proof that two trajectories in the actual
PDEBench generator share an observation. It must not be used as a source-specific
nonidentification result without that membership check.

These controls do not propose a new history or closure method; those parents
remain closed. They prevent a finite observed array from being silently promoted
to an independently known continuous truth field.

## 4. Nonlinear shock theory: useful parent, incomplete numerical oracle

Read the introduction, theorem3.4 and remark3.5 of
[Giesselmann & Sikstel, arXiv2305.01340v1](https://arxiv.org/pdf/2305.01340v1).
The selected work concerns first-order finite-volume approximations of
one-dimensional hyperbolic systems under a suitable entropy-solution semigroup
and variation/stability conditions. It bounds an L1 error through computable
residual quantities multiplied by stability constants; remark3.5 states that
those constants are not feasible to compute. The later journal version was not
substituted for this pinned reading.

L1 control is not itself a fatal mismatch to squared-L2 model comparison:
for bounded fixed d=m1-m2 and reference v=u+delta,

    |D(v)-D(u)| <= 2 ||d||_infinity ||delta||_1.

This elementary dual-norm inequality preserves the risk target. What remains
unqualified is an actual numerical radius with known constants and the applicable
state/solution class. The inspected one-dimensional theorem does not certify
two-dimensional shallow-water trajectories from height alone: momentum/flux,
boundary conditions, reconstruction, entropy and stability contracts are additional
requirements. No claim is made that all future multidimensional bounds are impossible.

## 5. Rights, replay and confirmation boundaries

The pinned [root license](https://github.com/pdebench/PDEBench/blob/4ff3e3a4aa1561721b5571fa3a048a0a463e0568/LICENSE.txt)
uses MIT except where separately stated. Both inspected advection scripts retain
NEC headers specifying noncommercial internal research and additional conditions
on derivatives and publication. Therefore a blanket MIT reuse/release qualification
is not recorded. Linked data and dependency rights are separate. Only provenance
metadata is added to this project; external source bodies remain in the private
temporary source cache. No distribution, publication or execution is authorized.

A complete future same-input fidelity asset needs a frozen continuous initial
recipe with trajectory-level parameters and periodic extension, generation grid
and scheme, exact observation operator, physical clock, solver tolerances and
intermediate state, immutable dependency/RNG replay, admissible code/data rights,
and an untouched coefficient/initial-family confirmation partition. Holding a
seed fixed while changing coordinate-dependent initial generation is insufficient.

Reserve an independently governed nonlinear source before a nonlinear transfer
claim. Count truth construction, storage, numerical enclosures, training, tuning
and inference costs. Stop if released-data lineage, the original observable,
complete state, constants, rights or confirmation remain unqualified, or if the
scientific claim still reduces to existing approximation/observation theory.

This preflight adds a fixed source asset and dynamic controls. It removes no
recorded contribution blocker and authorizes no new question, cycle, forecast,
machine card, scientific implementation, solver, GPU or outcome access. The
next update must supply an actual same-observable capability or a primary
disagreement that changes a named decision, not another generic method label.
