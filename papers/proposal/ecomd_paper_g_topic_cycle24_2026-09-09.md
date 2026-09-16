# Paper G Cycle 24: settlement contracts and admissible auction bids

**PRIVATE / INTERNAL — exploratory topic selection, not public or
confirmatory evidence.** Literature cutoff: September 9, 2026.

Two native theory questions receive exact F1 screens; neither advances.
The retained result is two analytic boundaries: a dispatch penalty is part
of the settlement contract, and a quantity choice is part of the bidding
game. Removing either while retaining the original equilibrium conclusion
changes the claim. Neither calculation establishes a new Paper G thesis.

Record: `research/paper_g/cycle24_question_screen_20260909.yaml`.
This compact cycle was formulated during primary-source reading and is not
preregistered. No forecast, outcome access, solver, implementation or GPU work.

## Eligibility and questions

The registry and evidence/re-entry ledgers contained neither the screened
nonconvex electricity payment formulation nor the discriminatory-auction
quantity-choice formulation. Prior CfD, dispatch-forecast, random-auction-clock,
generic action-grammar liquidation and simulator-observation closures remain
closed. These are specific static settlement/bidding questions, not re-entry
into those parents. Six primary works were retained across the two screens:
two substantive model-text inspections and four abstract/context inspections.
There are at most three anchors for either F1 question. This is a two-question
compact cycle; no twelve-question sampling quota or full review is invoked.

| ID | Native object and rivals | Discriminator and two-sided value | Decision |
| --- | --- | --- | --- |
| G24-01, theory | The same nonconvex dispatch and individual feasible sets, settled either by energy price alone or the full ALD payment. Does exact augmented duality supply a uniform energy price with zero deviation gain, or does the guarantee require the contingent penalty? | Derive individual best responses and compare complete cash schedules. Success would qualify the price-only interpretation; failure identifies the contractual term required. | F1 quick-closed: no uniform price supports the witness dispatch. The complete ALD contract changes deviation incentives and is not contradicted by this result. |
| G24-02, theory | Two identical buyers in a pay-as-bid auction, with either fixed full-quantity bids or a freely chosen bid quantity. Does common information/payment format alone preserve uniqueness, or is the admissible quantity choice load-bearing? | Enumerate scalar-bid best responses and construct a profitable quantity deviation. Success would justify the transfer; failure identifies the missing action. | F1 quick-closed: a continuum of symmetric fixed-quantity equilibria fails the proposed unrestricted-uniqueness transfer. This is an elementary different-game boundary, not a refutation of Pycia–Woodward. |

No verified primary-model contradiction remains after matching contracts.
Positive/null values describe the proposed tests, not publication prospects.

## A. Pure prices versus a complete dispatch-dependent payment

Use the one-area fixture in Wang et al., arXiv v1, §5.1, equation (28):

\[
\min 2500x_1+500x_2,\quad
50x_1+50x_2=35,\quad x_1\in[.2,1],\ x_2\in\{0,1\}.
\]

The feasible centralized allocation is \(x^*=(.7,0)\), cost 1750. Write
physical output as \(z_i=50x_i\). At a pure per-unit price \(p\), profits
are \((p-50)z_1\) and \((p-10)z_2\). Supporting the interior output
\(z_1^*=35\) requires \(p=50\); keeping the block supplier at zero requires
\(p\leq10\). Both cannot hold.

Define lost opportunity cost as the best profit over each individual feasible
set minus profit at its assigned output. Exact maximization gives

\[
LOC_1(p)=\begin{cases}25(50-p)&p\leq50,\\15(p-50)&p\geq50,\end{cases}
\qquad LOC_2(p)=50(p-10)_+.
\]

Thus the total is \(1250-25p\) below 10, \(750+25p\) between 10 and 50,
and \(65p-1250\) above 50. Its global minimum is **1000 at \(p=10\)**.
At \(p=50\), the total is 2000. These are algebraic values in the published
fixture's units; they are not real-market measurements. They compare
price-taking individual choices, not a physically balanced unilateral dispatch.

The full one-period ALD cash transfer inferred from equation (7) is

\[
T_i(z_i;z_i^*)=\lambda z_i+\rho z_i^*-
\rho|z_i-z_i^*|
=(\lambda+\rho)z_i-2\rho(z_i-z_i^*)_+.
\]

The equality follows from \(|d|+d=2d_+\). On the allocated quantity it
looks like a common price \(p=\lambda+\rho\); away from that quantity it
has an additional one-sided charge. Using the paper's \(\lambda=10,\rho=40\),
the allocated price is 50 and the charge rate is 80 per excess unit.
Generator 1's profit is \(-80(z_1-35)_+\); generator 2 earns zero at zero
output and \(-2000\) at 50. Both allocated choices are therefore optimal
under this complete contract, with zero penalty-adjusted LOC.

The first generator is indifferent throughout \(z_1\in[10,35]\). The witness
supports weak optimality, not unique execution or convergence. This does not
refute the paper's no-profitable-deviation definition. Nor does the comparison
establish truthful reporting, demand-side participation, lawful implementation
or a real-market welfare gain. [Wang, Hesamzadeh, Zhao and Kronqvist,
equations (7), (28), (31)–(32)](https://arxiv.org/html/2603.25490v1).

Exact augmented duality already includes a nonlinear constraint penalty;
it is not a theorem providing anonymous linear prices. [Feizollahi, Ahmed
and Sun, accepted manuscript, abstract](https://mitsloan.mit.edu/shared/ods/documents?PublicationDocumentID=8183).
The broader distinction between competitive price support, loss coverage
and pricing objectives also has direct prior art. [Bichler, Knörr and
Maldonado, ISR](https://doi.org/10.1287/isre.2022.1139);
[Ahunbay, Bichler and Knörr, Operations Research](https://doi.org/10.1287/opre.2023.0401).
Only the price-only transfer and its proposed independent novelty are closed.
We have not audited the full ALD theorem, algorithm or network treatment.

## B. Fixed bid quantity versus an optional quantity choice

Declare a hypothetical auction with supply 1, two risk-neutral identical
buyers, complete information, value \(V(q)=q-q^2/2\) on \([0,1]\), zero
reserve and no fees. Each buyer initially may submit only a nonnegative
scalar price for quantity 1, or abstain. Highest bid receives the supply;
equal bids split it equally. Payment is own bid times allocated quantity.
This is a defined game, not an assertion about a current Treasury rule.

At symmetric price \(b\), each receives payoff
\(U_{tie}=3/8-b/2\). A lower bid loses and receives zero. A higher bid
\(b+\epsilon\) receives payoff \(1/2-b-\epsilon\). Consequently every

\[
\boxed{b\in[1/4,3/4]}
\]

is a symmetric pure Nash equilibrium, and no symmetric price outside that
interval is one. The calculation checks all available scalar-bid deviations
and abstention; it does not assert a classification of asymmetric equilibria.

Now keep values, supply, payment and pro-rata rationing fixed but allow a
bidder to choose its quantity \(z\in[0,1]\). Against a rival bidding \(b\)
for quantity 1, submit price \(b+\epsilon\) for
\(z=1-b-\epsilon\). It receives that quantity and earns
\(\tfrac12(1-b-\epsilon)^2\). Relative to the original tied profile,

\[
\lim_{\epsilon\downarrow0}\left[
\tfrac12(1-b-\epsilon)^2-(3/8-b/2)\right]
=\tfrac12(b-1/2)^2.
\]

For every \(b\neq1/2\) in the original interval, a sufficiently small
positive \(\epsilon\) therefore gives a profitable deviation. For example,
at \(b=1/4\), bid \(26/100\) for \(74/100\): payoff rises from
\(1/4\) to \(1369/5000\), a gain of \(119/5000\).

The full-quantity profile at \(b=1/2\) remains an equilibrium in this expanded
single-price game: a lower bid earns zero; an equal-price smaller quantity
receives at most one half and cannot improve its concave payoff; a higher
price has maximum payoff strictly below \(1/8\). This proves survival of
that profile, not uniqueness across every profile of the expanded game.

Both versions use one positive price per bid. The load-bearing change is
**quantity choice**, not a price tick or the number of positive price steps.
Calling this a finite-tick effect would be incorrect.

Pycia–Woodward's 2026 paper specifies a richer bid-function class and
explicitly identifies restrictions on permissible bids as outside its model.
Its uniqueness theorem is not contradicted by the fixed-quantity game.
[A Case for Pay-as-Bid Auctions, §2 and introductory scope](https://kylewoodward.com/research/auto/pycia%2Bwoodward-2026A.pdf).
Constrained-bidding equilibria already have a direct theoretical parent in
[Kastl 2012](https://collaborate.princeton.edu/en/publications/on-the-properties-of-equilibria-in-private-value-divisible-good-a/).
The exact fixture above is our elementary derivation, not a claim to reproduce
Kastl's private-information or variable-step theorem.

## Disposition and next update

Counts: **2 raw / 2 F1 / 0 F2 / 0 F3 / 0 cards**; both transfer formulations
quick-closed. Two reusable analytic diagnostics; zero outcome assets,
simulator runs, forecasts or re-entry audits. No hard gate was replaced by a
probability threshold. No full six-work F2 neighborhood was undertaken: the
six retained sources span the two F1 screens and context, not one full audit.

Neither familiar constraints nor an error in interpreting a paper supplies
an independent contribution. The next eligible search should freeze all
off-allocation payments and admissible bids before testing novelty. Reopening
either closed formulation requires a specific result or lawful control asset
that removes its recorded blocker and the applicable validated trigger.
No broader empirical, implementation or publication work is authorized here.
