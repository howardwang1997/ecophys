# Paper G: goal-error truth capability preflight

**PRIVATE / INTERNAL — source infrastructure, not public research evidence.**
Session started 2026-09-09T07:51:24Z; literature cutoff 2026-09-09. This was
written after interleaved reading and algebra, not prospectively frozen.

The previous goal turn made progress: cycle 30 supplied a formal contribution
closure and reusable continuum-ranking controls. Its canonical state was
revalidated before this preflight. This session examines the named blocker
`supplied_reference_certificate_is_elementary_error_propagation` and the
remaining need for an independently qualified physical truth bound. It does
not harvest a third neural-PDE measurement question.

**Decision: partial capability; no removed contribution blocker and no re-entry.**
Known elliptic variational structure can provide useful bounds on a model-pair
risk difference without an exact full-field reference. The construction is an
ordinary goal-oriented error estimate with established neural error-estimation
parents. The source does not yet qualify immutable execution, complete rights,
validated integration, independent confirmation or a cost advantage here.

## 1. Preserve the target before using a certificate

For a bounded Lipschitz domain, let V=H_0^1(Omega), let kappa(x) be symmetric
uniformly positive definite with lower bound kappa0>0, and define

    B(v,w) = integral grad(v)^T kappa grad(w),
    ell(w) = integral f w,       f in L2(Omega).

The physical solution satisfies B(u,w)=ell(w) for every w in V. Work with fixed
predictions m1,m2 in V, d=m1-m2, and **continuum L2** squared-risk difference

    D(u) = ||m1-u||_2^2 - ||m2-u||_2^2
         = C - J(u),
    C = ||m1||_2^2 - ||m2||_2^2,       J(w) = 2 integral d w.

This target is linear in the unknown solution because its squared term cancels.
It is not automatically the grid MSE of a benchmark. For a frozen bounded
observation map Q:V->R^n and fixed positive weight matrix W, the analogous
functional is J_Q(w)=2 (Qm1-Qm2)^T W Qw. Cell averages supply one bounded map.
Bare point evaluation in dimensions two and higher is not a bounded functional
on H_0^1 alone; extra regularity or a different observation contract is needed.
This preflight does not silently replace a locked benchmark's observable.

## 2. Goal-error identity and a fully specified sufficient bound

Let z in V solve B(w,z)=J(w). For any conforming approximations v,z_tilde in V,
define R_v(w)=ell(w)-B(v,w) and

    D_center = C - J(v) - R_v(z_tilde).

Then the exact identity is

    D(u)-D_center = -B(u-v,z-z_tilde).

Consequently, certified energy-error upper bounds E_p>=||u-v||_B and
E_d>=||z-z_tilde||_B yield

    D(u) in [D_center-E_p E_d, D_center+E_p E_d].

An interval wholly below zero certifies that m1 has smaller error; one wholly
above zero certifies m2. Crossing zero means unresolved. The product bound can
be useful when the adjoint is accurate, but no universal strict improvement
over cycle 30's norm bound or a cheaper computation is asserted.

For this diffusion problem, an explicit standard flux majorant follows directly
from integration by parts. With q in H(div;Omega) and a valid Friedrichs constant
||w||_2<=C_F||grad w||_2,

    E_p = ||kappa^(-1/2)(q-kappa grad v)||_2
          + C_F/sqrt(kappa0) ||f+div q||_2

is sufficient. Indeed, insert q into R_v(w), integrate div q, and apply
Cauchy--Schwarz and Friedrichs. Apply the same expression to z_tilde and a dual
flux p, replacing f by 2d, to obtain E_d for the continuum L2 functional.
The bounded-observation case needs its own dual-load representation.

Both identities are elementary consequences of the weak equation; this is not
a new method or theorem. Exact z makes the goal correction exact even with an
inexact primal v; exact v also eliminates the remainder. Setting m1=m2 gives
J=0 and the tied ranking. These are useful verification nulls.

For numerical evaluation, the norm integrals used in E_p and E_d need upper
enclosures, kappa0 needs a valid lower bound, and C_F needs a valid upper bound.
If the center itself has a certified integration/roundoff error eta, add eta
to the interval radius. A computed residual or an unspecified equivalence
constant is not yet a numerical certificate. No assumption of Galerkin
orthogonality is needed for the displayed identity.

## 3. Two exact controls that protect the observable and the bound

**Metric control.** For -u''=sin(x) on (0,pi) with zero boundary values, u=sin(x).
Normalize integrals by 2/pi. Predictions m1=u+(1/2)sin(3x) and m2=u+sin(x) have
L2 squared errors 1/4 and 1, but derivative-energy squared errors 9/4 and 1.
Thus their rankings reverse. In a symmetric coercive problem the energy-risk
difference can be evaluated without solving for u:

    D_B = B(m1,m1)-B(m2,m2)-2 ell(m1-m2).

This is the usual quadratic variational-energy identity. It does not certify
the L2 ranking; norm bounds do not preserve ordering. The control is unrelated
to a claim that Paper D uses the wrong metric.

**Integration control.** For -u''=f on (0,1), zero boundary values, take any
finite prescribed integration nodes x_i and f(x)=product_i(x-x_i)^2. With
v=0 and q=0, the majorant's f-squared term is zero at all those nodes, but its
integral is positive and the true solution is nonzero. A finite node sum alone
therefore need not upper-bound the continuous error. This is a standard
quadrature limitation, not a bug in a source implementation. It is an
unrestricted-function control: a fixed polynomial or band-limited family with
a sufficiently exact integration rule is an explicit null. No failure is
asserted under any paper's actual frozen function class or numerical protocol.

## 4. Selected primary sources and actual reading limits

| Source | Binding role and limit |
|---|---|
| [Roth, Schroeder & Wick, v1 (2021)](https://arxiv.org/pdf/2102.12450v1), section 2.2–2.3 | Neural adjoints and goal-oriented residual estimation are direct parents. The general nonlinear representation includes remainder terms; its approximate estimator is not automatically a guaranteed interval. |
| [Fanaskov, Rudikov & Oseledets, v1 (2024)](https://arxiv.org/html/2402.05585v1), sections 2.1–2.4 and reproducibility pointer | Neural auxiliary fields with functional error majorants are direct prior. Conformity, constants and continuous integrals remain conditions; actual numerical bounds and timing were not reproduced. |
| [Qiu, Dahmen & Chen, v1 (2025)](https://arxiv.org/html/2512.21319v1), selected section 3.1.2, equations 28–33 | Expands the already registered FOSLS parent: conforming trial spaces, boundary lifts and PDE-dependent norms matter. Norm equivalence is not an unqualified L2 ranking certificate. |
| [VLSF/UQNO repository](https://github.com/VLSF/UQNO), root README and directory metadata only | Documents an elliptic source family and code/notebook/data pointers, with an Unlicense label. Full license text, immutable replay and separate linked-data rights were not qualified. |

No notebook output, linked dataset, model weight or scientific implementation was
accessed. Search-only residual-corrector and error-model results were not promoted
to additional reviewed works. This is not a full literature audit or a new forecast.

## 5. Supported truth-asset family and remaining qualification

Supported analytically: symmetric uniformly elliptic diffusion, admissible
boundary conditions, conforming reconstructions, a declared L2 or bounded-Q
pairwise score, and valid primal/dual residual majorants. These equations do
not automatically cover Paper D's time-dependent advection or shallow water.
An explicit PDE/observation bridge is required before applying this source.

For each prospective instance, retain the full coefficient/forcing law, domain,
boundary lift, predictor reconstruction, score and quadrature weights, primal
and adjoint spaces, flux reconstructions, constants, quadrature enclosures,
solver/optimizer tolerances and all selection/RNG state. Pair the same physical
instance and freeze model selection before confirmation. Separate field
reconstruction error, numerical integration error and statistical risk uncertainty.

The root metadata qualifies the existence of a source lineage, not a ready
truth oracle. Software/dependency/linked-data and derived-release rights remain
unqualified; an immutable complete replay is not supplied. No participants or
outreach are involved. Existing Paper D partitions retain their evidence roles.
Reserve untouched coefficient/geometry families and an independently governed
confirmation source before outcome access; none is qualified now.

A future cost contract must include primal and adjoint solves, flux fitting,
certified integration, reconstruction, training and selection. Stop if the
interval overlaps zero at the allowed cost, the original score changes, the
PDE lacks the required stability/conformity contract, or any result reduces to
existing goal-oriented estimation. No speedup or actual ranking is claimed.

This preflight removes no recorded novelty blocker and creates no new question,
cycle, F3 subject or machine card. The qualified-trigger requirement after
cycles 29–30 remains binding. The next useful source update must supply an
actual same-observable capability or primary disagreement that changes a named
decision; another generic error-estimation method is not enough.
