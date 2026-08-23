# EcoMD new-problem selection after Q/C closure — 2026-08-22

**Closure update, 2026-08-23:** the selected partial-order card failed T0 and is RED. Correct state-dependent
semantics reduce to linearizability/reachability; finite fully observed learned-response variants collide with
PAC/robust stochastic games; decision certificates reduce to observational determinism/model checking. The
metadata gate was not opened.
See `ecomd_partial_order_event_t0_result_2026-08-23.md`. No card from this ranking is automatically promoted.

**Decision at selection time:** no candidate was GREEN. Exactly one **AMBER / T0-only** card was advanced to
the now-completed audit:

> **Resolution-certified partially ordered event dynamics:** when a market feed fixes only a partial order of
> hard, state-dependent events, compute and learn non-vacuous outcome and intervention-response sets without
> inventing a total order.

The nearest fallback is a validity certificate for gradients through hard stochastic events. A randomized
auction stopping-time experiment is the strongest empirical wildcard. Code--trajectory-anchored machine theory
of mind is the strongest NMI-shaped alternative, but it currently has a much weaker real support path and a
weaker connection to molecular dynamics.

This memo selects a question for a zero-compute reduction audit. It does **not** claim novelty, authorize data
outcomes, endorse an EcoMD checkpoint, or start a Nature-level project.

## 1. Why the search was reset

The observation-quotient and intervention-preserving coarse-graining cards are closed. Their conjunction cannot
be used as a new title. The invariant-measure, generic simulator-audit, entropy/TUR, generic learned-GLE,
hydrodynamic/universal-scaling and generic rare-event cards also remain closed or parked. On-chain intervention
searches repeatedly failed support, identity or transport gates. These failures impose four requirements on a
new question:

1. the object must exist independently of EcoMD and be externally anchored;
2. the first result must be a precise theorem, algorithm or randomized empirical estimand, not a conjunction of
   desirable properties;
3. a fully ordered or randomized ground truth must exist before any market outcome is opened;
4. EcoMD must supply a difficult computational test or a necessary capability, not synthetic evidence that the
   proposed market mechanism is real.

The repository nevertheless contains useful assets: exact state/RNG/clock continuation, asynchronous updates,
continuous-time marked-event likelihoods, queue reconstruction, chronological splits and strong provenance.
It also exposes the relevant failure. `strictify_timestamps` currently preserves vendor row order and turns tied
timestamps into an arbitrary strict clock using either `nextafter` or capped uniform increments. That is valid
only when row order itself is authoritative. The code cannot marginalize unknown within-bucket order, report an
order-induced response set, or abstain when event order changes a conclusion. Individual-order matching and
price--time priority are still unsupported.

## 2. Selection criteria

Each candidate was screened against six gates.

| Gate | Required property |
|---|---|
| Scientific object | a falsifiable object that remains meaningful without an EcoMD fit |
| Irreducibility | one exact result not reducible to standard identification, AD, process mining or simulation QA |
| Anchor | exact sequence ground truth, real randomization or code/rule-bound agent identity |
| Density | repeated units or a prospective test, not a handful of famous events |
| Transfer | at least one non-financial system with the same computational obstruction |
| EcoMD dependence | a method-dependent use of stateful interacting dynamics rather than an MD metaphor |

## 3. Ranked pool

The probabilities are planning priors for surviving a strict T0 and for assembling a complete Nature-level
evidence package from the current starting point. They are not journal acceptance rates.

| Rank | Candidate | Decision | T0 survival | Complete NCS/NMI package | Primary venue |
|---:|---|---|---:|---:|---|
| 1 | resolution-certified partially ordered market events | **AMBER; freeze T0** | 15--25% | 4--8% | NCS |
| 2 | certified gradients for hard stochastic matching events | AMBER-; comparator only | 10--20% | 3--6% | NMI/NCS |
| 3 | randomized auction stopping-time spectroscopy of liquidity memory | AMBER-; support/theory card only | 10--20% | 2--5% | NCS |
| 4 | code--trajectory-anchored market machine theory of mind | AMBER-; NMI reserve | 12--20% | 3--6% | NMI |
| 5 | certified induction of executable market mechanisms | AMBER-/RED | 8--14% | 2--4% | NMI |
| 6 | order-age Kovacs effect without randomized protocol | RED as standalone | below 10% | below 2% | NCS conditional |
| 7 | non-normal/non-reciprocal fragility, higher-body forces or grand-canonical agents | RED | below 10% | below 2% | none yet |

Only rank 1 is activated. Ranks 2--5 are collision controls and fallbacks, not parallel implementation tracks.

## 4. Selected problem: partially ordered hard-event dynamics

### 4.1 Exact object

Let an event update a stateful simulator through

\[
S_{k+1}=K_{e_k,u}(S_k,\xi_k),
\]

where the intervention or rule is $u$. In an observed time bucket $b$, the data may determine a poset
$P_b=(E_b,\prec_b)$, not a unique event sequence. Let $\mathcal L(P_b)$ be its legal linear extensions and

\[
K_{\pi,u}=K_{\pi_m,u}\circ\cdots\circ K_{\pi_1,u}.
\]

For a declared target $f$, the honest output is the order-ambiguity set

\[
\Psi_u(P_b,s)=
\left\{
\mathbb E\!\left[f(K_{\pi,u}(s,\xi))\right]:
\pi\in\mathcal L(P_b)
\right\},
\]

or a certified interval hull. An intervention contrast is formed from two such sets under externally specified
rules; it is not a latent-force counterfactual.

For two incomparable events, the scalar discrepancy

\[
\Delta^f_{e,e'}(s)=
f(K_{e'}K_e s)-f(K_eK_{e'}s)
\]

is the relevant update-operator commutator on the reachable state. This identity and the fact that all linear
extensions are connected by swaps of adjacent incomparable elements are established baselines, not proposed
contributions.

### 4.2 Why it is scientifically real

- A hard market event changes the valid state for the next event: an add, cancel and execution need not commute.
- Price--time priority makes order sequence economically consequential, while coarsened timestamps, packet
  conflation and cross-feed clocks may not preserve that sequence.
- Current market point-process work often imposes or conflates an order. State-dependent Hawkes work explicitly
  notes tied timestamp handling and the need for accurate ordering
  ([Morariu-Patrichi and Pakkanen](https://academic.oup.com/jfec/article/22/4/1098/7241580)).
- The problem has a genuine molecular-dynamics analogue. Event-driven hard-particle dynamics must detect and
  resolve collision events stably; finite precision can create invalid states whose dynamics are undefined
  ([Bannerman et al.](https://doi.org/10.1007/s40571-014-0021-8)). The transferable object is event semantics and
  certification, not a claim that orders are molecules.

### 4.3 The novelty barrier

Most attractive first statements are already occupied:

- probabilistic concurrent systems and trace monoids already model partial-order state transitions
  ([Abbes](https://arxiv.org/abs/1505.05536));
- partial-order reduction already exploits commuting transitions to preserve verified properties;
- partial-order process mining already extracts and analyses uncertain event orders
  ([survey](https://link.springer.com/article/10.1007/s10115-022-01777-3));
- partial-order resolution already learns distributions over feasible total orders and supplies approximation
  guarantees for conformance results
  ([van der Aa, Leopold and Weidlich](https://doi.org/10.1016/j.dss.2020.113347));
- interval-censored Hawkes inference already handles events observed only in bins
  ([Rizoiu et al.](https://www.jmlr.org/papers/v23/21-0917.html));
- counting linear extensions is #P-complete, is not FPT in cover-graph treewidth under standard assumptions, and
  is FPT in incomparability-graph treewidth
  ([Eiben et al.](https://doi.org/10.1007/s00453-018-0496-4));
- commutator weak-error estimates are standard in stochastic reaction-network operator splitting
  ([Hellander, Lawson and Drawert](https://doi.org/10.1016/j.jcp.2014.02.004)).

Therefore none of the following counts as novelty: timestamp jitter, random tie-breaking, enumerating all
orders, an ordinary trace-monoid representation, a generic commutator bound, an interval-censored point process,
or a standard treewidth dynamic program.

### 4.4 The only eligible residuals

T0 must produce at least one exact residual that survives reduction:

1. **Certified semantic response algorithm.** Exact or certified extremal response over partially ordered,
   state-dependent events with runtime controlled by a newly justified *semantic conflict* parameter, together
   with a matching hardness or approximation boundary. Merely parameterizing standard linear-extension counting
   by incomparability width fails.
2. **Calibrated learned response set.** A finite-sample coverage result that combines uncertainty in learned hard
   transition kernels with unknown legal event order, remains non-vacuous under declared local conflicts, and has
   a matching lower bound. A conformal wrapper or union bound over enumerated orders fails.
3. **Decision certificate with abstention.** A computable condition under which every legal order gives the same
   declared decision, plus a minimal witness set when it does not, with a result stronger than ordinary
   property-preserving partial-order reduction.

The elementary functional-commutation characterization may be proved as a sanity check but cannot make T0 pass.

### 4.5 Ground-truth ladder if T0 passes

The empirical design must begin with dual-resolution truth, not a coarse feed alone:

1. an order-level source with authoritative sequence or packet identifiers;
2. a deterministic coarsening operator that removes selected order information while preserving event content;
3. a genuinely coarse, independently produced market feed;
4. a chain or exchange log with canonical within-block or within-engine order;
5. an external event system, such as a chemical reaction network or distributed trace, with the same exact-to-
   coarsened construction.

The first test is coverage of the hidden full-order output after deliberate coarsening. Only after that may a
rule change such as timestamp precision, continuous-to-batch execution or sequencer ordering be considered. A
single LOBSTER row order is not an uncertain-order dataset; it is useful as exact sequence ground truth that can
be coarsened under a frozen operator.

### 4.6 EcoMD's role

EcoMD would enter only after T0 and source qualification. The project would need an event-driven matching shell
with persistent orders and externally specified priority. EcoMD's stateful latent dynamics could then generate
agent intentions between hard events, while the selected method propagates event-order uncertainty through the
matching layer. The current aggregate adapter is not sufficient and must not be presented as validation.

### 4.7 Kill rules

Close the card immediately if any condition holds:

- every theorem reduces to trace equivalence, standard partial-order reduction, process-log resolution,
  operator splitting or known linear-extension algorithms;
- the proposed complexity advantage disappears when compared at the correct incomparability/conflict width;
- coverage requires enumerating all linear extensions or an unknown order law;
- certified intervals are close to the full output range at realistic metadata-only batch widths;
- no source provides both an authoritative sequence and a defensible coarsening contract;
- only synthetic EcoMD events support the result;
- the result changes under arbitrary grouping of a single marketable order's split executions.

## 5. Comparator: gradients through hard stochastic matching

The second problem asks when a backward gradient is the derivative of the exact hard-forward objective rather
than of a soft surrogate. A possible certificate would combine exact pathwise/saltation terms far from event
ties with stochastic boundary corrections near priority changes, and return a budget-dependent error bound.

The novelty risk is higher than the headline suggests. Unbiased automatic differentiation for programs with
discrete randomness is already available
([Arya et al., NeurIPS 2022](https://proceedings.neurips.cc/paper_files/paper/2022/hash/43d8e5fc816c692f342493331d5e98fc-Abstract-Conference.html));
differentiable discrete-event queue control already uses a hard forward path and smooth backward approximation
([Che, Dong and Namkoong](https://arxiv.org/abs/2409.03740)); hybrid-event derivatives use saltation matrices;
and exact CTMC forward simulation has already been paired with massively parallel surrogate backward gradients
([Vilar and Saiz](https://arxiv.org/abs/2602.19775)). Queueing perturbation analysis and weak derivatives are
also decades old.

This card remains a T0 comparator only. It can advance later only with a computable, non-asymptotic bias/variance
certificate whose cost is strictly better than general stochastic AD on a declared class of matching programs.

## 6. Empirical wildcard: randomized auction stopping-time spectroscopy

A more empirical route uses the realized random end of a call auction as a repeated stopping-time intervention.
The question is whether extra randomized accumulation time changes the post-uncrossing relaxation distribution,
conditional on the state before the random window, and whether an age-resolved event simulator predicts that
dose response out of venue.

This is a better protocol than an observational claim that “old orders matter.” Random endings are deployed in
real exchanges: Xetra's call phase has a random end
([market model](https://www.xetra.com/resource/blob/4075548/7e88c74e94df979cc54400511fe5e0d9/data/T7_Release_13.0_-_Market_Model%20_Xetra.pdf)),
and Hong Kong's revamped closing auction randomized the end between 16:08 and 16:10. However, the broad effects
of introducing random auction endings on manipulation and price efficiency are already studied
([Lin, Michayluk and Zou](https://doi.org/10.1142/S2010139224500010)); auction frequency, pre-auction dynamics and
closing-price design also have a large literature.

The narrow possible residual is *within-rule realized stopping time as randomized relaxation spectroscopy*, not
“random endings improve markets.” It is killed if the realized stopping time or full auction book is unavailable,
if rule-triggered extensions contaminate the declared random component, if prior work already estimates the same
within-window dose response, or if only one venue supports the protocol. This card authorizes a later
rules/schema/availability audit only after the selected T0 is resolved; it does not authorize auction outcomes.

## 7. NMI reserve: code--trajectory-anchored market theory of mind

The strongest NMI-shaped question is to learn a strategy representation from a versioned agent program plus its
execution traces and predict the same agent in an unseen market mechanism. Entire agent-by-mechanism cells and a
future code upgrade would be held out. This avoids pretending to identify strategies from anonymous aggregate
flow.

It faces close work on behavior-only machine theory of mind
([Rabinowitz et al.](https://proceedings.mlr.press/v80/rabinowitz18a.html)), policy-source conditioning
([Lin et al.](https://arxiv.org/abs/2512.21024)) and executable code world models
([PatchWorld](https://arxiv.org/abs/2605.30880)). The public agent-by-mechanism matrix is also likely sparse, as
the project's earlier on-chain identity audits repeatedly showed. Without at least 50 externally anchored agents,
three mechanism families and real cross-mechanism cells, this remains RED. It is not the active EcoMD route.

## 8. T0 execution order

The machine-readable freeze is `configs/empirical_physics/ecomd_partial_order_event_t0_v1.yaml`; the full gate is
`papers/proposal/ecomd_partial_order_event_t0_freeze_2026-08-22.md`.

1. Build a 40-plus-primary-work reduction matrix before writing code.
2. Solve add/cancel/execute toy queues and label all standard trace/commutator facts as baselines.
3. Attempt the exact algorithmic, statistical and decision-certificate exits.
4. Only if one mathematical exit survives, inspect source documentation, schemas, licences and event identity
   semantics without reading market outcomes.
5. Make a fail-closed decision. Do not merge the selected card with hard-event gradients to rescue a failure.

Until that decision, market outcomes, paid/bulk data, EcoMD training, benchmark implementation and GPUs remain
locked.
