# Paper G: singularity event-time truth preflight

**PRIVATE / INTERNAL — development infrastructure; public_evidence_eligible: false.**
Started 2026-09-10 02:12 NZST (2026-09-09T14:12:44Z). This follows the
[kernel-certificate scope audit](ecomd_paper_g_ks_kernel_certificate_scope_2026-09-10.md).
The persistent objective remains a substantial, novel Paper G related to the
repository's experiments, suitable for ICML main / NMI / NCS after validation.

**Decision: partial_capability.** A published enclosure supplies a concrete
initial-value event-time reference. It does not remove the recorded direct-prior
blocker, establish a new contribution, or authorize candidate harvesting.
This is a truth-asset preflight, not another topic cycle. No forecast is made.

## What has become testable

[Mizuguchi et al.](https://link.springer.com/article/10.1007/s13160-022-00545-8)
report a computer-assisted enclosure for the following fixed problem:

\[
u_t=u_{xx}+u^2,\quad x\in(0,1),\quad u(t,0)=u(t,1)=0,
\qquad u(0,x)=\frac{192}{5}x(x-1)(x^2-x-1).
\]

The solution is positive inside the domain, so the article's nonlinearity
\(|u|u\) agrees with \(u^2\). The target is divergence of the continuum
\(L^2(0,1)\) norm, with reported physical time

\[
T^*\in(0.3068,\;0.317713].
\]

The lower endpoint comes from verified existence; the upper endpoint uses an
energy inequality and verified solution bounds. Theorem 1, Section 3.1 and
Appendix A were checked. The stated function class includes continuous
\(H^1_0\) evolution, interior-time \(C^1(L^2)\), and continuous evolution in the
Dirichlet Laplacian domain. The article appeared online in November 2022,
in volume 40 (2023). This is an externally reported reference, not a computation
reproduced here. Only this fixture is qualified in the present record.

This reference supports exclusion: a prediction incompatible with the interval
is falsified under the matched contract. A point inside it is merely compatible.
Its midpoint is not exact truth. A proposed interval overlapping it does not
thereby have proven coverage. Future tolerances must account for reference width.
The published example is already development-visible and cannot be relabelled
untouched confirmation.

## Paper-only certificate interface

The following is a specialization of an existing energy-comparison argument,
not a new theorem. For a regular positive solution of the fixed problem, put

\[
y(t)=\|u(t)\|_2^2,\qquad
E(u)=\tfrac12\|u_x\|_2^2-\tfrac13\|u\|_3^3.
\]

Integration by parts and the energy dissipation identity give

\[
E'(u(t))=-\|u_t\|_2^2,\qquad
y'(t)=-4E(u(t))+\tfrac23\|u(t)\|_3^3.
\]

Since the domain has unit measure, \(\|u\|_3^3\ge y^{3/2}\).
Suppose a separate verifier has established existence through \(t_i\),
\(y(t_i)\ge y_->0\), and \(E(u(t_i))\le E_+\). If
\(y_-^{3/2}>6E_+\), the increasing scalar comparison field stays positive and

\[
T^*\le t_i+\int_{y_-}^{\infty}
\frac{ds}{-4E_++\frac23s^{3/2}}.
\]

For example, a certified \(L^2\) error radius \(\rho_2\) around an approximate
field gives \(y_-=(\|\hat u\|_2-\rho_2)^2\) only when
\(\|\hat u\|_2>\rho_2\). The energy bound additionally needs spatial-derivative
and nonlinear-norm control. A collocation loss or sampled scalar moment does not
supply those bounds or the existence certificate. The integral, norm bounds and
floating-point errors would all need rigorous enclosure in any implementation.
No such implementation or numerical evaluation was performed.

This shows exactly where a future neural approximation could enter a classical
verifier. Merely replacing its approximate field by a neural network leaves the
certificate principle within direct prior work. Any claimed advantage must
survive comparison with the original verifier and include verification cost.

## Profile, physical clock, and initial state are different objects

[Kavousanakis et al.](https://www.nature.com/articles/s41467-026-75936-3)
combine symmetry reduction and PINNs; their 2026 final article includes a
stationary gKdV blow-up profile and a learned rescaling rate. Generic neural
pinning, moving coordinates and self-similar profile learning already have
direct parents. Selected final-article case studies and reconstruction discussion
were read. Its data/code availability statement was inspected, but no repository,
warm-start files, source code or outputs were opened.

Here is a standard clock calculation, derived from the gKdV scaling rather than
claimed as a source theorem. With

\[
u=A^{-2/(p-1)}w(x/A+K,\tau),\qquad G=A_\tau/A,
\]

normalizing the third spatial derivative to coefficient one requires
\(dt/d\tau=A^3\). Thus a positive width following the actual transformed
trajectory has remaining physical time

\[
T^*-t(\tau_0)=\int_{\tau_0}^{\infty}A(s)^3\,ds,
\]

provided the transformed solution persists, this limit is the relevant
singularity, and its singular behavior has been established. For constant
\(G=-g<0\), the integral is \(A(\tau_0)^3/(3g)\). Matching a normalized
profile and rate does not freeze the physical width or the initial-value match.

More generally, if a theorem certifies
\(0<g_{\min}\le-G(s)\le g_{\max}\) for **all** \(s\ge\tau_0\), then
exponential comparison yields

\[
\frac{A(\tau_0)^3}{3g_{\max}}
\le \int_{\tau_0}^{\infty}A(s)^3ds
\le \frac{A(\tau_0)^3}{3g_{\min}}.
\]

Certified width and accumulated-clock intervals must also be propagated. This
elementary bound does not establish its own all-future hypotheses. A finite
training window cannot certify them by inspection. We have not constructed two
different exact solutions of the same well-posed initial-value problem: this is
a certificate-scope distinction, not a violation of uniqueness. The gKdV clock
is not transferred to the Fujita equation or Keller–Segel.

## Exact scaling controls are useful, but not independent replication

The Fujita equation admits the following paper-only parabolic scaling. For any
\(\lambda>0\), define

\[
u_\lambda(t,x)=\lambda^2u(\lambda^2t,\lambda x),
\qquad x\in(0,1/\lambda).
\]

Both \(\partial_tu_\lambda\), \(\partial_{xx}u_\lambda\) and
\(u_\lambda^2\) acquire the factor \(\lambda^4\). The boundary and initial
data transform too, and \(\|u_\lambda(t)\|_2^2=\lambda^3\|u(\lambda^2t)\|_2^2\).
Consequently the inherited event enclosure is

\[
T_\lambda^*\in(0.3068/\lambda^2,\;0.317713/\lambda^2].
\]

These are exact covariance checks and descendants of one truth fixture.
They are not independent systems or unseen event labels. Changing only the
amplitude while holding the domain and profile coordinates fixed does not
justify this time law. All scaling descendants must remain in the same data
partition as their parent.

## Adjacent sources do not supply the same event contract

- [Takayasu et al.](https://link.springer.com/article/10.1007/s00211-022-01291-2):
  selected introduction and theorem statements concern periodic heat evolution
  in complex time. Their branching region and global complex-ray evolution do
  not provide the same real-time Dirichlet event interval. The article itself
  distinguishes a conditional real-axis localization from its proved result.
- [Wang et al., arXiv v3](https://arxiv.org/abs/2201.06780v3): abstract/metadata
  only; neural Euler/Boussinesq profile work is a direct broad-method parent.
  No full proof or specified-initial-value time enclosure was audited here.
- [Chen–Hou, arXiv v3](https://arxiv.org/abs/2305.05660v3): abstract/metadata
  only; the boundary-setting stability and rigorous-numerics work cannot be
  substituted for a free-space or Fujita initial-value truth contract.

An author announcement dated 2026-09-07 about unforced Euler on whole space was
read as a lead only. Its manuscript was not inspected and no proof, theorem
disagreement or new truth capability is inferred from the announcement.
Search-only adjacent abstracts were not promoted to read-work evidence.

## Truth-asset contract and disposition

| Component | Frozen scope or unresolved requirement |
|---|---|
| Estimand | Continuum \(L^2\) event time of the specified positive Dirichlet Fujita solution, physical coefficients and clock fixed |
| Assignment / interference | No intervention executed; any future initial-data family must be fixed before outputs; scaling descendants share a parent partition |
| Lifecycle / replay | Equation, domain, boundary, complete initial field, regularity, norm, clock, existence slabs, verifier precision, residual/energy bounds and interval endpoints |
| Rights / release | Public article reading only; article access does not grant source/data rights; no redistribution or public artifact authorized |
| Confirmation | Current published fixture is development-visible; no untouched confirmation family exists in this record |
| Independent replication | No independent verifier run; a second mesh, transformed copy or point prediction is not automatically independent truth |
| Cost | Published method requires validated numerics; neural training plus certification cost unmeasured; no compute allocation |
| Stop rules | No midpoint-as-truth, profile-as-proof, finite-window-as-global, norm/domain/clock substitution, or scaling-as-replication; stop generic wrapper claims |

The fixed event interval is a stronger truth asset than a virial upper time
bound, but its scope is narrow and the verification method already exists.
No matched disagreement between primary models was found in the selected
reading. The existing route's failure codes and status remain unchanged.

Next useful update: identify a specific **existing** stability/verification
theorem that can certify the physical-clock tail and initial-data connection,
or a new independent event-truth family with a contribution-relevant capability.
Audit its exact hypotheses before a re-entry decision. Do not perform a third
generic certificate cycle or open a full fifteen-work review on the strength
of this reference alone.

No scientific implementation, simulation, arrays, checkpoints, notebooks,
GPU/SSH, participants, outreach, purchase, publication, commit or push occurred.
Bookkeeping validation checks records, not scientific novelty or the external
computer-assisted proof. The Paper G goal remains active and unachieved.
