# Paper G: emulator-superiority primary-disagreement audit

**PRIVATE / INTERNAL — exploratory selection record, not public research evidence.**
Session started 2026-09-09T08:19:37Z; literature cutoff 2026-09-09.
Written after interleaved reading and algebra, with no prospective forecast.

The proposed re-entry is **not_trigger**. A direct NeurIPS main-conference parent
already studies trained emulators exceeding their numerical teachers. The
inspected apparently opposing papers do not supply opposite predictions under
the same comparison contract. The existing cycle30 formulation remains closed;
this audit strengthens its prior-work boundary without closing the entire field.

## Direct collision and scope correction

Koehler and Thuerey's [Neural Emulator Superiority](https://arxiv.org/html/2510.23111v2)
defines teacher-relative superiority in section 2.3. Sections 3–4 distinguish
state-distribution transfer from autoregressive improvement. Appendix B.1
includes advection experiments with the same initial-condition law for training
and testing, one-step training, longer rollouts and analytical reference truth.
The Burgers comparison in section 4.2 uses a more converged discrete reference;
it is not thereby a continuum-error certificate. Section 5 explicitly limits
the result to particular regimes and identifies moderate teacher fidelity as
future work. The [official proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/f200119a40846e508954abcd61f5f3fd-Abstract-Conference.html)
confirm NeurIPS 2025 Main Conference, volume 38.

Consequently, neither trained-model existence, spectral inductive-bias examples,
nor the general warning about evaluating against a numerical teacher can be
claimed as a new Paper G contribution. Earlier local statements that prevalence
is unresolved must be read as referring to the repository's particular models,
data and a broader independently specified population. Published existence in
other setups is established by this source; it was not reproduced here.

## Same-comparison audit

A disagreement must match the physical input law, PDE and full state,
label-generating scheme, model information, fitting rule, reference truth,
observation, error functional, horizon and cost accounting. Merely sharing an
equation name or opposite titles is insufficient.

| Inspected work | Actual comparison and information | Re-entry verdict |
| --- | --- | --- |
| Neural Emulator Superiority, v2, sections 2–5 and B.1 | Learned rollout versus its label generator, both scored against a separately specified reference | Direct parent; regime-dependent existence, not a universal claim |
| [DeepFDM](https://arxiv.org/html/2507.21269v1), sections 3.1, 7, 9 and 9.4 | Learned coefficient-based finite differences versus FNO/U-Net/ResNet on benchmark or projected high-resolution solver data; includes varying coefficients and input distributions | Different competing methods and reference contract; no matched negative test of teacher-relative superiority |
| [CHONKNORIS](https://arxiv.org/html/2511.19980v1), sections 2.2–2.3, 3.1 and 3.2 | Learned approximate inverse inside known-residual iterations; finite-difference experiments compare with a numerical Newton–Kantorovich reference | Additional equation information and a discrete target; machine precision here does not certify continuum machine precision |
| [Predicting Change, Not States](https://arxiv.org/html/2412.13074v2), sections 3, 4.1 and 5.2 | Derivatives estimated from trajectory labels, followed by a chosen ODE integrator, versus state prediction | Changes fitting target and rollout procedure; no matched assertion that the teacher is a universal accuracy floor |

DeepFDM's section 9.4 explanation in terms of FNO bias is the authors'
interpretation; this audit does not promote it to a universal impossibility for
variable-coefficient operator learning. Likewise, a derivative-target gain need
not require extra high-fidelity labels: changed processing of existing labels
already changes the learning contract. Count inference evaluations and residual
access explicitly rather than treating every method as one equivalent call.

The unidentified TMLR search hit, PEDS, neural caches, APEBench and the recent
Koehler thesis were intake leads only. No source-specific conclusion or new
evidence record is based on their search snippets. This was a bounded
four-work comparison, not a fifteen-work hostile audit or new question harvest.

## Two elementary controls against overclosing

These are paper-only deductions, not novel theorems or trained-model evidence.

**Projection can improve or worsen continuum accuracy under the same input law.**
Let H=L2(mu;Y), with square-integrable continuum target u and deterministic
teacher v=u+delta. For a closed linear hypothesis subspace M and orthogonal
projection P, the population squared-loss optimizer is f*=P v. Orthogonality gives

    ||f*-u||^2 = ||(I-P)u||^2 + ||P delta||^2,
    ||f*-u||^2 - ||v-u||^2 = ||(I-P)u||^2 - ||(I-P)delta||^2.

Thus teacher superiority is not a general lower bound even without changing mu.
If u lies in M, discarded teacher error can help. If the omitted true signal is
larger, it hurts. In R2 with M=span(e1), u=e1 and delta=b e2 yield improvement;
u=e2 and delta=epsilon e1 yield degradation. M=H gives equality. This is ordinary
approximation theory, not a prediction for a trained nonlinear architecture,
finite samples, optimization or long rollouts. Conditional-mean-zero random
label noise is a separate statistical setting from deterministic solver bias.

**Equal initial laws do not establish equal rollout-state coverage.**
For a deterministic teacher T, if F(y)=T(y) on every teacher state reachable from
the initial support through horizon n, then induction gives F^t(x)=T^t(x) for
all t<=n. There is no strict teacher-relative improvement on this exact-fit
control. Zero population loss on initial states alone does not supply that
premise. With a uniform defect at teacher-reachable states bounded by eta and
F Lipschitz with constant L on a region containing both trajectories,

    ||F^t(x)-T^t(x)|| <= eta * sum_(j=0)^(t-1) L^j.

Proof: add and subtract F(T^t(x)) at the next step, then iterate the resulting
recursion. Small average one-step training loss alone supplies neither uniform
eta nor L. This control explains compatible statements; it does not invalidate
the cited empirical result or assume a distribution shift was hidden by its authors.

## Decision, repository bridge and next decisive update

The repository connection remains Paper D's neural-PDE prediction and resolution
transfer source/config contracts. This audit does not show teacher-relative
superiority, a ranking reversal or a source-fidelity problem in Paper D. Its
existing evidence roles remain unchanged. Known advection truth in another
paper does not recover the historical PDEBench continuous initial states.

Add the direct-prior blocker
`emulator_superiority_and_benchmark_fidelity_have_direct_neurips_prior` to the
existing terminal node, with this formal audit and its machine-readable record.
No recorded blocker is removed; no candidate harvest is authorized. The two
no-card cycles still preclude a third relabelled neural-PDE measurement cycle.

A next re-entry review needs a named, versioned pair of primary claims that
disagree on one fully matched target, or an independently qualified truth/control
asset and a distinct contribution beyond this direct parent and the earlier
reference-error accounting. Repeating the existence result on another PDE,
listing moderate-fidelity experiments from the prior's outlook, or changing
the score is not by itself a trigger. An exact-fit control is useful but not a
new scientific program. No broad empirical null or publication probability is
inferred from this audit.

No scientific implementation, simulation, raw outcomes, checkpoints, notebook
outputs, GPU work, outreach, purchase, participants or publication was involved.
The broader Paper G objective remains active.
