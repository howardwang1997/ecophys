# Paper G: stochastic closure, memory and finite-time uncertainty

PRIVATE / INTERNAL — discovery source audit, not public evidence.
Session 4, 2026-09-10 00:54 NZST; literature read through 2026-09-09 UTC.

**Decision: no qualified re-entry trigger.** The source lane has a concrete
physical object, but the inspected papers do not establish conflicting
predictions under matched conditions. Adding noise, history, or a finite-time
ensemble diagnostic already has direct parents. No new candidate, search
cycle, forecast, experiment or machine card is created.

This continues the repository-related neural PDE scope. The link to Paper D
is coarse dynamics and physical constraints, not an inference from its
uninspected experimental outcomes. Generic measurement cycles 29–30 remain
closed; this audit does not reopen them or close the broader turbulence field.

## The apparent fork and its actual scope

The object is the conditional law of resolved shell velocities at finite
physical lead time. Distinguish uncertainty in the full initial state,
uncertainty conditional on its coarse projection, and future microscopic
forcing. They are different prediction contracts.

| Primary source and reading scope | What the comparison supports | What it does not establish |
| --- | --- | --- |
| [Freitas et al., EPL 2026](https://doi.org/10.1209/0295-5075/ae5a56), published April 22; selected final main text and [v1 Appendices C–D](https://arxiv.org/html/2602.19875v1) | In a truncated Sabra model, sustained stochastic closure improves finite-time ensemble spread relative to the tested initialization-only alternatives. The neural ablation retains the learned drift without retraining. Its written Langevin model evolves two auxiliary shells; the phenomenological comparison has correlated multiplier processes. | This is not a lower bound for all separately trained deterministic latent models at matched information and cost. “Markovian” must refer to the complete augmented state. Published findings were read, not reproduced. |
| [Domingues Lemos and Mailybaev](https://arxiv.org/html/2308.01503v1), 2023 preprint, PRE 109, 025101 (2024); selected §§III, V–VIII | Conditional mixture sampling uses shell or closure history in an intrinsic clock. Evaluation includes moments, flux distributions and transfer between cutoffs. The reported benefit of the tested history variants is mixed. | This is not a matched negative result for the 2026 fixed-initial-condition variance target. Merely replacing the density estimator or adding history is an occupied direction. |
| [Brolly, JAMES 2025](https://doi.org/10.1029/2025MS005223), published August 31; selected §§3.1, 4.1.2–4.1.3, 5 | Lorenz examples distinguish local/nonlocal and memory assumptions. Resampling frequency changes forecast skill and sampling cost; stationary and finite-time objectives can favor different settings. | This does not contradict the Sabra result: model, scale separation, conditioning and target differ. This paper is distinct from the Brolly 2026 scoring paper already in the graph. |

Additional scope checks, not additional comparison programs:

- [Mailybaev, arXiv:2510.01204v2](https://arxiv.org/pdf/2510.01204v2),
  introduction and §V.B–C only: the RG limit requires an applicable kernel
  relation and an attraction basin. Canonical regularization and physical
  viscosity are distinguished; §VI discusses extension but was not audited.
  Neither a fixed-point existence proof nor arbitrary-closure universality is
  inferred from these passages.
- [Bandak et al., arXiv:2401.13881v3](https://arxiv.org/abs/2401.13881v3),
  abstract only: the vanishing-noise rate matters, and Navier–Stokes transfer
  is conditional. No full theorem or numerical audit was performed.
- [Freeman, Giannakis and Slawinska, arXiv:2208.03390v1](https://arxiv.org/abs/2208.03390v1),
  abstract only: operator-state closure is demonstrated on Lorenz systems.
  Its abstract does not supply an opposing Sabra finite-time prediction.

Freitas 2025 solver-in-the-loop and 2026 symmetry follow-ups were bibliographic
intake only. Repository landing descriptions were encountered, but no source
code, data, checkpoints, notebook outputs or release assets were accessed.

## Exact control: two matched aggregate noise summaries are insufficient

This is a **standard paper-only covariance calculation**, not a novelty claim
or an explanation of the published Sabra results.

Let the observed scalar velocity satisfy
\(X(t)=\int_0^t F(s)\,ds\), with known \(X(0)=0\). In both alternatives,
the unobserved force is stationary, zero-mean Gaussian. Physical time, units,
observation and external initial information are fixed. Write
\(C(h)=\mathbb E[F(s+h)F(s)]\). Then

\[
V(t)=\operatorname{Var}[X(t)\mid X(0)=0]
     =2\int_0^t(t-h)C(h)\,dh.
\]

Choose positive \(v,\tau\) and

\[
C_A(h)=v e^{-|h|/\tau},\qquad
C_B(h)=v\left[\tfrac13e^{-|h|/(2\tau)}
                    +\tfrac23e^{-2|h|/\tau}\right].
\]

These are valid covariances: A is an Ornstein–Uhlenbeck force; B is a sum of
two independent stationary Ornstein–Uhlenbeck forces with component variances
\(v/3,2v/3\). Both satisfy

\[
C(0)=v,\qquad \int_0^\infty C(h)\,dh=v\tau.
\]

Thus their instantaneous variance, integral correlation time and asymptotic
variance-growth slope coincide. Their finite-time variances do not:

\[
V_A(\tau)=2e^{-1}v\tau^2,
\qquad
V_B(\tau)=\left[-1+\tfrac83e^{-1/2}+\tfrac13e^{-2}\right]v\tau^2.
\]

The coefficients are approximately 0.736 and 0.663. The null is equally
useful: if the covariance kernels agree throughout \([0,t]\), this observable
has the same variance. Conversely, where twice differentiable,
\(V''(t)=2C(t)\); exact recovery over all lead times retains the whole kernel.

Only the force correlation kernel changes. Both models continually receive
noise; this is not a deterministic-versus-stochastic comparison. Their
augmented dimensions differ, so this is not a matched-capacity bound either.
It rules out a generic finite-time law based solely on the two matched noise
summaries. No turbulent cascade, learning procedure or simulation is involved.

## What would justify further scientific escalation

A source comparison must first supply the same resolved state, physical clock,
boundary/forcing law, initial sigma-algebra and conditional target. Model
ablation is not automatically a legal intervention on the physical reference.
Fresh noise, random latent initialization and supplied observed history must
have explicit, separate information and resource accounts.

For this lane, the next useful update is a **named pair of models with
incompatible predictions for that fixed target**, or a cascade-specific
theorem that survives the covariance-kernel control above. A fitted variance
curve, extra memory, another noise schedule, or a new dataset is insufficient.
Any proposed information/memory/computational lower bound must declare
precision, latent dimension, stiffness and allowed initialization; none has
been established here.

Stop generic noise/history source expansion now. The next turn must assess a
specific residual or change the source lane, rather than open another broad
review. The unresolved scientific question is not promoted to a qualified
Paper G topic. The original publication goal remains active.

Records: `research/paper_g/stochastic_closure_scope_20260910.yaml`, the evidence
registry, route graph, re-entry ledger, daily log and long-term memory.
