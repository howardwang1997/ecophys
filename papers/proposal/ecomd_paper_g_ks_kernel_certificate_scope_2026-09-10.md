# Paper G: scope of a sampled Keller–Segel moment certificate

**PRIVATE / INTERNAL — paper-only development analysis, not public evidence.**
Session started 2026-09-09T13:50:42Z (2026-09-10 01:50 NZST).
This is the bounded follow-up to the critical-aggregation truth preflight. The
previous goal turn made progress; its records and source hashes were revalidated.
Nothing here is a prospective forecast, independent confirmation or new cycle.

**Decision: partial capability, no re-entry.** The kernel contribution to a
specified moment balance admits a bounded finite-sample estimate. This resolves
one narrow computational concern from the previous session without needing a
density upper bound. It does not upper-bound the full velocity residual, certify
density accuracy, or establish novel event-time prediction. Generic scalar-moment
certification is not advanced as a Paper G topic.

## 1. Minimal primary comparison

[Wang–Xin–Zhang, DeepParticle v2](https://arxiv.org/html/2209.00109v2),
Sections 2.1–2.2,3.4 and selected 4.1 passages, explicitly uses a regularized
particle teacher, compares second moments and discusses regularization effects.
Thus neural-versus-particle virial diagnostics and teacher regularization are
already direct parents. Equation 7 multiplies the **potential**, and Equation 8
differentiates it. The [PDF](https://arxiv.org/pdf/2209.00109v2) page4 was visually
checked; code and raw results were not inspected. The preprint is dated
2024-01-29, linked to the Physica D 460 (2024),134082 lineage. Final-article text
identity was not audited. A later paper's citation of this method does not pin
its exact executed kernel.

[Fournier–Jourdain v1](https://arxiv.org/html/1507.01087v1), Sections 1.1–1.4
and 2 selected passages, gives a different, explicitly regularized **force**,
uses odd-kernel symmetrization, and distinguishes interacting particles from an
infinite-population law. These are direct classical parents of the calculations
below. Their convergence regime is not silently extended to supercritical mass.

[Hoeffding 1963](https://doi.org/10.1080/01621459.1963.10500830) supplies the
standard bounded-independent-sample concentration parent. Publisher metadata and
abstract were read through the primary search record; full text was unavailable.
The elementary bound used here is derived below. The existing 1948 U-statistic
registry entry is reused for the distinction between distinct pairs and diagonal
self-pairs; no new U-statistic result is claimed.

Prior critical-mass, log-HLS and conditional-reconstruction sources retain the
reading scopes in the preceding preflight. No full literature neighborhood opened.

## 2. Freeze the full kernel before estimating its effect

Use the whole plane, no advection or screening, normalized smooth density p,
diffusion μ>0, attraction χM>0 and finite centered second moment J. Write

    K(r)=log(r/ℓ)/(2π),
    gδ(r)=2π r Kδ'(r),
    Dδ(r)=1−gδ(r),
    c=χM/(2π),  κ=c−4μ.

The length reference ℓ is fixed together with the regularization. For an exact
log potential it only changes an additive constant; after a nonlinear operation
on that potential it must not be silently changed. All following statements
concern the declared mathematical kernel, not an uninspected implementation.

For the regularized mean-field velocity

    Aδ[p]=−μ∇log p−χM∇Kδ*p,

oddness and exchange of x,y give

    ∫p(x)(x−m)·∇Kδ*p(x) dx
      = 1/2 E[(X−Y)·∇Kδ(X−Y)],          X,Y iid with law p.

Consequently an exact regularized mean-field trajectory obeys

    J' = −κ + c Cδ(p),
    Cδ(p)=E[Dδ(|X−Y|)].

This is a classical virial symmetrization. It concerns the scalar drift of J,
not the vector norm of the kernel bias and not the difference between entire
solutions. Finite interacting-particle empirical moments have an additional
stochastic and finite-N contract; they are not substituted in this equation.

Two explicit regularizations make the source distinction concrete:

1. The force in Fournier–Jourdain Equation 8 is −x/[2π(r²+δ²)]. In potential
   notation this gives gδ=r²/(r²+δ²), Dδ=δ²/(r²+δ²), hence 0≤Dδ≤1.
2. The potential in DeepParticle Equation 7 is

       Kδ(r)=log(r/ℓ) r²/[2π(r²+δ²)].

   Differentiation instead gives

       gδ(r)=r²/(r²+δ²)+2r²δ² log(r/ℓ)/(r²+δ²)².

   At r=δ, gδ=1/2+log(δ/ℓ)/2. The first regularization's [0,1] range cannot
   be assigned to this second expression. This is a check of the written
   mathematical definition, with no claim about the source's executed code,
   numerical prevalence or a new physical mechanism.

Nevertheless the second Dδ is bounded for every fixed δ/ℓ. Let

    dδ=|log(δ/ℓ)|/2+1/4.

With s=r/δ, u=log s, the extra term in gδ is
2s²[log(δ/ℓ)+log s]/(1+s²)². Its constant part is bounded in absolute value
by |log(δ/ℓ)|/2, and its remaining part has absolute value
|u|/[2 cosh²u]≤1/4, since cosh²u≥1+u²≥2|u|. Therefore

    −dδ ≤ Dδ(r) ≤ 1+dδ,
    range width Rδ = 1+2dδ = 3/2+|log(δ/ℓ)|.

No density bound is involved. These are different legal kernels at matched δ;
there is no universal correction depending on δ alone. The previous audit's
missing exact-kernel description is narrowed at the **written parent** level;
the later DeepLagrangian implementation remains uninspected.

## 3. Finite-sample estimation of the scalar correction

Freeze θ, t, δ, ℓ and the observation contract before evaluation. Assume access
to fresh independent draws from the fixed generated density pθ(t). With n
independent pairs, let

    Ĉδ = (1/n) Σ Dδ(|Xi−Yi|).

If Dδ has a known range of width Rδ, then

    P(|Ĉδ−Cδ|>e) ≤ 2 exp[−2n e²/Rδ²],
    eα = Rδ sqrt[log(2/α)/(2n)].

For completeness: the log moment generating function of a centered bounded
variable has second derivative equal to a variance under exponential tilting.
The tilted law has the same range, so that variance is at most Rδ²/4. Integrate
twice from zero, use independence, and optimize the Chernoff parameter. Apply
the same calculation to the negative variable and a union bound. This is the
standard Hoeffding proof, not a new sample-complexity theorem.

Cost is 2n generated samples and n pair evaluations. This is not a measured
wall-time or an optimality result. Using every pair does not create n²
independent observations. Disjoint labels inside one interacting-particle
simulation also do not make the particles independent. Resampling a fixed
empirical cloud with replacement estimates a functional of that empirical law,
not automatically the continuum target. Fresh latent draws from a fixed
pointwise generator do meet the stated conditional-iid contract; batch-coupled
generation would require a different analysis.

For a fixed nonnegative time weight b(t), define B=∫₀ᵀb(t)dt>0. Independently
draw times Si with density b/B and two independent pθ(Si) draws per time. The
same range bound estimates

    Cδ,b = B⁻¹ ∫₀ᵀb(t)Cδ(pθ(t))dt.

This removes deterministic time-grid quadrature from this single integral when
the stipulated continuous-time sampler is available. It is not uniform-time
coverage. Selecting θ,δ,b or an endpoint after seeing these draws needs fresh
evaluation or an explicit simultaneous bound. None of these draws was taken.

## 4. What the correction contributes to the persistence bound

For a smooth finite-moment hypothesis satisfying

    ∂t p̂ + div[p̂(Aδ[p̂]+εδ)] = 0,

let Lδ,shape=∫∫p̂|εδ−∫p̂εδ|². The center-subtracted virial identity gives

    J' = −κ + c Cδ(p̂) + 2∫p̂(x−m)·εδ.

For b(t)=a/(1+at), a>0, B=log(1+aT), the same square completion as in the
previous session implies

    Lδ,shape + c B Cδ,b
      ≥ b(T)J(T) − aJ0 + κ B
      ≥ −aJ0 + κ B.

An upper confidence bound U on Cδ,b therefore yields, on its coverage event,

    Lδ,shape ≥ max{0, −aJ0 + κB − cBU}.

This is a lower bound on necessary action for the stipulated hypothesis and
kernel. If an **independent certified upper bound** on Lδ,shape also existed,
one could test compatibility with persistence. The pair statistic supplies no
such upper bound. A training minibatch loss is not automatically that bound.
Nor does controlling Cδ bound ∫p̂|χM(∇K−∇Kδ)*p̂|²: a scalar projection does
not upper-bound a vector norm. The generic full predictive-certificate claim
therefore remains unqualified despite the bounded scalar estimate.

## 5. Exact scalar agreement does not identify the density

Take a smooth centered radial reference solution p(t) of the unforced equation
on a pre-singularity interval, with finite J(t)>0. Its covariance is J(t)I/2.
Choose a smooth η(t), η(0)=0, |η|<1, and define

    S(t)=diag(sqrt(1+η(t)), sqrt(1−η(t))),
    p̂(t)=S(t)#p(t).

This is a smooth invertible transformation with the same initial density,
normalization and center. It preserves J(t) exactly for every t, so the scalar
virial residual J'+κ is identically zero. But its covariance eigenvalues are
J(1+η)/2 and J(1−η)/2, and its eigenvalue gap is |η|J>0 when η≠0. The
reference gap is zero. The gap does not disappear on rotating coordinates.

If p has continuity velocity v, the transformed curve has velocity
S'S⁻¹x+S v(t,S⁻¹x); it is a legitimate density-flow hypothesis, not merely a
disconnected sequence of marginals. It is not the same unforced radial PDE
solution. This construction is a standard moment nonidentification control,
not a trained-network result or a claim that its softened-kernel pair correction
also matches the reference. More quadratic checks can detect this particular
anisotropy; finite-moment matching does not become density identification by
that repair alone.

## 6. Capability, contribution and next action

The precise newly supported estimand is a bounded iid estimate of a specified
kernel's contribution to the scalar moment balance. Its concentration guarantee
is informative for that estimand, conditional on the sampler and fixed protocol.
The earlier blanket concern about needing an unusable density upper bound is
therefore too strong for this scalar task. Keep this positive result.

The broader proposed contribution fails: symmetry-based virial reduction, iid
concentration and moment nonidentification have immediate classical parents;
DeepParticle already studies neural/particle second moments and regularization.
This does not establish a new event-time predictor, density-distance upper bound
or full population-residual certificate. A critique of a kernel definition is
also not a Paper G thesis. Stop generic scalar-moment certificate expansion.

The unchanged truth preflight applies with these refinements:

- Assignment/interference: fixed generated law with fresh iid latent/time pairs;
  interacting particles, empirical resampling and batch-coupled generation are
  distinct experiments. No actual samples or outcomes have been accessed.
- Complete lifecycle/replay: domain, boundary, mass, μ,χ, full potential/force
  definition, δ,ℓ, time weight, fixed θ, latent law, batching, RNG and endpoint
  moment/tail contract must be pinned. Only the mathematical subset is qualified.
- Rights/ethics/release: one CC-BY-4.0 primary preprint is privately cached; no
  software/data license, participant work, outreach or publication authorized.
- Confirmation: all source reading and constructions are development. No
  untouched validation draws, partition or independently executed replication.
- Cost/stop: symbolic O(n) pair estimation, no hardware benchmark. Stop at a
  false independence premise, unaccounted selection, a substituted kernel, or
  promotion of a scalar necessary check to sufficient prediction fidelity.

A further re-entry review requires a **substantive spatial coercivity, exact
event-time/control truth asset or matched primary-model disagreement** that
removes a recorded contribution blocker. Adding another moment, an iid confidence
interval or a relabelled neural solver does not qualify. There is no candidate
harvest, new cycle, F3 audit, forecast, machine card, implementation or compute.
