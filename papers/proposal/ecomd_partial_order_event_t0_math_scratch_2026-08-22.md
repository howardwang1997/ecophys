# Partially ordered hard-event dynamics — T0 mathematical reduction

**Started:** 2026-08-22

**Closed:** 2026-08-23

**Scope:** finite symbolic systems only; no market outcome, benchmark, fitting or GPU

**Verdict:** FAIL/RED; no E1--E3 result escaped the reductions below

## 1. Correct object: legal schedules, not all linear extensions

Let (P=(E,\prec)) be the externally declared event poset. For a recorded history, write an event block as
(e=(\mathrm{id},\mathrm{op},\mathrm{arg},\mathrm{ret})). Let the sequential specification be a partial transition
function

\[
\bar\delta:S\times\mathrm{Op}\times\mathrm{Arg}\rightharpoonup S\times Y.
\]

Define (\delta(s,e)=(s',y)) only when
(\bar\delta(s,\mathrm{op}_e,\mathrm{arg}_e)=(s',y)) and (y=\mathrm{ret}_e). Thus recorded acknowledgements,
rejects and fill tapes must match the sequential specification rather than being silently regenerated. For a
generative event with no recorded return, the last equality is omitted and (y) becomes part of the generated
response. For an initial state (s_0), the relevant complete-schedule set is

\[
\mathcal V(P,s_0)=\left\{
  \pi=(e_1,\ldots,e_m)\in\mathcal L(P):
  \delta(s_{j-1},e_j)\downarrow\text{ for every }j
\right\}.
\]

Thus (mathcal V(P,s_0)) can be a strict subset of (mathcal L(P)). State-dependent enabledness cannot be
added after enumerating a static poset; it is part of the sequential specification.

For deterministic updates this filtered set is enough. For a stochastic kernel, however, enabledness can depend
on the realized state and noise, so the causal relation between order and trajectory must be declared. There are
at least two different estimands.

For an **open-loop order**, (\pi) or an order law is selected before execution and independently of future
noise. One can restrict to permutations that complete almost surely,

\[
\Psi_u^{\mathrm{open}}(P,s_0)=\left\{
  \mathbb E[f(S_m,Y_{1:m})\mid \pi,u]:
  \pi\in\mathcal L(P),\ \Pr_{\pi,u}(D_m=E)=1
\right\},
\]

or retain every (\pi) by adding an explicit absorbing failure outcome (\bot) and defining (f) on it. Pathwise
filtering does not turn an exogenous order into feedback control.

For a **feedback order**, use this stronger object only if the ordering mechanism can observe the realized
history and adapt. Let (H_j=(e_{1:j},Y_{1:j},O(S_{0:j}))) and
(\mathcal F_j=\sigma(H_j)). A randomized non-anticipating scheduler (\gamma_j) is
(\mathcal F_j)-measurable. Conditional on (H_j), it may assign mass only to unprocessed, precedence-available
blocks that are admissible almost surely under the corresponding conditional state law. If the full state is
public, declare (O(S)=S); otherwise the policy acts on the observable history or belief state, not an undeclared
latent state. Let (\Gamma_{\mathrm{as}}(P,s_0)) contain feedback policies that reach completion (D=E) almost
surely. Its response set is

\[
\Psi_u(P,s_0)=\left\{
  \mathbb E[f(S_m,Y_{1:m})\mid \gamma,u]:\gamma\in\Gamma_{\mathrm{as}}(P,s_0)
\right\}.
\]

The frozen memo is not wrong merely because it uses a fixed (\pi); it is incomplete because it calls every
linear extension legal without declaring open-loop versus feedback information, pathwise failure, completion or
recorded-return consistency. Its formula is valid as the almost-surely completing open-loop object when every
included order remains admissible on every realization. Using (\Gamma_{\mathrm{as}}) without causal support
would instead enlarge external order uncertainty into a feedback controller. Totalizing an invalid transition
as a reject or no-op also does not repair a recorded-history semantics: it replaces an event reported by the feed
as completed with a rejection.

## 2. Finite price--time queue semantics

Use a one-sided ask book. At each price, the state stores a FIFO list of pairs ((i,q_i)), with persistent order
identity (i) and positive integer residual quantity (q_i). Lower prices have priority. The event families are:

- (A(i,p,q)): add a previously absent identity to the tail at price (p);
- (C(i,r)): cancel exactly (r\le q_i), with equality giving a full cancel;
- (C^*(i)): cancel the full current residual quantity;
- (T(i,r)): report an execution of (r\le q_i) against (i), enabled only when (i) is the current
  price--time head;
- (M(r)): one atomic marketable buy that consumes (r) units in price--time order and emits its ordered fill
  tape.

Every transition records the affected identity, pre/post residual quantity and fill tape. Treating a rejected
operation as an unlabelled no-op would erase exactly the semantic distinction under audit, so rejection is an
explicit output rather than silent acceptance.

## 3. Four mandatory cases

### Case 1 — disjoint resources commute

Initial book: (A@100:q=2), (B@101:q=2). Let (e=C(A,1)) and (e'=C(B,1)). Both orders are enabled and

\[
\delta_{e'}\delta_e(s_0)=\delta_e\delta_{e'}(s_0)
  =\{A@100:q=1,\ B@101:q=1\}.
\]

The fills and acknowledgements also agree. This is ordinary semantic independence.

### Case 2 — cancel/execute enabledness is state dependent

Initial book: (A@100:q=2). Let (e=C^*(A)) and (e'=T(A,1)). Both are enabled at (s_0), but

- (T(A,1);C^*(A)) is legal and leaves no (A), with one unit filled;
- (C^*(A);T(A,1)) is illegal because (A) no longer exists.

Consequently, declaring (e) and (e') incomparable does not authorize both static linear extensions. The
poset must be repaired from lifecycle metadata, or the sequential specification must reject the invalid prefix.

### Case 3 — add/aggressive execution changes the filled identity

Initial book: (A@101:q=1). Let (e=A(B,100,1)) and (e'=M(1)). Both orders are legal:

| schedule | fill tape | terminal book |
|---|---|---|
| (e;e') | (B) | (A@101:q=1) |
| (e';e) | (A) | (B@100:q=1) |

For (f=\mathbf 1\{B\text{ is filled}\}), the two answers are 1 and 0. A row-order-preserving timestamp jitter
returns only one of them and therefore contradicts the other legal schedule. This is the required sanity check,
not a new theorem.

### Case 4 — split executions from one aggressor must be atomic

Initial book: (A@100:q=1), (B@101:q=1). Let (G=M(2)) be a generative macro-event with no recorded fill return;
its internal execution can be transported as two child messages. A concurrent event is (e=A(C,99,1)).

The only macro-event schedules are:

| schedule | ordered fill tape | terminal book |
|---|---|---|
| (G;e) | ((A,B)) | (C@99:q=1) |
| (e;G) | ((C,A)) | (B@101:q=1) |

Because this toy is generative, both macro placements above are admissible counterfactual executions. If the two
children of (G) are incorrectly replaced by generic market-consumption kernels
(M(1),M(1)), the interleaving `M(1); add C; M(1)` produces the third tape ((A,C)). No placement of the atomic
marketable order produces that tape.

An identity-bearing recorded feed is a different observation contract. If its children record fills ((A,B)),
the grouped macro-event has recorded return ((A,B)); return consistency then accepts only the placement that
emits ((A,B)), not the alternative ((C,A)). If those rows are nevertheless split as targeted transitions
(T(A,1),T(B,1)), the interleaving above is rejected: after adding the better-priced (C), execution of (B) is no
longer enabled. The false generative tape and the recorded-history deadlock are distinct consequences of an
incorrect split; they must not be combined into one estimand. Atomic grouping is part of either observation
contract, not a modelling preference.

A flat poset cannot express this atomicity while retaining both possible placements of the group. Write the two
internal fills as (x<y) and the external event as (z). To permit both (zxy) and (xyz), (z) can be ordered
neither before (x) nor after (y); then the same poset necessarily permits (xzy). The input must collapse
((x,y)) to one macro-event or use a richer hierarchical/event-structure semantics. Adding ordinary precedence
edges is insufficient.

## 4. Frozen elementary reductions

For two everywhere-enabled incomparable events (e,e'), the order effect is exactly

\[
\Delta^f_{e,e'}(s)=f(K_{e'}K_es)-f(K_eK_{e'}s).
\]

For the full set (mathcal L(P)), any two linear extensions are connected by adjacent swaps of incomparable
events. Hence pairwise property-preserving commutation on every reachable swap proves invariance. This is the
standard trace/commutator argument.

The qualification matters: the graph induced by (mathcal V(P,s_0)) need not remain connected under legal
adjacent swaps. A partial sequential specification can accept two schedules while every intermediate adjacent
swap is rejected. Therefore a certificate based only on locally swappable valid schedules is incomplete;
ordinary state-space reachability, linearizability checking or confluence analysis supplies the correct global
object.

## 5. Exact configuration-graph reduction

Let a finite observer have initial state (q_0), update
(q'=U(q,e,y,s')) and accepting payoff (r(s,q)); this retains any path-dependent quantity in
(f(S_m,Y_{1:m})). Construct an acyclic graph (G_{P,s_0,q_0}). A vertex is ((D,s,q)), where
(D\subseteq E) is a down-set of completed events, (s) is the resulting system state and (q) is the observer
state. From ((D,s,q)), add an edge labelled ((e,y)) to ((D\cup\{e\},s',q')) exactly when

1. every predecessor of (e) is in (D); and
2. (\delta(s,e)=(s',y)) is defined, including any recorded-return match; and
3. (q'=U(q,e,y,s')).

Only vertices with (D=E) are accepting. A sink with (D\ne E) is a non-accepting deadlock, as in Case 2, not a
legal complete schedule. Every root-to-accepting path is a member of (\mathcal V(P,s_0)), and every member gives
one path. Define the reachable-payoff set by the ordinary DAG recurrence

\[
\mathcal R(D,s,q)=
\begin{cases}
\{r(s,q)\}, & D=E,\\
\displaystyle\bigcup_{e\in A(D,s)}\mathcal R(D\cup\{e\},s_e,q_e), & D\ne E,
\end{cases}
\]

where an empty union is the empty set. Feasibility is non-emptiness of (\mathcal R), and min/max are taken only
over a non-empty reachable-payoff set. This prevents a deadlocked prefix from being mistaken for a response.

The graph can be exponential; memoizing equal states and quotienting commuting transitions are precisely
state-space search and partial-order reduction.

There is also a direct semantic reduction. Take a complete concurrent history, let (P) be its real-time
precedence relation, encode each completed operation as (e=(\mathrm{op},\mathrm{arg},\mathrm{ret})), and let
(\bar\delta) be the sequential ADT specification. The admissibility rule above requires every emitted return to
equal the recorded return. Then

\[
\mathcal V(P,s_0)\ne\varnothing
\quad\Longleftrightarrow\quad
\text{the history is linearizable}.
\]

This is exact on the linearizability-history subclass. More general feed precedence constraints give the same
language-reachability problem with an enriched happens-before relation. Queue and priority-queue histories are
not analogies: they are the sequential specifications used by the nearest algorithms.

## 6. E1 audit — semantic-conflict algorithm

Three attempted formulations all reduce:

1. **Existence:** whether a legal order exists is history linearizability/language reachability.
2. **Extremum:** attach the accepting functional through observer state (q) and solve min/max reachability on
   (G_{P,s_0,q_0}).
3. **Representative exploration:** quotient executions by state-dependent independence, which is dynamic
   partial-order reduction.

General single-history checking is NP-complete. More importantly for the frozen residual, 2026 work already
gives fixed-parameter linearizability monitors for queues and priority queues, parameterized by the number of
processes (k), and current trace/DPOR work supplies exact hardness, approximation and sampling
boundaries. No different semantic-conflict parameter, algorithm and matching lower bound was derived here.

There is a direct price--time embedding of linear-extension counting. Given any poset (P), start from an empty
book and create one unit add (A_i) per element, all at the same price, with the precedence edges of (P). Every
add is enabled, and the accepting FIFO identity sequence is exactly the chosen linear extension. Therefore

\[
\#\{\text{distinct accepting FIFO states}\}=\#\mathcal L(P),
\]

so counting distinct responses is (\#P)-hard even on this arbitrary-poset, add-only, injective subclass. This
does not assert that the general distinct-output problem, where many schedules may collide, belongs to (\#P),
nor does it establish the same lower bound for interval-order inputs.

**E1 verdict: FAIL/RED.** The available recurrence is ordinary reachability/POR, and the nearest queue-specific
parameterized boundary is already occupied.

## 7. E2 audit — learned calibrated response set

Under a finite, fully observed Markov model and an explicitly specified uncertainty-game semantics, choosing an
available event can be represented as a scheduler action and the learned (K_{e,u}) as a stochastic transition
kernel. Extremal responses can then be encoded as robust value problems. This is a nearest-work reduction only
after declaring who selects the uncertain kernel and when. A joint confidence region can be non-rectangular;
replacing it by independently varying transition intervals gives an ordinary rectangular robust MDP but may
strictly overapproximate the intended response set. PAC statistical model checking already handles unknown
transition probabilities together with nondeterministic MDP/game choices, and robust concurrent stochastic-game
verification handles interval transition uncertainty explicitly. The underspecified frozen object itself does
not justify a stronger exact equivalence.

There is also a distribution-free obstruction. Suppose two admissible data-generating systems (M_0,M_1)
induce the same observed-data law (Q), but their target responses are (\theta_0,\theta_1), with
(d=|\theta_1-\theta_0|>0). Any random set (C(X)) satisfying

\[
\Pr_{M_i}\{\theta_i\in C(X)\}\ge 1-\alpha,\qquad i\in\{0,1\},
\]

must, under their common law, satisfy

\[
Q\{\theta_0,\theta_1\in C(X)\}\ge 1-2\alpha.
\]

Hence (\operatorname{diam}C(X)\ge d) with probability at least (1-2\alpha). More samples cannot remove
unobserved order ambiguity unless an order law, extra metadata or response invariance is assumed. This is the
standard two-point/partial-identification argument, not a new matching rate.

For the often-invoked “unvisited transition” version, let (U) have probability (q) under both models and suppose
the conditional observed-data laws agree on (U). Marginal (1-\alpha) coverage under each model implies

\[
\Pr\!\left(U\cap\{\theta_0,\theta_1\in C(X)\}\right)\ge q-2\alpha,
\qquad
\Pr\!\left(\theta_0,\theta_1\in C(X)\mid U\right)\ge 1-\frac{2\alpha}{q}.
\]

The second display is a consequence of marginal coverage plus conditional observational equivalence; it is not
an assumption of conditional coverage. The bound is non-vacuous only when (q>2\alpha).

**E2 verdict: FAIL/RED.** Under the declared finite Markov/uncertainty semantics, the construction has close
robust-model-checking baselines, but exact calibrated-set equivalence still depends on the uncertainty and
coverage semantics; without those declarations the frozen target is underspecified. Without new identifying
structure, the set cannot shrink below the separation of an observationally indistinguishable pair established
above. The bound does not claim that it must contain the entire identified range with high probability.

## 8. E3 audit — abstaining decision certificate

Let (g) be the declared accepting decision. The certificate asks whether

\[
\left|\{g(s,q):(E,s,q)\text{ is reachable in }G_{P,s_0,q_0}\}\right|=1.
\]

This finite-instance test is self-composed product reachability/observable determinism. If two labels occur, the
corresponding accepting paths are a counterexample pair. Full state confluence is stronger than constancy of
(g); confluence modulo the declared observation is one sufficient proof technique under its usual hypotheses,
not an equivalent characterization of decision invariance. Property-preserving POR can retain a counterexample
in the reduced graph.

Enabledness also defeats a naive use of adjacent-swap connectivity. Consider one FIFO price level, initially
empty, with adds (A,B) of identities (a,b), and successful head executions (X,Y) targeting (a,b). Let

\[
A\prec X,\qquad A\prec Y,\qquad B\prec Y,
\]

with no other poset edges. This is an interval order, witnessed by intervals
(A=[0,1],B=[0.5,2.5],X=[2,4],Y=[3,5]). Its strictly legal schedules are

\[
AXBY,\qquad ABXY,\qquad BAYX.
\]

The first two are connected by one legal adjacent swap and fill (a) first. The third is isolated in the graph
of legal adjacent swaps and fills (b) first; every swap path through the full linear-extension graph crosses a
schedule with a disabled targeted execution. Recovering the missing component is completion/reachability, not a
stronger local commutator test.

A counterexample is already a pair of complete accepting schedules. Because both contain all event blocks,
ordinary path length is fixed and a “shortest path” claim is vacuous. Any optimized witness must first declare a
cost, such as the number of causal blocks or order reversals needed to distinguish the decisions. Repeatedly
deleting single blocks and re-running a suitably redefined instance yields at most a deletion-order-dependent
1-minimal witness: enabledness makes the property non-monotone, so it need not be inclusion-minimal. A true
inclusion-minimal witness requires exhaustive subset checks or a proved monotonicity condition. Related
minimum-counterexample variants are known to be hard, but no hardness reduction is claimed for an undeclared
cost on this instance. None supplies the frozen nonstandard guarantee.

**E3 verdict: FAIL/RED.** The invariant/abstain/witness interface is useful software behavior, but its theorem is
product reachability/observational determinism plus counterexample extraction. Observation-level confluence is
only one sufficient proof technique.

## 9. Cross-domain collision and T0 consequence

The molecular-dynamics transfer does not rescue the card. Halm and Posa's set-valued simultaneous-impact model
was motivated by simulators choosing an unpredictable collision order heuristically; it propagates arbitrary
impact ordering into a post-impact velocity set and gives existence, dissipation, finite termination and a tight
randomized approximation with probabilistic guarantees. The mechanical analogue therefore already contains
the card's broad “do not invent one order; return a certified outcome set” statement.

All three eligible exits fail before source qualification. Under the frozen stop rule, no market metadata audit,
benchmark implementation, outcome access, model fit or GPU run is permitted.

Two further reductions make the closure especially direct. Order-incomplete database theory already treats all
linear extensions as possible worlds, computes the set of order-aware accumulation results, and asks POSS/CERT
(whether a value occurs in some world or is fixed across all worlds), with NP/coNP hardness and bounded-width
tractable cases. In current concurrency theory, queue/priority-queue linearizability monitoring is explicitly
fixed-parameter tractable in the number of processes (k). These occupy the broad response-set and
invariant-decision interfaces even before adding a market interpretation.
