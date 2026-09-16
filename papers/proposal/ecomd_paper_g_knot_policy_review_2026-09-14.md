# Paper G fixed-knot policy review

PRIVATE / INTERNAL. 2026-09-14 NZ. Exploratory adjudication, not public research evidence.

Decision: park `g42_fixed_knot_learned_moves` nonterminally. Learned proposal selection, composite moves and cost-aware decorrelation objectives have direct parents. The current formulation lacks a concrete topology-specific efficiency mechanism and a qualified reference contract. This does not establish that learned polymer sampling cannot work.

## Allocation and comparison

The [bounded allocation](../../../research/paper_g/knot_policy_review_start_20260914.yaml) permits two new works and two existing-work readings. No new formulation/cycle, F2/F3, forecast, machine card, outcome payload, implementation or simulation. The original Cycle42 records remain unchanged.

Bojesen, [Policy-guided Monte Carlo: Reinforcement-learning Markov chain dynamics](https://arxiv.org/html/1808.09095), PRE 98, 063303 (2018), selected sections II–III and IV.3–4, already optimizes a policy using an observable's integrated autocorrelation and computational cost. It also describes composite and stochastic chain policies, with no-change actions and within-action memory. Its examples concern spins; “self-avoiding” policy history there is not a polymer topology certificate. Nevertheless, neither changing proposal weights nor joining elementary moves creates an independent algorithmic claim here. The paper's warning about short-horizon reward proxies also precedes a generic acceptance-versus-decorrelation critique.

Galliano et al., [Policy-guided Monte Carlo on general state spaces](https://arxiv.org/html/2407.03275v2), v2 dated 22 August 2024, selected II.1–2, extends proposal optimization to general state spaces and formulates accepted-transition rewards. This work already exists in the registry as `g38_pgmc`; this is a new route association/reading-depth record, not a globally new work. Its glass-mixture performance does not resolve the polymer comparison.

Janse van Rensburg and Rechnitzer, [BFACF-style algorithms for polygons in the body-centered and face-centered cubic lattices](https://arxiv.org/pdf/1011.3847), selected move definitions and irreducibility statements, supplies a useful scope check. The paper quotes the simple-cubic result and proves corresponding BCC/FCC results for unrooted polygons of fixed knot type. The move families allow length changes. These statements do not prove connectivity for a fixed-length restriction, bounded auxiliary length, labelled/rooted representation or a particular PAEA library. This selected reading verifies the theorem's stated scope, not every proof step or a new shortest-path result.

Existing [PAEA short-range-attraction work](https://arxiv.org/pdf/1212.6569), selected introduction/method scope, explicitly limits exactness of the topology check to small-segment moves. Its Wang–Landau thermal sampler remains a direct comparator. A learned policy must declare the actual certified move subset; its name alone supplies no certificate. Cycle42's knot-guided diffusion and PE VAE comparisons remain unchanged, including their already reported structural statistics and distinct physical ensembles.

Two works are globally new, two are existing-work readings. Six unique works now support the route: the original three, PGMC2018, reused PGMC2024 and BFACF. No full neighborhood review is claimed.

## R1 — proposal weighting cannot add missing edges

Consider a finite target distribution pi with positive mass and a reversible transition matrix P whose allowed off-diagonal transitions lie in a fixed undirected graph G. For a nontrivial state subset S, define its inside boundary

\[
B_S=\{x\in S:\exists y\notin S\text{ with }(x,y)\in G\}.
\]

The stationary probability flux out of S satisfies

\[
Q(S,S^c)=\sum_{x\in S,y\notin S}\pi(x)P(x,y)
\leq\pi(B_S).
\]

For the indicator function of S, the Dirichlet form is Q(S,S^c) and its variance is pi(S)pi(S^c). The variational characterization therefore bounds the ordinary reversible spectral gap by

\[
1-\lambda_2(P)\leq
\frac{Q(S,S^c)}{\pi(S)\pi(S^c)}
\leq\frac{\pi(B_S)}{\pi(S)\pi(S^c)}.
\]

This is a standard conductance/Rayleigh control, not a new theorem. Learning the probabilities on the same graph can improve flux up to the support limit; it cannot connect disconnected components. No actual polymer set S with a small boundary has been exhibited here, so this is not a polymer mixing lower bound. Composite proposals can change G and must be compared with classical composite moves and PGMC chain policies. Their construction, certification and reverse-path costs count per completed update; no free long-jump advantage follows.

The next useful construction would identify a specific family of polymer configurations, a bottleneck under named baseline moves, and a certified learned/composite move that crosses it economically. Simply asserting that knots are globally constrained is insufficient.

## R2 — auxiliary length is a possible reference route, with a sampling-clock condition

Suppose a normalizable extended ensemble on a consistently represented polygon space has

\[
\Pi(x)\propto w_{|x|}\exp[-\beta E(x)]\,\mathbf1\{K(x)=K\},
\]

with positive w_N depending only on length. Conditioning stationary per-step records on |x|=N cancels w_N and yields the fixed-length canonical measure. Thus permitting auxiliary length changes need not change the final fixed-length estimand. This algebra is not a claim that every BFACF implementation samples this exact measure. Counting conventions, rooting multiplicities, energy, Hastings factors, normalization and reachable components must match. Hard length caps can remove the connectivity supplied by unrestricted moves; the cited theorem does not remove this issue.

Recording only accepted changes uses a different clock. The stationary jump-chain measure is proportional to pi(x)[1-P(x,x)]. For example,

\[
P=\begin{pmatrix}0.9&0.1\\0.2&0.8\end{pmatrix}
\]

has stationary pi=(2/3,1/3), while the sequence of accepted changes alternates and has frequencies (1/2,1/2). Both states may belong to the same knot/length sector in the abstract control. Preserve holding-time weights or use stationary per-step records. This does not diagnose any published sampler; it prevents an invalid proposed reference protocol. Correct conditioning does not guarantee sufficiently frequent returns to the target length or affordable effective samples.

## Disposition, family guard and return condition

The current candidate proposes generic learned probabilities over existing certified moves. PGMC already covers that mechanism and the cost/decorrelation objective; PAEA and BFACF establish substantial classical topology machinery. No concrete advantage construction, matched fixed-length reference or empirical result qualifies further expense. Park at F1 without claiming a scientific impossibility or ruling out a rigorous empirical contribution.

Cycles38 and42 both produced no machine card for the narrow family “learned selection/composition of Monte Carlo proposals plus exact correction and cost optimization,” with direct learned-MC parents and no identified physical efficiency increment. Under the two-cycle rule, do not spend a third cycle on that generic formulation merely by changing the material or policy architecture. Re-entry needs a named new primary mechanism disagreement, a newly usable truth/control asset, or a theorem removing a recorded blocker, validated in the re-entry ledger with candidate harvesting explicitly authorized. This guard does not saturate all polymer science, all Monte Carlo research or unrelated scientific ML.

Stop this routine methods chain. Next general allocation is an unsaturated native scientific question; return here only for the contribution-changing mechanism/asset/theorem above. The original candidate's positive/null value remains valid, but is not evidence of novelty.

Counts unchanged: Paper G86 formulations /26 cycles /0 cards; detailed33 cycles /170 raw questions; inclusive42 /226. Four source records and eight locators are added: graph330 nodes /279 edges /1,946 locators; registry1,213 sources; candidate0 /parked12. No new forecasts or re-entry authorizations. Administrative validation cannot establish physical sampling quality or conference acceptance. Broad ICLR/ICML goal remains incomplete.
